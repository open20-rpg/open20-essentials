"""The built-in pack's objects, drawn top-down with the ink engine (pen.py).
256 px = 1 map tile; light from the top-left. Colorable parts are painted in
pure red (g == b): the editor recolors them with the object's color."""

import math

import skia

from kit import *  # noqa: F401,F403
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, vary


# -- furniture -----------------------------------------------------------------------------


def round_table(seed=1):
    s = 360
    a = Art(s, s, seed)
    m = s / 2

    def top(art, path):
        for x in range(int(m - 150), int(m + 151), 52):
            art.ink([(x, 20), (x, s - 20)], DETAIL * 0.8, color=shade(WOOD, 0.5), alpha=0.9, taper=False, wob=0.6)
        grain_lines(art, 30, 30, s - 30, s - 30, 7, shade(WOOD, 0.45), vertical=True, alpha=0.5)
        art.ink(ellipse(m, m, m - 30, m - 30, 72), DETAIL * 0.8, closed=True, color=shade(WOOD, 0.5), alpha=0.6, wob=0.6)

    a.shape(ellipse(m, m, m - 10, m - 10, 96), WOOD, detail=top, depth=14)
    return a.image()


def long_table(seed=2):
    w, h = 512, 240
    a = Art(w, h, seed)

    def top(art, path):
        for k in range(1, 4):
            y = 12 + k * (h - 24) / 4
            art.ink([(12, y), (w - 12, y)], DETAIL * 0.8, color=shade(WOOD, 0.5), alpha=0.9, taper=False, wob=0.6)
        grain_lines(art, 12, 12, w - 12, h - 12, 8, shade(WOOD, 0.45), alpha=0.5)

    a.shape(rect(10, 10, w - 10, h - 10), WOOD, corner=10, detail=top, depth=12)
    # Runner (colorable) down the middle, with tassels.
    y0, y1 = h * 0.36, h * 0.64
    a.shape(rect(w * 0.16, y0, w * 0.84, y1), RED, outline=DETAIL * 1.2, corner=3, depth=6, mottle=0.03)
    a.ink([(w * 0.18, y0 + 9), (w * 0.82, y0 + 9)], FINE, color=tint(RED, 0.5), alpha=0.9, taper=False)
    a.ink([(w * 0.18, y1 - 9), (w * 0.82, y1 - 9)], FINE, color=tint(RED, 0.5), alpha=0.9, taper=False)
    return a.image()


def chair(seed=3):
    s = 170
    a = Art(s, s, seed)
    # Legs peek out past the seat's corners.
    for x, y in ((34, 52), (s - 34, 52), (34, s - 22), (s - 34, s - 22)):
        a.shape(rect(x - 11, y - 11, x + 11, y + 11), WOOD_DARK, outline=DETAIL * 1.3, corner=4, depth=4, mottle=0)

    def seat(art, path):
        for x in (68, 102):
            art.ink([(x, 58), (x, s - 28)], DETAIL * 0.8, color=shade(WOOD, 0.5), alpha=0.85, taper=False)
        grain_lines(art, 40, 60, s - 40, s - 30, 3, shade(WOOD, 0.45), vertical=True, alpha=0.4)

    a.shape(rect(30, 48, s - 30, s - 26), WOOD, corner=9, detail=seat, depth=8)
    # Backrest: a curved rail on two posts, spindles down to the seat.
    for x in (62, 85, 108):
        a.shape(rect(x - 4, 26, x + 4, 52), WOOD_DARK, outline=DETAIL, corner=2, depth=2, mottle=0)
    rail = [(26, 30), (s / 2, 18), (s - 26, 30), (s - 26, 42), (s / 2, 32), (26, 42)]
    a.shape(chaikin(rail, True, 2), WOOD_DARK, outline=OUTLINE * 0.85, corner=0, depth=6)
    for x in (30, s - 30):
        a.shape(ellipse(x, 36, 12, 12, 28), WOOD_DARK, outline=DETAIL * 1.3, depth=4, mottle=0)
    return a.image()


def stool(seed=4):
    s = 130
    a = Art(s, s, seed)
    m = s / 2

    def top(art, path):
        art.ink(ellipse(m, m, m - 26, m - 26, 48), DETAIL * 0.8, closed=True, color=shade(WOOD, 0.5), alpha=0.7)
        grain_lines(art, 20, 20, s - 20, s - 20, 3, shade(WOOD, 0.45), vertical=True, alpha=0.5)

    a.shape(ellipse(m, m, m - 10, m - 10, 64), WOOD_LIGHT, detail=top, depth=9)
    return a.image()


