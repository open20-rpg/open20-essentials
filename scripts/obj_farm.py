"""Farm, animals, harbor and water (batch 13). Strict top-down, same pen
style. Animals face up (toward the top of the image); the editor rotates
them. Red (g == b) parts are recolorable."""

import math

import numpy as np

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


# -- four-legged animals -------------------------------------------------------------------------
# Seen from straight above, nose toward the top. The whole animal (head, neck,
# body) is ONE silhouette built around a slightly curved spine from a width
# profile, so it reads as an animal and not as a body with parts stuck on.
# Legs stay hidden under the body except for the tips of hooves/paws.

# Body plans: full width as a fraction of length; (s along the spine from
# nose 0 to rump 1, half-width as a fraction of the widest point); and where
# the eyes, ears and horns sit along the spine.
PLANS = {
    "cow": (0.50, [(0, 0.20), (0.02, 0.30), (0.07, 0.27), (0.13, 0.34), (0.17, 0.42), (0.21, 0.45), (0.245, 0.40), (0.29, 0.46), (0.34, 0.62), (0.40, 0.86), (0.47, 0.83), (0.58, 0.97), (0.66, 1.0), (0.75, 0.91), (0.82, 1.0), (0.87, 0.95), (0.95, 0.72), (0.99, 0.40), (1, 0.12)], dict(eye=0.17, ear=0.21, horn=0.215)),
    "horse": (0.32, [(0, 0.18), (0.02, 0.26), (0.07, 0.24), (0.12, 0.27), (0.19, 0.36), (0.21, 0.38), (0.25, 0.30), (0.28, 0.28), (0.34, 0.34), (0.40, 0.48), (0.47, 0.80), (0.50, 0.88), (0.60, 0.96), (0.70, 0.98), (0.78, 0.92), (0.86, 1.0), (0.92, 0.94), (0.98, 0.60), (1, 0.20)], dict(eye=0.19, ear=0.245, horn=0.24)),
    "pig": (0.55, [(0, 0.30), (0.03, 0.36), (0.08, 0.42), (0.14, 0.56), (0.20, 0.72), (0.28, 0.86), (0.40, 0.96), (0.55, 1.0), (0.70, 0.98), (0.84, 0.92), (0.94, 0.74), (1, 0.36)], dict(eye=0.11, ear=0.15, horn=0.15)),
    "goat": (0.38, [(0, 0.14), (0.03, 0.22), (0.10, 0.28), (0.16, 0.36), (0.19, 0.40), (0.24, 0.30), (0.30, 0.32), (0.38, 0.52), (0.44, 0.82), (0.55, 0.90), (0.66, 0.96), (0.76, 0.88), (0.84, 0.98), (0.93, 0.86), (0.98, 0.50), (1, 0.15)], dict(eye=0.165, ear=0.2, horn=0.195)),
    "sheep": (0.42, [(0, 0.14), (0.04, 0.24), (0.12, 0.34), (0.18, 0.38), (0.26, 0.34), (0.32, 0.42), (0.45, 0.7), (1, 0.7)], dict(eye=0.15, ear=0.2, horn=0.2)),
    "dog": (0.40, [(0, 0.10), (0.03, 0.18), (0.09, 0.24), (0.14, 0.40), (0.18, 0.44), (0.22, 0.40), (0.25, 0.30), (0.31, 0.36), (0.38, 0.62), (0.44, 0.90), (0.52, 0.88), (0.62, 0.76), (0.70, 0.70), (0.80, 0.84), (0.86, 0.88), (0.95, 0.66), (1, 0.25)], dict(eye=0.125, ear=0.185, horn=0.18)),
    "hound": (0.36, [(0, 0.09), (0.04, 0.15), (0.11, 0.22), (0.16, 0.36), (0.20, 0.40), (0.23, 0.36), (0.27, 0.28), (0.33, 0.34), (0.40, 0.62), (0.46, 0.92), (0.54, 0.88), (0.64, 0.70), (0.72, 0.62), (0.81, 0.80), (0.87, 0.86), (0.95, 0.64), (1, 0.24)], dict(eye=0.15, ear=0.2, horn=0.2)),
    "cat": (0.40, [(0, 0.18), (0.03, 0.40), (0.08, 0.56), (0.12, 0.60), (0.17, 0.48), (0.22, 0.34), (0.28, 0.44), (0.36, 0.78), (0.46, 0.82), (0.58, 0.80), (0.72, 0.92), (0.82, 0.96), (0.92, 0.78), (1, 0.34)], dict(eye=0.07, ear=0.12, horn=0.12)),
}


