"""
Shorts generator — vertical 9:16 fast-paced videos for YouTube Shorts,
Instagram Reels, TikTok, and Twitter.

Design principles:
  • FAST pacing — TTS at +20% speed, quick 0.15s fades
  • Relevant stock images from Pexels (portrait orientation)
  • Heavy dark overlay with bold centered text
  • Ken Burns zoom (10% — more dramatic than landscape)
  • Punchy hooks, numbered points, strong CTA
  • Max 58 seconds to stay under 60s limit
  • One output file works on all platforms
"""

import os
import re
import asyncio
import logging
import tempfile
import shutil
import hashlib
import yaml
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

WIDTH, HEIGHT = 1080, 1920  # 9:16 vertical
FPS = 30
MAX_DURATION = 58
_PROJECT_ROOT = Path(__file__).parent.parent

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

# ── Accent palette ────────────────────────────────────────────────────────
ACCENTS = [
    {"name": "blue",   "primary": (96, 165, 250),  "dark": (37, 99, 235)},
    {"name": "green",  "primary": (52, 211, 153),  "dark": (16, 185, 129)},
    {"name": "amber",  "primary": (251, 191, 36),  "dark": (217, 119, 6)},
    {"name": "purple", "primary": (192, 132, 252), "dark": (139, 92, 246)},
    {"name": "rose",   "primary": (251, 113, 133), "dark": (225, 29, 72)},
    {"name": "teal",   "primary": (45, 212, 191),  "dark": (20, 184, 166)},
]

KB_STYLES = ["zoom_in", "zoom_out", "pan_up", "pan_down"]


