"""Shared palette and drawing helpers for the pack's objects."""

import math

import skia

from pen import DETAIL, FINE, INK, OUTLINE, Art, blob, chaikin, ellipse, mix, rect, rgb, shade, tint, to_path, vary  # noqa: F401

WOOD = rgb("#a8754a")
WOOD_DARK = rgb("#7a5233")
WOOD_LIGHT = rgb("#c39463")
IRON = rgb("#5d6068")
BRASS = rgb("#d2a647")
STONE = rgb("#a39d93")
RED = (192, 42, 42)  # colorable region: g == b
LEAF = rgb("#6b9a45")
LEAF_DARK = rgb("#4f7c34")
LEAF_LIGHT = rgb("#86b25a")


def dot(a, x, y, r, color=INK, alpha=1.0):
    p = skia.Path()
    p.addCircle(x, y, r)
    a.fill_path(p, color, alpha)


def ring(a, cx, cy, r, width, color, alpha=1.0):
    p = skia.Path()
    p.addCircle(cx, cy, r)
    a.stroke_path(p, color, width, alpha)


def grain_lines(a, x0, y0, x1, y1, n, color, vertical=False, alpha=0.65):
    """Wood grain: long, gently waving thin lines along the board."""
    for k in range(n):
        if vertical:
            gx = x0 + (x1 - x0) * (k + 0.5) / n + a.rng.uniform(-3, 3)
            ya = y0 + a.rng.uniform(4, (y1 - y0) * 0.25)
            yb = y1 - a.rng.uniform(4, (y1 - y0) * 0.25)
            pts = [(gx + 2 * math.sin(t / 30 + k), t) for t in range(int(ya), int(yb), 6)]
        else:
            gy = y0 + (y1 - y0) * (k + 0.5) / n + a.rng.uniform(-3, 3)
            xa = x0 + a.rng.uniform(4, (x1 - x0) * 0.25)
            xb = x1 - a.rng.uniform(4, (x1 - x0) * 0.25)
            pts = [(t, gy + 2 * math.sin(t / 30 + k)) for t in range(int(xa), int(xb), 6)]
        if len(pts) > 1:
            a.ink(pts, FINE * 0.85, color=color, alpha=alpha, wob=0.4)


def scallop(cx, cy, r, rng, bumps=9, depth=0.12, ry=None):
    """A leafy, cloud-like outline: round bumps around a circle."""
    ry = ry or r
    out = []
    n = bumps * 10
    phase = rng.uniform(0, 6.28)
    jit = [rng.uniform(-0.05, 0.05) for _ in range(bumps)]
    for i in range(n):
        t = i / n
        a = 2 * math.pi * t + phase
        b = (t * bumps) % 1
        k = 1 - depth + depth * math.sin(math.pi * b) + jit[int(t * bumps)]
        out.append((cx + r * k * math.cos(a), cy + ry * k * math.sin(a)))
    return out




def boards(a, x0, y0, x1, y1, color, n=3, vertical=False, seam=0.85, grain=True):
    """Plank seams (and grain) across a board, drawn inside its clip."""
    for k in range(1, n):
        if vertical:
            x = x0 + (x1 - x0) * k / n
            a.ink([(x, y0), (x, y1)], DETAIL * seam, color=shade(color, 0.5), alpha=0.85, taper=False, wob=0.5)
        else:
            y = y0 + (y1 - y0) * k / n
            a.ink([(x0, y), (x1, y)], DETAIL * seam, color=shade(color, 0.5), alpha=0.85, taper=False, wob=0.5)
    if grain:
        grain_lines(a, x0, y0, x1, y1, max(2, n * 2), shade(color, 0.45), vertical=vertical, alpha=0.45)


def board(a, x0, y0, x1, y1, color=WOOD, n=3, vertical=False, corner=6, outline=OUTLINE, depth=None, **kw):
    """A wooden board/top: a shaded, outlined rect with plank seams and grain."""
    return a.shape(rect(x0, y0, x1, y1), color, outline=outline, corner=corner, depth=depth, detail=lambda art, p: boards(art, x0, y0, x1, y1, color, n, vertical), **kw)


def cabinet(a, x0, y0, x1, y1, color=WOOD_DARK, front=0.28, inside=None, top_n=2):
    """A tall piece of furniture from above with a hint of perspective: its
    top board covers most of it; only a strip of its front shows below
    (where `inside(art, x0, y0, x1, y1)` draws what peeks out)."""
    fy = y1 - (y1 - y0) * front
    a.shape(rect(x0, fy - 8, x1, y1), shade(color, 0.25), corner=5, depth=4, shade_k=0.3, light_k=0.0, ao=0.4)
    if inside:
        with a.clip(to_path(rect(x0 + 10, fy - 8, x1 - 10, y1 - 6))):
            inside(a, x0 + 10, fy, x1 - 10, y1 - 6)
    top = board(a, x0, y0, x1, fy, color, n=top_n, corner=6)
    a.ink(rect(x0 + 10, y0 + 9, x1 - 10, fy - 9), FINE * 1.1, closed=True, color=shade(color, 0.5), alpha=0.7, wob=0.4)
    return top


