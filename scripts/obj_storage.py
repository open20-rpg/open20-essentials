"""Storage, kitchen and tableware (batch 2)."""

import math

import skia

from kit import coin, fruit, pile, soft_shadow, BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, cabinet, dot, grain_lines, ring, scallop
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, vary

CLAY = rgb("#bf7a4f")
CERAMIC = rgb("#e4dccb")
GOLD = rgb("#e2b84e")
APPLE = rgb("#c4473a")
STRAW = rgb("#d9bf72")
BURLAP = rgb("#cdb07e")
GLASS_G = rgb("#6f9a6a")
WAX = rgb("#f1e6c8")


def vessel(a, cx, cy, r, body, inside, rim=0.78, outline=OUTLINE, fill_inside=None):
    """A round container seen from above: body, rim and its darker inside."""
    a.shape(ellipse(cx, cy, r, r, 72), body, outline=outline, depth=r * 0.12)
    a.shape(ellipse(cx, cy, r * rim, r * rim, 64), inside, outline=DETAIL * 1.1, depth=r * 0.15, shade_k=0.0, light_k=0.0, ao=0.6, mottle=0.04, detail=fill_inside)


def coins(a, cx, cy, n, spread, r=None, ry=None, fill=False):
    """A heap of coins: a golden mound (so no floor shows between them) with
    coins piled on it, the top ones lighter. With `fill` (inside a
    container) the heap runs past the edges, which clip it."""
    ry = ry or spread
    if fill:
        base = rect(cx - spread * 1.3, cy - ry * 1.3, cx + spread * 1.3, cy + ry * 1.3)
        a.shape(base, shade(GOLD, 0.35), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.1)
        pile(a, cx, cy, spread * 1.25, int(n * 0.7), lambda art, x, y, h: coin(art, x, y, 0.0, r), ry=ry * 1.25, min_gap=0.3)
    else:
        mound = blob(cx, cy, spread * 0.92, a.rng, 12, 0.08, ry=ry * 0.92)
        a.shape(mound, shade(GOLD, 0.15), outline=DETAIL, smooth=True, depth=spread * 0.12, shade_k=0.5, light_k=0.4, ao=0.2, mottle=0.08)
    pile(a, cx, cy, spread * (1.05 if fill else 0.95), n, lambda art, x, y, h: coin(art, x, y, h, r), ry=ry * (1.05 if fill else 0.95), min_gap=0.3)


def apples(a, cx, cy, n, spread, r=13, kinds=("apple", "apple", "green")):
    """Fruit filling a container: a packed bottom layer (darker, lower) over
    the whole inside, then a heap on it running past the rim (clipped)."""
    pile(a, cx, cy, spread * 1.25, int(n * 1.2), lambda art, x, y, h: fruit(art, x, y, 0.0, art.rng.choice(kinds)), min_gap=0.7)
    pile(a, cx, cy, spread * 1.05, n, lambda art, x, y, h: fruit(art, x, y, 0.25 + 0.75 * h, art.rng.choice(kinds)), min_gap=0.9)


# -- storage ---------------------------------------------------------------------------------


def open_chest(seed=101):
    w, h = 280, 230
    a = Art(w, h, seed)
    # Lid flipped open behind (top), the box with its treasure in front.
    board(a, 12, 6, w - 12, 70, WOOD_DARK, n=2, corner=10)
    for x in (44, w - 44):
        a.shape(rect(x - 11, 6, x + 11, 70), IRON, outline=DETAIL * 1.2, corner=3, depth=4, mottle=0)
    a.shape(rect(10, 64, w - 10, h - 10), WOOD, corner=10, depth=10)

    def treasure(art, path):
        coins(art, w / 2, 150, 110, 118, ry=72, fill=True)
        for x, y, c in ((92, 128, rgb("#5fb0d8")), (190, 165, rgb("#d0465a")), (150, 120, rgb("#7ccf8a"))):
            soft_shadow(art, (x, y), 10, 3, 4, 0.35, 3)
            art.shape([(x, y - 11), (x + 10, y), (x, y + 11), (x - 10, y)], c, outline=DETAIL, corner=1, depth=3, light_k=0.8, mottle=0)
        soft_shadow(art, (210, 118), 16, 4, 5, 0.4, 4)
        art.shape(ellipse(210, 118, 16, 16, 28), GOLD, outline=DETAIL, depth=3, light_k=0.5, mottle=0)
        art.shape(ellipse(210, 118, 10, 10, 20), rgb("#7a2030"), outline=FINE, depth=2, shade_k=0, light_k=0, mottle=0)

    a.shape(rect(26, 80, w - 26, h - 26), rgb("#4a3324"), outline=DETAIL * 1.2, corner=6, depth=10, shade_k=0, light_k=0, ao=0.5, detail=treasure)
    return a.image()


