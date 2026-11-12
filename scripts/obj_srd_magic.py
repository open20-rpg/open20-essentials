"""SRD 5.2.1 magic items (batch: SRD): potions and oils, rings, rods,
staffs, wands, scrolls and books, jewelry, gems and stones. Each named item
gets its own colours and emblem from its SRD description, drawn by a few
parametric drawers (bottle, ring, rod, staff, wand, tome, amulet, gem).
Top-down, same pen style (red = colorable)."""

import math
from contextlib import contextmanager

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, dot, scallop, soft_shadow
from obj_craft import rot_pts
from obj_magic import GLASS, PARCH, crystal, roll
from obj_tavern import PAGES
from pen import DETAIL, FINE, INK, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint

GOLD = rgb("#e2b84e")
SILVER = rgb("#c7ccd4")
PLATINUM = rgb("#dfe2e4")
COPPER = rgb("#c27a4a")
BRONZE = rgb("#b08a4a")
BLACKEN = rgb("#3a3638")
BONE = rgb("#e6dcc4")
CORK = rgb("#b88a5a")
WAX_BLACK = rgb("#2c2a2e")
WHITE = (250, 250, 245)
O = DETAIL * 2.0  # outline weight for wands, staffs and rods (as the tools)

# Gem colours (none matches the colorable mask: red ones keep g != b).
RUBY = rgb("#c8384a")
GARNET = rgb("#9a2a3c")
SAPPHIRE = rgb("#3f6fc8")
EMERALD = rgb("#3fa868")
TOPAZ = rgb("#f0c24a")
AMETHYST = rgb("#9a5ad0")
JET = rgb("#2a2830")
PEARL = rgb("#ece6dc")
JADE = rgb("#6fbf8f")
AMBER = rgb("#d99a3a")


def L(pts, cx, cy, ang):
    """Local drawing coordinates (centred at 0, 0; long axis along x) to the
    image: rotated by `ang` and moved to (cx, cy)."""
    return rot_pts([(cx + x, cy + y) for x, y in pts], cx, cy, ang)


def flat(a, pts, color, outline=0, **kw):
    """A plain fill (no shading), for small marks inside a shape."""
    base = dict(outline=outline, corner=0, wob=0.1, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    base.update(kw)
    return a.shape(pts, color, **base)


def halo(a, x, y, r, color, alpha=0.4):
    """A soft glow kept well inside the image, so its blur never reaches
    the canvas edge (a cut halo shows as a tinted square)."""
    room = min(x, y, a.w - x, a.h - y)
    r = min(r, room * 0.5)
    p = skia.Path()
    p.addCircle(x, y, r)
    a.fill_path(p, color, alpha, blur=r * 0.16)


@contextmanager
def scaled(a, x, y, k):
    """Draw around (x, y) k times larger (staff heads, wand tips)."""
    a.c.save()
    a.c.translate(x, y)
    a.c.scale(k, k)
    a.c.translate(-x, -y)
    try:
        yield
    finally:
        a.c.restore()


def tight(fn, pad=4):
    """The drawing cropped to what's painted (plus `pad`): drawers work on
    roomy canvases; the asset keeps only its footprint."""

    def make():
        img = fn()
        box = img.getchannel("A").point(lambda v: 255 if v > 3 else 0).getbbox()
        if not box:
            return img
        x0, y0, x1, y1 = box
        return img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))

    return make


def sparkle(a, x, y, r, color=WHITE, alpha=0.95):
    a.ink([(x - r, y), (x + r, y)], FINE * 1.1, color=color, alpha=alpha, wob=0)
    a.ink([(x, y - r), (x, y + r)], FINE * 1.1, color=color, alpha=alpha, wob=0)


# -- potions and oils ------------------------------------------------------------------------------------
# A bottle lying on the floor, seen from above: its whole side shows, the
# liquid inside it, the neck and the stopper. Drawn in local coordinates
# (base at -x, neck toward +x) and rotated.

BOTTLES = {
    # shape: (body(inset) -> local points, neck (x0, x1, half width), stopper (x0, x1, half width))
    "round": (lambda i: ellipse(-8, 0, 30 - i, 30 - i, 48), (18, 36, 8), (36, 48, 7)),
    "vial": (lambda i: rect(-42 + i, -15 + i, 24 - i, 15 - i), (24, 30, 16), (30, 42, 11)),
    "square": (lambda i: rect(-34 + i, -24 + i, 14 - i, 24 - i), (14, 30, 8), (30, 42, 7)),
    "tear": (lambda i: chaikin([(-38 + i, 0), (-30 + i * 0.7, -22 + i), (-8, -26 + i), (12 - i, -12 + i * 0.6), (20 - i, 0), (12 - i, 12 - i * 0.6), (-8, 26 - i), (-30 + i * 0.7, 22 - i)], True, 2), (18, 34, 7), (34, 46, 6)),
    "flask": (lambda i: ellipse(-6, 0, 30 - i, 21 - i, 44), (22, 34, 7), (34, 44, 6)),
    "tube": (lambda i: rect(-46 + i, -10 + i, 30 - i, 10 - i), (30, 30, 10), (30, 44, 11)),
    "gourd": (lambda i: chaikin([(-40 + i, 0), (-34, -20 + i), (-16, -22 + i), (-6, -10 + i * 0.5), (8, -15 + i * 0.6), (20 - i, -8 + i * 0.4), (22 - i, 0), (20 - i, 8 - i * 0.4), (8, 15 - i * 0.6), (-6, 10 - i * 0.5), (-16, 22 - i), (-34, 20 - i)], True, 2), (20, 34, 7), (34, 46, 6)),
}


def bottle(
    seed,
    liquid,
    shape="round",
    ang=-0.35,
    liquid_alpha=1.0,
    extras=None,
    stopper=CORK,
    band=None,
    glass=GLASS,
    size=(170, 130),
    k=1.0,
):
    """A potion bottle lying on its side. `extras(art, R, k)` draws what
    floats in the liquid (clipped to it); R maps local points to the image."""
    w, h = size
    a = Art(w, h, seed)
    cx, cy = w / 2 - 8, h / 2 + 4
    body, (n0, n1, nh), (s0, s1, sh) = BOTTLES[shape]

    def R(pts):
        return L([(x * k, y * k) for x, y in pts], cx, cy, ang)

    soft_shadow(a, R(body(0)), dx=4, dy=5, alpha=0.3, blur=3)
    if n1 > n0:
        a.shape(R(rect(n0 - 2, -nh, n1, nh)), glass, outline=DETAIL * 1.3, corner=3, depth=2, light_k=0.6, mottle=0)
    a.shape(R(body(0)), glass, outline=DETAIL * 1.4, corner=6, depth=3, light_k=0.6, mottle=0)
    if liquid_alpha >= 0.99:
        path = a.shape(R(body(5)), liquid, outline=0, corner=6, depth=4, shade_k=0.35, light_k=0.3, ao=0.25, mottle=0.04)
    else:
        path = a.shape(R(body(5)), mix(glass, liquid, liquid_alpha), outline=0, corner=6, depth=3, shade_k=0.2, light_k=0.2, ao=0, mottle=0)
    if extras:
        with a.clip(path):
            extras(a, R, k)
    # Glint along the upper side of the glass.
    bx = [x for x, _ in body(0)]
    x0, x1 = min(bx), max(bx)
    top = min(y for _, y in body(0))
    a.ink(R([(x0 + (x1 - x0) * 0.22, top + 7), (x0 + (x1 - x0) * 0.62, top + 6)]), FINE * 1.8, color=WHITE, alpha=0.85)
    if band:
        a.shape(R(rect(n1 - 7, -nh - 2, n1, nh + 2)), band, outline=DETAIL, corner=2, depth=2, light_k=0.5, mottle=0)
    a.shape(R(rect(s0, -sh, s1, sh)), stopper, outline=DETAIL * 1.3, corner=4, depth=2, light_k=0.4, mottle=0)
    return a.image()


def potion(seed, liquid, shape="round", **kw):
    return lambda: bottle(seed, liquid, shape, **kw)


def specks(colors, n=10, r=(1.6, 3.0)):
    def draw(a, R, k):
        for i in range(n):
            x, y = a.rng.uniform(-34, 14), a.rng.uniform(-20, 20)
            dot(a, *R([(x, y)])[0], a.rng.uniform(*r), colors[i % len(colors)], 0.9)

    return draw


def bubbles(color=WHITE, n=8, r=(2.0, 4.5), alpha=0.8):
    def draw(a, R, k):
        for _ in range(n):
            x, y = a.rng.uniform(-34, 12), a.rng.uniform(-18, 18)
            a.ink(ellipse(*R([(x, y)])[0], *(a.rng.uniform(*r),) * 2, 14), FINE * 0.9, closed=True, color=color, alpha=alpha, wob=0)

    return draw


def glimmers(n=6):
    def draw(a, R, k):
        for _ in range(n):
            x, y = a.rng.uniform(-32, 10), a.rng.uniform(-16, 16)
            sparkle(a, *R([(x, y)])[0], a.rng.uniform(2.5, 4))

    return draw


def swirl(color, alpha=0.85, width=FINE * 1.6, turns=1.6):
    def draw(a, R, k):
        pts = []
        for i in range(40):
            t = i / 39
            r = 4 + 18 * t
            th = t * turns * 2 * math.pi
            pts.append((-10 + r * math.cos(th), r * 0.8 * math.sin(th)))
        a.ink(R(pts), width, color=color, alpha=alpha)

    return draw


def layers(colors):
    def draw(a, R, k):
        n = len(colors)
        for i, c in enumerate(colors):
            x0 = -50 + 80 * i / n
            flat(a, R(chaikin([(x0, -40), (x0 + 80 / n + 3, -40), (x0 + 80 / n + 6, 0), (x0 + 80 / n + 3, 40), (x0, 40), (x0 + 3, 0)], True, 1)), c)

    return draw


def eyeball(a, R, k):
    (x, y), = R([(-8, 0)])
    a.shape(ellipse(x, y, 10, 10, 24), WHITE, outline=FINE * 1.3, depth=1, light_k=0.3, mottle=0)
    a.shape(ellipse(x + 2, y - 1, 5, 5, 16), rgb("#4f8fd0"), outline=0, depth=1, mottle=0)
    dot(a, x + 2, y - 1, 2.2, INK)


def bead(color, r=5):
    def draw(a, R, k):
        (x, y), = R([(-8, 0)])
        halo(a, x, y, r * 3, color, 0.5)
        a.shape(ellipse(x, y, r, r, 16), color, outline=FINE * 1.1, depth=1, light_k=0.5, mottle=0)

    return draw


def cloud(color, n=3, r=9, alpha=0.8):
    def draw(a, R, k):
        for i in range(n):
            x, y = -26 + i * 14 + a.rng.uniform(-3, 3), a.rng.uniform(-8, 8)
            p = R(scallop(x, y, r, a.rng, 6, 0.25))
            a.fill_path(_path(p), color, alpha, blur=1.5)

    return draw


def _path(pts):
    from pen import to_path

    return to_path(pts)


def heart_pts(x, y, s):
    pts = []
    for i in range(32):
        t = 2 * math.pi * i / 32
        hx = 16 * math.sin(t) ** 3
        hy = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x + hx * s / 16, y + hy * s / 16))
    return pts


