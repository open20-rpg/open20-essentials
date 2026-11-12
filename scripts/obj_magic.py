"""Magic and alchemy (batch 7). Top-down, same pen style."""

import math

import skia

from kit import BRASS, IRON, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, dot, scallop, soft_shadow
from obj_nature import leaf
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

GLASS = rgb("#bcd6dc")
PARCH = rgb("#e9dcb8")
BONE = rgb("#e6dcc4")
WAX = rgb("#f1e6c8")
GOLD = rgb("#d6ae4c")
CHALK = rgb("#f2efe6")
ARCANE = rgb("#8a6ad8")
TEAL = rgb("#4fc2c0")
POTIONS = [rgb("#c8443a"), rgb("#4f8fd0"), rgb("#6fb84a"), rgb("#a86ad0"), rgb("#e6b84a")]


def glow(a, x, y, r, color, alpha=0.4):
    """A soft halo that fades out inside the image (never cut by its edge)."""
    room = min(x, y, a.w - x, a.h - y)
    r = min(r, room * 0.62)
    p = skia.Path()
    p.addCircle(x, y, r)
    a.fill_path(p, color, alpha, blur=r * 0.28)


def flask(a, x, y, r, liquid):
    """A round flask from above: glass body with liquid, the neck and cork."""
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r, 40), GLASS, outline=DETAIL * 1.3, depth=3, light_k=0.6, mottle=0)
    a.shape(ellipse(x, y, r * 0.78, r * 0.78, 36), liquid, outline=0, depth=2, shade_k=0.3, light_k=0.4, ao=0, mottle=0)
    a.shape(ellipse(x, y, r * 0.32, r * 0.32, 20), GLASS, outline=FINE * 1.3, depth=1, mottle=0, shade_k=0, light_k=0)
    dot(a, x, y, r * 0.2, rgb("#b88a5a"))
    a.ink([(x - r * 0.6, y - r * 0.2), (x - r * 0.3, y - r * 0.6)], FINE * 1.6, color=(250, 250, 245), alpha=0.85)


def candle(a, x, y, r=10, lit=True):
    if lit:
        glow(a, x, y, r * 3, rgb("#ffd27a"), 0.35)
    a.shape(ellipse(x, y, r, r, 24), WAX, outline=DETAIL, depth=2, mottle=0)
    if lit:
        a.shape(scallop(x, y, r * 0.45, a.rng, 5, 0.25), rgb("#f6b444"), outline=FINE, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        dot(a, x, y, r * 0.18, rgb("#fff4cf"))


def crystal(a, x, y, r, color, ang=0.0):
    """A crystal point from above: a hexagon with facet lines to its tip."""
    pts = [(x + r * math.cos(ang + k * math.pi / 3), y + r * math.sin(ang + k * math.pi / 3)) for k in range(6)]
    soft_shadow(a, pts, dx=3, dy=4)
    for k in range(6):
        face = [pts[k], pts[(k + 1) % 6], (x, y)]
        lit = math.cos(ang + (k + 0.5) * math.pi / 3 + math.pi * 0.75)
        col = tint(color, 0.3 * lit) if lit > 0 else shade(color, -0.3 * lit)
        a.shape(face, col, outline=0, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    for k in range(6):
        a.ink([pts[k], (x, y)], FINE * 0.9, color=shade(color, 0.5), alpha=0.6, wob=0)
    a.ink(pts, DETAIL * 1.1, closed=True, wob=0.2)


def circle_marks(a, cx, cy, R, color, n_runes=8):
    """A ritual circle drawn on the floor: two rings, a star, rune marks."""
    for r in (R, R * 0.86):
        a.ink(ellipse(cx, cy, r, r, 96), DETAIL * 1.2, closed=True, color=color, alpha=0.95, wob=0.6)
    star = [(cx + R * 0.86 * math.cos(-math.pi / 2 + k * 4 * math.pi / 5), cy + R * 0.86 * math.sin(-math.pi / 2 + k * 4 * math.pi / 5)) for k in range(5)]
    a.ink(star, DETAIL, closed=True, color=color, alpha=0.9, wob=0.6)
    for k in range(n_runes):
        t = 2 * math.pi * (k + 0.5) / n_runes
        x, y = cx + R * 0.93 * math.cos(t), cy + R * 0.93 * math.sin(t)
        a.ink([(x - 5, y - 5), (x + 2, y), (x - 3, y + 6)], FINE * 1.3, color=color, alpha=0.9)


# -- alchemy -------------------------------------------------------------------------------------


def alchemy_table(seed=601):
    w, h = 480, 240
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD_DARK, n=3, corner=8)
    flask(a, 70, 70, 26, POTIONS[1])
    flask(a, 120, 160, 20, POTIONS[2])
    flask(a, 400, 170, 24, POTIONS[3])
    mortar(a, 330, 70, 30)
    for k, x in enumerate((180, 210, 240, 270)):
        a.shape(ellipse(x, 180, 12, 12, 20), rgb("#c9b896"), outline=DETAIL, depth=2, mottle=0)
        dot(a, x, 180, 6, POTIONS[k], 0.9)
    open_book(a, 230, 90, 0.9)
    candle(a, 440, 60, 10)
    return a.image()


def mortar(a, x, y, r):
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r, 40), STONE, outline=DETAIL * 1.3, depth=4, light_k=0.4)
    a.shape(ellipse(x, y, r * 0.68, r * 0.68, 36), shade(STONE, 0.35), outline=DETAIL, depth=4, shade_k=0, light_k=0, ao=0.5, detail=lambda art, p: [dot(art, x + art.rng.uniform(-r * 0.4, r * 0.4), y + art.rng.uniform(-r * 0.4, r * 0.4), 2, rgb("#7fae5a")) for _ in range(6)])
    a.ink([(x - r * 0.1, y - r * 0.1), (x + r * 1.3, y - r * 0.9)], DETAIL * 2.4, color=INK, taper=False)
    a.ink([(x - r * 0.1, y - r * 0.1), (x + r * 1.3, y - r * 0.9)], DETAIL * 1.4, color=tint(STONE, 0.1), taper=False)


