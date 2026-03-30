#!/bin/bash

#SBATCH --job-name=train_layoutlmv3
#SBATCH --partition=gpu                # Use GPU partition
#SBATCH --nodes=1                      # Number of nodes
#SBATCH --ntasks=1                     # Number of tasks (processes)
#SBATCH --cpus-per-task=4              # CPU cores per task
#SBATCH --mem=16GB                     # Memory per node
#SBATCH --time=24:00:00                # Time limit (hh:mm:ss)
#SBATCH --gres=gpu:1                   # Request 1 GPU
#SBATCH --output=train_%j.out          # Standard output log
#SBATCH --error=train_%j.err           # Standard error log

# Load necessary modules (adjust based on cluster setup)
# module load python/3.10  # or whatever Python version is available
# module load cuda/11.8    # or appropriate CUDA version

# Activate your Python environment (if using conda/virtualenv)
# conda activate your_env_name
# or
# source /path/to/your/venv/bin/activate

# Install requirements if not already installed
# pip install -r requirements.txt

# Set environment variables for better performance
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Run the training script
# Replace /path/to/data with your actual data directory path
python train.py \
    --data-dir /path/to/your/data_directory \
    --output-dir runs/layoutlmv3 \
    --model-name microsoft/layoutlmv3-base \
    --epochs 10 \
    --batch-size 4 \
    --lr 1e-5 \
    --seed 42