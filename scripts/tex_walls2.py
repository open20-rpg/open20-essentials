"""More walls for the built-in pack (strip + end cap, like tex_build.WALLS):
stone in many colours and sizes, brick bonds, timber, plaster, fences,
fantasy materials. Each strip repeats along x (512 px); 256 px = 1 tile."""

import math

from PIL import Image

from floors import speckles, split
from pen import DETAIL, FINE, INK, JOINT, JOINT_ALPHA, OUTLINE, Art, grout, joint_color, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary
from tex_build import SW, T, band, dot, end_block, rock_wall, strip, wall_blocks


# -- helpers --------------------------------------------------------------------------------------


def over(base, overlay):
    """Composite an overlay strip (same size) over a base strip image."""
    out = base.convert("RGBA").copy()
    out.alpha_composite(overlay.convert("RGBA"))
    return out


def blocks(seed, color, rows=2, lo=50, hi=90, h=64, cap=None, **kw):
    def make():
        return wall_blocks(seed, color, rows, lo, hi, h, **kw), end_block(seed + 1, cap or color, h)

    return make


def bricks(seed, color, mortar=rgb("#d9cbb2"), rows=3, lo=36, hi=46, h=60):
    def make():
        return wall_blocks(seed, color, rows=rows, lo=lo, hi=hi, h=h, mortar=mortar, corner=3, wob=0.5, cracks=0.1), end_block(seed + 1, color, h)

    return make


