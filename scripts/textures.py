"""Tiling textures for the built-in pack: floors, patterns, terrain, walls,
paths, caves, roofs, lights and portals. 256 px = 1 map tile."""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from ink import INK, Canvas, Tile, blob, darker, lighter, mix, rect, rgb, rounded

T = 256  # px per tile


def noise_field(size, scale, seed, octaves=3):
    """Smooth periodic value noise in 0..1 (wraps at `size`)."""
    rs = np.random.RandomState(seed)
    out = np.zeros((size, size), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        cells = max(2, int(size / scale * (2**o)))
        grid = rs.rand(cells, cells).astype(np.float32)
        tiled = np.tile(grid, (2, 2))
        img = Image.fromarray(tiled).resize((size * 2, size * 2), Image.BICUBIC)
        out += np.asarray(img)[:size, :size] * amp
        total += amp
        amp *= 0.5
    out /= total
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def tint_by(img, field, strength):
    """Vary the color subtly by a 0..1 field (flat color with gentle mottling)."""
    a = np.asarray(img).astype(np.float32)
    a[..., :3] *= (1 - strength / 2 + field[..., None] * strength)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)


def with_height(img, field, lo=0.55):
    """Terrain alpha = height (Dungeondraft blends terrain by it): lo..1."""
    a = np.asarray(img).copy()
    a[..., 3] = ((lo + (1 - lo) * field) * 255).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


# -- floors (tilesets) -----------------------------------------------------------


def wood_floor(seed=1):
    s = 2 * T
    base = rgb("#b98a57")
    t = Tile(s, base, seed)
    rows = 8
    h = s / rows
    for r in range(rows):
        y = r * h
        x = t.rng.uniform(0, s)
        lengths = []
        while sum(lengths) < s:
            lengths.append(t.rng.choice([s / 2, s / 3, s / 4, s / 2.5]))
        lengths[-1] -= sum(lengths) - s
        for ln in lengths:
            c = mix(base, rgb("#a2733f") if t.rng.random() < 0.5 else rgb("#c79a68"), t.rng.uniform(0.2, 0.7))
            t.wshape(rect(x, y, x + ln, y + h), c, width=2.0, shade=0.12, light=0.08)
            # Grain lines along the plank.
            for _ in range(2):
                gy = y + t.rng.uniform(h * 0.25, h * 0.75)
                gx = x + t.rng.uniform(4, ln * 0.4)
                t.wline([(gx, gy), (gx + ln * t.rng.uniform(0.2, 0.5), gy + t.rng.uniform(-1.5, 1.5))], 1.0, darker(c, 0.5), 140)
            # Nails at the ends.
            for nx in (x + 6, x + ln - 6):
                for ny in (y + h * 0.3, y + h * 0.7):
                    t.wfill([(nx - 1.4, ny - 1.4), (nx + 1.4, ny - 1.4), (nx + 1.4, ny + 1.4), (nx - 1.4, ny + 1.4)], INK, 200)
            x += ln
    return t.result()


def flagstones(seed=2):
    s = 2 * T
    mortar = rgb("#8d8579")
    t = Tile(s, mortar, seed)
    n = 4
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell + t.rng.uniform(-6, 6), j * cell + t.rng.uniform(-6, 6)
            c = mix(rgb("#b4ada0"), rgb("#9d968a"), t.rng.random())
            pts = rounded(x0 + 5, y0 + 5, x0 + cell - 5, y0 + cell - 5, 10)
            pts = [(x + t.rng.uniform(-3, 3), y + t.rng.uniform(-3, 3)) for x, y in pts]
            t.wshape(pts, c, width=2.2, shade=0.2, light=0.12)
            # A crack now and then.
            if t.rng.random() < 0.35:
                cx, cy = x0 + cell * 0.3, y0 + cell * t.rng.uniform(0.3, 0.7)
                t.wline([(cx, cy), (cx + 12, cy + 6), (cx + 22, cy + 2), (cx + 34, cy + 10)], 1.1, INK, 170)
    return t.result()


def terracotta(seed=3):
    s = 2 * T
    grout = rgb("#d9c7a8")
    t = Tile(s, grout, seed)
    n = 8
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = mix(rgb("#c26a43"), rgb("#ad5a37"), t.rng.random())
            t.wshape(rounded(x0 + 3, y0 + 3, x0 + cell - 3, y0 + cell - 3, 5, 3), c, width=1.8, shade=0.18, light=0.1)
    return t.result()


