"""
Stock Image Submitter — Prepares and exports AI images for stock platforms.

NO stock photo platform offers a contributor upload API.
This module prepares images with platform-optimised metadata and exports
them to a structured staging directory for batch upload.

Supported platforms (all accept AI-generated content with disclosure):
  1. Wirestock     — distribution hub → auto-sends to Adobe, Shutterstock, Freepik, etc.
  2. Adobe Stock   — 33% commission, manual upload via contributor portal
  3. Shutterstock  — 15-40% commission, manual upload
  4. Freepik       — contributor program, manual upload
  5. Dreamstime    — 25-60% commission, manual upload
  6. 123RF         — 30-60% commission, manual upload
  7. Pond5         — 50-60% commission, you set prices, manual upload
  8. Depositphotos — 34-42% commission, manual upload

Platforms that BAN AI content (do NOT upload):
  ✗ Alamy
  ✗ iStock / Getty Images
  ✗ Stocksy

Flow:
  1. Pick unsubmitted images from DB (status = 'generated')
  2. Generate platform-specific metadata (title, description, keywords, category)
  3. Copy to data/stock_exports/<platform>/ with metadata sidecar files
  4. Update DB status to 'exported'
  5. User uploads batch to each platform (manual step)
  6. User marks as 'submitted' in dashboard (updates DB + tracks revenue)
"""

import json
import shutil
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_DB_PATH = _PROJECT_ROOT / "data" / "bot.db"
_EXPORT_DIR = _PROJECT_ROOT / "data" / "stock_exports"

# ── Platform configuration ────────────────────────────────────────────────

