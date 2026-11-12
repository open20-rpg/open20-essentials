"""SRD 5.2.1 weapons: the simple and martial weapons the pack didn't have
yet, their ammunition, and the SRD's named magic weapons. Lying flat, seen
from above, in the same pen style as obj_war (whose weapons this reuses)."""

import math

from kit import BRASS, IRON, RED, WOOD, WOOD_DARK, WOOD_LIGHT, dot
from obj_craft import STEEL, axe_at, hammer_at, handle, rot_pts
from obj_magic import glow
from obj_war import LEATHER, O, V, blade_shape
from pen import DETAIL, FINE, INK, Art, chaikin, ellipse, rect, rgb, shade, tint, to_path

GOLD = rgb("#d6ae4c")
SILVER = rgb("#c4cad2")
DARK_STEEL = rgb("#4c4f58")
BLACK_IRON = rgb("#34323a")
FEATHER = rgb("#e6dcc4")
LEAD = rgb("#7d8088")
CORD = rgb("#c9b48a")
FIRE = rgb("#f08a3a")
FIRE_HOT = rgb("#ffd36a")
ICE = rgb("#bfe2f0")
FROST = rgb("#9fd2f2")
VENOM = rgb("#7cbf3e")
BLOOD = rgb("#9a2b2b")
ARCANE = rgb("#9a72e0")
HOLY = rgb("#ffe9a0")
SEA = rgb("#4fc2b0")
SPARK = rgb("#cfe6ff")


# -- canvas -------------------------------------------------------------------------------------


def item(draw, w, h, seed, margin=6):
    """An asset drawn on a roomy canvas and cropped to what was drawn (plus a
    margin), so no weapon is ever cut by the canvas edge."""

    P = 70  # room for glows that spill past the drawing

    def make():
        a = Art(w + 2 * P, h + 2 * P, seed)
        a.c.translate(P, P)
        draw(a)
        img = a.image()
        box = img.getchannel("A").point(lambda v: 255 if v > 3 else 0).getbbox()
        if not box:
            return img
        x0, y0, x1, y1 = box
        return img.crop((max(0, x0 - margin), max(0, y0 - margin), min(a.w, x1 + margin), min(a.h, y1 + margin)))

    return make


def aura(a, pts, color, alpha=0.5, width=22, blur=10):
    """A soft glow around a shape (drawn under it)."""
    p = to_path(pts)
    a.stroke_path(p, color, width, alpha, blur=blur)
    a.fill_path(p, color, alpha, blur=blur)


def line_glow(a, p0, p1, color, width=30, alpha=0.45):
    a.stroke_path(to_path([p0, p1], False), color, width, alpha, blur=width * 0.45)


def runes(a, pts, color, size=5, width=FINE * 1.1, alpha=0.95):
    """Little carved glyphs at the given points (alternating shapes)."""
    for k, (x, y) in enumerate(pts):
        s = size
        shapes = (
            [[(x - s * 0.5, y - s), (x - s * 0.5, y + s)], [(x - s * 0.5, y - s * 0.2), (x + s * 0.6, y - s)]],
            [[(x - s * 0.6, y + s), (x, y - s), (x + s * 0.6, y + s)]],
            [[(x - s * 0.6, y - s), (x + s * 0.6, y + s)], [(x + s * 0.6, y - s), (x - s * 0.6, y + s)]],
            [[(x, y - s), (x, y + s)], [(x - s * 0.6, y), (x + s * 0.6, y)]],
        )[k % 4]
        for seg in shapes:
            a.ink(seg, width, color=color, alpha=alpha, wob=0, taper=False, var=0)