def dungeon_stone(seed=4):
    s = 2 * T
    t = Tile(s, rgb("#6d6862"), seed)
    rows = 6
    h = s / rows
    for r in range(rows):
        x = t.rng.uniform(0, 40) + (h * 0.6 if r % 2 else 0)
        while x < s + 40:
            w = t.rng.uniform(h * 1.0, h * 1.9)
            c = mix(rgb("#8c8780"), rgb("#78736c"), t.rng.random())
            t.wshape(rounded(x + 3, r * h + 3, x + w - 3, r * h + h - 3, 7, 3), c, width=2.2, shade=0.22, light=0.1)
            x += w
    t.dots(260, (0, 0, s, s), INK, (0.5, 1.1), 110)
    return t.result()


def carpet(seed=5):
    s = T
    base = rgb("#8a2f2f")
    t = Tile(s, base, seed)
    gold = rgb("#d8b25a")
    for (cx, cy) in ((0, 0), (s, 0), (0, s), (s, s), (s / 2, s / 2)):
        r = s * 0.32
        t.wshape([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], rgb("#a63b37"), width=2.0, shade=0.1, light=0.12)
        r2 = r * 0.45
        t.wshape([(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)], gold, width=1.8, shade=0.12, light=0.15)
    t.dots(140, (0, 0, s, s), darker(base, 0.5), (0.5, 1.0), 90)
    return t.result()


def marble_checker(seed=6):
    s = T
    t = Tile(s, rgb("#e8e2d6"), seed)
    cell = s / 2
    for i in range(2):
        for j in range(2):
            c = rgb("#e8e2d6") if (i + j) % 2 == 0 else rgb("#4b4a52")
            t.wshape(rect(i * cell + 2, j * cell + 2, (i + 1) * cell - 2, (j + 1) * cell - 2), c, width=1.6, shade=0.12, light=0.1)
            # Veins.
            vc = darker(c, 0.25) if (i + j) % 2 == 0 else lighter(c, 0.3)
            x = i * cell + t.rng.uniform(10, cell - 10)
            y = j * cell + 8
            pts = [(x, y)]
            for _ in range(5):
                x += t.rng.uniform(-14, 14)
                y += cell / 6
                pts.append((x, y))
            t.wline(pts, 1.0, vc, 150)
    return t.result()


# -- terrain ---------------------------------------------------------------------------


def grass(seed=11):
    s = 2 * T
    base = rgb("#7aa152")
    t = Tile(s, base, seed)
    for _ in range(26):
        x, y = t.rng.uniform(0, s), t.rng.uniform(0, s)
        t.wfill(blob(x, y, t.rng.uniform(20, 45), t.rng, 12, 0.25), rgb("#6f9a48") if t.rng.random() < 0.5 else rgb("#86ad5d"), 150)
    t.wstrokes(900, (5, 10), (-0.5, 0.5), 1.1, rgb("#4d7232"), 170)
    t.wstrokes(250, (4, 8), (-0.6, 0.6), 1.0, rgb("#a9c77c"), 150)
    img = t.result()
    field = noise_field(s, 64, seed)
    return with_height(tint_by(img, field, 0.08), field, 0.6)


def dirt(seed=12):
    s = 2 * T
    base = rgb("#a17d55")
    t = Tile(s, base, seed)
    for _ in range(30):
        x, y = t.rng.uniform(0, s), t.rng.uniform(0, s)
        t.wfill(blob(x, y, t.rng.uniform(18, 40), t.rng, 12, 0.3), rgb("#94704b") if t.rng.random() < 0.5 else rgb("#ad8a60"), 140)
    for _ in range(70):
        x, y = t.rng.uniform(0, s), t.rng.uniform(0, s)
        t.wshape(blob(x, y, t.rng.uniform(2.5, 5), t.rng, 8, 0.25), rgb("#8f8274"), 1.2, 0.2, 0.15)
    t.dots(500, (0, 0, s, s), darker(base, 0.45), (0.5, 1.2), 120)
    field = noise_field(s, 80, seed)
    return with_height(tint_by(t.result(), field, 0.1), field, 0.5)


def gravel(seed=13):
    s = 2 * T
    t = Tile(s, rgb("#8f8b84"), seed)
    for _ in range(240):
        x, y = t.rng.uniform(0, s), t.rng.uniform(0, s)
        c = mix(rgb("#a9a59d"), rgb("#7c7871"), t.rng.random())
        t.wshape(blob(x, y, t.rng.uniform(4, 9), t.rng, 9, 0.25), c, 1.3, 0.25, 0.15)
    field = noise_field(s, 40, seed)
    return with_height(t.result(), field, 0.55)


