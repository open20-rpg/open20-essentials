"""Camp and travel (batch 12). Top-down, same pen style (red = colorable)."""

import math

import skia

from kit import BRASS, IRON, RED, STONE, WOOD, WOOD_DARK, WOOD_LIGHT, board, dot, scallop, soft_shadow
from obj_craft import handle
from obj_magic import PARCH, glow
from obj_nature import GREEN, GREEN_D, leaf
from objects import campfire
from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

LEATHER = rgb("#8a5a3a")
LEATHER_D = rgb("#6a422a")
CANVAS = rgb("#d8ccb0")
FUR = rgb("#8a6a4e")
ROPE = rgb("#c9b088")
BLANKET = RED


def tie(a, x0, y0, x1, y1):
    a.ink([(x0, y0), (x1, y1)], DETAIL * 2.4, color=INK, taper=False)
    a.ink([(x0, y0), (x1, y1)], DETAIL * 1.4, color=ROPE, taper=False)


# -- shelters ------------------------------------------------------------------------------------


def ridge_tent(seed=1101):
    w, h = 320, 380
    a = Art(w, h, seed)
    # Guy ropes and pegs first, then the two panels (lit one lighter), ridge.
    for x0, y0 in ((14, 30), (w - 14, 30), (14, h - 60), (w - 14, h - 60)):
        a.ink([(x0, y0), (w / 2 + (x0 - w / 2) * 0.8, (y0 + h / 2) / 2)], FINE * 1.3, color=ROPE)
        a.shape(ellipse(x0, y0, 5, 5, 12), WOOD_DARK, outline=FINE * 1.2, depth=1, mottle=0)
    a.shape(rect(40, 40, w / 2, h - 50), tint(RED, 0.06), outline=OUTLINE, corner=4, depth=6, light_k=0.35)
    a.shape(rect(w / 2, 40, w - 40, h - 50), shade(RED, 0.2), outline=OUTLINE, corner=4, depth=6, shade_k=0.6, light_k=0.1)
    a.ink([(w / 2, 40), (w / 2, h - 50)], DETAIL * 2.4)
    # The open flap at the front, the dark inside showing.
    a.shape([(w / 2 - 50, h - 50), (w / 2, h - 120), (w / 2 + 50, h - 50)], rgb("#2a221e"), outline=DETAIL, corner=2, depth=2, shade_k=0, light_k=0, mottle=0)
    a.shape([(w / 2 - 50, h - 50), (w / 2 - 6, h - 112), (w / 2 - 30, h - 20)], tint(RED, 0.1), outline=DETAIL * 1.2, corner=2, depth=2, mottle=0)
    return a.image()


def round_tent(seed=1102):
    s = 380
    a = Art(s, s, seed)
    m = s / 2
    n = 10
    for k in range(n):
        t = 2 * math.pi * k / n
        x0, y0 = m + 168 * math.cos(t), m + 168 * math.sin(t)
        a.ink([(m + 140 * math.cos(t), m + 140 * math.sin(t)), (x0, y0)], FINE * 1.3, color=ROPE)
        a.shape(ellipse(x0, y0, 5, 5, 12), WOOD_DARK, outline=FINE * 1.2, depth=1, mottle=0)
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        seg = [(m, m), (m + 140 * math.cos(t0), m + 140 * math.sin(t0)), (m + 140 * math.cos(t1), m + 140 * math.sin(t1))]
        lit = math.cos((t0 + t1) / 2 + math.pi * 0.75)
        col = RED if k % 2 == 0 else CANVAS
        a.shape(seg, tint(col, 0.15 * lit) if lit > 0 else shade(col, -0.2 * lit), outline=DETAIL, corner=0, wob=0.2, depth=1, shade_k=0, light_k=0, ao=0, mottle=0.03)
    a.ink([(m + 140 * math.cos(t), m + 140 * math.sin(t)) for t in [2 * math.pi * k / n for k in range(n)]], OUTLINE * 0.85, closed=True, wob=0.2)
    a.shape(ellipse(m, m, 16, 16, 24), WOOD_DARK, outline=DETAIL * 1.3, depth=3, mottle=0)
    return a.image()


