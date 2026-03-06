#!/usr/bin/env python3
"""
Start the full AI Income Bot: Flask dashboard in background + APScheduler.
Press Ctrl+C to stop.
"""

import os
import sys
import logging
import threading
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(PROJECT_ROOT / "data" / "logs" / "bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("start_bot")

import yaml
from core import analytics_tracker


def load_config() -> dict:
    """Load niches and settings YAML."""
    with open(PROJECT_ROOT / "config" / "niches.yaml") as f:
        niches = yaml.safe_load(f).get("niches", {})
    with open(PROJECT_ROOT / "config" / "settings.yaml") as f:
        settings = yaml.safe_load(f)
    settings["site_url"] = os.getenv("SITE_URL", "http://localhost:8080")
    settings["youtube_channel_name"] = os.getenv("YOUTUBE_CHANNEL_NAME", "TechLife Insights")
    return {"niches": niches, "settings": settings}


def start_flask_daemon():
    """Start Flask dashboard in a background daemon thread."""
    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / "dashboard"))
        from dashboard.app import app

        port = int(os.getenv("DASHBOARD_PORT", 5000))
        logger.info("Starting dashboard on http://localhost:%d", port)
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except Exception as exc:
        logger.error("Dashboard failed to start: %s", exc)


def main():
    # Initialize DB
    db_path = PROJECT_ROOT / "data" / "bot.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    analytics_tracker.init_db(db_path)
    logger.info("Database ready: %s", db_path)

    # Start Flask in daemon thread
    flask_thread = threading.Thread(target=start_flask_daemon, daemon=True, name="flask-dashboard")
    flask_thread.start()
    logger.info("Dashboard thread started")

    # Load config and start scheduler (blocking)
    config = load_config()
    logger.info("Loaded %d niches", len(config["niches"]))

    print("\n" + "=" * 60)
    print("  🤖 AI Content Generator Bot")
    print(f"  Dashboard: http://localhost:{os.getenv('DASHBOARD_PORT', 5000)}")
    print(f"  Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    from core import scheduler
    scheduler.start_scheduler(config, db_path)


if __name__ == "__main__":
    main()
