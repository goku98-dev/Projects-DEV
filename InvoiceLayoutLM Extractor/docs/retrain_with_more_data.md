# Retraining With More Data On The Cluster

This guide is a repeatable runbook for the case where you add more invoice documents to the dataset and want to train and evaluate the model again on the Slurm cluster.

It assumes:

- the cluster copy of the project already exists under `~/HCNLP-Project`,
- the dataset is stored in the repository under `dataset/`,
- the dataset uses explicit `train`, `val`, and `test` splits,
- you submit jobs through `scripts/submit_finetune_slurm.sh`.

Important: do not use `model_finetuning/train.slurm` for this workflow. Use the helper script in `scripts/`.

## 1. Add the new dataset files locally

Put the new files into the correct split folders on your local machine:

```text
dataset/
  train/
    annotations/
    images/
    metadata/
    pdfs/
  val/
    annotations/
    images/
    metadata/
    pdfs/
  test/
    annotations/
    images/
    metadata/
    pdfs/
```

Each invoice must stay consistent across the folders:

- `annotations/invoice_xxxx.json`
- `images/invoice_xxxx.png`
- `metadata/invoice_xxxx.json`
- `pdfs/invoice_xxxx.pdf`

Why: the validator and training code expect every annotation to reference a matching image and metadata/PDF files.

## 2. Validate the updated dataset locally

Run this from the repository root on your local machine:

```bash
python -m model_finetuning.check_dataset --data-dir dataset
```

Why: this catches missing files, broken annotation keys, mismatched token/bbox/tag lengths, and unknown labels before you spend cluster time.

## 3. Decide whether to overwrite the old run

If you train again into the same output folder, the previous model and metrics will be overwritten.

Recommended: use a new output directory for every retraining run.

Example:

```text
model_finetuning/runs/layoutlmv3_moredata_2026-03-24
```

Why: this keeps every experiment separate and makes comparisons much easier.

## 4. Copy the updated project to the cluster

Run these commands from Windows PowerShell, not from the cluster shell:

```powershell
scp -r E:/HCNLP-Project/scripts jani55ne@ants.cs.ovgu.de:~/HCNLP-Project/
scp -r E:/HCNLP-Project/model_finetuning jani55ne@ants.cs.ovgu.de:~/HCNLP-Project/
scp -r E:/HCNLP-Project/dataset jani55ne@ants.cs.ovgu.de:~/HCNLP-Project/
scp E:/HCNLP-Project/.gitattributes jani55ne@ants.cs.ovgu.de:~/HCNLP-Project/
```

Why:

- `scripts/` updates the Slurm helper scripts,
- `model_finetuning/` updates the training/evaluation code,
- `dataset/` copies your new invoices to the cluster,
- `.gitattributes` preserves LF line endings for shell/Slurm files when using Git later.

If only the dataset changed and the code did not, you can copy just `dataset/`.

## 5. Prepare the cluster copy

SSH to the cluster and run:

```bash
cd ~/HCNLP-Project
sed -i 's/\r$//' scripts/*.sh scripts/*.slurm model_finetuning/*.py
chmod +x scripts/submit_finetune_slurm.sh
python -m model_finetuning.check_dataset --data-dir dataset
```

Why:

- `sed` removes Windows line endings if any were copied across,
- `chmod` makes the helper script executable,
- the validator confirms the copied dataset is still correct on the cluster.

## 6. Submit a new training job

Recommended command:

```bash
PARTITION=gpu-stud \
CPUS=8 \
MEM=32G \
TRAIN_TIME=08:00:00 \
OUTPUT_DIR=model_finetuning/runs/layoutlmv3_moredata_2026-03-24 \
bash scripts/submit_finetune_slurm.sh train
```

Why these variables matter:

- `PARTITION`: selects the GPU partition explicitly,
- `CPUS`: CPU cores for data loading and preprocessing,
- `MEM`: RAM for the job,
- `TRAIN_TIME`: wall-clock limit,
- `OUTPUT_DIR`: keeps this retraining run separate from older runs.

