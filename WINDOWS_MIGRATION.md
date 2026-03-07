# 🖥️ Windows PC Migration Guide
## Moving the AI Content Generator Bot from macOS → Windows

> This guide covers migrating your fully-working bot from a Mac to a Windows PC so it can run 24/7 unattended.

---

## Table of Contents

1. [Why Migrate to Windows?](#1-why-migrate-to-windows)
2. [Windows PC Requirements](#2-windows-pc-requirements)
3. [Step 1 — Install Required Software](#3-step-1--install-required-software)
4. [Step 2 — Clone Your Repository](#4-step-2--clone-your-repository)
5. [Step 3 — Set Up Python Virtual Environment](#5-step-3--set-up-python-virtual-environment)
6. [Step 4 — Install Ollama & AI Models](#6-step-4--install-ollama--ai-models)
7. [Step 5 — Copy Your Credentials & Config](#7-step-5--copy-your-credentials--config)
8. [Step 6 — Configure Environment Variables](#8-step-6--configure-environment-variables)
9. [Step 7 — Test the Bot](#9-step-7--test-the-bot)
10. [Step 8 — Auto-Start on Boot (Task Scheduler)](#10-step-8--auto-start-on-boot-task-scheduler)
11. [Step 9 — Keep PC Awake 24/7](#11-step-9--keep-pc-awake-247)
12. [Useful Windows Commands](#12-useful-windows-commands)
13. [Troubleshooting Windows-Specific Issues](#13-troubleshooting-windows-specific-issues)
14. [Stock Platform Submissions](#14-new-features--stock-platform-submissions)
15. [Real Income Tracking](#15-new-features--real-income-tracking)
16. [Trend Intelligence (Video Types)](#16-new-features--trend-intelligence-video-types)
17. [Affiliate Click Tracking](#17-new-features--affiliate-click-tracking)
18. [Bot Modes](#18-new-features--bot-modes)
19. [Twitter/X Auto-Posting](#19-new-features--twitterx-auto-posting)
20. [Full Pipeline Dependency Chain](#20-full-pipeline-dependency-chain-manual-run-all)

---

## 1. Why Migrate to Windows?

Your current Mac setup requires you to keep the laptop open and running. A dedicated Windows PC can:

- Run 24/7 without interrupting your daily work
- Use far less electricity than a laptop (~$3–6/month vs $8–15/month for a laptop)
- Stay always-on so the bot never misses a scheduled run
- Be controlled remotely via Remote Desktop or TeamViewer

**Ideal hardware**: Any Windows PC built after 2018 with 16 GB RAM and 4+ CPU cores works well.
An older desktop (or a $150–300 refurbished mini PC) is perfect for this.

---

## 2. Windows PC Requirements

| Component | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 (64-bit) | Windows 11 |
| RAM | 8 GB | 16 GB (for llama3.1 70B or better models) |
| CPU | 4 cores | 8 cores (faster article generation) |
| Disk | 20 GB free | 50 GB free (models + database + output) |
| Internet | Any broadband | Any broadband |
| Python | 3.10+ | 3.13 |

> **Mini PC recommendation**: Beelink Mini S12 Pro (~$150, 16GB RAM, N100 CPU) — handles llama3.1:8b perfectly.

---

## 3. Step 1 — Install Required Software

### 3.1 Install Python

1. Go to [python.org/downloads/windows](https://www.python.org/downloads/windows/)
2. Download the latest **Python 3.12 or 3.13** installer
3. Run the installer — **CRITICAL**: Check **"Add python.exe to PATH"** before clicking Install
4. Verify in PowerShell:
   ```powershell
   python --version
   # Should print: Python 3.12.x
   ```

### 3.2 Install Git

1. Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2. Download and run the installer (all defaults are fine)
3. Verify:
   ```powershell
   git --version
   # Should print: git version 2.x.x
   ```

### 3.3 Install Visual C++ Build Tools (needed for some Python packages)

1. Go to [visualstudio.microsoft.com/downloads](https://visualstudio.microsoft.com/downloads/)
2. Scroll down to **Tools for Visual Studio** → **Build Tools for Visual Studio**
3. Download and install, selecting **"Desktop development with C++"**

   > Alternative one-liner (run in PowerShell as Administrator):
   ```powershell
   winget install Microsoft.VisualStudio.2022.BuildTools
   ```

### 3.4 Install ffmpeg (for video generation)

```powershell
# Using winget (Windows Package Manager — built into Windows 11)
winget install Gyan.FFmpeg

# OR download manually from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg\ and add C:\ffmpeg\bin to your PATH
```

Verify: `ffmpeg -version`

---

## 4. Step 2 — Clone Your Repository

Open **PowerShell** (Windows key → type "powershell"):

```powershell
# Go to where you want the project (e.g., Documents)
cd C:\Users\YourName\Documents

# Clone your GitHub repository
git clone https://github.com/cachila-universe/content-generator-bot.git

# Enter the directory
cd content-generator-bot

# Verify files are present
dir
# Should show: config/, core/, dashboard/, scripts/, site/, etc.
```

---

## 5. Step 3 — Set Up Python Virtual Environment

```powershell
# Inside the project directory
cd C:\Users\YourName\Documents\content-generator-bot

# Create virtual environment named 'contentgenerator'
python -m venv contentgenerator

# Activate it
contentgenerator\Scripts\Activate.ps1
```

> **If you get an error about execution policy**, run this first (one-time):
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

You should see `(contentgenerator)` appear at the start of your prompt.

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify
python -c "import flask; import ollama; print('OK')"
```

---

## 6. Step 4 — Install Ollama & AI Models

### Install Ollama

1. Go to [ollama.com/download](https://ollama.com/download)
2. Download and run the Windows installer
3. Ollama runs as a system tray application and starts automatically on boot

### Download AI Models

Open a new PowerShell window (Ollama must be running first):

```powershell
# Primary model for Windows (48 GB+ RAM — best free model available)
ollama pull llama3.3:70b

# Fallback model (32 GB RAM — excellent quality, slightly smaller)
ollama pull llama3.1:70b

# Verify both are available
ollama list
```

> **Which one to use?** See the table below. The bot reads `OLLAMA_MODEL` from your `.env` file — just set the right value for your RAM.

### Choosing the Best Free Model for Your RAM

| Model | RAM Needed | Quality | Speed | Recommended For |
|---|---|---|---|---|
| `llama3.1:8b` | 8 GB | ⭐⭐⭐ Good | Fast (~2 min/article) | Low-RAM machines |
| `qwen2.5:14b` | 10 GB | ⭐⭐⭐⭐ Very Good | Medium | 16 GB RAM |
| `phi4:14b` | 10 GB | ⭐⭐⭐⭐ Very Good | Medium | 16 GB RAM |
| `gemma3:12b` | 8 GB | ⭐⭐⭐⭐ Very Good | Medium (~3 min/article) | 8–16 GB RAM |
| `llama3.1:70b` | 40 GB | ⭐⭐⭐⭐⭐ Excellent | Slow (~20 min/article) | **32 GB RAM — FALLBACK** |
| `llama3.3:70b` | 48 GB | ⭐⭐⭐⭐⭐ Best Free | Slow (~20 min/article) | **48 GB+ RAM — PRIMARY** |

### ✅ Recommended Setup for Your Windows PC (48 GB+ RAM)

**Primary — set this in your `.env`:**
```env
OLLAMA_MODEL=llama3.3:70b
```

This is the best free AI model currently available. It writes near-GPT-4 quality articles.

**Fallback — only switch to this if llama3.3:70b is too slow or runs out of memory:**
```env
OLLAMA_MODEL=llama3.1:70b
```

`llama3.1:70b` needs ~40 GB of RAM and is slightly faster than llama3.3:70b while still being excellent quality.

**How to switch:**
1. Open `.env` in your project folder
2. Change the `OLLAMA_MODEL` line
3. Restart the bot — it will use the new model immediately (no rebuild needed)

---

## 7. Step 5 — Copy Your Credentials & Config

You need to transfer these files from your Mac to the Windows PC:

### Option A: Via GitHub (Recommended)

These files should **not** be in git (they contain secrets). Transfer them manually:

| File | Where it goes | How to transfer |
|---|---|---|
| `.env` | Project root | Copy via USB / email to yourself / encrypted cloud |
| `client_secrets.json` | Project root | Copy via USB / email to yourself |
| `data/youtube_token.json` | `data/` folder | Copy via USB (avoids re-authorizing YouTube) |
| `data/bot.db` | `data/` folder | Optional (transfers all post history) |

### Option B: Via USB Drive

1. On Mac: copy `.env`, `client_secrets.json`, `data/youtube_token.json`, and optionally `data/bot.db` to a USB drive
2. On Windows PC: paste them into the project directory

### Option C: Via Secure Cloud Storage

Upload the sensitive files to an encrypted cloud service (1Password, BitWarden, or password-protected zip) and download on the Windows PC.

---

## 8. Step 6 — Configure Environment Variables

### Option A: `.env` file (Recommended — already set up)

Your `.env` file should be in the project root. Open it with Notepad:

```powershell
notepad .env
```

Update any Mac-specific paths. Common things to check:

```env
# Update if you changed your site URL
SITE_URL=https://tech-life-insights.com

# YouTube - keep the same
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json

# Ollama model
OLLAMA_MODEL=llama3.1

# Dashboard port
DASHBOARD_PORT=5002

# Your Amazon tag
AMAZON_AFFILIATE_TAG=techlife0ac-20

# Timezone (change to your actual timezone)
BOT_TIMEZONE=America/New_York
```

### Option B: Windows System Environment Variables

For extra security, you can set environment variables at the system level:

1. Windows Key → "Edit the system environment variables"
2. Click **Environment Variables...**
3. Under "User variables", click **New**
4. Add each variable from your `.env` file

---

## 9. Step 7 — Test the Bot

```powershell
# Activate virtual environment
contentgenerator\Scripts\Activate.ps1

# Make sure Ollama is running (check system tray)

# Run the test script
$env:PYTHONPATH = "."
python scripts/test_run.py
```

Expected output:
```
============================================================
  🤖 AI Content Generator Bot — Test Run
============================================================
  Using niche: AI Tools & SaaS (ai_tools)
  ▶ Fetching trending topics...
  ✅ Fetching trending topics — OK
  ▶ Generating article: 'best AI tools 2026'...
  ✅ Generating article — OK
     Title: Top AI Productivity Tools for 2026
     Words: 1,243
  ...
  ✅ Publishing to static site — OK
     Published to: /ai_tools/top-ai-productivity-tools-for-2026.html
============================================================
  🎉 Test run complete!
```

If the test passes, your migration is complete. Now set up auto-start.

---

## 10. Step 8 — Auto-Start on Boot (Task Scheduler)

This makes the bot start automatically every time Windows boots — no manual steps needed.

### Create the Startup Script

Create a file called `start_bot_windows.bat` in the project root:

```batch
@echo off
REM AI Content Generator Bot - Windows Startup Script
REM Place in project root and add to Task Scheduler

cd /d "C:\Users\YourName\Documents\content-generator-bot"

REM Activate virtual environment
call contentgenerator\Scripts\activate.bat

REM Set PYTHONPATH
set PYTHONPATH=.

REM Wait for Ollama to be ready (30 seconds)
timeout /t 30 /nobreak

REM Start the bot
python scripts/start_bot.py

REM Keep window open if bot exits
pause
```

> **Update the path**: Change `C:\Users\YourName\Documents\content-generator-bot` to your actual project path.

### Add to Task Scheduler

1. Press **Windows + R**, type `taskschd.msc`, press Enter
2. Click **Create Basic Task...**
3. Name: `AI Content Bot`
4. Trigger: **When the computer starts**
5. Action: **Start a program**
6. Program/script: `C:\Users\YourName\Documents\content-generator-bot\start_bot_windows.bat`
7. Click **Finish**

### Verify Auto-Start Works

1. Restart your Windows PC
2. After boot, open your browser and go to `http://localhost:5002`
3. The dashboard should be accessible within 1–2 minutes of boot

### Alternative: Run as a Windows Service

For more reliability, use NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM from https://nssm.cc/download
# Extract and run:
nssm install ContentBot

# In the NSSM dialog:
# Path: C:\Users\YourName\Documents\content-generator-bot\contentgenerator\Scripts\python.exe
# Startup directory: C:\Users\YourName\Documents\content-generator-bot
# Arguments: scripts/start_bot.py
# Environment: PYTHONPATH=.

nssm start ContentBot
```

---

## 11. Step 9 — Keep PC Awake 24/7

By default, Windows may sleep after a period of inactivity, killing the bot.

### Disable Sleep Mode

1. Windows Key → **Settings** → **System** → **Power & sleep**
2. Set **"When plugged in, PC goes to sleep after"** → **Never**
3. Set **"When plugged in, turn off after"** (screen) → **1 hour** or **Never**

### Prevent Screen Lock

1. Windows Key → **Settings** → **Accounts** → **Sign-in options**
2. Under "Require sign-in", set to **Never**

### Power Settings via Command Line

```powershell
# Run as Administrator:
powercfg /change standby-timeout-ac 0    # Disable sleep on AC power
powercfg /change monitor-timeout-ac 60   # Turn off monitor after 1 hour (saves electricity)
```

---

## 12. Useful Windows Commands

| Task | Command |
|---|---|
| Activate venv | `contentgenerator\Scripts\Activate.ps1` |
| Run bot | `$env:PYTHONPATH = "." ; python scripts/start_bot.py` |
| Run dashboard only | `$env:PYTHONPATH = "." ; python scripts/start_dashboard.py` |
| Test run (one article) | `$env:PYTHONPATH = "." ; python scripts/test_run.py` |
| Generate all niches now | `$env:PYTHONPATH = "." ; python scripts/generate_all_niches.py` |
| Rebuild site | `$env:PYTHONPATH = "." ; python scripts/rebuild_site.py` |
| Check Ollama | `curl http://localhost:11434/api/version` |
| Kill process on port 5002 | `netstat -ano \| findstr :5002` then `taskkill /PID <pid> /F` |
| Check running Python | `tasklist \| findstr python` |

---

## 13. Troubleshooting Windows-Specific Issues

### ❌ `'python' is not recognized as an internal or external command`
**Fix**: Python is not in PATH. Re-install Python and check "Add to PATH" box.

### ❌ `cannot be loaded because running scripts is disabled on this system`
**Fix**: Run in PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ `ModuleNotFoundError` after activating venv
**Fix**: Make sure you activated the venv *before* installing requirements:
```powershell
contentgenerator\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ Ollama not found / `connection refused`
**Fix**: Ollama runs as a Windows tray application. Check the system tray (bottom right). If not there, start it from the Start menu or run `ollama serve` in a terminal.

### ❌ `error: src refspec main does not match any`
**Fix**: Initialize git properly:
```powershell
git init
git add .
git commit -m "Initial"
git branch -M main
git remote add origin https://github.com/cachila-universe/content-generator-bot.git
git push -u origin main
```

### ❌ `FileNotFoundError` for ffmpeg during video generation
**Fix**: Add ffmpeg to PATH:
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract to `C:\ffmpeg`
2. Windows Key → "Edit system environment variables" → Environment Variables
3. Under "System Variables", edit `Path` → Add `C:\ffmpeg\bin`
4. Restart PowerShell

### ❌ Bot stops when you close the terminal
**Fix**: Use `start_bot_windows.bat` via Task Scheduler (see Step 8), or run:
```powershell
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "scripts/start_bot.py"
```

### ❌ Dashboard accessible on localhost but not from other devices on network
**Fix**: Normal behavior — Flask binds to `0.0.0.0` by default. Access from other devices using `http://YOUR_PC_IP:5002`. To find your PC's local IP: `ipconfig | findstr IPv4`.

---

## Quick Reference: Mac → Windows Command Equivalents

| Mac/Linux Command | Windows Equivalent |
|---|---|
| `source contentgenerator/bin/activate` | `contentgenerator\Scripts\Activate.ps1` |
| `PYTHONPATH=. python script.py` | `$env:PYTHONPATH = "." ; python script.py` |
| `python3` | `python` |
| `cat file.txt` | `type file.txt` |
| `nano .env` | `notepad .env` |
| `lsof -i :5002` | `netstat -ano \| findstr :5002` |
| `kill <pid>` | `taskkill /PID <pid> /F` |
| `ps aux \| grep python` | `tasklist \| findstr python` |
| `cp .env.example .env` | `copy .env.example .env` |
| `mkdir -p data/logs` | `mkdir data\logs` |

---

*Last updated: March 2026 — AI Content Generator Bot*

---

## 14. New Features — Stock Platform Submissions

### What It Does

The bot generates AI images and prepares them with platform-specific metadata for stock photo platform submissions. Export creates organized folders with images + JSON sidecars.

### Windows-Specific Notes

- Export directory: `data\stock_exports\<platform>\`
- File paths use backslashes on Windows — the bot handles this automatically
- To open export folder: `explorer data\stock_exports`

### Stock Platforms (All Free to Join)

| Platform | Apply URL | Commission |
|---|---|---|
| Wirestock | contributor.wirestock.io | Varies |
| Adobe Stock | contributor.stock.adobe.com | 33% |
| Shutterstock | submit.shutterstock.com | 15–40% |
| Freepik | contributor.freepik.com | Up to 50% |
| Dreamstime | dreamstime.com/sell | 25–60% |
| Pond5 | pond5.com/sell | 50–60% |
| Depositphotos | depositphotos.com/sell | 34–42% |
| 123RF | 123rf.com/contributors | 30–60% |

**Do NOT upload to:** Alamy, iStock/Getty, Stocksy (they ban AI content)

### Dashboard Usage

1. Open `http://localhost:5002/stock-images`
2. Generate images → Export for Platforms
3. Upload to each platform's web portal
4. Mark as submitted in dashboard

---

## 15. New Features — Real Income Tracking

### What It Does

The dashboard tracks **real income only**. No fake estimates. Revenue from AdSense, Amazon, stock photos, YouTube, and other affiliates is tracked in a central database.

### Dashboard Usage

1. Open `http://localhost:5002/income`
2. Add income entries (source, amount, niche, period)
3. Stock photo sales auto-sync from recorded data
4. All other sources: enter manually from their reporting dashboards

### Revenue Sources

- **Google AdSense** — Manual from AdSense reports
- **Amazon Associates** — Manual from Associates reports
- **Stock Photos** — Auto-synced from bot's sales records
- **YouTube** — Manual from YouTube Studio (requires monetization)
- **Other Affiliates** — Manual from CJ/ShareASale/etc.

---

## 16. New Features — Trend Intelligence (Video Types)

### What Changed

The trend intelligence system now distinguishes between:

- **Short-Form (9:16)** — 7 vertical formats for Shorts/Reels/TikTok (≤60s)
- **Landscape (16:9)** — 6 horizontal formats for YouTube long-form (5–20 min)

### Short-Form Formats

Quick Tips, Split Screen, Hook + Story, Tutorial Steps, Text Reveal, POV Style, Myth Busting

### Landscape Formats

Deep Dive, Top List, Tutorial, Comparison Review, News Roundup, Story Documentary

### Dashboard

View all formats on the **🧠 Intelligence** page — now shows two separate tables.

---

## 17. New Features — Affiliate Click Tracking

The published website now tracks outbound affiliate link clicks. JavaScript in each article page intercepts clicks on affiliate links (Amazon, ShareASale, CJ, etc.) and sends a tracking ping for per-article analytics.

---

## 18. New Features — Bot Modes

The bot supports three operational modes:

| Mode | Behavior |
|---|---|
| ⏸️ Paused | Bot is active but does nothing |
| 📅 Scheduled | Follows cron schedule automatically |
| 🔧 Manual | Only runs when you click trigger buttons |

Switch modes from the dashboard Overview page.

---

## 19. New Features — Twitter/X Auto-Posting

The bot auto-posts to Twitter/X when articles or videos are published.

### Windows Setup

Add Twitter credentials to `config/settings.yaml`:

```yaml
social:
  twitter:
    api_key: "your_key"
    api_secret: "your_secret"
    access_token: "your_token"
    access_token_secret: "your_token_secret"
    bearer_token: "your_bearer"
```

Apply for Twitter API access at [developer.x.com](https://developer.x.com). Free tier allows 1,500 tweets/month.

---

## 20. Full Pipeline Dependency Chain (Manual Run All)

When you click "Run All Pipeline" on the dashboard, the bot executes in this order:

1. 🔍 Trend Intelligence refresh
2. 📝 Article generation (per niche)
3. 🖼️ Stock image generation (per niche)
4. 🎬 Short video generation (per niche)
5. 🐦 Twitter posting (per niche)
6. 📌 Pinterest posting (per niche)
7. 📦 Stock image export for platforms
8. 💰 Income sync (stock earnings)

---

## Quick Reference: Mac → Windows Command Equivalents

| Mac/Linux Command | Windows Equivalent |
|---|---|
| `source contentgenerator/bin/activate` | `contentgenerator\Scripts\Activate.ps1` |
| `PYTHONPATH=. python script.py` | `$env:PYTHONPATH = "." ; python script.py` |
| `python3` | `python` |
| `cat file.txt` | `type file.txt` |
| `nano .env` | `notepad .env` |
| `lsof -i :5002` | `netstat -ano \| findstr :5002` |
| `kill <pid>` | `taskkill /PID <pid> /F` |
| `ps aux \| grep python` | `tasklist \| findstr python` |
| `cp .env.example .env` | `copy .env.example .env` |
| `mkdir -p data/logs` | `mkdir data\logs` |

---

*Last updated: June 2025 — AI Content Generator Bot v3.0*
