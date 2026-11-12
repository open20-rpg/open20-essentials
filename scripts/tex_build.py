"""Structural textures for the built-in pack: walls (strip + end cap),
portals (doors/windows/arches), caves (floor + wall) and roofs (tiles + edge,
ridge and hip lines). Same pen style as floors.py: hand-inked, flat colours,
subtle shading. Strips repeat along x; floors and roof tiles are seamless.
256 px = 1 map tile."""

import math

import skia

from floors import crack, inset, speckles, split, voronoi_cells
from pen import DETAIL, FINE, INK, JOINT, JOINT_ALPHA, OUTLINE, Art, grout, joint_color, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

T = 256
SW = 2 * T  # strip width (repeats along x)


def strip(seed, h=64):
    """A transparent strip that repeats along x (shapes crossing the ends wrap)."""
    return Art(SW, h, seed, tile=True)


def band(a, y0, y1, color, outline=DETAIL * 1.3, detail=None, light_k=0.3, mottle=0.0, shade_k=0.5):
    """A full-width band across a repeating strip/tile: filled and shaded
    without tiled copies (they'd show their ends as seams), outlined only
    along its top and bottom; `detail(art)` then draws with wrapping on."""
    tile = a.tile
    a.tile = False
    a.shape(rect(-60, y0, a.w + 60, y1), color, outline=0, corner=0, wob=0, depth=4, shade_k=shade_k, light_k=light_k, ao=0.15, mottle=mottle)
    a.tile = tile
    if detail:
        with a.clip(to_path(rect(-60, y0, a.w + 60, y1))):
            detail(a)
    if outline:
        a.tile = False
        for y in (y0, y1):
            a.ink([(-60, y), (a.w + 60, y)], outline, taper=False, wob=0, var=0.0)
        a.tile = tile


def dot(a, x, y, r, color=INK, alpha=1.0):
    p = skia.Path()
    p.addCircle(x, y, r)
    a.fill_path(p, color, alpha)


# -- walls ------------------------------------------------------------------------------------


def wall_blocks(seed, color, rows=2, lo=50, hi=90, h=64, mortar=None, corner=7, wob=1.0, cracks=0.3, ruined=False, veins=False):
    """Masonry seen from above: one solid wall body (inked only along its two
    long edges) cut into staggered courses by thin joints of the stone's own
    darker tone, so it reads as a wall and not as loose blocks."""
    a = strip(seed, h)
    pad = 5
    if not ruined:
        band(a, pad, h - pad, grout(color, mortar), outline=0, light_k=0, shade_k=0.15)
    rh = (h - 2 * pad) / rows
    for r in range(rows):
        x = a.rng.uniform(0, SW)
        for wdt in split(SW, a.rng, lo, hi):
            y0, y1 = pad + r * rh, pad + (r + 1) * rh
            if ruined and a.rng.random() < 0.22:
                x += wdt
                continue
            c = vary(a.rng, color, 0.045)
            g = 0.9
            pts = rect(x + g, y0 + g, x + wdt - g, y1 - g)
            if ruined:
                pts = [(px + a.rng.uniform(-3, 3), py + a.rng.uniform(-2, 2)) for px, py in pts]

            def detail(art, path, x=x, wdt=wdt, y0=y0, y1=y1, c=c):
                speckles(art, path, shade(c, 0.45), 6)
                if art.rng.random() < cracks:
                    crack(art, x + wdt * art.rng.uniform(0.3, 0.7), (y0 + y1) / 2, art.rng.uniform(0, 6.28), min(30, wdt * 0.5))
                if veins:
                    art.ink(chaikin([(x + 6, y0 + 6), (x + wdt * 0.4, (y0 + y1) / 2), (x + wdt - 6, y1 - 6)], False, 2), FINE * 0.8, color=shade(c, 0.3), alpha=0.6)

            if ruined:
                # Ruins are loose blocks: each keeps its own ink outline.
                a.shape(pts, c, outline=DETAIL * 1.1, corner=corner, wob=wob, depth=5, shade_k=0.5, light_k=0.35, ao=0.2, detail=detail, var=0.1)
                x += wdt
                continue
            a.shape(pts, c, outline=JOINT, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA, corner=min(corner, 3), wob=wob * 0.5, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, detail=detail, var=0.1)
            x += wdt
    if not ruined:
        a.tile = False
        for y in (pad, h - pad):
            a.ink([(-60, y), (a.w + 60, y)], OUTLINE * 0.75, taper=False, wob=0.4, var=0.1)
        a.tile = True
    if ruined:
        for _ in range(10):
            x, y = a.rng.uniform(0, SW), a.rng.uniform(10, h - 10)
            a.shape(blob(x, y, a.rng.uniform(4, 8), a.rng, 7, 0.25), shade(color, 0.1), outline=DETAIL * 0.8, smooth=True, depth=2, mottle=0)
    return a.image()


def end_block(seed, color, s=64, round_=False, rings=False):
    a = Art(s, s, seed)
    if round_:
        p = a.shape(ellipse(s / 2, s / 2, s / 2 - 5, s / 2 - 5, 40), color, outline=OUTLINE * 0.8, depth=6)
        if rings:
            for r in (6, 13, 20):
                a.ink(ellipse(s / 2 + 1, s / 2 + 1, r, r, 32), FINE, closed=True, color=shade(color, 0.45), alpha=0.75)
    else:
        a.shape(rect(5, 5, s - 5, s - 5), color, outline=OUTLINE * 0.8, corner=8, depth=6, detail=lambda art, p: speckles(art, p, shade(color, 0.45), 5))
    return a.image()


def blocks_wall(seed, color, rows=2, lo=50, hi=90, h=64, **kw):
    def make():
        return wall_blocks(seed, color, rows, lo, hi, h, **kw), end_block(seed + 1, color, h)

    return make


def brick_wall(seed, color, mortar=rgb("#d9cbb2")):
    def make():
        return wall_blocks(seed, color, rows=3, lo=36, hi=46, h=60, mortar=mortar, corner=3, wob=0.5, cracks=0.1), end_block(seed + 1, color, 60)

    return make


def log_wall(seed=1301):
    h = 66
    a = strip(seed, h)
    bark = rgb("#7a5a3e")
    rows = 2
    rh = (h - 8) / rows
    for r in range(rows):
        y0, y1 = 4 + r * rh, 4 + (r + 1) * rh
        c = vary(a.rng, bark, 0.06)

        def lines(art, y0=y0, y1=y1, c=c):
            for k in range(3):
                yy = y0 + (y1 - y0) * (k + 1) / 4
                x0 = art.rng.uniform(0, SW)
                for _ in range(6):
                    L = art.rng.uniform(30, 70)
                    art.ink([(x0, yy), (x0 + L, yy + art.rng.uniform(-1.5, 1.5))], FINE, color=shade(c, 0.55), alpha=0.7, wob=0.3)
                    x0 += L + art.rng.uniform(15, 50)

        band(a, y0 + 1, y1 - 1, c, detail=lines)
    return a.image(), end_block(seed + 1, rgb("#c39463"), h, round_=True, rings=True)


