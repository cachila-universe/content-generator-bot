# Stock Photo Platform Research — AI Content & Contributor APIs

> **Date:** March 7, 2026  
> **Purpose:** Evaluate platforms for automated AI-generated stock image submission

---

## Quick Comparison Matrix

| Platform | AI Content? | Contributor Upload API? | Best For Automation? |
|---|---|---|---|
| **Adobe Stock** | ✅ Yes (with disclosure) | ❌ No contributor API | ❌ No |
| **Shutterstock** | ✅ Yes (with disclosure) | ❌ No public contributor upload API | ❌ No |
| **Dreamstime** | ✅ Yes (with disclosure) | ⚠️ Buyer-side API only | ❌ No |
| **Freepik** | ✅ Yes (with disclosure) | ❌ No API — manual portal only | ❌ No |
| **Alamy** | ❌ No — banned entirely | ❌ No contributor API | ❌ No |
| **123RF** | ✅ Yes (likely, with disclosure) | ❌ No public contributor API | ❌ No |
| **Pond5** | ✅ Yes (with disclosure) | ❌ No public contributor API | ❌ No |
| **Wirestock** | ✅ Yes — AI-native platform | ⚠️ No documented public API, but auto-distributes | ✅ Best option |
| **iStock/Getty** | ❌ No — banned entirely | ❌ No public contributor API | ❌ No |
| **Depositphotos** | ✅ Yes (with disclosure) | ❌ No public contributor API | ❌ No |
| **EyeEm** | 🔀 Merged into Freepik | N/A — redirects to Freepik | ❌ No |
| **Stocksy** | ❌ No — banned (invite-only) | ❌ No API | ❌ No |
| **SmugMug** | N/A — portfolio/selling site, not stock | ❌ No stock contributor API | ❌ No |

---

## 1. Adobe Stock (Contributor)

### AI Content Policy
**✅ Yes — with mandatory disclosure**

Adobe Stock explicitly accepts generative AI content. Their detailed policy requires:
- Check the **"Created using generative AI tools"** checkbox before submission
- Check **"People and Property are fictional"** if depicting fake persons/property
- Prompts/titles/keywords must NOT contain: artist names, real people names, fictional characters, government agencies, third-party IP
- Submit AI photos as "Photos" (if photorealistic) or "Illustrations" (if artistic/fantasy)
- Do NOT add "generative AI" to titles/keywords — the checkbox handles classification
- Model releases required if depicting/based on real identifiable persons
- AI content cannot be submitted to the Illustrative Editorial Collection (IEC)

### Contributor Upload API
**❌ No — there is NO contributor upload API**

Adobe's own documentation explicitly states:
> "Approvals will NOT be given to Contributor use cases because there is no API for Stock Contributors. There is no API to get sales data, see top sellers, see creation dates or upload new Stock content. Those actions must be performed in the Stock Contributors portal."

The Adobe Stock API is **buyer-side only** (search, license, download). As of November 2024, it's restricted to Stock for Enterprise customers only.

### API Details (Buyer-side only)
- **URL:** https://developer.adobe.com/stock/docs/
- **Auth:** OAuth 2.0 / Server-to-server (Enterprise only)
- **Capabilities:** Search, license, download — NOT upload/submit

### How to Submit Content
1. Sign up at https://contributor.stock.adobe.com/ with an Adobe ID
2. Upload via the contributor web portal manually
3. Add metadata (title, keywords, categories, releases) in the portal UI

### Commission Rate
- **33% royalty** on all sales

### AI Disclosure Requirements
- Mandatory "Created using generative AI tools" checkbox
- "People and Property are fictional" checkbox if applicable
- No artist names, real people, or IP references in prompts

---

## 2. Shutterstock (Contributor)

### AI Content Policy
**✅ Yes — with mandatory disclosure**

Shutterstock accepts AI-generated content. Contributors must:
- Disclose AI-generated content during the submission process
- Mark content as AI-generated using the provided tools
- Ensure they have rights to submit (review AI tool terms of service)
- Not submit content that infringes on IP or depicts real identifiable people without releases

### Contributor Upload API
**❌ No public contributor upload API**

