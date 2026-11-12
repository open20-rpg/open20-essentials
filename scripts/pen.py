"""Hand-inked drawing engine for the built-in pack (skia).

The look we're after is a neat hand-inked battle map:
- one confident ink outline per shape, thick on the silhouette, with a slow
  hand wobble and gently varying weight; thinner tapered strokes for detail
- flat fills with a soft watercolor mottle (no grainy noise)
- a crisp cel shade along the side away from the light (top-left) and a thin
  highlight on the side facing it, plus a soft darkening just inside the edge

Sizes are in final pixels (256 px = 1 map tile). The editor shows a tile at
~64 px at 100 % zoom, so outlines must be ~6-8 px here to read as ink there.
Everything renders at S x and is downsampled for clean antialiasing.
"""

import math
import random
from contextlib import contextmanager

import numpy as np
import skia
from PIL import Image

S = 2
INK = (38, 30, 26)

OUTLINE = 7.0  # silhouette
DETAIL = 3.2  # inner lines (plank seams, rims)
FINE = 2.0  # grain, cracks, texture marks
# Joints between bricks, tiles, planks and cobbles: thin and in a darker tone
# of the piece itself (never INK), so a surface reads as one wall or floor
# and not as a pile of loose, individually inked pieces.
JOINT = 1.5
JOINT_ALPHA = 0.75


# -- color ---------------------------------------------------------------------------------


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def shade(c, t=0.25):
    """Darker and a touch warmer/more saturated, like a wash over the color."""
    return mix(c, (int(c[0] * 0.45), int(c[1] * 0.38), int(c[2] * 0.36)), min(1, t * 2.2))


def tint(c, t=0.2):
    return mix(c, (255, 248, 232), t)


def vary(rng, c, amount=0.06):
    k = 1 + rng.uniform(-amount, amount)
    return tuple(max(0, min(255, int(v * k))) for v in c)


def skc(c, a=1.0):
    return skia.Color(c[0], c[1], c[2], int(max(0, min(1, a)) * 255))


# -- geometry ------------------------------------------------------------------------------


SHARP_TURN = math.radians(100)


def turn(a, b, c):
    """How far the line turns at b going a -> b -> c (radians, 0..pi)."""
    u = (b[0] - a[0], b[1] - a[1])
    v = (c[0] - b[0], c[1] - b[1])
    return abs(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))


def resample(pts, closed, step=3.0):
    """Points every `step` along the line. Sharp corners (a blade's point, a
    square corner) are kept as samples: cut by a chord, the ink would run
    inside the shape's own corner and leave its fill poking out."""
    pts = list(pts)
    n = len(pts)
    if closed:
        pts = pts + pts[:1]
    out = [pts[0]]
    carry = 0.0
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            continue
        d = step - carry
        while d <= L:
            t = d / L
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
            d += step
        carry = L - (d - step)
        j = i + 1
        if (closed or j < n - 1) and j < n and turn(pts[i], pts[j], pts[(j + 1) % n]) > SHARP_TURN:
            if out[-1] != (x1, y1):
                out.append((x1, y1))
            carry = 0.0
    if closed:
        out.pop()  # drop the duplicate of the first point
    elif out[-1] != pts[-1]:
        out.append(pts[-1])
    return out


def length(pts, closed):
    q = pts + pts[:1] if closed else pts
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(q, q[1:]))


