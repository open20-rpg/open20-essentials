"""SRD 5.2.1 mounts and vehicles: the mounts the pack didn't have yet, tack,
drawn vehicles and ships. Top-down, same pen style; animals and vehicles
face up (toward the top of the image) and are drawn at map scale
(256 px = 5 ft). Ships are at scale up to ~4096 px on their long side
(the longest ones a little under scale). Red (g == b) parts recolor."""

import math

import numpy as np
import skia

import obj_farm as farm
import objects as objs
from kit import BRASS, IRON, RED, WOOD, WOOD_DARK, WOOD_LIGHT, board, boards, dot, soft_shadow
from obj_craft import STEEL, handle
from obj_farm import PLANS, Spine, autocrop, beast
from obj_town import wheel
from obj_variants import swap
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path

FT = 256 / 5  # px per foot
O = DETAIL * 2.0
CANVAS = rgb("#e6dcc4")
ROPE = rgb("#c9b088")
LEATHER = rgb("#8a5a3a")
LEATHER_D = rgb("#6a422a")
HULL = rgb("#6e4a30")
DECK = rgb("#c49a68")
GOLD = rgb("#d8b04a")
OATS = rgb("#d6bc7a")


def paste(a, img, cx, cy, w=None, rot=0.0):
    """Draw a PIL image centred at (cx, cy), `w` px wide, rotated `rot` rad."""
    if w is not None:
        img = img.resize((int(w), int(img.height * w / img.width)))
    sk = skia.Image.fromarray(np.ascontiguousarray(np.asarray(img.convert("RGBA"))), colorType=skia.kRGBA_8888_ColorType)
    a.c.save()
    a.c.translate(cx, cy)
    a.c.rotate(math.degrees(rot))
    a.c.drawImageRect(sk, skia.Rect.MakeXYWH(-img.width / 2, -img.height / 2, img.width, img.height), skia.SamplingOptions(skia.FilterMode.kLinear))
    a.c.restore()


# -- mounts ----------------------------------------------------------------------------------------


def horse_spine(kind, L, bend):
    """The spine `beast` builds for a horse-plan animal of length L (no
    jitter), so tack and barding can be laid on it."""
    Wk, profile, anch = PLANS["horse"]
    profile = [(s, w * (1.2 if s <= anch["ear"] + 0.02 else 1.0)) for s, w in profile]
    if kind == "pony":
        profile = [(s, w * 1.12) for s, w in profile]
    W = Wk * L
    size = int(L * 2.2 + 140)
    return Spine(size / 2, 80 + W * 0.3, L, W, profile, bend), size


def dressed(kind, L, color, bend, seed, over, **kw):
    """A horse-plan beast with something drawn over it (`over(art, spine)`)."""

    def make():
        with swap(farm, autocrop=lambda img, pad=10: img):
            base = beast(kind, L, color, bend=bend, **kw)(seed)
        sp, size = horse_spine(kind, L, bend)
        a = Art(size, size, seed + 1)
        over(a, sp)
        base.alpha_composite(a.image())
        return autocrop(base)

    return make


def body_band(sp, s0, s1, k=1.0, n=14):
    """Outline of the body between s0 and s1, widened by k (unjittered)."""
    ss = [s0 + (s1 - s0) * i / n for i in range(n + 1)]
    left = [sp.side_pt(s, float(np.interp(s, sp.ss, sp.ws)) * k, -1) for s in ss]
    right = [sp.side_pt(s, float(np.interp(s, sp.ss, sp.ws)) * k, 1) for s in ss]
    return left + right[::-1]


def hump(a, sp):
    """A dromedary's hump: a long, soft rise over the back, lit on top, its
    edge only a faint line where it settles into the body."""
    W = sp.W
    left = [sp.at(s, -k) for s, k in ((0.47, 0.25), (0.52, 0.55), (0.6, 0.66), (0.7, 0.6), (0.78, 0.3))]
    right = [sp.at(s, k) for s, k in ((0.47, 0.25), (0.52, 0.55), (0.6, 0.66), (0.7, 0.6), (0.78, 0.3))]
    pts = chaikin(left + right[::-1], True, 3)
    col = rgb("#d4b07a")
    cx, cy = sp.at(0.6)

    def hair(art, p):
        g = skia.Path()
        g.addOval(skia.Rect.MakeXYWH(cx - W * 0.28, cy - sp.L * 0.12, W * 0.4, sp.L * 0.16))
        art.fill_path(g, tint(col, 0.4), 0.55, blur=14)
        for _ in range(30):
            t = art.rng.uniform(0, 6.28)
            r = art.rng.uniform(0.35, 0.9)
            px, py = cx + W * 0.3 * r * math.cos(t), cy + sp.L * 0.15 * r * math.sin(t)
            art.ink([(px, py), (px + 6 * math.cos(t), py + 6 * math.sin(t))], FINE * 0.9, color=shade(col, 0.45), alpha=0.45)

    a.shape(pts, col, outline=DETAIL * 1.1, outline_color=shade(col, 0.6), outline_alpha=0.8, corner=0, depth=14, shade_k=0.45, light_k=0.2, ao=0.2, detail=hair)


def barding(a, sp):
    """Warhorse kit: a cloth caparison over the body (red = colorable) with a
    gold hem, plate crinet on the neck, a chanfron on the face and a war
    saddle."""
    cap = chaikin(body_band(sp, 0.40, 1.0, 1.16), True, 2)
    soft_shadow(a, cap, dx=4, dy=5, alpha=0.25, blur=5)

    def pattern(art, p):
        art.ink(chaikin(body_band(sp, 0.40, 1.0, 1.0), True, 2), DETAIL * 1.4, closed=True, color=GOLD, alpha=0.95, taper=False, wob=0.3)
        for s in (0.62, 0.84):
            for side in (-1, 1):
                x, y = sp.at(s, side * 0.62)
                art.shape([(x, y - 22), (x + 14, y), (x, y + 22), (x - 14, y)], GOLD, outline=FINE * 1.3, corner=1, depth=2, mottle=0)

    a.shape(cap, RED, outline=OUTLINE * 0.75, corner=0, depth=10, light_k=0.3, detail=pattern)
    # Crinet: overlapping plates down the neck crest.
    for k in range(6, -1, -1):
        s = 0.27 + k * 0.022
        x, y, tx, ty, nx, ny = sp.frame(s)
        hw = sp.hw(s) * 0.62
        pts = [(x - nx * hw, y - ny * hw), (x + nx * hw, y + ny * hw), (x + nx * hw * 0.9 + tx * 16, y + ny * hw * 0.9 + ty * 16), (x - nx * hw * 0.9 + tx * 16, y - ny * hw * 0.9 + ty * 16)]
        a.shape(pts, STEEL, outline=DETAIL * 1.2, corner=4, depth=3, light_k=0.5, mottle=0)
    # Chanfron: a plate down the face with a small spike.
    pts = [sp.at(0.025, -0.45), sp.at(0.025, 0.45), sp.at(0.12, 0.62), sp.at(0.2, 0.55), sp.at(0.2, -0.55), sp.at(0.12, -0.62)]
    a.shape(pts, STEEL, outline=DETAIL * 1.4, corner=8, depth=4, light_k=0.5, mottle=0, detail=lambda art, p: art.ink(sp.line(0.04, 0.18), FINE * 1.3, color=shade(STEEL, 0.45), alpha=0.8))
    x, y = sp.at(0.13)
    a.shape(ellipse(x, y, 7, 7, 14), BRASS, outline=FINE * 1.3, depth=1, mottle=0)
    # War saddle: high pommel and cantle.
    war_saddle_on(a, sp, 0.5, 0.68)


