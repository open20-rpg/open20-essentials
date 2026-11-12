"""Stone things (batch 3): pillars, statues, altars, graves, standing stones,
rubble and other masonry. Top-down with the faint perspective the other
objects use: what stands tall shows its top, lighter, over its base."""

import math

import skia

from kit import BRASS, RED, STONE, WOOD, WOOD_DARK, cushion, dot, scallop, soft_shadow
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, vary

GREY = STONE
DARK_STONE = rgb("#7f7a72")
LIGHT_STONE = rgb("#c4beb3")
MARBLE = rgb("#e4dfd4")
MOSS = rgb("#6f9443")


def chips(a, path, color, n=14):
    """Speckles and a few chips in stone."""
    b = path.getBounds()
    for _ in range(n):
        x, y = a.rng.uniform(b.left(), b.right()), a.rng.uniform(b.top(), b.bottom())
        if path.contains(x, y):
            dot(a, x, y, a.rng.uniform(1.0, 2.0), shade(color, 0.45), 0.55)


def crack(a, x, y, ang, L, width=FINE * 1.2):
    pts = [(x, y)]
    for _ in range(4):
        ang += a.rng.uniform(-0.6, 0.6)
        x += math.cos(ang) * L / 4
        y += math.sin(ang) * L / 4
        pts.append((x, y))
    a.ink(pts, width, alpha=0.8, wob=0.3)


def stone_block(a, pts, color=GREY, outline=OUTLINE, depth=None, cracks=1, **kw):
    def detail(art, path):
        chips(art, path, color)
        b = path.getBounds()
        for _ in range(cracks):
            if art.rng.random() < 0.7:
                crack(art, art.rng.uniform(b.left() + 10, b.right() - 10), art.rng.uniform(b.top() + 10, b.bottom() - 10), art.rng.uniform(0, 6.28), min(b.width(), b.height()) * 0.4)

    return a.shape(pts, color, outline=outline, depth=depth, detail=detail, **kw)


def moss(a, path, amount=6, r=(10, 20)):
    """Soft moss patches on a stone (inside its clip)."""
    b = path.getBounds()
    with a.clip(path):
        for _ in range(amount):
            x, y = a.rng.uniform(b.left(), b.right()), a.rng.uniform(b.top(), b.bottom())
            a.shape(blob(x, y, a.rng.uniform(*r), a.rng, 9, 0.3), MOSS, outline=0, smooth=True, depth=2, shade_k=0.3, light_k=0.3, ao=0, mottle=0.1)


# -- columns -----------------------------------------------------------------------------------


def round_pillar(seed=201):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    # Square plinth, the round shaft's top (fluted), its capital ring.
    stone_block(a, rect(10, 10, s - 10, s - 10), DARK_STONE, corner=8, cracks=0)
    a.shape(ellipse(m, m, 86, 86, 96), GREY, depth=10)

    def flutes(art, path):
        for i in range(20):
            t = 2 * math.pi * i / 20
            art.ink([(m + 58 * math.cos(t), m + 58 * math.sin(t)), (m + 80 * math.cos(t), m + 80 * math.sin(t))], FINE * 1.2, color=shade(LIGHT_STONE, 0.4), alpha=0.8, taper=False)

    a.shape(ellipse(m, m, 80, 80, 96), LIGHT_STONE, outline=DETAIL * 1.2, depth=8, light_k=0.45, detail=flutes)
    a.ink(ellipse(m, m, 56, 56, 80), FINE * 1.4, closed=True, color=shade(LIGHT_STONE, 0.4), alpha=0.8)
    return a.image()


def square_pillar(seed=202):
    s = 200
    a = Art(s, s, seed)
    stone_block(a, rect(8, 8, s - 8, s - 8), DARK_STONE, corner=6, cracks=0)
    stone_block(a, rect(26, 26, s - 26, s - 26), LIGHT_STONE, outline=DETAIL * 1.3, corner=4, light_k=0.45)
    a.ink(rect(44, 44, s - 44, s - 44), FINE * 1.3, closed=True, color=shade(LIGHT_STONE, 0.4), alpha=0.8)
    return a.image()


