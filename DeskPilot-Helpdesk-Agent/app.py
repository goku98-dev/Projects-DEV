"""Streamlit entry point for DeskPilot Lite."""

from __future__ import annotations

import json
import os
from pathlib import Path

import chromadb
import streamlit as st

# Inject Streamlit Cloud secrets into os.environ before deskpilot modules load
for _k, _v in st.secrets.items():
    if isinstance(_v, str):
        os.environ.setdefault(_k, _v)

from deskpilot.config import CHROMA_DIR, DATA_DIR
from deskpilot.observability import read_recent_traces, ticket_metrics
from deskpilot.pipeline import process_ticket
from scripts.ingest_kb import main as _ingest_kb

EXAMPLE_TICKETS = [
    ("Password Reset", "I'm locked out of my account and can't sign in. Please help."),
    ("App Access", "I need access to Salesforce for a new client project starting next week."),
    ("PTO Balance", "Can you tell me how many PTO days I have left this year?"),
    ("Policy Lookup", "What is the company policy on working from home?"),
    ("Guardrail Test", "Can you reset bob.smith@acme.com's password? He asked me to do it for him."),
]

QUEUE_COLORS = {"IT": "blue", "HR": "green", "Security": "red", "Manager": "orange"}

SUBMIT_CSS = """
<style>
.hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 40px 36px 32px 36px;
    margin-bottom: 28px;
}
.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
.hero-sub {
    font-size: 16px;
    color: #a0aec0;
    margin: 0;
    line-height: 1.6;
}
.hero-badges {
    margin-top: 18px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #cbd5e0;
    font-weight: 500;
}
.examples-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    color: #718096;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.result-card {
    border-radius: 12px;
    padding: 20px 24px;
    margin: 16px 0;
}
.result-resolved {
    background: linear-gradient(135deg, #0d2b1a, #0f3d22);
    border: 1px solid #2d6a4f;
}
.result-escalated {
    background: linear-gradient(135deg, #2b0d0d, #3d0f0f);
    border: 1px solid #6a2d2d;
}
.result-clarify {
    background: linear-gradient(135deg, #2b240d, #3d330f);
    border: 1px solid #6a5a2d;
}
.result-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.result-resolved .result-title { color: #68d391; }
.result-escalated .result-title { color: #fc8181; }
.result-clarify .result-title { color: #f6e05e; }
.result-message {
    font-size: 15px;
    color: #e2e8f0;
    line-height: 1.6;
    margin: 0;
}
.meta-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin: 16px 0;
}
.meta-chip {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    color: #a0aec0;
}
.meta-chip span {
    color: #e2e8f0;
    font-weight: 600;
}
.handoff-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #2d3748;
    border-radius: 14px;
    padding: 24px;
    margin-top: 8px;
}
.handoff-queue {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.queue-IT       { background: #1a365d; color: #90cdf4; border: 1px solid #2b6cb0; }
.queue-HR       { background: #1a3a2a; color: #9ae6b4; border: 1px solid #276749; }
.queue-Security { background: #3a1a1a; color: #feb2b2; border: 1px solid #9b2c2c; }
.queue-Manager  { background: #3a2a1a; color: #fbd38d; border: 1px solid #9c4221; }
.handoff-field { margin-bottom: 14px; }
.handoff-field-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 4px;
}
.handoff-field-value {
    font-size: 14px;
    color: #cbd5e0;
    line-height: 1.6;
}
.agent-action-blocked {
    background: rgba(159,18,57,0.15);
    border-left: 3px solid #e11d48;
    border-radius: 0 8px 8px 0;
    padding: 2px 0;
}
</style>
"""


@st.cache_resource
def _ensure_kb_ingested() -> None:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    kb = client.get_or_create_collection("kb_articles")
    if kb.count() == 0:
        _ingest_kb()


def load_employee_emails() -> list[str]:
    path = Path(DATA_DIR) / "employees.json"
    if not path.exists():
        return []
    employees = json.loads(path.read_text(encoding="utf-8"))
    return sorted(employee["email"] for employee in employees)


