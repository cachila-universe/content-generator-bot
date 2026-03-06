"""Flask dashboard with full bot management: start/stop, niche toggles, manual trigger, settings."""

import os
import yaml
import logging
from pathlib import Path
from urllib.parse import unquote
from flask import Flask, render_template, redirect, request, jsonify
from dotenv import load_dotenv

load_dotenv()

_PROJECT_ROOT = Path(__file__).parent.parent
_DB_PATH = _PROJECT_ROOT / "data" / "bot.db"
_NICHES_CONFIG_PATH = _PROJECT_ROOT / "config" / "niches.yaml"
_SETTINGS_CONFIG_PATH = _PROJECT_ROOT / "config" / "settings.yaml"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SECRET_KEY", "dev-secret-key-change-me")


def _get_db():
    import sys
    sys.path.insert(0, str(_PROJECT_ROOT))
    from core import analytics_tracker
    if not _DB_PATH.exists():
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        analytics_tracker.init_db(_DB_PATH)
    return _DB_PATH


def _load_niches() -> dict:
    try:
        with open(_NICHES_CONFIG_PATH) as f:
            return yaml.safe_load(f).get("niches", {})
    except Exception:
        return {}


def _load_settings() -> dict:
    try:
        with open(_SETTINGS_CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


# ── Page routes ──────────────────────────────────────────────────────────────


@app.route("/")
def index():
    from core import analytics_tracker, bot_state
    db = _get_db()
    stats = analytics_tracker.get_dashboard_stats(db)
    niches = _load_niches()
    settings = _load_settings()
    state = bot_state.get_full_state()
    return render_template(
        "index.html",
        stats=stats,
        niches=niches,
        settings=settings,
        bot_state=state,
        site_title=settings.get("site", {}).get("title", "TechLife Insights"),
    )


@app.route("/posts")
def posts():
    from core import analytics_tracker
    db = _get_db()
    all_posts = analytics_tracker.get_all_posts(db)
    settings = _load_settings()
    return render_template("posts.html", posts=all_posts, settings=settings)


@app.route("/analytics")
def analytics():
    from core import analytics_tracker
    db = _get_db()
    niche_stats = analytics_tracker.get_niche_stats(db)
    settings = _load_settings()
    return render_template("analytics.html", niche_stats=niche_stats, settings=settings)


@app.route("/logs")
def logs():
    from core import analytics_tracker
    db = _get_db()
    limit = _load_settings().get("dashboard", {}).get("log_display_limit", 200)
    recent_logs = analytics_tracker.get_recent_logs(db, limit=limit)
    settings = _load_settings()
    return render_template("logs.html", logs=recent_logs, settings=settings)


@app.route("/niches")
def niches():
    from core import analytics_tracker, bot_state
    db = _get_db()
    niches_config = _load_niches()
    niche_stats = {s["niche_id"]: s for s in analytics_tracker.get_niche_stats(db)}
    state = bot_state.get_full_state()
    settings = _load_settings()
    return render_template(
        "niches.html",
        niches=niches_config,
        niche_stats=niche_stats,
        bot_state=state,
        settings=settings,
    )


@app.route("/settings")
def settings_page():
    from core import bot_state
    settings = _load_settings()
    state = bot_state.get_full_state()
    return render_template("settings.html", settings=settings, bot_state=state)


# ── Click tracking ───────────────────────────────────────────────────────────


@app.route("/track")
def track():
    from core import analytics_tracker
    db = _get_db()
    raw_url = request.args.get("url", "")
    post_slug = request.args.get("slug", "")
    niche_id = request.args.get("niche", "")
    affiliate_url = unquote(raw_url)
    if not affiliate_url:
        return redirect("/"), 302
    if affiliate_url.startswith(("http://", "https://")):
        analytics_tracker.log_click(db, post_slug, affiliate_url, niche_id)
        return redirect(affiliate_url, code=302)
    return redirect("/"), 302


# ── Bot control API ──────────────────────────────────────────────────────────


@app.route("/api/bot/start", methods=["POST"])
def api_bot_start():
    from core import bot_state
    state = bot_state.set_bot_running(True)
    return jsonify({"ok": True, "bot_running": state["bot_running"]})


@app.route("/api/bot/stop", methods=["POST"])
def api_bot_stop():
    from core import bot_state
    state = bot_state.set_bot_running(False)
    return jsonify({"ok": True, "bot_running": state["bot_running"]})


@app.route("/api/bot/state")
def api_bot_state():
    from core import bot_state
    return jsonify(bot_state.get_full_state())


@app.route("/api/niche/<niche_id>/toggle", methods=["POST"])
def api_niche_toggle(niche_id):
    from core import bot_state
    data = request.get_json(force=True)
    enabled = data.get("enabled", True)
    state = bot_state.set_niche_enabled(niche_id, enabled)
    return jsonify({"ok": True, "niche_id": niche_id, "enabled": enabled})


@app.route("/api/platform/<platform>/toggle", methods=["POST"])
def api_platform_toggle(platform):
    from core import bot_state
    data = request.get_json(force=True)
    enabled = data.get("enabled", True)
    state = bot_state.set_platform_enabled(platform, enabled)
    return jsonify({"ok": True, "platform": platform, "enabled": enabled})


@app.route("/api/schedule/update", methods=["POST"])
def api_schedule_update():
    from core import bot_state
    data = request.get_json(force=True)
    allowed_keys = {"randomize_minutes", "cooldown_hours", "max_posts_per_day"}
    filtered = {k: v for k, v in data.items() if k in allowed_keys}
    state = bot_state.update_schedule_settings(filtered)
    return jsonify({"ok": True, "schedule": state.get("schedule", {})})


@app.route("/api/trigger", methods=["POST"])
def api_manual_trigger():
    """Queue a manual content generation run. Requires confirmation token."""
    from core import bot_state
    data = request.get_json(force=True)
    confirm = data.get("confirm")
    if confirm != "CONFIRM_TRIGGER":
        return jsonify({"ok": False, "error": "Missing confirmation token"}), 400

    niche_id = data.get("niche_id", "")
    platforms = data.get("platforms", ["blog"])

    if not niche_id:
        return jsonify({"ok": False, "error": "niche_id required"}), 400

    niches = _load_niches()
    if niche_id not in niches:
        return jsonify({"ok": False, "error": f"Unknown niche: {niche_id}"}), 400

    state = bot_state.add_manual_trigger(niche_id, platforms)
    return jsonify({
        "ok": True,
        "message": f"Manual trigger queued for {niche_id}",
        "queue_length": len(state.get("manual_trigger_queue", [])),
    })


# ── Data API endpoints ───────────────────────────────────────────────────────


@app.route("/api/stats")
def api_stats():
    from core import analytics_tracker, bot_state
    db = _get_db()
    stats = analytics_tracker.get_dashboard_stats(db)
    stats["bot_state"] = bot_state.get_full_state()
    return jsonify(stats)


@app.route("/api/logs")
def api_logs():
    from core import analytics_tracker
    db = _get_db()
    limit = int(request.args.get("limit", 100))
    return jsonify(analytics_tracker.get_recent_logs(db, limit=limit))


@app.route("/api/posts")
def api_posts():
    from core import analytics_tracker
    db = _get_db()
    return jsonify(analytics_tracker.get_all_posts(db))


@app.route("/api/income-chart")
def api_income_chart():
    from core import analytics_tracker
    db = _get_db()
    days = int(request.args.get("days", 30))
    return jsonify(analytics_tracker.get_income_chart_data(db, days=days))


@app.route("/api/posts-chart")
def api_posts_chart():
    from core import analytics_tracker
    db = _get_db()
    return jsonify(analytics_tracker.get_posts_chart_data(db))


if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", 5002))
    _get_db()
    app.run(host="0.0.0.0", port=port, debug=False)
