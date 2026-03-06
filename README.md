# 🤖 AI Content Generator Bot

> **Fully automated, self-hosted passive income system — writes SEO articles, creates YouTube videos, posts to Pinterest, and earns from ads + 4 affiliate networks. Runs 24/7 for ~$9/year (just a domain name).**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](README.md)

---

## ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot

# 2. Setup (Windows)
python scripts/setup.py

# 3. Setup (macOS/Linux)
python3 scripts/setup.py

# 4. Start
python scripts/start_bot.py
```

Dashboard → **http://localhost:5000**

---

## 💰 What This Makes You

| Revenue Stream | How | Est. Monthly (Year 1) |
|---|---|---|
| Google AdSense | Ads on every article | $5–$50 |
| Amazon Associates | Product links in articles | $10–$100 |
| ShareASale | Niche affiliate programs | $10–$80 |
| CJ Affiliate | Brand affiliate programs | $5–$50 |
| YouTube Ads | Auto-generated video channel | $0–$50 (after 12 mo) |
| Pinterest | Drives extra traffic to site | (traffic amplifier) |
| **Total Year 1** | | **$30–$330/mo** |
| **Total Year 2** | | **$300–$1,500/mo** |

---

## 💵 Complete Cost Breakdown

| Item | Cost | Notes |
|---|---|---|
| Domain name | ~$9/year | Only real cost. Use Namecheap or Cloudflare. |
| Hosting (GitHub Pages) | **FREE** | Unlimited static hosting |
| Hosting (Netlify) | **FREE** | 100 GB/month bandwidth |
| Hosting (Cloudflare Pages) | **FREE** | Unlimited requests |
| Ollama (AI writer) | **FREE** | Runs locally on your machine |
| Mistral AI model | **FREE** | Downloaded once by Ollama |
| Google Trends (pytrends) | **FREE** | No API key needed |
| AdSense | **FREE** | Google pays you |
| Amazon Associates | **FREE** | Amazon pays you |
| ShareASale | **FREE** | Merchants pay you |
| CJ Affiliate | **FREE** | Brands pay you |
| YouTube API | **FREE** | 10,000 units/day quota |
| Pinterest API | **FREE** | Free developer account |
| Flask dashboard | **FREE** | Runs on your machine |
| SQLite database | **FREE** | Built into Python |
| **TOTAL** | **~$9/year** | |

> **One domain covers all 5 niches.** You do NOT need separate domains per niche or per AdSense ad unit. Use `yourdomain.com/travel/`, `yourdomain.com/health/`, etc. A single AdSense account with one domain approval covers the entire site.

---

## 📅 Income Timeline (Realistic)

| Period | Est. Monthly Income | Why |
|---|---|---|
| Month 1–3 | $0 | AdSense pending approval, no traffic yet |
| Month 4–6 | $5–$50 | AdSense approved, early organic traffic |
| Month 7–12 | $60–$400 | SEO gains traction, affiliate conversions |
| Year 2 | $300–$1,500 | Compounding content, YouTube growing |

---

## 🤖 What the Bot Does Automatically

Every single day, without you doing anything:

| Time | Action |
|---|---|
| 8:00 AM | Fetch trending Google topics for all 5 niches |
| 9:00 AM | Write + publish AI Tools article |
| 9:15 AM | Write + publish Personal Finance article |
| 9:30 AM | Write + publish Health/Biohacking article |
| 9:45 AM | Write + publish Home Tech article |
| 9:50 AM | Write + publish Travel article |
| 11:00 AM | Generate + upload YouTube video (AI Tools) |
| 11:15 AM | Generate + upload YouTube video (Finance) |
| 11:30 AM | Generate + upload YouTube video (Health) |
| 11:45 AM | Generate + upload YouTube video (Home Tech) |
| 11:50 AM | Generate + upload YouTube video (Travel) |
| 12:00 PM | Post to Pinterest (AI Tools) |
| 12:15 PM | Post to Pinterest (Finance) |
| 12:30 PM | Post to Pinterest (Health) |
| 12:45 PM | Post to Pinterest (Home Tech) |
| 12:50 PM | Post to Pinterest (Travel) |
| Every hour | Income snapshot saved to database |
| Sunday midnight | Full site rebuild |

---

## 🏷️ 5 Niches (One Domain, All Paths)

1. **AI Tools & SaaS** → `yourdomain.com/ai_tools/`
2. **Personal Finance & Investing** → `yourdomain.com/personal_finance/`
3. **Health & Biohacking** → `yourdomain.com/health_biohacking/`
4. **Home Tech & Smart Devices** → `yourdomain.com/home_tech/`
5. **Travel** → `yourdomain.com/travel/`

> ✅ AdSense approves **your domain once** — all paths are covered automatically.

---

## 💡 6 Revenue Streams Explained

### 1. Google AdSense
Paste one code snippet into `site/templates/post.html` and `site/templates/index.html`. Ads auto-appear on every article. Earn $1–$5 per 1,000 page views.

### 2. Amazon Associates
Sign up at [affiliate-program.amazon.com](https://affiliate-program.amazon.com). Add your tag to `.env` as `AMAZON_AFFILIATE_TAG`. The bot auto-embeds product links into every article matching product keywords.

### 3. ShareASale
Sign up at [shareasale.com](https://www.shareasale.com). Add `SHAREASALE_AFFILIATE_ID` to `.env`. Paste program-specific URLs into `config/niches.yaml`. Earn 5–20% commissions.

### 4. CJ Affiliate (Commission Junction)
Sign up at [cj.com](https://www.cj.com). Add `CJ_AFFILIATE_ID` to `.env`. Paste deep links into `config/niches.yaml`. Earn per-sale commissions from major brands.

### 5. YouTube
The bot extracts key points from every article, generates text-to-speech audio with gTTS, builds slides with Pillow, and exports a 1280×720 MP4. It then uploads to YouTube via the Data API v3. After 1,000 subscribers + 4,000 watch hours, you qualify for YouTube Partner Program ads.

### 6. Pinterest
The bot auto-creates a 1000×1500 pin image using Pillow, uploads it to Pinterest via API v5, and links back to the published article. Pinterest drives organic traffic to your site for free, boosting all other revenue streams.

---

## 📋 Prerequisites

- Python 3.10 or higher
- Git
- [Ollama](https://ollama.ai) (free local AI)
- A domain name (~$9/year) — for AdSense approval and hosting

---

## 🛠️ Installation

### Windows

```powershell
# Install Python 3.10+ from python.org, then:
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
python scripts/setup.py
copy .env.example .env
# Edit .env with your settings
python scripts/start_bot.py
```

### macOS

```bash
# Install Python 3.10+ via brew if needed: brew install python@3.12
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
python3 scripts/setup.py
cp .env.example .env
# Edit .env with your settings
python3 scripts/start_bot.py
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv git
git clone https://github.com/bbet-sudo/content-generator-bot.git
cd content-generator-bot
python3 scripts/setup.py
cp .env.example .env
# Edit .env with your settings
python3 scripts/start_bot.py
```

---

## 🦙 Ollama Setup

Ollama runs the Mistral AI model locally — 100% free, no API keys needed.

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral

# Windows: download installer from https://ollama.ai/download
# After install:
ollama pull mistral
```

