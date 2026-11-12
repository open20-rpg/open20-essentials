"""Religion and temple (batch 8). Top-down, same pen style."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, coin, cushion, dot, fruit, pile, scallop, soft_shadow
from obj_magic import GOLD, candle, glow, open_book
from obj_stone import DARK_STONE, GREY, LIGHT_STONE, MARBLE, stone_block
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

WATER = rgb("#7aa3b4")
CLOTH_GOLD = rgb("#e2c068")
SMOKE = rgb("#d8d4cc")


# -- altars & offerings ---------------------------------------------------------------------------


def offering_altar(seed=701):
    w, h = 420, 240
    a = Art(w, h, seed)
    stone_block(a, rect(10, 10, w - 10, h - 10), DARK_STONE, corner=8, cracks=1)
    stone_block(a, rect(28, 28, w - 28, h - 28), LIGHT_STONE, outline=DETAIL * 1.3, corner=6, light_k=0.4, cracks=0)
    # A runner (colorable) down the middle with gold edging.
    a.shape(rect(w / 2 - 60, 22, w / 2 + 60, h - 22), RED, outline=DETAIL * 1.2, corner=3, depth=5, mottle=0.03)
    for y in (36, h - 36):
        a.ink([(w / 2 - 50, y), (w / 2 + 50, y)], DETAIL, color=CLOTH_GOLD, taper=False)
    # Offerings: a gold chalice, fruit, coins, candles.
    a.shape(ellipse(w / 2, h / 2, 22, 22, 32), GOLD, outline=DETAIL * 1.2, depth=4, light_k=0.5)
    a.shape(ellipse(w / 2, h / 2, 13, 13, 24), rgb("#7a2030"), outline=FINE * 1.2, depth=2, shade_k=0, light_k=0, mottle=0)
    for x, y in ((90, 80), (110, 160)):
        fruit(a, x, y, 0.8, "apple")
    pile(a, 320, 150, 26, 12, lambda art, x, y, hh: coin(art, x, y, hh, 8))
    for x, y in ((60, 50), (w - 60, 50), (60, h - 50), (w - 60, h - 50)):
        candle(a, x, y, 12)
    return a.image()


def offering_table(seed=702):
    w, h = 360, 200
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD_DARK, n=2, corner=8)
    # Bowls of fruit and bread, a jug, flowers.
    for cx, cy in ((90, 100), (250, 90)):
        soft_shadow(a, (cx, cy), 50, 4, 5)
        a.shape(ellipse(cx, cy, 50, 50, 56), rgb("#e4dccb"), outline=DETAIL * 1.3, depth=4)
        pile(a, cx, cy, 36, 8, lambda art, x, y, hh: fruit(art, x, y, hh))
    bread = rgb("#c98d4f")
    a.shape(ellipse(170, 150, 34, 20, 40), bread, outline=DETAIL * 1.2, depth=5, light_k=0.4, detail=lambda art, p: [art.ink([(x, 136), (x + 8, 164)], FINE * 1.3, color=shade(bread, 0.5)) for x in (150, 168, 186)])
    a.shape(ellipse(320, 150, 18, 18, 28), rgb("#b98a5a"), outline=DETAIL * 1.2, depth=3, mottle=0)
    a.shape(ellipse(320, 150, 8, 8, 16), rgb("#2a221e"), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def offering_bowl(seed=703):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 60, 4, 5)
    a.shape(ellipse(m, m, 60, 60, 64), BRASS, outline=DETAIL * 1.4, depth=6, light_k=0.5)
    a.shape(ellipse(m, m, 46, 46, 56), shade(BRASS, 0.3), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.5)
    pile(a, m, m, 34, 16, lambda art, x, y, hh: coin(art, x, y, hh, 8))
    return a.image()


def reliquary(seed=704):
    w, h = 220, 160
    a = Art(w, h, seed)
    a.shape(rect(10, 12, w - 10, h - 12), GOLD, corner=10, depth=10, light_k=0.5)

    def deco(art, p):
        art.ink(rect(26, 28, w - 26, h - 28), DETAIL, closed=True, color=shade(GOLD, 0.45))
        for x, y, c in ((w / 2, h / 2, rgb("#c8443a")), (50, 40, rgb("#4f8fd0")), (w - 50, 40, rgb("#4f8fd0")), (50, h - 40, rgb("#4f8fd0")), (w - 50, h - 40, rgb("#4f8fd0"))):
            art.shape([(x, y - 9), (x + 9, y), (x, y + 9), (x - 9, y)], c, outline=FINE * 1.3, corner=1, depth=2, light_k=0.7, mottle=0)
        art.ink([(w / 2, 34), (w / 2, h - 34)], DETAIL * 1.4, color=tint(GOLD, 0.4))
        art.ink([(w / 2 - 24, h / 2 - 16), (w / 2 + 24, h / 2 - 16)], DETAIL * 1.4, color=tint(GOLD, 0.4))

    a.shape(rect(18, 20, w - 18, h - 20), tint(GOLD, 0.08), outline=DETAIL * 1.2, corner=6, depth=4, light_k=0.4, detail=deco)
    return a.image()


def sun_altar(seed=705):
    s = 360
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, ellipse(m, m, 168, 168, 96), GREY, cracks=1)
    # A sun mosaic: rays of gold and terracotta tiles around a gold disc.
    for k in range(16):
        t0, t1 = 2 * math.pi * k / 16, 2 * math.pi * (k + 0.5) / 16
        col = GOLD if k % 2 == 0 else rgb("#c06a45")
        tip = 150 if k % 2 == 0 else 120
        ray = [(m + 60 * math.cos(t0 - 0.1), m + 60 * math.sin(t0 - 0.1)), (m + tip * math.cos((t0 + t1) / 2 - 0.1), m + tip * math.sin((t0 + t1) / 2 - 0.1)), (m + 60 * math.cos(t1 - 0.1), m + 60 * math.sin(t1 - 0.1))]
        a.shape(ray, col, outline=DETAIL, corner=2, depth=3, light_k=0.3, mottle=0.05)
    a.shape(ellipse(m, m, 62, 62, 64), GOLD, outline=DETAIL * 1.4, depth=6, light_k=0.6)
    a.ink(ellipse(m, m, 44, 44, 56), FINE * 1.3, closed=True, color=shade(GOLD, 0.45))
    return a.image()


# -- furnishings -----------------------------------------------------------------------------------


def lectern(seed=711):
    w, h = 220, 200
    a = Art(w, h, seed)
    # Slanted top (seen from above: a wide board), the post's foot behind.
    a.shape(rect(70, 140, 150, 190), WOOD_DARK, outline=DETAIL * 1.2, corner=8, depth=4)
    board(a, 20, 20, w - 20, 150, WOOD, n=2, corner=8)
    open_book(a, w / 2, 86, 0.95)
    a.shape(rect(w / 2 - 3, 40, w / 2 + 3, 140), rgb("#a8483a"), outline=FINE, corner=1, depth=1, mottle=0)
    return a.image()


def kneeler(seed=712):
    w, h = 360, 120
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, 52, WOOD_DARK, n=1, corner=6)  # armrest board
    a.shape(rect(20, 58, w - 20, h - 10), WOOD, corner=6, depth=6)
    cushion(a, 32, 64, w - 32, h - 16, RED, tufts=False)
    return a.image()


def prayer_mat(seed=713):
    w, h = 300, 460
    a = Art(w, h, seed)
    cream = rgb("#e6d29f")
    for x in range(26, w - 20, 12):
        a.ink([(x, h - 18), (x, h - 4)], FINE * 1.2, color=shade(cream, 0.3))

    def pattern(art, p):
        art.ink(rect(34, 34, w - 34, h - 34), DETAIL, closed=True, color=cream, wob=0.3)
        # A niche (arch) at the head end, a lamp motif under it.
        arch = chaikin([(70, 230), (70, 120), (w / 2, 60), (w - 70, 120), (w - 70, 230)], False, 3)
        art.ink(arch, DETAIL * 1.2, color=cream)
        art.shape(ellipse(w / 2, 150, 16, 22, 28), cream, outline=FINE * 1.2, depth=2, shade_k=0, light_k=0, mottle=0)
        for k in range(5):
            y = 280 + k * 30
            art.shape([(w / 2, y - 12), (w / 2 + 12, y), (w / 2, y + 12), (w / 2 - 12, y)], cream, outline=FINE * 1.1, corner=1, depth=1, mottle=0, shade_k=0, light_k=0)

    a.shape(rect(18, 18, w - 18, h - 18), RED, corner=4, depth=8, detail=pattern, shade_k=0.3, light_k=0.15)
    return a.image()


def floor_banner(seed=714):
    """A temple banner laid out on the floor (colorable cloth, gold fringe)."""
    w, h = 220, 480
    a = Art(w, h, seed)
    cloth = chaikin([(20, 20), (w - 20, 20), (w - 20, h - 80), (w / 2, h - 20), (20, h - 80)], True, 1)

    def emblem(art, p):
        art.ink(rect(34, 34, w - 34, h - 110), FINE * 1.4, closed=True, color=CLOTH_GOLD)
        art.shape(ellipse(w / 2, 180, 50, 50, 48), CLOTH_GOLD, outline=DETAIL, depth=3, light_k=0.4, mottle=0)
        art.ink([(w / 2, 140), (w / 2, 220)], DETAIL * 1.6, color=shade(RED, 0.2))
        art.ink([(w / 2 - 30, 172), (w / 2 + 30, 172)], DETAIL * 1.6, color=shade(RED, 0.2))

    a.shape(cloth, RED, corner=0, depth=8, detail=emblem)
    a.shape(rect(6, 8, w - 6, 26), WOOD_DARK, outline=DETAIL * 1.3, corner=8, depth=4)
    return a.image()


def temple_bench(seed=715):
    w, h = 520, 140
    a = Art(w, h, seed)
    a.shape(rect(8, 12, w - 8, 46), WOOD_DARK, corner=6, depth=6)  # back
    board(a, 8, 42, w - 8, h - 12, WOOD, n=2, corner=8)
    for x in (8, w / 2 - 12, w - 32):
        a.shape(rect(x, 12, x + 24, h - 12), WOOD_DARK, outline=DETAIL * 1.3, corner=6, depth=5)
    return a.image()


def tabernacle(seed=716):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, rect(14, 14, s - 14, s - 14), MARBLE, corner=6, cracks=0, light_k=0.4)
    # Its little dome from above, gold cross on top.
    a.shape(ellipse(m, m, 70, 70, 64), GOLD, outline=DETAIL * 1.4, depth=10, light_k=0.55)
    for r in (50, 30):
        a.ink(ellipse(m, m, r, r, 48), FINE * 1.2, closed=True, color=shade(GOLD, 0.45))
    a.ink([(m, m - 24), (m, m + 24)], DETAIL * 2, color=tint(GOLD, 0.4))
    a.ink([(m - 16, m - 6), (m + 16, m - 6)], DETAIL * 2, color=tint(GOLD, 0.4))
    return a.image()


# -- ritual objects --------------------------------------------------------------------------------


def censer(seed=721):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 44, 4, 5)
    a.shape(ellipse(m, m, 44, 44, 48), BRASS, outline=DETAIL * 1.4, depth=6, light_k=0.5, detail=lambda art, p: [dot(art, m + 30 * math.cos(t), m + 30 * math.sin(t), 4, shade(BRASS, 0.5)) for t in [2 * math.pi * k / 10 for k in range(10)]])
    a.shape(ellipse(m, m, 14, 14, 20), BRASS, outline=DETAIL, depth=2, mottle=0)
    # Smoke curling up and away.
    for k in range(3):
        pts = [(m - 14 + 14 * k + 18 * math.sin(t * 2.2 + k * 1.3), m - 10 - t * 15) for t in [j / 2 for j in range(12)]]
        pts = chaikin(pts, False, 2)
        a.ink(pts, DETAIL * 3.6, color=shade(SMOKE, 0.25), alpha=0.5, wob=0.3)
        a.ink(pts, DETAIL * 2.2, color=tint(SMOKE, 0.3), alpha=0.85, wob=0.3)
    return a.image()


def baptismal_font(seed=722):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    octa = [(m + 136 * math.cos(t), m + 136 * math.sin(t)) for t in [math.pi / 8 + math.pi / 4 * i for i in range(8)]]
    stone_block(a, octa, MARBLE, corner=6, cracks=0, light_k=0.4)
    a.ink([(m + 116 * math.cos(t), m + 116 * math.sin(t)) for t in [math.pi / 8 + math.pi / 4 * i for i in range(8)]], FINE * 1.3, closed=True, color=shade(MARBLE, 0.4))

    def ripples(art, p):
        for r in (40, 70):
            art.ink([(m + r * math.cos(t), m + r * math.sin(t)) for t in [0.5 + j * 0.08 for j in range(10)]], FINE * 1.3, color=rgb("#e4f2f6"), alpha=0.85)

    a.shape(ellipse(m, m, 96, 96, 80), WATER, outline=DETAIL * 1.3, depth=12, shade_k=0, light_k=0, ao=0.6, detail=ripples)
    return a.image()


def holy_water(seed=723):
    s = 170
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, scallop(m, m, 70, a.rng, 8, 0.12), MARBLE, corner=0, cracks=0, light_k=0.45)
    a.shape(ellipse(m, m, 44, 44, 48), WATER, outline=DETAIL * 1.2, depth=8, shade_k=0, light_k=0, ao=0.6)
    glow(a, m, m, 40, rgb("#cfeaf2"), 0.35)
    return a.image()


def temple_bell(seed=724):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    # A big bell hanging from its yoke, seen from above: the crown and the
    # bell's shoulders, the yoke beam across.
    a.shape(ellipse(m, m, 84, 84, 72), BRASS, depth=12, light_k=0.5, detail=lambda art, p: [art.ink(ellipse(m, m, r, r, 64), FINE * 1.3, closed=True, color=shade(BRASS, 0.45), alpha=0.8) for r in (60, 70)])
    a.shape(rect(10, m - 14, s - 10, m + 14), WOOD_DARK, outline=DETAIL * 1.3, corner=6, depth=5)
    a.shape(ellipse(m, m, 24, 24, 32), tint(BRASS, 0.12), outline=DETAIL * 1.2, depth=4, light_k=0.5)
    return a.image()


def gong(seed=725):
    w, h = 300, 140
    a = Art(w, h, seed)
    # A gong in its frame, seen from above: the frame's top bar and posts,
    # the gong's edge as a narrow ellipse hanging under it.
    for x in (20, w - 20):
        a.shape(rect(x - 14, 20, x + 14, h - 20), WOOD_DARK, outline=DETAIL * 1.3, corner=5, depth=5)
    a.shape(rect(8, h / 2 - 12, w - 8, h / 2 + 12), WOOD_DARK, outline=DETAIL * 1.3, corner=6, depth=4)
    a.shape(ellipse(w / 2, h / 2 + 14, 110, 22, 64), BRASS, outline=DETAIL * 1.3, depth=4, light_k=0.55)
    a.shape(ellipse(w / 2, h / 2 + 14, 30, 7, 32), tint(BRASS, 0.2), outline=FINE, depth=1, mottle=0)
    return a.image()


def votive_rack(seed=726):
    w, h = 360, 180
    a = Art(w, h, seed)
    a.shape(rect(8, 10, w - 8, h - 10), IRON, corner=8, depth=8)
    a.shape(rect(20, 22, w - 20, h - 22), shade(IRON, 0.3), outline=DETAIL, corner=4, depth=4, shade_k=0, light_k=0, ao=0.4)
    for row in range(3):
        for k in range(7):
            x, y = 50 + k * 44 + (22 if row % 2 else 0), 46 + row * 44
            if x > w - 30:
                continue
            a.shape(ellipse(x, y, 14, 14, 20), rgb("#c84a3a"), outline=DETAIL, depth=2, mottle=0)
            candle(a, x, y, 9, lit=a.rng.random() < 0.75)
    return a.image()


def tall_candelabrum(seed=727):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    for t in [2 * math.pi * k / 5 + 0.3 for k in range(5)]:
        x, y = m + 70 * math.cos(t), m + 70 * math.sin(t)
        a.ink([(m, m), (x, y)], DETAIL * 3, color=INK, taper=False)
        a.ink([(m, m), (x, y)], DETAIL * 1.8, color=IRON, taper=False)
    a.shape(ellipse(m, m, 22, 22, 32), IRON, outline=DETAIL * 1.3, depth=4, light_k=0.5)
    for t in [2 * math.pi * k / 5 + 0.3 for k in range(5)]:
        x, y = m + 70 * math.cos(t), m + 70 * math.sin(t)
        a.shape(ellipse(x, y, 16, 16, 24), IRON, outline=DETAIL, depth=2, mottle=0)
        candle(a, x, y, 11)
    return a.image()


# -- idols & shrines -------------------------------------------------------------------------------


def goddess_statue(seed=733):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, ellipse(m, m, 116, 116, 80), DARK_STONE, cracks=1)

    def folds(art, p):
        for dx in (-50, -20, 20, 50):
            art.ink([(m + dx * 0.6, m), (m + dx, m + 70)], FINE * 1.3, color=shade(MARBLE, 0.4), alpha=0.8)

    a.shape(ellipse(m, m + 20, 80, 60, 64), shade(MARBLE, 0.04), depth=10, light_k=0.3, detail=folds)
    # Arms raised forward holding a bowl.
    for side in (-1, 1):
        arm = chaikin([(m + side * 54, m - 16), (m + side * 30, m - 40), (m + side * 14, m - 54), (m + side * 6, m - 46), (m + side * 22, m - 26), (m + side * 40, m - 4)], True, 2)
        a.shape(arm, tint(MARBLE, 0.1), outline=DETAIL * 1.2, corner=0, depth=4, light_k=0.4)
    a.shape(ellipse(m, m - 62, 22, 14, 28), tint(MARBLE, 0.12), outline=DETAIL * 1.2, depth=3, light_k=0.4)
    a.shape(ellipse(m, m - 8, 28, 28, 40), tint(MARBLE, 0.16), outline=DETAIL * 1.4, depth=6, light_k=0.5)
    a.ink(chaikin([(m - 26, m - 4), (m - 18, m + 22), (m - 6, m + 30)], False, 2), FINE * 1.3, color=shade(MARBLE, 0.4), alpha=0.8)
    a.ink(chaikin([(m + 26, m - 4), (m + 18, m + 22), (m + 6, m + 30)], False, 2), FINE * 1.3, color=shade(MARBLE, 0.4), alpha=0.8)
    return a.image()


def wayside_shrine(seed=734):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    # A little roofed shrine from above: a hip roof of wooden shingles, its
    # ridge line, an offering shelf peeking out in front.
    a.shape(rect(m - 40, s - 70, m + 40, s - 14), WOOD_LIGHT, outline=DETAIL * 1.2, corner=4, depth=4)
    candle(a, m - 18, s - 40, 9)
    a.shape(ellipse(m + 18, s - 40, 10, 10, 20), rgb("#c84a3a"), outline=DETAIL, depth=2, mottle=0)
    roof = rect(24, 24, s - 24, s - 74)
    rc = rgb("#8a5a3a")
    a.shape(roof, rc, corner=6, depth=10, light_k=0.3, detail=lambda art, p: [art.ink([(24, y), (s - 24, y)], FINE * 1.1, color=shade(rc, 0.5), alpha=0.7, taper=False) for y in range(40, s - 74, 16)])
    a.ink([(24, 24), (m - 40, (24 + s - 74) / 2), (24, s - 74)], DETAIL * 1.2)
    a.ink([(s - 24, 24), (m + 40, (24 + s - 74) / 2), (s - 24, s - 74)], DETAIL * 1.2)
    a.ink([(m - 40, (24 + s - 74) / 2), (m + 40, (24 + s - 74) / 2)], DETAIL * 1.6)
    return a.image()


TEMPLE = {
    "Offering Altar": offering_altar,
    "Offering Table": offering_table,
    "Offering Bowl": offering_bowl,
    "Reliquary": reliquary,
    "Sun Altar": sun_altar,
    "Lectern": lectern,
    "Kneeler": kneeler,
    "Prayer Mat": prayer_mat,
    "Floor Banner": floor_banner,
    "Temple Bench": temple_bench,
    "Tabernacle": tabernacle,
    "Censer": censer,
    "Baptismal Font": baptismal_font,
    "Holy Water Basin": holy_water,
    "Temple Bell": temple_bell,
    "Gong": gong,
    "Votive Candles": votive_rack,
    "Tall Candelabrum": tall_candelabrum,
    "Goddess Statue": goddess_statue,
    "Wayside Shrine": wayside_shrine,
}

TEMPLE_COLORABLE = {"Offering Altar", "Kneeler", "Prayer Mat", "Floor Banner"}
