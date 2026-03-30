#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/data_generation/output}"
IMAGE_NAME="${IMAGE_NAME:-hcnlp-data-gen}"

mkdir -p "$OUTPUT_DIR"

docker run --rm \
  -v "$OUTPUT_DIR:/data" \
  "$IMAGE_NAME" \
  "$@"
