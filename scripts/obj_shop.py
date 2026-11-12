"""Shops, extra kitchen, graveyard and fantasy odds and ends (batch 13).
Top-down, same pen style (red = colorable)."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, dot, fruit, pile, scallop, soft_shadow
from obj_craft import STEEL, handle, rot_pts, shovel_at
from obj_magic import BONE, GOLD, PARCH, WAX, candle, crystal, flask, glow, open_book, skull_at
from obj_nature import GREEN, GREEN_D, GREEN_L, leaf
from obj_stone import DARK_STONE, GREY, LIGHT_STONE, MARBLE, MOSS, moss, stone_block
from obj_town import wheel
from obj_war import arrow_at
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

BREAD = rgb("#c98d4f")
MEAT = rgb("#b5543c")
FAT = rgb("#ecd6c0")
CERAMIC = rgb("#e4dccb")
CLAY = rgb("#bf7a4f")
DIRT = rgb("#7a5e44")
FABRICS = {"Red": RED, "Blue": rgb("#4f6ea8"), "Green": rgb("#5f8f5a"), "Cream": rgb("#e6dcc4"), "Purple": rgb("#7a5a9a")}
SPICES = {"Paprika": rgb("#c8443a"), "Saffron": rgb("#e6a83a"), "Turmeric": rgb("#e8c040"), "Herbs": rgb("#6f9443"), "Pepper": rgb("#4a3e36")}
V = 0.08


# -- small goods (drawn into any art) ---------------------------------------------------------------


def loaf(a, x, y, ang=0.0, L=60, W=30):
    pts = rot_pts(ellipse(x, y, L / 2, W / 2, 32), x, y, ang)
    soft_shadow(a, pts, dx=3, dy=4, alpha=0.3, blur=3)

    def cuts(art, p):
        for k in (-1, 0, 1):
            cx = x + k * L * 0.22
            art.ink(rot_pts([(cx - 4, y - W * 0.3), (cx + 4, y + W * 0.3)], x, y, ang), FINE * 1.3, color=shade(BREAD, 0.45))

    a.shape(pts, vary(a.rng, BREAD, 0.05), outline=DETAIL * 1.2, corner=0, depth=4, light_k=0.45, mottle=0, detail=cuts)


def bun(a, x, y, r=16):
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r * 0.92, 28), vary(a.rng, BREAD, 0.06), outline=DETAIL, depth=3, light_k=0.5, mottle=0)


def steak(a, x, y, ang=0.0, s=1.0):
    pts = rot_pts(chaikin([(x - 30 * s, y - 14 * s), (x + 22 * s, y - 20 * s), (x + 32 * s, y + 4 * s), (x + 10 * s, y + 20 * s), (x - 28 * s, y + 14 * s)], True, 2), x, y, ang)
    soft_shadow(a, pts, dx=3, dy=4, alpha=0.3, blur=3)

    def marbling(art, p):
        art.ink(rot_pts([(x - 20 * s, y + 10 * s), (x + 24 * s, y + 12 * s)], x, y, ang), DETAIL * 1.6, color=FAT, alpha=0.9)
        art.ink(rot_pts([(x - 10 * s, y - 6 * s), (x + 8 * s, y)], x, y, ang), FINE, color=FAT, alpha=0.8)

    a.shape(pts, MEAT, outline=DETAIL * 1.2, corner=0, depth=3, light_k=0.4, mottle=0, detail=marbling)


def ham(a, x, y, ang=0.0):
    pts = rot_pts(chaikin([(x - 46, y - 24), (x + 20, y - 30), (x + 40, y), (x + 20, y + 30), (x - 46, y + 24)], True, 2), x, y, ang)
    soft_shadow(a, pts, dx=4, dy=5)
    a.shape(pts, rgb("#a8483a"), outline=DETAIL * 1.3, corner=0, depth=6, light_k=0.4, mottle=0)
    bone = rot_pts([(x + 34, y - 6), (x + 64, y - 6), (x + 64, y + 6), (x + 34, y + 6)], x, y, ang)
    a.shape(bone, BONE, outline=DETAIL, corner=4, depth=2, mottle=0)


def fish(a, x, y, ang=0.0, s=1.0, col=rgb("#9fb3bc")):
    body = rot_pts(chaikin([(x - 34 * s, y), (x - 10 * s, y - 13 * s), (x + 22 * s, y - 9 * s), (x + 34 * s, y), (x + 22 * s, y + 9 * s), (x - 10 * s, y + 13 * s)], True, 2), x, y, ang)
    tail = rot_pts([(x + 30 * s, y), (x + 46 * s, y - 12 * s), (x + 46 * s, y + 12 * s)], x, y, ang)
    soft_shadow(a, body, dx=2, dy=3, alpha=0.3, blur=2)
    a.shape(tail, shade(col, 0.15), outline=DETAIL, corner=1, depth=1, mottle=0)
    a.shape(body, vary(a.rng, col, 0.06), outline=DETAIL, corner=0, depth=3, light_k=0.5, mottle=0)
    ex, ey = rot_pts([(x - 22 * s, y - 2 * s)], x, y, ang)[0]
    dot(a, ex, ey, 2.4 * s)


def veg(a, x, y, kind):
    if kind == "carrot":
        ang = a.rng.uniform(0, 6.28)
        pts = rot_pts([(x - 22, y - 6), (x + 22, y - 1), (x + 22, y + 1), (x - 22, y + 6)], x, y, ang)
        a.shape(pts, rgb("#e08a3a"), outline=DETAIL, corner=3, depth=2, mottle=0)
        lx, ly = rot_pts([(x - 26, y)], x, y, ang)[0]
        leaf(a, lx, ly, 16, GREEN, ang=ang + math.pi, vein=False, outline=FINE)
    elif kind == "cabbage":
        a.shape(scallop(x, y, 20, a.rng, 8, 0.12), GREEN_L, outline=DETAIL, corner=0, depth=3, light_k=0.4, mottle=0)
        a.ink(scallop(x, y, 11, a.rng, 6, 0.12), FINE, closed=True, color=shade(GREEN_L, 0.45))
    elif kind == "onion":
        a.shape(ellipse(x, y, 13, 13, 24), rgb("#c99a5a"), outline=DETAIL, depth=2, light_k=0.5, mottle=0)
        a.ink([(x - 6, y - 8), (x, y), (x + 6, y - 8)], FINE, color=shade(rgb("#c99a5a"), 0.5))
    else:  # tomato
        a.shape(ellipse(x, y, 13, 13, 24), rgb("#c8443a"), outline=DETAIL, depth=2, light_k=0.55, mottle=0)
        a.shape(scallop(x, y, 4, a.rng, 5, 0.3), GREEN_D, outline=0, depth=1, mottle=0, shade_k=0, light_k=0)


def fabric_bolt_at(a, x, y, color, ang=0.0, L=200, W=46):
    """A bolt of cloth lying down: the rolled body, the cardboard core end."""
    pts = rot_pts([(x - L / 2, y - W / 2), (x + L / 2, y - W / 2), (x + L / 2, y + W / 2), (x - L / 2, y + W / 2)], x, y, ang)
    soft_shadow(a, pts, dx=4, dy=5)

    def folds(art, p):
        for k in (-0.25, 0.2):
            art.ink(rot_pts([(x - L / 2 + 10, y + W * k), (x + L / 2 - 20, y + W * k)], x, y, ang), FINE, color=shade(color, 0.4), alpha=0.6)

    a.shape(pts, color, outline=DETAIL * 1.3, corner=W / 2.4, depth=5, light_k=0.4, detail=folds)
    ex, ey = rot_pts([(x + L / 2 - 8, y)], x, y, ang)[0]
    a.shape(rot_pts(ellipse(ex, ey, 10, W / 2 - 2, 24), ex, ey, ang), tint(color, 0.15), outline=DETAIL, depth=1, mottle=0)
    a.shape(rot_pts(ellipse(ex, ey, 4, 8, 16), ex, ey, ang), rgb("#c9a878"), outline=FINE, depth=1, mottle=0)


def jar_at(a, x, y, r, fill):
    soft_shadow(a, (x, y), r, 3, 4)
    a.shape(ellipse(x, y, r, r, 28), rgb("#bcd6dc"), outline=DETAIL * 1.2, depth=2, light_k=0.6, mottle=0)
    a.shape(ellipse(x, y, r * 0.72, r * 0.72, 24), fill, outline=0, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0.15)
    a.shape(ellipse(x, y, r * 0.4, r * 0.4, 16), rgb("#b88a5a"), outline=FINE, depth=1, mottle=0)


def plate(a, x, y, r=26, food=None):
    soft_shadow(a, (x, y), r, 3, 4)
    a.shape(ellipse(x, y, r, r, 36), CERAMIC, outline=DETAIL * 1.2, depth=2, light_k=0.4, mottle=0)
    a.ink(ellipse(x, y, r * 0.7, r * 0.7, 32), FINE, closed=True, color=shade(CERAMIC, 0.3), alpha=0.8)
    if food:
        food(a, x, y)


def counter(a, w, h, color=WOOD):
    """A shop counter seen from above: its top board and a front lip."""
    board(a, 8, 10, w - 8, h - 10, color, n=2, corner=8)


def heap_in(a, clip_pts, base, cx, cy, R, n, item, ry=None):
    """Goods filling a container: a packed bottom layer, a heap over it, all
    clipped by the container's rim."""
    with a.clip(to_path(clip_pts)):
        a.shape(clip_pts, shade(base, 0.25), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.1)
        pile(a, cx, cy, R * 1.25, int(n * 1.1), lambda art, x, y, h: item(art, x, y, 0.0))
        pile(a, cx, cy, R, n, lambda art, x, y, h: item(art, x, y, 0.3 + 0.7 * h), ry=ry)


# -- shops -------------------------------------------------------------------------------------


def apothecary_counter(seed=1201):
    w, h = 460, 200
    a = Art(w, h, seed)
    counter(a, w, h, WOOD_DARK)
    for k, (x, y) in enumerate(((50, 60), (100, 70), (150, 56), (60, 140), (380, 60), (420, 140))):
        flask(a, x, y, a.rng.uniform(16, 22), [rgb("#c8443a"), rgb("#4f8fd0"), rgb("#6fb84a"), rgb("#a86ad0"), rgb("#e6b84a")][k % 5])
    from obj_magic import mortar

    mortar(a, 230, 100, 30)
    for x in (300, 330):
        jar_at(a, x, 150, 16, rgb("#7fae5a"))
    for _ in range(5):
        leaf(a, a.rng.uniform(180, 300), a.rng.uniform(40, 70), 24, vary(a.rng, GREEN, 0.06), vein=False, outline=FINE)
    return a.image()


