"""Trees: leafy canopies in several colors (and a recolorable one), pines,
palms, a bare tree and a cut stump. Same pen style as objects.py."""

import math

import skia

from kit import WOOD, WOOD_DARK, WOOD_LIGHT
from objects import scallop
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


N_ANG = 360


def organic_radius(rng, R, lobes=(3, 7), stretch=(1.0, 1.12), reach=(0.08, 0.28)):
    """An irregular, star-shaped outline as radius-per-degree: a core plus
    random lobes (some far out, making arms), maybe stretched one way,
    smoothed so there are no creases. Peaks at about R."""
    core = R * rng.uniform(0.62, 0.72)
    ls = []
    for _ in range(rng.randint(*lobes)):
        ang = rng.uniform(0, 2 * math.pi)
        d = R * rng.uniform(*reach)
        ls.append((d * math.cos(ang), d * math.sin(ang), R * rng.uniform(0.45, 0.6)))
    k = rng.uniform(*stretch)
    rot = rng.uniform(0, math.pi)
    rs = []
    for i in range(N_ANG):
        ang = 2 * math.pi * i / N_ANG
        ux, uy = math.cos(ang), math.sin(ang)
        best = core
        for lx, ly, lr in ls:
            bb = lx * ux + ly * uy
            disc = lr * lr - (lx * lx + ly * ly) + bb * bb
            if disc >= 0:
                best = max(best, bb + math.sqrt(disc))
        # Stretch along `rot`.
        c = math.cos(ang - rot)
        best *= 1 + (k - 1) * c * c
        rs.append(best)
    for _ in range(3):  # smooth (circular moving average)
        rs = [(rs[i - 2] + rs[i - 1] * 2 + rs[i] * 3 + rs[(i + 1) % N_ANG] * 2 + rs[(i + 2) % N_ANG]) / 9 for i in range(N_ANG)]
    top = max(rs)
    return [r * R / top for r in rs]


def r_at(rs, ang):
    f = (ang % (2 * math.pi)) / (2 * math.pi) * N_ANG
    i = int(f)
    t = f - i
    return rs[i % N_ANG] * (1 - t) + rs[(i + 1) % N_ANG] * t


def bumpy_ring(rng, cx, cy, rs, scale, start, span, bump_len, height, sizes=(0.7, 1.3)):
    """Points along the outline scaled by `scale`, from angle `start` over
    `span`, with outward bumps about `bump_len` long (each a bit different)."""
    pts = []
    ang = start
    end = start + span
    while ang < end - 1e-6:
        r = r_at(rs, ang) * scale
        w = bump_len * rng.uniform(*sizes) / max(r, 1)  # bump width in radians
        w = min(w, end - ang)
        h = height * rng.uniform(*sizes)
        steps = max(4, int(w * r / 3))
        for j in range(steps):
            t = ang + w * j / steps
            rr = r_at(rs, t) * scale + h * math.sin(math.pi * j / steps)
            pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
        ang += w
    rr = r_at(rs, end) * scale
    pts.append((cx + rr * math.cos(end), cy + rr * math.sin(end)))
    return pts


def leafy(seed, palette, size=720, bump=(0.12, 0.2), rings=(0.8, 0.6, 0.4, 0.2), lobes=(3, 7), stretch=(1.0, 1.12), reach=(0.08, 0.28)):
    """A broadleaf tree: an irregular organic canopy with a bumpy edge, pen
    lines following its shape inward (scaled outlines), lit top-left."""
    greens, ink = palette
    dark, mid, light = greens
    a = Art(size, size, seed)
    cx = cy = size / 2
    R = size * 0.42
    rs = organic_radius(a.rng, R, lobes, stretch, reach)
    bl = R * a.rng.uniform(*bump)
    edge = bumpy_ring(a.rng, cx, cy, rs, 1 / 1.06, 0, 2 * math.pi, bl, bl * 0.32)

    def inside(art, path):
        glow = skia.Path()
        glow.addCircle(cx - R * 0.25, cy - R * 0.25, R * 0.55)
        art.fill_path(glow, light, 0.55, blur=R * 0.18)
        dim = skia.Path()
        dim.addCircle(cx + R * 0.45, cy + R * 0.45, R * 0.6)
        art.fill_path(dim, dark, 0.45, blur=R * 0.2)
        for scale in rings:
            ang = art.rng.uniform(0, 2 * math.pi)
            end = ang + 2 * math.pi - 0.15
            while ang < end:
                span = min(end - ang, art.rng.uniform(0.5, 1.6) * (1.2 - scale * 0.6))
                lb = bl * (0.6 + scale * 0.5)
                pts = bumpy_ring(art.rng, cx, cy, rs, scale * art.rng.uniform(0.95, 1.05), ang, span, lb, lb * 0.3)
                if len(pts) > 3:
                    art.ink(pts, DETAIL * art.rng.uniform(0.6, 1.0), color=ink, alpha=art.rng.uniform(0.55, 0.85), wob=0.4)
                ang += span + art.rng.uniform(0.12, 0.5)
        for _ in range(int(R * 0.2)):
            ang = art.rng.uniform(0, 6.28)
            d = r_at(rs, ang) * math.sqrt(art.rng.uniform(0, 0.75))
            x, y = cx + d * math.cos(ang), cy + d * math.sin(ang)
            t = art.rng.uniform(0.2, 1.4)
            art.ink([(x, y), (x + 7 * math.cos(t), y + 7 * math.sin(t))], FINE, color=ink, alpha=0.4, wob=0.1)

    a.shape(edge, mid, outline=OUTLINE, corner=0, wob=0.6, depth=R * 0.1, shade_k=0.5, light_k=0.25, ao=0.35, mottle=0.06, detail=inside)
    return a.image()


