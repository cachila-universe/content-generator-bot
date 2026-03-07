"""Trend finder using Google Trends (pytrends) to discover viral topics.

Supports subtopic-aware discovery: rotates through niche subtopics so
every subtopic gets content coverage over time.
"""

import random
import time
import sqlite3
import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_NICHES_PATH = _PROJECT_ROOT / "config" / "niches.yaml"


def _load_subtopics(niche_id: str) -> dict:
    """Load subtopic config for a niche from niches.yaml."""
    try:
        with open(_NICHES_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        niche_cfg = data.get("niches", {}).get(niche_id, {})
        return niche_cfg.get("subtopics", {})
    except Exception:
        return {}


def _pick_subtopic(niche_id: str, db_path: Path) -> tuple:
    """
    Pick the subtopic with the fewest published articles for balanced coverage.

    Returns (subtopic_id, subtopic_config) or ("", {}) if no subtopics.
    """
    subtopics = _load_subtopics(niche_id)
    if not subtopics:
        return "", {}

    # Count existing posts per subtopic
    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT subtopic_id, COUNT(*) FROM posts WHERE niche_id = ? GROUP BY subtopic_id",
            (niche_id,),
        ).fetchall()
        conn.close()
        counts = {r[0]: r[1] for r in rows if r[0]}
    except Exception:
        counts = {}

    # Find subtopic with fewest posts (balanced coverage)
    sub_list = [(sid, scfg, counts.get(sid, 0)) for sid, scfg in subtopics.items()]
    sub_list.sort(key=lambda x: x[2])

    # Among the least-covered, pick randomly to add variety
    min_count = sub_list[0][2]
    least_covered = [s for s in sub_list if s[2] == min_count]
    chosen = random.choice(least_covered)
    return chosen[0], chosen[1]


def get_trending_topics(niche_id: str, niche_config: dict, db_path: Path) -> list:
    """
    Fetch trending topics for a niche using Google Trends.

    Automatically targets the least-covered subtopic for balanced content
    distribution. Returns a list of dicts with 'topic' and 'subtopic_id' keys.

    Returns top 5 unique topics sorted by trend interest.
    Falls back to seed keywords if pytrends fails.
    """
    seed_keywords = niche_config.get("seed_keywords", [])
    existing_topics = _get_existing_topics(db_path)

    # Pick target subtopic for this run
    subtopic_id, subtopic_cfg = _pick_subtopic(niche_id, db_path)
    subtopic_keywords = subtopic_cfg.get("keywords", []) if subtopic_cfg else []

    # Combine: subtopic keywords first (higher priority), then niche seeds
    search_keywords = subtopic_keywords[:3] + [
        kw for kw in seed_keywords if kw not in subtopic_keywords
    ][:2]

    if subtopic_id:
        logger.info(
            "Targeting subtopic '%s' for niche %s (%d keywords)",
            subtopic_id, niche_id, len(search_keywords),
        )

    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 30), retries=2, backoff_factor=0.5)
        candidate_topics: dict[str, int] = {}

        for seed in search_keywords[:4]:  # Use up to 4 keywords
            try:
                pytrends.build_payload([seed], cat=0, timeframe="now 7-d", geo="US")
                related = pytrends.related_queries()

                if seed in related and related[seed]:
                    rising_df = related[seed].get("rising")
                    top_df = related[seed].get("top")

                    if rising_df is not None and not rising_df.empty:
                        for _, row in rising_df.head(10).iterrows():
                            query = str(row.get("query", "")).strip()
                            value_raw = row.get("value", 0)
                            try:
                                value = int(value_raw)
                            except (ValueError, TypeError):
                                value = 200
                            if query and query not in candidate_topics:
                                candidate_topics[query] = value

                    if top_df is not None and not top_df.empty:
                        for _, row in top_df.head(5).iterrows():
                            query = str(row.get("query", "")).strip()
                            try:
                                value = int(row.get("value", 0))
                            except (ValueError, TypeError):
                                value = 0
                            if query and query not in candidate_topics:
                                candidate_topics[query] = value

                time.sleep(1)
            except Exception as exc:
                logger.warning("pytrends error for keyword '%s': %s", seed, exc)
                time.sleep(2)

        # Sort by interest value descending
        sorted_topics = sorted(candidate_topics.items(), key=lambda x: x[1], reverse=True)
        unique_topics = [
            topic for topic, _ in sorted_topics
            if topic.lower() not in {e.lower() for e in existing_topics}
        ]

        if unique_topics:
            logger.info(
                "Found %d trending topics for niche %s (subtopic: %s) via pytrends",
                len(unique_topics), niche_id, subtopic_id or "general",
            )
            # Return dicts with subtopic context
            return [
                {"topic": t, "subtopic_id": subtopic_id}
                for t in unique_topics[:5]
            ]

    except ImportError:
        logger.warning("pytrends not installed, falling back to seed keywords")
    except Exception as exc:
        logger.warning("pytrends failed for niche %s: %s — using seed keywords", niche_id, exc)

    # Fallback: return seed/subtopic keywords not already published
    fallback_pool = (subtopic_keywords or []) + seed_keywords
    fallback = [
        kw for kw in fallback_pool
        if kw.lower() not in {e.lower() for e in existing_topics}
    ]
    if not fallback:
        fallback = seed_keywords[:5]
    logger.info("Using %d seed keyword(s) as fallback for niche %s", len(fallback), niche_id)
    return [
        {"topic": t, "subtopic_id": subtopic_id}
        for t in fallback[:5]
    ]


def _get_existing_topics(db_path: Path) -> list:
    """Return list of existing post titles from the database."""
    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT title FROM posts").fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []
