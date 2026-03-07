# 🚀 Complete Setup Manual — AI Content Generator Bot

> **Estimated setup time:** 20–30 minutes (first-time), 5 minutes (returning)

---

## Table of Contents

1.  [Prerequisites](#1-prerequisites)
2.  [Install System Dependencies](#2-install-system-dependencies)
3.  [Clone & Install the Project](#3-clone--install-the-project)
4.  [Install & Configure Ollama (Local AI)](#4-install--configure-ollama-local-ai)
5.  [Environment Variables (.env)](#5-environment-variables-env)
6.  [Configure Your Niches & Settings](#6-configure-your-niches--settings)
7.  [Run the Dashboard Locally](#7-run-the-dashboard-locally)
8.  [Run the Bot](#8-run-the-bot)
9.  [YouTube API Setup (Shorts)](#9-youtube-api-setup-shorts)
10.  [Pinterest API Setup](#10-pinterest-api-setup)
11.  [Domain & Hosting Setup](#11-domain--hosting-setup)
12.  [Google AdSense Application](#12-google-adsense-application)
13.  [Going Live Checklist](#13-going-live-checklist)
14.  [Troubleshooting](#14-troubleshooting)

---

## 1. Prerequisites

| Requirement | Minimum | Recommended |
|---|---|---|
| macOS / Linux / Windows WSL | Any | macOS Ventura+ |
| Python | 3.10 | 3.12 |
| RAM | 8 GB | 16 GB (for Ollama AI models) |
| Disk Space | 10 GB | 20 GB (AI models ~4 GB each) |
| Internet | Required | Required |

---

## 2. Install System Dependencies

### Step 2: Install System Dependencies

**macOS (Homebrew):**

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Install ffmpeg (needed for video generation)
brew install ffmpeg

# Verify installation
python3 --version   # Should show 3.10+
ffmpeg -version     # Should show ffmpeg info
```

**Ubuntu / Debian:**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.12 python3.12-venv python3-pip ffmpeg -y
```

**Windows (via WSL):**

```powershell
# Install WSL first (run in PowerShell as Admin)
wsl --install -d Ubuntu

# Then follow Ubuntu instructions inside WSL
```

---

## 3. Clone & Install the Project

```bash
# Navigate to where you want the project
cd ~/Documents/Github/Projects

# Clone the repository (or if you already have it, skip this)
# git clone https://github.com/cachila-universe/content-generator-bot.git

# Enter the project
cd content-generator-bot

# Create a Python virtual environment
python3 -m venv contentgenerator

# Activate it
source contentgenerator/bin/activate   # macOS/Linux
# .\contentgenerator\Scripts\Activate   # Windows

# Install all Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import flask; import ollama; print('✅ All dependencies installed')"
```

---

## 4. Install & Configure Ollama (Local AI)

Ollama runs AI models locally on your machine. **No API keys needed. No cloud costs. 100% private.**

### Install Ollama

```bash
# macOS / Linux — one command
curl -fsSL https://ollama.com/install.sh | sh

# Or on macOS via Homebrew:
brew install ollama
```

For Windows: Download from [https://ollama.com/download](https://ollama.com/download)

### Start Ollama & Download the Mistral Model

```bash
# Start Ollama (runs in background)
ollama serve &

# Download the Mistral 7B model (used for content generation)
# This downloads ~4 GB on first run
ollama pull mistral

# Verify it works
ollama run mistral "Say hello in one sentence"
```

**Alternative models** (if you want better quality and have more RAM):

```bash
ollama pull llama3.1          # 8B params, great quality
```

If you switch models, update `core/llm_writer.py` → change the model name in the `ollama.chat()` call.

### Verify Ollama is Running

```bash
curl http://localhost:11434/api/tags# Should return JSON with your installed models
```

---

## 5. Environment Variables (.env)

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```ini
# ── Required ──────────────────────────────────────────

# Dashboard
DASHBOARD_SECRET_KEY=your-random-secret-key-here-change-me

# ── YouTube (Optional — only if using YouTube Shorts) ──
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_API_SCOPES=https://www.googleapis.com/auth/youtube.upload

# ── Pinterest (Optional — only if using Pinterest) ────
PINTEREST_ACCESS_TOKEN=your_pinterest_token
PINTEREST_BOARD_ID=your_board_id

# ── Site ──────────────────────────────────────────────
SITE_URL=https://tech-life-insights.com
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 6. Configure Your Niches & Settings

### `config/settings.yaml`

Key settings to review:

```yaml
site:
  title: "TechLife Insights"                 # Your site name
  tagline: "Smart Guides for Modern Living"

video:
  format: "shorts"                           # "shorts" for YouTube Shorts (recommended)

platforms:
  blog: true                                 # Generate blog articles
  youtube_shorts: true                       # Generate YouTube Shorts
  pinterest: true                            # Generate Pinterest pins

scheduler:
  timezone: "America/New_York"               # Change to YOUR timezone
  max_posts_per_day: 3                       # Anti-spam: max posts per day
  cooldown_hours: 20                         # Hours between posts per niche
  randomize_minutes: 15                      # ±15 min jitter on schedule
```

### `config/niches.yaml`

Each niche has:

-   **seed_keywords** — what Google Trends searches for
-   **affiliate_programs** — your affiliate links (replace `YOUR_ID` with your actual IDs)
-   **schedule times** — when each niche publishes

**To add a new niche**, copy an existing block and modify it:

```yaml
niches:
  my_new_niche:
    name: "My New Niche"
    enabled: true
    seed_keywords:
      - "keyword 1"
      - "keyword 2"
    affiliate_programs:
      - name: "Program Name"
        url: "https://example.com?aff=YOUR_ID"
        keywords: ["keyword", "another keyword"]
    post_schedule_hour: 10
    post_schedule_minute: 0
    video_schedule_hour: 12
    video_schedule_minute: 0
    pinterest_schedule_hour: 14
    pinterest_schedule_minute: 0
```

---

## 7. Run the Dashboard Locally

```bash
# Make sure your venv is activated
source contentgenerator/bin/activate

# Start the dashboard
python scripts/start_dashboard.py

# Or manually:
python -m dashboard.app
```

Open your browser: **[http://localhost:5000](http://localhost:5000)**

You'll see:

-   📊 **Overview** — stats, bot status, manual trigger
-   📝 **Posts** — all published articles
-   📈 **Analytics** — charts per niche
-   🎯 **Niches** — toggle niches on/off
-   🗒️ **Logs** — real-time bot activity
-   ⚙️ **Settings** — platform toggles, schedule controls

### Dashboard Controls

| Action | How |
|---|---|
| Start Bot | Click **▶ Start** in top bar |
| Stop Bot | Click **⏹ Stop** in top bar |
| Toggle a niche | Niches page → flip the toggle switch |
| Toggle a platform | Settings page → flip platform switches |
| Manual trigger | Overview → Arm Trigger → Select niche → Fire |

Overview → Arm Trigger → Select niche → Fire

---

## 8. Run the Bot

```bash
# Option 1: Via the dashboard (recommended)
# Start the dashboard, then click "Start" in the top bar

# Option 2: Command line
python scripts/start_bot.py

# Option 3: One-time test run
python scripts/test_run.py

# Option 4: Rebuild all site pages manually
PYTHONPATH=. python scripts/rebuild_site.py
```

The bot will:

1.  Check Google Trends for each niche
2.  Pick a unique topic (dedup check)
3.  Generate an article via Ollama AI
4.  Optimize SEO meta tags
5.  Inject affiliate links
6.  Publish to your site
7.  Generate a YouTube Short (if enabled)
8.  Upload to YouTube (if configured)
9.  Create a Pinterest pin (if configured)
10.  Log everything to the database

---

## 9. YouTube API Setup (Shorts)

### Step 1: Create a Google Cloud Project

1.  Go to [Google Cloud Console](https://console.cloud.google.com/)
2.  Click **Select a project** → **New Project**
3.  Name it `content-bot-youtube`, click **Create**

### Step 2: Enable the YouTube Data API v3

1.  Go to **APIs & Services** → **Enable APIs and Services**
2.  Search for **YouTube Data API v3**
3.  Click **Enable**

### Step 3: Create OAuth 2.0 Credentials

1.  Go to **APIs & Services** → **Credentials**
2.  Click **+ Create Credentials** → **OAuth client ID**
3.  If prompted, configure the **OAuth consent screen**:
    -   User type: **External**
    -   App name: `Content Bot`
    -   Support email: your email
    -   Scopes: add `youtube.upload`
4.  Application type: **Desktop app**
5.  Click **Create**, then **Download JSON**
6.  Save as `client_secrets.json` in your project root

### Step 3b: Add Yourself as a Test User ⚠️ Required

Google blocks OAuth apps that haven't completed their verification process. Since this is your **personal bot**, you never need to verify — you just need to add your own email as an approved tester.

**Finding the Test Users section:**

1.  Go to [console.cloud.google.com](https://console.cloud.google.com)
2.  Make sure your **project is selected** in the top-left dropdown (should say `content-bot-youtube` or whatever you named it)
3.  In the left sidebar: **APIs & Services** → **OAuth consent screen**
4.  On that page, look for the **"Audience"** tab (Google recently renamed the section)
5.  Scroll down — you'll see **"Test users"** with a **+ Add Users** button

**If you don't see "Test users":**

Your app may be set to **Internal** instead of **External**. Check the top of the OAuth consent screen page — it should say **User type: External**. If it says Internal, click **Make External**.

**Quick URL shortcut:**

Paste this into your browser, replacing `YOUR_PROJECT_ID` with your actual project ID:

```
https://console.cloud.google.com/apis/credentials/consent?project=YOUR_PROJECT_ID
```

Your project ID is visible in Google Cloud Console's top bar (looks like `content-bot-youtube-123456`).

**Add your email:**

1.  Click **+ Add Users**
2.  Enter your Google account email (e.g. `cachila.universe@gmail.com`)
3.  Click **Save**

> You only need to do this once. The bot will use the saved `data/youtube_token.json` on all future runs.

### Step 4: First Authentication

```bash
source contentgenerator/bin/activate
python -c "from core.youtube_uploader import authenticate; authenticate()"
```

This opens your browser for OAuth. Sign in with the **same email you added as a test user** and click **Allow**. A token is saved to `data/youtube_token.json` automatically.

> **If you see "Access blocked" / Error 403:** You haven't added your email as a test user yet. Complete Step 3b above first.

> ⚠️ **YouTube quota**: New projects get 10,000 units/day. Each upload costs ~1,600 units. That's ~6 uploads/day. The bot's `max_posts_per_day: 3` stays safely within this limit.

---

## 10. Pinterest API Setup

### Step 1: Create a Pinterest Developer App

1.  Go to [Pinterest Developers](https://developers.pinterest.com/)
2.  Click **My Apps** → **Create app**
3.  Fill in your app details
4.  Under **Redirect URIs**, add `https://localhost:3000/callback`

### Step 2: Get Access Token

1.  In your Pinterest app, go to **Generate token**
2.  Select scopes: `boards:read`, `pins:write`
3.  Copy the access token

### Step 3: Get Your Board ID

1.  Go to your Pinterest board URL (e.g., `https://pinterest.com/yourusername/your-board/`)
2.  Use the API to get the board ID:

```bash
curl -X GET "https://api.pinterest.com/v5/boards"   -H "Authorization: Bearer YOUR_TOKEN"
```

3.  Copy the board `id` from the response

### Step 4: Update `.env`

```ini
PINTEREST_ACCESS_TOKEN=your_token_here
PINTEREST_BOARD_ID=your_board_id_here
```

---

## 11. Domain & Hosting Setup

### Recommended Domain Name

**`tech-life-insights.com`**

Why this name works:

-   ✅ Professional and brandable
-   ✅ Matches your site title in `settings.yaml`
-   ✅ Covers all your niches (tech, life, insights)
-   ✅ SEO-friendly (dashes are fine — used by major brands like "tech-insider.com")
-   ✅ Easy to remember and spell
-   ✅ Available as `.com` (verified!)

**Alternative options** if `tech-life-insights.com` becomes unavailable:

-   `tech-life-insights.io`
-   `smart-tech-insights.com`
-   `tech-life-guides.com`
-   `insightful-tech.com`

### Step 1: Buy the Domain from Cloudflare

#### 1a. Create a Cloudflare Account

1.  Go to [cloudflare.com](https://www.cloudflare.com)
2.  Click **Sign up** (top right)
3.  Enter your email and create a password
4.  Verify your email
5.  You're now in the Cloudflare dashboard

#### 1b. Purchase Your Domain

1.  In the Cloudflare dashboard, click **Registrar** in the left sidebar (or search for it)
2.  Click **Register domain** or **Transfer domain** (if you have one elsewhere)
3.  In the search box, type `tech-life-insights.com`
4.  Click **Search**
5.  If available, you'll see a price (typically $8.95/year for `.com`)
6.  Click **Add to cart**
7.  Review your cart → **Proceed to checkout**
8.  Enter your payment info and complete purchase
9.  You now own the domain! ✅

> **Cloudflare Registrar is $1.80 cheaper than Namecheap on renewals because they don't mark up.** You'll see the real ICANN registration price.

#### 1c. Verify Domain Settings

1.  Back in the Cloudflare dashboard, go to **Registrar** → **Domains**
2.  Click on `tech-life-insights.com`
3.  Verify:
    -   **Domain Status**: Active ✅
    -   **Nameservers**: Should show Cloudflare nameservers (ns1.cloudflare.com, ns2.cloudflare.com, etc.)
    -   **Auto-renewal**: Toggle ON (recommended) so you don't lose the domain

> The nameservers are **automatically set to Cloudflare** — you don't need to change anything at a different registrar because **you bought directly from Cloudflare**.

---

### Step 2: Set Up Free Hosting with Cloudflare Pages

Since the bot generates static HTML files, you can host for **free** on Cloudflare Pages.

#### 2a. Prepare Your GitHub Repository

First, make sure your bot code is on GitHub:

```bash
cd ~/Documents/Github/Projects/content-generator-bot

# Initialize git repository (if not already done)
git init

# Add remote origin with your GitHub username
git remote set-url origin https://github.com/YOUR_USERNAME/content-generator-bot.git
# (replace YOUR_USERNAME with your actual GitHub username)

# Stage and commit all files
git add .
git commit -m "Initial bot setup"

# Push to GitHub
git push -u origin main
```

#### 2b. Create Cloudflare Pages Project

1.  In the Cloudflare dashboard, go to **Workers & Pages** (left sidebar)
2.  Click the **Pages** tab
3.  Click **Create application** → **Connect to Git**
4.  **Authorize GitHub** (click the button, log in to GitHub)
5.  **Select your repository**: `content-generator-bot`
6.  Click **Begin setup**

#### 2c. Configure Build Settings

1.  **Project name**: `content-generator-bot` (or leave as suggested)
2.  **Production branch**: `main`
3.  **Framework preset**: `None` (since it's a static site)
4.  **Build command**: *(leave empty — your bot generates static HTML)*
5.  **Build output directory**: `site/output`
6.  **Environment variables**: *(leave empty for now)*
7.  Click **Save and deploy**

> Cloudflare will now build and deploy your site. Check the **Deployments** tab to see the build log.

#### 2d. Connect Your Domain (Detailed Steps)

**Prerequisites:**
- ✅ Cloudflare Pages deployment completed
- ✅ Your domain registered with Cloudflare Registrar
- ✅ Domain nameservers pointing to Cloudflare (automatic if you bought through Cloudflare)

**Step 1: Access Cloudflare Pages Settings**

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. In the left sidebar, click **Workers & Pages**
3. Click the **Pages** tab
4. Find your `content-generator-bot` project
5. Click on your project to open it
6. Click the **Settings** tab (near the top)

**Step 2: Add Your Primary Domain**

1. Scroll down to the **Domains** section
2. Click **Add domain**
3. In the dialog, type your domain: `tech-life-insights.com`
   - Do NOT include `https://` or `www.` at this stage
   - Just the domain: `tech-life-insights.com`
4. Click **Continue**

**Step 3: Verify Domain Ownership**

Cloudflare will automatically verify your domain because:
- You registered it through Cloudflare Registrar
- Nameservers are already pointing to Cloudflare
- No additional DNS records needed

Status should show: **Active** ✅

Your site is now live at:
- `https://tech-life-insights.com` ✅
- `https://www.tech-life-insights.com` (auto-redirects)

**Step 4: Add WWW Subdomain (Optional)**

To explicitly add `www` as an alias:

1. Still in **Domains** section
2. Click **Add domain** again
3. Type: `www.tech-life-insights.com`
4. Click **Continue**
5. Verify and confirm

**Troubleshooting:**

| Issue | Solution |
|-------|----------|
| Domain not verifying | Check that nameservers point to Cloudflare (usually automatic). See [Nameserver Guide](https://developers.cloudflare.com/dns/zone-setup/ns-records/) |
| "Domain already exists" | You already added it. Check the **Domains** list or try a subdomain |
| Getting Cloudflare error page | Wait 5-10 minutes for DNS to propagate, then refresh |
| Site shows "Not Found" | Ensure `site/output/index.html` exists locally and was pushed to GitHub |

**Verification Checklist:**

```bash
# Test your domain
curl -I https://tech-life-insights.com

# Expected output should include:
# HTTP/2 200
# cf-cache-status: HIT
# server: cloudflare
```

**Advanced: Point a Subdomain (e.g., blog.tech-life-insights.com)**

1. Follow the same steps but use `blog.tech-life-insights.com`
2. Create a separate Pages project (if desired) or use the same one
3. Configure DNS record (if needed) at Cloudflare → DNS

---

### Step 3: Enable SSL/TLS

1.  In Cloudflare dashboard, go to **SSL/TLS** (left sidebar)
2.  Click the **Overview** tab
3.  Under **SSL/TLS encryption mode**, select **Full (strict)**
4.  This ensures all traffic is encrypted

---

### Step 4: Set Up Auto-Deployment

Every time the bot publishes new content to `site/output/`, you want it automatically deployed. Here's how:

#### Option A: GitHub Actions (Recommended — Fully Automated)

**What This Does:**
Every time the bot creates new content and pushes it to GitHub, your live site updates automatically within minutes. ✅

**Step 1: Create the GitHub Actions Workflow File**

Create a new file: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches:
      - main
    paths:
      - 'site/output/**'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: content-generator-bot
          directory: site/output
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

**Step 2: Get Your Cloudflare API Token**

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Click your **Profile icon** (bottom left) → **My Profile**
3. Click **API Tokens** (left sidebar)
4. Click **Create Token** button
5. Find template: **Edit Cloudflare Workers** → Click **Use template**
6. Configure permissions:
   - ✅ Account Resources: Include (Specific) → Select your account
   - ✅ Permissions: 
     - `Pages:Edit` (allows updating Pages)
     - `Pages:Build and Deploy` (allows deployments)
   - ✅ Zone Resources: All zones (or specific domain only)
7. Set **TTL** to 12 months or as needed
8. Click **Create Token**
9. **Copy the token immediately** (you won't see it again!)

**Step 3: Get Your Cloudflare Account ID**

1. In [Cloudflare Dashboard](https://dash.cloudflare.com/), look at the **bottom left corner**
2. You'll see your account information
3. The **Account ID** is a 32-character hex string (example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)
4. Copy it

**Step 4: Add Secrets to GitHub**

1. Go to your GitHub repository: `https://github.com/cachila-universe/content-generator-bot`
2. Click **Settings** (top right)
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** (green button)

**Add Secret 1: CLOUDFLARE_API_TOKEN**
- Name: `CLOUDFLARE_API_TOKEN`
- Value: *(paste your API token from Step 2)*
- Click **Add secret**

**Add Secret 2: CLOUDFLARE_ACCOUNT_ID**
- Name: `CLOUDFLARE_ACCOUNT_ID`
- Value: *(paste your Account ID from Step 3)*
- Click **Add secret**

**Step 5: Test the Workflow**

1. In GitHub, go to **Actions** tab
2. You should see "Deploy to Cloudflare Pages" workflow
3. Click **Run workflow** → **Run workflow** (manual trigger)
4. Wait ~2 minutes for it to complete
5. Check status: Green ✅ = Success, Red ❌ = Error

**Troubleshooting:**

| Error | Fix |
|-------|-----|
| `Invalid API Token` | Regenerate token with correct permissions in Cloudflare |
| `Account ID not found` | Copy the full 32-character hex string, not your email |
| `Project not found` | Make sure project name is exactly `content-generator-bot` |
| Workflow doesn't run | Check that changes are in `site/output/` folder |

**How to Monitor Deployments:**

1. After bot publishes content, GitHub Actions automatically triggers
2. Check deployment status in GitHub: **Actions** tab
3. Check live site status in Cloudflare: **Workers & Pages** → **Deployments** tab
4. Site updates within 2-5 minutes of push

#### Option B: Manual Deploy (Simple but requires manual pushes)

```bash
# After the bot publishes content:
cd ~/Documents/Github/Projects/content-generator-bot

# Stage only the new content files
git add site/output/

# Commit with a timestamp
git commit -m "Bot published new content: $(date '+%Y-%m-%d %H:%M')"

# Push to GitHub (Cloudflare automatically deploys from main branch)
git push origin main
```

---

### Step 5: Configure DNS Records (Optional but Recommended)

Most DNS is auto-configured, but you can customize:

1.  In Cloudflare dashboard → **DNS**
2.  You'll see auto-generated records for your domain
3.  Leave them as-is for now (Cloudflare handles everything)

> If you want email forwarding for `admin@tech-life-insights.com`, you can add custom MX records here later.

---

### Step 6: Verify Your Site is Live

1.  Open your browser
2.  Go to `https://tech-life-insights.com`
3.  You should see your site (initially showing `site/templates/index.html`)

✅ **Your site is now live on Cloudflare Pages with a custom domain!**

---

## 12. Google AdSense Application

### When to Apply

**Apply for AdSense AFTER you have:**

| Requirement | Target |
|---|---|
| Published articles | **15–20 minimum** |
| Unique content | All AI-generated + affiliate disclosures |
| Active site age | **2–4 weeks** after first content |
| Custom domain | Must be on your own domain (not github.io) |
| Essential pages | Privacy Policy, About, Contact, Disclaimer |
| SSL certificate | HTTPS enabled (free via Cloudflare) |

### Step 1: Create Essential Pages

Before applying, create these pages on your site:

1.  **Privacy Policy** — Use [privacypolicygenerator.info](https://www.privacypolicygenerator.info/)
2.  **About** — Who you are, what the site is about
3.  **Contact** — Simple contact form or email address
4.  **Disclaimer/Disclosure** — Already built into your post template (FTC disclosure)

### Step 2: Apply for AdSense

1.  Go to [Google AdSense](https://www.google.com/adsense/)
2.  Click **Get Started**
3.  Enter your site URL: `https://tech-life-insights.com`
4.  Fill in your personal/business information
5.  Google will give you a **verification code** (HTML snippet)
6.  Add it to your `site/templates/index.html` `<head>` section
7.  Wait 1–14 days for review

### Step 3: Replace Ad Placeholders

Once approved, replace the `<!-- Google AdSense -->` comment blocks in your templates with actual ad unit code:

In `site/templates/post.html`, replace:

```html
<div class="ad-slot">
  <span>Advertisement</span>
</div>
```

With your actual AdSense code:

```html
<div class="ad-slot">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-YOUR_ID"
    crossorigin="anonymous"></script>
  <ins class="adsbygoogle"
    style="display:block"
    data-ad-client="ca-pub-YOUR_ID"
    data-ad-slot="YOUR_SLOT_ID"
    data-ad-format="auto"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
```

### Common Rejection Reasons & Fixes

| Reason | Fix |
|---|---|
| "Insufficient content" | Publish more articles (aim for 20+) |
| "Valuable inventory" | Make content longer, more detailed |
| "Navigational issues" | Add proper nav links, sitemap |
| "Under construction" | Remove placeholder text, fill all pages |

---

## 13. Going Live Checklist

### Development Setup
- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` successful
- [ ] Ollama installed and mistral model downloaded
- [ ] `.env` file created with your secrets
- [ ] `config/niches.yaml` — affiliate IDs replaced
- [ ] `config/settings.yaml` — timezone set correctly

### Bot Verification
- [ ] Dashboard runs at `localhost:5002`
- [ ] Bot can generate a test article (`python scripts/test_run.py`)
- [ ] Rebuild site generates all pages (`PYTHONPATH=. python scripts/rebuild_site.py`)
- [ ] Homepage shows all 5 niche category cards
- [ ] Each niche has its own index page (`/ai_tools/`, `/personal_finance/`, etc.)

### Domain & Hosting
- [ ] Domain purchased (`tech-life-insights.com`)
- [ ] Hosting set up (Cloudflare Pages)
- [ ] DNS configured, HTTPS working

### Platforms (Optional)
- [ ] YouTube API credentials (if using Shorts)
- [ ] Pinterest API credentials (if using pins)

### Content & Monetization
- [ ] Privacy Policy / About / Contact pages created
- [ ] 15+ articles published
- [ ] AdSense applied (after 2-4 weeks of content)
- [ ] Ad unit codes inserted into templates

---

## 14. Troubleshooting

### "Ollama connection refused"

```bash
# Start Ollama if not running
ollama serve

# Check it's running
curl http://localhost:11434/api/tags
```

### "ModuleNotFoundError"

```bash
# Make sure venv is activated
source contentgenerator/bin/activate
pip install -r requirements.txt
```

### "ffmpeg not found" (video generation)

```bash
brew install ffmpeg      # macOS
sudo apt install ffmpeg  # Ubuntu
```

### "YouTube upload fails"

-   Delete `token.json` and re-authenticate
-   Check your API quota at [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)

### "Dashboard won't start"

```bash
# Check if port 5002 is in use
lsof -i :5002

# Kill the process or use a different port
DASHBOARD_PORT=5003 python scripts/start_dashboard.py
```

### "Bot not generating content"

1.  Check Logs page in the dashboard
2.  Verify Ollama is running: `curl http://localhost:11434/api/tags`
3.  Run a manual test: `python scripts/test_run.py`
4.  Check `data/logs/` for error files

---

## 15. Site Architecture & Templates

### How Pages Are Generated

The bot uses **3 Jinja2 templates** in `site/templates/` to generate all HTML pages into `site/output/`:

| Template | Generates | URL Pattern |
|---|---|---|
| `index.html` | Homepage with niche cards + all posts | `tech-life-insights.com/` |
| `niche_index.html` | Per-niche category page with articles list | `tech-life-insights.com/ai_tools/` |
| `post.html` | Individual article page | `tech-life-insights.com/ai_tools/best-ai-tools-2026.html` |

### Generated Output Structure

```
site/output/
├── index.html                          ← Homepage
├── ai_tools/
│   ├── index.html                      ← AI Tools category page
│   └── best-ai-tools-productivity.html ← Article
├── personal_finance/
│   ├── index.html                      ← Finance category page
│   └── ...articles...
├── health_biohacking/
│   ├── index.html                      ← Health category page
│   └── ...articles...
├── home_tech/
│   ├── index.html                      ← Home Tech category page
│   └── ...articles...
└── travel/
    ├── index.html                      ← Travel category page
    └── ...articles...
```

### Automatic Rebuilds

Every time the bot publishes an article, `core/publisher.py` automatically:

1. Renders the article → `site/output/{niche}/{slug}.html`
2. Rebuilds the homepage → `site/output/index.html`
3. Rebuilds all 5 niche index pages → `site/output/{niche}/index.html`

### Manual Rebuild

To regenerate all pages at any time:

```bash
source contentgenerator/bin/activate
PYTHONPATH=. python scripts/rebuild_site.py
```

### Adding Amazon Affiliate Products

1. Get your Amazon Associate tag (e.g., `yourtag-20`) from [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
2. Open `config/niches.yaml`
3. Replace `YOUR_TAG` with your actual tag in the Amazon entries:

```yaml
affiliate_programs:
  - name: "Amazon Health"
    url: "https://amazon.com?tag=yourtag-20"
    keywords: ["supplement", "vitamins", "protein powder"]
```

4. The bot's `affiliate_injector.py` automatically scans every article for matching keywords and wraps them with your affiliate link
5. You can add specific product URLs too:

```yaml
  - name: "Roomba j7+"
    url: "https://amazon.com/dp/B094NYHTMF?tag=yourtag-20"
    keywords: ["Roomba", "robot vacuum", "Roomba j7"]
```

### Adding a New Niche

1. Open `config/niches.yaml`
2. Add a new entry at the bottom:

```yaml
  new_niche_id:
    name: "Display Name"
    enabled: true
    seed_keywords:
      - "keyword 1"
      - "keyword 2"
    affiliate_programs:
      - name: "Program Name"
        url: "https://example.com?aff=YOUR_ID"
        keywords: ["keyword1", "keyword2"]
    post_schedule_hour: 10
    post_schedule_minute: 15
    video_schedule_hour: 13
    video_schedule_minute: 0
    pinterest_schedule_hour: 15
    pinterest_schedule_minute: 0
```

3. Restart the bot — it automatically picks up the new niche
4. Run `PYTHONPATH=. python scripts/rebuild_site.py` to generate the new niche's index page
5. Push to GitHub — Cloudflare deploys the new page automatically

---

## AI Image API Setup (Stock Images + Video Backgrounds)

The bot generates AI images using a **cascading multi-API system** — it tries the best API first, then falls back to the next if it runs out of tokens. All APIs are **free with no credit card required**.

### API Priority Order

| Priority | API | Free Tier | Quality | Setup |
|---|---|---|---|---|
| 1st | **Leonardo AI** | 150 tokens/day (~20-37 images) | ⭐⭐⭐⭐⭐ Highest | app.leonardo.ai |
| 2nd | **Stability AI** | 25 credits on signup (~7 images) | ⭐⭐⭐⭐ Great | platform.stability.ai |
| 3rd | **HuggingFace** | ~30 images/day, always free | ⭐⭐⭐ Good | huggingface.co |

### Leonardo AI Setup (Best Quality — Recommended)

1. Go to **https://app.leonardo.ai** and sign up (free, no CC)
2. Go to **https://app.leonardo.ai/api** → Click "Create API key"
3. Copy the API key
4. Add to `config/settings.yaml`:

```yaml
stock_images:
  leonardo_api_key: "your-leonardo-key-here"
```

### Stability AI Setup

1. Go to **https://platform.stability.ai** and sign up (free, no CC)
2. Go to **Account → API Keys → Create key**
3. Copy the API key
4. Add to `config/settings.yaml`:

```yaml
stock_images:
  stability_api_key: "sk-your-stability-key-here"
```

### HuggingFace Setup (Free Fallback — Always Works)

1. Go to **https://huggingface.co/settings/tokens**
2. Sign up or log in (free account)
3. Click **"New token"**
4. Name: `content-generator-bot`, Type: **Read**
5. Click **"Generate"** and copy the token (starts with `hf_...`)
6. Add to `config/settings.yaml`:

```yaml
stock_images:
  huggingface_token: "hf_YOUR_TOKEN_HERE"
```

### How It Works

The bot tries Leonardo first (highest quality). If Leonardo runs out of tokens, it falls back to Stability AI. If both are exhausted, HuggingFace handles it. You can configure one, two, or all three — the bot skips any API with a blank key.

### Test It

```bash
source contentgenerator/bin/activate
PYTHONPATH=. python -c "
from core.stock_generator import generate_stock_images
import yaml
with open('config/settings.yaml') as f:
    settings = yaml.safe_load(f)
topics = [{'topic': 'modern workspace', 'niche_id': 'ai_tools'}]
results = generate_stock_images(topics, settings, count=1)
print('✅ Success!' if results else '❌ Check your API keys')
"
```

---

## Bot Modes

The dashboard has **three operating modes**:

| Mode | Behavior |
|---|---|
| ⏸️ **Paused** | Bot is active but does nothing. No scheduled jobs run. Use this to stop all automated work while keeping the bot alive. |
| 📅 **Scheduled** | Normal operation — follows the cron schedule (trends → articles → videos → tweets → pins). |
| 🔧 **Manual** | Only runs tasks when YOU click the trigger. Runs all tasks in dependency order: Trends → Articles → Stock Images → Videos → Twitter → Pinterest. |

Switch modes from the Overview page in the dashboard.

---

## Quick Start (TL;DR)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral

# 2. Set up the project
cd content-generator-bot
python3 -m venv contentgenerator && source contentgenerator/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit with your secrets

# 3. Run it
python scripts/start_dashboard.py
# Open http://localhost:5002 → Click "Start"
```

That's it. The system handles the rest. ✅

---

## Stock Photography Platform Setup

The bot generates AI images and prepares them for stock platform submissions. **No platform offers an upload API** — you must upload via each platform's web portal. The bot generates optimized metadata for each platform.

### Step 1: Register on Stock Platforms (All Free)

| Platform | Apply Here | Commission | Notes |
|---|---|---|---|
| **Wirestock** (recommended first) | [contributor.wirestock.io](https://contributor.wirestock.io) | Varies | Distributes to 6+ platforms at once |
| **Adobe Stock** | [contributor.stock.adobe.com](https://contributor.stock.adobe.com) | 33% | Requires Adobe ID |
| **Shutterstock** | [submit.shutterstock.com](https://submit.shutterstock.com) | 15–40% | Largest marketplace |
| **Freepik** | [contributor.freepik.com](https://contributor.freepik.com) | Up to 50% | Growing fast |
| **Dreamstime** | [dreamstime.com/sell](https://www.dreamstime.com/sell) | 25–60% | Easy approval |
| **Pond5** | [pond5.com/sell](https://www.pond5.com/sell) | 50–60% | Best for video + images |
| **Depositphotos** | [depositphotos.com/sell](https://depositphotos.com/sell) | 34–42% | Solid marketplace |
| **123RF** | [123rf.com/contributors](https://www.123rf.com/contributors) | 30–60% | Easy onboarding |

### Step 2: Generate & Export Images

1. Open dashboard → **🖼️ Stock Images**
2. Click **🎨 Generate Stock Images** to create a batch
3. Click **📦 Export for Stock Platforms** to prepare metadata
4. Check `data/stock_exports/<platform>/` for files + metadata JSON

### Step 3: Upload to Platforms

1. Go to each platform's contributor portal
2. Upload the images from `data/stock_exports/<platform>/`
3. Copy title, description, and keywords from the JSON metadata file
4. Mark as submitted in the dashboard

### Step 4: Track Sales

1. When a sale happens on a platform, go to **💰 Income** page
2. Add the income entry with source = "stock_photos"
3. Or use the stock image dashboard to record individual sales

### Platforms That BAN AI Content (Do NOT Upload)

- ❌ **Alamy** — Bans all AI content
- ❌ **iStock / Getty Images** — Bans AI content
- ❌ **Stocksy** — Bans AI content

---

## Income Tracking Setup

The bot tracks **real income only** — no estimates or fake numbers.

### Supported Revenue Sources

1. **Google AdSense** — Manual entry from AdSense dashboard
2. **Amazon Associates** — Manual entry from Associates reports
3. **Stock Photos** — Auto-synced from recorded sales
4. **YouTube** — Manual entry from YouTube Studio (requires monetization)
5. **Other Affiliates** — Manual entry (CJ, ShareASale, etc.)

### How to Use

1. Go to **💰 Income** in the dashboard sidebar
2. Select revenue source, enter amount, pick niche and period
3. Click "Add Income"
4. Track your real earnings over time

---

## Video Intelligence — Short-Form vs Landscape

The trend intelligence now automatically selects the right video format based on content type:

- **Short-Form (9:16)** — 7 formats for Shorts/Reels/TikTok (≤60 seconds)
- **Landscape (16:9)** — 6 formats for YouTube long-form (5–20 minutes)

View all formats on the **🧠 Intelligence** dashboard page.