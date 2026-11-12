"""Dungeon and prison (batch 9): restraints, torture, traps, remains and
dungeon floor details. Top-down, same pen style."""

import math

import skia

from kit import IRON, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, dot, scallop, soft_shadow
from obj_magic import BONE, glow, skull_at
from obj_stone import DARK_STONE, GREY, stone_block
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

RUST = rgb("#8a5a42")
DARK_IRON = rgb("#4a4c52")
STRAW = rgb("#d9bf72")
BLOOD = rgb("#7a1e1c")
SLIME = rgb("#7fae4a")


# -- chains & restraints ----------------------------------------------------------------------------


def chain(a, pts, link=12, width=None, color=DARK_IRON):
    """A chain along a polyline: alternating flat and edge-on links."""
    from pen import resample

    p = resample(pts, False, link * 0.9)
    for i in range(len(p) - 1):
        (x0, y0), (x1, y1) = p[i], p[i + 1]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ang = math.atan2(y1 - y0, x1 - x0)
        if i % 2 == 0:
            a.shape(ellipse(cx, cy, link * 0.7, link * 0.42, 20, rot=ang), color, outline=DETAIL * 1.1, depth=1.5, shade_k=0.3, light_k=0.5, ao=0, mottle=0)
            a.shape(ellipse(cx, cy, link * 0.38, link * 0.14, 16, rot=ang), (232, 223, 200), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0) if False else a.ink(ellipse(cx, cy, link * 0.36, link * 0.12, 16, rot=ang), FINE * 1.2, closed=True, color=INK, alpha=0.9)
        else:
            a.ink([(cx - math.cos(ang) * link * 0.6, cy - math.sin(ang) * link * 0.6), (cx + math.cos(ang) * link * 0.6, cy + math.sin(ang) * link * 0.6)], link * 0.42 + 4, color=INK, taper=False)
            a.ink([(cx - math.cos(ang) * link * 0.6, cy - math.sin(ang) * link * 0.6), (cx + math.cos(ang) * link * 0.6, cy + math.sin(ang) * link * 0.6)], link * 0.42, color=tint(color, 0.15), taper=False)


def cuff(a, x, y, r=16):
    a.shape(ellipse(x, y, r, r, 28), DARK_IRON, outline=DETAIL * 1.3, depth=3, light_k=0.5, mottle=0)
    a.ink(ellipse(x, y, r * 0.6, r * 0.6, 24), FINE * 1.3, closed=True, alpha=0.9)
    a.shape(rect(x - 4, y - r - 4, x + 4, y - r + 6), IRON, outline=FINE * 1.2, corner=1, depth=1, mottle=0)