def war_saddle_on(a, sp, s0, s1):
    """A war saddle on the spine: narrow at the pommel, broad at the high
    cantle, its flaps and stirrups hanging over the sides."""
    sm = (s0 + s1) / 2
    for side in (-1, 1):  # flaps
        flap = [sp.at(s0 + 0.03, side * 0.5), sp.at(s0 + 0.03, side * 1.08), sp.at(s1 - 0.03, side * 1.08), sp.at(s1 - 0.03, side * 0.5)]
        a.shape(flap, LEATHER_D, outline=DETAIL * 1.3, corner=10, depth=3, light_k=0.3)
        x, y = sp.at(sm, side * 1.2)
        a.shape(rect(x - 9, y - 12, x + 9, y + 12), IRON, outline=DETAIL, corner=4, depth=2, mottle=0)
    seat = chaikin([sp.at(s0, 0), sp.at(s0 + 0.03, 0.4), sp.at(sm, 0.62), sp.at(s1, 0.72), sp.at(s1 + 0.012, 0), sp.at(s1, -0.72), sp.at(sm, -0.62), sp.at(s0 + 0.03, -0.4)], True, 2)
    a.shape(seat, LEATHER, outline=DETAIL * 1.7, corner=0, depth=7, light_k=0.45)
    a.shape(chaikin([sp.at(s0 - 0.005, 0), sp.at(s0 + 0.02, 0.3), sp.at(s0 + 0.04, 0), sp.at(s0 + 0.02, -0.3)], True, 2), LEATHER_D, outline=DETAIL * 1.3, corner=0, depth=3, mottle=0)
    a.shape(chaikin([sp.at(s1 - 0.025, 0.7), sp.at(s1 + 0.012, 0.6), sp.at(s1 + 0.018, 0), sp.at(s1 + 0.012, -0.6), sp.at(s1 - 0.025, -0.7), sp.at(s1 - 0.01, 0)], True, 2), LEATHER_D, outline=DETAIL * 1.3, corner=0, depth=4, light_k=0.4, mottle=0)


def elephant(seed=1601):
    w, h = 760, 900
    a = Art(w, h, seed)
    G = rgb("#8f8984")
    cx = w / 2
    body = chaikin([(cx, 300), (cx + 150, 320), (cx + 205, 430), (cx + 215, 600), (cx + 195, 740), (cx + 120, 820), (cx, 832), (cx - 120, 820), (cx - 195, 740), (cx - 215, 600), (cx - 205, 430), (cx - 150, 320)], True, 3)
    soft_shadow(a, body, dx=8, dy=10, alpha=0.28, blur=9)
    # Tail: thin, with a tuft.
    tp = chaikin([(cx + 6, 815), (cx + 20, 850), (cx + 12, 880)], False, 2)
    a.ink(tp, 10, color=INK, taper=False)
    a.ink(tp, 5, color=shade(G, 0.1), taper=False)
    a.shape(ellipse(cx + 12, 884, 6, 10, 12), shade(G, 0.5), outline=FINE * 1.3, depth=1, mottle=0)
    for side in (-1, 1):  # foot tips
        for y in (420, 760):
            x = cx + side * 200
            a.shape(ellipse(x, y, 34, 30, 20), shade(G, 0.15), outline=DETAIL * 1.3, depth=2, mottle=0, light_k=0)

    def wrinkles(art, p):
        art.ink([(cx, 330), (cx + 4, 800)], FINE * 1.3, color=shade(G, 0.4), alpha=0.45)
        for _ in range(40):
            x, y = art.rng.uniform(cx - 190, cx + 190), art.rng.uniform(330, 810)
            art.ink([(x, y), (x + art.rng.uniform(-14, 14), y + art.rng.uniform(4, 10))], FINE, color=shade(G, 0.4), alpha=0.45)
        for side in (-1, 1):
            art.ink(chaikin([(cx + side * 60, 690), (cx + side * 150, 700), (cx + side * 190, 760)], False, 2), FINE * 1.2, color=shade(G, 0.4), alpha=0.5)

    a.shape(body, G, outline=OUTLINE * 0.9, corner=0, depth=16, light_k=0.35, detail=wrinkles)
    # Ears: big fans lying back over the shoulders.
    for side in (-1, 1):
        ear = chaikin([(cx + side * 70, 190), (cx + side * 200, 170), (cx + side * 300, 230), (cx + side * 320, 340), (cx + side * 280, 450), (cx + side * 200, 470), (cx + side * 140, 400), (cx + side * 90, 300)], True, 3)

        def veins(art, p, side=side):
            for k in range(4):
                art.ink(chaikin([(cx + side * 110, 240 + k * 30), (cx + side * (190 + k * 12), 270 + k * 40), (cx + side * (250 - k * 10), 360 + k * 25)], False, 2), FINE * 1.1, color=shade(G, 0.4), alpha=0.5)
            art.fill_path(to_path(chaikin([(cx + side * 120, 220), (cx + side * 250, 230), (cx + side * 280, 340), (cx + side * 220, 420), (cx + side * 150, 360)], True, 2)), tint(rgb("#c8a0a0"), 0.1), 0.25)

        a.shape(ear, shade(G, 0.06), outline=OUTLINE * 0.75, corner=0, depth=10, light_k=0.3, detail=veins)
    # Tusks, then the head over their roots, then the trunk.
    for side in (-1, 1):
        tusk = chaikin([(cx + side * 50, 150), (cx + side * 74, 90), (cx + side * 60, 40)], False, 2)
        a.ink(tusk, 22, color=INK, taper=True)
        a.ink(tusk, 15, color=rgb("#efe6d2"), taper=True)
    # The head runs on into the shoulders: only its front and sides are
    # inked, so it reads as one animal and not a ball set on the body.
    head = chaikin([(cx, 92), (cx + 90, 110), (cx + 125, 190), (cx + 118, 290), (cx + 60, 360), (cx, 372), (cx - 60, 360), (cx - 118, 290), (cx - 125, 190), (cx - 90, 110)], True, 3)

    def face(art, p):
        art.ink(chaikin([(cx - 70, 150), (cx, 130), (cx + 70, 150)], False, 2), FINE * 1.2, color=shade(G, 0.4), alpha=0.5)
        art.ink([(cx, 140), (cx, 260)], FINE * 1.2, color=shade(G, 0.4), alpha=0.35)

    a.shape(head, G, outline=0, corner=0, depth=12, shade_k=0, light_k=0.4, ao=0, mottle=0.03, detail=face)
    front = [p for p in head if p[1] < 300]
    k = max(range(len(front)), key=lambda i: math.hypot(front[i][0] - front[i - 1][0], front[i][1] - front[i - 1][1]))
    a.ink(front[k:] + front[:k], OUTLINE * 0.85, wob=0.3)
    for side in (-1, 1):
        dot(a, cx + side * 108, 175, 5, INK)
    trunk = chaikin([(cx, 120), (cx + 4, 70), (cx + 30, 30), (cx + 62, 18)], False, 3)
    a.ink(trunk, 52, color=INK, taper=False, var=0.05)
    a.ink(trunk, 40, color=G, taper=False, var=0.05)
    for i in range(3, len(trunk) - 2, 3):  # rings
        (px, py), (qx, qy) = trunk[i - 1], trunk[i + 1]
        d = math.hypot(qx - px, qy - py) or 1
        ux, uy = -(qy - py) / d, (qx - px) / d
        x, y = trunk[i]
        a.ink([(x - ux * 15, y - uy * 15), (x + ux * 15, y + uy * 15)], FINE * 1.1, color=shade(G, 0.45), alpha=0.6)
    x, y = trunk[-1]
    a.shape(ellipse(x, y, 20, 20, 18), shade(G, 0.1), outline=DETAIL * 1.4, depth=3, mottle=0)
    for k in (-1, 1):
        dot(a, x + 7 * k, y, 4, INK)
    return autocrop(a.image())


# -- tack and feed ---------------------------------------------------------------------------------