def crate_stack(seed=102):
    w, h = 420, 400
    a = Art(w, h, seed)
    from objects import crate

    for (x, y, s) in ((10, 150, 240), (200, 170, 210), (110, 10, 220)):
        img = crate(seed=a.rng.randint(0, 999))
        a.c.drawImageRect(skia.Image.fromarray(__import__("numpy").asarray(img.resize((s, s))), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(x, y, s, s))
    return a.image(grain=0)


def small_crate(seed=103):
    s = 150
    a = Art(s, s, seed)
    a.shape(rect(8, 8, s - 8, s - 8), WOOD_LIGHT, corner=5, depth=8, detail=lambda art, p: boards(art, 8, 8, s - 8, s - 8, WOOD_LIGHT, 3))
    a.shape([(26, s - 36), (s - 46, 24), (s - 26, 24), (s - 26, 36), (46, s - 24), (26, s - 24)], WOOD, outline=DETAIL * 1.2, corner=3, depth=5)
    return a.image()


def straw_crate(seed=104):
    s = 230
    a = Art(s, s, seed)
    a.shape(rect(8, 8, s - 8, s - 8), WOOD, corner=6, depth=10)

    def straw(art, path):
        for _ in range(140):
            x, y = art.rng.uniform(20, s - 20), art.rng.uniform(20, s - 20)
            t = art.rng.uniform(0, 6.28)
            art.ink([(x, y), (x + 14 * math.cos(t), y + 14 * math.sin(t))], FINE * 1.1, color=shade(STRAW, art.rng.uniform(0.1, 0.5)), alpha=0.9, wob=0.2)
        art.shape(ellipse(90, 110, 22, 18, 28), rgb("#9fc0d0"), outline=DETAIL, depth=4, light_k=0.6)
        art.shape(ellipse(150, 140, 18, 18, 24), GLASS_G, outline=DETAIL, depth=3, light_k=0.6)

    a.shape(rect(28, 28, s - 28, s - 28), STRAW, outline=DETAIL * 1.2, corner=4, depth=10, shade_k=0, light_k=0, ao=0.4, detail=straw)
    return a.image()


def open_barrel(seed=105, fill=None):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    R = m - 8

    def staves(art, path):
        for i in range(18):
            ang = 2 * math.pi * i / 18
            art.ink([(m + (R - 22) * math.cos(ang), m + (R - 22) * math.sin(ang)), (m + R * math.cos(ang), m + R * math.sin(ang))], DETAIL * 0.8, color=shade(WOOD_DARK, 0.5), alpha=0.9, taper=False)

    a.shape(ellipse(m, m, R, R, 120), WOOD_DARK, depth=10, detail=staves)
    ring(a, m, m, R - 9, 8, IRON)
    a.ink(ellipse(m, m, R - 5, R - 5, 120), FINE, closed=True, wob=0.2)
    a.ink(ellipse(m, m, R - 13, R - 13, 120), FINE, closed=True, wob=0.2)
    inside = fill or (rgb("#5f8ea4"), None)
    a.shape(ellipse(m, m, R - 22, R - 22, 100), inside[0], outline=DETAIL * 1.2, depth=14, shade_k=0, light_k=0, ao=0.6, detail=inside[1])
    return a.image()


def water_barrel(seed=105):
    def ripples(art, path):
        art.ink([(70, 90), (100, 82), (130, 88)], FINE * 1.4, color=rgb("#dceff5"), alpha=0.9)
        art.ink([(110, 140), (140, 134)], FINE * 1.2, color=rgb("#dceff5"), alpha=0.8)

    return open_barrel(seed, (rgb("#5f8ea4"), ripples))


def apple_barrel(seed=106):
    return open_barrel(seed, (rgb("#4a3324"), lambda art, p: apples(art, 110, 110, 26, 60)))


def keg(seed=107):
    """A keg lying on its cradle, seen from above: flat heads at both ends,
    sides bulging out, staves running its length, iron hoops across."""
    w, h = 320, 230
    a = Art(w, h, seed)
    for x in (80, w - 80):
        a.shape(rect(x - 16, 10, x + 16, h - 10), WOOD_DARK, outline=DETAIL * 1.3, corner=5, depth=5)
    x0, x1 = 34, w - 44
    half = 76
    bulge = 22

    def edge(t, side):
        # side: -1 top edge, +1 bottom edge; the half-width bulges in the middle.
        y = h / 2 + side * (half - bulge + bulge * math.sin(math.pi * t))
        return (x0 + (x1 - x0) * t, y)

    top = [edge(j / 20, -1) for j in range(21)]
    bot = [edge(j / 20, 1) for j in range(21)][::-1]

    def staves(art, path):
        for k in range(1, 6):
            f = -1 + 2 * k / 6
            art.ink([(x0 + (x1 - x0) * j / 20, h / 2 + f * (half - bulge + bulge * math.sin(math.pi * j / 20))) for j in range(21)], DETAIL * 0.75, color=shade(WOOD, 0.5), alpha=0.85, taper=False)
        for t in (0.12, 0.3, 0.7, 0.88):
            hx, hy = edge(t, -1)
            art.ink([(hx, hy), (hx, h - hy)], DETAIL * 2.4, color=IRON, alpha=1, taper=False, wob=0.2)
            art.ink([(hx - 3, hy + 2), (hx - 3, h - hy - 2)], FINE, color=tint(IRON, 0.6), alpha=0.8, taper=False)

    a.shape(top + bot, WOOD, corner=4, depth=14, detail=staves)
    # The right head shows as a thin ellipse, with the tap.
    a.shape(ellipse(x1, h / 2, 9, half - bulge, 32), WOOD_LIGHT, outline=DETAIL * 1.2, depth=3, mottle=0)
    a.shape(rect(x1 + 6, h / 2 - 7, x1 + 32, h / 2 + 7), BRASS, outline=DETAIL, corner=3, depth=3, mottle=0)
    a.shape(rect(x1 + 24, h / 2 - 13, x1 + 32, h / 2 + 13), BRASS, outline=DETAIL, corner=2, depth=2, mottle=0)
    return a.image()


def sack_pile(seed=108):
    w, h = 380, 330
    a = Art(w, h, seed)
    from objects import sack

    for (x, y, s) in ((10, 110, 190), (170, 120, 180), (90, 10, 190)):
        img = sack(seed=a.rng.randint(0, 999)).resize((int(s * 180 / 220), s))
        a.c.drawImageRect(skia.Image.fromarray(__import__("numpy").asarray(img), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(x, y, img.width, img.height))
    return a.image(grain=0)


def grain_sack(seed=109):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m + 6, 92, a.rng, 10, 0.06), BURLAP, smooth=True, depth=12)
    a.ink(chaikin(blob(m, m, 62, a.rng, 9, 0.08), True, 2), DETAIL * 1.1, closed=True, color=shade(BURLAP, 0.5), alpha=0.9)

    def grain(art, path):
        for _ in range(160):
            ang, d = art.rng.uniform(0, 6.28), 58 * math.sqrt(art.rng.random())
            dot(art, m + d * math.cos(ang), m + d * math.sin(ang), art.rng.uniform(1.4, 2.4), rgb("#e8d79a"), 0.95)

    a.shape(blob(m, m, 60, a.rng, 9, 0.08), rgb("#cdb874"), outline=0, smooth=True, depth=8, shade_k=0.2, light_k=0, ao=0.5, detail=grain)
    return a.image()


