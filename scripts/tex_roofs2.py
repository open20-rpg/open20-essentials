"""More roof styles for the built-in pack (on top of tex_build.ROOFS): each a
tuple (tiles 512x512 seamless, edge 512x30, ridge 512x40, hip 512x34), the
same shape tex_build.roof() returns. Reuses tex_build's tile and line
drawing for the classic kinds and adds new kinds (hexagonal, barrel and flat
clay, planks, turf, palm, canvas, standing-seam metal, oriental) plus
overlays (snow, moss, damage) composited on top."""

import math

from PIL import Image

from floors import speckles
from pen import DETAIL, FINE, INK, JOINT, JOINT_ALPHA, Art, blob, chaikin, grout, joint_color, mix, rect, rgb, shade, tint, vary
from tex_build import SW, band, roof_line, roof_tiles, strip

S = SW  # tile size


# -- new tile kinds -----------------------------------------------------------------------


# Joints between roof pieces: thin, in a darker tone of the piece. Pieces that
# overlap (shingles, clay, scales, barrel caps) keep a slightly heavier edge
# for the overlap shadow, still tone-on-tone instead of INK.
LAP = JOINT * 1.7
LAP_ALPHA = 0.85


def _joint(c, lap=False):
    return {"outline": LAP if lap else JOINT * 1.2, "outline_color": shade(c, 0.55) if lap else joint_color(c), "outline_alpha": LAP_ALPHA if lap else JOINT_ALPHA}


def _fill(a, color):
    a.tile = False
    a.shape(rect(-10, -10, a.w + 10, a.h + 10), color, outline=0, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.04)
    a.tile = True


def hex_tiles(seed, base, n=8):
    a = Art(S, S, seed, tile=True, bg=grout(base))
    w = S / n
    rows = int(round(S / (1.5 * w / math.sqrt(3))))
    if rows % 2:
        rows += 1
    # Pointy-top hexes squashed to fit a whole number of rows: an affine
    # copy of the regular grid, so they still tessellate without gaps.
    rx = w / math.sqrt(3)
    ry = S / rows / 1.5
    for j in range(rows):
        for i in range(n):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * 1.5 * ry
            k_ = 1 - 1.0 / rx
            pts = [(cx + rx * k_ * math.cos(k * math.pi / 3 + math.pi / 6), cy + ry * k_ * math.sin(k * math.pi / 3 + math.pi / 6)) for k in range(6)]
            c = vary(a.rng, mix(base, tint(base, 0.2), a.rng.random() * 0.6), 0.03)
            a.shape(pts, c, corner=2, wob=0.3, depth=3, shade_k=0.4, light_k=0.3, ao=0.08, mottle=0.03, var=0.1, **_joint(c))
    return a.image()


def barrel_tiles(seed, base, cols=8):
    """Spanish barrel tiles: alternating convex caps (lit) and pans (shaded) in columns."""
    a = Art(S, S, seed, tile=True, bg=grout(base))
    w = S / cols
    rows = 6
    h = S / rows
    for i in range(cols):
        x = i * w
        cap = i % 2 == 0
        for r in range(rows):
            y = r * h + (h / 2 if cap else 0)
            c = vary(a.rng, tint(base, 0.12) if cap else shade(base, 0.12), 0.04)
            pts = rect(x + 0.8, y, x + w - 0.8, y + h + 2)

            def det(art, p, x=x, y=y, c=c, cap=cap):
                if cap:
                    art.ink([(x + w * 0.35, y + 4), (x + w * 0.35, y + h - 4)], FINE * 1.4, color=tint(c, 0.45), alpha=0.85, taper=False)
                else:
                    art.ink([(x + w * 0.5, y + 4), (x + w * 0.5, y + h - 4)], FINE * 1.2, color=shade(c, 0.35), alpha=0.6, taper=False)

            a.shape(pts, c, corner=w * 0.4, wob=0.3, depth=3, shade_k=0.45, light_k=0.35, ao=0.08, mottle=0.03, detail=det, var=0.1, **_joint(c, lap=True))
    return a.image()


