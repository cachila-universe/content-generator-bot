"""Static site publisher that renders Jinja2 templates and writes HTML files."""

import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timezone

from core import analytics_tracker

logger = logging.getLogger(__name__)

# Resolve paths relative to project root
_PROJECT_ROOT = Path(__file__).parent.parent
_TEMPLATES_DIR = _PROJECT_ROOT / "site" / "templates"
_OUTPUT_DIR = _PROJECT_ROOT / "site" / "output"


def publish(article: dict, niche_id: str, niche_name: str, settings: dict, db_path: Path) -> str:
    """
    Render article to static HTML and publish to site/output/.

    Returns URL path of the published article.
    """
    slug = article.get("slug", "untitled")
    site_url = settings.get("site_url", "http://localhost:8080")

    # Ensure output directory exists
    niche_output_dir = _OUTPUT_DIR / niche_id
    niche_output_dir.mkdir(parents=True, exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=True,
    )

    # Render the post template
    try:
        template = env.get_template("post.html")
    except Exception as exc:
        logger.error("Could not load post.html template: %s", exc)
        return ""

    rendered = template.render(
        article=article,
        niche_id=niche_id,
        niche_name=niche_name,
        site_url=site_url,
        settings=settings,
        published_at=article.get("published_at", datetime.now(timezone.utc).isoformat()),
    )

    # Write post HTML file
    output_file = niche_output_dir / f"{slug}.html"
    try:
        output_file.write_text(rendered, encoding="utf-8")
        logger.info("Published post: %s", output_file)
    except Exception as exc:
        logger.error("Failed to write post HTML: %s", exc)
        return ""

    url_path = f"/{niche_id}/{slug}.html"

    # Save to database
    avg_commission = float(settings.get("analytics", {}).get("avg_commission_value", 25.0))
    estimated_ctr = float(settings.get("analytics", {}).get("estimated_ctr", 0.02))
    word_count = article.get("word_count", 0)
    affiliate_count = article.get("affiliate_links_count", 0)
    estimated_clicks = int(word_count * estimated_ctr)
    estimated_income = round(estimated_clicks * avg_commission * estimated_ctr, 2)

    analytics_tracker.save_post(
        db_path,
        {
            "niche_id": niche_id,
            "niche_name": niche_name,
            "title": article.get("title", ""),
            "slug": slug,
            "url": f"{site_url.rstrip('/')}{url_path}",
            "youtube_url": article.get("youtube_url", ""),
            "word_count": word_count,
            "affiliate_links_count": affiliate_count,
            "estimated_clicks": estimated_clicks,
            "estimated_income": estimated_income,
            "status": "published",
        },
    )

    analytics_tracker.log_action(
        db_path,
        level="SUCCESS",
        action="publish_post",
        message=f"Published: {article.get('title', slug)}",
        niche_id=niche_id,
    )

    # Rebuild homepage
    _rebuild_index(env, settings, db_path, site_url)

    return url_path


def _rebuild_index(env: Environment, settings: dict, db_path: Path, site_url: str) -> None:
    """Rebuild the site homepage index.html."""
    try:
        all_posts = analytics_tracker.get_all_posts(db_path)
        template = env.get_template("index.html")
        rendered = template.render(
            posts=all_posts,
            settings=settings,
            site_url=site_url,
            site_title=settings.get("site", {}).get("title", "TechLife Insights"),
            tagline=settings.get("site", {}).get("tagline", "Smart Guides for Modern Living"),
        )
        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (_OUTPUT_DIR / "index.html").write_text(rendered, encoding="utf-8")
        logger.info("Rebuilt site index.html (%d posts)", len(all_posts))
    except Exception as exc:
        logger.warning("Could not rebuild index.html: %s", exc)
