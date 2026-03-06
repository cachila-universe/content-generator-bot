"""Pinterest poster using Pinterest API v5 to create pins and drive traffic to articles."""

import os
import io
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_PIN_WIDTH = 1000
_PIN_HEIGHT = 1500  # 2:3 ratio — optimal for Pinterest
_BG_COLOR = (13, 17, 23)
_ACCENT_COLOR = (0, 255, 136)
_TEXT_COLOR = (255, 255, 255)
_SUBTEXT_COLOR = (180, 180, 180)
_CARD_COLOR = (22, 27, 34)


def create_pin(article: dict, niche_config: dict, site_url: str) -> "str | None":
    """
    Create a Pinterest pin for a published article.

    Generates a pin image with Pillow, uploads it to Pinterest via API v5,
    and returns the pin URL on success.  Returns None if Pinterest is not
    configured or if creation fails.
    """
    access_token = os.getenv("PINTEREST_ACCESS_TOKEN", "")
    board_id = os.getenv("PINTEREST_BOARD_ID", "")

    if not access_token or not board_id:
        logger.info("Pinterest not configured (PINTEREST_ACCESS_TOKEN / PINTEREST_BOARD_ID) — skipping")
        return None

    try:
        import requests
    except ImportError:
        logger.error("requests package not installed")
        return None

    title = article.get("title", "Untitled")
    slug = article.get("slug", "untitled")
    niche_id = article.get("niche_id", "")
    meta_description = article.get("meta_description", "")

    article_url = f"{site_url.rstrip('/')}/{niche_id}/{slug}.html" if niche_id else site_url
    niche_name = niche_config.get("name", "")

    # 1. Generate pin image
    pin_image_path = _generate_pin_image(title, niche_name, meta_description)

    # 2. Upload image to Pinterest media endpoint
    media_id = _upload_media(access_token, pin_image_path, requests)
    if pin_image_path:
        try:
            Path(pin_image_path).unlink(missing_ok=True)
        except Exception:
            pass

    # 3. Create the pin
    try:
        pin_url = _create_pin_api(
            access_token=access_token,
            board_id=board_id,
            title=title,
            description=_build_pin_description(article, niche_config),
            link=article_url,
            media_id=media_id,
            requests_lib=requests,
        )
        if pin_url:
            logger.info("Pinterest pin created: %s", pin_url)
        return pin_url
    except Exception as exc:
        logger.error("Pinterest pin creation failed: %s", exc)
        return None


# ── Image generation ─────────────────────────────────────────────────────────


def _generate_pin_image(title: str, niche_name: str, description: str) -> "str | None":
    """Generate a 1000×1500 pin image and return the path to a temp JPEG file."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (_PIN_WIDTH, _PIN_HEIGHT), color=_BG_COLOR)
        draw = ImageDraw.Draw(img)

        # ── Background accent bar at top ──────────────────────────────────
        draw.rectangle([(0, 0), (_PIN_WIDTH, 8)], fill=_ACCENT_COLOR)

        # ── Niche badge ───────────────────────────────────────────────────
        badge_font = _load_font(28)
        badge_text = f"  {niche_name}  "
        badge_x, badge_y = 60, 50
        badge_w = len(badge_text) * 17
        draw.rounded_rectangle(
            [(badge_x, badge_y), (badge_x + badge_w, badge_y + 42)],
            radius=8,
            fill=_ACCENT_COLOR,
        )
        draw.text((badge_x + 8, badge_y + 7), badge_text, font=badge_font, fill=_BG_COLOR)

        # ── Decorative card in middle ─────────────────────────────────────
        card_top = 140
        card_bottom = _PIN_HEIGHT - 200
        draw.rounded_rectangle(
            [(40, card_top), (_PIN_WIDTH - 40, card_bottom)],
            radius=16,
            fill=_CARD_COLOR,
        )

        # ── Title text ────────────────────────────────────────────────────
        title_font = _load_font(54)
        _draw_wrapped(draw, title, title_font, _TEXT_COLOR, 80, card_top + 60, _PIN_WIDTH - 160, line_spacing=16)

        # ── Separator line ────────────────────────────────────────────────
        sep_y = card_top + 60 + _estimate_text_height(draw, title, title_font, _PIN_WIDTH - 160, 16) + 30
        draw.rectangle([(80, sep_y), (_PIN_WIDTH - 80, sep_y + 2)], fill=_ACCENT_COLOR)

        # ── Description excerpt ───────────────────────────────────────────
        desc_font = _load_font(30)
        desc_text = (description[:220] + "…") if len(description) > 220 else description
        _draw_wrapped(draw, desc_text, desc_font, _SUBTEXT_COLOR, 80, sep_y + 28, _PIN_WIDTH - 160, line_spacing=12)

        # ── CTA strip at bottom of card ───────────────────────────────────
        cta_font = _load_font(32)
        cta_y = card_bottom - 80
        draw.rounded_rectangle(
            [(80, cta_y), (_PIN_WIDTH - 80, cta_y + 52)],
            radius=8,
            fill=_ACCENT_COLOR,
        )
        cta_text = "Read Full Article →"
        draw.text((_PIN_WIDTH // 2 - 90, cta_y + 10), cta_text, font=cta_font, fill=_BG_COLOR)

        # ── Bottom accent bar ─────────────────────────────────────────────
        draw.rectangle([(0, _PIN_HEIGHT - 8), (_PIN_WIDTH, _PIN_HEIGHT)], fill=_ACCENT_COLOR)

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".jpg", prefix="pin_")
        os.close(tmp_fd)
        img.save(tmp_path, "JPEG", quality=92, optimize=True)
        return tmp_path

    except ImportError:
        logger.warning("Pillow not installed — cannot generate pin image")
        return None
    except Exception as exc:
        logger.warning("Pin image generation failed: %s", exc)
        return None


def _draw_wrapped(
    draw,
    text: str,
    font,
    color: tuple,
    x: int,
    y: int,
    max_width: int,
    line_spacing: int = 12,
    max_lines: int = 8,
) -> int:
    """Draw word-wrapped text; returns the final y position."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    cy = y
    for line in lines[:max_lines]:
        draw.text((x, cy), line, font=font, fill=color)
        bbox = draw.textbbox((x, cy), line, font=font)
        cy += (bbox[3] - bbox[1]) + line_spacing
    return cy


