# 📋 OPERATIONS MANUAL — AI Content Generator Bot

> Complete guide to running, maintaining, and monetizing your automated content bot.
> Last Updated: March 2026

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Revenue Streams](#2-revenue-streams)
3. [Complete Cost Breakdown](#3-complete-cost-breakdown)
4. [The Domain Question](#4-the-domain-question)
5. [AdSense Setup](#5-adsense-setup)
6. [Amazon Associates Setup](#6-amazon-associates-setup)
7. [ShareASale Setup](#7-shareasale-setup)
8. [CJ Affiliate Setup](#8-cj-affiliate-setup)
9. [YouTube API Setup](#9-youtube-api-setup)
10. [Pinterest API Setup](#10-pinterest-api-setup)
11. [Installing Ollama](#11-installing-ollama)
12. [First-Time Setup](#12-first-time-setup)
13. [Daily Startup Procedure](#13-daily-startup-procedure)
14. [Daily Shutdown Procedure](#14-daily-shutdown-procedure)
15. [Dashboard Guide](#15-dashboard-guide)
16. [Understanding Income](#16-understanding-income)
17. [What the Bot Does Every Day](#17-what-the-bot-does-every-day)
18. [Niche Configuration Guide](#18-niche-configuration-guide)
19. [Affiliate Link Management](#19-affiliate-link-management)
20. [Hosting Your Site Free](#20-hosting-your-site-free)
21. [Realistic Income Expectations](#21-realistic-income-expectations)
22. [Troubleshooting](#22-troubleshooting)
23. [Maintenance](#23-maintenance)
24. [FAQ](#24-faq)
25. [Legal & Compliance](#25-legal--compliance)

---

## 1. System Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      YOUR COMPUTER                              │
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Ollama    │    │  APScheduler  │    │  Flask Dashboard │  │
│  │  (Mistral)  │◄───│  (core/      │    │  (dashboard/     │  │
│  │  :11434     │    │  scheduler.py)│    │   app.py) :5000  │  │
│  └─────────────┘    └──────┬───────┘    └────────┬─────────┘  │
│                             │                     │            │
│            ┌────────────────┼─────────────────────┘            │
│            ▼                ▼                                   │
│  ┌─────────────────────────────────────────────┐               │
│  │              PIPELINE (per niche)            │               │
│  │                                             │               │
│  │  trend_finder → llm_writer → affiliate_    │               │
│  │  injector → seo_optimizer → publisher      │               │
│  │       ↓              ↓                      │               │
│  │  video_generator  pinterest_poster          │               │
│  │       ↓                                     │               │
│  │  youtube_uploader                           │               │
│  └─────────────────────────────────────────────┘               │
│            │                │                                   │
│            ▼                ▼                                   │
│  ┌──────────────┐   ┌──────────────┐                          │
│  │  SQLite DB   │   │  site/output/│                          │
│  │  data/bot.db │   │  (HTML files)│                          │
│  └──────────────┘   └──────┬───────┘                          │
│                             │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │ deploy
                              ▼
              ┌───────────────────────────────┐
              │  FREE HOSTING                  │
              │  GitHub Pages / Netlify /      │
              │  Cloudflare Pages              │
              │  yourdomain.com                │
              └───────────────────────────────┘
                              │
              ┌───────────────┼───────────────────────┐
              ▼               ▼                        ▼
        ┌──────────┐  ┌──────────────┐        ┌────────────┐
        │  Google  │  │   YouTube    │        │  Pinterest │
        │  AdSense │  │  (auto-upload│        │  (auto-pin)│
        │  (ads)   │  │   videos)    │        │  (traffic) │
        └──────────┘  └──────────────┘        └────────────┘
```

### Key Components

| File | Purpose |
|---|---|
| `core/llm_writer.py` | Calls Ollama (Mistral) to write 1000–1400 word SEO articles |
| `core/trend_finder.py` | Uses Google Trends (pytrends) to find viral topics |
| `core/affiliate_injector.py` | Injects Amazon/ShareASale/CJ links + FTC disclosure |
| `core/seo_optimizer.py` | Generates meta tags, JSON-LD schema, sitemap.xml |
| `core/publisher.py` | Renders Jinja2 templates → static HTML files |
| `core/video_generator.py` | Builds 1280×720 MP4 with Pillow slides + gTTS narration |
| `core/youtube_uploader.py` | Uploads video to YouTube via OAuth2 |
| `core/pinterest_poster.py` | Creates Pinterest pins via API v5 |
| `core/scheduler.py` | APScheduler: orchestrates all jobs on a daily cron schedule |
| `core/analytics_tracker.py` | SQLite CRUD for posts, logs, clicks, income snapshots |
| `dashboard/app.py` | Flask web app: live dashboard at localhost:5000 |

---

## 2. Revenue Streams

### Stream 1: Google AdSense
- **How it works**: Google auto-places ads on every page of your site. You earn money every time a visitor sees or clicks an ad.
- **Payout**: $1–$10 CPM (cost per 1,000 views). Clicks pay more.
- **Setup time**: 1–2 weeks for AdSense approval.
- **Payment threshold**: $100 USD. Monthly payouts via bank transfer or check.

### Stream 2: Amazon Associates
- **How it works**: The bot automatically finds product keywords in every article and wraps them with your Amazon affiliate link. When a visitor clicks and buys anything on Amazon within 24 hours, you earn a commission.
- **Commission rate**: 1–10% depending on product category.
- **Payment threshold**: $10 (gift card), $100 (direct deposit).
- **Cookie window**: 24 hours.

### Stream 3: ShareASale
- **How it works**: ShareASale is a network of thousands of merchants. You join individual programs, get affiliate links, paste them into `config/niches.yaml`, and the bot auto-injects them.
- **Commission rate**: 5–50% (often much higher than Amazon).
- **Payment threshold**: $50.
- **Cookie window**: Varies by merchant (30–90 days is common).

### Stream 4: CJ Affiliate (Commission Junction)
- **How it works**: Same as ShareASale but different merchants. Many major brands (Expedia, Overstock, Barnes & Noble) use CJ. Join programs, get links, add to `niches.yaml`.
- **Commission rate**: 3–15% for most programs.
- **Payment threshold**: $50.
- **Cookie window**: Varies (often 30 days).

### Stream 5: YouTube
- **How it works**: The bot converts every article into a narrated video (slide show with TTS audio). It uploads these to your YouTube channel automatically. Once you hit 1,000 subscribers and 4,000 watch hours, you can monetize with YouTube ads.
- **Payout**: $1–$5 RPM (per 1,000 views) once monetized.
- **Timeline**: 6–18 months to reach monetization threshold.
- **Note**: Videos also drive traffic back to your site.

### Stream 6: Pinterest
- **How it works**: The bot creates a visually rich pin (1000×1500 image) for every article and posts it to your Pinterest board. Pinterest has very long content lifespans — pins get traffic for months or years.
- **Revenue**: Pinterest doesn't pay you directly. It drives traffic to your site, which increases AdSense revenue and affiliate clicks.
- **Effect**: Can 2–5× your monthly traffic over time.

---

## 3. Complete Cost Breakdown

| Item | Monthly Cost | Annual Cost | Notes |
|---|---|---|---|
| Domain name | $0.75 | ~$9 | Namecheap, Cloudflare, or Google Domains |
| Web hosting | $0 | $0 | GitHub Pages / Netlify / Cloudflare Pages (all free) |
| Ollama (AI) | $0 | $0 | Runs on your computer; no cloud AI costs |
| Mistral model | $0 | $0 | Downloaded once (~4 GB), runs locally |
| Google Trends | $0 | $0 | No API key; pytrends is free |
| AdSense | $0 | $0 | Google pays you |
| Amazon Associates | $0 | $0 | Amazon pays you |
| ShareASale | $0 | $0 | Free to join; merchants pay you |
| CJ Affiliate | $0 | $0 | Free to join; brands pay you |
| YouTube API | $0 | $0 | 10,000 free quota units/day |
| Pinterest API | $0 | $0 | Free developer account |
| Flask + Python | $0 | $0 | Open source |
| SQLite | $0 | $0 | Built into Python |
| Electricity | ~$2–5 | ~$24–60 | Running a computer 24/7 |
| **TOTAL** | **~$2–6/mo** | **~$33–69/yr** | |

> Most people already have a computer running. If you run the bot only during the day (8 AM–2 PM), electricity cost is negligible.

---

## 4. The Domain Question

### Do I need a separate domain for each niche?

**No. You need exactly ONE domain.**

Here's how it works:

```
yourdomain.com/               ← Homepage (index.html)
yourdomain.com/ai_tools/      ← AI Tools articles
yourdomain.com/personal_finance/ ← Finance articles
yourdomain.com/health_biohacking/ ← Health articles
yourdomain.com/home_tech/     ← Home Tech articles
yourdomain.com/travel/        ← Travel articles
```

### For AdSense
When you add your domain to AdSense, **the entire domain is approved** — including all subpaths. You do not need separate AdSense accounts or applications for each niche/path.

### For YouTube
One YouTube channel covers all niches. The bot uploads videos for all niches to the same channel with appropriate titles and descriptions.

### For Pinterest
One Pinterest board (or multiple boards) can cover all niches. You can organize by board name (e.g., "AI Tools Tips", "Travel Hacks").

### Recommended Domain Registration
- [Namecheap](https://namecheap.com) — ~$9/year for `.com`
- [Cloudflare Registrar](https://cloudflare.com/products/registrar/) — at-cost pricing, often cheapest

---

## 5. AdSense Setup

### Step-by-Step

1. **Deploy your site first** (see Section 20). AdSense requires a live, indexed site.
2. Go to [google.com/adsense](https://www.google.com/adsense/start/) and sign in with Google.
3. Click **Get started** and enter your site URL.
4. Copy the provided AdSense code snippet.
5. Open `site/templates/post.html` and `site/templates/index.html`.
6. Paste the snippet inside `<head>` before `</head>`.
7. Redeploy your site.
8. In AdSense, click **I've placed the code** and submit for review.

### Approval Requirements
- Site must have **original content** (the bot generates unique articles)
- Must have a **Privacy Policy** page (add `/privacy.html` to your site)
- Must be **accessible** (no login required)
- Must comply with [AdSense Program Policies](https://support.google.com/adsense/answer/48182)

### Realistic Timeline
- Week 1: Submit application
- Week 1–2: Google crawls and reviews
- Week 2–4: Approval email (or rejection with reasons)
- After approval: Ads appear within 24 hours

### After Approval: Use Auto Ads
Enable **Auto Ads** in AdSense — Google automatically places and optimizes ad placement across all your pages without any additional code.

---

## 6. Amazon Associates Setup

1. Go to [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
2. Sign in with your Amazon account
3. Fill out your account information (website URL = your domain)
4. Your **Associate tag** is shown in the format `yourtag-20`
5. Open `.env` and set: `AMAZON_AFFILIATE_TAG=yourtag-20`
6. Update Amazon-related entries in `config/niches.yaml` — change `YOUR_TAG` to your tag

### Important Notes
- You must make **3 qualifying sales within 180 days** of approval, or your account is closed
- Use real product links in `niches.yaml` (e.g., `https://amazon.com/dp/B08N5WRWNW?tag=yourtag-20`)
- Payment: Monthly via direct deposit or gift card. Threshold: $10 (gift card) or $100 (bank)

---

## 7. ShareASale Setup

1. Go to [shareasale.com/info/join.cfm](https://www.shareasale.com/info/join.cfm)
2. Complete the publisher application (your website = your domain)
3. Wait for approval (usually 24–48 hours)
4. Browse merchants in the ShareASale marketplace
5. Apply to individual merchant programs
6. Once approved by a merchant, get their affiliate link
7. Add the link to the relevant niche in `config/niches.yaml`
8. Set `SHAREASALE_AFFILIATE_ID=your_id` in `.env`

### Recommended ShareASale Programs by Niche
- **AI Tools**: Jasper AI, Semrush, Writesonic
- **Finance**: Quicken, Credit Karma, TurboTax
- **Health**: Thrive Market, iHerb, Bulletproof
- **Home Tech**: Vivint, Ring (via Amazon), Nest (via Google)
- **Travel**: TripAdvisor, Booking.com (has ShareASale program)

---

## 8. CJ Affiliate Setup

1. Go to [signup.cj.com](https://signup.cj.com/member/signup/publisher/)
2. Create a publisher account
3. Add your website
4. Search for advertiser programs and apply
5. Once approved, get your tracking links
6. Add links to `config/niches.yaml`
7. Set `CJ_AFFILIATE_ID=your_id` in `.env`

### Recommended CJ Programs by Niche
- **Travel**: Expedia, Hotels.com, Priceline, Enterprise
- **Finance**: Credit cards, insurance companies
- **Home Tech**: Best Buy, Home Depot, Lowe's
- **Health**: GNC, Vitamin Shoppe, Bodybuilding.com

---

## 9. YouTube API Setup

### Step 1: Google Cloud Console

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project: click dropdown → **New Project** → name it "ContentBot"
3. Select your project

### Step 2: Enable YouTube Data API

1. Go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click **Enable**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen first:
   - User Type: External
   - App name: ContentBot
   - Add your email as test user
4. Application type: **Desktop app**
5. Name: "ContentBot"
6. Click **Create**
7. Download the JSON file
8. Save it as `client_secrets.json` in the project root

### Step 4: Configure .env

```bash
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_CHANNEL_NAME=Your Channel Name
```

### Step 5: First Authorization

The first time the bot tries to upload a video, a browser window will open for you to authorize. This only happens once — the token is saved to `data/youtube_token.json`.

### Quota Limits

| Action | Quota Cost |
|---|---|
| Upload a video | ~1,600 units |
| Daily free quota | 10,000 units |
| Max uploads/day | ~6 videos |

> The bot handles quota gracefully: if quota is exceeded, it logs a warning and skips the upload without crashing.

---

## 10. Pinterest API Setup

### Step 1: Create a Business Account

1. Go to [business.pinterest.com](https://business.pinterest.com)
2. Create or convert your account to Business

### Step 2: Create a Developer App

1. Go to [developers.pinterest.com](https://developers.pinterest.com/apps/)
2. Click **Create app**
3. Fill in app details (name, description)
4. Request scopes: `pins:read_write`, `boards:read`, `user_accounts:read`

### Step 3: Generate Access Token

1. In your app settings, go to **Authentication**
2. Generate an access token with the required scopes
3. Copy the token

### Step 4: Get Your Board ID

1. Go to your Pinterest profile and open a board
2. The Board ID is in the URL: `pinterest.com/username/board-name/` → use the numeric ID
   or go to Board settings where the numeric ID is shown

### Step 5: Configure .env

```bash
PINTEREST_ACCESS_TOKEN=your_access_token_here
PINTEREST_BOARD_ID=1234567890123456789
```

### Notes
- Pinterest API v5 is required (the bot uses v5 endpoints)
- If not configured, the bot skips Pinterest gracefully — no errors

---

## 11. Installing Ollama

Ollama runs the Mistral AI model locally on your computer. No API keys, no monthly fees.

### Windows

1. Download the installer from [ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open a terminal and run: `ollama pull mistral`
4. Test: `ollama run mistral "Write a haiku about AI"`

### macOS

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
# Test:
ollama run mistral "Write a haiku about AI"
```

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
# Start service (if not auto-started):
ollama serve &
# Test:
ollama run mistral "Write a haiku about AI"
```

### Hardware Requirements

| RAM | What works |
|---|---|
| 8 GB | Mistral 7B (default) — recommended |
| 16 GB | Mistral 7B + better performance |
| 32 GB+ | Can run larger models |

> The bot defaults to `mistral` (Mistral 7B). You can change this in `.env` with `OLLAMA_MODEL=llama3` or any other Ollama model.

---

## 12. First-Time Setup

### Windows

```powershell
# Open PowerShell as Administrator
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
python scripts/setup.py
copy .env.example .env
notepad .env
# Edit your settings, then:
python scripts/test_run.py
```

### macOS

```bash
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
python3 scripts/setup.py
cp .env.example .env
nano .env   # or: open -e .env
python3 scripts/test_run.py
```

### Linux

```bash
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
python3 scripts/setup.py
cp .env.example .env
nano .env
python3 scripts/test_run.py
```

### What `setup.py` Does

1. Checks Python 3.10+
2. Creates a virtual environment (`venv/`)
3. Installs all packages from `requirements.txt`
4. Copies `.env.example` → `.env` (if `.env` doesn't exist)
5. Creates necessary directories (`data/`, `site/output/`)
6. Initializes the SQLite database
7. Downloads Chart.js from CDN
8. Checks if Ollama is running

---

## 13. Daily Startup Procedure

### Automated (Recommended)

```bash
# Start the full bot (scheduler + dashboard)
python scripts/start_bot.py
# or
make run
```

The bot will:
1. Start the Flask dashboard at `http://localhost:5000`
2. Start APScheduler with all cron jobs
3. Run an immediate bootstrap cycle if no posts exist yet

### Manual Step-by-Step

```bash
# Step 1: Make sure Ollama is running
ollama serve   # or it may start automatically on Windows/macOS

# Step 2: Start the bot
python scripts/start_bot.py
```

### Check Everything is Working

1. Open `http://localhost:5000` — dashboard should load
2. Check the **Logs** page — you should see "Scheduler started" message
3. Check **Posts** page — articles will appear after 9 AM

---

## 14. Daily Shutdown Procedure

### Safe Shutdown

Press **Ctrl+C** in the terminal where `start_bot.py` is running.

The scheduler will finish any in-progress job before stopping. This is safe — no data will be lost.

### If the Bot is Frozen

```bash
# Find the process ID
# Windows:
tasklist | findstr python
taskkill /PID <pid> /F

# macOS/Linux:
ps aux | grep python
kill <pid>
```

### Before Shutting Down
1. Check **Logs** page for any ERROR messages
2. Check **Posts** page — confirm today's articles were published
3. Deploy any new articles to your hosting (if not auto-deployed)

---

## 15. Dashboard Guide

Open **http://localhost:5000** in your browser.

### Overview Page (`/`)

Shows:
- **Total Posts** — all published articles
- **Estimated Clicks** — based on word count × estimated CTR
- **Estimated Income** — clicks × average commission value
- **Active Niches** — number of enabled niches
- **Posts over Time** chart (last 30 days)
- **Income over Time** chart (last 30 days)
- **Recent Activity** — last 20 bot actions

### Posts Page (`/posts`)

- Searchable table of all published articles
- Shows: title, niche, word count, affiliate links count, published date
- Click any post title to visit the live article

### Analytics Page (`/analytics`)

- Bar chart: posts per niche
- Bar chart: estimated income per niche
- Summary statistics

### Logs Page (`/logs`)

- Color-coded log viewer (green = SUCCESS, red = ERROR, yellow = WARNING, blue = INFO)
- Auto-refreshes every 5 seconds
- Shows the last 200 log entries

### Niches Page (`/niches`)

- Cards for each configured niche
- Shows: name, status (enabled/disabled), number of posts, seed keywords, affiliate programs

### API Endpoints

| Endpoint | Returns |
|---|---|
| `/api/stats` | JSON stats summary |
| `/api/logs` | JSON recent logs |
| `/api/posts` | JSON all posts |
| `/api/income-chart` | JSON income chart data |
| `/api/posts-chart` | JSON posts chart data |
| `/track?url=URL&post=SLUG&niche=NICHE` | Records click, redirects to URL |

---

## 16. Understanding Income

### How Each Stream Pays

**AdSense**
- Earnings accumulate daily in your AdSense account
- Paid monthly on the 21st of the following month
- Minimum threshold: $100
- Payment methods: bank transfer, check, wire transfer

**Amazon Associates**
- Earnings available in your Associates account ~60 days after the order ships
- Paid monthly via direct deposit ($10 threshold) or gift card ($10 threshold)
- Reports available in Associates Central

**ShareASale**
- Paid on the 20th of each month for previous month's commissions
- Minimum threshold: $50
- Payment: direct deposit, check, Payoneer

**CJ Affiliate**
- Paid on the 20th of each month
- Minimum threshold: $50 (direct deposit) or $100 (check)

**YouTube**
- AdSense for YouTube — same $100 threshold, monthly payment
- Must first reach 1,000 subscribers + 4,000 watch hours (YouTube Partner Program)

### Income Formula (Dashboard Estimate)

```
Estimated Income = Total Posts × Avg Words × ESTIMATED_CTR × AVG_COMMISSION_VALUE
```

These are rough estimates. Actual income depends on:
- Real traffic (SEO takes 3–6 months to build)
- Actual click-through rates (vary by niche and content quality)
- Actual conversion rates (vary by product and audience)

---

## 17. What the Bot Does Every Day

| Time | Job | Details |
|---|---|---|
| 8:00 AM | Fetch Trends | Queries Google Trends for rising topics in all 5 niches. Saves to `data/trends_cache.json`. Deduplicates against already-published topics. |
| 9:00 AM | Post: AI Tools | Selects topic → Ollama generates article → affiliates injected → SEO optimized → HTML published to `site/output/ai_tools/` → saved to database |
| 9:15 AM | Post: Personal Finance | Same pipeline for Finance niche |
| 9:30 AM | Post: Health | Same pipeline for Health niche |
| 9:45 AM | Post: Home Tech | Same pipeline for Home Tech niche |
| 9:50 AM | Post: Travel | Same pipeline for Travel niche |
| 11:00 AM | Video: AI Tools | Loads latest AI Tools post → extracts key points → gTTS audio → Pillow slides → MoviePy MP4 → uploads to YouTube |
| 11:15 AM | Video: Finance | Same for Finance |
| 11:30 AM | Video: Health | Same for Health |
| 11:45 AM | Video: Home Tech | Same for Home Tech |
| 11:50 AM | Video: Travel | Same for Travel |
| 12:00 PM | Pinterest: AI Tools | Generates 1000×1500 pin image → uploads to Pinterest API v5 → links back to article |
| 12:15 PM | Pinterest: Finance | Same for Finance |
| 12:30 PM | Pinterest: Health | Same for Health |
| 12:45 PM | Pinterest: Home Tech | Same for Home Tech |
| 12:50 PM | Pinterest: Travel | Same for Travel |
| Every hour | Income Snapshot | Calculates estimated income from click data, saves to `income_snapshots` table |
| Sunday 12:00 AM | Rebuild Site | Rebuilds `site/output/index.html` with all published posts |

---

## 18. Niche Configuration Guide

### File: `config/niches.yaml`

Each niche follows this structure:

```yaml
niches:
  your_niche_id:            # Used in URL paths (no spaces)
    name: "Display Name"    # Shown in dashboard and articles
    enabled: true           # Set false to pause this niche
    seed_keywords:          # Topics for Google Trends + fallback
      - "topic 1"
      - "topic 2"
    affiliate_programs:
      - name: "Program Name"
        url: "https://example.com?aff=YOUR_ID"  # Your affiliate URL
        keywords: ["keyword1", "keyword2"]       # Words to link in articles
    post_schedule_hour: 9
    post_schedule_minute: 0
    video_schedule_hour: 11
    video_schedule_minute: 0
    pinterest_schedule_hour: 12
    pinterest_schedule_minute: 0
```

### Adding a New Niche

1. Add a new entry in `config/niches.yaml`
2. Use a unique `niche_id` (lowercase, underscores only)
3. Set a schedule time that doesn't conflict with existing niches
4. Restart the bot

### Disabling a Niche

```yaml
  health_biohacking:
    enabled: false   # ← Simply set this to false
```

### Changing Post Frequency

To post twice daily, you can add a second APScheduler job in `core/scheduler.py`. The current schedule runs once per day per niche.

---

## 19. Affiliate Link Management

### How Links Are Injected

The `core/affiliate_injector.py` module uses BeautifulSoup to scan each article's HTML for keyword matches. When it finds a matching keyword that isn't already linked, it wraps it with the affiliate URL.

Example:
- Keyword: `"Jasper"`
- Article text: `"Many writers use Jasper for content creation"`
- Result: `Many writers use <a href="/track?url=...&post=...&niche=..." rel="nofollow sponsored">Jasper</a> for content creation`

### Updating Affiliate Links

1. Open `config/niches.yaml`
2. Find the affiliate program you want to update
3. Change the `url` field to your new affiliate URL
4. The bot will use the new URL for all future articles

### Click Tracking

All affiliate links are wrapped through the `/track` endpoint:

```
/track?url=ENCODED_AFFILIATE_URL&post=article-slug&niche=niche_id
```

This records the click in the `clicks` table before redirecting the user to the affiliate URL.

### Adding New Affiliate Programs

```yaml
affiliate_programs:
  - name: "New Program"
    url: "https://newprogram.com?ref=YOUR_ID"
    keywords: ["keyword that appears in articles", "another keyword"]
```

---

## 20. Hosting Your Site Free

### Option 1: GitHub Pages (Recommended for Beginners)

```bash
# From project root:
cd site/output

# Initialize git in output folder (first time only)
git init

# Add remote with your GitHub username
git remote add origin https://github.com/yourusername/yourusername.github.io.git

# Stage all files
git add .

# Create initial commit
git commit -m "Deploy site"

# Push to GitHub
git push origin main

# OR use subtree push from project root:
git subtree push --prefix site/output origin gh-pages
```

Then in GitHub repo → Settings → Pages:
- Source: `gh-pages` branch
- Custom domain: `yourdomain.com`

**DNS Setup**: Point your domain's A record to `185.199.108.153` (GitHub Pages IP).

### Option 2: Netlify (Best for Automation)

```bash
npm install -g netlify-cli
netlify login
netlify deploy --prod --dir site/output --site-name yoursite
```

Or drag and drop `site/output/` at [netlify.com/drop](https://app.netlify.com/drop).

**Custom domain**: Netlify Dashboard → Domain settings → Add custom domain.

### Option 3: Cloudflare Pages

1. Sign up at [pages.cloudflare.com](https://pages.cloudflare.com)
2. **Connect to Git** → choose your repository
3. Build settings:
   - Build command: (leave empty for static sites)
   - Build output directory: `site/output`
4. Add custom domain in Cloudflare Pages settings

**Advantage**: Cloudflare Pages + Cloudflare DNS = fastest performance globally.

### Automated Deployment Script

Add this to your daily workflow to auto-deploy after posts are published:

```bash
# deploy.sh (run after start_bot.py generates content)
cd site/output
git add .
git commit -m "Auto-deploy $(date +%Y-%m-%d)"
git push origin main
```

---

## 21. Realistic Income Expectations

### Month-by-Month Breakdown

| Month | Est. Income | What's Happening |
|---|---|---|
| 1 | $0 | AdSense under review, no traffic yet, content building |
| 2 | $0–$2 | AdSense may be approved, tiny trickle of traffic |
| 3 | $0–$5 | First organic traffic from long-tail keywords |
| 4 | $5–$20 | Google starts trusting the site, more indexed pages |
| 5 | $10–$40 | Affiliate clicks begin converting, Pinterest driving traffic |
| 6 | $20–$60 | 180+ articles published, YouTube channel building |
| 7 | $30–$100 | SEO compounds, consistent daily traffic |
| 8 | $40–$150 | Strong affiliate conversions in proven niches |
| 9 | $50–$200 | Brand awareness building, returning visitors |
| 10 | $60–$250 | YouTube views growing, more affiliate commissions |
| 11 | $70–$300 | Close to YouTube monetization threshold |
| 12 | $80–$400 | Full year of content, multiple traffic sources |
| Year 2 | $300–$1,500/mo | Compounding effect, established authority |

### Why It Takes Time

1. **SEO takes 3–6 months**: Google doesn't fully trust new sites. Content needs to be indexed and compete for keywords.
2. **AdSense review takes 2–4 weeks**: And you need enough content first.
3. **YouTube threshold**: 1,000 subscribers + 4,000 watch hours typically takes 6–18 months.
4. **Pinterest compound effect**: Pins keep getting traffic for months/years.

### What Accelerates Income

- **More niches**: Adding niches = more articles = more traffic
- **Internal linking**: Articles linking to each other improve SEO
- **Email list**: Capturing emails lets you promote affiliate offers directly
- **Social sharing**: Manually sharing some articles early on helps initial indexing
- **Better keywords**: Targeting low-competition keywords ranks faster

---

## 22. Troubleshooting

### Issue 1: Ollama not running
**Symptom**: Logs show "Connection refused" or "Ollama attempt 1 failed"
**Fix**:
```bash
# Start Ollama
ollama serve

# Check it's running
curl http://localhost:11434/api/version
```

### Issue 2: pytrends rate limited
**Symptom**: "429 Too Many Requests" in logs
**Fix**: The bot automatically falls back to seed keywords. This is normal. Google rate-limits frequent requests. Wait 1–2 hours.

### Issue 3: YouTube quota exceeded
**Symptom**: "quotaExceeded" in logs
**Fix**: Wait until midnight Pacific time (when quota resets). The bot handles this gracefully and skips the upload.

### Issue 4: Pinterest "Unauthorized"
**Symptom**: "401" in Pinterest logs
**Fix**: Your access token may have expired. Generate a new token in the Pinterest Developer Portal and update `.env`.

### Issue 5: No articles being published
**Symptom**: Bot runs but no HTML files appear in `site/output/`
**Fix**:
1. Check logs for ERROR messages
2. Ensure Ollama is running: `curl http://localhost:11434/api/version`
3. Check `data/bot.db` exists
4. Try manual run: `python scripts/test_run.py`

### Issue 6: Dashboard won't load
**Symptom**: `http://localhost:5000` shows "Connection refused"
**Fix**:
```bash
# Start dashboard separately
python scripts/start_dashboard.py
# Check the port isn't in use
# Windows: netstat -ano | findstr 5000
# Linux/Mac: lsof -i :5000
```

### Issue 7: Templates not found
**Symptom**: "TemplateNotFound: post.html"
**Fix**: Ensure you're running from the project root directory. The templates are in `site/templates/` relative to project root.

### Issue 8: Database locked
**Symptom**: "database is locked" in logs
**Fix**: Only one process should write to the database. If you started the bot multiple times, stop all instances and start fresh.

### Issue 9: AdSense not approved
**Symptom**: Rejection email from Google
**Common reasons and fixes**:
- **Insufficient content**: Wait until you have 20+ articles
- **Copyrighted material**: All bot content is original — verify no plagiarism
- **Missing privacy policy**: Add a `/privacy.html` page to your site
- **Navigational issues**: Ensure your site has a working navigation menu

### Issue 10: Amazon Associates account closed
**Symptom**: "Your account has been closed" email
**Reason**: No sales in first 180 days
**Fix**: Manually promote some products on social media to get initial sales. Once active, the bot's natural traffic will maintain it.

### Issue 11: Python virtual environment issues
**Symptom**: "Module not found" errors
**Fix**:
```bash
# Activate venv manually
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 12: Video generation fails
**Symptom**: "Missing video dependency" in logs
**Fix**:
```bash
pip install moviepy gtts Pillow numpy
```

### Issue 13: Scheduler not running jobs
**Symptom**: Jobs scheduled but never execute
**Fix**: Check your system timezone. Set `BOT_TIMEZONE=America/New_York` (or your local timezone) in `.env`.

### Issue 14: Articles are too short
**Symptom**: Word count below 900 words
**Fix**: Ollama may be truncating responses. Try a different model:
```bash
ollama pull llama3
# Set in .env:
OLLAMA_MODEL=llama3
```

### Issue 15: Site index.html not updating
**Symptom**: Homepage shows old posts
**Fix**: Manually trigger a rebuild:
```bash
python -c "
from pathlib import Path
from core import analytics_tracker, publisher
from jinja2 import Environment, FileSystemLoader
import yaml

with open('config/settings.yaml') as f:
    settings = yaml.safe_load(f)
db = Path('data/bot.db')
# Rebuild will happen on next successful publish
"
# Or restart the bot — it rebuilds on Sunday automatically
# Or wait for the next publish cycle
```

---

## 23. Maintenance

### Weekly Tasks

- [ ] Check the **Logs** page for ERROR patterns
- [ ] Review published articles for quality
- [ ] Check AdSense for new ad unit suggestions
- [ ] Verify all affiliate links are still active
- [ ] Deploy new articles to hosting
- [ ] Check YouTube analytics for top-performing videos

### Monthly Tasks

- [ ] Review income reports in all affiliate dashboards
- [ ] Update affiliate URLs if programs have changed
- [ ] Check `config/niches.yaml` — adjust seed keywords based on what's trending
- [ ] Review and prune low-quality articles if any
- [ ] Update `requirements.txt` dependencies: `pip list --outdated`
- [ ] Back up `data/bot.db`
- [ ] Review Google Search Console for crawl errors

### Backing Up Your Database

```bash
cp data/bot.db data/bot_backup_$(date +%Y%m%d).db
```

### Updating Dependencies

```bash
pip install --upgrade -r requirements.txt
```

---

## 24. FAQ

**Q: Can I run this on a VPS (cloud server)?**
A: Yes. A $5–10/month VPS (DigitalOcean, Linode, Hetzner) can run the bot 24/7. You'll need to install Ollama on the server. A VPS with 8 GB RAM and 4 CPUs is recommended for smooth operation.

**Q: Can I run this on a Raspberry Pi?**
A: The Ollama/Mistral AI component requires significant CPU/RAM (8 GB minimum). Raspberry Pi 4/5 with 8 GB RAM can run Mistral, but slowly (~5–10 minutes per article). Not recommended for production.

**Q: Do I need to babysit it every day?**
A: No. The bot runs on a schedule automatically. Check in once a week to review logs and deploy new content.

**Q: What if Ollama writes bad content?**
A: The bot logs everything. Review articles in the **Posts** page. You can delete bad HTML files from `site/output/` and remove DB records with a simple SQL query.

**Q: Can I add my own articles?**
A: Yes. Write the HTML manually and save it to `site/output/{niche_id}/{slug}.html`. Add a database record via the analytics_tracker functions.

**Q: Will Google penalize AI-generated content?**
A: Google's official stance is that AI-generated content is acceptable if it provides genuine value to users. Focus on topics your bot generates content for, review quality, and add unique insights where possible.

**Q: How many articles will I have after 1 year?**
A: 5 niches × 365 days = up to 1,825 articles. In practice, expect 1,000–1,500 due to occasional outages and duplicate filtering.

**Q: Can I change the article language?**
A: Yes. Change `OLLAMA_MODEL` to a multilingual model and update the prompt in `core/llm_writer.py`. Update `content.language` in `config/settings.yaml`.

**Q: My site got deindexed by Google. What happened?**
A: Check Google Search Console for manual actions. Common causes: too many thin articles, duplicate content, or technical issues. Improve content quality and submit a reconsideration request.

**Q: Can I monetize with more than 4 affiliate networks?**
A: Yes. Add any affiliate program to `config/niches.yaml` by adding a new entry under `affiliate_programs`. The bot will inject those links automatically.

**Q: What's the best niche for quick income?**
A: Finance and health typically have the highest affiliate commissions. Travel has strong Pinterest performance. AI Tools has a very engaged audience. Personal Finance is very competitive but very profitable.

**Q: Do I need to pay taxes on this income?**
A: In most countries, yes. Consult a tax professional. Keep records of all affiliate program payments.

**Q: Can I run multiple instances for different sites?**
A: Yes. Clone the repo multiple times, use different `.env` files with different `SITE_URL` values, and run separate instances.

**Q: How do I add a second YouTube channel?**
A: Each YouTube OAuth credential connects to one channel. To use multiple channels, create multiple OAuth credential files and modify the scheduler to alternate between them.

**Q: What happens if my computer restarts?**
A: The bot stops. On Linux/macOS, create a systemd service or use `cron @reboot`. On Windows, use Task Scheduler to auto-start `start_bot.py`.

**Q: Can I share this bot with others?**
A: The code is MIT licensed — share freely. However, your `.env` file contains private API keys — never share that file.

---

## 25. Legal & Compliance

### FTC Disclosure Requirements

The bot automatically adds an FTC disclosure to every article:

> "This post may contain affiliate links. If you click through and make a purchase, we may earn a commission at no extra cost to you."

This is **required by the FTC** for any content that includes affiliate links. The disclosure is injected by `core/affiliate_injector.py` at the top of every article.

**Additional requirements**:
- The disclosure must be "clear and conspicuous" — near the top of the article
- Cannot be hidden or in hard-to-read text
- The bot's disclosure satisfies these requirements

### AdSense Policies

Key rules you must follow:
- **Don't click your own ads** — this is click fraud and will get your account banned
- **Don't ask others to click your ads** — same penalty
- **No prohibited content**: adult content, violence, illegal content
- **No deceptive content**: the bot's AI-generated content must not be misleading
- Full policy: [AdSense Program Policies](https://support.google.com/adsense/answer/48182)

### Amazon Associates Agreement

Key requirements:
- **Disclosure**: Required on every page with Amazon links (auto-handled by the bot)
- **No purchase incentives**: Don't offer rewards to click Amazon links
- **Accurate prices**: Don't display specific prices (the bot doesn't show prices, just links)
- **Prohibited uses**: Don't use Amazon links in emails (only on your website)
- Full policy: [Amazon Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)

### ShareASale & CJ Terms

Each merchant has its own terms. Generally:
- You must disclose your affiliate relationship (auto-handled)
- You cannot bid on trademarked terms in PPC advertising
- You must not make false claims about products

### GDPR / Privacy

If you have visitors from the EU:
- Add a Privacy Policy page to your site (required for AdSense)
- Disclose use of Google Analytics and AdSense cookies
- Consider a cookie consent banner

### Copyright

The bot generates original articles using AI. However:
- Do not scrape or republish others' content
- AI-generated images and text are original
- Videos use only your generated images and public-domain TTS voices

### DMCA Safe Harbor

If someone claims copyright infringement on content the bot generated, promptly remove the content and submit a DMCA counter-notice if appropriate.

---

*Last updated: 2026 — AI Content Generator Bot v1.0*
