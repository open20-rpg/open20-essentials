"""Furniture (batch 1): tables, seats, beds, cabinets, rugs and the like."""

import math

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, cabinet, cushion, dot, grain_lines, scallop
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, vary

LINEN = rgb("#ece4d3")
PAGES = rgb("#ddcfae")
BOOKS = ["#8a3f37", "#3c5a78", "#55743f", "#9a7a37", "#694a6e", "#a85e34", "#2f6461", "#7b5a3c"]


def books_row(a, x0, y0, x1, y1):
    """Book spines and tops peeking out under a shelf."""
    x = x0
    while x < x1 - 8:
        bw = a.rng.uniform(12, 22)
        if a.rng.random() < 0.1:
            x += a.rng.uniform(8, 16)
            continue
        col = rgb(a.rng.choice(BOOKS))
        top = y0 - 10 + a.rng.uniform(0, 8)
        a.shape(rect(x, top, x + bw, y1 + 6), col, outline=DETAIL * 0.9, corner=2, wob=0.3, depth=3, shade_k=0.3, light_k=0.25, ao=0, mottle=0)
        a.ink([(x + 3, top + 10), (x + bw - 3, top + 10)], FINE, color=tint(col, 0.5), alpha=0.9, taper=False)
        x += bw + a.rng.uniform(0.5, 1.5)


def bookshelf(seed=10):
    w, h = 512, 170
    a = Art(w, h, seed)
    cabinet(a, 6, 8, w - 6, h - 8, WOOD_DARK, front=0.34, inside=books_row)
    return a.image()


def tall_shelf(seed=61):
    """Shelf of jars and bottles peeking out."""
    w, h = 384, 170
    a = Art(w, h, seed)

    def jars(art, x0, y0, x1, y1):
        x = x0 + 4
        cols = [rgb("#6f9fb5"), rgb("#8bb06a"), rgb("#c9a45a"), rgb("#b56a6a"), rgb("#d9d2c0")]
        while x < x1 - 20:
            r = art.rng.uniform(10, 16)
            art.shape(ellipse(x + r, y0 + r * 0.6, r, r * 0.9, 24), art.rng.choice(cols), outline=DETAIL, depth=4, mottle=0)
            x += 2 * r + art.rng.uniform(3, 9)

    cabinet(a, 6, 8, w - 6, h - 8, WOOD, front=0.34, inside=jars)
    return a.image()


def wardrobe(seed=62):
    w, h = 400, 210
    a = Art(w, h, seed)

    def doors(art, x0, y0, x1, y1):
        mx = (x0 + x1) / 2
        art.ink([(mx, y0 - 8), (mx, y1)], DETAIL, alpha=0.9, taper=False)
        for x in (mx - 14, mx + 14):
            dot(art, x, (y0 + y1) / 2 - 2, 4, BRASS)

    cabinet(a, 6, 8, w - 6, h - 8, WOOD_DARK, front=0.26, inside=doors, top_n=3)
    return a.image()


def dresser(seed=63):
    w, h = 360, 190
    a = Art(w, h, seed)

    def drawers(art, x0, y0, x1, y1):
        n = 3
        for k in range(1, n):
            x = x0 + (x1 - x0) * k / n
            art.ink([(x, y0 - 8), (x, y1)], DETAIL, alpha=0.9, taper=False)
        for k in range(n):
            dot(art, x0 + (x1 - x0) * (k + 0.5) / n, (y0 + y1) / 2 - 2, 4, BRASS)

    cabinet(a, 6, 8, w - 6, h - 8, WOOD, front=0.28, inside=drawers)
    # A small mirror stand and a candle on top.
    a.shape(ellipse(80, 60, 30, 22, 40), rgb("#b9d3dc"), outline=DETAIL * 1.2, depth=5, light_k=0.6)
    a.shape(ellipse(w - 70, 55, 10, 10, 20), rgb("#f1e6c8"), outline=DETAIL, depth=3, mottle=0)
    return a.image()


def nightstand(seed=64):
    s = 170
    a = Art(s, s, seed)

    def drawer(art, x0, y0, x1, y1):
        dot(art, (x0 + x1) / 2, (y0 + y1) / 2 - 2, 4, BRASS)

    cabinet(a, 8, 8, s - 8, s - 8, WOOD, front=0.3, inside=drawer, top_n=1)
    a.shape(ellipse(58, 52, 16, 16, 24), rgb("#d9c28a"), outline=DETAIL, depth=4)
    a.shape(ellipse(58, 52, 6, 6, 16), rgb("#fbf0c8"), outline=FINE, depth=2, mottle=0)
    return a.image()


