"""End-to-end DeskPilot ticket pipeline."""

from __future__ import annotations

import uuid
from typing import Any, Callable, Literal, Optional

from pydantic import BaseModel, Field

from deskpilot.agents import escalator, resolver, router
from deskpilot.agents.escalator import EscalationHandoff
from deskpilot.agents.router import TicketClassification
from deskpilot.memory import retrieve_similar, store_ticket
from deskpilot.observability import log_trace


class TicketResult(BaseModel):
    ticket_id: str
    outcome: Literal["resolved", "clarify", "escalated"]
    message: str = ""
    classification: TicketClassification
    handoff: Optional[EscalationHandoff] = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)


def generate_id() -> str:
    return f"DP-{uuid.uuid4().hex[:10].upper()}"


def process_ticket(
    ticket_text: str,
    sender_email: str,
    progress: Optional[Callable[[str], None]] = None,
) -> TicketResult:
    """Process one ticket end-to-end."""
    ticket_id = generate_id()
    if progress:
        progress("Classifying...")
    classification = router.classify(ticket_text, ticket_id=ticket_id)

    if classification.needs_clarification:
        message = classification.clarification_question or "Can you share one more detail so I can route this correctly?"
        log_trace(ticket_id, "pipeline", "finish", {}, {"outcome": "clarify", "message": message})
        return TicketResult(ticket_id=ticket_id, outcome="clarify", message=message, classification=classification)

    if progress:
        progress("Retrieving similar tickets...")
    similar = retrieve_similar(ticket_text, k=3)

    if progress:
        progress("Resolving...")
    resolver_outcome = resolver.run(ticket_text, sender_email, classification, similar, ticket_id=ticket_id)

    if resolver_outcome.outcome in ("escalate", "iteration_cap"):
        if progress:
            progress("Writing escalation handoff...")
        handoff = escalator.write_handoff(ticket_text, classification, resolver_outcome.trace, ticket_id=ticket_id)
        store_ticket(ticket_id, ticket_text, sender_email, classification.category, "escalated", handoff.summary)
        log_trace(ticket_id, "pipeline", "finish", {}, {"outcome": "escalated", "message": handoff.summary})
        return TicketResult(
            ticket_id=ticket_id,
            outcome="escalated",
            message=handoff.summary,
            classification=classification,
            handoff=handoff,
            tool_calls=resolver_outcome.tool_calls,
        )

    if resolver_outcome.outcome == "resolved":
        store_ticket(ticket_id, ticket_text, sender_email, classification.category, "resolved", resolver_outcome.message)
        log_trace(ticket_id, "pipeline", "finish", {}, {"outcome": "resolved", "message": resolver_outcome.message})
        return TicketResult(
            ticket_id=ticket_id,
            outcome="resolved",
            message=resolver_outcome.message,
            classification=classification,
            tool_calls=resolver_outcome.tool_calls,
        )

    log_trace(ticket_id, "pipeline", "finish", {}, {"outcome": "clarify", "message": resolver_outcome.message})
    return TicketResult(
        ticket_id=ticket_id,
        outcome="clarify",
        message=resolver_outcome.message,
        classification=classification,
        tool_calls=resolver_outcome.tool_calls,
    )


if __name__ == "__main__":
    print(generate_id())