def basket(seed=110, contents=None):
    s = 210
    a = Art(s, s, seed)
    m = s / 2
    wick = rgb("#b99258")

    def weave(art, path):
        for i in range(36):
            ang = 2 * math.pi * i / 36
            art.ink([(m + 70 * math.cos(ang), m + 70 * math.sin(ang)), (m + 96 * math.cos(ang + 0.05), m + 96 * math.sin(ang + 0.05))], FINE * 1.2, color=shade(wick, 0.5), alpha=0.8)

    a.shape(ellipse(m, m, m - 8, m - 8, 96), wick, depth=10, detail=weave)
    a.ink(ellipse(m, m, m - 30, m - 30, 96), DETAIL * 1.1, closed=True, color=shade(wick, 0.55))

    def inside(art, path):
        if contents:
            contents(art)
        else:
            for k in range(-4, 5):
                art.ink([(m + k * 14, 40), (m + k * 14, s - 40)], FINE, color=shade(wick, 0.5), alpha=0.6, taper=False)

    a.shape(ellipse(m, m, m - 32, m - 32, 96), shade(wick, 0.1), outline=DETAIL, depth=10, shade_k=0, light_k=0, ao=0.55, detail=inside)
    return a.image()


def apple_basket(seed=111):
    return basket(seed, lambda art: apples(art, 105, 105, 18, 52))


