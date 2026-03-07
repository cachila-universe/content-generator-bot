#!/usr/bin/env python3
"""Test the new Pexels image system with real article titles."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.seo_optimizer import (
    _extract_image_query,
    _load_pexels_key,
    _fetch_pexels_image_relevant,
    _is_image_relevant,
)
import requests

titles = [
    ("Top Dog Food Picks for 2026: Ensuring Optimal Nutrition for Your Canine Companion", "pet_care"),
    ("Navigating the Future: The Top AI Tools for 2026", "ai_tools"),
    ("The Ultimate Guide to Best Home Gym Equipment for 2026", "fitness_wellness"),
    ("Biohacking Tips 2026: Mastering Your Peak Performance", "health_biohacking"),
    ("The Future of Home Automation: Best Smart Home Devices 2026", "home_tech"),
    ("Mastering Your Financial Future: How to Invest Money in 2026", "personal_finance"),
    ("Exploring the World in 2026: Top Travel Destinations and Tips", "travel"),
    ("The Ultimate Guide to the Best Home Office Setup 2026", "remote_work"),
]

print("=== Keyword Extraction ===")
for title, niche in titles:
    q = _extract_image_query(title, niche)
    print(f"  [{niche:20s}] query: \"{q}\"")
print()

key = _load_pexels_key()
print(f"Pexels key loaded: {'YES' if key else 'NO'} ({len(key)} chars)")
print()

if not key:
    print("No Pexels key — cannot test image search")
    sys.exit(1)

print("=== Pexels Image Search (all 8 titles) ===")
for title, niche in titles:
    url = _fetch_pexels_image_relevant(title, niche)
    status = "FOUND" if url else "SKIPPED (no relevant match)"
    short_url = url[:80] + "..." if url and len(url) > 80 else (url or "")
    print(f"  [{niche:20s}] {status}")
    if url:
        print(f"    {short_url}")
    print()

print("Done!")
