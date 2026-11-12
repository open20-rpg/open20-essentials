"""Planters and vessels (batch 5): pots with soil or plants, planter boxes,
vases and jugs. Top-down: a pot shows its rim and what's inside it."""

import math

import skia

from kit import WOOD, WOOD_DARK, dot, scallop, soft_shadow
from obj_nature import GREEN, GREEN_D, GREEN_L, blades, leaf
from objects import canopy
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, vary

TERRACOTTA = rgb("#c06a45")
STONE_POT = rgb("#a39d93")
SOIL = rgb("#5a4030")
GLAZES = {"Blue": rgb("#4f74a8"), "Green": rgb("#5f8f6a"), "Cream": rgb("#e6dcc4"), "Red": rgb("#a8483a")}


def pot(a, cx, cy, r, color=TERRACOTTA, inside=SOIL, rim=0.8, contents=None, band=None):
    """A round pot from above: its rim (with a lit and a shaded side), the
    soil or opening inside, and `contents(art)` drawn over it."""
    soft_shadow(a, (cx, cy), r, 4, 5, 0.35, 4)

    def deco(art, path):
        if band:
            art.ink(ellipse(cx, cy, r * 0.9, r * 0.9, 72), DETAIL * 1.6, closed=True, color=band, alpha=0.95)

    a.shape(ellipse(cx, cy, r, r, 80), color, depth=r * 0.12, light_k=0.4, detail=deco)
    a.shape(ellipse(cx, cy, r * rim, r * rim, 72), inside, outline=DETAIL * 1.2, depth=r * 0.15, shade_k=0, light_k=0, ao=0.6, mottle=0.08, detail=lambda art, p: [dot(art, cx + art.rng.uniform(-r * 0.6, r * 0.6), cy + art.rng.uniform(-r * 0.6, r * 0.6), art.rng.uniform(1, 2), tint(inside, 0.2), 0.7) for _ in range(int(r / 3))])
    if contents:
        contents(a)


