"""
Generate YouTube channel banner (2560x1440) and improved square logo (800x800).

YouTube banner safe areas:
  • TV:      full 2560x1440
  • Desktop: 2560x423 horizontal strip (center)
  • Mobile:  1546x423 centered in middle
  → Keep all important content within the center ~1546x423 safe zone.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = "site/output/assets"


# ── Font loaders ──────────────────────────────────────────────────────────
def font_heavy(size):
    """Avenir Next Heavy — bold, modern, premium feel."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=8)
    except:
        pass
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
    except:
        return ImageFont.load_default()


def font_bold(size):
    """Avenir Next Bold."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=0)
    except:
        return font_heavy(size)


def font_medium(size):
    """Avenir Next Medium."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=5)
    except:
        return font_heavy(size)


def font_demi(size):
    """Avenir Next Demi Bold."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=2)
    except:
        return font_bold(size)


def font_light(size):
    """Avenir Next Regular/Light."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", size, index=7)
    except:
        return font_medium(size)


# ── Brand colors ──────────────────────────────────────────────────────────
DARK_BG      = (15, 23, 42)     # Very dark navy
BLUE_PRIMARY = (37, 99, 235)    # Brand blue
BLUE_ACCENT  = (96, 165, 250)   # Light blue accent
BLUE_GLOW    = (59, 130, 246)   # Mid-blue
WHITE        = (255, 255, 255)
GRAY_LIGHT   = (203, 213, 225)
GRAY_MID     = (148, 163, 184)
GRAY_DIM     = (100, 116, 139)


