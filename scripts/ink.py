"""Ink-and-wash drawing helpers for the built-in pack's art.

The look: dark, slightly wobbly ink outlines (as if drawn by hand), flat
fills, a subtle shade on the side away from the light (top-left), a soft
highlight on the side facing it, and a faint paper grain. Everything is
drawn at SS× and downsampled, so lines come out antialiased.
"""

import math
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

SS = 3  # supersampling factor
INK = (43, 36, 31)  # outline color: warm near-black


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def darker(c, t=0.18):
    return mix(c, (20, 16, 14), t)


def lighter(c, t=0.15):
    return mix(c, (255, 250, 240), t)


class Canvas:
    """An RGBA canvas drawn at SS× (coordinates are given at final scale)."""

    def __init__(self, w, h, seed=1, bg=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * SS, h * SS), bg)
        self.rng = random.Random(seed)

    # -- geometry ---------------------------------------------------------------

    def wobble(self, pts, closed=True, amp=0.6, step=6.0):
        """A hand-drawn version of a polyline: subdivided, nudged sideways a little."""
        if len(pts) < 2:
            return pts
        segs = list(zip(pts, pts[1:] + (pts[:1] if closed else [])))
        out = []
        phase = self.rng.uniform(0, 6.28)
        freq = self.rng.uniform(0.15, 0.3)
        k = 0.0
        for (x0, y0), (x1, y1) in segs:
            length = math.hypot(x1 - x0, y1 - y0)
            n = max(1, int(length / step))
            nx, ny = (-(y1 - y0) / (length or 1), (x1 - x0) / (length or 1))
            for i in range(n):
                t = i / n
                k += length / n
                d = amp * math.sin(phase + k * freq) + self.rng.uniform(-amp, amp) * 0.25
                out.append((x0 + (x1 - x0) * t + nx * d, y0 + (y1 - y0) * t + ny * d))
        if not closed:
            out.append(pts[-1])
        return out

    def _s(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    # -- primitives ---------------------------------------------------------------

    def fill(self, pts, color, alpha=255):
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon(self._s(pts), fill=color + (alpha,))
        self.img.alpha_composite(layer)

    def line(self, pts, width=2.2, color=INK, alpha=255, closed=False, wobble=True):
        p = self.wobble(pts, closed) if wobble else list(pts)
        if closed:
            p = p + p[:1]
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).line(self._s(p), fill=color + (alpha,), width=max(1, int(width * SS)), joint="curve")
        # Round caps.
        r = width * SS / 2
        d = ImageDraw.Draw(layer)
        for x, y in (self._s(p)[0], self._s(p)[-1]):
            d.ellipse((x - r, y - r, x + r, y + r), fill=color + (alpha,))
        self.img.alpha_composite(layer)

    def shape(self, pts, color, width=2.4, shade=0.16, light=0.1, offset=None, outline=True):
        """A filled, shaded, outlined polygon (map-top view, light from top-left)."""
        mask = Image.new("L", self.img.size, 0)
        ImageDraw.Draw(mask).polygon(self._s(self.wobble(pts, True, amp=0.35)), fill=255)
        self._shaded(mask, color, shade, light, offset)
        if outline:
            self.line(pts, width=width, closed=True)

    def ellipse(self, cx, cy, rx, ry, color, width=2.4, shade=0.16, light=0.1, n=48, outline=True):
        pts = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
        self.shape(pts, color, width, shade, light, outline=outline)
        return pts

    def _shaded(self, mask, color, shade, light, offset=None):
        """Flat color over `mask`, darkened toward its bottom-right edge and lit at its top-left."""
        size = self.img.size
        flat = Image.new("RGBA", size, color + (255,))
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        layer.paste(flat, (0, 0), mask)
        off = offset or max(3, int(min(size) * 0.025 / SS)) * SS
        if shade > 0:
            moved = ImageChops.offset(mask, -off, -off)
            rim = ImageChops.subtract(mask, moved).filter(ImageFilter.GaussianBlur(off * 0.7))
            rim = ImageChops.multiply(rim, mask)
            dark = Image.new("RGBA", size, darker(color, 0.55) + (0,))
            dark.putalpha(rim.point(lambda v: int(v * shade * 1.6)))
            layer.alpha_composite(dark)
        if light > 0:
            moved = ImageChops.offset(mask, off, off)
            rim = ImageChops.subtract(mask, moved).filter(ImageFilter.GaussianBlur(off * 0.7))
            rim = ImageChops.multiply(rim, mask)
            lite = Image.new("RGBA", size, lighter(color, 0.6) + (0,))
            lite.putalpha(rim.point(lambda v: int(v * light * 1.6)))
            layer.alpha_composite(lite)
        self.img.alpha_composite(layer)

    def dots(self, n, box, color=INK, r=(0.8, 1.6), alpha=200, mask_fn=None):
        x0, y0, x1, y1 = box
        d = ImageDraw.Draw(self.img)
        for _ in range(n):
            x, y = self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)
            if mask_fn and not mask_fn(x, y):
                continue
            rr = self.rng.uniform(*r) * SS
            d.ellipse((x * SS - rr, y * SS - rr, x * SS + rr, y * SS + rr), fill=color + (alpha,))

    def strokes(self, n, box, length=(4, 9), angle=(-0.4, 0.4), width=1.2, color=INK, alpha=150, mask_fn=None):
        """Short pen strokes (grass, grain, hatching)."""
        x0, y0, x1, y1 = box
        for _ in range(n):
            x, y = self.rng.uniform(x0, x1), self.rng.uniform(y0, y1)
            if mask_fn and not mask_fn(x, y):
                continue
            a = self.rng.uniform(*angle) - math.pi / 2
            ln = self.rng.uniform(*length)
            self.line([(x, y), (x + math.cos(a) * ln, y + math.sin(a) * ln)], width, color, alpha, wobble=False)

    # -- output ---------------------------------------------------------------

    def result(self, grain=0.035, seed=None):
        img = self.img.resize((self.w, self.h), Image.LANCZOS)
        if grain > 0:
            img = paper_grain(img, grain, seed if seed is not None else self.rng.randint(0, 10**6))
        return img


