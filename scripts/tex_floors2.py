"""More floor tilesets for the built-in pack (512x512 seamless), in the same
hand-inked look as floors.py / tex_ground.FLOORS: woods, stones, tiles,
carpets, loose floors and fantasy materials. Exported as FLOORS2."""

import math

import numpy as np

from floors import crack, inset, speckles, split, voronoi_cells
from pen import DETAIL, FINE, INK, JOINT, JOINT_ALPHA, Art, grout, joint_color, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary
from tex_ground import S2, ashlar, brick_floor, carpet_floor, cobbles, dot, flag_floor, herringbone, parquet, planks, tiles


def rgbs(cols):
    return [rgb(c) for c in cols]


def _rgb(c):
    return rgb(c) if isinstance(c, str) else tuple(c)


def _lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def soft_gap(gap, tones):
    """Joint background close to the pieces' tone: a dark `gap` only nudges it
    darker, a light mortar pulls it lighter. Never a near-black trench."""
    cols = [_rgb(t) for t in tones]
    base = tuple(sum(c[i] for c in cols) / len(cols) for i in range(3))
    g = _rgb(gap)
    return grout(base, g) if _lum(g) > _lum(base) else mix(grout(base), g, 0.15)


def J(c, k=1.0):
    """Thin, tone-on-tone joint outline for a piece of colour `c`."""
    return dict(outline=JOINT * k, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA)


# ---------------------------------------------------------------------------------------------------
# Wood
# ---------------------------------------------------------------------------------------------------


def plank_grain(art, x, y, ln, h, c, horizontal=True, knots=0.3):
    n = max(1, int(h / 22))
    for k in range(n):
        if horizontal:
            gy = y + h * (0.2 + 0.6 * (k + 0.5) / n) + art.rng.uniform(-3, 3)
            gx0 = x + art.rng.uniform(-10, ln * 0.3)
            gx1 = gx0 + ln * art.rng.uniform(0.5, 0.9)
            pts = [(gx, gy + 2.2 * math.sin((gx - gx0) / 55)) for gx in np.linspace(gx0, gx1, 10)]
        else:
            gx = x + h * (0.2 + 0.6 * (k + 0.5) / n) + art.rng.uniform(-3, 3)
            gy0 = y + art.rng.uniform(-10, ln * 0.3)
            gy1 = gy0 + ln * art.rng.uniform(0.5, 0.9)
            pts = [(gx + 2.2 * math.sin((gy - gy0) / 55), gy) for gy in np.linspace(gy0, gy1, 10)]
        art.ink(pts, FINE * 0.85, color=shade(c, 0.45), alpha=0.7, wob=0.5)
    if art.rng.random() < knots:
        if horizontal:
            kx, ky = x + art.rng.uniform(ln * 0.25, ln * 0.75), y + h * art.rng.uniform(0.35, 0.65)
            art.ink(ellipse(kx, ky, 7, min(3.5, h * 0.12), 24), FINE, closed=True, color=shade(c, 0.5), alpha=0.8, wob=0.2)
        else:
            kx, ky = x + h * art.rng.uniform(0.35, 0.65), y + art.rng.uniform(ln * 0.25, ln * 0.75)
            art.ink(ellipse(kx, ky, min(3.5, h * 0.12), 7, 24), FINE, closed=True, color=shade(c, 0.5), alpha=0.8, wob=0.2)


def wood_floor(seed, tones, gap="#3b271b", rows=8, vertical=False, nails=True, wear=0.0, paint=None, bolts=False, lo=0.3, hi=0.65, gap_w=1.6):
    """Planks running across (or down) the tile. `paint` is drawn over the
    wood and worn through in patches by `wear`."""
    s = S2
    # Wide gaps (boardwalks) are real openings onto what's beneath; narrow
    # ones are just joints between boards.
    open_gaps = gap_w >= 4
    a = Art(s, s, seed, tile=True, bg=rgb(gap) if open_gaps else soft_gap(gap, tones))
    tones = rgbs(tones)
    if not open_gaps:
        gap_w = 0.8
    h = s / rows
    for r in range(rows):
        y = r * h
        x = a.rng.uniform(0, s)
        for ln in split(s, a.rng, s * lo, s * hi):
            c = vary(a.rng, a.rng.choice(tones), 0.04)
            if vertical:
                box = rect(y + gap_w, x + gap_w, y + h - gap_w, x + ln - gap_w)
            else:
                box = rect(x + gap_w, y + gap_w, x + ln - gap_w, y + h - gap_w)

            def detail(art, path, x=x, y=y, ln=ln, c=c):
                if vertical:
                    plank_grain(art, y, x, ln, h, c, horizontal=False)
                else:
                    plank_grain(art, x, y, ln, h, c)
                if paint is not None:
                    pc = vary(art.rng, rgb(paint), 0.03)
                    b = path.getBounds()
                    art.fill_path(path, pc, 0.92)
                    for _ in range(int(6 * wear)):
                        wx = art.rng.uniform(b.left(), b.right())
                        wy = art.rng.uniform(b.top(), b.bottom())
                        art.fill_path(to_path(blob(wx, wy, art.rng.uniform(6, 18), art.rng, 9, 0.4, ry=art.rng.uniform(3, 8))), c, 0.9)
                elif wear > 0:
                    b = path.getBounds()
                    for _ in range(int(10 * wear)):
                        wx, wy = art.rng.uniform(b.left(), b.right()), art.rng.uniform(b.top(), b.bottom())
                        L = art.rng.uniform(6, 18)
                        art.ink([(wx, wy), (wx + L, wy + art.rng.uniform(-2, 2))], FINE * 0.7, color=tint(c, 0.4), alpha=0.6, wob=0.2)

            a.shape(box, c, **J(c), corner=1.5, wob=0.4, depth=3, shade_k=0.35, light_k=0.25, ao=0.12, mottle=0.05, detail=detail)
            for e in (x + 9, x + ln - 9):
                for f in (y + h * 0.3, y + h * 0.7) if h > 40 else (y + h * 0.5,):
                    px, py = (f, e) if vertical else (e, f)
                    if bolts:
                        dot(a, px, py, 3.4, rgb("#4a4a50"), 0.95)
                        dot(a, px - 0.8, py - 0.8, 1.3, rgb("#a0a0a8"), 0.9)
                    elif nails:
                        dot(a, px, py, 2.0, shade(c, 0.6), 0.7)
            x += ln
    return a.image()


