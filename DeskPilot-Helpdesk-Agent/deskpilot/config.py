"""Configuration for DeskPilot Lite."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
KB_DIR = DATA_DIR / "kb"
CHROMA_DIR = ROOT_DIR / "chroma_db"
TRACES_DIR = ROOT_DIR / "traces"
EVAL_DIR = ROOT_DIR / "eval"
MEMORY_DB_PATH = ROOT_DIR / "ticket_memory.db"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "claude-haiku-4-5-20251001")
RESOLVER_MODEL = os.getenv("RESOLVER_MODEL", "claude-haiku-4-5-20251001")
ESCALATOR_MODEL = os.getenv("ESCALATOR_MODEL", "claude-haiku-4-5-20251001")

MAX_RESOLVER_ITERATIONS = 6

# Update these constants if Anthropic pricing changes.
MODEL_PRICING_USD_PER_1M_TOKENS: dict[str, dict[str, float]] = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 0.80, "output": 4.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
}


def require_api_key() -> str:
    """Return the Anthropic API key or raise a clear setup error."""
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_api_key_here":
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to .env before running agents.")
    return ANTHROPIC_API_KEY


def cost_for_tokens(model: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate API cost for a model call."""
    pricing = MODEL_PRICING_USD_PER_1M_TOKENS.get(model, {"input": 0.0, "output": 0.0})
    return (tokens_in * pricing["input"] + tokens_out * pricing["output"]) / 1_000_000


if __name__ == "__main__":
    print(f"DeskPilot root: {ROOT_DIR}")
    print(f"Router model: {ROUTER_MODEL}")