def broken_pillar(seed=203):
    w, h = 420, 230
    a = Art(w, h, seed)
    m = 115
    stone_block(a, rect(10, 10, 220, 220), DARK_STONE, corner=8, cracks=1)
    # The stump of the shaft with a jagged break, and a fallen drum beside it.
    stump = [(m + 70 * math.cos(t) * (1 + a.rng.uniform(-0.08, 0.04)), m + 70 * math.sin(t) * (1 + a.rng.uniform(-0.08, 0.04))) for t in [2 * math.pi * i / 22 for i in range(22)]]
    stone_block(a, stump, LIGHT_STONE, outline=DETAIL * 1.3, corner=0, light_k=0.4, cracks=2)
    a.ink([(m - 50, m - 10), (m - 10, m + 6), (m + 30, m - 12), (m + 56, m + 4)], DETAIL, alpha=0.8)
    drum = rect(240, 70, 410, 170)

    def flutes(art, path):
        for y in range(84, 160, 14):
            art.ink([(250, y), (400, y)], FINE * 1.1, color=shade(GREY, 0.45), alpha=0.75, taper=False)

    a.shape(drum, GREY, corner=46, depth=10, detail=flutes)
    a.shape(ellipse(392, 120, 16, 48, 40), LIGHT_STONE, outline=DETAIL * 1.1, depth=3, mottle=0)
    return a.image()


def rubble(seed=204):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    pieces = []
    for _ in range(14):
        ang, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, 100)
        pieces.append((m + d * math.cos(ang), m + d * math.sin(ang), a.rng.uniform(14, 34)))
    for x, y, r in sorted(pieces, key=lambda p: p[1]):
        pts = [(x + r * math.cos(t) * a.rng.uniform(0.7, 1.1), y + r * math.sin(t) * a.rng.uniform(0.7, 1.1)) for t in [2 * math.pi * i / 6 + a.rng.uniform(-0.2, 0.2) for i in range(6)]]
        soft_shadow(a, pts, dx=4, dy=5, alpha=0.3, blur=4)
        stone_block(a, pts, vary(a.rng, GREY, 0.08), outline=DETAIL * 1.3, corner=4, cracks=0)
    for _ in range(30):
        ang, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, 130)
        dot(a, m + d * math.cos(ang), m + d * math.sin(ang), a.rng.uniform(2, 4), shade(GREY, 0.3), 0.9)
    return a.image()


# -- statues, altars, graves -------------------------------------------------------------------


def statue(seed=205):
    """A robed figure with a sword on a plinth, seen from above: the robe's
    hem flaring out under broad shoulders, the head, and arms running down
    the sides and forward to hands resting on the sword's pommel."""
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, rect(14, 14, s - 14, s - 14), DARK_STONE, corner=8, cracks=1)

    def folds(art, path):
        for dx in (-60, -30, 30, 60):
            art.ink([(m + dx * 0.8, m + 30), (m + dx, m + 74)], FINE * 1.3, color=shade(MARBLE, 0.4), alpha=0.8)

    a.shape(ellipse(m, m + 22, 92, 62, 64), shade(MARBLE, 0.06), depth=10, light_k=0.3, detail=folds)
    # Sword: blade pointing toward the viewer, crossguard, grip under the hands.
    a.shape(rect(m - 7, m + 52, m + 7, m + 116), rgb("#b9bec6"), outline=DETAIL, corner=3, depth=3, mottle=0)
    a.shape(rect(m - 30, m + 46, m + 30, m + 56), rgb("#b9bec6"), outline=DETAIL, corner=3, depth=2, mottle=0)
    a.shape(ellipse(m, m - 6, 82, 42, 56), MARBLE, outline=OUTLINE, depth=10, light_k=0.45)
    for side in (-1, 1):
        arm = chaikin([(m + side * 80, m - 14), (m + side * 88, m + 16), (m + side * 56, m + 46), (m + side * 18, m + 52), (m + side * 14, m + 34), (m + side * 46, m + 26), (m + side * 60, m - 4)], True, 2)
        a.shape(arm, tint(MARBLE, 0.1), outline=DETAIL * 1.3, corner=0, depth=6, light_k=0.4)
    a.shape(ellipse(m, m + 42, 18, 13, 28), tint(MARBLE, 0.14), outline=DETAIL * 1.2, depth=4, light_k=0.4)
    a.shape(ellipse(m, m - 14, 30, 30, 40), tint(MARBLE, 0.16), outline=DETAIL * 1.4, depth=6, light_k=0.5)
    a.ink(chaikin([(m - 18, m - 30), (m, m - 38), (m + 18, m - 30)], False, 2), FINE * 1.2, color=shade(MARBLE, 0.4), alpha=0.7)
    return a.image()

