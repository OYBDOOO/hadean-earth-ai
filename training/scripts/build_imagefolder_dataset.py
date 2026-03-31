#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "training" / "manifests" / "hadean_lora_manifest.csv"
DEFAULT_OUT_DIR = ROOT / "training" / "data" / "imagefolder"


def main() -> int:
    manifest_path = DEFAULT_MANIFEST
    out_dir = DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = out_dir / "metadata.jsonl"
    rows_written = 0

    with manifest_path.open("r", encoding="utf-8", newline="") as f, metadata_path.open(
        "w", encoding="utf-8"
    ) as out:
        reader = csv.DictReader(f)
        for row in reader:
            image_rel = row["image_path"].strip()
            caption = row["caption"].strip()
            if not image_rel or not caption:
                continue

            src = ROOT / image_rel
            if not src.exists():
                print(f"skip missing image: {src}")
                continue

            dst = out_dir / src.name
            if src.resolve() != dst.resolve():
                shutil.copy2(src, dst)

            out.write(json.dumps({"file_name": src.name, "text": caption}, ensure_ascii=False) + "\n")
            rows_written += 1

    print(f"Wrote {rows_written} samples to {metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
