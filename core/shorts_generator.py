"""
YouTube Shorts generator — creates vertical 9:16 short-form videos (≤60 sec).

Much better reach than full-length videos. Can also be repurposed for
Instagram Reels and TikTok.
"""

import os
import re
import logging
import tempfile
import shutil
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 1080, 1920   # 9:16 vertical
BG_COLOR = (13, 17, 23)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 255, 136)
SUBTITLE_COLOR = (180, 180, 180)
FPS = 30
MAX_DURATION = 58  # stay under 60s limit


def generate_short(article: dict, output_path: Path) -> Path | None:
    """
    Generate a YouTube Short (vertical 9:16, ≤60 sec) from article content.

    Returns output_path on success, None on failure.
    """
    try:
        from moviepy.editor import (
            ImageClip,
            AudioFileClip,
            concatenate_videoclips,
        )
        from gtts import gTTS
    except ImportError as exc:
        logger.error("Missing video dependency: %s", exc)
        return None

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

            # Generate TTS narration
            try:
                tts = gTTS(text=slide["narration"], lang="en", slow=False)
                tts.save(str(audio_path))
            except Exception as exc:
                logger.warning("TTS failed for slide %d: %s", i, exc)
                audio_path = None

            # Build vertical slide image
            img_array = _build_short_slide(slide)

            # Create video clip
            if audio_path and audio_path.exists():
                audio_clip = AudioFileClip(str(audio_path))
                duration = min(audio_clip.duration + 0.3, MAX_DURATION - total_duration)
                video_clip = ImageClip(img_array).set_duration(duration).set_audio(audio_clip)
            else:
                duration = min(4.0, MAX_DURATION - total_duration)
                video_clip = ImageClip(img_array).set_duration(duration)

            video_clip = video_clip.fadein(0.2).fadeout(0.2)
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
            verbose=False,
            logger=None,
        )
        logger.info("YouTube Short generated: %s (%.1f sec)", output_path, total_duration)
        return output_path

    except Exception as exc:
        logger.error("Short generation failed: %s", exc)
        return None
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


def _extract_short_slides(article: dict) -> list:
    """Extract 3-5 punchy slides for a Short from article HTML."""
    html = article.get("html_content", "")
    title = article.get("title", "Untitled")

    slides = []

    # Slide 1: Hook (title as question/statement)
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

        # Skip FAQ and CTA sections
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


def _build_short_slide(slide: dict) -> np.ndarray:
    """Build a 1080x1920 vertical slide image."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    slide_type = slide.get("type", "point")
    heading = slide.get("heading", "")
    body = slide.get("body", "")

    font_big = _get_font(64)
    font_medium = _get_font(42)
    font_body = _get_font(36)

    # Top accent bar
    draw.rectangle([(0, 0), (WIDTH, 8)], fill=ACCENT_COLOR)

    if slide_type == "hook":
        # Big centered text
        _draw_wrapped(draw, heading, font_big, ACCENT_COLOR, 60, 600, WIDTH - 120, line_spacing=20)

    elif slide_type == "point":
        # Number/heading in accent
        _draw_wrapped(draw, heading, font_medium, ACCENT_COLOR, 60, 500, WIDTH - 120, line_spacing=16)
        # Separator
        sep_y = 700
        draw.rectangle([(60, sep_y), (WIDTH - 60, sep_y + 3)], fill=(48, 54, 61))
        # Body text
        if body:
            _draw_wrapped(draw, body, font_body, TEXT_COLOR, 60, sep_y + 40, WIDTH - 120, line_spacing=14)

    elif slide_type == "cta":
        # CTA with prominent button-like styling
        _draw_wrapped(draw, heading, font_big, TEXT_COLOR, 60, 650, WIDTH - 120, line_spacing=20)
        # "Button"
        btn_y = 900
        draw.rounded_rectangle(
            [(120, btn_y), (WIDTH - 120, btn_y + 80)],
            radius=12,
            fill=ACCENT_COLOR,
        )
        _draw_wrapped(draw, body, font_medium, BG_COLOR, 180, btn_y + 18, WIDTH - 360)

    # Bottom accent bar
    draw.rectangle([(0, HEIGHT - 8), (WIDTH, HEIGHT)], fill=ACCENT_COLOR)

    return np.array(img)


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    color: tuple,
    x: int,
    y: int,
    max_width: int,
    line_spacing: int = 12,
    max_lines: int = 8,
) -> int:
    """Draw word-wrapped text. Returns final y position."""
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


def _get_font(size: int):
    """Load a PIL font with fallback to default."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()