def herringbone45(seed, tones, gap="#3b271b", k=8):
    """Herringbone rotated 45° (the classic look): bricks laid along the
    diagonals, periodic over the tile."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(gap, tones))
    tones = rgbs(tones)
    u = s / (math.sqrt(2) * k)
    c45 = math.cos(math.pi / 4)

    def rot(px, py):
        return ((px - py) * c45, (px + py) * c45)

    n = int(s / u) * 2
    seen = set()
    for i in range(-n, n):
        for j in range(-n, n):
            x, y = (i - 2 * j) * u, (i + 2 * j) * u
            for bx, by, w, h in ((x, y, 2 * u, u), (x, y + u, u, 2 * u)):
                pts = [rot(px, py) for px, py in ((bx + 0.7, by + 0.7), (bx + w - 0.7, by + 0.7), (bx + w - 0.7, by + h - 0.7), (bx + 0.7, by + h - 0.7))]
                cx = sum(p[0] for p in pts) / 4
                cy = sum(p[1] for p in pts) / 4
                if not (-u * 2 < cx < s + u * 2 and -u * 2 < cy < s + u * 2):
                    continue
                key = (round(cx % s, 1), round(cy % s, 1), w > h)
                if key in seen:
                    continue
                seen.add(key)
                c = vary(a.rng, a.rng.choice(tones), 0.04)
                a.shape(pts, c, **J(c), corner=1.2, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.03)
    return a.image()


def chevron(seed, tones, gap="#3b271b", rows=8, cols=4):
    """Chevron parquet: planks cut at an angle, meeting in V's down columns."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(gap, tones))
    tones = rgbs(tones)
    cw = s / cols
    h = s / rows
    slope = cw * 0.5
    for ci in range(cols):
        x0 = ci * cw
        for r in range(-1, rows + 1):
            y = r * h
            for side in (0, 1):
                xa, xb = (x0, x0 + cw / 2) if side == 0 else (x0 + cw / 2, x0 + cw)
                if side == 0:
                    pts = [(xa, y + slope), (xb, y), (xb, y + h), (xa, y + h + slope)]
                else:
                    pts = [(xa, y), (xb, y + slope), (xb, y + h + slope), (xa, y + h)]
                pts = inset(pts, 0.9)
                c = vary(a.rng, a.rng.choice(tones), 0.04)
                a.shape(pts, c, **J(c), corner=1.2, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.03)
    return a.image()


def square_parquet(seed, tones, gap="#3b271b", n=4, strips=3, border=None):
    """Parquet of square blocks, each made of strips, alternating direction,
    optionally with a dark frame strip around each block."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(gap, tones))
    tones = rgbs(tones)
    cell = s / n
    for bi in range(n):
        for bj in range(n):
            x0, y0 = bi * cell, bj * cell
            inner = 0
            if border:
                bc = vary(a.rng, rgb(border), 0.03)
                a.shape(rect(x0 + 0.8, y0 + 0.8, x0 + cell - 0.8, y0 + cell - 0.8), bc, **J(bc), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.03)
                inner = cell * 0.12
            horizontal = (bi + bj) % 2 == 0
            span = cell - 2 * inner
            for k in range(strips):
                if horizontal:
                    x, y, w, hh = x0 + inner, y0 + inner + k * span / strips, span, span / strips
                else:
                    x, y, w, hh = x0 + inner + k * span / strips, y0 + inner, span / strips, span
                c = vary(a.rng, a.rng.choice(tones), 0.04)
                a.shape(rect(x + 0.8, y + 0.8, x + w - 0.8, y + hh - 0.8), c, **J(c), corner=1.5, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, mottle=0.03)
    return a.image()


def ship_deck(seed, tones=("#b98f60", "#ab8156", "#c49a6a"), caulk="#1e1712"):
    return wood_floor(seed, tones, gap=caulk, rows=12, nails=False, bolts=True, lo=0.45, hi=0.95, gap_w=2.2)


def boardwalk(seed, tones=("#9a7652", "#8c6a48", "#a8825c"), under="#22303a"):
    """Wide boards with open gaps showing dark water/ground beneath."""
    return wood_floor(seed, tones, gap=under, rows=6, vertical=True, lo=0.5, hi=1.0, gap_w=5.5)


def log_floor(seed, tones=("#8a6440", "#7a5838", "#94704a")):
    """Split logs laid side by side: rounded ends, bark edges."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap("#2a1d14", tones))
    tones = rgbs(tones)
    rows = 8
    h = s / rows
    for r in range(rows):
        y = r * h
        x = a.rng.uniform(0, s)
        for ln in split(s, a.rng, s * 0.45, s * 0.9):
            c = vary(a.rng, a.rng.choice(tones), 0.05)

            def detail(art, path, x=x, y=y, ln=ln, c=c):
                plank_grain(art, x, y, ln, h, c, knots=0.6)
                art.ink([(x + 6, y + 5), (x + ln - 6, y + 5)], DETAIL, color=shade(c, 0.5), alpha=0.6, wob=0.6)

            a.shape(rect(x + 1.2, y + 1.2, x + ln - 1.2, y + h - 1.2), c, **J(c, 1.3), corner=h * 0.45, wob=0.8, depth=4, shade_k=0.45, light_k=0.3, ao=0.18, mottle=0.06, detail=detail)
            x += ln
    return a.image()


# ---------------------------------------------------------------------------------------------------
# Stone
# ---------------------------------------------------------------------------------------------------


def flagstones2(seed, base, alt, mortar, n=5, cracks=0.4, moss=0.0, missing=0.0, rounded=10, jitter=0.3, earth="#6e5a44"):
    """Irregular flagstones with optional moss and missing stones (dirt)."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(mortar, [base, *alt]))
    base = rgb(base)
    moss_c = rgb("#6f8a45")
    for (cx, cy), poly in voronoi_cells(s, s, n, n, a.rng, jitter):
        p = inset(poly, 2.0)
        if a.rng.random() < missing:
            a.shape(chaikin(p, True, 2), rgb(earth), **J(rgb(earth), 1.2), corner=0, wob=0.8, depth=6, shade_k=0.0, light_k=0.0, ao=0.6, mottle=0.1, detail=lambda art, path: speckles(art, path, shade(rgb(earth), 0.4), 30, (0.8, 2.0)))
            continue
        c = vary(a.rng, mix(base, rgb(alt[0]) if a.rng.random() < 0.5 else rgb(alt[1]), a.rng.uniform(0.2, 0.7)), 0.03)

        def detail(art, path, cx=cx, cy=cy, c=c):
            speckles(art, path, shade(c, 0.4), 16)
            if art.rng.random() < cracks:
                crack(art, cx + art.rng.uniform(-20, 20), cy + art.rng.uniform(-20, 20), art.rng.uniform(0, 6.28), art.rng.uniform(30, 55))
            if moss > 0 and art.rng.random() < moss:
                b = path.getBounds()
                for _ in range(4):
                    mx = art.rng.uniform(b.left(), b.right())
                    my = art.rng.choice((b.top(), b.bottom())) + art.rng.uniform(-6, 6)
                    art.fill_path(to_path(blob(mx, my, art.rng.uniform(18, 32), art.rng, 10, 0.4)), vary(art.rng, moss_c, 0.08), 0.85)
                    for _ in range(5):
                        dot(art, mx + art.rng.uniform(-14, 14), my + art.rng.uniform(-10, 10), 2, shade(moss_c, 0.4), 0.7)

        a.shape(p, c, **J(c, 1.2), corner=min(rounded, 8), wob=0.8, depth=5, shade_k=0.45, light_k=0.3, ao=0.18, detail=detail)
    return a.image()


def ashlar2(seed, base, mortar, rows=6, cracks=0.3, moss=0.0, lo=1.1, hi=1.9):
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(mortar, base))
    h = s / rows
    moss_c = rgb("#6f8a45")
    for r in range(rows):
        x = a.rng.uniform(0, s)
        for w in split(s, a.rng, h * lo, h * hi):
            c = vary(a.rng, mix(rgb(base[0]), rgb(base[1]), a.rng.random()), 0.03)

            def detail(art, path, x=x, w=w, r=r, c=c):
                speckles(art, path, shade(c, 0.45), 12)
                if art.rng.random() < cracks:
                    crack(art, x + w * art.rng.uniform(0.2, 0.8), r * h + h * 0.5, art.rng.uniform(0, 6.28), 30)
                if moss and art.rng.random() < moss:
                    art.fill_path(to_path(blob(x + art.rng.uniform(0, w), r * h + art.rng.choice((4, h - 4)), art.rng.uniform(16, 28), art.rng, 9, 0.4)), vary(art.rng, moss_c, 0.08), 0.85)

            a.shape(rect(x + 1.5, r * h + 1.5, x + w - 1.5, r * h + h - 1.5), c, **J(c, 1.2), corner=4, wob=0.8, depth=5, shade_k=0.45, light_k=0.3, ao=0.18, detail=detail)
            x += w
    return a.image()


def square_stones(seed, base, mortar, n=4, grid_jitter=6, cracks=0.4):
    """Large square slabs on a grid (paving / temple floors)."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(mortar, base))
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = vary(a.rng, mix(rgb(base[0]), rgb(base[1]), a.rng.random()), 0.03)
            pts = [(px + a.rng.uniform(-grid_jitter, grid_jitter) * 0.3, py + a.rng.uniform(-grid_jitter, grid_jitter) * 0.3) for px, py in rect(x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2)]

            def detail(art, path, x0=x0, y0=y0, c=c):
                speckles(art, path, shade(c, 0.45), 20)
                if art.rng.random() < cracks:
                    crack(art, x0 + cell * art.rng.uniform(0.3, 0.7), y0 + cell * art.rng.uniform(0.3, 0.7), art.rng.uniform(0, 6.28), cell * 0.4)

            a.shape(pts, c, **J(c, 1.2), corner=4, wob=0.7, depth=5, shade_k=0.45, light_k=0.3, ao=0.18, detail=detail)
    return a.image()


