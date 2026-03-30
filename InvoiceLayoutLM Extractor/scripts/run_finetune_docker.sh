#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATASET_DIR="${DATASET_DIR:-$ROOT_DIR/dataset}"
RUNS_DIR="${RUNS_DIR:-$ROOT_DIR/model_finetuning/runs}"
IMAGE_NAME="${IMAGE_NAME:-hcnlp-finetune}"

mkdir -p "$RUNS_DIR"

docker run --rm \
  -v "$DATASET_DIR:/app/dataset" \
  -v "$RUNS_DIR:/app/model_finetuning/runs" \
  "$IMAGE_NAME" \
  "$@"
