"""SRD 5.2.1 adventuring gear: what the pack didn't have yet (vials and
flasks, focuses, holy symbols, kits, tools of the trade, light sources) and
the seven equipment packs laid out with their contents. Top-down, same pen
style. Gear that already exists elsewhere (Backpack, Rope Coil, Bedroll,
Bear Trap...) is reused, not redrawn."""

import math

import skia
from PIL import Image

import obj_camp
import obj_storage
import obj_tavern
import objects
from kit import BRASS, IRON, RED, WOOD, WOOD_DARK, WOOD_LIGHT, dot, ring, scallop, soft_shadow
from obj_craft import STEEL, handle, hammer_at, rot_pts
from obj_dungeon import chain
from obj_magic import glow
from pen import DETAIL, FINE, INK, Art, blob, chaikin, ellipse, rect, rgb, shade, tint, vary

GLASS = rgb("#c9dde2")
LEATHER = rgb("#8a5a3a")
LEATHER_DARK = rgb("#6a4228")
PARCH = rgb("#e9dcb8")
PAPER = rgb("#f2ede0")
LINEN = rgb("#ece4d0")
SILVER = rgb("#c4c8cc")
GOLD = rgb("#d6ae4c")
FLAME = rgb("#f6b444")
CORK = rgb("#c39463")
TWINE = rgb("#d4b77c")
O = DETAIL * 1.6  # outline weight for small gear


def _glint(a, pts, alpha=0.85):
    a.ink(pts, FINE * 1.6, color=(250, 248, 240), alpha=alpha, wob=0.2)


def flame(a, x, y, r, ang=0.0):
    """A small flame seen from above, pointing along `ang`, with its glow."""
    glow(a, x, y, r * 3.2, rgb("#ffd27a"), 0.4)
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    pts = chaikin([(x - ux * r * 0.7 + px * r, y - uy * r * 0.7 + py * r), (x + ux * r * 1.8, y + uy * r * 1.8), (x - ux * r * 0.7 - px * r, y - uy * r * 0.7 - py * r), (x - ux * r * 1.2, y - uy * r * 1.2)], True, 2)
    a.shape(pts, FLAME, outline=FINE * 1.3, corner=0, depth=1, mottle=0, shade_k=0, light_k=0, ao=0)
    a.shape(ellipse(x + ux * r * 0.2, y + uy * r * 0.2, r * 0.45, r * 0.45, 16), rgb("#fff4cf"), outline=0, depth=1, mottle=0, shade_k=0, light_k=0, ao=0)


# -- vials, flasks and bottles lying on their side ---------------------------------------------


def bottle_side(a, x, y, ang, L, r, liquid, kind="vial", glass=GLASS, cap=CORK, neck=None):
    """A glass container lying on its side, pointing along `ang` from its
    base at (x, y): `vial` is a narrow tube, `flask` a round body with a long
    neck, `bottle` a shouldered bottle. `liquid` fills the glass (None =
    empty), seen through a pale glass rim."""
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    neck = neck or r * 0.45
    if kind == "flask":
        bx = x + r
        body = ellipse(bx, y, r, r, 40)
        nk = rect(bx + r * 0.6, y - neck, x + L - 6, y + neck)
    elif kind == "bottle":
        bl = L * 0.62
        body = chaikin([(x, y - r), (x + bl, y - r), (x + bl + r * 0.7, y - neck), (x + bl + r * 0.7, y + neck), (x + bl, y + r), (x, y + r)], True, 2)
        nk = rect(x + bl + r * 0.5, y - neck, x + L - 6, y + neck)
    else:
        body = rect(x, y - r, x + L - 10, y + r)
        nk = rect(x + L - 16, y - r * 0.92, x + L - 6, y + r * 0.92)
    soft_shadow(a, loc(body), dx=3, dy=4, alpha=0.3)
    if kind != "vial":
        a.shape(loc(nk), glass, outline=O, corner=3, depth=2, light_k=0.6, mottle=0)
    a.shape(loc(body), glass, outline=O, corner=r * 0.7 if kind == "vial" else 0, depth=2, light_k=0.6, mottle=0)
    if liquid is not None:
        inner = ellipse(x + r, y, r * 0.78, r * 0.78, 36) if kind == "flask" else (chaikin([(x + 4, y - r * 0.72), (x + L * 0.62 - 2, y - r * 0.72), (x + L * 0.62 + r * 0.4, y - neck * 0.6), (x + L * 0.62 + r * 0.4, y + neck * 0.6), (x + L * 0.62 - 2, y + r * 0.72), (x + 4, y + r * 0.72)], True, 2) if kind == "bottle" else rect(x + 4, y - r * 0.68, x + L * 0.72, y + r * 0.68))
        a.shape(loc(inner), liquid, outline=0, corner=r * 0.5, depth=2, light_k=0.3, shade_k=0.35, ao=0, mottle=0.04)
    _glint(a, loc([(x + r * 0.5, y - r * 0.55), (x + (r * 1.4 if kind == "flask" else L * 0.45), y - r * 0.55)]))
    # Stopper at the mouth.
    a.shape(loc(rect(x + L - 12, y - neck - 1, x + L, y + neck + 1)), cap, outline=FINE * 1.5, corner=2, depth=2, mottle=0)
    return loc


def _vial_item(seed, w, h, liquid, kind="vial", L=None, r=None, ang=-0.25, extra=None, glass=GLASS, cap=CORK):
    def make():
        a = Art(w, h, seed)
        LL = L or w - 30
        rr = r or h * 0.22
        x0 = (w - LL * math.cos(ang)) / 2
        y0 = (h - LL * math.sin(ang)) / 2
        loc = bottle_side(a, x0, y0, ang, LL, rr, liquid, kind, glass, cap)
        if extra:
            extra(a, loc, x0, y0, LL, rr)
        return a.image()

    return make


def _bubbles(a, loc, x0, y0, L, r):
    for dx, dy, rr in ((0.18, -0.2, 3.2), (0.32, 0.25, 2.4), (0.48, -0.05, 3.6), (0.6, 0.3, 2.2)):
        p = loc([(x0 + L * dx, y0 + r * dy)])[0]
        ring(a, p[0], p[1], rr, 1.4, tint(rgb("#8ed04a"), 0.6), 0.9)


def _label(color=PARCH, mark=None):
    def draw(a, loc, x0, y0, L, r):
        a.shape(loc(rect(x0 + L * 0.2, y0 - r * 0.9, x0 + L * 0.42, y0 + r * 0.9)), color, outline=FINE * 1.4, corner=1, depth=1, mottle=0, shade_k=0.2, light_k=0)
        if mark:
            mark(a, loc, x0 + L * 0.31, y0, r)

    return draw


def _skull(a, loc, cx, cy, r):
    (x, y), = loc([(cx, cy)])
    a.shape(ellipse(x, y - 1, r * 0.42, r * 0.38, 16), rgb("#efe8d6"), outline=FINE * 1.1, depth=1, mottle=0, shade_k=0, light_k=0, ao=0)
    dot(a, x - r * 0.15, y - 1, r * 0.1)
    dot(a, x + r * 0.15, y - 1, r * 0.1)


def _cross(a, loc, cx, cy, r):
    a.ink(loc([(cx, cy - r * 0.5), (cx, cy + r * 0.5)]), FINE * 1.3, color=rgb("#4a6fa8"), taper=False)
    a.ink(loc([(cx - r * 0.3, cy - r * 0.1), (cx + r * 0.3, cy - r * 0.1)]), FINE * 1.3, color=rgb("#4a6fa8"), taper=False)


def _sun(a, loc, cx, cy, r):
    (x, y), = loc([(cx, cy)])
    dot(a, x, y, r * 0.22, GOLD)
    for k in range(8):
        t = k * math.pi / 4
        a.ink([(x + r * 0.3 * math.cos(t), y + r * 0.3 * math.sin(t)), (x + r * 0.5 * math.cos(t), y + r * 0.5 * math.sin(t))], FINE, color=shade(GOLD, 0.3), taper=False)


def _fire_glow(a, loc, x0, y0, L, r):
    p = loc([(x0 + r, y0)])[0]
    glow(a, p[0], p[1], r * 2.2, rgb("#ff9a3a"), 0.3)
    # A rag stuck in the neck, ready to light.
    q = loc([(x0 + L, y0)])[0]
    rag = blob(q[0] + 6, q[1] + 2, 9, a.rng, 7, 0.25)
    a.shape(rag, rgb("#d8ccb0"), outline=FINE * 1.4, depth=1, mottle=0, smooth=True)


def oil_flask(seed=2007):
    """Oil: a squat clay flask with a stopper, a drip of oil on its shoulder."""
    w, h = 120, 80
    a = Art(w, h, seed)
    clay = rgb("#b98a5a")
    soft_shadow(a, ellipse(48, 42, 32, 26, 32), dx=3, dy=4)
    a.shape(rect(66, 32, 104, 50), clay, outline=O, corner=6, depth=2, mottle=0.05)
    a.shape(ellipse(48, 41, 34, 28, 40), clay, outline=O, depth=5, light_k=0.4)
    a.ink([(30, 32), (58, 30)], FINE * 1.3, color=shade(clay, 0.4), alpha=0.7)
    a.ink([(28, 50), (60, 52)], FINE * 1.3, color=shade(clay, 0.4), alpha=0.7)
    a.shape(rect(98, 33, 112, 49), CORK, outline=FINE * 1.5, corner=2, depth=2, mottle=0)
    a.shape(ellipse(70, 30, 6, 4, 14), rgb("#d9b84a"), outline=FINE, depth=1, mottle=0, shade_k=0, light_k=0.4, ao=0)
    return a.image()


