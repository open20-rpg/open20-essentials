"""Ground textures for the built-in pack: 20 floors (seamless tilesets), 20
recolorable patterns, 20 terrains (alpha = height), 20 paths (strips periodic
along x) and 20 light shapes. Same hand-inked look as floors.py."""

import math

import numpy as np
import skia
from PIL import Image

from floors import P_GROUT, P_RED, crack, inset, speckles, split, voronoi_cells
from pen import DETAIL, FINE, INK, JOINT, JOINT_ALPHA, Art, grout, joint_color, blob, chaikin, ellipse, mix, periodic_noise, rect, rgb, shade, tint, to_path, vary

T = 256
S2 = 2 * T


def jkw(c, k=1.0):
    """Shape kwargs for a piece of masonry/planking: thin joint in the
    piece's own darker tone instead of a heavy ink outline."""
    return dict(outline=JOINT * k, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA)


def dot(a, x, y, r, color, alpha=1.0):
    p = skia.Path()
    p.addCircle(x, y, r)
    a.fill_path(p, color, alpha)


# ===================================================================================================
# FLOORS (512x512 seamless)
# ===================================================================================================


def planks(seed=1, tones=("#b07d4f", "#a5724a", "#ba8a5a", "#9c6a42"), gap="#3b271b", rows=8, nails=True):
    s = S2
    tones = [rgb(t) for t in tones]
    # `gap` used to be the dark trench colour; now only nudges the grout.
    a = Art(s, s, seed, tile=True, bg=mix(grout(tones[0]), rgb(gap), 0.15))
    h = s / rows
    for r in range(rows):
        y = r * h
        x = a.rng.uniform(0, s)
        for ln in split(s, a.rng, s * 0.3, s * 0.65):
            c = vary(a.rng, a.rng.choice(tones), 0.04)

            def grain(art, path, x=x, y=y, ln=ln, c=c):
                for k in range(max(1, int(h / 22))):
                    gy = y + h * (0.2 + 0.6 * (k + 0.5) / max(1, int(h / 22))) + art.rng.uniform(-3, 3)
                    gx0 = x + art.rng.uniform(-10, ln * 0.3)
                    gx1 = gx0 + ln * art.rng.uniform(0.5, 0.9)
                    pts = [(gx, gy + 2.2 * math.sin((gx - gx0) / art.rng.uniform(40, 70))) for gx in np.linspace(gx0, gx1, 12)]
                    art.ink(pts, FINE * 0.85, color=shade(c, 0.45), alpha=0.7, wob=0.5)
                if art.rng.random() < 0.3:
                    kx, ky = x + art.rng.uniform(ln * 0.25, ln * 0.75), y + h * art.rng.uniform(0.35, 0.65)
                    art.ink(ellipse(kx, ky, 7, min(3.5, h * 0.12), 24), FINE, closed=True, color=shade(c, 0.5), alpha=0.8, wob=0.2)

            a.shape(rect(x + 0.8, y + 0.8, x + ln - 0.8, y + h - 0.8), c, **jkw(c), corner=1.5, wob=0.4, depth=3, shade_k=0.35, light_k=0.25, ao=0.12, mottle=0.05, detail=grain)
            if nails:
                for nx in (x + 9, x + ln - 9):
                    for ny in (y + h * 0.3, y + h * 0.7):
                        dot(a, nx, ny, 2.0, shade(c, 0.6), 0.7)
            x += ln
    return a.image()


def herringbone_bricks(size, u):
    """Rects of a herringbone tiling with 2u x u bricks, periodic over `size`
    (size/u must be a multiple of 4): horizontal bricks on the lattice
    (1,1)u, (-2,2)u, each with a vertical brick at +(0,1)u."""
    n = int(size / u)
    out = []
    seen = set()
    for i in range(-2 * n, 2 * n):
        for j in range(-n, n):
            x, y = (i - 2 * j) * u, (i + 2 * j) * u
            for bx, by, w, h in ((x, y, 2 * u, u), (x, y + u, u, 2 * u)):
                if bx + w < 0 or bx > size or by + h < 0 or by > size:
                    continue
                key = (round(bx % size), round(by % size), w)
                if key in seen:
                    continue
                seen.add(key)
                out.append((bx, by, w, h))
    return out


def herringbone(seed=6, tones=("#b98a5a", "#a87a4c", "#c49866"), gap="#3b271b"):
    s = S2
    tones = [rgb(t) for t in tones]
    a = Art(s, s, seed, tile=True, bg=mix(grout(tones[0]), rgb(gap), 0.15))
    for x, y, w, h in herringbone_bricks(s, 64):
        c = vary(a.rng, a.rng.choice(tones), 0.04)
        mid = [(x + 8, y + h / 2), (x + w - 8, y + h / 2)] if w > h else [(x + w / 2, y + 8), (x + w / 2, y + h - 8)]
        a.shape(rect(x + 0.8, y + 0.8, x + w - 0.8, y + h - 0.8), c, **jkw(c), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.04, detail=lambda art, p, mid=mid, c=c: art.ink(mid, FINE * 0.8, color=shade(c, 0.45), alpha=0.6, wob=0.4))
    return a.image()

def parquet(seed=7, tones=("#b98a5a", "#a87a4c", "#c79c6a"), gap="#3b271b"):
    s = S2
    tones = [rgb(t) for t in tones]
    a = Art(s, s, seed, tile=True, bg=mix(grout(tones[0]), rgb(gap), 0.15))
    cell = s / 4
    for bi in range(4):
        for bj in range(4):
            x0, y0 = bi * cell, bj * cell
            horizontal = (bi + bj) % 2 == 0
            n = 4
            for k in range(n):
                if horizontal:
                    x, y, w, h = x0, y0 + k * cell / n, cell, cell / n
                else:
                    x, y, w, h = x0 + k * cell / n, y0, cell / n, cell
                c = vary(a.rng, a.rng.choice(tones), 0.04)
                a.shape(rect(x + 0.8, y + 0.8, x + w - 0.8, y + h - 0.8), c, **jkw(c), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.04)
    return a.image()


def flag_floor(seed=2, base="#a9a296", alt=("#b8ae9c", "#968f86"), mortar="#6f685f", n=5, cracks=0.45):
    s = S2
    base = rgb(base)
    a = Art(s, s, seed, tile=True, bg=grout(base, rgb(mortar)))
    for (cx, cy), poly in voronoi_cells(s, s, n, n, a.rng, 0.3):
        p = inset(poly, 2.0)
        c = vary(a.rng, mix(base, rgb(alt[0]) if a.rng.random() < 0.5 else rgb(alt[1]), a.rng.uniform(0.2, 0.7)), 0.03)

        def detail(art, path, cx=cx, cy=cy, c=c):
            speckles(art, path, shade(c, 0.4), 18)
            if art.rng.random() < cracks:
                crack(art, cx + art.rng.uniform(-20, 20), cy + art.rng.uniform(-20, 20), art.rng.uniform(0, 6.28), art.rng.uniform(30, 55))

        a.shape(p, c, **jkw(c, 1.2), corner=8, wob=0.8, depth=5, shade_k=0.45, light_k=0.3, ao=0.18, detail=detail)
    return a.image()