PLATFORMS = {
    "wirestock": {
        "name": "Wirestock",
        "url": "https://wirestock.io/upload",
        "commission": "Varies (distributes to 6+ platforms)",
        "accepts_ai": True,
        "ai_disclosure": "Mark as AI-generated during upload",
        "max_keywords": 50,
        "max_title_len": 200,
        "max_desc_len": 500,
        "categories": [
            "Abstract", "Animals", "Architecture", "Backgrounds", "Business",
            "Education", "Food", "Health", "Nature", "People", "Science",
            "Sports", "Technology", "Travel", "Other",
        ],
        "export_format": "jpg",
        "min_resolution": "1024x1024",
        "signup_url": "https://wirestock.io/signup",
        "setup_steps": [
            "Go to https://wirestock.io/signup",
            "Create account with email",
            "Complete profile and add payment info (PayPal or bank)",
            "Upload images via drag-and-drop (batch supported)",
            "Enable distribution to partner platforms in settings",
            "Images auto-distribute to Adobe Stock, Shutterstock, Freepik, etc.",
        ],
    },
    "adobe_stock": {
        "name": "Adobe Stock",
        "url": "https://contributor.stock.adobe.com/",
        "commission": "33% per sale",
        "accepts_ai": True,
        "ai_disclosure": "Check '[AI generated]' checkbox during upload",
        "max_keywords": 49,
        "max_title_len": 200,
        "max_desc_len": 200,
        "categories": [
            "Animals", "Buildings and Architecture", "Business", "Drinks",
            "Environment", "Feelings Emotions and Mental States", "Food",
            "Graphic Resources", "Hobbies and Leisure", "Industry",
            "Landscapes", "Lifestyle", "People", "Plants and Flowers",
            "Science", "Social Issues", "Sports", "Technology",
            "Transport", "Travel",
        ],
        "export_format": "jpg",
        "min_resolution": "1600x1600",
        "signup_url": "https://contributor.stock.adobe.com/",
        "setup_steps": [
            "Go to https://contributor.stock.adobe.com/",
            "Sign in with Adobe ID (or create one — free)",
            "Complete contributor profile",
            "Add tax information (W-9 for US, W-8BEN for non-US)",
            "Add payment method (PayPal or Skrill)",
            "Upload images via web portal",
            "IMPORTANT: Check the 'AI generated' checkbox for every image",
        ],
    },
    "shutterstock": {
        "name": "Shutterstock",
        "url": "https://submit.shutterstock.com/",
        "commission": "15-40% (tiered by lifetime earnings)",
        "accepts_ai": True,
        "ai_disclosure": "Select 'AI generated' content type during upload",
        "max_keywords": 50,
        "max_title_len": 200,
        "max_desc_len": 200,
        "categories": [
            "Abstract", "Animals/Wildlife", "Arts", "Backgrounds/Textures",
            "Beauty/Fashion", "Buildings/Landmarks", "Business/Finance",
            "Celebrities", "Education", "Food and Drink", "Healthcare/Medical",
            "Holidays", "Industrial", "Interiors", "Miscellaneous",
            "Nature", "Objects", "Parks/Outdoor", "People", "Religion",
            "Science", "Signs/Symbols", "Sports/Recreation", "Technology",
            "Transportation", "Vintage",
        ],
        "export_format": "jpg",
        "min_resolution": "1000x1000",
        "signup_url": "https://submit.shutterstock.com/signup",
        "setup_steps": [
            "Go to https://submit.shutterstock.com/signup",
            "Create contributor account",
            "Verify email and complete profile",
            "Submit tax information",
            "Add payment info (PayPal, Payoneer, or check)",
            "Upload images via web portal",
            "Select 'AI generated' as content type for each image",
        ],
    },
    "freepik": {
        "name": "Freepik",
        "url": "https://contributor.freepik.com/",
        "commission": "Up to 50% per sale",
        "accepts_ai": True,
        "ai_disclosure": "Tag as AI-generated during upload",
        "max_keywords": 50,
        "max_title_len": 200,
        "max_desc_len": 500,
        "categories": [
            "Abstract", "Animals", "Architecture", "Arts and Entertainment",
            "Beauty", "Business", "Education", "Food", "Health",
            "Nature", "People", "Science", "Sports", "Technology", "Travel",
        ],
        "export_format": "jpg",
        "min_resolution": "1000x1000",
        "signup_url": "https://contributor.freepik.com/",
        "setup_steps": [
            "Go to https://contributor.freepik.com/",
            "Click 'Become a contributor'",
            "Create account or sign in",
            "Complete profile and portfolio review (may take days)",
            "Once approved, upload images via contributor dashboard",
            "Mark as AI-generated during upload",
        ],
    },
    "dreamstime": {
        "name": "Dreamstime",
        "url": "https://www.dreamstime.com/sell-stock-photos",
        "commission": "25-60% per sale",
        "accepts_ai": True,
        "ai_disclosure": "Check 'AI-generated' box in upload form",
        "max_keywords": 50,
        "max_title_len": 200,
        "max_desc_len": 200,
        "categories": [
            "Abstract", "Animals", "Architecture", "Arts", "Business",
            "Editorial", "Education", "Food and Drink", "Health",
            "Holidays", "Industrial", "IT and C", "Miscellaneous",
            "Nature", "Objects", "People", "Religion", "Science",
            "Sports", "Technology", "Travel",
        ],
        "export_format": "jpg",
        "min_resolution": "1600x1600",
        "signup_url": "https://www.dreamstime.com/register",
        "setup_steps": [
            "Go to https://www.dreamstime.com/register",
            "Create free contributor account",
            "Complete profile and tax info",
            "Upload images via web interface",
            "Check 'AI-generated' checkbox per image",
            "Minimum payout: $100 (PayPal, Moneybookers, check)",
        ],
    },
    "pond5": {
        "name": "Pond5",
        "url": "https://www.pond5.com/sell-media",
        "commission": "50-60% (you set your own prices!)",
        "accepts_ai": True,
        "ai_disclosure": "Label as AI-generated in description",
        "max_keywords": 50,
        "max_title_len": 200,
        "max_desc_len": 500,
        "categories": [
            "Abstract", "Animals", "Architecture", "Business",
            "Education", "Food", "Healthcare", "Holidays",
            "Industry", "Nature", "People", "Religion",
            "Science", "Sports", "Technology", "Transportation", "Travel",
        ],
        "export_format": "jpg",
        "min_resolution": "1000x1000",
        "signup_url": "https://www.pond5.com/sell-media",
        "setup_steps": [
            "Go to https://www.pond5.com/sell-media",
            "Click 'Start Selling'",
            "Create account and complete artist profile",
            "Set your own prices per image (typically $5-$50)",
            "Upload via web portal",
            "Include AI disclosure in description field",
        ],
    },
    "depositphotos": {
        "name": "Depositphotos",
        "url": "https://depositphotos.com/sell-photos.html",
        "commission": "34-42% per sale",
        "accepts_ai": True,
        "ai_disclosure": "Mark as AI-generated in upload settings",
        "max_keywords": 50,
        "max_title_len": 200,
        "max_desc_len": 200,
        "categories": [
            "Abstract", "Animals", "Architecture", "Arts", "Business",
            "Celebrities", "Editorial", "Education", "Food",
            "Healthcare", "Holidays", "Industrial", "Nature",
            "Objects", "People", "Religion", "Science", "Signs/Symbols",
            "Sports", "Technology", "Transportation", "Travel",
        ],
        "export_format": "jpg",
        "min_resolution": "1600x1600",
        "signup_url": "https://depositphotos.com/sell-photos.html",
        "setup_steps": [
            "Go to https://depositphotos.com/sell-photos.html",
            "Click 'Become a Contributor'",
            "Create account and pass initial review (upload 5 sample images)",
            "Once approved, upload via contributor dashboard",
            "Mark as AI-generated",
        ],
    },
    "123rf": {
        "name": "123RF",
        "url": "https://www.123rf.com/contributors/",
        "commission": "30-60% per sale",
        "accepts_ai": True,
        "ai_disclosure": "Select AI-generated option during upload",
        "max_keywords": 50,
        "max_title_len": 200,
        "max_desc_len": 200,
        "categories": [
            "Abstract", "Animals", "Architecture", "Arts",
            "Business", "Education", "Food", "Health",
            "Holidays", "Industrial", "Nature", "Objects",
            "People", "Religion", "Science", "Sports",
            "Technology", "Transportation", "Travel",
        ],
        "export_format": "jpg",
        "min_resolution": "1000x1000",
        "signup_url": "https://www.123rf.com/contributors/",
        "setup_steps": [
            "Go to https://www.123rf.com/contributors/",
            "Click 'Start Contributing'",
            "Create account and complete tax info",
            "Upload images via web portal",
            "Select AI-generated content type",
        ],
    },
}