def mortar_pestle(seed=602):
    s = 140
    a = Art(s, s, seed)
    mortar(a, 60, 80, 40)
    return a.image()


def alembic(seed=603):
    w, h = 320, 220
    a = Art(w, h, seed)
    # Burner, the round boiling flask on it, the tube to the receiver flask.
    glow(a, 90, 110, 60, rgb("#ff9a3c"), 0.3)
    a.shape(ellipse(90, 110, 50, 50, 48), IRON, outline=DETAIL * 1.3, depth=5)
    flask(a, 90, 110, 40, POTIONS[0])
    a.ink(chaikin([(90, 70), (130, 40), (220, 50), (240, 110)], False, 2), DETAIL * 3.4, color=INK, taper=False)
    a.ink(chaikin([(90, 70), (130, 40), (220, 50), (240, 110)], False, 2), DETAIL * 2.2, color=GLASS, taper=False)
    flask(a, 240, 140, 34, tint(POTIONS[0], 0.25))
    return a.image()


def flask_set(seed=604):
    w, h = 260, 200
    a = Art(w, h, seed)
    spots = [(60, 60, 28), (140, 50, 22), (210, 80, 26), (90, 140, 24), (170, 145, 30)]
    for (x, y, r), c in zip(spots, POTIONS):
        flask(a, x, y, r, c)
    return a.image()


def ingredient_jars(seed=605):
    w, h = 300, 180
    a = Art(w, h, seed)
    fills = [rgb("#7fae5a"), rgb("#c9a45a"), rgb("#b56a6a"), rgb("#6f9fb5"), rgb("#9a7a5a"), rgb("#d8d0b8")]
    for k in range(6):
        x, y = 50 + (k % 3) * 100, 50 + (k // 3) * 80
        soft_shadow(a, (x, y), 30, 3, 4)
        a.shape(ellipse(x, y, 30, 30, 36), GLASS, outline=DETAIL * 1.3, depth=3, light_k=0.5, mottle=0)
        a.shape(ellipse(x, y, 22, 22, 32), fills[k], outline=0, depth=2, shade_k=0.3, light_k=0.3, ao=0, mottle=0.1)
        a.shape(ellipse(x, y, 12, 12, 20), rgb("#b88a5a"), outline=FINE * 1.3, depth=2, mottle=0)
    return a.image()


def herb_bundles(seed=606):
    w, h = 360, 220
    a = Art(w, h, seed)
    # A drying line across, bundles hanging (seen from above: lying fans).
    a.ink([(10, 40), (w - 10, 46)], DETAIL * 1.6, color=rgb("#8a6a40"))
    greens = [rgb("#6f9443"), rgb("#8aa65a"), rgb("#a8a050"), rgb("#7a8a4a")]
    for k, x in enumerate(range(50, w - 30, 70)):
        for _ in range(12):
            t = math.pi / 2 + a.rng.uniform(-0.35, 0.35)
            L = a.rng.uniform(60, 120)
            leaf(a, x + math.cos(t) * L * 0.75, 50 + math.sin(t) * L * 0.75, a.rng.uniform(34, 46), vary(a.rng, greens[k % 4], 0.05), ang=t, vein=True, outline=FINE * 1.2)
        a.shape(rect(x - 8, 40, x + 8, 60), rgb("#c9a061"), outline=DETAIL, corner=3, depth=2, mottle=0)
    return a.image()


def bubbling_cauldron(seed=607):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    black = rgb("#45464c")
    brew = ARCANE
    glow(a, m, m, 110, brew, 0.3)
    for ang in (math.pi * 0.15, math.pi * 1.15):
        x, y = m + (m - 16) * math.cos(ang), m + (m - 16) * math.sin(ang)
        a.shape(ellipse(x, y, 14, 14, 32), black, outline=DETAIL * 1.3, depth=4)
    a.shape(ellipse(m, m, m - 20, m - 20, 96), black, depth=12)

    def bubbles(art, path):
        for _ in range(10):
            t, d = art.rng.uniform(0, 6.28), art.rng.uniform(0, m - 60)
            rr = art.rng.uniform(5, 13)
            art.shape(ellipse(m + d * math.cos(t), m + d * math.sin(t), rr, rr, 24), tint(brew, 0.35), outline=FINE * 1.2, depth=2, shade_k=0.2, light_k=0.5, ao=0, mottle=0)

    a.shape(ellipse(m, m, m - 40, m - 40, 96), brew, outline=DETAIL * 1.3, depth=10, shade_k=0, light_k=0, detail=bubbles)
    return a.image()


# -- arcane --------------------------------------------------------------------------------------


def summoning_circle(seed=611):
    s = 520
    a = Art(s, s, seed)
    m = s / 2
    blood = rgb("#9a2a26")
    circle_marks(a, m, m, 220, blood)
    for k in range(5):
        t = -math.pi / 2 + k * 2 * math.pi / 5
        candle(a, m + 240 * math.cos(t), m + 240 * math.sin(t), 13)
    return a.image(grain=0.02)


def teleport_circle(seed=612):
    s = 480
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 210, TEAL, 0.25)
    circle_marks(a, m, m, 200, tint(TEAL, 0.3), 12)
    for r in (120, 60):
        a.ink(ellipse(m, m, r, r, 80), DETAIL, closed=True, color=tint(TEAL, 0.4), alpha=0.9)
    glow(a, m, m, 60, tint(TEAL, 0.5), 0.5)
    return a.image(grain=0.02)


def chalk_pentagram(seed=613):
    s = 400
    a = Art(s, s, seed)
    m = s / 2
    circle_marks(a, m, m, 170, CHALK, 0)
    return a.image(grain=0.02)


def crystal_cluster(seed=614, color=ARCANE):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 90, color, 0.3)
    pts = [(m + a.rng.uniform(-50, 50), m + a.rng.uniform(-50, 50), a.rng.uniform(18, 34)) for _ in range(6)]
    for x, y, r in sorted(pts, key=lambda p: p[2]):
        crystal(a, x, y, r, vary(a.rng, color, 0.06), a.rng.uniform(0, 1))
    return a.image()


def orb_pedestal(seed=615):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    a.shape(rect(20, 20, s - 20, s - 20), STONE, corner=10, depth=10)
    a.shape(ellipse(m, m, 70, 70, 64), tint(STONE, 0.15), outline=DETAIL * 1.3, depth=6, light_k=0.4)
    glow(a, m, m, 70, ARCANE, 0.45)
    a.shape(ellipse(m, m, 44, 44, 56), ARCANE, outline=DETAIL * 1.3, depth=6, light_k=0.7, mottle=0.06)
    a.ink([(m - 24, m - 14), (m - 10, m - 28)], FINE * 2.2, color=(250, 248, 255), alpha=0.85)
    return a.image()


