"""More path strips (512 x ~150, periodic along x, transparent outside the
path): roads, trails, pavings, boardwalks, stepping stones, streams, rails
and garden borders. Reuses tex_ground's path machinery (an Art in tile
mode, so whatever crosses x = 0 / 512 comes back on the other side)."""

import math

import numpy as np

from floors import inset, speckles, split, voronoi_cells
from pen import FINE, INK, JOINT, JOINT_ALPHA, blob, grout, joint_color, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary
from tex_ground import PH, PW, boards_content, dirt_content, dot, flag_content, gravel_content, grass_trail_content, mud_content, path_strip, stones_in

C = rgb


def avg(cols):
    cs = [C(c) for c in cols]
    return tuple(sum(c[i] for c in cs) // len(cs) for i in range(3))


def gx(cols, mortar=None):
    """Hex background for a paved path: the joints' tone (see pen.grout),
    so the gaps between pieces read as thin joints, not dark trenches."""
    return "#%02x%02x%02x" % grout(avg(cols), C(mortar) if mortar else None)


def joint_shape(a, pts, c, k=1.0, **kw):
    """A paving piece outlined by a thin joint of its own darker tone."""
    kw.setdefault("wob", 0.4)
    kw.setdefault("depth", 3)
    kw.setdefault("shade_k", 0.35)
    kw.setdefault("light_k", 0.25)
    kw.setdefault("ao", 0.1)
    kw.setdefault("mottle", 0.03)
    return a.shape(pts, c, outline=JOINT * k, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA, **kw)


# -- content helpers -------------------------------------------------------------------------------


def span(top, bot):
    t = min(p[1] for p in top if 0 <= p[0] <= PW)
    b = max(p[1] for p in bot if 0 <= p[0] <= PW)
    return t, b


def specks(cols, n=400, r=(0.5, 1.3), alpha=0.6):
    def f(a, top, bot):
        t, b = span(top, bot)
        for _ in range(n):
            dot(a, a.rng.uniform(0, PW), a.rng.uniform(t, b), a.rng.uniform(*r), C(a.rng.choice(cols)), alpha)

    return f


def combine(*fs):
    def f(a, top, bot):
        for g in fs:
            g(a, top, bot)

    return f


def ruts(color, width=2.4, ys=(0.36, 0.64), amp=3):
    def f(a, top, bot):
        for ry in ys:
            y = PH * ry
            ph = a.rng.uniform(0, 6.28)
            a.ink([(x, y + amp * math.sin(2 * math.pi * x / PW * 3 + ph)) for x in np.linspace(-20, PW + 20, 40)], width, color=C(color), alpha=0.7, taper=False)

    return f


def cart_tracks(rut_col, mid_col):
    """Two worn wheel tracks with a grassy (or lighter) hump between them."""
    def f(a, top, bot):
        t, b = span(top, bot)
        mid = [(x, PH / 2 + 3 * math.sin(2 * math.pi * x / PW * 2)) for x in np.linspace(-30, PW + 30, 50)]
        a.ink(mid, (b - t) * 0.26, color=C(mid_col), alpha=0.85, taper=False, wob=0.6)
        for ry in (0.3, 0.7):
            y = PH * ry
            a.ink([(x, y + 2 * math.sin(2 * math.pi * x / PW * 3 + ry * 9)) for x in np.linspace(-30, PW + 30, 50)], 12, color=C(rut_col), alpha=0.55, taper=False, wob=0.4)
        grass_trail_content(a, top, bot) if mid_col.startswith("#8") or mid_col.startswith("#9") else None

    return f


def pebbles_in(cols, n=320, r=(3, 6.5)):
    def f(a, top, bot):
        t, b = span(top, bot)
        for _ in range(n):
            x, y = a.rng.uniform(0, PW), a.rng.uniform(t + 4, b - 4)
            a.shape(blob(x, y, a.rng.uniform(*r), a.rng, 8, 0.25), vary(a.rng, C(a.rng.choice(cols)), 0.06), outline=1.3, corner=0, wob=0.2, depth=1.5, shade_k=0.4, light_k=0.4, ao=0, mottle=0)

    return f


def cobbles(cols, r=(11, 15), rows=4, outline=2.4):
    """Packed cobbles: like tex_ground.stones_in but set close together with
    thin tone-on-tone joints (`outline` only scales the joint)."""
    def f(a, top, bot):
        t, b = span(top, bot)
        hh = b - t
        rr = (r[0] + r[1]) / 2
        count = int(PW / (rr * 1.75))
        for row in range(rows):
            for k in range(count):
                x = (k + 0.5 + (0.5 if row % 2 else 0)) * PW / count + a.rng.uniform(-3, 3)
                y = t + hh * (row + 0.5) / rows + a.rng.uniform(-4, 4)
                c = vary(a.rng, C(a.rng.choice(cols)), 0.06)
                joint_shape(a, blob(x, y, a.rng.uniform(*r) * 1.05, a.rng, 9, 0.16), c, 1.2 * outline / 2.4, corner=0, depth=3, mottle=0)

    return f


def setts(cols, rows=5, w=34):
    """Rectangular paving setts in staggered rows."""
    def f(a, top, bot):
        hh = PH / rows
        n = int(PW / w)
        ww = PW / n
        for r in range(rows):
            off = ww / 2 if r % 2 else 0
            for k in range(-1, n + 1):
                x = k * ww + off
                joint_shape(a, rect(x + 1, r * hh + 1, x + ww - 1, r * hh + hh - 1), vary(a.rng, C(a.rng.choice(cols)), 0.05), 1.2, corner=3)

    return f


def bricks(cols, bond="running", rows=5):
    def f(a, top, bot):
        hh = PH / rows
        bw = 2 * hh
        n = int(round(PW / bw))
        bw = PW / n
        cs = [C(c) for c in cols]

        def brick(x0, y0, x1, y1):
            joint_shape(a, rect(x0 + 0.9, y0 + 0.9, x1 - 0.9, y1 - 0.9), vary(a.rng, a.rng.choice(cs), 0.05), corner=1.5)

        if bond == "stack":
            for r in range(rows):
                for k in range(n):
                    brick(k * bw, r * hh, (k + 1) * bw, (r + 1) * hh)
        elif bond == "basket":
            u = PH / 4
            m = int(round(PW / (2 * u)))
            u2 = PW / m
            for bi in range(m):
                for bj in range(2):
                    x0, y0 = bi * u2, bj * PH / 2
                    if (bi + bj) % 2 == 0:
                        brick(x0, y0, x0 + u2, y0 + PH / 4)
                        brick(x0, y0 + PH / 4, x0 + u2, y0 + PH / 2)
                    else:
                        brick(x0, y0, x0 + u2 / 2, y0 + PH / 2)
                        brick(x0 + u2 / 2, y0, x0 + u2, y0 + PH / 2)
        elif bond == "soldier":
            # Bricks stood on end across the road, a header course at each edge.
            m = int(round(PW / (hh * 0.9)))
            ww = PW / m
            for k in range(m):
                brick(k * ww, hh, (k + 1) * ww, PH - hh)
            for r in (0, rows - 1):
                for k in range(n):
                    brick(k * bw, r * hh, (k + 1) * bw, (r + 1) * hh)
        else:
            for r in range(rows):
                off = 0 if r % 2 == 0 else bw / 2
                for k in range(-1, n + 1):
                    brick(k * bw + off, r * hh, k * bw + off + bw, (r + 1) * hh)

    return f


def flags(cols, n=7, rows=2):
    def f(a, top, bot):
        for (cx, cy), poly in voronoi_cells(PW, PH, n, rows, a.rng, 0.3):
            p = inset(poly, 1.8)
            joint_shape(a, p, vary(a.rng, C(a.rng.choice(cols)), 0.05), 1.2, corner=7, wob=0.7, depth=4, shade_k=0.4, light_k=0.3, ao=0.15, detail=lambda art, path: speckles(art, path, shade(C(cols[0]), 0.45), 6))

    return f


def roman_road(paving, curb):
    def f(a, top, bot):
        flags(paving, 9, 2)(a, top, bot)
        for y0, y1 in ((2, 24), (PH - 24, PH - 2)):
            n = 12
            for k in range(n):
                x = k * PW / n
                joint_shape(a, rect(x + 1, y0 + 1, x + PW / n - 1, y1 - 1), vary(a.rng, C(curb), 0.05), 1.2, corner=2)

    return f


def mosaic(cols, cell=10):
    def f(a, top, bot):
        rows = int(PH / cell)
        # Whole diamond periods across the strip, so the motif wraps.
        n = max(rows, int(round(PW / cell / rows)) * rows)
        cw = PW / n
        for r in range(rows):
            for k in range(n):
                x, y = k * cw, r * cell
                band = abs(r + 0.5 - rows / 2) / (rows / 2)
                if band > 0.78:
                    col = cols[0]
                else:
                    # A diamond chain down the middle of the road.
                    period = rows
                    dx = abs(((k % period) - period / 2))
                    dy = abs(r + 0.5 - rows / 2)
                    col = cols[1] if abs(dx + dy - rows * 0.3) < 1.0 else (cols[1] if a.rng.random() < 0.06 else cols[2])
                a.fill_path(to_path(rect(x + 1, y + 1, x + cw - 1, y + cell - 1)), vary(a.rng, C(col), 0.07))

    return f


def needles(cols, n=420, length=(6, 12)):
    def f(a, top, bot):
        t, b = span(top, bot)
        for _ in range(n):
            x, y = a.rng.uniform(0, PW), a.rng.uniform(t, b)
            ang = a.rng.uniform(0, 6.28)
            L = a.rng.uniform(*length)
            a.ink([(x, y), (x + L * math.cos(ang), y + L * math.sin(ang))], 1.9, color=C(a.rng.choice(cols)), alpha=0.9, wob=0.1, var=0.1)

    return f


def leaves(cols, n=60):
    def f(a, top, bot):
        t, b = span(top, bot)
        for _ in range(n):
            x, y = a.rng.uniform(0, PW), a.rng.uniform(t, b)
            ang = a.rng.uniform(0, 6.28)
            s = a.rng.uniform(8, 13)
            ux, uy = math.cos(ang), math.sin(ang)
            pts = chaikin([(x - ux * s, y - uy * s), (x - uy * s * 0.45, y + ux * s * 0.45), (x + ux * s, y + uy * s), (x + uy * s * 0.45, y - ux * s * 0.45)], True, 1)
            a.shape(pts, vary(a.rng, C(a.rng.choice(cols)), 0.05), outline=1.3, corner=0, wob=0.2, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)

    return f


def footprints(color, n=12, hoof=False):
    def f(a, top, bot):
        for k in range(n):
            x = (k + 0.5) * PW / n
            y = PH / 2 + (10 if k % 2 else -10)
            if hoof:
                a.ink([(x - 5 + 5 * math.cos(t), y + 6 * math.sin(t)) for t in np.linspace(0.4, 5.9, 12)], 2.2, color=C(color), alpha=0.7)
            else:
                a.fill_path(to_path(ellipse(x, y, 8, 4.5, 16)), C(color), 0.75)
                a.fill_path(to_path(ellipse(x + 10, y, 4.5, 4, 12)), C(color), 0.75)

    return f


def ice_cracks(a, top, bot):
    t, b = span(top, bot)
    for _ in range(14):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(t + 10, b - 10)
        pts = [(x, y)]
        ang = a.rng.uniform(0, 6.28)
        for _ in range(4):
            ang += a.rng.uniform(-0.7, 0.7)
            x += math.cos(ang) * 10
            y += math.sin(ang) * 10
            pts.append((x, y))
        a.ink(pts, 1.1, color=C("#7f98aa"), alpha=0.7, wob=0.2)
    for _ in range(10):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(t + 10, b - 10)
        a.ink([(x, y), (x + 18, y - 4)], 2.2, color=C("#f4fbff"), alpha=0.85)


def embers(a, top, bot):
    t, b = span(top, bot)
    for _ in range(40):
        dot(a, a.rng.uniform(0, PW), a.rng.uniform(t, b), a.rng.uniform(1.2, 2.6), C(a.rng.choice(("#ff8a3a", "#ffb347", "#e9773a"))), 0.95)


def stepping(cols, n=5, r=(34, 42), ry=(26, 32), outline=3.0, detail_col="#6f6a62", rings=False):
    def f(a, top, bot):
        for k in range(n):
            x = (k + 0.5) * PW / n + a.rng.uniform(-8, 8)
            y = PH / 2 + a.rng.uniform(-14, 14)
            col = vary(a.rng, C(a.rng.choice(cols)), 0.06)

            def det(art, p, x=x, y=y, col=col):
                if rings:
                    for rr in (8, 16, 24):
                        art.ink(ellipse(x, y, rr, rr * 0.8, 24), 1.1, closed=True, color=shade(col, 0.45), alpha=0.7)
                else:
                    speckles(art, p, C(detail_col), 10)

            a.shape(blob(x, y, a.rng.uniform(*r), a.rng, 10, 0.12, ry=a.rng.uniform(*ry)), col, outline=outline, corner=0, wob=0.6, depth=7, shade_k=0.55, light_k=0.45, ao=0.2, detail=det)

    return f


def lava_between(a, top, bot):
    t, b = span(top, bot)
    a.fill_path(to_path(rect(-10, t, PW + 10, b)), C("#c8461e"), 0.9)
    for _ in range(30):
        x, y = a.rng.uniform(0, PW), a.rng.uniform(t, b)
        a.fill_path(to_path(blob(x, y, a.rng.uniform(6, 14), a.rng, 8, 0.3)), C("#ffb347"), 0.7)
    stepping(("#3a3634", "#2e2a28"), detail_col="#5a5450")(a, top, bot)


def boards(color, across=True, gap=26):
    """tex_ground.boards_content with thin tone-on-tone joints and nails."""
    def f(a, top, bot):
        col = C(color)
        if across:
            x = 0
            while x < PW - 2:
                w = gap
                c = vary(a.rng, col, 0.05)
                joint_shape(a, rect(x + 0.8, 4, x + w - 0.8, PH - 4), c, corner=1.5, mottle=0.04, detail=lambda art, p, x=x, c=c: art.ink([(x + w / 2 + art.rng.uniform(-3, 3), 12), (x + w / 2 + art.rng.uniform(-3, 3), PH - 12)], FINE * 0.8, color=shade(c, 0.45), alpha=0.6))
                for ny in (20, PH - 20):
                    dot(a, x + w / 2, ny, 2, shade(c, 0.6), 0.7)
                x += w
        else:
            rows = 5
            hh = PH / rows
            for r in range(rows):
                x = a.rng.uniform(0, PW)
                for ln in split(PW, a.rng, PW * 0.3, PW * 0.6):
                    c = vary(a.rng, col, 0.05)
                    joint_shape(a, rect(x + 0.8, r * hh + 0.8, x + ln - 0.8, r * hh + hh - 0.8), c, corner=1.5, mottle=0.04)
                    x += ln

    return f


def logs_across(col, w=24):
    def f(a, top, bot):
        n = int(PW / w)
        ww = PW / n
        for k in range(n):
            x = k * ww
            c = vary(a.rng, C(col), 0.06)
            a.shape(rect(x + 1, 6, x + ww - 1, PH - 6), c, outline=2.2, corner=ww * 0.45, wob=0.3, depth=3, shade_k=0.5, light_k=0.3, ao=0.1, mottle=0.03, detail=lambda art, p, x=x, c=c: art.ink([(x + ww / 2, 16), (x + ww / 2 + art.rng.uniform(-2, 2), PH - 16)], FINE, color=shade(c, 0.5), alpha=0.6))
            for y in (8, PH - 8):
                a.shape(ellipse(x + ww / 2, y, ww * 0.42, 5, 16), tint(c, 0.25), outline=1.2, depth=1, mottle=0)

    return f


def rope_bridge(wood):
    def f(a, top, bot):
        boards(wood, across=True, gap=24)(a, top, bot)
        for y in (10, PH - 10):
            a.ink([(x, y + 3 * math.sin(2 * math.pi * x / PW * 4)) for x in np.linspace(-20, PW + 20, 60)], 6, color=INK, taper=False)
            a.ink([(x, y + 3 * math.sin(2 * math.pi * x / PW * 4)) for x in np.linspace(-20, PW + 20, 60)], 3.5, color=C("#c9b088"), taper=False)
        for k in range(8):
            x = k * PW / 8
            for y0, y1 in ((10, 26), (PH - 26, PH - 10)):
                a.ink([(x, y0), (x + 4, y1)], 1.6, color=C("#c9b088"))

    return f


def stream(water, bank, rocks=0, mud=False, ice=False):
    def f(a, top, bot):
        t, b = span(top, bot)
        a.fill_path(to_path(rect(-10, t - 4, PW + 10, b + 4)), C(water), 1.0)
        mid = [(x, (t + b) / 2 + 4 * math.sin(2 * math.pi * x / PW * 2)) for x in np.linspace(-20, PW + 20, 60)]
        a.ink(mid, (b - t) * 0.35, color=shade(C(water), 0.2), alpha=0.35, taper=False, wob=0.4)
        for line in (top, bot):
            a.ink(line, 14, color=C(bank), alpha=0.8, taper=False, wob=0.6)
        for _ in range(16):
            x, y = a.rng.uniform(0, PW), a.rng.uniform(t + 14, b - 14)
            if ice:
                a.ink([(x, y), (x + 22, y - 3)], 2.2, color=C("#f4fbff"), alpha=0.85)
            else:
                a.ink([(x, y), (x + 10, y - 2), (x + 20, y)], 1.4, color=C("#e4f2f6"), alpha=0.85)
        for _ in range(rocks):
            x, y = a.rng.uniform(0, PW), a.rng.uniform(t + 8, b - 8)
            a.shape(blob(x, y, a.rng.uniform(7, 14), a.rng, 8, 0.2), vary(a.rng, C("#9d978d"), 0.08), outline=1.8, corner=0, wob=0.3, depth=3, shade_k=0.45, light_k=0.45, ao=0, mottle=0)
        if mud:
            for _ in range(10):
                x, y = a.rng.uniform(0, PW), a.rng.uniform(t + 10, b - 10)
                a.fill_path(to_path(blob(x, y, a.rng.uniform(8, 16), a.rng, 9, 0.3)), C("#6e5641"), 0.5)

    return f


def rails(ground, tie, rail="#6a6c72", overgrown=False):
    def f(a, top, bot):
        gravel_content(a, top, bot) if ground == "gravel" else None
        n = 16
        for k in range(n):
            x = k * PW / n + 6
            a.shape(rect(x, 18, x + 18, PH - 18), vary(a.rng, C(tie), 0.06), outline=2.0, corner=2, wob=0.3, depth=2, shade_k=0.4, light_k=0.3, ao=0.1, mottle=0.03)
        for y in (PH * 0.32, PH * 0.68):
            a.ink([(-20, y), (PW + 20, y)], 11, color=INK, taper=False, wob=0, var=0.02)
            a.ink([(-20, y), (PW + 20, y)], 7, color=C(rail), taper=False, wob=0, var=0.02)
            a.ink([(-20, y - 1.5), (PW + 20, y - 1.5)], 1.6, color=tint(C(rail), 0.55), taper=False, wob=0, var=0.02)
        if overgrown:
            grass_trail_content(a, top, bot)

    return f


def border_of(kind, cols=("#c8443a",)):
    def f(a, top, bot):
        if kind == "curb":
            # One continuous curb (inked only along its long edges) cut into
            # blocks by thin joints, not a row of loose inked blocks.
            n = 10
            t, b = span(top, bot)
            y0, y1 = max(6, t + 2.5), min(PH - 6, b - 2.5)
            tile = a.tile
            a.tile = False
            a.fill_path(to_path(rect(-20, y0, PW + 20, y1)), grout(C(cols[0])))
            a.tile = tile
            for k in range(n):
                x = k * PW / n
                joint_shape(a, rect(x + 1, y0 + 1, x + PW / n - 1, y1 - 1), vary(a.rng, C(cols[0]), 0.05), 1.2, corner=2, depth=4, shade_k=0.4, light_k=0.3, ao=0.12)
            a.tile = False
            for y in (y0, y1):
                a.ink([(-20, y), (PW + 20, y)], 3.2, taper=False, wob=0.3, var=0.08)
            a.tile = tile
        elif kind == "flowers":
            grass_trail_content(a, top, bot)
            for _ in range(70):
                x, y = a.rng.uniform(0, PW), a.rng.uniform(12, PH - 12)
                c = C(a.rng.choice(cols))
                for k in range(5):
                    pa = 2 * math.pi * k / 5
                    a.shape(ellipse(x + 4 * math.cos(pa), y + 4 * math.sin(pa), 4, 2.8, 10, rot=pa), c, outline=0.9, depth=1, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
                dot(a, x, y, 1.8, C("#f2d24a"))
        elif kind == "hedge":
            from objects import scallop

            for k in range(9):
                x = (k + 0.5) * PW / 9
                a.shape(scallop(x, PH / 2, 34, a.rng, 9, 0.12), vary(a.rng, C(cols[0]), 0.05), outline=2.4, corner=0, wob=0.3, depth=6, shade_k=0.5, light_k=0.35, ao=0.2, mottle=0.05)
        elif kind == "picket":
            a.shape(rect(-20, PH / 2 - 5, PW + 20, PH / 2 + 5), C("#c9b896"), outline=2.0, corner=2, depth=2)
            n = 16
            for k in range(n):
                x = (k + 0.5) * PW / n
                a.shape(rect(x - 9, PH / 2 - 10, x + 9, PH / 2 + 10), C(cols[0]), outline=2.0, corner=2, depth=2, mottle=0)
        elif kind == "logs":
            n = 4
            for k in range(n):
                x = k * PW / n
                a.shape(rect(x + 3, PH / 2 - 16, x + PW / n - 3, PH / 2 + 16), vary(a.rng, C(cols[0]), 0.06), outline=2.4, corner=14, depth=4, shade_k=0.5, light_k=0.3)
        elif kind == "pebbles":
            stones_in(a, top, bot, cols, (8, 12), rows=3, outline=1.8)
        elif kind == "lavender":
            for k in range(14):
                x = (k + 0.5) * PW / 14
                for j in range(12):
                    ang = 2 * math.pi * j / 12
                    L = a.rng.uniform(16, 26)
                    a.ink([(x, PH / 2), (x + L * math.cos(ang), PH / 2 + L * math.sin(ang))], 2.2, color=C("#6f8a5a"), alpha=0.9)
                    dot(a, x + L * math.cos(ang), PH / 2 + L * math.sin(ang), 3, C(cols[0]))

    return f


# -- the catalog ----------------------------------------------------------------------------------


def P(seed, base, content, **kw):
    return lambda: path_strip(seed, base, content=content, **kw)


GREYS = ("#aaa49b", "#958f86", "#a39d93")
PATHS2 = {
    # Earth roads
    "Red Earth Road": P(501, "#a8603e", combine(dirt_content, specks(("#7a3e26",)))),
    "Dark Loam Road": P(502, "#6e5236", combine(ruts("#4a3624"), specks(("#3e2c1e",)))),
    "Clay Road": P(503, "#b88a5e", combine(ruts("#8a6440", 1.8), specks(("#8a6440",), 200))),
    "Pale Dust Road": P(504, "#d2bc94", specks(("#a8906a", "#bfa880"), 500)),
    "Ochre Road": P(505, "#c49a4e", combine(dirt_content, specks(("#8a6a2e",), 300))),
    "Cart Track": P(506, "#a8845a", cart_tracks("#6e5236", "#8faa62")),
    "Sandy Cart Track": P(507, "#d6be8a", cart_tracks("#a8906a", "#e2cfa0")),
    "Snowy Cart Track": P(508, "#e6ecf1", cart_tracks("#a8b8c8", "#f4f8fb"), edge_col="#9aaabb"),
    "Rutted Mud Road": P(509, "#5e4a36", combine(mud_content, ruts("#3a2c20", 3.4))),
    "Puddled Road": P(510, "#8a6e50", combine(dirt_content, mud_content)),
    # Sand & gravel
    "Dune Sand Trail": P(511, "#e2c890", combine(ruts("#c4a56a", 1.4, (0.3, 0.5, 0.7), 5), specks(("#b8985e",), 300)), margin=24, amp=9),
    "White Sand Path": P(512, "#ece2c8", specks(("#c8bc9e", "#d8ccae"), 500), margin=24, amp=8),
    "Black Sand Path": P(513, "#4a4644", specks(("#2a2624", "#6a6460"), 600), margin=24, amp=8),
    "Shell Path": P(514, "#e4dccb", pebbles_in(("#f4ece0", "#e8d4c4", "#d8c8b4"), 260, (3, 6))),
    "Warm Gravel Path": P(515, "#9a8a74", pebbles_in(("#b8a68c", "#a8967c", "#c4b298"))),
    "Dark Gravel Path": P(516, "#5a5654", pebbles_in(("#6e6a66", "#4e4a48", "#7e7a76"))),
    "White Gravel Path": P(517, "#cfcbc4", pebbles_in(("#e8e4de", "#d6d2ca", "#f2eee8"))),
    "Red Gravel Path": P(518, "#8a5a4a", pebbles_in(("#a86a58", "#985c4a", "#b87a66"))),
    "Bark Mulch Path": P(519, "#6e4a30", needles(("#a8784e", "#3e2818", "#c08a5a"), 560, (8, 16))),
    # Cobbles
    "Small Cobbles": P(520, gx(GREYS), cobbles(GREYS, (8, 11), 5, 2.0), margin=10, amp=2),
    "Large Cobbles": P(521, gx(GREYS), cobbles(GREYS, (15, 20), 3, 2.6), margin=10, amp=2),
    "Basalt Cobbles": P(522, gx(("#5a5654", "#4a4644", "#666260")), cobbles(("#5a5654", "#4a4644", "#666260")), margin=10, amp=2),
    "Sandstone Cobbles": P(523, gx(("#cdb68e", "#d9c49c", "#bfa67e")), cobbles(("#cdb68e", "#d9c49c", "#bfa67e")), margin=10, amp=2),
    "Mossy Cobbles": P(524, gx(GREYS), combine(cobbles(GREYS), specks(("#6f9443",), 260, (1.5, 3.5), 0.8)), margin=10, amp=2),
    "Limestone Cobbles": P(525, gx(("#e6e0d0", "#d8d2c2", "#efe9da")), cobbles(("#e6e0d0", "#d8d2c2", "#efe9da")), margin=10, amp=2),
    "Blue-grey Cobbles": P(526, gx(("#8a96a2", "#7a8692", "#96a2ae")), cobbles(("#8a96a2", "#7a8692", "#96a2ae")), margin=10, amp=2),
    "Mixed Cobbles": P(527, gx(("#aaa49b", "#b07a5e", "#cdb68e", "#8a96a2")), cobbles(("#aaa49b", "#b07a5e", "#cdb68e", "#8a96a2")), margin=10, amp=2),
    "Worn Cobbles": P(528, gx(GREYS), combine(cobbles(GREYS, (10, 14), 4, 1.8), dirt_content), margin=12, amp=4),
    # Setts & flagstones
    "Granite Setts": P(529, gx(("#9a958e", "#8a857e", "#a6a19a")), setts(("#9a958e", "#8a857e", "#a6a19a")), margin=6, amp=0),
    "Dark Setts": P(530, gx(("#5e5a56", "#6a6662", "#545050")), setts(("#5e5a56", "#6a6662", "#545050")), margin=6, amp=0),
    "Sandstone Setts": P(531, gx(("#c8b088", "#d6c098", "#b89e78")), setts(("#c8b088", "#d6c098", "#b89e78")), margin=6, amp=0),
    "Large Grey Flagstones": P(532, gx(("#a9a296", "#b8ae9c", "#968f86")), flags(("#a9a296", "#b8ae9c", "#968f86"), 5), margin=10, amp=2),
    "Slate Flagstones Path": P(533, gx(("#6a727c", "#5e666e", "#77808a")), flags(("#6a727c", "#5e666e", "#77808a")), margin=10, amp=2),
    "Red Flagstones": P(534, gx(("#a86a58", "#985c4a", "#b87a66")), flags(("#a86a58", "#985c4a", "#b87a66")), margin=10, amp=2),
    "Marble Flagstones": P(535, gx(("#ece6da", "#e0dace", "#f4efe4")), flags(("#ece6da", "#e0dace", "#f4efe4")), margin=10, amp=2),
    "Crazy Paving": P(536, gx(("#a9a296", "#cdb68e", "#968f86", "#b8ae9c")), flags(("#a9a296", "#cdb68e", "#968f86", "#b8ae9c"), 11, 3), margin=10, amp=2),
    "Dark Flagstones": P(537, gx(("#5a5654", "#4e4a48", "#666260")), flags(("#5a5654", "#4e4a48", "#666260")), margin=10, amp=2),
    # Bricks
    "Soldier Course Bricks": P(538, gx(("#a8503b", "#94432f", "#b5604a"), "#c9b9a2"), bricks(("#a8503b", "#94432f", "#b5604a"), "soldier"), margin=6, amp=0),
    "Basketweave Bricks": P(539, gx(("#a8503b", "#94432f", "#b5604a"), "#c9b9a2"), bricks(("#a8503b", "#94432f", "#b5604a"), "basket"), margin=6, amp=0),
    "Stack Bond Bricks": P(540, gx(("#a8503b", "#94432f", "#b5604a"), "#c9b9a2"), bricks(("#a8503b", "#94432f", "#b5604a"), "stack"), margin=6, amp=0),
    "Brown Brick Road": P(541, gx(("#7a5040", "#6a4434", "#8a5e4c"), "#b8a890"), bricks(("#7a5040", "#6a4434", "#8a5e4c")), margin=6, amp=0),
    "Grey Brick Road": P(542, gx(("#7a7670", "#6a6660", "#86827c"), "#9a968e"), bricks(("#7a7670", "#6a6660", "#86827c")), margin=6, amp=0),
    "White Brick Road": P(543, gx(("#e6e0d0", "#d8d2c2", "#efe9da"), "#a8a294"), bricks(("#e6e0d0", "#d8d2c2", "#efe9da")), margin=6, amp=0),
    "Old Brick Road": P(544, gx(("#a8503b", "#7a5040", "#94432f"), "#8a7a68"), combine(bricks(("#a8503b", "#7a5040", "#94432f")), specks(("#6f9443",), 160, (1.5, 3), 0.7)), margin=6, amp=0),
    # Special pavings
    "Roman Road": P(545, gx(("#a9a296", "#b8ae9c", "#968f86")), roman_road(("#a9a296", "#b8ae9c", "#968f86"), "#8a857e"), margin=0, amp=0, edge_ink=False),
    "Sandstone Roman Road": P(546, gx(("#cdb68e", "#d9c49c", "#bfa67e")), roman_road(("#cdb68e", "#d9c49c", "#bfa67e"), "#a8906a"), margin=0, amp=0, edge_ink=False),
    "Mosaic Road": P(547, "#e4dccb", mosaic(("#4f74a8", "#c8443a", "#e6dcc4")), margin=6, amp=0),
    "Gold Mosaic Road": P(548, "#e4dccb", mosaic(("#7a2e26", "#d6ae4c", "#efe6d0")), margin=6, amp=0),
    # Trails
    "Pine Needle Trail": P(549, "#8a6a48", needles(("#c89a5a", "#5a3a20", "#d8a868"), 520), margin=30, amp=9),
    "Leafy Trail": P(550, "#7a6248", combine(dirt_content, leaves(("#c9752f", "#d99a3a", "#b54a2c", "#a8652f"))), margin=26, amp=9),
    "Green Leaf Trail": P(551, "#6e6a48", leaves(("#5f8f3c", "#7aa64a", "#4f7c34"), 70), margin=26, amp=9),
    "Snowy Footprints": P(552, "#eef3f7", footprints("#a8b8c8"), edge_col="#9aaabb", margin=26, amp=8),
    "Sand Footprints": P(553, "#dcc48f", footprints("#a88e5a"), margin=26, amp=8),
    "Hoofprint Trail": P(554, "#a68660", combine(dirt_content, footprints("#5e4630", 16, True)), margin=22, amp=7),
    "Icy Path": P(555, "#cfe2ee", ice_cracks, edge_col="#7f98aa"),
    "Ember Ash Trail": P(556, "#4e4a46", combine(specks(("#2e2a28",), 400), embers)),
    "Mossy Trail": P(557, "#5e7040", combine(specks(("#7a9a50", "#4e6a34"), 400, (1, 2.5), 0.8), grass_trail_content), margin=28, amp=9),
    "Worn Grass Trail": P(558, "#a8a070", combine(grass_trail_content, needles(("#6a8a44", "#8aa65a"), 260, (4, 8)), specks(("#7a6a44",), 300)), margin=34, amp=10),
    "Dry Grass Trail": P(559, "#c8b47a", needles(("#8a7a40", "#e6d49a"), 460, (5, 10)), margin=30, amp=9),
    "Deer Trail": P(560, "#9a8a64", combine(grass_trail_content, footprints("#5e4e34", 14, True)), margin=50, amp=10),
    "Swamp Trail": P(561, "#4e5a3a", combine(mud_content, specks(("#3a4a2a",), 300)), margin=24, amp=9),
    "Clay Footpath": P(562, "#b07a52", combine(dirt_content, specks(("#8a5a3a",), 200)), margin=44, amp=10),
    # Stepping stones
    "Lava Stepping Stones": P(563, "#000000", lava_between, fill=False, edge_ink=False, margin=26, amp=8),
    "River Rock Steps": P(564, "#000000", stepping(("#8f948f", "#a8a49a", "#7f857f"), 7, (22, 28), (18, 24)), fill=False, edge_ink=False),
    "Slate Slab Steps": P(565, "#000000", stepping(("#6a727c", "#5e666e"), 4, (40, 46), (28, 32), detail_col="#3e4248"), fill=False, edge_ink=False),
    "Round Pavers": P(566, "#000000", stepping(("#b8b2a8", "#c4beb3"), 6, (26, 28), (26, 28)), fill=False, edge_ink=False),
    "Log Slice Steps": P(567, "#000000", stepping(("#c39463", "#b8875a"), 6, (26, 30), (24, 28), rings=True), fill=False, edge_ink=False),
    "Sandstone Steps": P(568, "#000000", stepping(("#cdb68e", "#d9c49c"), 5), fill=False, edge_ink=False),
    "Mossy Steps": P(569, "#000000", combine(stepping(("#8f948a", "#7f857c")), specks(("#6f9443",), 120, (2, 4), 0.9)), fill=False, edge_ink=False),
    # Wood
    "Dark Boardwalk": P(570, gx(("#6e4a32",)), boards("#6e4a32", across=True), margin=6, amp=0),
    "Pale Boardwalk": P(571, gx(("#d2a878",)), boards("#d2a878", across=True), margin=6, amp=0),
    "Weathered Boardwalk": P(572, gx(("#a8a294",)), boards("#a8a294", across=True), margin=6, amp=0),
    "Painted Boardwalk": P(573, gx(("#a8483a",)), boards("#a8483a", across=True), margin=6, amp=0),
    "Long Plank Walk": P(574, gx(("#a8784e",)), boards("#a8784e", across=False), margin=6, amp=0),
    "Log Path": P(575, "#6e4a30", logs_across("#7a5a3e"), margin=2, amp=0, edge_ink=False),
    "Birch Log Path": P(576, "#a8a294", logs_across("#d8d2c4", 22), margin=2, amp=0, edge_ink=False),
    "Rope Bridge": P(577, "#9a6c43", rope_bridge("#a8784e"), margin=2, amp=0, edge_ink=False),
    "Old Rope Bridge": P(578, "#6e5a44", rope_bridge("#8a7a64"), margin=2, amp=0, edge_ink=False),
    "Swamp Boardwalk": P(579, gx(("#6e5a40",)), combine(boards("#6e5a40", across=True, gap=30), specks(("#6f9443",), 120, (1.5, 3), 0.8)), margin=6, amp=0),
    # Water
    "Shallow Stream": P(580, "#6aa0b6", stream("#6aa0b6", "#8a7a54"), margin=14, amp=8, edge_ink=False),
    "Rocky Creek": P(581, "#5f8ea4", stream("#5f8ea4", "#8a8478", rocks=26), margin=12, amp=8, edge_ink=False),
    "Muddy Creek": P(582, "#7a8a74", stream("#7a8a74", "#5e4a36", mud=True), margin=14, amp=8, edge_ink=False),
    "Frozen Stream": P(583, "#b8d6e6", stream("#b8d6e6", "#dfe8ee", ice=True), margin=14, amp=8, edge_ink=False),
    "Grassy Brook": P(584, "#6aa0b6", stream("#6aa0b6", "#6f9443", rocks=8), margin=26, amp=10, edge_ink=False),
    "Wide River": P(585, "#4f7a92", stream("#4f7a92", "#8a7a54", rocks=6), margin=4, amp=6, edge_ink=False),
    "Lava Flow": P(586, "#c8461e", combine(stream("#c8461e", "#3a3634"), embers), margin=16, amp=9, edge_ink=False),
    # Rails
    "Minecart Track": P(587, "#6e6a62", rails("gravel", "#6e4a2f"), margin=8, amp=2),
    "Dark Minecart Track": P(588, "#3e3a36", rails("none", "#4e3624", "#5a5c62"), margin=8, amp=2),
    "Overgrown Track": P(589, "#6e7a50", rails("none", "#6e5a44", "#7a6e62", overgrown=True), margin=8, amp=2),
    # Borders & edgings
    "Stone Curb": P(590, "#000000", border_of("curb", ("#9a958e",)), fill=False, edge_ink=False, margin=40, amp=0),
    "Red Flower Border": P(591, "#5f7a3c", border_of("flowers", ("#c8443a", "#d8584a")), margin=28, amp=8),
    "Mixed Flower Border": P(592, "#5f7a3c", border_of("flowers", ("#c8443a", "#e6b84a", "#f3eee2", "#9a6ab8")), margin=28, amp=8),
    "Blue Flower Border": P(593, "#5f7a3c", border_of("flowers", ("#6f8fd0", "#8aa6e0")), margin=28, amp=8),
    "Hedge Border": P(594, "#000000", border_of("hedge", ("#4f7c34",)), fill=False, edge_ink=False, margin=30, amp=0),
    "Picket Border": P(595, "#000000", border_of("picket", ("#ece4d3",)), fill=False, edge_ink=False, margin=30, amp=0),
    "Log Edging": P(596, "#000000", border_of("logs", ("#7a5a3e",)), fill=False, edge_ink=False, margin=40, amp=0),
    "Pebble Edging": P(597, "#000000", border_of("pebbles", GREYS), fill=False, edge_ink=False, margin=40, amp=0),
    "Lavender Row": P(598, "#000000", border_of("lavender", ("#9a7ad0",)), fill=False, edge_ink=False, margin=30, amp=0),
    "Brick Edging": P(599, "#000000", border_of("curb", ("#a8503b",)), fill=False, edge_ink=False, margin=50, amp=0),
}