# Platforms that BAN AI content — never upload to these
BANNED_PLATFORMS = ["alamy", "istock", "getty", "stocksy"]

# ── Niche → stock platform category mapping ───────────────────────────────

NICHE_CATEGORIES = {
    "ai_tools": "Technology",
    "personal_finance": "Business",
    "health_biohacking": "Health",
    "home_tech": "Technology",
    "travel": "Travel",
    "pet_care": "Animals",
    "fitness_wellness": "Sports",
    "remote_work": "Business",
}


# ── Database helpers ──────────────────────────────────────────────────────

def _ensure_tables():
    """Ensure submission tracking tables exist."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS stock_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            status TEXT DEFAULT 'exported',
            submitted_at TEXT,
            approved_at TEXT,
            rejection_reason TEXT,
            sale_count INTEGER DEFAULT 0,
            total_earnings REAL DEFAULT 0.0,
            platform_asset_id TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES stock_images(id)
        );

        CREATE INDEX IF NOT EXISTS idx_submissions_image
        ON stock_submissions(image_id);

        CREATE INDEX IF NOT EXISTS idx_submissions_platform
        ON stock_submissions(platform);
    """)
    conn.commit()
    conn.close()


def _get_category_for_platform(niche_id: str, platform_id: str) -> str:
    """Map niche to the best matching category for a given platform."""
    generic = NICHE_CATEGORIES.get(niche_id, "Other")
    platform = PLATFORMS.get(platform_id, {})
    categories = platform.get("categories", [])

    # Try exact match
    if generic in categories:
        return generic

    # Try fuzzy match
    generic_lower = generic.lower()
    for cat in categories:
        if generic_lower in cat.lower() or cat.lower() in generic_lower:
            return cat

    # Fallback
    return categories[-1] if categories else "Other"


