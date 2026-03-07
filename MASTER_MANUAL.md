# 📖 AI Content Generator Bot — Complete Master Manual

> **Everything you need to know about this system — from first install to earning passive income.**
> Last Updated: March 2026

---

## � Quick Start: Setting Up the `contentgenerator` Environment

### Prerequisites
- **macOS / Linux / Windows WSL**: Any version with Python 3.10+
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB recommended for video generation)
- **Disk Space**: 20GB free (AI models require ~4GB)

### Step 1: Create and Activate Virtual Environment

**On macOS/Linux:**
```bash
# Navigate to the project directory
cd /Users/thekelvinlachica/Documents/Github/Projects/content-generator-bot2

# Create virtual environment named 'contentgenerator'
python3 -m venv contentgenerator

# Activate the environment
source contentgenerator/bin/activate
```

**On Windows (PowerShell):**
```powershell
# Navigate to project directory
cd C:\Users\YourName\Documents\Github\Projects\content-generator-bot2

# Create virtual environment
python -m venv contentgenerator

# Activate the environment
.\contentgenerator\Scripts\Activate.ps1
```

### Step 2: Install Dependencies

Once activated (you should see `(contentgenerator)` in your terminal):

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -c "import flask; import ollama; print('✅ All dependencies installed successfully')"
```

### Step 4: Download Ollama (Local AI Engine)

Ollama runs AI models locally on your computer with zero API costs.

**macOS:**
```bash
brew install ollama
ollama pull mistral
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
```

**Windows:**
Download from [ollama.com/download](https://ollama.com/download) and run the installer.

### Step 5: Configure Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit with your settings (API keys, affiliate IDs, etc.)
nano .env  # or use your preferred editor
```

### Step 6: Start the Bot

**Option A: Dashboard + Bot (Recommended)**
```bash
# Make sure (contentgenerator) is active
source contentgenerator/bin/activate
python scripts/start_bot.py
```

**Option B: Dashboard Only**
```bash
source contentgenerator/bin/activate
python scripts/start_dashboard.py
```

Access the dashboard at: **http://localhost:5002**

### Step 7: Test Run (Recommended Before Full Start)

```bash
source contentgenerator/bin/activate
python scripts/test_run.py
```

This generates one test article across all niches to verify everything works.

---

## �📋 Table of Contents