def altar(seed=206):
    w, h = 400, 240
    a = Art(w, h, seed)
    stone_block(a, rect(10, 10, w - 10, h - 10), DARK_STONE, corner=8, cracks=1)
    top = stone_block(a, rect(30, 30, w - 30, h - 30), LIGHT_STONE, outline=DETAIL * 1.3, corner=6, light_k=0.4)
    # An altar cloth (recolorable) and candles.
    a.shape(rect(w / 2 - 70, 26, w / 2 + 70, h - 26), RED, outline=DETAIL * 1.2, corner=3, depth=6, mottle=0.03)
    a.ink([(w / 2 - 60, 40), (w / 2 + 60, 40)], FINE * 1.2, color=tint(RED, 0.5), taper=False)
    a.ink([(w / 2 - 60, h - 40), (w / 2 + 60, h - 40)], FINE * 1.2, color=tint(RED, 0.5), taper=False)
    for x, y in ((70, 70), (70, h - 70), (w - 70, 70), (w - 70, h - 70)):
        glow = skia.Path()
        glow.addCircle(x, y, 24)
        a.fill_path(glow, rgb("#ffd27a"), 0.35, blur=8)
        a.shape(ellipse(x, y, 14, 14, 24), rgb("#f1e6c8"), outline=DETAIL, depth=3, mottle=0)
        dot(a, x, y, 4, rgb("#f6b444"))
    a.shape(ellipse(w / 2, h / 2, 26, 26, 32), BRASS, outline=DETAIL * 1.2, depth=4, light_k=0.5)
    return a.image()


def sacrificial_altar(seed=207):
    w, h = 360, 260
    a = Art(w, h, seed)
    slab = chaikin([(20, 30), (w - 30, 16), (w - 14, h - 40), (34, h - 20)], True, 1)
    p = stone_block(a, slab, DARK_STONE, corner=10, cracks=2)
    with a.clip(p):
        for _ in range(3):
            a.shape(blob(a.rng.uniform(100, 260), a.rng.uniform(80, 180), a.rng.uniform(16, 30), a.rng, 9, 0.3), rgb("#6e2a26"), outline=0, smooth=True, depth=2, shade_k=0.3, light_k=0, ao=0, mottle=0.1)
    for x, y in ((70, 70), (w - 70, h - 70)):
        a.ink([(x - 30, y), (x + 30, y)], DETAIL * 1.3, color=rgb("#4a4648"))
        a.ink([(x, y - 30), (x, y + 30)], DETAIL * 1.3, color=rgb("#4a4648"))
    return a.image()


def sarcophagus(seed=208):
    w, h = 300, 520
    a = Art(w, h, seed)
    stone_block(a, rect(10, 10, w - 10, h - 10), DARK_STONE, corner=10, cracks=1)

    def carving(art, path):
        cx = w / 2
        art.ink(chaikin([(cx - 50, 90), (cx, 50), (cx + 50, 90), (cx + 70, 200), (cx + 50, h - 70), (cx - 50, h - 70), (cx - 70, 200)], True, 2), DETAIL, color=shade(LIGHT_STONE, 0.45), alpha=0.9)
        art.ink(ellipse(cx, 110, 30, 34, 40), DETAIL, closed=True, color=shade(LIGHT_STONE, 0.45), alpha=0.9)
        art.ink([(cx, 160), (cx, h - 110)], DETAIL, color=shade(LIGHT_STONE, 0.45), alpha=0.9)
        art.ink([(cx - 40, 220), (cx + 40, 220)], DETAIL, color=shade(LIGHT_STONE, 0.45), alpha=0.9)

    stone_block(a, rect(28, 28, w - 28, h - 28), LIGHT_STONE, outline=DETAIL * 1.3, corner=14, light_k=0.4, cracks=0)
    with a.clip(skia.Path()):
        pass
    a.shape(rect(28, 28, w - 28, h - 28), LIGHT_STONE, outline=0, corner=14, depth=1, shade_k=0, light_k=0, ao=0, mottle=0, detail=carving)
    return a.image()