def _generate_metadata(image: dict, platform_id: str) -> dict:
    """Generate platform-optimised metadata for an image."""
    platform = PLATFORMS.get(platform_id, {})
    max_title = platform.get("max_title_len", 200)
    max_desc = platform.get("max_desc_len", 200)
    max_kw = platform.get("max_keywords", 50)

    title = image.get("title", "AI Generated Stock Image")[:max_title]
    description = image.get("description", "")[:max_desc]
    keywords = image.get("keywords", "")

    # Parse keywords
    if isinstance(keywords, str):
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    else:
        kw_list = list(keywords) if keywords else []

    # Ensure AI disclosure keywords are always present
    ai_keywords = ["ai generated", "artificial intelligence", "ai art", "generative ai"]
    for ak in ai_keywords:
        if ak not in [k.lower() for k in kw_list]:
            kw_list.append(ak)

    # Add niche-specific keywords
    niche_id = image.get("niche_id", "")
    niche_keywords = {
        "ai_tools": ["technology", "software", "artificial intelligence", "productivity"],
        "personal_finance": ["money", "investment", "finance", "budgeting"],
        "health_biohacking": ["health", "wellness", "biohacking", "supplement"],
        "home_tech": ["smart home", "iot", "home automation", "gadget"],
        "travel": ["travel", "destination", "adventure", "tourism"],
        "pet_care": ["pet", "animal", "dog", "cat", "pet care"],
        "fitness_wellness": ["fitness", "workout", "gym", "exercise", "health"],
        "remote_work": ["remote work", "home office", "productivity", "workspace"],
    }
    for nk in niche_keywords.get(niche_id, []):
        if nk not in [k.lower() for k in kw_list]:
            kw_list.append(nk)

    kw_list = kw_list[:max_kw]

    category = _get_category_for_platform(niche_id, platform_id)

    return {
        "title": title,
        "description": description,
        "keywords": kw_list,
        "category": category,
        "ai_generated": True,
        "ai_disclosure": platform.get("ai_disclosure", "Mark as AI-generated"),
        "content_type": "photo",
        "editorial": False,
        "model_release": False,
        "property_release": False,
    }


# ── Export functions ──────────────────────────────────────────────────────

