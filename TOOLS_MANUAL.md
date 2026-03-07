# 🛠️ Tools Manual — TechLife Insights

Everything you need to know about the 8 interactive tools on the site, how they work,
how to customize them, and how to set up affiliate monetization.

---

## Table of Contents

1. [Deal Finder](#1-deal-finder)
2. [Market Data Center](#2-market-data-center)
3. [Travel Search](#3-travel-search)
4. [Budget Calculator](#4-budget-calculator)
5. [AI Tool Directory](#5-ai-tool-directory)
6. [Workout Generator](#6-workout-generator)
7. [Pet Food Analyzer](#7-pet-food-analyzer)
8. [Smart Home Hub](#8-smart-home-hub)
9. [Affiliate Setup Guide](#9-affiliate-setup-guide)
10. [Regenerating Templates](#10-regenerating-templates)

---

## 1. Deal Finder

**URL:** `/tools/deal-finder.html`
**Template:** `site/templates/deal_finder.html`

### What It Does
- User types a product name (e.g., "wireless headphones")
- Shows a grid of 9 retailer cards, each pre-filled with the search query
- **Open All** button opens every retailer simultaneously in new tabs
- Recent searches saved to localStorage for quick re-access
- 12 popular category shortcuts for one-click searching

### Retailers (with search URL patterns)
| Retailer | Affiliate | Notes |
|----------|-----------|-------|
| Amazon | `tag=techlife0ac-20` | ✅ Active affiliate tag |
| Best Buy | None | Add via Impact |
| Walmart | None | Add via Impact |
| Target | None | Add via Impact |
| Newegg | None | Direct link |
| eBay | None | Add via eBay Partner Network |
| B&H Photo | None | Direct link |
| Costco | None | Direct link |
| Google Shopping | None | Meta-search (no affiliate) |

### How to Add a Retailer
In `scripts/rebuild_tools.py` → `deal_finder()` function, add to the `retailers` JS array:
```js
{name:'StoreName', icon:'🏪',
 search:'https://example.com/search?q=QUERY&affiliate=YOUR_ID',
 desc:'Description here'}
```
The `QUERY` placeholder gets replaced with the user's search term.

### Amazon Affiliate Tag
Currently set to `techlife0ac-20`. To change, find `tag=techlife0ac-20` in the
deal_finder template and replace with your Amazon Associates tag.

---

## 2. Market Data Center

**URL:** `/personal_finance/markets.html`
**Template:** `site/templates/market_data.html`

### What It Does
- **TradingView Ticker Tape** — real-time scrolling prices at the top (S&P 500, BTC, Gold, etc.)
- **Symbol Search** — type any symbol (AAPL, BTC, EUR/USD) and load an interactive chart
- **Quick Chips** — one-click buttons for popular symbols
- **TradingView Advanced Chart** — full interactive chart with:
  - Drawing tools, technical indicators, multiple timeframes
  - Built-in symbol search (click the symbol name in the chart)
  - Watchlist sidebar
- **TradingView Market Overview** — tabbed widget with Indices, Stocks, Crypto, Forex, Commodities
- **CoinGecko Live Crypto** — 10 major coins with price, 24h change, market cap (auto-refreshes every 60s)
- **Timestamp** — shows date AND time, updates every 60 seconds

### Data Sources & Refresh Rates
| Source | Data | Refresh |
|--------|------|---------|
| TradingView Ticker Tape | Indices, stocks, crypto, forex, commodities | Real-time (up to 15-min delay for equities) |
| TradingView Advanced Chart | Any searchable symbol | Real-time |
| TradingView Market Overview | Tabbed market categories | Real-time |
| CoinGecko API | Top 10 crypto prices | Every 60 seconds |

### Customizing Symbols
- **Ticker Tape symbols:** Edit the `symbols` array in the ticker tape `<script>` tag
- **Quick chips:** Edit the `QUICK` array in the JavaScript
- **Market Overview tabs:** Edit the `tabs` array in the Market Overview widget config
- **Crypto coins:** Edit `CRYPTO_IDS` in the JavaScript

### TradingView Widget Notes
- Widgets are **free** and require no API key
- Equities have up to 15-minute delay on the free tier
- Crypto is near real-time
- Widgets load their own CSS — no styling needed

---

## 3. Travel Search

**URL:** `/travel/search.html`
**Template:** `site/templates/travel_search.html`

### What It Does
- **3 Tabs:** Flights, Hotels, Cars
- **Smart Autocomplete** — 65+ major airports worldwide with IATA codes
  - Type a city name, airport name, or IATA code
  - Dropdown shows matching airports with code, city, and full name
  - Click to select
- **Multi-Provider Results** — when user searches, shows a grid of provider cards:
  - Each card is a deep link to the provider with all search params pre-filled
  - "Open All Providers" button opens all at once
- **Default dates** set to tomorrow and next week

### Flight Providers
| Provider | Deep Link Format | Affiliate |
|----------|-----------------|-----------|
| Google Flights | Natural language search URL | No affiliate program |
| Skyscanner | `/transport/flights/{FROM}/{TO}/{DATE}/` | Skyscanner Travel APIs |
| Kayak | `/flights/{FROM}-{TO}/{DATE}/{DATE}` | Kayak Affiliate |
| Momondo | `/flight-search/{FROM}-{TO}/{DATE}/{DATE}` | Same as Kayak |
| Kiwi.com | `/search/results/{FROM}/{TO}/{DATE}/{DATE}` | Kiwi Tequila API |

### Hotel Providers
| Provider | Affiliate |
|----------|-----------|
| Booking.com | Booking.com Affiliate Partner Centre |
| Hotels.com | Expedia Group affiliate |
| Agoda | Agoda Partner Program |
| Trivago | Trivago Affiliate |
| Hostelworld | Hostelworld Affiliate |

### Car Rental Providers
| Provider | Affiliate |
|----------|-----------|
| Kayak Cars | Kayak Affiliate |
| RentalCars.com | Booking Holdings affiliate |
| Discover Cars | DiscoverCars affiliate |
| AutoEurope | AutoEurope affiliate |

### Adding Airports
Edit the `AP` array in the JavaScript. Format:
```js
{c:'IATA', city:'City', n:'Full Airport Name', co:'Country Code'}
```

### Affiliate Integration
To add affiliate IDs to the deep links, find the URL construction in
`searchFlights()`, `searchHotels()`, or `searchCars()` and append your ID:
```js
// Example: Booking.com affiliate
url: 'https://www.booking.com/searchresults.html?aid=YOUR_AID&ss=...'
```

---

## 4. Budget Calculator

**URL:** `/tools/budget-calculator.html`
**Template:** `site/templates/budget_calculator.html`

### What It Does
- **4 Calculators** in tabbed view:
  1. **Monthly Budget** — income, needs, wants → 50/30/20 analysis with bar chart, surplus/deficit, smart insights
  2. **Debt Payoff** — balance, APR, monthly payment → payoff timeline, total interest, extra payment impact
  3. **Savings Goal** — goal, current savings, monthly contribution, expected return → timeline, growth projection
  4. **Emergency Fund** — essential expenses × target months → progress bar, timeline
- **Print/PDF Export** — print button hides nav/footer for clean printout
- **Visual Results** — bar charts, color-coded boxes, progress indicators

### Customization
Each calculator is a pure JavaScript function. Modify the `calc*()` functions
to change logic, formulas, or output formatting.

---

## 5. AI Tool Directory

**URL:** `/tools/ai-tool-finder.html`
**Template:** `site/templates/ai_tool_finder.html`

### What It Does
- **60+ AI tools** across 10 categories: Writing, Images, Video, Code, Voice, Productivity, Research, Marketing, Design
- **Category filters** — click to filter by category (uses event delegation, no onclick quoting bugs)
- **Search** — real-time text search across name, description, and category
- **Tool count** — shows "Showing X of Y tools"
- **Visit buttons** — direct links to each tool's website

### Adding New Tools
Edit the `aiTools` array in the JavaScript:
```js
{name:'Tool Name', cat:'Category', desc:'Description', pricing:'Free / $X/mo', url:'https://...'}
```

### Monetization
Some AI tools have affiliate programs. Replace the `url` field with your
affiliate link for tools like Jasper, SurferSEO, Semrush, etc.

---

## 6. Workout Generator

**URL:** `/tools/workout-generator.html`
**Template:** `site/templates/workout_generator.html`

### What It Does
- **4 Selection Steps:** Goal, Equipment, Time, Level
- **Visual Validation** — unselected categories highlight in red with border when user clicks Generate
- **Smart Exercise Selection** — draws from categorized pools:
  - Bodyweight (no equipment), Dumbbells, Home Gym, Full Gym
  - Warmup, Strength, Cardio, Flexibility pools
- **Generated Workout:**
  - Warm-up → Main exercises → Cool-down
  - Sets, reps, rest periods adjusted by goal and level
  - Printable layout
- **Randomized** — each generation produces a different workout

### Exercise Database
Edit the `EX` object in the JavaScript to add/remove exercises per equipment type and category.

---

## 7. Pet Food Analyzer

**URL:** `/tools/pet-food-checker.html`
**Template:** `site/templates/pet_food_checker.html`

### What It Does
- User selects **Dog** or **Cat**
- Pastes the ingredient list from pet food packaging
- **Analyzes each ingredient** against 3 databases:
  - ✅ Good ingredients (quality proteins, whole foods, supplements)
  - ⚠️ Acceptable ingredients (common fillers, supplements)
  - ❌ Concerning ingredients (by-products, artificial colors, preservatives)
- **Quality Score** — 0-100 based on ingredient ratings
- **Color-coded breakdown** — each ingredient tagged green/yellow/red
- **Smart Tips** — personalized based on analysis results

### Ingredient Databases
Edit the `goodIng`, `okIng`, and `badIng` arrays in the JavaScript.
The `goodIng` object has separate lists for dogs and cats.

### Fixes Applied
- **Split regex** — properly handles comma, semicolon, and newline-separated ingredients
- **Event handling** — analyze button works reliably on all browsers

---

## 8. Smart Home Hub

**URL:** `/tools/smart-home.html`
**Template:** `site/templates/smart_home.html`

### What It Does
- **31 devices** across 10 categories: Speaker, Lighting, Security, Climate, Locks, Cleaning, Plugs, Hubs, Display, Switches
- **Ecosystem filter** — filter by All, Alexa, Google, HomeKit, or Matter compatible
- **Category filter** — filter by device type (uses event delegation, no onclick quoting bugs)
- **Search** — text search across device names, descriptions, categories
- **Compatibility badges** — ✓/✗ for Alexa, Google, HomeKit, Matter
- **Price display** — estimated retail price
- **Amazon buy links** — each device links to Amazon search with affiliate tag `techlife0ac-20`

### Adding Devices
Edit the `devices` array in the JavaScript:
```js
{name:'Device Name', cat:'Category', alexa:1, google:1, homekit:0, matter:0,
 price:'$99', desc:'Description'}
```
Values: `1` = compatible, `0` = not compatible.

### Fixes Applied
- **Onclick quoting bug** — fixed by using `addEventListener()` + `event delegation` instead of inline `onclick` with problematic quote escaping

---

## 9. Affiliate Setup Guide

### Amazon Associates
1. Sign up at [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
2. Get your Associate Tag (currently `techlife0ac-20`)
3. Used in: Deal Finder, Smart Home Hub buy links
4. To change tag, edit `rebuild_tools.py` and search for `techlife0ac-20`

### Skyscanner Travel APIs
1. Apply at [partners.skyscanner.net](https://partners.skyscanner.net)
2. Get your affiliate ID
3. Append to Skyscanner URLs: `&associate=YOUR_ID`

### Booking.com Affiliate Partner Centre
1. Sign up at [www.booking.com/affiliate-program](https://www.booking.com/affiliate-program/v2/index.html)
2. Get your `aid` parameter
3. Add to Booking.com URLs: `?aid=YOUR_AID&...`

### Kayak Affiliate
1. Apply through Impact or CJ Affiliate
2. Use their link generator or append tracking parameters

### Kiwi.com Tequila API
1. Register at [tequila.kiwi.com](https://tequila.kiwi.com)
2. Get your API key for server-side integration (optional)
3. For deep links, use partner ID in the URL

### AI Tool Affiliates
Many AI tools have affiliate programs. Check:
- **Jasper** — partner program
- **SurferSEO** — affiliate via Impact
- **Semrush** — Semrush affiliate program (generous commissions)
- **Copy.ai** — partner program
- **ElevenLabs** — referral program

### Kit Newsletter
Currently configured: `https://techlife-insights.kit.com/be266c00d5`
The floating subscribe button appears on every tool page.

---

## 10. Regenerating Templates

### Full Rebuild
```bash
# 1. Regenerate all tool templates
python scripts/rebuild_tools.py

# 2. Rebuild the static site (renders templates → output HTML)
python -c "
from core import publisher
import yaml
from pathlib import Path
s = yaml.safe_load(Path('config/settings.yaml').read_text())
publisher.rebuild_site(s, Path('data/bot.db'), s.get('site_url', ''))
"

# 3. Commit and push
git add -A && git commit -m "rebuild tools" && git push origin main
```

### Template Architecture
```
site/templates/           ← Jinja2 templates (source of truth)
  ├── market_data.html    → /personal_finance/markets.html
  ├── travel_search.html  → /travel/search.html
  ├── deal_finder.html    → /tools/deal-finder.html
  ├── ai_tool_finder.html → /tools/ai-tool-finder.html
  ├── budget_calculator.html → /tools/budget-calculator.html
  ├── workout_generator.html → /tools/workout-generator.html
  ├── pet_food_checker.html → /tools/pet-food-checker.html
  ├── smart_home.html     → /tools/smart-home.html
  └── tools_index.html    → /tools/index.html

scripts/rebuild_tools.py  ← Python script that generates all templates
core/publisher.py         ← Renders templates → site/output/
```

### Publisher Mapping
The publisher's `_rebuild_tools_pages()` maps templates to output:
- `tools_index.html` → `site/output/tools/index.html`
- `deal_finder.html` → `site/output/tools/deal-finder.html`
- `ai_tool_finder.html` → `site/output/tools/ai-tool-finder.html`
- etc.

The `_rebuild_travel_search()` and `_rebuild_market_data()` handle those two
separately since they're in niche-specific directories.

---

## Common Issues

### Tools not working after deploy
Run `python scripts/rebuild_tools.py` then `rebuild_site()`. The generator
overwrites template files; the publisher renders them to output.

### Category filters not clicking
**Fixed.** Previously, inline `onclick="fn(''+c+'')"` had a quoting bug.
Now all templates use `addEventListener()` + event delegation instead.

### Pet food analyzer not analyzing
**Fixed.** The split regex used a literal newline character. Now uses proper
`/,|;|\n/` regex pattern.

### TradingView widgets not loading
- Check for ad blockers — some block TradingView scripts
- Widgets need HTTPS
- Each widget loads ~200KB of JavaScript; slow connections may delay rendering

### Travel autocomplete not showing
- Type at least 2 characters
- Click outside the dropdown to dismiss
- Dropdown uses `position: absolute` — check for CSS overflow conflicts
