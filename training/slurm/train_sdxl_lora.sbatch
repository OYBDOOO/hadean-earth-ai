#!/bin/bash
# Edit the SBATCH lines for your site before submitting.
# Submit with: sbatch training/slurm/train_sdxl_lora.sbatch

#SBATCH --job-name=hadean-sdxl-lora
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err
#SBATCH --partition=gpu
#SBATCH --account=your_account_here

set -euo pipefail

cd "${SLURM_SUBMIT_DIR}"
mkdir -p logs outputs

# Adjust these paths for your account and site policy.
export PROJECT_ROOT="${SLURM_SUBMIT_DIR}"
export WORKDIR="${PROJECT_ROOT}"
export HF_HOME="${PROJECT_ROOT}/.hf-cache"
export TRANSFORMERS_CACHE="${HF_HOME}/transformers"
export HUGGINGFACE_HUB_CACHE="${HF_HOME}/hub"
export MODEL_NAME="stabilityai/stable-diffusion-xl-base-1.0"
export TRAIN_DIR="${PROJECT_ROOT}/training/data/imagefolder"
export OUTPUT_DIR="${PROJECT_ROOT}/outputs/sdxl-hadean-lora-v1"
export VALID_PROMPT="Photorealistic Hadean Earth from orbit, dark steam ocean, volcanic haze, no modern continents"

# Site-specific environment init. Replace as needed.
module purge || true
module load cuda/12.1 || true
module load miniconda3 || true

if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
  conda activate hadean-lora
fi

python3 --version
nvidia-smi || true

# Build imagefolder dataset from the manifest if needed.
python3 training/scripts/build_imagefolder_dataset.py

# Clone diffusers once into the project if you don't already have it.
if [ ! -d "${PROJECT_ROOT}/vendor/diffusers" ]; then
  mkdir -p "${PROJECT_ROOT}/vendor"
  git clone https://github.com/huggingface/diffusers "${PROJECT_ROOT}/vendor/diffusers"
fi

cd "${PROJECT_ROOT}/vendor/diffusers"
pip install .
cd examples/text_to_image
pip install -r requirements.txt
pip install bitsandbytes peft transformers accelerate datasets sentencepiece

# Use bf16 on Ampere/Hopper if supported; change to fp16 if your GPU requires it.
accelerate launch \
  --mixed_precision="bf16" \
  train_text_to_image_lora_sdxl.py \
  --pretrained_model_name_or_path="${MODEL_NAME}" \
  --train_data_dir="${TRAIN_DIR}" \
  --image_column="image" \
  --caption_column="text" \
  --resolution=768 \
  --center_crop \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --max_train_steps=1500 \
  --checkpointing_steps=250 \
  --learning_rate=1e-4 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --rank=16 \
  --dataloader_num_workers=4 \
  --validation_prompt="${VALID_PROMPT}" \
  --num_validation_images=4 \
  --validation_epochs=1 \
  --seed=42 \
  --output_dir="${OUTPUT_DIR}"
