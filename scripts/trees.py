"""Trees: leafy canopies in several colors (and a recolorable one), pines,
palms, a bare tree and a cut stump. Same pen style as objects.py."""

import math

import skia

from kit import WOOD, WOOD_DARK, WOOD_LIGHT
from objects import canopy, scallop
from pen import DETAIL, FINE, INK, OUTLINE, Art, chaikin, ellipse, mix, rgb, shade, tint, vary

# (dark, mid, light), ink
OAK = ((rgb("#3b6629"), rgb("#5a8a38"), rgb("#86b04f")), rgb("#1d2e15"))
DEEP = ((rgb("#24452a"), rgb("#36603a"), rgb("#58855a")), rgb("#132216"))
AUTUMN = ((rgb("#9a4d1e"), rgb("#cc7a2c"), rgb("#eab25a")), rgb("#3c1f0e"))
CRIMSON = ((rgb("#7a2622"), rgb("#a83a2e"), rgb("#d26a4c")), rgb("#2e110e"))
BIRCH = ((rgb("#9a9a2c"), rgb("#c8c24a"), rgb("#ece17c")), rgb("#3a3812"))
BLOSSOM = ((rgb("#b8607a"), rgb("#e090a6"), rgb("#f7c6d2")), rgb("#4a2030"))
# Recolorable: reds with g == b (the editor swaps them for the chosen color).
COLORABLE = ((rgb("#7a1c1c"), rgb("#b02a2a"), rgb("#dc5050")), rgb("#2c2222"))


def leafy(seed, palette, size=720, bumps=13):
    greens, ink = palette
    a = Art(size, size, seed)
    canopy(a, size / 2, size / 2, size * 0.4, greens, ink, bumps=bumps)
    return a.image()


def pine(seed=31, size=640, colors=(rgb("#2c5233"), rgb("#3f6e44"), rgb("#6a9a64")), ink=rgb("#142218")):
    """A conifer from above: three stacked layers of boughs (uneven, rounded
    stars), each smaller, lighter and turned a little, with needle strokes."""
    a = Art(size, size, seed)
    m = size / 2
    R = size * 0.43
    dark, mid, light = colors
    for k, (scale, n, col) in enumerate(((1.0, 11, dark), (0.7, 9, mid), (0.42, 7, light))):
        r = R * scale
        rot = a.rng.uniform(0, 6.28)
        pts, tips = [], []
        for i in range(n):
            a0 = rot + 2 * math.pi * i / n + a.rng.uniform(-0.1, 0.1)
            a1 = rot + 2 * math.pi * (i + 0.5) / n
            r0 = r * a.rng.uniform(0.86, 1.04)
            tips.append((a0, r0))
            pts.append((m + r0 * math.cos(a0), m + r0 * math.sin(a0)))
            pts.append((m + r * 0.62 * math.cos(a1), m + r * 0.62 * math.sin(a1)))
        pts = chaikin(pts, True, 1)

        def needles(art, path, r=r, tips=tips):
            for a0, r0 in tips:
                # The bough's midrib and its needles.
                art.ink([(m + r * 0.2 * math.cos(a0), m + r * 0.2 * math.sin(a0)), (m + r0 * 0.88 * math.cos(a0), m + r0 * 0.88 * math.sin(a0))], FINE * 1.2, color=ink, alpha=0.6, wob=0.3)
                for f in (0.45, 0.62, 0.78):
                    bx, by = m + r0 * f * math.cos(a0), m + r0 * f * math.sin(a0)
                    for side in (-1, 1):
                        ang = a0 + side * 0.75
                        art.ink([(bx, by), (bx + math.cos(ang) * r * 0.09, by + math.sin(ang) * r * 0.09)], FINE * 0.9, color=ink, alpha=0.45, wob=0.1)

        a.shape(pts, col, outline=OUTLINE if k == 0 else DETAIL * 1.1, corner=0, wob=0.5, depth=r * 0.1, shade_k=0.5, light_k=0.25, ao=0.35, mottle=0.05, detail=needles)
    a.shape(ellipse(m, m, R * 0.06, R * 0.06, 24), rgb("#6d5040"), outline=DETAIL, depth=3, mottle=0)
    return a.image()