def wall_shackles(seed=801):
    w, h = 260, 160
    a = Art(w, h, seed)
    a.shape(rect(6, 4, w - 6, 24), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    for x in (70, w - 70):
        a.shape(rect(x - 10, 14, x + 10, 34), IRON, outline=DETAIL, corner=3, depth=2, mottle=0)
        chain(a, [(x, 34), (x + (10 if x < w / 2 else -10), 70), (x, 104)], 13)
        cuff(a, x, 122, 17)
    return a.image()


def floor_chains(seed=802):
    s = 260
    a = Art(s, s, seed)
    pts = [(30 + 200 * t + 24 * math.sin(t * 6), 60 + 140 * t + 30 * math.sin(t * 4 + 1)) for t in [k / 20 for k in range(21)]]
    chain(a, pts, 14)
    cuff(a, pts[-1][0] + 10, pts[-1][1] + 12, 18)
    a.shape(ellipse(pts[0][0], pts[0][1], 14, 14, 24), IRON, outline=DETAIL * 1.2, depth=3, mottle=0)
    return a.image()


def ball_and_chain(seed=803):
    w, h = 280, 180
    a = Art(w, h, seed)
    chain(a, [(40, 60), (110, 90), (170, 80)], 14)
    cuff(a, 32, 52, 18)
    soft_shadow(a, (210, 100), 46, 5, 6, 0.4, 5)
    a.shape(ellipse(210, 100, 46, 46, 48), DARK_IRON, outline=OUTLINE, depth=10, light_k=0.55)
    a.ink([(186, 80), (200, 72)], FINE * 2, color=tint(DARK_IRON, 0.6), alpha=0.9)
    return a.image()


def manacles(seed=804):
    w, h = 200, 120
    a = Art(w, h, seed)
    chain(a, [(56, 60), (100, 72), (144, 60)], 12)
    cuff(a, 40, 58, 20)
    cuff(a, 160, 58, 20)
    return a.image()


def hanging_cage(seed=805):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    # A round cage seen from above: the domed top with its ring, bars running
    # down to the base ring below (slightly offset: the hint of perspective).
    a.shape(ellipse(m + 6, m + 10, 100, 100, 80), shade(STONE, 0.3), outline=DETAIL, depth=4, shade_k=0, light_k=0, ao=0.4)
    for k in range(16):
        t = 2 * math.pi * k / 16
        a.ink([(m + 96 * math.cos(t), m + 96 * math.sin(t)), (m + 6 + 100 * math.cos(t), m + 10 + 100 * math.sin(t))], DETAIL * 1.6, color=DARK_IRON, taper=False)
    a.ink(ellipse(m + 6, m + 10, 100, 100, 80), DETAIL * 2, closed=True, color=DARK_IRON)
    a.ink(ellipse(m, m, 96, 96, 80), DETAIL * 2.4, closed=True, color=INK)
    a.ink(ellipse(m, m, 96, 96, 80), DETAIL * 1.4, closed=True, color=IRON)
    for k in range(8):
        t = 2 * math.pi * k / 8
        a.ink([(m, m), (m + 96 * math.cos(t), m + 96 * math.sin(t))], DETAIL * 1.4, color=IRON, taper=False)
    a.shape(ellipse(m, m, 14, 14, 24), IRON, outline=DETAIL * 1.3, depth=3, mottle=0)
    a.ink(ellipse(m, m, 7, 7, 16), FINE * 1.3, closed=True)
    return a.image()


def prison_cot(seed=806):
    w, h = 220, 420
    a = Art(w, h, seed)
    board(a, 8, 8, w - 8, h - 8, WOOD_DARK, n=4, vertical=True, corner=6)

    def straw(art, p):
        for _ in range(110):
            x, y = art.rng.uniform(30, w - 30), art.rng.uniform(40, h - 40)
            t = art.rng.uniform(-0.5, 0.5) + math.pi / 2
            art.ink([(x, y), (x + 14 * math.cos(t), y + 14 * math.sin(t))], FINE * 1.1, color=shade(STRAW, art.rng.uniform(0.1, 0.45)), alpha=0.9, wob=0.2)

    a.shape(blob(w / 2, h / 2, 86, a.rng, 10, 0.08, ry=176), STRAW, outline=DETAIL * 1.2, smooth=True, depth=8, detail=straw)
    a.shape(rect(30, 400 - 380, w - 30, 90), rgb("#9a8a72"), outline=DETAIL * 1.2, corner=14, depth=5)  # rag pillow
    return a.image()


def straw_pile(seed=807):
    s = 240
    a = Art(s, s, seed)
    m = s / 2

    def straw(art, p):
        for _ in range(180):
            x, y = art.rng.uniform(20, s - 20), art.rng.uniform(20, s - 20)
            t = art.rng.uniform(0, 6.28)
            art.ink([(x, y), (x + 16 * math.cos(t), y + 16 * math.sin(t))], FINE * 1.1, color=shade(STRAW, art.rng.uniform(0.05, 0.45)), alpha=0.9, wob=0.2)

    a.shape(blob(m, m, 96, a.rng, 12, 0.14), STRAW, outline=DETAIL, smooth=True, depth=8, detail=straw)
    for _ in range(18):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(96, 112)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        a.ink([(x, y), (x + 12 * math.cos(t), y + 12 * math.sin(t))], FINE * 1.1, color=shade(STRAW, 0.2))
    return a.image()


def prisoner_bucket(seed=808):
    s = 130
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 46, 4, 5)
    a.shape(ellipse(m, m, 46, 46, 48), WOOD, outline=DETAIL * 1.4, depth=6, detail=lambda art, p: [art.ink([(m + 34 * math.cos(t), m + 34 * math.sin(t)), (m + 46 * math.cos(t), m + 46 * math.sin(t))], DETAIL * 0.7, color=shade(WOOD, 0.5), taper=False) for t in [2 * math.pi * k / 12 for k in range(12)]])
    a.shape(ellipse(m, m, 32, 32, 40), rgb("#5a4a30"), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.6)
    return a.image()


