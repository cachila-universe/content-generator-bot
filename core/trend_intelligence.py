"""
Trend Intelligence — the self-learning brain of the bot.

Scans multiple data sources to discover:
  1. Trending TOPICS   — what people are searching for RIGHT NOW
  2. Writing STYLES    — article formats that perform best (listicles, how-tos, etc.)
  3. Video FORMATS     — styles getting views (split-screen, reels, POV, ASMR-text, etc.)
  4. Image DEMAND      — what stock image styles sell (based on niche + season)

Data sources (all free, no API key needed unless noted):
  • Google Trends (pytrends)           — real-time search volume
  • Reddit (JSON feeds)                — viral discussion topics
  • HackerNews (API)                   — tech trend signals
  • YouTube trending (RSS)             — video format intelligence
  • Google Suggest (autocomplete)      — long-tail keyword ideas

All intelligence is cached in the DB so the scheduler, writer, video generator,
and stock image system can query it without re-fetching.
"""

import json
import time
import random
import sqlite3
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_DB_PATH = _PROJECT_ROOT / "data" / "bot.db"
_CACHE_DIR = _PROJECT_ROOT / "data" / "intelligence"

# ── Refresh intervals (hours) ────────────────────────────────────────────
REFRESH_INTERVALS = {
    "topics": 6,       # Trending topics every 6 hours
    "styles": 24,      # Writing style analysis daily
    "video_formats": 24,  # Video trend analysis daily
    "image_demand": 24,   # Stock image demand daily
}

# ── Writing style templates detected from successful content ─────────────
WRITING_STYLES = {
    "listicle": {
        "name": "Listicle / Top-N",
        "pattern": "Top {N} {topic}",
        "description": "Numbered list format — consistently high CTR, great for SEO",
        "example_titles": [
            "Top 10 AI Tools for {topic}",
            "7 Best {topic} You Need in 2025",
            "15 {topic} That Actually Work",
        ],
    },
    "how_to": {
        "name": "How-To Guide",
        "pattern": "How to {action} {topic}",
        "description": "Step-by-step tutorial format — high engagement, high search volume",
        "example_titles": [
            "How to {topic}: A Complete Guide",
            "How to Master {topic} in 2025",
            "The Ultimate Guide to {topic}",
        ],
    },
    "comparison": {
        "name": "Comparison / vs",
        "pattern": "{A} vs {B}: Which is Better?",
        "description": "Product/tool comparison — high commercial intent, good for affiliates",
        "example_titles": [
            "{A} vs {B}: Which Should You Choose?",
            "{topic} Compared: The Honest Truth",
        ],
    },
    "review": {
        "name": "In-Depth Review",
        "pattern": "{product} Review: Is It Worth It?",
        "description": "Detailed product review — strong affiliate conversion",
        "example_titles": [
            "{topic} Review: My Honest Experience After 30 Days",
            "I Tried {topic} — Here's What Happened",
        ],
    },
    "problem_solution": {
        "name": "Problem-Solution",
        "pattern": "Why {problem} and How to Fix It",
        "description": "Addresses pain point then offers solution — good for trust building",
        "example_titles": [
            "Why {topic} Fails (And What to Do Instead)",
            "The Hidden Problem With {topic}",
        ],
    },
    "news_trending": {
        "name": "Trending News",
        "pattern": "{topic} in 2025: What You Need to Know",
        "description": "Newsjacking / trend commentary — great for timeliness",
        "example_titles": [
            "Breaking: {topic} Changes Everything",
            "{topic} in 2025: What Just Changed",
        ],
    },
    "beginner_guide": {
        "name": "Beginner's Guide",
        "pattern": "{topic} for Beginners",
        "description": "Introductory content — evergreen, high search volume",
        "example_titles": [
            "{topic} for Beginners: Everything You Need to Know",
            "A Complete Beginner's Guide to {topic}",
        ],
    },
}

