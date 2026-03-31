#!/usr/bin/env python3
"""
build_presentation.py — 生成最终展示用 HTML
将 gallery/ 中的图片转为 base64 内嵌，生成独立 HTML 文件
"""
import base64, json, sys
from pathlib import Path

GALLERY = Path("gallery")
PROMPTS = json.loads(Path("prompts.json").read_text())

# 主题中文名 + emoji + 时间
THEME_META = {
    "orbit":       ("🌍 宏观行星视角",     "4.2 Ga", "从太空俯瞰冥古宙地球——没有蓝色海洋和绿色大陆，只有黑暗的原始洋壳、零星的火山辉光和浓厚的朦胧大气"),
    "coast":       ("🌊 原始海岸线",       "4.0 Ga", "黑色玄武岩海岸线，暗色温暖海洋，浓厚蒸汽和火山雾霾笼罩，没有任何植被，硫化物大气弥漫"),
    "impact":      ("☄️ 陨石撞击事件",     "4.2 Ga", "巨型小行星撞击地表或海洋，巨大的蒸汽/喷射物羽流、冲击波、发光的撞击熔融物和充满碎屑的天空"),
    "vent":        ("🔥 热液喷口与生命起源", "4.0 Ga", "深海热液喷口——黑色烟囱或白色烟囱喷涌着富含矿物质的热液，铁硫化物沉积，可能是生命诞生之地"),
    "magma_ocean": ("🔴 全球岩浆海洋",     "4.5 Ga", "地球最早期的全球岩浆海洋，炽热的表面漂浮着暗色固化地壳碎片，浓厚的蒸汽大气笼罩"),
    "cool_hadean": ("🌙 温和的冥古宙",     "4.2 Ga", "挑战 '地狱般冥古宙' 叙事——厚厚云层下的暗色海洋、岩石岛屿，温暖但并非炼狱"),
}

def img_to_b64(path: Path) -> str:
    if not path.exists():
        return ""
    data = path.read_bytes()
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"

# 构建每个主题的数据
sections = []
for p in PROMPTS:
    theme = p["theme"]
    meta = THEME_META[theme]
    flux_img = img_to_b64(GALLERY / f"{theme}_flux.png")
    gemini_img = img_to_b64(GALLERY / f"{theme}_gemini.png")
    flux_size = (GALLERY / f"{theme}_flux.png").stat().st_size if (GALLERY / f"{theme}_flux.png").exists() else 0
    gemini_size = (GALLERY / f"{theme}_gemini.png").stat().st_size if (GALLERY / f"{theme}_gemini.png").exists() else 0
    sections.append({
        "theme": theme,
        "title": meta[0],
        "time": meta[1],
        "desc": meta[2],
        "flux_img": flux_img,
        "gemini_img": gemini_img,
        "flux_size": f"{flux_size/1024:.0f} KB",
        "gemini_size": f"{gemini_size/1024:.0f} KB",
        "citations": p.get("citations", []),
        "paper_count": len(p.get("citations", [])),
    })

# 生成主题区块 HTML
theme_html = ""
for i, s in enumerate(sections):
    cite_items = "\n".join(f'<li>{c}</li>' for c in s["citations"])
    theme_html += f"""
<div class="theme-section" id="theme-{s['theme']}">
  <div class="theme-header">
    <h2>{s['title']}</h2>
    <span class="time-badge">⏱ {s['time']}</span>
    <span class="paper-badge">📚 {s['paper_count']} papers</span>
  </div>
  <p class="theme-desc">{s['desc']}</p>
  <div class="compare-grid">
    <div class="image-card flux-card">
      <div class="card-label"><span class="api-tag flux">FLUX Pro 1.1</span><span class="size-tag">{s['flux_size']}</span></div>
      <img src="{s['flux_img']}" alt="FLUX - {s['theme']}" loading="lazy">
    </div>
    <div class="vs-divider">VS</div>
    <div class="image-card gemini-card">
      <div class="card-label"><span class="api-tag gemini">Gemini 2.5 Flash</span><span class="size-tag">{s['gemini_size']}</span></div>
      <img src="{s['gemini_img']}" alt="Gemini - {s['theme']}" loading="lazy">
    </div>
  </div>
  <details class="citations">
    <summary>📖 查看论文引用 ({s['paper_count']} 篇)</summary>
    <ol>{cite_items}</ol>
  </details>
</div>
"""

