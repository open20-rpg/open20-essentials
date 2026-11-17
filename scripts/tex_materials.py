"""Materials for the Material brush, as packs ship them (textures/materials/):
each one a seamless tile texture plus a border strip drawn along the edge of
whatever is painted with it. The tiles are the pack's own grounds (terrains
and floors, made opaque); the borders are drawn here in the same inked style.

A border strip is BW px wide (periodic along x, so it tiles along the line)
and as tall as the border is wide on the map (256 px = one tile). The editor
centers it on the material's outline with its top toward the outside: the
lower half overlaps the material and fades into it, the upper half is the
edge spilling out — tufts of grass, a rim of pebbles, a kerb of stones…"""

import math

import numpy as np
from PIL import Image

from pen import FINE, Art, blob, chaikin, rgb, shade, tint, to_path, vary
from tex_ground import FLOORS, TERRAINS, dot
from tex_terrain2 import TERRAINS2

BW = 512  # border strip width (px): two tiles, like the 512 px ground tiles
GROUNDS = {**TERRAINS, **TERRAINS2, **FLOORS}


def C(c):
    """A color given as hex or as an (r, g, b) tuple."""
    return tuple(c) if isinstance(c, tuple) else rgb(c)


def opaque(img):
    """A ground texture as a material tile: terrain alpha is a blend height,
    not transparency."""
    img = img.convert("RGBA")
    img.putalpha(255)
    return img


def average(img):
    a = np.asarray(img.convert("RGB"), dtype=np.float64)
    return tuple(int(v) for v in a.reshape(-1, 3).mean(axis=0))


def wrap(x):
    """The copies of something at x that the strip shows (it tiles along x)."""
    return [x + d for d in (-BW, 0, BW) if -60 < x + d < BW + 60]


def wave(rng, y0, amp, waves=(2, 5, 9), n=160):
    """A periodic wavy line across the strip (sampled a little past both ends)."""
    ph = [rng.uniform(0, 6.28) for _ in waves]
    xs = np.linspace(-40, BW + 40, n)
    return [(x, y0 + sum(amp / (1 + i) * math.sin(2 * math.pi * x / BW * k + ph[i]) for i, k in enumerate(waves))) for x in xs]