def spiky_ring(rng, cx, cy, rs, scale, start, span, tooth, height):
    """Needle zigzag along the outline scaled by `scale`: teeth of uneven
    width and height pointing outward."""
    pts = []
    ang = start
    end = start + span
    while ang < end - 1e-6:
        r = r_at(rs, ang) * scale
        w = min(tooth * rng.uniform(0.6, 1.4) / max(r, 1), end - ang)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        ta = ang + w * rng.uniform(0.35, 0.65)
        tr_ = r_at(rs, ta) * scale + height * rng.uniform(0.6, 1.4)
        pts.append((cx + tr_ * math.cos(ta), cy + tr_ * math.sin(ta)))
        ang += w
    r = r_at(rs, end) * scale
    pts.append((cx + r * math.cos(end), cy + r * math.sin(end)))
    return pts


def pine(seed=31, size=640, colors=(rgb("#2c5233"), rgb("#3f6e44"), rgb("#6a9a64")), ink=rgb("#142218"), rings=(0.8, 0.62, 0.44, 0.26)):
    """A conifer from above: one irregular canopy with a needle-tipped edge;
    inside, only pen lines: concentric needle zigzags following its shape and
    short needle strokes, lit top-left."""
    dark, mid, light = colors
    a = Art(size, size, seed)
    cx = cy = size / 2
    R = size * 0.42
    rs = organic_radius(a.rng, R, lobes=(3, 6), stretch=(1.0, 1.1))
    tooth = R * a.rng.uniform(0.07, 0.1)
    edge = spiky_ring(a.rng, cx, cy, rs, 1 / 1.08, 0, 2 * math.pi, tooth, tooth * 0.75)

    def inside(art, path):
        glow = skia.Path()
        glow.addCircle(cx - R * 0.25, cy - R * 0.25, R * 0.55)
        art.fill_path(glow, light, 0.5, blur=R * 0.18)
        dim = skia.Path()
        dim.addCircle(cx + R * 0.45, cy + R * 0.45, R * 0.6)
        art.fill_path(dim, dark, 0.5, blur=R * 0.2)
        for scale in rings:
            ang = art.rng.uniform(0, 2 * math.pi)
            end = ang + 2 * math.pi - 0.12
            while ang < end:
                span = min(end - ang, art.rng.uniform(0.4, 1.3) * (1.2 - scale * 0.5))
                tt = tooth * (0.55 + scale * 0.5)
                pts = spiky_ring(art.rng, cx, cy, rs, scale * art.rng.uniform(0.95, 1.05), ang, span, tt, tt * 0.7)
                if len(pts) > 3:
                    art.ink(pts, DETAIL * art.rng.uniform(0.55, 0.9), color=ink, alpha=art.rng.uniform(0.55, 0.85), wob=0.2)
                ang += span + art.rng.uniform(0.1, 0.45)
        # Short needle strokes, mostly radial.
        for _ in range(int(R * 0.45)):
            ang = art.rng.uniform(0, 6.28)
            d = r_at(rs, ang) * math.sqrt(art.rng.uniform(0.02, 0.85))
            x, y = cx + d * math.cos(ang), cy + d * math.sin(ang)
            t = ang + art.rng.uniform(-0.5, 0.5)
            ln = art.rng.uniform(6, 12)
            art.ink([(x, y), (x + ln * math.cos(t), y + ln * math.sin(t))], FINE * 0.9, color=ink, alpha=0.45, wob=0.1)

    a.shape(edge, mid, outline=OUTLINE, corner=0, wob=0.4, depth=R * 0.1, shade_k=0.5, light_k=0.25, ao=0.35, mottle=0.05, detail=inside)
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