def ashlar(seed=4, base=("#8a857d", "#7a756e"), mortar="#4c4842", rows=6):
    s = S2
    a = Art(s, s, seed, tile=True, bg=grout(mix(rgb(base[0]), rgb(base[1]), 0.5), rgb(mortar)))
    h = s / rows
    for r in range(rows):
        x = a.rng.uniform(0, s)
        for w in split(s, a.rng, h * 1.1, h * 1.9):
            c = vary(a.rng, mix(rgb(base[0]), rgb(base[1]), a.rng.random()), 0.03)

            def detail(art, path, x=x, w=w, r=r, c=c):
                speckles(art, path, shade(c, 0.45), 14)
                if art.rng.random() < 0.3:
                    crack(art, x + w * art.rng.uniform(0.2, 0.8), r * h + h * 0.5, art.rng.uniform(0, 6.28), 30)

            a.shape(rect(x + 1.5, r * h + 1.5, x + w - 1.5, r * h + h - 1.5), c, **jkw(c, 1.2), corner=5, wob=0.9, depth=5, shade_k=0.45, light_k=0.3, ao=0.18, detail=detail)
            x += w
    return a.image()


def cobbles(seed=12, base=("#9a948a", "#857f77", "#a8a296"), mortar="#5e5850", n=9):
    s = S2
    a = Art(s, s, seed, tile=True, bg=grout(rgb(base[0]), rgb(mortar)))
    for (cx, cy), poly in voronoi_cells(s, s, n, n, a.rng, 0.35):
        p = chaikin(inset(poly, 2.2), True, 2)
        c = vary(a.rng, rgb(a.rng.choice(base)), 0.05)
        a.shape(p, c, **jkw(c, 1.2), corner=0, wob=0.5, depth=5, shade_k=0.45, light_k=0.35, ao=0.18, detail=lambda art, path, c=c: speckles(art, path, shade(c, 0.45), 6))
    return a.image()


def tiles(seed=13, color="#bf6b45", grout="#dccdb0", n=8, alt=None):
    s = S2
    a = Art(s, s, seed, tile=True, bg=mix(rgb(grout), rgb(color), 0.25))
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            col = rgb(alt) if alt and (i + j) % 2 else rgb(color)
            c = vary(a.rng, col, 0.04)
            a.shape(rect(x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2), c, **jkw(c), corner=3, wob=0.4, depth=4, shade_k=0.4, light_k=0.3, ao=0.15)
    return a.image()


def marble_floor(seed=15):
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb("#2c2a2f"))
    n = 4
    cell = s / n
    for i in range(n):
        for j in range(n):
            light_tile = (i + j) % 2 == 0
            c = rgb("#e6e0d4") if light_tile else rgb("#47454d")
            x0, y0 = i * cell, j * cell

            def veins(art, path, x0=x0, y0=y0, c=c, light_tile=light_tile):
                vc = shade(c, 0.35) if light_tile else tint(c, 0.35)
                for _ in range(2):
                    x, y = x0 + art.rng.uniform(0, cell), y0
                    pts = [(x, y)]
                    for _ in range(6):
                        x += art.rng.uniform(-16, 16)
                        y += cell / 6
                        pts.append((x, y))
                    art.ink(chaikin(pts, False, 2), FINE * 0.8, color=vc, alpha=0.7, wob=0.4)

            a.shape(rect(x0 + 2.5, y0 + 2.5, x0 + cell - 2.5, y0 + cell - 2.5), c, outline=2.6, corner=3, wob=0.4, depth=5, shade_k=0.4, light_k=0.35, ao=0.2, detail=veins)
    return a.image()


def carpet_floor(seed=16, base="#7e2a2a", mid="#9a3836", gold="#d6ad55", dark="#5e1f22"):
    s = S2
    base = rgb(base)
    a = Art(s, s, seed, tile=True, bg=base)
    step = s / 2
    for cx in (0, step, s):
        for cy in (0, step, s):
            for ox, oy in ((0, 0), (step / 2, step / 2)):
                x, y = cx + ox, cy + oy
                for r, col in ((step * 0.36, rgb(mid)), (step * 0.24, rgb(gold)), (step * 0.14, rgb(dark))):
                    a.shape([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], col, outline=2.4, corner=2, wob=0.4, depth=3, shade_k=0.3, light_k=0.2, ao=0.1, mottle=0.03)
    for k in range(0, s, 6):
        a.ink([(k, 0), (k, s)], 0.8, color=shade(base, 0.5), alpha=0.18, taper=False, wob=0.1)
    return a.image()


def dirt_floor(seed=17):
    s = S2
    base = rgb("#8f7356")
    a = Art(s, s, seed, tile=True, bg=base)
    for _ in range(40):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        col = rgb("#86694c") if a.rng.random() < 0.5 else rgb("#9b8061")
        a.fill_path(to_path(blob(x, y, a.rng.uniform(20, 50), a.rng, 12, 0.3)), col, 0.22, blur=6)
    for _ in range(60):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(3, 6), a.rng, 8, 0.25), vary(a.rng, rgb("#9d9183"), 0.06), outline=1.4, corner=0, wob=0.2, depth=1.5, shade_k=0.4, light_k=0.4, ao=0, mottle=0)
    for _ in range(500):
        dot(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0.6, 1.4), shade(base, 0.45), 0.5)
    for _ in range(8):
        crack(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0, 6.28), a.rng.uniform(30, 60), FINE * 0.9, 0.5)
    return a.image()


def straw_floor(seed=18):
    s = S2
    base = rgb("#c9ae6c")
    a = Art(s, s, seed, tile=True, bg=base)
    for _ in range(30):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.fill_path(to_path(blob(x, y, a.rng.uniform(30, 60), a.rng, 12, 0.3)), rgb("#b89c5c") if a.rng.random() < 0.5 else rgb("#d8bf80"), 0.22, blur=6)
    for _ in range(1300):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        L = a.rng.uniform(10, 22)
        col = mix(rgb("#7a5f2a"), rgb("#f2e0a0"), a.rng.random())
        a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], FINE * 1.4, color=col, alpha=0.95, wob=0.15, var=0.1)
    return a.image()


def rough_stone(seed=19):
    s = S2
    a = Art(s, s, seed, tile=True, bg=grout(rgb("#67625b")))
    for (cx, cy), poly in voronoi_cells(s, s, 4, 4, a.rng, 0.4):
        p = inset(poly, 2)
        c = vary(a.rng, mix(rgb("#6f6a62"), rgb("#5f5a54"), a.rng.random()), 0.04)

        def detail(art, path, cx=cx, cy=cy, c=c):
            speckles(art, path, shade(c, 0.5), 30)
            for _ in range(2):
                crack(art, cx + art.rng.uniform(-40, 40), cy + art.rng.uniform(-40, 40), art.rng.uniform(0, 6.28), art.rng.uniform(40, 80))

        a.shape(p, c, **jkw(c, 1.3), corner=18, wob=1.6, depth=8, shade_k=0.5, light_k=0.3, ao=0.25, mottle=0.08, detail=detail)
    return a.image()


