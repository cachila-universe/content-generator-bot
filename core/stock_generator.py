"""
AI Stock Image Generator — Multi-provider cascade with automatic rollover.

Priority order (all have free tiers, no credit card required):
  1. Leonardo AI   — 150 free tokens/day  (best quality)
  2. Stability AI  — 25 free credits       (SD 3.5 Medium)
  3. HuggingFace   — ~30 images/day        (always-free fallback)

When a provider's daily limit is exhausted, the system automatically rolls
over to the next one.  If ALL providers are exhausted, returns None and the
caller falls back to Pexels.

Usage is tracked per-day in  data/ai_image_usage.json  so limits reset at
midnight UTC.

Functions consumed by seo_optimizer.py:
  • get_usable_images_for_niche(niche_id, limit) — return cached AI images
  • _generate_image_cascading(prompt, neg, settings, w, h) — cascade call
  • _build_prompt(title, niche_id) — build positive/negative prompt pair
"""

import io
import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_STOCK_DIR = _PROJECT_ROOT / "data" / "stock_images"
_USAGE_FILE = _PROJECT_ROOT / "data" / "ai_image_usage.json"

# ── Daily free-tier limits ────────────────────────────────────────────────────
_DAILY_LIMITS = {
    "leonardo": 150,     # tokens / day  (1 image ≈ 5 tokens)
    "stability": 25,     # credits / day
    "huggingface": 30,   # images / day
}

# How many "units" each generation costs
_COST_PER_IMAGE = {
    "leonardo": 5,       # ~5 tokens per image
    "stability": 1,      # 1 credit per image
    "huggingface": 1,    # 1 request per image
}

# ── Niche → concrete visual prompts ──────────────────────────────────────────
_NICHE_VISUAL_HINTS = {
    "ai_tools":           "modern software interface, digital workspace, clean UI, technology",
    "personal_finance":   "money, investment charts, financial planning, piggy bank, coins",
    "health_biohacking":  "healthy lifestyle, supplements, wellness, biohacking lab",
    "home_tech":          "smart home devices, modern living room, IoT gadgets",
    "travel":             "scenic destination, travel photography, adventure landscape",
    "pet_care":           "cute pets, dogs, cats, veterinary care, pet supplies",
    "fitness_wellness":   "gym workout, exercise equipment, fitness, healthy body",
    "remote_work":        "home office setup, laptop, remote working, cozy desk",
}

_NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, watermark, text overlay, logo, "
    "deformed, ugly, bad anatomy, cartoon, anime, illustration, "
    "nsfw, violent, gore, offensive"
)


# ═══════════════════════════════════════════════════════════════════════════════
#  Usage Tracking
# ═══════════════════════════════════════════════════════════════════════════════

def _load_usage() -> dict:
    """Load today's usage counters. Resets if date has changed."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        if _USAGE_FILE.exists():
            data = json.loads(_USAGE_FILE.read_text(encoding="utf-8"))
            if data.get("date") == today:
                return data
    except Exception:
        pass
    # Fresh day — reset all counters
    return {
        "date": today,
        "leonardo": 0,
        "stability": 0,
        "huggingface": 0,
        "total_generated": 0,
    }


def _save_usage(usage: dict) -> None:
    try:
        _USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _USAGE_FILE.write_text(json.dumps(usage, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.warning("Failed to save AI image usage: %s", exc)


def _can_use_provider(provider: str, usage: dict) -> bool:
    """Check if provider still has budget remaining today."""
    used = usage.get(provider, 0)
    limit = _DAILY_LIMITS.get(provider, 0)
    cost = _COST_PER_IMAGE.get(provider, 1)
    return (used + cost) <= limit


def _record_usage(provider: str, usage: dict) -> dict:
    """Increment usage counter for a provider."""
    cost = _COST_PER_IMAGE.get(provider, 1)
    usage[provider] = usage.get(provider, 0) + cost
    usage["total_generated"] = usage.get("total_generated", 0) + 1
    _save_usage(usage)
    return usage


def get_usage_summary() -> dict:
    """Return a summary of today's AI image generation usage."""
    usage = _load_usage()
    summary = {"date": usage.get("date", ""), "providers": {}}
    for provider in ("leonardo", "stability", "huggingface"):
        used = usage.get(provider, 0)
        limit = _DAILY_LIMITS[provider]
        summary["providers"][provider] = {
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used),
            "exhausted": used >= limit,
        }
    summary["total_generated"] = usage.get("total_generated", 0)
    return summary


# ═══════════════════════════════════════════════════════════════════════════════
#  Prompt Builder
# ═══════════════════════════════════════════════════════════════════════════════

