"""Fine-tune LayoutLMv3 on the synthetic invoice annotations."""

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
        create_split_manifest,
        examples_for_split,
        has_explicit_splits,
        load_examples,
        load_examples_by_split,
        load_split_manifest,
        save_split_manifest,
    )
    from .labels import ID_TO_LABEL, LABEL_TO_ID, LABELS
    from .metrics import build_compute_metrics
except ImportError:
    from data import (
        LayoutLMv3InvoiceDataset,
        create_split_manifest,
        examples_for_split,
        has_explicit_splits,
        load_examples,
        load_examples_by_split,
        load_split_manifest,
        save_split_manifest,
    )
    from labels import ID_TO_LABEL, LABEL_TO_ID, LABELS
    from metrics import build_compute_metrics


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "dataset"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "runs" / "layoutlmv3"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fine-tune LayoutLMv3 on the synthetic invoice dataset."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Generated dataset directory (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="microsoft/layoutlmv3-base",
        help="Pretrained LayoutLMv3 checkpoint to fine-tune.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Training output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--split-file",
        type=Path,
        default=None,
        help="Optional path to a saved split manifest JSON.",
    )
    parser.add_argument(
        "--split-strategy",
        type=str,
        default="random",
        choices=["random", "template_holdout"],
        help="How to divide invoices into train/val/test.",
    )
    parser.add_argument("--val-size", type=float, default=0.1)
    parser.add_argument("--test-size", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--num-train-epochs", type=float, default=8.0)
    parser.add_argument("--learning-rate", type=float, default=3e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.1)
    parser.add_argument("--per-device-train-batch-size", type=int, default=2)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--save-total-limit", type=int, default=2)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument(
        "--fp16",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable fp16 mixed precision when supported.",
    )
    parser.add_argument(
        "--bf16",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable bf16 mixed precision when supported.",
    )
    return parser.parse_args()


