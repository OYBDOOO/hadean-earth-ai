# Scripts

## `generate_hadean_prompts.py`

Generates literature-informed prompt variants for Hadean Earth image generation.

Example:

```bash
python3 scripts/generate_hadean_prompts.py \
  --theme orbit \
  --model flux \
  --tone cinematic \
  --count 6 \
  --format markdown \
  --save outputs/prompts/orbit_flux.md
```

Useful presets:

- `--theme orbit`
- `--theme coast`
- `--theme impact`
- `--theme vent`
- `--theme cool_late_hadean`

Supported target models:

- `openai`
- `flux`
- `midjourney`
- `ideogram`
