"""
Bot state manager — controls runtime state from the dashboard.

Persists to data/bot_state.json so state survives restarts.
The scheduler reads this before every job to decide whether to execute.
"""

import json
import logging
import threading
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_STATE_FILE = _PROJECT_ROOT / "data" / "bot_state.json"
_lock = threading.Lock()

# Default state for a fresh install
_DEFAULT_STATE = {
    "bot_running": False,
    "bot_mode": "scheduled",       # "paused" | "scheduled" | "manual"
    "niches": {},           # niche_id -> {"enabled": True/False}
    "platforms": {
        "blog": True,
        "youtube_shorts": True,
        "pinterest": True,
        "twitter": True,
    },
    "schedule": {
        "randomize_minutes": 15,   # ±N minutes jitter added to schedules
        "cooldown_hours": 20,      # minimum hours between posts in same niche
        "max_posts_per_day": 3,    # hard cap across all niches
    },
    "manual_trigger_queue": [],    # list of {"niche_id": ..., "platforms": [...], "requested_at": ...}
    "last_runs": {},               # niche_id -> ISO timestamp of last post
    "posts_today": 0,
    "posts_today_date": "",
    "created_at": "",
    "updated_at": "",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state() -> dict:
    """Load bot state from disk. Returns default state if file missing."""
    with _lock:
        try:
            if _STATE_FILE.exists():
                data = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
                # Merge with defaults so new fields are always present
                merged = {**_DEFAULT_STATE, **data}
                merged["platforms"] = {**_DEFAULT_STATE["platforms"], **data.get("platforms", {})}
                merged["schedule"] = {**_DEFAULT_STATE["schedule"], **data.get("schedule", {})}
                return merged
        except Exception as exc:
            logger.warning("Failed to load bot state: %s", exc)
        return {**_DEFAULT_STATE, "created_at": _now_iso()}


def save_state(state: dict) -> None:
    """Persist bot state to disk."""
    with _lock:
        try:
            state["updated_at"] = _now_iso()
            _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.error("Failed to save bot state: %s", exc)


def init_state(niches_config: dict) -> dict:
    """
    Initialize bot state with niches from config.
    Preserves existing niche toggles; adds new niches as enabled.
    """
    state = load_state()
    for niche_id, niche_cfg in niches_config.items():
        if niche_id not in state.get("niches", {}):
            state.setdefault("niches", {})[niche_id] = {
                "enabled": niche_cfg.get("enabled", True),
            }
    if not state.get("created_at"):
        state["created_at"] = _now_iso()
    save_state(state)
    return state


# ── Convenience getters/setters ──────────────────────────────────────────────


def is_bot_running() -> bool:
    return load_state().get("bot_running", False)


def set_bot_running(running: bool) -> dict:
    state = load_state()
    state["bot_running"] = running
    save_state(state)
    logger.info("Bot %s", "STARTED" if running else "STOPPED")
    return state


def get_bot_mode() -> str:
    """Get current bot mode: 'paused', 'scheduled', or 'manual'."""
    return load_state().get("bot_mode", "scheduled")


def set_bot_mode(mode: str) -> dict:
    """
    Set bot operating mode:
      - 'paused'    → bot is active but does NOTHING (no scheduled jobs execute)
      - 'scheduled' → follows the normal cron schedule
      - 'manual'    → waits for manual trigger only, runs all tasks in dependency order
    """
    valid = {"paused", "scheduled", "manual"}
    if mode not in valid:
        logger.warning("Invalid bot mode '%s', defaulting to 'scheduled'", mode)
        mode = "scheduled"

    state = load_state()
    old_mode = state.get("bot_mode", "scheduled")
    state["bot_mode"] = mode

    # Auto-manage bot_running based on mode
    if mode == "paused":
        state["bot_running"] = True  # Active but idle
    elif mode in ("scheduled", "manual"):
        state["bot_running"] = True

    save_state(state)
    logger.info("Bot mode changed: %s → %s", old_mode, mode)
    return state


def should_execute_scheduled_job() -> bool:
    """Check if scheduled (cron) jobs should execute. Returns False when paused or manual."""
    state = load_state()
    if not state.get("bot_running", False):
        return False
    return state.get("bot_mode", "scheduled") == "scheduled"


def is_niche_enabled(niche_id: str) -> bool:
    state = load_state()
    return state.get("niches", {}).get(niche_id, {}).get("enabled", True)


def set_niche_enabled(niche_id: str, enabled: bool) -> dict:
    state = load_state()
    state.setdefault("niches", {})[niche_id] = {"enabled": enabled}
    save_state(state)
    logger.info("Niche %s %s", niche_id, "ENABLED" if enabled else "DISABLED")
    return state


def is_platform_enabled(platform: str) -> bool:
    state = load_state()
    return state.get("platforms", {}).get(platform, True)


def set_platform_enabled(platform: str, enabled: bool) -> dict:
    state = load_state()
    state.setdefault("platforms", {})[platform] = enabled
    save_state(state)
    logger.info("Platform %s %s", platform, "ENABLED" if enabled else "DISABLED")
    return state


def update_schedule_settings(settings: dict) -> dict:
    state = load_state()
    state["schedule"] = {**state.get("schedule", {}), **settings}
    save_state(state)
    return state


def add_manual_trigger(niche_id: str, platforms: list | None = None) -> dict:
    """Queue a manual content generation run."""
    state = load_state()
    state.setdefault("manual_trigger_queue", []).append({
        "niche_id": niche_id,
        "platforms": platforms or ["blog"],
        "requested_at": _now_iso(),
    })
    save_state(state)
    logger.info("Manual trigger queued for niche: %s", niche_id)
    return state


def pop_manual_trigger() -> dict | None:
    """Pop the oldest manual trigger from the queue."""
    state = load_state()
    queue = state.get("manual_trigger_queue", [])
    if not queue:
        return None
    trigger = queue.pop(0)
    save_state(state)
    return trigger


def record_post_run(niche_id: str) -> None:
    """Record that a post was generated for rate limiting."""
    state = load_state()
    state["last_runs"] = state.get("last_runs", {})
    state["last_runs"][niche_id] = _now_iso()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if state.get("posts_today_date") != today:
        state["posts_today"] = 0
        state["posts_today_date"] = today
    state["posts_today"] = state.get("posts_today", 0) + 1
    save_state(state)


def can_post_now(niche_id: str, ignore_mode: bool = False) -> tuple[bool, str]:
    """
    Check if posting is allowed right now based on rate limits and bot mode.
    Set ignore_mode=True for manual triggers that bypass mode checks.
    Returns (allowed, reason).
    """
    state = load_state()

    if not state.get("bot_running", False):
        return False, "Bot is stopped"

    if not ignore_mode:
        mode = state.get("bot_mode", "scheduled")
        if mode == "paused":
            return False, "Bot is paused — switch to Scheduled or Manual mode"
        if mode == "manual":
            return False, "Bot is in Manual mode — use manual trigger"

    if not state.get("bot_running", False):
        return False, "Bot is stopped"

    niche_state = state.get("niches", {}).get(niche_id, {})
    if not niche_state.get("enabled", True):
        return False, f"Niche '{niche_id}' is disabled"

    # Check daily cap
    schedule = state.get("schedule", {})
    max_per_day = schedule.get("max_posts_per_day", 3)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if state.get("posts_today_date") == today and state.get("posts_today", 0) >= max_per_day:
        return False, f"Daily limit reached ({max_per_day} posts/day)"

    # Check cooldown
    cooldown_hours = schedule.get("cooldown_hours", 20)
    last_run_str = state.get("last_runs", {}).get(niche_id)
    if last_run_str:
        try:
            last_run = datetime.fromisoformat(last_run_str)
            hours_since = (datetime.now(timezone.utc) - last_run).total_seconds() / 3600
            if hours_since < cooldown_hours:
                remaining = round(cooldown_hours - hours_since, 1)
                return False, f"Cooldown: {remaining}h remaining for '{niche_id}'"
        except Exception:
            pass

    return True, "OK"


def get_full_state() -> dict:
    """Return the complete state dict for the dashboard API."""
    return load_state()
