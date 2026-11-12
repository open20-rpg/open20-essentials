"""SRD 5.2.1 tools (batch SRD): artisan's tools, kits, gaming sets and
musical instruments. Each kit is an open case, tray or tool roll with its
characteristic tools visible from above, so kits tell apart at a glance.
Top-down, same pen style (red = colorable: roll linings, velvet, drum and
bag skins)."""

import math

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, dot, open_lid, soft_shadow
from obj_craft import STEEL, handle, hammer_at, rot_pts, saw_at, tongs_at
from obj_magic import GLASS, PARCH, flask
from obj_nature import leaf, tube
from obj_tavern import CERAMIC, GOLD, INKC, cards_at, inkwell_at, paper_at
from pen import DETAIL, FINE, INK, OUTLINE, Art, chaikin, ellipse, mix, rect, rgb, shade, tint

LEATHER = rgb("#8a5a3a")
LEATHER_DARK = rgb("#5e3c26")
CANVAS = rgb("#cbbd99")
CLAY = rgb("#b47a52")
THREAD = rgb("#e6dcc4")
COPPER = rgb("#c27a4a")
O = DETAIL * 1.6  # outline weight of small tools


def L(x, y, ang):
    """Local frame: points given as offsets (along, across) from (x, y),
    rotated by `ang`."""
    c, s = math.cos(ang), math.sin(ang)
    return lambda pts: [(x + dx * c - dy * s, y + dx * s + dy * c) for dx, dy in pts]


def metal(a, pts, color=STEEL, outline=O, depth=2):
    a.shape(pts, color, outline=outline, corner=1, wob=0.1, depth=depth, light_k=0.55, mottle=0, var=0.08)


def thin(a, pts, w, color, edge=4.5):
    """A thin rod: an ink line with a colored core."""
    a.ink(pts, w + edge, color=INK, taper=False, wob=0, var=0.05)
    a.ink(pts, w, color=color, taper=False, wob=0, var=0.05)


# -- small tools (any angle) ---------------------------------------------------------------------


def chisel_at(a, x, y, ang, L_=110, w=12, gouge=False):
    t = L(x, y, ang)
    handle(a, *t([(0, 0)])[0], *t([(L_ * 0.5, 0)])[0], 10)
    metal(a, t([(L_ * 0.48, -4), (L_ * 0.62, -4), (L_ * 0.62, 4), (L_ * 0.48, 4)]), BRASS)
    if gouge:
        metal(a, t([(L_ * 0.62, -3), (L_ - 8, -w / 2), (L_, -w / 2 + 2), (L_ + 2, 0), (L_, w / 2 - 2), (L_ - 8, w / 2), (L_ * 0.62, 3)]))
        a.ink(t([(L_ - 14, -w / 4), (L_ - 4, 0), (L_ - 14, w / 4)]), FINE, color=shade(STEEL, 0.5), wob=0)
    else:
        metal(a, t([(L_ * 0.62, -3), (L_ - 6, -w / 2), (L_, -w / 2), (L_, w / 2), (L_ - 6, w / 2), (L_ * 0.62, 3)]))
        a.ink(t([(L_ - 9, -w / 2 + 2), (L_ - 9, w / 2 - 2)]), FINE, color=tint(STEEL, 0.6), wob=0)


def knife_at(a, x, y, ang, L_=110, handle_c=WOOD_DARK, curved=True):
    t = L(x, y, ang)
    a.shape(t(rect(0, -6, L_ * 0.42, 6)), handle_c, outline=O, corner=4, depth=2, mottle=0)
    for k in (0.12, 0.3):
        dot(a, *t([(L_ * k, 0)])[0], 2, BRASS)
    b = [(L_ * 0.42, -6), (L_ * 0.8, -6), (L_, -1), (L_ * 0.9, 5), (L_ * 0.42, 6)] if curved else [(L_ * 0.42, -5), (L_, -2), (L_, 1), (L_ * 0.42, 5)]
    metal(a, t(b))
    a.ink(t([(L_ * 0.46, -2), (L_ * 0.82, -2)]), FINE * 0.9, color=tint(STEEL, 0.6), alpha=0.8, wob=0)


def round_knife_at(a, x, y, ang):
    """A leatherworker's head knife: a half-moon blade on a short handle."""
    t = L(x, y, ang)
    a.shape(t(rect(0, -6, 46, 6)), WOOD_DARK, outline=O, corner=4, depth=2, mottle=0)
    metal(a, t([(46, -4), (58, -4), (58, 4), (46, 4)]))
    metal(a, t([(58, -30)] + [(58 + 24 * math.sin(math.pi * k / 14), -30 * math.cos(math.pi * k / 14)) for k in range(15)] + [(58, 30)]))


def awl_at(a, x, y, ang, L_=80, knob=WOOD):
    t = L(x, y, ang)
    thin(a, t([(14, 0), (L_, 0)]), 2.5, STEEL)
    a.shape(t(ellipse(10, 0, 16, 10, 24)), knob, outline=O, depth=2, light_k=0.5, mottle=0)


def needle_at(a, x, y, ang, L_=50):
    t = L(x, y, ang)
    thin(a, t([(0, 0), (L_, 0)]), 1.6, STEEL, 3)
    a.ink(t(ellipse(4, 0, 3, 1.4, 10)), FINE * 0.7, closed=True, color=INK)


def file_at(a, x, y, ang, L_=110):
    t = L(x, y, ang)
    handle(a, *t([(0, 0)])[0], *t([(34, 0)])[0], 10)
    b = t([(34, -6), (L_ - 10, -5), (L_, 0), (L_ - 10, 5), (34, 6)])
    a.shape(b, IRON, outline=O, corner=1, wob=0.1, depth=2, light_k=0.4, mottle=0, detail=lambda art, p: [art.ink(t([(k, -6), (k + 6, 6)]), FINE * 0.7, color=shade(IRON, 0.5), alpha=0.8, wob=0) for k in range(40, int(L_) - 10, 5)])


def pliers_at(a, x, y, ang, L_=90, color=IRON):
    t = L(x, y, ang)
    for s in (-1, 1):
        thin(a, t([(0, s * 12), (L_ * 0.55, s * 1), (L_, s * 2)]), 5, color)
    dot(a, *t([(L_ * 0.55, 0)])[0], 4.5, tint(color, 0.3))
    for s in (-1, 1):
        a.ink(t([(2, s * 12), (L_ * 0.35, s * 6)]), 9, color=INK, taper=False, wob=0)
        a.ink(t([(2, s * 12), (L_ * 0.35, s * 6)]), 5, color=LEATHER_DARK, taper=False, wob=0)


def mallet_at(a, x, y, ang, L_=110, head=WOOD_LIGHT):
    t = L(x, y, ang)
    handle(a, *t([(0, 0)])[0], *t([(L_, 0)])[0], 9)
    a.shape(t(rect(L_ - 18, -30, L_ + 18, 30)), head, outline=O, corner=6, depth=3, light_k=0.4, mottle=0)
    a.ink(t([(L_ - 6, -24), (L_ - 6, 24)]), FINE, color=shade(head, 0.45), alpha=0.7)


def brush_at(a, x, y, ang, L_=110, paint=None, wide=False):
    t = L(x, y, ang)
    handle(a, *t([(0, 0)])[0], *t([(L_ * 0.65, 0)])[0], 6, WOOD_DARK if wide else WOOD)
    w = 9 if wide else 5
    metal(a, t(rect(L_ * 0.62, -w, L_ * 0.76, w)), BRASS, outline=FINE * 1.4, depth=1)
    tip = paint or rgb("#3a2e28")
    a.shape(t([(L_ * 0.76, -w), (L_ * 0.95, -w + 1), (L_, 0), (L_ * 0.95, w - 1), (L_ * 0.76, w)]), rgb("#5a4030"), outline=FINE * 1.4, corner=2, depth=1, mottle=0)
    if paint:
        a.shape(t([(L_ * 0.88, -w + 1), (L_ * 0.96, -w + 2), (L_, 0), (L_ * 0.96, w - 2), (L_ * 0.88, w - 1)]), tip, outline=0, corner=2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)


def quill_at(a, x, y, ang, L_=110):
    t = L(x, y, ang)
    a.ink(t([(0, 0), (L_, 0)]), DETAIL * 1.4, color=INK)
    vane = chaikin(t([(L_ * 0.3, 0), (L_ * 0.45, -10), (L_ * 0.95, -12), (L_ * 1.05, -4), (L_ * 0.9, 6), (L_ * 0.45, 6)]), True, 2)
    a.shape(vane, rgb("#f2efe6"), outline=DETAIL, corner=0, depth=1, mottle=0)
    a.ink(t([(L_ * 0.3, 0), (L_ * 1.02, -4)]), FINE, color=shade(rgb("#f2efe6"), 0.4))


def jar_at(a, x, y, r, lid=WOOD, body=GLASS, content=None):
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r, 32), body, outline=DETAIL * 1.2, depth=3, light_k=0.5, mottle=0)
    if content:
        a.shape(ellipse(x, y, r * 0.8, r * 0.8, 28), content, outline=0, depth=2, shade_k=0.3, light_k=0.2, ao=0, mottle=0)
    if lid:
        a.shape(ellipse(x, y, r * 0.66, r * 0.66, 28), lid, outline=FINE * 1.4, depth=2, light_k=0.4, mottle=0)


def pot_at(a, x, y, r, color, lid=False):
    """A small ointment/paint pot, open (color inside) or capped."""
    soft_shadow(a, (x, y), r, 2, 3, 0.3, 2)
    a.shape(ellipse(x, y, r, r, 28), CERAMIC, outline=DETAIL * 1.1, depth=2, light_k=0.4, mottle=0)
    a.shape(ellipse(x, y, r * 0.72, r * 0.72, 24), color, outline=FINE, depth=1.5, shade_k=0.25, light_k=0.3, ao=0.2, mottle=0)


