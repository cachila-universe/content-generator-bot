"""SEO optimizer that adds meta tags, schema markup, sitemaps, and canonical URLs.

Image priority: AI-generated (Leonardo → Stability → HuggingFace) → Pexels → Picsum fallback.
"""

import re
import os
import io
import json
import uuid
import hashlib
import logging
import requests
from pathlib import Path
from slugify import slugify
from datetime import datetime, timezone
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_STOCK_DIR = _PROJECT_ROOT / "data" / "stock_images"
_ARTICLE_IMG_DIR = _PROJECT_ROOT / "site" / "output" / "assets" / "images"


def optimize(article: dict, niche_id: str, niche_config: dict, site_url: str, output_dir: Path) -> dict:
    """
    Add SEO metadata, schema markup, sitemap entry, and canonical URL to article.
    Generates AI hero + inline images (Leonardo → Stability → HuggingFace → Pexels → Picsum).

    Returns enriched article dict with: slug, meta_html, schema_markup, canonical_url
    """
    title = article.get("title", "Untitled")
    meta_description = article.get("meta_description", "")
    tags = article.get("tags", [])
    html_content = article.get("html_content", "")
    published_at = datetime.now(timezone.utc).isoformat()

    # Generate URL slug
    slug = slugify(title, max_length=80, word_boundary=True, save_order=True)
    subtopic_id = article.get("subtopic_id", "")
    canonical_url = f"{site_url.rstrip('/')}/{niche_id}/{slug}.html"

    # ── Hero image: AI-generated primary, Pexels fallback, Picsum last resort ──
    image_url = _generate_hero_image(title, niche_id, slug, site_url)

    # Build meta HTML block
    site_name = os.getenv("SITE_NAME", "TechLife Insights")
    meta_html = _build_meta_html(title, meta_description, canonical_url, site_name, tags, image_url)

    # Build JSON-LD Article schema
    article_schema = _build_article_schema(title, meta_description, canonical_url, site_name, published_at)

    # Build JSON-LD FAQ schema
    faq_schema = _build_faq_schema(html_content)

    schema_markup = article_schema
    if faq_schema:
        schema_markup += "\n" + faq_schema

    # Inject inline images after every H2 heading (AI-generated when possible)
    enriched_content = _inject_inline_images(html_content, slug, niche_id, site_url)

    # Update sitemap
    _update_sitemap(output_dir, canonical_url, published_at)

    # Ping Google sitemap (best-effort)
    if os.getenv("SITEMAP_PING_ENABLED", "true").lower() == "true":
        _ping_sitemap(site_url, output_dir)

    return {
        **article,
        "html_content": enriched_content,
        "slug": slug,
        "subtopic_id": subtopic_id,
        "meta_html": meta_html,
        "schema_markup": schema_markup,
        "canonical_url": canonical_url,
        "published_at": published_at,
        "image_url": image_url,
    }


# ═══════════════════════════════════════════════════════════════════════════
#  AI Image Generation for Articles
# ═══════════════════════════════════════════════════════════════════════════

def _generate_hero_image(title: str, niche_id: str, slug: str, site_url: str) -> str:
    """
    Generate a hero image for the article using AI image APIs.
    Falls back through: AI stock images → Pexels → Picsum.
    Returns a URL string.
    """
    # 1. Try to find existing AI stock image for this topic
    try:
        from core.stock_generator import get_usable_images_for_niche
        ai_images = get_usable_images_for_niche(niche_id, limit=5)
        if ai_images:
            # Pick the best match (first available)
            img = ai_images[0]
            filepath = Path(img.get("filepath", ""))
            if filepath.exists():
                # Copy to article assets
                dest = _copy_to_article_assets(filepath, slug, "hero")
                if dest:
                    return f"/assets/images/{dest.name}"
    except Exception as exc:
        logger.debug("AI stock image lookup failed: %s", exc)

    # 2. Try generating a new AI image on-the-fly
    try:
        ai_url = _generate_ai_image_for_article(title, niche_id, slug, "hero")
        if ai_url:
            return ai_url
    except Exception as exc:
        logger.debug("AI image generation failed: %s", exc)

    # 3. Try Pexels
    try:
        pexels_url = _fetch_pexels_image(title, niche_id)
        if pexels_url:
            return pexels_url
    except Exception as exc:
        logger.debug("Pexels fetch failed: %s", exc)

    # 4. Last resort: Picsum (deterministic, always works)
    logger.info("Using Picsum fallback for hero image: %s", slug)
    return f"https://picsum.photos/seed/{slug}/800/450"