def bolt_zigzag(a, p0, p1, rng, n=7, jag=10, color=SPARK, glow_c=rgb("#7fb6ff")):
    """A lightning bolt from p0 to p1: dark edge, bright core, blue glow."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    pts = [p0]
    for k in range(1, n):
        t = k / n
        d = rng.uniform(-jag, jag) * (1 if k % 2 else -1)
        pts.append((x0 + (x1 - x0) * t + nx * d, y0 + (y1 - y0) * t + ny * d))
    pts.append(p1)
    a.stroke_path(to_path(pts, False), glow_c, 16, 0.5, blur=7)
    a.ink(pts, 6.5, color=rgb("#2c3c78"), taper=True, wob=0, var=0.1)
    a.ink(pts, 3.2, color=color, taper=True, wob=0, var=0.1)


def flame(a, x, y, ang, size):
    """A flame licking out toward `ang`: an orange tongue with a hot core."""
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    tip = (x + ux * size * 1.7, y + uy * size * 1.7)
    pts = chaikin([(x - nx * size * 0.55, y - ny * size * 0.55), (x + ux * size * 0.7 - nx * size * 0.5, y + uy * size * 0.7 - ny * size * 0.5), tip, (x + ux * size * 0.7 + nx * size * 0.45, y + uy * size * 0.7 + ny * size * 0.45), (x + nx * size * 0.55, y + ny * size * 0.55), (x - ux * size * 0.3, y - uy * size * 0.3)], True, 2)
    a.shape(pts, FIRE, outline=FINE * 1.3, outline_color=rgb("#8a3a1a"), corner=0, wob=0.3, depth=2, shade_k=0.2, light_k=0.4, ao=0, mottle=0)
    core = [(x + (px - x) * 0.5, y + (py - y) * 0.5) for px, py in pts]
    a.shape(core, FIRE_HOT, outline=0, corner=0, wob=0.2, shade_k=0, light_k=0, ao=0, mottle=0)


def snowflake(a, x, y, r, color=(250, 252, 255)):
    for k in range(3):
        t = k * math.pi / 3
        a.ink([(x - r * math.cos(t), y - r * math.sin(t)), (x + r * math.cos(t), y + r * math.sin(t))], 3.4, color=rgb("#4a7ea0"), taper=False, wob=0, var=0)
    for k in range(3):
        t = k * math.pi / 3
        a.ink([(x - r * math.cos(t), y - r * math.sin(t)), (x + r * math.cos(t), y + r * math.sin(t))], 1.6, color=color, taper=False, wob=0, var=0)


def drip(a, x, y, r, color):
    a.shape([(x, y - r * 1.8), (x + r, y), (x + r * 0.7, y + r * 0.8), (x, y + r), (x - r * 0.7, y + r * 0.8), (x - r, y)], color, outline=FINE * 1.2, corner=0, wob=0.1, depth=1.5, light_k=0.5, ao=0, mottle=0)


def sparkle(a, x, y, r, color=(255, 255, 250)):
    pts = []
    for k in range(8):
        t = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.28
        pts.append((x + rr * math.cos(t), y + rr * math.sin(t)))
    glow(a, x, y, r * 1.4, color, 0.5)
    a.shape(pts, color, outline=FINE * 1.1, corner=0, wob=0, shade_k=0, light_k=0, ao=0, mottle=0)


def gem(a, x, y, r, color):
    a.shape(ellipse(x, y, r, r, 20), color, outline=FINE * 1.3, depth=2, light_k=0.6, mottle=0)
    dot(a, x - r * 0.3, y - r * 0.3, r * 0.28, tint(color, 0.7))


# -- swords -------------------------------------------------------------------------------------


def blade_outline(x, y, bx, Lb, w, kind="straight", curve=0.0, serrate=False):
    """The blade's outline (local, unrotated: the blade runs along +x from
    `bx`), plus a function giving its centerline at t in 0..1."""

    def c(t):
        return (bx + Lb * t, y + curve * Lb * t * t)

    def prof(t):
        if kind == "curved":  # single-edged, widening toward the tip, edge on the outer side
            tip = min(1.0, (1 - t) / 0.22)
            return w * 0.32 * min(1.0, (1 - t) / 0.08), w * (0.45 + 0.5 * t) * (tip**0.6)
        if kind == "thin":  # rapier: tapering all along
            hw = w / 2 * (1 - 0.45 * t) * min(1.0, (1 - t) / 0.08)
            return hw, hw
        if kind == "leaf":
            hw = w / 2 * (1 + 0.25 * math.sin(math.pi * min(1, t / 0.8))) * min(1.0, (1 - t) / 0.2)
            return hw, hw
        hw = w / 2 * min(1.0, (1 - t) / 0.13)
        return hw, hw

    N = 36
    top, bot = [], []
    for i in range(N + 1):
        t = i / N
        cx, cy = c(t)
        dx, dy = Lb, 2 * curve * Lb * t
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        ht, hb = prof(t)
        if serrate and 0.08 < t < 0.8 and i % 2:
            hb += 4.5
        top.append((cx - nx * ht, cy - ny * ht))
        bot.append((cx + nx * hb, cy + ny * hb))
    return top + bot[::-1][1:], c


def sword(
    a,
    x,
    y,
    ang,
    L=230,
    w=16,
    grip=44,
    blade=STEEL,
    guard=BRASS,
    wrap=LEATHER,
    pommel=BRASS,
    span=30,
    kind="straight",
    curve=0.0,
    guard_kind="bar",
    glow_c=None,
    glow_a=0.5,
    fuller=True,
    serrate=False,
    outline_color=None,
    pommel_gem=None,
    guard_gem=None,
    detail=None,
    before=None,
    blade_outline_w=O,
):
    """A sword lying flat: pommel, wrapped grip, guard and blade (generic
    enough for short swords, greatswords, scimitars, rapiers and the magic
    blades). `detail(art, loc, c)` draws on the blade (clipped);
    `before(art, loc, blade_pts)` under it (flames, glows)."""
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    gx = x + 8 + grip
    bx = gx + 5
    pts, c = blade_outline(x, y, bx, x + L - bx, w, kind, curve, serrate)
    bpts = loc(pts)
    if glow_c:
        aura(a, bpts, glow_c, glow_a)
    if before:
        before(a, loc, bpts)
    # Grip with its diagonal wrap, then the pommel.
    def wrapping(art, p):
        for k in range(int(grip / 9)):
            gx0 = x + 10 + k * 9
            art.ink(loc([(gx0, y - 7), (gx0 + 6, y + 7)]), FINE * 1.1, color=shade(wrap, 0.5), alpha=0.8, wob=0)

    a.shape(loc(rect(x + 4, y - 6.5, gx, y + 6.5)), wrap, outline=O, corner=3, depth=2, mottle=0, var=V, detail=wrapping)
    a.shape(loc(ellipse(x, y, 9.5, 9.5, 20)), pommel, outline=O, depth=2, light_k=0.5, mottle=0, var=V)
    if pommel_gem:
        gem(a, *loc([(x, y)])[0], 4.5, pommel_gem)

    def on_blade(art, p):
        if fuller and kind != "thin":
            q = [c(t) for t in [0.02 + k * 0.035 for k in range(21)]]
            if kind == "curved":
                q = [(qx, qy + w * 0.05) for qx, qy in q]
            art.ink(loc(q), FINE * 1.2, color=shade(blade, 0.4), alpha=0.75, wob=0)
        if detail:
            detail(art, loc, c)

    a.shape(bpts, blade, outline=blade_outline_w, corner=0, wob=0.1, depth=2, light_k=0.55, mottle=0, var=V, detail=on_blade, outline_color=outline_color)
    # The guard.
    if guard_kind == "bar":
        a.shape(loc(rect(gx - 6, y - span, gx + 6, y + span)), guard, outline=O, corner=4, depth=2, light_k=0.5, mottle=0, var=V)
    elif guard_kind == "cross":
        a.shape(loc(rect(gx - 5, y - span, gx + 5, y + span)), guard, outline=O, corner=3, depth=2, light_k=0.5, mottle=0, var=V)
        for s in (-1, 1):
            a.shape(loc(ellipse(gx, y + s * span, 8, 8, 18)), guard, outline=O * 0.8, depth=2, light_k=0.5, mottle=0, var=V)
        a.shape(loc([(gx - 8, y - 10), (gx + 16, y), (gx - 8, y + 10)]), guard, outline=O * 0.8, corner=2, depth=2, light_k=0.5, mottle=0, var=V)
    elif guard_kind == "wings":  # dragon wings swept toward the blade
        for s in (-1, 1):
            wing = [(gx - 8, y + s * 4), (gx + 4, y + s * 6), (gx + 26, y + s * span * 1.25), (gx + 10, y + s * span * 0.95), (gx + 8, y + s * span * 1.1), (gx - 4, y + s * span * 0.8), (gx - 6, y + s * span * 0.95), (gx - 12, y + s * span * 0.5)]
            a.shape(loc(wing), guard, outline=O * 0.9, corner=1, depth=2, light_k=0.5, mottle=0, var=V)
        a.shape(loc(ellipse(gx, y, 10, 10, 20)), guard, outline=O * 0.9, depth=2, light_k=0.5, mottle=0, var=V)
    elif guard_kind == "shield":  # Defender: a small kite shield as the guard
        sh = [(gx - 10, y - span), (gx + 6, y - span * 0.9), (gx + 20, y), (gx + 6, y + span * 0.9), (gx - 10, y + span), (gx - 4, y)]
        a.shape(loc(chaikin(sh, True, 1)), guard, outline=O * 0.9, corner=0, depth=3, light_k=0.5, mottle=0, var=V)
    elif guard_kind == "ring":  # rapier: quillons, a side ring and the knuckle bow
        a.shape(loc(rect(gx - 4, y - span, gx + 4, y + span)), guard, outline=O * 0.8, corner=3, depth=2, light_k=0.5, mottle=0, var=V)
        ring = loc(ellipse(gx + 12, y + 2, 9, 15, 28))
        a.ink(ring, 8, closed=True, color=INK, wob=0, var=0)
        a.ink(ring, 4, closed=True, color=guard, wob=0, var=0)
        bow_ = loc(chaikin([(gx, y + span), (gx - grip * 0.4, y + span + 10), (x + 10, y + 16), (x + 4, y + 6)], False, 3))
        a.ink(bow_, 8.5, color=INK, taper=False, wob=0, var=0)
        a.ink(bow_, 4.2, color=guard, taper=False, wob=0, var=0)
        for s in (-1, 1):
            dot(a, *loc([(gx, y + s * span)])[0], 5, guard)
    if guard_gem:
        gem(a, *loc([(gx, y)])[0], 5.5, guard_gem)
    return loc, c


def sword_item(seed, L=230, w=16, ang=-0.15, **kw):
    H = int(abs(math.sin(ang)) * L + 160)
    return item(lambda a: sword(a, 40, H / 2 + math.sin(-ang) * L / 2, ang, L, w, **kw), L + 100, H, seed)


# -- hafted weapons ------------------------------------------------------------------------------


def haft_end(x, y, ang, L):
    return x + math.cos(ang) * L, y + math.sin(ang) * L


def greataxe_at(a, x, y, ang, L=290, blade=STEEL, haft=WOOD, glow_c=None):
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    head = [(hx - 14, hy - 10), (hx + 14, hy - 10), (hx + 38, hy - 52)]
    head += [(hx + 46 * math.cos(t), hy - 52 - 30 * math.sin(t)) for t in [0.15 + k * (math.pi - 0.3) / 14 for k in range(15)]]
    head += [(hx - 38, hy - 52)]
    if glow_c:
        aura(a, loc(head), glow_c, 0.5)
    handle(a, x, y, hx + math.cos(ang) * 14, hy + math.sin(ang) * 14, 13, haft)
    blade_shape(a, loc(head), blade)
    a.ink(loc(chaikin([(hx - 34, hy - 70), (hx, hy - 80), (hx + 34, hy - 70)], False, 2)), FINE * 1.4, color=tint(blade, 0.6), alpha=0.9)
    blade_shape(a, loc([(hx - 8, hy + 10), (hx + 8, hy + 10), (hx, hy + 40)]), blade)
    a.shape(loc(rect(hx - 15, hy - 13, hx + 15, hy + 13)), IRON, outline=O, corner=3, depth=2, mottle=0, var=V)
    return loc


def pick_at(a, x, y, ang, L=170, head=IRON):
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    handle(a, x, y, hx + math.cos(ang) * 10, hy + math.sin(ang) * 10, 11)
    spike = chaikin([(hx - 9, hy - 8), (hx + 9, hy - 8), (hx + 10, hy - 40), (hx + 14, hy - 78), (hx + 2, hy - 44)], True, 1)
    blade_shape(a, loc(spike), head)
    a.shape(loc(rect(hx - 12, hy + 6, hx + 12, hy + 30)), head, outline=O, corner=3, depth=3, light_k=0.5, mottle=0, var=V)
    a.shape(loc(rect(hx - 13, hy - 12, hx + 13, hy + 12)), shade(head, 0.15), outline=O, corner=3, depth=2, mottle=0, var=V)


def maul_at(a, x, y, ang, L=270, head=IRON, haft=WOOD, glow_c=None, detail=None):
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    block = loc(rect(hx - 28, hy - 50, hx + 28, hy + 50))
    if glow_c:
        aura(a, block, glow_c, 0.55, 30, 14)
    handle(a, x, y, hx + math.cos(ang) * 20, hy + math.sin(ang) * 20, 13, haft)

    def bands(art, p):
        for d in (-34, 34):
            art.ink(loc([(hx - 28, hy + d), (hx + 28, hy + d)]), DETAIL, color=shade(head, 0.45), alpha=0.85, taper=False, wob=0)
        if detail:
            detail(art, loc)

    a.shape(block, head, outline=O, corner=6, depth=4, light_k=0.5, mottle=0, var=V, detail=bands)


def hammer_head_at(a, x, y, ang, L=200, head=IRON, haft=WOOD, glow_c=None, detail=None, bands=None):
    """A warhammer: square face on one side, a short beak on the other."""
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    body = loc(rect(hx - 20, hy - 36, hx + 20, hy + 12))
    if glow_c:
        aura(a, body, glow_c, 0.55, 26, 12)
    handle(a, x, y, hx + math.cos(ang) * 10, hy + math.sin(ang) * 10, 12, haft)
    if bands:
        for t in (0.15, 0.55):
            bx, by = x + (hx - x) * t, y + (hy - y) * t
            a.shape(rot_pts(rect(bx - 6, by - 9, bx + 6, by + 9), bx, by, ang), bands, outline=FINE * 1.6, corner=2, depth=1, light_k=0.5, mottle=0)
    a.shape(body, head, outline=O, corner=4, depth=3, light_k=0.5, mottle=0, var=V, detail=(lambda art, p: detail(art, loc)) if detail else None)
    blade_shape(a, loc([(hx - 9, hy + 12), (hx + 9, hy + 12), (hx, hy + 46)]), head)


def spiked_ball(a, cx, cy, r, color=IRON, n=10, spike=1.0, flanged=False):
    for k in range(n):
        t = 2 * math.pi * k / n + 0.2
        if flanged:
            pts = [(cx + r * 0.7 * math.cos(t - 0.22), cy + r * 0.7 * math.sin(t - 0.22)), (cx + r * 1.45 * math.cos(t), cy + r * 1.45 * math.sin(t)), (cx + r * 0.7 * math.cos(t + 0.22), cy + r * 0.7 * math.sin(t + 0.22))]
        else:
            pts = [(cx + r * 0.85 * math.cos(t - 0.2), cy + r * 0.85 * math.sin(t - 0.2)), (cx + r * (1 + 0.75 * spike) * math.cos(t), cy + r * (1 + 0.75 * spike) * math.sin(t)), (cx + r * 0.85 * math.cos(t + 0.2), cy + r * 0.85 * math.sin(t + 0.2))]
        blade_shape(a, pts, shade(color, 0.05))
    a.shape(ellipse(cx, cy, r, r, 32), color, outline=O, depth=3, light_k=0.5, mottle=0, var=V)
    if not flanged:
        blade_shape(a, ellipse(cx - 1, cy - 1, r * 0.3, r * 0.3, 12), tint(color, 0.15))


def mace2_at(a, x, y, ang, L=170, head=IRON, haft=WOOD, glow_c=None, glow_a=0.55):
    hx, hy = haft_end(x, y, ang, L)
    if glow_c:
        glow(a, hx, hy, 70, glow_c, glow_a)
    handle(a, x, y, hx, hy, 11, haft)
    spiked_ball(a, hx, hy, 22, head, 8, flanged=True)


def javelin_at(a, x, y, ang, L=240, head=STEEL, haft=WOOD_LIGHT):
    hx, hy = haft_end(x, y, ang, L)
    handle(a, x, y, hx, hy, 8, haft)
    mx, my = x + (hx - x) * 0.45, y + (hy - y) * 0.45
    a.shape(rot_pts(rect(mx - 18, my - 7, mx + 18, my + 7), mx, my, ang), LEATHER, outline=FINE * 1.8, corner=3, depth=1, mottle=0)
    blade_shape(a, rot_pts([(hx - 6, hy - 7), (hx + 8, hy - 8), (hx + 40, hy), (hx + 8, hy + 8), (hx - 6, hy + 7)], hx, hy, ang), head)
    return hx, hy


def trident_at(a, x, y, ang, L=300, metal=STEEL, haft=WOOD, glow_c=None):
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    if glow_c:
        glow(a, *loc([(hx + 40, hy)])[0], 80, glow_c, 0.5)
    handle(a, x, y, hx, hy, 10, haft)
    for d in (-24, 0, 24):
        L2 = 86 if d == 0 else 72
        prong = [(hx + 6, hy + d - 4), (hx + L2, hy + d - 4), (hx + L2 + 18, hy + d), (hx + L2, hy + d + 4), (hx + 6, hy + d + 4)]
        blade_shape(a, loc(prong), metal)
        s = -1 if d < 0 else 1
        if d:
            blade_shape(a, loc([(hx + L2 - 2, hy + d + s * 3), (hx + L2 - 14, hy + d + s * 13), (hx + L2 - 14, hy + d + s * 3)]), metal)
    a.shape(loc(rect(hx - 4, hy - 30, hx + 10, hy + 30)), metal, outline=O, corner=5, depth=2, light_k=0.5, mottle=0, var=V)


def arrow2_at(a, x, y, ang, L=150, shaft=WOOD_LIGHT, head=IRON, vanes=FEATHER, head_glow=None):
    hx, hy = haft_end(x, y, ang, L)
    if head_glow:
        glow(a, hx, hy, 34, head_glow, 0.6)
    a.ink([(x, y), (hx, hy)], 7, color=INK, taper=False, var=V)
    a.ink([(x, y), (hx, hy)], 3.5, color=shaft, taper=False, var=V)
    blade_shape(a, rot_pts([(hx - 2, hy - 6), (hx + 16, hy), (hx - 2, hy + 6)], hx, hy, ang), head)
    for s in (-1, 1):
        a.shape(rot_pts([(x + 8, y), (x + 34, y), (x + 26, y + s * 9), (x, y + s * 9)], x, y, ang), vanes, outline=FINE * 1.3, corner=1, depth=1, mottle=0)


def bolt_at(a, x, y, ang, L=105):
    hx, hy = haft_end(x, y, ang, L)
    a.ink([(x, y), (hx, hy)], 9, color=INK, taper=False, var=V)
    a.ink([(x, y), (hx, hy)], 5, color=WOOD, taper=False, var=V)
    blade_shape(a, rot_pts([(hx - 3, hy - 7), (hx + 18, hy), (hx - 3, hy + 7)], hx, hy, ang), IRON)
    for s in (-1, 1):
        a.shape(rot_pts([(x + 4, y), (x + 24, y), (x + 20, y + s * 8), (x + 2, y + s * 8)], x, y, ang), rgb("#cdbfa2"), outline=FINE * 1.3, corner=1, depth=1, mottle=0)


def longbow_at(a, x, y, ang, L=380, wood=WOOD, string=FEATHER, grip=LEATHER):
    loc = lambda pts: rot_pts(pts, x, y, ang)  # noqa: E731
    limb = chaikin([(x, y - L / 2), (x + 34, y - L / 4), (x + 42, y), (x + 34, y + L / 4), (x, y + L / 2)], False, 3)
    a.ink(loc(limb), 13, color=INK, taper=True, var=V)
    a.ink(loc(limb), 8, color=wood, taper=True, var=V)
    a.ink(loc([(x, y - L / 2), (x, y + L / 2)]), FINE * 1.1, color=string, wob=0)
    a.shape(loc(rect(x + 32, y - 16, x + 48, y + 16)), grip, outline=O * 0.8, corner=3, depth=1, mottle=0, var=V)
    return loc, limb


# -- simple weapons --------------------------------------------------------------------------------


def club_at(a, x, y, ang, L=200, fat=26, studs=0, wood=WOOD):
    top = [(x, y - 6), (x + L * 0.35, y - 8), (x + L * 0.75, y - fat * 0.75), (x + L - 8, y - fat), (x + L + 4, y - fat * 0.4)]
    bot = [(x + L + 4, y + fat * 0.5), (x + L - 10, y + fat * 0.95), (x + L * 0.7, y + fat * 0.7), (x + L * 0.35, y + 8), (x, y + 6)]
    pts = rot_pts(chaikin(top + bot, True, 2), x, y, ang)

    def knots(art, p):
        for t, d in ((0.5, -4), (0.72, 6), (0.88, -10)):
            kx, ky = rot_pts([(x + L * t, y + d)], x, y, ang)[0]
            art.ink(ellipse(kx, ky, 5, 3.5, 12, rot=ang), FINE * 1.2, closed=True, color=shade(wood, 0.5), alpha=0.8)
        art.ink(rot_pts([(x + 10, y - 1), (x + L * 0.6, y - 4), (x + L - 10, y - fat * 0.3)], x, y, ang), FINE, color=shade(wood, 0.45), alpha=0.6)

    a.shape(pts, wood, outline=O, corner=0, depth=4, light_k=0.4, mottle=0.04, var=V, detail=knots)
    a.shape(rot_pts(rect(x - 2, y - 8, x + 40, y + 8), x, y, ang), LEATHER, outline=O * 0.8, corner=3, depth=1, mottle=0, var=V)
    for k in range(studs):
        t = 0.62 + 0.36 * (k // 2) / max(1, (studs - 1) // 2)
        d = (-1 if k % 2 else 1) * fat * 0.45 * (0.6 + 0.5 * t)
        sx, sy = rot_pts([(x + L * t, y + d)], x, y, ang)[0]
        a.shape(ellipse(sx, sy, 5.5, 5.5, 14), IRON, outline=FINE * 1.4, depth=1.5, light_k=0.6, mottle=0)


def quarterstaff_at(a, x, y, ang, L=420):
    hx, hy = haft_end(x, y, ang, L)
    handle(a, x, y, hx, hy, 13, WOOD)
    for t in (0.0, 1.0):
        cx, cy = x + (hx - x) * t, y + (hy - y) * t
        a.shape(rot_pts(rect(cx - 10, cy - 9, cx + 10, cy + 9), cx, cy, ang), IRON, outline=FINE * 1.8, corner=3, depth=1.5, light_k=0.5, mottle=0)
    for t in (0.36, 0.64):
        cx, cy = x + (hx - x) * t, y + (hy - y) * t
        a.shape(rot_pts(rect(cx - 20, cy - 9, cx + 20, cy + 9), cx, cy, ang), LEATHER, outline=FINE * 1.8, corner=3, depth=1, mottle=0)


def sickle_at(a, x, y, ang, L=80):
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    R = 52
    outer, inner = [], []
    N = 26
    for i in range(N + 1):
        th = math.pi / 2 - (math.pi * 1.25) * i / N
        cx, cy = hx + 8 + R * math.cos(th) * 0.95, hy - R + R * math.sin(th)
        nx, ny = math.cos(th), math.sin(th)
        hw = 15 * (1 - i / N) ** 0.7 + 1
        outer.append((cx + nx * hw * 0.6, cy + ny * hw * 0.6))
        inner.append((cx - nx * hw, cy - ny * hw))
    blade_shape(a, loc(outer + inner[::-1]))
    a.ink(loc(inner[2:-3]), FINE * 1.3, color=tint(STEEL, 0.6), alpha=0.9, wob=0)
    handle(a, x, y, hx + math.cos(ang) * 6, hy + math.sin(ang) * 6, 12, WOOD)
    a.shape(loc(rect(hx - 4, hy - 8, hx + 12, hy + 8)), IRON, outline=FINE * 1.8, corner=2, depth=1, mottle=0)


def dart_at(a, x, y, ang, L=80):
    hx, hy = haft_end(x, y, ang, L)
    a.ink([(x, y), (hx, hy)], 8, color=INK, taper=False, var=V)
    a.ink([(x, y), (hx, hy)], 4, color=WOOD_LIGHT, taper=False, var=V)
    blade_shape(a, rot_pts([(hx - 14, hy - 5), (hx + 2, hy - 6), (hx + 20, hy), (hx + 2, hy + 6), (hx - 14, hy + 5)], hx, hy, ang), STEEL)
    for s in (-1, 1):
        a.shape(rot_pts([(x + 2, y), (x + 22, y), (x + 14, y + s * 10), (x - 2, y + s * 10)], x, y, ang), RED_FEATHER, outline=FINE * 1.3, corner=1, depth=1, mottle=0)


RED_FEATHER = rgb("#b5523e")


def sling(a):
    cx, cy = 150, 95
    for s, end in ((-1, [(40, 60), (20, 40), (36, 22), (56, 36), (40, 60)]), (1, [(262, 140), (282, 150)])):
        cords = chaikin([(cx + s * 26, cy), (cx + s * 60, cy + s * 18), (cx + s * 90, cy - 6), (cx + s * 112, cy + s * 30)] + ([(56, 60)] if s < 0 else [(262, 140)]), False, 3)
        a.ink(cords, 6.5, color=INK, taper=False, wob=0.6)
        a.ink(cords, 3, color=CORD, taper=False, wob=0.6)
        if s < 0:
            loop = ellipse(46, 54, 16, 12, 24)
            a.ink(loop, 6.5, closed=True, color=INK)
            a.ink(loop, 3, closed=True, color=CORD)
        else:
            dot(a, 266, 142, 6, INK)
            dot(a, 266, 142, 3.5, CORD)
    pouch = chaikin([(cx - 30, cy), (cx - 8, cy - 22), (cx + 8, cy - 22), (cx + 30, cy), (cx + 8, cy + 22), (cx - 8, cy + 22)], True, 2)
    a.shape(pouch, LEATHER, outline=O, corner=0, depth=4, light_k=0.35, mottle=0.04)
    a.shape(ellipse(cx, cy, 11, 10, 20), STONE_GREY, outline=FINE * 1.5, depth=2, light_k=0.5, mottle=0)


STONE_GREY = rgb("#9b968c")


def whip(a):
    # Handle, then the lash coiled in loose loops ending in a thin popper.
    x0, y0 = 30, 150
    handle(a, x0, y0, x0 + 80, y0 - 30, 12, LEATHER)
    dot(a, x0, y0, 9, shade(LEATHER, 0.2))
    pts = []
    cx, cy = 190, 110
    for i in range(160):
        t = i / 160
        th = math.pi * 0.95 + t * 2.4 * 2 * math.pi
        r = 70 - 26 * t + 6 * math.sin(t * 9)
        pts.append((cx + r * math.cos(th) * 1.05, cy + r * math.sin(th) * 0.8))
    lash = [(x0 + 80, y0 - 30)] + pts
    lash = chaikin(lash, False, 1)
    a.ink(lash, 11, color=INK, taper=True, wob=0.4, var=0.05)
    a.ink(lash, 6, color=rgb("#8e5b38"), taper=True, wob=0.4, var=0.05)
    a.ink(lash, 1.6, color=tint(rgb("#8e5b38"), 0.4), alpha=0.7, taper=True, wob=0.4)
    ex, ey = lash[-1]
    a.ink([(ex, ey), (ex + 18, ey + 10), (ex + 30, ey + 6)], 3.2, color=INK)


def blowgun(a):
    x, y, L, ang = 30, 90, 300, -0.1
    hx, hy = haft_end(x, y, ang, L)
    handle(a, x, y, hx, hy, 12, rgb("#c9b06a"))
    for t in (0.22, 0.5, 0.78):
        cx, cy = x + (hx - x) * t, y + (hy - y) * t
        a.ink(rot_pts([(cx, cy - 9), (cx, cy + 9)], cx, cy, ang), FINE * 1.6, color=shade(rgb("#c9b06a"), 0.5), wob=0)
    a.shape(rot_pts(rect(x - 6, y - 10, x + 22, y + 10), x, y, ang), WOOD_DARK, outline=FINE * 2, corner=5, depth=1.5, mottle=0)
    for k, (nx, ny, na) in enumerate(((150, 128, 0.2), (190, 140, -0.05))):
        needle(a, nx, ny, na)


def needle(a, x, y, ang, L=60):
    hx, hy = haft_end(x, y, ang, L)
    a.ink([(x + math.cos(ang) * 14, y + math.sin(ang) * 14), (hx, hy)], 3.6, color=INK, taper=False, wob=0)
    a.ink([(x + math.cos(ang) * 14, y + math.sin(ang) * 14), (hx, hy)], 1.6, color=SILVER, taper=False, wob=0)
    a.shape(rot_pts(chaikin([(x - 2, y), (x + 8, y - 7), (x + 18, y - 3), (x + 18, y + 3), (x + 8, y + 7)], True, 1), x, y, ang), rgb("#e8dcc0"), outline=FINE * 1.2, corner=0, depth=1, mottle=0)


# -- crossbows and firearms ----------------------------------------------------------------------


def hand_crossbow(a):
    x, y = 30, 110
    stock = chaikin([(x + 20, y - 9), (x + 150, y - 9), (x + 150, y + 9), (x + 52, y + 9), (x + 30, y + 46), (x + 6, y + 44), (x + 22, y + 9)], True, 1)
    limb = chaikin([(x + 128, y - 66), (x + 142, y - 30), (x + 146, y), (x + 142, y + 30), (x + 128, y + 66)], False, 3)
    a.ink([(x + 128, y - 66), (x + 76, y), (x + 128, y + 66)], FINE * 1.1, color=FEATHER, wob=0)
    a.shape(stock, WOOD_DARK, outline=O, corner=0, depth=3, light_k=0.4, mottle=0, var=V)
    a.ink(limb, 11, color=INK, taper=False, var=V)
    a.ink(limb, 6, color=IRON, taper=False, var=V)
    a.shape(rect(x + 64, y - 5, x + 90, y + 5), IRON, outline=FINE * 1.6, corner=2, depth=1, mottle=0)
    a.ink(chaikin([(x + 50, y + 9), (x + 60, y + 26), (x + 72, y + 9)], False, 2), 4, color=INK)


def heavy_crossbow(a):
    x, y = 40, 160
    a.shape(rect(x, y - 15, x + 270, y + 15), WOOD_DARK, outline=O, corner=7, depth=3, mottle=0, var=V, detail=lambda art, p: art.ink([(x + 30, y), (x + 230, y)], FINE * 1.2, color=shade(WOOD_DARK, 0.5), alpha=0.7))
    # Windlass at the butt: the crank's axle and two handles.
    a.shape(rect(x - 10, y - 40, x + 18, y + 40), IRON, outline=O, corner=6, depth=2, light_k=0.5, mottle=0, var=V)
    for s in (-1, 1):
        a.ink([(x + 4, y + s * 40), (x - 20, y + s * 58)], 9, color=INK, taper=False)
        a.ink([(x + 4, y + s * 40), (x - 20, y + s * 58)], 4.5, color=IRON, taper=False)
        dot(a, x - 20, y + s * 58, 7, WOOD)
    limb = chaikin([(x + 228, y - 130), (x + 256, y - 60), (x + 262, y), (x + 256, y + 60), (x + 228, y + 130)], False, 3)
    a.ink([(x + 228, y - 130), (x + 120, y), (x + 228, y + 130)], FINE * 1.3, color=FEATHER, wob=0)
    a.ink(limb, 18, color=INK, taper=False, var=V)
    a.ink(limb, 11, color=STEEL, taper=False, var=V)
    a.shape(rect(x + 110, y - 7, x + 150, y + 7), IRON, outline=O * 0.8, corner=2, depth=1, mottle=0, var=V)
    # The stirrup at the front, for the foot while spanning.
    stirrup = chaikin([(x + 266, y - 18), (x + 300, y - 22), (x + 306, y), (x + 300, y + 22), (x + 266, y + 18)], False, 2)
    a.ink(stirrup, 10, color=INK, taper=False)
    a.ink(stirrup, 5, color=IRON, taper=False)


def musket(a):
    x, y = 24, 70
    stock = chaikin([(x, y - 26), (x + 40, y - 20), (x + 110, y - 9), (x + 440, y - 9), (x + 440, y + 7), (x + 150, y + 9), (x + 118, y + 17), (x + 90, y + 15), (x + 40, y + 40), (x, y + 48)], True, 1)

    def grain(art, p):
        art.ink([(x + 10, y + 4), (x + 90, y + 2), (x + 200, y)], FINE, color=shade(WOOD, 0.45), alpha=0.6)

    a.shape(stock, WOOD, outline=O, corner=0, depth=3, light_k=0.4, mottle=0.04, var=V, detail=grain)
    a.shape(rect(x + 2, y - 26, x + 14, y + 48), shade(WOOD_DARK, 0.2), outline=FINE * 1.8, corner=3, depth=1, mottle=0)  # butt plate
    a.shape(rect(x + 120, y - 17, x + 520, y - 3), STEEL, outline=O * 0.85, corner=3, depth=2, light_k=0.55, mottle=0, var=V)  # barrel
    a.ink([(x + 160, y + 3), (x + 480, y + 3)], 6, color=INK, taper=False)  # ramrod
    a.ink([(x + 160, y + 3), (x + 480, y + 3)], 2.5, color=WOOD_LIGHT, taper=False)
    for bx in (x + 260, x + 380):
        a.shape(rect(bx - 4, y - 15, bx + 4, y + 6), BRASS, outline=FINE * 1.5, corner=2, depth=1, mottle=0)
    lock_(a, x + 120, y + 2)
    a.ink(chaikin([(x + 100, y + 14), (x + 104, y + 32), (x + 124, y + 28), (x + 128, y + 12)], False, 2), 5, color=INK)


def lock_(a, cx, cy):
    """The flintlock: a lock plate with the cock and the frizzen."""
    a.shape(rect(cx - 30, cy - 8, cx + 14, cy + 6), STEEL, outline=FINE * 1.8, corner=3, depth=1, light_k=0.5, mottle=0)
    cock = chaikin([(cx - 22, cy - 2), (cx - 30, cy - 18), (cx - 18, cy - 24), (cx - 12, cy - 16), (cx - 14, cy - 4)], True, 1)
    a.shape(cock, IRON, outline=FINE * 1.8, corner=0, depth=1, light_k=0.5, mottle=0)
    a.shape(rect(cx - 2, cy - 22, cx + 6, cy - 6), IRON, outline=FINE * 1.6, corner=2, depth=1, mottle=0)


def pistol(a):
    x, y = 30, 60
    grip = chaikin([(x + 70, y - 10), (x + 62, y + 4), (x + 30, y + 40), (x + 6, y + 70), (x - 6, y + 62), (x + 6, y + 40), (x + 30, y + 6), (x + 40, y - 10)], True, 2)
    a.shape(grip, WOOD, outline=O, corner=0, depth=3, light_k=0.4, mottle=0.04, var=V)
    a.shape(ellipse(x, y + 66, 12, 10, 20), BRASS, outline=FINE * 1.8, depth=1.5, light_k=0.5, mottle=0)  # pommel cap
    a.shape(rect(x + 36, y - 12, x + 200, y + 4), WOOD, outline=O, corner=4, depth=2, light_k=0.4, mottle=0, var=V)
    a.shape(rect(x + 70, y - 12, x + 230, y - 2), STEEL, outline=O * 0.85, corner=3, depth=2, light_k=0.55, mottle=0, var=V)
    lock_(a, x + 82, y + 2)
    a.ink(chaikin([(x + 50, y + 4), (x + 56, y + 22), (x + 76, y + 18), (x + 78, y + 4)], False, 2), 4.5, color=INK)


# -- ammunition --------------------------------------------------------------------------------------


def crossbow_bolts(a):
    for x, y, t in ((30, 60, -0.1), (40, 100, 0.05), (36, 140, -0.04), (60, 176, 0.12)):
        bolt_at(a, x, y, t, 130)


def bolt_case(a):
    x0, y0, x1, y1 = 30, 40, 280, 100
    body = rect(x0, y0, x1, y1)

    def bands(art, p):
        for bx in (x0 + 60, x1 - 60):
            art.shape(rect(bx - 9, y0 - 2, bx + 9, y1 + 2), shade(LEATHER, 0.25), outline=FINE * 1.6, corner=2, depth=1, mottle=0)
        art.ink([(x0 + 10, (y0 + y1) / 2 - 8), (x1 - 40, (y0 + y1) / 2 - 8)], FINE, color=tint(WOOD, 0.3), alpha=0.6)

    a.shape(body, WOOD, outline=O, corner=26, depth=6, light_k=0.4, detail=bands)
    a.shape(rect(x1 - 30, y0 - 5, x1 + 6, y1 + 5), LEATHER, outline=O, corner=14, depth=4, light_k=0.35, mottle=0)  # cap
    strap = chaikin([(x0 + 60, y1), (x0 + 120, y1 + 40), (x1 - 120, y1 + 40), (x1 - 60, y1)], False, 3)
    a.ink(strap, 11, color=INK, taper=False)
    a.ink(strap, 6, color=LEATHER, taper=False)
    bolt_at(a, x0 - 6, y0 - 22, -0.02, 120)


def lead_ball(a, x, y, r=8, color=LEAD):
    a.shape(ellipse(x, y, r, r, 18), color, outline=FINE * 1.5, depth=1.5, light_k=0.6, ao=0, mottle=0)


def firearm_bullets(a):
    # A small open pouch with lead balls, a few rolled out.
    cx, cy = 110, 100
    pouch = chaikin([(cx - 60, cy - 30), (cx - 30, cy - 52), (cx + 34, cy - 50), (cx + 62, cy - 20), (cx + 52, cy + 40), (cx, cy + 56), (cx - 54, cy + 36)], True, 2)
    a.shape(pouch, LEATHER, outline=O, corner=0, depth=6, light_k=0.35, mottle=0.04)
    a.shape(ellipse(cx, cy - 4, 40, 32, 36), shade(LEATHER, 0.45), outline=DETAIL, depth=4, shade_k=0, light_k=0, ao=0.5, mottle=0)
    for k in range(9):
        lead_ball(a, cx - 24 + (k % 3) * 22 + a.rng.uniform(-4, 4), cy - 22 + (k // 3) * 18 + a.rng.uniform(-3, 3), 8.5)
    a.ink(chaikin([(cx - 50, cy - 36), (cx - 90, cy - 70), (cx - 110, cy - 50)], False, 2), 5, color=INK)
    for bx, by in ((190, 150), (212, 132), (176, 176)):
        lead_ball(a, bx, by, 8.5)


def sling_bullets(a):
    for k in range(9):
        x, y = 30 + (k % 3) * 46 + a.rng.uniform(-10, 10), 30 + (k // 3) * 40 + a.rng.uniform(-8, 8)
        if k % 3 == 1:
            a.shape(ellipse(x, y, 12, 10, 18), STONE_GREY, outline=FINE * 1.6, depth=2, light_k=0.45, ao=0, mottle=0.04)
        else:
            # Cast lead glandes: almond-shaped.
            a.shape(ellipse(x, y, 13, 7.5, 22, rot=a.rng.uniform(0, 3.14)), LEAD, outline=FINE * 1.6, depth=1.5, light_k=0.6, ao=0, mottle=0)


def blowgun_needles(a):
    # A small leather fold with needles tucked into it, two loose.
    a.shape(rect(20, 30, 170, 110), LEATHER, outline=O, corner=10, depth=5, light_k=0.35, mottle=0.04)
    a.ink([(95, 34), (95, 106)], DETAIL, color=shade(LEATHER, 0.5), alpha=0.8, taper=False)
    for k in range(5):
        needle(a, 32 + k * 12, 100 - k * 3, -1.45, 64)
    needle(a, 110, 140, -0.15)
    needle(a, 130, 168, 0.1)


# -- magic weapon details -----------------------------------------------------------------------------


def flames_before(art, loc, bpts):
    """Uneven tongues of fire licking off both edges, bigger toward the tip."""
    half = len(bpts) // 2
    for side, pts, base in ((-1, bpts[:half], -math.pi / 2), (1, bpts[half + 1 :][::-1], math.pi / 2)):
        i = 2
        while i < len(pts) - 2:
            t = i / len(pts)
            px, py = pts[i]
            flame(art, px, py, base - 0.55 + art.rng.uniform(-0.35, 0.35), art.rng.uniform(6, 10) + 9 * t)
            i += art.rng.randint(3, 6)


def frost_before(art, loc, bpts):
    for k, (px, py) in enumerate(bpts[4:-4:7]):
        snowflake(art, px + art.rng.uniform(-8, 8), py + (-14 if k % 2 else 14), art.rng.uniform(5, 8))


def rune_detail(color, n=6, t0=0.1, t1=0.7, size=4.5, offset=0.0):
    def d(art, loc, c):
        pts = [c(t0 + (t1 - t0) * k / max(1, n - 1)) for k in range(n)]
        runes(art, loc([(px, py + offset) for px, py in pts]), color, size)

    return d


def veins_detail(art, loc, c):
    for k in range(5):
        t = 0.08 + k * 0.15
        x, y = c(t)
        art.ink(loc([(x, y), (x + 14, y - 5), (x + 26, y + 3), (x + 40, y - 2)]), FINE * 1.4, color=rgb("#d0364a"), alpha=0.9)


def drips_detail(color):
    def d(art, loc, c):
        for t in (0.25, 0.5, 0.7):
            x, y = c(t)
            px, py = loc([(x, y + 3)])[0]
            drip(art, px, py, 3.5, color)

    return d


def dagger_of_venom(a):
    loc, c = sword(a, 40, 70, -0.25, L=130, w=15, grip=30, span=22, blade=rgb("#a7b2a0"), glow_c=VENOM, glow_a=0.35, detail=drips_detail(VENOM))
    px, py = loc([c(0.95)])[0]
    drip(a, px + 10, py + 22, 5, VENOM)


def vorpal_detail(art, loc, c):
    art.ink(loc([c(t) for t in [k / 24 * 0.95 for k in range(25)]]), FINE * 1.6, color=tint(ARCANE, 0.4), alpha=0.9, wob=0)


def sharp_detail(art, loc, c):
    edge = [c(t) for t in [k / 20 * 0.86 for k in range(21)]]
    art.ink(loc([(x, y + 6) for x, y in edge]), FINE * 1.5, color=(255, 255, 255), alpha=0.95, wob=0)


def dancing_after(a, loc, c):
    for k, (r, a0) in enumerate(((70, -0.3), (88, -0.15), (106, 0.0))):
        x, y = c(0.9)
        arc = [(x - 40 + r * math.cos(t) * 0.4, y + r * math.sin(t) * 0.55) for t in [a0 + 0.5 + j * 0.12 for j in range(10)]]
        a.ink(loc(arc), DETAIL * 1.3, color=rgb("#3f7ec0"), alpha=0.95 - k * 0.2)


def speed_lines(a, loc, c, color):
    for k, (t, d) in enumerate(((0.3, -24), (0.55, -30), (0.8, -22), (0.45, 34), (0.7, 38))):
        x, y = c(t)
        a.ink(loc([(x - 60, y + d), (x - 10, y + d)]), DETAIL * 0.9, color=color, alpha=0.8)


def holy_detail(art, loc, c):
    x, y = c(0.22)
    art.ink(loc([(x - 10, y), (x + 10, y)]), FINE * 1.8, color=GOLD, wob=0, taper=False)
    art.ink(loc([(x, y - 6), (x, y + 6)]), FINE * 1.8, color=GOLD, wob=0, taper=False)


def nine_detail(art, loc, c):
    for k in range(9):
        x, y = c(0.06 + k * 0.085)
        px, py = loc([(x, y)])[0]
        dot(art, px, py, 2.6, rgb("#b8f0a8"))
        dot(art, px, py, 1.3, (255, 255, 255))


def clover(a, x, y, r=5):
    for k in range(4):
        t = k * math.pi / 2 + math.pi / 4
        a.shape(ellipse(x + r * 0.7 * math.cos(t), y + r * 0.7 * math.sin(t), r * 0.62, r * 0.62, 14), rgb("#4fae58"), outline=FINE * 1.1, depth=1, light_k=0.5, ao=0, mottle=0)


def luck_blade(a):
    loc, c = sword(a, 40, 70, -0.15, L=240, w=16, guard=GOLD, pommel=GOLD, glow_c=rgb("#bfe68a"), glow_a=0.35, guard_kind="cross")
    clover(a, *loc([(40, 70)])[0], 7)


def scimitar_speed(a):
    loc, c = sword(a, 40, 110, -0.05, L=250, w=20, grip=40, span=24, kind="curved", curve=-0.22, guard=GOLD, wrap=rgb("#3c6a8a"), glow_c=rgb("#8ee6e0"), glow_a=0.35)
    speed_lines(a, loc, c, rgb("#4aa6b0"))


def dancing_sword(a):
    loc, c = sword(a, 40, 110, -0.15, L=240, w=16, glow_c=rgb("#a8d4ff"), glow_a=0.35, guard_kind="cross", guard=SILVER, pommel=SILVER, guard_gem=rgb("#4f8fd0"))
    dancing_after(a, loc, c)


def sharpness(a):
    loc, c = sword(a, 40, 70, -0.15, L=250, w=17, blade=tint(STEEL, 0.25), detail=sharp_detail, guard=SILVER, pommel=SILVER)
    sparkle(a, *loc([c(0.985)])[0], 12)


def sun_blade(a):
    # A hilt with a blade of pure sunlight.
    sword(a, 40, 70, -0.15, L=240, w=18, blade=rgb("#fff3b0"), glow_c=rgb("#ffd86a"), glow_a=0.7, fuller=False, outline_color=rgb("#c88a1a"), guard=GOLD, pommel=GOLD, guard_kind="cross", guard_gem=rgb("#f0a030"))


def generic_magic(a):
    sword(a, 40, 70, -0.15, L=230, w=16, glow_c=rgb("#9cc8ff"), glow_a=0.3, detail=rune_detail(rgb("#3f78c8"), 3, 0.2, 0.5, 4.5))


# -- magic hafted ----------------------------------------------------------------------------------


def berserker_axe(a):
    loc = greataxe_at(a, 30, 140, -0.22, 280, blade=rgb("#8a8a92"), haft=rgb("#5a3a28"), glow_c=rgb("#e0483a"))
    hx, hy = haft_end(30, 140, -0.22, 280)
    runes(a, loc([(hx - 22, hy - 50), (hx - 6, hy - 58), (hx + 10, hy - 58), (hx + 26, hy - 50)]), rgb("#c0282a"), 5)


def dwarven_thrower(a):
    hammer_head_at(a, 30, 120, -0.25, 200, head=rgb("#6e7480"), glow_c=rgb("#8cc0ff"), bands=GOLD)
    hx, hy = haft_end(30, 120, -0.25, 200)
    runes(a, rot_pts([(hx - 10, hy - 22), (hx + 8, hy - 22), (hx - 1, hy - 4)], hx, hy, -0.25), GOLD, 5)


def hammer_of_thunderbolts(a):
    maul_at(a, 30, 160, -0.22, 260, head=rgb("#6c7280"), glow_c=rgb("#9cc8ff"))
    hx, hy = haft_end(30, 160, -0.22, 260)
    rng = a.rng
    bolt_zigzag(a, (hx - 30, hy - 60), (hx + 50, hy + 60), rng, 6, 12)
    bolt_zigzag(a, (hx - 140, hy + 10), (hx - 60, hy + 40), rng, 5, 8)
    runes(a, rot_pts([(hx - 12, hy - 8), (hx + 6, hy - 8), (hx - 3, hy + 14)], hx, hy, -0.22), GOLD, 5)


def mace_disruption(a):
    mace2_at(a, 30, 130, -0.3, 170, head=rgb("#d8dce4"), glow_c=rgb("#fff0a8"), glow_a=0.8)
    hx, hy = haft_end(30, 130, -0.3, 170)
    for k in range(8):
        t = k * math.pi / 4
        a.ink([(hx + 46 * math.cos(t), hy + 46 * math.sin(t)), (hx + 64 * math.cos(t), hy + 64 * math.sin(t))], FINE * 1.6, color=rgb("#d8a830"), alpha=0.9)


def mace_smiting(a):
    mace2_at(a, 30, 130, -0.3, 170, head=SILVER, haft=WOOD_DARK, glow_c=rgb("#ffd86a"), glow_a=0.45)
    hx, hy = haft_end(30, 130, -0.3, 170)
    gem(a, hx, hy, 6, rgb("#f0a030"))


def mace_terror(a):
    mace2_at(a, 30, 130, -0.3, 170, head=BLACK_IRON, haft=rgb("#3a2a24"), glow_c=rgb("#8a4ad0"), glow_a=0.6)
    hx, hy = haft_end(30, 130, -0.3, 170)
    # A tiny skull boss on the head.
    a.shape(ellipse(hx, hy, 8, 9, 18), rgb("#e6dcc4"), outline=FINE * 1.4, depth=1, mottle=0)
    for s in (-1, 1):
        dot(a, hx + s * 3, hy - 1, 2, INK)


def javelin_lightning(a):
    hx, hy = javelin_at(a, 30, 90, -0.12, 250, head=rgb("#cfd8e6"))
    glow(a, hx + 20, hy - 2, 40, rgb("#9cc8ff"), 0.6)
    bolt_zigzag(a, (90, 112), (hx + 10, hy - 22), a.rng, 9, 10)


def trident_fish(a):
    trident_at(a, 30, 110, -0.08, 280, metal=rgb("#c9a65a"), haft=rgb("#3f7a74"), glow_c=SEA)
    for k, (fx, fy) in enumerate(((140, 70), (190, 150))):
        # Little fish shapes swimming round the haft.
        a.shape([(fx - 14, fy), (fx, fy - 7), (fx + 12, fy), (fx, fy + 7)], rgb("#6fc2d8"), outline=FINE * 1.3, corner=3, depth=1, mottle=0)
        a.shape([(fx - 14, fy), (fx - 22, fy - 7), (fx - 22, fy + 7)], rgb("#6fc2d8"), outline=FINE * 1.3, corner=1, depth=1, mottle=0)


def oathbow(a):
    x, y = 40, 200
    glow(a, x + 40, y, 120, rgb("#a8e6a0"), 0.35)
    loc, limb = longbow_at(a, x, y, 0.0, 360, wood=rgb("#efe6d2"), string=rgb("#b8e8c0"), grip=rgb("#4a7a52"))
    for t in (0.18, 0.82):
        px, py = loc([limb[int(t * (len(limb) - 1))]])[0]
        runes(a, [(px + 4, py)], rgb("#3a9a58"), 5)
    for s in (-1, 1):
        dot(a, x, y + s * 180, 6, SILVER)


def arrow_slaying(a):
    arrow2_at(a, 30, 70, -0.12, 190, shaft=rgb("#3a3036"), head=rgb("#5a1a22"), vanes=rgb("#2e2a30"), head_glow=rgb("#e04040"))


def magic_arrows(a):
    for x, y, t in ((30, 50, -0.08), (36, 90, 0.04), (44, 130, -0.02)):
        arrow2_at(a, x, y, t, 170, head=rgb("#b8d8ff"), head_glow=rgb("#9cc8ff"))


# -- table ---------------------------------------------------------------------------------------------


def tool_item(fn, w, h, seed, x, y, ang, **kw):
    return item(lambda a: fn(a, x, y, ang, **kw), w, h, seed)


def draw_item(fn, w, h, seed):
    return item(fn, w, h, seed)


SRD_WEAPONS = {
    # Simple melee
    "Club": tool_item(club_at, 300, 160, 2001, 30, 90, -0.2),
    "Greatclub": tool_item(lambda a, x, y, t: club_at(a, x, y, t, 300, 40, studs=8), 400, 220, 2002, 30, 130, -0.2),
    "Handaxe": tool_item(lambda a, x, y, t: axe_at(a, x, y, t, 115), 260, 220, 2003, 30, 160, -0.3),
    "Javelin": tool_item(lambda a, x, y, t: javelin_at(a, x, y, t, 260), 360, 140, 2004, 30, 90, -0.12),
    "Light Hammer": tool_item(lambda a, x, y, t: hammer_at(a, x, y, t, 100), 220, 200, 2005, 30, 140, -0.35),
    "Quarterstaff": tool_item(quarterstaff_at, 500, 160, 2006, 30, 110, -0.1),
    "Sickle": tool_item(sickle_at, 260, 240, 2007, 30, 170, -0.2),
    "Dart": draw_item(lambda a: [dart_at(a, x, y, t) for x, y, t in ((20, 40, -0.1), (30, 80, 0.05), (24, 120, -0.02))], 200, 160, 2008),
    "Sling": draw_item(sling, 310, 190, 2009),
    # Martial melee
    "Flail": draw_item(lambda a: flail(a), 320, 260, 2010),
    "Glaive": tool_item(lambda a, x, y, t: glaive_at(a, x, y, t), 520, 180, 2011, 30, 120, -0.1),
    "Greataxe": tool_item(greataxe_at, 400, 260, 2012, 30, 200, -0.22),
    "Greatsword": sword_item(2013, L=380, w=22, grip=78, span=42),
    "Lance": draw_item(lambda a: lance(a), 560, 140, 2014),
    "Maul": tool_item(maul_at, 380, 260, 2015, 30, 200, -0.22),
    "Morningstar": draw_item(lambda a: morningstar(a), 300, 240, 2016),
    "Pike": tool_item(lambda a, x, y, t: pike_at(a, x, y, t), 600, 140, 2017, 30, 90, -0.06),
    "Rapier": sword_item(2018, L=300, w=13, blade_outline_w=O * 0.6, grip=44, span=24, kind="thin", guard=SILVER, pommel=SILVER, guard_kind="ring"),
    "Scimitar": sword_item(2019, L=250, w=20, grip=40, span=24, kind="curved", curve=-0.22, ang=-0.05),
    "Shortsword": sword_item(2020, L=180, w=17, grip=38, span=24, kind="leaf"),
    "Trident": tool_item(trident_at, 420, 160, 2021, 30, 100, -0.08),
    "War Pick": tool_item(pick_at, 280, 240, 2022, 30, 180, -0.3),
    "Whip": draw_item(whip, 320, 220, 2023),
    # Ranged
    "Blowgun": draw_item(blowgun, 360, 190, 2024),
    "Hand Crossbow": draw_item(hand_crossbow, 220, 220, 2025),
    "Heavy Crossbow": draw_item(heavy_crossbow, 380, 330, 2026),
    "Longbow": tool_item(lambda a, x, y, t: longbow_at(a, x, y, t), 140, 420, 2027, 40, 210, 0.0),
    "Musket": draw_item(musket, 580, 140, 2028),
    "Pistol": draw_item(pistol, 300, 160, 2029),
    # Ammunition
    "Crossbow Bolts": draw_item(crossbow_bolts, 220, 220, 2030),
    "Bolt Case": draw_item(bolt_case, 320, 170, 2031),
    "Firearm Bullets": draw_item(firearm_bullets, 240, 200, 2032),
    "Sling Bullets": draw_item(sling_bullets, 170, 140, 2033),
    "Blowgun Needles": draw_item(blowgun_needles, 200, 200, 2034),
    # Magic weapons
    "Flame Tongue": sword_item(2101, L=240, blade=rgb("#b8a8a0"), glow_c=rgb("#ffa04a"), glow_a=0.45, before=flames_before),
    "Frost Brand": sword_item(2102, L=240, blade=ICE, glow_c=FROST, glow_a=0.5, before=frost_before, guard=SILVER, pommel=SILVER, guard_gem=rgb("#6ab0e0")),
    "Sun Blade": draw_item(sun_blade, 340, 160, 2103),
    "Vorpal Sword": sword_item(2104, L=250, w=17, blade=tint(STEEL, 0.15), glow_c=ARCANE, glow_a=0.3, detail=vorpal_detail, guard_kind="cross", guard=SILVER, pommel=SILVER, guard_gem=ARCANE),
    "Holy Avenger": sword_item(2105, L=270, w=18, glow_c=HOLY, glow_a=0.55, detail=holy_detail, guard_kind="cross", guard=GOLD, pommel=GOLD, pommel_gem=rgb("#4f8fd0"), guard_gem=rgb("#4f8fd0")),
    "Dancing Sword": draw_item(dancing_sword, 380, 240, 2106),
    "Sword of Life Stealing": sword_item(2107, L=240, blade=DARK_STEEL, glow_c=rgb("#d0364a"), glow_a=0.4, detail=veins_detail, guard=BLACK_IRON, pommel=BLACK_IRON, wrap=rgb("#5a2026"), guard_gem=rgb("#c0283a")),
    "Sword of Sharpness": draw_item(sharpness, 360, 160, 2108),
    "Sword of Wounding": sword_item(2109, L=240, blade=rgb("#8e949e"), serrate=True, detail=drips_detail(BLOOD), guard=IRON, pommel=IRON),
    "Nine Lives Stealer": sword_item(2110, L=240, blade=DARK_STEEL, glow_c=rgb("#9ae08a"), glow_a=0.3, detail=nine_detail, guard=BLACK_IRON, pommel=BLACK_IRON),
    "Luck Blade": draw_item(luck_blade, 360, 160, 2111),
    "Dragon Slayer": sword_item(2112, L=260, w=18, glow_c=rgb("#ff8a5a"), glow_a=0.3, detail=rune_detail(rgb("#b02a20"), 5), guard_kind="wings", guard=rgb("#a8402a"), pommel=rgb("#a8402a"), span=32, guard_gem=rgb("#e0a030")),
    "Giant Slayer": sword_item(2113, L=380, w=24, grip=78, span=44, glow_c=rgb("#e0b070"), glow_a=0.3, detail=rune_detail(rgb("#7a4a1a"), 6, 0.1, 0.7, 6), guard=IRON, pommel=IRON),
    "Defender": sword_item(2114, L=250, w=17, glow_c=rgb("#8cb8ff"), glow_a=0.35, guard_kind="shield", span=30, guard=rgb("#3f6aa8"), pommel=SILVER, guard_gem=SILVER),
    "Scimitar of Speed": draw_item(scimitar_speed, 360, 200, 2115),
    "Dagger of Venom": draw_item(dagger_of_venom, 220, 160, 2116),
    "Berserker Axe": draw_item(berserker_axe, 400, 280, 2117),
    "Dwarven Thrower": draw_item(dwarven_thrower, 300, 240, 2118),
    "Hammer of Thunderbolts": draw_item(hammer_of_thunderbolts, 400, 300, 2119),
    "Mace of Disruption": draw_item(mace_disruption, 300, 260, 2120),
    "Mace of Smiting": draw_item(mace_smiting, 300, 260, 2121),
    "Mace of Terror": draw_item(mace_terror, 300, 260, 2122),
    "Javelin of Lightning": draw_item(javelin_lightning, 380, 160, 2123),
    "Trident of Fish Command": draw_item(trident_fish, 400, 200, 2124),
    "Oathbow": draw_item(oathbow, 220, 440, 2125),
    "Arrow of Slaying": draw_item(arrow_slaying, 260, 120, 2126),
    "Weapon +1 (Longsword)": draw_item(generic_magic, 340, 160, 2127),
    "Ammunition +1 (Arrows)": draw_item(magic_arrows, 260, 190, 2128),
}


# -- the remaining martial pieces (defined after the table's lambdas need them) -------------------


def flail(a):
    x, y, ang, L = 30, 200, -0.45, 140
    hx, hy = haft_end(x, y, ang, L)
    handle(a, x, y, hx, hy, 12, WOOD)
    a.shape(rot_pts(rect(hx - 6, hy - 10, hx + 8, hy + 10), hx, hy, ang), IRON, outline=FINE * 2, corner=3, depth=1, mottle=0)
    bx, by = hx + 90, hy + 10
    # The chain sags from the haft's cap to the ball.
    links = [(hx + (bx - hx) * t, hy + (by - hy) * t + 24 * math.sin(math.pi * t)) for t in [k / 7 for k in range(1, 7)]]
    for k, (lx, ly) in enumerate(links):
        ang_l = math.atan2(by - hy, bx - hx)
        e = ellipse(lx, ly, 8, 4.5, 16, rot=ang_l + (0 if k % 2 else 1.4))
        a.ink(e, 6, closed=True, color=INK, wob=0, var=0)
        a.ink(e, 2.6, closed=True, color=STEEL, wob=0, var=0)
    spiked_ball(a, bx + 14, by, 22, IRON, 10)


def morningstar(a):
    x, y, ang, L = 30, 190, -0.4, 170
    hx, hy = haft_end(x, y, ang, L)
    handle(a, x, y, hx, hy, 12, WOOD)
    a.shape(rot_pts(rect(x + 6, y - 9, x + 50, y + 9), x, y, ang), LEATHER, outline=FINE * 2, corner=3, depth=1, mottle=0)
    spiked_ball(a, hx + 8, hy - 4, 24, IRON, 12, spike=1.3)


def glaive_at(a, x, y, ang, L=330):
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    handle(a, x, y, hx + math.cos(ang) * 6, hy + math.sin(ang) * 6, 11)
    edge = [(hx + 120 * t, hy - 10 - 24 * math.sin(math.pi * min(1, t * 0.85))) for t in [k / 12 for k in range(13)]]
    blade = [(hx - 4, hy + 9)] + edge + [(hx + 132, hy + 2), (hx + 70, hy + 9), (hx + 44, hy + 9), (hx + 36, hy + 26), (hx + 28, hy + 9)]
    blade_shape(a, loc(blade))
    a.ink(loc([(hx + 8, hy - 14), (hx + 60, hy - 30), (hx + 108, hy - 22)]), FINE * 1.4, color=tint(STEEL, 0.6), alpha=0.9)
    a.shape(loc(rect(hx - 20, hy - 10, hx + 4, hy + 10)), IRON, outline=O, corner=3, depth=2, mottle=0, var=V)


def pike_at(a, x, y, ang, L=520):
    hx, hy = haft_end(x, y, ang, L)
    loc = lambda pts: rot_pts(pts, hx, hy, ang)  # noqa: E731
    handle(a, x, y, hx, hy, 10, WOOD)
    a.ink(loc([(hx - 50, hy), (hx, hy)]), 14, color=INK, taper=False, wob=0)
    a.ink(loc([(hx - 50, hy), (hx, hy)]), 6, color=IRON, taper=False, wob=0)  # the langets
    blade_shape(a, loc([(hx - 4, hy - 8), (hx + 8, hy - 9), (hx + 40, hy), (hx + 8, hy + 9), (hx - 4, hy + 8)]))


def lance(a):
    x, y, L = 30, 70, 520
    # A painted (red = colorable) lance tapering to a blunt point, with a
    # funnel vamplate shielding the hand and a little pennon near the tip.
    shaft = chaikin([(x + 70, y - 16), (x + L - 30, y - 4), (x + L, y), (x + L - 30, y + 4), (x + 70, y + 16)], True, 1)

    def stripes(art, p):
        for k in range(9):
            sx = x + 100 + k * 48
            art.shape([(sx, y - 20), (sx + 22, y - 20), (sx + 6, y + 20), (sx - 16, y + 20)], (236, 226, 200), outline=0, corner=0, wob=0.2, shade_k=0, light_k=0, ao=0, mottle=0)

    a.shape(shaft, RED, outline=O, corner=0, depth=3, light_k=0.4, mottle=0, var=V, detail=stripes)
    a.shape(rect(x, y - 8, x + 70, y + 8), LEATHER, outline=O * 0.8, corner=4, depth=1, mottle=0, var=V)
    vamp = [(x + 58, y - 38), (x + 70, y - 38), (x + 110, y - 15), (x + 110, y + 15), (x + 70, y + 38), (x + 58, y + 38)]
    a.shape(vamp, STEEL, outline=O, corner=4, depth=3, light_k=0.55, mottle=0, var=V)
    pen = [(x + L - 120, y - 5), (x + L - 70, y - 40), (x + L - 96, y - 30), (x + L - 104, y - 44), (x + L - 140, y - 6)]
    a.shape(pen, RED, outline=FINE * 1.8, corner=1, depth=2, light_k=0.4, mottle=0)


SRD_WEAPONS_COLORABLE = {"Lance"}
