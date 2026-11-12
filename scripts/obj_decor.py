"""Decoration, castle & nobility, and garden (batch 13). Top-down, same pen
style (red = colorable)."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, cushion, dot, scallop, soft_shadow
from obj_craft import handle
from obj_furniture import furniture_top, raised_shadow, upholstered
from obj_magic import GOLD, candle, glow
from obj_nature import GREEN, GREEN_D, GREEN_L, blades, leaf
from obj_pots import flower_heads, pot
from objects import FOLIAGE, FOLIAGE_INK, canopy
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

CREAM = rgb("#e6d29f")
LINEN = rgb("#ece4d3")
GLASS = rgb("#bcd6dc")
WATER = rgb("#6aa0b6")
O = DETAIL * 2.0
V = 0.08


def fringe(a, x0, x1, y, dy, color, step=12):
    x = x0
    while x <= x1:
        a.ink([(x, y), (x + a.rng.uniform(-2, 2), y + dy)], FINE * 1.2, color=color)
        x += step


# -- rugs (red = colorable) ------------------------------------------------------------------------


def rug_rect(seed, w, h, motif="diamond", fringed=True, main=RED, trim=CREAM):
    a = Art(w, h, seed)
    if fringed:
        fringe(a, 26, w - 26, 20, -16, shade(trim, 0.3))
        fringe(a, 26, w - 26, h - 20, 16, shade(trim, 0.3))

    def pattern(art, p):
        art.ink(rect(38, 38, w - 38, h - 38), DETAIL, closed=True, color=trim, wob=0.3)
        art.ink(rect(52, 52, w - 52, h - 52), FINE * 1.3, closed=True, color=trim, wob=0.3)
        cx, cy = w / 2, h / 2
        if motif == "diamond":
            for r, c in ((min(w, h) * 0.32, trim), (min(w, h) * 0.2, shade(main, 0.25)), (min(w, h) * 0.08, trim)):
                art.shape([(cx, cy - r * 1.3), (cx + r, cy), (cx, cy + r * 1.3), (cx - r, cy)], c, outline=DETAIL, corner=2, depth=2, mottle=0, shade_k=0.15, light_k=0)
        elif motif == "medallion":
            for r, c in ((min(w, h) * 0.3, trim), (min(w, h) * 0.22, shade(main, 0.2)), (min(w, h) * 0.1, trim)):
                art.shape(scallop(cx, cy, r, art.rng, 10, 0.12), c, outline=DETAIL, corner=0, depth=2, mottle=0, shade_k=0.15, light_k=0)
        elif motif == "stripes":
            for k in range(1, 6):
                y = 52 + k * (h - 104) / 6
                art.shape(rect(52, y - 8, w - 52, y + 8), trim if k % 2 else shade(main, 0.25), outline=FINE * 1.2, corner=1, depth=1, mottle=0, shade_k=0, light_k=0)
        elif motif == "checks":
            n = 6
            cw, ch = (w - 104) / n, (h - 104) / n
            for i in range(n):
                for j in range(n):
                    if (i + j) % 2 == 0:
                        art.shape(rect(52 + i * cw + 3, 52 + j * ch + 3, 52 + (i + 1) * cw - 3, 52 + (j + 1) * ch - 3), trim, outline=FINE, corner=2, depth=1, mottle=0, shade_k=0, light_k=0)
        for x, y in ((70, 70), (w - 70, 70), (70, h - 70), (w - 70, h - 70)):
            art.shape([(x, y - 12), (x + 12, y), (x, y + 12), (x - 12, y)], trim, outline=FINE * 1.2, corner=1, depth=1, mottle=0, shade_k=0, light_k=0)

    a.shape(rect(20, 20, w - 20, h - 20), main, corner=4, depth=8, detail=pattern, shade_k=0.3, light_k=0.15)
    return a.image()


def rug_oval(seed, w=520, h=340, main=RED, trim=CREAM):
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2

    def pattern(art, p):
        for f, c in ((0.86, trim), (0.78, main), (0.5, trim), (0.42, shade(main, 0.2)), (0.16, trim)):
            art.shape(ellipse(cx, cy, (w / 2 - 20) * f, (h / 2 - 20) * f, 80), c, outline=DETAIL, depth=2, mottle=0.02, shade_k=0.1, light_k=0)

    a.shape(ellipse(cx, cy, w / 2 - 14, h / 2 - 14, 96), main, depth=8, detail=pattern, shade_k=0.3, light_k=0.15)
    return a.image()


def braided_rug(seed=1201):
    w, h = 460, 320
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2
    cols = [RED, CREAM, shade(RED, 0.25), rgb("#8a7a5a")]
    a.shape(ellipse(cx, cy, w / 2 - 12, h / 2 - 12, 96), RED, depth=8, shade_k=0.3, light_k=0.1)
    for k in range(9):
        f = 1 - k / 9
        a.ink(ellipse(cx, cy, (w / 2 - 22) * f, (h / 2 - 22) * f, 96), 14, closed=True, color=cols[k % 4], wob=0.3)
        a.ink(ellipse(cx, cy, (w / 2 - 22) * f + 7, (h / 2 - 22) * f + 7, 96), FINE, closed=True, color=shade(cols[k % 4], 0.45), alpha=0.6, wob=0.3)
    a.ink(ellipse(cx, cy, w / 2 - 12, h / 2 - 12, 96), OUTLINE, closed=True, wob=0.4)
    return a.image()


def fur_rug(seed=1202, fur=rgb("#d8cbb0")):
    w, h = 380, 300
    a = Art(w, h, seed)
    pts = blob(w / 2, h / 2, 170, a.rng, 16, 0.08, ry=124)

    def hair(art, p):
        for _ in range(360):
            x, y = art.rng.uniform(10, w - 10), art.rng.uniform(10, h - 10)
            if p.contains(x, y):
                t = math.atan2(y - h / 2, x - w / 2) + art.rng.uniform(-0.4, 0.4)
                art.ink([(x, y), (x + 9 * math.cos(t), y + 9 * math.sin(t))], FINE, color=shade(fur, art.rng.uniform(0.2, 0.4)), alpha=0.6, wob=0.1)

    a.shape(spiky_edge(pts, a.rng), fur, corner=0, depth=10, light_k=0.3, detail=hair)
    return a.image()


def spiky_edge(pts, rng, amp=7):
    from pen import normals, resample

    p = resample(pts + pts[:1], False, 6)[:-1]
    cx = sum(q[0] for q in p) / len(p)
    cy = sum(q[1] for q in p) / len(p)
    ns = normals(p, True)
    out = []
    for i, ((x, y), (nx, ny)) in enumerate(zip(p, ns)):
        if (x - cx) * nx + (y - cy) * ny < 0:
            nx, ny = -nx, -ny
        d = amp * rng.uniform(0.3, 1.0) if i % 2 == 0 else -amp * 0.2
        out.append((x + nx * d, y + ny * d))
    return out


def round_rug(seed, main=RED, trim=CREAM, s=420):
    a = Art(s, s, seed)
    m = s / 2

    def pattern(art, p):
        for f, c in ((0.88, trim), (0.8, main), (0.48, trim), (0.4, shade(main, 0.2)), (0.14, trim)):
            art.shape(ellipse(m, m, (m - 16) * f, (m - 16) * f, 96), c, outline=DETAIL, depth=2, mottle=0.02, shade_k=0.1, light_k=0)
        for i in range(8):
            t = 2 * math.pi * i / 8
            x, y = m + (m - 16) * 0.64 * math.cos(t), m + (m - 16) * 0.64 * math.sin(t)
            art.shape(ellipse(x, y, 12, 12, 20), trim, outline=FINE * 1.2, depth=1, mottle=0, shade_k=0, light_k=0)

    a.shape(ellipse(m, m, m - 14, m - 14, 120), main, depth=8, detail=pattern, shade_k=0.3, light_k=0.15)
    return a.image()


# -- soft things -------------------------------------------------------------------------------------


def floor_cushion(seed=1211, color=RED, s=170):
    a = Art(s, s, seed)
    cushion(a, 20, 20, s - 20, s - 20, color)
    for x, y in ((24, 24), (s - 24, 24), (24, s - 24), (s - 24, s - 24)):
        a.shape(scallop(x, y, 8, a.rng, 5, 0.3), rgb("#e2c068"), outline=FINE * 1.1, depth=1, mottle=0)
    return a.image()


def pillow_pile(seed=1212):
    s = 300
    a = Art(s, s, seed)
    spots = [(90, 110, 0.2), (190, 100, -0.3), (140, 190, 0.1), (220, 200, 0.5), (90, 210, -0.4)]
    cols = [RED, rgb("#e2c068"), shade(RED, 0.2), CREAM, tint(RED, 0.15)]
    for (x, y, t), c in zip(spots, cols):
        pts = [(x + dx * math.cos(t) - dy * math.sin(t), y + dx * math.sin(t) + dy * math.cos(t)) for dx, dy in ((-56, -42), (56, -42), (56, 42), (-56, 42))]
        soft_shadow(a, pts, dx=5, dy=6)
        a.shape(chaikin(pts, True, 3), c, outline=DETAIL * 1.3, corner=0, depth=6, light_k=0.4)
    return a.image()


def curtain(seed=1213, color=RED):
    """Curtains drawn at a window, from above: the wall edge with the window
    gap, the gathered fabric bunched at both sides (wavy folds)."""
    w, h = 420, 90
    a = Art(w, h, seed)
    a.shape(rect(4, 6, w - 4, 30), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    a.shape(rect(130, 6, w - 130, 30), GLASS, outline=DETAIL, corner=2, depth=2, light_k=0.5, mottle=0)
    a.ink([(10, 38), (w - 10, 38)], DETAIL * 1.4, color=BRASS)
    for x0, x1 in ((14, 150), (w - 150, w - 14)):
        pts = []
        n = 14
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            pts.append((x, 40 + (14 if i % 2 else 0) + 20))
        body = [(x0, 34)] + pts + [(x1, 34)]
        a.shape(body, color, outline=DETAIL * 1.4, corner=4, depth=6, light_k=0.3, detail=lambda art, p, x0=x0, x1=x1: [art.ink([(x0 + (x1 - x0) * i / 14, 38), (x0 + (x1 - x0) * i / 14, 66)], FINE * 1.1, color=shade(color, 0.45), alpha=0.8) for i in range(1, 14, 2)])
    return a.image()


def wall_hanging(seed=1214, color=RED):
    """A tapestry on a wall, from above: its rod along the wall edge and the
    cloth hanging down (a narrow band with its pattern barely showing)."""
    w, h = 400, 70
    a = Art(w, h, seed)
    a.shape(rect(4, 6, w - 4, 26), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    a.shape(rect(30, 26, w - 30, 50), color, outline=DETAIL * 1.3, corner=2, depth=4, light_k=0.2, detail=lambda art, p: [art.ink([(x, 30), (x + 8, 46)], FINE, color=tint(color, 0.4)) for x in range(44, w - 40, 22)])
    handle(a, 20, 28, w - 20, 28, 9, WOOD_DARK)
    for x in (20, w - 20):
        a.shape(ellipse(x, 28, 8, 8, 16), BRASS, outline=DETAIL, depth=1, mottle=0)
    return a.image()


# -- objects & curios ---------------------------------------------------------------------------------


def potted_palm(seed=1221):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    pot(a, m, m, 52)
    for i in range(8):
        t = 2 * math.pi * i / 8 + a.rng.uniform(-0.2, 0.2)
        L = a.rng.uniform(100, 130)
        spine = [(m + L * k / 12 * math.cos(t + 0.2 * (k / 12) ** 2), m + L * k / 12 * math.sin(t + 0.2 * (k / 12) ** 2)) for k in range(13)]
        for k in range(3, 12):
            x, y = spine[k]
            for side in (-1, 1):
                ang = t + side * 0.9
                leaf(a, x + math.cos(ang) * 10, y + math.sin(ang) * 10, 24 * math.sin(math.pi * k / 13) + 8, vary(a.rng, GREEN, 0.05), ang=ang, vein=False, outline=FINE)
        a.ink(spine, DETAIL * 0.8, color=GREEN_D)
    return a.image()


def flower_arrangement(seed=1222, petal=rgb("#e88aa8"), vase_col=rgb("#e6dcc4")):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    pot(a, m, m, 38, vase_col, inside=rgb("#2a221e"), rim=0.4)
    for _ in range(5):
        t = a.rng.uniform(0, 6.28)
        leaf(a, m + 46 * math.cos(t), m + 46 * math.sin(t), 30, vary(a.rng, GREEN, 0.05), ang=t)
    flower_heads(a, m, m, 72, 9, petal, rgb("#f6d24a"))
    return a.image()


def standing_mirror(seed=1223):
    """A standing mirror from above: its frame's top edge (a narrow band) and
    the stand's feet; the glass catches a glint along it."""
    w, h = 220, 120
    a = Art(w, h, seed)
    for x in (40, w - 40):
        a.shape(rect(x - 10, 20, x + 10, h - 20), WOOD_DARK, outline=O, corner=4, depth=3, var=V)
    a.shape(rect(20, h / 2 - 14, w - 20, h / 2 + 14), GOLD, outline=O, corner=10, depth=4, light_k=0.5, var=V)
    a.shape(rect(30, h / 2 - 5, w - 30, h / 2 + 5), GLASS, outline=FINE * 1.3, corner=4, depth=1, light_k=0.6, mottle=0)
    return a.image()