def blacksmith_counter(seed=1202):
    w, h = 460, 200
    a = Art(w, h, seed)
    counter(a, w, h, WOOD_DARK)
    from obj_craft import hammer_at, tongs_at
    from obj_war import dagger_at, sword_at

    sword_at(a, 30, 60, 0.0, 230)
    dagger_at(a, 280, 60, 0.05)
    hammer_at(a, 40, 150, -0.1, 100)
    tongs_at(a, 200, 150, -0.05, 110)
    for k in range(3):
        x = 380 + k * 18
        a.shape(rect(x, 120, x + 14, 176), rgb("#c7ccd4"), outline=DETAIL, corner=2, depth=2, light_k=0.6, mottle=0)
    return a.image()


def tailor_counter(seed=1203):
    w, h = 460, 220
    a = Art(w, h, seed)
    counter(a, w, h, WOOD)
    for k, col in enumerate((RED, FABRICS["Blue"], FABRICS["Cream"])):
        fabric_bolt_at(a, 150, 56 + k * 52, col, 0.0, 220, 42)
    # Scissors, a pincushion and a tape measure.
    a.shape(ellipse(340, 80, 22, 22, 28), RED, outline=DETAIL, depth=3, light_k=0.4, mottle=0)
    for t in range(6):
        ang = t * 1.05
        a.ink([(340 + 8 * math.cos(ang), 80 + 8 * math.sin(ang)), (340 + 18 * math.cos(ang), 80 + 18 * math.sin(ang))], FINE, color=rgb("#c7ccd4"))
    for s in (-1, 1):
        a.ink([(370, 150), (420, 150 + s * 8)], DETAIL * 1.4, color=STEEL)
        a.ink(ellipse(358, 150 + s * 12, 10, 7, 16), DETAIL, closed=True, color=rgb("#3a3a40"))
    a.ink(chaikin([(300, 170), (330, 190), (380, 186), (420, 196)], False, 2), DETAIL * 1.6, color=rgb("#e6d29f"))
    return a.image()


def baker_counter(seed=1204):
    w, h = 460, 200
    a = Art(w, h, seed)
    counter(a, w, h, WOOD_LIGHT)
    for k in range(4):
        loaf(a, 70 + k * 64, 64, a.rng.uniform(-0.3, 0.3))
    for k in range(5):
        bun(a, 300 + (k % 3) * 40, 60 + (k // 3) * 40)
    pie_at(a, 120, 150, 40, rgb("#8a3a5a"))
    for k in range(3):
        bun(a, 260 + k * 50, 150, 20)
    return a.image()


def butcher_counter(seed=1205):
    w, h = 460, 200
    a = Art(w, h, seed)
    counter(a, w, h, WOOD_LIGHT)
    with a.clip(to_path(rect(8, 10, w - 8, h - 10))):
        for _ in range(4):
            a.shape(blob(a.rng.uniform(60, 400), a.rng.uniform(40, 160), a.rng.uniform(10, 18), a.rng, 8, 0.3), rgb("#8a2a24"), outline=0, smooth=True, depth=1, shade_k=0, light_k=0.2, ao=0, mottle=0)
    for k in range(3):
        steak(a, 70 + k * 80, 60, a.rng.uniform(-0.4, 0.4))
    ham(a, 330, 70, 0.1)
    for k in range(4):
        x = 60 + k * 26
        a.shape(ellipse(x, 150, 12, 22, 20, rot=0.3), rgb("#a8584a"), outline=DETAIL, depth=2, light_k=0.4, mottle=0)  # sausages
    cleaver_at(a, 260, 160, -0.1)
    return a.image()


def jeweler_display(seed=1206):
    w, h = 400, 220
    a = Art(w, h, seed)
    a.shape(rect(8, 10, w - 8, h - 10), WOOD_DARK, corner=10, depth=10)
    a.shape(rect(26, 28, w - 26, h - 28), rgb("#5a2a3a"), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.4)  # velvet
    gems = [rgb("#d0465a"), rgb("#5fb0d8"), rgb("#7ccf8a"), rgb("#a86ad0"), rgb("#f2e08a")]
    for k in range(10):
        x, y = 60 + (k % 5) * 70, 70 + (k // 5) * 80
        if k % 3 == 0:
            a.ink(ellipse(x, y, 18, 18, 28), DETAIL * 2.2, closed=True, color=GOLD)  # ring
            crystal(a, x, y - 18, 7, gems[k % 5])
        elif k % 3 == 1:
            a.ink(chaikin([(x - 26, y - 16), (x, y + 18), (x + 26, y - 16)], False, 2), DETAIL * 1.2, color=GOLD)  # necklace
            crystal(a, x, y + 18, 8, gems[(k + 1) % 5])
        else:
            crystal(a, x, y, 12, gems[(k + 2) % 5])
    # The glass lid catching light.
    a.ink([(40, 34), (110, 34)], FINE * 2, color=(250, 250, 255), alpha=0.6)
    return a.image()


def fabric_bolt(seed=1210, color=RED):
    w, h = 240, 90
    a = Art(w, h, seed)
    fabric_bolt_at(a, w / 2, h / 2, color, 0.0, 210, 50)
    return a.image()


def fabric_stack(seed=1215):
    w, h = 260, 260
    a = Art(w, h, seed)
    cols = [FABRICS["Blue"], FABRICS["Green"], RED, FABRICS["Cream"], FABRICS["Purple"]]
    for k, c in enumerate(cols):
        fabric_bolt_at(a, w / 2 + a.rng.uniform(-10, 10), 40 + k * 44, c, a.rng.uniform(-0.08, 0.08), 220, 44)
    return a.image()


def clothes_rack(seed=1216):
    w, h = 420, 160
    a = Art(w, h, seed)
    for x in (16, w - 16):
        a.shape(ellipse(x, h / 2, 14, 30, 24), WOOD_DARK, outline=DETAIL * 1.3, depth=3)
    handle(a, 16, h / 2, w - 16, h / 2, 10, WOOD)
    cols = [RED, FABRICS["Blue"], FABRICS["Green"], FABRICS["Cream"], RED, FABRICS["Purple"]]
    for k, c in enumerate(cols):
        x = 60 + k * 58
        # A garment on its hanger, seen from above: its shoulders as a band.
        pts = chaikin([(x - 14, h / 2 - 54), (x + 14, h / 2 - 54), (x + 18, h / 2 + 54), (x - 18, h / 2 + 54)], True, 1)
        a.shape(pts, c, outline=DETAIL * 1.2, corner=0, depth=4, light_k=0.35)
        a.ink([(x - 10, h / 2), (x + 10, h / 2)], DETAIL * 1.4, color=WOOD_DARK)
    return a.image()


def mannequin(seed=1217):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m + 6, 44, 18, 24), WOOD_DARK, outline=DETAIL * 1.2, depth=3)  # stand base peeking
    torso = chaikin([(m - 64, m - 10), (m - 40, m - 30), (m + 40, m - 30), (m + 64, m - 10), (m + 50, m + 20), (m - 50, m + 20)], True, 2)
    a.shape(torso, RED, depth=8, light_k=0.4, detail=lambda art, p: art.ink([(m, m - 28), (m, m + 18)], FINE * 1.3, color=shade(RED, 0.45)))
    a.shape(ellipse(m, m - 12, 16, 16, 24), rgb("#d8c8a8"), outline=DETAIL * 1.2, depth=3, mottle=0)
    return a.image()


def shoe_rack(seed=1218):
    w, h = 360, 160
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD, n=2, corner=6)
    leather = [rgb("#6a422a"), rgb("#8a5a3a"), rgb("#3a2e28")]
    for k in range(4):
        x = 60 + k * 80
        c = leather[k % 3]
        for s in (-1, 1):
            y = h / 2 + s * 30
            pts = chaikin([(x - 30, y), (x - 20, y - 12), (x + 22, y - 10), (x + 32, y), (x + 22, y + 10), (x - 20, y + 12)], True, 2)
            a.shape(pts, c, outline=DETAIL * 1.2, corner=0, depth=3, light_k=0.4, mottle=0)
            a.shape(ellipse(x - 10, y, 10, 6, 16), shade(c, 0.4), outline=FINE, depth=1, mottle=0, shade_k=0, light_k=0)
    return a.image()


