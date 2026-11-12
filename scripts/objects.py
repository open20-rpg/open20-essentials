"""The built-in pack's objects, drawn top-down (light from the top-left).
256 px = 1 map tile. Colorable parts are painted in pure red (g == b): the
editor recolors them with the object's color, as Dungeondraft does."""

import math

from ink import INK, Canvas, blob, darker, lighter, mix, rect, rgb, rounded

WOOD = rgb("#9a6c43")
WOOD_DARK = rgb("#6e4a2f")
WOOD_LIGHT = rgb("#b98a57")
IRON = rgb("#5a5c63")
STONE = rgb("#a19c94")
RED = (196, 44, 44)  # colorable region: g == b
LEAF = rgb("#5f8c3e")


def grain(c, x0, y0, x1, y1, n, col, horizontal=True):
    for _ in range(n):
        if horizontal:
            y = c.rng.uniform(y0 + 4, y1 - 4)
            x = c.rng.uniform(x0 + 6, x0 + (x1 - x0) * 0.5)
            c.line([(x, y), (x + (x1 - x0) * c.rng.uniform(0.2, 0.45), y + c.rng.uniform(-1, 1))], 1.0, col, 150)
        else:
            x = c.rng.uniform(x0 + 4, x1 - 4)
            y = c.rng.uniform(y0 + 6, y0 + (y1 - y0) * 0.5)
            c.line([(x, y), (x + c.rng.uniform(-1, 1), y + (y1 - y0) * c.rng.uniform(0.2, 0.45))], 1.0, col, 150)


def round_table(seed=1):
    s = 360
    c = Canvas(s, s, seed)
    m = s / 2
    c.ellipse(m, m, m - 6, m - 6, WOOD, 2.6, 0.2, 0.12)
    c.ellipse(m, m, m - 24, m - 24, WOOD_LIGHT, 1.4, 0.0, 0.0, outline=True)
    c.ellipse(m, m, m - 26, m - 26, WOOD, 0, 0, 0, outline=False)
    for k in range(5):
        r = 30 + k * 26
        a0 = c.rng.uniform(0, 6.28)
        c.line([(m + r * math.cos(a0 + t / 20), m + r * math.sin(a0 + t / 20)) for t in range(0, 22)], 1.0, darker(WOOD, 0.4), 140)
    return c.result()


def rect_table(seed=2):
    w, h = 512, 256
    c = Canvas(w, h, seed)
    c.shape(rounded(8, 8, w - 8, h - 8, 10), WOOD, 2.6, 0.2, 0.12)
    planks = 4
    ph = (h - 16) / planks
    for i in range(1, planks):
        c.line([(10, 8 + i * ph), (w - 10, 8 + i * ph)], 1.4, darker(WOOD, 0.5), 220)
    grain(c, 8, 8, w - 8, h - 8, 12, darker(WOOD, 0.4))
    # A runner down the middle (colorable).
    c.shape(rect(w * 0.18, h * 0.38, w * 0.82, h * 0.62), RED, 1.8, 0.14, 0.14)
    for x in range(int(w * 0.18) + 10, int(w * 0.82) - 4, 14):
        c.line([(x, h * 0.62), (x, h * 0.62 + 7)], 1.0, INK, 160, wobble=False)
        c.line([(x, h * 0.38), (x, h * 0.38 - 7)], 1.0, INK, 160, wobble=False)
    return c.result()


def chair(seed=3):
    s = 150
    c = Canvas(s, s, seed)
    c.shape(rounded(22, 34, s - 22, s - 16, 8), WOOD, 2.2, 0.2, 0.12)
    c.shape(rounded(16, 12, s - 16, 34, 6), WOOD_DARK, 2.2, 0.2, 0.1)
    grain(c, 22, 34, s - 22, s - 16, 3, darker(WOOD, 0.4), horizontal=False)
    return c.result()


def stool(seed=4):
    s = 120
    c = Canvas(s, s, seed)
    c.ellipse(s / 2, s / 2, s / 2 - 8, s / 2 - 8, WOOD, 2.2, 0.22, 0.12)
    c.ellipse(s / 2, s / 2, s / 2 - 24, s / 2 - 24, WOOD_LIGHT, 1.0, 0, 0)
    return c.result()