def urn(seed=112, body=CLAY):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, m - 10, m - 10, 80), body, depth=12, light_k=0.4, detail=lambda art, p: art.ink(ellipse(m, m, m - 26, m - 26, 72), FINE * 1.2, closed=True, color=shade(body, 0.45), alpha=0.7))
    a.shape(ellipse(m, m, 36, 36, 48), tint(body, 0.1), outline=DETAIL * 1.2, depth=5)
    a.shape(ellipse(m, m, 24, 24, 40), rgb("#3a2a22"), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.5)
    return a.image()


def amphora(seed=113):
    w, h = 170, 300
    a = Art(w, h, seed)
    # Lying on its side: body, neck and two handles.
    body = chaikin([(w / 2, h - 10), (w - 14, h - 90), (w - 22, 120), (w / 2 + 18, 70), (w / 2 - 18, 70), (22, 120), (14, h - 90)], True, 3)

    def bands(art, path):
        for y in (150, 175):
            art.ink([(20, y), (w - 20, y + 4)], DETAIL * 0.9, color=rgb("#3a2a22"), alpha=0.85)

    a.shape(body, CLAY, depth=12, light_k=0.4, detail=bands)
    a.shape(rect(w / 2 - 18, 22, w / 2 + 18, 78), CLAY, outline=DETAIL * 1.3, corner=6, depth=6)
    a.shape(ellipse(w / 2, 22, 24, 12, 32), tint(CLAY, 0.1), outline=DETAIL * 1.2, depth=4)
    for side in (-1, 1):
        a.ink([(w / 2 + side * 18, 46), (w / 2 + side * 46, 60), (w / 2 + side * 34, 96)], DETAIL * 1.6, color=shade(CLAY, 0.3))
    return a.image()


def jar(seed=114):
    s = 130
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, m - 10, m - 10, 64), rgb("#9fb8a8"), depth=8, light_k=0.6)
    a.shape(ellipse(m, m, 26, 26, 40), rgb("#b88a5a"), outline=DETAIL * 1.2, depth=4)
    a.ink([(m - 26, m), (m + 26, m)], FINE * 1.3, color=shade(rgb("#b88a5a"), 0.5), taper=False)
    return a.image()


def bucket(seed=115):
    s = 150
    a = Art(s, s, seed)
    m = s / 2

    def ripples(art, path):
        art.ink([(m - 22, m - 8), (m, m - 14), (m + 20, m - 8)], FINE * 1.3, color=rgb("#dceff5"))

    a.shape(ellipse(m, m, m - 10, m - 10, 72), WOOD, depth=8, detail=lambda art, p: [art.ink([(m + (m - 26) * math.cos(t), m + (m - 26) * math.sin(t)), (m + (m - 10) * math.cos(t), m + (m - 10) * math.sin(t))], DETAIL * 0.7, color=shade(WOOD, 0.5), taper=False) for t in [2 * math.pi * i / 14 for i in range(14)]])
    ring(a, m, m, m - 16, 6, IRON)
    a.shape(ellipse(m, m, m - 26, m - 26, 64), rgb("#5f8ea4"), outline=DETAIL, depth=8, shade_k=0, light_k=0, ao=0.6, detail=ripples)
    a.ink([(14, m), (m, 6), (s - 14, m)], DETAIL * 1.1, color=IRON, taper=False)
    return a.image()


def trough(seed=116):
    w, h = 512, 170
    a = Art(w, h, seed)
    a.shape(rect(8, 10, w - 8, h - 10), WOOD_DARK, corner=10, depth=10)

    def ripples(art, path):
        for x in (110, 260, 380):
            art.ink([(x, 70), (x + 30, 64), (x + 60, 70)], FINE * 1.4, color=rgb("#dceff5"), alpha=0.9)

    a.shape(rect(28, 30, w - 28, h - 30), rgb("#5f8ea4"), outline=DETAIL * 1.2, corner=6, depth=12, shade_k=0, light_k=0, ao=0.6, detail=ripples)
    return a.image()


