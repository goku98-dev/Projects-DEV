"""Ticket memory using SQLite metadata and ChromaDB similarity search."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

import chromadb

from deskpilot.config import CHROMA_DIR, MEMORY_DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(MEMORY_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            raw_text TEXT NOT NULL,
            sender_email TEXT NOT NULL,
            category TEXT NOT NULL,
            outcome TEXT NOT NULL,
            resolution_summary TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """
    )
    return conn


def _collection() -> chromadb.Collection:
    CHROMA_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection("ticket_memory")


def store_ticket(ticket_id: str, raw_text: str, sender_email: str, category: str, outcome: str, resolution_summary: str) -> None:
    """Store resolved/escalated ticket metadata and embedding."""
    conn = _connect()
    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO tickets
            (id, raw_text, sender_email, category, outcome, resolution_summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ticket_id, raw_text, sender_email, category, outcome, resolution_summary, datetime.now(timezone.utc).isoformat()),
        )
    conn.close()
    _collection().upsert(ids=[ticket_id], documents=[raw_text], metadatas=[{"ticket_id": ticket_id}])


def retrieve_similar(ticket_text: str, k: int = 3) -> list[dict[str, Any]]:
    """Retrieve similar past tickets by raw text."""
    try:
        collection = _collection()
        if collection.count() == 0:
            return []
        results = collection.query(query_texts=[ticket_text], n_results=max(1, min(k, 10)))
        ids = results.get("ids", [[]])[0]
        if not ids:
            return []
        conn = _connect()
        placeholders = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT raw_text, category, outcome, resolution_summary FROM tickets WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
        conn.close()
        return [
            {"raw_text": row[0], "category": row[1], "outcome": row[2], "resolution_summary": row[3]}
            for row in rows
        ]
    except Exception:
        return []


if __name__ == "__main__":
    store_ticket("smoke", "I forgot my password", "jane.doe@acme.com", "password_reset", "resolved", "Issued a temporary password.")
    print(retrieve_similar("locked out of account"))