def cabinet_obj(seed=65):
    w, h = 300, 190
    a = Art(w, h, seed)

    def doors(art, x0, y0, x1, y1):
        mx = (x0 + x1) / 2
        art.ink([(mx, y0 - 8), (mx, y1)], DETAIL, alpha=0.9, taper=False)
        dot(art, mx - 12, (y0 + y1) / 2 - 2, 3.5, IRON)
        dot(art, mx + 12, (y0 + y1) / 2 - 2, 3.5, IRON)

    cabinet(a, 6, 8, w - 6, h - 8, WOOD_LIGHT, front=0.28, inside=doors)
    return a.image()


def square_table(seed=66):
    s = 300
    a = Art(s, s, seed)
    board(a, 10, 10, s - 10, s - 10, WOOD, n=4, vertical=True, corner=10)
    return a.image()


def small_round_table(seed=67):
    s = 230
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, m - 10, m - 10, 80), WOOD_LIGHT, depth=10, detail=lambda art, p: boards(art, 0, 0, s, s, WOOD_LIGHT, 4, vertical=True))
    return a.image()


def side_table(seed=68):
    s = 170
    a = Art(s, s, seed)
    board(a, 12, 12, s - 12, s - 12, WOOD, n=2, corner=8)
    a.shape(ellipse(70, 70, 18, 18, 24), rgb("#d8d0c0"), outline=DETAIL, depth=4)
    a.shape(ellipse(70, 70, 10, 10, 20), rgb("#8a5a3a"), outline=FINE, depth=2, mottle=0, shade_k=0, light_k=0)
    return a.image()


def clothed_table(seed=69):
    w, h = 512, 280
    a = Art(w, h, seed)

    def folds(art, path):
        for x in range(40, w - 30, 70):
            art.ink([(x, h - 26), (x + 6, h - 6)], FINE * 1.2, color=shade(RED, 0.45), alpha=0.8)
            art.ink([(x, 26), (x + 6, 6)], FINE * 1.2, color=shade(RED, 0.45), alpha=0.8)

    a.shape(rect(6, 6, w - 6, h - 6), RED, corner=14, depth=10, detail=folds)
    a.ink(rect(26, 26, w - 26, h - 26), FINE * 1.3, closed=True, color=tint(RED, 0.45), alpha=0.9)
    for x, y in ((150, 110), (360, 170)):
        a.shape(ellipse(x, y, 30, 30, 32), rgb("#e4dccb"), outline=DETAIL, depth=4)
    a.shape(ellipse(255, 140, 12, 12, 20), rgb("#c9a640"), outline=DETAIL, depth=3)
    return a.image()


def armchair(seed=70):
    s = 240
    a = Art(s, s, seed)
    # Frame: back and arms, then the seat cushion (recolorable).
    a.shape(rect(14, 14, s - 14, s - 18), WOOD_DARK, corner=24, depth=10)
    cushion(a, 30, 22, s - 30, 70, RED, tufts=True)
    cushion(a, 20, 66, 56, s - 26, RED, tufts=False, corner=14)
    cushion(a, s - 56, 66, s - 20, s - 26, RED, tufts=False, corner=14)
    cushion(a, 56, 70, s - 56, s - 30, RED)
    return a.image()


def sofa(seed=71):
    w, h = 512, 220
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 14), WOOD_DARK, corner=26, depth=10)
    cushion(a, 26, 18, w - 26, 72, RED)
    cushion(a, 16, 62, 64, h - 24, RED, tufts=False, corner=16)
    cushion(a, w - 64, 62, w - 16, h - 24, RED, tufts=False, corner=16)
    cushion(a, 64, 70, w / 2, h - 28, RED)
    cushion(a, w / 2, 70, w - 64, h - 28, RED)
    return a.image()


def footstool(seed=72):
    s = 150
    a = Art(s, s, seed)
    a.shape(rect(12, 12, s - 12, s - 12), WOOD_DARK, corner=16, depth=6)
    cushion(a, 22, 22, s - 22, s - 22, RED)
    return a.image()


