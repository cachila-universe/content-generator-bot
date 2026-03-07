"""
Image fetcher — downloads relevant stock photos for video slides.

Priority order:
  1. Local AI-generated stock images (from stock_generator, FREE via HuggingFace)
  2. Pexels API (free tier, 200 req/month)
  3. Graceful fallback to None

• AI images checked first via stock_generator.get_usable_images_for_niche()
• Pexels API: Free key from https://www.pexels.com/api/new/
• Disk cache in data/image_cache/ — never re-downloads the same image
"""

import re
import hashlib
import logging
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(__file__).parent.parent / "data" / "image_cache"

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "as", "are", "was", "were",
    "be", "been", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "your", "our",
    "their", "its", "this", "that", "these", "those", "how", "what",
    "which", "who", "when", "where", "why", "not", "no", "so", "too",
    "very", "just", "also", "more", "most", "much", "many", "only",
    "other", "some", "any", "all", "each", "every", "about", "up",
    "out", "into", "over", "after", "before", "between", "under",
    "again", "here", "there", "then", "than", "now", "you", "know",
    "did", "best", "top", "guide", "ultimate", "complete", "new",
    "review", "number", "tips", "want", "learn", "read", "full",
    "don", "forget", "like", "subscribe", "follow", "more", "get",
    "started", "ready", "article", "video",
}


def extract_search_query(heading: str, niche_name: str = "") -> str:
    """
    Extract meaningful search keywords from a slide heading.

    >>> extract_search_query("Best AI Tools for Productivity in 2026")
    'tools productivity'
    >>> extract_search_query("Follow for more! 🔔", "AI Tools & SaaS")
    'artificial intelligence tools'
    """
    words = re.sub(r"[^a-zA-Z\s]", "", heading).lower().split()
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    query = " ".join(keywords[:4])

    if not query and niche_name:
        query = re.sub(r"[^a-zA-Z\s]", "", niche_name).lower().strip()

    return query or "technology"


def fetch_image(
    query: str,
    api_key: str,
    orientation: str = "landscape",
    target_w: int = 1280,
    target_h: int = 720,
    photo_index: int = 0,
    niche_id: str = "",
    use_ai_images: bool = True,
) -> "Image.Image | None":
    """
    Fetch a relevant image for video slides via Pexels API.

    Returns a PIL Image or None if the fetch fails.
    """
    return _fetch_from_pexels(query, api_key, orientation, target_w, target_h, photo_index)


def _fetch_from_pexels(
    query: str,
    api_key: str,
    orientation: str,
    target_w: int,
    target_h: int,
    photo_index: int,
) -> "Image.Image | None":
    """Fetch an image from Pexels API with disk caching."""
    if not api_key:
        return None

    _CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_key = hashlib.md5(
        f"{query}_{orientation}_{photo_index}".encode()
    ).hexdigest()
    cache_path = _CACHE_DIR / f"{cache_key}.jpg"

    # ── Try cache ─────────────────────────────────────────────────
    if cache_path.exists():
        try:
            img = Image.open(cache_path)
            return _resize_cover(img, target_w, target_h)
        except Exception:
            cache_path.unlink(missing_ok=True)

    # ── Fetch from Pexels ─────────────────────────────────────────
    try:
        import httpx

        resp = httpx.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={
                "query": query,
                "per_page": max(5, photo_index + 1),
                "orientation": orientation,
                "size": "large",
            },
            timeout=15,
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])

        if not photos:
            logger.debug("No Pexels results for '%s'", query)
            return None

        photo = photos[photo_index % len(photos)]

        if orientation == "portrait":
            img_url = photo["src"].get("portrait") or photo["src"]["large"]
        else:
            img_url = photo["src"].get("large2x") or photo["src"]["large"]

        img_resp = httpx.get(img_url, timeout=20, follow_redirects=True)
        img_resp.raise_for_status()

        cache_path.write_bytes(img_resp.content)
        img = Image.open(cache_path)
        return _resize_cover(img, target_w, target_h)

    except Exception as exc:
        logger.warning("Pexels fetch failed for '%s': %s", query, exc)
        return None


def _resize_cover(img: "Image.Image", target_w: int, target_h: int) -> "Image.Image":
    """Resize to cover the target area completely, then center-crop."""
    img = img.convert("RGB")
    w, h = img.size
    scale = max(target_w / w, target_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))