def military_saddle(seed=1611):
    w, h = 280, 340
    a = Art(w, h, seed)
    cx = w / 2

    def quilt(art, p):
        art.ink(rect(32, 52, w - 32, h - 52), DETAIL * 1.3, closed=True, color=GOLD, alpha=0.9, taper=False, wob=0.3)

    a.shape(rect(18, 36, w - 18, h - 36), RED, outline=DETAIL * 1.4, corner=10, depth=5, light_k=0.3, detail=quilt)
    seat = chaikin([(cx, 40), (w - 54, 82), (w - 46, 200), (cx, h - 46), (46, 200), (54, 82)], True, 2)
    a.shape(seat, LEATHER, depth=10, light_k=0.45)
    a.shape(chaikin([(cx - 50, 52), (cx + 50, 52), (cx + 46, 92), (cx - 46, 92)], True, 2), LEATHER_D, outline=DETAIL * 1.4, depth=5, light_k=0.4)  # pommel
    a.shape(chaikin([(cx - 70, h - 108), (cx + 70, h - 108), (cx + 56, h - 62), (cx - 56, h - 62)], True, 2), LEATHER_D, outline=DETAIL * 1.4, depth=5, light_k=0.4)  # high cantle
    for x in (cx - 30, cx + 30):
        dot(a, x, 72, 4, BRASS)
    a.ink(chaikin([(76, 170), (cx, 154), (w - 76, 170)], False, 2), FINE * 1.3, color=shade(LEATHER, 0.45))
    for side in (-1, 1):  # lance rest / holster and stirrups
        x = cx + side * (w / 2 - 22)
        a.ink([(x, 150), (x, 226)], DETAIL * 1.4, color=LEATHER_D)
        a.shape(rect(x - 15, 222, x + 15, 244), IRON, outline=DETAIL, corner=4, depth=2, mottle=0)
    a.shape(rect(w - 60, 96, w - 30, 150), LEATHER_D, outline=DETAIL * 1.2, corner=5, depth=3)
    return a.image()


def exotic_saddle(seed=1612):
    """For an unusual mount (a griffon, a giant lizard): a strapped frame
    with a high backrest, a broad girth and many buckled straps."""
    w, h = 320, 380
    a = Art(w, h, seed)
    cx = w / 2
    for y in (110, 250):  # girth straps running out to both sides
        a.shape(rect(6, y - 13, w - 6, y + 13), LEATHER_D, outline=DETAIL * 1.3, corner=5, depth=3)
        for x in (24, w - 24):
            a.shape(rect(x - 10, y - 12, x + 10, y + 12), BRASS, outline=FINE * 1.3, corner=3, depth=1, mottle=0)

    def weave(art, p):
        for k in range(6):
            art.ink([(70, 70 + k * 46), (w - 70, 70 + k * 46)], FINE * 1.2, color=shade(RED, 0.45), alpha=0.7)
        art.ink(rect(66, 64, w - 66, h - 64), DETAIL * 1.2, closed=True, color=GOLD, alpha=0.9, taper=False)

    a.shape(rect(50, 46, w - 50, h - 46), RED, outline=DETAIL * 1.4, corner=26, depth=6, light_k=0.3, detail=weave)
    seat = chaikin([(cx, 64), (cx + 72, 110), (cx + 66, 230), (cx, 262), (cx - 66, 230), (cx - 72, 110)], True, 2)
    a.shape(seat, LEATHER, depth=10, light_k=0.45)
    a.shape(chaikin([(cx - 26, 64), (cx + 26, 64), (cx + 20, 104), (cx - 20, 104)], True, 2), LEATHER_D, outline=DETAIL * 1.4, depth=4)
    # High backrest frame behind the seat, with its strut.
    a.shape(chaikin([(cx - 92, 248), (cx + 92, 248), (cx + 84, 300), (cx - 84, 300)], True, 2), WOOD_DARK, outline=DETAIL * 1.6, depth=6, light_k=0.4, detail=lambda art, p: boards(art, cx - 92, 248, cx + 92, 300, WOOD_DARK, 2))
    a.shape(chaikin([(cx - 80, 256), (cx + 80, 256), (cx + 74, 286), (cx - 74, 286)], True, 2), LEATHER, outline=DETAIL * 1.1, depth=3, light_k=0.3)
    for x in (cx - 70, cx + 70):
        dot(a, x, 270, 5, BRASS)
    for side in (-1, 1):  # safety straps hanging loose
        x = cx + side * 64
        a.ink(chaikin([(x, 170), (x + side * 26, 196), (x + side * 18, 228)], False, 2), DETAIL * 1.6, color=LEATHER_D)
        a.shape(rect(x + side * 18 - 9, 224, x + side * 18 + 9, 238), IRON, outline=FINE * 1.3, corner=2, depth=1, mottle=0)
    return a.image()


def feed(seed=1613):
    """A day's feed: a canvas nosebag full of oats, its strap trailing."""
    w, h = 220, 200
    a = Art(w, h, seed)
    strap = chaikin([(62, 70), (24, 120), (60, 178), (150, 182), (196, 140)], False, 3)
    a.ink(strap, 13, color=INK, taper=False)
    a.ink(strap, 7, color=LEATHER, taper=False)
    from kit import scallop

    a.shape(scallop(110, 96, 74, a.rng, 14, 0.1, ry=68), rgb("#b8a684"), corner=0, depth=10, light_k=0.35, detail=lambda art, p: [art.ink([(110 + 72 * math.cos(t), 96 + 66 * math.sin(t)), (110 + 56 * math.cos(t), 96 + 50 * math.sin(t))], FINE * 1.2, color=shade(rgb("#b8a684"), 0.45), alpha=0.7) for t in [k * 6.28 / 14 for k in range(14)]])
    a.shape(ellipse(110, 92, 56, 50, 36), shade(rgb("#b8a684"), 0.3), outline=DETAIL * 1.2, depth=6, shade_k=0, light_k=0, ao=0.5)

    def grains(art, p):
        for _ in range(140):
            x, y = art.rng.uniform(56, 166), art.rng.uniform(44, 140)
            t = art.rng.uniform(0, 3.14)
            art.fill_path(to_path(ellipse(x, y, 4, 2, 8, rot=t)), mix(OATS, rgb("#a8884e"), art.rng.random()), 0.95)

    a.shape(ellipse(110, 94, 50, 44, 36), OATS, outline=FINE * 1.3, depth=5, light_k=0.5, detail=grains)
    for x, y in ((180, 70), (190, 92), (40, 64)):  # a few spilled grains
        a.shape(ellipse(x, y, 4, 2, 8, rot=a.rng.uniform(0, 3)), OATS, outline=FINE * 0.8, depth=0.5, mottle=0)
    return a.image()


# -- drawn vehicles --------------------------------------------------------------------------------


def shafts(a, x0, y_mid, x1, gap, w=12):
    for s in (-1, 1):
        handle(a, x0, y_mid + s * gap, x1, y_mid + s * gap * 0.75, w)
    a.ink([(x0 + 20, y_mid - gap), (x0 + 20, y_mid + gap)], 10, color=INK, taper=False)
    a.ink([(x0 + 20, y_mid - gap), (x0 + 20, y_mid + gap)], 5, color=WOOD, taper=False)


def tongue(a, x0, y, x1, yoke=70):
    handle(a, x0, y, x1, y, 14)
    a.shape(rect(x1 - 30, y - yoke, x1 - 14, y + yoke), WOOD_DARK, outline=DETAIL * 1.4, corner=6, depth=3)


def wagon(seed=1621):
    """An open four-wheeled wagon: plank bed with side boards, a driver's
    bench at the front and the tongue for a team."""
    w, h = 660, 300
    a = Art(w, h, seed)
    for x in (120, 380):
        wheel(a, x, 22, 120, 22)
        wheel(a, x, h - 22, 120, 22)
    tongue(a, 470, h / 2, w - 14)
    a.shape(rect(30, 40, 480, h - 40), WOOD_DARK, corner=6, depth=10, detail=lambda art, p: boards(art, 30, 40, 480, h - 40, WOOD_DARK, 2))
    a.shape(rect(46, 56, 464, h - 56), WOOD, outline=DETAIL * 1.3, corner=4, depth=8, shade_k=0.3, light_k=0, ao=0.45, detail=lambda art, p: boards(art, 46, 56, 464, h - 56, WOOD, 6, vertical=True))
    board(a, 400, 58, 452, h - 58, WOOD_LIGHT, n=1, corner=5)  # driver's bench
    for img, x, y, ww in ((objs.OBJECTS["Sack"](seed=31), 120, 110, 100), (objs.OBJECTS["Sack"](seed=32), 200, 180, 100), (objs.OBJECTS["Crate"](), 300, 120, 110), (objs.OBJECTS["Barrel"](), 110, 200, 90)):
        paste(a, img, x, y, ww, a.rng.uniform(-0.4, 0.4))
    return a.image()


def carriage(seed=1622):
    """A closed coach: lacquered roof (red = colorable) with a gilt rail and
    luggage, the driver's box in front, lamps, four wheels, the tongue."""
    w, h = 700, 340
    a = Art(w, h, seed)
    for x, r in ((130, 140), (420, 110)):
        wheel(a, x, 24, r, 22)
        wheel(a, x, h - 24, r, 22)
    tongue(a, 520, h / 2, w - 14, 80)
    # Running board and body under the roof.
    a.shape(rect(36, 44, 540, h - 44), WOOD_DARK, corner=12, depth=8, detail=lambda art, p: boards(art, 36, 44, 540, h - 44, WOOD_DARK, 2))
    board(a, 430, 60, 520, h - 60, WOOD, n=1, corner=8)  # driver's box
    a.shape(rect(450, 76, 500, h - 76), mix(RED, (90, 30, 30), 0.35), outline=DETAIL * 1.2, corner=10, depth=4, light_k=0.3)  # seat cushion
    for y in (58, h - 58):  # lamps
        a.shape(ellipse(426, y, 13, 13, 18), BRASS, outline=DETAIL * 1.2, depth=2, mottle=0)
        dot(a, 426, y, 5, rgb("#f6e3a0"))

    def roof_detail(art, p):
        art.ink(rect(62, 72, 404, h - 72), DETAIL * 1.6, closed=True, color=GOLD, alpha=0.95, taper=False, wob=0.3)
        for x in (150, 240, 330):
            art.ink([(x, 74), (x, h - 74)], FINE * 1.2, color=shade(RED, 0.4), alpha=0.6)

    a.shape(rect(48, 56, 420, h - 56), RED, outline=OUTLINE, corner=26, depth=12, light_k=0.35, detail=roof_detail)
    for x, y in ((62, 72), (404, 72), (62, h - 72), (404, h - 72)):
        a.shape(ellipse(x, y, 9, 9, 14), GOLD, outline=FINE * 1.4, depth=1, mottle=0)
    # Strapped trunk on the roof at the back.
    a.shape(rect(86, 120, 180, h - 120), LEATHER, outline=DETAIL * 1.4, corner=8, depth=5, light_k=0.4)
    for y in (140, h - 140):
        a.ink([(84, y), (182, y)], DETAIL * 1.3, color=LEATHER_D, taper=False)
    return a.image()


def chariot(seed=1623):
    """A two-wheeled war chariot: an open D-shaped car (painted sides: red =
    colorable) on a single axle, with a long pole and yoke for two horses."""
    w, h = 560, 300
    a = Art(w, h, seed)
    axle = 130
    a.ink([(axle, 30), (axle, h - 30)], 16, color=INK, taper=False)
    a.ink([(axle, 30), (axle, h - 30)], 9, color=WOOD_DARK, taper=False)
    for y in (26, h - 26):
        wheel(a, axle, y, 150, 20)
        for k in (-1, 1):  # scythe blades on the hubs
            a.shape([(axle - 6, y + k * 4), (axle + 6, y + k * 4), (axle + 2, y + k * 34)], STEEL, outline=DETAIL, corner=0, depth=1, mottle=0, light_k=0.5)
    tongue(a, 200, h / 2, w - 16, 96)
    car = chaikin([(60, 60), (150, 60), (210, 90), (232, h / 2), (210, h - 90), (150, h - 60), (60, h - 60)], True, 2)
    a.shape(car, RED, depth=10, light_k=0.35, detail=lambda art, p: art.ink(chaikin([(70, 72), (148, 72), (200, 98), (220, h / 2), (200, h - 98), (148, h - 72), (70, h - 72)], False, 2), DETAIL * 1.3, color=GOLD, alpha=0.9, taper=False))
    floor = chaikin([(74, 78), (146, 78), (194, 104), (212, h / 2), (194, h - 104), (146, h - 78), (74, h - 78)], True, 2)
    a.shape(floor, WOOD, outline=DETAIL * 1.2, corner=0, depth=8, shade_k=0.3, light_k=0, ao=0.5, detail=lambda art, p: boards(art, 70, 76, 216, h - 76, WOOD, 5, vertical=True))
    a.shape(ellipse(220, h / 2, 12, 12, 16), GOLD, outline=DETAIL, depth=2, mottle=0)
    return a.image()


def sled(seed=1624):
    """A cargo sled: two runners curling up at the front, a slatted deck
    with a lashed bundle, and the hauling rope."""
    w, h = 460, 220
    a = Art(w, h, seed)
    for y in (34, h - 34):
        a.shape(rect(30, y - 9, 360, y + 9), WOOD_DARK, outline=DETAIL * 1.6, corner=8, depth=3)
        a.ink(chaikin([(340, y), (378, y), (396, y + (h / 2 - y) * 0.12)], False, 2), 18 + DETAIL * 2.4, color=INK, taper=False)
        a.ink(chaikin([(340, y), (378, y), (396, y + (h / 2 - y) * 0.12)], False, 2), 14, color=WOOD_DARK, taper=False)
    rope = chaikin([(396, 40), (430, h / 2 - 10), (452, h / 2), (430, h / 2 + 10), (396, h - 40)], False, 3)
    a.ink(rope, 9, color=INK, taper=False)
    a.ink(rope, 5, color=ROPE, taper=False)
    for k in range(7):  # cross slats
        x = 50 + k * 46
        a.shape(rect(x, 24, x + 32, h - 24), WOOD, outline=DETAIL * 1.3, corner=4, depth=3, detail=lambda art, p, x=x: boards(art, x, 24, x + 32, h - 24, WOOD, 1, vertical=True))
    fur = rgb("#8a6a4e")

    def tufts(art, p):
        for _ in range(60):
            x, y = art.rng.uniform(80, 300), art.rng.uniform(56, h - 56)
            art.ink([(x, y), (x + art.rng.uniform(-6, 6), y + 8)], FINE, color=shade(fur, 0.45), alpha=0.6)

    a.shape(blob(190, h / 2, 120, a.rng, 12, 0.08, ry=70), fur, outline=OUTLINE * 0.8, smooth=True, depth=10, light_k=0.35, detail=tufts)
    for x in (140, 240):
        a.ink([(x, 40), (x + 6, h - 40)], DETAIL * 1.6, color=ROPE)
    return a.image()


# -- ships -----------------------------------------------------------------------------------------
# Bow at the top. A hull is a half-width profile along the length; inside
# its rail, the deck's planks run lengthwise. Sails are drawn furled on
# their yards so the deck stays playable.


def big_shape(a, pts, color, outline=OUTLINE, depth=12, shade_k=0.5, light_k=0.35, ao=0.35, mottle=0.03, detail=None, wob=0.6):
    """Art.shape for ship-sized outlines: the same fill, shading and ink, but
    the path is sampled coarser (skia's path ops give up on the thousands of
    points a 3 px resampling makes along a 4000 px hull)."""
    from pen import wobble

    q = wobble(pts, True, a.rng, amp=wob, wavelength=80, step=8)
    path = to_path(q)
    a.fill_path(path, color)
    b = path.getBounds()
    with a.clip(path):
        if mottle > 0:
            a.mottle(b, color, mottle)
        if detail:
            detail(a, path)
        lx, ly = a.light
        for k, col, alpha in ((1.0, shade(color, 0.3), shade_k), (-0.55, tint(color, 0.45), light_k)):
            if alpha > 0:
                moved = skia.Path(path)
                moved.offset(lx * depth * k, ly * depth * k)
                a.fill_path(skia.Op(path, moved, skia.kDifference_PathOp), col, alpha, blur=0.6)
        if ao > 0:
            a.stroke_path(path, shade(color, 0.4), depth * 1.6, ao, blur=depth * 0.9)
    if outline:
        a.ink(q, outline, closed=True, wob=0.0, var=0.14)
    return path


