"""Workshop and crafts (batch 6): smithy, carpentry, weaving, pottery,
tanning and loose tools. Top-down, same pen style."""

import math

import skia

from kit import BRASS, IRON, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, dot, scallop, soft_shadow
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

STEEL = rgb("#9aa0aa")
COAL = rgb("#2e2a28")
EMBER = rgb("#e9773a")
LEATHER = rgb("#8a5a3a")
HIDE = rgb("#c9a27a")
CLAY = rgb("#b98a5a")
BRICK = rgb("#a8604a")
YARN = rgb("#d8c9a8")


def rot_pts(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


# -- loose tools (drawn into any art at any angle) -----------------------------------------------


def handle(a, x0, y0, x1, y1, w=10, color=WOOD):
    a.ink([(x0, y0), (x1, y1)], w + 9, color=INK, taper=False, wob=0, var=0.02)
    a.ink([(x0, y0), (x1, y1)], w, color=color, taper=False, wob=0, var=0.02)
    a.ink([(x0, y0), (x1, y1)], max(1, w * 0.2), color=tint(color, 0.35), alpha=0.7, taper=False, wob=0, var=0.02)


def hammer_at(a, x, y, ang, L=110):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx, hy, 10)
    head = rot_pts(rect(hx - 12, hy - 26, hx + 12, hy + 26), hx, hy, ang)
    a.shape(head, IRON, outline=DETAIL * 2.0, corner=3, depth=3, light_k=0.5, mottle=0, var=0.03)


def tongs_at(a, x, y, ang, L=130):
    for side in (-1, 1):
        t = ang + side * 0.06
        a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], 13, color=INK, taper=False, var=0.02)
        a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], 6, color=shade(IRON, 0.1), taper=False, var=0.02)
    dot(a, x + L * 0.62 * math.cos(ang), y + L * 0.62 * math.sin(ang), 5, STEEL)


def saw_at(a, x, y, ang, L=170):
    """A handsaw: tapering blade with a toothed lower edge, a wooden grip
    with its hand hole."""
    tooth_pts = []
    n = 14
    for k in range(n + 1):
        t = k / n
        bx = x + 40 + (L - 40) * t
        by = y + 12 - 4 * t
        tooth_pts.append((bx, by + (5 if k % 2 else 0)))
    blade = [(x + 40, y - 14), (x + L, y - 2)] + tooth_pts[::-1]
    blade = rot_pts(blade, x, y, ang)
    a.shape(blade, STEEL, outline=DETAIL * 2.0, corner=0, wob=0.1, depth=2, light_k=0.55, mottle=0, var=0.03)
    a.ink(rot_pts([(x + 50, y - 6), (x + L - 20, y + 1)], x, y, ang), FINE * 1.2, color=tint(STEEL, 0.6), alpha=0.8)
    grip = rot_pts(chaikin([(x, y - 22), (x + 46, y - 18), (x + 46, y + 18), (x, y + 24)], True, 2), x, y, ang)
    a.shape(grip, WOOD, outline=DETAIL * 2.0, corner=0, depth=3, mottle=0, var=0.03)
    hole = rot_pts(ellipse(x + 20, y, 9, 12, 20), x, y, ang)
    a.shape(hole, rgb("#e8dfc8"), outline=FINE * 1.2, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0, var=0.03)


def axe_at(a, x, y, ang, L=150):
    """An axe lying flat: the handle, and at its end the head standing out
    sideways (perpendicular to the handle): the eye around the handle, the
    poll behind it and the blade flaring to a curved cutting edge."""
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx + ux * 8, hy + uy * 8, 11)
    edge = [(hx + 34 * math.cos(t), hy - 42 + 14 * math.sin(t)) for t in [-0.1 - k * (math.pi - 0.2) / 12 for k in range(13)]]
    local = [(hx - 12, hy + 18), (hx + 12, hy + 18), (hx + 12, hy - 6), (hx + 34, hy - 40)] + edge[1:-1] + [(hx - 30, hy - 40), (hx - 12, hy - 6)]
    head = rot_pts(local, hx, hy, ang)
    a.shape(head, STEEL, outline=DETAIL * 2.0, corner=2, depth=4, light_k=0.55, mottle=0, var=0.03)
    bevel = rot_pts([(hx - 24, hy - 38), (hx, hy - 44), (hx + 28, hy - 38)], hx, hy, ang)
    a.ink(bevel, FINE * 1.4, color=tint(STEEL, 0.65), alpha=0.9)
    a.ink(rot_pts([(hx - 12, hy + 4), (hx + 12, hy + 4)], hx, hy, ang), FINE * 1.2, color=shade(STEEL, 0.4), alpha=0.8)