def hip_flask(seed=2008):
    """Flask: a flat pewter hip flask with a screw cap."""
    w, h = 110, 120
    a = Art(w, h, seed)
    pewter = rgb("#a7abb0")
    body = chaikin([(22, 34), (88, 34), (94, 70), (84, 108), (26, 108), (16, 70)], True, 2)
    soft_shadow(a, body)
    a.shape(rect(44, 14, 66, 38), pewter, outline=O, corner=4, depth=2, mottle=0)
    a.shape(body, pewter, outline=O, depth=6, light_k=0.55, mottle=0.03)
    a.ink(chaikin([(30, 46), (80, 46), (84, 72), (76, 98), (34, 98), (26, 72)], True, 2), FINE * 1.2, closed=True, color=shade(pewter, 0.4), alpha=0.7)
    a.shape(rect(41, 8, 69, 22), shade(pewter, 0.25), outline=O, corner=4, depth=2, mottle=0)
    _glint(a, [(30, 56), (34, 90)])
    return a.image()


def ink_bottle(seed=2009):
    """Ink: a squat glass ink pot from above, black ink at the mouth."""
    s = 80
    a = Art(s, s, seed)
    m = s / 2
    a.shape(ellipse(m, m, 28, 28, 40), rgb("#3a4652"), outline=O, depth=5, light_k=0.6)
    a.shape(ellipse(m, m, 12, 12, 24), shade(GLASS, 0.15), outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(m, m, 8, 8, 20), rgb("#16161c"), outline=0, depth=1, mottle=0, shade_k=0, light_k=0.2, ao=0)
    _glint(a, [(m - 18, m - 8), (m - 9, m - 19)])
    return a.image()


def ink_pen(seed=2010):
    """Ink Pen: a wooden pen holder with a metal nib (no feather: that's the
    quill)."""
    w, h = 190, 60
    a = Art(w, h, seed)
    ang = -0.12
    x, y = 20, 38
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    soft_shadow(a, loc(rect(x, y - 6, x + 150, y + 6)), alpha=0.25)
    a.shape(loc(rect(x, y - 6, x + 120, y + 6)), WOOD_DARK, outline=O, corner=5, depth=2, mottle=0)
    a.shape(loc(rect(x + 112, y - 7, x + 128, y + 7)), BRASS, outline=FINE * 1.5, corner=2, depth=1, mottle=0)
    a.shape(loc([(x + 128, y - 6), (x + 156, y - 1), (x + 162, y), (x + 156, y + 1), (x + 128, y + 6)]), STEEL, outline=FINE * 1.5, corner=0, wob=0.1, depth=1, mottle=0)
    a.ink(loc([(x + 134, y), (x + 158, y)]), FINE, color=INK, alpha=0.9)
    dot(a, *loc([(x + 160, y)])[0], 2.2, rgb("#16161c"))
    return a.image()


# -- arcane and druidic focuses, holy symbols ---------------------------------------------------


def arcane_crystal(seed=2020):
    """Arcane Focus (Crystal): a long faceted quartz point lying on its side."""
    w, h = 150, 80
    a = Art(w, h, seed)
    c = rgb("#b9a6e8")
    glow(a, 75, 40, 60, rgb("#a68ae0"), 0.3)
    pts = [(18, 30), (100, 22), (134, 40), (100, 58), (18, 50)]
    soft_shadow(a, pts)
    a.shape(pts, c, outline=O, corner=0, wob=0.1, depth=2, light_k=0.6, mottle=0)
    a.shape([(18, 30), (100, 22), (134, 40), (18, 40)], tint(c, 0.25), outline=0, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    for xa in (18, 100):
        a.ink([(xa, 24 if xa == 100 else 30), (xa, 56 if xa == 100 else 50)], FINE * 1.2, color=shade(c, 0.4), alpha=0.8)
    a.ink([(18, 40), (134, 40)], FINE * 1.2, color=shade(c, 0.4), alpha=0.7)
    _glint(a, [(30, 33), (90, 28)])
    return a.image()


def arcane_orb(seed=2021):
    """Arcane Focus (Orb): a glass orb with a swirl of light inside."""
    s = 110
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 52, rgb("#7fa6f0"), 0.4)
    soft_shadow(a, (m, m), 34)
    a.shape(ellipse(m, m, 34, 34, 48), rgb("#5f7fd0"), outline=O, depth=8, light_k=0.6, mottle=0.05)
    a.ink([(m - 14, m + 8), (m - 4, m - 8), (m + 10, m - 4), (m + 6, m + 10), (m - 2, m + 4)], FINE * 1.6, color=rgb("#cfe0ff"), alpha=0.9)
    _glint(a, [(m - 22, m - 6), (m - 10, m - 22)])
    return a.image()


def arcane_rod(seed=2022):
    """Arcane Focus (Rod): a short iron rod with flanged ends and a gem."""
    w, h = 220, 70
    a = Art(w, h, seed)
    ang = -0.1
    x, y = 24, 40
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    soft_shadow(a, loc(rect(x, y - 8, x + 170, y + 8)), alpha=0.25)
    a.shape(loc(rect(x, y - 7, x + 170, y + 7)), shade(IRON, 0.05), outline=O, corner=4, depth=2, light_k=0.5, mottle=0)
    for t in (0, 60, 110):
        a.shape(loc(rect(x + t - 2, y - 10, x + t + 8, y + 10)), BRASS, outline=FINE * 1.5, corner=2, depth=1, mottle=0)
    a.shape(loc(rect(x + 160, y - 14, x + 176, y + 14)), BRASS, outline=O, corner=3, depth=2, mottle=0)
    p = loc([(x + 186, y)])[0]
    glow(a, p[0], p[1], 20, rgb("#e05a5a"), 0.35)
    a.shape(ellipse(p[0], p[1], 10, 10, 20), rgb("#c84a5e"), outline=FINE * 1.6, depth=2, light_k=0.6, mottle=0)
    return a.image()


def mistletoe(seed=2023):
    """Druidic Focus (Sprig of Mistletoe): forked green twigs, paired leaves
    and white berries, tied with a twine."""
    s = 150
    a = Art(s, s, seed)
    stem = rgb("#7a8a3a")
    leaf = rgb("#8fae4a")
    branches = [[(30, 120), (62, 92), (96, 70)], [(62, 92), (70, 54), (64, 28)], [(62, 92), (104, 100), (130, 92)], [(96, 70), (124, 52)], [(96, 70), (106, 34)]]
    for br in branches:
        a.ink(br, 8, color=INK, taper=False)
        a.ink(br, 4, color=stem, taper=False)
    for br in branches:
        ex, ey = br[-1]
        px, py = br[-2]
        ang = math.atan2(ey - py, ex - px)
        for s_ in (-0.7, 0.7):
            t = ang + s_
            cx, cy = ex + 16 * math.cos(t), ey + 16 * math.sin(t)
            a.shape(ellipse(cx, cy, 15, 6, 20, rot=t), vary(a.rng, leaf, 0.06), outline=FINE * 1.5, depth=1.5, mottle=0)
    for bx, by in ((60, 88), (66, 94), (94, 66), (100, 72), (90, 72)):
        a.shape(ellipse(bx, by, 5, 5, 14), rgb("#f4f1e4"), outline=FINE * 1.2, depth=1, mottle=0, shade_k=0.3, light_k=0, ao=0)
    a.ink([(36, 108), (46, 118)], 6, color=INK, taper=False)
    a.ink([(36, 108), (46, 118)], 3.5, color=TWINE, taper=False)
    return a.image()


def druid_staff(seed=2024):
    """Druidic Focus (Wooden Staff): a gnarled branch staff, its head
    sprouting live leaves."""
    w, h = 400, 120
    a = Art(w, h, seed)
    shaft = chaikin([(20, 92), (120, 80), (220, 74), (320, 58), (350, 52)], False, 2)
    a.ink(shaft, 22, color=INK, taper=False)
    a.ink(shaft, 15, color=WOOD_DARK, taper=False)
    a.ink(shaft, 3, color=tint(WOOD_DARK, 0.3), alpha=0.6, taper=False)
    for k in (90, 180, 260):
        a.ink([(k, 84 - k * 0.06), (k + 10, 74 - k * 0.06)], 6, color=INK, taper=True)
    twig = chaikin([(340, 54), (362, 30), (380, 40)], False, 2)
    a.ink(twig, 11, color=INK, taper=False)
    a.ink(twig, 6, color=WOOD_DARK, taper=False)
    twig2 = chaikin([(346, 54), (370, 74), (388, 62)], False, 2)
    a.ink(twig2, 11, color=INK, taper=False)
    a.ink(twig2, 6, color=WOOD_DARK, taper=False)
    for cx, cy, t in ((372, 26, -0.6), (386, 44, 0.4), (362, 82, 2.0), (392, 66, 0.9), (356, 40, -1.8)):
        a.shape(ellipse(cx, cy, 13, 6, 20, rot=t), vary(a.rng, rgb("#6b9a45"), 0.08), outline=FINE * 1.5, depth=1.5, mottle=0)
    return a.image()


