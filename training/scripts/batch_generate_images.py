#!/usr/bin/env python3
"""
batch_generate_images.py — 批量调用多个 AI API 生成冥古宙地球图像

支持的 API:
  1. Google Gemini Imagen (imagen-3.0-generate-002)
  2. FLUX API (Black Forest Labs)

用法:
    # 先用 RAG 脚本生成 prompts.json
    python paper_to_prompt_rag.py --all --output prompts.json

    # 用 Gemini Imagen 生成所有主题
    python batch_generate_images.py --input prompts.json --api gemini

    # 用 FLUX 生成所有主题
    python batch_generate_images.py --input prompts.json --api flux

    # 两个 API 同时用，生成对比图
    python batch_generate_images.py --input prompts.json --api both

    # 指定输出目录
    python batch_generate_images.py --input prompts.json --api both --outdir ./gallery

环境变量:
    GEMINI_API_KEY  — Google AI Studio API key (或 novai.su 的 sk-xxx key)
    GEMINI_BASE_URL — Gemini API 代理 base URL (默认 https://generativelanguage.googleapis.com)
    BFL_API_KEY     — Black Forest Labs (FLUX) API key
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _api_request(url: str, data: dict, headers: dict, method: str = "POST") -> dict:
    """发送 JSON API 请求并返回解析后的 JSON。"""
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] HTTP {e.code}: {error_body}", file=sys.stderr)
        raise


def _api_get(url: str, headers: dict) -> dict:
    """发送 GET 请求。"""
    req = Request(url, headers=headers, method="GET")
    with urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _save_base64_image(b64_data: str, path: Path) -> None:
    """将 base64 编码的图片保存到文件。"""
    img_bytes = base64.b64decode(b64_data)
    path.write_bytes(img_bytes)


def _download_image(url: str, path: Path) -> None:
    """从 URL 下载图片到文件。"""
    req = Request(url, method="GET")
    with urlopen(req, timeout=60) as resp:
        path.write_bytes(resp.read())


# ---------------------------------------------------------------------------
# Google Gemini Imagen API
# ---------------------------------------------------------------------------

def generate_gemini(prompt: str, negative: str, outdir: Path, name: str) -> dict | None:
    """调用 Google Gemini Imagen API 生成图像。"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[SKIP] GEMINI_API_KEY not set", file=sys.stderr)
        return None

    full_prompt = prompt
    if negative:
        full_prompt += f". Avoid: {negative}"

    print(f"  🎨 [Gemini] Generating: {name}...")

    # 支持自定义 base URL（如 novai.su 代理: https://us.novaiapi.com）
    base_url = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")

    # 依次尝试多个 Gemini 图像模型
    IMAGE_MODELS = [
        "gemini-2.5-flash-image",
        "gemini-3.1-flash-image-preview",
        "gemini-3-pro-image-preview",
    ]

    for model in IMAGE_MODELS:
        url = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"
        data = {
            "contents": [{"parts": [{"text": f"Generate a photorealistic image: {full_prompt}"}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
        }
        headers = {"Content-Type": "application/json"}

        try:
            result = _api_request(url, data, headers)
        except Exception as e:
            print(f"  ⚠️  [Gemini] {model} failed ({e}), trying next...", file=sys.stderr)
            continue

        # 从返回中提取 inlineData 图片
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                inline = part.get("inlineData", {})
                if inline.get("mimeType", "").startswith("image/"):
                    filename = outdir / f"{name}_gemini.png"
                    _save_base64_image(inline["data"], filename)
                    print(f"  ✅ [Gemini/{model}] Saved: {filename}")
                    return {"api": "gemini", "file": str(filename), "prompt": prompt}

    print(f"  ❌ [Gemini] All models failed", file=sys.stderr)
    return None





# ---------------------------------------------------------------------------
# FLUX API (Black Forest Labs)
# ---------------------------------------------------------------------------

def generate_flux(prompt: str, negative: str, outdir: Path, name: str) -> dict | None:
    """调用 FLUX API 生成图像（异步：先提交，再轮询）。"""
    api_key = os.environ.get("BFL_API_KEY")
    if not api_key:
        print("[SKIP] BFL_API_KEY not set", file=sys.stderr)
        return None

    print(f"  🎨 [FLUX] Generating: {name}...")

    data = {
        "prompt": prompt,
        "width": 1440,
        "height": 960,
    }
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "x-key": api_key,
    }

    # 1. 提交任务
    try:
        submit_result = _api_request(
            "https://api.bfl.ai/v1/flux-pro-1.1",
            data, headers
        )
    except Exception as e:
        print(f"  ❌ [FLUX] Submit failed: {e}", file=sys.stderr)
        return None

    task_id = submit_result.get("id")
    if not task_id:
        print(f"  ❌ [FLUX] No task ID: {submit_result}", file=sys.stderr)
        return None

    # 2. 轮询结果
    poll_url = f"https://api.bfl.ai/v1/get_result?id={task_id}"
    poll_headers = {"accept": "application/json", "x-key": api_key}

    for attempt in range(60):  # 最多等 5 分钟
        time.sleep(5)
        try:
            status = _api_get(poll_url, poll_headers)
        except Exception:
            continue

        if status.get("status") == "Ready":
            image_url = status.get("result", {}).get("sample")
            if image_url:
                filename = outdir / f"{name}_flux.png"
                _download_image(image_url, filename)
                print(f"  ✅ [FLUX] Saved: {filename}")
                return {"api": "flux", "file": str(filename), "prompt": prompt}
            break
        elif status.get("status") in ("Error", "Request Moderated"):
            print(f"  ❌ [FLUX] Error: {status}", file=sys.stderr)
            break
        else:
            sys.stdout.write(".")
            sys.stdout.flush()

    print(f"\n  ❌ [FLUX] Timed out for {name}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# 主逻辑
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch generate Hadean Earth images using multiple AI APIs"
    )
    parser.add_argument("--input", type=str, required=True,
                        help="Path to prompts.json (from paper_to_prompt_rag.py)")
    parser.add_argument("--api", choices=["gemini", "flux", "both"], default="both",
                        help="Which API(s) to use")
    parser.add_argument("--outdir", type=str, default="gallery",
                        help="Output directory for generated images")
    parser.add_argument("--use-refined", action="store_true",
                        help="Use LLM-refined prompts if available")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Delay between API calls (seconds)")
    args = parser.parse_args()

    # 加载 prompts
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found. Run paper_to_prompt_rag.py --all --output prompts.json first.",
              file=sys.stderr)
        return 1

    with input_path.open("r", encoding="utf-8") as f:
        prompts = json.load(f)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Batch generation starting")
    print(f"   Prompts: {len(prompts)}")
    print(f"   API(s):  {args.api}")
    print(f"   Output:  {outdir}\n")

    results: list[dict] = []
    use_apis = []
    if args.api in ("gemini", "both"):
        use_apis.append("gemini")
    if args.api in ("flux", "both"):
        use_apis.append("flux")

    for i, prompt_data in enumerate(prompts):
        theme = prompt_data.get("theme", f"prompt_{i}")
        positive = prompt_data.get("positive_prompt", "")
        negative = prompt_data.get("negative_prompt", "")

        # 如果有 LLM 润色版且用户选择了，优先用
        if args.use_refined and "refined_prompt" in prompt_data:
            positive = prompt_data["refined_prompt"]

        safe_name = theme.replace("/", "_").replace(" ", "_")

        print(f"\n{'─'*60}")
        print(f"[{i+1}/{len(prompts)}] Theme: {theme}")
        print(f"  Keywords: {', '.join(prompt_data.get('keywords_used', [])[:5])}...")
        print(f"  Papers:   {prompt_data.get('paper_count', '?')} cited")

        for api_name in use_apis:
            if api_name == "gemini":
                r = generate_gemini(positive, negative, outdir, safe_name)
            elif api_name == "flux":
                r = generate_flux(positive, negative, outdir, safe_name)
            else:
                continue

            if r:
                r["theme"] = theme
                r["citations"] = prompt_data.get("citations", [])
                results.append(r)

            if args.delay > 0:
                time.sleep(args.delay)

    # 保存结果清单
    manifest_path = outdir / "generation_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"🎉 Done! Generated {len(results)} images.")
    print(f"📋 Manifest: {manifest_path}")
    print(f"📁 Gallery:  {outdir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
