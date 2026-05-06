"""JSONL tracing and metrics helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

from deskpilot.config import TRACES_DIR


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_trace(
    ticket_id: str,
    agent: str,
    action: str,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: float = 0.0,
    latency_ms: int = 0,
) -> None:
    """Append one trace event to today's JSONL file."""
    try:
        TRACES_DIR.mkdir(exist_ok=True)
        path = TRACES_DIR / f"{datetime.now(timezone.utc).date().isoformat()}.jsonl"
        event = {
            "timestamp": utc_now_iso(),
            "ticket_id": ticket_id,
            "agent": agent,
            "action": action,
            "input": input_data,
            "output": output_data,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, default=str) + "\n")
    except Exception:
        return


def read_recent_traces(limit: int = 100) -> list[dict[str, Any]]:
    """Read recent trace rows across trace files."""
    if not TRACES_DIR.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(Path(TRACES_DIR).glob("*.jsonl"), reverse=True):
        for line in reversed(path.read_text(encoding="utf-8").splitlines()):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(rows) >= limit:
                return rows
    return rows


def ticket_metrics() -> dict[str, Any]:
    """Aggregate ticket-level metrics from trace events."""
    traces = read_recent_traces(limit=10_000)
    grouped: dict[str, dict[str, Any]] = {}
    for event in traces:
        ticket_id = event["ticket_id"]
        grouped.setdefault(ticket_id, {"cost": 0.0, "latency": 0, "category": "", "outcome": "", "timestamp": event["timestamp"]})
        grouped[ticket_id]["cost"] += float(event.get("cost_usd", 0.0))
        grouped[ticket_id]["latency"] += int(event.get("latency_ms", 0))
        if event["agent"] == "router" and event["action"] == "finish":
            grouped[ticket_id]["category"] = event.get("output", {}).get("category", "")
        if event["action"] == "finish":
            grouped[ticket_id]["outcome"] = event.get("output", {}).get("outcome", grouped[ticket_id].get("outcome", ""))
    tickets = list(grouped.values())
    total = len(tickets)
    resolved = sum(1 for item in tickets if item.get("outcome") == "resolved")
    latencies = sorted(int(item.get("latency", 0)) for item in tickets)
    costs = [float(item.get("cost", 0.0)) for item in tickets]
    p50 = median(latencies) if latencies else 0
    p95 = latencies[int(0.95 * (len(latencies) - 1))] if latencies else 0
    return {
        "total_tickets": total,
        "autonomous_resolution_rate": resolved / total if total else 0.0,
        "avg_cost": sum(costs) / total if total else 0.0,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95,
        "tickets": tickets,
    }


if __name__ == "__main__":
    print(read_recent_traces(5))