def bench(seed=5):
    w, h = 512, 120
    c = Canvas(w, h, seed)
    c.shape(rounded(6, 20, w - 6, h - 20, 8), WOOD, 2.4, 0.2, 0.12)
    c.line([(8, h / 2), (w - 8, h / 2)], 1.4, darker(WOOD, 0.5), 220)
    grain(c, 6, 20, w - 6, h - 20, 8, darker(WOOD, 0.4))
    return c.result()


def bed(seed=6):
    w, h = 300, 512
    c = Canvas(w, h, seed)
    c.shape(rounded(6, 6, w - 6, h - 6, 10), WOOD_DARK, 2.6, 0.2, 0.1)
    c.shape(rounded(20, 22, w - 20, h - 20, 12), rgb("#efe7d6"), 2.0, 0.14, 0.1)
    c.shape(rounded(40, 36, w - 40, 120, 26), rgb("#f6f1e6"), 2.0, 0.18, 0.12)
    c.line([(70, 78), (110, 74)], 1.0, darker(rgb("#f6f1e6"), 0.3), 160)
    # Blanket (colorable), folded back at the top.
    c.shape(rounded(18, 150, w - 18, h - 18, 12), RED, 2.2, 0.18, 0.12)
    c.shape(rect(18, 150, w - 18, 186), lighter(RED, 0.25), 2.0, 0.1, 0.1)
    for y in (240, 330, 420):
        c.line([(30, y), (w - 30, y + c.rng.uniform(-4, 4))], 1.0, darker(RED, 0.35), 140)
    return c.result()


def chest(seed=7):
    w, h = 256, 170
    c = Canvas(w, h, seed)
    c.shape(rounded(8, 10, w - 8, h - 10, 10), WOOD, 2.6, 0.22, 0.12)
    for x in (34, w - 34):
        c.shape(rect(x - 9, 10, x + 9, h - 10), IRON, 2.0, 0.2, 0.14)
        for y in (24, h / 2, h - 24):
            c.ellipse(x, y, 2.2, 2.2, lighter(IRON, 0.3), 1.0, 0, 0)
    c.line([(44, h / 2), (w - 44, h / 2)], 1.6, darker(WOOD, 0.5), 220)
    c.shape(rounded(w / 2 - 16, h / 2 - 12, w / 2 + 16, h / 2 + 18, 4), rgb("#c9a640"), 2.0, 0.2, 0.2)
    c.ellipse(w / 2, h / 2 + 3, 3, 4, INK, 1.0, 0, 0)
    return c.result()


def crate(seed=8):
    s = 230
    c = Canvas(s, s, seed)
    c.shape(rect(8, 8, s - 8, s - 8), WOOD_LIGHT, 2.6, 0.22, 0.12)
    for i in range(1, 4):
        c.line([(10, 8 + i * (s - 16) / 4), (s - 10, 8 + i * (s - 16) / 4)], 1.2, darker(WOOD_LIGHT, 0.5), 200)
    c.shape(rect(8, 8, s - 8, 30), WOOD, 2.0, 0.2, 0.1)
    c.shape(rect(8, s - 30, s - 8, s - 8), WOOD, 2.0, 0.2, 0.1)
    c.shape([(26, s - 30), (s - 46, 30), (s - 26, 30), (46, s - 30)], WOOD, 2.0, 0.2, 0.1)
    for x, y in ((18, 19), (s - 18, 19), (18, s - 19), (s - 18, s - 19)):
        c.ellipse(x, y, 2.2, 2.2, INK, 1.0, 0, 0)
    return c.result()