def flat_tiles(seed, base, rows=12):
    """Flat interlocking tiles: rectangles in staggered rows with a nib line."""
    a = Art(S, S, seed, tile=True, bg=grout(base))
    h = S / rows
    n = 8
    w = S / n
    for r in range(rows):
        x = 0 if r % 2 == 0 else -w / 2
        for _ in range(n):
            c = vary(a.rng, mix(base, tint(base, 0.18), a.rng.random()), 0.03)
            y0 = r * h

            def det(art, p, x=x, y0=y0, c=c):
                art.ink([(x + 6, y0 + h * 0.3), (x + w - 6, y0 + h * 0.3)], FINE, color=shade(c, 0.35), alpha=0.6, taper=False)

            a.shape(rect(x + 0.9, y0 + 0.9, x + w - 0.9, y0 + h - 0.9), c, corner=2, wob=0.3, depth=2.5, shade_k=0.4, light_k=0.3, ao=0.08, mottle=0.03, detail=det, var=0.1, **_joint(c))
            x += w
    return a.image()


def plank_roof(seed, base, n=10):
    """Wooden planks running down the slope with battens across."""
    a = Art(S, S, seed, tile=True, bg=grout(base))
    w = S / n
    for i in range(n):
        x = i * w
        c = vary(a.rng, mix(base, tint(base, 0.15) if a.rng.random() < 0.5 else shade(base, 0.12), a.rng.random()), 0.03)
        a.tile = False
        a.shape(rect(x + 0.8, -6, x + w - 0.8, S + 6), c, outline=0, corner=0, wob=0, depth=3, shade_k=0.4, light_k=0.3, ao=0.08, mottle=0.03)
        a.tile = True
        for k in range(3):
            gx = x + w * (0.25 + 0.25 * k) + a.rng.uniform(-2, 2)
            y0 = a.rng.uniform(0, S)
            a.ink([(gx, y0), (gx + a.rng.uniform(-2, 2), y0 + a.rng.uniform(80, 200))], FINE * 0.9, color=shade(c, 0.45), alpha=0.6, wob=0.4)
    a.tile = False
    for i in range(n + 1):
        a.ink([(i * w, -6), (i * w, S + 6)], JOINT * 1.2, color=joint_color(base), alpha=JOINT_ALPHA, taper=False, wob=0.2, var=0.0)
    a.tile = True
    for y in (S * 0.25, S * 0.75):
        batten = shade(base, 0.2)
        band(a, y - 8, y + 8, batten, outline=0, light_k=0.25)
        a.tile = False
        for yy in (y - 8, y + 8):
            a.ink([(-6, yy), (S + 6, yy)], LAP, color=shade(batten, 0.55), alpha=LAP_ALPHA, taper=False, wob=0, var=0.0)
        a.tile = True
        for i in range(n):
            a.fill_path(_dot(i * w + w / 2, y), shade(batten, 0.6), 0.8)
    return a.image()


def _dot(x, y, r=2.2):
    import skia

    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def turf_roof(seed, base=rgb("#6f9443")):
    """Sod/turf roof: grass tufts and wild flowers over earth."""
    a = Art(S, S, seed, tile=True, bg=shade(base, 0.25))
    for _ in range(60):
        x, y = a.rng.uniform(0, S), a.rng.uniform(0, S)
        a.fill_path(_blob_path(blob(x, y, a.rng.uniform(16, 34), a.rng, 9, 0.3)), vary(a.rng, mix(base, tint(base, 0.25), a.rng.random()), 0.04), 0.9)
    for _ in range(900):
        x, y = a.rng.uniform(0, S), a.rng.uniform(0, S)
        t = -math.pi / 2 + a.rng.uniform(-0.6, 0.6)
        ln = a.rng.uniform(5, 11)
        a.ink([(x, y), (x + ln * math.cos(t), y + ln * math.sin(t))], FINE * 1.0, color=shade(base, a.rng.uniform(0.3, 0.55)) if a.rng.random() < 0.8 else tint(base, 0.4), alpha=0.85, wob=0.1)
    for _ in range(30):
        x, y = a.rng.uniform(0, S), a.rng.uniform(0, S)
        a.fill_path(_dot(x, y, a.rng.uniform(2, 3.4)), a.rng.choice([rgb("#f2e08a"), rgb("#f3eee2"), rgb("#d88aa8")]), 0.95)
    return a.image()


