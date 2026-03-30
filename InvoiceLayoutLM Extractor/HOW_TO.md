# How To Run

This file is a step-by-step run guide for the repository.

All commands below were checked against the current source files, script arguments, Dockerfiles, and helper shell scripts in this repo.

## Before You Start

Run all commands from the repository root:

```bash
cd /workspaces/HCNLP-Project
```

The project has two main stages:

1. `data_generation/`
   Generate synthetic invoices and create BIO annotations.
2. `model_finetuning/`
   Validate the dataset, fine-tune LayoutLMv3, and evaluate a saved checkpoint.

You do not need to generate data if you want to train on the dataset already included in `dataset/`.

## Flow A: Train Using The Dataset Already In The Repo

This is the shortest path if you only want to run training and evaluation.

### Step 1: Create a Python environment

Use Python 3.12+ for the fine-tuning stage.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Step 2: Install fine-tuning dependencies

```bash
python -m pip install -r model_finetuning/requirements.txt
```

### Step 3: Validate the dataset

This checks that `train`, `val`, and `test` exist and that the annotation files point to valid images, metadata, and PDFs.

```bash
python -m model_finetuning.check_dataset --data-dir dataset
```

### Step 4: Train LayoutLMv3

```bash
python -m model_finetuning.train \
  --data-dir dataset \
  --output-dir model_finetuning/runs/layoutlmv3 \
  --model-name microsoft/layoutlmv3-base \
  --seed 42
```

What this does:

- uses `dataset/train`, `dataset/val`, and `dataset/test` directly,
- trains on GPU if CUDA is available,
- falls back to CPU automatically if CUDA is not available,
- saves the model, processor, split manifest, training args, and metrics under `model_finetuning/runs/layoutlmv3`.

### Step 5: Evaluate the saved checkpoint

```bash
python -m model_finetuning.evaluate \
  --model-dir model_finetuning/runs/layoutlmv3 \
  --data-dir dataset \
  --split test \
  --seed 42
```

This writes evaluation metrics to:

```text
model_finetuning/runs/layoutlmv3/metrics_test.json
```

## Flow B: Generate New Synthetic Data First, Then Train

Use this flow if you want to create a fresh dataset locally.

### Step 1: Create a Python environment

If you plan to both generate data and fine-tune in one environment, Python 3.12 is the safest choice in this repo.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Step 2: Install data-generation dependencies

```bash
python -m pip install -r data_generation/requirements.txt
python -m playwright install chromium
```

### Step 3: Generate invoices

This writes PDFs, HTML, and metadata under `data_generation/output/`.

```bash
python data_generation/generate.py -n 500 --locale random
```

Useful variations:

```bash
python data_generation/generate.py
python data_generation/generate.py -n 20 --locale en_US
python data_generation/generate.py -n 500 -o data_generation/output --seed 42
```

Generated files go to:

```text
data_generation/output/pdfs/
data_generation/output/html/
data_generation/output/metadata/
```

### Step 4: Create annotations

This renders invoice page images and writes BIO annotation JSON files.

```bash
python data_generation/annotate.py -o data_generation/output
```

Optional DPI override:

```bash
python data_generation/annotate.py -o data_generation/output --dpi 300
```

Annotated files go to:

```text
data_generation/output/images/
data_generation/output/annotations/
```

### Step 5: Optionally visualize annotations

This is a debugging step, not a training requirement.

```bash
python data_generation/visualize_annotations.py -o data_generation/output
```

To visualize only a few invoices:

```bash
python data_generation/visualize_annotations.py \
  -o data_generation/output \
  --ids invoice_0000 invoice_0001
```

Debug images are written to:

```text
data_generation/output/debug/
```

### Step 6: Install fine-tuning dependencies

If you are still in the same environment, install the training dependencies next:

```bash
python -m pip install -r model_finetuning/requirements.txt
```

### Step 7: Train on the generated dataset

If your generated output is a single folder like `data_generation/output/`, the training script can create split manifests automatically.

```bash
python -m model_finetuning.train \
  --data-dir data_generation/output \
  --split-strategy template_holdout \
  --output-dir model_finetuning/runs/layoutlmv3_generated \
  --model-name microsoft/layoutlmv3-base \
  --seed 42
```

Notes:

- for a single-folder dataset, the trainer creates or reuses a split manifest under `data_generation/output/splits/`,
- `template_holdout` is useful when you want evaluation on unseen layouts,
- you can also use `--split-strategy random`.

### Step 8: Evaluate the generated-data checkpoint

```bash
python -m model_finetuning.evaluate \
  --model-dir model_finetuning/runs/layoutlmv3_generated \
  --data-dir data_generation/output \
  --split test \
  --seed 42
```

## Flow C: Run With Docker

Use this if you want to avoid installing local Python dependencies.

## Data Generation In Docker

### Step 1: Build the data-generation image

Run from the repository root:

```bash
docker build -t hcnlp-data-gen ./data_generation
```