def _build_prompt(title: str, niche_id: str) -> dict:
    """
    Build a structured prompt for AI image generation from article title + niche.

    Returns:
        {"positive": "...", "negative": "..."}
    """
    import re

    # Clean title
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip()

    # Get niche visual context
    niche_hint = _NICHE_VISUAL_HINTS.get(niche_id, "technology, modern, professional")

    positive = (
        f"Professional stock photograph for article: {clean}. "
        f"Context: {niche_hint}. "
        "High quality, sharp focus, natural lighting, photorealistic, "
        "editorial style, clean composition, 4K resolution, "
        "suitable for blog hero image."
    )

    return {
        "positive": positive,
        "negative": _NEGATIVE_PROMPT,
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  Provider Implementations
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_leonardo(prompt: str, negative: str, api_key: str, width: int, height: int) -> bytes | None:
    """Generate an image via Leonardo AI API."""
    import requests

    if not api_key:
        return None

    try:
        # Step 1: Create generation request
        resp = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "negative_prompt": negative,
                "width": min(width, 1024),
                "height": min(height, 1024),
                "num_images": 1,
                "modelId": "6b645e3a-d64f-4341-a6d8-7a3690fbf042",  # Leonardo Creative
                "guidance_scale": 7,
                "sd_version": "v2",
            },
            timeout=30,
        )
        resp.raise_for_status()
        generation_id = resp.json().get("sdGenerationJob", {}).get("generationId")
        if not generation_id:
            return None

        # Step 2: Poll for completion (max 60s)
        for _ in range(12):
            time.sleep(5)
            poll = requests.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            poll.raise_for_status()
            gen_data = poll.json().get("generations_by_pk", {})
            status = gen_data.get("status")

            if status == "COMPLETE":
                images = gen_data.get("generated_images", [])
                if images:
                    img_url = images[0].get("url")
                    if img_url:
                        img_resp = requests.get(img_url, timeout=20)
                        img_resp.raise_for_status()
                        logger.info("Leonardo AI: image generated successfully")
                        return img_resp.content
                return None
            elif status == "FAILED":
                logger.warning("Leonardo AI generation failed")
                return None

        logger.warning("Leonardo AI: generation timed out")
        return None

    except Exception as exc:
        logger.debug("Leonardo AI error: %s", exc)
        return None