# -- torture & execution -----------------------------------------------------------------------------


def rack(seed=811):
    w, h = 260, 520
    a = Art(w, h, seed)
    board(a, 20, 30, w - 20, h - 30, WOOD, n=3, vertical=True, corner=6)
    for y in (40, h - 40):
        a.shape(rect(8, y - 18, w - 8, y + 18), WOOD_DARK, outline=DETAIL * 1.3, corner=8, depth=5)
        for x in (24, w - 24):
            a.shape(ellipse(x, y, 16, 16, 24), WOOD_LIGHT, outline=DETAIL, depth=3, mottle=0)
            for k in range(4):
                t = math.pi / 4 + k * math.pi / 2
                a.ink([(x, y), (x + 26 * math.cos(t), y + 26 * math.sin(t))], DETAIL * 1.6, color=WOOD_DARK)
    for x in (w / 2 - 34, w / 2 + 34):
        a.ink([(x, 58), (x, 110)], FINE * 1.4, color=rgb("#c9b088"))
        a.ink([(x, h - 58), (x, h - 110)], FINE * 1.4, color=rgb("#c9b088"))
        cuff(a, x, 120, 13)
        cuff(a, x, h - 120, 13)
    return a.image()


def stocks(seed=812):
    w, h = 380, 160
    a = Art(w, h, seed)
    for x in (40, w - 40):
        a.shape(rect(x - 18, 30, x + 18, h - 30), WOOD_DARK, outline=DETAIL * 1.3, corner=5, depth=5)
    # The stocks board standing upright: seen from above as a thick plank
    # with its head and wrist holes showing as notches.
    a.shape(rect(14, h / 2 - 22, w - 14, h / 2 + 22), WOOD, corner=6, depth=6, light_k=0.4)
    a.ink([(14, h / 2), (w - 14, h / 2)], DETAIL, alpha=0.9, taper=False)
    for x, r in ((w / 2, 16), (w / 2 - 70, 10), (w / 2 + 70, 10)):
        a.shape(ellipse(x, h / 2, r, r * 0.6, 24), rgb("#2a221e"), outline=FINE * 1.2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    return a.image()


def execution_block(seed=813):
    w, h = 300, 220
    a = Art(w, h, seed)
    a.shape(scallop(110, 110, 84, a.rng, 12, 0.05), shade(WOOD, 0.1), depth=10, detail=lambda art, p: [art.ink(scallop(110, 110, r, art.rng, 9, 0.03), FINE * 1.1, closed=True, color=shade(WOOD, 0.5), alpha=0.7) for r in (30, 56)])
    a.shape(ellipse(110, 70, 22, 12, 24), shade(WOOD, 0.35), outline=FINE * 1.2, depth=2, shade_k=0, light_k=0, mottle=0)  # the neck notch
    with a.clip(to_path(scallop(110, 110, 84, a.rng, 12, 0.05))):
        a.shape(blob(140, 130, 24, a.rng, 9, 0.3), BLOOD, outline=0, smooth=True, depth=1, shade_k=0, light_k=0.2, ao=0, mottle=0.1)
    # The headsman's axe leaning on it.
    from obj_craft import axe_at

    axe_at(a, 170, 200, -0.6, 140)
    return a.image()


def brazier_irons(seed=815):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 90, rgb("#ff9a3c"), 0.35)
    a.shape(ellipse(m, m, 76, 76, 64), DARK_IRON, depth=10)
    a.shape(ellipse(m, m, 58, 58, 64), rgb("#2c2420"), outline=DETAIL * 1.3, depth=8, shade_k=0, light_k=0, ao=0.6)
    for _ in range(26):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, 50)
        hot = a.rng.random() < 0.5
        a.shape(blob(m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(6, 10), a.rng, 6, 0.2), rgb("#e9773a") if hot else rgb("#2e2a28"), outline=FINE, depth=1, shade_k=0.3, light_k=0.4, ao=0, mottle=0)
    for t in (0.4, 2.2, 4.0):
        x0, y0 = m + 20 * math.cos(t), m + 20 * math.sin(t)
        x1, y1 = m + 104 * math.cos(t), m + 104 * math.sin(t)
        a.ink([(x0, y0), (x1, y1)], 10, color=INK, taper=False)
        a.ink([(x0, y0), (x1, y1)], 5.5, color=IRON, taper=False)
        dot(a, x0, y0, 6, rgb("#ff8a3a"))
    return a.image()