def tarp_shelter(seed=1103):
    w, h = 360, 280
    a = Art(w, h, seed)
    for x, y in ((20, 20), (w - 20, 20), (20, h - 20), (w - 20, h - 20)):
        a.ink([(x, y), (w / 2 + (x - w / 2) * 0.82, h / 2 + (y - h / 2) * 0.82)], FINE * 1.3, color=ROPE)
        a.shape(ellipse(x, y, 5, 5, 12), WOOD_DARK, outline=FINE * 1.2, depth=1, mottle=0)
    tarp = [(40, 40), (w - 40, 40), (w - 30, h - 40), (30, h - 40)]
    a.shape(tarp, rgb("#6f8a5a"), outline=OUTLINE, corner=4, depth=8, light_k=0.3, detail=lambda art, p: [art.ink([(40, y), (w - 40, y + 4)], FINE, color=shade(rgb("#6f8a5a"), 0.45), alpha=0.6) for y in (100, 160, 220)])
    a.ink([(w / 2, 40), (w / 2 + 4, h - 40)], DETAIL * 1.6, color=shade(rgb("#6f8a5a"), 0.5))
    return a.image()


def lean_to(seed=1104):
    """A lean-to from above: a sloping roof of leafy branches laid over poles,
    its open front (bottom) showing the pole ends and a dark gap under it."""
    w, h = 380, 280
    a = Art(w, h, seed)
    a.shape(rect(30, h - 70, w - 30, h - 30), rgb("#2e2622"), outline=DETAIL, corner=4, depth=4, shade_k=0, light_k=0, ao=0.4)
    for k in range(7):
        x = 40 + k * 50
        handle(a, x, 30, x + 4, h - 40, 12, WOOD_DARK)
    handle(a, 16, h - 46, w - 16, h - 46, 16, WOOD)  # front beam
    roof = rect(24, 24, w - 24, h - 56)
    a.shape(roof, GREEN_D, outline=OUTLINE, corner=10, depth=8, light_k=0.2)
    with a.clip(to_path(roof)):
        for _ in range(120):
            x, y = a.rng.uniform(24, w - 24), a.rng.uniform(24, h - 56)
            k = (y - 24) / (h - 80)  # lower = nearer the open front, lit
            leaf(a, x, y, a.rng.uniform(26, 38), vary(a.rng, mix(GREEN_D, GREEN, 0.3 + 0.6 * k), 0.06), ang=math.pi / 2 + a.rng.uniform(-0.6, 0.6), vein=False, outline=FINE)
    a.ink(roof, OUTLINE, closed=True, wob=0.4)
    for k in range(7):
        x = 40 + k * 50
        a.shape(ellipse(x + 4, h - 46, 8, 8, 16), WOOD_LIGHT, outline=DETAIL, depth=1, mottle=0)
    return a.image()


def sleeping_bag(seed=1111):
    w, h = 200, 460
    a = Art(w, h, seed)

    def quilting(art, p):
        for y in range(80, h - 30, 40):
            art.ink([(28, y), (w - 28, y + 4)], FINE * 1.3, color=shade(BLANKET, 0.45), alpha=0.8)

    a.shape(rect(18, 40, w - 18, h - 14), BLANKET, corner=40, depth=10, light_k=0.35, detail=quilting)
    a.shape(rect(36, 50, w - 36, 130), CANVAS, outline=DETAIL * 1.3, corner=26, depth=6)  # pillow / hood
    a.shape(rect(18, 120, w - 18, 160), tint(BLANKET, 0.2), outline=DETAIL * 1.2, corner=10, depth=5)  # folded top
    return a.image()


def sleeping_fur(seed=1112):
    w, h = 260, 400
    a = Art(w, h, seed)
    pts = blob(w / 2, h / 2, 110, a.rng, 14, 0.1, ry=180)

    def hair(art, p):
        for _ in range(240):
            x, y = art.rng.uniform(20, w - 20), art.rng.uniform(20, h - 20)
            if p.contains(x, y):
                t = math.atan2(y - h / 2, x - w / 2)
                art.ink([(x, y), (x + 9 * math.cos(t), y + 9 * math.sin(t))], FINE, color=shade(FUR, art.rng.uniform(0.3, 0.5)), alpha=0.6, wob=0.1)

    a.shape(pts, FUR, smooth=True, depth=10, light_k=0.3, detail=hair)
    return a.image()