def bench(seed=5):
    w, h = 512, 120
    a = Art(w, h, seed)

    def top(art, path):
        art.ink([(14, h / 2), (w - 14, h / 2)], DETAIL * 0.8, color=shade(WOOD, 0.5), alpha=0.9, taper=False)
        grain_lines(art, 14, 22, w - 14, h - 22, 4, shade(WOOD, 0.45), alpha=0.5)

    a.shape(rect(10, 20, w - 10, h - 20), WOOD, corner=8, detail=top, depth=8)
    return a.image()


def bed(seed=6):
    w, h = 300, 520
    a = Art(w, h, seed)
    a.shape(rect(8, 8, w - 8, h - 8), WOOD_DARK, corner=12, depth=10)
    linen = rgb("#ece4d3")
    a.shape(rect(24, 50, w - 24, h - 22), linen, outline=DETAIL * 1.3, corner=12, depth=8)
    # Headboard.
    a.shape(rect(8, 8, w - 8, 44), WOOD, corner=10, depth=7)
    # Pillow.
    def pillow(art, path):
        art.ink([(100, 92), (120, 86), (150, 90)], FINE, color=shade(linen, 0.35), alpha=0.8)
        art.ink([(180, 112), (200, 108)], FINE, color=shade(linen, 0.35), alpha=0.7)

    a.shape(rect(46, 62, w - 46, 142), rgb("#f5f0e5"), outline=DETAIL * 1.3, corner=26, depth=9, detail=pillow)

    # Blanket (colorable), folded back at the top.
    def folds(art, path):
        for y, x0, x1 in ((280, 50, 150), (360, 130, 260), (440, 60, 190)):
            art.ink([(x0, y), ((x0 + x1) / 2, y + 6), (x1, y - 2)], FINE * 1.2, color=shade(RED, 0.45), alpha=0.8)

    a.shape(rect(20, 180, w - 20, h - 18), RED, outline=DETAIL * 1.4, corner=12, depth=10, detail=folds)
    a.shape(rect(20, 180, w - 20, 222), tint(RED, 0.25), outline=DETAIL * 1.2, corner=6, depth=6)
    return a.image()


def chest(seed=7):
    w, h = 270, 180
    a = Art(w, h, seed)

    def lid(art, path):
        for k in (1, 2):
            y = 12 + k * (h - 24) / 3
            art.ink([(14, y), (w - 14, y)], DETAIL * 0.8, color=shade(WOOD, 0.5), alpha=0.9, taper=False)
        grain_lines(art, 14, 14, w - 14, h - 14, 5, shade(WOOD, 0.45), alpha=0.45)

    a.shape(rect(10, 12, w - 10, h - 12), WOOD, corner=10, detail=lid, depth=12)
    for x in (42, w - 42):
        a.shape(rect(x - 12, 12, x + 12, h - 12), IRON, outline=DETAIL * 1.3, corner=3, depth=6)
        for y in (26, h / 2, h - 26):
            dot(a, x, y, 3, tint(IRON, 0.45))
            dot(a, x - 1, y - 1, 1.4, tint(IRON, 0.8))
    a.shape(rect(w / 2 - 20, h / 2 - 16, w / 2 + 20, h / 2 + 22), BRASS, outline=DETAIL * 1.3, corner=6, depth=6)
    a.shape([(w / 2 - 4, h / 2), (w / 2 + 4, h / 2), (w / 2 + 3, h / 2 + 12), (w / 2 - 3, h / 2 + 12)], INK, outline=0, corner=2, shade_k=0, light_k=0, ao=0, mottle=0)
    return a.image()


