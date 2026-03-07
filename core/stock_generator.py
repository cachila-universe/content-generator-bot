"""
AI Stock Image Generator — Multi-API cascading image generation with trend intelligence.

API Priority (all free, no credit card required):
  1. Leonardo AI     — 150 free tokens/day (highest quality)
  2. Stability AI    — 25 free credits on signup (SD 3.5)
  3. HuggingFace     — ~30 images/day free (SDXL / FLUX.1-schnell)

Pipeline:
  1. Trend intelligence feeds trending topics + market demand
  2. Build optimised prompts from niche + style + quality
  3. Cascade through APIs: Leonardo → Stability → HuggingFace
  4. Post-process (resize, JPEG, EXIF-ready)
  5. Track in DB with mandatory AI disclosure metadata
  6. Images used in videos and submitted to stock platforms

Mandatory AI disclosure is embedded in every image and metadata record.
"""

import io
import re
import json
import time
import uuid
import logging
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_OUTPUT_DIR = _PROJECT_ROOT / "data" / "stock_images"
_DB_PATH = _PROJECT_ROOT / "data" / "bot.db"

# ── API Priority ──────────────────────────────────────────────────────────
API_PROVIDERS = ["leonardo", "stability", "huggingface"]

# ── AI disclosure (MANDATORY — never disable) ────────────────────────────
AI_DISCLOSURE = {
    "notice": "This image was created using generative artificial intelligence.",
    "mandatory_keywords": [
        "ai generated",
        "artificial intelligence",
        "ai art",
        "generative ai",
    ],
}

# ── Niche-specific prompt templates ───────────────────────────────────────
NICHE_TEMPLATES = {
    "ai_tools": [
        "futuristic {topic} technology workspace, glowing holographic displays, "
        "dark background, blue neon accents, photorealistic, 4K",
        "person using {topic} on modern laptop, clean minimal office, "
        "natural light, shallow depth of field, commercial stock photo",
        "{topic} digital concept, abstract flowing data visualization, "
        "vibrant blue and purple gradients, professional stock imagery",
    ],
    "personal_finance": [
        "{topic} financial planning scene, modern office desk with calculator "
        "and charts, warm lighting, professional photography",
        "diverse professionals discussing {topic}, contemporary conference room, "
        "clean background, corporate aesthetic, stock photo quality",
        "{topic} investment concept, rising bar chart with golden coins, "
        "clean white background, 3D render, high detail",
    ],
    "health_biohacking": [
        "serene {topic} wellness scene, soft natural light, green plants, "
        "calm atmosphere, mindfulness aesthetic, stock photo",
        "scientist researching {topic}, modern laboratory, clean environment, "
        "blue and white tones, professional medical photography",
        "{topic} healthy lifestyle, person meditating outdoors, golden hour, "
        "peaceful setting, high-quality stock imagery",
    ],
    "home_tech": [
        "smart home {topic} technology, modern interior design, "
        "ambient lighting, IoT devices, photorealistic, commercial quality",
        "person controlling {topic} with smartphone, contemporary living room, "
        "warm tones, lifestyle photography, stock photo",
        "{topic} home automation concept, futuristic interface, "
        "clean minimalist design, blue accents, 4K render",
    ],
    "travel": [
        "breathtaking {topic} travel destination, aerial photography, "
        "vibrant colors, golden hour, National Geographic style",
        "adventurous traveler exploring {topic}, backpack, scenic landscape, "
        "dramatic clouds, professional travel photography",
        "{topic} iconic travel scene, crystal clear water, lush greenery, "
        "paradise aesthetic, high-resolution stock photo",
    ],
    "pet_care": [
        "adorable {topic} pet portrait, studio lighting, soft background, "
        "sharp focus on eyes, professional animal photography",
        "happy pet owner with {topic}, outdoor park setting, natural light, "
        "joyful expression, lifestyle stock photo",
        "{topic} veterinary care scene, modern clinic, clean environment, "
        "caring professional, commercial quality photography",
    ],
    "fitness_wellness": [
        "energetic {topic} fitness photo, dynamic movement, athletic wear, "
        "modern gym setting, dramatic lighting, stock photography",
        "person practicing {topic} outdoors, sunrise backdrop, "
        "motivational composition, action shot, professional quality",
        "{topic} healthy living concept, fresh fruits and workout equipment, "
        "flat lay, bright colors, clean commercial aesthetic",
    ],
    "remote_work": [
        "productive {topic} home office, modern desk setup, dual monitors, "
        "natural light from window, cozy aesthetic, stock photo",
        "diverse team in {topic} video call, laptop screen, "
        "contemporary workspace, professional commercial photography",
        "{topic} digital nomad lifestyle, person working from cafe, "
        "laptop and coffee, warm tones, lifestyle stock imagery",
    ],
}

