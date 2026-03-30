"""Metrics helpers for LayoutLMv3 token classification."""

from __future__ import annotations

from typing import Callable

import numpy as np
from seqeval.metrics import accuracy_score, f1_score, precision_score, recall_score


def build_compute_metrics(id_to_label: dict[int, str]) -> Callable:
    """Create a Trainer-compatible metric callback."""

    def compute_metrics(eval_pred: tuple[np.ndarray, np.ndarray]) -> dict[str, float]:
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=2)

        true_predictions: list[list[str]] = []
        true_labels: list[list[str]] = []

        for pred_row, label_row in zip(predictions, labels):
            pred_labels: list[str] = []
            gold_labels: list[str] = []
            for pred_id, label_id in zip(pred_row, label_row):
                if label_id == -100:
                    continue
                pred_labels.append(id_to_label[int(pred_id)])
                gold_labels.append(id_to_label[int(label_id)])
            true_predictions.append(pred_labels)
            true_labels.append(gold_labels)

        return {
            "precision": precision_score(true_labels, true_predictions),
            "recall": recall_score(true_labels, true_predictions),
            "f1": f1_score(true_labels, true_predictions),
            "accuracy": accuracy_score(true_labels, true_predictions),
        }

    return compute_metrics

