"""Resolver agent with tool-use loop."""

from __future__ import annotations

import time
from typing import Any, Literal

import anthropic
from pydantic import BaseModel, Field

from deskpilot import config
from deskpilot.agents.router import TicketClassification
from deskpilot.guardrails import TicketContext
from deskpilot.observability import log_trace
from deskpilot.tools.registry import ANTHROPIC_TOOLS, execute_tool

PROMPT = """You are DeskPilot Resolver, an autonomous Acme Corp IT/HR helpdesk agent.

WHEN TO ESCALATE — do this immediately if any condition is met:
- Any tool returns a result containing "blocked": true — never resolve a blocked action
- The request is for another user's password reset or account unlock (sender_email != target)
- AWS Console access is requested — route to Security
- The employee cannot be found in the directory
- The request involves suspicious, unsafe, or clearly out-of-scope activity

WHEN TO CLARIFY — ask exactly one question when a required detail is missing:
- access_request: app name is not mentioned
- onboarding: new hire name or start date is missing

WHEN TO RESOLVE — when you have completed the request using tools:
- Use search_kb before answering any policy question
- Credential ops (reset_password, unlock_account): only for the sender's own account
- grant_app_access returning status="approval_required" is a successful outcome — tell the user approval is pending and call finish_resolved
- After a successful tool action, always call finish_resolved with a clear summary

TOOL RESULT RULES:
- "blocked": true in any tool result → call finish_escalate immediately, state the blocked action as the reason
- Tool error that is not "blocked" → try an alternative tool or clarify, do not silently escalate

You must finish by calling exactly one sentinel:
- finish_resolved(message_to_user): request fully handled
- finish_clarify(question): one required detail is missing
- finish_escalate(reason): cannot or must not resolve autonomously

Keep user-facing messages concise, specific, and honest. Never invent approvals, passwords, balances, or policy details."""


class ResolverOutcome(BaseModel):
    outcome: Literal["resolved", "clarify", "escalate", "iteration_cap"]
    message: str = ""
    reason: str = ""
    trace: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


def _block_to_dict(block: Any) -> dict[str, Any]:
    if hasattr(block, "model_dump"):
        return block.model_dump()
    if isinstance(block, dict):
        return block
    data: dict[str, Any] = {"type": getattr(block, "type", "")}
    for key in ("text", "id", "name", "input"):
        if hasattr(block, key):
            data[key] = getattr(block, key)
    return data


def _usage(message: Any) -> tuple[int, int]:
    usage = getattr(message, "usage", None)
    return int(getattr(usage, "input_tokens", 0) or 0), int(getattr(usage, "output_tokens", 0) or 0)


def _raise_model_error(exc: Exception) -> None:
    if getattr(exc, "status_code", None) == 404:
        raise RuntimeError("Anthropic model was not found. Update the model strings in deskpilot/config.py.") from exc
    raise exc


def run(
    ticket_text: str,
    sender_email: str,
    classification: TicketClassification,
    similar_resolutions: list[dict[str, Any]],
    ticket_id: str = "manual",
) -> ResolverOutcome:
    """Run the resolver loop until a finish sentinel or iteration cap."""
    client = anthropic.Anthropic(api_key=config.require_api_key())
    context = TicketContext(ticket_id=ticket_id, sender_email=sender_email)
    user_payload = {
        "ticket_text": ticket_text,
        "sender_email": sender_email,
        "classification": classification.model_dump(),
        "similar_resolutions": similar_resolutions,
    }
    messages: list[dict[str, Any]] = [{"role": "user", "content": str(user_payload)}]
    trace: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []

    for _ in range(config.MAX_RESOLVER_ITERATIONS):
        started = time.perf_counter()
        try:
            message = client.messages.create(
                model=config.RESOLVER_MODEL,
                max_tokens=900,
                temperature=0,
                system=PROMPT,
                messages=messages,
                tools=ANTHROPIC_TOOLS,
            )
        except Exception as exc:
            _raise_model_error(exc)
        latency_ms = int((time.perf_counter() - started) * 1000)
        tokens_in, tokens_out = _usage(message)
        log_trace(
            ticket_id,
            "resolver",
            "model_call",
            {"messages": messages[-2:]},
            {"stop_reason": getattr(message, "stop_reason", "")},
            tokens_in,
            tokens_out,
            config.cost_for_tokens(config.RESOLVER_MODEL, tokens_in, tokens_out),
            latency_ms,
        )
        assistant_content = [_block_to_dict(block) for block in message.content]
        messages.append({"role": "assistant", "content": assistant_content})

        tool_results: list[dict[str, Any]] = []
        used_tool = False
        for block in message.content:
            if getattr(block, "type", "") != "tool_use":
                continue
            used_tool = True
            tool_name = str(getattr(block, "name", ""))
            args = dict(getattr(block, "input", {}) or {})
            result = execute_tool(tool_name, args, context)
            call_record = {"tool": tool_name, "args": args, "result": result}
            trace.append(call_record)
            tool_calls.append(call_record)
            log_trace(ticket_id, "resolver", "tool_call", {"tool": tool_name, "args": args}, {"result": result})

            if tool_name == "finish_resolved":
                message_to_user = str(result.get("message_to_user", args.get("message_to_user", "")))
                log_trace(ticket_id, "resolver", "finish", {}, {"outcome": "resolved", "message": message_to_user})
                return ResolverOutcome(outcome="resolved", message=message_to_user, trace=trace, tool_calls=tool_calls)
            if tool_name == "finish_clarify":
                question = str(result.get("question", args.get("question", "")))
                log_trace(ticket_id, "resolver", "finish", {}, {"outcome": "clarify", "message": question})
                return ResolverOutcome(outcome="clarify", message=question, trace=trace, tool_calls=tool_calls)
            if tool_name == "finish_escalate":
                reason = str(result.get("reason", args.get("reason", "")))
                log_trace(ticket_id, "resolver", "finish", {}, {"outcome": "escalate", "reason": reason})
                return ResolverOutcome(outcome="escalate", reason=reason, trace=trace, tool_calls=tool_calls)

            tool_results.append({"type": "tool_result", "tool_use_id": getattr(block, "id", ""), "content": str(result)})

        if not used_tool:
            reason = "Resolver returned no tool call."
            log_trace(ticket_id, "resolver", "finish", {}, {"outcome": "escalate", "reason": reason})
            return ResolverOutcome(outcome="escalate", reason=reason, trace=trace, tool_calls=tool_calls)
        messages.append({"role": "user", "content": tool_results})

    reason = "Resolver reached the maximum tool-use iterations."
    log_trace(ticket_id, "resolver", "finish", {}, {"outcome": "iteration_cap", "reason": reason})
    return ResolverOutcome(outcome="iteration_cap", reason=reason, trace=trace, tool_calls=tool_calls)


if __name__ == "__main__":
    print(ResolverOutcome(outcome="clarify", message="Which app do you need?"))
