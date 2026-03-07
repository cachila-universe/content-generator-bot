#!/usr/bin/env python3
"""
Generate articles using smart niche rotation.

Picks the niches that have gone longest without a new article (round-robin),
respects max_posts_per_day from settings.yaml, and uses trend-based topics.

Usage:
  python scripts/batch_generate.py             # Auto-rotate (default 3 niches)
  python scripts/batch_generate.py --all       # Force all 8 niches (ignore limits)
  python scripts/batch_generate.py --niche ai_tools pet_care   # Specific niches only
"""
import os
import sys
import yaml
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from core import analytics_tracker, llm_writer, affiliate_injector, seo_optimizer, publisher

# Optional modules (may not exist)
try:
    from core import internal_linker
except ImportError:
    internal_linker = None

db_path = PROJECT_ROOT / "data" / "bot.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
analytics_tracker.init_db(db_path)

with open("config/niches.yaml") as f:
    niches = yaml.safe_load(f).get("niches", {})
with open("config/settings.yaml") as f:
    settings = yaml.safe_load(f)

settings["site_url"] = os.getenv("SITE_URL", "https://tech-life-insights.com")
site_url = settings["site_url"]
output_dir = PROJECT_ROOT / "site" / "output"

# ── Parse arguments ──────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate articles with niche rotation")
parser.add_argument("--all", action="store_true", help="Generate for ALL niches (ignore daily limit)")
parser.add_argument("--niche", nargs="+", help="Specific niche IDs to generate for")
args = parser.parse_args()

max_per_day = settings.get("scheduler", {}).get("max_posts_per_day", 3)

# ── Determine which niches to run ────────────────────────────────────────
if args.niche:
    # User specified exact niches
    selected = [n for n in args.niche if n in niches]
    if not selected:
        print(f"❌ None of {args.niche} found in niches.yaml")
        print(f"   Available: {list(niches.keys())}")
        sys.exit(1)
elif args.all:
    # All enabled niches
    selected = [nid for nid, cfg in niches.items() if cfg.get("enabled", True)]
else:
    # Smart rotation: pick niches with oldest last-post time
    from core import bot_state
    all_ids = [nid for nid, cfg in niches.items() if cfg.get("enabled", True)]
    selected = bot_state.get_todays_niches(all_ids, max_per_day)

print(f"\n{'='*60}")
print(f"  BATCH GENERATE — {len(selected)} niches")
print(f"  Rotation: {', '.join(selected)}")
print(f"{'='*60}")


# ── Pick topics using trend_finder ───────────────────────────────────────
def pick_topic(niche_id, niche_cfg):
    """Pick a trending topic for a niche, avoiding duplicates."""
    try:
        from core import trend_finder
        topics = trend_finder.get_trending_topics(niche_id, niche_cfg, db_path)
        if topics:
            topic_data = topics[0] if isinstance(topics[0], dict) else {"topic": topics[0]}
            return topic_data.get("topic", str(topics[0]))
    except Exception:
        pass
    # Fallback to first seed keyword
    keywords = niche_cfg.get("seed_keywords", [])
    return keywords[0] if keywords else f"best {niche_cfg.get('name', niche_id)} 2026"


# ── Generate ─────────────────────────────────────────────────────────────
success_count = 0

for niche_id in selected:
    niche_cfg = niches[niche_id]
    topic = pick_topic(niche_id, niche_cfg)

    print(f"\n{'─'*60}")
    print(f"  Generating: {topic}")
    print(f"  Niche: {niche_cfg['name']} ({niche_id})")
    print(f"{'─'*60}")

    try:
        article = llm_writer.generate_article(topic, niche_cfg)
        if not article:
            print(f"  ❌ LLM failed for {niche_id}")
            continue

        print(f"  ✅ Generated: {article['title']} ({article['word_count']} words)")

        # Affiliate injection
        html, count = affiliate_injector.inject_links(article["html_content"], niche_cfg, "")
        article["html_content"] = html
        article["affiliate_links_count"] = count
        print(f"  ✅ Affiliate links: {count}")

        # Internal linking
        if internal_linker:
            all_posts = analytics_tracker.get_all_posts(db_path)
            article["html_content"] = internal_linker.inject_internal_links(
                article["html_content"], "", all_posts, site_url
            )

        # SEO optimization (includes Pexels image search)
        article.update(seo_optimizer.optimize(article, niche_id, niche_cfg, site_url, output_dir))
        print(f"  ✅ SEO: {article['slug']}")
        if article.get("image_url"):
            print(f"  🖼️  Hero image: {article['image_url'][:70]}...")
        else:
            print(f"  ⚠️  No relevant hero image found (skipped)")

        # Publish
        url = publisher.publish(article, niche_id, niche_cfg["name"], settings, db_path)
        print(f"  ✅ Published: {url}")

        # Record for rotation tracking
        try:
            from core import bot_state
            bot_state.record_post_run(niche_id)
        except Exception:
            pass

        success_count += 1

    except Exception as exc:
        print(f"  ❌ Error: {exc}")
        import traceback
        traceback.print_exc()

# ── Summary ──────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  BATCH SUMMARY")
print(f"{'='*60}")
stats = analytics_tracker.get_dashboard_stats(db_path)
print(f"  ✅ Generated: {success_count}/{len(selected)} articles")
print(f"  📝 Total posts: {stats['total_posts']}")
print(f"  💰 Est. income: ${stats['estimated_income']:.2f}")

# Show next rotation
remaining = [n for n in niches if n not in selected and niches[n].get("enabled", True)]
if remaining:
    print(f"  🔄 Next rotation: {', '.join(remaining[:max_per_day])}")

print(f"  🎉 Done!")
print(f"{'='*60}")
