"""More recolorable patterns (seamless, 256 px = 1 tile). The parts that take
the Pattern tool's color are pure reds (g == b) on the neutral grout, like
floors.P_RED; darker/lighter reds give shading that still recolors."""

import math

from floors import P_GROUT, P_RED, inset, voronoi_cells
from pen import DETAIL, FINE, JOINT, JOINT_ALPHA, Art, chaikin, ellipse, rect

T = 256
RED = P_RED
RED_D = (150, 30, 30)
RED_L = (214, 88, 88)
# Joint line between tiles/bricks/planks: a dark red (g == b) so it recolors
# with the pieces, thin, instead of an ink trench around every piece.
RED_J = (118, 26, 26)


def pat(seed, size=T, bg=P_GROUT):
    return Art(size, size, seed, tile=True, bg=bg)


def ps(a, pts, col=RED, out=2.4, corner=3, smooth=False, shade_k=0.4, light_k=0.0, joint=False):
    if joint:
        a.shape(pts, col, outline=JOINT, outline_color=RED_J, outline_alpha=JOINT_ALPHA, corner=corner, smooth=smooth, wob=0.3, depth=3, shade_k=shade_k * 0.85, light_k=light_k, ao=0.1, mottle=0.0)
    else:
        a.shape(pts, col, outline=out, corner=corner, smooth=smooth, wob=0.35, depth=3, shade_k=shade_k, light_k=light_k, ao=0.15, mottle=0.0)


def ring(a, pts, col=RED, w=DETAIL * 1.6):
    a.ink(pts, w, closed=True, color=col, wob=0.3, var=0.06)


def line(a, pts, col=RED, w=DETAIL * 1.6, closed=False):
    a.ink(pts, w, closed=closed, color=col, wob=0.3, var=0.06, taper=False)


