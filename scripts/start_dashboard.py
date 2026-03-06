#!/usr/bin/env python3
"""Start only the monitoring dashboard (no bot). http://localhost:5002"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from core import analytics_tracker

db_path = PROJECT_ROOT / "data" / "bot.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
analytics_tracker.init_db(db_path)

port = int(os.getenv("DASHBOARD_PORT", 5002))

print(f"\n  🤖 AI Income Bot — Dashboard")
print(f"  URL: http://localhost:{port}")
print(f"  Press Ctrl+C to stop\n")

from dashboard.app import app
app.run(host="0.0.0.0", port=port, debug=False)