def _blob_path(pts):
    from pen import to_path

    return to_path(chaikin(pts, True, 2))


def palm_thatch(seed, base=rgb("#a8a050"), rows=7):
    """Palm/leaf thatch: overlapping rows of long pointed fronds."""
    a = Art(S, S, seed, tile=True, bg=shade(base, 0.4))
    h = S / rows
    for r in range(rows):
        y = r * h
        n = 16
        w = S / n
        x = 0 if r % 2 == 0 else -w / 2
        for _ in range(n):
            c = vary(a.rng, mix(base, shade(base, 0.15) if a.rng.random() < 0.5 else tint(base, 0.15), a.rng.random()), 0.04)
            tipx = x + w / 2 + a.rng.uniform(-4, 4)
            pts = [(x, y), (x + w, y), (tipx + 3, y + h * 1.35), (tipx - 3, y + h * 1.35)]

            def det(art, p, x=x, y=y, tipx=tipx, c=c):
                art.ink([(x + w / 2, y + 2), (tipx, y + h * 1.25)], FINE * 1.1, color=shade(c, 0.45), alpha=0.8)

            a.shape(pts, c, outline=DETAIL * 1.0, corner=1, wob=0.3, depth=2.5, shade_k=0.45, light_k=0.3, ao=0.1, mottle=0.03, detail=det, var=0.1)
            x += w
    return a.image()


def canvas_roof(seed, c1, c2, stripes=8):
    """Tent canvas: wide stripes with seam stitching and a few folds."""
    a = Art(S, S, seed, tile=True, bg=c2)
    w = S / stripes
    a.tile = False
    for i in range(stripes):
        a.shape(rect(i * w, -6, (i + 1) * w, S + 6), c1 if i % 2 == 0 else c2, outline=0, corner=0, wob=0, depth=2, shade_k=0.3, light_k=0.25, ao=0.05, mottle=0.04)
    for i in range(stripes + 1):
        a.ink([(i * w, -6), (i * w, S + 6)], DETAIL * 0.9, color=shade(c2, 0.5), taper=False, wob=0.2, var=0.0)
        for y in range(4, S, 14):
            a.ink([(i * w + 5, y), (i * w + 5, y + 6)], FINE * 0.8, color=shade(c1, 0.45), alpha=0.6, taper=False, wob=0)
    a.tile = True
    for _ in range(6):
        y = a.rng.uniform(0, S)
        x = a.rng.uniform(0, S)
        a.ink([(x, y), (x + a.rng.uniform(60, 140), y + a.rng.uniform(-10, 10))], FINE * 1.2, color=INK, alpha=0.25, wob=0.5)
    return a.image()


def seam_metal(seed, base, n=8, rust=0.0):
    """Standing-seam metal: smooth panels with raised seams; optional rust."""
    a = Art(S, S, seed, tile=True)
    _fill(a, base)
    w = S / n
    for i in range(n):
        x = i * w
        a.tile = False
        a.shape(rect(x + 3, -6, x + w - 3, S + 6), vary(a.rng, base, 0.03), outline=0, corner=0, wob=0, depth=2, shade_k=0.25, light_k=0.3, ao=0.05, mottle=0.05)
        a.tile = True
    a.tile = False
    for i in range(n + 1):
        a.ink([(i * w, -6), (i * w, S + 6)], DETAIL * 1.6, taper=False, wob=0.1, var=0.0)
        a.ink([(i * w + 3, -6), (i * w + 3, S + 6)], FINE * 1.1, color=tint(base, 0.5), alpha=0.85, taper=False, wob=0.1, var=0.0)
    a.tile = True
    for _ in range(int(rust * 40)):
        x, y = a.rng.uniform(0, S), a.rng.uniform(0, S)
        a.fill_path(_blob_path(blob(x, y, a.rng.uniform(6, 22), a.rng, 9, 0.35, ry=a.rng.uniform(12, 40))), rgb("#9a5a32"), 0.55)
    return a.image()


