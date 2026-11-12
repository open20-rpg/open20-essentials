"""Nature bits (batch 4): fallen logs, branches, leaves, pebbles, plants,
flowers, mushrooms. Top-down, same pen style."""

import math

import skia

from kit import STONE, WOOD_LIGHT, dot, scallop, soft_shadow
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, normals, rect, rgb, shade, tint, to_path, vary

BARK = rgb("#7a5a3e")
MOSS = rgb("#6f9443")
GREEN = rgb("#5f8f3c")
GREEN_D = rgb("#3f6a2a")
GREEN_L = rgb("#8fb85a")
AUTUMN = [rgb("#c9752f"), rgb("#d99a3a"), rgb("#b54a2c"), rgb("#a8652f"), rgb("#d6b04a")]
DRY = [rgb("#a07a4a"), rgb("#8a6a40"), rgb("#b8915a"), rgb("#7a5a38")]


# -- shared pieces ---------------------------------------------------------------------------


def tube(spine, w0, w1):
    """A polygon around a polyline, its width going from w0 to w1."""
    ns = normals(spine, False)
    n = len(spine)
    ws = [w0 + (w1 - w0) * i / (n - 1) for i in range(n)]
    left = [(x + nx * w / 2, y + ny * w / 2) for (x, y), (nx, ny), w in zip(spine, ns, ws)]
    right = [(x - nx * w / 2, y - ny * w / 2) for (x, y), (nx, ny), w in zip(spine, ns, ws)]
    return left + right[::-1]


def bark_strokes(a, spine, w, color, rows=(-0.3, 0.0, 0.3)):
    """Short pen strokes along a log/branch, either side of its middle."""
    ns = normals(spine, False)
    n = len(spine)
    for f in rows:
        j = a.rng.randint(0, 2)
        while j < n - 2:
            run = a.rng.randint(2, 4)
            seg = [(spine[k][0] + ns[k][0] * w * f, spine[k][1] + ns[k][1] * w * f) for k in range(j, min(n, j + run + 1))]
            if len(seg) > 1:
                a.ink(seg, FINE * 0.9, color=shade(color, 0.6), alpha=0.7, wob=0.4)
            j += run + a.rng.randint(1, 3)


def wavy(x0, y0, x1, y1, rng, n=14, amp=6):
    out = []
    ph = rng.uniform(0, 6.28)
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        d = amp * math.sin(t * 3 + ph) * math.sin(math.pi * t)
        out.append((x + nx * d, y + ny * d))
    return out


def leaf(a, x, y, size, color, ang=None, vein=True, outline=FINE * 1.3):
    """One leaf: pointed oval with a midrib."""
    ang = a.rng.uniform(0, 6.28) if ang is None else ang
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    L, W = size, size * a.rng.uniform(0.38, 0.5)
    pts = [(x - ux * L / 2, y - uy * L / 2), (x + px * W / 2, y + py * W / 2), (x + ux * L / 2, y + uy * L / 2), (x - px * W / 2, y - py * W / 2)]
    soft_shadow(a, pts, dx=2, dy=3, alpha=0.25, blur=2)
    a.shape(chaikin(pts, True, 2), color, outline=outline, corner=0, wob=0.2, depth=2, shade_k=0.35, light_k=0.35, ao=0, mottle=0)
    if vein:
        a.ink([(x - ux * L * 0.45, y - uy * L * 0.45), (x + ux * L * 0.4, y + uy * L * 0.4)], FINE * 0.8, color=shade(color, 0.5), alpha=0.8)


def oak_leaf(a, x, y, size, color, ang=None):
    """A lobed leaf (oak-like)."""
    ang = a.rng.uniform(0, 6.28) if ang is None else ang
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    pts = []
    for i in range(41):
        t = i / 40
        s = -0.5 + t
        w = math.sin(math.pi * t) * (0.32 + 0.1 * math.sin(t * math.pi * 8)) * size
        pts.append((x + ux * s * size + px * w, y + uy * s * size + py * w))
    for i in range(40, -1, -1):
        t = i / 40
        s = -0.5 + t
        w = math.sin(math.pi * t) * (0.32 + 0.1 * math.sin(t * math.pi * 8)) * size
        pts.append((x + ux * s * size - px * w, y + uy * s * size - py * w))
    soft_shadow(a, pts, dx=2, dy=3, alpha=0.25, blur=2)
    a.shape(pts, color, outline=FINE * 1.3, corner=0, wob=0.2, depth=2, shade_k=0.35, light_k=0.35, ao=0, mottle=0)
    a.ink([(x - ux * size * 0.55, y - uy * size * 0.55), (x + ux * size * 0.4, y + uy * size * 0.4)], FINE * 0.8, color=shade(color, 0.5), alpha=0.8)


