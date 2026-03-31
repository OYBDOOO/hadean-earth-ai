# SDXL LoRA on HPC

This guide assumes a Slurm-based GPU cluster such as a Sugon supercomputing environment.

It is built around the official Hugging Face Diffusers SDXL LoRA script:

- Diffusers LoRA training guide: <https://huggingface.co/docs/diffusers/training/lora>
- Official SDXL LoRA example script: <https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora_sdxl.py>
- Accelerate quicktour with explicit CLI config notes for Slurm: <https://huggingface.co/docs/accelerate/quicktour>

## Why this route

For your project, the cleanest training target is:

- base model: `stabilityai/stable-diffusion-xl-base-1.0`
- training type: `LoRA`
- data format: local `imagefolder` with `metadata.jsonl`
- launcher: `accelerate` under `Slurm`

This is much easier to defend and reproduce than ad hoc WebUI training.

## Expected cluster assumptions

You need:

- Linux login node
- Slurm scheduler
- at least 1 CUDA GPU node
- internet access to Hugging Face, or a mirrored model path

Recommended GPU tiers:

- minimum: `1 x 24GB` for a cautious run
- better: `1 x 40GB/48GB/80GB`
- ideal: `A100/H100` class if available

## Data format

The Diffusers SDXL LoRA example expects a local image folder that follows the Hugging Face `imagefolder` layout and includes `metadata.jsonl`.

Use this project structure:

```text
training/
  data/
    selected/
      orbit_001.jpg
      coast_001.jpg
    imagefolder/
      orbit_001.jpg
      coast_001.jpg
      metadata.jsonl
```

`metadata.jsonl` should look like:

```json
{"file_name":"orbit_001.jpg","text":"hadean earth, orbital view, dark steam ocean, volcanic belts, impact haze, no modern continents"}
{"file_name":"coast_001.jpg","text":"hadean earth shoreline, basaltic coast, hot primordial ocean, dense steam, volcanic haze, no vegetation"}
```

## Build the training dataset

After you fill the manifest and put images into `training/data/selected/`, run:

```bash
python3 training/scripts/build_imagefolder_dataset.py
```

That creates:

- `training/data/imagefolder/`
- copied image files
- `training/data/imagefolder/metadata.jsonl`

## Suggested first-run hyperparameters

These are tuned for a first stable run, not for squeezing the last bit of quality:

- resolution: `768`
- rank: `16`
- batch size per GPU: `1`
- gradient accumulation: `4`
- max steps: `1500`
- learning rate: `1e-4`
- mixed precision: `bf16` on newer GPUs, otherwise `fp16`
- no text encoder training on the first run

## Environment setup on cluster

Exact module names differ by site, but the pattern is usually:

```bash
module purge
module load cuda/12.1
module load gcc
module load miniconda3
conda create -n hadean-lora python=3.10 -y
conda activate hadean-lora
```

Then install:

```bash
git clone https://github.com/huggingface/diffusers
cd diffusers
pip install .
cd examples/text_to_image
pip install -r requirements.txt
pip install bitsandbytes peft transformers accelerate datasets sentencepiece
```

Important:

- The diffusers docs say to install from source before using the example scripts.
- On restrictive clusters, you may want a persistent wheel cache in your home directory.

## One-GPU first

Do not start with multi-node.

Your first successful run should be:

- 1 node
- 1 GPU
- local scratch
- short validation prompt

Only scale after that works.

## Slurm submission

Use the provided script:

- [training/slurm/train_sdxl_lora.sbatch](/Volumes/OYBDOOOG1T2/Runcode/archeangpt/training/slurm/train_sdxl_lora.sbatch)

You must edit:

- account / project code
- partition name
- GPU resource line
- conda activation path
- local scratch path if needed

Then submit:

```bash
sbatch training/slurm/train_sdxl_lora.sbatch
```

## Outputs

The run writes:

- LoRA checkpoints
- final `pytorch_lora_weights.safetensors`
- validation images

Suggested output folder name:

```text
outputs/sdxl-hadean-lora-v1
```

## Validation prompt

Use one fixed validation prompt so you can compare runs:

```text
Photorealistic Hadean Earth from orbit, dark steam ocean, volcanic haze, no modern continents
```

## Strong practical advice

- First run on `30-50` images, not 200.
- If the cluster has shared filesystem bottlenecks, copy data and model cache to node-local scratch.
- Save checkpoints every `250` or `500` steps.
- Do not train text encoders until the base LoRA route is proven.
- Keep captions short and factual.

## If the cluster is locked down

Common blockers:

- no outbound internet
- no `git clone`
- no `pip install` on compute nodes

Fallback:

1. build the environment on login node or in a container
2. pre-download model weights
3. set `HF_HOME` and `TRANSFORMERS_CACHE` to your storage path
4. point the script at local model files

## What I would run first

If I had your supercomputer account but no machine-specific docs yet, I would do this order:

1. verify `nvidia-smi`
2. create the imagefolder dataset
3. run a 200-step smoke test on 1 GPU
4. inspect validation images
5. rerun with `1500-2500` steps

That gives you a real result fast without wasting queue time.
