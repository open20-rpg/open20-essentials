"""SRD 5.2.1 armor, shields, clothes and magic wearables. Top-down, as they
would lie on a floor or a table: body armor laid flat with the shoulders
up, full plate laid out piece by piece, cloaks and robes spread open,
boots, gloves and bracers in pairs. Same pen style as the rest."""

import math

import skia

from kit import BRASS, IRON, RED, WOOD, dot, ring, scallop, soft_shadow
from obj_craft import STEEL, rot_pts
from obj_magic import glow
from pen import DETAIL, FINE, INK, Art, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary

O = DETAIL * 2.0  # outline weight for small gear (same as weapons)
V = 0.08
GOLD = rgb("#e2c068")
SILVER = rgb("#c9ced6")
LEATHER = rgb("#8a5a3a")
LEATHER_D = rgb("#6a422a")
LINEN = rgb("#d9cba6")
HIDE = rgb("#94714c")
FUR_D = rgb("#6e5136")
ADAMANT = rgb("#4c5a55")
MITHRAL = rgb("#dfe6ee")
ELVEN = rgb("#bccdbb")
BRONZE = rgb("#b07a3c")
DEMON = rgb("#3b3338")
EMBER = rgb("#ef6a2c")
GHOST = rgb("#bfe0f0")
ARCANE = rgb("#9c7ce0")
SKYGLOW = rgb("#8fd0ff")
WHITE = rgb("#ece6d8")
GREEN_CLOTH = rgb("#5f7a4a")
BLUE_CLOTH = rgb("#33496e")
BLACK_CLOTH = rgb("#2f2b30")
GEMS = {"ruby": rgb("#c8323c"), "sapphire": rgb("#3a64c8"), "emerald": rgb("#3aa860"), "amethyst": rgb("#8a4cc8"), "diamond": rgb("#eef4fa"), "topaz": rgb("#e8a83a"), "opal": rgb("#bfe8e0")}


# -- geometry helpers ------------------------------------------------------------------------------


def mirrored(left, bottom, top):
    """A symmetric outline from its left half (top center -> bottom center,
    down the left side): left + bottom + the right half + top."""
    right = [(-x, y) for x, y in reversed(left)]
    return left + [bottom] + right + [top]


def place(pts, cx, cy, s=1.0, sy=None):
    sy = s if sy is None else sy
    return [(cx + x * s, cy + y * sy) for x, y in pts]


def flip(pts, cx):
    return [(2 * cx - x, y) for x, y in pts]


def body_pts(length=1.0, flare=0.0, neck=1.0):
    """A torso piece laid flat, shoulders up (unit: ~200 wide)."""
    left = [(-18 * neck, -100), (-34 * neck, -118), (-70, -112), (-96, -96), (-98, -72), (-78, -50), (-70, 0), (-74, 50 * length), (-80 - flare, 95 * length), (-40 - flare * 0.4, 108 * length)]
    return mirrored(left, (0, 110 * length), (0, -94))


SHORT_SLEEVE = [(-88, -106), (-128, -86), (-142, -40), (-112, -28), (-82, -56)]
LONG_SLEEVE = [(-88, -106), (-130, -88), (-158, -4), (-164, 56), (-130, 62), (-120, 2), (-82, -50)]


def gem(a, x, y, r, color, glow_alpha=0.0):
    if glow_alpha:
        glow(a, x, y, r * 3, tint(color, 0.3), glow_alpha)
    a.shape(ellipse(x, y, r, r, 20), color, outline=FINE * 1.4, corner=0, wob=0.1, depth=max(1.5, r * 0.3), light_k=0.6, mottle=0)
    dot(a, x - r * 0.35, y - r * 0.35, max(1.2, r * 0.25), tint(color, 0.8))


def star(a, x, y, r, color, alpha=1.0, points=4):
    pts = []
    for k in range(points * 2):
        t = math.pi * k / points - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.35
        pts.append((x + rr * math.cos(t), y + rr * math.sin(t)))
    a.fill_path(to_path(pts), color, alpha)


def rune_marks(a, cx, cy, R, n, color, width=FINE * 1.3, alpha=0.9):
    """Little angular glyphs around a circle."""
    for k in range(n):
        t = 2 * math.pi * k / n
        x, y = cx + R * math.cos(t), cy + R * math.sin(t)
        s = 5
        kind = k % 3
        if kind == 0:
            pts = [(x - s, y + s), (x, y - s), (x + s, y + s)]
        elif kind == 1:
            pts = [(x - s, y - s), (x + s, y), (x - s, y + s)]
        else:
            pts = [(x, y - s), (x, y + s), (x + s, y)]
        a.ink(pts, width, color=color, alpha=alpha, wob=0.2, taper=False)


# -- surface details (drawn clipped inside a shape) ------------------------------------------------


def rings_detail(color, r=4.2, sp=None, width=1.5, metal=None):
    """Mail: rows of interlocking rings (one stroked path: fast)."""

    def d(art, path):
        b = path.getBounds()
        step = sp or r * 1.7
        p = skia.Path()
        y, row = b.top(), 0
        while y < b.bottom() + r:
            x = b.left() + (step / 2 if row % 2 else 0)
            while x < b.right() + r:
                p.addCircle(x, y, r)
                x += step
            y += step * 0.78
            row += 1
        if metal:
            art.stroke_path(p, INK, width + 2.2, 0.9)
            art.stroke_path(p, metal, width, 1.0)
        else:
            art.stroke_path(p, shade(color, 0.55), width, 0.85)
            hl = skia.Path(p)
            hl.offset(-0.8, -0.8)
            art.stroke_path(hl, tint(color, 0.55), width * 0.5, 0.5)

    return d


def scales_detail(color, w=20, h=15, var=0.07):
    """Overlapping scales hanging down: upper rows drawn last, over the
    rounded bottoms of the rows below."""

    def d(art, path):
        b = path.getBounds()
        rows = []
        y, k = b.top() - 4, 0
        while y < b.bottom() + h:
            rows.append((y, k))
            y += h
            k += 1
        for y, k in reversed(rows):
            x = b.left() - (w / 2 if k % 2 else 0)
            while x < b.right() + w:
                pts = [(x - w / 2, y - h), (x + w / 2, y - h)] + [(x + w / 2 * math.cos(t), y + w / 2 * 0.95 * math.sin(t)) for t in [i * math.pi / 10 for i in range(11)]]
                p = to_path(pts)
                c = vary(art.rng, color, var)
                art.fill_path(p, c)
                hl = to_path([(x - w / 2 + 3, y - 2)] + [(x + (w / 2 - 3) * math.cos(t), y + (w / 2 - 3) * 0.9 * math.sin(t)) for t in [math.pi - i * 0.18 for i in range(6)]], closed=False)
                art.stroke_path(hl, tint(c, 0.5), 1.4, 0.6)
                art.stroke_path(p, shade(c, 0.6), 1.7, 0.9)
                x += w

    return d


def quilt_detail(color, sp=20):
    def d(art, path):
        b = path.getBounds()
        span = b.width() + b.height()
        for k in range(int(-span / sp), int(span / sp) + 1):
            x0 = b.left() + k * sp
            for sgn in (1, -1):
                pts = [(x0, b.top()), (x0 + sgn * b.height(), b.bottom())]
                art.ink(pts, FINE * 1.1, color=shade(color, 0.45), alpha=0.75, taper=False, wob=0.4)

    return d


def studs_detail(metal=BRASS, sp=22, r=3.6):
    def d(art, path):
        b = path.getBounds()
        y, row = b.top() + sp / 2, 0
        while y < b.bottom():
            x = b.left() + (sp / 2 if row % 2 else sp)
            while x < b.right():
                if path.contains(x, y):
                    dot(art, x + 1, y + 1.5, r + 1.4, INK, 0.8)
                    dot(art, x, y, r, metal)
                    dot(art, x - r * 0.35, y - r * 0.35, r * 0.4, tint(metal, 0.7))
                x += sp
            y += sp * 0.85
            row += 1

    return d


def stitch_line(a, pts, color, width=FINE * 1.1, gap=7):
    """A row of stitches (short dashes) along a polyline."""
    q = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / gap))
        for i in range(n):
            if i % 2 == 0:
                t0, t1 = i / n, (i + 1) / n
                q.append([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)])
    for seg in q:
        a.ink(seg, width, color=color, alpha=0.85, taper=False, wob=0)


def leather_detail(color, cx, cy, s, length=1.0):
    def d(art, path):
        c = shade(color, 0.5)
        art.ink([(cx, cy - 92 * s), (cx, cy + 108 * s * length)], DETAIL * 0.9, color=c, alpha=0.8, wob=0.4)
        art.ink(chaikin([(cx - 74 * s, cy - 30 * s), (cx, cy - 10 * s), (cx + 74 * s, cy - 30 * s)], False, 2), DETAIL * 0.9, color=c, alpha=0.8)
        art.ink(chaikin([(cx - 74 * s, cy + 50 * s * length), (cx, cy + 60 * s * length), (cx + 74 * s, cy + 50 * s * length)], False, 2), DETAIL * 0.9, color=c, alpha=0.8)
        for sx in (-1, 1):
            stitch_line(art, [(cx + sx * 6 * s, cy - 88 * s), (cx + sx * 6 * s, cy + 100 * s * length)], tint(color, 0.35))
        grain = shade(color, 0.3)
        for _ in range(10):
            x, y = cx + art.rng.uniform(-70, 70) * s, cy + art.rng.uniform(-90, 100) * s
            art.ink([(x, y), (x + art.rng.uniform(6, 14), y + art.rng.uniform(-3, 3))], FINE * 0.8, color=grain, alpha=0.4)

    return d


def plate_detail(color, cx, cy, s, faulds=3, length=1.0, ridge=True):
    """A plate cuirass: the medial ridge catching the light, a rolled neck
    edge and the horizontal lames of the faulds at the bottom."""

    def d(art, path):
        if ridge:
            art.ink([(cx, cy - 90 * s), (cx, cy + 40 * s)], DETAIL * 1.0, color=shade(color, 0.45), alpha=0.8, wob=0.2)
            art.ink([(cx - 4, cy - 86 * s), (cx - 4, cy + 30 * s)], DETAIL * 1.3, color=tint(color, 0.6), alpha=0.7, wob=0.2)
        art.ink(chaikin([(cx - 40 * s, cy - 112 * s), (cx, cy - 86 * s), (cx + 40 * s, cy - 112 * s)], False, 2), DETAIL * 1.1, color=shade(color, 0.5), alpha=0.85)
        art.ink([(cx - 50 * s, cy - 60 * s), (cx - 34 * s, cy + 10 * s)], DETAIL * 2.2, color=tint(color, 0.7), alpha=0.45, wob=0.3)
        for k in range(faulds):
            y = cy + (52 + k * 20) * s * length
            art.ink(chaikin([(cx - 100 * s, y - 6), (cx, y + 6 * s), (cx + 100 * s, y - 6)], False, 2), DETAIL * 1.1, color=shade(color, 0.55), alpha=0.9)
            for x in (cx - 56 * s, cx + 56 * s):
                dot(art, x, y + 5 * s, 2.6, tint(color, 0.5))

    return d


# -- armor pieces --------------------------------------------------------------------------------


