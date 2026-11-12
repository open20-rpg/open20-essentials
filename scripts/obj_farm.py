"""Farm, animals, harbor and water (batch 13). Strict top-down, same pen
style. Animals face up (toward the top of the image); the editor rotates
them. Red (g == b) parts are recolorable."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, dot, fruit, pile, scallop, soft_shadow
from obj_craft import handle
from obj_nature import GREEN, GREEN_D, GREEN_L, blades, leaf
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

O = DETAIL * 2.0
V = 0.08
STRAW = rgb("#d9bf72")
ROPE = rgb("#c9b088")
WATER = rgb("#6aa0b6")
FOAM = rgb("#e4f2f6")
SOIL = rgb("#6a4e36")
NET = rgb("#b8a882")


def mirror_x(pts, cx):
    return [(2 * cx - x, y) for x, y in reversed(pts)]


# -- animals ---------------------------------------------------------------------------------------


def quadruped(a, cx, cy, L, W, color, head=0.32, muzzle=None, ears="up", ear_color=None, tail="thin",
              tail_color=None, legs=True, leg_color=None, spots=None, horns=None, mane=None, wool=False, belly=None):
    """A four-legged animal seen from above, head toward the top. L/W are
    the body's length/width (px). Legs peek out at the sides, the tail
    behind, the head (with muzzle and ears) in front."""
    leg_color = leg_color or shade(color, 0.25)
    tail_color = tail_color or shade(color, 0.2)
    top, bot = cy - L / 2, cy + L / 2
    hl = L * head  # head length
    hw = W * 0.42 if head < 0.4 else W * 0.5
    hcy = top - hl * 0.25
    # Legs (peeking out under the body), tail.
    if legs:
        for fy, fx in ((top + L * 0.18, 0.5), (bot - L * 0.16, 0.48)):
            for side in (-1, 1):
                x = cx + side * W * fx
                a.shape(ellipse(x, fy, W * 0.1, L * 0.06, 20), leg_color, outline=DETAIL * 1.3, depth=2, shade_k=0.3, light_k=0, ao=0, mottle=0)
    if tail == "thin":
        pts = chaikin([(cx, bot - 4), (cx + W * 0.08, bot + L * 0.12), (cx - W * 0.04, bot + L * 0.22)], False, 2)
        a.ink(pts, 9, color=INK, taper=True)
        a.ink(pts, 5, color=tail_color, taper=True)
        a.shape(scallop(pts[-1][0], pts[-1][1], W * 0.06, a.rng, 6, 0.3), shade(tail_color, 0.15), outline=FINE * 1.4, depth=1, mottle=0)
    elif tail == "bushy":
        a.shape(chaikin([(cx - W * 0.12, bot - 6), (cx + W * 0.12, bot - 6), (cx + W * 0.1, bot + L * 0.28), (cx, bot + L * 0.36), (cx - W * 0.1, bot + L * 0.28)], True, 2), tail_color, outline=DETAIL * 1.3, depth=3, light_k=0.3)
    elif tail == "curly":
        sp = [(cx + (2 + 1.4 * t) * math.cos(t * 1.6), bot + 6 + (2 + 1.4 * t) * math.sin(t * 1.6)) for t in [k * 0.25 for k in range(30)]]
        a.ink(sp, 8, color=INK, taper=True)
        a.ink(sp, 4.5, color=tail_color, taper=True)
    elif tail == "stub":
        a.shape(ellipse(cx, bot + 4, W * 0.1, W * 0.12, 16), tail_color, outline=DETAIL, depth=1, mottle=0)
    # Body.
    body = [(cx + W / 2 * math.cos(t) * (1 - 0.1 * math.sin(t)), cy + L / 2 * math.sin(t)) for t in [2 * math.pi * k / 64 for k in range(64)]]
    if wool:
        body = scallop(cx, cy, W / 2, a.rng, 16, 0.08, ry=L / 2)

    def detail(art, p):
        if spots:
            for _ in range(spots[1]):
                art.shape(blob(art.rng.uniform(cx - W * 0.4, cx + W * 0.4), art.rng.uniform(top + L * 0.1, bot - L * 0.1), art.rng.uniform(W * 0.1, W * 0.22), art.rng, 9, 0.3), spots[0], outline=0, smooth=True, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        if wool:
            for _ in range(int(L * W / 500)):
                x, y = art.rng.uniform(cx - W / 2, cx + W / 2), art.rng.uniform(top, bot)
                art.ink([(x + 4 * math.cos(t), y + 4 * math.sin(t)) for t in [k * 0.6 for k in range(9)]], FINE, color=shade(color, 0.3), alpha=0.6)
        else:
            art.ink([(cx, top + L * 0.12), (cx, bot - L * 0.12)], FINE * 1.2, color=shade(color, 0.4), alpha=0.5)
        if belly:
            pass

    a.shape(body, color, outline=OUTLINE * 0.8, corner=0, depth=L * 0.04, light_k=0.4, detail=detail)
    if mane:
        a.shape(rect(cx - W * 0.09, top - hl * 0.1, cx + W * 0.09, top + L * 0.38), mane, outline=DETAIL * 1.2, corner=W * 0.08, depth=2, mottle=0)
    # Head.
    if horns:
        for side in (-1, 1):
            pts = chaikin([(cx + side * hw * 0.3, hcy), (cx + side * hw * 1.1, hcy - hl * 0.05), (cx + side * hw * 1.3, hcy - hl * 0.35)], False, 2)
            a.ink(pts, 13, color=INK, taper=True)
            a.ink(pts, 8, color=horns, taper=True)
    if ears:
        ec = ear_color or shade(color, 0.1)
        for side in (-1, 1):
            if ears == "up":
                e = ellipse(cx + side * hw * 0.62, hcy + hl * 0.12, hw * 0.28, hl * 0.2, 16, rot=side * 0.6)
            elif ears == "side":
                e = ellipse(cx + side * hw * 0.95, hcy + hl * 0.1, hw * 0.42, hl * 0.13, 16, rot=side * 0.25)
            else:  # floppy
                e = ellipse(cx + side * hw * 0.8, hcy + hl * 0.2, hw * 0.3, hl * 0.28, 16, rot=side * 0.3)
            a.shape(e, ec, outline=DETAIL * 1.2, depth=2, mottle=0)
    a.shape(ellipse(cx, hcy, hw / 2 * 0.85, hl / 2, 40), tint(color, 0.06), outline=DETAIL * 1.6, depth=3, light_k=0.45)
    if muzzle:
        mc, ml = muzzle
        my = hcy - hl * 0.42
        a.shape(ellipse(cx, my, hw * 0.33, hl * ml, 28), mc, outline=DETAIL * 1.4, depth=2, light_k=0.3, mottle=0)
        for side in (-1, 1):
            dot(a, cx + side * hw * 0.12, my - hl * ml * 0.4, max(1.8, hw * 0.04), shade(mc, 0.6))
    if mane:
        a.ink([(cx, hcy - hl * 0.1), (cx, hcy + hl * 0.45)], 7, color=mane, taper=False)


def animal(w, h, **kw):
    def make(seed=1300):
        L, hd = kw["L"], kw.get("head", 0.32)
        tail_room = {"bushy": 0.4, "thin": 0.3, "curly": 0.1, "stub": 0.08}.get(kw.get("tail", "thin"), 0.1)
        hh = int(L * (1 + hd * 0.8 + tail_room) + 50)
        a = Art(w, hh, seed)
        cy = 25 + L * hd * 0.8 + L / 2
        soft_shadow(a, ellipse(w / 2, cy, kw["W"] / 2, kw["L"] / 2, 48), dx=5, dy=7, alpha=0.3, blur=6)
        quadruped(a, w / 2, cy, **kw)
        return a.image()

    return make


def bird(a, cx, cy, size, body, wing, head_c=None, beak=rgb("#e0a640"), tail=None, comb=None, long_neck=False):
    """A bird from above, head toward the top: tail feathers, body, folded
    wings over the back, head with beak (a comb for roosters/hens)."""
    head_c = head_c or body
    L, W = size, size * 0.62
    top = cy - L / 2
    tc = tail or shade(wing, 0.1)
    a.shape([(cx - W * 0.22, cy + L * 0.25), (cx + W * 0.22, cy + L * 0.25), (cx + W * 0.3, cy + L * 0.62), (cx, cy + L * 0.68), (cx - W * 0.3, cy + L * 0.62)], tc, outline=DETAIL * 1.3, corner=4, depth=2, mottle=0)
    a.shape(ellipse(cx, cy + L * 0.08, W / 2, L * 0.4, 40), body, outline=OUTLINE * 0.7, depth=4, light_k=0.4)
    for side in (-1, 1):
        wpts = chaikin([(cx + side * W * 0.05, cy - L * 0.18), (cx + side * W * 0.5, cy - L * 0.02), (cx + side * W * 0.42, cy + L * 0.34), (cx + side * W * 0.12, cy + L * 0.42)], True, 2)
        a.shape(wpts, wing, outline=DETAIL * 1.3, corner=0, depth=2, light_k=0.3, mottle=0, detail=lambda art, p, side=side: [art.ink([(cx + side * W * (0.18 + 0.1 * k), cy + L * 0.05 + k * 6), (cx + side * W * (0.22 + 0.1 * k), cy + L * 0.32)], FINE, color=shade(wing, 0.4), alpha=0.7) for k in range(3)])
    hy = top + L * (0.0 if long_neck else 0.1)
    if long_neck:
        a.ink([(cx, cy - L * 0.18), (cx, hy + L * 0.05)], W * 0.26 + 6, color=INK, taper=False)
        a.ink([(cx, cy - L * 0.18), (cx, hy + L * 0.05)], W * 0.26, color=head_c, taper=False)
    a.shape(ellipse(cx, hy, W * 0.22, W * 0.24, 28), head_c, outline=DETAIL * 1.4, depth=2, light_k=0.4, mottle=0)
    if comb:
        a.shape(scallop(cx, hy + W * 0.02, W * 0.1, a.rng, 4, 0.3, ry=W * 0.16), comb, outline=FINE * 1.3, depth=1, mottle=0)
    a.shape([(cx - W * 0.08, hy - W * 0.18), (cx + W * 0.08, hy - W * 0.18), (cx, hy - W * 0.38)], beak, outline=FINE * 1.4, corner=1, depth=1, mottle=0)


def bird_obj(size, **kw):
    def make(seed=1350):
        s = int(size * 1.6)
        a = Art(s, s, seed)
        soft_shadow(a, (s / 2, s / 2 + size * 0.1), size * 0.32, 3, 4, 0.3, 3)
        bird(a, s / 2, s / 2 - size * 0.05, size, **kw)
        return a.image()

    return make


def chicks(seed=1360):
    s = 200
    a = Art(s, s, seed)
    for x, y in ((70, 70), (130, 80), (90, 130), (140, 140)):
        soft_shadow(a, (x, y), 14, 2, 3, 0.3, 2)
        bird(a, x, y, 40, rgb("#f2d25a"), rgb("#e6c24a"), beak=rgb("#e0883a"))
    return a.image()


def cat(seed=1361, color=rgb("#8a7a6a")):
    w, h = 160, 260
    a = Art(w, h, seed)
    soft_shadow(a, ellipse(w / 2, h / 2, 40, 70, 40), dx=4, dy=6)
    # Curled tail around the side.
    pts = chaikin([(w / 2, h / 2 + 60), (w / 2 + 40, h / 2 + 70), (w / 2 + 52, h / 2 + 20)], False, 2)
    a.ink(pts, 16, color=INK, taper=True)
    a.ink(pts, 10, color=color, taper=True)
    quadruped(a, w / 2, h / 2 + 10, 120, 70, color, head=0.4, ears="up", tail=None, spots=(shade(color, 0.3), 4))
    return a.image()


def frog(seed=1362):
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    c = rgb("#6f9a45")
    for side in (-1, 1):
        a.shape(ellipse(m + side * 30, m + 26, 18, 10, 20, rot=side * 0.6), shade(c, 0.1), outline=DETAIL * 1.2, depth=2, mottle=0)
        a.shape(ellipse(m + side * 24, m - 14, 8, 6, 16), shade(c, 0.1), outline=DETAIL, depth=1, mottle=0)
    a.shape(ellipse(m, m + 6, 28, 30, 36), c, outline=DETAIL * 1.6, depth=3, light_k=0.4, detail=lambda art, p: [dot(art, m + art.rng.uniform(-16, 16), m + art.rng.uniform(-6, 26), 3, shade(c, 0.35)) for _ in range(6)])
    for side in (-1, 1):
        a.shape(ellipse(m + side * 12, m - 18, 8, 8, 16), tint(c, 0.15), outline=DETAIL * 1.1, depth=2, mottle=0)
        dot(a, m + side * 12, m - 19, 3.4)
    return a.image()


def snake(seed=1363):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    c = rgb("#7a8a3e")
    sp = [(m + (14 + 6.5 * t) * math.cos(t * 1.15), m + (14 + 6.5 * t) * math.sin(t * 1.15)) for t in [k * 0.12 for k in range(100)]]
    sp = sp[::-1]
    a.ink([(x + 3, y + 4) for x, y in sp], 22, color=INK, alpha=0.25, taper=True)
    a.ink(sp, 24, color=INK, taper=True)
    a.ink(sp, 17, color=c, taper=True)
    for i in range(4, len(sp) - 4, 5):
        dot(a, sp[i][0], sp[i][1], 3.4, shade(c, 0.4))
    hx, hy = sp[0]
    a.shape(ellipse(hx, hy, 15, 11, 24, rot=1.15 * 11.9 + math.pi / 2), c, outline=DETAIL * 1.4, depth=2, light_k=0.4, mottle=0)
    return a.image()


def rat(seed=1364):
    w, h = 90, 190
    a = Art(w, h, seed)
    soft_shadow(a, ellipse(w / 2, 80, 20, 34, 28), dx=3, dy=4)
    quadruped(a, w / 2, 86, 66, 40, rgb("#7a726a"), head=0.42, ears="side", ear_color=rgb("#c99a8a"), tail=None, legs=True)
    pts = chaikin([(w / 2, 118), (w / 2 + 20, 150), (w / 2 - 6, 180)], False, 2)
    a.ink(pts, 7, color=INK, taper=True)
    a.ink(pts, 3.5, color=rgb("#c99a8a"), taper=True)
    return a.image()


def owl(seed=1365):
    s = 150
    a = Art(s, s, seed)
    m = s / 2
    c = rgb("#8a6a4e")
    soft_shadow(a, (m, m), 44, 4, 5)
    a.shape(ellipse(m, m + 6, 42, 48, 40), c, outline=OUTLINE * 0.7, depth=4, light_k=0.4, detail=lambda art, p: [art.ink([(m + x, m + y), (m + x + 4, m + y + 6)], FINE * 1.2, color=shade(c, 0.45), alpha=0.8) for x, y in ((-20, 0), (0, 10), (16, -4), (-8, 24), (14, 26))])
    a.shape(ellipse(m, m - 18, 32, 28, 36), tint(c, 0.12), outline=DETAIL * 1.5, depth=3, light_k=0.4)
    for side in (-1, 1):
        a.shape([(m + side * 18, m - 36), (m + side * 30, m - 50), (m + side * 30, m - 30)], c, outline=DETAIL, corner=1, depth=1, mottle=0)
    return a.image()


# -- beehives, crops & farm gear ------------------------------------------------------------------------


def skep(seed=1401):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 64, 5, 6)
    a.shape(ellipse(m, m, 64, 64, 64), STRAW, depth=10, light_k=0.45, detail=lambda art, p: [art.ink(ellipse(m, m, r, r, 48), DETAIL * 0.9, closed=True, color=shade(STRAW, 0.45), alpha=0.85) for r in (14, 28, 42, 56)])
    for _ in range(5):
        x, y = m + a.rng.uniform(-70, 70), m + a.rng.uniform(-70, 70)
        if abs(x - m) + abs(y - m) > 70:
            dot(a, x, y, 3, rgb("#e6b84a"))
            dot(a, x, y, 1.4, INK)
    return a.image()


def box_hive(seed=1402):
    w, h = 180, 220
    a = Art(w, h, seed)
    a.shape(rect(14, 14, w - 14, h - 14), rgb("#e6dcc4"), corner=6, depth=10, light_k=0.3, detail=lambda art, p: boards(art, 14, 14, w - 14, h - 14, rgb("#e6dcc4"), 3, grain=False))
    a.shape(rect(26, 26, w - 26, h - 26), rgb("#d8c9a8"), outline=DETAIL * 1.2, corner=4, depth=4, light_k=0.3)
    # The roof's ridge and a weight stone on top.
    a.ink([(w / 2, 26), (w / 2, h - 26)], DETAIL * 1.4, color=shade(rgb("#d8c9a8"), 0.45))
    a.shape(blob(w / 2 + 20, h / 2, 18, a.rng, 8, 0.2), STONE, outline=DETAIL * 1.2, smooth=True, depth=3, light_k=0.4, mottle=0)
    for _ in range(4):
        dot(a, a.rng.uniform(30, w - 30), h - 8, 3, rgb("#e6b84a"))
    return a.image()


def crop_rows(plant, rows=4, w=512, h=512, seed=1410, soil=SOIL):
    def make(seed=seed):
        a = Art(w, h, seed)
        pitch = (h - 40) / rows
        for r in range(rows):
            y = 20 + pitch * (r + 0.5)
            a.shape(rect(14, y - pitch * 0.32, w - 14, y + pitch * 0.32), vary(a.rng, soil, 0.05), outline=DETAIL * 1.2, corner=pitch * 0.25, depth=4, light_k=0.25, mottle=0.1)
            x = 40
            while x < w - 40:
                plant(a, x + a.rng.uniform(-4, 4), y + a.rng.uniform(-3, 3))
                x += a.rng.uniform(46, 58)
        return a.image()

    return make


def p_wheat(a, x, y):
    blades(a, x, y, 7, 30, [rgb("#d9bf72"), rgb("#c9a85a"), rgb("#e6d08a")], width=6)
    for k in range(3):
        t = a.rng.uniform(0, 6.28)
        a.shape(ellipse(x + 18 * math.cos(t), y + 18 * math.sin(t), 7, 4, 12, rot=t), rgb("#e6c86a"), outline=FINE * 1.2, depth=1, mottle=0)


def p_corn(a, x, y):
    for k in range(6):
        t = 2 * math.pi * k / 6 + a.rng.uniform(-0.2, 0.2)
        leaf(a, x + 16 * math.cos(t), y + 16 * math.sin(t), 36, vary(a.rng, GREEN, 0.06), ang=t, vein=True, outline=FINE * 1.2)
    a.shape(ellipse(x, y, 6, 6, 12), rgb("#e6c86a"), outline=FINE * 1.2, depth=1, mottle=0)


def p_cabbage(a, x, y):
    c = rgb("#8fb85a")
    a.shape(scallop(x, y, 20, a.rng, 7, 0.18), shade(c, 0.1), outline=DETAIL * 1.2, depth=3, light_k=0.4)
    a.shape(ellipse(x - 2, y - 2, 11, 11, 20), tint(c, 0.2), outline=DETAIL, depth=2, light_k=0.4, mottle=0)


def p_carrot(a, x, y):
    blades(a, x, y, 6, 22, [GREEN, GREEN_L], width=5)
    dot(a, x, y, 5, rgb("#e08a3a"))


def p_pumpkin(a, x, y):
    blades(a, x - 14, y, 4, 22, [GREEN, GREEN_D], width=7)
    pumpkin_at(a, x + 6, y, 18)


def pumpkin_at(a, x, y, r):
    c = rgb("#e08a3a")
    soft_shadow(a, (x, y), r, 3, 4, 0.3, 3)
    a.shape(ellipse(x, y, r, r * 0.92, 32), c, outline=DETAIL * 1.4, depth=3, light_k=0.45, mottle=0, detail=lambda art, p: [art.ink([(x + r * 0.9 * math.cos(t), y + r * 0.9 * math.sin(t)), (x + r * 0.2 * math.cos(t), y + r * 0.2 * math.sin(t))], FINE * 1.1, color=shade(c, 0.4), alpha=0.8) for t in [2 * math.pi * k / 8 for k in range(8)]])
    a.shape(ellipse(x, y, r * 0.2, r * 0.2, 12), rgb("#6a5a2e"), outline=FINE * 1.2, depth=1, mottle=0)


def pumpkin(seed=1420, r=46):
    def make(seed=seed):
        s = int(r * 2 + 40)
        a = Art(s, s, seed)
        leaf(a, s / 2 + r * 0.6, s / 2 - r * 0.7, r * 0.7, GREEN, ang=-0.8)
        pumpkin_at(a, s / 2, s / 2, r)
        return a.image()

    return make


def scarecrow(seed=1421):
    w, h = 280, 200
    a = Art(w, h, seed)
    m = w / 2
    # From above: the crossbar with the shirt's sleeves, the straw hat brim.
    a.shape(rect(20, h / 2 - 12, w - 20, h / 2 + 12), WOOD, outline=O * 0.8, corner=6, depth=3, var=V)
    shirt = rgb("#7a8ab0")
    a.shape(chaikin([(40, h / 2 - 26), (w - 40, h / 2 - 26), (w - 40, h / 2 + 26), (m + 40, h / 2 + 50), (m - 40, h / 2 + 50), (40, h / 2 + 26)], True, 2), shirt, depth=6, light_k=0.3, detail=lambda art, p: [art.ink([(x, h / 2 - 20), (x + 6, h / 2 + 20)], FINE, color=shade(shirt, 0.4)) for x in (70, 110, 170, 210)])
    for x in (30, w - 30):
        for _ in range(5):
            t = a.rng.uniform(-1, 1) + (math.pi if x < m else 0)
            a.ink([(x, h / 2), (x + 16 * math.cos(t), h / 2 + 16 * math.sin(t))], FINE * 1.3, color=STRAW)
    a.shape(ellipse(m, h / 2 - 8, 50, 46, 48), STRAW, outline=DETAIL * 1.6, depth=5, light_k=0.4, detail=lambda art, p: art.ink(ellipse(m, h / 2 - 8, 26, 24, 32), FINE * 1.3, closed=True, color=shade(STRAW, 0.45)))
    a.shape(ellipse(m, h / 2 - 8, 24, 22, 32), tint(STRAW, 0.08), outline=DETAIL, depth=3, light_k=0.4)
    return a.image()


def feed_trough(seed=1422):
    w, h = 400, 130
    a = Art(w, h, seed)
    a.shape(rect(10, 12, w - 10, h - 12), WOOD_DARK, corner=10, depth=8)
    a.shape(rect(26, 28, w - 26, h - 28), shade(WOOD_DARK, 0.4), outline=DETAIL, corner=6, depth=8, shade_k=0, light_k=0, ao=0.5)
    for _ in range(140):
        dot(a, a.rng.uniform(32, w - 32), a.rng.uniform(34, h - 34), a.rng.uniform(1.4, 2.6), rgb("#d8c07a"), 0.9)
    return a.image()


def milk_churn(seed=1423):
    s = 130
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 44, 4, 5)
    a.shape(ellipse(m, m, 44, 44, 48), rgb("#b9bec6"), depth=6, light_k=0.55)
    a.shape(ellipse(m, m, 24, 24, 32), rgb("#9aa0aa"), outline=DETAIL * 1.3, depth=3, light_k=0.5)
    for side in (-1, 1):
        a.ink([(m + side * 30, m - 18), (m + side * 46, m), (m + side * 30, m + 18)], DETAIL * 2.4, color=INK)
        a.ink([(m + side * 30, m - 18), (m + side * 46, m), (m + side * 30, m + 18)], DETAIL * 1.3, color=rgb("#9aa0aa"))
    return a.image()


def butter_churn(seed=1424):
    s = 140
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 50, 4, 5)
    a.shape(ellipse(m, m, 50, 50, 48), WOOD, depth=6, light_k=0.4, detail=lambda art, p: [art.ink([(m + 36 * math.cos(t), m + 36 * math.sin(t)), (m + 50 * math.cos(t), m + 50 * math.sin(t))], DETAIL * 0.7, color=shade(WOOD, 0.5), taper=False) for t in [2 * math.pi * k / 12 for k in range(12)]])
    a.shape(ellipse(m, m, 34, 34, 40), WOOD_LIGHT, outline=DETAIL * 1.3, depth=3, light_k=0.4)
    a.shape(ellipse(m, m, 9, 9, 16), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def egg_basket(seed=1425):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    wick = rgb("#b99258")
    a.shape(ellipse(m, m, 70, 70, 64), wick, depth=8, light_k=0.3, detail=lambda art, p: [art.ink([(m + 56 * math.cos(t), m + 56 * math.sin(t)), (m + 70 * math.cos(t + 0.05), m + 70 * math.sin(t + 0.05))], FINE * 1.2, color=shade(wick, 0.5), alpha=0.8) for t in [2 * math.pi * k / 30 for k in range(30)]])

    def eggs(art, p):
        art.shape(ellipse(m, m, 54, 54, 56), STRAW, outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.1)
        for _ in range(9):
            x, y = m + art.rng.uniform(-34, 34), m + art.rng.uniform(-34, 34)
            soft_shadow(art, (x, y), 12, 2, 3, 0.3, 2)
            art.shape(ellipse(x, y, 13, 10, 24, rot=art.rng.uniform(0, 3)), vary(art.rng, rgb("#f2e6cf"), 0.04), outline=FINE * 1.3, depth=1, light_k=0.5, mottle=0)

    a.shape(ellipse(m, m, 56, 56, 56), shade(wick, 0.3), outline=DETAIL, depth=6, shade_k=0, light_k=0, ao=0.5, detail=eggs)
    return a.image()


def hay_fork(seed=1426):
    w, h = 360, 120
    a = Art(w, h, seed)
    handle(a, 14, h / 2 + 10, 250, h / 2, 11)
    a.ink([(250, h / 2 - 24), (250, h / 2 + 24)], 13, color=INK, taper=False)
    a.ink([(250, h / 2 - 24), (250, h / 2 + 24)], 7, color=rgb("#9aa0aa"), taper=False)
    for dy in (-20, 0, 20):
        a.ink([(250, h / 2 + dy), (320, h / 2 + dy * 1.2)], 11, color=INK, taper=True)
        a.ink([(250, h / 2 + dy), (320, h / 2 + dy * 1.2)], 6, color=rgb("#9aa0aa"), taper=True)
    return a.image()


def plough(seed=1427):
    w, h = 420, 200
    a = Art(w, h, seed)
    for y in (h / 2 - 50, h / 2 + 50):
        handle(a, 14, y, 200, h / 2 + (y - h / 2) * 0.3, 12, WOOD)
    a.shape(rect(180, h / 2 - 18, w - 70, h / 2 + 18), WOOD_DARK, outline=O * 0.8, corner=6, depth=5, var=V)
    blade = [(w - 90, h / 2 - 30), (w - 20, h / 2 - 10), (w - 10, h / 2 + 4), (w - 90, h / 2 + 30)]
    a.shape(blade, rgb("#7a8088"), outline=O * 0.8, corner=4, depth=4, light_k=0.5, var=V)
    return a.image()


def water_pump(seed=1428):
    w, h = 200, 220
    a = Art(w, h, seed)
    a.shape(rect(30, 100, w - 30, h - 20), STONE, corner=10, depth=6)
    a.shape(rect(46, 116, w - 46, h - 36), rgb("#6aa0b6"), outline=DETAIL * 1.2, corner=6, depth=6, shade_k=0, light_k=0, ao=0.5)
    a.shape(ellipse(w / 2, 70, 30, 30, 32), rgb("#4a6a5a"), outline=O * 0.8, depth=5, light_k=0.5, var=V)
    a.shape(rect(w / 2 - 9, 70, w / 2 + 9, 120), rgb("#4a6a5a"), outline=O * 0.8, corner=4, depth=3, var=V)  # spout
    handle(a, w / 2 + 10, 60, w - 20, 16, 10, rgb("#4a6a5a"))
    return a.image()


def trellis(seed=1429):
    w, h = 420, 160
    a = Art(w, h, seed)
    for x in range(20, w, 60):
        handle(a, x, 20, x, h - 20, 9, WOOD)
    for y in (40, h / 2, h - 40):
        handle(a, 14, y, w - 14, y, 8, WOOD_LIGHT)
    for _ in range(46):
        x, y = a.rng.uniform(20, w - 20), a.rng.uniform(26, h - 26)
        leaf(a, x, y, a.rng.uniform(22, 30), vary(a.rng, GREEN, 0.06), vein=False, outline=FINE)
    for _ in range(8):
        x, y = a.rng.uniform(40, w - 40), a.rng.uniform(40, h - 40)
        for k in range(5):
            dot(a, x + a.rng.uniform(-8, 8), y + a.rng.uniform(-8, 8), 5, rgb("#6a3a6a"))
            dot(a, x + a.rng.uniform(-8, 8), y + a.rng.uniform(-8, 8), 1.6, rgb("#c8a0d0"))
    return a.image()


def compost(seed=1430):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    a.shape(rect(14, 14, s - 14, s - 14), WOOD_DARK, corner=6, depth=6, detail=lambda art, p: boards(art, 14, 14, s - 14, s - 14, WOOD_DARK, 4))
    a.shape(rect(30, 30, s - 30, s - 30), SOIL, outline=DETAIL * 1.2, corner=4, depth=8, shade_k=0, light_k=0.2, ao=0.5)
    for _ in range(20):
        leaf(a, a.rng.uniform(46, s - 46), a.rng.uniform(46, s - 46), a.rng.uniform(18, 26), vary(a.rng, rgb("#8a7a3e"), 0.1), vein=False, outline=FINE)
    for _ in range(5):
        x, y = a.rng.uniform(60, s - 60), a.rng.uniform(60, s - 60)
        a.shape(ellipse(x, y, 10, 6, 16, rot=a.rng.uniform(0, 3)), rgb("#e08a3a"), outline=FINE * 1.2, depth=1, mottle=0)
    return a.image()


def wheat_sheaf(seed=1431):
    s = 180
    a = Art(s, s, seed)
    m = s / 2
    for k in range(26):
        t = 2 * math.pi * k / 26 + a.rng.uniform(-0.1, 0.1)
        x1, y1 = m + 74 * math.cos(t), m + 74 * math.sin(t)
        a.ink([(m, m), (x1, y1)], 5, color=INK, taper=False)
        a.ink([(m, m), (x1, y1)], 2.6, color=STRAW, taper=False)
        a.shape(ellipse(x1, y1, 9, 4.5, 12, rot=t), rgb("#e6c86a"), outline=FINE * 1.2, depth=1, mottle=0)
    a.shape(ellipse(m, m, 18, 18, 24), shade(STRAW, 0.15), outline=DETAIL * 1.3, depth=3, mottle=0)
    a.ink(ellipse(m, m, 10, 10, 20), DETAIL * 1.2, closed=True, color=rgb("#8a6a3e"))
    return a.image()


# -- harbor & water --------------------------------------------------------------------------------


def hull(cx, cy, L, W, bow=0.32, stern=0.12):
    """A boat hull outline from above: pointed bow at the top, squarer stern."""
    top, bot = cy - L / 2, cy + L / 2
    pts = [(cx, top)]
    for k in range(1, 9):
        t = k / 8
        pts.append((cx + W / 2 * math.sin(t * math.pi / 2), top + L * bow * t))
    pts += [(cx + W / 2, top + L * bow), (cx + W / 2, bot - L * stern), (cx + W * 0.38, bot)]
    return chaikin(pts + [(x, y) for x, y in mirror_x(pts, cx)[1:]] + [], True, 1)


def boat(L, W, paint=RED, seats=3, oars=True, sail=False, canoe=False):
    def make(seed=1500):
        pad = 80 if oars else 40
        w, h = int(W + pad * 2 + (60 if oars else 0)), int(L + 60)
        a = Art(w, h, seed)
        cx, cy = w / 2, h / 2
        outer = hull(cx, cy, L, W, bow=0.4 if canoe else 0.32, stern=0.05 if canoe else 0.12)
        if canoe:
            outer = chaikin([(cx, cy - L / 2), (cx + W / 2, cy - L * 0.15), (cx + W / 2, cy + L * 0.15), (cx, cy + L / 2), (cx - W / 2, cy + L * 0.15), (cx - W / 2, cy - L * 0.15)], True, 3)
        soft_shadow(a, outer, dx=6, dy=8, alpha=0.3, blur=8)
        if oars:
            for side in (-1, 1):
                y = cy + L * 0.05
                handle(a, cx + side * W * 0.1, y - 20, cx + side * (W / 2 + 70), y + 30, 9, WOOD_LIGHT)
                a.shape(ellipse(cx + side * (W / 2 + 76), y + 34, 12, 26, 20, rot=side * -0.5), WOOD_LIGHT, outline=DETAIL * 1.4, depth=2, mottle=0)
        a.shape(outer, paint, outline=OUTLINE, corner=0, wob=0.4, depth=8, light_k=0.4)
        inner = [(cx + (x - cx) * 0.84, cy + (y - cy) * 0.92) for x, y in outer]
        a.shape(inner, WOOD, outline=DETAIL * 1.3, corner=0, wob=0.3, depth=8, shade_k=0.3, light_k=0, ao=0.45, detail=lambda art, p: boards(art, cx - W / 2, cy - L / 2, cx + W / 2, cy + L / 2, WOOD, 5, vertical=True))
        for k in range(seats):
            y = cy - L * 0.25 + k * L * 0.5 / max(1, seats - 1) if seats > 1 else cy
            half = W * 0.42 * (0.85 if abs(y - cy) > L * 0.2 else 1)
            a.shape(rect(cx - half, y - 10, cx + half, y + 10), WOOD_LIGHT, outline=DETAIL * 1.2, corner=3, depth=3)
        if sail:
            a.shape(rect(cx - 7, cy - L * 0.42, cx + 7, cy + L * 0.25), WOOD_DARK, outline=DETAIL * 1.3, corner=3, depth=3)  # boom/mast line
            s_pts = [(cx + 8, cy - L * 0.4), (cx + W * 0.9, cy + L * 0.18), (cx + 8, cy + L * 0.22)]
            a.shape(s_pts, rgb("#ece4d3"), outline=DETAIL * 1.4, corner=4, depth=4, light_k=0.4, detail=lambda art, p: [art.ink([(cx + 10, cy - L * 0.4 + k * 30), (cx + W * 0.5, cy + k * 10)], FINE, color=shade(rgb("#ece4d3"), 0.3), alpha=0.6) for k in range(4)])
            a.shape(ellipse(cx, cy - L * 0.15, 11, 11, 20), WOOD_DARK, outline=DETAIL, depth=2, mottle=0)
        return a.image()

    return make


def pier(kind="straight", seed=1520):
    def make(seed=seed):
        if kind == "straight":
            w, h = 256, 512
        elif kind == "end":
            w, h = 256, 300
        else:
            w, h = 400, 400
        a = Art(w, h, seed)
        posts = []

        def planks(x0, y0, x1, y1, vertical):
            if vertical:
                for y in range(int(y0), int(y1), 28):
                    a.shape(rect(x0 + a.rng.uniform(-3, 3), y, x1 + a.rng.uniform(-3, 3), y + 26), vary(a.rng, WOOD, 0.07), outline=DETAIL * 1.2, corner=2, depth=2)
            else:
                for x in range(int(x0), int(x1), 28):
                    a.shape(rect(x, y0 + a.rng.uniform(-3, 3), x + 26, y1 + a.rng.uniform(-3, 3)), vary(a.rng, WOOD, 0.07), outline=DETAIL * 1.2, corner=2, depth=2)

        if kind == "straight":
            planks(30, 0, w - 30, h, True)
            posts = [(22, y) for y in (40, h / 2, h - 40)] + [(w - 22, y) for y in (40, h / 2, h - 40)]
        elif kind == "end":
            planks(30, 0, w - 30, h - 30, True)
            posts = [(22, 40), (22, h - 40), (w - 22, 40), (w - 22, h - 40), (w / 2, h - 22)]
        else:
            planks(30, 0, 226, 226, True)
            planks(226, 30, w, 226, False)
            posts = [(22, 40), (22, 200), (200, 240), (w - 40, 240), (w - 40, 22)]
        for x, y in posts:
            a.shape(ellipse(x, y, 17, 17, 24), WOOD_DARK, outline=DETAIL * 1.4, depth=3, light_k=0.3, detail=lambda art, p, x=x, y=y: art.ink(ellipse(x, y, 8, 8, 16), FINE, closed=True, color=shade(WOOD_DARK, 0.45)))
        return a.image()

    return make


def mooring_post(seed=1530):
    s = 140
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 34, 4, 5)
    a.shape(ellipse(m, m, 34, 34, 40), WOOD_DARK, outline=OUTLINE * 0.8, depth=5, light_k=0.3, detail=lambda art, p: [art.ink(ellipse(m, m, r, r, 32), FINE, closed=True, color=shade(WOOD_DARK, 0.45), alpha=0.8) for r in (12, 22)])
    a.ink(ellipse(m, m, 40, 40, 40), DETAIL * 2.6, closed=True, color=INK)
    a.ink(ellipse(m, m, 40, 40, 40), DETAIL * 1.5, closed=True, color=ROPE)
    pts = chaikin([(m + 38, m + 10), (m + 54, m + 40), (m + 30, m + 62)], False, 2)
    a.ink(pts, DETAIL * 2.6, color=INK)
    a.ink(pts, DETAIL * 1.5, color=ROPE)
    return a.image()


def bollard(seed=1531):
    s = 120
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 30, 4, 5)
    a.shape(ellipse(m, m, 34, 26, 40), rgb("#4a4c52"), outline=OUTLINE * 0.8, depth=5, light_k=0.5)
    a.shape(ellipse(m, m, 18, 14, 32), rgb("#5d6068"), outline=DETAIL, depth=3, light_k=0.5)
    return a.image()


def fishing_net(seed=1532, piled=False):
    def make(seed=seed):
        s = 320 if not piled else 220
        a = Art(s, s, seed)
        m = s / 2
        if piled:
            a.shape(blob(m, m, 84, a.rng, 12, 0.18), shade(NET, 0.2), outline=DETAIL * 1.3, smooth=True, depth=8, light_k=0.3, detail=lambda art, p: [art.ink([(m + art.rng.uniform(-80, 80), m + art.rng.uniform(-80, 80)) for _ in range(3)], FINE, color=shade(NET, 0.5), alpha=0.7) for _ in range(40)])
            for _ in range(6):
                t = a.rng.uniform(0, 6.28)
                a.shape(ellipse(m + 78 * math.cos(t), m + 78 * math.sin(t), 9, 9, 16), rgb("#c8a04a"), outline=FINE * 1.3, depth=2, light_k=0.4, mottle=0)
            return a.image()
        edge = blob(m, m, 130, a.rng, 14, 0.08)
        with a.clip(to_path(chaikin(edge, True, 2))):
            for k in range(-12, 13):
                a.ink([(m + k * 22 - 200, m - 200), (m + k * 22 + 200, m + 200)], FINE * 1.2, color=NET, alpha=0.95, taper=False, wob=0.6)
                a.ink([(m + k * 22 + 200, m - 200), (m + k * 22 - 200, m + 200)], FINE * 1.2, color=NET, alpha=0.95, taper=False, wob=0.6)
        a.ink(chaikin(edge, True, 2), DETAIL * 2.4, closed=True, color=INK)
        a.ink(chaikin(edge, True, 2), DETAIL * 1.4, closed=True, color=ROPE)
        for x, y in chaikin(edge, True, 2)[::10]:
            a.shape(ellipse(x, y, 9, 9, 16), rgb("#c8a04a"), outline=FINE * 1.3, depth=2, light_k=0.4, mottle=0)
        return a.image()

    return make


def lobster_trap(seed=1533):
    w, h = 240, 170
    a = Art(w, h, seed)
    a.shape(rect(14, 14, w - 14, h - 14), shade(WOOD, 0.1), corner=30, depth=8, light_k=0.3)
    a.shape(rect(26, 26, w - 26, h - 26), rgb("#3a3430"), outline=DETAIL, corner=24, depth=4, shade_k=0, light_k=0, ao=0.4)
    for x in range(30, w - 20, 22):
        handle(a, x, 18, x, h - 18, 7, WOOD_LIGHT)
    a.ink(ellipse(w / 2, h / 2, 26, 20, 28), DETAIL * 1.3, closed=True, color=NET)
    return a.image()


def anchor(seed=1534):
    w, h = 220, 280
    a = Art(w, h, seed)
    m = w / 2
    col = rgb("#4a4c52")
    a.ink([(m, 40), (m, h - 50)], 26, color=INK, taper=False)
    a.ink([(m, 40), (m, h - 50)], 17, color=col, taper=False)
    arc = [(m + 80 * math.sin(t), h - 50 - 70 * math.cos(t) + 70) for t in [-1.2 + k * 2.4 / 20 for k in range(21)]]
    arc = [(x, y - 70) for x, y in arc]
    a.ink(arc, 24, color=INK, taper=False)
    a.ink(arc, 15, color=col, taper=False)
    for x, y in (arc[0], arc[-1]):
        a.shape([(x - 14, y + 6), (x + 14, y + 6), (x, y - 22)], col, outline=DETAIL * 1.4, corner=2, depth=2, mottle=0)
    a.shape(rect(m - 50, 56, m + 50, 74), col, outline=DETAIL * 1.4, corner=6, depth=3, light_k=0.5)
    a.ink(ellipse(m, 28, 18, 18, 24), 12, closed=True, color=INK)
    a.ink(ellipse(m, 28, 18, 18, 24), 6, closed=True, color=col)
    return a.image()


def buoy(seed=1535, color=RED):
    def make(seed=seed):
        s = 140
        a = Art(s, s, seed)
        m = s / 2
        a.shape(ellipse(m + 4, m + 6, 52, 52, 48), WATER, outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)  # wet ring
        a.ink(ellipse(m + 4, m + 6, 52, 52, 48), FINE * 1.3, closed=True, color=FOAM, alpha=0.8)
        a.shape(ellipse(m, m, 40, 40, 48), color, outline=OUTLINE * 0.8, depth=6, light_k=0.5, detail=lambda art, p: [art.shape(rect(m - 42, y, m + 42, y + 12), rgb("#ece4d3"), outline=0, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0) for y in (m - 30, m + 10)])
        a.shape(ellipse(m, m, 10, 10, 16), IRON, outline=DETAIL, depth=2, mottle=0)
        return a.image()

    return make


def life_ring(seed=1536):
    s = 160
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 60, 4, 5)
    a.ink(ellipse(m, m, 48, 48, 64), 36, closed=True, color=INK)
    a.ink(ellipse(m, m, 48, 48, 64), 28, closed=True, color=rgb("#ece4d3"))
    for k in range(4):
        t0 = math.pi / 2 * k + 0.4
        a.ink([(m + 48 * math.cos(t0 + j * 0.06), m + 48 * math.sin(t0 + j * 0.06)) for j in range(12)], 28, color=RED, taper=False)
    a.ink(ellipse(m, m, 48, 48, 64), FINE * 1.3, closed=True, color=ROPE)
    return a.image()


def fish_barrel(seed=1537):
    s = 210
    a = Art(s, s, seed)
    m = s / 2
    R = m - 8
    a.shape(ellipse(m, m, R, R, 96), WOOD_DARK, depth=10, detail=lambda art, p: [art.ink([(m + (R - 22) * math.cos(t), m + (R - 22) * math.sin(t)), (m + R * math.cos(t), m + R * math.sin(t))], DETAIL * 0.8, color=shade(WOOD_DARK, 0.5), taper=False) for t in [2 * math.pi * k / 18 for k in range(18)]])
    a.ink(ellipse(m, m, R - 9, R - 9, 96), 9, closed=True, color=IRON)

    def fishes(art, p):
        for _ in range(9):
            x, y = m + art.rng.uniform(-50, 50), m + art.rng.uniform(-50, 50)
            fish_at(art, x, y, art.rng.uniform(0, 6.28), art.rng.uniform(48, 60))

    a.shape(ellipse(m, m, R - 22, R - 22, 80), rgb("#3a4a52"), outline=DETAIL * 1.2, depth=10, shade_k=0, light_k=0, ao=0.6, detail=fishes)
    return a.image()


def fish_at(a, x, y, t, L=60, color=rgb("#9fb3bc")):
    c, s_ = math.cos(t), math.sin(t)
    loc = lambda pts: [(x + px * c - py * s_, y + px * s_ + py * c) for px, py in pts]  # noqa: E731
    soft_shadow(a, loc([(-L / 2, 0), (0, -L * 0.18), (L / 2, 0), (0, L * 0.18)]), dx=2, dy=3, alpha=0.25, blur=2)
    a.shape(loc([(L * 0.38, 0), (L * 0.6, -L * 0.2), (L * 0.6, L * 0.2)]), shade(color, 0.15), outline=DETAIL, corner=1, depth=1, mottle=0)
    a.shape(chaikin(loc([(-L / 2, 0), (-L * 0.15, -L * 0.2), (L * 0.3, -L * 0.14), (L * 0.42, 0), (L * 0.3, L * 0.14), (-L * 0.15, L * 0.2)]), True, 2), vary(a.rng, color, 0.06), outline=DETAIL * 1.1, corner=0, depth=2, light_k=0.5, mottle=0)
    (ex, ey), = loc([(-L * 0.32, -L * 0.04)])
    dot(a, ex, ey, 2.2)


def fish_pile(seed=1538):
    s = 240
    a = Art(s, s, seed)
    for _ in range(14):
        fish_at(a, 120 + a.rng.uniform(-60, 60), 120 + a.rng.uniform(-60, 60), a.rng.uniform(0, 6.28), a.rng.uniform(56, 72), vary(a.rng, rgb("#9fb3bc"), 0.1))
    return a.image()


def single_fish(seed=1539):
    w, h = 140, 70
    a = Art(w, h, seed)
    fish_at(a, w / 2 - 6, h / 2, 0.0, 100)
    return a.image()


def crab(seed=1540):
    s = 140
    a = Art(s, s, seed)
    m = s / 2
    c = rgb("#c8543a")
    for side in (-1, 1):
        for k in range(3):
            y = m - 4 + k * 12
            pts = [(m + side * 24, y), (m + side * 46, y - 6 + k * 4), (m + side * 56, y + 6 + k * 6)]
            a.ink(pts, 8, color=INK, taper=True)
            a.ink(pts, 4.5, color=c, taper=True)
        a.ink([(m + side * 20, m - 14), (m + side * 36, m - 34)], 10, color=INK, taper=False)
        a.ink([(m + side * 20, m - 14), (m + side * 36, m - 34)], 6, color=c, taper=False)
        a.shape(scallop(m + side * 40, m - 42, 12, a.rng, 4, 0.3), c, outline=DETAIL * 1.2, depth=2, light_k=0.4, mottle=0)
    a.shape(ellipse(m, m, 30, 24, 36), c, outline=DETAIL * 1.6, depth=3, light_k=0.45)
    for side in (-1, 1):
        dot(a, m + side * 8, m - 22, 3.4)
    return a.image()


def seaweed(seed=1541):
    s = 220
    a = Art(s, s, seed)
    m = s / 2
    col = rgb("#4a6a3a")
    for k in range(9):
        t = 2 * math.pi * k / 9 + a.rng.uniform(-0.2, 0.2)
        pts = [(m + d * math.cos(t) + 8 * math.sin(d / 12), m + d * math.sin(t) + 8 * math.cos(d / 14)) for d in range(0, 96, 6)]
        a.ink(pts, 13, color=INK, taper=True)
        a.ink(pts, 8, color=vary(a.rng, col, 0.1), taper=True)
    return a.image()


def lily_pads(seed=1542):
    s = 260
    a = Art(s, s, seed)
    for _ in range(7):
        x, y = a.rng.uniform(50, s - 50), a.rng.uniform(50, s - 50)
        r = a.rng.uniform(22, 36)
        t = a.rng.uniform(0, 6.28)
        pad = [(x, y)] + [(x + r * math.cos(t + 0.35 + k * 0.2), y + r * math.sin(t + 0.35 + k * 0.2)) for k in range(29)]
        a.shape(pad, vary(a.rng, rgb("#6d9a48"), 0.06), outline=DETAIL * 1.2, corner=0, depth=2, light_k=0.4, mottle=0, detail=lambda art, p, x=x, y=y, r=r: [art.ink([(x, y), (x + r * 0.8 * math.cos(q), y + r * 0.8 * math.sin(q))], FINE * 0.9, color=shade(rgb("#6d9a48"), 0.4), alpha=0.7) for q in [k * 1.1 for k in range(5)]])
    x, y = s / 2 + 10, s / 2 - 10
    for k in range(8):
        pa = 2 * math.pi * k / 8
        a.shape(ellipse(x + 10 * math.cos(pa), y + 10 * math.sin(pa), 11, 6, 16, rot=pa), rgb("#f2c2d2"), outline=FINE * 1.2, depth=1, mottle=0)
    dot(a, x, y, 5, rgb("#f6d24a"))
    return a.image()


def reeds_clump(seed=1543):
    s = 240
    a = Art(s, s, seed)
    m = s / 2
    blades(a, m, m, 22, 104, [rgb("#7a9a4a"), rgb("#9aa85a"), GREEN_D], width=6)
    for _ in range(7):
        t, d = a.rng.uniform(0, 6.28), a.rng.uniform(40, 90)
        a.shape(ellipse(m + d * math.cos(t), m + d * math.sin(t), 6, 15, 16, rot=t), rgb("#6e4a2f"), outline=FINE * 1.3, depth=2, light_k=0.3, mottle=0)
    return a.image()


def water_rocks(seed=1544):
    s = 260
    a = Art(s, s, seed)
    m = s / 2
    for _ in range(4):
        x, y, r = m + a.rng.uniform(-60, 60), m + a.rng.uniform(-60, 60), a.rng.uniform(30, 48)
        a.shape(blob(x + 4, y + 6, r * 1.25, a.rng, 10, 0.15), WATER, outline=0, smooth=True, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        a.ink(chaikin(blob(x + 4, y + 6, r * 1.25, a.rng, 10, 0.15), True, 2), FINE * 1.3, closed=True, color=FOAM, alpha=0.85)
    for _ in range(4):
        x, y, r = m + a.rng.uniform(-60, 60), m + a.rng.uniform(-60, 60), a.rng.uniform(26, 42)
        a.shape(blob(x, y, r, a.rng, 9, 0.18), rgb("#8f948f"), outline=DETAIL * 1.6, smooth=True, depth=6, light_k=0.45, detail=lambda art, p, x=x, y=y: art.shape(blob(x - 10, y + 10, 12, art.rng, 8, 0.3), rgb("#5a7a3a"), outline=0, smooth=True, depth=1, shade_k=0, light_k=0.2, ao=0, mottle=0.1))
    return a.image()


def dock_crates(seed=1545):
    w, h = 320, 240
    a = Art(w, h, seed)
    from objects import crate

    import numpy as np

    for x, y, s_ in ((10, 70, 160), (150, 80, 150), (70, 10, 140)):
        img = crate(seed=a.rng.randint(0, 999)).resize((s_, s_))
        a.c.drawImageRect(skia.Image.fromarray(np.asarray(img), colorType=skia.kRGBA_8888_ColorType), skia.Rect.MakeXYWH(x, y, s_, s_))
    pts = chaikin([(20, h - 20), (100, h - 50), (200, h - 30), (300, h - 60)], False, 2)
    a.ink(pts, DETAIL * 2.6, color=INK)
    a.ink(pts, DETAIL * 1.5, color=ROPE)
    return a.image(grain=0)


def gangplank(seed=1546):
    w, h = 200, 480
    a = Art(w, h, seed)
    for y in range(14, h - 10, 34):
        a.shape(rect(26, y, w - 26, y + 30), vary(a.rng, WOOD_LIGHT, 0.06), outline=DETAIL * 1.2, corner=3, depth=2)
        a.ink([(36, y + 15), (w - 36, y + 15)], FINE * 1.1, color=shade(WOOD_LIGHT, 0.4), alpha=0.6)
    for x in (18, w - 18):
        handle(a, x, 8, x, h - 8, 12, WOOD_DARK)
    return a.image()


def oars(seed=1547):
    w, h = 400, 160
    a = Art(w, h, seed)
    for y, t in ((50, 0.05), (110, -0.05)):
        handle(a, 20, y, 300, y + t * 280, 10, WOOD_LIGHT)
        a.shape(ellipse(330, y + t * 310, 50, 16, 24, rot=t), WOOD_LIGHT, outline=DETAIL * 1.6, depth=2, light_k=0.3, mottle=0)
    return a.image()


def rope_pile(seed=1548):
    s = 200
    a = Art(s, s, seed)
    m = s / 2
    for k in range(3):
        cx, cy = m + a.rng.uniform(-24, 24), m + a.rng.uniform(-24, 24)
        sp = [(cx + (12 + 3.6 * t) * math.cos(t * 1.1), cy + (10 + 3.0 * t) * math.sin(t * 1.1)) for t in [j * 0.15 for j in range(110 - k * 20)]]
        a.ink(sp, 14, color=INK, taper=False)
        a.ink(sp, 9, color=vary(a.rng, ROPE, 0.05), taper=False)
    return a.image()


FARM = {
    # Animals
    "Chicken": bird_obj(110, body=rgb("#ece4d3"), wing=rgb("#d8ccb4"), comb=rgb("#c8443a")),
    "Brown Hen": bird_obj(110, body=rgb("#a8653a"), wing=rgb("#8a4e2a"), comb=rgb("#c8443a")),
    "Rooster": bird_obj(130, body=rgb("#b8552f"), wing=rgb("#5a3a2a"), tail=rgb("#2f4a3a"), comb=rgb("#d03a30")),
    "Chicks": chicks,
    "Duck": bird_obj(130, body=rgb("#9a8a6a"), wing=rgb("#7a6a4e"), head_c=rgb("#3f6a4a"), beak=rgb("#e0a640")),
    "White Duck": bird_obj(130, body=rgb("#f2ece0"), wing=rgb("#e0d8c8"), beak=rgb("#e0883a")),
    "Goose": bird_obj(170, body=rgb("#ece4d3"), wing=rgb("#d0c8b8"), beak=rgb("#e0883a"), long_neck=True),
    "Crow": bird_obj(100, body=rgb("#2e2e36"), wing=rgb("#24242a"), beak=rgb("#3a3a40")),
    "Owl": owl,
    "Pigeon": bird_obj(90, body=rgb("#9aa0aa"), wing=rgb("#7a8090"), head_c=rgb("#6a7080"), beak=rgb("#d8c0a0")),
    "Cow": animal(320, 640, L=440, W=220, color=rgb("#f2ece0"), head=0.24, muzzle=(rgb("#e6b8a8"), 0.16), ears="side", horns=rgb("#e6dcc4"), tail="thin", spots=(rgb("#3a3430"), 6)),
    "Brown Cow": animal(320, 640, L=440, W=220, color=rgb("#8a5a3a"), head=0.24, muzzle=(rgb("#d8b8a0"), 0.16), ears="side", horns=rgb("#e6dcc4"), tail="thin"),
    "Ox": animal(340, 660, L=460, W=240, color=rgb("#6a4e3a"), head=0.24, muzzle=(rgb("#c9a88a"), 0.16), ears="side", horns=rgb("#e6dcc4"), tail="thin"),
    "Pig": animal(220, 400, L=260, W=150, color=rgb("#e8b8a8"), head=0.26, muzzle=(rgb("#d89a8a"), 0.14), ears="floppy", tail="curly"),
    "Piglet": animal(130, 230, L=140, W=84, color=rgb("#f0c4b4"), head=0.34, muzzle=(rgb("#e0a898"), 0.14), ears="floppy", tail="curly"),
    "Black Pig": animal(220, 400, L=260, W=150, color=rgb("#4a4248"), head=0.26, muzzle=(rgb("#6a5a60"), 0.14), ears="floppy", tail="curly"),
    "Sheep": animal(200, 340, L=220, W=150, color=rgb("#efe7d6"), head=0.3, muzzle=None, ears="side", ear_color=rgb("#3a3430"), tail="stub", wool=True, leg_color=rgb("#3a3430")),
    "Black Sheep": animal(200, 340, L=220, W=150, color=rgb("#4a4442"), head=0.3, ears="side", ear_color=rgb("#2a2422"), tail="stub", wool=True, leg_color=rgb("#2a2422")),
    "Lamb": animal(140, 230, L=140, W=96, color=rgb("#f4eee2"), head=0.32, ears="side", ear_color=rgb("#d8c8b8"), tail="stub", wool=True),
    "Goat": animal(170, 330, L=200, W=110, color=rgb("#d8ccb4"), head=0.34, muzzle=(rgb("#c8b8a0"), 0.14), ears="side", horns=rgb("#8a7a6a"), tail="stub"),
    "Horse": animal(240, 620, L=400, W=170, color=rgb("#8a5a3a"), head=0.36, muzzle=(rgb("#6a4a32"), 0.14), ears="up", tail="bushy", tail_color=rgb("#3a2a22"), mane=rgb("#3a2a22")),
    "White Horse": animal(240, 620, L=400, W=170, color=rgb("#ece4d8"), head=0.36, muzzle=(rgb("#c8b8b0"), 0.14), ears="up", tail="bushy", tail_color=rgb("#d8d0c4"), mane=rgb("#d8d0c4")),
    "Black Horse": animal(240, 620, L=400, W=170, color=rgb("#3a3436"), head=0.36, muzzle=(rgb("#4a4446"), 0.14), ears="up", tail="bushy", tail_color=rgb("#24201e"), mane=rgb("#24201e")),
    "Donkey": animal(200, 480, L=300, W=140, color=rgb("#8a8278"), head=0.38, muzzle=(rgb("#d8d0c4"), 0.15), ears="up", tail="thin", mane=rgb("#4a4440")),
    "Dog": animal(150, 300, L=180, W=96, color=rgb("#a8783e"), head=0.36, muzzle=(rgb("#8a6030"), 0.16), ears="floppy", tail="thin"),
    "Black Dog": animal(150, 300, L=180, W=96, color=rgb("#3a3436"), head=0.36, muzzle=(rgb("#4a4446"), 0.16), ears="floppy", tail="thin"),
    "Hound": animal(150, 330, L=210, W=90, color=rgb("#c9a878"), head=0.38, muzzle=(rgb("#a8885a"), 0.18), ears="floppy", tail="thin", spots=(rgb("#6a4a32"), 3)),
    "Cat": cat,
    "Black Cat": lambda: cat(1366, rgb("#3a3436")),
    "Orange Cat": lambda: cat(1367, rgb("#d08a4a")),
    "Calf": animal(220, 400, L=260, W=140, color=rgb("#c9a07a"), head=0.28, muzzle=(rgb("#e6c8b0"), 0.16), ears="side", tail="thin"),
    "Pony": animal(200, 460, L=290, W=140, color=rgb("#a8845a"), head=0.36, muzzle=(rgb("#7a5a3e"), 0.14), ears="up", tail="bushy", tail_color=rgb("#e6dcc4"), mane=rgb("#e6dcc4")),
    "Black Goat": animal(170, 330, L=200, W=110, color=rgb("#3a3436"), head=0.34, muzzle=(rgb("#5a5254"), 0.14), ears="side", horns=rgb("#8a7a6a"), tail="stub"),
    "Brown Sheep": animal(200, 340, L=220, W=150, color=rgb("#a88a6a"), head=0.3, ears="side", ear_color=rgb("#3a3430"), tail="stub", wool=True, leg_color=rgb("#3a3430")),
    "Turkey": bird_obj(150, body=rgb("#5a4a3e"), wing=rgb("#7a5a3e"), tail=rgb("#8a6a4a"), head_c=rgb("#c8a0a0"), comb=rgb("#c8443a")),
    "Rat": rat,
    "Frog": frog,
    "Snake": snake,
    # Farm
    "Straw Skep": skep,
    "Beehive Box": box_hive,
    "Wheat Rows": crop_rows(p_wheat, 4),
    "Corn Rows": crop_rows(p_corn, 3),
    "Cabbage Rows": crop_rows(p_cabbage, 4),
    "Carrot Rows": crop_rows(p_carrot, 5),
    "Pumpkin Patch": crop_rows(p_pumpkin, 3),
    "Pumpkin": pumpkin(1420, 46),
    "Small Pumpkin": pumpkin(1432, 30),
    "Big Pumpkin": pumpkin(1433, 70),
    "Scarecrow": scarecrow,
    "Feed Trough": feed_trough,
    "Milk Churn": milk_churn,
    "Butter Churn": butter_churn,
    "Egg Basket": egg_basket,
    "Hay Fork": hay_fork,
    "Plough": plough,
    "Water Pump": water_pump,
    "Grape Trellis": trellis,
    "Compost Heap": compost,
    "Wheat Sheaf": wheat_sheaf,
    # Harbor & water
    "Rowboat": boat(560, 220, RED, seats=3, oars=True),
    "Green Rowboat": lambda: boat(560, 220, rgb("#4f7a5a"), seats=3, oars=True)(1501),
    "Small Boat": boat(400, 170, RED, seats=2, oars=True),
    "Beached Boat": boat(520, 210, rgb("#8a7a6a"), seats=3, oars=False),
    "Canoe": boat(520, 130, rgb("#a8653a"), seats=2, oars=False, canoe=True),
    "Sailboat": boat(640, 240, RED, seats=2, oars=False, sail=True),
    "Pier": pier("straight"),
    "Pier End": pier("end"),
    "Pier Corner": pier("corner"),
    "Mooring Post": mooring_post,
    "Bollard": bollard,
    "Fishing Net": fishing_net(1532),
    "Net Pile": fishing_net(1549, piled=True),
    "Lobster Trap": lobster_trap,
    "Anchor": anchor,
    "Buoy": buoy(1535, RED),
    "Green Buoy": buoy(1550, rgb("#4f7a5a")),
    "Life Ring": life_ring,
    "Fish Barrel": fish_barrel,
    "Fish Pile": fish_pile,
    "Fish": single_fish,
    "Crab": crab,
    "Seaweed": seaweed,
    "Lily Pads": lily_pads,
    "Reed Clump": reeds_clump,
    "Rocks in Water": water_rocks,
    "Dock Crates": dock_crates,
    "Gangplank": gangplank,
    "Oars": oars,
    "Rope Pile": rope_pile,
}

FARM_COLORABLE = {"Rowboat", "Small Boat", "Sailboat", "Buoy", "Life Ring"}