def firewood(seed=117):
    """Split logs stacked lengthwise, seen from above: two layers, the top
    one lighter (nearer the light), sawn ends showing at the sides."""
    w, h = 420, 300
    a = Art(w, h, seed)
    bark = rgb("#7a5a3e")

    def log(y, x0, x1, r, col):
        def bark_lines(art, path):
            for k in range(3):
                yy = y - r * 0.5 + k * r * 0.5 + art.rng.uniform(-2, 2)
                xa = x0 + art.rng.uniform(10, 40)
                xb = x1 - art.rng.uniform(10, 40)
                art.ink([(xa, yy), ((xa + xb) / 2, yy + art.rng.uniform(-2, 2)), (xb, yy)], FINE * 1.1, color=shade(col, 0.5), alpha=0.75)

        a.shape(rect(x0, y - r, x1, y + r), col, outline=OUTLINE * 0.85, corner=r * 0.9, depth=r * 0.25, detail=bark_lines)
        for ex in (x0 + r * 0.45, x1 - r * 0.45):
            a.shape(ellipse(ex, y, r * 0.38, r * 0.85, 28), WOOD_LIGHT, outline=DETAIL, depth=2, mottle=0, shade_k=0.2, light_k=0.2)
            a.ink(ellipse(ex, y, r * 0.18, r * 0.42, 20), FINE, closed=True, color=shade(WOOD_LIGHT, 0.45), alpha=0.8)

    # Bottom layer, then the top layer resting in the gaps (lighter).
    for k in range(5):
        y = 46 + k * 52
        log(y, 20 + a.rng.uniform(-8, 8), w - 20 + a.rng.uniform(-8, 8), 26, vary(a.rng, shade(bark, 0.1), 0.05))
    for k in range(4):
        y = 72 + k * 52
        log(y, 40 + a.rng.uniform(-8, 8), w - 40 + a.rng.uniform(-8, 8), 25, vary(a.rng, bark, 0.05))
    return a.image()


# -- kitchen -----------------------------------------------------------------------------------


def kitchen_counter(seed=118):
    w, h = 640, 200
    a = Art(w, h, seed)
    board(a, 8, 8, w - 8, h - 8, WOOD_LIGHT, n=2, corner=8)
    # Cutting board with a knife, a bowl, some vegetables.
    a.shape(rect(60, 50, 210, 150), WOOD, outline=DETAIL * 1.2, corner=10, depth=5)
    a.shape(rect(90, 92, 190, 104), rgb("#c9ccd2"), outline=DETAIL, corner=3, depth=2, mottle=0)
    a.shape(rect(60, 92, 92, 104), WOOD_DARK, outline=DETAIL, corner=3, depth=2, mottle=0)
    vessel(a, 330, 100, 46, CERAMIC, rgb("#c9a061"), outline=DETAIL * 1.3)
    for x, y, c in ((450, 80, rgb("#e08a3a")), (480, 120, rgb("#e08a3a")), (520, 90, rgb("#8fb04a"))):
        a.shape(ellipse(x, y, 14, 9, 24, rot=0.6), c, outline=DETAIL, depth=3, mottle=0)
    return a.image()


def oven(seed=119):
    """A domed brick oven from above: courses of bricks in rings, a smoke
    hole on top, the arched mouth facing the room (bottom) with its glow."""
    s = 320
    a = Art(s, s, seed)
    m = s / 2
    brick = rgb("#b06a4e")
    cy = m - 16
    R = 130
    # The mouth's vault sticks out toward the viewer.
    a.shape(rect(m - 52, cy + R - 40, m + 52, s - 10), shade(brick, 0.1), corner=16, depth=8)

    def courses(art, path):
        for r in (36, 62, 88, 112):
            art.ink(ellipse(m, cy, r, r, 96), DETAIL * 0.8, closed=True, color=shade(brick, 0.5), alpha=0.85)
            n = int(r / 7)
            off = art.rng.uniform(0, 1)
            for k in range(n):
                t = 2 * math.pi * (k + off) / n
                art.ink([(m + r * math.cos(t), cy + r * math.sin(t)), (m + (r + 25) * math.cos(t), cy + (r + 25) * math.sin(t))], FINE * 1.1, color=shade(brick, 0.5), alpha=0.75, taper=False)

    a.shape(ellipse(m, cy, R, R, 120), brick, depth=16, light_k=0.35, detail=courses)
    a.shape(ellipse(m, cy, 22, 22, 32), rgb("#2c2420"), outline=DETAIL * 1.3, depth=6, shade_k=0, light_k=0, ao=0.5)
    a.shape(rect(m - 34, s - 44, m + 34, s - 10), rgb("#2c2420"), outline=DETAIL * 1.2, corner=10, depth=4, shade_k=0, light_k=0)
    glow = skia.Path()
    glow.addCircle(m, s - 22, 30)
    a.fill_path(glow, rgb("#ff9a3c"), 0.7, blur=10)
    return a.image()