def torture_table(seed=816):
    w, h = 260, 480
    a = Art(w, h, seed)
    board(a, 10, 10, w - 10, h - 10, WOOD_DARK, n=3, vertical=True, corner=6)
    for x, y in ((60, 80), (w - 60, 80), (70, h - 70), (w - 70, h - 70)):
        a.shape(rect(x - 22, y - 9, x + 22, y + 9), RUST, outline=DETAIL, corner=3, depth=2, mottle=0)
    with a.clip(to_path(rect(10, 10, w - 10, h - 10))):
        for _ in range(3):
            a.shape(blob(a.rng.uniform(60, 200), a.rng.uniform(120, 360), a.rng.uniform(14, 26), a.rng, 9, 0.3), BLOOD, outline=0, smooth=True, depth=1, shade_k=0, light_k=0.2, ao=0, mottle=0.1)
    return a.image()


# -- traps -----------------------------------------------------------------------------------------


def spike_trap(seed=821):
    s = 256
    a = Art(s, s, seed)
    a.shape(rect(8, 8, s - 8, s - 8), DARK_STONE, corner=4, depth=6)
    a.shape(rect(22, 22, s - 22, s - 22), rgb("#3a3430"), outline=DETAIL * 1.2, corner=3, depth=8, shade_k=0, light_k=0, ao=0.5)
    for i in range(5):
        for j in range(5):
            x, y = 44 + i * 42, 44 + j * 42
            pts = [(x + 11 * math.cos(t), y + 11 * math.sin(t)) for t in [k * 2 * math.pi / 4 + math.pi / 4 for k in range(4)]]
            for k in range(4):
                face = [pts[k], pts[(k + 1) % 4], (x, y)]
                lit = math.cos((k + 0.5) * math.pi / 2 + math.pi * 0.75 + math.pi / 4)
                a.shape(face, tint(IRON, 0.3 * lit) if lit > 0 else shade(IRON, -0.3 * lit), outline=0, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
            a.ink(pts, FINE * 1.3, closed=True, wob=0)
    return a.image()


def pit_trap(seed=822):
    s = 256
    a = Art(s, s, seed)
    m = s / 2
    a.shape(rect(10, 10, s - 10, s - 10), DARK_STONE, corner=4, depth=6)
    a.shape(rect(26, 26, s - 26, s - 26), rgb("#1e1a18"), outline=DETAIL * 1.3, corner=4, depth=20, shade_k=0, light_k=0, ao=0.7)
    # Broken trapdoor boards hanging in, spikes at the bottom.
    for x0 in (30, s - 70):
        a.shape([(x0, 28), (x0 + 40, 28), (x0 + 34, 90), (x0 + 6, 86)], WOOD_DARK, outline=DETAIL * 1.1, corner=2, depth=3)
    for _ in range(9):
        x, y = a.rng.uniform(60, s - 60), a.rng.uniform(110, s - 50)
        a.shape([(x, y - 9), (x + 6, y + 5), (x - 6, y + 5)], rgb("#6a6c72"), outline=FINE, corner=1, depth=1, mottle=0)
    return a.image()


def pressure_plate(seed=823):
    s = 160
    a = Art(s, s, seed)
    a.shape(rect(12, 12, s - 12, s - 12), DARK_STONE, outline=DETAIL * 1.3, corner=4, depth=4, shade_k=0, light_k=0, ao=0.4)
    stone_block(a, rect(22, 22, s - 22, s - 22), GREY, outline=DETAIL * 1.2, corner=3, cracks=0, light_k=0.4)
    a.ink(rect(40, 40, s - 40, s - 40), FINE * 1.2, closed=True, color=shade(GREY, 0.45), alpha=0.7)
    return a.image()


def bear_trap(seed=824):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    a.ink(ellipse(m, m, 80, 80, 72), DETAIL * 3.4, closed=True, color=INK)
    a.ink(ellipse(m, m, 80, 80, 72), DETAIL * 2, closed=True, color=DARK_IRON)
    for k in range(18):
        t = 2 * math.pi * k / 18
        x0, y0 = m + 80 * math.cos(t), m + 80 * math.sin(t)
        x1, y1 = m + 60 * math.cos(t + 0.08), m + 60 * math.sin(t + 0.08)
        a.shape([(x0 - 6 * math.sin(t), y0 + 6 * math.cos(t)), (x1, y1), (x0 + 6 * math.sin(t), y0 - 6 * math.cos(t))], rgb("#9aa0aa"), outline=FINE * 1.2, corner=0, depth=1, mottle=0)
    a.shape(ellipse(m, m, 22, 22, 28), RUST, outline=DETAIL * 1.3, depth=3, light_k=0.3, mottle=0)
    chain(a, [(m + 22, m), (m + 70, m + 40), (m + 96, m + 90)], 12)
    return a.image()


def arrow_trap(seed=825):
    w, h = 200, 60
    a = Art(w, h, seed)
    a.shape(rect(6, 6, w - 6, 40), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    for x in (60, 100, 140):
        a.shape(ellipse(x, 30, 9, 6, 16), rgb("#1e1a18"), outline=FINE * 1.2, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def floor_grate(seed=826):
    s = 200
    a = Art(s, s, seed)
    a.shape(rect(14, 14, s - 14, s - 14), rgb("#1e1a18"), outline=DETAIL * 1.3, corner=4, depth=10, shade_k=0, light_k=0, ao=0.6)
    for k in range(1, 7):
        x = 14 + k * (s - 28) / 7
        a.ink([(x, 14), (x, s - 14)], DETAIL * 2.6, color=INK, taper=False)
        a.ink([(x, 14), (x, s - 14)], DETAIL * 1.4, color=IRON, taper=False)
    a.ink(rect(14, 14, s - 14, s - 14), DETAIL * 2.4, closed=True, color=IRON)
    return a.image()


def trapdoor(seed=827):
    s = 230
    a = Art(s, s, seed)
    board(a, 10, 10, s - 10, s - 10, WOOD_DARK, n=4, vertical=True, corner=4)
    for y in (40, s - 40):
        a.shape(rect(10, y - 10, s - 10, y + 10), IRON, outline=DETAIL, corner=2, depth=2, mottle=0)
    a.ink(ellipse(s / 2, s / 2, 16, 16, 24), DETAIL * 1.8, closed=True, color=IRON)
    return a.image()


# -- remains & mess ---------------------------------------------------------------------------------


def skeleton(seed=831):
    w, h = 200, 420
    a = Art(w, h, seed)
    cx = w / 2

    def bone_line(pts, wd=9):
        a.ink(pts, wd + 6, color=INK, taper=False)
        a.ink(pts, wd, color=BONE, taper=False)

    # Spine, ribs, pelvis, limbs, then the skull.
    bone_line([(cx, 90), (cx + 2, 250)], 8)
    for k in range(6):
        y = 120 + k * 16
        for side in (-1, 1):
            bone_line(chaikin([(cx, y), (cx + side * 34, y + 6), (cx + side * 40, y + 20)], False, 1), 6)
    a.shape(chaikin([(cx - 40, 250), (cx + 40, 250), (cx + 30, 290), (cx - 30, 290)], True, 2), BONE, outline=DETAIL * 1.2, corner=0, depth=3, light_k=0.3)
    for side in (-1, 1):
        bone_line([(cx + side * 40, 110), (cx + side * 66, 200), (cx + side * 74, 280)])
        bone_line([(cx + side * 22, 290), (cx + side * 30, 360), (cx + side * 34, 410)], 10)
        for k in range(3):
            bone_line([(cx + side * 74, 280), (cx + side * (68 + k * 6), 300)], 4)
    skull_at(a, cx, 60, 1.25)
    return a.image()


def skull_pile(seed=832):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    spots = [(m + a.rng.uniform(-70, 70), m + a.rng.uniform(-60, 60)) for _ in range(8)]
    for x, y in sorted(spots, key=lambda p: p[1]):
        skull_at(a, x, y, a.rng.uniform(0.85, 1.1))
    return a.image()


def blood_stain(seed=833):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m, 66, a.rng, 14, 0.3), BLOOD, outline=0, smooth=True, depth=2, shade_k=0, light_k=0.25, ao=0, mottle=0.12)
    for _ in range(12):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(70, 100)
        dot(a, m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(3, 7), BLOOD, 0.95)
    return a.image(grain=0.02)


def slime_puddle(seed=834):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 90, SLIME, 0.3)
    a.shape(blob(m, m, 84, a.rng, 12, 0.25), SLIME, outline=DETAIL, smooth=True, depth=6, shade_k=0.2, light_k=0.5, ao=0, mottle=0.1)
    for _ in range(6):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, 50)
        a.shape(ellipse(m + d * math.cos(t), m + d * math.sin(t), 8, 8, 16), tint(SLIME, 0.35), outline=FINE, depth=1, shade_k=0.2, light_k=0.5, ao=0, mottle=0)
    return a.image()