def paper_grain(img, amount=0.035, seed=0):
    """A faint paper texture over the color (alpha untouched)."""
    rs = np.random.RandomState(seed)
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    noise = rs.normal(0, 1, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
    noise = np.asarray(Image.fromarray(noise).resize((w, h), Image.BILINEAR))
    a[..., :3] *= 1 + noise[..., None] * amount
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


class Tile(Canvas):
    """A seamless (wrapping) square texture: anything drawn near an edge repeats on the other side."""

    def __init__(self, size, base, seed=1):
        super().__init__(size, size, seed, base + (255,))
        self.size = size

    def _wrap(self, fn, pts):
        s = self.size
        for dx in (-s, 0, s):
            for dy in (-s, 0, s):
                moved = [(x + dx, y + dy) for x, y in pts]
                xs = [p[0] for p in moved]
                ys = [p[1] for p in moved]
                if max(xs) < -8 or min(xs) > s + 8 or max(ys) < -8 or min(ys) > s + 8:
                    continue
                fn(moved)

    def wshape(self, pts, color, width=2.2, shade=0.16, light=0.1):
        # One wobble for all copies, so the wrapped parts line up.
        st = self.rng.getstate()
        def draw(p):
            self.rng.setstate(st)
            self.shape(p, color, width, shade, light)
        self._wrap(draw, pts)

    def wline(self, pts, width=1.6, color=INK, alpha=255, closed=False):
        st = self.rng.getstate()
        def draw(p):
            self.rng.setstate(st)
            self.line(p, width, color, alpha, closed)
        self._wrap(draw, pts)

    def wfill(self, pts, color, alpha=255):
        self._wrap(lambda p: self.fill(p, color, alpha), pts)

    def wstrokes(self, n, length=(4, 9), angle=(-0.4, 0.4), width=1.2, color=INK, alpha=150):
        for _ in range(n):
            x, y = self.rng.uniform(0, self.size), self.rng.uniform(0, self.size)
            a = self.rng.uniform(*angle) - math.pi / 2
            ln = self.rng.uniform(*length)
            self.wline([(x, y), (x + math.cos(a) * ln, y + math.sin(a) * ln)], width, color, alpha)

    def result(self, grain=0.035, seed=None):
        img = super().result(grain, seed)
        return seamless_grain_fix(img)


def seamless_grain_fix(img):
    """Paper grain isn't periodic: blend a few edge pixels so the tile still wraps cleanly."""
    a = np.asarray(img).astype(np.float32)
    k = 6
    for i in range(k):
        t = (i + 0.5) / k * 0.5
        a[:, i] = a[:, i] * (1 - t) + a[:, -1 - i] * t
        a[:, -1 - i] = a[:, -1 - i] * (1 - t) + a[:, i] * t
        a[i, :] = a[i, :] * (1 - t) + a[-1 - i, :] * t
        a[-1 - i, :] = a[-1 - i, :] * (1 - t) + a[i, :] * t
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rounded(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def blob(cx, cy, r, rng, n=14, jag=0.18):
    """An irregular round outline (rocks, bushes, stones)."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + rng.uniform(-jag, jag))
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out
