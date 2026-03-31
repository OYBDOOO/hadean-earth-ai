#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ThemePreset:
    name: str
    zh_name: str
    time_window: list[str]
    viewpoint: list[str]
    geology: list[str]
    atmosphere: list[str]
    events: list[str]
    constraints: list[str]


THEMES: dict[str, ThemePreset] = {
    "orbit": ThemePreset(
        name="orbit",
        zh_name="太空宏观视角",
        time_window=["4.4 billion years ago", "4.2 billion years ago", "4.0 billion years ago"],
        viewpoint=[
            "photorealistic orbital view of the Hadean Earth",
            "planetary-scale space view of early Earth",
            "cinematic reconstruction of the Hadean Earth seen from orbit",
        ],
        geology=[
            "dark rocky surface with limited proto-continents",
            "steam-covered oceans and discontinuous basaltic crust",
            "glowing volcanic belts and fractured primitive crust",
        ],
        atmosphere=[
            "thick hazy atmosphere rich in volcanic gases",
            "dusty steam-laden sky with impact haze",
            "murky reducing atmosphere with strong light scattering",
        ],
        events=[
            "heavy meteor bombardment in the distance",
            "subtle impact scars and glowing volcanic arcs",
            "cloud bands mixed with ash and steam plumes",
        ],
        constraints=[
            "no modern continents",
            "no plants or animals",
            "no modern blue sky",
        ],
    ),
    "coast": ThemePreset(
        name="coast",
        zh_name="火山海岸地表视角",
        time_window=["4.2 billion years ago", "4.1 billion years ago", "late Hadean Earth"],
        viewpoint=[
            "ground-level view on the Hadean Earth",
            "low-angle shoreline view on early Earth",
            "immersive geological reconstruction from the Hadean coast",
        ],
        geology=[
            "black basaltic coastline beside a hot primordial ocean",
            "wet igneous rocks and fresh lava channels",
            "dark volcanic islands rising from a mineral-rich sea",
        ],
        atmosphere=[
            "dense steam rising from the water",
            "ash-filled sky with volcanic haze",
            "sulfur-rich air and heavy cloud cover",
        ],
        events=[
            "active volcanoes on the horizon",
            "lightning flashing through the haze",
            "lava entering the ocean and creating violent steam bursts",
        ],
        constraints=[
            "no vegetation",
            "no humans",
            "scientifically plausible early Earth environment",
        ],
    ),
    "impact": ThemePreset(
        name="impact",
        zh_name="陨石撞击场景",
        time_window=["4.1 billion years ago", "late heavy bombardment era", "Hadean Earth during intense impacts"],
        viewpoint=[
            "catastrophic impact scene on the Hadean Earth",
            "cinematic view of a giant meteor striking early Earth",
            "planetary disaster reconstruction during the Hadean",
        ],
        geology=[
            "dark iron-rich ocean under a primitive crustal margin",
            "black volcanic shoreline and fractured basaltic surface",
            "steam ocean beneath a dim mineral-rich sky",
        ],
        atmosphere=[
            "sky filled with ash, dust, and vaporized rock",
            "impact-generated steam and reducing haze",
            "glowing debris moving through a thick turbulent atmosphere",
        ],
        events=[
            "enormous steam explosion and molten ejecta",
            "shockwave spreading across the ocean surface",
            "fire-lit clouds and incandescent impact plume",
        ],
        constraints=[
            "no modern cities or structures",
            "no life visible",
            "scientifically plausible impact reconstruction",
        ],
    ),
    "vent": ThemePreset(
        name="vent",
        zh_name="热液喷口与生命起源",
        time_window=["late Hadean Earth", "4.0 billion years ago", "Hadean seafloor environment"],
        viewpoint=[
            "deep ocean hydrothermal vent scene on the Hadean Earth",
            "underwater reconstruction of a Hadean hydrothermal field",
            "submarine prebiotic chemistry environment on early Earth",
        ],
        geology=[
            "black smoker chimneys on a dark basaltic seafloor",
            "iron-sulfur mineral deposits and fractured crust",
            "steep vent structures surrounded by particulate-rich water",
        ],
        atmosphere=[
            "dim underwater light and suspended minerals",
            "turbulent mixing of hot vent fluids and cold ocean water",
            "murky water with strong thermal gradients",
        ],
        events=[
            "dense black plumes rising from active vents",
            "mineral precipitation around hydrothermal chimneys",
            "dramatic flow patterns around vent clusters",
        ],
        constraints=[
            "no fish or modern marine life",
            "prebiotic chemistry environment",
            "scientifically grounded origin-of-life setting",
        ],
    ),
    "cool_late_hadean": ThemePreset(
        name="cool_late_hadean",
        zh_name="较冷的晚期冥古宙",
        time_window=["cooler late Hadean Earth", "4.1 billion years ago", "post-magma-ocean Hadean Earth"],
        viewpoint=[
            "scientific reconstruction of a cooler late Hadean Earth",
            "temperate but harsh late Hadean planetary scene",
            "late Hadean Earth with stabilized surface water",
        ],
        geology=[
            "shallow dark oceans and scattered volcanic islands",
            "proto-crust with broken coastlines and basaltic highlands",
            "ancient mineral-rich shoreline under primitive tectonic activity",
        ],
        atmosphere=[
            "thick hazy sky without oxygen-rich blue tones",
            "heavy clouds mixed with steam and volcanic gases",
            "subdued sunlight filtered through a dense primitive atmosphere",
        ],
        events=[
            "ongoing geothermal activity and distant eruptions",
            "low-lying steam banks over the sea",
            "intermittent lightning under a cloud-heavy sky",
        ],
        constraints=[
            "no visible life",
            "no modern continents",
            "not a fully molten lava planet",
        ],
    ),
}