def cobweb(seed=835):
    s = 260
    a = Art(s, s, seed)
    # Anchored in the top-left corner, fanning out.
    col = rgb("#f2efe6")
    spokes = [math.radians(d) for d in (2, 22, 45, 68, 88)]
    for t in spokes:
        a.ink([(4, 4), (4 + 240 * math.cos(t), 4 + 240 * math.sin(t))], FINE * 1.2, color=col, alpha=0.9, wob=0.3)
    for r in (40, 80, 120, 160, 200):
        pts = []
        for t in spokes:
            pts.append((4 + r * math.cos(t), 4 + r * math.sin(t)))
        for p0, p1 in zip(pts, pts[1:]):
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            a.ink(chaikin([p0, (mx - (mx - 4) * 0.08, my - (my - 4) * 0.08), p1], False, 2), FINE, color=col, alpha=0.85, wob=0.2)
    return a.image(grain=0)


def broken_barrel(seed=836):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    for k in range(9):
        t = a.rng.uniform(0, 6.28)
        d = a.rng.uniform(20, 80)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        L = a.rng.uniform(60, 90)
        ang = a.rng.uniform(0, 3.14)
        pts = [(x - math.cos(ang) * L / 2 - math.sin(ang) * 9, y - math.sin(ang) * L / 2 + math.cos(ang) * 9), (x + math.cos(ang) * L / 2 - math.sin(ang) * 9, y + math.sin(ang) * L / 2 + math.cos(ang) * 9), (x + math.cos(ang) * L / 2 + math.sin(ang) * 9, y + math.sin(ang) * L / 2 - math.cos(ang) * 9), (x - math.cos(ang) * L / 2 + math.sin(ang) * 9, y - math.sin(ang) * L / 2 - math.cos(ang) * 9)]
        soft_shadow(a, pts, dx=3, dy=4)
        a.shape(pts, vary(a.rng, WOOD, 0.06), outline=DETAIL * 1.2, corner=4, depth=3)
    a.ink(chaikin([(m - 70, m + 30), (m - 20, m + 70), (m + 50, m + 60)], False, 2), DETAIL * 2.4, color=INK)
    a.ink(chaikin([(m - 70, m + 30), (m - 20, m + 70), (m + 50, m + 60)], False, 2), DETAIL * 1.4, color=IRON)
    return a.image()


DUNGEON = {
    "Wall Shackles": wall_shackles,
    "Floor Chains": floor_chains,
    "Ball and Chain": ball_and_chain,
    "Manacles": manacles,
    "Hanging Cage": hanging_cage,
    "Prison Cot": prison_cot,
    "Straw Pile": straw_pile,
    "Prisoner Bucket": prisoner_bucket,
    "Rack": rack,
    "Stocks": stocks,
    "Execution Block": execution_block,
    "Brazier with Irons": brazier_irons,
    "Torture Table": torture_table,
    "Spike Trap": spike_trap,
    "Pit Trap": pit_trap,
    "Pressure Plate": pressure_plate,
    "Bear Trap": bear_trap,
    "Arrow Trap": arrow_trap,
    "Floor Grate": floor_grate,
    "Trapdoor": trapdoor,
    "Skeleton": skeleton,
    "Skull Pile": skull_pile,
    "Blood Stain": blood_stain,
    "Slime Puddle": slime_puddle,
    "Cobweb": cobweb,
    "Broken Barrel": broken_barrel,
}