def shovel_at(a, x, y, ang, L=170):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx, hy, 10)
    blade = rot_pts(chaikin([(hx, hy - 24), (hx + 60, hy - 22), (hx + 74, hy), (hx + 60, hy + 22), (hx, hy + 24)], True, 1), hx, hy, ang)
    a.shape(blade, STEEL, outline=DETAIL * 2.0, corner=0, depth=3, light_k=0.5, mottle=0, var=0.03)
    a.ink(rot_pts([(x - 14, y - 16), (x - 14, y + 16)], x, y, ang), 12, color=INK, taper=False, var=0.02)
    a.ink(rot_pts([(x - 14, y - 16), (x - 14, y + 16)], x, y, ang), 5, color=WOOD, taper=False, var=0.02)


def pickaxe_at(a, x, y, ang, L=150):
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx, hy, 11)
    head = rot_pts(chaikin([(hx - 4, hy - 60), (hx + 8, hy - 20), (hx + 10, hy), (hx + 8, hy + 20), (hx - 4, hy + 60), (hx - 8, hy + 20), (hx - 8, hy - 20)], True, 1), hx, hy, ang)
    a.shape(head, IRON, outline=DETAIL * 2.0, corner=0, depth=3, light_k=0.5, mottle=0, var=0.03)


def tool(fn, w=260, h=200, ang=-0.4, x=None, y=None, **kw):
    def make(seed=500):
        a = Art(w, h, seed)
        fn(a, x if x is not None else 40, y if y is not None else h - 40, ang, **kw)
        return a.image()

    return make


# -- smithy ---------------------------------------------------------------------------------------


def forge(seed=501):
    w, h = 360, 300
    a = Art(w, h, seed)
    # Brick hearth; its chimney at the back seen from above (a square stack
    # with the dark flue), coals glowing in the firepot.
    a.shape(rect(10, 10, w - 10, h - 10), BRICK, corner=10, depth=12, detail=lambda art, p: [art.ink([(10, y), (w - 10, y)], FINE * 1.2, color=shade(BRICK, 0.5), alpha=0.7, taper=False) for y in range(40, h, 30)])
    stack = rect(w / 2 - 70, 14, w / 2 + 70, 96)
    soft_shadow(a, stack, dx=8, dy=10, alpha=0.4, blur=8)
    a.shape(stack, tint(BRICK, 0.12), outline=DETAIL * 1.3, corner=6, depth=8, light_k=0.4)
    a.shape(rect(w / 2 - 40, 32, w / 2 + 40, 78), rgb("#241e1c"), outline=DETAIL, corner=4, depth=4, shade_k=0, light_k=0, ao=0.5)
    glow = skia.Path()
    glow.addCircle(w / 2, 190, 90)
    a.fill_path(glow, rgb("#ff9a3c"), 0.35, blur=30)

    def coals(art, p):
        for _ in range(40):
            x, y = art.rng.uniform(w / 2 - 80, w / 2 + 80), art.rng.uniform(132, 250)
            hot = art.rng.random() < 0.4
            art.shape(blob(x, y, art.rng.uniform(7, 12), art.rng, 7, 0.2), EMBER if hot else COAL, outline=FINE * 1.1, smooth=True, depth=2, shade_k=0.3, light_k=0.4 if hot else 0.2, ao=0, mottle=0)
        g = skia.Path()
        g.addCircle(w / 2, 190, 40)
        art.fill_path(g, rgb("#ffd27a"), 0.5, blur=14)

    a.shape(rect(w / 2 - 96, 118, w / 2 + 96, 262), COAL, outline=DETAIL * 1.3, corner=12, depth=12, shade_k=0, light_k=0, ao=0.6, detail=coals)
    return a.image()


