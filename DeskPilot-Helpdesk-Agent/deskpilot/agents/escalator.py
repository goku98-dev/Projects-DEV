"""Escalator agent for structured human handoff summaries."""

from __future__ import annotations

import time
from typing import Any, Literal

import anthropic
from pydantic import BaseModel, Field

from deskpilot import config
from deskpilot.agents.router import TicketClassification
from deskpilot.observability import log_trace

PROMPT = """You are DeskPilot Escalator, writing concise handoff notes for Acme Corp human support queues.

Create a structured handoff from the raw ticket, router classification, and resolver trace. Be factual. Include unsafe or blocked actions, missing information, relevant KB article titles mentioned in tool results, and the next best human action.

Queue guidance:
- IT: routine identity, device, SaaS, VPN, software, onboarding systems
- HR: PTO, leave, conduct, employment status, benefits
- Security: AWS Console, suspected social engineering, phishing, incidents, privileged access, data exposure
- Manager: business approval or budget approval needed

Return only by calling submit_handoff."""


class EscalationHandoff(BaseModel):
    summary: str
    what_was_tried: str
    suggested_resolution: str
    relevant_kb_articles: list[str] = Field(default_factory=list)
    suggested_assignee_queue: Literal["IT", "HR", "Security", "Manager"]


HANDOFF_TOOL = {
    "name": "submit_handoff",
    "description": "Submit a structured escalation handoff.",
    "input_schema": EscalationHandoff.model_json_schema(),
}


def _usage(message: Any) -> tuple[int, int]:
    usage = getattr(message, "usage", None)
    return int(getattr(usage, "input_tokens", 0) or 0), int(getattr(usage, "output_tokens", 0) or 0)


def _raise_model_error(exc: Exception) -> None:
    if getattr(exc, "status_code", None) == 404:
        raise RuntimeError("Anthropic model was not found. Update the model strings in deskpilot/config.py.") from exc
    raise exc


def write_handoff(
    ticket_text: str,
    classification: TicketClassification,
    resolver_trace: list[dict[str, Any]],
    ticket_id: str = "manual",
) -> EscalationHandoff:
    """Write a structured escalation handoff."""
    client = anthropic.Anthropic(api_key=config.require_api_key())
    payload = {
        "ticket_text": ticket_text,
        "classification": classification.model_dump(),
        "resolver_trace": resolver_trace,
    }
    started = time.perf_counter()
    try:
        message = client.messages.create(
            model=config.ESCALATOR_MODEL,
            max_tokens=700,
            temperature=0,
            system=PROMPT,
            messages=[{"role": "user", "content": str(payload)}],
            tools=[HANDOFF_TOOL],
            tool_choice={"type": "tool", "name": "submit_handoff"},
        )
    except Exception as exc:
        _raise_model_error(exc)
    latency_ms = int((time.perf_counter() - started) * 1000)
    tokens_in, tokens_out = _usage(message)
    for block in message.content:
        if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "submit_handoff":
            handoff = EscalationHandoff.model_validate(getattr(block, "input", {}))
            log_trace(
                ticket_id,
                "escalator",
                "finish",
                payload,
                handoff.model_dump(),
                tokens_in,
                tokens_out,
                config.cost_for_tokens(config.ESCALATOR_MODEL, tokens_in, tokens_out),
                latency_ms,
            )
            return handoff
    raise RuntimeError("Escalator did not call submit_handoff.")


if __name__ == "__main__":
    print(EscalationHandoff.model_validate({"summary": "Example", "what_was_tried": "None", "suggested_resolution": "Review", "relevant_kb_articles": [], "suggested_assignee_queue": "IT"}))