def easel(seed=1224):
    w, h = 260, 220
    a = Art(w, h, seed)
    for x0, y0, x1, y1 in ((40, 30, 70, h - 20), (w - 40, 30, w - 70, h - 20), (w / 2, 40, w / 2, 10)):
        handle(a, x0, y0, x1, y1, 10, WOOD)
    # The canvas leaning on it: its top edge, and the picture tilted toward us.
    canvas = [(40, 60), (w - 40, 60), (w - 50, 170), (50, 170)]
    a.shape(canvas, rgb("#f1ead8"), outline=O, corner=3, depth=4, var=V, detail=lambda art, p: [art.shape(blob(x, y, r, art.rng, 8, 0.25), c, outline=0, smooth=True, depth=1, shade_k=0, light_k=0, ao=0, mottle=0) for x, y, r, c in ((100, 110, 30, rgb("#86b04f")), (160, 100, 24, rgb("#7aa6c9")), (130, 140, 20, rgb("#e6b84a")))])
    a.ink(canvas, DETAIL * 2.4, closed=True, color=WOOD_DARK)
    a.shape(rect(30, 170, w - 30, 186), WOOD_DARK, outline=O, corner=4, depth=3, var=V)
    return a.image()


def wall_shelf(seed=1225):
    w, h = 400, 90
    a = Art(w, h, seed)
    a.shape(rect(4, 4, w - 4, 24), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    board(a, 14, 20, w - 14, 74, WOOD, n=1, corner=4)
    pot(a, 60, 48, 18, rgb("#4f74a8"), inside=rgb("#2a221e"), rim=0.4)
    for k, c in enumerate((rgb("#8a3f37"), rgb("#3c5a78"), rgb("#55743f"))):
        a.shape(rect(110 + k * 22, 28, 128 + k * 22, 70), c, outline=DETAIL, corner=2, depth=2, mottle=0)
    candle(a, 230, 48, 10)
    a.shape(ellipse(290, 48, 18, 18, 24), rgb("#e6dcc4"), outline=DETAIL * 1.2, depth=3)
    pot(a, 350, 48, 18, rgb("#c06a45"))
    return a.image()


def coat_rack(seed=1226):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    for t in (0.3, 2.4, 4.5):
        handle(a, m, m, m + 70 * math.cos(t), m + 70 * math.sin(t), 10, WOOD_DARK)
    # A cloak and a hat hanging from its hooks.
    a.shape(chaikin([(m - 30, m - 10), (m + 20, m - 40), (m + 60, m - 10), (m + 40, m + 50), (m - 10, m + 60)], True, 2), rgb("#4a5a3a"), outline=O, corner=0, depth=6, light_k=0.3, var=V)
    a.shape(ellipse(m - 30, m + 30, 30, 30, 36), rgb("#5a3a2a"), outline=O, depth=4, light_k=0.4, var=V)
    a.shape(ellipse(m - 30, m + 30, 16, 16, 24), shade(rgb("#5a3a2a"), 0.2), outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(m, m, 12, 12, 20), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def umbrella_stand(seed=1227):
    s = 140
    a = Art(s, s, seed)
    m = s / 2
    pot(a, m, m, 48, rgb("#7a8088"), inside=rgb("#2a2a2e"), rim=0.82)
    for x, y, c in ((m - 12, m - 8, RED), (m + 12, m + 6, rgb("#3c5a78")), (m + 2, m - 18, WOOD_DARK)):
        a.shape(ellipse(x, y, 9, 9, 16), c, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def grandfather_clock(seed=1228):
    """A grandfather clock from above: only its top (a carved hood)."""
    w, h = 170, 120
    a = Art(w, h, seed)
    furniture_top(a, 10, 10, w - 10, h - 10, WOOD_DARK, n=1)
    a.ink(chaikin([(30, h - 30), (w / 2, 26), (w - 30, h - 30)], False, 2), DETAIL * 1.4, color=GOLD)
    a.shape(ellipse(w / 2, 32, 9, 9, 16), GOLD, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def table_clock(seed=1229):
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 44, 44, 48), BRASS, outline=O, depth=5, light_k=0.5, var=V)
    a.shape(ellipse(m, m, 34, 34, 48), rgb("#f2ece0"), outline=DETAIL, depth=2, mottle=0, shade_k=0.1, light_k=0)
    for k in range(12):
        t = 2 * math.pi * k / 12
        a.ink([(m + 28 * math.cos(t), m + 28 * math.sin(t)), (m + 32 * math.cos(t), m + 32 * math.sin(t))], FINE, alpha=0.8)
    a.ink([(m, m), (m, m - 22)], DETAIL, taper=False)
    a.ink([(m, m), (m + 16, m + 6)], DETAIL, taper=False)
    return a.image()


def large_hourglass(seed=1230):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 70, 70, 64), WOOD_DARK, depth=8)
    for k in range(4):
        t = 2 * math.pi * k / 4 + 0.78
        a.shape(ellipse(m + 58 * math.cos(t), m + 58 * math.sin(t), 11, 11, 20), WOOD, outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(m, m, 44, 44, 48), GLASS, outline=DETAIL * 1.3, depth=3, light_k=0.6, mottle=0)
    a.shape(ellipse(m, m, 26, 26, 36), rgb("#e0c07a"), outline=FINE, depth=2, mottle=0)
    return a.image()


