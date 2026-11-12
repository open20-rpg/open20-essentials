"""Variants of approved designs (batch: variety): trees, bushes, rocks,
plants, logs and furniture in other woods/colors. They reuse the approved
drawing functions; colors are swapped through the modules' palette
constants so the drawings themselves stay exactly as approved."""

import math
from contextlib import contextmanager

from PIL import Image

import obj_furniture as furn
import obj_nature as nat
import obj_stone as stn
import objects as objs
import trees as tr
from kit import STONE, soft_shadow
from obj_stone import moss, stone_block
from objects import canopy
from pen import DETAIL, FINE, OUTLINE, Art, blob, chaikin, ellipse, rgb, shade, tint, vary

# -- helpers ------------------------------------------------------------------------------------


@contextmanager
def swap(module, **values):
    """Temporarily replace palette constants in a module (restored after)."""
    old = {k: module.__dict__[k] for k in values}
    module.__dict__.update(values)
    try:
        yield
    finally:
        module.__dict__.update(old)


def recolored(fn, *modules_values, **kw):
    """fn drawn with some modules' palette constants swapped."""

    def make():
        from contextlib import ExitStack

        with ExitStack() as st:
            for module, values in modules_values:
                st.enter_context(swap(module, **values))
            return fn(**kw)

    return make


def composite(size, parts):
    """Several images on one canvas: parts = [(img, x, y)] (top-left), in order."""
    w, h = size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for img, x, y in parts:
        out.alpha_composite(img, (int(x), int(y)))
    return out


# -- palettes ------------------------------------------------------------------------------------

P = lambda d, m, l, ink: ((rgb(d), rgb(m), rgb(l)), rgb(ink))  # noqa: E731
OLIVE = P("#545a26", "#7a8236", "#a6ac5a", "#24260e")
TEAL = P("#1f5a52", "#2f7a6e", "#5aa596", "#0f2a26")
DARK_PINE = P("#1b3a26", "#2a5034", "#3f6e4a", "#0e1c12")
YELLOW_AUTUMN = P("#a07a1e", "#d0a632", "#ecd06a", "#3a2c0c")
ORANGE = P("#a8521c", "#d6782c", "#f0a85a", "#3c1c0a")
PURPLE = P("#4a2a6a", "#6e4696", "#9a78c6", "#1e1030")
SNOWY = P("#7a9a8c", "#b6cec4", "#eef4f0", "#2a3a34")
DEAD_BROWN = P("#5a4630", "#7a6244", "#a08866", "#241a10")
LIME = P("#4a7a22", "#74a832", "#a6d064", "#1c300c")
BLUE_SPRUCE = P("#2a4a5a", "#3e6676", "#6a929c", "#101e24")


def pine_p(seed, size, pal, **kw):
    greens, ink = pal
    return tr.pine(seed, size=size, colors=greens, ink=ink, **kw)


def cluster(seed, specs, size=(900, 760)):
    """2-3 overlapping canopies: specs = [(kind, seed, size, palette, x, y)],
    drawn back (bottom-right) to front."""
    parts = []
    for kind, s, sz, pal, x, y in specs:
        img = tr.leafy(s, pal, size=sz, reach=(0.02, 0.14)) if kind == "leafy" else pine_p(s, sz, pal)
        parts.append((img, x, y))
    return composite(size, parts)


def sapling(seed, pal=tr.OAK):
    return tr.leafy(seed, pal, size=260, rings=(0.65, 0.3), reach=(0.02, 0.1), bump=(0.14, 0.22))


# -- trees ---------------------------------------------------------------------------------------