def hull_outline(cx, top, L, W, prof):
    left = [(cx - W / 2 * w, top + L * t) for t, w in prof]
    right = [(cx + W / 2 * w, top + L * t) for t, w in prof]
    return chaikin(left + right[::-1], True, 3)


def inset(prof, k, cut=0.012):
    """The profile of the deck inside a rail: narrower, and short of the
    hull's ends."""
    t0, t1 = prof[0][0] + cut * 2, prof[-1][0] - cut
    return [(t0 + (t - prof[0][0]) * (t1 - t0) / (prof[-1][0] - prof[0][0]), w * k) for t, w in prof]


def deck(a, cx, top, L, W, prof, hull=HULL, planks=DECK, rail=0.9):
    outer = hull_outline(cx, top, L, W, prof)
    soft_shadow(a, outer, dx=10, dy=14, alpha=0.3, blur=12)
    big_shape(a, outer, hull, outline=OUTLINE * 1.1, depth=14, light_k=0.3)
    inner = hull_outline(cx, top, L, W, inset(prof, rail))
    n = max(6, int(W / 34))
    big_shape(a, inner, planks, outline=DETAIL * 1.5, wob=0.4, depth=12, shade_k=0.35, light_k=0, ao=0.45, detail=lambda art, p: boards(art, cx - W / 2, top, cx + W / 2, top + L, planks, n, vertical=True))
    return outer, inner


def butt_joints(a, cx, top, L, W, color=DECK, every=150):
    """Short crosswise seams where deck planks butt, staggered."""
    n = max(6, int(W / 34))
    for k in range(n):
        x0 = cx - W / 2 + W * k / n
        y = top + a.rng.uniform(0, every)
        while y < top + L:
            a.ink([(x0 + 2, y), (x0 + W / n - 2, y)], FINE, color=shade(color, 0.5), alpha=0.55, taper=False, wob=0.2)
            y += every * a.rng.uniform(0.8, 1.3)


def mast(a, x, y, yard_w, r=22, sail=CANVAS, furl=True):
    """A mast from above with its yard across the ship and the sail furled
    along it (lashed with gaskets)."""
    if yard_w:
        a.shape(rect(x - yard_w / 2, y - 9, x + yard_w / 2, y + 9), WOOD_DARK, outline=DETAIL * 1.4, corner=8, depth=3)
        if furl:
            fw = yard_w * 0.88

            def gaskets(art, p):
                for k in range(1, 9):
                    gx = x - fw / 2 + fw * k / 9
                    art.ink([(gx - 3, y + 2), (gx + 3, y + 44)], DETAIL * 1.3, color=shade(ROPE, 0.3), alpha=0.9)
                for yy in (y + 16, y + 30):
                    art.ink([(x - fw / 2 + 16, yy), (x + fw / 2 - 16, yy)], FINE * 1.3, color=shade(sail, 0.4), alpha=0.6)

            a.shape(chaikin([(x - fw / 2, y + 2), (x + fw / 2, y + 2), (x + fw / 2 - 18, y + 46), (x - fw / 2 + 18, y + 46)], True, 2), sail, outline=DETAIL * 1.4, corner=0, depth=6, light_k=0.4, detail=gaskets)
    a.shape(ellipse(x, y, r, r, 24), WOOD_DARK, outline=DETAIL * 1.6, depth=4, light_k=0.45, mottle=0)
    a.ink(ellipse(x, y, r * 0.5, r * 0.5, 16), FINE * 1.2, closed=True, color=shade(WOOD_DARK, 0.4), alpha=0.7)


def shrouds(a, x, y, pts, alpha=0.75):
    for px, py in pts:
        a.ink([(x, y), (px, py)], FINE * 1.2, color=INK, alpha=alpha, taper=False, wob=0.2)


def hatch(a, x0, y0, x1, y1):
    a.shape(rect(x0, y0, x1, y1), WOOD_DARK, outline=DETAIL * 1.5, corner=4, depth=4, light_k=0.4)
    g = rect(x0 + 10, y0 + 10, x1 - 10, y1 - 10)
    a.shape(g, rgb("#2e2622"), outline=DETAIL, corner=2, depth=2, shade_k=0, light_k=0, ao=0, mottle=0)
    with a.clip(to_path(g)):
        for x in range(int(x0 + 18), int(x1 - 10), 18):
            a.ink([(x, y0 + 10), (x, y1 - 10)], 6, color=WOOD, taper=False, wob=0)
        for y in range(int(y0 + 18), int(y1 - 10), 18):
            a.ink([(x0 + 10, y), (x1 - 10, y)], 6, color=WOOD, taper=False, wob=0)


def raised_deck(a, cx, top, L, W, prof, t0, t1, rail=0.88, color=None):
    """A forecastle / quarterdeck: a lighter, raised stretch of deck between
    t0 and t1, its edge marked by a step and a rail line."""
    color = color or tint(DECK, 0.12)
    p = [(t, w * rail) for t, w in prof]
    tt = [t0 + (t1 - t0) * k / 16 for k in range(17)]
    ws = [float(np.interp(t, [q[0] for q in p], [q[1] for q in p])) for t in tt]
    left = [(cx - W / 2 * w, top + L * t) for t, w in zip(tt, ws)]
    right = [(cx + W / 2 * w, top + L * t) for t, w in zip(tt, ws)]
    pts = chaikin(left + right[::-1], True, 2)
    soft_shadow(a, pts, dx=0, dy=10 if t0 > 0.3 else -10, alpha=0.35, blur=6)
    n = max(6, int(W / 34))
    big_shape(a, pts, color, outline=DETAIL * 1.6, wob=0.3, depth=8, shade_k=0.35, light_k=0.2, ao=0.3, detail=lambda art, path: boards(art, cx - W / 2, top + L * t0, cx + W / 2, top + L * t1, color, n, vertical=True))
    edge_y = top + L * (t0 if t0 > 0.3 else t1)
    ew = float(np.interp(t0 if t0 > 0.3 else t1, tt, ws)) * W / 2
    a.ink([(cx - ew + 10, edge_y), (cx + ew - 10, edge_y)], DETAIL * 2.2, color=WOOD_DARK, taper=False)
    for x in np.linspace(cx - ew + 24, cx + ew - 24, 9):  # balusters
        dot(a, x, edge_y, 5, WOOD_DARK)
    return pts


def oars_out(a, cx, ys, half, length, blade=True):
    for y in ys:
        for s in (-1, 1):
            x0, x1 = cx + s * (half - 40), cx + s * (half + length)
            handle(a, x0, y, x1, y + 26, 8, WOOD_LIGHT)
            if blade:
                a.shape(ellipse(x1 + s * 10, y + 28, 24, 10, 16, rot=0.25 * s), WOOD_LIGHT, outline=DETAIL * 1.2, depth=2, mottle=0)


def bench(a, cx, y, half, w=26):
    a.shape(rect(cx - half, y - w / 2, cx + half, y + w / 2), WOOD, outline=DETAIL * 1.3, corner=4, depth=3, detail=lambda art, p: boards(art, cx - half, y - w / 2, cx + half, y + w / 2, WOOD, 1))


def coil(a, x, y, r=26):
    a.shape(ellipse(x, y, r, r, 24), ROPE, outline=DETAIL * 1.3, depth=3, mottle=0, detail=lambda art, p: [art.ink(ellipse(x, y, r * k, r * k, 20), FINE * 1.1, closed=True, color=shade(ROPE, 0.45), alpha=0.8) for k in (0.3, 0.55, 0.8)])


def steering_oar(a, x, y, side=1, L=360):
    handle(a, x, y - 60, x + side * 50, y + L, 14)
    a.shape(ellipse(x + side * 54, y + L, 22, 70, 20, rot=-side * 0.12), WOOD, outline=DETAIL * 1.4, depth=3, mottle=0)


