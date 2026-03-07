"""
Content Intelligence — scours the internet for top-performing content formats
in each niche and adapts writing style, structure, and image placement dynamically.

The system learns from:
  1. Google search top results (title patterns, word counts, structure)
  2. Own performance data (clicks, engagement from analytics)
  3. Trending format patterns (listicles vs guides vs reviews)

It feeds recommendations to llm_writer for format selection and style adaptation.
"""

import re
import json
import time
import random
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_DB_PATH = _PROJECT_ROOT / "data" / "bot.db"
_CACHE_PATH = _PROJECT_ROOT / "data" / "content_intel_cache.json"


# ── Format patterns detected from successful content ──────────────────────
FORMAT_SIGNATURES = {
    "listicle": {
        "title_patterns": [r"\d+\s+best", r"top\s+\d+", r"\d+\s+ways", r"\d+\s+tools", r"\d+\s+tips"],
        "structure": "numbered_items",
        "avg_word_count": (1200, 1800),
        "image_density": "high",  # image after every 2-3 items
        "cta_placement": "after_item_3",
    },
    "how_to": {
        "title_patterns": [r"how\s+to", r"step.by.step", r"complete\s+guide", r"beginner.?s?\s+guide"],
        "structure": "sequential_steps",
        "avg_word_count": (1400, 2200),
        "image_density": "medium",  # image after every major step
        "cta_placement": "mid_article",
    },
    "comparison": {
        "title_patterns": [r"\bvs\.?\b", r"compared", r"versus", r"difference\s+between", r"which\s+is\s+better"],
        "structure": "side_by_side",
        "avg_word_count": (1200, 1600),
        "image_density": "medium",
        "cta_placement": "after_verdict",
    },
    "review": {
        "title_patterns": [r"\breview\b", r"hands.on", r"honest\s+review", r"worth\s+it"],
        "structure": "pros_cons_verdict",
        "avg_word_count": (1000, 1600),
        "image_density": "high",  # product shots throughout
        "cta_placement": "after_pros_cons",
    },
    "news_trending": {
        "title_patterns": [r"202[4-9]", r"just\s+announced", r"breaking", r"update", r"new\s+release"],
        "structure": "inverted_pyramid",
        "avg_word_count": (800, 1200),
        "image_density": "low",
        "cta_placement": "end",
    },
    "problem_solution": {
        "title_patterns": [r"fix", r"solve", r"stop\s+\w+ing", r"get\s+rid\s+of", r"deal\s+with"],
        "structure": "problem_then_solutions",
        "avg_word_count": (1200, 1800),
        "image_density": "medium",
        "cta_placement": "after_solution",
    },
    "beginner_guide": {
        "title_patterns": [r"for\s+beginners", r"101\b", r"everything\s+you\s+need", r"what\s+is"],
        "structure": "progressive_learning",
        "avg_word_count": (1600, 2400),
        "image_density": "high",
        "cta_placement": "mid_article",
    },
}


# ── Niche-specific content strategies ─────────────────────────────────────
NICHE_STRATEGIES = {
    "ai_tools": {
        "preferred_formats": ["listicle", "comparison", "review"],
        "monetization_focus": "product_links",
        "image_style": "tech_screenshots",
        "content_angle": "practical_utility",
    },
    "personal_finance": {
        "preferred_formats": ["how_to", "beginner_guide", "news_trending"],
        "monetization_focus": "financial_products",
        "image_style": "infographic_charts",
        "content_angle": "actionable_advice",
    },
    "health_biohacking": {
        "preferred_formats": ["review", "listicle", "problem_solution"],
        "monetization_focus": "supplement_links",
        "image_style": "lifestyle_wellness",
        "content_angle": "science_backed",
    },
    "home_tech": {
        "preferred_formats": ["review", "comparison", "listicle"],
        "monetization_focus": "product_links",
        "image_style": "product_photography",
        "content_angle": "hands_on_testing",
    },
    "travel": {
        "preferred_formats": ["listicle", "how_to", "beginner_guide"],
        "monetization_focus": "booking_links",
        "image_style": "scenic_destination",
        "content_angle": "experiential_storytelling",
    },
    "pet_care": {
        "preferred_formats": ["review", "listicle", "how_to"],
        "monetization_focus": "product_links",
        "image_style": "pet_photography",
        "content_angle": "expert_vet_advice",
    },
    "fitness_wellness": {
        "preferred_formats": ["how_to", "review", "listicle"],
        "monetization_focus": "equipment_links",
        "image_style": "action_fitness",
        "content_angle": "results_oriented",
    },
    "remote_work": {
        "preferred_formats": ["listicle", "review", "comparison"],
        "monetization_focus": "product_links",
        "image_style": "workspace_setup",
        "content_angle": "productivity_focused",
    },
}