def palm(seed=32, size=620):
    a = Art(size, size, seed)
    m = size / 2
    R = size * 0.46
    green, dark = rgb("#5f9a3e"), rgb("#2f5320")
    n = 9
    rot = a.rng.uniform(0, 6.28)
    for i in range(n):
        ang = rot + 2 * math.pi * i / n + a.rng.uniform(-0.12, 0.12)
        L = R * a.rng.uniform(0.85, 1.0)
        bend = a.rng.uniform(-0.25, 0.25)
        spine = []
        for j in range(13):
            t = j / 12
            aa = ang + bend * t * t
            spine.append((m + L * t * math.cos(aa), m + L * t * math.sin(aa)))
        left, right = [], []
        for j, (x, y) in enumerate(spine):
            t = j / 12
            aa = ang + bend * t * t
            w = R * 0.15 * math.sin(math.pi * min(1, t * 1.1)) + 1
            # Serrated sides: leaflets.
            w *= 0.85 if j % 2 else 1.1
            nx, ny = -math.sin(aa), math.cos(aa)
            left.append((x + nx * w, y + ny * w))
            right.append((x - nx * w, y - ny * w))
        frond = left + right[::-1]

        def rib(art, path, spine=spine):
            art.ink(spine, DETAIL * 0.8, color=dark, alpha=0.9, wob=0.2)
            for j in range(2, 12):
                x, y = spine[j]
                px, py = spine[j - 1]
                ang2 = math.atan2(y - py, x - px)
                for side in (-1, 1):
                    art.ink([(x, y), (x + math.cos(ang2 + side * 1.0) * R * 0.11, y + math.sin(ang2 + side * 1.0) * R * 0.11)], FINE, color=dark, alpha=0.55, wob=0.1)

        a.shape(frond, vary(a.rng, green, 0.06), outline=DETAIL * 1.4, corner=0, wob=0.3, depth=8, shade_k=0.45, light_k=0.3, ao=0.15, detail=rib)
    a.shape(ellipse(m, m, R * 0.09, R * 0.09, 32), rgb("#8a6a43"), outline=DETAIL * 1.3, depth=4)
    return a.image()


def dead_tree(seed=33, size=620):
    a = Art(size, size, seed)
    m = size / 2
    bark = rgb("#7a624c")
    strokes = []

    def branch(x, y, ang, L, w, depth):
        ex, ey = x + L * math.cos(ang), y + L * math.sin(ang)
        mx = (x + ex) / 2 + a.rng.uniform(-10, 10)
        my = (y + ey) / 2 + a.rng.uniform(-10, 10)
        strokes.append((chaikin([(x, y), (mx, my), (ex, ey)], False, 2), w))
        if depth > 0:
            for d in (-1, 1):
                if a.rng.random() < 0.9:
                    branch(ex, ey, ang + d * a.rng.uniform(0.35, 0.6), L * a.rng.uniform(0.55, 0.7), w * 0.62, depth - 1)

    for i in range(5):
        ang = 2 * math.pi * i / 5 + a.rng.uniform(-0.25, 0.25)
        branch(m, m, ang, size * a.rng.uniform(0.2, 0.25), 26, 2)
    # All the ink first, then all the bark, so branches merge at the forks.
    seed_ = a.rng.getstate()
    for pts, w in strokes:
        a.ink(pts, w + 7, color=INK, taper=True, wob=0.0, var=0.0)
    for pts, w in strokes:
        a.ink(pts, w, color=bark, taper=True, wob=0.0, var=0.0)
        a.ink(pts, max(1.5, w * 0.18), color=shade(bark, 0.45), alpha=0.7, taper=True, wob=0.3)
    a.rng.setstate(seed_)
    a.shape(ellipse(m, m, 40, 40, 40), bark, outline=OUTLINE, depth=7)
    a.ink(ellipse(m + 2, m + 2, 18, 18, 24), FINE * 1.2, closed=True, color=shade(bark, 0.5), alpha=0.8)
    return a.image()