def balance_scale(seed=1219):
    w, h = 300, 160
    a = Art(w, h, seed)
    a.shape(rect(w / 2 - 30, h / 2 - 20, w / 2 + 30, h / 2 + 20), WOOD_DARK, outline=DETAIL * 1.3, corner=6, depth=3)
    handle(a, 40, h / 2, w - 40, h / 2, 8, BRASS)
    for x in (50, w - 50):
        a.shape(ellipse(x, h / 2, 44, 44, 40), BRASS, outline=DETAIL * 1.3, depth=4, light_k=0.55)
        a.shape(ellipse(x, h / 2, 32, 32, 32), shade(BRASS, 0.2), outline=FINE, depth=2, shade_k=0, light_k=0, ao=0.3)
    from kit import coin as _coin

    pile(a, 50, h / 2, 20, 6, lambda art, x, y, hh: _coin(art, x, y, hh, 7))
    a.shape(rect(w - 66, h / 2 - 14, w - 34, h / 2 + 14), IRON, outline=DETAIL, corner=3, depth=2, mottle=0)
    a.shape(ellipse(w / 2, h / 2, 12, 12, 20), BRASS, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def cash_box(seed=1220):
    w, h = 220, 170
    a = Art(w, h, seed)
    a.shape(rect(10, 12, w - 10, h - 12), IRON, corner=8, depth=8, light_k=0.4)
    a.shape(rect(24, 26, w - 24, h - 26), rgb("#3a3430"), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5)
    for k in range(3):
        x0 = 30 + k * 54
        a.ink([(x0 + 50, 28), (x0 + 50, h - 28)], DETAIL, color=IRON, taper=False) if k < 2 else None
    from kit import coin as _coin

    gold, silver, copper = rgb("#e2b84e"), rgb("#c7ccd4"), rgb("#c97a4a")
    for k, (n, col) in enumerate(((22, copper), (30, gold), (20, silver))):
        x0 = 26 + k * 56
        cx = x0 + 26
        box = rect(x0, 28, x0 + 52, h - 28)
        with a.clip(to_path(box)):
            a.shape(box, shade(col, 0.35), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.1)
            for _ in range(n):
                x, y = cx + a.rng.uniform(-30, 30), h / 2 + a.rng.uniform(-62, 62)
                soft_shadow(a, (x, y), 8, 2, 3, 0.3, 2)
                a.shape(ellipse(x, y, 9, 9 * a.rng.uniform(0.6, 1), 20, rot=a.rng.uniform(0, 3)), vary(a.rng, col, 0.08), outline=FINE * 1.3, depth=1.5, shade_k=0.35, light_k=0.5, ao=0, mottle=0)
    for x in (80, 136):
        a.ink([(x, 26), (x, h - 26)], DETAIL * 1.6, color=IRON, taper=False)
    return a.image()


def ledger(seed=1221):
    w, h = 240, 170
    a = Art(w, h, seed)
    open_book(a, w / 2 - 10, h / 2, 1.3)
    a.ink([(w - 30, 30), (w - 70, 110)], DETAIL * 1.4, color=rgb("#f1ece2"))  # quill
    a.shape(ellipse(w - 30, h - 30, 14, 14, 20), rgb("#3a3a46"), outline=DETAIL, depth=2, mottle=0)  # inkwell
    return a.image()


def display_table(seed=1222):
    w, h = 400, 240
    a = Art(w, h, seed)
    a.shape(rect(8, 10, w - 8, h - 10), RED, corner=10, depth=8, light_k=0.3)  # tablecloth
    a.ink(rect(22, 24, w - 22, h - 24), FINE * 1.3, closed=True, color=tint(RED, 0.4), alpha=0.9)
    for k in range(3):
        x = 80 + k * 120
        plate(a, x, 80, 34, lambda art, xx, yy: pile(art, xx, yy, 18, 5, lambda a2, x2, y2, hh: fruit(a2, x2, y2, hh)))
    for k in range(4):
        jar_at(a, 70 + k * 86, 170, 18, list(SPICES.values())[k])
    return a.image()


def shop_sign(seed=1223, color=RED):
    w, h = 260, 120
    a = Art(w, h, seed)
    board(a, 10, 14, w - 10, h - 14, WOOD, n=1, corner=8)
    a.ink([(30, h / 2 - 16), (w - 30, h / 2 - 16)], FINE * 1.2, color=shade(WOOD, 0.45), alpha=0.6)
    # Painted emblem: a boot, a loaf or a mug.
    a.shape(ellipse(w / 2, h / 2, 42, 24, 32), color, outline=DETAIL * 1.2, depth=2, mottle=0)
    a.shape(ellipse(w / 2, h / 2, 16, 10, 20), tint(color, 0.5), outline=FINE, depth=1, mottle=0)
    for x in (24, w - 24):
        a.ink(ellipse(x, 20, 7, 7, 16), DETAIL, closed=True, color=IRON)
    return a.image()


def goods_barrel(seed=1230, kind="apples"):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    R = m - 8

    def staves(art, path):
        for i in range(18):
            ang = 2 * math.pi * i / 18
            art.ink([(m + (R - 22) * math.cos(ang), m + (R - 22) * math.sin(ang)), (m + R * math.cos(ang), m + R * math.sin(ang))], DETAIL * 0.8, color=shade(WOOD_DARK, 0.5), alpha=0.9, taper=False)

    a.shape(ellipse(m, m, R, R, 120), WOOD_DARK, depth=10, detail=staves)
    from kit import ring

    ring(a, m, m, R - 9, 8, IRON)
    inner = ellipse(m, m, R - 22, R - 22, 100)
    if kind == "apples":
        heap_in(a, inner, rgb("#7a2a20"), m, m, 64, 22, lambda art, x, y, hh: fruit(art, x, y, hh))
    elif kind == "grain":
        heap_in(a, inner, rgb("#c9a85a"), m, m, 60, 140, lambda art, x, y, hh: dot(art, x, y, art.rng.uniform(1.6, 2.6), mix(rgb("#b8964a"), rgb("#ead48a"), hh)))
    elif kind == "flour":
        def flour(art, p):
            art.shape(blob(m - 6, m - 6, 52, art.rng, 10, 0.12), rgb("#f6f1e6"), outline=0, smooth=True, depth=8, shade_k=0.4, light_k=0.3, ao=0, mottle=0)
            art.ink([(m - 20, m - 10), (m + 10, m - 18)], FINE, color=rgb("#d8d0c0"))

        a.shape(inner, rgb("#ece6d8"), outline=DETAIL * 1.2, depth=10, shade_k=0, light_k=0, ao=0.5, detail=flour)
    elif kind == "fish":
        with a.clip(to_path(inner)):
            a.shape(inner, rgb("#d8d4cc"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
            for _ in range(10):
                fish(a, m + a.rng.uniform(-50, 50), m + a.rng.uniform(-50, 50), a.rng.uniform(0, 6.28), 1.0, rgb("#b8c4c8"))
            for _ in range(60):
                dot(a, m + a.rng.uniform(-70, 70), m + a.rng.uniform(-70, 70), a.rng.uniform(1.4, 2.4), rgb("#f6f6f2"), 0.9)  # salt
    elif kind == "arrows":
        with a.clip(to_path(inner)):
            a.shape(inner, rgb("#3a2e28"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
            for _ in range(26):
                t, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, 60)
                x, y = m + d * math.cos(t), m + d * math.sin(t)
                a.shape(rot_pts([(x - 7, y), (x, y - 8), (x + 7, y), (x, y + 8)], x, y, a.rng.uniform(0, 3)), rgb("#e6dcc4"), outline=FINE, corner=1, depth=1, mottle=0)  # fletchings
    a.ink(inner, DETAIL * 1.2, closed=True)
    return a.image()


def spice_sack(seed=1240, color=SPICES["Paprika"]):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    burlap = rgb("#cdb07e")
    a.shape(blob(m, m, 84, a.rng, 10, 0.06), burlap, smooth=True, depth=10)
    rim = chaikin(blob(m, m, 62, a.rng, 9, 0.08), True, 2)
    a.ink(rim, DETAIL * 2, closed=True, color=shade(burlap, 0.25))

    def powder(art, p):
        art.shape(blob(m - 4, m - 4, 50, art.rng, 10, 0.1), color, outline=0, smooth=True, depth=6, shade_k=0.4, light_k=0.35, ao=0, mottle=0.12)
        for _ in range(40):
            dot(art, m + art.rng.uniform(-50, 50), m + art.rng.uniform(-50, 50), art.rng.uniform(1, 2), shade(color, 0.3), 0.7)

    a.shape(rim, shade(color, 0.3), outline=DETAIL, corner=0, depth=6, shade_k=0, light_k=0, ao=0.4, detail=powder)
    # A wooden scoop.
    handle(a, m + 20, m + 10, m + 80, m + 70, 8, WOOD_LIGHT)
    return a.image()


def pottery_for_sale(seed=1250):
    w, h = 360, 240
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD, n=2, corner=6)
    glazes = [CLAY, rgb("#4f74a8"), rgb("#5f8f6a"), rgb("#e6dcc4"), rgb("#a8483a")]
    for k in range(9):
        x, y = 60 + (k % 4) * 82 + (20 if k >= 4 else 0), 70 + (k // 4) * 70
        if y > h - 40:
            continue
        r = a.rng.uniform(22, 30)
        c = a.rng.choice(glazes)
        soft_shadow(a, (x, y), r, 3, 4)
        a.shape(ellipse(x, y, r, r, 36), c, outline=DETAIL * 1.2, depth=4, light_k=0.5, mottle=0)
        a.shape(ellipse(x, y, r * 0.4, r * 0.4, 20), rgb("#2a221e"), outline=FINE, depth=2, shade_k=0, light_k=0, ao=0.4, mottle=0)
    return a.image()


def rug_pile(seed=1251):
    w, h = 420, 300
    a = Art(w, h, seed)
    cols = [rgb("#7a3a6a"), rgb("#4f6ea8"), RED, rgb("#c99a3a")]
    for k, c in enumerate(cols):
        x0, y0 = 20 + k * 10, 20 + k * 14
        pts = rot_pts(rect(x0, y0, x0 + 340, y0 + 220), x0 + 170, y0 + 110, a.rng.uniform(-0.06, 0.06))
        soft_shadow(a, pts, dx=4, dy=5)

        def pattern(art, p, c=c, x0=x0, y0=y0):
            art.ink(rect(x0 + 20, y0 + 20, x0 + 320, y0 + 200), DETAIL, closed=True, color=rgb("#e6d29f"), wob=0.3)
            cx, cy = x0 + 170, y0 + 110
            art.shape([(cx, cy - 60), (cx + 80, cy), (cx, cy + 60), (cx - 80, cy)], rgb("#e6d29f"), outline=DETAIL, corner=2, depth=2, mottle=0, shade_k=0, light_k=0)

        a.shape(pts, c, outline=DETAIL * 1.4, corner=3, depth=4, detail=pattern)
    return a.image()


# -- kitchen ---------------------------------------------------------------------------------------


def cleaver_at(a, x, y, ang):
    handle(a, x, y, x + 50 * math.cos(ang), y + 50 * math.sin(ang), 11)
    hx, hy = x + 50 * math.cos(ang), y + 50 * math.sin(ang)
    blade = rot_pts([(hx, hy - 12), (hx + 60, hy - 12), (hx + 64, hy + 30), (hx, hy + 30)], hx, hy, ang)
    a.shape(blade, STEEL, outline=DETAIL * 2, corner=3, depth=2, light_k=0.55, mottle=0, var=V)


def pie_at(a, x, y, r, filling):
    soft_shadow(a, (x, y), r, 3, 4)
    a.shape(ellipse(x, y, r, r, 48), rgb("#d8a860"), outline=DETAIL * 1.3, depth=4, light_k=0.4)
    a.shape(ellipse(x, y, r * 0.78, r * 0.78, 40), filling, outline=DETAIL, depth=3, shade_k=0.2, light_k=0.3, mottle=0.08)
    for k in range(4):  # lattice
        t = (k - 1.5) * r * 0.36
        a.ink([(x + t, y - r * 0.75), (x + t, y + r * 0.75)], DETAIL * 1.4, color=rgb("#e8bd74"))
        a.ink([(x - r * 0.75, y + t), (x + r * 0.75, y + t)], DETAIL * 1.4, color=rgb("#e8bd74"))


def pie(seed=1260, filling=rgb("#8a3a5a")):
    s = 140
    a = Art(s, s, seed)
    pie_at(a, s / 2, s / 2, 56, filling)
    return a.image()


def hearth_pot(seed=1261):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 90, rgb("#ff9a3c"), 0.3)
    a.shape(ellipse(m, m, 86, 86, 64), rgb("#3c322d"), depth=6, shade_k=0, light_k=0, ao=0.4, mottle=0.1)
    for _ in range(18):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(60, 82)
        hot = a.rng.random() < 0.5
        a.shape(blob(m + d * math.cos(t), m + d * math.sin(t), 7, a.rng, 6, 0.2), rgb("#e9773a") if hot else rgb("#2e2a28"), outline=FINE, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    a.shape(ellipse(m, m, 60, 60, 56), rgb("#3a3a40"), outline=DETAIL * 1.4, depth=6, light_k=0.45)
    a.shape(ellipse(m, m, 46, 46, 48), rgb("#a86a3a"), outline=DETAIL, depth=5, shade_k=0, light_k=0.3, ao=0.4, detail=lambda art, p: [veg(art, m + art.rng.uniform(-24, 24), m + art.rng.uniform(-24, 24), art.rng.choice(("carrot", "onion"))) for _ in range(4)])
    return a.image()


def pot_rack(seed=1262):
    w, h = 380, 200
    a = Art(w, h, seed)
    # A hanging rack from above: the iron ring frame and the pots under it.
    for k in range(4):
        x = 60 + k * 86
        r = a.rng.uniform(30, 38)
        a.shape(ellipse(x, h / 2, r, r, 36), rgb("#a8683a") if k % 2 else rgb("#3a3a40"), outline=DETAIL * 1.3, depth=4, light_k=0.5)
        a.shape(ellipse(x, h / 2, r * 0.7, r * 0.7, 28), shade(rgb("#a8683a") if k % 2 else rgb("#3a3a40"), 0.3), outline=FINE, depth=3, shade_k=0, light_k=0, ao=0.4)
    a.ink(rect(20, h / 2 - 50, w - 20, h / 2 + 50), DETAIL * 2.4, closed=True, color=IRON)
    for x in (20, w - 20):
        a.ink([(x, h / 2 - 50), (x, h / 2 + 50)], DETAIL * 2.4, color=IRON)
    return a.image()


def pantry_shelf(seed=1263):
    w, h = 420, 150
    a = Art(w, h, seed)
    from kit import cabinet

    def goods(art, x0, y0, x1, y1):
        x = x0 + 10
        while x < x1 - 30:
            kind = art.rng.choice(("jar", "bun", "cheese"))
            if kind == "jar":
                jar_at(art, x + 16, (y0 + y1) / 2 - 2, 15, art.rng.choice(list(SPICES.values())))
            elif kind == "bun":
                bun(art, x + 16, (y0 + y1) / 2 - 2, 15)
            else:
                art.shape(ellipse(x + 18, (y0 + y1) / 2 - 2, 18, 18, 28), rgb("#ecc85a"), outline=DETAIL, depth=2, light_k=0.4, mottle=0)
            x += 40

    cabinet(a, 6, 8, w - 6, h - 8, WOOD, front=0.36, inside=goods)
    return a.image()


def butcher_block(seed=1264):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    a.shape(rect(14, 14, s - 14, s - 14), WOOD_LIGHT, corner=12, depth=10, detail=lambda art, p: [art.ink([(16, y), (s - 16, y)], FINE, color=shade(WOOD_LIGHT, 0.45), alpha=0.6, taper=False) for y in range(40, s - 20, 26)])
    with a.clip(to_path(rect(14, 14, s - 14, s - 14))):
        a.shape(blob(m + 20, m + 30, 30, a.rng, 9, 0.3), rgb("#8a2a24"), outline=0, smooth=True, depth=1, shade_k=0, light_k=0.2, ao=0, mottle=0)
    steak(a, m - 20, m - 30, 0.3, 1.2)
    cleaver_at(a, 40, s - 50, -0.5)
    return a.image()


def dough_table(seed=1265):
    w, h = 400, 220
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD_LIGHT, n=3, corner=8)
    with a.clip(to_path(rect(8, 10, w - 8, h - 10))):
        a.shape(blob(170, 110, 90, a.rng, 12, 0.2, ry=60), rgb("#f2ece0"), outline=0, smooth=True, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.1)  # flour
    a.shape(blob(170, 110, 52, a.rng, 10, 0.08, ry=38), rgb("#ecd8b0"), outline=DETAIL * 1.3, smooth=True, depth=6, light_k=0.45)
    handle(a, 270, 60, 370, 90, 16, WOOD)  # rolling pin
    for x, y in ((300, 160), (340, 170)):
        a.shape(ellipse(x, y, 14, 12, 20), rgb("#f3eee2"), outline=DETAIL, depth=2, light_k=0.4, mottle=0)  # eggs
    return a.image()


def soup_cauldron(seed=1266):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    black = rgb("#45464c")
    for ang in (math.pi * 0.15, math.pi * 1.15):
        x, y = m + (m - 16) * math.cos(ang), m + (m - 16) * math.sin(ang)
        a.shape(ellipse(x, y, 14, 14, 32), black, outline=DETAIL * 1.3, depth=4)
    a.shape(ellipse(m, m, m - 20, m - 20, 96), black, depth=12)
    soup = rgb("#c08a4a")

    def contents(art, p):
        for _ in range(9):
            veg(art, m + art.rng.uniform(-50, 50), m + art.rng.uniform(-50, 50), art.rng.choice(("carrot", "onion", "cabbage")))
        handle(art, m - 10, m, m + 90, m - 70, 10, WOOD_LIGHT)  # ladle

    a.shape(ellipse(m, m, m - 40, m - 40, 96), soup, outline=DETAIL * 1.3, depth=10, shade_k=0, light_k=0.2, ao=0.4, detail=contents)
    return a.image()


def dish_rack(seed=1267):
    w, h = 300, 160
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD, n=1, corner=6)
    for k in range(7):
        x = 40 + k * 36
        a.shape(rect(x - 6, 20, x + 6, h - 20), CERAMIC, outline=DETAIL * 1.2, corner=6, depth=2, light_k=0.4, mottle=0)  # plates on edge
    for x in range(26, w - 20, 36):
        a.ink([(x, 14), (x, h - 14)], DETAIL, color=WOOD_DARK, taper=False)
    return a.image()


def washing_tub(seed=1268):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 96, 96, 64), WOOD, depth=8, detail=lambda art, p: [art.ink([(m + 80 * math.cos(t), m + 80 * math.sin(t)), (m + 96 * math.cos(t), m + 96 * math.sin(t))], DETAIL * 0.7, color=shade(WOOD, 0.5), taper=False) for t in [2 * math.pi * k / 20 for k in range(20)]])
    water = rgb("#9ab8c0")

    def dishes(art, p):
        for _ in range(4):
            plate(art, m + art.rng.uniform(-36, 36), m + art.rng.uniform(-36, 36), art.rng.uniform(20, 26))
        for _ in range(8):
            art.shape(ellipse(m + art.rng.uniform(-60, 60), m + art.rng.uniform(-60, 60), art.rng.uniform(5, 10), art.rng.uniform(5, 10), 16), rgb("#f2f6f6"), outline=FINE, depth=1, mottle=0, shade_k=0, light_k=0.4)  # suds

    a.shape(ellipse(m, m, 78, 78, 64), water, outline=DETAIL * 1.2, depth=8, shade_k=0, light_k=0, ao=0.5, detail=dishes)
    return a.image()


