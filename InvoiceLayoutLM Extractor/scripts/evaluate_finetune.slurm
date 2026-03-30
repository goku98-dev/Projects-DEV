#!/bin/bash
#SBATCH --job-name=hcnlp-eval
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$PWD}"
VENV_PATH="${VENV_PATH:-$PROJECT_DIR/.venv}"
DATA_DIR="${DATA_DIR:-dataset}"
MODEL_DIR="${MODEL_DIR:-model_finetuning/runs/layoutlmv3}"
SPLIT="${SPLIT:-test}"
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

python -m model_finetuning.evaluate \
  --model-dir "$MODEL_DIR" \
  --data-dir "$DATA_DIR" \
  --split "$SPLIT" \
  --seed "$SEED"