def heart(color, s=9, ring_=None):
    def draw(a, R, k):
        (x, y), = R([(-8, 0)])
        if ring_:
            a.ink(ellipse(x, y, s * 1.9, s * 1.9, 28), FINE * 1.4, closed=True, color=ring_, alpha=0.8)
        a.shape(heart_pts(x, y, s), color, outline=FINE * 1.2, corner=0, depth=1, light_k=0.4, mottle=0)

    return draw


def sliver(a, R, k):
    pts = [(-30, 2), (-12, -12), (8, -10), (-8, -4)]
    p = R(chaikin(pts, True, 2))
    (x, y), = R([(-8, -4)])
    halo(a, x, y, 40, rgb("#fff2b0"), 0.9)
    flat(a, p, rgb("#fffbe8"), outline=FINE * 0.8, outline_color=rgb("#d8c48a"))


def shards(a, R, k):
    for _ in range(9):
        x, y = a.rng.uniform(-34, 12), a.rng.uniform(-16, 16)
        t = a.rng.uniform(0, 3.14)
        a.ink(R([(x - 4 * math.cos(t), y - 4 * math.sin(t)), (x + 4 * math.cos(t), y + 4 * math.sin(t))]), FINE * 1.3, color=SILVER, alpha=0.95, wob=0)
        sparkle(a, *R([(x, y)])[0], 1.6)


def both(*fns):
    def draw(a, R, k):
        for f in fns:
            f(a, R, k)

    return draw


def jellyfish(a, R, k):
    (x, y), = R([(-6, 0)])
    a.shape(ellipse(x, y, 9, 9, 20), tint(rgb("#bfe6e0"), 0.3), outline=FINE, depth=1, light_k=0.5, mottle=0)
    for d in (-4, 0, 4):
        a.ink(R([(-14, d), (-24, d + 2), (-32, d - 1)]), FINE * 0.9, color=rgb("#e8fbf6"), alpha=0.85)


POTIONS_ = {
    "Potion of Animal Friendship": potion(3101, rgb("#7a6a42"), "gourd", extras=both(specks([rgb("#c7ccd4"), rgb("#5fb0d8"), rgb("#2c2a2e"), rgb("#b88a5a")], 9), lambda a, R, k: a.ink(R([(-20, 6), (-6, -4)]), FINE * 1.4, color=rgb("#4fb0a8")))),
    "Potion of Clairvoyance": potion(3102, rgb("#e2cc5a"), "round", extras=eyeball),
    "Potion of Climbing": potion(3103, rgb("#8a6a4a"), "vial", extras=layers([rgb("#8a6a4a"), rgb("#c7ccd4"), rgb("#8f8f92"), rgb("#8a6a4a"), rgb("#c7ccd4")])),
    "Potion of Diminution": potion(3104, rgb("#e6eef0"), "tear", liquid_alpha=0.35, extras=bead(rgb("#c8384a"), 4)),
    "Potion of Flying": potion(3105, rgb("#dfeef2"), "flask", liquid_alpha=0.45, extras=cloud(WHITE, 3, 8, 0.75)),
    "Potion of Gaseous Form": potion(3106, rgb("#b6bcc4"), "round", liquid_alpha=0.6, extras=both(cloud(rgb("#eef0f2"), 4, 9, 0.7), swirl(WHITE, 0.6))),
    "Potion of Giant Strength": potion(3107, rgb("#efe6c4"), "square", liquid_alpha=0.45, extras=sliver),
    "Potion of Growth": potion(3108, rgb("#e6eef0"), "vial", liquid_alpha=0.3, extras=lambda a, R, k: flat(a, R(scallop(-9, 0, 12, a.rng, 7, 0.3)), rgb("#c8384a"))),
    "Potion of Healing": potion(3109, rgb("#c8384a"), "round", extras=glimmers(5)),
    "Potion of Greater Healing": potion(3110, rgb("#c8344a"), "square", extras=glimmers(7), band=SILVER),
    "Potion of Superior Healing": potion(3111, rgb("#c23048"), "tear", extras=glimmers(9), band=GOLD, size=(150, 110), k=1.1),
    "Potion of Supreme Healing": potion(3112, rgb("#d03a52"), "gourd", extras=both(glimmers(11), bead(rgb("#ffd27a"), 3)), band=GOLD, stopper=GOLD, size=(160, 116), k=1.18),
    "Potion of Heroism": potion(3113, rgb("#4f8fd0"), "flask", extras=bubbles(rgb("#dff0ff"), 10)),
    "Potion of Invisibility": potion(3114, rgb("#dfeef2"), "vial", liquid_alpha=0.12),
    "Potion of Invulnerability": potion(3115, rgb("#7d8088"), "square", extras=swirl(rgb("#c7ccd4"), 0.9, FINE * 2.2, 1.2)),
    "Potion of Longevity": potion(3116, AMBER, "round", extras=heart(rgb("#a8303c"), 6)),
    "Potion of Mind Reading": potion(3117, rgb("#6a3a9a"), "tear", extras=lambda a, R, k: a.fill_path(_path(R(ellipse(-10, 0, 14, 9, 24))), rgb("#f2a0c8"), 0.85, blur=2)),
    "Potion of Poison": potion(3118, rgb("#c8384a"), "round", extras=both(glimmers(4), swirl(rgb("#4a6a3a"), 0.55)), stopper=WAX_BLACK),
    "Potion of Resistance": potion(3119, RED, "square", extras=swirl(tint(RED, 0.4), 0.9)),
    "Potion of Speed": potion(3120, rgb("#ecc63a"), "vial", extras=swirl(rgb("#2c2a2e"), 0.9, FINE * 1.8, 2.2)),
    "Potion of Vitality": potion(3121, rgb("#a8243a"), "round", extras=heart(rgb("#e85a6a"), 8, rgb("#f2a0a8"))),
    "Potion of Water Breathing": potion(3122, rgb("#6fae8a"), "flask", extras=jellyfish),
    "Elixir of Health": potion(3123, rgb("#d0485a"), "tear", liquid_alpha=0.75, extras=bubbles(rgb("#fff4cf"), 10, (1.6, 3.2), 0.95)),
    "Oil of Etherealness": potion(3124, rgb("#7f8894"), "vial", extras=lambda a, R, k: [a.shape(R(ellipse(x, y, 5, 5, 12)), rgb("#e4e8ee"), outline=FINE * 0.8, depth=1, light_k=0.5, mottle=0) for x, y in ((-30, -4), (-18, 5), (-6, -6), (6, 3), (-26, 7))]),
    "Oil of Sharpness": potion(3125, rgb("#e6eef0"), "round", liquid_alpha=0.4, extras=shards),
    "Oil of Slipperiness": potion(3126, rgb("#2a2830"), "gourd", extras=lambda a, R, k: a.ink(R([(-30, -8), (-10, -12), (8, -6)]), FINE * 1.6, color=rgb("#8f8f9a"), alpha=0.8)),
    "Philter of Love": potion(3127, rgb("#e88aa8"), "tear", extras=both(bubbles(WHITE, 7, (1.6, 3), 0.85), heart(rgb("#f8c8d8"), 6))),
    "Universal Solvent": potion(3128, rgb("#ece8dc"), "tube", stopper=IRON),
    "Sovereign Glue": potion(3129, rgb("#f2efe6"), "flask", extras=lambda a, R, k: a.ink(R([(-30, 6), (-14, 2), (0, 8), (10, 4)]), FINE * 1.6, color=rgb("#d8d4c8"), alpha=0.9), stopper=WAX_BLACK),
}


# -- rings -----------------------------------------------------------------------------------------------


def ring_item(seed, metal=GOLD, gems=(), band=10, setting=None, marks=None, s=96):
    """One ring lying flat: the band (a thick annulus) and its settings.
    `gems`: [(angle, radius, colour)]; `setting(art, x, y)` draws a custom
    face at the top; `marks(art, cx, cy, r)` engraves the band."""
    a = Art(s, s, seed)
    cx, cy = s / 2, s / 2 + 4
    r = s * 0.27
    outer, inner = ellipse(cx, cy, r + band / 2, r + band / 2, 56), ellipse(cx, cy, r - band / 2, r - band / 2, 56)
    ring_path = _path(outer)
    ring_path.addPath(_path(inner[::-1]))
    # The shadow is an annulus too: a filled disc would show through the
    # finger hole as a grey plug.
    shadow = skia.Path(ring_path)
    shadow.offset(3, 4)
    a.fill_path(shadow, INK, 0.32, blur=3)
    a.fill_path(ring_path, metal)
    with a.clip(ring_path):
        a.ink(ellipse(cx, cy, r + band / 2 - 2, r + band / 2 - 2, 56)[34:52], FINE * 1.6, color=tint(metal, 0.6), alpha=0.9, wob=0)
        a.ink(ellipse(cx, cy, r - band / 2 + 2, r - band / 2 + 2, 56)[6:22], FINE * 1.6, color=shade(metal, 0.35), alpha=0.8, wob=0)
        if marks:
            marks(a, cx, cy, r)
    a.ink(outer, DETAIL * 1.3, closed=True, wob=0.1)
    a.ink(inner, DETAIL * 1.1, closed=True, wob=0.1)
    if setting:
        setting(a, cx, cy - r)
    for ang, gr, col in gems:
        gx, gy = cx + r * math.cos(ang), cy + r * math.sin(ang)
        gem_at(a, gx, gy, gr, col, metal)
    return a.image()


def gem_at(a, x, y, r, color, metal=GOLD, cut="round"):
    """A set gem: its bezel, the stone with a facet star and a glint."""
    a.shape(ellipse(x, y, r + 3, r + 3, 24), metal, outline=FINE * 1.4, depth=1.5, light_k=0.5, mottle=0)
    if cut == "square":
        pts = rot_pts(rect(x - r, y - r, x + r, y + r), x, y, 0.785)
    else:
        pts = ellipse(x, y, r, r, 24)
    a.shape(pts, color, outline=FINE * 1.2, corner=1, depth=max(1, r * 0.3), shade_k=0.4, light_k=0.55, mottle=0)
    if r >= 5:
        for k in range(4):
            t = k * math.pi / 4
            a.ink([(x - r * 0.6 * math.cos(t), y - r * 0.6 * math.sin(t)), (x + r * 0.6 * math.cos(t), y + r * 0.6 * math.sin(t))], FINE * 0.6, color=shade(color, 0.45), alpha=0.5, wob=0)
    dot(a, x - r * 0.35, y - r * 0.35, max(1.2, r * 0.22), WHITE, 0.9)


def ring(seed, metal=GOLD, gem=None, r=8, **kw):
    gems = [(-math.pi / 2, r, gem)] if gem else []
    return lambda: ring_item(seed, metal, gems, **kw)


def _engrave_dots(color):
    def m(a, cx, cy, r):
        for k in range(14):
            t = 2 * math.pi * k / 14
            dot(a, cx + r * math.cos(t), cy + r * math.sin(t), 1.4, color, 0.9)

    return m


def _engrave_waves(color):
    def m(a, cx, cy, r):
        pts = [(cx + (r + 2.2 * math.sin(10 * t)) * math.cos(t), cy + (r + 2.2 * math.sin(10 * t)) * math.sin(t)) for t in [2 * math.pi * k / 120 for k in range(120)]]
        a.ink(pts, FINE * 0.9, closed=True, color=color, alpha=0.85, wob=0)

    return m


