"""More portals for the built-in pack (doors, windows, arches, gates and
doorways), seen from above for placing in walls. Same conventions as
tex_build.PORTALS: ~256 px wide (single) or ~512 (double), the wall line runs
along the middle (y = h / 2), frame posts at both ends."""

import math

import skia

from floors import split
from pen import DETAIL, FINE, INK, JOINT, JOINT_ALPHA, Art, grout, joint_color, chaikin, ellipse, mix, rect, rgb, shade, tint, vary
from tex_build import BRASS, DOOR, FRAME, IRON, SW, T, dot, jambs, leaf, swing

STONE = rgb("#a39d93")
DARK_STONE = rgb("#7f7a72")
BRICK = rgb("#a8604a")
GLASS = rgb("#a9cfdc")
BRONZE = rgb("#b07a3e")
GOLD = rgb("#d6ae4c")
STEEL = rgb("#8f949c")
HOLE = rgb("#1e1a18")

WOODS = {
    "Oak": rgb("#9a6c43"),
    "Walnut": rgb("#6e4a2f"),
    "Pine": rgb("#c39463"),
    "Ebony": rgb("#3e2c22"),
    "Cherry": rgb("#8f4e34"),
    "Ash": rgb("#b8a382"),
    "Weathered": rgb("#8a8274"),
}
PAINTS = {
    "Red": rgb("#a8483a"),
    "Blue": rgb("#4f6f98"),
    "Green": rgb("#5f8a52"),
    "Black": rgb("#36322f"),
    "White": rgb("#e4ddd0"),
    "Yellow": rgb("#d1a743"),
}


def frame_posts(a, w, h, color=FRAME, depth=18):
    jambs(a, w, h, color, depth)


def handles(a, x, h, thick, color=BRASS, ring=False):
    for s in (-1, 1):
        if ring:
            a.ink(ellipse(x, h / 2 + s * (thick / 2 + 7), 6, 5, 16), FINE * 1.6, closed=True, color=color)
        else:
            a.shape(ellipse(x, h / 2 + s * (thick / 2 + 5), 5, 4, 16), color, outline=FINE * 1.3, depth=1, mottle=0)


def slab(a, x0, x1, h, color, style="plank", thick=16, studs=False, trim=None):
    """A closed door leaf (or a part of one) in one of several styles."""
    y0, y1 = h / 2 - thick / 2, h / 2 + thick / 2

    def detail(art, p):
        if style == "plank":
            n = max(2, int((x1 - x0) / 26))
            for k in range(1, n):
                x = x0 + (x1 - x0) * k / n
                art.ink([(x, y0 + 1), (x, y1 - 1)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False)
        elif style == "panel":
            n = max(2, int((x1 - x0) / 54))
            for k in range(n):
                xa = x0 + 6 + (x1 - x0 - 12) * k / n
                xb = x0 + 6 + (x1 - x0 - 12) * (k + 1) / n - 6
                art.ink(rect(xa, y0 + 4, xb, y1 - 4), FINE * 1.1, closed=True, color=shade(color, 0.45), alpha=0.85, wob=0.2)
        elif style == "chevron":
            for x in range(int(x0) + 10, int(x1) - 4, 16):
                art.ink([(x, y0 + 2), (x + 7, h / 2), (x, y1 - 2)], FINE * 1.1, color=shade(color, 0.45), alpha=0.85, taper=False)
        elif style == "carved":
            art.ink([(x0 + 10, h / 2), (x1 - 10, h / 2)], FINE * 1.2, color=shade(color, 0.45), alpha=0.8)
            for x in range(int(x0) + 24, int(x1) - 16, 30):
                art.ink(ellipse(x, h / 2, 6, 3.5, 16), FINE, closed=True, color=shade(color, 0.45), alpha=0.85)
        elif style == "stone":
            for x in range(int(x0) + 22, int(x1) - 10, 28):
                art.ink([(x, y0 + 1), (x + 3, y1 - 1)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA)
        elif style == "rivets":
            for x in range(int(x0) + 10, int(x1) - 6, 14):
                for y in (y0 + 4, y1 - 4):
                    dot(art, x, y, 1.8, tint(color, 0.4))

    a.shape(rect(x0, y0, x1, y1), color, outline=DETAIL * 1.4, corner=3, depth=3, light_k=0.4, detail=detail)
    if trim is not None:
        for x in (x0 + 9, x1 - 9):
            a.shape(rect(x - 4, y0 - 2, x + 4, y1 + 2), trim, outline=FINE * 1.2, corner=1, depth=1, mottle=0)
    if studs:
        for x in range(int(x0) + 16, int(x1) - 8, 18):
            dot(a, x, h / 2, 2.4, tint(IRON, 0.4))


# -- closed doors -------------------------------------------------------------------------------


def door(seed, color, style="plank", frame=FRAME, w=T, h=80, thick=16, trim=IRON, studs=False, knob=BRASS, ring=False):
    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h, frame)
        slab(a, 20, w - 20, h, color, style, thick, studs, trim)
        handles(a, w - 40, h, thick, knob, ring)
        return a.image()

    return make


def double(seed, color, style="plank", frame=FRAME, h=86, thick=18, trim=IRON, studs=False, knob=BRASS, ring=False):
    w = SW

    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h, frame, depth=22)
        slab(a, 24, w / 2 - 1, h, color, style, thick, studs, trim)
        slab(a, w / 2 + 1, w - 24, h, color, style, thick, studs, trim)
        handles(a, w / 2 - 22, h, thick, knob, ring)
        handles(a, w / 2 + 22, h, thick, knob, ring)
        return a.image()

    return make


# -- open / ajar doors --------------------------------------------------------------------------