_GENERIC_TEMPLATES = [
    "high quality stock photo of {topic}, professional photography, "
    "clean composition, natural lighting, 4K resolution",
    "{topic} concept image, commercial use, neutral background, "
    "sharp focus, highly detailed, professional stock photo",
]

STYLES = [
    "photorealistic, DSLR photograph, natural lighting",
    "digital art, vibrant colors, clean modern aesthetic",
    "minimalist design, negative space, clean composition",
    "cinematic photography, dramatic lighting, film grain",
    "editorial photography, magazine quality, high fashion",
]

QUALITY_SUFFIX = (
    ", 4K resolution, highly detailed, sharp focus, professional stock photo, "
    "commercial photography, high production value"
)

NEGATIVE_PROMPT = (
    "blurry, low quality, watermark, text, deformed, ugly, disfigured, "
    "nsfw, nudity, violence, gore, disturbing, offensive, logo, brand name, "
    "cartoon, anime, sketch, draft, noise, artifacts, cropped, out of frame"
)


# ═══════════════════════════════════════════════════════════════════════════
#  DB helpers
# ═══════════════════════════════════════════════════════════════════════════

def _ensure_stock_table():
    """Create the stock_images table if it doesn't exist."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            prompt TEXT,
            topic TEXT,
            niche_id TEXT,
            category TEXT,
            style TEXT,
            resolution TEXT DEFAULT '1024x1024',
            ai_model TEXT,
            api_provider TEXT DEFAULT 'huggingface',
            ai_disclosed BOOLEAN DEFAULT 1,
            ai_disclosure_text TEXT,
            title TEXT,
            description TEXT,
            keywords TEXT,
            file_size_bytes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'generated',
            platform_submissions TEXT DEFAULT '',
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_in_video BOOLEAN DEFAULT 0,
            trend_source TEXT DEFAULT '',
            market_demand_score REAL DEFAULT 0.0
        )
    """)
    # Add columns if they don't exist (for upgrades from old schema)
    for col, typedef in [
        ("api_provider", "TEXT DEFAULT 'huggingface'"),
        ("trend_source", "TEXT DEFAULT ''"),
        ("market_demand_score", "REAL DEFAULT 0.0"),
    ]:
        try:
            conn.execute(f"ALTER TABLE stock_images ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass  # Column already exists
    conn.commit()
    conn.close()


def _ensure_api_usage_table():
    """Track API usage per provider for dashboard display."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            action TEXT DEFAULT 'image_generate',
            credits_used REAL DEFAULT 0,
            success BOOLEAN DEFAULT 1,
            error_message TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _log_api_usage(provider: str, success: bool, credits: float = 0, error: str = ""):
    """Record an API call for dashboard tracking."""
    _ensure_api_usage_table()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        "INSERT INTO api_usage (provider, credits_used, success, error_message) VALUES (?, ?, ?, ?)",
        (provider, credits, 1 if success else 0, error),
    )
    conn.commit()
    conn.close()


def _insert_stock_image(record: dict) -> int:
    """Insert a stock image record and return its row ID."""
    conn = sqlite3.connect(str(_DB_PATH))
    cur = conn.execute("""
        INSERT INTO stock_images
            (filename, filepath, prompt, topic, niche_id, category, style,
             resolution, ai_model, api_provider, ai_disclosed, ai_disclosure_text,
             title, description, keywords, file_size_bytes, status,
             trend_source, market_demand_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, 'generated', ?, ?)
    """, (
        record["filename"],
        record["filepath"],
        record.get("prompt", ""),
        record.get("topic", ""),
        record.get("niche_id", ""),
        record.get("category", ""),
        record.get("style", ""),
        record.get("resolution", "1024x1024"),
        record.get("ai_model", ""),
        record.get("api_provider", "huggingface"),
        AI_DISCLOSURE["notice"],
        record.get("title", ""),
        record.get("description", ""),
        record.get("keywords", ""),
        record.get("file_size_bytes", 0),
        record.get("trend_source", ""),
        record.get("market_demand_score", 0.0),
    ))
    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    return row_id


# ═══════════════════════════════════════════════════════════════════════════
#  Public query functions (dashboard + video integration)
# ═══════════════════════════════════════════════════════════════════════════

def get_all_stock_images() -> list:
    """Fetch all stock images for the dashboard."""
    _ensure_stock_table()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM stock_images ORDER BY generated_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stock_stats() -> dict:
    """Return summary stats for the dashboard."""
    _ensure_stock_table()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'generated' THEN 1 ELSE 0 END) as generated,
            SUM(CASE WHEN status = 'submitted' THEN 1 ELSE 0 END) as submitted,
            SUM(CASE WHEN used_in_video = 1 THEN 1 ELSE 0 END) as used_in_video,
            SUM(file_size_bytes) as total_bytes
        FROM stock_images
    """).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_api_usage_stats() -> dict:
    """Return per-provider API usage stats for the dashboard."""
    _ensure_api_usage_table()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT
            provider,
            COUNT(*) as total_calls,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
            SUM(credits_used) as total_credits,
            MAX(timestamp) as last_used
        FROM api_usage
        GROUP BY provider
        ORDER BY total_calls DESC
    """).fetchall()
    conn.close()
    return {r["provider"]: dict(r) for r in rows}


def get_usable_images_for_niche(niche_id: str, limit: int = 10) -> list:
    """Get AI-generated images for a niche to use in videos."""
    _ensure_stock_table()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT * FROM stock_images
        WHERE niche_id = ? AND status = 'generated'
        ORDER BY generated_at DESC
        LIMIT ?
    """, (niche_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_used_in_video(image_id: int):
    """Mark a stock image as used in a video."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        "UPDATE stock_images SET used_in_video = 1 WHERE id = ?", (image_id,)
    )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════
#  API 1: Leonardo AI (highest quality, 150 free tokens/day)
# ═══════════════════════════════════════════════════════════════════════════

def _call_leonardo(
    prompt: str,
    negative_prompt: str,
    api_key: str,
    width: int = 1024,
    height: int = 1024,
) -> Optional[bytes]:
    """
    Generate an image via Leonardo AI API.

    Free tier: 150 tokens/day (1 image ~ 4-8 tokens depending on model).
    No credit card required.

    Setup:
      1. Sign up at https://app.leonardo.ai
      2. Go to https://app.leonardo.ai/api → Create API key
      3. Add to settings.yaml → stock_images.leonardo_api_key
    """
    try:
        import httpx
    except ImportError:
        logger.error("httpx not installed — run: pip install httpx")
        return None

    if not api_key:
        logger.debug("Leonardo AI: no API key configured")
        return None

    base_url = "https://cloud.leonardo.ai/api/rest/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        # Step 1: Create generation
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "modelId": "e71a1c2f-4f80-4800-934f-2c68979d8cc8",  # Leonardo Phoenix
            "width": min(width, 1024),
            "height": min(height, 1024),
            "num_images": 1,
            "alchemy": False,
            "photoReal": False,
            "promptMagic": False,
        }

        resp = httpx.post(
            f"{base_url}/generations",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp.status_code == 402:
            logger.info("Leonardo AI: out of free tokens for today")
            _log_api_usage("leonardo", False, error="out of tokens")
            return None

        if resp.status_code != 200:
            logger.warning("Leonardo API error %d: %s", resp.status_code, resp.text[:200])
            _log_api_usage("leonardo", False, error=f"HTTP {resp.status_code}")
            return None

        gen_id = resp.json().get("sdGenerationJob", {}).get("generationId")
        if not gen_id:
            logger.warning("Leonardo: no generation ID returned")
            _log_api_usage("leonardo", False, error="no generation ID")
            return None

        # Step 2: Poll for completion
        for _ in range(30):  # Max ~5 minutes
            time.sleep(10)
            status_resp = httpx.get(
                f"{base_url}/generations/{gen_id}",
                headers=headers,
                timeout=30,
            )
            if status_resp.status_code != 200:
                continue

            gen_data = status_resp.json().get("generations_by_pk", {})
            status = gen_data.get("status")

            if status == "COMPLETE":
                images = gen_data.get("generated_images", [])
                if images:
                    img_url = images[0].get("url")
                    if img_url:
                        img_resp = httpx.get(img_url, timeout=30, follow_redirects=True)
                        if img_resp.status_code == 200:
                            _log_api_usage("leonardo", True, credits=5)
                            logger.info("Leonardo AI: image generated successfully")
                            return img_resp.content
                break

            if status == "FAILED":
                logger.warning("Leonardo generation failed")
                _log_api_usage("leonardo", False, error="generation failed")
                return None

        logger.warning("Leonardo: generation timed out")
        _log_api_usage("leonardo", False, error="timeout")
        return None

    except Exception as exc:
        logger.warning("Leonardo AI error: %s", exc)
        _log_api_usage("leonardo", False, error=str(exc))
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  API 2: Stability AI (25 free credits, high quality SD 3.5)
# ═══════════════════════════════════════════════════════════════════════════

def _call_stability(
    prompt: str,
    negative_prompt: str,
    api_key: str,
    width: int = 1024,
    height: int = 1024,
) -> Optional[bytes]:
    """
    Generate an image via Stability AI API.

    Free tier: 25 credits on signup (1 image ~ 3-6.5 credits).
    No credit card required.

    Setup:
      1. Sign up at https://platform.stability.ai
      2. Go to Account → API Keys → Create key
      3. Add to settings.yaml → stock_images.stability_api_key
    """
    try:
        import httpx
    except ImportError:
        return None

    if not api_key:
        logger.debug("Stability AI: no API key configured")
        return None

    try:
        resp = httpx.post(
            "https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "image/*",
            },
            data={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "model": "sd3.5-medium",
                "output_format": "jpeg",
                "aspect_ratio": "1:1",
            },
            timeout=120,
        )

        if resp.status_code == 402:
            logger.info("Stability AI: out of free credits")
            _log_api_usage("stability", False, error="out of credits")
            return None

        if resp.status_code == 403:
            logger.info("Stability AI: content moderation rejection")
            _log_api_usage("stability", False, error="content filtered")
            return None

        if resp.status_code != 200:
            logger.warning("Stability API error %d: %s", resp.status_code, resp.text[:200])
            _log_api_usage("stability", False, error=f"HTTP {resp.status_code}")
            return None

        _log_api_usage("stability", True, credits=3.5)
        logger.info("Stability AI: image generated successfully")
        return resp.content

    except Exception as exc:
        logger.warning("Stability AI error: %s", exc)
        _log_api_usage("stability", False, error=str(exc))
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  API 3: HuggingFace (free fallback, ~30 images/day)
# ═══════════════════════════════════════════════════════════════════════════

def _call_huggingface(
    prompt: str,
    negative_prompt: str,
    model: str,
    token: str,
    width: int = 1024,
    height: int = 1024,
    max_retries: int = 3,
) -> Optional[bytes]:
    """Call HuggingFace Inference API (FREE) to generate an image."""
    try:
        import httpx
    except ImportError:
        logger.error("httpx not installed — run: pip install httpx")
        return None

    if not token:
        logger.debug("HuggingFace: no token configured")
        return None

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        },
    }

    for attempt in range(max_retries):
        try:
            resp = httpx.post(url, headers=headers, json=payload, timeout=180)

            if resp.status_code == 200:
                _log_api_usage("huggingface", True)
                return resp.content

            if resp.status_code in (503, 429):
                wait = (5.0 if resp.status_code == 429 else 2.0) * (2 ** attempt)
                logger.info("HF %d — waiting %.0fs (attempt %d/%d)", resp.status_code, wait, attempt + 1, max_retries)
                time.sleep(wait)
                continue

            logger.error("HF API error %d: %s", resp.status_code, resp.text[:200])
            _log_api_usage("huggingface", False, error=f"HTTP {resp.status_code}")
            return None

        except Exception as exc:
            wait = 3.0 * (2 ** attempt)
            logger.warning("HF request error (attempt %d): %s", attempt + 1, exc)
            time.sleep(wait)

    _log_api_usage("huggingface", False, error="all retries failed")
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  Cascading image generation — try APIs in priority order
# ═══════════════════════════════════════════════════════════════════════════

def _generate_image_cascading(
    prompt: str,
    negative_prompt: str,
    settings: dict,
    width: int = 1024,
    height: int = 1024,
) -> tuple[Optional[bytes], str, str]:
    """
    Try image generation APIs in priority order:
      1. Leonardo AI (best quality)
      2. Stability AI (great quality)
      3. HuggingFace SDXL (good quality, always free)
      4. HuggingFace FLUX.1-schnell (fast fallback)

    Returns: (image_bytes, model_name, api_provider) or (None, "", "")
    """
    stock_cfg = settings.get("stock_images", {})

    # 1. Leonardo AI
    leo_key = stock_cfg.get("leonardo_api_key", "").strip()
    if leo_key:
        logger.info("  Trying Leonardo AI...")
        result = _call_leonardo(prompt, negative_prompt, leo_key, width, height)
        if result:
            return result, "Leonardo Phoenix", "leonardo"

    # 2. Stability AI
    stab_key = stock_cfg.get("stability_api_key", "").strip()
    if stab_key:
        logger.info("  Trying Stability AI...")
        result = _call_stability(prompt, negative_prompt, stab_key, width, height)
        if result:
            return result, "SD 3.5 Medium", "stability"

    # 3. HuggingFace (primary model)
    hf_token = stock_cfg.get("huggingface_token", "").strip()
    primary_model = stock_cfg.get("primary_model", "stabilityai/stable-diffusion-xl-base-1.0")
    if hf_token:
        logger.info("  Trying HuggingFace (%s)...", primary_model.split("/")[-1])
        result = _call_huggingface(prompt, negative_prompt, primary_model, hf_token, width, height)
        if result:
            return result, primary_model, "huggingface"

        # 4. HuggingFace fallback model
        fallback_model = stock_cfg.get("fallback_model", "black-forest-labs/FLUX.1-schnell")
        logger.info("  Trying HuggingFace fallback (%s)...", fallback_model.split("/")[-1])
        result = _call_huggingface(prompt, negative_prompt, fallback_model, hf_token, width, height)
        if result:
            return result, fallback_model, "huggingface"

    logger.error("All image APIs exhausted — no image generated")
    return None, "", ""


# ═══════════════════════════════════════════════════════════════════════════
#  Image processing
# ═══════════════════════════════════════════════════════════════════════════

def _process_image(
    image_bytes: bytes,
    output_path: Path,
    target_w: int = 1024,
    target_h: int = 1024,
    jpeg_quality: int = 95,
) -> Optional[Path]:
    """Validate, resize, and save generated image as high-quality JPEG."""
    from PIL import Image

    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        w, h = img.size
        if w < 256 or h < 256:
            logger.warning("Generated image too small (%dx%d), skipping", w, h)
            return None

        if (w, h) != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.LANCZOS)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, format="JPEG", quality=jpeg_quality, optimize=True)
        return output_path

    except Exception as exc:
        logger.error("Image processing failed: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  Prompt Builder
# ═══════════════════════════════════════════════════════════════════════════

def _build_prompt(topic: str, niche_id: str = "", style: str = "") -> dict:
    """Build a detailed image generation prompt for a topic."""
    import random

    templates = NICHE_TEMPLATES.get(niche_id, _GENERIC_TEMPLATES)
    template = random.choice(templates)
    base = template.format(topic=topic)

    if not style:
        style = random.choice(STYLES)

    positive = f"{base}, {style}{QUALITY_SUFFIX}"

    return {
        "positive": positive,
        "negative": NEGATIVE_PROMPT,
        "topic": topic,
        "category": niche_id or "general",
        "style": style.split(",")[0].strip(),
    }


def _generate_metadata(topic: str, niche_id: str, style: str) -> dict:
    """Generate title, description, and keywords for a stock image."""
    topic_words = re.sub(r"[^a-zA-Z\s]", "", topic).lower().split()
    keywords = list(dict.fromkeys(
        AI_DISCLOSURE["mandatory_keywords"]
        + topic_words
        + [niche_id.replace("_", " ")]
        + ["stock photo", "commercial", "high resolution", "professional"]
    ))

    title = f"{topic.title()} - AI Generated {style.title()} Stock Image"
    description = (
        f"{AI_DISCLOSURE['notice']} "
        f"High-quality {style} image of {topic.lower()}. "
        f"Professional stock photography suitable for commercial use. "
        f"Category: {niche_id.replace('_', ' ').title()}."
    )

    return {
        "title": title[:200],
        "description": description[:500],
        "keywords": ", ".join(keywords[:50]),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  Main generation pipeline
# ═══════════════════════════════════════════════════════════════════════════

def generate_stock_images(
    topics: list[dict],
    settings: dict,
    count: int = 5,
) -> list[dict]:
    """
    Generate AI stock images using cascading APIs.

    Priority: Leonardo AI → Stability AI → HuggingFace (SDXL → FLUX)

    Args:
        topics: List of dicts with 'topic', 'niche_id', optional 'trend_source',
                'market_demand_score' keys.
        settings: Full settings.yaml dict.
        count: Number of images to generate (default 5).

    Returns:
        List of generated image metadata dicts.
    """
    import random

    _ensure_stock_table()
    _ensure_api_usage_table()

    stock_cfg = settings.get("stock_images", {})
    resolution = stock_cfg.get("resolution", "1024x1024")

    # Check at least one API is configured
    has_api = any([
        stock_cfg.get("leonardo_api_key", "").strip(),
        stock_cfg.get("stability_api_key", "").strip(),
        stock_cfg.get("huggingface_token", "").strip(),
    ])
    if not has_api:
        logger.error(
            "No image generation API keys configured. Add at least one:\n"
            "  - Leonardo AI (best): stock_images.leonardo_api_key\n"
            "  - Stability AI: stock_images.stability_api_key\n"
            "  - HuggingFace (free): stock_images.huggingface_token\n"
            "See SETUP_MANUAL.md for instructions."
        )
        return []

    try:
        w, h = resolution.lower().split("x")
        target_w, target_h = int(w), int(h)
    except (ValueError, AttributeError):
        target_w, target_h = 1024, 1024

    results = []

    for i in range(min(count, len(topics) if topics else count)):
        topic_data = topics[i % len(topics)] if topics else {"topic": "technology", "niche_id": "ai_tools"}
        topic = topic_data.get("topic", "technology")
        niche_id = topic_data.get("niche_id", "general")
        trend_source = topic_data.get("trend_source", "")
        demand_score = topic_data.get("market_demand_score", 0.0)
        style = random.choice(STYLES)

        logger.info("Generating stock image %d/%d: '%s' (%s)", i + 1, count, topic[:50], niche_id)

        prompt = _build_prompt(topic, niche_id, style)

        # Cascade through APIs
        image_bytes, model_name, provider = _generate_image_cascading(
            prompt["positive"], prompt["negative"], settings, target_w, target_h,
        )

        if image_bytes is None:
            logger.error("All APIs failed for '%s' — skipping", topic)
            continue

        # Save
        filename = f"{uuid.uuid4().hex}.jpg"
        date_str = datetime.utcnow().strftime("%Y/%m/%d")
        output_dir = _OUTPUT_DIR / date_str / niche_id
        output_path = output_dir / filename

        saved = _process_image(image_bytes, output_path, target_w, target_h)
        if saved is None:
            continue

        file_size = output_path.stat().st_size
        metadata = _generate_metadata(topic, niche_id, prompt["style"])

        record = {
            "filename": filename,
            "filepath": str(output_path),
            "prompt": prompt["positive"],
            "topic": topic,
            "niche_id": niche_id,
            "category": niche_id,
            "style": prompt["style"],
            "resolution": resolution,
            "ai_model": model_name,
            "api_provider": provider,
            "file_size_bytes": file_size,
            "trend_source": trend_source,
            "market_demand_score": demand_score,
            **metadata,
        }

        row_id = _insert_stock_image(record)
        record["id"] = row_id
        results.append(record)

        logger.info(
            "  ✓ Image %d saved: %s (%d KB, %s via %s)",
            row_id, filename, file_size // 1024, model_name.split("/")[-1], provider,
        )

    logger.info("Stock image generation complete: %d/%d images generated", len(results), count)
    return results


def generate_for_article(article: dict, settings: dict, count: int = 3) -> list[dict]:
    """Generate stock images relevant to a specific article."""
    from bs4 import BeautifulSoup

    html = article.get("html_content", "")
    niche_id = article.get("niche_id", "general")
    title = article.get("title", "")

    topics = []
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for h2 in soup.find_all("h2"):
            text = h2.get_text(strip=True)
            if text and not any(skip in text.lower() for skip in ["faq", "conclusion", "final"]):
                topics.append({"topic": text, "niche_id": niche_id})

    if not topics:
        topics.append({"topic": title, "niche_id": niche_id})

    return generate_stock_images(topics, settings, count=count)