def river_stones(seed, cols, mortar="#6b6252", n=12):
    """Rounded river pebbles packed tight in mortar."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(mortar, cols))
    cols = rgbs(cols)
    for (cx, cy), poly in voronoi_cells(s, s, n, n, a.rng, 0.45):
        p = chaikin(chaikin(inset(poly, 3), True, 2), True, 1)
        c = vary(a.rng, a.rng.choice(cols), 0.06)
        a.shape(p, c, **J(c, 1.2), corner=0, wob=0.4, depth=4, shade_k=0.45, light_k=0.45, ao=0.15)
    return a.image()


def lava_rock(seed):
    """Dark basalt slabs with glowing cracks between them."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb("#ff8a2a"))
    glow_c = rgb("#ffcf5a")
    for (cx, cy), poly in voronoi_cells(s, s, 5, 5, a.rng, 0.4):
        p = inset(poly, 5)
        a.stroke_path(to_path(p), glow_c, 7, 0.6, blur=4)
        c = vary(a.rng, mix(rgb("#3a3330"), rgb("#2c2725"), a.rng.random()), 0.04)

        def detail(art, path, cx=cx, cy=cy, c=c):
            speckles(art, path, tint(c, 0.25), 30, (0.8, 1.8))
            if art.rng.random() < 0.5:
                crack(art, cx, cy, art.rng.uniform(0, 6.28), 40, FINE * 1.4, 0.9)

        a.shape(p, c, outline=3.6, corner=14, wob=1.6, depth=8, shade_k=0.5, light_k=0.25, ao=0.3, mottle=0.08, detail=detail)
    return a.image()


# ---------------------------------------------------------------------------------------------------
# Tiles
# ---------------------------------------------------------------------------------------------------


def hex_tiles(seed, cols, grout, cols_n=6):
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, cols))
    cols = rgbs(cols)
    w = s / cols_n
    r = w / math.sqrt(3)
    rows = round(s / (1.5 * r))
    if rows % 2:
        rows += 1
    r = s / rows / 1.5
    for j in range(rows):
        for i in range(cols_n):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * 1.5 * r
            rr = min(r, w / math.sqrt(3)) - 1.5
            pts = [(cx + rr * math.cos(math.pi / 6 + k * math.pi / 3), cy + rr * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
            pts = [(cx + (x - cx) * 1.0, cy + (y - cy) * 1.0) for x, y in pts]
            c = vary(a.rng, a.rng.choice(cols), 0.04)
            a.shape(pts, c, **J(c), corner=2, wob=0.3, depth=3, shade_k=0.4, light_k=0.3, ao=0.12)
    return a.image()


def octagon_dot(seed, oct_c, dot_c, grout, n=4):
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, [oct_c]))
    cell = s / n
    k = cell * 0.29
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            pts = [(x0 + k, y0 + 3), (x0 + cell - k, y0 + 3), (x0 + cell - 3, y0 + k), (x0 + cell - 3, y0 + cell - k), (x0 + cell - k, y0 + cell - 3), (x0 + k, y0 + cell - 3), (x0 + 3, y0 + cell - k), (x0 + 3, y0 + k)]
            oc = vary(a.rng, rgb(oct_c), 0.04)
            a.shape(pts, oc, **J(oc), corner=2, wob=0.3, depth=3, shade_k=0.4, light_k=0.3, ao=0.12)
            d = k * 0.95
            sq = [(x0, y0 - d + 3), (x0 + d - 3, y0), (x0, y0 + d - 3), (x0 - d + 3, y0)]
            dc = vary(a.rng, rgb(dot_c), 0.04)
            a.shape(sq, dc, **J(dc), corner=1.5, wob=0.3, depth=2, shade_k=0.35, light_k=0.25, ao=0.08)
    return a.image()


def glazed_tiles(seed, cols, grout, n=8):
    """Glossy tiles: each with a white glint at its top-left and a slight
    color variation between tiles."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, cols))
    cols = rgbs(cols)
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = vary(a.rng, a.rng.choice(cols), 0.05)

            def glint(art, path, x0=x0, y0=y0):
                art.ink([(x0 + 10, y0 + cell * 0.45), (x0 + 10, y0 + 10), (x0 + cell * 0.45, y0 + 10)], FINE * 1.4, color=(250, 250, 245), alpha=0.7, wob=0.1)

            a.shape(rect(x0 + 1.8, y0 + 1.8, x0 + cell - 1.8, y0 + cell - 1.8), c, **J(c), corner=4, wob=0.3, depth=4, shade_k=0.4, light_k=0.4, ao=0.12, mottle=0.02, detail=glint)
    return a.image()


def mosaic2(seed, cols, grout, n=16, motif="ring"):
    """Small-tile mosaics with a repeating motif every 8 cells."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, cols))
    cols = rgbs(cols)
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            u, v = (i % 8) - 3.5, (j % 8) - 3.5
            if motif == "ring":
                d = math.hypot(u, v)
            elif motif == "cross":
                d = min(abs(u), abs(v)) * 2
            elif motif == "stripes":
                d = (i + j) % 8 / 2
            else:
                d = max(abs(u), abs(v))
            idx = int(d) % len(cols)
            c = vary(a.rng, cols[idx], 0.06)
            a.shape(rect(x0 + 1.4, y0 + 1.4, x0 + cell - 1.4, y0 + cell - 1.4), c, **J(c, 0.9), corner=1.5, wob=0.3, depth=2, shade_k=0.35, light_k=0.25, ao=0.08, mottle=0)
    return a.image()