def mosaic_floor(seed=20):
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb("#d8cdb6"))
    cols = [rgb(c) for c in ("#5f7fa0", "#a8483a", "#d6ad55", "#6f9a5a", "#e4dccb", "#3c4a5a")]
    n = 16
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            # A diamond medallion repeating every 8 cells.
            u, v = (i % 8) - 3.5, (j % 8) - 3.5
            d = abs(u) + abs(v)
            col = cols[int(d) % len(cols)] if d < 4.5 else cols[4]
            c = vary(a.rng, col, 0.05)
            a.shape(rect(x0 + 2.4, y0 + 2.4, x0 + cell - 2.4, y0 + cell - 2.4), c, outline=1.8, corner=2, wob=0.4, depth=2, shade_k=0.4, light_k=0.3, ao=0.1, mottle=0)
    return a.image()


def brick_floor(seed=21, col=("#a8503b", "#94432f", "#b5604a"), mortar="#c9b9a2"):
    s = S2
    a = Art(s, s, seed, tile=True, bg=grout(rgb(col[0]), rgb(mortar)))
    rows = 16
    h = s / rows
    bw = h * 2
    for r in range(rows):
        off = 0 if r % 2 == 0 else bw / 2
        x = -off
        while x < s:
            c = vary(a.rng, rgb(a.rng.choice(col)), 0.04)
            a.shape(rect(x + 1, r * h + 1, x + bw - 1, r * h + h - 1), c, **jkw(c), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.03)
            x += bw
    return a.image()


FLOORS = {
    "Oak Planks": lambda: planks(101),
    "Dark Planks": lambda: planks(102, ("#6e4a32", "#5f3f2a", "#7a5438", "#664530"), gap="#22160f"),
    "Pale Planks": lambda: planks(103, ("#d6b88a", "#cbad80", "#e0c296", "#c4a274"), gap="#5a4532"),
    "Narrow Planks": lambda: planks(104, ("#a8784e", "#b8875a", "#9a6c44"), rows=14, nails=False),
    "Herringbone Wood": lambda: herringbone(105),
    "Parquet": lambda: parquet(106),
    "Grey Flagstones": lambda: flag_floor(107),
    "Sandstone Flagstones": lambda: flag_floor(108, "#cdb68e", ("#d9c49c", "#bfa67e"), "#8a7558"),
    "Slate Flagstones": lambda: flag_floor(109, "#5f6670", ("#6b737d", "#535a63"), "#33373d", n=6),
    "Dungeon Stone": lambda: ashlar(110),
    "Sandstone Blocks": lambda: ashlar(111, ("#c8b088", "#b89e78"), "#7a6648", rows=5),
    "Cobblestone": lambda: cobbles(112),
    "Terracotta Tiles": lambda: tiles(113),
    "Checker Tiles": lambda: tiles(114, "#e6dfd0", "#8a8378", 8, alt="#3e3c44"),
    "Marble": marble_floor,
    "Red Carpet": lambda: carpet_floor(116),
    "Blue Carpet": lambda: carpet_floor(117, "#2f4466", "#3c5480", "#d6ad55", "#1f2e48"),
    "Dirt Floor": dirt_floor,
    "Straw Floor": straw_floor,
    "Rough Stone": rough_stone,
    "Mosaic": mosaic_floor,
    "Brick Floor": brick_floor,
}


# ===================================================================================================
# PATTERNS (256x256 seamless, recolorable red on neutral grout)
# ===================================================================================================


def pshape(a, pts, out=2.6, corner=3, joint=False):
    """A recolorable piece. `joint` = masonry/tile piece: thin joint in a
    darker red (g == b, so it recolors with the piece) instead of ink."""
    c = vary(a.rng, P_RED, 0.05)
    if joint:
        a.shape(pts, c, outline=JOINT, outline_color=shade(P_RED, 0.5), outline_alpha=JOINT_ALPHA, corner=corner, wob=0.3, depth=3, shade_k=0.35, light_k=0.0, ao=0.12, mottle=0.0)
    else:
        a.shape(pts, c, outline=out, corner=corner, wob=0.4, depth=4, shade_k=0.45, light_k=0.0, ao=0.2, mottle=0.0)


def pat(seed):
    return Art(T, T, seed, tile=True, bg=P_GROUT)


def p_tiles(seed=201, n=4, gap=3.5):
    a = pat(seed)
    cell = T / n
    gap = min(gap, 2.0)
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            pshape(a, rect(x0 + gap, y0 + gap, x0 + cell - gap, y0 + cell - gap), corner=3, joint=True)
    return a.image(grain=0.02)


def p_offset_tiles(seed=202):
    a = pat(seed)
    n = 4
    cell = T / n
    for j in range(n):
        off = cell / 2 if j % 2 else 0
        for i in range(-1, n + 1):
            x0, y0 = i * cell + off, j * cell
            pshape(a, rect(x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2), corner=3, joint=True)
    return a.image(grain=0.02)


def p_hex(seed=203):
    a = pat(seed)
    cols = 4
    w = T / cols
    rows = 4
    rh = T / rows
    for j in range(rows + 1):
        for i in range(-1, cols + 1):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * rh
            rr = w / math.sqrt(3) - 1.5
            pts = [(cx + rr * math.sin(k * math.pi / 3 + math.pi / 6), cy + rr * math.cos(k * math.pi / 3 + math.pi / 6)) for k in range(6)]
            pshape(a, pts, corner=2, joint=True)
    return a.image(grain=0.02)


def p_basketweave(seed=204):
    a = pat(seed)
    u = T / 8
    for bi in range(4):
        for bj in range(4):
            x0, y0 = bi * 2 * u, bj * 2 * u
            horizontal = (bi + bj) % 2 == 0
            for k in range(2):
                if horizontal:
                    x, y, w, h = x0, y0 + k * u, 2 * u, u
                else:
                    x, y, w, h = x0 + k * u, y0, u, 2 * u
                pshape(a, rect(x + 1.5, y + 1.5, x + w - 1.5, y + h - 1.5), corner=2, joint=True)
    return a.image(grain=0.02)


def p_herringbone(seed=205):
    a = pat(seed)
    for x, y, w, h in herringbone_bricks(T, T / 8):
        pshape(a, rect(x + 1.5, y + 1.5, x + w - 1.5, y + h - 1.5), corner=2, joint=True)
    return a.image(grain=0.02)

def p_diamonds(seed=206):
    a = pat(seed)
    n = 4
    cell = T / n
    for i in range(n + 1):
        for j in range(n + 1):
            for ox, oy in ((0, 0), (cell / 2, cell / 2)):
                cx, cy = i * cell + ox, j * cell + oy
                r = cell / 2 - 3
                pshape(a, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], corner=2)
    return a.image(grain=0.02)


def p_circles(seed=207):
    a = pat(seed)
    n = 4
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            pshape(a, ellipse(cx, cy, cell * 0.42, cell * 0.42, 40), corner=0)
    return a.image(grain=0.02)


