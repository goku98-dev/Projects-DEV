"""Router agent for ticket classification and entity extraction."""

from __future__ import annotations

import time
from typing import Any, Literal, Optional

import anthropic
from pydantic import BaseModel, Field

from deskpilot import config
from deskpilot.observability import log_trace

PROMPT = """You are DeskPilot Router, a precise triage agent for Acme Corp internal IT/HR helpdesk tickets.

Classify the user's ticket into exactly one category:
- password_reset: user is locked out, forgot password, needs password reset, or account unlock
- access_request: user needs SaaS access, permissions, app provisioning, or app removal
- pto_query: PTO balance, accrual, time-off balance, or PTO policy questions
- onboarding: new hire setup, equipment, accounts, onboarding checklist, first-week access
- policy_lookup: general IT/HR policy questions answerable from the knowledge base
- other: anything outside those categories, unsafe requests, unclear multi-domain actions

Extract useful entities such as user_email, target_email, app, policy_topic, date, manager_name, and urgency.
If a ticket cannot be acted on because a required detail is missing, set needs_clarification true and ask one concise question.
Do not over-clarify when the sender email can identify the requester. Password reset language should be password_reset even if it mentions urgency.
Return only by calling submit_classification."""


class TicketClassification(BaseModel):
    category: Literal["password_reset", "access_request", "pto_query", "onboarding", "policy_lookup", "other"]
    entities: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    needs_clarification: bool
    clarification_question: Optional[str] = None


CLASSIFICATION_TOOL = {
    "name": "submit_classification",
    "description": "Submit the validated ticket classification.",
    "input_schema": TicketClassification.model_json_schema(),
}


def _usage(message: Any) -> tuple[int, int]:
    usage = getattr(message, "usage", None)
    return int(getattr(usage, "input_tokens", 0) or 0), int(getattr(usage, "output_tokens", 0) or 0)


def _raise_model_error(exc: Exception) -> None:
    status = getattr(exc, "status_code", None)
    if status == 404:
        raise RuntimeError("Anthropic model was not found. Update the model strings in deskpilot/config.py.") from exc
    raise exc


def classify(ticket_text: str, ticket_id: str = "manual") -> TicketClassification:
    """Classify a ticket using Anthropic tool use."""
    client = anthropic.Anthropic(api_key=config.require_api_key())
    started = time.perf_counter()
    try:
        message = client.messages.create(
            model=config.ROUTER_MODEL,
            max_tokens=500,
            temperature=0,
            system=PROMPT,
            messages=[{"role": "user", "content": ticket_text}],
            tools=[CLASSIFICATION_TOOL],
            tool_choice={"type": "tool", "name": "submit_classification"},
        )
    except Exception as exc:
        _raise_model_error(exc)
    latency_ms = int((time.perf_counter() - started) * 1000)
    tokens_in, tokens_out = _usage(message)
    for block in message.content:
        if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "submit_classification":
            classification = TicketClassification.model_validate(getattr(block, "input", {}))
            log_trace(
                ticket_id,
                "router",
                "finish",
                {"ticket_text": ticket_text},
                classification.model_dump(),
                tokens_in,
                tokens_out,
                config.cost_for_tokens(config.ROUTER_MODEL, tokens_in, tokens_out),
                latency_ms,
            )
            return classification
    raise RuntimeError("Router did not call submit_classification.")


if __name__ == "__main__":
    print(TicketClassification(category="password_reset", entities={}, confidence=0.9, needs_clarification=False))