def oriental_tiles(seed, base, cols=10):
    """East-Asian style: rows of round-ended barrel tiles with dark end caps."""
    a = Art(S, S, seed, tile=True, bg=grout(base))
    w = S / cols
    rows = 8
    h = S / rows
    for r in range(rows):
        for i in range(cols):
            x = i * w
            y = r * h
            c = vary(a.rng, tint(base, 0.08), 0.03)
            a.shape(rect(x + 1.5, y, x + w - 1.5, y + h + 1), c, corner=w * 0.45, wob=0.2, depth=3, shade_k=0.45, light_k=0.35, ao=0.08, mottle=0.03, var=0.1, **_joint(c, lap=True))
            cap = shade(base, 0.25)
            a.shape(rect(x + 5, y + h - 9, x + w - 5, y + h - 1), cap, corner=4, wob=0.1, depth=1, shade_k=0, light_k=0, ao=0, mottle=0, **_joint(cap))
    return a.image()


# -- overlays -----------------------------------------------------------------------------


def _overlay(base_img, seed, draw):
    a = Art(S, S, seed, tile=True)
    draw(a)
    over = a.image(grain=0)
    out = base_img.copy()
    out.alpha_composite(over)
    return out


def snow(img, seed, amount=0.5):
    def draw(a):
        white = rgb("#f2f4f6")
        for _ in range(int(16 * amount) + 4):
            x, y = a.rng.uniform(0, S), a.rng.uniform(0, S)
            pts = blob(x, y, a.rng.uniform(40, 90), a.rng, 10, 0.3, ry=a.rng.uniform(16, 34))
            a.shape(chaikin(pts, True, 2), white, outline=DETAIL * 1.0, corner=0, wob=0.4, depth=4, shade_k=0.35, light_k=0.2, ao=0, mottle=0.02)

    return _overlay(img, seed, draw)


def moss(img, seed, amount=0.5):
    def draw(a):
        m = rgb("#6f9443")
        for _ in range(int(26 * amount) + 4):
            x, y = a.rng.uniform(0, S), a.rng.uniform(0, S)
            a.shape(chaikin(blob(x, y, a.rng.uniform(10, 30), a.rng, 9, 0.35), True, 2), vary(a.rng, m, 0.08), outline=0, corner=0, wob=0.3, depth=2, shade_k=0.3, light_k=0.3, ao=0, mottle=0.1)

    return _overlay(img, seed, draw)


def damage(img, seed):
    def draw(a):
        for _ in range(3):
            x, y = a.rng.uniform(60, S - 60), a.rng.uniform(60, S - 60)
            pts = blob(x, y, a.rng.uniform(26, 46), a.rng, 9, 0.35)
            a.shape(pts, rgb("#1e1a18"), outline=DETAIL * 1.2, corner=0, wob=0.5, depth=6, shade_k=0, light_k=0, ao=0.6, mottle=0)
            for k in range(3):
                t = a.rng.uniform(0, 6.28)
                a.ink([(x + 30 * math.cos(t), y + 30 * math.sin(t)), (x + 60 * math.cos(t), y + 60 * math.sin(t))], FINE * 1.2, alpha=0.8)

    return _overlay(img, seed, draw)


# -- lines --------------------------------------------------------------------------------