### Step 2: Generate invoices

The helper script mounts `data_generation/output` to `/data` inside the container.

```bash
./scripts/run_data_gen_docker.sh python generate.py -n 500 -o /data
```

### Step 3: Annotate the generated invoices

```bash
./scripts/run_data_gen_docker.sh python annotate.py -o /data
```

### Step 4: Optionally visualize annotations

```bash
./scripts/run_data_gen_docker.sh python visualize_annotations.py -o /data
```

## Fine-Tuning In Docker

### Step 1: Build the fine-tuning image

```bash
docker build -t hcnlp-finetune ./model_finetuning
```

### Step 2: Validate the checked-in dataset

The fine-tuning helper script mounts:

- `dataset/` to `/app/dataset`
- `model_finetuning/runs/` to `/app/model_finetuning/runs`

Run:

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.check_dataset --data-dir dataset
```

### Step 3: Train

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.train \
    --data-dir dataset \
    --output-dir model_finetuning/runs/layoutlmv3 \
    --model-name microsoft/layoutlmv3-base \
    --seed 42
```

### Step 4: Evaluate

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.evaluate \
    --model-dir model_finetuning/runs/layoutlmv3 \
    --data-dir dataset \
    --split test \
    --seed 42
```

## Output Locations

### Data generation outputs

```text
data_generation/output/pdfs/
data_generation/output/html/
data_generation/output/metadata/
data_generation/output/images/
data_generation/output/annotations/
data_generation/output/debug/
```

### Fine-tuning outputs

```text
model_finetuning/runs/layoutlmv3/
model_finetuning/runs/layoutlmv3_generated/
```

Typical saved files include:

```text
config.json
preprocessor_config.json
model.safetensors
split_manifest.json
training_args.json
metrics.json
metrics_test.json
```

## Command Check Notes

These command details were verified directly against the repository code:

- `data_generation/generate.py` accepts `-n/--count`, `-o/--output`, `--locale`, and `--seed`
- `data_generation/annotate.py` accepts `-o/--output` and `--dpi`
- `data_generation/visualize_annotations.py` accepts `-o/--output` and `--ids`
- `model_finetuning.check_dataset` accepts `--data-dir`
- `model_finetuning.train` accepts `--data-dir`, `--output-dir`, `--model-name`, `--seed`, and split-related arguments
- `model_finetuning.evaluate` accepts `--model-dir`, `--data-dir`, `--split`, and `--seed`
- `scripts/run_data_gen_docker.sh` and `scripts/run_finetune_docker.sh` are valid shell scripts and mount the expected directories

## Recommended First Run

If you just want the cleanest end-to-end path, use this order:

1. Create and activate a virtual environment.
2. Install `model_finetuning/requirements.txt`.
3. Run dataset validation on `dataset/`.
4. Train with `python -m model_finetuning.train ...`.
5. Evaluate with `python -m model_finetuning.evaluate ...`.

If you want fresh synthetic data first, use Flow B before training.

## Flow D: Run On A Slurm Cluster

Use this flow when you want to prepare everything locally first, then submit jobs on a cluster.

### Step 1: Local preparation

From your local machine, commit and push your latest changes so the cluster can pull the same version.

```bash
git add .
git commit -m "prepare cluster run"
git push
```

### Step 2: Clone or update on the cluster

```bash
git clone <your-repo-url> HCNLP-Pro
cd HCNLP-Pro
```

If the repo already exists on the cluster:

```bash
cd HCNLP-Pro
git pull
```

### Step 3: Submit training job

Use the submit helper. It auto-detects a GPU partition from `sinfo` when possible and applies GPU defaults.

```bash
bash scripts/submit_finetune_slurm.sh train
```

Optional overrides when needed:

```bash
PARTITION=gpu GPU_REQUEST=gpu:1 CPUS=8 MEM=32G TRAIN_TIME=08:00:00 \
bash scripts/submit_finetune_slurm.sh train
```

### Step 4: Monitor training

```bash
squeue -u $USER
tail -f logs/hcnlp-train-<jobid>.out
```

### Step 5: Submit evaluation job

Use the provided evaluation script:

```text
scripts/evaluate_finetune.slurm
```

Submit:

```bash
bash scripts/submit_finetune_slurm.sh eval
```

Optional overrides:

```bash
PARTITION=gpu GPU_REQUEST=gpu:1 CPUS=4 MEM=16G EVAL_TIME=02:00:00 \
bash scripts/submit_finetune_slurm.sh eval
```

### Step 6: Monitor evaluation

```bash
squeue -u $USER
tail -f logs/hcnlp-eval-<jobid>.out
```

### Notes

- `scripts/train_finetune.slurm` and `scripts/evaluate_finetune.slurm` are execution scripts.
- `scripts/submit_finetune_slurm.sh` is the preferred entry point for cluster submission.
- You can still call `sbatch` directly if your cluster policies require fixed flags.