def round_corners(pts, r, n=5):
    """Replace each corner by a small arc (radius clamped to the edges)."""
    if r <= 0:
        return list(pts)
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % m]
        a = (p0[0] - p1[0], p0[1] - p1[1])
        b = (p2[0] - p1[0], p2[1] - p1[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        if la == 0 or lb == 0:
            continue
        rr = min(r, la / 2.05, lb / 2.05)
        s = (p1[0] + a[0] / la * rr, p1[1] + a[1] / la * rr)
        e = (p1[0] + b[0] / lb * rr, p1[1] + b[1] / lb * rr)
        for k in range(n + 1):
            t = k / n
            # Quadratic bezier s -> p1 -> e.
            x = (1 - t) ** 2 * s[0] + 2 * (1 - t) * t * p1[0] + t * t * e[0]
            y = (1 - t) ** 2 * s[1] + 2 * (1 - t) * t * p1[1] + t * t * e[1]
            out.append((x, y))
    return out


def normals(pts, closed):
    n = len(pts)
    out = []
    for i in range(n):
        if closed:
            a, b = pts[i - 1], pts[(i + 1) % n]
        else:
            a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((-dy / L, dx / L))
    return out


class Wave:
    """Smooth 1-D noise in [-1, 1]: a few sines; periodic over `period` if given."""

    def __init__(self, rng, wavelength=60.0, period=None):
        self.terms = []
        for k, amp in ((1.0, 1.0), (2.3, 0.5), (5.1, 0.25)):
            wl = wavelength / k
            if period:
                f = max(1, round(period / wl)) / period
            else:
                f = 1 / wl
            self.terms.append((2 * math.pi * f, rng.uniform(0, 2 * math.pi), amp))
        self.norm = sum(a for _, _, a in self.terms)

    def __call__(self, s):
        return sum(a * math.sin(w * s + p) for w, p, a in self.terms) / self.norm


def wobble(pts, closed, rng, amp=1.2, wavelength=70.0, step=3.0):
    """A hand-drawn version of the line: resampled, nudged sideways slowly."""
    p = resample(pts, closed, step)
    if len(p) < 3:
        return p
    L = length(p, closed)
    wave = Wave(rng, wavelength, L if closed else None)
    ns = normals(p, closed)
    out = []
    s = 0.0
    for i, ((x, y), (nx, ny)) in enumerate(zip(p, ns)):
        if i:
            s += math.hypot(x - p[i - 1][0], y - p[i - 1][1])
        d = amp * wave(s)
        if not closed:
            # Ends stay where they were drawn to.
            d *= min(1.0, s / 12, (L - s) / 12)
        out.append((x + nx * d, y + ny * d))
    return out


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def ellipse(cx, cy, rx, ry, n=64, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def blob(cx, cy, r, rng, n=10, jag=0.15, ry=None):
    ry = ry or r
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.12, 0.12)
        k = 1 + rng.uniform(-jag, jag)
        out.append((cx + r * k * math.cos(a), cy + ry * k * math.sin(a)))
    return out


def chaikin(pts, closed=True, it=2):
    for _ in range(it):
        out = []
        n = len(pts)
        rng_ = range(n) if closed else range(n - 1)
        if not closed:
            out.append(pts[0])
        for i in rng_:
            a, b = pts[i], pts[(i + 1) % n]
            out.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
            out.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def to_path(pts, closed=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def periodic_noise(w, h, scale, seed, octaves=3):
    """Smooth value noise in 0..1, periodic over (w, h)."""
    rs = np.random.RandomState(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cx = max(2, int(round(w / scale * 2**o)))
        cy = max(2, int(round(h / scale * 2**o)))
        g = rs.rand(cy, cx).astype(np.float32)
        g = np.tile(g, (3, 3))
        im = Image.fromarray(g).resize((w * 3, h * 3), Image.BICUBIC)
        out += np.asarray(im)[h : 2 * h, w : 2 * w] * amp
        tot += amp
        amp *= 0.5
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


# -- canvas --------------------------------------------------------------------------------


class Art:
    """An RGBA drawing. With `tile=True` it's a seamless texture: every shape is
    also drawn shifted by the size, so what crosses an edge comes back on the
    other side."""

    def __init__(self, w, h, seed=1, tile=False, bg=None):
        self.w, self.h = w, h
        self.rng = random.Random(seed)
        self.seed = seed
        self.tile = tile
        self.surface = skia.Surface(w * S, h * S)
        self.c = self.surface.getCanvas()
        self.c.scale(S, S)
        self.c.clear(skc(bg) if bg else skia.ColorTRANSPARENT)
        self.light = (-1.0, -1.0)  # light comes from the top-left

    # -- low level --

    def _copies(self, path):
        if not self.tile:
            return [path]
        b = path.getBounds()
        out = []
        for dx in (-self.w, 0, self.w):
            for dy in (-self.h, 0, self.h):
                if b.right() + dx < -2 or b.left() + dx > self.w + 2:
                    continue
                if b.bottom() + dy < -2 or b.top() + dy > self.h + 2:
                    continue
                q = skia.Path(path)
                q.offset(dx, dy)
                out.append(q)
        return out

    def paint(self, color, alpha=1.0, blur=0.0, mode=None):
        p = skia.Paint(AntiAlias=True, Color=skc(color, alpha))
        if blur > 0:
            p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur * S))
        if mode is not None:
            p.setBlendMode(mode)
        return p

    def fill_path(self, path, color, alpha=1.0, blur=0.0, mode=None):
        paint = self.paint(color, alpha, blur, mode)
        for q in self._copies(path):
            self.c.drawPath(q, paint)

    def stroke_path(self, path, color, width, alpha=1.0, blur=0.0):
        paint = self.paint(color, alpha, blur)
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setStrokeWidth(width)
        paint.setStrokeJoin(skia.Paint.kRound_Join)
        paint.setStrokeCap(skia.Paint.kRound_Cap)
        for q in self._copies(path):
            self.c.drawPath(q, paint)

    @contextmanager
    def clip(self, path):
        self.c.save()
        clip = skia.Path()
        for q in self._copies(path):
            clip = skia.Op(clip, q, skia.kUnion_PathOp) if not clip.isEmpty() else skia.Path(q)
        self.c.clipPath(clip, skia.ClipOp.kIntersect, True)
        try:
            yield
        finally:
            self.c.restore()

    # -- ink --

    def ink(self, pts, width=DETAIL, closed=False, color=INK, alpha=1.0, taper=True, wob=0.8, var=0.18):
        """A pen stroke: wobbly, slightly varying weight, tapered ends if open."""
        p = wobble(pts, closed, self.rng, amp=wob, wavelength=60)
        if len(p) < 2:
            return
        L = length(p, closed)
        wave = Wave(self.rng, 45, L if closed else None)
        ns = normals(p, closed)
        left, right = [], []
        s = 0.0
        tl = min(L * 0.3, width * 4)
        for i, ((x, y), (nx, ny)) in enumerate(zip(p, ns)):
            if i:
                s += math.hypot(x - p[i - 1][0], y - p[i - 1][1])
            w = width * (1 + var * wave(s))
            if not closed and taper and tl > 0:
                t = min(1.0, s / tl, (L - s) / tl)
                w *= 0.25 + 0.75 * (t * t * (3 - 2 * t))
            h = w / 2
            left.append((x + nx * h, y + ny * h))
            right.append((x - nx * h, y - ny * h))
        if closed:
            # The two edges run in opposite directions, so nonzero winding
            # paints the ring and leaves the inside clear. At a sharp corner
            # (a blade's point) the inner edge folds over itself: that fold
            # counts twice, which even-odd would leave unpainted as a pale
            # notch in the ink.
            path = to_path(left)
            path.addPath(to_path(right[::-1]))
            path.setFillType(skia.PathFillType.kWinding)
        else:
            path = to_path(left + right[::-1])
            path.setFillType(skia.PathFillType.kWinding)
        self.fill_path(path, color, alpha)
        if not closed and not taper:
            for x, y in (p[0], p[-1]):
                c = skia.Path()
                c.addCircle(x, y, width / 2)
                self.fill_path(c, color, alpha)

    def shape(
        self,
        pts,
        color,
        outline=OUTLINE,
        corner=4.0,
        wob=1.0,
        depth=None,
        shade_k=0.5,
        light_k=0.35,
        ao=0.35,
        mottle=0.06,
        smooth=False,
        detail=None,
        var=0.14,
        outline_color=None,
        outline_alpha=1.0,
    ):
        """A filled, shaded, ink-outlined shape. `detail(art, path)` draws inside
        it (clipped) before the outline goes on top. Returns the shape's path."""
        q = chaikin(pts, True, 2) if smooth else round_corners(pts, corner)
        q = wobble(q, True, self.rng, amp=wob, wavelength=80)
        path = to_path(q)
        self.fill_path(path, color)
        b = path.getBounds()
        size = min(b.width(), b.height())
        d = depth if depth is not None else max(3.0, min(14.0, size * 0.09))
        with self.clip(path):
            if mottle > 0:
                self.mottle(b, color, mottle)
            if detail:
                detail(self, path)
            lx, ly = self.light
            if shade_k > 0:
                moved = skia.Path(path)
                moved.offset(lx * d, ly * d)
                band = skia.Op(path, moved, skia.kDifference_PathOp)
                self.fill_path(band, shade(color, 0.3), shade_k, blur=0.6)
            if light_k > 0:
                moved = skia.Path(path)
                moved.offset(-lx * d * 0.55, -ly * d * 0.55)
                band = skia.Op(path, moved, skia.kDifference_PathOp)
                self.fill_path(band, tint(color, 0.45), light_k, blur=0.6)
            if ao > 0:
                self.stroke_path(path, shade(color, 0.4), d * 1.6, ao, blur=d * 0.9)
        if outline:
            self.ink(q, outline, closed=True, color=outline_color or INK, alpha=outline_alpha, wob=0.0, var=var)
        return path

    def mottle(self, bounds, color, strength):
        """Soft watercolor unevenness over the clip (periodic in tiles)."""
        if self.tile:
            x0, y0, w, h = 0, 0, self.w, self.h
        else:
            x0, y0 = int(bounds.left()) - 2, int(bounds.top()) - 2
            w, h = int(bounds.width()) + 4, int(bounds.height()) + 4
        if w < 4 or h < 4:
            return
        n = periodic_noise(w, h, max(24, min(w, h) / 3), self.rng.randint(0, 10**6))
        dark = shade(color, 0.3)
        a = np.zeros((h, w, 4), np.uint8)
        a[..., 0], a[..., 1], a[..., 2] = dark[0], dark[1], dark[2]
        a[..., 3] = (np.clip((n - 0.45) * 2, 0, 1) * 255 * strength * 3).astype(np.uint8)
        light = tint(color, 0.3)
        b = np.zeros((h, w, 4), np.uint8)
        b[..., 0], b[..., 1], b[..., 2] = light[0], light[1], light[2]
        b[..., 3] = (np.clip((0.4 - n) * 2, 0, 1) * 255 * strength * 3).astype(np.uint8)
        for arr in (a, b):
            img = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
            if self.tile:
                for dx in (-w, 0, w):
                    for dy in (-h, 0, h):
                        self.c.drawImageRect(img, skia.Rect.MakeXYWH(x0 + dx, y0 + dy, w, h))
            else:
                self.c.drawImageRect(img, skia.Rect.MakeXYWH(x0, y0, w, h))

    def hatch(self, region, angle=0.8, spacing=7.0, width=FINE, color=INK, alpha=0.55, length_=(10, 22)):
        """Short parallel pen strokes over `region` (a path), e.g. in shadows."""
        b = region.getBounds()
        dx, dy = math.cos(angle), math.sin(angle)
        nx, ny = -dy, dx
        cx, cy = b.centerX(), b.centerY()
        R = math.hypot(b.width(), b.height()) / 2 + 10
        with self.clip(region):
            k = -R
            while k < R:
                t = -R
                while t < R:
                    L = self.rng.uniform(*length_)
                    x, y = cx + nx * k + dx * t, cy + ny * k + dy * t
                    if region.contains(x + dx * L / 2, y + dy * L / 2):
                        self.ink([(x, y), (x + dx * L, y + dy * L)], width, color=color, alpha=alpha, wob=0.3)
                    t += L + self.rng.uniform(3, 9)
                k += spacing * self.rng.uniform(0.85, 1.15)

    # -- output --

    def image(self, grain=0.035, scale=1):
        """The drawing, `scale` times its size in pixels (up to S: the
        supersampled canvas, so a larger scale is just as sharp)."""
        arr = self.surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
        img = Image.fromarray(arr, "RGBA")
        if scale != S:
            img = img.resize((round(self.w * scale), round(self.h * scale)), Image.LANCZOS)
        img = pastel(img)
        return add_grain(img, grain, self.seed) if grain > 0 else img


def pastel(img, desat=0.12, lift=0.06):
    """Nudge every color a little toward pastel: slightly less saturated and a
    touch lighter (the darkest inks barely move)."""
    a = np.asarray(img).astype(np.float32)
    rgb_ = a[..., :3]
    lum = (rgb_ @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    rgb_ = rgb_ + (lum - rgb_) * desat
    k = lift * np.clip(lum / 255 * 1.6, 0, 1)
    rgb_ = rgb_ + (np.array([255, 251, 244], np.float32) - rgb_) * k
    a[..., :3] = rgb_
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def add_grain(img, amount, seed):
    """A very light paper/pigment grain. Per-pixel noise exactly the image's
    size, softened with a wrapping blur, so a tile still repeats seamlessly."""
    rs = np.random.RandomState(seed + 7)
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    n = rs.normal(0, 1, (h, w)).astype(np.float32)
    n = (n * 2 + np.roll(n, 1, 0) + np.roll(n, -1, 0) + np.roll(n, 1, 1) + np.roll(n, -1, 1)) / 4.5
    a[..., :3] *= 1 + n[..., None] * amount
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def joint_color(c):
    """Line colour for the joints of a masonry/plank surface made of `c`."""
    return shade(c, 0.5)


def grout(c, mortar=None, t=0.35):
    """Background between pieces: close to the pieces' own tone (a light
    mortar pulls it lighter), so gaps read as joints, not dark trenches."""
    return mix(shade(c, 0.22), mortar, t) if mortar else shade(c, 0.28)