def random_mosaic(seed, cols, grout, n=8):
    """Irregular stone mosaic (opus incertum): small voronoi pieces."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, cols))
    cols = rgbs(cols)
    for (cx, cy), poly in voronoi_cells(s, s, n * 2, n * 2, a.rng, 0.4):
        p = inset(poly, 1.4)
        c = vary(a.rng, a.rng.choice(cols), 0.05)
        a.shape(p, c, **J(c, 0.9), corner=2, wob=0.3, depth=2, shade_k=0.35, light_k=0.3, ao=0.08, mottle=0)
    return a.image()


def cathedral_marble(seed, light="#e6e0d4", dark="#5a4e48", accent="#a8483a", grout="#2c2a2f"):
    """Large marble squares with a smaller rotated inlay square in each."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, [light, dark]))
    n = 2
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = rgb(light) if (i + j) % 2 == 0 else rgb(dark)

            def veins(art, path, x0=x0, y0=y0, c=c):
                vc = shade(c, 0.3) if sum(c) > 400 else tint(c, 0.3)
                for _ in range(3):
                    x, y = x0 + art.rng.uniform(0, cell), y0
                    pts = [(x, y)]
                    for _ in range(8):
                        x += art.rng.uniform(-18, 18)
                        y += cell / 8
                        pts.append((x, y))
                    art.ink(chaikin(pts, False, 2), FINE * 0.8, color=vc, alpha=0.6, wob=0.4)

            a.shape(rect(x0 + 1.5, y0 + 1.5, x0 + cell - 1.5, y0 + cell - 1.5), c, **J(c), corner=2, wob=0.3, depth=4, shade_k=0.35, light_k=0.3, ao=0.12, detail=veins)
            mx, my = x0 + cell / 2, y0 + cell / 2
            r = cell * 0.28
            ic = rgb(dark) if (i + j) % 2 == 0 else rgb(light)
            a.shape([(mx, my - r), (mx + r, my), (mx, my + r), (mx - r, my)], ic, **J(ic), corner=2, wob=0.3, depth=3, shade_k=0.35, light_k=0.3, ao=0.1)
            r2 = r * 0.4
            a.shape([(mx, my - r2), (mx + r2, my), (mx, my + r2), (mx - r2, my)], rgb(accent), **J(rgb(accent)), corner=1.5, wob=0.3, depth=2, shade_k=0.3, light_k=0.3, ao=0.1, mottle=0)
    return a.image()


def inlaid_tiles(seed, base, inlay, grout, n=4):
    """Square tiles with a small contrasting square set at every corner."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, [base]))
    cell = s / n
    k = cell * 0.2
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            pts = [(x0 + k, y0 + 3), (x0 + cell - k, y0 + 3), (x0 + cell - k, y0 + k), (x0 + cell - 3, y0 + k), (x0 + cell - 3, y0 + cell - k), (x0 + cell - k, y0 + cell - k), (x0 + cell - k, y0 + cell - 3), (x0 + k, y0 + cell - 3), (x0 + k, y0 + cell - k), (x0 + 3, y0 + cell - k), (x0 + 3, y0 + k), (x0 + k, y0 + k)]
            bc = vary(a.rng, rgb(base), 0.04)
            a.shape(pts, bc, **J(bc), corner=2, wob=0.3, depth=3, shade_k=0.4, light_k=0.3, ao=0.12)
            ic = vary(a.rng, rgb(inlay), 0.04)
            a.shape(rect(x0 - k + 3, y0 - k + 3, x0 + k - 3, y0 + k - 3), ic, **J(ic), corner=2, wob=0.3, depth=2, shade_k=0.35, light_k=0.25, ao=0.08)
    return a.image()


def gold_temple(seed):
    """Gilded square slabs, each engraved with a sun disc, set in dark stone."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb("#3a2f22"))
    gold = rgb("#d6ae4c")
    n = 4
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = vary(a.rng, gold if (i + j) % 2 == 0 else rgb("#c49a3e"), 0.03)
            mx, my = x0 + cell / 2, y0 + cell / 2

            def engrave(art, path, mx=mx, my=my, c=c):
                art.ink(ellipse(mx, my, cell * 0.22, cell * 0.22, 40), FINE * 1.3, closed=True, color=shade(c, 0.45), alpha=0.85, wob=0.2)
                for k in range(8):
                    t = math.pi * k / 4
                    art.ink([(mx + cell * 0.27 * math.cos(t), my + cell * 0.27 * math.sin(t)), (mx + cell * 0.38 * math.cos(t), my + cell * 0.38 * math.sin(t))], FINE * 1.2, color=shade(c, 0.45), alpha=0.8, wob=0.2)
                art.ink([(x0 + 10, y0 + cell * 0.4), (x0 + 10, y0 + 10), (x0 + cell * 0.4, y0 + 10)], FINE * 1.3, color=tint(c, 0.6), alpha=0.7, wob=0.1)

            a.shape(rect(x0 + 4, y0 + 4, x0 + cell - 4, y0 + cell - 4), c, outline=3.0, corner=4, wob=0.4, depth=6, shade_k=0.5, light_k=0.5, ao=0.2, mottle=0.05, detail=engrave)
    return a.image()


# ---------------------------------------------------------------------------------------------------
# Carpets
# ---------------------------------------------------------------------------------------------------


def striped_carpet(seed, cols, n=8):
    s = S2
    cols = rgbs(cols)
    a = Art(s, s, seed, tile=True, bg=cols[0])
    w = s / n
    for k in range(n):
        c = cols[k % len(cols)]
        a.fill_path(to_path(rect(-4, k * w, s + 4, (k + 1) * w)), c)
        a.ink([(-10, k * w), (s + 10, k * w)], 1.6, color=INK, alpha=0.8, taper=False, wob=0.0, var=0.0)
        for x in range(0, s, 16):
            a.ink([(x, k * w + w * 0.5 - 4), (x + 6, k * w + w * 0.5), (x, k * w + w * 0.5 + 4)], FINE * 0.8, color=shade(c, 0.35), alpha=0.5, wob=0.1)
    for y in range(0, s, 6):
        a.ink([(0, y), (s, y)], 0.8, color=shade(cols[0], 0.5), alpha=0.12, taper=False, wob=0.1)
    return a.image()