def tombstone(seed=209):
    """A rounded headstone from above (its top edge), with a grave mound."""
    w, h = 200, 330
    a = Art(w, h, seed)
    dirt = rgb("#8a6a4a")
    mound = a.shape(chaikin(rect(30, 90, w - 30, h - 14), True, 3), dirt, depth=10)
    with a.clip(mound):
        for _ in range(30):
            dot(a, a.rng.uniform(30, w - 30), a.rng.uniform(90, h - 14), a.rng.uniform(1.5, 3), shade(dirt, 0.4), 0.8)
    stone_block(a, chaikin([(24, 96), (24, 50), (w / 2, 18), (w - 24, 50), (w - 24, 96)], True, 2), GREY, corner=0, cracks=1, light_k=0.45)
    return a.image()


def cross_grave(seed=210):
    w, h = 220, 330
    a = Art(w, h, seed)
    dirt = rgb("#8a6a4a")
    a.shape(chaikin(rect(36, 100, w - 36, h - 14), True, 3), dirt, depth=10)
    cx = w / 2
    stone_block(a, [(cx - 18, 14), (cx + 18, 14), (cx + 18, 54), (cx + 70, 54), (cx + 70, 86), (cx + 18, 86), (cx + 18, 150), (cx - 18, 150), (cx - 18, 86), (cx - 70, 86), (cx - 70, 54), (cx - 18, 54)], GREY, corner=4, cracks=1, light_k=0.45)
    return a.image()


def broken_tombstone(seed=211):
    w, h = 220, 200
    a = Art(w, h, seed)
    stone_block(a, [(30, 120), (30, 70), (80, 50), (110, 74), (140, 52), (190, 70), (190, 120)], GREY, corner=6, cracks=1, light_k=0.4)
    piece = [(60, 140), (130, 150), (126, 186), (54, 178)]
    soft_shadow(a, piece, dx=4, dy=5)
    stone_block(a, piece, GREY, outline=DETAIL * 1.3, corner=6, cracks=0)
    return a.image()


def obelisk(seed=212):
    s = 230
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, rect(10, 10, s - 10, s - 10), DARK_STONE, corner=6, cracks=0)
    # The obelisk's four faces meet at its point (center): lit faces lighter.
    c = [(36, 36), (s - 36, 36), (s - 36, s - 36), (36, s - 36)]
    for k, tone in enumerate((0.25, 0.0, -0.25, 0.05)):
        face = [c[k], c[(k + 1) % 4], (m, m)]
        col = tint(GREY, tone) if tone > 0 else shade(GREY, -tone)
        a.shape(face, col, outline=DETAIL, corner=0, depth=2, shade_k=0, light_k=0, ao=0, mottle=0.04)
    a.ink(c, OUTLINE * 0.8, closed=True, wob=0.3)
    return a.image()


def rune_stone(seed=213):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    p = stone_block(a, blob(m, m, 84, a.rng, 9, 0.12), GREY, smooth=True, cracks=0, light_k=0.4)
    glow = rgb("#7fd3e0")
    with a.clip(p):
        for k in range(5):
            x, y = m - 50 + k * 25, m + a.rng.uniform(-30, 30)
            pts = [(x, y - 16), (x + a.rng.uniform(-8, 8), y), (x, y + 16)]
            a.ink(pts, DETAIL * 2.6, color=glow, alpha=0.35)
            a.ink(pts, DETAIL, color=tint(glow, 0.4))
            a.ink([(x, y - 4), (x + 9, y - 10)], DETAIL * 0.8, color=tint(glow, 0.4))
    return a.image()