def stack_bricks(seed, color, mortar=rgb("#d9cbb2"), h=60, bw=40):
    """Stack bond: bricks lined up in columns (no stagger), on one solid wall
    body inked only along its long edges (same build as wall_blocks)."""

    def make():
        a = strip(seed, h)
        pad = 5
        band(a, pad, h - pad, grout(color, mortar), outline=0, light_k=0, shade_k=0.15)
        rows = 3
        rh = (h - 2 * pad) / rows
        n = int(SW // bw)
        cw = SW / n
        for r in range(rows):
            for k in range(n):
                x = k * cw
                y0, y1 = pad + r * rh, pad + (r + 1) * rh
                c = vary(a.rng, color, 0.045)
                a.shape(rect(x + 0.9, y0 + 0.9, x + cw - 0.9, y1 - 0.9), c, outline=JOINT, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA, corner=2, wob=0.25, depth=3, shade_k=0.35, light_k=0.25, ao=0.1, var=0.1)
        a.tile = False
        for y in (pad, h - pad):
            a.ink([(-60, y), (a.w + 60, y)], OUTLINE * 0.75, taper=False, wob=0.4, var=0.1)
        a.tile = True
        return a.image(), end_block(seed + 1, color, h)

    return make


def overlay_moss(seed, h, n=14, color=rgb("#6f9443"), leaves=False, flowers=None):
    a = strip(seed, h)
    for _ in range(n):
        x, y = a.rng.uniform(0, SW), a.rng.uniform(8, h - 8)
        r = a.rng.uniform(7, 16)
        pts = [(px, min(h - 3, max(3, py))) for px, py in blob(x, y, r, a.rng, 9, 0.3)]
        a.shape(pts, vary(a.rng, color, 0.06), outline=FINE * 1.2 if leaves else 0, smooth=True, depth=2, shade_k=0.3, light_k=0.35, ao=0, mottle=0.08)
    if leaves:
        x = a.rng.uniform(0, SW)
        for _ in range(3):
            pts = [(x + t * 6, h / 2 + 18 * math.sin(t * 0.35 + a.rng.uniform(0, 0.4))) for t in range(30)]
            pts = [(px, min(h - 4, max(4, py))) for px, py in pts]
            a.ink(pts, FINE * 1.6, color=shade(color, 0.5), alpha=0.9)
            for px, py in pts[::3]:
                t = a.rng.uniform(0, 6.28)
                a.shape(ellipse(px + 4 * math.cos(t), py + 4 * math.sin(t), 6, 3.5, 12, rot=t), tint(color, 0.1), outline=FINE, depth=1, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
            x += a.rng.uniform(140, 200)
    if flowers:
        for _ in range(20):
            x, y = a.rng.uniform(0, SW), a.rng.uniform(10, h - 10)
            dot(a, x, y, 3.2, flowers)
            dot(a, x, y, 1.2, rgb("#f6e08a"))
    return a.image()


def mossy(maker, seed, h, **kw):
    def make():
        strip_img, cap = maker()
        return over(strip_img, overlay_moss(seed, strip_img.height, **kw)), cap

    return make


def runes_over(seed, h, glow):
    a = strip(seed, h)
    x = a.rng.uniform(0, 60)
    while x < SW:
        y = h / 2 + a.rng.uniform(-6, 6)
        pts = [(x, y - 12), (x + a.rng.uniform(-7, 7), y), (x, y + 12)]
        a.ink(pts, DETAIL * 3.2, color=glow, alpha=0.3)
        a.ink(pts, DETAIL * 1.1, color=tint(glow, 0.45))
        a.ink([(x, y - 3), (x + 8, y - 9)], DETAIL * 0.9, color=tint(glow, 0.45))
        x += a.rng.uniform(46, 80)
    return a.image()


def runic(seed, color, glow):
    def make():
        s, cap = blocks(seed, color, rows=2, lo=60, hi=100)()
        return over(s, runes_over(seed + 7, s.height, glow)), cap

    return make


def obsidian(seed):
    col = rgb("#3a3440")

    def make():
        s, cap = blocks(seed, col, rows=2, lo=50, hi=90, corner=3, wob=0.4, cracks=0.2)()
        g = strip(seed + 3, s.height)
        for _ in range(26):
            x, y = g.rng.uniform(0, SW), g.rng.uniform(10, s.height - 10)
            g.ink([(x, y), (x + g.rng.uniform(4, 10), y - g.rng.uniform(2, 6))], FINE * 1.3, color=rgb("#c9b8e6"), alpha=0.7, wob=0)
        return over(s, g.image()), cap

    return make


def crenellated(seed, color):
    """Battlements from above: merlons (full-height blocks) alternate with
    crenels (lower, narrower), on a walkway band."""

    def make():
        h = 72
        a = strip(seed, h)
        band(a, 22, h - 6, shade(color, 0.12), outline=DETAIL * 1.2, light_k=0.1, shade_k=0.3, detail=lambda art: speckles(art, to_path(rect(0, 22, SW, h - 6)), shade(color, 0.45), 30))
        n = 8
        cw = SW / n
        for k in range(n):
            x = k * cw
            a.shape(rect(x + 3, 4, x + cw * 0.68, 38), vary(a.rng, color, 0.05), outline=DETAIL * 1.3, corner=4, depth=6, shade_k=0.55, light_k=0.4, ao=0.25, var=0.1, detail=lambda art, p: speckles(art, p, shade(color, 0.45), 4))
        return a.image(), end_block(seed + 1, color, h)

    return make


def log_wall(seed, bark, face, rows=2, mossy_=False, birch=False):
    def make():
        h = 66
        a = strip(seed, h)
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
                        col = INK if birch else shade(c, 0.55)
                        w = FINE * (1.6 if birch else 1.0)
                        art.ink([(x0, yy), (x0 + L * (0.3 if birch else 1), yy + art.rng.uniform(-1.5, 1.5))], w, color=col, alpha=0.7, wob=0.3)
                        x0 += L + art.rng.uniform(15, 50)

            band(a, y0 + 1, y1 - 1, c, detail=lines)
        img = a.image()
        if mossy_:
            img = over(img, overlay_moss(seed + 5, h, 12))
        return img, end_block(seed + 1, face, h, round_=True, rings=True)

    return make


def planks(seed, color, h=56, vertical=True, battens=False):
    """A plank wall from above: boards in a row along the wall."""

    def make():
        a = strip(seed, h)

        def seams(art):
            if vertical:
                x = 0.0
                for wd in split(SW, art.rng, 26, 40):
                    art.ink([(x, 6), (x, h - 6)], JOINT * 1.3, color=joint_color(color), alpha=JOINT_ALPHA, taper=False, wob=0.2)
                    x += wd
            else:
                art.ink([(-10, h / 2), (SW + 10, h / 2)], JOINT * 1.3, color=joint_color(color), alpha=JOINT_ALPHA, taper=False, wob=0, var=0.0)
            for _ in range(24):
                x, y = art.rng.uniform(0, SW), art.rng.uniform(10, h - 10)
                art.ink([(x, y), (x + art.rng.uniform(12, 30), y + art.rng.uniform(-1, 1))], FINE * 0.8, color=shade(color, 0.45), alpha=0.6)

        band(a, 5, h - 5, color, detail=seams)
        if battens:
            for x in range(0, SW, 64):
                a.shape(rect(x - 5, 3, x + 5, h - 3), shade(color, 0.15), outline=DETAIL, corner=2, depth=2, var=0.1)
        return a.image(), end_block(seed + 1, shade(color, 0.1), h)

    return make


def palisade(seed, wood, r=27):
    def make():
        h = 64
        a = strip(seed, h)
        n = int(SW // (2 * r - 2))
        step = SW / n
        rr = step / 2 + 1
        for k in range(n):
            cx = k * step + step / 2
            col = vary(a.rng, wood, 0.07)
            pts = ellipse(cx, h / 2, rr - 1, rr - 1, 32)
            a.fill_path(to_path(pts), col)
            for j in range(6):
                t0, t1 = 2 * math.pi * j / 6, 2 * math.pi * (j + 1) / 6
                face = [(cx + (rr - 1) * math.cos(t0), h / 2 + (rr - 1) * math.sin(t0)), (cx + (rr - 1) * math.cos(t1), h / 2 + (rr - 1) * math.sin(t1)), (cx, h / 2)]
                lit = math.cos((t0 + t1) / 2 + math.pi * 0.75)
                a.fill_path(to_path(face), tint(col, 0.22 * lit) if lit > 0 else shade(col, -0.28 * lit))
            a.ink(pts, DETAIL * 1.3, closed=True, wob=0.2, var=0.08)
        return a.image(), end_block(seed + 1, wood, h, round_=True, rings=True)

    return make


def wattle(seed, daub=None):
    """Wattle (woven withies between stakes), optionally daubed with mud."""

    def make():
        h = 56
        a = strip(seed, h)
        wood = rgb("#8a6a40")
        if daub:
            band(a, 6, h - 6, daub, outline=DETAIL * 1.2, detail=lambda art: speckles(art, to_path(rect(0, 6, SW, h - 6)), shade(daub, 0.4), 40))
        stakes = list(range(0, SW, 32))
        for k in range(3):
            y = 14 + k * 14
            pts = [(x, y + (6 if (x // 32 + k) % 2 else -6)) for x in range(-32, SW + 33, 16)]
            pts = chaikin(pts, False, 2)
            al = 0.45 if daub else 1.0
            a.ink(pts, 9, color=INK, alpha=al, taper=False, wob=0.2)
            a.ink(pts, 5.5, color=vary(a.rng, rgb("#b08a5a"), 0.06), alpha=al, taper=False, wob=0.2)
        for x in stakes:
            a.shape(ellipse(x, h / 2, 6, 6, 16), wood, outline=DETAIL, depth=2, mottle=0)
        return a.image(), end_block(seed + 1, daub or wood, h)

    return make


def plaster(seed, color, post=rgb("#6e4a2f"), straw=False, every=T, h=62, braces=False):
    def make():
        a = strip(seed, h)

        def tex(art):
            if straw:
                for _ in range(120):
                    x, y = art.rng.uniform(0, SW), art.rng.uniform(8, h - 8)
                    t = art.rng.uniform(0, 6.28)
                    art.ink([(x, y), (x + 6 * math.cos(t), y + 6 * math.sin(t))], FINE * 0.8, color=shade(color, 0.35), alpha=0.6, wob=0.1)
            for _ in range(8):
                x = art.rng.uniform(0, SW)
                y = art.rng.uniform(12, h - 12)
                art.ink([(x, y), (x + art.rng.uniform(6, 14), y + art.rng.uniform(-3, 3))], FINE * 0.9, color=shade(color, 0.4), alpha=0.6)

        band(a, 5, h - 5, color, detail=tex)
        if post:
            for x in range(0, SW, every):
                a.shape(rect(x - 9, 3, x + 9, h - 3), post, outline=DETAIL * 1.2, corner=3, depth=3, var=0.1)
            if braces:
                for x in range(0, SW, every):
                    a.ink([(x + 12, h - 9), (x + every * 0.4, 9)], 9, color=INK, taper=False, wob=0)
                    a.ink([(x + 12, h - 9), (x + every * 0.4, 9)], 5, color=post, taper=False, wob=0)
        return a.image(), end_block(seed + 1, post or color, h)

    return make


def thatch_topped(seed, base=rgb("#c9a36a")):
    def make():
        h = 64
        a = strip(seed, h)
        straw = rgb("#d6b56a")

        def strokes(art):
            for _ in range(500):
                x, y = art.rng.uniform(0, SW), art.rng.uniform(8, h - 8)
                art.ink([(x, y), (x + art.rng.uniform(-3, 3), y + art.rng.uniform(8, 14))], FINE, color=shade(straw, art.rng.uniform(0.1, 0.45)), alpha=0.8, wob=0.1)

        band(a, 5, h - 5, straw, detail=strokes)
        a.tile = False
        a.ink([(-10, h / 2), (SW + 10, h / 2)], DETAIL * 1.6, color=rgb("#8a6a40"), taper=False, wob=0, var=0.0)
        a.tile = True
        return a.image(), end_block(seed + 1, straw, h)

    return make


def hedge(seed, green, flowers=None, h=70):
    def make():
        a = strip(seed, h)
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
        if flowers:
            for _ in range(40):
                x, y = a.rng.uniform(0, SW), a.rng.uniform(12, h - 12)
                dot(a, x, y, 3.4, flowers)
                dot(a, x, y, 1.3, rgb("#f6e08a"))
        cap = Art(h, h, seed + 1)
        cap.shape(blob(h / 2, h / 2, h / 2 - 6, cap.rng, 10, 0.12), green, outline=OUTLINE * 0.8, smooth=True, depth=6)
        return a.image(), cap.image()

    return make


def thorns(seed):
    def make():
        h = 64
        a = strip(seed, h)
        stem = rgb("#5a4a2e")
        for k in range(5):
            y0 = a.rng.uniform(14, h - 14)
            ph = a.rng.uniform(0, 6.28)
            f = 2 * math.pi * a.rng.choice((2, 3, 4)) / SW
            pts = [(x, y0 + 14 * math.sin(f * x + ph)) for x in range(-20, SW + 21, 8)]
            pts = [(px, min(h - 6, max(6, py))) for px, py in pts]
            a.ink(pts, 8, color=INK, taper=False, wob=0.2)
            a.ink(pts, 4.5, color=stem, taper=False, wob=0.2)
            for px, py in pts[::2]:
                t = a.rng.uniform(0, 6.28)
                a.ink([(px, py), (px + 8 * math.cos(t), py + 8 * math.sin(t))], FINE * 1.5, color=INK, taper=True)
        for _ in range(16):
            x, y = a.rng.uniform(0, SW), a.rng.uniform(10, h - 10)
            a.shape(ellipse(x, y, 6, 3.5, 12, rot=a.rng.uniform(0, 3)), rgb("#4f7c34"), outline=FINE, depth=1, mottle=0)
        cap = Art(h, h, seed + 1)
        cap.shape(blob(h / 2, h / 2, h / 2 - 8, cap.rng, 9, 0.2), stem, outline=OUTLINE * 0.7, smooth=True, depth=4)
        return a.image(), cap.image()

    return make


def roots(seed):
    def make():
        h = 70
        a = strip(seed, h)
        wood = rgb("#7a5a3e")
        band(a, 10, h - 10, rgb("#5a4632"), outline=DETAIL, light_k=0, shade_k=0.3)
        for k in range(6):
            y0 = a.rng.uniform(16, h - 16)
            ph = a.rng.uniform(0, 6.28)
            f = 2 * math.pi * a.rng.choice((1, 2, 3)) / SW
            w = a.rng.uniform(10, 18)
            pts = [(x, y0 + 12 * math.sin(f * x + ph)) for x in range(-20, SW + 21, 8)]
            pts = [(px, min(h - 6 - w / 2, max(6 + w / 2, py))) for px, py in pts]
            a.ink(pts, w + 6, color=INK, taper=False, wob=0.3)
            a.ink(pts, w, color=vary(a.rng, wood, 0.08), taper=False, wob=0.3)
            a.ink(pts, max(1.5, w * 0.18), color=tint(wood, 0.3), alpha=0.7, taper=False, wob=0.3)
        cap = Art(h, h, seed + 1)
        cap.shape(blob(h / 2, h / 2, h / 2 - 7, cap.rng, 9, 0.2), wood, outline=OUTLINE * 0.8, smooth=True, depth=5)
        return a.image(), cap.image()

    return make


def coral(seed, cols):
    def make():
        h = 66
        a = strip(seed, h)
        band(a, 8, h - 8, rgb("#d8c6a0"), outline=DETAIL, light_k=0, shade_k=0.2)
        x = 0.0
        while x < SW:
            r = a.rng.uniform(12, 20)
            y = a.rng.uniform(r + 6, h - r - 6)
            c = a.rng.choice(cols)
            a.shape(blob(x, y, r, a.rng, 12, 0.35), c, outline=DETAIL, smooth=True, depth=3, light_k=0.4, mottle=0.04)
            for _ in range(4):
                dot(a, x + a.rng.uniform(-r * 0.5, r * 0.5), y + a.rng.uniform(-r * 0.5, r * 0.5), 2.2, shade(c, 0.4), 0.8)
            x += r * 1.2
        return a.image(), end_block(seed + 1, cols[0], h)

    return make


def crystal(seed, color):
    from tex_build import crystal_wall

    return lambda: crystal_wall(seed, color)


def ice(seed, color, lo=60, hi=110):
    def make():
        img = wall_blocks(seed, color, rows=2, lo=lo, hi=hi, h=64, corner=10, wob=1.4, cracks=0.6)
        return img, end_block(seed + 1, color, 64)

    return make


def sandbags(seed, color):
    def make():
        h = 64
        a = strip(seed, h)
        for r in range(2):
            y0 = 6 + r * 26
            x = 0.0 if r == 0 else -32.0
            n = int(SW // 64)
            for k in range(n + 1):
                cx = x + k * 64 + 32
                pts = chaikin(rect(cx - 30, y0, cx + 30, y0 + 26), True, 3)
                a.shape(pts, vary(a.rng, color, 0.06), outline=DETAIL * 1.2, corner=0, depth=4, light_k=0.4, mottle=0.04)
                a.ink([(cx - 22, y0 + 6), (cx - 26, y0 + 13)], FINE, color=shade(color, 0.45), alpha=0.8)
        return a.image(), end_block(seed + 1, color, h)

    return make


def rail_fence(seed, wood, rails=2, split_rail=False):
    def make():
        h = 44
        a = strip(seed, h)
        for k in range(rails):
            y = h / 2 + (k - (rails - 1) / 2) * 9
            a.tile = False
            # Full-width lines: no wobble or width change, so the ends meet at the wrap.
            a.ink([(-10, y), (SW + 10, y)], 11, color=INK, taper=False, wob=0, var=0.0)
            a.ink([(-10, y), (SW + 10, y)], 7, color=vary(a.rng, wood, 0.05), taper=False, wob=0, var=0.0)
            if split_rail:
                a.tile = True
                for x in range(20, SW, 46):
                    a.ink([(x, y - 1), (x + 18, y + 1)], FINE, color=shade(wood, 0.5), alpha=0.8)
                a.tile = False
            a.tile = True
        for x in range(32, SW, 128):
            a.shape(rect(x - 11, h / 2 - 11, x + 11, h / 2 + 11), shade(wood, 0.12), outline=DETAIL * 1.2, corner=3, depth=3, var=0.1)
        cap = Art(h, h, seed + 1)
        cap.shape(rect(9, 9, h - 9, h - 9), shade(wood, 0.12), outline=DETAIL * 1.4, corner=3, depth=3)
        return a.image(), cap.image()

    return make


def picket(seed, color):
    def make():
        h = 40
        a = strip(seed, h)
        a.tile = False
        a.ink([(-10, h / 2), (SW + 10, h / 2)], 10, color=INK, taper=False, wob=0, var=0.0)
        a.ink([(-10, h / 2), (SW + 10, h / 2)], 6, color=shade(color, 0.1), taper=False, wob=0, var=0.0)
        a.tile = True
        for x in range(8, SW, 16):
            a.shape([(x - 5, h / 2 - 7), (x + 5, h / 2 - 7), (x + 5, h / 2 + 7), (x - 5, h / 2 + 7)], color, outline=DETAIL, corner=1, depth=1, mottle=0, var=0.1)
        cap = Art(h, h, seed + 1)
        cap.shape(rect(9, 9, h - 9, h - 9), color, outline=DETAIL * 1.4, corner=3, depth=3)
        return a.image(), cap.image()

    return make


def iron_bars(seed, iron=rgb("#4a4c52"), thick=False, scroll=False, chain=False):
    def make():
        h = 44
        a = strip(seed, h)
        a.tile = False
        a.ink([(-10, h / 2), (SW + 10, h / 2)], DETAIL * 2.4, color=INK, taper=False, wob=0, var=0.0)
        a.ink([(-10, h / 2), (SW + 10, h / 2)], DETAIL * 1.3, color=iron, taper=False, wob=0, var=0.0)
        a.tile = True
        if chain:
            for x in range(0, SW, 14):
                a.ink(ellipse(x + 7, h / 2, 7, 3.5, 16), FINE * 1.6, closed=True, color=iron if (x // 14) % 2 else tint(iron, 0.3))
        else:
            step = 22 if thick else 32
            for x in range(step // 2, SW, step):
                r = 8 if thick else 6
                a.shape(ellipse(x, h / 2, r, r, 16), iron, outline=DETAIL * 0.9, depth=1, light_k=0.5, mottle=0)
        if scroll:
            for x in range(32, SW, 64):
                for s in (-1, 1):
                    pts = [(x + 6 * math.cos(t) * (1 - t / 12), h / 2 + s * (8 + 6 * math.sin(t) * (1 - t / 12))) for t in [k * 0.4 for k in range(16)]]
                    a.ink(pts, FINE * 1.6, color=iron)
        for x in range(0, SW, 128):
            a.shape(rect(x - 11, h / 2 - 11, x + 11, h / 2 + 11), iron, outline=DETAIL * 1.2, corner=3, depth=3, light_k=0.4, mottle=0)
        cap = Art(h, h, seed + 1)
        cap.shape(rect(9, 9, h - 9, h - 9), iron, outline=DETAIL * 1.4, corner=3, depth=3, light_k=0.4, mottle=0)
        return a.image(), cap.image()

    return make


def metal_plates(seed, color, h=52):
    def make():
        a = strip(seed, h)

        def seams(art):
            x = 0.0
            for wd in split(SW, art.rng, 70, 110):
                art.ink([(x, 6), (x, h - 6)], JOINT * 1.4, color=joint_color(color), alpha=JOINT_ALPHA + 0.1, taper=False, wob=0)
                for y in (12, h - 12):
                    for dx in (8, wd - 8):
                        dot(art, x + dx, y, 2.6, tint(color, 0.4))
                        dot(art, x + dx + 0.6, y + 0.6, 1.2, shade(color, 0.5))
                x += wd

        band(a, 5, h - 5, color, detail=seams, light_k=0.5)
        return a.image(), end_block(seed + 1, color, h)

    return make


def bamboo(seed, col):
    def make():
        h = 60
        a = strip(seed, h)
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

    return make


def rocks(seed, color, h=68, jag=0.25, moss=False):
    mk = rock_wall(seed, color, h, jag)
    if moss:
        return mossy(mk, seed + 9, h, n=16)
    return mk


# -- the walls ------------------------------------------------------------------------------------

STONE = {
    "Small Grey Blocks": blocks(2001, rgb("#a39d93"), rows=3, lo=34, hi=56),
    "Large Grey Blocks": blocks(2002, rgb("#9c968c"), rows=1, lo=90, hi=140, h=60),
    "Granite Wall": blocks(2003, rgb("#a8a29a"), rows=2, lo=50, hi=90, cracks=0.1),
    "Pink Granite Wall": blocks(2004, rgb("#c4a39a"), rows=2, lo=50, hi=90, cracks=0.1),
    "Limestone Wall": blocks(2005, rgb("#ddd5c2"), rows=2, lo=60, hi=100),
    "Red Sandstone Wall": blocks(2006, rgb("#b8705a"), rows=2, lo=60, hi=100),
    "Yellow Stone Wall": blocks(2007, rgb("#d9c27a"), rows=2, lo=50, hi=90),
    "White Stone Wall": blocks(2008, rgb("#ece8de"), rows=2, lo=55, hi=95, cracks=0.15),
    "Basalt Wall": blocks(2009, rgb("#55525a"), rows=2, lo=40, hi=70, corner=3, wob=0.5),
    "Slate Wall": blocks(2010, rgb("#6a7480"), rows=3, lo=60, hi=110, h=58, corner=2, wob=0.4),
    "Blue Stone Wall": blocks(2011, rgb("#8c98a8"), rows=2, lo=50, hi=90),
    "Green Stone Wall": blocks(2012, rgb("#8ea08a"), rows=2, lo=50, hi=90),
    "Weathered Stone Wall": blocks(2013, rgb("#b0a99c"), rows=2, lo=45, hi=85, cracks=0.9, wob=1.4),
    "Three-Course Stone Wall": blocks(2014, rgb("#a39d93"), rows=3, lo=50, hi=80, h=72),
    "Dark Ashlar Wall": blocks(2015, rgb("#6f6a64"), rows=2, lo=80, hi=120, h=72, corner=3, wob=0.4, cracks=0.1),
    "Sandstone Ashlar Wall": blocks(2016, rgb("#d2b98a"), rows=2, lo=80, hi=120, h=72, corner=3, wob=0.4, cracks=0.1),
    "White Ashlar Wall": blocks(2017, rgb("#e8e2d6"), rows=2, lo=80, hi=120, h=72, corner=3, wob=0.4, cracks=0.05),
    "Ruined Sandstone Wall": blocks(2018, rgb("#d2b98a"), rows=2, lo=40, hi=80, ruined=True, cracks=0.6),
    "Ruined Dark Wall": blocks(2019, rgb("#6f6a64"), rows=2, lo=40, hi=80, ruined=True, cracks=0.6),
    "Ruined Brick Wall": blocks(2020, rgb("#a8503b"), rows=3, lo=36, hi=46, h=60, mortar=rgb("#d9cbb2"), corner=3, wob=0.5, ruined=True, cracks=0.3),
    "Black Marble Wall": blocks(2021, rgb("#3e3c42"), rows=1, lo=110, hi=160, h=58, corner=3, wob=0.3, cracks=0.0, veins=True),
    "Green Marble Wall": blocks(2022, rgb("#7fa08a"), rows=1, lo=110, hi=160, h=58, corner=3, wob=0.3, cracks=0.0, veins=True),
    "Rose Marble Wall": blocks(2023, rgb("#e4c4c0"), rows=1, lo=110, hi=160, h=58, corner=3, wob=0.3, cracks=0.0, veins=True),
    "Obsidian Wall": obsidian(2024),
    "Mossy Stone Wall": mossy(blocks(2025, rgb("#9c968c")), 2026, 64),
    "Ivy Stone Wall": mossy(blocks(2027, rgb("#a39d93")), 2028, 64, n=6, leaves=True),
    "Mossy Ruins": mossy(blocks(2029, rgb("#9a958c"), rows=2, lo=40, hi=80, ruined=True, cracks=0.6), 2030, 64, n=18),
    "Mossy Basalt Wall": mossy(blocks(2031, rgb("#55525a"), corner=3, wob=0.5), 2032, 64),
    "Grey Battlements": crenellated(2033, rgb("#a39d93")),
    "Sandstone Battlements": crenellated(2034, rgb("#d2b98a")),
    "Dark Battlements": crenellated(2035, rgb("#6f6a64")),
}

BRICK = {
    "Yellow Brick Wall": bricks(2101, rgb("#d6b45a")),
    "Orange Brick Wall": bricks(2102, rgb("#c9763f")),
    "Dark Red Brick Wall": bricks(2103, rgb("#7e3a2e")),
    "Grey Brick Wall": bricks(2104, rgb("#8f8c88"), mortar=rgb("#cfcac2")),
    "Black Brick Wall": bricks(2105, rgb("#45424a"), mortar=rgb("#a39d93")),
    "Pale Brick Wall": bricks(2106, rgb("#e0c4a4")),
    "Burnt Brick Wall": bricks(2107, rgb("#6a3a2a"), mortar=rgb("#8a7a6a")),
    "Red Brick, Dark Mortar": bricks(2108, rgb("#a8503b"), mortar=rgb("#4a423c")),
    "Long Roman Brick": bricks(2109, rgb("#b8704a"), rows=4, lo=70, hi=90, h=60),
    "Large Brick Wall": bricks(2110, rgb("#a05a44"), rows=2, lo=56, hi=70, h=58),
    "Stack Bond Brick": stack_bricks(2111, rgb("#a8503b")),
    "Stack Bond Pale Brick": stack_bricks(2112, rgb("#e0c4a4")),
    "Ivy Brick Wall": mossy(bricks(2113, rgb("#a8503b")), 2114, 60, n=5, leaves=True),
}

TIMBER = {
    "Dark Log Wall": log_wall(2201, rgb("#5a4030"), rgb("#a07a50")),
    "Pale Log Wall": log_wall(2202, rgb("#b08a5e"), rgb("#d8b88a")),
    "Birch Log Wall": log_wall(2203, rgb("#e6e0d0"), rgb("#d8c8a0"), birch=True),
    "Mossy Log Wall": log_wall(2204, rgb("#7a5a3e"), rgb("#c39463"), mossy_=True),
    "Three-Log Wall": log_wall(2205, rgb("#7a5a3e"), rgb("#c39463"), rows=3),
    "Light Plank Wall": planks(2206, rgb("#c39463")),
    "Dark Plank Wall": planks(2207, rgb("#6e4a2f")),
    "Weathered Plank Wall": planks(2208, rgb("#9a9488")),
    "Red Painted Planks": planks(2209, rgb("#a8483a")),
    "Board and Batten": planks(2210, rgb("#b08a5e"), battens=True),
    "Dark Palisade": palisade(2211, rgb("#6a4a30")),
    "Pale Palisade": palisade(2212, rgb("#c0a07a")),
    "Thin Palisade": palisade(2213, rgb("#9a7048"), r=18),
    "Wattle Fence": wattle(2214),
    "Wattle and Daub": wattle(2215, daub=rgb("#b89a72")),
    "Half-Timber, Ochre": plaster(2216, rgb("#d9b46a"), braces=True),
    "Half-Timber, Rose": plaster(2217, rgb("#d8a8a0"), braces=True),
    "Half-Timber, Sky": plaster(2218, rgb("#a8c0d0"), braces=True),
    "Half-Timber, Sage": plaster(2219, rgb("#b0c0a0"), braces=True),
    "Half-Timber, Dark Posts": plaster(2220, rgb("#ece4d0"), post=rgb("#3e2c20"), every=128),
    "Thatch-Topped Wall": thatch_topped(2221),
}

PLASTER = {
    "White Plaster Wall": plaster(2301, rgb("#ece6da"), post=None),
    "Ochre Plaster Wall": plaster(2302, rgb("#d9b46a"), post=None),
    "Rose Plaster Wall": plaster(2303, rgb("#d8a8a0"), post=None),
    "Sky Plaster Wall": plaster(2304, rgb("#a8c0d0"), post=None),
    "Sage Plaster Wall": plaster(2305, rgb("#b0c0a0"), post=None),
    "Mud Wall": plaster(2306, rgb("#8a6a4a"), post=None, straw=True),
    "Red Adobe Wall": plaster(2307, rgb("#b8704a"), post=None, straw=True),
}

ROCK = {
    "Fieldstone Wall": rocks(2401, rgb("#a39d93")),
    "Sandstone Rubble": rocks(2402, rgb("#d2b98a")),
    "Dark Rubble Wall": rocks(2403, rgb("#6f6a64")),
    "Mossy Fieldstone": rocks(2404, rgb("#9c968c"), moss=True),
    "Slate Rubble": rocks(2405, rgb("#6a7480"), jag=0.35),
    "River Rock Wall": rocks(2406, rgb("#a8a49a"), jag=0.08),
    "Red Rock Wall": rocks(2407, rgb("#a8604a")),
    "Basalt Rocks": rocks(2408, rgb("#4a474e"), jag=0.3),
    "Limestone Cave Wall": rocks(2409, rgb("#d8d0bc"), h=74, jag=0.3),
    "Volcanic Cave Wall": rocks(2410, rgb("#3e3434"), h=74, jag=0.35),
    "Mossy Cave Wall": rocks(2411, rgb("#7f7a72"), h=74, jag=0.3, moss=True),
    "Icy Cave Wall": rocks(2412, rgb("#b8d0da"), h=74, jag=0.3),
    "Sandy Cave Wall": rocks(2413, rgb("#c8b088"), h=74, jag=0.28),
}

FANTASY = {
    "Blue Crystal Wall": crystal(2501, rgb("#7aa6d8")),
    "Green Crystal Wall": crystal(2502, rgb("#6fc08a")),
    "Red Crystal Wall": crystal(2503, rgb("#d06a6a")),
    "Amber Crystal Wall": crystal(2504, rgb("#e0a84a")),
    "Blue Ice Wall": ice(2505, rgb("#9ec6e0")),
    "Glacier Wall": ice(2506, rgb("#e2f0f4"), lo=90, hi=150),
    "Pink Coral Wall": coral(2507, [rgb("#e88a8a"), rgb("#f0b0a0"), rgb("#d86a7a")]),
    "Blue Coral Wall": coral(2508, [rgb("#7aa6d8"), rgb("#9ac0e0"), rgb("#6a8ac8")]),
    "Blue Runic Wall": runic(2509, rgb("#7f7a72"), rgb("#6fc8e0")),
    "Green Runic Wall": runic(2510, rgb("#6f6a64"), rgb("#7fe08a")),
    "Purple Runic Wall": runic(2511, rgb("#5a5660"), rgb("#b88ae0")),
    "Living Roots": roots(2512),
    "Thorn Wall": thorns(2513),
}

GREEN = {
    "Green Bamboo Wall": bamboo(2601, rgb("#8aa65a")),
    "Dark Bamboo Wall": bamboo(2602, rgb("#8a7a4a")),
    "Dark Hedge": hedge(2603, rgb("#3f6a2a")),
    "Flowering Hedge": hedge(2604, rgb("#5f8f3c"), flowers=rgb("#e88aa8")),
    "Autumn Hedge": hedge(2605, rgb("#b8783a")),
    "White Rose Hedge": hedge(2606, rgb("#4f7c34"), flowers=rgb("#f3eee2")),
}

FENCES = {
    "Wood Rail Fence": rail_fence(2701, rgb("#9a7048")),
    "Three-Rail Fence": rail_fence(2702, rgb("#b08a5e"), rails=3),
    "Split-Rail Fence": rail_fence(2703, rgb("#8a6a4a"), split_rail=True),
    "White Picket Fence": picket(2704, rgb("#ece4d3")),
    "Wood Picket Fence": picket(2705, rgb("#b08a5e")),
    "Wrought Iron Fence": iron_bars(2706, scroll=True),
    "Heavy Iron Bars": iron_bars(2707, thick=True),
    "Chain Fence": iron_bars(2708, chain=True),
    "Bronze Fence": iron_bars(2709, iron=rgb("#a87a4a")),
}

METAL = {
    "Iron Plate Wall": metal_plates(2801, rgb("#6a6c72")),
    "Bronze Plate Wall": metal_plates(2802, rgb("#a87a4a")),
    "Steel Plate Wall": metal_plates(2803, rgb("#9aa0aa")),
    "Tan Sandbags": sandbags(2804, rgb("#c9ad7c")),
    "Green Sandbags": sandbags(2805, rgb("#8a9a6a")),
}

WALLS2 = {**STONE, **BRICK, **TIMBER, **PLASTER, **ROCK, **FANTASY, **GREEN, **FENCES, **METAL}