def bamboo_wall(seed=1302):
    h = 60
    a = strip(seed, h)
    col = rgb("#b8b45a")
    for r in range(3):
        y0 = 4 + r * (h - 8) / 3
        y1 = y0 + (h - 8) / 3
        band(a, y0 + 1, y1 - 1, vary(a.rng, col, 0.05), outline=DETAIL * 1.1)
        x = a.rng.uniform(0, 60)
        while x < SW:
            a.ink([(x, y0 + 2), (x, y1 - 2)], DETAIL, color=shade(col, 0.45), taper=False, wob=0.1)
            x += a.rng.uniform(56, 80)
    for x in range(0, SW, 128):
        a.shape(rect(x - 4, 2, x + 4, h - 2), rgb("#8a6a40"), outline=FINE * 1.3, corner=2, depth=1, mottle=0)
    return a.image(), end_block(seed + 1, tint(col, 0.1), h, round_=True, rings=True)


def palisade_wall(seed=1303):
    h = 64
    a = strip(seed, h)
    r = 27
    x = 0.0
    while x < SW - 1:
        cx = x + r
        col = vary(a.rng, rgb("#9a7048"), 0.07)
        pts = ellipse(cx, h / 2, r - 1, r - 1, 32)
        p = to_path(pts)
        a.fill_path(p, col)
        for j in range(6):
            t0, t1 = 2 * math.pi * j / 6, 2 * math.pi * (j + 1) / 6
            face = [(cx + (r - 1) * math.cos(t0), h / 2 + (r - 1) * math.sin(t0)), (cx + (r - 1) * math.cos(t1), h / 2 + (r - 1) * math.sin(t1)), (cx, h / 2)]
            lit = math.cos((t0 + t1) / 2 + math.pi * 0.75)
            a.fill_path(to_path(face), tint(col, 0.22 * lit) if lit > 0 else shade(col, -0.28 * lit))
        a.ink(pts, DETAIL * 1.3, closed=True, wob=0.2, var=0.08)
        x += 2 * r - 2 + 2 / 9.0
    return a.image(), end_block(seed + 1, rgb("#9a7048"), h, round_=True, rings=True)


def plaster_wall(seed, plaster, post=rgb("#6e4a2f"), straw=False):
    def make():
        h = 62
        a = strip(seed, h)

        def tex(art):
            if straw:
                for _ in range(120):
                    x, y = art.rng.uniform(0, SW), art.rng.uniform(8, h - 8)
                    t = art.rng.uniform(0, 6.28)
                    art.ink([(x, y), (x + 6 * math.cos(t), y + 6 * math.sin(t))], FINE * 0.8, color=shade(plaster, 0.35), alpha=0.6, wob=0.1)
            for _ in range(8):
                x = art.rng.uniform(0, SW)
                y = art.rng.uniform(12, h - 12)
                art.ink([(x, y), (x + art.rng.uniform(6, 14), y + art.rng.uniform(-3, 3))], FINE * 0.9, color=shade(plaster, 0.4), alpha=0.6)

        band(a, 5, h - 5, plaster, detail=tex)
        if post:
            for x in range(0, SW, T):
                a.shape(rect(x - 9, 3, x + 9, h - 3), post, outline=DETAIL * 1.2, corner=3, depth=3, var=0.1)
        return a.image(), end_block(seed + 1, post or plaster, h)

    return make


def hedge_wall(seed=1305):
    h = 70
    a = strip(seed, h)
    green = rgb("#5f8f3c")
    band(a, 8, h - 8, shade(green, 0.15), outline=0, light_k=0, shade_k=0)
    x = 0.0
    while x < SW:
        r = a.rng.uniform(16, 24)
        for yy in (h * 0.36, h * 0.64):
            a.shape(blob(x, yy + a.rng.uniform(-3, 3), r, a.rng, 10, 0.14), vary(a.rng, green, 0.07), outline=DETAIL, smooth=True, depth=4, light_k=0.4, mottle=0.03)
        x += r * 1.3
    for _ in range(60):
        x, y = a.rng.uniform(0, SW), a.rng.uniform(12, h - 12)
        t = a.rng.uniform(0, 6.28)
        a.ink([(x, y), (x + 6 * math.cos(t), y + 6 * math.sin(t))], FINE, color=shade(green, 0.55), alpha=0.5, wob=0.1)
    cap = Art(h, h, seed + 1)
    cap.shape(blob(h / 2, h / 2, h / 2 - 6, cap.rng, 10, 0.12), green, outline=OUTLINE * 0.8, smooth=True, depth=6)
    return a.image(), cap.image()


def iron_fence(seed=1306):
    h = 44
    a = strip(seed, h)
    iron = rgb("#4a4c52")
    a.ink([(-10, h / 2), (SW + 10, h / 2)], DETAIL * 2.4, color=INK, taper=False, wob=0, var=0.05)
    a.ink([(-10, h / 2), (SW + 10, h / 2)], DETAIL * 1.3, color=iron, taper=False, wob=0, var=0.05)
    for x in range(16, SW, 32):
        a.shape(ellipse(x, h / 2, 6, 6, 16), iron, outline=DETAIL * 0.9, depth=1, light_k=0.5, mottle=0)
    for x in range(0, SW, 128):
        a.shape(rect(x - 11, h / 2 - 11, x + 11, h / 2 + 11), iron, outline=DETAIL * 1.2, corner=3, depth=3, light_k=0.4, mottle=0)
    cap = Art(h, h, seed + 1)
    cap.shape(rect(9, 9, h - 9, h - 9), iron, outline=DETAIL * 1.4, corner=3, depth=3, light_k=0.4, mottle=0)
    return a.image(), cap.image()


def rock_wall(seed, color=rgb("#9a958c"), h=68, jag=0.25):
    """Fieldstone/rubble: irregular stones packed into one wall. The stones
    share a mortar body whose silhouette carries the ink; between stones only
    thin joints of their own darker tone."""

    def make():
        a = strip(seed, h)
        stones = []
        x = 0.0
        while x < SW:
            bw = a.rng.uniform(26, 46)
            pts = blob(x + bw / 2, h / 2, bw / 2 + 4, a.rng, 9, jag, ry=h / 2 - 6)
            stones.append([(px, min(h - 5, max(5, py))) for px, py in pts])
            x += bw * 0.82
        # The body: union of the stones and their copies one strip-length
        # away, cut to the strip, drawn without tiled copies so its outline
        # has no seams at the ends.
        body = skia.Path()
        for pts in stones:
            for dx in (-SW, 0, SW):
                q = [(px + dx, py) for px, py in pts]
                if max(px for px, _ in q) < -20 or min(px for px, _ in q) > SW + 20:
                    continue
                pq = to_path(chaikin(q, True, 2))
                body = skia.Op(body, pq, skia.kUnion_PathOp) if not body.isEmpty() else pq
        body = skia.Op(body, to_path(rect(-12, -10, SW + 12, h + 10)), skia.kIntersect_PathOp)
        a.tile = False
        a.fill_path(body, grout(color))
        a.tile = True
        for pts in stones:
            c = vary(a.rng, color, 0.07)
            a.shape([(px + a.rng.uniform(-0.5, 0.5), py) for px, py in pts], c, outline=JOINT * 1.2, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA, corner=4, depth=4, shade_k=0.4, light_k=0.25, ao=0.12, var=0.1, detail=lambda art, p, c=c: speckles(art, p, shade(c, 0.45), 4))
        a.tile = False
        a.stroke_path(body, INK, OUTLINE * 0.75)
        a.tile = True
        cap = Art(h, h, seed + 1)
        cap.shape(blob(h / 2, h / 2, h / 2 - 7, cap.rng, 8, 0.18), color, outline=OUTLINE * 0.8, smooth=False, corner=5, depth=6)
        return a.image(), cap.image()

    return make


def crystal_wall(seed=1308, color=rgb("#9a86d0")):
    h = 66
    a = strip(seed, h)
    band(a, 10, h - 10, shade(color, 0.35), outline=DETAIL)
    x = 0.0
    while x < SW:
        r = a.rng.uniform(12, 22)
        cy = a.rng.uniform(r + 4, h - r - 4)
        ang = a.rng.uniform(0, 1)
        pts = [(x + r * math.cos(ang + k * math.pi / 3), cy + r * 0.9 * math.sin(ang + k * math.pi / 3)) for k in range(6)]
        for k in range(6):
            face = [pts[k], pts[(k + 1) % 6], (x, cy)]
            lit = math.cos(ang + (k + 0.5) * math.pi / 3 + math.pi * 0.75)
            a.fill_path(to_path(face), tint(color, 0.3 * lit) if lit > 0 else shade(color, -0.3 * lit))
        for k in range(6):
            a.ink([pts[k], (x, cy)], FINE * 0.8, color=shade(color, 0.5), alpha=0.5, wob=0)
        a.ink(pts, DETAIL * 1.1, closed=True, wob=0.1)
        x += r * 1.3
    cap = Art(h, h, seed + 1)
    m = h / 2
    pts = [(m + 26 * math.cos(k * math.pi / 3), m + 26 * math.sin(k * math.pi / 3)) for k in range(6)]
    cap.shape(pts, color, outline=OUTLINE * 0.8, corner=2, depth=5, light_k=0.5)
    return a.image(), cap.image()


def ice_wall(seed=1309):
    col = rgb("#cfe6ee")

    def make():
        img = wall_blocks(seed, col, rows=2, lo=60, hi=110, h=64, corner=10, wob=1.4, cracks=0.6)
        return img, end_block(seed + 1, col, 64)

    return make


def bone_wall(seed=1310):
    h = 60
    a = strip(seed, h)
    bone = rgb("#e6dcc4")
    band(a, 6, h - 6, rgb("#6a5e52"), outline=DETAIL, light_k=0, shade_k=0.3)
    x = 0.0
    while x < SW:
        y = a.rng.uniform(16, h - 16)
        L = a.rng.uniform(40, 64)
        for e in (0, L):
            for k in (-1, 1):
                a.shape(ellipse(x + e, y + k * 5, 7, 7, 16), bone, outline=DETAIL * 0.9, depth=1, mottle=0)
        a.ink([(x, y), (x + L, y)], 13, color=INK, taper=False, wob=0, var=0.05)
        a.ink([(x, y), (x + L, y)], 8, color=bone, taper=False, wob=0, var=0.05)
        if a.rng.random() < 0.3:
            sx = x + L / 2
            a.shape(chaikin([(sx - 12, y - 4), (sx - 9, y - 14), (sx + 9, y - 14), (sx + 12, y - 4), (sx + 8, y + 10), (sx - 8, y + 10)], True, 2), bone, outline=DETAIL, corner=0, depth=2, mottle=0)
            for dx in (-5, 5):
                dot(a, sx + dx, y - 3, 3.2, rgb("#2a221e"))
        x += L * 0.75
    cap = Art(h, h, seed + 1)
    m = h / 2
    cap.shape(chaikin([(m - 18, m - 4), (m - 14, m - 20), (m + 14, m - 20), (m + 18, m - 4), (m + 12, m + 16), (m - 12, m + 16)], True, 2), bone, outline=OUTLINE * 0.7, corner=0, depth=4)
    for dx in (-7, 7):
        dot(cap, m + dx, m - 4, 4.5, rgb("#2a221e"))
    return a.image(), cap.image()


WALLS = {
    "Grey Stone Wall": blocks_wall(1311, rgb("#a39d93")),
    "Sandstone Wall": blocks_wall(1312, rgb("#d2b98a"), lo=60, hi=100),
    "Dark Stone Wall": blocks_wall(1313, rgb("#6f6a64"), rows=2, lo=40, hi=70),
    "Castle Ashlar Wall": blocks_wall(1314, rgb("#b8b2a6"), rows=2, lo=80, hi=120, h=72, corner=3, wob=0.4, cracks=0.1),
    "Ruined Stone Wall": blocks_wall(1315, rgb("#9a958c"), rows=2, lo=40, hi=80, ruined=True, cracks=0.6),
    "Marble Wall": blocks_wall(1316, rgb("#ece8de"), rows=1, lo=110, hi=160, h=58, corner=3, wob=0.3, cracks=0.0, veins=True),
    "Red Brick Wall": brick_wall(1317, rgb("#a8503b")),
    "Brown Brick Wall": brick_wall(1318, rgb("#8a5a3e")),
    "White Brick Wall": brick_wall(1319, rgb("#e6e0d4"), mortar=rgb("#a39d93")),
    "Log Wall": log_wall,
    "Bamboo Wall": bamboo_wall,
    "Palisade Wall": palisade_wall,
    "Timber Frame Wall": plaster_wall(1320, rgb("#e6dccb")),
    "Adobe Wall": plaster_wall(1321, rgb("#c99a6a"), post=None, straw=True),
    "Hedge": hedge_wall,
    "Iron Fence": iron_fence,
    "Cave Rock Wall": rock_wall(1322),
    "Crystal Wall": crystal_wall,
    "Ice Wall": ice_wall(1323),
    "Bone Wall": bone_wall,
}


# -- portals ----------------------------------------------------------------------------------------

FRAME = rgb("#6e4a2f")
DOOR = rgb("#9a6c43")
IRON = rgb("#5d6068")
BRASS = rgb("#d2a647")


def jambs(a, w, h, color=FRAME, depth=18):
    """The door frame's posts at both ends and the threshold between them."""
    a.shape(rect(4, h / 2 - 6, w - 4, h / 2 + 6), shade(color, 0.25), outline=DETAIL, corner=2, depth=2, mottle=0)
    for x0 in (2, w - 2 - depth):
        a.shape(rect(x0, 8, x0 + depth, h - 8), color, outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.35)


def leaf(a, x0, x1, h, color=DOOR, bands=True, handle_at=None, thick=16, studs=False):
    """A door leaf seen from above: a thick plank slab across the opening."""
    y0, y1 = h / 2 - thick / 2, h / 2 + thick / 2

    def planks(art, p):
        n = max(2, int((x1 - x0) / 28))
        for k in range(1, n):
            x = x0 + (x1 - x0) * k / n
            art.ink([(x, y0 + 1), (x, y1 - 1)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False)

    a.shape(rect(x0, y0, x1, y1), color, outline=DETAIL * 1.4, corner=3, depth=3, light_k=0.4, detail=planks)
    if bands:
        for x in (x0 + 10, x1 - 10):
            a.shape(rect(x - 4, y0 - 2, x + 4, y1 + 2), IRON, outline=FINE * 1.2, corner=1, depth=1, mottle=0)
    if studs:
        for x in range(int(x0) + 16, int(x1) - 8, 18):
            dot(a, x, h / 2, 2.4, tint(IRON, 0.4))
    if handle_at is not None:
        for s in (-1, 1):
            a.shape(ellipse(handle_at, h / 2 + s * (thick / 2 + 5), 5, 4, 16), BRASS, outline=FINE * 1.3, depth=1, mottle=0)


def swing(a, hx, hy, r, a0, a1):
    """The dotted arc a door sweeps when it opens."""
    k = 0
    t = a0
    while t < a1:
        t1 = min(a1, t + 0.09)
        if k % 2 == 0:
            a.ink([(hx + r * math.cos(t), hy + r * math.sin(t)), (hx + r * math.cos(t1), hy + r * math.sin(t1))], FINE, alpha=0.6, taper=False, wob=0)
        t = t1
        k += 1


def portal_wood_door(seed=1401, color=DOOR, w=T, h=80, studs=False, iron=False):
    def make():
        a = Art(w, h, seed)
        jambs(a, w, h)
        leaf(a, 20, w - 20, h, IRON if iron else color, bands=not iron, handle_at=w - 40, studs=studs or iron)
        return a.image()

    return make


def double_door(seed=1402, color=DOOR, w=SW, h=84, studs=False):
    def make():
        a = Art(w, h, seed)
        jambs(a, w, h)
        leaf(a, 20, w / 2 - 1, h, color, handle_at=w / 2 - 20, studs=studs)
        leaf(a, w / 2 + 1, w - 20, h, color, handle_at=w / 2 + 20, studs=studs)
        return a.image()

    return make


def open_door(seed=1403, double=False):
    w = SW if double else T
    span = (w - 40) / (2 if double else 1)
    h = int(30 + span * 0.95 + 16)

    def make():
        a = Art(w, h, seed)
        a.shape(rect(4, 24, w - 4, 36), shade(FRAME, 0.25), outline=DETAIL, corner=2, depth=2, mottle=0)
        for x0 in (2, w - 20):
            a.shape(rect(x0, 10, x0 + 18, 50), FRAME, outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.35)
        hinges = [(20, -1)] + ([(w - 20, 1)] if double else [])
        for hx, side in hinges:
            ang = 1.3 if side < 0 else math.pi - 1.3
            if side < 0:
                swing(a, hx, 30, span, 0.08, ang - 0.05)
            else:
                swing(a, hx, 30, span, ang + 0.05, math.pi - 0.08)
            x1, y1 = hx + span * math.cos(ang), 30 + span * math.sin(ang)
            ux, uy = math.cos(ang), math.sin(ang)
            px, py = -uy * 8, ux * 8
            a.shape([(hx + px, 30 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (hx - px, 30 - py)], DOOR, outline=DETAIL * 1.4, corner=2, depth=2, light_k=0.4)
            hx2, hy2 = hx + (span - 20) * ux, 30 + (span - 20) * uy
            for s_ in (-1, 1):
                a.shape(ellipse(hx2 + s_ * px * 1.3, hy2 + s_ * py * 1.3, 5, 4, 16), BRASS, outline=FINE * 1.3, depth=1, mottle=0)
        return a.image()

    return make

def cell_door(seed=1404):
    w, h = T, 80

    def make():
        a = Art(w, h, seed)
        jambs(a, w, h, rgb("#7f7a72"))
        a.shape(rect(20, h / 2 - 7, w - 20, h / 2 + 7), IRON, outline=DETAIL * 1.3, corner=2, depth=2, light_k=0.4, mottle=0)
        for x in range(34, w - 20, 18):
            a.shape(ellipse(x, h / 2, 5, 5, 12), shade(IRON, 0.1), outline=FINE * 1.2, depth=1, light_k=0.5, mottle=0)
        a.shape(rect(w - 48, h / 2 - 12, w - 32, h / 2 + 12), BRASS, outline=FINE * 1.3, corner=2, depth=1, mottle=0)
        return a.image()

    return make


def portcullis(seed=1405):
    w, h = SW, 80

    def make():
        a = Art(w, h, seed)
        jambs(a, w, h, rgb("#8a857d"), depth=26)
        a.shape(rect(26, h / 2 - 10, w - 26, h / 2 + 10), shade(IRON, 0.2), outline=DETAIL * 1.4, corner=2, depth=2, mottle=0)
        for x in range(40, w - 26, 22):
            a.shape([(x - 5, h / 2 - 10), (x + 5, h / 2 - 10), (x + 5, h / 2 + 10), (x, h / 2 + 16), (x - 5, h / 2 + 10)], IRON, outline=FINE * 1.3, corner=1, depth=1, light_k=0.5, mottle=0)
        return a.image()

    return make


def secret_door(seed=1406):
    w, h = T, 72

    def make():
        a = Art(w, h, seed)
        stone = rgb("#a39d93")
        # One stretch of wall: a mortar body with the ink outline, blocks
        # inside it separated by thin joints.
        a.shape(rect(1, 7, w - 1, h - 7), grout(stone), outline=DETAIL * 1.4, corner=4, depth=2, shade_k=0.2, light_k=0, ao=0.1, mottle=0)
        x = 0.0
        for wdt in split(w, a.rng, 44, 70):
            c = vary(a.rng, stone, 0.045)
            a.shape(rect(max(x, 3) + 0.9, 9, min(x + wdt, w - 3) - 0.9, h - 9), c, outline=JOINT, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA, corner=2, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1)
            x += wdt
        # The seams of the hidden door, a little darker, and a hidden catch.
        a.ink([(40, 10), (40, h - 10)], DETAIL, color=shade(stone, 0.5), alpha=0.8)
        a.ink([(w - 40, 10), (w - 40, h - 10)], DETAIL, color=shade(stone, 0.5), alpha=0.8)
        dot(a, w - 52, h / 2, 4, shade(stone, 0.5))
        return a.image()

    return make


def arch(seed=1407, color=rgb("#a39d93"), w=T, h=80, keystone=True):
    def make():
        a = Art(w, h, seed)
        for x0 in (2, w - 32):
            a.shape(rect(x0, 6, x0 + 30, h - 6), color, outline=DETAIL * 1.4, corner=6, depth=5, light_k=0.4)
        # The arch's voussoirs over the opening, seen from above as a band.
        a.shape(rect(30, h / 2 - 10, w - 30, h / 2 + 10), tint(color, 0.08), outline=DETAIL * 1.2, corner=4, depth=3, detail=lambda art, p: [art.ink([(x, h / 2 - 10), (x, h / 2 + 10)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False) for x in range(48, w - 30, 22)])
        if keystone:
            a.shape(rect(w / 2 - 10, h / 2 - 14, w / 2 + 10, h / 2 + 14), tint(color, 0.15), outline=DETAIL * 1.2, corner=2, depth=2)
        return a.image()

    return make


def window(seed=1408, kind="glass", w=T, h=70):
    def make():
        a = Art(w, h, seed)
        jambs(a, w, h, FRAME, depth=16)
        if kind == "glass":
            a.shape(rect(18, h / 2 - 6, w - 18, h / 2 + 6), rgb("#a9cfdc"), outline=DETAIL * 1.2, corner=2, depth=1, light_k=0.6, mottle=0)
            a.ink([(w / 2, h / 2 - 6), (w / 2, h / 2 + 6)], DETAIL, taper=False)
            a.ink([(30, h / 2 - 2), (60, h / 2 - 2)], FINE * 1.3, color=(250, 250, 250), alpha=0.9, taper=False)
        elif kind == "stained":
            cols = [rgb("#c8443a"), rgb("#4f74a8"), rgb("#e2c068"), rgb("#5f8f6a")]
            n = 8
            for k in range(n):
                x0 = 18 + (w - 36) * k / n
                a.shape(rect(x0, h / 2 - 6, x0 + (w - 36) / n, h / 2 + 6), cols[k % 4], outline=DETAIL, corner=1, depth=1, light_k=0.5, mottle=0)
        elif kind == "shutters":
            a.shape(rect(18, h / 2 - 5, w - 18, h / 2 + 5), rgb("#a9cfdc"), outline=DETAIL, corner=2, depth=1, light_k=0.6, mottle=0)
            L = (w - 36) / 2 - 6
            for hx, t in ((18, 0.32), (w - 18, math.pi - 0.32)):
                x1, y1 = hx + L * math.cos(t), h / 2 + 6 + L * math.sin(t)
                ux, uy = math.cos(t), math.sin(t)
                px, py = -uy * 5, ux * 5
                a.shape([(hx + px, h / 2 + 6 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (hx - px, h / 2 + 6 - py)], rgb("#5f8f6a"), outline=DETAIL * 1.2, corner=1, depth=1, light_k=0.4, mottle=0)
        elif kind == "slit":
            a.shape(rect(18, h / 2 - 8, w - 18, h / 2 + 8), rgb("#8a857d"), outline=DETAIL * 1.2, corner=2, depth=2)
            a.shape(rect(w / 2 - 22, h / 2 - 3, w / 2 + 22, h / 2 + 3), rgb("#1e1a18"), outline=FINE, corner=1, depth=1, mottle=0)
        return a.image()

    return make


def curtain_doorway(seed=1409):
    w, h = T, 80

    def make():
        a = Art(w, h, seed)
        jambs(a, w, h)
        cloth = rgb("#a8483a")
        pts = [(20, h / 2 - 6)]
        for k in range(17):
            x = 20 + (w - 40) * k / 16
            pts.append((x, h / 2 - 6 + (5 if k % 2 else -1)))
        pts += [(w - 20, h / 2 + 8), (20, h / 2 + 8)]
        a.shape(pts, cloth, outline=DETAIL * 1.2, corner=1, depth=2, light_k=0.4)
        a.ink([(20, h / 2 - 10), (w - 20, h / 2 - 10)], DETAIL * 1.2, color=BRASS)
        return a.image()

    return make


def iron_gate(seed=1410, w=SW, h=70):
    def make():
        a = Art(w, h, seed)
        jambs(a, w, h, rgb("#8a857d"), depth=24)
        for x0, x1 in ((24, w / 2 - 2), (w / 2 + 2, w - 24)):
            a.ink([(x0, h / 2), (x1, h / 2)], DETAIL * 2.6, color=INK, taper=False, wob=0)
            a.ink([(x0, h / 2), (x1, h / 2)], DETAIL * 1.5, color=IRON, taper=False, wob=0)
            for x in range(int(x0) + 12, int(x1), 18):
                a.shape(ellipse(x, h / 2, 5, 5, 12), IRON, outline=FINE * 1.1, depth=1, light_k=0.5, mottle=0)
        return a.image()

    return make


def barricaded_door(seed=1411):
    w, h = T, 90

    def make():
        a = Art(w, h, seed)
        jambs(a, w, h)
        leaf(a, 20, w - 20, h, DOOR, handle_at=None)
        for x0, y0, x1, y1 in ((14, 20, w - 30, h - 24), (30, h - 20, w - 14, 24), (10, h / 2 + 16, w - 10, h / 2 + 10)):
            ang = math.atan2(y1 - y0, x1 - x0)
            px, py = -math.sin(ang) * 7, math.cos(ang) * 7
            a.shape([(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)], vary(a.rng, rgb("#b8915a"), 0.06), outline=DETAIL * 1.2, corner=2, depth=2)
            for t in (0.12, 0.88):
                dot(a, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 2.4)
        return a.image()

    return make


def broken_door(seed=1412):
    w, h = T, 90

    def make():
        a = Art(w, h, seed)
        jambs(a, w, 60)
        # A splintered stub on the hinge and pieces scattered.
        a.shape([(20, 22), (80, 22), (70, 30), (90, 34), (20, 38)], DOOR, outline=DETAIL * 1.3, corner=1, depth=2)
        for _ in range(5):
            x, y = a.rng.uniform(60, w - 40), a.rng.uniform(46, h - 10)
            L = a.rng.uniform(26, 50)
            t = a.rng.uniform(-0.6, 0.6)
            px, py = -math.sin(t) * 6, math.cos(t) * 6
            a.shape([(x + px, y + py), (x + L * math.cos(t) + px, y + L * math.sin(t) + py), (x + L * math.cos(t) - px, y + L * math.sin(t) - py), (x - px, y - py)], vary(a.rng, DOOR, 0.06), outline=DETAIL * 1.1, corner=1, depth=1)
        return a.image()

    return make


def round_door(seed=1413):
    w, h = T, 80

    def make():
        a = Art(w, h, seed)
        jambs(a, w, h, rgb("#8a857d"))
        green = rgb("#5f8f4a")
        a.shape(rect(20, h / 2 - 9, w - 20, h / 2 + 9), green, outline=DETAIL * 1.4, corner=9, depth=3, light_k=0.4, detail=lambda art, p: [art.ink([(x, h / 2 - 8), (x, h / 2 + 8)], FINE, color=shade(green, 0.45), alpha=0.8, taper=False) for x in range(44, w - 20, 26)])
        a.shape(ellipse(w / 2, h / 2 - 14, 7, 6, 16), BRASS, outline=FINE * 1.3, depth=1, mottle=0)
        a.shape(ellipse(w / 2, h / 2 + 14, 7, 6, 16), BRASS, outline=FINE * 1.3, depth=1, mottle=0)
        return a.image()

    return make


PORTALS = {
    "Wooden Door": portal_wood_door(1421),
    "Dark Wooden Door": portal_wood_door(1422, rgb("#6e4a2f")),
    "Studded Door": portal_wood_door(1423, rgb("#8a5e3a"), studs=True),
    "Iron Door": portal_wood_door(1424, iron=True),
    "Double Door": double_door(1425),
    "Reinforced Gate": double_door(1426, rgb("#7a5233"), studs=True, h=96),
    "Open Door": open_door(1427),
    "Open Double Door": open_door(1428, double=True),
    "Cell Door": cell_door(),
    "Portcullis": portcullis(),
    "Secret Door": secret_door(),
    "Stone Arch": arch(1429),
    "Wooden Arch": arch(1430, rgb("#8a6040"), keystone=False),
    "Glass Window": window(1431, "glass"),
    "Shuttered Window": window(1432, "shutters", h=110),
    "Stained Glass Window": window(1433, "stained"),
    "Arrow Slit": window(1434, "slit"),
    "Curtain Doorway": curtain_doorway(),
    "Iron Gate": iron_gate(),
    "Barricaded Door": barricaded_door(),
    "Broken Door": broken_door(),
    "Round Door": round_door(),
}


# -- caves (light greys, tinted by the cave's colour) ----------------------------------------------


def cave_floor(seed, base=rgb("#d2d0cb"), patches=36, pebbles=60, cracks=0, sand=False, crystals=0, moss=0, dots=400, slabs=False, mushrooms=0, puddles=0):
    s = SW
    a = Art(s, s, seed, tile=True, bg=base)
    for _ in range(patches):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(20, 50), a.rng, 12, 0.3), mix(base, rgb("#bcbab4") if a.rng.random() < 0.5 else rgb("#dedcd7"), 0.6), outline=0, smooth=True, depth=2, shade_k=0, light_k=0, ao=0, mottle=0.04)
    if slabs:
        for (cx, cy), poly in voronoi_cells(s, s, 5, 5, a.rng, 0.35):
            a.shape(inset(poly, 4), vary(a.rng, base, 0.04), outline=DETAIL * 1.2, corner=10, depth=5, shade_k=0.4, light_k=0.3)
    if sand:
        for r in range(16):
            y = r * s / 16 + a.rng.uniform(-5, 5)
            a.ink([(x, y + 4 * math.sin(2 * math.pi * x / s * 3 + r)) for x in range(-20, s + 21, 16)], FINE * 1.1, color=shade(base, 0.3), alpha=0.7, wob=0.2)
    for _ in range(pebbles):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(3, 8), a.rng, 9, 0.25), shade(base, 0.12), outline=DETAIL * 0.8, smooth=True, depth=2, shade_k=0.4, light_k=0.4, mottle=0)
    for _ in range(cracks):
        crack(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0, 6.28), a.rng.uniform(40, 90), width=FINE * 1.2)
    for _ in range(crystals):
        x, y, r = a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(6, 12)
        pts = [(x + r * math.cos(k * math.pi / 3), y + r * math.sin(k * math.pi / 3)) for k in range(6)]
        a.shape(pts, tint(base, 0.25), outline=DETAIL * 0.9, corner=1, depth=2, light_k=0.6, mottle=0)
    for _ in range(moss):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(14, 30), a.rng, 10, 0.35), shade(base, 0.2), outline=DETAIL * 0.7, smooth=True, depth=3, shade_k=0.2, light_k=0.3, ao=0, mottle=0.1, detail=lambda art, p: speckles(art, p, shade(base, 0.45), 30, (0.6, 1.3), 0.7))
    for _ in range(puddles):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(18, 40), a.rng, 11, 0.25), tint(base, 0.12), outline=DETAIL * 0.9, smooth=True, depth=4, shade_k=0, light_k=0, ao=0.5, mottle=0,
                detail=lambda art, p, x=x, y=y: art.ink([(x - 10, y - 4), (x + 6, y - 7)], FINE * 1.3, color=(250, 250, 250), alpha=0.9))
    for _ in range(mushrooms):
        cx, cy = a.rng.uniform(0, s), a.rng.uniform(0, s)
        for _ in range(a.rng.randint(2, 4)):
            x, y, r = cx + a.rng.uniform(-14, 14), cy + a.rng.uniform(-14, 14), a.rng.uniform(4, 9)
            a.shape(ellipse(x, y, r, r, 20), tint(base, 0.2), outline=DETAIL * 0.8, depth=2, light_k=0.5, mottle=0)
            dot(a, x - r * 0.3, y - r * 0.3, r * 0.25, shade(base, 0.25))
    for _ in range(dots):
        dot(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0.5, 1.1), rgb("#8c8983"), 0.45)
    return a.image()


def cave_wall(seed, base=rgb("#bebbb4"), h=72, kind="rocks"):
    a = strip(seed, h)
    if kind == "strata":
        for r in range(2):
            y0 = 6 + r * (h - 12) / 2
            y1 = y0 + (h - 12) / 2
            x = a.rng.uniform(0, SW)
            for wdt in split(SW, a.rng, 50, 110):
                pts = [(x + 2, y0 + 2 + a.rng.uniform(-1, 2)), (x + wdt - 2, y0 + 2 + a.rng.uniform(-1, 2)), (x + wdt - 2 + a.rng.uniform(-4, 4), y1 - 2), (x + 2 + a.rng.uniform(-4, 4), y1 - 2)]
                a.shape(pts, vary(a.rng, base, 0.06), outline=DETAIL * 1.2, corner=4, wob=1.2, depth=4, shade_k=0.55, light_k=0.3, var=0.1)
                x += wdt
        return a.image()
    if kind == "icicles":
        band(a, 8, h - 8, base, outline=DETAIL * 1.2)
        x = 0.0
        while x < SW:
            r = a.rng.uniform(8, 14)
            a.shape([(x - r, h / 2 - 4), (x + r, h / 2 - 4), (x, h / 2 + r * 1.4)], tint(base, 0.2), outline=DETAIL * 0.9, corner=1, depth=2, light_k=0.5, mottle=0)
            x += r * 1.8
        return a.image()
    if kind == "crystals":
        band(a, 10, h - 10, shade(base, 0.08), outline=DETAIL)
        x = 0.0
        while x < SW:
            r = a.rng.uniform(10, 18)
            cy = a.rng.uniform(r + 4, h - r - 4)
            pts = [(x + r * math.cos(k * math.pi / 3 + 0.3), cy + r * math.sin(k * math.pi / 3 + 0.3)) for k in range(6)]
            a.shape(pts, tint(base, 0.25), outline=DETAIL, corner=1, depth=3, light_k=0.6, mottle=0)
            x += r * 1.6
        return a.image()
    jag = {"rocks": 0.25, "jagged": 0.45, "smooth": 0.1, "boulders": 0.12}[kind]
    size = {"rocks": (26, 48), "jagged": (20, 36), "smooth": (40, 70), "boulders": (44, 70)}[kind]
    x = 0.0
    while x < SW:
        bw = a.rng.uniform(*size)
        pts = blob(x + bw / 2, h / 2, bw / 2 + 3, a.rng, 10, jag, ry=h / 2 - 6)
        pts = [(px, min(h - 4, max(4, py))) for px, py in pts]
        a.shape(pts, mix(base, rgb("#a9a69f"), a.rng.random()), outline=DETAIL * 1.3, corner=3, depth=4, shade_k=0.55, light_k=0.3, var=0.1)
        x += bw * 0.8
    return a.image()


def cave(seed, floor_kw, wall_kw):
    def make():
        return cave_floor(seed, **floor_kw), cave_wall(seed + 50, **wall_kw)

    return make


CAVES = {
    "Rocky Cave": cave(1501, {}, {}),
    "Pebbly Cave": cave(1502, {"pebbles": 220}, {"kind": "smooth"}),
    "Cracked Cave": cave(1503, {"cracks": 18, "pebbles": 20}, {"kind": "jagged"}),
    "Crystal Cave": cave(1504, {"crystals": 30}, {"kind": "crystals"}),
    "Mossy Cave": cave(1505, {"moss": 26, "pebbles": 30}, {}),
    "Sandy Cave": cave(1506, {"sand": True, "pebbles": 20, "patches": 20, "base": rgb("#dcd8cc")}, {"kind": "smooth", "base": rgb("#c8c2b4")}),
    "Icy Cave": cave(1507, {"cracks": 10, "pebbles": 0, "base": rgb("#dfe3e6"), "dots": 120}, {"kind": "icicles", "base": rgb("#d4dadf")}),
    "Volcanic Cave": cave(1508, {"cracks": 24, "base": rgb("#a8a4a0"), "pebbles": 80}, {"kind": "jagged", "base": rgb("#8f8a86")}),
    "Muddy Cave": cave(1509, {"patches": 60, "pebbles": 20, "base": rgb("#c9c4ba")}, {"kind": "smooth", "base": rgb("#b4ada2")}),
    "Smooth Stone Cave": cave(1510, {"patches": 12, "pebbles": 10, "dots": 150}, {"kind": "smooth"}),
    "Boulder Cave": cave(1511, {"pebbles": 30}, {"kind": "boulders"}),
    "Gravel Cave": cave(1512, {"pebbles": 400, "patches": 10}, {"kind": "rocks"}),
    "Limestone Cave": cave(1513, {"slabs": True, "pebbles": 10, "base": rgb("#dedad0")}, {"kind": "strata", "base": rgb("#ccc6b8")}),
    "Slate Cave": cave(1514, {"slabs": True, "pebbles": 0, "base": rgb("#bdbcbc"), "cracks": 8}, {"kind": "strata", "base": rgb("#a8a6a6")}),
    "Fungal Cave": cave(1515, {"moss": 8, "pebbles": 20, "mushrooms": 18}, {"kind": "rocks"}),
    "Rooty Cave": cave(1516, {"cracks": 30, "pebbles": 40, "base": rgb("#d0ccc4")}, {"kind": "rocks", "base": rgb("#b8b2a8")}),
    "Dusty Cave": cave(1517, {"patches": 50, "pebbles": 30, "dots": 900}, {"kind": "rocks"}),
    "Wet Cave": cave(1518, {"patches": 40, "pebbles": 40, "puddles": 14, "base": rgb("#c8cbcc")}, {"kind": "smooth", "base": rgb("#b6b9ba")}),
    "Ancient Cave": cave(1519, {"slabs": True, "cracks": 12, "pebbles": 30}, {"kind": "boulders"}),
    "Jagged Cave": cave(1520, {"cracks": 10, "pebbles": 120}, {"kind": "jagged"}),
}


# -- roofs -------------------------------------------------------------------------------------------


def roof_tiles(seed, base, kind="shingle", rows=10, gap=None):
    s = SW
    a = Art(s, s, seed, tile=True, bg=shade(base, 0.3) if gap is None else gap)
    h = s / rows
    if kind == "thatch":
        for r in range(rows):
            y = r * h
            band(a, y + 1, y + h + 1, vary(a.rng, base, 0.04), outline=DETAIL * 1.1)
            for _ in range(170):
                x = a.rng.uniform(0, s)
                yy = y + a.rng.uniform(2, h - 4)
                c = shade(base, a.rng.uniform(0.25, 0.55)) if a.rng.random() < 0.7 else tint(base, 0.35)
                a.ink([(x, yy), (x + a.rng.uniform(-3, 3), yy + a.rng.uniform(12, 24))], FINE * 1.1, color=c, alpha=0.85, wob=0.2)
        return a.image()
    if kind == "copper":
        a.tile = False
        a.shape(rect(-10, -10, s + 10, s + 10), base, outline=0, corner=0, wob=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.tile = True
        for x in range(0, s, 64):
            a.ink([(x, -10), (x, s + 10)], DETAIL * 1.2, color=shade(base, 0.45), taper=False, wob=0.2)
            a.ink([(x + 4, -10), (x + 4, s + 10)], FINE, color=tint(base, 0.4), taper=False, wob=0.2)
        return a.image()
    for r in range(rows):
        w = {"shingle": h * 1.2, "slate": h * 1.6, "clay": h * 0.9, "scale": h * 1.0, "stone": h * 2.2, "bark": h * 1.4}[kind]
        n = max(1, round(s / w))
        w = s / n  # a whole number of tiles per row, so the row wraps cleanly
        x = 0 if r % 2 == 0 else -w / 2
        for _ in range(n):
            c = vary(a.rng, mix(base, tint(base, 0.2) if a.rng.random() < 0.5 else shade(base, 0.12), a.rng.uniform(0.2, 0.8)), 0.03)
            y0 = r * h
            if kind == "shingle":
                pts = [(x + 2, y0), (x + w - 2, y0), (x + w - 2, y0 + h * 0.85), (x + w / 2, y0 + h - 1), (x + 2, y0 + h * 0.85)]
            elif kind == "slate":
                pts = rect(x + 2, y0, x + w - 2, y0 + h - 1)
            elif kind == "clay":
                pts = [(x + 2, y0)] + [(x + w / 2 + (w / 2 - 2) * math.cos(t), y0 + h * 0.7 + h * 0.3 * math.sin(t)) for t in [math.pi * k / 8 for k in range(9)]][::-1] + [(x + w - 2, y0)]
                pts = [(x + 2, y0), (x + w - 2, y0)] + [(x + w / 2 + (w / 2 - 2) * math.cos(t), y0 + h * 0.65 + h * 0.34 * math.sin(t)) for t in [math.pi * k / 8 for k in range(9)]]
            elif kind == "scale":
                pts = [(x + 1, y0)] + [(x + w - 1, y0)] + [(x + w / 2 + (w / 2 - 1) * math.cos(t), y0 + h * 0.5 + h * 0.5 * math.sin(t)) for t in [math.pi * k / 10 for k in range(11)]]
            elif kind == "stone":
                pts = [(px + a.rng.uniform(-2, 2), py) for px, py in rect(x + 3, y0 + 1, x + w - 3, y0 + h - 1)]
            else:  # bark
                pts = [(x + 2, y0), (x + w - 2, y0 + a.rng.uniform(-2, 2)), (x + w - 4, y0 + h * 0.9), (x + w * 0.55, y0 + h), (x + 4, y0 + h * 0.92)]
            det = None
            if kind == "clay":
                det = lambda art, p, x=x, y0=y0, w=w, c=c: art.ink([(x + w * 0.3, y0 + 4), (x + w * 0.3, y0 + h * 0.8)], FINE * 1.3, color=tint(c, 0.35), alpha=0.8, taper=False)
            elif kind in ("bark", "stone"):
                det = lambda art, p, c=c: speckles(art, p, shade(c, 0.45), 4)
            a.shape(pts, c, outline=DETAIL * 1.1, corner=2 if kind != "stone" else 5, wob=0.4, depth=3, shade_k=0.45, light_k=0.3, ao=0.1, mottle=0.03, detail=det, var=0.1)
            x += w
    return a.image()


def roof_line(seed, base, part, kind="cap"):
    h = {"edge": 30, "ridge": 40, "hip": 34}[part]
    a = strip(seed, h)
    col = shade(base, 0.12)
    if part == "edge" or kind == "band":
        band(a, 4, h - 4, col, outline=DETAIL * 1.3, light_k=0.25)
        if kind == "thatch":
            for _ in range(80):
                x = a.rng.uniform(0, SW)
                a.ink([(x, 6), (x + a.rng.uniform(-2, 2), h - 6)], FINE, color=shade(col, 0.4), alpha=0.7, wob=0.1)
        return a.image()
    x = 0.0
    step = 34 if part == "ridge" else 30
    while x < SW:
        a.shape(rect(x + 1, 3, x + step + 2, h - 3), mix(col, tint(col, 0.2), a.rng.random()), outline=DETAIL * 1.1, corner=h / 3, wob=0.3, depth=3, shade_k=0.45, light_k=0.3, var=0.1)
        x += step
    return a.image()


def roof(seed, base, kind="shingle", line_kind="cap", rows=10):
    def make():
        return (roof_tiles(seed, base, kind, rows), roof_line(seed + 1, base, "edge", line_kind), roof_line(seed + 2, base, "ridge", line_kind), roof_line(seed + 3, base, "hip", line_kind))

    return make


ROOFS = {
    "Wood Shingles": roof(1601, rgb("#8a5a3a")),
    "Dark Shingles": roof(1602, rgb("#5e4232")),
    "Mossy Shingles": roof(1603, rgb("#6f7a4a")),
    "Slate": roof(1604, rgb("#5d6670"), "slate", rows=12),
    "Blue Slate": roof(1605, rgb("#4f6680"), "slate", rows=12),
    "Black Slate": roof(1606, rgb("#3e4046"), "slate", rows=12),
    "Red Clay Tiles": roof(1607, rgb("#b0503a"), "clay", rows=11),
    "Orange Clay Tiles": roof(1608, rgb("#c8743e"), "clay", rows=11),
    "Brown Clay Tiles": roof(1609, rgb("#8a5a42"), "clay", rows=11),
    "Blue Glazed Tiles": roof(1610, rgb("#4f74a8"), "clay", rows=11),
    "Thatch": roof(1611, rgb("#c9a961"), "thatch", "thatch", rows=8),
    "Dark Thatch": roof(1612, rgb("#9a7f4e"), "thatch", "thatch", rows=8),
    "Reed": roof(1613, rgb("#b8ad6e"), "thatch", "thatch", rows=12),
    "Green Copper": roof(1614, rgb("#6fa08a"), "copper", "band"),
    "Stone Slabs": roof(1615, rgb("#9a958c"), "stone", rows=7),
    "Bark": roof(1616, rgb("#7a5a3e"), "bark", rows=9),
    "Fish Scale": roof(1617, rgb("#7f8a96"), "scale", rows=14),
    "Red Scale": roof(1618, rgb("#a8483a"), "scale", rows=14),
    "Gold Scale": roof(1619, rgb("#d6ae4c"), "scale", rows=14),
    "Green Scale": roof(1620, rgb("#5f8f5a"), "scale", rows=14),
}
