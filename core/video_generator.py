"""
Video generator — creates YouTube-style 16:9 videos from article content.

Features:
  • Microsoft Edge TTS neural voices (free, high-quality, no API key)
  • Voice rotation — different voice each video
  • Visual theme rotation — varied color schemes, layouts, accent styles
  • Pillow-based frame rendering (no ImageMagick needed)
  • MoviePy composition with fade transitions
"""

import os
import re
import asyncio
import logging
import tempfile
import shutil
import hashlib
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 1280, 720
FPS = 24

# ── Voice pool (Edge TTS neural voices, all English) ──────────────────────
VOICES = [
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-AriaNeural",
    "en-US-AvaNeural",
    "en-US-AndrewNeural",
    "en-US-EmmaNeural",
    "en-US-BrianNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-MichelleNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "en-GB-ThomasNeural",
    "en-AU-NatashaNeural",
    "en-CA-ClaraNeural",
    "en-CA-LiamNeural",
]

# ── Visual theme pool ─────────────────────────────────────────────────────
THEMES = [
    {
        "name": "cyber_green",
        "bg": (13, 17, 23),
        "text": (255, 255, 255),
        "accent": (0, 255, 136),
        "subtitle": (180, 180, 180),
        "separator": (48, 54, 61),
    },
    {
        "name": "royal_blue",
        "bg": (15, 23, 42),
        "text": (248, 250, 252),
        "accent": (96, 165, 250),
        "subtitle": (148, 163, 184),
        "separator": (51, 65, 85),
    },
    {
        "name": "sunset_orange",
        "bg": (28, 12, 8),
        "text": (255, 247, 237),
        "accent": (251, 146, 60),
        "subtitle": (194, 165, 148),
        "separator": (68, 45, 32),
    },
    {
        "name": "electric_purple",
        "bg": (20, 10, 32),
        "text": (250, 245, 255),
        "accent": (192, 132, 252),
        "subtitle": (168, 148, 194),
        "separator": (55, 35, 75),
    },
    {
        "name": "crimson_fire",
        "bg": (24, 10, 12),
        "text": (255, 241, 242),
        "accent": (251, 113, 133),
        "subtitle": (190, 150, 155),
        "separator": (65, 30, 38),
    },
    {
        "name": "teal_wave",
        "bg": (10, 25, 28),
        "text": (240, 253, 250),
        "accent": (45, 212, 191),
        "subtitle": (148, 194, 188),
        "separator": (35, 65, 60),
    },
    {
        "name": "golden_dark",
        "bg": (22, 18, 10),
        "text": (255, 251, 235),
        "accent": (250, 204, 21),
        "subtitle": (194, 180, 148),
        "separator": (55, 48, 28),
    },
    {
        "name": "ice_slate",
        "bg": (15, 23, 36),
        "text": (226, 232, 240),
        "accent": (125, 211, 252),
        "subtitle": (148, 163, 184),
        "separator": (45, 55, 72),
    },
]

# ── Layout pool (slide arrangements) ──────────────────────────────────────
LAYOUTS = ["classic", "centered", "left_bar", "gradient_banner"]