# ── Video format templates ───────────────────────────────────────────────
VIDEO_FORMATS = {
    "quick_tips": {
        "name": "Quick Tips / Top 5",
        "duration": "30-60s",
        "description": "Fast-paced numbered tips with text overlay — highest engagement",
        "style_notes": "Quick cuts, progress counter, bold text, upbeat music",
    },
    "split_screen": {
        "name": "Split Screen",
        "duration": "30-60s",
        "description": "Side-by-side comparison (before/after, good/bad) — very trending on Reels",
        "style_notes": "Two parallel scenes, comparison text, dramatic reveal",
    },
    "hook_story": {
        "name": "Hook + Story",
        "duration": "45-90s",
        "description": "Opens with provocative hook, then delivers value — best retention",
        "style_notes": "First 3 seconds = hook text, then narration with images",
    },
    "tutorial_steps": {
        "name": "Tutorial Steps",
        "duration": "30-60s",
        "description": "Step-by-step walkthrough with numbered captions — educational shorts",
        "style_notes": "Step counter, clear captions, screen recordings or images",
    },
    "text_reveal": {
        "name": "Text Reveal / ASMR Text",
        "description": "Text appears word-by-word or line-by-line with satisfying effects",
        "duration": "15-30s",
        "style_notes": "Typewriter effect, minimal background, trending on TikTok",
    },
    "pov_style": {
        "name": "POV Style",
        "duration": "15-45s",
        "description": "POV: You discover {topic} — first-person framing trending on TikTok/Reels",
        "style_notes": "Starts with 'POV:' text, immersive visuals, emotional hook",
    },
    "myth_bust": {
        "name": "Myth Busting",
        "duration": "30-60s",
        "description": "Myth vs Reality format — drives comments and shares",
        "style_notes": "'MYTH:' screen → dramatic pause → 'REALITY:' screen",
    },
}

# ── Stock image demand signals ───────────────────────────────────────────
IMAGE_DEMAND_CATEGORIES = {
    "ai_tools": ["AI workspace", "futuristic technology", "robot assistant", "coding hologram"],
    "personal_finance": ["money growing", "investment chart", "budgeting", "financial freedom"],
    "health_biohacking": ["wellness routine", "supplement stack", "biohacking lab", "meditation"],
    "home_tech": ["smart home", "IoT devices", "home automation", "connected devices"],
    "travel": ["exotic destination", "backpacker adventure", "luxury resort", "hidden gem"],
    "pet_care": ["cute pet portrait", "pet health", "dog training", "cat lifestyle"],
    "fitness_wellness": ["gym workout", "healthy meal prep", "yoga pose", "running trail"],
    "remote_work": ["home office setup", "digital nomad", "video conference", "productivity desk"],
}


# ═══════════════════════════════════════════════════════════════════════════
#  DB Setup
# ═══════════════════════════════════════════════════════════════════════════