def medallion_carpet(seed, base, ring, center, n=2):
    """Repeating round medallions on a plain field, with a small motif
    between them."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb(base))
    step = s / n
    for i in range(n + 1):
        for j in range(n + 1):
            cx, cy = i * step, j * step
            for r, col in ((step * 0.36, rgb(ring)), (step * 0.27, rgb(base)), (step * 0.2, rgb(center)), (step * 0.08, rgb(ring))):
                a.shape(ellipse(cx, cy, r, r, 48), col, outline=2.2, corner=0, wob=0.3, depth=2, shade_k=0.25, light_k=0.15, ao=0.05, mottle=0.03)
            ox, oy = cx + step / 2, cy + step / 2
            r = step * 0.08
            a.shape([(ox, oy - r), (ox + r, oy), (ox, oy + r), (ox - r, oy)], rgb(center), outline=1.8, corner=1, wob=0.2, depth=2, shade_k=0.2, light_k=0.1, ao=0, mottle=0)
    for k in range(0, s, 6):
        a.ink([(k, 0), (k, s)], 0.8, color=shade(rgb(base), 0.5), alpha=0.15, taper=False, wob=0.1)
    return a.image()


def checker_carpet(seed, c1, c2, n=8):
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb(c1))
    cell = s / n
    for i in range(n):
        for j in range(n):
            if (i + j) % 2:
                a.shape(rect(i * cell, j * cell, (i + 1) * cell, (j + 1) * cell), rgb(c2), outline=1.4, corner=0, wob=0.3, depth=1.5, shade_k=0.2, light_k=0.1, ao=0, mottle=0.03)
    for k in range(0, s, 6):
        a.ink([(k, 0), (k, s)], 0.8, color=shade(rgb(c1), 0.5), alpha=0.15, taper=False, wob=0.1)
    return a.image()


# ---------------------------------------------------------------------------------------------------
# Loose floors
# ---------------------------------------------------------------------------------------------------


def loose_floor(seed, base, blotch, pebble=None, dots=500, cracks=6, strokes=0, stroke_cols=None, ripples=0):
    s = S2
    base = rgb(base)
    a = Art(s, s, seed, tile=True, bg=base)
    for _ in range(36):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.fill_path(to_path(blob(x, y, a.rng.uniform(20, 55), a.rng, 12, 0.3)), rgb(a.rng.choice(blotch)), 0.22, blur=6)
    for r in range(ripples):
        y = r * s / ripples + a.rng.uniform(-6, 6)
        pts = [(x, y + 5 * math.sin(2 * math.pi * x / s * 3 + r)) for x in range(-20, s + 21, 16)]
        a.ink(pts, FINE * 1.2, color=shade(base, 0.35), alpha=0.6, wob=0.3)
    if pebble:
        for _ in range(60):
            x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
            a.shape(blob(x, y, a.rng.uniform(3, 7), a.rng, 8, 0.25), vary(a.rng, rgb(pebble), 0.08), outline=1.4, corner=0, wob=0.2, depth=1.5, shade_k=0.4, light_k=0.4, ao=0, mottle=0)
    for _ in range(strokes):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        L = a.rng.uniform(10, 22)
        a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], FINE * 1.3, color=rgb(a.rng.choice(stroke_cols)), alpha=0.9, wob=0.15, var=0.1)
    for _ in range(dots):
        dot(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0.6, 1.4), shade(base, 0.45), 0.5)
    for _ in range(cracks):
        crack(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0, 6.28), a.rng.uniform(30, 60), FINE * 0.9, 0.5)
    return a.image()


# ---------------------------------------------------------------------------------------------------
# Metal & fantasy
# ---------------------------------------------------------------------------------------------------


def metal_plates(seed, base=("#7d838c", "#6f757e"), seam="#2a2c30", n=4, rivets=True, rust=0.0):
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb(seam))
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = vary(a.rng, mix(rgb(base[0]), rgb(base[1]), a.rng.random()), 0.03)

            def detail(art, path, x0=x0, y0=y0, c=c):
                for _ in range(6):
                    sx, sy = x0 + art.rng.uniform(10, cell - 10), y0 + art.rng.uniform(10, cell - 10)
                    art.ink([(sx, sy), (sx + art.rng.uniform(8, 20), sy + art.rng.uniform(-3, 3))], FINE * 0.7, color=tint(c, 0.4), alpha=0.5, wob=0.1)
                if rust and art.rng.random() < rust:
                    art.fill_path(to_path(blob(x0 + art.rng.uniform(20, cell - 20), y0 + art.rng.uniform(20, cell - 20), art.rng.uniform(14, 30), art.rng, 10, 0.4)), rgb("#8a4a2a"), 0.55)

            a.shape(rect(x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2), c, outline=2.6, corner=3, wob=0.2, depth=4, shade_k=0.45, light_k=0.45, ao=0.2, mottle=0.04, detail=detail)
            if rivets:
                for px, py in ((x0 + 12, y0 + 12), (x0 + cell - 12, y0 + 12), (x0 + 12, y0 + cell - 12), (x0 + cell - 12, y0 + cell - 12)):
                    dot(a, px, py, 3.6, shade(c, 0.4), 0.95)
                    dot(a, px - 1, py - 1, 1.4, tint(c, 0.6), 0.9)
    return a.image()


def tread_plate(seed, base="#8a9098"):
    """Metal floor with raised diamond tread bars."""
    s = S2
    base = rgb(base)
    a = Art(s, s, seed, tile=True, bg=base)
    step = s / 16
    for i in range(16):
        for j in range(16):
            cx, cy = (i + 0.5) * step, (j + 0.5) * step
            ang = math.pi / 4 if (i + j) % 2 == 0 else -math.pi / 4
            dx, dy = math.cos(ang) * step * 0.32, math.sin(ang) * step * 0.32
            a.ink([(cx - dx, cy - dy), (cx + dx, cy + dy)], 7, color=shade(base, 0.4), alpha=0.9, wob=0.05, var=0.05)
            a.ink([(cx - dx, cy - dy - 1.5), (cx + dx, cy + dy - 1.5)], 3, color=tint(base, 0.35), alpha=0.8, wob=0.05, var=0.05)
    return a.image()


def iron_grate(seed, bar="#5a5c62", under="#141210", n=8):
    """A grate of crossing iron bars over a dark pit."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb(under))
    cell = s / n
    for k in range(n):
        x = k * cell
        a.shape(rect(x - 7, -20, x + 7, s + 20), vary(a.rng, rgb(bar), 0.03), outline=2.4, corner=2, wob=0.2, depth=3, shade_k=0.45, light_k=0.5, ao=0.1, mottle=0)
    for k in range(n):
        y = k * cell
        a.shape(rect(-20, y - 7, s + 20, y + 7), vary(a.rng, rgb(bar), 0.03), outline=2.4, corner=2, wob=0.2, depth=3, shade_k=0.45, light_k=0.5, ao=0.1, mottle=0)
        for j in range(n):
            dot(a, j * cell, y, 5, shade(rgb(bar), 0.3), 0.95)
    return a.image()


