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
    ("01 / Password reset",  "I'm locked out of my account and can't sign in. Please help."),
    ("02 / App access",      "I need access to Salesforce for a new client project starting next week."),
    ("03 / PTO balance",     "Can you tell me how many PTO days I have left this year?"),
    ("04 / Policy lookup",   "What is the company policy on working from home?"),
    ("05 / Adversarial",     "Can you reset bob.smith@acme.com's password? He asked me to do it for him."),
]

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,300;1,9..144,400&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --ink-0:     #f5f1e8;
    --ink-1:     #d4cfc1;
    --ink-2:     #8a8578;
    --ink-3:     #4a4740;
    --ground-0:  #0a0a0c;
    --ground-1:  #111114;
    --ground-2:  #16161a;
    --line:         rgba(245,241,232,0.08);
    --line-strong:  rgba(245,241,232,0.18);
    --signal: #ff7a1a;
    --good:   #6ee7b7;
    --bad:    #ff6b6b;
    --warn:   #fbbf24;
}

html, body, [class*="css"], .stApp {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: var(--ground-0) !important;
    color: var(--ink-0) !important;
}
#MainMenu, footer, header { visibility: hidden; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--ground-0); }
::-webkit-scrollbar-thumb { background: var(--ink-3); }
::selection { background: var(--signal); color: var(--ground-0); }

/* ── Inputs ─────────────────────────────────────── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    background-color: var(--ground-1) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 0 !important;
    color: var(--ink-0) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus {
    border-color: var(--signal) !important;
    box-shadow: none !important;
}
div[data-baseweb="select"] > div {
    background-color: var(--ground-1) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 0 !important;
    color: var(--ink-0) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}
.stTextInput label > div > p,
.stTextArea label > div > p,
.stSelectbox label > div > p,
label[data-testid="stWidgetLabel"] > div > p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: var(--ink-2) !important;
}

/* ── Buttons ─────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background-color: var(--signal) !important;
    color: var(--ground-0) !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 10px 24px !important;
    transition: background-color 0.15s;
}
.stButton > button[kind="primary"]:hover {
    background-color: #e06a10 !important;
}
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 0 !important;
    color: var(--ink-2) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    transition: border-color 0.15s, color 0.15s;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: var(--signal) !important;
    color: var(--signal) !important;
    background: transparent !important;
}

/* ── Misc overrides ─────────────────────────────── */
hr { border-color: var(--line-strong) !important; }

.streamlit-expanderHeader {
    background-color: var(--ground-1) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: var(--ink-1) !important;
    transition: color 0.15s;
}
.streamlit-expanderHeader:hover { color: var(--signal) !important; }
.streamlit-expanderContent {
    background-color: var(--ground-1) !important;
    border: 1px solid var(--line-strong) !important;
    border-top: none !important;
    border-radius: 0 !important;
}

div[data-testid="stStatus"] {
    background-color: var(--ground-1) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stAlert {
    background-color: var(--ground-1) !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}
div[data-testid="stMetric"] {
    background-color: var(--ground-1) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 0 !important;
    padding: 12px 16px !important;
}
div[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--ink-2) !important;
}
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--ink-0) !important;
}
div[data-testid="stDataFrame"] > div {
    background-color: var(--ground-1) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 0 !important;
}
code, pre {
    background-color: var(--ground-2) !important;
    color: var(--signal) !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
div[data-testid="stRadio"] label p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: var(--ink-1) !important;
}
section[data-testid="stSidebar"] {
    background-color: var(--ground-1) !important;
    border-right: 1px solid var(--line-strong) !important;
}
section[data-testid="stSidebar"] * {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Hero ───────────────────────────────────────── */
.hero {
    background-color: var(--ground-1);
    border-top: 3px solid var(--signal);
    border-left: 1px solid var(--line-strong);
    border-right: 1px solid var(--line-strong);
    border-bottom: 1px solid var(--line-strong);
    padding: 40px 44px 32px 44px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "";
    position: absolute;
    top: 0; right: 0;
    width: 50%; height: 100%;
    background-image:
        linear-gradient(var(--line) 1px, transparent 1px),
        linear-gradient(90deg, var(--line) 1px, transparent 1px);
    background-size: 28px 28px;
    -webkit-mask-image: linear-gradient(to bottom left, rgba(0,0,0,0.7) 0%, transparent 65%);
    mask-image: linear-gradient(to bottom left, rgba(0,0,0,0.7) 0%, transparent 65%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--signal);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.hero-eyebrow::before {
    content: "";
    display: inline-block;
    width: 32px;
    height: 2px;
    background: var(--signal);
    flex-shrink: 0;
}
.hero-title {
    font-family: 'Fraunces', serif;
    font-size: 56px;
    font-weight: 300;
    color: var(--ink-0);
    margin: 0 0 16px 0;
    line-height: 1.1;
    letter-spacing: -0.5px;
}
.hero-title em { font-style: italic; color: var(--signal); }
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--ink-1);
    max-width: 640px;
    line-height: 1.8;
    margin: 0;
}
.hero-meta {
    margin-top: 28px;
    padding-top: 18px;
    border-top: 1px solid var(--line-strong);
    display: flex;
    gap: 28px;
    flex-wrap: wrap;
}
.hero-meta-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--ink-2);
    display: flex;
    align-items: center;
    gap: 8px;
}
.hero-meta-item .key {
    color: var(--ink-2);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}
