"""SRD 5.2.1 wondrous items: bags, bottles, horns, decks, cubes, carpets,
holes and the rest of the magic gear that isn't worn, wielded, drunk or read.
Top-down, same pen style (red g==b = colorable). Floor-sized items (carpet,
holes, sphere, unfolded boat, deployed fortress) are at map scale; small
trinkets are drawn larger than life, like the rest of the pack's loose items."""

import math


from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, dot, scallop, soft_shadow
from obj_cave import FIRE, fire
from obj_craft import handle, rot_pts
from obj_dungeon import chain
from obj_farm import autocrop, beast, bird, hull
from obj_magic import GLASS, PARCH, glow
from obj_nature import tube
from obj_tavern import GOLD, SILVER
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

LEATHER = rgb("#8a5a3a")
CLOTH = rgb("#cdb07e")
SILK = rgb("#e6dcc4")
ROPE = rgb("#c9b088")
BRONZE = rgb("#b07a42")
COPPER = rgb("#c27a4e")
DARK_IRON = rgb("#46484e")
RUST = rgb("#9a5a3a")
IVORY = rgb("#ece2c8")
OBSIDIAN = rgb("#2c2a30")
ONYX = rgb("#34323a")
MARBLE = rgb("#e4e0d8")
EBONY = rgb("#3a2e2a")
SERPENTINE = rgb("#6f8a5a")
ARCANE = rgb("#8a6ad8")
VOID = rgb("#141018")
WATER = rgb("#5f8ea4")
FOAM = rgb("#dceff5")
SMOKE = rgb("#9a9690")
V = 0.08


def art(w, h, seed):
    return Art(int(w), int(h), seed)


def flat(a, pts, color, outline=DETAIL, **kw):
    """A small flat piece (no shading bands): labels, glyphs, insets."""
    kw.setdefault("depth", 1)
    return a.shape(pts, color, outline=outline, corner=kw.pop("corner", 1), shade_k=0, light_k=0, ao=0, mottle=0, **kw)


def sparkle(a, x, y, r, color=(255, 250, 235), alpha=0.95):
    """A four-pointed glint."""
    pts = []
    for k in range(8):
        t = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.28
        pts.append((x + rr * math.cos(t), y + rr * math.sin(t)))
    p = to_path(pts)
    a.fill_path(p, color, alpha)


def rune(a, x, y, r, color, kind=0, width=None):
    """A small arcane glyph: a few strokes inside a circle-ish frame."""
    w = width or FINE * 1.1
    glyphs = [
        [[(-1, -1), (1, 1)], [(-1, 1), (0, 0)], [(0, -1), (0, 1)]],
        [[(-1, 0), (1, 0)], [(0, -1), (-0.6, 1)], [(0, -1), (0.6, 1)]],
        [[(-0.8, -1), (-0.8, 1), (0.8, 1)], [(-0.8, 0), (0.8, -1)]],
        [[(0, -1), (1, 0), (0, 1), (-1, 0), (0, -1)], [(0, -0.4), (0, 0.4)]],
        [[(-1, -1), (0, 1), (1, -1)], [(-0.5, 0), (0.5, 0)]],
        [[(-1, -0.6), (1, -0.6)], [(-1, 0.6), (1, 0.6)], [(0, -1), (0, 1)]],
    ]
    for stroke in glyphs[kind % len(glyphs)]:
        a.ink([(x + px * r, y + py * r) for px, py in stroke], w, color=color, alpha=0.9, wob=0.2, taper=False)


def cord(a, pts, w=6, color=ROPE):
    a.ink(pts, w + 4, color=INK, taper=False, var=V)
    a.ink(pts, w, color=color, taper=False, var=V)


def sack(a, cx, cy, r, color, neck=0.42, tie=ROPE, seed_jag=0.07, open_=False, inside=None):
    """A soft bag from above: a lumpy body, the gathered neck (or an open
    mouth with `inside(art, x, y, r)` drawn in it) and a tie."""
    soft_shadow(a, (cx + 2, cy + 4), r * 0.95, 4, 6, 0.32, 5)
    body = blob(cx, cy, r, a.rng, 11, seed_jag)

    def folds(art, p):
        for k in range(5):
            t = -2.4 + k * 0.45 + art.rng.uniform(-0.1, 0.1)
            art.ink([(cx + r * 0.32 * math.cos(t), cy + r * 0.32 * math.sin(t)), (cx + r * 0.88 * math.cos(t), cy + r * 0.88 * math.sin(t))], FINE * 1.1, color=shade(color, 0.45), alpha=0.6)

    a.shape(body, color, smooth=True, depth=max(5, r * 0.12), light_k=0.35, detail=folds)
    if open_:
        a.shape(ellipse(cx, cy - r * 0.15, r * neck, r * neck * 0.8, 32), shade(color, 0.15), outline=DETAIL * 1.4, depth=4, light_k=0.3)
        mouth = ellipse(cx, cy - r * 0.15, r * neck * 0.75, r * neck * 0.6, 28)
        p = a.shape(mouth, VOID, outline=DETAIL, depth=2, shade_k=0, light_k=0, ao=0, mottle=0)
        if inside:
            with a.clip(p):
                inside(a, cx, cy - r * 0.15, r * neck * 0.75)
        a.ink(ellipse(cx, cy - r * 0.15, r * neck * 0.95, r * neck * 0.77, 32), DETAIL * 1.3, closed=True, color=tie, alpha=0.9)
    else:
        ny = cy - r * 0.62
        a.shape(scallop(cx, ny, r * neck * 0.75, a.rng, 7, 0.22, ry=r * neck * 0.5), shade(color, 0.1), outline=DETAIL * 1.3, depth=3, light_k=0.3, mottle=0)
        a.ink([(cx - r * neck * 0.6, ny + r * 0.22), (cx + r * neck * 0.6, ny + r * 0.22)], DETAIL * 1.6, color=tie, taper=False)
        cord(a, [(cx + r * neck * 0.5, ny + r * 0.24), (cx + r * 0.55, ny + r * 0.4), (cx + r * 0.62, ny + r * 0.62)], 4, tie)
        dot(a, cx + r * 0.62, ny + r * 0.64, 5, tie)


def bottle_lying(a, x, y, L, r, color, ang=0.0, stopper=WOOD_LIGHT, neck=0.32, detail=None, outline=OUTLINE * 0.8):
    """A bottle on its side seen from above: round body, shoulder, neck and
    stopper along `ang`."""
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    body = chaikin([(x, y - r), (x + L * 0.55, y - r), (x + L * 0.68, y - r * neck * 1.1), (x + L * 0.88, y - r * neck), (x + L * 0.88, y + r * neck), (x + L * 0.68, y + r * neck * 1.1), (x + L * 0.55, y + r), (x, y + r), (x - r * 0.25, y)], True, 2)
    soft_shadow(a, loc(body), dx=5, dy=6, alpha=0.3, blur=5)
    a.shape(loc(body), color, outline=outline, corner=0, depth=max(4, r * 0.2), light_k=0.5, detail=detail, var=V)
    a.shape(loc(rect(x + L * 0.86, y - r * neck * 1.05, x + L, y + r * neck * 1.05)), stopper, outline=DETAIL * 1.2, corner=3, depth=2, mottle=0, var=V)
    a.ink(loc([(x + r * 0.2, y - r * 0.55), (x + L * 0.5, y - r * 0.62)]), FINE * 2, color=tint(color, 0.7), alpha=0.75)


def horn_shape(a, x0, y0, L, w0, w1, color, bend=2.4, bell=None, bands=(), detail=None):
    """A curved horn lying flat: mouthpiece at (x0, y0), bell to the right."""
    pts = [(x0 + L * t, y0 - L * 0.28 * math.sin(t * bend)) for t in [k / 20 for k in range(21)]]
    soft_shadow(a, tube(pts, w0, w1), dx=4, dy=6, alpha=0.3, blur=5)
    a.shape(tube(pts, w0, w1), color, depth=5, light_k=0.45, detail=detail, var=V)
    for t in bands:
        i = int(t * 20)
        x, y = pts[i]
        ww = w0 + (w1 - w0) * t
        a.ink([(x - 3, y - ww * 0.55), (x + 3, y + ww * 0.55)], DETAIL * 2.4, color=INK, taper=False, wob=0)
        a.ink([(x - 3, y - ww * 0.52), (x + 3, y + ww * 0.52)], DETAIL * 1.4, color=bell or GOLD, taper=False, wob=0)
    ex, ey = pts[-1]
    if bell:
        a.shape(ellipse(ex, ey, w1 * 0.26, w1 * 0.56, 24), bell, outline=DETAIL * 1.3, depth=2, light_k=0.5, mottle=0)
        a.shape(rot_pts(rect(pts[0][0] - 6, pts[0][1] - w0 * 0.7, pts[0][0] + 14, pts[0][1] + w0 * 0.7), pts[0][0], pts[0][1], -0.5), bell, outline=DETAIL, corner=3, depth=1, mottle=0)
    a.shape(ellipse(ex, ey, w1 * 0.18, w1 * 0.44, 24), shade(color, 0.6), outline=DETAIL * 1.1, depth=2, shade_k=0, light_k=0, mottle=0)
    return pts


def plinth(a, cx, cy, r, color=STONE):
    soft_shadow(a, (cx, cy), r, 4, 6, 0.35, 5)
    a.shape(ellipse(cx, cy, r, r, 40), color, outline=DETAIL * 1.6, depth=5, light_k=0.4)
    a.ink(ellipse(cx, cy, r * 0.82, r * 0.82, 40), FINE, closed=True, color=shade(color, 0.4), alpha=0.6)


# -- bags ----------------------------------------------------------------------------------------


def bag_of_holding(seed=4001, color=RED):
    s = 200
    a = art(s, s, seed)
    sack(a, s / 2, s / 2 + 8, 72, color, tie=GOLD)
    for k in range(3):
        rune(a, s / 2 - 30 + k * 30, s / 2 + 30, 8, GOLD, k)
    return a.image()


def bag_of_holding_open(seed=4002, color=RED):
    """Its mouth opened on the void inside, starry and bottomless."""
    s = 220
    a = art(s, s, seed)

    def void(art, x, y, r):
        glow(art, x, y, r * 1.2, ARCANE, 0.5)
        for _ in range(14):
            sparkle(art, x + art.rng.uniform(-r, r), y + art.rng.uniform(-r, r), art.rng.uniform(2, 5), tint(ARCANE, 0.6))

    sack(a, s / 2, s / 2 + 10, 82, color, neck=0.62, tie=GOLD, open_=True, inside=void)
    return a.image()