class Spine:
    """A gently curved centreline from nose (s=0) to rump (s=1)."""

    def __init__(self, cx, top, L, W, prof, bend=0.0, rng=None):
        self.cx, self.top, self.L, self.W, self.bend = cx, top, L, W, bend
        self.ss, self.ws = zip(*prof)
        # Each side gets its own small irregularities, like a hand-traced line.
        j = (lambda: rng.uniform(-0.05, 0.05)) if rng else (lambda: 0.0)
        self.jl = [w * (1 + j()) for w in self.ws]
        self.jr = [w * (1 + j()) for w in self.ws]

    def xy(self, s):
        # The head and neck turn to one side about the withers (a slight pose);
        # the body sways a little the other way.
        pivot = 0.42
        x, y = self.cx - self.bend * self.L * 0.03 * math.sin(math.pi * s), self.top + s * self.L
        if s < pivot:
            t = (pivot - s) / pivot
            ang = self.bend * 0.75 * (t * (2 - t))
            px, py = self.cx, self.top + pivot * self.L
            dx, dy = x - px, y - py
            c, sn = math.cos(ang), math.sin(ang)
            x, y = px + dx * c - dy * sn, py + dx * sn + dy * c
        return (x, y)

    def frame(self, s):
        e = 1e-3
        x0, y0 = self.xy(max(0, s - e))
        x1, y1 = self.xy(min(1, s + e))
        n = math.hypot(x1 - x0, y1 - y0) or 1
        tx, ty = (x1 - x0) / n, (y1 - y0) / n
        x, y = self.xy(s)
        return x, y, tx, ty, -ty, tx  # point, tangent (toward the rump), normal (right)

    def hw(self, s):
        return float(np.interp(s, self.ss, self.ws)) * self.W / 2

    def at(self, s, side=0.0, ahead=0.0):
        """Spine point s, `side` half-widths to the right (negative: left),
        `ahead` px toward the nose."""
        x, y, tx, ty, nx, ny = self.frame(s)
        h = self.hw(s) * side
        return (x + nx * h - tx * ahead, y + ny * h - ty * ahead)

    def side_pt(self, s, w, side):
        x, y, tx, ty, nx, ny = self.frame(s)
        h = w * self.W / 2 * side
        return (x + nx * h, y + ny * h)

    def outline(self, s0=0.0, s1=1.0):
        """The silhouette through the landmarks (nose, cheeks, poll, neck,
        shoulders, ribs, flank, hips, rump), each side traced on its own and
        rounded with chaikin."""
        keep = [i for i, s in enumerate(self.ss) if s0 <= s <= s1]
        left = [self.side_pt(self.ss[i], self.jl[i], -1) for i in keep]
        right = [self.side_pt(self.ss[i], self.jr[i], 1) for i in keep]
        if s1 < 1:
            left.append(self.side_pt(s1, float(np.interp(s1, self.ss, self.jl)), -1))
            right.append(self.side_pt(s1, float(np.interp(s1, self.ss, self.jr)), 1))
        return chaikin(left + right[::-1], True, 3)

    def line(self, s0, s1, side=0.0, n=24):
        return [self.at(s0 + (s1 - s0) * k / n, side) for k in range(n + 1)]


def autocrop(img, pad=10):
    box = img.getchannel("A").getbbox()
    if not box:
        return img
    x0, y0, x1, y1 = box
    return img.crop((max(0, x0 - pad), max(0, y0 - pad), min(img.width, x1 + pad), min(img.height, y1 + pad)))


def fur(art, sp, color, n, s0=0.3, s1=0.95, L=10, alpha=0.35):
    """Short hair strokes over the back, lying toward the rump and outward."""
    for _ in range(n):
        s = art.rng.uniform(s0, s1)
        side = art.rng.choice((-1, 1)) * art.rng.uniform(0.3, 0.9)
        _, _, tx, ty, nx, ny = sp.frame(s)
        px, py = sp.at(s, side)
        ox, oy = nx * side * 0.4, ny * side * 0.4
        art.ink([(px, py), (px + (tx + ox) * L, py + (ty + oy) * L)], FINE * 0.9, color=color, alpha=alpha, wob=0.2)


def legs(a, sp, color, hoof, s_front, s_back, length, width, paw=False):
    """Only the tips of the legs peek out from under chest and hips, in
    mid-stride (one front leg reaching forward, the other back)."""
    gait = ((s_front - 0.035, -1), (s_front + 0.03, 1), (s_back + 0.03, -1), (s_back - 0.02, 1))
    for s, side in gait:
        x, y = sp.at(s, side * 0.9)
        _, _, tx, ty, nx, ny = sp.frame(s)
        x, y = x + nx * side * length * 0.35, y + ny * side * length * 0.35
        if paw:
            a.shape(blob(x, y, width * 0.55, a.rng, 7, 0.08, ry=width * 0.62), color, outline=DETAIL * 1.2, smooth=True, depth=1, mottle=0, shade_k=0.25, light_k=0)
            for k in (-1, 0, 1):  # toes
                px, py = x - tx * width * 0.45 + nx * k * width * 0.22, y - ty * width * 0.45 + ny * k * width * 0.22
                a.ink([(px + tx * 3, py + ty * 3), (px - tx * 1, py - ty * 1)], FINE, color=shade(color, 0.5), alpha=0.7)
        else:
            a.shape(blob(x, y, width * 0.52, a.rng, 7, 0.06, ry=width * 0.42), hoof, outline=DETAIL * 1.2, smooth=True, depth=1, mottle=0, shade_k=0.25, light_k=0)
            a.ink([(x - nx * side * width * 0.1 - tx * width * 0.4, y - ny * side * width * 0.1 - ty * width * 0.4), (x - tx * width * 0.05, y - ty * width * 0.05)], FINE * 1.1, color=shade(hoof, 0.5), alpha=0.7)