def flower_heads(a, cx, cy, R, n, petal, center, stems=True):
    rot = a.rng.uniform(0, 6.28)
    heads = []
    for i in range(n):
        t = rot + 2 * math.pi * i / n + a.rng.uniform(-0.3, 0.3)
        d = R * a.rng.uniform(0.45, 1.0)
        heads.append((cx + d * math.cos(t), cy + d * math.sin(t), t))
    if stems:
        for x, y, t in heads:
            a.ink([(cx, cy), (x, y)], 5, color=INK, taper=False, wob=0.3)
            a.ink([(cx, cy), (x, y)], 2.8, color=shade(GREEN, 0.15), taper=False, wob=0.3)
    for x, y, t in heads:
        r = a.rng.uniform(9, 13)
        for k in range(5):
            pa = 2 * math.pi * k / 5 + a.rng.uniform(-0.1, 0.1)
            a.shape(ellipse(x + r * 0.6 * math.cos(pa), y + r * 0.6 * math.sin(pa), r * 0.55, r * 0.38, 16, rot=pa), vary(a.rng, petal, 0.05), outline=FINE * 1.1, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
        dot(a, x, y, r * 0.3, center)


# -- pots with soil / plants ---------------------------------------------------------------------


def empty_pot(seed=401, color=TERRACOTTA):
    s = 160
    a = Art(s, s, seed)
    pot(a, s / 2, s / 2, 62, color)
    return a.image()


def stone_pot(seed=402):
    return empty_pot(seed, STONE_POT)


def wooden_tub(seed=403):
    s = 180
    a = Art(s, s, seed)
    m = s / 2

    def contents(art):
        blades(art, m, m, 10, 46, [GREEN, GREEN_L], width=7)

    pot(a, m, m, 72, WOOD, rim=0.78, contents=contents)
    # Staves and an iron hoop on the rim.
    for i in range(16):
        t = 2 * math.pi * i / 16
        a.ink([(m + 58 * math.cos(t), m + 58 * math.sin(t)), (m + 71 * math.cos(t), m + 71 * math.sin(t))], DETAIL * 0.8, color=shade(WOOD, 0.5), taper=False)
    return a.image()


def flower_pot(seed=404, petal=rgb("#e6b84a"), center=rgb("#9a5a2a")):
    s = 200
    a = Art(s, s, seed)
    m = s / 2

    def contents(art):
        blades(art, m, m, 10, 40, [GREEN, GREEN_D], width=7)
        flower_heads(art, m, m, 66, 7, petal, center)

    pot(a, m, m, 60, contents=contents)
    return a.image()


def red_flower_pot(seed=405):
    return flower_pot(seed, rgb("#c8443a"), rgb("#3a2a22"))


def purple_flower_pot(seed=406):
    return flower_pot(seed, rgb("#9a6ab8"), rgb("#f2e08a"))


def fern_pot(seed=407):
    s = 240
    a = Art(s, s, seed)
    m = s / 2

    def contents(art):
        for i in range(7):
            t = 2 * math.pi * i / 7 + art.rng.uniform(-0.15, 0.15)
            L = art.rng.uniform(80, 100)
            spine = [(m + L * k / 10 * math.cos(t), m + L * k / 10 * math.sin(t)) for k in range(11)]
            for k in range(2, 10):
                x, y = spine[k]
                ln = 22 * math.sin(math.pi * k / 11) + 5
                for side in (-1, 1):
                    leaf(art, x + math.cos(t + side * 1.1) * ln * 0.5, y + math.sin(t + side * 1.1) * ln * 0.5, ln, vary(art.rng, GREEN if k % 2 else GREEN_L, 0.04), ang=t + side * 1.1, vein=False, outline=FINE)
            art.ink(spine, DETAIL * 0.7, color=GREEN_D)

    pot(a, m, m, 58, STONE_POT, contents=contents)
    return a.image()


def succulent_pot(seed=408):
    s = 170
    a = Art(s, s, seed)
    m = s / 2
    leafc = rgb("#7fae8a")

    def contents(art):
        # A rosette: rings of fat pointed leaves, inner ones lighter.
        for ring_r, n, size, col in ((40, 9, 34, shade(leafc, 0.1)), (26, 7, 26, leafc), (12, 5, 18, tint(leafc, 0.2))):
            rot = art.rng.uniform(0, 6.28)
            for k in range(n):
                t = rot + 2 * math.pi * k / n
                x, y = m + ring_r * math.cos(t), m + ring_r * math.sin(t)
                ux, uy = math.cos(t), math.sin(t)
                pts = [(x - ux * size * 0.5, y - uy * size * 0.5), (x - uy * size * 0.3, y + ux * size * 0.3), (x + ux * size * 0.5, y + uy * size * 0.5), (x + uy * size * 0.3, y - ux * size * 0.3)]
                art.shape(chaikin(pts, True, 2), col, outline=FINE * 1.2, corner=0, depth=2, shade_k=0.35, light_k=0.4, ao=0, mottle=0)

    pot(a, m, m, 60, contents=contents)
    return a.image()


def cactus_pot(seed=409):
    s = 170
    a = Art(s, s, seed)
    m = s / 2
    cactus = rgb("#5f9a5a")

    def contents(art):
        def ribs(a2, p):
            for i in range(10):
                t = 2 * math.pi * i / 10
                a2.ink([(m + 6 * math.cos(t), m + 6 * math.sin(t)), (m + 32 * math.cos(t), m + 32 * math.sin(t))], FINE * 1.1, color=shade(cactus, 0.45), alpha=0.8)
                for d in (14, 24):
                    dot(a2, m + d * math.cos(t + 0.3), m + d * math.sin(t + 0.3), 1.6, rgb("#f1e6c8"))

        art.shape(ellipse(m, m, 36, 36, 48), cactus, outline=DETAIL * 1.3, depth=6, light_k=0.45, detail=ribs)
        art.shape(scallop(m, m, 8, art.rng, 6, 0.25), rgb("#e88aa8"), outline=FINE, depth=1, mottle=0, shade_k=0, light_k=0)

    pot(a, m, m, 60, contents=contents)
    return a.image()


def tree_pot(seed=410):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    pot(a, m, m, 70, STONE_POT)
    canopy(a, m, m, 112, bumps=10, clusters=(0.7, 0.4))
    return a.image()


def herb_pot(seed=411):
    s = 190
    a = Art(s, s, seed)
    m = s / 2
    herb = rgb("#7aa65a")

    def contents(art):
        for _ in range(22):
            t, d = art.rng.uniform(0, 6.28), art.rng.uniform(0, 56)
            leaf(art, m + d * math.cos(t), m + d * math.sin(t), art.rng.uniform(16, 22), vary(art.rng, herb, 0.07), vein=False, outline=FINE)

    pot(a, m, m, 60, contents=contents)
    return a.image()


def planter_box(seed=412):
    w, h = 420, 150
    a = Art(w, h, seed)
    soft_shadow(a, rect(10, 12, w - 10, h - 10), dx=6, dy=8, alpha=0.35, blur=6)
    a.shape(rect(8, 10, w - 8, h - 10), WOOD_DARK, corner=8, depth=8)
    a.shape(rect(24, 26, w - 24, h - 26), SOIL, outline=DETAIL * 1.2, corner=4, depth=10, shade_k=0, light_k=0, ao=0.6, mottle=0.08)
    for x in range(70, w - 40, 80):
        blades(a, x, h / 2, 8, 36, [GREEN, GREEN_D], width=7)
        flower_heads(a, x, h / 2, 34, 4, a.rng.choice([rgb("#e6b84a"), rgb("#c8443a"), rgb("#f3eee2"), rgb("#9a6ab8")]), rgb("#9a5a2a"))
    return a.image()


def stacked_pots(seed=413):
    w, h = 260, 200
    a = Art(w, h, seed)
    # Pots nested upside down: concentric rims seen from above (bottoms up).
    for cx, cy in ((80, 110), (180, 90)):
        soft_shadow(a, (cx, cy), 62, 6, 8, 0.35, 6)
        a.shape(ellipse(cx, cy, 62, 62, 64), TERRACOTTA, depth=8, light_k=0.4)
        a.shape(ellipse(cx, cy, 40, 40, 48), tint(TERRACOTTA, 0.1), outline=DETAIL * 1.1, depth=4, light_k=0.4)
        a.shape(ellipse(cx, cy, 9, 9, 16), shade(TERRACOTTA, 0.5), outline=FINE * 1.2, depth=2, shade_k=0, light_k=0, mottle=0)
    return a.image()


def broken_pot(seed=414):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    # Soil spilled, shards around.
    a.shape(blob(m, m + 6, 70, a.rng, 11, 0.25), SOIL, outline=DETAIL, smooth=True, depth=6, shade_k=0.3, light_k=0.2, ao=0, mottle=0.1)
    for _ in range(6):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(30, 80)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        r = a.rng.uniform(14, 24)
        a0 = a.rng.uniform(0, 6.28)
        shard = [(x + r * math.cos(a0 + k * 0.5), y + r * math.sin(a0 + k * 0.5)) for k in range(4)] + [(x + r * 0.6 * math.cos(a0 + 1.5 - k * 0.5), y + r * 0.6 * math.sin(a0 + 1.5 - k * 0.5)) for k in range(4)]
        soft_shadow(a, shard, dx=3, dy=4)
        a.shape(shard, vary(a.rng, TERRACOTTA, 0.06), outline=DETAIL, corner=2, depth=3, light_k=0.4, mottle=0)
    blades(a, m - 10, m, 7, 40, [GREEN, GREEN_L], width=7)
    return a.image()


# -- vases & jugs --------------------------------------------------------------------------------


def vase(seed=420, color=GLAZES["Blue"], band=None, opening=0.32):
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    pot(a, m, m, 56, color, inside=rgb("#2a221e"), rim=opening, band=band)
    # A glint on the glaze.
    a.ink([(m - 34, m - 18), (m - 22, m - 34)], FINE * 2, color=(250, 248, 240), alpha=0.8)
    return a.image()


def flower_vase(seed=421):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    pot(a, m, m, 46, GLAZES["Cream"], inside=rgb("#2a221e"), rim=0.36)
    flower_heads(a, m, m, 74, 7, rgb("#e88aa8"), rgb("#f6d24a"))
    for _ in range(4):
        t = a.rng.uniform(0, 6.28)
        leaf(a, m + 40 * math.cos(t), m + 40 * math.sin(t), 26, vary(a.rng, GREEN, 0.05), ang=t)
    return a.image()


def lidded_jar(seed=422):
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 56, 6, 8, 0.35, 6)
    a.shape(ellipse(m, m, 56, 56, 64), GLAZES["Green"], depth=8, light_k=0.45, detail=lambda art, p: art.ink(ellipse(m, m, 50, 50, 64), DETAIL * 1.4, closed=True, color=rgb("#d8c07a"), alpha=0.95))
    a.shape(ellipse(m, m, 32, 32, 48), tint(GLAZES["Green"], 0.12), outline=DETAIL * 1.2, depth=5, light_k=0.45)
    a.shape(ellipse(m, m, 10, 10, 20), rgb("#d8c07a"), outline=DETAIL, depth=3, mottle=0)
    return a.image()