def pebble(a, x, y, r, color=STONE, outline=DETAIL):
    pts = blob(x, y, r, a.rng, 8, 0.18, ry=r * a.rng.uniform(0.7, 1.0))
    soft_shadow(a, pts, dx=2, dy=3, alpha=0.3, blur=2)
    a.shape(pts, vary(a.rng, color, 0.08), outline=outline, smooth=True, depth=max(2, r * 0.2), shade_k=0.45, light_k=0.45, ao=0, mottle=0)


# -- wood ---------------------------------------------------------------------------------------


def fallen_log(seed=301, mossy=False, hollow=False):
    w, h = 520, 200
    a = Art(w, h, seed)
    spine = [(40 + (w - 100) * t, h / 2 + 10 * math.sin(t * 2.5 + 1)) for t in [i / 20 for i in range(21)]]
    poly = tube(spine, 92, 80)
    # A broken-off branch stub and the root end's flare.
    stub = tube([(200, h / 2 - 30), (230, 22), (250, 6)], 26, 14)
    a.shape(stub, BARK, outline=DETAIL * 1.3, corner=0, depth=4)
    body = a.shape(poly, BARK, corner=0, depth=12, light_k=0.3, detail=lambda art, p: bark_strokes(art, spine, 92, BARK, (-0.32, -0.1, 0.12, 0.34)))
    if mossy:
        with a.clip(body):
            for _ in range(7):
                x = a.rng.uniform(60, w - 90)
                a.shape(blob(x, h / 2 - 30, a.rng.uniform(20, 36), a.rng, 9, 0.3, ry=a.rng.uniform(14, 22)), MOSS, outline=0, smooth=True, depth=3, shade_k=0.3, light_k=0.3, ao=0, mottle=0.1)
    # The sawn/broken end (right) showing rings; the left end is the rounded root.
    ex, ey = spine[-1]
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


def mossy_log(seed=302):
    return fallen_log(seed, mossy=True)


def hollow_log(seed=303):
    return fallen_log(seed, hollow=True)


def branch(seed=304):
    w, h = 420, 220
    a = Art(w, h, seed)
    limbs = []

    def grow(x, y, ang, L, wd, depth):
        spine = [(x, y)]
        for i in range(1, 9):
            ang += a.rng.gauss(0, 0.08)
            px, py = spine[-1]
            spine.append((px + L / 8 * math.cos(ang), py + L / 8 * math.sin(ang)))
        limbs.append((wd, tube(spine, wd, max(1.5, wd * 0.45))))
        if depth < 2:
            for k in (3, 6):
                side = a.rng.choice((-1, 1))
                bx, by = spine[k]
                grow(bx, by, ang + side * a.rng.uniform(0.4, 0.8), L * 0.45, wd * 0.5, depth + 1)

    grow(20, h / 2 + 30, -0.12, 300, 24, 0)
    body = to_path(limbs[0][1])
    for _, q in limbs[1:]:
        try:
            body = skia.Op(body, to_path(q), skia.kUnion_PathOp)
        except RuntimeError:
            pass
    a.fill_path(body, BARK)
    with a.clip(body):
        a.stroke_path(body, shade(BARK, 0.4), 5, 0.35, blur=3)
    a.stroke_path(body, INK, DETAIL * 1.1)
    # A few leaves still on it.
    for _ in range(5):
        leaf(a, a.rng.uniform(180, 390), a.rng.uniform(60, 170), 26, vary(a.rng, GREEN, 0.06))
    return a.image()