TREES_V = {
    "Oak Tree (Large)": lambda: tr.leafy(61, tr.OAK, size=860, lobes=(5, 8), reach=(0.04, 0.16)),
    "Oak Tree (Small)": lambda: tr.leafy(62, tr.OAK, size=480, rings=(0.75, 0.45, 0.2), reach=(0.02, 0.1)),
    "Olive Tree": lambda: tr.leafy(63, OLIVE, size=600, bump=(0.09, 0.14), lobes=(4, 7), reach=(0.1, 0.26)),
    "Teal Tree": lambda: tr.leafy(64, TEAL, size=660, reach=(0.02, 0.12)),
    "Golden Autumn Tree": lambda: tr.leafy(65, YELLOW_AUTUMN, size=680, bump=(0.14, 0.22)),
    "Orange Autumn Tree": lambda: tr.leafy(66, ORANGE, size=640, reach=(0.04, 0.16)),
    "Fey Tree": lambda: tr.leafy(67, PURPLE, size=680, bump=(0.16, 0.24), reach=(0.02, 0.12)),
    "Snowy Tree": lambda: tr.leafy(68, SNOWY, size=640, reach=(0.02, 0.12)),
    "Withered Tree": lambda: tr.leafy(69, DEAD_BROWN, size=600, bump=(0.07, 0.11), lobes=(4, 7), reach=(0.1, 0.24)),
    "Spring Tree": lambda: tr.leafy(70, LIME, size=620, bump=(0.15, 0.24)),
    "Crimson Tree (Small)": lambda: tr.leafy(71, tr.CRIMSON, size=460, rings=(0.72, 0.44, 0.2)),
    "Birch Tree (Large)": lambda: tr.leafy(72, tr.BIRCH, size=760, bump=(0.09, 0.14)),
    "Blossom Tree (Small)": lambda: tr.leafy(73, tr.BLOSSOM, size=440, bump=(0.16, 0.26), rings=(0.7, 0.4)),
    "Forest Tree (Large)": lambda: tr.leafy(74, tr.DEEP, size=860, bump=(0.08, 0.13), lobes=(5, 8)),
    "Colorable Tree (Small)": lambda: tr.leafy(75, tr.COLORABLE, size=460, rings=(0.72, 0.44, 0.2)),
    "Pine Tree (Dark)": lambda: pine_p(76, 660, DARK_PINE),
    "Blue Spruce": lambda: pine_p(77, 620, BLUE_SPRUCE),
    "Snowy Pine": lambda: pine_p(78, 620, SNOWY),
    "Pine Tree (Large)": lambda: pine_p(79, 820, ((rgb("#2c5233"), rgb("#3f6e44"), rgb("#6a9a64")), rgb("#142218"))),
    "Dead Pine": lambda: pine_p(80, 560, DEAD_BROWN),
    "Fir Sapling": lambda: pine_p(81, 300, ((rgb("#2c5233"), rgb("#3f6e44"), rgb("#6a9a64")), rgb("#142218")), rings=(0.7, 0.4)),
    "Oak Sapling": lambda: sapling(82),
    "Autumn Sapling": lambda: sapling(83, tr.AUTUMN),
    "Blossom Sapling": lambda: sapling(84, tr.BLOSSOM),
    "Dead Tree 2": lambda: tr.dead_tree(85),
    "Dead Tree (Small)": lambda: tr.dead_tree(86, size=440),
    "Tree Stump 2": lambda: tr.stump(87),
    "Tree Stump (Small)": lambda: tr.stump(88, size=200),
    "Tree Cluster": lambda: cluster(89, [("leafy", 90, 560, tr.DEEP, 320, 200), ("leafy", 91, 520, tr.OAK, 40, 220), ("leafy", 92, 480, tr.OAK, 200, 0)]),
    "Autumn Cluster": lambda: cluster(93, [("leafy", 94, 520, ORANGE, 340, 220), ("leafy", 95, 500, tr.AUTUMN, 40, 200), ("leafy", 96, 460, YELLOW_AUTUMN, 220, 10)]),
    "Pine Cluster": lambda: cluster(97, [("pine", 98, 520, DARK_PINE, 340, 220), ("pine", 99, 480, ((rgb("#2c5233"), rgb("#3f6e44"), rgb("#6a9a64")), rgb("#142218")), 40, 230), ("pine", 100, 440, BLUE_SPRUCE, 220, 20)]),
    "Twin Oaks": lambda: cluster(101, [("leafy", 102, 520, tr.OAK, 300, 120), ("leafy", 103, 480, tr.OAK, 20, 60)], size=(840, 660)),
}

