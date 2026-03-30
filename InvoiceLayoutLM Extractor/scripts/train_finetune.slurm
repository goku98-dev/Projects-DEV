#!/bin/bash
#SBATCH --job-name=hcnlp-train
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$PWD}"
VENV_PATH="${VENV_PATH:-$PROJECT_DIR/.venv}"
DATA_DIR="${DATA_DIR:-dataset}"
OUTPUT_DIR="${OUTPUT_DIR:-model_finetuning/runs/layoutlmv3}"
MODEL_NAME="${MODEL_NAME:-microsoft/layoutlmv3-base}"
SEED="${SEED:-42}"

if [ -n "${SLURM_CPUS_PER_TASK:-}" ]; then
  export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
fi

mkdir -p "$PROJECT_DIR/logs"
cd "$PROJECT_DIR"

if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r model_finetuning/requirements.txt

python -m model_finetuning.check_dataset --data-dir "$DATA_DIR"

python -m model_finetuning.train \
  --data-dir "$DATA_DIR" \
  --output-dir "$OUTPUT_DIR" \
  --model-name "$MODEL_NAME" \
  --seed "$SEED"