def tail(a, sp, kind, color, length):
    bx, by = sp.at(0.985)
    _, _, tx, ty, nx, ny = sp.frame(1.0)
    sw = a.rng.choice((-1, 1))

    def pt(f_along, f_side):
        return (bx + tx * length * f_along + nx * sw * length * f_side, by + ty * length * f_along + ny * sw * length * f_side)

    if kind == "rope":  # cattle, donkey: thin tail with a tuft
        pts = chaikin([(bx, by - 4), pt(0.3, 0.16), pt(0.65, 0.02), pt(1.0, 0.14)], False, 3)
        a.ink(pts, 11, color=INK, taper=False)
        a.ink(pts, 5.5, color=color, taper=False)
        ex, ey = pts[-1]
        tuft = [(ex - 8, ey - 6), (ex + 8, ey - 6), (ex + 6, ey + 18), (ex, ey + 26), (ex - 6, ey + 18)]
        a.shape(tuft, shade(color, 0.3), outline=DETAIL * 1.2, corner=5, depth=2, mottle=0, detail=lambda art, p: [art.ink([(ex + d, ey - 3), (ex + d * 0.6, ey + 20)], FINE * 0.8, color=shade(color, 0.55), alpha=0.6) for d in (-3, 0, 3)])
    elif kind == "horse":  # long hair: full near the dock, wavy, tapering to locks
        mid = chaikin([(bx, by - 14), pt(0.35, 0.14), pt(0.7, -0.02), pt(1.0, 0.1)], False, 3)
        n = len(mid)
        w0 = sp.W * 0.11

        def wid(i):
            t = i / (n - 1)
            return w0 * (0.75 + 0.7 * math.sin(math.pi * min(1, t * 1.6)) ** 0.7) * (1 - 0.8 * t ** 1.5)

        def norm(i):
            (x0, y0), (x1, y1) = mid[max(0, i - 1)], mid[min(n - 1, i + 1)]
            d = math.hypot(x1 - x0, y1 - y0) or 1
            return -(y1 - y0) / d, (x1 - x0) / d

        left, right = [], []
        for i, (x, y) in enumerate(mid):
            ux, uy = norm(i)
            left.append((x - ux * wid(i), y - uy * wid(i)))
            right.append((x + ux * wid(i), y + uy * wid(i)))
        tip = mid[-1]
        tx2, ty2 = tip[0] - mid[-4][0], tip[1] - mid[-4][1]
        d = math.hypot(tx2, ty2) or 1
        tips = [(tip[0] + tx2 / d * 14 + k * 5, tip[1] + ty2 / d * 14) for k in (-1, 1)]

        def hair(art, p):
            for dd in (-0.7, -0.35, 0, 0.35, 0.7):
                pts_ = []
                for i, (x, y) in enumerate(mid[3:], 3):
                    ux, uy = norm(i)
                    pts_.append((x + ux * wid(i) * dd, y + uy * wid(i) * dd))
                art.ink(pts_, FINE * 1.1, color=shade(color, 0.45), alpha=0.6)

        a.shape(left + [tips[0], (tip[0], tip[1] + 4), tips[1]] + right[::-1], color, outline=DETAIL * 1.4, corner=4, wob=0.6, depth=3, light_k=0.3, detail=hair)
    elif kind == "curly":  # pig
        cx, cy = pt(0.6, 0.2)
        spiral = [(cx + (3 + 2.2 * t) * math.cos(t * 1.7), cy + (3 + 2.2 * t) * math.sin(t * 1.7)) for t in [k * 0.2 for k in range(26)]][::-1]
        spiral = [(bx, by - 2)] + spiral[:1] + spiral
        a.ink(spiral, 10, color=INK, taper=True)
        a.ink(spiral, 5.5, color=color, taper=True)
    elif kind == "stub":  # sheep, goat
        x, y = pt(0.25, 0)
        a.shape(ellipse(x, y, length * 0.34, length * 0.46, 20), color, outline=DETAIL * 1.3, depth=2, mottle=0)
    else:  # dog / cat: tapered, swinging to one side
        bend = 0.3 if kind == "dog" else 0.55
        pts = chaikin([(bx, by - 8), pt(0.45, bend * 0.35), pt(0.85, bend)], False, 3)
        w = sp.W * (0.15 if kind == "dog" else 0.13)
        a.ink(pts, w + 2 * DETAIL * 1.3, color=INK, taper=True, var=0.05)
        a.ink(pts, w, color=color, taper=True, var=0.05)


def head_frame(sp, s):
    """Map head-relative (u right, v forward) offsets to canvas points, so
    ears and horns turn with the head."""
    x, y, tx, ty, nx, ny = sp.frame(s)

    def P(px, py, u, v):
        return (px + nx * u - tx * v, py + ny * u - ty * v)

    return P


def rot_ellipse(P, ox, oy, u, v, ru, rv, n=24, pinch=0.0):
    """An ellipse in head coordinates centred at (u, v)."""
    return [P(ox, oy, u + ru * math.cos(t), v + rv * math.sin(t) * (1 + pinch * math.cos(t))) for t in [2 * math.pi * k / n for k in range(n)]]