def crystal_ball(seed=616):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 62, 62, 56), GOLD, outline=DETAIL * 1.3, depth=6, light_k=0.5)
    glow(a, m, m, 50, rgb("#9fd6e6"), 0.45)
    a.shape(ellipse(m, m, 46, 46, 56), rgb("#b9dbe6"), outline=DETAIL * 1.3, depth=6, light_k=0.7, mottle=0.04, detail=lambda art, p: art.ink(chaikin([(m - 20, m + 6), (m, m - 10), (m + 18, m + 8), (m - 4, m + 18)], True, 2), FINE * 1.4, color=rgb("#e8f6fa"), alpha=0.8))
    a.ink([(m - 26, m - 14), (m - 12, m - 28)], FINE * 2.2, color=(250, 250, 255), alpha=0.9)
    return a.image()


def blue_brazier(seed=617):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    flame_c = rgb("#5fb0e8")
    glow(a, m, m, 90, flame_c, 0.4)
    a.shape(ellipse(m, m, 80, 80, 64), IRON, depth=10)
    a.shape(ellipse(m, m, 60, 60, 64), rgb("#2c2a30"), outline=DETAIL * 1.3, depth=8, shade_k=0, light_k=0, ao=0.6)
    for r, col in ((42, flame_c), (28, tint(flame_c, 0.35)), (12, rgb("#eaf8ff"))):
        a.shape(scallop(m, m, r, a.rng, 7, 0.22), col, outline=DETAIL if r > 20 else 0, depth=3, shade_k=0.2, light_k=0, ao=0, mottle=0)
    return a.image()


def glowing_mushrooms(seed=618):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    cap = TEAL
    for _ in range(6):
        x, y, r = m + a.rng.uniform(-55, 55), m + a.rng.uniform(-55, 55), a.rng.uniform(12, 26)
        glow(a, x, y, r * 2, cap, 0.35)
        a.shape(ellipse(x, y, r, r * 0.92, 32), cap, outline=DETAIL, depth=r * 0.2, light_k=0.6, mottle=0)
        for _ in range(int(r / 5)):
            t, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, r * 0.6)
            dot(a, x + d * math.cos(t), y + d * math.sin(t), 2, rgb("#e8fffc"))
    return a.image()


# -- books, scrolls -------------------------------------------------------------------------------


def open_book(a, x, y, k=1.0):
    w, h = 140 * k, 96 * k
    soft_shadow(a, rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), dx=4, dy=5)
    a.shape(rect(x - w / 2 - 6, y - h / 2 - 4, x + w / 2 + 6, y + h / 2 + 4), rgb("#6a3a2e"), outline=DETAIL * 1.3, corner=4, depth=3)
    for side in (-1, 1):
        page = rect(x if side > 0 else x - w / 2, y - h / 2, x + w / 2 if side > 0 else x, y + h / 2)

        def lines(art, p, side=side):
            for j in range(7):
                yy = y - h / 2 + 14 * k + j * 10 * k
                xa = x + side * 10 * k
                xb = x + side * (w / 2 - 10 * k)
                art.ink([(min(xa, xb), yy), (max(xa, xb) - art.rng.uniform(0, 20 * k), yy)], FINE * 0.9, color=shade(PARCH, 0.5), alpha=0.7, taper=False)

        a.shape(page, PARCH, outline=DETAIL, corner=3, depth=3, shade_k=0.2, light_k=0.2, detail=lines)
    a.ink([(x, y - h / 2), (x, y + h / 2)], DETAIL, alpha=0.8, taper=False)


def spellbook(seed=621):
    w, h = 220, 160
    a = Art(w, h, seed)
    open_book(a, w / 2, h / 2, 1.2)
    a.ink(ellipse(w / 2 + 40, h / 2, 18, 18, 32), FINE * 1.4, closed=True, color=ARCANE)
    a.ink([(w / 2 + 40, h / 2 - 18), (w / 2 + 40, h / 2 + 18)], FINE * 1.2, color=ARCANE)
    return a.image()