def bellows(seed=502):
    w, h = 300, 160
    a = Art(w, h, seed)
    body = chaikin([(30, 20), (200, 30), (240, h / 2), (200, h - 30), (30, h - 20)], True, 2)

    def pleats(art, p):
        for x in (80, 120, 160):
            art.ink([(x, 26), (x, h - 26)], FINE * 1.3, color=shade(LEATHER, 0.5), alpha=0.8)

    a.shape(body, LEATHER, depth=10, light_k=0.4, detail=pleats)
    a.shape(rect(232, h / 2 - 9, w - 10, h / 2 + 9), BRASS, outline=DETAIL, corner=4, depth=3, mottle=0)
    a.shape(rect(6, 40, 40, h - 40), WOOD, outline=DETAIL * 1.2, corner=6, depth=4)
    return a.image()


def anvil_stump(seed=503):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    a.shape(scallop(m, m, 112, a.rng, 12, 0.05), shade(WOOD, 0.15), depth=12, detail=lambda art, p: [art.ink(scallop(m, m, r, art.rng, 9, 0.03), FINE * 1.1, closed=True, color=shade(WOOD, 0.5), alpha=0.7) for r in (40, 70, 95)])
    body = [(m - 110, m), (m - 64, m - 26), (m - 30, m - 32), (m + 90, m - 36), (m + 110, m - 26), (m + 110, m + 26), (m + 90, m + 36), (m - 30, m + 32), (m - 64, m + 26)]
    soft_shadow(a, body, dx=6, dy=8, alpha=0.4, blur=6)
    a.shape(body, IRON, corner=8, depth=10, light_k=0.5)
    a.ink([(m - 20, m - 16), (m + 96, m - 18)], FINE * 1.4, color=tint(IRON, 0.6), alpha=0.9)
    a.shape(rect(m + 74, m - 7, m + 88, m + 7), shade(IRON, 0.4), outline=DETAIL * 0.9, corner=2, depth=2, mottle=0)
    return a.image()


def quench_trough(seed=504):
    w, h = 340, 150
    a = Art(w, h, seed)
    a.shape(rect(8, 10, w - 8, h - 10), IRON, corner=10, depth=10, light_k=0.3)

    def water(art, p):
        art.ink([(80, 60), (110, 54), (140, 60)], FINE * 1.4, color=rgb("#cfe4ea"), alpha=0.9)
        art.ink([(200, 90), (230, 84)], FINE * 1.2, color=rgb("#cfe4ea"), alpha=0.8)

    a.shape(rect(26, 26, w - 26, h - 26), rgb("#4a6a78"), outline=DETAIL * 1.2, corner=6, depth=12, shade_k=0, light_k=0, ao=0.6, detail=water)
    return a.image()


def grindstone(seed=505):
    w, h = 300, 220
    a = Art(w, h, seed)
    # The frame with a seat, and the stone wheel standing in it (seen as a band).
    a.shape(rect(20, 30, w - 20, h - 30), WOOD_DARK, corner=8, depth=8)
    a.shape(rect(36, 46, w - 36, h - 46), shade(WOOD_DARK, 0.4), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5)
    a.shape(rect(110, 20, 170, h - 20), STONE, corner=24, depth=8, light_k=0.4, detail=lambda art, p: [art.ink([(112, y), (168, y)], FINE, color=shade(STONE, 0.45), alpha=0.6, taper=False) for y in range(40, h - 20, 18)])
    a.ink([(90, h / 2), (190, h / 2)], DETAIL * 2.2, color=IRON, taper=False)
    a.shape(rect(186, h / 2 - 34, 202, h / 2 + 4), WOOD, outline=DETAIL, corner=4, depth=2, mottle=0)
    return a.image()


def crucible(seed=506):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 56, 4, 5, 0.35, 4)
    a.shape(ellipse(m, m, 56, 56, 64), rgb("#5a504a"), depth=8, light_k=0.3)
    g = skia.Path()
    g.addCircle(m, m, 38)
    a.fill_path(g, rgb("#ffb347"), 0.6, blur=10)
    a.shape(ellipse(m, m, 40, 40, 56), rgb("#f6a03a"), outline=DETAIL * 1.2, depth=6, shade_k=0, light_k=0.5, ao=0.3, mottle=0.1)
    a.ink([(m - 18, m - 6), (m + 4, m - 12)], FINE * 1.4, color=rgb("#fff0b8"))
    return a.image()