def snow_line(img, seed):
    """A snow cap along the top of a ridge/hip/edge strip."""
    a = Art(img.width, img.height, seed, tile=True)
    h = img.height
    pts = [(x, h * 0.45 + 3 * math.sin(2 * math.pi * x / SW * 5) + 2 * math.sin(2 * math.pi * x / SW * 11)) for x in range(-60, SW + 61, 8)]
    a.tile = False
    a.shape(pts + [(SW + 60, -5), (-60, -5)], rgb("#f2f4f6"), outline=0, corner=0, wob=0, depth=2, shade_k=0.3, light_k=0.2, ao=0, mottle=0)
    a.ink(pts, DETAIL * 0.9, wob=0.2, taper=False)
    a.tile = True
    out = img.copy()
    out.alpha_composite(a.image(grain=0))
    return out


def roof2(seed, base, tiles, line_kind="cap", post=None, line_post=None):
    """A roof from a tiles function (seed -> image) plus tex_build lines."""

    def make():
        t = tiles()
        if post:
            t = post(t)
        lines = [roof_line(seed + k, base, part, line_kind) for k, part in ((1, "edge"), (2, "ridge"), (3, "hip"))]
        if line_post:
            lines = [line_post(l) for l in lines]
        return (t, *lines)

    return make


def classic_tiles(seed, base, kind="shingle", rows=10):
    """tex_build.roof_tiles' piece kinds with thin tone-on-tone joints over a
    grout close to the tile colour (thatch keeps tex_build's drawing)."""
    if kind not in ("shingle", "slate", "clay", "scale", "stone", "bark"):
        return roof_tiles(seed, base, kind, rows)
    s = SW
    a = Art(s, s, seed, tile=True, bg=grout(base))
    h = s / rows
    lap = kind in ("shingle", "clay", "scale", "bark")
    g = 1.0
    for r in range(rows):
        w = {"shingle": h * 1.2, "slate": h * 1.6, "clay": h * 0.9, "scale": h * 1.0, "stone": h * 2.2, "bark": h * 1.4}[kind]
        n = max(1, round(s / w))
        w = s / n  # a whole number of tiles per row, so the row wraps cleanly
        x = 0 if r % 2 == 0 else -w / 2
        for _ in range(n):
            c = vary(a.rng, mix(base, tint(base, 0.2) if a.rng.random() < 0.5 else shade(base, 0.12), a.rng.uniform(0.2, 0.8)), 0.03)
            y0 = r * h
            if kind == "shingle":
                pts = [(x + g, y0), (x + w - g, y0), (x + w - g, y0 + h * 0.85), (x + w / 2, y0 + h - 0.5), (x + g, y0 + h * 0.85)]
            elif kind == "slate":
                pts = rect(x + g, y0, x + w - g, y0 + h - g)
            elif kind == "clay":
                pts = [(x + g, y0), (x + w - g, y0)] + [(x + w / 2 + (w / 2 - g) * math.cos(t), y0 + h * 0.65 + h * 0.34 * math.sin(t)) for t in [math.pi * k / 8 for k in range(9)]]
            elif kind == "scale":
                pts = [(x + 0.5, y0), (x + w - 0.5, y0)] + [(x + w / 2 + (w / 2 - 0.5) * math.cos(t), y0 + h * 0.5 + h * 0.5 * math.sin(t)) for t in [math.pi * k / 10 for k in range(11)]]
            elif kind == "stone":
                pts = [(px + a.rng.uniform(-1.5, 1.5), py) for px, py in rect(x + 1.5, y0 + 1, x + w - 1.5, y0 + h - 1)]
            else:  # bark
                pts = [(x + g, y0), (x + w - g, y0 + a.rng.uniform(-2, 2)), (x + w - 3, y0 + h * 0.9), (x + w * 0.55, y0 + h), (x + 3, y0 + h * 0.92)]
            det = None
            if kind == "clay":
                det = lambda art, p, x=x, y0=y0, w=w, c=c: art.ink([(x + w * 0.3, y0 + 4), (x + w * 0.3, y0 + h * 0.8)], FINE * 1.3, color=tint(c, 0.35), alpha=0.8, taper=False)
            elif kind in ("bark", "stone"):
                det = lambda art, p, c=c: speckles(art, p, shade(c, 0.45), 4)
            a.shape(pts, c, corner=2 if kind != "stone" else 4, wob=0.4, depth=3, shade_k=0.4, light_k=0.3, ao=0.08, mottle=0.03, detail=det, var=0.1, **_joint(c, lap))
            x += w
    return a.image()


