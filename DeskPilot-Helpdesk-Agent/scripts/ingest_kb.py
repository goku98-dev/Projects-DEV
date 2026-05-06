"""Ingest Acme Corp KB markdown files into ChromaDB."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deskpilot.config import CHROMA_DIR, KB_DIR


def title_from_markdown(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else fallback


def main() -> None:
    CHROMA_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection("kb_articles")
    files = sorted(Path(KB_DIR).glob("*.md"))
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        ids.append(path.stem)
        documents.append(text)
        metadatas.append({"title": title_from_markdown(text, path.stem), "source": path.name})
    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Ingested {len(ids)} KB articles into {CHROMA_DIR}.")


if __name__ == "__main__":
    main()