def bag_of_devouring(seed=4003):
    """Looks like a Bag of Holding, but its mouth is a maw: a wet, fleshy
    gullet ringed by teeth."""
    s = 220
    a = art(s, s, seed)
    flesh = rgb("#7a2f3a")

    def maw(art, x, y, r):
        art.shape(ellipse(x, y, r, r * 0.8, 32), flesh, outline=0, depth=6, shade_k=0.6, light_k=0.2, ao=0.6)
        art.shape(ellipse(x, y + 2, r * 0.45, r * 0.35, 24), rgb("#2a0e14"), outline=0, depth=2, shade_k=0, light_k=0, ao=0, mottle=0)
        for k in range(14):
            t = 2 * math.pi * k / 14
            bx, by = x + r * 0.95 * math.cos(t), y + r * 0.76 * math.sin(t)
            tx, ty = x + r * 0.62 * math.cos(t), y + r * 0.5 * math.sin(t)
            nx, ny = -math.sin(t) * 5, math.cos(t) * 4
            art.shape([(bx - nx, by - ny), (bx + nx, by + ny), (tx, ty)], IVORY, outline=FINE * 1.1, corner=0, depth=1, shade_k=0.2, light_k=0, ao=0, mottle=0)

    sack(a, s / 2, s / 2 + 10, 82, rgb("#6a5a4a"), neck=0.62, tie=rgb("#4a3a2e"), open_=True, inside=maw)
    return a.image()


def bag_of_beans(seed=4004):
    """A heavy cloth bag, with a few of its dried beans spilled out."""
    w, h = 220, 190
    a = art(w, h, seed)
    bean = rgb("#9a5a3a")
    for _ in range(9):
        x, y = a.rng.uniform(130, 205), a.rng.uniform(110, 175)
        t = a.rng.uniform(0, 3.14)
        soft_shadow(a, (x, y), 5, 1, 2, 0.3, 1.5)
        a.shape(ellipse(x, y, 7, 4.5, 16, rot=t), vary(a.rng, bean, 0.12), outline=FINE * 1.2, depth=1, shade_k=0.3, light_k=0.4, ao=0, mottle=0)
    sack(a, 90, 92, 66, rgb("#b8a27a"), tie=rgb("#6a4a2e"))
    return a.image()


TRICKS = {"Gray": rgb("#9a9894"), "Rust": rgb("#a8603e"), "Tan": rgb("#c9a882")}


def bag_of_tricks(color, seed=4005):
    """A small furry bag: tufts of fur all over it."""

    def make():
        s = 170
        a = art(s, s, seed)
        sack(a, s / 2, s / 2 + 8, 56, color, tie=shade(color, 0.5))
        for _ in range(28):
            t = a.rng.uniform(0, 6.28)
            d = a.rng.uniform(0.1, 0.85) * 52
            x, y = s / 2 + d * math.cos(t), s / 2 + 12 + d * math.sin(t)
            if y < s / 2 - 18:
                continue
            a.ink([(x, y), (x + a.rng.uniform(-5, 5), y + a.rng.uniform(4, 9))], FINE * 1.2, color=shade(color, 0.4), alpha=0.7)
        return a.image()

    return make


def handy_haversack(seed=4006, color=RED):
    """A backpack with a central pouch and two side pouches."""
    w, h = 270, 250
    a = art(w, h, seed)
    leather = rgb("#7a4e32")
    soft_shadow(a, rect(40, 40, w - 40, h - 20), dx=6, dy=8, alpha=0.3, blur=6)
    for x0 in (14, w - 74):
        a.shape(rect(x0, 80, x0 + 60, 200), color, corner=16, depth=6, light_k=0.35)
        a.shape(rect(x0 + 4, 80, x0 + 56, 120), shade(color, 0.15), outline=DETAIL * 1.3, corner=12, depth=3)
        dot(a, x0 + 30, 116, 5, GOLD)
    a.shape(rect(64, 30, w - 64, h - 18), color, corner=22, depth=8, light_k=0.35)
    a.shape(rect(70, 30, w - 70, 120), leather, outline=DETAIL * 1.5, corner=18, depth=5)
    a.shape(rect(116, 108, 154, 132), GOLD, outline=DETAIL * 1.2, corner=4, depth=2, light_k=0.5, mottle=0)
    for x in (100, 170):
        a.ink([(x, 20), (x, 34)], DETAIL * 3, color=INK, taper=False)
        a.ink([(x, 20), (x, 34)], DETAIL * 1.6, color=leather, taper=False)
    rune(a, w / 2, 180, 14, GOLD, 3, FINE * 1.5)
    return a.image()


def dust_packet(color, spill, seed, label=None):
    """A small paper packet folded shut, a pinch of its dust spilled beside."""

    def make():
        w, h = 170, 150
        a = art(w, h, seed)
        for _ in range(60):
            t = a.rng.uniform(0, 6.28)
            d = a.rng.uniform(0, 1) ** 0.7 * 34
            dot(a, 118 + d * math.cos(t), 98 + d * 0.7 * math.sin(t), a.rng.uniform(1.2, 2.8), vary(a.rng, spill, 0.1), 0.85)
        pts = rot_pts(rect(28, 30, 110, 96), 69, 63, -0.25)
        soft_shadow(a, pts, dx=4, dy=5, alpha=0.3, blur=4)
        a.shape(pts, PARCH, outline=DETAIL * 1.5, corner=5, depth=4, light_k=0.4, detail=lambda art, p: art.ink(rot_pts([(28, 56), (69, 72), (110, 56)], 69, 63, -0.25), FINE * 1.4, color=shade(PARCH, 0.4), alpha=0.8))
        dot(a, *rot_pts([(69, 72)], 69, 63, -0.25)[0], 7, label or rgb("#8a2f3a"))
        return a.image()

    return make


# -- bottles, flasks and vessels -----------------------------------------------------------------


def efreeti_bottle(seed=4011):
    """A heavy, ornate brass bottle with a lead stopper sealed by wax."""
    w, h = 250, 140
    a = art(w, h, seed)

    def chase(art, p):
        for x in (70, 104):
            art.ink([(x, 30), (x + 6, 110)], DETAIL * 1.1, color=shade(BRASS, 0.45), alpha=0.85)
        for k in range(4):
            art.ink(ellipse(56 + k * 12, 70, 8, 8, 16), FINE, closed=True, color=shade(BRASS, 0.4), alpha=0.6)

    bottle_lying(a, 30, 70, 200, 46, BRASS, -0.05, stopper=rgb("#7a7e86"), neck=0.36, detail=chase)
    dot(a, 226, 61, 9, rgb("#a8303a"))
    return a.image()


def eversmoking_bottle(seed=4012, smoking=False):
    w, h = (480, 440) if smoking else (210, 130)
    a = art(w, h, seed)
    bx, by = (40, h - 80) if smoking else (30, 65)
    if smoking:
        # Smoke pouring out of the open neck, billowing away.
        for k in range(14):
            t = k / 13
            x = bx + 150 + 180 * t + a.rng.uniform(-15, 15)
            y = by - 60 - 210 * t + a.rng.uniform(-20, 20)
            r = 26 + 60 * t
            col = mix(SMOKE, tint(SMOKE, 0.5), a.rng.random())
            a.shape(scallop(x, y, r, a.rng, 7, 0.2), col, outline=DETAIL * 0.9, outline_alpha=0.35, depth=6, shade_k=0.35, light_k=0.3, ao=0, mottle=0.04)
    bottle_lying(a, bx, by, 170, 40, rgb("#4f5a4a"), -0.1 if not smoking else -0.35, stopper=WOOD_LIGHT)
    return autocrop(a.image(), 12) if smoking else a.image()


def decanter(seed=4013, pouring=False):
    """A corked flask whose stopper is out: a stream of water splashing
    into a spreading puddle when it pours."""
    w, h = (420, 300) if pouring else (190, 150)
    a = art(w, h, seed)
    if pouring:
        pool = blob(300, 170, 120, a.rng, 14, 0.15, ry=100)
        a.shape(pool, WATER, outline=DETAIL * 1.2, outline_alpha=0.6, smooth=True, depth=10, shade_k=0.3, light_k=0.5, detail=lambda art, p: [art.ink(ellipse(300, 170, 30 + 22 * k, 24 + 18 * k, 40), FINE * 1.2, closed=True, color=FOAM, alpha=0.6) for k in range(4)])
        a.ink([(170, 150), (230, 160), (300, 170)], 18, color=FOAM, alpha=0.9)
        a.ink([(170, 150), (230, 160), (300, 170)], 8, color=tint(WATER, 0.6), alpha=0.9)
        for _ in range(10):
            t = a.rng.uniform(0, 6.28)
            dot(a, 300 + 40 * math.cos(t), 170 + 30 * math.sin(t), a.rng.uniform(3, 6), FOAM)

    def wave(art, p):
        art.ink([(40, 80), (70, 70), (100, 80), (130, 70)], FINE * 1.5, color=tint(GLASS, 0.6), alpha=0.8)

    bottle_lying(a, 30, 80 if not pouring else 150, 150, 46, rgb("#9ab8c0"), 0.0, stopper=rgb("#b88a5a") if not pouring else rgb("#9ab8c0"), neck=0.34, detail=wave)
    if pouring:
        a.shape(ellipse(60, 250, 14, 10, 20), rgb("#b88a5a"), outline=DETAIL, depth=2, mottle=0)
    return a.image()


def iron_flask(seed=4014):
    """A dark iron flask with a brass stopper, covered in sigils."""
    w, h = 220, 130
    a = art(w, h, seed)

    def sigils(art, p):
        for k in range(4):
            rune(art, 50 + k * 26, 65 + (k % 2) * 10 - 5, 8, rgb("#c8b8e8"), k)

    bottle_lying(a, 26, 65, 180, 40, DARK_IRON, 0.05, stopper=BRASS, neck=0.4, detail=sigils)
    glow(a, 110, 65, 70, ARCANE, 0.15)
    return a.image()


def bowl_water(seed=4015):
    """A wide green-glass bowl filled with water, the size of a basin."""
    s = 300
    a = art(s, s, seed)
    m = s / 2
    glass = rgb("#6f9a8a")
    soft_shadow(a, (m, m), 128, 6, 8, 0.35, 6)
    a.shape(ellipse(m, m, 128, 128, 72), glass, outline=OUTLINE, depth=10, light_k=0.6)

    def water(art, p):
        for k in range(4):
            art.ink(ellipse(m + 6, m + 4, 20 + 22 * k, 18 + 20 * k, 48), FINE * 1.3, closed=True, color=FOAM, alpha=0.55)

    a.shape(ellipse(m, m, 104, 104, 64), WATER, outline=DETAIL * 1.4, depth=8, shade_k=0.2, light_k=0.5, ao=0.4, detail=water)
    a.ink([(m - 100, m - 40), (m - 70, m - 92)], FINE * 2.4, color=(240, 250, 248), alpha=0.8)
    return a.image()


