"""Anthropic tool registry for the resolver agent."""

from __future__ import annotations

from typing import Any, Callable

from deskpilot.guardrails import REAL_ACTION_TOOLS, TicketContext, guarded_call
from deskpilot.tools.hris import check_pto_balance, get_employee
from deskpilot.tools.idp import reset_password, unlock_account
from deskpilot.tools.kb import search_kb
from deskpilot.tools.provisioner import grant_app_access, revoke_app_access


def finish_resolved(message_to_user: str) -> dict[str, Any]:
    return {"sentinel": "finish_resolved", "message_to_user": message_to_user}


def finish_clarify(question: str) -> dict[str, Any]:
    return {"sentinel": "finish_clarify", "question": question}


def finish_escalate(reason: str) -> dict[str, Any]:
    return {"sentinel": "finish_escalate", "reason": reason}


TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "search_kb": search_kb,
    "get_employee": get_employee,
    "check_pto_balance": check_pto_balance,
    "reset_password": reset_password,
    "unlock_account": unlock_account,
    "grant_app_access": grant_app_access,
    "revoke_app_access": revoke_app_access,
    "finish_resolved": finish_resolved,
    "finish_clarify": finish_clarify,
    "finish_escalate": finish_escalate,
}

ANTHROPIC_TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_kb",
        "description": "Search Acme Corp IT and HR knowledge base articles.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 3}},
            "required": ["query"],
        },
    },
    {
        "name": "get_employee",
        "description": "Look up the authenticated requester's employee record or a direct report's record.",
        "input_schema": {"type": "object", "properties": {"user_email": {"type": "string"}}, "required": ["user_email"]},
    },
    {
        "name": "check_pto_balance",
        "description": "Check PTO balance for the requester or a sender's direct report.",
        "input_schema": {"type": "object", "properties": {"user_email": {"type": "string"}}, "required": ["user_email"]},
    },
    {
        "name": "reset_password",
        "description": "Issue a temporary password for the ticket sender only.",
        "input_schema": {"type": "object", "properties": {"user_email": {"type": "string"}}, "required": ["user_email"]},
    },
    {
        "name": "unlock_account",
        "description": "Unlock the ticket sender's identity account only.",
        "input_schema": {"type": "object", "properties": {"user_email": {"type": "string"}}, "required": ["user_email"]},
    },
    {
        "name": "grant_app_access",
        "description": "Grant or route approval for SaaS access according to app policy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_email": {"type": "string"},
                "app": {"type": "string"},
                "justification": {"type": "string"},
            },
            "required": ["user_email", "app", "justification"],
        },
    },
    {
        "name": "revoke_app_access",
        "description": "Revoke SaaS app access for the authenticated requester.",
        "input_schema": {
            "type": "object",
            "properties": {"user_email": {"type": "string"}, "app": {"type": "string"}},
            "required": ["user_email", "app"],
        },
    },
    {
        "name": "finish_resolved",
        "description": "End the ticket as resolved with a user-facing response.",
        "input_schema": {
            "type": "object",
            "properties": {"message_to_user": {"type": "string"}},
            "required": ["message_to_user"],
        },
    },
    {
        "name": "finish_clarify",
        "description": "End the turn by asking exactly one clarifying question.",
        "input_schema": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]},
    },
    {
        "name": "finish_escalate",
        "description": "End the ticket by escalating with a concise reason.",
        "input_schema": {"type": "object", "properties": {"reason": {"type": "string"}}, "required": ["reason"]},
    },
]


def execute_tool(tool_name: str, args: dict[str, Any], context: TicketContext) -> Any:
    """Execute a registered tool with deterministic guardrails where required."""
    try:
        func = TOOL_FUNCTIONS[tool_name]
        if tool_name in REAL_ACTION_TOOLS:
            return guarded_call(tool_name, args, context, func)
        return func(**args)
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    ctx = TicketContext(ticket_id="smoke", sender_email="jane.doe@acme.com")
    print(execute_tool("get_employee", {"user_email": "jane.doe@acme.com"}, ctx))
