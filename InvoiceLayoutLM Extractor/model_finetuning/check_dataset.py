"""Validate the invoice dataset structure before LayoutLMv3 fine-tuning."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

try:
    from .labels import LABEL_TO_ID
except ImportError:
    from labels import LABEL_TO_ID


REQUIRED_ANNOTATION_KEYS = {"id", "image_path", "words", "bboxes", "ner_tags"}


def has_explicit_splits(data_dir: Path) -> bool:
    """Return True when the dataset root already contains train/val/test folders."""
    return all((data_dir / split / "annotations").exists() for split in ("train", "val", "test"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a pre-split invoice dataset for LayoutLMv3 fine-tuning."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dataset",
        help="Dataset root containing train/val/test folders.",
    )
    return parser.parse_args()


def _validate_bbox(bbox: object, annotation_path: Path, token_index: int) -> None:
    if not isinstance(bbox, list) or len(bbox) != 4:
        raise ValueError(
            f"Invalid bbox at token {token_index} in {annotation_path}: {bbox!r}"
        )
    if not all(isinstance(value, int) for value in bbox):
        raise ValueError(
            f"Non-integer bbox at token {token_index} in {annotation_path}: {bbox!r}"
        )


def _validate_split(split_dir: Path, split: str) -> tuple[int, Counter[str]]:
    annotations_dir = split_dir / "annotations"
    metadata_dir = split_dir / "metadata"
    pdfs_dir = split_dir / "pdfs"

    label_counts: Counter[str] = Counter()
    annotation_files = sorted(annotations_dir.glob("invoice_*.json"))
    if not annotation_files:
        raise FileNotFoundError(f"No annotations found in {annotations_dir}")

    for annotation_path in annotation_files:
        annotation = json.loads(annotation_path.read_text(encoding="utf-8"))
        missing_keys = REQUIRED_ANNOTATION_KEYS - set(annotation)
        if missing_keys:
            missing_text = ", ".join(sorted(missing_keys))
            raise KeyError(f"{annotation_path} is missing keys: {missing_text}")

        invoice_id = annotation["id"]
        words = annotation["words"]
        bboxes = annotation["bboxes"]
        ner_tags = annotation["ner_tags"]

        if not isinstance(words, list) or not isinstance(bboxes, list) or not isinstance(ner_tags, list):
            raise TypeError(f"{annotation_path} must store words, bboxes, and ner_tags as lists.")
        if not (len(words) == len(bboxes) == len(ner_tags)):
            raise ValueError(
                f"Mismatched lengths in {annotation_path}: "
                f"{len(words)} words, {len(bboxes)} bboxes, {len(ner_tags)} labels"
            )

        for index, bbox in enumerate(bboxes):
            _validate_bbox(bbox, annotation_path, index)

        unknown_labels = sorted({label for label in ner_tags if label not in LABEL_TO_ID})
        if unknown_labels:
            raise ValueError(
                f"Unknown labels in {annotation_path}: {', '.join(unknown_labels)}"
            )

        image_path = split_dir / annotation["image_path"]
        if not image_path.exists():
            raise FileNotFoundError(
                f"Image referenced by {annotation_path} does not exist: {image_path}"
            )

        metadata_path = metadata_dir / f"{invoice_id}.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Missing metadata file: {metadata_path}")

        pdf_path = pdfs_dir / f"{invoice_id}.pdf"
        if not pdf_path.exists():
            raise FileNotFoundError(f"Missing PDF file: {pdf_path}")

        label_counts.update(ner_tags)

    print(f"{split}: {len(annotation_files)} documents validated")
    return len(annotation_files), label_counts


def main() -> None:
    args = parse_args()
    if not has_explicit_splits(args.data_dir):
        raise FileNotFoundError(
            f"{args.data_dir} does not contain train/val/test annotation folders."
        )

    total_docs = 0
    total_labels: Counter[str] = Counter()
    for split in ("train", "val", "test"):
        split_count, split_labels = _validate_split(args.data_dir / split, split)
        total_docs += split_count
        total_labels.update(split_labels)

    print(f"total: {total_docs} documents validated")
    print("label distribution:")
    for label, count in total_labels.most_common():
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