def standing_stone(seed=214):
    w, h = 200, 240
    a = Art(w, h, seed)
    p = stone_block(a, chaikin([(40, 210), (24, 120), (50, 30), (120, 14), (172, 60), (180, 170), (150, 220)], True, 2), GREY, corner=0, cracks=1, light_k=0.4)
    moss(a, p, 4)
    return a.image()


def stone_circle_stone(seed=215):
    w, h = 170, 150
    a = Art(w, h, seed)
    p = stone_block(a, chaikin([(20, 110), (16, 50), (60, 18), (130, 24), (156, 70), (140, 128), (70, 136)], True, 2), DARK_STONE, corner=0, cracks=1)
    moss(a, p, 3, (8, 16))
    return a.image()


def boulder(seed=216):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    p = stone_block(a, blob(m, m, 120, a.rng, 10, 0.16), GREY, smooth=True, cracks=1, light_k=0.45, depth=24)
    with a.clip(p):
        top = blob(m - 25, m - 25, 60, a.rng, 7, 0.2)
        a.shape(chaikin(top, True, 1), tint(GREY, 0.18), outline=DETAIL, corner=0, depth=6, shade_k=0.2, light_k=0.3, ao=0)
    return a.image()


def mossy_boulder(seed=217):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    p = stone_block(a, blob(m, m, 116, a.rng, 10, 0.14), DARK_STONE, smooth=True, cracks=1, depth=24)
    moss(a, p, 9, (18, 34))
    return a.image()


def stone_pile(seed=218):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    stones = [(m + a.rng.uniform(-60, 60), m + a.rng.uniform(-50, 50), a.rng.uniform(22, 36)) for _ in range(7)]
    for x, y, r in sorted(stones, key=lambda p: p[1]):
        pts = blob(x, y, r, a.rng, 8, 0.15)
        soft_shadow(a, pts, dx=4, dy=5)
        stone_block(a, pts, vary(a.rng, GREY, 0.08), outline=DETAIL * 1.4, smooth=True, cracks=0)
    return a.image()


def stone_bench(seed=219):
    w, h = 400, 140
    a = Art(w, h, seed)
    for x in (40, w - 40):
        stone_block(a, rect(x - 26, 16, x + 26, h - 16), DARK_STONE, outline=DETAIL * 1.3, corner=6, cracks=0)
    stone_block(a, rect(14, 28, w - 14, h - 28), LIGHT_STONE, corner=8, cracks=2, light_k=0.4)
    return a.image()


def stone_table(seed=220):
    s = 280
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, ellipse(m, m, m - 12, m - 12, 80), LIGHT_STONE, cracks=2, light_k=0.4)
    a.ink(ellipse(m, m, m - 34, m - 34, 80), FINE * 1.3, closed=True, color=shade(LIGHT_STONE, 0.4), alpha=0.8)
    return a.image()


def fountain(seed=221):
    s = 420
    a = Art(s, s, seed)
    m = s / 2
    # Octagonal basin, water, a central pedestal with a bowl spilling over.
    octa = [(m + 196 * math.cos(t), m + 196 * math.sin(t)) for t in [math.pi / 8 + math.pi / 4 * i for i in range(8)]]
    stone_block(a, octa, GREY, corner=10, cracks=1, depth=14)
    water = rgb("#6aa0b6")

    def ripples(art, path):
        for r in (90, 130, 165):
            for k in range(4):
                t0 = art.rng.uniform(0, 6.28)
                art.ink([(m + r * math.cos(t0 + j * 0.06), m + r * math.sin(t0 + j * 0.06)) for j in range(10)], FINE * 1.3, color=rgb("#e4f2f6"), alpha=0.85)

    inner = [(m + 166 * math.cos(t), m + 166 * math.sin(t)) for t in [math.pi / 8 + math.pi / 4 * i for i in range(8)]]
    a.shape(inner, water, outline=DETAIL * 1.2, corner=8, depth=20, shade_k=0, light_k=0, ao=0.6, detail=ripples)
    stone_block(a, ellipse(m, m, 62, 62, 64), LIGHT_STONE, outline=DETAIL * 1.4, cracks=0, light_k=0.45)
    a.shape(ellipse(m, m, 44, 44, 56), water, outline=DETAIL, depth=8, shade_k=0, light_k=0, ao=0.5)
    a.shape(ellipse(m, m, 14, 14, 24), LIGHT_STONE, outline=DETAIL, depth=3, mottle=0)
    return a.image()