def _format_ratio_for_filename(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text.replace(".", "p")


def _default_split_file(
    data_dir: Path,
    strategy: str,
    seed: int,
    val_size: float,
    test_size: float,
) -> Path:
    val_tag = _format_ratio_for_filename(val_size)
    test_tag = _format_ratio_for_filename(test_size)
    return data_dir / "splits" / f"{strategy}_val{val_tag}_test{test_tag}_seed{seed}.json"


def _validate_existing_manifest(
    manifest: dict,
    strategy: str,
    seed: int,
    val_size: float,
    test_size: float,
) -> None:
    expected = {
        "strategy": strategy,
        "seed": seed,
        "val_size": val_size,
        "test_size": test_size,
    }
    for key, expected_value in expected.items():
        actual_value = manifest.get(key)
        if actual_value != expected_value:
            raise ValueError(
                f"Split manifest does not match requested {key}: "
                f"expected {expected_value}, found {actual_value}. "
                "Use a different --split-file or delete the stale manifest."
            )


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


def _make_training_arguments(
    args: argparse.Namespace,
    output_dir: Path,
    has_validation: bool,
    cuda_available: bool,
) -> TrainingArguments:
    params = inspect.signature(TrainingArguments.__init__).parameters
    kwargs: dict[str, object] = {
        "output_dir": str(output_dir),
        "overwrite_output_dir": True,
        "learning_rate": args.learning_rate,
        "num_train_epochs": args.num_train_epochs,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "per_device_eval_batch_size": args.per_device_eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "save_total_limit": args.save_total_limit,
        "logging_steps": args.logging_steps,
        "save_strategy": "epoch" if has_validation else "no",
        "load_best_model_at_end": has_validation,
        "metric_for_best_model": "eval_f1",
        "greater_is_better": True,
        "remove_unused_columns": False,
        "fp16": args.fp16,
        "report_to": "none",
        "seed": args.seed,
    }

    eval_strategy = "epoch" if has_validation else "no"
    if "evaluation_strategy" in params:
        kwargs["evaluation_strategy"] = eval_strategy
    elif "eval_strategy" in params:
        kwargs["eval_strategy"] = eval_strategy

    if "bf16" in params:
        kwargs["bf16"] = args.bf16

    if "use_cpu" in params:
        kwargs["use_cpu"] = not cuda_available
    elif "no_cuda" in params:
        kwargs["no_cuda"] = not cuda_available

    if "data_seed" in params:
        kwargs["data_seed"] = args.seed

    filtered_kwargs = {key: value for key, value in kwargs.items() if key in params}
    return TrainingArguments(**filtered_kwargs)


def main() -> None:
    args = parse_args()
    cuda_available = _configure_runtime(args.seed)
    if has_explicit_splits(args.data_dir):
        split_examples = load_examples_by_split(args.data_dir)
        train_examples = split_examples["train"]
        val_examples = split_examples["val"]
        test_examples = split_examples["test"]
        manifest = {
            "strategy": "pre_split",
            "seed": None,
            "val_size": None,
            "test_size": None,
            "train_ids": [example.invoice_id for example in train_examples],
            "val_ids": [example.invoice_id for example in val_examples],
            "test_ids": [example.invoice_id for example in test_examples],
        }
    else:
        examples = load_examples(args.data_dir)
        split_file = args.split_file or _default_split_file(
            data_dir=args.data_dir,
            strategy=args.split_strategy,
            seed=args.seed,
            val_size=args.val_size,
            test_size=args.test_size,
        )
        if split_file.exists():
            manifest = load_split_manifest(split_file)
            _validate_existing_manifest(
                manifest=manifest,
                strategy=args.split_strategy,
                seed=args.seed,
                val_size=args.val_size,
                test_size=args.test_size,
            )
        else:
            manifest = create_split_manifest(
                examples=examples,
                strategy=args.split_strategy,
                val_size=args.val_size,
                test_size=args.test_size,
                seed=args.seed,
            )
            save_split_manifest(manifest, split_file)

        train_examples = examples_for_split(examples, manifest, "train")
        val_examples = examples_for_split(examples, manifest, "val")
        test_examples = examples_for_split(examples, manifest, "test")

    print(
        "Loaded dataset splits:",
        f"train={len(train_examples)}",
        f"val={len(val_examples)}",
        f"test={len(test_examples)}",
    )
    print(f"Execution device: {'cuda' if cuda_available else 'cpu'}")
    print(f"Deterministic seed: {args.seed}")

    processor = AutoProcessor.from_pretrained(args.model_name, apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        args.model_name,
        num_labels=len(LABELS),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID,
    )

    train_dataset = LayoutLMv3InvoiceDataset(
        examples=train_examples,
        processor=processor,
        max_length=args.max_length,
    )
    val_dataset = (
        LayoutLMv3InvoiceDataset(
            examples=val_examples,
            processor=processor,
            max_length=args.max_length,
        )
        if val_examples
        else None
    )
    test_dataset = (
        LayoutLMv3InvoiceDataset(
            examples=test_examples,
            processor=processor,
            max_length=args.max_length,
        )
        if test_examples
        else None
    )

    training_args = _make_training_arguments(
        args=args,
        output_dir=args.output_dir,
        has_validation=val_dataset is not None,
        cuda_available=cuda_available,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=processor,
        data_collator=default_data_collator,
        compute_metrics=build_compute_metrics(ID_TO_LABEL),
    )

    train_result = trainer.train()
    trainer.save_model()
    processor.save_pretrained(args.output_dir)

    metrics: dict[str, float] = dict(train_result.metrics)
    metrics["train_examples"] = len(train_examples)
    metrics["val_examples"] = len(val_examples)
    metrics["test_examples"] = len(test_examples)

    if val_dataset is not None:
        metrics.update(trainer.evaluate(eval_dataset=val_dataset, metric_key_prefix="val"))
    if test_dataset is not None:
        metrics.update(trainer.evaluate(eval_dataset=test_dataset, metric_key_prefix="test"))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_split_manifest(manifest, args.output_dir / "split_manifest.json")
    (args.output_dir / "training_args.json").write_text(
        json.dumps(vars(args), indent=2, default=str),
        encoding="utf-8",
    )
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("\nTraining complete.")
    print(f"Model saved to: {args.output_dir}")
    print(f"Metrics saved to: {args.output_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