def _engrave_runes(color):
    def m(a, cx, cy, r):
        for k in range(8):
            t = 2 * math.pi * k / 8 + 0.2
            x, y = cx + r * math.cos(t), cy + r * math.sin(t)
            a.ink([(x - 2, y - 2), (x + 2, y), (x - 1, y + 2)], FINE * 0.8, color=color, alpha=0.9, wob=0)

    return m


def _feather_face(a, x, y):
    pts = chaikin([(x - 14, y + 2), (x - 4, y - 6), (x + 14, y - 4), (x + 4, y + 5)], True, 2)
    a.shape(pts, WHITE, outline=FINE * 1.3, depth=1, light_k=0.3, mottle=0)
    a.ink([(x - 14, y + 2), (x + 12, y - 3)], FINE, color=shade(BONE, 0.4))


def _ram_face(a, x, y):
    a.shape(ellipse(x, y, 9, 8, 20), BRONZE, outline=FINE * 1.3, depth=2, light_k=0.5, mottle=0)
    for s_ in (-1, 1):
        sp = [(x + s_ * (6 + 6 * math.cos(t)), y + 6 * math.sin(t)) for t in [k * 0.4 for k in range(12)]]
        a.ink(sp, DETAIL * 1.2, color=INK)
        a.ink(sp, DETAIL * 0.6, color=tint(BRONZE, 0.2))


def _signet(color, emblem=None):
    def face(a, x, y):
        a.shape(rect(x - 11, y - 9, x + 11, y + 9), color, outline=FINE * 1.4, corner=3, depth=2, light_k=0.5, mottle=0)
        if emblem:
            emblem(a, x, y)

    return face


def _star(a, x, y, r, color, n=5, inner=0.45, fill=True):
    pts = [(x + (r if i % 2 == 0 else r * inner) * math.cos(-math.pi / 2 + i * math.pi / n), y + (r if i % 2 == 0 else r * inner) * math.sin(-math.pi / 2 + i * math.pi / n)) for i in range(2 * n)]
    if fill:
        flat(a, pts, color, outline=FINE * 0.8)
    else:
        a.ink(pts, FINE, closed=True, color=color, wob=0)


RINGS = {
    "Ring of Animal Influence": ring(3201, BRONZE, setting=_signet(BRONZE, lambda a, x, y: [dot(a, x + dx, y + dy, rr, shade(BRONZE, 0.5)) for dx, dy, rr in ((0, 3, 3.6), (-5, -3, 1.8), (-2, -5, 1.8), (2, -5, 1.8), (5, -3, 1.8))])),
    "Ring of Djinni Summoning": ring(3202, GOLD, setting=lambda a, x, y: (gem_at(a, x, y, 8, rgb("#5fb0d8")), a.ink([(x - 4, y + 2), (x, y - 2), (x + 4, y + 1)], FINE, color=WHITE, alpha=0.8))),
    "Ring of Elemental Command": lambda: ring_item(3203, PLATINUM, [(-math.pi / 2, 6, rgb("#5fb0d8")), (-math.pi / 2 - 0.55, 5, rgb("#e0623a")), (-math.pi / 2 + 0.55, 5, EMERALD), (-math.pi / 2 + 1.1, 5, TOPAZ)]),
    "Ring of Evasion": ring(3204, SILVER, marks=_engrave_waves(shade(SILVER, 0.5)), gem=rgb("#6a6f80"), r=5),
    "Ring of Feather Falling": ring(3205, SILVER, setting=_feather_face),
    "Ring of Free Action": ring(3206, COPPER, marks=_engrave_waves(shade(COPPER, 0.5))),
    "Ring of Invisibility": ring(3207, PLATINUM, band=7, marks=_engrave_runes(rgb("#9fb6c4"))),
    "Ring of Jumping": ring(3208, GOLD, marks=_engrave_runes(shade(GOLD, 0.5)), gem=JADE, r=5),
    "Ring of Mind Shielding": ring(3209, SILVER, setting=lambda a, x, y: gem_at(a, x, y, 8, AMETHYST, SILVER, "square")),
    "Ring of Protection": ring(3210, SILVER, setting=_signet(SILVER, lambda a, x, y: flat(a, [(x - 6, y - 6), (x + 6, y - 6), (x + 6, y + 1), (x, y + 7), (x - 6, y + 1)], SAPPHIRE, outline=FINE * 0.8))),
    "Ring of Regeneration": ring(3211, GOLD, gem=EMERALD, r=8, marks=_engrave_dots(shade(GOLD, 0.45))),
    "Ring of Resistance": ring(3212, GOLD, gem=RED, r=8),
    "Ring of Shooting Stars": lambda: ring_item(3213, SILVER, [], marks=lambda a, cx, cy, r: [_star(a, cx + r * math.cos(t), cy + r * math.sin(t), 4.5, rgb("#fff0a8")) for t in [2 * math.pi * k / 6 for k in range(6)]], band=11),
    "Ring of Spell Storing": ring(3214, GOLD, gem=rgb("#7a7adc"), r=8, marks=_engrave_runes(shade(GOLD, 0.5))),
    "Ring of Spell Turning": ring(3215, SILVER, setting=lambda a, x, y: gem_at(a, x, y, 8, rgb("#bfe0f0"), SILVER), marks=_engrave_runes(rgb("#5f7a9a"))),
    "Ring of Swimming": ring(3216, SILVER, gem=rgb("#4fb0c0"), r=6, marks=_engrave_waves(rgb("#4f8fb0"))),
    "Ring of Telekinesis": ring(3217, GOLD, setting=lambda a, x, y: (gem_at(a, x, y, 8, rgb("#c6a8ec")), a.ink(ellipse(x, y, 13, 13, 24), FINE, closed=True, color=rgb("#a86ad0"), alpha=0.7))),
    "Ring of the Ram": ring(3218, BRONZE, setting=_ram_face),
    "Ring of Three Wishes": lambda: ring_item(3219, PLATINUM, [(-math.pi / 2 - 0.5, 5.5, rgb("#e6f0ff")), (-math.pi / 2, 6.5, rgb("#e6f0ff")), (-math.pi / 2 + 0.5, 5.5, rgb("#e6f0ff"))]),
    "Ring of Warmth": ring(3220, COPPER, gem=rgb("#e0623a"), r=7),
    "Ring of Water Walking": ring(3221, SILVER, gem=rgb("#7ac8e0"), r=6, marks=_engrave_waves(rgb("#5f9ab8"))),
    "Ring of X-ray Vision": ring(3222, GOLD, setting=lambda a, x, y: (gem_at(a, x, y, 8, rgb("#f2f4f8")), a.shape(ellipse(x, y, 5, 3, 16), rgb("#4f8fd0"), outline=FINE, depth=1, mottle=0), dot(a, x, y, 1.6, INK))),
}


# -- rods, staffs, wands -----------------------------------------------------------------------------------


def shaft(a, pts, w, color, ink_w=None):
    pts = chaikin(pts, False, 2) if len(pts) > 2 else pts
    a.ink(pts, w + (ink_w or 8), color=INK, taper=False, wob=0, var=0.06)
    a.ink(pts, w, color=color, taper=False, wob=0, var=0.06)
    a.ink(pts, max(1.2, w * 0.22), color=tint(color, 0.4), alpha=0.7, taper=False, wob=0, var=0.06)


def rings_on(a, p0, p1, ts, w, color):
    """Bands around a straight shaft at fractions `ts` of p0 -> p1."""
    ux, uy = p1[0] - p0[0], p1[1] - p0[1]
    Ln = math.hypot(ux, uy)
    ux, uy = ux / Ln, uy / Ln
    for t in ts:
        x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        a.shape(rot_pts(rect(x - 4, y - w, x + 4, y + w), x, y, math.atan2(uy, ux)), color, outline=FINE * 1.3, corner=2, depth=1, light_k=0.5, mottle=0)


# Rods: a metal scepter (~250 px), its head at the right.


