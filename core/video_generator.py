"""
Video generator — YouTube landscape (16:9) with image backgrounds & TTS.

Two modes:
  1. Single-article video  (generate_video)   — one article → ~1-2 min video
  2. Weekly roundup video   (generate_roundup) — 3-7 articles → 5-10 min video
     "This Week in [Niche]" format for regular YouTube uploads.

Features:
  • Relevant stock images from Pexels on every slide
  • Dark gradient overlays for text readability
  • Ken Burns subtle zoom/pan for motion (not a static slideshow)
  • Professional text layout with drop shadows (Avenir Next)
  • Slide counter, progress bar, TechLife Insights watermark
  • Edge TTS neural voice rotation

If no Pexels API key is configured, falls back to gradient backgrounds.
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

WIDTH, HEIGHT = 1280, 720
FPS = 24
_PROJECT_ROOT = Path(__file__).parent.parent

# ── Voice pool (Edge TTS, all English) ────────────────────────────────────
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

# ── Accent colour palette (picked per video via slug hash) ────────────────
ACCENTS = [
    {"name": "blue",   "primary": (96, 165, 250),  "dark": (37, 99, 235)},
    {"name": "green",  "primary": (52, 211, 153),  "dark": (16, 185, 129)},
    {"name": "amber",  "primary": (251, 191, 36),  "dark": (217, 119, 6)},
    {"name": "purple", "primary": (192, 132, 252), "dark": (139, 92, 246)},
    {"name": "rose",   "primary": (251, 113, 133), "dark": (225, 29, 72)},
    {"name": "teal",   "primary": (45, 212, 191),  "dark": (20, 184, 166)},
]

# ── Ken Burns motion styles (cycled per slide) ───────────────────────────
KB_STYLES = ["zoom_in", "zoom_out", "pan_left", "pan_right"]


# ═══════════════════════════════════════════════════════════════════════════
#  Deterministic picks
# ═══════════════════════════════════════════════════════════════════════════
def _pick(pool: list, seed: str, offset: int = 0):
    h = int(hashlib.md5((seed + str(offset)).encode()).hexdigest(), 16)
    return pool[h % len(pool)]


# ═══════════════════════════════════════════════════════════════════════════
#  Settings helper
# ═══════════════════════════════════════════════════════════════════════════
def _load_pexels_key() -> str:
    try:
        cfg = yaml.safe_load((_PROJECT_ROOT / "config" / "settings.yaml").read_text())
        return cfg.get("video", {}).get("pexels_api_key", "") or ""
    except Exception:
        return ""


# ═══════════════════════════════════════════════════════════════════════════
#  TTS
# ═══════════════════════════════════════════════════════════════════════════
def _tts_generate(text: str, voice: str, out_path: Path, rate: str = "+0%") -> "Path | None":
    """Generate speech audio using Edge TTS with gTTS fallback."""
    try:
        import edge_tts

        async def _gen():
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(str(out_path))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(_gen())
        finally:
            loop.close()

        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path
    except Exception as exc:
        logger.warning("Edge TTS failed (%s): %s — trying gTTS", voice, exc)

    try:
        from gtts import gTTS
        gTTS(text=text, lang="en", slow=False).save(str(out_path))
        return out_path
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  Main entry
# ═══════════════════════════════════════════════════════════════════════════
def generate_video(article: dict, output_path: Path) -> "Path | None":
    """
    Generate a 16:9 YouTube video with image backgrounds and TTS narration.

    Returns output_path on success, None on failure.
    """
    try:
        from moviepy import VideoClip, ImageClip, AudioFileClip, concatenate_videoclips, vfx
    except ImportError as exc:
        logger.error("Missing moviepy: %s", exc)
        return None

    slug = article.get("slug", "video")
    niche_name = article.get("niche_name", "")
    niche_id = article.get("niche_id", "")
    voice = _pick(VOICES, slug, offset=0)
    accent = _pick(ACCENTS, slug, offset=1)
    pexels_key = _load_pexels_key()

    logger.info(
        "Video style → voice=%s  accent=%s  images=%s",
        voice, accent["name"], "ai-stock+pexels" if niche_id else ("pexels" if pexels_key else "gradient-fallback"),
    )

    tmp_dir = Path(tempfile.mkdtemp(prefix="videogen_"))
    try:
        slides = _extract_slides(article)
        if not slides:
            logger.error("No slides could be extracted from article")
            return None

        total_slides = len(slides)
        clips = []

        for i, slide in enumerate(slides):
            # 1. Fetch relevant image for this slide
            from core.image_fetcher import fetch_image, extract_search_query

            query = extract_search_query(slide["heading"], niche_name)
            bg_img = fetch_image(
                query, pexels_key, "landscape", WIDTH, HEIGHT, photo_index=i,
                niche_id=niche_id,
            )
            if bg_img:
                logger.info("  Slide %d/%d: image fetched for '%s'", i + 1, total_slides, query)
            else:
                logger.info("  Slide %d/%d: using gradient fallback", i + 1, total_slides)

            # 2. Compose the frame (image + overlay + text + decorations)
            frame = _build_frame(slide, bg_img, accent, i, total_slides)
            frame_array = np.array(frame)

            # 3. TTS audio
            audio_path = tmp_dir / f"audio_{i}.mp3"
            audio_file = _tts_generate(slide["narration"], voice, audio_path)

            # 4. Create video clip with Ken Burns motion
            if audio_file and audio_file.exists():
                audio_clip = AudioFileClip(str(audio_file))
                duration = audio_clip.duration + 0.5
                clip = _make_ken_burns_clip(frame_array, duration, FPS, i)
                clip = clip.with_audio(audio_clip)
            else:
                duration = max(4.0, len(slide["narration"]) / 15)
                clip = _make_ken_burns_clip(frame_array, duration, FPS, i)

            clip = clip.with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.3)])
            clips.append(clip)

        if not clips:
            logger.error("No clips generated")
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(output_path), fps=FPS, codec="libx264", audio_codec="aac",
        )
        logger.info("Video generated: %s (voice=%s, accent=%s)", output_path, voice, accent["name"])
        return output_path

    except Exception as exc:
        logger.error("Video generation failed: %s", exc)
        return None
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Weekly Roundup Video (multi-article, 5-10 min)
# ═══════════════════════════════════════════════════════════════════════════
def generate_roundup(
    articles: list,
    niche_name: str,
    niche_id: str,
    output_path: Path,
) -> "Path | None":
    """
    Generate a weekly roundup video combining multiple articles into one
    5-10 minute 16:9 landscape video.

    Format:
      • Intro slide   — "This Week in [Niche]" with article count
      • Per article    — Title card → 1-2 key-point slides
      • Outro CTA     — subscribe + website

    This is different from the Short (single article, 58s vertical).
    The roundup gives a conversational overview of the whole week.

    Returns output_path on success, None on failure.
    """
    if not articles:
        logger.warning("Roundup: no articles provided")
        return None

    try:
        from moviepy import VideoClip, ImageClip, AudioFileClip, concatenate_videoclips, vfx
    except ImportError as exc:
        logger.error("Missing moviepy: %s", exc)
        return None

    seed = f"roundup_{niche_id}_{len(articles)}"
    voice = _pick(VOICES, seed, offset=0)
    accent = _pick(ACCENTS, seed, offset=1)
    pexels_key = _load_pexels_key()

    logger.info(
        "Roundup video → niche=%s  articles=%d  voice=%s  accent=%s",
        niche_name, len(articles), voice, accent["name"],
    )

    tmp_dir = Path(tempfile.mkdtemp(prefix="roundup_"))
    try:
        slides = _extract_roundup_slides(articles, niche_name)
        if not slides:
            logger.error("Roundup: no slides extracted")
            return None

        total_slides = len(slides)
        clips = []

        for i, slide in enumerate(slides):
            # 1. Fetch relevant image
            from core.image_fetcher import fetch_image, extract_search_query

            search_hint = slide.get("search_query", slide["heading"])
            query = extract_search_query(search_hint, niche_name)
            bg_img = fetch_image(
                query, pexels_key, "landscape", WIDTH, HEIGHT, photo_index=i,
                niche_id=niche_id,
            )
            if bg_img:
                logger.info("  Roundup slide %d/%d: image for '%s'", i + 1, total_slides, query[:40])
            else:
                logger.info("  Roundup slide %d/%d: gradient fallback", i + 1, total_slides)

            # 2. Compose frame
            frame = _build_roundup_frame(slide, bg_img, accent, i, total_slides)
            frame_array = np.array(frame)

            # 3. TTS narration (normal speed for long-form — more conversational)
            audio_path = tmp_dir / f"roundup_audio_{i}.mp3"
            audio_file = _tts_generate(slide["narration"], voice, audio_path)

            # 4. Ken Burns clip
            if audio_file and audio_file.exists():
                audio_clip = AudioFileClip(str(audio_file))
                duration = audio_clip.duration + 0.8  # slight pause between slides
                clip = _make_ken_burns_clip(frame_array, duration, FPS, i, amount=0.04)
                clip = clip.with_audio(audio_clip)
            else:
                duration = max(5.0, len(slide["narration"]) / 12)
                clip = _make_ken_burns_clip(frame_array, duration, FPS, i, amount=0.04)

            clip = clip.with_effects([vfx.FadeIn(0.4), vfx.FadeOut(0.4)])
            clips.append(clip)

        if not clips:
            logger.error("Roundup: no clips generated")
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(output_path), fps=FPS, codec="libx264", audio_codec="aac",
        )
        logger.info(
            "Roundup video generated: %s (%d articles, %.1f min)",
            output_path, len(articles), final.duration / 60,
        )
        return output_path

    except Exception as exc:
        logger.error("Roundup video generation failed: %s", exc)
        return None
    finally:
        shutil.rmtree(str(tmp_dir), ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
#  Roundup slide extraction (multi-article)
# ═══════════════════════════════════════════════════════════════════════════
def _extract_roundup_slides(articles: list, niche_name: str) -> list:
    """
    Build slides for a weekly roundup from multiple articles.

    Structure:
      1  Intro          — "This Week in [Niche]" + article count
      N  Article cards  — per article: title card + 1-2 key points
      1  Outro CTA      — subscribe + website

    Each article gets 2-3 slides so the viewer gets the gist without
    watching each individual Short.
    """
    slides = []
    count = len(articles)
    week_label = "this week" if count <= 7 else f"these past {count} articles"

    # ── Intro slide ───────────────────────────────────────────────
    slides.append({
        "type": "roundup_intro",
        "heading": f"This Week in {niche_name}",
        "body": f"{count} {'story' if count == 1 else 'stories'} you need to know",
        "niche": niche_name,
        "search_query": f"{niche_name} weekly highlights",
        "narration": (
            f"Welcome to This Week in {niche_name} on TechLife Insights! "
            f"We've got {count} {'story' if count == 1 else 'stories'} to cover {week_label}. "
            f"Let's dive right in."
        ),
    })

    # ── Per-article segments ──────────────────────────────────────
    for idx, article in enumerate(articles):
        title = article.get("title", "Untitled")
        html = article.get("html_content", "")

        # Extract first paragraph as intro
        intro_match = re.search(r"<p[^>]*>(.*?)</p>", html, re.DOTALL)
        intro_text = re.sub(r"<[^>]+>", "", intro_match.group(1)).strip() if intro_match else ""

        # Article title card
        article_num = f"Story {idx + 1} of {count}"
        slides.append({
            "type": "roundup_article_title",
            "heading": title,
            "body": article_num,
            "niche": niche_name,
            "search_query": title,
            "narration": (
                f"{'First up' if idx == 0 else 'Next up' if idx < count - 1 else 'And finally'}, "
                f"story number {idx + 1}: {title}."
            ),
        })

        # Extract H2 key points for this article
        h2_pattern = re.compile(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|$)", re.DOTALL)
        key_points = []
        for match in h2_pattern.finditer(html):
            h2_text = re.sub(r"<[^>]+>", "", match.group(1)).strip()
            body_html = match.group(2)
            if any(skip in h2_text.lower()
                   for skip in ["faq", "question", "frequently", "conclusion", "summary"]):
                continue
            body_text = re.sub(r"<[^>]+>", " ", body_html).strip()
            body_text = re.sub(r"\s+", " ", body_text)
            sentences = [s.strip() for s in body_text.split(".") if len(s.strip()) > 20]
            key_points.append({
                "heading": h2_text,
                "summary": ". ".join(sentences[:2]) + "." if sentences else body_text[:200],
                "narration": ". ".join(sentences[:3]) + "." if sentences else body_text[:300],
            })
            if len(key_points) >= 2:
                break

        # Add 1-2 key point slides per article
        for kp in key_points:
            slides.append({
                "type": "roundup_key_point",
                "heading": kp["heading"],
                "body": kp["summary"][:280],
                "search_query": kp["heading"],
                "narration": f"{kp['heading']}. {kp['narration'][:400]}",
            })

        # If no H2 points found, use intro paragraph
        if not key_points and intro_text:
            slides.append({
                "type": "roundup_key_point",
                "heading": "Key Takeaway",
                "body": intro_text[:280],
                "search_query": title,
                "narration": intro_text[:400],
            })

    # ── Outro CTA ─────────────────────────────────────────────────
    slides.append({
        "type": "roundup_outro",
        "heading": f"That's a Wrap!",
        "body": (
            f"Read full articles at tech-life-insights.com"
        ),
        "niche": niche_name,
        "search_query": f"{niche_name} technology insights",
        "narration": (
            f"That's a wrap for This Week in {niche_name}! "
            f"For the full articles with all the details and links, "
            f"head over to tech life insights dot com. "
            f"If you found this helpful, hit that like button and subscribe "
            f"so you never miss a weekly roundup. See you next week!"
        ),
    })

    return slides


# ═══════════════════════════════════════════════════════════════════════════
#  Roundup frame composition
# ═══════════════════════════════════════════════════════════════════════════
def _build_roundup_frame(
    slide: dict,
    bg_img: "Image.Image | None",
    accent: dict,
    slide_index: int,
    total_slides: int,
) -> Image.Image:
    """Compose a roundup slide frame — slightly different layout than single-article."""
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

    font_title = _get_font(46, "heavy")
    font_h2 = _get_font(36, "bold")
    font_body = _get_font(24, "medium")
    font_small = _get_font(18, "regular")
    font_label = _get_font(20, "demibold")
    font_brand = _get_font(16, "demibold")

    if stype == "roundup_intro":
        # "WEEKLY ROUNDUP" badge
        _draw_badge(draw, "WEEKLY ROUNDUP", font_small, ac, 80, 80)

        # Big title
        _draw_text_shadow(draw, heading, font_title, (255, 255, 255), 80, 160, WIDTH - 160)

        # Subtitle (article count)
        if body:
            _draw_text_shadow(draw, body, font_body, (200, 210, 225), 80, 380, WIDTH - 160)

        # Decorative accent line
        draw.rectangle([(80, 350), (380, 353)], fill=ac)

    elif stype == "roundup_article_title":
        # Story number badge
        if body:
            _draw_badge(draw, body.upper(), font_small, ac, 80, 90)

        # Article title (big and bold)
        _draw_text_shadow(draw, heading, font_title, (255, 255, 255), 80, 170, WIDTH - 160)

        # Accent underline
        draw.rectangle([(80, 420), (300, 423)], fill=ac)

    elif stype == "roundup_key_point":
        # "KEY TAKEAWAY" label
        _draw_text_shadow(draw, "KEY TAKEAWAY", font_label, ac, 80, 70, WIDTH - 160)

        # Heading
        _draw_text_shadow(draw, heading, font_h2, (255, 255, 255), 80, 120, WIDTH - 160)

        # Separator
        draw.rectangle([(80, 265), (260, 268)], fill=ac)

        # Body text
        if body:
            _draw_text_shadow(draw, body, font_body, (220, 225, 235), 80, 295, WIDTH - 160)

    elif stype == "roundup_outro":
        # "THAT'S A WRAP" big text
        _draw_text_shadow(draw, heading, font_title, (255, 255, 255), 80, 180, WIDTH - 160)

        draw.rectangle([(80, 330), (380, 333)], fill=ac)

        if body:
            _draw_text_shadow(draw, body, font_body, ac, 80, 360, WIDTH - 160)

        _draw_text_shadow(
            draw, "Like & Subscribe for weekly roundups!",
            font_small, (180, 190, 200), 80, 460, WIDTH - 160,
        )

    else:
        # Fallback — treat like content
        _draw_text_shadow(draw, heading, font_h2, ac, 80, 120, WIDTH - 160)
        if body:
            _draw_text_shadow(draw, body, font_body, (225, 230, 240), 80, 280, WIDTH - 160)

    # ── Progress bar ──────────────────────────────────────────────
    progress = (slide_index + 1) / total_slides
    bar_y = HEIGHT - 4
    draw.rectangle([(0, bar_y), (int(WIDTH * progress), HEIGHT)], fill=ac)
    draw.rectangle([(int(WIDTH * progress), bar_y), (WIDTH, HEIGHT)], fill=(20, 20, 20))

    # ── Brand watermark ───────────────────────────────────────────
    brand = "TechLife Insights — Weekly Roundup"
    bbox = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bbox[2] - bbox[0]
    _draw_text_shadow(draw, brand, font_brand, (100, 110, 125), WIDTH - 80 - bw, HEIGHT - 35, 400)

    return frame


# ═══════════════════════════════════════════════════════════════════════════
#  Ken Burns (subtle zoom / pan on each slide)
# ═══════════════════════════════════════════════════════════════════════════
def _make_ken_burns_clip(frame_array: np.ndarray, duration: float, fps: int,
                         slide_index: int, amount: float = 0.06):
    """
    Create a clip with subtle Ken Burns zoom / pan for motion.

    Falls back to a static ImageClip if VideoClip creation fails.
    """
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
            elif style == "pan_left":
                zoom = 1.0 + amount
                cx = int(w * (0.55 - 0.10 * progress))
                cy = h // 2
            else:  # pan_right
                zoom = 1.0 + amount
                cx = int(w * (0.45 + 0.10 * progress))
                cy = h // 2

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

    except Exception as exc:
        logger.debug("Ken Burns unavailable (%s) — using static frame", exc)
        from moviepy import ImageClip
        return ImageClip(frame_array, duration=duration)


# ═══════════════════════════════════════════════════════════════════════════
#  Slide extraction
# ═══════════════════════════════════════════════════════════════════════════
def _extract_slides(article: dict) -> list:
    """Extract slides from article HTML for the landscape video."""
    html = article.get("html_content", "")
    title = article.get("title", "Untitled")
    niche_name = article.get("niche_name", "")

    slides = []

    # ── Title slide ───────────────────────────────────────────────
    intro_match = re.search(r"<p[^>]*>(.*?)</p>", html, re.DOTALL)
    intro = re.sub(r"<[^>]+>", "", intro_match.group(1)).strip() if intro_match else ""
    slides.append({
        "type": "title",
        "heading": title,
        "body": intro[:220] if intro else "",
        "niche": niche_name,
        "narration": f"{title}. {intro[:350]}" if intro else title,
    })

    # ── Content slides from H2 sections ───────────────────────────
    h2_pattern = re.compile(r"<h2[^>]*>(.*?)</h2>(.*?)(?=<h2|$)", re.DOTALL)
    for match in h2_pattern.finditer(html):
        heading = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        body_html = match.group(2)

        if any(skip in heading.lower()
               for skip in ["faq", "question", "frequently", "conclusion", "summary"]):
            continue

        body_text = re.sub(r"<[^>]+>", " ", body_html).strip()
        body_text = re.sub(r"\s+", " ", body_text)

        sentences = [s.strip() for s in body_text.split(".") if s.strip()]
        body_short = ". ".join(sentences[:2]) + "." if sentences else body_text[:250]
        narration = ". ".join(sentences[:4]) + "." if sentences else body_text[:500]

        slides.append({
            "type": "content",
            "heading": heading,
            "body": body_short[:300],
            "narration": f"{heading}. {narration[:500]}",
        })

        if len(slides) >= 7:
            break

    # ── CTA slide ─────────────────────────────────────────────────
    slides.append({
        "type": "cta",
        "heading": "Read the Full Article",
        "body": "tech-life-insights.com",
        "narration": (
            "For the complete article and more insights, "
            "visit tech life insights dot com. "
            "Don't forget to like and subscribe for more!"
        ),
    })

    return slides


# ═══════════════════════════════════════════════════════════════════════════
#  Frame composition
# ═══════════════════════════════════════════════════════════════════════════
def _build_frame(
    slide: dict,
    bg_img: "Image.Image | None",
    accent: dict,
    slide_index: int,
    total_slides: int,
) -> Image.Image:
    """Compose a complete slide frame with image background, overlay, text, decorations."""
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

    font_title = _get_font(50, "heavy")
    font_h2 = _get_font(38, "bold")
    font_body = _get_font(26, "medium")
    font_small = _get_font(18, "regular")
    font_brand = _get_font(16, "demibold")

    if stype == "title":
        # Niche badge top-left
        niche = slide.get("niche", "")
        if niche:
            _draw_badge(draw, niche.upper(), font_small, ac, 80, 100)

        # Big title
        _draw_text_shadow(draw, heading, font_title, (255, 255, 255), 80, 180, WIDTH - 160)

        # Intro text
        if body:
            _draw_text_shadow(draw, body, font_body, (200, 210, 225), 80, 420, WIDTH - 160)

    elif stype == "content":
        # Slide counter top-right
        counter = f"{slide_index + 1} / {total_slides}"
        cbox = draw.textbbox((0, 0), counter, font=font_small)
        cw = cbox[2] - cbox[0]
        _draw_text_shadow(draw, counter, font_small, (150, 160, 175), WIDTH - 80 - cw, 40, 200)

        # Heading in accent colour
        _draw_text_shadow(draw, heading, font_h2, ac, 80, 120, WIDTH - 160)

        # Short accent line separator
        draw.rectangle([(80, 265), (260, 268)], fill=ac)

        # Body text
        if body:
            _draw_text_shadow(draw, body, font_body, (225, 230, 240), 80, 295, WIDTH - 160)

    elif stype == "cta":
        _draw_text_shadow(draw, heading, font_h2, (255, 255, 255), 80, 200, WIDTH - 160)
        if body:
            _draw_text_shadow(draw, body, font_body, ac, 80, 320, WIDTH - 160)

        _draw_text_shadow(
            draw, "Like & Subscribe for more!",
            font_small, (180, 190, 200), 80, 420, WIDTH - 160,
        )

    # ── Progress bar (bottom) ─────────────────────────────────────
    progress = (slide_index + 1) / total_slides
    bar_y = HEIGHT - 4
    draw.rectangle([(0, bar_y), (int(WIDTH * progress), HEIGHT)], fill=ac)
    draw.rectangle([(int(WIDTH * progress), bar_y), (WIDTH, HEIGHT)], fill=(20, 20, 20))

    # ── Brand watermark (bottom-right) ────────────────────────────
    brand = "TechLife Insights"
    bbox = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bbox[2] - bbox[0]
    _draw_text_shadow(draw, brand, font_brand, (100, 110, 125), WIDTH - 80 - bw, HEIGHT - 35, 300)

    return frame


# ═══════════════════════════════════════════════════════════════════════════
#  Image processing helpers
# ═══════════════════════════════════════════════════════════════════════════
def _apply_dark_overlay(img: Image.Image, slide_type: str = "content") -> Image.Image:
    """Apply a gradient dark overlay — lighter at top, darker at bottom for text."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size

    if slide_type == "title":
        top_alpha, bot_alpha = 0.40, 0.75
    elif slide_type == "cta":
        top_alpha, bot_alpha = 0.55, 0.80
    else:
        top_alpha, bot_alpha = 0.35, 0.72

    for y in range(h):
        t = y / h
        if t < 0.15:
            alpha = top_alpha
        elif t < 0.45:
            alpha = top_alpha + (bot_alpha - top_alpha) * ((t - 0.15) / 0.30)
        else:
            alpha = bot_alpha
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, int(255 * alpha)))

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _generate_gradient_bg(w: int, h: int, accent: dict) -> Image.Image:
    """Beautiful gradient background as fallback when no Pexels image is available."""
    ac = accent["primary"]
    dark = (15, 23, 42)

    y_grad = np.linspace(0, 1, h).reshape(-1, 1)
    x_grad = np.linspace(0, 1, w).reshape(1, -1)
    t = np.clip((x_grad * 0.4 + y_grad * 0.6) * 0.35, 0, 1)

    r = np.clip(dark[0] + (ac[0] - dark[0]) * t, 0, 255).astype(np.uint8)
    g = np.clip(dark[1] + (ac[1] - dark[1]) * t, 0, 255).astype(np.uint8)
    b = np.clip(dark[2] + (ac[2] - dark[2]) * t, 0, 255).astype(np.uint8)

    img = Image.fromarray(np.stack([r, g, b], axis=-1))
    draw = ImageDraw.Draw(img)

    # Subtle decorative circles
    for cx_f, cy_f, radius, opacity in [
        (0.75, 0.3, 180, 15), (0.2, 0.7, 120, 12), (0.5, 0.5, 250, 8),
    ]:
        cx_i, cy_i = int(w * cx_f), int(h * cy_f)
        draw.ellipse(
            [(cx_i - radius, cy_i - radius), (cx_i + radius, cy_i + radius)],
            outline=(*ac, opacity), width=2,
        )

    return img


# ═══════════════════════════════════════════════════════════════════════════
#  Text drawing helpers
# ═══════════════════════════════════════════════════════════════════════════
def _draw_text_shadow(
    draw, text: str, font, colour: tuple, x: int, y: int,
    max_width: int, shadow_offset: int = 2, line_spacing: int = 10,
) -> int:
    """Draw word-wrapped text with a subtle drop shadow. Returns final Y."""
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
        if cy > HEIGHT - 50:
            break
    return cy


def _draw_badge(draw, text: str, font, colour: tuple, x: int, y: int):
    """Draw a rounded accent-colour badge/pill."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x, pad_y = 14, 7
    draw.rounded_rectangle(
        [(x, y), (x + tw + pad_x * 2, y + th + pad_y * 2)],
        radius=6, fill=colour,
    )
    draw.text((x + pad_x, y + pad_y), text, font=font, fill=(15, 23, 42))


# ═══════════════════════════════════════════════════════════════════════════
#  Font loader
# ═══════════════════════════════════════════════════════════════════════════
def _get_font(size: int, weight: str = "heavy"):
    """Load Avenir Next at the specified weight, with cross-platform fallbacks."""
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
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()