def classic(seed, base, kind, rows, line_kind="cap", post=None, line_post=None):
    return roof2(seed, base, lambda: classic_tiles(seed, base, kind, rows), line_kind, post, line_post)


def C(h):
    return rgb(h)


ROOFS2 = {}


def add(name, maker):
    assert name not in ROOFS2, name
    ROOFS2[name] = maker


# Shingles.
for i, (name, col, rows) in enumerate([
    ("Cedar Shingles", "#a8653f", 10), ("Weathered Shingles", "#8a8278", 10), ("Silver Shingles", "#a9a59e", 11),
    ("Red Painted Shingles", "#9a3a32", 10), ("Green Painted Shingles", "#4f7a52", 10), ("Blue Painted Shingles", "#4a6488", 10),
    ("Small Shingles", "#8a5a3a", 14), ("Large Shingles", "#7a5236", 7), ("Pale Shingles", "#c09a6a", 10),
    ("Black Shingles", "#3e3a38", 10), ("Teal Shingles", "#3f7a7a", 10), ("Ochre Shingles", "#b08a3a", 10),
]):
    add(name, classic(1700 + i * 5, C(col), "shingle", rows))
# Slate.
for i, (name, col, rows) in enumerate([
    ("Grey Slate", "#7a7e84", 12), ("Light Slate", "#9aa0a8", 12), ("Green Slate", "#5a6e5e", 12), ("Purple Slate", "#5e5468", 12),
    ("Charcoal Slate", "#47484c", 13), ("Rough Slate", "#6a6e74", 9), ("Fine Slate", "#5d6670", 16), ("Rust Slate", "#7a5e4e", 12),
    ("Welsh Slate", "#52586a", 12), ("Pale Blue Slate", "#7a8ea6", 12),
]):
    add(name, classic(1800 + i * 5, C(col), "slate", rows))
# Classic clay (pantile) colors.
for i, (name, col) in enumerate([
    ("Terracotta Pantiles", "#c06a45"), ("Dark Red Pantiles", "#8e3a2e"), ("Yellow Clay Tiles", "#d0a24a"),
    ("Green Glazed Tiles", "#4f8a5e"), ("Black Glazed Tiles", "#34363c"), ("Turquoise Glazed Tiles", "#3f9aa0"),
    ("Weathered Clay Tiles", "#a8775e"),
]):
    add(name, classic(1900 + i * 5, C(col), "clay", 11))
# Barrel (spanish) tiles.
for i, (name, col) in enumerate([
    ("Red Barrel Tiles", "#b8563c"), ("Orange Barrel Tiles", "#cf7a42"), ("Brown Barrel Tiles", "#8e5c42"),
    ("Blue Barrel Tiles", "#4f74a8"), ("Green Barrel Tiles", "#4f8a5e"), ("Sun-bleached Barrel Tiles", "#d8a882"),
]):
    add(name, roof2(2000 + i * 5, C(col), (lambda s=2000 + i * 5, c=C(col): barrel_tiles(s, c))))
# Flat interlocking tiles.
for i, (name, col) in enumerate([
    ("Red Flat Tiles", "#a84a3a"), ("Brown Flat Tiles", "#7a5240"), ("Grey Flat Tiles", "#6e7076"),
    ("Black Flat Tiles", "#3a3a40"), ("Orange Flat Tiles", "#c0703e"),
]):
    add(name, roof2(2100 + i * 5, C(col), (lambda s=2100 + i * 5, c=C(col): flat_tiles(s, c))))