def p_scales(seed=208):
    a = pat(seed)
    n = 4
    w = T / n
    rows = 8
    rh = T / rows
    for j in range(rows + 1):
        for i in range(-1, n + 1):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * rh
            r = w / 2 - 2
            pts = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [math.pi * k / 16 for k in range(17)]]
            pts += [(cx - r, cy - rh * 0.6), (cx + r, cy - rh * 0.6)][::-1] if False else []
            pts = [(cx - r, cy - r * 0.25)] + pts[::-1] + [(cx + r, cy - r * 0.25)]
            pts = [(cx + r, cy - r * 0.25)] + [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [math.pi * k / 16 for k in range(17)]] + [(cx - r, cy - r * 0.25)]
            pshape(a, pts, 2.3, 2)
    return a.image(grain=0.02)


def p_stars(seed=209):
    a = pat(seed)
    n = 4
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            pts = []
            for k in range(10):
                r = cell * (0.44 if k % 2 == 0 else 0.2)
                t = -math.pi / 2 + k * math.pi / 5
                pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
            pshape(a, pts, 2.2, 1)
    return a.image(grain=0.02)


def p_chevrons(seed=210):
    a = pat(seed)
    n = 4
    cell = T / n
    for j in range(n):
        for i in range(n):
            x0, y0 = i * cell, j * cell
            t = cell * 0.3
            pts = [(x0, y0 + t), (x0 + cell / 2, y0 + t * 0.2 + 2), (x0 + cell, y0 + t), (x0 + cell, y0 + t + cell * 0.4), (x0 + cell / 2, y0 + t * 0.2 + cell * 0.4 + 2), (x0, y0 + t + cell * 0.4)]
            pshape(a, pts, 2.3, 1)
    return a.image(grain=0.02)


def p_brick_bond(seed=211):
    a = pat(seed)
    rows = 8
    h = T / rows
    bw = 2 * h
    for r in range(rows):
        off = 0 if r % 2 == 0 else bw / 2
        for k in range(-1, int(T / bw) + 1):
            x = k * bw + off
            pshape(a, rect(x + 1.5, r * h + 1.5, x + bw - 1.5, r * h + h - 1.5), corner=2, joint=True)
    return a.image(grain=0.02)


def p_octagons(seed=212):
    a = pat(seed)
    n = 4
    cell = T / n
    c = cell * 0.29
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell + 2.5, j * cell + 2.5
            x1, y1 = (i + 1) * cell - 2.5, (j + 1) * cell - 2.5
            pshape(a, [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)], 2.4, 1)
    return a.image(grain=0.02)


def p_waves(seed=213):
    """Wavy bands: filled without closing edges (so the wrap is clean) and
    inked only along the waves."""
    a = pat(seed)
    rows = 6
    h = T / rows
    xs = np.linspace(-T * 0.5, T * 1.5, 80)
    for r in range(rows):
        y = r * h
        wave = lambda x, yy: yy + 7 * math.sin(2 * math.pi * x / (T / 2))  # noqa: E731
        top = [(x, wave(x, y)) for x in xs]
        bot = [(x, wave(x, y + h * 0.5)) for x in xs[::-1]]
        col = vary(a.rng, P_RED, 0.04)
        p = skia.Path()
        p.addPoly(top + bot, True)
        a.c.save()
        a.c.clipRect(skia.Rect.MakeWH(T, T))
        a.c.drawPath(p, a.paint(col))
        sh = skia.Path()
        sh.addPoly([(x, yy - 5) for x, yy in bot[::-1]] + bot, True)
        a.c.drawPath(sh, a.paint(shade(P_RED, 0.3), 0.45, blur=1.5))
        a.c.restore()
        for line in (top, bot):
            q = [(x, yy) for x, yy in line if -10 <= x <= T + 10]
            a.ink(q, 2.3, taper=False, wob=0.3)
    return a.image(grain=0.02)

def p_triangles(seed=214):
    a = pat(seed)
    n = 4
    cell = T / n
    for j in range(n):
        for i in range(-1, n + 1):
            x0, y0 = i * cell + (cell / 2 if j % 2 else 0), j * cell
            pshape(a, [(x0 + 3, y0 + cell - 3), (x0 + cell / 2, y0 + 4), (x0 + cell - 3, y0 + cell - 3)], 2.3, 2)
    return a.image(grain=0.02)


def p_small_mosaic(seed=215):
    a = pat(seed)
    n = 10
    cell = T / n
    for i in range(n):
        for j in range(n):
            if a.rng.random() < 0.7:
                x0, y0 = i * cell + a.rng.uniform(-1.5, 1.5), j * cell + a.rng.uniform(-1.5, 1.5)
                pshape(a, rect(x0 + 2.4, y0 + 2.4, x0 + cell - 2.4, y0 + cell - 2.4), 1.8, 2)
    return a.image(grain=0.02)


def p_crosses(seed=216):
    a = pat(seed)
    n = 4
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            r, t = cell * 0.4, cell * 0.13
            pshape(a, [(cx - t, cy - r), (cx + t, cy - r), (cx + t, cy - t), (cx + r, cy - t), (cx + r, cy + t), (cx + t, cy + t), (cx + t, cy + r), (cx - t, cy + r), (cx - t, cy + t), (cx - r, cy + t), (cx - r, cy - t), (cx - t, cy - t)], 2.2, 1)
    return a.image(grain=0.02)


def p_rings(seed=217):
    a = pat(seed)
    n = 4
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            outer = ellipse(cx, cy, cell * 0.44, cell * 0.44, 40)
            inner = ellipse(cx, cy, cell * 0.22, cell * 0.22, 32)[::-1]
            path = to_path(outer)
            path.addPath(to_path(inner))
            path.setFillType(skia.PathFillType.kEvenOdd)
            col = vary(a.rng, P_RED, 0.05)
            a.fill_path(path, col)
            a.ink(outer, 2.3, closed=True, wob=0.3)
            a.ink(inner, 2.0, closed=True, wob=0.3)
    return a.image(grain=0.02)


def p_checker(seed=218):
    a = pat(seed)
    n = 4
    cell = T / n
    for i in range(n):
        for j in range(n):
            if (i + j) % 2 == 0:
                x0, y0 = i * cell, j * cell
                pshape(a, rect(x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2), 2.4, 2)
    return a.image(grain=0.02)


def p_quatrefoil(seed=219):
    a = pat(seed)
    n = 4
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            pts = []
            for k in range(64):
                t = 2 * math.pi * k / 64
                r = cell * (0.3 + 0.12 * abs(math.cos(2 * t)))
                pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
            pshape(a, pts, 2.3, 0)
    return a.image(grain=0.02)


def p_dots(seed=220):
    a = pat(seed)
    n = 8
    cell = T / n
    for i in range(n):
        for j in range(n):
            ox = cell / 2 if j % 2 else 0
            cx, cy = i * cell + ox + cell / 4, j * cell + cell / 2
            pshape(a, ellipse(cx, cy, cell * 0.24, cell * 0.24, 24), 1.8, 0)
    return a.image(grain=0.02)


PATTERNS = {
    "Square Tiles": p_tiles,
    "Large Tiles": lambda: p_tiles(221, n=2, gap=4),
    "Offset Tiles": p_offset_tiles,
    "Hexagons": p_hex,
    "Basketweave": p_basketweave,
    "Herringbone": p_herringbone,
    "Diamonds": p_diamonds,
    "Circles": p_circles,
    "Scales": p_scales,
    "Stars": p_stars,
    "Chevrons": p_chevrons,
    "Brick Bond": p_brick_bond,
    "Octagons": p_octagons,
    "Waves": p_waves,
    "Triangles": p_triangles,
    "Small Mosaic": p_small_mosaic,
    "Crosses": p_crosses,
    "Rings": p_rings,
    "Checker": p_checker,
    "Quatrefoils": p_quatrefoil,
    "Dots": p_dots,
}


