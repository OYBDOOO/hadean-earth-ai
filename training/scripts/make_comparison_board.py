#!/usr/bin/env python3
"""
make_comparison_board.py — 生成冥古宙地球 AI 图像对比展板 (HTML)

从 gallery/generation_manifest.json 读取生成记录，
输出一个漂亮的 HTML 页面，用于课堂展示。

用法:
    # 默认从 gallery/ 读取
    python make_comparison_board.py

    # 指定目录
    python make_comparison_board.py --gallery ./my_gallery

    # 指定输出文件
    python make_comparison_board.py --output presentation.html

    # 也可以直接指定图片目录（即使没有 manifest，会自动扫描）
    python make_comparison_board.py --gallery ./my_images --scan
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# HTML 模板
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>冥古宙地球 — AI 图像对比展板</title>
<style>
  :root {{
    --bg: #0a0a0f;
    --card-bg: #12121a;
    --accent: #ff6b35;
    --accent2: #4ecdc4;
    --text: #e0e0e0;
    --muted: #888;
    --border: #2a2a3a;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'SF Pro Display', -apple-system, 'Segoe UI', sans-serif;
    line-height: 1.6;
  }}

  /* 头部 */
  .hero {{
    text-align: center;
    padding: 60px 20px 40px;
    background: linear-gradient(180deg, #1a0a00 0%, var(--bg) 100%);
    border-bottom: 1px solid var(--border);
  }}
  .hero h1 {{
    font-size: 2.8em;
    background: linear-gradient(135deg, var(--accent), #ffd700, var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
    letter-spacing: 2px;
  }}
  .hero .subtitle {{
    color: var(--muted);
    font-size: 1.1em;
    max-width: 700px;
    margin: 0 auto;
  }}
  .hero .stats {{
    margin-top: 20px;
    display: flex;
    justify-content: center;
    gap: 40px;
  }}
  .hero .stat {{
    text-align: center;
  }}
  .hero .stat-num {{
    font-size: 2em;
    font-weight: 700;
    color: var(--accent);
  }}
  .hero .stat-label {{
    font-size: 0.85em;
    color: var(--muted);
  }}

  /* 时间线 */
  .timeline-bar {{
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 30px 20px;
    gap: 0;
    overflow-x: auto;
    background: #0d0d14;
    border-bottom: 1px solid var(--border);
  }}
  .tl-node {{
    text-align: center;
    min-width: 100px;
    position: relative;
  }}
  .tl-node::after {{
    content: '';
    position: absolute;
    top: 12px;
    right: -50%;
    width: 100%;
    height: 2px;
    background: var(--border);
    z-index: 0;
  }}
  .tl-node:last-child::after {{ display: none; }}
  .tl-dot {{
    width: 12px; height: 12px;
    background: var(--accent);
    border-radius: 50%;
    margin: 0 auto 6px;
    position: relative;
    z-index: 1;
    box-shadow: 0 0 8px var(--accent);
  }}
  .tl-time {{ font-size: 0.9em; color: var(--accent2); font-weight: 600; }}
  .tl-event {{ font-size: 0.7em; color: var(--muted); max-width: 120px; margin: 0 auto; }}

  /* 主题区域 */
  .theme-section {{
    max-width: 1400px;
    margin: 40px auto;
    padding: 0 20px;
  }}
  .theme-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--accent);
  }}
  .theme-header h2 {{
    font-size: 1.6em;
    color: var(--accent);
  }}
  .theme-header .paper-badge {{
    background: var(--accent2);
    color: #000;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
  }}

  /* 对比网格 */
  .compare-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 20px;
  }}
  .image-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .image-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(255, 107, 53, 0.15);
  }}
  .image-card img {{
    width: 100%;
    height: 300px;
    object-fit: cover;
    display: block;
  }}
  .image-card .placeholder {{
    width: 100%;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a0500, #0a0a1a);
    color: var(--muted);
    font-size: 1.2em;
  }}
  .card-info {{
    padding: 16px;
  }}
  .card-info .api-tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.8em;
    font-weight: 600;
    margin-bottom: 8px;
  }}
  .api-tag.gemini {{ background: #4285f422; color: #8ab4f8; border: 1px solid #4285f444; }}
  .api-tag.flux {{ background: #7c3aed22; color: #a78bfa; border: 1px solid #7c3aed44; }}
  .api-tag.midjourney {{ background: #e1195722; color: #ff6b8a; border: 1px solid #e1195744; }}
  .card-info .prompt-preview {{
    font-size: 0.8em;
    color: var(--muted);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}

  /* 引用区 */
  .citations {{
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
  }}
  .citations summary {{
    cursor: pointer;
    font-size: 0.85em;
    color: var(--accent2);
  }}
  .citations ul {{
    margin-top: 6px;
    padding-left: 16px;
  }}
  .citations li {{
    font-size: 0.75em;
    color: var(--muted);
    margin-bottom: 4px;
  }}

  /* 方法论 */
  .methodology {{
    max-width: 1000px;
    margin: 60px auto;
    padding: 30px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
  }}
  .methodology h2 {{ color: var(--accent2); margin-bottom: 16px; }}
  .method-flow {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin: 20px 0;
  }}
  .method-step {{
    background: #1a1a2e;
    border: 1px solid var(--accent);
    border-radius: 8px;
    padding: 10px 16px;
    text-align: center;
    min-width: 120px;
  }}
  .method-step .step-num {{
    font-size: 1.4em;
    color: var(--accent);
    font-weight: 700;
  }}
  .method-step .step-text {{
    font-size: 0.8em;
    color: var(--text);
  }}
  .method-arrow {{
    font-size: 1.5em;
    color: var(--accent);
  }}

  /* 页脚 */
  .footer {{
    text-align: center;
    padding: 40px 20px;
    color: var(--muted);
    font-size: 0.85em;
    border-top: 1px solid var(--border);
  }}

  @media (max-width: 600px) {{
    .compare-grid {{ grid-template-columns: 1fr; }}
    .hero h1 {{ font-size: 1.8em; }}
  }}
</style>
</head>
<body>

<div class="hero">
  <h1>🌋 冥古宙地球 · AI 视觉重建</h1>
  <p class="subtitle">
    基于 {paper_count} 篇科学论文的视觉约束，使用多种生成式 AI 工具重建冥古宙地球（4.5–3.8 Ga）的不同面貌
  </p>
  <div class="stats">
    <div class="stat">
      <div class="stat-num">{paper_count}</div>
      <div class="stat-label">引用论文</div>
    </div>
    <div class="stat">
      <div class="stat-num">{theme_count}</div>
      <div class="stat-label">视觉主题</div>
    </div>
    <div class="stat">
      <div class="stat-num">{image_count}</div>
      <div class="stat-label">生成图像</div>
    </div>
    <div class="stat">
      <div class="stat-num">{api_count}</div>
      <div class="stat-label">AI 工具</div>
    </div>
  </div>
</div>

<div class="timeline-bar">
{timeline_html}
</div>

<div class="methodology">
  <h2>📐 方法论：论文驱动的图像生成流水线</h2>
  <div class="method-flow">
    <div class="method-step">
      <div class="step-num">①</div>
      <div class="step-text">论文知识库<br><small>{paper_count} 篇</small></div>
    </div>
    <div class="method-arrow">→</div>
    <div class="method-step">
      <div class="step-num">②</div>
      <div class="step-text">视觉约束<br><small>提取</small></div>
    </div>
    <div class="method-arrow">→</div>
    <div class="method-step">
      <div class="step-num">③</div>
      <div class="step-text">RAG 检索<br><small>按主题匹配</small></div>
    </div>
    <div class="method-arrow">→</div>
    <div class="method-step">
      <div class="step-num">④</div>
      <div class="step-text">Prompt 组装<br><small>结构化拼装</small></div>
    </div>
    <div class="method-arrow">→</div>
    <div class="method-step">
      <div class="step-num">⑤</div>
      <div class="step-text">多 API 生成<br><small>Gemini + FLUX</small></div>
    </div>
    <div class="method-arrow">→</div>
    <div class="method-step">
      <div class="step-num">⑥</div>
      <div class="step-text">对比分析<br><small>科学一致性</small></div>
    </div>
  </div>
  <p style="color: var(--muted); font-size: 0.9em; text-align: center;">
    每张图像的 prompt 不是凭空想象，而是由论文中提取的地质、大气、海洋等视觉特征自动拼装而成。<br>
    这是一个 <strong>文献驱动的视觉重建</strong>（literature-informed speculative visualization）流程。
  </p>
</div>

{sections_html}

<div class="footer">
  <p>冥古宙地球 AI 视觉重建项目 · Paper-grounded Hadean Earth Visualization</p>
  <p>Generated by paper_to_prompt_rag.py + batch_generate_images.py</p>
  <p style="margin-top: 8px;">
    ⚠️ 免责声明：这些图像是基于文献的推测性可视化，不是冥古宙地球的真实照片。<br>
    Disclaimer: These are literature-informed speculative visualizations, not actual photographs.
  </p>
</div>

</body>
</html>
"""