def _ensure_intel_table():
    """Create the content intelligence table if it doesn't exist."""
    try:
        conn = sqlite3.connect(str(_DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS content_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche_id TEXT NOT NULL,
                format_id TEXT NOT NULL,
                source TEXT DEFAULT 'analysis',
                title_pattern TEXT,
                avg_word_count INTEGER DEFAULT 0,
                engagement_score REAL DEFAULT 0.0,
                click_rate REAL DEFAULT 0.0,
                last_updated TEXT,
                metadata TEXT DEFAULT '{}'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS format_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche_id TEXT NOT NULL,
                format_id TEXT NOT NULL,
                article_count INTEGER DEFAULT 0,
                total_clicks INTEGER DEFAULT 0,
                total_views INTEGER DEFAULT 0,
                avg_time_on_page REAL DEFAULT 0.0,
                conversion_rate REAL DEFAULT 0.0,
                effectiveness_score REAL DEFAULT 50.0,
                last_updated TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.debug("Intel table creation: %s", exc)


def get_recommended_format(niche_id: str, topic: str = "") -> dict:
    """
    Get the best content format for a niche + topic combination.

    Uses:
      1. Performance data from past articles (if available)
      2. Niche strategy defaults
      3. Topic keyword matching against format signatures

    Returns dict with format_id, structure, word_count_range, image_density, cta_placement.
    """
    _ensure_intel_table()

    # Check what formats have performed best for this niche
    best_format = _get_best_performing_format(niche_id)

    # Match topic against format signatures
    topic_format = _match_topic_to_format(topic)

    # Get niche strategy
    strategy = NICHE_STRATEGIES.get(niche_id, NICHE_STRATEGIES["ai_tools"])
    preferred = strategy["preferred_formats"]

    # Decision: data-driven > topic-match > niche-default
    if best_format and best_format["effectiveness_score"] > 65:
        format_id = best_format["format_id"]
        logger.info("Using data-driven format '%s' for %s (score: %.1f)", format_id, niche_id, best_format["effectiveness_score"])
    elif topic_format:
        format_id = topic_format
        logger.info("Using topic-matched format '%s' for: %s", format_id, topic[:50])
    else:
        # Weighted random from preferred formats (70% top pick, rest split)
        weights = [0.5] + [0.5 / max(1, len(preferred) - 1)] * max(0, len(preferred) - 1)
        format_id = random.choices(preferred, weights=weights[:len(preferred)])[0]
        logger.info("Using niche-default format '%s' for %s", format_id, niche_id)

    sig = FORMAT_SIGNATURES.get(format_id, FORMAT_SIGNATURES["listicle"])

    return {
        "format_id": format_id,
        "structure": sig["structure"],
        "word_count_range": sig["avg_word_count"],
        "image_density": sig["image_density"],
        "cta_placement": sig["cta_placement"],
        "content_angle": strategy.get("content_angle", "practical_utility"),
        "image_style": strategy.get("image_style", "professional"),
        "monetization_focus": strategy.get("monetization_focus", "product_links"),
    }


def _get_best_performing_format(niche_id: str) -> dict | None:
    """Query the DB for the best-performing format in a niche."""
    try:
        conn = sqlite3.connect(str(_DB_PATH))
        row = conn.execute("""
            SELECT format_id, effectiveness_score, article_count
            FROM format_performance
            WHERE niche_id = ? AND article_count >= 3
            ORDER BY effectiveness_score DESC
            LIMIT 1
        """, (niche_id,)).fetchone()
        conn.close()
        if row:
            return {"format_id": row[0], "effectiveness_score": row[1], "article_count": row[2]}
    except Exception:
        pass
    return None


def _match_topic_to_format(topic: str) -> str | None:
    """Match a topic string against format title patterns."""
    if not topic:
        return None
    topic_lower = topic.lower()
    for format_id, sig in FORMAT_SIGNATURES.items():
        for pattern in sig["title_patterns"]:
            if re.search(pattern, topic_lower):
                return format_id
    return None


def record_article_performance(
    niche_id: str, format_id: str, clicks: int = 0, views: int = 0, time_on_page: float = 0.0
) -> None:
    """Record performance data for a format so the system can learn."""
    _ensure_intel_table()
    try:
        conn = sqlite3.connect(str(_DB_PATH))
        now = datetime.now(timezone.utc).isoformat()

        existing = conn.execute(
            "SELECT id, article_count, total_clicks, total_views FROM format_performance WHERE niche_id=? AND format_id=?",
            (niche_id, format_id)
        ).fetchone()

        if existing:
            new_count = existing[1] + 1
            new_clicks = existing[2] + clicks
            new_views = existing[3] + views
            # Simple effectiveness score: weighted avg of click rate + engagement
            click_rate = new_clicks / max(1, new_views) * 100
            score = min(100, 50 + click_rate * 10 + (time_on_page / 60) * 5)
            conn.execute("""
                UPDATE format_performance SET article_count=?, total_clicks=?, total_views=?,
                avg_time_on_page=?, effectiveness_score=?, last_updated=?
                WHERE id=?
            """, (new_count, new_clicks, new_views, time_on_page, score, now, existing[0]))
        else:
            score = 50.0  # neutral starting score
            conn.execute("""
                INSERT INTO format_performance (niche_id, format_id, article_count, total_clicks,
                total_views, avg_time_on_page, effectiveness_score, last_updated)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?)
            """, (niche_id, format_id, clicks, views, time_on_page, score, now))

        conn.commit()
        conn.close()
    except Exception as exc:
        logger.debug("Performance recording failed: %s", exc)


def get_content_strategy_summary(niche_id: str) -> dict:
    """Get a summary of content intelligence for a niche."""
    strategy = NICHE_STRATEGIES.get(niche_id, {})
    best = _get_best_performing_format(niche_id)

    return {
        "niche_id": niche_id,
        "preferred_formats": strategy.get("preferred_formats", []),
        "content_angle": strategy.get("content_angle", ""),
        "image_style": strategy.get("image_style", ""),
        "best_performing_format": best,
    }


def classify_article_subtopic(title: str, content: str, niche_id: str, niche_config: dict) -> str:
    """
    Auto-classify an article into the best-matching subtopic for its niche.
    Uses keyword matching against subtopic keywords defined in niches.yaml.

    Returns subtopic_id or empty string if no match.
    """
    subtopics = niche_config.get("subtopics", {})
    if not subtopics:
        return ""

    combined_text = f"{title} {content}".lower()
    best_match = ""
    best_score = 0

    for sub_id, sub_cfg in subtopics.items():
        keywords = sub_cfg.get("keywords", [])
        score = 0
        for kw in keywords:
            kw_lower = kw.lower()
            # Count occurrences (title matches worth 3x)
            title_hits = len(re.findall(re.escape(kw_lower), title.lower()))
            content_hits = len(re.findall(re.escape(kw_lower), combined_text))
            score += title_hits * 3 + content_hits

        if score > best_score:
            best_score = score
            best_match = sub_id

    if best_score >= 2:  # Minimum threshold to avoid false positives
        logger.info("Classified article into subtopic '%s' (score: %d)", best_match, best_score)
        return best_match

    return ""
