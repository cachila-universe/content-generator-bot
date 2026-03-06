"""APScheduler-based job scheduler with bot state management, anti-spam, and content dedup."""

import json
import random
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_TRENDS_CACHE = _PROJECT_ROOT / "data" / "trends_cache.json"

# Global reference so the dashboard can access it
_scheduler_instance = None


def get_scheduler():
    """Return the running scheduler instance (for dashboard status display)."""
    return _scheduler_instance


def start_scheduler(config: dict, db_path: Path) -> None:
    """
    Start the APScheduler with all content generation jobs.
    Respects bot_state for start/stop, niche toggles, and rate limits.
    """
    global _scheduler_instance

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except ImportError:
        logger.error("APScheduler not installed. Run: pip install APScheduler")
        return

    from core import bot_state

    niches_config = config.get("niches", {})
    settings = config.get("settings", {})
    site_url = settings.get("site_url", "http://localhost:8080")
    tz = settings.get("scheduler", {}).get("timezone", "America/New_York")

    avg_commission = float(settings.get("analytics", {}).get("avg_commission_value", 25.0))
    estimated_ctr = float(settings.get("analytics", {}).get("estimated_ctr", 0.02))

    # Initialize bot state with niches
    state = bot_state.init_state(niches_config)

    scheduler = BackgroundScheduler(timezone=tz)
    _scheduler_instance = scheduler

    # --- Job 1: Fetch trends daily at 8:00 AM ---
    scheduler.add_job(
        job_fetch_trends,
        trigger="cron",
        hour=8,
        minute=0,
        args=[niches_config],
        id="fetch_trends",
        name="Fetch Trending Topics",
        replace_existing=True,
    )

    # --- Per-niche content jobs ---
    for niche_id, niche_cfg in niches_config.items():
        post_hour = niche_cfg.get("post_schedule_hour", 9)
        post_minute = niche_cfg.get("post_schedule_minute", 0)
        video_hour = niche_cfg.get("video_schedule_hour", 11)
        video_minute = niche_cfg.get("video_schedule_minute", 0)

        # Blog post job
        scheduler.add_job(
            job_generate_and_publish,
            trigger="cron",
            hour=post_hour,
            minute=post_minute,
            args=[niche_id, niche_cfg, settings, db_path, site_url],
            id=f"post_{niche_id}",
            name=f"Post: {niche_cfg.get('name', niche_id)}",
            replace_existing=True,
        )

        # YouTube Shorts job
        scheduler.add_job(
            job_generate_and_upload_short,
            trigger="cron",
            hour=video_hour,
            minute=video_minute,
            args=[niche_id, niche_cfg, settings, db_path],
            id=f"short_{niche_id}",
            name=f"Short: {niche_cfg.get('name', niche_id)}",
            replace_existing=True,
        )

        # Pinterest job
        pinterest_hour = niche_cfg.get("pinterest_schedule_hour", 12)
        pinterest_minute = niche_cfg.get("pinterest_schedule_minute", 0)
        scheduler.add_job(
            job_post_to_pinterest,
            trigger="cron",
            hour=pinterest_hour,
            minute=pinterest_minute,
            args=[niche_id, niche_cfg, settings, db_path, site_url],
            id=f"pinterest_{niche_id}",
            name=f"Pinterest: {niche_cfg.get('name', niche_id)}",
            replace_existing=True,
        )

    # --- Rebuild site every Sunday ---
    scheduler.add_job(
        job_rebuild_site,
        trigger="cron",
        day_of_week="sun",
        hour=0,
        minute=0,
        args=[settings, db_path, site_url],
        id="rebuild_site",
        name="Rebuild Static Site",
        replace_existing=True,
    )

    # --- Income snapshot every hour ---
    scheduler.add_job(
        job_take_snapshot,
        trigger="interval",
        hours=1,
        args=[db_path, avg_commission, estimated_ctr],
        id="income_snapshot",
        name="Income Snapshot",
        replace_existing=True,
    )

    # --- Check manual trigger queue every 30 seconds ---
    scheduler.add_job(
        job_check_manual_triggers,
        trigger="interval",
        seconds=30,
        args=[niches_config, settings, db_path, site_url],
        id="manual_trigger_check",
        name="Check Manual Triggers",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    # Auto-start the bot
    bot_state.set_bot_running(True)

    # Bootstrap: if posts table is empty, run one full cycle immediately
    if _is_posts_empty(db_path):
        logger.info("No posts found — running bootstrap cycle")
        job_fetch_trends(niches_config)
        for niche_id, niche_cfg in niches_config.items():
            if bot_state.is_niche_enabled(niche_id):
                job_generate_and_publish(niche_id, niche_cfg, settings, db_path, site_url)

    # Block until Ctrl+C
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        bot_state.set_bot_running(False)
        scheduler.shutdown()
        logger.info("Scheduler stopped")


# ── Anti-spam delay ──────────────────────────────────────────────────────────


def _human_delay():
    """Add random delay (30-180 sec) to mimic human behavior."""
    import time
    delay = random.randint(30, 180)
    logger.debug("Anti-spam delay: %d seconds", delay)
    time.sleep(delay)


# ── Job implementations ─────────────────────────────────────────────────────


def job_fetch_trends(niches_config: dict) -> None:
    """Fetch and cache trending topics for all enabled niches."""
    from core import trend_finder, analytics_tracker, bot_state

    db_path = _PROJECT_ROOT / "data" / "bot.db"
    trends_data = {}

    for niche_id, niche_cfg in niches_config.items():
        if not bot_state.is_niche_enabled(niche_id):
            continue
        try:
            topics = trend_finder.get_trending_topics(niche_id, niche_cfg, db_path)
            trends_data[niche_id] = topics
            logger.info("Fetched %d topics for %s", len(topics), niche_id)
        except Exception as exc:
            logger.warning("Trend fetch failed for %s: %s", niche_id, exc)
            trends_data[niche_id] = niche_cfg.get("seed_keywords", [])[:5]

        # Anti-spam: stagger pytrends requests
        import time
        time.sleep(random.randint(2, 5))

    _TRENDS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    _TRENDS_CACHE.write_text(json.dumps(trends_data, indent=2))
    logger.info("Trends cache updated: %s", _TRENDS_CACHE)


def job_generate_and_publish(
    niche_id: str,
    niche_cfg: dict,
    settings: dict,
    db_path: Path,
    site_url: str,
) -> None:
    """Full pipeline: check state → fetch topic → dedup → write → inject → SEO → publish."""
    from core import (
        trend_finder,
        llm_writer,
        affiliate_injector,
        seo_optimizer,
        publisher,
        analytics_tracker,
        bot_state,
        content_guard,
    )

    # Gate: check bot state and rate limits
    allowed, reason = bot_state.can_post_now(niche_id)
    if not allowed:
        logger.info("Skipping post for %s: %s", niche_id, reason)
        return

    # Check platform enabled
    if not bot_state.is_platform_enabled("blog"):
        logger.info("Blog platform disabled, skipping post for %s", niche_id)
        return

    # Anti-spam: random delay before starting
    _human_delay()

    output_dir = _PROJECT_ROOT / "site" / "output"
    niche_name = niche_cfg.get("name", niche_id)

    analytics_tracker.log_action(
        db_path, "INFO", "pipeline_start", f"Starting pipeline for {niche_name}", niche_id
    )

    try:
        # 1. Pick a non-duplicate topic
        topic = _pick_unique_topic(niche_id, niche_cfg, db_path)
        if not topic:
            analytics_tracker.log_action(
                db_path, "WARNING", "no_topic", "No new unique topic found, skipping", niche_id
            )
            return

        analytics_tracker.log_action(
            db_path, "INFO", "topic_selected", f"Topic: {topic}", niche_id
        )

        # 2. Generate article
        article = llm_writer.generate_article(topic, niche_cfg)
        if not article:
            analytics_tracker.log_action(
                db_path, "ERROR", "llm_failed", "LLM generation failed", niche_id
            )
            return

        # 3. Check content isn't duplicate
        if content_guard.is_duplicate_content(db_path, article.get("html_content", "")):
            analytics_tracker.log_action(
                db_path, "WARNING", "duplicate_content", "Generated content was duplicate, skipping", niche_id
            )
            return

        analytics_tracker.log_action(
            db_path, "INFO", "article_generated",
            f"Generated: {article.get('title')} ({article.get('word_count')} words)", niche_id
        )

        # 4. Inject affiliate links
        dashboard_url = f"http://localhost:{settings.get('dashboard', {}).get('port', 5000)}"
        html_with_links, links_count = affiliate_injector.inject_links(
            article["html_content"], niche_cfg, dashboard_url
        )
        article["html_content"] = html_with_links
        article["affiliate_links_count"] = links_count

        # 5. SEO optimize
        article = seo_optimizer.optimize(article, niche_id, niche_cfg, site_url, output_dir)

        # 6. Publish to static site
        url_path = publisher.publish(article, niche_id, niche_name, settings, db_path)

        # 7. Record content fingerprint
        content_guard.record_content(
            db_path, niche_id, topic,
            article.get("title", ""), article.get("html_content", "")
        )

        # 8. Record run for rate limiting
        bot_state.record_post_run(niche_id)

        analytics_tracker.log_action(
            db_path, "SUCCESS", "post_published",
            f"Published '{article.get('title')}' → {url_path}", niche_id
        )

    except Exception as exc:
        logger.error("Pipeline error for %s: %s", niche_id, exc)
        analytics_tracker.log_action(
            db_path, "ERROR", "pipeline_error", f"Pipeline error: {exc}", niche_id, error=str(exc)
        )


def job_generate_and_upload_short(
    niche_id: str,
    niche_cfg: dict,
    settings: dict,
    db_path: Path,
) -> None:
    """Get latest post → generate YouTube Short → upload."""
    from core import shorts_generator, youtube_uploader, analytics_tracker, bot_state

    if not bot_state.is_bot_running():
        return
    if not bot_state.is_niche_enabled(niche_id):
        return
    if not bot_state.is_platform_enabled("youtube_shorts"):
        return
    if not settings.get("video", {}).get("enabled", True):
        return

    _human_delay()

    channel_name = settings.get("youtube_channel_name", "TechLife Insights")

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM posts WHERE niche_id = ? AND (youtube_url IS NULL OR youtube_url = '') "
            "ORDER BY published_at DESC LIMIT 1",
            (niche_id,),
        ).fetchone()
        conn.close()

        if not row:
            return

        post = dict(row)
        article = {
            "title": post["title"],
            "html_content": "",
            "meta_description": "",
            "tags": [],
            "slug": post["slug"],
        }

        # Load HTML content
        html_path = _PROJECT_ROOT / "site" / "output" / niche_id / f"{post['slug']}.html"
        if html_path.exists():
            from bs4 import BeautifulSoup
            full_html = html_path.read_text(encoding="utf-8")
            soup = BeautifulSoup(full_html, "lxml")
            main = soup.find("article") or soup.find("main") or soup.find("body")
            article["html_content"] = str(main) if main else full_html

        output_dir = _PROJECT_ROOT / "site" / "output" / niche_id
        output_dir.mkdir(parents=True, exist_ok=True)
        video_path = output_dir / f"{post['slug']}_short.mp4"

        analytics_tracker.log_action(
            db_path, "INFO", "short_start", f"Generating Short for: {post['title']}", niche_id
        )

        result = shorts_generator.generate_short(article, video_path)
        if not result:
            analytics_tracker.log_action(
                db_path, "ERROR", "short_failed", f"Short generation failed: {post['title']}", niche_id
            )
            return

        youtube_url = youtube_uploader.upload_video(video_path, article, niche_cfg, channel_name)

        if youtube_url:
            conn = sqlite3.connect(str(db_path))
            conn.execute("UPDATE posts SET youtube_url = ? WHERE slug = ?", (youtube_url, post["slug"]))
            conn.commit()
            conn.close()
            analytics_tracker.log_action(
                db_path, "SUCCESS", "short_uploaded", f"Short uploaded: {youtube_url}", niche_id
            )
        else:
            analytics_tracker.log_action(
                db_path, "INFO", "short_generated",
                f"Short generated locally: {video_path}", niche_id
            )

    except Exception as exc:
        logger.error("Short job error for %s: %s", niche_id, exc)
        analytics_tracker.log_action(
            db_path, "ERROR", "short_error", f"Short error: {exc}", niche_id, error=str(exc)
        )