def throne(seed=73):
    w, h = 300, 300
    a = Art(w, h, seed)
    gold = rgb("#d6ae4c")
    back = [(30, 70), (60, 18), (w / 2, 6), (w - 60, 18), (w - 30, 70), (w - 30, 92), (30, 92)]
    a.shape(back, gold, corner=10, depth=10, light_k=0.5)
    for x in (60, w / 2, w - 60):
        a.shape(ellipse(x, 40 if x != w / 2 else 30, 9, 9, 20), rgb("#7aa6c9"), outline=DETAIL, depth=3, light_k=0.6, mottle=0)
    a.shape(rect(20, 86, 64, h - 16), gold, corner=14, depth=8, light_k=0.5)
    a.shape(rect(w - 64, 86, w - 20, h - 16), gold, corner=14, depth=8, light_k=0.5)
    cushion(a, 64, 90, w - 64, h - 24, RED)
    return a.image()


def pew(seed=74):
    w, h = 512, 150
    a = Art(w, h, seed)
    a.shape(rect(8, 10, w - 8, 44), WOOD_DARK, corner=8, depth=6)
    board(a, 8, 40, w - 8, h - 12, WOOD, n=2, corner=8)
    for x in (8, w - 30):
        a.shape(rect(x, 10, x + 22, h - 10), WOOD_DARK, outline=DETAIL * 1.4, corner=6, depth=5)
    return a.image()


def double_bed(seed=75):
    w, h = 470, 520
    a = Art(w, h, seed)
    a.shape(rect(8, 8, w - 8, h - 8), WOOD_DARK, corner=12, depth=10)
    a.shape(rect(24, 50, w - 24, h - 22), LINEN, outline=DETAIL * 1.3, corner=12, depth=8)
    board(a, 8, 8, w - 8, 46, WOOD, n=1, corner=10)
    for x0 in (44, w / 2 + 8):
        a.shape(rect(x0, 62, x0 + w / 2 - 52, 140), rgb("#f5f0e5"), outline=DETAIL * 1.3, corner=26, depth=9)

    def folds(art, path):
        for y, x0, x1 in ((290, 60, 200), (370, 220, 400), (450, 70, 260)):
            art.ink([(x0, y), ((x0 + x1) / 2, y + 7), (x1, y - 2)], FINE * 1.2, color=shade(RED, 0.45), alpha=0.8)

    a.shape(rect(20, 180, w - 20, h - 18), RED, outline=DETAIL * 1.4, corner=12, depth=10, detail=folds)
    a.shape(rect(20, 180, w - 20, 224), tint(RED, 0.25), outline=DETAIL * 1.2, corner=6, depth=6)
    return a.image()


def bedroll(seed=76):
    w, h = 200, 470
    a = Art(w, h, seed)

    def stitch(art, path):
        art.ink([(30, 30), (30, h - 30)], FINE, color=tint(RED, 0.45), alpha=0.8, taper=False)
        art.ink([(w - 30, 30), (w - 30, h - 30)], FINE, color=tint(RED, 0.45), alpha=0.8, taper=False)

    a.shape(rect(16, 70, w - 16, h - 12), RED, corner=30, depth=10, detail=stitch)
    # Rolled-up head end and a small pillow.
    a.shape(rect(10, 12, w - 10, 80), shade(RED, 0.15), corner=34, depth=8)
    for x in (50, w / 2, w - 50):
        a.ink([(x, 18), (x, 74)], FINE * 1.2, color=shade(RED, 0.5), alpha=0.8)
    a.shape(rect(40, 96, w - 40, 160), LINEN, outline=DETAIL * 1.2, corner=20, depth=6)
    return a.image()


def round_rug(seed=77):
    s = 520
    a = Art(s, s, seed)
    m = s / 2
    cream = rgb("#e6d29f")

    def pattern(art, path):
        for r, col in ((m - 44, cream), (m - 58, RED), (m * 0.5, cream), (m * 0.4, shade(RED, 0.2)), (m * 0.16, cream)):
            art.shape(ellipse(m, m, r, r, 96), col, outline=DETAIL, depth=3, mottle=0.02, shade_k=0.15, light_k=0)
        for i in range(12):
            ang = 2 * math.pi * i / 12
            x, y = m + m * 0.66 * math.cos(ang), m + m * 0.66 * math.sin(ang)
            art.shape([(x, y - 14), (x + 14, y), (x, y + 14), (x - 14, y)], cream, outline=DETAIL * 0.9, corner=2, depth=2, mottle=0, shade_k=0, light_k=0)

    a.shape(ellipse(m, m, m - 20, m - 20, 120), RED, depth=8, detail=pattern, shade_k=0.3, light_k=0.15)
    return a.image()