def bread_peel(seed=1269):
    w, h = 340, 120
    a = Art(w, h, seed)
    handle(a, 10, h / 2, 200, h / 2, 14, WOOD)
    a.shape(chaikin([(180, 20), (300, 16), (330, h / 2), (300, h - 16), (180, h - 20)], True, 2), WOOD_LIGHT, depth=4, light_k=0.4)
    loaf(a, 260, h / 2, 0.1)
    return a.image()


def spice_jars(seed=1270):
    w, h = 260, 160
    a = Art(w, h, seed)
    for k, c in enumerate(SPICES.values()):
        jar_at(a, 40 + (k % 3) * 90, 50 + (k // 3) * 64, 24, c)
    return a.image()


def veggie_board(seed=1271):
    w, h = 300, 200
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), WOOD_LIGHT, corner=20, depth=6)
    for kind, x, y in (("carrot", 70, 60), ("carrot", 90, 90), ("cabbage", 200, 70), ("onion", 70, 150), ("tomato", 120, 150), ("tomato", 150, 140)):
        veg(a, x, y, kind)
    for k in range(5):
        a.shape(ellipse(200 + k * 14, 150, 6, 6, 12), rgb("#e08a3a"), outline=FINE, depth=1, mottle=0)  # carrot slices
    from obj_craft import STEEL as _s

    a.shape(rect(160, 110, 260, 122), _s, outline=DETAIL * 1.6, corner=3, depth=2, light_k=0.6, mottle=0, var=V)
    a.shape(rect(260, 108, 290, 124), WOOD_DARK, outline=DETAIL * 1.6, corner=4, depth=2, mottle=0, var=V)
    return a.image()


def kettle(seed=1272):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    a.ink(chaikin([(m - 40, m), (m, m - 56), (m + 40, m)], False, 2), DETAIL * 3, color=INK)
    a.ink(chaikin([(m - 40, m), (m, m - 56), (m + 40, m)], False, 2), DETAIL * 1.8, color=IRON)
    a.shape([(m + 40, m - 6), (m + 70, m - 14), (m + 70, m - 2), (m + 40, m + 8)], rgb("#3a3a40"), outline=DETAIL * 1.3, corner=3, depth=2, mottle=0)
    a.shape(ellipse(m, m, 46, 46, 48), rgb("#3a3a40"), outline=DETAIL * 1.4, depth=6, light_k=0.5)
    a.shape(ellipse(m, m, 18, 18, 24), shade(rgb("#3a3a40"), 0.2), outline=DETAIL, depth=2, mottle=0)
    return a.image()


def teapot_set(seed=1273):
    w, h = 300, 200
    a = Art(w, h, seed)
    a.shape(ellipse(w / 2, h / 2, 136, 86, 64), rgb("#c7ccd4"), outline=DETAIL * 1.3, depth=4, light_k=0.5)  # tray
    teal = rgb("#5f9a9a")
    a.shape([(w / 2 + 40, h / 2 - 6), (w / 2 + 64, h / 2 - 14), (w / 2 + 64, h / 2 - 4), (w / 2 + 40, h / 2 + 8)], teal, outline=DETAIL, corner=3, depth=2, mottle=0)
    a.shape(ellipse(w / 2, h / 2, 40, 40, 40), teal, outline=DETAIL * 1.3, depth=5, light_k=0.5)
    a.shape(ellipse(w / 2, h / 2, 14, 14, 20), tint(teal, 0.2), outline=DETAIL, depth=2, mottle=0)
    for x, y in ((60, 60), (60, 140), (w - 60, 140)):
        a.shape(ellipse(x, y, 18, 18, 24), CERAMIC, outline=DETAIL * 1.2, depth=2, light_k=0.4, mottle=0)
        a.shape(ellipse(x, y, 12, 12, 20), rgb("#8a5a2a"), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def plates_stack(seed=1274):
    s = 140
    a = Art(s, s, seed)
    for k in range(4):
        plate(a, 64 + k * 3, 64 + k * 3, 48)
    return a.image()


def cutlery(seed=1275):
    w, h = 200, 120
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), RED, corner=6, depth=3, light_k=0.3)  # napkin
    for k, kind in enumerate(("fork", "knife", "spoon")):
        x = 50 + k * 50
        a.ink([(x, 24), (x, h - 24)], DETAIL * 2.2, color=INK, taper=False)
        a.ink([(x, 24), (x, h - 24)], DETAIL * 1.2, color=STEEL, taper=False)
        if kind == "spoon":
            a.shape(ellipse(x, 30, 9, 13, 20), STEEL, outline=DETAIL, depth=1, light_k=0.5, mottle=0)
        elif kind == "fork":
            for dx in (-5, 0, 5):
                a.ink([(x + dx, 20), (x + dx, 38)], FINE * 1.3, color=STEEL)
    return a.image()


