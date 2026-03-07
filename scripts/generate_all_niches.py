#!/usr/bin/env python3
"""Generate ONE article per niche using the full pipeline (trend → write → SEO → publish)."""

import os
import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("generate_all")

import yaml
from core import (
    analytics_tracker, trend_finder, llm_writer,
    affiliate_injector, seo_optimizer, publisher
)

# Try importing internal_linker (may not exist yet)
try:
    from core import internal_linker
    HAS_INTERNAL_LINKER = True
except ImportError:
    HAS_INTERNAL_LINKER = False

# ── Config ────────────────────────────────────────────────────────────────
DB_PATH = PROJECT_ROOT / "data" / "bot.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
analytics_tracker.init_db(DB_PATH)

with open(PROJECT_ROOT / "config" / "niches.yaml") as f:
    niches = yaml.safe_load(f).get("niches", {})
with open(PROJECT_ROOT / "config" / "settings.yaml") as f:
    settings = yaml.safe_load(f)

SITE_URL = os.getenv("SITE_URL", settings.get("site_url", "https://tech-life-insights.com"))
settings["site_url"] = SITE_URL
OUTPUT_DIR = PROJECT_ROOT / "site" / "output"
DASHBOARD_URL = f"http://localhost:{settings.get('dashboard', {}).get('port', 5002)}"

print("\n" + "=" * 60)
print("  🤖 Generate One Article Per Niche")
print(f"  Model: qwen2.5:14b  |  Site: {SITE_URL}")
print("=" * 60)

results = []

for niche_id, niche_cfg in niches.items():
    if not niche_cfg.get("enabled", True):
        print(f"\n  ⏭  Skipping disabled niche: {niche_id}")
        continue

    niche_name = niche_cfg.get("name", niche_id)
    print(f"\n{'─'*60}")
    print(f"  📌 Niche: {niche_name} ({niche_id})")

    # 1. Get topic
    try:
        topics = trend_finder.get_trending_topics(niche_id, niche_cfg, DB_PATH)
        topic = topics[0] if topics else niche_cfg.get("seed_keywords", ["best tools 2026"])[0]
    except Exception:
        topic = niche_cfg.get("seed_keywords", ["best tools 2026"])[0]
    print(f"  🔍 Topic: {topic}")

    # 2. Generate article
    try:
        article = llm_writer.generate_article(topic, niche_cfg)
        if not article:
            raise ValueError("Empty article returned")
        print(f"  ✍️  Title: {article['title']}")
        print(f"  📝 Words: {article.get('word_count', '?')}")
    except Exception as exc:
        logger.error("LLM write failed for %s: %s", niche_id, exc)
        results.append((niche_id, False, str(exc)))
        continue

    # 3. Inject affiliate links
    try:
        html, count = affiliate_injector.inject_links(article["html_content"], niche_cfg, DASHBOARD_URL)
        article["html_content"] = html
        article["affiliate_links_count"] = count
        print(f"  🔗 Affiliate links: {count}")
    except Exception as exc:
        logger.warning("Affiliate injection failed: %s", exc)
        article["affiliate_links_count"] = 0

    # 4. Internal linking
    if HAS_INTERNAL_LINKER:
        try:
            all_posts = analytics_tracker.get_all_posts(DB_PATH)
            article["html_content"] = internal_linker.inject_internal_links(
                article["html_content"], article.get("slug", ""), all_posts, SITE_URL
            )
        except Exception as exc:
            logger.warning("Internal linking failed: %s", exc)

    # 5. SEO optimization
    try:
        optimized = seo_optimizer.optimize(article, niche_id, niche_cfg, SITE_URL, OUTPUT_DIR)
        if optimized:
            article.update(optimized)
        print(f"  🔎 Slug: {article.get('slug')}")
    except Exception as exc:
        logger.error("SEO optimization failed: %s", exc)
        results.append((niche_id, False, str(exc)))
        continue

    # 6. Publish
    try:
        url = publisher.publish(article, niche_id, niche_name, settings, DB_PATH)
        if url:
            print(f"  ✅ Published: {url}")
            results.append((niche_id, True, url))
        else:
            raise ValueError("publisher.publish returned empty URL")
    except Exception as exc:
        logger.error("Publish failed: %s", exc)
        results.append((niche_id, False, str(exc)))

# ── Final rebuild ─────────────────────────────────────────────────────────
print(f"\n{'─'*60}")
print("  🔄 Rebuilding site indexes...")
try:
    publisher.rebuild_site(settings, DB_PATH, SITE_URL)
    print("  ✅ Site indexes rebuilt")
except Exception as exc:
    logger.error("Site rebuild failed: %s", exc)

# ── Summary ───────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  GENERATION SUMMARY")
print(f"{'='*60}")
ok = [r for r in results if r[1]]
fail = [r for r in results if not r[1]]
print(f"  ✅ Success: {len(ok)} niches")
for nid, _, url in ok:
    print(f"     {nid}: {url}")
if fail:
    print(f"  ❌ Failed: {len(fail)} niches")
    for nid, _, err in fail:
        print(f"     {nid}: {err}")

stats = analytics_tracker.get_dashboard_stats(DB_PATH)
print(f"\n  📊 Total posts now: {stats['total_posts']}")
print(f"  💰 Est. income:     ${stats['estimated_income']:.2f}")
print(f"{'='*60}\n")