def keelboat(seed=1631):
    """A river keelboat (~60 ft): long, flat and narrow, with a cargo cabin
    amidships, a single mast with its sail furled, poles and a steering oar."""
    L, W = 3000, 680
    w, h = int(W + 300), int(L + 240)
    a = Art(w, h, seed)
    cx, top = w / 2, 80
    prof = [(0, 0.15), (0.02, 0.6), (0.06, 0.88), (0.12, 1.0), (0.9, 1.0), (0.97, 0.9), (1, 0.7)]
    steering_oar(a, cx + 40, top + L * 0.9, 1, 300)
    outer, inner = deck(a, cx, top, L, W, prof, hull=rgb("#7a5a3e"))
    butt_joints(a, cx, top + 60, L - 120, W * 0.85)
    # Cabin: a low plank-roofed house amidships.
    c0, c1 = top + L * 0.42, top + L * 0.74
    soft_shadow(a, rect(cx - W * 0.4, c0, cx + W * 0.4, c1), dx=12, dy=16, alpha=0.35, blur=10)
    for s_ in (-1, 1):  # the roof's two pitches, planked across, a ridge beam between
        x0, x1 = sorted((cx, cx + s_ * W * 0.4))
        a.shape(rect(x0, c0, x1, c1), WOOD if s_ > 0 else WOOD_LIGHT, outline=OUTLINE * 0.9, corner=8, depth=10, light_k=0.3, detail=lambda art, p, x0=x0, x1=x1, s_=s_: boards(art, x0, c0, x1, c1, WOOD if s_ > 0 else WOOD_LIGHT, 12))
    a.shape(rect(cx - 14, c0 - 6, cx + 14, c1 + 6), WOOD_DARK, outline=DETAIL * 1.6, corner=6, depth=4, light_k=0.4)
    a.shape(ellipse(cx + W * 0.2, c0 + 70, 24, 24, 20), IRON, outline=DETAIL * 1.4, depth=3, mottle=0)  # stove pipe
    dot(a, cx + W * 0.2, c0 + 70, 12, INK)
    hatch(a, cx - 80, top + L * 0.3, cx + 80, top + L * 0.38)
    mast(a, cx, top + L * 0.22, W * 1.05)
    shrouds(a, cx, top + L * 0.22, [(cx - W * 0.46, top + L * 0.28), (cx + W * 0.46, top + L * 0.28), (cx, top + 40)])
    for side in (-1, 1):  # poles lying along the rail
        handle(a, cx + side * W * 0.36, top + L * 0.08, cx + side * W * 0.37, top + L * 0.36, 9, WOOD_LIGHT)
    for img, x, y, ww in ((objs.OBJECTS["Crate"](), cx - 120, top + L * 0.82, 200), (objs.OBJECTS["Barrel"](), cx + 120, top + L * 0.8, 150), (objs.OBJECTS["Sack"](seed=33), cx + 60, top + L * 0.86, 140)):
        paste(a, img, x, y, ww, a.rng.uniform(-0.4, 0.4))
    coil(a, cx - 160, top + L * 0.12, 40)
    return autocrop(a.image(), 14)


def dragon_prow(a, x, y, s=1.0, color=WOOD_DARK):
    """A carved dragon head on a curving stem post, seen from above."""
    neck = chaikin([(x, y + 120 * s), (x + 8 * s, y + 50 * s), (x - 4 * s, y)], False, 2)
    a.ink(neck, 44 * s, color=INK, taper=False)
    a.ink(neck, 34 * s, color=color, taper=False)
    head = [(x - 26 * s, y + 6 * s), (x - 16 * s, y - 40 * s), (x, y - 70 * s), (x + 16 * s, y - 40 * s), (x + 26 * s, y + 6 * s)]
    a.shape(head, color, outline=DETAIL * 1.6, corner=8, depth=4, light_k=0.4)
    for k in (-1, 1):
        a.shape([(x + k * 14 * s, y - 6 * s), (x + k * 40 * s, y + 26 * s), (x + k * 18 * s, y + 14 * s)], color, outline=DETAIL * 1.2, corner=2, depth=2, mottle=0)  # horns
        dot(a, x + k * 10 * s, y - 26 * s, 4 * s, rgb("#e0b040"))


def longship(seed=1632):
    """A longship (70 ft): slender, double-ended, a dragon prow, rowing
    benches with the oars run out, painted shields along the rails (red =
    colorable, with the striped sail furled on its yard)."""
    L, W = 3500, 760
    w, h = int(W + 2 * 360), int(L + 260)
    a = Art(w, h, seed)
    cx, top = w / 2, 160
    prof = [(0, 0.0), (0.03, 0.3), (0.1, 0.68), (0.22, 0.92), (0.35, 1.0), (0.65, 1.0), (0.78, 0.92), (0.9, 0.68), (0.97, 0.3), (1, 0.0)]
    rows = [top + L * (0.2 + 0.6 * k / 13) for k in range(14)]
    oars_out(a, cx, rows, W / 2 * 0.95, 290)
    steering_oar(a, cx + W * 0.3, top + L * 0.82, 1, 380)
    deck(a, cx, top, L, W, prof, hull=rgb("#5e4230"), planks=rgb("#b88c5c"))
    for y in rows:
        half = float(np.interp((y - top) / L, [p[0] for p in prof], [p[1] for p in prof])) * W / 2 * 0.86
        bench(a, cx, y + 40, half)
    # Shields along both rails, overlapping, each painted with a boss and
    # a cross (the field is the colorable red).
    for y in np.linspace(top + L * 0.17, top + L * 0.83, 22):
        t = (y - top) / L
        half = float(np.interp(t, [p[0] for p in prof], [p[1] for p in prof])) * W / 2
        for s in (-1, 1):
            x = cx + s * (half - 8)
            col = RED if int((y - top) / 10) % 2 else rgb("#e6dcc4")

            def face(art, p, x=x, y=y, col=col):
                art.ink([(x - 34, y), (x + 34, y)], 7, color=shade(col, 0.35) if col != RED else rgb("#e6dcc4"), alpha=0.9, taper=False)

            a.shape(ellipse(x, y, 34, 34, 28), col, outline=DETAIL * 1.6, depth=4, light_k=0.4, detail=face)
            a.shape(ellipse(x, y, 10, 10, 14), IRON, outline=DETAIL, depth=2, mottle=0)
    mast(a, cx, top + L * 0.46, W * 1.25, r=26, sail=RED)
    with a.clip(to_path(rect(0, 0, w, h))):
        fw = W * 1.25 * 0.88
        for k in range(1, 6, 2):  # cream stripes over the furled red sail
            x = cx - fw / 2 + fw * k / 6
            a.shape(rect(x - 22, top + L * 0.46 + 8, x + 22, top + L * 0.46 + 42), rgb("#e6dcc4"), outline=0, corner=3, depth=1, shade_k=0.2, light_k=0, ao=0, mottle=0)
        a.shape(ellipse(cx, top + L * 0.46, 26, 26, 24), WOOD_DARK, outline=DETAIL * 1.6, depth=4, light_k=0.45, mottle=0)
    shrouds(a, cx, top + L * 0.46, [(cx - W * 0.46, top + L * 0.5), (cx + W * 0.46, top + L * 0.5), (cx, top + L * 0.1), (cx, top + L * 0.86)])
    dragon_prow(a, cx, top - 10, 1.4)
    tail = chaikin([(cx, top + L - 40), (cx + 6, top + L + 30), (cx + 40, top + L + 60), (cx + 52, top + L + 30), (cx + 30, top + L + 20)], False, 3)
    a.ink(tail, 40, color=INK, taper=True)
    a.ink(tail, 30, color=rgb("#5e4230"), taper=True)
    for img, x, y, ww in ((objs.OBJECTS["Chest"](), cx - 110, top + L * 0.12, 190), (objs.OBJECTS["Barrel"](), cx + 100, top + L * 0.13, 140)):
        paste(a, img, x, y, ww, a.rng.uniform(-0.3, 0.3))
    return autocrop(a.image(), 14)