def crate(seed=8):
    s = 230
    a = Art(s, s, seed)
    c = WOOD_LIGHT
    a.shape(rect(8, 8, s - 8, s - 8), c, corner=6, depth=10, detail=lambda art, p: grain_lines(art, 30, 30, s - 30, s - 30, 5, shade(c, 0.45), alpha=0.4))
    for k in (1, 2, 3):
        y = 34 + k * (s - 68) / 4
        a.ink([(34, y), (s - 34, y)], DETAIL * 0.8, color=shade(c, 0.5), alpha=0.85, taper=False)
    # Frame and brace.
    for x0, y0, x1, y1 in ((8, 8, s - 8, 36), (8, s - 36, s - 8, s - 8), (8, 36, 36, s - 36), (s - 36, 36, s - 8, s - 36)):
        a.shape(rect(x0, y0, x1, y1), WOOD, outline=DETAIL * 1.3, corner=3, depth=6)
    a.shape([(40, s - 50), (s - 62, 36), (s - 36, 36), (s - 36, 50), (62, s - 36), (36, s - 36)], WOOD, outline=DETAIL * 1.3, corner=3, depth=6)
    for x, y in ((22, 22), (s - 22, 22), (22, s - 22), (s - 22, s - 22)):
        dot(a, x, y, 3.4)
    a.ink(rect(8, 8, s - 8, s - 8), OUTLINE, closed=True, wob=0)
    return a.image()


def bookshelf(seed=10):
    w, h = 512, 150
    a = Art(w, h, seed)
    case = WOOD_DARK
    a.shape(rect(6, 8, w - 6, h - 8), case, corner=6, depth=8)
    # The shelf's back board, then books standing in rows between dividers.
    a.shape(rect(22, 20, w - 22, 42), shade(case, 0.15), outline=DETAIL, corner=2, depth=3, mottle=0, shade_k=0.2, light_k=0.0, ao=0.3)
    palette = ["#8a3f37", "#3c5a78", "#55743f", "#9a7a37", "#694a6e", "#a85e34", "#2f6461", "#7b5a3c"]
    pages = rgb("#ddcfae")
    bays = [(22, 170), (178, 334), (342, w - 22)]
    for x0, x1 in bays:
        x = x0 + 2
        while x < x1 - 10:
            bw = a.rng.uniform(13, 22)
            if x + bw > x1 - 2:
                break
            col = rgb(a.rng.choice(palette))
            top, bot = 40, 40 + a.rng.uniform(70, 92)
            if a.rng.random() < 0.12:
                x += a.rng.uniform(10, 18)  # a gap
                continue
            # Cover around a cream block of page edges (seen from above).
            a.shape(rect(x, top, x + bw, bot), col, outline=DETAIL * 0.9, corner=2, wob=0.3, depth=3, shade_k=0.3, light_k=0.2, ao=0, mottle=0)
            a.shape(rect(x + 5, top + 5, x + bw - 5, bot - 7), pages, outline=FINE, corner=1, wob=0.2, depth=2, shade_k=0.2, light_k=0, ao=0, mottle=0)
            x += bw + a.rng.uniform(0.5, 1.5)
        # A book lying flat on its side at the end of some bays.
    for x0, x1 in bays[1:]:
        a.shape(rect(x0 - 8, 16, x0, h - 14), case, outline=DETAIL * 1.2, corner=2, depth=3)
    lay_x = bays[2][1] - 60
    a.shape(rect(lay_x, h - 54, lay_x + 50, h - 22), rgb("#3c5a78"), outline=DETAIL * 0.9, corner=3, depth=3, mottle=0)
    a.shape(rect(lay_x + 4, h - 50, lay_x + 46, h - 30), pages, outline=FINE, corner=1, depth=2, mottle=0, shade_k=0.2, light_k=0)
    return a.image()


def rug(seed=11):
    w, h = 512, 768
    a = Art(w, h, seed)
    cream = rgb("#e6d29f")
    # Fringes first, under the rug.
    for x in range(30, w - 24, 13):
        a.ink([(x, 22), (x + a.rng.uniform(-2, 2), 4)], FINE * 1.2, color=shade(cream, 0.3), taper=True)
        a.ink([(x, h - 22), (x + a.rng.uniform(-2, 2), h - 4)], FINE * 1.2, color=shade(cream, 0.3), taper=True)

    def pattern(art, path):
        art.shape(rect(46, 46, w - 46, h - 46), cream, outline=DETAIL, corner=2, depth=3, mottle=0, shade_k=0.2, light_k=0)
        art.shape(rect(62, 62, w - 62, h - 62), RED, outline=DETAIL, corner=2, depth=3, mottle=0.03, shade_k=0.2, light_k=0)
        cx, cy = w / 2, h / 2
        art.shape([(cx, cy - 210), (cx + 140, cy), (cx, cy + 210), (cx - 140, cy)], cream, outline=DETAIL, corner=3, depth=4, mottle=0, shade_k=0.2, light_k=0)
        art.shape([(cx, cy - 140), (cx + 92, cy), (cx, cy + 140), (cx - 92, cy)], shade(RED, 0.2), outline=DETAIL, corner=3, depth=4, mottle=0, shade_k=0.2, light_k=0)
        art.shape([(cx, cy - 56), (cx + 38, cy), (cx, cy + 56), (cx - 38, cy)], cream, outline=DETAIL, corner=2, depth=3, mottle=0, shade_k=0.2, light_k=0)
        for x, y in ((108, 108), (w - 108, 108), (108, h - 108), (w - 108, h - 108)):
            art.shape([(x, y - 22), (x + 22, y), (x, y + 22), (x - 22, y)], cream, outline=DETAIL * 0.9, corner=2, depth=2, mottle=0, shade_k=0, light_k=0)

    a.shape(rect(20, 20, w - 20, h - 20), RED, corner=4, depth=8, detail=pattern, shade_k=0.3, light_k=0.15)
    return a.image()