def _edge_at(line, x):
    """y of a line (sorted by x) at x."""
    for (x0, y0), (x1, y1) in zip(line, line[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0) if x1 > x0 else 0
            return y0 + (y1 - y0) * t
    return line[-1][1]


# -- silhouettes: the strip's outer edge, as a polyline across it ------------------------------------


def scallops(rng, y0, r=(10, 18), lift=0.8):
    """Rounded bumps (moss, snow, bushes): arcs side by side."""
    pts = []
    x = -40.0
    while x < BW + 40:
        w = rng.uniform(*r) * 2
        h = w / 2 * lift * rng.uniform(0.6, 1.0)
        for k in range(9):
            t = k / 8
            pts.append((x + w * t, y0 - h * math.sin(math.pi * t)))
        x += w
    return pts


def blades(rng, y0, w=(14, 24), h=(10, 20)):
    """Clumps of grass blades: a saw of pointed tips over a gentle wave."""
    base = wave(rng, y0, 3)
    pts = []
    x = -40.0
    while x < BW + 40:
        cw = rng.uniform(*w)
        tips = rng.randint(3, 5)
        top = rng.uniform(*h)
        for k in range(tips):
            xa = x + cw * k / tips
            xb = x + cw * (k + 0.5) / tips
            pts.append((xa, _edge_at(base, xa) - top * 0.25))
            pts.append((xb + rng.uniform(-2, 2), _edge_at(base, xb) - top * rng.uniform(0.6, 1.0)))
        x += cw
    return pts


def jagged(rng, y0, step=(8, 18), amp=(4, 14)):
    """Sharp, broken edge (ice, lava crust, crystal)."""
    pts = []
    x = -40.0
    up = True
    while x < BW + 40:
        pts.append((x, y0 - (rng.uniform(*amp) if up else rng.uniform(0, 3))))
        x += rng.uniform(*step)
        up = not up
    return pts


# -- decorations along the edge -----------------------------------------------------------------------


def stones_along(a, line, cols, r=(4, 7), every=(9, 15), dy=(-4, 6), outline=1.8, depth=2):
    x = 0.0
    while x < BW:
        rr = a.rng.uniform(*r)
        y = _edge_at(line, x) + a.rng.uniform(*dy)
        c = vary(a.rng, C(a.rng.choice(cols)), 0.06)
        for xx in wrap(x):
            a.shape(blob(xx, y, rr, a.rng, 8, 0.22), c, outline=outline, corner=0, wob=0.2, depth=depth, shade_k=0.4, light_k=0.4, ao=0, mottle=0)
        x += a.rng.uniform(*every)


def specks_along(a, line, col, n=220, spread=(-14, 10), r=(0.8, 2.0), alpha=0.65):
    for _ in range(n):
        x = a.rng.uniform(0, BW)
        y = _edge_at(line, x) + a.rng.uniform(*spread)
        for xx in wrap(x):
            dot(a, xx, y, a.rng.uniform(*r), C(col), alpha)


def strokes_inside(a, line, col, n=360, ln=(6, 14), depth=(2, 26), w=1.6, alpha=0.7):
    """Short upright marks just inside the edge (grass blades, moss fibres)."""
    for _ in range(n):
        x = a.rng.uniform(0, BW)
        y = _edge_at(line, x) + a.rng.uniform(*depth)
        t = -math.pi / 2 + a.rng.uniform(-0.45, 0.45)
        L = a.rng.uniform(*ln)
        for xx in wrap(x):
            a.ink([(xx, y), (xx + L * math.cos(t), y + L * math.sin(t))], w, color=C(col), alpha=alpha, wob=0.1, var=0.1, taper=True)


def flowers_along(a, line, cols, n=46, r=3.2):
    for _ in range(n):
        x = a.rng.uniform(0, BW)
        y = _edge_at(line, x) + a.rng.uniform(-2, 10)
        c = C(a.rng.choice(cols))
        for xx in wrap(x):
            for k in range(5):
                t = 2 * math.pi * k / 5
                dot(a, xx + r * 1.3 * math.cos(t), y + r * 1.3 * math.sin(t), r, c, 0.95)
            dot(a, xx, y, r * 0.6, rgb("#e6b84a"))


def leaves_along(a, line, cols, n=70, size=(10, 17)):
    for _ in range(n):
        x = a.rng.uniform(0, BW)
        y = _edge_at(line, x) + a.rng.uniform(-6, 8)
        t = a.rng.uniform(0, 6.28)
        L = a.rng.uniform(*size)
        W = L * a.rng.uniform(0.35, 0.45)
        ux, uy = math.cos(t), math.sin(t)
        c = vary(a.rng, C(a.rng.choice(cols)), 0.06)
        for xx in wrap(x):
            pts = [(xx - ux * L / 2, y - uy * L / 2), (xx - uy * W / 2, y + ux * W / 2), (xx + ux * L / 2, y + uy * L / 2), (xx + uy * W / 2, y - ux * W / 2)]
            a.shape(chaikin(pts, True, 1), c, outline=1.5, corner=0, wob=0.1, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)


def kerb_stones(seed, y0, h, cols, w=(28, 42)):
    """A row of dressed stones across the strip (a cobbled area's curb):
    [(x, width, top, color)], their tops being the edge."""
    import random

    rng = random.Random(seed)
    out = []
    x = 0.0
    while x < BW - 6:
        sw = min(rng.uniform(*w), BW - x)
        out.append((x, sw, y0 + rng.uniform(-1.5, 1.5), vary(rng, C(rng.choice(cols)), 0.07)))
        x += sw
    return out


def kerb_edge(stones):
    pts = []
    for x, sw, top, _c in stones:
        pts += [(x, top), (x + sw, top)]
    first, last = stones[0], stones[-1]
    return [(-40, last[2])] + pts + [(BW + 40, first[2])]


def draw_kerb(a, stones, h):
    for x, sw, top, c in stones:
        for xx in wrap(x):
            pts = chaikin([(xx + 1.5, top), (xx + sw - 1.5, top), (xx + sw - 1.5, top + h), (xx + 1.5, top + h)], True, 2)
            a.shape(pts, c, outline=2.2, corner=0, wob=0.25, depth=3, shade_k=0.45, light_k=0.35, ao=0.1, mottle=0.02)


# -- the strip ------------------------------------------------------------------------------------------


def border(tile, seed, h, edge, decorate=None, ink=0.55, ink_w=2.6, fade=(0.62, 0.96)):
    """A border strip `h` px tall: the tile's texture below `edge` (a
    silhouette polyline across the strip, built from the strip's rng), faded
    out toward the bottom, inked along the edge, then `decorate(art, line)`."""
    a = Art(BW, h, seed)
    line = edge(a.rng)
    poly = line + [(BW + 40, h + 4), (-40, h + 4)]
    mask = Art(BW, h, seed)
    mask.fill_path(to_path(poly), (255, 255, 255))
    alpha = np.asarray(mask.image(grain=0, scale=1))[..., 3].astype(np.float64) / 255
    ys = np.arange(h)[:, None] / h
    alpha *= np.clip((fade[1] - ys) / (fade[1] - fade[0]), 0, 1)
    base = average(tile)
    tex = np.asarray(tile.convert("RGB"))
    strip = np.tile(tex[:h], (1, BW // tex.shape[1] + 1, 1))[:, :BW]
    body = np.dstack([strip, (alpha * 255).astype(np.uint8)])
    out = Image.fromarray(body.astype(np.uint8), "RGBA")
    a.ink(line, ink_w, color=shade(base, ink), alpha=0.9, taper=False, wob=0.0, var=0.1)
    if decorate:
        decorate(a, line, base)
    return Image.alpha_composite(out, a.image(grain=0.02, scale=1))


def material(ground, seed, h, edge, decorate=None, **kw):
    def make():
        tile = opaque(GROUNDS[ground]())
        return tile, border(tile, seed, h, edge, decorate, **kw)

    return make


# -- the catalog ------------------------------------------------------------------------------------------


def grass_decor(cols=None, flowers=None):
    def f(a, line, base):
        strokes_inside(a, line, shade(base, 0.45), n=320)
        strokes_inside(a, line, tint(base, 0.3), n=120, alpha=0.5)
        if flowers:
            flowers_along(a, line, flowers)

    return f


def pebble_decor(cols, r=(4, 7), every=(8, 14), specks=None):
    def f(a, line, base):
        if specks:
            specks_along(a, line, specks)
        stones_along(a, line, cols, r=r, every=every)

    return f


def specks_decor(col, n=260, spread=(-16, 10), stones=None):
    def f(a, line, base):
        specks_along(a, line, col, n=n, spread=spread)
        if stones:
            stones_along(a, line, stones, r=(3.5, 6.5), every=(18, 36), dy=(-12, 4), outline=1.6, depth=1.6)

    return f


def cobble_kerb(cols, seed=9011, h=88):
    """Cobblestones edged by a kerb: the kerb's stones are the silhouette."""

    def make():
        tile = opaque(GROUNDS["Cobblestone"]())
        stones = kerb_stones(seed, h * 0.3, h * 0.38, cols)
        return tile, border(tile, seed, h, lambda _rng: kerb_edge(stones), lambda a, _l, _b: draw_kerb(a, stones, h * 0.38), ink_w=0.01)

    return make


MATERIALS = {
    "Grass": material("Lush Grass", 9001, 160, lambda r: blades(r, 84, w=(22, 38), h=(20, 36)), grass_decor()),
    "Meadow": material("Wildflower Meadow", 9002, 160, lambda r: blades(r, 84, w=(22, 38), h=(16, 30)), grass_decor(flowers=("#f3eee2", "#e6b84a", "#c86ab8", "#c8443a", "#6f8fd0"))),
    "Moss": material("Thick Moss", 9003, 128, lambda r: scallops(r, 68, (9, 16)), lambda a, l, b: strokes_inside(a, l, shade(b, 0.4), n=420, ln=(3, 7), depth=(1, 20))),
    "Leaf Litter": material("Leaf Litter", 9004, 128, lambda r: wave(r, 66, 5), lambda a, l, b: leaves_along(a, l, ("#a8642e", "#c88a3a", "#8a5a2e", "#b8a040"), n=90, size=(14, 24))),
    "Dirt": material("Dirt", 9005, 112, lambda r: wave(r, 58, 7), specks_decor("#6e5236", spread=(-22, 14), stones=("#988c7e", "#8a7e70"))),
    "Mud": material("Wet Mud", 9006, 112, lambda r: scallops(r, 58, (20, 36), 0.45), lambda a, l, b: specks_along(a, l, "#3e2e22", n=200, spread=(-6, 18), r=(0.8, 2.2))),
    "Sand": material("Sand", 9007, 104, lambda r: wave(r, 54, 6, (2, 4, 7)), specks_decor("#b89a62", n=420, spread=(-24, 12)), ink=0.75, ink_w=1.8),
    "Gravel": material("Gravel", 9008, 104, lambda r: wave(r, 54, 3), pebble_decor(("#a9a59d", "#8a867f", "#9d978d"), r=(5, 9), every=(9, 15), specks="#6e6a62")),
    "Rubble": material("Rubble Ground", 9009, 128, lambda r: wave(r, 66, 4), pebble_decor(("#9e9a90", "#8a867c", "#a8a294"), r=(9, 16), every=(16, 28))),
    "Snow": material("Snow", 9010, 128, lambda r: scallops(r, 66, (20, 34), 0.5), specks_decor("#ffffff", n=160, spread=(-14, 6)), ink=0.82, ink_w=2.0),
    "Cobblestone": cobble_kerb(("#9a948a", "#8a847a", "#a8a296")),
    "Ice": material("Ice", 9012, 112, lambda r: jagged(r, 60, (12, 26), (6, 22)), lambda a, l, b: specks_along(a, l, "#f4fbff", n=110, spread=(-10, 10), r=(1.2, 3), alpha=0.8), ink=0.6),
    "Lava": material("Glowing Lava Crust", 9013, 128, lambda r: jagged(r, 66, (14, 28), (8, 18)), pebble_decor(("#3a3230", "#2e2826", "#4a403a"), r=(6, 12), every=(14, 24))),
    "Swamp": material("Swamp Muck", 9014, 128, lambda r: scallops(r, 66, (14, 28), 0.5), lambda a, l, b: (specks_along(a, l, "#6e8a3a", n=260, spread=(-3, 20), r=(1.4, 3.4), alpha=0.8), strokes_inside(a, l, "#3e5a2a", n=120, ln=(7, 14)))),
    "Ash": material("Ash", 9015, 104, lambda r: wave(r, 54, 5, (3, 6, 11)), specks_decor("#3e3a36", n=400, spread=(-26, 12)), ink=0.65, ink_w=1.8),
    "Crystal": material("Crystal Ground", 9016, 128, lambda r: jagged(r, 66, (9, 20), (9, 24)), lambda a, l, b: specks_along(a, l, "#e8f4ff", n=120, spread=(-12, 8), r=(1.4, 2.8), alpha=0.9)),
}
