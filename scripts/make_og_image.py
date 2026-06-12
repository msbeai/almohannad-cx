#!/usr/bin/env python3
"""Generate the default Open Graph image (1200x630) in the site's dark editorial style."""
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path

FONTS = Path.home() / "Library" / "Fonts"
OUT = Path.home() / "Projects" / "almohannad-cx" / "public" / "og-default.png"

BG, CREAM, TERRA, MUTED = "#1a1815", "#faf8f5", "#d4775c", "#b6aea4"

def ar(text):
    return get_display(arabic_reshaper.reshape(text))

im = Image.new("RGB", (1200, 630), BG)
d = ImageDraw.Draw(im)

display_bold = ImageFont.truetype(str(FONTS / "thmanyahserifdisplay-Bold.otf"), 96)
display_ar = ImageFont.truetype(str(FONTS / "thmanyahserifdisplay-Bold.otf"), 64)
sans = ImageFont.truetype(str(FONTS / "thmanyahsans-Regular.otf"), 34)

# top rule + kicker dot
d.rectangle([80, 80, 1120, 84], fill="#2e2924")
d.ellipse([80, 130, 104, 154], fill=TERRA)

# Arabic name (large, right-aligned like the site)
name = ar("المهند السبيعي")
w = d.textlength(name, font=display_ar)
d.text((1120 - w, 200), name, font=display_ar, fill=CREAM)

# domain wordmark
d.text((1120 - d.textlength("almohannad", font=display_bold) - d.textlength(".cx", font=display_bold), 300),
       "almohannad", font=display_bold, fill=CREAM)
d.text((1120 - d.textlength(".cx", font=display_bold), 300), ".cx", font=display_bold, fill=TERRA)

# subtitle Arabic
sub = ar("تجربة العميل · الأبحاث التسويقية · الكتابة")
w = d.textlength(sub, font=sans)
d.text((1120 - w, 460), sub, font=sans, fill=MUTED)

# bottom rule
d.rectangle([80, 546, 1120, 550], fill="#2e2924")

im.save(OUT, "PNG")
print(f"saved {OUT} ({OUT.stat().st_size // 1024} KB)")
