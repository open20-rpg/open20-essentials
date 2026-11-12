"""More cave styles and light shapes for the built-in pack.

CAVES2: each style returns (floor 512x512 seamless, wall strip 512xH periodic
along x), light greys so the cave's colour tints them. Floors are built from
structural features (crack networks, strata, pebble beds, shards, puddles,
bones, ripples, ice plates, roots, moss, veins, fungus, dripstone, basalt
columns, terraces...) combined per style so they read clearly different.

LIGHTS2: 512x512 white RGBA shapes with alpha falloff (the editor tints
them), complementing tex_ground.LIGHTS."""

import math

import numpy as np

from floors import crack, inset, speckles, split, voronoi_cells
from pen import DETAIL, FINE, INK, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary
from tex_build import SW, band, dot, strip
from tex_ground import LS, _edge, _grid, _light, _noise

GREY = rgb("#d2d0cb")
LIGHTER = rgb("#dedcd7")
DARKER = rgb("#bcbab4")


# -- floor features --------------------------------------------------------------------------------


def f_patches(a, base, n=30, size=(20, 50)):
    s = a.w
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        col = mix(base, shade(base, 0.12) if a.rng.random() < 0.5 else tint(base, 0.18), 0.6)
        a.shape(blob(x, y, a.rng.uniform(*size), a.rng, 12, 0.3), col, outline=0, smooth=True, depth=2, shade_k=0, light_k=0, ao=0, mottle=0.04)


def f_dots(a, base, n=300, r=(0.5, 1.1), alpha=0.45):
    s = a.w
    for _ in range(n):
        dot(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(*r), shade(base, 0.4), alpha)


def f_pebbles(a, base, n=80, r=(3, 8), outline=DETAIL * 0.8):
    s = a.w
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        col = vary(a.rng, shade(base, a.rng.uniform(0.02, 0.16)), 0.05)
        a.shape(blob(x, y, a.rng.uniform(*r), a.rng, 9, 0.25), col, outline=outline, smooth=True, depth=2, shade_k=0.4, light_k=0.4, mottle=0)


def f_cracknet(a, base, cols=6, width=FINE * 1.4, jitter=0.4):
    """A network of cracks along the edges of a periodic Voronoi diagram."""
    s = a.w
    for (cx, cy), poly in voronoi_cells(s, s, cols, cols, a.rng, jitter):
        if len(poly) < 3:
            continue
        pts = [(x + a.rng.uniform(-2, 2), y + a.rng.uniform(-2, 2)) for x, y in poly]
        a.ink(pts, width, closed=True, color=shade(base, 0.55), alpha=0.8, wob=1.0)


def f_cracks(a, base, n=14, L=(40, 90)):
    s = a.w
    for _ in range(n):
        crack(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0, 6.28), a.rng.uniform(*L), width=FINE * 1.2)


def f_slabs(a, base, cols=5, jitter=0.35, outline=DETAIL * 1.2, corner=10, gap=4):
    s = a.w
    for (cx, cy), poly in voronoi_cells(s, s, cols, cols, a.rng, jitter):
        if len(poly) < 3:
            continue
        a.shape(inset(poly, gap), vary(a.rng, base, 0.05), outline=outline, corner=corner, depth=5, shade_k=0.4, light_k=0.3)


def f_basalt(a, base, n=6):
    """Hexagonal column tops (basalt)."""
    s = a.w
    w = s / n
    r = w / math.sqrt(3)
    rows = int(round(s / (1.5 * r)))
    if rows % 2:
        rows += 1
    r = s / rows / 1.5
    for j in range(rows):
        for i in range(n):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * 1.5 * r
            rr = r - 3
            pts = [(cx + rr * math.sin(k * math.pi / 3), cy + rr * math.cos(k * math.pi / 3)) for k in range(6)]
            a.shape(pts, vary(a.rng, base, 0.06), outline=DETAIL * 1.1, corner=3, depth=4, shade_k=0.45, light_k=0.35)


def f_strata(a, base, n=8, amp=10):
    """Wavy layered bands across the floor, periodic both ways. Drawn
    without wrapped copies and past the edges (rows -1..n), so no band's
    shaded ends fall inside the tile."""
    s = a.w
    h = s / n
    ph = a.rng.uniform(0, 6.28)
    cols = [vary(a.rng, shade(base, 0.04 * (r % 3)), 0.03) for r in range(n)]

    def edge(r, step):
        return [(x, r * h + amp * math.sin(2 * math.pi * x / s * 2 + ph + 2 * math.pi * r / n)) for x in range(-64, s + 65, step)]

    tile = a.tile
    a.tile = False
    for r in range(-1, n + 1):
        a.shape(edge(r, 16) + edge(r + 1, 16)[::-1], cols[r % n], outline=0, corner=0, wob=0, depth=3, shade_k=0.25, light_k=0.2, ao=0, mottle=0)
    for r in range(-1, n + 2):
        a.ink(edge(r, 8), DETAIL * 0.9, color=shade(base, 0.45), alpha=0.85, wob=0.0, taper=False, var=0.0)
    a.tile = tile

def f_terraces(a, base, n=7):
    """Contour lines of a gently stepped floor: irregular wavy lines across
    the tile at uneven spacing (periodic in both directions)."""
    s = a.w
    ys = sorted(a.rng.uniform(0, s) for _ in range(n))
    for i, y in enumerate(ys):
        k1, k2 = a.rng.choice((1, 2)), a.rng.choice((3, 4, 5))
        a1, a2 = a.rng.uniform(10, 26), a.rng.uniform(3, 8)
        p1, p2 = a.rng.uniform(0, 6.28), a.rng.uniform(0, 6.28)
        pts = [(x, y + a1 * math.sin(2 * math.pi * x / s * k1 + p1) + a2 * math.sin(2 * math.pi * x / s * k2 + p2)) for x in range(0, s + 1, 8)]
        a.ink(pts, FINE * 1.3, color=shade(base, 0.4), alpha=0.8, wob=0.5, taper=False)
        a.ink([(x, py + 4) for x, py in pts], FINE * 0.8, color=shade(base, 0.2), alpha=0.5, wob=0.5, taper=False)