def _estimate_text_height(draw, text: str, font, max_width: int, line_spacing: int) -> int:
    """Estimate the pixel height of wrapped text without drawing it."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))

    if not lines:
        return 0
    sample_bbox = draw.textbbox((0, 0), lines[0], font=font)
    line_h = sample_bbox[3] - sample_bbox[1]
    return len(lines) * (line_h + line_spacing)


def _load_font(size: int):
    """Load a truetype font with fallback to default."""
    from PIL import ImageFont

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


# ── Pinterest API helpers ─────────────────────────────────────────────────────


def _upload_media(access_token: str, image_path: "str | None", requests_lib) -> "str | None":
    """
    Upload an image to Pinterest and return its media_id.

    Pinterest API v5 requires a two-step media upload:
    1. Register the upload → get upload_url + media_id
    2. PUT the image bytes to upload_url
    """
    if not image_path or not Path(image_path).exists():
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        # Step 1: register upload
        register_resp = requests_lib.post(
            "https://api.pinterest.com/v5/media",
            headers=headers,
            json={"media_type": "image"},
            timeout=15,
        )
        if register_resp.status_code not in (200, 201):
            logger.warning(
                "Pinterest media register failed: %d %s",
                register_resp.status_code,
                register_resp.text[:200],
            )
            return None

        register_data = register_resp.json()
        media_id = register_data.get("media_id")
        upload_url = register_data.get("upload_url")
        upload_parameters = register_data.get("upload_parameters", {})

        if not upload_url:
            logger.warning("Pinterest media register returned no upload_url")
            return None

        # Step 2: PUT image to the signed URL
        image_bytes = Path(image_path).read_bytes()
        put_headers = {k: v for k, v in upload_parameters.items()}
        put_resp = requests_lib.put(upload_url, data=image_bytes, headers=put_headers, timeout=30)

        if put_resp.status_code not in (200, 201, 204):
            logger.warning("Pinterest media upload PUT failed: %d", put_resp.status_code)
            return None

        logger.debug("Pinterest media uploaded: media_id=%s", media_id)
        return media_id

    except Exception as exc:
        logger.warning("Pinterest media upload error: %s", exc)
        return None


def _create_pin_api(
    access_token: str,
    board_id: str,
    title: str,
    description: str,
    link: str,
    media_id: "str | None",
    requests_lib,
) -> "str | None":
    """Call the Pinterest API v5 pins endpoint to create a pin."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    body: dict = {
        "board_id": board_id,
        "title": title[:100],
        "description": description[:500],
        "link": link,
    }

    if media_id:
        body["media_source"] = {
            "source_type": "media_id",
            "media_id": media_id,
        }
    else:
        # Fallback: use a plain text pin without image
        logger.warning("No media_id available — creating text-only pin")

    try:
        resp = requests_lib.post(
            "https://api.pinterest.com/v5/pins",
            headers=headers,
            json=body,
            timeout=20,
        )

        if resp.status_code in (200, 201):
            pin_data = resp.json()
            pin_id = pin_data.get("id", "")
            pin_url = f"https://www.pinterest.com/pin/{pin_id}/" if pin_id else None
            return pin_url

        logger.warning(
            "Pinterest pin creation failed: %d %s",
            resp.status_code,
            resp.text[:300],
        )
        return None

    except Exception as exc:
        logger.error("Pinterest API call failed: %s", exc)
        return None


# ── Description builder ───────────────────────────────────────────────────────


def _build_pin_description(article: dict, niche_config: dict) -> str:
    """Build a keyword-rich pin description (max 500 chars)."""
    meta = article.get("meta_description", "")
    tags = article.get("tags", [])
    seed_keywords = niche_config.get("seed_keywords", [])

    hashtags = " ".join(
        "#" + kw.replace(" ", "").replace("&", "and")[:25]
        for kw in (tags + seed_keywords)[:8]
        if kw.strip()
    )

    base = meta if meta else article.get("title", "")
    combined = f"{base}\n\n{hashtags}"
    return combined[:500]