MODEL_HINTS = {
    "openai": {
        "style": [
            "scientifically grounded paleo-planetary reconstruction",
            "high compliance to geological details",
            "realistic planetary science visualization",
        ],
        "extras": ["ultra-detailed", "photorealistic", "natural lighting"],
    },
    "flux": {
        "style": [
            "cinematic realism with dramatic atmosphere",
            "strong material textures and volumetric lighting",
            "epic geological scale with realistic surface detail",
        ],
        "extras": ["ultra-detailed", "moody lighting", "high texture fidelity"],
    },
    "midjourney": {
        "style": [
            "striking concept-art composition with grounded geology",
            "cinematic wide shot with strong visual hierarchy",
            "high-end paleo-science illustration mood",
        ],
        "extras": ["dramatic composition", "rich atmosphere", "sharp focal structure"],
    },
    "ideogram": {
        "style": [
            "clean science-poster composition",
            "highly readable visual arrangement",
            "presentation-friendly planetary illustration",
        ],
        "extras": ["clear subject separation", "balanced composition", "poster-ready detail"],
    },
}


TONES = {
    "photorealistic": ["photorealistic", "realistic geology", "naturalistic rendering"],
    "cinematic": ["cinematic", "dramatic lighting", "epic scale"],
    "scientific": ["scientifically plausible", "research-informed", "reconstruction style"],
    "poster": ["presentation-ready", "clean composition", "high contrast readability"],
}


NEGATIVE_TERMS = [
    "no forests",
    "no grass",
    "no trees",
    "no dinosaurs",
    "no mammals",
    "no birds",
    "no human structures",
    "no spacecraft",
    "no text",
    "no watermark",
]


def pick(rng: random.Random, values: list[str]) -> str:
    return rng.choice(values)


def build_prompt(theme: ThemePreset, model: str, tone: str, rng: random.Random) -> dict[str, str]:
    hint = MODEL_HINTS[model]
    pieces = [
        pick(rng, theme.time_window),
        pick(rng, theme.viewpoint),
        pick(rng, theme.geology),
        pick(rng, theme.atmosphere),
        pick(rng, theme.events),
        ", ".join(theme.constraints),
        pick(rng, hint["style"]),
        ", ".join(TONES[tone]),
        ", ".join(hint["extras"]),
    ]
    prompt = ", ".join(pieces)
    negative = ", ".join(NEGATIVE_TERMS)
    note = (
        f"主题: {theme.zh_name} | 模型: {model} | 风格: {tone} | "
        "视觉约束来自冥古宙海洋、火山、撞击与热液环境这几类文献线索。"
    )
    return {"prompt": prompt, "negative_prompt": negative, "note": note}


def format_text(records: list[dict[str, str]]) -> str:
    blocks: list[str] = []
    for idx, record in enumerate(records, start=1):
        blocks.append(
            "\n".join(
                [
                    f"Prompt {idx}",
                    record["note"],
                    "",
                    "Prompt:",
                    record["prompt"],
                    "",
                    "Negative Prompt:",
                    record["negative_prompt"],
                ]
            )
        )
    return "\n\n" + ("\n\n" + ("-" * 72) + "\n\n").join(blocks) + "\n"


def format_markdown(records: list[dict[str, str]]) -> str:
    parts = ["# Hadean Prompt Set", ""]
    for idx, record in enumerate(records, start=1):
        parts.extend(
            [
                f"## Prompt {idx}",
                record["note"],
                "",
                "```text",
                record["prompt"],
                "```",
                "",
                "Negative prompt:",
                "",
                "```text",
                record["negative_prompt"],
                "```",
                "",
            ]
        )
    return "\n".join(parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate literature-informed prompts for Hadean Earth image generation."
    )
    parser.add_argument(
        "--theme",
        default="orbit",
        choices=sorted(THEMES.keys()),
        help="Scene theme to generate.",
    )
    parser.add_argument(
        "--model",
        default="openai",
        choices=sorted(MODEL_HINTS.keys()),
        help="Target image model family.",
    )
    parser.add_argument(
        "--tone",
        default="scientific",
        choices=sorted(TONES.keys()),
        help="Stylistic tone preset.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=4,
        help="Number of prompt variants to produce.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible prompt variants.",
    )
    parser.add_argument(
        "--format",
        default="text",
        choices=["text", "json", "markdown"],
        help="Output format.",
    )
    parser.add_argument(
        "--save",
        help="Optional output file path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)
    theme = THEMES[args.theme]
    records = [build_prompt(theme, args.model, args.tone, rng) for _ in range(args.count)]

    if args.format == "json":
        output = json.dumps(records, ensure_ascii=False, indent=2)
    elif args.format == "markdown":
        output = format_markdown(records)
    else:
        output = format_text(records)

    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