def brazier_fire(seed=4016):
    """A brass brazier on three legs, filled with a roaring fire."""
    s = 280
    a = art(s, s, seed)
    m = s / 2
    for k in range(3):
        t = -math.pi / 2 + k * 2 * math.pi / 3
        a.shape(ellipse(m + 104 * math.cos(t), m + 104 * math.sin(t), 16, 16, 20), shade(BRASS, 0.2), outline=DETAIL * 1.3, depth=3, mottle=0)
    soft_shadow(a, (m, m), 90, 5, 7, 0.35, 6)
    a.shape(ellipse(m, m, 92, 92, 64), BRASS, outline=OUTLINE, depth=8, light_k=0.55, detail=lambda art, p: [art.ink(ellipse(m, m, 82, 82, 64), FINE * 1.2, closed=True, color=shade(BRASS, 0.4), alpha=0.7)])
    a.shape(ellipse(m, m, 72, 72, 56), rgb("#3a2e28"), outline=DETAIL * 1.3, depth=4, shade_k=0, light_k=0, mottle=0)
    for _ in range(9):
        t = a.rng.uniform(0, 6.28)
        d = a.rng.uniform(0, 50)
        dot(a, m + d * math.cos(t), m + d * math.sin(t), a.rng.uniform(5, 9), rgb("#e9773a"))
    fire(a, m, m, 54, FIRE, glow_r=120)
    return a.image()


def censer_air(seed=4017):
    """A swinging censer on its chain, wisps of incense curling round it."""
    w, h = 300, 260
    a = art(w, h, seed)
    cx, cy = 190, 150
    chain(a, [(40, 40), (90, 80), (140, 110), (cx - 30, cy - 20)], 11, color=shade(SILVER, 0.2))
    for k in range(4):
        r = 50 + k * 18
        t0 = a.rng.uniform(0, 6.28)
        pts = [(cx + r * math.cos(t0 + t), cy + r * 0.8 * math.sin(t0 + t)) for t in [j * 0.12 for j in range(22)]]
        a.ink(pts, 9, color=tint(SMOKE, 0.5), alpha=0.6)
    soft_shadow(a, (cx, cy), 44, 5, 7, 0.35, 5)
    a.shape(ellipse(cx, cy, 44, 44, 48), SILVER, outline=OUTLINE * 0.85, depth=6, light_k=0.55)
    for k in range(8):
        t = 2 * math.pi * k / 8
        a.shape(ellipse(cx + 26 * math.cos(t), cy + 26 * math.sin(t), 5, 5, 12), rgb("#3a3a42"), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    a.shape(ellipse(cx, cy, 12, 12, 20), shade(SILVER, 0.2), outline=DETAIL, depth=2, mottle=0)
    return a.image()


# -- horns and pipes -----------------------------------------------------------------------------


def horn_of_blasting(seed=4021):
    w, h = 290, 160
    a = art(w, h, seed)
    pts = horn_shape(a, 24, 120, 230, 12, 62, rgb("#d8c6a0"), bands=(0.25, 0.55, 0.85), bell=rgb("#7a5a3a"))
    for k, t in enumerate((0.38, 0.7)):
        x, y = pts[int(t * 20)]
        rune(a, x, y, 7, shade(rgb("#d8c6a0"), 0.6), k + 1)
    return a.image()


def horn_of_valhalla(metal, seed=4022):
    def make():
        w, h = 300, 170
        a = art(w, h, seed)
        horn_shape(a, 24, 128, 240, 12, 66, rgb("#e6d6b0"), bands=(0.0, 0.3, 0.6, 1.0), bell=metal, bend=2.6)
        return a.image()

    return make


def pan_pipes(color, seed, tie=ROPE, holes=INK):
    """Pan pipes from above: a row of tubes of decreasing length, bound."""

    def make():
        w, h = 200, 190
        a = art(w, h, seed)
        for k in range(7):
            x = 40 + k * 18
            L = 140 - k * 13
            soft_shadow(a, rect(x, 30, x + 17, 30 + L), dx=4, dy=5, alpha=0.3, blur=4)
            a.shape(rect(x, 30, x + 17, 30 + L), vary(a.rng, color, 0.05), outline=DETAIL * 1.3, corner=7, depth=3, light_k=0.45, mottle=0)
            a.shape(ellipse(x + 8.5, 38, 4.5, 4.5, 12), holes, outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        for y in (62, 96):
            a.ink([(34, y), (172, y)], DETAIL * 2.4, color=INK, taper=False)
            a.ink([(34, y), (172, y)], DETAIL * 1.3, color=tie, taper=False)
        return a.image()

    return make


def chime_of_opening(seed=4024):
    """A hollow metal tube a foot long, with the little striker beside it."""
    w, h = 230, 110
    a = art(w, h, seed)
    loc = lambda pts: rot_pts(pts, 115, 50, -0.12)  # noqa: E731
    soft_shadow(a, loc(rect(30, 36, 200, 64)), dx=4, dy=6, alpha=0.3, blur=4)
    a.shape(loc(rect(30, 36, 200, 64)), SILVER, outline=DETAIL * 2, corner=10, depth=4, light_k=0.6, mottle=0)
    a.shape(loc(ellipse(196, 50, 6, 13, 16)), rgb("#3a3a42"), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0)
    for x in (70, 160):
        a.ink(loc([(x, 37), (x, 63)]), FINE * 1.4, color=shade(SILVER, 0.5), alpha=0.8)
    handle(a, 60, 92, 150, 86, 6, WOOD_DARK)
    a.shape(ellipse(156, 86, 9, 9, 16), SILVER, outline=DETAIL * 1.2, depth=2, mottle=0)
    return a.image()


# -- cards, cubes, stones -------------------------------------------------------------------------


def card(a, x, y, ang, face, back=None, w=24, h=36, mark=None):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(x + dx * c - dy * s, y + dx * s + dy * c) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    soft_shadow(a, pts, dx=2, dy=3, alpha=0.25, blur=2)
    a.shape(pts, face, outline=FINE * 1.5, corner=3, depth=1.5, shade_k=0.2, light_k=0.2, ao=0, mottle=0)
    inner = [(x + dx * c - dy * s, y + dx * s + dy * c) for dx, dy in ((-w / 2 + 4, -h / 2 + 4), (w / 2 - 4, -h / 2 + 4), (w / 2 - 4, h / 2 - 4), (-w / 2 + 4, h / 2 - 4))]
    a.ink(inner, FINE * 0.9, closed=True, color=shade(face, 0.45), alpha=0.7, wob=0.1)
    if mark:
        mark(a, x, y, ang)


def deck_of_many_things(seed=4031):
    """Ivory plaques with arcane emblems, fanned out, some face down."""
    w, h = 280, 200
    a = art(w, h, seed)
    marks = [
        lambda art, x, y, t: sparkle(art, x, y, 9, GOLD),
        lambda art, x, y, t: dot(art, x, y, 7, rgb("#c8443a")),
        lambda art, x, y, t: rune(art, x, y, 7, rgb("#3c5a78"), 1, FINE * 1.4),
        lambda art, x, y, t: art.shape(ellipse(x, y, 8, 5, 16, rot=t), rgb("#2a2a30"), outline=FINE, depth=1, shade_k=0, light_k=0, mottle=0),
        lambda art, x, y, t: rune(art, x, y, 7, rgb("#694a6e"), 3, FINE * 1.4),
        lambda art, x, y, t: art.ink(ellipse(x, y, 7, 7, 16), FINE * 1.6, closed=True, color=GOLD),
    ]
    for k in range(9):
        t = -0.9 + k * 0.22
        x = 140 + 70 * math.sin(t)
        y = 140 - 70 * math.cos(t) + 30
        card(a, x, y, t, IVORY, mark=marks[k % len(marks)], w=34, h=50)
    for k in range(4):  # the rest of the deck in a stack
        card(a, 52 + k * 1.5, 150 - k * 1.5, 0.3, rgb("#5a3a5a"), w=34, h=50)
    rune(a, 58, 145, 8, GOLD, 3, FINE * 1.5)
    return a.image()


def deck_of_illusions(seed=4032):
    """A deck of cards in a leather case, its cards spread like a hand."""
    w, h = 260, 180
    a = art(w, h, seed)
    a.shape(rot_pts(rect(20, 60, 90, 150), 55, 105, -0.2), LEATHER, outline=DETAIL * 1.6, corner=6, depth=4)
    suits = [rgb("#a8483a"), rgb("#2a2a30")]
    for k in range(8):
        t = -0.7 + k * 0.18
        x = 165 + 60 * math.sin(t)
        y = 120 - 60 * math.cos(t) + 24
        col = suits[k % 2]
        card(a, x, y, t, rgb("#f3eee2"), mark=lambda art, x, y, tt, col=col: (art.shape(ellipse(x, y, 6, 8, 12, rot=tt), col, outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0), glow(art, x, y, 14, tint(ARCANE, 0.3), 0.25)), w=28, h=42)
    return a.image()


def cube(a, cx, cy, s, top, side_l, side_r, outline=DETAIL * 1.6):
    """A small cube seen from above at a slight angle: the top face and the
    two near sides foreshortened below it."""
    h = s * 0.32
    a.shape([(cx - s / 2, cy - s / 2 + h), (cx + s / 2, cy - s / 2 + h), (cx + s / 2, cy + s / 2 + h * 0.6), (cx - s / 2, cy + s / 2 + h * 0.6)], side_l, outline=outline, corner=2, depth=2, shade_k=0.2, light_k=0, mottle=0)
    a.shape(rect(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), top, outline=outline, corner=3, depth=3, light_k=0.4, mottle=0)


def cube_of_force(seed=4033, active=False):
    """A tiny glowing cube; active, a shimmering wall of force 15 ft on a side."""
    if active:
        s = 3 * 256 + 40
        a = art(s, s, seed)
        m = s / 2
        R = 384
        field = rect(m - R, m - R, m + R, m + R)
        a.fill_path(to_path(field), rgb("#9ad0f0"), 0.3)
        with a.clip(to_path(field)):
            for k in range(-12, 13):
                a.ink([(m - R + k * 64, m - R), (m + k * 64 + R, m + R)], FINE * 1.6, color=rgb("#f2fbff"), alpha=0.55)
            a.stroke_path(to_path(field), rgb("#5fa0d8"), 40, 0.35, blur=12)
        a.ink(field, DETAIL * 3, closed=True, color=rgb("#4f8fd0"), alpha=0.95)
        a.ink(field, DETAIL * 0.8, closed=True, color=rgb("#e6f6ff"), alpha=0.9)
        glow(a, m, m, 40, rgb("#9ad0f0"), 0.5)
        cube(a, m, m, 26, rgb("#c8e8f6"), rgb("#7aa8c8"), rgb("#7aa8c8"), outline=DETAIL * 1.2)
        return a.image()
    s = 110
    a = art(s, s, seed)
    glow(a, s / 2, s / 2, 50, rgb("#9ad0f0"), 0.5)
    soft_shadow(a, (s / 2, s / 2 + 6), 22, 3, 4, 0.3, 3)
    cube(a, s / 2, s / 2 - 4, 46, rgb("#c8e8f6"), rgb("#7aa8c8"), rgb("#7aa8c8"))
    a.ink(rect(s / 2 - 14, s / 2 - 18, s / 2 + 14, s / 2 + 10), FINE * 1.3, closed=True, color=rgb("#4f8fd0"), alpha=0.8)
    sparkle(a, s / 2 - 12, s / 2 - 16, 6)
    return a.image()


def cubic_gate(seed=4034):
    """A three-inch cube, each face etched with a different sigil."""
    s = 130
    a = art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m + 8), 30, 3, 5, 0.35, 4)
    cube(a, m, m - 6, 66, rgb("#8a8478"), rgb("#6a645a"), rgb("#6a645a"))
    a.ink(ellipse(m, m - 6, 22, 22, 32), FINE * 1.6, closed=True, color=ARCANE, alpha=0.9)
    rune(a, m, m - 6, 12, ARCANE, 3, FINE * 1.6)
    for k in range(2):
        rune(a, m - 16 + k * 32, m + 33, 6, tint(ARCANE, 0.3), k, FINE * 1.1)
    glow(a, m, m - 6, 30, ARCANE, 0.2)
    return a.image()