def spool_at(a, x, y, ang, color=THREAD, L_=34):
    t = L(x, y, ang)
    soft_shadow(a, t(rect(0, -14, L_, 14)), dx=2, dy=3, alpha=0.3, blur=2)
    a.shape(t(rect(5, -10, L_ - 5, 10)), color, outline=FINE * 1.4, corner=2, depth=2, light_k=0.4, mottle=0, detail=lambda art, p: [art.ink(t([(k, -10), (k, 10)]), FINE * 0.6, color=shade(color, 0.35), alpha=0.7, wob=0) for k in range(8, L_ - 5, 3)])
    for e in (0, L_ - 6):
        a.shape(t(rect(e, -14, e + 6, 14)), WOOD_LIGHT, outline=FINE * 1.4, corner=2, depth=1, mottle=0)


def yarn_at(a, x, y, r, color):
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)

    def wraps(art, p):
        for k in range(7):
            u = art.rng.uniform(0, math.pi)
            dx, dy = math.cos(u), math.sin(u)
            o = art.rng.uniform(-r * 0.6, r * 0.6)
            art.ink([(x - dx * r + dy * o, y - dy * r - dx * o), (x + dx * r + dy * o, y + dy * r - dx * o)], FINE * 0.9, color=shade(color, 0.4), alpha=0.7, wob=0.5)

    a.shape(ellipse(x, y, r, r, 32), color, outline=DETAIL * 1.1, depth=3, light_k=0.4, mottle=0, detail=wraps)


def coin_at(a, x, y, r=8, color=GOLD):
    a.shape(ellipse(x, y, r, r, 20), color, outline=FINE * 1.3, corner=0, wob=0.1, depth=1.5, shade_k=0.35, light_k=0.5, ao=0, mottle=0)
    a.ink(ellipse(x, y, r * 0.6, r * 0.6, 16), FINE * 0.7, closed=True, color=shade(color, 0.4), alpha=0.7, wob=0.1)


def gem_at(a, x, y, r, color):
    pts = [(x + r * math.cos(k * math.pi / 3 + 0.3), y + r * math.sin(k * math.pi / 3 + 0.3)) for k in range(6)]
    a.shape(pts, color, outline=FINE * 1.4, corner=0, wob=0.1, depth=2, shade_k=0.4, light_k=0.6, ao=0, mottle=0)
    a.ink([pts[0], pts[3]], FINE * 0.6, color=tint(color, 0.6), alpha=0.8, wob=0)
    dot(a, x - r * 0.3, y - r * 0.3, r * 0.2, (255, 255, 250), 0.9)


def dividers_at(a, x, y, ang, L_=100, spread=0.22):
    for s in (-1, 1):
        u = ang + s * spread / 2
        thin(a, [(x, y), (x + L_ * math.cos(u), y + L_ * math.sin(u))], 3.5, BRASS)
    dot(a, x, y, 7, BRASS)
    a.ink(ellipse(x, y, 7, 7, 16), FINE * 1.2, closed=True, color=INK)


def square_at(a, x, y, ang, L1=110, L2=70, w=10, color=STEEL):
    t = L(x, y, ang)
    metal(a, t([(0, 0), (L1, 0), (L1, w), (w, w), (w, L2), (0, L2)]), color)
    for k in range(20, int(L1), 12):
        a.ink(t([(k, 0), (k, 4)]), FINE * 0.7, color=INK, alpha=0.8, wob=0)


def cloth_at(a, x0, y0, x1, y1, color, folds=2, corner=8):
    def fold(art, p):
        for k in range(folds):
            yy = y0 + (y1 - y0) * (k + 1) / (folds + 1)
            art.ink([(x0 + 6, yy + art.rng.uniform(-4, 4)), (x1 - 6, yy + art.rng.uniform(-4, 4))], FINE * 1.1, color=shade(color, 0.4), alpha=0.6, wob=1.2)

    soft_shadow(a, rect(x0, y0, x1, y1), dx=4, dy=5)
    return a.shape(rect(x0, y0, x1, y1), color, outline=DETAIL * 1.3, corner=corner, depth=5, light_k=0.3, detail=fold)


# -- containers ----------------------------------------------------------------------------------


def case(a, x0, y0, x1, y1, wood=WOOD, lining=RED, lid=40, metal_=BRASS, cells=()):
    """An open box from above: the lid flung open behind (top), the box with
    its rim, a lined floor and wooden dividers (`cells`: x positions, or
    (x, y0, y1) tuples)."""
    if lid:
        open_lid(a, x0, y0 - lid, x1, y0 + 10, wood, metal_, n=2)
    soft_shadow(a, rect(x0, y0, x1, y1), dx=6, dy=7, alpha=0.4, blur=5)
    board(a, x0, y0, x1, y1, wood, n=1, corner=7, depth=6)
    rim = 10
    a.shape(rect(x0 + rim, y0 + rim, x1 - rim, y1 - rim), lining, outline=DETAIL, corner=4, depth=7, shade_k=0.6, light_k=0.0, ao=0.6)
    for c in cells:
        if isinstance(c, tuple):
            if len(c) == 3:
                cx, cy0, cy1 = c
                a.shape(rect(cx - 3, cy0, cx + 3, cy1), wood, outline=FINE * 1.4, corner=1, depth=2, mottle=0)
            else:
                cy, cx0, cx1, _ = c
                a.shape(rect(cx0, cy - 3, cx1, cy + 3), wood, outline=FINE * 1.4, corner=1, depth=2, mottle=0)
        else:
            a.shape(rect(c - 3, y0 + rim, c + 3, y1 - rim), wood, outline=FINE * 1.4, corner=1, depth=2, mottle=0)
    cx = (x0 + x1) / 2
    a.shape(rect(cx - 12, y1 - 6, cx + 12, y1 + 6), metal_, outline=DETAIL, corner=3, depth=2, light_k=0.5, mottle=0)


def roll_kit(a, x0, y0, x1, y1, color=RED, pocket=0.45, ties=True):
    """A tool roll laid open: cloth with a folded-back top flap; returns a
    function drawing its pocket layer, to call after the tools so their lower
    ends sit in the pockets."""
    soft_shadow(a, rect(x0, y0, x1, y1), dx=5, dy=6, alpha=0.4, blur=4)
    a.shape(rect(x0, y0, x1, y1), color, outline=DETAIL * 1.4, corner=8, depth=5, shade_k=0.4, light_k=0.25)
    a.shape(rect(x0 - 4, y0 - 6, x1 + 4, y0 + 18), shade(color, 0.15), outline=DETAIL * 1.4, corner=9, depth=5, light_k=0.35)  # rolled edge
    py = y1 - (y1 - y0) * pocket

    def pockets(n=6):
        a.shape(rect(x0 + 4, py, x1 - 4, y1 - 4), shade(color, 0.2), outline=DETAIL * 1.2, corner=4, depth=4, shade_k=0.3, light_k=0.4)
        for k in range(1, n):
            xx = x0 + (x1 - x0) * k / n
            a.ink([(xx, py + 3), (xx, y1 - 7)], FINE, color=tint(color, 0.45), alpha=0.85, wob=0.3)
        a.ink([(x0 + 10, py + 6), (x1 - 10, py + 6)], FINE * 0.9, color=tint(color, 0.45), alpha=0.7, wob=0.3)
        if ties:
            for dy in (-6, 6):
                a.ink([(x1 - 2, (y0 + y1) / 2 + dy), (x1 + 26, (y0 + y1) / 2 + dy * 3 + 8)], DETAIL * 1.6, color=INK, taper=True)
                a.ink([(x1 - 2, (y0 + y1) / 2 + dy), (x1 + 26, (y0 + y1) / 2 + dy * 3 + 8)], DETAIL * 0.7, color=LEATHER, taper=True)

    return pockets


def tray(a, x0, y0, x1, y1, wood=WOOD, handle_bar=True):
    """A carpenter's tote: a long open tray, divided by a handle board."""
    soft_shadow(a, rect(x0, y0, x1, y1), dx=6, dy=7, alpha=0.4, blur=5)
    board(a, x0, y0, x1, y1, wood, n=1, corner=6, depth=6)
    a.shape(rect(x0 + 9, y0 + 9, x1 - 9, y1 - 9), shade(wood, 0.35), outline=DETAIL, corner=3, depth=6, shade_k=0.5, light_k=0, ao=0.6)
    if handle_bar:
        my = (y0 + y1) / 2
        return lambda: board(a, x0 + 4, my - 7, x1 - 4, my + 7, WOOD_LIGHT, n=1, corner=3, depth=3)
    return lambda: None


def art(w, h, seed):
    return Art(w, h, seed)


# -- artisan's tools -----------------------------------------------------------------------------


def alchemists_supplies(seed=7001):
    w, h = 280, 230
    a = art(w, h, seed)
    case(a, 16, 60, w - 16, h - 14, WOOD_DARK, RED, cells=(150,))
    liquids = [rgb("#4f8fd0"), rgb("#6fb84a"), rgb("#e6b84a"), rgb("#a86ad0"), rgb("#4fc2c0"), rgb("#e07a3a")]
    for i, (x, y) in enumerate(((48, 98), (88, 98), (128, 98), (48, 140), (88, 140), (128, 140))):
        flask(a, x, y, 15, liquids[i])
    # Mortar, a test-tube rack and a glass beaker in the right compartment.
    a.shape(ellipse(192, 110, 22, 22, 32), STONE, outline=DETAIL * 1.2, depth=3)
    a.shape(ellipse(192, 110, 14, 14, 28), shade(STONE, 0.35), outline=FINE * 1.2, depth=3, shade_k=0, light_k=0, ao=0.5)
    thin(a, [(186, 116), (214, 90)], 5, tint(STONE, 0.1))
    a.shape(rect(172, 150, 248, 172), WOOD_LIGHT, outline=DETAIL, corner=3, depth=2, mottle=0)
    for k, c in enumerate(liquids[:4]):
        dot(a, 184 + k * 18, 161, 7, INK)
        dot(a, 184 + k * 18, 161, 5, c)
    jar_at(a, 236, 112, 15, lid=None, body=GLASS, content=rgb("#c8e0a8"))
    return a.image()


