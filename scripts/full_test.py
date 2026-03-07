#!/usr/bin/env python3
"""Full test run: 1 article per niche + shorts + social posting."""
import os, sys, yaml, sqlite3, logging, traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s — %(message)s",
)
logger = logging.getLogger("full_test")

from core import (
    analytics_tracker, llm_writer, affiliate_injector,
    seo_optimizer, publisher, bot_state,
)

db_path = PROJECT_ROOT / "data" / "bot.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
analytics_tracker.init_db(db_path)

with open("config/niches.yaml") as f:
    niches = yaml.safe_load(f).get("niches", {})
with open("config/settings.yaml") as f:
    settings = yaml.safe_load(f)

site_url = os.getenv("SITE_URL", "https://tech-life-insights.com")
settings["site_url"] = site_url
output_dir = PROJECT_ROOT / "site" / "output"

# Optional modules
try:
    from core import internal_linker
except ImportError:
    internal_linker = None

# All 8 niches
selected = [nid for nid, cfg in niches.items() if cfg.get("enabled", True)]

print(f"\n{'='*60}")
print(f"  FULL TEST RUN — {len(selected)} niches")
print(f"  Articles → Shorts → Twitter")
print(f"  Niches: {', '.join(selected)}")
print(f"{'='*60}\n")

# ── Check API status ────────────────────────────────────────────────────
yt_token = PROJECT_ROOT / "data" / "youtube_token.json"
cs_file = PROJECT_ROOT / "client_secrets.json"
print("API Status:")
print(f"  YouTube token: {'✅' if yt_token.exists() else '❌ missing'}")
print(f"  YouTube secrets: {'✅' if cs_file.exists() else '❌ missing (no upload)'}")
tw = settings.get("social", {}).get("twitter", {})
print(f"  Twitter: {'✅ configured' if tw.get('api_key') and tw.get('access_token') else '❌ not configured'}")
print(f"  Pexels (video imgs): {'✅' if settings.get('video', {}).get('pexels_api_key') else '❌'}")
hf = settings.get("stock_images", {}).get("huggingface_token", "")
print(f"  HuggingFace (AI imgs): {'✅' if hf else '❌ not set'}")
print()

# ── PHASE 1: Generate articles ──────────────────────────────────────────
success_articles = []

for niche_id in selected:
    niche_cfg = niches[niche_id]
    niche_name = niche_cfg.get("name", niche_id)

    # Pick topic
    try:
        from core import trend_finder
        topics = trend_finder.get_trending_topics(niche_id, niche_cfg, db_path)
        topic = topics[0] if isinstance(topics[0], str) else topics[0].get("topic", str(topics[0])) if topics else None
    except Exception:
        topic = None

    if not topic:
        kw = niche_cfg.get("seed_keywords", [])
        topic = kw[0] if kw else f"best {niche_name} 2026"

    print(f"\n{'─'*60}")
    print(f"  📝 [{niche_id}] Topic: {topic}")
    print(f"{'─'*60}")

    try:
        article = llm_writer.generate_article(topic, niche_cfg, niche_id=niche_id)
        if not article:
            print(f"  ❌ LLM failed")
            continue

        print(f"  ✅ Written: {article['title']} ({article['word_count']} words)")

        # Affiliate injection
        html, count = affiliate_injector.inject_links(article["html_content"], niche_cfg, "")
        article["html_content"] = html
        article["affiliate_links_count"] = count

        # Internal linking
        if internal_linker:
            all_posts = analytics_tracker.get_all_posts(db_path)
            article["html_content"] = internal_linker.inject_internal_links(
                article["html_content"], "", all_posts, site_url
            )

        # SEO optimization (adds hero image via Pexels)
        article.update(seo_optimizer.optimize(article, niche_id, niche_cfg, site_url, output_dir))
        print(f"  ✅ SEO done: {article['slug']}")

        # Publish
        url = publisher.publish(article, niche_id, niche_name, settings, db_path)
        print(f"  ✅ Published: {url}")

        bot_state.record_post_run(niche_id)
        success_articles.append({"niche_id": niche_id, "niche_cfg": niche_cfg, "article": article})

    except Exception as exc:
        print(f"  ❌ Error: {exc}")
        traceback.print_exc()

print(f"\n{'='*60}")
print(f"  PHASE 1 DONE — {len(success_articles)}/{len(selected)} articles generated")
print(f"{'='*60}")

if not success_articles:
    print("No articles generated — stopping.")
    sys.exit(1)

