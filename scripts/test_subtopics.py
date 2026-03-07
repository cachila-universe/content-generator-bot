#!/usr/bin/env python3
"""Test script for subtopic system integration."""

import sys
sys.path.insert(0, ".")

print("=== Testing imports ===")
from core import publisher
print("  publisher OK")
from core import trend_finder
print("  trend_finder OK")
from core import llm_writer
print("  llm_writer OK")
from core import analytics_tracker
print("  analytics_tracker OK")
from core import content_intelligence
print("  content_intelligence OK")
from core import seo_optimizer
print("  seo_optimizer OK")
print()

print("=== Testing subtopic classification ===")
from core.content_intelligence import classify_article_subtopic
import yaml

with open("config/niches.yaml") as f:
    niches_data = yaml.safe_load(f) or {}
niches = niches_data.get("niches", {})

result = classify_article_subtopic(
    "Best AI Apps for Productivity",
    "top ai apps productivity workflow automation",
    "ai_tools", niches.get("ai_tools", {}),
)
print(f"  ai_tools / AI Apps article -> subtopic: {result}")

result2 = classify_article_subtopic(
    "Bitcoin Price Analysis",
    "bitcoin crypto market analysis trading",
    "personal_finance", niches.get("personal_finance", {}),
)
print(f"  personal_finance / Bitcoin article -> subtopic: {result2}")

result3 = classify_article_subtopic(
    "Best Hotels in Bali",
    "luxury hotels bali destinations accommodation",
    "travel", niches.get("travel", {}),
)
print(f"  travel / Hotels article -> subtopic: {result3}")

result4 = classify_article_subtopic(
    "Best Running Shoes 2025",
    "running shoes marathon training gear runners",
    "fitness_wellness", niches.get("fitness_wellness", {}),
)
print(f"  fitness_wellness / Running Shoes -> subtopic: {result4}")

result5 = classify_article_subtopic(
    "Best Dog Food Brands",
    "dog food nutrition kibble brands pet food",
    "pet_care", niches.get("pet_care", {}),
)
print(f"  pet_care / Dog Food -> subtopic: {result5}")
print()

print("=== Testing trend_finder subtopic picking ===")
from pathlib import Path
db_path = Path("data/bot.db")
from core.trend_finder import _pick_subtopic, _load_subtopics

for niche in ["ai_tools", "personal_finance", "travel", "fitness_wellness", "pet_care"]:
    subs = _load_subtopics(niche)
    sub_id, sub_cfg = _pick_subtopic(niche, db_path)
    print(f"  {niche}: {len(subs)} subtopics, picked: {sub_id}")
print()

print("=== Testing content intelligence format recommendation ===")
from core.content_intelligence import get_recommended_format

for niche, topic in [
    ("fitness_wellness", "Best Running Shoes 2025"),
    ("ai_tools", "How to Use ChatGPT for Coding"),
    ("personal_finance", "Top Crypto to Buy in 2025"),
    ("home_tech", "Ring vs Nest Doorbell Camera"),
]:
    rec = get_recommended_format(niche, topic)
    fmt = rec.get("format_name", rec.get("format_id", "?")) if rec else "none"
    print(f"  {niche} / {topic[:30]}... -> {fmt}")
print()

print("=== Testing publisher rebuild ===")
import yaml
with open("config/settings.yaml") as f:
    settings = yaml.safe_load(f) or {}
site_url = settings.get("site_url", "https://tech-life-insights.com")

from core.publisher import rebuild_site
rebuild_site(settings, db_path, site_url)
print("  rebuild_site completed")
print()

# Check what was generated
import os
output_dir = "site/output"
for root, dirs, files in os.walk(output_dir):
    depth = root.replace(output_dir, "").count(os.sep)
    indent = "  " * (depth + 1)
    folder = os.path.basename(root)
    html_count = sum(1 for f in files if f.endswith(".html"))
    if html_count > 0:
        print(f"{indent}{folder}/ ({html_count} html files)")

print()
print("=== ALL TESTS PASSED ===")