def torso(a, cx, cy, s, color, detail=None, length=1.0, flare=0.0, sleeves=None, sleeve_detail=None, outline=None, **kw):
    """Sleeves (behind), the torso and the darker inside of the back seen
    through the neck opening."""
    if sleeves:
        for side in (1, -1):
            pts = place([(x * side, y) for x, y in sleeves], cx, cy, s)
            a.shape(pts, shade(color, 0.08), corner=8, depth=6, light_k=0.3, detail=sleeve_detail, **({"outline": outline} if outline else {}))
    pts = place(body_pts(length, flare), cx, cy, s)
    path = a.shape(pts, color, corner=10, depth=9, light_k=0.4, detail=detail, **({"outline": outline} if outline else {}), **kw)
    a.shape(place(ellipse(0, -104, 28, 10, 28), cx, cy, s), shade(color, 0.55), outline=DETAIL * 1.1, corner=0, depth=3, shade_k=0, light_k=0, ao=0.4, mottle=0)
    return path


def pauldron(a, x, y, s, color, side, lames=3, trim=None):
    pts = ellipse(x, y, 44 * s, 38 * s, 40, rot=side * -0.35)

    def d(art, p):
        for k in range(1, lames + 1):
            r = 1 - k * 0.24
            art.ink(chaikin([(x + side * 40 * s * r, y - 30 * s * r), (x + side * 46 * s * r, y + 2), (x + side * 30 * s * r, y + 32 * s * r)], False, 2), FINE * 1.4, color=shade(color, 0.5), alpha=0.85)
        if trim:
            art.ink(ellipse(x, y, 40 * s, 34 * s, 40, rot=side * -0.35), DETAIL * 1.2, closed=True, color=trim, alpha=0.9)

    a.shape(pts, color, outline=O, depth=6, light_k=0.55, mottle=0, var=V, detail=d)


def tassets(a, cx, y, s, color, n=2):
    for side in (-1, 1):
        x = cx + side * 44 * s
        for k in range(n):
            yy = y + k * 18 * s
            a.shape(rect(x - 34 * s, yy, x + 34 * s, yy + 26 * s), color, outline=O * 0.9, corner=7, depth=4, light_k=0.5, mottle=0, var=V)


def hand_pts():
    """A gloved right hand, palm down, fingers up (unit: ~90 wide)."""
    return [(-28, 60), (-30, 12), (-50, -8), (-54, -22), (-44, -27), (-28, -12), (-27, -32), (-29, -70), (-20, -75), (-13, -70), (-11, -42), (-8, -80), (0, -84), (7, -80), (7, -44), (12, -76), (20, -78), (25, -72), (23, -40), (28, -62), (35, -63), (39, -57), (33, -10), (31, 60)]


def glove(a, cx, cy, s, color, ang=0.0, left=False, cuff=None, metal=False, detail=None):
    pts = place(hand_pts(), cx, cy, s)
    if left:
        pts = flip(pts, cx)
    pts = rot_pts(pts, cx, cy, ang)

    def d(art, p):
        if metal:
            for k in range(3):
                yy = cy + (-30 + k * 16) * s
                art.ink(rot_pts([(cx - 30 * s, yy), (cx + 32 * s, yy)], cx, cy, ang), FINE * 1.5, color=shade(color, 0.5), alpha=0.85)
            for fx in (-20, -2, 15, 30):
                fx = -fx if left else fx
                art.ink(rot_pts([(cx + fx * s * 0.9, cy - 44 * s), (cx + fx * s * 0.9, cy - 36 * s)], cx, cy, ang), FINE * 1.5, color=shade(color, 0.5), alpha=0.8)
        if detail:
            detail(art, p)

    a.shape(pts, color, outline=O, corner=4, depth=4, light_k=0.5, mottle=0 if metal else 0.05, var=V, detail=d)
    if cuff:
        cpts = rot_pts(place([(-36, 38), (36, 38), (42, 74), (-42, 74)], cx, cy, s), cx, cy, ang)
        a.shape(cpts, cuff, outline=O, corner=6, depth=4, light_k=0.45, mottle=0, var=V)


def helm_top(a, x, y, r, color, ridge=True, visor=True, trim=None):
    a.shape(ellipse(x, y, r, r * 1.08, 48), color, outline=O, depth=6, light_k=0.55, mottle=0, var=V)
    if ridge:
        a.ink([(x, y - r * 1.02), (x, y + r * 0.9)], DETAIL * 1.4, color=shade(color, 0.45))
    if trim:
        a.ink(ellipse(x, y, r * 0.86, r * 0.92, 48), DETAIL * 1.2, closed=True, color=trim, alpha=0.95)
    if visor:
        a.shape(rect(x - r * 0.58, y + r * 0.5, x + r * 0.58, y + r * 0.72), shade(color, 0.55), outline=FINE * 1.3, corner=4, depth=1, mottle=0)


PLATE_ARM = [(-88, -106), (-128, -90), (-156, -10), (-166, 64), (-128, 70), (-118, 4), (-82, -50)]


def plate_arm_detail(color, cx, cy, s, side):
    """The arm's lames: bands across the rerebrace and vambrace, and the
    couter (elbow cop) where they meet."""

    def d(art, path):
        for k in range(6):
            t = k / 5
            y = cy + (-70 + t * 128) * s
            x0 = cx + side * (96 + t * 22) * s
            x1 = cx + side * (150 + t * 18) * s
            art.ink([(x0, y), (x1, y + 4 * s)], FINE * 1.5, color=shade(color, 0.5), alpha=0.85)
        art.ink([(cx + side * 118 * s, cy - 76 * s), (cx + side * 146 * s, cy + 52 * s)], DETAIL * 1.6, color=tint(color, 0.6), alpha=0.45, wob=0.3)

    return d


def plate_suit(seed, metal=STEEL, trim=None, gems=(), runes=None, spikes=False, seams=None, alpha_ghost=None, aura=None, dent=False, stocky=False):
    """A full plate harness laid flat like the other armors (shoulders up):
    the cuirass with its gorget, big pauldrons, the arms plated all the way
    down to the gauntlets, and long tassets. Unlike half plate, no mail
    shows anywhere. One piece, not a figure of loose parts."""
    w, h = 420, 340
    a = Art(w, h, seed)
    cx, cy = w / 2, 158
    s = 1.0 if not stocky else 1.04
    if aura:
        glow(a, cx, cy + 30, 210, aura, 0.35)
    soft_shadow(a, place(body_pts(0.9), cx, cy, s), dx=5, dy=6)
    for side in (-1, 1):
        pts = place([(x * -side, y) for x, y in PLATE_ARM], cx, cy, s)
        a.shape(pts, shade(metal, 0.06), outline=O, corner=10, depth=6, light_k=0.5, mottle=0, var=V, detail=plate_arm_detail(metal, cx, cy, s, side))
        ex, ey = cx + side * 136 * s, cy + 2 * s
        a.shape(ellipse(ex, ey, 22 * s, 18 * s, 28), tint(metal, 0.08), outline=O, depth=3, light_k=0.6, mottle=0, var=V)
        glove(a, cx + side * 147 * s, cy + 106 * s, 0.6 * s, metal, ang=math.pi, left=side > 0, metal=True)
    tassets(a, cx, cy + 66 * s, 1.08 * s, metal, n=3)
    detail = plate_detail(metal, cx, cy, s, faulds=2)
    torso(a, cx, cy, s, metal, detail=detail, length=0.9, mottle=0, var=V)
    # The gorget: a curved collar plate over the neck opening.
    gorget = place(chaikin([(-52, -108), (0, -84), (52, -108), (46, -92), (0, -70), (-46, -92)], True, 2), cx, cy, s)
    a.shape(gorget, tint(metal, 0.06), outline=O * 0.9, corner=0, depth=3, light_k=0.55, mottle=0, var=V)
    for side in (-1, 1):
        pauldron(a, cx + side * 94 * s, cy - 94 * s, 1.1 * s, metal, side, lames=4, trim=trim)
    if trim:
        a.ink(place(chaikin([(-46, -94), (0, -72), (46, -94)], False, 2), cx, cy, s), DETAIL * 1.4, color=trim)
        a.ink(place([(-74, 46), (74, 46)], cx, cy, s), DETAIL * 1.2, color=trim, alpha=0.9)
    if runes:
        rune_marks(a, cx, cy - 14 * s, 32, 9, runes, alpha=0.95)
    for gx, gy, gc in gems:
        gem(a, cx + gx, cy + gy, 9, gc, 0.35)
    if spikes:
        for side in (-1, 1):
            for k in range(3):
                x0, y0 = cx + side * (108 + k * 12) * s, cy + (-120 + k * 14) * s
                a.shape([(x0 - 7, y0 + 6), (x0 + side * 22, y0 - 16), (x0 + 7, y0 - 4)], shade(metal, 0.2), outline=FINE * 1.6, corner=1, depth=2, mottle=0)
            x0, y0 = cx + side * 150 * s, cy + 30 * s
            a.shape([(x0 - side * 6, y0 - 8), (x0 + side * 26, y0), (x0 - side * 6, y0 + 8)], shade(metal, 0.2), outline=FINE * 1.6, corner=1, depth=2, mottle=0)
    if seams:
        for pts in ([(-30, -50), (-10, -10), (-24, 30)], [(26, -40), (8, 6), (30, 44)], [(-64, 60), (0, 70), (64, 60)]):
            q = place(pts, cx, cy, s)
            a.ink(q, DETAIL * 2.4, color=seams, alpha=0.35)
            a.ink(q, DETAIL * 0.9, color=tint(seams, 0.4), alpha=0.95)
    if dent:
        for x, y in ((-30, -40), (40, 20), (-140, -20), (138, 50)):
            x, y = cx + x * s, cy + y * s
            a.ink([(x - 10, y - 8), (x - 2, y), (x - 6, y + 6), (x + 6, y + 14)], FINE * 1.4, color=INK, alpha=0.85, taper=False)
    img = a.image()
    if alpha_ghost is not None:
        import numpy as np
        from PIL import Image

        arr = np.asarray(img).copy()
        arr[..., 3] = (arr[..., 3].astype(np.float32) * alpha_ghost).astype(np.uint8)
        img = Image.fromarray(arr, "RGBA")
    return img


def body_armor(seed, color, detail_fn, w=320, h=300, s=0.95, length=1.0, flare=0.0, sleeves=None, sleeve_color=None, sleeve_detail_fn=None, extra=None, **kw):
    """One torso piece on its own canvas. detail_fn(cx, cy, s) -> detail."""
    a = Art(w, h, seed)
    cx, cy = w / 2, 140 * s + 6
    soft_shadow(a, place(body_pts(length, flare), cx, cy, s), dx=5, dy=6)
    if sleeves:
        sc = sleeve_color or color
        sd = sleeve_detail_fn(cx, cy, s) if sleeve_detail_fn else None
        for side in (1, -1):
            pts = place([(x * side, y) for x, y in sleeves], cx, cy, s)
            a.shape(pts, shade(sc, 0.06), corner=8, depth=6, light_k=0.3, detail=sd, **kw)
    path = a.shape(place(body_pts(length, flare), cx, cy, s), color, corner=10, depth=9, light_k=0.4, detail=detail_fn(cx, cy, s) if detail_fn else None, **kw)
    a.shape(place(ellipse(0, -104, 28, 10, 28), cx, cy, s), shade(color, 0.6), outline=DETAIL * 1.1, corner=0, depth=3, shade_k=0, light_k=0, ao=0.4, mottle=0)
    if extra:
        extra(a, cx, cy, s, path)
    return a.image()