def bird_cage(seed=1231):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 70, 70, 64), rgb("#e8dfc8"), outline=0, depth=2, shade_k=0, light_k=0, ao=0.2, mottle=0)
    bird = rgb("#e6c03a")
    a.shape(ellipse(m + 10, m + 14, 16, 11, 24, rot=0.5), bird, outline=DETAIL, depth=2, light_k=0.4, mottle=0)
    a.shape(ellipse(m + 22, m + 4, 8, 8, 16), bird, outline=FINE * 1.3, depth=1, mottle=0)
    for k in range(12):
        t = 2 * math.pi * k / 12
        a.ink([(m + 10 * math.cos(t), m + 10 * math.sin(t)), (m + 70 * math.cos(t), m + 70 * math.sin(t))], FINE * 1.4, color=BRASS)
    a.ink(ellipse(m, m, 70, 70, 64), DETAIL * 2, closed=True, color=BRASS)
    a.ink(ellipse(m, m, 72, 72, 64), FINE * 1.2, closed=True)
    a.shape(ellipse(m, m, 12, 12, 20), BRASS, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def fish_bowl(seed=1232):
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 56, 56, 56), GLASS, outline=O, depth=3, light_k=0.6, mottle=0, var=V)
    a.shape(ellipse(m, m, 46, 46, 56), WATER, outline=0, depth=2, shade_k=0, light_k=0.3, ao=0.3, mottle=0)
    for x, y, t in ((m - 10, m - 4, 0.3), (m + 14, m + 12, 2.8)):
        a.shape(ellipse(x, y, 11, 6, 20, rot=t), rgb("#f08a3a"), outline=FINE * 1.3, depth=1, mottle=0, light_k=0.4)
        a.shape([(x - 12 * math.cos(t), y - 12 * math.sin(t)), (x - 20 * math.cos(t - 0.4), y - 20 * math.sin(t - 0.4)), (x - 20 * math.cos(t + 0.4), y - 20 * math.sin(t + 0.4))], rgb("#f08a3a"), outline=FINE, corner=1, depth=1, mottle=0)
    a.ink([(m - 30, m - 26), (m - 16, m - 38)], FINE * 2, color=(250, 250, 255), alpha=0.85)
    return a.image()


