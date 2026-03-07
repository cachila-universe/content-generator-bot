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
30. [Formspree — Contact Form Setup](#30-formspree--making-your-contact-form-work)
31. [Best Free AI Models (by RAM)](#31-best-free-ai-models-ranked-by-quality)
32. [Google AdSense — Auto Ads (No Space Reserved Needed)](#32-google-adsense--do-you-need-to-reserve-space)
33. [Amazon Product Cards in Articles](#33-amazon-product-cards-in-articles)
34. [Daily Bot Schedule](#34-daily-bot-schedule)
35. [Maintenance Schedule](#35-maintenance-schedule)
36. [YouTube Video Quality Tips](#36-youtube-video-quality-tips)
37. [Pinterest — Status & Configuration](#37-pinterest--status--configuration)
38. [Windows PC Migration](#38-windows-pc-migration)
39. [Newsletter Email List Setup — "📬 Get Our Best Guides Weekly"](#39-newsletter-email-list--how-to-set-up--get-our-best-guides-weekly)
40. [YouTube — Best Free Video Content Makers](#40-youtube--best-free-video-content-makers)
41. [YouTube Channel — Connect the Bot for Auto-Uploads](#41-youtube-channel--connect-the-bot-for-auto-uploads)
42. [Social Media Auto-Posting (Twitter, Instagram Reels, TikTok)](#42-social-media-auto-posting-twitter-instagram-reels-tiktok)
43. [Video Generation: Edge TTS Neural Voices & Visual Variety](#43-video-generation-edge-tts-neural-voices--visual-variety)
44. [AI Stock Image Generator — Multi-API Cascade](#44-ai-stock-image-generator--multi-api-cascade)
45. [Trend Intelligence System — Self-Learning Brain](#45-trend-intelligence-system--self-learning-brain)
46. [Bot Modes — Paused, Scheduled & Manual](#46-bot-modes--paused-scheduled--manual)
47. [Twitter/X Auto-Posting for Articles & Videos](#47-twitterx-auto-posting-for-articles--videos)

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

*Manual Version 2.0 — March 2026*
*For the latest updates, check the repository README.*

---

## 30. Formspree — Making Your Contact Form Work

Your contact page (`/contact.html`) has a form that submits to Formspree. Without setting this up, the form does nothing.

### Step-by-Step Formspree Setup (Free — No Server Needed)

1. **Sign up** at [formspree.io](https://formspree.io) — free plan allows 50 submissions/month
2. In your Formspree dashboard, click **+ New Form**
3. Name it "Tech Life Insights Contact"
4. Copy the **8-character Form ID** shown (e.g., `xpznkqrb`)
5. Open `site/templates/contact.html`
6. Find the line:
   ```html
   <form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
   ```
7. Replace `YOUR_FORM_ID` with your real ID:
   ```html
   <form action="https://formspree.io/f/xpznkqrb" method="POST">
   ```
8. Rebuild and push:
   ```bash
   PYTHONPATH=. python scripts/rebuild_site.py
   git add site/output/ site/templates/
   git commit -m "Add Formspree contact form"
   git push origin main
   ```
9. Test by submitting the form — you'll receive an email at your Formspree-registered address

### What Email Does Formspree Send To?

> **Formspree sends all form submissions to the email address you used when you signed up at [formspree.io](https://formspree.io).**

To check or change the notification email:
1. Log in at [formspree.io](https://formspree.io)
2. Click on your form → **Settings** → **Email Notifications**
3. You can add multiple recipient emails here
4. You can also set a **custom redirect URL** after submission (e.g., a "Thank You" page)

### Formspree Free Plan Limits
| Feature | Free |
|---|---|
| Submissions / month | 50 |
| Email notifications | ✅ Yes |
| Spam filter | ✅ Yes |
| File uploads | ❌ No |
| Custom redirect after submit | ❌ No (upgrade to $8/mo) |

> 50 submissions/month is plenty for a growing site. Upgrade only if you get a lot of contact requests.

### ⚠️ Troubleshooting — "Form not found. Please check the form hashid."

This is the #1 Formspree error. Here's exactly what causes it and how to fix it:

**Cause 1 — The form ID in `contact.html` is a placeholder, not your real form**
The file currently contains `xwvrkzov` which was a test ID. You need to replace it with YOUR form's ID.

**Cause 2 — You haven't created a form in Formspree yet**
Signing up for Formspree is NOT enough. You must also create a form:
1. Log in at [formspree.io](https://formspree.io)
2. Click **+ New Form** (top right of dashboard)
3. Name it anything → **Create Form**
4. Copy the 8-character ID from the endpoint URL shown (e.g. `xpznkqrb`)

**Cause 3 — First submission requires activation (most missed step)**
After you update the form ID and push, submit the form ONCE on your live site. Formspree will send you an **"Activate Your Form"** email. **You must click the confirmation link in that email.** Until you do, ALL submissions return "Form not found" — even with a valid ID.

**Step-by-step fix:**
```bash
# 1. Update site/templates/contact.html — replace xwvrkzov with your real ID
# (Edit the file, find xwvrkzov, replace it)

# 2. Rebuild and push
PYTHONPATH=. python scripts/rebuild_site.py
git add site/output/ site/templates/contact.html
git commit -m "Fix Formspree form ID"
git push origin main

# 3. Go to https://tech-life-insights.com/contact.html
# 4. Submit the form with your own email
# 5. Check your inbox for "Activate your Formspree form" → click the link
# 6. Done — all future submissions deliver to your inbox
```

### Formspree Alternatives (Also Free)

| Service | Free Plan | Notes |
|---|---|---|
| [Formspree](https://formspree.io) | 50/mo | Easiest, no setup |
| [Basin](https://usebasin.com) | 100/mo | More features |
| [Web3Forms](https://web3forms.com) | 250/mo | Most generous free tier |
| [Getform](https://getform.io) | 50/mo | Good UI |

To use Web3Forms instead (250 submissions/month free):
1. Sign up at [web3forms.com](https://web3forms.com)
2. Get your access key
3. Change the form action:
   ```html
   <form action="https://api.web3forms.com/submit" method="POST">
   <input type="hidden" name="access_key" value="YOUR_WEB3FORMS_KEY">
   ```

---

## 31. Best Free AI Models (Ranked by Quality)

Your system uses Ollama to run AI models locally — completely free, no API costs.
The default model is `llama3.1:8b`. Here are all the best options ranked by quality.

### Quick Reference by RAM

| Your RAM | Best Model to Use | How to Install |
|---|---|---|
| 8 GB | `llama3.1:8b` (current default) | Already installed |
| 8 GB | `gemma3:12b` (better quality, same RAM) | `ollama pull gemma3:12b` |
| 16 GB | `qwen2.5:14b` (excellent articles) | `ollama pull qwen2.5:14b` |
| 16 GB | `phi4:14b` (Microsoft, very good) | `ollama pull phi4:14b` |
| 24 GB | `llama3.3:70b-instruct-q2_K` (near-GPT4 quality) | `ollama pull llama3.3` |
| 32 GB | `llama3.1:70b` (best all-rounder) | `ollama pull llama3.1:70b` |
| 48 GB+ | `llama3.3:70b` (best free model available) | `ollama pull llama3.3:70b` |

### Full Rankings (Best Free Models for Article Writing)

1. **`llama3.3:70b`** — Best quality. Near GPT-4. Needs 40 GB RAM. ~20 min/article.
2. **`llama3.1:70b`** — Excellent. Very well-rounded writer. Needs 40 GB RAM.
3. **`qwen2.5:14b`** — Best under 16 GB. Extremely good at structured content.
4. **`phi4:14b`** — Microsoft's model. Excellent reasoning, very clean output.
5. **`gemma3:12b`** — Google's model. Fast, good at SEO-style articles. Needs only 8 GB.
6. **`mistral-nemo:12b`** — Balanced quality/speed. Good multilingual support.
7. **`llama3.1:8b`** — Current default. Fast, decent quality. 8 GB RAM.
8. **`mistral:7b`** — Original model. Reliable but slightly lower quality than llama3.1.

### How to Switch Models

**Option A — In `.env` file:**
```env
OLLAMA_MODEL=qwen2.5:14b
```

**Option B — In `core/llm_writer.py`:**
Find the line:
```python
model = os.getenv("OLLAMA_MODEL", "llama3.1")
```
Change `"llama3.1"` to whichever model you want.

**Test a model before switching:**
```bash
ollama run qwen2.5:14b "Write a 200-word intro for an article about the best robot vacuums in 2026."
```

### Tips for Best Article Quality (Any Model)

- **More RAM = better quality**: Even llama3.1:8b performs noticeably better with 16 GB vs 8 GB
- **Use quantized models carefully**: `q4_0` is fast but lower quality than `q8_0`
- **Try `qwen2.5:14b` first if you have 16 GB** — many users find it writes better SEO articles than llama3.1:70b for its size
- The prompt in `core/llm_writer.py` has been tuned for SEO article quality — you generally don't need to change it

---

## 32. Google AdSense — Do You Need to Reserve Space?

> ✅ **No action needed right now.** Once your AdSense account is approved, you paste **ONE `<script>` tag** into `<head>` of your templates — Google Auto Ads handles placement automatically across every article and page. You don't need to reserve ad space, add divs, or change any content layout.

**Short answer: No. AdSense Auto Ads handles placement automatically.**

### How AdSense Auto Ads Works

1. You add ONE snippet of JavaScript to your site's `<head>` tag
2. Google's AI automatically scans every page and inserts ads in optimal positions
3. You don't need to mark anything, leave space, or add div tags
4. Google tests different ad positions and optimizes for maximum revenue over time

### Setting Up AdSense Auto Ads (After Approval)

Once Google approves your AdSense account:

1. Log in to [adsense.google.com](https://adsense.google.com)
2. Go to **Ads** → **Overview** → **By site**
3. Click **Get code** next to your site
4. Copy the code snippet (looks like this):
   ```html
   <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
        crossorigin="anonymous"></script>
   ```
5. Open `site/templates/post.html` and paste it inside `<head>`, just before `</head>`:
   ```html
   <!-- Google AdSense Auto Ads -->
   <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
        crossorigin="anonymous"></script>
   </head>
   ```
6. Do the same for `site/templates/index.html` and `site/templates/niche_index.html`
7. Rebuild and push:
   ```bash
   PYTHONPATH=. python scripts/rebuild_site.py
   git add site/output/ site/templates/
   git commit -m "Add AdSense Auto Ads"
   git push origin main
   ```
8. In AdSense, enable **Auto Ads** for your site
9. Ads will appear within 24 hours

### What AdSense Inserts Automatically

- In-article ads (between paragraphs)
- Display ads (above/below content)
- Sticky ads (fixed to screen edges on mobile)
- Multiplex ads (grid of related content ads)

> **You do NOT need to manually place ad slots.** The blank ad slots that were in the old templates have already been replaced with content CTAs. Auto Ads handles everything.

### Getting AdSense Approved

You must apply BEFORE you get the code. Requirements:
- **Live site** with real content (at least 20+ articles is a good baseline)
- **Privacy Policy** page (already at `/privacy.html`)
- **No prohibited content** (all bot content is safe)
- **Navigable site** (all niche pages, home page working)

**Timeline**: Submit → 1–2 weeks for review → approval email → paste code → ads go live within 24 hours.

---

## 33. Amazon Product Cards in Articles

To boost affiliate income, embed specific Amazon product recommendations in your articles. These are pre-configured product links the bot injects alongside the general Amazon tag.

### Method 1 — Add Specific Products to `niches.yaml` (Easiest)

For each niche, add specific product ASINs (Amazon product IDs) as keyword matches:

```yaml
affiliate_programs:
  - name: "Amazon Recommended Products"
    url: "https://amazon.com/dp/B0CQHZPF4X?tag=techlife0ac-20"
    keywords: ["best robot vacuum", "Roomba j9+"]
  - name: "Amazon Standing Desk"
    url: "https://amazon.com/dp/B09B94ZM45?tag=techlife0ac-20"
    keywords: ["standing desk", "adjustable desk", "sit stand desk"]
```

**How to find the ASIN:**
1. Go to [amazon.com](https://amazon.com) and find the product
2. The ASIN is in the URL: `amazon.com/dp/B0CQHZPF4X/...` — the `B0CQHZPF4X` part
3. Build the affiliate URL: `https://amazon.com/dp/ASIN?tag=techlife0ac-20`

### Method 2 — Amazon Native Shopping Ads (After Approval)

Once approved for AdSense, you can also use **Amazon Native Shopping Ads** which automatically show relevant Amazon products:

1. Log in to [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
2. Go to **Product Linking** → **Native Shopping Ads**
3. Create a "Recommendation Ad" — Amazon auto-picks products based on page content
4. Copy the ad code and paste into your article templates

### Recommended Products by Niche (Pre-set Up)

Add these specific product links to your `niches.yaml` for each niche:

**AI Tools niche** (best-selling tech gadgets / software subscriptions):
```yaml
- name: "Amazon Keyboard for AI Productivity"
  url: "https://amazon.com/dp/B09BNB8W5X?tag=techlife0ac-20"
  keywords: ["mechanical keyboard", "productivity keyboard"]
```

**Health & Biohacking** (already configured for supplements):
```yaml
- name: "Amazon Creatine Monohydrate"
  url: "https://amazon.com/s?k=creatine+monohydrate&tag=techlife0ac-20"
  keywords: ["creatine", "creatine monohydrate"]
```

**Note on Amazon Search Links:** Use `amazon.com/s?k=KEYWORD&tag=TAG` for search pages instead of specific products. This still earns commissions and is more durable (products go out of stock).

Example for any niche:
```yaml
- name: "Amazon Search - Best Products"
  url: "https://amazon.com/s?k=best+robot+vacuum+2026&tag=techlife0ac-20"
  keywords: ["robot vacuum", "best robot vacuum"]
```

---

## 34. Daily Bot Schedule

Here is exactly what the bot does every day when running:

| Time | Job | What Happens |
|---|---|---|
| 8:00 AM | Trend Fetch | Queries Google Trends for all 8 niches. Falls back to seed keywords if rate-limited. Caches to `data/trends_cache.json`. Deduplicates against already-published topics. |
| 9:00 AM | AI Tools post | Topic → llama3.1 writes 1,000–1,400 word article → affiliate links injected (Amazon only if configured) → SEO meta tags → HTML published to `site/output/ai_tools/` |
| 9:15 AM | Finance post | Same pipeline for Personal Finance |
| 9:30 AM | Health post | Same for Health & Biohacking |
| 9:45 AM | Home Tech post | Same for Home Tech |
| 9:50 AM | Travel post | Same for Travel |
| 10:00 AM | Pet Care post | Same for Pet Care (new niche) |
| 10:15 AM | Fitness post | Same for Fitness & Wellness (new niche) |
| 10:30 AM | Remote Work post | Same for Remote Work (new niche) |
| 11:00 AM | AI Tools video | Article → key points extracted → gTTS audio narration → Pillow slide images → MoviePy MP4 → uploaded to YouTube |
| 11:15–11:50 AM | Remaining videos | Same video pipeline for all other niches |
| 12:00 PM | Pinterest (AI Tools) | 1000×1500 pin image generated → posted to Pinterest API → links back to article |
| 12:15–12:50 PM | Pinterest (all niches) | Same for all niches |
| 13:00–13:30 PM | New niche Pinterest | Pet Care, Fitness, Remote Work pins |
| Every hour | Income snapshot | Calculates estimated income from click data, saves to `income_snapshots` table |
| Sunday midnight | Full site rebuild | Rebuilds homepage and all niche index pages with all published posts |

> **Note**: Pinterest and YouTube jobs only run if the respective API credentials are configured in `.env`. If not configured, those jobs are silently skipped — no errors.

---

## 35. Maintenance Schedule

### Daily (Fully Automated — No Action Required)
- ✅ Bot publishes 8 articles (one per niche)
- ✅ Bot generates 8 videos and uploads to YouTube
- ✅ Bot posts 8 Pinterest pins
- ✅ Income estimates updated hourly

### Weekly (5–10 minutes)
- [ ] Open dashboard at http://localhost:5002
- [ ] Check **Logs** page for ERROR or WARNING entries
- [ ] Check **Posts** page — confirm articles are being published
- [ ] Push any new content to GitHub: `git add site/output/ && git commit -m "Weekly deploy" && git push`
- [ ] Check YouTube Studio — see which videos are getting views
- [ ] Delete any low-quality articles using the dashboard **Delete** button

### Monthly (15–20 minutes)
- [ ] Check AdSense dashboard for earnings progress
- [ ] Check Amazon Associates for commission reports
- [ ] Check ShareASale and CJ Affiliate for commissions
- [ ] Review top-performing articles (most clicks) in the Posts page
- [ ] Back up your database: `cp data/bot.db data/bot_backup_$(date +%Y%m%d).db`
- [ ] Check `ollama list` for model updates: `ollama pull llama3.1`
- [ ] Review and update affiliate URLs in `config/niches.yaml` if programs have changed

### Quarterly (30 minutes)
- [ ] Update seed keywords in `config/niches.yaml` based on trending topics
- [ ] Check Google Search Console for crawl errors and new keyword rankings
- [ ] Consider adding new niches (if bot is working well — more niches = more income)
- [ ] Run `pip install --upgrade -r requirements.txt` to update packages
- [ ] Review which niches are performing best and adjust posting schedule if needed

### Annual
- [ ] Renew domain name (~$9–12 via Namecheap or Cloudflare)
- [ ] Review all affiliate program terms (they change occasionally)
- [ ] Evaluate new AI models: `ollama search` for the latest releases
- [ ] Apply for YouTube Partner Program if you've hit 1,000 subscribers + 4,000 watch hours

---

## 36. YouTube Video Quality Tips

The bot auto-generates and uploads one video per article. Here's how to maximize quality.

### Current Video Format

The bot creates:
- Resolution: **1280×720** (HD)
- Style: Dark background slides with text + automated voiceover
- Audio: **gTTS** (Google Text-to-Speech — sounds robotic but is clear)
- Length: **3–6 minutes** (based on article word count)

### Tips for Better YouTube Performance

**Titles** (auto-generated from article title — usually good):
- The bot uses the exact article title
- Aim for 50–60 characters; the bot respects the 100-char YouTube limit

**Thumbnails** (auto-generated with Pillow):
- Current design: dark background, white text, green accent bar
- Customize colors in `core/youtube_uploader.py` → `_generate_thumbnail()`

**Descriptions** (auto-generated — includes affiliate links):
- Auto-includes affiliate program links — only configured ones (no placeholders)
- Change the default tags in `_build_tags()` in `youtube_uploader.py`

**Voice Quality Upgrade** (optional):
The default `gTTS` voice is robotic. For better quality, replace with Edge TTS (free, sounds natural):

```bash
pip install edge-tts
```

Then in `core/video_generator.py`, find the TTS call and replace it with:
```python
import edge_tts, asyncio

async def generate_tts_edge(text: str, output_path: str):
    voice = "en-US-AriaNeural"  # Natural-sounding voice
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

asyncio.run(generate_tts_edge(narration_text, str(audio_path)))
```

**Available Edge TTS voices** (all free):
- `en-US-AriaNeural` — Female, natural, professional
- `en-US-GuyNeural` — Male, natural, professional
- `en-US-JennyNeural` — Female, friendly
- `en-GB-SoniaNeural` — British female
- `en-AU-NatashaNeural` — Australian female

### Playlists

Organize your YouTube channel by creating playlists for each niche. The bot doesn't do this automatically, but you can:
1. Create a playlist in YouTube Studio for each niche
2. The bot's videos go into the general "Uploads" feed
3. Manually move them to the right playlist once/week (takes 5 minutes)

---

## 37. Pinterest — Status & Configuration

### Current Status
Pinterest API access requires **approval** from Pinterest. If your developer app is still pending:

- The bot automatically skips Pinterest posting if `PINTEREST_ACCESS_TOKEN` is not set
- No errors, no crashes — it just logs "Pinterest not configured, skipping"
- Once approved, simply add your token to `.env` and the bot will start posting

### Pinterest Approval Tips

If your application is pending or was rejected:
1. Ensure your Pinterest business account has a **complete profile** (bio, profile pic, cover photo)
2. Your developer app description should mention: "Automated content marketing for my website [your URL]"
3. The app needs scopes: `pins:read_write`, `boards:read_write`, `user_accounts:read`
4. Pinterest typically approves apps within **1–7 business days** if your account looks legitimate

### After Pinterest Approval

1. Generate an access token in [developers.pinterest.com/apps](https://developers.pinterest.com/apps/)
2. Create at least one board for each niche (or one general board)
3. Add to `.env`:
   ```env
   PINTEREST_ACCESS_TOKEN=your_token_here
   PINTEREST_BOARD_ID=your_board_id_here
   ```
4. Restart the bot — Pinterest posting will begin at the scheduled times

### Getting Your Pinterest Board ID
1. Go to your Pinterest profile → click a board
2. The URL is: `pinterest.com/username/board-name/`
3. To get the numeric ID, go to **Edit Board** → it's shown in the settings page
4. Or use the Pinterest API: `curl -H "Authorization: Bearer YOUR_TOKEN" https://api.pinterest.com/v5/boards`

---

## 38. Windows PC Migration

A dedicated guide for migrating this bot from macOS to a Windows PC is available in:

📄 **[WINDOWS_MIGRATION.md](WINDOWS_MIGRATION.md)**

Key topics covered:
- Windows software requirements and installation
- Setting up Python, Ollama, Git on Windows
- Transferring credentials and config files securely
- Auto-starting the bot on Windows boot via Task Scheduler
- Keeping the PC awake 24/7 without sleep interruptions
- Troubleshooting Windows-specific issues

---

## 39. Newsletter Email List — How to Set Up "📬 Get Our Best Guides Weekly"

### Is It Free?

**Yes — all recommended options below have a free plan that covers you until you grow.**

The "📬 Get Our Best Guides Weekly" banner on your homepage currently links to your contact page. It's cosmetic only — no real email list is connected yet. Here's how to set up a real newsletter for free.

---

### Option 1 — Mailchimp (Most Popular, Free Up to 500 Contacts)

**Free plan:** 500 subscribers, 1,000 emails/month

1. Sign up at [mailchimp.com](https://mailchimp.com) — click **Sign Up Free**
2. Create an **Audience** (this is your email list)
3. Go to **Audience** → **Signup forms** → **Form builder**
4. Customize the form title (e.g., "Get Our Best Guides Weekly")
5. Copy the **Form URL** from the top of the page — it looks like:
   `https://techlifeinsights.us21.list-manage.com/subscribe/post?u=...`
6. Open `site/templates/index.html` and find the "Subscribe Free →" button:
   ```html
   <a href="/contact.html" ...>Subscribe Free →</a>
   ```
7. Replace `/contact.html` with your Mailchimp form URL:
   ```html
   <a href="https://techlifeinsights.us21.list-manage.com/subscribe/post?u=..." ...>Subscribe Free →</a>
   ```
8. Do the same in `site/templates/niche_index.html` (the sidebar subscribe button)
9. Rebuild and push:
   ```bash
   PYTHONPATH=. python scripts/rebuild_site.py
   git add site/output/ site/templates/
   git commit -m "Connect newsletter to Mailchimp"
   git push origin main
   ```

> **Tip**: In Mailchimp you can also create a **Landing Page** (free) — a hosted signup page with a clean URL like `mailchi.mp/techlifeinsights/weekly`. Use this URL for your subscribe button instead.

---

### Option 2 — Brevo (Best Free Tier — 300 Emails/Day, Unlimited Contacts)

**Free plan:** Unlimited subscribers, 300 emails/day (9,000/month)

1. Sign up at [brevo.com](https://brevo.com)
2. Go to **Contacts** → **Forms** → **Create a subscription form**
3. Copy the embed code or the hosted form URL
4. Replace the subscribe button href as shown in Option 1, steps 6–9 above

> Brevo's free plan is the most generous for contacts. Once you have a large list, 300 emails/day is plenty for a weekly newsletter.

---

### Option 3 — ConvertKit / Kit ✅ RECOMMENDED (Free Up to 10,000 Subscribers)

**Free plan:** Up to 10,000 subscribers, unlimited landing pages, unlimited forms
**Best for:** Long-term growth — the most powerful free tier available

#### Full Setup Instructions

**Step 1 — Create your Kit account**
1. Go to [kit.com](https://kit.com) and click **Get started free**
2. Enter your name, email, and password → **Create account**
3. Answer the onboarding questions (choose "I'm a creator" and "Blogging/Content")
4. Verify your email address (click the link they send)

**Step 2 — Create a signup form**
1. In your Kit dashboard, click **Grow** → **Landing Pages & Forms**
2. Click **+ Create new** → choose **Form** (inline, not landing page)
3. Choose a template — "Minimal" or "Charlotte" look clean on blog sites
4. Customize the title: `📬 Get Our Best Guides Weekly`
5. Customize the description: `Free expert tips on AI, finance, health, home tech, travel, pet care, fitness & remote work — delivered to your inbox.`
6. In the form settings, set the **Success message**: "You're in! Check your inbox to confirm your subscription."
7. Click **Save** then **Publish**

**Step 3 — Get your form's hosted URL**
1. After publishing, click **Share** → copy the **URL** (it looks like `app.kit.com/forms/1234567/embed`)
2. Alternatively, copy the **Hosted URL** (e.g. `kit.com/techlife-insights/weekly-guides`)

**Step 4 — Update the Subscribe button on your site**
1. Open `site/templates/index.html`
2. Find the "Subscribe Free →" button — change the `href`:
   ```html
   <!-- FROM: -->
   <a href="/contact.html" style="...">Subscribe Free →</a>

   <!-- TO: -->
   <a href="https://app.kit.com/forms/YOUR_FORM_ID/hosted" target="_blank" rel="noopener" style="...">Subscribe Free →</a>
   ```
   (Replace `YOUR_FORM_ID` with the number from your Kit form URL)
3. Do the same in `site/templates/niche_index.html` (sidebar subscribe button):
   ```html
   <!-- Find: -->
   <a href="/contact.html" style="background:#2563eb;...">Subscribe Free →</a>
   <!-- Replace href the same way -->
   ```

**Step 5 — Rebuild and push**
```bash
PYTHONPATH=. python scripts/rebuild_site.py
git add site/output/ site/templates/
git commit -m "Connect newsletter to Kit/ConvertKit"
git push origin main
```

**Step 6 — Test**
1. Visit your live site at [tech-life-insights.com](https://tech-life-insights.com)
2. Click the **Subscribe Free →** button — it opens your Kit form
3. Enter a test email and subscribe
4. Check your inbox for the confirmation email — click it
5. In your Kit dashboard → **Subscribers** — you should see the new subscriber ✅

**Step 7 — Send your first broadcast (when ready)**
1. In Kit dashboard → **Send** → **Broadcasts** → **+ New broadcast**
2. Pick your 3–5 best new articles from the week
3. Write a short intro, paste article titles + links
4. **Send** — free plan lets you send unlimited broadcasts

#### What Emails Does Kit Send From?
Kit sends from `yourname@kit.com` by default. Once you have a custom domain, you can set up a custom "from" address like `hello@tech-life-insights.com`. (Available on free plan after domain verification.)

> **Kit vs Mailchimp:** Kit is better for long-term growth (10,000 free subscribers vs 500). Mailchimp is easier to embed inline. Either works — start with Kit if you want to scale without paying until you're large.

---

### Comparison

| Service | Free Contacts | Free Emails/Month | Ease | Best For |
|---|---|---|---|---|
| **Mailchimp** | 500 | 1,000 | ⭐⭐⭐⭐⭐ Easy | Getting started fast |
| **Brevo** | Unlimited | 9,000 (300/day) | ⭐⭐⭐⭐ Good | Most generous free tier |
| **ConvertKit/Kit** | 10,000 | Unlimited broadcasts | ⭐⭐⭐⭐ Good | Scaling up |
| **Substack** | Unlimited | Unlimited | ⭐⭐⭐⭐⭐ Easiest | Paid newsletters (10% fee on paid only) |

**Recommendation**: Start with **Brevo** (most generous free tier) or **Mailchimp** (easiest to embed). Migrate to ConvertKit when you hit 500+ subscribers.

---

### What to Send Your Subscribers

Once set up, use Mailchimp/Brevo to send a **weekly digest** of your best new articles. The bot publishes 8 articles/day — pick the top 3–5 for the weekly email. Takes 10 minutes/week.

---

## 40. YouTube — Best Free Video Content Makers

### What the Bot Already Uses

The bot auto-generates and uploads videos using:
- **MoviePy** — stitches slide images into MP4 video
- **gTTS (Google Text-to-Speech)** — converts article text to audio narration
- **Pillow** — generates slide images (text on colored backgrounds)

This works but produces a basic robotic-voice video. Here's how to upgrade for free.

---

### 🥇 Best Free Upgrade: Microsoft Edge TTS (Already Documented in §36)

**The single best free improvement you can make.** Replace gTTS with Edge TTS for a natural-sounding AI voice — it's free and requires no API key.

```bash
# Install (one command)
pip install edge-tts
```

Best free voices:
| Voice | Style |
|---|---|
| `en-US-AriaNeural` | Female, professional, warm |
| `en-US-GuyNeural` | Male, clear, natural |
| `en-US-JennyNeural` | Female, friendly, upbeat |
| `en-GB-RyanNeural` | British male, authoritative |
| `en-AU-NatashaNeural` | Australian female, clear |

See [§36 YouTube Video Quality Tips](#36-youtube-video-quality-tips) for the exact code swap.

---

### 🥈 CapCut Desktop (Free — Best for Editing & Shorts)

**Best for:** Polished Shorts with transitions, text effects, and auto-captions
**Download:** [capcut.com/download](https://www.capcut.com/download) (Windows + macOS)

What it does:
- Drag-and-drop video editor with one-click auto-captions
- 300+ free transitions and effects
- AI background remover
- Exports 1080p/4K with no watermark

**How to use with this bot:** The bot generates MP4 videos. Download them from YouTube Studio → drop into CapCut → add captions, music, and transitions → re-upload as Shorts.

---

### 🥉 Canva Video (Free Tier — Best for Thumbnails + Slideshows)

**Best for:** Professional thumbnails and simple slideshow videos
**Platform:** Browser at [canva.com](https://www.canva.com) — no download needed

Recommended uses:
1. **Thumbnails** → Create Design → YouTube Thumbnail (1280×720) → bold template → swap text → download
2. **Simple Shorts** → Upload your article Picsum images + Edge TTS audio → assemble into a 60-second Short

---

### DaVinci Resolve (Free — Professional Grade, No Watermark)

**Best for:** Serious video editing — Hollywood-grade editor, completely free forever
**Download:** [blackmagicdesign.com/products/davinciresolve](https://www.blackmagicdesign.com/products/davinciresolve) (Windows + macOS + Linux)

> Zero limitations on the free version. No watermark. No time limit. The paid version ($295 one-time) only adds collaboration tools — you don't need it.

---

### Recommended Free Stack

| Step | Tool | Cost |
|---|---|---|
| AI narration | Edge TTS `en-US-AriaNeural` | Free |
| Video assembly | MoviePy (bot handles automatically) | Free |
| Editing / Shorts | CapCut Desktop | Free |
| Thumbnails | Canva | Free |
| Pro editing | DaVinci Resolve | Free |
| Background music | [pixabay.com/music](https://pixabay.com/music) | Free (CC0 license) |
| Free B-roll video | [pexels.com/videos](https://www.pexels.com/videos) | Free (CC0 license) |

---

## 41. YouTube Channel — Connect the Bot for Auto-Uploads

Your channel: **[TechLife Insights YouTube](https://www.youtube.com/channel/UCV0XW2sQNv2TWqtz3wFAxhA)**

The bot is fully built to upload videos automatically. It only needs a one-time OAuth2 setup. Here's the complete process.

---

### What the Bot Uploads

Every day after publishing articles, the bot:
1. Converts each article into a narrated video (slide show + voice)
2. Generates a thumbnail (dark background with article title)
3. Uploads to YouTube with title, description, affiliate links, and tags
4. Stores the YouTube URL in the database

> Videos appear as **regular uploads** in your channel. YouTube Shorts need to be ≤60 seconds with `#Shorts` in the title (already configured in `settings.yaml`).

---

### Step 1 — Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** (top left) → **New Project**
3. Name it `TechLife Insights Bot` → **Create**
4. Make sure the new project is selected in the dropdown

### Step 2 — Enable the YouTube Data API

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for **YouTube Data API v3**
3. Click it → **Enable**

### Step 3 — Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. If prompted, configure the **OAuth consent screen** first:
   - User type: **External**
   - App name: `TechLife Insights Bot`
   - User support email: your email
   - Click **Save and Continue** through all screens
   - On the **Test users** screen, add YOUR Google account email → **Save**
4. Back on Create Credentials:
   - Application type: **Desktop app**
   - Name: `TechLife Bot Desktop`
   - Click **Create**
5. Click **Download JSON** → save the file as `client_secrets.json` in your project root:
   ```
   /Users/thekelvinlachica/Documents/Github/Projects/content-generator-bot/client_secrets.json
   ```

### Step 4 — Set the Credentials File Path in `.env`

Open your `.env` file (create it if it doesn't exist) and add:
```env
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
```

### Step 5 — Run the One-Time Authentication

This opens a browser window to authorize the bot:

```bash
cd /Users/thekelvinlachica/Documents/Github/Projects/content-generator-bot
source contentgenerator/bin/activate
PYTHONPATH=. python3 -c "from core.youtube_uploader import authenticate; authenticate()"
```

What happens:
1. A browser tab opens asking you to sign in with Google
2. Sign in with the **same Google account that owns your YouTube channel**
3. You'll see "This app isn't verified" — click **Advanced** → **Go to TechLife Insights Bot (unsafe)**
   (This is safe — it's YOUR app on YOUR Google account)
4. Click **Allow** on the permissions screen
5. The browser shows "The authentication flow has completed" — you can close it
6. The bot saves a token file to `data/youtube_token.json`

**You only need to do this ONCE.** The token auto-refreshes forever.

### Step 6 — Test the Upload

Generate a test article and verify the upload works:

```bash
source contentgenerator/bin/activate
PYTHONPATH=. python3 -c "
from core import youtube_uploader
from pathlib import Path
import os

# Quick test — checks credentials are valid
secrets = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE', 'client_secrets.json')
creds = youtube_uploader._get_credentials(secrets)
if creds and creds.valid:
    print('✅ YouTube credentials valid — bot is ready to upload!')
else:
    print('❌ Credentials invalid — re-run the authentication step')
"
```

### Step 7 — Let the Bot Run

Once authenticated, the bot automatically uploads videos at the scheduled times (see §34 Daily Schedule). No further action needed.

**To verify a successful upload:**
1. Check your YouTube Studio: [studio.youtube.com](https://studio.youtube.com)
2. Go to **Content** — new videos appear within a few minutes of upload
3. Or check the bot dashboard at http://localhost:5002 → **Posts** — URLs starting with `youtube.com/watch?v=` confirm successful uploads

---

### Troubleshooting YouTube Uploads

| Error | Cause | Fix |
|---|---|---|
| `YouTube client secrets not configured` | `.env` missing `YOUTUBE_CLIENT_SECRETS_FILE` | Add the line to `.env` |
| `client_secrets.json not found` | Wrong path | Put file in project root, or set full path in `.env` |
| `403 quotaExceeded` | Hit YouTube daily upload quota (10,000 units/day) | Wait 24 hours — resets at midnight Pacific |
| `Token expired` | Refresh token issue | Re-run the authentication step (Step 5) |
| `Video uploaded but not visible` | YouTube processing | Wait 5–10 minutes — large files take time to process |
| `This app isn't verified` at auth step | Normal for personal OAuth apps | Click Advanced → proceed (it's your own app) |

### Notes on YouTube Shorts vs Regular Videos

The bot currently generates **regular videos** (landscape 1280×720). To publish as **Shorts** (which get more algorithmic reach):

1. In `config/settings.yaml`, the `format: "shorts"` setting is already set
2. Shorts must be ≤60 seconds vertical (1080×1920) — this is already configured
3. The bot adds `#Shorts` to the title automatically when format is "shorts"

> **Best strategy**: publish as Shorts first (60s vertical clips get free views), then repost longer horizontal versions later.

---

## §42 — Social Media Auto-Posting (Twitter, Instagram Reels, TikTok)

The bot now supports automatic posting to **Twitter/X**, **Instagram Reels**, and **TikTok** via the `core/social_poster.py` module. Each platform is independently configurable — leave credentials blank to disable any platform.

### Architecture Overview

```
Article published ──▶ Tweet article link (Twitter)
                  ──▶ Upload Short video as tweet (Twitter)
                  ──▶ Post as Reel (Instagram)
                  ──▶ Post as TikTok video (TikTok)
```

All social credentials live in `config/settings.yaml` under the `social` key.

---

### §42.1 — Twitter/X Setup

**Requirements:**
- Twitter Developer account (free tier allows 1,500 tweets/month)
- App with OAuth 1.0a + v2 API access

**Step 1: Create a Twitter Developer App**

1. Go to [developer.x.com/en/portal/dashboard](https://developer.x.com/en/portal/dashboard)
2. Click **+ Create Project** → name it `TechLife Bot`
3. Under the project, click **+ Add App**
4. Choose **Production** environment
5. Save the **API Key**, **API Secret**, **Bearer Token**

**Step 2: Generate Access Tokens**

1. In your app settings → **Keys and Tokens**
2. Under **Authentication Tokens**, click **Generate** for:
   - Access Token
   - Access Token Secret
3. Make sure **App permissions** = **Read and Write**

**Step 3: Add Credentials to Settings**

Edit `config/settings.yaml`:

```yaml
social:
  twitter:
    api_key: "YOUR_API_KEY"
    api_secret: "YOUR_API_SECRET"
    access_token: "YOUR_ACCESS_TOKEN"
    access_token_secret: "YOUR_ACCESS_TOKEN_SECRET"
    bearer_token: "YOUR_BEARER_TOKEN"
```

**Step 4: Test**

```bash
source contentgenerator/bin/activate
python -c "
import yaml
from core.social_poster import TwitterPoster
cfg = yaml.safe_load(open('config/settings.yaml'))
tp = TwitterPoster(cfg['social']['twitter'])
print('✅ Twitter connected!' if tp.enabled else '❌ Twitter not configured')
"
```

**What gets posted to Twitter:**
- 📝 Article links with title + niche hashtags (auto-trimmed to 280 chars)
- 🎬 Short-form videos with captions (uploaded natively)

---

### §42.2 — Instagram Reels Setup

Instagram does **not** allow bots to upload Reels via a simple API key. You must go through Meta's full review process. Here's how it actually works:

#### What You Need

- Instagram **Business** or **Creator** account (not a personal account)
- A **Facebook Page** linked to that Instagram account
- A **Meta Developer App** that passes Meta's App Review
- A **public URL** where your video file is hosted (Instagram won't accept local files)

#### Step 1 — Convert Your Instagram to a Business Account

1. Open the Instagram app → tap your profile → ☰ → **Settings and privacy**
2. Scroll to **Account type and tools** → **Switch to professional account**
3. Choose **Business** (not Creator — Business gets full API access)
4. Connect it to a Facebook Page when prompted. If you don't have one, Instagram will create one for you

#### Step 2 — Create a Meta Developer App

1. Go to **https://developers.facebook.com/** → log in with the Facebook account that owns the Page
2. Click **My Apps** (top-right) → **Create App**
3. Choose app type: **Business**
4. Name it something like `TechLife Bot` → click **Create App**

#### Step 3 — Add Instagram Graph API to Your App

1. In your new app's dashboard, click **Add Product** in the left sidebar
2. Find **Instagram Graph API** → click **Set Up**
3. This adds the Instagram API to your app

#### Step 4 — Request Permissions (App Review Required)

This is the part most guides skip. You **must** submit your app for Meta review before you can publish content.

1. In your app dashboard, go to **App Review** → **Permissions and Features**
2. Request these permissions:
   - `instagram_basic` — read profile info
   - `instagram_content_publish` — publish Reels and posts
   - `pages_read_engagement` — required dependency
3. For each permission, you need to:
   - Write a description of how you'll use it (e.g., "Automated posting of educational tech videos as Reels")
   - Provide a screencast demo showing your app in action
   - Submit a privacy policy URL (use `https://tech-life-insights.com/privacy.html`)
4. Click **Submit for Review**
5. **Timeline:** Meta typically takes **3–7 business days** to review. You may get follow-up questions.

> ⚠️ **Until your app passes review, you can only use the API with test users added in the dashboard.** This is enough to test the pipeline.

#### Step 5 — Generate a Long-Lived Access Token

1. Go to **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
2. Select your app from the dropdown
3. Click **Generate Access Token** → grant the permissions when prompted
4. This gives you a **short-lived token** (valid ~1 hour). Exchange it for a long-lived one:

```bash
# Replace YOUR_APP_ID, YOUR_APP_SECRET, and YOUR_SHORT_TOKEN
curl -s "https://graph.facebook.com/v21.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=YOUR_APP_ID&\
client_secret=YOUR_APP_SECRET&\
fb_exchange_token=YOUR_SHORT_TOKEN" | python3 -m json.tool
```

The response gives you a token valid for **60 days**. Save it.

> 💡 **To auto-refresh before it expires**, set a reminder to regenerate every 50 days, or build a refresh script (the token endpoint returns a new long-lived token if you exchange the current one before expiry).

#### Step 6 — Find Your Instagram Business Account User ID

```bash
# Step A: Get your Facebook Page ID
curl -s "https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_LONG_LIVED_TOKEN" | python3 -m json.tool
# Look for the "id" field of your page

# Step B: Get the Instagram account linked to that page
curl -s "https://graph.facebook.com/v21.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_LONG_LIVED_TOKEN" | python3 -m json.tool
# The "instagram_business_account.id" is your ig_user_id
```

#### Step 7 — Add Credentials to Settings

Edit `config/settings.yaml`:

```yaml
social:
  instagram:
    access_token: "EAAxxxxxxxxx..."     # Your long-lived token from Step 5
    ig_user_id: "17841400xxxxxxx"        # Your IG user ID from Step 6
```

#### Step 8 — Test It

```bash
source contentgenerator/bin/activate
PYTHONPATH=. python -c "
import yaml
from core.social_poster import InstagramPoster
cfg = yaml.safe_load(open('config/settings.yaml'))
ip = InstagramPoster(cfg['social']['instagram'])
print('✅ Instagram connected!' if ip.enabled else '❌ Not configured')
"
```

#### How Posting Works

The bot **cannot** upload a local file directly to Instagram. Instead:

1. Bot generates a video locally (e.g., `data/videos/my-short.mp4`)
2. You push it to your site so it gets a public URL:
   ```bash
   cp data/videos/my-short.mp4 site/output/videos/
   git add site/output/videos/ && git commit -m "Add video" && git push
   # URL becomes: https://tech-life-insights.com/videos/my-short.mp4
   ```
3. The bot calls Instagram Graph API with that **public URL** → Instagram downloads and publishes it as a Reel

> ⚠️ **Common gotchas:**
> - Video must be MP4, H.264, AAC audio, 3–90 seconds, max 1GB
> - The URL must be directly accessible (no redirects, no auth walls)
> - Cloudflare Pages works perfectly as the video host
> - If your token expires you'll get a `190` error — regenerate it

---

### §42.3 — TikTok Setup

TikTok's Content Posting API also requires developer approval. It's stricter than Meta's.

#### What You Need

- A TikTok account (the one you'll post to)
- A TikTok Developer account with an approved app
- OAuth2 access token with `video.publish` scope
- A **public URL** where your video file is hosted

#### Step 1 — Register as a TikTok Developer

1. Go to **https://developers.tiktok.com/** → click **Log In** (use your TikTok account)
2. Fill in the developer registration form (name, email, purpose)
3. Accept the Terms of Service

#### Step 2 — Create an App

1. In the TikTok Developer Portal → **Manage Apps** → **Connect an app**
2. Fill in:
   - **App name:** `TechLife Bot`
   - **App description:** "Automated educational content posting for tech insights"
   - **App icon:** Upload your logo
   - **Category:** Media/Entertainment or Education
   - **Platform:** Web
3. Under **Products**, add: **Content Posting API**
4. Under **Scopes**, select: `video.publish`, `video.upload`

#### Step 3 — Submit for Review

1. Go to your app → **Submit for review**
2. You need to provide:
   - A **privacy policy URL** (`https://tech-life-insights.com/privacy.html`)
   - A **terms of service URL** (`https://tech-life-insights.com/terms.html`)
   - A description of your use case
   - A demo video or screenshots of your app
3. **Timeline:** TikTok reviews take **1–5 business days**, sometimes longer
4. You may be rejected the first time — common reasons: vague use case description, missing privacy policy. Resubmit with more detail.

> ⚠️ **TikTok is the strictest of the three platforms.** Many apps get rejected on the first try. Be specific about your use case: "We publish educational technology review videos to our TikTok audience. Each video summarizes an article from our website tech-life-insights.com."

#### Step 4 — Get an OAuth2 Access Token

Once approved, you need to run TikTok's OAuth2 flow to get a token for your account:

1. In your app settings, find your **Client Key** and **Client Secret**
2. Build the authorization URL:
   ```
   https://www.tiktok.com/v2/auth/authorize/?
     client_key=YOUR_CLIENT_KEY&
     scope=video.publish,video.upload&
     response_type=code&
     redirect_uri=https://tech-life-insights.com/callback&
     state=random_string
   ```
3. Open that URL in a browser → log into TikTok → authorize the app
4. You'll be redirected to your `redirect_uri` with a `?code=AUTH_CODE` parameter
5. Exchange the auth code for an access token:

```bash
curl -X POST "https://open.tiktokapis.com/v2/oauth/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_key=YOUR_CLIENT_KEY&client_secret=YOUR_CLIENT_SECRET&code=YOUR_AUTH_CODE&grant_type=authorization_code&redirect_uri=https://tech-life-insights.com/callback"
```

The response contains `access_token` (valid 24 hours) and `refresh_token` (valid 365 days).

> 💡 **The access token expires every 24 hours.** You must use the `refresh_token` to get a new one. A cron job or the bot's scheduler can handle this automatically.

#### Step 5 — Add to Settings

```yaml
social:
  tiktok:
    client_key: "YOUR_CLIENT_KEY"          # From TikTok Developer Portal
    client_secret: "YOUR_CLIENT_SECRET"    # From TikTok Developer Portal
    access_token: "YOUR_ACCESS_TOKEN"      # From OAuth2 flow
    refresh_token: "YOUR_REFRESH_TOKEN"    # For auto-renewal
```

#### Step 6 — Test It

```bash
source contentgenerator/bin/activate
PYTHONPATH=. python -c "
import yaml
from core.social_poster import TikTokPoster
cfg = yaml.safe_load(open('config/settings.yaml'))
tp = TikTokPoster(cfg['social']['tiktok'])
print('✅ TikTok connected!' if tp.enabled else '❌ Not configured')
"
```

#### How Posting Works

Same as Instagram — TikTok pulls the video from a **public URL**:

1. Bot generates video → push to site → get public URL
2. Bot calls TikTok Content Posting API with the URL
3. TikTok downloads and publishes it

> ⚠️ **Common gotchas:**
> - Video must be MP4, 1–60 seconds for feed, up to 10 min for long-form
> - Min resolution: 720p. Shorts (9:16) work best
> - The Content Posting API has a rate limit of **~20 posts/day**
> - If your access token expires, use the refresh token to get a new one

---

### §42.4 — Video Hosting for Instagram & TikTok

Both Instagram and TikTok require a **publicly accessible video URL** — they will NOT accept a local file upload. The simplest approach is to push videos to your Cloudflare Pages site:

```bash
# After generating a video:
mkdir -p site/output/videos
cp data/videos/my-short.mp4 site/output/videos/
git add site/output/videos/my-short.mp4
git commit -m "Add video for social posting"
git push origin main
# Cloudflare Pages deploys automatically in ~30 seconds
# Video URL: https://tech-life-insights.com/videos/my-short.mp4
```

**Other hosting options:**

| Method | Pros | Cons |
|---|---|---|
| **Cloudflare Pages** (current setup) | Free, already configured, auto-deploys | Git repo gets large with videos over time |
| **Cloudflare R2** | Free 10GB, purpose-built for media | Requires R2 bucket setup + API calls |
| **GitHub Release assets** | Free, up to 2GB per file | Manual upload, not automated easily |
| **AWS S3 / DigitalOcean Spaces** | Reliable, scalable | Costs ~$0.02/GB/month |

> 💡 **Recommendation:** Start with Cloudflare Pages (push to `site/output/videos/`). When your video library grows past ~500MB, move to Cloudflare R2 for dedicated media storage.

---

### §42.5 — Quick Reference: What's Working vs. Needs Setup

| Platform | Status | What You Need |
|---|---|---|
| **YouTube** | ✅ Working | Already configured — `client_secrets.json` + `data/youtube_token.json` |
| **Twitter/X** | ✅ Working | Already configured in `config/settings.yaml` |
| **Instagram** | ⬜ Needs Setup | Meta Developer App + App Review (~3–7 days) + public video URL |
| **TikTok** | ⬜ Needs Setup | TikTok Developer App + App Review (~1–5 days) + public video URL |

**Easiest order to set up:** YouTube → Twitter (done) → Instagram → TikTok

---

### §42.5 — Niche-Specific Hashtags

Each niche has pre-configured hashtags in `core/social_poster.py`:

| Niche | Hashtags |
|---|---|
| ai_tools | #AI #AITools #ArtificialIntelligence #Productivity #Tech |
| personal_finance | #PersonalFinance #Money #Investing #Budget #Finance |
| health_biohacking | #Health #Biohacking #Wellness #Longevity #HealthTech |
| home_tech | #SmartHome #HomeTech #IoT #Gadgets #HomeAutomation |
| travel | #Travel #TravelTips #TravelTech #DigitalNomad #Explore |
| pet_care | #Pets #PetCare #Dogs #Cats #PetHealth |
| fitness_wellness | #Fitness #Wellness #Workout #GymLife #HealthyLiving |
| remote_work | #RemoteWork #WFH #Productivity #DigitalNomad #WorkFromHome |

All posts also include `#TechLifeInsights` for brand recognition.

---

## §43 — Video Generation: Edge TTS Neural Voices & Visual Variety

The video pipeline now uses **Microsoft Edge TTS** — free, high-quality neural voices that sound natural (not robotic like the old gTTS).

### Voice Rotation (12 voices)

Every article gets a **different voice** based on its slug hash. No two videos in a row sound the same:

| Voice | Accent | Gender |
|---|---|---|
| en-US-GuyNeural | American | Male |
| en-US-JennyNeural | American | Female |
| en-US-AriaNeural | American | Female |
| en-US-DavisNeural | American | Male |
| en-US-TonyNeural | American | Male |
| en-US-SaraNeural | American | Female |
| en-GB-SoniaNeural | British | Female |
| en-GB-RyanNeural | British | Male |
| en-AU-NatashaNeural | Australian | Female |
| en-AU-WilliamNeural | Australian | Male |
| en-CA-ClaraNeural | Canadian | Female |
| en-CA-LiamNeural | Canadian | Male |

### Visual Theme Rotation (8 themes)

Each video gets a different color scheme:

- **Cyber Green** — dark bg + neon green accents
- **Royal Blue** — navy bg + soft blue accents
- **Sunset Orange** — warm dark bg + orange accents
- **Electric Purple** — deep purple bg + violet accents
- **Crimson Fire** — dark red bg + rose accents
- **Teal Wave** — dark teal bg + mint accents
- **Golden Dark** — dark gold bg + amber accents
- **Ice Slate** — slate bg + cyan accents

### Layout Rotation (4 layouts for landscape, 4 for shorts)

**Landscape (YouTube):** classic, centered, left_bar, gradient_banner
**Shorts (Reels/TikTok):** bold_center, numbered_card, side_stripe, top_gradient

### Testing Video Generation

```bash
source contentgenerator/bin/activate
PYTHONPATH=. python -c "
from core.video_generator import generate_video
from pathlib import Path

article = {
    'slug': 'test-video',
    'title': 'Top 5 AI Tools for Productivity in 2025',
    'html_content': '<p>AI tools are changing how we work.</p><h2>1. ChatGPT</h2><p>The most popular AI assistant.</p><h2>2. Notion AI</h2><p>Smart note-taking and docs.</p><h2>3. Grammarly</h2><p>AI-powered writing assistant.</p>',
}

result = generate_video(article, Path('data/test_video.mp4'))
print(f'✅ Video created: {result}' if result else '❌ Failed')
"
```

---

## §44 — AI Stock Image Generator — Multi-API Cascade

### Overview

The stock image generator creates **high-quality AI images** using a **multi-API cascade** system that automatically falls through to the next provider when one runs out of credits:

**Leonardo AI → Stability AI → HuggingFace SDXL → HuggingFace FLUX**

Images are tracked for:

1. **Stock photo platform submission** — Adobe Stock, Dreamstime, Freepik, Alamy, 123RF, Pond5, Wirestock
2. **Video backgrounds** — replaces Pexels images with unique AI-generated visuals
3. **Article hero images** — custom imagery for blog posts

All images carry **mandatory AI disclosure** metadata — this cannot be disabled.

### Multi-API Cascade — Priority Order

| Priority | Provider | Model | Free Tier | Quality |
|----------|----------|-------|-----------|---------|
| 🥇 1st | **Leonardo AI** | Leonardo Phoenix | 150 tokens/day (~20 images) | ⭐⭐⭐⭐⭐ |
| 🥈 2nd | **Stability AI** | SD 3.5 Medium | 25 credits (~7 images) | ⭐⭐⭐⭐⭐ |
| 🥉 3rd | **HuggingFace** | SDXL 1.0 | ~30 images/day | ⭐⭐⭐⭐ |
| 4th | **HuggingFace** | FLUX.1-schnell | ~30 images/day | ⭐⭐⭐ |
| Fallback | **Pexels** | N/A | 200 req/month | Stock photos |

**How the cascade works:**
1. The bot tries **Leonardo AI** first (highest quality)
2. If Leonardo returns 402 (out of tokens) or fails → tries **Stability AI**
3. If Stability returns 402 (out of credits) or fails → tries **HuggingFace SDXL**
4. If SDXL fails → tries **HuggingFace FLUX** as last resort
5. Every API call is logged to the `api_usage` database table for dashboard tracking

**No API key required to start** — the system works with just HuggingFace. Add Leonardo and Stability keys when available for higher quality output.

### Configuration

In `config/settings.yaml`:

```yaml
stock_images:
  enabled: true
  leonardo_api_key: ""         # Get FREE at https://app.leonardo.ai — 150 tokens/day
  stability_api_key: ""        # Get FREE at https://platform.stability.ai — 25 credits on signup
  huggingface_token: "hf_..."  # Get FREE at https://huggingface.co/settings/tokens
  primary_model: "stabilityai/stable-diffusion-xl-base-1.0"
  fallback_model: "black-forest-labs/FLUX.1-schnell"
  images_per_run: 5
  resolution: "1024x1024"
  use_in_videos: true
  ai_disclosure:
    enabled: true              # MANDATORY — DO NOT DISABLE
    title_prefix: "[AI Generated]"
    description_notice: "This content was created using generative artificial intelligence."
```

### How It Works

```
                              ┌──────────────┐
Article H2 / Trend Topics ──→│ Prompt Builder │
                              └──────┬───────┘
                                     ↓
                        ┌────────────────────────┐
                        │   Leonardo AI (best)    │──→ 402? ─┐
                        └────────────────────────┘          │
                        ┌────────────────────────┐          │
                    ┌───│   Stability AI (great)  │←─────────┘
                    │   └────────────────────────┘
                    │   ┌────────────────────────┐
               402? ├───│   HuggingFace SDXL     │
                    │   └────────────────────────┘
                    │   ┌────────────────────────┐
                    └──→│   HuggingFace FLUX     │
                        └───────────┬────────────┘
                                    ↓
                        ┌────────────────────────┐
                        │  Post-process + Save    │
                        │  + API Usage Logging    │
                        │  + AI Disclosure        │
                        └────────────────────────┘
```

#### Trend-Aware Image Generation

When the **Trend Intelligence System** (§45) is active, stock image generation uses trending topics and market demand data to pick the most commercially valuable subjects:

- **Google Trends** data determines what people are searching for
- **Niche-specific demand categories** ensure relevant output
- **Market demand scores** are stored per image for prioritization

#### Prompt Engineering

Each niche has 3 tailored prompt templates. A random **style modifier** is applied:

- **Photorealistic** — studio lighting, sharp focus
- **Digital Art** — vibrant colors, creative composition
- **Minimalist** — clean, soft palette
- **Cinematic** — dramatic lighting, wide aspect
- **Editorial** — magazine-quality, professional

A **quality suffix** ensures professional output:
> "4K resolution, highly detailed, professional stock photo, sharp focus, clean composition"

#### AI Disclosure (Mandatory)

Every generated image record includes:
- `ai_disclosed = 1` (always true, cannot be overridden)
- `ai_disclosure_text` — "This image was created using generative artificial intelligence."
- Keywords always include: `ai generated`, `artificial intelligence`, `ai art`, `generative ai`

This ensures compliance with stock platform requirements for AI-generated content.

### Video Integration

The image fetcher uses this **priority order** for video backgrounds:

1. **Local AI stock images** — check `stock_generator.get_usable_images_for_niche()`
2. **Pexels API** — fallback to stock photo search
3. **Gradient** — solid color fallback if all sources fail

When an AI image is used in a video, it's marked via `mark_used_in_video()` in the DB.

### Dashboard

The dashboard has a dedicated **Stock Images** tab (`/stock-images`) showing:

- Total generated / submitted / used in videos / storage size
- Image gallery with preview thumbnails
- One-click **Generate** button for batch creation (now uses trend intelligence for topics)
- AI disclosure badge on every image card
- **API Usage Stats** — per-provider breakdown (Leonardo / Stability / HuggingFace) with call counts, success rates, and last-used timestamps

### Database Schema

Table `stock_images`:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| filename | TEXT | UUID-based filename |
| filepath | TEXT | Absolute path on disk |
| prompt | TEXT | Full positive prompt used |
| topic | TEXT | Source topic / heading |
| niche_id | TEXT | Associated niche |
| category | TEXT | Content category |
| style | TEXT | Style modifier applied |
| resolution | TEXT | e.g. "1024x1024" |
| ai_model | TEXT | Model used (Leonardo / SD3.5 / SDXL / FLUX) |
| api_provider | TEXT | **NEW** — "leonardo" / "stability" / "huggingface" |
| trend_source | TEXT | **NEW** — Source trend that inspired this image |
| market_demand_score | REAL | **NEW** — 0.0–1.0 commercial demand score |
| ai_disclosed | INTEGER | Always 1 |
| ai_disclosure_text | TEXT | Disclosure notice |
| title | TEXT | Generated SEO title |
| description | TEXT | Generated description |
| keywords | TEXT | Comma-separated keywords |
| file_size_bytes | INTEGER | File size |
| status | TEXT | "generated" / "submitted" |
| platform_submissions | TEXT | JSON of platform submissions |
| generated_at | TEXT | Timestamp |
| used_in_video | INTEGER | 0 or 1 |

Table `api_usage` (**NEW**):

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| provider | TEXT | "leonardo" / "stability" / "huggingface" |
| endpoint | TEXT | API endpoint called |
| status_code | INTEGER | HTTP response code |
| success | INTEGER | 1 = success, 0 = failure |
| error_message | TEXT | Error details (if failed) |
| timestamp | TEXT | ISO timestamp |

### File Structure

```
core/stock_generator.py          # Multi-API cascade generator
data/stock_images/               # Output directory
  └── 2026/03/15/ai_tools/       # Organized by date + niche
       └── abc123def456.jpg
```

### Manual Test

```bash
source contentgenerator/bin/activate
PYTHONPATH=. python -c "
from core.stock_generator import generate_stock_images, get_api_usage_stats
import yaml

with open('config/settings.yaml') as f:
    settings = yaml.safe_load(f)

topics = [
    {'topic': 'AI productivity workspace setup', 'niche_id': 'ai_tools'},
    {'topic': 'Smart home technology dashboard', 'niche_id': 'home_tech'},
]

results = generate_stock_images(topics, settings, count=2)
for r in results:
    print(f'  ✓ {r[\"filename\"]} — {r[\"title\"]} via {r.get(\"api_provider\", \"unknown\")}')
print(f'Generated {len(results)} images')

# Check API usage
stats = get_api_usage_stats()
for provider, data in stats.items():
    print(f'  {provider}: {data[\"total_calls\"]} calls, {data[\"success_rate\"]}% success')
"
```

---

## §45 — Trend Intelligence System — Self-Learning Brain

### Overview

The **Trend Intelligence System** is the bot's "self-learning brain." It continuously gathers data from multiple online sources to determine:

1. **What topics are trending** — what to write about
2. **What writing styles perform best** — how to format articles
3. **What video formats get views** — how to structure Shorts
4. **What images have market demand** — what stock photos to generate

The system **learns from its own performance data** over time, adjusting recommendations based on what actually works.

### Data Sources

| Source | What It Provides | Update Frequency |
|--------|-----------------|------------------|
| **Google Trends** | Real-time trending topics per niche | Daily (6 AM) |
| **Google Suggest** | Autocomplete queries people are searching | Daily (6 AM) |
| **Reddit** | Hot posts from niche-specific subreddits | Daily (6 AM) |
| **HackerNews** | Top tech/startup stories | Daily (6 AM) |
| **Internal DB** | Style performance metrics (self-learning) | After each article |

### Writing Style Intelligence

The system recommends one of **7 article styles** based on topic analysis:

| Style | When It's Used | Example |
|-------|---------------|---------|
| **Listicle** | "best", "top", numbers in topic | "10 Best AI Tools for 2025" |
| **How-To** | "how to", "setup", "guide" | "How to Set Up a Smart Home" |
| **Comparison** | "vs", "compare", "alternative" | "ChatGPT vs Claude: Which Is Better?" |
| **Review** | "review", product names | "Notion AI Review: Worth It?" |
| **Problem-Solution** | "fix", "solve", "issue" | "Fix Slow WiFi in 5 Minutes" |
| **News/Trending** | breaking news, fresh trends | "Apple Just Launched Vision Pro 2" |
| **Beginner Guide** | "beginner", "start", "101" | "Investing 101: Where to Start" |

Each style has a **specialized LLM prompt** that shapes the article's structure, tone, and formatting.

### Video Format Intelligence

The system catalogs **7 trending video formats** for YouTube Shorts:

| Format | Duration | Description |
|--------|----------|-------------|
| **Quick Tips** | 15–30s | Rapid-fire numbered tips with text overlays |
| **Split Screen** | 30–45s | Before/after or side-by-side comparisons |
| **Hook → Story** | 45–60s | Controversial opening → explanation → CTA |
| **Tutorial Steps** | 30–45s | Numbered steps with progress bar |
| **Text Reveal** | 15–30s | Text appearing word-by-word over visuals |
| **POV Style** | 30–45s | First-person "when you discover…" framing |
| **Myth Bust** | 30–45s | "Most people think X… actually Y" format |

### Self-Learning Loop

```
Article Published → Track Views/Engagement → Record Style Performance
       ↑                                              ↓
       └──── Next Article Uses Best-Performing Style ←┘
```

The `style_intelligence` database table stores a **rolling average** effectiveness score for each writing style per niche. Over time, the bot naturally gravitates toward styles that generate the most engagement.

### Dashboard — Intelligence Page

Access at **Dashboard → 🧠 Intelligence** (`/intelligence`):

- **Metrics Bar** — cached topics, writing styles, video formats, last refresh time
- **Refresh Button** — force-refresh all intelligence data
- **Data Sources** — visual grid showing all 4 sources with status
- **Writing Style Table** — all 7 styles with patterns and best-for categories
- **Video Format Table** — all 7 formats with durations and descriptions
- **Style Performance** — self-learning data table (appears after articles are published)

### Database Schema

Table `trend_intelligence`:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| niche_id | TEXT | Associated niche |
| source | TEXT | "google_trends" / "reddit" / "hackernews" / "google_suggest" |
| topic | TEXT | Trending topic text |
| score | REAL | Relevance/trending score |
| url | TEXT | Source URL (if available) |
| fetched_at | TEXT | ISO timestamp |

Table `style_intelligence`:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| niche_id | TEXT | Associated niche |
| style_type | TEXT | "writing" or "video" |
| style_name | TEXT | e.g. "listicle", "quick_tips" |
| effectiveness | REAL | Rolling average score (0.0–1.0) |
| sample_count | INTEGER | Number of data points |
| updated_at | TEXT | Last update timestamp |

### File Structure

```
core/trend_intelligence.py       # Self-learning intelligence engine
```

### Configuration

No additional configuration needed — the trend intelligence system is built into the scheduler and runs automatically. It uses only free, public APIs (no keys required for Google Trends, Reddit, or HackerNews).

---

## §46 — Bot Modes — Paused, Scheduled & Manual

### Overview

The bot supports **3 operating modes** controllable from the dashboard:

| Mode | Icon | Behavior |
|------|------|----------|
| ⏸️ **Paused** | Yellow | Bot is running but **does nothing**. All scheduled jobs are skipped. Dashboard still accessible. |
| 📅 **Scheduled** | Green | **Normal operation.** Bot follows its configured schedule automatically. |
| 🎯 **Manual** | Blue | Bot only acts when you **manually trigger** tasks from the dashboard. |

### Switching Modes

From the **Dashboard home page**, click the mode buttons at the top:

```
┌──────────┐  ┌────────────┐  ┌──────────┐
│ ⏸️ Paused │  │ 📅 Schedule │  │ 🎯 Manual │
└──────────┘  └────────────┘  └──────────┘
```

The active mode is highlighted. Mode persists across bot restarts (stored in `bot_state.json`).

### Dependency-Aware Manual Pipeline

In **Manual mode**, the "Run All Pipeline" button executes tasks in the correct dependency order:

```
Step 1: 🧠 Refresh Trend Intelligence     (no dependencies)
Step 2: 📝 Generate & Publish Articles     (needs trends)
Step 3: 🎨 Generate Stock Images           (needs trends)
Step 4: 🎬 Generate YouTube Shorts         (needs articles)
Step 5: 🐦 Post to Twitter                 (needs articles + videos)
Step 6: 📌 Post to Pinterest               (needs articles)
```

Articles are **always generated before videos** because videos use article content as their script.

### Individual Manual Triggers

You can also trigger individual tasks from the dashboard. The manual trigger section lets you:

1. Select which niche to run
2. Choose which platforms to publish to (Blog, YouTube, Pinterest, Twitter)
3. Fire the task — it runs in the background

### How Mode Checking Works

Every scheduled job calls `bot_state.should_execute_scheduled_job()` before doing any work:

- **Paused** → returns `False` → job logs "Bot is paused, skipping" and exits
- **Scheduled** → returns `True` → job runs normally
- **Manual** → returns `False` → job skips (waits for manual trigger)

Manual triggers bypass the mode check — they always execute regardless of current mode.

### Bot State File

The mode is stored in `data/bot_state.json`:

```json
{
  "bot_mode": "scheduled",
  "platforms": {
    "blog": true,
    "youtube": true,
    "pinterest": true,
    "twitter": true
  }
}
```

---

## §47 — Twitter/X Auto-Posting for Articles & Videos

### Overview

The bot now **automatically tweets** when new content is created:

1. **Article tweets** — posted 30 minutes after each article is published
2. **Video tweets** — posted immediately after each YouTube Short is generated

### What Gets Tweeted

#### Article Tweet Format
```
📝 New article: {Article Title}

{First 200 chars of article}...

Read more: {article_url}

#niche #hashtags
```

#### Video Tweet Format
```
🎬 New video: {Video Title}

Watch: {youtube_url}

#niche #hashtags
```

### Schedule

| Event | Timing |
|-------|--------|
| Article tweet | 30 min after article published |
| Video tweet | Immediately after Short generated |

### Configuration

Twitter credentials in `config/settings.yaml`:

```yaml
social:
  twitter:
    api_key: "your_api_key"
    api_secret: "your_api_secret"
    access_token: "your_access_token"
    access_token_secret: "your_access_token_secret"
    bearer_token: "your_bearer_token"
```

If any Twitter credential is empty, the bot skips Twitter posting automatically — no errors.

### Dashboard Integration

- **Twitter platform pill** on dashboard home page (🐦 icon)
- **Twitter checkbox** in manual trigger section
- Twitter posting included in "Run All Pipeline" dependency chain

### Social Media Posting — Empty Credential Handling

If any social platform (Instagram, TikTok, Twitter) has **empty API credentials** in `settings.yaml`, the bot will **skip posting** to that platform automatically — no errors, no crashes. Only platforms with valid, non-empty credentials will be used.

---

## §48 — Stock Platform Submission System

### Overview

The bot generates AI images using the Multi-API Cascade (Leonardo → Stability → HuggingFace). These images can be sold on stock photography platforms. **No stock platform offers a contributor upload API** — all submissions are done through each platform's web portal. The bot prepares your images with **platform-optimized metadata** (titles, descriptions, keywords, categories) for fast batch uploading.

**File:** `core/stock_submitter.py`

### Platforms That Accept AI-Generated Content

| Platform | Commission | Max Keywords | Max Title | Signup URL |
|---|---|---|---|---|
| **Wirestock** | Varies (distributes to 6+) | 50 | 200 chars | contributor.wirestock.io |
| **Adobe Stock** | 33% | 25 | 70 chars | contributor.stock.adobe.com |
| **Shutterstock** | 15–40% | 50 | 200 chars | submit.shutterstock.com |
| **Freepik** | Up to 50% | 50 | 100 chars | contributor.freepik.com |
| **Dreamstime** | 25–60% | 50 | 100 chars | dreamstime.com/sell |
| **Pond5** | 50–60% | 50 | 100 chars | pond5.com/sell |
| **Depositphotos** | 34–42% | 50 | 200 chars | depositphotos.com/sell |
| **123RF** | 30–60% | 25 | 120 chars | 123rf.com/contributors |

### Platforms That BAN AI Content

- ❌ **Alamy** — Strictly bans all AI-generated imagery
- ❌ **iStock / Getty Images** — Prohibits AI content
- ❌ **Stocksy** — No AI-generated work accepted

### How It Works

1. **Generate** — Bot creates images via Leonardo/Stability/HuggingFace
2. **Export** — Click "Export for Stock Platforms" on dashboard or run via pipeline
3. **Metadata** — Bot creates a JSON sidecar per platform with optimized title, description, keywords, category
4. **Upload** — You upload manually via each platform's web portal using the prepared metadata
5. **Track** — Mark images as submitted/approved/rejected/sold in the dashboard

### Export Directory Structure

```
data/stock_exports/
├── wirestock/
│   ├── img_001.jpg
│   ├── img_001_metadata.json
├── adobe_stock/
│   ├── img_001.jpg
│   ├── img_001_metadata.json
├── shutterstock/
│   └── ...
```

### Metadata JSON Example

```json
{
  "platform": "adobe_stock",
  "title": "AI-Powered Productivity Dashboard 2025",
  "description": "AI-generated digital illustration of a modern productivity dashboard...",
  "keywords": ["ai generated", "productivity", "dashboard", "technology", ...],
  "category": "Technology",
  "ai_generated": true,
  "original_file": "data/stock_images/img_001.jpg"
}
```

### Dashboard Integration

- **Stock Images** page → "Export for Stock Platforms" button
- **Platform Submission Tracker** — per-platform stats (exported/submitted/approved/rejected/sales/earnings)
- **Platform Setup Guide** — direct signup links for each platform
- **Full pipeline** auto-exports after image generation

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/stock-images/export` | POST | Export all unsubmitted images |
| `/api/stock-images/<id>/submit` | POST | Mark image as submitted to platform |
| `/api/stock-images/<id>/sale` | POST | Record a sale |
| `/api/stock-images/submission-stats` | GET | Get per-platform stats |
| `/api/stock-images/platforms` | GET | Get platform info |

---

## §49 — Real Income Tracking

### Overview

The dashboard tracks **real income only** — no estimated or fake numbers. Revenue from all monetization sources is tracked in a central `income_entries` database table.

**File:** `core/income_tracker.py`

### Revenue Sources

| Source | Icon | Auto-Sync | How to Track |
|---|---|---|---|
| **Google AdSense** | 📊 | ❌ Manual | Login to AdSense → Reports → Enter monthly earnings |
| **Amazon Associates** | 🛒 | ❌ Manual | Login to Amazon Associates → Reports → Enter commission |
| **Stock Photos** | 📸 | ✅ Auto | Sales recorded via dashboard auto-sync from stock_submissions |
| **YouTube** | ▶️ | ❌ Manual | YouTube Studio → Analytics → Revenue (requires monetization) |
| **Other Affiliates** | 🤝 | ❌ Manual | CJ, ShareASale, etc. — enter from their dashboards |

### Why Not Fully Automated?

- **AdSense API** requires a verified, monetized publisher account
- **Amazon Associates API** provides product data only, not commission reports
- **YouTube Revenue API** requires YouTube Partner Program (1000 subs + 4000 watch hours)
- **Stock platforms** have no reporting API — only web portal dashboards
- **Stock photo sales** ARE auto-synced because we track them in our own database

### Dashboard Income Page

Navigate to **💰 Income** in the sidebar to:

1. View total all-time income (big green number)
2. See revenue breakdown by source (5 cards)
3. Add income entries (source, amount, niche, period, description)
4. Delete incorrect entries
5. See a guide for tracking each revenue source

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/income` | GET | Income tracker page |
| `/api/income/add` | POST | Add income entry |
| `/api/income/<id>/delete` | POST | Delete income entry |
| `/api/income/summary` | GET | Full income summary JSON |
| `/api/income/sync-stock` | POST | Sync stock photo earnings |

### Important Changes from Previous Versions

- **Removed fake income estimates** — `publisher.py` no longer calculates `estimated_income` from word count
- **Dashboard shows $0.00** until you add real earnings
- **Analytics page** shows real per-source income cards
- **"Total Income"** replaces "Est. Monthly Income" on the home dashboard

---

## §50 — Affiliate Click Tracking

### Overview

Every article on the published website now tracks outbound affiliate link clicks client-side.

### How It Works

1. JavaScript in `site/templates/post.html` intercepts clicks on:
   - All links with `rel="nofollow"` attribute
   - Known affiliate domains: amazon.com, amzn.to, shareasale.com, anrdoezrs.net, tkqlhce.com, dpbolvw.net, jdoqocy.com, kqzyfj.com
2. Sends a tracking ping via `navigator.sendBeacon` to `/track` endpoint
3. Falls back to Image pixel if sendBeacon unavailable
4. Passes `slug` (article identifier) and `niche` for per-article analytics

### What This Enables

- Know which articles drive the most affiliate clicks
- Know which niches convert best
- Track which affiliate programs get the most outbound traffic
- Use data to optimize article placement and affiliate link strategy

---

## §51 — Video Intelligence: Short-Form vs Landscape

### Overview

The trend intelligence system now differentiates between **short-form vertical videos** (Shorts/Reels/TikTok) and **landscape horizontal videos** (YouTube long-form). Each format pool has separate recommendation logic.

**File:** `core/trend_intelligence.py`

### Short-Form Formats (9:16 Vertical, ≤60 seconds)

| Format | Duration | Best For |
|---|---|---|
| ⚡ Quick Tips | 30–60s | Tips, tools, quick fixes, lists |
| 🔀 Split Screen | 30–60s | Comparisons, vs, before/after |
| 🪝 Hook + Story | 45–90s | Storytelling, surprising facts, mistakes |
| 📐 Tutorial Steps | 30–60s | How-to, step-by-step, guides |
| ✨ Text Reveal | 15–30s | Facts, secrets, ASMR-style reveals |
| 👁️ POV Style | 15–45s | First-person, day-in-the-life |
| 🔍 Myth Busting | 30–60s | Myths, misconceptions, debunking |

### Landscape Formats (16:9 Horizontal, 5–20 minutes)

| Format | Duration | Best For |
|---|---|---|
| 🔬 Deep Dive | 10–20 min | Complex topics, analysis, research |
| 📋 Top List | 8–15 min | Rankings, best-of, recommendations |
| 🎓 Tutorial | 10–20 min | Full walkthroughs, how-to, setup |
| ⚖️ Comparison Review | 8–15 min | Product comparisons, vs, reviews |
| 📰 News Roundup | 5–10 min | Weekly updates, news, announcements |
| 📖 Story Documentary | 10–20 min | Narratives, history, stories |

### Smart Format Selection

The `get_recommended_video_format(niche_id, topic, video_type="short")` function:

1. Accepts `video_type` parameter: `"short"` or `"landscape"`
2. Selects only from the matching format pool
3. Scores each format by matching topic keywords against `best_for` lists
4. Returns the best-matching format with all metadata (aspect ratio, duration, etc.)

### Intelligence Dashboard

The **🧠 Intelligence** page now shows two separate tables:
- **📱 Short-Form Video Formats** — 7 vertical formats
- **🖥️ Landscape Video Formats** — 6 horizontal formats

---

*Manual Version 3.0 — June 2025*
*For the latest updates, check the repository README.*