# -- the 12 armors ---------------------------------------------------------------------------------


def padded(seed=3301):
    return body_armor(seed, RED, lambda cx, cy, s: quilt_detail(RED), sleeves=LONG_SLEEVE, sleeve_detail_fn=lambda cx, cy, s: quilt_detail(RED), w=340, length=1.05, flare=6)


def leather(seed=3302):
    def extra(a, cx, cy, s, path):
        for side in (-1, 1):
            a.shape(ellipse(cx + side * 86 * s, cy - 96 * s, 30 * s, 22 * s, 28, rot=side * -0.4), LEATHER_D, outline=O, depth=4, light_k=0.4, mottle=0.04)
        a.shape(rect(cx - 96 * s, cy + 22 * s, cx + 96 * s, cy + 40 * s), LEATHER_D, outline=O * 0.9, corner=5, depth=3, mottle=0)
        a.shape(rect(cx - 9, cy + 20 * s, cx + 9, cy + 42 * s), BRASS, outline=FINE * 1.4, corner=2, depth=2, mottle=0)

    return body_armor(seed, LEATHER, lambda cx, cy, s: leather_detail(LEATHER, cx, cy, s), extra=extra)


def studded(seed=3303, metal=BRASS, base=LEATHER_D, sheen=None):
    def extra(a, cx, cy, s, path):
        for side in (-1, 1):
            a.shape(ellipse(cx + side * 86 * s, cy - 96 * s, 30 * s, 22 * s, 28, rot=side * -0.4), shade(base, 0.15), outline=O, depth=4, light_k=0.4, mottle=0.04, detail=studs_detail(metal, sp=14, r=2.8))
        if sheen:
            for k in range(3):
                a.ink(chaikin([(cx - 80 * s, cy - 40 * s + k * 50 * s), (cx, cy - 60 * s + k * 50 * s), (cx + 80 * s, cy - 30 * s + k * 50 * s)], False, 2), DETAIL * 2.5, color=sheen, alpha=0.35)
                for _ in range(4):
                    star(a, cx + a.rng.uniform(-70, 70) * s, cy + a.rng.uniform(-80, 90) * s, 6, tint(sheen, 0.6), 0.9)

    def det(cx, cy, s):
        lt = leather_detail(base, cx, cy, s)
        st = studs_detail(metal)
        return lambda art, p: (lt(art, p), st(art, p))

    return body_armor(seed, base, det, extra=extra)


def hide(seed=3304):
    a = Art(320, 310, seed)
    cx, cy, s = 160, 146, 0.95
    base = place(body_pts(1.05, 8), cx, cy, s)
    # A shaggy edge: the outline resampled with fur tufts sticking out.
    from pen import resample

    q = resample(base, True, 9)
    shag = [(x + a.rng.uniform(-4, 4), y + a.rng.uniform(-4, 4)) for x, y in q]
    soft_shadow(a, shag, dx=5, dy=6)

    def fur(art, p):
        b = p.getBounds()
        for _ in range(170):
            x, y = art.rng.uniform(b.left(), b.right()), art.rng.uniform(b.top(), b.bottom())
            t = art.rng.uniform(1.2, 1.9)
            L = art.rng.uniform(8, 16)
            art.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], FINE * 1.0, color=art.rng.choice((shade(HIDE, 0.45), tint(HIDE, 0.35))), alpha=0.7)
        for _ in range(5):
            x, y = art.rng.uniform(b.left() + 30, b.right() - 30), art.rng.uniform(b.top() + 40, b.bottom() - 30)
            art.fill_path(to_path(ellipse(x, y, art.rng.uniform(14, 26), art.rng.uniform(10, 20), 20)), FUR_D, 0.35, blur=4)

    a.shape(shag, HIDE, corner=2, wob=0.6, depth=9, light_k=0.35, detail=fur)
    a.shape(place(ellipse(0, -104, 28, 10, 28), cx, cy, s), shade(HIDE, 0.6), outline=DETAIL * 1.1, corner=0, depth=3, shade_k=0, light_k=0, ao=0.4, mottle=0)
    for side in (-1, 1):
        a.ink([(cx + side * 30, cy + 10), (cx + side * 4, cy + 22)], DETAIL * 1.6, color=LEATHER_D)
        a.ink([(cx + side * 30, cy + 40), (cx + side * 4, cy + 52)], DETAIL * 1.6, color=LEATHER_D)
    return a.image()


def chain_shirt(seed=3305, metal=STEEL, extra=None, **kw):
    return body_armor(seed, metal, lambda cx, cy, s: rings_detail(metal), sleeves=SHORT_SLEEVE, sleeve_detail_fn=lambda cx, cy, s: rings_detail(metal), length=0.85, extra=extra, mottle=0, **kw)


def scale_mail(seed=3306, color=rgb("#a9a68f"), w=20, h=15, extra=None):
    def ex(a, cx, cy, s, path):
        a.shape(rect(cx - 96 * s, cy + 18 * s, cx + 96 * s, cy + 34 * s), LEATHER_D, outline=O * 0.9, corner=5, depth=3, mottle=0)
        a.shape(rect(cx - 9, cy + 16 * s, cx + 9, cy + 36 * s), BRASS, outline=FINE * 1.4, corner=2, depth=2, mottle=0)
        if extra:
            extra(a, cx, cy, s, path)

    return body_armor(seed, color, lambda cx, cy, s: scales_detail(color, w, h), sleeves=SHORT_SLEEVE, sleeve_detail_fn=lambda cx, cy, s: scales_detail(color, w, h), length=1.3, flare=10, w=320, h=330, extra=ex, mottle=0)


def breastplate(seed=3307):
    def ex(a, cx, cy, s, path):
        # Leather straps: over the shoulders, and the side ones hanging loose.
        for side in (-1, 1):
            for pts in ([(cx + side * 50 * s, cy - 114 * s), (cx + side * 90 * s, cy - 100 * s)], [(cx + side * 70 * s, cy + 30 * s), (cx + side * 84 * s, cy + 92 * s)]):
                a.ink(pts, DETAIL * 4.2, color=INK, taper=False)
                a.ink(pts, DETAIL * 2.6, color=LEATHER, taper=False)
            a.shape(rect(cx + side * 70 * s - 6, cy - 112 * s, cx + side * 70 * s + 6, cy - 100 * s), BRASS, outline=FINE * 1.3, corner=2, depth=1, mottle=0)

    return body_armor(seed, tint(STEEL, 0.1), lambda cx, cy, s: plate_detail(tint(STEEL, 0.1), cx, cy, s, faulds=0, length=0.7), length=0.62, h=250, extra=ex, mottle=0, var=V)


def half_plate(seed=3308, metal=STEEL, gem_color=None):
    w, h = 380, 360
    a = Art(w, h, seed)
    cx, cy, s = w / 2, 150, 0.95
    soft_shadow(a, place(body_pts(1.0), cx, cy, s), dx=5, dy=6)
    for side in (1, -1):
        a.shape(place([(x * side, y) for x, y in SHORT_SLEEVE], cx, cy, s), shade(STEEL, 0.1), corner=8, depth=6, light_k=0.3, detail=rings_detail(STEEL), mottle=0)
    tassets(a, cx, cy + 70, 1.05, metal, n=3)
    torso(a, cx, cy, s, metal, detail=plate_detail(metal, cx, cy, s, faulds=2), length=0.9, mottle=0, var=V)
    for side in (-1, 1):
        pauldron(a, cx + side * 96, cy - 92, 1.05, metal, side)
    if gem_color:
        a.shape(ellipse(cx, cy - 30, 20, 20, 32), GOLD, outline=O * 0.9, depth=3, mottle=0)
        gem(a, cx, cy - 30, 12, gem_color, 0.45)
    return a.image()


def ring_mail(seed=3309):
    return body_armor(seed, LEATHER, lambda cx, cy, s: rings_detail(LEATHER, r=7.5, sp=19, width=2.4, metal=IRON), sleeves=SHORT_SLEEVE, sleeve_detail_fn=lambda cx, cy, s: rings_detail(LEATHER, r=7.5, sp=19, width=2.4, metal=IRON), length=1.1, flare=6)


def chain_mail(seed=3310, metal=STEEL, extra=None):
    def ex(a, cx, cy, s, path):
        # The coif, folded down behind the neck.
        a.shape(place(ellipse(0, -128, 44, 26, 36), cx, cy, s), metal, outline=O, depth=5, light_k=0.4, mottle=0, detail=rings_detail(metal))
        a.shape(place(ellipse(0, -124, 24, 12, 28), cx, cy, s), shade(metal, 0.6), outline=DETAIL * 1.1, corner=0, depth=3, shade_k=0, light_k=0, ao=0.4, mottle=0)
        a.shape(rect(cx - 96 * s, cy + 18 * s, cx + 96 * s, cy + 32 * s), LEATHER_D, outline=O * 0.9, corner=5, depth=3, mottle=0)
        if extra:
            extra(a, cx, cy, s, path)

    return body_armor(seed, metal, lambda cx, cy, s: rings_detail(metal), sleeves=LONG_SLEEVE, sleeve_detail_fn=lambda cx, cy, s: rings_detail(metal), length=1.45, flare=16, w=350, h=380, s=0.92, extra=ex, mottle=0)


def splint(seed=3311):
    def det(cx, cy, s):
        def d(art, p):
            b = p.getBounds()
            x = b.left() + 4
            while x < b.right():
                pts = rect(x, cy - 66 * s, x + 15, b.bottom() + 4)
                art.fill_path(to_path(pts), vary(art.rng, STEEL, 0.05))
                art.stroke_path(to_path(pts), INK, 2.2, 0.9)
                art.ink([(x + 4, cy - 62 * s), (x + 4, b.bottom())], FINE * 1.1, color=tint(STEEL, 0.6), alpha=0.6, taper=False, wob=0)
                for yy in (cy - 58 * s, cy + 20 * s, cy + 96 * s):
                    dot(art, x + 7.5, yy, 2.4, shade(STEEL, 0.5))
                x += 16

        return d

    def ex(a, cx, cy, s, path):
        for side in (-1, 1):
            pauldron(a, cx + side * 90 * s, cy - 96 * s, 0.85, STEEL, side, lames=4)
        a.shape(rect(cx - 96 * s, cy + 16 * s, cx + 96 * s, cy + 30 * s), LEATHER_D, outline=O * 0.9, corner=5, depth=3, mottle=0)

    return body_armor(seed, LEATHER_D, det, sleeves=SHORT_SLEEVE, sleeve_color=STEEL, sleeve_detail_fn=lambda cx, cy, s: rings_detail(STEEL), length=1.15, flare=6, w=340, h=320, extra=ex)


def plate(seed=3312):
    return plate_suit(seed)


# -- magic armor -----------------------------------------------------------------------------------


DRAGON = {
    "Black": rgb("#3a3a44"),
    "Blue": rgb("#3f6fb8"),
    "Green": rgb("#4f8a4a"),
    "White": rgb("#dfe6ea"),
    "Gold": rgb("#d8aa3e"),
    "Silver": rgb("#bfc6cf"),
}


def dragon_scale(color=RED, seed=3320):
    return scale_mail(seed, color, w=30, h=22)


def elven_chain(seed=3322):
    def ex(a, cx, cy, s, path):
        # A leafy filigree band down the front and around the neck.
        for k in range(7):
            y = cy - 70 * s + k * 26 * s
            for side in (-1, 1):
                lx = cx + side * 14
                a.shape(rot_pts(ellipse(lx, y, 10, 4.5, 16), lx, y, side * 0.6), rgb("#a6c48a"), outline=FINE * 1.2, corner=0, depth=1, mottle=0)
        a.ink([(cx, cy - 86 * s), (cx, cy + 92 * s)], FINE * 1.4, color=GOLD)
        a.ink(chaikin([(cx - 38 * s, cy - 114 * s), (cx, cy - 92 * s), (cx + 38 * s, cy - 114 * s)], False, 2), DETAIL * 1.2, color=GOLD)

    return chain_shirt(seed, ELVEN, extra=ex)


def mithral(seed=3321):
    def ex(a, cx, cy, s, path):
        for _ in range(9):
            star(a, cx + a.rng.uniform(-80, 80) * s, cy + a.rng.uniform(-80, 70) * s, a.rng.uniform(5, 8), (255, 255, 255), 0.95)

    return chain_shirt(seed, MITHRAL, extra=ex)


def glamoured(seed=3326):
    return studded(seed, metal=GOLD, base=rgb("#5a3a52"), sheen=rgb("#d6a8f0"))


def armor_of_resistance(seed=3330):
    return half_plate(seed, STEEL, gem_color=RED)


# -- shields ---------------------------------------------------------------------------------------


def shield_pts(kind, cx, cy, s=1.0):
    if kind == "round":
        return ellipse(cx, cy, 92 * s, 92 * s, 80)
    if kind == "kite":
        return chaikin(place([(-80, -86), (0, -118), (80, -86), (70, 20), (0, 132), (-70, 20)], cx, cy, s), True, 2)
    return chaikin(place([(-82, -100), (82, -100), (82, -14), (0, 112), (-82, -14)], cx, cy, s), True, 2)


def shield(seed, kind, color, rim=IRON, deco=None, boss=False, aura=None, size=None):
    w, h = size or ((220, 220) if kind == "round" else (210, 290) if kind == "kite" else (210, 260))
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2
    pts = shield_pts(kind, cx, cy)
    if aura:
        glow(a, cx, cy, 130, aura, 0.4)
    soft_shadow(a, pts, dx=5, dy=6)
    a.shape(pts, color, depth=10, light_k=0.4, detail=(lambda art, p: deco(art, cx, cy)) if deco else None)
    inner = [(cx + (x - cx) * 0.9, cy + (y - cy) * 0.9) for x, y in pts]
    a.ink(inner, DETAIL * 2.2, closed=True, color=rim, alpha=0.95)
    if boss:
        a.shape(ellipse(cx, cy, 24, 24, 36), IRON, outline=O, depth=4, light_k=0.6, mottle=0, var=V)
    return a, cx, cy


def animated_shield(seed=3340):
    def deco(art, cx, cy):
        rune_marks(art, cx, cy - 10, 44, 8, SKYGLOW, width=FINE * 1.8)
        art.ink(ellipse(cx, cy - 10, 30, 30, 40), DETAIL, closed=True, color=SKYGLOW, alpha=0.9)

    a, cx, cy = shield(seed, "heater", rgb("#5b6f8c"), rim=SILVER, deco=deco, aura=SKYGLOW, size=(250, 300))
    for k, r in enumerate((112, 122)):
        a.ink([(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [2.3 + i * 0.08 for i in range(14)]], FINE * 1.6, color=SKYGLOW, alpha=0.8 - k * 0.3)
        a.ink([(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [-0.8 + i * 0.08 for i in range(14)]], FINE * 1.6, color=SKYGLOW, alpha=0.8 - k * 0.3)
    return a.image()


def stuck_arrow(a, x, y, ang, L=90):
    """An arrow sunk into the shield at (x, y), its shaft and fletching
    sticking out along `ang`: the head is buried, so only a split shows."""
    from obj_war import arrow_at

    ex, ey = x + math.cos(ang) * L, y + math.sin(ang) * L
    arrow_at(a, ex, ey, ang + math.pi, L)
    a.shape(ellipse(x, y, 7, 7, 16), shade(WOOD, 0.55), outline=FINE * 1.3, corner=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)


def arrow_catching(seed=3341):
    def deco(art, cx, cy):
        for k in range(-3, 4):
            art.ink([(cx + k * 26, cy - 100), (cx + k * 26, cy + 100)], DETAIL * 0.8, color=shade(WOOD, 0.4), alpha=0.8, taper=False)
        art.ink(ellipse(cx, cy, 60, 60, 60), FINE * 1.6, closed=True, color=rgb("#e0c060"), alpha=0.9)

    a, cx, cy = shield(seed, "round", WOOD, deco=deco, boss=True, size=(340, 340))
    for x, y, t in ((cx - 44, cy - 30, -2.6), (cx + 40, cy - 46, -0.7), (cx + 46, cy + 34, 0.6), (cx - 30, cy + 50, 2.1)):
        stuck_arrow(a, x, y, t)
    return a.image()


def missile_attraction(seed=3342):
    def deco(art, cx, cy):
        for r, c in ((70, WHITE), (52, rgb("#b23a3a")), (34, WHITE), (16, rgb("#b23a3a"))):
            art.fill_path(to_path(ellipse(cx, cy - 6, r, r, 50)), c)
            art.ink(ellipse(cx, cy - 6, r, r, 50), FINE * 1.3, closed=True, color=INK, alpha=0.7)

    a, cx, cy = shield(seed, "kite", rgb("#6a6f78"), rim=rgb("#3e4048"), deco=deco, size=(250, 320))
    for x, y in ((cx - 116, cy - 96), (cx + 112, cy - 66), (cx + 108, cy + 96)):
        ang = math.atan2(cy - y, cx - x)
        a.ink([(x, y), (x + 34 * math.cos(ang), y + 34 * math.sin(ang))], DETAIL * 1.2, color=rgb("#7a2a4a"), alpha=0.95)
        a.ink([(x + 20 * math.cos(ang) + 8 * math.cos(ang + 2.5), y + 20 * math.sin(ang) + 8 * math.sin(ang + 2.5)), (x + 34 * math.cos(ang), y + 34 * math.sin(ang)), (x + 20 * math.cos(ang) + 8 * math.cos(ang - 2.5), y + 20 * math.sin(ang) + 8 * math.sin(ang - 2.5))], DETAIL * 1.2, color=rgb("#7a2a4a"), alpha=0.95, taper=False)
    return a.image()


def spellguard(seed=3343):
    def deco(art, cx, cy):
        art.ink(ellipse(cx, cy - 10, 50, 50, 60), DETAIL * 1.2, closed=True, color=ARCANE)
        art.ink(ellipse(cx, cy - 10, 38, 38, 60), FINE * 1.3, closed=True, color=ARCANE)
        pts = [(cx + 38 * math.cos(-math.pi / 2 + k * 4 * math.pi / 5), cy - 10 + 38 * math.sin(-math.pi / 2 + k * 4 * math.pi / 5)) for k in range(5)]
        art.ink(pts, FINE * 1.4, closed=True, color=ARCANE, taper=False)
        rune_marks(art, cx, cy - 10, 44, 10, tint(ARCANE, 0.3), width=FINE)

    a, cx, cy = shield(seed, "kite", rgb("#c3c8d0"), rim=GOLD, deco=deco, aura=ARCANE, size=(250, 320))
    return a.image()


def sentinel(seed=3344):
    def deco(art, cx, cy):
        eye = [(cx - 52, cy - 14), (cx, cy - 46), (cx + 52, cy - 14), (cx, cy + 18)]
        art.shape(chaikin(eye, True, 2), WHITE, outline=DETAIL * 1.3, corner=0, depth=2, mottle=0)
        art.shape(ellipse(cx, cy - 14, 18, 18, 30), rgb("#3a8a9a"), outline=FINE * 1.4, depth=2, mottle=0)
        dot(art, cx, cy - 14, 8, INK)
        dot(art, cx - 5, cy - 19, 3, (255, 255, 255))

    a, cx, cy = shield(seed, "heater", rgb("#4a5f7a"), rim=GOLD, deco=deco)
    return a.image()


# -- clothes, robes and cloaks ----------------------------------------------------------------------


def tunic_pts(length=1.0):
    left = [(-20, -112), (-45, -118), (-80, -104), (-140, -40), (-152, 30), (-120, 38), (-102, -28), (-80, -18), (-82, 100 * length), (-40, 106 * length)]
    return mirrored(left, (0, 108 * length), (0, -100))


def robe_pts():
    left = [(-22, -128), (-50, -124), (-82, -112), (-150, -56), (-176, 12), (-120, 34), (-98, -26), (-92, 60), (-112, 156), (-60, 164)]
    return mirrored(left, (0, 166), (0, -114))


def cloak_pts(short=False):
    L = 0.6 if short else 1.0
    left = [(-28, -118), (-56, -110), (-104, 40 * L - (40 if short else 0)), (-132, 150 * L), (-70, 166 * L)]
    return mirrored(left, (0, 170 * L), (0, -108))


def garment(seed, pts_fn, color, w, h, s=1.0, cy=None, detail=None, after=None, hood=None, collar=True):
    a = Art(w, h, seed)
    cx = w / 2
    cy = cy if cy is not None else h / 2
    pts = place(pts_fn(), cx, cy, s)
    soft_shadow(a, pts, dx=5, dy=6)
    a.shape(pts, color, corner=10, depth=10, light_k=0.35, detail=(lambda art, p: detail(art, p, cx, cy, s)) if detail else None)
    if hood:
        hx, hy = cx, cy + hood[1] * s
        a.shape(ellipse(hx, hy, hood[0] * s, hood[0] * 0.62 * s, 40), shade(color, 0.05), outline=None or 7.0, depth=7, light_k=0.35)
        a.shape(ellipse(hx, hy + 6 * s, hood[0] * 0.6 * s, hood[0] * 0.3 * s, 32), shade(color, 0.6), outline=DETAIL * 1.1, corner=0, depth=3, shade_k=0, light_k=0, ao=0.4, mottle=0)
    elif collar:
        a.shape(place(ellipse(0, -106, 26, 9, 28), cx, cy, s), shade(color, 0.6), outline=DETAIL * 1.1, corner=0, depth=3, shade_k=0, light_k=0, ao=0.4, mottle=0)
    if after:
        after(a, cx, cy, s)
    return a.image()


def folds(art, cx, cy, s, color, top=-100, bottom=150, n=4, spread=90):
    for k in range(n):
        f = (k + 0.5) / n * 2 - 1
        art.ink(chaikin([(cx + f * 20 * s, cy + top * s), (cx + f * spread * 0.6 * s, cy + (top + bottom) / 2 * s), (cx + f * spread * s, cy + bottom * s)], False, 2), FINE * 1.3, color=shade(color, 0.45), alpha=0.6)


def fine_clothes(seed=3350):
    def det(art, p, cx, cy, s):
        art.ink([(cx, cy - 100 * s), (cx, cy + 108 * s)], DETAIL, color=shade(RED, 0.5), alpha=0.8)
        for side in (-1, 1):
            art.ink([(cx + side * 130 * s, cy + 16 * s), (cx + side * 154 * s, cy + 24 * s)], DETAIL * 2.4, color=GOLD)
        art.ink([(cx - 82 * s, cy + 80 * s), (cx + 82 * s, cy + 80 * s)], DETAIL * 2.2, color=GOLD)

    def after(a, cx, cy, s):
        a.shape(scallop(cx, cy - 106 * s, 40 * s, a.rng, 12, 0.18, ry=18 * s), WHITE, outline=DETAIL * 1.2, depth=3, mottle=0)
        a.shape(place(ellipse(0, -106, 20, 7, 28), cx, cy, s), shade(WHITE, 0.4), outline=FINE * 1.2, corner=0, depth=2, shade_k=0, light_k=0, ao=0.3, mottle=0)
        for k in range(6):
            gem(a, cx, cy + (-74 + k * 28) * s, 4.5, GOLD)

    return garment(seed, tunic_pts, RED, 340, 260, s=0.95, detail=det, after=after, collar=False)


def travelers_clothes(seed=3351):
    def det(art, p, cx, cy, s):
        folds(art, cx, cy, s, RED, top=-90, bottom=100, n=3, spread=60)
        art.ink([(cx - 10, cy - 104 * s), (cx, cy - 70 * s), (cx + 10, cy - 104 * s)], FINE * 1.4, color=shade(RED, 0.5))

    def after(a, cx, cy, s):
        a.shape(rect(cx - 84 * s, cy + 44 * s, cx + 84 * s, cy + 60 * s), LEATHER_D, outline=O * 0.9, corner=5, depth=3, mottle=0)
        a.shape(rect(cx - 10, cy + 41 * s, cx + 10, cy + 63 * s), IRON, outline=FINE * 1.4, corner=2, depth=2, mottle=0)
        # a pouch hanging from the belt
        a.shape(ellipse(cx + 54 * s, cy + 74 * s, 16, 18, 24), LEATHER, outline=O * 0.8, depth=3, mottle=0.04)

    return garment(seed, tunic_pts, RED, 340, 260, s=0.95, detail=det, after=after)


def costume(seed=3352):
    YEL = rgb("#e0b84a")

    def det(art, p, cx, cy, s):
        d = 26
        for i in range(-8, 9):
            for j in range(-8, 9):
                x, y = cx + i * d, cy + j * d
                if (i + j) % 2:
                    art.fill_path(to_path([(x, y - d / 2), (x + d / 2, y), (x, y + d / 2), (x - d / 2, y)]), YEL)

    def after(a, cx, cy, s):
        for x, y in ((-140, 34), (140, 34), (-60, 108), (0, 112), (60, 108)):
            dot(a, cx + x * s + 1, cy + y * s + 2, 7, INK, 0.8)
            dot(a, cx + x * s, cy + y * s, 5.5, GOLD)
            dot(a, cx + x * s - 1.5, cy + y * s - 1.5, 1.8, tint(GOLD, 0.7))
        a.shape(scallop(cx, cy - 104 * s, 36 * s, a.rng, 8, 0.3, ry=16 * s), YEL, outline=DETAIL * 1.2, depth=3, mottle=0)

    def pts():
        base = tunic_pts()
        # A zigzag hem.
        out = [p for p in base if p[1] < 90]
        idx = next(i for i, p in enumerate(base) if p[1] >= 90)
        hem = [(-82 + k * 82 / 4, 104 if k % 2 == 0 else 128) for k in range(9)]
        return out[:idx] + hem + out[idx:]

    return garment(seed, pts, RED, 340, 280, s=0.95, cy=128, detail=det, after=after)


def robe(seed=3353, color=RED, detail=None, after=None, belt=rgb("#cdb07a"), hood=True):
    def det(art, p, cx, cy, s):
        folds(art, cx, cy, s, color, top=-80, bottom=160, n=4, spread=80)
        for side in (-1, 1):
            art.ink([(cx + side * 120 * s, cy + 36 * s), (cx + side * 176 * s, cy + 12 * s)], DETAIL * 1.2, color=shade(color, 0.5), alpha=0.8)
        if detail:
            detail(art, p, cx, cy, s)

    def aft(a, cx, cy, s):
        if belt:
            a.ink(chaikin([(cx - 94 * s, cy + 40 * s), (cx, cy + 46 * s), (cx + 94 * s, cy + 40 * s)], False, 2), DETAIL * 3.4, color=INK)
            a.ink(chaikin([(cx - 94 * s, cy + 40 * s), (cx, cy + 46 * s), (cx + 94 * s, cy + 40 * s)], False, 2), DETAIL * 1.8, color=belt)
            for dx in (-6, 6):
                a.ink([(cx + dx, cy + 46 * s), (cx + dx * 2, cy + 100 * s)], DETAIL * 2.8, color=INK)
                a.ink([(cx + dx, cy + 46 * s), (cx + dx * 2, cy + 100 * s)], DETAIL * 1.4, color=belt)
        if after:
            after(a, cx, cy, s)

    return garment(seed, robe_pts, color, 360, 360, s=0.95, cy=190, detail=det, after=aft, hood=(54, -130) if hood else None, collar=not hood)


def cloak(seed, color, detail=None, after=None, short=False, clasp=SILVER, hood=True, w=300, h=None, pts_fn=None):
    h = h or (280 if short else 370)

    def det(art, p, cx, cy, s):
        folds(art, cx, cy, s, color, top=-100, bottom=100 if short else 160, n=5, spread=110)
        if detail:
            detail(art, p, cx, cy, s)

    def aft(a, cx, cy, s):
        for side in (-1, 1):
            a.shape(ellipse(cx + side * 22 * s, cy - 100 * s, 9, 9, 20), clasp, outline=FINE * 1.6, depth=2, light_k=0.6, mottle=0)
        a.ink([(cx - 14 * s, cy - 100 * s), (cx + 14 * s, cy - 100 * s)], FINE * 1.6, color=clasp)
        if after:
            after(a, cx, cy, s)

    return garment(seed, pts_fn or (lambda: cloak_pts(short)), color, w, h, detail=det, after=aft, cy=180 if hood else 150, hood=(50, -126) if hood else None)


def web(art, cx, cy, R, color, alpha=0.8, spokes=10, rings_=5):
    for k in range(spokes):
        t = 2 * math.pi * k / spokes
        art.ink([(cx, cy), (cx + R * math.cos(t), cy + R * math.sin(t))], FINE * 1.1, color=color, alpha=alpha, taper=False)
    for j in range(1, rings_ + 1):
        r = R * j / rings_
        pts = []
        for k in range(spokes + 1):
            t = 2 * math.pi * k / spokes
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        art.ink(chaikin(pts, False, 1), FINE, color=color, alpha=alpha, taper=False)


def spider(a, x, y, r, color=INK):
    for side in (-1, 1):
        for k in range(4):
            t = -0.9 + k * 0.6
            a.ink(chaikin([(x, y), (x + side * r * 1.4 * math.cos(t), y + r * 1.0 * math.sin(t) - r * 0.4), (x + side * r * 2.0 * math.cos(t), y + r * 1.6 * math.sin(t))], False, 1), FINE * 1.5, color=color)
    a.shape(ellipse(x, y + r * 0.5, r * 0.75, r, 20), color, outline=FINE * 1.2, depth=1, mottle=0)
    a.shape(ellipse(x, y - r * 0.6, r * 0.5, r * 0.45, 16), color, outline=FINE * 1.2, depth=1, mottle=0)


def cloak_arachnida(seed=3360):
    def det(art, p, cx, cy, s):
        web(art, cx, cy + 30, 150, rgb("#c8c8d4"), 0.55, spokes=12, rings_=7)

    def after(a, cx, cy, s):
        spider(a, cx, cy - 100 * s, 9, rgb("#7a2a34"))

    return cloak(seed, BLACK_CLOTH, detail=det, after=after, clasp=rgb("#7a2a34"))


def cloak_displacement(seed=3361):
    import numpy as np
    from PIL import Image

    base = cloak(seed, rgb("#5a5a8a"), detail=lambda art, p, cx, cy, s: [star(art, cx + art.rng.uniform(-100, 100), cy + art.rng.uniform(-60, 150), 4, rgb("#c8c8f0"), 0.8) for _ in range(14)])
    ghost = np.asarray(base).astype(np.float32)
    ghost[..., 3] *= 0.38
    ghost[..., 2] = np.clip(ghost[..., 2] * 1.2, 0, 255)
    g = Image.fromarray(ghost.astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (base.width + 30, base.height + 10), (0, 0, 0, 0))
    out.alpha_composite(g, (30, 0))
    out.alpha_composite(base, (0, 10))
    return out


def cloak_elvenkind(seed=3362):
    col = rgb("#708a6a")

    def det(art, p, cx, cy, s):
        for _ in range(16):
            x, y = cx + art.rng.uniform(-110, 110), cy + art.rng.uniform(-60, 160)
            t = art.rng.uniform(0, 6.28)
            lp = rot_pts(ellipse(x, y, 13, 5, 16), x, y, t)
            art.fill_path(to_path(lp), tint(col, 0.25), 0.6)
            art.ink(rot_pts([(x - 12, y), (x + 12, y)], x, y, t), FINE * 0.8, color=shade(col, 0.4), alpha=0.6)

    def after(a, cx, cy, s):
        x, y = cx, cy - 100 * s
        a.shape(rot_pts(ellipse(x, y, 16, 7, 20), x, y, -0.4), rgb("#a6c48a"), outline=FINE * 1.5, corner=0, depth=2, mottle=0)

    return cloak(seed, col, detail=det, after=after, clasp=GOLD)


def cloak_protection(seed=3363):
    def after(a, cx, cy, s):
        x, y = cx, cy - 100 * s
        a.shape(chaikin([(x - 12, y - 12), (x + 12, y - 12), (x + 12, y + 2), (x, y + 16), (x - 12, y + 2)], True, 1), SILVER, outline=FINE * 1.6, corner=0, depth=2, light_k=0.6, mottle=0)

    def det(art, p, cx, cy, s):
        art.ink(cloak_pts_inner(cx, cy, s), DETAIL * 1.4, closed=True, color=GOLD, alpha=0.9)

    return cloak(seed, RED, detail=det, after=after, clasp=SILVER)


def cloak_pts_inner(cx, cy, s, k=0.9):
    pts = place(cloak_pts(), cx, cy, s)
    mx = cx
    my = cy + 20 * s
    return [(mx + (x - mx) * k, my + (y - my) * k) for x, y in pts]


def bat_pts():
    left = [(-28, -118), (-56, -110), (-110, -20), (-150, 60), (-150, 140), (-120, 118), (-100, 160), (-70, 130), (-40, 170)]
    return mirrored(left, (0, 140), (0, -108))


def cloak_bat(seed=3364):
    col = rgb("#3e3236")

    def det(art, p, cx, cy, s):
        for side in (-1, 1):
            for k in range(4):
                art.ink(chaikin([(cx + side * 20, cy - 96), (cx + side * (40 + k * 30), cy + 20), (cx + side * (50 + k * 26), cy + 150 - k * 6)], False, 2), FINE * 1.6, color=shade(col, 0.6), alpha=0.9)

    return cloak(seed, col, detail=det, clasp=rgb("#9a8a7a"), pts_fn=bat_pts, w=330)


def manta_pts():
    left = [(-24, -118), (-50, -108), (-150, 0), (-162, 30), (-90, 60), (-30, 150), (-8, 210)]
    return mirrored(left, (0, 214), (0, -108))


def cloak_manta(seed=3365):
    col = rgb("#4a5f78")

    def det(art, p, cx, cy, s):
        for _ in range(16):
            x, y = cx + art.rng.uniform(-110, 110), cy + art.rng.uniform(-50, 100)
            art.fill_path(to_path(ellipse(x, y, art.rng.uniform(3, 6), art.rng.uniform(3, 6), 12)), tint(col, 0.55), 0.8)
        art.ink(chaikin([(cx - 150, cy + 10), (cx, cy - 30), (cx + 150, cy + 10)], False, 2), FINE * 1.4, color=shade(col, 0.5), alpha=0.7)

    return cloak(seed, col, detail=det, clasp=rgb("#d8d0b8"), pts_fn=manta_pts, w=360, h=400)


def cape_mountebank(seed=3366):
    def det(art, p, cx, cy, s):
        art.ink(cloak_pts_inner(cx, cy, s, 0.92), DETAIL * 1.6, closed=True, color=GOLD, alpha=0.95)

    return cloak(seed, RED, detail=det, short=True, clasp=GOLD, hood=False, w=300)


def mantle_spell_resistance(seed=3367):
    col = rgb("#3a4f8a")

    def det(art, p, cx, cy, s):
        for k in range(12):
            t = k / 11
            x = cx - 110 + 220 * t
            y = cy + 140 + 10 * math.sin(t * math.pi)
            a = k % 3
            pts = [(x - 5, y + 5), (x, y - 6), (x + 5, y + 5)] if a == 0 else [(x - 5, y - 5), (x + 5, y), (x - 5, y + 5)] if a == 1 else [(x, y - 6), (x, y + 6), (x + 5, y)]
            art.ink(pts, FINE * 1.5, color=SILVER, taper=False, wob=0.2)
        art.ink(cloak_pts_inner(cx, cy, s, 0.86), DETAIL, closed=True, color=SILVER, alpha=0.8)

    return cloak(seed, col, detail=det, clasp=SILVER)


def eye_at(art, x, y, r, iris=rgb("#3a8a9a")):
    art.shape(chaikin([(x - r, y), (x, y - r * 0.6), (x + r, y), (x, y + r * 0.6)], True, 2), WHITE, outline=FINE * 1.4, corner=0, wob=0.1, depth=1, shade_k=0.2, light_k=0, ao=0, mottle=0)
    dot(art, x, y, r * 0.42, iris)
    dot(art, x, y, r * 0.2, INK)


def robe_of_eyes(seed=3370):
    col = rgb("#6a5a7a")

    def after(a, cx, cy, s):
        pts = place(robe_pts(), cx, cy, s)
        path = to_path(pts)
        n = 0
        tries = 0
        spots = []
        while n < 22 and tries < 500:
            tries += 1
            x, y = cx + a.rng.uniform(-170, 170) * s, cy + a.rng.uniform(-90, 150) * s
            if not path.contains(x, y) or any(math.hypot(x - u, y - v) < 34 for u, v in spots):
                continue
            spots.append((x, y))
            eye_at(a, x, y, a.rng.uniform(9, 13), a.rng.choice((rgb("#3a8a9a"), rgb("#8a6a3a"), rgb("#5a8a3a"))))
            n += 1

    return robe(seed, col, after=after, belt=None)


def robe_scintillating(seed=3371):
    cols = [rgb(h) for h in ("#d9534f", "#ef9a3c", "#e8d04a", "#5cb85c", "#4a90d9", "#8a5cc8")]

    def det(art, p, cx, cy, s):
        b = p.getBounds()
        bw = 34
        for k in range(-12, 14):
            x = cx + k * bw
            art.fill_path(to_path([(x, b.top()), (x + bw, b.top()), (x + bw + 160, b.bottom()), (x + 160, b.bottom())]), cols[k % len(cols)], 0.85)
        for _ in range(16):
            star(art, art.rng.uniform(b.left(), b.right()), art.rng.uniform(b.top(), b.bottom()), 6, (255, 255, 255), 0.85)

    return robe(seed, rgb("#c0a0d0"), detail=det, belt=GOLD)


def robe_of_stars(seed=3372):
    col = rgb("#26305a")

    def det(art, p, cx, cy, s):
        b = p.getBounds()
        for _ in range(40):
            star(art, art.rng.uniform(b.left(), b.right()), art.rng.uniform(b.top(), b.bottom()), art.rng.uniform(3, 6), rgb("#eef0ff"), 0.95)
        for _ in range(5):
            star(art, art.rng.uniform(b.left() + 30, b.right() - 30), art.rng.uniform(b.top() + 60, b.bottom() - 20), 11, rgb("#fff4c8"), 1.0)

    return robe(seed, col, detail=det, belt=SILVER)


def robe_archmagi(seed=3373, color=WHITE, trim=GOLD):
    def det(art, p, cx, cy, s):
        art.ink([(cx, cy - 112 * s), (cx, cy + 166 * s)], DETAIL * 3, color=trim, alpha=0.9)
        for k in range(8):
            y = cy + (-90 + k * 32) * s
            rune_marks(art, cx, y, 0.01, 1, shade(trim, 0.4), width=FINE * 1.4)
        b = p.getBounds()
        art.ink([(b.left(), cy + 150 * s), (b.right(), cy + 150 * s)], DETAIL * 3, color=trim, alpha=0.9)
        for side in (-1, 1):
            art.ink([(cx + side * 124 * s, cy + 40 * s), (cx + side * 178 * s, cy + 16 * s)], DETAIL * 3, color=trim, alpha=0.9)

    def after(a, cx, cy, s):
        glow(a, cx, cy - 20, 60, rgb("#c8b8ff"), 0.25)

    return robe(seed, color, detail=det, after=after, belt=trim)


def robe_useful_items(seed=3374):
    col = rgb("#8a6a4a")
    patch_cols = [rgb(h) for h in ("#c9b088", "#7a8a5a", "#5a6a8a", "#9a7a5a", "#b08a6a", "#6a8a8a")]

    def after(a, cx, cy, s):
        path = to_path(place(robe_pts(), cx, cy, s))
        spots = []
        tries = 0
        while len(spots) < 12 and tries < 400:
            tries += 1
            x, y = cx + a.rng.uniform(-150, 150) * s, cy + a.rng.uniform(-80, 140) * s
            if not path.contains(x, y) or any(math.hypot(x - u, y - v) < 40 for u, v in spots):
                continue
            spots.append((x, y))
            sz = a.rng.uniform(12, 17)
            pc = a.rng.choice(patch_cols)
            pr = rot_pts(rect(x - sz, y - sz, x + sz, y + sz), x, y, a.rng.uniform(-0.3, 0.3))
            a.shape(pr, pc, outline=FINE * 1.5, corner=3, depth=2, mottle=0)
            stitch_line(a, pr + pr[:1], shade(pc, 0.5), width=FINE * 0.8, gap=5)

    return robe(seed, col, after=after)


def wings_of_flying(seed=3375):
    w, h = 460, 260
    a = Art(w, h, seed)
    cx, cy = w / 2, 70
    for side in (-1, 1):
        for row, (L, col) in enumerate(((210, rgb("#8a6a4a")), (160, rgb("#b8946a")), (100, rgb("#ddc8a0")))):
            n = 8 - row
            for k in range(n):
                t = math.radians(-20 + k * (90 / n) + row * 6)
                ux, uy = side * math.cos(t), math.sin(t)
                bx, by = cx + side * 26, cy + 8
                tipx, tipy = bx + ux * L, by + uy * L
                nx, ny = -uy, ux
                fw = 15 - row * 2
                pts = chaikin([(bx, by), (bx + ux * L * 0.5 + nx * fw, by + uy * L * 0.5 + ny * fw), (tipx, tipy), (bx + ux * L * 0.5 - nx * fw, by + uy * L * 0.5 - ny * fw)], True, 2)
                a.shape(pts, vary(a.rng, col, 0.05), outline=DETAIL * 1.2, corner=0, wob=0.2, depth=2, mottle=0, light_k=0.3)
                a.ink([(bx, by), (bx + ux * L * 0.9, by + uy * L * 0.9)], FINE, color=shade(col, 0.4), alpha=0.7)
    a.shape(rect(cx - 34, cy - 20, cx + 34, cy + 30), LEATHER_D, outline=O, corner=10, depth=4, mottle=0.04)
    a.shape(ellipse(cx, cy + 4, 12, 12, 20), GOLD, outline=FINE * 1.5, depth=2, mottle=0)
    return a.image()


# -- boots, gloves, bracers, belts ------------------------------------------------------------------


BOOT = [(0, 0), (38, 0), (40, 70), (44, 104), (42, 120), (-58, 120), (-68, 110), (-60, 96), (-20, 86), (0, 70)]


def boot(a, x, y, color, s=1.0, cuff=None, sole=LEATHER_D, detail=None, low=False):
    pts = BOOT if not low else [(0, 64), (38, 64), (40, 82), (44, 104), (42, 120), (-58, 120), (-68, 110), (-60, 96), (-20, 86), (0, 80)]
    q = place(pts, x, y, s)
    a.shape(q, color, outline=O, corner=8, depth=5, light_k=0.4, mottle=0.04, var=V, detail=(lambda art, p: detail(art, x, y, s)) if detail else None)
    a.shape(place([(-62, 112), (44, 112), (42, 122), (-58, 122), (-68, 112)], x, y, s), sole, outline=FINE * 1.6, corner=4, depth=2, mottle=0)
    if cuff and not low:
        cuff(a, x, y, s)


def boots(seed, color, cuff=None, detail=None, low=False, below=None, after=None, w=200, h=200, sole=LEATHER_D):
    a = Art(w, h, seed)
    if below:
        below(a)
    for k, (x, y) in enumerate(((110, 30), (140, 52))):
        boot(a, x, y, shade(color, 0.12) if k == 0 else color, cuff=cuff, detail=detail, low=low, sole=sole)
    if after:
        after(a)
    return a.image()


def boots_elvenkind(seed=3380):
    col = rgb("#6a7a4a")

    def cuff(a, x, y, s):
        a.shape(place([(-6, -4), (44, -4), (36, 22), (20, 12), (8, 24)], x, y, s), tint(col, 0.15), outline=O * 0.8, corner=3, depth=3, mottle=0)

    def det(art, x, y, s):
        art.ink(chaikin([(x + 10, y + 30), (x - 10, y + 80), (x - 50, y + 104)], False, 2), FINE * 1.2, color=GOLD, alpha=0.8)

    return boots(seed, col, cuff=cuff, detail=det)


def boots_levitation(seed=3381):
    col = rgb("#7a8aa0")

    def below(a):
        glow(a, 100, 170, 70, SKYGLOW, 0.4)

    def after(a):
        for x in (60, 100, 140):
            a.ink([(x, 196), (x, 176)], FINE * 1.6, color=SKYGLOW, alpha=0.9)
            a.ink([(x - 6, 182), (x, 174), (x + 6, 182)], FINE * 1.6, color=SKYGLOW, alpha=0.9)

    def cuff(a, x, y, s):
        a.shape(place(rect(-4, -4, 42, 14), x, y, s), SILVER, outline=O * 0.8, corner=4, depth=2, mottle=0)

    return boots(seed, col, cuff=cuff, below=below, after=after, h=210)


def boots_speed(seed=3382):
    col = rgb("#8a3a2a")

    def det(art, x, y, s):
        bolt = [(x + 24, y + 20), (x + 10, y + 56), (x + 22, y + 56), (x + 6, y + 96), (x + 32, y + 50), (x + 20, y + 50), (x + 32, y + 20)]
        art.shape(bolt, GOLD, outline=FINE * 1.3, corner=0, depth=1, mottle=0)

    def after(a):
        for k in range(3):
            y = 120 + k * 22
            a.ink([(196, y), (176, y)], FINE * 1.8, color=GOLD, alpha=0.8)

    return boots(seed, col, detail=det, after=after, cuff=lambda a, x, y, s: a.shape(place(rect(-4, -4, 42, 14), x, y, s), GOLD, outline=O * 0.8, corner=4, depth=2, mottle=0))


def boots_striding(seed=3383):
    col = rgb("#5a7a6a")

    def after(a):
        for x0, y0 in ((110 + 36, 30 + 122), (140 + 36, 52 + 122)):
            pts = [(x0 - 6 + (12 if k % 2 else 0), y0 + k * 5) for k in range(7)]
            a.ink(pts, DETAIL * 2.2, color=INK, taper=False, wob=0)
            a.ink(pts, DETAIL * 1.0, color=SILVER, taper=False, wob=0)

    return boots(seed, col, after=after, h=230, cuff=lambda a, x, y, s: a.shape(place(rect(-4, -4, 42, 14), x, y, s), rgb("#c9b088"), outline=O * 0.8, corner=4, depth=2, mottle=0))


def boots_winterlands(seed=3384):
    col = rgb("#6a7a8a")

    def cuff(a, x, y, s):
        a.shape(scallop(x + 19, y + 6, 32, a.rng, 9, 0.25, ry=16), rgb("#f0ece4"), outline=O * 0.8, depth=3, mottle=0)

    def det(art, x, y, s):
        star(art, x - 20, y + 100, 6, (255, 255, 255), 0.9, points=6)

    return boots(seed, col, cuff=cuff, detail=det, w=210)


def winged_boots(seed=3385):
    col = rgb("#9a7a52")

    def cuff(a, x, y, s):
        for k in range(3):
            pts = chaikin([(x + 40, y + 30 + k * 6), (x + 70 + k * 6, y + 6 + k * 12), (x + 82 + k * 4, y + 16 + k * 14), (x + 42, y + 42 + k * 6)], True, 2)
            a.shape(pts, (240, 236, 226), outline=FINE * 1.5, corner=0, depth=1, mottle=0)

    return boots(seed, col, cuff=cuff, w=250)


def slippers_spider(seed=3386):
    col = rgb("#2f2b33")

    def det(art, x, y, s):
        web(art, x - 12, y + 100, 34, rgb("#c8c8d4"), 0.7, spokes=8, rings_=3)

    return boots(seed, col, detail=det, low=True, sole=rgb("#4a4048"), h=200)


def pair_gloves(seed, color, metal=False, cuff=None, detail=None, w=230, h=200, s=0.95, aura=None):
    a = Art(w, h, seed)
    if aura:
        glow(a, w / 2, h / 2, 110, aura, 0.35)
    glove(a, w / 2 - 50, h / 2, s, color, ang=-0.15, left=True, cuff=cuff, metal=metal, detail=detail)
    glove(a, w / 2 + 50, h / 2 + 4, s, color, ang=0.15, cuff=cuff, metal=metal, detail=detail)
    return a.image()


def gauntlets_ogre(seed=3390):
    return pair_gloves(seed, rgb("#6a6e76"), metal=True, cuff=rgb("#5a5e66"), w=290, h=240, s=1.25)


def gloves_missile_snaring(seed=3391):
    a = Art(250, 210, seed)
    glove(a, 75, 108, 0.95, LEATHER, ang=-0.15, left=True, cuff=LEATHER_D)
    glove(a, 175, 112, 0.95, LEATHER, ang=0.15, cuff=LEATHER_D)
    # An arrow caught between them.
    from obj_war import arrow_at

    arrow_at(a, 40, 40, 0.18, 170)
    return a.image()


def gloves_swimming(seed=3392):
    col = rgb("#5a8a7a")

    a = Art(240, 210, seed)
    for cx, ang, left in ((70, -0.15, True), (170, 0.15, False)):
        cy = 105
        # The webbing: a membrane between the fingers, under the glove.
        web_pts = rot_pts(place([(-30, -30), (-28, -62), (0, -78), (24, -64), (36, -54), (32, -20)], cx, cy, 0.95), cx, cy, ang)
        if left:
            web_pts = rot_pts(flip(place([(-30, -30), (-28, -62), (0, -78), (24, -64), (36, -54), (32, -20)], cx, cy, 0.95), cx), cx, cy, ang)
        a.shape(web_pts, tint(col, 0.35), outline=FINE * 1.3, corner=6, depth=2, mottle=0)
        glove(a, cx, cy, 0.95, col, ang=ang, left=left, cuff=shade(col, 0.2))
    return a.image()


def bracer(a, x, y, color, s=1.0, ang=0.0, detail=None):
    pts = rot_pts(place([(-30, -56), (30, -56), (24, 56), (-24, 56)], x, y, s), x, y, ang)
    a.shape(pts, color, outline=O, corner=12, depth=5, light_k=0.5, mottle=0.03, var=V, detail=(lambda art, p: detail(art, x, y, s, ang)) if detail else None)


def bracers(seed, color, detail=None, after=None, w=220, h=170):
    a = Art(w, h, seed)
    bracer(a, w / 2 - 44, h / 2, color, ang=-0.2, detail=detail)
    bracer(a, w / 2 + 44, h / 2, color, ang=0.2, detail=detail)
    if after:
        after(a)
    return a.image()


def bracers_archery(seed=3393):
    def det(art, x, y, s, ang):
        stitch_line(art, rot_pts([(x - 24, y - 46), (x - 20, y + 46)], x, y, ang), tint(LEATHER, 0.4))
        stitch_line(art, rot_pts([(x + 24, y - 46), (x + 20, y + 46)], x, y, ang), tint(LEATHER, 0.4))
        p = rot_pts([(x, y + 34), (x, y - 30)], x, y, ang)
        art.ink(p, FINE * 1.8, color=GOLD)
        art.ink(rot_pts([(x - 8, y - 20), (x, y - 32), (x + 8, y - 20)], x, y, ang), FINE * 1.8, color=GOLD, taper=False)
        art.ink(rot_pts([(x - 7, y + 34), (x, y + 26), (x + 7, y + 34)], x, y, ang), FINE * 1.6, color=GOLD, taper=False)

    return bracers(seed, LEATHER, detail=det)


def bracers_defense(seed=3394):
    def det(art, x, y, s, ang):
        for yy in (-40, 40):
            art.ink(rot_pts([(x - 26, y + yy), (x + 26, y + yy)], x, y, ang), DETAIL, color=GOLD, alpha=0.9)

    def after(a):
        for x in (66, 154):
            gem(a, x, 85, 10, GEMS["sapphire"], 0.4)

    return bracers(seed, STEEL, detail=det, after=after)


def belt(seed, color, w=230, h=190, thick=22, buckle=BRASS, plates=None, gem_color=None, buckle_size=1.0, runes=None):
    a = Art(w, h, seed)
    cx, cy = w / 2, h / 2
    rx, ry = w / 2 - thick - 22, h / 2 - thick * 0.6 - 22
    arc = [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in [0.5 + i * (2 * math.pi - 0.3) / 60 for i in range(61)]]
    a.ink(arc, thick + 8, color=INK, taper=False, wob=0.2, var=0.04)
    a.ink(arc, thick, color=color, taper=False, wob=0.2, var=0.04)
    a.ink([(x - 1, y - 1) for x, y in arc], thick * 0.25, color=tint(color, 0.35), alpha=0.6, taper=False, wob=0.2, var=0.04)
    stitch_line(a, [(cx + (rx - thick * 0.32) * math.cos(t), cy + (ry - thick * 0.32) * math.sin(t)) for t in [0.6 + i * 0.1 for i in range(56)]], tint(color, 0.4), gap=6)
    if plates:
        for k in range(8):
            t = 1.0 + k * 0.62
            x, y = cx + rx * math.cos(t), cy + ry * math.sin(t)
            a.shape(rot_pts(rect(x - thick * 0.5, y - thick * 0.42, x + thick * 0.5, y + thick * 0.42), x, y, t), plates, outline=FINE * 1.6, corner=3, depth=2, light_k=0.5, mottle=0)
    if runes:
        rune_marks(a, cx, cy, (rx + ry) / 2 * 0.92, 12, runes, width=FINE * 1.3)
    bx, by = cx + rx * math.cos(0.3), cy + ry * math.sin(0.3)
    bs = thick * buckle_size
    a.shape(rot_pts(rect(bx - bs * 0.8, by - bs * 0.95, bx + bs * 0.8, by + bs * 0.95), bx, by, 1.87), buckle, outline=O * 0.9, corner=5, depth=3, light_k=0.55, mottle=0)
    a.shape(rot_pts(rect(bx - bs * 0.45, by - bs * 0.6, bx + bs * 0.45, by + bs * 0.6), bx, by, 1.87), shade(buckle, 0.45), outline=FINE * 1.4, corner=3, depth=1, mottle=0)
    if gem_color:
        gem(a, bx, by, bs * 0.4, gem_color, 0.0)
    return a.image()


# -- head ----------------------------------------------------------------------------------------


def head_canvas(seed, s=170):
    a = Art(s, s, seed)
    m = s / 2
    soft_shadow(a, (m, m), s * 0.34, 4, 5)
    return a, m


def hat_of_disguise(seed=3400):
    a = Art(220, 200, seed)
    cx, cy = 110, 100
    soft_shadow(a, (cx, cy), 84, 4, 5)
    a.shape(ellipse(cx, cy, 92, 76, 64), RED, depth=8, light_k=0.35)
    a.shape(ellipse(cx, cy - 4, 46, 40, 48), shade(RED, 0.1), depth=6, light_k=0.4)
    a.ink(ellipse(cx, cy - 4, 46, 40, 48), DETAIL * 3.2, closed=True, color=INK)
    a.ink(ellipse(cx, cy - 4, 46, 40, 48), DETAIL * 1.8, closed=True, color=GOLD)
    feather = chaikin([(cx + 30, cy - 20), (cx + 70, cy - 70), (cx + 96, cy - 92), (cx + 60, cy - 52)], True, 2)
    a.shape(feather, rgb("#ece4d0"), outline=DETAIL * 1.2, corner=0, depth=2, mottle=0)
    a.ink([(cx + 32, cy - 22), (cx + 92, cy - 88)], FINE, color=shade(rgb("#ece4d0"), 0.4))
    return a.image()


def helm(seed, metal, trim=None, after=None, aura=None, s=170):
    a, m = head_canvas(seed, s)
    if aura:
        glow(a, m, m, 80, aura, 0.4)
    helm_top(a, m, m, 56, metal, trim=trim)
    if after:
        after(a, m)
    return a.image()


def helm_brilliance(seed=3401):
    def after(a, m):
        cols = [GEMS["diamond"], GEMS["ruby"], GEMS["topaz"], GEMS["opal"]]
        for k in range(12):
            t = 2 * math.pi * k / 12
            gem(a, m + 46 * math.cos(t), m + 50 * math.sin(t), 6, cols[k % 4])
        gem(a, m, m, 9, GEMS["diamond"], 0.3)

    return helm(seed, GOLD, trim=None, after=after, aura=rgb("#ffe6a0"))


def helm_languages(seed=3402):
    def after(a, m):
        for side in (-1, 1):
            a.shape([(m + side * 52, m - 10), (m + side * 82, m - 24), (m + side * 76, m + 6), (m + side * 54, m + 14)], BRONZE, outline=O * 0.9, corner=4, depth=3, light_k=0.5, mottle=0)
        rune_marks(a, m, m, 44, 12, shade(BRONZE, 0.6), width=FINE * 1.5)

    return helm(seed, BRONZE, after=after, s=180)


def helm_telepathy(seed=3403):
    def after(a, m):
        for r in (66, 76):
            a.ink([(m + r * math.cos(t), m + r * math.sin(t)) for t in [-2.6 + i * 0.1 for i in range(10)]], FINE * 1.6, color=ARCANE, alpha=0.8)
            a.ink([(m + r * math.cos(t), m + r * math.sin(t)) for t in [-1.5 + i * 0.1 for i in range(10)]], FINE * 1.6, color=ARCANE, alpha=0.8)
        gem(a, m, m + 30, 9, GEMS["amethyst"], 0.5)

    return helm(seed, SILVER, trim=ARCANE, after=after, s=180)


def helm_teleportation(seed=3404):
    def after(a, m):
        pts = [(m + (4 + t * 5) * math.cos(t * 1.1), m - 6 + (4 + t * 5) * math.sin(t * 1.1)) for t in [i * 0.2 for i in range(40)]]
        a.ink(pts, DETAIL * 1.1, color=SKYGLOW)

    return helm(seed, rgb("#7f8a98"), after=after, aura=SKYGLOW)


def circlet(seed, metal, gem_color, r=56, aura=None, band=6):
    a = Art(170, 160, seed)
    cx, cy = 85, 80
    if aura:
        glow(a, cx, cy + 50, 50, aura, 0.5)
    pts = ellipse(cx, cy, r, r * 0.86, 64)
    a.ink(pts, band + 8, closed=True, color=INK, wob=0.2, var=0.05)
    a.ink(pts, band, closed=True, color=metal, wob=0.2, var=0.05)
    a.ink([(x - 1.5, y - 1.5) for x, y in pts], band * 0.3, closed=True, color=tint(metal, 0.6), alpha=0.6, wob=0.2)
    a.shape([(cx - 14, cy + r * 0.86 - 2), (cx, cy + r * 0.86 - 16), (cx + 14, cy + r * 0.86 - 2), (cx, cy + r * 0.86 + 12)], metal, outline=FINE * 1.6, corner=2, depth=2, mottle=0)
    gem(a, cx, cy + r * 0.86 - 2, 7, gem_color)
    return a.image()


def goggles_of_night(seed=3410):
    a = Art(200, 130, seed)
    cy = 66
    strap = chaikin([(40, cy), (30, cy - 40), (100, cy - 54), (170, cy - 40), (160, cy)], False, 2)
    a.ink(strap, 11, color=INK, taper=False)
    a.ink(strap, 6, color=LEATHER_D, taper=False)
    for x in (66, 134):
        a.shape(ellipse(x, cy, 30, 28, 40), BRASS, outline=O, depth=3, light_k=0.5, mottle=0)
        a.shape(ellipse(x, cy, 21, 20, 36), rgb("#2a3448"), outline=FINE * 1.4, depth=2, light_k=0.3, mottle=0)
        a.ink([(x - 10, cy - 8), (x - 3, cy - 13)], FINE * 1.6, color=rgb("#7ab0d8"), alpha=0.9)
    a.shape(rect(92, cy - 6, 108, cy + 6), BRASS, outline=FINE * 1.6, corner=3, depth=1, mottle=0)
    return a.image()


def lens_case(seed, tint_c, after=None):
    a = Art(170, 120, seed)
    soft_shadow(a, rect(16, 18, 154, 102), dx=4, dy=5)
    a.shape(rect(16, 18, 154, 102), LEATHER_D, outline=O, corner=14, depth=5, mottle=0.04)
    a.shape(rect(26, 28, 144, 92), rgb("#5a3a5a"), outline=DETAIL * 1.1, corner=10, depth=3, shade_k=0.2, light_k=0, ao=0.5)
    for x in (58, 112):
        a.shape(ellipse(x, 60, 20, 20, 32), tint_c, outline=DETAIL * 1.2, depth=2, light_k=0.6, mottle=0, shade_k=0.2)
        dot(a, x, 60, 6, shade(tint_c, 0.4), 0.7)
        a.ink([(x - 10, 52), (x - 4, 47)], FINE * 1.6, color=(255, 255, 255), alpha=0.9)
        if after:
            after(a, x, 60)
    return a.image()


def eyes_minute(seed=3412):
    def after(a, x, y):
        for k in range(3):
            a.ink([(x - 8, y + 4 + k * 3), (x + 8, y + 4 + k * 3)], FINE * 0.7, color=INK, alpha=0.5)

    return lens_case(seed, rgb("#dce8ee"), after)


# -- registry -----------------------------------------------------------------------------------


SRD_ARMOR = {
    "Padded Armor": padded,
    "Leather Armor": leather,
    "Studded Leather Armor": studded,
    "Hide Armor": hide,
    "Chain Shirt": chain_shirt,
    "Scale Mail": scale_mail,
    "Breastplate": breastplate,
    "Half Plate Armor": half_plate,
    "Ring Mail": ring_mail,
    "Chain Mail": chain_mail,
    "Splint Armor": splint,
    "Plate Armor": plate,
    # magic armor
    "Adamantine Armor": lambda: plate_suit(3323, metal=ADAMANT, trim=rgb("#8aa89a")),
    "Mithral Armor": mithral,
    "Dragon Scale Mail": dragon_scale,
    **{f"Dragon Scale Mail ({k})": (lambda c=c, i=i: dragon_scale(c, 3330 + i)) for i, (k, c) in enumerate(DRAGON.items())},
    "Elven Chain": elven_chain,
    "Dwarven Plate": lambda: plate_suit(3324, metal=rgb("#8e9096"), trim=GOLD, runes=GOLD, stocky=True),
    "Demon Armor": lambda: plate_suit(3325, metal=DEMON, spikes=True, seams=EMBER, trim=rgb("#6a2a2a")),
    "Glamoured Studded Leather": glamoured,
    "Plate Armor of Etherealness": lambda: plate_suit(3327, metal=GHOST, trim=rgb("#e8f6ff"), aura=GHOST, alpha_ghost=0.7),
    "Armor of Invulnerability": lambda: plate_suit(3328, metal=rgb("#c4c8d0"), trim=GOLD, gems=((0, -30, GEMS["diamond"]),), aura=rgb("#fff0b0")),
    "Armor of Resistance": armor_of_resistance,
    "Armor of Vulnerability": lambda: plate_suit(3329, metal=rgb("#7a7488"), trim=rgb("#5a3a6a"), runes=rgb("#8a4ca0"), dent=True),
    # magic shields
    "Animated Shield": animated_shield,
    "Arrow-Catching Shield": arrow_catching,
    "Shield of Missile Attraction": missile_attraction,
    "Spellguard Shield": spellguard,
    "Sentinel Shield": sentinel,
    # clothes
    "Fine Clothes": fine_clothes,
    "Traveler's Clothes": travelers_clothes,
    "Costume": costume,
    "Robe": robe,
    # magic wearables
    "Boots of Elvenkind": boots_elvenkind,
    "Boots of Levitation": boots_levitation,
    "Boots of Speed": boots_speed,
    "Boots of Striding and Springing": boots_striding,
    "Boots of the Winterlands": boots_winterlands,
    "Winged Boots": winged_boots,
    "Slippers of Spider Climbing": slippers_spider,
    "Bracers of Archery": bracers_archery,
    "Bracers of Defense": bracers_defense,
    "Gauntlets of Ogre Power": gauntlets_ogre,
    "Gloves of Missile Snaring": gloves_missile_snaring,
    "Gloves of Swimming and Climbing": gloves_swimming,
    "Belt of Dwarvenkind": lambda: belt(3395, rgb("#6a4a2e"), thick=28, buckle=BRONZE, plates=BRONZE, runes=None),
    "Belt of Giant Strength": lambda: belt(3396, LEATHER, w=280, h=230, thick=34, buckle=GOLD, gem_color=RED, buckle_size=1.25),
    "Cloak of Arachnida": cloak_arachnida,
    "Cloak of Displacement": cloak_displacement,
    "Cloak of Elvenkind": cloak_elvenkind,
    "Cloak of Protection": cloak_protection,
    "Cloak of the Bat": cloak_bat,
    "Cloak of the Manta Ray": cloak_manta,
    "Cape of the Mountebank": cape_mountebank,
    "Mantle of Spell Resistance": mantle_spell_resistance,
    "Robe of Eyes": robe_of_eyes,
    "Robe of Scintillating Colors": robe_scintillating,
    "Robe of Stars": robe_of_stars,
    "Robe of the Archmagi": robe_archmagi,
    "Robe of the Archmagi (Gray)": lambda: robe_archmagi(3376, rgb("#8a8a90"), SILVER),
    "Robe of the Archmagi (Black)": lambda: robe_archmagi(3377, rgb("#2e2a32"), rgb("#b04a4a")),
    "Robe of Useful Items": robe_useful_items,
    "Hat of Disguise": hat_of_disguise,
    "Helm of Brilliance": helm_brilliance,
    "Helm of Comprehending Languages": helm_languages,
    "Helm of Telepathy": helm_telepathy,
    "Helm of Teleportation": helm_teleportation,
    "Headband of Intellect": lambda: circlet(3405, rgb("#4a5a8a"), GEMS["sapphire"], band=12),
    "Circlet of Blasting": lambda: circlet(3406, GOLD, GEMS["ruby"], aura=EMBER),
    "Goggles of Night": goggles_of_night,
    "Eyes of Charming": lambda: lens_case(3411, rgb("#e8b8d8")),
    "Eyes of Minute Seeing": eyes_minute,
    "Eyes of the Eagle": lambda: lens_case(3413, rgb("#e8c060")),
    "Wings of Flying": wings_of_flying,
}

SRD_ARMOR_COLORABLE = {
    "Padded Armor",
    "Dragon Scale Mail",
    "Armor of Resistance",
    "Fine Clothes",
    "Traveler's Clothes",
    "Costume",
    "Robe",
    "Cloak of Protection",
    "Cape of the Mountebank",
    "Hat of Disguise",
    "Belt of Giant Strength",
}