# ── Deterministic selection from article slug ─────────────────────────────
def _pick(pool: list, seed: str, offset: int = 0):
    """Pick an item from pool based on a hash seed."""
    h = int(hashlib.md5((seed + str(offset)).encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def _tts_generate(text: str, voice: str, out_path: Path) -> "Path | None":
    """Sync wrapper around Edge TTS with gTTS fallback."""
    try:
        import edge_tts

        async def _gen():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(out_path))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_gen())
        finally:
            loop.close()

        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path
    except Exception as exc:
        logger.warning("Edge TTS failed (%s): %s — falling back to gTTS", voice, exc)

    # Fallback: gTTS
    try:
        from gtts import gTTS

        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(str(out_path))
        return out_path
    except Exception as exc:
        logger.warning("gTTS also failed: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  Main entry
# ═══════════════════════════════════════════════════════════════════════════
def generate_video(article: dict, output_path: Path) -> "Path | None":
    """
    Generate a 16:9 YouTube video from article content.

    Uses Edge TTS neural voices with automatic rotation and varied visual themes.
    Returns output_path on success, None on failure.
    """
    try:
        from moviepy import (
            ImageClip,
            AudioFileClip,
            concatenate_videoclips,
            vfx,
        )
    except ImportError as exc:
        logger.error("Missing moviepy: %s", exc)
        return None

    slug = article.get("slug", "video")
    voice = _pick(VOICES, slug, offset=0)
    theme = _pick(THEMES, slug, offset=1)
    layout = _pick(LAYOUTS, slug, offset=2)
    logger.info("Video style → voice=%s  theme=%s  layout=%s", voice, theme["name"], layout)

    tmp_dir = Path(tempfile.mkdtemp(prefix="videogen_"))
    try:
        slides = _extract_slides(article)
        if not slides:
            logger.error("No slides could be extracted from article")
            return None

        clips = []
        for i, slide in enumerate(slides):
            audio_path = tmp_dir / f"audio_{i}.mp3"
            audio_file = _tts_generate(slide["narration"], voice, audio_path)

            img_array = _build_slide_image(slide, theme, layout)
            if audio_file and audio_file.exists():
                audio_clip = AudioFileClip(str(audio_file))
                duration = audio_clip.duration + 0.5
                video_clip = (
                    ImageClip(img_array, duration=duration)
                    .with_audio(audio_clip)
                )
            else:
                duration = max(4.0, len(slide["narration"]) / 15)
                video_clip = ImageClip(img_array, duration=duration)

            video_clip = video_clip.with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.3)])
            clips.append(video_clip)

        if not clips:
            logger.error("No clips generated")
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
        )
        logger.info("Video generated: %s (voice=%s, theme=%s)", output_path, voice, theme["name"])
        return output_path

    except Exception as exc:
        logger.error("Video generation failed: %s", exc)
        return None
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Slide extraction
# ═══════════════════════════════════════════════════════════════════════════
def _extract_slides(article: dict) -> list:
    """Extract slide content from article HTML."""
    html = article.get("html_content", "")
    title = article.get("title", "Untitled")
    site_url = os.getenv("SITE_URL", "https://tech-life-insights.com")

    slides = []

    # Title slide
    intro_match = re.search(r"<p>(.*?)</p>", html, re.DOTALL)
    intro_text = re.sub(r"<[^>]+>", "", intro_match.group(1)).strip() if intro_match else ""
    slides.append({
        "type": "title",
        "heading": title,
        "body": intro_text[:200] if intro_text else "",
        "narration": f"{title}. {intro_text[:300]}" if intro_text else title,
    })

    # Content slides from H2 sections
    h2_pattern = re.compile(r"<h2>(.*?)</h2>(.*?)(?=<h2>|$)", re.DOTALL)
    for match in h2_pattern.finditer(html):
        heading = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        body_html = match.group(2)

        if any(skip in heading.lower() for skip in ["faq", "question", "frequently"]):
            continue

        body_text = re.sub(r"<[^>]+>", " ", body_html).strip()
        body_text = re.sub(r"\s+", " ", body_text)
        first_sentence = (
            body_text.split(".")[0].strip() + "." if "." in body_text else body_text[:200]
        )

        slides.append({
            "type": "content",
            "heading": heading,
            "body": first_sentence[:300],
            "narration": f"{heading}. {body_text[:400]}",
        })

        if len(slides) >= 6:
            break

    # CTA slide
    slides.append({
        "type": "cta",
        "heading": "Want to Learn More?",
        "body": f"Visit tech-life-insights.com",
        "narration": f"For more tips and guides, visit us at tech life insights dot com. "
                     f"Don't forget to like and subscribe!",
    })

    return slides


# ═══════════════════════════════════════════════════════════════════════════
#  Frame rendering (Pillow)
# ═══════════════════════════════════════════════════════════════════════════
def _build_slide_image(slide: dict, theme: dict, layout: str) -> np.ndarray:
    """Build a 1280x720 slide image with the given theme and layout."""
    bg = theme["bg"]
    text_color = theme["text"]
    accent = theme["accent"]
    subtitle = theme["subtitle"]
    separator = theme["separator"]

    img = Image.new("RGB", (WIDTH, HEIGHT), color=bg)
    draw = ImageDraw.Draw(img)

    slide_type = slide.get("type", "content")
    heading = slide.get("heading", "")
    body = slide.get("body", "")

    font_title = _get_font(54)
    font_h2 = _get_font(44)
    font_body = _get_font(32)
    font_small = _get_font(24)

    if layout == "classic":
        _render_classic(draw, slide_type, heading, body, font_title, font_h2, font_body,
                        text_color, accent, subtitle, separator)
    elif layout == "centered":
        _render_centered(draw, slide_type, heading, body, font_title, font_h2, font_body,
                         text_color, accent, subtitle, separator)
    elif layout == "left_bar":
        _render_left_bar(draw, slide_type, heading, body, font_title, font_h2, font_body,
                         text_color, accent, subtitle, separator)
    elif layout == "gradient_banner":
        _render_gradient_banner(draw, img, slide_type, heading, body, font_title, font_h2, font_body,
                                text_color, accent, subtitle, separator)
    else:
        _render_classic(draw, slide_type, heading, body, font_title, font_h2, font_body,
                        text_color, accent, subtitle, separator)

    return np.array(img)