def ingots(seed=507):
    w, h = 240, 200
    a = Art(w, h, seed)
    gold, silver, copper = rgb("#e2b84e"), rgb("#c7ccd4"), rgb("#c97a4a")
    for row, (y, cols) in enumerate(((60, (silver, silver, gold)), (120, (copper, silver, copper)))):
        for k, col in enumerate(cols):
            x = 44 + k * 66 + (row * 16)
            pts = [(x - 26, y - 16), (x + 26, y - 16), (x + 32, y + 18), (x - 32, y + 18)]
            soft_shadow(a, pts, dx=3, dy=4)
            a.shape(pts, col, outline=DETAIL * 1.1, corner=3, depth=4, light_k=0.6, mottle=0)
            a.shape([(x - 18, y - 10), (x + 18, y - 10), (x + 20, y + 10), (x - 20, y + 10)], tint(col, 0.15), outline=FINE, corner=2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    return a.image()


def coal_pile(seed=508):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m, 96, a.rng, 12, 0.1), shade(COAL, 0.1), outline=DETAIL, smooth=True, depth=10, shade_k=0.4, light_k=0.2, ao=0.2, mottle=0.1)
    for _ in range(70):
        t, d = a.rng.uniform(0, 6.28), 92 * math.sqrt(a.rng.random())
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        a.shape(blob(x, y, a.rng.uniform(6, 11), a.rng, 6, 0.25), mix(COAL, rgb("#4a4644"), 1 - d / 92), outline=FINE, depth=2, shade_k=0.3, light_k=0.5, ao=0, mottle=0)
    return a.image()


# -- carpentry ------------------------------------------------------------------------------------


def workbench(seed=511):
    w, h = 480, 220
    a = Art(w, h, seed)
    board(a, 8, 10, w - 8, h - 10, WOOD_LIGHT, n=4, corner=8)
    a.shape(rect(w - 70, 10, w - 8, 70), IRON, outline=DETAIL * 1.2, corner=4, depth=4, mottle=0)  # vise
    a.ink([(w - 40, 70), (w - 40, 100)], DETAIL * 1.6, color=STEEL, taper=False)
    hammer_at(a, 60, 160, -0.3, 100)
    saw_at(a, 180, 70, 0.1, 170)
    a.shape(rect(260, 130, 380, 166), WOOD, outline=DETAIL, corner=3, depth=3)  # a plank on it
    for _ in range(18):
        dot(a, a.rng.uniform(250, 400), a.rng.uniform(110, 190), a.rng.uniform(1.4, 2.6), rgb("#e8d4a8"), 0.9)
    return a.image()


def sawhorse(seed=512):
    w, h = 420, 220
    a = Art(w, h, seed)
    for x in (90, w - 90):
        for dx in (-22, 22):
            a.ink([(x + dx, 30), (x - dx, h - 30)], 16, color=INK, taper=False)
            a.ink([(x + dx, 30), (x - dx, h - 30)], 11, color=WOOD_DARK, taper=False)
        a.shape(rect(x - 20, 20, x + 20, h - 20), WOOD, outline=DETAIL * 1.2, corner=4, depth=4)
    board(a, 10, h / 2 - 34, w - 10, h / 2 + 34, WOOD_LIGHT, n=1, corner=4)
    a.ink([(w * 0.7, h / 2 - 34), (w * 0.7 + 6, h / 2 + 34)], FINE * 1.3, alpha=0.8)  # a saw cut
    return a.image()


def chopping_block(seed=513):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    a.shape(scallop(m, m, 92, a.rng, 12, 0.05), shade(WOOD, 0.15), depth=10)
    a.shape(scallop(m, m, 76, a.rng, 10, 0.03), WOOD_LIGHT, outline=DETAIL * 1.2, depth=4, light_k=0.3, detail=lambda art, p: [art.ink(scallop(m, m, r, art.rng, 9, 0.03), FINE, closed=True, color=shade(WOOD_LIGHT, 0.45), alpha=0.7) for r in (24, 48)])
    axe_at(a, 30, s - 40, -0.75, 140)
    for k in range(3):
        x, y = 40 + k * 26, 50 + k * 10
        a.shape(rect(x, y, x + 20, y + 54), WOOD_LIGHT, outline=DETAIL, corner=3, depth=3)
    return a.image()