def jug(seed=423):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    clay = rgb("#b98a5a")
    # The handle (a loop) on the right and a pouring lip on the left.
    a.ink(chaikin([(m + 40, m - 22), (m + 70, m - 18), (m + 72, m + 18), (m + 40, m + 22)], False, 2), DETAIL * 3.2, color=INK)
    a.ink(chaikin([(m + 40, m - 22), (m + 70, m - 18), (m + 72, m + 18), (m + 40, m + 22)], False, 2), DETAIL * 2, color=clay)
    pot(a, m, m, 50, clay, inside=rgb("#2a221e"), rim=0.42)
    a.shape([(m - 52, m - 8), (m - 66, m), (m - 52, m + 8)], clay, outline=DETAIL, corner=2, depth=2, mottle=0)
    return a.image()


def water_jug(seed=424):
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    pot(a, m, m, 54, rgb("#c9a27a"), inside=rgb("#6aa0b6"), rim=0.4, band=rgb("#7a4a2a"))
    a.ink([(m - 8, m - 6), (m + 6, m - 9)], FINE * 1.3, color=rgb("#e4f2f6"), alpha=0.9)
    return a.image()


POTS = {
    "Terracotta Pot": empty_pot,
    "Stone Pot": stone_pot,
    "Wooden Tub": wooden_tub,
    "Yellow Flower Pot": flower_pot,
    "Red Flower Pot": red_flower_pot,
    "Purple Flower Pot": purple_flower_pot,
    "Fern Pot": fern_pot,
    "Succulent Pot": succulent_pot,
    "Cactus Pot": cactus_pot,
    "Potted Tree": tree_pot,
    "Herb Pot": herb_pot,
    "Planter Box": planter_box,
    "Stacked Pots": stacked_pots,
    "Broken Pot": broken_pot,
    "Blue Vase": lambda: vase(420, GLAZES["Blue"]),
    "Green Vase": lambda: vase(425, GLAZES["Green"], band=rgb("#d8c07a")),
    "Cream Vase": lambda: vase(426, GLAZES["Cream"], band=rgb("#4f74a8")),
    "Red Vase": lambda: vase(427, GLAZES["Red"], band=rgb("#1f1814")),
    "Flower Vase": flower_vase,
    "Lidded Jar": lidded_jar,
    "Jug": jug,
    "Water Jug": water_jug,
}
