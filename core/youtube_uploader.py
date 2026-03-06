"""YouTube video uploader using Google API with OAuth2 authentication."""

import os
import json
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_TOKEN_PATH = _PROJECT_ROOT / "data" / "youtube_token.json"
_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def upload_video(video_path: Path, article: dict, niche_config: dict, channel_name: str) -> "str | None":
    """
    Upload a video to YouTube.

    Returns YouTube video URL on success, None if not configured or on failure.
    """
    secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "")
    if not secrets_file or not Path(secrets_file).exists():
        logger.info("YouTube client secrets not configured — skipping upload")
        return None

    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError as exc:
        logger.warning("Google API packages not installed: %s", exc)
        return None

    try:
        credentials = _get_credentials(secrets_file)
        if credentials is None:
            return None

        youtube = build("youtube", "v3", credentials=credentials)

        title = article.get("title", "Untitled Video")[:100]
        description = _build_description(article, niche_config)
        tags = _build_tags(article, niche_config)

        # Generate thumbnail
        thumb_path = _generate_thumbnail(article, niche_config)

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22",  # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024 * 5,
        )

        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            _, response = request.next_chunk()

        video_id = response.get("id", "")
        if not video_id:
            logger.error("Upload succeeded but no video ID returned")
            return None

        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        # Upload thumbnail if available
        if thumb_path and thumb_path.exists():
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(str(thumb_path), mimetype="image/jpeg"),
                ).execute()
            except Exception as exc:
                logger.warning("Thumbnail upload failed: %s", exc)

        logger.info("Video uploaded to YouTube: %s", youtube_url)
        return youtube_url

    except Exception as exc:
        err_str = str(exc)
        if "403" in err_str or "quotaExceeded" in err_str:
            logger.warning("YouTube quota exceeded — skipping upload")
        else:
            logger.error("YouTube upload failed: %s", exc)
        return None
    finally:
        if thumb_path and thumb_path.exists():
            try:
                thumb_path.unlink()
            except Exception:
                pass


def authenticate(secrets_file: str = "") -> bool:
    """
    Run the OAuth2 flow interactively to obtain and save YouTube credentials.
    Call this once from the terminal before using the bot.

    Usage:
        python -c "from core.youtube_uploader import authenticate; authenticate()"
    """
    if not secrets_file:
        secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")

    if not Path(secrets_file).exists():
        print(f"\n❌  client_secrets.json not found at: {Path(secrets_file).resolve()}")
        print("    1. Go to https://console.cloud.google.com/apis/credentials")
        print("    2. Create an OAuth 2.0 Client ID (Desktop app)")
        print("    3. Download and save as 'client_secrets.json' in the project root\n")
        return False

    creds = _get_credentials(secrets_file)
    if creds and creds.valid:
        print(f"\n✅  YouTube authentication successful!")
        print(f"    Token saved to: {_TOKEN_PATH}\n")
        return True
    else:
        print("\n❌  Authentication failed. Check your client_secrets.json and try again.\n")
        return False


def _get_credentials(secrets_file: str):
    """Load or refresh OAuth2 credentials."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        creds = None
        if _TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), _SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(secrets_file, _SCOPES)
                creds = flow.run_local_server(port=0)

            _TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            _TOKEN_PATH.write_text(creds.to_json())

        return creds
    except Exception as exc:
        logger.error("Failed to obtain YouTube credentials: %s", exc)
        return None


def _build_description(article: dict, niche_config: dict) -> str:
    """Build YouTube video description."""
    import re

    title = article.get("title", "")
    meta_desc = article.get("meta_description", "")
    affiliate_programs = niche_config.get("affiliate_programs", [])

    lines = [
        title,
        "",
        meta_desc,
        "",
        "─────────────────────────────",
        "🔗 LINKS MENTIONED:",
        "",
    ]

    for prog in affiliate_programs[:5]:
        lines.append(f"• {prog.get('name', '')}: {prog.get('url', '')}")

    lines += [
        "",
        "─────────────────────────────",
        "⚠️ DISCLAIMER: This video may contain affiliate links. "
        "We may earn a commission if you purchase through our links at no extra cost to you.",
        "",
        "#affiliate #review #guide",
    ]

    return "\n".join(lines)[:5000]


def _build_tags(article: dict, niche_config: dict) -> list:
    """Build YouTube tags list (max 500 chars total)."""
    tags = list(article.get("tags", []))
    seed_keywords = niche_config.get("seed_keywords", [])
    tags.extend(seed_keywords)

    # Deduplicate
    seen = set()
    unique_tags = []
    total_chars = 0
    for tag in tags:
        tag_clean = tag.strip()[:50]
        if tag_clean.lower() not in seen and total_chars + len(tag_clean) < 480:
            seen.add(tag_clean.lower())
            unique_tags.append(tag_clean)
            total_chars += len(tag_clean)

    return unique_tags


def _generate_thumbnail(article: dict, niche_config: dict) -> "Path | None":
    """Generate a 1280x720 thumbnail image with Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (1280, 720), color=(13, 17, 23))
        draw = ImageDraw.Draw(img)

        # Accent bar at top
        draw.rectangle([(0, 0), (1280, 8)], fill=(0, 255, 136))

        title = article.get("title", "")[:80]
        niche_name = niche_config.get("name", "")

        # Load fonts
        title_font = _get_thumbnail_font(60)
        badge_font = _get_thumbnail_font(28)

        # Draw title
        _thumb_draw_wrapped(draw, title, title_font, (255, 255, 255), 80, 160, 1120)

        # Niche badge
        badge_text = f"  {niche_name}  "
        draw.rectangle([(80, 600), (80 + len(badge_text) * 16, 645)], fill=(0, 255, 136))
        draw.text((88, 607), badge_text, font=badge_font, fill=(13, 17, 23))

        # Accent bar at bottom
        draw.rectangle([(0, 712), (1280, 720)], fill=(0, 255, 136))

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
        os.close(tmp_fd)
        tmp = Path(tmp_path)
        img.save(str(tmp), "JPEG", quality=90)
        return tmp
    except Exception as exc:
        logger.warning("Thumbnail generation failed: %s", exc)
        return None


def _get_thumbnail_font(size: int):
    """Load a PIL font for thumbnails."""
    from PIL import ImageFont

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _thumb_draw_wrapped(draw, text: str, font, color: tuple, x: int, y: int, max_width: int) -> None:
    """Draw word-wrapped text on thumbnail."""
    words = text.split()
    lines = []
    current = []
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
    for line in lines[:4]:
        draw.text((x, cy), line, font=font, fill=color)
        bbox = draw.textbbox((x, cy), line, font=font)
        cy += (bbox[3] - bbox[1]) + 12
