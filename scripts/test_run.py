#!/usr/bin/env python3
"""Run ONE complete cycle manually for testing with step-by-step output."""

import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

import yaml
from core import analytics_tracker

print("\n" + "=" * 60)
print("  🤖 AI Content Generator Bot — Test Run")
print("=" * 60)

# Initialize DB
db_path = PROJECT_ROOT / "data" / "bot.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
analytics_tracker.init_db(db_path)

# Load config
with open(PROJECT_ROOT / "config" / "niches.yaml") as f:
    niches = yaml.safe_load(f).get("niches", {})
with open(PROJECT_ROOT / "config" / "settings.yaml") as f:
    settings = yaml.safe_load(f)

settings["site_url"] = os.getenv("SITE_URL", "http://localhost:8080")
site_url = settings["site_url"]

# Pick first enabled niche for test
niche_id = None
niche_cfg = None
for nid, ncfg in niches.items():
    if ncfg.get("enabled", True):
        niche_id = nid
        niche_cfg = ncfg
        break

if not niche_id:
    print("❌ No enabled niches found in config/niches.yaml")
    sys.exit(1)

print(f"\n  Using niche: {niche_cfg['name']} ({niche_id})")
print("-" * 60)


def run_step(name: str, fn):
    """Run a step and print ✅/❌ result."""
    print(f"\n  ▶ {name}...")
    try:
        result = fn()
        if result is not None and result is not False:
            print(f"  ✅ {name} — OK")
            return result
        else:
            print(f"  ❌ {name} — returned None/False")
            return None
    except Exception as exc:
        print(f"  ❌ {name} — ERROR: {exc}")
        import traceback
        traceback.print_exc()
        return None


# ── Step 1: Trend Finder ─────────────────────────────────────────────────
from core import trend_finder
topics = run_step("Fetching trending topics", lambda: trend_finder.get_trending_topics(niche_id, niche_cfg, db_path))

if not topics:
    topics = niche_cfg.get("seed_keywords", [])[:3]
    print(f"  ⚠️  Using seed keywords as fallback: {topics[:2]}")

topic = topics[0] if topics else "best AI tools 2026"
print(f"  📌 Topic selected: {topic}")


# ── Step 2: LLM Writer ───────────────────────────────────────────────────
from core import llm_writer
article = run_step(f"Generating article: '{topic}'", lambda: llm_writer.generate_article(topic, niche_cfg))

if not article:
    print("\n  ⚠️  Ollama not available — using mock article for testing")
    article = {
        "title": f"Top 10 {topic.title()} You Need to Know in 2025",
        "html_content": f"""
<h1>Top 10 {topic.title()} You Need to Know in 2025</h1>
<p>Discover the most powerful {topic} that can transform your productivity and income in 2025.</p>
<h2>Why {topic.title()} Matter</h2>
<p>In today's fast-paced world, having the right tools makes all the difference between success and failure.</p>
<h2>The Best Options Available</h2>
<p>We've researched and tested dozens of options to bring you only the best. Here are our top picks.</p>
<h2>How to Get Started</h2>
<p>Getting started is easier than you think. Follow these simple steps to begin your journey.</p>
<h2>Frequently Asked Questions</h2>
<p class="faq-question"><strong>Q: What is the best option for beginners?</strong></p>
<p class="faq-answer">A: For beginners, we recommend starting with the most user-friendly option that offers a free trial.</p>
<p class="faq-question"><strong>Q: How much does it cost?</strong></p>
<p class="faq-answer">A: Prices range from free to $99/month depending on your needs and the plan you choose.</p>
<p class="faq-question"><strong>Q: Is it worth the investment?</strong></p>
<p class="faq-answer">A: Absolutely. Most users see a return on investment within the first month of use.</p>
<h2>Ready to Get Started?</h2>
<p>Don't wait — the best time to start is right now. Click the links below to try the top-rated options.</p>
""",
        "meta_description": f"Discover the top {topic} for 2025. Our expert guide covers everything you need to know.",
        "tags": niche_cfg.get("seed_keywords", [])[:5],
        "word_count": 350,
    }
    print(f"  ✅ Mock article created: {article['title']}")
else:
    print(f"     Title: {article['title']}")
    print(f"     Words: {article['word_count']}")


# ── Step 3: Affiliate Injector ───────────────────────────────────────────
from core import affiliate_injector
dashboard_url = f"http://localhost:{settings.get('dashboard', {}).get('port', 5000)}"

def inject():
    html, count = affiliate_injector.inject_links(article["html_content"], niche_cfg, dashboard_url)
    article["html_content"] = html
    article["affiliate_links_count"] = count
    return count

link_count = run_step("Injecting affiliate links", inject)
if link_count is not None:
    print(f"     Links injected: {link_count}")


# ── Step 4: SEO Optimizer ─────────────────────────────────────────────────
from core import seo_optimizer
output_dir = PROJECT_ROOT / "site" / "output"

def optimize():
    return seo_optimizer.optimize(article, niche_id, niche_cfg, site_url, output_dir)

optimized = run_step("SEO optimization", optimize)
if optimized:
    article.update(optimized)
    print(f"     Slug: {article.get('slug')}")
    print(f"     Canonical URL: {article.get('canonical_url')}")


# ── Step 5: Publisher ─────────────────────────────────────────────────────
from core import publisher
niche_name = niche_cfg.get("name", niche_id)

def publish():
    return publisher.publish(article, niche_id, niche_name, settings, db_path)

url_path = run_step("Publishing to static site", publish)
if url_path:
    print(f"     Published to: {url_path}")
    output_file = PROJECT_ROOT / "site" / "output" / niche_id / f"{article.get('slug', 'test')}.html"
    if output_file.exists():
        size = output_file.stat().st_size
        print(f"     File size: {size:,} bytes")


# ── Summary ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  TEST RUN SUMMARY")
print("=" * 60)

stats = analytics_tracker.get_dashboard_stats(db_path)
print(f"  📝 Total posts in DB: {stats['total_posts']}")
print(f"  💰 Est. income:       ${stats['estimated_income']:.2f}")
print(f"  📋 Recent logs:       {len(stats['recent_logs'])} entries")

output_html = PROJECT_ROOT / "site" / "output" / niche_id / f"{article.get('slug', '')}.html"
if output_html.exists():
    print(f"\n  ✅ Article HTML:  {output_html}")
else:
    print(f"\n  ⚠️  No HTML output file found")

index_html = PROJECT_ROOT / "site" / "output" / "index.html"
if index_html.exists():
    print(f"  ✅ Site index:    {index_html}")

print("\n  🎉 Test run complete!")
print(f"  Start dashboard: python scripts/start_dashboard.py")
print("=" * 60 + "\n")