def rot(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def poly(cx, cy, r, n, ang=0.0):
    return [(cx + r * math.cos(ang + 2 * math.pi * k / n), cy + r * math.sin(ang + 2 * math.pi * k / n)) for k in range(n)]


def star(cx, cy, r0, r1, n, ang=-math.pi / 2):
    out = []
    for k in range(2 * n):
        r = r0 if k % 2 == 0 else r1
        t = ang + math.pi * k / n
        out.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return out


def done(a):
    return a.image(grain=0.02)


# -- tile layouts --------------------------------------------------------------------------------


def grid(seed, n=4, gap=3.5, corner=5, alt=None, size=T):
    a = pat(seed, size)
    cell = size / n
    gap = min(gap, 2.0)
    for i in range(n):
        for j in range(n):
            col = alt if alt and (i + j) % 2 else RED
            ps(a, rect(i * cell + gap, j * cell + gap, (i + 1) * cell - gap, (j + 1) * cell - gap), col, corner=corner, joint=True)
    return done(a)


def bond(seed, rows=8, per=4, shift=0.5, gap=2.5, alt=False):
    """Running/stack bond bricks: `per` bricks per row, rows offset by `shift`."""
    a = pat(seed)
    h = T / rows
    gap = min(gap, 1.5)
    w = T / per
    for j in range(rows):
        off = (j * shift % 1) * w
        for i in range(-1, per + 1):
            x0 = i * w + off
            col = RED_D if alt and (i + j) % 3 == 0 else RED
            ps(a, rect(x0 + gap, j * h + gap, x0 + w - gap, (j + 1) * h - gap), col, corner=2, joint=True)
    return done(a)


def flemish(seed):
    """Flemish bond: long and short bricks alternating, rows offset."""
    a = pat(seed)
    rows = 8
    h = T / rows
    u = T / 6  # long = u, short = u/2 -> pairs of 1.5u, 4 pairs per row
    for j in range(rows):
        x = -u * 0.75 if j % 2 else 0
        while x < T + u:
            ps(a, rect(x + 1.5, j * h + 1.5, x + u - 1.5, (j + 1) * h - 1.5), RED, corner=2, joint=True)
            ps(a, rect(x + u + 1.5, j * h + 1.5, x + 1.5 * u - 1.5, (j + 1) * h - 1.5), RED_D, corner=2, joint=True)
            x += 1.5 * u
    return done(a)


def pinwheel(seed, n=2):
    """Pinwheel: a small square framed by four rectangles turning around it."""
    a = pat(seed)
    P = T / n
    s = P / 4  # small square side
    L = P - s  # long side of each rectangle
    W = s * 3 / 2 if False else (P - s) / 2  # rectangles are L x (P-s)/... keep simple
    for i in range(n):
        for j in range(n):
            x0, y0 = i * P, j * P
            # 4 rectangles L x s around a central square, rotating.
            q = (P - s) / 2
            pieces = [
                rect(x0, y0, x0 + q + s, y0 + q),
                rect(x0 + q + s, y0, x0 + P, y0 + q + s),
                rect(x0 + q, y0 + q + s, x0 + P, y0 + P),
                rect(x0, y0 + q, x0 + q, y0 + P),
            ]
            for k, pc in enumerate(pieces):
                ps(a, [(px + (1.5 if px < x0 + P / 2 else -1.5), py + (1.5 if py < y0 + P / 2 else -1.5)) for px, py in pc], RED if k % 2 else RED_D, corner=3, joint=True)
            ps(a, rect(x0 + q + 1.5, y0 + q + 1.5, x0 + q + s - 1.5, y0 + q + s - 1.5), RED_L, corner=2, joint=True)
    return done(a)


def hopscotch(seed):
    """Hopscotch: 2x2 squares with 1x1 squares, lattice (2,1),(-1,2)."""
    a = pat(seed)
    u = T / 5
    for i in range(-4, 6):
        for j in range(-4, 6):
            ox, oy = (2 * i - j) * u, (i + 2 * j) * u
            if ox < -3 * u or ox > T + u or oy < -3 * u or oy > T + u:
                continue
            ps(a, rect(ox + 1.8, oy + 1.8, ox + 2 * u - 1.8, oy + 2 * u - 1.8), RED, corner=4, joint=True)
            ps(a, rect(ox + 2 * u + 1.8, oy + 1.8, ox + 3 * u - 1.8, oy + u - 1.8), RED_D, corner=2, joint=True)
    return done(a)


def basket(seed, units=4, k=2, gap=2.5):
    """Basketweave of `k` slats per block, `units` blocks per side."""
    a = pat(seed)
    b = T / units
    u = b / k
    gap = min(gap, 1.5)
    for bi in range(units):
        for bj in range(units):
            x0, y0 = bi * b, bj * b
            hor = (bi + bj) % 2 == 0
            for m in range(k):
                if hor:
                    r = rect(x0 + gap, y0 + m * u + gap, x0 + b - gap, y0 + (m + 1) * u - gap)
                else:
                    r = rect(x0 + m * u + gap, y0 + gap, x0 + (m + 1) * u - gap, y0 + b - gap)
                ps(a, r, RED if m % 2 == 0 else RED_D, corner=2, joint=True)
    return done(a)


def herring45(seed, n=8):
    """Classic 45-degree herringbone: 2x1 slats in a staircase (H at k(1,1),
    V beside it), rows repeated by (2,-2), all turned 45 degrees so the
    lattice is axis-aligned and tiles at T."""
    a = pat(seed)
    u = T / (math.sqrt(2) * n)
    r2 = math.sqrt(2)

    def tr(x, y):
        return ((x - y) / r2 * u, (x + y) / r2 * u)

    g = 1.4
    for k in range(-2 * n, 2 * n + 1):
        for m in range(-n, n + 1):
            ox, oy = k + 2 * m, k - 2 * m
            for bx, by, bw, bh, col in ((0, 0, 2, 1, RED), (-1, 0, 1, 2, RED_D)):
                corners = [tr(ox + bx, oy + by), tr(ox + bx + bw, oy + by), tr(ox + bx + bw, oy + by + bh), tr(ox + bx, oy + by + bh)]
                xs = [c[0] for c in corners]
                ys = [c[1] for c in corners]
                if max(xs) < -4 or min(xs) > T + 4 or max(ys) < -4 or min(ys) > T + 4:
                    continue
                cx, cy = sum(xs) / 4, sum(ys) / 4
                shrunk = [(cx + (x - cx) * (1 - g / (u * 1.2)), cy + (y - cy) * (1 - g / (u * 1.2))) for x, y in corners]
                ps(a, shrunk, col, corner=1.5, out=1.8, joint=True)
    return done(a)


def chevron_planks(seed, rows=4):
    """Chevron (V) parquet: slanted slats meeting on a center line."""
    a = pat(seed)
    h = T / rows
    w = T / 2
    for j in range(rows + 1):
        y = j * h
        for i in range(2):
            x = i * w
            left = [(x, y), (x + w / 2, y + h * 0.35), (x + w / 2, y + h * 0.35 + h - 3), (x, y + h - 3)]
            right = [(x + w / 2, y + h * 0.35), (x + w, y), (x + w, y + h - 3), (x + w / 2, y + h * 0.35 + h - 3)]
            ps(a, [(px + 1.5, py + 1.5) for px, py in left], RED, corner=1, out=2.0, joint=True)
            ps(a, [(px - 1.5, py + 1.5) for px, py in right], RED_D, corner=1, out=2.0, joint=True)
    return done(a)


def planks(seed, rows=6, alt=True):
    """Floor planks (the wood takes the color), staggered butt joints."""
    a = pat(seed, bg=(168, 70, 70))
    h = T / rows
    for j in range(rows):
        x = a.rng.uniform(0, T)
        lens = []
        while sum(lens) < T - 1:
            lens.append(a.rng.choice((T / 2, T / 3, T / 4)))
        lens[-1] -= sum(lens) - T
        for ln in lens:
            if ln < 16:
                continue
            col = (RED, RED_D, RED_L)[a.rng.randint(0, 2)] if alt else RED

            def grain(art, p, x=x, y=j * h, ln=ln, col=col):
                for k in range(2):
                    gy = y + h * (0.3 + 0.4 * k)
                    art.ink([(x + 8, gy), (x + ln * 0.6, gy + art.rng.uniform(-1.5, 1.5))], FINE * 0.8, color=(110, 20, 20), alpha=0.5, wob=0.4)

            a.shape(rect(x + 0.8, j * h + 0.8, x + ln - 0.8, (j + 1) * h - 0.8), col, outline=JOINT, outline_color=RED_J, outline_alpha=JOINT_ALPHA, corner=2, wob=0.4, depth=3, shade_k=0.35, light_k=0.0, ao=0.1, mottle=0.0, detail=grain)
            x += ln
    return done(a)


def shingles_pat(seed, rows=8, round_=True):
    a = pat(seed, bg=(120, 96, 80))
    h = T / rows
    w = h * 1.2
    per = max(1, round(T / w))
    w = T / per
    for j in range(rows + 1):
        off = w / 2 if j % 2 else 0
        for i in range(-1, per + 1):
            x = i * w + off
            y = j * h
            if round_:
                pts = [(x + 2, y - h * 0.4), (x + w - 2, y - h * 0.4), (x + w - 2, y + h * 0.4)] + [(x + w / 2 + (w / 2 - 2) * math.cos(t), y + h * 0.4 + h * 0.5 * math.sin(t)) for t in [k * math.pi / 8 for k in range(9)]] + [(x + 2, y + h * 0.4)]
            else:
                pts = [(x + 2, y - h * 0.4), (x + w - 2, y - h * 0.4), (x + w - 2, y + h * 0.5), (x + 2, y + h * 0.5)]
            ps(a, pts, RED if (i + j) % 2 else RED_D, corner=2, out=2.0)
    return done(a)


def cobbles_pat(seed, cols=6, jitter=0.35):
    a = pat(seed)
    for (cx, cy), cell in voronoi_cells(T, T, cols, cols, a.rng, jitter):
        p = inset(cell, 2.0)
        if len(p) > 2:
            col = (RED, RED_D, RED_L)[a.rng.randint(0, 2)]
            ps(a, p, col, corner=6, out=2.2, joint=True)
    return done(a)


def random_mosaic(seed, n=10):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            if a.rng.random() < 0.12:
                continue
            col = (RED, RED_D, RED_L)[a.rng.randint(0, 2)]
            jx, jy = a.rng.uniform(-1.5, 1.5), a.rng.uniform(-1.5, 1.5)
            ps(a, rect(i * cell + 2.0 + jx, j * cell + 2.0 + jy, (i + 1) * cell - 2.0 + jx, (j + 1) * cell - 2.0 + jy), col, corner=2, out=1.6, joint=True)
    return done(a)


# -- geometric -------------------------------------------------------------------------------------


def hexes(seed, cols=4, gap=3.0, mode="fill"):
    a = pat(seed)
    w = T / cols
    r = w / math.sqrt(3)
    rows = int(round(T / (1.5 * r)))
    if rows % 2:
        rows += 1
    rh = T / rows
    r = rh / 1.5
    if mode in ("fill", "three"):
        gap = min(gap, 1.5)
    for j in range(rows + 1):
        for i in range(-1, cols + 1):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * rh
            pts = poly(cx, cy, min(r, w / math.sqrt(3)) - gap, 6, math.pi / 6)
            if mode == "fill":
                ps(a, pts, RED if (i + 2 * j) % 3 else RED_D, corner=2, joint=True)
            elif mode == "ring":
                ring(a, pts)
            elif mode == "dot":
                ps(a, pts, RED, corner=2, out=2.2)
                ps(a, poly(cx, cy, r * 0.32, 6, math.pi / 6), RED_L, corner=1, out=1.6)
            elif mode == "three":
                # Cube illusion: each hex split in 3 rhombi of different reds.
                rr = min(r, w / math.sqrt(3)) - gap
                c = poly(cx, cy, rr, 6, math.pi / 6)
                for k, col in enumerate((RED_L, RED, RED_D)):
                    q = [(cx, cy), c[2 * k], c[(2 * k + 1) % 6], c[(2 * k + 2) % 6]]
                    ps(a, q, col, corner=1, shade_k=0.1, joint=True)
    return done(a)


def triangles_pat(seed, n=4, alt=True):
    """Equilateral-ish triangles: rows of up and down triangles, every other
    row shifted half a triangle (rows == n, so it wraps)."""
    a = pat(seed)
    w = T / n
    h = T / n
    g = 2.2
    for j in range(n):
        y = j * h
        off = w / 2 if j % 2 else 0
        for i in range(-1, n + 1):
            x = i * w + off
            up = [(x + g * 1.6, y + h - g), (x + w / 2, y + g * 1.8), (x + w - g * 1.6, y + h - g)]
            dn = [(x + w / 2 + g * 1.6, y + g), (x + w * 1.5 - g * 1.6, y + g), (x + w, y + h - g * 1.8)]
            ps(a, up, RED, corner=1.5, out=2.0)
            ps(a, dn, RED_D if alt else RED, corner=1.5, out=2.0)
    return done(a)


def rhombus(seed, n=4, ratio=1.6):
    a = pat(seed)
    w = T / n
    h = w * ratio
    rows = max(1, int(round(T / h)))
    h = T / rows
    for j in range(rows + 1):
        for i in range(n + 1):
            for ox, oy in ((0, 0), (w / 2, h / 2)):
                cx, cy = i * w + ox, j * h + oy
                ps(a, [(cx, cy - h / 2 + 1.8), (cx + w / 2 - 1.8, cy), (cx, cy + h / 2 - 1.8), (cx - w / 2 + 1.8, cy)], RED if ox == 0 else RED_D, corner=2, out=2.0, joint=True)
    return done(a)


def stars_pat(seed, n=4, points=6, inner=0.45, fill_gaps=False):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            ps(a, star(cx, cy, cell * 0.44, cell * 0.44 * inner, points), RED, corner=1, out=2.2)
            if fill_gaps:
                ps(a, poly(i * cell, j * cell, cell * 0.12, 4, math.pi / 4), RED_D, corner=1, out=1.6)
    return done(a)


def eight_star_cross(seed):
    """Eight-pointed stars with crosses between them (a tiling)."""
    a = pat(seed)
    n = 2
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            ps(a, star(cx, cy, cell * 0.5 - 3, cell * 0.33, 8, -math.pi / 2), RED, corner=1, out=2.2)
            x, y = i * cell, j * cell
            cr = cell * 0.18
            ps(a, [(x - cr, y - cr * 0.4), (x - cr * 0.4, y - cr * 0.4), (x - cr * 0.4, y - cr), (x + cr * 0.4, y - cr), (x + cr * 0.4, y - cr * 0.4), (x + cr, y - cr * 0.4), (x + cr, y + cr * 0.4), (x + cr * 0.4, y + cr * 0.4), (x + cr * 0.4, y + cr), (x - cr * 0.4, y + cr), (x - cr * 0.4, y + cr * 0.4), (x - cr, y + cr * 0.4)], RED_D, corner=1, out=1.8)
    return done(a)


def crosses_pat(seed, n=4, thick=0.3, kind="greek"):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            r = cell * 0.4
            t = r * thick
            if kind == "greek":
                pts = [(cx - t, cy - r), (cx + t, cy - r), (cx + t, cy - t), (cx + r, cy - t), (cx + r, cy + t), (cx + t, cy + t), (cx + t, cy + r), (cx - t, cy + r), (cx - t, cy + t), (cx - r, cy + t), (cx - r, cy - t), (cx - t, cy - t)]
            elif kind == "x":
                pts = rot([(cx - t, cy - r), (cx + t, cy - r), (cx + t, cy - t), (cx + r, cy - t), (cx + r, cy + t), (cx + t, cy + t), (cx + t, cy + r), (cx - t, cy + r), (cx - t, cy + t), (cx - r, cy + t), (cx - r, cy - t), (cx - t, cy - t)], cx, cy, math.pi / 4)
            else:  # pattee: flared arms
                pts = []
                for k in range(4):
                    ang = k * math.pi / 2
                    tip = [(cx + r * 0.2, cy - r * 0.15), (cx + r, cy - r * 0.45), (cx + r, cy + r * 0.45), (cx + r * 0.2, cy + r * 0.15)]
                    pts += rot(tip, cx, cy, ang)
            ps(a, pts, RED if (i + j) % 2 == 0 else RED_D, corner=1, out=2.0)
    return done(a)


def quatrefoil2(seed, n=2, filled=True):
    a = pat(seed)
    cell = T / n
    for i in range(n + 1):
        for j in range(n + 1):
            cx, cy = i * cell, j * cell
            r = cell * 0.22
            from objects import lobed

            pts = lobed(cx, cy, r * 0.6, [(cx + r * math.cos(t), cy + r * math.sin(t), r * 0.95) for t in (0, math.pi / 2, math.pi, 3 * math.pi / 2)])
            if filled:
                ps(a, pts, RED, corner=0, out=2.2)
            else:
                ring(a, pts)
            ps(a, poly(cx + cell / 2, cy + cell / 2, cell * 0.12, 4, math.pi / 4), RED_D, corner=1, out=1.8)
    return done(a)


def ogee(seed, n=4):
    """Ogee lattice: onion-shaped cells from S curves."""
    a = pat(seed)
    w = T / n
    h = w * 1.5
    rows = max(1, int(round(T / h)))
    h = T / rows
    for j in range(rows + 1):
        for i in range(n + 1):
            for ox, oy in ((0, 0), (w / 2, h / 2)):
                cx, cy = i * w + ox, j * h + oy
                pts = []
                for k in range(25):
                    t = k / 24
                    y = cy - h / 2 + h * t
                    x = (w / 2 - 4) * math.sin(math.pi * t) ** 1.6 * (1 - 0.25 * math.sin(2 * math.pi * t))
                    pts.append((cx + x, y))
                pts += [(2 * cx - x, y) for x, y in reversed(pts[1:-1])]
                ps(a, chaikin(pts, True, 1), RED if ox == 0 else RED_D, corner=0, out=2.0)
    return done(a)


def fish_scale(seed, n=4, rows=8, outline_only=False):
    a = pat(seed)
    w = T / n
    rh = T / rows
    for j in range(rows + 1):
        for i in range(-1, n + 1):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * rh
            r = w / 2 - 2
            pts = [(cx + r, cy - r * 0.2)] + [(cx + r * math.cos(t), cy + r * math.sin(t) * 0.9) for t in [math.pi * k / 16 for k in range(17)]] + [(cx - r, cy - r * 0.2)]
            if outline_only:
                line(a, pts[1:-1])
            else:
                ps(a, pts, RED if j % 2 else RED_D, corner=2, out=2.0)
    return done(a)


def meander(seed, rows=4):
    """Greek key bands."""
    a = pat(seed)
    h = T / rows
    unit = T / 4
    for j in range(rows):
        y = j * h + h / 2
        s = h * 0.32
        for i in range(-1, 5):
            x = i * unit
            pts = [(x, y + s), (x, y - s), (x + unit * 0.75, y - s), (x + unit * 0.75, y + s * 0.3), (x + unit * 0.35, y + s * 0.3), (x + unit * 0.35, y - s * 0.3)]
            line(a, pts + [(x + unit * 0.35, y - s * 0.3)])
            line(a, [(x + unit * 0.75, y + s * 0.3), (x + unit * 0.75, y + s), (x + unit, y + s)])
    return done(a)


def zigzag(seed, rows=6, filled=True, amp=0.5):
    a = pat(seed)
    h = T / rows
    n = 4
    w = T / n
    for j in range(rows):
        y = j * h
        top = []
        for i in range(n * 2 + 3):
            x = -w + i * w / 2
            top.append((x, y + (h * amp if i % 2 else 0)))
        if filled:
            band = top + [(x, yy + h * 0.45) for x, yy in reversed(top)]
            ps(a, band, RED if j % 2 else RED_D, corner=1, out=2.0)
        else:
            line(a, top)
    return done(a)


def waves2(seed, rows=6, filled=False):
    a = pat(seed)
    h = T / rows
    for j in range(rows):
        y = j * h + h / 2
        pts = [(x, y + h * 0.28 * math.sin(2 * math.pi * x / (T / 2))) for x in range(-16, T + 17, 8)]
        if filled:
            band = pts + [(x, yy + h * 0.35) for x, yy in reversed(pts)]
            ps(a, band, RED if j % 2 else RED_D, corner=0, out=2.0)
        else:
            line(a, pts, w=DETAIL * 2)
    return done(a)


def overlap_circles(seed, n=4):
    """Seed-of-life style overlapping rings."""
    a = pat(seed)
    cell = T / n
    r = cell / 2
    for i in range(n + 1):
        for j in range(n + 1):
            for ox, oy in ((0, 0), (cell / 2, cell / 2)):
                ring(a, ellipse(i * cell + ox, j * cell + oy, r, r, 48), w=DETAIL * 1.2)
    return done(a)


def polka(seed, n=4, size=0.28, offset=True):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx = (i + 0.5) * cell + (cell / 2 if offset and j % 2 else 0)
            cy = (j + 0.5) * cell
            r = cell * size
            ps(a, ellipse(cx, cy, r, r, 32), RED, corner=0, out=2.0)
    return done(a)


def stripes(seed, n=8, diag=False, two=False):
    """Vertical stripes: flat bands inked only along their long edges (so
    nothing marks the seam where the tile repeats vertically)."""
    from pen import to_path

    a = pat(seed)
    w = T / n
    for i in range(0, n, 2):
        x = i * w
        col = RED_D if two and (i // 2) % 2 else RED
        a.fill_path(to_path(rect(x + 1, -2, x + w - 1, T + 2)), col)
        g = to_path(rect(x + w * 0.62, -2, x + w - 1, T + 2))
        a.fill_path(g, (120, 24, 24), 0.35, blur=2)
        for ex in (x + 1, x + w - 1):
            a.ink([(ex, -8), (ex, T + 8)], 2.0, color=(43, 36, 31), taper=False, wob=0, var=0.04)
    return done(a)


def plaid(seed):
    a = pat(seed)
    for k, (w, col) in enumerate(((48, RED), (16, RED_D), (8, RED_L))):
        for x0 in (40, 168):
            a.fill_path(__import__("pen").to_path(rect(x0 - w / 2, 0, x0 + w / 2, T)), col, 0.75)
            a.fill_path(__import__("pen").to_path(rect(0, x0 - w / 2, T, x0 + w / 2)), col, 0.75)
    for x0 in (40, 168):
        for d in (-24, 24):
            line(a, [(x0 + d, 0), (x0 + d, T)], (110, 20, 20), w=FINE)
            line(a, [(0, x0 + d), (T, x0 + d)], (110, 20, 20), w=FINE)
    return done(a)


def argyle(seed):
    a = pat(seed)
    cell = T / 2
    for i in range(3):
        for j in range(3):
            cx, cy = i * cell, j * cell
            ps(a, [(cx, cy - cell / 2 + 2), (cx + cell / 2 - 2, cy), (cx, cy + cell / 2 - 2), (cx - cell / 2 + 2, cy)], RED if (i + j) % 2 else RED_D, corner=1, out=2.0)
    for k in range(-2, 4):
        line(a, [(k * cell, 0), (k * cell + T, T)], RED_L, w=FINE * 1.3)
        line(a, [(k * cell, T), (k * cell + T, 0)], RED_L, w=FINE * 1.3)
    return done(a)


def trellis(seed, n=4, ang=math.pi / 4):
    """Diagonal lattice (garden trellis) bars."""
    a = pat(seed)
    step = T / n
    for k in range(-n, 2 * n + 1):
        for sgn in (1, -1):
            p0 = (k * step, 0) if sgn > 0 else (k * step, T)
            p1 = (k * step + T, T) if sgn > 0 else (k * step + T, 0)
            a.ink([p0, p1], 13, color=(60, 30, 26), taper=False, wob=0.2)
            a.ink([p0, p1], 8, color=RED, taper=False, wob=0.2)
    return done(a)


def crosshatch(seed, n=8):
    a = pat(seed)
    step = T / n
    for k in range(n + 1):
        line(a, [(k * step, -4), (k * step, T + 4)], RED, w=DETAIL)
        line(a, [(-4, k * step), (T + 4, k * step)], RED, w=DETAIL)
    for i in range(n):
        for j in range(n):
            if (i + j) % 2 == 0:
                ps(a, rect(i * step + 4, j * step + 4, (i + 1) * step - 4, (j + 1) * step - 4), RED_L, corner=1, out=1.2, shade_k=0.1)
    return done(a)


def windmill(seed):
    a = pat(seed)
    n = 2
    P = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * P, (j + 0.5) * P
            for k in range(4):
                blade = [(cx, cy), (cx + P * 0.45, cy - P * 0.08), (cx + P * 0.45, cy + P * 0.22)]
                ps(a, rot(blade, cx, cy, k * math.pi / 2), RED if k % 2 else RED_D, corner=1, out=2.0)
    return done(a)


def girih(seed):
    """Simple girih-like: 8-point stars with kite shapes around."""
    a = pat(seed)
    n = 2
    cell = T / n
    for i in range(n + 1):
        for j in range(n + 1):
            cx, cy = i * cell, j * cell
            ps(a, star(cx, cy, cell * 0.38, cell * 0.24, 8, 0), RED, corner=1, out=2.0)
            for k in range(8):
                t = k * math.pi / 4 + math.pi / 8
                x, y = cx + cell * 0.5 * math.cos(t), cy + cell * 0.5 * math.sin(t)
                ps(a, rot([(x - 8, y), (x, y - 14), (x + 8, y), (x, y + 14)], x, y, t), RED_D, corner=1, out=1.6)
    return done(a)


def celtic_band(seed, rows=4):
    """Interlaced band: two waves crossing, drawn as wide ribbons."""
    a = pat(seed)
    h = T / rows
    for j in range(rows):
        y0 = j * h + h / 2
        for ph in (0, math.pi):
            pts = [(x, y0 + h * 0.28 * math.sin(2 * math.pi * x / (T / 2) + ph)) for x in range(-16, T + 17, 6)]
            a.ink(pts, 15, color=(60, 30, 26), taper=False, wob=0)
            a.ink(pts, 9, color=RED if ph == 0 else RED_D, taper=False, wob=0)
    return done(a)


# -- motifs ----------------------------------------------------------------------------------------


def flower_at(a, cx, cy, r, petals=5, col=RED, center=RED_L):
    for k in range(petals):
        t = 2 * math.pi * k / petals
        ps(a, ellipse(cx + r * 0.55 * math.cos(t), cy + r * 0.55 * math.sin(t), r * 0.5, r * 0.32, 20, rot=t), col, corner=0, out=1.6, shade_k=0.25)
    ps(a, ellipse(cx, cy, r * 0.28, r * 0.28, 16), center, corner=0, out=1.4)


def leaf_at(a, cx, cy, size, ang, col=RED):
    pts = rot([(cx - size / 2, cy), (cx, cy - size * 0.3), (cx + size / 2, cy), (cx, cy + size * 0.3)], cx, cy, ang)
    ps(a, chaikin(pts, True, 2), col, corner=0, out=1.6, shade_k=0.25)
    line(a, rot([(cx - size * 0.4, cy), (cx + size * 0.4, cy)], cx, cy, ang), (110, 20, 20), w=FINE * 0.8)


def florals(seed, n=4, petals=5, leaves=True):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx = (i + 0.5) * cell + (cell / 2 if j % 2 else 0)
            cy = (j + 0.5) * cell
            if leaves:
                leaf_at(a, cx + cell * 0.3, cy + cell * 0.18, cell * 0.36, 0.6, RED_D)
                leaf_at(a, cx - cell * 0.3, cy - cell * 0.18, cell * 0.36, 0.6, RED_D)
            flower_at(a, cx, cy, cell * 0.3, petals)
    return done(a)


def leaves_pat(seed, n=6):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            leaf_at(a, cx, cy, cell * 0.8, a.rng.uniform(0, math.pi), (RED, RED_D, RED_L)[a.rng.randint(0, 2)])
    return done(a)


def vines_pat(seed, rows=3):
    a = pat(seed)
    h = T / rows
    for j in range(rows):
        y0 = j * h + h / 2
        pts = [(x, y0 + h * 0.2 * math.sin(2 * math.pi * x / T * 2)) for x in range(-16, T + 17, 6)]
        line(a, pts, RED_D, w=DETAIL * 1.4)
        for k in range(8):
            x = k * T / 8 + 8
            y = y0 + h * 0.2 * math.sin(2 * math.pi * x / T * 2)
            leaf_at(a, x + 10, y + (-12 if k % 2 else 12), 26, 0.5 if k % 2 else -0.5)
    return done(a)


def fleur(a, cx, cy, s, col=RED):
    """A simple fleur-de-lis."""
    mid = [(cx, cy - s), (cx + s * 0.22, cy - s * 0.35), (cx + s * 0.12, cy + s * 0.1), (cx - s * 0.12, cy + s * 0.1), (cx - s * 0.22, cy - s * 0.35)]
    ps(a, chaikin(mid, True, 1), col, corner=0, out=1.8)
    for side in (-1, 1):
        petal = [(cx + side * s * 0.1, cy), (cx + side * s * 0.65, cy - s * 0.55), (cx + side * s * 0.75, cy - s * 0.15), (cx + side * s * 0.25, cy + s * 0.2)]
        ps(a, chaikin(petal, True, 1), col, corner=0, out=1.8)
    ps(a, rect(cx - s * 0.4, cy + s * 0.1, cx + s * 0.4, cy + s * 0.28), col, corner=2, out=1.6)
    ps(a, [(cx - s * 0.12, cy + s * 0.28), (cx + s * 0.12, cy + s * 0.28), (cx, cy + s * 0.6)], col, corner=1, out=1.6)


def fleur_pat(seed, n=3, diamond=True):
    a = pat(seed)
    cell = T / n if n != 3 else T / 4
    n = int(round(T / cell))
    for i in range(n):
        for j in range(n):
            cx = (i + 0.5) * cell + (cell / 2 if j % 2 else 0)
            cy = (j + 0.5) * cell
            fleur(a, cx, cy, cell * 0.36)
    if diamond:
        for k in range(-n, 2 * n + 1):
            line(a, [(k * cell, 0), (k * cell + T, T)], RED_D, w=FINE)
            line(a, [(k * cell, T), (k * cell + T, 0)], RED_D, w=FINE)
    return done(a)


def arcane(seed, n=2):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            r = cell * 0.42
            ring(a, ellipse(cx, cy, r, r, 64), w=DETAIL * 1.3)
            ring(a, ellipse(cx, cy, r * 0.82, r * 0.82, 64), w=DETAIL)
            line(a, star(cx, cy, r * 0.82, r * 0.82, 3) + [], RED, w=DETAIL, closed=True)
            line(a, star(cx, cy, r * 0.82, r * 0.82, 3, math.pi / 2), RED, w=DETAIL, closed=True)
            for k in range(8):
                t = 2 * math.pi * k / 8 + math.pi / 8
                x, y = cx + r * 0.91 * math.cos(t), cy + r * 0.91 * math.sin(t)
                line(a, [(x - 4, y - 4), (x + 2, y), (x - 3, y + 5)], RED_D, w=FINE * 1.2)
            ps(a, ellipse(cx, cy, r * 0.16, r * 0.16, 24), RED_D, corner=0, out=1.6)
    return done(a)


def runes(seed, n=4):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            s = cell * 0.32
            ps(a, rect(cx - s, cy - s, cx + s, cy + s), RED_L, corner=4, out=1.6, shade_k=0.2)
            strokes = a.rng.sample([[(0, -1), (0, 1)], [(-0.6, -0.6), (0.6, 0.6)], [(0.6, -0.6), (-0.6, 0.6)], [(0, -1), (0.6, -0.3)], [(0, 0), (-0.6, 0.5)], [(-0.6, 0), (0.6, 0)], [(0, 0.2), (0.6, 0.8)]], 3)
            for st in strokes:
                line(a, [(cx + px * s * 0.8, cy + py * s * 0.8) for px, py in st], RED_D, w=DETAIL * 1.2)
    return done(a)


def suns(seed, n=4):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            ps(a, star(cx, cy, cell * 0.44, cell * 0.28, 12), RED_D, corner=1, out=1.8)
            ps(a, ellipse(cx, cy, cell * 0.24, cell * 0.24, 32), RED, corner=0, out=1.8)
    return done(a)


def moons(seed, n=4):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            r = cell * 0.36
            outer = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [math.pi * 0.25 + k * math.pi * 1.5 / 24 for k in range(25)]]
            inner = [(cx + r * 0.35 + r * 0.8 * math.cos(t), cy - r * 0.15 + r * 0.8 * math.sin(t)) for t in [math.pi * 1.6 - k * math.pi * 1.1 / 24 for k in range(25)]]
            ps(a, outer + inner, RED if (i + j) % 2 else RED_D, corner=0, out=1.8)
    return done(a)


def hearts(seed, n=4):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell + (cell / 2 if j % 2 else 0), (j + 0.5) * cell
            s = cell * 0.022
            pts = [(cx + s * 16 * math.sin(t) ** 3, cy - s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))) for t in [k * 2 * math.pi / 40 for k in range(40)]]
            ps(a, pts, RED, corner=0, out=1.8)
    return done(a)