# ===================================================================================================
# TERRAIN (512x512 seamless, alpha = height)
# ===================================================================================================


def with_height(img, field, lo=0.5):
    a = np.asarray(img).copy()
    a[..., 3] = ((lo + (1 - lo) * field) * 255).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def terrain(seed, base, blotch=(), strokes=None, stones=None, dots=None, leaves=None, flowers=None, ripples=None, cracks=0, scale=72, lo=0.5, tint_k=0.06):
    """A seamless terrain: flat base, soft blotches, then optional details
    (grass strokes, stones, specks, leaves, flowers, ripples, cracks)."""
    s = S2
    base = rgb(base)
    a = Art(s, s, seed, tile=True, bg=base)
    for _ in range(36):
        if not blotch:
            break
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.fill_path(to_path(blob(x, y, a.rng.uniform(22, 60), a.rng, 12, 0.3)), rgb(a.rng.choice(blotch)), 0.22, blur=6)
    if ripples:
        col, n = ripples
        for r in range(n):
            y = r * s / n + a.rng.uniform(-6, 6)
            pts = [(x, y + 5 * math.sin(2 * math.pi * x / s * 3 + r)) for x in np.linspace(-20, s + 20, 30)]
            a.ink(pts, FINE * 1.2, color=rgb(col), alpha=0.6, wob=0.3, taper=False)
    if cracks:
        for _ in range(cracks):
            crack(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0, 6.28), a.rng.uniform(40, 90), FINE * 1.1, 0.6)
    if stones:
        n, cols, rr = stones
        for _ in range(n):
            x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
            a.shape(blob(x, y, a.rng.uniform(*rr), a.rng, 8, 0.25), vary(a.rng, rgb(a.rng.choice(cols)), 0.06), outline=1.6, corner=0, wob=0.3, depth=2, shade_k=0.45, light_k=0.45, ao=0, mottle=0)
    if leaves:
        n, cols = leaves
        for _ in range(n):
            x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
            t = a.rng.uniform(0, 6.28)
            L, W = a.rng.uniform(12, 20), a.rng.uniform(5, 8)
            ux, uy = math.cos(t), math.sin(t)
            pts = [(x - ux * L / 2, y - uy * L / 2), (x - uy * W / 2, y + ux * W / 2), (x + ux * L / 2, y + uy * L / 2), (x + uy * W / 2, y - ux * W / 2)]
            a.shape(chaikin(pts, True, 1), vary(a.rng, rgb(a.rng.choice(cols)), 0.06), outline=1.2, corner=0, wob=0.1, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    if strokes:
        for n, col, ln, w in strokes:
            for _ in range(n):
                x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
                t = -math.pi / 2 + a.rng.uniform(-0.5, 0.5)
                L = a.rng.uniform(*ln)
                a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], w, color=rgb(col), alpha=0.75, wob=0.1, var=0.1)
    if flowers:
        n, cols = flowers
        for _ in range(n):
            x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
            c = rgb(a.rng.choice(cols))
            for k in range(5):
                t = 2 * math.pi * k / 5
                dot(a, x + 3.4 * math.cos(t), y + 3.4 * math.sin(t), 2.6, c, 0.95)
            dot(a, x, y, 1.6, rgb("#e6b84a"))
    if dots:
        n, col, rr = dots
        for _ in range(n):
            dot(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(*rr), rgb(col), 0.6)
    img = a.image()
    field = periodic_noise(s, s, scale, seed + 3)
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= (1 - tint_k / 2 + field[..., None] * tint_k)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    return with_height(img, field, lo)


TERRAINS = {
    "Grass": lambda: terrain(301, "#7aa152", ("#6f9a48", "#86ad5d"), strokes=[(800, "#4d7232", (5, 10), 1.6), (240, "#a9c77c", (4, 8), 1.4)], lo=0.6),
    "Lush Grass": lambda: terrain(302, "#5f9440", ("#558a38", "#6ea04c"), strokes=[(1100, "#3a6326", (6, 12), 1.7), (300, "#8cbc60", (4, 9), 1.4)], lo=0.6),
    "Dry Grass": lambda: terrain(303, "#b4ab64", ("#a89e58", "#c2b872"), strokes=[(900, "#8a7e40", (6, 12), 1.5), (260, "#d8cf8a", (4, 8), 1.3)], lo=0.55),
    "Autumn Grass": lambda: terrain(304, "#a8984e", ("#b0863e", "#9a9a4c"), strokes=[(700, "#7a6a2e", (5, 10), 1.5)], leaves=(90, ("#c9752f", "#d99a3a", "#b54a2c")), lo=0.55),
    "Flower Meadow": lambda: terrain(305, "#7aa152", ("#6f9a48", "#86ad5d"), strokes=[(700, "#4d7232", (5, 10), 1.6)], flowers=(140, ("#f3eee2", "#e6b84a", "#c86ab8", "#e88aa8")), lo=0.6),
    "Moss": lambda: terrain(306, "#6f8f45", ("#64843c", "#7f9e52", "#5a7a36"), dots=(1600, "#4f6e30", (0.8, 2.2)), lo=0.6),
    "Dirt": lambda: terrain(307, "#a17d55", ("#94704b", "#ad8a60"), stones=(60, ("#8f8274", "#9d9183"), (2.5, 5)), dots=(500, "#6e5236", (0.5, 1.2)), lo=0.5),
    "Mud": lambda: terrain(308, "#6e5641", ("#5e4836", "#7a6049"), ripples=("#4e3a2a", 10), dots=(300, "#4a3828", (0.8, 2)), cracks=0, lo=0.5),
    "Clay": lambda: terrain(309, "#b8774f", ("#a86a44", "#c4845a"), cracks=24, dots=(300, "#8a5236", (0.5, 1.2)), lo=0.5),
    "Sand": lambda: terrain(310, "#dcc48f", ("#d2b984", "#e4cf9e"), ripples=("#b89c62", 14), dots=(700, "#a88e5a", (0.4, 0.9)), scale=96, lo=0.5),
    "Gravel": lambda: terrain(311, "#8f8b84", (), stones=(260, ("#a9a59d", "#7c7871", "#958f86"), (4, 9)), lo=0.55, scale=40),
    "Pebbles": lambda: terrain(312, "#a39a88", ("#9a917f",), stones=(140, ("#b8b0a2", "#8f948f", "#c4b8a0"), (6, 13)), lo=0.55),
    "Rocky Ground": lambda: terrain(313, "#8a8378", ("#7e776c", "#958e82"), stones=(36, ("#9d978d", "#86807a"), (14, 30)), cracks=10, dots=(300, "#5e5850", (0.5, 1.2)), lo=0.5),
    "Leaf Litter": lambda: terrain(314, "#7a6244", ("#6e583c", "#86704e"), leaves=(420, ("#c9752f", "#d99a3a", "#b54a2c", "#a8652f", "#8a6a40")), lo=0.55),
    "Snow": lambda: terrain(315, "#eef1f4", ("#e2e8ee", "#f6f8fa"), ripples=("#c8d4e0", 8), dots=(200, "#c0ccd8", (0.6, 1.4)), scale=110, lo=0.55, tint_k=0.04),
    "Ice": lambda: terrain(316, "#bcd8e4", ("#aacbd8", "#cde4ec"), cracks=30, lo=0.5, tint_k=0.05),
    "Swamp": lambda: terrain(317, "#5a6a3e", ("#4a5c34", "#66763f", "#3e5240"), strokes=[(300, "#3a4a26", (6, 12), 1.5)], dots=(400, "#7a8a4a", (1, 2.5)), lo=0.5),
    "Ash": lambda: terrain(318, "#6b6763", ("#5e5a56", "#7a7672"), dots=(700, "#3e3a36", (0.6, 1.6)), cracks=8, lo=0.5),
    "Lava Crust": lambda: terrain(319, "#3a302c", ("#2e2624", "#463a34"), cracks=46, dots=(200, "#e9773a", (1, 2.2)), lo=0.5),
    "Forest Floor": lambda: terrain(320, "#5e5a3a", ("#54503a", "#6a6440"), leaves=(200, ("#8a6a40", "#6f8f45", "#a8652f")), strokes=[(200, "#3e4a26", (5, 9), 1.4)], dots=(200, "#3e3626", (0.8, 1.6)), lo=0.55),
}