# -- workshop & outdoors -------------------------------------------------------------------


def cauldron(seed=12):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    black = rgb("#45464c")
    for ang in (math.pi * 0.15, math.pi * 1.15):
        x, y = m + (m - 16) * math.cos(ang), m + (m - 16) * math.sin(ang)
        a.shape(ellipse(x, y, 14, 14, 32), black, outline=DETAIL * 1.3, depth=4)
    a.shape(ellipse(m, m, m - 20, m - 20, 96), black, depth=12)
    brew = rgb("#7cbf5a")

    def bubbles(art, path):
        for _ in range(9):
            ang, r = art.rng.uniform(0, 6.28), art.rng.uniform(0, m - 60)
            rr = art.rng.uniform(5, 12)
            art.shape(ellipse(m + r * math.cos(ang), m + r * math.sin(ang), rr, rr, 24), tint(brew, 0.35), outline=FINE * 1.2, depth=2, shade_k=0.2, light_k=0.5, ao=0, mottle=0)

    a.shape(ellipse(m, m, m - 40, m - 40, 96), brew, outline=DETAIL * 1.3, depth=10, shade_k=0.0, light_k=0.0, detail=bubbles)
    # Light on the rim.
    a.ink([(m - 70, m - 66), (m - 30, m - 92), (m + 10, m - 96)], FINE * 1.3, color=tint(black, 0.5), alpha=0.9)
    return a.image()


def anvil(seed=14):
    w, h = 320, 170
    a = Art(w, h, seed)
    a.shape(rect(96, 34, 250, h - 34), rgb("#6c4b33"), corner=6, depth=8)
    a.shape(ellipse(173, h / 2, 54, 54, 48), shade(rgb("#6c4b33"), 0.1), outline=DETAIL, depth=4, mottle=0)
    body = [(24, h / 2), (70, h / 2 - 30), (110, h / 2 - 36), (270, h / 2 - 40), (300, h / 2 - 30), (300, h / 2 + 30), (270, h / 2 + 40), (110, h / 2 + 36), (70, h / 2 + 30)]
    a.shape(body, IRON, corner=8, depth=10, light_k=0.5)
    a.ink([(120, h / 2 - 20), (270, h / 2 - 22)], FINE * 1.4, color=tint(IRON, 0.6), alpha=0.9)
    a.shape(rect(246, h / 2 - 9, 264, h / 2 + 9), shade(IRON, 0.4), outline=DETAIL * 0.9, corner=2, depth=2, mottle=0)
    return a.image()


def well(seed=15):
    s = 340
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, m - 12, m - 12, 96), shade(STONE, 0.15), depth=8)
    n = 14
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n + 0.02, 2 * math.pi * (i + 1) / n - 0.02
        r0, r1 = m - 62, m - 14
        pts = [(m + r1 * math.cos(a0 + (a1 - a0) * t), m + r1 * math.sin(a0 + (a1 - a0) * t)) for t in (0, 0.5, 1)]
        pts += [(m + r0 * math.cos(a1 - (a1 - a0) * t), m + r0 * math.sin(a1 - (a1 - a0) * t)) for t in (0, 0.5, 1)]
        a.shape(pts, vary(a.rng, STONE, 0.06), outline=DETAIL * 1.2, corner=6, depth=6)
    water = rgb("#3f6f86")

    def ripples(art, path):
        art.ink([(m - 50, m - 30), (m - 20, m - 40), (m + 10, m - 34)], FINE * 1.4, color=tint(water, 0.5), alpha=0.9)
        art.ink([(m + 10, m + 30), (m + 40, m + 22)], FINE * 1.2, color=tint(water, 0.4), alpha=0.8)

    a.shape(ellipse(m, m, m - 64, m - 64, 80), water, outline=DETAIL * 1.3, depth=14, shade_k=0.0, light_k=0.0, ao=0.6, detail=ripples)
    # Crossbeam with the rope drum.
    a.shape(rect(m - 12, 2, m + 12, s - 2), WOOD_DARK, outline=DETAIL * 1.3, corner=4, depth=5)
    a.shape(rect(m - 26, m - 30, m + 26, m + 30), WOOD, outline=DETAIL * 1.3, corner=10, depth=6)
    for y in range(int(m - 22), int(m + 23), 8):
        a.ink([(m - 22, y), (m + 22, y + 2)], FINE, color=rgb("#c9b087"), alpha=0.9, taper=False)
    return a.image()


