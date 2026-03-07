"""Analytics tracker using SQLite for storing posts, logs, clicks, and income snapshots."""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def init_db(db_path: Path) -> None:
    """Initialize all database tables if they don't exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niche_id TEXT NOT NULL,
            niche_name TEXT NOT NULL,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            url TEXT,
            youtube_url TEXT,
            published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            word_count INTEGER DEFAULT 0,
            affiliate_links_count INTEGER DEFAULT 0,
            estimated_clicks INTEGER DEFAULT 0,
            estimated_income REAL DEFAULT 0.0,
            status TEXT DEFAULT 'published'
        );

        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL,
            niche_id TEXT,
            action TEXT NOT NULL,
            message TEXT NOT NULL,
            error TEXT
        );

        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            post_slug TEXT,
            affiliate_url TEXT,
            niche_id TEXT
        );

        CREATE TABLE IF NOT EXISTS income_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date DATE NOT NULL,
            niche_id TEXT NOT NULL,
            total_posts INTEGER DEFAULT 0,
            total_clicks INTEGER DEFAULT 0,
            estimated_income REAL DEFAULT 0.0
        );

        CREATE TABLE IF NOT EXISTS content_fingerprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niche_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            title TEXT NOT NULL,
            title_normalized TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_fingerprint_niche
        ON content_fingerprints(niche_id);

        CREATE INDEX IF NOT EXISTS idx_fingerprint_hash
        ON content_fingerprints(content_hash);
    """)

    conn.commit()
    conn.close()


def log_action(
    db_path: Path,
    level: str,
    action: str,
    message: str,
    niche_id: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """Insert a log entry into bot_logs table."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            "INSERT INTO bot_logs (level, action, message, niche_id, error) VALUES (?, ?, ?, ?, ?)",
            (level, action, message, niche_id, error),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("Failed to log action: %s", exc)


def save_post(db_path: Path, post_data: dict) -> None:
    """Insert a post record into posts table."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            """INSERT OR REPLACE INTO posts
               (niche_id, niche_name, title, slug, url, youtube_url,
                word_count, affiliate_links_count, estimated_clicks, estimated_income, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                post_data.get("niche_id", ""),
                post_data.get("niche_name", ""),
                post_data.get("title", ""),
                post_data.get("slug", ""),
                post_data.get("url", ""),
                post_data.get("youtube_url", ""),
                post_data.get("word_count", 0),
                post_data.get("affiliate_links_count", 0),
                post_data.get("estimated_clicks", 0),
                post_data.get("estimated_income", 0.0),
                post_data.get("status", "published"),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("Failed to save post: %s", exc)


def log_click(db_path: Path, post_slug: str, affiliate_url: str, niche_id: str) -> None:
    """Insert a click record into clicks table."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            "INSERT INTO clicks (post_slug, affiliate_url, niche_id) VALUES (?, ?, ?)",
            (post_slug, affiliate_url, niche_id),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("Failed to log click: %s", exc)


def take_income_snapshot(db_path: Path, avg_commission: float, estimated_ctr: float) -> None:
    """Compute and store income snapshot for each niche."""
    try:
        conn = sqlite3.connect(str(db_path))
        today = date.today().isoformat()

        niches = conn.execute("SELECT DISTINCT niche_id FROM posts").fetchall()
        for (niche_id,) in niches:
            total_posts = conn.execute(
                "SELECT COUNT(*) FROM posts WHERE niche_id = ?", (niche_id,)
            ).fetchone()[0]
            total_clicks = conn.execute(
                "SELECT COUNT(*) FROM clicks WHERE niche_id = ?", (niche_id,)
            ).fetchone()[0]
            estimated_income = total_clicks * estimated_ctr * avg_commission

            # Upsert: delete existing snapshot for today+niche, then insert
            conn.execute(
                "DELETE FROM income_snapshots WHERE snapshot_date = ? AND niche_id = ?",
                (today, niche_id),
            )
            conn.execute(
                """INSERT INTO income_snapshots
                   (snapshot_date, niche_id, total_posts, total_clicks, estimated_income)
                   VALUES (?, ?, ?, ?, ?)""",
                (today, niche_id, total_posts, total_clicks, estimated_income),
            )

        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("Failed to take income snapshot: %s", exc)


def get_dashboard_stats(db_path: Path) -> dict:
    """Return total_posts, total_videos, total_clicks, estimated_income, recent_logs, posts_by_niche."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        total_posts = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        total_videos = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE youtube_url IS NOT NULL AND youtube_url != ''"
        ).fetchone()[0]
        total_clicks = conn.execute("SELECT COUNT(*) FROM clicks").fetchone()[0]

        avg_commission = float(
            conn.execute(
                "SELECT COALESCE(AVG(estimated_income / NULLIF(estimated_clicks, 0)), 25.0) FROM posts"
            ).fetchone()[0]
            or 25.0
        )
        estimated_income = total_clicks * 0.02 * avg_commission

        recent_logs = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM bot_logs ORDER BY timestamp DESC LIMIT 10"
            ).fetchall()
        ]

        posts_by_niche = [
            dict(row)
            for row in conn.execute(
                "SELECT niche_id, niche_name, COUNT(*) as count FROM posts GROUP BY niche_id"
            ).fetchall()
        ]

        conn.close()
        return {
            "total_posts": total_posts,
            "total_videos": total_videos,
            "total_clicks": total_clicks,
            "estimated_income": round(estimated_income, 2),
            "recent_logs": recent_logs,
            "posts_by_niche": posts_by_niche,
        }
    except Exception:
        return {
            "total_posts": 0,
            "total_videos": 0,
            "total_clicks": 0,
            "estimated_income": 0.0,
            "recent_logs": [],
            "posts_by_niche": [],
        }