def ears(a, sp, kind, s, color, inner=None):
    """Ears rooted on the skull: the base sits inside the head outline."""
    inner = inner or tint(color, 0.3)
    W = sp.W
    P = head_frame(sp, s)
    for side in (-1, 1):
        ox, oy = sp.at(s, side * 0.7)
        if kind == "cow":  # out to the side behind the horns, drooping back
            ox, oy = sp.at(s + 0.02, side * 0.7)
            P2 = head_frame(sp, s + 0.02)
            shp = [P2(ox, oy, side * (W * 0.12 + W * 0.15 * math.cos(t)), -W * 0.03 + W * 0.065 * math.sin(t) * (1 + 0.3 * math.cos(t)) - W * 0.05 * (1 + math.cos(t)) / 2) for t in [k * math.pi / 14 for k in range(28)]]
            inn = [P2(ox, oy, side * (W * 0.15 + W * 0.08 * math.cos(t)), -W * 0.05 + W * 0.025 * math.sin(t)) for t in [k * math.pi / 8 for k in range(16)]]
            a.shape(shp, color, outline=DETAIL * 1.3, corner=0, depth=2, light_k=0.3, mottle=0, detail=lambda art, p, inn=inn: art.fill_path(to_path(inn), inner, 0.8))
        elif kind in ("horse", "donkey"):  # upright, pointed, tipped forward
            ox, oy = sp.at(s, side * 0.45)
            Le = W * (0.24 if kind == "horse" else 0.40)
            pts = [P(ox, oy, -side * Le * 0.1, -Le * 0.12), P(ox, oy, side * Le * 0.25, -Le * 0.05), P(ox, oy, side * Le * 0.3, Le * 0.55), P(ox, oy, side * Le * 0.18, Le * 0.85), P(ox, oy, -side * Le * 0.02, Le * 0.4)]
            a.shape(chaikin(pts, True, 2), color, outline=DETAIL * 1.2, corner=0, depth=2, mottle=0, detail=lambda art, p, ox=ox, oy=oy, side=side, Le=Le, P=P: art.ink([P(ox, oy, side * Le * 0.1, 0), P(ox, oy, side * Le * 0.17, Le * 0.6)], FINE * 1.6, color=shade(color, 0.45), alpha=0.7))
        elif kind == "pig":  # big floppy triangles over the face
            ox, oy = sp.at(s, side * 0.45)
            r = W * 0.24
            pts = [P(ox, oy, -side * r * 0.35, -r * 0.35), P(ox, oy, side * r * 0.7, -r * 0.2), P(ox, oy, side * r * 0.35, r * 1.0)]
            a.shape(pts, color, outline=DETAIL * 1.3, corner=7, depth=3, light_k=0.35, mottle=0)
        elif kind in ("sheep", "goat"):  # sideways, drooping back
            a.shape(rot_ellipse(P, ox, oy, side * W * 0.1, -W * 0.05, W * 0.14, W * 0.055, pinch=0.25), color, outline=DETAIL * 1.2, corner=0, depth=2, mottle=0)
        elif kind == "floppy":  # dog: hanging down the sides of the head
            ox, oy = sp.at(s, side * 0.8)
            a.shape(rot_ellipse(P, ox, oy, side * W * 0.04, -W * 0.08, W * 0.09, W * 0.17, pinch=0.2), color, outline=DETAIL * 1.2, corner=0, depth=2, light_k=0.2, mottle=0)
        else:  # pointy cat ears
            ox, oy = sp.at(s, side * 0.55)
            r = W * 0.34
            pts = [P(ox, oy, -side * r * 0.45, -r * 0.25), P(ox, oy, side * r * 0.5, -r * 0.3), P(ox, oy, side * r * 0.3, r * 0.85)]
            inn = [P(ox, oy, -side * r * 0.15, -r * 0.15), P(ox, oy, side * r * 0.3, -r * 0.18), P(ox, oy, side * r * 0.22, r * 0.45)]
            a.shape(pts, color, outline=DETAIL * 1.2, corner=3, depth=2, mottle=0, detail=lambda art, p, inn=inn: art.fill_path(to_path(inn), inner, 0.85))