def tome_stack(seed=622):
    s = 200
    a = Art(s, s, seed)
    cols = [rgb("#6a3a2e"), rgb("#3c5a78"), rgb("#55743f"), rgb("#694a6e")]
    for k, c in enumerate(cols):
        x, y = 100 + a.rng.uniform(-10, 10), 100 + a.rng.uniform(-10, 10)
        ang = a.rng.uniform(-0.3, 0.3)
        ca, sa = math.cos(ang), math.sin(ang)
        bw, bh = 120 - k * 12, 84 - k * 8
        pts = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in ((-bw / 2, -bh / 2), (bw / 2, -bh / 2), (bw / 2, bh / 2), (-bw / 2, bh / 2))]
        soft_shadow(a, pts, dx=4, dy=5)
        a.shape(pts, tint(c, 0.04 * k), outline=DETAIL * 1.3, corner=4, depth=4, light_k=0.35)
        a.ink([(x - bw * 0.3 * ca, y - bw * 0.3 * sa), (x + bw * 0.3 * ca, y + bw * 0.3 * sa)], FINE * 1.2, color=GOLD, alpha=0.8)
    return a.image()


def spiral_end(a, cx, cy, rx, ry, ang, color):
    """The end of a roll of parchment: an oval face with a spiral."""
    face = [(cx + rx * math.cos(t) * math.cos(ang) - ry * math.sin(t) * math.sin(ang), cy + rx * math.cos(t) * math.sin(ang) + ry * math.sin(t) * math.cos(ang)) for t in [2 * math.pi * k / 32 for k in range(32)]]
    a.shape(face, tint(color, 0.08), outline=DETAIL, corner=0, wob=0.1, depth=1.5, shade_k=0.25, light_k=0.2, ao=0, mottle=0)
    sp = []
    for k in range(40):
        t = k / 39 * 2.6 * 2 * math.pi
        f = 0.15 + 0.8 * k / 39
        lx, ly = rx * f * math.cos(t), ry * f * math.sin(t)
        sp.append((cx + lx * math.cos(ang) - ly * math.sin(ang), cy + lx * math.sin(ang) + ly * math.cos(ang)))
    a.ink(sp, FINE * 1.1, color=shade(color, 0.5), alpha=0.85, wob=0.1)