def _ensure_tables():
    """Create intelligence cache tables."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trend_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            niche_id TEXT DEFAULT '',
            data_type TEXT NOT NULL,
            data_json TEXT NOT NULL,
            source TEXT DEFAULT '',
            score REAL DEFAULT 0,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS style_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            style_type TEXT NOT NULL,
            style_id TEXT NOT NULL,
            niche_id TEXT DEFAULT '',
            effectiveness_score REAL DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            data_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _needs_refresh(category: str) -> bool:
    """Check if a cache category needs refreshing."""
    conn = sqlite3.connect(str(_DB_PATH))
    row = conn.execute(
        "SELECT MAX(fetched_at) FROM trend_intelligence WHERE category = ?",
        (category,)
    ).fetchone()
    conn.close()

    if not row or not row[0]:
        return True

    try:
        last_fetch = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
        hours_since = (datetime.now(timezone.utc) - last_fetch).total_seconds() / 3600
        return hours_since >= REFRESH_INTERVALS.get(category, 24)
    except Exception:
        return True


# ═══════════════════════════════════════════════════════════════════════════
#  Data Source: Google Trends
# ═══════════════════════════════════════════════════════════════════════════

def _fetch_google_trends(niche_id: str, seed_keywords: list) -> list[dict]:
    """Fetch trending queries from Google Trends."""
    results = []
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 30), retries=2, backoff_factor=0.5)

        for seed in seed_keywords[:3]:
            try:
                pytrends.build_payload([seed], cat=0, timeframe="now 7-d", geo="US")
                related = pytrends.related_queries()

                if seed in related and related[seed]:
                    rising = related[seed].get("rising")
                    if rising is not None and not rising.empty:
                        for _, row in rising.head(8).iterrows():
                            query = str(row.get("query", "")).strip()
                            try:
                                score = int(row.get("value", 0))
                            except (ValueError, TypeError):
                                score = 200  # "Breakout"
                            if query:
                                results.append({
                                    "topic": query,
                                    "score": min(score, 300),
                                    "source": "google_trends",
                                    "keyword": seed,
                                })
                time.sleep(random.uniform(1, 3))
            except Exception as exc:
                logger.debug("Google Trends error for '%s': %s", seed, exc)
    except ImportError:
        logger.debug("pytrends not available")
    except Exception as exc:
        logger.debug("Google Trends failed: %s", exc)

    return results


# ═══════════════════════════════════════════════════════════════════════════
#  Data Source: Google Autocomplete (free, no API key)
# ═══════════════════════════════════════════════════════════════════════════

def _fetch_google_suggest(keywords: list) -> list[dict]:
    """Get Google autocomplete suggestions — free long-tail keyword ideas."""
    results = []
    try:
        import httpx
        for kw in keywords[:5]:
            try:
                resp = httpx.get(
                    "https://suggestqueries.google.com/complete/search",
                    params={"client": "firefox", "q": kw},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    suggestions = data[1] if len(data) > 1 else []
                    for s in suggestions[:5]:
                        if s.lower() != kw.lower():
                            results.append({
                                "topic": s,
                                "score": 50,
                                "source": "google_suggest",
                                "keyword": kw,
                            })
                time.sleep(random.uniform(0.5, 1.5))
            except Exception:
                pass
    except ImportError:
        pass
    return results


# ═══════════════════════════════════════════════════════════════════════════
#  Data Source: Reddit (free JSON feed, no API key needed)
# ═══════════════════════════════════════════════════════════════════════════

NICHE_SUBREDDITS = {
    "ai_tools": ["artificial", "ChatGPT", "MachineLearning"],
    "personal_finance": ["personalfinance", "investing", "financialindependence"],
    "health_biohacking": ["Biohackers", "longevity", "Nootropics"],
    "home_tech": ["smarthome", "homeautomation", "homeassistant"],
    "travel": ["travel", "solotravel", "digitalnomad"],
    "pet_care": ["pets", "dogs", "cats"],
    "fitness_wellness": ["fitness", "bodyweightfitness", "nutrition"],
    "remote_work": ["remotework", "digitalnomad", "WorkOnline"],
}


def _fetch_reddit_trends(niche_id: str) -> list[dict]:
    """Fetch hot posts from relevant subreddits."""
    results = []
    subreddits = NICHE_SUBREDDITS.get(niche_id, [])

    try:
        import httpx
        headers = {"User-Agent": "ContentBot/1.0 (educational project)"}

        for sub in subreddits[:2]:
            try:
                resp = httpx.get(
                    f"https://www.reddit.com/r/{sub}/hot.json?limit=10",
                    headers=headers,
                    timeout=15,
                    follow_redirects=True,
                )
                if resp.status_code == 200:
                    posts = resp.json().get("data", {}).get("children", [])
                    for post in posts:
                        data = post.get("data", {})
                        title = data.get("title", "")
                        ups = data.get("ups", 0)
                        if title and ups > 50:
                            results.append({
                                "topic": title,
                                "score": min(ups // 10, 200),
                                "source": f"reddit_r/{sub}",
                                "keyword": sub,
                                "engagement": ups,
                            })
                time.sleep(random.uniform(1, 3))
            except Exception as exc:
                logger.debug("Reddit error for r/%s: %s", sub, exc)
    except ImportError:
        pass

    return results


# ═══════════════════════════════════════════════════════════════════════════
#  Data Source: HackerNews (free API, no key needed)
# ═══════════════════════════════════════════════════════════════════════════

def _fetch_hackernews_trends() -> list[dict]:
    """Fetch top HackerNews stories for tech trend signals."""
    results = []
    try:
        import httpx
        resp = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        if resp.status_code != 200:
            return results

        story_ids = resp.json()[:15]
        for sid in story_ids:
            try:
                story = httpx.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10
                ).json()
                title = story.get("title", "")
                score = story.get("score", 0)
                if title and score > 50:
                    results.append({
                        "topic": title,
                        "score": min(score // 5, 200),
                        "source": "hackernews",
                        "keyword": "tech",
                        "engagement": score,
                    })
            except Exception:
                pass
        time.sleep(1)
    except ImportError:
        pass
    except Exception as exc:
        logger.debug("HackerNews error: %s", exc)

    return results


# ═══════════════════════════════════════════════════════════════════════════
#  Main intelligence pipeline
# ═══════════════════════════════════════════════════════════════════════════

def gather_trending_topics(niche_id: str, niche_config: dict, force: bool = False) -> list[dict]:
    """
    Gather trending topics from all sources for a niche.
    Results are cached — only refreshes if stale or force=True.

    Returns sorted list of {topic, score, source, keyword} dicts.
    """
    _ensure_tables()

    if not force and not _needs_refresh("topics"):
        cached = _get_cached_topics(niche_id)
        if cached:
            return cached

    seed_keywords = niche_config.get("seed_keywords", [])
    all_topics = []

    # Gather from all sources
    logger.info("🔍 Gathering trend intelligence for %s...", niche_id)

    topics_google = _fetch_google_trends(niche_id, seed_keywords)
    all_topics.extend(topics_google)
    logger.info("  Google Trends: %d topics", len(topics_google))

    topics_suggest = _fetch_google_suggest(seed_keywords)
    all_topics.extend(topics_suggest)
    logger.info("  Google Suggest: %d ideas", len(topics_suggest))

    topics_reddit = _fetch_reddit_trends(niche_id)
    all_topics.extend(topics_reddit)
    logger.info("  Reddit: %d topics", len(topics_reddit))

    # HackerNews for tech niches
    if niche_id in ("ai_tools", "home_tech", "remote_work"):
        topics_hn = _fetch_hackernews_trends()
        all_topics.extend(topics_hn)
        logger.info("  HackerNews: %d topics", len(topics_hn))

    # Deduplicate by similarity
    seen = set()
    unique = []
    for t in all_topics:
        key = t["topic"].lower().strip()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(t)

    # Sort by score descending
    unique.sort(key=lambda x: x.get("score", 0), reverse=True)

    # Cache to DB
    _cache_topics(niche_id, unique)

    logger.info("📊 Total unique topics for %s: %d", niche_id, len(unique))
    return unique[:20]


def _get_cached_topics(niche_id: str) -> list[dict]:
    """Get cached trending topics."""
    conn = sqlite3.connect(str(_DB_PATH))
    row = conn.execute(
        "SELECT data_json FROM trend_intelligence WHERE category = 'topics' AND niche_id = ? "
        "ORDER BY fetched_at DESC LIMIT 1",
        (niche_id,)
    ).fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except Exception:
            pass
    return []


def _cache_topics(niche_id: str, topics: list[dict]):
    """Cache trending topics in DB."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        "INSERT INTO trend_intelligence (category, niche_id, data_type, data_json, source, score) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("topics", niche_id, "trending_topics", json.dumps(topics[:20]),
         "multi_source", len(topics)),
    )
    # Clean old cache (keep last 7 days)
    conn.execute(
        "DELETE FROM trend_intelligence WHERE category = 'topics' AND "
        "fetched_at < datetime('now', '-7 days')"
    )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════
