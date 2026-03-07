"""Regenerate all static site pages from templates."""
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from core import analytics_tracker

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "site" / "templates"
OUTPUT_DIR = PROJECT_ROOT / "site" / "output"
DB_PATH = PROJECT_ROOT / "data" / "bot.db"


def main():
    # Load configs
    with open(PROJECT_ROOT / "config" / "settings.yaml") as f:
        settings = yaml.safe_load(f)
    with open(PROJECT_ROOT / "config" / "niches.yaml") as f:
        niches = yaml.safe_load(f).get("niches", {})

    site_title = settings.get("site", {}).get("title", "TechLife Insights")
    tagline = settings.get("site", {}).get("tagline", "Smart Guides for Modern Living")
    site_url = "https://tech-life-insights.com"

    # Get posts from DB (may be empty)
    try:
        all_posts = analytics_tracker.get_all_posts(DB_PATH)
    except Exception as e:
        print(f"No DB or posts yet: {e}")
        all_posts = []

    print(f"Found {len(all_posts)} posts")
    print(f"Niches: {list(niches.keys())}")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

    # 1. Build homepage
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tpl = env.get_template("index.html")
    html = tpl.render(
        posts=all_posts, settings=settings, site_url=site_url,
        niches=niches, site_title=site_title, tagline=tagline,
    )
    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print("Built: site/output/index.html")

    # 2. Build niche index pages
    tpl_niche = env.get_template("niche_index.html")
    for niche_id, niche_cfg in niches.items():
        if not niche_cfg.get("enabled", False):
            continue
        niche_posts = [p for p in all_posts if p.get("niche_id") == niche_id]
        niche_dir = OUTPUT_DIR / niche_id
        niche_dir.mkdir(parents=True, exist_ok=True)
        html = tpl_niche.render(
            niche_id=niche_id, niche_name=niche_cfg.get("name", niche_id),
            posts=niche_posts, niches=niches, settings=settings,
            site_url=site_url, site_title=site_title, tagline=tagline,
        )
        (niche_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"Built: site/output/{niche_id}/index.html ({len(niche_posts)} posts)")

    print("\nAll pages generated!")


if __name__ == "__main__":
    main()