def roll(a, x, y, L, half_w, ang, color=PARCH, spiral_at=1, tie=None):
    """A rolled parchment: slimmer in the middle, its rolled end (one side)
    showing the spiral."""
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    n = 16
    spine = [(x + ux * L * (i / n - 0.5), y + uy * L * (i / n - 0.5)) for i in range(n + 1)]
    ws = [half_w * (1 - 0.34 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    left = [(sx + px * w, sy + py * w) for (sx, sy), w in zip(spine, ws)]
    right = [(sx - px * w, sy - py * w) for (sx, sy), w in zip(spine, ws)]
    poly = left + right[::-1]
    soft_shadow(a, poly, dx=3, dy=4)

    def lines(art, p):
        for k in (-0.45, 0.4):
            art.ink([(sx + px * w * k, sy + py * w * k) for (sx, sy), w in zip(spine[1:-1], ws[1:-1])], FINE * 0.9, color=shade(color, 0.4), alpha=0.6, wob=0.2)

    a.shape(poly, color, outline=DETAIL * 1.2, corner=0, wob=0.2, depth=3, light_k=0.4, mottle=0.03, detail=lines)
    ex, ey = spine[-1] if spiral_at > 0 else spine[0]
    spiral_end(a, ex, ey, ws[-1] * 0.42, ws[-1], ang, color)
    if tie:
        a.ink([(x - px * half_w * 0.8, y - py * half_w * 0.8), (x + px * half_w * 0.8, y + py * half_w * 0.8)], DETAIL * 1.4, color=tie)


def scroll(a, x, y, L, ang, open_=False):
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    if open_:
        sheet_ = [(x - ux * L / 2 - px * 40, y - uy * L / 2 - py * 40), (x + ux * L / 2 - px * 40, y + uy * L / 2 - py * 40), (x + ux * L / 2 + px * 40, y + uy * L / 2 + py * 40), (x - ux * L / 2 + px * 40, y - uy * L / 2 + py * 40)]
        soft_shadow(a, sheet_, dx=4, dy=5)
        a.shape(sheet_, PARCH, outline=DETAIL * 1.2, corner=3, depth=3, detail=lambda art, p: [art.ink([(x - ux * L * 0.35 + px * o, y - uy * L * 0.35 + py * o), (x + ux * L * 0.35 + px * o, y + uy * L * 0.35 + py * o)], FINE * 0.9, color=shade(PARCH, 0.5), alpha=0.7) for o in (-24, -12, 0, 12, 24)])
        # The rolls at both ends lie across the sheet; each shows its spiral
        # at the bottom end.
        for e in (-1, 1):
            cx, cy = x + ux * e * L / 2, y + uy * e * L / 2
            roll(a, cx, cy, 96, 11, ang + math.pi / 2, tint(PARCH, 0.05), spiral_at=1)
    else:
        roll(a, x, y, L, 13, ang, PARCH, spiral_at=1, tie=rgb("#a8483a"))

def open_scroll(seed=623):
    w, h = 260, 160
    a = Art(w, h, seed)
    scroll(a, w / 2, h / 2, 170, 0.0, open_=True)
    return a.image()


def scroll_pile(seed=624):
    s = 220
    a = Art(s, s, seed)
    for _ in range(7):
        scroll(a, 110 + a.rng.uniform(-40, 40), 110 + a.rng.uniform(-40, 40), a.rng.uniform(90, 130), a.rng.uniform(0, 3.14))
    return a.image()


def rolled_scroll(seed=625):
    w, h = 180, 80
    a = Art(w, h, seed)
    scroll(a, w / 2, h / 2, 140, 0.1)
    return a.image()


# -- dark -----------------------------------------------------------------------------------------


def skull_at(a, x, y, s=1.0):
    pts = chaikin([(x - 30 * s, y - 10 * s), (x - 22 * s, y - 34 * s), (x + 22 * s, y - 34 * s), (x + 30 * s, y - 10 * s), (x + 22 * s, y + 24 * s), (x - 22 * s, y + 24 * s)], True, 2)
    soft_shadow(a, pts, dx=4, dy=5)
    a.shape(pts, BONE, outline=DETAIL * 1.3, corner=0, depth=4, light_k=0.4)
    for dx in (-12, 12):
        a.shape(ellipse(x + dx * s, y + 2 * s, 8 * s, 9 * s, 20), rgb("#2a221e"), outline=FINE, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    a.shape([(x, y + 12 * s), (x - 4 * s, y + 18 * s), (x + 4 * s, y + 18 * s)], rgb("#2a221e"), outline=0, corner=1, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)


def skull_candle(seed=631):
    s = 140
    a = Art(s, s, seed)
    m = s / 2
    skull_at(a, m, m + 8, 1.4)
    a.shape(scallop(m, m - 8, 22, a.rng, 9, 0.2), WAX, outline=DETAIL, depth=3, mottle=0)  # wax drip on top
    candle(a, m, m - 8, 11)
    return a.image()


def bones(seed=632):
    w, h = 260, 200
    a = Art(w, h, seed)

    def bone(x, y, L, ang):
        ux, uy = math.cos(ang), math.sin(ang)
        for e in (-1, 1):
            for k in (-1, 1):
                cx, cy = x + ux * e * L / 2 - uy * k * 7, y + uy * e * L / 2 + ux * k * 7
                a.shape(ellipse(cx, cy, 9, 9, 16), BONE, outline=DETAIL, depth=2, mottle=0)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 16, color=INK, taper=False)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 10, color=BONE, taper=False)

    for _ in range(4):
        bone(130 + a.rng.uniform(-60, 60), 100 + a.rng.uniform(-40, 40), a.rng.uniform(70, 110), a.rng.uniform(0, 3.14))
    skull_at(a, 70, 70, 1.0)
    return a.image()


def candle_cluster(seed=633):
    s = 180
    a = Art(s, s, seed)
    for _ in range(7):
        candle(a, 90 + a.rng.uniform(-50, 50), 90 + a.rng.uniform(-50, 50), a.rng.uniform(8, 14))
    return a.image()


# -- items ----------------------------------------------------------------------------------------


def wand(seed=641):
    w, h = 200, 80
    a = Art(w, h, seed)
    a.ink([(20, 50), (180, 30)], 13, color=INK, taper=False)
    a.ink([(20, 50), (180, 30)], 8, color=WOOD_DARK, taper=False)
    a.ink([(20, 50), (60, 45)], 8, color=GOLD, taper=False)
    glow(a, 180, 30, 20, ARCANE, 0.5)
    crystal(a, 182, 30, 9, ARCANE)
    return a.image()


def staff(seed=642):
    w, h = 380, 120
    a = Art(w, h, seed)
    a.ink(chaikin([(20, 90), (200, 70), (330, 56)], False, 2), 17, color=INK, taper=False)
    a.ink(chaikin([(20, 90), (200, 70), (330, 56)], False, 2), 11, color=WOOD, taper=False)
    a.ink(chaikin([(320, 70), (350, 30), (370, 60), (348, 84)], False, 2), 13, color=INK, taper=False)
    a.ink(chaikin([(320, 70), (350, 30), (370, 60), (348, 84)], False, 2), 8, color=WOOD, taper=False)
    glow(a, 348, 58, 28, TEAL, 0.5)
    a.shape(ellipse(348, 58, 14, 14, 24), TEAL, outline=DETAIL, depth=3, light_k=0.7, mottle=0)
    return a.image()


def hourglass(seed=643):
    s = 130
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 48, 48, 48), WOOD_DARK, depth=6)
    for k in range(3):
        t = 2 * math.pi * k / 3 + 0.5
        a.shape(ellipse(m + 40 * math.cos(t), m + 40 * math.sin(t), 8, 8, 16), WOOD, outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(m, m, 30, 30, 40), GLASS, outline=DETAIL * 1.2, depth=3, light_k=0.6, mottle=0)
    a.shape(ellipse(m, m, 18, 18, 32), rgb("#e0c07a"), outline=FINE, depth=2, mottle=0)
    return a.image()