def horns(a, sp, s, color, kind):
    """Tapered horns growing from the poll, darker at the base."""
    W = sp.W
    P = head_frame(sp, s)
    for side in (-1, 1):
        ox, oy = sp.at(s, side * 0.45)
        if kind == "cow":  # short: out, then curving forward and up
            mid = [(0, 0), (side * W * 0.16, W * 0.01), (side * W * 0.23, W * 0.12)]
            wd = 13
        elif kind == "ox":  # long and wide, tips turned forward
            mid = [(0, 0), (side * W * 0.3, -W * 0.02), (side * W * 0.46, W * 0.14)]
            wd = 16
        else:  # goat: swept back over the neck
            ox, oy = sp.at(s, side * 0.3)
            mid = [(0, W * 0.03), (side * W * 0.12, -W * 0.16), (side * W * 0.07, -W * 0.34)]
            wd = 13
        pts = chaikin([P(ox, oy, u, v) for u, v in mid], False, 2)
        a.ink(pts, wd + 7, color=INK, taper=True)
        a.ink(pts, wd, color=color, taper=True)
        a.ink(pts[: len(pts) // 3], wd * 0.8, color=shade(color, 0.3), alpha=0.7, taper=False)
        for t in (0.45, 0.6, 0.75):  # growth rings
            i = int(len(pts) * t)
            (px, py), (qx, qy) = pts[i], pts[i + 1]
            d = math.hypot(qx - px, qy - py) or 1
            ux, uy = -(qy - py) / d, (qx - px) / d
            a.ink([(px - ux * wd * 0.3, py - uy * wd * 0.3), (px + ux * wd * 0.3, py + uy * wd * 0.3)], FINE, color=shade(color, 0.45), alpha=0.6, taper=False)


def eyes(a, sp, s, side_k=0.9, color=INK, closed=False):
    """Eyes on the sides of the head, as seen from above: small dark almonds."""
    for side in (-1, 1):
        x, y = sp.at(s, side * side_k)
        r = max(3.0, sp.W * 0.026)
        if closed:
            a.ink([(x - r, y), (x, y + r * 0.5), (x + r, y)], 2.2, color=INK, alpha=0.85)
            continue
        a.fill_path(to_path(ellipse(x, y, r * 0.8, r * 1.2, 14)), color, 1.0)
        a.fill_path(to_path(ellipse(x - r * 0.2, y - r * 0.4, r * 0.3, r * 0.3, 8)), (240, 236, 228), 0.85)


def nostrils(a, sp, color, k=0.42):
    for side in (-1, 1):
        x, y = sp.at(0.012, side * k)
        r = max(2.0, sp.W * 0.022)
        a.fill_path(to_path(ellipse(x, y, r, r * 1.4, 12, rot=side * 0.45)), color, 0.9)


def beast(kind, L, color, *, muzzle=None, spots=None, blaze=None, mane=None, tail_c=None, hoof=None, horn=None, ear_c=None, stripes=None, bend=None):
    """A quadruped `L` px from nose to rump; `kind` picks the body plan and
    the ears/tail/head details."""
    plan = {"ox": "cow", "calf": "cow", "donkey": "horse", "pony": "horse"}.get(kind, kind)
    Wk, profile, anch = PLANS[plan]
    head_k = {"cow": 1.3, "horse": 1.2, "goat": 1.2, "dog": 1.12, "hound": 1.12, "cat": 1.08, "sheep": 1.2}.get(plan, 1.0)
    profile = [(s, w * (head_k if s <= anch["ear"] + 0.02 else 1.0)) for s, w in profile]
    if kind == "pony":  # stockier, bigger head
        profile = [(s, w * 1.12) for s, w in profile]
    if kind == "calf":
        profile = [(s, w * (1.2 if s < 0.3 else 0.95)) for s, w in profile]

    def make(seed=1300):
        W = Wk * L
        size = int(L * 2.2 + 140)
        a = Art(size, size, seed)
        b = bend if bend is not None else a.rng.choice((-1, 1)) * a.rng.uniform(0.25, 0.5)
        sp = Spine(size / 2, 80 + W * 0.3, L, W, profile, b, a.rng)
        tc = tail_c or shade(color, 0.15)
        ec = ear_c or shade(color, 0.08)
        body = sp.outline()
        soft_shadow(a, body, dx=6, dy=8, alpha=0.28, blur=7)
        # Under the body: the tips of the legs, the tail.
        lc = shade(color, 0.12)
        if plan in ("cow", "horse", "goat"):
            legs(a, sp, lc, hoof or shade(color, 0.55), 0.47, 0.86, L * 0.07, W * (0.13 if plan == "horse" else 0.15))
        elif plan == "sheep":
            legs(a, sp, ec, shade(ec, 0.4), 0.47, 0.86, L * 0.06, W * 0.12)
        elif plan in ("dog", "hound", "cat"):
            legs(a, sp, lc, lc, 0.45, 0.87, L * 0.07, W * 0.17, paw=True)
        else:
            legs(a, sp, lc, shade(color, 0.45), 0.32, 0.84, L * 0.04, W * 0.12)
        tk = {"cow": "rope", "horse": "horse", "pig": "curly", "sheep": "stub", "goat": "stub", "dog": "dog", "hound": "dog", "cat": "cat"}[plan]
        if kind == "donkey":
            tk = "rope"
        tail(a, sp, tk, tc, {"rope": L * 0.32, "horse": L * 0.34, "curly": L * 0.12, "stub": W * 0.3, "dog": L * 0.42, "cat": L * 0.8}[tk])
        line = shade(color, 0.42)

        if plan == "sheep":
            # Dark head, then the woolly fleece over the neck and body.
            a.shape(sp.outline(0, 0.42), ec, outline=OUTLINE * 0.75, corner=0, depth=4, light_k=0.35)
            ears(a, sp, "sheep", anch["ear"], ec)
            eyes(a, sp, anch["eye"], 0.92, color=(20, 16, 14) if sum(ec) > 300 else (230, 220, 200))
            nostrils(a, sp, shade(ec, 0.6) if sum(ec) > 300 else tint(ec, 0.25), 0.35)
            cx, cy = sp.at(0.64)
            fleece = scallop(cx, cy, W * 0.52, a.rng, 16, 0.08, ry=L * 0.42)

            def wool(art, p):
                for _ in range(int(W * L / 380)):
                    x, y = art.rng.uniform(cx - W / 2, cx + W / 2), art.rng.uniform(cy - L * 0.42, cy + L * 0.42)
                    r = art.rng.uniform(4, 7) * L / 220
                    art.ink([(x + r * math.cos(t), y + r * math.sin(t)) for t in [k * 0.5 for k in range(11)]], FINE, color=shade(color, 0.3), alpha=0.55, wob=0.3)

            a.shape(fleece, color, outline=OUTLINE * 0.8, corner=0, depth=L * 0.05, light_k=0.45, detail=wool)
            hx, hy = sp.at(0.27)
            a.shape(scallop(hx, hy, W * 0.2, a.rng, 7, 0.2), tint(color, 0.05), outline=DETAIL * 1.3, corner=0, depth=2, mottle=0)
            return autocrop(a.image())

        def detail(art, p):
            if muzzle:
                mx, my = sp.at(0.0)
                art.fill_path(to_path(ellipse(mx, my, sp.hw(0.03) * 1.3, L * 0.06, 32)), muzzle, 1.0)
            if blaze:
                art.ink(sp.line(0.05, 0.22), sp.W * 0.07, color=blaze, alpha=0.95, taper=True, var=0.25)
            if spots:
                sc, n = spots
                for _ in range(n):
                    s = art.rng.uniform(0.2, 0.95)
                    x, y = sp.at(s, art.rng.uniform(-1.0, 1.0))
                    r = sp.hw(s) * art.rng.uniform(0.25, 0.5)
                    art.shape(blob(x, y, r, art.rng, 13, 0.4, ry=r * art.rng.uniform(0.8, 1.6)), sc, outline=0, smooth=True, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
            if stripes:  # tabby: broken stripes from the spine down each flank
                for k in range(8):
                    s = 0.32 + k * 0.08 + art.rng.uniform(-0.015, 0.015)
                    for side in (-1, 1):
                        if art.rng.random() < 0.15:
                            continue
                        art.ink(chaikin([sp.at(s, side * 0.12), sp.at(s + 0.012, side * 0.5), sp.at(s + 0.035, side * art.rng.uniform(0.75, 0.95))], False, 2), sp.W * 0.04, color=stripes, alpha=0.6, taper=True)
                art.ink(sp.line(0.3, 0.95), sp.W * 0.06, color=stripes, alpha=0.5, taper=True)
                for side in (-1, 1):
                    art.ink(sp.line(0.06, 0.16, side * 0.3), sp.W * 0.03, color=stripes, alpha=0.7, taper=True)
            # Anatomy: spine, shoulder blades and hip bones as soft lines.
            art.ink(sp.line(0.42, 0.92), FINE * 1.2, color=line, alpha=0.3)
            for side in (-1, 1):
                art.ink(chaikin([sp.at(0.42, side * 0.25), sp.at(0.48, side * 0.6), sp.at(0.56, side * 0.55)], False, 2), FINE * 1.1, color=line, alpha=0.45)
                art.ink(chaikin([sp.at(0.78, side * 0.3), sp.at(0.82, side * 0.65), sp.at(0.9, side * 0.55)], False, 2), FINE * 1.1, color=line, alpha=0.45)
            if plan == "pig":
                art.ink(chaikin([sp.at(0.22, -0.65), sp.at(0.25, 0), sp.at(0.22, 0.65)], False, 2), FINE * 1.1, color=line, alpha=0.4)
            else:  # cheek line where the head meets the neck
                for side in (-1, 1):
                    art.ink(chaikin([sp.at(anch["eye"] + 0.02, side * 0.6), sp.at(anch["ear"] + 0.03, side * 0.75), sp.at(anch["ear"] + 0.07, side * 0.6)], False, 2), FINE * 1.1, color=line, alpha=0.4)
            fur(art, sp, line, int(L / 8) if plan != "pig" else int(L / 22), L=max(6, L * 0.025))

        a.shape(body, color, outline=OUTLINE * 0.8, corner=0, wob=0.8, depth=L * 0.03, light_k=0.4, ao=0.25, detail=detail)
        if mane:
            # Mane: tapered strands falling from the neck crest down one side
            # and back, each over the one behind; a forelock between the ears.
            side = -1 if b > 0 else 1
            s0, s1 = anch["ear"] + 0.01, 0.47
            n = 8
            for k in range(n, -1, -1):
                s = s0 + (s1 - s0) * k / n
                x0, y0 = sp.at(s, -side * 0.1)
                _, _, tx, ty, nx, ny = sp.frame(s)
                Lh = sp.hw(s) * (1.0 + 0.3 * a.rng.random())
                ex, ey = x0 + nx * side * Lh + tx * Lh * 0.8, y0 + ny * side * Lh + ty * Lh * 0.8
                mx, my = x0 + nx * side * Lh * 0.6 + tx * Lh * 0.15, y0 + ny * side * Lh * 0.6 + ty * Lh * 0.15
                pts = chaikin([(x0, y0), (mx, my), (ex, ey)], False, 3)
                w = sp.W * 0.15
                a.ink(pts, w + 2 * DETAIL * 1.1, color=INK, taper=True, var=0.1)
                a.ink(pts, w, color=mane, taper=True, var=0.1)
                a.ink(pts[2:-3], FINE, color=shade(mane, 0.45), alpha=0.6, taper=True)
            for k in (-1, 0, 1):
                fp = [sp.at(anch["ear"] + 0.01, k * 0.12), sp.at(anch["ear"] - 0.03, k * 0.2), sp.at(anch["ear"] - 0.06, k * 0.14)]
                a.ink(fp, sp.W * 0.07 + 2 * DETAIL, color=INK, taper=True)
                a.ink(fp, sp.W * 0.07, color=mane, taper=True)
        ears(a, sp, {"cow": "cow", "horse": "donkey" if kind == "donkey" else "horse", "pig": "pig", "goat": "goat", "dog": "floppy", "hound": "floppy", "cat": "cat"}[plan], anch["ear"], ec)
        if horn:
            horns(a, sp, anch["horn"], horn, {"cow": "cow", "calf": "cow", "ox": "ox", "goat": "goat", "black_goat": "goat"}.get(kind, "goat"))
        if plan == "pig":
            x, y = sp.at(0.0)
            r = sp.hw(0.03) * 0.95
            a.shape(ellipse(x, y + r * 0.1, r, r * 0.7, 28), muzzle or shade(color, 0.08), outline=DETAIL * 1.3, depth=2, light_k=0.3, mottle=0)
            for side in (-1, 1):
                dot(a, x + side * r * 0.35, y + r * 0.1, r * 0.17, shade(color, 0.6))
            eyes(a, sp, anch["eye"], 0.75)
        elif plan == "cat":
            eyes(a, sp, anch["eye"], 0.6, color=rgb("#9a8a3a"))
            x, y = sp.at(0.0, 0, -4)
            a.shape([(x - 4, y), (x + 4, y), (x, y + 4)], rgb("#d89a9a"), outline=FINE, corner=1, depth=1, mottle=0)
            for side in (-1, 1):  # whiskers
                wx, wy = sp.at(0.03, side * 0.55)
                for k in (-1, 0, 1):
                    a.ink([(wx, wy), (wx + side * sp.W * 0.3, wy - sp.W * (0.06 + 0.06 * k))], 1.3, color=INK, alpha=0.5, wob=0.2)
        else:
            eyes(a, sp, anch["eye"], 0.92)
            if plan in ("dog", "hound"):
                x, y = sp.at(0.0, 0, -2)
                a.shape(ellipse(x, y + 4, sp.W * 0.055, sp.W * 0.04, 16), INK, outline=0, depth=1, shade_k=0, light_k=0, ao=0, mottle=0)
            else:
                nostrils(a, sp, shade(muzzle or color, 0.6))
        return autocrop(a.image())

    return make


def curled_cat(seed=1366, color=rgb("#3a3436"), stripes=None):
    """A cat asleep, curled into a ball with its tail wrapped round."""
    s = 240
    a = Art(s, s, seed)
    c = s / 2
    R = 62
    soft_shadow(a, ellipse(c, c, R, R * 0.92, 48), dx=5, dy=7, alpha=0.28, blur=6)
    body = [(c + R * math.cos(t) * (1 + 0.05 * math.sin(3 * t)), c + R * 0.92 * math.sin(t)) for t in [2 * math.pi * k / 72 for k in range(72)]]
    line = tint(color, 0.25)

    def detail(art, p):
        if stripes:
            for k in range(8):
                t = -1.2 + k * 0.42
                art.ink([(c + R * 0.3 * math.cos(t), c + R * 0.3 * math.sin(t)), (c + R * 0.95 * math.cos(t + 0.1), c + R * 0.95 * math.sin(t + 0.1))], 6, color=stripes, alpha=0.7, taper=True)
        # The spine curling round, and fur lying along it.
        art.ink([(c + R * 0.72 * math.cos(t), c + R * 0.66 * math.sin(t)) for t in [-3.0 + k * 0.12 for k in range(34)]], FINE * 1.2, color=line, alpha=0.5)
        for _ in range(30):
            t = art.rng.uniform(0, 6.28)
            r = art.rng.uniform(0.4, 0.9) * R
            x, y = c + r * math.cos(t), c + r * math.sin(t)
            art.ink([(x, y), (x - 7 * math.sin(t), y + 7 * math.cos(t))], FINE * 0.9, color=line, alpha=0.45)

    a.shape(body, color, outline=OUTLINE * 0.8, corner=0, smooth=True, depth=6, light_k=0.4, detail=detail)
    # Tail wrapped round the front, the head tucked against it.
    tp = [(c + R * 0.98 * math.cos(t), c + R * 0.9 * math.sin(t)) for t in [0.1 + k * 0.08 for k in range(30)]]
    a.ink(tp, 22 + 2 * DETAIL * 1.3, color=INK, taper=True, var=0.05)
    a.ink(tp, 22, color=shade(color, 0.05), taper=True, var=0.05)
    hx, hy = c - R * 0.12, c + R * 0.38
    for side in (-1, 1):
        ex, ey = hx + side * 22, hy - 16
        a.shape([(ex - side * 11, ey + 6), (ex + side * 10, ey + 4), (ex + side * 7, ey - 17)], color, outline=DETAIL * 1.2, corner=3, depth=2, mottle=0, detail=lambda art, p, ex=ex, ey=ey, side=side: art.fill_path(to_path([(ex - side * 4, ey + 3), (ex + side * 5, ey + 2), (ex + side * 5, ey - 8)]), tint(color, 0.3), 0.85))
    a.shape(ellipse(hx, hy, 34, 28, 36), tint(color, 0.06), outline=DETAIL * 1.6, depth=3, light_k=0.4, mottle=0)
    for side in (-1, 1):  # closed eyes
        a.ink([(hx + side * 8, hy + 2), (hx + side * 13, hy + 5), (hx + side * 18, hy + 2)], 2.4, color=tint(color, 0.45) if sum(color) < 300 else INK, alpha=0.9, taper=True)
    a.shape([(hx - 4, hy + 12), (hx + 4, hy + 12), (hx, hy + 16)], rgb("#d89a9a"), outline=FINE, corner=1, depth=1, mottle=0)
    return autocrop(a.image())


# -- birds and small animals ----------------------------------------------------------------


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


# The rat keeps the simple small-critter drawing.
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
        w, h = int(W + pad * 2 + (60 if oars else 0) + (W * 1.0 if sail else 0)), int(L + 60)
        a = Art(w, h, seed)
        cx, cy = (W / 2 + pad + 20 if sail else w / 2), h / 2
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
            return autocrop(a.image(), 14)
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
    "Cow": beast("cow", 400, rgb("#f2ece0"), muzzle=rgb("#e6b8a8"), spots=(rgb("#3a3430"), 7), horn=rgb("#e6dcc4"), tail_c=rgb("#e6dcd0"), hoof=rgb("#4a4440")),
    "Brown Cow": beast("cow", 400, rgb("#8a5a3a"), muzzle=rgb("#d8b8a0"), blaze=rgb("#efe6d8"), horn=rgb("#e6dcc4")),
    "Ox": beast("ox", 440, rgb("#6a4e3a"), muzzle=rgb("#c9a88a"), horn=rgb("#e6dcc4")),
    "Pig": beast("pig", 230, rgb("#e8b8a8"), muzzle=rgb("#e0a898")),
    "Piglet": beast("pig", 130, rgb("#f0c4b4"), muzzle=rgb("#e8b0a0")),
    "Black Pig": beast("pig", 230, rgb("#4a4248"), muzzle=rgb("#7a6a70")),
    "Sheep": beast("sheep", 220, rgb("#efe7d6"), ear_c=rgb("#3a3430")),
    "Black Sheep": beast("sheep", 220, rgb("#4a4442"), ear_c=rgb("#2a2422")),
    "Lamb": beast("sheep", 140, rgb("#f4eee2"), ear_c=rgb("#e0d0c0")),
    "Goat": beast("goat", 220, rgb("#d8ccb4"), muzzle=rgb("#c8b8a0"), horn=rgb("#8a7a6a"), tail_c=rgb("#c8bca4")),
    "Horse": beast("horse", 440, rgb("#8a5a3a"), muzzle=rgb("#5a3e2c"), blaze=rgb("#efe6d8"), mane=rgb("#3a2a22"), tail_c=rgb("#3a2a22")),
    "White Horse": beast("horse", 440, rgb("#ece4d8"), muzzle=rgb("#a89a94"), mane=rgb("#d8d0c4"), tail_c=rgb("#d8d0c4"), hoof=rgb("#6a625c")),
    "Black Horse": beast("horse", 440, rgb("#3a3436"), muzzle=rgb("#4a4446"), mane=rgb("#24201e"), tail_c=rgb("#24201e")),
    "Donkey": beast("donkey", 320, rgb("#8a8278"), muzzle=rgb("#e0d8cc"), mane=rgb("#4a4440"), tail_c=rgb("#6a625a")),
    "Dog": beast("dog", 190, rgb("#a8783e"), ear_c=rgb("#7a5228")),
    "Black Dog": beast("dog", 190, rgb("#3a3436"), ear_c=rgb("#2a2426")),
    "Hound": beast("hound", 220, rgb("#e6dccb"), spots=(rgb("#8a5a34"), 4), ear_c=rgb("#8a5a34")),
    "Cat": beast("cat", 130, rgb("#8a7a6a"), stripes=rgb("#5a4e44")),
    "Black Cat": lambda: curled_cat(1366, rgb("#3a3436")),
    "Orange Cat": beast("cat", 130, rgb("#d08a4a"), stripes=rgb("#a8602e")),
    "Calf": beast("calf", 270, rgb("#c9a07a"), muzzle=rgb("#e6c8b0"), tail_c=rgb("#b88e6a")),
    "Pony": beast("pony", 320, rgb("#a8845a"), muzzle=rgb("#7a5a3e"), mane=rgb("#e6dcc4"), tail_c=rgb("#e6dcc4")),
    "Black Goat": beast("goat", 220, rgb("#3a3436"), muzzle=rgb("#5a5254"), horn=rgb("#8a7a6a")),
    "Brown Sheep": beast("sheep", 220, rgb("#a88a6a"), ear_c=rgb("#3a3430")),
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