def spirals(seed, n=4):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            pts = [(cx + (2 + 3.2 * t) * math.cos(t), cy + (2 + 3.2 * t) * math.sin(t)) for t in [k * 0.25 for k in range(48)]]
            line(a, pts, RED if (i + j) % 2 else RED_D, w=DETAIL * 1.4)
    return done(a)


def drops(seed, n=4):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell + (cell / 2 if j % 2 else 0), (j + 0.5) * cell
            r = cell * 0.24
            pts = [(cx, cy - r * 1.6)] + [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [-math.pi * 0.2 + k * math.pi * 1.4 / 20 for k in range(21)]]
            ps(a, pts, RED, corner=0, out=1.8)
    return done(a)


def keys_pat(seed, n=4):
    """Tiny diamonds and dots (damask-like ground)."""
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            d = cell * 0.4
            ps(a, [(cx, cy - d), (cx + d * 0.6, cy), (cx, cy + d), (cx - d * 0.6, cy)], RED, corner=1, out=1.8)
            ps(a, [(cx, cy - d * 0.45), (cx + d * 0.26, cy), (cx, cy + d * 0.45), (cx - d * 0.26, cy)], RED_L, corner=1, out=1.2, shade_k=0.1)
            ps(a, ellipse(i * cell, j * cell, cell * 0.08, cell * 0.08, 16), RED_D, corner=0, out=1.2)
    return done(a)


