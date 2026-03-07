"""
YouTube Shorts / Instagram Reels / TikTok generator — vertical 9:16 ≤60s.

Features:
  • Edge TTS neural voices (rotated per article)
  • Visual theme & layout rotation (never the same look twice)
  • Optimised for Shorts, Reels, and TikTok re-upload
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

WIDTH, HEIGHT = 1080, 1920  # 9:16 vertical
FPS = 30
MAX_DURATION = 58  # stay under 60s limit

# ── Voice pool ────────────────────────────────────────────────────────────
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

# ── Theme pool ────────────────────────────────────────────────────────────
THEMES = [
    {"name": "neon_green",   "bg": (13, 17, 23),  "text": (255, 255, 255), "accent": (0, 255, 136),   "sub": (180, 180, 180), "sep": (48, 54, 61)},
    {"name": "ocean_blue",   "bg": (15, 23, 42),  "text": (248, 250, 252), "accent": (96, 165, 250),  "sub": (148, 163, 184), "sep": (51, 65, 85)},
    {"name": "warm_amber",   "bg": (28, 18, 8),   "text": (255, 247, 237), "accent": (251, 191, 36),  "sub": (194, 175, 148), "sep": (68, 52, 28)},
    {"name": "violet_dream", "bg": (20, 10, 32),  "text": (250, 245, 255), "accent": (192, 132, 252), "sub": (168, 148, 194), "sep": (55, 35, 75)},
    {"name": "rose_red",     "bg": (24, 10, 12),  "text": (255, 241, 242), "accent": (251, 113, 133), "sub": (190, 150, 155), "sep": (65, 30, 38)},
    {"name": "mint_teal",    "bg": (10, 25, 28),  "text": (240, 253, 250), "accent": (45, 212, 191),  "sub": (148, 194, 188), "sep": (35, 65, 60)},
    {"name": "coral_pop",    "bg": (26, 14, 16),  "text": (255, 245, 247), "accent": (244, 114, 100), "sub": (190, 155, 150), "sep": (60, 35, 38)},
    {"name": "sky_cyan",     "bg": (10, 20, 28),  "text": (230, 245, 255), "accent": (34, 211, 238),  "sub": (140, 180, 200), "sep": (30, 50, 65)},
]

# ── Layout pool ───────────────────────────────────────────────────────────
LAYOUTS = ["bold_center", "numbered_card", "side_stripe", "top_gradient"]


def _pick(pool: list, seed: str, offset: int = 0):
    h = int(hashlib.md5((seed + str(offset)).encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def _tts(text: str, voice: str, out_path: Path) -> "Path | None":
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
    try:
        from gtts import gTTS
        gTTS(text=text, lang="en", slow=False).save(str(out_path))
        return out_path
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  Main entry
# ═══════════════════════════════════════════════════════════════════════════
def generate_short(article: dict, output_path: Path) -> "Path | None":
    """
    Generate a vertical short-form video (≤60 sec) from article content.

    Works for YouTube Shorts, Instagram Reels, and TikTok.
    Returns output_path on success, None on failure.
    """
    try:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, vfx
    except ImportError as exc:
        logger.error("Missing moviepy: %s", exc)
        return None

    slug = article.get("slug", "short")
    voice = _pick(VOICES, slug, offset=10)
    theme = _pick(THEMES, slug, offset=11)
    layout = _pick(LAYOUTS, slug, offset=12)
    logger.info("Short style → voice=%s  theme=%s  layout=%s", voice, theme["name"], layout)

    tmp_dir = Path(tempfile.mkdtemp(prefix="shortgen_"))
    try:
        slides = _extract_short_slides(article)
        if not slides:
            logger.error("No slides extracted for Short")
            return None

        clips = []
        total_duration = 0.0

        for i, slide in enumerate(slides):
            if total_duration >= MAX_DURATION:
                break

            audio_path = tmp_dir / f"audio_{i}.mp3"
            audio_file = _tts(slide["narration"], voice, audio_path)

            img_array = _build_short_slide(slide, theme, layout)

            if audio_file and audio_file.exists():
                audio_clip = AudioFileClip(str(audio_file))
                duration = min(audio_clip.duration + 0.3, MAX_DURATION - total_duration)
                video_clip = ImageClip(img_array, duration=duration).with_audio(audio_clip)
            else:
                duration = min(4.0, MAX_DURATION - total_duration)
                video_clip = ImageClip(img_array, duration=duration)

            video_clip = video_clip.with_effects([vfx.FadeIn(0.2), vfx.FadeOut(0.2)])
            clips.append(video_clip)
            total_duration += duration

        if not clips:
            logger.error("No clips generated for Short")
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
        )
        logger.info("Short generated: %s (%.1fs, voice=%s, theme=%s)",
                     output_path, total_duration, voice, theme["name"])
        return output_path

    except Exception as exc:
        logger.error("Short generation failed: %s", exc)
        return None
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Slide extraction
# ═══════════════════════════════════════════════════════════════════════════
def _extract_short_slides(article: dict) -> list:
    """Extract 3-5 punchy slides for a Short from article HTML."""
    html = article.get("html_content", "")
    title = article.get("title", "Untitled")

    slides = []

    # Slide 1: Hook
    hook = title
    if not hook.endswith("?"):
        hook = f"Did you know? {title}"
    slides.append({
        "type": "hook",
        "heading": hook,
        "body": "",
        "narration": hook,
    })

    # Slides 2-4: Key points from H2 sections
    h2_pattern = re.compile(r"<h2>(.*?)</h2>(.*?)(?=<h2>|$)", re.DOTALL)
    point_num = 1
    for match in h2_pattern.finditer(html):
        heading = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        body_html = match.group(2)

        if any(skip in heading.lower() for skip in ["faq", "question", "ready to", "get started"]):
            continue

        body_text = re.sub(r"<[^>]+>", " ", body_html).strip()
        body_text = re.sub(r"\s+", " ", body_text)
        first_sentence = body_text.split(".")[0].strip() + "." if "." in body_text else body_text[:150]

        slides.append({
            "type": "point",
            "heading": f"#{point_num}: {heading}",
            "body": first_sentence[:200],
            "narration": f"Number {point_num}. {heading}. {first_sentence[:200]}",
        })
        point_num += 1
        if len(slides) >= 4:
            break

    # Final slide: CTA
    slides.append({
        "type": "cta",
        "heading": "Follow for more! 🔔",
        "body": "Link in bio →",
        "narration": "Follow for more tips and subscribe!",
    })

    return slides


# ═══════════════════════════════════════════════════════════════════════════
#  Frame rendering
# ═══════════════════════════════════════════════════════════════════════════
def _build_short_slide(slide: dict, theme: dict, layout: str) -> np.ndarray:
    """Build a 1080x1920 vertical slide image."""
    bg = theme["bg"]
    tc = theme["text"]
    ac = theme["accent"]
    sc = theme["sub"]
    sep = theme["sep"]

    img = Image.new("RGB", (WIDTH, HEIGHT), color=bg)
    draw = ImageDraw.Draw(img)

    stype = slide.get("type", "point")
    heading = slide.get("heading", "")
    body = slide.get("body", "")

    fb = _get_font(64)   # big
    fm = _get_font(44)   # medium
    fs = _get_font(36)   # small

    if layout == "bold_center":
        _layout_bold_center(draw, stype, heading, body, fb, fm, fs, tc, ac, sc, sep)
    elif layout == "numbered_card":
        _layout_numbered_card(draw, stype, heading, body, fb, fm, fs, tc, ac, sc, sep)
    elif layout == "side_stripe":
        _layout_side_stripe(draw, stype, heading, body, fb, fm, fs, tc, ac, sc, sep)
    elif layout == "top_gradient":
        _layout_top_gradient(draw, img, stype, heading, body, fb, fm, fs, tc, ac, sc, sep)
    else:
        _layout_bold_center(draw, stype, heading, body, fb, fm, fs, tc, ac, sc, sep)

    return np.array(img)


# ── Layout renderers ──────────────────────────────────────────────────────
def _layout_bold_center(draw, stype, heading, body, fb, fm, fs, tc, ac, sc, sep):
    """Big bold text centered vertically."""
    draw.rectangle([(0, 0), (WIDTH, 8)], fill=ac)
    draw.rectangle([(0, HEIGHT - 8), (WIDTH, HEIGHT)], fill=ac)

    if stype == "hook":
        _draw_wrapped(draw, heading, fb, ac, 60, 700, WIDTH - 120, line_spacing=20)
    elif stype == "point":
        _draw_wrapped(draw, heading, fm, ac, 60, 600, WIDTH - 120, line_spacing=16)
        if body:
            draw.rectangle([(60, 800), (WIDTH - 60, 803)], fill=sep)
            _draw_wrapped(draw, body, fs, tc, 60, 840, WIDTH - 120)
    elif stype == "cta":
        _draw_wrapped(draw, heading, fb, tc, 60, 700, WIDTH - 120, line_spacing=20)
        draw.rounded_rectangle([(120, 920), (WIDTH - 120, 1000)], radius=12, fill=ac)
        _draw_wrapped(draw, body, fm, (13, 17, 23), 180, 938, WIDTH - 360)


def _layout_numbered_card(draw, stype, heading, body, fb, fm, fs, tc, ac, sc, sep):
    """Card-style with rounded rectangle background for content."""
    if stype == "hook":
        draw.rectangle([(0, 0), (WIDTH, 8)], fill=ac)
        _draw_wrapped(draw, heading, fb, ac, 60, 700, WIDTH - 120, line_spacing=20)
    elif stype == "point":
        # Card background
        draw.rounded_rectangle([(40, 540), (WIDTH - 40, 1100)], radius=24, fill=sep)
        _draw_wrapped(draw, heading, fm, ac, 80, 580, WIDTH - 160, line_spacing=16)
        if body:
            _draw_wrapped(draw, body, fs, tc, 80, 760, WIDTH - 160)
    elif stype == "cta":
        _draw_wrapped(draw, heading, fb, tc, 60, 650, WIDTH - 120, line_spacing=20)
        draw.rounded_rectangle([(120, 900), (WIDTH - 120, 980)], radius=12, fill=ac)
        _draw_wrapped(draw, body, fm, (13, 17, 23), 180, 918, WIDTH - 360)


def _layout_side_stripe(draw, stype, heading, body, fb, fm, fs, tc, ac, sc, sep):
    """Thick accent stripe on the left side."""
    draw.rectangle([(0, 0), (16, HEIGHT)], fill=ac)
    x = 60

    if stype == "hook":
        _draw_wrapped(draw, heading, fb, ac, x, 700, WIDTH - x - 60, line_spacing=20)
    elif stype == "point":
        _draw_wrapped(draw, heading, fm, ac, x, 600, WIDTH - x - 60, line_spacing=16)
        if body:
            draw.rectangle([(x, 800), (WIDTH - 60, 803)], fill=sep)
            _draw_wrapped(draw, body, fs, tc, x, 840, WIDTH - x - 60)
    elif stype == "cta":
        _draw_wrapped(draw, heading, fb, tc, x, 700, WIDTH - x - 60, line_spacing=20)
        if body:
            _draw_wrapped(draw, body, fm, ac, x, 900, WIDTH - x - 60)


def _layout_top_gradient(draw, img, stype, heading, body, fb, fm, fs, tc, ac, sc, sep):
    """Gradient accent at top of frame."""
    bg_pixel = img.getpixel((0, 0))
    for y in range(200):
        alpha = 1.0 - (y / 200)
        r = int(ac[0] * alpha + bg_pixel[0] * (1 - alpha))
        g = int(ac[1] * alpha + bg_pixel[1] * (1 - alpha))
        b = int(ac[2] * alpha + bg_pixel[2] * (1 - alpha))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    if stype == "hook":
        _draw_wrapped(draw, heading, fb, (255, 255, 255), 60, 50, WIDTH - 120, line_spacing=20)
    elif stype == "point":
        _draw_wrapped(draw, heading, fm, (255, 255, 255), 60, 40, WIDTH - 120, line_spacing=16)
        if body:
            _draw_wrapped(draw, body, fs, tc, 60, 700, WIDTH - 120)
    elif stype == "cta":
        _draw_wrapped(draw, heading, fb, (255, 255, 255), 60, 40, WIDTH - 120, line_spacing=20)
        if body:
            draw.rounded_rectangle([(120, 900), (WIDTH - 120, 980)], radius=12, fill=ac)
            _draw_wrapped(draw, body, fm, (13, 17, 23), 180, 918, WIDTH - 360)


# ═══════════════════════════════════════════════════════════════════════════
#  Drawing helpers
# ═══════════════════════════════════════════════════════════════════════════
def _draw_wrapped(draw, text, font, color, x, y, max_width, line_spacing=12, max_lines=8):
    """Draw word-wrapped text. Returns final y position."""
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
    for line in lines[:max_lines]:
        draw.text((x, cy), line, font=font, fill=color)
        bbox = draw.textbbox((x, cy), line, font=font)
        cy += (bbox[3] - bbox[1]) + line_spacing
    return cy


def _get_font(size: int):
    """Load a PIL font with fallback."""
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