def lobed(cx, cy, r0, lobes):
    """A star-shaped outline: the far edge of a base circle and some lobe circles
    (cx, cy, r) as seen from the center, sampled around."""
    out = []
    n = 220
    for i in range(n):
        ang = 2 * math.pi * i / n
        ux, uy = math.cos(ang), math.sin(ang)
        best = r0
        for lx, ly, lr in lobes:
            ox, oy = lx - cx, ly - cy
            b = ox * ux + oy * uy
            disc = lr * lr - (ox * ox + oy * oy) + b * b
            if disc >= 0:
                best = max(best, b + math.sqrt(disc))
        out.append((cx + ux * best, cy + uy * best))
    return out


def _dot(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def shadow_edge(a, pts, width, color=INK, alpha=0.85):
    """Ink only along the part of a closed outline facing away from the light
    (bottom-right): layered foliage reads without outlining every clump."""
    n = len(pts)
    run = []

    def flush():
        if len(run) > 3:
            a.ink(list(run), width, color=color, alpha=alpha, wob=0.3)
        run.clear()

    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    start = max(range(n), key=lambda i: -((pts[i][0] - cx) + (pts[i][1] - cy)))  # most top-left point
    for k in range(n + 1):
        x, y = pts[(start + k) % n]
        facing = ((x - cx) + (y - cy)) / (math.hypot(x - cx, y - cy) * 1.414 + 1e-6)
        if facing > -0.15:
            run.append((x, y))
        else:
            flush()
    flush()


def barrel(seed=9):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    R = m - 8

    def staves(art, path):
        n = 18
        for i in range(n):
            ang = 2 * math.pi * i / n + 0.1
            art.ink([(m + (R - 30) * math.cos(ang), m + (R - 30) * math.sin(ang)), (m + R * math.cos(ang), m + R * math.sin(ang))], DETAIL * 0.8, color=shade(WOOD_DARK, 0.5), alpha=0.9, taper=False)

    a.shape(ellipse(m, m, R, R, 120), WOOD_DARK, depth=10, detail=staves, shade_k=0.6)
    for r, wdt in ((R - 9, 8), (R - 30, 10)):
        hoop = skia.Path()
        hoop.addCircle(m, m, r)
        a.stroke_path(hoop, IRON, wdt)
        a.stroke_path(hoop, tint(IRON, 0.5), 2.2, 0.75)
        a.ink(ellipse(m, m, r + wdt / 2, r + wdt / 2, 120), FINE * 1.1, closed=True, wob=0.2)
        a.ink(ellipse(m, m, r - wdt / 2, r - wdt / 2, 120), FINE * 1.1, closed=True, wob=0.2)
    head = R - 36

    def lid(art, path):
        for k in (-2, -1, 0, 1, 2):
            x = m + k * 24
            art.ink([(x, m - head), (x, m + head)], DETAIL * 0.75, color=shade(WOOD_LIGHT, 0.5), alpha=0.9, taper=False)
        grain_lines(art, m - head, m - head, m + head, m + head, 6, shade(WOOD_LIGHT, 0.45), vertical=True, alpha=0.4)

    a.shape(ellipse(m, m, head, head, 120), WOOD_LIGHT, outline=DETAIL * 1.1, depth=9, shade_k=0.2, light_k=0.2, ao=0.6, detail=lid)
    a.shape(ellipse(m + 24, m - 10, 8, 8, 28), shade(WOOD, 0.35), outline=FINE * 1.4, depth=3, shade_k=0, light_k=0, ao=0.5, mottle=0)
    return a.image()


def campfire(seed=13):
    s = 320
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 104, 104, 64), rgb("#5a4d45"), outline=0, depth=6, shade_k=0.0, light_k=0.0, ao=0.4, mottle=0.1)
    n = 11
    for i in range(n):
        ang = 2 * math.pi * i / n + a.rng.uniform(-0.08, 0.08)
        c = vary(a.rng, STONE, 0.07)
        a.shape(blob(m + 118 * math.cos(ang), m + 118 * math.sin(ang), 24, a.rng, 8, 0.15), c, smooth=True, depth=6)
    # Six logs crossed over the fire, seen from above, ends sawn.
    for i in range(4):
        ang = math.pi * i / 4 + 0.3 + a.rng.uniform(-0.12, 0.12)
        ux, uy = math.cos(ang), math.sin(ang)
        L = a.rng.uniform(78, 90)
        x0, y0 = m + ux * L, m + uy * L
        x1, y1 = m - ux * L, m - uy * L
        nx, ny = -uy * 11, ux * 11

        def bark(art, path, x0=x0, y0=y0, x1=x1, y1=y1):
            art.ink([(x0, y0), (x1, y1)], FINE, color=shade(WOOD_DARK, 0.6), alpha=0.6)
            char = skia.Path()
            char.addCircle(m, m, 46)
            art.fill_path(char, rgb("#2b2220"), 0.85, blur=10)

        a.shape([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], vary(a.rng, WOOD_DARK, 0.06), corner=10, depth=5, detail=bark)
        for ex, ey in ((x0, y0), (x1, y1)):

            def rings(art, path, ex=ex, ey=ey):
                art.ink(ellipse(ex, ey, 5.5, 5.5, 20), FINE, closed=True, color=shade(WOOD_LIGHT, 0.45), alpha=0.8)

            a.shape(ellipse(ex, ey, 11, 11, 28), WOOD_LIGHT, outline=DETAIL, depth=3, mottle=0, detail=rings)
    for r, col in ((50, rgb("#e9773a")), (33, rgb("#f4b544")), (16, rgb("#fde8a6"))):
        a.shape(scallop(m, m, r, a.rng, 7, 0.22), col, outline=DETAIL if r > 20 else 0, depth=4, shade_k=0.2, light_k=0.0, ao=0.0, mottle=0)
    for _ in range(12):
        ang, r = a.rng.uniform(0, 6.28), a.rng.uniform(56, 96)
        d = skia.Path()
        d.addCircle(m + r * math.cos(ang), m + r * math.sin(ang), a.rng.uniform(1.5, 2.8))
        a.fill_path(d, rgb("#ffb347"), 0.95)
    return a.image()


