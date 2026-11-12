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