# ===================================================================================================
# PATHS (drawn as 512 x ~150 strips, periodic along x, transparent outside;
# saved at 2x, 1024 x ~300: a path is as wide as its texture is tall, so this
# puts their stones and boards at the scale of the floors and objects)
# ===================================================================================================

PW, PH = S2, 150
PATH_SCALE = 2


def path_edges(rng, h=PH, margin=18, amp=6, x0=-40, x1=PW + 40):
    """Wavy top and bottom edges, periodic over the strip's width (sampled a
    little past both ends, so wrapped copies continue them seamlessly)."""
    ph = [rng.uniform(0, 6.28) for _ in range(4)]
    xs = np.linspace(x0, x1, 80)
    top = [(x, margin + amp * math.sin(2 * math.pi * x / PW * 2 + ph[0]) + amp * 0.5 * math.sin(2 * math.pi * x / PW * 5 + ph[1])) for x in xs]
    bot = [(x, h - margin + amp * math.sin(2 * math.pi * x / PW * 3 + ph[2]) + amp * 0.5 * math.sin(2 * math.pi * x / PW * 7 + ph[3])) for x in xs]
    return top, bot


def strip_poly(top, bot):
    return top + bot[::-1]

def path_strip(seed, base, edge_ink=True, fill=True, content=None, h=PH, margin=18, amp=6, edge_col=None):
    a = Art(PW, h, seed, tile=True)
    top, bot = path_edges(a.rng, h, margin, amp)
    path = to_path(strip_poly(top, bot))
    base = rgb(base)
    if fill:
        a.fill_path(path, base)
    with a.clip(path):
        if fill:
            for _ in range(14):
                x, y = a.rng.uniform(0, PW), a.rng.uniform(margin, h - margin)
                a.fill_path(to_path(blob(x, y, a.rng.uniform(18, 34), a.rng, 10, 0.3)), vary(a.rng, base, 0.06), 0.22, blur=6)
        if content:
            content(a, top, bot)
    if edge_ink:
        ec = rgb(edge_col) if edge_col else shade(base, 0.6)
        for line in (top, bot):
            a.ink(line, 1.9, color=ec, alpha=0.9, taper=False, wob=0.0, var=0.08)
    return a.image(scale=PATH_SCALE)

def stones_in(a, top, bot, cols, r=(14, 22), n=None, outline=2.6, spacing=1.0, rows=2):
    span_t = min(p[1] for p in top if 0 <= p[0] <= PW)
    span_b = max(p[1] for p in bot if 0 <= p[0] <= PW)
    hh = span_b - span_t
    rr = (r[0] + r[1]) / 2
    count = n or int(PW / (rr * 1.9 * spacing))
    for row in range(rows):
        for k in range(count):
            x = (k + 0.5 + (0.5 if row % 2 else 0)) * PW / count + a.rng.uniform(-4, 4)
            y = span_t + hh * (row + 0.5) / rows + a.rng.uniform(-6, 6)
            c = vary(a.rng, rgb(a.rng.choice(cols)), 0.06)
            a.shape(blob(x, y, a.rng.uniform(*r), a.rng, 9, 0.18), c, outline=JOINT * 1.3, outline_color=shade(c, 0.6), outline_alpha=0.85, corner=0, wob=0.4, depth=4, shade_k=0.45, light_k=0.35, ao=0.12, mottle=0)


def cobble_content(cols):
    def f(a, top, bot):
        stones_in(a, top, bot, cols, (11, 15), rows=4, outline=2.4)

    return f


def gravel_content(a, top, bot):
    for _ in range(320):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(10, PH - 10)
        a.shape(blob(x, y, a.rng.uniform(3, 6.5), a.rng, 8, 0.25), vary(a.rng, rgb(a.rng.choice(("#a9a59d", "#8a867f", "#9d978d"))), 0.06), outline=1.3, corner=0, wob=0.2, depth=1.5, shade_k=0.4, light_k=0.4, ao=0, mottle=0)


def dirt_content(a, top, bot):
    for ry in (0.38, 0.62):
        y = PH * ry
        a.ink([(x, y + 3 * math.sin(2 * math.pi * x / PW * 4)) for x in np.linspace(-20, PW + 20, 40)], 1.4, color=rgb("#7e5e3c"), alpha=0.6, taper=False)
    for _ in range(36):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(30, PH - 30)
        a.shape(blob(x, y, a.rng.uniform(2.5, 4.5), a.rng, 8), rgb("#988c7e"), outline=1.2, corner=0, wob=0.2, depth=1.2, shade_k=0.3, light_k=0.3, ao=0, mottle=0)


def boards_content(color, across=True, gap=26):
    def f(a, top, bot):
        col = rgb(color)
        if across:
            x = 0
            while x < PW - 2:
                w = gap
                c = vary(a.rng, col, 0.05)
                a.shape(rect(x + 0.8, 4, x + w - 0.8, PH - 4), c, **jkw(c), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.04, detail=lambda art, p, x=x, c=c: art.ink([(x + w / 2 + art.rng.uniform(-3, 3), 12), (x + w / 2 + art.rng.uniform(-3, 3), PH - 12)], FINE * 0.8, color=shade(c, 0.45), alpha=0.6))
                for ny in (20, PH - 20):
                    dot(a, x + w / 2, ny, 2, shade(c, 0.6), 0.7)
                x += w
        else:
            rows = 5
            hh = PH / rows
            for r in range(rows):
                x = a.rng.uniform(0, PW)
                for ln in split(PW, a.rng, PW * 0.3, PW * 0.6):
                    c = vary(a.rng, col, 0.05)
                    a.shape(rect(x + 0.8, r * hh + 0.8, x + ln - 0.8, r * hh + hh - 0.8), c, **jkw(c), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.04)
                    x += ln

    return f


