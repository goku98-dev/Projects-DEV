"""Mock identity provider tools."""

from __future__ import annotations

import secrets
import string
from typing import Any

from deskpilot.tools.hris import get_employee


def _temporary_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%?"
    while True:
        value = "".join(secrets.choice(alphabet) for _ in range(length))
        if any(c.islower() for c in value) and any(c.isupper() for c in value) and any(c.isdigit() for c in value):
            return value


def reset_password(user_email: str) -> dict[str, Any]:
    """Issue a mock temporary password."""
    try:
        employee = get_employee(user_email)
        if employee.get("error"):
            return employee
        if employee.get("status") != "active":
            return {"error": "employee_not_active", "status": employee.get("status")}
        return {
            "status": "temporary_password_issued",
            "temp_password": _temporary_password(),
            "expires_minutes": 30,
        }
    except Exception as exc:
        return {"error": str(exc)}


def unlock_account(user_email: str) -> dict[str, Any]:
    """Unlock a mock identity account."""
    try:
        employee = get_employee(user_email)
        if employee.get("error"):
            return employee
        if employee.get("status") != "active":
            return {"error": "employee_not_active", "status": employee.get("status")}
        return {"status": "account_unlocked"}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    print(unlock_account("jane.doe@acme.com"))