# ---------------------------------------------------------------------------
# 主题中文名映射
# ---------------------------------------------------------------------------

THEME_CN = {
    "orbit": "🌍 宏观行星视角",
    "coast": "🌊 地表火山海洋",
    "impact": "☄️ 陨石撞击事件",
    "vent": "🔥 热液喷口与生命起源",
    "magma_ocean": "🔴 全球岩浆海洋",
    "cool_hadean": "🌙 冷却后的冥古宙",
}

TIMELINE_EVENTS = [
    ("4.53 Ga", "Theia 大撞击 / 月球形成"),
    ("4.5 Ga", "全球岩浆海洋"),
    ("4.4 Ga", "最早液态水 / 原始地壳"),
    ("4.3 Ga", "锆石证据：表面液态水"),
    ("4.2 Ga", "早期地磁场"),
    ("4.0 Ga", "原始地壳分异"),
    ("3.9 Ga", "晚期重轰炸"),
    ("3.8 Ga", "过渡到始太古代"),
]


# ---------------------------------------------------------------------------
# 构建函数
# ---------------------------------------------------------------------------

def embed_image_or_placeholder(filepath: str | None) -> str:
    """将图片嵌入为 base64 data URI，或返回占位符。"""
    if filepath:
        p = Path(filepath)
        if p.exists():
            data = base64.b64encode(p.read_bytes()).decode("ascii")
            suffix = p.suffix.lower().lstrip(".")
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(suffix, "image/png")
            return f'<img src="data:{mime};base64,{data}" alt="Hadean Earth">'
    return '<div class="placeholder">🎨 待生成<br><small>运行 batch_generate_images.py</small></div>'