# ── PHASE 2: Generate YouTube Shorts ────────────────────────────────────
print(f"\n{'='*60}")
print(f"  PHASE 2 — YouTube Shorts ({len(success_articles)} videos)")
print(f"{'='*60}")

shorts_generated = []

for item in success_articles:
    niche_id = item["niche_id"]
    niche_cfg = item["niche_cfg"]
    article = item["article"]
    slug = article.get("slug", "unknown")

    print(f"\n  🎬 Generating Short for: {article['title'][:50]}...")

    try:
        from core import shorts_generator

        video_dir = output_dir / niche_id
        video_dir.mkdir(parents=True, exist_ok=True)
        video_path = video_dir / f"{slug}_short.mp4"

        result = shorts_generator.generate_short(article, video_path)
        if result and result.exists():
            size_mb = result.stat().st_size / 1048576
            print(f"  ✅ Short: {result.name} ({size_mb:.1f} MB)")
            shorts_generated.append({
                "niche_id": niche_id, "niche_cfg": niche_cfg,
                "article": article, "video_path": result,
            })
        else:
            print(f"  ❌ Short generation failed")
    except Exception as exc:
        print(f"  ❌ Short error: {exc}")
        traceback.print_exc()

print(f"\n  Shorts generated: {len(shorts_generated)}/{len(success_articles)}")

# ── PHASE 3: Upload Shorts to YouTube ───────────────────────────────────
yt_secrets = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(cs_file))
yt_uploads = 0

if cs_file.exists():
    print(f"\n{'='*60}")
    print(f"  PHASE 3 — YouTube Upload ({len(shorts_generated)} shorts)")
    print(f"{'='*60}")

    os.environ.setdefault("YOUTUBE_CLIENT_SECRETS_FILE", str(cs_file))

    for item in shorts_generated:
        try:
            from core import youtube_uploader
            channel = settings.get("youtube_channel_name", "TechLife Insights")
            yt_url = youtube_uploader.upload_video(
                item["video_path"], item["article"], item["niche_cfg"], channel
            )
            if yt_url:
                print(f"  ✅ Uploaded: {yt_url}")
                # Save URL to DB
                conn = sqlite3.connect(str(db_path))
                conn.execute(
                    "UPDATE posts SET youtube_url = ? WHERE slug = ?",
                    (yt_url, item["article"]["slug"]),
                )
                conn.commit()
                conn.close()
                yt_uploads += 1
            else:
                print(f"  ⚠️  YouTube upload skipped (not configured or quota)")
        except Exception as exc:
            print(f"  ❌ Upload error: {exc}")
else:
    print(f"\n  ⚠️  Skipping YouTube upload — client_secrets.json not found")

# ── PHASE 4: Tweet articles ─────────────────────────────────────────────
tw_cfg = settings.get("social", {}).get("twitter", {})
tweets_sent = 0

if tw_cfg.get("api_key") and tw_cfg.get("access_token"):
    print(f"\n{'='*60}")
    print(f"  PHASE 4 — Twitter ({len(success_articles)} tweets)")
    print(f"{'='*60}")

    for item in success_articles:
        try:
            from core.social_poster import SocialPoster
            poster = SocialPoster(settings)

            if poster.twitter.enabled:
                article = item["article"]
                article_url = f"{site_url}/{item['niche_id']}/{article['slug']}.html"
                tweet_data = {
                    "title": article["title"],
                    "url": article_url,
                    "niche_id": item["niche_id"],
                    "meta_description": article.get("meta_description", ""),
                }
                tweet_id = poster.twitter.post_article(tweet_data)
                if tweet_id:
                    print(f"  ✅ Tweeted: {article['title'][:40]}... → {tweet_id}")
                    tweets_sent += 1
                else:
                    print(f"  ⚠️  Tweet failed for {item['niche_id']}")
            else:
                print(f"  ⚠️  Twitter poster not enabled")
                break
        except Exception as exc:
            print(f"  ❌ Tweet error: {exc}")
            traceback.print_exc()
            break  # Don't keep trying if Twitter is broken
else:
    print(f"\n  ⚠️  Skipping Twitter — API not configured")

# ── FINAL SUMMARY ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  🎉 FULL TEST COMPLETE")
print(f"{'='*60}")
print(f"  📝 Articles:  {len(success_articles)}/{len(selected)}")
print(f"  🎬 Shorts:    {len(shorts_generated)}/{len(success_articles)}")
print(f"  ▶️  YT uploads: {yt_uploads}")
print(f"  🐦 Tweets:    {tweets_sent}")
print(f"{'='*60}")