def medallions(seed, n=2):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            from objects import scallop

            ps(a, scallop(cx, cy, cell * 0.42, a.rng, 12, 0.12), RED_D, corner=0, out=2.0)
            ps(a, ellipse(cx, cy, cell * 0.3, cell * 0.3, 48), RED, corner=0, out=1.8)
            flower_at(a, cx, cy, cell * 0.2, 8, RED_L, RED_D)
            ps(a, poly(i * cell, j * cell, cell * 0.1, 4, math.pi / 4), RED_D, corner=1, out=1.4)
    return done(a)


def checks(seed, n=8, inset_=0.0, round_=False):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            if (i + j) % 2:
                continue
            g = cell * inset_ + 1.5
            if round_:
                ps(a, ellipse((i + 0.5) * cell, (j + 0.5) * cell, cell / 2 - g, cell / 2 - g, 28), RED, corner=0, out=1.6)
            else:
                ps(a, rect(i * cell + g, j * cell + g, (i + 1) * cell - g, (j + 1) * cell - g), RED, corner=1, out=1.6)
    return done(a)


def squares_in_squares(seed, n=4):
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            for k, col in enumerate((RED_D, RED, RED_L)):
                g = 3 + k * cell * 0.14
                ps(a, rect(x0 + g, y0 + g, x0 + cell - g, y0 + cell - g), col, corner=2, out=1.6, shade_k=0.25)
    return done(a)