def _dot(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def spiky(pts, rng, amp=8.0, step=7.0, closed=True):
    """A leafy fringe along a closed outline: leaf tips at uneven spacing, of
    uneven length (in clumps), each leaning a little along the edge."""
    from pen import Wave, length, normals, resample

    base = resample(pts, closed, 1.5)
    L = length(base, closed)
    cx = sum(q[0] for q in base) / len(base)
    cy = sum(q[1] for q in base) / len(base)
    ns = normals(base, closed)
    clump = Wave(rng, step * 9, L)
    out = []
    pos = 0.0
    idx = lambda d: int(d / L * len(base)) % len(base)  # noqa: E731
    while pos < L - step * 0.6:
        gap = step * rng.uniform(0.7, 1.4)
        # Valley, then the tip leaning toward the next valley.
        for frac, kind in ((0.0, "v"), (rng.uniform(0.45, 0.75), "t")):
            i = idx(pos + gap * frac)
            x, y = base[i]
            nx, ny = ns[i]
            if (x - cx) * nx + (y - cy) * ny < 0:
                nx, ny = -nx, -ny
            if kind == "v":
                d = -amp * rng.uniform(0.15, 0.4)
            else:
                d = amp * max(0.25, 0.75 + 0.45 * clump(pos)) * rng.uniform(0.6, 1.2)
            out.append((x + nx * d, y + ny * d))
        pos += gap
    return out

def blotch(cx, cy, r, rng, lobes=7, spread=0.55, size=(0.35, 0.55)):
    """An organic patch: a base circle and random lobes, star-shaped."""
    ls = []
    for _ in range(lobes):
        ang = rng.uniform(0, 2 * math.pi)
        d = r * rng.uniform(0.2, spread)
        ls.append((cx + d * math.cos(ang), cy + d * math.sin(ang), r * rng.uniform(*size)))
    return lobed(cx, cy, r * 0.45, ls)


FOLIAGE = (rgb("#3b6629"), rgb("#5a8a38"), rgb("#86b04f"))
FOLIAGE_INK = rgb("#1d2e15")


def tree(seed=16, size=720, greens=FOLIAGE):
    a = Art(size, size, seed)
    canopy(a, size / 2, size / 2, size * 0.4, greens)
    return a.image()


def canopy(a, cx, cy, R, greens=FOLIAGE, ink=FOLIAGE_INK, rings=((9, 0.5, 0.6, 0.2, 0.26), (6, 0.24, 0.34, 0.18, 0.23), (3, 0.06, 0.12, 0.13, 0.16))):
    """Leafy top-down foliage (trees, bushes): edge clumps with a fringe of leaf
    tips, rings of lighter patches toward the lit middle. Returns its outline path."""
    m = cx
    dark, mid, light = greens
    # Canopy: leafy clumps around the edge, each with a fringe of leaf tips.
    lobes = []
    n = 11
    for i in range(n):
        ang = 2 * math.pi * i / n + a.rng.uniform(-0.12, 0.12)
        d = R * a.rng.uniform(0.68, 0.74)
        lobes.append((cx + d * math.cos(ang), cy + d * math.sin(ang), R * a.rng.uniform(0.24, 0.3)))
    edge = spiky(lobed(cx, cy, R * 0.8, lobes), a.rng, amp=R * 0.05, step=R * 0.034)
    sil = a.shape(edge, dark, outline=0, corner=0, wob=0.0, depth=R * 0.09, shade_k=0.45, light_k=0.0, ao=0.45, mottle=0.05)

    def patch(cx, cy, r, color, lobes=7):
        pts = spiky(blotch(cx, cy, r, a.rng, lobes), a.rng, amp=r * 0.12 + 3, step=r * 0.09 + 4)
        a.shape(pts, color, outline=0, corner=0, wob=0.0, depth=r * 0.1, shade_k=0.4, light_k=0.3, ao=0.0, mottle=0.04)
        shadow_edge(a, pts, FINE * 1.3, color=ink, alpha=0.85)

    lx, ly = cx - R * 0.1, cy - R * 0.1  # the canopy's lit middle

    def ring(count, d0, d1, r0, r1, color, cx, cy, rot):
        spots = []
        for i in range(count):
            ang = 2 * math.pi * i / count + rot + a.rng.uniform(-0.2, 0.2)
            d = R * a.rng.uniform(d0, d1)
            spots.append((cx + d * math.cos(ang), cy + d * math.sin(ang), R * a.rng.uniform(r0, r1)))
        for x, y, r in sorted(spots, key=lambda q: -(q[0] + q[1])):
            patch(x, y, r, vary(a.rng, color, 0.03))

    with a.clip(sil):
        colors = (mix(dark, mid, 0.55), mid, mix(mid, light, 0.7))
        centers = ((cx, cy), (lx, ly), (lx - R * 0.04, ly - R * 0.04))
        for (count, d0, d1, r0, r1), col, (rx, ry) in zip(rings, colors, centers):
            ring(count, d0, d1, r0, r1, col, rx, ry, a.rng.uniform(0, 6.28))
        for _ in range(int(R * 0.3)):
            ang, d = a.rng.uniform(0, 6.28), R * math.sqrt(a.rng.uniform(0, 0.85))
            x, y = cx + d * math.cos(ang), cy + d * math.sin(ang)
            t = a.rng.uniform(0, 6.28)
            a.ink([(x, y), (x + 6 * math.cos(t), y + 6 * math.sin(t))], FINE * 0.9, color=ink, alpha=0.4, wob=0.1)
    a.ink(edge, FINE * 1.7, closed=True, color=ink, wob=0.0, var=0.25)
    return sil

def bush(seed=17, berries=True):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    canopy(a, m, m, 122, rings=((7, 0.48, 0.58, 0.24, 0.3), (4, 0.2, 0.3, 0.22, 0.26), (2, 0.05, 0.1, 0.16, 0.2)))
    if berries:
        for _ in range(7):
            ang, r = a.rng.uniform(0, 6.28), a.rng.uniform(15, 95)
            a.shape(ellipse(m + r * math.cos(ang), m + r * math.sin(ang), 7, 7, 20), rgb("#c84a3e"), outline=FINE * 1.4, depth=3, light_k=0.6, mottle=0)
    return a.image()

def rock(seed=18):
    s = 270
    a = Art(s, s, seed)
    m = s / 2
    pts = blob(m, m, 108, a.rng, 9, 0.18)
    path = a.shape(pts, STONE, corner=14, depth=20, light_k=0.5)
    with a.clip(path):
        # Facets: a top plane catching the light, edges into it.
        top = [(m - 50, m - 40), (m + 20, m - 60), (m + 50, m - 10), (m, m + 30), (m - 55, m + 5)]
        a.shape(top, tint(STONE, 0.18), outline=DETAIL, corner=8, depth=6, shade_k=0.2, light_k=0.3, ao=0.0)
        a.ink([(m + 50, m - 10), (m + 120, m + 14)], DETAIL, alpha=0.9)
        a.ink([(m, m + 30), (m + 12, m + 130)], DETAIL, alpha=0.9)
        a.ink([(m - 55, m + 5), (m - 130, m + 22)], DETAIL, alpha=0.9)
    return a.image()


def sack(seed=19):
    w, h = 180, 220
    a = Art(w, h, seed)
    burlap = rgb("#cdb07e")

    def weave(art, path):
        for k in range(-200, 200, 9):
            art.ink([(k, 40), (k + 140, 210)], 0.9, color=shade(burlap, 0.4), alpha=0.25, taper=False, wob=0.1)
        art.ink([(w / 2 - 30, 110), (w / 2 - 10, 150)], FINE, color=shade(burlap, 0.5), alpha=0.8)
        art.ink([(w / 2 + 34, 100), (w / 2 + 20, 160)], FINE, color=shade(burlap, 0.5), alpha=0.8)

    a.shape(blob(w / 2, h / 2 + 20, 72, a.rng, 9, 0.06, ry=80), burlap, smooth=True, depth=12, detail=weave)
    a.shape([(w / 2 - 26, 22), (w / 2 + 26, 22), (w / 2 + 16, 70), (w / 2 - 16, 70)], tint(burlap, 0.1), outline=DETAIL * 1.4, corner=8, depth=6)
    a.shape(rect(w / 2 - 22, 58, w / 2 + 22, 70), rgb("#8a6a3e"), outline=DETAIL, corner=4, depth=3, mottle=0)
    return a.image()


def potted_plant(seed=20):
    s = 210
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 62, 62, 64), rgb("#bf6a45"), depth=8)
    a.shape(ellipse(m, m, 49, 49, 64), rgb("#5f4433"), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.5)
    for i in range(8):
        ang = 2 * math.pi * i / 8 + a.rng.uniform(-0.2, 0.2)
        L = a.rng.uniform(70, 92)
        tip = (m + L * math.cos(ang), m + L * math.sin(ang))
        nx, ny = -math.sin(ang), math.cos(ang)
        mid = (m + L * 0.5 * math.cos(ang), m + L * 0.5 * math.sin(ang))
        leaf = chaikin([(m, m), (mid[0] + nx * 16, mid[1] + ny * 16), tip, (mid[0] - nx * 16, mid[1] - ny * 16)], True, 2)

        def vein(art, path, tip=tip):
            art.ink([(m, m), tip], FINE, color=shade(LEAF, 0.5), alpha=0.8)

        a.shape(leaf, vary(a.rng, LEAF, 0.06), outline=DETAIL * 1.3, corner=0, depth=5, detail=vein)
    return a.image()


OBJECTS = {
    "Round Table": round_table,
    "Long Table": long_table,
    "Chair": chair,
    "Stool": stool,
    "Bench": bench,
    "Bed": bed,
    "Chest": chest,
    "Crate": crate,
    "Barrel": barrel,
    "Bookshelf": bookshelf,
    "Rug": rug,
    "Cauldron": cauldron,
    "Campfire": campfire,
    "Anvil": anvil,
    "Well": well,
    "Tree": tree,
    "Bush": bush,
    "Rock": rock,
    "Sack": sack,
    "Potted Plant": potted_plant,
}

# Objects with red (recolorable) parts.
COLORABLE = {"Long Table", "Bed", "Rug"}

TAGS = {
    "Furniture": ["Round Table", "Long Table", "Chair", "Stool", "Bench", "Bed", "Bookshelf", "Rug"],
    "Storage": ["Chest", "Crate", "Barrel", "Sack"],
    "Nature": ["Tree", "Bush", "Rock", "Potted Plant"],
    "Crafting": ["Anvil", "Cauldron", "Campfire", "Well"],
}