def job_post_to_pinterest(
    niche_id: str,
    niche_cfg: dict,
    settings: dict,
    db_path: Path,
    site_url: str,
) -> None:
    """Create a Pinterest pin for the latest published post."""
    from core import pinterest_poster, analytics_tracker, bot_state

    if not bot_state.is_bot_running():
        return
    if not bot_state.is_niche_enabled(niche_id):
        return
    if not bot_state.is_platform_enabled("pinterest"):
        return

    _human_delay()

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM posts WHERE niche_id = ? ORDER BY published_at DESC LIMIT 1",
            (niche_id,),
        ).fetchone()
        conn.close()

        if not row:
            return

        post = dict(row)
        article = {
            "title": post["title"],
            "slug": post["slug"],
            "niche_id": niche_id,
            "meta_description": post.get("meta_description", ""),
            "tags": [],
        }

        analytics_tracker.log_action(
            db_path, "INFO", "pinterest_start",
            f"Creating Pinterest pin for: {post['title']}", niche_id
        )

        pin_url = pinterest_poster.create_pin(article, niche_cfg, site_url)

        if pin_url:
            analytics_tracker.log_action(
                db_path, "SUCCESS", "pinterest_posted", f"Pin created: {pin_url}", niche_id
            )
        else:
            analytics_tracker.log_action(
                db_path, "INFO", "pinterest_skipped", "Pinterest not configured", niche_id
            )
    except Exception as exc:
        logger.error("Pinterest error for %s: %s", niche_id, exc)
        analytics_tracker.log_action(
            db_path, "ERROR", "pinterest_error", f"Pinterest error: {exc}", niche_id, error=str(exc)
        )