def astrolabe(seed=644):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 90, 90, 72), GOLD, depth=8, light_k=0.5)
    a.shape(ellipse(m, m, 74, 74, 72), shade(GOLD, 0.15), outline=DETAIL, depth=4, detail=lambda art, p: [art.ink([(m + 60 * math.cos(t), m + 60 * math.sin(t)), (m + 72 * math.cos(t), m + 72 * math.sin(t))], FINE, color=shade(GOLD, 0.5)) for t in [2 * math.pi * k / 24 for k in range(24)]])
    a.ink(ellipse(m - 10, m, 44, 34, 48), DETAIL, closed=True, color=shade(GOLD, 0.5))
    a.ink([(m - 70, m + 20), (m + 70, m - 20)], DETAIL * 1.4, color=shade(GOLD, 0.45))
    a.shape(ellipse(m, m, 8, 8, 16), BRASS, outline=DETAIL, depth=2, mottle=0)
    return a.image()


MAGIC = {
    "Alchemy Table": alchemy_table,
    "Mortar and Pestle": mortar_pestle,
    "Alembic": alembic,
    "Flasks": flask_set,
    "Ingredient Jars": ingredient_jars,
    "Drying Herbs": herb_bundles,
    "Bubbling Cauldron": bubbling_cauldron,
    "Summoning Circle": summoning_circle,
    "Teleport Circle": teleport_circle,
    "Chalk Pentagram": chalk_pentagram,
    "Purple Crystals": crystal_cluster,
    "Blue Crystals": lambda: crystal_cluster(615, rgb("#5f9ad8")),
    "Green Crystals": lambda: crystal_cluster(616, rgb("#5fb87a")),
    "Orb on Pedestal": orb_pedestal,
    "Crystal Ball": crystal_ball,
    "Blue Fire Brazier": blue_brazier,
    "Glowing Mushrooms": glowing_mushrooms,
    "Spellbook": spellbook,
    "Tome Stack": tome_stack,
    "Open Scroll": open_scroll,
    "Scroll Pile": scroll_pile,
    "Rolled Scroll": rolled_scroll,
    "Skull Candle": skull_candle,
    "Bones": bones,
    "Candle Cluster": candle_cluster,
    "Wand": wand,
    "Staff": staff,
    "Hourglass": hourglass,
    "Astrolabe": astrolabe,
}
