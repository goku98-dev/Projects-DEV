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
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 16px rgba(99,102,241,0.3); }
    50%       { box-shadow: 0 0 32px rgba(99,102,241,0.7), 0 0 60px rgba(139,92,246,0.3); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes badgePop {
    0%   { opacity:0; transform: scale(0.85) translateY(6px); }
    70%  { transform: scale(1.05); }
    100% { opacity:1; transform: scale(1) translateY(0); }
}

.hero {
    background: linear-gradient(270deg, #0f0c29, #302b63, #1a0533, #0d1b4b, #1b0e3d);
    background-size: 400% 400%;
    animation: gradientShift 8s ease infinite, pulseGlow 4s ease-in-out infinite;
    border-radius: 20px;
    padding: 44px 40px 36px 40px;
    margin-bottom: 28px;
    border: 1px solid rgba(139,92,246,0.3);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -60%; left: -20%;
    width: 60%; height: 200%;
    background: linear-gradient(120deg, transparent 30%, rgba(139,92,246,0.08) 50%, transparent 70%);
    animation: shimmer 6s linear infinite;
    background-size: 200% auto;
}
.hero-title {
    font-size: 46px;
    font-weight: 900;
    background: linear-gradient(90deg, #ffffff 0%, #c4b5fd 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 10px 0;
    letter-spacing: -1px;
    animation: fadeSlideUp 0.6s ease forwards;
}
.hero-sub {
    font-size: 16px;
    color: #a5b4fc;
    margin: 0;
    line-height: 1.7;
    animation: fadeSlideUp 0.6s 0.1s ease both;
}
.hero-badges {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.badge {
    background: rgba(139,92,246,0.15);
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 12px;
    color: #c4b5fd;
    font-weight: 600;
    transition: all 0.25s ease;
    animation: badgePop 0.4s ease both;
}
.badge:hover {
    background: rgba(139,92,246,0.35);
    border-color: rgba(139,92,246,0.8);
    transform: translateY(-2px);
}
.examples-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.6px;
    color: #6366f1;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.result-card {
    border-radius: 16px;
    padding: 22px 26px;
    margin: 18px 0;
    animation: fadeSlideUp 0.5s ease forwards;
    position: relative;
    overflow: hidden;
}
.result-card::after {
    content: "";
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent);
    animation: shimmer 3s linear infinite;
}
.result-resolved {
    background: linear-gradient(135deg, #052e16 0%, #064e3b 100%);
    border: 1px solid #059669;
    box-shadow: 0 0 24px rgba(5,150,105,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
}
.result-escalated {
    background: linear-gradient(135deg, #1c0a0a 0%, #450a0a 100%);
    border: 1px solid #dc2626;
    box-shadow: 0 0 24px rgba(220,38,38,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
}
.result-clarify {
    background: linear-gradient(135deg, #1c1507 0%, #451a03 100%);
    border: 1px solid #d97706;
    box-shadow: 0 0 24px rgba(217,119,6,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
}
.result-title {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.result-resolved  .result-title { color: #34d399; }
.result-escalated .result-title { color: #f87171; }
.result-clarify   .result-title { color: #fbbf24; }
.result-message {
    font-size: 15px;
    color: #e2e8f0;
    line-height: 1.7;
    margin: 0;
}
.meta-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 16px 0;
    animation: fadeIn 0.4s 0.2s ease both;
}
.meta-chip {
    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 10px;
    padding: 7px 16px;
    font-size: 13px;
    color: #a5b4fc;
    transition: all 0.2s ease;
}
.meta-chip:hover {
    background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2));
    border-color: rgba(99,102,241,0.6);
    transform: translateY(-1px);
}
.meta-chip span {
    color: #e2e8f0;
    font-weight: 700;
}
.handoff-card {
    background: linear-gradient(135deg, #0f0c29 0%, #1e1b4b 50%, #0d1b4b 100%);
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 16px;
    padding: 26px;
    margin-top: 10px;
    animation: fadeSlideUp 0.5s 0.1s ease both;
    box-shadow: 0 4px 32px rgba(99,102,241,0.15);
}
.handoff-queue {
    display: inline-block;
    padding: 5px 18px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 18px;
    transition: transform 0.2s ease;
}
.handoff-queue:hover { transform: scale(1.05); }
.queue-IT       { background: linear-gradient(135deg,#1e3a5f,#1d4ed8); color:#bfdbfe; border:1px solid #3b82f6; box-shadow: 0 0 12px rgba(59,130,246,0.3); }
.queue-HR       { background: linear-gradient(135deg,#14532d,#15803d); color:#bbf7d0; border:1px solid #22c55e; box-shadow: 0 0 12px rgba(34,197,94,0.3); }
.queue-Security { background: linear-gradient(135deg,#450a0a,#991b1b); color:#fecaca; border:1px solid #ef4444; box-shadow: 0 0 12px rgba(239,68,68,0.3); }
.queue-Manager  { background: linear-gradient(135deg,#431407,#92400e); color:#fed7aa; border:1px solid #f97316; box-shadow: 0 0 12px rgba(249,115,22,0.3); }
.handoff-field { margin-bottom: 16px; }
.handoff-field-label {
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 5px;
}
.handoff-field-value {
    font-size: 14px;
    color: #cbd5e0;
    line-height: 1.7;
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