def brewers_supplies(seed=7002):
    w, h = 300, 240
    a = art(w, h, seed)
    cloth_at(a, 12, 20, w - 12, h - 12, CANVAS, folds=0)
    # A big glass carboy with its airlock, a siphon hose, a funnel, hops and
    # a mash paddle.
    soft_shadow(a, (90, 100), 58, 5, 6, 0.35, 5)
    a.shape(ellipse(90, 100, 58, 58, 48), GLASS, outline=OUTLINE * 0.8, depth=5, light_k=0.6, mottle=0)
    a.shape(ellipse(90, 100, 48, 48, 40), rgb("#d9a441"), outline=0, depth=3, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    a.shape(ellipse(90, 100, 18, 18, 24), GLASS, outline=DETAIL, depth=2, light_k=0.5, mottle=0)
    dot(a, 90, 100, 10, rgb("#b88a5a"))
    a.ink([(68, 70), (78, 62)], FINE * 2, color=(250, 250, 245), alpha=0.85)
    hose = chaikin([(98, 96), (150, 70), (200, 80), (230, 130), (210, 190)], False, 3)
    a.ink(hose, 10, color=INK, taper=False)
    a.ink(hose, 6, color=rgb("#d8cfb4"), taper=False)
    # Funnel.
    a.shape(ellipse(230, 64, 30, 30, 36), COPPER, outline=DETAIL * 1.3, depth=3, light_k=0.5, mottle=0)
    a.shape(ellipse(230, 64, 8, 8, 16), shade(COPPER, 0.6), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    for k in range(12):
        u = a.rng.uniform(0, 6.28)
        d = a.rng.uniform(0, 26)
        a.shape(ellipse(70 + d * math.cos(u), 190 + d * math.sin(u) * 0.6, 9, 7, 16, rot=a.rng.uniform(0, 3)), rgb("#8fb350"), outline=FINE * 1.2, depth=1.5, light_k=0.4, ao=0, mottle=0)
    handle(a, 150, 210, 270, 160, 9, WOOD_LIGHT)
    a.shape(rot_pts(rect(254, 140, 290, 168), 272, 154, -0.4), WOOD_LIGHT, outline=O, corner=6, depth=2, mottle=0)
    return a.image()


def calligraphers_supplies(seed=7003):
    w, h = 280, 210
    a = art(w, h, seed)
    board(a, 12, 14, w - 12, h - 14, WOOD, n=1, corner=8, depth=6)
    paper_at(a, 104, 104, 130, 150, -0.06, lines=False)
    # Flourished letters in ink on the sheet.
    for k in range(5):
        y = 56 + k * 22
        pts = [(52 + i * 8, y + 6 * math.sin(i * 1.3 + k)) for i in range(12 - (k % 2) * 3)]
        a.ink(pts, FINE * 1.5, color=INKC, alpha=0.85, wob=0.6)
    a.ink([(48, 44), (60, 30), (64, 52)], DETAIL, color=rgb("#7a2030"), alpha=0.9)
    inkwell_at(a, 210, 150)
    pot_at(a, 214, 50, 14, rgb("#7a2030"))
    pot_at(a, 244, 82, 12, rgb("#2a3f78"))
    quill_at(a, 182, 120, -1.3, 70)
    knife_at(a, 176, 186, -0.05, 80, curved=False)
    return a.image()


def carpenters_tools(seed=7004):
    w, h = 320, 210
    a = art(w, h, seed)
    bar = tray(a, 10, 14, w - 10, h - 14)
    saw_at(a, 26, 58, 0.0, 200)
    bar()
    hammer_at(a, 30, 150, -0.05, 120)
    chisel_at(a, 170, 136, 0.0, 120)
    chisel_at(a, 170, 166, 0.0, 110, w=8)
    # A block plane with its blade and knob, beside the hammer.
    a.shape(rect(232, 74, 296, 106), WOOD_LIGHT, outline=O, corner=6, depth=3, mottle=0)
    a.shape(rect(258, 78, 268, 102), STEEL, outline=FINE * 1.4, corner=1, depth=1, mottle=0)
    dot(a, 282, 90, 6, WOOD_DARK)
    a.ink(ellipse(282, 90, 6, 6, 14), FINE, closed=True)
    return a.image()


def cartographers_tools(seed=7005):
    w, h = 300, 230
    a = art(w, h, seed)
    board(a, 10, 12, w - 10, h - 12, WOOD_DARK, n=1, corner=8, depth=6)

    def map_marks(art_, p):
        coast = chaikin([(40, 130), (70, 90), (110, 100), (140, 60), (180, 80), (200, 120), (170, 160), (110, 170), (60, 160)], True, 2)
        art_.ink(coast, DETAIL, closed=True, color=rgb("#5a4632"), alpha=0.85)
        for x, y in ((100, 130), (150, 110), (120, 145)):
            art_.ink([(x - 6, y + 4), (x, y - 6), (x + 6, y + 4)], FINE * 1.2, color=rgb("#5a4632"), alpha=0.8)
        art_.ink([(60, 70), (230, 190)], FINE, color=rgb("#9a3a2a"), alpha=0.6, wob=0.2)
        cx, cy = 210, 60
        for u in range(4):
            ang = u * math.pi / 2
            art_.ink([(cx, cy), (cx + 16 * math.cos(ang), cy + 16 * math.sin(ang))], FINE * 1.2, color=rgb("#5a4632"))

    soft_shadow(a, rect(28, 30, 248, 196), dx=4, dy=5)
    a.shape(rect(28, 30, 248, 196), PARCH, outline=DETAIL, corner=3, depth=3, shade_k=0.2, light_k=0.2, detail=map_marks)
    dividers_at(a, 200, 150, 0.6, 90)
    handle(a, 40, 210, 200, 200, 7, WOOD_LIGHT)  # ruler
    for k in range(50, 196, 12):
        a.ink([(k, 202 - (k - 40) * 0.0625), (k, 208 - (k - 40) * 0.0625)], FINE * 0.7, color=INK, wob=0)
    inkwell_at(a, 262, 160)
    return a.image()


# A foot outline (heel at 0, toe at 110): narrow heel, waisted arch, wide
# ball and a rounded toe, so it reads as a shoe sole, not a pebble.
FOOT = [(0, -11), (14, -15), (40, -12), (62, -19), (88, -22), (106, -14), (112, 0), (106, 14), (88, 20), (62, 16), (40, 8), (14, 14), (0, 10)]


def shoe_last_at(a, x, y, ang, color=WOOD_LIGHT):
    t = L(x, y, ang)
    sole = chaikin(t(FOOT), True, 2)
    soft_shadow(a, sole, dx=3, dy=4)
    a.shape(sole, color, outline=DETAIL * 1.3, corner=0, depth=4, light_k=0.45, mottle=0.04)
    dot(a, *t([(14, 0)])[0], 4, IRON)  # the hole for the last's jack
    a.ink(t([(30, 0), (90, -2)]), FINE, color=shade(color, 0.4), alpha=0.6)


def cobblers_tools(seed=7006):
    w, h = 280, 220
    a = art(w, h, seed)
    cloth_at(a, 10, 14, w - 10, h - 12, LEATHER_DARK, folds=0)
    shoe_last_at(a, 30, 70, 0.05)
    # A half-made boot sole and an upper, cut from leather.
    t = L(146, 64, -0.05)
    sole = chaikin(t(FOOT), True, 2)
    a.shape(sole, rgb("#b07a4a"), outline=DETAIL * 1.3, corner=0, depth=3, light_k=0.3)
    inner = chaikin(t([(x * 0.86 + 7, y * 0.7) for x, y in FOOT]), True, 2)
    for k in range(0, len(inner), 4):
        dot(a, *inner[k], 1.6, INK, 0.8)
    hammer_at(a, 40, 160, -0.1, 100)
    awl_at(a, 160, 130, 0.2, 80)
    spool_at(a, 220, 160, 0.4)
    needle_at(a, 150, 190, -0.2, 50)
    for k in range(6):
        dot(a, 120 + a.rng.uniform(0, 30), 120 + a.rng.uniform(0, 20), 2.6, IRON)  # tacks
    return a.image()


def cooks_utensils(seed=7007):
    w, h = 300, 220
    a = art(w, h, seed)
    cloth_at(a, 10, 14, w - 10, h - 12, RED, folds=1)
    # An iron pot, a ladle, a cleaver, a spoon and a fork.
    soft_shadow(a, (84, 86), 52, 5, 6, 0.4, 5)
    a.shape(ellipse(84, 86, 52, 52, 48), IRON, outline=OUTLINE * 0.8, depth=5, light_k=0.4, mottle=0)
    a.shape(ellipse(84, 86, 40, 40, 40), shade(IRON, 0.5), outline=DETAIL, depth=5, shade_k=0, light_k=0, ao=0.5)
    for s in (-1, 1):
        a.ink([(84 + s * 52, 80), (84 + s * 62, 86), (84 + s * 52, 92)], DETAIL * 1.4, color=INK, taper=False)
    thin(a, [(150, 60), (250, 40)], 6, STEEL)
    a.shape(ellipse(258, 38, 20, 18, 24), STEEL, outline=O, depth=2, light_k=0.5, mottle=0)
    a.shape(ellipse(258, 38, 13, 11, 20), shade(STEEL, 0.4), outline=0, depth=1, shade_k=0, light_k=0, ao=0.4, mottle=0)
    t = L(150, 120, 0.1)
    a.shape(t(rect(0, -7, 44, 7)), WOOD_DARK, outline=O, corner=4, depth=2, mottle=0)
    metal(a, t([(44, -10), (122, -14), (126, 20), (44, 10)]))
    dot(a, *t([(112, -4)])[0], 4, INK)
    handle(a, 40, 180, 140, 170, 7, WOOD_LIGHT)
    a.shape(ellipse(150, 169, 14, 10, 20, rot=-0.1), WOOD_LIGHT, outline=O, depth=2, mottle=0)
    thin(a, [(170, 190), (240, 182)], 4, STEEL)
    for k in (-6, -2, 2, 6):
        thin(a, [(240, 182 + k * 0.9), (264, 180 + k * 1.3)], 1.6, STEEL, 3)
    return a.image()


def glassblowers_tools(seed=7008):
    w, h = 340, 200
    a = art(w, h, seed)
    cloth_at(a, 10, 14, w - 10, h - 12, LEATHER, folds=0)
    # The long blowpipe with a glowing gather at its tip.
    thin(a, [(26, 60), (270, 50)], 8, IRON, 6)
    a.shape(ellipse(22, 60, 10, 12, 20), WOOD, outline=O, depth=2, mottle=0)
    from obj_magic import glow

    glow(a, 294, 50, 40, rgb("#ffb24a"), 0.5)
    a.shape(ellipse(294, 50, 26, 22, 32), rgb("#f2a03a"), outline=DETAIL * 1.3, depth=4, shade_k=0.3, light_k=0.6, mottle=0)
    dot(a, 288, 44, 8, rgb("#ffe7a8"))
    # Jacks (big tweezers), shears, a paddle and finished pieces.
    tongs_at(a, 30, 120, 0.04, 140)
    pliers_at(a, 190, 110, 0.3, 80)
    a.shape(rect(30, 150, 140, 178), WOOD_LIGHT, outline=O, corner=6, depth=2, mottle=0)
    for x, y, c in ((230, 160, rgb("#7fc0c8")), (270, 140, rgb("#9ad08a")), (300, 170, rgb("#5f8fd0"))):
        soft_shadow(a, (x, y), 14, 3, 4, 0.3, 3)
        a.shape(ellipse(x, y, 14, 14, 24), c, outline=DETAIL, depth=3, light_k=0.7, mottle=0)
        a.shape(ellipse(x, y, 6, 6, 16), shade(c, 0.3), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def jewelers_tools(seed=7009):
    w, h = 240, 220
    a = art(w, h, seed)
    case(a, 14, 60, w - 14, h - 14, WOOD_DARK, RED, metal_=GOLD, cells=((120, 70, 206),))
    # Loupe, fine pliers, files, a tiny hammer, gems and a ring.
    a.shape(ellipse(52, 102, 18, 18, 28), rgb("#2a2a30"), outline=DETAIL, depth=2, light_k=0.4, mottle=0)
    a.shape(ellipse(52, 102, 11, 11, 20), GLASS, outline=FINE * 1.2, depth=1, light_k=0.7, mottle=0)
    pliers_at(a, 32, 150, -0.15, 74)
    file_at(a, 30, 186, -0.05, 86)
    for x, y, c in ((150, 96, rgb("#d0465a")), (184, 92, rgb("#5fb0d8")), (164, 124, rgb("#7ccf8a")), (198, 130, rgb("#f2d24a")), (148, 156, rgb("#a86ad0"))):
        gem_at(a, x, y, 9, c)
    a.ink(ellipse(186, 176, 14, 14, 24), 9, closed=True, color=INK)
    a.ink(ellipse(186, 176, 14, 14, 24), 5, closed=True, color=GOLD)
    gem_at(a, 186, 162, 6, rgb("#5fb0d8"))
    return a.image()


def leatherworkers_tools(seed=7010):
    w, h = 300, 230
    a = art(w, h, seed)
    # A tanned hide with a pattern cut from it, the head knife, an awl,
    # waxed thread and a few stitching punches.
    hide = chaikin([(20, 40), (80, 20), (170, 30), (260, 18), (284, 80), (270, 160), (284, 210), (180, 216), (90, 206), (20, 214), (32, 130)], True, 2)
    soft_shadow(a, hide, dx=5, dy=6)

    def marks(art_, p):
        art_.ink(chaikin([(60, 70), (150, 66), (160, 120), (70, 126)], True, 1), FINE * 1.2, closed=True, color=shade(rgb("#c9a27a"), 0.45), alpha=0.8, wob=0.2)
        for k in range(12):
            dot(art_, 66 + k * 7.5, 76, 1.4, shade(rgb("#c9a27a"), 0.6), 0.8)

    a.shape(hide, rgb("#c9a27a"), outline=DETAIL * 1.6, corner=0, depth=6, light_k=0.3, detail=marks)
    round_knife_at(a, 170, 100, -0.4)
    awl_at(a, 40, 170, -0.1, 80)
    spool_at(a, 150, 170, 0.3, rgb("#e2cf8f"))
    mallet_at(a, 200, 200, -1.2, 80, rgb("#c0a080"))
    return a.image()


def masons_tools(seed=7011):
    w, h = 300, 220
    a = art(w, h, seed)
    # A cut stone block, a trowel, a point chisel, a hammer and a plumb line.
    soft_shadow(a, rect(170, 30, 280, 120), dx=6, dy=7)
    a.shape(rect(170, 30, 280, 120), STONE, outline=OUTLINE * 0.8, corner=5, depth=8, light_k=0.35, detail=lambda art_, p: [art_.ink([(180 + k * 14, 34), (176 + k * 14, 116)], FINE * 0.8, color=shade(STONE, 0.4), alpha=0.6) for k in range(7)])
    t = L(30, 80, -0.15)
    handle(a, *t([(0, 0)])[0], *t([(46, 0)])[0], 10)
    thin(a, t([(46, 0), (60, 0), (64, -10)]), 4, STEEL)
    metal(a, t([(56, -12), (110, -30), (140, -12), (110, 6)]))
    chisel_at(a, 40, 140, 0.05, 110, w=6)
    hammer_at(a, 160, 190, -0.15, 90)
    a.ink([(240, 140), (270, 200)], FINE * 1.2, color=THREAD)
    a.shape([(262, 196), (278, 196), (270, 214)], BRASS, outline=FINE * 1.4, corner=1, depth=2, mottle=0)
    return a.image()


def painters_supplies(seed=7012):
    w, h = 300, 220
    a = art(w, h, seed)
    # A small canvas on its stretcher, the palette with dabs of paint, the
    # brushes, a rag and paint pots.
    soft_shadow(a, rect(170, 20, 286, 130), dx=5, dy=6)
    a.shape(rect(170, 20, 286, 130), WOOD_LIGHT, outline=DETAIL * 1.3, corner=3, depth=4)
    a.shape(rect(178, 28, 278, 122), rgb("#efe7d2"), outline=FINE * 1.3, corner=1, depth=2, shade_k=0.1, light_k=0, ao=0.2, detail=lambda art_, p: (art_.shape(chaikin([(178, 90), (210, 70), (240, 84), (278, 66), (278, 122), (178, 122)], True, 2), rgb("#8fb06a"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0), art_.shape(ellipse(250, 48, 12, 12, 20), rgb("#f0c44a"), outline=0, depth=1, shade_k=0, light_k=0, ao=0)))
    pal = chaikin([(20, 60), (60, 30), (130, 34), (160, 70), (150, 120), (110, 140), (90, 120), (60, 130), (24, 110)], True, 3)
    soft_shadow(a, pal, dx=5, dy=6)
    a.shape(pal, rgb("#c9a06a"), outline=DETAIL * 1.4, corner=0, depth=4, light_k=0.35, mottle=0.04)
    a.shape(ellipse(52, 100, 9, 11, 16), rgb("#e8dfc8"), outline=FINE * 1.2, depth=1, shade_k=0, light_k=0, mottle=0)  # thumb hole
    for (x, y), c in zip(((50, 58), (80, 46), (112, 50), (136, 74), (130, 104), (100, 118), (80, 82)), ("#c8443a", "#e6b84a", "#4f8fd0", "#6fb84a", "#a86ad0", "#f2efe6", "#2a2a30")):
        a.shape(ellipse(x, y, 10, 8, 16, rot=a.rng.uniform(0, 3)), rgb(c), outline=FINE * 1.2, corner=0, depth=1.5, light_k=0.4, ao=0, mottle=0)
    brush_at(a, 30, 176, -0.2, 120, rgb("#4f8fd0"))
    brush_at(a, 40, 200, -0.08, 130, rgb("#c8443a"), wide=True)
    pot_at(a, 200, 170, 14, rgb("#e6b84a"))
    pot_at(a, 234, 160, 14, rgb("#4f8fd0"))
    pot_at(a, 264, 186, 14, rgb("#c8443a"))
    return a.image()


def potters_tools(seed=7013):
    w, h = 280, 210
    a = art(w, h, seed)
    board(a, 10, 12, w - 10, h - 12, WOOD_LIGHT, n=1, corner=8, depth=6)
    # A lump of wet clay with the cutting wire, ribs, a sponge and a pot.
    lump = chaikin([(40, 50), (90, 34), (130, 50), (126, 100), (80, 110), (36, 94)], True, 2)
    a.shape(lump, CLAY, outline=DETAIL * 1.4, corner=0, depth=6, light_k=0.3)
    a.ink([(60, 60), (110, 90)], FINE * 1.2, color=shade(CLAY, 0.45), alpha=0.8)
    a.ink([(30, 140), (120, 132)], FINE * 1.2, color=STEEL)
    for x, y in ((26, 141), (124, 131)):
        a.shape(ellipse(x, y, 5, 10, 16, rot=-0.1), WOOD, outline=FINE * 1.3, depth=1, mottle=0)
    a.shape(chaikin([(150, 40), (200, 36), (210, 60), (170, 70)], True, 2), WOOD, outline=O, corner=0, depth=2, mottle=0)
    a.shape(ellipse(170, 170, 22, 16, 24), rgb("#e2c46a"), outline=DETAIL, depth=2, light_k=0.3, mottle=0.1)
    soft_shadow(a, (226, 120), 30, 4, 5)
    a.shape(ellipse(226, 120, 30, 30, 40), CLAY, outline=DETAIL * 1.3, depth=4, light_k=0.4)
    a.shape(ellipse(226, 120, 18, 18, 32), shade(CLAY, 0.45), outline=FINE * 1.3, depth=3, shade_k=0, light_k=0, ao=0.5)
    for r in (24,):
        a.ink(ellipse(226, 120, r, r, 32), FINE, closed=True, color=shade(CLAY, 0.4), alpha=0.6)
    awl_at(a, 70, 186, -0.1, 70)
    return a.image()


def smiths_tools(seed=7014):
    w, h = 320, 200
    a = art(w, h, seed)
    pockets = roll_kit(a, 12, 20, w - 34, h - 10, LEATHER_DARK, pocket=0.4, ties=True)
    hammer_at(a, 40, 150, -1.5, 100)
    tongs_at(a, 92, 160, -1.52, 130)
    # Punches and a hardy (set chisel), standing in the pockets.
    for x in (150, 180, 210):
        thin(a, [(x, 160), (x, 66)], 8, IRON)
        a.ink([(x - 6, 70), (x + 6, 70)], FINE, color=tint(IRON, 0.4))
    file_at(a, 250, 170, -1.57, 120)
    pockets(6)
    return a.image()


def tinkers_tools(seed=7015):
    w, h = 270, 220
    a = art(w, h, seed)
    case(a, 14, 56, w - 14, h - 14, WOOD, rgb("#4a3a32"), metal_=BRASS, cells=(110, (136, 110, 256, 0)))

    def gear(x, y, r, color=BRASS, teeth=10):
        pts = []
        for k in range(teeth * 4):
            u = 2 * math.pi * k / (teeth * 4)
            rr = r if (k // 2) % 2 == 0 else r * 0.78
            pts.append((x + rr * math.cos(u), y + rr * math.sin(u)))
        a.shape(pts, color, outline=FINE * 1.5, corner=0, wob=0, depth=2, light_k=0.5, mottle=0)
        a.shape(ellipse(x, y, r * 0.28, r * 0.28, 16), shade(color, 0.5), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)

    gear(160, 94, 18)
    gear(196, 102, 12, COPPER, 8)
    gear(226, 90, 14, STEEL, 9)
    for k in range(9):
        dot(a, 150 + a.rng.uniform(0, 90), 156 + a.rng.uniform(0, 34), 2.6, a.rng.choice((IRON, BRASS, COPPER)))
    pliers_at(a, 30, 100, 0.25, 70)
    hammer_at(a, 34, 170, -0.25, 70)
    thin(a, [(56, 196), (96, 150)], 3, STEEL)
    a.shape(rot_pts(rect(46, 186, 70, 206), 58, 196, -0.85), WOOD_DARK, outline=FINE * 1.4, corner=4, depth=1, mottle=0)
    return a.image()


def shuttle_at(a, x, y, ang, L_=110):
    t = L(x, y, ang)
    body = chaikin(t([(0, 0), (20, -12), (L_ - 20, -12), (L_, 0), (L_ - 20, 12), (20, 12)]), True, 2)
    soft_shadow(a, body, dx=3, dy=4)
    a.shape(body, WOOD_LIGHT, outline=O, corner=0, depth=3, light_k=0.4, mottle=0)
    a.shape(t(rect(L_ * 0.3, -6, L_ * 0.7, 6)), shade(WOOD, 0.3), outline=FINE * 1.2, corner=3, depth=1, mottle=0)
    a.shape(t(rect(L_ * 0.35, -4, L_ * 0.65, 4)), THREAD, outline=FINE, corner=2, depth=1, mottle=0)


def weavers_tools(seed=7016):
    w, h = 300, 220
    a = art(w, h, seed)
    # A small backstrap/inkle loom with a strip being woven (red = colorable),
    # a shuttle, balls of yarn and a drop spindle.
    soft_shadow(a, rect(20, 30, 180, 190), dx=5, dy=6)
    for x0 in (20, 160):
        a.shape(rect(x0, 30, x0 + 20, 190), WOOD, outline=DETAIL * 1.3, corner=4, depth=3)
    for k in range(12):
        x = 50 + k * 10
        a.ink([(x, 34), (x, 186)], FINE * 0.9, color=THREAD, alpha=0.95, wob=0)
    a.shape(rect(44, 110, 156, 186), RED, outline=DETAIL * 1.2, corner=2, depth=3, light_k=0.3, detail=lambda art_, p: [art_.ink([(44, y), (156, y)], FINE * 0.8, color=shade(RED, 0.35), alpha=0.6, wob=0.3) for y in range(116, 186, 6)])
    for y in (36, 184):
        a.shape(rect(14, y - 7, 186, y + 7), WOOD_DARK, outline=DETAIL, corner=4, depth=2)
    shuttle_at(a, 60, 96, 0.0, 100)
    yarn_at(a, 230, 60, 24, rgb("#4f8fd0"))
    yarn_at(a, 262, 100, 18, rgb("#e6b84a"))
    yarn_at(a, 226, 120, 16, CERAMIC)
    thin(a, [(210, 200), (282, 160)], 4, WOOD_LIGHT)
    a.shape(ellipse(270, 167, 14, 14, 20), WOOD, outline=O, depth=2, mottle=0)
    a.shape(ellipse(240, 184, 10, 8, 16, rot=-0.5), THREAD, outline=FINE * 1.3, depth=1, mottle=0)
    return a.image()


def woodcarvers_tools(seed=7017):
    w, h = 300, 210
    a = art(w, h, seed)
    pockets = roll_kit(a, 12, 20, 170, h - 12, RED, pocket=0.4, ties=False)
    for k, (gouge, ww) in enumerate(((False, 10), (True, 12), (True, 8), (False, 6))):
        x = 34 + k * 36
        chisel_at(a, x, 186, -1.57, 130, w=ww, gouge=gouge)
    pockets(4)
    knife_at(a, 190, 190, -0.5, 90)
    # A block being carved into a little bird, and curled shavings.
    soft_shadow(a, rect(200, 30, 280, 110), dx=5, dy=6)
    a.shape(rect(200, 30, 280, 110), WOOD_LIGHT, outline=DETAIL * 1.4, corner=10, depth=6, light_k=0.4)
    bird = chaikin([(212, 80), (230, 54), (256, 50), (272, 62), (262, 80), (240, 96)], True, 2)
    a.shape(bird, tint(WOOD_LIGHT, 0.2), outline=DETAIL, corner=0, depth=3, light_k=0.5, mottle=0)
    dot(a, 258, 60, 2.5, INK)
    for _ in range(9):
        x, y = 230 + a.rng.uniform(-30, 50), 150 + a.rng.uniform(-20, 40)
        u = a.rng.uniform(0, 6.28)
        pts = [(x + 8 * math.cos(u + k * 0.7) * (1 - k / 12), y + 8 * math.sin(u + k * 0.7) * (1 - k / 12)) for k in range(10)]
        a.ink(pts, 4, color=INK)
        a.ink(pts, 2.2, color=tint(WOOD_LIGHT, 0.3))
    return a.image()


# -- other tools ---------------------------------------------------------------------------------


def hand_mirror_at(a, x, y, ang, r=26):
    t = L(x, y, ang)
    a.shape(t(rect(r - 2, -6, r + 46, 6)), BRASS, outline=O, corner=4, depth=2, mottle=0)
    soft_shadow(a, (x, y), r, 3, 4)
    a.shape(ellipse(x, y, r, r * 1.15, 32, rot=ang), BRASS, outline=DETAIL * 1.4, depth=3, light_k=0.5, mottle=0)
    a.shape(ellipse(x, y, r * 0.8, r * 0.95, 32, rot=ang), rgb("#cfe0e6"), outline=FINE * 1.3, depth=2, light_k=0.8, mottle=0)
    a.ink([(x - r * 0.4, y - r * 0.1), (x - r * 0.1, y - r * 0.5)], FINE * 2, color=(255, 255, 250), alpha=0.9)


def disguise_kit(seed=7018):
    w, h = 290, 240
    a = art(w, h, seed)
    case(a, 14, 66, w - 14, h - 14, WOOD_DARK, RED, metal_=BRASS)
    # Inside the lid, a mirror; in the box, a wig, a false beard, makeup pots
    # and powder brushes.
    a.shape(ellipse(w / 2, 40, 46, 20, 32), rgb("#cfe0e6"), outline=DETAIL * 1.2, depth=2, light_k=0.8, mottle=0)
    wig = chaikin([(36, 96), (80, 82), (124, 96), (130, 140), (110, 176), (90, 150), (60, 150), (40, 176), (28, 140)], True, 2)

    def curls(art_, p):
        for _ in range(16):
            x, y = 40 + art_.rng.uniform(0, 80), 96 + art_.rng.uniform(0, 70)
            art_.ink([(x, y), (x + 4, y + 6), (x, y + 12)], FINE * 1.1, color=shade(rgb("#d9b25a"), 0.45), alpha=0.8)

    a.shape(wig, rgb("#d9b25a"), outline=DETAIL * 1.3, corner=0, depth=5, light_k=0.35, detail=curls)
    beard = chaikin([(150, 150), (200, 146), (196, 176), (176, 200), (156, 176)], True, 2)
    a.shape(beard, rgb("#4a3328"), outline=DETAIL, corner=0, depth=3, light_k=0.3)
    for x, y, c in ((160, 100, rgb("#e8b8a0")), (196, 98, rgb("#c47a6a")), (232, 102, rgb("#f2efe6")), (240, 140, rgb("#6a5a7a"))):
        pot_at(a, x, y, 13, c)
    brush_at(a, 214, 200, -0.6, 70, rgb("#e8b8a0"), wide=True)
    return a.image()


def wax_seal_at(a, x, y, r=12, color=rgb("#9a2a30")):
    a.shape(chaikin([(x + r * math.cos(u) * (1 + 0.15 * math.sin(5 * u)), y + r * math.sin(u) * (1 + 0.15 * math.sin(5 * u))) for u in [k * 0.4 for k in range(16)]], True, 1), color, outline=FINE * 1.4, corner=0, depth=2, light_k=0.4, mottle=0)
    a.ink(ellipse(x, y, r * 0.55, r * 0.55, 16), FINE * 0.8, closed=True, color=shade(color, 0.5), alpha=0.8)


def forgery_kit(seed=7019):
    w, h = 290, 230
    a = art(w, h, seed)
    case(a, 14, 60, w - 14, h - 14, LEATHER_DARK, rgb("#3a3a46"), metal_=IRON, cells=(176,))
    # Blank and half-copied papers, a signet seal, wax sticks, inks, quills.
    paper_at(a, 78, 132, 88, 116, -0.08, lines=True)
    paper_at(a, 104, 140, 88, 116, 0.06, lines=True)
    wax_seal_at(a, 128, 180, 11)
    for k, c in enumerate((rgb("#9a2a30"), rgb("#2f5a3a"), rgb("#2a3f78"))):
        a.shape(rot_pts(rect(196, 90 + k * 18, 256, 102 + k * 18), 226, 96 + k * 18, 0.05), c, outline=FINE * 1.4, corner=4, depth=2, light_k=0.4, mottle=0)
    a.shape(ellipse(212, 168, 12, 12, 20), BRASS, outline=DETAIL, depth=3, light_k=0.5, mottle=0)  # signet
    thin(a, [(212, 168), (248, 186)], 7, WOOD_DARK)
    pot_at(a, 244, 160, 10, INKC)
    quill_at(a, 30, 210, -0.25, 80)
    return a.image()


def herbalism_kit(seed=7020):
    w, h = 300, 230
    a = art(w, h, seed)
    # An open leather satchel; around it pouches, a pruning knife, dried
    # sprigs and leaves, small jars and gloves.
    # The flap, thrown back (up), with its buckle strap.
    flap = chaikin([(26, 70), (156, 70), (150, 24), (120, 14), (60, 14), (32, 24)], True, 2)
    soft_shadow(a, flap, dx=4, dy=5)
    a.shape(flap, shade(LEATHER, 0.15), outline=DETAIL * 1.4, corner=0, depth=4, light_k=0.3)
    a.shape(rect(80, 10, 102, 40), LEATHER_DARK, outline=DETAIL, corner=3, depth=2, mottle=0)
    a.shape(rect(84, 16, 98, 26), BRASS, outline=FINE * 1.3, corner=2, depth=1, mottle=0)
    bag = rect(20, 66, 162, 196)
    soft_shadow(a, bag, dx=5, dy=6)
    a.shape(bag, LEATHER, outline=DETAIL * 1.5, corner=12, depth=6, light_k=0.3)
    a.shape(rect(32, 74, 150, 140), shade(LEATHER, 0.5), outline=DETAIL, corner=8, depth=6, shade_k=0, light_k=0, ao=0.6)
    for k in range(11):
        leaf(a, 44 + k * 9.5, 104 + a.rng.uniform(-14, 14), 28, mix(rgb("#6b9a45"), rgb("#8aa060"), a.rng.random()), ang=-1.3 + a.rng.uniform(-0.5, 0.5))
    a.ink([(30, 160), (152, 160)], FINE * 1.3, color=shade(LEATHER, 0.5), alpha=0.8)
    for x, y, c in ((190, 50, rgb("#a8c86a")), (230, 60, rgb("#c9a2d0")), (270, 50, rgb("#e6c86a"))):
        jar_at(a, x, y, 16, lid=WOOD_DARK, content=c)
    for x, y in ((200, 110), (250, 120)):
        pouch = chaikin([(x - 20, y - 10), (x + 20, y - 10), (x + 22, y + 22), (x - 22, y + 22)], True, 2)
        a.shape(pouch, CANVAS, outline=DETAIL * 1.2, corner=0, depth=3, light_k=0.3)
        a.ink([(x - 16, y - 6), (x + 16, y - 6)], FINE * 1.3, color=LEATHER_DARK)
    # A bundle of dried herbs tied with string.
    for k in range(5):
        a.ink([(170, 190), (250 + k * 6, 170 + k * 8)], FINE * 1.6, color=rgb("#8a7a40"))
        leaf(a, 250 + k * 6, 170 + k * 8, 18, rgb("#9a9a58"), ang=0.3 + k * 0.1, vein=False)
    a.ink([(196, 178), (198, 194)], DETAIL, color=THREAD)
    knife_at(a, 40, 214, -0.05, 90)
    return a.image()


def compass_at(a, x, y, r=26):
    soft_shadow(a, (x, y), r, 3, 4)
    a.shape(ellipse(x, y, r, r, 36), BRASS, outline=DETAIL * 1.4, depth=3, light_k=0.5, mottle=0)
    a.shape(ellipse(x, y, r * 0.78, r * 0.78, 32), rgb("#efe7d2"), outline=FINE * 1.2, depth=1, shade_k=0.1, light_k=0, ao=0.2, mottle=0)
    a.shape([(x, y - r * 0.68), (x + 5, y), (x - 5, y)], rgb("#a8483a"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    a.shape([(x, y + r * 0.68), (x + 5, y), (x - 5, y)], rgb("#2a2a30"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    dot(a, x, y, 2.5, BRASS)


def navigators_tools(seed=7021):
    w, h = 300, 230
    a = art(w, h, seed)
    # A sea chart, a brass sextant, a compass, dividers and a ruler.
    soft_shadow(a, rect(16, 16, 230, 200), dx=5, dy=6)

    def chart(art_, p):
        for u in range(16):
            ang = u * math.pi / 8
            art_.ink([(120, 108), (120 + 120 * math.cos(ang), 108 + 120 * math.sin(ang))], FINE * 0.8, color=rgb("#7a6a52"), alpha=0.5, wob=0)
        art_.ink(chaikin([(16, 160), (60, 140), (80, 170), (130, 196)], False, 2), DETAIL * 0.8, color=rgb("#5a4632"), alpha=0.8)
        art_.ink(chaikin([(170, 16), (190, 50), (230, 60)], False, 2), DETAIL * 0.8, color=rgb("#5a4632"), alpha=0.8)

    a.shape(rect(16, 16, 230, 200), PARCH, outline=DETAIL, corner=3, depth=3, shade_k=0.2, light_k=0.2, detail=chart)
    # Sextant: the arc, two arms and the eyepiece.
    sx, sy = 90, 80
    arc = [(sx + 80 * math.cos(u), sy + 80 * math.sin(u)) for u in [0.5 + k * 0.08 for k in range(14)]]
    a.ink(arc, 12, color=INK, taper=False)
    a.ink(arc, 7, color=BRASS, taper=False)
    for p in (arc[0], arc[-1]):
        thin(a, [(sx, sy), p], 5, BRASS)
    thin(a, [(sx, sy), arc[6]], 4, STEEL)
    a.shape(ellipse(sx, sy, 9, 9, 16), BRASS, outline=DETAIL, depth=2, mottle=0)
    a.shape(rot_pts(rect(sx + 30, sy - 26, sx + 70, sy - 14), sx + 50, sy - 20, 0.5), rgb("#2a2a30"), outline=FINE * 1.4, corner=4, depth=2, mottle=0)
    compass_at(a, 260, 60)
    dividers_at(a, 240, 120, 1.7, 90)
    handle(a, 40, 214, 220, 208, 7, WOOD_LIGHT)
    return a.image()


def poisoners_kit(seed=7022):
    w, h = 270, 230
    a = art(w, h, seed)
    case(a, 14, 60, w - 14, h - 14, rgb("#3e3a36"), RED, metal_=IRON, cells=((150, 70, 206),))
    # Vials of venom, a dropper, a skull-marked bottle, gloves.
    for (x, y), c in zip(((44, 94), (78, 94), (112, 94), (44, 132), (78, 132), (112, 132)), (rgb("#7ccf5a"), rgb("#a86ad0"), rgb("#d8d060"), rgb("#4fc28a"), rgb("#6a8a30"), rgb("#c8d8e8"))):
        flask(a, x, y, 13, c)
    a.shape(ellipse(204, 112, 30, 30, 36), rgb("#3f5a3a"), outline=DETAIL * 1.4, depth=3, light_k=0.6, mottle=0)
    a.shape(ellipse(204, 112, 10, 10, 16), rgb("#2e2a28"), outline=FINE, depth=1, mottle=0)
    # A skull painted on the bottle's shoulder, below its cork.
    a.shape(ellipse(204, 130, 9, 8, 16), rgb("#e6dcc4"), outline=FINE, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    for dx in (-3.5, 3.5):
        dot(a, 204 + dx, 129, 2.2, INK)
    a.ink([(199, 137), (209, 137)], FINE * 1.4, color=rgb("#e6dcc4"))
    thin(a, [(40, 180), (120, 176)], 3, GLASS)
    a.shape(ellipse(36, 180, 9, 8, 16), rgb("#2a2a30"), outline=FINE * 1.3, depth=2, mottle=0)
    glove = chaikin([(170, 170), (240, 164), (250, 176), (244, 196), (172, 200)], True, 2)
    a.shape(glove, rgb("#2f2a26"), outline=DETAIL * 1.2, corner=0, depth=3, light_k=0.3)
    for k in range(4):
        a.ink([(236, 168 + k * 8), (254, 168 + k * 8)], DETAIL * 2.0, color=INK, taper=True)
    return a.image()


def lockpick_at(a, x, y, ang, L_=90, tip="hook"):
    t = L(x, y, ang)
    a.shape(t(rect(0, -6, 30, 6)), LEATHER_DARK, outline=FINE * 1.5, corner=3, depth=1, mottle=0)
    end = {"hook": [(L_ - 6, 0), (L_, 0), (L_ + 2, -6)], "diamond": [(L_ - 8, 0), (L_ - 4, -4), (L_, 0)], "rake": [(L_ - 16, 0), (L_ - 12, -4), (L_ - 8, 0), (L_ - 4, -4), (L_, 0)], "straight": [(L_, 0)]}[tip]
    thin(a, t([(30, 0)] + end), 1.8, STEEL, 3)


def thieves_tools(seed=7023):
    w, h = 280, 190
    a = art(w, h, seed)
    pockets = roll_kit(a, 12, 20, w - 40, h - 12, RED, pocket=0.42)
    for k, tip in enumerate(("hook", "rake", "diamond", "straight", "hook")):
        lockpick_at(a, 36 + k * 22, 170, -1.57 + (k - 2) * 0.03, 120, tip)
    # A narrow file, a tension wrench, small scissors and a little mirror on a
    # stick.
    file_at(a, 160, 172, -1.57, 120)
    thin(a, [(196, 170), (196, 80), (206, 74)], 3, STEEL)
    t = L(224, 172, -1.57)
    thin(a, t([(0, 0), (110, 0)]), 3, STEEL)
    a.shape(ellipse(*t([(118, 0)])[0], 9, 9, 16), rgb("#cfe0e6"), outline=FINE * 1.4, depth=1, light_k=0.8, mottle=0)
    pockets(6)
    return a.image()


# -- gaming sets ---------------------------------------------------------------------------------


def dragonchess_set(seed=7024):
    """Three stacked boards (sky, ground, underworld), each offset, with
    pieces on them."""
    w, h = 300, 280
    a = art(w, h, seed)
    boards = ((20, 120, rgb("#5a3e2a"), rgb("#c8a878")), (70, 70, rgb("#3c5a78"), rgb("#cfe0e6")), (120, 20, rgb("#55743f"), rgb("#d8e2b0")))[::-1]
    for x0, y0, dark, light in boards[::-1]:
        s = 150
        soft_shadow(a, rect(x0, y0, x0 + s, y0 + s), dx=8, dy=10, alpha=0.4, blur=6)
        a.shape(rect(x0, y0, x0 + s, y0 + s), WOOD_DARK, outline=DETAIL * 1.4, corner=4, depth=4)
        n = 8
        c = (s - 16) / n
        for i in range(n):
            for j in range(n):
                col = light if (i + j) % 2 == 0 else dark
                a.shape(rect(x0 + 8 + i * c, y0 + 8 + j * c, x0 + 8 + (i + 1) * c, y0 + 8 + (j + 1) * c), col, outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.ink(rect(x0 + 8, y0 + 8, x0 + s - 8, y0 + s - 8), FINE * 1.3, closed=True)
        for _ in range(5):
            i, j = a.rng.randrange(n), a.rng.choice((0, 1, 6, 7))
            px, py = x0 + 8 + (i + 0.5) * c, y0 + 8 + (j + 0.5) * c
            col = rgb("#f3eee2") if j < 4 else rgb("#2a2a30")
            a.shape(ellipse(px, py, c * 0.32, c * 0.32, 16), col, outline=FINE * 1.2, depth=1.5, shade_k=0.3, light_k=0.4, ao=0, mottle=0)
        # Corner posts between the levels.
        for px, py in ((x0 + 4, y0 + 4), (x0 + s - 4, y0 + 4), (x0 + 4, y0 + s - 4), (x0 + s - 4, y0 + s - 4)):
            dot(a, px, py, 5, BRASS)
            a.ink(ellipse(px, py, 5, 5, 12), FINE, closed=True)
    return a.image()


def playing_cards(seed=7025):
    w, h = 190, 150
    a = art(w, h, seed)
    # The deck squared up, and a fanned hand beside it.
    for k in range(5, 0, -1):
        a.shape(rect(26 + k, 30 + k, 80 + k, 108 + k), rgb("#e8e0cc"), outline=FINE * 1.3, corner=4, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    a.shape(rect(26, 30, 80, 108), rgb("#3c5a78"), outline=DETAIL * 1.1, corner=4, depth=2, light_k=0.3, mottle=0)
    a.ink(rect(32, 36, 74, 102), FINE, closed=True, color=CERAMIC, alpha=0.8)
    a.ink([(32, 36), (74, 102)], FINE * 0.8, color=CERAMIC, alpha=0.6)
    a.ink([(74, 36), (32, 102)], FINE * 0.8, color=CERAMIC, alpha=0.6)
    for k in range(5):
        u = -0.5 + k * 0.25
        t = L(130, 120, u - 1.57)
        pts = t([(0, -14), (68, -14), (68, 14), (0, 14)])
        a.shape(pts, rgb("#f3eee2"), outline=FINE * 1.3, corner=3, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.shape(t(rect(52, -8, 62, 0)), rgb("#a8483a") if k % 2 else rgb("#2a2a30"), outline=0, corner=1, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    return a.image()


def three_dragon_ante(seed=7026):
    w, h = 240, 190
    a = art(w, h, seed)
    # Dragon cards laid in a row (each a colored dragon silhouette), and the
    # ante: a pile of coins in the middle.
    cols = (rgb("#c8443a"), rgb("#4f8fd0"), rgb("#55743f"), rgb("#2a2a30"), rgb("#e2b84e"))
    for k, c in enumerate(cols):
        x = 34 + k * 42
        t = L(x, 54, 0.04 * (k - 2) + 1.57)
        a.shape(t(rect(-30, -18, 30, 18)), rgb("#f3eee2"), outline=FINE * 1.4, corner=3, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        dragon = [(-18, 0), (-6, -10), (2, -4), (14, -12), (10, 0), (16, 8), (2, 6), (-8, 10)]
        a.shape(t(dragon), c, outline=FINE, corner=1, depth=1, shade_k=0.2, light_k=0.2, ao=0, mottle=0)
    for k in range(14):
        coin_at(a, 120 + a.rng.uniform(-26, 26), 140 + a.rng.uniform(-16, 16), a.rng.uniform(7, 9), GOLD if k % 4 else rgb("#c7ccd4"))
    cards_at(a, 40, 150, 3, 0.5)
    cards_at(a, 200, 150, 3, 0.5)
    return a.image()


# -- musical instruments -------------------------------------------------------------------------


def bagpipes(seed=7027):
    w, h = 260, 230
    a = art(w, h, seed)
    # The bag (red = colorable, a tartan-less cloth cover), three drones
    # resting over the shoulder, the blowpipe and the chanter.
    for (x1, y1), L_ in (((230, 30), 1), ((240, 70), 1), ((210, 16), 1)):
        thin(a, [(130, 110), (x1, y1)], 10, WOOD_DARK)
        a.shape(ellipse(x1, y1, 11, 11, 20), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
        a.shape(ellipse(x1, y1, 5, 5, 12), INK, outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        for f in (0.45, 0.75):
            mx, my = 130 + (x1 - 130) * f, 110 + (y1 - 110) * f
            dot(a, mx, my, 7, CERAMIC)
            a.ink(ellipse(mx, my, 7, 7, 12), FINE, closed=True)
    for (x1, y1), r in (((30, 50), 8), ((40, 210), 12)):
        thin(a, [(100, 120), (x1, y1)], 9 if r == 8 else 11, WOOD_DARK)
    a.shape(ellipse(40, 210, 14, 14, 20), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
    for k in range(5):
        f = 0.3 + k * 0.1
        dot(a, 100 + (40 - 100) * f, 120 + (210 - 120) * f, 2.5, INK)
    bag = chaikin([(70, 80), (140, 70), (180, 110), (160, 170), (100, 180), (60, 140)], True, 3)
    soft_shadow(a, bag, dx=6, dy=7)
    a.shape(bag, RED, outline=DETAIL * 1.6, corner=0, depth=8, light_k=0.35, detail=lambda art_, p: [art_.ink([(60, y), (190, y + 10)], FINE * 1.1, color=shade(RED, 0.45), alpha=0.5) for y in range(90, 180, 18)])
    a.ink([(80, 150), (168, 96)], DETAIL * 1.1, color=CERAMIC, alpha=0.9)  # tassel cord
    return a.image()


def drum(seed=7028):
    """A war drum seen from above: drumhead on a deep shell, rope tensioning
    zig-zag around it, and two sticks across."""
    s = 220
    a = art(s, s, seed)
    cx = cy = 110
    r = 86
    soft_shadow(a, (cx, cy), r, 6, 8, 0.4, 6)

    def ropes(art_, p):
        for k in range(16):
            u0 = 2 * math.pi * k / 16
            u1 = u0 + math.pi / 16
            art_.ink([(cx + r * 0.84 * math.cos(u0), cy + r * 0.84 * math.sin(u0)), (cx + r * math.cos(u1), cy + r * math.sin(u1)), (cx + r * 0.84 * math.cos(u1 + math.pi / 16), cy + r * 0.84 * math.sin(u1 + math.pi / 16))], FINE * 1.6, color=CERAMIC, alpha=0.95)

    a.shape(ellipse(cx, cy, r, r, 64), RED, outline=OUTLINE * 0.85, depth=6, light_k=0.3, detail=ropes)
    a.shape(ellipse(cx, cy, r * 0.8, r * 0.8, 56), rgb("#e8dcc0"), outline=DETAIL * 1.3, depth=4, light_k=0.4, detail=lambda art_, p: art_.ink(ellipse(cx, cy, r * 0.5, r * 0.5, 40), FINE, closed=True, color=shade(rgb("#e8dcc0"), 0.25), alpha=0.6))
    for dy, u in ((-10, -0.35), (12, -0.15)):
        handle(a, 40, cy + 40 + dy, 190, cy - 40 + dy + 20 * u, 7, WOOD_LIGHT)
        dot(a, 190, cy - 40 + dy + 20 * u, 7, CERAMIC)
        a.ink(ellipse(190, cy - 40 + dy + 20 * u, 7, 7, 14), FINE * 1.2, closed=True)
    return a.image()


def dulcimer(seed=7029):
    """A hammered dulcimer: a trapezoid soundbox strung across, two bridges,
    rose holes and the two little hammers."""
    w, h = 300, 210
    a = art(w, h, seed)
    box = [(20, 30), (280, 60), (280, 150), (20, 180)]
    soft_shadow(a, box, dx=6, dy=7)
    a.shape(box, WOOD_DARK, outline=OUTLINE * 0.8, corner=6, depth=5)
    a.shape([(34, 42), (266, 70), (266, 140), (34, 168)], rgb("#c9a06a"), outline=DETAIL, corner=3, depth=3, shade_k=0.2, light_k=0.2)
    for x, y in ((110, 82), (190, 128)):
        a.shape(ellipse(x, y, 14, 14, 24), rgb("#2a1e18"), outline=FINE * 1.3, depth=1, shade_k=0, light_k=0, mottle=0)
        a.ink(ellipse(x, y, 18, 18, 24), FINE, closed=True, color=shade(rgb("#c9a06a"), 0.4), alpha=0.7)
    for k in range(14):
        f = (k + 0.5) / 14
        y0, y1 = 42 + 126 * f, 70 + 70 * f
        a.ink([(30, y0), (270, y1)], FINE * 0.7, color=rgb("#eee6d2"), alpha=0.95, wob=0)
    for x in (90, 200):
        top = 42 + (70 - 42) * (x - 20) / 260 + 6
        bot = 168 - (168 - 140) * (x - 20) / 260 - 6
        a.shape(rect(x - 4, top, x + 4, bot), WOOD_LIGHT, outline=FINE * 1.3, corner=2, depth=1, mottle=0)
    for k in range(2):
        handle(a, 60 + k * 30, 200, 120 + k * 30, 186, 4, WOOD_LIGHT)
        a.shape(ellipse(124 + k * 30, 185, 7, 5, 14, rot=-0.2), WOOD, outline=FINE * 1.3, depth=1, mottle=0)
    return a.image()


def brass_horn(seed=7030):
    """A brass hunting horn: a tube wound once around, flaring into a wide
    bell that points out of the coil, with a leather carrying strap."""
    s = 210
    a = art(s, s, seed)
    cx, cy, R = 96, 110, 58
    us = [-0.6 + k * (2 * math.pi - 0.9) / 40 for k in range(41)]
    spine = [(cx + R * math.cos(u), cy + R * math.sin(u)) for u in us]
    u1 = us[-1]
    tx, ty = -math.sin(u1), math.cos(u1)  # direction of travel at the end
    ex, ey = spine[-1]
    bell_c = (ex + tx * 34, ey + ty * 34)
    a.ink(chaikin([spine[6], (cx, cy - 4), spine[26]], False, 2), DETAIL * 1.8, color=INK)
    a.ink(chaikin([spine[6], (cx, cy - 4), spine[26]], False, 2), DETAIL * 0.9, color=LEATHER)
    soft_shadow(a, tube(spine, 12, 20), dx=5, dy=6)
    a.shape(tube(spine, 12, 20), BRASS, outline=DETAIL * 1.4, corner=0, depth=3, light_k=0.55, mottle=0)
    flare = tube([(ex - tx * 2, ey - ty * 2), (ex + tx * 16, ey + ty * 16), bell_c], 20, 64)
    a.shape(flare, BRASS, outline=DETAIL * 1.4, corner=0, depth=4, light_k=0.55, mottle=0)
    ang = math.atan2(ty, tx)
    a.shape(ellipse(bell_c[0], bell_c[1], 10, 32, 32, rot=ang), shade(BRASS, 0.5), outline=DETAIL * 1.2, depth=2, shade_k=0, light_k=0, ao=0.5, mottle=0)
    a.shape(ellipse(spine[0][0], spine[0][1], 8, 8, 16), STEEL, outline=FINE * 1.4, depth=1, mottle=0)
    return a.image()


def lyre(seed=7031):
    w, h = 190, 250
    a = art(w, h, seed)
    # A tortoiseshell-style soundbox, two curved arms, a crossbar and strings.
    for s in (-1, 1):
        arm = chaikin([(95 + s * 34, 170), (95 + s * 60, 120), (95 + s * 46, 70), (95 + s * 62, 30)], False, 3)
        a.shape(tube(arm, 18, 14), WOOD, outline=DETAIL * 1.4, corner=0, depth=3, light_k=0.4, mottle=0)
    a.shape(rect(20, 30, 170, 46), WOOD_DARK, outline=DETAIL * 1.3, corner=6, depth=3)
    box = chaikin([(40, 150), (95, 136), (150, 150), (160, 200), (95, 236), (30, 200)], True, 3)
    soft_shadow(a, box, dx=5, dy=6)
    a.shape(box, rgb("#9a6a3a"), outline=DETAIL * 1.5, corner=0, depth=6, light_k=0.4, detail=lambda art_, p: [art_.ink(ellipse(95, 190, r, r * 0.8, 24), FINE, closed=True, color=shade(rgb("#9a6a3a"), 0.45), alpha=0.6) for r in (20, 36)])
    a.shape(rect(60, 196, 130, 206), WOOD_LIGHT, outline=FINE * 1.3, corner=2, depth=1, mottle=0)
    for k in range(7):
        x = 66 + k * 10
        a.ink([(x, 40), (x, 200)], FINE * 0.8, color=rgb("#eee6d2"), alpha=0.95, wob=0)
        dot(a, x, 38, 2.6, BRASS)
    return a.image()


def pan_flute(seed=7032):
    w, h = 210, 160
    a = art(w, h, seed)
    # Reed pipes side by side, shortest to longest, bound with cord.
    pipes = []
    for k in range(8):
        x = 30 + k * 20
        Lp = 50 + k * 11
        pipes.append((x, Lp))
    for x, Lp in pipes:
        soft_shadow(a, rect(x - 10, 20, x + 10, 20 + Lp), dx=4, dy=5, alpha=0.3, blur=3)
    for x, Lp in pipes:
        a.shape(rect(x - 10, 20, x + 10, 20 + Lp), rgb("#d6bc7a"), outline=DETAIL * 1.2, corner=4, depth=2, light_k=0.45, mottle=0)
        a.shape(ellipse(x, 28, 5, 4, 14), rgb("#3a2e22"), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    for y in (50, 62):
        a.ink([(18, y), (192, y)], DETAIL * 1.1, color=rgb("#8a4a2a"), taper=False)
    return a.image()


def shawm(seed=7033):
    w, h = 300, 110
    a = art(w, h, seed)
    # A long conical wooden pipe with finger holes, the double reed in its
    # pirouette at the narrow end, flaring to a wide bell.
    spine = [(30 + k * 12, 56 - k * 0.4) for k in range(20)]
    soft_shadow(a, tube(spine, 12, 26), dx=4, dy=5)
    a.shape(tube(spine, 12, 26), WOOD_DARK, outline=DETAIL * 1.4, corner=0, depth=3, light_k=0.45, mottle=0)
    ex, ey = spine[-1]
    a.shape(tube([(ex - 6, ey), (ex + 20, ey), (ex + 40, ey)], 26, 74), WOOD_DARK, outline=DETAIL * 1.4, corner=0, depth=4, light_k=0.45, mottle=0)
    a.shape(ellipse(ex + 40, ey, 8, 36, 28), shade(WOOD_DARK, 0.5), outline=DETAIL, depth=2, shade_k=0, light_k=0, ao=0.5, mottle=0)
    for k in range(7):
        x = 90 + k * 20
        dot(a, x, 56 - (x - 30) / 30, 3.2, INK)
    a.shape(ellipse(28, 56, 9, 9, 16), BRASS, outline=FINE * 1.4, depth=1, mottle=0)
    a.shape([(4, 52), (22, 53), (22, 59), (4, 60)], rgb("#d6bc7a"), outline=FINE * 1.3, corner=2, depth=1, mottle=0)
    return a.image()


def viol(seed=7034):
    w, h = 320, 160
    a = art(w, h, seed)
    # Body with C-bouts and f-holes, fingerboard, pegbox and scroll, strings;
    # the bow laid along it.
    body = chaikin([(20, 80), (30, 40), (70, 30), (100, 50), (130, 42), (170, 30), (200, 50), (204, 80), (200, 110), (170, 130), (130, 118), (100, 110), (70, 130), (30, 120)], True, 3)
    soft_shadow(a, body, dx=5, dy=6)
    a.shape(body, rgb("#b0632e"), outline=DETAIL * 1.6, corner=0, depth=6, light_k=0.4)
    for y in (64, 96):
        a.ink([(100, y - 8 if y < 80 else y + 8), (108, y), (128, y), (136, y + 8 if y < 80 else y - 8)], FINE * 1.3, color=INK)
    a.shape(rect(90, 72, 270, 88), rgb("#2a1e18"), outline=DETAIL, corner=3, depth=2, mottle=0)
    a.shape(rect(264, 70, 296, 90), rgb("#7a4a2a"), outline=DETAIL, corner=3, depth=2, mottle=0)
    a.shape(ellipse(302, 80, 10, 10, 20), rgb("#7a4a2a"), outline=DETAIL, depth=2, mottle=0)
    for x in (272, 284):
        for s in (-1, 1):
            a.ink([(x, 80 + s * 10), (x, 80 + s * 18)], DETAIL * 1.3, color=INK, taper=False)
    a.shape(rect(52, 72, 60, 88), rgb("#2a1e18"), outline=FINE, corner=2, depth=1, mottle=0)
    a.shape(rect(140, 70, 146, 90), WOOD_LIGHT, outline=FINE, corner=1, depth=1, mottle=0)
    for k in range(4):
        y = 74 + k * 4
        a.ink([(56, y), (276, y)], FINE * 0.6, color=rgb("#eee6d2"), alpha=0.95, wob=0)
    thin(a, [(30, 148), (290, 132)], 4, WOOD_DARK)
    a.ink([(40, 142), (284, 127)], FINE, color=rgb("#f3eee2"), alpha=0.9, wob=0)
    a.shape(rot_pts(rect(26, 140, 44, 154), 35, 147, -0.06), rgb("#2a1e18"), outline=FINE * 1.3, corner=2, depth=1, mottle=0)
    return a.image()


SRD_TOOLS = {
    "Alchemist's Supplies": alchemists_supplies,
    "Brewer's Supplies": brewers_supplies,
    "Calligrapher's Supplies": calligraphers_supplies,
    "Carpenter's Tools": carpenters_tools,
    "Cartographer's Tools": cartographers_tools,
    "Cobbler's Tools": cobblers_tools,
    "Cook's Utensils": cooks_utensils,
    "Glassblower's Tools": glassblowers_tools,
    "Jeweler's Tools": jewelers_tools,
    "Leatherworker's Tools": leatherworkers_tools,
    "Mason's Tools": masons_tools,
    "Painter's Supplies": painters_supplies,
    "Potter's Tools": potters_tools,
    "Smith's Tools": smiths_tools,
    "Tinker's Tools": tinkers_tools,
    "Weaver's Tools": weavers_tools,
    "Woodcarver's Tools": woodcarvers_tools,
    "Disguise Kit": disguise_kit,
    "Forgery Kit": forgery_kit,
    "Herbalism Kit": herbalism_kit,
    "Navigator's Tools": navigators_tools,
    "Poisoner's Kit": poisoners_kit,
    "Thieves' Tools": thieves_tools,
    "Dragonchess Set": dragonchess_set,
    "Playing Cards": playing_cards,
    "Three-Dragon Ante Set": three_dragon_ante,
    "Bagpipes": bagpipes,
    "Drum": drum,
    "Dulcimer": dulcimer,
    "Horn": brass_horn,
    "Lyre": lyre,
    "Pan Flute": pan_flute,
    "Shawm": shawm,
    "Viol": viol,
}

SRD_TOOLS_COLORABLE = {
    "Alchemist's Supplies",
    "Cook's Utensils",
    "Jeweler's Tools",
    "Weaver's Tools",
    "Woodcarver's Tools",
    "Disguise Kit",
    "Poisoner's Kit",
    "Thieves' Tools",
    "Bagpipes",
    "Drum",
}
