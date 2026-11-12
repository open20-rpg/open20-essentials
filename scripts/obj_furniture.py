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


def raised_shadow(a, seat, raised, blur=10, alpha=0.45):
    """The soft shadow raised parts (a backrest, arms) cast onto the lower
    seat next to them: drawn on the seat only."""
    import skia as _sk
    from pen import to_path as _tp

    with a.clip(_tp(seat)):
        for r in raised:
            q = _tp([(x + 6, y + 8) for x, y in r])
            a.fill_path(q, INK, alpha, blur=blur)


def upholstered(a, seat_boxes, back_box, arm_boxes, frame_box, frame=WOOD_DARK, color=RED):
    """Seat cushions low, backrest and arms higher: those are a touch lighter
    and cast a soft shadow onto the seat."""
    a.shape(rect(*frame_box), frame, corner=24, depth=10)
    for box in seat_boxes:
        cushion(a, *box, color=shade(color, 0.08))
    raised = [rect(*back_box)] + [rect(*b) for b in arm_boxes]
    for box in seat_boxes:
        raised_shadow(a, rect(*box), raised)
    hi = tint(color, 0.1)
    cushion(a, *back_box, color=hi)
    for b in arm_boxes:
        cushion(a, *b, color=hi, tufts=False, corner=14)


def furniture_top(a, x0, y0, x1, y1, color, n=2):
    """A piece of furniture seen straight from above: its top board, with a
    molded edge (no fronts or drawers: those can't be seen from above)."""
    board(a, x0, y0, x1, y1, color, n=n, corner=6)
    a.ink(rect(x0 + 10, y0 + 9, x1 - 10, y1 - 9), FINE * 1.1, closed=True, color=shade(color, 0.5), alpha=0.7, wob=0.4)


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
    w, h = 400, 170
    a = Art(w, h, seed)
    furniture_top(a, 6, 8, w - 6, h - 8, WOOD_DARK, n=3)
    return a.image()


def dresser(seed=63):
    w, h = 360, 160
    a = Art(w, h, seed)
    furniture_top(a, 6, 8, w - 6, h - 8, WOOD, n=2)
    a.shape(ellipse(80, 72, 34, 26, 40), rgb("#b9d3dc"), outline=DETAIL * 1.2, depth=5, light_k=0.6)
    a.shape(ellipse(w - 80, 68, 12, 12, 20), rgb("#f1e6c8"), outline=DETAIL, depth=3, mottle=0)
    a.shape(rect(160, 50, 230, 104), rgb("#3c5a78"), outline=DETAIL, corner=4, depth=4, mottle=0)
    a.shape(rect(166, 56, 224, 98), PAGES, outline=FINE, corner=2, depth=2, mottle=0, shade_k=0.2, light_k=0)
    return a.image()


def nightstand(seed=64):
    s = 160
    a = Art(s, s, seed)
    furniture_top(a, 8, 8, s - 8, s - 8, WOOD, n=1)
    a.shape(ellipse(62, 62, 18, 18, 24), rgb("#d9c28a"), outline=DETAIL, depth=4)
    a.shape(ellipse(62, 62, 7, 7, 16), rgb("#fbf0c8"), outline=FINE, depth=2, mottle=0)
    a.shape(rect(86, 90, 132, 132), rgb("#8a3f37"), outline=DETAIL, corner=3, depth=3, mottle=0)
    return a.image()


def cabinet_obj(seed=65):
    w, h = 300, 160
    a = Art(w, h, seed)
    furniture_top(a, 6, 8, w - 6, h - 8, WOOD_LIGHT, n=2)
    a.shape(ellipse(70, 70, 20, 20, 28), rgb("#9fb8a8"), outline=DETAIL, depth=4, light_k=0.6)
    a.shape(ellipse(70, 70, 9, 9, 20), rgb("#b88a5a"), outline=FINE, depth=2, mottle=0)
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
    upholstered(a, [(56, 66, s - 56, s - 30)], (28, 20, s - 28, 70), [(18, 60, 58, s - 24), (s - 58, 60, s - 18, s - 24)], (12, 12, s - 12, s - 16))
    return a.image()


