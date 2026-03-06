"""Trend finder using Google Trends (pytrends) to discover viral topics."""

import time
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_trending_topics(niche_id: str, niche_config: dict, db_path: Path) -> list:
    """
    Fetch trending topics for a niche using Google Trends.

    Returns top 5 unique topics sorted by trend interest.
    Falls back to seed keywords if pytrends fails.
    """
    seed_keywords = niche_config.get("seed_keywords", [])
    existing_topics = _get_existing_topics(db_path)

    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 30), retries=2, backoff_factor=0.5)
        candidate_topics: dict[str, int] = {}

        for seed in seed_keywords[:3]:  # Limit to avoid rate limiting
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
                            # "Breakout" means very high interest; assign 200
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
            logger.info("Found %d trending topics for niche %s via pytrends", len(unique_topics), niche_id)
            return unique_topics[:5]

    except ImportError:
        logger.warning("pytrends not installed, falling back to seed keywords")
    except Exception as exc:
        logger.warning("pytrends failed for niche %s: %s — using seed keywords", niche_id, exc)

    # Fallback: return seed keywords not already published
    fallback = [
        kw for kw in seed_keywords
        if kw.lower() not in {e.lower() for e in existing_topics}
    ]
    logger.info("Using %d seed keyword(s) as fallback for niche %s", len(fallback), niche_id)
    return fallback[:5] if fallback else seed_keywords[:5]


def _get_existing_topics(db_path: Path) -> list:
    """Return list of existing post titles from the database."""
    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT title FROM posts").fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []
