"""Seamless floor tilesets and the recolorable patterns (512 px = 2 tiles)."""

import math

import numpy as np
import skia

from pen import DETAIL, FINE, INK, Art, chaikin, ellipse, mix, rect, rgb, round_corners, shade, tint, to_path, vary, wobble

T = 256


# -- shared pieces ---------------------------------------------------------------------------


def voronoi_cells(w, h, cols, rows, rng, jitter=0.35):
    """Polygons of a periodic Voronoi diagram over a jittered grid (stones)."""
    pts = []
    for j in range(rows):
        for i in range(cols):
            x = (i + 0.5 + rng.uniform(-jitter, jitter)) * w / cols
            y = (j + 0.5 + rng.uniform(-jitter, jitter)) * h / rows
            pts.append((x, y))
    ext = [(x + dx, y + dy) for x, y in pts for dx in (-w, 0, w) for dy in (-h, 0, h)]
    cells = []
    R = max(w / cols, h / rows) * 2.5
    for (px, py) in pts:
        poly = [(px - R, py - R), (px + R, py - R), (px + R, py + R), (px - R, py + R)]
        for (qx, qy) in ext:
            if (qx, qy) == (px, py) or abs(qx - px) > R or abs(qy - py) > R:
                continue
            # Keep the half-plane closer to p than to q.
            mx, my = (px + qx) / 2, (py + qy) / 2
            nx, ny = qx - px, qy - py
            poly = clip_half(poly, mx, my, nx, ny)
            if not poly:
                break
        cells.append(((px, py), poly))
    return cells


def clip_half(poly, mx, my, nx, ny):
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = (a[0] - mx) * nx + (a[1] - my) * ny
        db = (b[0] - mx) * nx + (b[1] - my) * ny
        if da <= 0:
            out.append(a)
        if (da <= 0) != (db <= 0):
            t = da / (da - db)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def inset(poly, d):
    """Shrink a convex polygon toward its centroid by about `d` px."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        L = math.hypot(x - cx, y - cy) or 1
        k = max(0.0, (L - d) / L)
        out.append((cx + (x - cx) * k, cy + (y - cy) * k))
    return out


def crack(art, x, y, angle, L, width=FINE, alpha=0.75):
    pts = [(x, y)]
    a = angle
    for _ in range(4):
        a += art.rng.uniform(-0.6, 0.6)
        x += math.cos(a) * L / 4
        y += math.sin(a) * L / 4
        pts.append((x, y))
    art.ink(pts, width, alpha=alpha, wob=0.4)
    if art.rng.random() < 0.5:
        i = art.rng.randint(1, 3)
        bx, by = pts[i]
        b = a + art.rng.choice((-1, 1)) * art.rng.uniform(0.6, 1.1)
        art.ink([(bx, by), (bx + math.cos(b) * L / 4, by + math.sin(b) * L / 4)], width * 0.8, alpha=alpha, wob=0.3)


def speckles(art, path, color, n, r=(0.8, 1.8), alpha=0.45):
    b = path.getBounds()
    for _ in range(n):
        x = art.rng.uniform(b.left(), b.right())
        y = art.rng.uniform(b.top(), b.bottom())
        if path.contains(x, y):
            c = skia.Path()
            c.addCircle(x, y, art.rng.uniform(*r))
            art.fill_path(c, color, alpha)


def split(total, rng, lo, hi):
    """Random lengths in [lo, hi] that add up exactly to `total` (a row that wraps)."""
    out = []
    while total - sum(out) > hi:
        out.append(rng.uniform(lo, hi))
    rest = total - sum(out)
    if rest < lo and out:
        # Share the short remainder with the previous piece.
        last = out.pop() + rest
        out += [last / 2, last / 2] if last > hi else [last]
    else:
        out.append(rest)
    return out


# -- floors ----------------------------------------------------------------------------------


def wood_planks(seed=1):
    s = 2 * T
    gap = rgb("#3b271b")
    a = Art(s, s, seed, tile=True, bg=gap)
    tones = [rgb("#b07d4f"), rgb("#a5724a"), rgb("#ba8a5a"), rgb("#9c6a42")]
    rows = 8
    h = s / rows
    for r in range(rows):
        y = r * h
        x = a.rng.uniform(0, s)
        lengths = split(s, a.rng, s * 0.3, s * 0.65)
        for ln in lengths:
            c = vary(a.rng, a.rng.choice(tones), 0.04)

            def grain(art, path, x=x, y=y, ln=ln, c=c):
                # Long grain lines that drift along the plank, one knot sometimes.
                for k in range(3):
                    gy = y + h * (0.22 + 0.28 * k) + art.rng.uniform(-4, 4)
                    gx0 = x + art.rng.uniform(-10, ln * 0.3)
                    gx1 = gx0 + ln * art.rng.uniform(0.5, 0.9)
                    pts = [(gx, gy + 2.5 * math.sin((gx - gx0) / art.rng.uniform(40, 70))) for gx in np.linspace(gx0, gx1, 12)]
                    art.ink(pts, FINE * 0.85, color=shade(c, 0.45), alpha=0.7, wob=0.5)
                if art.rng.random() < 0.35:
                    kx, ky = x + art.rng.uniform(ln * 0.25, ln * 0.75), y + h * art.rng.uniform(0.35, 0.65)
                    art.ink(ellipse(kx, ky, 7, 3.5, 24), FINE, closed=True, color=shade(c, 0.5), alpha=0.8, wob=0.2)
                    art.ink(ellipse(kx, ky, 15, 7, 32), FINE * 0.8, closed=True, color=shade(c, 0.45), alpha=0.5, wob=0.3)

            a.shape(rect(x + 1.6, y + 1.6, x + ln - 1.6, y + h - 1.6), c, outline=2.6, corner=2.5, wob=0.5, depth=4, shade_k=0.45, light_k=0.3, ao=0.2, mottle=0.05, detail=grain)
            # Nails at both ends.
            for nx in (x + 9, x + ln - 9):
                for ny in (y + h * 0.3, y + h * 0.7):
                    dot = skia.Path()
                    dot.addCircle(nx, ny, 2.2)
                    a.fill_path(dot, INK, 0.85)
            x += ln
    return a.image()


def flagstones(seed=2):
    s = 2 * T
    mortar = rgb("#6f685f")
    a = Art(s, s, seed, tile=True, bg=mortar)
    base = rgb("#a9a296")
    for (cx, cy), poly in voronoi_cells(s, s, 5, 5, a.rng, 0.3):
        p = inset(poly, 4.5)
        c = vary(a.rng, mix(base, rgb("#b8ae9c") if a.rng.random() < 0.5 else rgb("#968f86"), a.rng.uniform(0.2, 0.7)), 0.03)

        def detail(art, path, cx=cx, cy=cy, c=c):
            speckles(art, path, shade(c, 0.4), 18)
            if art.rng.random() < 0.45:
                crack(art, cx + art.rng.uniform(-20, 20), cy + art.rng.uniform(-20, 20), art.rng.uniform(0, 6.28), art.rng.uniform(30, 55))

        a.shape(p, c, outline=3.6, corner=10, wob=1.0, depth=7, shade_k=0.55, light_k=0.4, ao=0.3, detail=detail)
    return a.image()


def tiles(seed=3, color="#bf6b45", grout="#dccdb0", n=8):
    s = 2 * T
    a = Art(s, s, seed, tile=True, bg=rgb(grout))
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            c = vary(a.rng, rgb(color), 0.05)
            a.shape(rect(x0 + 3.5, y0 + 3.5, x0 + cell - 3.5, y0 + cell - 3.5), c, outline=2.8, corner=5, wob=0.5, depth=5, shade_k=0.5, light_k=0.4, ao=0.25)
    return a.image()


def dungeon_stone(seed=4):
    s = 2 * T
    a = Art(s, s, seed, tile=True, bg=rgb("#4c4842"))
    rows = 6
    h = s / rows
    for r in range(rows):
        x = a.rng.uniform(0, s)
        for w in split(s, a.rng, h * 1.1, h * 1.9):
            c = vary(a.rng, mix(rgb("#8a857d"), rgb("#7a756e"), a.rng.random()), 0.03)

            def detail(art, path, x=x, w=w, r=r, c=c):
                speckles(art, path, shade(c, 0.45), 14)
                if art.rng.random() < 0.3:
                    crack(art, x + w * art.rng.uniform(0.2, 0.8), r * h + h * 0.5, art.rng.uniform(0, 6.28), 30)

            a.shape(rect(x + 3, r * h + 3, x + w - 3, r * h + h - 3), c, outline=3.6, corner=8, wob=1.2, depth=7, shade_k=0.6, light_k=0.35, ao=0.3, detail=detail)
            x += w
    return a.image()


def carpet(seed=5):
    s = T
    base = rgb("#7e2a2a")
    a = Art(s, s, seed, tile=True, bg=base)
    gold = rgb("#d6ad55")
    for cx, cy in ((0, 0), (s, 0), (0, s), (s, s), (s / 2, s / 2)):
        for r, col in ((s * 0.36, rgb("#9a3836")), (s * 0.24, gold), (s * 0.14, rgb("#5e1f22"))):
            a.shape([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], col, outline=2.4, corner=2, wob=0.4, depth=3, shade_k=0.3, light_k=0.2, ao=0.1, mottle=0.03)
    # Woven texture: faint cross lines.
    for k in range(0, s, 6):
        a.ink([(k, 0), (k, s)], 0.8, color=shade(base, 0.5), alpha=0.18, taper=False, wob=0.1)
    return a.image()


def marble(seed=6):
    s = T
    a = Art(s, s, seed, tile=True, bg=rgb("#2c2a2f"))
    cell = s / 2
    for i in range(2):
        for j in range(2):
            light_tile = (i + j) % 2 == 0
            c = rgb("#e6e0d4") if light_tile else rgb("#47454d")
            x0, y0 = i * cell, j * cell

            def veins(art, path, x0=x0, y0=y0, c=c):
                vc = shade(c, 0.35) if light_tile else tint(c, 0.35)
                for _ in range(2):
                    x, y = x0 + art.rng.uniform(0, cell), y0
                    pts = [(x, y)]
                    for _ in range(6):
                        x += art.rng.uniform(-16, 16)
                        y += cell / 6
                        pts.append((x, y))
                    art.ink(chaikin(pts, False, 2), FINE * 0.8, color=vc, alpha=0.7, wob=0.4)

            a.shape(rect(x0 + 2.5, y0 + 2.5, x0 + cell - 2.5, y0 + cell - 2.5), c, outline=2.6, corner=3, wob=0.4, depth=5, shade_k=0.4, light_k=0.35, ao=0.2, detail=veins)
    return a.image()


# -- patterns: grey/white with RED regions (recolored by the Pattern tool's color) ---------------

P_RED = (190, 40, 40)
P_GROUT = (226, 222, 214)


def pattern_tiles(seed=21):
    s = T
    a = Art(s, s, seed, tile=True, bg=P_GROUT)
    n = 4
    cell = s / n
    for i in range(n):
        for j in range(n):
            x0, y0 = i * cell, j * cell
            a.shape(rect(x0 + 3.5, y0 + 3.5, x0 + cell - 3.5, y0 + cell - 3.5), vary(a.rng, P_RED, 0.05), outline=2.6, corner=5, wob=0.4, depth=5, shade_k=0.45, light_k=0.0, ao=0.2, mottle=0.0)
    return a.image()


def pattern_hex(seed=22):
    s = T
    a = Art(s, s, seed, tile=True, bg=P_GROUT)
    cols = 4
    w = s / cols
    rows = 4
    rh = s / rows  # row pitch; hex radius from it
    r = rh / 1.5 * 1.0
    for j in range(rows + 1):
        for i in range(cols + 1):
            cx = i * w + (w / 2 if j % 2 else 0)
            cy = j * rh
            rr = min(r, w / math.sqrt(3)) - 3
            pts = [(cx + rr * math.sin(k * math.pi / 3 + math.pi / 6) * 1.0, cy + rr * math.cos(k * math.pi / 3 + math.pi / 6)) for k in range(6)]
            a.shape(pts, vary(a.rng, P_RED, 0.05), outline=2.6, corner=3, wob=0.4, depth=4, shade_k=0.45, light_k=0.0, ao=0.2, mottle=0.0)
    return a.image()


def pattern_basketweave(seed=23):
    s = T
    a = Art(s, s, seed, tile=True, bg=P_GROUT)
    u = s / 8
    for bi in range(4):
        for bj in range(4):
            x0, y0 = bi * 2 * u, bj * 2 * u
            horizontal = (bi + bj) % 2 == 0
            for k in range(2):
                if horizontal:
                    x, y, w, h = x0, y0 + k * u, 2 * u, u
                else:
                    x, y, w, h = x0 + k * u, y0, u, 2 * u
                a.shape(rect(x + 2.5, y + 2.5, x + w - 2.5, y + h - 2.5), vary(a.rng, P_RED, 0.05), outline=2.4, corner=3, wob=0.3, depth=4, shade_k=0.45, light_k=0.0, ao=0.2, mottle=0.0)
    return a.image()