def dead_tree(seed=33, size=640):
    """A bare tree from above: limbs that wander and thin out gradually,
    forking at their ends (their thickness carries into the forks), with the
    last twigs as fine pen strokes."""
    from pen import normals

    a = Art(size, size, seed)
    m = size / 2
    bark = rgb("#7a624c")
    limbs = []  # (width, polygon, spine)
    twigs = []  # (spine, width)

    def grow(x, y, ang, L, w0, depth):
        w1 = w0 * a.rng.uniform(0.55, 0.68)
        n = 12
        spine, widths = [(x, y)], [w0]
        turn = a.rng.gauss(0, 0.04)
        for j in range(1, n + 1):
            turn += a.rng.gauss(0, 0.05)
            turn *= 0.85
            ang += turn
            px, py = spine[-1]
            spine.append((px + L / n * math.cos(ang), py + L / n * math.sin(ang)))
            widths.append(w0 + (w1 - w0) * j / n)
        if w0 < 5:
            twigs.append((spine, w0))
        else:
            ns = normals(spine, False)
            left = [(px + nx * w / 2, py + ny * w / 2) for (px, py), (nx, ny), w in zip(spine, ns, widths)]
            right = [(px - nx * w / 2, py - ny * w / 2) for (px, py), (nx, ny), w in zip(spine, ns, widths)]
            tip = spine[-1]
            # A round end, so the forks grow out of it smoothly.
            cap = [(tip[0] + math.cos(ang + t) * w1 / 2, tip[1] + math.sin(ang + t) * w1 / 2) for t in [math.pi / 2 - math.pi * k / 6 for k in range(7)]]
            limbs.append((w0, left + cap + right[::-1], spine))
        if depth >= 4 or w1 < 2.2:
            return
        forks = 2 if a.rng.random() < 0.85 else 3
        spread = a.rng.uniform(0.35, 0.6)
        for k in range(forks):
            off = spread * (k - (forks - 1) / 2) * (2 / max(1, forks - 1)) + a.rng.uniform(-0.15, 0.15)
            grow(spine[-1][0], spine[-1][1], ang + off, L * a.rng.uniform(0.62, 0.78), w1 * a.rng.uniform(0.75, 0.9), depth + 1)
        if depth < 2 and a.rng.random() < 0.4:
            j = a.rng.randint(4, 8)
            side = a.rng.choice((-1, 1))
            bx, by = spine[j]
            grow(bx, by, ang + side * a.rng.uniform(0.6, 1.0), L * 0.5, widths[j] * 0.55, depth + 2)

    count = a.rng.randint(4, 6)
    rot = a.rng.uniform(0, 6.28)
    for i in range(count):
        ang = rot + 2 * math.pi * i / count + a.rng.uniform(-0.25, 0.25)
        grow(m, m, ang, size * a.rng.uniform(0.15, 0.19), a.rng.uniform(36, 46), 0)
    for spine, w in twigs:
        a.ink(spine, w + 0.6, color=shade(bark, 0.65), alpha=0.95, taper=True, wob=0.2, var=0.1)
    # Thinnest first, so thicker limbs cover their forks.
    for w0, poly, spine in sorted(limbs, key=lambda l: l[0]):

        def grain(art, path, spine=spine, w0=w0):
            if w0 > 12:
                art.ink(spine[1:-1], FINE, color=shade(bark, 0.45), alpha=0.7, wob=0.3)

        a.shape(poly, bark, outline=DETAIL * (1.25 if w0 > 20 else 0.95), corner=0, wob=0.15, depth=3, shade_k=0.4, light_k=0.25, ao=0.0, mottle=0)
    a.shape(scallop(m, m, 40, a.rng, 9, 0.08), bark, outline=OUTLINE, corner=0, depth=7)
    for rr in (12, 24):
        a.ink(scallop(m + 2, m + 2, rr, a.rng, 7, 0.05), FINE * 1.1, closed=True, color=shade(bark, 0.5), alpha=0.75)
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
    "Oak Tree": lambda: leafy(16, OAK, reach=(0.02, 0.1)),
    "Wide Oak": lambda: leafy(51, OAK, size=780, lobes=(5, 8), stretch=(1.1, 1.2)),
    "Forest Tree": lambda: leafy(42, DEEP, bump=(0.08, 0.13), reach=(0.02, 0.1)),
    "Twin Crown Tree": lambda: leafy(52, OAK, lobes=(2, 2), stretch=(1.15, 1.25), reach=(0.25, 0.32)),
    "Autumn Tree": lambda: leafy(43, AUTUMN, bump=(0.15, 0.24)),
    "Crimson Tree": lambda: leafy(44, CRIMSON, lobes=(4, 6), rings=(0.78, 0.52, 0.26), reach=(0.02, 0.12)),
    "Birch Tree": lambda: leafy(45, BIRCH, size=560, bump=(0.09, 0.14)),
    "Blossom Tree": lambda: leafy(46, BLOSSOM, size=620, bump=(0.16, 0.26), reach=(0.02, 0.1)),
    "Young Tree": lambda: leafy(53, OAK, size=420, rings=(0.7, 0.35), reach=(0.02, 0.1)),
    "Colorable Tree": lambda: leafy(47, COLORABLE, reach=(0.02, 0.12)),
    "Pine Tree": pine,
    "Tall Pine": lambda: pine(36, size=700, colors=(rgb("#23462e"), rgb("#33603c"), rgb("#55845a"))),
    "Small Pine": lambda: pine(35, size=420),
    "Palm Tree": palm,
    "Dead Tree": dead_tree,
    "Tree Stump": stump,
}

TREES_COLORABLE = {"Colorable Tree"}