def runner_rug(seed=78):
    w, h = 768, 240
    a = Art(w, h, seed)
    cream = rgb("#e6d29f")
    for y in range(28, h - 22, 13):
        a.ink([(20, y), (4, y + a.rng.uniform(-2, 2))], FINE * 1.2, color=shade(cream, 0.3))
        a.ink([(w - 20, y), (w - 4, y + a.rng.uniform(-2, 2))], FINE * 1.2, color=shade(cream, 0.3))

    def pattern(art, path):
        art.ink(rect(40, 36, w - 40, h - 36), DETAIL, closed=True, color=cream, alpha=0.95, wob=0.3)
        for x in range(90, w - 60, 90):
            art.shape([(x, h / 2 - 34), (x + 34, h / 2), (x, h / 2 + 34), (x - 34, h / 2)], cream, outline=DETAIL * 0.9, corner=2, depth=2, mottle=0, shade_k=0.15, light_k=0)
            art.shape([(x, h / 2 - 14), (x + 14, h / 2), (x, h / 2 + 14), (x - 14, h / 2)], shade(RED, 0.25), outline=FINE, corner=1, depth=1, mottle=0, shade_k=0, light_k=0)

    a.shape(rect(18, 16, w - 18, h - 16), RED, corner=4, depth=8, detail=pattern, shade_k=0.3, light_k=0.15)
    return a.image()


def bearskin_rug(seed=79):
    w, h = 420, 520
    a = Art(w, h, seed)
    fur = rgb("#7a5a40")
    m = w / 2
    body = [(m, 40), (m + 60, 90), (m + 160, 120), (m + 120, 200), (m + 110, 330), (m + 180, 430), (m + 70, 420), (m, 480), (m - 70, 420), (m - 180, 430), (m - 110, 330), (m - 120, 200), (m - 160, 120), (m - 60, 90)]

    def fur_lines(art, path):
        for _ in range(70):
            x, y = art.rng.uniform(60, w - 60), art.rng.uniform(80, h - 60)
            if path.contains(x, y):
                t = math.atan2(y - 260, x - m)
                art.ink([(x, y), (x + 9 * math.cos(t), y + 9 * math.sin(t))], FINE, color=shade(fur, 0.5), alpha=0.6, wob=0.1)

    a.shape(chaikin(body, True, 2), fur, depth=12, detail=fur_lines)
    a.shape(ellipse(m, 70, 46, 52, 40), shade(fur, 0.1), outline=DETAIL * 1.4, depth=8)
    for dx in (-30, 30):
        a.shape(ellipse(m + dx, 32, 12, 12, 20), fur, outline=DETAIL, depth=3, mottle=0)
    dot(a, m - 15, 66, 3.5)
    dot(a, m + 15, 66, 3.5)
    a.shape(ellipse(m, 100, 12, 9, 20), rgb("#3a2a22"), outline=FINE, depth=2, mottle=0)
    return a.image()


def fireplace(seed=80):
    w, h = 400, 220
    a = Art(w, h, seed)
    # Stone hearth with the fire pit opening toward the room (bottom).
    stones = []
    x = 8
    while x < w - 10:
        bw = a.rng.uniform(46, 70)
        stones.append((x, min(w - 8, x + bw)))
        x += bw
    for x0, x1 in stones:
        a.shape(rect(x0 + 2, 8, x1 - 2, 70), vary(a.rng, STONE, 0.06), outline=DETAIL * 1.3, corner=8, depth=6)
    a.shape(rect(8, 66, 70, h - 10), STONE, corner=8, depth=8)
    a.shape(rect(w - 70, 66, w - 8, h - 10), STONE, corner=8, depth=8)
    a.shape(rect(70, 70, w - 70, h - 14), rgb("#3c322d"), outline=DETAIL * 1.3, corner=6, depth=10, shade_k=0, light_k=0, ao=0.6)
    for x0, x1 in ((110, 250), (170, 300)):
        a.shape(rect(x0, 130, x1, 152), WOOD_DARK, outline=DETAIL, corner=10, depth=4)
    for r, col in ((40, rgb("#e9773a")), (26, rgb("#f4b544")), (12, rgb("#fde8a6"))):
        a.shape(scallop(w / 2, 140, r, a.rng, 6, 0.22), col, outline=DETAIL if r > 20 else 0, depth=3, shade_k=0.2, light_k=0, ao=0, mottle=0)
    return a.image()


