"""Caves & underground, ruins & debris, and lighting (batch 13).
Top-down, same pen style (red g==b = colorable)."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, dot, scallop, soft_shadow
from obj_craft import handle, pickaxe_at, rot_pts, shovel_at
from obj_dungeon import BLOOD, chain
from obj_magic import BONE, WAX, candle, crystal, glow, skull_at
from obj_nature import GREEN, GREEN_D, leaf, pebble, tube
from obj_stone import DARK_STONE, GREY, LIGHT_STONE, MARBLE, MOSS, crack, stone_block
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

CAVE_ROCK = rgb("#8a847c")
CAVE_DARK = rgb("#4a4440")
WATER = rgb("#5f8ea4")
FOAM = rgb("#dceff5")
ASH = rgb("#9a948c")
SOOT = rgb("#2e2a28")
ROPE = rgb("#c9b088")
FIRE = (rgb("#e5652e"), rgb("#f4a23a"), rgb("#fde07a"))
GREEN_FIRE = (rgb("#3f9a4a"), rgb("#7fd36a"), rgb("#d6f7b0"))
BLUE_FIRE = (rgb("#3f7ad0"), rgb("#6fb0f0"), rgb("#dff1ff"))
PURPLE_FIRE = (rgb("#7a4ac8"), rgb("#b08af0"), rgb("#f0e2ff"))
GEMS = {"Purple": rgb("#8a6ad8"), "Blue": rgb("#5f9ad8"), "Green": rgb("#5fb87a"), "Red": rgb("#d0505a"), "Amber": rgb("#e0a040"), "White": rgb("#dfe6ea")}


def fire(a, x, y, r, palette=FIRE, glow_r=None):
    """Flames seen from above: three nested flickering blobs and a halo."""
    glow(a, x, y, glow_r or r * 2.4, palette[1], 0.4)
    for k, (f, col) in enumerate(((1.0, palette[0]), (0.66, palette[1]), (0.34, palette[2]))):
        a.shape(scallop(x - k * r * 0.06, y - k * r * 0.06, r * f, a.rng, 7, 0.24), col, outline=DETAIL * 0.9 if k == 0 else 0, depth=2, shade_k=0.2, light_k=0, ao=0, mottle=0)


# -- cave: stalagmites ------------------------------------------------------------------------------


def cone(a, x, y, r, color=CAVE_ROCK):
    """A stalagmite seen from above: round base rising to a tip near the
    centre (shifted a little toward the light), facet lines to the tip."""
    base = blob(x, y, r, a.rng, 9, 0.12)
    soft_shadow(a, base, dx=r * 0.18, dy=r * 0.22, alpha=0.35, blur=r * 0.12)
    tx, ty = x - r * 0.12, y - r * 0.12

    def facets(art, p):
        for (bx, by) in base:
            art.ink([(bx, by), (tx, ty)], FINE * 1.1, color=shade(color, 0.45), alpha=0.6, wob=0.2)
        g = skia.Path()
        g.addCircle(tx, ty, r * 0.45)
        art.fill_path(g, tint(color, 0.35), 0.6, blur=r * 0.25)

    a.shape(base, color, outline=DETAIL * (1.6 if r > 30 else 1.2), smooth=True, depth=r * 0.2, shade_k=0.55, light_k=0.4, detail=facets)
    dot(a, tx, ty, max(2, r * 0.08), tint(color, 0.5))


def stalagmite(seed=1301):
    s = 200
    a = Art(s, s, seed)
    cone(a, s / 2, s / 2, 70)
    return a.image()


def stalagmite_cluster(seed=1302):
    s = 320
    a = Art(s, s, seed)
    spots = [(160, 150, 70), (90, 110, 42), (230, 100, 36), (220, 220, 48), (100, 220, 32), (160, 250, 24)]
    for x, y, r in sorted(spots, key=lambda p: p[2]):
        cone(a, x, y, r, vary(a.rng, CAVE_ROCK, 0.06))
    return a.image()


def small_stalagmites(seed=1303):
    s = 220
    a = Art(s, s, seed)
    for _ in range(7):
        cone(a, a.rng.uniform(40, 180), a.rng.uniform(40, 180), a.rng.uniform(14, 26), vary(a.rng, CAVE_ROCK, 0.08))
    return a.image()


def broken_stalagmite(seed=1304):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    base = blob(m, m, 66, a.rng, 9, 0.12)
    soft_shadow(a, base, dx=10, dy=12)
    stone_block(a, base, CAVE_ROCK, smooth=True, cracks=0, depth=10)
    a.shape(blob(m - 4, m - 4, 40, a.rng, 9, 0.2), tint(CAVE_ROCK, 0.18), outline=DETAIL * 1.2, smooth=True, depth=4, shade_k=0.3, light_k=0.2)  # the snapped-off face
    for _ in range(5):
        pebble(a, m + a.rng.uniform(-90, 90), m + a.rng.uniform(70, 96), a.rng.uniform(6, 12), CAVE_ROCK)
    return a.image()


def crystal_formation(color, seed=1305):
    def make():
        s = 260
        a = Art(s, s, seed)
        m = s / 2
        glow(a, m, m, 110, color, 0.35)
        stone_block(a, blob(m, m + 10, 80, a.rng, 10, 0.12, ry=60), CAVE_DARK, smooth=True, cracks=0)
        pts = [(m + a.rng.uniform(-60, 60), m + a.rng.uniform(-40, 50), a.rng.uniform(16, 40)) for _ in range(8)]
        for x, y, r in sorted(pts, key=lambda p: p[2]):
            crystal(a, x, y, r, vary(a.rng, color, 0.06), a.rng.uniform(0, 1))
        return a.image()

    return make


# -- cave: mushrooms --------------------------------------------------------------------------------


def big_cap(a, x, y, r, color, spots=True, glows=False):
    if glows:
        glow(a, x, y, r * 1.8, color, 0.4)
    soft_shadow(a, (x, y), r, r * 0.15, r * 0.2, 0.4, r * 0.12)

    def detail(art, p):
        art.ink(ellipse(x, y, r * 0.55, r * 0.55, 40), FINE * 1.2, closed=True, color=shade(color, 0.35), alpha=0.6)
        if spots:
            for _ in range(int(r / 6)):
                t, d = art.rng.uniform(0, 6.28), art.rng.uniform(0, r * 0.8)
                art.shape(ellipse(x + d * math.cos(t), y + d * math.sin(t), r * 0.09, r * 0.08, 16), tint(color, 0.7), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)

    a.shape(scallop(x, y, r, a.rng, 10, 0.04), color, outline=OUTLINE * (1 if r > 40 else 0.7), corner=0, depth=r * 0.18, light_k=0.5, detail=detail)


def giant_mushroom(color, spots=True, glows=False, seed=1311):
    def make():
        s = 300
        a = Art(s, s, seed)
        big_cap(a, s / 2, s / 2, 110, color, spots, glows)
        return a.image()

    return make


def mushroom_cluster(seed=1316):
    s = 320
    a = Art(s, s, seed)
    caps = [(110, 120, 70, rgb("#b84a3a")), (220, 110, 50, rgb("#a8845a")), (200, 220, 60, rgb("#b84a3a")), (100, 230, 34, rgb("#a8845a")), (250, 260, 26, rgb("#b84a3a"))]
    for x, y, r, c in sorted(caps, key=lambda p: p[2]):
        big_cap(a, x, y, r, c, spots=c == rgb("#b84a3a"))
    return a.image()


# -- cave: water, holes, rocks --------------------------------------------------------------------


def pool(a, cx, cy, rx, ry, water=WATER, glows=False):
    rim = blob(cx, cy, rx + 22, a.rng, 14, 0.12, ry=ry + 22)
    stone_block(a, rim, CAVE_ROCK, smooth=True, cracks=1, depth=10)
    if glows:
        glow(a, cx, cy, rx * 1.1, water, 0.4)

    def ripples(art, p):
        for f in (0.4, 0.7):
            t0 = art.rng.uniform(0, 6.28)
            art.ink([(cx + rx * f * math.cos(t0 + j * 0.08), cy + ry * f * math.sin(t0 + j * 0.08)) for j in range(10)], FINE * 1.3, color=tint(water, 0.6), alpha=0.85)

    a.shape(blob(cx, cy, rx, a.rng, 12, 0.12, ry=ry), water, outline=DETAIL * 1.3, smooth=True, depth=ry * 0.25, shade_k=0, light_k=0.2 if glows else 0, ao=0.6, detail=ripples)


def cave_pool(seed=1321):
    w, h = 360, 280
    a = Art(w, h, seed)
    pool(a, w / 2, h / 2, 140, 100)
    return a.image()


def small_cave_pool(seed=1322):
    s = 220
    a = Art(s, s, seed)
    pool(a, s / 2, s / 2, 70, 56)
    return a.image()


def glowing_pool(seed=1323):
    w, h = 340, 280
    a = Art(w, h, seed)
    pool(a, w / 2, h / 2, 124, 92, rgb("#4fc2c0"), glows=True)
    return a.image()


def hole(a, cx, cy, rx, ry, rim_stones=True):
    if rim_stones:
        for k in range(16):
            t = 2 * math.pi * k / 16
            pebble(a, cx + (rx + 12) * math.cos(t), cy + (ry + 12) * math.sin(t), a.rng.uniform(9, 16), CAVE_ROCK, outline=DETAIL * 1.2)
    pts = blob(cx, cy, rx, a.rng, 12, 0.1, ry=ry)
    a.shape(pts, rgb("#1a1614"), outline=DETAIL * 1.4, smooth=True, depth=ry * 0.4, shade_k=0, light_k=0, ao=0.8)
    # The far wall's lit lip (bottom edge seen from above).
    with a.clip(to_path(chaikin(pts, True, 2))):
        g = skia.Path()
        g.addOval(skia.Rect.MakeXYWH(cx - rx, cy + ry * 0.35, rx * 2, ry))
        a.fill_path(g, CAVE_DARK, 0.9, blur=ry * 0.25)


def cave_hole(seed=1331):
    s = 240
    a = Art(s, s, seed)
    hole(a, s / 2, s / 2, 80, 70)
    return a.image()


def deep_pit(seed=1332):
    w, h = 380, 320
    a = Art(w, h, seed)
    hole(a, w / 2, h / 2, 150, 120)
    return a.image()


def rope_ladder_hole(seed=1333):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    hole(a, m, m + 10, 86, 74)
    # Stakes at the rim, the ladder going down into the dark (fading).
    for x in (m - 26, m + 26):
        a.shape(ellipse(x, m - 70, 9, 9, 16), WOOD_DARK, outline=DETAIL * 1.2, depth=2, mottle=0)
        a.ink([(x, m - 70), (x, m + 30)], DETAIL * 1.4, color=ROPE)
    for k, y in enumerate(range(int(m - 54), int(m + 30), 16)):
        a.ink([(m - 26, y), (m + 26, y)], DETAIL * 2.2, color=mix(WOOD, rgb("#1a1614"), k / 7))
    return a.image()


def rock_formation(seed=1334, big=False):
    s = 360 if big else 260
    a = Art(s, s, seed)
    m = s / 2
    n = 6 if big else 4
    spots = [(m + a.rng.uniform(-s * 0.22, s * 0.22), m + a.rng.uniform(-s * 0.2, s * 0.2), a.rng.uniform(s * 0.12, s * 0.22)) for _ in range(n)]
    for x, y, r in sorted(spots, key=lambda p: p[1]):
        pts = blob(x, y, r, a.rng, 8, 0.2)
        soft_shadow(a, pts, dx=8, dy=10, alpha=0.35, blur=6)
        p = stone_block(a, pts, vary(a.rng, CAVE_ROCK, 0.08), smooth=True, cracks=1, light_k=0.45, depth=r * 0.2)
    return a.image()


def stream_rocks(seed=1336):
    w, h = 400, 220
    a = Art(w, h, seed)
    band = [(0 + x, h / 2 - 50 + 16 * math.sin(x / 60)) for x in range(10, w - 9, 20)] + [(x, h / 2 + 50 + 16 * math.sin(x / 50 + 1)) for x in range(w - 10, 9, -20)]

    def flow(art, p):
        for k in range(6):
            y = h / 2 - 30 + k * 12
            x0 = art.rng.uniform(20, 120)
            art.ink([(x, y + 6 * math.sin(x / 40 + k)) for x in range(int(x0), int(x0 + 120), 10)], FINE * 1.2, color=FOAM, alpha=0.8)

    a.shape(band, WATER, outline=DETAIL * 1.2, corner=0, depth=6, shade_k=0, light_k=0, ao=0.5, detail=flow)
    for _ in range(9):
        pebble(a, a.rng.uniform(30, w - 30), h / 2 + a.rng.uniform(-50, 50), a.rng.uniform(12, 24), CAVE_ROCK, outline=DETAIL * 1.3)
    return a.image()


# -- cave: mining ---------------------------------------------------------------------------------


def rails(a, pts, gauge=60):
    """Mine rails along a polyline: ties across, two iron rails."""
    from pen import normals, resample

    p = resample(pts, False, 4)
    ns = normals(p, False)
    for i in range(0, len(p), 9):
        (x, y), (nx, ny) = p[i], ns[i]
        tie = [(x + nx * gauge * 0.8 - ny * 7, y + ny * gauge * 0.8 + nx * 7), (x + nx * gauge * 0.8 + ny * 7, y + ny * gauge * 0.8 - nx * 7), (x - nx * gauge * 0.8 + ny * 7, y - ny * gauge * 0.8 - nx * 7), (x - nx * gauge * 0.8 - ny * 7, y - ny * gauge * 0.8 + nx * 7)]
        a.shape(tie, vary(a.rng, WOOD, 0.06), outline=DETAIL * 1.2, corner=2, depth=2)
    for s in (-1, 1):
        line = [(x + nx * gauge / 2 * s, y + ny * gauge / 2 * s) for (x, y), (nx, ny) in zip(p, ns)]
        a.ink(line, 11, color=INK, taper=False, wob=0, var=0.04)
        a.ink(line, 6, color=IRON, taper=False, wob=0, var=0.04)
        a.ink(line, 2, color=tint(IRON, 0.5), taper=False, wob=0, var=0.04)


def rail_straight(seed=1341):
    w, h = 120, 512
    a = Art(w, h, seed)
    rails(a, [(w / 2, 4), (w / 2, h - 4)])
    return a.image()


def rail_curve(seed=1342):
    s = 512
    a = Art(s, s, seed)
    R = s - 70
    # A quarter circle from the bottom edge to the right edge, centred on the
    # top-left corner region so both ends meet the tile edges squarely.
    cx, cy = s - 4 - R, 4 + 0
    pts = [(s - 4 - R + R * math.sin(t), 4 + R * math.cos(t)) for t in [k / 40 * math.pi / 2 for k in range(41)]]
    pts = [(x, y + (s - 8 - R)) for x, y in pts]
    rails(a, pts)
    return a.image()


def rail_end(seed=1343):
    w, h = 140, 300
    a = Art(w, h, seed)
    rails(a, [(w / 2, h - 4), (w / 2, 60)])
    a.shape(rect(14, 30, w - 14, 70), WOOD_DARK, outline=OUTLINE * 0.8, corner=4, depth=6)
    for x in (34, w - 34):
        a.shape(rect(x - 12, 18, x + 12, 34), IRON, outline=DETAIL * 1.2, corner=3, depth=2, mottle=0)
    return a.image()


def minecart(fill=None, seed=1344):
    def make():
        w, h = 200, 240
        a = Art(w, h, seed)
        for x in (24, w - 24):
            for y in (60, h - 60):
                a.shape(rect(x - 9, y - 26, x + 9, y + 26), rgb("#3a3a40"), outline=DETAIL * 1.4, corner=6, depth=2, mottle=0)
        a.shape(rect(30, 20, w - 30, h - 20), rgb("#6a6e76"), corner=10, depth=10, light_k=0.4)
        for y in (60, h - 60):
            a.ink([(30, y), (w - 30, y)], DETAIL * 1.6, color=rgb("#4a4c52"), taper=False)
        inside = rect(46, 36, w - 46, h - 36)

        def load(art, p):
            if fill:
                for _ in range(26):
                    x, y = art.rng.uniform(52, w - 52), art.rng.uniform(42, h - 42)
                    art.shape(blob(x, y, art.rng.uniform(9, 15), art.rng, 7, 0.25), vary(art.rng, fill, 0.1), outline=FINE * 1.3, depth=2, shade_k=0.3, light_k=0.5, ao=0, mottle=0)

        a.shape(inside, rgb("#3a3a40"), outline=DETAIL * 1.2, corner=6, depth=10, shade_k=0, light_k=0, ao=0.6, detail=load)
        for x, y in ((40, 30), (w - 40, 30), (40, h - 30), (w - 40, h - 30)):
            dot(a, x, y, 3.5, tint(IRON, 0.4))
        return a.image()

    return make


def support_frame(seed=1347):
    w, h = 420, 140
    a = Art(w, h, seed)
    for x in (40, w - 40):
        a.shape(rect(x - 26, h / 2 - 26, x + 26, h / 2 + 26), WOOD_DARK, outline=OUTLINE * 0.85, corner=4, depth=6)
        a.ink(ellipse(x, h / 2, 12, 12, 20), FINE * 1.2, closed=True, color=shade(WOOD_DARK, 0.5))
    a.shape(rect(10, h / 2 - 20, w - 10, h / 2 + 20), WOOD, corner=5, depth=8, light_k=0.4, detail=lambda art, p: boards(art, 10, h / 2 - 20, w - 10, h / 2 + 20, WOOD, 1))
    for x in (90, w - 90):
        a.shape([(x - 30, h / 2 + 16), (x + 30, h / 2 + 16), (x, h / 2 + 46)], WOOD, outline=DETAIL * 1.2, corner=2, depth=3)
    return a.image()


def timber_props(seed=1348):
    w, h = 360, 220
    a = Art(w, h, seed)
    for k in range(5):
        y = 40 + k * 34 + a.rng.uniform(-4, 4)
        x0, x1 = 20 + a.rng.uniform(0, 30), w - 20 - a.rng.uniform(0, 30)
        a.shape(rect(x0, y - 15, x1, y + 15), vary(a.rng, WOOD, 0.06), outline=DETAIL * 1.3, corner=4, depth=3, detail=lambda art, p, y=y, x0=x0, x1=x1: boards(art, x0, y - 15, x1, y + 15, WOOD, 1))
    return a.image()


def mining_tools(seed=1349):
    s = 260
    a = Art(s, s, seed)
    pickaxe_at(a, 40, 200, -0.7, 150)
    shovel_at(a, 30, 120, 0.15, 120)
    a.shape(ellipse(200, 210, 32, 26, 32), rgb("#6a6e76"), outline=DETAIL * 1.4, depth=4, light_k=0.4)  # bucket
    a.shape(ellipse(200, 210, 22, 17, 28), rgb("#3a3a40"), outline=DETAIL, depth=4, shade_k=0, light_k=0, ao=0.5)
    return a.image()


def ore_pile(color, seed=1350):
    def make():
        s = 240
        a = Art(s, s, seed)
        m = s / 2
        a.shape(blob(m, m, 90, a.rng, 11, 0.14), CAVE_ROCK, outline=DETAIL, smooth=True, depth=10, shade_k=0.4, light_k=0.3, ao=0.2)
        spots = []
        for _ in range(60):
            t, d = a.rng.uniform(0, 6.28), 86 * math.sqrt(a.rng.random())
            spots.append((m + d * math.cos(t), m + d * math.sin(t), 1 - d / 86))
        for x, y, hh in sorted(spots, key=lambda p: p[2]):
            rock_c = mix(shade(CAVE_ROCK, 0.08), tint(CAVE_ROCK, 0.22), hh)
            a.shape(blob(x, y, a.rng.uniform(7, 13), a.rng, 7, 0.25), rock_c, outline=FINE * 1.3, depth=2, shade_k=0.3, light_k=0.4, ao=0, mottle=0)
            if a.rng.random() < 0.45:
                a.shape(blob(x + 2, y - 2, a.rng.uniform(4, 7), a.rng, 6, 0.2), color, outline=FINE * 1.2, depth=1, shade_k=0.2, light_k=0.7, ao=0, mottle=0)
        return a.image()

    return make


def gem_pile(seed=1354):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    for _ in range(14):
        t, d = a.rng.uniform(0, 6.28), 70 * math.sqrt(a.rng.random())
        crystal(a, m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(9, 16), a.rng.choice(list(GEMS.values())), a.rng.uniform(0, 1))
    return a.image()


def hook_lantern(seed=1355):
    w, h = 180, 200
    a = Art(w, h, seed)
    a.shape(rect(6, 4, w - 6, 28), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)  # rock wall edge
    a.ink([(w / 2, 26), (w / 2, 60)], DETAIL * 2.4, color=IRON)
    glow(a, w / 2, 110, 80, rgb("#ffd27a"), 0.45)
    a.shape(rect(w / 2 - 30, 80, w / 2 + 30, 140), IRON, corner=8, depth=5)
    a.shape(rect(w / 2 - 20, 90, w / 2 + 20, 130), rgb("#ffe39a"), outline=DETAIL, corner=4, depth=3, shade_k=0, light_k=0.4)
    a.ink([(w / 2 - 20, 110), (w / 2 + 20, 110)], DETAIL, color=IRON, taper=False)
    return a.image()


# -- cave: creatures & remains ----------------------------------------------------------------------


def bat(a, x, y, s, ang):
    """A bat from above, wings spread: scalloped trailing edges, the body
    and ears in the middle."""
    half = [(0.08, -0.22), (0.3, -0.42), (0.62, -0.4), (1.0, -0.12), (0.84, 0.02), (0.74, 0.18), (0.58, 0.08), (0.46, 0.26), (0.3, 0.14), (0.14, 0.28)]
    pts = half + [(-px, py) for px, py in reversed(half)]
    pts = rot_pts([(x + px * s, y + py * s) for px, py in pts], x, y, ang)
    soft_shadow(a, pts, dx=3, dy=4, alpha=0.3, blur=3)
    a.shape(pts, rgb("#3a3036"), outline=DETAIL * 1.1, corner=0, wob=0.2, depth=2, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    for side in (-1, 1):
        a.ink(rot_pts([(x + side * 0.1 * s, y - 0.1 * s), (x + side * 0.62 * s, y - 0.36 * s)], x, y, ang), FINE, color=rgb("#5a4e56"), alpha=0.9)
    body = rot_pts(ellipse(x, y, s * 0.13, s * 0.28, 20), x, y, ang)
    a.shape(body, rgb("#5a4a50"), outline=FINE * 1.3, corner=0, depth=1, light_k=0.4, mottle=0)
    for side in (-1, 1):
        a.shape(rot_pts([(x + side * 0.03 * s, y - 0.24 * s), (x + side * 0.12 * s, y - 0.4 * s), (x + side * 0.12 * s, y - 0.22 * s)], x, y, ang), rgb("#5a4a50"), outline=FINE, corner=0, depth=1, mottle=0)


def bat_roost(seed=1361):
    s = 280
    a = Art(s, s, seed)
    for _ in range(6):
        bat(a, a.rng.uniform(60, s - 60), a.rng.uniform(60, s - 60), a.rng.uniform(34, 48), a.rng.uniform(-0.6, 0.6))
    return a.image()


def spider_web(seed=1362):
    s = 360
    a = Art(s, s, seed)
    m = s / 2
    col = rgb("#e8e4dc")
    spokes = [2 * math.pi * k / 12 + a.rng.uniform(-0.05, 0.05) for k in range(12)]
    for t in spokes:
        pts = [(m, m), (m + 160 * math.cos(t), m + 160 * math.sin(t))]
        a.ink(pts, FINE * 2.6, color=INK, alpha=0.7, wob=0.2)
        a.ink(pts, FINE * 1.3, color=col, alpha=0.95, wob=0.2)
    for r in range(18, 160, 16):
        ring_pts = []
        for t in spokes + [spokes[0]]:
            ring_pts.append((m + r * math.cos(t), m + r * math.sin(t)))
        for p0, p1 in zip(ring_pts, ring_pts[1:]):
            mid = ((p0[0] + p1[0]) / 2 * 0.96 + m * 0.04, (p0[1] + p1[1]) / 2 * 0.96 + m * 0.04)
            a.ink(chaikin([p0, mid, p1], False, 2), FINE * 2.2, color=INK, alpha=0.5, wob=0.1)
            a.ink(chaikin([p0, mid, p1], False, 2), FINE * 1.0, color=col, alpha=0.95, wob=0.1)
    return a.image(grain=0)


def egg_clutch(seed=1363):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    nest = scallop(m, m, 96, a.rng, 14, 0.08)
    a.shape(nest, rgb("#8a7a5a"), depth=10, light_k=0.3, detail=lambda art, p: [art.ink([(m + r * math.cos(t), m + r * math.sin(t)), (m + (r + 14) * math.cos(t + 0.4), m + (r + 14) * math.sin(t + 0.4))], FINE * 1.2, color=shade(rgb("#8a7a5a"), 0.5), alpha=0.8) for r in (60, 74) for t in [2 * math.pi * k / 18 for k in range(18)]])
    a.shape(ellipse(m, m, 58, 58, 48), rgb("#4a3e30"), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.5)
    for x, y in ((m - 20, m - 14), (m + 18, m - 16), (m, m + 18), (m - 26, m + 18), (m + 26, m + 14)):
        soft_shadow(a, (x, y), 18, 3, 4)
        a.shape(ellipse(x, y, 18, 22, 28, rot=a.rng.uniform(0, 3)), rgb("#e6e0c8"), outline=DETAIL, depth=3, light_k=0.5, mottle=0, detail=lambda art, p, x=x, y=y: [dot(art, x + art.rng.uniform(-10, 10), y + art.rng.uniform(-12, 12), 2.4, rgb("#9a8a6a")) for _ in range(5)])
    return a.image()


def cave_bones(seed=1364):
    s = 260
    a = Art(s, s, seed)

    def bone(x, y, L, ang):
        ux, uy = math.cos(ang), math.sin(ang)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 15, color=INK, taper=False)
        a.ink([(x - ux * L / 2, y - uy * L / 2), (x + ux * L / 2, y + uy * L / 2)], 9, color=BONE, taper=False)
        for e in (-1, 1):
            a.shape(ellipse(x + ux * e * L / 2, y + uy * e * L / 2, 9, 9, 16), BONE, outline=DETAIL, depth=2, mottle=0)

    for _ in range(6):
        bone(a.rng.uniform(60, 200), a.rng.uniform(60, 200), a.rng.uniform(60, 100), a.rng.uniform(0, 3.14))
    skull_at(a, 180, 80, 0.9)
    pebble(a, 60, 200, 14, CAVE_ROCK)
    return a.image()


def glowing_moss(color, seed=1365):
    def make():
        s = 260
        a = Art(s, s, seed)
        m = s / 2
        glow(a, m, m, 110, color, 0.35)
        for _ in range(9):
            a.shape(blob(m + a.rng.uniform(-60, 60), m + a.rng.uniform(-60, 60), a.rng.uniform(18, 34), a.rng, 10, 0.3), vary(a.rng, color, 0.08), outline=FINE * 1.3, smooth=True, depth=2, shade_k=0.3, light_k=0.5, ao=0, mottle=0.1)
        for _ in range(40):
            dot(a, m + a.rng.uniform(-80, 80), m + a.rng.uniform(-80, 80), a.rng.uniform(1.5, 3), tint(color, 0.6))
        return a.image()

    return make


def root_tangle(seed=1366):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    root = rgb("#6d5040")
    for _ in range(7):
        t = a.rng.uniform(0, 6.28)
        pts = [(m + 20 * math.cos(t), m + 20 * math.sin(t))]
        ang = t
        for k in range(8):
            ang += a.rng.uniform(-0.4, 0.4)
            px, py = pts[-1]
            pts.append((px + 16 * math.cos(ang), py + 16 * math.sin(ang)))
        poly = tube(chaikin(pts, False, 2), 18, 3)
        a.shape(poly, vary(a.rng, root, 0.06), outline=DETAIL * 1.1, corner=0, wob=0.1, depth=2, mottle=0, var=0.08)
    hole(a, m, m, 26, 22, rim_stones=False)
    return a.image()


def ceiling_roots(seed=1367):
    s = 260
    a = Art(s, s, seed)
    root = rgb("#6d5040")
    # Roots dangling from above: seen as curled ends and short strands.
    for _ in range(14):
        x, y = a.rng.uniform(40, s - 40), a.rng.uniform(40, s - 40)
        pts = [(x, y)]
        ang = a.rng.uniform(0, 6.28)
        for k in range(5):
            ang += a.rng.uniform(-0.8, 0.8)
            px, py = pts[-1]
            pts.append((px + 10 * math.cos(ang), py + 10 * math.sin(ang)))
        a.ink(chaikin(pts, False, 2), 13, color=INK, taper=True)
        a.ink(chaikin(pts, False, 2), 8, color=root, taper=True)
    return a.image()


# -- ruins & debris -------------------------------------------------------------------------------


def wall_chunk(seed=1401, big=False):
    w, h = (440, 240) if big else (300, 180)
    a = Art(w, h, seed)
    brick = rgb("#a39d93")
    rows = 4 if big else 3
    rh = (h - 60) / rows
    for r in range(rows):
        x = 30 + (rh * 0.6 if r % 2 else 0)
        lim = w - 30 - r * (40 if big else 30) - a.rng.uniform(0, 30)
        while x < lim:
            bw = a.rng.uniform(rh * 1.2, rh * 1.8)
            stone_block(a, rect(x + 2, 30 + r * rh + 2, min(lim, x + bw) - 2, 30 + (r + 1) * rh - 2), vary(a.rng, brick, 0.06), outline=DETAIL * 1.3, corner=4, cracks=0)
            x += bw
    for _ in range(10 if big else 6):
        pebble(a, a.rng.uniform(w * 0.5, w - 20), a.rng.uniform(20, h - 20), a.rng.uniform(8, 16), brick, outline=DETAIL * 1.2)
    return a.image()


def beam_at(a, x0, y0, x1, y1, wd=34, color=WOOD):
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    pts = [(x0, y0 - wd / 2), (x0 + L, y0 - wd / 2), (x0 + L - 8, y0 - wd / 6), (x0 + L + 4, y0), (x0 + L - 10, y0 + wd / 4), (x0 + L, y0 + wd / 2), (x0, y0 + wd / 2)]
    pts = rot_pts(pts, x0, y0, ang)
    soft_shadow(a, pts, dx=6, dy=8)
    a.shape(pts, color, outline=DETAIL * 1.6, corner=2, depth=4, light_k=0.4, detail=lambda art, p: [art.ink(rot_pts([(x0 + 10, y0 + o), (x0 + L - 20, y0 + o)], x0, y0, ang), FINE * 1.1, color=shade(color, 0.5), alpha=0.7) for o in (-wd * 0.25, wd * 0.15)])


def fallen_beam(seed=1403):
    w, h = 460, 140
    a = Art(w, h, seed)
    beam_at(a, 20, h / 2 + 10, w - 30, h / 2 - 10)
    return a.image()


def crossed_beams(seed=1404):
    s = 400
    a = Art(s, s, seed)
    beam_at(a, 30, 90, 370, 300)
    beam_at(a, 50, 320, 360, 70, 30, WOOD_DARK)
    return a.image()


def debris_pile(seed=1405, small=False):
    s = 220 if small else 320
    a = Art(s, s, seed)
    m = s / 2
    n = 6 if small else 12
    for _ in range(n):
        x, y = m + a.rng.uniform(-s * 0.25, s * 0.25), m + a.rng.uniform(-s * 0.25, s * 0.25)
        L, ang = a.rng.uniform(s * 0.2, s * 0.4), a.rng.uniform(0, 3.14)
        ux, uy = math.cos(ang), math.sin(ang)
        wd = a.rng.uniform(14, 22)
        pts = [(x - ux * L / 2 - uy * wd / 2, y - uy * L / 2 + ux * wd / 2), (x + ux * L / 2 - uy * wd / 2, y + uy * L / 2 + ux * wd / 2), (x + ux * L / 2 + uy * wd / 2, y + uy * L / 2 - ux * wd / 2), (x - ux * L / 2 + uy * wd / 2, y - uy * L / 2 - ux * wd / 2)]
        soft_shadow(a, pts, dx=4, dy=5)
        a.shape(pts, vary(a.rng, a.rng.choice([WOOD, WOOD_DARK, WOOD_LIGHT]), 0.06), outline=DETAIL * 1.2, corner=2, depth=2)
    for _ in range(n):
        dot(a, m + a.rng.uniform(-s * 0.35, s * 0.35), m + a.rng.uniform(-s * 0.35, s * 0.35), a.rng.uniform(2, 4), WOOD_LIGHT)
    return a.image()


def broken_door(seed=1407):
    w, h = 300, 220
    a = Art(w, h, seed)
    door = [(20, 30), (230, 20), (250, 100), (210, 130), (240, 200), (30, 200)]
    soft_shadow(a, door, dx=6, dy=8)
    a.shape(door, WOOD, corner=4, depth=6, light_k=0.3, detail=lambda art, p: boards(art, 20, 20, 260, 210, WOOD, 4))
    for y in (60, 160):
        a.shape(rect(30, y - 9, 220, y + 9), IRON, outline=DETAIL * 1.2, corner=2, depth=2, mottle=0)
    a.ink([(170, 30), (190, 90), (176, 140)], DETAIL * 1.2)  # split
    a.shape([(250, 110), (290, 120), (280, 150), (246, 140)], WOOD, outline=DETAIL * 1.2, corner=2, depth=2)  # splinter
    return a.image()


def broken_table(seed=1408):
    w, h = 380, 260
    a = Art(w, h, seed)
    halves = ([(20, 40), (190, 30), (176, 230), (30, 220)], [(200, 50), (360, 70), (350, 240), (186, 230)])
    for k, half in enumerate(halves):
        soft_shadow(a, half, dx=6, dy=8)
        a.shape(rot_pts(half, 190, 140, (-0.08, 0.1)[k]), WOOD, corner=4, depth=8, light_k=0.3, detail=lambda art, p: boards(art, 20, 30, 360, 240, WOOD, 3, vertical=True))
    for x, y in ((40, 250), (330, 20)):
        a.shape(rect(x - 12, y - 10, x + 12, y + 10), WOOD_DARK, outline=DETAIL * 1.2, corner=3, depth=2)
    return a.image()


def broken_chair(seed=1409):
    s = 200
    a = Art(s, s, seed)
    seat = [(40, 60), (150, 50), (160, 150), (50, 160)]
    soft_shadow(a, seat, dx=5, dy=6)
    a.shape(seat, WOOD, corner=6, depth=6, light_k=0.3)
    a.ink([(100, 55), (110, 150)], DETAIL, color=shade(WOOD, 0.5))
    beam_at(a, 20, 30, 120, 10, 14, WOOD_DARK)
    beam_at(a, 130, 180, 190, 140, 12, WOOD_DARK)
    return a.image()


def torn_cloth(a, pts, color):
    a.shape(pts, color, corner=0, depth=6, light_k=0.3, detail=lambda art, p: [art.ink([(px + art.rng.uniform(-10, 10), py), (px + art.rng.uniform(-10, 10), py + art.rng.uniform(30, 60))], FINE * 1.2, color=shade(color, 0.4), alpha=0.6) for px, py in pts[::3]])


def torn_banner(seed=1410):
    w, h = 220, 420
    a = Art(w, h, seed)
    handle(a, 10, 20, w - 10, 20, 12, WOOD_DARK)
    edge = [(30, 30), (w - 30, 30), (w - 30, 220), (w - 40, 260), (w - 60, 240), (w - 70, 330), (w / 2, 290), (90, 360), (70, 280), (40, 300), (30, 200)]
    torn_cloth(a, edge, RED)
    a.shape(ellipse(w / 2, 130, 34, 34, 32), rgb("#e2c068"), outline=DETAIL, depth=2, mottle=0)
    return a.image()


def torn_cloth_pile(seed=1411):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    pts = [(m + r * math.cos(t), m + r * math.sin(t)) for t, r in [(2 * math.pi * k / 14, a.rng.uniform(60, 110)) for k in range(14)]]
    torn_cloth(a, pts, RED)
    a.ink(chaikin([(m - 60, m - 10), (m, m + 20), (m + 70, m)], False, 2), DETAIL, color=shade(RED, 0.45))
    return a.image()


def splatter(seed, size=220):
    def make():
        a = Art(size, size, seed)
        m = size / 2
        a.shape(blob(m, m, size * 0.28, a.rng, 14, 0.35), BLOOD, outline=0, smooth=True, depth=2, shade_k=0, light_k=0.25, ao=0, mottle=0.12)
        for _ in range(16):
            t, d = a.rng.uniform(0, 6.28), a.rng.uniform(size * 0.3, size * 0.44)
            r = a.rng.uniform(2.5, 8)
            a.shape(blob(m + d * math.cos(t), m + d * math.sin(t), r, a.rng, 7, 0.25), BLOOD, outline=0, smooth=True, depth=1, shade_k=0, light_k=0.2, ao=0, mottle=0)
            a.ink([(m + d * 0.8 * math.cos(t), m + d * 0.8 * math.sin(t)), (m + d * math.cos(t), m + d * math.sin(t))], r * 0.6, color=BLOOD, taper=True)
        return a.image(grain=0.02)

    return make


def scorch(seed=1415, burnt=False):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    for r, al in ((100, 0.35), (76, 0.55), (52, 0.8)):
        p = to_path(blob(m, m, r, a.rng, 14, 0.25))
        a.fill_path(p, SOOT, al, blur=r * 0.18)
    for _ in range(18):
        t = a.rng.uniform(0, 6.28)
        a.ink([(m + 40 * math.cos(t), m + 40 * math.sin(t)), (m + a.rng.uniform(90, 120) * math.cos(t), m + a.rng.uniform(90, 120) * math.sin(t))], DETAIL * 1.2, color=SOOT, alpha=0.7, taper=True)
    if burnt:
        for _ in range(12):
            x, y = m + a.rng.uniform(-70, 70), m + a.rng.uniform(-70, 70)
            a.shape(rect(x - 20, y - 6, x + 20, y + 6), rgb("#3a2e28"), outline=DETAIL, corner=2, depth=1, mottle=0)
            dot(a, x + a.rng.uniform(-14, 14), y, 3, rgb("#e9773a"), 0.9)
    return a.image(grain=0.02)


def ash_pile(seed=1417):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    a.shape(blob(m, m, 84, a.rng, 12, 0.16), ASH, outline=DETAIL, smooth=True, depth=8, shade_k=0.3, light_k=0.4, ao=0, mottle=0.12)
    for _ in range(40):
        dot(a, m + a.rng.uniform(-70, 70), m + a.rng.uniform(-70, 70), a.rng.uniform(1.5, 3.5), a.rng.choice([SOOT, shade(ASH, 0.3)]), 0.9)
    for _ in range(4):
        x, y = m + a.rng.uniform(-40, 40), m + a.rng.uniform(-40, 40)
        a.shape(rect(x - 16, y - 5, x + 16, y + 5), SOOT, outline=FINE * 1.2, corner=2, depth=1, mottle=0)
    return a.image()


def rubble_pile(size, seed=1418):
    def make():
        s = {"small": 200, "medium": 300, "large": 420}[size]
        a = Art(s, s, seed)
        m = s / 2
        n = {"small": 8, "medium": 16, "large": 28}[size]
        pieces = [(m + a.rng.uniform(-s * 0.3, s * 0.3), m + a.rng.uniform(-s * 0.3, s * 0.3), a.rng.uniform(s * 0.05, s * 0.11)) for _ in range(n)]
        for x, y, r in sorted(pieces, key=lambda p: p[1]):
            pts = [(x + r * math.cos(t) * a.rng.uniform(0.7, 1.1), y + r * math.sin(t) * a.rng.uniform(0.7, 1.1)) for t in [2 * math.pi * i / 6 + a.rng.uniform(-0.2, 0.2) for i in range(6)]]
            soft_shadow(a, pts, dx=4, dy=5, alpha=0.3, blur=4)
            stone_block(a, pts, vary(a.rng, GREY, 0.08), outline=DETAIL * 1.3, corner=4, cracks=0)
        for _ in range(n * 2):
            dot(a, m + a.rng.uniform(-s * 0.4, s * 0.4), m + a.rng.uniform(-s * 0.4, s * 0.4), a.rng.uniform(2, 4), shade(GREY, 0.3), 0.9)
        return a.image()

    return make


def broken_pottery(seed=1421):
    """A smashed pot: curved shards of its wall (outer face and the lighter
    broken edge showing), a piece of the rim, scattered around."""
    s = 240
    a = Art(s, s, seed)
    clay = rgb("#bf7a4f")
    m = s / 2
    for k in range(7):
        t = 2 * math.pi * k / 7 + a.rng.uniform(-0.3, 0.3)
        d = a.rng.uniform(30, 70)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        r = a.rng.uniform(26, 40)
        a0 = a.rng.uniform(0, 6.28)
        span = a.rng.uniform(0.7, 1.2)
        outer = [(x + r * math.cos(a0 + span * j / 8), y + r * math.sin(a0 + span * j / 8)) for j in range(9)]
        inner = [(x + (r * 0.45) * math.cos(a0 + span * j / 8), y + (r * 0.45) * math.sin(a0 + span * j / 8)) for j in range(8, -1, -1)]
        shard = outer + inner
        soft_shadow(a, shard, dx=3, dy=4)
        a.shape(shard, vary(a.rng, clay, 0.06), outline=DETAIL * 1.2, corner=1, depth=3, light_k=0.45, mottle=0)
        a.ink(inner, FINE * 1.3, color=tint(clay, 0.4), alpha=0.9)
    rim = [(m + 30 * math.cos(t), m + 30 * math.sin(t)) for t in [0.3 + j * 0.15 for j in range(14)]]
    a.ink(rim, 16, color=INK, taper=False)
    a.ink(rim, 10, color=shade(clay, 0.1), taper=False)
    return a.image()


def broken_wheel(seed=1422):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    rim = [(m + 90 * math.cos(t), m + 90 * math.sin(t)) for t in [0.6 + k * (2 * math.pi - 1.6) / 30 for k in range(31)]]
    a.ink(rim, 24, color=INK, taper=False)
    a.ink(rim, 16, color=WOOD_DARK, taper=False)
    for k in range(7):
        t = 0.9 + k * 0.7
        handle(a, m + 14 * math.cos(t), m + 14 * math.sin(t), m + 80 * math.cos(t), m + 80 * math.sin(t), 9, WOOD)
    a.shape(ellipse(m, m, 20, 20, 24), WOOD, outline=DETAIL * 1.4, depth=3, mottle=0)
    beam_at(a, 140, 50, 200, 40, 12, WOOD)
    return a.image()


def cart_parts(seed=1423):
    w, h = 420, 300
    a = Art(w, h, seed)
    bed = rot_pts(rect(40, 60, 300, 220), 170, 140, 0.25)
    soft_shadow(a, bed, dx=8, dy=10)
    a.shape(bed, WOOD, corner=6, depth=8, light_k=0.3, detail=lambda art, p: boards(art, 20, 20, 340, 280, WOOD, 4, vertical=True))
    a.shape(rot_pts(rect(330, 40, 360, 160), 345, 100, 0.4), WOOD_DARK, outline=OUTLINE * 0.8, corner=12, depth=4)
    handle(a, 290, 260, 410, 210, 12, WOOD)
    for _ in range(4):
        x, y = a.rng.uniform(40, 380), a.rng.uniform(230, 290)
        a.shape(rect(x - 20, y - 5, x + 20, y + 5), WOOD_LIGHT, outline=DETAIL, corner=2, depth=1)
    return a.image()


def cracked_tiles(seed=1424):
    s = 256
    a = Art(s, s, seed)
    for i in range(2):
        for j in range(2):
            x0, y0 = 8 + i * 120, 8 + j * 120
            p = stone_block(a, rect(x0 + 2, y0 + 2, x0 + 118, y0 + 118), vary(a.rng, LIGHT_STONE, 0.05), outline=DETAIL * 1.3, corner=3, cracks=0, depth=4)
            with a.clip(p):
                for _ in range(2):
                    crack(a, x0 + a.rng.uniform(20, 100), y0 + a.rng.uniform(20, 100), a.rng.uniform(0, 6.28), 90, FINE * 1.6)
    pebble(a, 200, 210, 12, LIGHT_STONE)
    return a.image()


def statue_head(seed=1425):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    head = chaikin([(m - 60, m - 20), (m - 40, m - 64), (m + 30, m - 70), (m + 66, m - 20), (m + 56, m + 50), (m - 10, m + 70), (m - 56, m + 36)], True, 2)
    soft_shadow(a, head, dx=8, dy=10)
    stone_block(a, head, MARBLE, corner=0, cracks=2, light_k=0.45)
    # Lying on its side: profile features drawn on the top face.
    a.ink(chaikin([(m + 10, m - 30), (m + 30, m - 10), (m + 24, m + 4), (m + 34, m + 16)], False, 2), DETAIL, color=shade(MARBLE, 0.4))
    a.ink([(m - 2, m - 18), (m + 10, m - 20)], DETAIL, color=shade(MARBLE, 0.45))
    for k in range(5):
        a.ink([(m - 50 + k * 10, m - 50 + k * 4), (m - 40 + k * 10, m - 30 + k * 6)], FINE * 1.2, color=shade(MARBLE, 0.4))
    return a.image()


def column_drums(seed=1426):
    w, h = 460, 260
    a = Art(w, h, seed)

    def drum(x, y, L, ang):
        pts = rot_pts(rect(x, y - 44, x + L, y + 44), x, y, ang)
        soft_shadow(a, pts, dx=8, dy=10)
        a.shape(pts, GREY, corner=36, depth=10, light_k=0.35, detail=lambda art, p: [art.ink(rot_pts([(x + 6, y + o), (x + L - 6, y + o)], x, y, ang), FINE * 1.1, color=shade(GREY, 0.45), alpha=0.75) for o in range(-36, 40, 12)])
        ex, ey = rot_pts([(x + L, y)], x, y, ang)[0]
        a.shape(rot_pts(ellipse(ex, ey, 14, 44, 32), ex, ey, ang), LIGHT_STONE, outline=DETAIL * 1.2, depth=3, mottle=0)

    drum(30, 90, 150, 0.15)
    drum(220, 180, 140, -0.1)
    return a.image()


def overgrown_rubble(seed=1427):
    s = 300
    img_rubble = rubble_pile("medium", seed)()
    a = Art(s, s, seed)
    import numpy as np

    a.c.drawImage(skia.Image.fromarray(np.asarray(img_rubble), colorType=skia.kRGBA_8888_ColorType), 0, 0)
    m = s / 2
    for k in range(3):
        pts = [(m - 120 + t * 240 + 20 * math.sin(t * 7 + k), m - 60 + k * 50 + 30 * math.sin(t * 4 + k)) for t in [j / 20 for j in range(21)]]
        a.ink(pts, 6, color=INK, taper=True)
        a.ink(pts, 3.5, color=rgb("#5a6a2e"), taper=True)
        for j in range(2, 20, 3):
            x, y = pts[j]
            leaf(a, x + a.rng.uniform(-8, 8), y + a.rng.uniform(-8, 8), 22, vary(a.rng, GREEN, 0.06))
    return a.image()


def debris_puddle(seed=1428):
    w, h = 320, 240
    a = Art(w, h, seed)

    def glints(art, p):
        art.ink([(110, 90), (150, 84)], FINE * 1.5, color=FOAM, alpha=0.9)

    a.shape(blob(w / 2, h / 2, 130, a.rng, 11, 0.14, ry=90), rgb("#6f8a96"), outline=DETAIL, smooth=True, depth=8, shade_k=0, light_k=0, ao=0.5, detail=glints)
    for _ in range(5):
        pebble(a, w / 2 + a.rng.uniform(-100, 100), h / 2 + a.rng.uniform(-60, 60), a.rng.uniform(8, 14), GREY)
    beam_at(a, 60, 170, 170, 150, 16, WOOD_DARK)
    return a.image()


# -- lighting ---------------------------------------------------------------------------------------


def wall_edge(a, w, h=26):
    a.shape(rect(4, 4, w - 4, h), shade(STONE, 0.2), outline=DETAIL * 1.2, corner=3, depth=4)


def wall_torch(seed=1501, lit=True):
    w, h = 160, 200
    a = Art(w, h, seed)
    wall_edge(a, w)
    a.shape(rect(w / 2 - 18, 18, w / 2 + 18, 46), IRON, outline=DETAIL * 1.4, corner=4, depth=3, mottle=0)
    handle(a, w / 2, 40, w / 2, 110, 14, WOOD_DARK)
    a.shape(ellipse(w / 2, 116, 16, 16, 24), rgb("#3a2e28"), outline=DETAIL * 1.3, depth=2, mottle=0)  # pitch-soaked head
    if lit:
        fire(a, w / 2, 118, 22, glow_r=70)
    return a.image()


def double_sconce(seed=1503):
    w, h = 260, 180
    a = Art(w, h, seed)
    wall_edge(a, w)
    a.shape(rect(w / 2 - 70, 18, w / 2 + 70, 40), BRASS, outline=DETAIL * 1.4, corner=6, depth=3, mottle=0)
    for x in (w / 2 - 60, w / 2 + 60):
        handle(a, w / 2, 34, x, 90, 8, BRASS)
        a.shape(ellipse(x, 96, 18, 18, 24), BRASS, outline=DETAIL * 1.2, depth=3, mottle=0)
        candle(a, x, 96, 11)
    return a.image()


def standing_torch(seed=1504):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    for t in (0.5, 2.6, 4.7):
        handle(a, m, m, m + 64 * math.cos(t), m + 64 * math.sin(t), 9, IRON)
    a.shape(ellipse(m, m, 22, 22, 28), IRON, outline=DETAIL * 1.3, depth=3, mottle=0)
    fire(a, m, m, 24, glow_r=80)
    return a.image()


def brazier(palette, square=False, seed=1505):
    def make():
        s = 220
        a = Art(s, s, seed)
        m = s / 2
        if square:
            a.shape(rect(30, 30, s - 30, s - 30), rgb("#4a4c52"), corner=10, depth=10)
            a.shape(rect(46, 46, s - 46, s - 46), SOOT, outline=DETAIL * 1.3, corner=6, depth=8, shade_k=0, light_k=0, ao=0.6)
            for x, y in ((38, 38), (s - 38, 38), (38, s - 38), (s - 38, s - 38)):
                dot(a, x, y, 4, tint(IRON, 0.4))
        else:
            for t in (0.3, 2.4, 4.5):
                a.shape(ellipse(m + 72 * math.cos(t), m + 72 * math.sin(t), 12, 12, 20), IRON, outline=DETAIL * 1.2, depth=2, mottle=0)
            a.shape(ellipse(m, m, 74, 74, 64), rgb("#4a4c52"), depth=10)
            a.shape(ellipse(m, m, 56, 56, 64), SOOT, outline=DETAIL * 1.3, depth=8, shade_k=0, light_k=0, ao=0.6)
        fire(a, m, m, 40, palette, glow_r=95)
        return a.image()

    return make


def floor_candelabra(color=IRON, seed=1510):
    def make():
        s = 220
        a = Art(s, s, seed)
        m = s / 2
        for t in [2 * math.pi * k / 3 + 0.5 for k in range(3)]:
            handle(a, m, m, m + 60 * math.cos(t), m + 60 * math.sin(t), 8, color)
        a.shape(ellipse(m, m, 20, 20, 28), color, outline=DETAIL * 1.3, depth=4, light_k=0.5, mottle=0)
        candle(a, m, m, 11)
        for t in [2 * math.pi * k / 3 + 0.5 for k in range(3)]:
            x, y = m + 60 * math.cos(t), m + 60 * math.sin(t)
            a.shape(ellipse(x, y, 15, 15, 24), color, outline=DETAIL * 1.2, depth=2, mottle=0)
            candle(a, x, y, 10)
        return a.image()

    return make


def chandelier(seed=1512, wheel=False):
    s = 320
    a = Art(s, s, seed)
    m = s / 2
    R = 120
    col = WOOD_DARK if wheel else BRASS
    if wheel:
        a.ink(ellipse(m, m, R, R, 80), 26, closed=True, color=INK)
        a.ink(ellipse(m, m, R, R, 80), 18, closed=True, color=col)
        for k in range(8):
            t = 2 * math.pi * k / 8
            handle(a, m, m, m + R * math.cos(t), m + R * math.sin(t), 9, WOOD)
    else:
        a.ink(ellipse(m, m, R, R, 80), 14, closed=True, color=INK)
        a.ink(ellipse(m, m, R, R, 80), 8, closed=True, color=col)
        for k in range(4):
            t = 2 * math.pi * k / 4 + math.pi / 4
            chain(a, [(m, m), (m + R * math.cos(t), m + R * math.sin(t))], 10, color=rgb("#8a7a4a"))
    a.shape(ellipse(m, m, 18, 18, 24), col, outline=DETAIL * 1.3, depth=3, mottle=0)
    n = 8 if wheel else 6
    for k in range(n):
        t = 2 * math.pi * k / n
        candle(a, m + R * math.cos(t), m + R * math.sin(t), 11)
    return a.image()


def candle_group(seed=1514, n=5, spread=50, melted=False):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    if melted:
        a.shape(blob(m, m, spread + 20, a.rng, 12, 0.25), WAX, outline=DETAIL, smooth=True, depth=3, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
    for _ in range(n):
        t, d = a.rng.uniform(0, 6.28), spread * math.sqrt(a.rng.random())
        candle(a, m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(8, 14), lit=a.rng.random() < 0.85)
    return a.image()


def lantern(body=IRON, light=rgb("#ffe39a"), lit=True, seed=1517):
    def make():
        s = 170
        a = Art(s, s, seed)
        m = s / 2
        if lit:
            glow(a, m, m, 75, rgb("#ffd27a"), 0.45)
        a.shape(rect(m - 36, m - 36, m + 36, m + 36), body, corner=8, depth=6, light_k=0.4)
        a.shape(rect(m - 24, m - 24, m + 24, m + 24), light if lit else rgb("#5a5048"), outline=DETAIL, corner=4, depth=3, shade_k=0, light_k=0.4)
        a.ink([(m - 24, m), (m + 24, m)], DETAIL, color=body, taper=False)
        a.ink([(m, m - 24), (m, m + 24)], DETAIL, color=body, taper=False)
        a.shape(ellipse(m, m, 10, 10, 16), body, outline=DETAIL, depth=2, mottle=0)
        a.ink(ellipse(m, m - 38, 10, 7, 16), DETAIL * 1.3, closed=True, color=body)
        return a.image()

    return make


def paper_lantern(seed=1520):
    s = 170
    a = Art(s, s, seed)
    m = s / 2
    glow(a, m, m, 75, rgb("#ffb070"), 0.45)
    a.shape(ellipse(m, m, 50, 50, 48), RED, depth=6, light_k=0.5, detail=lambda art, p: [art.ink(ellipse(m, m, r, r, 40), FINE * 1.2, closed=True, color=shade(RED, 0.4), alpha=0.8) for r in (18, 30, 42)])
    a.shape(ellipse(m, m, 10, 10, 16), rgb("#3a2e28"), outline=DETAIL, depth=1, mottle=0)
    return a.image()


def oil_lamp(seed=1521):
    w, h = 170, 110
    a = Art(w, h, seed)
    glow(a, w - 30, h / 2, 40, rgb("#ffd27a"), 0.45)
    a.shape(chaikin([(16, h / 2), (50, 18), (110, 22), (w - 20, h / 2 - 8), (w - 20, h / 2 + 8), (110, h - 22), (50, h - 18)], True, 2), BRASS, depth=6, light_k=0.5)
    a.shape(ellipse(64, h / 2, 16, 16, 24), shade(BRASS, 0.35), outline=DETAIL, depth=3, shade_k=0, light_k=0, mottle=0)
    a.shape(scallop(w - 24, h / 2, 9, a.rng, 5, 0.2), rgb("#f6b444"), outline=FINE * 1.2, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def fire_pit(seed=1522):
    s = 320
    a = Art(s, s, seed)
    m = s / 2
    pit = rect(40, 40, s - 40, s - 40)
    stone_block(a, rect(20, 20, s - 20, s - 20), GREY, corner=10, cracks=1)
    a.shape(pit, SOOT, outline=DETAIL * 1.3, corner=8, depth=12, shade_k=0, light_k=0, ao=0.6)
    for k in range(4):
        t = k * math.pi / 4 + 0.3
        handle(a, m - 70 * math.cos(t), m - 70 * math.sin(t), m + 70 * math.cos(t), m + 70 * math.sin(t), 22, WOOD_DARK)
    fire(a, m, m, 52, glow_r=120)
    return a.image()


def orb_lamp(color, seed=1523):
    def make():
        s = 180
        a = Art(s, s, seed)
        m = s / 2
        for t in (0.5, 2.6, 4.7):
            handle(a, m, m, m + 62 * math.cos(t), m + 62 * math.sin(t), 8, BRASS)
        glow(a, m, m, 80, color, 0.5)
        a.shape(ellipse(m, m, 34, 34, 40), color, outline=DETAIL * 1.4, depth=5, light_k=0.8, mottle=0.04)
        a.ink([(m - 18, m - 10), (m - 8, m - 20)], FINE * 2, color=(255, 255, 255), alpha=0.85)
        return a.image()

    return make


def light_crystal(color, seed=1525):
    def make():
        s = 200
        a = Art(s, s, seed)
        m = s / 2
        glow(a, m, m, 90, color, 0.5)
        stone_block(a, blob(m, m + 8, 46, a.rng, 9, 0.12), CAVE_DARK, smooth=True, cracks=0)
        crystal(a, m, m, 38, color, 0.3)
        crystal(a, m - 34, m + 20, 18, color, 0.8)
        crystal(a, m + 32, m + 18, 15, color, 0.1)
        return a.image()

    return make


CAVE = {
    # caves & underground
    "Stalagmite": stalagmite,
    "Stalagmite Cluster": stalagmite_cluster,
    "Small Stalagmites": small_stalagmites,
    "Broken Stalagmite": broken_stalagmite,
    **{f"{k} Crystal Formation": crystal_formation(c, 1305 + i) for i, (k, c) in enumerate(GEMS.items())},
    "Red Giant Mushroom": giant_mushroom(rgb("#b84a3a"), True, False, 1311),
    "Brown Giant Mushroom": giant_mushroom(rgb("#a8845a"), False, False, 1312),
    "Purple Giant Mushroom": giant_mushroom(rgb("#8a5ab0"), True, False, 1313),
    "Glowing Giant Mushroom": giant_mushroom(rgb("#4fc2c0"), True, True, 1314),
    "Yellow Giant Mushroom": giant_mushroom(rgb("#d6b04a"), True, False, 1315),
    "Giant Mushroom Cluster": mushroom_cluster,
    "Cave Pool": cave_pool,
    "Small Cave Pool": small_cave_pool,
    "Glowing Pool": glowing_pool,
    "Root Tangle": root_tangle,
    "Hanging Roots": ceiling_roots,
    "Cave Hole": cave_hole,
    "Deep Pit": deep_pit,
    "Rope Ladder Hole": rope_ladder_hole,
    "Rock Formation": rock_formation,
    "Large Rock Formation": lambda: rock_formation(1335, big=True),
    "Stream Rocks": stream_rocks,
    "Rail Straight": rail_straight,
    "Rail Curve": rail_curve,
    "Rail End": rail_end,
    "Minecart": minecart(None, 1344),
    "Minecart with Ore": minecart(rgb("#7a6e66"), 1345),
    "Minecart with Gold": minecart(rgb("#e2b84e"), 1346),
    "Mine Support": support_frame,
    "Timber Props": timber_props,
    "Mining Tools": mining_tools,
    "Iron Ore Pile": ore_pile(rgb("#b8735a"), 1350),
    "Gold Ore Pile": ore_pile(rgb("#e2b84e"), 1351),
    "Copper Ore Pile": ore_pile(rgb("#5fb0a0"), 1352),
    "Silver Ore Pile": ore_pile(rgb("#d6dbe2"), 1353),
    "Gem Pile": gem_pile,
    "Hook Lantern": hook_lantern,
    "Bat Roost": bat_roost,
    "Large Spider Web": spider_web,
    "Egg Clutch": egg_clutch,
    "Cave Bones": cave_bones,
    "Glowing Moss": glowing_moss(rgb("#7fd36a"), 1365),
    "Blue Glowing Moss": glowing_moss(rgb("#4fc2c0"), 1366),
    # ruins & debris
    "Collapsed Wall": lambda: wall_chunk(1401),
    "Large Collapsed Wall": lambda: wall_chunk(1402, big=True),
    "Fallen Beam": fallen_beam,
    "Crossed Beams": crossed_beams,
    "Wood Debris": debris_pile,
    "Small Wood Debris": lambda: debris_pile(1406, small=True),
    "Broken Door": broken_door,
    "Broken Table": broken_table,
    "Broken Chair": broken_chair,
    "Torn Banner": torn_banner,
    "Torn Cloth": torn_cloth_pile,
    "Blood Splatter": splatter(1412),
    "Blood Splatter Small": splatter(1413, 150),
    "Blood Splatter Large": splatter(1414, 300),
    "Scorch Mark": scorch,
    "Burnt Floor": lambda: scorch(1416, burnt=True),
    "Ash Pile": ash_pile,
    "Rubble Small": rubble_pile("small", 1418),
    "Rubble Medium": rubble_pile("medium", 1419),
    "Rubble Large": rubble_pile("large", 1420),
    "Broken Pottery": broken_pottery,
    "Broken Wheel": broken_wheel,
    "Wrecked Cart": cart_parts,
    "Cracked Tiles": cracked_tiles,
    "Statue Head": statue_head,
    "Column Drums": column_drums,
    "Overgrown Rubble": overgrown_rubble,
    "Debris Puddle": debris_puddle,
    # lighting
    "Wall Torch": wall_torch,
    "Unlit Wall Torch": lambda: wall_torch(1502, lit=False),
    "Double Sconce": double_sconce,
    "Standing Torch": standing_torch,
    "Brazier": brazier(FIRE, False, 1505),
    "Green Fire Brazier": brazier(GREEN_FIRE, False, 1506),
    "Blue Fire Brazier Iron": brazier(BLUE_FIRE, False, 1507),
    "Purple Fire Brazier": brazier(PURPLE_FIRE, False, 1508),
    "Square Brazier": brazier(FIRE, True, 1509),
    "Floor Candelabra": floor_candelabra(IRON, 1510),
    "Gold Floor Candelabra": floor_candelabra(BRASS, 1511),
    "Chandelier": chandelier,
    "Wheel Chandelier": lambda: chandelier(1513, wheel=True),
    "Candles": lambda: candle_group(1514, 3, 30),
    "Many Candles": lambda: candle_group(1515, 9, 66),
    "Melted Candles": lambda: candle_group(1516, 5, 40, melted=True),
    "Iron Lantern": lantern(IRON, seed=1517),
    "Brass Lantern": lantern(BRASS, seed=1518),
    "Unlit Lantern": lantern(IRON, lit=False, seed=1519),
    "Paper Lantern": paper_lantern,
    "Brass Oil Lamp": oil_lamp,
    "Fire Pit": fire_pit,
    "Blue Orb Lamp": orb_lamp(rgb("#6fb0f0"), 1523),
    "Amber Orb Lamp": orb_lamp(rgb("#f0b050"), 1524),
    "Blue Light Crystal": light_crystal(rgb("#6fb0f0"), 1525),
    "Green Light Crystal": light_crystal(rgb("#7fd36a"), 1526),
    "Pink Light Crystal": light_crystal(rgb("#f08ac0"), 1527),
}

CAVE_COLORABLE = {"Torn Banner", "Torn Cloth", "Paper Lantern"}