def f_ripples(a, base, n=18, amp=5):
    s = a.w
    for r in range(n):
        y = r * s / n + a.rng.uniform(-4, 4)
        k = a.rng.choice((2, 3, 4))
        a.ink([(x, y + amp * math.sin(2 * math.pi * x / s * k + r)) for x in range(-20, s + 21, 12)], FINE * 1.2, color=shade(base, 0.32), alpha=0.75, wob=0.2)


def f_shards(a, base, n=26, L=(26, 44)):
    """Angular broken shards in small clusters (fanning from a point)."""
    s = a.w
    for _ in range(max(1, n // 3)):
        cx, cy = a.rng.uniform(0, s), a.rng.uniform(0, s)
        rot = a.rng.uniform(0, 6.28)
        for k in range(a.rng.randint(2, 4)):
            t = rot + k * a.rng.uniform(0.6, 1.2)
            ln, wd = a.rng.uniform(*L), a.rng.uniform(6, 10)
            ux, uy = math.cos(t), math.sin(t)
            x, y = cx + ux * ln * 0.6, cy + uy * ln * 0.6
            pts = [(x - ux * ln * 0.6, y - uy * ln * 0.6), (x - uy * wd + ux * ln * 0.1, y + ux * wd + uy * ln * 0.1), (x + ux * ln, y + uy * ln), (x + uy * wd * 0.7 + ux * ln * 0.3, y - ux * wd * 0.7 + uy * ln * 0.3)]
            a.shape(pts, tint(base, 0.3), outline=DETAIL, corner=0, wob=0.1, depth=2, light_k=0.7, mottle=0)
            a.ink([pts[0], pts[2]], FINE * 0.8, color=shade(base, 0.2), alpha=0.6, wob=0)


def f_crystals(a, base, n=24):
    s = a.w
    for _ in range(n):
        cx, cy = a.rng.uniform(0, s), a.rng.uniform(0, s)
        for _ in range(a.rng.randint(1, 3)):
            x, y, r = cx + a.rng.uniform(-14, 14), cy + a.rng.uniform(-14, 14), a.rng.uniform(9, 18)
            pts = [(x + r * math.cos(k * math.pi / 3 + 0.3), y + r * math.sin(k * math.pi / 3 + 0.3)) for k in range(6)]
            a.shape(pts, tint(base, 0.28), outline=DETAIL, corner=1, depth=2, light_k=0.6, mottle=0)
            for p in pts[::2]:
                a.ink([(x, y), p], FINE * 0.8, color=shade(base, 0.25), alpha=0.6, wob=0)


def f_puddles(a, base, n=10, r=(26, 58)):
    s = a.w
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(*r), a.rng, 11, 0.25), tint(base, 0.14), outline=DETAIL * 0.9, smooth=True, depth=4, shade_k=0, light_k=0, ao=0.5, mottle=0,
                detail=lambda art, p, x=x, y=y: art.ink([(x - 10, y - 4), (x + 6, y - 7)], FINE * 1.3, color=(250, 250, 250), alpha=0.9))


def f_bones(a, base, n=12):
    s = a.w
    bone = tint(base, 0.32)
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, math.pi)
        L = a.rng.uniform(12, 22)
        ux, uy = math.cos(t), math.sin(t)
        for e in (-1, 1):
            for k in (-1, 1):
                a.shape(ellipse(x + ux * e * L - uy * k * 3.5, y + uy * e * L + ux * k * 3.5, 4.5, 4.5, 12), bone, outline=FINE * 1.2, depth=1, mottle=0)
        a.ink([(x - ux * L, y - uy * L), (x + ux * L, y + uy * L)], 9, color=INK, taper=False)
        a.ink([(x - ux * L, y - uy * L), (x + ux * L, y + uy * L)], 5.5, color=bone, taper=False)


def f_roots(a, base, n=7):
    """Long smooth roots snaking across the floor, a few side roots."""
    s = a.w
    col = shade(base, 0.25)
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        pts = [(x, y)]
        for _ in range(12):
            t += a.rng.uniform(-0.25, 0.25)
            x += 18 * math.cos(t)
            y += 18 * math.sin(t)
            pts.append((x, y))
        pts = chaikin(pts, False, 2)
        a.ink(pts, 11, color=INK, taper=True, wob=0.3)
        a.ink(pts, 7, color=col, taper=True, wob=0.3)
        for j in (len(pts) // 3, 2 * len(pts) // 3):
            bx, by = pts[j]
            px_, py_ = pts[j - 1]
            bt = math.atan2(by - py_, bx - px_) + a.rng.choice((-1, 1)) * 0.7
            side = chaikin([(bx, by), (bx + 20 * math.cos(bt), by + 20 * math.sin(bt)), (bx + 40 * math.cos(bt + 0.3), by + 40 * math.sin(bt + 0.3))], False, 2)
            a.ink(side, 6, color=INK, taper=True)
            a.ink(side, 3.5, color=col, taper=True)


def f_moss(a, base, n=20, r=(16, 36)):
    s = a.w
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(*r), a.rng, 10, 0.35), shade(base, 0.18), outline=DETAIL * 0.7, smooth=True, depth=3, shade_k=0.2, light_k=0.3, ao=0, mottle=0.1,
                detail=lambda art, p: speckles(art, p, shade(base, 0.45), 30, (0.6, 1.3), 0.7))


def f_veins(a, base, n=6):
    """Bright veins (lava, quartz) branching across a darker crust."""
    s = a.w
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        pts = [(x, y)]
        for _ in range(22):
            t += a.rng.uniform(-0.45, 0.45)
            x += 13 * math.cos(t)
            y += 13 * math.sin(t)
            pts.append((x, y))
        a.ink(pts, 10, color=shade(base, 0.5), alpha=0.9, taper=True, wob=0.4)
        a.ink(pts, 4.5, color=tint(base, 0.65), alpha=1.0, taper=True, wob=0.4)
        bx, by = pts[11]
        bt = t + 1.2
        br = [(bx + k * 12 * math.cos(bt + 0.1 * k), by + k * 12 * math.sin(bt + 0.1 * k)) for k in range(7)]
        a.ink(br, 7, color=shade(base, 0.5), alpha=0.9, taper=True)
        a.ink(br, 3, color=tint(base, 0.65), taper=True)