def music_box(seed=1233):
    w, h = 160, 120
    a = Art(w, h, seed)
    a.shape(rect(12, 12, w - 12, h - 12), rgb("#6a3a2e"), outline=O, corner=8, depth=6, light_k=0.4, var=V)
    a.shape(rect(26, 26, w - 26, h - 26), rgb("#8a4a3a"), outline=DETAIL, corner=4, depth=3, light_k=0.3)
    a.shape(ellipse(w / 2, h / 2, 14, 14, 24), GOLD, outline=DETAIL, depth=2, mottle=0)
    a.shape(rect(w - 14, h / 2 - 6, w - 2, h / 2 + 6), BRASS, outline=FINE * 1.2, corner=2, depth=1, mottle=0)
    return a.image()


# -- castle & nobility --------------------------------------------------------------------------------


def banquet_table(seed=1241, w=640):
    h = 260
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD_DARK, n=2, corner=8)
    a.shape(rect(30, h / 2 - 34, w - 30, h / 2 + 34), RED, outline=DETAIL * 1.3, corner=3, depth=4, mottle=0.03)
    for y in (h / 2 - 24, h / 2 + 24):
        a.ink([(40, y), (w - 40, y)], FINE * 1.3, color=rgb("#e2c068"), taper=False)
    for k in range(int((w - 80) / 120)):
        x = 90 + k * 120
        for y in (44, h - 44):
            a.shape(ellipse(x, y, 26, 26, 32), rgb("#e4dccb"), outline=DETAIL * 1.2, depth=3)
            a.shape(ellipse(x, y, 16, 16, 24), rgb("#b5643a"), outline=FINE, depth=1, mottle=0, light_k=0.3)
            a.shape(ellipse(x + 40, y, 9, 9, 16), GOLD, outline=DETAIL, depth=2, mottle=0)
        candle(a, x + 60, h / 2, 10)
    return a.image()


def high_back_chair(seed=1242, color=RED):
    w, h = 190, 200
    a = Art(w, h, seed)
    seat = rect(36, 70, w - 36, h - 24)
    a.shape(rect(26, 60, w - 26, h - 14), WOOD_DARK, outline=OUTLINE, corner=10, depth=6)
    cushion(a, 36, 70, w - 36, h - 24, shade(color, 0.06))
    back = rect(18, 14, w - 18, 66)
    raised_shadow(a, seat, [back])
    a.shape(back, tint(WOOD_DARK, 0.12), outline=OUTLINE, corner=12, depth=6, light_k=0.45, detail=lambda art, p: art.ink(chaikin([(40, 54), (w / 2, 24), (w - 40, 54)], False, 2), DETAIL, color=GOLD))
    for x in (26, w - 26):
        a.shape(ellipse(x, 40, 12, 12, 20), GOLD, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def canopy_bed(seed=1243, color=RED):
    """A four-poster bed from above: the canopy's fabric roof hides the bed,
    its valance hangs at the edges, the four posts' tops at the corners."""
    w, h = 470, 560
    a = Art(w, h, seed)
    a.shape(rect(16, 16, w - 16, h - 16), WOOD_DARK, corner=10, depth=10)

    def drape(art, p):
        for x in range(60, w - 40, 50):
            art.ink([(x, 40), (x + 4, h - 40)], FINE * 1.3, color=shade(color, 0.4), alpha=0.7)
        art.ink(rect(40, 40, w - 40, h - 40), DETAIL, closed=True, color=rgb("#e2c068"))

    a.shape(rect(26, 26, w - 26, h - 26), color, outline=DETAIL * 1.4, corner=8, depth=10, light_k=0.35, detail=drape)
    for k in range(10):  # valance scallops along the foot
        x = 30 + k * (w - 60) / 10
        a.shape(chaikin([(x, h - 30), (x + (w - 60) / 10, h - 30), (x + (w - 60) / 20, h - 14)], True, 2), shade(color, 0.12), outline=DETAIL, corner=0, depth=2, mottle=0)
    for x, y in ((24, 24), (w - 24, 24), (24, h - 24), (w - 24, h - 24)):
        a.shape(ellipse(x, y, 20, 20, 24), WOOD, outline=O, depth=4, light_k=0.5, var=V)
        a.shape(ellipse(x, y, 8, 8, 16), GOLD, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def heraldic_banner(seed=1244, color=RED, charge="lion"):
    w, h = 220, 440
    a = Art(w, h, seed)
    cloth = chaikin([(20, 30), (w - 20, 30), (w - 20, h - 70), (w - 60, h - 20), (w / 2, h - 60), (60, h - 20), (20, h - 70)], True, 1)

    def deco(art, p):
        art.ink(rect(34, 44, w - 34, h - 100), FINE * 1.4, closed=True, color=rgb("#e2c068"))
        cx, cy = w / 2, 180
        if charge == "cross":
            art.shape(rect(cx - 14, cy - 70, cx + 14, cy + 70), rgb("#e2c068"), outline=DETAIL, corner=2, depth=2, mottle=0)
            art.shape(rect(cx - 56, cy - 14, cx + 56, cy + 14), rgb("#e2c068"), outline=DETAIL, corner=2, depth=2, mottle=0)
        elif charge == "star":
            pts = [(cx + (56 if k % 2 == 0 else 24) * math.cos(-math.pi / 2 + k * math.pi / 5), cy + (56 if k % 2 == 0 else 24) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)]
            art.shape(pts, rgb("#e2c068"), outline=DETAIL, corner=1, depth=2, mottle=0)
        else:
            art.shape(scallop(cx, cy, 56, art.rng, 10, 0.12), rgb("#e2c068"), outline=DETAIL, corner=0, depth=2, mottle=0)
            art.shape(ellipse(cx, cy, 26, 26, 32), shade(color, 0.2), outline=DETAIL, depth=1, mottle=0)

    a.shape(cloth, color, corner=0, depth=8, light_k=0.25, detail=deco)
    handle(a, 8, 24, w - 8, 24, 12, WOOD_DARK)
    return a.image()


def armor_display(seed=1245):
    from obj_war import armor_stand

    return armor_stand(seed)


def weapon_display(seed=1246):
    """Crossed swords over a shield on a wall, from above (along the wall)."""
    from obj_war import sword_at

    w, h = 360, 120
    a = Art(w, h, seed)
    a.shape(rect(4, 4, w - 4, 26), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    sword_at(a, 40, 70, -0.1, 200)
    sword_at(a, w - 40, 70, math.pi + 0.1, 200)
    a.shape(ellipse(w / 2, 50, 54, 24, 48), RED, outline=OUTLINE, depth=6, light_k=0.4)
    a.ink(ellipse(w / 2, 50, 46, 18, 48), DETAIL * 1.6, closed=True, color=IRON)
    return a.image()


def great_fireplace(seed=1247):
    from obj_stone import GREY, stone_block

    w, h = 560, 260
    a = Art(w, h, seed)
    x = 10
    while x < w - 10:
        bw = min(a.rng.uniform(56, 84), w - 10 - x)
        stone_block(a, rect(x + 2, 8, x + bw - 2, 80), vary(a.rng, GREY, 0.06), outline=DETAIL * 1.3, corner=8, cracks=0)
        x += bw
    stone_block(a, rect(10, 76, 90, h - 10), GREY, corner=8, cracks=1)
    stone_block(a, rect(w - 90, 76, w - 10, h - 10), GREY, corner=8, cracks=1)
    glow(a, w / 2, 170, 120, rgb("#ff9a3c"), 0.35)
    a.shape(rect(90, 80, w - 90, h - 14), rgb("#3c322d"), outline=DETAIL * 1.3, corner=6, depth=10, shade_k=0, light_k=0, ao=0.6)
    for x0, x1 in ((170, 360), (230, 400)):
        a.shape(rect(x0, 150, x1, 176), WOOD_DARK, outline=DETAIL, corner=12, depth=4)
    for r, col in ((54, rgb("#e9773a")), (34, rgb("#f4b544")), (16, rgb("#fde8a6"))):
        a.shape(scallop(w / 2, 162, r, a.rng, 7, 0.22), col, outline=DETAIL if r > 20 else 0, depth=3, shade_k=0.2, light_k=0, ao=0, mottle=0)
    for x in (110, w - 110):
        a.shape(ellipse(x, h - 40, 14, 14, 24), IRON, outline=DETAIL, depth=2, mottle=0)  # andirons
    return a.image()


def chandelier(seed=1248):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 130, rgb("#ffd27a"), 0.3)
    a.ink(ellipse(m, m, 104, 104, 80), DETAIL * 3, closed=True, color=INK)
    a.ink(ellipse(m, m, 104, 104, 80), DETAIL * 1.8, closed=True, color=IRON)
    for k in range(4):
        t = math.pi / 4 + k * math.pi / 2
        a.ink([(m, m), (m + 104 * math.cos(t), m + 104 * math.sin(t))], DETAIL * 1.6, color=IRON)
    a.shape(ellipse(m, m, 18, 18, 24), IRON, outline=DETAIL * 1.3, depth=3, mottle=0)
    for k in range(10):
        t = 2 * math.pi * k / 10
        x, y = m + 104 * math.cos(t), m + 104 * math.sin(t)
        candle(a, x, y, 10)
    return a.image()


def vanity_table(seed=1249):
    w, h = 320, 200
    a = Art(w, h, seed)
    furniture_top(a, 8, 10, w - 8, h - 10, WOOD_LIGHT, n=2)
    a.shape(rect(80, 12, w - 80, 34), GOLD, outline=O, corner=8, depth=3, light_k=0.5, var=V)
    a.shape(rect(92, 18, w - 92, 28), GLASS, outline=FINE * 1.2, corner=3, depth=1, light_k=0.6, mottle=0)
    for x, y, c in ((70, 110, rgb("#c890b0")), (110, 130, rgb("#9fc0d0")), (230, 120, rgb("#e6b84a"))):
        a.shape(ellipse(x, y, 12, 12, 20), c, outline=DETAIL, depth=2, light_k=0.5, mottle=0)
    a.shape(ellipse(170, 130, 30, 22, 32), rgb("#f2ece0"), outline=DETAIL, depth=2, mottle=0)  # powder bowl
    return a.image()


def foot_chest(seed=1250):
    w, h = 320, 150
    a = Art(w, h, seed)
    a.shape(rect(10, 12, w - 10, h - 12), rgb("#6a3a2e"), corner=10, depth=10, light_k=0.35)
    for x in (50, w / 2, w - 50):
        a.shape(rect(x - 10, 12, x + 10, h - 12), GOLD, outline=DETAIL * 1.3, corner=3, depth=3, light_k=0.5)
    a.shape(rect(w / 2 - 18, h / 2 - 14, w / 2 + 18, h / 2 + 18), GOLD, outline=DETAIL * 1.3, corner=4, depth=3)
    return a.image()


def harp(seed=1251):
    """A floor harp from above: its soundbox (a long tapering board), the
    curved neck above it, strings between them."""
    w, h = 180, 300
    a = Art(w, h, seed)
    box = [(70, 40), (110, 40), (130, h - 30), (50, h - 30)]
    a.shape(box, WOOD, outline=O, corner=8, depth=5, light_k=0.4, var=V)
    neck = chaikin([(80, 30), (150, 70), (150, 200), (120, h - 40)], False, 2)
    for k in range(7):
        y = 70 + k * 26
        a.ink([(92 + k * 3, y), (148 - (k * 2), y)], FINE, color=rgb("#f2ece0"), alpha=0.95)
    a.ink(neck, 20, color=INK, taper=False)
    a.ink(neck, 13, color=GOLD, taper=False)
    return a.image()

def globe(seed=1252):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 82, 82, 64), WOOD_DARK, outline=O, depth=6, var=V)
    sea = rgb("#6f9fbf")

    def land(art, p):
        for _ in range(4):
            art.shape(blob(m + art.rng.uniform(-30, 30), m + art.rng.uniform(-30, 30), art.rng.uniform(14, 24), art.rng, 9, 0.35), rgb("#c9b07a"), outline=FINE * 1.1, smooth=True, depth=1, shade_k=0, light_k=0.2, ao=0, mottle=0)
        art.ink(ellipse(m, m, 62, 20, 48), FINE, closed=True, alpha=0.4)

    a.shape(ellipse(m, m, 62, 62, 64), sea, outline=DETAIL * 1.3, depth=6, light_k=0.5, detail=land)
    a.ink(ellipse(m, m, 70, 70, 64), DETAIL * 1.6, closed=True, color=BRASS)
    return a.image()


