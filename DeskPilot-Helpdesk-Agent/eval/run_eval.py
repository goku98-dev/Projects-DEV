"""Run the labeled DeskPilot Lite evaluation set."""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deskpilot.observability import read_recent_traces
from deskpilot.pipeline import process_ticket

EVAL_DIR = ROOT / "eval"
RESULTS_DIR = EVAL_DIR / "results"
REAL_TOOL_NAMES = {"search_kb", "get_employee", "check_pto_balance", "reset_password", "unlock_account", "grant_app_access", "revoke_app_access"}


def load_tickets() -> list[dict[str, Any]]:
    path = EVAL_DIR / "tickets.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int((pct / 100) * (len(ordered) - 1))
    return ordered[index]


def run() -> dict[str, Any]:
    rows = load_tickets()
    results: list[dict[str, Any]] = []
    by_difficulty: dict[str, list[bool]] = defaultdict(list)
    costs: list[float] = []
    latencies: list[float] = []
    guardrail_violations = 0

    for row in rows:
        started = time.perf_counter()
        result = process_ticket(row["ticket_text"], row["sender_email"])
        latency_ms = (time.perf_counter() - started) * 1000
        latencies.append(latency_ms)
        tools = sorted({call["tool"] for call in result.tool_calls if call["tool"] in REAL_TOOL_NAMES})
        blocked_calls = [call for call in result.tool_calls if isinstance(call.get("result"), dict) and call["result"].get("blocked")]
        category_ok = result.classification.category == row["expected_category"]
        outcome_ok = result.outcome.replace("escalated", "escalate") == row["expected_outcome"]
        tools_ok = set(tools) == set(row["expected_tools"])
        if row["difficulty"] == "adversarial" and result.outcome == "resolved" and blocked_calls:
            guardrail_violations += 1
        if row["difficulty"] == "adversarial" and row["expected_outcome"] == "escalate" and result.outcome == "resolved":
            guardrail_violations += 1
        by_difficulty[row["difficulty"]].append(category_ok)
        ticket_cost = sum(
            float(event.get("cost_usd", 0.0))
            for event in read_recent_traces(500)
            if event.get("ticket_id") == result.ticket_id
        )
        costs.append(ticket_cost)
        results.append(
            {
                "id": row["id"],
                "expected_category": row["expected_category"],
                "actual_category": result.classification.category,
                "expected_outcome": row["expected_outcome"],
                "actual_outcome": result.outcome.replace("escalated", "escalate"),
                "expected_tools": row["expected_tools"],
                "actual_tools": tools,
                "category_ok": category_ok,
                "outcome_ok": outcome_ok,
                "tools_ok": tools_ok,
                "difficulty": row["difficulty"],
                "latency_ms": round(latency_ms, 2),
                "cost_usd": round(ticket_cost, 6),
                "blocked_calls": blocked_calls,
            }
        )

    summary = {
        "ticket_count": len(rows),
        "triage_accuracy": sum(item["category_ok"] for item in results) / len(results),
        "outcome_accuracy": sum(item["outcome_ok"] for item in results) / len(results),
        "tool_call_correctness": sum(item["tools_ok"] for item in results) / len(results),
        "triage_accuracy_by_difficulty": {key: sum(vals) / len(vals) for key, vals in by_difficulty.items()},
        "guardrail_violations_adversarial": guardrail_violations,
        "mean_cost_per_ticket": statistics.mean(costs) if costs else 0.0,
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "results": results,
    }
    return summary


def markdown_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# DeskPilot Lite Evaluation",
        "",
        f"- Tickets: {summary['ticket_count']}",
        f"- Triage accuracy: {summary['triage_accuracy']:.1%}",
        f"- Outcome accuracy: {summary['outcome_accuracy']:.1%}",
        f"- Tool-call correctness: {summary['tool_call_correctness']:.1%}",
        f"- Guardrail violations on adversarial set: {summary['guardrail_violations_adversarial']}",
        f"- Mean cost per ticket: ${summary['mean_cost_per_ticket']:.4f}",
        f"- p50 latency: {summary['p50_latency_ms']:.0f} ms",
        f"- p95 latency: {summary['p95_latency_ms']:.0f} ms",
        "",
        "## Triage Accuracy by Difficulty",
        "",
    ]
    for difficulty, value in summary["triage_accuracy_by_difficulty"].items():
        lines.append(f"- {difficulty}: {value:.1%}")
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary = run()
    json_path = RESULTS_DIR / f"run_{timestamp}.json"
    md_path = RESULTS_DIR / f"run_{timestamp}.md"
    json_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    md = markdown_summary(summary)
    md_path.write_text(md, encoding="utf-8")
    print(md)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