def stone_brazier(seed=222):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    stone_block(a, ellipse(m, m, 84, 84, 64), GREY, cracks=1)
    a.shape(ellipse(m, m, 62, 62, 64), rgb("#3c322d"), outline=DETAIL * 1.3, depth=8, shade_k=0, light_k=0, ao=0.6)
    glow = skia.Path()
    glow.addCircle(m, m, 60)
    a.fill_path(glow, rgb("#ff9a3c"), 0.45, blur=18)
    for r, col in ((40, rgb("#e9773a")), (26, rgb("#f4b544")), (12, rgb("#fde8a6"))):
        a.shape(scallop(m, m, r, a.rng, 7, 0.22), col, outline=DETAIL if r > 20 else 0, depth=3, shade_k=0.2, light_k=0, ao=0, mottle=0)
    return a.image()


def throne_dais(seed=223):
    w, h = 440, 400
    a = Art(w, h, seed)
    stone_block(a, rect(8, 8, w - 8, h - 8), DARK_STONE, corner=10, cracks=2)
    stone_block(a, rect(40, 30, w - 40, h - 60), GREY, outline=DETAIL * 1.4, corner=8, cracks=1, light_k=0.4)
    # Steps toward the room (bottom).
    for k, y in enumerate((h - 60, h - 36)):
        a.shape(rect(60 + k * 20, y, w - 60 - k * 20, y + 24), tint(GREY, 0.05 * (1 - k)), outline=DETAIL * 1.2, corner=4, depth=4)
    a.ink(rect(64, 54, w - 64, h - 84), FINE * 1.3, closed=True, color=shade(GREY, 0.45), alpha=0.8)
    return a.image()