def cheese_wheel(seed=1276):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    cheese = rgb("#ecc85a")
    a.shape(ellipse(m, m, 70, 70, 64), shade(cheese, 0.1), depth=8, light_k=0.4)
    # A wedge cut out showing the paler inside.
    a.shape([(m, m), (m + 70, m - 10), (m + 50, m + 50)], tint(cheese, 0.3), outline=DETAIL * 1.2, corner=2, depth=2, light_k=0.2, mottle=0)
    for x, y in ((m + 34, m + 10), (m + 46, m + 26)):
        a.shape(ellipse(x, y, 5, 4, 12), shade(cheese, 0.2), outline=FINE, depth=1, mottle=0, shade_k=0, light_k=0)
    return a.image()


def ham_leg(seed=1277):
    w, h = 260, 150
    a = Art(w, h, seed)
    a.c.save()
    a.c.translate(95, h / 2)
    a.c.scale(1.5, 1.5)
    ham(a, 0, 0, 0.0)
    a.c.restore()
    return a.image()


def bread_basket(seed=1278):
    s = 210
    a = Art(s, s, seed)
    m = s / 2
    wick = rgb("#b99258")
    a.shape(ellipse(m, m, 94, 78, 80), wick, depth=10, detail=lambda art, p: [art.ink([(m + 78 * math.cos(t), m + 64 * math.sin(t)), (m + 94 * math.cos(t + 0.05), m + 78 * math.sin(t + 0.05))], FINE * 1.2, color=shade(wick, 0.5), alpha=0.8) for t in [2 * math.pi * k / 36 for k in range(36)]])
    inner = ellipse(m, m, 74, 58, 72)
    with a.clip(to_path(inner)):
        a.shape(inner, rgb("#e8dcc4"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)  # cloth
        for k in range(4):
            loaf(a, m - 40 + k * 26, m + a.rng.uniform(-14, 14), 1.3 + a.rng.uniform(-0.2, 0.2), 70, 28)
    a.ink(inner, DETAIL * 1.2, closed=True, color=shade(wick, 0.55))
    return a.image()


def egg_basket(seed=1279):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    wick = rgb("#b99258")
    a.shape(ellipse(m, m, 80, 80, 80), wick, depth=10)
    inner = ellipse(m, m, 62, 62, 72)
    with a.clip(to_path(inner)):
        a.shape(inner, rgb("#d9bf72"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.1)  # straw
        pile(a, m, m, 70, 14, lambda art, x, y, hh: (soft_shadow(art, (x, y), 12, 2, 3, 0.3, 2), art.shape(ellipse(x, y, 13, 10, 24, rot=art.rng.uniform(0, 3)), mix(rgb("#d8c8a8"), rgb("#f6f0e4"), hh), outline=DETAIL, depth=2, light_k=0.5, mottle=0)))
    a.ink(inner, DETAIL * 1.2, closed=True, color=shade(wick, 0.55))
    return a.image()


# -- graveyard -------------------------------------------------------------------------------------


def grave_mound(a, x0, y0, x1, y1, color=DIRT, grass=False):
    pts = chaikin(rect(x0, y0, x1, y1), True, 3)
    a.shape(pts, color, depth=10, light_k=0.3, detail=lambda art, p: [dot(art, art.rng.uniform(x0, x1), art.rng.uniform(y0, y1), art.rng.uniform(1.4, 2.8), shade(color, 0.4), 0.8) for _ in range(30)])
    if grass:
        for _ in range(8):
            x, y = a.rng.uniform(x0 + 10, x1 - 10), a.rng.uniform(y0 + 10, y1 - 10)
            for t in range(5):
                ang = -math.pi / 2 + (t - 2) * 0.35
                a.ink([(x, y), (x + 10 * math.cos(ang), y + 10 * math.sin(ang))], FINE * 1.2, color=GREEN)


def headstone(seed=1301, shape="round", color=GREY, mossy=False, mound=True):
    w, h = 200, 330 if mound else 130
    a = Art(w, h, seed)
    if mound:
        grave_mound(a, 34, 96, w - 34, h - 14, grass=mossy)
    cx = w / 2
    if shape == "round":
        pts = chaikin([(28, 100), (28, 52), (cx, 20), (w - 28, 52), (w - 28, 100)], True, 2)
    elif shape == "square":
        pts = rect(30, 30, w - 30, 100)
    elif shape == "pointed":
        pts = [(30, 100), (30, 52), (cx, 18), (w - 30, 52), (w - 30, 100)]
    elif shape == "cross":
        pts = [(cx - 16, 14), (cx + 16, 14), (cx + 16, 46), (cx + 56, 46), (cx + 56, 74), (cx + 16, 74), (cx + 16, 104), (cx - 16, 104), (cx - 16, 74), (cx - 56, 74), (cx - 56, 46), (cx - 16, 46)]
    elif shape == "celtic":
        pts = [(cx - 14, 10), (cx + 14, 10), (cx + 14, 44), (cx + 50, 44), (cx + 50, 70), (cx + 14, 70), (cx + 14, 106), (cx - 14, 106), (cx - 14, 70), (cx - 50, 70), (cx - 50, 44), (cx - 14, 44)]
    elif shape == "broken":
        pts = [(28, 100), (28, 60), (60, 44), (84, 66), (112, 40), (w - 28, 56), (w - 28, 100)]
    else:  # obelisk
        pts = rect(cx - 30, 30, cx + 30, 100)
    p = stone_block(a, pts, color, corner=4 if shape not in ("round",) else 0, cracks=1, light_k=0.45)
    if shape == "celtic":
        a.ink(ellipse(cx, 57, 30, 30, 40), DETAIL * 2.6, closed=True, color=INK)
        a.ink(ellipse(cx, 57, 30, 30, 40), DETAIL * 1.4, closed=True, color=color)
    if shape == "obelisk":
        c = [(cx - 30, 30), (cx + 30, 30), (cx + 30, 100), (cx - 30, 100)]
        for k, tone in enumerate((0.2, 0.0, -0.25, 0.05)):
            col = tint(color, tone) if tone > 0 else shade(color, -tone)
            a.shape([c[k], c[(k + 1) % 4], (cx, 65)], col, outline=DETAIL * 0.8, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.ink(c, OUTLINE * 0.8, closed=True, wob=0.3)
    if mossy:
        moss(a, p, 3, (8, 16))
    if shape == "broken":
        piece = [(70, 126), (120, 132), (116, 160), (66, 152)]
        if mound:
            soft_shadow(a, piece, dx=3, dy=4)
            stone_block(a, piece, color, outline=DETAIL * 1.3, corner=4, cracks=0)
    return a.image()


def grave_plot(seed=1320):
    w, h = 220, 400
    a = Art(w, h, seed)
    border = rect(14, 14, w - 14, h - 14)
    stone_block(a, border, GREY, corner=6, cracks=1)
    a.shape(rect(34, 34, w - 34, h - 34), DIRT, outline=DETAIL * 1.2, corner=4, depth=6, shade_k=0, light_k=0, ao=0.4, detail=lambda art, p: [dot(art, art.rng.uniform(34, w - 34), art.rng.uniform(34, h - 34), art.rng.uniform(1.4, 2.6), shade(DIRT, 0.4), 0.8) for _ in range(40)])
    stone_block(a, chaikin([(30, 74), (30, 40), (w / 2, 22), (w - 30, 40), (w - 30, 74)], True, 2), LIGHT_STONE, outline=DETAIL * 1.4, cracks=0, light_k=0.45)
    for x, y in ((80, 200), (140, 260)):
        candle(a, x, y, 10)
    return a.image()


def open_grave(seed=1321):
    w, h = 420, 400
    a = Art(w, h, seed)
    # The pit, the dug earth heaped beside it, a shovel stuck in the heap.
    a.shape(blob(320, 200, 84, a.rng, 12, 0.12, ry=140), DIRT, smooth=True, depth=14, light_k=0.4, detail=lambda art, p: [dot(art, art.rng.uniform(240, 400), art.rng.uniform(60, 340), art.rng.uniform(1.6, 3.4), shade(DIRT, art.rng.uniform(0.2, 0.5)), 0.8) for _ in range(70)])
    a.shape(rect(40, 40, 200, h - 40), rgb("#2e2420"), outline=OUTLINE, corner=6, depth=24, shade_k=0, light_k=0, ao=0.7)
    with a.clip(to_path(rect(40, 40, 200, h - 40))):
        a.shape(rect(30, 30, 210, 70), shade(DIRT, 0.2), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)  # the far wall, lit
    shovel_at(a, 300, 120, 0.9, 110)
    return a.image()


def dirt_pile(seed=1322):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m, 96, a.rng, 12, 0.12), DIRT, smooth=True, depth=14, light_k=0.4, detail=lambda art, p: [dot(art, art.rng.uniform(20, s - 20), art.rng.uniform(20, s - 20), art.rng.uniform(1.6, 3.4), shade(DIRT, art.rng.uniform(0.2, 0.5)), 0.8) for _ in range(60)])
    return a.image()


def coffin_shape(x, y, L, W):
    return [(x - W * 0.35, y - L / 2), (x + W * 0.35, y - L / 2), (x + W / 2, y - L * 0.22), (x + W * 0.32, y + L / 2), (x - W * 0.32, y + L / 2), (x - W / 2, y - L * 0.22)]


def coffin(seed=1323, open_=False, skeleton=False):
    w, h = 200, 440
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2
    outer = coffin_shape(cx, cy, 400, 150)
    a.shape(outer, WOOD_DARK, depth=10, light_k=0.35)
    if not open_:
        a.ink(coffin_shape(cx, cy, 370, 126), FINE * 1.4, closed=True, color=shade(WOOD_DARK, 0.5), alpha=0.8)
        a.shape(rect(cx - 6, cy - 120, cx + 6, cy - 40), BRASS, outline=DETAIL, corner=2, depth=1, mottle=0)
        a.shape(rect(cx - 30, cy - 92, cx + 30, cy - 80), BRASS, outline=DETAIL, corner=2, depth=1, mottle=0)
        return a.image()
    inner = coffin_shape(cx, cy, 370, 124)

    def inside(art, p):
        if skeleton:
            skull_at(art, cx, cy - 130, 1.0)
            art.ink([(cx, cy - 100), (cx, cy + 60)], 12, color=INK, taper=False)
            art.ink([(cx, cy - 100), (cx, cy + 60)], 7, color=BONE, taper=False)
            for k in range(5):
                y = cy - 80 + k * 14
                for s in (-1, 1):
                    art.ink(chaikin([(cx, y), (cx + s * 26, y + 4), (cx + s * 30, y + 16)], False, 1), 8, color=INK, taper=False)
                    art.ink(chaikin([(cx, y), (cx + s * 26, y + 4), (cx + s * 30, y + 16)], False, 1), 4, color=BONE, taper=False)

    a.shape(inner, rgb("#5a2a3a"), outline=DETAIL * 1.2, corner=0, depth=10, shade_k=0, light_k=0, ao=0.5, detail=inside)
    return a.image()


def mausoleum_roof(seed=1324):
    w, h = 400, 440
    a = Art(w, h, seed)
    stone_block(a, rect(10, 10, w - 10, h - 10), DARK_STONE, corner=6, cracks=1)
    # A gable roof of stone slabs, the ridge down the middle, steps in front.
    for x0, x1, tone in ((24, w / 2, 0.1), (w / 2, w - 24, -0.15)):
        col = tint(GREY, tone) if tone > 0 else shade(GREY, -tone)
        a.shape(rect(x0, 24, x1, h - 70), col, outline=DETAIL * 1.3, corner=3, depth=4, light_k=0.3, detail=lambda art, p, x0=x0, x1=x1, col=col: [art.ink([(x0, y), (x1, y)], FINE * 1.2, color=shade(col, 0.4), alpha=0.7, taper=False) for y in range(60, h - 70, 40)])
    a.ink([(w / 2, 24), (w / 2, h - 70)], DETAIL * 2.4)
    for k in range(2):
        stone_block(a, rect(80 + k * 20, h - 70 + k * 22, w - 80 - k * 20, h - 46 + k * 22), LIGHT_STONE, outline=DETAIL * 1.2, corner=3, cracks=0)
    return a.image()


def cemetery_fence(seed=1325, gate=False):
    w, h = 512, 60
    a = Art(w, h, seed)
    a.ink([(10, h / 2), (w - 10, h / 2)], DETAIL * 3, color=INK, taper=False)
    a.ink([(10, h / 2), (w - 10, h / 2)], DETAIL * 1.8, color=rgb("#3a3a40"), taper=False)
    for k in range(17):
        x = 16 + k * 30
        if gate and 6 <= k <= 10:
            continue
        a.shape([(x - 6, h / 2 - 6), (x, h / 2 - 16), (x + 6, h / 2 - 6), (x + 6, h / 2 + 6), (x - 6, h / 2 + 6)], rgb("#3a3a40"), outline=DETAIL * 1.2, corner=1, depth=2, light_k=0.5, mottle=0)
    for x in (12, w - 12) if not gate else (12, 190, 322, w - 12):
        stone_block(a, rect(x - 14, h / 2 - 14, x + 14, h / 2 + 14), GREY, outline=DETAIL * 1.3, corner=3, cracks=0)
    if gate:
        a.ink([(190, h / 2), (250, h / 2 - 26)], DETAIL * 2.6, color=INK)
        a.ink([(190, h / 2), (250, h / 2 - 26)], DETAIL * 1.6, color=rgb("#3a3a40"))
    return a.image()


def shovel_in_dirt(seed=1326):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m + 20, 80, a.rng, 11, 0.14, ry=60), DIRT, smooth=True, depth=10, light_k=0.4)
    shovel_at(a, m - 60, m - 40, 0.6, 100)
    return a.image()