def barrel(seed=9):
    s = 200
    c = Canvas(s, s, seed)
    m = s / 2
    c.ellipse(m, m, m - 8, m - 8, WOOD, 2.6, 0.24, 0.12)
    c.ellipse(m, m, m - 22, m - 22, IRON, 2.0, 0, 0)
    c.ellipse(m, m, m - 30, m - 30, WOOD_LIGHT, 1.6, 0.18, 0.1)
    for i in range(-2, 3):
        x = m + i * 24
        half = math.sqrt(max(0, (m - 32) ** 2 - (x - m) ** 2))
        c.line([(x, m - half + 4), (x, m + half - 4)], 1.1, darker(WOOD_LIGHT, 0.45), 190)
    c.ellipse(m + 20, m - 10, 5, 5, darker(WOOD, 0.3), 1.2, 0, 0)
    return c.result()


def bookshelf(seed=10):
    w, h = 512, 130
    c = Canvas(w, h, seed)
    c.shape(rect(6, 8, w - 6, h - 8), WOOD_DARK, 2.6, 0.2, 0.1)
    x = 18
    palette = ["#7a3b33", "#33506e", "#4e6b3a", "#8a6a2f", "#5b3f63", "#a0522d", "#2f5d5a"]
    while x < w - 26:
        bw = c.rng.uniform(10, 20)
        col = rgb(c.rng.choice(palette))
        depth = c.rng.uniform(0.62, 0.86)
        c.shape(rect(x, 18, x + bw, 18 + (h - 36) * depth), col, 1.4, 0.18, 0.15)
        c.line([(x + 2, 26), (x + bw - 2, 26)], 1.0, lighter(col, 0.5), 170, wobble=False)
        x += bw + (c.rng.uniform(1, 3) if c.rng.random() < 0.85 else 18)
    return c.result()


def rug(seed=11):
    w, h = 512, 768
    c = Canvas(w, h, seed)
    c.shape(rect(16, 16, w - 16, h - 16), RED, 2.4, 0.12, 0.12)
    c.shape(rect(44, 44, w - 44, h - 44), rgb("#e2cf9c"), 1.8, 0.0, 0.0)
    c.shape(rect(58, 58, w - 58, h - 58), RED, 1.8, 0.0, 0.0)
    cx, cy = w / 2, h / 2
    c.shape([(cx, cy - 190), (cx + 120, cy), (cx, cy + 190), (cx - 120, cy)], rgb("#e2cf9c"), 1.8, 0.0, 0.0)
    c.shape([(cx, cy - 110), (cx + 70, cy), (cx, cy + 110), (cx - 70, cy)], darker(RED, 0.35), 1.6, 0.0, 0.0)
    for x, y in ((100, 100), (w - 100, 100), (100, h - 100), (w - 100, h - 100)):
        c.shape([(x, y - 22), (x + 22, y), (x, y + 22), (x - 22, y)], rgb("#e2cf9c"), 1.4, 0, 0)
    # Fringes.
    for x in range(26, w - 20, 12):
        c.line([(x, 16), (x, 2)], 1.2, rgb("#d9c48e"), 255, wobble=False)
        c.line([(x, h - 16), (x, h - 2)], 1.2, rgb("#d9c48e"), 255, wobble=False)
    return c.result()


def cauldron(seed=12):
    s = 220
    c = Canvas(s, s, seed)
    m = s / 2
    for a in (math.pi * 0.25, math.pi * 1.25):
        c.ellipse(m + (m - 14) * math.cos(a), m + (m - 14) * math.sin(a), 10, 10, IRON, 2.0, 0.2, 0.1)
    c.ellipse(m, m, m - 16, m - 16, rgb("#3e4045"), 2.6, 0.25, 0.16)
    c.ellipse(m, m, m - 32, m - 32, rgb("#6fae4f"), 2.0, 0.1, 0.3)
    for _ in range(7):
        a, r = c.rng.uniform(0, 6.28), c.rng.uniform(0, m - 48)
        rr = c.rng.uniform(4, 9)
        c.ellipse(m + r * math.cos(a), m + r * math.sin(a), rr, rr, rgb("#9bd27a"), 1.2, 0, 0.3)
    return c.result()