def _generate_ai_image_for_article(title: str, niche_id: str, slug: str, img_type: str) -> str | None:
    """
    Generate a single AI image for an article section using the stock_generator cascade.
    Returns local URL path or None.
    """
    import yaml

    try:
        settings_path = _PROJECT_ROOT / "config" / "settings.yaml"
        with open(settings_path) as f:
            settings = yaml.safe_load(f) or {}
    except Exception:
        return None

    stock_cfg = settings.get("stock_images", {})
    has_api = any([
        stock_cfg.get("leonardo_api_key", "").strip(),
        stock_cfg.get("stability_api_key", "").strip(),
        stock_cfg.get("huggingface_token", "").strip(),
    ])
    if not has_api:
        return None

    try:
        from core.stock_generator import _generate_image_cascading, _build_prompt

        prompt = _build_prompt(title, niche_id)
        image_bytes, model_name, provider = _generate_image_cascading(
            prompt["positive"], prompt["negative"], settings, 800, 450,
        )
        if image_bytes is None:
            return None

        # Save to article assets
        _ARTICLE_IMG_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{slug}-{img_type}-{uuid.uuid4().hex[:6]}.jpg"
        output_path = _ARTICLE_IMG_DIR / filename

        from PIL import Image as PILImage
        img = PILImage.open(io.BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = img.resize((800, 450), PILImage.LANCZOS)
        img.save(output_path, format="JPEG", quality=90, optimize=True)

        logger.info("AI hero image generated: %s (%s via %s)", filename, model_name, provider)
        return f"/assets/images/{filename}"

    except Exception as exc:
        logger.debug("AI image cascade failed for article: %s", exc)
        return None


def _fetch_pexels_image(query: str, niche_id: str) -> str | None:
    """Fetch a relevant image URL from Pexels API."""
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        return None

    # Clean query for search
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', query)
    words = [w for w in clean.split() if len(w) > 2][:4]
    search_query = " ".join(words) if words else niche_id.replace("_", " ")

    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": search_query, "per_page": 3, "orientation": "landscape"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            photos = data.get("photos", [])
            if photos:
                # Return the large2x version (high quality, landscape)
                return photos[0].get("src", {}).get("large2x", photos[0].get("src", {}).get("large", ""))
    except Exception as exc:
        logger.debug("Pexels API error: %s", exc)

    return None


def _copy_to_article_assets(source: Path, slug: str, img_type: str) -> Path | None:
    """Copy an existing stock image to the article assets directory."""
    try:
        from PIL import Image as PILImage
        _ARTICLE_IMG_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{slug}-{img_type}-{uuid.uuid4().hex[:6]}.jpg"
        dest = _ARTICLE_IMG_DIR / filename

        img = PILImage.open(source)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = img.resize((800, 450), PILImage.LANCZOS)
        img.save(dest, format="JPEG", quality=90, optimize=True)
        return dest
    except Exception as exc:
        logger.debug("Image copy failed: %s", exc)
        return None


def _inject_inline_images(html_content: str, base_slug: str, niche_id: str = "", site_url: str = "") -> str:
    """
    Inject topic-relevant images throughout the article dynamically.
    Priority: AI-generated → Pexels → Picsum fallback.
    Number of images varies per article — typically 2-5 depending on section count.
    Skips FAQ, Conclusion, and headings that are purely affiliate links.
    """

    # Words that add no keyword value
    _STOP_WORDS = {
        'best', 'top', 'most', 'the', 'a', 'an', 'and', 'or', 'for', 'in', 'to',
        'of', 'how', 'why', 'what', 'when', 'where', 'your', 'our', 'my', 'get',
        'all', 'new', 'free', 'great', 'good', 'about', 'with', 'from', 'this',
        'that', 'are', 'is', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'must', 'can', 'up', 'out', 'on', 'at', 'by', 'as', 'its', 'it', 'we',
        'you', 'they', 'he', 'she', 'ultimate', 'guide', 'complete', 'right',
        'choosing', 'tips', 'tricks', 'review', 'reviews', 'buying', 'finding',
        'using', 'making', 'getting', 'having', 'setting', 'understanding',
    }

    _NICHE_FALLBACK = {
        'ai_tools': 'technology,software',
        'personal_finance': 'finance,money',
        'health_biohacking': 'health,wellness',
        'home_tech': 'smart,home',
        'travel': 'travel,destination',
        'pet_care': 'pets,animals',
        'fitness_wellness': 'fitness,exercise',
        'remote_work': 'office,laptop',
    }

    # Count content H2s (excluding FAQ/Conclusion)
    all_h2s = re.findall(r"<h2>(.*?)</h2>", html_content, flags=re.IGNORECASE | re.DOTALL)
    content_h2s = []
    for h2_html in all_h2s:
        plain = re.sub(r'<[^>]+>', '', h2_html).strip().lower()
        if not any(w in plain for w in ("faq", "frequently", "question", "conclusion")):
            content_h2s.append(plain)

    total_sections = len(content_h2s)

    # Decide which sections get images
    if total_sections <= 2:
        image_positions = set(range(1, total_sections + 1))
    elif total_sections <= 4:
        image_positions = {1, total_sections}
        if total_sections >= 3:
            image_positions.add(total_sections // 2 + 1)
    else:
        image_positions = {1, total_sections}
        step = max(1, total_sections // 3)
        for i in range(step, total_sections, step):
            image_positions.add(i)
        if len(image_positions) > 5:
            image_positions = set(sorted(image_positions)[:5])

    used_seeds = set()
    img_counter = [0]

    def _keywords_from_heading(raw_html: str) -> str:
        clean = re.sub(r'<[^>]+>', '', raw_html)
        clean = re.sub(r'[^a-zA-Z0-9 ]', ' ', clean)
        words = [w.lower() for w in clean.split() if len(w) > 2 and w.lower() not in _STOP_WORDS]
        keywords = words[:3]
        if not keywords:
            keywords = _NICHE_FALLBACK.get(niche_id, 'lifestyle,guide').split(',')
        return ','.join(keywords)

    def _unique_seed(keywords: str) -> str:
        raw = f"{base_slug}-{keywords}-{img_counter[0]}"
        seed = hashlib.md5(raw.encode()).hexdigest()[:8]
        while seed in used_seeds:
            seed = hashlib.md5(f"{seed}x".encode()).hexdigest()[:8]
        used_seeds.add(seed)
        return seed

    def _replace_h2(match: re.Match) -> str:
        heading_html = match.group(1)
        plain_heading = re.sub(r'<[^>]+>', '', heading_html).strip()

        lower = plain_heading.lower()
        if any(word in lower for word in ("faq", "frequently", "question", "conclusion")):
            return match.group(0)

        img_counter[0] += 1

        if img_counter[0] not in image_positions:
            return match.group(0)

        keywords = _keywords_from_heading(heading_html)
        seed = _unique_seed(keywords)
        alt_text = plain_heading[:80] if plain_heading else keywords.replace(',', ' ')

        # Try AI image generation for inline image
        img_src = None

        # Try Pexels first for inline (faster, saves AI credits for hero)
        try:
            pexels_url = _fetch_pexels_image(plain_heading, niche_id)
            if pexels_url:
                img_src = pexels_url
        except Exception:
            pass

        # Fallback to Picsum
        if not img_src:
            img_src = f"https://picsum.photos/seed/{seed}/800/400"

        img_html = (
            f'\n<figure style="margin:24px 0;text-align:center;">'
            f'<img src="{img_src}" '
            f'alt="{alt_text}" '
            f'style="width:100%;max-width:800px;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.10);" '
            f'loading="lazy" width="800" height="400">'
            f'</figure>'
        )
        return match.group(0) + img_html

    enriched = re.sub(r"<h2>(.*?)</h2>", _replace_h2, html_content, flags=re.IGNORECASE | re.DOTALL)
    return enriched


def _build_meta_html(title: str, description: str, canonical_url: str, site_name: str, tags: list, image_url: str = "") -> str:
    """Build HTML meta tags block."""
    keywords = ", ".join(tags)
    img_tags = f'\n<meta property="og:image" content="{image_url}">\n<meta name="twitter:image" content="{image_url}">' if image_url else ""
    return f"""<title>{title} | {site_name}</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{canonical_url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{site_name}">{img_tags}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">"""


def _build_article_schema(
    title: str, description: str, url: str, site_name: str, published_at: str
) -> str:
    """Build JSON-LD Article schema markup."""
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "url": url,
        "datePublished": published_at,
        "dateModified": published_at,
        "publisher": {
            "@type": "Organization",
            "name": site_name,
            "url": urlparse(url).scheme + "://" + urlparse(url).netloc,
        },
        "author": {"@type": "Organization", "name": site_name},
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def _build_faq_schema(html_content: str) -> str:
    """Build JSON-LD FAQ schema from HTML FAQ section."""
    faq_items = []

    # Find FAQ Q&A pairs
    question_pattern = re.compile(
        r'<p[^>]*class="faq-question"[^>]*><strong>Q:\s*(.*?)</strong></p>\s*'
        r'<p[^>]*class="faq-answer"[^>]*>(.*?)</p>',
        re.DOTALL | re.IGNORECASE,
    )
    matches = question_pattern.findall(html_content)

    # Also try plain bold Q: pattern
    if not matches:
        question_pattern2 = re.compile(
            r"<strong>Q:\s*(.*?)</strong>.*?A:\s*(.*?)</p>",
            re.DOTALL | re.IGNORECASE,
        )
        matches = question_pattern2.findall(html_content)

    for question, answer in matches:
        q_clean = re.sub(r"<[^>]+>", "", question).strip()
        a_clean = re.sub(r"<[^>]+>", "", answer).strip()
        if q_clean and a_clean:
            faq_items.append(
                {"@type": "Question", "name": q_clean, "acceptedAnswer": {"@type": "Answer", "text": a_clean}}
            )

    if not faq_items:
        return ""

    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_items}
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def _update_sitemap(output_dir: Path, url: str, lastmod: str) -> None:
    """Add or update a URL entry in sitemap.xml."""
    sitemap_path = output_dir / "sitemap.xml"
    try:
        if sitemap_path.exists():
            ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
            tree = ET.parse(str(sitemap_path))
            root = tree.getroot()
        else:
            root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
            tree = ET.ElementTree(root)

        ns = "http://www.sitemaps.org/schemas/sitemap/0.9"

        # Check if URL already exists
        existing_urls = [loc.text for loc in root.findall(f"{{{ns}}}url/{{{ns}}}loc")]
        if url not in existing_urls:
            url_el = ET.SubElement(root, f"{{{ns}}}url")
            loc_el = ET.SubElement(url_el, f"{{{ns}}}loc")
            loc_el.text = url
            lastmod_el = ET.SubElement(url_el, f"{{{ns}}}lastmod")
            lastmod_el.text = lastmod[:10]
            changefreq_el = ET.SubElement(url_el, f"{{{ns}}}changefreq")
            changefreq_el.text = "weekly"
            priority_el = ET.SubElement(url_el, f"{{{ns}}}priority")
            priority_el.text = "0.8"

        output_dir.mkdir(parents=True, exist_ok=True)
        tree.write(str(sitemap_path), xml_declaration=True, encoding="utf-8")
    except Exception as exc:
        logger.warning("Could not update sitemap: %s", exc)


def _ping_sitemap(site_url: str, output_dir: Path) -> None:
    """Ping Google to notify of sitemap update."""
    sitemap_url = f"{site_url.rstrip('/')}/sitemap.xml"
    ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"
    try:
        resp = requests.get(ping_url, timeout=5)
        logger.info("Sitemap pinged: %s → %d", ping_url, resp.status_code)
    except Exception as exc:
        logger.debug("Sitemap ping failed (non-critical): %s", exc)