def job_check_manual_triggers(
    niches_config: dict,
    settings: dict,
    db_path: Path,
    site_url: str,
) -> None:
    """Check and execute any queued manual trigger requests."""
    from core import bot_state

    trigger = bot_state.pop_manual_trigger()
    if not trigger:
        return

    niche_id = trigger.get("niche_id", "")
    platforms = trigger.get("platforms", ["blog"])
    niche_cfg = niches_config.get(niche_id)
    if not niche_cfg:
        logger.warning("Manual trigger: unknown niche '%s'", niche_id)
        return

    logger.info("Executing manual trigger for %s: %s", niche_id, platforms)

    # Temporarily force bot running for manual triggers
    state = bot_state.load_state()
    was_running = state.get("bot_running", False)
    state["bot_running"] = True
    bot_state.save_state(state)

    try:
        if "blog" in platforms:
            job_generate_and_publish(niche_id, niche_cfg, settings, db_path, site_url)
        if "youtube_shorts" in platforms:
            job_generate_and_upload_short(niche_id, niche_cfg, settings, db_path)
        if "pinterest" in platforms:
            job_post_to_pinterest(niche_id, niche_cfg, settings, db_path, site_url)
    finally:
        state = bot_state.load_state()
        state["bot_running"] = was_running
        bot_state.save_state(state)