Test it works: `ollama run mistral "Hello"`

---

## 🔗 Affiliate Program Signups

| Program | Sign Up URL | What to Add to .env |
|---|---|---|
| Amazon Associates | https://affiliate-program.amazon.com | `AMAZON_AFFILIATE_TAG=yourtag-20` |
| ShareASale | https://www.shareasale.com/info/join | `SHAREASALE_AFFILIATE_ID=123456` |
| CJ Affiliate | https://signup.cj.com | `CJ_AFFILIATE_ID=your_id` |

After signing up, also update the `url` fields in `config/niches.yaml` with your personal affiliate deep links.

---

## 📺 YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (e.g., "ContentBot")
3. Enable **YouTube Data API v3**
4. Go to **Credentials** → Create **OAuth 2.0 Client ID** (Desktop app)
5. Download the JSON file → save as `client_secrets.json` in the project root
6. Set `YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json` in `.env`
7. First run: a browser window opens for one-time OAuth authorization

> **Quota**: YouTube gives 10,000 units/day free. Each upload = ~1,600 units. You get ~6 uploads/day free.

---

## 📌 Pinterest API Setup

1. Create a [Pinterest Business Account](https://business.pinterest.com)
2. Go to [Pinterest Developers](https://developers.pinterest.com)
3. Create a new app → request `pins:read_write` and `boards:read` scopes
4. Generate an Access Token
5. Get your Board ID from the board URL (the number in `pinterest.com/yourusername/board-name/`)
6. Set in `.env`:
   ```
   PINTEREST_ACCESS_TOKEN=your_token_here
   PINTEREST_BOARD_ID=1234567890
   ```

---

## 📢 AdSense Setup

1. Sign up at [google.com/adsense](https://www.google.com/adsense)
2. Add your domain (e.g., `yourdomain.com`) — **ONE domain covers all 5 niches**
3. Paste the AdSense verification snippet into `site/templates/post.html` and `site/templates/index.html` inside `<head>`
4. Deploy your site (see Hosting section below)
5. Wait 1–14 days for approval

```html
<!-- Paste your AdSense code here, inside <head> in post.html and index.html -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
     crossorigin="anonymous"></script>
```

AdSense auto-places ads — you don't need to add individual ad units (use Auto Ads).

---

## 🌐 Hosting Your Site Free

### GitHub Pages (Recommended)
```bash
# Push site/output/ to gh-pages branch
git subtree push --prefix site/output origin gh-pages
# Set custom domain in repo Settings → Pages
```

### Netlify
```bash
# Install netlify-cli or drag-and-drop site/output/ at netlify.com
npm install -g netlify-cli
netlify deploy --prod --dir site/output
```

### Cloudflare Pages
1. Go to [pages.cloudflare.com](https://pages.cloudflare.com)
2. Connect GitHub repo
3. Set build output directory to `site/output`
4. Set custom domain in Cloudflare DNS

---

## ▶️ Starting and Stopping the Bot

```bash
# Start everything (bot + dashboard)
python scripts/start_bot.py

# Start dashboard only
python scripts/start_dashboard.py

# Run one test cycle manually
python scripts/test_run.py

# Stop
# Press Ctrl+C in the terminal
```

---

## 📊 Dashboard Usage

Open **http://localhost:5000** in your browser.

| Page | URL | What it shows |
|---|---|---|
| Overview | `/` | Total posts, estimated income, recent activity |
| Posts | `/posts` | All published articles, searchable |
| Analytics | `/analytics` | Charts by niche, clicks, income |
| Logs | `/logs` | Live-updating bot activity log |
| Niches | `/niches` | Configuration cards for all 5 niches |

---

## 🧪 Running Tests

```bash
# Run all unit tests
make unittest
# or
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```
content-generator-bot/
├── core/                    # Bot engine modules
│   ├── llm_writer.py        # Ollama article generator
│   ├── trend_finder.py      # Google Trends topic finder
│   ├── affiliate_injector.py # Affiliate link injector
│   ├── seo_optimizer.py     # Meta tags, schema, sitemap
│   ├── publisher.py         # Static HTML publisher
│   ├── video_generator.py   # YouTube video creator
│   ├── youtube_uploader.py  # YouTube uploader
│   ├── pinterest_poster.py  # Pinterest pin creator
│   ├── scheduler.py         # APScheduler jobs
│   └── analytics_tracker.py # SQLite analytics
├── dashboard/               # Flask web dashboard
│   ├── app.py
│   ├── templates/
│   └── static/
├── site/                    # Static site output
│   ├── templates/
│   └── output/              # Generated HTML files
├── config/
│   ├── niches.yaml          # All 5 niches configuration
│   └── settings.yaml        # Site and bot settings
├── scripts/
│   ├── setup.py             # First-time setup
│   ├── start_bot.py         # Start bot + dashboard
│   ├── start_dashboard.py   # Start dashboard only
│   └── test_run.py          # Manual test cycle
├── tests/                   # Unit tests
├── data/                    # SQLite database + logs
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── Makefile                 # Common commands
└── OPERATIONS_MANUAL.md     # Complete operations guide
```

---

## 🤝 Contributing

Pull requests welcome. Please run `make unittest` before submitting.

---

## ⚖️ Legal

- All generated content must comply with AdSense policies and FTC disclosure requirements
- Affiliate links are automatically wrapped with `rel="nofollow sponsored"`
- FTC disclosure is auto-injected into every article
- See `OPERATIONS_MANUAL.md` → Section 25 for full legal & compliance guidance

---

## 📄 License

MIT — see [LICENSE](LICENSE)


```
08:00 AM  Fetches trending topics (Google Trends)
09:00 AM  Writes + publishes article — AI Tools niche
09:15 AM  Writes + publishes article — Finance niche
09:30 AM  Writes + publishes article — Health niche
09:45 AM  Writes + publishes article — Home Tech niche
10:00 AM  Writes + publishes article — Travel niche
11:00 AM  Creates + uploads YouTube video × 5 niches
01:00 PM  Posts Pinterest pins × 5 niches
Every hr  Updates income + analytics dashboard
Sunday    Rebuilds full site index + sitemap
```

**That's 5 articles + 5 videos + 5 Pinterest pins per day. $0 in AI costs.**

---

## 💸 Real Cost Breakdown

| Item | Cost |
|---|---|
| Python + all libraries | $0 |
| Ollama local AI (Mistral model) | $0 |
| GitHub + GitHub Pages hosting | $0 |
| All affiliate accounts | $0 |
| YouTube API | $0 |
| Pinterest API | $0 |
| **Custom domain (REQUIRED for AdSense)** | **~$9/year** |
| VPS for 24/7 running (optional) | $4–6/month |
| **Minimum total** | **$0.75/month** |

---

## 📚 Full Documentation

👉 **[Read the Complete Master Manual](MASTER_MANUAL.md)**

The manual covers everything:
- Step-by-step installation (Windows, macOS, Linux)
- Setting up all 6 revenue streams
- Domain setup + AdSense approval tips
- Startup and shutdown procedures
- Dashboard usage guide
- Hosting your site for free
- Troubleshooting + FAQ
- Legal compliance

---

## 📁 Project Structure

```
content-generator-bot/
├── core/                 ← Bot engine (AI writer, scheduler, video gen)
├── dashboard/            ← Flask monitoring web UI
├── site/                 ← Generated static website (deploy this)
├── config/               ← Edit niches.yaml to configure your affiliate links
├── scripts/              ← start_bot.py, setup.py, test_run.py
├── data/                 ← SQLite DB + logs (auto-created)
├── .env.example          ← Copy to .env and fill in your keys
├── requirements.txt      ← All dependencies
├── MASTER_MANUAL.md      ← Complete documentation
└── Makefile              ← make setup / make run / make dashboard
```

---

## 🌿 The 5 Niches

| Niche | Why | Est. Commission |
|---|---|---|
| 🤖 AI Tools & SaaS | 20–40% recurring | $15–$80/sale |
| 💵 Personal Finance | Highest commissions | $10–$150/lead |
| 💪 Health & Biohacking | Evergreen, high volume | $5–$40/sale |
| 🏠 Home Tech & Smart Devices | Amazon high-ticket | $5–$30/sale |
| ✈️ Travel | High-value bookings | $8–$60/booking |

---

## 🚀 After Setup Checklist

- [ ] Install Ollama → https://ollama.com/download
- [ ] Run `ollama pull mistral`
- [ ] Buy domain (~$9/yr) → https://namecheap.com
- [ ] Apply Amazon Associates → https://affiliate-program.amazon.com
- [ ] Apply ShareASale → https://shareasale.com
- [ ] Apply CJ Affiliate → https://cj.com
- [ ] Set up YouTube channel + API (see MASTER_MANUAL.md Section 19)
- [ ] Set up Pinterest Business account (see MASTER_MANUAL.md Section 20)
- [ ] Deploy site/output/ to GitHub Pages or Netlify (free)
- [ ] Apply for AdSense AFTER 20+ articles published

---

## 📊 Dashboard Preview

Open http://localhost:5000 while the bot is running to see:
- Real-time post count, video count, estimated income, click tracking
- Charts for posts over time and income trends
- Live bot activity logs (color-coded)
- Per-niche performance breakdown
- Full niche configuration viewer

---

*For complete setup instructions, revenue stream guides, startup/shutdown procedures, and troubleshooting — read [MASTER_MANUAL.md](MASTER_MANUAL.md)*