def royal_runner(seed=1253):
    return rug_rect(seed, 300, 760, "diamond", fringed=True, main=RED, trim=rgb("#e2c068"))


# -- garden ------------------------------------------------------------------------------------------


def hedge(seed=1261, w=512, h=140):
    a = Art(w, h, seed)
    # A clipped hedge: one long canopy, lit along the top edge.
    from objects import FOLIAGE, FOLIAGE_INK

    dark, mid, light = FOLIAGE
    pts = []
    for i in range(80):
        t = i / 79
        pts.append((20 + (w - 40) * t, 20 + 4 * math.sin(t * 17)))
    for i in range(80):
        t = 1 - i / 79
        pts.append((20 + (w - 40) * t, h - 20 + 4 * math.sin(t * 13)))

    def leaves(art, p):
        g = skia.Path()
        g.addRect(skia.Rect.MakeLTRB(0, 0, w, h * 0.45))
        art.fill_path(g, light, 0.45, blur=20)
        for _ in range(int(w / 9)):
            x, y = art.rng.uniform(30, w - 30), art.rng.uniform(30, h - 30)
            t = art.rng.uniform(0, math.pi)
            r = art.rng.uniform(8, 14)
            art.ink([(x + r * math.cos(t + k * 0.3), y + r * math.sin(t + k * 0.3)) for k in range(8)], DETAIL * 0.8, color=FOLIAGE_INK, alpha=0.7, wob=0.2)

    a.shape(pts, mid, outline=OUTLINE, corner=0, depth=14, shade_k=0.5, light_k=0.2, ao=0.35, detail=leaves)
    return a.image()


