#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-train}"

if [[ "$MODE" == "-h" || "$MODE" == "--help" ]]; then
  echo "Usage: scripts/submit_finetune_slurm.sh [train|eval]"
  exit 0
fi

if [[ "$MODE" != "train" && "$MODE" != "eval" ]]; then
  echo "Usage: scripts/submit_finetune_slurm.sh [train|eval]"
  exit 1
fi

if ! command -v sbatch >/dev/null 2>&1; then
  echo "sbatch not found. Run this script on a Slurm login node."
  exit 1
fi

detect_partition() {
  if ! command -v sinfo >/dev/null 2>&1; then
    return 0
  fi

  local p
  p="$(sinfo -h -o '%P %G' | awk '$2 ~ /gpu/ {gsub(/\*/, "", $1); print $1; exit}')"
  if [[ -n "$p" ]]; then
    echo "$p"
    return 0
  fi

  p="$(sinfo -h -o '%P' | awk 'NR==1 {gsub(/\*/, "", $1); print $1}')"
  echo "$p"
}

PARTITION="${PARTITION:-$(detect_partition)}"
GPU_REQUEST="${GPU_REQUEST:-gpu:1}"
TRAIN_TIME="${TRAIN_TIME:-}"
EVAL_TIME="${EVAL_TIME:-}"
CPUS="${CPUS:-}"
MEM="${MEM:-}"
ACCOUNT="${ACCOUNT:-}"

SBATCH_ARGS=()

if [[ -n "$PARTITION" ]]; then
  SBATCH_ARGS+=("--partition=$PARTITION")
fi

if [[ -n "$GPU_REQUEST" ]]; then
  SBATCH_ARGS+=("--gres=$GPU_REQUEST")
fi

if [[ -n "$CPUS" ]]; then
  SBATCH_ARGS+=("--cpus-per-task=$CPUS")
fi

if [[ -n "$MEM" ]]; then
  SBATCH_ARGS+=("--mem=$MEM")
fi

if [[ -n "$ACCOUNT" ]]; then
  SBATCH_ARGS+=("--account=$ACCOUNT")
fi

if [[ "$MODE" == "train" && -n "$TRAIN_TIME" ]]; then
  SBATCH_ARGS+=("--time=$TRAIN_TIME")
fi

if [[ "$MODE" == "eval" && -n "$EVAL_TIME" ]]; then
  SBATCH_ARGS+=("--time=$EVAL_TIME")
fi

if [[ "$MODE" == "train" ]]; then
  TARGET_SCRIPT="$ROOT_DIR/scripts/train_finetune.slurm"
else
  TARGET_SCRIPT="$ROOT_DIR/scripts/evaluate_finetune.slurm"
fi

if [[ ! -f "$TARGET_SCRIPT" ]]; then
  echo "Missing Slurm script: $TARGET_SCRIPT"
  exit 1
fi

mkdir -p "$ROOT_DIR/logs"

echo "Submitting $MODE job"
echo "  partition: ${PARTITION:-<cluster default>}"
echo "  gres: ${GPU_REQUEST:-<none>}"
echo "  cpus: ${CPUS:-<cluster default>}"
echo "  mem: ${MEM:-<cluster default>}"

sbatch "${SBATCH_ARGS[@]}" \
  --export=ALL,PROJECT_DIR="$ROOT_DIR" \
  "$TARGET_SCRIPT"