def rod(seed, metal, head, grip=None, w=11, size=(280, 110)):
    W, H = size
    a = Art(W, H, seed)
    p0, p1 = (20, H * 0.62), (W - 58, H * 0.42)
    soft_shadow(a, [(p0[0], p0[1] - 6), (p1[0], p1[1] - 6), (p1[0], p1[1] + 6), (p0[0], p0[1] + 6)], dx=4, dy=5, alpha=0.3)
    shaft(a, [p0, p1], w, metal)
    a.shape(ellipse(p0[0], p0[1], w * 0.9, w * 0.9, 20), tint(metal, 0.05), outline=FINE * 1.5, depth=2, light_k=0.5, mottle=0)
    if grip:
        q = (p0[0] + (p1[0] - p0[0]) * 0.32, p0[1] + (p1[1] - p0[1]) * 0.32)
        shaft(a, [(p0[0] + 10, p0[1] - 0.8), q], w + 1, grip, 7)
        rings_on(a, p0, p1, (0.05, 0.34), w * 0.8, metal)
    head(a, p1[0], p1[1], math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return a.image()


def _flanged(metal, gem=None, eye=False):
    def head(a, x, y, ang):
        for k in range(6):
            t = ang + k * math.pi / 3
            fl = [(x + 12 * math.cos(t - 0.2), y + 12 * math.sin(t - 0.2)), (x + 28 * math.cos(t - 0.08), y + 28 * math.sin(t - 0.08)), (x + 28 * math.cos(t + 0.08), y + 28 * math.sin(t + 0.08)), (x + 12 * math.cos(t + 0.2), y + 12 * math.sin(t + 0.2))]
            a.shape(fl, metal, outline=FINE * 1.6, corner=1, depth=2, light_k=0.5, mottle=0)
        a.shape(ellipse(x, y, 15, 15, 28), metal, outline=DETAIL * 1.2, depth=3, light_k=0.55, mottle=0)
        if gem:
            gem_at(a, x, y, 6, gem, metal)
        if eye:
            a.shape(ellipse(x, y, 9, 6, 20), WHITE, outline=FINE * 1.2, depth=1, mottle=0)
            a.shape(ellipse(x, y, 4, 4, 16), rgb("#c8a83a"), outline=0, depth=1, mottle=0)
            dot(a, x, y, 1.8, INK)

    return head


def _lordly(a, x, y, ang):
    _flanged(IRON)(a, x, y, ang)
    # Its six buttons along the shaft.
    for k in range(3):
        bx, by = x - (40 + k * 16) * math.cos(ang), y - (40 + k * 16) * math.sin(ang)
        for s_ in (-1, 1):
            dot(a, bx - s_ * 9 * math.sin(ang), by + s_ * 9 * math.cos(ang), 3.4, INK)
            dot(a, bx - s_ * 9 * math.sin(ang), by + s_ * 9 * math.cos(ang), 2.2, rgb("#c8384a") if k == 0 else BRASS)


def _crown_head(a, x, y, ang):
    pts = []
    for i in range(10):
        t = ang + 2 * math.pi * i / 10
        r = 26 if i % 2 == 0 else 15
        pts.append((x + r * math.cos(t), y + r * math.sin(t)))
    a.shape(pts, GOLD, outline=DETAIL * 1.2, corner=2, depth=3, light_k=0.55, mottle=0)
    for i in range(0, 10, 2):
        t = ang + 2 * math.pi * i / 10
        dot(a, x + 24 * math.cos(t), y + 24 * math.sin(t), 3.2, RUBY)
    gem_at(a, x, y, 7, SAPPHIRE, GOLD)


def _vortex(a, x, y, ang):
    halo(a, x, y, 30, rgb("#8a5ad8"), 0.5)
    a.shape(ellipse(x, y, 19, 19, 32), JET, outline=DETAIL * 1.2, depth=3, light_k=0.3, mottle=0)
    sp = [(x + (1 + 15 * k / 39) * math.cos(k / 39 * 3.4 * math.pi), y + (1 + 15 * k / 39) * math.sin(k / 39 * 3.4 * math.pi)) for k in range(40)]
    a.ink(sp, FINE * 1.6, color=rgb("#b48aec"), alpha=0.95)


def _keyhead(a, x, y, ang):
    a.shape(ellipse(x, y, 20, 20, 32), SILVER, outline=DETAIL * 1.2, depth=3, light_k=0.55, mottle=0)
    a.ink(ellipse(x, y, 15, 15, 32), FINE, closed=True, color=shade(SILVER, 0.5), alpha=0.8)
    flat(a, ellipse(x, y - 3, 4, 4, 14), INK)
    flat(a, [(x - 2.5, y - 1), (x + 2.5, y - 1), (x + 4, y + 9), (x - 4, y + 9)], INK)


def _sun_head(a, x, y, ang):
    halo(a, x, y, 32, rgb("#ffe7a0"), 0.55)
    for k in range(12):
        t = ang + 2 * math.pi * k / 12
        a.shape([(x + 14 * math.cos(t - 0.18), y + 14 * math.sin(t - 0.18)), (x + 28 * math.cos(t), y + 28 * math.sin(t)), (x + 14 * math.cos(t + 0.18), y + 14 * math.sin(t + 0.18))], GOLD, outline=FINE * 1.3, corner=0, depth=1, light_k=0.5, mottle=0)
    a.shape(ellipse(x, y, 15, 15, 28), GOLD, outline=DETAIL * 1.2, depth=3, light_k=0.55, mottle=0)
    gem_at(a, x, y, 7, rgb("#fff4cf"), GOLD)


def immovable_rod(seed=3301):
    W, H = 250, 80
    a = Art(W, H, seed)
    p0, p1 = (24, 48), (220, 34)
    soft_shadow(a, [(p0[0], p0[1] - 6), (p1[0], p1[1] - 6), (p1[0], p1[1] + 6), (p0[0], p0[1] + 6)], dx=4, dy=5, alpha=0.3)
    shaft(a, [p0, p1], 13, IRON)
    for p in (p0, p1):
        a.shape(ellipse(p[0], p[1], 10, 10, 20), shade(IRON, 0.1), outline=FINE * 1.5, depth=2, light_k=0.4, mottle=0)
    a.shape(ellipse(p1[0], p1[1], 5, 5, 14), rgb("#b84a3a"), outline=FINE * 1.2, depth=1, light_k=0.6, mottle=0)
    return a.image()


RODS = {
    "Immovable Rod": immovable_rod,
    "Rod of Absorption": lambda: rod(3302, BLACKEN, _vortex, grip=rgb("#5a3a6a")),
    "Rod of Alertness": lambda: rod(3303, SILVER, _flanged(SILVER, eye=True), grip=rgb("#3c5a78")),
    "Rod of Lordly Might": lambda: rod(3304, IRON, _lordly, grip=rgb("#5a3a22"), w=13),
    "Rod of Resurrection": lambda: rod(3305, GOLD, _sun_head, grip=WHITE),
    "Rod of Rulership": lambda: rod(3306, GOLD, _crown_head, grip=rgb("#6a2a3a")),
    "Rod of Security": lambda: rod(3307, SILVER, _keyhead, grip=rgb("#3a4a5a")),
}


# Staffs: ~360 px, a pole with its head at the right.


def staff_item(seed, pole, head, wood=WOOD, w=12, size=(440, 160), bands=(), band_color=BRASS, path=None, head_k=1.45):
    W, H = size
    a = Art(W, H, seed)
    pts = path or [(20, H * 0.66), (W * 0.48, H * 0.56), (W - 100, H * 0.45)]
    soft_shadow(a, [(x, y - 7) for x, y in pts] + [(x, y + 7) for x, y in pts[::-1]], dx=5, dy=6, alpha=0.3)
    pole(a, pts, w, wood)
    if bands:
        rings_on(a, pts[0], pts[-1], bands, w * 0.75, band_color)
    hx, hy = pts[-1]
    with scaled(a, hx, hy, head_k):
        head(a, hx, hy, math.atan2(hy - pts[-2][1], hx - pts[-2][0]))
    return a.image()


def plain_pole(a, pts, w, wood):
    shaft(a, pts, w, wood)


def gnarled_pole(a, pts, w, wood):
    pts = chaikin(pts, False, 2)
    out = []
    for i in range(0, 41):
        t = i / 40
        j = min(len(pts) - 2, int(t * (len(pts) - 1)))
        f = t * (len(pts) - 1) - j
        x = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f
        y = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f + 4 * math.sin(t * 19)
        out.append((x, y))
    shaft(a, out, w, wood)
    for t in (0.25, 0.55, 0.8):
        x, y = out[int(t * 40)]
        dot(a, x, y, w * 0.32, shade(wood, 0.45), 0.9)


def _orb_head(color, metal=GOLD, prongs=4, r=17, glow_a=0.5):
    def head(a, x, y, ang):
        ox, oy = x + 14 * math.cos(ang), y + 14 * math.sin(ang)
        halo(a, ox, oy, r * 2.2, color, glow_a)
        for k in range(prongs):
            t = ang + math.pi + (k - (prongs - 1) / 2) * 0.55
            a.ink([(x, y), (ox + (r + 4) * math.cos(t + math.pi), oy + (r + 4) * math.sin(t + math.pi))], 9, color=INK)
            a.ink([(x, y), (ox + (r + 4) * math.cos(t + math.pi), oy + (r + 4) * math.sin(t + math.pi))], 4.5, color=metal)
        a.shape(ellipse(ox, oy, r, r, 32), color, outline=DETAIL * 1.2, depth=4, light_k=0.65, mottle=0.03)
        a.ink([(ox - r * 0.5, oy - r * 0.15), (ox - r * 0.15, oy - r * 0.55)], FINE * 1.8, color=WHITE, alpha=0.9)

    return head


def _crook_head(gem):
    def head(a, x, y, ang):
        pts = [(x, y), (x + 22 * math.cos(ang), y + 22 * math.sin(ang))]
        cx, cy = pts[-1][0] - 18 * math.sin(ang), pts[-1][1] + 18 * math.cos(ang)
        arc = [(cx + 18 * math.cos(ang - math.pi / 2 + t), cy + 18 * math.sin(ang - math.pi / 2 + t)) for t in [k * 0.25 for k in range(15)]]
        shaft(a, pts + arc, 11, WOOD_LIGHT)
        gem_at(a, pts[-1][0], pts[-1][1], 7, gem, GOLD)

    return head


def _flame_head(a, x, y, ang):
    halo(a, x + 16 * math.cos(ang), y + 16 * math.sin(ang), 34, rgb("#ffb050"), 0.55)
    for r, col in ((24, rgb("#d8462a")), (16, rgb("#f08a3a")), (8, rgb("#ffe08a"))):
        fx, fy = x + (30 - r * 0.6) * math.cos(ang), y + (30 - r * 0.6) * math.sin(ang)
        a.shape(scallop(fx, fy, r, a.rng, 7, 0.3), col, outline=DETAIL if r > 20 else 0, depth=2, shade_k=0.2, light_k=0.2, ao=0, mottle=0)
    a.shape(ellipse(x, y, 11, 11, 20), BLACKEN, outline=FINE * 1.5, depth=2, light_k=0.4, mottle=0)


def _frost_head(a, x, y, ang):
    halo(a, x + 14 * math.cos(ang), y + 14 * math.sin(ang), 34, rgb("#bfe6ff"), 0.55)
    for k, (dl, r) in enumerate(((0.0, 18), (-0.7, 13), (0.7, 13), (-1.5, 10), (1.5, 10))):
        t = ang + dl
        crystal(a, x + (14 + r * 0.4) * math.cos(t), y + (14 + r * 0.4) * math.sin(t), r, rgb("#a8d8f0"), t)


def _healing_head(a, x, y, ang):
    halo(a, x + 12 * math.cos(ang), y + 12 * math.sin(ang), 30, rgb("#fff4cf"), 0.5)
    from obj_nature import leaf

    for t in (-0.9, -0.3, 0.3, 0.9):
        lx, ly = x + 22 * math.cos(ang + t), y + 22 * math.sin(ang + t)
        leaf(a, lx, ly, 22, rgb("#7bb05a"), ang + t)
    a.shape(ellipse(x + 8 * math.cos(ang), y + 8 * math.sin(ang), 11, 11, 24), PEARL, outline=DETAIL, depth=2, light_k=0.5, mottle=0)
    a.ink([(x + 8 * math.cos(ang) - 6, y + 8 * math.sin(ang)), (x + 8 * math.cos(ang) + 6, y + 8 * math.sin(ang))], FINE * 1.8, color=rgb("#c84a3a"))
    a.ink([(x + 8 * math.cos(ang), y + 8 * math.sin(ang) - 6), (x + 8 * math.cos(ang), y + 8 * math.sin(ang) + 6)], FINE * 1.8, color=rgb("#c84a3a"))


def _hive_head(a, x, y, ang):
    hx, hy = x + 16 * math.cos(ang), y + 16 * math.sin(ang)
    a.shape(ellipse(hx, hy, 20, 16, 32, rot=ang), rgb("#d9b25a"), outline=DETAIL * 1.2, depth=3, light_k=0.4, mottle=0, detail=lambda art, p: [art.ink(ellipse(hx, hy, 20 - k * 6, 16 - k * 5, 32, rot=ang), FINE, closed=True, color=shade(rgb("#d9b25a"), 0.5), alpha=0.8) for k in (1, 2)])
    for _ in range(6):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(26, 38)
        bx, by = hx + d * math.cos(t), hy + d * math.sin(t)
        if 4 < bx < a.w - 4 and 4 < by < a.h - 4:
            dot(a, bx, by, 3.2, INK)
            dot(a, bx - 1, by - 2, 1.8, WHITE, 0.8)


def _magi_head(a, x, y, ang):
    halo(a, x + 16 * math.cos(ang), y + 16 * math.sin(ang), 40, rgb("#b48aec"), 0.45)
    for k, col in enumerate((RUBY, SAPPHIRE, EMERALD, TOPAZ, AMETHYST)):
        t = ang + (k - 2) * 0.62
        gx, gy = x + 24 * math.cos(t), y + 24 * math.sin(t)
        a.ink([(x, y), (gx, gy)], 8, color=INK)
        a.ink([(x, y), (gx, gy)], 4, color=SILVER)
        gem_at(a, gx, gy, 5, col, SILVER)
    gem_at(a, x + 4 * math.cos(ang), y + 4 * math.sin(ang), 9, rgb("#e6f0ff"), SILVER)


def _python_pole(a, pts, w, wood):
    snake = rgb("#5f8a3a")
    pts = chaikin(pts, False, 2)
    out = []
    for i in range(0, 61):
        t = i / 60
        j = min(len(pts) - 2, int(t * (len(pts) - 1)))
        f = t * (len(pts) - 1) - j
        x = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f
        y = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f + 7 * math.sin(t * 22) * (0.3 + 0.7 * t)
        out.append((x, y))
    a.ink(out, w + 9, color=INK, taper=True, wob=0, var=0.05)
    a.ink(out, w + 1, color=snake, taper=True, wob=0, var=0.05)
    for i in range(3, 58, 4):
        dot(a, out[i][0], out[i][1], 2.6, shade(snake, 0.45), 0.9)
    a.ink(out, 2.5, color=tint(snake, 0.4), alpha=0.6, taper=True, wob=0)


def _snake_head(a, x, y, ang):
    snake = rgb("#5f8a3a")
    hx, hy = x + 12 * math.cos(ang), y + 12 * math.sin(ang)
    pts = rot_pts([(hx - 14, hy - 11), (hx + 8, hy - 10), (hx + 20, hy), (hx + 8, hy + 10), (hx - 14, hy + 11)], hx, hy, ang)
    a.shape(chaikin(pts, True, 2), snake, outline=DETAIL * 1.3, depth=3, light_k=0.4, mottle=0)
    for s_ in (-1, 1):
        ex, ey = rot_pts([(hx + 6, hy + s_ * 6)], hx, hy, ang)[0]
        dot(a, ex, ey, 2.8, rgb("#f2d24a"))
        dot(a, ex, ey, 1.2, INK)
    tx, ty = rot_pts([(hx + 20, hy)], hx, hy, ang)[0]
    a.ink([(tx, ty), (tx + 10 * math.cos(ang + 0.3), ty + 10 * math.sin(ang + 0.3))], FINE * 1.3, color=rgb("#c84a3a"))
    a.ink([(tx, ty), (tx + 10 * math.cos(ang - 0.3), ty + 10 * math.sin(ang - 0.3))], FINE * 1.3, color=rgb("#c84a3a"))


def _woodlands_head(a, x, y, ang):
    from obj_nature import leaf

    for t in (-1.0, -0.4, 0.2, 0.8, 1.3):
        lx, ly = x + 18 * math.cos(ang + t), y + 18 * math.sin(ang + t)
        leaf(a, lx, ly, 24, rgb("#6b9a45"), ang + t)
    a.shape(ellipse(x, y, 10, 10, 20), WOOD, outline=FINE * 1.5, depth=2, light_k=0.4, mottle=0)


def _bolt_head(a, x, y, ang):
    halo(a, x + 16 * math.cos(ang), y + 16 * math.sin(ang), 36, rgb("#bfe0ff"), 0.5)
    for s_ in (-1, 1):
        pts = [(0, 0), (12, s_ * 4), (8, s_ * 10), (24, s_ * 16), (20, s_ * 22), (36, s_ * 30)]
        world = rot_pts([(x + px, y + py) for px, py in pts], x, y, ang)
        a.ink(world, 9, color=INK, taper=True)
        a.ink(world, 4.5, color=rgb("#f2e070"), taper=True)
    a.shape(ellipse(x, y, 12, 12, 24), rgb("#5f7a9a"), outline=DETAIL, depth=2, light_k=0.5, mottle=0)


def _skull_head(a, x, y, ang):
    from obj_magic import skull_at

    halo(a, x + 12 * math.cos(ang), y + 12 * math.sin(ang), 30, rgb("#8ad07a"), 0.35)
    skull_at(a, x + 12 * math.cos(ang), y + 12 * math.sin(ang), 0.62)


def _striking_head(a, x, y, ang):
    a.shape(rot_pts(rect(x - 12, y - 11, x + 12, y + 11), x, y, ang), IRON, outline=DETAIL * 1.2, corner=4, depth=3, light_k=0.5, mottle=0)
    dot(a, x, y, 3, shade(IRON, 0.5))


STAFFS = {
    "Staff of Charming": lambda: staff_item(3401, plain_pole, _crook_head(rgb("#e88aa8")), WOOD_LIGHT, bands=(0.6,), band_color=GOLD),
    "Staff of Fire": lambda: staff_item(3402, plain_pole, _flame_head, rgb("#5a2a22"), bands=(0.35, 0.7), band_color=BRASS),
    "Staff of Frost": lambda: staff_item(3403, plain_pole, _frost_head, rgb("#b6c8d4"), bands=(0.5,), band_color=SILVER),
    "Staff of Healing": lambda: staff_item(3404, plain_pole, _healing_head, rgb("#e2d4b4"), bands=(0.45,), band_color=GOLD),
    "Staff of Power": lambda: staff_item(3405, plain_pole, _orb_head(rgb("#6fb0f0"), SILVER, 4, 18, 0.55), rgb("#6a6f80"), bands=(0.2, 0.45, 0.7), band_color=SILVER),
    "Staff of Striking": lambda: staff_item(3406, plain_pole, _striking_head, WOOD, bands=(0.03, 0.5), band_color=IRON),
    "Staff of Swarming Insects": lambda: staff_item(3407, gnarled_pole, _hive_head, WOOD_DARK),
    "Staff of the Magi": lambda: staff_item(3408, plain_pole, _magi_head, rgb("#3c4a6a"), bands=(0.15, 0.3, 0.45, 0.6, 0.75), band_color=SILVER, size=(420, 140)),
    "Staff of the Python": lambda: staff_item(3409, _python_pole, _snake_head, w=12),
    "Staff of the Woodlands": lambda: staff_item(3410, gnarled_pole, _woodlands_head, WOOD),
    "Staff of Thunder and Lightning": lambda: staff_item(3411, plain_pole, _bolt_head, rgb("#4a5a6a"), bands=(0.3, 0.6), band_color=BRASS),
    "Staff of Withering": lambda: staff_item(3412, gnarled_pole, _skull_head, rgb("#3a3228")),
}


# Wands: ~190 px, the tip at the right.


def wand_item(seed, body, tip, grip=None, w=8, bands=(), band_color=GOLD, size=(240, 110), twist=None, tip_k=1.25):
    W, H = size
    a = Art(W, H, seed)
    p0, p1 = (18, H * 0.6), (W - 56, H * 0.42)
    soft_shadow(a, [(p0[0], p0[1] - 4), (p1[0], p1[1] - 4), (p1[0], p1[1] + 4), (p0[0], p0[1] + 4)], dx=3, dy=4, alpha=0.3)
    shaft(a, [p0, p1], w, body, 6)
    if twist:
        ux, uy = p1[0] - p0[0], p1[1] - p0[1]
        Ln = math.hypot(ux, uy)
        nx, ny = -uy / Ln, ux / Ln
        pts = [(p0[0] + ux * t + nx * (w * 0.4) * math.sin(t * 50), p0[1] + uy * t + ny * (w * 0.4) * math.sin(t * 50)) for t in [k / 80 for k in range(81)]]
        a.ink(pts, FINE * 1.3, color=twist, alpha=0.9, wob=0)
    if grip:
        q = (p0[0] + (p1[0] - p0[0]) * 0.28, p0[1] + (p1[1] - p0[1]) * 0.28)
        shaft(a, [p0, q], w + 1, grip, 6)
    if bands:
        rings_on(a, p0, p1, bands, w * 0.75, band_color)
    with scaled(a, p1[0], p1[1], tip_k):
        tip(a, p1[0], p1[1], math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return a.image()


def _gem_tip(color, r=8, glow_a=0.5, metal=GOLD):
    def tip(a, x, y, ang):
        halo(a, x, y, r * 2.6, color, glow_a)
        crystal(a, x + 3 * math.cos(ang), y + 3 * math.sin(ang), r, color, ang)

    return tip


def _orb_tip(color, r=8, glow_a=0.5):
    def tip(a, x, y, ang):
        halo(a, x, y, r * 2.6, color, glow_a)
        a.shape(ellipse(x + 3 * math.cos(ang), y + 3 * math.sin(ang), r, r, 24), color, outline=DETAIL, depth=2, light_k=0.65, mottle=0)
        dot(a, x - r * 0.3, y - r * 0.4, r * 0.22, WHITE, 0.9)

    return tip


def _eye_tip(a, x, y, ang):
    halo(a, x, y, 20, rgb("#e0623a"), 0.45)
    a.shape(ellipse(x + 3, y, 10, 7, 24, rot=ang), WHITE, outline=DETAIL, depth=1, mottle=0)
    a.shape(ellipse(x + 3, y, 4.5, 4.5, 16), rgb("#c84a3a"), outline=0, depth=1, mottle=0)
    dot(a, x + 3, y, 2, INK)


def _skull_tip(a, x, y, ang):
    from obj_magic import skull_at

    halo(a, x, y, 22, rgb("#8ad07a"), 0.35)
    skull_at(a, x + 4, y, 0.42)


def _fire_tip(a, x, y, ang):
    halo(a, x, y, 22, rgb("#ffb050"), 0.6)
    for r, col in ((11, rgb("#d8462a")), (7, rgb("#f08a3a")), (3.5, rgb("#ffe08a"))):
        a.shape(scallop(x + 3, y, r, a.rng, 6, 0.3), col, outline=FINE * 1.2 if r > 10 else 0, depth=1, shade_k=0.2, light_k=0, ao=0, mottle=0)


def _bolt_tip(a, x, y, ang):
    halo(a, x, y, 22, rgb("#bfe0ff"), 0.55)
    pts = rot_pts([(x - 2, y), (x + 8, y - 6), (x + 6, y), (x + 18, y - 8), (x + 12, y + 2), (x + 14, y - 2)], x, y, ang)
    a.ink(pts, 7, color=INK, taper=True)
    a.ink(pts, 3.5, color=rgb("#f2e070"), taper=True)


def _star_tip(color, r=10):
    def tip(a, x, y, ang):
        halo(a, x, y, r * 2.4, color, 0.55)
        _star(a, x + 3, y, r, color)

    return tip


def _keyhole_tip(a, x, y, ang):
    a.shape(ellipse(x + 2, y, 8, 8, 20), SILVER, outline=DETAIL, depth=2, light_k=0.55, mottle=0)
    flat(a, ellipse(x + 2, y - 1.5, 2.2, 2.2, 12), INK)
    flat(a, [(x + 0.8, y), (x + 3.2, y), (x + 4, y + 5), (x, y + 5)], INK)


def _web_tip(a, x, y, ang):
    for k in range(6):
        t = k * math.pi / 3
        a.ink([(x + 3, y), (x + 3 + 14 * math.cos(t), y + 14 * math.sin(t))], FINE * 0.9, color=WHITE, alpha=0.9, wob=0)
    for r in (6, 11):
        a.ink([(x + 3 + r * math.cos(k * math.pi / 3), y + r * math.sin(k * math.pi / 3)) for k in range(6)], FINE * 0.8, closed=True, color=WHITE, alpha=0.9, wob=0)
    a.shape(ellipse(x + 3, y, 4, 4, 14), JET, outline=FINE, depth=1, mottle=0)


def _chain_tip(a, x, y, ang):
    for k in range(3):
        cx, cy = x - 6 + k * 7 * math.cos(ang), y + k * 7 * math.sin(ang)
        a.ink(ellipse(cx, cy, 5, 3.4, 16, rot=ang + (k % 2) * 1.57), DETAIL * 1.4, closed=True, color=INK, wob=0)
        a.ink(ellipse(cx, cy, 5, 3.4, 16, rot=ang + (k % 2) * 1.57), DETAIL * 0.7, closed=True, color=SILVER, wob=0)


def _wonder_tip(a, x, y, ang):
    halo(a, x, y, 22, rgb("#fff0a8"), 0.5)
    for k, col in enumerate((rgb("#e0623a"), TOPAZ, EMERALD, SAPPHIRE, AMETHYST)):
        t = 2 * math.pi * k / 5
        dot(a, x + 3 + 8 * math.cos(t), y + 8 * math.sin(t), 3.4, INK)
        dot(a, x + 3 + 8 * math.cos(t), y + 8 * math.sin(t), 2.4, col)
    _star(a, x + 3, y, 6, rgb("#fff4cf"))


WANDS = {
    "Wand of Binding": lambda: wand_item(3501, IRON, _chain_tip, grip=rgb("#3a2a22"), bands=(0.5,), band_color=SILVER),
    "Wand of Enemy Detection": lambda: wand_item(3502, WOOD_DARK, _eye_tip, bands=(0.32,), band_color=BRASS),
    "Wand of Fear": lambda: wand_item(3503, BONE, _skull_tip),
    "Wand of Fireballs": lambda: wand_item(3504, rgb("#7a2a22"), _fire_tip, grip=BLACKEN, bands=(0.6,), band_color=GOLD),
    "Wand of Lightning Bolts": lambda: wand_item(3505, rgb("#4a5a7a"), _bolt_tip, bands=(0.3, 0.6), band_color=BRASS),
    "Wand of Magic Detection": lambda: wand_item(3506, WOOD_LIGHT, _gem_tip(rgb("#4fc2c0")), bands=(0.3,), band_color=SILVER),
    "Wand of Magic Missiles": lambda: wand_item(3507, rgb("#4a3a6a"), _star_tip(rgb("#c6a8ec"), 9), bands=(0.3,), band_color=SILVER),
    "Wand of Paralysis": lambda: wand_item(3508, rgb("#5a6a5a"), _orb_tip(rgb("#9ad0f0")), twist=rgb("#bfe6ff")),
    "Wand of Polymorph": lambda: wand_item(3509, rgb("#5a8a4a"), _gem_tip(rgb("#e88aa8")), twist=rgb("#ecc63a")),
    "Wand of Secrets": lambda: wand_item(3510, BLACKEN, _keyhole_tip, bands=(0.3,), band_color=SILVER),
    "Wand of the War Mage": lambda: wand_item(3511, IRON, _gem_tip(rgb("#e0623a"), 7, 0.45), grip=rgb("#5a3a22"), bands=(0.36, 0.5, 0.64), band_color=BRASS),
    "Wand of Web": lambda: wand_item(3512, rgb("#3a3230"), _web_tip),
    "Wand of Wonder": lambda: wand_item(3513, rgb("#6a4a8a"), _wonder_tip, twist=rgb("#f2d24a"), bands=(0.25,), band_color=GOLD),
}


# -- scrolls and books -----------------------------------------------------------------------------------


def spell_scroll(seed=3601, seal=RED):
    """An open spell scroll: lines of text around an arcane sigil, its wax
    seal (colorable) dangling on a ribbon."""
    w, h = 270, 170
    a = Art(w, h, seed)
    from obj_magic import scroll as draw_scroll

    draw_scroll(a, 130, 82, 180, 0.0, open_=True)
    cx, cy = 130, 82
    a.ink(ellipse(cx, cy, 17, 17, 36), FINE * 1.4, closed=True, color=rgb("#6a4ac0"), alpha=0.9)
    _star(a, cx, cy, 14, rgb("#6a4ac0"), 5, 0.38, fill=False)
    # Ribbon and seal hanging off the lower edge.
    a.ink([(cx + 40, 120), (cx + 50, 140), (cx + 44, 150)], DETAIL * 1.4, color=INK)
    a.ink([(cx + 40, 120), (cx + 50, 140), (cx + 44, 150)], DETAIL * 0.7, color=seal)
    a.shape(scallop(cx + 46, 150, 11, a.rng, 8, 0.15), seal, outline=DETAIL, depth=2, light_k=0.4, mottle=0)
    _star(a, cx + 46, 150, 5, tint(seal, 0.4), 5, 0.4, fill=False)
    return a.image()


def spell_scroll_rolled(seed=3602, seal=RED):
    w, h = 200, 90
    a = Art(w, h, seed)
    roll(a, 100, 44, 150, 14, 0.08, PARCH, spiral_at=1)
    a.ink([(100, 30), (98, 58)], DETAIL * 1.6, color=INK)
    a.ink([(100, 30), (98, 58)], DETAIL * 0.8, color=seal)
    a.shape(scallop(99, 46, 11, a.rng, 8, 0.15), seal, outline=DETAIL, depth=2, light_k=0.4, mottle=0)
    _star(a, 99, 46, 5, tint(seal, 0.4), 5, 0.4, fill=False)
    return a.image()


def tome(seed, cover, emblem, metal=GOLD, w=104, h=138, corners=True, clasp=True):
    """A thick closed book lying flat: page block, cover, corner guards, a
    clasp, and its emblem tooled in the middle."""
    W, H = w + 46, h + 40
    a = Art(W, H, seed)
    x0, y0 = 20, 18
    ang = -0.12
    cx, cy = x0 + w / 2, y0 + h / 2
    R = lambda pts: rot_pts(pts, cx, cy, ang)  # noqa: E731
    soft_shadow(a, R(rect(x0, y0, x0 + w, y0 + h)), dx=5, dy=6, alpha=0.35)
    a.shape(R(rect(x0 + 6, y0 + 4, x0 + w + 4, y0 + h - 4)), PAGES, outline=DETAIL, corner=2, depth=1, mottle=0, detail=lambda art, p: [art.ink(R([(x0 + w - 2 + d, y0 + 8), (x0 + w - 2 + d, y0 + h - 8)]), FINE * 0.7, color=shade(PAGES, 0.4), alpha=0.6) for d in (-2, 1)])
    a.shape(R(rect(x0, y0, x0 + w - 4, y0 + h)), cover, outline=DETAIL * 1.4, corner=4, depth=5, light_k=0.35, mottle=0.05)
    a.ink(R([(x0 + 12, y0 + 5), (x0 + 12, y0 + h - 5)]), FINE * 1.4, color=shade(cover, 0.45), alpha=0.85)
    a.ink(R(rect(x0 + 20, y0 + 12, x0 + w - 14, y0 + h - 12)), FINE * 1.1, closed=True, color=metal, alpha=0.75)
    if corners:
        for px, py, sx, sy in ((x0 + w - 4, y0, -1, 1), (x0 + w - 4, y0 + h, -1, -1)):
            a.shape(R([(px, py), (px + sx * 18, py), (px, py + sy * 18)]), metal, outline=FINE * 1.3, corner=1, depth=1, light_k=0.5, mottle=0)
    if clasp:
        a.shape(R(rect(x0 + w - 14, cy - 7, x0 + w + 8, cy + 7)), metal, outline=FINE * 1.4, corner=2, depth=2, light_k=0.5, mottle=0)
    ex, ey = R([(cx + 4, cy)])[0]
    emblem(a, ex, ey, metal)
    return a.image()


def _em_heart(a, x, y, m):
    a.shape(heart_pts(x, y, 15), rgb("#b8343c"), outline=FINE * 1.4, corner=0, depth=2, light_k=0.4, mottle=0)


def _em_fist(a, x, y, m):
    # A dumbbell: the "gainful exercise".
    a.ink([(x - 16, y), (x + 16, y)], 9, color=INK, taper=False)
    a.ink([(x - 16, y), (x + 16, y)], 4, color=m, taper=False)
    for s_ in (-1, 1):
        a.shape(rect(x + s_ * 18 - 5, y - 12, x + s_ * 18 + 5, y + 12), IRON, outline=FINE * 1.3, corner=2, depth=2, light_k=0.5, mottle=0)


def _em_golem(a, x, y, m):
    a.shape(rect(x - 14, y - 16, x + 14, y + 16), STONE, outline=FINE * 1.5, corner=3, depth=2, light_k=0.4, mottle=0)
    for dx in (-6, 6):
        flat(a, rect(x + dx - 3, y - 6, x + dx + 3, y - 2), rgb("#f2c24a"))
    a.ink([(x - 6, y + 7), (x + 6, y + 7)], FINE * 1.3)
    a.ink([(x - 3, y - 16), (x + 1, y - 9), (x - 1, y - 4)], FINE, color=shade(STONE, 0.5))


def _em_wing(a, x, y, m):
    for k in range(4):
        a.ink([(x - 12, y + 8), (x + 2 + k * 4, y - 14 + k * 6)], DETAIL * 0.9, color=m)
    a.ink([(x - 16, y + 10), (x + 16, y - 2)], FINE * 1.4, color=m)


def _em_eye(a, x, y, m):
    a.ink([(x - 18, y), (x - 6, y - 9), (x + 6, y - 9), (x + 18, y), (x + 6, y + 9), (x - 6, y + 9)], FINE * 1.6, closed=True, color=m)
    flat(a, ellipse(x, y, 6, 6, 16), rgb("#4f8fd0"), outline=FINE)
    dot(a, x, y, 2.4, INK)


def _em_crown(a, x, y, m):
    pts = [(x - 16, y + 10), (x - 16, y - 6), (x - 8, y + 2), (x, y - 12), (x + 8, y + 2), (x + 16, y - 6), (x + 16, y + 10)]
    a.shape(pts, m, outline=FINE * 1.4, corner=1, depth=2, light_k=0.5, mottle=0)
    for dx in (-8, 0, 8):
        dot(a, x + dx, y + 5, 2.2, RUBY)


def _em_owl(a, x, y, m):
    a.ink(ellipse(x, y, 16, 16, 32), FINE * 1.4, closed=True, color=m)
    for dx in (-6, 6):
        a.ink(ellipse(x + dx, y - 2, 4.5, 4.5, 16), FINE * 1.3, closed=True, color=m)
        dot(a, x + dx, y - 2, 1.6, m)
    a.ink([(x - 2, y + 4), (x, y + 8), (x + 2, y + 4)], FINE * 1.2, color=m)


BOOKS = {
    "Spell Scroll": spell_scroll,
    "Spell Scroll (Rolled)": spell_scroll_rolled,
    "Manual of Bodily Health": lambda: tome(3611, rgb("#7a3a2e"), _em_heart, BRASS),
    "Manual of Gainful Exercise": lambda: tome(3612, rgb("#8a5a2e"), _em_fist, BRASS),
    "Manual of Golems": lambda: tome(3613, rgb("#4a4a52"), _em_golem, IRON, w=112, h=146),
    "Manual of Quickness of Action": lambda: tome(3614, rgb("#2f6461"), _em_wing, SILVER),
    "Tome of Clear Thought": lambda: tome(3615, rgb("#3c5a78"), _em_eye, SILVER),
    "Tome of Leadership and Influence": lambda: tome(3616, rgb("#6a2a3a"), _em_crown, GOLD),
    "Tome of Understanding": lambda: tome(3617, rgb("#55743f"), _em_owl, GOLD),
}


# -- jewelry -----------------------------------------------------------------------------------------------


def chain_loop(a, cx, cy, rx, ry, metal, beads=None, gap=0.9, links=True):
    """A necklace lying in a loose loop open at the bottom (where the pendant
    hangs): an inked chain, optionally strung with `beads(i, t) -> colour`."""
    ts = [math.pi / 2 + gap / 2 + k * (2 * math.pi - gap) / 40 for k in range(41)]
    pts = [(cx + rx * math.cos(t) * (1 + 0.04 * math.sin(3 * t)), cy + ry * math.sin(t)) for t in ts]
    a.ink(pts, DETAIL * 2.0, color=INK)
    a.ink(pts, DETAIL * 1.0, color=metal)
    if links:
        for k in range(0, 41, 2):
            dot(a, pts[k][0], pts[k][1], 1.6, tint(metal, 0.5), 0.9)
    if beads:
        for k in range(1, 40, 2):
            c = beads(k, ts[k])
            if c:
                r = 5.2 if c[1] else 4.0
                a.shape(ellipse(pts[k][0], pts[k][1], r, r, 16), c[0], outline=FINE * 1.2, depth=1, light_k=0.55, mottle=0)
    return pts[0], pts[-1]


def amulet(seed, metal, pendant, size=150, rx=50, ry=40, beads=None):
    a = Art(size, size, seed)
    cx, cy = size / 2, size / 2 - 14
    chain_loop(a, cx, cy, rx, ry, metal, beads)
    px, py = cx, cy + ry + 14
    a.ink([(cx - 10, cy + ry - 2), (px, py - 8), (cx + 10, cy + ry - 2)], DETAIL * 1.6, color=INK)
    a.ink([(cx - 10, cy + ry - 2), (px, py - 8), (cx + 10, cy + ry - 2)], DETAIL * 0.8, color=metal)
    soft_shadow(a, (px, py), 18, 3, 4, 0.3, 3)
    pendant(a, px, py)
    return a.image()


def _disc(metal, r=17, inner=None):
    def p(a, x, y):
        a.shape(ellipse(x, y, r, r, 36), metal, outline=DETAIL * 1.3, depth=3, light_k=0.5, mottle=0)
        a.ink(ellipse(x, y, r - 4, r - 4, 36), FINE, closed=True, color=shade(metal, 0.45), alpha=0.8)
        if inner:
            inner(a, x, y)

    return p


def _teardrop(metal, gem):
    def p(a, x, y):
        pts = chaikin([(x, y - 16), (x + 12, y + 2), (x, y + 18), (x - 12, y + 2)], True, 2)
        a.shape(pts, metal, outline=DETAIL * 1.2, depth=2, light_k=0.5, mottle=0)
        gem_at(a, x, y + 2, 8, gem, metal, "square" if gem == JET else "round")

    return p


def _planes(a, x, y):
    for r, col in ((10, rgb("#5f7ab8")), (6, rgb("#9a5ad0")), (2.5, rgb("#fff4cf"))):
        a.ink(ellipse(x, y, r, r * 0.6, 24, rot=0.5), FINE * 1.3, closed=True, color=col)
    a.ink(ellipse(x, y, 11, 4, 24, rot=-0.6), FINE * 1.1, closed=True, color=rgb("#e0623a"))


def _veiled(a, x, y):
    flat(a, ellipse(x, y, 9, 9, 24), JET, outline=FINE * 1.2)
    a.ink([(x - 7, y - 2), (x + 7, y + 3)], FINE, color=rgb("#6a6f80"), alpha=0.9)
    a.ink([(x - 6, y + 4), (x + 5, y - 5)], FINE, color=rgb("#6a6f80"), alpha=0.9)


def brooch_of_shielding(seed=3701):
    s = 110
    a = Art(s, s, seed)
    m = s / 2
    pts = [(m - 30, m - 26), (m + 30, m - 26), (m + 30, m + 2), (m, m + 34), (m - 30, m + 2)]
    soft_shadow(a, pts, dx=3, dy=4, alpha=0.3)
    a.shape(pts, SILVER, outline=DETAIL * 1.4, corner=6, depth=4, light_k=0.55, mottle=0)
    a.ink([(m - 22, m - 18), (m + 22, m - 18), (m + 22, m + 1), (m, m + 25), (m - 22, m + 1)], FINE * 1.1, closed=True, color=shade(SILVER, 0.45), alpha=0.8)
    gem_at(a, m, m - 2, 8, SAPPHIRE, SILVER)
    a.ink([(m - 34, m - 30), (m + 34, m - 30)], DETAIL * 1.6, color=INK)
    a.ink([(m - 34, m - 30), (m + 34, m - 30)], DETAIL * 0.7, color=SILVER)
    return a.image()


def scarab(seed=3702):
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    beetle = rgb("#3f8a7a")
    soft_shadow(a, (m, m + 2), 32, 3, 4, 0.3, 3)
    a.shape(ellipse(m, m + 4, 26, 32, 40), beetle, outline=DETAIL * 1.4, depth=4, light_k=0.55, mottle=0.04)
    a.ink([(m, m - 12), (m, m + 34)], FINE * 1.4, color=shade(beetle, 0.5))
    a.shape(ellipse(m, m - 22, 16, 9, 24), GOLD, outline=DETAIL * 1.2, depth=2, light_k=0.5, mottle=0)
    a.shape(ellipse(m, m - 34, 9, 6, 20), GOLD, outline=DETAIL, depth=2, light_k=0.5, mottle=0)
    for s_ in (-1, 1):
        for k in range(3):
            y = m - 6 + k * 14
            a.ink([(m + s_ * 24, y), (m + s_ * 36, y - 4 + k * 4)], DETAIL * 0.9, color=INK)
        a.ink([(m + s_ * 5, m - 38), (m + s_ * 12, m - 48)], FINE * 1.3, color=INK)
    dot(a, m - 9, m - 4, 3, tint(beetle, 0.6), 0.9)
    return a.image()


def _sun_pendant(a, x, y):
    for k in range(12):
        t = 2 * math.pi * k / 12
        a.shape([(x + 11 * math.cos(t - 0.2), y + 11 * math.sin(t - 0.2)), (x + 21 * math.cos(t), y + 21 * math.sin(t)), (x + 11 * math.cos(t + 0.2), y + 11 * math.sin(t + 0.2))], GOLD, outline=FINE * 1.2, corner=0, depth=1, light_k=0.5, mottle=0)
    a.shape(ellipse(x, y, 12, 12, 24), GOLD, outline=DETAIL, depth=2, light_k=0.55, mottle=0)
    gem_at(a, x, y, 5, rgb("#fff4cf"), GOLD)


def _evil_pendant(a, x, y):
    pts = [(x, y - 20), (x + 14, y - 2), (x + 6, y + 20), (x - 6, y + 20), (x - 14, y - 2)]
    a.shape(pts, BLACKEN, outline=DETAIL * 1.2, corner=2, depth=2, light_k=0.3, mottle=0)
    for s_ in (-1, 1):
        a.ink([(x + s_ * 8, y - 12), (x + s_ * 18, y - 22)], DETAIL * 1.4, color=INK)
        a.ink([(x + s_ * 8, y - 12), (x + s_ * 18, y - 22)], DETAIL * 0.6, color=rgb("#5a5258"))
    halo(a, x, y + 2, 12, rgb("#d03040"), 0.5)
    gem_at(a, x, y + 2, 6, GARNET, BLACKEN)


def _sphere_pendant(a, x, y):
    a.shape(ellipse(x, y, 18, 18, 36), SILVER, outline=DETAIL * 1.2, depth=3, light_k=0.5, mottle=0)
    a.ink(ellipse(x, y, 14, 14, 36), FINE, closed=True, color=shade(SILVER, 0.45))
    flat(a, ellipse(x, y, 9, 9, 28), rgb("#141216"), outline=FINE * 1.2)
    a.ink(ellipse(x, y, 11, 11, 28), FINE * 0.9, closed=True, color=rgb("#8a6ad8"), alpha=0.8)


def _medallion_mind(a, x, y):
    _disc(SILVER, 18)(a, x, y)
    pts = chaikin([(x - 10, y + 2), (x - 9, y - 7), (x - 2, y - 10), (x + 6, y - 9), (x + 10, y - 2), (x + 7, y + 6), (x - 4, y + 8)], True, 2)
    a.shape(pts, rgb("#e8a8b8"), outline=FINE * 1.2, depth=1, light_k=0.4, mottle=0)
    a.ink([(x - 1, y - 9), (x, y + 6)], FINE * 0.9, color=shade(rgb("#e8a8b8"), 0.5))


def _periapt_wound(a, x, y):
    _teardrop(SILVER, PEARL)(a, x, y)
    a.ink([(x - 5, y + 2), (x + 5, y + 2)], FINE * 1.1, color=rgb("#c84a3a"))
    for dx in (-3, 0, 3):
        a.ink([(x + dx, y - 1), (x + dx, y + 5)], FINE * 0.8, color=rgb("#c84a3a"))


def _fire_beads(i, t):
    return (rgb("#e0623a") if i % 4 == 1 else rgb("#f08a3a"), i % 4 == 1)


def _prayer_beads(i, t):
    special = {5: rgb("#5fb0d8"), 13: rgb("#f2d24a"), 21: rgb("#e0e0e8"), 29: rgb("#7ccf8a"), 35: rgb("#c84a3a")}
    if i in special:
        return (special[i], True)
    return (rgb("#b8946a"), False)


def _bubble_beads(i, t):
    return (rgb("#cfe6f0"), i % 6 == 1)


def _fireball_pendant(a, x, y):
    halo(a, x, y, 18, rgb("#ffb050"), 0.55)
    a.shape(ellipse(x, y, 10, 10, 24), rgb("#e0623a"), outline=DETAIL, depth=2, light_k=0.55, mottle=0)
    dot(a, x - 3, y - 3, 2.2, rgb("#ffe08a"))


def _bubble_pendant(a, x, y):
    a.shape(ellipse(x, y, 13, 13, 28), rgb("#dff2f8"), outline=DETAIL, depth=2, light_k=0.6, mottle=0)
    a.ink([(x - 7, y - 3), (x - 3, y - 8)], FINE * 1.6, color=WHITE)


def _holy_bead(a, x, y):
    a.shape(ellipse(x, y, 9, 9, 20), rgb("#b8946a"), outline=DETAIL, depth=2, light_k=0.5, mottle=0)
    a.ink([(x - 6, y), (x + 6, y)], FINE * 1.2, color=GOLD)
    a.ink([(x, y - 6), (x, y + 6)], FINE * 1.2, color=GOLD)


JEWELRY = {
    "Amulet of Health": lambda: amulet(3711, GOLD, _teardrop(GOLD, RUBY)),
    "Amulet of Proof against Detection and Location": lambda: amulet(3712, rgb("#7a7e86"), _disc(rgb("#7a7e86"), 16, _veiled)),
    "Amulet of the Planes": lambda: amulet(3713, GOLD, _disc(GOLD, 18, _planes)),
    "Brooch of Shielding": brooch_of_shielding,
    "Medallion of Thoughts": lambda: amulet(3714, SILVER, _medallion_mind),
    "Necklace of Adaptation": lambda: amulet(3715, SILVER, _bubble_pendant, beads=_bubble_beads),
    "Necklace of Fireballs": lambda: amulet(3716, BRASS, _fireball_pendant, beads=_fire_beads),
    "Necklace of Prayer Beads": lambda: amulet(3717, rgb("#8a6a4a"), _holy_bead, beads=_prayer_beads),
    "Periapt of Health": lambda: amulet(3718, GOLD, _teardrop(GOLD, rgb("#d0485a"))),
    "Periapt of Proof against Poison": lambda: amulet(3719, SILVER, _teardrop(SILVER, JET)),
    "Periapt of Wound Closure": lambda: amulet(3720, SILVER, _periapt_wound),
    "Scarab of Protection": scarab,
    "Talisman of Pure Good": lambda: amulet(3721, GOLD, _sun_pendant),
    "Talisman of the Sphere": lambda: amulet(3722, SILVER, _sphere_pendant),
    "Talisman of Ultimate Evil": lambda: amulet(3723, BLACKEN, _evil_pendant),
}


# -- gems and stones ---------------------------------------------------------------------------------------


def cut_gem(seed, color, s=130, r=30, glow_a=0.0, cut="brilliant"):
    """A loose cut gem from above: the table and the facets around it."""
    a = Art(s, s, seed)
    m = s / 2
    if glow_a:
        halo(a, m, m, r * 2.2, color, glow_a)
    n = 8
    outer = [(m + r * math.cos(k * 2 * math.pi / n + math.pi / 8), m + r * math.sin(k * 2 * math.pi / n + math.pi / 8)) for k in range(n)]
    if cut == "emerald":
        outer = rect(m - r * 1.1, m - r * 0.8, m + r * 1.1, m + r * 0.8)
        outer = [outer[0], outer[1], outer[2], outer[3]]
    soft_shadow(a, outer, dx=4, dy=5, alpha=0.35)
    a.shape(outer, color, outline=DETAIL * 1.3, corner=1, wob=0.2, depth=4, shade_k=0.45, light_k=0.4, mottle=0)
    tbl = [(m + (x - m) * 0.52, m + (y - m) * 0.52) for x, y in outer]
    a.shape(tbl, tint(color, 0.18), outline=FINE * 1.2, corner=0, wob=0.1, depth=1, shade_k=0.15, light_k=0.3, ao=0, mottle=0)
    for (x0, y0), (x1, y1) in zip(outer, tbl):
        a.ink([(x0, y0), (x1, y1)], FINE * 0.9, color=shade(color, 0.45), alpha=0.7, wob=0)
    a.ink([(m - r * 0.55, m - r * 0.1), (m - r * 0.2, m - r * 0.5)], FINE * 1.8, color=WHITE, alpha=0.9)
    return a.image()


def prism(seed, color, glow_a=0.5):
    """Gem of Brightness: a long hexagonal prism lying flat, glowing."""
    w, h = 190, 150
    a = Art(w, h, seed)
    cx, cy, ang = 95, 75, -0.3
    halo(a, cx, cy, 70, color, glow_a)
    R = lambda pts: L(pts, cx, cy, ang)  # noqa: E731
    body = R([(-40, -14), (32, -14), (46, 0), (32, 14), (-40, 14), (-50, 0)])
    soft_shadow(a, body, dx=4, dy=5, alpha=0.3)
    a.shape(body, color, outline=DETAIL * 1.3, corner=1, wob=0.2, depth=3, light_k=0.55, mottle=0)
    for y in (-5, 5):
        a.ink(R([(-44, y), (38, y)]), FINE * 0.9, color=shade(color, 0.35), alpha=0.7, wob=0)
    a.ink(R([(-30, -9), (20, -9)]), FINE * 1.8, color=WHITE, alpha=0.9)
    sparkle(a, *R([(36, -4)])[0], 6)
    return a.image()


def ioun(seed, color, shape="sphere", second=None, glow_a=0.45):
    """A marble-sized Ioun stone, drawn larger than life so its shape reads,
    with the faint glow of its orbit."""
    s = 130
    a = Art(s, s, seed)
    m = s / 2
    halo(a, m, m, 60, color, glow_a)
    a.ink(ellipse(m, m, 42, 14, 48, rot=-0.4), FINE * 1.2, closed=True, color=tint(color, 0.3), alpha=0.7)
    r = 20
    if shape == "sphere":
        pts = ellipse(m, m, r, r, 32)
    elif shape == "ellipsoid":
        pts = ellipse(m, m, r * 1.3, r * 0.8, 32, rot=-0.4)
    elif shape == "rhomboid":
        pts = [(m - r * 1.3, m), (m, m - r), (m + r * 1.3, m), (m, m + r)]
    elif shape == "prism":
        pts = [(m + r * math.cos(-math.pi / 2 + k * 2 * math.pi / 3), m + r * math.sin(-math.pi / 2 + k * 2 * math.pi / 3)) for k in range(3)]
    else:  # spindle
        pts = chaikin([(m - r * 1.5, m), (m, m - r * 0.6), (m + r * 1.5, m), (m, m + r * 0.6)], True, 1)
    path = a.shape(pts, color, outline=DETAIL * 1.2, corner=2, depth=3, light_k=0.6, mottle=0)
    if second:
        with a.clip(path):
            a.ink([(m - r, m + 4), (m - 4, m - 2), (m + 4, m + 6), (m + r, m - 2)], DETAIL * 1.6, color=second, alpha=0.9)
    dot(a, m - 5, m - 5, 2.6, WHITE, 0.9)
    return a.image()


def stone(seed, color, s=110, r=34, runes=None, polished=True, marks=None):
    a = Art(s, s, seed)
    m = s / 2
    pts = blob(m, m, r, a.rng, 9, 0.12, ry=r * 0.8) if not polished else ellipse(m, m, r, r * 0.78, 40, rot=0.3)
    soft_shadow(a, pts, dx=4, dy=5, alpha=0.35)
    a.shape(pts, color, outline=DETAIL * 1.4, corner=3, smooth=not polished, depth=5, light_k=0.5 if polished else 0.35, mottle=0.06)
    if marks:
        marks(a, m, m)
    if runes:
        for k in range(5):
            t = 2 * math.pi * k / 5
            x, y = m + r * 0.5 * math.cos(t), m + r * 0.4 * math.sin(t)
            a.ink([(x - 3, y - 4), (x + 1, y), (x - 2, y + 4)], FINE * 1.2, color=runes, alpha=0.95)
    if polished:
        a.ink([(m - r * 0.55, m - r * 0.1), (m - r * 0.25, m - r * 0.45)], FINE * 2, color=WHITE, alpha=0.85)
    return a.image()


def _agate(a, m, _):
    for k, c in enumerate((rgb("#e8c89a"), rgb("#b8784a"), rgb("#f2e2c8"))):
        a.ink(ellipse(m, m, 24 - k * 7, 17 - k * 5, 36, rot=0.3), DETAIL * 0.9, closed=True, color=c, alpha=0.85)


def pearl(seed=3801):
    s = 80
    a = Art(s, s, seed)
    m = s / 2
    halo(a, m, m, 30, rgb("#e6e0ff"), 0.35)
    soft_shadow(a, (m, m), 18, 3, 4, 0.35, 3)
    a.shape(ellipse(m, m, 18, 18, 36), PEARL, outline=DETAIL * 1.3, depth=4, light_k=0.6, mottle=0.03)
    a.ink(ellipse(m + 2, m + 2, 11, 11, 24)[4:14], FINE * 1.4, color=rgb("#d8c8ec"), alpha=0.8)
    dot(a, m - 6, m - 6, 3.2, WHITE, 0.95)
    return a.image()


def small_bead(seed, color, s=64, r=14, soft=False):
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), r, 3, 4, 0.35, 2.5)
    a.shape(ellipse(m, m, r, r * (0.9 if soft else 1), 28), color, outline=DETAIL * 1.2, depth=2.5, light_k=0.55 if not soft else 0.35, mottle=0.04 if soft else 0)
    dot(a, m - r * 0.35, m - r * 0.35, r * 0.22, WHITE, 0.85 if not soft else 0.5)
    return a.image()