def hedge_corner(seed=1262):
    s_ = 320
    a = Art(s_, s_, seed)
    dark, mid, light = FOLIAGE
    pts = []
    W = 120
    outer = [(20, 20), (s_ - 20, 20), (s_ - 20, W), (W, W), (W, s_ - 20), (20, s_ - 20)]
    from pen import resample

    for x, y in resample(outer + outer[:1], False, 12)[:-1]:
        pts.append((x + a.rng.uniform(-3, 3), y + a.rng.uniform(-3, 3)))

    def leaves(art, p):
        g = skia.Path()
        g.addCircle(60, 60, 140)
        art.fill_path(g, light, 0.4, blur=30)
        for _ in range(60):
            x, y = art.rng.uniform(30, s_ - 30), art.rng.uniform(30, s_ - 30)
            if not p.contains(x, y):
                continue
            t = art.rng.uniform(0, math.pi)
            r = art.rng.uniform(8, 14)
            art.ink([(x + r * math.cos(t + k * 0.3), y + r * math.sin(t + k * 0.3)) for k in range(8)], DETAIL * 0.8, color=FOLIAGE_INK, alpha=0.7, wob=0.2)

    a.shape(chaikin(pts, True, 1), mid, outline=OUTLINE, corner=0, depth=14, shade_k=0.5, light_k=0.2, ao=0.35, detail=leaves)
    return a.image()

def topiary_ball(seed=1263, s=200):
    a = Art(s, s, seed)
    canopy(a, s / 2, s / 2, s * 0.4, bumps=14, clusters=(0.7, 0.4))
    return a.image()


def topiary_spiral(seed=1264):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    dark, mid, light = FOLIAGE
    for k, r in enumerate((86, 64, 42, 22)):
        col = mix(dark, light, k / 3)
        pts = scallop(m - k * 3, m - k * 3, r, a.rng, 12 - k * 2, 0.08)
        soft_shadow(a, pts, dx=5, dy=6)
        a.shape(pts, col, outline=DETAIL * 1.6 if k else OUTLINE, corner=0, depth=6, shade_k=0.4, light_k=0.3, ao=0.2)
    return a.image()


def flower_bed(seed=1265, colors=None, w=400, h=220, round_=False):
    a = Art(w, h, seed)
    border = ellipse(w / 2, h / 2, w / 2 - 12, h / 2 - 12, 80) if round_ else rect(12, 12, w - 12, h - 12)
    from obj_stone import GREY, stone_block

    stone_block(a, border, GREY, corner=10, cracks=0)
    inner = ellipse(w / 2, h / 2, w / 2 - 30, h / 2 - 30, 80) if round_ else rect(30, 30, w - 30, h - 30)
    a.shape(inner, rgb("#5a4030"), outline=DETAIL * 1.2, corner=6, depth=6, shade_k=0, light_k=0, ao=0.5, mottle=0.08)
    colors = colors or [rgb("#e6b84a"), rgb("#c8443a"), rgb("#f3eee2"), rgb("#9a6ab8")]
    with a.clip(to_path(inner)):
        for _ in range(int(w * h / 3600)):
            x, y = a.rng.uniform(34, w - 34), a.rng.uniform(34, h - 34)
            blades(a, x, y, 6, 22, [GREEN, GREEN_D], width=6)
        for _ in range(int(w * h / 1400)):
            x, y = a.rng.uniform(34, w - 34), a.rng.uniform(34, h - 34)
            c = a.rng.choice(colors)
            for k in range(5):
                pa = 2 * math.pi * k / 5
                a.shape(ellipse(x + 6 * math.cos(pa), y + 6 * math.sin(pa), 6, 4, 12, rot=pa), c, outline=FINE, depth=1, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
            dot(a, x, y, 3, rgb("#9a5a2a"))
    return a.image()


def garden_bench(seed=1266):
    w, h = 400, 150
    a = Art(w, h, seed)
    a.shape(rect(20, 30, w - 20, h - 20), IRON, outline=O, corner=8, depth=4, var=V)
    board(a, 24, 50, w - 24, h - 26, WOOD_LIGHT, n=4, corner=4)
    back = rect(18, 16, w - 18, 50)
    raised_shadow(a, rect(24, 50, w - 24, h - 26), [back])
    a.shape(back, tint(WOOD_LIGHT, 0.08), outline=OUTLINE, corner=6, depth=4, light_k=0.4, detail=lambda art, p: boards(art, 18, 16, w - 18, 50, WOOD_LIGHT, 2))
    for x in (18, w - 18):
        a.shape(ellipse(x, 32, 14, 14, 20), IRON, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def path_tiles(seed=1267):
    from obj_stone import GREY, stone_block

    w, h = 200, 512
    a = Art(w, h, seed)
    y = 10
    while y < h - 60:
        th = a.rng.uniform(70, 100)
        stone_block(a, chaikin(rect(20 + a.rng.uniform(-6, 6), y, w - 20 + a.rng.uniform(-6, 6), y + th), True, 1), vary(a.rng, GREY, 0.06), corner=0, cracks=1)
        y += th + a.rng.uniform(14, 24)
    return a.image()


def stepping_stones(seed=1268):
    from obj_stone import GREY, stone_block

    w, h = 260, 512
    a = Art(w, h, seed)
    y = 50
    while y < h - 40:
        x = w / 2 + a.rng.uniform(-50, 50)
        stone_block(a, blob(x, y, a.rng.uniform(36, 46), a.rng, 9, 0.12), vary(a.rng, GREY, 0.07), smooth=True, cracks=0)
        y += a.rng.uniform(90, 110)
    return a.image()


def rose_arch(seed=1269):
    w, h = 300, 140
    a = Art(w, h, seed)
    # The arch's top from above: a band of trellis over the path, roses on it.
    for x in (24, w - 24):
        a.shape(rect(x - 14, 20, x + 14, h - 20), WOOD, outline=O, corner=4, depth=4, var=V)
    a.shape(rect(18, 40, w - 18, h - 40), WOOD_LIGHT, outline=O, corner=8, depth=6, light_k=0.4, var=V, detail=lambda art, p: [art.ink([(x, 42), (x + 20, h - 42)], FINE * 1.2, color=shade(WOOD_LIGHT, 0.45)) for x in range(30, w - 30, 26)])
    for _ in range(26):
        x, y = a.rng.uniform(30, w - 30), a.rng.uniform(34, h - 34)
        if a.rng.random() < 0.5:
            leaf(a, x, y, 22, vary(a.rng, GREEN, 0.05), vein=False, outline=FINE)
        else:
            a.shape(scallop(x, y, 9, a.rng, 6, 0.25), rgb("#c8443a"), outline=FINE * 1.3, depth=2, mottle=0, light_k=0.4)
            dot(a, x, y, 2.4, shade(rgb("#c8443a"), 0.4))
    return a.image()


def trellis(seed=1270):
    w, h = 400, 80
    a = Art(w, h, seed)
    a.shape(rect(10, h / 2 - 12, w - 10, h / 2 + 12), WOOD_LIGHT, outline=O, corner=4, depth=4, var=V, detail=lambda art, p: [art.ink([(x, h / 2 - 12), (x + 12, h / 2 + 12)], FINE * 1.2, color=shade(WOOD_LIGHT, 0.5)) for x in range(14, w - 14, 18)])
    for _ in range(18):
        x = a.rng.uniform(20, w - 20)
        leaf(a, x, h / 2 + a.rng.uniform(-16, 16), 22, vary(a.rng, GREEN, 0.06), vein=False, outline=FINE)
    return a.image()


def vegetable_bed(seed=1271):
    w, h = 420, 260
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), WOOD_DARK, corner=6, depth=8)
    a.shape(rect(26, 26, w - 26, h - 26), rgb("#5a4030"), outline=DETAIL * 1.2, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5, mottle=0.08)
    for row in range(3):
        y = 60 + row * 70
        for k in range(6):
            x = 60 + k * 60
            if row == 0:  # cabbages
                a.shape(scallop(x, y, 20, a.rng, 8, 0.15), rgb("#8fb86a"), outline=DETAIL, corner=0, depth=3, light_k=0.4, mottle=0)
                a.shape(scallop(x - 2, y - 2, 10, a.rng, 6, 0.15), tint(rgb("#8fb86a"), 0.2), outline=FINE, corner=0, depth=1, mottle=0)
            elif row == 1:  # carrot tops
                blades(a, x, y, 7, 22, [GREEN, GREEN_L], width=5)
                dot(a, x, y, 5, rgb("#e08a3a"))
            else:  # lettuce
                a.shape(scallop(x, y, 18, a.rng, 10, 0.2), rgb("#a8c86a"), outline=DETAIL, corner=0, depth=3, light_k=0.4, mottle=0)
    return a.image()