def cushion(a, x0, y0, x1, y1, color=RED, tufts=True, outline=DETAIL * 1.3, corner=None):
    """A soft cushion (red = recolorable): rounded, with a highlight and tufting."""
    r = corner if corner is not None else min(x1 - x0, y1 - y0) * 0.28

    def tuft(art, path):
        art.ink([(x0 + 10, y0 + 8), ((x0 + x1) / 2, y0 + 5), (x1 - 10, y0 + 8)], FINE * 1.3, color=tint(color, 0.5), alpha=0.8)
        if tufts:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            for dx in (-(x1 - x0) * 0.22, 0, (x1 - x0) * 0.22):
                dot(art, cx + dx, cy, 2.4, shade(color, 0.5), 0.9)

    return a.shape(rect(x0, y0, x1, y1), color, outline=outline, corner=r, depth=8, shade_k=0.5, light_k=0.35, detail=tuft)


def soft_shadow(a, pts_or_center, r=None, dx=4, dy=5, alpha=0.35, blur=4):
    """A light shadow under a small item (gives piles a hint of depth)."""
    p = skia.Path()
    if r is not None:
        cx, cy = pts_or_center
        p.addCircle(cx + dx, cy + dy, r)
    else:
        p = to_path([(x + dx, y + dy) for x, y in pts_or_center])
    a.fill_path(p, INK, alpha, blur=blur)


def pile(a, cx, cy, R, n, item, ry=None, min_gap=0.55):
    """Items heaped in a mound: spread so they overlap only partly, drawn from
    the bottom of the heap (outer, lower) to its top (center), each with a
    soft shadow under it. `item(art, x, y, height)` draws one; height is
    0 at the heap's edge and 1 at its top."""
    ry = ry or R
    spots = []
    tries = 0
    while len(spots) < n and tries < n * 60:
        tries += 1
        ang = a.rng.uniform(0, 2 * math.pi)
        d = math.sqrt(a.rng.random())
        x, y = cx + R * d * math.cos(ang), cy + ry * d * math.sin(ang)
        h = max(0.0, 1 - d * d)
        if any(math.hypot(x - sx, y - sy) < R * min_gap * 0.18 for sx, sy, _ in spots):
            continue
        spots.append((x, y, h))
    for x, y, h in sorted(spots, key=lambda s: (s[2], s[1])):
        item(a, x, y, h)


def coin(a, x, y, h, r=None):
    """One gold coin, at a random tilt; lighter higher up the heap."""
    from pen import mix as _mix

    r = r or a.rng.uniform(7, 10)
    gold = _mix(shade((226, 184, 78), 0.3), tint((226, 184, 78), 0.25), h)
    tilt = a.rng.uniform(0.45, 1.0)
    rot = a.rng.uniform(0, math.pi)
    soft_shadow(a, (x, y), r * 0.9, 2, 3, 0.3, 2.5)
    a.shape(ellipse(x, y, r, r * tilt, 24, rot=rot), gold, outline=FINE * 1.3, corner=0, wob=0.1, depth=1.5, shade_k=0.35, light_k=0.5, ao=0, mottle=0)
    if tilt > 0.7:
        a.ink(ellipse(x, y, r * 0.62, r * 0.62 * tilt, 20, rot=rot), FINE * 0.7, closed=True, color=shade(gold, 0.4), alpha=0.7, wob=0.1)


def fruit(a, x, y, h, kind=None):
    from pen import mix as _mix

    kind = kind or a.rng.choice(("apple", "apple", "apple", "green", "pear"))
    base = {"apple": (196, 71, 58), "green": (156, 179, 74), "pear": (210, 190, 80)}[kind]
    col = _mix(shade(base, 0.25), tint(base, 0.15), h)
    r = a.rng.uniform(11, 15)
    soft_shadow(a, (x, y), r, 3, 4, 0.35, 3)
    if kind == "pear":
        pts = ellipse(x, y, r * 0.8, r * 1.15, 28, rot=a.rng.uniform(0, 3.14))
    else:
        pts = ellipse(x, y, r, r * 0.95, 28)
    a.shape(pts, col, outline=DETAIL, corner=0, wob=0.2, depth=3, shade_k=0.45, light_k=0.5, ao=0, mottle=0)
    a.ink([(x, y), (x + 3, y - 5)], FINE, color=(122, 82, 51))