def yew_wand(seed=2025):
    """Druidic Focus (Yew Wand): a twisting reddish yew wand with a leaf
    bud at its tip."""
    w, h = 200, 70
    a = Art(w, h, seed)
    yew = rgb("#9a5a3a")
    pts = [(18, 48), (60, 40), (100, 36), (140, 30), (176, 22)]
    wavy = [(x, y + 3 * math.sin(i * 1.7)) for i, (x, y) in enumerate(chaikin(pts, False, 2))]
    a.ink(wavy, 12, color=INK, taper=False)
    a.ink(wavy, 7, color=yew, taper=False)
    for k in range(4):
        x = 40 + k * 32
        a.ink([(x, 46 - k * 4), (x + 8, 38 - k * 4)], FINE * 1.2, color=shade(yew, 0.5), alpha=0.8)
    for t in (-0.9, 0.3):
        a.shape(ellipse(180 + 10 * math.cos(t), 20 + 10 * math.sin(t), 11, 4.5, 16, rot=t), rgb("#4f7c34"), outline=FINE * 1.4, depth=1, mottle=0)
    return a.image()


def holy_amulet(seed=2030):
    """Holy Symbol (Amulet): a silver sun disc hanging from its chain, the
    chain lying in a loop above it."""
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    loop = ellipse(m, m - 18, 44, 40, 48)
    a.ink(loop, 6, closed=True, color=INK)
    a.ink(loop, 2.6, closed=True, color=SILVER)
    for k in range(0, 48, 3):
        x, y = loop[k]
        dot(a, x, y, 1.4, shade(SILVER, 0.5))
    cx, cy = m, m + 36
    rays = []
    for k in range(24):
        t = k * math.pi / 12
        R = 30 if k % 2 == 0 else 22
        rays.append((cx + R * math.cos(t), cy + R * math.sin(t)))
    soft_shadow(a, rays)
    a.shape(rays, SILVER, outline=O, corner=0, wob=0.1, depth=2, light_k=0.5, mottle=0)
    a.shape(ellipse(cx, cy, 13, 13, 24), GOLD, outline=FINE * 1.5, depth=2, light_k=0.5, mottle=0)
    return a.image()


def holy_emblem(seed=2031):
    """Holy Symbol (Emblem): a sacred sign inlaid on a small enamel badge
    (worn on a shield or tabard)."""
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    badge = [(m - 36, m - 40), (m + 36, m - 40), (m + 36, m), (m, m + 44), (m - 36, m)]
    soft_shadow(a, badge)
    a.shape(badge, GOLD, outline=O, corner=6, depth=3, light_k=0.5, mottle=0)
    inner = [(m - 26, m - 30), (m + 26, m - 30), (m + 26, m - 2), (m, m + 30), (m - 26, m - 2)]
    a.shape(inner, rgb("#3f5f9a"), outline=FINE * 1.5, corner=4, depth=2, light_k=0.3, mottle=0)
    a.ink([(m, m - 24), (m, m + 18)], 6, color=GOLD, taper=False)
    a.ink([(m - 16, m - 10), (m + 16, m - 10)], 6, color=GOLD, taper=False)
    return a.image()


def holy_reliquary(seed=2032):
    """Holy Symbol (Reliquary): a tiny gilded box holding a sacred relic,
    a crystal window on its lid."""
    w, h = 120, 100
    a = Art(w, h, seed)
    box = rect(18, 18, w - 18, h - 18)
    soft_shadow(a, box)
    a.shape(box, GOLD, outline=O, corner=6, depth=4, light_k=0.5, mottle=0.03)
    a.ink(rect(26, 26, w - 26, h - 26), FINE * 1.3, closed=True, color=shade(GOLD, 0.4), alpha=0.8)
    a.shape(ellipse(w / 2, h / 2, 18, 13, 24), GLASS, outline=FINE * 1.6, depth=2, light_k=0.6, mottle=0)
    a.shape(rect(w / 2 - 8, h / 2 - 3, w / 2 + 8, h / 2 + 3), rgb("#efe8d6"), outline=FINE * 1.1, corner=2, depth=1, mottle=0, shade_k=0.2, light_k=0, ao=0)
    for x, y in ((26, 26), (w - 26, 26), (26, h - 26), (w - 26, h - 26)):
        dot(a, x, y, 3.5, rgb("#c84a5e"))
    return a.image()


# -- tools and hardware -------------------------------------------------------------------------


def ball_bearings(seed=2040):
    """Ball Bearings: a small pouch spilling a scatter of steel balls."""
    s = 150
    a = Art(s, s, seed)
    for _ in range(26):
        x, y = 92 + a.rng.gauss(0, 20), 92 + a.rng.gauss(0, 18)
        soft_shadow(a, (x, y), 4.5, 2, 2, 0.3, 1.5)
        a.shape(ellipse(x, y, 4.5, 4.5, 14), STEEL, outline=FINE * 1.2, depth=1.5, light_k=0.7, mottle=0, ao=0)
        dot(a, x - 1.5, y - 1.5, 1.2, (250, 250, 250))
    a.shape(blob(52, 52, 30, a.rng, 9, 0.08), LEATHER, smooth=True, outline=O, depth=6)
    a.shape(ellipse(70, 70, 12, 9, 20, rot=0.8), shade(LEATHER, 0.35), outline=FINE * 1.5, depth=2, mottle=0)
    a.ink([(36, 40), (60, 34)], FINE * 1.6, color=TWINE)
    return a.image()


def bell(seed=2041):
    """Bell: a brass hand bell lying on its side: flared mouth, wooden grip."""
    w, h = 140, 100
    a = Art(w, h, seed)
    body = chaikin([(52, 34), (82, 28), (112, 18), (116, 50), (112, 82), (82, 72), (52, 66)], True, 2)
    soft_shadow(a, body)
    handle(a, 14, 50, 54, 50, 10, WOOD_DARK)
    a.shape(body, BRASS, outline=O, corner=0, depth=5, light_k=0.5, mottle=0.03)
    a.shape(ellipse(113, 50, 7, 31, 30), shade(BRASS, 0.45), outline=FINE * 1.6, depth=2, mottle=0)
    a.ink([(66, 36), (100, 26)], FINE * 1.6, color=tint(BRASS, 0.6), alpha=0.9)
    return a.image()