def stone_lion(seed=224):
    """A stone lion lying like a sphinx, seen from above, as ONE silhouette
    (mane, forelegs, body and haunches merged) with its details drawn as pen
    lines inside: the mane's edge, the face, spine, haunch curves, toes."""
    from pen import to_path

    w, h = 260, 340
    a = Art(w, h, seed)
    cx = w / 2
    stone_block(a, rect(12, 12, w - 12, h - 12), DARK_STONE, corner=8, cracks=0)
    stone = LIGHT_STONE
    # The tail, curled along the right flank (under the body).
    tail = chaikin([(cx + 20, h - 40), (cx + 80, h - 42), (cx + 96, h - 90), (cx + 90, h - 130)], False, 2)
    a.ink(tail, DETAIL * 3.4, color=INK, taper=False)
    a.ink(tail, DETAIL * 2.0, color=stone, taper=False)
    a.shape(scallop(cx + 90, h - 136, 11, a.rng, 6, 0.2), GREY, outline=DETAIL, corner=0, depth=2, mottle=0)
    parts = [
        chaikin(rect(cx - 62, 30, cx - 32, 170), True, 3),  # forelegs
        chaikin(rect(cx + 32, 30, cx + 62, 170), True, 3),
        ellipse(cx - 50, 34, 22, 16, 28),  # paws
        ellipse(cx + 50, 34, 22, 16, 28),
        chaikin([(cx - 64, 170), (cx - 60, 214), (cx - 74, h - 92), (cx - 76, h - 58), (cx - 46, h - 32), (cx + 46, h - 32), (cx + 76, h - 58), (cx + 74, h - 92), (cx + 60, 214), (cx + 64, 170)], True, 3),  # body: waist, then haunches

    ]
    body = to_path(parts[0])
    for q in parts[1:]:
        body = skia.Op(body, to_path(q), skia.kUnion_PathOp)
    a.fill_path(body, stone)
    line = shade(stone, 0.5)
    with a.clip(body):
        glow = skia.Path()
        glow.addCircle(cx - 40, 130, 120)
        a.fill_path(glow, tint(stone, 0.3), 0.5, blur=40)
        a.stroke_path(body, shade(stone, 0.4), 10, 0.35, blur=5)
        # Paws: toe lines at the front of each foreleg.
        for side in (-1, 1):
            x = cx + side * 50
            for k in (-1, 0, 1):
                a.ink([(x + k * 9, 20), (x + k * 9, 32)], FINE * 1.3, color=line, alpha=0.85)
        # Spine and the haunches' curves.
        a.ink([(cx, 230), (cx + 2, h - 90), (cx, h - 50)], FINE * 1.4, color=line, alpha=0.75)
        for side in (-1, 1):
            # Hind legs folded along the flanks.
            a.ink(chaikin([(cx + side * 30, h - 120), (cx + side * 62, h - 112), (cx + side * 66, h - 56)], False, 2), FINE * 1.3, color=line, alpha=0.7)
    a.stroke_path(body, INK, OUTLINE * 0.9)
    # The mane on top: its own outlined shape, strokes radiating; then the head.
    mane = scallop(cx, 150, 78, a.rng, 15, 0.1)

    def mane_strokes(art, path):
        for i in range(26):
            t = 2 * math.pi * i / 26 + art.rng.uniform(-0.05, 0.05)
            art.ink([(cx + 46 * math.cos(t), 150 + 46 * math.sin(t)), (cx + 72 * math.cos(t), 150 + 72 * math.sin(t))], FINE * 1.2, color=line, alpha=0.75)

    a.shape(mane, shade(stone, 0.12), outline=OUTLINE * 0.85, corner=0, depth=10, light_k=0.35, detail=mane_strokes)
    if True:
        # Head (crown seen from above), ears, muzzle toward the front.
        head = chaikin([(cx - 36, 160), (cx - 32, 118), (cx - 16, 86), (cx + 16, 86), (cx + 32, 118), (cx + 36, 160), (cx, 176)], True, 2)
        a.shape(head, stone, outline=DETAIL * 1.2, corner=0, depth=5, light_k=0.4, mottle=0.04)
        for side in (-1, 1):
            a.shape(ellipse(cx + side * 32, 150, 8, 7, 16), shade(stone, 0.2), outline=DETAIL * 0.9, depth=2, mottle=0)
        a.shape(ellipse(cx, 88, 11, 7, 20), shade(stone, 0.25), outline=FINE * 1.2, depth=1, mottle=0)
        a.ink([(cx - 12, 116), (cx, 124), (cx + 12, 116)], FINE * 1.2, color=line, alpha=0.8)
    return a.image()

def well_stone(seed=225):
    from objects import well

    return well(seed)


STONE_OBJECTS = {
    "Round Pillar": round_pillar,
    "Square Pillar": square_pillar,
    "Broken Pillar": broken_pillar,
    "Rubble": rubble,
    "Statue": statue,
    "Altar": altar,
    "Sacrificial Altar": sacrificial_altar,
    "Sarcophagus": sarcophagus,
    "Tombstone": tombstone,
    "Cross Grave": cross_grave,
    "Broken Tombstone": broken_tombstone,
    "Obelisk": obelisk,
    "Rune Stone": rune_stone,
    "Standing Stone": standing_stone,
    "Small Standing Stone": stone_circle_stone,
    "Boulder": boulder,
    "Mossy Boulder": mossy_boulder,
    "Stone Pile": stone_pile,
    "Stone Bench": stone_bench,
    "Stone Table": stone_table,
    "Fountain": fountain,
    "Stone Brazier": stone_brazier,
    "Throne Dais": throne_dais,
    "Stone Lion": stone_lion,
}

STONE_COLORABLE = {"Altar"}