def sand(seed=14):
    s = 2 * T
    base = rgb("#dcc48f")
    t = Tile(s, base, seed)
    # Wind ripples.
    for r in range(14):
        y = r * s / 14 + t.rng.uniform(-6, 6)
        pts = [(x, y + 5 * math.sin(x / 40 + r)) for x in range(-20, s + 21, 20)]
        t.wline(pts, 1.3, darker(base, 0.4), 170)
    t.dots(700, (0, 0, s, s), darker(base, 0.35), (0.4, 0.9), 110)
    field = noise_field(s, 96, seed)
    return with_height(tint_by(t.result(), field, 0.08), field, 0.5)


# -- walls -----------------------------------------------------------------------------

WALL_H = 56


def wall_strip(kind, seed):
    w, h = 2 * T, WALL_H
    c = Canvas(w, h, seed)
    if kind == "stone":
        x = 0
        while x < w:
            bw = c.rng.uniform(46, 80)
            col = mix(rgb("#9b968e"), rgb("#857f77"), c.rng.random())
            c.shape(rounded(x + 1.5, 3, min(w, x + bw) - 1.5, h - 3, 6, 3), col, 2.2, 0.22, 0.12)
            x += bw
    elif kind == "brick":
        c.fill(rect(0, 2, w, h - 2), rgb("#c9b9a2"))
        rows = 3
        bh = (h - 4) / rows
        for r in range(rows):
            x = -20 if r % 2 else 0
            while x < w:
                bw = 40
                col = mix(rgb("#a8503b"), rgb("#94432f"), c.rng.random())
                c.shape(rect(max(0, x + 1.5), 2 + r * bh + 1.5, min(w, x + bw - 1.5), 2 + (r + 1) * bh - 1.5), col, 1.6, 0.18, 0.1)
                x += bw
        c.line([(0, 2), (w, 2)], 2.2)
        c.line([(0, h - 2), (w, h - 2)], 2.2)
    elif kind == "wood":
        logs = 3
        lh = (h - 4) / logs
        for r in range(logs):
            col = mix(rgb("#8b6340"), rgb("#7a5536"), c.rng.random())
            c.shape(rounded(1, 2 + r * lh + 1, w - 1, 2 + (r + 1) * lh - 1, lh / 2.2, 4), col, 2.0, 0.2, 0.12)
            for _ in range(5):
                gx = c.rng.uniform(10, w - 80)
                gy = 2 + r * lh + lh * c.rng.uniform(0.35, 0.65)
                c.line([(gx, gy), (gx + c.rng.uniform(30, 70), gy + c.rng.uniform(-1, 1))], 1.0, darker(col, 0.5), 150)
    elif kind == "plaster":
        c.shape(rect(0, 3, w, h - 3), rgb("#e4dccb"), 2.2, 0.14, 0.08)
        # Timber posts every tile.
        for px in (0, T, 2 * T):
            c.shape(rect(px - 7, 2, px + 7, h - 2), rgb("#6e4a2f"), 2.0, 0.2, 0.1)
        for _ in range(10):
            x = c.rng.uniform(20, w - 20)
            y = c.rng.uniform(12, h - 12)
            c.line([(x, y), (x + c.rng.uniform(4, 12), y + c.rng.uniform(-3, 3))], 0.9, darker(rgb("#e4dccb"), 0.4), 120)
    return c.result(0.03)


def wall_end(kind, seed):
    s = WALL_H
    c = Canvas(s, s, seed)
    cols = {"stone": "#928c84", "brick": "#a24c38", "wood": "#83603e", "plaster": "#6e4a2f"}
    c.shape(rounded(3, 3, s - 3, s - 3, 8), rgb(cols[kind]), 2.2, 0.22, 0.12)
    if kind == "wood":
        for r in (8, 16):
            c.line([(s / 2 + r * math.cos(a / 10), s / 2 + r * math.sin(a / 10)) for a in range(0, 63)], 1.0, darker(rgb(cols[kind]), 0.5), 140)
    return c.result(0.03)


# -- paths -----------------------------------------------------------------------------


