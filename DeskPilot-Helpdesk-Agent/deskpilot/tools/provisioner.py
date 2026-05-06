"""Mock SaaS provisioner backed by apps.json and access_grants.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from deskpilot.config import DATA_DIR
from deskpilot.tools.hris import get_employee, get_employee_by_id

APPS_PATH = DATA_DIR / "apps.json"
GRANTS_PATH = DATA_DIR / "access_grants.json"


def _load_apps() -> list[dict[str, Any]]:
    return json.loads(Path(APPS_PATH).read_text(encoding="utf-8"))


def _load_grants() -> dict[str, list[str]]:
    return json.loads(Path(GRANTS_PATH).read_text(encoding="utf-8"))


def _write_grants(grants: dict[str, list[str]]) -> None:
    Path(GRANTS_PATH).write_text(json.dumps(grants, indent=2), encoding="utf-8")


def get_app(app: str) -> dict[str, Any]:
    """Return an app config by friendly name."""
    try:
        requested = app.strip().lower()
        for app_config in _load_apps():
            if str(app_config["name"]).lower() == requested:
                return app_config
        return {"error": "unknown_app"}
    except Exception as exc:
        return {"error": str(exc)}


def grant_app_access(user_email: str, app: str, justification: str) -> dict[str, Any]:
    """Grant or route approval for application access."""
    try:
        employee = get_employee(user_email)
        if employee.get("error"):
            return employee
        app_config = get_app(app)
        if app_config.get("error"):
            return app_config

        department = str(employee["department"])
        requires_approval = bool(app_config["requires_manager_approval"]) and department not in app_config["auto_approve_departments"]
        manager = get_employee_by_id(str(employee.get("manager_id"))) if employee.get("manager_id") else {"email": "hr@acme.com"}
        approver_email = manager.get("email", "hr@acme.com")

        if requires_approval:
            return {
                "status": "approval_required",
                "requires_approval": True,
                "approver_email": approver_email,
                "app": app_config["name"],
                "justification": justification,
            }

        grants = _load_grants()
        employee_id = str(employee["id"])
        grants.setdefault(employee_id, [])
        if app_config["name"] not in grants[employee_id]:
            grants[employee_id].append(app_config["name"])
            grants[employee_id] = sorted(grants[employee_id])
            _write_grants(grants)
        return {"status": "granted", "requires_approval": False, "approver_email": None, "app": app_config["name"]}
    except Exception as exc:
        return {"error": str(exc)}


def revoke_app_access(user_email: str, app: str) -> dict[str, Any]:
    """Revoke application access."""
    try:
        employee = get_employee(user_email)
        if employee.get("error"):
            return employee
        app_config = get_app(app)
        if app_config.get("error"):
            return app_config
        grants = _load_grants()
        employee_id = str(employee["id"])
        current = set(grants.get(employee_id, []))
        current.discard(str(app_config["name"]))
        grants[employee_id] = sorted(current)
        _write_grants(grants)
        return {"status": "revoked", "app": app_config["name"]}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    print(grant_app_access("jane.doe@acme.com", "Figma", "Design review"))
