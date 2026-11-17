"""Contact sheets for reviewing the pack: every asset with an ID and its name.

    python3 scripts/builtin-pack/review.py <outdir>
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG = (232, 223, 200)


import numpy as np


def recolor(img, color):
    """The colorable-object recolor (as recolor.rs): reddish pixels
    with g ~= b take `color`, scaled by their red channel."""
    a = np.asarray(img.convert("RGBA")).astype(np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    tint = np.array(color, np.float32) / 255
    mask = (np.abs(g - b) <= 0.04) & (r - (g + b) / 2 > 0.1)
    out = a.copy()
    tex = r[..., None] * tint
    lum = (0.299 * r + 0.587 * g + 0.114 * b)[..., None]
    k = np.clip(lum - 0.333, 0, None)
    tex = tex + (1 - tex) * k
    out[..., :3] = np.where(mask[..., None], tex, a[..., :3])
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA")


def sheet(items, path, cell=300, cols=5, tiled=False, title=""):
    """items: [(id, name, PIL image)]. Objects are fit into the cell; tiled
    textures are shown repeated 2x2 so seams would show."""
    rows = (len(items) + cols - 1) // cols
    lab = 34
    top = 50 if title else 0
    out = Image.new("RGB", (cols * cell, top + rows * (cell + lab)), BG)
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(FONT, 17)
    if title:
        d.text((12, 12), title, fill=(40, 30, 25), font=ImageFont.truetype(FONT, 24))
    for i, item in enumerate(items):
        iid, name, im = item[:3]
        colorable = len(item) > 3 and item[3]
        x, y = (i % cols) * cell, top + (i // cols) * (cell + lab)
        im = im.convert("RGBA")
        if tiled:
            w, h = im.size
            t = Image.new("RGBA", (w * 2, h * 2))
            for dx in (0, w):
                for dy in (0, h):
                    t.paste(im, (dx, dy))
            im = t
        pad = 10
        im = im.copy()
        im.thumbnail((cell - 2 * pad, cell - 2 * pad), Image.LANCZOS)
        out.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2), im)
        if colorable:
            # Colorable: also show it recolored (the red is what takes the color).
            for j, col in enumerate(((70, 110, 170), (80, 140, 80))):
                mini = recolor(im, col)
                mini.thumbnail((cell // 4, cell // 4), Image.LANCZOS)
                mx = x + cell - (j + 1) * (cell // 4 + 4)
                out.paste(mini, (mx, y + cell - cell // 4 - 4), mini)
        d.rectangle((x, y + cell, x + cell, y + cell + lab), fill=(52, 44, 38))
        d.text((x + 8, y + cell + 7), f"{iid}  {name}", fill=(245, 235, 215), font=f)
    out.save(path)
    return path
