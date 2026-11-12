"""Tavern & feast, library & study, and treasure (batch 13). Top-down, same
pen style (red = colorable)."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, coin, cushion, dot, fruit, pile, scallop, soft_shadow
from obj_craft import handle
from obj_magic import GLASS, PARCH, candle, flask, glow, open_book, roll
from obj_storage import coins
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

GOLD = rgb("#e2b84e")
SILVER = rgb("#c7ccd4")
PEWTER = rgb("#9aa0a6")
CERAMIC = rgb("#e4dccb")
ALE = rgb("#e0b04a")
WINE = rgb("#7a2030")
BREAD = rgb("#c98d4f")
ROAST = rgb("#b5643a")
CHEESE = rgb("#ecc85a")
PAGES = rgb("#ddcfae")
INKC = rgb("#1f1c24")
BOOKS = ["#8a3f37", "#3c5a78", "#55743f", "#9a7a37", "#694a6e", "#a85e34", "#2f6461", "#7b5a3c"]
GEMS = [rgb("#d0465a"), rgb("#5fb0d8"), rgb("#7ccf8a"), rgb("#a86ad0"), rgb("#f2d24a")]
VELVET = rgb("#6a2a3a")


# -- small table items (drawn into any art) --------------------------------------------------------


def mug_at(a, x, y, r=22, liquid=ALE, body=WOOD, ang=0.0):
    hx, hy = x + (r + 8) * math.cos(ang), y + (r + 8) * math.sin(ang)
    a.shape(ellipse(hx, hy, 9, 7, 16, rot=ang), body, outline=DETAIL, depth=2, mottle=0)
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r, 32), body, outline=DETAIL * 1.3, depth=3, light_k=0.4, mottle=0)
    a.shape(ellipse(x, y, r * 0.74, r * 0.74, 28), liquid, outline=FINE * 1.2, depth=2, shade_k=0, light_k=0.3, ao=0.3, mottle=0)
    if liquid == ALE:
        dot(a, x - r * 0.25, y - r * 0.25, r * 0.22, rgb("#fff4d6"), 0.9)


def plate_at(a, x, y, r=34, food=None):
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r, 40), CERAMIC, outline=DETAIL * 1.3, depth=3, mottle=0)
    a.ink(ellipse(x, y, r * 0.72, r * 0.72, 36), FINE, closed=True, color=shade(CERAMIC, 0.3), alpha=0.7)
    if food == "meat":
        a.shape(ellipse(x - 4, y - 2, r * 0.5, r * 0.34, 28, rot=0.4), ROAST, outline=DETAIL, depth=3, light_k=0.4, mottle=0)
        a.shape(ellipse(x + r * 0.4, y + r * 0.3, r * 0.18, r * 0.18, 16), rgb("#7ea74a"), outline=FINE * 1.2, depth=1, mottle=0)
    elif food == "bread":
        a.shape(ellipse(x, y, r * 0.55, r * 0.36, 28, rot=-0.3), BREAD, outline=DETAIL, depth=3, light_k=0.4, mottle=0)
    elif food == "stew":
        a.shape(ellipse(x, y, r * 0.6, r * 0.6, 28), rgb("#9a5a2a"), outline=FINE * 1.2, depth=1, shade_k=0, light_k=0.2, ao=0.3, mottle=0)
        for _ in range(4):
            dot(a, x + a.rng.uniform(-r * 0.35, r * 0.35), y + a.rng.uniform(-r * 0.35, r * 0.35), 3, rgb("#e08a3a"))


def cards_at(a, x, y, n=5, spread=1.0):
    for k in range(n):
        t = a.rng.uniform(-0.6, 0.6)
        cx, cy = x + a.rng.uniform(-20, 20) * spread, y + a.rng.uniform(-14, 14) * spread
        c, s = math.cos(t), math.sin(t)
        pts = [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-11, -16), (11, -16), (11, 16), (-11, 16))]
        a.shape(pts, rgb("#f3eee2"), outline=FINE * 1.3, corner=2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.shape([(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-4, -6), (4, -6), (4, 6), (-4, 6))], rgb("#a8483a") if k % 2 else rgb("#2a2a30"), outline=0, corner=1, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)


def die_at(a, x, y, s=12, pips=None):
    t = a.rng.uniform(0, 1.5)
    c, sn = math.cos(t), math.sin(t)
    pts = [(x + dx * c - dy * sn, y + dx * sn + dy * c) for dx, dy in ((-s, -s), (s, -s), (s, s), (-s, s))]
    soft_shadow(a, pts, dx=2, dy=3, alpha=0.3, blur=2)
    a.shape(pts, rgb("#f3eee2"), outline=FINE * 1.4, corner=3, depth=1.5, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    n = pips or a.rng.randint(1, 6)
    spots = {1: [(0, 0)], 2: [(-0.5, -0.5), (0.5, 0.5)], 3: [(-0.5, -0.5), (0, 0), (0.5, 0.5)], 4: [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)], 5: [(-0.5, -0.5), (0.5, -0.5), (0, 0), (-0.5, 0.5), (0.5, 0.5)], 6: [(-0.5, -0.6), (0.5, -0.6), (-0.5, 0), (0.5, 0), (-0.5, 0.6), (0.5, 0.6)]}[n]
    for px, py in spots:
        dx, dy = px * s, py * s
        dot(a, x + dx * c - dy * sn, y + dx * sn + dy * c, s * 0.16, INKC)


def bottle_at(a, x, y, color=rgb("#3f5a3a"), r=16):
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r, 28), color, outline=DETAIL * 1.3, depth=3, light_k=0.6, mottle=0)
    a.shape(ellipse(x, y, r * 0.4, r * 0.4, 16), shade(color, 0.2), outline=FINE, depth=1, mottle=0)
    dot(a, x, y, r * 0.22, rgb("#b88a5a"))


def goblet_at(a, x, y, r=16, metal=GOLD, liquid=WINE):
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r, 28), metal, outline=DETAIL * 1.3, depth=3, light_k=0.5, mottle=0)
    a.shape(ellipse(x, y, r * 0.66, r * 0.66, 24), liquid, outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)


def inkwell_at(a, x, y):
    soft_shadow(a, (x, y), 13, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, 13, 13, 24), INKC, outline=DETAIL * 1.2, depth=2, light_k=0.5, mottle=0)
    dot(a, x - 3, y - 3, 3, rgb("#5a5a6a"))
    # Quill standing in it, leaning out.
    a.ink([(x, y), (x + 60, y - 48)], DETAIL * 1.6, color=INK, taper=True)
    vane = chaikin([(x + 14, y - 8), (x + 30, y - 34), (x + 56, y - 52), (x + 66, y - 50), (x + 52, y - 28), (x + 30, y - 12)], True, 2)
    a.shape(vane, rgb("#f2efe6"), outline=DETAIL, corner=0, depth=1, mottle=0)
    a.ink([(x + 12, y - 8), (x + 62, y - 50)], FINE, color=shade(rgb("#f2efe6"), 0.4))


def paper_at(a, x, y, w=60, h=80, ang=0.0, lines=True, color=PARCH):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(x + dx * c - dy * s, y + dx * s + dy * c) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    soft_shadow(a, pts, dx=3, dy=4, alpha=0.3, blur=3)

    def ln(art, p):
        if lines:
            for k in range(int(h / 12) - 1):
                dy = -h / 2 + 12 + k * 11
                art.ink([(x + (-w / 2 + 8) * c - dy * s, y + (-w / 2 + 8) * s + dy * c), (x + (w / 2 - 8 - art.rng.uniform(0, 12)) * c - dy * s, y + (w / 2 - 8) * s + dy * c)], FINE * 0.9, color=shade(color, 0.5), alpha=0.7, wob=0.1)

    a.shape(pts, color, outline=DETAIL, corner=2, depth=2, shade_k=0.2, light_k=0.2, detail=ln)


def book_at(a, x, y, w=70, h=96, ang=0.0, color=None):
    color = color or rgb(a.rng.choice(BOOKS))
    c, s = math.cos(ang), math.sin(ang)
    rot = lambda pts: [(x + dx * c - dy * s, y + dx * s + dy * c) for dx, dy in pts]  # noqa: E731
    soft_shadow(a, rot([(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]), dx=3, dy=4)
    a.shape(rot([(-w / 2 + 4, -h / 2 + 3), (w / 2, -h / 2 + 3), (w / 2, h / 2 - 3), (-w / 2 + 4, h / 2 - 3)]), PAGES, outline=DETAIL, corner=2, depth=1, mottle=0)
    a.shape(rot([(-w / 2, -h / 2), (w / 2 - 5, -h / 2), (w / 2 - 5, h / 2), (-w / 2, h / 2)]), color, outline=DETAIL * 1.3, corner=3, depth=3, light_k=0.35, mottle=0)
    a.ink(rot([(-w / 2 + 8, -h / 2 + 4), (-w / 2 + 8, h / 2 - 4)]), FINE * 1.2, color=shade(color, 0.45), alpha=0.8)
    a.ink(rot([(-w / 2 + 18, -h * 0.2), (w / 2 - 16, -h * 0.2)]), FINE * 1.3, color=GOLD, alpha=0.9)


def candle_holder_at(a, x, y, r=11):
    a.shape(ellipse(x, y, r * 1.7, r * 1.7, 28), BRASS, outline=DETAIL, depth=2, mottle=0)
    candle(a, x, y, r)


# -- tavern -------------------------------------------------------------------------------------


def tavern_table(seed=1201, setting="ale", w=420, h=240, round_=False):
    a = Art(w, h, seed)
    if round_:
        m = w / 2
        a.shape(ellipse(m, h / 2, w / 2 - 12, h / 2 - 12, 96), WOOD, depth=12, detail=lambda art, p: boards(art, 0, 0, w, h, WOOD, 5, vertical=True))
    else:
        board(a, 10, 10, w - 10, h - 10, WOOD, n=3, corner=10)
    cx, cy = w / 2, h / 2
    if setting == "ale":
        for k, (dx, dy) in enumerate(((-110, -50), (90, -60), (-60, 60), (120, 50))):
            mug_at(a, cx + dx, cy + dy, 22, ang=a.rng.uniform(0, 6.28))
        bottle_at(a, cx + 10, cy - 10)
    elif setting == "cards":
        cards_at(a, cx - 40, cy, 7, 1.6)
        mug_at(a, cx + 120, cy - 50, 20)
        mug_at(a, cx - 140, cy + 60, 20, ang=2.0)
        coins(a, cx + 90, cy + 50, 10, 20)
    elif setting == "dice":
        for _ in range(3):
            die_at(a, cx + a.rng.uniform(-40, 40), cy + a.rng.uniform(-30, 30), 12)
        coins(a, cx - 110, cy - 30, 12, 24)
        coins(a, cx + 110, cy + 30, 8, 18)
        mug_at(a, cx + 120, cy - 60, 20)
    elif setting == "meal":
        plate_at(a, cx - 100, cy - 40, 34, "meat")
        plate_at(a, cx + 100, cy + 40, 34, "stew")
        plate_at(a, cx + 90, cy - 50, 30, "bread")
        mug_at(a, cx - 50, cy + 60, 20)
        mug_at(a, cx + 20, cy - 70, 20, ang=1.0)
        candle_holder_at(a, cx, cy, 10)
    elif setting == "candle":
        glow(a, cx, cy, 90, rgb("#ffd27a"), 0.3)
        candle_holder_at(a, cx, cy, 12)
        goblet_at(a, cx - 70, cy + 30)
        goblet_at(a, cx + 70, cy - 30)
    return a.image()


def card_table(seed=1205):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, m - 12, m - 12, 96), WOOD_DARK, depth=12)
    a.shape(ellipse(m, m, m - 34, m - 34, 96), rgb("#3f6a4a"), outline=DETAIL * 1.3, depth=4, shade_k=0.2, light_k=0.1, mottle=0.05)
    cards_at(a, m, m, 6, 1.3)
    for t in (0.3, 2.4, 4.4):
        coins(a, m + 80 * math.cos(t), m + 80 * math.sin(t), 6, 14)
    return a.image()


def dice_set(seed=1206):
    s = 140
    a = Art(s, s, seed)
    a.shape(ellipse(70, 70, 56, 56, 48), rgb("#6a3a2e"), outline=DETAIL * 1.3, depth=4, shade_k=0.2, light_k=0.2, mottle=0)  # dice cup tray
    for x, y, p in ((54, 56, 6), (84, 64, 3), (66, 92, 5)):
        die_at(a, x, y, 13, p)
    return a.image()


def game_board(seed=1207, kind="chess"):
    s = 230
    a = Art(s, s, seed)
    a.shape(rect(10, 10, s - 10, s - 10), WOOD_DARK, corner=6, depth=8)
    n = 8
    c0 = 24
    cell = (s - 2 * c0) / n
    for i in range(n):
        for j in range(n):
            col = rgb("#e8dcc0") if (i + j) % 2 == 0 else rgb("#5a3e2a")
            a.shape(rect(c0 + i * cell, c0 + j * cell, c0 + (i + 1) * cell, c0 + (j + 1) * cell), col, outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    a.ink(rect(c0, c0, s - c0, s - c0), DETAIL, closed=True)
    pieces = [(rgb("#f3eee2"), (0, 1)), (rgb("#2a2a30"), (6, 7))]
    for col, rows in pieces:
        for j in rows:
            for i in range(n):
                if a.rng.random() < (0.85 if kind == "chess" else 0.0) or (kind == "checkers" and (i + j) % 2 == 1):
                    x, y = c0 + (i + 0.5) * cell, c0 + (j + 0.5) * cell
                    r = cell * (0.36 if kind == "checkers" else 0.3)
                    a.shape(ellipse(x, y, r, r, 20), col, outline=FINE * 1.3, depth=1.5, shade_k=0.3, light_k=0.4, ao=0, mottle=0)
                    if kind == "chess" and j in (0, 7) and i in (3, 4):
                        dot(a, x, y, r * 0.45, GOLD)
    return a.image()


def bard_stage(seed=1208):
    w, h = 460, 300
    a = Art(w, h, seed)
    board(a, 10, 10, w - 10, h - 10, WOOD_DARK, n=6, vertical=True, corner=8)
    a.shape(rect(10, h - 34, w - 10, h - 10), WOOD, outline=DETAIL * 1.3, corner=4, depth=4)  # front edge
    lute_at(a, 160, 120, -0.5)
    drum_at(a, 320, 110, 40)
    a.shape(rect(260, 170, 330, 210), RED, outline=DETAIL * 1.2, corner=10, depth=4)  # stool cushion
    candle_holder_at(a, 40, 40, 9)
    candle_holder_at(a, w - 40, 40, 9)
    return a.image()


def lute_at(a, x, y, ang):
    c, s = math.cos(ang), math.sin(ang)
    rot = lambda pts: [(x + dx * c - dy * s, y + dx * s + dy * c) for dx, dy in pts]  # noqa: E731
    a.shape(rot(rect(30, -8, 130, 8)), WOOD_DARK, outline=DETAIL * 1.3, corner=3, depth=2, mottle=0)
    a.shape(rot([(122, -12), (160, -16), (164, 16), (122, 12)]), WOOD_DARK, outline=DETAIL * 1.2, corner=3, depth=2, mottle=0)
    body = rot(chaikin([(-50, 0), (-30, -42), (10, -46), (40, -20), (44, 0), (40, 20), (10, 46), (-30, 42)], True, 2))
    soft_shadow(a, body, dx=4, dy=5)
    a.shape(body, rgb("#c28a4a"), depth=6, light_k=0.4)
    a.shape(rot(ellipse(0, 0, 13, 13, 24)), rgb("#2a1e18"), outline=FINE * 1.3, depth=1, shade_k=0, light_k=0, mottle=0)
    for k in (-4, 0, 4):
        a.ink(rot([(-34, k), (160, k * 0.6)]), FINE * 0.7, color=rgb("#efe6d2"), alpha=0.9, wob=0)


def lute(seed=1209):
    w, h = 260, 140
    a = Art(w, h, seed)
    lute_at(a, 70, 74, -0.15)
    return a.image()


def drum_at(a, x, y, r):
    soft_shadow(a, (x, y), r, 4, 5)
    a.shape(ellipse(x, y, r, r, 48), RED, depth=5, light_k=0.3, detail=lambda art, p: [art.ink([(x + r * 0.84 * math.cos(t), y + r * 0.84 * math.sin(t)), (x + r * math.cos(t + 0.3), y + r * math.sin(t + 0.3))], FINE * 1.2, color=CERAMIC) for t in [2 * math.pi * k / 10 for k in range(10)]])
    a.shape(ellipse(x, y, r * 0.8, r * 0.8, 48), CERAMIC, outline=DETAIL * 1.2, depth=3, light_k=0.4)


def hand_drum(seed=1210):
    s = 130
    a = Art(s, s, seed)
    drum_at(a, 65, 65, 48)
    return a.image()


def flute(seed=1211):
    w, h = 220, 70
    a = Art(w, h, seed)
    handle(a, 20, 40, 200, 30, 12, WOOD_LIGHT)
    for k in range(6):
        x = 90 + k * 16
        dot(a, x, 34.5 - (x - 20) * 0.055, 3, INKC)
    return a.image()


def horn(seed=1212):
    w, h = 220, 130
    a = Art(w, h, seed)
    pts = []
    for k in range(21):
        t = k / 20
        x, y = 20 + 170 * t, 90 - 50 * math.sin(t * 2.4)
        pts.append((x, y))
    from obj_nature import tube

    a.shape(tube(pts, 10, 46), rgb("#e6d6b0"), depth=5, light_k=0.4, detail=lambda art, p: [art.ink([(pts[k][0] - 4, pts[k][1] - 12), (pts[k][0] + 4, pts[k][1] + 12)], FINE, color=shade(rgb("#e6d6b0"), 0.4), alpha=0.6) for k in range(4, 20, 3)])
    a.shape(ellipse(pts[-1][0], pts[-1][1], 9, 23, 24), rgb("#3a2e28"), outline=DETAIL, depth=1, shade_k=0, light_k=0, mottle=0)
    a.ink([(40, 82), (180, 50)], DETAIL * 1.2, color=rgb("#6a422a"))
    return a.image()


def tankard_stack(seed=1213):
    s = 200
    a = Art(s, s, seed)
    for x, y in ((60, 70), (120, 60), (80, 130), (140, 125)):
        mug_at(a, x, y, 26, liquid=rgb("#3a2e28"), body=PEWTER, ang=a.rng.uniform(0, 6.28))
    return a.image()


def ale_mug(seed=1214):
    s = 90
    a = Art(s, s, seed)
    mug_at(a, 40, 46, 26, ang=0.0)
    return a.image()


def pewter_mug(seed=1215):
    s = 90
    a = Art(s, s, seed)
    mug_at(a, 40, 46, 26, liquid=WINE, body=PEWTER, ang=0.0)
    return a.image()


def bar_stool(seed=1216, top=WOOD_LIGHT):
    s = 110
    a = Art(s, s, seed)
    for t in (0.8, 2.4, 3.9, 5.5):
        a.shape(ellipse(55 + 38 * math.cos(t), 55 + 38 * math.sin(t), 9, 9, 16), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(55, 55, 38, 38, 48), top, depth=6, light_k=0.4)
    return a.image()


def keg_on_bar(seed=1217):
    w, h = 260, 200
    a = Art(w, h, seed)
    board(a, 8, 8, w - 8, h - 8, WOOD_DARK, n=2, corner=6)
    from obj_storage import keg

    img = keg(seed).resize((200, 144))
    import numpy as np

    a.c.drawImageRect(skia.Image.fromarray(np.asarray(img), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(20, 28, 200, 144))
    return a.image(grain=0)


def food_platter(seed=1218, kind="chicken"):
    w, h = 220, 160
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2
    soft_shadow(a, ellipse(cx, cy, 96, 66, 48), dx=4, dy=5)
    a.shape(ellipse(cx, cy, 96, 66, 48), SILVER, depth=4, light_k=0.5)
    a.ink(ellipse(cx, cy, 82, 54, 48), FINE * 1.2, closed=True, color=shade(SILVER, 0.35), alpha=0.8)
    if kind == "chicken":
        a.shape(ellipse(cx, cy, 50, 36, 40), rgb("#c47a3a"), outline=DETAIL * 1.3, depth=6, light_k=0.5)
        for s_ in (-1, 1):
            a.shape(ellipse(cx + 46, cy + s_ * 20, 18, 11, 20, rot=s_ * 0.5), rgb("#b56a32"), outline=DETAIL, depth=3, light_k=0.4, mottle=0)
            a.shape(ellipse(cx + 62, cy + s_ * 26, 6, 6, 12), CERAMIC, outline=FINE, depth=1, mottle=0)
        for x, y in ((cx - 60, cy - 30), (cx - 64, cy + 24), (cx + 10, cy + 46)):
            a.shape(ellipse(x, y, 10, 10, 16), rgb("#7ea74a"), outline=FINE * 1.2, depth=1, mottle=0)
    elif kind == "ham":
        a.shape(chaikin([(cx - 50, cy - 20), (cx + 10, cy - 36), (cx + 46, cy - 6), (cx + 30, cy + 30), (cx - 30, cy + 34), (cx - 56, cy + 10)], True, 2), rgb("#c46a5a"), outline=DETAIL * 1.3, corner=0, depth=6, light_k=0.4, detail=lambda art, p: [art.ink([(cx - 30 + k * 18, cy - 30), (cx - 40 + k * 18, cy + 30)], FINE * 1.1, color=shade(rgb("#c46a5a"), 0.4), alpha=0.7) for k in range(4)])
        a.shape(ellipse(cx + 54, cy - 6, 14, 10, 20), CERAMIC, outline=DETAIL, depth=2, mottle=0)
    elif kind == "fish":
        body = [(cx - 60, cy), (cx - 20, cy - 24), (cx + 40, cy - 16), (cx + 56, cy), (cx + 40, cy + 16), (cx - 20, cy + 24)]
        a.shape(chaikin(body, True, 2), rgb("#c99a6a"), outline=DETAIL * 1.3, corner=0, depth=4, light_k=0.4)
        a.shape([(cx + 50, cy), (cx + 76, cy - 20), (cx + 76, cy + 20)], rgb("#b5895a"), outline=DETAIL, corner=1, depth=2, mottle=0)
        dot(a, cx - 44, cy - 4, 3)
        for x in (cx - 20, cx, cx + 20):
            a.ink([(x, cy - 14), (x + 6, cy + 14)], FINE * 1.2, color=shade(rgb("#c99a6a"), 0.4), alpha=0.7)
    return a.image()


def bread_basket(seed=1219):
    from obj_storage import basket

    def loaves(art):
        for x, y, t in ((80, 90, 0.3), (130, 100, -0.4), (100, 130, 1.2)):
            art.shape(ellipse(x, y, 34, 20, 28, rot=t), BREAD, outline=DETAIL * 1.2, depth=4, light_k=0.4)
            for k in (-1, 0, 1):
                art.ink([(x + k * 12 * math.cos(t) - 6 * math.sin(t), y + k * 12 * math.sin(t) + 6 * math.cos(t)), (x + k * 12 * math.cos(t) + 6 * math.sin(t), y + k * 12 * math.sin(t) - 6 * math.cos(t))], FINE * 1.3, color=shade(BREAD, 0.5))

    return basket(seed, loaves)


def cheese_wheel(seed=1220):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    pts = [(m, m)] + [(m + 70 * math.cos(t), m + 70 * math.sin(t)) for t in [0.6 + k * (2 * math.pi - 0.9) / 40 for k in range(41)]]
    soft_shadow(a, pts, dx=4, dy=5)
    a.shape(pts, CHEESE, outline=OUTLINE * 0.9, corner=0, depth=6, light_k=0.4, detail=lambda art, p: art.ink(ellipse(m, m, 62, 62, 64), DETAIL, closed=True, color=rgb("#c99a3a"), alpha=0.8))
    wedge = [(m + 20, m + 4), (m + 88, m + 34), (m + 70, m + 70)]
    a.shape(wedge, tint(CHEESE, 0.1), outline=DETAIL * 1.3, corner=1, depth=3, mottle=0)
    for x, y in ((m - 20, m - 20), (m + 10, m + 30), (m - 30, m + 20)):
        a.shape(ellipse(x, y, 6, 5, 12), shade(CHEESE, 0.15), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def pie(seed=1221):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 64, 4, 5)
    a.shape(ellipse(m, m, 64, 64, 64), rgb("#c99050"), depth=6, light_k=0.4, detail=lambda art, p: [art.ink([(m + 20 * math.cos(t), m + 20 * math.sin(t)), (m + 56 * math.cos(t), m + 56 * math.sin(t))], FINE * 1.4, color=shade(rgb("#c99050"), 0.45)) for t in [2 * math.pi * k / 8 for k in range(8)]])
    a.shape(ellipse(m, m, 14, 14, 20), rgb("#8a2a3a"), outline=FINE * 1.2, depth=1, mottle=0)
    return a.image()


def stew_pot(seed=1222):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    for t in (0.2, math.pi + 0.2):
        a.shape(ellipse(m + 70 * math.cos(t), m + 70 * math.sin(t), 12, 8, 16, rot=t), IRON, outline=DETAIL, depth=2, mottle=0)
    soft_shadow(a, (m, m), 64, 4, 5)
    a.shape(ellipse(m, m, 64, 64, 64), rgb("#3e4045"), depth=8, light_k=0.4)
    a.shape(ellipse(m, m, 50, 50, 56), rgb("#9a5a2a"), outline=DETAIL, depth=6, shade_k=0, light_k=0.2, ao=0.4, detail=lambda art, p: [art.shape(ellipse(m + art.rng.uniform(-30, 30), m + art.rng.uniform(-30, 30), art.rng.uniform(5, 9), art.rng.uniform(4, 7), 14), art.rng.choice([rgb("#e08a3a"), rgb("#7ea74a"), rgb("#e6d6b0")]), outline=FINE, depth=1, mottle=0) for _ in range(10)])
    a.ink([(m - 10, m - 10), (m + 70, m - 70)], DETAIL * 2.4, color=INK)
    a.ink([(m - 10, m - 10), (m + 70, m - 70)], DETAIL * 1.4, color=WOOD_LIGHT)
    return a.image()


def roast_pig(seed=1223):
    w, h = 340, 200
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2
    soft_shadow(a, ellipse(cx, cy, 160, 90, 48), dx=4, dy=5)
    a.shape(ellipse(cx, cy, 160, 90, 48), SILVER, depth=4, light_k=0.5)
    pig = rgb("#c67a4a")
    a.shape(ellipse(cx - 10, cy, 100, 54, 48), pig, outline=OUTLINE * 0.8, depth=8, light_k=0.5, detail=lambda art, p: [art.ink([(cx - 60 + k * 24, cy - 46), (cx - 66 + k * 24, cy + 46)], FINE * 1.2, color=shade(pig, 0.4), alpha=0.6) for k in range(6)])
    a.shape(ellipse(cx + 96, cy, 34, 30, 32), tint(pig, 0.05), outline=DETAIL * 1.3, depth=5, light_k=0.5)
    a.shape(ellipse(cx + 124, cy, 13, 13, 20), rgb("#c4473a"), outline=DETAIL, depth=2, light_k=0.6, mottle=0)  # apple
    for x, y in ((cx - 130, cy - 40), (cx - 134, cy + 36), (cx + 70, cy + 70), (cx + 70, cy - 70)):
        a.shape(ellipse(x, y, 12, 12, 16), rgb("#7ea74a"), outline=FINE * 1.2, depth=1, mottle=0)
    return a.image()


def ale_puddle(seed=1224):
    s = 200
    a = Art(s, s, seed)
    a.shape(blob(100, 100, 70, a.rng, 12, 0.3), rgb("#c99a4a"), outline=0, smooth=True, depth=2, shade_k=0, light_k=0.4, ao=0, mottle=0.08)
    a.ink([(70, 80), (96, 74)], FINE * 1.5, color=rgb("#fff0c8"), alpha=0.8)
    for _ in range(6):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(72, 90)
        dot(a, 100 + d * math.cos(t), 100 + d * math.sin(t), a.rng.uniform(3, 6), rgb("#c99a4a"), 0.9)
    from obj_storage import mug

    import numpy as np

    img = mug(seed).rotate(60, expand=True)
    a.c.drawImageRect(skia.Image.fromarray(np.asarray(img), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(100, 30, img.width * 0.7, img.height * 0.7))
    return a.image(grain=0)


def bench_table_set(seed=1225):
    w, h = 480, 360
    a = Art(w, h, seed)
    for y in (20, h - 70):
        board(a, 20, y, w - 20, y + 50, WOOD_DARK, n=1, corner=6)
    board(a, 10, 90, w - 10, h - 90, WOOD, n=3, corner=8)
    for x, y in ((90, 130), (210, 140), (330, 130), (120, 220), (260, 230), (390, 220)):
        mug_at(a, x, y, 20, ang=a.rng.uniform(0, 6.28))
    plate_at(a, 400, 140, 28, "bread")
    return a.image()


def menu_board(seed=1226):
    w, h = 240, 300
    a = Art(w, h, seed)
    # A chalkboard sign leaning flat on the floor: frame and the chalk menu.
    a.shape(rect(10, 10, w - 10, h - 10), WOOD_DARK, corner=6, depth=8)

    def chalk(art, p):
        for k in range(7):
            y = 50 + k * 30
            art.ink([(40, y), (40 + art.rng.uniform(80, 150), y + art.rng.uniform(-2, 2))], FINE * 1.3, color=rgb("#efece4"), alpha=0.85)
            dot(art, w - 50, y, 3, rgb("#efece4"), 0.85)

    a.shape(rect(26, 26, w - 26, h - 26), rgb("#2e3a32"), outline=DETAIL * 1.2, corner=3, depth=4, shade_k=0.1, light_k=0, mottle=0.1, detail=chalk)
    return a.image()


# -- library & study ------------------------------------------------------------------------------


def reading_desk(seed=1301):
    w, h = 400, 220
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD, n=3, corner=8)
    open_book(a, 150, 110, 1.0)
    candle_holder_at(a, 320, 60, 10)
    book_at(a, 320, 150, 60, 80, 0.3)
    return a.image()


def study_desk(seed=1302):
    w, h = 460, 240
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD_DARK, n=3, corner=8)
    paper_at(a, 120, 110, 90, 120, -0.1)
    paper_at(a, 200, 130, 80, 110, 0.15)
    inkwell_at(a, 290, 160)
    book_at(a, 380, 80, 70, 96, -0.2)
    candle_holder_at(a, 400, 180, 10)
    for _ in range(2):
        roll(a, 330 + a.rng.uniform(-10, 10), 60 + a.rng.uniform(-6, 6), 90, 9, a.rng.uniform(0.1, 0.4))
    return a.image()


def book_pile(seed=1303, n=5, size=1.0):
    s = int(220 * size)
    a = Art(s, s, seed)
    for k in range(n):
        x, y = s / 2 + a.rng.uniform(-14, 14) * size, s / 2 + a.rng.uniform(-14, 14) * size
        book_at(a, x, y, (120 - k * 10) * size, (90 - k * 6) * size, a.rng.uniform(-0.4, 0.4))
    return a.image()


def scattered_books(seed=1304):
    s = 300
    a = Art(s, s, seed)
    for _ in range(6):
        book_at(a, a.rng.uniform(70, 230), a.rng.uniform(70, 230), a.rng.uniform(56, 76), a.rng.uniform(80, 100), a.rng.uniform(0, 6.28))
    open_book(a, 150, 150, 0.8)
    return a.image()


def open_book_obj(seed=1305, k=1.1):
    w, h = int(190 * k), int(140 * k)
    a = Art(w, h, seed)
    open_book(a, w / 2, h / 2, k)
    return a.image()


def closed_book(seed=1306, color=None):
    s = 140
    a = Art(s, s, seed)
    book_at(a, 70, 70, 76, 104, -0.15, rgb(color) if color else None)
    return a.image()


def globe_stand(seed=1307):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    for t in (0.6, 2.7, 4.8):
        handle(a, m, m, m + 92 * math.cos(t), m + 92 * math.sin(t), 11, WOOD_DARK)
    sea = rgb("#6f9fc0")

    def lands(art, p):
        for x, y, r in ((m - 30, m - 20, 26), (m + 30, m + 14, 22), (m - 10, m + 40, 14)):
            art.shape(blob(x, y, r, art.rng, 9, 0.35), rgb("#b8c87a"), outline=FINE * 1.2, smooth=True, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        for k in (-1, 0, 1):
            art.ink(ellipse(m, m + k * 30, 64 * math.cos(k * 0.45), 8, 40), FINE * 0.9, closed=True, color=shade(sea, 0.4), alpha=0.6)

    a.shape(ellipse(m, m, 66, 66, 64), sea, depth=10, light_k=0.6, detail=lands)
    a.ink(ellipse(m, m, 74, 74, 64), DETAIL * 2.4, closed=True, color=BRASS)
    return a.image()


def telescope(seed=1308):
    w, h = 340, 260
    a = Art(w, h, seed)
    cx, cy = 140, 150
    for t in (1.0, 2.6, 4.4):
        handle(a, cx, cy, cx + 100 * math.cos(t), cy + 100 * math.sin(t), 10, WOOD_DARK)
    from obj_nature import tube

    spine = [(cx - 50 + 18 * k, cy + 30 - 12 * k) for k in range(12)]
    a.shape(tube(spine, 22, 34), BRASS, depth=5, light_k=0.55)
    for k in (3, 7):
        x, y = spine[k]
        a.ink([(x - 8, y - 14), (x + 8, y + 14)], DETAIL, color=shade(BRASS, 0.4))
    ex, ey = spine[-1]
    a.shape(ellipse(ex, ey, 10, 17, 24, rot=-0.6), rgb("#9fd0e0"), outline=DETAIL, depth=1, mottle=0, light_k=0.5)
    return a.image()


def map_table(seed=1309):
    w, h = 460, 300
    a = Art(w, h, seed)
    board(a, 8, 8, w - 8, h - 8, WOOD_DARK, n=3, corner=8)
    big = [(60, 50), (w - 70, 40), (w - 60, h - 60), (70, h - 50)]

    def drawn(art, p):
        art.ink(chaikin([(110, 200), (180, 140), (260, 170), (360, 90)], False, 2), DETAIL, color=rgb("#a8483a"), alpha=0.9)
        art.ink(chaikin([(90, 100), (150, 80), (230, 110), (300, 70)], False, 2), FINE * 1.4, color=rgb("#4f74a8"), alpha=0.9)
        for x, y in ((140, 220), (170, 230), (300, 200)):
            art.ink([(x - 12, y + 7), (x, y - 10), (x + 12, y + 7)], FINE * 1.4, color=rgb("#6a5a4a"))
        art.ink(ellipse(330, 210, 26, 26, 32), FINE * 1.2, closed=True, color=rgb("#6a5a4a"))
        art.ink([(330, 180), (330, 240)], FINE * 1.2, color=rgb("#6a5a4a"))
        art.ink([(300, 210), (360, 210)], FINE * 1.2, color=rgb("#6a5a4a"))

    soft_shadow(a, big, dx=4, dy=5)
    a.shape(big, PARCH, outline=DETAIL * 1.3, corner=3, depth=3, detail=drawn)
    for x, y in ((70, 56), (w - 74, 48), (w - 66, h - 66), (78, h - 58)):
        a.shape(ellipse(x, y, 10, 10, 16), IRON, outline=DETAIL, depth=2, mottle=0)  # weights
    candle_holder_at(a, w - 40, h / 2, 9)
    return a.image()


def scroll_rack(seed=1310):
    w, h = 380, 200
    a = Art(w, h, seed)
    # Pigeonholes seen from above: a grid of square cells, rolled scrolls lying in them.
    board(a, 8, 8, w - 8, h - 8, WOOD_DARK, n=1, corner=6)
    cols, rows = 5, 2
    cw, ch = (w - 40) / cols, (h - 40) / rows
    for i in range(cols):
        for j in range(rows):
            x0, y0 = 20 + i * cw, 20 + j * ch
            a.shape(rect(x0 + 4, y0 + 4, x0 + cw - 4, y0 + ch - 4), shade(WOOD_DARK, 0.4), outline=DETAIL, corner=3, depth=4, shade_k=0, light_k=0, ao=0.5)
            for k in range(a.rng.randint(1, 3)):
                roll(a, x0 + cw / 2, y0 + 20 + k * 22, cw - 18, 9, 0.0)
    return a.image()


def lectern_book(seed=1311, wood=WOOD):
    w, h = 220, 200
    a = Art(w, h, seed)
    a.shape(rect(70, 140, 150, 190), shade(wood, 0.2), outline=DETAIL * 1.2, corner=8, depth=4)
    board(a, 20, 20, w - 20, 150, wood, n=2, corner=8)
    open_book(a, w / 2, 86, 0.95)
    return a.image()


def reading_nook(seed=1312):
    w, h = 420, 320
    a = Art(w, h, seed)
    from obj_furniture import upholstered

    upholstered(a, [(60, 70, 200, 250)], (30, 20, 230, 74), [(20, 64, 64, 256), (196, 64, 240, 256)], (14, 14, 246, 266))
    board(a, 270, 90, 400, 220, WOOD, n=1, corner=60)
    candle_holder_at(a, 335, 130, 10)
    book_at(a, 330, 180, 50, 66, 0.4)
    book_at(a, 130, 290, 90, 50, -0.1) if False else None
    return a.image()


def specimen_jars(seed=1313):
    w, h = 280, 180
    a = Art(w, h, seed)
    contents = [rgb("#7fae5a"), rgb("#c9a45a"), rgb("#b56a6a"), rgb("#8a6ad8"), rgb("#e6dcc4")]
    for k in range(5):
        x, y = 50 + (k % 3) * 90 + (k // 3) * 45, 55 + (k // 3) * 75
        soft_shadow(a, (x, y), 32, 3, 4)
        a.shape(ellipse(x, y, 32, 32, 36), rgb("#cfe3e0"), outline=DETAIL * 1.3, depth=3, light_k=0.6, mottle=0)
        a.shape(blob(x, y, 16, a.rng, 8, 0.3), contents[k], outline=FINE * 1.2, smooth=True, depth=1, mottle=0)
        a.shape(ellipse(x, y, 14, 14, 20), rgb("#b88a5a"), outline=FINE * 1.3, depth=1, mottle=0) if False else None
        a.ink([(x - 20, y - 12), (x - 10, y - 22)], FINE * 1.8, color=(250, 250, 250), alpha=0.9)
    return a.image()


def quill_ink(seed=1314):
    s = 160
    a = Art(s, s, seed)
    paper_at(a, 56, 84, 70, 90, -0.2)
    inkwell_at(a, 76, 116)
    return a.image()


def letters(seed=1315):
    s = 220
    a = Art(s, s, seed)
    for _ in range(5):
        x, y, t = a.rng.uniform(70, 150), a.rng.uniform(70, 150), a.rng.uniform(-0.6, 0.6)
        c, sn = math.cos(t), math.sin(t)
        rot = lambda pts, x=x, y=y, c=c, sn=sn: [(x + dx * c - dy * sn, y + dx * sn + dy * c) for dx, dy in pts]  # noqa: E731
        env = rot([(-50, -32), (50, -32), (50, 32), (-50, 32)])
        soft_shadow(a, env, dx=3, dy=4)
        a.shape(env, rgb("#e8dcc0"), outline=DETAIL * 1.1, corner=2, depth=2, mottle=0)
        a.ink(rot([(-50, -32), (0, 4), (50, -32)]), FINE * 1.2, color=shade(rgb("#e8dcc0"), 0.45), alpha=0.8)
        sx, sy = rot([(0, 4)])[0]
        a.shape(scallop(sx, sy, 9, a.rng, 7, 0.2), rgb("#a8283a"), outline=FINE * 1.2, depth=1, mottle=0, light_k=0.5)
    return a.image()


def magnifying_glass(seed=1316):
    w, h = 220, 130
    a = Art(w, h, seed)
    handle(a, 110, 72, 200, 100, 13, WOOD_DARK)
    a.ink(ellipse(70, 60, 46, 46, 48), DETAIL * 4.2, closed=True, color=INK)
    a.ink(ellipse(70, 60, 46, 46, 48), DETAIL * 2.6, closed=True, color=BRASS)
    a.shape(ellipse(70, 60, 42, 42, 48), rgb("#cfe6ee"), outline=0, depth=1, shade_k=0, light_k=0.6, ao=0, mottle=0)
    a.ink([(48, 44), (62, 30)], FINE * 2.2, color=(255, 255, 255), alpha=0.9)
    return a.image()


def compass(seed=1317):
    s = 140
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 52, 3, 4)
    a.shape(ellipse(m, m, 52, 52, 48), BRASS, depth=5, light_k=0.5)
    a.shape(ellipse(m, m, 40, 40, 48), rgb("#efe6d2"), outline=DETAIL, depth=2, mottle=0, detail=lambda art, p: [art.ink([(m + 32 * math.cos(t), m + 32 * math.sin(t)), (m + 38 * math.cos(t), m + 38 * math.sin(t))], FINE, color=INKC) for t in [2 * math.pi * k / 16 for k in range(16)]])
    a.shape([(m, m - 32), (m + 7, m), (m - 7, m)], rgb("#a8483a"), outline=FINE, corner=1, depth=1, mottle=0)
    a.shape([(m, m + 32), (m + 7, m), (m - 7, m)], INKC, outline=FINE, corner=1, depth=1, mottle=0)
    dot(a, m, m, 3, BRASS)
    return a.image()


def abacus(seed=1318):
    w, h = 240, 160
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), WOOD_DARK, corner=6, depth=6)
    a.shape(rect(24, 24, w - 24, h - 24), shade(WOOD_DARK, 0.4), outline=DETAIL, corner=3, depth=3, shade_k=0, light_k=0, ao=0.4)
    for j in range(5):
        y = 38 + j * 21
        a.ink([(24, y), (w - 24, y)], FINE * 1.2, color=SILVER)
        n = a.rng.randint(2, 6)
        for k in range(8):
            x = 40 + k * 22 + (60 if k >= n else 0)
            if x > w - 34:
                continue
            a.shape(ellipse(x, y, 9, 8, 16), [rgb("#a8483a"), rgb("#e6b84a"), rgb("#4f74a8")][j % 3], outline=FINE * 1.2, depth=1.5, light_k=0.4, mottle=0)
    return a.image()


def candle_stand(seed=1319):
    s = 120
    a = Art(s, s, seed)
    glow(a, 60, 60, 52, rgb("#ffd27a"), 0.4)
    a.shape(ellipse(60, 60, 30, 30, 32), IRON, outline=DETAIL * 1.3, depth=4, light_k=0.4)
    candle(a, 60, 60, 14)
    return a.image()


def hourglass_desk(seed=1320):
    w, h = 200, 160
    a = Art(w, h, seed)
    paper_at(a, 80, 80, 90, 110, 0.1)
    a.shape(ellipse(150, 60, 30, 30, 32), WOOD_DARK, outline=DETAIL * 1.2, depth=4)
    a.shape(ellipse(150, 60, 18, 18, 28), GLASS, outline=DETAIL, depth=2, light_k=0.6, mottle=0)
    a.shape(ellipse(150, 60, 10, 10, 20), rgb("#e0c07a"), outline=FINE, depth=1, mottle=0)
    return a.image()


def bookstand_stack(seed=1321):
    w, h = 320, 180
    a = Art(w, h, seed)
    for k in range(9):
        x = 36 + k * 28
        col = rgb(a.rng.choice(BOOKS))
        a.shape(rect(x, 30, x + 24, h - 30), col, outline=DETAIL, corner=2, depth=3, light_k=0.3, mottle=0)
        a.ink([(x + 12, 40), (x + 12, h - 40)], FINE, color=GOLD, alpha=0.8)
    for x in (22, w - 22):
        a.shape(rect(x - 12, 20, x + 12, h - 20), STONE, outline=DETAIL * 1.3, corner=3, depth=4)  # bookends
    return a.image()


# -- treasure ----------------------------------------------------------------------------------------


def chest_body(a, x0, y0, x1, y1, wood=WOOD, metal=GOLD):
    a.shape(rect(x0, y0, x1, y1), wood, corner=10, depth=10, detail=lambda art, p: boards(art, x0, y0, x1, y1, wood, 3))
    for x in (x0 + 34, x1 - 34):
        a.shape(rect(x - 12, y0, x + 12, y1), metal, outline=DETAIL * 1.3, corner=3, depth=4, light_k=0.5, mottle=0)
        for y in (y0 + 16, (y0 + y1) / 2, y1 - 16):
            dot(a, x, y, 3, tint(metal, 0.4))
    for cx, cy in ((x0 + 10, y0 + 10), (x1 - 10, y0 + 10), (x0 + 10, y1 - 10), (x1 - 10, y1 - 10)):
        a.shape([(cx - 12, cy - 12), (cx + 12, cy - 12), (cx + 12, cy + 12), (cx - 12, cy + 12)], metal, outline=DETAIL, corner=4, depth=2, mottle=0)


def ornate_chest(seed=1401, wood=WOOD_DARK, metal=GOLD):
    w, h = 300, 200
    a = Art(w, h, seed)
    chest_body(a, 10, 12, w - 10, h - 12, wood, metal)
    a.shape(rect(w / 2 - 24, h / 2 - 20, w / 2 + 24, h / 2 + 26), metal, outline=DETAIL * 1.3, corner=6, depth=5, light_k=0.5)
    a.shape(rect(w / 2 - 4, h / 2 - 2, w / 2 + 4, h / 2 + 14), INKC, outline=0, corner=2, depth=1, shade_k=0, light_k=0, mottle=0)
    a.shape([(w / 2, 30), (w / 2 + 12, 42), (w / 2, 54), (w / 2 - 12, 42)], GEMS[0], outline=FINE * 1.3, corner=1, depth=2, light_k=0.7, mottle=0)
    return a.image()


def treasure_chest_open(seed=1402, wood=WOOD, metal=GOLD, gems=True):
    w, h = 320, 270
    a = Art(w, h, seed)
    # The lid flipped open behind, the box with its heap of coins (filling it
    # to the rim, clipped by it) in front.
    board(a, 14, 6, w - 14, 76, shade(wood, 0.1), n=2, corner=10)
    for x in (48, w - 48):
        a.shape(rect(x - 12, 6, x + 12, 76), metal, outline=DETAIL * 1.2, corner=3, depth=4, light_k=0.5, mottle=0)
    chest_body(a, 10, 66, w - 10, h - 10, wood, metal)
    inner = rect(28, 82, w - 28, h - 26)

    def treasure(art, p):
        coins(art, w / 2, (82 + h - 26) / 2, 120, 130, ry=80, fill=True)
        if gems:
            for _ in range(5):
                x, y = art.rng.uniform(60, w - 60), art.rng.uniform(100, h - 50)
                c = art.rng.choice(GEMS)
                soft_shadow(art, (x, y), 10, 3, 4, 0.35, 3)
                art.shape([(x, y - 11), (x + 10, y), (x, y + 11), (x - 10, y)], c, outline=DETAIL, corner=1, depth=3, light_k=0.8, mottle=0)

    a.shape(inner, rgb("#4a3324"), outline=DETAIL * 1.2, corner=6, depth=10, shade_k=0, light_k=0, ao=0.5, detail=treasure)
    return a.image()


def gold_pile(seed=1403, size=1.0):
    s = int(280 * size)
    a = Art(s, s, seed)
    coins(a, s / 2, s / 2, int(110 * size * size), 110 * size, r=9 * max(1.0, size * 0.85))
    return a.image()


def gem_pile(seed=1404):
    s = 200
    a = Art(s, s, seed)
    m = s / 2

    def gem(art, x, y, hgt):
        c = art.rng.choice(GEMS)
        r = art.rng.uniform(8, 13)
        soft_shadow(art, (x, y), r, 2, 3, 0.3, 2)
        kind = art.rng.random()
        if kind < 0.5:
            art.shape([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], c, outline=FINE * 1.3, corner=1, depth=2, light_k=0.8, mottle=0)
        else:
            art.shape([(x + r * math.cos(t), y + r * math.sin(t)) for t in [k * math.pi / 3 for k in range(6)]], c, outline=FINE * 1.3, corner=1, depth=2, light_k=0.8, mottle=0)
        dot(art, x - r * 0.3, y - r * 0.3, r * 0.2, (255, 255, 255), 0.8)

    pile(a, m, m, 70, 34, gem, min_gap=0.7)
    return a.image()


def crown(seed=1405, metal=GOLD):
    s = 170
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 56, 4, 5)
    pts = []
    for k in range(16):
        t = 2 * math.pi * k / 16
        r = 62 if k % 2 == 0 else 46
        pts.append((m + r * math.cos(t), m + r * math.sin(t)))
    a.shape(pts, metal, outline=DETAIL * 1.4, corner=2, depth=4, light_k=0.55)
    a.shape(ellipse(m, m, 40, 40, 48), VELVET, outline=DETAIL * 1.2, depth=4, light_k=0.3)
    for k in range(8):
        t = 2 * math.pi * k / 8
        dot(a, m + 62 * math.cos(t), m + 62 * math.sin(t), 5, GEMS[k % 4])
    return a.image()


def scepter(seed=1406):
    w, h = 260, 90
    a = Art(w, h, seed)
    handle(a, 20, 50, 200, 40, 11, GOLD)
    for x in (60, 120):
        a.ink([(x, 36), (x + 1, 56)], DETAIL * 1.4, color=shade(GOLD, 0.4))
    a.shape(ellipse(214, 40, 24, 24, 32), GOLD, outline=DETAIL * 1.3, depth=3, light_k=0.5)
    a.shape([(214, 24), (228, 40), (214, 56), (200, 40)], GEMS[1], outline=FINE * 1.3, corner=1, depth=2, light_k=0.8, mottle=0)
    return a.image()


def chalice(seed=1407, metal=GOLD):
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 40, 3, 4)
    a.shape(ellipse(m, m, 40, 40, 48), metal, outline=DETAIL * 1.4, depth=5, light_k=0.55, detail=lambda art, p: [dot(art, m + 34 * math.cos(t), m + 34 * math.sin(t), 3.4, GEMS[k % 5]) for k, t in enumerate([2 * math.pi * k / 8 for k in range(8)])])
    a.shape(ellipse(m, m, 26, 26, 40), WINE, outline=DETAIL, depth=3, shade_k=0, light_k=0.2, ao=0.3, mottle=0)
    return a.image()


def jewelry_box(seed=1408):
    w, h = 220, 170
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), WOOD_DARK, corner=8, depth=8)
    a.shape(rect(24, 24, w - 24, h - 24), VELVET, outline=DETAIL * 1.2, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5)
    necklace_at(a, 80, 80, 36)
    for x, y, c in ((150, 70, GEMS[0]), (160, 120, GEMS[1])):
        ring_at(a, x, y, 13, GOLD, c)
    return a.image()


def necklace_at(a, x, y, r, metal=GOLD, gem=None):
    pts = [(x + r * math.cos(t), y + r * 0.8 * math.sin(t)) for t in [0.5 + k * (2 * math.pi - 1.0) / 30 for k in range(31)]]
    a.ink(pts, DETAIL * 2.2, color=INK)
    a.ink(pts, DETAIL * 1.2, color=metal)
    for k in range(0, 31, 3):
        dot(a, pts[k][0], pts[k][1], 2.6, tint(metal, 0.3))
    gx, gy = x, y + r * 0.8 + 10
    a.shape([(gx, gy - 12), (gx + 10, gy), (gx, gy + 12), (gx - 10, gy)], gem or GEMS[0], outline=DETAIL, corner=1, depth=2, light_k=0.8, mottle=0)


def necklace(seed=1409):
    s = 150
    a = Art(s, s, seed)
    necklace_at(a, 75, 64, 50)
    return a.image()


def ring_at(a, x, y, r, metal, gem):
    a.ink(ellipse(x, y, r, r, 32), DETAIL * 2.4, closed=True, color=INK)
    a.ink(ellipse(x, y, r, r, 32), DETAIL * 1.3, closed=True, color=metal)
    a.shape(ellipse(x + r * 0.7, y - r * 0.7, r * 0.5, r * 0.5, 16), gem, outline=FINE * 1.3, depth=1, light_k=0.8, mottle=0)


def rings(seed=1410):
    s = 150
    a = Art(s, s, seed)
    for (x, y), c, mt in zip(((50, 60), (100, 50), (80, 105)), GEMS, (GOLD, SILVER, GOLD)):
        ring_at(a, x, y, 16, mt, c)
    return a.image()


def treasure_sack(seed=1411):
    w, h = 200, 220
    a = Art(w, h, seed)
    from objects import sack

    import numpy as np

    img = sack(seed).resize((150, 183))
    a.c.drawImageRect(skia.Image.fromarray(np.asarray(img), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(10, 10, 150, 183))
    coins(a, 150, 175, 14, 26)
    return a.image(grain=0)


def gold_bars(seed=1412):
    w, h = 260, 200
    a = Art(w, h, seed)
    for row, (y, n, off) in enumerate(((140, 3, 0), (100, 2, 36), (60, 1, 72))):
        for k in range(n):
            x = 56 + off + k * 72
            pts = [(x - 30, y - 18), (x + 30, y - 18), (x + 36, y + 20), (x - 36, y + 20)]
            soft_shadow(a, pts, dx=3, dy=4)
            col = tint(GOLD, 0.06 * row)
            a.shape(pts, col, outline=DETAIL * 1.2, corner=3, depth=4, light_k=0.6, mottle=0)
            a.shape([(x - 22, y - 12), (x + 22, y - 12), (x + 24, y + 12), (x - 24, y + 12)], tint(col, 0.15), outline=FINE, corner=2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    return a.image()


def ornate_urn(seed=1413):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 66, 4, 5)
    a.shape(ellipse(m, m, 66, 66, 64), GOLD, depth=8, light_k=0.55, detail=lambda art, p: [art.ink(ellipse(m, m, r, r, 64), FINE * 1.3, closed=True, color=shade(GOLD, 0.45), alpha=0.8) for r in (56, 46)])
    a.shape(ellipse(m, m, 30, 30, 40), tint(GOLD, 0.1), outline=DETAIL * 1.2, depth=4, light_k=0.5)
    a.shape(ellipse(m, m, 18, 18, 28), rgb("#2a221e"), outline=DETAIL, depth=3, shade_k=0, light_k=0, ao=0.5)
    for k in range(6):
        t = 2 * math.pi * k / 6
        dot(a, m + 51 * math.cos(t), m + 51 * math.sin(t), 4, GEMS[k % 5])
    return a.image()


def mimic_chest(seed=1414):
    w, h = 320, 260
    a = Art(w, h, seed)
    # Lid gaping up behind, rows of teeth on both rims, a tongue lolling out.
    board(a, 14, 6, w - 14, 86, WOOD_DARK, n=2, corner=10)
    chest_body(a, 10, 76, w - 10, h - 10, WOOD_DARK, IRON)
    mouth = rect(28, 92, w - 28, h - 26)
    a.shape(mouth, rgb("#5a1a22"), outline=DETAIL * 1.3, corner=10, depth=12, shade_k=0, light_k=0, ao=0.6)
    for y0, d in ((92, 1), (h - 26, -1)):
        for k in range(10):
            x = 40 + k * 26
            a.shape([(x - 10, y0), (x + 10, y0), (x, y0 + d * 24)], rgb("#efe6d2"), outline=FINE * 1.3, corner=1, depth=1, mottle=0)
    for y0, d in ((86, 1), (h - 20, -1)):
        for k in range(10):
            x = 40 + k * 26
            a.shape([(x - 10, y0), (x + 10, y0), (x, y0 - d * 18)], rgb("#efe6d2"), outline=FINE * 1.3, corner=1, depth=1, mottle=0) if False else None
    tongue = chaikin([(w / 2 - 30, 140), (w / 2 + 30, 140), (w / 2 + 36, 210), (w / 2 + 10, 236), (w / 2 - 20, 220)], True, 2)
    a.shape(tongue, rgb("#c8506a"), outline=DETAIL * 1.3, corner=0, depth=4, light_k=0.4)
    a.ink([(w / 2, 150), (w / 2 + 6, 216)], FINE * 1.4, color=shade(rgb("#c8506a"), 0.5))
    for x in (60, w - 60):
        a.shape(ellipse(x, 40, 14, 10, 20), rgb("#f2d24a"), outline=DETAIL, depth=2, light_k=0.5, mottle=0)
        a.shape(ellipse(x, 40, 3, 8, 12), INKC, outline=0, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def trophy_shelf(seed=1415):
    w, h = 420, 170
    a = Art(w, h, seed)
    a.shape(rect(4, 4, w - 4, 24), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    board(a, 10, 20, w - 10, h - 12, WOOD_DARK, n=2, corner=4)
    chalice_at = lambda x, y, mt: goblet_at(a, x, y, 22, mt, shade(mt, 0.4))  # noqa: E731
    chalice_at(70, 90, GOLD)
    chalice_at(150, 90, SILVER)
    a.shape(ellipse(250, 92, 34, 34, 40), BRASS, outline=DETAIL * 1.3, depth=4, light_k=0.5)  # medal plate
    a.shape([(250, 72), (264, 92), (250, 112), (236, 92)], GEMS[3], outline=FINE * 1.3, corner=1, depth=2, light_k=0.8, mottle=0)
    from obj_magic import skull_at

    skull_at(a, 350, 96, 0.9)
    return a.image()


def coin_stacks(seed=1416):
    s = 200
    a = Art(s, s, seed)
    for x, y, n in ((60, 70, 6), (120, 60, 9), (90, 130, 4), (150, 130, 7)):
        for k in range(n):
            yy = y - k * 3
            a.shape(ellipse(x, yy, 22, 18, 28), tint(GOLD, 0.02 * k), outline=FINE * 1.3, depth=1, shade_k=0.3, light_k=0.4, ao=0, mottle=0)
        a.ink(ellipse(x, y - (n - 1) * 3, 14, 11, 24), FINE, closed=True, color=shade(GOLD, 0.4), alpha=0.7)
    return a.image()


def silver_pile(seed=1417):
    s = 240
    a = Art(s, s, seed)
    from kit import pile as _pile

    m = s / 2
    a.shape(blob(m, m, 88, a.rng, 12, 0.08), shade(SILVER, 0.2), outline=DETAIL, smooth=True, depth=10, shade_k=0.5, light_k=0.4, ao=0.2, mottle=0.06)

    def scoin(art, x, y, hgt):
        col = mix(shade(SILVER, 0.3), tint(SILVER, 0.2), hgt)
        r = art.rng.uniform(7, 10)
        t = art.rng.uniform(0.45, 1.0)
        soft_shadow(art, (x, y), r * 0.9, 2, 3, 0.3, 2.5)
        art.shape(ellipse(x, y, r, r * t, 24, rot=art.rng.uniform(0, 3.14)), col, outline=FINE * 1.3, corner=0, wob=0.1, depth=1.5, shade_k=0.35, light_k=0.5, ao=0, mottle=0)

    _pile(a, m, m, 90, 90, scoin, min_gap=0.3)
    return a.image()


def clothed_round_table(seed=1240):
    s = 320
    a = Art(s, s, seed)
    m = s / 2

    def folds(art, p):
        for t in [2 * math.pi * k / 10 for k in range(10)]:
            art.ink([(m + 118 * math.cos(t), m + 118 * math.sin(t)), (m + 140 * math.cos(t + 0.05), m + 140 * math.sin(t + 0.05))], FINE * 1.3, color=shade(RED, 0.45), alpha=0.8)

    a.shape(scallop(m, m, 146, a.rng, 10, 0.04), RED, depth=10, detail=folds)
    a.ink(ellipse(m, m, 110, 110, 80), FINE * 1.3, closed=True, color=tint(RED, 0.45))
    candle_holder_at(a, m, m, 10)
    for t in (0.4, 2.2, 4.2):
        plate_at(a, m + 70 * math.cos(t), m + 70 * math.sin(t), 26, a.rng.choice(["meat", "bread", "stew"]))
    return a.image()


def feast_table(seed=1241):
    w, h = 760, 260
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), RED, corner=8, depth=10)
    a.shape(rect(30, h / 2 - 30, w - 30, h / 2 + 30), rgb("#e2c068"), outline=DETAIL, corner=3, depth=3, mottle=0.03)
    for k, x in enumerate(range(90, w - 60, 110)):
        plate_at(a, x, 50, 30, ["meat", "bread", "stew"][k % 3])
        plate_at(a, x + 40, h - 50, 30, ["stew", "meat", "bread"][k % 3])
        mug_at(a, x + 40, 56, 16, ang=0.5)
        goblet_at(a, x, h - 56, 14)
    for x in (w * 0.3, w * 0.7):
        candle_holder_at(a, x, h / 2, 11)
    bottle_at(a, w / 2, h / 2, rgb("#5a2a3a"), 18)
    return a.image()


def wine_bottles(seed=1242):
    s = 160
    a = Art(s, s, seed)
    for x, y, c in ((50, 50, rgb("#5a2a3a")), (104, 46, rgb("#3f5a3a")), (70, 108, rgb("#5a2a3a")), (118, 104, rgb("#4a5a2e"))):
        bottle_at(a, x, y, c, 20)
    return a.image()


def gem_pile_of(seed, color):
    s = 180
    a = Art(s, s, seed)

    def gem(art, x, y, hgt):
        r = art.rng.uniform(8, 12)
        c = mix(shade(color, 0.2), tint(color, 0.2), hgt)
        soft_shadow(art, (x, y), r, 2, 3, 0.3, 2)
        art.shape([(x + r * math.cos(t), y + r * math.sin(t)) for t in [k * math.pi / 3 + art.rng.uniform(0, 1) for k in range(6)]], c, outline=FINE * 1.3, corner=1, depth=2, light_k=0.8, mottle=0)
        dot(art, x - r * 0.3, y - r * 0.3, r * 0.2, (255, 255, 255), 0.8)

    pile(a, s / 2, s / 2, 60, 24, gem, min_gap=0.7)
    return a.image()


def scattered_coins(seed=1243):
    s = 240
    a = Art(s, s, seed)
    for _ in range(26):
        coin(a, a.rng.uniform(30, s - 30), a.rng.uniform(30, s - 30), a.rng.random(), 9)
    return a.image()


def bookcase_top(seed=1244):
    w, h = 460, 150
    a = Art(w, h, seed)
    from kit import cabinet
    from obj_furniture import books_row

    cabinet(a, 6, 8, w - 6, h - 8, rgb("#5a3a2a"), front=0.34, inside=books_row)
    return a.image()


def wax_candles(seed=1245):
    s = 160
    a = Art(s, s, seed)
    a.shape(blob(80, 84, 56, a.rng, 10, 0.2), rgb("#f1e6c8"), outline=DETAIL, smooth=True, depth=3, shade_k=0.2, light_k=0.3, mottle=0)  # melted wax
    for x, y, r in ((60, 70, 12), (100, 64, 10), (84, 104, 13)):
        candle(a, x, y, r)
    return a.image()


def royal_cushion(seed=1246):
    s = 170
    a = Art(s, s, seed)
    from kit import cushion as _cushion

    _cushion(a, 20, 20, s - 20, s - 20, RED, tufts=False)
    for x, y in ((20, 20), (s - 20, 20), (20, s - 20), (s - 20, s - 20)):
        a.shape(scallop(x, y, 9, a.rng, 6, 0.3), rgb("#e2c068"), outline=FINE * 1.3, depth=1, mottle=0)
    img = crown(seed).resize((110, 110))
    import numpy as np

    a.c.drawImageRect(skia.Image.fromarray(np.asarray(img), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(30, 30, 110, 110))
    return a.image(grain=0)


TAVERN = {
    # tavern & feast
    "Tavern Table (Ale)": lambda: tavern_table(1201, "ale"),
    "Tavern Table (Cards)": lambda: tavern_table(1202, "cards"),
    "Tavern Table (Dice)": lambda: tavern_table(1203, "dice"),
    "Tavern Table (Meal)": lambda: tavern_table(1204, "meal"),
    "Round Table (Ale)": lambda: tavern_table(1231, "ale", 340, 340, True),
    "Round Table (Meal)": lambda: tavern_table(1232, "meal", 340, 340, True),
    "Candlelit Table": lambda: tavern_table(1233, "candle", 300, 300, True),
    "Card Table": card_table,
    "Dice Set": dice_set,
    "Chess Board": lambda: game_board(1207, "chess"),
    "Checkers Board": lambda: game_board(1234, "checkers"),
    "Bard Stage": bard_stage,
    "Lute": lute,
    "Hand Drum": hand_drum,
    "Flute": flute,
    "Drinking Horn": horn,
    "Tankards": tankard_stack,
    "Ale Mug": ale_mug,
    "Pewter Mug": pewter_mug,
    "Bar Stool": bar_stool,
    "Cushioned Bar Stool": lambda: bar_stool(1235, RED),
    "Keg on Bar": keg_on_bar,
    "Roast Chicken Platter": lambda: food_platter(1218, "chicken"),
    "Ham Platter": lambda: food_platter(1236, "ham"),
    "Fish Platter": lambda: food_platter(1237, "fish"),
    "Bread Basket": bread_basket,
    "Cheese Wheel": cheese_wheel,
    "Pie": pie,
    "Stew Pot": stew_pot,
    "Roast Pig": roast_pig,
    "Spilled Ale": ale_puddle,
    "Bench Table Set": bench_table_set,
    "Menu Board": menu_board,
    "Clothed Round Table": clothed_round_table,
    "Feast Table": feast_table,
    "Wine Bottles": wine_bottles,
    "Melted Candles": wax_candles,
    # library & study
    "Reading Desk": reading_desk,
    "Study Desk": study_desk,
    "Book Pile": book_pile,
    "Small Book Pile": lambda: book_pile(1322, 3, 0.75),
    "Tall Book Pile": lambda: book_pile(1323, 8, 1.0),
    "Scattered Books": scattered_books,
    "Open Book": open_book_obj,
    "Large Open Book": lambda: open_book_obj(1324, 1.5),
    "Red Book": lambda: closed_book(1325, "#8a3f37"),
    "Blue Book": lambda: closed_book(1326, "#3c5a78"),
    "Green Book": lambda: closed_book(1327, "#55743f"),
    "Purple Book": lambda: closed_book(1328, "#694a6e"),
    "Globe": globe_stand,
    "Telescope": telescope,
    "Map Table": map_table,
    "Scroll Rack": scroll_rack,
    "Lectern with Book": lectern_book,
    "Dark Lectern": lambda: lectern_book(1329, WOOD_DARK),
    "Reading Nook": reading_nook,
    "Specimen Jars": specimen_jars,
    "Quill and Inkwell": quill_ink,
    "Letters": letters,
    "Magnifying Glass": magnifying_glass,
    "Compass": compass,
    "Abacus": abacus,
    "Candle Stand": candle_stand,
    "Papers and Hourglass": hourglass_desk,
    "Books with Bookends": bookstand_stack,
    "Brown Book": lambda: closed_book(1330, "#7b5a3c"),
    "Teal Book": lambda: closed_book(1331, "#2f6461"),
    "Tall Bookcase": bookcase_top,
    "Big Book Pile": lambda: book_pile(1332, 6, 1.3),
    # treasure
    "Ornate Chest": ornate_chest,
    "Iron-bound Chest": lambda: ornate_chest(1418, WOOD, IRON),
    "Silver Chest": lambda: ornate_chest(1419, rgb("#5a3a5a"), SILVER),
    "Treasure Chest": treasure_chest_open,
    "Treasure Chest (Gold Only)": lambda: treasure_chest_open(1420, WOOD_DARK, GOLD, False),
    "Iron Treasure Chest": lambda: treasure_chest_open(1421, WOOD, IRON),
    "Gold Pile": gold_pile,
    "Small Gold Pile": lambda: gold_pile(1422, 0.6),
    "Large Gold Pile": lambda: gold_pile(1423, 1.5),
    "Silver Pile": silver_pile,
    "Coin Stacks": coin_stacks,
    "Gem Pile": gem_pile,
    "Crown": crown,
    "Silver Crown": lambda: crown(1424, SILVER),
    "Scepter": scepter,
    "Chalice": chalice,
    "Silver Chalice": lambda: chalice(1425, SILVER),
    "Jewelry Box": jewelry_box,
    "Necklace": necklace,
    "Rings": rings,
    "Treasure Sack": treasure_sack,
    "Gold Bars": gold_bars,
    "Ornate Urn": ornate_urn,
    "Mimic": mimic_chest,
    "Trophy Shelf": trophy_shelf,
    "Ruby Pile": lambda: gem_pile_of(1430, GEMS[0]),
    "Sapphire Pile": lambda: gem_pile_of(1431, GEMS[1]),
    "Emerald Pile": lambda: gem_pile_of(1432, GEMS[2]),
    "Scattered Coins": scattered_coins,
    "Crown on Cushion": royal_cushion,
    "Dark Ornate Chest": lambda: ornate_chest(1433, rgb("#3a2a22"), GOLD),
}

TAVERN_COLORABLE = {"Bard Stage", "Hand Drum", "Cushioned Bar Stool", "Reading Nook", "Clothed Round Table", "Feast Table", "Crown on Cushion"}