def sofa(seed=71):
    w, h = 512, 220
    a = Art(w, h, seed)
    upholstered(a, [(62, 68, w / 2, h - 28), (w / 2, 68, w - 62, h - 28)], (24, 16, w - 24, 72), [(14, 58, 64, h - 22), (w - 64, 58, w - 14, h - 22)], (8, 8, w - 8, h - 12))
    return a.image()


def footstool(seed=72):
    s = 150
    a = Art(s, s, seed)
    a.shape(rect(12, 12, s - 12, s - 12), WOOD_DARK, corner=16, depth=6)
    cushion(a, 22, 22, s - 22, s - 22, RED)
    return a.image()


def throne(seed=73):
    """A throne on a stone dais: dark carved wood with gold trim, a tall
    crested back (lighter: it rises highest), arms ending in gold knobs and a
    recolorable seat cushion shaded by them."""
    w, h = 340, 360
    a = Art(w, h, seed)
    gold = rgb("#d6ae4c")
    wood = rgb("#5e3b2a")
    a.shape(rect(8, 30, w - 8, h - 8), STONE, corner=10, depth=10)
    a.ink(rect(28, 50, w - 28, h - 28), FINE * 1.3, closed=True, color=shade(STONE, 0.45), alpha=0.8)
    seat = rect(96, 120, w - 96, h - 70)
    a.shape(rect(76, 90, w - 76, h - 56), wood, corner=12, depth=8)
    cushion(a, *seat[0], *seat[2], color=shade(RED, 0.08))
    crest = chaikin([(64, 112), (64, 64), (110, 50), (w / 2 - 26, 40), (w / 2, 14), (w / 2 + 26, 40), (w - 110, 50), (w - 64, 64), (w - 64, 112)], True, 2)
    arms = [rect(56, 100, 98, h - 62), rect(w - 98, 100, w - 56, h - 62)]
    raised_shadow(a, seat, [crest] + arms)
    for arm in arms:
        a.shape(arm, tint(wood, 0.1), corner=16, depth=8, light_k=0.45)
    for x in (77, w - 77):
        a.shape(ellipse(x, h - 70, 17, 17, 28), gold, outline=DETAIL * 1.3, depth=4, light_k=0.6, mottle=0)

    def carving(art, path):
        art.ink(chaikin([(84, 100), (84, 72), (120, 62), (w / 2 - 22, 54), (w / 2, 34), (w / 2 + 22, 54), (w - 120, 62), (w - 84, 72), (w - 84, 100)], False, 2), DETAIL, color=gold, alpha=0.95)

    a.shape(crest, tint(wood, 0.16), corner=0, depth=10, light_k=0.5, detail=carving)
    a.shape(ellipse(w / 2, 34, 13, 13, 24), rgb("#7aa6c9"), outline=DETAIL, depth=3, light_k=0.7, mottle=0)
    for x in (64, w - 64):
        a.shape(ellipse(x, 70, 16, 16, 28), gold, outline=DETAIL * 1.3, depth=4, light_k=0.6, mottle=0)
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
    """A bear pelt laid flat (after a real one). The head is part of the same
    pelt: snout, skull and ear bumps are all in one outline with the body;
    muzzle and features are painted on it. Leather trim around the fur."""
    import skia

    w, h = 460, 540
    a = Art(w, h, seed)
    cx = w / 2
    fur = rgb("#7a573c")
    leather = rgb("#c7a77c")
    half = [
        (cx - 6, 22), (cx - 16, 28), (cx - 21, 44), (cx - 26, 58),  # snout
        (cx - 38, 62), (cx - 46, 54), (cx - 54, 58), (cx - 54, 70), (cx - 48, 80),  # skull and ear
        (cx - 50, 96), (cx - 62, 110), (cx - 84, 116),  # cheek and neck into the shoulder
        (cx - 130, 102), (cx - 178, 86), (cx - 208, 84),  # front leg, top edge
        (cx - 222, 98), (cx - 216, 122), (cx - 196, 134),  # paw
        (cx - 150, 140), (cx - 118, 160),  # front leg, under side
        (cx - 116, 210), (cx - 124, 270), (cx - 118, 330),  # body side
        (cx - 136, 384), (cx - 176, 440), (cx - 206, 476),  # hind leg
        (cx - 200, 500), (cx - 170, 506), (cx - 132, 496),  # paw
        (cx - 92, 470), (cx - 52, 470), (cx - 18, 486),  # rump to tail
    ]
    tail = [(cx - 8, 500), (cx, 506), (cx + 8, 500)]
    outline = half + tail + [(2 * cx - x, y) for x, y in reversed(half)]
    trim = chaikin(outline, True, 2)
    a.shape(trim, leather, depth=6, shade_k=0.3, light_k=0.2, ao=0.0, mottle=0.04)
    inner = [(cx + (x - cx) * 0.94, 280 + (y - 280) * 0.95) for x, y in trim]

    def fur_and_face(art, path):
        glow = skia.Path()
        glow.addCircle(cx - 20, 230, 150)
        art.fill_path(glow, tint(fur, 0.25), 0.5, blur=60)
        for _ in range(520):
            x, y = art.rng.uniform(10, w - 10), art.rng.uniform(90, h - 30)
            if not path.contains(x, y):
                continue
            ang = math.atan2(18 + abs(x - cx) * 0.25, (x - cx) * 0.9 + 0.001)
            ln = art.rng.uniform(8, 14)
            art.ink([(x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang))], FINE * art.rng.uniform(0.7, 1.0), color=shade(fur, art.rng.uniform(0.35, 0.6)), alpha=0.7, wob=0.2)
        # Muzzle: lighter fur blending in, the nose, eyes, inner ears.
        muzzle = skia.Path()
        muzzle.addOval(skia.Rect.MakeXYWH(cx - 20, 30, 40, 40))
        art.fill_path(muzzle, tint(fur, 0.35), 0.8, blur=8)
        nose = chaikin([(cx - 9, 34), (cx + 9, 34), (cx + 6, 44), (cx - 6, 44)], True, 2)
        art.shape(nose, rgb("#2a201c"), outline=FINE, corner=0, depth=1, shade_k=0, light_k=0.3, ao=0, mottle=0)
        art.ink([(cx, 44), (cx, 54)], FINE * 1.1, color=shade(fur, 0.6), alpha=0.8)
        for dx in (-18, 18):
            dot(art, cx + dx, 74, 3.4, rgb("#1f1814"))
            art.shape(ellipse(cx + dx * 2.6, 66, 6, 6, 16), shade(fur, 0.3), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        for _ in range(50):
            x, y = art.rng.uniform(cx - 50, cx + 50), art.rng.uniform(56, 110)
            if path.contains(x, y) and abs(x - cx) > 12:
                t = math.atan2(y - 40, x - cx)
                art.ink([(x, y), (x + 7 * math.cos(t), y + 7 * math.sin(t))], FINE * 0.8, color=shade(fur, 0.5), alpha=0.6, wob=0.1)

    a.shape(inner, fur, outline=DETAIL * 0.8, depth=14, shade_k=0.45, light_k=0.2, ao=0.35, detail=fur_and_face)
    for px, py, ang in ((cx - 206, 108, math.pi * 1.05), (cx + 206, 108, -math.pi * 0.05), (cx - 182, 494, math.pi * 0.62), (cx + 182, 494, math.pi * 0.38)):
        ux, uy = math.cos(ang), math.sin(ang)
        for k in (-1.5, -0.5, 0.5, 1.5):
            x0, y0 = px - uy * k * 9, py + ux * k * 9
            a.ink([(x0, y0), (x0 + 13 * ux, y0 + 13 * uy)], DETAIL * 1.2, color=rgb("#efe6d2"), taper=True)
            a.ink([(x0, y0), (x0 + 13 * ux, y0 + 13 * uy)], FINE * 0.8, color=INK, alpha=0.5, taper=True)
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