def export_for_platform(image: dict, platform_id: str) -> Optional[dict]:
    """
    Export a single image for a specific platform.

    Creates:
      data/stock_exports/<platform>/<filename>.jpg
      data/stock_exports/<platform>/<filename>.json   (metadata sidecar)

    Returns export info dict or None on failure.
    """
    if platform_id not in PLATFORMS:
        logger.warning("Unknown platform: %s", platform_id)
        return None

    platform = PLATFORMS[platform_id]
    _ensure_tables()

    src_path = Path(image.get("filepath", ""))
    if not src_path.exists():
        logger.warning("Image file not found: %s", src_path)
        return None

    # Create export directory
    export_dir = _EXPORT_DIR / platform_id
    export_dir.mkdir(parents=True, exist_ok=True)

    # Copy image
    filename = image.get("filename", src_path.name)
    dest_path = export_dir / filename
    shutil.copy2(str(src_path), str(dest_path))

    # Generate and save metadata
    metadata = _generate_metadata(image, platform_id)
    metadata_path = export_dir / f"{Path(filename).stem}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # Record in DB
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        """INSERT INTO stock_submissions (image_id, platform, status, submitted_at)
           VALUES (?, ?, 'exported', ?)""",
        (image.get("id", 0), platform_id, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    logger.info("Exported %s for %s → %s", filename, platform["name"], dest_path)

    return {
        "image_id": image.get("id"),
        "platform": platform_id,
        "platform_name": platform["name"],
        "export_path": str(dest_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
    }


def export_batch(images: list[dict], platform_ids: Optional[list[str]] = None) -> list[dict]:
    """
    Export a batch of images for all (or specified) platforms.

    Args:
        images: list of image dicts from stock_generator.get_all_stock_images()
        platform_ids: specific platforms, or None for all

    Returns list of export results.
    """
    if platform_ids is None:
        platform_ids = list(PLATFORMS.keys())

    results = []
    for image in images:
        for pid in platform_ids:
            try:
                result = export_for_platform(image, pid)
                if result:
                    results.append(result)
            except Exception as exc:
                logger.warning("Failed to export image %s for %s: %s",
                               image.get("id"), pid, exc)

    logger.info("Exported %d images across %d platforms", len(images), len(platform_ids))
    return results


def export_unsubmitted(platform_ids: Optional[list[str]] = None) -> list[dict]:
    """Export all images that haven't been exported yet."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row

    # Get images not yet exported
    rows = conn.execute("""
        SELECT si.* FROM stock_images si
        WHERE si.status = 'generated'
        AND si.id NOT IN (
            SELECT DISTINCT image_id FROM stock_submissions
        )
        ORDER BY si.generated_at DESC
    """).fetchall()
    conn.close()

    images = [dict(r) for r in rows]
    if not images:
        logger.info("No unsubmitted images to export")
        return []

    return export_batch(images, platform_ids)


# ── Submission tracking ───────────────────────────────────────────────────

def mark_submitted(image_id: int, platform: str):
    """Mark an image as submitted to a platform (user clicked 'Mark Submitted')."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        """UPDATE stock_submissions SET status = 'submitted', updated_at = ?
           WHERE image_id = ? AND platform = ?""",
        (datetime.now().isoformat(), image_id, platform),
    )
    # Also update the main stock_images table
    conn.execute(
        "UPDATE stock_images SET status = 'submitted' WHERE id = ?",
        (image_id,),
    )
    conn.commit()
    conn.close()


def mark_approved(image_id: int, platform: str, platform_asset_id: str = ""):
    """Mark an image as approved on a platform."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        """UPDATE stock_submissions
           SET status = 'approved', approved_at = ?, platform_asset_id = ?, updated_at = ?
           WHERE image_id = ? AND platform = ?""",
        (datetime.now().isoformat(), platform_asset_id,
         datetime.now().isoformat(), image_id, platform),
    )
    conn.commit()
    conn.close()


def mark_rejected(image_id: int, platform: str, reason: str = ""):
    """Mark an image as rejected on a platform."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        """UPDATE stock_submissions
           SET status = 'rejected', rejection_reason = ?, updated_at = ?
           WHERE image_id = ? AND platform = ?""",
        (reason, datetime.now().isoformat(), image_id, platform),
    )
    conn.commit()
    conn.close()


def record_sale(image_id: int, platform: str, amount: float):
    """Record a sale for an image on a platform."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        """UPDATE stock_submissions
           SET sale_count = sale_count + 1,
               total_earnings = total_earnings + ?,
               updated_at = ?
           WHERE image_id = ? AND platform = ?""",
        (amount, datetime.now().isoformat(), image_id, platform),
    )
    conn.commit()
    conn.close()


# ── Stats & reporting ─────────────────────────────────────────────────────

def get_submission_stats() -> dict:
    """Get submission statistics across all platforms."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row

    # Per-platform stats
    platform_stats = {}
    for pid in PLATFORMS:
        row = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'exported' THEN 1 ELSE 0 END) as exported,
                SUM(CASE WHEN status = 'submitted' THEN 1 ELSE 0 END) as submitted,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(sale_count) as sales,
                SUM(total_earnings) as earnings
            FROM stock_submissions WHERE platform = ?
        """, (pid,)).fetchone()

        platform_stats[pid] = {
            "name": PLATFORMS[pid]["name"],
            "total": row["total"] or 0,
            "exported": row["exported"] or 0,
            "submitted": row["submitted"] or 0,
            "approved": row["approved"] or 0,
            "rejected": row["rejected"] or 0,
            "sales": row["sales"] or 0,
            "earnings": round(row["earnings"] or 0, 2),
        }

    # Totals
    totals = conn.execute("""
        SELECT
            COUNT(DISTINCT image_id) as images_exported,
            SUM(sale_count) as total_sales,
            SUM(total_earnings) as total_earnings
        FROM stock_submissions
    """).fetchone()

    conn.close()

    return {
        "platforms": platform_stats,
        "totals": {
            "images_exported": totals["images_exported"] or 0,
            "total_sales": totals["total_sales"] or 0,
            "total_earnings": round(totals["total_earnings"] or 0, 2),
        },
    }


def get_image_submissions(image_id: int) -> list[dict]:
    """Get all submissions for a specific image."""
    _ensure_tables()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM stock_submissions WHERE image_id = ? ORDER BY platform",
        (image_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_platform_info() -> dict:
    """Return platform configuration for dashboard display."""
    return {
        pid: {
            "name": p["name"],
            "url": p["url"],
            "commission": p["commission"],
            "accepts_ai": p["accepts_ai"],
            "ai_disclosure": p["ai_disclosure"],
            "signup_url": p["signup_url"],
            "setup_steps": p["setup_steps"],
        }
        for pid, p in PLATFORMS.items()
    }