def instant_fortress(seed=4035):
    """The adamantine cube, an inch on a side, before it's spoken to."""
    s = 110
    a = art(s, s, seed)
    soft_shadow(a, (s / 2, s / 2 + 6), 22, 3, 4, 0.3, 3)
    ad = rgb("#5a6470")
    cube(a, s / 2, s / 2 - 4, 46, ad, shade(ad, 0.3), shade(ad, 0.3))
    for k in range(4):
        x = s / 2 - 18 + k * 12
        a.shape(rect(x, s / 2 - 27, x + 7, s / 2 - 21), tint(ad, 0.3), outline=FINE, corner=1, depth=1, shade_k=0, light_k=0, mottle=0)
    return a.image()


def instant_fortress_deployed(seed=4036):
    """The fortress unfolded: a square stone tower 20 ft on a side (seen
    from above: its battlemented roof, the four corner turrets, the trapdoor
    to the stairs)."""
    T = 256
    s = 4 * T + 120
    a = art(s, s, seed)
    m = s / 2
    R = 2 * T
    ad = rgb("#6a707a")
    soft_shadow(a, rect(m - R, m - R, m + R, m + R), dx=14, dy=18, alpha=0.4, blur=14)
    a.shape(rect(m - R, m - R, m + R, m + R), ad, outline=OUTLINE * 1.3, corner=6, depth=14, light_k=0.3)
    inner = rect(m - R + 44, m - R + 44, m + R - 44, m + R - 44)

    def flags(art, p):
        for k in range(1, 8):
            x = m - R + 44 + k * (2 * R - 88) / 8
            art.ink([(x, m - R + 44), (x, m + R - 44)], FINE * 1.3, color=shade(ad, 0.45), alpha=0.6, taper=False)
        for k in range(1, 8):
            y = m - R + 44 + k * (2 * R - 88) / 8
            art.ink([(m - R + 44, y), (m + R - 44, y)], FINE * 1.3, color=shade(ad, 0.45), alpha=0.6, taper=False)

    a.shape(inner, tint(ad, 0.12), outline=DETAIL * 2, corner=2, depth=10, shade_k=0.3, light_k=0, ao=0.5, detail=flags)
    # Merlons all around the parapet.
    n = 9
    for side in range(4):
        for k in range(n):
            t = (k + 0.5) / n
            L = 2 * R
            if side == 0:
                x, y = m - R + L * t, m - R + 22
            elif side == 1:
                x, y = m + R - 22, m - R + L * t
            elif side == 2:
                x, y = m - R + L * t, m + R - 22
            else:
                x, y = m - R + 22, m - R + L * t
            if k % 2 == 0:
                a.shape(rect(x - 26, y - 18, x + 26, y + 18) if side % 2 == 0 else rect(x - 18, y - 26, x + 18, y + 26), tint(ad, 0.2), outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.4, mottle=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = m + sx * (R - 40), m + sy * (R - 40)
            a.shape(rect(cx - 56, cy - 56, cx + 56, cy + 56), shade(ad, 0.08), outline=DETAIL * 2, corner=4, depth=8, light_k=0.4)
            a.ink(rect(cx - 40, cy - 40, cx + 40, cy + 40), FINE * 1.4, closed=True, color=shade(ad, 0.45), alpha=0.7)
    board(a, m - 60, m - 60, m + 60, m + 60, WOOD_DARK, n=4, corner=4)
    a.shape(ellipse(m + 40, m, 8, 8, 16), IRON, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def iron_bands(seed=4037):
    """A rusty iron sphere, its bands seamed all round it."""
    s = 130
    a = art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), 40, 4, 5, 0.35, 4)

    def bands(art, p):
        for k in range(-2, 3):
            art.ink(ellipse(m + k * 15, m, 40 - abs(k) * 8, 42, 36), DETAIL * 1.1, closed=False, color=shade(RUST, 0.5), alpha=0.85)
        for _ in range(8):
            dot(art, m + art.rng.uniform(-30, 30), m + art.rng.uniform(-30, 30), art.rng.uniform(2, 5), rgb("#b8703e"), 0.7)

    a.shape(ellipse(m, m, 42, 42, 48), mix(DARK_IRON, RUST, 0.4), outline=OUTLINE * 0.8, depth=7, light_k=0.45, detail=bands)
    return a.image()


# -- floor-sized items ----------------------------------------------------------------------------


