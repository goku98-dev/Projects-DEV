"""Mock HRIS tools backed by employees.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from deskpilot.config import DATA_DIR

EMPLOYEES_PATH = DATA_DIR / "employees.json"


def _load_employees() -> list[dict[str, Any]]:
    return json.loads(Path(EMPLOYEES_PATH).read_text(encoding="utf-8"))


def get_employee(user_email: str) -> dict[str, Any]:
    """Return an employee record by email."""
    try:
        user_email = user_email.strip().lower()
        for employee in _load_employees():
            if str(employee["email"]).lower() == user_email:
                return employee
        return {"error": "not_found"}
    except Exception as exc:
        return {"error": str(exc)}


def get_employee_by_id(employee_id: str) -> dict[str, Any]:
    """Return an employee record by employee ID."""
    try:
        for employee in _load_employees():
            if employee["id"] == employee_id:
                return employee
        return {"error": "not_found"}
    except Exception as exc:
        return {"error": str(exc)}


def get_manager(user_email: str) -> dict[str, Any]:
    """Return the manager record for an employee."""
    try:
        employee = get_employee(user_email)
        if employee.get("error"):
            return employee
        manager_id = employee.get("manager_id")
        if not manager_id:
            return {"error": "no_manager"}
        return get_employee_by_id(str(manager_id))
    except Exception as exc:
        return {"error": str(exc)}


def check_pto_balance(user_email: str) -> dict[str, Any]:
    """Return PTO balance details for an employee."""
    try:
        employee = get_employee(user_email)
        if employee.get("error"):
            return employee
        return {
            "balance_days": employee["pto_balance_days"],
            "accrual_rate_per_month": 1.5,
            "status": employee["status"],
        }
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    print(get_employee("jane.doe@acme.com"))
    print(check_pto_balance("jane.doe@acme.com"))
