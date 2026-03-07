"""Convert SVG logos to JPG copies using Pillow (no Cairo dependency)."""
from PIL import Image, ImageDraw, ImageFont
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_font(size):
    for fp in ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/SFNSDisplay.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        try:
            return ImageFont.truetype(fp, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()

# --- logo-full-dark.jpg (960x240 horizontal, dark bg) ---
img = Image.new("RGB", (960, 240), color=(30, 58, 138))
draw = ImageDraw.Draw(img)

# TL icon box
draw.rounded_rectangle([(8, 20), (208, 220)], radius=40, fill=(37, 99, 235))
font_tl = get_font(104)
draw.text((50, 42), "TL", font=font_tl, fill="white")
# Accent dot
draw.ellipse([(170, 40), (190, 60)], fill=(96, 165, 250))
draw.ellipse([(175, 45), (185, 55)], fill="white")

# Brand text
font_brand = get_font(72)
font_sub = get_font(44)
draw.text((228, 36), "Tech", font=font_brand, fill=(249, 250, 251))
draw.text((478, 36), "Life", font=font_brand, fill=(96, 165, 250))
draw.text((228, 140), "INSIGHTS", font=font_sub, fill=(156, 163, 175))

img.save("site/output/assets/logo-full-dark.jpg", "JPEG", quality=95)
print(f"Created logo-full-dark.jpg: {img.size[0]}x{img.size[1]}")

# --- logo-social.jpg (800x800 square) ---
img2 = Image.new("RGB", (800, 800), color=(30, 58, 138))
draw2 = ImageDraw.Draw(img2)

# Rounded bg gradient simulation — solid blue
draw2.rounded_rectangle([(20, 20), (780, 780)], radius=120, fill=(37, 99, 235))
font_big = get_font(260)
font_ins = get_font(80)
font_tag = get_font(36)
draw2.text((150, 160), "TL", font=font_big, fill="white")
# Accent bar
draw2.rounded_rectangle([(200, 440), (600, 448)], radius=3, fill=(96, 165, 250))
draw2.text((160, 480), "INSIGHTS", font=font_ins, fill="white")
draw2.text((270, 620), "TECHLIFE", font=font_tag, fill=(255, 255, 255, 140))
# Accent dot
draw2.ellipse([(600, 160), (630, 190)], fill=(96, 165, 250))
draw2.ellipse([(608, 168), (622, 182)], fill="white")

img2.save("site/output/assets/logo-social.jpg", "JPEG", quality=95)
print(f"Created logo-social.jpg: {img2.size[0]}x{img2.size[1]}")

# --- logo.jpg (400x400 icon) ---
img3 = Image.new("RGB", (400, 400), color=(30, 58, 138))
draw3 = ImageDraw.Draw(img3)

draw3.rounded_rectangle([(16, 16), (384, 384)], radius=72, fill=(37, 99, 235))
font_icon = get_font(200)
draw3.text((50, 60), "TL", font=font_icon, fill="white")
draw3.ellipse([(320, 60), (356, 96)], fill=(96, 165, 250))
draw3.ellipse([(329, 69), (347, 87)], fill="white")

img3.save("site/output/assets/logo.jpg", "JPEG", quality=95)
print(f"Created logo.jpg: {img3.size[0]}x{img3.size[1]}")
