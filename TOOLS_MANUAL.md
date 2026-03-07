# 🛠️ Tools Manual — TechLife Insights

> **Comprehensive reference** for all interactive tools on the site.
> Covers architecture, code components, data sources, affiliate/monetization
> setup, maintenance procedures, and troubleshooting.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Deal Finder](#2-deal-finder)
3. [Travel Search](#3-travel-search)
4. [AI Tool Directory](#4-ai-tool-directory)
5. [Budget Calculator](#5-budget-calculator)
6. [Workout Generator](#6-workout-generator)
7. [Pet Food Analyzer](#7-pet-food-analyzer)
8. [Smart Home Hub](#8-smart-home-hub)
9. [Market Data Center](#9-market-data-center)
10. [Affiliate & Monetization Setup](#10-affiliate--monetization-setup)
11. [Adding a New Tool](#11-adding-a-new-tool)
12. [Testing & Deployment](#12-testing--deployment)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Architecture Overview

### 1.1 Rendering Pipeline

```
config/settings.yaml          ← Central config (site info, affiliate IDs, etc.)
config/niches.yaml             ← Navigation data (niche names, subtopics)
        │
        ▼
core/publisher.py              ← Python Jinja2 renderer
        │
        ├─ _rebuild_tools_pages()   → reads site/templates/*.html
        ├─ _rebuild_travel_search() → reads site/templates/travel_search.html
        └─ _rebuild_market_data()   → reads site/templates/market_data.html
        │
        ▼
site/output/tools/*.html       ← Static HTML files served to users
site/output/travel/search.html
site/output/personal_finance/markets.html
```

**Key function:** `core/publisher.py :: _rebuild_tools_pages()`

This function:
1. Loads all tool templates from `site/templates/`
2. Passes these Jinja2 context variables to each template:
   - `niches` — navigation data from `config/niches.yaml`
   - `settings` — full `config/settings.yaml` dict
   - `affiliates` — shortcut to `settings['affiliates']` dict
   - `site_url`, `site_title`, `tagline`
3. Writes rendered HTML to `site/output/tools/`

The template-to-output filename mapping:

| Template File | Output File |
|---------------|-------------|
| `deal_finder.html` | `tools/deal-finder.html` |
| `ai_tool_finder.html` | `tools/ai-tool-finder.html` |
| `budget_calculator.html` | `tools/budget-calculator.html` |
| `workout_generator.html` | `tools/workout-generator.html` |
| `pet_food_checker.html` | `tools/pet-food-checker.html` |
| `smart_home.html` | `tools/smart-home.html` |
| `travel_search.html` | `travel/search.html` |
| `market_data.html` | `personal_finance/markets.html` |
| `tools_index.html` | `tools/index.html` |

### 1.2 How Affiliate IDs Flow

```
config/settings.yaml            Jinja2 Template (HTML)              Browser (JS)
────────────────────          ─────────────────────────          ──────────────────
affiliates:                   {{ affiliates.amazon_tag }}        var AFF = {
  amazon_tag: "techlife0ac-20"  ──renders to──►                   amazon: 'techlife0ac-20'
  booking_aid: ""             {{ affiliates.booking_aid }}        };
  jasper_fpr: "abc123"          ──renders to──►                   // Empty string = no tracking
                                                                  // Non-empty = append to URL
```

At build time, Jinja2 replaces `{{ affiliates.KEY | default("") }}` with the
value from `settings.yaml`. If the value is blank, the JS helper functions
(e.g., `affUrl()`, `aitAff()`) detect the empty string and return the plain
URL without any tracking parameters.

### 1.3 Database

The tools themselves do **not** use any database. All tool data (exercises,
ingredients, AI tools, device lists, airport codes) is **hardcoded inside
the HTML template** as JavaScript arrays/objects. This is intentional:

- **Zero latency** — no API calls, no server needed
- **Works on static hosting** — Cloudflare Pages, GitHub Pages, Netlify
- **No CORS issues** — everything is same-origin
- **No API key exposure** — all data is baked in at build time

The only database in the project is `data/bot.db` (SQLite), which stores
published articles and analytics — it has nothing to do with the tools.

### 1.4 File Structure

```
site/
├── templates/                    ← Jinja2 source templates
│   ├── deal_finder.html          ← Tool templates
│   ├── travel_search.html
│   ├── ai_tool_finder.html
│   ├── budget_calculator.html
│   ├── workout_generator.html
│   ├── pet_food_checker.html
│   ├── smart_home.html
│   ├── market_data.html
│   ├── tools_index.html          ← /tools/ landing page
│   ├── index.html                ← Site homepage
│   └── post.html                 ← Blog post template
├── output/                       ← Rendered static HTML (git-tracked)
│   ├── tools/
│   │   ├── deal-finder.html
│   │   ├── ai-tool-finder.html
│   │   └── ...
│   ├── travel/
│   │   └── search.html
│   └── personal_finance/
│       └── markets.html
config/
├── settings.yaml                 ← All config including affiliate IDs
└── niches.yaml                   ← Navigation structure
core/
└── publisher.py                  ← Jinja2 rendering engine
```

### 1.5 Common Template Anatomy

Every tool template follows the same structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Meta tags, title, favicon -->
  <style>
    /* Self-contained CSS — no external stylesheets except Google Fonts */
    /* Each tool has its own accent color (--accent) */
  </style>
</head>
<body>
  <!-- Sticky header with logo + dynamic navigation from niches.yaml -->
  <header class="header">
    {% for nid, niche in niches.items() %}...{% endfor %}
  </header>

  <!-- Hero banner with tool name -->
  <div class="page-hero">...</div>

  <!-- Tool UI: inputs, buttons, result areas -->
  <div class="container">...</div>

  <!-- Footer -->
  <footer>...</footer>

  <!-- Floating subscribe button (Kit newsletter) -->
  <a href="https://techlife-insights.kit.com/be266c00d5" class="subscribe-float">📬 Subscribe</a>

  <script>
    /* Affiliate config object (reads from Jinja2 at build time) */
    var AFF = {
      amazon: '{{ affiliates.amazon_tag | default("") }}',
      ...
    };

    /* All tool data as JS arrays/objects */
    var data = [...];

    /* Event delegation (no inline onclick) */
    document.querySelector('.container').addEventListener('click', ...);

    /* Core logic functions */
    function doThing() { ... }
  </script>
</body>
</html>
```

**Design patterns used across all tools:**
- **Event delegation** — one listener on a parent element, uses `e.target.closest()`
- **No inline `onclick`** — prevents quoting bugs with dynamic content
- **Disabled buttons** — grey out until all required inputs are filled
- **`data-*` attributes** — pass data to event handlers without string escaping
- **Self-contained** — each template is a single file with HTML + CSS + JS

---

## 2. Deal Finder

**URL:** `/tools/deal-finder.html`
**Template:** `site/templates/deal_finder.html`
**Accent Color:** `#2563eb` (blue)

### What It Does
User types a product name → sees 9 retailer cards → clicks to open
price-comparison searches at each store. "Open All" button opens all
9 retailers in parallel tabs.

### Key Components

| Component | Description |
|-----------|-------------|
| `AFF` object | JS object with affiliate IDs from `{{ affiliates.* }}` |
| `affUrl(base, params)` | Helper that appends affiliate tracking params if ID is set |
| `retailers` array | 9 objects: `{name, icon, searchUrl, affParams}` |
| `recentSearches` | `localStorage` array of last 10 searches |
| Category shortcuts | 12 buttons for common product categories |
| "Open All" button | Opens all 9 retailer searches in new tabs |

### Retailers & Affiliate Status

| # | Retailer | Search URL Pattern | Affiliate Param | Config Key |
|---|----------|-------------------|-----------------|------------|
| 1 | Amazon | `amazon.com/s?k={query}` | `tag=` | `amazon_tag` |
| 2 | Best Buy | `bestbuy.com/site/searchpage.jsp?st={query}` | `irclickid=` | `bestbuy_pid` |
| 3 | Walmart | `walmart.com/search?q={query}` | `irclickid=` | `walmart_impact_id` |
| 4 | Target | `target.com/s?searchTerm={query}` | `ref=` | `target_affiliate_id` |
| 5 | Newegg | `newegg.com/p/pl?d={query}` | `ref=` | `newegg_affiliate_id` |
| 6 | eBay | `ebay.com/sch/i.html?_nkw={query}` | `campid=` + `toolid=` | `ebay_campid` |
| 7 | B&H Photo | `bhphotovideo.com/c/search?q={query}` | *(no program)* | — |
| 8 | Costco | `costco.com/CatalogSearch?keyword={query}` | *(no program)* | — |
| 9 | Google Shopping | `google.com/search?tbm=shop&q={query}` | *(meta-search)* | — |

### Data Flow
```
User types query ──► JS reads input ──► builds URL for each retailer
                                         ├─ if AFF.amazon is set: append &tag=...
                                         └─ if AFF.amazon is '': use plain URL
                     ──► opens in new tab(s)
                     ──► saves to localStorage for "Recent" list
```

### How to Add a Retailer
In `deal_finder.html`, add an entry to the `retailers` JS array:
```js
{name:'NewStore', icon:'🏪', url:function(q){
  var base='https://newstore.com/search?q='+encodeURIComponent(q);
  return affUrl(base, {ref: AFF.newstore});
}}
```
Then add `newstore_affiliate_id: ""` to `config/settings.yaml` under `affiliates:`.

### Maintenance
- **Update retailer URLs** if any store changes their search URL pattern
- **Add new category shortcuts** by editing the `categories` array in the template
- **localStorage** auto-manages recent searches (max 10, FIFO)

---

## 3. Travel Search

**URL:** `/travel/search.html`
**Template:** `site/templates/travel_search.html`
**Accent Color:** `#0ea5e9` (sky blue)

### What It Does
User selects origin/destination airports + dates → sees in-page flight, hotel,
and car rental results organized by provider. Each result links to the actual
booking site with the search pre-filled.

### Key Components

| Component | Description |
|-----------|-------------|
| `TAFF` object | JS object with 7 affiliate IDs from Jinja2 |
| `airports` array | **175+ airports** worldwide with IATA codes |
| `flightProviders` array | 5 flight search engines with URL builders |
| `hotelProviders` array | 5 hotel booking sites with URL builders |
| `carProviders` array | 4 car rental aggregators with URL builders |
| Autocomplete inputs | Type-ahead airport search (origin + destination) |
| In-page results | Cards showing each provider's link + description |

### Airport Database
All 175+ airports are hardcoded as JS objects:
```js
{code:'JFK', name:'John F. Kennedy International', city:'New York'}
```
Airports span: North America (60+), Europe (40+), Asia (30+), Latin America (15+),
Middle East (10+), Africa (10+), Oceania (5+).

### Provider Affiliate Status

**Flights:**
| Provider | Affiliate Param | Config Key |
|----------|-----------------|------------|
| Google Flights | *(no program)* | — |
| Skyscanner | `&associate=` | `skyscanner_associate` |
| Kayak | `&mc=` | `kayak_affiliate_id` |
| Momondo | *(no program)* | — |
| Kiwi.com | *(no program)* | — |

**Hotels:**
| Provider | Affiliate Param | Config Key |
|----------|-----------------|------------|
| Booking.com | `&aid=` | `booking_aid` |
| Hotels.com | *(no program)* | — |
| Hostelworld | `&affiliate=` | `hostelworld_affiliate_id` |
| Agoda | *(no program)* | — |
| Trivago | *(no program)* | — |

**Car Rentals:**
| Provider | Affiliate Param | Config Key |
|----------|-----------------|------------|
| Kayak Cars | `&mc=` | `kayak_affiliate_id` |
| RentalCars.com | `&affiliateCode=` | `rentalcars_affiliate_id` |
| Discover Cars | `&a_id=` | `discovercars_affiliate_id` |
| AutoEurope | *(no program)* | — |

### Data Flow
```
User selects airports + dates ──► JS validates inputs
  ──► builds provider URLs with dates + airport codes
  ──► if TAFF.booking is set: appends &aid=...
  ──► renders in-page result cards with links
```

### How to Add an Airport
Add to the `airports` array in `travel_search.html`:
```js
{code:'XYZ', name:'New Airport Name', city:'City Name'}
```

### How to Add a Provider
Add to `flightProviders`, `hotelProviders`, or `carProviders` array:
```js
{name:'NewProvider', icon:'✈️', desc:'Description here',
 url:function(o,d,dep,ret){
   var base='https://newprovider.com/search?from='+o+'&to='+d;
   return TAFF.newprovider ? base + '&ref=' + TAFF.newprovider : base;
 }}
```

### Maintenance
- **Update provider URLs** when booking sites change their URL structure
- **Add airports** as new routes open (e.g., new international terminals)
- **Check affiliate links** quarterly — providers may change their parameter names
- **Date format** — providers use various formats (YYYY-MM-DD, YYYYMMDD, etc.);
  the URL builder handles conversion for each

---

## 4. AI Tool Directory

**URL:** `/tools/ai-tool-finder.html`
**Template:** `site/templates/ai_tool_finder.html`
**Accent Color:** `#2563eb` (blue)

### What It Does
Browsable directory of 47 AI tools organized by category. Users can filter
by category or search by name/description. Each card shows the tool name,
description, pricing, and a "Visit" link.

### Key Components

| Component | Description |
|-----------|-------------|
| `AITAFF` object | JS object with 7 affiliate IDs from Jinja2 |
| `aitAff(base, key, param)` | Helper that appends affiliate param if ID is set |
| `aiTools` array | 47 tool objects: `{name, cat, desc, pricing, url}` |
| `categories` array | Auto-generated from unique `cat` values |
| Filter buttons | Category filter bar (All, Writing, Images, Video, etc.) |
| Search input | Real-time text search across name + description + category |
| `filterTools()` | Main render function — filters + generates card HTML |

### Categories (9 total)
Writing (8 tools) · Images (6) · Video (5) · Code (5) · Voice (4) ·
Productivity (5) · Research (4) · Marketing (5) · Design (5)

### Tools with Affiliate Programs

| Tool | Affiliate Network | URL Param | Config Key |
|------|-------------------|-----------|------------|
| Jasper | Direct | `?fpr=` | `jasper_fpr` |
| Grammarly | ShareASale | `?affiliateId=` | `grammarly_affiliate_id` |
| Writesonic | Direct | `?ref=` | `writesonic_ref` |
| Canva | Direct | `?affiliateRef=` | `canva_affiliate_id` |
| Descript | Direct | `?ref=` | `descript_ref` |
| SurferSEO | Impact | `?ref=` | `surferseo_ref` |
| Semrush | BeRush | `?ref=` | `semrush_ref` |

Tools without known affiliate programs (ChatGPT, Claude, Gemini, Midjourney,
Stable Diffusion, etc.) use plain direct URLs.

### How to Add a Tool
Add to the `aiTools` array:
```js
{name:'ToolName', cat:'Category', desc:'What it does.', pricing:'$X/mo', url:'https://tool.com'}
```
If it has an affiliate program:
```js
url: aitAff('https://tool.com', 'configkey', 'paramname')
```
And add `configkey: ""` to `settings.yaml` under `affiliates:`.

### Maintenance
- **Update pricing** quarterly (AI tool prices change frequently)
- **Add new tools** as they launch (keep array sorted by category)
- **Remove discontinued tools** (check URLs quarterly)
- **Apostrophe safety** — never use literal `'` inside single-quoted JS strings;
  use the curly right quote `'` (U+2019) for possessives in descriptions

---

## 5. Budget Calculator

**URL:** `/tools/budget-calculator.html`
**Template:** `site/templates/budget_calculator.html`
**Accent Color:** `#2563eb` (blue) / `#059669` (green hero)

### What It Does
4-tab financial calculator:
1. **Monthly Budget** — 50/30/20 rule analysis
2. **Debt Payoff** — amortization timeline with extra payment comparison
3. **Savings Goal** — compound interest projection to reach a target
4. **Emergency Fund** — progress tracker with fill timeline

### Key Components

| Component | Description |
|-----------|-------------|
| `BAFF` object | JS object with 3 financial affiliate IDs |
| `baffUrl(base, key, param)` | Helper for affiliate URL building |
| `finProducts` array | 3 recommended financial products (SoFi, Wealthfront, Betterment) |
| `showRecs(tab)` | Shows contextual product recommendations after results |
| Tab system | `data-tab` buttons + `tab-panel` divs, JS click handler |
| `calcBudget()` | 50/30/20 rule analysis with bar chart + insights |
| `calcDebt()` | Amortization with base vs. accelerated payoff comparison |
| `calcSavings()` | Compound interest future-value projection |
| `calcEmergency()` | Gap analysis with progress bar |
| `fmt(n)` | Dollar formatter with commas |
| `fmtYM(months)` | Months → "X yr Y mo" formatter |

### Financial Product Recommendations

After any calculation completes, `showRecs(tab)` displays a recommendations
panel with links to financial products:

| Product | For Tabs | Config Key |
|---------|----------|------------|
| SoFi Checking & Savings | budget, savings, emergency | `sofi_ref` |
| Wealthfront | budget, savings | `wealthfront_ref` |
| Betterment | budget, savings | `betterment_ref` |

### Calculations Explained

**Monthly Budget (50/30/20 Rule):**
- Sums all "needs" inputs (`.expense.needs`) and "wants" inputs (`.expense.wants`)
- Surplus = Total Income − (Needs + Wants)
- Compares percentages against ideal 50% needs / 30% wants / 20% savings
- Generates personalized insights based on overages

**Debt Payoff:**
- Uses iterative amortization loop (not closed-form) for accuracy
- Compares base payment vs. base + extra payment scenarios
- Shows months saved and interest saved with accelerated payments
- Guard: refuses if payment ≤ monthly interest charge

**Savings Goal:**
- Compound interest loop: `balance = balance * (1 + monthlyRate) + monthlyContrib`
- Shows total contributions vs. investment growth breakdown
- Bonus: projects "+50% contribution" scenario for motivation

**Emergency Fund:**
- Target = monthly expenses × months of coverage
- Progress bar with color coding: red (<50%), yellow (50-99%), green (100%+)
- Calculates months to fully funded at current contribution rate

### Maintenance
- **Update product recommendations** when new high-yield accounts launch
- **APY rates** in the recommendations panel are hardcoded text — update quarterly
- **No external APIs** — all calculations run client-side

---

## 6. Workout Generator

**URL:** `/tools/workout-generator.html`
**Template:** `site/templates/workout_generator.html`
**Accent Color:** `#7c3aed` (purple)

### What It Does
User picks 4 options (goal, equipment, time, level) → generates a complete
workout plan with warm-up, main set, and cool-down exercises, each with
sets/reps/rest prescriptions.

### Key Components

| Component | Description |
|-----------|-------------|
| `WAFF_TAG` | Amazon affiliate tag from Jinja2 |
| `amzSearch(q)` | Builds Amazon search URL with affiliate tag |
| `gearMap` object | Equipment recommendations per equipment type |
| `showGear(equip)` | Shows gear recommendations after workout generation |
| `sel` object | Tracks user selections: `{goal, equip, time, level}` |
| `exercises` object | Exercise database organized by equipment → type |
| `pick(arr, n)` | Random selection of n items from array (no repeats) |
| `generateWorkout()` | Core function — builds the workout plan |
| `checkReady()` | Enables/disables generate button based on selections |
| Option buttons | `data-group` + `data-val` attributes, event delegation |
| Phase headers | Colored section dividers: warm-up (orange), main (purple), cool-down (green) |
| Exercise pills | Colored badges showing sets, reps, rest per exercise |

### Exercise Database Structure
```js
exercises = {
  bodyweight: {
    warmup: ['Jumping Jacks', 'High Knees', ...],        // 5 exercises
    strength: ['Push-ups', 'Diamond Push-ups', ...],      // 12 exercises
    cardio: ['Burpees', 'Mountain Climbers', ...],        // 8 exercises
    flexibility: ['Cat-Cow Stretch', 'Pigeon Pose', ...]  // 8 exercises
  },
  dumbbells: { strength: [...], cardio: [...] },           // 13 exercises
  home: { strength: [...], cardio: [...] },                // 11 exercises
  full: { strength: [...], cardio: [...] }                 // 16 exercises
}
```
Total: ~73 unique exercises across all equipment tiers.

### Workout Generation Algorithm
1. Calculate exercise count: `max(3, floor(minutes / 5))`
2. Allocate: 20% warm-up (min 2-3) + 2 cool-down + rest to main set
3. Equipment pool merging: e.g., "home" = bodyweight + dumbbells + home-specific
4. Goal-based pool selection:
   - strength/muscle → `pool.strength`
   - cardio → `pool.cardio`
   - flexibility → `pool.flexibility`
   - weight_loss/general → `strength + cardio` mixed
5. Random pick from pools (no repeats)
6. Prescribe sets/reps based on level and goal:
   - Beginner: 2 sets · Intermediate: 3 sets · Advanced: 4 sets
   - Strength: 6-8 reps · Muscle: 8-12 reps · Cardio: 30 sec · Flexibility: 15-20 reps

### Equipment Recommendations (Affiliate)

After workout generation, `showGear(equip)` shows Amazon shopping links
for recommended gear based on the selected equipment type:

| Equipment | Recommended Gear |
|-----------|-----------------|
| No Equipment | Exercise Mat, Jump Rope, Resistance Bands |
| Dumbbells | Adjustable Dumbbells, Exercise Mat, Workout Gloves |
| Home Gym | Resistance Bands Set, Weight Bench, Pull-Up Bar, Foam Roller |
| Full Gym | Lifting Belt, Wrist Wraps, Gym Bag |

All links use `amazon_tag` from `settings.yaml`.

### Maintenance
- **Add exercises** to the appropriate `exercises.{equipment}.{type}` array
- **Apostrophe safety** — use `\u2019` (curly quote) for possessives like "Child's Pose"
- **Print stylesheet** — the tool supports `window.print()` with a print-specific
  CSS that hides nav, footer, and config sections

---

## 7. Pet Food Analyzer

**URL:** `/tools/pet-food-checker.html`
**Template:** `site/templates/pet_food_checker.html`
**Accent Color:** `#ea580c` (orange)

### What It Does
User selects pet type (dog/cat) → pastes ingredient list from food packaging →
gets a quality score (0-100) with per-ingredient breakdown showing which
ingredients are good, neutral, or concerning.

### Key Components

| Component | Description |
|-----------|-------------|
| `PAFF` object | JS object with `amazon_tag` and `chewy` affiliate IDs |
| `chewyUrl(q)` | Builds Chewy.com search URL with optional affiliate ref |
| `amzPetUrl(q)` | Builds Amazon pet food search URL with tag |
| `petBrands` object | 4 recommended brands per pet type (dog/cat) |
| `showBrandRecs(pet)` | Shows brand recommendations after analysis |
| `petType` variable | `'dog'` or `'cat'` |
| `goodIngredients` | Object with separate arrays for dog (32 items) and cat (18 items) |
| `okIngredients` | Array of 19 acceptable/filler ingredients |
| `badIngredients` | Array of 24 harmful/low-quality ingredients |
| `analyzeFood()` | Core function — splits, scores, and displays results |
| `checkAnalyzeReady()` | Enables/disables button based on textarea content |

### Scoring Algorithm
```
For each ingredient:
  1. Check against goodIngredients[petType] → "good" (10 pts)
  2. If not good, check against badIngredients → "bad" (0 pts)
  3. Otherwise → "ok" (5 pts)

Score = (totalPoints / maxPossiblePoints) × 100

Rating:
  ≥ 70 = "Good Quality" (green)
  40-69 = "Average Quality" (yellow)
  < 40 = "Below Average" (red)
```

### Ingredient Database

**Good Ingredients (Dog):** chicken, beef, salmon, turkey, lamb, duck,
venison, bison, brown rice, sweet potato, peas, blueberries, cranberries,
spinach, carrots, pumpkin, flaxseed, fish oil, coconut oil, turmeric,
probiotics, glucosamine, chondroitin, egg, sardine, herring, oatmeal,
barley, quinoa, kale, broccoli, apple

**Good Ingredients (Cat):** chicken, tuna, salmon, turkey, duck, rabbit,
sardine, herring, egg, liver, heart, fish oil, pumpkin, cranberries,
blueberries, taurine, probiotics, flaxseed

**Bad Ingredients (Universal):** by-product, artificial, BHA, BHT,
ethoxyquin, propylene glycol, menadione, food coloring, Red 40, Blue 2,
Yellow 5, Yellow 6, sodium nitrite, carrageenan, xylitol, propyl gallate,
TBHQ, rendered fat, animal digest, sugar, corn syrup, sorbitol

### Brand Recommendations (Affiliate)

After analysis, `showBrandRecs(petType)` shows shopping links to top-rated brands:

| Brand | Pet Type | Chewy Link | Amazon Link |
|-------|----------|------------|-------------|
| Blue Buffalo Life Protection | Dog | ✅ | ✅ |
| Taste of the Wild | Dog | ✅ | ✅ |
| Orijen Original | Dog | ✅ | ✅ |
| Wellness CORE | Dog | ✅ | ✅ |
| Blue Buffalo Wilderness | Cat | ✅ | ✅ |
| Taste of the Wild Canyon River | Cat | ✅ | ✅ |
| Orijen Cat & Kitten | Cat | ✅ | ✅ |
| Wellness CORE Indoor | Cat | ✅ | ✅ |

Config keys: `chewy_affiliate_id` (Chewy), `amazon_tag` (Amazon).

### Maintenance
- **Add ingredients** to `goodIngredients`, `okIngredients`, or `badIngredients`
- **Add brands** to the `petBrands` object
- **Update scoring weights** by changing point values (currently 10/5/0)
- **Ingredient matching** is case-insensitive substring matching — be specific
  to avoid false positives (e.g., "corn" also matches "corn syrup")

---

## 8. Smart Home Hub

**URL:** `/tools/smart-home.html`
**Template:** `site/templates/smart_home.html`
**Accent Color:** `#2563eb` (blue)

### What It Does
Interactive smart home compatibility checker. Users browse 29 devices across
4 ecosystems (Apple, Google, Amazon, SmartThings). Each device card shows
which ecosystems it works with, its category, and has an Amazon buy link.

### Key Components

| Component | Description |
|-----------|-------------|
| `devices` array | 29 smart home devices with compatibility data |
| `renderFilters()` | Builds ecosystem filter buttons |
| `renderDevices()` | Generates device cards with compatibility icons |
| Filter buttons | `data-eco` attributes for ecosystem filtering |
| Device cards | Name, category, compatibility icons, Amazon buy link |
| Amazon buy links | `https://amazon.com/s?k={name}&tag={amazon_tag}` |

### Device Database (29 devices)
Each device object:
```js
{name:'Echo Dot', cat:'Speaker', eco:['amazon','google']}
```

Categories: Speaker, Display, Thermostat, Lock, Camera, Light, Plug, Doorbell, Sensor, Robot

Ecosystems:
- 🍎 Apple HomeKit
- 🔵 Google Home
- 📦 Amazon Alexa
- ⚡ SmartThings

### Affiliate Integration
Every device card includes an Amazon buy link:
```
https://www.amazon.com/s?k={deviceName}&tag={{ affiliates.amazon_tag | default("techlife0ac-20") }}
```
This is the only tool where the affiliate tag is used directly in the HTML
template (not through a JS helper) because the tag value doesn't need
conditional logic — it always defaults to the active Amazon tag.

### How to Add a Device
Add to the `devices` array:
```js
{name:'Device Name', cat:'Category', eco:['apple','google','amazon','smartthings']}
```

### Maintenance
- **Update compatibility** when devices add/remove ecosystem support
- **Add new devices** as smart home products launch
- **Category consistency** — use existing category names to keep filters clean
- **Amazon URLs** use search, not direct product links — this is intentional
  because specific ASINs go stale; search links always work

---

## 9. Market Data Center

**URL:** `/personal_finance/markets.html`
**Template:** `site/templates/market_data.html`
**Accent Color:** `#059669` (green)

### What It Does
Displays live market data using embedded TradingView widgets. Shows major
indices, forex pairs, and crypto prices in a clean dashboard layout.

### Key Components

| Component | Description |
|-----------|-------------|
| TradingView widgets | Embedded iframes for market data |
| Market sections | Indices, Forex, Crypto organized in grids |
| Auto-refresh | Widgets update via TradingView's own refresh mechanism |

### Data Source
All market data comes from **TradingView's embeddable widgets** — no API key
needed, no rate limits, no data staleness issues. The data is always live.

### Maintenance
- **Minimal** — TradingView handles all data updates
- **Widget changes** — if TradingView changes their embed format, update the
  widget code in the template
- **No affiliate opportunity** — TradingView's free widgets don't have referral programs

---

## 10. Affiliate & Monetization Setup

### 10.1 Where Affiliate IDs Are Stored

All affiliate IDs live in one place: `config/settings.yaml` under the `affiliates:` key.

```yaml
affiliates:
  amazon_tag: "techlife0ac-20"       # ← Already active
  bestbuy_pid: ""                    # ← Fill when you join
  booking_aid: ""
  jasper_fpr: ""
  # ... (25+ keys total)
```

### 10.2 How to Activate an Affiliate Program

1. **Sign up** for the affiliate program (see table below)
2. **Get your affiliate ID** (tracking tag, partner ID, referral code, etc.)
3. **Paste the ID** into the corresponding field in `config/settings.yaml`
4. **Rebuild the site** to inject the new ID into templates:
   ```bash
   source contentgenerator/bin/activate
   python3 -c "
   from core.publisher import rebuild_site
   import yaml
   from pathlib import Path
   with open('config/settings.yaml') as f:
       settings = yaml.safe_load(f)
   rebuild_site(settings, Path('data/bot.db'), settings.get('site', {}).get('url', ''))
   "
   ```
5. **Commit and push** — Cloudflare Pages auto-deploys

### 10.3 Affiliate Programs — Sign-Up Links & Details

#### Shopping / Deal Finder

| Program | Sign-Up URL | ID Format | Notes |
|---------|-------------|-----------|-------|
| Amazon Associates | https://affiliate-program.amazon.com | Tag: `yourname-20` | Most common, 1-10% commission |
| Best Buy (Impact) | https://app.impact.com/campaign-promo-signup/Best-Buy.brand | PID (numeric) | Via Impact Radius |
| Walmart (Impact) | https://affiliates.walmart.com | Click ID | Via Impact Radius |
| Target (Impact) | https://partners.target.com | Affiliate ID | Via Impact Radius |
| eBay Partner Network | https://partnernetwork.ebay.com | Campaign ID + Tool ID | Up to 4% commission |
| Newegg (CJ) | https://www.cj.com (search "Newegg") | Advertiser ID | Via Commission Junction |

#### Travel

| Program | Sign-Up URL | ID Format | Notes |
|---------|-------------|-----------|-------|
| Booking.com | https://www.booking.com/affiliate-program | Aid (numeric) | 25-40% commission |
| Skyscanner | https://www.partners.skyscanner.net | Associate ID | Flight search referrals |
| Kayak / KAYAK | https://www.kayak.com/affiliates | MC (advertiser code) | Via CJ Affiliate |
| Hostelworld | https://www.hostelworld.com/affiliates | Affiliate ID | Budget travel niche |
| RentalCars.com | https://www.rentalcars.com/affiliates | Affiliate Code | Via Booking Holdings |
| Discover Cars | https://www.discovercars.com/affiliates | Partner ID (a_id) | Car rental comparison |

#### AI Tools

| Program | Sign-Up URL | ID Format | Notes |
|---------|-------------|-----------|-------|
| Jasper AI | https://www.jasper.ai/partners | FPR code | 30% recurring commission |
| Grammarly | https://www.shareasale.com (search "Grammarly") | ShareASale affiliate ID | $0.20/free + $20/premium |
| Semrush (BeRush) | https://www.semrush.com/lp/affiliate-program | Ref code | $200/sale recurring |
| SurferSEO | https://surferseo.com/affiliates | Ref code | 25% recurring |
| Canva | https://www.canva.com/affiliates | Affiliate ID | Via Impact |
| Writesonic | https://writesonic.com/affiliates | Ref code | 30% lifetime |
| Descript | https://www.descript.com/affiliates | Ref ID | Per-sale commission |

#### Pet Food

| Program | Sign-Up URL | ID Format | Notes |
|---------|-------------|-----------|-------|
| Chewy.com | https://www.chewy.com/affiliate (or via Partnerize/CJ) | Affiliate ref | Per-sale commission |
| Amazon (Pet category) | Same as Amazon Associates | Same tag | Use `amazon_tag` |

#### Finance / Budget

| Program | Sign-Up URL | ID Format | Notes |
|---------|-------------|-----------|-------|
| SoFi | https://www.sofi.com/invite | Referral ID | $25-$300 per referral |
| Wealthfront | https://www.wealthfront.com/invite | Invite link | $5K managed free |
| Betterment | https://www.betterment.com/referrals | Referral code | Varies |

### 10.4 Revenue Potential by Tool

| Tool | Monthly Traffic Est. | Affiliate Sources | Revenue Potential |
|------|---------------------|-------------------|-------------------|
| Deal Finder | High | 6 retailers with programs | $$$ — every click = potential sale |
| Travel Search | High | 6 providers with programs | $$$ — high-value bookings |
| AI Tool Directory | Medium | 7 tools with programs | $$ — SaaS recurring commissions |
| Smart Home Hub | Medium | Amazon on all 29 devices | $$ — product purchases |
| Budget Calculator | Low-Medium | 3 fintech products | $$ — high-value signups |
| Workout Generator | Low-Medium | Amazon gear links | $ — equipment purchases |
| Pet Food Analyzer | Low | Chewy + Amazon | $ — repeat pet food purchases |
| Market Data | Low | None currently | — |

### 10.5 Compliance Notes

- **FTC Disclosure:** Every tool with affiliate links includes a disclaimer:
  *"Some links may be affiliate links — we may earn a commission at no extra cost to you."*
- **Add a site-wide disclosure page** at `/affiliate-disclosure.html` (recommended)
- **Amazon specifically requires** visible disclosure near affiliate links
- **Never cloak** affiliate links — transparency builds trust

---

## 11. Adding a New Tool

### Step 1: Create the Template
Create `site/templates/my_new_tool.html` following the common anatomy
(see §1.5). Copy an existing tool template as a starting point.

### Step 2: Register in Publisher
In `core/publisher.py`, add to the `tool_templates` dict in `_rebuild_tools_pages()`:
```python
tool_templates = {
    ...
    "my_new_tool.html": "my-new-tool.html",
}
```

### Step 3: Add to Navigation
In every tool template's nav dropdown, add:
```html
<a href="/tools/my-new-tool.html">🔧 My New Tool</a>
```
Also add it to the tools index template `tools_index.html`.

### Step 4: Add Affiliate Config (if applicable)
In `config/settings.yaml` under `affiliates:`, add any new keys:
```yaml
affiliates:
  my_new_tool_ref: ""
```

### Step 5: Rebuild & Test
```bash
source contentgenerator/bin/activate
python3 -c "
from core.publisher import rebuild_site
import yaml
from pathlib import Path
with open('config/settings.yaml') as f:
    settings = yaml.safe_load(f)
rebuild_site(settings, Path('data/bot.db'), settings.get('site', {}).get('url', ''))
"
```

Then open `site/output/tools/my-new-tool.html` in a browser to verify.

---

## 12. Testing & Deployment

### Local Testing
```bash
# Option 1: Python HTTP server
cd site/output && python3 -m http.server 8080
# Then open http://localhost:8080/tools/deal-finder.html

# Option 2: Open file directly
open site/output/tools/deal-finder.html
```

### Rebuild All Tools
```bash
source contentgenerator/bin/activate
python3 -c "
from core.publisher import rebuild_site
import yaml
from pathlib import Path
with open('config/settings.yaml') as f:
    settings = yaml.safe_load(f)
rebuild_site(settings, Path('data/bot.db'), settings.get('site', {}).get('url', ''))
"
```

### Deploy to Cloudflare Pages
```bash
git add -A
git commit -m "update: tool templates"
git push origin main
```
Cloudflare Pages auto-deploys from the `main` branch. Changes go live
within 1-2 minutes of push.

### Validate Affiliate Links
After deployment, spot-check:
1. Open each tool on the live site
2. Perform a test action (search, calculate, generate)
3. Inspect the outbound link URLs — verify affiliate params are present
4. Click through to confirm the destination site accepts the tracking param

---

## 13. Troubleshooting

### Common Issues

**Problem:** Tool page shows `{{ affiliates.xxx }}` literally instead of the value
**Cause:** Template was opened directly in browser, not rendered by publisher
**Fix:** Rebuild the site using `rebuild_site()` — never serve raw templates

**Problem:** JS crash — tool buttons don't work
**Cause:** Usually an unescaped character inside a JS string literal
**Fix:** Check for literal apostrophes (`'`) inside single-quoted JS strings.
Use `\u2019` (curly right quote) for possessives in descriptions.
Check for literal newlines in regex patterns — use `[...\n]` character class.

**Problem:** Affiliate links not working
**Cause:** The affiliate ID in `settings.yaml` is empty, or the parameter
name changed on the provider's side
**Fix:** Verify the ID is filled in `settings.yaml`, rebuild, and test the URL

**Problem:** Category/filter buttons not clickable
**Cause:** Inline `onclick` handlers with string quoting issues
**Fix:** All tools now use event delegation. If adding new interactive
elements, use `data-*` attributes + parent `.addEventListener('click', ...)`.

**Problem:** New tool not showing up at `/tools/`
**Cause:** Template not registered in `publisher.py`
**Fix:** Add the template-to-filename mapping to `_rebuild_tools_pages()`
and add a nav link in the tools dropdown of every template.

### Quick Diagnostics
```bash
# Check a template for JS syntax errors
node -e "
  const fs = require('fs');
  const html = fs.readFileSync('site/output/tools/ai-tool-finder.html','utf8');
  const m = html.match(/<script>([\s\S]*?)<\/script>/);
  if (m) { eval(m[1]); console.log('JS OK'); }
"

# Check all templates render without Jinja2 errors
python3 -c "
from core.publisher import rebuild_site
import yaml
from pathlib import Path
with open('config/settings.yaml') as f:
    s = yaml.safe_load(f)
rebuild_site(s, Path('data/bot.db'), s.get('site',{}).get('url',''))
print('All templates rendered OK')
"
```

---

*Last updated: June 2025*
