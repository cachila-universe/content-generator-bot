#!/usr/bin/env python3
"""
Rewrite hero and inline images in existing published articles.
Replaces Picsum/LoremFlickr URLs with relevant Pexels images.
Does NOT regenerate article content — only updates images.
"""
import os
import re
import sys
import yaml
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from core.seo_optimizer import (
    _extract_image_query,
    _load_pexels_key,
    _fetch_pexels_image_relevant,
    _fetch_pexels_image,
    _STOP_WORDS_IMG,
)

OUTPUT_DIR = PROJECT_ROOT / "site" / "output"
DB_PATH = PROJECT_ROOT / "data" / "bot.db"


def get_all_articles():
    """Get all published articles from DB."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT niche_id, title, slug, url FROM posts ORDER BY niche_id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fix_article_images(article: dict, pexels_key: str) -> bool:
    """Replace Picsum/LoremFlickr images in an article's HTML file with Pexels."""
    niche_id = article["niche_id"]
    slug = article["slug"]
    title = article["title"]

    html_path = OUTPUT_DIR / niche_id / f"{slug}.html"
    if not html_path.exists():
        logger.warning("File not found: %s", html_path)
        return False

    html = html_path.read_text(encoding="utf-8")
    original = html

    # 1. Fix hero image (Picsum → Pexels)
    hero_url = _fetch_pexels_image_relevant(title, niche_id)

    if hero_url:
        # Replace OG/Twitter meta images
        html = re.sub(
            r'(content=")https://picsum\.photos/[^"]*(")',
            rf'\1{hero_url}\2',
            html,
        )
        # Replace hero img src
        html = re.sub(
            r'(src=")https://picsum\.photos/[^"]*(")',
            rf'\1{hero_url}\2',
            html,
        )
        # Also fix escaped versions (Jinja2 escapes & to &amp;)
        hero_escaped = hero_url.replace("&", "&amp;")
        html = re.sub(
            r'(src=")https://picsum\.photos/[^"]*(")',
            rf'\1{hero_escaped}\2',
            html,
        )
        logger.info("  Hero: Pexels ✓")
    else:
        # Remove the hero image entirely rather than keep random one
        html = re.sub(
            r'<div[^>]*>\s*<img[^>]*src="https://picsum\.photos/[^"]*"[^>]*>\s*</div>',
            '',
            html,
        )
        # Remove OG/Twitter image meta tags with picsum
        html = re.sub(
            r'<meta[^>]*content="https://picsum\.photos/[^"]*"[^>]*>\n?',
            '',
            html,
        )
        logger.info("  Hero: removed (no relevant Pexels match)")

    # 2. Fix inline images (LoremFlickr/Picsum → Pexels)
    inline_count = 0

    def replace_inline(match):
        nonlocal inline_count
        full_tag = match.group(0)
        alt_text = re.search(r'alt="([^"]*)"', full_tag)
        heading = alt_text.group(1) if alt_text else ""

        # Try Pexels for this heading
        pexels_url = _fetch_pexels_image(heading, niche_id) if heading else None

        if pexels_url:
            inline_count += 1
            new_tag = re.sub(r'src="[^"]*"', f'src="{pexels_url}"', full_tag)
            return new_tag
        else:
            # Remove the entire figure if no relevant image
            return ''

    # Replace LoremFlickr inline images
    html = re.sub(
        r'<figure[^>]*>\s*<img[^>]*src="https://loremflickr\.com/[^"]*"[^>]*>\s*</figure>',
        replace_inline,
        html,
    )

    # Replace Picsum inline images (in figures)
    html = re.sub(
        r'<figure[^>]*>\s*<img[^>]*src="https://picsum\.photos/seed/[^"]*"[^>]*>\s*</figure>',
        replace_inline,
        html,
    )

    if html != original:
        html_path.write_text(html, encoding="utf-8")
        logger.info("  Inline images updated: %d replaced", inline_count)
        return True
    else:
        logger.info("  No changes needed")
        return False


def main():
    key = _load_pexels_key()
    if not key:
        logger.error("No Pexels API key found!")
        sys.exit(1)

    articles = get_all_articles()
    logger.info("Found %d articles to process", len(articles))

    fixed = 0
    for art in articles:
        logger.info("[%s] %s", art["niche_id"], art["title"][:60])
        if fix_article_images(art, key):
            fixed += 1

    logger.info("\nDone! Fixed %d/%d articles", fixed, len(articles))


if __name__ == "__main__":
    main()