def ice_floor(seed, base=("#cfe6ee", "#b9d8e4"), grout="#7fa6b8"):
    s = S2
    a = Art(s, s, seed, tile=True, bg=soft_gap(grout, base))
    for (cx, cy), poly in voronoi_cells(s, s, 4, 4, a.rng, 0.45):
        p = inset(poly, 1.8)
        c = vary(a.rng, mix(rgb(base[0]), rgb(base[1]), a.rng.random()), 0.03)

        def detail(art, path, cx=cx, cy=cy, c=c):
            for _ in range(3):
                crack(art, cx + art.rng.uniform(-40, 40), cy + art.rng.uniform(-40, 40), art.rng.uniform(0, 6.28), art.rng.uniform(40, 80), FINE, 0.45)
            for _ in range(2):
                x, y = cx + art.rng.uniform(-50, 50), cy + art.rng.uniform(-50, 50)
                art.ink([(x, y), (x + 30, y - 12)], FINE * 1.6, color=(250, 252, 255), alpha=0.75, wob=0.1)

        a.shape(p, c, **J(c, 1.2), corner=5, wob=0.5, depth=6, shade_k=0.3, light_k=0.5, ao=0.15, mottle=0.06, detail=detail)
    return a.image()


def crystal_floor(seed, base="#8a6ad8", grout="#2a2240"):
    """Faceted crystal slabs: each cell split into lit and shaded facets."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb(grout))
    base = rgb(base)
    for (cx, cy), poly in voronoi_cells(s, s, 5, 5, a.rng, 0.4):
        p = inset(poly, 3)
        n = len(p)
        for k in range(n):
            face = [p[k], p[(k + 1) % n], (cx, cy)]
            mx = (p[k][0] + p[(k + 1) % n][0]) / 2 - cx
            my = (p[k][1] + p[(k + 1) % n][1]) / 2 - cy
            lit = -(mx + my) / (math.hypot(mx, my) * 1.414 + 1e-6)
            col = tint(base, 0.35 * lit) if lit > 0 else shade(base, -0.3 * lit)
            a.shape(face, col, outline=0, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        for k in range(n):
            a.ink([p[k], (cx, cy)], FINE, color=shade(base, 0.5), alpha=0.6, wob=0)
        a.ink(p, DETAIL * 1.1, closed=True, wob=0.2)
    return a.image()


def bone_floor(seed):
    """Bones and skulls packed in pale earth (ossuary floor)."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb("#8a7d68"))
    bone = rgb("#e6dcc4")
    for _ in range(110):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        L = a.rng.uniform(70, 120)
        ux, uy = math.cos(t), math.sin(t)
        x0, y0, x1, y1 = x - ux * L / 2, y - uy * L / 2, x + ux * L / 2, y + uy * L / 2
        c = vary(a.rng, bone, 0.05)
        for ex, ey in ((x0, y0), (x1, y1)):
            for k in (-1, 1):
                a.shape(ellipse(ex - uy * k * 7, ey + ux * k * 7, 9, 9, 16), c, outline=2.2, corner=0, wob=0.1, depth=1.5, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
        a.shape([(x0 - uy * 6, y0 + ux * 6), (x1 - uy * 6, y1 + ux * 6), (x1 + uy * 6, y1 - ux * 6), (x0 + uy * 6, y0 - ux * 6)], c, outline=2.2, corner=1, wob=0.1, depth=1.5, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    for _ in range(10):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        x, y = x, y
        a.shape(chaikin([(x - 24, y - 6), (x - 18, y - 27), (x + 18, y - 27), (x + 24, y - 6), (x + 16, y + 18), (x - 16, y + 18)], True, 2), bone, outline=2.6, corner=0, wob=0.1, depth=2, shade_k=0.35, light_k=0.3, ao=0, mottle=0)
        for dx in (-9, 9):
            dot(a, x + dx, y - 3, 6, rgb("#2a221e"))
    return a.image()


def roots_floor(seed):
    """Packed earth threaded with gnarled roots."""
    s = S2
    base = rgb("#6e5a44")
    a = Art(s, s, seed, tile=True, bg=base)
    for _ in range(30):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.fill_path(to_path(blob(x, y, a.rng.uniform(20, 50), a.rng, 12, 0.3)), rgb(a.rng.choice(("#64503c", "#7a6650"))), 0.22, blur=6)
    for _ in range(9):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        pts = [(x, y)]
        for _ in range(8):
            t += a.rng.uniform(-0.5, 0.5)
            x += 22 * math.cos(t)
            y += 22 * math.sin(t)
            pts.append((x, y))
        a.ink(pts, 14, color=INK, taper=True, wob=0.4)
        a.ink(pts, 9, color=rgb("#8a6a4a"), taper=True, wob=0.4)
    for _ in range(400):
        dot(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0.6, 1.4), shade(base, 0.45), 0.5)
    return a.image()


# ---------------------------------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------------------------------

OAK = ("#b07d4f", "#a5724a", "#ba8a5a", "#9c6a42")
WALNUT = ("#6b4a33", "#5e412c", "#76533a")
MAPLE = ("#e0c49a", "#d8ba8c", "#e8cea6")
CHERRY = ("#a8583a", "#9a4f34", "#b36444")
PINE = ("#d4ad74", "#c99f68", "#ddb882")
ASH = ("#cbbfa6", "#c0b399", "#d6cbb3")
MAHOGANY = ("#7e3a2a", "#713326", "#8a4430")
EBONY = ("#3a2e2a", "#322824", "#44362f")
GREY_WOOD = ("#9c958a", "#8f887e", "#a8a196")
TEAK = ("#a87a44", "#9c6f3c", "#b4864e")

FLOORS2 = {
    # Wood: species
    "Walnut Planks": lambda: wood_floor(2001, WALNUT, gap="#21160f"),
    "Maple Planks": lambda: wood_floor(2002, MAPLE, gap="#6a5238"),
    "Cherry Planks": lambda: wood_floor(2003, CHERRY, gap="#2e140d"),
    "Pine Planks": lambda: wood_floor(2004, PINE, gap="#5a4128", rows=6),
    "Ash Planks": lambda: wood_floor(2005, ASH, gap="#5a5245"),
    "Mahogany Planks": lambda: wood_floor(2006, MAHOGANY, gap="#1e0c08"),
    "Ebony Planks": lambda: wood_floor(2007, EBONY, gap="#100c0a"),
    "Grey Weathered Planks": lambda: wood_floor(2008, GREY_WOOD, gap="#3a3630", wear=1.0),
    "Teak Planks": lambda: wood_floor(2009, TEAK, gap="#2e1e10"),
    "Wide Oak Boards": lambda: wood_floor(2010, OAK, rows=5),
    "Narrow Walnut Strips": lambda: wood_floor(2011, WALNUT, gap="#21160f", rows=16, nails=False),
    "Vertical Oak Planks": lambda: wood_floor(2012, OAK, vertical=True),
    "Vertical Pine Planks": lambda: wood_floor(2013, PINE, gap="#5a4128", vertical=True, rows=7),
    "Worn Oak Planks": lambda: wood_floor(2014, OAK, wear=1.6),
    "Worn Dark Planks": lambda: wood_floor(2015, WALNUT, gap="#21160f", wear=1.6),
    # Wood: painted
    "Blue Painted Planks": lambda: wood_floor(2016, OAK, paint="#5f7fa0", wear=1.2),
    "Green Painted Planks": lambda: wood_floor(2017, OAK, paint="#6f8a5a", wear=1.2),
    "Red Painted Planks": lambda: wood_floor(2018, OAK, paint="#9a4a3a", wear=1.2),
    "White Painted Planks": lambda: wood_floor(2019, OAK, paint="#e6dfd0", wear=1.4),
    "Black Painted Planks": lambda: wood_floor(2020, OAK, paint="#3a3634", wear=1.0),
    # Wood: patterns
    "Herringbone Oak 45": lambda: herringbone45(2021, ("#b98a5a", "#a87a4c", "#c49866")),
    "Herringbone Walnut 45": lambda: herringbone45(2022, WALNUT, gap="#21160f"),
    "Herringbone Maple 45": lambda: herringbone45(2023, MAPLE, gap="#6a5238"),
    "Herringbone Grey 45": lambda: herringbone45(2024, GREY_WOOD, gap="#3a3630"),
    "Chevron Oak": lambda: chevron(2025, ("#b98a5a", "#a87a4c", "#c49866")),
    "Chevron Walnut": lambda: chevron(2026, WALNUT, gap="#21160f"),
    "Chevron Two-Tone": lambda: chevron(2027, ("#c79c6a", "#6b4a33"), gap="#2e1e10"),
    "Herringbone Cherry": lambda: herringbone(2028, CHERRY, gap="#2e140d"),
    "Herringbone Pine": lambda: herringbone(2029, PINE, gap="#5a4128"),
    "Basket Parquet Walnut": lambda: parquet(2030, WALNUT, gap="#21160f"),
    "Basket Parquet Maple": lambda: parquet(2031, MAPLE, gap="#6a5238"),
    "Framed Parquet": lambda: square_parquet(2032, ("#c79c6a", "#b98a5a"), border="#6b4a33"),
    "Framed Parquet Dark": lambda: square_parquet(2033, WALNUT, gap="#21160f", border="#c79c6a"),
    "Block Parquet": lambda: square_parquet(2034, ("#b98a5a", "#a87a4c", "#c79c6a"), n=6, strips=3),
    "Two-Tone Parquet": lambda: square_parquet(2035, ("#d8ba8c", "#7e5a3e"), n=4, strips=5),
    "Ship Deck": lambda: ship_deck(2036),
    "Pale Ship Deck": lambda: ship_deck(2037, ("#d6c4a0", "#cbb894", "#e0cfac")),
    "Boardwalk": lambda: boardwalk(2038),
    "Grey Boardwalk": lambda: boardwalk(2039, GREY_WOOD, under="#1e2a30"),
    "Split Log Floor": lambda: log_floor(2040),
    # Stone
    "Cream Flagstones": lambda: flagstones2(2041, "#ddd2bc", ("#e6dcc8", "#cdc0a6"), "#8f8470"),
    "Red Flagstones": lambda: flagstones2(2042, "#b2725a", ("#c08066", "#9e624c"), "#5e3a2e"),
    "Blue-Grey Flagstones": lambda: flagstones2(2043, "#8a96a2", ("#96a2ae", "#7c8894"), "#454d56"),
    "Green Slate Flagstones": lambda: flagstones2(2044, "#6e7e6a", ("#7a8a76", "#62705e"), "#363d34", n=6),
    "Mossy Flagstones": lambda: flagstones2(2045, "#a9a296", ("#b8ae9c", "#968f86"), "#5a5a44", moss=0.6),
    "Ruined Flagstones": lambda: flagstones2(2046, "#a39c90", ("#b2aa9c", "#8f887e"), "#5e574e", cracks=0.8, missing=0.18),
    "Broken Mossy Flagstones": lambda: flagstones2(2047, "#8f8a80", ("#9c968a", "#7f7a72"), "#4a4a38", cracks=0.7, moss=0.7, missing=0.15),
    "Small Flagstones": lambda: flagstones2(2048, "#a9a296", ("#b8ae9c", "#968f86"), "#6f685f", n=8, rounded=6),
    "Large Flagstones": lambda: flagstones2(2049, "#9c958a", ("#aaa296", "#8a847a"), "#5e574e", n=3, rounded=14),
    "Granite Ashlar": lambda: ashlar2(2050, ("#8f8b88", "#7f7b78"), "#3e3c3a"),
    "Limestone Ashlar": lambda: ashlar2(2051, ("#ddd4c0", "#cfc5b0"), "#8f8470", rows=5),
    "Basalt Ashlar": lambda: ashlar2(2052, ("#4e4b4a", "#444140"), "#1e1c1b"),
    "Mossy Ashlar": lambda: ashlar2(2053, ("#8a857d", "#7a756e"), "#3e4232", moss=0.5),
    "Long Ashlar": lambda: ashlar2(2054, ("#a8a090", "#968e80"), "#5a544a", rows=8, lo=1.6, hi=3.0),
    "Red Sandstone Ashlar": lambda: ashlar2(2055, ("#b8785a", "#a66a4e"), "#5e3a2e"),
    "Granite Slabs": lambda: square_stones(2056, ("#8f8b88", "#7f7b78"), "#3e3c3a"),
    "Limestone Slabs": lambda: square_stones(2057, ("#ddd4c0", "#cfc5b0"), "#8f8470", cracks=0.25),
    "Slate Slabs": lambda: square_stones(2058, ("#5f6670", "#535a63"), "#2a2e33", n=4),
    "Small Paving Stones": lambda: square_stones(2059, ("#a39c90", "#938c80"), "#5e574e", n=8, cracks=0.15),
    "Dark Cobblestone": lambda: cobbles(2060, ("#5e5a56", "#4e4a46", "#6a6662"), "#2a2826"),
    "Sandstone Cobbles": lambda: cobbles(2061, ("#cdb68e", "#bfa67e", "#d9c49c"), "#7a6648"),
    "Mixed Cobbles": lambda: cobbles(2062, ("#9a948a", "#b0907a", "#8a8f96", "#a8a296"), "#5e5850", n=11),
    "River Stones": lambda: river_stones(2063, ("#a8a49a", "#8f948f", "#b8ad9a", "#7f857f"), n=10),
    "Dark River Stones": lambda: river_stones(2064, ("#5e5a56", "#6e6862", "#4e4a46"), "#2a2826", n=9),
    "Warm River Stones": lambda: river_stones(2065, ("#c4a882", "#b0907a", "#d2bc9a", "#9a8470"), "#6e5a44", n=11),
    "Lava Rock": lambda: lava_rock(2066),
    # Tiles
    "Orange Terracotta": lambda: tiles(2067, "#d08050", "#dccdb0", 8),
    "Large Terracotta": lambda: tiles(2068, "#bf6b45", "#d6c6a8", 4),
    "Red Tile": lambda: tiles(2069, "#a8483a", "#d6c6a8", 8),
    "Black and White Checker": lambda: tiles(2070, "#ece6da", "#8a8378", 8, alt="#2a2a2e"),
    "Red and Cream Checker": lambda: tiles(2071, "#e6dcc8", "#8a8378", 8, alt="#a8483a"),
    "Blue and White Checker": lambda: tiles(2072, "#ece6da", "#8a8378", 8, alt="#4f6f9a"),
    "Green and Cream Checker": lambda: tiles(2073, "#e6dcc8", "#8a8378", 8, alt="#5f7f5a"),
    "Large Grey Checker": lambda: tiles(2074, "#bdb8b0", "#6a665f", 4, alt="#6e6a64"),
    "Terracotta Hexagons": lambda: hex_tiles(2075, ("#c06a45", "#b05e3c", "#cc7650"), "#dccdb0"),
    "White Hexagons": lambda: hex_tiles(2076, ("#ece6da", "#e2dccf"), "#8a8378", 8),
    "Mixed Hexagons": lambda: hex_tiles(2077, ("#5f7fa0", "#e6dcc8", "#a8483a", "#d6ad55"), "#3a3634"),
    "Octagon and Dot": lambda: octagon_dot(2078, "#e6dfd0", "#2a2a2e", "#8a8378"),
    "Terracotta Octagons": lambda: octagon_dot(2079, "#c06a45", "#3e5a6a", "#dccdb0"),
    "Glazed Blue Tiles": lambda: glazed_tiles(2080, ("#4f74a8", "#5a80b4", "#46699a"), "#dcd6c8"),
    "Glazed Green Tiles": lambda: glazed_tiles(2081, ("#4f8a6a", "#5a9676", "#467c5e"), "#dcd6c8"),
    "Glazed Teal Tiles": lambda: glazed_tiles(2082, ("#3f8a8a", "#4a9696", "#367c7c"), "#e6dfd0", 6),
    "Glazed Mixed Tiles": lambda: glazed_tiles(2083, ("#4f74a8", "#d6ad55", "#e6dcc8", "#a8483a"), "#3a3634"),
    "Ring Mosaic": lambda: mosaic2(2084, ("#d6ad55", "#a8483a", "#e6dcc8", "#3c4a5a"), "#d8cdb6"),
    "Cross Mosaic": lambda: mosaic2(2085, ("#4f74a8", "#e6dcc8", "#4f74a8", "#d6ad55"), "#d8cdb6", motif="cross"),
    "Square Mosaic": lambda: mosaic2(2086, ("#6f9a5a", "#e6dcc8", "#a8483a", "#e6dcc8"), "#d8cdb6", motif="square"),
    "Striped Mosaic": lambda: mosaic2(2087, ("#3f8a8a", "#e6dcc8", "#d6ad55", "#e6dcc8"), "#d8cdb6", motif="stripes"),
    "Pebble Mosaic": lambda: random_mosaic(2088, ("#e6dcc8", "#b8ad9a", "#8f948f", "#a8483a"), "#5e5850"),
    "Roman Mosaic": lambda: random_mosaic(2089, ("#e6dcc8", "#d8cdb6", "#cdbfa2", "#a8483a", "#3c4a5a"), "#8a7d68", n=10),
    "Cathedral Marble": lambda: cathedral_marble(2090),
    "Green Cathedral Marble": lambda: cathedral_marble(2091, "#e6e0d4", "#3e5a4a", "#d6ad55"),
    "Inlaid Tiles": lambda: inlaid_tiles(2092, "#e6dfd0", "#3a3634", "#8a8378"),
    "Inlaid Terracotta": lambda: inlaid_tiles(2093, "#c06a45", "#e6dcc8", "#6e4a32"),
    "Gold Temple Floor": lambda: gold_temple(2094),
    "Red Brick Herringbone": lambda: herringbone(2095, ("#a8503b", "#94432f", "#b5604a"), gap="#c9b9a2"),
    "Yellow Brick Floor": lambda: brick_floor(2096, ("#d6b468", "#c8a45a", "#e0c076"), "#8a7a58"),
    "Grey Brick Floor": lambda: brick_floor(2097, ("#8f8b88", "#7f7b78", "#9c9894"), "#4e4a46"),
    # Carpets
    "Green Carpet": lambda: carpet_floor(2098, "#2f5a3e", "#3c6e4c", "#d6ad55", "#1e3a28"),
    "Purple Carpet": lambda: carpet_floor(2099, "#4e2f66", "#5e3c7a", "#d6ad55", "#33204a"),
    "Brown Carpet": lambda: carpet_floor(2100, "#6e4a32", "#7e5a3e", "#e6dcc8", "#4e3222"),
    "Striped Red Carpet": lambda: striped_carpet(2101, ("#8a2f2f", "#d6ad55", "#8a2f2f", "#5e1f22")),
    "Striped Blue Carpet": lambda: striped_carpet(2102, ("#2f4466", "#e6dcc8", "#2f4466", "#5f7fa0")),
    "Medallion Carpet": lambda: medallion_carpet(2103, "#7e2a2a", "#d6ad55", "#2f4466"),
    "Blue Medallion Carpet": lambda: medallion_carpet(2104, "#2f4466", "#d6ad55", "#7e2a2a"),
    "Checkered Carpet": lambda: checker_carpet(2105, "#8a2f2f", "#6e2424"),
    # Loose floors
    "Packed Earth": lambda: loose_floor(2106, "#8f7356", ("#86694c", "#9b8061"), pebble="#9d9183"),
    "Dark Earth": lambda: loose_floor(2107, "#5e4a38", ("#544232", "#6a5440"), pebble="#7a7064"),
    "Sand Floor": lambda: loose_floor(2108, "#dcc48f", ("#d2b882", "#e4ce9c"), dots=700, cracks=0, ripples=12),
    "Mud Floor": lambda: loose_floor(2109, "#5a4632", ("#4e3c2a", "#66503a", "#3e5a5a"), dots=300, cracks=2),
    "Hay Floor": lambda: loose_floor(2110, "#c9ae6c", ("#b89c5c", "#d8bf80"), dots=100, cracks=0, strokes=1200, stroke_cols=("#a88a48", "#e0c886", "#f2e0a0", "#8a6e36")),
    "Rushes Floor": lambda: loose_floor(2111, "#8a8a52", ("#7e7e48", "#96965c"), dots=100, cracks=0, strokes=900, stroke_cols=("#6e7a3e", "#a6a86a", "#c4b878")),
    "Ash Floor": lambda: loose_floor(2112, "#8a8682", ("#7e7a76", "#96928e"), pebble="#3a3634", dots=600),
    "Root-Laced Earth": lambda: roots_floor(2113),
    # Metal & fantasy
    "Iron Plates": lambda: metal_plates(2114),
    "Rusty Plates": lambda: metal_plates(2115, ("#7a6e66", "#6a5f58"), rust=0.7),
    "Brass Plates": lambda: metal_plates(2116, ("#c49a4a", "#b08a40"), "#3a2a16"),
    "Tread Plate": lambda: tread_plate(2117),
    "Iron Grate": lambda: iron_grate(2118),
    "Fine Iron Grate": lambda: iron_grate(2119, n=16),
    "Ice Floor": lambda: ice_floor(2120),
    "Deep Ice": lambda: ice_floor(2121, ("#9fc6d8", "#8ab8cc"), "#4a7a90"),
    "Amethyst Crystal Floor": lambda: crystal_floor(2122),
    "Emerald Crystal Floor": lambda: crystal_floor(2123, "#4fae7a", "#1a3a2a"),
    "Ruby Crystal Floor": lambda: crystal_floor(2124, "#c8443a", "#3a1416"),
    "Ossuary Floor": lambda: bone_floor(2125),
}