def blanket_roll(seed=1113):
    w, h = 300, 120
    a = Art(w, h, seed)
    a.shape(rect(20, 20, w - 20, h - 20), BLANKET, corner=36, depth=8, light_k=0.4)
    a.shape(ellipse(w - 30, h / 2, 16, 40, 32), tint(BLANKET, 0.15), outline=DETAIL * 1.2, depth=3, mottle=0)
    sp = [(w - 30 + (3 + 1.2 * t) * 0.4 * math.cos(t), h / 2 + (3 + 1.2 * t) * math.sin(t)) for t in [k * 0.25 for k in range(110)]]
    a.ink(sp, FINE * 1.1, color=shade(BLANKET, 0.5), alpha=0.85)
    for x in (90, 190):
        tie(a, x, 18, x + 4, h - 18)
    return a.image()


# -- gear -----------------------------------------------------------------------------------------


def backpack(seed=1121):
    w, h = 200, 240
    a = Art(w, h, seed)
    body = rect(26, 30, w - 26, h - 20)
    a.shape(body, LEATHER, corner=24, depth=10, light_k=0.35)
    a.shape(rect(40, 40, w - 40, 120), LEATHER_D, outline=DETAIL * 1.3, corner=16, depth=5)  # top flap
    for x in (70, w - 70):
        a.ink([(x, 110), (x, 134)], DETAIL * 1.6, color=rgb("#4a2e1e"))
        a.shape(rect(x - 6, 128, x + 6, 140), BRASS, outline=FINE * 1.2, corner=2, depth=1, mottle=0)
    a.shape(rect(20, 160, 50, h - 30), LEATHER_D, outline=DETAIL, corner=8, depth=3)  # side pocket
    blanket = rect(30, 10, w - 30, 46)
    a.shape(blanket, BLANKET, outline=DETAIL * 1.2, corner=16, depth=4, light_k=0.4)
    return a.image()


def satchel(seed=1122):
    w, h = 220, 180
    a = Art(w, h, seed)
    a.ink(chaikin([(30, 60), (10, 140), (110, 172), (210, 140), (190, 60)], False, 2), DETAIL * 2.4, color=INK)
    a.ink(chaikin([(30, 60), (10, 140), (110, 172), (210, 140), (190, 60)], False, 2), DETAIL * 1.4, color=LEATHER_D)
    a.shape(rect(30, 30, w - 30, 130), LEATHER, corner=14, depth=8, light_k=0.35)
    a.shape(chaikin([(32, 34), (w - 32, 34), (w - 40, 96), (w / 2, 112), (40, 96)], True, 1), LEATHER_D, outline=DETAIL * 1.2, corner=0, depth=4)
    a.shape(rect(w / 2 - 8, 96, w / 2 + 8, 114), BRASS, outline=FINE * 1.2, corner=2, depth=1, mottle=0)
    return a.image()


def saddlebags(seed=1123):
    w, h = 320, 160
    a = Art(w, h, seed)
    a.shape(rect(110, 20, w - 110, h - 20), LEATHER_D, outline=DETAIL * 1.3, corner=8, depth=4)
    for x0 in (14, w - 124):
        a.shape(rect(x0, 30, x0 + 110, h - 30), LEATHER, corner=18, depth=8, light_k=0.35)
        a.shape(rect(x0 + 8, 36, x0 + 102, 74), LEATHER_D, outline=DETAIL * 1.1, corner=12, depth=4)
        a.shape(rect(x0 + 49, 66, x0 + 61, 80), BRASS, outline=FINE * 1.2, corner=2, depth=1, mottle=0)
    return a.image()


def saddle(seed=1124):
    w, h = 260, 320
    a = Art(w, h, seed)
    a.shape(rect(20, 40, w - 20, h - 40), BLANKET, outline=DETAIL * 1.3, corner=12, depth=4, light_k=0.3)  # saddle blanket
    seat = chaikin([(w / 2, 30), (w - 50, 80), (w - 40, 190), (w / 2, h - 40), (40, 190), (50, 80)], True, 2)
    a.shape(seat, LEATHER, depth=10, light_k=0.45)
    a.shape(ellipse(w / 2, 60, 22, 18, 28), LEATHER_D, outline=DETAIL * 1.2, depth=4, light_k=0.4)  # pommel
    a.ink(chaikin([(70, 150), (w / 2, 130), (w - 70, 150)], False, 2), FINE * 1.3, color=shade(LEATHER, 0.45))
    for x in (30, w - 30):
        a.ink([(x, 150), (x, 220)], DETAIL * 1.4, color=LEATHER_D)
        a.shape(rect(x - 14, 216, x + 14, 236), IRON, outline=DETAIL, corner=4, depth=2, mottle=0)  # stirrups
    return a.image()