def build_timeline_html() -> str:
    nodes = []
    for time_str, event in TIMELINE_EVENTS:
        nodes.append(f"""
  <div class="tl-node">
    <div class="tl-dot"></div>
    <div class="tl-time">{time_str}</div>
    <div class="tl-event">{event}</div>
  </div>""")
    return "\n".join(nodes)


def build_sections(manifest: list[dict], db: dict | None) -> str:
    """根据 manifest 和数据库构建主题展示区域。"""
    # 按主题分组
    by_theme: dict[str, list[dict]] = {}
    for item in manifest:
        theme = item.get("theme", "unknown")
        # 清理 timeline_ 前缀
        clean_theme = re.sub(r"^timeline_[\d.]+Ga$", "timeline", theme)
        by_theme.setdefault(clean_theme, []).append(item)

    # 如果没有 manifest 数据但有 db，创建占位卡片
    if not manifest and db:
        for theme_name in db.get("visual_themes", {}):
            by_theme[theme_name] = []

    sections = []
    for theme, items in by_theme.items():
        theme_cn = THEME_CN.get(theme, f"🌍 {theme}")
        paper_count = 0
        if items:
            paper_count = items[0].get("paper_count", len(items[0].get("citations", [])))

        # 构建图片卡
        cards = []
        if items:
            for item in items:
                api = item.get("api", "unknown")
                prompt = item.get("prompt", "")[:200]
                img_html = embed_image_or_placeholder(item.get("file"))

                citations_html = ""
                if item.get("citations"):
                    cites = "\n".join(f"<li>{c}</li>" for c in item["citations"][:5])
                    citations_html = f"""
              <div class="citations">
                <details><summary>📚 论文依据 ({len(item['citations'])} 篇)</summary>
                  <ul>{cites}</ul>
                </details>
              </div>"""

                cards.append(f"""
          <div class="image-card">
            {img_html}
            <div class="card-info">
              <span class="api-tag {api}">{api.upper()}</span>
              <div class="prompt-preview">{prompt}...</div>
              {citations_html}
            </div>
          </div>""")
        else:
            # 占位卡片
            for api in ["gemini", "flux"]:
                cards.append(f"""
          <div class="image-card">
            <div class="placeholder">🎨 待生成 ({api.upper()})<br><small>运行 batch_generate_images.py --api {api}</small></div>
            <div class="card-info">
              <span class="api-tag {api}">{api.upper()}</span>
              <div class="prompt-preview">运行 RAG 流水线后将自动填充论文驱动的 prompt</div>
            </div>
          </div>""")

        section = f"""
<div class="theme-section">
  <div class="theme-header">
    <h2>{theme_cn}</h2>
    <span class="paper-badge">📚 {paper_count} papers</span>
  </div>
  <div class="compare-grid">
    {''.join(cards)}
  </div>
</div>"""
        sections.append(section)

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an HTML comparison board for Hadean Earth AI images"
    )
    parser.add_argument("--gallery", type=str, default="gallery",
                        help="Gallery directory with images and manifest")
    parser.add_argument("--output", type=str, default="hadean_comparison_board.html",
                        help="Output HTML file path")
    parser.add_argument("--db", type=str,
                        default=str(Path(__file__).resolve().parents[1] / "data" / "hadean_paper_database.json"),
                        help="Path to paper database JSON")
    parser.add_argument("--scan", action="store_true",
                        help="Scan gallery for images even without manifest")
    args = parser.parse_args()

    gallery = Path(args.gallery)
    manifest: list[dict] = []
    db: dict | None = None

    # 加载论文数据库
    db_path = Path(args.db)
    if db_path.exists():
        with db_path.open("r", encoding="utf-8") as f:
            db = json.load(f)

    # 加载 manifest
    manifest_path = gallery / "generation_manifest.json"
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    elif args.scan and gallery.exists():
        # 扫描目录中的图片
        for img_path in sorted(gallery.glob("*.png")):
            name = img_path.stem
            api = "unknown"
            theme = name
            if "_openai" in name:
                api = "openai"
                theme = name.replace("_openai", "")
            elif "_flux" in name:
                api = "flux"
                theme = name.replace("_flux", "")
            manifest.append({
                "api": api,
                "theme": theme,
                "file": str(img_path),
                "prompt": f"(scanned from {img_path.name})",
                "citations": [],
            })

    # 统计
    paper_count = len(db["papers"]) if db else 0
    theme_count = len(db["visual_themes"]) if db else len(set(m.get("theme") for m in manifest))
    image_count = len(manifest)
    apis_used = set(m.get("api") for m in manifest)
    api_count = len(apis_used) if apis_used else 2

    # 组装 HTML
    html = HTML_TEMPLATE.format(
        paper_count=paper_count,
        theme_count=theme_count,
        image_count=image_count if image_count else "—",
        api_count=api_count,
        timeline_html=build_timeline_html(),
        sections_html=build_sections(manifest, db),
    )

    out_path = Path(args.output)
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ Comparison board saved to: {out_path}")
    print(f"   Open it in a browser to preview the presentation.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