def campfire(seed=13):
    s = 300
    c = Canvas(s, s, seed)
    m = s / 2
    n = 11
    for i in range(n):
        a = 2 * math.pi * i / n
        c.shape(blob(m + 112 * math.cos(a), m + 112 * math.sin(a), 22, c.rng, 10, 0.2), mix(STONE, rgb("#8d887f"), c.rng.random()), 2.0, 0.26, 0.14)
    c.ellipse(m, m, 84, 84, rgb("#5b5049"), 1.4, 0, 0)
    for a in (0.3, 1.4, 2.5):
        x0, y0 = m + 78 * math.cos(a), m + 78 * math.sin(a)
        x1, y1 = m - 40 * math.cos(a), m - 40 * math.sin(a)
        nx, ny = -math.sin(a) * 12, math.cos(a) * 12
        c.shape([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], WOOD_DARK, 2.0, 0.22, 0.1)
    c.shape(blob(m, m, 52, c.rng, 14, 0.3), rgb("#e8792f"), 2.0, 0.0, 0.25)
    c.shape(blob(m, m, 30, c.rng, 12, 0.3), rgb("#f6c14a"), 1.4, 0.0, 0.3)
    c.shape(blob(m, m, 12, c.rng, 10, 0.3), rgb("#fff1b8"), 0, 0, 0, outline=False)
    return c.result()


def anvil(seed=14):
    w, h = 300, 150
    c = Canvas(w, h, seed)
    c.shape(rect(90, 30, 240, h - 30), rgb("#6c4b33"), 2.2, 0.2, 0.1)
    pts = [(30, h / 2), (80, 42), (250, 36), (282, 46), (282, h - 46), (250, h - 36), (80, h - 42)]
    c.shape(pts, IRON, 2.6, 0.26, 0.2)
    c.line([(110, h / 2 - 12), (250, h / 2 - 14)], 1.2, lighter(IRON, 0.45), 200)
    c.ellipse(232, h / 2, 6, 6, darker(IRON, 0.4), 1.2, 0, 0)
    return c.result()


def well(seed=15):
    s = 330
    c = Canvas(s, s, seed)
    m = s / 2
    c.ellipse(m, m, m - 12, m - 12, rgb("#8d877e"), 2.6, 0.2, 0.1)
    n = 16
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        r0, r1 = m - 60, m - 14
        pts = [(m + r * math.cos(a), m + r * math.sin(a)) for r, a in ((r0, a0), (r1, a0), (r1, a1), (r0, a1))]
        c.shape(pts, mix(STONE, rgb("#b8b3aa"), c.rng.random()), 1.6, 0.2, 0.12)
    c.ellipse(m, m, m - 62, m - 62, rgb("#2c4b5c"), 2.0, 0.3, 0.0)
    c.ellipse(m - 14, m - 14, 22, 8, rgb("#5f8ba0"), 0, 0, 0, outline=False)
    c.shape(rect(m - 10, 4, m + 10, s - 4), WOOD_DARK, 2.0, 0.2, 0.1)
    c.ellipse(m, m, 14, 14, WOOD, 1.6, 0.2, 0.1)
    return c.result()


def tree(seed=16):
    s = 700
    c = Canvas(s, s, seed)
    m = s / 2
    # Canopy: a ring of leaf clusters around a center, darker inside.
    for i in range(14):
        a = 2 * math.pi * i / 14 + c.rng.uniform(-0.1, 0.1)
        r = c.rng.uniform(200, 240)
        c.shape(blob(m + r * math.cos(a), m + r * math.sin(a), c.rng.uniform(80, 105), c.rng, 16, 0.12), mix(LEAF, rgb("#4f7a33"), c.rng.random()), 2.4, 0.22, 0.12)
    c.shape(blob(m, m, 250, c.rng, 30, 0.06), LEAF, 0, 0.25, 0.1, outline=False)
    for i in range(8):
        a = 2 * math.pi * i / 8 + 0.3
        r = c.rng.uniform(80, 140)
        c.shape(blob(m + r * math.cos(a), m + r * math.sin(a), c.rng.uniform(70, 95), c.rng, 14, 0.14), mix(rgb("#6c9a47"), rgb("#78a653"), c.rng.random()), 2.2, 0.22, 0.14)
    c.shape(blob(m - 10, m - 10, 80, c.rng, 14, 0.14), rgb("#82b05c"), 2.2, 0.18, 0.16)
    # Leaf ticks.
    c.strokes(260, (60, 60, s - 60, s - 60), (5, 10), (-1.5, 1.5), 1.2, darker(LEAF, 0.45), 150, mask_fn=lambda x, y: math.hypot(x - m, y - m) < 290)
    return c.result()