def text_center_x(draw, text, font, canvas_width):
    """Get x position to center text on canvas."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    return (canvas_width - tw) // 2


def draw_gradient_rect(draw, box, color_top, color_bottom):
    """Fill a rectangle with a vertical gradient."""
    x1, y1, x2, y2 = box
    for y in range(y1, y2):
        ratio = (y - y1) / max(1, (y2 - y1))
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        draw.line([(x1, y), (x2, y)], fill=(r, g, b))


# ═══════════════════════════════════════════════════════════════════════════
#  1. YouTube Channel Banner (2560 x 1440)
# ═══════════════════════════════════════════════════════════════════════════
def create_youtube_banner():
    W, H = 2560, 1440
    img = Image.new("RGB", (W, H), color=DARK_BG)
    draw = ImageDraw.Draw(img)

    # ── Background: subtle gradient from darker top to slightly lighter bottom ──
    draw_gradient_rect(draw, (0, 0, W, H), (10, 17, 35), (20, 30, 55))

    # ── Decorative elements (subtle tech pattern) ──────────────────────────
    # Horizontal circuit-like lines
    for y_off in [380, 1060]:
        draw.line([(200, y_off), (600, y_off)], fill=(*BLUE_ACCENT, ), width=1)
        draw.ellipse([(596, y_off - 3), (602, y_off + 3)], fill=BLUE_ACCENT)
        draw.line([(1960, y_off), (2360, y_off)], fill=(*BLUE_ACCENT, ), width=1)
        draw.ellipse([(1956, y_off - 3), (1962, y_off + 3)], fill=BLUE_ACCENT)

    # Subtle grid dots across background
    for gx in range(0, W, 80):
        for gy in range(0, H, 80):
            # Only render some dots for subtlety
            if (gx + gy) % 240 == 0:
                draw.ellipse([(gx - 1, gy - 1), (gx + 1, gy + 1)], fill=(40, 55, 85))

    # ── Accent glow line (center horizontal) ──────────────────────────────
    glow_y = H // 2
    for i in range(6):
        alpha_ratio = 1.0 - (i / 6)
        c = int(BLUE_ACCENT[0] * alpha_ratio * 0.15)
        g = int(BLUE_ACCENT[1] * alpha_ratio * 0.15)
        b = int(BLUE_ACCENT[2] * alpha_ratio * 0.15)
        draw.line([(300, glow_y - 100 + i * 30), (W - 300, glow_y - 100 + i * 30)],
                  fill=(c + 15, g + 23, b + 42), width=1)

    # ── Logo icon (rounded square with "TL") — left of center ─────────────
    icon_size = 180
    icon_x = W // 2 - 440
    icon_y = H // 2 - icon_size // 2

    # Icon background with subtle gradient
    draw.rounded_rectangle(
        [(icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size)],
        radius=40,
        fill=BLUE_PRIMARY,
    )
    # Glass shine on top half
    draw.rounded_rectangle(
        [(icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size // 2)],
        radius=40,
        fill=(45, 110, 240),
    )
    # Fix bottom corners of shine overlay
    draw.rectangle(
        [(icon_x, icon_y + icon_size // 2 - 40), (icon_x + icon_size, icon_y + icon_size // 2)],
        fill=BLUE_PRIMARY,
    )

    # "TL" text inside icon
    f_icon = font_heavy(96)
    bbox = draw.textbbox((0, 0), "TL", font=f_icon)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (icon_x + (icon_size - tw) // 2, icon_y + (icon_size - th) // 2 - 8),
        "TL", font=f_icon, fill=WHITE,
    )

    # Accent dot on icon
    dot_x = icon_x + icon_size - 28
    dot_y = icon_y + 22
    draw.ellipse([(dot_x - 10, dot_y - 10), (dot_x + 10, dot_y + 10)], fill=BLUE_ACCENT)
    draw.ellipse([(dot_x - 4, dot_y - 4), (dot_x + 4, dot_y + 4)], fill=WHITE)

    # ── Brand text — right of icon ────────────────────────────────────────
    text_x = icon_x + icon_size + 40
    text_y_base = H // 2

    # "TechLife" — big, bold
    f_brand = font_heavy(110)
    draw.text((text_x, text_y_base - 90), "Tech", font=f_brand, fill=WHITE)
    # Measure "Tech" width
    tech_bbox = draw.textbbox((text_x, 0), "Tech", font=f_brand)
    tech_w = tech_bbox[2] - tech_bbox[0]
    draw.text((text_x + tech_w + 4, text_y_base - 90), "Life", font=f_brand, fill=BLUE_ACCENT)

    # "INSIGHTS" — spaced, lighter
    f_sub = font_demi(52)
    draw.text((text_x + 4, text_y_base + 40), "I N S I G H T S", font=f_sub, fill=GRAY_LIGHT)

    # ── Tagline (below center safe area, visible on TV) ───────────────────
    f_tag = font_light(32)
    tagline = "Smart Guides for Modern Living"
    tx = text_center_x(draw, tagline, f_tag, W)
    draw.text((tx, H // 2 + 160), tagline, font=f_tag, fill=GRAY_MID)

    # ── Top accent bar ────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 4)], fill=BLUE_ACCENT)

    # ── Bottom accent bar ─────────────────────────────────────────────────
    draw.rectangle([(0, H - 4), (W, H)], fill=BLUE_ACCENT)

    # ── Save ──────────────────────────────────────────────────────────────
    img.save(f"{OUT}/youtube-banner.jpg", "JPEG", quality=95)
    print(f"✅ Created youtube-banner.jpg: {W}x{H}")

    # Also save a PNG for maximum quality
    img.save(f"{OUT}/youtube-banner.png", "PNG")
    print(f"✅ Created youtube-banner.png: {W}x{H}")


# ═══════════════════════════════════════════════════════════════════════════
#  2. Improved Square Logo (800 x 800)
# ═══════════════════════════════════════════════════════════════════════════
def create_square_logo():
    S = 800
    img = Image.new("RGB", (S, S), color=DARK_BG)
    draw = ImageDraw.Draw(img)

    # ── Background: rounded blue square with gradient ─────────────────────
    # Outer subtle dark border
    draw.rounded_rectangle([(16, 16), (S - 16, S - 16)], radius=100, fill=(20, 35, 65))

    # Inner gradient blue square
    draw.rounded_rectangle([(24, 24), (S - 24, S - 24)], radius=96, fill=BLUE_PRIMARY)

    # Top-half glass shine
    draw.rounded_rectangle([(24, 24), (S - 24, S // 2)], radius=96, fill=(42, 108, 238))
    # Fix bottom of shine area
    draw.rectangle([(24, S // 2 - 96), (S - 24, S // 2)], fill=BLUE_PRIMARY)

    # ── Decorative circuit lines (tech DNA) ───────────────────────────────
    line_color = (55, 120, 245)  # subtle blue, slightly visible
    # Top-right corner circuit
    draw.line([(560, 80), (700, 80)], fill=line_color, width=2)
    draw.line([(700, 80), (700, 140)], fill=line_color, width=2)
    draw.ellipse([(694, 136), (706, 148)], fill=BLUE_ACCENT)
    # Bottom-left corner circuit
    draw.line([(100, 720), (100, 660)], fill=line_color, width=2)
    draw.line([(100, 660), (240, 660)], fill=line_color, width=2)
    draw.ellipse([(94, 716), (106, 728)], fill=BLUE_ACCENT)

    # ── Lightbulb-brain icon (represents "Insights" = ideas + intelligence) ──
    # This replaces the basic "TL" with a recognizable concept icon
    cx, cy_icon = S // 2, 240

    # Bulb outline (circle)
    bulb_r = 80
    draw.ellipse(
        [(cx - bulb_r, cy_icon - bulb_r), (cx + bulb_r, cy_icon + bulb_r)],
        fill=None, outline=WHITE, width=5,
    )

    # Inner glow fill (semi-bright)
    draw.ellipse(
        [(cx - bulb_r + 12, cy_icon - bulb_r + 12), (cx + bulb_r - 12, cy_icon + bulb_r - 12)],
        fill=(70, 140, 255),
    )

    # Filament / brain circuit inside the bulb
    # Three small horizontal lines (like a brain/circuit motif)
    for i, w in enumerate([36, 28, 20]):
        ly = cy_icon - 20 + i * 20
        draw.line([(cx - w, ly), (cx + w, ly)], fill=WHITE, width=3)

    # Bulb base (two small rectangles below)
    base_top = cy_icon + bulb_r + 4
    draw.rounded_rectangle([(cx - 30, base_top), (cx + 30, base_top + 14)], radius=4, fill=GRAY_LIGHT)
    draw.rounded_rectangle([(cx - 22, base_top + 18), (cx + 22, base_top + 30)], radius=4, fill=GRAY_LIGHT)
    # Tip
    draw.polygon([(cx - 10, base_top + 34), (cx + 10, base_top + 34), (cx, base_top + 46)], fill=GRAY_LIGHT)

    # Small radiating lines around the bulb (idea rays)
    ray_len = 18
    ray_gap = bulb_r + 14
    for angle_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
        angle = math.radians(angle_deg)
        x1 = cx + int(ray_gap * math.cos(angle))
        y1 = cy_icon + int(ray_gap * math.sin(angle))
        x2 = cx + int((ray_gap + ray_len) * math.cos(angle))
        y2 = cy_icon + int((ray_gap + ray_len) * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=BLUE_ACCENT, width=3)

    # ── "TechLife" brand text ─────────────────────────────────────────────
    f_name = font_heavy(88)
    # "Tech" in white, "Life" in accent
    tech_text = "Tech"
    life_text = "Life"
    tech_bbox = draw.textbbox((0, 0), tech_text, font=f_name)
    life_bbox = draw.textbbox((0, 0), life_text, font=f_name)
    tech_w = tech_bbox[2] - tech_bbox[0]
    life_w = life_bbox[2] - life_bbox[0]
    total_w = tech_w + life_w + 6
    name_x = (S - total_w) // 2
    name_y = 420

    draw.text((name_x, name_y), tech_text, font=f_name, fill=WHITE)
    draw.text((name_x + tech_w + 6, name_y), life_text, font=f_name, fill=BLUE_ACCENT)

    # ── Accent bar under brand name ───────────────────────────────────────
    bar_y = name_y + 100
    bar_w = 300
    bar_x = (S - bar_w) // 2
    draw.rounded_rectangle(
        [(bar_x, bar_y), (bar_x + bar_w, bar_y + 6)],
        radius=3,
        fill=BLUE_ACCENT,
    )

    # ── "INSIGHTS" below bar ──────────────────────────────────────────────
    f_ins = font_demi(56)
    ins_text = "I N S I G H T S"
    ix = text_center_x(draw, ins_text, f_ins, S)
    draw.text((ix, bar_y + 24), ins_text, font=f_ins, fill=WHITE)

    # ── Accent dot cluster (top-right) ────────────────────────────────────
    draw.ellipse([(620, 100), (644, 124)], fill=BLUE_ACCENT)
    draw.ellipse([(628, 108), (636, 116)], fill=WHITE)
    draw.ellipse([(652, 130), (664, 142)], fill=(*BLUE_ACCENT,))
    draw.ellipse([(600, 135), (608, 143)], fill=(120, 180, 255))

    # ── Save ──────────────────────────────────────────────────────────────
    img.save(f"{OUT}/logo-square.jpg", "JPEG", quality=95)
    print(f"✅ Created logo-square.jpg: {S}x{S}")

    img.save(f"{OUT}/logo-square.png", "PNG")
    print(f"✅ Created logo-square.png: {S}x{S}")

    # Also overwrite the old logo-social.jpg with the new design
    img.save(f"{OUT}/logo-social.jpg", "JPEG", quality=95)
    print(f"✅ Updated logo-social.jpg: {S}x{S}")


# ═══════════════════════════════════════════════════════════════════════════
#  Run
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    create_youtube_banner()
    create_square_logo()
    print("\nDone! Files in site/output/assets/")
    print("  • youtube-banner.jpg / .png  (2560x1440 — upload to YouTube)")
    print("  • logo-square.jpg / .png     (800x800 — profile pic)")
