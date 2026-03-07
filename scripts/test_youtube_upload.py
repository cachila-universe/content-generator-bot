#!/usr/bin/env python3
"""
End-to-end YouTube pipeline test.

Reads an article from the DB + HTML file, generates a video with Edge TTS,
and uploads it to YouTube with proper metadata.
"""

import os
import sys
import json
import yaml
import sqlite3
import logging
from pathlib import Path
from bs4 import BeautifulSoup

# Project root
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Load .env
env_path = ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s — %(message)s",
)
logger = logging.getLogger("test_youtube")


def get_article_from_db(niche_name: str = "ai_tools") -> dict | None:
    """Fetch the latest article for a niche from the DB."""
    db_path = ROOT / "data" / "bot.db"
    if not db_path.exists():
        logger.error("Database not found: %s", db_path)
        return None

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM posts WHERE niche_id = ? ORDER BY id DESC LIMIT 1",
        (niche_name,),
    ).fetchone()
    conn.close()

    if not row:
        logger.error("No article found for niche '%s'", niche_name)
        return None

    return dict(row)


def load_html_content(article: dict) -> str:
    """Read article HTML from the site output files."""
    niche = article["niche_id"]
    slug = article["slug"]
    html_path = ROOT / "site" / "output" / niche / f"{slug}.html"

    if not html_path.exists():
        logger.error("HTML file not found: %s", html_path)
        return ""

    full_html = html_path.read_text(encoding="utf-8")

    # Extract just the article body content
    soup = BeautifulSoup(full_html, "html.parser")

    # Try <article> tag first, then <main>, then full body
    article_el = soup.find("article") or soup.find("main")
    if article_el:
        return str(article_el)

    # Fallback: return everything inside <body>
    body = soup.find("body")
    return str(body) if body else full_html


def extract_meta_description(article: dict) -> str:
    """Extract meta description from the HTML file."""
    niche = article["niche_id"]
    slug = article["slug"]
    html_path = ROOT / "site" / "output" / niche / f"{slug}.html"

    if not html_path.exists():
        return ""

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"]

    # Fallback: first paragraph
    p = soup.find("p")
    return p.get_text()[:200] if p else ""


def load_niche_config(niche_name: str) -> dict:
    """Load niche configuration from niches.yaml."""
    config_path = ROOT / "config" / "niches.yaml"
    if not config_path.exists():
        return {}

    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    return data.get("niches", {}).get(niche_name, {})


def main():
    niche = sys.argv[1] if len(sys.argv) > 1 else "ai_tools"

    print(f"\n{'='*60}")
    print(f"  🎬  YouTube Pipeline Test — niche: {niche}")
    print(f"{'='*60}\n")

    # ── 1. Fetch article from DB ──────────────────────────────────
    print("📋 Step 1: Fetching article from database...")
    article = get_article_from_db(niche)
    if not article:
        sys.exit(1)

    print(f"   ✅ Found: {article['title']}")
    print(f"   📎 Slug:  {article['slug']}")
    print(f"   🔗 URL:   {article['url']}")

    # ── 2. Load HTML content ──────────────────────────────────────
    print("\n📄 Step 2: Loading HTML content...")
    html_content = load_html_content(article)
    if not html_content:
        print("   ❌ Failed to load HTML content")
        sys.exit(1)
    print(f"   ✅ HTML loaded ({len(html_content):,} chars)")

    # ── 3. Build enriched article dict ────────────────────────────
    meta_desc = extract_meta_description(article)
    article["html_content"] = html_content
    article["meta_description"] = meta_desc
    article["tags"] = []  # DB doesn't store tags

    print(f"   📝 Meta: {meta_desc[:80]}...")

    # ── 4. Load niche config ──────────────────────────────────────
    print("\n⚙️  Step 3: Loading niche config...")
    niche_config = load_niche_config(niche)
    if not niche_config:
        print("   ❌ Niche config not found")
        sys.exit(1)
    print(f"   ✅ Niche: {niche_config.get('name', niche)}")
    print(f"   🔑 Keywords: {', '.join(niche_config.get('seed_keywords', [])[:3])}")

    # ── 5. Generate video ─────────────────────────────────────────
    print("\n🎥 Step 4: Generating video with Edge TTS...")
    from core.video_generator import generate_video

    video_output = ROOT / "data" / "videos" / f"{article['slug']}.mp4"
    video_output.parent.mkdir(parents=True, exist_ok=True)

    result = generate_video(article, video_output)
    if not result:
        print("   ❌ Video generation failed")
        sys.exit(1)

    file_size_mb = video_output.stat().st_size / (1024 * 1024)
    print(f"   ✅ Video generated: {video_output}")
    print(f"   📦 Size: {file_size_mb:.1f} MB")

    # ── 6. Preview description & tags ─────────────────────────────
    print("\n📝 Step 5: Preview YouTube metadata...")
    from core.youtube_uploader import _build_description, _build_tags

    desc = _build_description(article, niche_config)
    tags = _build_tags(article, niche_config)

    print(f"\n{'─'*50}")
    print("DESCRIPTION PREVIEW:")
    print(f"{'─'*50}")
    print(desc[:600])
    print("...(truncated)")
    print(f"\n{'─'*50}")
    print(f"TAGS ({len(tags)}): {', '.join(tags[:8])}...")
    print(f"{'─'*50}")

    # ── 7. Upload to YouTube ──────────────────────────────────────
    print("\n🚀 Step 6: Uploading to YouTube...")

    confirm = input("\n   ⚡ Ready to upload? (y/n): ").strip().lower()
    if confirm != "y":
        print("   ⏸️  Upload cancelled.")
        print(f"\n   Video saved at: {video_output}")
        return

    from core.youtube_uploader import upload_video

    youtube_url = upload_video(
        video_path=video_output,
        article=article,
        niche_config=niche_config,
        channel_name="TechLife Insights",
    )

    if youtube_url:
        print(f"\n   🎉 SUCCESS! Video live at: {youtube_url}")

        # Update DB with YouTube URL
        db_path = ROOT / "data" / "bot.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            "UPDATE posts SET youtube_url = ? WHERE id = ?",
            (youtube_url, article["id"]),
        )
        conn.commit()
        conn.close()
        print(f"   📊 Database updated with YouTube URL")
    else:
        print("   ❌ Upload failed. Check logs above.")

    print(f"\n{'='*60}")
    print(f"  Pipeline complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