def spit_roast(seed=120):
    w, h = 420, 220
    a = Art(w, h, seed)
    for x in (34, w - 34):
        a.shape(ellipse(x, h / 2, 16, 16, 24), WOOD_DARK, outline=DETAIL * 1.2, depth=4)
    a.ink([(30, h / 2), (w - 30, h / 2)], DETAIL * 1.6, color=IRON, taper=False)
    meat = rgb("#a8552f")

    def crisp(art, path):
        for x in range(130, 300, 22):
            art.ink([(x, h / 2 - 34), (x + 6, h / 2 + 34)], FINE * 1.3, color=shade(meat, 0.5), alpha=0.8)

    a.shape(ellipse(w / 2, h / 2, 100, 46, 64), meat, depth=10, light_k=0.5, detail=crisp)
    return a.image()


def cutting_board(seed=121):
    w, h = 260, 170
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), WOOD_LIGHT, corner=18, depth=6)
    bread = rgb("#c98d4f")
    a.shape(ellipse(100, 80, 60, 34, 48), bread, depth=8, detail=lambda art, p: [art.ink([(x, 56), (x + 10, 104)], FINE * 1.3, color=shade(bread, 0.5)) for x in (70, 95, 120)])
    cheese = rgb("#ecc85a")
    a.shape([(170, 50), (230, 70), (210, 130), (170, 120)], cheese, outline=DETAIL * 1.2, corner=6, depth=5)
    for x, y in ((190, 80), (205, 105)):
        a.shape(ellipse(x, y, 5, 4, 12), shade(cheese, 0.2), outline=FINE, depth=1, mottle=0, shade_k=0, light_k=0)
    return a.image()


def sink(seed=122):
    w, h = 300, 200
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), STONE, corner=14, depth=8)
    a.shape(rect(36, 36, w - 36, h - 36), rgb("#7aa3b4"), outline=DETAIL * 1.2, corner=30, depth=12, shade_k=0, light_k=0, ao=0.6)
    a.shape(rect(w / 2 - 10, 4, w / 2 + 10, 40), IRON, outline=DETAIL, corner=4, depth=3, mottle=0)
    return a.image()


def wine_rack(seed=123):
    """A wine rack from above: bottles lying side by side between the rack's
    rails, necks all pointing one way."""
    w, h = 400, 260
    a = Art(w, h, seed)
    a.shape(rect(8, 8, w - 8, h - 8), WOOD_DARK, corner=8, depth=8)
    a.shape(rect(26, 22, w - 26, h - 22), shade(WOOD_DARK, 0.35), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5)
    glass = [rgb("#3f5a3a"), rgb("#5a2a3a"), rgb("#4a5a2e")]
    for k in range(7):
        y = 44 + k * 29
        col = a.rng.choice(glass)
        body = rect(52, y - 12, 250, y + 12)
        a.shape(body, col, outline=DETAIL * 1.1, corner=11, depth=4, light_k=0.6, mottle=0)
        a.shape(rect(246, y - 6, 300, y + 6), col, outline=DETAIL, corner=5, depth=2, light_k=0.5, mottle=0)
        a.shape(rect(296, y - 6, 312, y + 6), rgb("#8a2f2f"), outline=FINE * 1.3, corner=3, depth=1, mottle=0)
        a.ink([(70, y - 6), (220, y - 6)], FINE * 1.2, color=tint(col, 0.6), alpha=0.8, taper=False)
    for x in (100, 200):
        a.shape(rect(x - 8, 14, x + 8, h - 14), WOOD, outline=DETAIL * 1.2, corner=3, depth=3)
    return a.image()


def mug(seed=124):
    s = 90
    a = Art(s, s, seed)
    m = s / 2
    a.shape(rect(s - 30, m - 9, s - 6, m + 9), WOOD, outline=DETAIL * 1.2, corner=8, depth=3)
    vessel(a, m - 6, m, 30, WOOD, rgb("#e8c873"), rim=0.75, outline=DETAIL * 1.4, fill_inside=lambda art, p: dot(art, m - 12, m - 6, 5, rgb("#fff4d6"), 0.9))
    return a.image()


