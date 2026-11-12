"""Weapons and war (batch 10): loose weapons, shields, racks, armour,
training gear, siege engines and camp pieces. Top-down, same pen style."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, dot, scallop, soft_shadow
from obj_craft import STEEL, handle, rot_pts
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

LEATHER = rgb("#7a4e32")
STRAW = rgb("#d9bf72")
CANVAS = rgb("#d8ccb0")
O = DETAIL * 2.0  # outline weight for weapons (same as the tools)
V = 0.08


def blade_shape(a, pts, color=STEEL):
    a.shape(pts, color, outline=O, corner=0, wob=0.1, depth=2, light_k=0.55, mottle=0, var=V)


# -- weapons (drawn into any art at any angle) ------------------------------------------------------


def sword_at(a, x, y, ang, L=230, w=16):
    """A sword lying flat: pommel, grip, crossguard, the blade with its fuller."""
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    a.shape(loc(ellipse(x, y, 9, 9, 20)), BRASS, outline=O, depth=2, mottle=0, var=V)
    a.shape(loc(rect(x + 6, y - 6, x + 50, y + 6)), LEATHER, outline=O, corner=3, depth=2, mottle=0, var=V)
    a.shape(loc(rect(x + 46, y - 30, x + 58, y + 30)), BRASS, outline=O, corner=4, depth=2, light_k=0.5, mottle=0, var=V)
    blade_shape(a, loc([(x + 58, y - w / 2), (x + L - 24, y - w / 2), (x + L, y), (x + L - 24, y + w / 2), (x + 58, y + w / 2)]))
    a.ink(loc([(x + 64, y), (x + L - 40, y)]), FINE * 1.2, color=shade(STEEL, 0.4), alpha=0.8, wob=0)


def dagger_at(a, x, y, ang):
    sword_at(a, x, y, ang, L=120, w=14)


def axe_head(a, hx, hy, ang, double=False):
    def side(s):
        edge = [(hx + 40 * math.cos(t), hy + s * (44 + 16 * math.sin(t))) for t in [-1.3 + k * 2.6 / 12 for k in range(13)]]
        return [(hx - 10, hy + s * 10), (hx + 10, hy + s * 10)] + ([p for p in edge] if s > 0 else edge) + []

    for s in ((-1, 1) if double else (-1,)):
        pts = [(hx - 12, hy + s * 8), (hx + 12, hy + s * 8), (hx + 30, hy + s * 40)]
        pts += [(hx + 34 * math.cos(t), hy + s * (40 + 14 * math.sin(t))) for t in [0.1 + k * (math.pi - 0.2) / 10 for k in range(11)]]
        pts += [(hx - 30, hy + s * 40)]
        blade_shape(a, rot_pts(pts, hx, hy, ang))
    a.shape(rot_pts(rect(hx - 14, hy - 12, hx + 14, hy + 12), hx, hy, ang), IRON, outline=O, corner=3, depth=2, mottle=0, var=V)


def battleaxe_at(a, x, y, ang, L=220):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx + ux * 12, hy + uy * 12, 12)
    axe_head(a, hx, hy, ang, double=True)


def warhammer_at(a, x, y, ang, L=200):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx + ux * 10, hy + uy * 10, 12)
    a.shape(rot_pts(rect(hx - 18, hy - 34, hx + 18, hy + 10), hx, hy, ang), IRON, outline=O, corner=4, depth=3, light_k=0.5, mottle=0, var=V)
    blade_shape(a, rot_pts([(hx - 8, hy + 10), (hx + 8, hy + 10), (hx, hy + 48)], hx, hy, ang), IRON)


def mace_at(a, x, y, ang, L=170):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx, hy, 11)
    for k in range(8):
        t = 2 * math.pi * k / 8
        blade_shape(a, [(hx + 18 * math.cos(t - 0.25), hy + 18 * math.sin(t - 0.25)), (hx + 34 * math.cos(t), hy + 34 * math.sin(t)), (hx + 18 * math.cos(t + 0.25), hy + 18 * math.sin(t + 0.25))], IRON)
    a.shape(ellipse(hx, hy, 22, 22, 32), IRON, outline=O, depth=3, light_k=0.5, mottle=0, var=V)


def halberd_at(a, x, y, ang, L=360):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx, hy, 11)
    blade_shape(a, rot_pts([(hx, hy - 6), (hx + 50, hy), (hx, hy + 6)], hx, hy, ang))
    blade_shape(a, rot_pts([(hx - 30, hy - 6), (hx - 4, hy - 6), (hx + 6, hy - 40), (hx - 20, hy - 46), (hx - 34, hy - 30)], hx, hy, ang))
    blade_shape(a, rot_pts([(hx - 26, hy + 6), (hx - 8, hy + 6), (hx - 18, hy + 28)], hx, hy, ang))


def spear_at(a, x, y, ang, L=320):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx, hy, 10)
    blade_shape(a, rot_pts([(hx - 4, hy - 9), (hx + 44, hy), (hx - 4, hy + 9)], hx, hy, ang))


def arrow_at(a, x, y, ang, L=150):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    a.ink([(x, y), (hx, hy)], 7, color=INK, taper=False, var=V)
    a.ink([(x, y), (hx, hy)], 3.5, color=WOOD_LIGHT, taper=False, var=V)
    blade_shape(a, rot_pts([(hx - 2, hy - 6), (hx + 16, hy), (hx - 2, hy + 6)], hx, hy, ang), IRON)
    for s in (-1, 1):
        a.shape(rot_pts([(x, y), (x + 26, y), (x + 34, y + s * 9), (x + 8, y + s * 9)], x, y, ang), rgb("#e6dcc4"), outline=FINE * 1.3, corner=1, depth=1, mottle=0)


def bow_at(a, x, y, ang, L=240):
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    limb = chaikin([(x, y - L / 2), (x + 34, y - L / 4), (x + 40, y), (x + 34, y + L / 4), (x, y + L / 2)], False, 3)
    a.ink(loc(limb), 13, color=INK, taper=True, var=V)
    a.ink(loc(limb), 8, color=WOOD, taper=True, var=V)
    a.ink(loc([(x, y - L / 2), (x, y + L / 2)]), FINE * 1.1, color=rgb("#e6dcc4"), wob=0)
    a.shape(loc(rect(x + 30, y - 14, x + 46, y + 14)), LEATHER, outline=O * 0.8, corner=3, depth=1, mottle=0, var=V)


def crossbow_at(a, x, y, ang):
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    a.shape(loc(rect(x, y - 12, x + 180, y + 12)), WOOD, outline=O, corner=6, depth=3, mottle=0, var=V)
    limb = chaikin([(x + 150, y - 90), (x + 172, y - 40), (x + 176, y), (x + 172, y + 40), (x + 150, y + 90)], False, 3)
    a.ink(loc(limb), 13, color=INK, taper=False, var=V)
    a.ink(loc(limb), 8, color=IRON, taper=False, var=V)
    a.ink(loc([(x + 150, y - 90), (x + 70, y), (x + 150, y + 90)]), FINE * 1.1, color=rgb("#e6dcc4"), wob=0)
    a.shape(loc(rect(x + 60, y - 6, x + 90, y + 6)), IRON, outline=O * 0.8, corner=2, depth=1, mottle=0, var=V)


def weapon(fn, w, h, ang, x, y, **kw):
    def make(seed=900):
        a = Art(w, h, seed)
        fn(a, x, y, ang, **kw)
        return a.image()

    return make


# -- shields (red = colorable) --------------------------------------------------------------------


def round_shield(seed=901):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 94, 5, 6)

    def planks(art, p):
        for k in range(-3, 4):
            art.ink([(m + k * 26, 10), (m + k * 26, s - 10)], DETAIL * 0.8, color=shade(RED, 0.4), alpha=0.8, taper=False)

    a.shape(ellipse(m, m, 94, 94, 80), RED, depth=10, light_k=0.4, detail=planks)
    a.ink(ellipse(m, m, 88, 88, 80), DETAIL * 2.6, closed=True, color=IRON)
    a.shape(ellipse(m, m, 28, 28, 40), IRON, outline=O, depth=4, light_k=0.6, mottle=0, var=V)
    for k in range(8):
        t = 2 * math.pi * k / 8
        dot(a, m + 80 * math.cos(t), m + 80 * math.sin(t), 4, tint(IRON, 0.4))
    return a.image()


def kite_shield(seed=902):
    w, h = 200, 300
    a = Art(w, h, seed)
    pts = chaikin([(20, 50), (w / 2, 14), (w - 20, 50), (w - 30, 150), (w / 2, h - 14), (30, 150)], True, 2)
    soft_shadow(a, pts, dx=5, dy=6)

    def deco(art, p):
        art.ink([(w / 2, 30), (w / 2, h - 30)], DETAIL * 2, color=rgb("#e2c068"))
        art.ink([(40, 90), (w - 40, 90)], DETAIL * 2, color=rgb("#e2c068"))

    a.shape(pts, RED, depth=10, light_k=0.4, detail=deco)
    inner = [(w / 2 + (x - w / 2) * 0.9, 150 + (y - 150) * 0.92) for x, y in pts]
    a.ink(inner, DETAIL, closed=True, color=shade(RED, 0.45))
    return a.image()


def heater_shield(seed=903):
    w, h = 200, 240
    a = Art(w, h, seed)
    pts = chaikin([(20, 20), (w - 20, 20), (w - 20, 110), (w / 2, h - 14), (20, 110)], True, 2)
    soft_shadow(a, pts, dx=5, dy=6)

    def deco(art, p):
        # A chevron charge.
        art.shape([(30, 140), (w / 2, 70), (w - 30, 140), (w - 30, 170), (w / 2, 100), (30, 170)], rgb("#e2c068"), outline=DETAIL, corner=2, depth=2, mottle=0)

    a.shape(pts, RED, depth=10, light_k=0.4, detail=deco)
    a.ink([(w / 2 + (x - w / 2) * 0.9, 110 + (y - 110) * 0.9) for x, y in pts], DETAIL, closed=True, color=shade(RED, 0.45))
    return a.image()


# -- racks & armour ---------------------------------------------------------------------------------


def weapon_rack(seed=911):
    w, h = 460, 250
    a = Art(w, h, seed)
    a.shape(rect(4, 4, w - 4, 26), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    board(a, 10, 22, w - 10, h - 12, WOOD_DARK, n=3, corner=4)
    sword_at(a, 30, 60, 0.0, 220)
    spear_at(a, 20, 110, 0.0, 330)
    mace_at(a, 260, 70, 0.0, 140)
    battleaxe_at(a, 30, 180, 0.0, 190)
    return a.image()


def spear_stand(seed=912):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    # A round stand from above: spears stand upright in it, so we see their
    # tips pointing out a little (a hint of perspective), on a wooden ring.
    a.shape(ellipse(m, m, 70, 70, 64), WOOD_DARK, depth=8)
    a.shape(ellipse(m, m, 46, 46, 56), shade(WOOD_DARK, 0.35), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.5)
    for k in range(7):
        t = 2 * math.pi * k / 7 + 0.3
        x0, y0 = m + 34 * math.cos(t), m + 34 * math.sin(t)
        x1, y1 = m + 104 * math.cos(t), m + 104 * math.sin(t)
        handle(a, x0, y0, x1, y1, 9)
        blade_shape(a, rot_pts([(x1 - 4, y1 - 8), (x1 + 34, y1), (x1 - 4, y1 + 8)], x1, y1, t))
    return a.image()


def armor_stand(seed=913):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    # Plate armour on its stand, from above: the pauldrons (shoulders), the
    # breastplate's top, the helmet in the middle.
    a.shape(ellipse(m, m + 70, 56, 18, 32), WOOD_DARK, outline=DETAIL * 1.2, depth=3)  # the stand's base, peeking out
    for side in (-1, 1):
        a.shape(ellipse(m + side * 60, m, 42, 50, 40), STEEL, outline=O, depth=6, light_k=0.5, mottle=0, var=V, detail=lambda art, p, side=side: [art.ink(chaikin([(m + side * 30, m - 30 + k * 18), (m + side * 64, m - 34 + k * 18), (m + side * 96, m - 20 + k * 18)], False, 2), FINE * 1.3, color=shade(STEEL, 0.45), alpha=0.8) for k in range(4)])
    a.shape(ellipse(m, m + 10, 60, 50, 48), tint(STEEL, 0.05), outline=O, depth=6, light_k=0.5, mottle=0, var=V)
    a.shape(ellipse(m, m - 6, 36, 40, 40), tint(STEEL, 0.12), outline=O, depth=6, light_k=0.55, mottle=0, var=V)
    a.shape(scallop(m, m - 24, 14, a.rng, 7, 0.2), RED, outline=FINE * 1.3, depth=2, mottle=0)  # plume
    return a.image()


def helmet(seed=914):
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 52, 4, 5)
    a.shape(ellipse(m, m, 52, 56, 48), STEEL, outline=O, depth=6, light_k=0.55, mottle=0, var=V)
    a.ink([(m, m - 54), (m, m + 54)], DETAIL * 1.6, color=shade(STEEL, 0.4))
    a.shape(rect(m - 30, m + 26, m + 30, m + 38), shade(STEEL, 0.5), outline=FINE * 1.3, corner=4, depth=1, mottle=0)  # visor slit
    return a.image()


# -- training ---------------------------------------------------------------------------------------


def archery_target(seed=921):
    w, h = 260, 200
    a = Art(w, h, seed)
    # A target on its easel: the straw boss seen from above at an angle (a
    # wide oval with rings), the easel's legs behind it.
    for x in (60, w - 60):
        a.ink([(x, 40), (x + (20 if x < w / 2 else -20), h - 20)], 14, color=INK, taper=False)
        a.ink([(x, 40), (x + (20 if x < w / 2 else -20), h - 20)], 9, color=WOOD_DARK, taper=False)
    a.shape(ellipse(w / 2, 80, 110, 60, 64), STRAW, depth=8, light_k=0.3)
    for r, c in ((0.8, rgb("#f2efe6")), (0.6, rgb("#c8443a")), (0.4, rgb("#f2efe6")), (0.2, rgb("#c8443a"))):
        a.shape(ellipse(w / 2, 80, 100 * r, 54 * r, 48), c, outline=FINE * 1.2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    for x, y, t in ((w / 2 + 10, 76, -2.2), (w / 2 - 34, 92, -2.6)):
        arrow_at(a, x + 60 * math.cos(t), y + 60 * math.sin(t), t + math.pi, 60)
    return a.image()


def training_dummy(seed=922):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    # Post with a crossbar (arms), a straw-stuffed sack body and head.
    a.shape(rect(20, m - 12, s - 20, m + 12), WOOD, outline=O * 0.8, corner=6, depth=4, var=V)
    burlap = rgb("#c9ad7c")
    a.shape(ellipse(m, m + 10, 54, 44, 40), burlap, depth=8, light_k=0.3, detail=lambda art, p: [art.ink([(m - 40, m + y), (m + 40, m + y)], FINE * 1.1, color=shade(burlap, 0.4), alpha=0.7) for y in (-6, 12, 30)])
    a.shape(ellipse(m, m - 22, 30, 30, 36), tint(burlap, 0.08), outline=DETAIL * 1.3, depth=5, light_k=0.4)
    a.ink([(m - 14, m - 30), (m + 14, m - 14)], DETAIL * 1.3, color=rgb("#7a2e26"))
    a.ink([(m + 14, m - 30), (m - 14, m - 14)], DETAIL * 1.3, color=rgb("#7a2e26"))
    for x in (28, s - 28):
        for _ in range(5):
            t = a.rng.uniform(0, 6.28)
            a.ink([(x, m), (x + 14 * math.cos(t), m + 14 * math.sin(t))], FINE * 1.2, color=STRAW)
    return a.image()


# -- siege ----------------------------------------------------------------------------------------


def catapult(seed=931):
    w, h = 320, 480
    a = Art(w, h, seed)
    # The base frame on four wheels (seen as narrow bands), the A-frame, the
    # throwing arm with its bucket, counterweight rope.
    for x in (30, w - 30):
        for y in (90, h - 90):
            a.shape(rect(x - 14, y - 50, x + 14, y + 50), WOOD_DARK, outline=O * 0.8, corner=10, depth=4, var=V)
    for x in (54, w - 54):
        a.shape(rect(x - 14, 20, x + 14, h - 20), WOOD, outline=O * 0.8, corner=6, depth=5, var=V)
    for y in (60, h / 2, h - 60):
        a.shape(rect(40, y - 12, w - 40, y + 12), WOOD, outline=O * 0.8, corner=5, depth=4, var=V)
    a.shape(rect(w / 2 - 16, 90, w / 2 + 16, h - 110), WOOD_LIGHT, outline=O * 0.8, corner=8, depth=6, light_k=0.4, var=V)
    a.shape(ellipse(w / 2, 90, 40, 34, 40), WOOD_DARK, outline=O * 0.8, depth=4, var=V)
    a.shape(ellipse(w / 2, 90, 26, 20, 32), shade(WOOD_DARK, 0.4), outline=DETAIL, depth=4, shade_k=0, light_k=0, ao=0.5)
    a.shape(ellipse(w / 2, 90, 14, 12, 24), STONE, outline=DETAIL, depth=3, light_k=0.4, mottle=0)
    a.ink([(w / 2, h - 110), (w / 2, h - 30)], DETAIL * 1.4, color=rgb("#c9b088"))
    return a.image()


def ballista(seed=932):
    w, h = 340, 300
    a = Art(w, h, seed)
    a.shape(rect(w / 2 - 50, h - 90, w / 2 + 50, h - 20), WOOD_DARK, outline=O * 0.8, corner=8, depth=6, var=V)
    a.shape(rect(w / 2 - 16, 40, w / 2 + 16, h - 40), WOOD, outline=O * 0.8, corner=6, depth=6, light_k=0.4, var=V)
    limb = chaikin([(20, 120), (90, 90), (w / 2, 80), (w - 90, 90), (w - 20, 120)], False, 3)
    a.ink(limb, 22, color=INK, taper=False, var=V)
    a.ink(limb, 15, color=WOOD_DARK, taper=False, var=V)
    a.ink([(20, 120), (w / 2, h - 110), (w - 20, 120)], FINE * 1.4, color=rgb("#e6dcc4"), wob=0)
    spear_at(a, w / 2, h - 110, -math.pi / 2, 160)
    return a.image()


# -- camp -----------------------------------------------------------------------------------------


def military_tent(seed=941):
    w, h = 420, 340
    a = Art(w, h, seed)
    # A ridge tent from above: two sloping cloth panels (the lit one lighter),
    # the ridge pole, guy ropes and pegs, the open flap at the front.
    for x0, y0, x1, y1 in ((10, 30, 40, 10), (w - 10, 30, w - 40, 10), (10, h - 30, 40, h - 10), (w - 10, h - 30, w - 40, h - 10)):
        a.ink([(x0, y0), (w / 2 + (x0 - w / 2) * 0.8, h / 2 + (y0 - h / 2) * 0.8)], FINE * 1.3, color=rgb("#b8a882"))
        a.shape(ellipse(x0, y0, 5, 5, 12), WOOD_DARK, outline=FINE * 1.2, depth=1, mottle=0)
    left = rect(40, 40, w / 2, h - 40)
    right = rect(w / 2, 40, w - 40, h - 40)
    a.shape(left, tint(RED, 0.05), outline=OUTLINE, corner=4, depth=6, light_k=0.35, detail=lambda art, p: [art.ink([(x, 44), (x, h - 44)], FINE, color=shade(RED, 0.35), alpha=0.6) for x in (90, 140)])
    a.shape(right, shade(RED, 0.18), outline=OUTLINE, corner=4, depth=6, shade_k=0.6, light_k=0.1, detail=lambda art, p: [art.ink([(x, 44), (x, h - 44)], FINE, color=shade(RED, 0.5), alpha=0.6) for x in (w - 140, w - 90)])
    a.ink([(w / 2, 40), (w / 2, h - 40)], DETAIL * 2.4)
    a.shape([(w / 2 - 34, h - 40), (w / 2, h - 90), (w / 2 + 34, h - 40)], rgb("#2a221e"), outline=DETAIL, corner=2, depth=2, shade_k=0, light_k=0, mottle=0)
    return a.image()


def cheval_de_frise(seed=942):
    w, h = 480, 230
    a = Art(w, h, seed)
    a.shape(rect(10, h / 2 - 16, w - 10, h / 2 + 16), WOOD_DARK, outline=O * 0.8, corner=10, depth=6, var=V)
    for k in range(7):
        x = 40 + k * 66
        t = math.pi / 2 + (0.5 if k % 2 else -0.5)
        for s in (-1, 1):
            x1, y1 = x + s * 76 * math.cos(t), h / 2 + s * 76 * math.sin(t)
            handle(a, x, h / 2, x1, y1, 11, WOOD)
            blade_shape(a, rot_pts([(x1 - 2, y1 - 7), (x1 + 16, y1), (x1 - 2, y1 + 7)], x1, y1, t if s > 0 else t + math.pi), WOOD_LIGHT)
    return a.image()


def palisade(seed=943):
    w, h = 512, 90
    a = Art(w, h, seed)
    # Sharpened logs standing in a row, seen from above: their pointed tops.
    for k in range(10):
        x = 26 + k * 51
        r = a.rng.uniform(22, 26)
        p = ellipse(x, h / 2, r, r, 32)
        soft_shadow(a, p, dx=4, dy=6, alpha=0.35)
        col = vary(a.rng, WOOD, 0.06)
        for j in range(6):
            t0, t1 = 2 * math.pi * j / 6, 2 * math.pi * (j + 1) / 6
            face = [(x + r * math.cos(t0), h / 2 + r * math.sin(t0)), (x + r * math.cos(t1), h / 2 + r * math.sin(t1)), (x, h / 2)]
            lit = math.cos((t0 + t1) / 2 + math.pi * 0.75)
            a.shape(face, tint(col, 0.2 * lit) if lit > 0 else shade(col, -0.25 * lit), outline=0, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.ink(p, DETAIL * 1.3, closed=True)
    a.ink([(10, h - 12), (w - 10, h - 12)], DETAIL * 1.6, color=rgb("#c9b088"))
    return a.image()


def war_drum(seed=944):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 82, 82, 72), RED, depth=10, light_k=0.3, detail=lambda art, p: [art.ink([(m + 70 * math.cos(t), m + 70 * math.sin(t)), (m + 82 * math.cos(t + 0.4), m + 82 * math.sin(t + 0.4))], FINE * 1.3, color=rgb("#e6dcc4")) for t in [2 * math.pi * k / 12 for k in range(12)]])
    a.shape(ellipse(m, m, 66, 66, 64), rgb("#e6dcc4"), outline=DETAIL * 1.3, depth=4, light_k=0.4)
    for t in (0.6, 2.2):
        x0, y0 = m + 30 * math.cos(t), m + 30 * math.sin(t)
        handle(a, x0, y0, x0 + 56 * math.cos(t + 0.8), y0 + 56 * math.sin(t + 0.8), 8)
        a.shape(ellipse(x0, y0, 10, 10, 16), rgb("#e6dcc4"), outline=FINE * 1.3, depth=1, mottle=0)
    return a.image()


def war_banner(seed=945):
    w, h = 240, 420
    a = Art(w, h, seed)
    # A banner on its pole lying on the ground.
    handle(a, w / 2, 10, w / 2, h - 10, 12)
    cloth = [(w / 2 + 6, 40), (w - 20, 40), (w - 20, 260), (w / 2 + 60, 230), (w / 2 + 6, 260)]
    a.shape(cloth, RED, corner=2, depth=6, light_k=0.3, detail=lambda art, p: art.shape(ellipse(w / 2 + 52, 130, 30, 30, 32), rgb("#e2c068"), outline=DETAIL, depth=2, mottle=0))
    a.shape(rect(w / 2 - 50, 30, w / 2 + 50, 44), WOOD_DARK, outline=O * 0.8, corner=5, depth=3, var=V)
    blade_shape(a, [(w / 2 - 9, 14), (w / 2, -4 + 10), (w / 2 + 9, 14)], BRASS) if False else None
    return a.image()


WAR = {
    "Longsword": weapon(sword_at, 300, 120, -0.15, 20, 70),
    "Dagger": weapon(dagger_at, 180, 100, -0.3, 20, 70),
    "Battle Axe": weapon(battleaxe_at, 320, 200, -0.25, 20, 140),
    "Warhammer": weapon(warhammer_at, 300, 180, -0.3, 20, 140),
    "Mace": weapon(mace_at, 260, 160, -0.3, 20, 120),
    "Halberd": weapon(halberd_at, 460, 160, -0.12, 20, 110),
    "Spear": weapon(spear_at, 420, 100, -0.1, 20, 70),
    "Bow": weapon(bow_at, 140, 290, 0.0, 40, 145),
    "Crossbow": weapon(crossbow_at, 240, 220, 0.0, 20, 110),
    "Arrows": lambda: _arrows(),
    "Quiver": lambda: _quiver(),
    "Round Shield": round_shield,
    "Kite Shield": kite_shield,
    "Heater Shield": heater_shield,
    "Weapon Rack": weapon_rack,
    "Spear Stand": spear_stand,
    "Armor Stand": armor_stand,
    "Helmet": helmet,
    "Archery Target": archery_target,
    "Training Dummy": training_dummy,
    "Catapult": catapult,
    "Ballista": ballista,
    "Military Tent": military_tent,
    "Cheval de Frise": cheval_de_frise,
    "Palisade": palisade,
    "War Drum": war_drum,
    "War Banner": war_banner,
}


def _arrows(seed=950):
    s = 240
    a = Art(s, s, seed)
    for _ in range(6):
        t = a.rng.uniform(0, 6.28)
        x, y = 120 - 70 * math.cos(t) + a.rng.uniform(-20, 20), 120 - 70 * math.sin(t) + a.rng.uniform(-20, 20)
        arrow_at(a, x, y, t, 140)
    return a.image()


def _quiver(seed=951):
    w, h = 140, 320
    a = Art(w, h, seed)
    body = rect(30, 80, w - 30, h - 20)
    a.shape(body, LEATHER, corner=24, depth=8, light_k=0.35, detail=lambda art, p: [art.ink([(34, y), (w - 34, y)], FINE * 1.2, color=shade(LEATHER, 0.45), alpha=0.8) for y in (110, h - 50)])
    for k in range(5):
        x = 44 + k * 13
        a.ink([(x, 90), (x + a.rng.uniform(-6, 6), 30)], 5, color=INK, taper=False)
        a.ink([(x, 90), (x + a.rng.uniform(-6, 6), 30)], 2.5, color=WOOD_LIGHT, taper=False)
        a.shape([(x - 6, 22), (x + 6, 22), (x + 7, 46), (x - 7, 46)], vary(a.rng, rgb("#e6dcc4"), 0.05), outline=FINE * 1.2, corner=1, depth=1, mottle=0)
    a.ink([(30, 90), (w - 20, 30)], DETAIL * 1.6, color=rgb("#5a3a22"))
    return a.image()


WAR_COLORABLE = {"Round Shield", "Kite Shield", "Heater Shield", "Armor Stand", "Military Tent", "War Drum", "War Banner"}