def swung(seed, color, angle=1.3, double_=False, frame=FRAME, knob=BRASS):
    """A door (or a pair) standing open at `angle` from the wall, with the
    dotted arc it sweeps."""
    w = SW if double_ else T
    span = (w - 40) / (2 if double_ else 1)
    h = int(30 + span * math.sin(angle) + 22)

    def make():
        a = Art(w, h, seed)
        a.shape(rect(4, 24, w - 4, 36), shade(frame, 0.25), outline=DETAIL, corner=2, depth=2, mottle=0)
        for x0 in (2, w - 20):
            a.shape(rect(x0, 10, x0 + 18, 50), frame, outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.35)
        hinges = [(20, -1)] + ([(w - 20, 1)] if double_ else [])
        for hx, side in hinges:
            ang = angle if side < 0 else math.pi - angle
            if side < 0:
                swing(a, hx, 30, span, 0.08, ang - 0.05)
            else:
                swing(a, hx, 30, span, ang + 0.05, math.pi - 0.08)
            ux, uy = math.cos(ang), math.sin(ang)
            x1, y1 = hx + span * ux, 30 + span * uy
            px, py = -uy * 8, ux * 8
            a.shape([(hx + px, 30 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (hx - px, 30 - py)], color, outline=DETAIL * 1.4, corner=2, depth=2, light_k=0.4)
            hx2, hy2 = hx + (span - 20) * ux, 30 + (span - 20) * uy
            for s_ in (-1, 1):
                a.shape(ellipse(hx2 + s_ * px * 1.3, hy2 + s_ * py * 1.3, 5, 4, 16), knob, outline=FINE * 1.3, depth=1, mottle=0)
        return a.image()

    return make


def saloon(seed=1601, color=rgb("#b8915a")):
    w, h = T, 120

    def make():
        a = Art(w, h, seed)
        a.shape(rect(4, h / 2 - 6, w - 4, h / 2 + 6), shade(FRAME, 0.25), outline=DETAIL, corner=2, depth=2, mottle=0)
        for x0 in (2, w - 20):
            a.shape(rect(x0, h / 2 - 20, x0 + 18, h / 2 + 20), FRAME, outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.35)
        half = (w - 40) / 2 - 4
        for hx, base in ((20, 0.42), (w - 20, math.pi + 0.42)):
            ux, uy = math.cos(base), math.sin(base)
            x1, y1 = hx + half * ux, h / 2 + half * uy
            px, py = -uy * 6, ux * 6
            a.shape([(hx + px, h / 2 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (hx - px, h / 2 - py)], color, outline=DETAIL * 1.3, corner=2, depth=2, light_k=0.4, detail=lambda art, p, hx=hx, ux=ux, uy=uy: [art.ink([(hx + t * ux - uy * 5, h / 2 + t * uy + ux * 5), (hx + t * ux + uy * 5, h / 2 + t * uy - ux * 5)], FINE, color=shade(color, 0.5), alpha=0.8, taper=False) for t in range(16, int(half) - 6, 14)])
        return a.image()

    return make


def sliding(seed, color, open_=0.0, w=SW, h=96, track=IRON):
    """A sliding barn door hung on a rail along the wall, `open_` slid aside."""

    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h, FRAME, depth=22)
        a.ink([(8, h / 2 - 20), (w - 8, h / 2 - 20)], DETAIL * 2.2, color=INK, taper=False)
        a.ink([(8, h / 2 - 20), (w - 8, h / 2 - 20)], DETAIL * 1.2, color=track, taper=False)
        span = w - 48
        x0 = 24 + span * 0.5 * open_
        x1 = x0 + span / 2
        a.shape(rect(x0, h / 2 - 12, x1, h / 2 + 12), color, outline=DETAIL * 1.4, corner=3, depth=3, light_k=0.4, detail=lambda art, p: [art.ink([(x, h / 2 - 11), (x, h / 2 + 11)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False) for x in range(int(x0) + 26, int(x1) - 6, 26)])
        a.ink([(x0 + 8, h / 2 - 10), (x1 - 8, h / 2 + 10)], DETAIL * 1.2, color=shade(color, 0.45))
        x2 = 24 + span / 2 + (span / 2) * (0.5 * open_) if open_ else 24 + span / 2
        if open_ < 1:
            a.shape(rect(24 + span / 2 + 2, h / 2 - 12, w - 24, h / 2 + 12), color, outline=DETAIL * 1.4, corner=3, depth=3, light_k=0.4, detail=lambda art, p: [art.ink([(x, h / 2 - 11), (x, h / 2 + 11)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False) for x in range(int(24 + span / 2) + 26, int(w - 24) - 6, 26)]) if open_ == 0 else None
        for x in (x0 + 14, x1 - 14):
            a.shape(ellipse(x, h / 2 - 20, 6, 6, 16), track, outline=FINE * 1.3, depth=1, mottle=0)
        del x2
        return a.image()

    return make


# -- metal doors ---------------------------------------------------------------------------------


def vault_door(seed=1611):
    w, h = T, 110

    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h, DARK_STONE, depth=30)
        a.shape(rect(30, h / 2 - 22, w - 30, h / 2 + 22), STEEL, outline=DETAIL * 1.6, corner=6, depth=4, light_k=0.45, detail=lambda art, p: [dot(art, x, y, 2.4, tint(STEEL, 0.45)) for x in range(42, w - 30, 16) for y in (h / 2 - 16, h / 2 + 16)])
        cx, cy = w / 2, h / 2
        a.shape(ellipse(cx, cy, 15, 15, 32), shade(STEEL, 0.2), outline=DETAIL * 1.3, depth=2, light_k=0.5, mottle=0)
        for k in range(4):
            t = math.pi / 4 + k * math.pi / 2
            a.ink([(cx, cy), (cx + 24 * math.cos(t), cy + 24 * math.sin(t))], DETAIL * 1.4, color=BRASS)
        dot(a, cx, cy, 5, BRASS)
        return a.image()

    return make


def bronze_door(seed=1612):
    return double(seed, BRONZE, "rivets", frame=DARK_STONE, trim=shade(BRONZE, 0.3), knob=GOLD, ring=True)


# -- gates -------------------------------------------------------------------------------------------


def picket_gate(seed, color=rgb("#e4ddd0"), w=T, h=70, open_=False):
    def make():
        a = Art(w, h, seed)
        py = 36 if open_ else h / 2
        for x0 in (4, w - 26):
            a.shape(rect(x0, py - 14, x0 + 22, py + 14), FRAME, outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.35)
        if open_:
            ang = 1.1
            span = w - 56
            y0 = 36
            swing(a, 26, y0, span, 0.08, ang - 0.05)
            pts = [(26 + t * math.cos(ang), y0 + t * math.sin(ang)) for t in range(10, int(span), 16)]
            a.ink([(26, y0), (26 + span * math.cos(ang), y0 + span * math.sin(ang))], DETAIL * 2.2, color=INK, taper=False)
            a.ink([(26, y0), (26 + span * math.cos(ang), y0 + span * math.sin(ang))], DETAIL * 1.2, color=color, taper=False)
        else:
            a.shape(rect(26, h / 2 - 3, w - 26, h / 2 + 3), color, outline=DETAIL, corner=2, depth=1, mottle=0)
            pts = [(x, h / 2) for x in range(36, w - 26, 16)]
        for x, y in pts:
            a.shape(rect(x - 6, y - 6, x + 6, y + 6), color, outline=DETAIL * 1.1, corner=2, depth=1, light_k=0.3, mottle=0)
        return a.image()

    return make


def rail_gate(seed, color=rgb("#8a6040"), w=T, h=70):
    def make():
        a = Art(w, h, seed)
        for x0 in (4, w - 28):
            a.shape(rect(x0, h / 2 - 16, x0 + 24, h / 2 + 16), shade(color, 0.2), outline=DETAIL * 1.4, corner=4, depth=4, light_k=0.35)
        for y in (h / 2 - 7, h / 2 + 7):
            a.shape(rect(28, y - 4, w - 28, y + 4), color, outline=DETAIL * 1.1, corner=3, depth=2, mottle=0)
        a.ink([(34, h / 2 - 7), (w - 34, h / 2 + 7)], DETAIL * 1.2, color=shade(color, 0.3))
        a.shape(rect(w - 46, h / 2 - 11, w - 34, h / 2 + 11), IRON, outline=FINE * 1.3, corner=2, depth=1, mottle=0)
        return a.image()

    return make


def spear_gate(seed, color=rgb("#3e3d42"), w=SW, h=80, gold_tips=False, open_=False):
    def make():
        a = Art(w, h, seed)
        leaves = [(26, w / 2 - 2), (w / 2 + 2, w - 26)]
        if open_:
            yy = 36
            a.shape(rect(4, yy - 6, w - 4, yy + 6), shade(DARK_STONE, 0.25), outline=DETAIL, corner=2, depth=2, mottle=0)
            for x0 in (2, w - 28):
                a.shape(rect(x0, yy - 24, x0 + 26, yy + 24), DARK_STONE, outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.35)
            for hx, side in ((26, -1), (w - 26, 1)):
                ang = 1.2 if side < 0 else math.pi - 1.2
                L = h - yy - 24
                if side < 0:
                    swing(a, hx, yy, L, 0.08, 1.15)
                else:
                    swing(a, hx, yy, L, math.pi - 1.15, math.pi - 0.08)
                a.ink([(hx, yy), (hx + L * math.cos(ang), yy + L * math.sin(ang))], DETAIL * 2.6, color=INK, taper=False)
                a.ink([(hx, yy), (hx + L * math.cos(ang), yy + L * math.sin(ang))], DETAIL * 1.5, color=color, taper=False)
            return a.image()
        frame_posts(a, w, h, DARK_STONE, depth=26)
        if False:
            for hx, side in ((26, -1), (w - 26, 1)):
                ang = 1.2 if side < 0 else math.pi - 1.2
                span = w / 2 - 28
                swing(a, hx, h / 2, min(span, h * 0.6), 0.08, 1.15) if side < 0 else swing(a, hx, h / 2, min(span, h * 0.6), math.pi - 1.15, math.pi - 0.08)
                L = min(span, h * 0.6)
                a.ink([(hx, h / 2), (hx + L * math.cos(ang), h / 2 + L * math.sin(ang))], DETAIL * 2.6, color=INK, taper=False)
                a.ink([(hx, h / 2), (hx + L * math.cos(ang), h / 2 + L * math.sin(ang))], DETAIL * 1.5, color=color, taper=False)
            return a.image()
        for x0, x1 in leaves:
            a.ink([(x0, h / 2), (x1, h / 2)], DETAIL * 2.8, color=INK, taper=False, wob=0)
            a.ink([(x0, h / 2), (x1, h / 2)], DETAIL * 1.6, color=color, taper=False, wob=0)
            for x in range(int(x0) + 12, int(x1), 16):
                tip = GOLD if gold_tips else color
                a.shape([(x - 5, h / 2 + 2), (x, h / 2 - 9), (x + 5, h / 2 + 2)], tip, outline=FINE * 1.2, corner=1, depth=1, light_k=0.5, mottle=0)
        return a.image()

    return make


def portcullis2(seed, color=IRON, frame=rgb("#8a857d"), raised=False, w=SW, h=84, wood=False):
    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h, frame, depth=28)
        if raised:
            a.shape(rect(28, h / 2 - 4, w - 28, h / 2 + 4), HOLE, outline=FINE, corner=1, depth=1, mottle=0)
            for x in range(40, w - 28, 22):
                dot(a, x, h / 2, 3.6, color)
            return a.image()
        col = rgb("#7a5233") if wood else color
        a.shape(rect(28, h / 2 - 9, w - 28, h / 2 + 9), shade(col, 0.2), outline=DETAIL * 1.4, corner=2, depth=2, mottle=0)
        for x in range(40, w - 28, 22):
            a.shape([(x - 5, h / 2 - 9), (x + 5, h / 2 - 9), (x + 5, h / 2 + 9), (x, h / 2 + 15), (x - 5, h / 2 + 9)], col, outline=FINE * 1.3, corner=1, depth=1, light_k=0.5, mottle=0)
        if wood:
            a.ink([(30, h / 2), (w - 30, h / 2)], DETAIL * 1.2, color=IRON, taper=False)
        return a.image()

    return make


# -- secret doors -------------------------------------------------------------------------------------


def bookshelf_door(seed=1631, open_=False):
    w, h = T, 250 if open_ else 80

    def books(a, x0, x1, y0, y1):
        x = x0 + 2
        palette = [rgb("#8a3f37"), rgb("#3c5a78"), rgb("#55743f"), rgb("#9a7a37"), rgb("#694a6e")]
        while x < x1 - 6:
            bw = a.rng.uniform(8, 14)
            a.shape(rect(x, y0, min(x1 - 2, x + bw), y1), a.rng.choice(palette), outline=FINE * 1.2, corner=1, depth=1, light_k=0.3, mottle=0)
            x += bw + 1

    def make():
        a = Art(w, h, seed)
        if open_:
            yy = 30
            a.shape(rect(4, yy - 6, w - 4, yy + 6), HOLE, outline=DETAIL, corner=2, depth=2, mottle=0)
            for x0 in (2, w - 22):
                a.shape(rect(x0, yy - 20, x0 + 20, yy + 20), rgb("#5a3a26"), outline=DETAIL * 1.4, corner=3, depth=4, light_k=0.35)
            ang = 1.1
            span = w - 46
            swing(a, 22, yy, span, 0.08, ang - 0.05)
            ux, uy = math.cos(ang), math.sin(ang)
            px, py = -uy * 16, ux * 16
            x1, y1 = 22 + span * ux, yy + span * uy
            a.shape([(22 + px, yy + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (22 - px, yy - py)], rgb("#6e4a2f"), outline=DETAIL * 1.4, corner=2, depth=3, light_k=0.35)
            palette = [rgb("#8a3f37"), rgb("#3c5a78"), rgb("#55743f"), rgb("#9a7a37"), rgb("#694a6e")]
            for t in range(14, int(span) - 10, 12):
                cx, cy = 22 + t * ux - px * 0.35, yy + t * uy - py * 0.35
                a.shape([(cx - ux * 5 - px * 0.4, cy - uy * 5 - py * 0.4), (cx + ux * 5 - px * 0.4, cy + uy * 5 - py * 0.4), (cx + ux * 5 + px * 0.4, cy + uy * 5 + py * 0.4), (cx - ux * 5 + px * 0.4, cy - uy * 5 + py * 0.4)], a.rng.choice(palette), outline=FINE * 1.1, corner=1, depth=1, mottle=0)
            return a.image()
        frame_posts(a, w, h, rgb("#5a3a26"), depth=20)
        a.shape(rect(20, h / 2 - 16, w - 20, h / 2 + 16), rgb("#6e4a2f"), outline=DETAIL * 1.4, corner=3, depth=3, light_k=0.35)
        books(a, 24, w - 24, h / 2 - 2, h / 2 + 12)
        dot(a, w / 2 + 40, h / 2 - 9, 3, BRASS)
        return a.image()

    return make


def stone_secret(seed, color=STONE, pivot=False):
    w, h = T, 120 if pivot else 72

    def make():
        a = Art(w, h, seed)
        if pivot:
            for x0 in (2, w - 40):
                a.shape(rect(x0, h / 2 - 18, x0 + 38, h / 2 + 18), vary(a.rng, color, 0.05), outline=DETAIL * 1.3, corner=6, depth=4)
            ang = 0.5
            cx, cy = w / 2, h / 2
            L = (w - 84) / 2
            ux, uy = math.cos(ang), math.sin(ang)
            pts = [(cx - L * ux - uy * 14, cy - L * uy + ux * 14), (cx + L * ux - uy * 14, cy + L * uy + ux * 14), (cx + L * ux + uy * 14, cy + L * uy - ux * 14), (cx - L * ux + uy * 14, cy - L * uy - ux * 14)]
            a.shape(pts, tint(color, 0.05), outline=DETAIL * 1.4, corner=4, depth=4, light_k=0.4)
            dot(a, cx, cy, 4, shade(color, 0.5))
            return a.image()
        # One stretch of wall (inked body, thin joints between its blocks)
        # with the hidden door's seams a little darker.
        a.shape(rect(1, 7, w - 1, h - 7), grout(color), outline=DETAIL * 1.4, corner=4, depth=2, shade_k=0.2, light_k=0, ao=0.1, mottle=0)
        x = 0.0
        for wdt in split(w, a.rng, 40, 64):
            c = vary(a.rng, color, 0.045)
            a.shape(rect(max(x, 3) + 0.9, 9, min(x + wdt, w - 3) - 0.9, h - 9), c, outline=JOINT, outline_color=joint_color(c), outline_alpha=JOINT_ALPHA, corner=2, wob=0.3, depth=3, shade_k=0.35, light_k=0.25, ao=0.1)
            x += wdt
        a.ink([(36, 10), (36, h - 10)], DETAIL, color=shade(color, 0.5), alpha=0.8)
        a.ink([(w - 36, 10), (w - 36, h - 10)], DETAIL, color=shade(color, 0.5), alpha=0.8)
        a.shape(ellipse(w - 50, h / 2, 6, 6, 16), shade(color, 0.25), outline=FINE * 1.2, depth=1, mottle=0)
        return a.image()

    return make


# -- arches ------------------------------------------------------------------------------------------


def arch2(seed, color, w=T, h=84, kind="voussoir", broken=False):
    def make():
        a = Art(w, h, seed)
        pw = 32 if w <= T else 40
        for x0 in (2, w - pw - 2):
            a.shape(rect(x0, 6, x0 + pw, h - 6), color, outline=DETAIL * 1.4, corner=6, depth=5, light_k=0.4, detail=(lambda art, p, x0=x0: [art.ink([(x0 + 3, y), (x0 + pw - 3, y)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False) for y in range(18, h - 8, 16)]) if kind == "brick" else None)
        if broken:
            x_end = w * 0.55
            a.shape([(pw, h / 2 - 11), (x_end, h / 2 - 11), (x_end - 10, h / 2 - 2), (x_end + 6, h / 2 + 4), (x_end - 6, h / 2 + 11), (pw, h / 2 + 11)], tint(color, 0.08), outline=DETAIL * 1.2, corner=2, depth=3)
            for _ in range(5):
                x, y = a.rng.uniform(x_end + 10, w - pw - 16), a.rng.uniform(16, h - 16)
                r = a.rng.uniform(6, 11)
                a.shape([(x + r * math.cos(t), y + r * math.sin(t)) for t in [k * 1.2 + a.rng.uniform(-0.3, 0.3) for k in range(5)]], vary(a.rng, color, 0.06), outline=DETAIL, corner=1, depth=2, mottle=0)
            return a.image()

        def courses(art, p):
            if kind == "voussoir":
                for x in range(pw + 18, w - pw, 22):
                    art.ink([(x, h / 2 - 11), (x, h / 2 + 11)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False)
            elif kind == "brick":
                for x in range(pw + 12, w - pw, 14):
                    art.ink([(x + 7 * ((x // 14) % 2), h / 2 - 11), (x + 7 * ((x // 14) % 2), h / 2)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False)
                    art.ink([(x + 7 * (1 - (x // 14) % 2), h / 2), (x + 7 * (1 - (x // 14) % 2), h / 2 + 11)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False)
                art.ink([(pw, h / 2), (w - pw, h / 2)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA, taper=False)
            elif kind == "wood":
                art.ink([(pw, h / 2 - 4), (w - pw, h / 2 - 3)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA)
                art.ink([(pw, h / 2 + 4), (w - pw, h / 2 + 5)], JOINT, color=joint_color(color), alpha=JOINT_ALPHA)

        a.shape(rect(pw, h / 2 - 11, w - pw, h / 2 + 11), tint(color, 0.08), outline=DETAIL * 1.2, corner=3, depth=3, detail=courses)
        if kind == "pointed":
            a.shape([(w / 2 - 14, h / 2 - 13), (w / 2 + 14, h / 2 - 13), (w / 2 + 20, h / 2), (w / 2 + 14, h / 2 + 13), (w / 2 - 14, h / 2 + 13), (w / 2 - 20, h / 2)], tint(color, 0.15), outline=DETAIL * 1.2, corner=2, depth=2)
        elif kind == "voussoir":
            a.shape(rect(w / 2 - 10, h / 2 - 14, w / 2 + 10, h / 2 + 14), tint(color, 0.15), outline=DETAIL * 1.2, corner=2, depth=2)
        elif kind == "round":
            a.shape(ellipse(w / 2, h / 2, 16, 14, 24), tint(color, 0.15), outline=DETAIL * 1.2, depth=2, mottle=0)
        return a.image()

    return make


# -- windows -------------------------------------------------------------------------------------------


def window2(seed, kind="glass", frame=FRAME, w=T, h=70, glass=GLASS, panes=2, color=None):
    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h, frame, depth=16)
        if kind == "glass":
            a.shape(rect(18, h / 2 - 6, w - 18, h / 2 + 6), glass, outline=DETAIL * 1.2, corner=2, depth=1, light_k=0.6, mottle=0)
            for k in range(1, panes):
                x = 18 + (w - 36) * k / panes
                a.ink([(x, h / 2 - 6), (x, h / 2 + 6)], DETAIL, color=frame, taper=False)
            a.ink([(30, h / 2 - 2), (54, h / 2 - 2)], FINE * 1.3, color=(250, 250, 250), alpha=0.9, taper=False)
        elif kind == "sill":
            a.shape(rect(14, h / 2 + 4, w - 14, h / 2 + 18), tint(frame, 0.1), outline=DETAIL * 1.2, corner=3, depth=2)
            a.shape(rect(18, h / 2 - 6, w - 18, h / 2 + 4), glass, outline=DETAIL * 1.2, corner=2, depth=1, light_k=0.6, mottle=0)
            for x in range(40, w - 30, 34):
                a.shape(ellipse(x, h / 2 + 11, 9, 6, 16), color or rgb("#c8443a"), outline=FINE * 1.2, depth=1, mottle=0)
        elif kind == "barred":
            a.shape(rect(18, h / 2 - 6, w - 18, h / 2 + 6), HOLE, outline=DETAIL * 1.2, corner=2, depth=1, mottle=0)
            for x in range(28, w - 18, 14):
                dot(a, x, h / 2, 3.2, IRON)
        elif kind == "broken":
            a.shape(rect(18, h / 2 - 6, w - 18, h / 2 + 6), glass, outline=DETAIL * 1.2, corner=2, depth=1, light_k=0.6, mottle=0)
            a.shape([(w / 2 - 20, h / 2 - 6), (w / 2 + 6, h / 2 - 6), (w / 2 - 4, h / 2 + 6), (w / 2 - 30, h / 2 + 6)], HOLE, outline=FINE, corner=1, depth=1, mottle=0)
            for _ in range(7):
                x, y = a.rng.uniform(w / 2 - 50, w / 2 + 40), a.rng.uniform(h / 2 + 12, h - 6)
                a.shape([(x, y - 4), (x + 5, y + 2), (x - 3, y + 4)], tint(glass, 0.2), outline=FINE, corner=1, depth=1, mottle=0)
        elif kind == "shut":
            c = color or rgb("#5f8f6a")
            a.shape(rect(18, h / 2 - 7, w / 2 - 1, h / 2 + 7), c, outline=DETAIL * 1.2, corner=2, depth=1, light_k=0.4, mottle=0, detail=lambda art, p: [art.ink([(x, h / 2 - 6), (x, h / 2 + 6)], FINE, color=shade(c, 0.45), alpha=0.8, taper=False) for x in range(26, int(w / 2), 8)])
            a.shape(rect(w / 2 + 1, h / 2 - 7, w - 18, h / 2 + 7), c, outline=DETAIL * 1.2, corner=2, depth=1, light_k=0.4, mottle=0, detail=lambda art, p: [art.ink([(x, h / 2 - 6), (x, h / 2 + 6)], FINE, color=shade(c, 0.45), alpha=0.8, taper=False) for x in range(int(w / 2) + 9, w - 18, 8)])
        elif kind == "open_shutters":
            c = color or rgb("#5f8f6a")
            a.shape(rect(18, h / 2 - 5, w - 18, h / 2 + 5), glass, outline=DETAIL, corner=2, depth=1, light_k=0.6, mottle=0)
            L = (w - 36) / 2 - 6
            for hx, t in ((18, 0.4), (w - 18, math.pi - 0.4)):
                x1, y1 = hx + L * math.cos(t), h / 2 + 6 + L * math.sin(t)
                ux, uy = math.cos(t), math.sin(t)
                px, py = -uy * 5, ux * 5
                a.shape([(hx + px, h / 2 + 6 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (hx - px, h / 2 + 6 - py)], c, outline=DETAIL * 1.2, corner=1, depth=1, light_k=0.4, mottle=0)
        elif kind == "stained":
            cols = color or [rgb("#c8443a"), rgb("#4f74a8"), rgb("#e2c068"), rgb("#5f8f6a")]
            n = 10
            for k in range(n):
                x0 = 18 + (w - 36) * k / n
                a.shape(rect(x0, h / 2 - 6, x0 + (w - 36) / n, h / 2 + 6), cols[k % len(cols)], outline=DETAIL, corner=1, depth=1, light_k=0.5, mottle=0)
            a.ink([(18, h / 2), (w - 18, h / 2)], FINE * 1.2, color=INK, alpha=0.9, taper=False)
        elif kind == "round":
            a.shape(rect(18, h / 2 - 9, w - 18, h / 2 + 9), tint(frame, 0.1), outline=DETAIL * 1.2, corner=4, depth=2)
            a.shape(ellipse(w / 2, h / 2, (w - 60) / 2, 6, 40), glass, outline=DETAIL * 1.1, depth=1, light_k=0.6, mottle=0)
            a.ink([(w / 2, h / 2 - 6), (w / 2, h / 2 + 6)], FINE * 1.3, color=frame, taper=False)
        elif kind == "slit":
            a.shape(rect(18, h / 2 - 9, w - 18, h / 2 + 9), frame, outline=DETAIL * 1.2, corner=2, depth=2)
            n = panes
            for k in range(n):
                cx = 18 + (w - 36) * (k + 0.5) / n
                a.shape([(cx - 18, h / 2 - 3), (cx + 18, h / 2 - 3), (cx + 22, h / 2 + 3), (cx - 22, h / 2 + 3)], HOLE, outline=FINE, corner=1, depth=1, mottle=0)
        elif kind == "cross_slit":
            a.shape(rect(18, h / 2 - 9, w - 18, h / 2 + 9), frame, outline=DETAIL * 1.2, corner=2, depth=2)
            a.shape(rect(w / 2 - 24, h / 2 - 3, w / 2 + 24, h / 2 + 3), HOLE, outline=FINE, corner=1, depth=1, mottle=0)
            a.shape(rect(w / 2 - 4, h / 2 - 8, w / 2 + 4, h / 2 + 8), HOLE, outline=FINE, corner=1, depth=1, mottle=0)
        elif kind == "lattice":
            a.shape(rect(18, h / 2 - 6, w - 18, h / 2 + 6), glass, outline=DETAIL * 1.2, corner=2, depth=1, light_k=0.6, mottle=0)
            for x in range(26, w - 18, 12):
                a.ink([(x, h / 2 - 6), (x + 6, h / 2 + 6)], FINE, color=shade(frame, 0.2), alpha=0.85, taper=False)
                a.ink([(x + 6, h / 2 - 6), (x, h / 2 + 6)], FINE, color=shade(frame, 0.2), alpha=0.85, taper=False)
        elif kind == "bay":
            a.shape([(18, h / 2 - 6), (w - 18, h / 2 - 6), (w - 40, h / 2 + 22), (40, h / 2 + 22)], tint(frame, 0.15), outline=DETAIL * 1.3, corner=3, depth=3)
            a.shape([(26, h / 2 - 2), (w - 26, h / 2 - 2), (w - 46, h / 2 + 18), (46, h / 2 + 18)], glass, outline=DETAIL, corner=2, depth=1, light_k=0.6, mottle=0)
            for x in (w / 2 - 30, w / 2 + 30):
                a.ink([(x, h / 2 - 2), (x, h / 2 + 18)], DETAIL, color=frame, taper=False)
        return a.image()

    return make


# -- doorways & portals -----------------------------------------------------------------------------


def bead_curtain(seed=1651, colors=(rgb("#c8443a"), rgb("#e2c068"), rgb("#4f74a8"))):
    w, h = T, 80

    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h)
        a.ink([(20, h / 2 - 10), (w - 20, h / 2 - 10)], DETAIL * 1.4, color=FRAME)
        for k, x in enumerate(range(26, w - 20, 9)):
            for j in range(3):
                dot(a, x, h / 2 - 4 + j * 7, 3.2, colors[(k + j) % len(colors)])
        return a.image()

    return make


def cloth_doorway(seed, cloth, w=T, h=80, tied=False):
    def make():
        a = Art(w, h, seed)
        frame_posts(a, w, h)
        a.ink([(16, h / 2 - 10), (w - 16, h / 2 - 10)], DETAIL * 1.4, color=BRASS)
        if tied:
            for x0, x1 in ((20, 62), (w - 62, w - 20)):
                a.shape(chaikin([(x0, h / 2 - 8), (x1, h / 2 - 8), (x1 - 6, h / 2 + 10), (x0 + 6, h / 2 + 10)], True, 1), cloth, outline=DETAIL * 1.2, corner=0, depth=2, light_k=0.4)
                a.ink([((x0 + x1) / 2 - 10, h / 2 + 2), ((x0 + x1) / 2 + 10, h / 2 + 2)], DETAIL, color=BRASS)
            return a.image()
        pts = [(20, h / 2 - 6)]
        for k in range(17):
            pts.append((20 + (w - 40) * k / 16, h / 2 - 6 + (5 if k % 2 else -1)))
        pts += [(w - 20, h / 2 + 8), (20, h / 2 + 8)]
        a.shape(pts, cloth, outline=DETAIL * 1.2, corner=1, depth=2, light_k=0.4)
        a.ink([(w / 2, h / 2 - 6), (w / 2, h / 2 + 8)], FINE * 1.3, color=shade(cloth, 0.45))
        return a.image()

    return make


def magic_doorway(seed, glow=rgb("#7fd3e0"), w=T, h=90, frame=DARK_STONE):
    def make():
        a = Art(w, h, seed)
        p = skia.Path()
        p.addOval(skia.Rect.MakeLTRB(24, h / 2 - 28, w - 24, h / 2 + 28))
        a.fill_path(p, glow, 0.35, blur=12)
        frame_posts(a, w, h, frame, depth=22)
        a.shape(rect(22, h / 2 - 7, w - 22, h / 2 + 7), tint(glow, 0.35), outline=DETAIL * 1.1, corner=6, depth=1, shade_k=0, light_k=0.3, mottle=0)
        for x in range(36, w - 30, 22):
            a.ink([(x, h / 2 - 3), (x + 8, h / 2 + 3)], FINE * 1.2, color=tint(glow, 0.7), alpha=0.9)
        for x0 in (11, w - 11):
            a.ink([(x0 - 4, h / 2 - 16), (x0 + 3, h / 2), (x0 - 4, h / 2 + 16)], FINE * 1.4, color=glow, alpha=0.95)
        return a.image()

    return make


# -- catalogue ----------------------------------------------------------------------------------------

PORTALS2 = {}
_seed = [1700]


def _add(name, maker):
    PORTALS2[name] = maker


def _s():
    _seed[0] += 1
    return _seed[0]


for wood, c in WOODS.items():
    _add(f"{wood} Plank Door", door(_s(), c, "plank"))
for wood in ("Oak", "Walnut", "Cherry", "Ebony"):
    _add(f"{wood} Panel Door", door(_s(), WOODS[wood], "panel", trim=None))
for name, c in PAINTS.items():
    _add(f"{name} Painted Door", door(_s(), c, "panel", trim=None, knob=IRON if name == "Yellow" else BRASS))
_add("Banded Door", door(_s(), WOODS["Oak"], "plank", trim=IRON, studs=True))
_add("Chevron Door", door(_s(), WOODS["Pine"], "chevron", trim=IRON))
_add("Rustic Door", door(_s(), WOODS["Weathered"], "plank", trim=rgb("#7a5a3e"), knob=IRON, ring=True))
_add("Temple Gold Door", door(_s(), GOLD, "carved", frame=rgb("#e4ddd0"), trim=None, knob=rgb("#7aa6c9")))
_add("Elven Door", door(_s(), rgb("#a8c08a"), "carved", frame=rgb("#c8b98a"), trim=None, knob=rgb("#e6dcc4")))
_add("Dwarven Stone Door", door(_s(), DARK_STONE, "stone", frame=rgb("#5d6068"), thick=22, trim=BRONZE, knob=BRONZE, ring=True))
_add("Iron Rivet Door", door(_s(), IRON, "rivets", trim=None, knob=STEEL, ring=True))
_add("Bronze Rivet Door", door(_s(), BRONZE, "rivets", frame=DARK_STONE, trim=None, knob=GOLD, ring=True))
_add("Vault Door", vault_door(_s()))
_add("Ring Handle Door", door(_s(), WOODS["Walnut"], "plank", trim=IRON, knob=IRON, ring=True))

for wood in ("Oak", "Walnut", "Pine", "Ebony"):
    _add(f"{wood} Double Door", double(_s(), WOODS[wood], "plank"))
_add("Panelled Double Door", double(_s(), WOODS["Cherry"], "panel", trim=None))
_add("Red Double Door", double(_s(), PAINTS["Red"], "panel", trim=None))
_add("Blue Double Door", double(_s(), PAINTS["Blue"], "panel", trim=None))
_add("Studded Double Door", double(_s(), WOODS["Walnut"], "plank", studs=True))
_add("Iron Double Door", double(_s(), IRON, "rivets", trim=None, knob=STEEL, ring=True))
_add("Bronze Double Door", bronze_door(_s()))
_add("Temple Double Door", double(_s(), GOLD, "carved", frame=rgb("#e4ddd0"), trim=None, knob=rgb("#7aa6c9")))
_add("Dwarven Double Door", double(_s(), DARK_STONE, "stone", frame=rgb("#5d6068"), thick=24, trim=BRONZE, knob=BRONZE, ring=True))
_add("Elven Double Door", double(_s(), rgb("#a8c08a"), "carved", frame=rgb("#c8b98a"), trim=None, knob=rgb("#e6dcc4")))

for wood in ("Oak", "Walnut", "Pine"):
    _add(f"{wood} Door Ajar", swung(_s(), WOODS[wood], 0.55))
for wood in ("Walnut", "Pine"):
    _add(f"{wood} Door Open", swung(_s(), WOODS[wood], 1.4))
_add("Red Door Open", swung(_s(), PAINTS["Red"], 1.2))
_add("Iron Door Open", swung(_s(), IRON, 1.25, knob=STEEL))
_add("Double Door Ajar", swung(_s(), WOODS["Oak"], 0.5, double_=True))
_add("Walnut Double Door Open", swung(_s(), WOODS["Walnut"], 1.4, double_=True))
_add("Saloon Doors", saloon(_s()))
_add("Dark Saloon Doors", saloon(_s(), WOODS["Walnut"]))
_add("Barn Door", sliding(_s(), rgb("#a8483a"), 0.0))
_add("Barn Door Open", sliding(_s(), rgb("#a8483a"), 1.0))
_add("Sliding Wood Door", sliding(_s(), WOODS["Pine"], 0.0))

_add("White Picket Gate", picket_gate(_s()))
_add("White Picket Gate Open", picket_gate(_s(), open_=True, h=260))
_add("Wooden Picket Gate", picket_gate(_s(), WOODS["Oak"]))
_add("Farm Gate", rail_gate(_s()))
_add("Grey Farm Gate", rail_gate(_s(), WOODS["Weathered"]))
_add("Spear Gate", spear_gate(_s()))
_add("Gilded Spear Gate", spear_gate(_s(), gold_tips=True))
_add("Spear Gate Open", spear_gate(_s(), open_=True, h=260))
_add("Single Iron Gate", spear_gate(_s(), w=T))
_add("Raised Portcullis", portcullis2(_s(), raised=True))
_add("Wooden Portcullis", portcullis2(_s(), wood=True))
_add("Dark Portcullis", portcullis2(_s(), rgb("#3e3d42"), DARK_STONE))
_add("Small Portcullis", portcullis2(_s(), w=T))

_add("Bookshelf Secret Door", bookshelf_door(_s()))
_add("Bookshelf Secret Door Open", bookshelf_door(_s(), open_=True))
_add("Pivot Stone Door", stone_secret(_s(), pivot=True))
_add("Dark Secret Door", stone_secret(_s(), DARK_STONE))
_add("Sandstone Secret Door", stone_secret(_s(), rgb("#cdb48a")))

_add("Round Stone Arch", arch2(_s(), STONE, kind="round"))
_add("Pointed Stone Arch", arch2(_s(), STONE, kind="pointed"))
_add("Brick Arch", arch2(_s(), BRICK, kind="brick"))
_add("Wide Brick Arch", arch2(_s(), BRICK, w=SW, kind="brick"))
_add("Wide Stone Arch", arch2(_s(), STONE, w=SW))
_add("Sandstone Arch", arch2(_s(), rgb("#cdb48a")))
_add("Dark Stone Arch", arch2(_s(), DARK_STONE, kind="pointed"))
_add("Marble Arch", arch2(_s(), rgb("#e4dfd4"), kind="round"))
_add("Timber Arch", arch2(_s(), WOODS["Walnut"], kind="wood"))
_add("Broken Arch", arch2(_s(), STONE, broken=True))
_add("Broken Brick Arch", arch2(_s(), BRICK, kind="brick", broken=True))

_add("Two Pane Window", window2(_s(), "glass", panes=2))
_add("Four Pane Window", window2(_s(), "glass", panes=4))
_add("Wide Window", window2(_s(), "glass", w=SW, panes=6))
_add("Dark Frame Window", window2(_s(), "glass", frame=WOODS["Ebony"], panes=3))
_add("White Frame Window", window2(_s(), "glass", frame=rgb("#e4ddd0"), panes=3))
_add("Stone Frame Window", window2(_s(), "glass", frame=STONE, panes=2))
_add("Lattice Window", window2(_s(), "lattice"))
_add("Flower Box Window", window2(_s(), "sill", h=80))
_add("Blue Flower Box Window", window2(_s(), "sill", h=80, color=rgb("#6f8fd0")))
_add("Green Shutters Closed", window2(_s(), "shut"))
_add("Blue Shutters Closed", window2(_s(), "shut", color=PAINTS["Blue"]))
_add("Red Shutters Closed", window2(_s(), "shut", color=PAINTS["Red"]))
_add("Blue Shutters Open", window2(_s(), "open_shutters", h=110, color=PAINTS["Blue"]))
_add("Red Shutters Open", window2(_s(), "open_shutters", h=110, color=PAINTS["Red"]))
_add("Blue Stained Glass", window2(_s(), "stained", color=[rgb("#4f74a8"), rgb("#6f9fd0"), rgb("#2f4f78"), rgb("#a9cfdc")]))
_add("Red Stained Glass", window2(_s(), "stained", color=[rgb("#c8443a"), rgb("#e08a3a"), rgb("#8a2f2f"), rgb("#e2c068")]))
_add("Green Stained Glass", window2(_s(), "stained", color=[rgb("#5f8f6a"), rgb("#8fb85a"), rgb("#3f6a2a"), rgb("#e2c068")]))
_add("Purple Stained Glass", window2(_s(), "stained", color=[rgb("#8a6ad8"), rgb("#c8443a"), rgb("#4f74a8"), rgb("#e2c068")]))
_add("Wide Stained Glass", window2(_s(), "stained", w=SW))
_add("Barred Window", window2(_s(), "barred", frame=DARK_STONE))
_add("Wide Barred Window", window2(_s(), "barred", frame=DARK_STONE, w=SW))
_add("Round Window", window2(_s(), "round"))
_add("Stone Round Window", window2(_s(), "round", frame=STONE))
_add("Bay Window", window2(_s(), "bay", h=90, w=SW))
_add("Broken Window", window2(_s(), "broken", h=90))
_add("Double Arrow Slit", window2(_s(), "slit", frame=STONE, panes=2))
_add("Triple Arrow Slit", window2(_s(), "slit", frame=STONE, w=SW, panes=3))
_add("Cross Arrow Slit", window2(_s(), "cross_slit", frame=STONE))
_add("Dark Arrow Slit", window2(_s(), "slit", frame=DARK_STONE, panes=1))

_add("Bead Curtain", bead_curtain(_s()))
_add("Wooden Bead Curtain", bead_curtain(_s(), (rgb("#9a6c43"), rgb("#c39463"), rgb("#6e4a2f"))))
_add("Blue Curtain Doorway", cloth_doorway(_s(), PAINTS["Blue"]))
_add("Green Curtain Doorway", cloth_doorway(_s(), PAINTS["Green"]))
_add("Hide Curtain Doorway", cloth_doorway(_s(), rgb("#b8946a")))
_add("Tied Curtains", cloth_doorway(_s(), rgb("#a8483a"), tied=True))
_add("Tied Purple Curtains", cloth_doorway(_s(), rgb("#6a4a8a"), tied=True))
_add("Blue Magic Doorway", magic_doorway(_s()))
_add("Purple Magic Doorway", magic_doorway(_s(), rgb("#a86ad0")))
_add("Green Magic Doorway", magic_doorway(_s(), rgb("#7fd08a")))
_add("Fire Magic Doorway", magic_doorway(_s(), rgb("#f09a3a")))