def sending_stones(seed=3802):
    w, h = 150, 100
    a = Art(w, h, seed)
    from PIL import Image  # noqa: F401

    for x, y, rot in ((48, 50, 0.2), (104, 54, -0.3)):
        pts = ellipse(x, y, 26, 20, 36, rot=rot)
        soft_shadow(a, pts, dx=3, dy=4, alpha=0.32)
        a.shape(pts, rgb("#8a9aa6"), outline=DETAIL * 1.3, depth=4, light_k=0.5, mottle=0.06)
        # The matching carving: a spiral on both.
        sp = [(x + (1 + 12 * k / 30) * math.cos(k / 30 * 3.2 * math.pi + rot), y + (1 + 9 * k / 30) * math.sin(k / 30 * 3.2 * math.pi + rot)) for k in range(31)]
        a.ink(sp, FINE * 1.4, color=rgb("#4a5a66"), alpha=0.95)
    return a.image()


GEMS = {
    "Elemental Gem (Air)": lambda: cut_gem(3811, rgb("#5f8fd8"), glow_a=0.3),
    "Elemental Gem (Water)": lambda: cut_gem(3812, EMERALD, glow_a=0.3, cut="emerald"),
    "Elemental Gem (Fire)": lambda: cut_gem(3813, rgb("#d0463a"), glow_a=0.3),
    "Elemental Gem (Earth)": lambda: cut_gem(3814, rgb("#f0cc4a"), glow_a=0.3),
    "Gem of Brightness": lambda: prism(3815, rgb("#f6f0c8"), 0.6),
    "Gem of Seeing": lambda: cut_gem(3816, rgb("#cfe6f0"), r=32, glow_a=0.25),
    "Ioun Stone (Absorption)": lambda: ioun(3821, rgb("#c8b8e8"), "ellipsoid"),
    "Ioun Stone (Agility)": lambda: ioun(3822, rgb("#a8243a"), "sphere"),
    "Ioun Stone (Awareness)": lambda: ioun(3823, rgb("#2f4a8a"), "rhomboid"),
    "Ioun Stone (Fortitude)": lambda: ioun(3824, rgb("#f0a8c0"), "rhomboid"),
    "Ioun Stone (Greater Absorption)": lambda: ioun(3825, rgb("#c8b8e8"), "ellipsoid", second=rgb("#7ccf8a")),
    "Ioun Stone (Insight)": lambda: ioun(3826, rgb("#5fb8f0"), "sphere", glow_a=0.7),
    "Ioun Stone (Intellect)": lambda: ioun(3827, rgb("#d0463a"), "sphere", second=rgb("#3f6fc8")),
    "Ioun Stone (Leadership)": lambda: ioun(3828, rgb("#f0a8c0"), "sphere", second=rgb("#5fa86a")),
    "Ioun Stone (Mastery)": lambda: ioun(3829, rgb("#a8dca0"), "prism"),
    "Ioun Stone (Protection)": lambda: ioun(3830, rgb("#c89a9a"), "prism"),
    "Ioun Stone (Regeneration)": lambda: ioun(3831, rgb("#f0ece4"), "spindle"),
    "Ioun Stone (Reserve)": lambda: ioun(3832, rgb("#8a3ad0"), "prism"),
    "Ioun Stone (Strength)": lambda: ioun(3833, rgb("#a8c8ec"), "rhomboid"),
    "Ioun Stone (Sustenance)": lambda: ioun(3834, rgb("#e6eef0"), "spindle", glow_a=0.3),
    "Pearl of Power": pearl,
    "Stone of Good Luck": lambda: stone(3841, rgb("#c08a5a"), marks=_agate),
    "Stone of Controlling Earth Elementals": lambda: stone(3842, rgb("#8a7a62"), s=140, r=48, runes=rgb("#f2c24a"), polished=False),
    "Sending Stones": sending_stones,
    "Bead of Force": lambda: small_bead(3843, rgb("#3a3640")),
    "Bead of Nourishment": lambda: small_bead(3844, rgb("#e2d49a"), soft=True),
}


SRD_MAGIC = {name: tight(fn) for name, fn in {**POTIONS_, **RINGS, **RODS, **STAFFS, **WANDS, **BOOKS, **JEWELRY, **GEMS}.items()}

SRD_MAGIC_COLORABLE = {"Potion of Resistance", "Ring of Resistance", "Spell Scroll", "Spell Scroll (Rolled)"}