# -- bushes ---------------------------------------------------------------------------------------


def bush_v(seed, greens=objs.FOLIAGE, ink=objs.FOLIAGE_INK, size=300, berries=None, flowers=None, bumps=9):
    a = Art(size, size, seed)
    m = size / 2
    R = size * 0.39
    canopy(a, m, m, R, greens, ink, bumps=bumps, clusters=(0.72, 0.45, 0.2) if size > 220 else (0.6, 0.25))
    dots = berries or flowers
    if dots:
        for _ in range(int(7 * size / 300) + 3):
            ang, r = a.rng.uniform(0, 6.28), a.rng.uniform(0.1, 0.8) * R
            x, y = m + r * math.cos(ang), m + r * math.sin(ang)
            if berries:
                a.shape(ellipse(x, y, 7, 7, 20), berries, outline=FINE * 1.4, depth=3, light_k=0.6, mottle=0)
            else:
                for k in range(5):
                    pa = 2 * math.pi * k / 5
                    a.shape(ellipse(x + 5 * math.cos(pa), y + 5 * math.sin(pa), 5, 3.5, 12, rot=pa), flowers, outline=FINE, depth=1, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
                a.shape(ellipse(x, y, 2.4, 2.4, 8), rgb("#f2d24a"), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    return a.image()


def hedge(seed, length=640, greens=objs.FOLIAGE, ink=objs.FOLIAGE_INK):
    """A trimmed hedge: one long canopy (same look as the bushes: lobed edge,
    concentric scalloped pen lines inside, light top-left)."""
    import skia

    from kit import scallop

    h = 210
    a = Art(length, h, seed)
    cx, cy = length / 2, h / 2
    rx, ry = length / 2 - 16, h / 2 - 16
    dark, mid, light = greens
    def sq(t, k):
        # A superellipse (rounded rectangle) point at angle t, scale k.
        c, s_ = math.cos(t), math.sin(t)
        return (cx + rx * k * math.copysign(abs(c) ** 0.45, c), cy + ry * k * math.copysign(abs(s_) ** 0.45, s_))

    nb = int(length / 22)
    edge = []
    for j in range(nb * 12):
        t = 2 * math.pi * j / (nb * 12)
        b = (j % 12) / 12
        x, y = sq(t, 1)
        nx, ny = x - cx, y - cy
        L = math.hypot(nx / rx, ny / ry) or 1
        bump = 1 - 0.06 + 0.06 * math.sin(math.pi * b)
        edge.append((cx + nx * bump, cy + ny * bump))

    def inside(art, path):
        g = skia.Path()
        g.addOval(skia.Rect.MakeXYWH(cx - rx * 0.9, cy - ry * 0.9, rx * 1.2, ry * 1.0))
        art.fill_path(g, light, 0.5, blur=ry * 0.4)
        for rr in (0.75, 0.45):
            ang = art.rng.uniform(0, 2 * math.pi)
            end = ang + 2 * math.pi - 0.2
            while ang < end:
                bumps = art.rng.randint(1, 4)
                bw = art.rng.uniform(0.12, 0.2)
                span = min(bumps * bw, end - ang)
                pts = []
                for j in range(int(span * 60) + 2):
                    t = ang + span * j / (int(span * 60) + 1)
                    ph = ((t - ang) / bw) % 1
                    k = rr + 0.06 * math.sin(math.pi * ph)
                    pts.append(sq(t, k))
                art.ink(pts, DETAIL * art.rng.uniform(0.6, 1.0), color=ink, alpha=art.rng.uniform(0.55, 0.85), wob=0.4)
                ang += span + art.rng.uniform(0.08, 0.3)

    a.shape(edge, mid, outline=OUTLINE, corner=0, wob=0.6, depth=ry * 0.12, shade_k=0.5, light_k=0.25, ao=0.35, mottle=0.06, detail=inside)
    return a.image()


BUSHES_V = {
    "Bush (Small)": lambda: bush_v(111, size=200),
    "Bush (Large)": lambda: bush_v(112, size=380, bumps=11),
    "Dark Bush": lambda: bush_v(113, tr.DEEP[0], tr.DEEP[1]),
    "Light Bush": lambda: bush_v(114, LIME[0], LIME[1]),
    "Olive Bush": lambda: bush_v(115, OLIVE[0], OLIVE[1], size=260),
    "Autumn Bush": lambda: bush_v(116, tr.AUTUMN[0], tr.AUTUMN[1]),
    "Crimson Bush": lambda: bush_v(117, tr.CRIMSON[0], tr.CRIMSON[1], size=260),
    "Blueberry Bush": lambda: bush_v(118, berries=rgb("#4a5aa0")),
    "Red Berry Bush": lambda: bush_v(119, berries=rgb("#c84a3e"), size=260),
    "White Flower Bush": lambda: bush_v(120, flowers=rgb("#f3eee2")),
    "Pink Flower Bush": lambda: bush_v(121, tr.DEEP[0], tr.DEEP[1], flowers=rgb("#e88aa8")),
    "Yellow Flower Bush": lambda: bush_v(122, flowers=rgb("#e6b84a"), size=260),
    "Fey Bush": lambda: bush_v(123, PURPLE[0], PURPLE[1], size=260),
    "Snowy Bush": lambda: bush_v(124, SNOWY[0], SNOWY[1], size=260),
    "Hedge": lambda: hedge(125),
    "Short Hedge": lambda: hedge(126, 380),
}

# -- rocks ----------------------------------------------------------------------------------------

SANDSTONE = rgb("#c8a878")
BASALT = rgb("#5a5a60")
GRANITE = rgb("#b0a8a0")
SLATE = rgb("#6e767c")


def boulder_v(seed, color=STONE, size=300, r=0.4, jag=0.16, n=10, mossy=0, top=True):
    a = Art(size, size, seed)
    m = size / 2
    p = stone_block(a, blob(m, m, size * r, a.rng, n, jag), color, smooth=True, cracks=1, light_k=0.45, depth=size * 0.08)
    if top:
        with a.clip(p):
            t = blob(m - size * 0.08, m - size * 0.08, size * r * 0.5, a.rng, 7, 0.2)
            a.shape(chaikin(t, True, 1), tint(color, 0.18), outline=DETAIL, corner=0, depth=6, shade_k=0.2, light_k=0.3, ao=0)
    if mossy:
        moss(a, p, mossy, (size * 0.06, size * 0.11))
    return a.image()


def flat_rock(seed, color=GRANITE, w=360, h=240):
    a = Art(w, h, seed)
    stone_block(a, blob(w / 2, h / 2, w * 0.42, a.rng, 9, 0.1, ry=h * 0.38), color, smooth=True, cracks=2, light_k=0.4, depth=8)
    return a.image()


def rock_cluster(seed, color=STONE, count=5, size=320):
    a = Art(size, size, seed)
    m = size / 2
    rocks = [(m + a.rng.uniform(-size * 0.22, size * 0.22), m + a.rng.uniform(-size * 0.2, size * 0.2), a.rng.uniform(size * 0.1, size * 0.18)) for _ in range(count)]
    for x, y, r in sorted(rocks, key=lambda q: q[1]):
        pts = blob(x, y, r, a.rng, 8, 0.18)
        soft_shadow(a, pts, dx=4, dy=5)
        stone_block(a, pts, vary(a.rng, color, 0.07), outline=DETAIL * 1.6, smooth=True, cracks=0, light_k=0.45, depth=r * 0.15)
    return a.image()


def jagged_rock(seed, color=SLATE, size=280):
    a = Art(size, size, seed)
    m = size / 2
    pts = [(m + size * 0.38 * a.rng.uniform(0.7, 1.05) * math.cos(t), m + size * 0.38 * a.rng.uniform(0.7, 1.05) * math.sin(t)) for t in [2 * math.pi * k / 9 for k in range(9)]]
    p = stone_block(a, pts, color, corner=8, cracks=1, light_k=0.45, depth=size * 0.08)
    with a.clip(p):
        a.ink([(m - size * 0.2, m - size * 0.1), (m + size * 0.05, m - size * 0.04), (m + size * 0.25, m - size * 0.2)], DETAIL, alpha=0.85)
        a.ink([(m + size * 0.05, m - size * 0.04), (m + size * 0.08, m + size * 0.3)], DETAIL, alpha=0.85)
    return a.image()


ROCKS_V = {
    "Boulder (Small)": lambda: boulder_v(131, size=180),
    "Boulder (Large)": lambda: boulder_v(132, size=440, n=12),
    "Sandstone Boulder": lambda: boulder_v(133, SANDSTONE, size=300),
    "Basalt Boulder": lambda: boulder_v(134, BASALT, size=300),
    "Granite Boulder": lambda: boulder_v(135, GRANITE, size=320),
    "Mossy Boulder 2": lambda: boulder_v(136, stn.DARK_STONE, size=320, mossy=8),
    "Mossy Rock (Small)": lambda: boulder_v(137, STONE, size=200, mossy=4),
    "Round Stone": lambda: boulder_v(138, GRANITE, size=220, r=0.4, jag=0.05, top=False),
    "Long Rock": lambda: flat_rock(139, STONE, 420, 200),
    "Flat Rock": lambda: flat_rock(140),
    "Flat Sandstone": lambda: flat_rock(141, SANDSTONE, 320, 240),
    "Rock Cluster": lambda: rock_cluster(142),
    "Sandstone Cluster": lambda: rock_cluster(143, SANDSTONE, 6),
    "Basalt Cluster": lambda: rock_cluster(144, BASALT, 5),
    "Slate Cluster": lambda: rock_cluster(145, SLATE, 4, 280),
    "Jagged Rock": lambda: jagged_rock(146),
    "Jagged Basalt": lambda: jagged_rock(147, BASALT, 320),
    "Rock (Pale)": lambda: boulder_v(148, rgb("#c9c3b8"), size=260),
    "Rock (Reddish)": lambda: boulder_v(149, rgb("#a8806a"), size=260),
    "Pebble Patch": lambda: rock_cluster(150, GRANITE, 11, 260),
}

# -- plants ---------------------------------------------------------------------------------------

PLANTS_V = {
    "Grass Tuft 2": lambda: nat.grass_tuft(161),
    "Dry Grass Tuft": recolored(nat.grass_tuft, (nat, {"GREEN": rgb("#a89a5a"), "GREEN_L": rgb("#c8b878"), "GREEN_D": rgb("#7a6a3a")}), seed=162),
    "Tall Grass 2": lambda: nat.tall_grass(169),
    "Fern 2": lambda: nat.fern(164),
    "Dark Fern": recolored(nat.fern, (nat, {"GREEN": rgb("#3f6a3a"), "GREEN_L": rgb("#5a8a4a"), "GREEN_D": rgb("#24402a")}), seed=165),
    "Purple Flowers": lambda: nat.flowers(166, rgb("#9a6ab8"), rgb("#f2e08a")),
    "Pink Flowers": lambda: nat.flowers(167, rgb("#e88aa8"), rgb("#f6d24a")),
    "Orange Flowers": lambda: nat.flowers(168, rgb("#e6843a"), rgb("#6a3a1a")),
    "Lavender": lambda: nat.flowers(169, rgb("#a89ad8"), rgb("#6a5aa0")),
    "Yellow Flowers 2": lambda: nat.flowers(170),
    "Purple Mushrooms": lambda: nat.mushrooms(171, rgb("#8a5ab0")),
    "Yellow Mushrooms": lambda: nat.mushrooms(172, rgb("#d8b84a"), spots=False),
    "White Mushrooms": lambda: nat.mushrooms(173, rgb("#e8e0d0"), spots=False),
    "Blue Mushrooms": lambda: nat.mushrooms(174, rgb("#4f7ac0")),
    "Reeds 2": lambda: nat.reeds(175),
    "Marsh Reeds": recolored(nat.reeds, (nat, {"GREEN_D": rgb("#5a6a2a")}), seed=176),
    "Clover 2": lambda: nat.clover(177),
    "Vines 2": lambda: nat.vines(178),
    "Lily Pads": lambda: lily_pads(179),
    "Water Lilies": lambda: lily_pads(180, flowers=True),
}


def lily_pads(seed, flowers=False):
    s = 300
    a = Art(s, s, seed)
    for _ in range(7):
        x, y = a.rng.uniform(50, s - 50), a.rng.uniform(50, s - 50)
        r = a.rng.uniform(20, 34)
        t = a.rng.uniform(0, 6.28)
        pad = [(x, y)] + [(x + r * math.cos(t + 0.35 + k * 0.2), y + r * math.sin(t + 0.35 + k * 0.2)) for k in range(29)]
        a.shape(pad, vary(a.rng, rgb("#6d9a48"), 0.06), outline=DETAIL, corner=0, depth=2, light_k=0.4, mottle=0)
        a.ink([(x, y), (x + r * 0.8 * math.cos(t + 3.3), y + r * 0.8 * math.sin(t + 3.3))], FINE, color=rgb("#3f6a2a"), alpha=0.7)
    if flowers:
        for _ in range(3):
            x, y = a.rng.uniform(70, s - 70), a.rng.uniform(70, s - 70)
            for k in range(8):
                pa = 2 * math.pi * k / 8
                a.shape(ellipse(x + 9 * math.cos(pa), y + 9 * math.sin(pa), 9, 5, 14, rot=pa), rgb("#f2c2d2"), outline=FINE * 1.1, depth=1, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
            a.shape(ellipse(x, y, 5, 5, 12), rgb("#f6d24a"), outline=FINE, depth=1, mottle=0)
    return a.image()


def log_v(seed, bark=None, mossy=False, hollow=False):
    """The approved fallen log (obj_nature.fallen_log) on a slightly taller
    canvas so its branch stub never touches the top edge."""
    import obj_nature as n2
    from obj_nature import bark_strokes, tube

    BARK = bark or n2.BARK
    w, h = 520, 220
    a = Art(w, h, seed)
    cy = h / 2 + 8
    spine = [(40 + (w - 100) * t, cy + 10 * math.sin(t * 2.5 + 1)) for t in [i / 20 for i in range(21)]]
    poly = tube(spine, 92, 80)
    stub = tube([(200, cy - 30), (230, 34), (250, 20)], 26, 14)
    a.shape(stub, BARK, outline=DETAIL * 1.3, corner=0, depth=4)
    body = a.shape(poly, BARK, corner=0, depth=12, light_k=0.3, detail=lambda art, p: bark_strokes(art, spine, 92, BARK, (-0.32, -0.1, 0.12, 0.34)))
    if mossy:
        with a.clip(body):
            for _ in range(7):
                x = a.rng.uniform(60, w - 90)
                a.shape(blob(x, cy - 30, a.rng.uniform(20, 36), a.rng, 9, 0.3, ry=a.rng.uniform(14, 22)), n2.MOSS, outline=0, smooth=True, depth=3, shade_k=0.3, light_k=0.3, ao=0, mottle=0.1)
    ex, ey = spine[-1]
    from kit import WOOD_LIGHT

    if hollow:
        a.shape(ellipse(ex, ey, 22, 40, 40), WOOD_LIGHT, outline=DETAIL * 1.2, depth=3, mottle=0)
        a.shape(ellipse(ex - 2, ey, 13, 26, 32), rgb("#2c2220"), outline=DETAIL, depth=3, shade_k=0, light_k=0, ao=0)
    else:
        def rings(art, p):
            for rr in (0.35, 0.65):
                art.ink(ellipse(ex, ey, 20 * rr, 38 * rr, 28), FINE, closed=True, color=shade(WOOD_LIGHT, 0.45), alpha=0.8)
            art.ink([(ex, ey), (ex + 6, ey - 30)], FINE * 1.2, alpha=0.8)

        a.shape(ellipse(ex, ey, 22, 40, 40), WOOD_LIGHT, outline=DETAIL * 1.2, depth=3, mottle=0, detail=rings)
    return a.image()


# -- logs & wood ------------------------------------------------------------------------------------

DARK_BARK = rgb("#5a4230")
PALE_BARK = rgb("#9a8a72")
BIRCH_BARK = rgb("#ddd6c6")

LOGS_V = {
    "Fallen Log 2": lambda: log_v(191),
    "Dark Log": lambda: log_v(192, DARK_BARK),
    "Pale Log": lambda: log_v(193, PALE_BARK),
    "Birch Log": lambda: log_v(194, BIRCH_BARK),
    "Mossy Log 2": lambda: log_v(195, mossy=True),
    "Hollow Log 2": lambda: log_v(196, hollow=True),
    "Mossy Dark Log": lambda: log_v(197, DARK_BARK, mossy=True),
    "Fallen Branch 2": lambda: nat.branch(204),
    "Twigs 2": lambda: nat.twigs(199),
    "Dark Twigs": recolored(nat.twigs, (nat, {"BARK": DARK_BARK}), seed=200),
}

# -- furniture in other woods --------------------------------------------------------------------------

WOODS = {
    "Dark": dict(WOOD=rgb("#6e4a30"), WOOD_DARK=rgb("#4e3422"), WOOD_LIGHT=rgb("#8e6a48")),
    "Pale": dict(WOOD=rgb("#c9a878"), WOOD_DARK=rgb("#a8865a"), WOOD_LIGHT=rgb("#dcc49a")),
    "Red": dict(WOOD=rgb("#9a5a3e"), WOOD_DARK=rgb("#6e3c28"), WOOD_LIGHT=rgb("#b87a5a")),
    "Painted Blue": dict(WOOD=rgb("#5a7a9a"), WOOD_DARK=rgb("#3e566e"), WOOD_LIGHT=rgb("#7a9ab8")),
    "Painted Green": dict(WOOD=rgb("#6a8a5a"), WOOD_DARK=rgb("#4a6640"), WOOD_LIGHT=rgb("#8aa878")),
}


def in_wood(fn, wood, module=objs, **kw):
    return recolored(fn, (module, WOODS[wood]), **kw)


FURNITURE_V = {}
for wood in ("Dark", "Pale", "Red"):
    FURNITURE_V[f"Round Table ({wood})"] = in_wood(objs.round_table, wood)
    FURNITURE_V[f"Long Table ({wood})"] = in_wood(objs.long_table, wood)
    FURNITURE_V[f"Chair ({wood})"] = in_wood(objs.chair, wood)
    FURNITURE_V[f"Chest ({wood})"] = in_wood(objs.chest, wood)
    FURNITURE_V[f"Bookshelf ({wood})"] = in_wood(furn.bookshelf, wood, furn)
    FURNITURE_V[f"Bed ({wood})"] = in_wood(objs.bed, wood)
for wood in ("Painted Blue", "Painted Green"):
    FURNITURE_V[f"Chair ({wood})"] = in_wood(objs.chair, wood)
    FURNITURE_V[f"Chest ({wood})"] = in_wood(objs.chest, wood)
    FURNITURE_V[f"Stool ({wood})"] = in_wood(objs.stool, wood)
FURNITURE_V["Square Table (Dark)"] = in_wood(furn.square_table, "Dark", furn)
FURNITURE_V["Square Table (Pale)"] = in_wood(furn.square_table, "Pale", furn)
FURNITURE_V["Bench (Dark)"] = in_wood(objs.bench, "Dark")
FURNITURE_V["Desk (Dark)"] = in_wood(furn.desk, "Dark", furn)


VARIANTS = {}
for group in (TREES_V, BUSHES_V, ROCKS_V, PLANTS_V, LOGS_V, FURNITURE_V):
    VARIANTS.update(group)

VARIANTS_COLORABLE = {"Colorable Tree (Small)"} | {n for n in FURNITURE_V if n.startswith(("Long Table", "Bed"))}
