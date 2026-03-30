"""Shared label definitions for invoice table token classification."""

ENTITY_LABELS: list[str] = [
    "item_description",
    "quantity",
    "unit_price",
    "line_total",
    "tax",
    "position",
    "article_number",
]

LABELS: list[str] = ["O"]
for entity in ENTITY_LABELS:
    LABELS.append(f"B-{entity}")
    LABELS.append(f"I-{entity}")

LABEL_TO_ID: dict[str, int] = {label: idx for idx, label in enumerate(LABELS)}
ID_TO_LABEL: dict[int, str] = {idx: label for label, idx in LABEL_TO_ID.items()}