def bathtub(seed=81):
    w, h = 470, 250
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), WOOD, corner=90, depth=10, detail=lambda art, p: boards(art, 0, 0, w, h, WOOD, 8, vertical=True, grain=False))
    a.ink([(20, h * 0.35), (w - 20, h * 0.35)], DETAIL * 1.4, color=IRON, alpha=0.9, taper=False)
    a.ink([(20, h * 0.65), (w - 20, h * 0.65)], DETAIL * 1.4, color=IRON, alpha=0.9, taper=False)

    def ripples(art, path):
        for x0, y in ((140, 100), (260, 150), (330, 95)):
            art.ink([(x0, y), (x0 + 30, y - 5), (x0 + 60, y)], FINE * 1.3, color=rgb("#e4f2f6"), alpha=0.9)

    a.shape(rect(36, 34, w - 36, h - 34), rgb("#8fbfd0"), outline=DETAIL * 1.2, corner=70, depth=12, shade_k=0, light_k=0, ao=0.6, detail=ripples)
    return a.image()


def folding_screen(seed=82):
    w, h = 512, 110
    a = Art(w, h, seed)
    panels = 4
    pw = (w - 20) / panels
    for k in range(panels):
        x = 10 + k * pw
        y = 20 if k % 2 == 0 else 40
        a.shape(rect(x, y, x + pw, y + 50), WOOD_DARK, corner=4, depth=5)
        a.shape(rect(x + 10, y + 12, x + pw - 10, y + 38), RED, outline=DETAIL, corner=3, depth=4, mottle=0)
    return a.image()


def bar_counter(seed=83):
    w, h = 768, 200
    a = Art(w, h, seed)
    board(a, 8, 8, w - 8, h - 8, WOOD_DARK, n=2, corner=10)
    a.ink([(16, 46), (w - 16, 46)], DETAIL * 1.1, color=shade(WOOD_DARK, 0.5), alpha=0.9, taper=False)
    for x in (120, 200, 420, 610):
        a.shape(ellipse(x, 110, 16, 16, 24), rgb("#c9a061"), outline=DETAIL, depth=4)
        a.shape(ellipse(x, 110, 10, 10, 20), rgb("#f2e3b8"), outline=FINE, depth=2, mottle=0, shade_k=0, light_k=0)
    a.shape(ellipse(320, 120, 14, 14, 24), rgb("#4f7a52"), outline=DETAIL, depth=3, light_k=0.6)
    return a.image()


def desk(seed=84):
    w, h = 420, 230
    a = Art(w, h, seed)
    board(a, 8, 8, w - 8, h - 8, WOOD, n=3, corner=8)
    a.shape([(70, 60), (210, 50), (220, 160), (80, 172)], rgb("#efe5cc"), outline=DETAIL, corner=3, depth=4)
    for y in (82, 100, 118, 136):
        a.ink([(96, y), (198, y - 6)], FINE, color=shade(PAGES, 0.5), alpha=0.7, taper=False)
    a.shape(ellipse(300, 80, 14, 14, 24), rgb("#3a3a46"), outline=DETAIL, depth=4)
    a.ink([(300, 80), (360, 30)], FINE * 1.6, color=rgb("#f1ece2"))
    a.shape(rect(270, 130, 370, 190), rgb("#5b3f63"), outline=DETAIL, corner=4, depth=4)
    a.shape(rect(276, 136, 364, 184), PAGES, outline=FINE, corner=2, depth=2, mottle=0)
    return a.image()


FURNITURE = {
    "Bookshelf": bookshelf,
    "Potion Shelf": tall_shelf,
    "Wardrobe": wardrobe,
    "Dresser": dresser,
    "Nightstand": nightstand,
    "Cabinet": cabinet_obj,
    "Square Table": square_table,
    "Small Round Table": small_round_table,
    "Side Table": side_table,
    "Clothed Table": clothed_table,
    "Armchair": armchair,
    "Sofa": sofa,
    "Footstool": footstool,
    "Throne": throne,
    "Pew": pew,
    "Double Bed": double_bed,
    "Bedroll": bedroll,
    "Round Rug": round_rug,
    "Runner Rug": runner_rug,
    "Bearskin Rug": bearskin_rug,
    "Fireplace": fireplace,
    "Bathtub": bathtub,
    "Folding Screen": folding_screen,
    "Bar Counter": bar_counter,
    "Desk": desk,
}

FURNITURE_COLORABLE = {"Clothed Table", "Armchair", "Sofa", "Footstool", "Throne", "Double Bed", "Bedroll", "Round Rug", "Runner Rug", "Folding Screen"}