def wreath(seed=1327, flowers=True):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    for k in range(28):
        t = 2 * math.pi * k / 28
        leaf(a, m + 56 * math.cos(t), m + 56 * math.sin(t), 30, vary(a.rng, GREEN_D if k % 2 else GREEN, 0.05), ang=t + math.pi / 2 + a.rng.uniform(-0.3, 0.3), vein=False, outline=FINE * 1.2)
    if flowers:
        for k in range(6):
            t = 2 * math.pi * k / 6 + 0.3
            x, y = m + 56 * math.cos(t), m + 56 * math.sin(t)
            for j in range(5):
                pa = 2 * math.pi * j / 5
                a.shape(ellipse(x + 6 * math.cos(pa), y + 6 * math.sin(pa), 6, 4, 12, rot=pa), RED, outline=FINE, depth=1, mottle=0, shade_k=0.2, light_k=0.3)
            dot(a, x, y, 3, rgb("#f2e08a"))
    a.shape(rect(m - 10, m + 46, m + 10, m + 70), RED, outline=DETAIL, corner=3, depth=1, mottle=0)  # ribbon
    return a.image()


def grave_candles(seed=1328):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, rect(30, 30, s - 30, s - 30), LIGHT_STONE, corner=6, cracks=1, light_k=0.4)
    for x, y, r in ((70, 70, 12), (130, 80, 10), (90, 130, 14), (140, 136, 9)):
        a.shape(scallop(x, y, r + 6, a.rng, 7, 0.2), WAX, outline=DETAIL * 0.9, depth=2, mottle=0)  # melted wax
        candle(a, x, y, r)
    return a.image()


def skull_and_bones(seed=1329):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    for ang in (0.7, -0.7):
        ux, uy = math.cos(ang), math.sin(ang)
        for e in (-1, 1):
            for k in (-1, 1):
                a.shape(ellipse(m + ux * e * 70 - uy * k * 7, m + uy * e * 70 + ux * k * 7, 10, 10, 16), BONE, outline=DETAIL, depth=2, mottle=0)
        a.ink([(m - ux * 70, m - uy * 70), (m + ux * 70, m + uy * 70)], 18, color=INK, taper=False)
        a.ink([(m - ux * 70, m - uy * 70), (m + ux * 70, m + uy * 70)], 11, color=BONE, taper=False)
    skull_at(a, m, m, 1.3)
    return a.image()


def bone_pile(seed=1330):
    s = 260
    a = Art(s, s, seed)
    m = s / 2

    def bone(x, y, L, ang):
        ux, uy = math.cos(ang), math.sin(ang)
        for e in (-1, 1):
            for k in (-1, 1):
                a.shape(ellipse(x + ux * e * L / 2 - uy * k * 6, y + uy * e * L / 2 + ux * k * 6, 8, 8, 14), BONE, outline=DETAIL * 0.9, depth=2, mottle=0)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 14, color=INK, taper=False)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 8, color=BONE, taper=False)

    for _ in range(12):
        bone(m + a.rng.uniform(-60, 60), m + a.rng.uniform(-60, 60), a.rng.uniform(60, 100), a.rng.uniform(0, 3.14))
    for _ in range(3):
        skull_at(a, m + a.rng.uniform(-50, 50), m + a.rng.uniform(-50, 50), a.rng.uniform(0.8, 1.0))
    return a.image()


def angel_statue(seed=1331):
    s = 280
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, rect(14, 14, s - 14, s - 14), DARK_STONE, corner=6, cracks=1)
    # Wings spread behind, robed body, head bowed.
    for side in (-1, 1):
        wing = chaikin([(m + side * 20, m - 10), (m + side * 70, m - 60), (m + side * 120, m - 50), (m + side * 110, m), (m + side * 80, m + 20), (m + side * 30, m + 20)], True, 2)
        a.shape(wing, LIGHT_STONE, outline=DETAIL * 1.3, corner=0, depth=6, light_k=0.4, detail=lambda art, p, side=side: [art.ink([(m + side * 40, m + 6 - k * 10), (m + side * (90 - k * 6), m - 30 - k * 10)], FINE * 1.2, color=shade(LIGHT_STONE, 0.4), alpha=0.8) for k in range(4)])
    a.shape(ellipse(m, m + 30, 50, 60, 48), MARBLE, outline=DETAIL * 1.4, depth=8, light_k=0.4)
    a.shape(ellipse(m, m + 4, 24, 24, 32), tint(MARBLE, 0.15), outline=DETAIL * 1.3, depth=4, light_k=0.5)
    return a.image()


def grave_lantern(seed=1332):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, rect(30, 30, s - 30, s - 30), GREY, corner=4, cracks=0, light_k=0.4)
    glow(a, m, m, 60, rgb("#ffd27a"), 0.4)
    a.shape(rect(m - 26, m - 26, m + 26, m + 26), rgb("#3a3a40"), outline=DETAIL * 1.3, corner=4, depth=3)
    a.shape(rect(m - 16, m - 16, m + 16, m + 16), rgb("#ffe39a"), outline=DETAIL, corner=3, depth=2, shade_k=0, light_k=0.5, mottle=0)
    return a.image()


# -- fantasy remains ------------------------------------------------------------------------------