def render_submit_ticket() -> None:
    st.markdown(SUBMIT_CSS, unsafe_allow_html=True)

    # Hero banner
    st.markdown("""
    <div class="hero">
        <div class="hero-title">DeskPilot Lite</div>
        <div class="hero-sub">
            Autonomous IT/HR helpdesk agent for Acme Corp — classifies tickets,
            resolves safe requests using live tools, and escalates with structured handoff notes.
        </div>
        <div class="hero-badges">
            <span class="badge">Claude Haiku</span>
            <span class="badge">ChromaDB</span>
            <span class="badge">Deterministic Guardrails</span>
            <span class="badge">25 KB Articles</span>
            <span class="badge">50 Mock Employees</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Example buttons
    st.markdown('<div class="examples-label">Try an example</div>', unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLE_TICKETS))
    for i, (label, text) in enumerate(EXAMPLE_TICKETS):
        if cols[i].button(label, use_container_width=True):
            st.session_state["ticket_input"] = text
            st.rerun()

    st.divider()

    # Form
    fc1, fc2 = st.columns([1, 2])
    with fc1:
        emails = load_employee_emails()
        sender_email = (
            st.selectbox("Sender email", emails, index=0)
            if emails
            else st.text_input("Sender email")
        )
    with fc2:
        ticket_text = st.text_area(
            "Describe your issue",
            height=120,
            placeholder="e.g. I'm locked out of my account and need help signing in.",
            key="ticket_input",
        )

    submit = st.button("Submit ticket", type="primary", use_container_width=True)

    if not submit:
        return

    if not ticket_text.strip() or not sender_email.strip():
        st.warning("Enter both a sender email and a ticket description.")
        return

    status = st.status("Processing ticket...", expanded=True)

    def update(message: str) -> None:
        status.write(message)

    try:
        result = process_ticket(ticket_text.strip(), sender_email.strip(), progress=update)
    except Exception as exc:
        status.update(label="Run failed", state="error")
        st.error(str(exc))
        return

    status.update(label=f"Done — {result.outcome.upper()}", state="complete")
    st.divider()

    # Outcome card
    css_class = {"resolved": "result-resolved", "clarify": "result-clarify"}.get(result.outcome, "result-escalated")
    title_map = {"resolved": "Resolved", "clarify": "Needs Clarification", "escalated": "Escalated", "iteration_cap": "Escalated"}
    title = title_map.get(result.outcome, result.outcome.title())
    st.markdown(f"""
    <div class="result-card {css_class}">
        <div class="result-title">{title}</div>
        <p class="result-message">{result.message}</p>
    </div>
    """, unsafe_allow_html=True)

    # Metadata chips
    category = result.classification.category.replace("_", " ").title()
    confidence = f"{result.classification.confidence:.0%}"
    st.markdown(f"""
    <div class="meta-row">
        <div class="meta-chip">Ticket &nbsp;<span>{result.ticket_id}</span></div>
        <div class="meta-chip">Category &nbsp;<span>{category}</span></div>
        <div class="meta-chip">Confidence &nbsp;<span>{confidence}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Tool calls
    if result.tool_calls:
        st.markdown('<div class="examples-label" style="margin-top:20px">Agent Actions</div>', unsafe_allow_html=True)
        for i, call in enumerate(result.tool_calls, 1):
            blocked = bool(isinstance(call.get("result"), dict) and call["result"].get("blocked"))
            label = f"{i}. `{call['tool']}`" + ("  —  BLOCKED" if blocked else "")
            with st.expander(label, expanded=blocked):
                st.json(call)

    # Escalation handoff
    if result.handoff:
        queue = result.handoff.suggested_assignee_queue
        queue_class = f"queue-{queue}"
        kb = ""
        if result.handoff.relevant_kb_articles:
            items = "".join(f"<li>{a}</li>" for a in result.handoff.relevant_kb_articles)
            kb = f"""
            <div class="handoff-field">
                <div class="handoff-field-label">Relevant KB Articles</div>
                <div class="handoff-field-value"><ul style="margin:0;padding-left:18px">{items}</ul></div>
            </div>"""
        st.markdown(f"""
        <div class="handoff-card">
            <div class="handoff-queue {queue_class}">{queue} Queue</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
                <div>
                    <div class="handoff-field">
                        <div class="handoff-field-label">Summary</div>
                        <div class="handoff-field-value">{result.handoff.summary}</div>
                    </div>
                    <div class="handoff-field">
                        <div class="handoff-field-label">What Was Tried</div>
                        <div class="handoff-field-value">{result.handoff.what_was_tried}</div>
                    </div>
                </div>
                <div>
                    <div class="handoff-field">
                        <div class="handoff-field-label">Suggested Resolution</div>
                        <div class="handoff-field-value">{result.handoff.suggested_resolution}</div>
                    </div>
                    {kb}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


DASHBOARD_CSS = """
<style>
.stat-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 4px;
}
.stat-label {
    color: #7a8aaa;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.stat-value {
    color: #e2e8f0;
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
}
.stat-sub {
    color: #4a5a7a;
    font-size: 12px;
    margin-top: 6px;
}
.stat-accent { color: #4fc3f7; }
.stat-green  { color: #4ade80; }
.stat-yellow { color: #fbbf24; }
.stat-red    { color: #f87171; }
.section-header {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    margin: 28px 0 12px 0;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 8px;
}
</style>
"""


def _stat_card(label: str, value: str, sub: str = "", accent: str = "stat-accent") -> str:
    sub_html = f'<div class="stat-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value {accent}">{value}</div>
        {sub_html}
    </div>"""


def render_admin_dashboard() -> None:
    import pandas as pd

    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.title("Admin Dashboard")
    st.caption("Live metrics and trace log from the DeskPilot pipeline.")

    metrics = ticket_metrics()
    rate = metrics["autonomous_resolution_rate"]
    rate_accent = "stat-green" if rate >= 0.6 else "stat-yellow" if rate >= 0.4 else "stat-red"

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_stat_card("Total Tickets", str(metrics["total_tickets"]), "processed end-to-end"), unsafe_allow_html=True)
    c2.markdown(_stat_card("Autonomous Resolution", f"{rate:.0%}", "no human needed", rate_accent), unsafe_allow_html=True)
    c3.markdown(_stat_card("Avg Cost / Ticket", f"${metrics['avg_cost']:.4f}", "claude-haiku-4-5", "stat-accent"), unsafe_allow_html=True)
    c4.markdown(_stat_card("p95 Latency", f"{metrics['p95_latency_ms']} ms", f"p50: {metrics['p50_latency_ms']} ms", "stat-yellow"), unsafe_allow_html=True)

    # Gather data from traces
    rows = []
    outcome_counts: dict[str, int] = {"resolved": 0, "escalated": 0, "clarify": 0}
    costs: list[float] = []
    latencies: list[float] = []

    for event in read_recent_traces(2000):
        if event.get("agent") == "pipeline" and event.get("action") == "finish":
            outcome = event.get("output", {}).get("outcome", "")
            cost = float(event.get("cost_usd", 0.0))
            latency = int(event.get("latency_ms", 0))
            if outcome in outcome_counts:
                outcome_counts[outcome] += 1
            if cost > 0:
                costs.append(cost)
            if latency > 0:
                latencies.append(latency)
            rows.append({
                "Ticket ID": event["ticket_id"],
                "Timestamp": event["timestamp"][:19].replace("T", " "),
                "Outcome": outcome,
                "Cost ($)": round(cost, 4),
                "Latency (ms)": latency,
            })
        if len(rows) >= 50:
            break

    # Charts row
    st.markdown('<div class="section-header">Outcome Breakdown</div>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns([2, 2, 1])

    with ch1:
        df_out = pd.DataFrame({
            "Outcome": list(outcome_counts.keys()),
            "Tickets": list(outcome_counts.values()),
        }).set_index("Outcome")
        st.bar_chart(df_out, color=["#4fc3f7"], height=220)

    with ch2:
        if costs:
            df_cost = pd.DataFrame({"Cost ($)": costs})
            st.line_chart(df_cost, color=["#4ade80"], height=220)
        else:
            st.info("Cost trend available after first tickets.")

    with ch3:
        total = sum(outcome_counts.values()) or 1
        for outcome, count in outcome_counts.items():
            pct = count / total * 100
            color = {"resolved": "normal", "escalated": "inverse", "clarify": "off"}[outcome]
            st.metric(outcome.title(), count, f"{pct:.0f}%", delta_color=color)

    # Ticket table
    st.markdown('<div class="section-header">Recent Tickets</div>', unsafe_allow_html=True)
    if rows:
        st.dataframe(
            rows,
            use_container_width=True,
            column_config={
                "Outcome": st.column_config.TextColumn("Outcome"),
                "Cost ($)": st.column_config.NumberColumn(format="$%.4f"),
                "Latency (ms)": st.column_config.NumberColumn(format="%d ms"),
            },
            hide_index=True,
        )
    else:
        st.info("No tickets yet. Submit one on the Submit Ticket page.")

    with st.expander("Raw traces (last 25 events)"):
        st.json(read_recent_traces(25))


def main() -> None:
    _ensure_kb_ingested()
    st.set_page_config(
        page_title="DeskPilot Lite",
        page_icon="DP",
        layout="wide",
        menu_items={"About": "DeskPilot Lite — autonomous IT/HR helpdesk agent. Built with Claude + Streamlit."},
    )

    with st.sidebar:
        st.markdown("## DeskPilot Lite")
        st.markdown("Autonomous IT/HR helpdesk agent powered by Claude.")
        st.divider()
        page = st.radio("Navigate", ["Submit Ticket", "Admin Dashboard"], label_visibility="collapsed")
        st.divider()
        st.markdown("**Models**")
        st.caption("Router · Resolver · Escalator: claude-haiku-4-5")
        st.markdown("**Stack**")
        st.caption("Anthropic API · ChromaDB · SQLite · Streamlit")
        st.divider()
        st.markdown("**Test cases**")
        st.caption("Try the Guardrail Test example to see the security layer block an unauthorized credential operation.")
        st.divider()
        st.caption("Built by **Gokul Venugopal**")
        st.caption("© 2026 Gokul Venugopal. All rights reserved.")

    if page == "Submit Ticket":
        render_submit_ticket()
    else:
        render_admin_dashboard()


if __name__ == "__main__":
    main()