The Shutterstock API (https://api-reference.shutterstock.com/) is a **buyer/consumer API** only. It provides:
- Image/video/audio search
- Licensing and downloading
- Collections management
- Computer vision (reverse image search, keyword suggestions)

There are **no endpoints for uploading/submitting content as a contributor**. The API documentation covers `GET /v2/images`, `POST /v2/images/licenses`, search endpoints, etc. — all consumer-facing.

### API Details (Buyer-side only)
- **URL:** https://api-reference.shutterstock.com/
- **Auth:** HTTP Basic auth (some endpoints) + OAuth 2.0 (all endpoints)
- **Scopes:** `licenses.create`, `licenses.view`, `purchases.view`, `collections.edit`, `user.view`
- **Application setup:** https://www.shutterstock.com/account/developers/apps
- **Rate limits:** Vary by subscription tier

### How to Submit Content
1. Sign up at https://submit.shutterstock.com/
2. Upload via the contributor portal or mobile app
3. Required metadata: title, description, keywords (7-50), categories, editorial vs. commercial, model/property releases
4. Content reviewed by Shutterstock team

### Commission Rate
- **15%–40%** based on lifetime earnings level
  - Level 1: 15% (0–100 lifetime downloads)
  - Level 2: 20% (101–250)
  - Level 3: 25% (251–500)
  - Level 4: 30% (501–2,500)
  - Level 5: 35% (2,501–25,000)
  - Level 6: 40% (25,001+)
- Over **$1 billion paid** to contributors since 2003

### AI Disclosure Requirements
- Must mark content as AI-generated during submission
- Must have rights under the AI tool's terms of service

---

## 3. Dreamstime

### AI Content Policy
**✅ Yes — with disclosure (accepted since ~2023)**

Dreamstime accepts AI-generated images with proper disclosure. Contributors must label AI content appropriately.

### Contributor Upload API
**⚠️ Buyer-side API only — no contributor upload endpoint**

The Dreamstime API (https://www.dreamstime.com/dreamstime-api) is focused on:
- **Partner / Search API** — embed search in your site, earn affiliate commissions
- **Business API** — integrate stock library for your customers
- **Enterprise / Intranet API** — CMS/DAM integration
- **Reseller** — sell from your own platform
- **Affiliate Program** — promote Dreamstime, earn 10%+ commissions

No documentation for contributor upload/submission via API. Upload is done at https://www.dreamstime.com/upload (web portal).

### How to Submit Content
1. Register at https://www.dreamstime.com/ (free)
2. Upload images via the web portal at https://www.dreamstime.com/upload
3. Required metadata: title, description, keywords, categories, model/property releases
4. Images reviewed by editors

### Commission Rate
- **25%–50%** for non-exclusive contributors
- Up to **60%** for exclusive contributors
- Payment via PayPal, Skrill, or check when balance reaches $100

### AI Disclosure Requirements
- Must label AI-generated content during submission

---

## 4. Freepik (Contributor)

### AI Content Policy
**✅ Yes — with disclosure**

Freepik accepts AI-generated content. Note: EyeEm (formerly a separate platform) now redirects entirely to Freepik's contributor portal.

### Contributor Upload API
**❌ No API — manual portal upload only**

Freepik uses a web-based contributor panel (https://contributor.freepik.com/) with:
- Batch uploading capability
- Keyword management tools
- Impact/analytics dashboard
- No documented public API for automated submission

### How to Submit Content
1. Register at https://www.freepik.com/sign-up?client_id=freepik_contributor
2. Upload 10 initial resources for review
3. Once approved, upload via contributor panel
4. Supports: photos, vectors, illustrations, PSD mockups/templates
5. Add keywords and metadata in the panel

### Commission Rate
- **Pay per download** model (specific rates not publicly disclosed on main page)
- Referral program available for additional earnings
- Brand Ambassador program available

### AI Disclosure Requirements
- Must follow Freepik's submission guidelines for AI content

---

## 5. Alamy

### AI Content Policy
**❌ No — AI-generated content is BANNED**

Alamy's contributor page explicitly states:
> "As champions of authentic content, we don't accept any AI-generated images on our platform, so if you're a photographer or artist who works in the real world you can find your home here with like-minded creatives."

### Contributor Upload API
**❌ No contributor upload API**

Alamy has a buyer-side API for search/licensing (https://www.alamy.com/api-partnerships/), but no contributor upload API. Contributors upload via:
- Online web portal
- FTP client

### How to Submit Content
1. Register at https://www.alamy.com/registration/contributor-signup.aspx
2. Upload through the online portal or FTP
3. Pass quality control review
4. Add captions and tags/keywords

### Commission Rate
- **Up to 50%** commission on sales
- **100% commission** for students (for 2 years)

### AI Disclosure Requirements
- N/A — AI content not accepted at all

---

## 6. 123RF

### AI Content Policy
**✅ Likely Yes — with disclosure**

123RF (owned by Inmagine) accepts various content types. They have an AI Image Generator built into their platform, suggesting they accept AI-created content with appropriate disclosure.

### Contributor Upload API
**❌ No documented public contributor API**

No public contributor upload API documentation found. Content is submitted through the contributor portal at https://www.123rf.com/sellimages/.

### How to Submit Content
1. Register at https://www.123rf.com/sellimages/
2. Upload photos, vectors, video, audio, or fonts
3. Content is marketed across 44 countries in 17 languages

### Commission Rate
- **30%–60%** commission per license sold
- Payment via PayPal, Skrill, Payoneer, or Alipay (China only)
- Minimum payout threshold: **$50**
- Payments processed automatically on the 15th of every month
- Non-exclusive (can sell elsewhere)

### AI Disclosure Requirements
- Must follow platform guidelines for AI content disclosure

---

## 7. Pond5

### AI Content Policy
**✅ Yes — with disclosure**

Pond5 accepts AI-generated content but requires clear labeling and disclosure. Contributors must indicate AI involvement in creation.

### Contributor Upload API
**❌ No public contributor upload API found**

Pond5 does not appear to offer a public contributor upload API. Content is submitted through their web portal. Their site returned 403 errors for most documentation pages during research.

### How to Submit Content
1. Sign up at https://www.pond5.com/sell-media
2. Upload via the contributor portal
3. Required: title, description, keywords, categories, pricing (artist sets prices)
4. Supports: video, photos, illustrations, music, sound effects, 3D models, After Effects templates

### Commission Rate
- **Contributor sets their own prices** (unique among stock platforms)
- Pond5 takes a commission on each sale
- Non-exclusive contributors: **50%** revenue share
- Exclusive contributors: **60%** revenue share

### AI Disclosure Requirements
- Must label AI-generated content

---

## 8. Wirestock ⭐ BEST FOR AUTOMATION

### AI Content Policy
**✅ Yes — AI-native platform**

Wirestock is the most AI-friendly platform researched. They:
- Accept AI-generated photos, videos, illustrations, 3D, and AI art
- Have paid AI training projects where creators contribute to AI labs
- Host creative challenges (e.g., co-hosted with OpenAI)
- Describe themselves as "Connecting Creators and AI Teams"
- Have paid $10M+ to creators

### Contributor Upload API
**⚠️ No documented public REST API, BUT auto-distributes to major platforms**

Wirestock's killer feature: **upload once, distribute to multiple stock platforms automatically**. When you upload to Wirestock, they can submit your content to:
- Shutterstock
- Adobe Stock
- Getty/iStock
- Freepik
- Dreamstime
- Alamy
- And others

This effectively gives you **automated multi-platform distribution** through a single upload.

### How to Submit Content
1. Sign up at https://wirestock.io/signup
2. Upload your content (photos, videos, illustrations, 3D, AI art)
3. Wirestock handles metadata optimization and multi-platform distribution
4. Also participate in paid AI training projects and creative challenges

### Commission Rate
- Revenue share on stock sales (varies by destination platform)
- Additional earnings from paid AI training projects
- Monthly payouts
- $10M+ total paid to creators

### AI Disclosure Requirements
- AI content is welcomed and supported natively
- Appropriate disclosure is handled as part of the submission flow

---

## 9. iStock / Getty Images

### AI Content Policy
**❌ No — AI-generated content is BANNED**

Getty Images and iStock have prohibited AI-generated content since September 2022. Their position:
- AI-generated images created using tools like DALL-E, Midjourney, Stable Diffusion, etc. are **not accepted**
- Concerns about: copyright of training data, inability to assign copyright to AI outputs, and potential legal liability
- This applies to both Getty Images and iStock (same company)

### Contributor Upload API
**❌ No public contributor upload API**

Getty uses ESP (Electronic Submission Portal) at https://esp.gettyimages.com/ for contributors. This is a web portal, not a REST API. Contributors must apply to be accepted.

### How to Submit Content
1. Apply at https://www.gettyimages.com/workwithus
2. Must be accepted (curated/selective process)
3. Upload via ESP portal (https://esp.gettyimages.com/)
4. Very high quality standards

### Commission Rate
- **iStock:** 15%–45% depending on exclusivity and content type
- **Getty Images:** 20%–25% for creative content, 25%–30% for editorial

### AI Disclosure Requirements
- N/A — AI content not accepted at all

---

## 10. Depositphotos

### AI Content Policy
**✅ Yes — with disclosure (likely)**

Depositphotos (now owned by Vista/VistaPrint) has an AI Image Generator integrated into their platform. They likely accept AI-generated contributor content with appropriate disclosure, though explicit policy documentation was limited.

### Contributor Upload API
**❌ No public contributor upload API found**

No documented public API for contributor uploads. Depositphotos has a buyer-side API for search and licensing.

### How to Submit Content
1. Sign up as a contributor at https://depositphotos.com/
2. Upload via the contributor portal
3. Required: titles, descriptions, keywords, categories, releases
4. Content reviewed before acceptance

### Commission Rate
- **34%–42%** for non-exclusive contributors
- Up to **42%** for exclusive contributors
- Varies by content type and buyer's purchase method

### AI Disclosure Requirements
- Follow platform disclosure guidelines for AI content

---

## 11. EyeEm

### AI Content Policy
**🔀 Merged — redirects to Freepik**

EyeEm has been acquired/merged and now redirects entirely to Freepik's contributor portal (https://contributor.freepik.com/). See Freepik section above for current policies.

---

## 12. Stocksy

### AI Content Policy
**❌ No — AI-generated content is BANNED**

Stocksy is an invite-only artist cooperative that focuses on authentic, curated content. They do not accept AI-generated images.

### Contributor Upload API
**❌ No API**

Stocksy is an invitation-only platform. No public contributor API.

### How to Submit Content
1. Apply and get invited
2. Stocksy is very selective about who they accept
3. Upload through their internal portal once accepted

### Commission Rate
- **50%** for standard licenses
- **75%** for extended licenses
- Co-op model — artists are co-owners

### AI Disclosure Requirements
- N/A — AI content not accepted

---

## 13. SmugMug

### AI Content Policy
**N/A — SmugMug is NOT a stock agency**

SmugMug is a photo hosting and selling platform (portfolio/print sales), not a stock photography marketplace. Photographers use it to sell prints and digital downloads directly to their clients.

### Contributor Upload API
**N/A for stock submission**

SmugMug has an API for managing galleries and photos on the platform, but it's for portfolio/client management, not stock photo contribution.

### Commission Rate
- Photographers set their own prices
- SmugMug takes a subscription fee ($13–$47/month) rather than per-sale commission

---

---

## Deep Dive: FTP/SFTP Upload Research (March 2026)

### Does Any Stock Platform Still Support FTP/SFTP for Contributors?

| Platform | FTP/SFTP Support? | Details |
|---|---|---|
| **Adobe Stock** | ❌ **No** | No FTP/SFTP. Upload only via contributor portal (contributor.stock.adobe.com). Help docs mention only the web uploader. No alternative upload methods documented. |
| **Shutterstock** | ❌ **No** | No FTP/SFTP. Upload only via contributor portal (submit.shutterstock.com) or Contributor Mobile App. Help center lists only web portal and mobile app as upload methods. Historical SFTP access was removed years ago. |
| **Alamy** | ⚠️ **Yes, FTP exists** | Alamy mentions FTP upload for contributors, BUT **Alamy bans all AI content**, so this is not usable for our use case. |
| **Dreamstime** | ❌ **No** | Web portal upload only at dreamstime.com/upload |
| **Freepik** | ❌ **No** | Contributor panel only at contributor.freepik.com |
| **123RF** | ❌ **No** | Contributor portal only |
| **Pond5** | ❌ **No** | Contributor portal only |
| **Depositphotos** | ❌ **No** | Contributor portal only |
| **Getty/iStock** | ❌ **No** (ESP portal only) | Uses ESP (Electronic Submission Portal) web interface. No FTP/SFTP. Also bans AI content entirely. |

**Conclusion:** FTP/SFTP contributor upload is effectively **dead** across the industry. The only platform that still supports it (Alamy) bans AI content entirely. All major platforms have migrated to web portal-only upload.

---

## Deep Dive: Wirestock API & Automation (March 2026)

### 1. Does Wirestock Have a Public REST API?

**❌ No documented public REST API for contributor uploads.**

- `wirestock.io/api` returns a 404 "No results found" page
- `wirestock.io/pricing` returns a 404 "No results found" page (old pricing page removed)
- No API documentation, no developer docs, no Swagger/OpenAPI spec found
- No mention of API keys, OAuth, or developer applications anywhere on the site

### 2. Wirestock's Current Business Model Has Pivoted

**⚠️ IMPORTANT: Wirestock has significantly pivoted since 2023.**

As of March 2026, Wirestock's homepage describes itself as:
> "POWER YOUR AI MODELS WITH MULTIMODAL IMAGE & VIDEO DATA"
> "FUELING AI WITH HUMAN CREATIVITY"

Their primary business is now **selling curated datasets to AI companies**, not stock photo distribution. Key stats from their site:
- 700K+ creators
- 50M+ total content pieces
- 1M+ new content sourced monthly
- $10M+ paid to creators

### 3. Ways to Earn on Wirestock (2026)

Wirestock now offers three main earning paths:
1. **Paid AI Training Projects** — Complete briefs from AI labs (photography, digital art, video, branding)
2. **Creative Challenges** — Submit AI art for cash prizes (co-hosted with OpenAI and others)
3. **Portfolio** — Upload content that may be licensed through data deals

The old "upload once, auto-distribute to stock platforms" feature is **no longer prominently advertised** on their site. The FAQ still mentions "Where and How Is My Content Sold?" and "Which partners does Wirestock work with?" but the emphasis has shifted to AI data licensing.

### 4. Wirestock Discord Bot (Semi-Automation)

Wirestock **does** have a Discord bot that provides a semi-automated workflow:

**How it works:**
1. Install the Wirestock bot via Discord OAuth link
2. Go to Wirestock Account Settings → copy your Discord token
3. In Discord, use `/login` command and paste the token
4. Click "More" on a Midjourney-generated image → "Apps" → "Upscale & Publish"
5. Bot auto-upscales the image and posts it to your Wirestock portfolio
6. Bot sends you a confirmation message with a link

**Limitations:**
- Designed specifically for Midjourney → Wirestock workflow
- Requires manual interaction per image (click "Upscale & Publish")
- Not a true programmatic API (no batch/bulk support)
- Posted in June 2023 — may or may not still be active in 2026

### 5. Wirestock FAQ Highlights

From `wirestock.io/docs/faq`:
- **Who Can Join?** — Anyone can join
- **Exclusivity?** — Wirestock does NOT require exclusivity
- **Partners?** — Lists partner platforms (specific partners not visible in FAQ summary, but historically included Shutterstock, Adobe Stock, Getty/iStock, Freepik, Dreamstime, Alamy)
- **Dataset Deals Program** — New program where uploaded content earns royalties through AI data licensing deals
- **Quality Requirements** — Content must meet platform quality standards

---

## Deep Dive: Shutterstock API Analysis (March 2026)

### API Capabilities (Buyer-Side Only)

The Shutterstock API at `api-reference.shutterstock.com` is **comprehensive but consumer-only**:

| Feature | Endpoint | Contributor Upload? |
|---|---|---|
| Search images | `GET /v2/images/search` | ❌ No |
| License images | `POST /v2/images/licenses` | ❌ No |
| Download images | `POST /v2/images/licenses/{id}/downloads` | ❌ No |
| Upload for reverse search | `POST /v2/cv/images` | ❌ For CV only, not contributor submission |
| Keyword suggestions | `GET /v2/cv/keywords` | ❌ Useful but not upload |
| Collections | `POST /v2/images/collections` | ❌ Buyer collections only |
| Catalog management | `POST /v2/catalog/collections` | ❌ Enterprise/SMB only |
| Bulk search | `POST /v2/bulk_search/images` | ❌ No |
| User details | `GET /v2/user` | ❌ Returns `contributor_id` but no upload |

**Key finding:** The `POST /v2/cv/images` endpoint accepts base64-encoded images, but it's strictly for computer vision (reverse image search and keyword suggestions), NOT for submitting content to the Shutterstock contributor library.

### Potentially Useful for Our Pipeline

Even though Shutterstock can't receive contributor uploads via API, two endpoints could help with **metadata optimization**:

1. **`POST /v2/cv/images` + `GET /v2/cv/keywords`** — Upload an image and get AI-suggested keywords. Could be used to improve our stock image keywording before manual submission.
2. **`GET /v2/images/search/suggestions`** — Get autocomplete suggestions for search terms. Useful for finding trending/popular keywords.

---

## Deep Dive: Adobe Stock Analysis (March 2026)

### Upload Methods

From `contributor.stock.adobe.com` and `helpx.adobe.com/stock/contributor`:
- **Web portal only** — No API, no FTP, no SFTP, no CLI tool
- Sign up with Adobe ID (free)
- Upload through the contributor web portal
- 33% royalty on all sales
- Free Adobe Portfolio website for contributors
- Non-exclusive partnership (you keep rights)

### AI Content Requirements
- Must check "Created using generative AI tools" checkbox
- Must check "People and Property are fictional" if applicable
- NO artist names, real people, or IP in prompts/titles/keywords
- Cannot submit AI content to the Illustrative Editorial Collection

---

## Recommended Strategy for Automated AI Stock Submission

### Tier 1: Wirestock as Distribution Hub (Best Option)

**Wirestock** remains the best single-upload-point despite their pivot:

#### Step-by-Step Setup Instructions

1. **Create Account**
   - Go to https://wirestock.io/signup
   - Sign up with email or social login
   - Complete your profile (payment info for payouts)

2. **Upload Content**
   - Navigate to your portfolio/upload section
   - Wirestock supports: photos, videos, illustrations, 3D, AI art
   - **Batch upload** via the web portal (drag-and-drop multiple files)
   - Add metadata: title, description, keywords, categories

3. **Enable Distribution** (if still available)
   - In account settings, enable distribution to partner platforms
   - Wirestock historically distributed to: Shutterstock, Adobe Stock, Getty/iStock, Freepik, Dreamstime, Alamy, and others
   - Wirestock handles platform-specific metadata requirements
   - Wirestock handles AI disclosure flags per platform

4. **Participate in Paid Projects**
   - Browse available projects at https://wirestock.io/creators/jobs-projects
   - AI training data projects pay per accepted submission
   - Creative challenges pay cash prizes

5. **Earn Through Multiple Channels**
   - Stock licensing royalties (via partner platforms)
   - Dataset licensing deals (new program)
   - Paid project submissions
   - Creative challenge prizes
   - Monthly payouts

#### Automation for Wirestock Upload

Since Wirestock has no public API, automation options are:

**Option A: Selenium/Playwright Browser Automation (Medium Risk)**
```python
# Pseudocode — automate Wirestock web upload
from playwright.sync_api import sync_playwright

def upload_to_wirestock(image_path, metadata):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://wirestock.io/login")
        # Login
        page.fill('input[name="email"]', WIRESTOCK_EMAIL)
        page.fill('input[name="password"]', WIRESTOCK_PASSWORD)
        page.click('button[type="submit"]')
        # Navigate to upload
        page.goto("https://wirestock.io/upload")  # or equivalent
        # Upload file
        page.set_input_files('input[type="file"]', image_path)
        # Fill metadata
        page.fill('input[name="title"]', metadata['title'])
        # ... keywords, description, categories
        page.click('button[type="submit"]')
        browser.close()
```

**⚠️ Risks of browser automation:**
- May violate Wirestock's Terms of Service
- Fragile — breaks when UI changes
- Rate limiting / CAPTCHA issues
- Account suspension risk

**Option B: Discord Bot Integration (Low Risk, Limited)**
- Use the Wirestock Discord bot for Midjourney-style workflows
- Can potentially be scripted via Discord API (discord.py)
- Limited to one image at a time
- Must be triggered from Discord context

**Option C: Watch Folder + Manual Upload (Safest)**
```
1. Bot generates images → saves to data/stock_images/pending/
2. Bot generates metadata JSON alongside each image
3. Manually batch-upload to Wirestock periodically
4. Wirestock distributes to all partner platforms
```
This is the safest approach — generate images programmatically, upload manually in batches.

### Tier 2: Direct Manual Submission (Higher Effort)

For platforms that accept AI content but have no API:
- **Adobe Stock** — 33% royalty, manual portal upload
- **Shutterstock** — 15-40% royalty, manual portal or mobile app
- **Freepik** — Per-download pay, manual portal with batch upload
- **Dreamstime** — 25-60% royalty, manual portal upload
- **123RF** — 30-60% commission, manual portal upload
- **Pond5** — Set your own prices, manual portal upload
- **Depositphotos** — 34-42% royalty, manual portal upload

### Tier 3: Avoid (AI Content Banned)
- **Alamy** — Explicitly bans all AI content (despite having FTP upload)
- **iStock/Getty Images** — Explicitly bans all AI content
- **Stocksy** — Invite-only co-op, bans AI content

### Best Automation Strategy Summary

```
┌─────────────────────────────────────────────────┐
│          AI Image Generation Pipeline           │
│  (Leonardo → Stability → HuggingFace cascade)   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         Metadata Preparation                     │
│  • Title, description, 30+ keywords              │
│  • AI disclosure flags                           │
│  • Shutterstock CV API for keyword suggestions   │
│  • Category classification                       │
│  • EXIF embedding                                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         Output to Staging Folder                 │
│  data/stock_images/pending/                      │
│  ├── image_001.jpg                               │
│  ├── image_001.json  (metadata sidecar)          │
│  ├── image_002.jpg                               │
│  └── image_002.json                              │
└─────────────────┬───────────────────────────────┘
                  │
          ┌───────┴────────┐
          ▼                ▼
┌──────────────┐  ┌────────────────────┐
│  Wirestock   │  │  Direct Platforms  │
│  (batch      │  │  (manual upload    │
│   upload)    │  │   as supplement)   │
│              │  │                    │
│  Auto-       │  │  • Adobe Stock     │
│  distributes │  │  • Shutterstock    │
│  to 6+       │  │  • Freepik         │
│  platforms   │  │  • Dreamstime      │
└──────────────┘  └────────────────────┘
```

### Key Metadata Fields Needed (Universal)
When generating images for stock, always prepare:
- **Title** (descriptive, 5-200 characters)
- **Description** (detailed, what's in the image)
- **Keywords** (7-50 relevant tags)
- **Category** (platform-specific categories like Nature, Business, Technology)
- **AI disclosure flag** (required by all accepting platforms)
- **Model release** (if people are depicted)
- **Property release** (if recognizable property/brands)
- **Editorial vs. Commercial** designation
- **Content type** (photo, illustration, vector, video)

---

## Appendix: API & Automation Quick Reference

### Shutterstock API (Buyer-Side — Useful for Keyword Research)
```bash
# Get an API app: https://www.shutterstock.com/account/developers/apps
# Install CLI: pip install shutterstock-cli

# Suggest keywords for an image (useful for stock metadata)
RESPONSE=$(curl -X POST "https://api.shutterstock.com/v2/cv/images" \
  -H "Authorization: Bearer $SHUTTERSTOCK_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"base64_image\":\"`base64 myImage.jpg | tr -d '\n'`\"}")

UPLOAD_ID=$(echo $RESPONSE | jq -r .upload_id)

curl -X GET "https://api.shutterstock.com/v2/cv/keywords" \
  -H "Authorization: Bearer $SHUTTERSTOCK_API_TOKEN" \
  -G --data-urlencode "asset_id=$UPLOAD_ID"
# Returns: ["nature", "wildlife", "animal", "cute", "bamboo", ...]

# Search trending terms
curl -X GET "https://api.shutterstock.com/v2/images/search/suggestions" \
  -H "Authorization: Bearer $SHUTTERSTOCK_API_TOKEN" \
  -G --data-urlencode "query=remote work"
```

### Wirestock Discord Bot (Semi-Automation)
```
1. Add bot: https://discord.com/login?redirect_to=...wirestock-bot-oauth
2. /login <your_wirestock_discord_token>
3. On any image: More → Apps → Upscale & Publish
4. Bot upscales + publishes to Wirestock portfolio
```

### No Contributor Upload APIs Exist For:
- Adobe Stock (buyer-side only, Enterprise-restricted)
- Shutterstock (buyer-side only)
- Dreamstime (buyer/affiliate only)
- Freepik (no API at all)
- 123RF, Pond5, Depositphotos (no public APIs)
- Getty/iStock (ESP web portal only)

### No FTP/SFTP Upload Exists For:
- Adobe Stock ❌
- Shutterstock ❌ (removed years ago)
- Freepik ❌
- Dreamstime ❌
- 123RF ❌
- Pond5 ❌
- Only Alamy still has FTP, but they ban AI content ❌
