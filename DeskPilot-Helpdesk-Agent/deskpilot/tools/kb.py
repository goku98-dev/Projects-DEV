"""Knowledge base search using ChromaDB."""

from __future__ import annotations

from typing import Any

import chromadb

from deskpilot.config import CHROMA_DIR


def _client() -> chromadb.PersistentClient:
    CHROMA_DIR.mkdir(exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def search_kb(query: str, k: int = 3) -> list[dict[str, Any]] | dict[str, str]:
    """Search the ingested KB collection."""
    try:
        collection = _client().get_or_create_collection("kb_articles")
        if collection.count() == 0:
            return {"error": "kb_not_ingested"}
        result = collection.query(query_texts=[query], n_results=max(1, min(k, 10)))
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        hits: list[dict[str, Any]] = []
        for document, metadata, distance in zip(documents, metadatas, distances):
            clean = " ".join(str(document).split())
            hits.append(
                {
                    "title": metadata.get("title", "Untitled") if metadata else "Untitled",
                    "snippet": clean[:420],
                    "score": round(1 / (1 + float(distance)), 4),
                }
            )
        return hits
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    print(search_kb("How do I reset MFA?", 2))
