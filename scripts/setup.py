#!/usr/bin/env python3
"""
One-command setup script for AI Content Generator Bot.
Run: python scripts/setup.py
Works on Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import subprocess
import urllib.request
from pathlib import Path

# Ensure we run from project root
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

# ── Colors ─────────────────────────────────────────────────────────────────

def color(text: str, code: str) -> str:
    """Return colored text if stdout supports ANSI codes."""
    if sys.stdout.isatty() or os.getenv("FORCE_COLOR"):
        return f"\033[{code}m{text}\033[0m"
    return text

green = lambda t: color(t, "32")
red   = lambda t: color(t, "31")
yellow = lambda t: color(t, "33")
bold  = lambda t: color(t, "1")
cyan  = lambda t: color(t, "36")

def ok(msg): print(f"  {green('✅')} {msg}")
def fail(msg): print(f"  {red('❌')} {msg}")
def info(msg): print(f"  {cyan('ℹ️')}  {msg}")
def warn(msg): print(f"  {yellow('⚠️')}  {msg}")


def step(title: str):
    print(f"\n{bold(title)}")
    print("─" * 50)


# ── 1. Check Python version ────────────────────────────────────────────────

step("Step 1: Checking Python version")
if sys.version_info < (3, 10):
    fail(f"Python 3.10+ required. Found: {sys.version}")
    sys.exit(1)
ok(f"Python {sys.version.split()[0]}")


# ── 2. Create virtual environment ──────────────────────────────────────────

step("Step 2: Creating virtual environment")
venv_dir = PROJECT_ROOT / ".venv"

if venv_dir.exists():
    warn(".venv already exists — skipping creation")
else:
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, capture_output=True)
        ok("Created .venv")
    except subprocess.CalledProcessError as e:
        fail(f"Failed to create venv: {e.stderr.decode()}")
        sys.exit(1)

# Determine venv python/pip
if sys.platform == "win32":
    venv_python = venv_dir / "Scripts" / "python.exe"
    venv_pip = venv_dir / "Scripts" / "pip.exe"
    activate_cmd = f".venv\\Scripts\\activate"
else:
    venv_python = venv_dir / "bin" / "python"
    venv_pip = venv_dir / "bin" / "pip"
    activate_cmd = "source .venv/bin/activate"

info(f"To activate: {yellow(activate_cmd)}")


# ── 3. Install requirements ────────────────────────────────────────────────

step("Step 3: Installing dependencies")
req_file = PROJECT_ROOT / "requirements.txt"

if not req_file.exists():
    fail("requirements.txt not found!")
    sys.exit(1)

print("  Installing packages (this may take a few minutes)...")
try:
    result = subprocess.run(
        [str(venv_pip), "install", "-r", str(req_file), "--quiet"],
        check=True,
        capture_output=True,
        text=True,
    )
    ok("All dependencies installed")
except subprocess.CalledProcessError as e:
    fail(f"pip install failed:\n{e.stderr}")
    warn("You may need to install manually: pip install -r requirements.txt")


# ── 4. Copy .env.example → .env ───────────────────────────────────────────

step("Step 4: Environment configuration")
env_example = PROJECT_ROOT / ".env.example"
env_file = PROJECT_ROOT / ".env"

if env_file.exists():
    warn(".env already exists — not overwriting")
else:
    shutil.copy(str(env_example), str(env_file))
    ok("Created .env from .env.example")
    warn("Edit .env to set your API keys and configuration")


# ── 5. Create required directories ────────────────────────────────────────

step("Step 5: Creating directories")
dirs = [
    PROJECT_ROOT / "data",
    PROJECT_ROOT / "data" / "logs",
    PROJECT_ROOT / "site" / "output",
    PROJECT_ROOT / "dashboard" / "static" / "js",
]
for d in dirs:
    d.mkdir(parents=True, exist_ok=True)
ok("All directories ready")


# ── 6. Initialize SQLite database ────────────────────────────────────────

step("Step 6: Initializing database")
db_path = PROJECT_ROOT / "data" / "bot.db"

try:
    sys.path.insert(0, str(PROJECT_ROOT))
    from core.analytics_tracker import init_db
    init_db(db_path)
    ok(f"Database initialized: {db_path}")
except Exception as exc:
    warn(f"DB init skipped (will auto-initialize on first run): {exc}")


# ── 7. Download Chart.js ──────────────────────────────────────────────────

step("Step 7: Downloading Chart.js")
chartjs_path = PROJECT_ROOT / "dashboard" / "static" / "js" / "chart.min.js"

if chartjs_path.exists():
    warn("chart.min.js already exists — skipping download")
else:
    chartjs_url = "https://cdn.jsdelivr.net/npm/chart.js/dist/chart.umd.min.js"
    print(f"  Downloading from {chartjs_url} ...")
    try:
        urllib.request.urlretrieve(chartjs_url, str(chartjs_path))
        ok(f"Chart.js saved to {chartjs_path}")
    except Exception as exc:
        warn(f"Could not download Chart.js: {exc}")
        warn("Charts will not render until chart.min.js is in dashboard/static/js/")
        # Create a minimal stub so the dashboard doesn't break
        chartjs_path.write_text("// Chart.js placeholder — download failed\nwindow.Chart = function(){};")


# ── 8. Check Ollama ────────────────────────────────────────────────────────

step("Step 8: Checking Ollama (optional)")
import urllib.request as req_lib
import urllib.error

ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
try:
    with req_lib.urlopen(f"{ollama_host}/api/tags", timeout=3) as resp:
        ok(f"Ollama is running at {ollama_host}")
except Exception:
    warn(f"Ollama not running at {ollama_host}")
    info("Install Ollama: https://ollama.ai/download")
    info("Then run: ollama pull mistral")


# ── 9. Summary ────────────────────────────────────────────────────────────

step("Setup Complete!")
print()
print(bold("  Next steps:"))
print(f"    1. {yellow(f'{activate_cmd}')}")
print(f"    2. Edit {yellow('.env')} with your settings")
print(f"    3. {yellow('python scripts/start_bot.py')}   — start the full bot")
print(f"    4. {yellow('python scripts/start_dashboard.py')} — start dashboard only")
print(f"    5. {yellow('python scripts/test_run.py')}    — test a single cycle")
print()
print(f"  Dashboard: {cyan('http://localhost:5000')}")
print(f"  Site:      {cyan('http://localhost:8080')}")
print()
ok("Setup complete! 🚀")
