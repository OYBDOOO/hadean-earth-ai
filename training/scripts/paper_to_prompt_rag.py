#!/usr/bin/env python3
"""
paper_to_prompt_rag.py — 论文驱动的冥古宙图像 Prompt 生成器

这个脚本实现了一个轻量级 RAG 流水线:
1. 从 hadean_paper_database.json 加载论文知识库
2. 根据用户选择的视觉主题，检索最相关的论文和视觉约束
3. 自动将论文证据拼装成结构化的图像生成 prompt
4. 可选：调用 Gemini API 让 LLM 润色 prompt

用法:
    # 列出所有可用主题
    python paper_to_prompt_rag.py --list-themes

    # 为某个主题生成 prompt（纯本地，不调 API）
    python paper_to_prompt_rag.py --theme orbit

    # 为某个主题生成 prompt，并用 LLM 润色
    python paper_to_prompt_rag.py --theme impact --refine

    # 按时间线生成一组 prompt
    python paper_to_prompt_rag.py --timeline

    # 为所有主题批量生成
    python paper_to_prompt_rag.py --all

    # 导出为 JSON 文件（供 batch_generate_images.py 使用）
    python paper_to_prompt_rag.py --all --output prompts.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "training" / "data" / "hadean_paper_database.json"

# ---------------------------------------------------------------------------
# 加载知识库
# ---------------------------------------------------------------------------

def load_database(path: Path = DB_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 检索：根据主题找到相关论文和视觉约束
# ---------------------------------------------------------------------------

def retrieve_by_theme(db: dict, theme: str) -> dict[str, Any]:
    """返回一个主题的所有视觉约束和相关论文信息。"""
    theme_info = db["visual_themes"].get(theme)
    if not theme_info:
        available = ", ".join(db["visual_themes"].keys())
        raise ValueError(f"Unknown theme '{theme}'. Available: {available}")

    paper_lookup = {p["id"]: p for p in db["papers"]}
    relevant_papers = []
    all_keywords: list[str] = []
    all_constraints: dict[str, str] = {}

    for pid in theme_info["relevant_paper_ids"]:
        paper = paper_lookup.get(pid)
        if not paper:
            continue
        relevant_papers.append(paper)
        all_keywords.extend(paper.get("prompt_keywords", []))
        for k, v in paper.get("visual_constraints", {}).items():
            all_constraints[f"{pid}.{k}"] = v

    return {
        "theme": theme,
        "theme_description": theme_info["description"],
        "composite_constraints": theme_info["composite_constraints"],
        "papers": relevant_papers,
        "merged_keywords": list(dict.fromkeys(all_keywords)),  # deduplicated, order-preserving
        "all_visual_constraints": all_constraints,
    }


def retrieve_by_time(db: dict, target_ga: float, window: float = 0.3) -> list[dict]:
    """返回与某个时间点相关的论文。"""
    results = []
    for paper in db["papers"]:
        tr = paper.get("time_range_ga", [])
        if len(tr) == 2:
            if tr[0] + window >= target_ga >= tr[1] - window:
                results.append(paper)
    return results


# ---------------------------------------------------------------------------
# Prompt 组装
# ---------------------------------------------------------------------------

STYLE_SUFFIX = (
    "scientifically grounded paleo-planetary reconstruction, "
    "photorealistic, cinematic lighting, ultra-detailed, "
    "no text, no watermark, no modern life, no spacecraft"
)

NEGATIVE_CONSTRAINTS = (
    "no forests, no grass, no trees, no dinosaurs, no mammals, no birds, "
    "no modern continents, no cities, no human structures, no modern blue sky"
)


def build_prompt(retrieval: dict[str, Any], style: str = "photorealistic") -> dict[str, str]:
    """从检索结果组装结构化 prompt。"""
    theme = retrieval["theme"]
    composite = retrieval["composite_constraints"]
    keywords = retrieval["merged_keywords"]

    # 收集论文引用信息
    citations = []
    for p in retrieval["papers"]:
        citations.append(f"{p['authors']} ({p['year']}): {p['key_finding']}")

    # 构建正向 prompt
    keyword_str = ", ".join(keywords[:15])  # 限制长度
    positive = f"{composite}, {keyword_str}, {STYLE_SUFFIX}"

    # 选择时间标注
    time_ranges = []
    for p in retrieval["papers"]:
        tr = p.get("time_range_ga", [])
        if tr:
            time_ranges.extend(tr)
    if time_ranges:
        avg_time = sum(time_ranges) / len(time_ranges)
        time_label = f"{avg_time:.1f} billion years ago"
        positive = f"Hadean Earth, {time_label}, " + positive

    return {
        "theme": theme,
        "positive_prompt": positive,
        "negative_prompt": NEGATIVE_CONSTRAINTS,
        "style": style,
        "paper_count": len(retrieval["papers"]),
        "citations": citations,
        "keywords_used": keywords[:15],
    }


def build_timeline_prompts(db: dict) -> list[dict[str, Any]]:
    """为时间线上的每个关键事件生成 prompt。"""
    results = []
    paper_lookup = {p["id"]: p for p in db["papers"]}

    for event in db["timeline"]:
        time_ga = event["time_ga"]
        event_desc = event["event"]
        papers = [paper_lookup[pid] for pid in event["paper_ids"] if pid in paper_lookup]

        if not papers:
            continue

        all_keywords = []
        for p in papers:
            all_keywords.extend(p.get("prompt_keywords", []))
        all_keywords = list(dict.fromkeys(all_keywords))[:12]

        keyword_str = ", ".join(all_keywords)
        positive = (
            f"Hadean Earth, {time_ga} billion years ago, {event_desc}, "
            f"{keyword_str}, {STYLE_SUFFIX}"
        )

        citations = [f"{p['authors']} ({p['year']}): {p['key_finding']}" for p in papers]

        results.append({
            "theme": f"timeline_{time_ga}Ga",
            "event": event_desc,
            "time_ga": time_ga,
            "positive_prompt": positive,
            "negative_prompt": NEGATIVE_CONSTRAINTS,
            "paper_count": len(papers),
            "citations": citations,
            "keywords_used": all_keywords,
        })

    return results


# ---------------------------------------------------------------------------
# 可选：用 LLM 润色 prompt
# ---------------------------------------------------------------------------

def refine_with_llm(prompt_data: dict[str, Any]) -> str:
    """调用 Gemini API 将原始 prompt 润色为更适合图像生成的版本。"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[WARN] GEMINI_API_KEY not set. Skipping LLM refinement.", file=sys.stderr)
        return prompt_data["positive_prompt"]

    import json as _json
    from urllib.request import Request, urlopen

    system_msg = (
        "You are an expert at writing image-generation prompts for scientific visualizations. "
        "You receive a raw prompt about the Hadean Earth (冥古宙) and scientific paper citations. "
        "Your job is to rewrite the prompt to be vivid, visually specific, and scientifically accurate. "
        "Output ONLY the refined English prompt, nothing else. Keep it under 200 words. "
        "Maintain all scientific constraints from the papers."
    )

    user_msg = (
        f"Theme: {prompt_data['theme']}\n\n"
        f"Raw prompt:\n{prompt_data['positive_prompt']}\n\n"
        f"Paper evidence:\n" + "\n".join(f"- {c}" for c in prompt_data['citations']) + "\n\n"
        f"Rewrite this into one cohesive, vivid image prompt."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    data = {
        "system_instruction": {"parts": [{"text": system_msg}]},
        "contents": [{"parts": [{"text": user_msg}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 400},
    }
    body = _json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[WARN] Gemini refinement failed: {e}", file=sys.stderr)
        return prompt_data["positive_prompt"]


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def print_prompt(data: dict, refined: str | None = None) -> None:
    """美观打印一条 prompt。"""
    print(f"\n{'='*72}")
    print(f"🌍 Theme: {data['theme']}")
    if "event" in data:
        print(f"📅 Event: {data['event']} ({data.get('time_ga', '?')} Ga)")
    print(f"📚 Papers cited: {data['paper_count']}")
    print(f"{'─'*72}")
    print(f"✅ POSITIVE PROMPT:")
    print(f"   {data['positive_prompt']}")
    print(f"\n❌ NEGATIVE PROMPT:")
    print(f"   {data['negative_prompt']}")
    if refined:
        print(f"\n✨ LLM-REFINED PROMPT:")
        print(f"   {refined}")
    print(f"\n📖 Citations:")
    for c in data["citations"]:
        print(f"   • {c}")
    print(f"{'='*72}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Paper-grounded Hadean Earth image prompt generator (RAG pipeline)"
    )
    parser.add_argument("--theme", type=str, help="Visual theme to generate prompt for")
    parser.add_argument("--list-themes", action="store_true", help="List all available themes")
    parser.add_argument("--all", action="store_true", help="Generate prompts for all themes")
    parser.add_argument("--timeline", action="store_true", help="Generate timeline-based prompts")
    parser.add_argument("--refine", action="store_true", help="Use LLM to refine prompts")
    parser.add_argument("--output", type=str, help="Export prompts to JSON file")
    parser.add_argument("--db", type=str, default=str(DB_PATH), help="Path to paper database JSON")
    args = parser.parse_args()

    db = load_database(Path(args.db))
    all_prompts: list[dict] = []

    if args.list_themes:
        print("\n📋 Available visual themes:\n")
        for name, info in db["visual_themes"].items():
            paper_count = len(info["relevant_paper_ids"])
            print(f"  • {name:20s} — {info['description']} ({paper_count} papers)")
        print()
        return 0

    if args.timeline:
        prompts = build_timeline_prompts(db)
        for p in prompts:
            refined = refine_with_llm(p) if args.refine else None
            if refined:
                p["refined_prompt"] = refined
            print_prompt(p, refined)
            all_prompts.append(p)

    elif args.all:
        for theme_name in db["visual_themes"]:
            retrieval = retrieve_by_theme(db, theme_name)
            prompt_data = build_prompt(retrieval)
            refined = refine_with_llm(prompt_data) if args.refine else None
            if refined:
                prompt_data["refined_prompt"] = refined
            print_prompt(prompt_data, refined)
            all_prompts.append(prompt_data)

    elif args.theme:
        retrieval = retrieve_by_theme(db, args.theme)
        prompt_data = build_prompt(retrieval)
        refined = refine_with_llm(prompt_data) if args.refine else None
        if refined:
            prompt_data["refined_prompt"] = refined
        print_prompt(prompt_data, refined)
        all_prompts.append(prompt_data)

    else:
        parser.print_help()
        return 1

    # 导出 JSON
    if args.output and all_prompts:
        out_path = Path(args.output)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(all_prompts, f, ensure_ascii=False, indent=2)
        print(f"💾 Exported {len(all_prompts)} prompts to {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