def plate_food(seed=125):
    s = 160
    a = Art(s, s, seed)
    m = s / 2

    def food(art, path):
        art.shape(ellipse(m - 12, m - 6, 26, 18, 32, rot=0.4), rgb("#b5643a"), outline=DETAIL, depth=4, light_k=0.4)
        art.shape(ellipse(m + 22, m + 14, 14, 14, 24), rgb("#e0b24a"), outline=DETAIL, depth=3, mottle=0)
        for x, y in ((m + 8, m - 24), (m + 26, m - 10)):
            art.shape(ellipse(x, y, 8, 8, 16), rgb("#7ea74a"), outline=FINE * 1.3, depth=2, mottle=0)

    vessel(a, m, m, m - 8, CERAMIC, tint(CERAMIC, 0.2), rim=0.8, outline=DETAIL * 1.4, fill_inside=food)
    return a.image()


def bottle(seed=126, color=GLASS_G):
    s = 90
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 32, 32, 48), color, outline=DETAIL * 1.4, depth=5, light_k=0.7)
    a.shape(ellipse(m, m, 12, 12, 24), shade(color, 0.2), outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(m, m, 6, 6, 16), WOOD_LIGHT, outline=FINE, depth=1, mottle=0)
    return a.image()


def wine_bottle(seed=127):
    return bottle(seed, rgb("#5a2a3a"))


def goblet(seed=128):
    s = 90
    a = Art(s, s, seed)
    m = s / 2
    vessel(a, m, m, 30, GOLD, rgb("#7a2030"), rim=0.72, outline=DETAIL * 1.4)
    return a.image()


def soup_bowl(seed=129):
    s = 130
    a = Art(s, s, seed)
    m = s / 2

    def soup(art, path):
        for _ in range(6):
            ang, d = art.rng.uniform(0, 6.28), art.rng.uniform(0, 22)
            art.shape(ellipse(m + d * math.cos(ang), m + d * math.sin(ang), 6, 5, 12), rgb("#e08a3a"), outline=FINE, depth=1, mottle=0)

    vessel(a, m, m, m - 10, WOOD, rgb("#c99a4a"), rim=0.78, outline=DETAIL * 1.4, fill_inside=soup)
    return a.image()


def fruit_bowl(seed=130):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    vessel(a, m, m, m - 10, CERAMIC, tint(CERAMIC, 0.15), rim=0.82, outline=DETAIL * 1.5, fill_inside=lambda art, p: apples(art, m, m, 12, 56, kinds=("apple", "green", "pear")))
    return a.image()


def candle(seed=131):
    s = 80
    a = Art(s, s, seed)
    m = s / 2
    glow = skia.Path()
    glow.addCircle(m, m, 34)
    a.fill_path(glow, rgb("#ffd27a"), 0.35, blur=10)
    a.shape(ellipse(m, m, 18, 18, 32), WAX, outline=DETAIL * 1.3, depth=4)
    a.shape(scallop(m, m, 8, a.rng, 5, 0.2), rgb("#f6b444"), outline=FINE * 1.2, depth=1, mottle=0, shade_k=0, light_k=0)
    dot(a, m, m, 3, rgb("#fff4cf"))
    return a.image()


def candelabra(seed=132):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    for ang in (0, 2.09, 4.19):
        x, y = m + 60 * math.cos(ang), m + 60 * math.sin(ang)
        a.ink([(m, m), (x, y)], DETAIL * 2.2, color=shade(GOLD, 0.15))
    a.shape(ellipse(m, m, 20, 20, 32), GOLD, outline=DETAIL * 1.3, depth=4, light_k=0.5)
    for ang in (0, 2.09, 4.19):
        x, y = m + 60 * math.cos(ang), m + 60 * math.sin(ang)
        glow = skia.Path()
        glow.addCircle(x, y, 26)
        a.fill_path(glow, rgb("#ffd27a"), 0.35, blur=8)
        a.shape(ellipse(x, y, 16, 16, 28), WAX, outline=DETAIL * 1.2, depth=3)
        a.shape(scallop(x, y, 7, a.rng, 5, 0.2), rgb("#f6b444"), outline=FINE, depth=1, mottle=0, shade_k=0, light_k=0)
    return a.image()