def galley(seed=1633):
    """A war galley (~130 ft, drawn at ~80 ft): long and narrow, a bronze
    ram, a central gangway between the rowers' benches, two banks of
    oars, a stern castle and a mast with its sail furled."""
    L, W = 3700, 860
    w, h = int(W + 2 * 400), int(L + 340)
    a = Art(w, h, seed)
    cx, top = w / 2, 220
    prof = [(0, 0.0), (0.03, 0.4), (0.08, 0.78), (0.16, 0.96), (0.25, 1.0), (0.85, 1.0), (0.94, 0.86), (1, 0.6)]
    rows = [top + L * (0.16 + 0.62 * k / 19) for k in range(20)]
    oars_out(a, cx, rows, W / 2 * 0.98, 330)
    oars_out(a, cx, [y + 46 for y in rows[::2]], W / 2 * 0.98, 240, blade=False)
    # The ram: a bronze beak at the waterline ahead of the bow.
    bronze = rgb("#b4823e")
    a.shape([(cx - 56, top + 120), (cx - 56, top - 40), (cx - 30, top - 130), (cx, top - 210), (cx + 30, top - 130), (cx + 56, top - 40), (cx + 56, top + 120)], bronze, outline=OUTLINE, corner=6, depth=8, light_k=0.5, mottle=0)
    for k in (-1, 1):  # the ram's fins
        a.ink([(cx + k * 50, top - 30), (cx + k * 8, top - 170)], DETAIL * 1.4, color=shade(bronze, 0.45), alpha=0.9, taper=False)
    a.ink([(cx, top - 190), (cx, top + 60)], FINE * 1.4, color=shade(bronze, 0.45))
    deck(a, cx, top, L, W, prof, hull=rgb("#5a3e2c"))
    for y in rows:
        for s in (-1, 1):
            a.shape(rect(cx + s * 80, y + 24, cx + s * (W / 2 * 0.86), y + 50), WOOD, outline=DETAIL * 1.2, corner=4, depth=3)
    # Gangway down the middle.
    g0, g1 = top + L * 0.12, top + L * 0.82
    big_shape(a, rect(cx - 70, g0, cx + 70, g1), WOOD_LIGHT, outline=DETAIL * 2, depth=6, wob=0.3, detail=lambda art, p: boards(art, cx - 70, g0, cx + 70, g1, WOOD_LIGHT, 3, vertical=True))
    raised_deck(a, cx, top, L, W, prof, 0.84, 1.0, color=tint(DECK, 0.15))
    raised_deck(a, cx, top, L, W, prof, 0.0, 0.1)
    mast(a, cx, top + L * 0.38, W * 1.3, r=28)
    shrouds(a, cx, top + L * 0.38, [(cx - W * 0.47, top + L * 0.42), (cx + W * 0.47, top + L * 0.42), (cx, top + L * 0.08)])
    for s in (-1, 1):
        steering_oar(a, cx + s * W * 0.42, top + L * 0.86, s, 360)
    coil(a, cx - 150, top + L * 0.05, 40)
    paste(a, objs.OBJECTS["Barrel"](), cx + 140, top + L * 0.92, 150)
    return autocrop(a.image(), 14)


def ship_wheel(a, x, y, w=230):
    """A ship's wheel from above: seen edge-on as a bar with spokes poking
    out, on its pedestal."""
    a.shape(rect(x - 26, y - 14, x + 26, y + 30), WOOD_DARK, outline=DETAIL * 1.4, corner=6, depth=3)
    a.shape(rect(x - w / 2, y - 10, x + w / 2, y + 10), WOOD, outline=DETAIL * 1.4, corner=8, depth=3, light_k=0.4)
    for k in range(-3, 4):
        a.shape(ellipse(x + k * w / 7, y - 18, 5, 10, 10), WOOD_LIGHT, outline=FINE * 1.3, depth=1, mottle=0)


def capstan(a, x, y, r=46):
    for k in range(6):
        t = k * math.pi / 3
        handle(a, x, y, x + (r + 50) * math.cos(t), y + (r + 50) * math.sin(t), 9, WOOD_LIGHT)
    a.shape(ellipse(x, y, r, r, 30), WOOD_DARK, outline=DETAIL * 1.6, depth=5, light_k=0.4)
    a.ink(ellipse(x, y, r * 0.55, r * 0.55, 24), DETAIL, closed=True, color=shade(WOOD_DARK, 0.45), alpha=0.8)


def sailing_ship(seed=1634, war=False):
    """A three-masted sailing ship (100 ft, drawn at ~80 ft): bowsprit,
    forecastle, main deck with hatches and capstan, quarterdeck with the
    wheel, sails furled on the yards. The warship is beamier, with a
    reinforced ram and ballistae and a catapult on deck."""
    L = 3700
    W = 1160 if war else 1000
    w, h = int(W + 360), int(L + 300)
    a = Art(w, h, seed)
    cx, top = w / 2, 260
    prof = [(0, 0.0), (0.04, 0.42), (0.1, 0.74), (0.2, 0.93), (0.32, 1.0), (0.72, 1.0), (0.88, 0.94), (1, 0.8)]
    # Bowsprit with its jib boom.
    handle(a, cx, top + 200, cx, top - 240, 22, WOOD_DARK)
    shrouds(a, cx, top - 200, [(cx - W * 0.3, top + L * 0.07), (cx + W * 0.3, top + L * 0.07)])
    if war:
        a.shape([(cx - 46, top + 80), (cx, top - 130), (cx + 46, top + 80)], IRON, outline=OUTLINE, corner=6, depth=6, light_k=0.5, mottle=0)
    hull = rgb("#3e3a40") if war else HULL
    deck(a, cx, top, L, W, prof, hull=hull)
    butt_joints(a, cx, top + L * 0.18, L * 0.6, W * 0.85)
    raised_deck(a, cx, top, L, W, prof, 0.0, 0.17)
    raised_deck(a, cx, top, L, W, prof, 0.74, 1.0, color=tint(DECK, 0.18))
    # Stern lanterns and the captain's skylight on the quarterdeck.
    for s in (-1, 1):
        a.shape(ellipse(cx + s * W * 0.3, top + L * 0.985, 22, 22, 18), BRASS, outline=DETAIL * 1.3, depth=2, mottle=0)
        dot(a, cx + s * W * 0.3, top + L * 0.985, 9, rgb("#f6e3a0"))
    a.shape(rect(cx - 90, top + L * 0.86, cx + 90, top + L * 0.92), rgb("#9fc0cc"), outline=DETAIL * 1.4, corner=6, depth=4, light_k=0.5, detail=lambda art, p: [art.ink([(x, top + L * 0.86), (x, top + L * 0.92)], DETAIL, color=WOOD_DARK) for x in (cx - 30, cx + 30)])
    ship_wheel(a, cx, top + L * 0.8)
    hatch(a, cx - 110, top + L * 0.27, cx + 110, top + L * 0.33)
    hatch(a, cx - 130, top + L * 0.5, cx + 130, top + L * 0.58)
    capstan(a, cx, top + L * 0.68)
    masts = [(0.2, 0.95, 24), (0.42, 1.25, 32), (0.63, 1.1, 28)]
    for t, k, r in masts:
        y = top + L * t
        mast(a, cx, y, W * k, r=r)
        shrouds(a, cx, y, [(cx - W * 0.47, y + 120), (cx + W * 0.47, y + 120), (cx - W * 0.47, y + 200), (cx + W * 0.47, y + 200)])
    if war:
        from obj_war import ballista, catapult

        b = ballista()
        for t, s in ((0.1, -1), (0.1, 1), (0.88, -1), (0.88, 1)):
            paste(a, b, cx + s * W * 0.22, top + L * t, 300, -math.pi / 2 + s * 0.5)
        paste(a, catapult(), cx, top + L * 0.36, 280, 0.0)
        for t in np.linspace(0.22, 0.7, 7):  # shield wall / gunwale plates
            for s in (-1, 1):
                x = cx + s * W * 0.465
                a.shape(rect(x - 16, top + L * t - 40, x + 16, top + L * t + 40), IRON, outline=DETAIL * 1.2, corner=4, depth=3, light_k=0.4, mottle=0)
        paste(a, objs.OBJECTS["Barrel"](), cx + W * 0.3, top + L * 0.46, 140)
        paste(a, objs.OBJECTS["Barrel"](), cx - W * 0.3, top + L * 0.62, 140)
    else:
        rb = farm.boat(560, 220, rgb("#7a6a5a"), seats=3, oars=False)(1640)
        paste(a, rb, cx - W * 0.22, top + L * 0.36, 210)
        for img, x, y, ww in ((objs.OBJECTS["Barrel"](), cx + W * 0.3, top + L * 0.45, 140), (objs.OBJECTS["Barrel"](), cx + W * 0.34, top + L * 0.49, 140), (objs.OBJECTS["Crate"](), cx + W * 0.25, top + L * 0.62, 170), (objs.OBJECTS["Sack"](seed=34), cx - W * 0.28, top + L * 0.62, 150)):
            paste(a, img, x, y, ww, a.rng.uniform(-0.4, 0.4))
    coil(a, cx - W * 0.3, top + L * 0.7, 40)
    coil(a, cx + W * 0.3, top + L * 0.72, 40)
    return autocrop(a.image(), 14)