def flag_content(cols, n=7):
    def f(a, top, bot):
        for (cx, cy), poly in voronoi_cells(PW, PH, n, 2, a.rng, 0.3):
            p = inset(poly, 2)
            c = vary(a.rng, rgb(a.rng.choice(cols)), 0.05)
            a.shape(p, c, **jkw(c, 1.2), corner=7, wob=0.7, depth=4, shade_k=0.4, light_k=0.3, ao=0.15, detail=lambda art, path: speckles(art, path, shade(rgb(cols[0]), 0.45), 6))

    return f


def brick_content(cols):
    def f(a, top, bot):
        rows = 5
        hh = PH / rows
        bw = 2 * hh
        for r in range(rows):
            off = 0 if r % 2 == 0 else bw / 2
            for k in range(-1, int(PW / bw) + 1):
                x = k * bw + off
                c = vary(a.rng, rgb(a.rng.choice(cols)), 0.05)
                a.shape(rect(x + 1, r * hh + 1, x + bw - 1, r * hh + hh - 1), c, **jkw(c), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.03)

    return f


def grass_trail_content(a, top, bot):
    for _ in range(260):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(20, PH - 20)
        t = -math.pi / 2 + a.rng.uniform(-0.5, 0.5)
        L = a.rng.uniform(4, 8)
        a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], 1.4, color=rgb("#6a8a44"), alpha=0.7, wob=0.1, var=0.1)


def mud_content(a, top, bot):
    for ry in (0.36, 0.64):
        y = PH * ry
        a.ink([(x, y + 4 * math.sin(2 * math.pi * x / PW * 3)) for x in np.linspace(-20, PW + 20, 40)], 3.0, color=rgb("#4a3828"), alpha=0.7, taper=False)
    for _ in range(10):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(40, PH - 40)
        a.shape(blob(x, y, a.rng.uniform(10, 18), a.rng, 9, 0.25, ry=a.rng.uniform(6, 10)), rgb("#6f8fa0"), outline=1.4, corner=0, wob=0.3, depth=2, shade_k=0, light_k=0.4, ao=0.3, mottle=0)


def mossy_content(a, top, bot):
    stones_in(a, top, bot, ("#8f948a", "#9d9a8e", "#7f857c"), (13, 20), rows=2)
    for _ in range(26):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(20, PH - 20)
        a.fill_path(to_path(blob(x, y, a.rng.uniform(6, 12), a.rng, 9, 0.3)), rgb("#6f9443"), 0.85)


def stepping_content(a, top, bot):
    for k in range(5):
        x = (k + 0.5) * PW / 5 + a.rng.uniform(-10, 10)
        y = PH / 2 + a.rng.uniform(-14, 14)
        a.shape(blob(x, y, a.rng.uniform(34, 42), a.rng, 10, 0.12, ry=a.rng.uniform(26, 32)), vary(a.rng, rgb("#a39d93"), 0.06), outline=3.0, corner=0, wob=0.6, depth=7, shade_k=0.55, light_k=0.45, ao=0.2, detail=lambda art, p: speckles(art, p, rgb("#6f6a62"), 10))


def plank_bridge_content(a, top, bot):
    boards_content("#9a6c43", across=True, gap=30)(a, top, bot)
    for y in (6, PH - 6):
        a.shape(rect(-20, y - 7, PW + 20, y + 7), rgb("#6e4a2f"), outline=2.4, corner=3, wob=0.3, depth=3, shade_k=0.45, light_k=0.3, ao=0.1, mottle=0.03)


PATHS = {
    "Dirt Road": lambda: path_strip(401, "#b08a5e", content=dirt_content),
    "Muddy Road": lambda: path_strip(402, "#6e5641", content=mud_content),
    "Sand Trail": lambda: path_strip(403, "#dcc48f", content=lambda a, t, b: [dot(a, a.rng.uniform(0, PW), a.rng.uniform(20, PH - 20), a.rng.uniform(0.5, 1.2), rgb("#a88e5a"), 0.6) for _ in range(400)], margin=26, amp=8),
    "Grass Trail": lambda: path_strip(404, "#9aa86a", content=grass_trail_content, margin=30, amp=9),
    "Narrow Footpath": lambda: path_strip(405, "#a68660", content=dirt_content, margin=42, amp=10),
    "Gravel Path": lambda: path_strip(406, "#8f8b84", content=gravel_content),
    "Cobblestone Road": lambda: path_strip(407, "#858077", content=cobble_content(("#aaa49b", "#958f86", "#a39d93")), margin=10, amp=2),
    "Red Cobblestone": lambda: path_strip(408, "#8a7064", content=cobble_content(("#b07a5e", "#9a6a52", "#a87862")), margin=10, amp=2),
    "Flagstone Path": lambda: path_strip(409, "#8a847a", content=flag_content(("#a9a296", "#b8ae9c", "#968f86")), margin=10, amp=2),
    "Sandstone Path": lambda: path_strip(410, "#a89270", content=flag_content(("#cdb68e", "#d9c49c", "#bfa67e")), margin=10, amp=2),
    "Brick Road": lambda: path_strip(411, "#c9b9a2", content=brick_content(("#a8503b", "#94432f", "#b5604a")), margin=8, amp=1),
    "Yellow Brick Road": lambda: path_strip(412, "#b8a070", content=brick_content(("#d9b04a", "#c9a03e", "#e4c060")), margin=8, amp=1),
    "Stepping Stones": lambda: path_strip(413, "#000000", fill=False, edge_ink=False, content=stepping_content),
    "River Pebbles": lambda: path_strip(414, "#8a8478", content=lambda a, t, b: stones_in(a, t, b, ("#a8a49a", "#8f948f", "#b8ad9a", "#7f857f"), (8, 13), rows=4, outline=2.0)),
    "Mossy Stones": lambda: path_strip(415, "#7c7c6c", content=mossy_content),
    "Boardwalk": lambda: path_strip(416, "#9a6c43", content=boards_content("#a8784e", across=True), margin=6, amp=0),
    "Plank Bridge": lambda: path_strip(417, "#9a6c43", content=plank_bridge_content, margin=2, amp=0, edge_ink=False),
    "Wooden Walkway": lambda: path_strip(418, "#9a6c43", content=boards_content("#b8875a", across=False), margin=6, amp=0),
    "Snowy Path": lambda: path_strip(419, "#e6ecf1", content=lambda a, t, b: [a.ink([(x, y), (x + 8, y + 2)], 2.0, color=rgb("#b8c6d4"), alpha=0.7) for x, y in [(a.rng.uniform(0, PW), a.rng.uniform(30, PH - 30)) for _ in range(60)]], edge_col="#9aaabb"),
    "Ash Trail": lambda: path_strip(420, "#5e5a56", content=lambda a, t, b: [dot(a, a.rng.uniform(0, PW), a.rng.uniform(20, PH - 20), a.rng.uniform(0.6, 1.6), rgb("#2e2a28"), 0.6) for _ in range(500)]),
}


# ===================================================================================================
# LIGHTS (512x512 white shapes; alpha = intensity; tinted by the light color)
# ===================================================================================================

LS = 512