def path_strip(kind, seed):
    w, h = 2 * T, 150
    c = Canvas(w, h, seed)
    if kind == "dirt":
        base = rgb("#b08a5e")
        top = [(x, 14 + 6 * math.sin(x / 37 + 1) + 3 * math.sin(x / 13)) for x in range(0, w + 1, 8)]
        bot = [(x, h - 14 + 6 * math.sin(x / 41 + 2) + 3 * math.sin(x / 11)) for x in range(w, -1, -8)]
        # Ends match so the strip repeats: both edges are periodic in x over w.
        top = [(x, 14 + 6 * math.sin(2 * math.pi * x / w * 2) + 3 * math.sin(2 * math.pi * x / w * 7)) for x, _ in top]
        bot = [(x, h - 14 + 6 * math.sin(2 * math.pi * x / w * 3 + 1) + 3 * math.sin(2 * math.pi * x / w * 9)) for x, _ in bot]
        c.fill(top + bot, base)
        c.line(top, 1.8, darker(base, 0.55), 200)
        c.line(bot, 1.8, darker(base, 0.55), 200)
        # Ruts and pebbles.
        for ry in (h * 0.38, h * 0.62):
            c.line([(x, ry + 3 * math.sin(2 * math.pi * x / w * 4)) for x in range(0, w + 1, 8)], 1.2, darker(base, 0.35), 150)
        for _ in range(40):
            x, y = c.rng.uniform(10, w - 10), c.rng.uniform(30, h - 30)
            c.shape(blob(x, y, c.rng.uniform(2.5, 4.5), c.rng, 8), rgb("#988c7e"), 1.1, 0.2, 0.12)
    else:  # cobble
        c.fill(rect(0, 10, w, h - 10), rgb("#7b766f"))
        x = 0
        row_h = (h - 20) / 3
        for r in range(3):
            x = 0 if r % 2 == 0 else -18
            while x < w:
                bw = c.rng.uniform(30, 44)
                col = mix(rgb("#aaa49b"), rgb("#958f86"), c.rng.random())
                y0 = 10 + r * row_h
                c.shape(rounded(max(1, x + 2), y0 + 2, min(w - 1, x + bw - 2), y0 + row_h - 2, 7, 3), col, 1.6, 0.22, 0.12)
                x += bw
        c.line([(0, 10), (w, 10)], 2.0)
        c.line([(0, h - 10), (w, h - 10)], 2.0)
    return c.result(0.03)


# -- caves (grey, tinted by the cave's colors) ------------------------------------------


def cave_floor(seed):
    s = 2 * T
    t = Tile(s, rgb("#d2d0cb"), seed)
    for _ in range(36):
        x, y = t.rng.uniform(0, s), t.rng.uniform(0, s)
        t.wfill(blob(x, y, t.rng.uniform(18, 46), t.rng, 12, 0.3), rgb("#c5c3bd") if t.rng.random() < 0.5 else rgb("#dcdad5"), 160)
    for _ in range(60):
        x, y = t.rng.uniform(0, s), t.rng.uniform(0, s)
        t.wshape(blob(x, y, t.rng.uniform(3, 7), t.rng, 9), rgb("#b5b2ab"), 1.3, 0.22, 0.12)
    t.dots(400, (0, 0, s, s), rgb("#8c8983"), (0.5, 1.1), 120)
    return t.result()


def cave_wall(seed):
    w, h = 2 * T, 72
    c = Canvas(w, h, seed)
    x = 0
    while x < w:
        bw = c.rng.uniform(26, 48)
        pts = blob(x + bw / 2, h / 2, bw / 2 + 3, c.rng, 10, 0.25)
        pts = [(px, min(h - 3, max(3, py))) for px, py in pts]
        c.shape(pts, mix(rgb("#bebbb4"), rgb("#a9a69f"), c.rng.random()), 2.0, 0.28, 0.12)
        x += bw * 0.8
    return c.result(0.03)


# -- roofs ------------------------------------------------------------------------------


def roof_tiles(kind, seed):
    s = 2 * T
    base = rgb("#8a5a3a") if kind == "shingles" else rgb("#5d6670")
    t = Tile(s, darker(base, 0.25), seed)
    rows = 10
    h = s / rows
    for r in range(rows):
        x = 0 if r % 2 == 0 else -h * 0.6
        while x < s:
            w = h * 1.2
            c = mix(base, lighter(base, 0.25) if t.rng.random() < 0.5 else darker(base, 0.15), t.rng.uniform(0.2, 0.8))
            pts = [(x + 2, r * h), (x + w - 2, r * h), (x + w - 2, r * h + h * 0.85), (x + w / 2, r * h + h - 1), (x + 2, r * h + h * 0.85)]
            t.wshape(pts, c, 1.6, 0.18, 0.1)
            x += w
    return t.result()


def roof_line(kind, part, seed):
    w = 2 * T
    h = {"edge": 30, "ridge": 40, "hip": 34}[part]
    c = Canvas(w, h, seed)
    col = rgb("#6b4429") if kind == "shingles" else rgb("#454c55")
    if part == "edge":
        c.shape(rect(0, 4, w, h - 4), col, 2.0, 0.2, 0.08)
    else:
        x = 0
        while x < w:
            c.shape(rounded(x + 1, 3, x + 36, h - 3, h / 3, 3), mix(col, lighter(col, 0.2), c.rng.random()), 1.8, 0.22, 0.14)
            x += 34
    return c.result(0.03)


