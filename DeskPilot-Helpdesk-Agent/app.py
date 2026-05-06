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
    st.title("DeskPilot Lite")
    st.markdown(
        "Autonomous IT/HR helpdesk agent for Acme Corp — classifies tickets, "
        "resolves safe requests using real tools, and escalates with structured handoff notes."
    )
    st.divider()

    st.markdown("##### Try an example")
    cols = st.columns(len(EXAMPLE_TICKETS))
    for i, (label, text) in enumerate(EXAMPLE_TICKETS):
        if cols[i].button(label, use_container_width=True):
            st.session_state["ticket_input"] = text
            st.rerun()

    st.divider()

    emails = load_employee_emails()
    sender_email = (
        st.selectbox("Sender email", emails, index=0)
        if emails
        else st.text_input("Sender email")
    )
    ticket_text = st.text_area(
        "Describe your issue",
        height=150,
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

    # Outcome banner
    if result.outcome == "resolved":
        st.success(f"**Resolved** — {result.message}")
    elif result.outcome == "clarify":
        st.warning(f"**Needs clarification** — {result.message}")
    else:
        st.error(f"**Escalated** — {result.message}")

    # Ticket metadata
    c1, c2, c3 = st.columns(3)
    c1.metric("Ticket ID", result.ticket_id)
    c2.metric("Category", result.classification.category.replace("_", " ").title())
    c3.metric("Confidence", f"{result.classification.confidence:.0%}")

    # Tool calls
    if result.tool_calls:
        st.markdown("#### Agent Actions")
        for i, call in enumerate(result.tool_calls, 1):
            blocked = isinstance(call.get("result"), dict) and call["result"].get("blocked")
            label = f"{i}. `{call['tool']}`" + ("  —  BLOCKED" if blocked else "")
            with st.expander(label, expanded=blocked):
                st.json(call)

    # Escalation handoff
    if result.handoff:
        st.markdown("#### Escalation Handoff")
        queue = result.handoff.suggested_assignee_queue
        color = QUEUE_COLORS.get(queue, "gray")
        st.markdown(f"**Assigned queue:** :{color}[**{queue}**]")

        hc1, hc2 = st.columns(2)
        with hc1:
            st.markdown(f"**Summary**\n\n{result.handoff.summary}")
            st.markdown(f"**What was tried**\n\n{result.handoff.what_was_tried}")
        with hc2:
            st.markdown(f"**Suggested resolution**\n\n{result.handoff.suggested_resolution}")
            if result.handoff.relevant_kb_articles:
                articles = "\n".join(f"- {a}" for a in result.handoff.relevant_kb_articles)
                st.markdown(f"**Relevant KB articles**\n\n{articles}")


def render_admin_dashboard() -> None:
    st.title("Admin Dashboard")
    st.caption("Live metrics and trace log from the DeskPilot pipeline.")

    metrics = ticket_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total tickets", metrics["total_tickets"])
    c2.metric("Autonomous resolution", f"{metrics['autonomous_resolution_rate']:.0%}")
    c3.metric("Avg cost / ticket", f"${metrics['avg_cost']:.4f}")
    c4.metric("p95 latency", f"{metrics['p95_latency_ms']} ms")

    st.divider()
    st.markdown("#### Recent Tickets")

    rows = []
    for event in read_recent_traces(2000):
        if event.get("agent") == "pipeline" and event.get("action") == "finish":
            rows.append({
                "Ticket ID": event["ticket_id"],
                "Timestamp": event["timestamp"][:19].replace("T", " "),
                "Outcome": event.get("output", {}).get("outcome", ""),
                "Cost ($)": round(float(event.get("cost_usd", 0.0)), 4),
                "Latency (ms)": event.get("latency_ms", 0),
            })
        if len(rows) >= 50:
            break

    if rows:
        st.dataframe(
            rows,
            use_container_width=True,
            column_config={
                "Cost ($)": st.column_config.NumberColumn(format="$%.4f"),
                "Latency (ms)": st.column_config.NumberColumn(format="%d ms"),
            },
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

    if page == "Submit Ticket":
        render_submit_ticket()
    else:
        render_admin_dashboard()


if __name__ == "__main__":
    main()