def lumber_stack(seed=514):
    w, h = 480, 220
    a = Art(w, h, seed)
    for k in range(5):
        y = 24 + k * 36
        x0 = 10 + a.rng.uniform(0, 20)
        x1 = w - 10 - a.rng.uniform(0, 20)
        board(a, x0, y, x1, y + 34, vary(a.rng, WOOD_LIGHT, 0.06), n=1, corner=3, outline=DETAIL * 1.2)
    for x in (100, w - 100):
        a.shape(rect(x - 12, 14, x + 12, h - 14), WOOD_DARK, outline=DETAIL * 1.2, corner=3, depth=3)
    return a.image()


def sawdust(seed=515):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    dust = rgb("#e2cc9a")
    a.shape(blob(m, m, 70, a.rng, 12, 0.18), dust, outline=0, smooth=True, depth=6, shade_k=0.3, light_k=0.3, ao=0, mottle=0.1)
    for _ in range(140):
        t, d = a.rng.uniform(0, 6.28), 84 * math.sqrt(a.rng.random())
        dot(a, m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(1, 2.4), shade(dust, a.rng.uniform(0.1, 0.4)), 0.9)
    for _ in range(6):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(20, 70)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        a.ink([(x, y), (x + 10, y + 4), (x + 16, y)], FINE * 1.4, color=shade(dust, 0.3))  # curls
    return a.image()


def tool_chest(seed=516):
    w, h = 280, 170
    a = Art(w, h, seed)
    a.shape(rect(8, 10, w - 8, h - 10), rgb("#7a4a3a"), corner=8, depth=10)
    a.shape(rect(20, 22, w - 20, h - 22), shade(rgb("#7a4a3a"), 0.35), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5)
    hammer_at(a, 40, 60, 0.05, 110)
    tongs_at(a, 40, 110, -0.05, 120)
    a.shape(ellipse(220, 84, 22, 22, 28), IRON, outline=DETAIL, depth=3, mottle=0)
    a.ink([(28, 30), (w - 28, 30)], DETAIL * 2.2, color=IRON, taper=False)
    return a.image()


def tool_rack(seed=517):
    """A deep tool shelf against a wall, from above: the wall's edge at the
    top, the shelf, tools lying along it at slight angles."""
    w, h = 460, 200
    a = Art(w, h, seed)
    a.shape(rect(4, 4, w - 4, 26), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)
    board(a, 10, 22, w - 10, h - 12, WOOD_DARK, n=3, corner=4)
    hammer_at(a, 30, 60, 0.05, 110)
    saw_at(a, 210, 56, 0.0, 170)
    tongs_at(a, 30, 100, -0.03, 140)
    axe_at(a, 220, 110, -0.05, 120)
    shovel_at(a, 40, 160, 0.02, 120)
    pickaxe_at(a, 300, 168, -0.08, 80)
    return a.image()

def loom(seed=521):
    w, h = 400, 300
    a = Art(w, h, seed)
    a.shape(rect(10, 10, w - 10, h - 10), WOOD, corner=8, depth=10)
    a.shape(rect(36, 46, w - 36, h - 46), rgb("#3a2e28"), outline=DETAIL, corner=4, depth=6, shade_k=0, light_k=0, ao=0.5)
    cloth = rgb("#a8483a")

    def weave(art, p):
        for x in range(46, w - 40, 8):
            art.ink([(x, 50), (x, h - 50)], 1.2, color=YARN, alpha=0.9, taper=False, wob=0)

    a.shape(rect(36, 46, w - 36, 120), cloth, outline=DETAIL, corner=2, depth=3, mottle=0.04, detail=lambda art, p: [art.ink([(40, y), (w - 40, y)], FINE, color=tint(cloth, 0.35), alpha=0.7, taper=False) for y in range(56, 120, 12)])
    a.shape(rect(36, 120, w - 36, h - 46), (0, 0, 0), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0, detail=weave) if False else None
    with a.clip(to_path(rect(36, 120, w - 36, h - 46))):
        weave(a, None)
    for y in (40, h - 40, 150):
        a.shape(rect(20, y - 9, w - 20, y + 9), WOOD_DARK, outline=DETAIL * 1.1, corner=4, depth=3)
    a.shape(ellipse(w / 2, 150, 46, 12, 32), WOOD_LIGHT, outline=DETAIL, depth=3, mottle=0)  # shuttle
    return a.image()


