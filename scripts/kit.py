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