def blanket(seed=2042):
    """Blanket (colorable): a wool blanket folded in a square, darker stripes
    near the ends and a fringe."""
    w, h = 220, 180
    a = Art(w, h, seed)
    body = rect(24, 20, w - 24, h - 20)

    def det(art, path):
        for x in (52, 62, w - 62, w - 52):
            art.shape(rect(x - 3, 20, x + 3, h - 20), shade(RED, 0.35), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        art.ink([(30, h / 2), (w - 30, h / 2)], DETAIL, color=shade(RED, 0.55), alpha=0.8)
        art.ink([(30, h / 2 + 6), (w - 30, h / 2 + 6)], FINE * 1.4, color=tint(RED, 0.4), alpha=0.6)

    a.shape(body, RED, corner=12, depth=9, light_k=0.35, detail=det)
    for y in range(28, h - 24, 9):
        for x0, sgn in ((24, -1), (w - 24, 1)):
            a.ink([(x0, y), (x0 + sgn * 12, y + a.rng.uniform(-2, 2))], FINE * 1.3, color=INK)
    return a.image()


def block_and_tackle(seed=2043):
    """Block and Tackle: two wooden pulley blocks with iron hooks, the rope
    reeved between them and its loose end coiled."""
    w, h = 260, 160
    a = Art(w, h, seed)
    rope = rgb("#cfae72")
    for dy in (-10, 0, 10):
        a.ink([(70, 70 + dy), (182, 76 + dy)], 9, color=INK, taper=False)
        a.ink([(70, 70 + dy), (182, 76 + dy)], 5, color=rope, taper=False)
    tail = chaikin([(70, 84), (110, 120), (160, 130), (200, 120), (220, 140)], False, 2)
    a.ink(tail, 9, color=INK, taper=False)
    a.ink(tail, 5, color=rope, taper=False)
    for cx, cy, flip in ((60, 72, -1), (192, 78, 1)):
        a.shape(rect(cx - 20, cy - 28, cx + 20, cy + 28), WOOD, outline=O, corner=12, depth=4)
        a.shape(ellipse(cx, cy, 13, 13, 24), IRON, outline=FINE * 1.5, depth=2, light_k=0.5, mottle=0)
        dot(a, cx, cy, 4, shade(IRON, 0.5))
        hx = cx + flip * 38
        a.ink([(cx + flip * 20, cy), (hx, cy)], 9, color=INK, taper=False)
        a.ink([(cx + flip * 20, cy), (hx, cy)], 5, color=IRON, taper=False)
        hook = [(hx + flip * 8 * math.cos(t), cy + 10 + 10 * math.sin(t)) for t in [-math.pi / 2 + k * math.pi / 8 for k in range(13)]]
        a.ink(hook, 9, color=INK, taper=False)
        a.ink(hook, 5, color=IRON, taper=False)
    return a.image()


def caltrop(a, x, y, r=11):
    """One caltrop from above: four spikes, one always pointing up (a dot)."""
    ang = a.rng.uniform(0, 2 * math.pi)
    soft_shadow(a, (x, y), r * 0.7, 2, 3, 0.3, 2)
    for k in range(3):
        t = ang + k * 2 * math.pi / 3
        tip = (x + r * math.cos(t), y + r * math.sin(t))
        px, py = -math.sin(t) * 3, math.cos(t) * 3
        a.shape([(x + px, y + py), tip, (x - px, y - py)], shade(IRON, 0.05), outline=FINE * 1.3, corner=0, wob=0.05, depth=1, mottle=0, ao=0)
    a.shape(ellipse(x, y, 3.5, 3.5, 12), STEEL, outline=FINE * 1.2, depth=1, mottle=0, ao=0)


def caltrops(seed=2044):
    """Caltrops: a bag's worth scattered over a 5-ft square's patch."""
    s = 220
    a = Art(s, s, seed)
    spots = []
    while len(spots) < 20:
        x, y = a.rng.uniform(20, s - 20), a.rng.uniform(20, s - 20)
        if all(math.hypot(x - u, y - v) > 26 for u, v in spots):
            spots.append((x, y))
    for x, y in spots:
        caltrop(a, x, y, a.rng.uniform(10, 13))
    return a.image()


def scroll_case(seed=2045):
    """Map or Scroll Case: a leather tube with capped ends and a strap."""
    w, h = 240, 80
    a = Art(w, h, seed)
    ang = -0.08
    x, y = 26, 44
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    soft_shadow(a, loc(rect(x, y - 18, x + 190, y + 18)))
    a.shape(loc(rect(x, y - 17, x + 190, y + 17)), LEATHER, outline=O, corner=8, depth=5, light_k=0.35)
    for x0 in (x - 4, x + 166):
        a.shape(loc(rect(x0, y - 20, x0 + 28, y + 20)), LEATHER_DARK, outline=O, corner=7, depth=4, light_k=0.3)
        a.shape(loc(rect(x0 + 10, y - 21, x0 + 16, y + 21)), BRASS, outline=FINE * 1.3, corner=1, depth=1, mottle=0)
    a.ink(loc([(x + 40, y + 17), (x + 100, y + 30), (x + 150, y + 17)]), 5, color=LEATHER_DARK)
    return a.image()


def iron_chain(seed=2046):
    """Chain: ten feet of heavy chain lying in a loose curve."""
    w, h = 260, 160
    a = Art(w, h, seed)
    pts = chaikin([(20, 120), (70, 40), (130, 50), (150, 120), (210, 130), (240, 50)], False, 3)
    chain(a, pts, 18, color=IRON)
    return a.image()


def piton(a, x, y, ang, L=40):
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    a.shape(loc([(x, y - 4), (x + L, y - 1), (x + L + 6, y), (x + L, y + 1), (x, y + 4)]), STEEL, outline=FINE * 1.4, corner=0, wob=0.05, depth=1, mottle=0)
    a.shape(loc(ellipse(x - 4, y, 7, 7, 16)), IRON, outline=FINE * 1.3, depth=1, mottle=0)
    dot(a, *loc([(x - 4, y)])[0], 2.5, INK)


def climbers_kit(seed=2047):
    """Climber's Kit: a leather harness, gloves, pitons, boot tips and a
    small hammer laid out on their roll."""
    w, h = 260, 200
    a = Art(w, h, seed)
    a.shape(rect(14, 20, w - 14, h - 16), rgb("#b89a6a"), corner=10, depth=6, light_k=0.3)
    # Harness straps.
    for pts in ([(40, 50), (120, 40), (200, 50)], [(40, 64), (120, 56), (200, 64)]):
        a.ink(pts, 13, color=INK, taper=False)
        a.ink(pts, 8, color=LEATHER_DARK, taper=False)
    ring(a, 120, 48, 10, 4.5, INK)
    ring(a, 120, 48, 10, 2.5, STEEL)
    for k in range(6):
        piton(a, 40 + k * 26, 104 + (k % 2) * 8, -1.2 + k * 0.05, 34)
    hammer_at(a, 190, 170, -0.9, 60)
    for gx in (64, 104):
        g = chaikin([(gx - 14, 170), (gx - 16, 140), (gx - 6, 134), (gx + 4, 134), (gx + 14, 142), (gx + 14, 170)], True, 2)
        a.shape(g, LEATHER, outline=O, depth=3, smooth=False)
        for f in range(3):
            a.ink([(gx - 8 + f * 7, 136), (gx - 8 + f * 7, 124)], 7, color=INK, taper=False)
            a.ink([(gx - 8 + f * 7, 136), (gx - 8 + f * 7, 124)], 3.5, color=LEATHER, taper=False)
    return a.image()


def component_pouch(seed=2048):
    """Component Pouch: a belt pouch with flap and compartments; a few
    spell components (a feather, a pinch of sulfur, a bat-guano pellet)
    spilled beside it."""
    w, h = 170, 150
    a = Art(w, h, seed)
    a.ink([(110, 110), (150, 92)], 3, color=rgb("#e6dcc4"))
    for k in range(5):
        a.ink([(116 + k * 7, 106 - k * 3), (110 + k * 7, 96 - k * 3)], FINE, color=rgb("#e6dcc4"))
    a.shape(blob(140, 130, 8, a.rng, 7, 0.2), rgb("#e0cc4a"), outline=FINE * 1.3, depth=1, mottle=0)
    a.shape(ellipse(118, 136, 5, 5, 12), rgb("#4a3a2a"), outline=FINE * 1.2, depth=1, mottle=0)
    body = rect(20, 24, 120, 118)
    soft_shadow(a, body)
    a.shape(body, LEATHER, outline=O, corner=14, depth=6, light_k=0.3)
    for x in (52, 86):
        a.ink([(x, 64), (x, 112)], FINE * 1.5, color=shade(LEATHER, 0.5), alpha=0.8)
    flap = chaikin([(20, 30), (120, 30), (118, 66), (70, 78), (22, 66)], True, 2)
    a.shape(flap, LEATHER_DARK, outline=O, depth=4, light_k=0.3)
    a.ink(chaikin([(28, 38), (112, 38), (110, 60), (70, 70), (30, 60)], True, 2), FINE * 1.2, closed=True, color=tint(LEATHER_DARK, 0.3), alpha=0.7)
    a.shape(ellipse(70, 70, 7, 7, 16), BRASS, outline=FINE * 1.4, depth=1, mottle=0)
    return a.image()


def crowbar(seed=2049):
    """Crowbar: an iron bar, a flattened wedge at one end and a curved
    claw at the other."""
    w, h = 270, 110
    a = Art(w, h, seed)
    shaft = [(30, 80), (200, 40)]
    a.ink(shaft, 17, color=INK, taper=False, wob=0)
    a.ink(shaft, 10, color=shade(IRON, 0.1), taper=False, wob=0)
    a.ink([(40, 74), (196, 36)], 2.5, color=tint(IRON, 0.4), alpha=0.7, taper=False)
    claw = chaikin([(200, 40), (226, 30), (246, 42), (248, 62), (236, 72)], False, 2)
    a.ink(claw, 17, color=INK, taper=False, wob=0)
    a.ink(claw, 10, color=shade(IRON, 0.1), taper=False, wob=0)
    a.shape([(232, 66), (244, 82), (228, 78)], shade(IRON, 0.1), outline=FINE * 1.5, corner=0, wob=0, depth=1, mottle=0)
    a.shape([(16, 82), (34, 72), (36, 88)], shade(IRON, 0.1), outline=FINE * 1.5, corner=0, wob=0, depth=1, mottle=0)
    return a.image()


def grappling_hook(seed=2050):
    """Grappling Hook: four curved iron tines around a shank (from above),
    a rope tied to its ring."""
    s = 200
    a = Art(s, s, seed)
    cx, cy = 80, 80
    rope = rgb("#cfae72")
    tail = chaikin([(cx + 20, cy + 20), (130, 120), (120, 160), (170, 180), (190, 150)], False, 2)
    a.ink(tail, 11, color=INK, taper=False)
    a.ink(tail, 6.5, color=rope, taper=False)
    for k in range(4):
        t = k * math.pi / 2 + math.pi / 4
        arc = [(cx + (14 + 34 * u) * math.cos(t + 0.5 * u * u), cy + (14 + 34 * u) * math.sin(t + 0.5 * u * u)) for u in [i / 10 for i in range(11)]]
        a.ink(arc, 15, color=INK, taper=False)
        a.ink(arc, 8, color=IRON, taper=False)
        tx, ty = arc[-1]
        a.shape(ellipse(tx, ty, 5, 5, 12), STEEL, outline=FINE * 1.3, depth=1, mottle=0)
    a.shape(ellipse(cx, cy, 15, 15, 24), IRON, outline=O, depth=2, light_k=0.5, mottle=0)
    ring(a, cx + 14, cy + 14, 7, 5, INK)
    ring(a, cx + 14, cy + 14, 7, 2.5, STEEL)
    return a.image()


def roll_bandage(a, x, y, r=12):
    a.shape(ellipse(x, y, r, r, 24), LINEN, outline=FINE * 1.5, depth=2, mottle=0)
    a.ink([(x + r * 0.5 * math.cos(t), y + r * 0.5 * math.sin(t)) for t in [k * 0.4 for k in range(16)]], FINE, color=shade(LINEN, 0.4), alpha=0.8)


def healers_kit(seed=2051):
    """Healer's Kit: an open leather case with bandage rolls, salve tins, a
    splint and small vials."""
    w, h = 220, 170
    a = Art(w, h, seed)
    a.shape(rect(14, 10, w - 14, 60), LEATHER_DARK, corner=10, depth=5, light_k=0.2)
    a.shape(rect(14, 50, w - 14, h - 10), LEATHER, corner=10, depth=6, light_k=0.3)
    a.shape(rect(26, 62, w - 26, h - 22), shade(LEATHER, 0.35), outline=DETAIL, corner=6, depth=4, shade_k=0, light_k=0, ao=0.4)
    for x in (52, 82, 112):
        roll_bandage(a, x, 90, 13)
    for x in (52, 82):
        a.shape(ellipse(x, 128, 12, 12, 20), SILVER, outline=FINE * 1.5, depth=2, light_k=0.5, mottle=0)
        a.ink([(x - 6, 128), (x + 6, 128)], FINE, color=shade(SILVER, 0.5))
    a.shape(rect(140, 72, 152, 140), WOOD_LIGHT, outline=FINE * 1.5, corner=3, depth=1, mottle=0)
    for k, c in enumerate((rgb("#c8443a"), rgb("#6fb84a"))):
        bottle_side(a, 160 + k * 18, 140, -math.pi / 2, 64, 7, c)
    a.shape(rect(w / 2 - 14, 20, w / 2 + 14, 48), PAPER, outline=FINE * 1.5, corner=3, depth=1, mottle=0)
    a.ink([(w / 2, 24), (w / 2, 44)], 5, color=rgb("#c8443a"), taper=False)
    a.ink([(w / 2 - 10, 34), (w / 2 + 10, 34)], 5, color=rgb("#c8443a"), taper=False)
    return a.image()


def lantern_body(a, cx, cy, r, open_=True, beam=None):
    """A round metal lantern from above: cap, vents, and (if open) its
    light — a halo, or a cone toward `beam` (an angle) for a bullseye."""
    if open_:
        if beam is None:
            glow(a, cx, cy, r * 2.4, rgb("#ffd27a"), 0.45)
    soft_shadow(a, (cx, cy), r)
    a.shape(ellipse(cx, cy, r, r, 36), IRON, outline=O, depth=4, light_k=0.5, mottle=0)
    a.shape(ellipse(cx, cy, r * 0.62, r * 0.62, 28), shade(IRON, 0.25), outline=FINE * 1.5, depth=2, mottle=0)
    for k in range(6):
        t = k * math.pi / 3
        dot(a, cx + r * 0.42 * math.cos(t), cy + r * 0.42 * math.sin(t), 2.2, rgb("#ffe39a") if open_ else INK)
    a.shape(ellipse(cx, cy, r * 0.22, r * 0.22, 16), shade(IRON, 0.1), outline=FINE * 1.3, depth=1, mottle=0)


def hooded_lantern(seed=2052, lit=True):
    """Hooded Lantern: a round lantern with a bail handle and its hood (a
    sliding shutter) raised or lowered."""
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    if lit:
        glow(a, m, m, 70, rgb("#ffd27a"), 0.45)
    bail = [(m - 30, m), (m - 26, m - 30), (m, m - 44), (m + 26, m - 30), (m + 30, m)]
    a.ink(chaikin(bail, False, 2), 7, color=INK, taper=False)
    a.ink(chaikin(bail, False, 2), 3, color=IRON, taper=False)
    a.shape(ellipse(m, m, 34, 34, 40), IRON, outline=O, depth=4, light_k=0.5, mottle=0)
    glass = rgb("#ffe39a") if lit else shade(GLASS, 0.3)
    a.shape(ellipse(m, m, 24, 24, 32), glass, outline=FINE * 1.6, depth=2, light_k=0.4, shade_k=0.2, mottle=0)
    for k in range(4):
        t = k * math.pi / 2 + math.pi / 4
        a.ink([(m + 10 * math.cos(t), m + 10 * math.sin(t)), (m + 24 * math.cos(t), m + 24 * math.sin(t))], FINE * 1.5, color=IRON, taper=False)
    a.shape(ellipse(m, m, 10, 10, 20), shade(IRON, 0.15), outline=FINE * 1.4, depth=2, mottle=0)
    if not lit:
        # The hood lowered over the glass.
        a.shape([(m - 30, m - 6), (m + 30, m - 6), (m + 26, m + 22), (m - 26, m + 22)], shade(IRON, 0.15), outline=O, corner=8, depth=3, light_k=0.4, mottle=0)
    return a.image()


def bullseye_lantern(seed=2053, lit=True):
    """Bullseye Lantern: a squat tin lantern with a lens on one side,
    throwing its light in a cone."""
    w, h = 240, 150
    a = Art(w, h, seed)
    cy = h / 2
    if lit:
        # The cone fades out along its length (stacked, ever shorter cones).
        for k in range(6):
            end = 120 + k * 18
            spread = 12 + (end - 100) * 0.42
            cone = skia.Path()
            cone.moveTo(96, cy - 12)
            cone.lineTo(end, cy - spread)
            cone.quadTo(end + 14, cy, end, cy + spread)
            cone.lineTo(96, cy + 12)
            cone.close()
            a.fill_path(cone, rgb("#ffd27a"), 0.17, blur=8)
        glow(a, 60, cy, 50, rgb("#ffd27a"), 0.25)
    soft_shadow(a, (60, cy), 34)
    a.shape(ellipse(60, cy, 34, 34, 40), shade(SILVER, 0.2), outline=O, depth=4, light_k=0.5, mottle=0)
    a.shape(rect(80, cy - 18, 102, cy + 18), shade(SILVER, 0.25), outline=O, corner=4, depth=2, mottle=0)
    a.shape(ellipse(101, cy, 6, 17, 24), rgb("#ffe39a") if lit else GLASS, outline=FINE * 1.6, depth=1, mottle=0, shade_k=0, light_k=0.3)
    a.shape(ellipse(60, cy, 14, 14, 20), shade(SILVER, 0.4), outline=FINE * 1.4, depth=2, mottle=0)
    for k in range(8):
        t = k * math.pi / 4
        dot(a, 60 + 24 * math.cos(t), cy + 24 * math.sin(t), 2, INK)
    a.shape(rect(18, cy - 5, 30, cy + 5), shade(SILVER, 0.3), outline=FINE * 1.4, corner=2, depth=1, mottle=0)
    return a.image()


def padlock(seed=2054):
    """Lock: an iron padlock with its shackle, and its key beside it."""
    w, h = 150, 140
    a = Art(w, h, seed)
    shackle = [(44 + 22 * math.cos(t), 54 + 26 * math.sin(t)) for t in [math.pi + k * math.pi / 12 for k in range(13)]]
    a.ink(shackle, 14, color=INK, taper=False)
    a.ink(shackle, 7, color=STEEL, taper=False)
    body = rect(14, 50, 76, 112)
    soft_shadow(a, body)
    a.shape(body, IRON, outline=O, corner=10, depth=4, light_k=0.5, mottle=0)
    a.shape([(42, 72), (48, 72), (49, 90), (41, 90)], INK, outline=0, corner=1, shade_k=0, light_k=0, ao=0, mottle=0)
    dot(a, 45, 72, 5, INK)
    # Key.
    ring(a, 104, 100, 11, 8, INK)
    ring(a, 104, 100, 11, 4, BRASS)
    a.ink([(112, 92), (140, 60)], 9, color=INK, taper=False)
    a.ink([(112, 92), (140, 60)], 5, color=BRASS, taper=False)
    for t in (0.0, 9.0):
        a.ink([(136 - t * 0.7, 66 + t * 0.8), (144 - t * 0.7, 74 + t * 0.8)], 6, color=BRASS, taper=False)
    return a.image()


def steel_mirror(seed=2055):
    """Mirror: a polished steel hand mirror with a wooden handle."""
    w, h = 120, 210
    a = Art(w, h, seed)
    handle(a, 60, 120, 60, 196, 13, WOOD_DARK)
    soft_shadow(a, (60, 70), 50)
    a.shape(ellipse(60, 70, 50, 54, 48), BRASS, outline=O, depth=4, light_k=0.5, mottle=0)
    a.shape(ellipse(60, 70, 40, 44, 48), rgb("#d6dde2"), outline=FINE * 1.6, depth=3, light_k=0.7, shade_k=0.3, mottle=0.04)
    _glint(a, [(36, 60), (50, 38)])
    _glint(a, [(42, 76), (60, 46)], 0.6)
    return a.image()


def net(seed=2056):
    """Net: a weighted throwing net spread out, lead weights at its rim."""
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    cord = rgb("#cdb685")
    rim = [(m + (96 + a.rng.uniform(-8, 8)) * math.cos(t), m + (96 + a.rng.uniform(-8, 8)) * math.sin(t)) for t in [k * 2 * math.pi / 12 for k in range(12)]]
    rim = chaikin(rim, True, 2)

    path = skia.Path()
    path.moveTo(*rim[0])
    for p in rim[1:]:
        path.lineTo(*p)
    path.close()
    with a.clip(path):
        for k in range(-10, 11):
            off = k * 18
            for ang in (0.7, -0.7):
                dx, dy = math.cos(ang), math.sin(ang)
                px, py = -dy, dx
                pts = [(m + px * off + dx * t, m + py * off + dy * t + 3 * math.sin(t / 15)) for t in range(-150, 151, 10)]
                a.ink(pts, 4.5, color=INK, alpha=0.9, taper=False, wob=0.4)
                a.ink(pts, 2.2, color=cord, taper=False, wob=0.4)
    a.ink(rim, 7, closed=True, color=INK)
    a.ink(rim, 3.5, closed=True, color=cord)
    for k in range(0, len(rim), max(1, len(rim) // 8)):
        x, y = rim[k]
        a.shape(ellipse(x, y, 7, 7, 14), rgb("#6f727a"), outline=FINE * 1.4, depth=1.5, mottle=0)
    return a.image()


def paper_sheets(seed=2057):
    """Paper: a small stack of clean, square-cut sheets."""
    w, h = 150, 170
    a = Art(w, h, seed)
    for k, ang in enumerate((0.18, -0.08, 0.04)):
        pts = rot_pts(rect(28, 26, 122, 144), 75, 85, ang)
        if k == 0:
            soft_shadow(a, pts)
        a.shape(pts, vary(a.rng, PAPER, 0.02), outline=DETAIL * 1.1, corner=1, depth=2, shade_k=0.2, light_k=0, mottle=0.02)
    for y in range(48, 130, 12):
        a.ink(rot_pts([(40, y), (110, y)], 75, 85, 0.04), FINE * 0.9, color=rgb("#a8b8c8"), alpha=0.6, taper=False)
    return a.image()


def parchment(seed=2058):
    """Parchment: a few uneven cream sheets of scraped hide, the top one
    curling at an edge, beside a rolled one."""
    w, h = 210, 170
    a = Art(w, h, seed)
    for k, ang in enumerate((0.12, -0.1)):
        pts = rot_pts([(36, 26), (150, 30), (146, 156), (38, 152)], 92, 92, ang)
        if k == 0:
            soft_shadow(a, pts)
        a.shape(pts, vary(a.rng, PARCH, 0.03), outline=DETAIL * 1.1, corner=8, depth=6, shade_k=0.25, light_k=0.15, mottle=0.06)
    a.shape([(124, 132), (148, 152), (138, 158)], shade(PARCH, 0.2), outline=FINE * 1.5, corner=3, depth=1, mottle=0)
    roll = rect(150, 24, 190, 150)
    soft_shadow(a, roll)
    a.shape(roll, PARCH, outline=DETAIL * 1.3, corner=16, depth=6, light_k=0.3)
    a.ink([(170, 26), (170, 148)], FINE * 1.2, color=shade(PARCH, 0.4), alpha=0.7)
    a.ink([(150, 86), (190, 84)], 6, color=INK, taper=False)
    a.ink([(150, 86), (190, 84)], 3, color=rgb("#9a3a3a"), taper=False)
    return a.image()


def perfume(seed=2059):
    """Perfume: a faceted glass bottle of rose-tinted scent with a
    teardrop crystal stopper, lying on its side."""
    w, h = 140, 90
    a = Art(w, h, seed)
    cy = 46
    body = [(18, cy - 18), (34, cy - 30), (70, cy - 30), (84, cy - 14), (84, cy + 14), (70, cy + 30), (34, cy + 30), (18, cy + 18)]
    soft_shadow(a, body)
    a.shape(rect(80, cy - 7, 98, cy + 7), GLASS, outline=FINE * 1.6, corner=2, depth=1, mottle=0)
    a.shape(body, rgb("#e7a8c0"), outline=O, corner=3, depth=4, light_k=0.55, mottle=0)
    for x in (34, 70):
        a.ink([(x, cy - 28), (x, cy + 28)], FINE * 1.1, color=tint(rgb("#e7a8c0"), 0.5), alpha=0.8)
    stop = chaikin([(96, cy), (112, cy - 16), (130, cy), (112, cy + 16)], True, 2)
    a.shape(stop, rgb("#d6e6ea"), outline=FINE * 1.8, depth=2, light_k=0.6, mottle=0)
    _glint(a, [(26, cy - 16), (40, cy - 24)])
    a.ink([(84, cy + 8), (102, cy + 22), (98, cy + 34)], 2.5, color=GOLD)
    return a.image()


def pole(seed=2060):
    """Pole: ten feet of plain wooden pole (two squares long)."""
    w, h = 520, 50
    a = Art(w, h, seed)
    handle(a, 16, 26, w - 16, 24, 14, WOOD_LIGHT)
    for x in (120, 300, 430):
        a.ink([(x, 22), (x + 16, 21)], FINE * 1.2, color=shade(WOOD_LIGHT, 0.5), alpha=0.7)
    return a.image()


def iron_pot(seed=2061):
    """Iron Pot: a lidless cooking pot from above, its bail handle laid
    down beside it."""
    s = 170
    a = Art(s, s, seed)
    m = s / 2
    bail = [(m - 62, m), (m - 56, m + 50), (m, m + 78), (m + 56, m + 50), (m + 62, m)]
    soft_shadow(a, (m, m), 56)
    a.shape(ellipse(m, m, 58, 58, 48), shade(IRON, 0.15), outline=O, depth=6, light_k=0.4, mottle=0.04)
    a.shape(ellipse(m, m, 46, 46, 48), shade(IRON, 0.32), outline=DETAIL, depth=8, shade_k=0.5, light_k=0.2, ao=0.5, mottle=0.05)
    a.ink([(m - 30, m - 4), (m - 6, m - 28)], FINE * 1.6, color=tint(IRON, 0.3), alpha=0.5)
    a.ink(chaikin(bail, False, 2), 8, color=INK, taper=False)
    a.ink(chaikin(bail, False, 2), 4, color=IRON, taper=False)
    for x in (m - 60, m + 60):
        a.shape(ellipse(x, m, 7, 7, 14), IRON, outline=FINE * 1.4, depth=1, mottle=0)
    return a.image()


def pouch(seed=2062):
    """Pouch (colorable): a small cloth drawstring pouch."""
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m + 8), 36)
    a.shape(blob(m, m + 10, 38, a.rng, 9, 0.06), RED, smooth=True, outline=O, depth=8, light_k=0.35)
    gather = scallop(m, m - 26, 18, a.rng, 7, 0.25, ry=11)
    a.shape(gather, shade(RED, 0.15), outline=DETAIL * 1.2, depth=3, mottle=0)
    a.ink([(m - 22, m - 16), (m + 20, m - 18)], 6, color=INK, taper=False)
    a.ink([(m - 22, m - 16), (m + 20, m - 18)], 3, color=TWINE, taper=False)
    a.ink([(m + 20, m - 18), (m + 36, m - 4), (m + 44, m + 6)], 3, color=TWINE)
    return a.image()


def portable_ram(seed=2063):
    """Ram, Portable: an iron-capped log with grab handles along it."""
    w, h = 300, 130
    a = Art(w, h, seed)
    body = rect(30, 44, 250, 86)
    soft_shadow(a, body)
    a.shape(body, WOOD, outline=O, corner=16, depth=6, light_k=0.3, detail=lambda art, p: [art.ink([(40, y), (240, y + art.rng.uniform(-3, 3))], FINE, color=shade(WOOD, 0.45), alpha=0.6) for y in (54, 66, 76)])
    a.shape(rect(232, 36, 286, 94), IRON, outline=O, corner=14, depth=5, light_k=0.5, mottle=0)
    a.shape(ellipse(276, 65, 8, 22, 24), shade(IRON, 0.3), outline=FINE * 1.4, depth=2, mottle=0)
    for x in (70, 150):
        for y0, y1 in ((44, 18), (86, 112)):
            a.ink([(x - 14, y0), (x - 12, y1), (x + 12, y1), (x + 14, y0)], 10, color=INK, taper=False)
            a.ink([(x - 14, y0), (x - 12, y1), (x + 12, y1), (x + 14, y0)], 5, color=IRON, taper=False)
    for x in (40, 200):
        a.shape(rect(x, 41, x + 12, 89), IRON, outline=FINE * 1.5, corner=2, depth=1, mottle=0)
    return a.image()


def rations(seed=2064):
    """Rations: a day's dry food on its cloth wrap: hardtack, jerky strips,
    dried fruit and nuts."""
    w, h = 190, 160
    a = Art(w, h, seed)
    a.shape(rot_pts(rect(20, 18, 170, 142), 95, 80, 0.08), LINEN, corner=8, depth=5, light_k=0.25, mottle=0.05)
    for x, y in ((56, 52), (92, 46), (60, 88)):
        a.shape(rect(x - 18, y - 16, x + 18, y + 16), rgb("#d8b47a"), outline=DETAIL * 1.2, corner=4, depth=3, mottle=0.05)
        for dx in (-8, 0, 8):
            for dy in (-7, 7):
                dot(a, x + dx, y + dy, 1.6, shade(rgb("#d8b47a"), 0.5))
    for k in range(3):
        x = 116 + k * 14
        a.shape(rot_pts(rect(x - 5, 42, x + 5, 104), x, 73, 0.2), rgb("#7a3a2a"), outline=FINE * 1.6, corner=3, depth=1.5, mottle=0.05)
    for _ in range(9):
        x, y = a.rng.uniform(78, 140), a.rng.uniform(108, 128)
        a.shape(ellipse(x, y, 6, 5, 12, rot=a.rng.uniform(0, 3)), a.rng.choice((rgb("#8a4a5a"), rgb("#b88a4a"), rgb("#6a4a3a"))), outline=FINE * 1.2, depth=1, mottle=0, ao=0)
    a.ink([(30, 132), (60, 140), (90, 130)], 4, color=TWINE)
    return a.image()


def signal_whistle(seed=2065):
    """Signal Whistle: a small brass whistle on a leather cord."""
    w, h = 140, 100
    a = Art(w, h, seed)
    cord = chaikin([(30, 60), (14, 30), (40, 12), (70, 22), (60, 50)], False, 2)
    a.ink(cord, 5, color=INK, taper=False)
    a.ink(cord, 2.5, color=LEATHER, taper=False)
    body = [(56, 46), (110, 46), (124, 52), (124, 70), (110, 74), (56, 74)]
    soft_shadow(a, body)
    a.shape(body, BRASS, outline=O, corner=6, depth=3, light_k=0.5, mottle=0)
    a.shape(rect(64, 50, 78, 58), INK, outline=0, corner=1, shade_k=0, light_k=0, ao=0, mottle=0)
    ring(a, 60, 50, 5, 4, INK)
    ring(a, 60, 50, 5, 2, BRASS)
    return a.image()


def iron_spikes(seed=2066):
    """Iron Spikes: a bundle of ten spikes tied with twine."""
    w, h = 200, 110
    a = Art(w, h, seed)
    for k in range(10):
        y = 30 + k * 5.5 + a.rng.uniform(-1, 1)
        x = 22 + a.rng.uniform(-6, 6)
        pts = [(x, y - 5), (x + 130, y - 3), (x + 154, y), (x + 130, y + 3), (x, y + 5)]
        if k == 0:
            soft_shadow(a, [(20, 26), (180, 26), (180, 86), (20, 86)], alpha=0.25)
        a.shape(pts, vary(a.rng, shade(IRON, 0.05), 0.05), outline=FINE * 1.6, corner=0, wob=0.1, depth=1, mottle=0, ao=0)
        a.shape(rect(x - 4, y - 6, x + 6, y + 6), IRON, outline=FINE * 1.4, corner=2, depth=1, mottle=0, ao=0)
    for x in (60, 110):
        a.ink([(x, 22), (x + 2, 90)], 8, color=INK, taper=False)
        a.ink([(x, 22), (x + 2, 90)], 4, color=TWINE, taper=False)
    return a.image()


def spyglass(seed=2067):
    """Spyglass: a brass telescope drawn out to its three sections."""
    w, h = 300, 80
    a = Art(w, h, seed)
    ang = -0.08
    x, y = 20, 46
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    soft_shadow(a, loc(rect(x, y - 18, x + 260, y + 18)))
    for x0, x1, r in ((x + 150, x + 255, 10), (x + 80, x + 160, 14), (x, x + 92, 19)):
        a.shape(loc(rect(x0, y - r, x1, y + r)), BRASS, outline=O, corner=4, depth=3, light_k=0.55, mottle=0)
        a.shape(loc(rect(x1 - 10, y - r - 2, x1, y + r + 2)), shade(BRASS, 0.25), outline=FINE * 1.5, corner=2, depth=1, mottle=0)
    a.shape(loc(rect(x + 20, y - 20, x + 70, y + 20)), LEATHER_DARK, outline=FINE * 1.6, corner=3, depth=2, mottle=0.04)
    p = loc([(x + 2, y)])[0]
    a.shape(ellipse(p[0], p[1], 5, 17, 24, rot=ang), rgb("#8fb4c4"), outline=FINE * 1.4, depth=1, mottle=0)
    return a.image()


def ball_of_string(seed=2068):
    """String: a ball of twine with its loose end trailing."""
    w, h = 150, 120
    a = Art(w, h, seed)
    tail = chaikin([(70, 60), (100, 90), (124, 72), (140, 100)], False, 2)
    a.ink(tail, 5, color=INK, taper=False)
    a.ink(tail, 2.5, color=TWINE, taper=False)
    soft_shadow(a, (60, 58), 40)
    a.shape(ellipse(60, 58, 40, 40, 40), TWINE, outline=O, depth=6, light_k=0.35)
    for k in range(7):
        t = k * 0.45
        a.ink(ellipse(60, 58, 34, 14, 30, rot=t)[2:14], FINE * 1.3, color=shade(TWINE, 0.45), alpha=0.8)
    return a.image()


def tinderbox(seed=2069):
    """Tinderbox: a small open tin with flint, fire steel and dry tinder."""
    w, h = 170, 130
    a = Art(w, h, seed)
    tin = rgb("#8f949a")
    a.shape(rect(18, 18, 100, 46), tin, outline=O, corner=6, depth=3, light_k=0.4, mottle=0)
    a.shape(rect(18, 44, 100, 112), tin, outline=O, corner=6, depth=4, light_k=0.4, mottle=0)
    a.shape(rect(26, 52, 92, 104), shade(tin, 0.4), outline=DETAIL, corner=3, depth=3, shade_k=0, light_k=0, ao=0.5, mottle=0)
    for _ in range(14):
        x, y = a.rng.uniform(32, 86), a.rng.uniform(58, 98)
        ang = a.rng.uniform(0, 3.14)
        a.ink([(x, y), (x + 10 * math.cos(ang), y + 10 * math.sin(ang))], FINE * 1.5, color=rgb("#c8a868"))
    a.shape(blob(130, 50, 16, a.rng, 7, 0.25), rgb("#4a4e58"), outline=O, depth=2, mottle=0)
    steel = chaikin([(110, 108), (112, 86), (150, 86), (152, 108)], False, 2)
    a.ink(steel, 12, color=INK, taper=False)
    a.ink(steel, 6, color=STEEL, taper=False)
    a.ink([(110, 108), (152, 108)], 12, color=INK, taper=False)
    a.ink([(110, 108), (152, 108)], 6, color=STEEL, taper=False)
    return a.image()


def torch_at(a, x, y, ang, L=200, lit=True):
    """A torch lying on the floor: a stick with its pitch-soaked rag head."""
    ux, uy = math.cos(ang), math.sin(ang)
    hx, hy = x + ux * L, y + uy * L
    handle(a, x, y, hx, hy, 11, WOOD_DARK)
    head = rot_pts(rect(hx - 34, hy - 13, hx + 4, hy + 13), hx, hy, ang)
    a.shape(head, rgb("#5a4a3a") if lit else rgb("#a89670"), outline=O, corner=6, depth=3, mottle=0.05)
    for k in range(3):
        a.ink(rot_pts([(hx - 30 + k * 11, hy - 13), (hx - 24 + k * 11, hy + 13)], hx, hy, ang), FINE * 1.3, color=INK, alpha=0.6)
    if lit:
        flame(a, hx + ux * 16, hy + uy * 16, 20, ang)


def torch(seed=2070, lit=False):
    w, h = 320, 140
    a = Art(w, h, seed)
    torch_at(a, 20, 90, -0.12, 220, lit)
    return a.image()


# -- equipment packs ----------------------------------------------------------------------------


def _scaled(img, k, rot=0.0):
    im = img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    return im


def _backpack(color):
    from review import recolor

    return recolor(obj_camp.backpack(), color)


def _clothes(seed, color):
    """Folded clothes (only used inside the packs: the apparel itself is
    drawn with the armor)."""
    a = Art(150, 120, seed)
    a.shape(rect(14, 14, 136, 106), color, corner=10, depth=7, light_k=0.3)
    a.ink([(18, 60), (132, 60)], DETAIL, color=shade(color, 0.5), alpha=0.8)
    a.ink([(60, 18), (60, 56)], FINE * 1.4, color=shade(color, 0.45), alpha=0.7)
    a.shape(rect(70, 22, 128, 52), tint(color, 0.15), outline=FINE * 1.5, corner=4, depth=2, mottle=0)
    return a.image()


def pack(seed, size, parts):
    """An equipment pack laid out: `parts` = [(image, x, y, scale, rotation)],
    placed by center, drawn in order."""
    w, h = size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for img, x, y, k, rot in parts:
        im = _scaled(img, k, rot)
        out.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    return out


def _torches(n, seed):
    a = Art(260, 140, seed)
    for k in range(n):
        torch_at(a, 16 + k * 3, 40 + k * 14, -0.04 + k * 0.02, 200, False)
    return a.image()


def _rations(n, seed):
    a = Art(170, 150, seed)
    for k in range(n):
        x, y = 40 + (k % 3) * 44, 40 + (k // 3) * 54
        a.shape(rect(x - 20, y - 22, x + 20, y + 22), LINEN, outline=DETAIL * 1.3, corner=6, depth=4, mottle=0.05)
        a.ink([(x - 20, y), (x + 20, y)], 4, color=TWINE, taper=False)
        a.ink([(x, y - 22), (x, y + 22)], 4, color=TWINE, taper=False)
    return a.image()


def _oil_flasks(n, seed):
    imgs = [oil_flask(seed + k) for k in range(n)]
    out = Image.new("RGBA", (40 + 46 * ((n + 1) // 2) + 60, 150), (0, 0, 0, 0))
    for k, im in enumerate(imgs):
        im = _scaled(im, 0.7, 90)
        out.alpha_composite(im, (10 + (k // 2) * 46 + (k % 2) * 20, 6 + (k % 2) * 60))
    return out


def burglars_pack(seed=2100):
    return pack(
        seed,
        (520, 460),
        [
            (_backpack((70, 70, 80)), 110, 140, 0.95, 0),
            (obj_camp.waterskin(), 100, 360, 0.7, 30),
            (_rope(), 260, 380, 0.75, 0),
            (crowbar(), 340, 60, 0.75, -10),
            (hooded_lantern(seed + 1, False), 400, 160, 0.8, 0),
            (_oil_flasks(7, seed + 10), 300, 240, 0.85, 0),
            (_candles(10, seed + 20), 430, 310, 0.8, 0),
            (ball_bearings(seed + 3), 220, 70, 0.6, 0),
            (bell(seed + 4), 470, 400, 0.6, 20),
            (_rations(5, seed + 5), 370, 420, 0.55, 0),
            (tinderbox(seed + 6), 210, 300, 0.55, 0),
        ],
    )


def _rope():
    import obj_town

    return obj_town.rope_coil()


def _candles(n, seed):
    a = Art(160, 120, seed)
    for k in range(n):
        x, y = 22 + (k % 5) * 28, 30 + (k // 5) * 56
        a.shape(rot_pts(rect(x - 6, y - 24, x + 6, y + 24), x, y, 0.1), rgb("#f1e6c8"), outline=FINE * 1.6, corner=4, depth=2, mottle=0)
        a.ink([(x, y - 24), (x, y - 30)], 2, color=INK)
    return a.image()


def diplomats_pack(seed=2110):
    return pack(
        seed,
        (520, 440),
        [
            (objects.chest(), 150, 150, 0.95, 0),
            (_clothes(seed + 1, rgb("#4a5f9a")), 380, 90, 0.95, 0),
            (scroll_case(seed + 2), 150, 330, 0.85, 0),
            (scroll_case(seed + 3), 160, 390, 0.85, 4),
            (paper_sheets(seed + 4), 390, 230, 0.7, 0),
            (ink_bottle(seed + 5), 470, 300, 0.75, 0),
            (ink_pen(seed + 6), 400, 330, 0.65, -20),
            (obj_storage.oil_lamp(), 330, 410, 0.75, 0),
            (_oil_flasks(2, seed + 7), 470, 400, 0.7, 0),
            (perfume(seed + 8), 300, 300, 0.7, 30),
            (tinderbox(seed + 9), 470, 180, 0.5, 0),
        ],
    )


def dungeoneers_pack(seed=2120):
    return pack(
        seed,
        (520, 460),
        [
            (_backpack((90, 80, 60)), 110, 140, 0.95, 0),
            (_torches(10, seed + 1), 370, 90, 0.9, 0),
            (crowbar(seed + 2), 330, 200, 0.75, 8),
            (_rope(), 270, 370, 0.75, 0),
            (caltrops(seed + 3), 440, 300, 0.55, 0),
            (_rations(10, seed + 4), 110, 360, 0.75, 0),
            (obj_camp.waterskin(), 440, 400, 0.6, -30),
            (_oil_flasks(2, seed + 5), 200, 280, 0.7, 0),
            (tinderbox(seed + 6), 360, 280, 0.5, 0),
        ],
    )


def entertainers_pack(seed=2130):
    return pack(
        seed,
        (540, 460),
        [
            (_backpack((150, 70, 140)), 110, 140, 0.95, 0),
            (obj_camp.blanket_roll(), 130, 390, 0.7, 0),
            (_clothes(seed + 1, rgb("#c8a03a")), 330, 70, 0.8, -6),
            (_clothes(seed + 2, rgb("#5aa08a")), 340, 110, 0.8, 4),
            (_clothes(seed + 3, rgb("#a84a8a")), 350, 150, 0.8, -2),
            (steel_mirror(seed + 4), 480, 120, 0.7, 20),
            (bullseye_lantern(seed + 5, False), 280, 260, 0.75, 0),
            (bell(seed + 6), 470, 250, 0.6, 0),
            (_oil_flasks(8, seed + 7), 420, 340, 0.75, 0),
            (_rations(9, seed + 8), 300, 400, 0.6, 0),
            (obj_camp.waterskin(), 480, 420, 0.55, 30),
            (tinderbox(seed + 9), 220, 310, 0.5, 0),
        ],
    )


def explorers_pack(seed=2140):
    return pack(
        seed,
        (520, 460),
        [
            (_backpack((80, 110, 70)), 110, 140, 0.95, 0),
            (obj_camp.blanket_roll(), 140, 390, 0.7, 0),
            (_torches(10, seed + 1), 370, 90, 0.9, 0),
            (_rope(), 400, 250, 0.7, 0),
            (_rations(10, seed + 2), 320, 390, 0.7, 0),
            (obj_camp.waterskin(), 470, 400, 0.55, -20),
            (_oil_flasks(2, seed + 3), 250, 260, 0.7, 0),
            (tinderbox(seed + 4), 260, 180, 0.5, 0),
        ],
    )


def priests_pack(seed=2150):
    return pack(
        seed,
        (500, 420),
        [
            (_backpack((200, 190, 160)), 110, 140, 0.95, 0),
            (_clothes(seed + 1, rgb("#e6e0cc")), 340, 80, 1.0, 0),
            (blanket(seed + 2), 340, 220, 0.8, 0),
            (_vial_item(seed + 3, 120, 70, rgb("#c8e0f0"), extra=_label(PAPER, _cross))(), 210, 320, 0.8, 0),
            (obj_storage.oil_lamp(), 330, 350, 0.7, 0),
            (_rations(7, seed + 4), 110, 360, 0.6, 0),
            (tinderbox(seed + 5), 450, 360, 0.5, 0),
        ],
    )


def scholars_pack(seed=2160):
    return pack(
        seed,
        (520, 440),
        [
            (_backpack((120, 70, 50)), 110, 140, 0.95, 0),
            (obj_tavern.closed_book(seed + 1, "#3f5a8a"), 300, 90, 0.9, 0),
            (parchment(seed + 2), 410, 120, 0.8, 0),
            (ink_bottle(seed + 3), 270, 210, 0.75, 0),
            (ink_pen(seed + 4), 380, 230, 0.6, -15),
            (obj_storage.oil_lamp(), 110, 360, 0.7, 0),
            (_oil_flasks(10, seed + 5), 330, 350, 0.8, 0),
            (tinderbox(seed + 6), 470, 300, 0.5, 0),
        ],
    )


# -- catalog ------------------------------------------------------------------------------------

SRD_GEAR = {
    "Acid": _vial_item(2001, 130, 70, rgb("#9ad04a"), extra=_bubbles),
    "Alchemist's Fire": _vial_item(2002, 140, 100, rgb("#e8702a"), kind="flask", r=26, extra=_fire_glow),
    "Antitoxin": _vial_item(2003, 130, 70, rgb("#d8e8e0"), extra=_label(PAPER, _cross)),
    "Basic Poison": _vial_item(2004, 130, 70, rgb("#4a7a3a"), extra=_label(PARCH, _skull), glass=rgb("#a6b8a8"), cap=rgb("#4a3a2e")),
    "Holy Water": _vial_item(2005, 140, 100, rgb("#bcd8f0"), kind="flask", r=24, extra=_label(PAPER, _sun), cap=SILVER),
    "Vial": _vial_item(2006, 120, 60, None),
    "Flask": hip_flask,
    "Oil": oil_flask,
    "Perfume": perfume,
    "Ink": ink_bottle,
    "Ink Pen": ink_pen,
    "Arcane Focus (Crystal)": arcane_crystal,
    "Arcane Focus (Orb)": arcane_orb,
    "Arcane Focus (Rod)": arcane_rod,
    "Druidic Focus (Sprig of Mistletoe)": mistletoe,
    "Druidic Focus (Wooden Staff)": druid_staff,
    "Druidic Focus (Yew Wand)": yew_wand,
    "Holy Symbol (Amulet)": holy_amulet,
    "Holy Symbol (Emblem)": holy_emblem,
    "Holy Symbol (Reliquary)": holy_reliquary,
    "Ball Bearings": ball_bearings,
    "Bell": bell,
    "Blanket": blanket,
    "Block and Tackle": block_and_tackle,
    "Caltrops": caltrops,
    "Map or Scroll Case": scroll_case,
    "Chain": iron_chain,
    "Climber's Kit": climbers_kit,
    "Component Pouch": component_pouch,
    "Crowbar": crowbar,
    "Grappling Hook": grappling_hook,
    "Healer's Kit": healers_kit,
    "Hooded Lantern": hooded_lantern,
    "Hooded Lantern (Closed)": lambda: hooded_lantern(2052, False),
    "Bullseye Lantern": bullseye_lantern,
    "Bullseye Lantern (Unlit)": lambda: bullseye_lantern(2053, False),
    "Lock": padlock,
    "Mirror": steel_mirror,
    "Net": net,
    "Paper": paper_sheets,
    "Parchment": parchment,
    "Pole": pole,
    "Iron Pot": iron_pot,
    "Pouch": pouch,
    "Portable Ram": portable_ram,
    "Rations": rations,
    "Signal Whistle": signal_whistle,
    "Iron Spikes": iron_spikes,
    "Spyglass": spyglass,
    "String": ball_of_string,
    "Tinderbox": tinderbox,
    "Torch": torch,
    "Lit Torch": lambda: torch(2071, True),
    "Burglar's Pack": burglars_pack,
    "Diplomat's Pack": diplomats_pack,
    "Dungeoneer's Pack": dungeoneers_pack,
    "Entertainer's Pack": entertainers_pack,
    "Explorer's Pack": explorers_pack,
    "Priest's Pack": priests_pack,
    "Scholar's Pack": scholars_pack,
}

SRD_GEAR_COLORABLE = {"Blanket", "Pouch"}