## 7. Monitor the training job

After submission, Slurm prints a job id. Use it in these commands:

```bash
squeue -u $USER
tail -f logs/hcnlp-train-<jobid>.out
```

Do not type angle brackets literally. Replace `<jobid>` with the real number.

Why:

- `squeue` shows whether the job is pending or running,
- `tail -f` lets you watch imports, validation, training progress, and final metrics.

## 8. Check the training outputs

When training finishes, inspect:

```bash
ls -la model_finetuning/runs/layoutlmv3_moredata_2026-03-24
cat model_finetuning/runs/layoutlmv3_moredata_2026-03-24/metrics.json
cat model_finetuning/runs/layoutlmv3_moredata_2026-03-24/training_args.json
```

Main files to look at:

- `metrics.json`: training, validation, and test metrics from the training run,
- `training_args.json`: confirms the hyperparameters,
- `split_manifest.json`: shows how the data was split if a manifest was used,
- `config.json` and `model.safetensors`: confirm the saved model exists.

## 9. Run a separate test-eval job

If you want a separate evaluation pass on the saved checkpoint, run:

```bash
PARTITION=gpu-stud \
CPUS=4 \
MEM=16G \
EVAL_TIME=02:00:00 \
MODEL_DIR=model_finetuning/runs/layoutlmv3_moredata_2026-03-24 \
bash scripts/submit_finetune_slurm.sh eval
```

Why `MODEL_DIR` matters: the eval helper defaults to `model_finetuning/runs/layoutlmv3`, so if you trained into a new output folder you must point eval at the same folder explicitly.

Monitor the eval job:

```bash
squeue -u $USER
tail -f logs/hcnlp-eval-<jobid>.out
```

Then inspect:

```bash
cat model_finetuning/runs/layoutlmv3_moredata_2026-03-24/metrics_test.json
```

This is the cleanest file to check when you want the held-out test metrics only.

## 10. Copy the outputs back to your local machine

Run these from Windows PowerShell:

```powershell
scp jani55ne@ants.cs.ovgu.de:~/HCNLP-Project/model_finetuning/runs/layoutlmv3_moredata_2026-03-24/metrics.json E:/HCNLP-Project/
scp jani55ne@ants.cs.ovgu.de:~/HCNLP-Project/model_finetuning/runs/layoutlmv3_moredata_2026-03-24/metrics_test.json E:/HCNLP-Project/
scp -r jani55ne@ants.cs.ovgu.de:~/HCNLP-Project/model_finetuning/runs/layoutlmv3_moredata_2026-03-24 E:/HCNLP-Project/model_finetuning/runs/
```

Why:

- copy only `metrics*.json` if you just want results,
- copy the whole run directory if you also want the saved checkpoint and config files.

## 11. Minimal repeat checklist

Use this when you repeat the process next time:

1. Add new invoices into `dataset/train`, `dataset/val`, and `dataset/test`.
2. Run `python -m model_finetuning.check_dataset --data-dir dataset` locally.
3. Pick a new `OUTPUT_DIR`.
4. Copy `scripts/`, `model_finetuning/`, and `dataset/` to the cluster.
5. Run the validator on the cluster.
6. Submit training.
7. Monitor the log.
8. Read `metrics.json`.
9. Submit eval with `MODEL_DIR=<same output dir>`.
10. Read `metrics_test.json`.
11. Copy outputs back to the local machine.

## 12. Common mistakes

- Running Windows commands like `scp E:/...` inside the cluster shell.
- Running cluster commands like `chmod`, `squeue`, or `sbatch` in Windows PowerShell.
- Typing `<jobid>` literally instead of the real numeric job id.
- Reusing the default `OUTPUT_DIR` and accidentally overwriting the previous model.
- Forgetting to set `MODEL_DIR` during eval when training used a custom output folder.
- Using `model_finetuning/train.slurm` instead of `scripts/submit_finetune_slurm.sh`.