def f_fungus(a, base, n=16):
    s = a.w
    for _ in range(n):
        cx, cy = a.rng.uniform(0, s), a.rng.uniform(0, s)
        for _ in range(a.rng.randint(2, 5)):
            x, y, r = cx + a.rng.uniform(-14, 14), cy + a.rng.uniform(-14, 14), a.rng.uniform(4, 10)
            a.shape(ellipse(x, y, r, r, 20), tint(base, 0.2), outline=DETAIL * 0.8, depth=2, light_k=0.5, mottle=0)
            dot(a, x - r * 0.3, y - r * 0.3, r * 0.25, shade(base, 0.25))


def f_dripstone(a, base, n=40):
    """Little stalagmite stumps: rings with a dot in the middle."""
    s = a.w
    for _ in range(n):
        x, y, r = a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(4, 9)
        a.shape(ellipse(x, y, r, r, 16), tint(base, 0.12), outline=DETAIL * 0.8, depth=2, shade_k=0.4, light_k=0.4, mottle=0)
        a.ink(ellipse(x, y, r * 0.5, r * 0.5, 12), FINE * 0.8, closed=True, color=shade(base, 0.35), alpha=0.7, wob=0)


def f_holes(a, base, n=30):
    """Pits: a dark hole with a lighter worn rim."""
    s = a.w
    for _ in range(n):
        x, y, r = a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(3, 9)
        a.shape(ellipse(x, y, r * 1.6, r * 1.4, 16), tint(base, 0.12), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.shape(ellipse(x, y, r, r * 0.8, 14), shade(base, 0.55), outline=FINE, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)


def f_rubble(a, base, n=40):
    s = a.w
    for _ in range(n):
        x, y, r = a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(6, 14)
        pts = [(x + r * math.cos(t) * a.rng.uniform(0.7, 1.1), y + r * math.sin(t) * a.rng.uniform(0.7, 1.1)) for t in [2 * math.pi * k / 5 + a.rng.uniform(-0.2, 0.2) for k in range(5)]]
        a.shape(pts, vary(a.rng, shade(base, 0.08), 0.06), outline=DETAIL * 0.9, corner=2, depth=3, shade_k=0.45, light_k=0.35, mottle=0)


def f_ice(a, base, cols=4):
    """Big ice plates with white fracture lines."""
    s = a.w
    for (cx, cy), poly in voronoi_cells(s, s, cols, cols, a.rng, 0.4):
        if len(poly) < 3:
            continue
        a.shape(inset(poly, 2), vary(a.rng, tint(base, 0.15), 0.03), outline=FINE * 1.2, corner=4, depth=3, shade_k=0.15, light_k=0.5, mottle=0.03,
                detail=lambda art, p, cx=cx, cy=cy: art.ink([(cx - 20, cy - 10), (cx + 4, cy - 2), (cx + 26, cy - 18)], FINE * 1.1, color=(250, 252, 255), alpha=0.9))


def f_tracks(a, base, n=4):
    """Long shallow grooves (drag marks, water channels)."""
    s = a.w
    for _ in range(n):
        y = a.rng.uniform(0, s)
        ph = a.rng.uniform(0, 6.28)
        pts = [(x, y + 14 * math.sin(2 * math.pi * x / s + ph)) for x in range(-20, s + 21, 12)]
        a.ink(pts, 12, color=shade(base, 0.18), alpha=0.7, taper=False, wob=0.5)
        a.ink(pts, FINE * 1.1, color=shade(base, 0.45), alpha=0.7, taper=False, wob=0.5)


def f_scales(a, base, n=10):
    """Flaky fish-scale crust (dried mud curls)."""
    s = a.w
    h = s / n
    for r in range(n):
        x0 = (h / 2) if r % 2 else 0
        for k in range(n + 1):
            cx, cy = x0 + k * h, r * h
            arc = [(cx + h * 0.5 * math.cos(t), cy + h * 0.5 * math.sin(t)) for t in [math.pi * j / 10 for j in range(11)]]
            a.ink(arc, FINE * 1.2, color=shade(base, 0.38), alpha=0.75, wob=0.4)


FEATURES = {
    "patches": f_patches, "dots": f_dots, "pebbles": f_pebbles, "cracknet": f_cracknet, "cracks": f_cracks,
    "slabs": f_slabs, "basalt": f_basalt, "strata": f_strata, "terraces": f_terraces, "ripples": f_ripples,
    "shards": f_shards, "crystals": f_crystals, "puddles": f_puddles, "bones": f_bones, "roots": f_roots,
    "moss": f_moss, "veins": f_veins, "fungus": f_fungus, "dripstone": f_dripstone, "holes": f_holes,
    "rubble": f_rubble, "ice": f_ice, "tracks": f_tracks, "scales": f_scales,
}


def floor(seed, base, steps):
    """steps: [(feature name, kwargs), ...] drawn in order."""
    a = Art(SW, SW, seed, tile=True, bg=base)
    for name, kw in steps:
        FEATURES[name](a, base, **kw)
    return a.image()


# -- walls ----------------------------------------------------------------------------------------


def wall(seed, base, kind="rocks", h=72, extra=None):
    a = strip(seed, h)

    def rocks(size=(26, 48), jag=0.25, cols=None):
        x = 0.0
        while x < SW:
            bw = a.rng.uniform(*size)
            pts = blob(x + bw / 2, h / 2, bw / 2 + 3, a.rng, 10, jag, ry=h / 2 - 6)
            pts = [(px, min(h - 4, max(4, py))) for px, py in pts]
            col = mix(base, shade(base, 0.12), a.rng.random()) if cols is None else a.rng.choice(cols)
            a.shape(pts, col, outline=DETAIL * 1.3, corner=3, depth=4, shade_k=0.55, light_k=0.3, var=0.1)
            x += bw * 0.8

    if kind == "rocks":
        rocks()
    elif kind == "jagged":
        rocks((20, 36), 0.45)
    elif kind == "smooth":
        rocks((44, 72), 0.08)
    elif kind == "boulders":
        rocks((50, 80), 0.12)
    elif kind == "rubble":
        band(a, 10, h - 10, shade(base, 0.1), outline=DETAIL * 1.1)
        x = 0.0
        while x < SW:
            r = a.rng.uniform(7, 13)
            cy = a.rng.uniform(r + 6, h - r - 6)
            a.shape(blob(x, cy, r, a.rng, 7, 0.25), vary(a.rng, base, 0.06), outline=DETAIL, corner=2, depth=3, shade_k=0.5, light_k=0.3, mottle=0)
            x += r * 1.3
    elif kind == "strata":
        for r in range(3):
            y0 = 6 + r * (h - 12) / 3
            y1 = y0 + (h - 12) / 3
            x = a.rng.uniform(0, SW)
            for wdt in split(SW, a.rng, 40, 100):
                pts = [(x + 2, y0 + 2), (x + wdt - 2, y0 + 2 + a.rng.uniform(-1, 1)), (x + wdt - 2 + a.rng.uniform(-3, 3), y1 - 2), (x + 2 + a.rng.uniform(-3, 3), y1 - 2)]
                a.shape(pts, vary(a.rng, shade(base, 0.04 * r), 0.05), outline=DETAIL * 1.1, corner=3, wob=1.0, depth=3, shade_k=0.5, light_k=0.3, var=0.1)
                x += wdt
    elif kind == "slabs":
        x = 0.0
        while x < SW:
            bw = a.rng.uniform(70, 120)
            a.shape(rect(x + 2, 8, x + bw - 2, h - 8), vary(a.rng, base, 0.05), outline=DETAIL * 1.3, corner=6, wob=1.0, depth=4, shade_k=0.5, light_k=0.35, var=0.1)
            x += bw
    elif kind == "columns":
        x = 0.0
        while x < SW:
            r = a.rng.uniform(14, 20)
            cy = a.rng.uniform(r + 4, h - r - 4)
            pts = [(x + r * math.cos(k * math.pi / 3), cy + r * math.sin(k * math.pi / 3)) for k in range(6)]
            a.shape(pts, vary(a.rng, base, 0.06), outline=DETAIL * 1.1, corner=2, depth=3, shade_k=0.5, light_k=0.4, mottle=0)
            x += r * 1.6
    elif kind == "icicles":
        band(a, 8, h - 8, base, outline=DETAIL * 1.2)
        x = 0.0
        while x < SW:
            r = a.rng.uniform(8, 14)
            a.shape([(x - r, h / 2 - 4), (x + r, h / 2 - 4), (x, h / 2 + r * 1.4)], tint(base, 0.22), outline=DETAIL * 0.9, corner=1, depth=2, light_k=0.5, mottle=0)
            x += r * 1.8
    elif kind == "crystals":
        band(a, 10, h - 10, shade(base, 0.08), outline=DETAIL)
        x = 0.0
        while x < SW:
            r = a.rng.uniform(10, 18)
            cy = a.rng.uniform(r + 4, h - r - 4)
            pts = [(x + r * math.cos(k * math.pi / 3 + 0.3), cy + r * math.sin(k * math.pi / 3 + 0.3)) for k in range(6)]
            a.shape(pts, tint(base, 0.25), outline=DETAIL, corner=1, depth=3, light_k=0.6, mottle=0)
            x += r * 1.6
    elif kind == "layered":
        for r in range(4):
            y0 = 6 + r * (h - 12) / 4
            band(a, y0, y0 + (h - 12) / 4, vary(a.rng, shade(base, 0.05 * (r % 2)), 0.03), outline=DETAIL * (1.3 if r in (0, 3) else 0.8), shade_k=0.3)
    elif kind == "pillars":
        band(a, 14, h - 14, shade(base, 0.12), outline=DETAIL)
        x = 0.0
        while x < SW:
            r = a.rng.uniform(16, 24)
            a.shape(ellipse(x, h / 2, r, min(r, h / 2 - 5), 24), vary(a.rng, base, 0.05), outline=DETAIL * 1.2, depth=4, shade_k=0.5, light_k=0.4, mottle=0)
            a.ink(ellipse(x, h / 2, r * 0.55, min(r, h / 2 - 5) * 0.55, 18), FINE, closed=True, color=shade(base, 0.35), alpha=0.7)
            x += r * 2.3
    if extra:
        extra(a, h, base)
    return a.image()


def w_moss(a, h, base):
    x = 0.0
    while x < SW:
        x += a.rng.uniform(40, 90)
        a.shape(blob(x, a.rng.uniform(14, h - 14), a.rng.uniform(8, 14), a.rng, 9, 0.35), shade(base, 0.2), outline=DETAIL * 0.7, smooth=True, depth=2, shade_k=0.2, light_k=0.3, ao=0, mottle=0.1)


def w_drips(a, h, base):
    for _ in range(26):
        x, y, r = a.rng.uniform(0, SW), a.rng.uniform(12, h - 12), a.rng.uniform(3, 6)
        a.shape(ellipse(x, y, r, r, 12), tint(base, 0.18), outline=FINE * 1.1, depth=1, light_k=0.5, mottle=0)


def w_roots(a, h, base):
    for _ in range(5):
        x = a.rng.uniform(0, SW)
        pts = [(x + a.rng.uniform(-6, 6), y) for y in range(4, h - 3, 8)]
        a.ink(pts, 7, color=INK, taper=True, wob=0.5)
        a.ink(pts, 4, color=shade(base, 0.3), taper=True, wob=0.5)


def w_bones(a, h, base):
    for _ in range(8):
        x, y = a.rng.uniform(0, SW), a.rng.uniform(14, h - 14)
        a.ink([(x - 12, y), (x + 12, y + a.rng.uniform(-4, 4))], 9, color=INK, taper=False)
        a.ink([(x - 12, y), (x + 12, y + a.rng.uniform(-4, 4))], 5.5, color=tint(base, 0.3), taper=False)


def w_fungus(a, h, base):
    for _ in range(14):
        x, y, r = a.rng.uniform(0, SW), a.rng.uniform(12, h - 12), a.rng.uniform(4, 8)
        a.shape(ellipse(x, y, r, r, 16), tint(base, 0.22), outline=DETAIL * 0.8, depth=2, light_k=0.5, mottle=0)


def w_veins(a, h, base):
    for _ in range(4):
        x = a.rng.uniform(0, SW)
        pts = [(x + k * 14, a.rng.uniform(10, h - 10)) for k in range(6)]
        a.ink(pts, 3, color=tint(base, 0.6), taper=True, wob=0.4)


def w_cracks(a, h, base):
    for _ in range(10):
        x = a.rng.uniform(0, SW)
        a.ink([(x, 8), (x + a.rng.uniform(-6, 6), h / 2), (x + a.rng.uniform(-8, 8), h - 8)], FINE * 1.2, color=shade(base, 0.5), alpha=0.8, wob=0.4)


EXTRAS = {"moss": w_moss, "drips": w_drips, "roots": w_roots, "bones": w_bones, "fungus": w_fungus, "veins": w_veins, "cracks": w_cracks}


def cave(seed, base, steps, wall_kind="rocks", wall_base=None, wall_h=72, wall_extra=None):
    def make():
        wb = wall_base or shade(base, 0.1)
        return floor(seed, base, steps), wall(seed + 77, wb, wall_kind, wall_h, EXTRAS.get(wall_extra))

    return make


# Shorthands for recipes.
P = lambda **kw: ("patches", kw)  # noqa: E731
D = lambda **kw: ("dots", kw)  # noqa: E731


def F(name, **kw):
    return (name, kw)


C = rgb
CAVES2 = {
    "Crackled Cave": cave(2001, C("#d4d2cd"), [P(n=20), F("cracknet", cols=7), D(n=200)], "jagged", wall_extra="cracks"),
    "Shattered Cave": cave(2002, C("#cfcdc8"), [F("cracknet", cols=11, width=FINE * 1.1), F("rubble", n=20), D()], "rubble"),
    "Layered Cave": cave(2003, C("#d6d1c6"), [F("strata", n=8), D(n=150)], "strata"),
    "Banded Cave": cave(2004, C("#cfcac0"), [F("strata", n=5, amp=18), F("pebbles", n=20)], "layered"),
    "Contour Cave": cave(2005, C("#d3d1cc"), [P(n=16), F("terraces"), D(n=120)], "smooth"),
    "Pebble Bed Cave": cave(2006, C("#cfcdc6"), [F("pebbles", n=420, r=(3, 7), outline=DETAIL * 0.7)], "rubble"),
    "Cobble Cave": cave(2007, C("#cbc9c3"), [F("pebbles", n=170, r=(8, 14), outline=DETAIL)], "boulders"),
    "Shard Cave": cave(2008, C("#d1d3d6"), [P(n=20), F("shards", n=40), D()], "crystals"),
    "Geode Cave": cave(2009, C("#d0cfd4"), [F("crystals", n=40), F("cracks", n=6), D()], "crystals", wall_extra="veins"),
    "Grotto Pools": cave(2010, C("#ccced0"), [P(n=30), F("puddles", n=16), F("pebbles", n=40)], "smooth", wall_extra="drips"),
    "Dripping Cave": cave(2011, C("#d2d2cf"), [P(n=24), F("dripstone", n=60), F("puddles", n=5, r=(12, 22))], "pillars", wall_extra="drips"),
    "Ossuary Cave": cave(2012, C("#d6d2c9"), [P(n=24), F("bones", n=18), F("pebbles", n=30)], "rocks", wall_extra="bones"),
    "Boneyard Cave": cave(2013, C("#d8d4cb"), [F("bones", n=34), F("rubble", n=12), D(n=200)], "rubble", wall_extra="bones"),
    "Dune Cave": cave(2014, C("#dbd6c9"), [F("ripples", n=22), D(n=500, r=(0.4, 0.9))], "smooth"),
    "Windswept Cave": cave(2015, C("#d9d5cb"), [F("ripples", n=12, amp=9), F("pebbles", n=24)], "layered"),
    "Glacier Cave": cave(2016, C("#dde1e4"), [F("ice", cols=4), D(n=80)], "icicles", wall_base=C("#d3d9de")),
    "Frost Plate Cave": cave(2017, C("#dadfe2"), [F("ice", cols=6), F("cracks", n=8)], "slabs", wall_base=C("#cfd5da")),
    "Root Cave": cave(2018, C("#d0ccc4"), [P(n=24), F("roots", n=9), D(n=180)], "rocks", wall_extra="roots"),
    "Tangled Root Cave": cave(2019, C("#cdc8bf"), [F("roots", n=16), F("pebbles", n=20)], "jagged", wall_extra="roots"),
    "Moss Carpet Cave": cave(2020, C("#cfd0ca"), [F("moss", n=40, r=(20, 44)), D(n=150)], "rocks", wall_extra="moss"),
    "Lichen Cave": cave(2021, C("#d2d2cc"), [P(n=20), F("moss", n=26, r=(8, 16)), F("pebbles", n=40)], "boulders", wall_extra="moss"),
    "Lava Vein Cave": cave(2022, C("#a9a5a2"), [F("cracknet", cols=6), F("veins", n=8), D(n=200)], "jagged", wall_base=C("#94908d"), wall_extra="veins"),
    "Quartz Vein Cave": cave(2023, C("#cfcdca"), [P(n=18), F("veins", n=12), D(n=150)], "slabs", wall_extra="veins"),
    "Mushroom Grotto": cave(2024, C("#d0cfc9"), [P(n=20), F("fungus", n=26), F("moss", n=6)], "rocks", wall_extra="fungus"),
    "Spore Cave": cave(2025, C("#d3d2cc"), [F("fungus", n=12), F("holes", n=60), D(n=300)], "smooth", wall_extra="fungus"),
    "Stalagmite Field": cave(2026, C("#d1cfca"), [P(n=16), F("dripstone", n=110)], "pillars"),
    "Basalt Cave": cave(2027, C("#b9b7b5"), [F("basalt", n=6)], "columns", wall_base=C("#a8a6a4")),
    "Columnar Cave": cave(2028, C("#c4c2bf"), [F("basalt", n=9), F("cracks", n=6)], "columns"),
    "Slab Cave": cave(2029, C("#d3d0c8"), [F("slabs", cols=4), D(n=120)], "slabs"),
    "Flagged Cave": cave(2030, C("#cfccc4"), [F("slabs", cols=7, corner=6, gap=3), F("moss", n=6)], "slabs", wall_extra="moss"),
    "Honeycomb Cave": cave(2031, C("#d1cec7"), [P(n=20), F("holes", n=160), D(n=100)], "rubble"),
    "Pitted Cave": cave(2032, C("#cdcbc5"), [F("holes", n=70), F("cracks", n=10), D()], "jagged"),
    "Rubble Cave": cave(2033, C("#cecbc5"), [P(n=16), F("rubble", n=60), D()], "rubble"),
    "Collapsed Cave": cave(2034, C("#cbc8c1"), [F("cracknet", cols=5), F("rubble", n=90)], "boulders", wall_extra="cracks"),
    "Channel Cave": cave(2035, C("#d0d1cf"), [P(n=24), F("tracks", n=5), F("pebbles", n=30)], "smooth", wall_extra="drips"),
    "Worn Cave": cave(2036, C("#d4d1ca"), [F("tracks", n=3), F("terraces", n=5), D()], "layered"),
    "Mudcrack Cave": cave(2037, C("#cbc5ba"), [F("cracknet", cols=9, width=FINE * 1.6, jitter=0.45), D(n=200)], "smooth", wall_base=C("#b8b0a4")),
    "Flaky Cave": cave(2038, C("#cdc8be"), [F("scales", n=12), D(n=200)], "strata"),
    "Crusted Cave": cave(2039, C("#c9c6c0"), [F("scales", n=8), F("cracks", n=10), F("pebbles", n=20)], "jagged"),
    "Wet Crystal Cave": cave(2040, C("#cdd0d4"), [F("puddles", n=10), F("crystals", n=18), D()], "crystals", wall_extra="drips"),
    "Frozen Pools": cave(2041, C("#dce1e5"), [F("ice", cols=3), F("puddles", n=6)], "icicles", wall_base=C("#d1d8de")),
    "Silt Cave": cave(2042, C("#d2cfc6"), [P(n=60, size=(14, 34)), F("ripples", n=8, amp=3), D(n=600, r=(0.4, 0.8))], "smooth"),
    "Ash Cave": cave(2043, C("#bdbab6"), [P(n=40), F("rubble", n=14), D(n=900, r=(0.4, 1.0), alpha=0.5)], "rubble", wall_base=C("#a9a6a2")),
    "Obsidian Cave": cave(2044, C("#a7a6a8"), [F("shards", n=50, L=(22, 36)), F("cracks", n=10)], "jagged", wall_base=C("#929194")),
    "Terraced Cave": cave(2045, C("#d5d2ca"), [F("terraces", n=9), F("pebbles", n=20)], "strata"),
    "Rootbound Pools": cave(2046, C("#ccccc6"), [F("puddles", n=8), F("roots", n=10), F("moss", n=8)], "rocks", wall_extra="roots"),
    "Crystal Rubble Cave": cave(2047, C("#cfd0d3"), [F("rubble", n=40), F("shards", n=20)], "crystals"),
    "Bone Pit Cave": cave(2048, C("#cfcbc2"), [F("holes", n=30), F("bones", n=22), F("cracks", n=8)], "jagged", wall_extra="bones"),
    "Sand And Stone Cave": cave(2049, C("#d8d3c6"), [F("ripples", n=14), F("pebbles", n=60, r=(5, 11))], "boulders"),
    "Gravel Wash Cave": cave(2050, C("#cfccc5"), [F("tracks", n=4), F("pebbles", n=220, r=(2, 5), outline=DETAIL * 0.6)], "rubble"),
    "Moss And Pebble Cave": cave(2051, C("#cfcfc9"), [F("moss", n=18), F("pebbles", n=140, r=(3, 7))], "rocks", wall_extra="moss"),
    "Fungal Root Cave": cave(2052, C("#cecbc3"), [F("roots", n=8), F("fungus", n=18)], "rocks", wall_extra="fungus"),
    "Dripping Crystal Cave": cave(2053, C("#d0d2d5"), [F("dripstone", n=50), F("crystals", n=16)], "pillars", wall_extra="veins"),
    "Ancient Floor Cave": cave(2054, C("#d4d0c6"), [F("slabs", cols=6, corner=4, gap=3), F("cracks", n=16), F("moss", n=5)], "slabs", wall_extra="cracks"),
    "Smooth Bedrock Cave": cave(2055, C("#d1cfca"), [P(n=12, size=(40, 80)), F("cracks", n=4), D(n=60)], "smooth"),
    "Sunken Cave": cave(2056, C("#cbcdcd"), [F("terraces", n=6), F("puddles", n=8)], "layered", wall_extra="drips"),
    "Splintered Cave": cave(2057, C("#d0cec9"), [F("cracknet", cols=9, width=FINE * 1.1, jitter=0.32), F("shards", n=14)], "jagged"),
    "Dusty Pebble Cave": cave(2058, C("#d6d2c8"), [D(n=1400, r=(0.4, 1.0), alpha=0.4), F("pebbles", n=60, r=(2, 6), outline=DETAIL * 0.6)], "rocks"),
    "Lava Crust Cave": cave(2059, C("#a19e9b"), [F("slabs", cols=5, corner=8, gap=6), F("veins", n=4)], "boulders", wall_base=C("#8e8a87"), wall_extra="veins"),
    "Icy Bone Cave": cave(2060, C("#dbe0e3"), [F("ice", cols=5), F("bones", n=10)], "icicles", wall_base=C("#d0d7dc"), wall_extra="bones"),
}


# -- lights ----------------------------------------------------------------------------------------


def _rot(dx, dy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return dx * c + dy * s, -dx * s + dy * c


def l_torch():
    dx, dy, d, t = _grid()
    n = _noise(60, 11)
    shape = np.clip(1 - d * (0.8 + 0.45 * n), 0, 1) ** 1.8
    return _light(shape * _edge(d))


def l_candle():
    dx, dy, d, t = _grid()
    return _light(np.clip(1 - d / 0.45, 0, 1) ** 1.6 + np.clip(1 - d, 0, 1) ** 6 * 0.15)


def l_fire():
    dx, dy, d, t = _grid()
    n = _noise(40, 12, 4)
    lobes = 0.85 + 0.25 * np.cos(t * 5 + n * 4)
    return _light(np.clip(1 - d * lobes * (0.9 + 0.3 * n), 0, 1) ** 1.5 * _edge(d))


def l_runes():
    dx, dy, d, t = _grid()
    ring = np.exp(-((d - 0.62) / 0.03) ** 2) + np.exp(-((d - 0.78) / 0.025) ** 2)
    marks = (np.abs(d - 0.7) < 0.05) * (np.cos(t * 16) > 0.55)
    star = np.zeros_like(d)
    for k in range(5):
        a0 = -math.pi / 2 + k * 4 * math.pi / 5
        a1 = -math.pi / 2 + (k + 1) * 4 * math.pi / 5
        x0, y0, x1, y1 = 0.62 * math.cos(a0), 0.62 * math.sin(a0), 0.62 * math.cos(a1), 0.62 * math.sin(a1)
        vx, vy = x1 - x0, y1 - y0
        L2 = vx * vx + vy * vy
        u = np.clip(((dx - x0) * vx + (dy - y0) * vy) / L2, 0, 1)
        dist = np.hypot(dx - (x0 + u * vx), dy - (y0 + u * vy))
        star = np.maximum(star, np.exp(-(dist / 0.018) ** 2))
    glow = np.clip(1 - d, 0, 1) ** 2 * 0.3
    return _light(np.clip(ring * 0.9 + marks * 0.8 + star * 0.85 + glow, 0, 1) * _edge(d))


def _window(cols, rows, w=0.6, h=0.6, bar=0.025, soft=0.06, skew=0.0):
    dx, dy, d, t = _grid()
    x = dx + skew * dy
    inside = np.clip((w - np.abs(x)) / soft, 0, 1) * np.clip((h - np.abs(dy)) / soft, 0, 1)
    bars = np.ones_like(d)
    for k in range(1, cols):
        xx = -w + 2 * w * k / cols
        bars *= 1 - 0.9 * np.clip(1 - np.abs(x - xx) / bar, 0, 1)
    for k in range(1, rows):
        yy = -h + 2 * h * k / rows
        bars *= 1 - 0.9 * np.clip(1 - np.abs(dy - yy) / bar, 0, 1)
    return _light(inside * bars * 0.95)


def l_stained():
    """An arched window of glass pieces (Voronoi cells) in lead cames: the
    cells vary in brightness, the leads are dark lines."""
    dx, dy, d, t = _grid()
    arch = (np.abs(dx) < 0.42) & ((dy > -0.2) | (np.hypot(dx, dy + 0.2) < 0.42)) & (dy < 0.7)
    rs = np.random.RandomState(23)
    pts = rs.uniform(-0.6, 0.75, (34, 2))
    d1 = np.full_like(d, 9.0)
    d2 = np.full_like(d, 9.0)
    idx = np.zeros(d.shape, np.int32)
    for i, (px, py) in enumerate(pts):
        dd = np.hypot(dx - px, dy - py)
        closer = dd < d1
        d2 = np.where(closer, d1, np.minimum(d2, dd))
        idx = np.where(closer, i, idx)
        d1 = np.where(closer, dd, d1)
    lead = np.clip(1 - (d2 - d1) / 0.025, 0, 1)
    frame = np.clip(1 - np.abs(np.abs(dx) - 0.42) / 0.02, 0, 1) * (dy > -0.2)
    shade_ = 0.55 + 0.45 * ((idx * 7) % 5) / 4
    alpha = arch * shade_ * (1 - 0.92 * np.maximum(lead, frame))
    return _light(np.clip(alpha, 0, 1) * 0.95)

def l_dapple(scale, seed, thr):
    def make():
        dx, dy, d, t = _grid()
        n = _noise(scale, seed, 3)
        spots = np.clip((n - thr) / 0.08, 0, 1)
        return _light(spots * np.clip(1 - d, 0, 1) ** 0.7 * _edge(d))

    return make


def l_clouds():
    dx, dy, d, t = _grid()
    n = _noise(120, 31, 4)
    return _light((0.35 + 0.65 * np.clip((n - 0.3) / 0.5, 0, 1)) * np.clip(1 - d, 0, 1) ** 0.6 * _edge(d))


def l_aurora():
    dx, dy, d, t = _grid()
    bands = np.zeros_like(d)
    for k, off in enumerate((-0.3, 0.0, 0.32)):
        y = off + 0.12 * np.sin(dx * 4 + k)
        bands += np.exp(-((dy - y) / 0.06) ** 2) * (0.6 + 0.4 * np.cos(dx * 9 + k * 2))
    return _light(np.clip(bands, 0, 1) * np.clip(1 - np.abs(dx), 0, 1) ** 0.5 * _edge(d))


def l_shafts(ang):
    def make():
        dx, dy, d, t = _grid()
        u, v = _rot(dx, dy, ang)
        stripes = np.clip(np.cos(v * 22) * 0.5 + 0.5, 0, 1) ** 3
        fade = np.clip(1 - np.abs(u) / 0.9, 0, 1)
        return _light(stripes * fade * np.clip(1 - np.abs(v) / 0.75, 0, 1) * _edge(d))

    return make


def l_cage():
    dx, dy, d, t = _grid()
    base = np.clip(1 - d, 0, 1) ** 1.2
    ribs = 1 - 0.85 * np.clip(1 - np.abs(np.sin(t * 4)) * d / 0.035, 0, 1)
    rings = 1 - 0.85 * (np.abs(d - 0.45) < 0.02)
    return _light(base * ribs * rings * _edge(d))


def l_bars():
    dx, dy, d, t = _grid()
    inside = np.clip((0.7 - np.abs(dx)) / 0.08, 0, 1) * np.clip((0.55 - np.abs(dy)) / 0.08, 0, 1)
    bars = 1 - 0.95 * (np.cos(dx * math.pi * 6) > 0.86)
    return _light(inside * bars * 0.9)


def l_blinds():
    dx, dy, d, t = _grid()
    inside = np.clip((0.6 - np.abs(dx)) / 0.06, 0, 1) * np.clip((0.6 - np.abs(dy)) / 0.06, 0, 1)
    slats = np.clip(np.sin(dy * 40) * 2, 0, 1)
    return _light(inside * slats * 0.9)


def l_starfield():
    rs = np.random.RandomState(41)
    dx, dy, d, t = _grid()
    out = np.clip(1 - d, 0, 1) ** 3 * 0.15
    for _ in range(140):
        x, y = rs.uniform(-0.9, 0.9), rs.uniform(-0.9, 0.9)
        r = rs.uniform(0.006, 0.02)
        out = np.maximum(out, np.exp(-((dx - x) ** 2 + (dy - y) ** 2) / (r * r)))
    return _light(out * _edge(d))


def l_spot(ang, width):
    def make():
        dx, dy, d, t = _grid()
        u, v = _rot(dx + 0.85 * math.cos(ang), dy + 0.85 * math.sin(ang), ang)
        cone = np.clip(1 - np.abs(np.arctan2(v, np.maximum(u, 1e-3))) / width, 0, 1) * (u > 0)
        fall = np.clip(1 - u / 1.7, 0, 1)
        return _light(cone ** 0.8 * fall * _edge(d))

    return make


def l_soft_square(size):
    def make():
        dx, dy, d, t = _grid()
        m = np.maximum(np.abs(dx), np.abs(dy))
        return _light(np.clip((size - m) / (size * 0.6), 0, 1) ** 1.3)

    return make


def l_hexagon():
    dx, dy, d, t = _grid()
    h = np.maximum(np.abs(dx) * 0.866 + np.abs(dy) * 0.5, np.abs(dy))
    return _light(np.clip((0.8 - h) / 0.35, 0, 1) ** 1.2)


def l_crescent():
    dx, dy, d, t = _grid()
    a = np.clip((0.7 - d) / 0.1, 0, 1)
    b = np.clip((0.62 - np.hypot(dx - 0.3, dy + 0.15)) / 0.1, 0, 1)
    return _light(np.clip(a - b, 0, 1) * 0.95)


def l_eye():
    dx, dy, d, t = _grid()
    lens = np.clip((0.75 - np.hypot(dx * 0.75, dy * 1.9)) / 0.15, 0, 1)
    pupil = np.exp(-(d / 0.18) ** 2)
    return _light(np.clip(lens * 0.7 + pupil * 0.4, 0, 1))


def l_rings(radii, w):
    def make():
        dx, dy, d, t = _grid()
        out = np.zeros_like(d)
        for r in radii:
            out = np.maximum(out, np.exp(-((d - r) / w) ** 2))
        return _light(out * _edge(d))

    return make


def l_mist(scale, seed, power):
    def make():
        dx, dy, d, t = _grid()
        n = _noise(scale, seed, 4)
        return _light(np.clip(n * 1.3 - 0.15, 0, 1) * np.clip(1 - d, 0, 1) ** power * _edge(d))

    return make


def l_halo_soft():
    dx, dy, d, t = _grid()
    return _light(np.exp(-((d - 0.45) / 0.25) ** 2) * _edge(d))


def l_flame_tall():
    dx, dy, d, t = _grid()
    n = _noise(50, 51)
    q = np.hypot(dx * 1.4, (dy + 0.1) * 0.8)
    return _light(np.clip(1 - q * (0.85 + 0.35 * n), 0, 1) ** 1.6 * _edge(d))


def l_moon():
    dx, dy, d, t = _grid()
    disc = np.clip((0.35 - d) / 0.05, 0, 1)
    halo = np.clip(1 - d, 0, 1) ** 3 * 0.45
    return _light(np.clip(disc + halo, 0, 1))


LIGHTS2 = {
    "Torch Flicker": l_torch,
    "Candle Glow": l_candle,
    "Campfire Glow": l_fire,
    "Tall Flame": l_flame_tall,
    "Rune Circle": l_runes,
    "Four Pane Window": lambda: _window(2, 2),
    "Six Pane Window": lambda: _window(3, 2, w=0.7, h=0.5),
    "Nine Pane Window": lambda: _window(3, 3),
    "Lattice Window": lambda: _window(6, 6, bar=0.015),
    "Tall Window": lambda: _window(2, 4, w=0.35, h=0.75),
    "Slanted Window": lambda: _window(2, 2, skew=0.5),
    "Stained Glass": l_stained,
    "Leafy Dapple": l_dapple(40, 61, 0.55),
    "Sparse Dapple": l_dapple(70, 62, 0.62),
    "Fine Dapple": l_dapple(22, 63, 0.58),
    "Cloud Shadows": l_clouds,
    "Aurora": l_aurora,
    "Sun Shafts": l_shafts(0.0),
    "Slanted Sun Shafts": l_shafts(0.6),
    "Steep Sun Shafts": l_shafts(1.2),
    "Lantern Cage": l_cage,
    "Prison Bars": l_bars,
    "Window Blinds": l_blinds,
    "Starfield": l_starfield,
    "Narrow Spot": l_spot(0.0, 0.25),
    "Wide Spot": l_spot(0.0, 0.6),
    "Spot Down": l_spot(math.pi / 2, 0.4),
    "Spot Up Left": l_spot(-2.4, 0.4),
    "Soft Square": l_soft_square(0.7),
    "Small Soft Square": l_soft_square(0.4),
    "Hexagon Light": l_hexagon,
    "Crescent Light": l_crescent,
    "Eye Light": l_eye,
    "Thin Rings": l_rings((0.3, 0.5, 0.7), 0.025),
    "Wide Ring": l_rings((0.55,), 0.12),
    "Triple Halo": l_rings((0.2, 0.45, 0.75), 0.06),
    "Soft Halo": l_halo_soft,
    "Swirling Mist": l_mist(90, 71, 0.8),
    "Thick Fog": l_mist(150, 72, 0.4),
    "Moonlight": l_moon,
}