def stump(seed=34, size=300):
    """A cut tree trunk: bark rim with roots, the sawn face with growth rings."""
    a = Art(size, size, seed)
    m = size / 2
    bark = rgb("#6d5040")
    # Roots spreading out under the trunk.
    for i in range(5):
        ang = 2 * math.pi * i / 5 + a.rng.uniform(-0.3, 0.3)
        L = size * a.rng.uniform(0.36, 0.45)
        ux, uy = math.cos(ang), math.sin(ang)
        nx, ny = -uy, ux
        w = size * 0.1
        L *= 0.85
        root = [(m + nx * w, m + ny * w), (m + ux * L * 0.65 + nx * w * 0.75, m + uy * L * 0.65 + ny * w * 0.75), (m + ux * L + nx * w * 0.35, m + uy * L + ny * w * 0.35), (m + ux * L * 1.05, m + uy * L * 1.05), (m + ux * L - nx * w * 0.35, m + uy * L - ny * w * 0.35), (m + ux * L * 0.65 - nx * w * 0.75, m + uy * L * 0.65 - ny * w * 0.75), (m - nx * w, m - ny * w)]
        a.shape(chaikin(root, True, 3), shade(bark, 0.1), outline=OUTLINE * 0.9, corner=0, depth=6)
    R = size * 0.3

    def bark_lines(art, path):
        for i in range(22):
            ang = 2 * math.pi * i / 22 + art.rng.uniform(-0.05, 0.05)
            art.ink([(m + R * 0.82 * math.cos(ang), m + R * 0.82 * math.sin(ang)), (m + R * 1.05 * math.cos(ang), m + R * 1.05 * math.sin(ang))], FINE * 1.2, color=shade(bark, 0.55), alpha=0.85, wob=0.3)

    a.shape(scallop(m, m, R, a.rng, 14, 0.05), bark, outline=OUTLINE, corner=0, depth=8, detail=bark_lines)
    face = WOOD_LIGHT

    def rings(art, path):
        for k, rr in enumerate((0.15, 0.3, 0.45, 0.6)):
            art.ink(scallop(m + 2, m + 1, R * 0.8 * rr / 0.6 * 0.95, art.rng, 9, 0.03), FINE * 1.2, closed=True, color=shade(face, 0.45), alpha=0.75, wob=0.6)
        ang = art.rng.uniform(0, 6.28)
        art.ink([(m + R * 0.1 * math.cos(ang), m + R * 0.1 * math.sin(ang)), (m + R * 0.72 * math.cos(ang + 0.1), m + R * 0.72 * math.sin(ang + 0.1))], DETAIL * 0.8, alpha=0.85, wob=0.5)
        dot = skia.Path()
        dot.addCircle(m + 2, m + 1, 3)
        art.fill_path(dot, shade(face, 0.5), 0.9)

    a.shape(scallop(m, m, R * 0.8, a.rng, 11, 0.03), face, outline=DETAIL * 1.2, corner=0, depth=6, shade_k=0.25, light_k=0.3, ao=0.25, detail=rings)
    return a.image()


TREES = {
    "Oak Tree": lambda: leafy(16, OAK),
    "Round Tree": lambda: leafy(41, OAK, size=560, bumps=10),
    "Forest Tree": lambda: leafy(42, DEEP, bumps=15),
    "Autumn Tree": lambda: leafy(43, AUTUMN),
    "Crimson Tree": lambda: leafy(44, CRIMSON, bumps=11),
    "Birch Tree": lambda: leafy(45, BIRCH, size=600, bumps=12),
    "Blossom Tree": lambda: leafy(46, BLOSSOM, size=620, bumps=12),
    "Colorable Tree": lambda: leafy(47, COLORABLE),
    "Pine Tree": pine,
    "Small Pine": lambda: pine(35, size=420),
    "Palm Tree": palm,
    "Dead Tree": dead_tree,
    "Tree Stump": stump,
}

TREES_COLORABLE = {"Colorable Tree"}