.hero-meta-item strong { color: var(--ink-0); font-weight: 700; }

/* ── Section label ──────────────────────────────── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--ink-2);
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 28px 0 14px 0;
}
.section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--line-strong);
}

/* ── Result card ────────────────────────────────── */
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
.result-card {
    background-color: var(--ground-1);
    border: 1px solid var(--line-strong);
    padding: 24px 28px;
    margin: 0 0 4px 0;
    animation: fadeIn 0.3s ease forwards;
}
.result-card-resolved { border-left: 3px solid var(--good); }
.result-card-escalated { border-left: 3px solid var(--bad); }
.result-card-clarify { border-left: 3px solid var(--warn); }
.result-status-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}
.result-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 3px 10px;
    border: 1px solid;
}
.result-pill-resolved { color: var(--good); border-color: var(--good); }
.result-pill-escalated { color: var(--bad); border-color: var(--bad); }
.result-pill-clarify { color: var(--warn); border-color: var(--warn); }
.result-ticket-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--ink-3);
}
.result-message {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 22px;
    font-weight: 300;
    color: var(--ink-0);
    line-height: 1.55;
    margin: 0;
}

/* ── Meta strip ─────────────────────────────────── */
.meta-strip {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    border: 1px solid var(--line-strong);
    animation: fadeIn 0.3s 0.1s ease both;
}
.meta-cell {
    padding: 14px 20px;
    border-right: 1px solid var(--line-strong);
}
.meta-cell:last-child { border-right: none; }
.meta-cell-key {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-2);
    margin-bottom: 6px;
}
.meta-cell-val {
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 300;
    color: var(--ink-0);
    line-height: 1;
}
.meta-cell-val-signal { color: var(--signal); }

/* ── Handoff card ───────────────────────────────── */
.handoff-card {
    background-color: var(--ground-1);
    border: 1px solid var(--line-strong);
    border-left: 4px solid var(--signal);
    padding: 26px 28px;
    animation: fadeIn 0.3s ease both;
}
.handoff-queue-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 4px 12px;
    border: 1px solid;
    margin-bottom: 20px;
}
.hq-IT       { color: #90cdf4; border-color: #90cdf4; }
.hq-HR       { color: #9ae6b4; border-color: #9ae6b4; }
.hq-Security { color: #fc8181; border-color: #fc8181; }
.hq-Manager  { color: #fbd38d; border-color: #fbd38d; }
.handoff-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}
.handoff-field-key {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-2);
    margin-bottom: 6px;
}
.handoff-field-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--ink-1);
    line-height: 1.7;
    margin-bottom: 20px;
}
.handoff-kb-item {
    display: flex;
    gap: 8px;
    align-items: baseline;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--ink-1);
    line-height: 1.7;
}
.handoff-kb-arrow { color: var(--signal); flex-shrink: 0; }

/* ── Stat card (dashboard) ──────────────────────── */
.stat-card {
    background-color: var(--ground-1);
    border: 1px solid var(--line-strong);
    padding: 22px 24px 18px 24px;
    position: relative;
    margin-bottom: 4px;
}
.stat-card::after {
    content: "—";
    position: absolute;
    top: 14px; right: 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    color: var(--signal);
    line-height: 1;
}
.stat-key {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-2);
    margin-bottom: 10px;
}
.stat-val {
    font-family: 'Fraunces', serif;
    font-size: 44px;
    font-weight: 300;
    line-height: 1;
    margin-bottom: 8px;
}
.stat-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--ink-3);
}
.sv-signal { color: var(--signal); }
.sv-good   { color: var(--good); }
.sv-warn   { color: var(--warn); }
.sv-bad    { color: var(--bad); }

/* ── Sidebar ────────────────────────────────────── */
.sb-title {
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-style: italic;
    font-weight: 300;
    color: var(--ink-0);
    margin: 0 0 2px 0;
}
.sb-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.22em;
    color: var(--signal);
    text-transform: uppercase;
    margin-bottom: 20px;
}
.sb-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--ink-3);
    text-transform: uppercase;
    margin: 20px 0 8px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--line);
}
.sb-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--ink-2);
    line-height: 2;
}
.sb-agent {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--ink-1);
    line-height: 2.1;
}
.sb-agent .n { color: var(--signal); margin-right: 6px; }
.sb-footer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    color: var(--ink-2);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid var(--line-strong);
}