1. [What This System Does](#1-what-this-system-does)
2. [How It Makes Money](#2-how-it-makes-money)
3. [The Domain Question — Critical Read Before Anything](#3-the-domain-question)
4. [Complete Cost Breakdown](#4-complete-cost-breakdown)
5. [Income Expectations — Honest Numbers](#5-income-expectations)
6. [Revenue Streams — All 6 Explained](#6-revenue-streams)
7. [The 5 Niches](#7-the-5-niches)
8. [System Architecture](#8-system-architecture)
9. [Prerequisites](#9-prerequisites)
10. [Installation — Windows](#10-installation-windows)
11. [Installation — macOS](#11-installation-macos)
12. [Installation — Linux / VPS](#12-installation-linux--vps)
13. [Setting Up Ollama (Local AI)](#13-setting-up-ollama-local-ai)
14. [Domain Setup — ONE Domain Strategy](#14-domain-setup)
15. [Google AdSense Setup](#15-google-adsense-setup)
16. [Amazon Associates Setup](#16-amazon-associates-setup)
17. [ShareASale Setup](#17-shareasale-setup)
18. [CJ Affiliate Setup](#18-cj-affiliate-setup)
19. [YouTube API Setup](#19-youtube-api-setup)
20. [Pinterest Auto-Posting Setup](#20-pinterest-auto-posting-setup)
21. [Configuring Your Niches](#21-configuring-your-niches)
22. [Startup Manual — How to Start the Bot](#22-startup-manual)
23. [Shutdown Manual — How to Safely Stop the Bot](#23-shutdown-manual)
24. [The Dashboard — Complete Guide](#24-the-dashboard)
25. [Hosting Your Site for Free](#25-hosting-your-site-for-free)
26. [Maintaining the System](#26-maintaining-the-system)
27. [Troubleshooting](#27-troubleshooting)
28. [FAQ](#28-faq)
29. [Legal & Compliance](#29-legal--compliance)

---

## 1. What This System Does

The AI Content Generator Bot is a **fully automated passive income machine** that:

| What It Does | How |
|---|---|
| Finds trending topics daily | Google Trends API (free) |
| Writes 1,000–1,400 word SEO articles | Local AI (Ollama/Mistral — free) |
| Publishes articles to your website | Static HTML (free) |
| Injects affiliate links automatically | Amazon, ShareASale, CJ (free to join) |
| Displays ads on your site | Google AdSense (they pay you) |
| Creates video versions of articles | MoviePy + gTTS (free) |
| Uploads videos to YouTube | YouTube Data API (free) |
| Auto-posts to Pinterest | Pinterest API (free) |
| Tracks all income + analytics | Local SQLite dashboard (free) |

**You set it up once. It runs forever. You check the dashboard.**

### What the bot does every single day automatically:

```
08:00 AM  →  Fetches trending topics for all 5 niches
09:00 AM  →  Writes + publishes article for niche 1 (AI Tools)
09:15 AM  →  Writes + publishes article for niche 2 (Personal Finance)
09:30 AM  →  Writes + publishes article for niche 3 (Health & Biohacking)
09:45 AM  →  Writes + publishes article for niche 4 (Home Tech)
10:00 AM  →  Writes + publishes article for niche 5 (Travel)
11:00 AM  →  Creates + uploads YouTube video for niche 1
11:15 AM  →  Creates + uploads YouTube video for niche 2
11:30 AM  →  Creates + uploads YouTube video for niche 3
11:45 AM  →  Creates + uploads YouTube video for niche 4
12:00 PM  →  Creates + uploads YouTube video for niche 5
01:00 PM  →  Creates + posts Pinterest pin for all 5 niches
Every Hour →  Updates income/analytics snapshot in dashboard
Every Sunday → Rebuilds full site index + regenerates sitemap
```

That is **5 articles + 5 videos + 5 Pinterest pins per day**, fully automated, for $0.

---

## 2. How It Makes Money

### The Complete Money Flow

```
┌─────────────────────────────────────────────────────────┐
│                    BOT RUNS DAILY                        │
│  Trend → Write → Inject Links → Publish → Video → Pin   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              YOUR WEBSITE (Static HTML)                  │
│  Articles indexed by Google over 3-6 months              │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              VISITOR LANDS ON YOUR ARTICLE               │
└────┬──────────────┬──────────────┬───────────────┬──────┘
     │              │              │               │
     ▼              ▼              ▼               ▼
 Sees AdSense   Clicks Amazon  Clicks ShareASale  Watches
 Ad → YOU GET   Link → Buys    Link → Buys        YouTube
 $0.001-$0.01   Anything →     Product →          Video →
                YOU GET 1-10%  YOU GET 5-50%      Ad Revenue
                commission     commission
```

### Revenue Source #1: Google AdSense
- Ads automatically appear on every article
- You earn per 1,000 views (RPM): typically $3–$15
- No action needed after setup — ads show automatically
- **This is your most reliable early income**

### Revenue Source #2: Amazon Associates
- Bot embeds product links in relevant articles
- When someone clicks and buys ANYTHING on Amazon within 24 hours, you earn 1–10%
- Example: Article about "best sleep supplements" → links to melatonin → reader buys melatonin ($20) → you earn $0.60–$2.00

### Revenue Source #3: ShareASale
- Higher commissions than Amazon (5–50% per sale)
- Niche-specific products (health, tech, finance tools)
- Bot auto-injects these links into articles

### Revenue Source #4: CJ Affiliate (Commission Junction)
- Major brands: Lowe's, Overstock, GNC, etc.
- Pay-per-lead (you earn when someone just SIGNS UP for something)
- Some pay $50–$150 per lead

### Revenue Source #5: YouTube Ad Revenue
- Bot uploads 5 videos/day to your channel
- YouTube monetization requires: 1,000 subscribers + 4,000 watch hours
- Once qualified: $1–$5 per 1,000 views (RPM)
- Timeline to qualify: approximately 6–18 months

### Revenue Source #6: Pinterest Traffic
- Pinterest drives FREE traffic to your articles
- More traffic = more AdSense impressions + more affiliate clicks
- Pinterest is a traffic amplifier, not a direct income source

---

## 3. The Domain Question

### ⚠️ THIS IS THE MOST IMPORTANT THING TO UNDERSTAND

**You CANNOT get Google AdSense approved on a free `.github.io` domain.**

Google requires:
- A real custom domain (e.g., `yourblog.com`)
- Because it proves you own the site
- Because `.github.io` looks like a test/temporary site to Google

### The ONE Domain Strategy

**You only need ONE domain.** Not five. Not one per niche.

Here is how to handle 5 niches on one domain:

```
yourdomain.com/                     ← Homepage (all niches)
yourdomain.com/ai-tools/            ← AI Tools articles
yourdomain.com/personal-finance/    ← Finance articles
yourdomain.com/health/              ← Health articles
yourdomain.com/home-tech/           ← Home Tech articles
yourdomain.com/travel/              ← Travel articles
```

One AdSense account. One domain. All 5 niches. ✅

### Recommended Domain Registrars (Cheapest)

| Registrar | .com Price/Year | Notes |
|---|---|---|
| **Namecheap** | $8.98/year | Best value, free WhoisGuard privacy |
| **Porkbun** | $9.73/year | Very beginner-friendly |
| **Google Domains** | $12/year | Easy DNS, integrates with everything |
| **GoDaddy** | $12–20/year | Popular but overpriced at renewal |

**Annual cost: ~$9–$12/year = less than $1/month**

### Good Domain Name Ideas (by niche combination)

- `modernlifeguides.com`
- `techlifeinsights.com`
- `everydaysmartliving.com`
- `thedailyguides.com`
- `smartlifereviews.com`

---

## 4. Complete Cost Breakdown

### Zero-Cost Items (Free Forever)

| Item | Cost | Notes |
|---|---|---|
| Python 3.10+ | $0 | Open source |
| All Python libraries | $0 | Open source |
| Ollama (local AI engine) | $0 | Runs on your computer |
| Mistral AI model | $0 | Downloaded locally via Ollama |
| GitHub account | $0 | Free |
| GitHub repository | $0 | Free for public repos |
| GitHub Pages hosting | $0 | Free forever |
| Netlify hosting | $0 | Free tier (100GB bandwidth/mo) |
| Cloudflare Pages | $0 | Free forever, unlimited bandwidth |
| Google AdSense account | $0 | They pay you |
| Amazon Associates | $0 | They pay you |
| ShareASale account | $0 | They pay you |
| CJ Affiliate account | $0 | They pay you |
| YouTube channel | $0 | Free |
| YouTube Data API | $0 | Free quota ~6 uploads/day |
| Pinterest account | $0 | Free |
| Pinterest API | $0 | Free |
| pytrends (Google Trends) | $0 | Free unofficial API |
| SQLite database | $0 | Built into Python |
| Flask dashboard | $0 | Open source |
| MoviePy (video creation) | $0 | Open source |
| gTTS (text to speech) | $0 | Free Google TTS |

### Required Costs

| Item | Cost | Frequency | Notes |
|---|---|---|---|
| **Custom domain name** | $9–12 | Per YEAR | REQUIRED for AdSense |

**That's it. One cost. ~$1/month.**

### Optional Costs (Only If You Want 24/7 Without Your PC)

| Item | Cost | Notes |
|---|---|---|
| VPS (Virtual Private Server) | $4–6/month | Run bot 24/7 without your PC being on. Hetzner CX11 recommended. |

### Total Cost Summary

| Scenario | Monthly Cost |
|---|---|
| Run on your own PC | **~$0.75/month** (just domain) |
| Run 24/7 on VPS | **~$5.75/month** (domain + VPS) |

---

## 5. Income Expectations

### Honest Monthly Income Timeline

| Month | Est. Income | What's Happening |
|---|---|---|
| 1 | $0 | Bot is writing. Google hasn't indexed anything. AdSense not approved yet. |
| 2 | $0 | More content building up. Still too early for Google ranking. |
| 3 | $0–$5 | First articles starting to appear in search. Trickle of traffic. |
| 4 | $5–$20 | AdSense approved (if 20–30 posts published). First ad revenue. |
| 5–6 | $20–$60 | Traffic growing. First affiliate sales. YouTube views trickling in. |
| 7–9 | $60–$200 | 300+ articles. Multiple posts ranking. Compounding effect begins. |
| 10–12 | $100–$400 | 500+ articles. Several posts on Google page 1. Steady income. |
| Year 2 | $300–$1,500/mo | 1,000+ articles. Established authority in all niches. |
| Year 3+ | $500–$5,000+/mo | Fully compounded. Top positions. Possible YouTube monetization. |

### Why It Takes 3–4 Months to Start Earning

Google does not rank new websites immediately. This is called the **"Google Sandbox"** period. Your site must:
1. Exist for at least 6–8 weeks
2. Have real content (not just 1–2 posts)
3. Have other sites linking to it (the bot helps by getting Pinterest traffic)
4. Pass Google's quality review for AdSense

**This is normal. Do not panic. Keep the bot running.**

### Realistic Year 1 Math (Conservative)

```
Articles published: 5 niches × 1/day × 365 = 1,825 articles
Google indexed (30% in year 1): ~548 articles
Avg monthly visits per indexed article: 8 visits
Total monthly traffic by month 12: ~4,400 visits

AdSense RPM: $4 average
AdSense income: 4,400 / 1,000 × $4 = $17.60/mo

Affiliate click rate: 2% of visitors = 88 clicks/mo
Affiliate conversion: 2.5% = ~2 sales/mo
Avg commission: $25
Affiliate income: $50/mo

Month 12 total: ~$68/mo
```

### Realistic Year 2 Math

```
Articles published: +1,825 new = 3,650 total
Indexed: ~1,800 articles
Monthly traffic: ~25,000 visits

AdSense income: 25,000 / 1,000 × $5 = $125/mo
Affiliate income: 25,000 × 2% × 2.5% × $25 = $312/mo
YouTube (if monetized): $50–$200/mo

Year 2 monthly total: $487–$637/mo
```

---

## 6. Revenue Streams

### Stream 1: Google AdSense

**What it is:** Google places ads on your articles. You earn money every time someone views or clicks an ad.

**How much:** $3–$15 RPM (revenue per 1,000 page views)
- Finance niche: up to $20 RPM (high-value ads)
- Travel niche: $5–$12 RPM
- Health niche: $4–$10 RPM
- AI/Tech niche: $5–$15 RPM

**Setup complexity:** Medium (needs domain + AdSense approval — takes 2–4 weeks)
**Maintenance:** Zero after setup
**Do you need one domain per niche?** NO — one domain covers all niches

---

### Stream 2: Amazon Associates

**What it is:** When your article links to an Amazon product and someone clicks and buys within 24 hours, you earn 1–10% of the sale. They can buy ANYTHING — not just what you linked.

**Commission rates by category:**
| Amazon Category | Commission % |
|---|---|
| Fashion | 10% |
| Health & Beauty | 8% |
| Amazon Devices | 4% |
| Furniture, Home | 8% |
| Electronics | 3% |
| Everything else | 1–4% |

**Setup complexity:** Easy (sign up, get tag, add to .env)
**Maintenance:** Zero
**Requirement:** You must make 3 qualifying sales in your first 180 days or your account is closed. The bot helps with this by generating consistent traffic.

---

### Stream 3: ShareASale

**What it is:** An affiliate network with 4,000+ merchants. Higher commissions than Amazon. Great for health, finance, and tech niches.

**Example programs:**
| Merchant | Commission | Niche |
|---|---|---|
| WP Engine (hosting) | $200/sale | Tech |
| Erin Condren (planners) | 10% | Lifestyle |
| NutriSystem | $40/sale | Health |
| Viator (travel) | 8% | Travel |
| Freshbooks | $5–$55 | Finance |

**Setup complexity:** Easy
**Maintenance:** Zero
**Requirement:** Account must be approved (usually instant)

---

### Stream 4: CJ Affiliate (Commission Junction)

**What it is:** Premium affiliate network. Major brands. High commissions.

**Example programs:**
| Brand | Commission | Niche |
|---|---|---|
| Overstock.com | 6% | Home |
| Lowe's | 2% | Home |
| Expedia | 6% | Travel |
| Hotels.com | 4% | Travel |
| GNC | 5% | Health |
| Bankrate | $0.50–$8 per lead | Finance |

**Setup complexity:** Medium (approval required)
**Maintenance:** Zero

---

### Stream 5: YouTube Ad Revenue

**What it is:** The bot creates a video version of every article (text → voiceover → slides) and uploads it to your YouTube channel. Once you hit 1,000 subscribers + 4,000 watch hours, YouTube pays you for ads shown on your videos.

**How much:** $1–$5 RPM (revenue per 1,000 YouTube views)
- Finance content: up to $15 RPM
- Health content: $3–$8 RPM

**Timeline to monetization:** Typically 12–24 months of consistent uploads
**Setup complexity:** Medium (YouTube API setup required)
**Maintenance:** Zero after initial auth

---

### Stream 6: Pinterest Traffic (Multiplier)

**What it is:** Pinterest is a search engine disguised as social media. The bot creates a pin (image + link) for every article and posts it. Pinterest drives free traffic directly to your articles — amplifying all other revenue streams.

**Direct income:** $0 (Pinterest doesn't pay you)
**Indirect income:** More traffic = more AdSense + more affiliate clicks
**Why it matters:** Pinterest traffic can appear in days vs. Google's 3–6 months. It's your early traffic source.

**Setup complexity:** Easy (Pinterest API — free)
**Maintenance:** Zero

---

## 7. The 5 Niches

The bot is pre-configured with these 5 niches, chosen for maximum affiliate commission potential and evergreen demand:

### Niche 1: AI Tools & SaaS
- **Why profitable:** Software products pay 20–40% recurring commissions. Every sale pays you every month the customer stays.
- **Target audience:** Business owners, entrepreneurs, content creators
- **Example articles bot writes:**
  - "Best AI Writing Tools in 2026 (Reviewed)"
  - "Top 10 ChatGPT Alternatives for Business"
  - "How to Automate Your Business with AI in 2026"
- **Affiliate programs:** Jasper AI, Notion AI, Surfer SEO, Copy.ai
- **Est. commission per sale:** $15–$80/month recurring

### Niche 2: Personal Finance & Investing
- **Why profitable:** Financial products pay the highest commissions in affiliate marketing. One sign-up = $50–$150.
- **Target audience:** Adults 25–45, anyone looking to manage money better
- **Example articles:**
  - "Best Budgeting Apps 2026 (Free & Paid)"
  - "How to Start Investing with $100"
  - "Passive Income Ideas That Actually Work"
- **Affiliate programs:** Empower, Acorns, Rocket Money, CreditKarma
- **Est. commission:** $10–$150 per lead/signup

### Niche 3: Health & Biohacking
- **Why profitable:** Health products are impulse purchases. High-volume, repeat buyers. Amazon commissions on supplements.
- **Target audience:** Health-conscious adults, fitness enthusiasts, men 30–50
- **Example articles:**
  - "Best Supplements for Energy in 2026"
  - "Cold Plunge Benefits: What Science Says"
  - "Intermittent Fasting for Beginners: Complete Guide"
- **Affiliate programs:** Amazon Health, Thrive Market, iHerb
- **Est. commission:** $5–$40 per sale

### Niche 4: Home Tech & Smart Devices
- **Why profitable:** High-ticket items ($100–$500) on Amazon. 3–8% of $300 = $9–$24 per sale. Frequent new product releases = constant fresh content.
- **Target audience:** Homeowners, renters, tech enthusiasts
- **Example articles:**
  - "Best Robot Vacuums 2026: Roomba vs Shark vs Ecovacs"
  - "Top Smart Thermostats for Saving Money"
  - "Best Smart Home Security System 2026"
- **Affiliate programs:** Amazon Smart Home, Best Buy
- **Est. commission:** $5–$30 per sale

### Niche 5: Travel
- **Why profitable:** Travel bookings have high value ($500–$5,000+ per booking). 4–8% of a $600 hotel booking = $24–$48.
- **Target audience:** Everyone who travels (huge audience)
- **Example articles:**
  - "Best Travel Credit Cards 2026 (No Annual Fee)"
  - "Cheapest Ways to Travel Europe in 2026"
  - "Best Travel Insurance Companies Reviewed"
- **Affiliate programs:** Expedia, Hotels.com, Viator, World Nomads (insurance)
- **Est. commission:** $8–$60 per booking

---

## 8. System Architecture

```
content-generator-bot/
│
├── 📁 config/                    ← Configuration files (edit these)
│   ├── niches.yaml               ← All 5 niches, keywords, affiliate links
│   └── settings.yaml             ← Site title, video settings, dashboard settings
│
├── 📁 core/                      ← The brain of the bot (do not edit)
│   ├── llm_writer.py             ← Connects to Ollama, generates articles
│   ├── trend_finder.py           ← Fetches trending topics from Google Trends
│   ├── affiliate_injector.py     ← Injects affiliate links into articles
│   ├── seo_optimizer.py          ← Adds meta tags, sitemap, schema markup
│   ├── publisher.py              ← Builds static HTML files + homepage + niche index pages
│   ├── video_generator.py        ← Creates MP4 videos from articles
│   ├── youtube_uploader.py       ← Uploads videos to YouTube
│   ├── pinterest_poster.py       ← Posts pins to Pinterest
│   ├── scheduler.py              ← Runs everything on a daily schedule
│   └── analytics_tracker.py      ← Tracks all data in SQLite database
│
├── 📁 dashboard/                 ← Web monitoring interface
│   ├── app.py                    ← Flask web server (http://localhost:5002)
│   ├── templates/                ← HTML pages for dashboard
│   └── static/                   ← CSS + JavaScript for dashboard
│
├── 📁 site/                      ← Your actual website (this goes live)
│   ├── templates/                ← Blog article + homepage + niche index HTML templates
│   │   ├── index.html            ← Homepage template (hero, niche cards, posts grid)
│   │   ├── niche_index.html      ← Per-niche category page template
│   │   └── post.html             ← Individual article template
│   └── output/                   ← Generated website files (deploy this folder)
│       ├── index.html            ← Generated homepage
│       ├── ai_tools/index.html   ← AI Tools category page
│       ├── personal_finance/     ← Finance category page + articles
│       ├── health_biohacking/    ← Health category page + articles
│       ├── home_tech/            ← Home Tech category page + articles
│       └── travel/               ← Travel category page + articles
│
├── 📁 data/                      ← Local data storage
│   ├── posts.db                  ← SQLite database (all posts, clicks, income)
│   └── logs/                     ← Daily bot activity logs
│
├── 📁 scripts/                   ← Run these to control the bot
│   ├── setup.py                  ← First-time setup (run once)
│   ├── start_bot.py              ← Start everything
│   ├── start_dashboard.py        ← Start dashboard only
│   ├── test_run.py               ← Test one article cycle
│   └── rebuild_site.py           ← Rebuild all homepage + niche index pages
│
├── .env                          ← Your private config (API keys, settings)
├── .env.example                  ← Template for .env
├── requirements.txt              ← Python dependencies
└── Makefile                      ← Shortcuts (make setup, make run, etc.)
```

---

## 9. Prerequisites

### What You Need Before Starting

| Requirement | Minimum | Recommended |
|---|---|---|
| **Operating System** | Windows 10, macOS 11, Ubuntu 20.04 | Windows 11, macOS 13+, Ubuntu 22.04 |
| **Python** | 3.10 | 3.11 or 3.12 |
| **RAM** | 4GB | 8GB+ (for video generation) |
| **Disk Space** | 10GB free | 20GB+ (AI model is ~4GB) |
| **Internet** | Any broadband | Stable connection |
| **Git** | Any version | Latest |

### Accounts to Create (All Free)

Before you start, create these free accounts. You'll need them during setup:

- [ ] [GitHub](https://github.com) — to host your code and website
- [ ] [Google Account](https://accounts.google.com) — for AdSense + YouTube API
- [ ] [Amazon Associates](https://affiliate-program.amazon.com) — affiliate program
- [ ] [ShareASale](https://shareasale.com) — affiliate network
- [ ] [CJ Affiliate](https://cj.com) — affiliate network
- [ ] [Pinterest Business Account](https://business.pinterest.com) — auto-posting
- [ ] [Namecheap](https://namecheap.com) — to buy your domain (~$9/year)

---

## 10. Installation — Windows

### Step 1: Install Python

1. Go to [python.org/downloads](https://python.org/downloads)
2. Download Python 3.11 (the yellow "Download Python 3.11.x" button)
3. Run the installer
4. **IMPORTANT:** Check the box that says **"Add Python to PATH"** before clicking Install
5. Click "Install Now"
6. When done, click "Disable path length limit" if prompted

**Verify installation:**
Open PowerShell (press Windows key, type "PowerShell", press Enter) and run:
```powershell
python --version
```
You should see: `Python 3.11.x`

### Step 2: Install Git

1. Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2. Download and run the installer
3. Accept all defaults (just keep clicking Next)

**Verify:**
```powershell
git --version
```

### Step 3: Clone the Repository

```powershell
cd C:\Users\YourName\Documents
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
```

### Step 4: Run Setup

```powershell
python scripts/setup.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Create your `.env` file
- Initialize the database
- Download Chart.js

### Step 5: Activate Virtual Environment

```powershell
.venv\Scripts\activate
```

You will see `(.venv)` at the start of your command prompt. **Always activate this before running the bot.**

### Step 6: Edit Your .env File

```powershell
notepad .env
```

Fill in your details (see Section 21 for what to fill in).

---

## 11. Installation — macOS

### Step 1: Install Homebrew (Package Manager)

Open Terminal (press Cmd+Space, type "Terminal", press Enter):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the prompts. This may take 5–10 minutes.

### Step 2: Install Python and Git

```bash
brew install python@3.11 git
```

**Verify:**
```bash
python3 --version
git --version
```

### Step 3: Clone the Repository

```bash
cd ~/Documents
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
```

### Step 4: Run Setup

```bash
python3 scripts/setup.py
```

### Step 5: Activate Virtual Environment

```bash
source .venv/bin/activate
```

You will see `(.venv)` in your prompt.

### Step 6: Edit Your .env File

```bash
nano .env
```

Use Ctrl+X, then Y, then Enter to save.

---

## 12. Installation — Linux / VPS

### Step 1: Update System and Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3-pip git -y
```

### Step 2: Clone the Repository

```bash
cd ~
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
```

### Step 3: Run Setup

```bash
python3 scripts/setup.py
```

### Step 4: Activate Virtual Environment

```bash
source .venv/bin/activate
```

### Step 5: (VPS Only) Install Screen for Background Running

```bash
sudo apt install screen -y
```

To run the bot in background on a VPS:
```bash
screen -S bot
python scripts/start_bot.py
# Press Ctrl+A then D to detach
# To reattach: screen -r bot
```

---

## 13. Setting Up Ollama (Local AI)

Ollama is the free, local AI engine that writes your articles. It runs on your computer — no API costs, no internet needed for content generation.

### Install Ollama

**Windows:**
1. Go to [ollama.com/download](https://ollama.com/download)
2. Click "Download for Windows"
3. Run the `.exe` installer
4. Ollama starts automatically in your system tray

**macOS:**
1. Go to [ollama.com/download](https://ollama.com/download)
2. Click "Download for Mac"
3. Open the `.dmg` file and drag Ollama to Applications
4. Open Ollama from Applications

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Download the AI Model

After installing Ollama, open a new terminal/PowerShell and run:

```bash
ollama pull mistral
```

This downloads the Mistral 7B model (~4GB). It takes 5–15 minutes depending on your internet speed. This is a one-time download.

### Verify Ollama is Working

```bash
ollama run mistral "Write one sentence about AI tools."
```

You should see a response. If you do, Ollama is working correctly.

### How Much RAM Does Ollama Need?

| Model | RAM Required | Quality |
|---|---|---|
| mistral (recommended) | 8GB | Excellent |
| llama3 | 8GB | Excellent |
| phi3-mini | 4GB | Good (use if RAM limited) |

**If you have 4GB RAM:** Change `OLLAMA_MODEL=phi3:mini` in your `.env` file.

---

## 14. Domain Setup

### Step 1: Buy Your Domain

1. Go to [namecheap.com](https://namecheap.com)
2. Search for your desired domain name
3. Choose a `.com` domain (~$8.98/year)
4. Add to cart and checkout (no extras needed — decline everything)
5. Create a free Namecheap account and complete purchase

### Step 2: Update Your .env

```env
SITE_URL=https://yourdomain.com
SITE_NAME=Your Blog Name
```

### Step 3: Connect Domain to GitHub Pages (after deploying — see Section 25)

1. In Namecheap dashboard, go to your domain → Manage → Advanced DNS
2. Add these records:

| Type | Host | Value |
|---|---|---|
| A Record | @ | 185.199.108.153 |
| A Record | @ | 185.199.109.153 |
| A Record | @ | 185.199.110.153 |
| A Record | @ | 185.199.111.153 |
| CNAME Record | www | yourusername.github.io |

3. In your GitHub Pages repo: Settings → Pages → Custom domain → enter `yourdomain.com`
4. Check "Enforce HTTPS"

**DNS changes take up to 48 hours to propagate.**

---

## 15. Google AdSense Setup

### ⚠️ IMPORTANT: Apply AFTER you have 20–30 published articles and a custom domain

### Step 1: Apply for AdSense

1. Go to [adsense.google.com](https://adsense.google.com)
2. Click "Get started"
3. Sign in with your Google account
4. Enter your website URL (your custom domain)
5. Select your country
6. Click "Start using AdSense"

### Step 2: Connect Your Site

AdSense will give you a code snippet like this:
```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX"
     crossorigin="anonymous"></script>
```

1. Open `site/templates/post.html`
2. Find `<!-- PASTE YOUR ADSENSE CODE HERE -->`
3. Replace that comment with your AdSense code
4. Also do the same in `site/templates/index.html`
5. Re-run the publisher to regenerate all HTML files

### Step 3: Wait for Approval

- Google reviews your site manually
- Takes 2–4 weeks
- They check: content quality, originality, site navigation, privacy policy

### What Google Checks For (AdSense Requirements)

| Requirement | Status |
|---|---|
| Custom domain (not .github.io) | ✅ Must have |
| HTTPS (SSL certificate) | ✅ GitHub Pages provides free |
| Privacy Policy page | ✅ Bot generates this |
| About page | ✅ Bot generates this |
| Contact page | ✅ Add manually (just an email) |
| 15–30 original articles | ✅ Bot publishes these |
| Site age 2+ weeks | ⏳ Wait after first deploy |
| No copyright violations | ✅ AI-generated, no copying |
| No adult/violent content | ✅ All niches are safe |

### Step 4: After Approval

- Ads appear automatically on all pages
- You do NOT need to touch anything
- Check your AdSense dashboard monthly for earnings

**You only need ONE AdSense account for all 5 niches on your one domain.**

---

## 16. Amazon Associates Setup

### Step 1: Sign Up

1. Go to [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
2. Click "Sign up"
3. Sign in with your Amazon account (or create one)
4. Fill in your account info:
   - Website URL: your domain
   - Describe your site: "Review and guide blog covering technology, health, finance, home products and travel"
5. Enter your preferred Associate ID (this becomes your tracking tag, e.g., `myblog-20`)
6. Select how you'll drive traffic: "SEO / Blog content"
7. Complete the profile

### Step 2: Add Your Tag to .env

```env
AMAZON_AFFILIATE_TAG=myblog-20
```

The bot will automatically append `?tag=myblog-20` to all Amazon links in articles.

### Step 3: Important Rules

- You MUST make 3 qualifying sales within your first 180 days or your account closes
- Always include an affiliate disclosure on your site (the bot does this automatically)
- Never use Amazon images or prices in your content
- Never use Amazon affiliate links in emails

---

## 17. ShareASale Setup

### Step 1: Create Account

1. Go to [shareasale.com](https://shareasale.com)
2. Click "Affiliate Sign Up"
3. Choose a username and password
4. Enter your website URL
5. Describe your traffic sources (blog/SEO)
6. Submit application

### Step 2: Apply to Merchant Programs

Once approved (usually same day), search for and apply to these programs for your niches:

**For Health niche:**
- Search "supplements" or "health" in the merchant search
- Apply to: Thrive Market, iHerb, Vitacost

**For Travel niche:**
- Search "travel"
- Apply to: Viator, TripAdvisor, Travelzoo

**For Finance niche:**
- Search "finance"
- Apply to: FreshBooks, Credit Karma

### Step 3: Get Your Affiliate Links

1. After approval, go to Links → Get a Link/Banner
2. Copy your affiliate link for each merchant
3. Add them to `config/niches.yaml` under the appropriate niche

### Step 4: Update niches.yaml

For each program, find the section in `config/niches.yaml` and replace `YOUR_ID` with your actual affiliate link:

```yaml
affiliate_programs:
  - name: "Thrive Market"
    url: "https://thrivemarket.com/r/YOUR_ACTUAL_LINK"
    keywords: ["Thrive Market", "organic"]
```

---

## 18. CJ Affiliate Setup

### Step 1: Create Account

1. Go to [cj.com](https://cj.com)
2. Click "Publisher Sign Up"
3. Fill in your website details
4. Select your categories (all that apply to your niches)

### Step 2: Apply to Advertisers

After approval, search for and apply to:
- **Travel:** Expedia, Hotels.com, Priceline, Enterprise
- **Health:** GNC, Vitamin Shoppe
- **Home:** Lowe's, Overstock, Wayfair
- **Finance:** Bankrate, LendingTree

### Step 3: Get Deep Links

1. In CJ dashboard: Links → Get Links
2. Select a product or homepage link
3. Copy the tracking URL
4. Add to `config/niches.yaml`

---

## 19. YouTube API Setup

The bot creates video versions of every article and uploads them automatically to YouTube.

### Step 1: Create a YouTube Channel

1. Sign in to [youtube.com](https://youtube.com) with your Google account
2. Click your profile picture → "Create a channel"
3. Choose a channel name matching your site name (e.g., "TechLife Insights")
4. Add a channel description and profile picture

### Step 2: Enable YouTube Data API

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Name it "Content Bot" → Create
4. In the left menu: APIs & Services → Library
5. Search "YouTube Data API v3"
6. Click it → Click "Enable"

### Step 3: Create OAuth2 Credentials

1. Go to: APIs & Services → Credentials
2. Click "+ Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - User type: External
   - App name: "Content Bot"
   - Support email: your email
   - Click Save and Continue (skip the rest)
4. Back in Credentials → Create Credentials → OAuth client ID
   - Application type: **Desktop app**
   - Name: "Content Bot Desktop"
   - Click Create
5. Click "Download JSON"
6. Rename the downloaded file to `client_secrets.json`
7. Place it in the root of your project folder

### Step 4: Update .env

```env
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_CHANNEL_NAME=TechLife Insights
```

### Step 5: First-Time Authentication

The first time the bot tries to upload a video, it will:
1. Print a URL in the terminal
2. Open your browser automatically (or ask you to open it manually)
3. Ask you to sign in with your Google account
4. Ask for permission to manage your YouTube account
5. Click "Allow"
6. The token is saved to `data/youtube_token.json` — this never expires unless you revoke it

**This only happens ONCE.**

### YouTube Free Quota

The YouTube Data API is free but has daily limits:
- Quota per day: 10,000 units
- Each video upload: ~1,600 units
- **Free uploads per day: ~6 videos**
- The bot uploads 5 videos/day — well within the free quota

---

## 20. Pinterest Auto-Posting Setup

Pinterest drives early traffic to your site (before Google indexes your content).

### Step 1: Create Pinterest Business Account

1. Go to [business.pinterest.com](https://business.pinterest.com)
2. Click "Create a free business account"
3. Fill in your business name and website URL
4. Select "Blogger/Content Creator" as your business type

### Step 2: Create Boards for Each Niche

In Pinterest, create 5 boards (one per niche):
- "AI Tools & Productivity Tips"
- "Personal Finance & Investing"
- "Health & Biohacking Tips"
- "Smart Home & Tech Gadgets"
- "Travel Tips & Guides"

Note the board IDs (visible in the board URL).

### Step 3: Get Pinterest API Access

1. Go to [developers.pinterest.com](https://developers.pinterest.com)
2. Click "My Apps" → "Create App"
3. Fill in app name: "Content Bot"
4. Get your App ID and Secret
5. Generate an access token with `boards:write` and `pins:write` permissions

### Step 4: Update .env

```env
PINTEREST_ACCESS_TOKEN=your_access_token_here
PINTEREST_BOARD_AI_TOOLS=your_board_id_here
PINTEREST_BOARD_FINANCE=your_board_id_here
PINTEREST_BOARD_HEALTH=your_board_id_here
PINTEREST_BOARD_HOME_TECH=your_board_id_here
PINTEREST_BOARD_TRAVEL=your_board_id_here
```

---

## 21. Configuring Your Niches

### File: `config/niches.yaml`

This is the main config file. After setting up all affiliate accounts, update the placeholder URLs:

1. Open `config/niches.yaml` in any text editor
2. Replace every `YOUR_ID` with your actual affiliate link
3. Replace every `YOUR_TAG` with your Amazon tag (e.g., `myblog-20`)
4. Add any custom keywords relevant to products you want to promote

**Example — Before:**
```yaml
- name: "Jasper AI"
  url: "https://jasper.ai?aff=YOUR_ID"
  keywords: ["Jasper", "AI writer"]
```

**Example — After:**
```yaml
- name: "Jasper AI"
  url: "https://jasper.ai?aff=abc123xyz"
  keywords: ["Jasper", "AI writer", "Jasper AI"]
```

### Adding a New Affiliate Program

To add a new affiliate program to any niche:

```yaml
affiliate_programs:
  - name: "New Program Name"
    url: "https://youraffiliatelink.com/ref/YOUR_ID"
    keywords: ["keyword1", "keyword2", "brand name"]
```

The bot will automatically inject links whenever it writes an article mentioning those keywords.

---

## 22. Startup Manual

### First Time Ever Starting the Bot

```bash
# 1. Make sure you're in the project folder
cd content-generator-bot

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Make sure Ollama is running
# Windows: Check system tray for Ollama icon
# macOS: Ollama should be running in menu bar
# Linux: sudo systemctl start ollama

# 4. Test one article cycle first
python scripts/test_run.py

# 5. If test passes, start the full bot
python scripts/start_bot.py
```

### Starting the Bot (Normal Operation)

```bash
# Windows (PowerShell):
cd C:\Users\YourName\Documents\content-generator-bot
.venv\Scripts\activate
python scripts/start_bot.py

# macOS/Linux (Terminal):
cd ~/Documents/content-generator-bot
source .venv/bin/activate
python scripts/start_bot.py
```

### Starting Only the Dashboard (No Bot)

Useful for checking stats without running content generation:

```bash
# Windows:
.venv\Scripts\activate
python scripts/start_dashboard.py

# macOS/Linux:
source .venv/bin/activate
python scripts/start_dashboard.py
```

Then open: [http://localhost:5002](http://localhost:5002)

### Starting on VPS (Background, 24/7)

```bash
screen -S content-bot
source .venv/bin/activate
python scripts/start_bot.py
# Detach: Ctrl+A then D
# Reattach anytime: screen -r content-bot
```

### Makefile Shortcuts (macOS/Linux)

```bash
make setup      # First-time setup
make run        # Start full bot + dashboard
make dashboard  # Dashboard only
make test       # Test one article cycle
make unittest   # Run unit tests
```

### What Happens When Bot Starts

1. Loads `.env` configuration
2. Initializes/connects to SQLite database
3. Starts Flask dashboard at http://localhost:5002
4. Schedules all jobs via APScheduler
5. If database is empty (first run): runs an immediate test cycle for all niches
6. Prints confirmation: "Bot is running. Dashboard at http://localhost:5002"

---

## 23. Shutdown Manual

### Graceful Shutdown (Recommended)

Simply press `Ctrl+C` in the terminal where the bot is running.

The bot will:
1. Finish the current task (does not cut off mid-article)
2. Save all pending data to SQLite
3. Close database connections
4. Stop the scheduler
5. Stop the Flask server
6. Print "Bot stopped safely."

### Force Shutdown (Emergency Only)

If the bot is frozen and Ctrl+C doesn't work:

**Windows:**
```powershell
# Find the process
Get-Process python
# Kill it
Stop-Process -Name python -Force
```

**macOS/Linux:**
```bash
# Find the process ID
ps aux | grep python
# Kill it
kill -9 [PID]
```

### What NOT to Do

- ❌ Do NOT close the terminal window without pressing Ctrl+C first — this can corrupt the SQLite database
- ❌ Do NOT shut down your computer while the bot is running without stopping it first
- ❌ Do NOT delete `data/posts.db` — this contains all your analytics and income tracking

### Restarting After Shutdown

The bot resumes from where it left off. Your scheduled jobs will run at their next scheduled time. No data is lost.

---

## 24. The Dashboard

Access the dashboard at: **http://localhost:5002**

The dashboard only works while `start_bot.py` or `start_dashboard.py` is running.

### Page: Overview (/)

Shows:
- **Total Posts Published** — all articles across all niches
- **Total Videos Uploaded** — YouTube videos created
- **Estimated Monthly Income** — based on clicks × CTR × avg commission
- **Total Clicks Tracked** — affiliate link clicks through your site
- **Posts Over Time** chart — line graph of publishing activity
- **Income Over Time** chart — trend of estimated earnings
- **Recent Activity** — last 10 bot actions with status badges

### Page: Posts (/posts)

Shows every article ever published:
- Niche, Title, Date Published, Word Count, Affiliate Links Count, Estimated Clicks, Estimated Income
- Click "View" to open the actual published article

### Page: Analytics (/analytics)

Visual breakdown of performance:
- Bar chart: posts published per niche
- Bar chart: estimated income per niche
- Bar chart: clicks per niche

### Page: Logs (/logs)

Live bot activity log:
- Auto-refreshes every 5 seconds
- Color-coded: INFO (blue), SUCCESS (green), ERROR (red), WARNING (yellow)
- Filter by log level

### Page: Niches (/niches)

Overview of all 5 niche configurations:
- Shows enabled/disabled status
- Affiliate programs configured
- Post count per niche
- Next scheduled run time

### Income Estimation Note

The income shown in the dashboard is an **estimate** based on:
```
Estimated Income = Tracked Clicks × CTR (2%) × Avg Commission ($25)
```

This is a conservative estimate. Actual income depends on:
- Real conversion rates (varies by niche and traffic quality)
- Actual commission rates (varies by program)
- Whether you're approved for AdSense (adds RPM income on top)

---

## 25. Hosting Your Site for Free

The bot generates a complete static website in `site/output/`. This folder contains all your HTML articles. You need to deploy this folder to a web host.

### Option A: GitHub Pages (Recommended)

**Cost: $0 forever**

1. Create a new GitHub repository named `my-income-blog` (make it public)
2. Go to Settings → Pages → Source → "Deploy from a branch"
3. Select main branch → `/root` → Save
4. Push your `site/output/` contents to this repo

```bash
cd site/output

# Initialize git repository
git init

# Stage all files
git add .

# Create initial commit
git commit -m "Deploy site"

# Add GitHub repository as remote
git remote add origin https://github.com/yourusername/my-income-blog.git

# Push to GitHub
git push -u origin main
```

5. Your site is live at `https://yourusername.github.io/my-income-blog`
6. Add your custom domain (see Section 14)

**Auto-deploy script** (run this after each bot cycle to push new articles):
```bash
cd site/output
git add .
git commit -m "New articles"
git push
```

The bot can do this automatically — set `AUTO_DEPLOY_GITHUB=true` in `.env`.

### Option B: Netlify (Drag & Drop — Easiest)

**Cost: $0 (100GB bandwidth/mo)**

1. Go to [netlify.com](https://netlify.com) and sign up free
2. On the dashboard, drag and drop your `site/output/` folder onto the page
3. Your site is instantly live at a Netlify URL
4. To add custom domain: Site Settings → Domain Management → Add custom domain

**Auto-deploy with Netlify CLI:**
```bash
npm install -g netlify-cli
netlify deploy --dir=site/output --prod
```

### Option C: Cloudflare Pages (Currently Active — Best Performance — Free)

**Cost: $0 forever, unlimited bandwidth, unlimited requests**

Your site is live at: [https://tech-life-insights.com](https://tech-life-insights.com)

Cloudflare auto-deploys every time you push to GitHub. To deploy new content:

```bash
git add site/output/
git commit -m "New content"
git push origin main
```

**Cloudflare Pages Free Tier Limits:**
| Resource | Limit |
|---|---|
| Page views / requests | Unlimited |
| Bandwidth | Unlimited |
| Builds per month | 500 |
| Concurrent builds | 1 |
| Max file size | 25 MB |

You'll never hit these limits with normal use.

### After Deploying — Update Site URL

Update your `.env`:
```env
SITE_URL=https://tech-life-insights.com
```

Then regenerate all pages so links point to your live domain:
```bash
source contentgenerator/bin/activate
PYTHONPATH=. python scripts/rebuild_site.py
git add site/output/
git commit -m "Rebuild with live domain URL"
git push origin main
```

---

## 26. Maintaining the System

### Daily (Zero effort — bot does it)
- Bot generates 5 articles at 9 AM
- Bot generates 5 videos at 11 AM
- Bot posts 5 Pinterest pins at 1 PM
- Dashboard auto-updates hourly

### Weekly (5 minutes)
1. Check dashboard at http://localhost:5002
2. Review logs page for any ERROR entries
3. Check that new articles are appearing in `site/output/`
4. Push new articles to your hosting (if not auto-deploying)

### Monthly (15 minutes)
1. Check AdSense dashboard for earnings
2. Check Amazon Associates for commissions
3. Check ShareASale and CJ for commissions
4. Review which posts are getting the most clicks (Posts page)
5. Consider updating affiliate links for top-performing posts

### Quarterly (30 minutes)
1. Update `config/niches.yaml` with new keywords if Google Trends shows new topics
2. Check if any affiliate programs have changed their links
3. Update `OLLAMA_MODEL` if a better free model has been released
4. Run `ollama pull mistral` to get the latest model version

### Annual
1. Renew your domain (~$9–12)
2. Review niche performance and potentially add/remove niches
3. Apply to YouTube Partner Program if you've hit 1,000 subscribers

---

## 27. Troubleshooting

### Problem: "Ollama connection refused" error
**Fix:**
- Windows: Check system tray for Ollama icon. Right-click → Restart
- macOS: Open Applications → Ollama
- Linux: `sudo systemctl start ollama`
- Verify: `curl http://localhost:11434` should return "Ollama is running"

### Problem: "pytrends rate limit" error in logs
**Fix:** Normal behavior. pytrends uses Google Trends which rate-limits requests. The bot automatically retries and uses cached topics. No action needed.

### Problem: Video generation is slow
**Fix:** Normal. Generating a 3-5 minute MP4 takes 2–5 minutes on average hardware. If it's too slow, set `video.enabled: false` in `config/settings.yaml`.

### Problem: YouTube upload fails with "quota exceeded"
**Fix:** You've hit the daily free quota (10,000 units = ~6 uploads). The bot will retry tomorrow automatically. This is normal.

### Problem: Articles have no affiliate links injected
**Fix:** Check that you've replaced `YOUR_ID` in `config/niches.yaml` with real affiliate URLs. The keywords in the YAML must match words that appear in the articles.

### Problem: Dashboard shows no data
**Fix:** The bot needs to have run at least one cycle. Run `python scripts/test_run.py` to generate the first article.

### Problem: AdSense not showing ads
**Fix:**
1. Verify you added the AdSense code to `site/templates/post.html` and `site/templates/index.html`
2. Re-publish all articles by running `PYTHONPATH=. python scripts/rebuild_site.py`
3. Push the updated files: `git add site/output/ && git commit -m "Rebuild" && git push origin main`
4. AdSense can take 24 hours to start showing ads after first approval

### Problem: "ModuleNotFoundError" on startup
**Fix:** You forgot to activate the virtual environment.
- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

### Problem: Pinterest posts are failing
**Fix:** Your Pinterest access token may have expired. Re-generate it at [developers.pinterest.com](https://developers.pinterest.com) and update `.env`.

### Problem: Bot stops overnight (PC goes to sleep)
**Fix:** Disable sleep mode on your PC while the bot is running, or use a VPS ($4-6/mo) to run it 24/7.

---

## 28. FAQ

**Q: Do I need to pay for any AI API (like OpenAI)?**
A: No. The bot uses Ollama which runs the AI model locally on your computer for free. There are no API costs ever.

**Q: Do I need to pay for GitHub?**
A: No. GitHub is free and GitHub Pages (website hosting) is free.

**Q: Do I really only need ONE domain?**
A: Yes. One domain with subfolders for each niche (e.g., yourdomain.com/travel/, yourdomain.com/health/). One AdSense account covers the entire domain.

**Q: How long until I make my first dollar?**
A: Realistically 3–5 months. AdSense approval takes 2–4 weeks after you have 20+ articles. Google needs 3–6 months to start ranking your content.

**Q: What if Google doesn't approve my AdSense?**
A: You still earn from Amazon, ShareASale, and CJ affiliate links — these don't require AdSense. Apply again after adding more content.

**Q: Can I run this on a cheap laptop?**
A: Yes, if it has 4GB+ RAM and 10GB+ free disk space. For video generation, 8GB RAM is better.

**Q: Does the bot need to run 24/7?**
A: No. The bot runs scheduled jobs. As long as your computer is on during the scheduled times (9 AM–1 PM), it will run. A VPS removes this requirement.

**Q: Will Google penalize AI-written content?**
A: Google's policy is about content quality, not how it was written. The bot generates detailed, helpful articles. As long as the content is genuinely useful, Google ranks it normally.

**Q: How do I get YouTube monetized?**
A: You need 1,000 subscribers and 4,000 watch hours. With 5 videos/day, you'll have 1,825 videos in a year. Getting subscribers requires promoting your channel. Focus on AdSense and affiliate income first.

**Q: Can I add more niches?**
A: Yes. Copy a niche block in `config/niches.yaml`, change the name and keywords, run `PYTHONPATH=. python scripts/rebuild_site.py` to generate the new niche's index page, push to GitHub, and restart the bot. It will start covering the new niche automatically.

---

## 29. Legal & Compliance

### FTC Affiliate Disclosure (Required by Law)

The bot automatically adds this disclosure to every article:

> "This post contains affiliate links. If you purchase through these links, I may earn a commission at no extra cost to you."

This is legally required in the United States and most countries.

### Google AdSense Policies

- Never click your own ads
- Never ask others to click your ads ("click my ads please")
- Do not place ads on pages with adult content
- Do not place more than 3 ad units per page

### Amazon Associates Terms

- Must disclose affiliate relationship on every page that contains Amazon links
- Cannot use Amazon product images without their official API
- Must make 3 qualifying sales in first 180 days or account closes
- Cannot include Amazon affiliate links in emails or PDF downloads

### GDPR / Privacy Policy

The bot generates a Privacy Policy page for your site. You must have one because:
- Google AdSense requires it
- Amazon Associates requires it
- GDPR requires it for EU visitors

Review the generated Privacy Policy and make sure it accurately describes how your site collects data (it doesn't collect personal data — the bot's click tracking is anonymous).

### Copyright

All content is generated by the AI and is original. You own it. There is no copyright issue with AI-generated content as of 2026. Do not manually copy text from other websites.

---

*Manual Version 1.0 — March 2026*
*For the latest updates, check the repository README.*