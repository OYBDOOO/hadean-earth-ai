# Hadean Image LoRA Training Pack

This folder is a minimal training scaffold for a `Hadean Earth` image LoRA.

## What I optimized for

- A project you can actually explain in class
- A training target that is realistic on student resources
- A workflow that is grounded in papers, not only aesthetic prompts

## Recommendation

Do **not** start with full-model training.
Do **not** start with FLUX local training on this machine.

This machine is:

- Apple M4
- 16 GB RAM

That is enough for data prep and light experimentation, but not a good target for serious FLUX LoRA training. The practical path is:

1. Build a paper-grounded dataset.
2. Train an `SDXL LoRA` first.
3. If needed later, move the same dataset to a stronger CUDA machine for FLUX LoRA.

## Project goal

Train a small LoRA that makes a base image model more consistent at drawing:

- basaltic black coastlines
- dark steam-covered oceans
- volcanic haze
- impact bombardment
- hydrothermal vent environments
- non-modern skies and landmasses

The LoRA is for **visual consistency**, not for claiming scientific truth.

## Folder layout

```text
training/
  README.md
  papers_and_sources.md
  data/
    raw/
    selected/
    captions/
  manifests/
    hadean_lora_manifest.csv
```

## Dataset target

Start with `60-120` selected images.

Split them roughly like this:

- `20-30` orbital / planetary views
- `15-25` volcanic coast / steam ocean scenes
- `10-20` impact scenes
- `10-20` hydrothermal vent / prebiotic environment scenes
- `10-15` geology texture references only

## Where images should come from

Use a mixture of:

- NASA or LPI early-Earth concept art
- open educational figures related to Hadean Earth
- geology reference photos: basalt, lava, ash cloud, black smoker vents
- a small number of your own generated images after manual screening

Avoid making the dataset mostly AI-generated images. That usually collapses diversity and makes the LoRA echo model mistakes.

## Labeling rule

Every selected image should get:

- one short caption
- one theme tag
- one confidence flag for scientific plausibility

Good caption style:

```text
hadean earth, orbital view, dark steam ocean, volcanic belts, impact haze, no modern continents
```

Bad caption style:

```text
beautiful cool earth fantasy wallpaper trending on artstation
```

## Model choice

Use this order:

1. `SDXL LoRA`
2. `FLUX LoRA` only if you later get CUDA cloud access

## Training suggestion

For the first run:

- image size: `768`
- rank: `16` or `32`
- epochs: `8-12`
- batch size: whatever fits
- caption dropout: low or none
- keep prompts factual and short

## Evaluation prompts

After training, compare base model vs LoRA with the same prompts:

1. `Photorealistic Hadean Earth from orbit, dark steam ocean, volcanic haze, no modern continents`
2. `Basaltic Hadean shoreline, hot steam ocean, ash-filled sky, lightning, no vegetation`
3. `Meteor striking the Hadean ocean, giant steam plume, molten ejecta, dark atmosphere`
4. `Hydrothermal vents on early Earth seafloor, black smokers, iron-sulfur minerals, prebiotic environment`

Check whether the LoRA improves:

- fewer modern-Earth errors
- darker and more plausible palette
- more consistent geology
- better scene identity across generations

## Immediate next step

1. Fill `manifests/hadean_lora_manifest.csv`.
2. Put chosen images in `data/selected/`.
3. Put matching caption files in `data/captions/`.
4. Train on a CUDA box if possible.

## Notes

- If you want a class-ready result fast, dataset quality matters more than exotic training tricks.
- A small, clean LoRA beats a messy large dataset.