def sundial(seed=1272):
    from obj_stone import LIGHT_STONE, stone_block

    s = 200
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, ellipse(m, m, 80, 80, 64), LIGHT_STONE, cracks=1, light_k=0.4)
    a.shape(ellipse(m, m, 64, 64, 64), BRASS, outline=DETAIL * 1.3, depth=3, light_k=0.5)
    for k in range(12):
        t = 2 * math.pi * k / 12
        a.ink([(m + 50 * math.cos(t), m + 50 * math.sin(t)), (m + 60 * math.cos(t), m + 60 * math.sin(t))], FINE * 1.2, color=shade(BRASS, 0.5))
    a.shape([(m, m - 50), (m + 6, m + 10), (m - 6, m + 10)], shade(BRASS, 0.2), outline=DETAIL, corner=1, depth=2, mottle=0)
    a.fill_path(to_path([(m, m - 48), (m + 40, m + 20), (m + 6, m + 10)]), INK, 0.25, blur=3)
    return a.image()


def garden_lantern(seed=1273):
    from obj_stone import GREY, stone_block

    s = 180
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 70, rgb("#ffd27a"), 0.35)
    stone_block(a, [(m + 70 * math.cos(t), m + 70 * math.sin(t)) for t in [math.pi / 6 + k * math.pi / 3 for k in range(6)]], GREY, corner=6, cracks=0)
    stone_block(a, [(m + 40 * math.cos(t), m + 40 * math.sin(t)) for t in [math.pi / 6 + k * math.pi / 3 for k in range(6)]], tint(GREY, 0.12), outline=DETAIL * 1.3, corner=4, cracks=0, light_k=0.45)
    a.shape(ellipse(m, m, 12, 12, 20), tint(GREY, 0.2), outline=DETAIL, depth=2, mottle=0)
    return a.image()


def gazebo(seed=1274):
    s = 480
    a = Art(s, s, seed)
    m = s / 2
    n = 8
    pts = [(m + 220 * math.cos(t), m + 220 * math.sin(t)) for t in [math.pi / 8 + k * math.pi / 4 for k in range(n)]]
    roof = rgb("#7a4a3a")
    for k in range(n):
        face = [pts[k], pts[(k + 1) % n], (m, m)]
        t = math.pi / 8 + (k + 0.5) * math.pi / 4
        lit = math.cos(t + math.pi * 0.75)
        col = tint(roof, 0.2 * lit) if lit > 0 else shade(roof, -0.25 * lit)
        a.shape(face, col, outline=DETAIL * 1.2, corner=0, wob=0.2, depth=2, shade_k=0, light_k=0, ao=0, mottle=0.04, detail=lambda art, p, k=k: [art.ink([(pts[k][0] + (m - pts[k][0]) * f, pts[k][1] + (m - pts[k][1]) * f), (pts[(k + 1) % n][0] + (m - pts[(k + 1) % n][0]) * f, pts[(k + 1) % n][1] + (m - pts[(k + 1) % n][1]) * f)], FINE * 1.1, color=shade(roof, 0.5), alpha=0.7) for f in (0.2, 0.4, 0.6, 0.8)])
    a.ink(pts, OUTLINE, closed=True, wob=0.3)
    a.shape(ellipse(m, m, 18, 18, 24), GOLD, outline=DETAIL * 1.3, depth=3, light_k=0.5, mottle=0)
    return a.image()


def small_pond(seed=1275):
    from obj_stone import GREY, stone_block

    w, h = 360, 260
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2
    pond = blob(cx, cy, 130, a.rng, 11, 0.1, ry=90)

    def ripples(art, p):
        art.ink([(cx - 40, cy - 20), (cx - 10, cy - 26), (cx + 20, cy - 20)], FINE * 1.4, color=rgb("#e4f2f6"), alpha=0.85)
        for _ in range(3):
            x, y = cx + art.rng.uniform(-80, 80), cy + art.rng.uniform(-40, 40)
            t = art.rng.uniform(0, 6.28)
            art.shape([(x, y)] + [(x + 16 * math.cos(t + 0.35 + j * 0.2), y + 16 * math.sin(t + 0.35 + j * 0.2)) for j in range(29)], rgb("#6d9a48"), outline=DETAIL, corner=0, depth=2, light_k=0.4, mottle=0)

    a.shape(pond, WATER, outline=DETAIL * 1.2, smooth=True, depth=12, shade_k=0, light_k=0, ao=0.6, detail=ripples)
    from pen import resample

    for px, py in resample(chaikin(pond, True, 2), True, 32):
        dx, dy = px - cx, py - cy
        L = math.hypot(dx, dy) or 1
        stone_block(a, blob(px + dx / L * 10, py + dy / L * 10, a.rng.uniform(15, 20), a.rng, 8, 0.15), vary(a.rng, GREY, 0.07), outline=DETAIL * 1.3, smooth=True, cracks=0)
    return a.image()


# -- registry ---------------------------------------------------------------------------------------

BLUE = rgb("#3c5a8a")
GREENC = rgb("#4a7a4a")

