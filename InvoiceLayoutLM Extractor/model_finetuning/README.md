# Model Fine-Tuning

This folder contains the code for fine-tuning LayoutLMv3 on the invoice dataset. The model is set up as a token classification task with BIO tagging to extract table entities such as item descriptions, quantities, unit prices, line totals, tax values, positions, and article numbers.

The current pipeline supports:

- pre-split datasets under `dataset/train`, `dataset/val`, and `dataset/test`,
- dataset validation before training,
- deterministic runs with a fixed seed,
- automatic CPU fallback when no GPU is available,
- local execution, Docker execution, and Slurm submission.

## How to Run

### Slurm quick start

From the repository root:

```bash
bash scripts/submit_finetune_slurm.sh train
bash scripts/submit_finetune_slurm.sh eval
```

Useful overrides:

```bash
PARTITION=gpu-stud CPUS=8 MEM=32G TRAIN_TIME=08:00:00 bash scripts/submit_finetune_slurm.sh train
PARTITION=gpu-stud CPUS=4 MEM=16G EVAL_TIME=02:00:00 bash scripts/submit_finetune_slurm.sh eval
```

Training writes checkpoints and metrics under `model_finetuning/runs/layoutlmv3/`. Evaluation writes `metrics_<split>.json` into the same directory.

### 1. Prepare data

From the repository root:

```bash
dataset/
  train/
    annotations/
    images/
    metadata/
  val/
    annotations/
    images/
    metadata/
  test/
    annotations/
    images/
    metadata/
```

Each annotation JSON is expected to contain:

- `id`
- `image_path`
- `words`
- `bboxes`
- `ner_tags`

This repository already has that structure under `dataset/`, so no extra conversion step is needed before training.

### 2. Install fine-tuning dependencies

```bash
python -m pip install -r model_finetuning/requirements.txt
```

### 3. Validate the dataset

```bash
python -m model_finetuning.check_dataset --data-dir dataset
```

This checks that:

- all three splits exist,
- annotations contain `id`, `image_path`, `words`, `bboxes`, and `ner_tags`,
- token, box, and tag lengths match,
- labels are valid BIO labels for the current task,
- referenced image, metadata, and PDF files exist.

### 4. Train LayoutLMv3

Run from the repository root:

```bash
python -m model_finetuning.train \
  --data-dir dataset \
  --output-dir model_finetuning/runs/layoutlmv3 \
  --model-name microsoft/layoutlmv3-base \
  --seed 42
```

The training script:

- loads invoice images and annotation JSON files,
- converts BIO tags to integer labels,
- encodes text, bounding boxes, and page images with `AutoProcessor`,
- fine-tunes `LayoutLMv3ForTokenClassification`,
- uses the existing `train` / `val` / `test` folders when present,
- otherwise creates or reuses a saved split manifest for single-folder datasets,
- uses deterministic seeding,
- falls back to CPU automatically if CUDA is unavailable,
- evaluates on validation and test splits,
- saves the trained model, processor, split manifest, and metrics.

### 5. Evaluate a saved checkpoint

```bash
python -m model_finetuning.evaluate \
  --model-dir model_finetuning/runs/layoutlmv3 \
  --data-dir dataset \
  --split test \
  --seed 42
```

## Runtime Behavior

### Deterministic runs

The training and evaluation scripts default to `--seed 42` and apply deterministic settings through Transformers and PyTorch where supported.

### Device selection

The scripts check `torch.cuda.is_available()` automatically:

- if a GPU is available, the run uses CUDA,
- if a GPU is not available, the run uses CPU.

No extra device flag is required for the standard workflow.

## Docker

Use a dedicated fine-tuning image that is separate from the data-generation image.

Build from the repository root:

```bash
docker build -t hcnlp-finetune ./model_finetuning
```

Helper script:

```bash
./scripts/run_finetune_docker.sh python -m model_finetuning.check_dataset --data-dir dataset
```

Run dataset validation:

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.check_dataset --data-dir dataset
```

Run training:

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.train \
    --data-dir dataset \
    --output-dir model_finetuning/runs/layoutlmv3 \
    --model-name microsoft/layoutlmv3-base \
    --seed 42
```

Run evaluation:

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.evaluate \
    --model-dir model_finetuning/runs/layoutlmv3 \
    --data-dir dataset \
    --split test \
    --seed 42
```

## Files

- `labels.py`
  Shared BIO label list and id mappings.
- `data.py`
  Dataset loading, split creation, and `torch.utils.data.Dataset` wrapper.
- `check_dataset.py`
  Dataset sanity checks for the pre-split invoice corpus.
- `metrics.py`
  Seqeval-based precision/recall/F1 computation.
- `train.py`
  Main LayoutLMv3 fine-tuning entry point.
- `evaluate.py`
  Checkpoint evaluation for a saved split.

## Split Strategies

The training script supports two split strategies:

- `random`
  Random invoice-level split.
- `template_holdout`
  Keeps full templates out of training when metadata is available, which is better for testing layout generalization.

Example for a single unsplit dataset:

```bash
python -m model_finetuning.train \
  --data-dir data_generation/output \
  --split-strategy template_holdout
```

If `--data-dir` already contains `train`, `val`, and `test`, those folders are used directly and the split settings are ignored. For single-folder datasets, split manifests are cached under `<data-dir>/splits/`. Their filenames encode the split strategy, validation size, test size, and seed so different experiment settings do not silently reuse the wrong split. If you pass a custom `--split-file`, the trainer checks that its saved settings match the requested run.

## Notes

- The code fine-tunes a pretrained LayoutLMv3 checkpoint. It does not reimplement the architecture from scratch.
- The dataset must already be annotated with BIO `ner_tags`.
- The current metrics use seqeval on BIO tag sequences.
- If you build with Docker, the dataset and training outputs should be mounted into the container at runtime.
- The fine-tuning Docker image is intentionally separate from the `data_generation` Docker image so the two stages can be run independently.
- `scripts/run_finetune_docker.sh` mounts `dataset/` and `model_finetuning/runs/` automatically by default.

## Status

This folder currently contains only the LayoutLMv3 pipeline. A separate text-only baseline implementation is not included here yet.
