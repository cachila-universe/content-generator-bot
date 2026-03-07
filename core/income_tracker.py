"""
Income Tracker — Real revenue tracking from all monetization sources.

Revenue sources tracked:
  1. Google AdSense      — ad revenue from website traffic
  2. Amazon Associates   — affiliate commission from product links
  3. YouTube AdSense     — ad revenue from YouTube videos
  4. Other Affiliates    — ShareASale, CJ Affiliate, etc.

Sync methods:
  • Manual entry    — user enters amounts via dashboard
  • Click tracking  — affiliate clicks tracked on website, actual revenue entered manually

Why no full auto-sync?
  - Google AdSense API requires verified publisher (6-month minimum)
  - Amazon Associates has no real-time API for individual sites
  - YouTube Revenue API requires monetised channel (1K subs + 4K watch hours)

Once thresholds are met, API sync can be added incrementally.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_DB_PATH = _PROJECT_ROOT / "data" / "bot.db"

# ── Revenue source definitions ────────────────────────────────────────────

REVENUE_SOURCES = {
    "adsense": {
        "name": "Google AdSense",
        "icon": "📊",
        "description": "Ad revenue from website display ads",
        "auto_sync": False,
        "sync_note": "Manual entry until AdSense API is configured (requires verified publisher)",
    },
    "amazon": {
        "name": "Amazon Associates",
        "icon": "🛒",
        "description": "Affiliate commissions from Amazon product links",
        "auto_sync": False,
        "sync_note": "Manual entry — check Amazon Associates dashboard monthly",
    },
    "youtube": {
        "name": "YouTube Revenue",
        "icon": "▶️",
        "description": "Ad revenue from YouTube videos",
        "auto_sync": False,
        "sync_note": "Manual entry — requires monetised channel (1K subs + 4K hours)",
    },
    "other_affiliates": {
        "name": "Other Affiliates",
        "icon": "🤝",
        "description": "ShareASale, CJ Affiliate, and other programs",
        "auto_sync": False,
        "sync_note": "Manual entry — check each affiliate dashboard",
    },
}


# ── Database ──────────────────────────────────────────────────────────────

def _ensure_tables():
    """Create income tracking tables."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS income_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            description TEXT,
            niche_id TEXT,
            period_start DATE,
            period_end DATE,
            entered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            auto_synced INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_income_source
        ON income_entries(source);

        CREATE INDEX IF NOT EXISTS idx_income_period
        ON income_entries(period_start);
    """)
    conn.commit()
    conn.close()


# ── Manual income entry ──────────────────────────────────────────────────

def add_income(
    source: str,
    amount: float,
    description: str = "",
    niche_id: str = "",
    period_start: str = "",
    period_end: str = "",
) -> int:
    """
    Add a manual income entry.

    Args:
        source: one of REVENUE_SOURCES keys
        amount: income amount in USD
        description: optional note
        niche_id: optional niche association
        period_start: date string (YYYY-MM-DD) for the income period
        period_end: date string (YYYY-MM-DD)

    Returns the entry ID.
    """
    _ensure_tables()
    if source not in REVENUE_SOURCES:
        raise ValueError(f"Unknown revenue source: {source}. Must be one of: {list(REVENUE_SOURCES.keys())}")

    if not period_start:
        period_start = date.today().replace(day=1).isoformat()
    if not period_end:
        period_end = date.today().isoformat()

    conn = sqlite3.connect(str(_DB_PATH))
    cur = conn.execute(
        """INSERT INTO income_entries
           (source, amount, description, niche_id, period_start, period_end, auto_synced)
           VALUES (?, ?, ?, ?, ?, ?, 0)""",
        (source, amount, description, niche_id, period_start, period_end),
    )
    entry_id = cur.lastrowid
    conn.commit()
    conn.close()

    logger.info("Income recorded: $%.2f from %s — %s", amount, source, description)
    return entry_id


def delete_income(entry_id: int) -> bool:
    """Delete an income entry."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    cur = conn.execute("DELETE FROM income_entries WHERE id = ?", (entry_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


# ── Reporting ─────────────────────────────────────────────────────────────

def get_total_income() -> float:
    """Get total all-time income across all sources."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM income_entries"
    ).fetchone()[0]
    conn.close()
    return round(total, 2)


def get_income_by_source() -> dict:
    """Get income breakdown by source."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT source, SUM(amount) as total, COUNT(*) as entries
        FROM income_entries GROUP BY source ORDER BY total DESC
    """).fetchall()
    conn.close()

    result = {}
    for src_id, src_info in REVENUE_SOURCES.items():
        row = next((r for r in rows if r["source"] == src_id), None)
        result[src_id] = {
            **src_info,
            "total": round(row["total"], 2) if row else 0.0,
            "entries": row["entries"] if row else 0,
        }

    return result


def get_income_by_month(months: int = 12) -> list[dict]:
    """Get monthly income for the last N months."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row

    cutoff = (date.today() - timedelta(days=months * 30)).isoformat()
    rows = conn.execute("""
        SELECT
            strftime('%Y-%m', period_start) as month,
            source,
            SUM(amount) as total
        FROM income_entries
        WHERE period_start >= ?
        GROUP BY month, source
        ORDER BY month
    """, (cutoff,)).fetchall()
    conn.close()

    # Group by month
    monthly = {}
    for row in rows:
        m = row["month"]
        if m not in monthly:
            monthly[m] = {"month": m, "total": 0.0, "sources": {}}
        monthly[m]["sources"][row["source"]] = round(row["total"], 2)
        monthly[m]["total"] = round(monthly[m]["total"] + row["total"], 2)

    return list(monthly.values())


def get_income_by_niche() -> dict:
    """Get income breakdown by niche (where niche_id is recorded)."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT niche_id, SUM(amount) as total, COUNT(*) as entries
        FROM income_entries
        WHERE niche_id != '' AND niche_id IS NOT NULL
        GROUP BY niche_id ORDER BY total DESC
    """).fetchall()
    conn.close()
    return {r["niche_id"]: {"total": round(r["total"], 2), "entries": r["entries"]} for r in rows}


def get_recent_entries(limit: int = 50) -> list[dict]:
    """Get recent income entries."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM income_entries ORDER BY entered_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_income_summary() -> dict:
    """
    Full income summary for dashboard.
    Returns total, by source, by month, recent entries.
    """
    return {
        "total_income": get_total_income(),
        "by_source": get_income_by_source(),
        "by_month": get_income_by_month(12),
        "by_niche": get_income_by_niche(),
        "recent_entries": get_recent_entries(20),
        "revenue_sources": REVENUE_SOURCES,
    }
