# Running HCNLP on a Slurm Cluster

This guide provides step-by-step instructions for running the HCNLP LayoutLMv3 fine-tuning pipeline on a Slurm cluster.

## Prerequisites

- SSH access to a Slurm login node
- The HCNLP-Pro repository cloned on the cluster
- Python 3.9+ available on the cluster (your cluster has Python 3.9.25 ✓)
- Git installed on the cluster
- No module system required (your cluster doesn't use `module load`)

## Quick Start

Your `gpu-stud` partition is ready. From the repository root:

```bash
bash scripts/submit_finetune_slurm.sh train
```

**Note:** The submission auto-detects your cluster's GPU partition (`gpu-stud`) and uses Python 3.9.25.

Check status:
```bash
squeue -u $USER
tail -f logs/hcnlp-train-<jobid>.out
```

---

## Before You Start: Cluster Configuration

**Your cluster setup (confirmed):**
- ✓ Python 3.9.25 available
- ✓ No module system (no `module load` needed)
- ✓ Scripts are in Unix format (LF line endings)

**If pushing from Windows:**
If you cloned this repo on Windows, ensure Unix line endings before pushing:
```bash
cd HCNLP-Pro
git add scripts/*.sh scripts/*.slurm
git commit -m "Unix line endings for cluster scripts"
git push
```

---

## Detailed Step-by-Step Guide

### Step 1: SSH into the Cluster

```bash
ssh username@cluster.domain.edu
```

### Step 2: Clone or Update the Repository

**If cloning for the first time:**
```bash
cd /path/to/your/workspace
git clone <repository-url> HCNLP-Pro
cd HCNLP-Pro
```

**If the repository already exists:**
```bash
cd /path/to/HCNLP-Pro
git pull
```

### Step 3: Verify Cluster Setup (Optional)

Check available partitions and GPUs:
```bash
sinfo -o "%P %t %N %G" | head -20
```

Example output:
```
PARTITION              STATE NODES GRES
gpu                      up     8 gpu:a100:4
cpu                      up    32 (null)
```

Check node details:
```bash
snode <node-name>
```

### Step 4: Submit Training Job

Navigate to the repository root:
```bash
cd /path/to/HCNLP-Pro
```

#### Option A: Auto-Detect (Recommended)

Let the submission script auto-detect your cluster's GPU partition:
```bash
bash scripts/submit_finetune_slurm.sh train
```

You should see output like:
```
Submitting train job
  partition: gpu
  gres: gpu:1
  cpus: <cluster default>
  mem: <cluster default>
```

#### Option B: Override Defaults

If your cluster requires specific resources, set them as environment variables:

```bash
PARTITION=gpu \
GPU_REQUEST=gpu:a100:1 \
CPUS=8 \
MEM=32G \
TRAIN_TIME=12:00:00 \
bash scripts/submit_finetune_slurm.sh train
```

Common scenarios:

**For A100 GPUs with high memory:**
```bash
PARTITION=gpu CPUS=16 MEM=64G TRAIN_TIME=24:00:00 bash scripts/submit_finetune_slurm.sh train
```

**For CPU-only (no GPU available):**
```bash
PARTITION=cpu GPU_REQUEST= CPUS=32 MEM=64G bash scripts/submit_finetune_slurm.sh train
```

**For a specific account/project:**
```bash
ACCOUNT=myproject bash scripts/submit_finetune_slurm.sh train
```

### Step 5: Monitor the Training Job

After submission, you'll see a job ID. Example: `Submitted batch job 12345`

List your running jobs:
```bash
squeue -u $USER
```

Example output:
```
JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
12345       gpu hcnlp-train myuser  R       1:23      1 gpu-node-03
```

View real-time job output:
```bash
tail -f logs/hcnlp-train-12345.out
```

Cancel a job if needed:
```bash
scancel 12345
```

### Step 6: Check Training Results

After the job completes, verify the model was saved:

```bash
ls -la model_finetuning/runs/layoutlmv3/
```

You should see:
- `config.json` — Model configuration
- `model.safetensors` — Trained weights
- `split_manifest.json` — Data split info
- `training_args.json` — Training hyperparameters
- `metrics.json` — Training metrics

### Step 7: Submit Evaluation Job

After training completes, evaluate the saved model on the test set:

```bash
bash scripts/submit_finetune_slurm.sh eval
```

Or with overrides:
```bash
PARTITION=gpu CPUS=4 MEM=16G EVAL_TIME=02:00:00 bash scripts/submit_finetune_slurm.sh eval
```

### Step 8: Monitor Evaluation

List your jobs:
```bash
squeue -u $USER
```

View evaluation output:
```bash
tail -f logs/hcnlp-eval-<jobid>.out
```

### Step 9: Retrieve Evaluation Results

After evaluation completes, check the metrics:

```bash
cat model_finetuning/runs/layoutlmv3/metrics_test.json
```

Example output:
```json
{
  "accuracy": 0.92,
  "precision": 0.89,
  "recall": 0.91,
  "f1": 0.90
}
```

---

## Environment Variables Reference

You can customize job submission by setting these environment variables:

| Variable | Default | Example | Description |
|----------|---------|---------|-------------|
| `PARTITION` | Auto-detected | `gpu` | Slurm partition name |
| `GPU_REQUEST` | `gpu:1` | `gpu:a100:1` | GPU resource format |
| `CPUS` | Cluster default | `8` | Cores per task |
| `MEM` | Cluster default | `32G` | Memory per task |
| `ACCOUNT` | (none) | `myproject` | Billing account |
| `TRAIN_TIME` | (none) | `08:00:00` | Training job walltime |
| `EVAL_TIME` | (none) | `02:00:00` | Evaluation job walltime |
| `PROJECT_DIR` | Auto | /path/to/repo | Repository root path |
| `DATA_DIR` | `dataset` | `/data/invoices` | Dataset location |
| `OUTPUT_DIR` | `model_finetuning/runs/layoutlmv3` | `/results/model` | Output directory |
| `VENV_PATH` | `.venv` | `/tmp/.venv` | Virtual environment path |

---

## Troubleshooting

### Job Submission Fails: "Batch script contains DOS line breaks"

**Issue:** 
```
sbatch: error: Batch script contains DOS line breaks (\r\n)
sbatch: error: instead of expected UNIX line breaks (\n).
```

**Cause:** The scripts were created on Windows with CRLF line endings instead of Unix LF.

**Solution:** Convert line endings on the cluster:
```bash
cd HCNLP-Pro/scripts
dos2unix submit_finetune_slurm.sh train_finetune.slurm evaluate_finetune.slurm
```

Or if `dos2unix` is not available, use `sed`:
```bash
cd HCNLP-Pro/scripts
sed -i 's/\r$//' submit_finetune_slurm.sh train_finetune.slurm evaluate_finetune.slurm
chmod +x submit_finetune_slurm.sh train_finetune.slurm evaluate_finetune.slurm
```

Then retry:
```bash
bash scripts/submit_finetune_slurm.sh train
```

### Job Submission Fails: "sbatch not found"

**Issue:** The submit script can't find sbatch.

**Solution:** Run from a Slurm login node (not a compute node):
```bash
ssh <login-node>
cd HCNLP-Pro
bash scripts/submit_finetune_slurm.sh train
```

### Job Fails: "No partition specified"

**Issue:** The auto-detection couldn't find a partition.

**Solution:** Explicitly set PARTITION:
```bash
PARTITION=gpu bash scripts/submit_finetune_slurm.sh train
```

### Job Fails: "Requested GPU unavailable"

**Issue:** The cluster doesn't have the requested GPU type.

**Solution:** Check available GPUs and adjust:
```bash
sinfo -o "%P %G" | grep gpu
GPU_REQUEST=gpu:1 bash scripts/submit_finetune_slurm.sh train
```

### Job Stuck in Queue (QOS limit exceeded)

**Issue:** Job stays in PENDING state due to queue policies.

**Solution:** Check account limits:
```bash
sacct -u $USER --format=Account,State
```

If needed, request a specific account or lower resource allocation:
```bash
ACCOUNT=higher_priority CPUS=4 MEM=16G bash scripts/submit_finetune_slurm.sh train
```

### Python Not Found or Version Mismatch

**Issue:** Python 3.9+ is not available or not in PATH.

**Solution:** Check Python availability:
```bash
python3 --version
```

If not found, contact your cluster administrator. If multiple versions exist, specify the full path in the Slurm script. Edit `scripts/train_finetune.slurm` and replace `python3` with the full path:
```bash
/usr/bin/python3.9 -m venv "$VENV_PATH"
```

### Out of Memory During Training

**Issue:** Job killed with OOM error.

**Solution:** Increase memory allocation:
```bash
MEM=64G bash scripts/submit_finetune_slurm.sh train
```

Or reduce batch size by editing the training script (advanced).

---

## Direct Slurm Submission (Without Helper Script)

If you prefer to use `sbatch` directly:

```bash
sbatch --partition=gpu --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=08:00:00 \
  --export=ALL,PROJECT_DIR=$(pwd) \
  scripts/train_finetune.slurm
```

For evaluation:
```bash
sbatch --partition=gpu --gres=gpu:1 --cpus-per-task=4 --mem=16G --time=02:00:00 \
  --export=ALL,PROJECT_DIR=$(pwd) \
  scripts/evaluate_finetune.slurm
```

---

## Tips for Success

1. **Test locally first:** Run the training locally with a small subset before submitting to the cluster to catch environment issues early.

2. **Use reasonable walltimes:** Training takes ~2-4 hours on a modern GPU. Start with 8 hours, then adjust based on actual run time.

3. **Monitor early:** Check job output in the first 30 seconds to catch import errors or module loading failures.

4. **Keep logs organized:** The scripts automatically create a `logs/` directory. Save important logs with a timestamp:
   ```bash
   cp logs/hcnlp-train-*.out logs/hcnlp-train-2026-03-23-batch1.out
   ```

5. **Use git for repeatability:** Commit all code changes before cluster submission so results are tied to a specific version.

6. **Check data format:** Before submitting, ensure dataset paths are correct:
   ```bash
   ls -la dataset/train/annotations/ | head -5
   ```

---

## Common Workflow

```bash
# SSH to cluster
ssh user@cluster.edu
cd HCNLP-Pro
git pull

# Submit training
bash scripts/submit_finetune_slurm.sh train

# Wait and monitor
watch -n 10 'squeue -u $USER'
tail -f logs/hcnlp-train-*.out

# After training completes, submit evaluation
bash scripts/submit_finetune_slurm.sh eval

# Check results
tail -f logs/hcnlp-eval-*.out
cat model_finetuning/runs/layoutlmv3/metrics_test.json
```

---

## For More Help

- Review the main [HOW_TO.md](HOW_TO.md) for local execution details
- Check [README.md](README.md) for project overview
- Review [model_finetuning/README.md](model_finetuning/README.md) for training details
- Run `bash scripts/submit_finetune_slurm.sh --help` (if implemented) or inspect the script for all options
