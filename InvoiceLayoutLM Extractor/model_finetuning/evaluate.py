"""Evaluate a fine-tuned LayoutLMv3 checkpoint on a chosen invoice split."""

from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path

import torch
from transformers import (
    AutoProcessor,
    LayoutLMv3ForTokenClassification,
    Trainer,
    TrainingArguments,
    default_data_collator,
    set_seed,
)

try:
    from .data import (
        LayoutLMv3InvoiceDataset,
        examples_for_split,
        has_explicit_splits,
        load_examples,
        load_examples_by_split,
        load_split_manifest,
    )
    from .labels import ID_TO_LABEL
    from .metrics import build_compute_metrics
except ImportError:
    from data import (
        LayoutLMv3InvoiceDataset,
        examples_for_split,
        has_explicit_splits,
        load_examples,
        load_examples_by_split,
        load_split_manifest,
    )
    from labels import ID_TO_LABEL
    from metrics import build_compute_metrics


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "dataset"
DEFAULT_MODEL_DIR = Path(__file__).resolve().parent / "runs" / "layoutlmv3"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a fine-tuned LayoutLMv3 checkpoint on invoice annotations."
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help=f"Directory containing a fine-tuned model (default: {DEFAULT_MODEL_DIR})",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Generated dataset directory (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--split-file",
        type=Path,
        default=None,
        help="Optional split manifest JSON. Defaults to model_dir/split_manifest.json.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        choices=["train", "val", "test"],
        help="Which split to evaluate.",
    )
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def _configure_runtime(seed: int) -> bool:
    """Set deterministic runtime behavior and report whether CUDA is available."""
    set_seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    torch.use_deterministic_algorithms(True, warn_only=True)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    return torch.cuda.is_available()


def _make_eval_training_arguments(
    model_dir: Path,
    batch_size: int,
    seed: int,
    cuda_available: bool,
) -> TrainingArguments:
    params = inspect.signature(TrainingArguments.__init__).parameters
    kwargs: dict[str, object] = {
        "output_dir": str(model_dir / "eval_tmp"),
        "report_to": "none",
        "per_device_eval_batch_size": batch_size,
        "remove_unused_columns": False,
        "seed": seed,
    }

    if "use_cpu" in params:
        kwargs["use_cpu"] = not cuda_available
    elif "no_cuda" in params:
        kwargs["no_cuda"] = not cuda_available

    if "data_seed" in params:
        kwargs["data_seed"] = seed

    filtered_kwargs = {key: value for key, value in kwargs.items() if key in params}
    return TrainingArguments(**filtered_kwargs)


def main() -> None:
    args = parse_args()
    cuda_available = _configure_runtime(args.seed)
    if has_explicit_splits(args.data_dir):
        split_examples = load_examples_by_split(args.data_dir)[args.split]
        if not split_examples:
            raise ValueError(f"Split '{args.split}' is empty under {args.data_dir}.")
    else:
        split_file = args.split_file or (args.model_dir / "split_manifest.json")
        if not split_file.exists():
            raise FileNotFoundError(
                f"Split manifest not found: {split_file}. "
                "Train the model first or pass --split-file explicitly."
            )

        examples = load_examples(args.data_dir)
        manifest = load_split_manifest(split_file)
        split_examples = examples_for_split(examples, manifest, args.split)
        if not split_examples:
            raise ValueError(f"Split '{args.split}' is empty in {split_file}.")

    processor = AutoProcessor.from_pretrained(args.model_dir, apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained(args.model_dir)
    dataset = LayoutLMv3InvoiceDataset(
        examples=split_examples,
        processor=processor,
        max_length=args.max_length,
    )
    print(f"Execution device: {'cuda' if cuda_available else 'cpu'}")
    print(f"Deterministic seed: {args.seed}")

    trainer = Trainer(
        model=model,
        args=_make_eval_training_arguments(
            model_dir=args.model_dir,
            batch_size=args.per_device_eval_batch_size,
            seed=args.seed,
            cuda_available=cuda_available,
        ),
        tokenizer=processor,
        data_collator=default_data_collator,
        compute_metrics=build_compute_metrics(model.config.id2label),
    )

    metrics = trainer.evaluate(eval_dataset=dataset, metric_key_prefix=args.split)
    out_path = args.model_dir / f"metrics_{args.split}.json"
    out_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Evaluated {len(split_examples)} examples from split '{args.split}'.")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"Saved metrics to: {out_path}")


if __name__ == "__main__":
    main()