def bush(seed=17):
    s = 300
    c = Canvas(s, s, seed)
    m = s / 2
    for i in range(7):
        a = 2 * math.pi * i / 7
        c.shape(blob(m + 70 * math.cos(a), m + 70 * math.sin(a), c.rng.uniform(46, 58), c.rng, 12, 0.14), mix(LEAF, rgb("#557f37"), c.rng.random()), 2.2, 0.22, 0.12)
    c.shape(blob(m, m, 70, c.rng, 14, 0.14), rgb("#6e9d49"), 2.2, 0.2, 0.15)
    c.strokes(70, (40, 40, s - 40, s - 40), (4, 8), (-1.5, 1.5), 1.1, darker(LEAF, 0.45), 150, mask_fn=lambda x, y: math.hypot(x - m, y - m) < 110)
    for _ in range(5):
        a, r = c.rng.uniform(0, 6.28), c.rng.uniform(10, 90)
        c.ellipse(m + r * math.cos(a), m + r * math.sin(a), 6, 6, rgb("#c2453c"), 1.2, 0.1, 0.3)
    return c.result()


def rock(seed=18):
    s = 260
    c = Canvas(s, s, seed)
    m = s / 2
    pts = blob(m, m, 100, c.rng, 9, 0.22)
    c.shape(pts, STONE, 2.6, 0.3, 0.18)
    # Facets.
    c.line([(m - 40, m - 30), (m + 5, m - 10), (m + 50, m - 40)], 1.3, darker(STONE, 0.45), 200)
    c.line([(m + 5, m - 10), (m + 10, m + 50)], 1.3, darker(STONE, 0.45), 200)
    c.dots(30, (m - 70, m - 70, m + 70, m + 70), darker(STONE, 0.5), (0.6, 1.2), 140)
    return c.result()


def sack(seed=19):
    w, h = 170, 210
    c = Canvas(w, h, seed)
    body = rgb("#c9ad7c")
    c.shape(blob(w / 2, h / 2 + 18, 66, c.rng, 14, 0.08), body, 2.4, 0.24, 0.12)
    c.shape([(w / 2 - 22, 26), (w / 2 + 22, 26), (w / 2 + 14, 70), (w / 2 - 14, 70)], body, 2.0, 0.18, 0.12)
    c.line([(w / 2 - 18, 62), (w / 2 + 18, 62)], 2.2, rgb("#7a5a35"))
    for a in (-0.6, 0.2, 0.9):
        c.line([(w / 2 + 10 * a, 80), (w / 2 + 50 * a, 150)], 1.0, darker(body, 0.4), 150)
    return c.result()


def potted_plant(seed=20):
    s = 200
    c = Canvas(s, s, seed)
    m = s / 2
    c.ellipse(m, m, 58, 58, rgb("#b8643f"), 2.4, 0.22, 0.12)
    c.ellipse(m, m, 46, 46, rgb("#5a4030"), 1.4, 0, 0)
    for i in range(7):
        a = 2 * math.pi * i / 7 + c.rng.uniform(-0.2, 0.2)
        L = c.rng.uniform(62, 84)
        tip = (m + L * math.cos(a), m + L * math.sin(a))
        nx, ny = -math.sin(a) * 16, math.cos(a) * 16
        mid = (m + L * 0.5 * math.cos(a), m + L * 0.5 * math.sin(a))
        c.shape([(m, m), (mid[0] + nx, mid[1] + ny), tip, (mid[0] - nx, mid[1] - ny)], mix(LEAF, rgb("#78a653"), c.rng.random()), 1.8, 0.18, 0.14)
        c.line([(m, m), tip], 1.0, darker(LEAF, 0.4), 160)
    return c.result()


OBJECTS = {
    "Round Table": round_table,
    "Long Table": rect_table,
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
