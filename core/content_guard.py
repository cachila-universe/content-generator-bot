"""
Content guard — prevents duplicate content, enforces anti-spam measures.

Uses SHA256 fingerprinting and fuzzy title matching to ensure
the bot never generates the same (or very similar) content twice.
"""

import hashlib
import logging
import sqlite3
import re
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def init_content_guard_table(db_path: Path) -> None:
    """Create the content_fingerprints table if it doesn't exist."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS content_fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                title TEXT NOT NULL,
                title_normalized TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fingerprint_niche
            ON content_fingerprints(niche_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_fingerprint_hash
            ON content_fingerprints(content_hash)
        """)
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("Could not init content_fingerprints table: %s", exc)


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip punctuation/numbers, collapse spaces."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z\s]", "", text)      # remove non-alpha
    text = re.sub(r"\s+", " ", text).strip()   # collapse whitespace
    # Remove common filler words for better matching
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
                  "to", "for", "of", "with", "and", "or", "but", "not", "you",
                  "your", "our", "this", "that", "it", "its", "by", "from", "as",
                  "be", "has", "have", "had", "do", "does", "did", "will", "can",
                  "could", "would", "should", "may", "might"}
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words)


def compute_hash(text: str) -> str:
    """SHA256 hash of normalized text."""
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()[:32]


def _word_overlap_ratio(text_a: str, text_b: str) -> float:
    """Compute Jaccard similarity between two normalized texts."""
    words_a = set(normalize_text(text_a).split())
    words_b = set(normalize_text(text_b).split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def is_duplicate_topic(db_path: Path, niche_id: str, topic: str, threshold: float = 0.6) -> bool:
    """
    Check if this topic is too similar to an existing one.

    Uses:
    1. Exact normalized match
    2. Jaccard word overlap (>= threshold)
    """
    normalized = normalize_text(topic)
    if not normalized:
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT topic, title_normalized FROM content_fingerprints WHERE niche_id = ?",
            (niche_id,),
        ).fetchall()
        conn.close()

        for existing_topic, existing_title_norm in rows:
            # Check exact match on normalized topic
            if normalize_text(existing_topic) == normalized:
                logger.info("Duplicate topic (exact match): '%s'", topic)
                return True
            # Check word overlap
            overlap = _word_overlap_ratio(topic, existing_topic)
            if overlap >= threshold:
                logger.info(
                    "Duplicate topic (%.0f%% overlap): '%s' ≈ '%s'",
                    overlap * 100, topic, existing_topic,
                )
                return True
            # Also check against title
            if existing_title_norm:
                title_overlap = _word_overlap_ratio(topic, existing_title_norm)
                if title_overlap >= threshold:
                    logger.info(
                        "Duplicate topic vs title (%.0f%% overlap): '%s' ≈ '%s'",
                        title_overlap * 100, topic, existing_title_norm,
                    )
                    return True

        return False
    except Exception as exc:
        logger.warning("Duplicate check failed: %s", exc)
        return False


def is_duplicate_content(db_path: Path, html_content: str) -> bool:
    """Check if this exact content has been published before."""
    content_hash = compute_hash(html_content)
    try:
        conn = sqlite3.connect(str(db_path))
        row = conn.execute(
            "SELECT id FROM content_fingerprints WHERE content_hash = ?",
            (content_hash,),
        ).fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False


def record_content(db_path: Path, niche_id: str, topic: str, title: str, html_content: str) -> None:
    """Record a content fingerprint after successful publication."""
    content_hash = compute_hash(html_content)
    title_normalized = normalize_text(title)
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            """INSERT INTO content_fingerprints
               (niche_id, topic, title, title_normalized, content_hash)
               VALUES (?, ?, ?, ?, ?)""",
            (niche_id, topic, title, title_normalized, content_hash),
        )
        conn.commit()
        conn.close()
        logger.debug("Recorded content fingerprint for '%s'", title)
    except Exception as exc:
        logger.warning("Failed to record content fingerprint: %s", exc)


def get_content_count(db_path: Path, niche_id: str | None = None) -> int:
    """Return total number of unique content pieces."""
    try:
        conn = sqlite3.connect(str(db_path))
        if niche_id:
            count = conn.execute(
                "SELECT COUNT(*) FROM content_fingerprints WHERE niche_id = ?",
                (niche_id,),
            ).fetchone()[0]
        else:
            count = conn.execute("SELECT COUNT(*) FROM content_fingerprints").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0
