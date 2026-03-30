# InvoiceLayoutLM: Layout-Aware Invoice Extraction
![Diagram](https://raw.githubusercontent.com/goku98-dev/Projects-DEV/main/InvoiceLayoutLM%20Extractor/img/diagram.png)
This project builds a synthetic invoice pipeline and fine-tunes LayoutLMv3 to extract invoice table information from PDF invoices. The current workflow supports:

- synthetic invoice generation,
- automatic BIO token annotation,
- pre-split invoice datasets under `dataset/train`, `dataset/val`, and `dataset/test`,
- LayoutLMv3 fine-tuning,
- dataset validation before training,
- deterministic training and evaluation with a fixed seed,
- automatic CPU fallback when no GPU is available,
- separate Docker images for data generation and model fine-tuning.

## Project Structure

- [data_generation](./data_generation/README.md)
  Synthetic invoice generation, PDF rendering, and automatic annotation.
- [model_finetuning](./model_finetuning/README.md)
  LayoutLMv3 dataset loading, validation, training, and evaluation.

## Dataset Format

The fine-tuning pipeline expects a pre-split dataset in this structure:

```text
dataset/
  train/
    annotations/
    html/        # optional; useful for generation/debugging
    images/
    metadata/
    pdfs/
  val/
    annotations/
    html/        # optional; useful for generation/debugging
    images/
    metadata/
    pdfs/
  test/
    annotations/
    html/        # optional; useful for generation/debugging
    images/
    metadata/
    pdfs/
```

Each annotation file must contain:

- `id`
- `image_path`
- `words`
- `bboxes`
- `ner_tags`

The current dataset checked into this repository already follows that layout.

## Local Setup

Use Python 3.12+.

Install fine-tuning dependencies:

```bash
python -m pip install -r model_finetuning/requirements.txt
```

If you also want to generate new synthetic invoices locally:

```bash
python -m pip install -r data_generation/requirements.txt
python -m playwright install chromium
```

## How To Run

### 1. Validate the dataset

```bash
python -m model_finetuning.check_dataset --data-dir dataset
```

This checks split presence, annotation keys, token/box/tag alignment, label validity, and referenced images, metadata files, and PDFs.

### 2. Train LayoutLMv3

```bash
python -m model_finetuning.train \
  --data-dir dataset \
  --output-dir model_finetuning/runs/layoutlmv3 \
  --model-name microsoft/layoutlmv3-base \
  --seed 42
```

Behavior:

- uses `dataset/train`, `dataset/val`, and `dataset/test` directly when present,
- automatically runs on CPU if no GPU is available,
- uses deterministic seeding with `--seed 42` by default,
- saves the trained checkpoint, processor, metrics, and split manifest under `model_finetuning/runs/layoutlmv3`.

### 3. Evaluate a saved checkpoint

```bash
python -m model_finetuning.evaluate \
  --model-dir model_finetuning/runs/layoutlmv3 \
  --data-dir dataset \
  --split test \
  --seed 42
```

### 4. Generate new invoices and annotations

```bash
python data_generation/generate.py -n 500 --locale random
python data_generation/annotate.py
```

By default, generation output is written under `data_generation/output/`.

## Reproducibility

Training and evaluation are configured to be repeatable:

- default seed is `42`,
- `transformers.set_seed(...)` is applied,
- PyTorch manual seeds are applied,
- deterministic PyTorch algorithms are enabled when possible,
- `data_seed` is set in `TrainingArguments`.

This does not guarantee bit-for-bit identical results across every machine and every PyTorch backend, but it is set up for stable reruns with the same data and configuration.

## CPU And GPU Behavior

The fine-tuning scripts check `torch.cuda.is_available()` at runtime:

- if CUDA is available, training and evaluation use GPU,
- if CUDA is not available, they fall back to CPU automatically.

No extra flag is required to force that fallback in the common case.

## Docker

Use two separate images:

- `data_generation` image for invoice creation and annotation,
- `model_finetuning` image for dataset validation, training, and evaluation.

Helper scripts are available under `scripts/` and should be run from the repository root:

- `scripts/run_data_gen_docker.sh`
- `scripts/run_finetune_docker.sh`

### 1. Build the data generation image

```bash
docker build -t hcnlp-data-gen ./data_generation
```

### 2. Generate and annotate invoices

```bash
./scripts/run_data_gen_docker.sh python generate.py -n 500 -o /data
```

```bash
./scripts/run_data_gen_docker.sh python annotate.py -o /data
```

### 3. Build the model fine-tuning image

```bash
docker build -t hcnlp-finetune ./model_finetuning
```

### 4. Validate the dataset in Docker

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.check_dataset --data-dir dataset
```

### 5. Train in Docker

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.train \
    --data-dir dataset \
    --output-dir model_finetuning/runs/layoutlmv3 \
    --model-name microsoft/layoutlmv3-base \
    --seed 42
```

### 6. Evaluate in Docker

```bash
./scripts/run_finetune_docker.sh \
  python -m model_finetuning.evaluate \
    --model-dir model_finetuning/runs/layoutlmv3 \
    --data-dir dataset \
    --split test \
    --seed 42
```

Environment overrides:

- `IMAGE_NAME` can override the Docker image tag in either helper script,
- `OUTPUT_DIR` can override the mounted data-generation output path,
- `DATASET_DIR` can override the mounted dataset path,
- `RUNS_DIR` can override the mounted fine-tuning runs path.

## Current Status

Completed so far:

- dataset loader updated to support pre-split invoice datasets,
- training and evaluation scripts updated to use `dataset/` by default,
- dataset validation script added,
- deterministic seeding added,
- automatic CPU fallback added,
- separate Docker images for data generation and fine-tuning added,
- READMEs updated with local and Docker run instructions.

## Additional Documentation

- [data_generation/README.md](./data_generation/README.md)
- [model_finetuning/README.md](./model_finetuning/README.md)
- [docs/retrain_with_more_data.md](./docs/retrain_with_more_data.md)