def airship(seed=1636):
    """An airship (100 ft, drawn at ~80 ft): a sleek hull hung from its
    gasbag (not drawn, so the deck stays visible) by cables to the rails,
    with fanned wing-sails on both sides (red = colorable) and propellers
    at the stern."""
    L, W = 3800, 860
    w, h = int(W + 2 * 700), int(L + 360)
    a = Art(w, h, seed)
    cx, top = w / 2, 200
    prof = [(0, 0.0), (0.05, 0.42), (0.14, 0.8), (0.28, 0.98), (0.4, 1.0), (0.7, 1.0), (0.86, 0.9), (1, 0.55)]
    # Wing-sails: ribbed fans out from each side.
    for s in (-1, 1):
        for y0, span, ln in ((top + L * 0.3, 640, L * 0.22), (top + L * 0.62, 520, L * 0.18)):
            root = [(cx + s * W * 0.4, y0), (cx + s * W * 0.4, y0 + ln)]
            ribs = [(cx + s * (W * 0.4 + span * math.sin(t)), y0 + ln * 0.15 + ln * 0.9 * (1 - math.cos(t)) * 0.6) for t in np.linspace(0.35, 1.45, 5)]
            pts = [root[0]] + chaikin(ribs, False, 2) + [root[1]]

            def ribbing(art, p, ribs=ribs, root=root):
                for rx, ry in ribs:
                    art.ink([((root[0][0]), (root[0][1] + root[1][1]) / 2), (rx, ry)], DETAIL * 1.4, color=WOOD_DARK, alpha=0.95, taper=False)

            soft_shadow(a, pts, dx=20, dy=30, alpha=0.2, blur=16)
            a.shape(pts, RED, outline=OUTLINE * 0.9, corner=6, depth=12, light_k=0.4, detail=ribbing)
    # Propellers at the stern on outriggers.
    for s in (-1, 1):
        px, py = cx + s * W * 0.62, top + L * 0.97
        handle(a, cx + s * W * 0.3, top + L * 0.92, px, py, 18, WOOD_DARK)
        for t in (0.3, 0.3 + math.pi):
            a.shape(ellipse(px + 70 * math.cos(t), py + 70 * math.sin(t), 74, 22, 20, rot=t), WOOD_LIGHT, outline=DETAIL * 1.4, depth=3, light_k=0.4, mottle=0)
        a.shape(ellipse(px, py, 24, 24, 18), BRASS, outline=DETAIL * 1.4, depth=3, mottle=0)
    deck(a, cx, top, L, W, prof, hull=rgb("#4e5a66"), planks=rgb("#c8a878"))
    raised_deck(a, cx, top, L, W, prof, 0.82, 1.0, color=rgb("#d6b888"))
    ship_wheel(a, cx, top + L * 0.86)
    # Brass fittings where the gasbag cables meet the rails.
    anchors = []
    for t in np.linspace(0.15, 0.85, 7):
        half = float(np.interp(t, [p[0] for p in prof], [p[1] for p in prof])) * W / 2 * 0.92
        for s in (-1, 1):
            x, y = cx + s * half, top + L * t
            anchors.append((x, y))
            a.ink([(x, y), (x - s * 120, y + 60)], FINE * 1.3, color=INK, alpha=0.6, taper=False)
            a.shape(ellipse(x, y, 14, 14, 14), BRASS, outline=DETAIL * 1.2, depth=2, mottle=0)
    hatch(a, cx - 110, top + L * 0.4, cx + 110, top + L * 0.48)
    # Engine housing amidships: an arcane furnace (glowing core).
    a.shape(rect(cx - 160, top + L * 0.56, cx + 160, top + L * 0.7), IRON, outline=OUTLINE, corner=30, depth=12, light_k=0.4)
    a.shape(ellipse(cx, top + L * 0.63, 70, 70, 30), rgb("#7fc4d8"), outline=DETAIL * 1.6, depth=6, light_k=0.6, mottle=0)
    glow = skia.Path()
    glow.addCircle(cx, top + L * 0.63, 110)
    a.fill_path(glow, rgb("#9fe0f0"), 0.25, blur=30)
    for s in (-1, 1):
        a.shape(ellipse(cx + s * 120, top + L * 0.63, 22, 22, 16), BRASS, outline=DETAIL * 1.2, depth=2, mottle=0)
    a.shape([(cx - 40, top + 40), (cx, top - 160), (cx + 40, top + 40)], BRASS, outline=OUTLINE, corner=6, depth=4, light_k=0.5, mottle=0)  # prow spike
    coil(a, cx - 200, top + L * 0.2, 40)
    paste(a, objs.OBJECTS["Crate"](), cx + 180, top + L * 0.22, 180, 0.2)
    return autocrop(a.image(), 14)


# -- catalog ---------------------------------------------------------------------------------------

_HORSE = rgb("#8a5a3a")

SRD_MOUNTS = {
    "Camel": dressed("horse", 500, rgb("#c9a46a"), 0.3, 1602, hump, muzzle=rgb("#a8845a"), tail_c=rgb("#8a6a44"), hoof=rgb("#6a5a4a")),
    "Draft Horse": lambda: beast("pony", 500, rgb("#6e4a2e"), muzzle=rgb("#4a3424"), blaze=rgb("#efe6d8"), mane=rgb("#e6dcc4"), tail_c=rgb("#e6dcc4"), hoof=rgb("#e0d4c0"))(1603),
    "Gray Draft Horse": lambda: beast("pony", 500, rgb("#a4a09c"), muzzle=rgb("#5a5654"), spots=(rgb("#8a8682"), 9), mane=rgb("#ece6dc"), tail_c=rgb("#ece6dc"), hoof=rgb("#4a4644"))(1604),
    "Elephant": elephant,
    "Mastiff": lambda: beast("dog", 250, rgb("#c49a64"), muzzle=rgb("#3a2e28"), ear_c=rgb("#4a3a30"))(1605),
    "Black Mastiff": lambda: beast("dog", 250, rgb("#3a3436"), muzzle=rgb("#2a2426"), ear_c=rgb("#24201e"))(1606),
    "Mule": lambda: beast("donkey", 400, rgb("#6e5240"), muzzle=rgb("#d8c8b4"), mane=rgb("#3a2a22"), tail_c=rgb("#4a362a"))(1608),
    "Warhorse": dressed("horse", 460, rgb("#3a3436"), 0.0, 1607, barding, muzzle=rgb("#4a4446"), mane=rgb("#24201e"), tail_c=rgb("#24201e")),
    "Military Saddle": military_saddle,
    "Exotic Saddle": exotic_saddle,
    "Feed": feed,
    "Wagon": wagon,
    "Carriage": carriage,
    "Chariot": chariot,
    "Sled": sled,
    "Keelboat": keelboat,
    "Longship": longship,
    "Galley": galley,
    "Sailing Ship": sailing_ship,
    "Warship": lambda: sailing_ship(1635, war=True),
    "Airship": airship,
}

SRD_MOUNTS_COLORABLE = {"Warhorse", "Military Saddle", "Exotic Saddle", "Carriage", "Chariot", "Longship", "Airship"}
