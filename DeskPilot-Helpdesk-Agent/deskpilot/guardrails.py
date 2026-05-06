"""Deterministic guardrails for action tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from deskpilot.observability import log_trace
from deskpilot.tools.hris import get_employee, get_employee_by_id
from deskpilot.tools.provisioner import get_app


@dataclass(frozen=True)
class TicketContext:
    ticket_id: str
    sender_email: str


REAL_ACTION_TOOLS = {"reset_password", "unlock_account", "grant_app_access", "revoke_app_access", "check_pto_balance", "get_employee"}


def _target_email(tool_name: str, args: dict[str, Any]) -> str:
    if "user_email" in args:
        return str(args["user_email"]).strip().lower()
    if "target_email" in args:
        return str(args["target_email"]).strip().lower()
    return ""


def _is_manager(sender_email: str, target_employee: dict[str, Any]) -> bool:
    manager_id = target_employee.get("manager_id")
    if not manager_id:
        return False
    manager = get_employee_by_id(str(manager_id))
    return str(manager.get("email", "")).lower() == sender_email.lower()


def evaluate_guardrail(tool_name: str, args: dict[str, Any], context: TicketContext) -> tuple[bool, str]:
    """Return allow/block decision and reason."""
    target_email = _target_email(tool_name, args)
    sender_email = context.sender_email.strip().lower()

    if tool_name in REAL_ACTION_TOOLS:
        employee = get_employee(target_email)
        if employee.get("error"):
            return False, "Unknown employee: target email is not present in employees.json."

    if tool_name in {"reset_password", "unlock_account"} and target_email != sender_email:
        return False, "Identity mismatch: cannot perform credential operations on behalf of another user."

    if tool_name in {"check_pto_balance", "get_employee"}:
        employee = get_employee(target_email)
        if target_email != sender_email and not _is_manager(sender_email, employee):
            return False, "Self-service only: employee data can be viewed only by the employee or their direct manager."

    if tool_name == "grant_app_access":
        app_name = str(args.get("app", ""))
        app = get_app(app_name)
        if app.get("error"):
            return False, "Unknown app: requested application is not in apps.json."
        if str(app.get("name", "")).lower() == "aws console":
            return False, "AWS Console access requires Security team review."

    return True, "allowed"


def guarded_call(tool_name: str, args: dict[str, Any], context: TicketContext, tool_func: Callable[..., Any]) -> Any:
    """Evaluate guardrails, log the decision, and invoke a tool when allowed."""
    allowed, reason = evaluate_guardrail(tool_name, args, context)
    log_trace(
        context.ticket_id,
        "guardrail",
        "guardrail_check",
        {"tool": tool_name, "args": args, "sender_email": context.sender_email},
        {"allowed": allowed, "reason": reason},
    )
    if not allowed:
        return {"error": reason, "blocked": True}
    return tool_func(**args)


if __name__ == "__main__":
    ctx = TicketContext(ticket_id="smoke", sender_email="jane.doe@acme.com")
    print(evaluate_guardrail("reset_password", {"user_email": "bob.smith@acme.com"}, ctx))