def twigs(seed=305):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    for _ in range(9):
        t = a.rng.uniform(0, 3.14)
        L = a.rng.uniform(90, 160)
        x0, y0 = m - L / 2 * math.cos(t) + a.rng.uniform(-30, 30), m - L / 2 * math.sin(t) + a.rng.uniform(-30, 30)
        pts = wavy(x0, y0, x0 + L * math.cos(t), y0 + L * math.sin(t), a.rng, 8, 4)
        a.ink(pts, 9, color=INK, taper=False, wob=0.2)
        a.ink(pts, 5.5, color=vary(a.rng, BARK, 0.08), taper=False, wob=0.2)
        j = a.rng.randint(3, 6)
        bx, by = pts[j]
        bt = t + a.rng.choice((-1, 1)) * 0.6
        a.ink([(bx, by), (bx + 26 * math.cos(bt), by + 26 * math.sin(bt))], 6, color=INK, taper=True)
        a.ink([(bx, by), (bx + 26 * math.cos(bt), by + 26 * math.sin(bt))], 3.5, color=BARK, taper=True)
    return a.image()


def pine_cone(seed=306):
    s = 110
    a = Art(s, s, seed)
    m = s / 2
    cone = rgb("#8a5e36")
    soft_shadow(a, (m, m), 30, 4, 5, 0.3, 4)
    a.shape(ellipse(m, m, 28, 38, 40, rot=0.5), cone, outline=DETAIL * 1.2, depth=5, light_k=0.4, mottle=0)
    for i in range(16):
        t = 2 * math.pi * i / 16
        for rr in (10, 20):
            x, y = m + rr * math.cos(t) * 0.75, m + rr * math.sin(t)
            a.shape(ellipse(x, y, 6, 4, 12, rot=t), tint(cone, 0.15), outline=FINE, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    return a.image()


# -- leaves -------------------------------------------------------------------------------------


def leaf_pile(seed=307, colors=None):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    colors = colors or AUTUMN
    base = blob(m, m, 110, a.rng, 12, 0.12)
    a.shape(base, shade(colors[0], 0.25), outline=DETAIL, smooth=True, depth=14, shade_k=0.5, light_k=0, ao=0.3, mottle=0.1)
    spots = []
    for _ in range(90):
        t, d = a.rng.uniform(0, 6.28), 110 * math.sqrt(a.rng.random())
        spots.append((m + d * math.cos(t), m + d * math.sin(t), 1 - d / 110))
    for x, y, hgt in sorted(spots, key=lambda p: p[2]):
        col = mix(shade(a.rng.choice(colors), 0.2), tint(a.rng.choice(colors), 0.15), hgt)
        (oak_leaf if a.rng.random() < 0.5 else leaf)(a, x, y, a.rng.uniform(26, 36), col)
    return a.image()


def green_leaf_pile(seed=308):
    return leaf_pile(seed, [GREEN, GREEN_L, GREEN_D, rgb("#7aa64a")])


def scattered_leaves(seed=309, colors=None):
    s = 320
    a = Art(s, s, seed)
    colors = colors or AUTUMN
    for _ in range(26):
        x, y = a.rng.uniform(30, s - 30), a.rng.uniform(30, s - 30)
        (oak_leaf if a.rng.random() < 0.5 else leaf)(a, x, y, a.rng.uniform(24, 34), vary(a.rng, a.rng.choice(colors), 0.05))
    return a.image()


def dry_leaves(seed=310):
    return scattered_leaves(seed, DRY)


def single_leaf(seed=311):
    s = 90
    a = Art(s, s, seed)
    oak_leaf(a, s / 2, s / 2, 70, AUTUMN[0], ang=-0.8)
    return a.image()


# -- stones -------------------------------------------------------------------------------------


def pebbles(seed=312):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    for _ in range(26):
        t, d = a.rng.uniform(0, 6.28), 100 * math.sqrt(a.rng.random())
        pebble(a, m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(5, 12), outline=FINE * 1.3)
    return a.image()


def river_stones(seed=313):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    cols = [rgb("#a8a49a"), rgb("#8f948f"), rgb("#b8ad9a"), rgb("#7f857f")]
    spots = [(m + a.rng.uniform(-80, 80), m + a.rng.uniform(-80, 80)) for _ in range(9)]
    for x, y in sorted(spots, key=lambda p: p[1]):
        pebble(a, x, y, a.rng.uniform(16, 28), a.rng.choice(cols), outline=DETAIL * 1.3)
    return a.image()


def stepping_stone(seed=314):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    p = a.shape(blob(m, m, 86, a.rng, 9, 0.1, ry=70), STONE, smooth=True, depth=10, light_k=0.4)
    with a.clip(p):
        for _ in range(12):
            dot(a, a.rng.uniform(40, 180), a.rng.uniform(50, 170), a.rng.uniform(1, 2), shade(STONE, 0.45), 0.6)
        a.shape(blob(m + 50, m + 40, 24, a.rng, 9, 0.3), MOSS, outline=0, smooth=True, depth=2, shade_k=0.3, light_k=0.3, ao=0, mottle=0.1)
    return a.image()


# -- plants -------------------------------------------------------------------------------------


def blades(a, cx, cy, n, length, colors, spread=math.pi * 2, width=7, rot=-math.pi / 2):
    """Grass blades fanning out from a point (seen from above, each a thin
    pointed shape bending outward)."""
    for i in range(n):
        t = rot + (i / max(1, n - 1) - 0.5) * spread if spread < 6 else 2 * math.pi * i / n + a.rng.uniform(-0.2, 0.2)
        L = length * a.rng.uniform(0.6, 1.0)
        bend = a.rng.uniform(-0.4, 0.4)
        spine = []
        for j in range(9):
            s = j / 8
            aa = t + bend * s * s
            spine.append((cx + L * s * math.cos(aa), cy + L * s * math.sin(aa)))
        poly = tube(spine, width, 0.6)
        a.shape(poly, vary(a.rng, a.rng.choice(colors), 0.05), outline=FINE * 1.2, corner=0, wob=0, depth=1.5, shade_k=0.3, light_k=0.3, ao=0, mottle=0)


def grass_tuft(seed=315):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    blades(a, m, m, 16, 80, [GREEN, GREEN_L, GREEN_D])
    blades(a, m, m, 9, 50, [GREEN_L, rgb("#a3c86a")])
    return a.image()


def tall_grass(seed=316):
    w, h = 320, 220
    a = Art(w, h, seed)
    for _ in range(6):
        blades(a, a.rng.uniform(70, w - 70), a.rng.uniform(80, h - 60), 12, 90, [GREEN, GREEN_L, rgb("#a8b85a"), rgb("#c8c070")])
    return a.image()


def fern(seed=317):
    s = 300
    a = Art(s, s, seed)
    m = s / 2
    for i in range(7):
        t = 2 * math.pi * i / 7 + a.rng.uniform(-0.15, 0.15)
        L = a.rng.uniform(110, 135)
        bend = a.rng.uniform(-0.3, 0.3)
        spine = [(m + L * k / 12 * math.cos(t + bend * (k / 12) ** 2), m + L * k / 12 * math.sin(t + bend * (k / 12) ** 2)) for k in range(13)]
        for k in range(2, 12):
            x, y = spine[k]
            px, py = spine[k - 1]
            ang = math.atan2(y - py, x - px)
            ln = 30 * math.sin(math.pi * k / 13) + 6
            for side in (-1, 1):
                leaf(a, x + math.cos(ang + side * 1.1) * ln * 0.5, y + math.sin(ang + side * 1.1) * ln * 0.5, ln, vary(a.rng, GREEN if k % 2 else GREEN_L, 0.04), ang=ang + side * 1.1, vein=False, outline=FINE)
        a.ink(spine, DETAIL * 0.8, color=GREEN_D)
    return a.image()


def flowers(seed=318, petal=rgb("#e6b84a"), center=rgb("#9a5a2a")):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    blades(a, m, m, 14, 70, [GREEN, GREEN_D, GREEN_L])
    for _ in range(9):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, 80)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        r = a.rng.uniform(11, 15)
        for k in range(5):
            pa = 2 * math.pi * k / 5 + a.rng.uniform(-0.1, 0.1)
            a.shape(ellipse(x + r * 0.6 * math.cos(pa), y + r * 0.6 * math.sin(pa), r * 0.55, r * 0.38, 16, rot=pa), vary(a.rng, petal, 0.05), outline=FINE * 1.1, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
        dot(a, x, y, r * 0.3, center)
    return a.image()


def red_flowers(seed=319):
    return flowers(seed, rgb("#c8443a"), rgb("#3a2a22"))


def blue_flowers(seed=320):
    return flowers(seed, rgb("#6f8fd0"), rgb("#f2e08a"))


def white_flowers(seed=321):
    return flowers(seed, rgb("#f3eee2"), rgb("#e6b84a"))


def mushrooms(seed=322, cap=rgb("#b84a3a"), spots=True):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    shrooms = [(m + a.rng.uniform(-50, 50), m + a.rng.uniform(-50, 50), a.rng.uniform(14, 30)) for _ in range(6)]
    for x, y, r in sorted(shrooms, key=lambda p: p[2]):
        soft_shadow(a, (x, y), r, 4, 5, 0.35, 4)
        a.shape(ellipse(x, y, r, r * 0.92, 32), cap, outline=DETAIL * (1.1 if r > 20 else 0.9), depth=r * 0.25, light_k=0.5, mottle=0)
        if spots:
            for _ in range(int(r / 5)):
                t, d = a.rng.uniform(0, 6.28), a.rng.uniform(0, r * 0.65)
                dot(a, x + d * math.cos(t), y + d * math.sin(t), a.rng.uniform(1.6, 3.2), rgb("#f3ead8"))
    return a.image()


def brown_mushrooms(seed=323):
    return mushrooms(seed, rgb("#a8845a"), spots=False)


def reeds(seed=324):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    blades(a, m, m, 18, 100, [rgb("#7a9a4a"), rgb("#9aa85a"), GREEN_D], width=6)
    for _ in range(6):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(30, 80)
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        a.shape(ellipse(x, y, 6, 14, 16, rot=t), rgb("#6e4a2f"), outline=FINE * 1.2, depth=2, light_k=0.3, mottle=0)
    return a.image()


def clover(seed=325):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    for _ in range(14):
        t, d = a.rng.uniform(0, 6.28), 70 * math.sqrt(a.rng.random())
        x, y = m + d * math.cos(t), m + d * math.sin(t)
        rot = a.rng.uniform(0, 6.28)
        for k in range(3):
            pa = rot + 2 * math.pi * k / 3
            a.shape(ellipse(x + 8 * math.cos(pa), y + 8 * math.sin(pa), 8, 8, 16), vary(a.rng, GREEN_L, 0.05), outline=FINE * 1.1, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)
    return a.image()


def vines(seed=326):
    w, h = 400, 220
    a = Art(w, h, seed)
    for k in range(3):
        pts = wavy(20, 40 + k * 70, w - 20, 60 + k * 60, a.rng, 30, 22)
        a.ink(pts, 6, color=INK, taper=True)
        a.ink(pts, 3.5, color=rgb("#5a6a2e"), taper=True)
        for j in range(2, 29, 3):
            x, y = pts[j]
            leaf(a, x + a.rng.uniform(-10, 10), y + a.rng.uniform(-10, 10), 24, vary(a.rng, GREEN, 0.06))
    return a.image()


def puddle(seed=327):
    w, h = 300, 200
    a = Art(w, h, seed)
    water = rgb("#7aa3b4")

    def glints(art, p):
        art.ink([(100, 70), (150, 64)], FINE * 1.5, color=rgb("#e4f2f6"), alpha=0.9)
        art.ink([(160, 120), (200, 116)], FINE * 1.3, color=rgb("#e4f2f6"), alpha=0.8)

    a.shape(blob(w / 2, h / 2, 130, a.rng, 11, 0.14, ry=80), water, outline=DETAIL, smooth=True, depth=8, shade_k=0, light_k=0, ao=0.5, detail=glints)
    return a.image()


NATURE = {
    "Fallen Log": fallen_log,
    "Mossy Log": mossy_log,
    "Hollow Log": hollow_log,
    "Fallen Branch": branch,
    "Twigs": twigs,
    "Pine Cone": pine_cone,
    "Autumn Leaf Pile": leaf_pile,
    "Green Leaf Pile": green_leaf_pile,
    "Fallen Leaves": scattered_leaves,
    "Dry Leaves": dry_leaves,
    "Leaf": single_leaf,
    "Pebbles": pebbles,
    "River Stones": river_stones,
    "Stepping Stone": stepping_stone,
    "Grass Tuft": grass_tuft,
    "Tall Grass": tall_grass,
    "Fern": fern,
    "Yellow Flowers": flowers,
    "Red Flowers": red_flowers,
    "Blue Flowers": blue_flowers,
    "White Flowers": white_flowers,
    "Red Mushrooms": mushrooms,
    "Brown Mushrooms": brown_mushrooms,
    "Reeds": reeds,
    "Clover": clover,
    "Vines": vines,
    "Puddle": puddle,
}