def job_rebuild_site(settings: dict, db_path: Path, site_url: str) -> None:
    """Rebuild the entire static site index."""
    from core import analytics_tracker
    from jinja2 import Environment, FileSystemLoader

    try:
        all_posts = analytics_tracker.get_all_posts(db_path)
        env = Environment(
            loader=FileSystemLoader(str(_PROJECT_ROOT / "site" / "templates")),
            autoescape=True,
        )
        template = env.get_template("index.html")
        rendered = template.render(
            posts=all_posts,
            settings=settings,
            site_url=site_url,
            site_title=settings.get("site", {}).get("title", "TechLife Insights"),
            tagline=settings.get("site", {}).get("tagline", "Smart Guides for Modern Living"),
        )
        (_PROJECT_ROOT / "site" / "output" / "index.html").write_text(rendered, encoding="utf-8")
        logger.info("Site rebuilt with %d posts", len(all_posts))
        analytics_tracker.log_action(db_path, "INFO", "rebuild_site", f"Rebuilt with {len(all_posts)} posts")
    except Exception as exc:
        logger.error("Site rebuild failed: %s", exc)


def job_take_snapshot(db_path: Path, avg_commission: float, estimated_ctr: float) -> None:
    """Take hourly income snapshot."""
    from core import analytics_tracker

    try:
        analytics_tracker.take_income_snapshot(db_path, avg_commission, estimated_ctr)
    except Exception as exc:
        logger.warning("Snapshot failed: %s", exc)


# ── Helpers ─────────────────────────────────────────────────────────────────


def _pick_unique_topic(niche_id: str, niche_cfg: dict, db_path: Path) -> str:
    """Pick a topic that hasn't been covered before (using content_guard)."""
    from core import content_guard

    candidates = []

    # Try trends cache first
    if _TRENDS_CACHE.exists():
        try:
            trends = json.loads(_TRENDS_CACHE.read_text())
            candidates.extend(trends.get(niche_id, []))
        except Exception:
            pass

    # Add seed keywords as fallback
    candidates.extend(niche_cfg.get("seed_keywords", []))

    existing_titles = _get_existing_titles(db_path)

    for topic in candidates:
        if topic.lower() in {t.lower() for t in existing_titles}:
            continue
        if content_guard.is_duplicate_topic(db_path, niche_id, topic):
            continue
        return topic

    logger.warning("All topics exhausted for niche %s", niche_id)
    return ""


def _get_existing_titles(db_path: Path) -> list:
    """Get list of already-published post titles."""
    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT title FROM posts").fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []


def _is_posts_empty(db_path: Path) -> bool:
    """Check if the posts table is empty."""
    try:
        conn = sqlite3.connect(str(db_path))
        count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        conn.close()
        return count == 0
    except Exception:
        return True