def _generate_stability(prompt: str, negative: str, api_key: str, width: int, height: int) -> bytes | None:
    """Generate an image via Stability AI API (SD 3.5 Medium)."""
    import requests

    if not api_key:
        return None

    try:
        # Round dimensions to nearest multiple of 64 (Stability requirement)
        w = max(512, min(1024, (width // 64) * 64))
        h = max(512, min(1024, (height // 64) * 64))

        resp = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "image/*",
            },
            files={"none": ""},
            data={
                "prompt": prompt,
                "negative_prompt": negative,
                "output_format": "jpeg",
                "aspect_ratio": "16:9",
                "model": "sd3.5-medium",
            },
            timeout=60,
        )

        if resp.status_code == 200:
            logger.info("Stability AI: image generated successfully")
            return resp.content
        elif resp.status_code == 402:
            logger.info("Stability AI: credits exhausted")
            return None
        else:
            logger.debug("Stability AI returned %d: %s", resp.status_code, resp.text[:200])
            return None

    except Exception as exc:
        logger.debug("Stability AI error: %s", exc)
        return None


def _generate_huggingface(prompt: str, negative: str, token: str, width: int, height: int,
                          model: str = "") -> bytes | None:
    """Generate an image via HuggingFace Inference API (always-free tier)."""
    import requests

    if not token:
        return None

    if not model:
        model = "stabilityai/stable-diffusion-xl-base-1.0"

    api_url = f"https://api-inference.huggingface.co/models/{model}"

    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative,
                "width": min(width, 1024),
                "height": min(height, 1024),
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
            },
        }

        resp = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=120,  # HuggingFace can be slow on cold start
        )

        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image/"):
            logger.info("HuggingFace (%s): image generated successfully", model.split("/")[-1])
            return resp.content
        elif resp.status_code == 503:
            # Model loading — try once more after delay
            logger.info("HuggingFace: model loading, retrying in 20s...")
            time.sleep(20)
            resp2 = requests.post(api_url, headers={"Authorization": f"Bearer {token}"},
                                  json=payload, timeout=120)
            if resp2.status_code == 200 and resp2.headers.get("content-type", "").startswith("image/"):
                logger.info("HuggingFace (%s): image generated on retry", model.split("/")[-1])
                return resp2.content
            return None
        elif resp.status_code == 429:
            logger.info("HuggingFace: rate limited")
            return None
        else:
            logger.debug("HuggingFace returned %d: %s", resp.status_code, resp.text[:200])
            return None

    except Exception as exc:
        logger.debug("HuggingFace error: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  Cascade Orchestrator
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_image_cascading(
    prompt: str,
    negative: str,
    settings: dict,
    width: int = 800,
    height: int = 450,
) -> tuple[bytes | None, str, str]:
    """
    Try each AI image provider in priority order, skipping exhausted ones.

    Returns:
        (image_bytes, model_name, provider_name) or (None, "", "") if all fail.
    """
    stock_cfg = settings.get("stock_images", {})
    if not stock_cfg.get("enabled", False):
        return None, "", ""

    usage = _load_usage()

    # ── 1. Leonardo AI ────────────────────────────────────────────
    leo_key = stock_cfg.get("leonardo_api_key", "").strip()
    if leo_key and _can_use_provider("leonardo", usage):
        result = _generate_leonardo(prompt, negative, leo_key, width, height)
        if result:
            _record_usage("leonardo", usage)
            return result, "Leonardo Creative", "leonardo"
        logger.debug("Leonardo: generation failed, trying next provider")
    elif leo_key:
        logger.info("Leonardo: daily limit reached (%d/%d), rolling over",
                     usage.get("leonardo", 0), _DAILY_LIMITS["leonardo"])

    # ── 2. Stability AI ──────────────────────────────────────────
    stab_key = stock_cfg.get("stability_api_key", "").strip()
    if stab_key and _can_use_provider("stability", usage):
        result = _generate_stability(prompt, negative, stab_key, width, height)
        if result:
            _record_usage("stability", usage)
            return result, "SD 3.5 Medium", "stability"
        logger.debug("Stability: generation failed, trying next provider")
    elif stab_key:
        logger.info("Stability: daily limit reached (%d/%d), rolling over",
                     usage.get("stability", 0), _DAILY_LIMITS["stability"])

    # ── 3. HuggingFace (always-free fallback) ────────────────────
    hf_token = stock_cfg.get("huggingface_token", "").strip()
    if hf_token and _can_use_provider("huggingface", usage):
        primary_model = stock_cfg.get("primary_model", "stabilityai/stable-diffusion-xl-base-1.0")
        fallback_model = stock_cfg.get("fallback_model", "black-forest-labs/FLUX.1-schnell")

        # Try primary model first
        result = _generate_huggingface(prompt, negative, hf_token, width, height, primary_model)
        if result:
            _record_usage("huggingface", usage)
            return result, primary_model.split("/")[-1], "huggingface"

        # Try fallback model
        result = _generate_huggingface(prompt, negative, hf_token, width, height, fallback_model)
        if result:
            _record_usage("huggingface", usage)
            return result, fallback_model.split("/")[-1], "huggingface"

        logger.debug("HuggingFace: both models failed")
    elif hf_token:
        logger.info("HuggingFace: daily limit reached (%d/%d)",
                     usage.get("huggingface", 0), _DAILY_LIMITS["huggingface"])

    # All providers exhausted or failed — caller falls back to Pexels
    logger.info("All AI image providers exhausted or unavailable — Pexels fallback")
    return None, "", ""


# ═══════════════════════════════════════════════════════════════════════════════
#  Cached Stock Images (pre-generated)
# ═══════════════════════════════════════════════════════════════════════════════

def get_usable_images_for_niche(niche_id: str, limit: int = 5) -> list[dict]:
    """
    Return existing pre-generated AI stock images for a niche.
    Images are stored in data/stock_images/<niche_id>/.

    Returns list of dicts: [{"filepath": Path, "niche": str, "created": str}, ...]
    """
    niche_dir = _STOCK_DIR / niche_id
    if not niche_dir.exists():
        return []

    images = []
    for img_path in sorted(niche_dir.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True):
        images.append({
            "filepath": str(img_path),
            "niche": niche_id,
            "created": datetime.fromtimestamp(img_path.stat().st_mtime, tz=timezone.utc).isoformat(),
        })
        if len(images) >= limit:
            break

    return images


def generate_stock_batch(niche_id: str, settings: dict, count: int = 5) -> list[str]:
    """
    Pre-generate a batch of stock images for a niche.
    Saves to data/stock_images/<niche_id>/ for later use.

    Returns list of saved file paths.
    """
    from PIL import Image as PILImage

    niche_hint = _NICHE_VISUAL_HINTS.get(niche_id, "technology professional")
    niche_dir = _STOCK_DIR / niche_id
    niche_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for i in range(count):
        prompt_data = _build_prompt(f"{niche_hint} stock photo variant {i+1}", niche_id)
        image_bytes, model, provider = _generate_image_cascading(
            prompt_data["positive"], prompt_data["negative"], settings, 1024, 1024,
        )
        if image_bytes is None:
            logger.info("Stock batch: stopped at %d/%d (providers exhausted)", i, count)
            break

        # Save as high-quality JPEG
        try:
            img = PILImage.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")

            filename = f"{niche_id}_{hashlib.md5(image_bytes[:256]).hexdigest()[:8]}.jpg"
            output_path = niche_dir / filename
            img.save(output_path, format="JPEG", quality=92, optimize=True)
            saved.append(str(output_path))
            logger.info("Stock image saved: %s (via %s/%s)", filename, provider, model)
        except Exception as exc:
            logger.warning("Failed to save stock image: %s", exc)

        # Small delay between generations to be nice to APIs
        time.sleep(2)

    logger.info("Stock batch complete: %d/%d images for %s", len(saved), count, niche_id)
    return saved