def waterskin(seed=1125):
    w, h = 140, 200
    a = Art(w, h, seed)
    a.shape(blob(w / 2, h / 2 + 14, 52, a.rng, 9, 0.06, ry=70), LEATHER, smooth=True, depth=8, light_k=0.4)
    a.shape(rect(w / 2 - 12, 18, w / 2 + 12, 56), LEATHER_D, outline=DETAIL * 1.2, corner=6, depth=3)
    a.shape(ellipse(w / 2, 20, 10, 8, 20), WOOD_LIGHT, outline=DETAIL, depth=2, mottle=0)
    a.ink(chaikin([(w / 2 - 12, 40), (10, 90), (w / 2 + 20, 170)], False, 2), DETAIL * 1.2, color=ROPE)
    return a.image()


def camp_map(seed=1126):
    w, h = 320, 240
    a = Art(w, h, seed)
    sheet = [(20, 30), (w - 24, 20), (w - 14, h - 26), (30, h - 18)]

    def drawn(art, p):
        art.ink(chaikin([(60, 170), (120, 120), (180, 140), (260, 70)], False, 2), DETAIL, color=rgb("#a8483a"), alpha=0.9)  # route
        art.ink(chaikin([(40, 80), (90, 60), (150, 80), (200, 50)], False, 2), FINE * 1.3, color=rgb("#4f74a8"), alpha=0.9)  # river
        for x, y in ((100, 180), (130, 190), (220, 170)):
            art.ink([(x - 10, y + 6), (x, y - 8), (x + 10, y + 6)], FINE * 1.3, color=rgb("#6a5a4a"), alpha=0.9)  # mountains
        art.ink([(258, 62), (270, 78)], DETAIL, color=rgb("#a8483a"))
        art.ink([(270, 62), (258, 78)], DETAIL, color=rgb("#a8483a"))

    soft_shadow(a, sheet, dx=4, dy=5)
    a.shape(sheet, PARCH, outline=DETAIL * 1.2, corner=3, depth=3, detail=drawn)
    for x, y in ((24, 34), (w - 28, 24), (w - 18, h - 30), (34, h - 22)):
        a.shape(blob(x, y, 14, a.rng, 7, 0.2), STONE, outline=DETAIL, smooth=True, depth=3, light_k=0.4, mottle=0)
    return a.image()


# -- camp kitchen & seats -----------------------------------------------------------------------------


def cooking_fire(seed=1131):
    s = 320
    img = campfire(seed)
    a = Art(s, s, seed)
    import numpy as np

    a.c.drawImage(skia.Image.fromarray(np.asarray(img), colorType=skia.kRGBA_8888_ColorType), 0, 0)
    m = s / 2
    # Tripod legs out to three sides, the pot hanging in the middle.
    for t in (math.pi * 0.2, math.pi * 0.9, math.pi * 1.55):
        handle(a, m, m, m + 148 * math.cos(t), m + 148 * math.sin(t), 10, WOOD_DARK)
    a.shape(ellipse(m, m, 46, 46, 48), rgb("#3a3a40"), outline=DETAIL * 1.4, depth=6, light_k=0.45)
    a.shape(ellipse(m, m, 34, 34, 40), rgb("#9a6a3a"), outline=DETAIL, depth=5, shade_k=0, light_k=0.3, ao=0.4, detail=lambda art, p: [dot(art, m + art.rng.uniform(-20, 20), m + art.rng.uniform(-20, 20), art.rng.uniform(3, 6), rgb("#c98a4a")) for _ in range(6)])
    a.ink([(m - 46, m), (m + 46, m)], DETAIL * 1.2, color=IRON)
    return a.image(grain=0)