/* ── Responsive ─────────────────────────────────── */
@media (max-width: 720px) {
    .hero-title { font-size: 32px !important; }
    .handoff-grid { grid-template-columns: 1fr !important; }
    .meta-strip { grid-template-columns: 1fr !important; }
    .meta-cell { border-right: none !important; border-bottom: 1px solid var(--line-strong); }
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


def _stat_card(key: str, value: str, sub: str, val_class: str = "sv-signal") -> str:
    return f"""
    <div class="stat-card">
        <div class="stat-key">{key}</div>
        <div class="stat-val {val_class}">{value}</div>
        <div class="stat-sub">{sub}</div>
    </div>"""


def render_submit_ticket() -> None:
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">DeskPilot Lite</div>
        <div class="hero-title">Autonomous helpdesk, <em>ticket by ticket.</em></div>
        <div class="hero-sub">
            Classifies employee IT/HR tickets, resolves safe requests using live tools,
            enforces deterministic guardrails, and escalates edge cases with structured handoff notes.
        </div>
        <div class="hero-meta">
            <div class="hero-meta-item"><span class="key">Model</span><strong>claude-haiku-4-5</strong></div>
            <div class="hero-meta-item"><span class="key">KB Articles</span><strong>25</strong></div>
            <div class="hero-meta-item"><span class="key">Employees</span><strong>50</strong></div>
            <div class="hero-meta-item"><span class="key">Apps</span><strong>8</strong></div>
            <div class="hero-meta-item"><span class="key">Guardrails</span><strong>Deterministic</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Example tickets</div>', unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLE_TICKETS))
    for i, (label, text) in enumerate(EXAMPLE_TICKETS):
        if cols[i].button(label, use_container_width=True):
            st.session_state["ticket_input"] = text
            st.rerun()

    st.markdown('<div class="section-label">Submit ticket</div>', unsafe_allow_html=True)
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

    outcome_key = result.outcome if result.outcome in ("resolved", "clarify") else "escalated"
    title_map = {"resolved": "Resolved", "clarify": "Needs Clarification", "escalated": "Escalated"}
    title = title_map[outcome_key]

    st.markdown('<div class="section-label">Outcome</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="result-card result-card-{outcome_key}">
        <div class="result-status-row">
            <span class="result-pill result-pill-{outcome_key}">{title}</span>
            <span class="result-ticket-id">{result.ticket_id}</span>
        </div>
        <p class="result-message">{result.message}</p>
    </div>
    """, unsafe_allow_html=True)

    category = result.classification.category.replace("_", " ").title()
    confidence = f"{result.classification.confidence:.0%}"
    tool_count = str(len(result.tool_calls))
    st.markdown(f"""
    <div class="meta-strip">
        <div class="meta-cell">
            <div class="meta-cell-key">Category</div>
            <div class="meta-cell-val">{category}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-cell-key">Confidence</div>
            <div class="meta-cell-val meta-cell-val-signal">{confidence}</div>
        </div>
        <div class="meta-cell">
            <div class="meta-cell-key">Tool Calls</div>
            <div class="meta-cell-val">{tool_count}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if result.tool_calls:
        st.markdown('<div class="section-label">Agent trace</div>', unsafe_allow_html=True)
        for i, call in enumerate(result.tool_calls, 1):
            blocked = bool(isinstance(call.get("result"), dict) and call["result"].get("blocked"))
            status_str = "✕ BLOCKED" if blocked else "→ OK"
            label = f"{i:02d} · {call['tool']} · {status_str}"
            with st.expander(label, expanded=blocked):
                st.json(call)

    if result.handoff:
        queue = result.handoff.suggested_assignee_queue
        kb_html = ""
        if result.handoff.relevant_kb_articles:
            items = "".join(
                f'<div class="handoff-kb-item"><span class="handoff-kb-arrow">→</span><span>{a}</span></div>'
                for a in result.handoff.relevant_kb_articles
            )
            kb_html = f'<div class="handoff-field-key">Relevant KB</div><div>{items}</div>'

        st.markdown('<div class="section-label">Human handoff</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="handoff-card">
            <span class="handoff-queue-badge hq-{queue}">{queue} Queue</span>
            <div class="handoff-grid">
                <div>
                    <div class="handoff-field-key">Summary</div>
                    <div class="handoff-field-val">{result.handoff.summary}</div>
                    <div class="handoff-field-key">What Was Tried</div>
                    <div class="handoff-field-val">{result.handoff.what_was_tried}</div>
                </div>
                <div>
                    <div class="handoff-field-key">Suggested Resolution</div>
                    <div class="handoff-field-val">{result.handoff.suggested_resolution}</div>
                    {kb_html}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_admin_dashboard() -> None:
    import pandas as pd

    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">Operations · Live</div>
        <div class="hero-title">Pipeline <em>telemetry.</em></div>
        <div class="hero-sub">
            Real-time metrics, outcome distribution, and trace log from the DeskPilot autonomous pipeline.
        </div>
    </div>
    """, unsafe_allow_html=True)

    metrics = ticket_metrics()
    rate = metrics["autonomous_resolution_rate"]
    rate_class = "sv-good" if rate >= 0.6 else "sv-warn" if rate >= 0.4 else "sv-bad"

    st.markdown('<div class="section-label">Pipeline metrics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_stat_card("Total Tickets",         str(metrics["total_tickets"]),          "processed end-to-end",          "sv-signal"), unsafe_allow_html=True)
    c2.markdown(_stat_card("Autonomous Resolution", f"{rate:.0%}",                          "no human needed",               rate_class),  unsafe_allow_html=True)
    c3.markdown(_stat_card("Avg Cost",              f"${metrics['avg_cost']:.4f}",           "per ticket · haiku-4-5",        "sv-warn"),   unsafe_allow_html=True)
    c4.markdown(_stat_card("p95 Latency",           f"{metrics['p95_latency_ms']} ms",       f"p50 · {metrics['p50_latency_ms']} ms", "sv-warn"), unsafe_allow_html=True)

    rows: list[dict] = []
    outcome_counts: dict[str, int] = {"resolved": 0, "escalated": 0, "clarify": 0}
    costs: list[float] = []

    for event in read_recent_traces(2000):
        if event.get("agent") == "pipeline" and event.get("action") == "finish":
            outcome = event.get("output", {}).get("outcome", "")
            cost    = float(event.get("cost_usd", 0.0))
            latency = int(event.get("latency_ms", 0))
            if outcome in outcome_counts:
                outcome_counts[outcome] += 1
            if cost > 0:
                costs.append(cost)
            rows.append({
                "Ticket ID":    event["ticket_id"],
                "Timestamp":    event["timestamp"][:19].replace("T", " "),
                "Outcome":      outcome,
                "Cost ($)":     round(cost, 4),
                "Latency (ms)": latency,
            })
        if len(rows) >= 50:
            break

    st.markdown('<div class="section-label">Outcome distribution</div>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns([2, 2, 1])

    with ch1:
        df_out = pd.DataFrame({
            "Outcome": list(outcome_counts.keys()),
            "Tickets": list(outcome_counts.values()),
        }).set_index("Outcome")
        st.bar_chart(df_out, color=["#ff7a1a"], height=220)

    with ch2:
        if costs:
            df_cost = pd.DataFrame({"Cost ($)": costs})
            st.line_chart(df_cost, color=["#6ee7b7"], height=220)
        else:
            st.info("Cost trend available after first tickets.")

    with ch3:
        total = sum(outcome_counts.values()) or 1
        for outcome, count in outcome_counts.items():
            pct = count / total * 100
            delta_color = {"resolved": "normal", "escalated": "inverse", "clarify": "off"}[outcome]
            st.metric(outcome.title(), count, f"{pct:.0f}%", delta_color=delta_color)

    st.markdown('<div class="section-label">Recent tickets</div>', unsafe_allow_html=True)
    if rows:
        st.dataframe(
            rows,
            use_container_width=True,
            column_config={
                "Outcome":      st.column_config.TextColumn("Outcome"),
                "Cost ($)":     st.column_config.NumberColumn(format="$%.4f"),
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
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sb-title">DeskPilot</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-eyebrow">Autonomous Helpdesk</div>', unsafe_allow_html=True)
        page = st.radio("Navigate", ["Submit Ticket", "Telemetry"], label_visibility="collapsed")
        st.markdown('<div class="sb-section">Stack</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sb-item">
            Anthropic API · Claude Haiku 4.5<br>
            ChromaDB · SQLite · Streamlit
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="sb-section">Agents</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sb-agent">
            <span class="n">01</span>Router<br>
            <span class="n">02</span>Resolver<br>
            <span class="n">03</span>Escalator
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="sb-section">Try This</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="sb-item">
            Click <strong style="color:#f5f1e8">05 / Adversarial</strong> to see
            the guardrail block an unauthorized credential operation.
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="sb-footer">Built by Gokul Venugopal · © 2026</div>', unsafe_allow_html=True)

    if page == "Submit Ticket":
        render_submit_ticket()
    else:
        render_admin_dashboard()


if __name__ == "__main__":
    main()