def _pick(pool, seed, offset=0):
    h = int(hashlib.md5((seed + str(offset)).encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def _load_pexels_key() -> str:
    try:
        cfg = yaml.safe_load((_PROJECT_ROOT / "config" / "settings.yaml").read_text())
        return cfg.get("video", {}).get("pexels_api_key", "") or ""
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════════════════
#  TTS (fast — +20% speed for shorts)
# ═══════════════════════════════════════════════════════════════════════════
def _tts_fast(text: str, voice: str, out_path: Path) -> "Path | None":
    """Generate speech at +20% speed for fast-paced shorts."""
    try:
        import edge_tts

        async def _gen():
            communicate = edge_tts.Communicate(text, voice, rate="+20%")
            await communicate.save(str(out_path))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_gen())
        finally:
            loop.close()

        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path
    except Exception as exc:
        logger.warning("Edge TTS failed: %s", exc)

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
    Generate a vertical short-form video (≤58s) from article content.

    Fast-paced, bold text, image backgrounds — one file for all platforms.
    Returns output_path on success, None on failure.
    """
    try:
        from moviepy import VideoClip, ImageClip, AudioFileClip, concatenate_videoclips, vfx
    except ImportError as exc:
        logger.error("Missing moviepy: %s", exc)
        return None

    slug = article.get("slug", "short")
    niche_name = article.get("niche_name", "")
    niche_id = article.get("niche_id", "")
    voice = _pick(VOICES, slug, offset=10)
    accent = _pick(ACCENTS, slug, offset=11)
    pexels_key = _load_pexels_key()

    logger.info(
        "Short style → voice=%s  accent=%s  images=%s",
        voice, accent["name"], "pexels" if pexels_key else "gradient",
    )

    tmp_dir = Path(tempfile.mkdtemp(prefix="shortgen_"))
    try:
        slides = _extract_short_slides(article)
        if not slides:
            logger.error("No slides extracted for Short")
            return None

        total_slides = len(slides)
        clips = []
        total_duration = 0.0

        for i, slide in enumerate(slides):
            if total_duration >= MAX_DURATION:
                break

            # 1. Fetch portrait image
            from core.image_fetcher import fetch_image, extract_search_query

            query = extract_search_query(slide["heading"], niche_name)
            bg_img = fetch_image(
                query, pexels_key, "portrait", WIDTH, HEIGHT, photo_index=i + 5,
                niche_id=niche_id,
            )

            # 2. Build frame
            frame = _build_short_frame(slide, bg_img, accent, i, total_slides)
            frame_array = np.array(frame)

            # 3. Fast TTS
            audio_path = tmp_dir / f"audio_{i}.mp3"
            audio_file = _tts_fast(slide["narration"], voice, audio_path)

            # 4. Create clip with Ken Burns
            if audio_file and audio_file.exists():
                audio_clip = AudioFileClip(str(audio_file))
                duration = min(audio_clip.duration + 0.3, MAX_DURATION - total_duration)
                clip = _make_ken_burns_clip(frame_array, duration, FPS, i)
                clip = clip.with_audio(audio_clip)
            else:
                duration = min(3.5, MAX_DURATION - total_duration)
                clip = _make_ken_burns_clip(frame_array, duration, FPS, i)

            # Quick fades for fast pacing
            clip = clip.with_effects([vfx.FadeIn(0.15), vfx.FadeOut(0.15)])
            clips.append(clip)
            total_duration += duration

        if not clips:
            logger.error("No clips generated for Short")
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        final = concatenate_videoclips(clips, method="compose")

        # Layer ambient background music under narration
        from core.music_generator import mix_music_into_video
        final = mix_music_into_video(
            final, niche_id=niche_id, slug=slug, variant=0, music_volume=0.08,
        )

        final.write_videofile(
            str(output_path), fps=FPS, codec="libx264", audio_codec="aac",
        )
        logger.info("Short generated: %s (%.1fs, voice=%s)", output_path, total_duration, voice)
        return output_path

    except Exception as exc:
        logger.error("Short generation failed: %s", exc)
        return None
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Ken Burns (more dramatic for shorts — 10% zoom)
# ═══════════════════════════════════════════════════════════════════════════
def _make_ken_burns_clip(frame_array, duration, fps, slide_index, amount=0.10):
    """Ken Burns with more dramatic zoom for shorts."""
    try:
        from moviepy import VideoClip

        h, w = frame_array.shape[:2]
        pil_source = Image.fromarray(frame_array)
        style = KB_STYLES[slide_index % len(KB_STYLES)]

        def make_frame(t):
            progress = max(0.0, min(1.0, t / max(duration, 0.01)))

            if style == "zoom_in":
                zoom = 1.0 + amount * progress
                cx, cy = w // 2, h // 2
            elif style == "zoom_out":
                zoom = 1.0 + amount * (1 - progress)
                cx, cy = w // 2, h // 2
            elif style == "pan_up":
                zoom = 1.0 + amount
                cx = w // 2
                cy = int(h * (0.55 - 0.10 * progress))
            else:  # pan_down
                zoom = 1.0 + amount
                cx = w // 2
                cy = int(h * (0.45 + 0.10 * progress))

            crop_w = min(int(w / zoom), w)
            crop_h = min(int(h / zoom), h)
            x1 = max(0, min(cx - crop_w // 2, w - crop_w))
            y1 = max(0, min(cy - crop_h // 2, h - crop_h))

            cropped = pil_source.crop((x1, y1, x1 + crop_w, y1 + crop_h))
            resized = cropped.resize((w, h), Image.LANCZOS)
            return np.array(resized)

        clip = VideoClip(make_frame, duration=duration)
        clip.fps = fps
        return clip

    except Exception:
        from moviepy import ImageClip
        return ImageClip(frame_array, duration=duration)


# ═══════════════════════════════════════════════════════════════════════════
#  Slide extraction (punchy, condensed)
# ═══════════════════════════════════════════════════════════════════════════
def _extract_short_slides(article: dict) -> list:
    """Extract 4-5 punchy slides for a Short from article content."""
    html = article.get("html_content", "")
    title = article.get("title", "Untitled")

    slides = []

    # ── Slide 1: Hook ─────────────────────────────────────────────
    hook = title
    if len(title) > 50:
        # Shorten for impact
        hook = title.split(":")[0].strip() if ":" in title else title[:50]
    if not hook.endswith("?"):
        hook = f"{hook} 🤯"

    slides.append({
        "type": "hook",
        "heading": hook,
        "body": "",
        "narration": f"Here's what you need to know about {title}",
    })

    # ── Slides 2-4: Key points ────────────────────────────────────
    h2_pattern = re.compile(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|$)", re.DOTALL)
    point_num = 1

    for match in h2_pattern.finditer(html):
        heading = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        # Strip markdown heading markers (e.g. "### Title" → "Title")
        heading = re.sub(r'^#{1,6}\s*', '', heading).strip()
        body_html = match.group(2)

        if any(skip in heading.lower()
               for skip in ["faq", "question", "frequently", "conclusion",
                            "summary", "ready", "get started"]):
            continue

        body_text = re.sub(r"<[^>]+>", " ", body_html).strip()
        body_text = re.sub(r"\s+", " ", body_text)

        # Just the first sentence — keep it punchy
        first_sentence = body_text.split(".")[0].strip()
        if first_sentence and not first_sentence.endswith("."):
            first_sentence += "."

        slides.append({
            "type": "point",
            "heading": heading,
            "number": point_num,
            "body": first_sentence[:180],
            "narration": f"Number {point_num}. {heading}. {first_sentence[:200]}",
        })
        point_num += 1

        if len(slides) >= 4:
            break

    # ── Final slide: CTA ──────────────────────────────────────────
    slides.append({
        "type": "cta",
        "heading": "Follow for more!",
        "body": "@tech-life-insights",
        "narration": "Follow for more insights and subscribe!",
    })

    return slides


# ═══════════════════════════════════════════════════════════════════════════
#  Frame composition (vertical, bold)
# ═══════════════════════════════════════════════════════════════════════════
def _build_short_frame(
    slide: dict,
    bg_img: "Image.Image | None",
    accent: dict,
    slide_index: int,
    total_slides: int,
) -> Image.Image:
    """Build a 1080×1920 vertical frame with image background."""
    if bg_img:
        frame = bg_img.copy().convert("RGB")
    else:
        frame = _generate_gradient_bg(WIDTH, HEIGHT, accent)

    frame = _apply_dark_overlay(frame, slide["type"])
    draw = ImageDraw.Draw(frame)

    stype = slide["type"]
    heading = slide.get("heading", "")
    body = slide.get("body", "")
    ac = accent["primary"]

    font_big = _get_font(72, "heavy")
    font_med = _get_font(48, "bold")
    font_body = _get_font(36, "medium")
    font_small = _get_font(28, "regular")
    font_num = _get_font(120, "heavy")
    font_brand = _get_font(22, "demibold")

    # ── Progress dots (top center) ────────────────────────────────
    dot_y = 100
    dot_spacing = 24
    total_w = total_slides * dot_spacing
    start_x = (WIDTH - total_w) // 2
    for d in range(total_slides):
        cx = start_x + d * dot_spacing + 6
        if d == slide_index:
            draw.ellipse([(cx - 6, dot_y - 6), (cx + 6, dot_y + 6)], fill=ac)
        else:
            draw.ellipse([(cx - 4, dot_y - 4), (cx + 4, dot_y + 4)], fill=(100, 100, 100))

    if stype == "hook":
        # Big bold hook text, centered vertically
        _draw_text_shadow(
            draw, heading, font_big, ac, 60, 680, WIDTH - 120,
            shadow_offset=3, line_spacing=18,
        )

    elif stype == "point":
        # Big number in accent color
        num_text = f"#{slide.get('number', slide_index)}"
        nbbox = draw.textbbox((0, 0), num_text, font=font_num)
        nw = nbbox[2] - nbbox[0]
        draw.text(((WIDTH - nw) // 2 + 3, 400 + 3), num_text, font=font_num, fill=(0, 0, 0))
        draw.text(((WIDTH - nw) // 2, 400), num_text, font=font_num, fill=ac)

        # Heading below number
        _draw_text_shadow(
            draw, heading, font_med, (255, 255, 255), 60, 620, WIDTH - 120,
            shadow_offset=3, line_spacing=14,
        )

        # Separator
        draw.rectangle([(60, 830), (240, 833)], fill=ac)

        # Body
        if body:
            _draw_text_shadow(
                draw, body, font_body, (210, 215, 225), 60, 870, WIDTH - 120,
                shadow_offset=2,
            )

    elif stype == "cta":
        # Big CTA text
        _draw_text_shadow(
            draw, heading, font_big, (255, 255, 255), 60, 650, WIDTH - 120,
            shadow_offset=3, line_spacing=18,
        )

        # Handle / username as button
        if body:
            bbox = draw.textbbox((0, 0), body, font=font_med)
            bw = bbox[2] - bbox[0]
            bh = bbox[3] - bbox[1]
            btn_x = (WIDTH - bw - 60) // 2
            btn_y = 880
            draw.rounded_rectangle(
                [(btn_x, btn_y), (btn_x + bw + 60, btn_y + bh + 30)],
                radius=12, fill=ac,
            )
            draw.text(
                (btn_x + 30, btn_y + 15), body,
                font=font_med, fill=(15, 23, 42),
            )

    # ── Brand watermark (bottom) ──────────────────────────────────
    brand = "TechLife Insights"
    bbox = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bbox[2] - bbox[0]
    _draw_text_shadow(
        draw, brand, font_brand, (90, 100, 115),
        (WIDTH - bw) // 2, HEIGHT - 120, WIDTH,
    )

    return frame


# ═══════════════════════════════════════════════════════════════════════════
#  Image helpers
# ═══════════════════════════════════════════════════════════════════════════
def _apply_dark_overlay(img: Image.Image, slide_type: str = "point") -> Image.Image:
    """Heavy dark overlay for vertical format — text must be very readable on phones."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size

    if slide_type == "hook":
        top_alpha, mid_alpha, bot_alpha = 0.30, 0.65, 0.75
    elif slide_type == "cta":
        top_alpha, mid_alpha, bot_alpha = 0.50, 0.75, 0.85
    else:
        top_alpha, mid_alpha, bot_alpha = 0.25, 0.60, 0.75

    for y in range(h):
        t = y / h
        if t < 0.15:
            alpha = top_alpha
        elif t < 0.35:
            alpha = top_alpha + (mid_alpha - top_alpha) * ((t - 0.15) / 0.20)
        elif t < 0.60:
            alpha = mid_alpha
        else:
            alpha = mid_alpha + (bot_alpha - mid_alpha) * ((t - 0.60) / 0.40)
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, int(255 * alpha)))

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _generate_gradient_bg(w: int, h: int, accent: dict) -> Image.Image:
    """Gradient background fallback for vertical format."""
    ac = accent["primary"]
    dark = (15, 23, 42)

    y_grad = np.linspace(0, 1, h).reshape(-1, 1)
    x_grad = np.linspace(0, 1, w).reshape(1, -1)
    t = np.clip((x_grad * 0.3 + y_grad * 0.7) * 0.30, 0, 1)

    r = np.clip(dark[0] + (ac[0] - dark[0]) * t, 0, 255).astype(np.uint8)
    g = np.clip(dark[1] + (ac[1] - dark[1]) * t, 0, 255).astype(np.uint8)
    b = np.clip(dark[2] + (ac[2] - dark[2]) * t, 0, 255).astype(np.uint8)

    return Image.fromarray(np.stack([r, g, b], axis=-1))


# ═══════════════════════════════════════════════════════════════════════════
#  Text helpers
# ═══════════════════════════════════════════════════════════════════════════
def _draw_text_shadow(
    draw, text: str, font, colour: tuple, x: int, y: int,
    max_width: int, shadow_offset: int = 2, line_spacing: int = 12,
) -> int:
    """Draw word-wrapped text with drop shadow. Returns final Y."""
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
    for line in lines[:6]:
        draw.text((x + shadow_offset, cy + shadow_offset), line, font=font, fill=(0, 0, 0))
        draw.text((x, cy), line, font=font, fill=colour)
        bbox = draw.textbbox((x, cy), line, font=font)
        cy += (bbox[3] - bbox[1]) + line_spacing
        if cy > HEIGHT - 140:
            break
    return cy


def _get_font(size: int, weight: str = "heavy"):
    """Load Avenir Next at the specified weight."""
    weight_map = {"regular": 0, "medium": 2, "demibold": 4, "bold": 6, "heavy": 8}
    idx = weight_map.get(weight, 8)

    for fp in [
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
    ]:
        try:
            return ImageFont.truetype(fp, size, index=idx)
        except (IOError, OSError):
            continue

    for fp in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()
