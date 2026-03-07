"""SEO optimizer that adds meta tags, schema markup, sitemaps, and canonical URLs."""

import re
import os
import json
import logging
import requests
from pathlib import Path
from slugify import slugify
from datetime import datetime, timezone
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def optimize(article: dict, niche_id: str, niche_config: dict, site_url: str, output_dir: Path) -> dict:
    """
    Add SEO metadata, schema markup, sitemap entry, and canonical URL to article.

    Returns enriched article dict with: slug, meta_html, schema_markup, canonical_url
    """
    title = article.get("title", "Untitled")
    meta_description = article.get("meta_description", "")
    tags = article.get("tags", [])
    html_content = article.get("html_content", "")
    published_at = datetime.now(timezone.utc).isoformat()

    # Generate URL slug
    slug = slugify(title, max_length=80, word_boundary=True, save_order=True)
    canonical_url = f"{site_url.rstrip('/')}/{niche_id}/{slug}.html"

    # Hero image via Picsum Photos (free, no API key needed)
    # For production: replace with Unsplash API or your own image CDN
    image_url = f"https://picsum.photos/seed/{slug}/800/450"

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

    # Inject inline images after every H2 heading (richer articles)
    enriched_content = _inject_inline_images(html_content, slug, niche_id)

    # Update sitemap
    _update_sitemap(output_dir, canonical_url, published_at)

    # Ping Google sitemap (best-effort)
    if os.getenv("SITEMAP_PING_ENABLED", "true").lower() == "true":
        _ping_sitemap(site_url, output_dir)

    return {
        **article,
        "html_content": enriched_content,
        "slug": slug,
        "meta_html": meta_html,
        "schema_markup": schema_markup,
        "canonical_url": canonical_url,
        "published_at": published_at,
        "image_url": image_url,
    }


def _inject_inline_images(html_content: str, base_slug: str, niche_id: str = "") -> str:
    """
    Inject topic-relevant images throughout the article dynamically.
    Uses Unsplash Source (keyword-based, free, no API key) so images relate to the section.
    Number of images varies per article — typically 2-5 depending on section count.
    Each image uses a unique seed to avoid duplicates within the same article.
    Skips FAQ, Conclusion, and headings that are purely affiliate links.
    """
    import hashlib

    # Words that add no keyword value — filtered out before building the image query
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

    # Per-niche fallback keywords if heading yields nothing useful
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

    # Count total content H2s (excluding FAQ/Conclusion) to decide image placement
    all_h2s = re.findall(r"<h2>(.*?)</h2>", html_content, flags=re.IGNORECASE | re.DOTALL)
    content_h2s = []
    for h2_html in all_h2s:
        plain = re.sub(r'<[^>]+>', '', h2_html).strip().lower()
        if not any(w in plain for w in ("faq", "frequently", "question", "conclusion")):
            content_h2s.append(plain)

    total_sections = len(content_h2s)

    # Decide which sections get images — spread them out, never the same pattern
    # For 1-2 sections: image on every section
    # For 3-4 sections: image on 2-3 sections (skip one in the middle)
    # For 5+ sections:  image on 3-4 sections (spread evenly)
    if total_sections <= 2:
        image_positions = set(range(1, total_sections + 1))
    elif total_sections <= 4:
        # Always first, always last content section, and one in middle
        image_positions = {1, total_sections}
        if total_sections >= 3:
            image_positions.add(total_sections // 2 + 1)
    else:
        # Spread evenly: first, ~1/3, ~2/3, last
        image_positions = {1, total_sections}
        step = max(1, total_sections // 3)
        for i in range(step, total_sections, step):
            image_positions.add(i)
        # Cap at 5 images max for very long articles
        if len(image_positions) > 5:
            image_positions = set(sorted(image_positions)[:5])

    used_seeds = set()
    img_counter = [0]

    def _keywords_from_heading(raw_html: str) -> str:
        """Strip HTML, remove stop words, return comma-separated keywords."""
        clean = re.sub(r'<[^>]+>', '', raw_html)          # strip HTML tags
        clean = re.sub(r'[^a-zA-Z0-9 ]', ' ', clean)      # keep only alphanumeric
        words = [w.lower() for w in clean.split() if len(w) > 2 and w.lower() not in _STOP_WORDS]
        keywords = words[:3]  # up to 3 keywords for better specificity
        if not keywords:
            keywords = _NICHE_FALLBACK.get(niche_id, 'lifestyle,guide').split(',')
        return ','.join(keywords)

    def _unique_seed(keywords: str) -> str:
        """Generate a unique seed from keywords + counter so no two images repeat."""
        raw = f"{base_slug}-{keywords}-{img_counter[0]}"
        seed = hashlib.md5(raw.encode()).hexdigest()[:8]
        # Ensure uniqueness even if keywords repeat
        while seed in used_seeds:
            seed = hashlib.md5(f"{seed}x".encode()).hexdigest()[:8]
        used_seeds.add(seed)
        return seed

    def _replace_h2(match: re.Match) -> str:
        heading_html = match.group(1)
        plain_heading = re.sub(r'<[^>]+>', '', heading_html).strip()

        # Skip image injection for FAQ / Conclusion / Questions sections
        lower = plain_heading.lower()
        if any(word in lower for word in ("faq", "frequently", "question", "conclusion")):
            return match.group(0)

        img_counter[0] += 1

        # Only inject at dynamically chosen positions
        if img_counter[0] not in image_positions:
            return match.group(0)

        keywords = _keywords_from_heading(heading_html)
        seed = _unique_seed(keywords)
        alt_text = plain_heading[:80] if plain_heading else keywords.replace(',', ' ')

        # Picsum with seed ensures deterministic unique images per section
        # Use keyword-derived seed so the same topic always gets the same image
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