# Thatch.
for i, (name, col, rows) in enumerate([
    ("Fresh Thatch", "#d8b866", 8), ("Old Thatch", "#a08a5a", 8), ("Grey Thatch", "#9a9278", 8),
    ("Golden Reed", "#d0b25a", 12), ("Straw Roof", "#e0c27a", 10), ("Heather Thatch", "#7a6a5a", 9),
]):
    add(name, classic(2200 + i * 5, C(col), "thatch", rows, "thatch"))
add("Mossy Thatch", classic(2240, C("#a8955e"), "thatch", 8, "thatch", post=lambda im: moss(im, 2241, 0.7)))
add("Snowy Thatch", classic(2245, C("#c9a961"), "thatch", 8, "thatch", post=lambda im: snow(im, 2246, 0.6), line_post=lambda im: snow_line(im, 2247)))
# Metal.
for i, (name, col, rust) in enumerate([
    ("New Copper", "#c97a4a", 0), ("Aged Copper", "#5fa08a", 0), ("Lead Roof", "#7a7e86", 0), ("Tin Roof", "#a9adb4", 0),
    ("Rusted Iron Roof", "#7a7e84", 0.7), ("Gold Roof", "#d6ae4c", 0), ("Blue Steel Roof", "#5a6e8a", 0),
    ("Red Metal Roof", "#9a3a32", 0.2), ("Rusty Tin Roof", "#a0a2a4", 1.0),
]):
    add(name, roof2(2300 + i * 5, C(col), (lambda s=2300 + i * 5, c=C(col), r=rust: seam_metal(s, c, rust=r)), "band"))
# Stone slabs.
for i, (name, col, rows) in enumerate([
    ("Grey Stone Slabs", "#8e8a84", 7), ("Sandstone Slabs", "#c9b088", 7), ("Dark Stone Slabs", "#6a6662", 7),
    ("Large Stone Slabs", "#9a958c", 5), ("Red Stone Slabs", "#a0705a", 7),
]):
    add(name, classic(2400 + i * 5, C(col), "stone", rows))
add("Mossy Stone Slabs", classic(2430, C("#8a8a7e"), "stone", 7, post=lambda im: moss(im, 2431, 0.8)))
# Bark / wood.
add("Birch Bark Roof", classic(2450, C("#d8d2c4"), "bark", 9))
add("Dark Bark Roof", classic(2455, C("#5a4232"), "bark", 9))
for i, (name, col) in enumerate([("Wooden Planks Roof", "#8a6a48"), ("Dark Plank Roof", "#5e4a38"), ("Grey Plank Roof", "#8a8680"), ("Red Plank Roof", "#8e4a3a")]):
    add(name, roof2(2500 + i * 5, C(col), (lambda s=2500 + i * 5, c=C(col): plank_roof(s, c)), "band"))
# Turf and leaf.
add("Turf Roof", roof2(2600, C("#6f9443"), lambda: turf_roof(2600)))
add("Dry Turf Roof", roof2(2605, C("#9a9a5a"), lambda: turf_roof(2605, C("#9a9a5a"))))
add("Snowy Turf Roof", roof2(2610, C("#6f9443"), lambda: turf_roof(2610), post=lambda im: snow(im, 2611, 0.9), line_post=lambda im: snow_line(im, 2612)))
add("Palm Thatch", roof2(2620, C("#a8a050"), lambda: palm_thatch(2620), "thatch"))
add("Green Leaf Thatch", roof2(2625, C("#6f9443"), lambda: palm_thatch(2625, C("#6f9443")), "thatch"))
add("Dry Leaf Thatch", roof2(2630, C("#b08a52"), lambda: palm_thatch(2630, C("#b08a52")), "thatch"))
# Scales and hexagons.
for i, (name, col) in enumerate([
    ("Blue Scale", "#4f6e9a"), ("Purple Scale", "#6e5486"), ("Black Scale", "#3e3e44"), ("Copper Scale", "#c97a4a"),
    ("Teal Scale", "#3f8a86"), ("White Scale", "#d8d6d0"), ("Brown Scale", "#7a5a44"),
]):
    add(name, classic(2700 + i * 5, C(col), "scale", 14))
