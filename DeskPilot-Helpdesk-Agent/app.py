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


@st.cache_resource
def _ensure_kb_ingested() -> None:
    """Ingest KB articles into ChromaDB if the collection is empty."""
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
    st.caption("Autonomous IT/HR helpdesk triage and resolution for Acme Corp.")
    emails = load_employee_emails()
    sender_email = st.selectbox("Sender email", emails, index=0) if emails else st.text_input("Sender email")
    ticket_text = st.text_area("Ticket", height=180, placeholder="I'm locked out of my account and need help signing in.")
    submit = st.button("Submit ticket", type="primary")

    if submit:
        if not ticket_text.strip() or not sender_email.strip():
            st.warning("Enter both a sender email and ticket text.")
            return
        status = st.status("Starting DeskPilot...", expanded=True)

        def update(message: str) -> None:
            status.write(message)

        try:
            result = process_ticket(ticket_text.strip(), sender_email.strip(), progress=update)
        except Exception as exc:
            status.update(label="Run failed", state="error")
            st.error(str(exc))
            return

        status.update(label=f"Finished: {result.outcome}", state="complete")
        st.subheader("Result")
        if result.outcome == "resolved":
            st.success(result.message)
        elif result.outcome == "clarify":
            st.warning(result.message)
        else:
            st.error(result.message)

        st.write(f"Ticket ID: `{result.ticket_id}`")
        st.write(f"Category: `{result.classification.category}`")
        st.write(f"Confidence: `{result.classification.confidence:.2f}`")

        if result.tool_calls:
            st.subheader("Tool Calls")
            for index, call in enumerate(result.tool_calls, start=1):
                with st.expander(f"{index}. {call['tool']}"):
                    st.json(call)

        if result.handoff:
            st.subheader("Escalation Handoff")
            st.markdown(f"**Summary:** {result.handoff.summary}")
            st.markdown(f"**What was tried:** {result.handoff.what_was_tried}")
            st.markdown(f"**Suggested resolution:** {result.handoff.suggested_resolution}")
            st.markdown(f"**Relevant KB articles:** {', '.join(result.handoff.relevant_kb_articles) or 'None'}")
            st.markdown(f"**Suggested assignee queue:** {result.handoff.suggested_assignee_queue}")


def render_admin_dashboard() -> None:
    st.title("Admin Dashboard")
    metrics = ticket_metrics()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total tickets", metrics["total_tickets"])
    col2.metric("Autonomous resolution", f"{metrics['autonomous_resolution_rate']:.0%}")
    col3.metric("Avg cost", f"${metrics['avg_cost']:.4f}")
    col4.metric("p95 latency", f"{metrics['p95_latency_ms']} ms")

    col5, col6 = st.columns(2)
    col5.metric("p50 latency", f"{metrics['p50_latency_ms']} ms")
    col6.metric("Recent trace rows", len(read_recent_traces(500)))

    rows = []
    for event in read_recent_traces(2000):
        if event.get("agent") == "pipeline" and event.get("action") == "finish":
            rows.append(
                {
                    "id": event["ticket_id"],
                    "timestamp": event["timestamp"],
                    "category": "",
                    "outcome": event.get("output", {}).get("outcome", ""),
                    "cost": event.get("cost_usd", 0.0),
                    "latency": event.get("latency_ms", 0),
                }
            )
        if len(rows) >= 50:
            break
    st.dataframe(rows, use_container_width=True)

    with st.expander("Recent raw traces"):
        st.json(read_recent_traces(25))


def main() -> None:
    _ensure_kb_ingested()
    st.set_page_config(page_title="DeskPilot Lite", page_icon="DP", layout="wide")
    page = st.sidebar.radio("Page", ["Submit Ticket", "Admin Dashboard"])
    if page == "Submit Ticket":
        render_submit_ticket()
    else:
        render_admin_dashboard()


if __name__ == "__main__":
    main()
