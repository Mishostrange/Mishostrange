"""Shared deterministic drawing helpers. No network assets or system font dependency."""
from pathlib import Path
import json
from functools import lru_cache
from html import escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG = '#070d16'
PANEL = '#0c1522'
GREEN = '#75f7ac'
CYAN = '#67dfee'
WHITE = '#e2edf4'
MUTED = '#9aafbf'

def config():
    return json.loads((ROOT / 'profile.json').read_text(encoding='utf-8'))

@lru_cache(maxsize=16)
def font(size):
    return ImageFont.truetype(str(ASSETS / 'fonts/SourceCodePro-Regular.ttf'), size)

def canvas(width, height, label):
    im = Image.new('RGB', (width, height), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, width-2, height-2), radius=18, outline='#243548', width=2)
    d.line((24, 48, width-24, 48), fill='#243548')
    for x, color in [(30, '#ed7180'), (50, '#e9c16b'), (70, GREEN)]:
        d.ellipse((x, 21, x+8, 29), fill=color)
    d.text((96, 16), label, font=font(14), fill=MUTED)
    return im

def save_gif(frames, path, durations):
    # Shared palette prevents per-frame palette flicker; 128 colors keep files small.
    palette = Image.new('RGB', (16, 8))
    colors = []
    for base in [(7,13,22), (117,247,172), (103,223,238), (226,237,244), (154,175,191), (36,53,72), (237,113,128), (233,193,107)]:
        for i in range(16):
            colors.append(tuple(int(7+(v-7)*i/15) for v in base))
    palette.putdata(colors)
    palette = palette.quantize(colors=128)
    indexed = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, optimize=True, disposal=1)

def svg(width, height, body, title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18" fill="{BG}" stroke="#243548"/>{body}</svg>\n'

def text(x, y, value, size=16, color=WHITE):
    return f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" fill="{color}">{escape(str(value))}</text>'