for i, (name, col) in enumerate([
    ("Hexagonal Slate", "#5d6670"), ("Red Hexagonal Tiles", "#a84a3a"), ("Green Hexagonal Tiles", "#5a7a52"),
    ("Sandstone Hexagons", "#c9b088"), ("Black Hexagonal Tiles", "#3e3e44"),
]):
    add(name, roof2(2800 + i * 5, C(col), (lambda s=2800 + i * 5, c=C(col): hex_tiles(s, c))))
# Oriental.
for i, (name, col) in enumerate([("Grey Oriental Tiles", "#6e7276"), ("Green Oriental Tiles", "#4f7a5a"), ("Blue Oriental Tiles", "#4a6488"), ("Gold Oriental Tiles", "#c9a24a"), ("Red Oriental Tiles", "#a0402e")]):
    add(name, roof2(2900 + i * 5, C(col), (lambda s=2900 + i * 5, c=C(col): oriental_tiles(s, c))))
# Canvas.
for i, (name, c1, c2) in enumerate([
    ("Red Striped Canvas", "#b23a32", "#e6dcc4"), ("Blue Striped Canvas", "#3f6290", "#e6dcc4"), ("Green Striped Canvas", "#4f7a52", "#e6dcc4"),
    ("Plain Canvas", "#d8ccb0", "#cfc2a4"), ("Gold Striped Canvas", "#c9a24a", "#7a2e2a"), ("Purple Striped Canvas", "#6e5486", "#e6dcc4"),
]):
    add(name, roof2(3000 + i * 5, C(c1), (lambda s=3000 + i * 5, a=C(c1), b=C(c2): canvas_roof(s, a, b)), "band"))
# Snowy, mossy and damaged versions of classics.
add("Snowy Shingles", classic(3100, C("#8a5a3a"), "shingle", 10, post=lambda im: snow(im, 3101, 0.6), line_post=lambda im: snow_line(im, 3102)))
add("Snowy Slate", classic(3105, C("#5d6670"), "slate", 12, post=lambda im: snow(im, 3106, 0.6), line_post=lambda im: snow_line(im, 3107)))
add("Snowy Clay Tiles", classic(3110, C("#b0503a"), "clay", 11, post=lambda im: snow(im, 3111, 0.6), line_post=lambda im: snow_line(im, 3112)))
add("Snowy Planks", roof2(3115, C("#8a6a48"), lambda: plank_roof(3115, C("#8a6a48")), "band", post=lambda im: snow(im, 3116, 0.7), line_post=lambda im: snow_line(im, 3117)))
add("Heavy Snow Roof", classic(3120, C("#5e4232"), "shingle", 10, post=lambda im: snow(im, 3121, 1.6), line_post=lambda im: snow_line(im, 3122)))
add("Mossy Slate", classic(3125, C("#5d6670"), "slate", 12, post=lambda im: moss(im, 3126, 0.7)))
add("Mossy Clay Tiles", classic(3130, C("#a0503a"), "clay", 11, post=lambda im: moss(im, 3131, 0.6)))
add("Overgrown Shingles", classic(3135, C("#6e5a42"), "shingle", 10, post=lambda im: moss(im, 3136, 1.3)))
add("Damaged Shingles", classic(3140, C("#7a5236"), "shingle", 10, post=lambda im: damage(im, 3141)))
add("Damaged Slate", classic(3145, C("#5d6670"), "slate", 12, post=lambda im: damage(im, 3146)))
add("Damaged Thatch", classic(3150, C("#a8955e"), "thatch", 8, "thatch", post=lambda im: damage(im, 3151)))
add("Ruined Clay Tiles", classic(3155, C("#a0503a"), "clay", 11, post=lambda im: damage(moss(im, 3156, 0.5), 3157)))
add("Damaged Planks", roof2(3160, C("#7a5a3e"), lambda: plank_roof(3160, C("#7a5a3e")), "band", post=lambda im: damage(im, 3161)))