def _grid():
    y, x = np.mgrid[0:LS, 0:LS].astype(np.float32)
    dx, dy = (x - LS / 2) / (LS / 2), (y - LS / 2) / (LS / 2)
    return dx, dy, np.hypot(dx, dy), np.arctan2(dy, dx)


def _light(alpha, grey=255):
    alpha = np.clip(alpha, 0, 1)
    a = (alpha * 255).astype(np.uint8)
    g = np.full_like(a, grey)
    return Image.fromarray(np.dstack([g, g, g, a]), "RGBA")


def _edge(d):
    """Fade everything to 0 before the image edge."""
    return np.clip((1.0 - d) / 0.08, 0, 1)


def _noise(scale, seed, octaves=3):
    return periodic_noise(LS, LS, scale, seed, octaves)


def l_soft():
    dx, dy, d, t = _grid()
    return _light(np.clip(1 - d, 0, 1) ** 1.6)


def l_bright():
    dx, dy, d, t = _grid()
    return _light(np.clip(1 - d, 0, 1) ** 0.8 * _edge(d))


def l_hard():
    dx, dy, d, t = _grid()
    return _light(np.clip((0.8 - d) / 0.06, 0, 1) * 0.9 + np.clip(1 - d, 0, 1) ** 3 * 0.1)


def l_rays():
    dx, dy, d, t = _grid()
    return _light(np.clip(1 - d, 0, 1) ** 1.5 * (0.8 + 0.2 * np.cos(t * 12)))


def l_sunburst():
    dx, dy, d, t = _grid()
    spokes = np.clip(np.cos(t * 8), 0, 1) ** 6
    return _light((np.clip(1 - d, 0, 1) ** 2.2 * 0.6 + spokes * np.clip(1 - d, 0, 1) ** 1.2 * 0.6) * _edge(d))


def l_flicker():
    dx, dy, d, t = _grid()
    n = _noise(80, 7)
    return _light(np.clip(1 - d * (0.85 + 0.3 * n), 0, 1) ** 1.6 * _edge(d))


def l_ring():
    dx, dy, d, t = _grid()
    return _light(np.exp(-((d - 0.6) / 0.14) ** 2) * 0.9 + np.clip(1 - d, 0, 1) ** 3 * 0.25)


def l_double_ring():
    dx, dy, d, t = _grid()
    return _light((np.exp(-((d - 0.35) / 0.08) ** 2) * 0.7 + np.exp(-((d - 0.72) / 0.1) ** 2) * 0.6) * _edge(d))


def l_window():
    dx, dy, d, t = _grid()
    sq = np.clip((0.55 - np.maximum(abs(dx), abs(dy))) / 0.12, 0, 1)
    bars = 1 - 0.85 * np.clip(1 - np.minimum(abs(dx), abs(dy)) / 0.03, 0, 1)
    return _light(sq * bars * 0.95)


def l_window_wide():
    dx, dy, d, t = _grid()
    sq = np.clip((0.75 - abs(dx)) / 0.15, 0, 1) * np.clip((0.4 - abs(dy)) / 0.12, 0, 1)
    bars = 1 - 0.85 * np.clip(1 - np.minimum(abs(dx % 0.5 - 0.25) * 4, abs(dy) * 10), 0, 1) * 0
    mull = 1 - 0.85 * np.clip(1 - abs(((dx + 0.75) % 0.5) - 0.25) / 0.02, 0, 1) * 0 - 0.85 * np.clip(1 - abs(dx) / 0.02, 0, 1)
    return _light(sq * mull * 0.95)


def l_cone():
    dx, dy, d, t = _grid()
    # Spotlight pointing right: a wedge from the centre, soft sides.
    ang = np.abs(np.angle(np.exp(1j * t)))
    wedge = np.clip((0.5 - ang) / 0.2, 0, 1)
    return _light(np.clip(wedge * np.clip(1 - d, 0, 1) ** 0.7 * _edge(d) + np.clip(1 - d / 0.12, 0, 1) * 0.7, 0, 1))


def l_spot():
    dx, dy, d, t = _grid()
    return _light(np.clip((0.45 - d) / 0.25, 0, 1) ** 1.2)


def l_star():
    dx, dy, d, t = _grid()
    r = 0.28 + 0.6 * np.abs(np.cos(t * 2.5)) ** 8
    return _light(np.clip(np.clip((r - d) / 0.3, 0, 1) ** 1.2 + np.clip(1 - d / 0.35, 0, 1) ** 2 * 0.5, 0, 1))


def l_cross():
    dx, dy, d, t = _grid()
    beams = np.clip(1 - np.minimum(abs(dx), abs(dy)) / 0.12, 0, 1) ** 2 * np.clip(1 - d, 0, 1)
    return _light(np.clip(beams + np.clip(1 - d / 0.3, 0, 1) ** 2, 0, 1) * _edge(d))


def l_caustics():
    dx, dy, d, t = _grid()
    n1 = _noise(60, 11)
    n2 = _noise(90, 13)
    lines = np.clip(1 - np.abs(n1 - 0.5) * 10, 0, 1) * 0.7 + np.clip(1 - np.abs(n2 - 0.5) * 12, 0, 1) * 0.5
    return _light(np.clip(lines * 0.8 + 0.25, 0, 1) * np.clip(1 - d, 0, 1) ** 0.9 * _edge(d))


def l_dappled():
    dx, dy, d, t = _grid()
    n = _noise(50, 17)
    return _light(np.clip((n - 0.45) * 3.5, 0, 1) * np.clip(1 - d, 0, 1) ** 0.8 * _edge(d))


def l_noise():
    dx, dy, d, t = _grid()
    n = _noise(120, 19)
    return _light(np.clip(1 - d, 0, 1) ** 1.4 * (0.6 + 0.5 * n))


def l_lantern_grid():
    dx, dy, d, t = _grid()
    grid = np.clip(1 - np.minimum(np.abs((dx * 3) % 1 - 0.5), np.abs((dy * 3) % 1 - 0.5)) / 0.06, 0, 1)
    return _light(np.clip(1 - d, 0, 1) ** 1.5 * (1 - 0.6 * grid))


def l_ellipse():
    dx, dy, d, t = _grid()
    e = np.hypot(dx / 1.0, dy / 0.5)
    return _light(np.clip(1 - e, 0, 1) ** 1.4)


def l_pulse():
    dx, dy, d, t = _grid()
    return _light(np.clip(1 - d, 0, 1) ** 1.2 * (0.75 + 0.25 * np.cos(d * 22)) * _edge(d))


LIGHTS = {
    "Soft Light": l_soft,
    "Bright Light": l_bright,
    "Hard Light": l_hard,
    "Radiant Light": l_rays,
    "Sunburst": l_sunburst,
    "Flicker": l_flicker,
    "Ring Light": l_ring,
    "Double Ring": l_double_ring,
    "Window Light": l_window,
    "Wide Window Light": l_window_wide,
    "Spotlight Cone": l_cone,
    "Spot": l_spot,
    "Star Light": l_star,
    "Cross Beams": l_cross,
    "Water Caustics": l_caustics,
    "Dappled Light": l_dappled,
    "Noisy Glow": l_noise,
    "Lantern Grid": l_lantern_grid,
    "Oval Light": l_ellipse,
    "Pulse Rings": l_pulse,
}