#  Writing Style Intelligence
# ═══════════════════════════════════════════════════════════════════════════

def get_recommended_writing_style(niche_id: str, topic: str) -> dict:
    """
    Recommend the best writing style for a topic based on intelligence data.

    Returns a style dict with name, pattern, instructions, and example title.
    """
    _ensure_tables()

    # Get style effectiveness from DB
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT style_id, effectiveness_score, usage_count FROM style_intelligence "
        "WHERE style_type = 'writing' AND (niche_id = ? OR niche_id = '') "
        "ORDER BY effectiveness_score DESC",
        (niche_id,)
    ).fetchall()
    conn.close()

    # Use DB scores if available, otherwise assign default weights
    style_scores = {}
    for row in rows:
        style_scores[row["style_id"]] = row["effectiveness_score"]

    # Default effectiveness weights (from content marketing research)
    default_weights = {
        "listicle": 90,
        "how_to": 85,
        "comparison": 80,
        "review": 75,
        "problem_solution": 70,
        "news_trending": 65,
        "beginner_guide": 60,
    }

    # Merge: prefer DB data, fall back to defaults
    for style_id, weight in default_weights.items():
        if style_id not in style_scores:
            style_scores[style_id] = weight

    # Topic-based heuristic boost
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["best", "top", "favorite"]):
        style_scores["listicle"] = style_scores.get("listicle", 0) + 20
    if any(w in topic_lower for w in ["how", "guide", "tutorial", "learn"]):
        style_scores["how_to"] = style_scores.get("how_to", 0) + 20
    if " vs " in topic_lower or "compare" in topic_lower:
        style_scores["comparison"] = style_scores.get("comparison", 0) + 30
    if any(w in topic_lower for w in ["review", "worth", "experience"]):
        style_scores["review"] = style_scores.get("review", 0) + 25
    if any(w in topic_lower for w in ["problem", "wrong", "mistake", "fail"]):
        style_scores["problem_solution"] = style_scores.get("problem_solution", 0) + 20
    if any(w in topic_lower for w in ["2025", "new", "latest", "breaking"]):
        style_scores["news_trending"] = style_scores.get("news_trending", 0) + 15
    if any(w in topic_lower for w in ["beginner", "start", "first"]):
        style_scores["beginner_guide"] = style_scores.get("beginner_guide", 0) + 20

    # Pick top-weighted style with some randomness (top 3, weighted random)
    sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_styles[:3]

    # Weighted random selection from top 3
    total = sum(s for _, s in top_3)
    r = random.uniform(0, total)
    cumulative = 0
    chosen_id = top_3[0][0]
    for sid, score in top_3:
        cumulative += score
        if r <= cumulative:
            chosen_id = sid
            break

    style = WRITING_STYLES.get(chosen_id, WRITING_STYLES["listicle"])

    # Build concrete title suggestion
    example = random.choice(style["example_titles"])
    suggested_title = example.replace("{topic}", topic).replace("{N}", str(random.choice([5, 7, 10, 15])))

    return {
        "style_id": chosen_id,
        "name": style["name"],
        "description": style["description"],
        "pattern": style["pattern"],
        "suggested_title": suggested_title,
        "effectiveness_score": style_scores.get(chosen_id, 50),
    }


