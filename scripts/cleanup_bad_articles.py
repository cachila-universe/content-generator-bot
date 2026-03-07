"""One-time cleanup: delete all articles that contain [H2 Section X Title] placeholders."""
import sqlite3
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
DB   = ROOT / "data" / "bot.db"

BAD_FILES = [
    "site/output/personal_finance/unleashing-financial-freedom-the-best-budgeting-apps-of-2026.html",
    "site/output/personal_finance/unveiling-the-best-budgeting-apps-of-2026-for-a-prosperous-financial-future.html",
    "site/output/personal_finance/discover-the-best-budgeting-apps-of-2026-for-your-financial-success.html",
    "site/output/ai_tools/unleashing-productivity-with-the-best-ai-tools-of-2026.html",
    "site/output/home_tech/the-top-smart-home-devices-to-watch-out-for-in-2026-your-comprehensive-home.html",
    "site/output/home_tech/discover-the-best-smart-home-devices-of-2026-your-ultimate-home-automation-guide.html",
    "site/output/home_tech/the-ultimate-guide-to-the-best-smart-home-devices-of-2026.html",
    "site/output/travel/unveiling-budget-travel-tips-for-solo-travelers-in-2026.html",
    "site/output/travel/unveiling-the-ultimate-budget-travel-guide-for-solo-adventurers-in-2026.html",
    "site/output/travel/budget-solo-travel-guide-exploring-the-best-travel-destinations-in-2026-on-a.html",
    "site/output/health_biohacking/unleashing-optimal-energy-and-focus-top-biohacking-supplements-for-2026.html",
    "site/output/health_biohacking/unleash-your-peak-performance-the-best-supplements-for-energy-and-focus.html",
    "site/output/health_biohacking/unleash-your-potential-the-best-supplements-for-energy-and-focus-in-2026.html",
]

conn = sqlite3.connect(str(DB))
removed_files = 0
removed_db = 0

for rel_path in BAD_FILES:
    p = ROOT / rel_path
    slug = p.stem  # filename without .html extension
    if p.exists():
        p.unlink()
        removed_files += 1
        print(f"  deleted file: {rel_path}")
    cur = conn.execute("DELETE FROM posts WHERE slug = ?", (slug,))
    if cur.rowcount:
        conn.execute("DELETE FROM clicks WHERE post_slug = ?", (slug,))
        removed_db += cur.rowcount
        print(f"  deleted DB row: slug={slug}")

conn.commit()
conn.close()

# Also remove the stray test.txt if it exists
test_txt = ROOT / "site" / "output" / "test.txt"
if test_txt.exists():
    test_txt.unlink()
    print("  deleted test.txt")

print(f"\nDone. Files deleted: {removed_files}  DB rows deleted: {removed_db}")

# Rebuild site indexes
import sys
sys.path.insert(0, str(ROOT))
import yaml
from pathlib import Path
from core import publisher, analytics_tracker

settings_path = ROOT / "config" / "settings.yaml"
with open(settings_path) as f:
    settings = yaml.safe_load(f)

db_path = DB
site_url = settings.get("site_url", "https://tech-life-insights.com")

print("\nRebuilding site indexes...")
publisher.rebuild_site(settings, db_path, site_url)
print("Site rebuild complete.")