def spinning_wheel(seed=522):
    """A spinning wheel from above: its slanted bench, the big upright wheel
    seen almost edge-on (a narrow ellipse with its spokes), the spindle with
    yarn, the distaff with wool, and the treadle."""
    w, h = 360, 240
    a = Art(w, h, seed)
    bench = chaikin([(30, 100), (w - 40, 80), (w - 30, 140), (40, 160)], True, 1)
    a.shape(bench, WOOD_DARK, corner=10, depth=6, detail=lambda art, p: boards(art, 30, 80, w - 30, 160, WOOD_DARK, 2))
    for x, y in ((50, 108), (50, 152), (w - 50, 92), (w - 50, 132)):
        a.shape(ellipse(x, y, 9, 9, 16), shade(WOOD_DARK, 0.2), outline=DETAIL, depth=2, mottle=0)
    # The wheel: rim as a narrow ellipse, hub and spokes showing through.
    cx, cy = 200, 120
    a.shape(ellipse(cx, cy, 26, 104, 72), WOOD, outline=DETAIL * 1.3, depth=6, light_k=0.4)
    a.shape(ellipse(cx, cy, 16, 92, 64), rgb("#e8dfc8"), outline=DETAIL, depth=1, shade_k=0, light_k=0, ao=0.2, mottle=0)
    for k in range(8):
        t = 2 * math.pi * k / 8
        a.ink([(cx, cy), (cx + 16 * math.cos(t), cy + 92 * math.sin(t))], DETAIL * 0.9, color=shade(WOOD, 0.3), taper=False)
    a.shape(ellipse(cx, cy, 10, 12, 20), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
    # Spindle with yarn, the drive band, the distaff with a bundle of wool.
    a.shape(ellipse(80, 118, 22, 22, 32), YARN, outline=DETAIL * 1.2, depth=4, light_k=0.4, detail=lambda art, p: [art.ink(ellipse(80, 118, r, r, 24), FINE, closed=True, color=shade(YARN, 0.35), alpha=0.8) for r in (8, 15)])
    a.ink([(100, 112), (cx - 18, 40)], FINE * 1.1, color=rgb("#d8c08a"))
    a.ink([(100, 124), (cx - 18, 200)], FINE * 1.1, color=rgb("#d8c08a"))
    a.shape(blob(120, 60, 24, a.rng, 9, 0.2), rgb("#efe7d6"), outline=DETAIL * 1.1, smooth=True, depth=4, light_k=0.4)
    a.shape(rect(w - 80, 150, w - 34, 176), WOOD_LIGHT, outline=DETAIL, corner=6, depth=3)
    return a.image()


def pottery_wheel(seed=523):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    a.shape(rect(20, 20, s - 20, s - 20), WOOD_DARK, corner=18, depth=10)
    a.shape(ellipse(m, m, 86, 86, 72), STONE, outline=DETAIL * 1.3, depth=8, light_k=0.4)
    # A pot being thrown on it, wet clay.
    a.shape(ellipse(m, m, 44, 44, 56), CLAY, outline=DETAIL * 1.2, depth=6, light_k=0.5)
    a.shape(ellipse(m, m, 26, 26, 40), shade(CLAY, 0.35), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.5)
    for r in (34, 40):
        a.ink(ellipse(m, m, r, r, 48), FINE * 0.9, closed=True, color=shade(CLAY, 0.4), alpha=0.6)
    return a.image()


def kiln(seed=524):
    s = 300
    a = Art(s, s, seed)
    m = s / 2

    def bricks(art, p):
        for r in (40, 70, 100):
            art.ink(ellipse(m, m, r, r, 80), DETAIL * 0.8, closed=True, color=shade(BRICK, 0.5), alpha=0.85)
            n = int(r / 8)
            for k in range(n):
                t = 2 * math.pi * k / n
                art.ink([(m + r * math.cos(t), m + r * math.sin(t)), (m + (r + 30) * math.cos(t), m + (r + 30) * math.sin(t))], FINE * 1.1, color=shade(BRICK, 0.5), alpha=0.7, taper=False)

    a.shape(ellipse(m, m, 126, 126, 96), tint(BRICK, 0.08), depth=14, light_k=0.35, detail=bricks)
    a.shape(ellipse(m, m, 24, 24, 32), COAL, outline=DETAIL * 1.3, depth=6, shade_k=0, light_k=0, ao=0.5)
    g = skia.Path()
    g.addCircle(m, m, 22)
    a.fill_path(g, rgb("#ff9a3c"), 0.5, blur=8)
    # Pots drying next to it.
    for x, y in ((40, 40), (s - 40, s - 44)):
        a.shape(ellipse(x, y, 20, 20, 28), CLAY, outline=DETAIL, depth=3, light_k=0.4, mottle=0)
        a.shape(ellipse(x, y, 10, 10, 20), shade(CLAY, 0.4), outline=FINE, depth=2, shade_k=0, light_k=0, mottle=0)
    return a.image()


def tanning_rack(seed=525):
    w, h = 300, 340
    a = Art(w, h, seed)
    for y in (20, h - 20):
        a.shape(rect(10, y - 10, w - 10, y + 10), WOOD_DARK, outline=DETAIL * 1.2, corner=4, depth=4)
    for x in (20, w - 20):
        a.shape(rect(x - 10, 10, x + 10, h - 10), WOOD_DARK, outline=DETAIL * 1.2, corner=4, depth=4)
    hide = chaikin([(w / 2, 46), (w / 2 + 60, 60), (w / 2 + 110, 50), (w / 2 + 96, 130), (w / 2 + 104, 230), (w / 2 + 112, 296), (w / 2 + 50, 280), (w / 2, 296), (w / 2 - 50, 280), (w / 2 - 112, 296), (w / 2 - 104, 230), (w / 2 - 96, 130), (w / 2 - 110, 50), (w / 2 - 60, 60)], True, 2)
    a.shape(hide, HIDE, depth=8, light_k=0.35, detail=lambda art, p: [art.ink([(w / 2 + art.rng.uniform(-80, 80), y), (w / 2 + art.rng.uniform(-80, 80), y + 6)], FINE, color=shade(HIDE, 0.35), alpha=0.6) for y in range(70, 290, 22)])
    # Cords lashing it to the frame.
    for x, y in ((w / 2 + 110, 50), (w / 2 - 110, 50), (w / 2 + 112, 296), (w / 2 - 112, 296), (w / 2 + 104, 170), (w / 2 - 104, 170)):
        fx = 20 if x < w / 2 else w - 20
        a.ink([(x, y), (fx, y)], FINE * 1.3, color=rgb("#d8c08a"))
    return a.image()


CRAFT = {
    "Forge": forge,
    "Bellows": bellows,
    "Anvil on Stump": anvil_stump,
    "Quench Trough": quench_trough,
    "Grindstone": grindstone,
    "Crucible": crucible,
    "Ingots": ingots,
    "Coal Pile": coal_pile,
    "Workbench": workbench,
    "Sawhorse": sawhorse,
    "Chopping Block": chopping_block,
    "Lumber Stack": lumber_stack,
    "Sawdust": sawdust,
    "Tool Chest": tool_chest,
    "Tool Rack": tool_rack,
    "Loom": loom,
    "Spinning Wheel": spinning_wheel,
    "Pottery Wheel": pottery_wheel,
    "Kiln": kiln,
    "Tanning Rack": tanning_rack,
    "Hammer": tool(hammer_at, 200, 160, -0.5, 30, 130),
    "Tongs": tool(tongs_at, 200, 160, -0.5, 30, 130),
    "Saw": tool(saw_at, 240, 150, -0.25, 20, 110),
    "Axe": tool(axe_at, 250, 220, -0.6, 30, 190),
    "Shovel": tool(shovel_at, 290, 140, -0.3, 30, 110),
    "Pickaxe": tool(pickaxe_at, 230, 200, -0.5, 30, 170),
}