def lantern(seed=133):
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    glow = skia.Path()
    glow.addCircle(m, m, 52)
    a.fill_path(glow, rgb("#ffd27a"), 0.35, blur=14)
    a.shape(rect(m - 34, m - 34, m + 34, m + 34), IRON, corner=8, depth=6)
    a.shape(rect(m - 24, m - 24, m + 24, m + 24), rgb("#ffe39a"), outline=DETAIL, corner=4, depth=4, shade_k=0, light_k=0.4)
    a.ink([(m - 24, m), (m + 24, m)], DETAIL, color=IRON, taper=False)
    a.ink([(m, m - 24), (m, m + 24)], DETAIL, color=IRON, taper=False)
    a.shape(ellipse(m, m - 34, 10, 6, 20), IRON, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def oil_lamp(seed=134):
    w, h = 140, 90
    a = Art(w, h, seed)
    body = rgb("#c9a061")
    a.shape(chaikin([(14, h / 2), (40, 16), (90, 18), (w - 14, h / 2 - 6), (w - 14, h / 2 + 6), (90, h - 18), (40, h - 16)], True, 2), body, depth=6)
    a.shape(ellipse(56, h / 2, 14, 14, 24), shade(body, 0.3), outline=DETAIL, depth=3, mottle=0, shade_k=0, light_k=0)
    a.shape(scallop(w - 16, h / 2, 9, a.rng, 5, 0.2), rgb("#f6b444"), outline=FINE * 1.2, depth=1, mottle=0, shade_k=0, light_k=0)
    return a.image()


def coin_pile(seed=135):
    s = 170
    a = Art(s, s, seed)
    coins(a, s / 2, s / 2, 70, 66)
    return a.image()


def coin_pouch(seed=136):
    s = 130
    a = Art(s, s, seed)
    m = s / 2
    leather = rgb("#8a5a3a")
    coins(a, m + 30, m + 30, 6, 20, r=8)
    a.shape(blob(m - 6, m + 4, 42, a.rng, 9, 0.08), leather, smooth=True, depth=8)
    a.shape(ellipse(m - 6, m - 34, 16, 10, 24), shade(leather, 0.15), outline=DETAIL * 1.2, depth=3)
    a.ink([(m - 22, m - 26), (m + 10, m - 26)], DETAIL * 1.2, color=rgb("#d8c08a"), taper=False)
    return a.image()


def potion(seed=137):
    s = 100
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 34, 34, 48), RED, outline=DETAIL * 1.4, depth=5, light_k=0.7)
    a.ink([(m - 18, m - 14), (m - 6, m - 24)], FINE * 2, color=(240, 230, 230))
    a.shape(ellipse(m, m, 12, 12, 24), rgb("#c9d6dc"), outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(m, m, 7, 7, 16), WOOD_LIGHT, outline=FINE, depth=1, mottle=0)
    return a.image()


def key_ring(seed=138):
    s = 150
    a = Art(s, s, seed)
    ring(a, 40, 40, 22, 6, IRON)
    a.ink(ellipse(40, 40, 25, 25, 32), FINE * 1.2, closed=True)
    for ang in (0.5, 1.1):
        x0, y0 = 40 + 22 * math.cos(ang), 40 + 22 * math.sin(ang)
        x1, y1 = x0 + 64 * math.cos(ang), y0 + 64 * math.sin(ang)
        a.ink([(x0, y0), (x1, y1)], DETAIL * 1.8, color=BRASS)
        a.shape(rect(x1 - 6, y1 - 6, x1 + 10, y1 + 10), BRASS, outline=DETAIL, corner=2, depth=2, mottle=0)
    return a.image()


STORAGE = {
    "Open Chest": open_chest,
    "Crate Stack": crate_stack,
    "Small Crate": small_crate,
    "Straw Crate": straw_crate,
    "Water Barrel": water_barrel,
    "Apple Barrel": apple_barrel,
    "Keg": keg,
    "Sack Pile": sack_pile,
    "Grain Sack": grain_sack,
    "Basket": basket,
    "Apple Basket": apple_basket,
    "Urn": urn,
    "Amphora": amphora,
    "Jar": jar,
    "Bucket": bucket,
    "Trough": trough,
    "Firewood": firewood,
    "Kitchen Counter": kitchen_counter,
    "Oven": oven,
    "Spit Roast": spit_roast,
    "Bread and Cheese": cutting_board,
    "Sink": sink,
    "Wine Rack": wine_rack,
    "Mug": mug,
    "Plate of Food": plate_food,
    "Bottle": bottle,
    "Wine Bottle": wine_bottle,
    "Goblet": goblet,
    "Soup Bowl": soup_bowl,
    "Fruit Bowl": fruit_bowl,
    "Candle": candle,
    "Candelabra": candelabra,
    "Lantern": lantern,
    "Oil Lamp": oil_lamp,
    "Coin Pile": coin_pile,
    "Coin Pouch": coin_pouch,
    "Potion": potion,
    "Key Ring": key_ring,
}

STORAGE_COLORABLE = {"Potion"}
