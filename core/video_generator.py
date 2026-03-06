"""Video generator that creates YouTube-style videos from article content using MoviePy and Pillow."""

import os
import re
import logging
import tempfile
import shutil
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 1280, 720
BG_COLOR = (13, 17, 23)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 255, 136)
FONT_TITLE_SIZE = 56
FONT_BODY_SIZE = 34
FONT_H2_SIZE = 44
FPS = 24


def generate_video(article: dict, output_path: Path) -> "Path | None":
    """
    Generate a video from article content.

    Uses Pillow (NOT ImageMagick) for cross-platform compatibility.
    Returns output_path on success, None on failure.
    """
    try:
        from moviepy.editor import (
            ImageClip,
            AudioFileClip,
            concatenate_videoclips,
            CompositeVideoClip,
        )
        from gtts import gTTS
    except ImportError as exc:
        logger.error("Missing video dependency: %s", exc)
        return None

    tmp_dir = Path(tempfile.mkdtemp(prefix="videogen_"))
    try:
        slides = _extract_slides(article)
        if not slides:
            logger.error("No slides could be extracted from article")
            return None

        clips = []
        for i, slide in enumerate(slides):
            audio_path = tmp_dir / f"audio_{i}.mp3"

            # Generate TTS audio
            try:
                tts = gTTS(text=slide["narration"], lang="en", slow=False)
                tts.save(str(audio_path))
            except Exception as exc:
                logger.warning("TTS failed for slide %d: %s — using silent clip", i, exc)
                audio_path = None

            # Build image frame
            img_array = _build_slide_image(slide)
            img_path = tmp_dir / f"frame_{i}.png"
            Image.fromarray(img_array).save(str(img_path))

            # Build video clip
            if audio_path and audio_path.exists():
                audio_clip = AudioFileClip(str(audio_path))
                duration = audio_clip.duration + 0.5
                video_clip = ImageClip(img_array).set_duration(duration).set_audio(audio_clip)
            else:
                duration = max(4.0, len(slide["narration"]) / 15)
                video_clip = ImageClip(img_array).set_duration(duration)

            video_clip = video_clip.fadein(0.3).fadeout(0.3)
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
            verbose=False,
            logger=None,
        )
        logger.info("Video generated: %s", output_path)
        return output_path

    except Exception as exc:
        logger.error("Video generation failed: %s", exc)
        return None
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


def _extract_slides(article: dict) -> list:
    """Extract slide content from article HTML."""
    html = article.get("html_content", "")
    title = article.get("title", "Untitled")
    site_url = os.getenv("SITE_URL", "http://localhost:8080")

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

        # Skip FAQ section in slides
        if "faq" in heading.lower() or "question" in heading.lower():
            continue

        # Extract first sentence of body
        body_text = re.sub(r"<[^>]+>", " ", body_html).strip()
        body_text = re.sub(r"\s+", " ", body_text)
        first_sentence = body_text.split(".")[0].strip() + "." if "." in body_text else body_text[:200]

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
        "body": f"Visit us at {site_url}",
        "narration": f"For more tips and guides, visit us at {site_url}",
    })

    return slides


def _build_slide_image(slide: dict) -> np.ndarray:
    """Build a 1280x720 slide image as numpy array using Pillow."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load a system font; fall back to default
    font_title = _get_font(FONT_TITLE_SIZE)
    font_body = _get_font(FONT_BODY_SIZE)
    font_h2 = _get_font(FONT_H2_SIZE)

    slide_type = slide.get("type", "content")
    heading = slide.get("heading", "")
    body = slide.get("body", "")

    if slide_type == "title":
        # Accent line at top
        draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT_COLOR)

        # Title text centered
        _draw_wrapped_text(draw, heading, font_title, TEXT_COLOR, 80, 150, WIDTH - 160)

        # Subtitle body text
        if body:
            _draw_wrapped_text(draw, body, font_body, (180, 180, 180), 80, 380, WIDTH - 160)

        # Accent line at bottom
        draw.rectangle([(0, HEIGHT - 6), (WIDTH, HEIGHT)], fill=ACCENT_COLOR)

    elif slide_type == "cta":
        draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT_COLOR)
        _draw_wrapped_text(draw, heading, font_h2, ACCENT_COLOR, 80, 200, WIDTH - 160)
        if body:
            _draw_wrapped_text(draw, body, font_body, TEXT_COLOR, 80, 350, WIDTH - 160)
        draw.rectangle([(0, HEIGHT - 6), (WIDTH, HEIGHT)], fill=ACCENT_COLOR)

    else:
        # Content slide: H2 heading in green, body in white
        draw.rectangle([(0, 0), (WIDTH, 6)], fill=ACCENT_COLOR)
        _draw_wrapped_text(draw, heading, font_h2, ACCENT_COLOR, 80, 100, WIDTH - 160)
        # Separator line
        draw.rectangle([(80, 200), (WIDTH - 80, 203)], fill=(48, 54, 61))
        if body:
            _draw_wrapped_text(draw, body, font_body, TEXT_COLOR, 80, 230, WIDTH - 160)

    return np.array(img)


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    color: tuple,
    x: int,
    y: int,
    max_width: int,
    line_spacing: int = 12,
) -> None:
    """Draw word-wrapped text onto a PIL ImageDraw object."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=color)
        bbox = draw.textbbox((x, current_y), line, font=font)
        line_height = bbox[3] - bbox[1]
        current_y += line_height + line_spacing

        if current_y > HEIGHT - 80:
            break


def _get_font(size: int):
    """Load a PIL font, falling back to default if no system fonts available."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()