def frying_pan(seed=1132):
    w, h = 280, 160
    a = Art(w, h, seed)
    handle(a, 150, h / 2, w - 20, h / 2 - 10, 14, rgb("#3a3a40"))
    a.shape(ellipse(84, h / 2, 70, 70, 64), rgb("#3a3a40"), depth=6, light_k=0.4)
    a.shape(ellipse(84, h / 2, 56, 56, 56), rgb("#2a2a2e"), outline=DETAIL, depth=4, shade_k=0, light_k=0, ao=0.4)
    for x, y in ((70, 70), (100, 90)):
        a.shape(ellipse(x, y, 18, 16, 28), rgb("#f3eee2"), outline=FINE * 1.3, depth=1, mottle=0, shade_k=0, light_k=0)
        a.shape(ellipse(x + 2, y + 1, 7, 7, 16), rgb("#f2b234"), outline=FINE, depth=1, mottle=0, light_k=0.5)
    a.shape(ellipse(70, 104, 20, 9, 20, rot=0.4), rgb("#a8552f"), outline=FINE * 1.3, depth=2, mottle=0)
    return a.image()


def log_seat(seed=1133):
    w, h = 400, 120
    a = Art(w, h, seed)
    a.shape(rect(14, 24, w - 14, h - 24), rgb("#7a5a3e"), corner=34, depth=10, light_k=0.3, detail=lambda art, p: [art.ink([(30 + art.rng.uniform(0, 40), y), (w - 30 - art.rng.uniform(0, 40), y + art.rng.uniform(-2, 2))], FINE * 1.1, color=shade(rgb("#7a5a3e"), 0.55), alpha=0.7) for y in (44, 60, 76)])
    a.shape(rect(40, 36, w - 40, 62), WOOD_LIGHT, outline=DETAIL, corner=8, depth=3, light_k=0.3)  # flat top cut for sitting
    for x in (14, w - 14):
        a.shape(ellipse(x + (20 if x < w / 2 else -20), h / 2, 14, 36, 32), WOOD_LIGHT, outline=DETAIL * 1.2, depth=3, mottle=0)
    return a.image()


def camp_stool(seed=1134):
    """A folding camp stool from above: two rails with the canvas seat slung
    between them, the crossed legs showing at the ends."""
    w, h = 180, 160
    a = Art(w, h, seed)
    for y0, y1 in ((20, h - 20), (h - 20, 20)):
        handle(a, 30, y0, w - 30, y1, 9, WOOD_DARK)
    for x in (30, w - 30):
        handle(a, x, 14, x, h - 14, 11, WOOD)
    a.shape(rect(30, 34, w - 30, h - 34), CANVAS, outline=DETAIL * 1.3, corner=4, depth=4, light_k=0.3, detail=lambda art, p: art.ink([(34, h / 2 + 6), (w / 2, h / 2 + 12), (w - 34, h / 2 + 6)], FINE * 1.3, color=shade(CANVAS, 0.4), alpha=0.8))
    return a.image()


def firewood_bundle(seed=1135):
    w, h = 300, 140
    a = Art(w, h, seed)
    for k in range(5):
        y = 34 + k * 18
        x0, x1 = 20 + a.rng.uniform(0, 20), w - 20 - a.rng.uniform(0, 20)
        a.shape(rect(x0, y - 11, x1, y + 11), vary(a.rng, rgb("#7a5a3e"), 0.06), outline=DETAIL * 1.2, corner=10, depth=3)
        a.shape(ellipse(x1 - 6, y, 6, 10, 16), WOOD_LIGHT, outline=FINE * 1.2, depth=1, mottle=0)
    for x in (100, 200):
        tie(a, x, 18, x + 4, h - 18)
    return a.image()


CAMP = {
    "Ridge Tent": ridge_tent,
    "Round Tent": round_tent,
    "Tarp Shelter": tarp_shelter,
    "Lean-to": lean_to,
    "Sleeping Bag": sleeping_bag,
    "Sleeping Fur": sleeping_fur,
    "Blanket Roll": blanket_roll,
    "Backpack": backpack,
    "Satchel": satchel,
    "Saddlebags": saddlebags,
    "Saddle": saddle,
    "Waterskin": waterskin,
    "Map on the Ground": camp_map,
    "Cooking Fire": cooking_fire,
    "Frying Pan": frying_pan,
    "Log Seat": log_seat,
    "Camp Stool": camp_stool,
    "Firewood Bundle": firewood_bundle,
}

CAMP_COLORABLE = {"Ridge Tent", "Round Tent", "Sleeping Bag", "Blanket Roll", "Backpack", "Saddle"}