# -- lights -----------------------------------------------------------------------------


def light(kind):
    s = 512
    y, x = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.hypot(x - s / 2, y - s / 2) / (s / 2)
    fall = np.clip(1 - d, 0, 1) ** 1.6
    if kind == "rays":
        a = np.arctan2(y - s / 2, x - s / 2)
        fall *= 0.85 + 0.15 * np.cos(a * 10)
    a = (fall * 255).astype(np.uint8)
    img = np.dstack([np.full_like(a, 255)] * 3 + [a])
    return Image.fromarray(img, "RGBA")


# -- portals ----------------------------------------------------------------------------


def portal(kind, seed):
    if kind == "double_door":
        w = 2 * T
    else:
        w = T
    h = 64
    c = Canvas(w, h, seed)
    frame = rgb("#6e4a2f")
    if kind in ("door", "double_door"):
        c.shape(rect(2, 14, 16, h - 14), frame, 2.0)
        c.shape(rect(w - 16, 14, w - 2, h - 14), frame, 2.0)
        leaves = [(16, w - 16)] if kind == "door" else [(16, w / 2), (w / 2, w - 16)]
        for x0, x1 in leaves:
            col = rgb("#9a6c43")
            c.shape(rect(x0, 20, x1, h - 20), col, 2.0, 0.2, 0.1)
            for gx in range(int(x0) + 18, int(x1) - 6, 22):
                c.line([(gx, 22), (gx, h - 22)], 1.0, darker(col, 0.45), 160)
            c.ellipse(x1 - 10 if x1 < w - 20 or kind == "door" else x0 + 10, h / 2, 3, 3, rgb("#c9a640"), 1.2)
    elif kind == "window":
        c.shape(rect(2, 22, w - 2, h - 22), rgb("#6e4a2f"), 2.0)
        c.shape(rect(14, 26, w - 14, h - 26), rgb("#a9cfdc"), 1.6, 0.1, 0.3)
        c.line([(w / 2, 24), (w / 2, h - 24)], 1.6)
    elif kind == "arch":
        for x0 in (2, w - 22):
            c.shape(rounded(x0, 10, x0 + 20, h - 10, 5), rgb("#9b968e"), 2.2, 0.22, 0.12)
    return c.result(0.03)


# -- patterns (recolorable: the red regions take the pattern's color) ------------------

PATTERN_RED = (200, 46, 46)


def pattern_tiles(seed=21):
    s = T
    t = Tile(s, rgb("#e6dccb"), seed)
    n = 4
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = mix(PATTERN_RED, darker(PATTERN_RED, 0.25), t.rng.random() * 0.6)
            t.wshape(rounded(x0 + 4, y0 + 4, x0 + cell - 4, y0 + cell - 4, 6, 3), c, 1.8, 0.18, 0.1)
    return t.result(0.02)


def pattern_basketweave(seed=22):
    s = T
    t = Tile(s, rgb("#e6dccb"), seed)
    u = s / 8  # brick: 2u x 1u; 2u x 2u blocks alternate horizontal / vertical pairs
    for bi in range(4):
        for bj in range(4):
            x0, y0 = bi * 2 * u, bj * 2 * u
            horizontal = (bi + bj) % 2 == 0
            for k in range(2):
                if horizontal:
                    x, y, w, h = x0, y0 + k * u, 2 * u, u
                else:
                    x, y, w, h = x0 + k * u, y0, u, 2 * u
                c = mix(PATTERN_RED, darker(PATTERN_RED, 0.25), t.rng.random() * 0.6)
                t.wshape(rect(x + 2, y + 2, x + w - 2, y + h - 2), c, 1.5, 0.15, 0.08)
    return t.result(0.02)


def pattern_hex(seed=23):
    s = T
    t = Tile(s, rgb("#e6dccb"), seed)
    # A hexagon grid that wraps at s: 4 columns of hexes with radius r.
    cols = 4
    w = s / cols
    r = w / math.sqrt(3)
    rows = round(s / (1.5 * r))
    r = s / rows / 1.5
    for i in range(cols):
        for j in range(rows):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * 1.5 * r
            pts = [(cx + (r - 2.5) * math.sin(a), cy + (r - 2.5) * math.cos(a)) for a in [k * math.pi / 3 for k in range(6)]]
            c = mix(PATTERN_RED, darker(PATTERN_RED, 0.25), t.rng.random() * 0.6)
            t.wshape(pts, c, 1.6, 0.16, 0.1)
    return t.result(0.02)
