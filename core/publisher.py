"""Static site publisher that renders Jinja2 templates and writes HTML files."""

import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timezone

import yaml

from core import analytics_tracker

logger = logging.getLogger(__name__)

# Resolve paths relative to project root
_PROJECT_ROOT = Path(__file__).parent.parent
_TEMPLATES_DIR = _PROJECT_ROOT / "site" / "templates"
_OUTPUT_DIR = _PROJECT_ROOT / "site" / "output"
_NICHES_PATH = _PROJECT_ROOT / "config" / "niches.yaml"


def _load_niches() -> dict:
    """Load niche configuration from config/niches.yaml."""
    try:
        with open(_NICHES_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("niches", {})
    except Exception as exc:
        logger.warning("Could not load niches.yaml: %s", exc)
        return {}


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
        niches=_load_niches(),
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

    # Save to database — income is tracked via income_tracker.py, NOT estimated here
    word_count = article.get("word_count", 0)
    affiliate_count = article.get("affiliate_links_count", 0)

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
            "estimated_clicks": 0,
            "estimated_income": 0.0,
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

    # Rebuild homepage and niche index pages
    _rebuild_index(env, settings, db_path, site_url)
    _rebuild_niche_indexes(env, settings, db_path, site_url)
    _rebuild_best_of_pages(env, settings, db_path, site_url)
    _rebuild_legal_pages(env, settings, site_url)

    return url_path


def _rebuild_index(env: Environment, settings: dict, db_path: Path, site_url: str) -> None:
    """Rebuild the site homepage index.html."""
    try:
        all_posts = analytics_tracker.get_all_posts(db_path)
        niches = _load_niches()
        template = env.get_template("index.html")
        rendered = template.render(
            posts=all_posts,
            settings=settings,
            site_url=site_url,
            niches=niches,
            site_title=settings.get("site", {}).get("title", "TechLife Insights"),
            tagline=settings.get("site", {}).get("tagline", "Smart Guides for Modern Living"),
        )
        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (_OUTPUT_DIR / "index.html").write_text(rendered, encoding="utf-8")
        logger.info("Rebuilt site index.html (%d posts)", len(all_posts))
    except Exception as exc:
        logger.warning("Could not rebuild index.html: %s", exc)


def _rebuild_niche_indexes(env: Environment, settings: dict, db_path: Path, site_url: str) -> None:
    """Rebuild per-niche index pages (e.g. /ai_tools/index.html)."""
    try:
        niches = _load_niches()
        all_posts = analytics_tracker.get_all_posts(db_path)
        template = env.get_template("niche_index.html")
        site_title = settings.get("site", {}).get("title", "TechLife Insights")
        tagline = settings.get("site", {}).get("tagline", "Smart Guides for Modern Living")

        for niche_id, niche_cfg in niches.items():
            if not niche_cfg.get("enabled", False):
                continue

            niche_posts = [p for p in all_posts if p.get("niche_id") == niche_id]
            niche_output_dir = _OUTPUT_DIR / niche_id
            niche_output_dir.mkdir(parents=True, exist_ok=True)

            rendered = template.render(
                niche_id=niche_id,
                niche_name=niche_cfg.get("name", niche_id),
                posts=niche_posts,
                niches=niches,
                settings=settings,
                site_url=site_url,
                site_title=site_title,
                tagline=tagline,
            )

            (niche_output_dir / "index.html").write_text(rendered, encoding="utf-8")
            logger.info("Rebuilt niche index: %s (%d posts)", niche_id, len(niche_posts))

    except Exception as exc:
        logger.warning("Could not rebuild niche indexes: %s", exc)


def _rebuild_best_of_pages(env: Environment, settings: dict, db_path: Path, site_url: str) -> None:
    """Rebuild per-niche 'Best Of' roundup pages."""
    try:
        niches = _load_niches()
        all_posts = analytics_tracker.get_all_posts(db_path)
        template = env.get_template("best_of.html")
        site_title = settings.get("site", {}).get("title", "TechLife Insights")
        tagline = settings.get("site", {}).get("tagline", "Smart Guides for Modern Living")

        for niche_id, niche_cfg in niches.items():
            if not niche_cfg.get("enabled", False):
                continue
            niche_posts = [p for p in all_posts if p.get("niche_id") == niche_id]
            if not niche_posts:
                continue
            niche_output_dir = _OUTPUT_DIR / niche_id
            niche_output_dir.mkdir(parents=True, exist_ok=True)
            rendered = template.render(
                niche_id=niche_id, niche_name=niche_cfg.get("name", niche_id),
                posts=niche_posts, niches=niches, settings=settings,
                site_url=site_url, site_title=site_title, tagline=tagline,
            )
            (niche_output_dir / "best-of.html").write_text(rendered, encoding="utf-8")
    except Exception as exc:
        logger.warning("Could not rebuild best-of pages: %s", exc)


def _rebuild_legal_pages(env: Environment, settings: dict, site_url: str) -> None:
    """Rebuild static legal pages (privacy, about, contact)."""
    try:
        niches = _load_niches()
        site_title = settings.get("site", {}).get("title", "TechLife Insights")
        tagline = settings.get("site", {}).get("tagline", "Smart Guides for Modern Living")
        current_date = datetime.now(timezone.utc).strftime("%B %d, %Y")

        for page in ["privacy.html", "about.html", "contact.html"]:
            try:
                template = env.get_template(page)
                rendered = template.render(
                    niches=niches, settings=settings, site_url=site_url,
                    site_title=site_title, tagline=tagline,
                    current_date=current_date,
                )
                _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                (_OUTPUT_DIR / page).write_text(rendered, encoding="utf-8")
            except Exception:
                pass  # Template may not exist yet
    except Exception as exc:
        logger.warning("Could not rebuild legal pages: %s", exc)


def rebuild_site(settings: dict, db_path: Path, site_url: str) -> None:
    """Rebuild all static site pages. Call after any content change (e.g. delete)."""
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=True,
    )
    _rebuild_index(env, settings, db_path, site_url)
    _rebuild_niche_indexes(env, settings, db_path, site_url)
    _rebuild_best_of_pages(env, settings, db_path, site_url)
    _rebuild_legal_pages(env, settings, site_url)
