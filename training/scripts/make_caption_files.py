#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create caption sidecar .txt files from a LoRA manifest CSV."
    )
    parser.add_argument(
        "--manifest",
        default="training/manifests/hadean_lora_manifest.csv",
        help="Path to the manifest CSV.",
    )
    parser.add_argument(
        "--out-dir",
        default="training/data/captions",
        help="Directory for generated caption files.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_path = Path(row["image_path"])
            caption = row["caption"].strip()
            if not image_path.name:
                continue

            sidecar_name = image_path.with_suffix(".txt").name
            sidecar_path = out_dir / sidecar_name
            sidecar_path.write_text(caption + "\n", encoding="utf-8")

    print(f"Caption files written to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