def dragon_skull(seed=1401):
    w, h = 520, 340
    a = Art(w, h, seed)
    cy = h / 2
    # Long snout to the right, the brow and horns sweeping back (left).
    for s in (-1, 1):
        horn = chaikin([(150, cy + s * 50), (90, cy + s * 110), (20, cy + s * 140), (60, cy + s * 96), (120, cy + s * 40)], True, 2)
        a.shape(horn, shade(BONE, 0.15), outline=OUTLINE * 0.9, corner=0, depth=6, light_k=0.4, detail=lambda art, p, s=s: [art.ink([(110 - k * 22, cy + s * (70 + k * 18)), (124 - k * 22, cy + s * (56 + k * 18))], FINE * 1.2, color=shade(BONE, 0.5), alpha=0.8) for k in range(4)])
    skull = chaikin([(120, cy - 70), (260, cy - 80), (420, cy - 40), (500, cy - 18), (500, cy + 18), (420, cy + 40), (260, cy + 80), (120, cy + 70), (100, cy)], True, 2)

    def holes(art, p):
        for s in (-1, 1):
            art.shape(ellipse(250, cy + s * 44, 32, 22, 32, rot=s * 0.2), rgb("#2a221e"), outline=DETAIL, depth=2, shade_k=0, light_k=0, ao=0, mottle=0)
            art.shape(ellipse(460, cy + s * 12, 10, 7, 16), rgb("#2a221e"), outline=FINE, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        art.ink([(140, cy), (420, cy)], FINE * 1.3, color=shade(BONE, 0.45), alpha=0.8)
        for x in range(300, 480, 22):
            for s in (-1, 1):
                art.shape([(x, cy + s * (34 - (x - 300) * 0.12)), (x + 6, cy + s * (46 - (x - 300) * 0.12)), (x + 12, cy + s * (34 - (x - 300) * 0.12))], rgb("#f6f0e4"), outline=FINE, corner=0, depth=1, mottle=0)

    a.shape(skull, BONE, depth=14, light_k=0.4, detail=holes)
    return a.image()


def giant_ribcage(seed=1402):
    w, h = 520, 400
    a = Art(w, h, seed)
    cy = h / 2
    a.ink([(20, cy), (w - 20, cy)], 26, color=INK, taper=False)
    a.ink([(20, cy), (w - 20, cy)], 18, color=BONE, taper=False)
    for k in range(9):
        x = 60 + k * 50
        L = 150 - abs(k - 3) * 12
        for s in (-1, 1):
            rib = chaikin([(x, cy), (x + 22, cy + s * L * 0.6), (x - 4, cy + s * L)], False, 2)
            a.ink(rib, 24, color=INK, taper=False, wob=0.3, var=0.08)
            a.ink(rib, 15, color=BONE, taper=False, wob=0.3, var=0.08)
        a.shape(ellipse(x, cy, 14, 16, 20), shade(BONE, 0.1), outline=DETAIL, depth=2, mottle=0)
    return a.image()


def tentacle(seed=1403):
    w, h = 460, 300
    a = Art(w, h, seed)
    from pen import normals

    spine = [(30 + 380 * t, h / 2 + 90 * math.sin(t * 5) * (1 - t * 0.5)) for t in [k / 40 for k in range(41)]]
    ws = [80 * (1 - k / 44) + 6 for k in range(41)]
    ns = normals(spine, False)
    left = [(x + nx * w_ / 2, y + ny * w_ / 2) for (x, y), (nx, ny), w_ in zip(spine, ns, ws)]
    right = [(x - nx * w_ / 2, y - ny * w_ / 2) for (x, y), (nx, ny), w_ in zip(spine, ns, ws)]
    col = rgb("#8a5a8a")

    def suckers(art, p):
        for k in range(2, 36, 3):
            x, y = spine[k]
            nx, ny = ns[k]
            r = ws[k] * 0.18
            art.shape(ellipse(x - nx * ws[k] * 0.2, y - ny * ws[k] * 0.2, r, r, 16), tint(col, 0.4), outline=FINE * 1.2, depth=1, mottle=0, shade_k=0, light_k=0.3)

    a.shape(left + right[::-1], col, outline=OUTLINE * 0.9, corner=0, wob=0.2, depth=10, light_k=0.4, detail=suckers)
    return a.image()


def egg_nest(seed=1404, egg=rgb("#e6dcc4")):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    twig = rgb("#8a6a4a")
    a.shape(ellipse(m, m, 110, 110, 80), shade(twig, 0.2), depth=10)
    for _ in range(90):
        t = a.rng.uniform(0, 6.28)
        d = a.rng.uniform(70, 106)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        tt = t + math.pi / 2 + a.rng.uniform(-0.5, 0.5)
        a.ink([(x - 16 * math.cos(tt), y - 16 * math.sin(tt)), (x + 16 * math.cos(tt), y + 16 * math.sin(tt))], DETAIL * 1.1, color=vary(a.rng, twig, 0.15), alpha=0.95)
    a.shape(ellipse(m, m, 70, 70, 64), shade(twig, 0.45), outline=DETAIL, depth=8, shade_k=0, light_k=0, ao=0.5)
    for k in range(3):
        t = 2 * math.pi * k / 3 + 0.4
        x, y = m + 30 * math.cos(t), m + 30 * math.sin(t)
        soft_shadow(a, (x, y), 28, 3, 4)
        a.shape(ellipse(x, y, 26, 34, 32, rot=t), egg, outline=DETAIL * 1.3, depth=4, light_k=0.55, detail=lambda art, p, x=x, y=y: [dot(art, x + art.rng.uniform(-14, 14), y + art.rng.uniform(-20, 20), art.rng.uniform(2, 4), shade(egg, 0.35), 0.7) for _ in range(6)])
    return a.image()


def dragon_egg(seed=1405, color=RED):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 60, color, 0.3)

    def scales(art, p):
        for r in range(2):
            for k in range(10):
                t = 2 * math.pi * k / 10 + r * 0.3
                d = 20 + r * 22
                art.ink([(m + d * math.cos(t) - 8, m + d * math.sin(t) * 1.3), (m + d * math.cos(t), m + d * math.sin(t) * 1.3 + 6), (m + d * math.cos(t) + 8, m + d * math.sin(t) * 1.3)], FINE * 1.2, color=shade(color, 0.45), alpha=0.8)

    a.shape(ellipse(m, m, 48, 62, 48), color, outline=OUTLINE * 0.85, depth=8, light_k=0.55, detail=scales)
    return a.image()


def broken_wheel(seed=1406):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    rim = [(m + 96 * math.cos(t), m + 96 * math.sin(t)) for t in [0.3 + k * (2 * math.pi - 1.4) / 40 for k in range(41)]]
    a.ink(rim, 26, color=INK, taper=False)
    a.ink(rim, 18, color=WOOD_DARK, taper=False)
    for k in range(10):
        t = 2 * math.pi * k / 10
        L = 84 if k not in (0, 9) else a.rng.uniform(30, 50)
        handle(a, m + 16 * math.cos(t), m + 16 * math.sin(t), m + L * math.cos(t), m + L * math.sin(t), 9, WOOD)
    a.shape(ellipse(m, m, 22, 22, 28), WOOD, outline=DETAIL * 1.4, depth=3, mottle=0)
    piece = [(m + 90, m - 40), (m + 112, m + 6), (m + 100, m + 10), (m + 80, m - 34)]
    a.shape(piece, WOOD_DARK, outline=DETAIL * 1.3, corner=3, depth=3)
    return a.image()


def portal_ring(seed=1407, color=rgb("#8a6ad8")):
    s = 460
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 200, color, 0.35)
    n = 12
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n + 0.03, 2 * math.pi * (k + 1) / n - 0.03
        pts = [(m + 200 * math.cos(t0 + (t1 - t0) * j / 4), m + 200 * math.sin(t0 + (t1 - t0) * j / 4)) for j in range(5)] + [(m + 160 * math.cos(t1 - (t1 - t0) * j / 4), m + 160 * math.sin(t1 - (t1 - t0) * j / 4)) for j in range(5)]
        stone_block(a, pts, GREY, outline=DETAIL * 1.3, corner=4, cracks=0, light_k=0.4)
        mx, my = m + 180 * math.cos((t0 + t1) / 2), m + 180 * math.sin((t0 + t1) / 2)
        a.ink([(mx - 5, my - 6), (mx + 3, my), (mx - 3, my + 7)], DETAIL, color=tint(color, 0.4))
    swirl = [(m + (6 + 4.6 * t) * math.cos(t * 0.9), m + (6 + 4.6 * t) * math.sin(t * 0.9)) for t in [k * 0.25 for k in range(130)]]
    a.shape(ellipse(m, m, 156, 156, 96), shade(color, 0.35), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.4, detail=lambda art, p: art.ink(swirl, DETAIL * 1.4, color=tint(color, 0.45), alpha=0.9))
    return a.image()


def statue_head(seed=1408):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    p = stone_block(a, ellipse(m, m, 80, 90, 64), LIGHT_STONE, cracks=2, light_k=0.4)
    a.shape(ellipse(m, m - 40, 50, 30, 40), GREY, outline=DETAIL * 1.2, depth=3, mottle=0)  # hair
    for dx in (-24, 24):
        a.ink([(m + dx - 12, m - 4), (m + dx + 12, m - 4)], DETAIL * 1.4)
    a.ink([(m, m), (m - 6, m + 26), (m + 6, m + 26)], DETAIL * 1.2)
    a.ink([(m - 18, m + 48), (m + 18, m + 48)], DETAIL * 1.2)
    moss(a, p, 2, (10, 18))
    return a.image()


def statue_hand(seed=1409):
    w, h = 260, 200
    a = Art(w, h, seed)
    palm = chaikin([(40, 70), (150, 60), (170, 140), (60, 150)], True, 2)
    stone_block(a, palm, LIGHT_STONE, cracks=1, light_k=0.4)
    for k in range(4):
        y = 70 + k * 22
        stone_block(a, rect(160, y - 9, 236 - abs(k - 1.5) * 10, y + 9), LIGHT_STONE, outline=DETAIL * 1.3, corner=8, cracks=0, light_k=0.4)
    stone_block(a, chaikin([(80, 140), (110, 180), (140, 176), (120, 140)], True, 1), LIGHT_STONE, outline=DETAIL * 1.3, cracks=0)  # thumb
    stone_block(a, rect(10, 80, 50, 140), GREY, outline=DETAIL * 1.3, corner=6, cracks=1)  # broken wrist
    return a.image()


def totem_top(seed=1410):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    # The carved head at the top of a totem pole, from above: a round crown
    # with outspread wings to the sides.
    for side in (-1, 1):
        wing = [(m + side * 40, m - 20), (m + side * 96, m - 34), (m + side * 90, m + 10), (m + side * 40, m + 20)]
        a.shape(wing, RED, outline=DETAIL * 1.3, corner=3, depth=5, light_k=0.3)
        for k in range(3):
            a.ink([(m + side * (50 + k * 14), m - 22), (m + side * (50 + k * 14), m + 12)], FINE * 1.3, color=shade(RED, 0.45))
    a.shape(ellipse(m, m, 50, 50, 48), WOOD, outline=OUTLINE * 0.85, depth=8, light_k=0.4, detail=lambda art, p: [art.ink(ellipse(m, m, r, r, 40), FINE * 1.2, closed=True, color=shade(WOOD, 0.45), alpha=0.8) for r in (20, 36)])
    a.shape([(m - 10, m - 50), (m + 10, m - 50), (m, m - 74)], rgb("#e6b84a"), outline=DETAIL, corner=1, depth=2, mottle=0)  # beak
    return a.image()


def signal_fire(seed=1411):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, ellipse(m, m, 130, 130, 64), GREY, cracks=1)
    glow(a, m, m, 110, rgb("#ff9a3c"), 0.4)
    # A tall stack of logs (seen from above as a log-cabin square) burning.
    for k in range(4):
        r = 80 - k * 14
        for side in (-1, 1):
            handle(a, m - r, m + side * r, m + r, m + side * r, 16, vary(a.rng, WOOD_DARK, 0.05)) if k % 2 == 0 else handle(a, m + side * r, m - r, m + side * r, m + r, 16, vary(a.rng, WOOD_DARK, 0.05))
    for r, col in ((56, rgb("#e9773a")), (38, rgb("#f4b544")), (18, rgb("#fde8a6"))):
        a.shape(scallop(m, m, r, a.rng, 8, 0.22), col, outline=DETAIL if r > 20 else 0, depth=3, shade_k=0.2, light_k=0, ao=0, mottle=0)
    return a.image()