total_papers = sum(s["paper_count"] for s in sections)
total_images = sum(1 for s in sections if s["flux_img"]) + sum(1 for s in sections if s["gemini_img"])

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>冥古宙地球 — AI 图像对比展板</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;600;700;900&display=swap');
:root {{
  --bg: #06060c;
  --card-bg: #0f0f18;
  --accent: #ff6b35;
  --accent2: #4ecdc4;
  --gemini-color: #4285f4;
  --flux-color: #a78bfa;
  --text: #e8e8f0;
  --muted: #7a7a8e;
  --border: #1e1e30;
  --glow-orange: rgba(255,107,53,0.3);
  --glow-blue: rgba(66,133,244,0.3);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Noto Sans SC', -apple-system, 'SF Pro Display', sans-serif;
  line-height: 1.7;
  overflow-x: hidden;
}}

/* ============ HERO ============ */
.hero {{
  position: relative;
  text-align: center;
  padding: 80px 24px 50px;
  background:
    radial-gradient(ellipse 80% 50% at 50% 0%, rgba(255,80,20,0.12) 0%, transparent 60%),
    linear-gradient(180deg, #120800 0%, var(--bg) 100%);
  border-bottom: 1px solid var(--border);
  overflow: hidden;
}}
.hero::before {{
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='1' cy='1' r='0.6' fill='%23ffffff08'/%3E%3C/svg%3E");
  opacity: 0.5;
}}
.hero h1 {{
  position: relative;
  font-size: 3.2em;
  font-weight: 900;
  letter-spacing: 3px;
  background: linear-gradient(135deg, #ff6b35 0%, #ffd700 40%, #4ecdc4 70%, #4285f4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
  text-shadow: 0 0 60px rgba(255,107,53,0.3);
}}
.hero .subtitle {{
  position: relative;
  color: var(--muted);
  font-size: 1.05em;
  max-width: 750px;
  margin: 0 auto 28px;
  line-height: 1.8;
}}
.stats-row {{
  position: relative;
  display: flex;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
}}
.stat {{ text-align: center; }}
.stat-num {{
  font-size: 2.4em;
  font-weight: 900;
  background: linear-gradient(135deg, var(--accent), #ffd700);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.stat-label {{ font-size: 0.82em; color: var(--muted); margin-top: 2px; }}

/* ============ TIMELINE ============ */
.timeline-bar {{
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 36px 20px 28px;
  gap: 0;
  background: linear-gradient(180deg, var(--bg) 0%, #08080f 100%);
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
}}
.tl-node {{
  text-align: center;
  min-width: 110px;
  position: relative;
}}
.tl-node::after {{
  content: '';
  position: absolute;
  top: 8px; right: -50%;
  width: 100%; height: 2px;
  background: linear-gradient(90deg, var(--accent) 0%, var(--border) 100%);
  z-index: 0;
}}
.tl-node:last-child::after {{ display: none; }}
.tl-dot {{
  width: 16px; height: 16px;
  background: var(--accent);
  border-radius: 50%;
  margin: 0 auto 8px;
  position: relative; z-index: 1;
  box-shadow: 0 0 12px var(--glow-orange), 0 0 24px rgba(255,107,53,0.15);
  animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
  0%,100% {{ box-shadow: 0 0 8px var(--glow-orange); }}
  50% {{ box-shadow: 0 0 20px var(--glow-orange), 0 0 40px rgba(255,107,53,0.1); }}
}}
.tl-time {{ font-size: 0.95em; color: var(--accent2); font-weight: 700; }}
.tl-event {{ font-size: 0.68em; color: var(--muted); max-width: 120px; margin: 4px auto 0; }}

/* ============ THEME SECTIONS ============ */
.theme-section {{
  max-width: 1500px;
  margin: 50px auto;
  padding: 0 24px;
}}
.theme-header {{
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 10px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--accent);
  flex-wrap: wrap;
}}
.theme-header h2 {{
  font-size: 1.7em;
  color: var(--accent);
  font-weight: 700;
}}
.time-badge {{
  background: rgba(78,205,196,0.12);
  color: var(--accent2);
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  border: 1px solid rgba(78,205,196,0.25);
}}
.paper-badge {{
  background: rgba(255,107,53,0.1);
  color: var(--accent);
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
  border: 1px solid rgba(255,107,53,0.25);
}}
.theme-desc {{
  color: var(--muted);
  font-size: 0.9em;
  margin-bottom: 20px;
  max-width: 900px;
}}

/* ============ COMPARE GRID ============ */
.compare-grid {{
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 0;
  align-items: stretch;
}}
.vs-divider {{
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6em;
  font-weight: 900;
  color: var(--accent);
  padding: 0 16px;
  text-shadow: 0 0 20px var(--glow-orange);
  writing-mode: vertical-lr;
  letter-spacing: 4px;
}}
.image-card {{
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  transition: transform 0.25s, box-shadow 0.25s;
}}
.image-card:hover {{
  transform: translateY(-6px) scale(1.01);
}}
.flux-card:hover {{ box-shadow: 0 12px 40px rgba(167,139,250,0.15); }}
.gemini-card:hover {{ box-shadow: 0 12px 40px rgba(66,133,244,0.15); }}
.card-label {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(0,0,0,0.4);
}}
.api-tag {{
  display: inline-block;
  padding: 4px 14px;
  border-radius: 8px;
  font-size: 0.82em;
  font-weight: 700;
  letter-spacing: 0.5px;
}}
.api-tag.flux {{
  background: rgba(167,139,250,0.12);
  color: var(--flux-color);
  border: 1px solid rgba(167,139,250,0.3);
}}
.api-tag.gemini {{
  background: rgba(66,133,244,0.12);
  color: var(--gemini-color);
  border: 1px solid rgba(66,133,244,0.3);
}}
.size-tag {{
  font-size: 0.75em;
  color: var(--muted);
  font-weight: 400;
}}
.image-card img {{
  width: 100%;
  height: 380px;
  object-fit: cover;
  display: block;
  cursor: zoom-in;
  transition: filter 0.3s;
}}
.image-card img:hover {{ filter: brightness(1.1); }}

/* zoom overlay */
.zoom-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
  z-index: 999;
  justify-content: center;
  align-items: center;
  cursor: zoom-out;
}}
.zoom-overlay.active {{ display: flex; }}
.zoom-overlay img {{
  max-width: 95vw;
  max-height: 95vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 0 60px rgba(0,0,0,0.8);
}}

/* ============ CITATIONS ============ */
.citations {{
  margin-top: 16px;
  background: rgba(15,15,24,0.6);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0;
}}
.citations summary {{
  cursor: pointer;
  font-size: 0.88em;
  color: var(--accent2);
  padding: 12px 18px;
  font-weight: 600;
  user-select: none;
}}
.citations summary:hover {{ color: #6ee7de; }}
.citations[open] summary {{ border-bottom: 1px solid var(--border); }}
.citations ol {{
  padding: 14px 18px 14px 36px;
}}
.citations li {{
  font-size: 0.78em;
  color: var(--muted);
  margin-bottom: 6px;
  line-height: 1.6;
}}

/* ============ METHODOLOGY / PIPELINE ============ */
.methodology {{
  max-width: 1100px;
  margin: 70px auto 50px;
  padding: 40px 36px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}}
.methodology::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), var(--accent2), var(--gemini-color));
}}
.methodology h2 {{
  color: var(--accent2);
  font-size: 1.5em;
  margin-bottom: 8px;
}}
.methodology .method-subtitle {{
  color: var(--muted);
  font-size: 0.9em;
  margin-bottom: 28px;
}}
.pipeline {{
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: 0;
  flex-wrap: wrap;
  margin: 24px 0;
}}
.pipe-step {{
  background: linear-gradient(135deg, #111122, #0d0d1a);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 14px;
  text-align: center;
  min-width: 130px;
  max-width: 160px;
  flex: 1;
  transition: border-color 0.3s, transform 0.2s;
}}
.pipe-step:hover {{
  border-color: var(--accent);
  transform: translateY(-4px);
}}
.pipe-icon {{ font-size: 2em; margin-bottom: 6px; }}
.pipe-title {{ font-size: 0.85em; font-weight: 700; color: var(--text); margin-bottom: 4px; }}
.pipe-detail {{ font-size: 0.7em; color: var(--muted); line-height: 1.5; }}
.pipe-arrow {{
  display: flex;
  align-items: center;
  font-size: 1.6em;
  color: var(--accent);
  padding: 0 6px;
  text-shadow: 0 0 10px var(--glow-orange);
}}

/* ============ COST SECTION ============ */
.cost-section {{
  max-width: 900px;
  margin: 0 auto 60px;
  padding: 36px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}}
.cost-section::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #22c55e, #4ecdc4, var(--gemini-color));
}}
.cost-section h2 {{
  color: #22c55e;
  font-size: 1.5em;
  margin-bottom: 24px;
}}
.cost-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}}
.cost-card {{
  background: linear-gradient(135deg, #111122, #0a0a16);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px 20px;
  text-align: center;
  transition: transform 0.2s;
}}
.cost-card:hover {{ transform: translateY(-4px); }}
.cost-card .cost-icon {{ font-size: 2.2em; margin-bottom: 8px; }}
.cost-card .cost-name {{ font-size: 1em; font-weight: 700; margin-bottom: 4px; }}
.cost-card .cost-price {{
  font-size: 1.8em;
  font-weight: 900;
  margin: 8px 0;
}}
.cost-card .cost-detail {{ font-size: 0.78em; color: var(--muted); line-height: 1.5; }}
.cost-card.flux-cost .cost-price {{ color: var(--flux-color); }}
.cost-card.gemini-cost .cost-price {{ color: var(--gemini-color); }}
.cost-card.total-cost .cost-price {{
  background: linear-gradient(135deg, var(--accent), #22c55e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.cost-card.total-cost {{ border-color: rgba(34,197,94,0.3); }}
.cost-total-bar {{
  margin-top: 20px;
  padding: 16px 24px;
  background: rgba(34,197,94,0.06);
  border: 1px solid rgba(34,197,94,0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}}
.cost-total-bar .total-label {{ color: var(--muted); font-size: 0.9em; }}
.cost-total-bar .total-value {{
  font-size: 1.1em;
  font-weight: 700;
  color: #22c55e;
}}

/* ============ FOOTER ============ */
.footer {{
  text-align: center;
  padding: 40px 24px;
  color: var(--muted);
  font-size: 0.82em;
  border-top: 1px solid var(--border);
  background: linear-gradient(180deg, var(--bg) 0%, #04040a 100%);
}}
.footer a {{ color: var(--accent2); text-decoration: none; }}
.footer a:hover {{ text-decoration: underline; }}

@media (max-width: 768px) {{
  .compare-grid {{ grid-template-columns: 1fr; }}
  .vs-divider {{ writing-mode: horizontal-tb; padding: 10px 0; }}
  .hero h1 {{ font-size: 2em; }}
  .cost-grid {{ grid-template-columns: 1fr; }}
  .pipeline {{ flex-direction: column; align-items: center; }}
  .pipe-arrow {{ transform: rotate(90deg); padding: 6px 0; }}
}}
</style>
</head>
<body>

<!-- Zoom overlay -->
<div class="zoom-overlay" id="zoomOverlay" onclick="this.classList.remove('active')">
  <img id="zoomImg" src="" alt="zoom">
</div>

<div class="hero">
  <h1>🌋 冥古宙地球 · AI 视觉重建</h1>
  <p class="subtitle">
    基于 <strong>30 篇</strong>科学论文的视觉约束，使用 <strong>FLUX Pro 1.1</strong> 与 <strong>Gemini 2.5 Flash</strong>
    两种生成式 AI 重建冥古宙地球（4.5 – 3.8 Ga）的六大场景
  </p>
  <div class="stats-row">
    <div class="stat"><div class="stat-num">30</div><div class="stat-label">引用论文</div></div>
    <div class="stat"><div class="stat-num">6</div><div class="stat-label">视觉主题</div></div>
    <div class="stat"><div class="stat-num">{total_images}</div><div class="stat-label">生成图像</div></div>
    <div class="stat"><div class="stat-num">2</div><div class="stat-label">AI 工具</div></div>
  </div>
</div>

<!-- TIMELINE -->
<div class="timeline-bar">
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">4.53 Ga</div><div class="tl-event">Theia 大撞击<br>月球形成</div></div>
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">4.5 Ga</div><div class="tl-event">全球岩浆海洋</div></div>
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">4.4 Ga</div><div class="tl-event">最早液态水<br>原始地壳</div></div>
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">4.3 Ga</div><div class="tl-event">锆石证据<br>表面液态水</div></div>
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">4.2 Ga</div><div class="tl-event">早期地磁场</div></div>
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">4.0 Ga</div><div class="tl-event">原始地壳分异</div></div>
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">3.9 Ga</div><div class="tl-event">晚期重轰炸</div></div>
  <div class="tl-node"><div class="tl-dot"></div><div class="tl-time">3.8 Ga</div><div class="tl-event">过渡到<br>始太古代</div></div>
</div>

<!-- ====== THEME COMPARISONS ====== -->
{theme_html}

<!-- ====== PIPELINE / METHODOLOGY ====== -->
<div class="methodology">
  <h2>📐 工作流：论文驱动的 AI 图像生成流水线</h2>
  <p class="method-subtitle">Paper-grounded Hadean Earth Visualization Pipeline</p>
  <div class="pipeline">
    <div class="pipe-step">
      <div class="pipe-icon">📚</div>
      <div class="pipe-title">论文知识库</div>
      <div class="pipe-detail">收集 30 篇冥古宙<br>相关研究论文<br>提取视觉约束</div>
    </div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">
      <div class="pipe-icon">🗂️</div>
      <div class="pipe-title">结构化数据库</div>
      <div class="pipe-detail">JSON 数据库<br>6 大主题分类<br>9 个时间节点</div>
    </div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">
      <div class="pipe-icon">🔍</div>
      <div class="pipe-title">RAG 检索</div>
      <div class="pipe-detail">按主题/时间<br>检索相关论文<br>匹配视觉关键词</div>
    </div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">
      <div class="pipe-icon">🧩</div>
      <div class="pipe-title">Prompt 组装</div>
      <div class="pipe-detail">结构化拼装<br>正/负提示词<br>文献约束注入</div>
    </div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">
      <div class="pipe-icon">🤖</div>
      <div class="pipe-title">多 API 生成</div>
      <div class="pipe-detail">FLUX Pro 1.1<br>Gemini 2.5 Flash<br>并行批量调用</div>
    </div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step">
      <div class="pipe-icon">⚖️</div>
      <div class="pipe-title">对比分析</div>
      <div class="pipe-detail">科学一致性检查<br>视觉风格对比<br>生成展板</div>
    </div>
  </div>
  <p style="color: var(--muted); font-size: 0.88em; text-align: center; margin-top: 16px; line-height: 1.8;">
    每张图像的 Prompt 并非凭空想象，而是由论文中提取的地质、大气、海洋等视觉特征<strong>自动检索并拼装</strong>而成。<br>
    这是一个 <em style="color:var(--accent2)">文献驱动的推测性视觉重建</em>（Literature-informed Speculative Visualization）流程。
  </p>
</div>

<!-- ====== COST SECTION ====== -->
<div class="cost-section">
  <h2>💰 制作成本</h2>
  <div class="cost-grid">
    <div class="cost-card flux-cost">
      <div class="cost-icon">⚡</div>
      <div class="cost-name">FLUX Pro 1.1</div>
      <div class="cost-price">$10</div>
      <div class="cost-detail">
        Black Forest Labs API<br>
        ~$0.055/张 (1440×960)<br>
        本次生成 7 张
      </div>
    </div>
    <div class="cost-card gemini-cost">
      <div class="cost-icon">💎</div>
      <div class="cost-name">Gemini 2.5 Flash</div>
      <div class="cost-price">¥20</div>
      <div class="cost-detail">
        via NovAI 代理转发<br>
        Google Gemini Image API<br>
        本次生成 7 张
      </div>
    </div>
    <div class="cost-card total-cost">
      <div class="cost-icon">🧾</div>
      <div class="cost-name">总计</div>
      <div class="cost-price">≈ ¥93</div>
      <div class="cost-detail">
        $10 + ¥20 ≈ ¥93<br>
        14 张 AI 图像<br>
        平均 ¥6.6/张
      </div>
    </div>
  </div>
  <div class="cost-total-bar">
    <span class="total-label">📊 性价比：用不到一顿饭的钱，重建了 45 亿年前的地球</span>
    <span class="total-value">✅ 学生友好价格</span>
  </div>
</div>

<!-- FOOTER -->
<div class="footer">
  <p style="font-size:1.1em; color:var(--text); margin-bottom:12px;">
    冥古宙地球 AI 视觉重建项目 · Paper-grounded Hadean Earth Visualization
  </p>
  <p>
    工具链：<code>paper_to_prompt_rag.py</code> → <code>batch_generate_images.py</code> → <code>build_presentation.py</code>
  </p>
  <p style="margin-top: 12px; padding: 12px; background: rgba(255,107,53,0.06); border-radius: 8px; display: inline-block;">
    ⚠️ 免责声明：这些图像是基于文献的<strong>推测性可视化</strong>，不是冥古宙地球的真实照片。<br>
    <span style="font-size:0.85em">Disclaimer: These are literature-informed speculative visualizations, not actual photographs.</span>
  </p>
</div>

<script>
// 点击图片放大
document.querySelectorAll('.image-card img').forEach(img => {{
  img.addEventListener('click', () => {{
    const overlay = document.getElementById('zoomOverlay');
    document.getElementById('zoomImg').src = img.src;
    overlay.classList.add('active');
  }});
}});
document.addEventListener('keydown', e => {{
  if (e.key === 'Escape') document.getElementById('zoomOverlay').classList.remove('active');
}});
</script>
</body>
</html>"""

out = Path("presentation.html")
out.write_text(html, encoding="utf-8")
print(f"✅ Written {out} ({len(html)/1024/1024:.1f} MB)")
