"""Town and outdoors (batch 11): market, carts, farmyard fences and hay,
village fixtures. Top-down, same pen style (red = colorable)."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, dot, fruit, pile, scallop, soft_shadow
from obj_craft import handle
from obj_magic import glow
from obj_nature import GREEN, GREEN_L, leaf
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

CANVAS = rgb("#e6dcc4")
HAY = rgb("#d9bf72")
ROPE = rgb("#c9b088")
FISH = rgb("#9fb3bc")


def wheel(a, x, y, length=70, width=16, ang=0.0):
    """A wheel standing upright, from above: a narrow band with a hub."""
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    pts = [(x - ux * length / 2 - px * width / 2, y - uy * length / 2 - py * width / 2), (x + ux * length / 2 - px * width / 2, y + uy * length / 2 - py * width / 2), (x + ux * length / 2 + px * width / 2, y + uy * length / 2 + py * width / 2), (x - ux * length / 2 + px * width / 2, y - uy * length / 2 + py * width / 2)]
    a.shape(pts, WOOD_DARK, outline=DETAIL * 1.6, corner=width / 2.2, depth=3, mottle=0)
    a.ink([(x - ux * length * 0.4, y - uy * length * 0.4), (x + ux * length * 0.4, y + uy * length * 0.4)], FINE * 1.2, color=IRON, alpha=0.9, taper=False)
    a.shape(ellipse(x, y, width * 0.7, width * 0.7, 16), IRON, outline=DETAIL, depth=2, mottle=0)


def striped_awning(a, x0, y0, x1, y1, stripes=6, color=RED):
    """A striped canvas awning (red stripes = colorable), scalloped front."""
    sw = (x1 - x0) / stripes
    base = rect(x0, y0, x1, y1)

    def stripes_(art, p):
        for k in range(0, stripes, 2):
            art.shape(rect(x0 + k * sw, y0 - 4, x0 + (k + 1) * sw, y1 + 4), color, outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.03)
        for k in range(1, stripes):
            art.ink([(x0 + k * sw, y0), (x0 + k * sw, y1)], FINE, color=shade(color, 0.4), alpha=0.6, taper=False)

    a.shape(base, CANVAS, corner=4, depth=8, light_k=0.3, detail=stripes_)
    # Scalloped valance along the front edge.
    for k in range(stripes):
        cx = x0 + (k + 0.5) * sw
        col = color if k % 2 == 0 else CANVAS
        a.shape(chaikin([(cx - sw / 2, y1), (cx + sw / 2, y1), (cx + sw * 0.3, y1 + 14), (cx - sw * 0.3, y1 + 14)], True, 2), col, outline=DETAIL, corner=0, depth=2, mottle=0)


# -- market --------------------------------------------------------------------------------------


def market_stall(seed=1001):
    w, h = 420, 300
    a = Art(w, h, seed)
    # The counter in front (bottom) peeks out under the awning.
    board(a, 20, h - 90, w - 20, h - 20, WOOD, n=1, corner=6)
    for x in range(60, w - 40, 70):
        soft_shadow(a, (x, h - 56), 22, 3, 4)
        a.shape(ellipse(x, h - 56, 22, 22, 32), rgb("#b9925a"), outline=DETAIL * 1.2, depth=3)
        pile(a, x, h - 56, 14, 4, lambda art, xx, yy, hh: fruit(art, xx, yy, hh))
    striped_awning(a, 10, 10, w - 10, h - 110)
    return a.image()


def fruit_stall(seed=1002):
    w, h = 380, 220
    a = Art(w, h, seed)
    board(a, 10, 10, w - 10, h - 10, WOOD_DARK, n=1, corner=6)
    kinds = [("apple",), ("green",), ("pear",)]
    for k, x in enumerate((70, 190, 310)):
        a.shape(rect(x - 54, 26, x + 54, h - 26), WOOD_LIGHT, outline=DETAIL * 1.2, corner=4, depth=4, detail=lambda art, p, x=x: boards(art, x - 54, 26, x + 54, h - 26, WOOD_LIGHT, 2, vertical=True))
        with a.clip(to_path(rect(x - 48, 32, x + 48, h - 32))):
            pile(a, x, h / 2, 64, 12, lambda art, xx, yy, hh, kk=kinds[k][0]: fruit(art, xx, yy, 0.3 + hh * 0.7, kk), ry=80)
    return a.image()


def fish_stall(seed=1003):
    w, h = 360, 200
    a = Art(w, h, seed)
    board(a, 10, 10, w - 10, h - 10, WOOD, n=1, corner=6)

    def ice(art, p):
        for _ in range(40):
            dot(art, art.rng.uniform(26, w - 26), art.rng.uniform(26, h - 26), art.rng.uniform(2, 4), rgb("#eef6f8"), 0.9)

    a.shape(rect(22, 22, w - 22, h - 22), rgb("#cfe0e4"), outline=DETAIL * 1.2, corner=4, depth=4, detail=ice)
    for k in range(7):
        x, y = 60 + (k % 4) * 80, 66 + (k // 4) * 70
        t = a.rng.uniform(-0.3, 0.3)
        body = [(x - 34, y), (x - 10, y - 13), (x + 22, y - 9), (x + 34, y), (x + 22, y + 9), (x - 10, y + 13)]
        body = [(x + (px - x) * math.cos(t) - (py - y) * math.sin(t), y + (px - x) * math.sin(t) + (py - y) * math.cos(t)) for px, py in body]
        a.shape(chaikin(body, True, 2), vary(a.rng, FISH, 0.08), outline=DETAIL, corner=0, depth=3, light_k=0.5, mottle=0)
        tail = [(x + 30, y), (x + 46, y - 12), (x + 46, y + 12)]
        tail = [(x + (px - x) * math.cos(t) - (py - y) * math.sin(t), y + (px - x) * math.sin(t) + (py - y) * math.cos(t)) for px, py in tail]
        a.shape(tail, shade(FISH, 0.15), outline=DETAIL, corner=1, depth=1, mottle=0)
        dot(a, x - 22 * math.cos(t), y - 22 * math.sin(t), 2.4)
    return a.image()


def parasol(seed=1004):
    s = 280
    a = Art(s, s, seed)
    m = s / 2
    n = 10
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        seg = [(m, m), (m + 120 * math.cos(t0), m + 120 * math.sin(t0)), (m + 112 * math.cos((t0 + t1) / 2), m + 112 * math.sin((t0 + t1) / 2)), (m + 120 * math.cos(t1), m + 120 * math.sin(t1))]
        lit = math.cos((t0 + t1) / 2 + math.pi * 0.75)
        col = RED if k % 2 == 0 else CANVAS
        a.shape(seg, tint(col, 0.12 * lit) if lit > 0 else shade(col, -0.15 * lit), outline=DETAIL, corner=0, wob=0.2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    a.ink([(m + 120 * math.cos(t), m + 120 * math.sin(t)) for t in [2 * math.pi * k / n for k in range(n)]] + [], OUTLINE * 0.8, closed=True, wob=0.2)
    a.shape(ellipse(m, m, 10, 10, 16), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def flower_cart(seed=1005):
    w, h = 340, 220
    a = Art(w, h, seed)
    wheel(a, w / 2, 16, 110, 18)
    wheel(a, w / 2, h - 16, 110, 18)
    handle(a, 20, h / 2 - 20, 70, h / 2 - 20, 10)
    handle(a, 20, h / 2 + 20, 70, h / 2 + 20, 10)
    a.shape(rect(60, 30, w - 20, h - 30), WOOD, corner=6, depth=8, detail=lambda art, p: boards(art, 60, 30, w - 20, h - 30, WOOD, 3, vertical=True))
    a.shape(rect(76, 46, w - 36, h - 46), rgb("#5a4030"), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5)
    cols = [rgb("#e6b84a"), rgb("#c8443a"), rgb("#f3eee2"), rgb("#9a6ab8"), rgb("#e88aa8")]
    for _ in range(26):
        x, y = a.rng.uniform(86, w - 46), a.rng.uniform(56, h - 56)
        if a.rng.random() < 0.4:
            leaf(a, x, y, 22, vary(a.rng, GREEN, 0.05), vein=False, outline=FINE)
        else:
            c = a.rng.choice(cols)
            for k in range(5):
                pa = 2 * math.pi * k / 5
                a.shape(ellipse(x + 6 * math.cos(pa), y + 6 * math.sin(pa), 6, 4, 12, rot=pa), c, outline=FINE, depth=1, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
            dot(a, x, y, 3, rgb("#9a5a2a"))
    return a.image()


def produce_crates(seed=1006):
    w, h = 300, 260
    a = Art(w, h, seed)
    fills = [("apple", None), ("green", None), (None, rgb("#e08a3a")), (None, rgb("#a8483a"))]
    for k, (kind, veg) in enumerate(fills):
        x, y = 10 + (k % 2) * 140, 10 + (k // 2) * 124
        a.shape(rect(x, y, x + 132, y + 116), WOOD_LIGHT, corner=4, depth=6)
        a.shape(rect(x + 10, y + 10, x + 122, y + 106), shade(WOOD_LIGHT, 0.4), outline=DETAIL, corner=3, depth=4, shade_k=0, light_k=0, ao=0.5)
        with a.clip(to_path(rect(x + 10, y + 10, x + 122, y + 106))):
            if kind:
                pile(a, x + 66, y + 58, 70, 14, lambda art, xx, yy, hh, kind=kind: fruit(art, xx, yy, 0.3 + hh * 0.7, kind), ry=60)
            else:
                for _ in range(14):
                    xx, yy = x + a.rng.uniform(20, 112), y + a.rng.uniform(20, 96)
                    soft_shadow(a, (xx, yy), 10, 2, 3)
                    a.shape(ellipse(xx, yy, 18, 8, 20, rot=a.rng.uniform(0, 3.14)), vary(a.rng, veg, 0.06), outline=FINE * 1.3, depth=2, light_k=0.4, mottle=0)
    return a.image()


# -- carts -----------------------------------------------------------------------------------------


def cart(seed=1011, broken=False):
    w, h = 420, 260
    a = Art(w, h, seed)
    wheel(a, 200, 16, 120, 20)
    if not broken:
        wheel(a, 200, h - 16, 120, 20)
    for y in (h / 2 - 34, h / 2 + 34):
        handle(a, 300, y, w - 10, y + (y - h / 2) * 0.3, 12)
    bed = rect(30, 34, 310, h - 34)
    if broken:
        bed = [(30, 34), (310, 34), (310, h - 60), (220, h - 20), (30, h - 40)]
    a.shape(bed, WOOD, corner=6, depth=10, detail=lambda art, p: boards(art, 30, 34, 310, h - 34, WOOD, 4, vertical=True))
    a.shape(rect(46, 50, 294, h - 50) if not broken else [(46, 50), (294, 50), (294, h - 74), (220, h - 40), (46, h - 56)], shade(WOOD, 0.3), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.4)
    if broken:
        for _ in range(3):
            x, y = a.rng.uniform(60, 240), a.rng.uniform(h - 30, h - 14)
            a.shape(rect(x, y - 6, x + a.rng.uniform(40, 70), y + 6), WOOD, outline=DETAIL, corner=3, depth=2)
    else:
        for x, y in ((100, 100), (170, 150)):
            from objects import sack

            img = sack(seed=a.rng.randint(0, 99)).resize((90, 110))
            import numpy as np

            a.c.drawImageRect(skia.Image.fromarray(np.asarray(img), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(x - 45, y - 55, 90, 110))
    return a.image()


def broken_cart(seed=1012):
    return cart(seed, broken=True)


def covered_wagon(seed=1013):
    w, h = 520, 280
    a = Art(w, h, seed)
    for x in (110, 330):
        wheel(a, x, 18, 110, 20)
        wheel(a, x, h - 18, 110, 20)
    handle(a, 420, h / 2, w - 10, h / 2, 14)
    # Canvas cover on hoops, from above: ribs across, the lit side lighter.
    cover = rect(30, 30, 430, h - 30)

    def hoops(art, p):
        for x in range(70, 430, 60):
            art.ink([(x, 32), (x + 4, h - 32)], DETAIL, color=shade(CANVAS, 0.45), alpha=0.85)
        g = skia.Path()
        g.addRect(skia.Rect.MakeLTRB(30, 30, 430, h / 2))
        art.fill_path(g, tint(CANVAS, 0.3), 0.4, blur=20)

    a.shape(cover, CANVAS, corner=40, depth=12, light_k=0.3, detail=hoops)
    return a.image()


def wheelbarrow(seed=1014):
    """A wheelbarrow from above: the two shafts running from the grips at the
    back to the wheel at the front (between them), the tray on top, wider at
    the back and narrowing forward, with its rim and a bit of soil inside."""
    w, h = 340, 200
    a = Art(w, h, seed)
    cy = h / 2
    # Wheel at the front, between the shaft ends.
    wheel(a, w - 46, cy, 72, 22, ang=0.0)
    for side in (-1, 1):
        handle(a, 14, cy + side * 54, w - 46, cy + side * 18, 11)
        grip = rect(6, cy + side * 54 - 8, 40, cy + side * 54 + 8)
        a.shape(grip, rgb("#5a3a22"), outline=DETAIL * 1.4, corner=6, depth=2, mottle=0)
    a.ink([(w - 46, cy - 20), (w - 46, cy + 20)], DETAIL * 2, color=IRON, taper=False)
    tray = chaikin([(64, cy - 70), (210, cy - 50), (250, cy - 24), (250, cy + 24), (210, cy + 50), (64, cy + 70)], True, 2)
    inner = chaikin([(84, cy - 52), (204, cy - 36), (232, cy - 16), (232, cy + 16), (204, cy + 36), (84, cy + 52)], True, 2)
    a.shape(tray, rgb("#7a8088"), depth=10, light_k=0.45)
    a.ink([(a_x, a_y) for a_x, a_y in tray], FINE * 1.2, closed=True, color=tint(rgb("#7a8088"), 0.4), alpha=0.6)

    def soil(art, p):
        art.shape(blob(140, cy + 4, 46, art.rng, 10, 0.2, ry=30), rgb("#6a4e36"), outline=0, smooth=True, depth=3, shade_k=0.3, light_k=0.3, ao=0, mottle=0.12)
        for _ in range(16):
            dot(art, art.rng.uniform(100, 190), art.rng.uniform(cy - 24, cy + 30), art.rng.uniform(1.4, 2.6), rgb("#4a3626"), 0.8)

    a.shape(inner, shade(rgb("#7a8088"), 0.35), outline=DETAIL, corner=0, depth=10, shade_k=0, light_k=0, ao=0.55, detail=soil)
    return a.image()

def cart_wheel(seed=1015):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    # A loose wheel lying flat: rim, spokes, hub.
    a.ink(ellipse(m, m, 92, 92, 80), 26, closed=True, color=INK)
    a.ink(ellipse(m, m, 92, 92, 80), 18, closed=True, color=WOOD_DARK)
    a.ink(ellipse(m, m, 101, 101, 80), 4, closed=True, color=IRON)
    for k in range(10):
        t = 2 * math.pi * k / 10
        handle(a, m + 16 * math.cos(t), m + 16 * math.sin(t), m + 82 * math.cos(t), m + 82 * math.sin(t), 9, WOOD)
    a.shape(ellipse(m, m, 22, 22, 28), WOOD, outline=DETAIL * 1.4, depth=3, mottle=0)
    a.shape(ellipse(m, m, 9, 9, 16), IRON, outline=DETAIL, depth=2, mottle=0)
    return a.image()


# -- farmyard -------------------------------------------------------------------------------------


def hay_strokes(a, path, n=160):
    b = path.getBounds()
    for _ in range(n):
        x, y = a.rng.uniform(b.left(), b.right()), a.rng.uniform(b.top(), b.bottom())
        t = a.rng.uniform(0, 6.28)
        a.ink([(x, y), (x + 14 * math.cos(t), y + 14 * math.sin(t))], FINE * 1.1, color=shade(HAY, a.rng.uniform(0.05, 0.45)), alpha=0.9, wob=0.2)


def round_bale(seed=1021):
    s = 240
    a = Art(s, s, seed)
    m = s / 2

    def swirl(art, p):
        hay_strokes(art, p, 90)
        sp = [(m + (8 + 3.4 * t) * math.cos(t * 0.9), m + (8 + 3.4 * t) * math.sin(t * 0.9)) for t in [k * 0.2 for k in range(130)]]
        art.ink(sp, DETAIL * 0.9, color=shade(HAY, 0.45), alpha=0.85)

    a.shape(ellipse(m, m, 100, 100, 80), HAY, depth=14, light_k=0.4, detail=swirl)
    return a.image()


def square_bale(seed=1022):
    w, h = 260, 160
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), HAY, corner=10, depth=10, light_k=0.4, detail=lambda art, p: hay_strokes(art, p, 120))
    for x in (80, w - 80):
        a.ink([(x, 12), (x + 4, h - 12)], DETAIL * 1.4, color=rgb("#8a6a3e"))
    return a.image()


def hay_pile(seed=1023):
    s = 280
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m, 116, a.rng, 12, 0.14), HAY, depth=14, light_k=0.4, smooth=True, detail=lambda art, p: hay_strokes(art, p, 240))
    for _ in range(24):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(116, 130)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        a.ink([(x, y), (x + 12 * math.cos(t), y + 12 * math.sin(t))], FINE * 1.1, color=shade(HAY, 0.2))
    return a.image()


def fence(seed=1031, length=512, posts=4, rails=2):
    w, h = length, 60
    a = Art(w, h, seed)
    for k in range(rails):
        y = h / 2 + (k - (rails - 1) / 2) * 10
        a.shape(rect(6, y - 6, w - 6, y + 6), vary(a.rng, WOOD, 0.05), outline=DETAIL * 1.2, corner=3, depth=2)
    for k in range(posts):
        x = 18 + k * (w - 36) / (posts - 1)
        a.shape(rect(x - 13, h / 2 - 16, x + 13, h / 2 + 16), WOOD_DARK, outline=DETAIL * 1.3, corner=4, depth=4)
        a.ink(rect(x - 6, h / 2 - 8, x + 6, h / 2 + 8), FINE, closed=True, color=shade(WOOD_DARK, 0.45), alpha=0.7)
    return a.image()


def fence_corner(seed=1032):
    s = 300
    a = Art(s, s, seed)
    for k in (-1, 1):
        y = 40 + k * 8
        a.shape(rect(30, y - 6, s - 6, y + 6), WOOD, outline=DETAIL * 1.2, corner=3, depth=2)
        x = 40 + k * 8
        a.shape(rect(x - 6, 30, x + 6, s - 6), WOOD, outline=DETAIL * 1.2, corner=3, depth=2)
    for x, y in ((40, 40), (s - 20, 40), (40, s - 20), (s / 2 + 10, 40), (40, s / 2 + 10)):
        a.shape(rect(x - 14, y - 14, x + 14, y + 14), WOOD_DARK, outline=DETAIL * 1.3, corner=4, depth=4)
    return a.image()


def fence_gate(seed=1033):
    w, h = 300, 140
    a = Art(w, h, seed)
    for x in (20, w - 20):
        a.shape(rect(x - 16, 44, x + 16, 96), WOOD_DARK, outline=DETAIL * 1.3, corner=4, depth=4)
    # The gate swung half open (a frame of boards with a brace).
    gate = [(36, 64), (w - 70, 30), (w - 66, 46), (40, 80)]
    a.shape(gate, WOOD, outline=DETAIL * 1.3, corner=3, depth=3)
    a.ink([(60, 68), (w - 90, 40)], FINE * 1.3, color=shade(WOOD, 0.5))
    a.shape(rect(w - 70, 26, w - 58, 50), IRON, outline=DETAIL, corner=2, depth=1, mottle=0)
    return a.image()


def picket_fence(seed=1034):
    w, h = 512, 50
    a = Art(w, h, seed)
    a.shape(rect(6, h / 2 - 6, w - 6, h / 2 + 6), WOOD_LIGHT, outline=DETAIL * 1.2, corner=3, depth=2)
    for k in range(16):
        x = 20 + k * 31.5
        pts = [(x - 9, h / 2 - 9), (x + 9, h / 2 - 9), (x + 9, h / 2 + 9), (x - 9, h / 2 + 9)]
        a.shape(pts, rgb("#ece4d3"), outline=DETAIL * 1.1, corner=2, depth=2, mottle=0)
    return a.image()


# -- village fixtures --------------------------------------------------------------------------------


def signpost(seed=1041):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    for ang, L in ((-0.5, 90), (0.6, 80), (2.6, 86)):
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        x0, y0 = m + ux * 8, m + uy * 8
        x1, y1 = m + ux * L, m + uy * L
        board_ = [(x0 - px * 14, y0 - py * 14), (x1 - px * 14, y1 - py * 14), (x1 + ux * 20, y1 + uy * 20), (x1 + px * 14, y1 + py * 14), (x0 + px * 14, y0 + py * 14)]
        a.shape(board_, WOOD_LIGHT, outline=DETAIL * 1.3, corner=2, depth=3)
        a.ink([(x0 + ux * 14, y0 + uy * 14), (x1 - ux * 6, y1 - uy * 6)], FINE * 1.2, color=shade(WOOD_LIGHT, 0.5), alpha=0.8)
    a.shape(ellipse(m, m, 18, 18, 24), WOOD_DARK, outline=DETAIL * 1.3, depth=3)
    return a.image()


def street_lamp(seed=1042):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 100, rgb("#ffd27a"), 0.4)
    a.shape(ellipse(m, m, 34, 34, 32), IRON, depth=6)
    a.shape(rect(m - 22, m - 22, m + 22, m + 22), rgb("#ffe39a"), outline=DETAIL * 1.3, corner=4, depth=3, shade_k=0, light_k=0.5)
    a.ink([(m - 22, m), (m + 22, m)], DETAIL, color=IRON, taper=False)
    a.ink([(m, m - 22), (m, m + 22)], DETAIL, color=IRON, taper=False)
    a.shape(ellipse(m, m, 10, 10, 16), IRON, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def gallows(seed=1043):
    w, h = 360, 360
    a = Art(w, h, seed)
    board(a, 20, 60, w - 20, h - 20, WOOD_DARK, n=5, vertical=True, corner=6)
    a.shape(rect(w / 2 - 50, h - 120, w / 2 + 50, h - 40), shade(WOOD_DARK, 0.4), outline=DETAIL * 1.2, corner=3, depth=6, shade_k=0, light_k=0, ao=0.5)  # trap door
    for k in range(4):
        a.shape(rect(w / 2 - 60, 20 + k * 12, w / 2 + 60, 30 + k * 12), WOOD, outline=DETAIL, corner=2, depth=2)  # steps
    a.shape(rect(30, 80, 64, 114), WOOD, outline=DETAIL * 1.3, corner=4, depth=4)  # upright
    a.shape(rect(30, 84, w / 2 + 14, 110), WOOD, outline=DETAIL * 1.3, corner=4, depth=5, light_k=0.4)  # beam
    a.ink([(w / 2, 110), (w / 2, h - 80)], DETAIL * 1.4, color=ROPE)
    a.ink(ellipse(w / 2, h - 70, 14, 14, 24), DETAIL * 1.4, closed=True, color=ROPE)
    return a.image()


def chicken_coop(seed=1044):
    w, h = 300, 240
    a = Art(w, h, seed)
    # A little hut (pitched roof from above) with a fenced run beside it.
    a.shape(rect(160, 30, w - 10, h - 30), rgb("#d8c9a8"), outline=DETAIL * 1.2, corner=4, depth=4, shade_k=0, light_k=0, ao=0.3)
    for x in range(170, w, 20):
        a.ink([(x, 30), (x, h - 30)], FINE, color=shade(rgb("#d8c9a8"), 0.4), alpha=0.6, taper=False)
    a.ink(rect(160, 30, w - 10, h - 30), DETAIL * 1.2, closed=True, color=WOOD_DARK)
    roof = rgb("#8a5a3a")
    a.shape(rect(10, 10, 170, h / 2), roof, corner=4, depth=6, light_k=0.4, detail=lambda art, p: [art.ink([(10, y), (170, y)], FINE, color=shade(roof, 0.5), alpha=0.7, taper=False) for y in range(24, int(h / 2), 14)])
    a.shape(rect(10, h / 2, 170, h - 10), shade(roof, 0.2), corner=4, depth=6, shade_k=0.6, detail=lambda art, p: [art.ink([(10, y), (170, y)], FINE, color=shade(roof, 0.6), alpha=0.7, taper=False) for y in range(int(h / 2) + 14, h - 10, 14)])
    a.ink([(10, h / 2), (170, h / 2)], DETAIL * 1.6)
    for x, y in ((210, 90), (250, 160)):
        a.shape(ellipse(x, y, 16, 12, 24), rgb("#f2ece0"), outline=DETAIL, depth=2, light_k=0.4, mottle=0)
        a.shape(ellipse(x + 12, y - 4, 7, 7, 16), rgb("#f2ece0"), outline=FINE * 1.3, depth=1, mottle=0)
        dot(a, x + 15, y - 9, 3, rgb("#c8443a"))
    return a.image()


def dog_house(seed=1045):
    w, h = 200, 220
    a = Art(w, h, seed)
    roof = rgb("#a8483a")
    a.shape(rect(10, 10, w / 2, h - 30), roof, corner=4, depth=6, light_k=0.4)
    a.shape(rect(w / 2, 10, w - 10, h - 30), shade(roof, 0.2), corner=4, depth=6, shade_k=0.6)
    a.ink([(w / 2, 10), (w / 2, h - 30)], DETAIL * 1.6)
    a.shape(rect(w / 2 - 36, h - 34, w / 2 + 36, h - 10), WOOD, outline=DETAIL * 1.2, corner=3, depth=3)
    a.shape(ellipse(w / 2, h - 22, 18, 10, 20), rgb("#2a221e"), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def outhouse(seed=1046):
    s = 200
    a = Art(s, s, seed)
    roof = rgb("#7a5a3e")
    a.shape(rect(14, 14, s - 14, s - 14), roof, corner=4, depth=10, light_k=0.3, detail=lambda art, p: boards(art, 14, 14, s - 14, s - 14, roof, 5, vertical=True))
    a.shape([(s / 2 - 10, 40), (s / 2 + 10, 40), (s / 2 + 4, 56), (s / 2 - 4, 56)], rgb("#e6b84a"), outline=FINE * 1.2, corner=1, depth=1, mottle=0)  # moon vent
    return a.image()


def laundry_line(seed=1047):
    w, h = 512, 160
    a = Art(w, h, seed)
    for x in (16, w - 16):
        a.shape(ellipse(x, h / 2, 12, 12, 20), WOOD_DARK, outline=DETAIL * 1.2, depth=3)
    a.ink([(16, h / 2), (w - 16, h / 2)], FINE * 1.3, color=ROPE)
    x = 50
    cols = [RED, CANVAS, rgb("#7a9ac8"), RED, CANVAS]
    for k, c in enumerate(cols):
        cw = a.rng.uniform(60, 90)
        ch = a.rng.uniform(40, 60)
        a.shape(rect(x, h / 2 - ch / 2, x + cw, h / 2 + ch / 2), c, outline=DETAIL * 1.2, corner=3, depth=4, light_k=0.3)
        for px_ in (x + 8, x + cw - 8):
            a.shape(rect(px_ - 3, h / 2 - 8, px_ + 3, h / 2 + 8), WOOD_LIGHT, outline=FINE, corner=1, depth=1, mottle=0)
        x += cw + 14
    return a.image()


def hitching_post(seed=1048):
    w, h = 320, 100
    a = Art(w, h, seed)
    for x in (30, w - 30):
        a.shape(rect(x - 16, h / 2 - 16, x + 16, h / 2 + 16), WOOD_DARK, outline=DETAIL * 1.3, corner=4, depth=4)
    a.shape(rect(20, h / 2 - 9, w - 20, h / 2 + 9), WOOD, outline=DETAIL * 1.2, corner=5, depth=3, light_k=0.4)
    for x in (110, 190):
        a.ink(ellipse(x, h / 2 + 18, 10, 12, 20), DETAIL * 1.2, closed=True, color=IRON)
    return a.image()


def ladder(seed=1049):
    w, h = 140, 460
    a = Art(w, h, seed)
    for x in (30, w - 30):
        handle(a, x, 10, x, h - 10, 14)
    for y in range(40, h - 20, 46):
        handle(a, 30, y, w - 30, y, 10, WOOD_LIGHT)
    return a.image()


def rope_coil(seed=1050):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    sp = [(m + (16 + 4.2 * t) * math.cos(t * 1.1), m + (16 + 4.2 * t) * math.sin(t * 1.1)) for t in [k * 0.12 for k in range(130)]]
    a.ink(sp, 16, color=INK, taper=False)
    a.ink(sp, 11, color=ROPE, taper=False)
    for i in range(0, len(sp) - 1, 3):
        (x0, y0), (x1, y1) = sp[i], sp[i + 1]
        a.ink([(x0, y0), (x1, y1)], FINE, color=shade(ROPE, 0.5), alpha=0.6)
    return a.image()


def footbridge(seed=1051):
    w, h = 220, 512
    a = Art(w, h, seed)
    for y in range(14, h - 10, 30):
        a.shape(rect(30 + a.rng.uniform(-4, 4), y, w - 30 + a.rng.uniform(-4, 4), y + 26), vary(a.rng, WOOD, 0.06), outline=DETAIL * 1.2, corner=3, depth=3)
    for x in (22, w - 22):
        handle(a, x, 6, x, h - 6, 14, WOOD_DARK)
        for y in (40, h / 2, h - 40):
            a.shape(rect(x - 12, y - 12, x + 12, y + 12), WOOD_DARK, outline=DETAIL * 1.2, corner=3, depth=3)
    return a.image()


TOWN = {
    "Market Stall": market_stall,
    "Fruit Stall": fruit_stall,
    "Fish Stall": fish_stall,
    "Parasol": parasol,
    "Flower Cart": flower_cart,
    "Produce Crates": produce_crates,
    "Cart": cart,
    "Broken Cart": broken_cart,
    "Covered Wagon": covered_wagon,
    "Wheelbarrow": wheelbarrow,
    "Cart Wheel": cart_wheel,
    "Round Hay Bale": round_bale,
    "Square Hay Bale": square_bale,
    "Hay Pile": hay_pile,
    "Fence": fence,
    "Short Fence": lambda: fence(1035, length=256, posts=2),
    "Fence Corner": fence_corner,
    "Fence Gate": fence_gate,
    "Picket Fence": picket_fence,
    "Signpost": signpost,
    "Street Lamp": street_lamp,
    "Gallows": gallows,
    "Chicken Coop": chicken_coop,
    "Dog House": dog_house,
    "Outhouse": outhouse,
    "Laundry Line": laundry_line,
    "Hitching Post": hitching_post,
    "Ladder": ladder,
    "Rope Coil": rope_coil,
    "Footbridge": footbridge,
}

TOWN_COLORABLE = {"Market Stall", "Parasol", "Laundry Line"}