def meteor_crater(seed=1412):
    s = 420
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m, 190, a.rng, 16, 0.08), rgb("#8a7a64"), smooth=True, depth=20, light_k=0.4, detail=lambda art, p: [dot(art, art.rng.uniform(20, s - 20), art.rng.uniform(20, s - 20), art.rng.uniform(2, 5), shade(rgb("#8a7a64"), 0.4), 0.8) for _ in range(80)])
    a.shape(blob(m, m, 130, a.rng, 14, 0.08), rgb("#4a3e34"), outline=DETAIL * 1.3, smooth=True, depth=24, shade_k=0, light_k=0, ao=0.6)
    glow(a, m, m, 80, rgb("#ff7a3c"), 0.45)
    a.shape(blob(m, m, 46, a.rng, 9, 0.2), rgb("#3a2e2a"), outline=OUTLINE * 0.9, smooth=True, depth=10, light_k=0.3, detail=lambda art, p: [art.ink([(m + art.rng.uniform(-30, 30), m + art.rng.uniform(-30, 30)), (m + art.rng.uniform(-30, 30), m + art.rng.uniform(-30, 30))], DETAIL, color=rgb("#ff9a3c"), alpha=0.9) for _ in range(5)])
    return a.image()


def bone_scatter(seed=1413):
    s = 300
    a = Art(s, s, seed)

    def bone(x, y, L, ang):
        ux, uy = math.cos(ang), math.sin(ang)
        for e in (-1, 1):
            for k in (-1, 1):
                a.shape(ellipse(x + ux * e * L / 2 - uy * k * 5, y + uy * e * L / 2 + ux * k * 5, 7, 7, 14), BONE, outline=DETAIL * 0.9, depth=2, mottle=0)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 12, color=INK, taper=False)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 7, color=BONE, taper=False)

    for _ in range(7):
        bone(a.rng.uniform(60, s - 60), a.rng.uniform(60, s - 60), a.rng.uniform(50, 90), a.rng.uniform(0, 3.14))
    if a.rng.random() < 0.7:
        skull_at(a, a.rng.uniform(80, s - 80), a.rng.uniform(80, s - 80), 1.0)
    return a.image()


def spider_eggs(seed=1414):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    web = rgb("#e8e4dc")
    for _ in range(20):
        t = a.rng.uniform(0, 6.28)
        a.ink([(m, m), (m + 110 * math.cos(t), m + 110 * math.sin(t))], FINE, color=web, alpha=0.8)
    for _ in range(7):
        x, y = m + a.rng.uniform(-60, 60), m + a.rng.uniform(-60, 60)
        r = a.rng.uniform(18, 28)
        soft_shadow(a, (x, y), r, 3, 4)
        a.shape(ellipse(x, y, r, r * 1.2, 28, rot=a.rng.uniform(0, 3)), rgb("#efe9dc"), outline=DETAIL * 1.2, depth=4, light_k=0.5, detail=lambda art, p, x=x, y=y, r=r: [art.ink([(x - r, y + k * 6), (x + r, y + k * 6 + 4)], FINE * 0.8, color=shade(web, 0.25), alpha=0.6) for k in (-1, 0, 1)])
    return a.image()


def giant_feather(seed=1415, color=rgb("#4f6ea8")):
    w, h = 400, 140
    a = Art(w, h, seed)
    vane = chaikin([(30, h / 2), (120, h / 2 - 46), (300, h / 2 - 40), (380, h / 2), (300, h / 2 + 40), (120, h / 2 + 46)], True, 2)
    a.shape(vane, color, depth=6, light_k=0.4, detail=lambda art, p: [art.ink([(x, h / 2), (x + 30, h / 2 + s * 40)], FINE * 1.1, color=shade(color, 0.4), alpha=0.7) for x in range(60, 340, 14) for s in (-1, 1)])
    a.ink([(10, h / 2 + 4), (370, h / 2)], DETAIL * 1.6, color=tint(color, 0.6))
    return a.image()


def geode(seed=1416, color=rgb("#a86ad0")):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, blob(m, m, 96, a.rng, 10, 0.12), GREY, smooth=True, cracks=0)
    a.shape(blob(m, m, 66, a.rng, 9, 0.12), shade(color, 0.3), outline=DETAIL * 1.2, smooth=True, depth=8, shade_k=0, light_k=0, ao=0.5)
    for _ in range(12):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(10, 50)
        crystal(a, m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(8, 14), vary(a.rng, color, 0.08), a.rng.uniform(0, 1))
    return a.image()


# -- catalog -----------------------------------------------------------------------------------------

SHOP = {
    # shops
    "Apothecary Counter": apothecary_counter,
    "Blacksmith Counter": blacksmith_counter,
    "Tailor Counter": tailor_counter,
    "Baker Counter": baker_counter,
    "Butcher Counter": butcher_counter,
    "Jeweler Display": jeweler_display,
    "Fabric Bolt": lambda: fabric_bolt(1210, RED),
    "Blue Fabric Bolt": lambda: fabric_bolt(1211, FABRICS["Blue"]),
    "Green Fabric Bolt": lambda: fabric_bolt(1212, FABRICS["Green"]),
    "Cream Fabric Bolt": lambda: fabric_bolt(1213, FABRICS["Cream"]),
    "Purple Fabric Bolt": lambda: fabric_bolt(1214, FABRICS["Purple"]),
    "Fabric Stack": fabric_stack,
    "Clothes Rack": clothes_rack,
    "Mannequin": mannequin,
    "Shoe Rack": shoe_rack,
    "Balance Scale": balance_scale,
    "Cash Box": cash_box,
    "Ledger": ledger,
    "Display Table": display_table,
    "Shop Sign": shop_sign,
    "Apple Barrel (Open)": lambda: goods_barrel(1230, "apples"),
    "Grain Barrel": lambda: goods_barrel(1231, "grain"),
    "Flour Barrel": lambda: goods_barrel(1232, "flour"),
    "Salt Fish Barrel": lambda: goods_barrel(1233, "fish"),
    "Arrow Barrel": lambda: goods_barrel(1234, "arrows"),
    "Paprika Sack": lambda: spice_sack(1240, SPICES["Paprika"]),
    "Saffron Sack": lambda: spice_sack(1241, SPICES["Saffron"]),
    "Turmeric Sack": lambda: spice_sack(1242, SPICES["Turmeric"]),
    "Herb Sack": lambda: spice_sack(1243, SPICES["Herbs"]),
    "Pepper Sack": lambda: spice_sack(1244, SPICES["Pepper"]),
    "Pottery Stall": pottery_for_sale,
    "Rug Pile": rug_pile,
    # kitchen
    "Hearth Pot": hearth_pot,
    "Pot Rack": pot_rack,
    "Pantry Shelf": pantry_shelf,
    "Butcher Block": butcher_block,
    "Dough Table": dough_table,
    "Berry Pie": lambda: pie(1260, rgb("#8a3a5a")),
    "Apple Pie": lambda: pie(1261, rgb("#d8a050")),
    "Cherry Pie": lambda: pie(1262, rgb("#b8343a")),
    "Soup Cauldron": soup_cauldron,
    "Dish Rack": dish_rack,
    "Washing Tub": washing_tub,
    "Bread Peel": bread_peel,
    "Spice Jars": spice_jars,
    "Veggie Board": veggie_board,
    "Kettle": kettle,
    "Tea Set": teapot_set,
    "Plate Stack": plates_stack,
    "Cutlery": cutlery,
    "Cheese Wheel": cheese_wheel,
    "Ham Leg": ham_leg,
    "Bread Basket": bread_basket,
    "Egg Basket": egg_basket,
    # graveyard
    "Rounded Gravestone": lambda: headstone(1301, "round"),
    "Square Gravestone": lambda: headstone(1302, "square"),
    "Pointed Gravestone": lambda: headstone(1303, "pointed"),
    "Cross Gravestone": lambda: headstone(1304, "cross"),
    "Celtic Cross": lambda: headstone(1305, "celtic"),
    "Small Obelisk": lambda: headstone(1306, "obelisk"),
    "Broken Gravestone": lambda: headstone(1307, "broken"),
    "Mossy Gravestone": lambda: headstone(1308, "round", DARK_STONE, mossy=True),
    "Mossy Cross": lambda: headstone(1309, "cross", DARK_STONE, mossy=True),
    "Dark Gravestone": lambda: headstone(1310, "square", DARK_STONE),
    "Marble Gravestone": lambda: headstone(1311, "pointed", MARBLE),
    "Headstone": lambda: headstone(1312, "round", GREY, mound=False),
    "Stone Cross": lambda: headstone(1313, "cross", GREY, mound=False),
    "Grave Plot": grave_plot,
    "Open Grave": open_grave,
    "Dirt Pile": dirt_pile,
    "Coffin": lambda: coffin(1323),
    "Open Coffin": lambda: coffin(1324, open_=True),
    "Coffin with Skeleton": lambda: coffin(1325, open_=True, skeleton=True),
    "Mausoleum Roof": mausoleum_roof,
    "Cemetery Fence": cemetery_fence,
    "Cemetery Gate": lambda: cemetery_fence(1326, gate=True),
    "Shovel in Dirt": shovel_in_dirt,
    "Flower Wreath": wreath,
    "Wreath": lambda: wreath(1328, flowers=False),
    "Grave Candles": grave_candles,
    "Skull and Bones": skull_and_bones,
    "Bone Pile": bone_pile,
    "Angel Statue": angel_statue,
    "Grave Lantern": grave_lantern,
    # fantasy
    "Dragon Skull": dragon_skull,
    "Giant Ribcage": giant_ribcage,
    "Tentacle": tentacle,
    "Egg Nest": egg_nest,
    "Speckled Egg Nest": lambda: egg_nest(1406, rgb("#b8c8a8")),
    "Dragon Egg": dragon_egg,
    "Blue Dragon Egg": lambda: dragon_egg(1407, rgb("#4f6ea8")),
    "Green Dragon Egg": lambda: dragon_egg(1408, rgb("#5f8f5a")),
    "Broken Wheel": broken_wheel,
    "Portal Ring": portal_ring,
    "Green Portal Ring": lambda: portal_ring(1409, rgb("#4fc28a")),
    "Statue Head": statue_head,
    "Statue Hand": statue_hand,
    "Totem Top": totem_top,
    "Signal Fire": signal_fire,
    "Meteor Crater": meteor_crater,
    "Bone Scatter": bone_scatter,
    "Bone Scatter 2": lambda: bone_scatter(1420),
    "Spider Egg Sacs": spider_eggs,
    "Giant Feather": giant_feather,
    "Red Feather": lambda: giant_feather(1416, rgb("#a8483a")),
    "Amethyst Geode": geode,
    "Sapphire Geode": lambda: geode(1417, rgb("#5f8fd8")),
}

SHOP_COLORABLE = {
    "Tailor Counter", "Fabric Bolt", "Fabric Stack", "Clothes Rack", "Mannequin", "Display Table", "Shop Sign",
    "Rug Pile", "Cutlery", "Flower Wreath", "Wreath", "Totem Top", "Dragon Egg",
}
