"""
Dependency-aware scheduler with bot modes, Twitter posting, and trend intelligence.

Bot Modes:
  • PAUSED    — bot is active but does nothing (all jobs skip)
  • SCHEDULED — follows the normal cron schedule
  • MANUAL    — waits for manual trigger; runs the FULL pipeline in order

Pipeline dependency order (manual mode runs all of these sequentially):
  1. Trend Intelligence  — scan Google Trends, Reddit, HackerNews
  2. Articles            — generate + publish blog posts
  3. Stock Images        — generate AI images for articles/videos
  4. Videos / Shorts     — create video from latest article
  5. Social Posts        — tweet article + video to Twitter
  6. Pinterest           — create pin for latest post
"""

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
    Respects bot_state modes: paused → skip all, scheduled → cron, manual → on-demand.
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

    # ── Job 1: Trend Intelligence (6:00 AM daily) ────────────────────────
    scheduler.add_job(
        job_refresh_intelligence,
        trigger="cron",
        hour=6,
        minute=0,
        args=[niches_config, settings],
        id="refresh_intelligence",
        name="🧠 Trend Intelligence",
        replace_existing=True,
    )

    # ── Job 2: Fetch Google Trends (8:00 AM daily) ───────────────────────
    scheduler.add_job(
        job_fetch_trends,
        trigger="cron",
        hour=8,
        minute=0,
        args=[niches_config],
        id="fetch_trends",
        name="📊 Fetch Trending Topics",
        replace_existing=True,
    )

    # ── Per-niche content jobs ───────────────────────────────────────────
    for niche_id, niche_cfg in niches_config.items():
        post_hour = niche_cfg.get("post_schedule_hour", 9)
        post_minute = niche_cfg.get("post_schedule_minute", 0)
        video_hour = niche_cfg.get("video_schedule_hour", 11)
        video_minute = niche_cfg.get("video_schedule_minute", 0)

        # Blog post + stock images job
        scheduler.add_job(
            job_generate_and_publish,
            trigger="cron",
            hour=post_hour,
            minute=post_minute,
            args=[niche_id, niche_cfg, settings, db_path, site_url],
            id=f"post_{niche_id}",
            name=f"📝 Post: {niche_cfg.get('name', niche_id)}",
            replace_existing=True,
        )

        # YouTube Shorts job (depends on articles existing)
        scheduler.add_job(
            job_generate_and_upload_short,
            trigger="cron",
            hour=video_hour,
            minute=video_minute,
            args=[niche_id, niche_cfg, settings, db_path],
            id=f"short_{niche_id}",
            name=f"🎬 Short: {niche_cfg.get('name', niche_id)}",
            replace_existing=True,
        )

        # Twitter post job (runs 30min after article)
        scheduler.add_job(
            job_post_to_twitter,
            trigger="cron",
            hour=post_hour,
            minute=(post_minute + 30) % 60,
            args=[niche_id, niche_cfg, settings, db_path, site_url],
            id=f"twitter_{niche_id}",
            name=f"🐦 Tweet: {niche_cfg.get('name', niche_id)}",
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
            name=f"📌 Pinterest: {niche_cfg.get('name', niche_id)}",
            replace_existing=True,
        )

    # ── Stock image batch job (2:00 PM daily) ────────────────────────────
    scheduler.add_job(
        job_generate_stock_images,
        trigger="cron",
        hour=14,
        minute=0,
        args=[niches_config, settings],
        id="stock_images",
        name="🖼️ Stock Image Generation",
        replace_existing=True,
    )

    # ── Rebuild site every Sunday ────────────────────────────────────────
    scheduler.add_job(
        job_rebuild_site,
        trigger="cron",
        day_of_week="sun",
        hour=0,
        minute=0,
        args=[settings, db_path, site_url],
        id="rebuild_site",
        name="🔄 Rebuild Static Site",
        replace_existing=True,
    )

    # ── Income snapshot every hour ───────────────────────────────────────
    scheduler.add_job(
        job_take_snapshot,
        trigger="interval",
        hours=1,
        args=[db_path, avg_commission, estimated_ctr],
        id="income_snapshot",
        name="💰 Income Snapshot",
        replace_existing=True,
    )

    # ── Check manual trigger queue every 30 seconds ──────────────────────
    scheduler.add_job(
        job_check_manual_triggers,
        trigger="interval",
        seconds=30,
        args=[niches_config, settings, db_path, site_url],
        id="manual_trigger_check",
        name="⚡ Check Manual Triggers",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    # Auto-start the bot in scheduled mode
    bot_state.set_bot_running(True)
    if not bot_state.get_bot_mode() in ("paused", "manual"):
        bot_state.set_bot_mode("scheduled")

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


def _should_run(job_name: str = "") -> bool:
    """Check if the current bot mode allows scheduled jobs to run."""
    from core import bot_state
    if not bot_state.should_execute_scheduled_job():
        mode = bot_state.get_bot_mode()
        logger.debug("Skipping %s — bot mode is '%s'", job_name, mode)
        return False
    return True


# ── Job implementations ─────────────────────────────────────────────────────


def job_refresh_intelligence(niches_config: dict, settings: dict) -> None:
    """Refresh trend intelligence from all sources — feeds into everything else."""
    if not _should_run("intelligence"):
        return

    from core import bot_state
    if not bot_state.is_bot_running():
        return

    try:
        from core import trend_intelligence, analytics_tracker
        db_path = _PROJECT_ROOT / "data" / "bot.db"

        analytics_tracker.log_action(
            db_path, "INFO", "intelligence_start", "Starting trend intelligence refresh"
        )

        summary = trend_intelligence.refresh_all_intelligence(niches_config, force=False)

        analytics_tracker.log_action(
            db_path, "SUCCESS", "intelligence_done",
            f"Intelligence refresh: {summary.get('total_topics', 0)} topics from "
            f"{len(summary.get('sources', []))} sources"
        )
    except Exception as exc:
        logger.error("Intelligence refresh failed: %s", exc)


def job_fetch_trends(niches_config: dict) -> None:
    """Fetch and cache trending topics for all enabled niches."""
    if not _should_run("trends"):
        return

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
            trends_data[niche_id] = [
                {"topic": kw, "subtopic_id": ""} for kw in niche_cfg.get("seed_keywords", [])[:5]
            ]

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
    if not _should_run(f"post_{niche_id}"):
        return

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
        # 1. Pick a non-duplicate topic (returns dict with topic + subtopic_id)
        topic_data = _pick_unique_topic(niche_id, niche_cfg, db_path)
        if not topic_data or not topic_data.get("topic"):
            analytics_tracker.log_action(
                db_path, "WARNING", "no_topic", "No new unique topic found, skipping", niche_id
            )
            return

        topic = topic_data["topic"]
        subtopic_id = topic_data.get("subtopic_id", "")

        analytics_tracker.log_action(
            db_path, "INFO", "topic_selected",
            f"Topic: {topic} (subtopic: {subtopic_id or 'general'})", niche_id
        )

        # 2. Generate article (with trend-intelligent style + subtopic context)
        article = llm_writer.generate_article(
            topic, niche_cfg, niche_id=niche_id, subtopic_id=subtopic_id
        )
        if not article:
            analytics_tracker.log_action(
                db_path, "ERROR", "llm_failed", "LLM generation failed", niche_id
            )
            return

        # Ensure subtopic_id is on the article
        if not article.get("subtopic_id"):
            article["subtopic_id"] = subtopic_id

        # 3. Check content isn't duplicate
        if content_guard.is_duplicate_content(db_path, article.get("html_content", "")):
            analytics_tracker.log_action(
                db_path, "WARNING", "duplicate_content", "Generated content was duplicate, skipping", niche_id
            )
            return

        style_used = article.get("writing_style", "default")
        analytics_tracker.log_action(
            db_path, "INFO", "article_generated",
            f"Generated: {article.get('title')} ({article.get('word_count')} words, style: {style_used})", niche_id
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

        # 9. Record style performance for learning
        try:
            from core.trend_intelligence import record_style_performance
            record_style_performance(style_used, "writing", niche_id, 70)  # Base score, updated later with real metrics
        except Exception:
            pass

        # 10. Record article performance for content intelligence
        try:
            from core.content_intelligence import record_article_performance
            record_article_performance(
                niche_id=niche_id,
                subtopic_id=subtopic_id,
                format_id=style_used,
                word_count=article.get("word_count", 0),
                affiliate_count=article.get("affiliate_links_count", 0),
            )
        except Exception:
            pass

        analytics_tracker.log_action(
            db_path, "SUCCESS", "post_published",
            f"Published '{article.get('title')}' → {url_path} [subtopic={subtopic_id or 'general'}]",
            niche_id,
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
    if not _should_run(f"short_{niche_id}"):
        return

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

        # Also tweet the video if Twitter is enabled
        _maybe_tweet_video(niche_id, niche_cfg, settings, db_path, video_path, post)

    except Exception as exc:
        logger.error("Short job error for %s: %s", niche_id, exc)
        analytics_tracker.log_action(
            db_path, "ERROR", "short_error", f"Short error: {exc}", niche_id, error=str(exc)
        )


def job_post_to_twitter(
    niche_id: str,
    niche_cfg: dict,
    settings: dict,
    db_path: Path,
    site_url: str,
) -> None:
    """Tweet the latest published article."""
    if not _should_run(f"twitter_{niche_id}"):
        return

    from core import bot_state, analytics_tracker

    if not bot_state.is_bot_running():
        return
    if not bot_state.is_niche_enabled(niche_id):
        return
    if not bot_state.is_platform_enabled("twitter"):
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

        # Build article URL
        slug = post.get("slug", "")
        article_url = f"{site_url.rstrip('/')}/{niche_id}/{slug}.html"

        article = {
            "title": post["title"],
            "url": article_url,
            "niche_id": niche_id,
            "meta_description": post.get("meta_description", ""),
        }

        from core.social_poster import SocialPoster
        poster = SocialPoster(settings)

        if poster.twitter.enabled:
            tweet_id = poster.twitter.post_article(article)
            if tweet_id:
                analytics_tracker.log_action(
                    db_path, "SUCCESS", "tweet_posted",
                    f"Tweet posted for '{post['title']}': {tweet_id}", niche_id
                )
            else:
                analytics_tracker.log_action(
                    db_path, "WARNING", "tweet_failed",
                    f"Tweet failed for '{post['title']}'", niche_id
                )
        else:
            logger.debug("Twitter not configured, skipping tweet for %s", niche_id)

    except Exception as exc:
        logger.error("Twitter job error for %s: %s", niche_id, exc)
        analytics_tracker.log_action(
            db_path, "ERROR", "twitter_error", f"Twitter error: {exc}", niche_id, error=str(exc)
        )


def _maybe_tweet_video(niche_id, niche_cfg, settings, db_path, video_path, post):
    """Tweet a video clip after Short generation (if Twitter is enabled)."""
    from core import bot_state, analytics_tracker

    if not bot_state.is_platform_enabled("twitter"):
        return

    try:
        from core.social_poster import SocialPoster
        poster = SocialPoster(settings)

        if poster.twitter.enabled and video_path.exists():
            niche_name = niche_cfg.get("name", niche_id.replace("_", " ").title())
            caption = f"🎬 New video: {post['title']}\n\n#{niche_name.replace(' ', '')} #TechLifeInsights"
            if len(caption) > 280:
                caption = caption[:277] + "…"
            tweet_id = poster.twitter.post_video(video_path, caption)
            if tweet_id:
                analytics_tracker.log_action(
                    db_path, "SUCCESS", "video_tweet_posted",
                    f"Video tweeted for '{post['title']}': {tweet_id}", niche_id
                )
    except Exception as exc:
        logger.debug("Video tweet error: %s", exc)


def job_generate_stock_images(niches_config: dict, settings: dict) -> None:
    """Generate AI stock images using trend intelligence for high-demand topics."""
    if not _should_run("stock_images"):
        return

    from core import bot_state

    if not bot_state.is_bot_running():
        return

    stock_cfg = settings.get("stock_images", {})
    if not stock_cfg.get("enabled", False):
        return

    try:
        from core import stock_generator, trend_intelligence, analytics_tracker
        db_path = _PROJECT_ROOT / "data" / "bot.db"

        count = stock_cfg.get("images_per_run", 5)
        all_topics = []

        for niche_id, niche_cfg in niches_config.items():
            if not bot_state.is_niche_enabled(niche_id):
                continue
            try:
                topics = trend_intelligence.get_image_demand_topics(niche_id, count=2)
                all_topics.extend(topics)
            except Exception:
                all_topics.append({"topic": niche_cfg.get("name", niche_id), "niche_id": niche_id})

        if all_topics:
            results = stock_generator.generate_stock_images(all_topics, settings, count=count)
            analytics_tracker.log_action(
                db_path, "SUCCESS", "stock_images_generated",
                f"Generated {len(results)} stock images"
            )
    except Exception as exc:
        logger.error("Stock image generation job failed: %s", exc)


def job_post_to_pinterest(
    niche_id: str,
    niche_cfg: dict,
    settings: dict,
    db_path: Path,
    site_url: str,
) -> None:
    """Create a Pinterest pin for the latest published post."""
    if not _should_run(f"pinterest_{niche_id}"):
        return

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
    """
    Check and execute any queued manual trigger requests.

    Manual triggers respect dependency order:
      1. Trend intelligence refresh
      2. Article generation
      3. Stock image generation
      4. Video/Short generation
      5. Twitter posting
      6. Pinterest posting
    """
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

    logger.info("🔧 Executing manual trigger for %s: %s", niche_id, platforms)

    # Temporarily force bot running for manual triggers
    state = bot_state.load_state()
    was_running = state.get("bot_running", False)
    was_mode = state.get("bot_mode", "scheduled")
    state["bot_running"] = True
    bot_state.save_state(state)

    try:
        # ── DEPENDENCY ORDER ─────────────────────────────────────────────

        # Step 1: Quick trend refresh for this niche
        try:
            from core import trend_intelligence
            trend_intelligence.gather_trending_topics(niche_id, niche_cfg, force=True)
            logger.info("  ✓ Step 1: Trends refreshed for %s", niche_id)
        except Exception as exc:
            logger.warning("  ✗ Step 1: Trend refresh failed: %s", exc)

        # Step 2: Generate article (if blog is in platforms)
        if "blog" in platforms:
            # Bypass mode check for manual triggers by calling job directly
            _manual_generate_and_publish(niche_id, niche_cfg, settings, db_path, site_url)
            logger.info("  ✓ Step 2: Article generated for %s", niche_id)

        # Step 3: Generate stock images
        try:
            from core import stock_generator, trend_intelligence as ti
            stock_cfg = settings.get("stock_images", {})
            if stock_cfg.get("enabled", False):
                topics = ti.get_image_demand_topics(niche_id, count=2)
                stock_generator.generate_stock_images(topics, settings, count=2)
                logger.info("  ✓ Step 3: Stock images generated")
        except Exception as exc:
            logger.debug("  ✗ Step 3: Stock images failed: %s", exc)

        # Step 4: Generate Short (depends on article existing)
        if "youtube_shorts" in platforms:
            _manual_generate_short(niche_id, niche_cfg, settings, db_path)
            logger.info("  ✓ Step 4: Short generated for %s", niche_id)

        # Step 5: Tweet article + video
        if "twitter" in platforms or "blog" in platforms:
            _manual_tweet(niche_id, niche_cfg, settings, db_path, site_url)
            logger.info("  ✓ Step 5: Tweeted for %s", niche_id)

        # Step 6: Pinterest
        if "pinterest" in platforms:
            _manual_pinterest(niche_id, niche_cfg, settings, db_path, site_url)
            logger.info("  ✓ Step 6: Pinterest pin created for %s", niche_id)

    finally:
        state = bot_state.load_state()
        state["bot_running"] = was_running
        state["bot_mode"] = was_mode
        bot_state.save_state(state)


def _manual_generate_and_publish(niche_id, niche_cfg, settings, db_path, site_url):
    """Manual trigger version of article generation — bypasses mode checks."""
    from core import (
        llm_writer, affiliate_injector, seo_optimizer,
        publisher, analytics_tracker, bot_state, content_guard,
    )

    output_dir = _PROJECT_ROOT / "site" / "output"
    niche_name = niche_cfg.get("name", niche_id)

    topic_data = _pick_unique_topic(niche_id, niche_cfg, db_path)
    if not topic_data or not topic_data.get("topic"):
        logger.warning("Manual trigger: no unique topic for %s", niche_id)
        return

    topic = topic_data["topic"]
    subtopic_id = topic_data.get("subtopic_id", "")

    article = llm_writer.generate_article(
        topic, niche_cfg, niche_id=niche_id, subtopic_id=subtopic_id
    )
    if not article:
        logger.warning("Manual trigger: LLM failed for %s", niche_id)
        return

    if not article.get("subtopic_id"):
        article["subtopic_id"] = subtopic_id

    if content_guard.is_duplicate_content(db_path, article.get("html_content", "")):
        logger.warning("Manual trigger: duplicate content for %s", niche_id)
        return

    dashboard_url = f"http://localhost:{settings.get('dashboard', {}).get('port', 5000)}"
    html_with_links, links_count = affiliate_injector.inject_links(
        article["html_content"], niche_cfg, dashboard_url
    )
    article["html_content"] = html_with_links
    article["affiliate_links_count"] = links_count

    article = seo_optimizer.optimize(article, niche_id, niche_cfg, site_url, output_dir)
    url_path = publisher.publish(article, niche_id, niche_name, settings, db_path)

    content_guard.record_content(
        db_path, niche_id, topic, article.get("title", ""), article.get("html_content", "")
    )
    bot_state.record_post_run(niche_id)

    analytics_tracker.log_action(
        db_path, "SUCCESS", "manual_post_published",
        f"Manual: Published '{article.get('title')}' → {url_path}", niche_id
    )


def _manual_generate_short(niche_id, niche_cfg, settings, db_path):
    """Manual trigger version of Short generation."""
    from core import shorts_generator, youtube_uploader, analytics_tracker

    if not settings.get("video", {}).get("enabled", True):
        return

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
    article = {"title": post["title"], "html_content": "", "meta_description": "", "tags": [], "slug": post["slug"]}

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

    result = shorts_generator.generate_short(article, video_path)
    if result:
        channel_name = settings.get("youtube_channel_name", "TechLife Insights")
        youtube_url = youtube_uploader.upload_video(video_path, article, niche_cfg, channel_name)
        if youtube_url:
            conn = sqlite3.connect(str(db_path))
            conn.execute("UPDATE posts SET youtube_url = ? WHERE slug = ?", (youtube_url, post["slug"]))
            conn.commit()
            conn.close()

        # Tweet the video too
        _maybe_tweet_video(niche_id, niche_cfg, settings, db_path, video_path, post)


def _manual_tweet(niche_id, niche_cfg, settings, db_path, site_url):
    """Manual trigger version of Twitter posting."""
    from core import bot_state

    if not bot_state.is_platform_enabled("twitter"):
        return

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
        slug = post.get("slug", "")
        article_url = f"{site_url.rstrip('/')}/{niche_id}/{slug}.html"

        article = {"title": post["title"], "url": article_url, "niche_id": niche_id}

        from core.social_poster import SocialPoster
        poster = SocialPoster(settings)
        if poster.twitter.enabled:
            poster.twitter.post_article(article)
    except Exception as exc:
        logger.debug("Manual tweet error: %s", exc)


def _manual_pinterest(niche_id, niche_cfg, settings, db_path, site_url):
    """Manual trigger version of Pinterest posting."""
    from core import pinterest_poster, bot_state

    if not bot_state.is_platform_enabled("pinterest"):
        return

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
            "title": post["title"], "slug": post["slug"],
            "niche_id": niche_id, "meta_description": post.get("meta_description", ""), "tags": [],
        }
        pinterest_poster.create_pin(article, niche_cfg, site_url)
    except Exception as exc:
        logger.debug("Manual Pinterest error: %s", exc)


def job_rebuild_site(settings: dict, db_path: Path, site_url: str) -> None:
    """Rebuild the entire static site index."""
    if not _should_run("rebuild_site"):
        return

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


# ═══════════════════════════════════════════════════════════════════════════
#  Full pipeline run (for manual "Run All" button)
# ═══════════════════════════════════════════════════════════════════════════

def run_full_pipeline(niches_config: dict, settings: dict, db_path: Path, site_url: str) -> dict:
    """
    Run the FULL pipeline in dependency order for ALL enabled niches.
    This is the "Manual Run All" button — it executes everything once.

    Dependency order:
      1. Trend intelligence
      2. Articles (per niche)
      3. Stock images
      4. Shorts (per niche)
      5. Twitter posts (per niche)
      6. Pinterest (per niche)

    Returns a summary dict.
    """
    from core import bot_state

    summary = {"steps_completed": 0, "errors": [], "details": {}}
    logger.info("🚀 Starting full pipeline run (manual mode)")

    # Step 1: Trend intelligence
    try:
        from core import trend_intelligence
        trend_intelligence.refresh_all_intelligence(niches_config, force=True)
        summary["details"]["trends"] = "✓ Refreshed"
        summary["steps_completed"] += 1
    except Exception as exc:
        summary["errors"].append(f"trends: {exc}")
        summary["details"]["trends"] = f"✗ {exc}"

    # Steps 2-6: Per niche
    for niche_id, niche_cfg in niches_config.items():
        if not bot_state.is_niche_enabled(niche_id):
            continue

        niche_summary = {}

        # Step 2: Article
        try:
            _manual_generate_and_publish(niche_id, niche_cfg, settings, db_path, site_url)
            niche_summary["article"] = "✓"
            summary["steps_completed"] += 1
        except Exception as exc:
            niche_summary["article"] = f"✗ {exc}"
            summary["errors"].append(f"{niche_id} article: {exc}")

        # Step 3: Stock images
        try:
            from core import stock_generator, trend_intelligence as ti
            if settings.get("stock_images", {}).get("enabled", False):
                topics = ti.get_image_demand_topics(niche_id, count=2)
                stock_generator.generate_stock_images(topics, settings, count=2)
                niche_summary["stock_images"] = "✓"
                summary["steps_completed"] += 1
        except Exception as exc:
            niche_summary["stock_images"] = f"✗ {exc}"

        # Step 4: Short
        try:
            _manual_generate_short(niche_id, niche_cfg, settings, db_path)
            niche_summary["short"] = "✓"
            summary["steps_completed"] += 1
        except Exception as exc:
            niche_summary["short"] = f"✗ {exc}"
            summary["errors"].append(f"{niche_id} short: {exc}")

        # Step 5: Tweet
        try:
            _manual_tweet(niche_id, niche_cfg, settings, db_path, site_url)
            niche_summary["twitter"] = "✓"
            summary["steps_completed"] += 1
        except Exception as exc:
            niche_summary["twitter"] = f"✗ {exc}"

        # Step 6: Pinterest
        try:
            _manual_pinterest(niche_id, niche_cfg, settings, db_path, site_url)
            niche_summary["pinterest"] = "✓"
            summary["steps_completed"] += 1
        except Exception as exc:
            niche_summary["pinterest"] = f"✗ {exc}"

        summary["details"][niche_id] = niche_summary

    # Step 7: Export stock images for platforms
    try:
        from core import stock_submitter
        results = stock_submitter.export_unsubmitted()
        summary["details"]["stock_export"] = f"✓ Exported {len(results)} images"
        if results:
            summary["steps_completed"] += 1
    except Exception as exc:
        summary["errors"].append(f"stock_export: {exc}")
        summary["details"]["stock_export"] = f"✗ {exc}"

    # Step 8: Sync stock earnings
    try:
        from core import income_tracker
        diff = income_tracker.sync_stock_earnings()
        if diff > 0:
            summary["details"]["income_sync"] = f"✓ Synced ${diff:.2f}"
        else:
            summary["details"]["income_sync"] = "✓ No new earnings"
        summary["steps_completed"] += 1
    except Exception as exc:
        summary["details"]["income_sync"] = f"✗ {exc}"

    logger.info("🏁 Full pipeline complete: %d steps, %d errors", summary["steps_completed"], len(summary["errors"]))
    return summary


# ── Helpers ─────────────────────────────────────────────────────────────────


def _pick_unique_topic(niche_id: str, niche_cfg: dict, db_path: Path) -> dict:
    """Pick a topic that hasn't been covered before (using content_guard + trend intelligence).

    Returns dict with keys 'topic' and 'subtopic_id', or empty dict on failure.
    """
    from core import content_guard

    candidates = []  # list of dicts: {"topic": str, "subtopic_id": str}

    # Try trend intelligence first (higher quality topics)
    try:
        from core.trend_intelligence import gather_trending_topics
        intel_topics = gather_trending_topics(niche_id, niche_cfg, force=False)
        for t in intel_topics:
            topic_str = t["topic"] if isinstance(t, dict) else t
            sub_id = t.get("subtopic_id", "") if isinstance(t, dict) else ""
            candidates.append({"topic": topic_str, "subtopic_id": sub_id})
    except Exception:
        pass

    # Try trends cache
    if _TRENDS_CACHE.exists():
        try:
            trends = json.loads(_TRENDS_CACHE.read_text())
            cached = trends.get(niche_id, [])
            for item in cached:
                if isinstance(item, dict):
                    candidates.append({"topic": item.get("topic", ""), "subtopic_id": item.get("subtopic_id", "")})
                elif isinstance(item, str):
                    candidates.append({"topic": item, "subtopic_id": ""})
        except Exception:
            pass

    # Add seed keywords as fallback
    for kw in niche_cfg.get("seed_keywords", []):
        candidates.append({"topic": kw, "subtopic_id": ""})

    existing_titles = _get_existing_titles(db_path)

    for cand in candidates:
        topic = cand.get("topic", "")
        if not topic:
            continue
        if topic.lower() in {t.lower() for t in existing_titles}:
            continue
        if content_guard.is_duplicate_topic(db_path, niche_id, topic):
            continue
        return cand

    logger.warning("All topics exhausted for niche %s", niche_id)
    return {}


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