def get_recent_logs(db_path: Path, limit: int = 100) -> list:
    """Return recent log entries as list of dicts."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM bot_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_all_posts(db_path: Path) -> list:
    """Return all posts as list of dicts."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM posts ORDER BY published_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_niche_stats(db_path: Path) -> list:
    """Return per-niche statistics as list of dicts."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT
                p.niche_id,
                p.niche_name,
                COUNT(*) as total_posts,
                SUM(CASE WHEN p.youtube_url != '' AND p.youtube_url IS NOT NULL THEN 1 ELSE 0 END) as total_videos,
                COALESCE(c.total_clicks, 0) as total_clicks,
                COALESCE(SUM(p.estimated_income), 0.0) as estimated_income
               FROM posts p
               LEFT JOIN (
                   SELECT niche_id, COUNT(*) as total_clicks FROM clicks GROUP BY niche_id
               ) c ON p.niche_id = c.niche_id
               GROUP BY p.niche_id"""
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_income_chart_data(db_path: Path, days: int = 30) -> dict:
    """Return Chart.js compatible data for income line chart."""
    try:
        conn = sqlite3.connect(str(db_path))
        since = (datetime.now() - timedelta(days=days)).date().isoformat()
        rows = conn.execute(
            """SELECT snapshot_date, SUM(estimated_income) as total_income
               FROM income_snapshots
               WHERE snapshot_date >= ?
               GROUP BY snapshot_date
               ORDER BY snapshot_date""",
            (since,),
        ).fetchall()
        conn.close()
        labels = [r[0] for r in rows]
        data = [round(r[1], 2) for r in rows]
        return {"labels": labels, "data": data}
    except Exception:
        return {"labels": [], "data": []}


def get_posts_chart_data(db_path: Path) -> dict:
    """Return Chart.js compatible data for posts bar chart."""
    try:
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute(
            "SELECT niche_name, COUNT(*) FROM posts GROUP BY niche_id ORDER BY niche_name"
        ).fetchall()
        conn.close()
        labels = [r[0] for r in rows]
        data = [r[1] for r in rows]
        return {"labels": labels, "data": data}
    except Exception:
        return {"labels": [], "data": []}


def delete_post(db_path: Path, post_id: int):
    """Delete a post by ID. Returns the deleted post dict, or None if not found."""
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if not row:
            conn.close()
            return None
        post_data = dict(row)
        slug = post_data.get("slug", "")
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        if slug:
            conn.execute("DELETE FROM clicks WHERE post_slug = ?", (slug,))
        conn.commit()
        conn.close()
        return post_data
    except Exception as exc:
        logger.warning("Failed to delete post %d: %s", post_id, exc)
        return None
