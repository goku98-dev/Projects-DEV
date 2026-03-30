"""Dataset loading and split helpers for LayoutLMv3 fine-tuning."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from torch.utils.data import Dataset

try:
    from .labels import LABEL_TO_ID
except ImportError:
    from labels import LABEL_TO_ID


@dataclass(frozen=True)
class AnnotationExample:
    invoice_id: str
    image_path: Path
    words: list[str]
    bboxes: list[list[int]]
    ner_tags: list[str]
    template: str | None = None


def _clip_bbox(bbox: list[int]) -> list[int]:
    return [max(0, min(1000, int(value))) for value in bbox]


def _load_template_name(metadata_path: Path) -> str | None:
    if not metadata_path.exists():
        return None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return metadata.get("template")


def load_examples(data_dir: Path) -> list[AnnotationExample]:
    """Load annotation examples from a generated dataset directory."""
    annotations_dir = data_dir / "annotations"
    metadata_dir = data_dir / "metadata"

    if not annotations_dir.exists():
        raise FileNotFoundError(
            f"Annotations directory not found: {annotations_dir}. "
            "Run data_generation/annotate.py first."
        )

    examples: list[AnnotationExample] = []
    for annotation_path in sorted(annotations_dir.glob("invoice_*.json")):
        annotation = json.loads(annotation_path.read_text(encoding="utf-8"))
        words: list[str] = annotation["words"]
        bboxes: list[list[int]] = annotation["bboxes"]
        ner_tags: list[str] = annotation["ner_tags"]

        if not (len(words) == len(bboxes) == len(ner_tags)):
            raise ValueError(
                f"Mismatched annotation lengths in {annotation_path}: "
                f"{len(words)} words, {len(bboxes)} bboxes, {len(ner_tags)} labels"
            )

        image_path = data_dir / annotation["image_path"]
        if not image_path.exists():
            raise FileNotFoundError(
                f"Image referenced by {annotation_path} does not exist: {image_path}"
            )

        template = _load_template_name(metadata_dir / f"{annotation['id']}.json")
        examples.append(
            AnnotationExample(
                invoice_id=annotation["id"],
                image_path=image_path,
                words=words,
                bboxes=[_clip_bbox(bbox) for bbox in bboxes],
                ner_tags=ner_tags,
                template=template,
            )
        )

    if not examples:
        raise FileNotFoundError(
            f"No invoice annotation files found in {annotations_dir}. "
            "Generate data and annotations before training."
        )

    return examples


def has_explicit_splits(data_dir: Path) -> bool:
    """Return True when the dataset root already contains train/val/test folders."""
    return all((data_dir / split / "annotations").exists() for split in ("train", "val", "test"))


def load_examples_by_split(data_dir: Path) -> dict[str, list[AnnotationExample]]:
    """Load examples from an explicitly pre-split dataset root."""
    if not has_explicit_splits(data_dir):
        raise FileNotFoundError(
            f"Expected pre-split dataset folders under {data_dir}. "
            "Missing one of train/annotations, val/annotations, or test/annotations."
        )

    return {
        split: load_examples(data_dir / split)
        for split in ("train", "val", "test")
    }


def _validate_split_sizes(val_size: float, test_size: float) -> None:
    if not 0.0 <= val_size < 1.0:
        raise ValueError("val_size must be in [0, 1).")
    if not 0.0 <= test_size < 1.0:
        raise ValueError("test_size must be in [0, 1).")
    if val_size + test_size >= 1.0:
        raise ValueError("val_size + test_size must be < 1.0.")


def _split_random_ids(
    invoice_ids: list[str],
    val_size: float,
    test_size: float,
    seed: int,
) -> dict[str, list[str]]:
    rng = random.Random(seed)
    shuffled = list(invoice_ids)
    rng.shuffle(shuffled)

    total = len(shuffled)
    test_count = max(1, round(total * test_size)) if test_size > 0 else 0
    val_count = max(1, round(total * val_size)) if val_size > 0 else 0

    if test_count + val_count >= total:
        test_count = min(test_count, max(0, total - 2))
        val_count = min(val_count, max(0, total - test_count - 1))

    test_ids = shuffled[:test_count]
    val_ids = shuffled[test_count:test_count + val_count]
    train_ids = shuffled[test_count + val_count:]

    if not train_ids:
        raise ValueError("Split produced an empty training set. Adjust split sizes.")

    return {"train": train_ids, "val": val_ids, "test": test_ids}


def _split_template_holdout_ids(
    examples: list[AnnotationExample],
    val_size: float,
    test_size: float,
    seed: int,
) -> dict[str, list[str]]:
    template_to_ids: dict[str, list[str]] = {}
    for example in examples:
        if example.template is None:
            raise ValueError(
                "Template holdout splitting requires metadata with template names "
                "for every invoice."
            )
        template_to_ids.setdefault(example.template, []).append(example.invoice_id)

    templates = sorted(template_to_ids)
    if len(templates) < 3:
        raise ValueError(
            "Template holdout split needs at least 3 distinct templates "
            f"(found {len(templates)})."
        )

    rng = random.Random(seed)
    rng.shuffle(templates)

    total_examples = len(examples)
    target_test = total_examples * test_size
    target_val = total_examples * val_size

    split_ids = {"train": [], "val": [], "test": []}
    counts = {"val": 0, "test": 0}

    for template in templates:
        invoice_ids = template_to_ids[template]
        if counts["test"] < target_test:
            split_ids["test"].extend(invoice_ids)
            counts["test"] += len(invoice_ids)
        elif counts["val"] < target_val:
            split_ids["val"].extend(invoice_ids)
            counts["val"] += len(invoice_ids)
        else:
            split_ids["train"].extend(invoice_ids)

    if not split_ids["train"]:
        raise ValueError(
            "Template holdout split produced an empty training set. "
            "Lower val/test sizes or generate more templates."
        )

    return split_ids


def create_split_manifest(
    examples: list[AnnotationExample],
    strategy: str = "random",
    val_size: float = 0.1,
    test_size: float = 0.1,
    seed: int = 42,
) -> dict[str, Any]:
    """Create a reusable split manifest from loaded examples."""
    _validate_split_sizes(val_size, test_size)

    if strategy == "random":
        split_ids = _split_random_ids(
            invoice_ids=[example.invoice_id for example in examples],
            val_size=val_size,
            test_size=test_size,
            seed=seed,
        )
    elif strategy == "template_holdout":
        split_ids = _split_template_holdout_ids(
            examples=examples,
            val_size=val_size,
            test_size=test_size,
            seed=seed,
        )
    else:
        raise ValueError(
            f"Unknown split strategy '{strategy}'. "
            "Use 'random' or 'template_holdout'."
        )

    return {
        "strategy": strategy,
        "seed": seed,
        "val_size": val_size,
        "test_size": test_size,
        "train_ids": split_ids["train"],
        "val_ids": split_ids["val"],
        "test_ids": split_ids["test"],
    }


def save_split_manifest(manifest: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def load_split_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def examples_for_split(
    examples: list[AnnotationExample],
    manifest: dict[str, Any],
    split: str,
) -> list[AnnotationExample]:
    split_key = f"{split}_ids"
    if split_key not in manifest:
        raise KeyError(f"Split '{split}' not found in manifest.")

    id_set = set(manifest[split_key])
    return [example for example in examples if example.invoice_id in id_set]


class LayoutLMv3InvoiceDataset(Dataset):
    """Torch dataset that encodes invoice examples for LayoutLMv3."""

    def __init__(self, examples: list[AnnotationExample], processor: Any,
                 max_length: int = 512) -> None:
        self.examples = examples
        self.processor = processor
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        from PIL import Image

        example = self.examples[index]
        image = Image.open(example.image_path).convert("RGB")
        labels = [LABEL_TO_ID[tag] for tag in example.ner_tags]

        encoding = self.processor(
            images=image,
            text=example.words,
            boxes=example.bboxes,
            word_labels=labels,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        return {key: value.squeeze(0) for key, value in encoding.items()}