def _render_classic(draw, stype, heading, body, ft, fh, fb, tc, ac, sc, sep):
    """Classic layout: accent bar top/bottom, content in middle."""
    draw.rectangle([(0, 0), (WIDTH, 6)], fill=ac)
    draw.rectangle([(0, HEIGHT - 6), (WIDTH, HEIGHT)], fill=ac)

    if stype == "title":
        _draw_wrapped_text(draw, heading, ft, tc, 80, 160, WIDTH - 160)
        if body:
            _draw_wrapped_text(draw, body, fb, sc, 80, 380, WIDTH - 160)
    elif stype == "cta":
        _draw_wrapped_text(draw, heading, fh, ac, 80, 220, WIDTH - 160)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, 80, 380, WIDTH - 160)
    else:
        _draw_wrapped_text(draw, heading, fh, ac, 80, 100, WIDTH - 160)
        draw.rectangle([(80, 210), (WIDTH - 80, 213)], fill=sep)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, 80, 240, WIDTH - 160)


def _render_centered(draw, stype, heading, body, ft, fh, fb, tc, ac, sc, sep):
    """Centered layout: content vertically centered, subtle accent circle."""
    cx, cy_center = WIDTH // 2, HEIGHT // 2
    draw.ellipse([(cx - 260, cy_center - 260), (cx + 260, cy_center + 260)],
                 outline=ac, width=2)

    if stype == "title":
        _draw_wrapped_text(draw, heading, ft, tc, 120, cy_center - 100, WIDTH - 240)
        if body:
            _draw_wrapped_text(draw, body, fb, sc, 120, cy_center + 60, WIDTH - 240)
    elif stype == "cta":
        _draw_wrapped_text(draw, heading, fh, ac, 120, cy_center - 60, WIDTH - 240)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, 120, cy_center + 60, WIDTH - 240)
    else:
        _draw_wrapped_text(draw, heading, fh, ac, 120, cy_center - 120, WIDTH - 240)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, 120, cy_center + 20, WIDTH - 240)


def _render_left_bar(draw, stype, heading, body, ft, fh, fb, tc, ac, sc, sep):
    """Left accent bar layout: thick colored bar on the left."""
    draw.rectangle([(0, 0), (12, HEIGHT)], fill=ac)
    x_offset = 60

    if stype == "title":
        _draw_wrapped_text(draw, heading, ft, tc, x_offset, 140, WIDTH - x_offset - 80)
        if body:
            _draw_wrapped_text(draw, body, fb, sc, x_offset, 360, WIDTH - x_offset - 80)
    elif stype == "cta":
        _draw_wrapped_text(draw, heading, fh, ac, x_offset, 200, WIDTH - x_offset - 80)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, x_offset, 380, WIDTH - x_offset - 80)
    else:
        _draw_wrapped_text(draw, heading, fh, ac, x_offset, 100, WIDTH - x_offset - 80)
        draw.rectangle([(x_offset, 210), (WIDTH - 80, 213)], fill=sep)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, x_offset, 240, WIDTH - x_offset - 80)


def _render_gradient_banner(draw, img, stype, heading, body, ft, fh, fb, tc, ac, sc, sep):
    """Top gradient banner with accent color fade."""
    bg_pixel = img.getpixel((0, 0))
    for y in range(120):
        alpha = 1.0 - (y / 120)
        r = int(ac[0] * alpha + bg_pixel[0] * (1 - alpha))
        g = int(ac[1] * alpha + bg_pixel[1] * (1 - alpha))
        b = int(ac[2] * alpha + bg_pixel[2] * (1 - alpha))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    if stype == "title":
        _draw_wrapped_text(draw, heading, ft, tc, 80, 180, WIDTH - 160)
        if body:
            _draw_wrapped_text(draw, body, fb, sc, 80, 400, WIDTH - 160)
    elif stype == "cta":
        _draw_wrapped_text(draw, heading, fh, (255, 255, 255), 80, 30, WIDTH - 160)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, 80, 380, WIDTH - 160)
    else:
        _draw_wrapped_text(draw, heading, fh, (255, 255, 255), 80, 30, WIDTH - 160)
        if body:
            _draw_wrapped_text(draw, body, fb, tc, 80, 250, WIDTH - 160)


# ═══════════════════════════════════════════════════════════════════════════
#  Drawing helpers
# ═══════════════════════════════════════════════════════════════════════════
def _draw_wrapped_text(draw, text, font, color, x, y, max_width, line_spacing=12):
    """Draw word-wrapped text onto a PIL ImageDraw object."""
    words = text.split()
    lines, current = [], []

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
    for line in lines:
        draw.text((x, cy), line, font=font, fill=color)
        bbox = draw.textbbox((x, cy), line, font=font)
        cy += (bbox[3] - bbox[1]) + line_spacing
        if cy > HEIGHT - 80:
            break


def _get_font(size: int):
    """Load a system font with fallback."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()
