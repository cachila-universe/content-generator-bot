#!/usr/bin/env python3
"""Generate articles for multiple niches in a single run."""
import os
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from core import analytics_tracker, llm_writer, affiliate_injector, seo_optimizer, publisher, internal_linker

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

# Topics to generate — one per niche
jobs = [
    ("personal_finance", "best budgeting apps 2026"),
    ("health_biohacking", "best supplements for energy and focus"),
    ("home_tech", "best smart home devices 2026"),
    ("travel", "budget travel tips for solo travelers"),
]

for niche_id, topic in jobs:
    niche_cfg = niches.get(niche_id)
    if not niche_cfg or not niche_cfg.get("enabled", True):
        print(f"Skipping disabled niche: {niche_id}")
        continue

    print(f"\n{'='*60}")
    print(f"  Generating: {topic}")
    print(f"  Niche: {niche_cfg['name']} ({niche_id})")
    print(f"{'='*60}")

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
        all_posts = analytics_tracker.get_all_posts(db_path)
        article["html_content"] = internal_linker.inject_internal_links(
            article["html_content"], "", all_posts, site_url
        )

        # SEO optimization
        article.update(seo_optimizer.optimize(article, niche_id, niche_cfg, site_url, output_dir))
        print(f"  ✅ SEO: {article['slug']}")

        # Publish
        url = publisher.publish(article, niche_id, niche_cfg["name"], settings, db_path)
        print(f"  ✅ Published: {url}")

    except Exception as exc:
        print(f"  ❌ Error: {exc}")
        import traceback
        traceback.print_exc()

# Summary
print(f"\n{'='*60}")
print("  BATCH SUMMARY")
print(f"{'='*60}")
stats = analytics_tracker.get_dashboard_stats(db_path)
print(f"  📝 Total posts: {stats['total_posts']}")
print(f"  💰 Est. income: ${stats['estimated_income']:.2f}")
print(f"  🎉 Done!")
print(f"{'='*60}")