def lattice_octagon(seed, n=4, dots=True):
    """Octagons with small diamonds between (square-octagon tiling)."""
    a = pat(seed)
    cell = T / n
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            ps(a, poly(cx, cy, cell * 0.52, 8, math.pi / 8), RED, corner=1, out=2.0)
            if dots:
                ps(a, poly(i * cell, j * cell, cell * 0.16, 4, 0), RED_D, corner=1, out=1.6)
    return done(a)


# -- registry --------------------------------------------------------------------------------------

PATTERNS2 = {
    "Small Square Tiles": lambda: grid(301, n=8, gap=2.5, corner=3),
    "Tiny Square Tiles": lambda: grid(302, n=16, gap=1.6, corner=2),
    "Two-Tone Tiles": lambda: grid(303, n=4, alt=RED_D),
    "Two-Tone Small Tiles": lambda: grid(304, n=8, gap=2.5, corner=3, alt=RED_L),
    "Big Slabs": lambda: grid(305, n=1, gap=5, corner=8),
    "Square Slabs": lambda: grid(306, n=2, gap=4, corner=6, alt=RED_D),
    "Rounded Tiles": lambda: grid(307, n=4, gap=4, corner=14),
    "Pill Tiles": lambda: grid(308, n=8, gap=3, corner=10),
    "Running Bond": lambda: bond(309, 8, 4, 0.5),
    "Third Bond": lambda: bond(310, 8, 4, 1 / 3),
    "Stack Bond": lambda: bond(311, 8, 4, 0.0),
    "Long Brick Bond": lambda: bond(312, 8, 2, 0.5),
    "Narrow Brick Bond": lambda: bond(313, 12, 4, 0.5, gap=2),
    "Speckled Brick Bond": lambda: bond(314, 8, 4, 0.5, alt=True),
    "Tall Stack Bond": lambda: bond(315, 4, 8, 0.0),
    "Flemish Bond": lambda: flemish(316),
    "Pinwheel Tiles": lambda: pinwheel(317, 2),
    "Small Pinwheel": lambda: pinwheel(318, 4),
    "Hopscotch Tiles": lambda: hopscotch(319),
    "Wide Basketweave": lambda: basket(320, 2, 3),
    "Fine Basketweave": lambda: basket(321, 8, 2, gap=1.8),
    "Triple Basketweave": lambda: basket(322, 4, 3),
    "Diagonal Herringbone": lambda: herring45(323, 6),
    "Fine Diagonal Herringbone": lambda: herring45(324, 10),
    "Chevron Parquet": lambda: chevron_planks(325),
    "Narrow Chevron": lambda: chevron_planks(326, 8),
    "Plank Floor": lambda: planks(327),
    "Wide Plank Floor": lambda: planks(328, 4),
    "Narrow Plank Floor": lambda: planks(329, 10),
    "Even Plank Floor": lambda: planks(330, 6, alt=False),
    "Round Shingles": lambda: shingles_pat(331),
    "Square Shingles": lambda: shingles_pat(332, round_=False),
    "Small Round Shingles": lambda: shingles_pat(333, 12),
    "Cobble Pattern": lambda: cobbles_pat(334),
    "Small Cobble Pattern": lambda: cobbles_pat(335, 9),
    "Large Cobble Pattern": lambda: cobbles_pat(336, 4, 0.3),
    "Random Mosaic": lambda: random_mosaic(337),
    "Fine Random Mosaic": lambda: random_mosaic(338, 16),
    "Small Hexagons": lambda: hexes(339, 8, 2.2),
    "Large Hexagons": lambda: hexes(340, 2, 4),
    "Hex Outlines": lambda: hexes(341, 4, 3, "ring"),
    "Dotted Hexagons": lambda: hexes(342, 4, 3, "dot"),
    "Tumbling Blocks": lambda: hexes(343, 4, 2, "three"),
    "Small Tumbling Blocks": lambda: hexes(344, 8, 1.6, "three"),
    "Two-Tone Triangles": lambda: triangles_pat(345),
    "Small Triangles": lambda: triangles_pat(346, 8),
    "Plain Triangles": lambda: triangles_pat(347, 4, alt=False),
    "Rhombus Tiles": lambda: rhombus(348),
    "Wide Rhombus": lambda: rhombus(349, 4, 1.0),
    "Tall Rhombus": lambda: rhombus(350, 4, 2.0),
    "Six-Point Stars": lambda: stars_pat(351, 4, 6, 0.5),
    "Eight-Point Stars": lambda: stars_pat(352, 4, 8, 0.6),
    "Five-Point Stars": lambda: stars_pat(353, 4, 5, 0.42, fill_gaps=True),
    "Small Stars": lambda: stars_pat(354, 8, 5, 0.42),
    "Star and Cross": lambda: eight_star_cross(355),
    "Greek Crosses": lambda: crosses_pat(356),
    "Saltire Crosses": lambda: crosses_pat(357, kind="x"),
    "Pattee Crosses": lambda: crosses_pat(358, kind="pattee"),
    "Small Crosses": lambda: crosses_pat(359, 8, 0.32),
    "Filled Quatrefoils": lambda: quatrefoil2(360),
    "Quatrefoil Outlines": lambda: quatrefoil2(361, 2, filled=False),
    "Small Quatrefoils": lambda: quatrefoil2(362, 4),
    "Ogee Lattice": lambda: ogee(363),
    "Large Ogee": lambda: ogee(364, 2),
    "Fish Scales": lambda: fish_scale(365),
    "Small Fish Scales": lambda: fish_scale(366, 8, 16),
    "Scale Outlines": lambda: fish_scale(367, 4, 8, outline_only=True),
    "Greek Key": lambda: meander(368),
    "Narrow Greek Key": lambda: meander(369, 6),
    "Zigzag Bands": lambda: zigzag(370),
    "Zigzag Lines": lambda: zigzag(371, 8, filled=False),
    "Wave Lines": lambda: waves2(372),
    "Wave Bands": lambda: waves2(373, 4, filled=True),
    "Overlapping Circles": lambda: overlap_circles(374),
    "Large Overlapping Circles": lambda: overlap_circles(375, 2),
    "Polka Dots": lambda: polka(376),
    "Small Polka Dots": lambda: polka(377, 8, 0.22),
    "Big Polka Dots": lambda: polka(378, 2, 0.3, offset=False),
    "Stripes": lambda: stripes(379),
    "Wide Stripes": lambda: stripes(380, 4),
    "Two-Tone Stripes": lambda: stripes(381, 8, two=True),
    "Plaid": lambda: plaid(382),
    "Argyle": lambda: argyle(383),
    "Diagonal Trellis": lambda: trellis(384),
    "Fine Trellis": lambda: trellis(385, 8),
    "Crosshatch Grid": lambda: crosshatch(386),
    "Windmills": lambda: windmill(387),
    "Girih Stars": lambda: girih(388),
    "Interlace Band": lambda: celtic_band(389),
    "Flowers": lambda: florals(390),
    "Small Flowers": lambda: florals(391, 8, 5, leaves=False),
    "Daisies": lambda: florals(392, 4, 8),
    "Leaves": lambda: leaves_pat(393, 5),
    "Big Leaves": lambda: leaves_pat(394, 4),
    "Vines": lambda: vines_pat(395),
    "Fleur-de-lis": lambda: fleur_pat(396),
    "Plain Fleur-de-lis": lambda: fleur_pat(397, diamond=False),
    "Arcane Circles": lambda: arcane(398),
    "Small Arcane Circles": lambda: arcane(399, 4),
    "Runes": lambda: runes(400),
    "Suns": lambda: suns(401),
    "Crescent Moons": lambda: moons(402),
    "Hearts": lambda: hearts(403),
    "Spirals": lambda: spirals(404),
    "Drops": lambda: drops(405),
    "Damask Diamonds": lambda: keys_pat(406),
    "Medallions": lambda: medallions(407),
    "Checkerboard Small": lambda: checks(408, 8),
    "Checkerboard Inset": lambda: checks(409, 8, 0.12),
    "Dot Checker": lambda: checks(410, 8, 0.1, round_=True),
    "Nested Squares": lambda: squares_in_squares(411),
    "Octagon Lattice": lambda: lattice_octagon(412),
    "Small Octagon Lattice": lambda: lattice_octagon(413, 8),
}