def record_style_performance(style_id: str, style_type: str, niche_id: str, score: float):
    """Record how well a writing/video style performed (for learning)."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))

    existing = conn.execute(
        "SELECT id, effectiveness_score, usage_count FROM style_intelligence "
        "WHERE style_id = ? AND style_type = ? AND niche_id = ?",
        (style_id, style_type, niche_id)
    ).fetchone()

    if existing:
        # Rolling average
        old_score = existing[1]
        count = existing[2]
        new_score = (old_score * count + score) / (count + 1)
        conn.execute(
            "UPDATE style_intelligence SET effectiveness_score = ?, usage_count = usage_count + 1, "
            "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_score, existing[0])
        )
    else:
        conn.execute(
            "INSERT INTO style_intelligence (style_type, style_id, niche_id, effectiveness_score, "
            "usage_count, data_json) VALUES (?, ?, ?, ?, 1, ?)",
            (style_type, style_id, niche_id, score, json.dumps({"initial": True}))
        )

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════
#  Video Format Intelligence
# ═══════════════════════════════════════════════════════════════════════════

def get_recommended_video_format(niche_id: str, topic: str) -> dict:
    """
    Recommend the best video format for a topic.
    Uses DB performance data + topic heuristics.
    """
    _ensure_tables()

    # Default format weights (from YouTube/TikTok analytics research)
    format_scores = {
        "quick_tips": 90,
        "hook_story": 85,
        "split_screen": 80,
        "tutorial_steps": 75,
        "text_reveal": 70,
        "pov_style": 65,
        "myth_bust": 60,
    }

    # Topic-based boosts
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["top", "best", "tip", "hack"]):
        format_scores["quick_tips"] += 20
    if any(w in topic_lower for w in ["vs", "compare", "better", "versus"]):
        format_scores["split_screen"] += 25
    if any(w in topic_lower for w in ["how", "tutorial", "step", "guide"]):
        format_scores["tutorial_steps"] += 20
    if any(w in topic_lower for w in ["myth", "wrong", "lie", "truth"]):
        format_scores["myth_bust"] += 25
    if any(w in topic_lower for w in ["secret", "hidden", "nobody", "pov"]):
        format_scores["pov_style"] += 20

    # Override with DB data
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT style_id, effectiveness_score FROM style_intelligence "
        "WHERE style_type = 'video' AND (niche_id = ? OR niche_id = '') "
        "ORDER BY effectiveness_score DESC",
        (niche_id,)
    ).fetchall()
    conn.close()

    for row in rows:
        if row["style_id"] in format_scores:
            format_scores[row["style_id"]] = row["effectiveness_score"]

    # Weighted random from top 3
    sorted_formats = sorted(format_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_formats[:3]
    total = sum(s for _, s in top_3)
    r = random.uniform(0, total)
    cumulative = 0
    chosen_id = top_3[0][0]
    for fid, score in top_3:
        cumulative += score
        if r <= cumulative:
            chosen_id = fid
            break

    fmt = VIDEO_FORMATS.get(chosen_id, VIDEO_FORMATS["quick_tips"])
    return {
        "format_id": chosen_id,
        **fmt,
        "effectiveness_score": format_scores.get(chosen_id, 50),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  Stock Image Demand Intelligence
# ═══════════════════════════════════════════════════════════════════════════

def get_image_demand_topics(niche_id: str, count: int = 5) -> list[dict]:
    """
    Get high-demand stock image topics for a niche.
    Combines trending topics + niche-specific demand signals.
    """
    _ensure_tables()
    topics = []

    # 1. Pull from trending topics
    cached = _get_cached_topics(niche_id)
    for t in cached[:count]:
        topics.append({
            "topic": t["topic"],
            "niche_id": niche_id,
            "trend_source": t.get("source", "cached"),
            "market_demand_score": min(t.get("score", 50) / 100, 1.0),
        })

    # 2. Fill with niche-specific high-demand categories
    demand = IMAGE_DEMAND_CATEGORIES.get(niche_id, ["technology", "modern lifestyle"])
    while len(topics) < count:
        topic = random.choice(demand)
        topics.append({
            "topic": topic,
            "niche_id": niche_id,
            "trend_source": "niche_demand",
            "market_demand_score": 0.6,
        })

    return topics[:count]


# ═══════════════════════════════════════════════════════════════════════════
#  Full intelligence refresh (called by scheduler)
# ═══════════════════════════════════════════════════════════════════════════

def refresh_all_intelligence(niches_config: dict, force: bool = False) -> dict:
    """
    Master refresh function — gathers all trend intelligence.
    Called daily by the scheduler.

    Returns summary of what was gathered.
    """
    _ensure_tables()
    summary = {"niches_scanned": 0, "total_topics": 0, "sources": set()}

    for niche_id, niche_cfg in niches_config.items():
        try:
            topics = gather_trending_topics(niche_id, niche_cfg, force=force)
            summary["niches_scanned"] += 1
            summary["total_topics"] += len(topics)
            for t in topics:
                summary["sources"].add(t.get("source", "unknown"))
            time.sleep(random.uniform(2, 5))  # Anti rate-limit
        except Exception as exc:
            logger.warning("Intelligence refresh failed for %s: %s", niche_id, exc)

    summary["sources"] = list(summary["sources"])
    logger.info(
        "🧠 Intelligence refresh complete: %d niches, %d topics from %s",
        summary["niches_scanned"], summary["total_topics"], summary["sources"]
    )
    return summary


def get_intelligence_summary() -> dict:
    """Get a summary of all intelligence data for the dashboard."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row

    # Topic counts per niche
    topics_by_niche = {}
    rows = conn.execute(
        "SELECT niche_id, COUNT(*) as cnt FROM trend_intelligence "
        "WHERE category = 'topics' GROUP BY niche_id"
    ).fetchall()
    for r in rows:
        topics_by_niche[r["niche_id"]] = r["cnt"]

    # Style performance
    styles = conn.execute(
        "SELECT style_type, style_id, niche_id, effectiveness_score, usage_count "
        "FROM style_intelligence ORDER BY effectiveness_score DESC LIMIT 20"
    ).fetchall()

    # Latest refresh time
    latest = conn.execute(
        "SELECT MAX(fetched_at) as last_refresh FROM trend_intelligence"
    ).fetchone()

    conn.close()

    return {
        "topics_by_niche": topics_by_niche,
        "top_styles": [dict(s) for s in styles],
        "last_refresh": latest["last_refresh"] if latest else None,
        "writing_styles": list(WRITING_STYLES.keys()),
        "video_formats": list(VIDEO_FORMATS.keys()),
    }