DECOR = {
    # rugs
    "Diamond Rug": lambda: rug_rect(1301, 420, 600, "diamond"),
    "Medallion Rug": lambda: rug_rect(1302, 440, 620, "medallion"),
    "Striped Rug": lambda: rug_rect(1303, 400, 560, "stripes"),
    "Checkered Rug": lambda: rug_rect(1304, 420, 420, "checks"),
    "Square Rug": lambda: rug_rect(1305, 380, 380, "diamond", fringed=False),
    "Small Rug": lambda: rug_rect(1306, 260, 360, "diamond"),
    "Long Runner": lambda: rug_rect(1307, 240, 760, "stripes"),
    "Oval Rug": lambda: rug_oval(1308),
    "Small Oval Rug": lambda: rug_oval(1309, 360, 240),
    "Round Patterned Rug": lambda: round_rug(1310),
    "Small Round Rug": lambda: round_rug(1311, s=280),
    "Braided Rug": braided_rug,
    "Sheepskin Rug": fur_rug,
    "Dark Fur Rug": lambda: fur_rug(1203, rgb("#5a4636")),
    "Wolf Fur Rug": lambda: fur_rug(1204, rgb("#8e8a84")),
    "Blue Diamond Rug": lambda: rug_rect(1312, 420, 600, "diamond", main=BLUE, trim=CREAM),
    "Green Medallion Rug": lambda: rug_rect(1313, 440, 620, "medallion", main=GREENC, trim=CREAM),
    "Gold Round Rug": lambda: round_rug(1314, main=rgb("#b88a3a"), trim=rgb("#5a3a22")),
    # soft
    "Floor Cushion": floor_cushion,
    "Large Floor Cushion": lambda: floor_cushion(1215, s=230),
    "Pillow Pile": pillow_pile,
    "Curtains": curtain,
    "Wall Tapestry": wall_hanging,
    # curios
    "Potted Palm": potted_palm,
    "Pink Flower Arrangement": flower_arrangement,
    "White Flower Arrangement": lambda: flower_arrangement(1234, rgb("#f3eee2"), rgb("#4f74a8")),
    "Yellow Flower Arrangement": lambda: flower_arrangement(1235, rgb("#e6b84a"), rgb("#a8483a")),
    "Purple Flower Arrangement": lambda: flower_arrangement(1236, rgb("#9a6ab8"), rgb("#5f8f6a")),
    "Standing Mirror": standing_mirror,
    "Easel": easel,
    "Wall Shelf": wall_shelf,
    "Coat Rack": coat_rack,
    "Umbrella Stand": umbrella_stand,
    "Grandfather Clock": grandfather_clock,
    "Table Clock": table_clock,
    "Large Hourglass": large_hourglass,
    "Bird Cage": bird_cage,
    "Fish Bowl": fish_bowl,
    "Music Box": music_box,
    # castle & nobility
    "Banquet Table": banquet_table,
    "Long Banquet Table": lambda: banquet_table(1255, 900),
    "High-Backed Chair": high_back_chair,
    "Blue High-Backed Chair": lambda: high_back_chair(1256, BLUE),
    "Canopy Bed": canopy_bed,
    "Blue Canopy Bed": lambda: canopy_bed(1257, BLUE),
    "Royal Runner": royal_runner,
    "Lion Banner": heraldic_banner,
    "Cross Banner": lambda: heraldic_banner(1258, BLUE, "cross"),
    "Star Banner": lambda: heraldic_banner(1259, GREENC, "star"),
    "Armor Display": armor_display,
    "Weapon Display": weapon_display,
    "Great Fireplace": great_fireplace,
    "Chandelier": chandelier,
    "Vanity Table": vanity_table,
    "Foot Chest": foot_chest,
    "Harp": harp,
    "Globe": globe,
    # garden
    "Hedge": hedge,
    "Short Hedge": lambda: hedge(1276, 256, 130),
    "Hedge Corner": hedge_corner,
    "Topiary Ball": topiary_ball,
    "Small Topiary": lambda: topiary_ball(1277, 140),
    "Spiral Topiary": topiary_spiral,
    "Flower Bed": flower_bed,
    "Red Flower Bed": lambda: flower_bed(1278, [rgb("#c8443a"), shade(rgb("#c8443a"), 0.2)]),
    "Yellow Flower Bed": lambda: flower_bed(1279, [rgb("#e6b84a"), rgb("#f2d27a")]),
    "Purple Flower Bed": lambda: flower_bed(1280, [rgb("#9a6ab8"), rgb("#c8a0e0")]),
    "Round Flower Bed": lambda: flower_bed(1281, w=300, h=300, round_=True),
    "Round Red Flower Bed": lambda: flower_bed(1282, [rgb("#c8443a"), rgb("#f3eee2")], w=300, h=300, round_=True),
    "Garden Bench": garden_bench,
    "Stone Path": path_tiles,
    "Stepping Stones Path": stepping_stones,
    "Rose Arch": rose_arch,
    "Trellis": trellis,
    "Vegetable Bed": vegetable_bed,
    "Sundial": sundial,
    "Garden Lantern": garden_lantern,
    "Gazebo": gazebo,
    "Small Pond": small_pond,
}

DECOR_COLORABLE = {
    "Diamond Rug", "Medallion Rug", "Striped Rug", "Checkered Rug", "Square Rug", "Small Rug", "Long Runner",
    "Oval Rug", "Small Oval Rug", "Round Patterned Rug", "Small Round Rug", "Braided Rug",
    "Floor Cushion", "Large Floor Cushion", "Pillow Pile", "Curtains", "Wall Tapestry",
    "Banquet Table", "Long Banquet Table", "High-Backed Chair", "Canopy Bed", "Royal Runner", "Lion Banner", "Weapon Display",
}

# variants
PURPLE = rgb("#6a3a7a")
TEAL = rgb("#2f6461")
DECOR.update({
    "Purple Medallion Rug": lambda: rug_rect(1320, 440, 620, "medallion", main=PURPLE, trim=rgb("#e2c068")),
    "Teal Striped Rug": lambda: rug_rect(1321, 400, 560, "stripes", main=TEAL, trim=CREAM),
    "Blue Oval Rug": lambda: rug_oval(1322, main=BLUE),
    "Green Round Rug": lambda: round_rug(1323, main=GREENC),
    "Blue Runner": lambda: rug_rect(1324, 240, 760, "diamond", main=BLUE),
    "Gold Floor Cushion": lambda: floor_cushion(1216, rgb("#c9a040")),
    "Blue Floor Cushion": lambda: floor_cushion(1217, BLUE),
    "Purple Floor Cushion": lambda: floor_cushion(1218, PURPLE),
    "Blue Curtains": lambda: curtain(1219, BLUE),
    "Green Wall Tapestry": lambda: wall_hanging(1220, GREENC),
    "Purple Banner": lambda: heraldic_banner(1260, PURPLE, "star"),
    "Gold Lion Banner": lambda: heraldic_banner(1261, rgb("#8a6a2a"), "lion"),
    "Green High-Backed Chair": lambda: high_back_chair(1262, GREENC),
    "Purple Canopy Bed": lambda: canopy_bed(1263, PURPLE),
    "Long Hedge": lambda: hedge(1283, 768, 140),
    "Large Topiary": lambda: topiary_ball(1284, 280),
    "Blue Flower Bed": lambda: flower_bed(1285, [rgb("#6f8fd0"), rgb("#f3eee2")]),
    "White Flower Bed": lambda: flower_bed(1286, [rgb("#f3eee2"), rgb("#f2d27a")]),
    "Round Yellow Flower Bed": lambda: flower_bed(1287, [rgb("#e6b84a"), rgb("#f3eee2")], w=300, h=300, round_=True),
    "Red Rose Arrangement": lambda: flower_arrangement(1288, rgb("#c8443a"), rgb("#e6dcc4")),
    "Small Gazebo": lambda: _scaled(gazebo, 0.7),
})


def _scaled(fn, k):
    from PIL import Image

    img = fn()
    return img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)