def carpet(seed=4041, w_ft=4, h_ft=6, field=RED, border=rgb("#3c5a78"), trim=GOLD):
    """A flying carpet: a rug with a rich border, medallion and tassels,
    floating a hand above the floor (a bigger, softer shadow)."""
    k = 256 / 5
    W, H = w_ft * k, h_ft * k
    a = art(W + 70, H + 90, seed)
    x0, y0 = 30, 30
    x1, y1 = x0 + W, y0 + H
    soft_shadow(a, rect(x0, y0, x1, y1), dx=18, dy=26, alpha=0.3, blur=14)
    for x in [x0 + 8 + j * (W - 16) / 11 for j in range(12)]:
        for yy, d in ((y0, -1), (y1, 1)):
            a.ink([(x, yy), (x + a.rng.uniform(-2, 2), yy + d * 16)], 4, color=trim, alpha=0.95)

    def pattern(art, p):
        art.shape(rect(x0 + 14, y0 + 14, x1 - 14, y1 - 14), field, outline=DETAIL * 1.2, corner=2, depth=4, shade_k=0.2, light_k=0, ao=0, mottle=0.05)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        med = [(cx, cy - H * 0.26), (cx + W * 0.26, cy), (cx, cy + H * 0.26), (cx - W * 0.26, cy)]
        art.shape(med, border, outline=DETAIL * 1.2, corner=4, depth=3, shade_k=0, light_k=0, ao=0, mottle=0)
        art.shape(ellipse(cx, cy, W * 0.09, W * 0.09, 24), trim, outline=FINE * 1.3, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                art.shape([(cx + sx * W * 0.32, cy + sy * H * 0.36), (cx + sx * W * 0.4, cy + sy * H * 0.28), (cx + sx * W * 0.4, cy + sy * H * 0.42)], border, outline=FINE * 1.2, corner=2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        art.ink(rect(x0 + 24, y0 + 24, x1 - 24, y1 - 24), FINE * 1.3, closed=True, color=trim, alpha=0.9)

    a.shape(rect(x0, y0, x1, y1), border, outline=OUTLINE, corner=3, depth=6, light_k=0.3, detail=pattern)
    return a.image()


def portable_hole(seed=4042, folded=False):
    """Spread out: a 6-ft circle of pure darkness, an extradimensional hole.
    Folded: a square of fine black cloth."""
    if folded:
        s = 140
        a = art(s, s, seed)
        cl = rgb("#2e2a34")
        pts = rot_pts(rect(30, 34, 110, 104), 70, 69, 0.2)
        soft_shadow(a, pts, dx=4, dy=6, alpha=0.35, blur=4)
        a.shape(pts, cl, outline=DETAIL * 1.6, corner=6, depth=5, light_k=0.4, detail=lambda art, p: art.ink(rot_pts([(30, 69), (110, 69)], 70, 69, 0.2), FINE * 1.4, color=tint(cl, 0.3), alpha=0.8))
        return a.image()
    R = 6 * 256 / 5 / 2
    s = int(2 * R + 60)
    a = art(s, s, seed)
    m = s / 2
    hole = blob(m, m, R, a.rng, 20, 0.02)
    p = a.shape(hole, VOID, outline=OUTLINE, smooth=True, depth=30, shade_k=0, light_k=0, ao=0.9, mottle=0)
    with a.clip(p):
        for k in range(5):
            a.ink(ellipse(m, m, R * (0.9 - k * 0.17), R * (0.9 - k * 0.17), 64), DETAIL, closed=True, color=rgb("#2c2438"), alpha=0.6 - k * 0.1)
    a.ink(ellipse(m - 4, m - 4, R - 4, R - 4, 72), FINE * 1.4, closed=True, color=rgb("#5a4a6e"), alpha=0.6)
    return a.image()


def well_of_many_worlds(seed=4043, folded=False):
    """Fine black cloth that opens a 6-ft circular portal: another world
    seen through it (a starry, swirling sky)."""
    if folded:
        s = 150
        a = art(s, s, seed)
        cl = rgb("#24202c")
        pts = rot_pts(rect(28, 36, 122, 112), 75, 74, -0.15)
        soft_shadow(a, pts, dx=4, dy=6, alpha=0.35, blur=4)

        def stars(art, p):
            for _ in range(10):
                dot(art, art.rng.uniform(35, 115), art.rng.uniform(40, 108), art.rng.uniform(1, 2.2), rgb("#d8d0f0"), 0.8)
            art.ink(rot_pts([(28, 74), (122, 74)], 75, 74, -0.15), FINE * 1.4, color=tint(cl, 0.3), alpha=0.8)

        a.shape(pts, cl, outline=DETAIL * 1.6, corner=6, depth=5, light_k=0.4, detail=stars)
        return a.image()
    R = 6 * 256 / 5 / 2
    s = int(2 * R + 70)
    a = art(s, s, seed)
    m = s / 2
    sky = rgb("#2a2a5a")

    def world(art, p):
        for k in range(6):
            r = R * (1 - k * 0.15)
            art.fill_path(to_path(ellipse(m + k * 4, m - k * 3, r, r, 64)), mix(sky, rgb("#6a4ab0"), k / 6), 0.8)
        for k in range(3):
            pts = [(m + (20 + t * 28) * math.cos(t + k * 2.1), m + (20 + t * 28) * math.sin(t + k * 2.1)) for t in [j * 0.15 for j in range(40)]]
            art.ink(pts, 10, color=rgb("#b8a0f0"), alpha=0.35)
        for _ in range(60):
            dot(art, m + art.rng.uniform(-R, R), m + art.rng.uniform(-R, R), art.rng.uniform(1, 3), rgb("#f2eeff"), 0.9)
        for _ in range(5):
            sparkle(art, m + art.rng.uniform(-R * 0.7, R * 0.7), m + art.rng.uniform(-R * 0.7, R * 0.7), art.rng.uniform(5, 9))

    glow(a, m, m, R * 1.2, rgb("#8a6ad8"), 0.35)
    a.shape(ellipse(m, m, R, R, 96), sky, outline=OUTLINE, depth=20, shade_k=0.4, light_k=0, ao=0.6, detail=world)
    a.ink(ellipse(m, m, R + 6, R + 6, 96), DETAIL, closed=True, color=rgb("#b8a0f0"), alpha=0.6)
    return a.image()


def sphere_of_annihilation(seed=4044):
    """A 2-ft sphere of blackness hovering, the floor around it scoured
    and pulled toward it."""
    s = 260
    a = art(s, s, seed)
    m = s / 2
    r = 2 * 256 / 5 / 2
    for k in range(20):
        t = 2 * math.pi * k / 20 + a.rng.uniform(-0.1, 0.1)
        r0, r1 = r * 2.4, r * 1.2
        pts = [(m + (r0 - (r0 - r1) * u) * math.cos(t + u * 0.6), m + (r0 - (r0 - r1) * u) * math.sin(t + u * 0.6)) for u in [j / 8 for j in range(9)]]
        a.ink(pts, FINE * 1.6, color=rgb("#4a3a5a"), alpha=0.5)
    glow(a, m, m, r * 2.2, rgb("#3a2a4a"), 0.45)
    a.shape(ellipse(m, m, r, r, 64), VOID, outline=OUTLINE, depth=10, shade_k=0, light_k=0, ao=0.5, mottle=0)
    a.ink(ellipse(m, m, r - 6, r - 6, 64), FINE * 1.4, closed=True, color=rgb("#6a5a8a"), alpha=0.5)
    return a.image()


def folding_boat(seed=4045, form="box"):
    """A wooden box 12 x 6 x 6 in; unfolded, a 10-ft rowboat with oars, or a
    24-ft ship with a deck, rowing seats and a mast."""
    if form == "box":
        w, h = 170, 110
        a = art(w, h, seed)
        soft_shadow(a, rect(20, 20, 150, 86), dx=5, dy=6, alpha=0.35, blur=5)
        board(a, 20, 20, 150, 86, WOOD, n=2, corner=5)
        a.ink(rect(28, 28, 142, 78), FINE * 1.2, closed=True, color=shade(WOOD, 0.5), alpha=0.7)
        for k, x in enumerate((60, 85, 110)):
            rune(a, x, 53, 8, shade(WOOD, 0.6), k + 2, FINE * 1.3)
        return a.image()
    k = 256 / 5
    if form == "boat":
        from obj_farm import boat

        return boat(10 * k, 4 * k, WOOD_LIGHT, seats=2, oars=True)(seed)
    L, W = 24 * k, 8 * k
    a = art(W + 260, L + 80, seed)
    cx, cy = (W + 260) / 2, (L + 80) / 2
    outer = hull(cx, cy, L, W, bow=0.3, stern=0.12)
    soft_shadow(a, outer, dx=8, dy=10, alpha=0.3, blur=10)
    for j in range(5):  # oars, five a side
        y = cy - L * 0.28 + j * L * 0.13
        for side in (-1, 1):
            handle(a, cx + side * W * 0.3, y, cx + side * (W / 2 + 110), y + 30, 9, WOOD_LIGHT)
            a.shape(ellipse(cx + side * (W / 2 + 116), y + 33, 12, 26, 20, rot=side * -0.5), WOOD_LIGHT, outline=DETAIL * 1.3, depth=2, mottle=0)
    a.shape(outer, WOOD, outline=OUTLINE, corner=0, wob=0.4, depth=10, light_k=0.4)
    inner = [(cx + (x - cx) * 0.86, cy + (y - cy) * 0.94) for x, y in outer]
    a.shape(inner, WOOD_LIGHT, outline=DETAIL * 1.3, corner=0, wob=0.3, depth=8, shade_k=0.3, light_k=0, ao=0.4, detail=lambda art, p: boards(art, cx - W / 2, cy - L / 2, cx + W / 2, cy + L / 2, WOOD_LIGHT, 7, vertical=True))
    for j in range(5):
        y = cy - L * 0.28 + j * L * 0.13
        a.shape(rect(cx - W * 0.38, y - 12, cx + W * 0.38, y + 12), WOOD, outline=DETAIL * 1.2, corner=3, depth=3)
    board(a, cx - W * 0.36, cy + L * 0.3, cx + W * 0.36, cy + L * 0.42, WOOD_DARK, n=3, corner=4)  # stern deck
    a.shape(ellipse(cx, cy - L * 0.1, 16, 16, 24), WOOD_DARK, outline=DETAIL * 1.4, depth=3, mottle=0)  # mast
    a.shape(rect(cx - W * 0.42, cy - L * 0.1 - 8, cx + W * 0.42, cy - L * 0.1 + 8), WOOD_DARK, outline=DETAIL * 1.2, corner=4, depth=2, mottle=0)  # yard
    return a.image()


# -- figurines -----------------------------------------------------------------------------------


def statue_tone(img, color, k=0.85):
    """Recast a drawing as carved/cast material: its luminance kept, its
    hue replaced by `color` (ink lines stay dark)."""
    import numpy as np
    from PIL import Image

    arr = np.asarray(img).astype(np.float32)
    lum = (arr[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)) / 255
    c = np.array(color, np.float32)
    lo, hi = c * 0.35, c + (np.array([255, 248, 232], np.float32) - c) * 0.45
    t = np.clip((lum - 0.12) / 0.8, 0, 1)[..., None]
    out = lo + (hi - lo) * t
    arr[..., :3] = arr[..., :3] * (1 - k) + out * k
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def rect_plinth(a, x0, y0, x1, y1, color):
    soft_shadow(a, rect(x0, y0, x1, y1), dx=4, dy=6, alpha=0.35, blur=5)
    a.shape(rect(x0, y0, x1, y1), color, outline=DETAIL * 1.6, corner=10, depth=5, light_k=0.4)
    a.ink(rect(x0 + 8, y0 + 8, x1 - 8, y1 - 8), FINE, closed=True, color=shade(color, 0.4), alpha=0.6)


def on_plinth(fig, material, base, seed, pad=10):
    """`fig` (a drawing in neutral greys) cast in `material` and set on a
    plinth just larger than its footprint."""
    fig = statue_tone(fig.convert("RGBA"), material)
    w, h = fig.width + 2 * pad + 10, fig.height + 2 * pad + 10
    a = art(w, h, seed)
    rect_plinth(a, 5, 5, w - 5, h - 5, base)
    img = a.image()
    img.alpha_composite(fig, (pad + 5, pad + 5))
    return img


def figurine_beast(kind, L, material, base, seed, lion=False, **kw):
    def make():
        b = beast(kind, L, rgb("#b8b0a4"), **kw)(seed + 1).convert("RGBA")
        if lion:
            # A shaggy mane ringing the head, under it.
            import numpy as np

            al = np.asarray(b)[..., 3]
            rows = np.where(al.max(axis=1) > 0)[0]
            top = rows[0]
            hy = top + b.height * 0.1
            m = art(b.width + 40, b.height + 40, seed + 2)
            m.shape(scallop(b.width / 2 + 20, hy + 20, b.width * 0.36, m.rng, 11, 0.25), rgb("#8a8278"), outline=DETAIL * 1.3, depth=3, light_k=0.3, detail=lambda art, p: [art.ink([(b.width / 2 + 20 + 12 * math.cos(t), hy + 20 + 12 * math.sin(t)), (b.width / 2 + 20 + b.width * 0.32 * math.cos(t), hy + 20 + b.width * 0.32 * math.sin(t))], FINE, color=INK, alpha=0.4) for t in [k * 0.5 for k in range(13)]])
            mi = m.image(grain=0)
            mi.alpha_composite(b, (20, 20))
            b = autocrop(mi, 2)
        return on_plinth(b, material, base, seed)

    return make


def elephant_fig(seed=4105):
    """A small elephant from above: broad back, great fanned ears, the trunk
    curling forward between two tusks."""
    w, h = 130, 170
    a = art(w, h, seed)
    g = rgb("#b8b0a4")
    cx = w / 2
    a.ink([(cx, 150), (cx + 6, 166)], 6, color=INK)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.shape(ellipse(cx + sx * 34, 95 + sy * 34, 12, 12, 16), shade(g, 0.1), outline=DETAIL, depth=2, mottle=0)
    a.shape(ellipse(cx, 100, 44, 56, 40), g, outline=DETAIL * 1.6, depth=5, light_k=0.4, detail=lambda art, p: art.ink([(cx, 60), (cx, 150)], FINE, color=INK, alpha=0.35))
    for side in (-1, 1):
        ear = chaikin([(cx + side * 10, 30), (cx + side * 56, 18), (cx + side * 62, 52), (cx + side * 40, 72), (cx + side * 14, 58)], True, 2)
        a.shape(ear, tint(g, 0.08), outline=DETAIL * 1.4, corner=0, depth=3, light_k=0.3)
    a.shape(ellipse(cx, 40, 24, 24, 28), g, outline=DETAIL * 1.5, depth=3, light_k=0.4)
    for side in (-1, 1):
        a.ink([(cx + side * 8, 28), (cx + side * 12, 8)], 6, color=INK, taper=True)
        a.ink([(cx + side * 8, 28), (cx + side * 12, 8)], 3, color=rgb("#f2eee6"), taper=True)
    trunk = [(cx, 30), (cx + 2, 16), (cx - 4, 6), (cx - 12, 4)]
    a.ink(chaikin(trunk, False, 2), 14, color=INK, taper=False)
    a.ink(chaikin(trunk, False, 2), 9, color=g, taper=False)
    for side in (-1, 1):
        dot(a, cx + side * 10, 40, 2.5, INK)
    return a.image(grain=0)


def figurine_bird(material, base, seed, size=150, griffon=False, owl=False):
    def make():
        s = size
        a = art(s, s, seed)
        plinth(a, s / 2, s / 2, s * 0.42, base)
        img = a.image()
        b = art(s, s, seed + 1)
        if griffon:
            # Eagle head and wings over a lion's body.
            b.shape(ellipse(s / 2, s / 2 + 18, 18, 30, 28), rgb("#b8b0a4"), outline=DETAIL * 1.3, depth=3)
            b.ink([(s / 2, s / 2 + 44), (s / 2 + 10, s / 2 + 60), (s / 2 + 18, s / 2 + 58)], 5, color=INK)
            for side in (-1, 1):
                pts = chaikin([(s / 2 + side * 8, s / 2 - 6), (s / 2 + side * 56, s / 2 - 22), (s / 2 + side * 44, s / 2 + 4), (s / 2 + side * 14, s / 2 + 20)], True, 2)
                b.shape(pts, rgb("#c8c0b4"), outline=DETAIL * 1.3, corner=0, depth=2, light_k=0.3, mottle=0, detail=lambda art, p, side=side: [art.ink([(s / 2 + side * (18 + 9 * k), s / 2 - 8), (s / 2 + side * (16 + 9 * k), s / 2 + 12)], FINE, color=INK, alpha=0.5) for k in range(4)])
            b.shape(ellipse(s / 2, s / 2 - 26, 13, 14, 24), rgb("#c8c0b4"), outline=DETAIL * 1.3, depth=2, mottle=0)
            b.shape([(s / 2 - 5, s / 2 - 38), (s / 2 + 5, s / 2 - 38), (s / 2, s / 2 - 50)], rgb("#a8a094"), outline=FINE * 1.3, corner=1, depth=1, mottle=0)
        elif owl:
            b.shape(ellipse(s / 2, s / 2, 30, 36, 32), rgb("#b8b0a4"), outline=DETAIL * 1.4, depth=4, light_k=0.4)
            for side in (-1, 1):
                b.shape(ellipse(s / 2 + side * 12, s / 2 - 12, 10, 10, 20), rgb("#d8d0c4"), outline=FINE * 1.3, depth=1, mottle=0)
                dot(b, s / 2 + side * 12, s / 2 - 12, 4, INK)
                b.shape([(s / 2 + side * 16, s / 2 - 30), (s / 2 + side * 26, s / 2 - 44), (s / 2 + side * 26, s / 2 - 26)], rgb("#b8b0a4"), outline=FINE * 1.3, corner=1, depth=1, mottle=0)
            b.shape([(s / 2 - 4, s / 2 - 4), (s / 2 + 4, s / 2 - 4), (s / 2, s / 2 + 6)], rgb("#8a8478"), outline=FINE, corner=1, depth=1, mottle=0)
        else:
            bird(b, s / 2, s / 2, s * 0.62, rgb("#b8b0a4"), rgb("#a8a094"), beak=rgb("#8a8478"))
        img.alpha_composite(statue_tone(b.image(grain=0), material))
        return img

    return make


def figurine_fly(seed=4057):
    """An ebony fly, as big as a fist, wings spread."""
    s = 140
    a = art(s, s, seed)
    plinth(a, s / 2, s / 2, s * 0.42, rgb("#6a5a50"))
    m = s / 2
    for side in (-1, 1):
        a.shape(ellipse(m + side * 22, m - 4, 22, 11, 24, rot=side * -0.5), rgb("#8a8090"), outline=DETAIL * 1.2, depth=2, light_k=0.5, mottle=0, detail=lambda art, p, side=side: art.ink([(m + side * 6, m - 4), (m + side * 38, m - 14)], FINE, color=INK, alpha=0.5))
        for k in range(3):
            a.ink([(m, m + k * 6), (m + side * 22, m + k * 10 - 2), (m + side * 30, m + k * 14 + 6)], FINE * 1.4, color=EBONY)
    a.shape(ellipse(m, m + 10, 10, 22, 24), EBONY, outline=DETAIL * 1.3, depth=3, light_k=0.5)
    a.shape(ellipse(m, m - 16, 11, 9, 20), EBONY, outline=DETAIL * 1.3, depth=2, light_k=0.5, mottle=0)
    for side in (-1, 1):
        dot(a, m + side * 6, m - 18, 4, rgb("#7a2a2a"))
    return a.image()


# -- light and misc -------------------------------------------------------------------------------


def lantern_of_revealing(seed=4061):
    """A hooded lantern whose light has a pale violet cast that shows the
    invisible."""
    s = 180
    a = art(s, s, seed)
    m = s / 2
    glow(a, m, m, 86, rgb("#c8b0f0"), 0.45)
    a.shape(ellipse(m, m, 44, 44, 40), shade(BRASS, 0.1), outline=OUTLINE * 0.8, depth=6, light_k=0.5)
    a.shape(ellipse(m, m, 32, 32, 36), rgb("#e8dcff"), outline=DETAIL * 1.2, depth=3, shade_k=0, light_k=0.3, mottle=0)
    for k in range(6):
        t = 2 * math.pi * k / 6
        a.ink([(m + 12 * math.cos(t), m + 12 * math.sin(t)), (m + 32 * math.cos(t), m + 32 * math.sin(t))], DETAIL * 1.2, color=shade(BRASS, 0.2), taper=False)
    a.shape(ellipse(m, m, 14, 14, 24), shade(BRASS, 0.1), outline=DETAIL, depth=2, mottle=0)
    a.ink(ellipse(m, m - 46, 18, 12, 24), DETAIL * 1.6, closed=False, color=INK)
    return a.image()


def candle_of_invocation(seed=4062):
    """A slender taper on a small dish, its flame burning with a pale holy
    light."""
    s = 140
    a = art(s, s, seed)
    m = s / 2
    glow(a, m, m, 64, rgb("#fff0b0"), 0.55)
    a.shape(ellipse(m, m, 40, 40, 40), SILVER, outline=DETAIL * 1.5, depth=4, light_k=0.5)
    a.ink(ellipse(m, m, 30, 30, 40), FINE * 1.2, closed=True, color=shade(SILVER, 0.4), alpha=0.7)
    a.shape(ellipse(m, m, 15, 15, 28), rgb("#f6f0dc"), outline=DETAIL * 1.4, depth=3, light_k=0.4)
    for k in range(3):
        t = 0.6 + k * 0.6
        a.ink([(m + 14 * math.cos(t), m + 14 * math.sin(t)), (m + 18 * math.cos(t), m + 22 * math.sin(t))], 4, color=rgb("#f6f0dc"))
    a.shape(scallop(m, m, 10, a.rng, 5, 0.25), rgb("#f6b444"), outline=FINE * 1.2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    a.shape(scallop(m, m, 5.5, a.rng, 5, 0.25), rgb("#fff4cf"), outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
    return a.image()


def mirror_of_life_trapping(seed=4063):
    """A 4-ft ornate mirror, pale ghostly faces trapped behind the glass."""
    k = 256 / 5
    w, h = int(2 * k + 60), int(4 * k + 60)
    a = art(w, h, seed)
    x0, y0, x1, y1 = 30, 30, w - 30, h - 30
    soft_shadow(a, rect(x0, y0, x1, y1), dx=8, dy=10, alpha=0.35, blur=8)
    a.shape(rect(x0, y0, x1, y1), GOLD, outline=OUTLINE, corner=40, depth=8, light_k=0.5, detail=lambda art, p: [dot(art, x, y, 4, tint(GOLD, 0.4)) for x, y in ((x0 + 16, (y0 + y1) / 2), (x1 - 16, (y0 + y1) / 2), ((x0 + x1) / 2, y0 + 14), ((x0 + x1) / 2, y1 - 14))])
    glass = rect(x0 + 22, y0 + 22, x1 - 22, y1 - 22)

    def faces(art, p):
        cx = (x0 + x1) / 2
        for j, (fx, fy) in enumerate(((cx - 16, y0 + 70), (cx + 14, y0 + 130), (cx - 8, y1 - 70))):
            art.fill_path(to_path(ellipse(fx, fy, 15, 19, 24)), rgb("#f2f8fa"), 0.6, blur=3)
            for side in (-1, 1):
                dot(art, fx + side * 5, fy - 3, 2.6, rgb("#2a3a4a"), 0.75)
            art.ink(ellipse(fx, fy + 8, 3, 4, 12), 1.8, closed=True, color=rgb("#2a3a4a"), alpha=0.7)
        art.ink([(x0 + 34, y0 + 60), (x0 + 60, y0 + 34)], FINE * 2.4, color=(250, 252, 255), alpha=0.8)

    a.shape(glass, rgb("#9ab0bc"), outline=DETAIL * 1.6, corner=28, depth=6, shade_k=0.3, light_k=0.4, detail=faces)
    return a.image()


def dimensional_shackles(seed=4064):
    """Manacles with runes worked into the cuffs, a faint violet sheen."""
    w, h = 230, 140
    a = art(w, h, seed)
    glow(a, 115, 70, 90, ARCANE, 0.2)
    chain(a, [(64, 70), (115, 86), (166, 70)], 12)
    for x in (44, 186):
        soft_shadow(a, (x, 68), 26, 3, 4, 0.3, 3)
        a.shape(ellipse(x, 68, 26, 26, 36), DARK_IRON, outline=DETAIL * 1.6, depth=4, light_k=0.5)
        a.shape(ellipse(x, 68, 14, 14, 28), rgb("#e8dfc8"), outline=DETAIL * 1.2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
        for j in range(4):
            t = j * math.pi / 2 + 0.4
            rune(a, x + 20 * math.cos(t), 68 + 20 * math.sin(t), 3.5, rgb("#c8b0f0"), j, FINE * 0.9)
    return a.image()


def efficient_quiver(seed=4065):
    """A long quiver with three compartments: arrows, javelins and staves."""
    w, h = 210, 380
    a = art(w, h, seed)
    leather = rgb("#7a4e32")
    soft_shadow(a, rect(40, 70, w - 40, h - 20), dx=5, dy=7, alpha=0.3, blur=5)
    # Contents poking out of the mouths.
    for k in range(5):
        x = 58 + k * 9
        a.ink([(x, 100), (x + a.rng.uniform(-5, 5), 30)], 5, color=INK, taper=False)
        a.ink([(x, 100), (x + a.rng.uniform(-5, 5), 30)], 2.5, color=WOOD_LIGHT, taper=False)
        a.shape([(x - 6, 22), (x + 6, 22), (x + 7, 44), (x - 7, 44)], rgb("#e6dcc4"), outline=FINE * 1.2, corner=1, depth=1, mottle=0)
    for k in range(2):
        x = 118 + k * 14
        handle(a, x, 100, x + 2, 14, 6, WOOD)
        a.shape([(x - 5, 22), (x + 7, 22), (x + 1, 2)], IRON, outline=FINE * 1.4, corner=0, depth=1, mottle=0)
    handle(a, 160, 100, 166, 8, 9, WOOD_DARK)
    a.shape(rect(36, 70, w - 36, h - 20), leather, corner=26, depth=8, light_k=0.35, detail=lambda art, p: [art.ink([(40, y), (w - 40, y)], FINE * 1.2, color=shade(leather, 0.45), alpha=0.8) for y in (150, h - 60)])
    for x0, x1 in ((40, 100), (104, 146), (150, w - 40)):
        a.shape(rect(x0, 72, x1, 100), shade(leather, 0.45), outline=DETAIL * 1.3, corner=8, depth=3, shade_k=0, light_k=0, mottle=0)
    rune(a, w / 2, 230, 14, GOLD, 4, FINE * 1.5)
    return a.image()


def feather_token(color, seed, mark=None):
    """A single feather lying flat, a tiny tag tied to its quill (the tag's
    color tells the tokens apart)."""

    def make():
        w, h = 220, 100
        a = art(w, h, seed)
        x0, x1, y = 34, 200, 52
        spine = [(x0 + (x1 - x0) * t, y - 10 * math.sin(t * 2.6)) for t in [k / 16 for k in range(17)]]

        def half(sign):
            out = []
            for k, (x, yy) in enumerate(spine):
                t = k / 16
                wv = 0 if t < 0.18 else 24 * math.sin(math.pi * min(1.0, (t - 0.18) / 0.86)) ** 0.7
                out.append((x + sign * 2, yy + sign * wv * (1.0 if sign > 0 else 0.85)))
            return out

        vane = half(-1) + half(1)[::-1]
        soft_shadow(a, vane, dx=3, dy=5, alpha=0.25, blur=4)

        def barbs(art, p):
            for k in range(4, 16):
                x, yy = spine[k]
                for sgn in (-1, 1):
                    art.ink([(x, yy), (x + 10, yy + sgn * 22)], FINE * 0.9, color=shade(color, 0.35), alpha=0.55)
            # A notch where the vane has split, as real feathers do.
            nx, ny = spine[9]
            art.ink([(nx + 4, ny - 4), (nx + 14, ny - 26)], FINE * 1.6, color=(240, 236, 226), alpha=0.9)

        a.shape(chaikin(vane, True, 2), color, outline=DETAIL * 1.3, corner=0, depth=3, light_k=0.45, detail=barbs)
        a.ink(spine[2:], 3.4, color=tint(color, 0.6), taper=True)
        a.ink([(12, 60), (spine[3][0], spine[3][1])], 4.5, color=IVORY, taper=False)
        if mark:
            a.ink([(26, 56), (30, 72)], 1.8, color=INK, alpha=0.8)
            a.shape(rect(22, 70, 38, 86), mark, outline=FINE * 1.3, corner=2, depth=1, shade_k=0.2, light_k=0.2, ao=0, mottle=0)
        return a.image()

    return make


def horseshoes(metal, seed, wind=False, sparks=False):
    """A set of four horseshoes laid out."""

    def make():
        s = 230
        a = art(s, s, seed)
        if wind:
            for k in range(3):
                pts = [(30 + 170 * t, 60 + k * 55 + 10 * math.sin(t * 8)) for t in [j / 20 for j in range(21)]]
                a.ink(pts, 3, color=rgb("#cfe6f0"), alpha=0.8)
        for (x, y, t) in ((70, 70, -0.3), (160, 70, 0.3), (70, 160, -0.2), (160, 160, 0.4)):
            pts = []
            for k in range(25):
                u = math.pi * 0.15 + k * math.pi * 1.7 / 24
                pts.append((x + 34 * math.cos(u + t + math.pi / 2), y + 36 * math.sin(u + t + math.pi / 2)))
            soft_shadow(a, tube(pts, 15, 15), dx=3, dy=4, alpha=0.3, blur=3)
            a.shape(tube(pts, 15, 15), metal, outline=DETAIL * 1.4, corner=0, depth=2, light_k=0.5, mottle=0)
            for k in (4, 8, 16, 20):
                dot(a, pts[k][0], pts[k][1], 2.2, shade(metal, 0.6))
            if sparks:
                for k in (2, 22):
                    sparkle(a, pts[k][0], pts[k][1], 7, rgb("#fff0b0"))
        return a.image()

    return make


def rope_coil(color, seed, tendrils=False):
    def make():
        s = 200
        a = art(s, s, seed)
        m = s / 2
        sp = [(m + (16 + 4.6 * t) * math.cos(t * 1.1), m + (16 + 4.6 * t) * math.sin(t * 1.1)) for t in [k * 0.12 for k in range(130)]]
        a.ink(sp, 15, color=INK, taper=False)
        a.ink(sp, 10, color=color, taper=False)
        for i in range(0, len(sp) - 1, 3):
            (x0, y0), (x1, y1) = sp[i], sp[i + 1]
            a.ink([(x0, y0), (x1, y1)], FINE, color=shade(color, 0.5), alpha=0.6)
        end = sp[-1]
        if tendrils:
            for k in range(3):
                t0 = a.rng.uniform(0, 6.28)
                pts = [(end[0] + 6 * j * math.cos(t0 + j * 0.3), end[1] + 6 * j * math.sin(t0 + j * 0.3)) for j in range(8)]
                pts = [(min(s - 8, max(8, x)), min(s - 8, max(8, y))) for x, y in pts]
                a.ink(pts, 9, color=INK, taper=True)
                a.ink(pts, 5, color=color, taper=True)
        else:
            a.shape(ellipse(end[0], end[1], 9, 9, 16), GOLD, outline=DETAIL, depth=2, mottle=0)
        return a.image()

    return make


def broom_of_flying(seed=4066):
    """A broom 5 ft long, floating (a soft shadow offset below it)."""
    w, h = 300, 130
    a = art(w, h, seed)
    loc = lambda pts: rot_pts(pts, 150, 65, -0.15)  # noqa: E731
    straw = rgb("#d9bf72")
    bristle = loc([(190, 50), (280, 30), (290, 65), (280, 100), (190, 80)])
    soft_shadow(a, bristle, dx=10, dy=16, alpha=0.25, blur=8)
    a.ink(loc([(14, 65), (200, 65)]), 14 + 9, color=INK, taper=False, wob=0)
    a.ink(loc([(14, 65), (200, 65)]), 14, color=WOOD, taper=False, wob=0)

    def straws(art, p):
        for k in range(10):
            y = 38 + k * 6
            art.ink(loc([(194, 65 + (y - 65) * 0.3), (286, y)]), FINE, color=shade(straw, 0.45), alpha=0.75)

    a.shape(chaikin(bristle, True, 1), straw, outline=DETAIL * 1.6, corner=0, depth=3, light_k=0.4, detail=straws)
    a.shape(loc(rect(186, 54, 204, 76)), rgb("#7a4e32"), outline=DETAIL * 1.3, corner=3, depth=2, mottle=0)
    return a.image()


def wind_fan(seed=4067):
    """A folding fan of silk on ivory ribs, opened."""
    w, h = 240, 160
    a = art(w, h, seed)
    cx, cy = 120, 140
    pts = [(cx, cy)]
    for k in range(25):
        t = math.pi + 0.35 + k * (math.pi - 0.7) / 24
        pts.append((cx + 110 * math.cos(t), cy + 110 * math.sin(t)))
    soft_shadow(a, pts, dx=4, dy=6, alpha=0.3, blur=5)
    silk = rgb("#e6dcc8")

    def folds(art, p):
        for k in range(13):
            t = math.pi + 0.35 + k * (math.pi - 0.7) / 12
            art.ink([(cx + 30 * math.cos(t), cy + 30 * math.sin(t)), (cx + 108 * math.cos(t), cy + 108 * math.sin(t))], FINE * 1.1, color=shade(silk, 0.4), alpha=0.7)
        for k in range(3):
            pp = [(cx + (60 + k * 14) * math.cos(t), cy + (60 + k * 14) * math.sin(t)) for t in [math.pi + 0.6 + j * 0.15 for j in range(14)]]
            art.ink(pp, 2, color=rgb("#6f9ac0"), alpha=0.6)

    a.shape(pts, silk, outline=DETAIL * 1.6, corner=0, depth=3, light_k=0.4, detail=folds)
    a.shape(ellipse(cx, cy, 9, 9, 16), IVORY, outline=DETAIL, depth=1, mottle=0)
    return a.image()


def marvelous_pigments(seed=4068):
    """A wooden box of little paint pots and a brush."""
    w, h = 250, 180
    a = art(w, h, seed)
    soft_shadow(a, rect(20, 20, 230, 160), dx=5, dy=7, alpha=0.35, blur=6)
    board(a, 20, 20, 230, 160, WOOD, n=2, corner=6)
    a.shape(rect(34, 34, 216, 146), shade(WOOD, 0.3), outline=DETAIL * 1.3, corner=4, depth=4, shade_k=0.3, light_k=0, ao=0.5)
    paints = ["#c8443a", "#e6b84a", "#4f8fd0", "#6fb84a", "#a86ad0", "#f2efe6", "#2a2a30", "#e0883a"]
    for k, col in enumerate(paints):
        x, y = 60 + (k % 4) * 44, 66 + (k // 4) * 48
        a.shape(ellipse(x, y, 17, 17, 24), CERAMIC_, outline=DETAIL * 1.2, depth=2, mottle=0)
        a.shape(ellipse(x, y, 12, 12, 20), rgb(col), outline=FINE, depth=1, shade_k=0.2, light_k=0.3, ao=0, mottle=0)
    handle(a, 40, 160 - 4, 200, 150 - 4, 5, WOOD_DARK)
    a.shape(ellipse(204, 145, 9, 5, 16, rot=-0.06), rgb("#4f8fd0"), outline=FINE * 1.2, depth=1, mottle=0)
    return a.image()


CERAMIC_ = rgb("#e4dccb")


def instrument_of_the_bards(seed=4069):
    """A golden lyre, strings of silver, set with a little gem."""
    w, h = 200, 240
    a = art(w, h, seed)
    soft_shadow(a, rect(40, 30, 160, 220), dx=5, dy=7, alpha=0.3, blur=5)
    for side in (-1, 1):
        arm = [(100 + side * 30, 200), (100 + side * 66, 150), (100 + side * 70, 80), (100 + side * 50, 34)]
        a.ink(chaikin(arm, False, 3), 20, color=INK, taper=False)
        a.ink(chaikin(arm, False, 3), 12, color=GOLD, taper=False)
    a.shape(rect(52, 34, 148, 52), GOLD, outline=DETAIL * 1.4, corner=6, depth=3, light_k=0.5, mottle=0)
    a.shape(chaikin([(60, 180), (140, 180), (150, 222), (50, 222)], True, 2), shade(GOLD, 0.1), outline=DETAIL * 1.5, corner=0, depth=4, light_k=0.4)
    for k in range(7):
        x = 76 + k * 8
        a.ink([(x, 50), (x, 190)], 1.6, color=rgb("#e8ecf0"), alpha=0.95, taper=False, wob=0.1)
    dot(a, 100, 206, 7, rgb("#5fb0d8"))
    sparkle(a, 97, 203, 4)
    return a.image()


def pincer(a, x, y, k, side):
    """A crab's claw pointing up: a heavy palm and two curved jaws, the
    gap between them open toward the front."""
    for dx, L, out in ((-1, 80, 1.0), (1, 64, 0.8)):
        # Each jaw bows outward then hooks back in: the gap reads as a pincer.
        pts = [(x + dx * k * (14 + 26 * out * math.sin(math.pi * t) - 10 * t), y - 26 * k - L * k * t) for t in [i / 10 for i in range(11)]]
        a.shape(tube(pts, 26 * k, 4 * k), IRON, outline=DETAIL * 2, corner=0, depth=3, light_k=0.5, mottle=0)
    a.shape(ellipse(x, y, 34 * k, 40 * k, 32), DARK_IRON, outline=DETAIL * 2, depth=5, light_k=0.45)
    for t in (-0.4, 0.4):
        dot(a, x + 20 * k * math.sin(t), y + 20 * k * math.cos(t), 3, tint(DARK_IRON, 0.4))


def apparatus_of_the_crab(seed=4070):
    """A sealed iron barrel 10 ft long on ten jointed legs, with two great
    pincers at the front and porthole shutters along its back."""
    k = 256 / 5
    L, W = 10 * k, 5 * k
    w, h = int(W + 340), int(L + 480)
    a = art(w, h, seed)
    cx, cy = w / 2, h / 2 + 130
    body = ellipse(cx, cy, W / 2, L / 2, 80)
    for j in range(5):
        y = cy - L * 0.28 + j * L * 0.14
        for side in (-1, 1):
            knee = (cx + side * (W / 2 + 60), y - 20)
            foot = (cx + side * (W / 2 + 110), y + 30)
            for pts, wd in (([(cx + side * W * 0.3, y), knee], 16), ([knee, foot], 12)):
                a.ink(pts, wd + 9, color=INK, taper=False, wob=0)
                a.ink(pts, wd, color=DARK_IRON, taper=False, wob=0)
            dot(a, *knee, 9, IRON)
    for side in (-1, 1):
        base = (cx + side * W * 0.22, cy - L * 0.42)
        elbow = (cx + side * W * 0.5, cy - L * 0.58)
        a.ink([base, elbow], 30, color=INK, taper=False, wob=0)
        a.ink([base, elbow], 21, color=DARK_IRON, taper=False, wob=0)
        ex, ey = elbow
        pincer(a, ex, ey - 10, 1.35, side)
    soft_shadow(a, body, dx=10, dy=14, alpha=0.35, blur=10)

    def hoops(art, p):
        for j in range(-4, 5):
            y = cy + j * L * 0.1
            art.ink([(cx - W / 2, y), (cx + W / 2, y)], DETAIL * 1.4, color=shade(DARK_IRON, 0.5), alpha=0.85, taper=False)
        for j in range(-3, 4):
            y = cy + j * L * 0.1 + L * 0.05
            for x in (cx - W * 0.42, cx + W * 0.42):
                dot(art, x, y, 3, tint(DARK_IRON, 0.4))

    a.shape(body, DARK_IRON, outline=OUTLINE * 1.2, depth=14, light_k=0.4, detail=hoops)
    for j in (-1, 1):
        a.shape(ellipse(cx + j * 40, cy - L * 0.38, 18, 14, 24), rgb("#ffe39a"), outline=DETAIL * 1.6, depth=2, shade_k=0, light_k=0.4, mottle=0)
    a.shape(ellipse(cx, cy + L * 0.05, 36, 36, 32), IRON, outline=DETAIL * 1.8, depth=5, light_k=0.5)  # hatch
    a.ink([(cx - 26, cy + L * 0.05), (cx + 26, cy + L * 0.05)], DETAIL * 1.4, color=shade(IRON, 0.5), taper=False)
    return autocrop(a.image(), 12)


def rope_of_climbing():
    return rope_coil(rgb("#e0d4b4"), 4071)()


SRD_WONDROUS = {
    "Apparatus of the Crab": apparatus_of_the_crab,
    "Bag of Beans": bag_of_beans,
    "Bag of Devouring": bag_of_devouring,
    "Bag of Holding": bag_of_holding,
    "Bag of Holding (Open)": bag_of_holding_open,
    "Gray Bag of Tricks": bag_of_tricks(TRICKS["Gray"], 4005),
    "Rust Bag of Tricks": bag_of_tricks(TRICKS["Rust"], 4007),
    "Tan Bag of Tricks": bag_of_tricks(TRICKS["Tan"], 4008),
    "Handy Haversack": handy_haversack,
    "Bowl of Commanding Water Elementals": bowl_water,
    "Brazier of Commanding Fire Elementals": brazier_fire,
    "Censer of Controlling Air Elementals": censer_air,
    "Broom of Flying": broom_of_flying,
    "Candle of Invocation": candle_of_invocation,
    "Carpet of Flying": carpet,
    "Carpet of Flying (Large)": lambda: carpet(4046, 6, 9),
    "Chime of Opening": chime_of_opening,
    "Cube of Force": cube_of_force,
    "Cube of Force (Active)": lambda: cube_of_force(4047, active=True),
    "Cubic Gate": cubic_gate,
    "Decanter of Endless Water": decanter,
    "Decanter of Endless Water (Pouring)": lambda: decanter(4048, pouring=True),
    "Deck of Illusions": deck_of_illusions,
    "Deck of Many Things": deck_of_many_things,
    "Dimensional Shackles": dimensional_shackles,
    "Dust of Disappearance": dust_packet(rgb("#d8dce4"), rgb("#c8ccd8"), 4081, rgb("#7a8aa8")),
    "Dust of Dryness": dust_packet(rgb("#d8c8a0"), rgb("#b8a070"), 4082, rgb("#a8783e")),
    "Dust of Sneezing and Choking": dust_packet(rgb("#9a9690"), rgb("#7a7670"), 4083, rgb("#4f6a3a")),
    "Efficient Quiver": efficient_quiver,
    "Efreeti Bottle": efreeti_bottle,
    "Eversmoking Bottle": eversmoking_bottle,
    "Eversmoking Bottle (Smoking)": lambda: eversmoking_bottle(4049, smoking=True),
    "Feather Token": feather_token(rgb("#ece4d8"), 4091, GOLD),
    "Feather Token (Swan Boat)": feather_token(rgb("#f6f2ea"), 4092, rgb("#5fb0d8")),
    "Feather Token (Tree)": feather_token(rgb("#e2dccb"), 4093, rgb("#5f8a4a")),
    "Feather Token (Anchor)": feather_token(rgb("#d0ccc4"), 4094, IRON),
    "Figurine: Bronze Griffon": figurine_bird(BRONZE, rgb("#8a7a6a"), 4101, griffon=True),
    "Figurine: Ebony Fly": figurine_fly,
    "Figurine: Golden Lions": figurine_beast("cat", 150, rgb("#e2b84e"), rgb("#8a7a6a"), 4103, lion=True),
    "Figurine: Ivory Goats": figurine_beast("goat", 130, IVORY, rgb("#8a7a6a"), 4104, horn=rgb("#a89a84")),
    "Figurine: Marble Elephant": lambda: on_plinth(elephant_fig(), MARBLE, rgb("#8a8480"), 4105),
    "Figurine: Obsidian Steed": figurine_beast("horse", 150, OBSIDIAN, rgb("#8a8480"), 4106, mane=rgb("#6a6670")),
    "Figurine: Onyx Dog": figurine_beast("dog", 130, ONYX, rgb("#8a8480"), 4107),
    "Figurine: Serpentine Owl": figurine_bird(SERPENTINE, rgb("#8a7a6a"), 4108, owl=True),
    "Figurine: Silver Raven": figurine_bird(SILVER, rgb("#6a6670"), 4109),
    "Folding Boat": folding_boat,
    "Folding Boat (Boat)": lambda: folding_boat(4110, "boat"),
    "Folding Boat (Ship)": lambda: folding_boat(4111, "ship"),
    "Horn of Blasting": horn_of_blasting,
    "Silver Horn of Valhalla": horn_of_valhalla(SILVER, 4022),
    "Brass Horn of Valhalla": horn_of_valhalla(BRASS, 4023),
    "Bronze Horn of Valhalla": horn_of_valhalla(BRONZE, 4025),
    "Iron Horn of Valhalla": horn_of_valhalla(DARK_IRON, 4026),
    "Horseshoes of Speed": horseshoes(IRON, 4121, sparks=True),
    "Horseshoes of a Zephyr": horseshoes(SILVER, 4122, wind=True),
    "Instant Fortress": instant_fortress,
    "Instant Fortress (Deployed)": instant_fortress_deployed,
    "Instrument of the Bards": instrument_of_the_bards,
    "Iron Bands": iron_bands,
    "Iron Flask": iron_flask,
    "Lantern of Revealing": lantern_of_revealing,
    "Marvelous Pigments": marvelous_pigments,
    "Mirror of Life Trapping": mirror_of_life_trapping,
    "Pipes of Haunting": pan_pipes(rgb("#e6dcc4"), 4131, tie=rgb("#3a3436")),
    "Pipes of the Sewers": pan_pipes(rgb("#8a7a5a"), 4132, tie=rgb("#5a4a3a")),
    "Portable Hole": portable_hole,
    "Portable Hole (Folded)": lambda: portable_hole(4141, folded=True),
    "Rope of Climbing": rope_of_climbing,
    "Rope of Entanglement": rope_coil(rgb("#6a5a4a"), 4072, tendrils=True),
    "Sphere of Annihilation": sphere_of_annihilation,
    "Well of Many Worlds": well_of_many_worlds,
    "Well of Many Worlds (Folded)": lambda: well_of_many_worlds(4142, folded=True),
    "Wind Fan": wind_fan,
}

SRD_WONDROUS_COLORABLE = {"Bag of Holding", "Bag of Holding (Open)", "Handy Haversack", "Carpet of Flying", "Carpet of Flying (Large)"}
