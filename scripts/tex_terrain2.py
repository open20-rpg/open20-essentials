"""More terrains for the built-in pack (seamless 512x512, alpha = height):
grass, dirt, sand, stone, snow, ice, swamp, forest, volcanic and fantasy
grounds. Same look and helpers as tex_ground.TERRAINS, plus a few extra
detail kinds (needles, clover, footprints, furrows, shards, crystals,
dried-mud cells, dunes)."""

import math

import numpy as np
from PIL import Image

from floors import crack, voronoi_cells
from pen import FINE, Art, blob, chaikin, periodic_noise, rgb, shade, tint, to_path, vary
from tex_ground import S2, dot, with_height


def _strokes(a, s, n, col, ln, w, spread=0.5, up=True, alpha=0.75):
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = (-math.pi / 2 if up else a.rng.uniform(0, 6.28)) + a.rng.uniform(-spread, spread)
        L = a.rng.uniform(*ln)
        a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], w, color=rgb(col), alpha=alpha, wob=0.1, var=0.1)


def _leaves(a, s, n, cols, size=(12, 20)):
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        L = a.rng.uniform(*size)
        W = L * a.rng.uniform(0.35, 0.45)
        ux, uy = math.cos(t), math.sin(t)
        pts = [(x - ux * L / 2, y - uy * L / 2), (x - uy * W / 2, y + ux * W / 2), (x + ux * L / 2, y + uy * L / 2), (x + uy * W / 2, y - ux * W / 2)]
        a.shape(chaikin(pts, True, 1), vary(a.rng, rgb(a.rng.choice(cols)), 0.06), outline=1.6, corner=0, wob=0.1, depth=1, shade_k=0.3, light_k=0.3, ao=0, mottle=0)


def _stones(a, s, n, cols, rr, outline=1.6):
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        a.shape(blob(x, y, a.rng.uniform(*rr), a.rng, 8, 0.25), vary(a.rng, rgb(a.rng.choice(cols)), 0.06), outline=outline, corner=0, wob=0.3, depth=2, shade_k=0.45, light_k=0.45, ao=0, mottle=0)


def _shards(a, s, n, cols, rr):
    """Angular flat stone shards (slate, obsidian)."""
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        r = a.rng.uniform(*rr)
        k = a.rng.randint(3, 5)
        t0 = a.rng.uniform(0, 6.28)
        pts = [(x + r * a.rng.uniform(0.6, 1.1) * math.cos(t0 + 2 * math.pi * i / k), y + r * a.rng.uniform(0.6, 1.1) * math.sin(t0 + 2 * math.pi * i / k)) for i in range(k)]
        a.shape(pts, vary(a.rng, rgb(a.rng.choice(cols)), 0.08), outline=2.0, corner=1, wob=0.1, depth=2, shade_k=0.4, light_k=0.5, ao=0, mottle=0)


def _crystals(a, s, n, cols, rr):
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        r = a.rng.uniform(*rr)
        t0 = a.rng.uniform(0, 6.28)
        pts = [(x + r * math.cos(t0 + k * math.pi / 3), y + r * math.sin(t0 + k * math.pi / 3)) for k in range(6)]
        col = rgb(a.rng.choice(cols))
        a.shape(pts, col, outline=1.3, corner=0, wob=0, depth=1.5, shade_k=0.45, light_k=0.6, ao=0, mottle=0)
        for k in range(0, 6, 2):
            a.ink([pts[k], (x, y)], FINE * 0.7, color=shade(col, 0.4), alpha=0.6, wob=0)


def _flowers(a, s, n, cols, r=2.6):
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        c = rgb(a.rng.choice(cols))
        for k in range(5):
            t = 2 * math.pi * k / 5
            dot(a, x + r * 1.3 * math.cos(t), y + r * 1.3 * math.sin(t), r, c, 0.95)
        dot(a, x, y, r * 0.6, rgb("#e6b84a"))


def _clover(a, s, n, col):
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        r0 = a.rng.uniform(0, 6.28)
        for k in range(3):
            t = r0 + 2 * math.pi * k / 3
            dot(a, x + 3.6 * math.cos(t), y + 3.6 * math.sin(t), 3.4, rgb(col), 0.9)


def _needles(a, s, n, cols):
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        L = a.rng.uniform(8, 16)
        a.ink([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], 2.0, color=rgb(a.rng.choice(cols)), alpha=0.9, wob=0, var=0.1)


def _footprints(a, s, n, col, boot=True):
    """A few trails of footprints crossing the tile."""
    for _ in range(n):
        x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
        t = a.rng.uniform(0, 6.28)
        ux, uy = math.cos(t), math.sin(t)
        for k in range(8):
            side = 1 if k % 2 else -1
            px, py = x + ux * k * 26 - uy * side * 7, y + uy * k * 26 + ux * side * 7
            pts = [(px + ux * dx - uy * dy, py + uy * dx + ux * dy) for dx, dy in [(-7, -3.5), (6, -4.5), (8, 0), (6, 4.5), (-7, 3.5)]] if boot else [(px + ux * dx - uy * dy, py + uy * dx + ux * dy) for dx, dy in [(-4, -3), (4, -3), (5, 0), (4, 3), (-4, 3)]]
            a.fill_path(to_path(chaikin(pts, True, 1)), rgb(col), 0.45)


def _furrows(a, s, n, col, light):
    """Ploughed rows across the tile (periodic: n rows over s)."""
    for r in range(n):
        y = (r + 0.5) * s / n
        pts = [(x, y + 2 * math.sin(2 * math.pi * x / s * 2 + r)) for x in np.linspace(-20, s + 20, 30)]
        a.ink(pts, s / n * 0.32, color=rgb(col), alpha=0.55, wob=0.2, taper=False)
        a.ink([(x, py - s / n * 0.22) for x, py in pts], 2.0, color=rgb(light), alpha=0.5, wob=0.2, taper=False)


def _dried_cells(a, s, col, n=6):
    """Dry, cracked earth: polygon cells with dark gaps."""
    for (_, _), poly in voronoi_cells(s, s, n, n, a.rng, 0.35):
        a.ink(poly, 2.2, closed=True, color=rgb(col), alpha=0.7, wob=0.3)


def _ripples(a, s, col, n, amp=5, k=3, width=1.2, alpha=0.6):
    for r in range(n):
        y = r * s / n + a.rng.uniform(-6, 6)
        pts = [(x, y + amp * math.sin(2 * math.pi * x / s * k + r)) for x in np.linspace(-20, s + 20, 40)]
        a.ink(pts, FINE * width, color=rgb(col), alpha=alpha, wob=0.3, taper=False)


def ground(seed, base, blotch=(), extras=(), scale=72, lo=0.5, tint_k=0.06, nblotch=36, blotch_r=(22, 60)):
    """A seamless terrain: flat base, soft blotches, then `extras`: a list
    of (fn, args) detail passes, each called as fn(art, size, *args)."""
    s = S2
    a = Art(s, s, seed, tile=True, bg=rgb(base))
    if blotch:
        for _ in range(nblotch):
            x, y = a.rng.uniform(0, s), a.rng.uniform(0, s)
            a.fill_path(to_path(blob(x, y, a.rng.uniform(*blotch_r), a.rng, 12, 0.3)), rgb(a.rng.choice(blotch)), 0.22, blur=6)
    for fn, *args in extras:
        fn(a, s, *args)
    img = a.image()
    field = periodic_noise(s, s, scale, seed + 3)
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= 1 - tint_k / 2 + field[..., None] * tint_k
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    return with_height(img, field, lo)


def _dots(a, s, n, col, rr, alpha=0.6):
    for _ in range(n):
        dot(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(*rr), rgb(col), alpha)


def _cracks(a, s, n, alpha=0.6):
    for _ in range(n):
        crack(a, a.rng.uniform(0, s), a.rng.uniform(0, s), a.rng.uniform(0, 6.28), a.rng.uniform(40, 90), FINE * 1.1, alpha)


def _grass(seed, base, blot, dark, light, n=1300, ln=(6, 12), extra=(), lo=0.6):
    return ground(seed, base, blot, [(_strokes, n, dark, ln, 2.2), (_strokes, n // 3, light, (ln[0] - 1, ln[1] - 2), 1.9)] + list(extra), lo=lo)


G_BLOT = ("#6f9a48", "#86ad5d")

TERRAINS2 = {
    # -- grass -------------------------------------------------------------------------------
    "Spring Grass": lambda: _grass(501, "#86b05a", ("#7aa64e", "#94bc66"), "#55803a", "#b4d488"),
    "Summer Grass": lambda: _grass(502, "#7a9e48", ("#6e9240", "#86aa54"), "#4a6e2c", "#a8c470"),
    "Deep Green Grass": lambda: _grass(503, "#4f7e3a", ("#467434", "#5a8a42"), "#2e5222", "#76a058"),
    "Blue-Green Grass": lambda: _grass(504, "#5e9268", ("#548860", "#6a9e72"), "#3a6644", "#8cbc90"),
    "Olive Grass": lambda: _grass(505, "#8a9a4e", ("#7e8e46", "#96a65a"), "#5e6e30", "#b4be78"),
    "Short Grass": lambda: _grass(506, "#7aa152", G_BLOT, "#4d7232", "#a9c77c", n=1400, ln=(3, 6)),
    "Long Grass": lambda: _grass(507, "#729a4c", G_BLOT, "#466a2e", "#9cc070", n=700, ln=(10, 18)),
    "Mowed Lawn": lambda: ground(508, "#7aa654", (), [(_ripples, "#6a9648", 8, 0, 1, 18, 0.35), (_strokes, 600, "#5a8640", (3, 5), 1.3)], lo=0.65),
    "Trampled Grass": lambda: _grass(509, "#8a9e58", ("#a08a5e", "#7e9650"), "#5a6e3a", "#b0bc80", n=500, extra=[(_strokes, 200, "#8a7a52", (8, 14), 1.4, 1.2, False)]),
    "Clover Field": lambda: _grass(510, "#6e9a4a", G_BLOT, "#4d7232", "#a9c77c", n=500, extra=[(_clover, 260, "#5e9442")]),
    "Clover with Flowers": lambda: _grass(511, "#6e9a4a", G_BLOT, "#4d7232", "#a9c77c", n=400, extra=[(_clover, 200, "#5e9442"), (_flowers, 60, ("#f3eee2", "#e8a8c8"), 2.2)]),
    "Daisy Meadow": lambda: _grass(512, "#7aa152", G_BLOT, "#4d7232", "#a9c77c", n=600, extra=[(_flowers, 160, ("#f6f2e8",), 2.6)]),
    "Poppy Meadow": lambda: _grass(513, "#7aa152", G_BLOT, "#4d7232", "#a9c77c", n=600, extra=[(_flowers, 140, ("#c8443a", "#d85a3e"), 2.8)]),
    "Bluebell Meadow": lambda: _grass(514, "#6e9a4a", G_BLOT, "#4d7232", "#a9c77c", n=600, extra=[(_flowers, 150, ("#6f8fd0", "#8a7ad0"), 2.4)]),
    "Buttercup Meadow": lambda: _grass(515, "#7aa152", G_BLOT, "#4d7232", "#a9c77c", n=600, extra=[(_flowers, 150, ("#f0c838", "#e6b84a"), 2.4)]),
    "Lavender Field": lambda: ground(516, "#7a8e5a", ("#6e8250",), [(_furrows, 8, "#5e6e40", "#94a670"), (_flowers, 260, ("#9a7ac8", "#8a6ab8", "#b294d8"), 2.2)], lo=0.6),
    "Wildflower Meadow": lambda: _grass(517, "#7aa152", G_BLOT, "#4d7232", "#a9c77c", n=500, extra=[(_flowers, 180, ("#f3eee2", "#e6b84a", "#c86ab8", "#c8443a", "#6f8fd0"), 2.4)]),
    "Weedy Grass": lambda: _grass(518, "#86a058", ("#7a9450", "#94ac62"), "#566e36", "#b0c47c", extra=[(_leaves, 60, ("#5e8a3e", "#6e9a4a"), (10, 16))]),
    "Savanna Grass": lambda: _grass(519, "#c4b062", ("#b8a456", "#d0bc70"), "#8e7c3a", "#e0d08e", n=700, ln=(8, 16), lo=0.55),
    "Tundra": lambda: ground(520, "#8e9278", ("#848870", "#9a9c84", "#a8a490"), [(_dots, 900, "#6e7460", (0.6, 1.6)), (_stones, 30, ("#9e9a90", "#8a867c"), (5, 10)), (_strokes, 200, "#6a7458", (4, 7), 1.2)], lo=0.55),
    "Frosted Grass": lambda: _grass(521, "#9ab4a0", ("#a8c0ae", "#8ea898"), "#6e8a78", "#e6eef0", extra=[(_dots, 400, "#f0f4f6", (0.6, 1.4), 0.8)]),
    "Dead Grass": lambda: _grass(522, "#a89a6e", ("#9e8e64", "#b4a87a"), "#7a6c48", "#cabe92", n=700, ln=(6, 12), lo=0.55),
    "Burnt Grass": lambda: _grass(523, "#5a5244", ("#4e463a", "#6a6050", "#3e3a34"), "#2e2a24", "#7a705c", n=600, extra=[(_dots, 300, "#1e1a18", (0.6, 1.6))], lo=0.5),
    "Fey Grass": lambda: _grass(524, "#5ea08a", ("#549680", "#6aac96"), "#3a7462", "#a0e0c8", extra=[(_flowers, 80, ("#e8a8f0", "#a8d8f8"), 2.0)]),
    # -- dirt & mud ---------------------------------------------------------------------------
    "Dark Soil": lambda: ground(531, "#5e4a38", ("#544232", "#6a5440"), [(_dots, 700, "#3a2c22", (0.6, 1.6)), (_stones, 30, ("#7a6a5a",), (2.5, 4.5))]),
    "Red Earth": lambda: ground(532, "#a8583a", ("#9a4e34", "#b46444"), [(_dots, 600, "#7a3a26", (0.5, 1.3)), (_stones, 40, ("#b87a5e", "#9a6a52"), (3, 6))]),
    "Yellow Earth": lambda: ground(533, "#c4a060", ("#b89456", "#d0ac6c"), [(_dots, 600, "#8a6e3e", (0.5, 1.2)), (_stones, 40, ("#c8b088",), (3, 5))]),
    "Cracked Earth": lambda: ground(534, "#b89a6e", ("#ae9064", "#c2a478"), [(_dried_cells, "#7a6040", 6), (_dots, 300, "#8a704c", (0.5, 1.1))], lo=0.5),
    "Dried Mud": lambda: ground(535, "#8e7656", ("#846c4e", "#98805e"), [(_dried_cells, "#5a4632", 8)], lo=0.5),
    "Ploughed Field": lambda: ground(536, "#7a5e44", ("#70563e",), [(_furrows, 10, "#4e3a2a", "#9a7e5e")], lo=0.5, scale=96),
    "Sown Field": lambda: ground(537, "#7a5e44", ("#70563e",), [(_furrows, 10, "#4e3a2a", "#9a7e5e"), (_dots, 260, "#6e9a4a", (1.2, 2.2), 0.9)], lo=0.55, scale=96),
    "Muddy Tracks": lambda: ground(538, "#7a6248", ("#6e5640", "#86704e"), [(_ripples, "#4e3a2a", 6, 4, 2, 2.4, 0.55), (_footprints, 3, "#4e3a2a")], lo=0.5),
    "Wet Mud": lambda: ground(539, "#5e4a38", ("#544232", "#6a5440", "#4a5a5e"), [(_ripples, "#3e2e22", 10), (_dots, 140, "#9ab0b8", (1.2, 3), 0.5)], lo=0.5),
    "Footprint Dirt": lambda: ground(540, "#a17d55", ("#94704b", "#ad8a60"), [(_footprints, 4, "#6e5236"), (_dots, 400, "#6e5236", (0.5, 1.2))]),
    "Cave Dirt": lambda: ground(541, "#6e665c", ("#645c52", "#7a7266"), [(_dots, 800, "#4a443c", (0.6, 1.6)), (_stones, 50, ("#857e74", "#6e675e"), (3, 7))], lo=0.5),
    "Packed Earth": lambda: ground(542, "#9a8264", ("#907a5e", "#a48c6c"), [(_dots, 300, "#6e5a44", (0.5, 1.1)), (_cracks, 6, 0.4)], lo=0.55),
    "Peat": lambda: ground(543, "#4a3a2e", ("#423428", "#544234"), [(_strokes, 300, "#2e241c", (6, 12), 1.3, 1.5, False), (_dots, 200, "#6a5a3e", (0.8, 1.6))], lo=0.5),
    "Clay Pit": lambda: ground(544, "#c48a64", ("#b87e5a", "#d0966e"), [(_ripples, "#9a6a4a", 9, 4, 2), (_cracks, 10, 0.5)], lo=0.5),
    # -- sand ---------------------------------------------------------------------------------
    "White Beach Sand": lambda: ground(551, "#efe6cc", ("#e6dcc0", "#f6eed8"), [(_ripples, "#d0c4a0", 12, 4, 3, 1.0, 0.5), (_dots, 500, "#c8b890", (0.4, 0.9))], scale=96, lo=0.5, tint_k=0.05),
    "Desert Dunes": lambda: ground(552, "#ddbb7e", ("#d2b074", "#e6c68a"), [(_ripples, "#b8925a", 10, 14, 2, 1.6, 0.55), (_ripples, "#f0d8a0", 10, 14, 2, 1.0, 0.4)], scale=110, lo=0.5),
    "Red Sand": lambda: ground(553, "#c8784e", ("#bc6e46", "#d4845a"), [(_ripples, "#9a5636", 12, 5, 3), (_dots, 500, "#9a5636", (0.4, 0.9))], scale=96, lo=0.5),
    "Wet Sand": lambda: ground(554, "#b8a274", ("#ac966a", "#c4ae80", "#a4a07a"), [(_ripples, "#8e7a50", 14, 3, 4, 1.1), (_dots, 120, "#e6ecec", (1, 2.4), 0.5)], scale=96, lo=0.5),
    "Black Sand": lambda: ground(555, "#4a4644", ("#423e3c", "#56524e"), [(_ripples, "#2e2a28", 12, 4, 3), (_dots, 600, "#7a7470", (0.4, 1.0))], scale=96, lo=0.5),
    "Shell Sand": lambda: ground(556, "#e6d6b0", ("#dccca6", "#eedebc"), [(_dots, 400, "#c4b088", (0.4, 0.9)), (_stones, 70, ("#f4ece0", "#e8c8b8", "#d8d0c4"), (2.5, 5))], scale=96, lo=0.5),
    "Coral Sand": lambda: ground(557, "#f0d6c4", ("#e8ccb8", "#f6e0d0"), [(_dots, 500, "#d8a890", (0.4, 1.0)), (_stones, 60, ("#e88a7a", "#f4c4b4", "#f8ece0"), (2.5, 5))], scale=96, lo=0.5),
    "Salt Flats": lambda: ground(558, "#ecebe4", ("#e2e0d8", "#f4f4ee"), [(_dried_cells, "#c4c0b4", 5), (_dots, 200, "#cfcac0", (0.5, 1))], scale=110, lo=0.55, tint_k=0.04),
    "Sandy Grass": lambda: ground(559, "#cdb784", ("#c2ac7a", "#bfc080"), [(_strokes, 300, "#7a8a46", (5, 10), 1.4), (_dots, 400, "#a89060", (0.4, 0.9))], lo=0.55),
    # -- gravel, pebbles, stone ---------------------------------------------------------------
    "Fine Gravel": lambda: ground(571, "#9a958c", (), [(_stones, 600, ("#aaa59c", "#888379", "#b6b0a6"), (2.5, 5), 1.2)], scale=40, lo=0.55),
    "Coarse Gravel": lambda: ground(572, "#857f76", (), [(_stones, 180, ("#a39d93", "#7c7770", "#948e85"), (7, 13))], scale=40, lo=0.55),
    "Red Gravel": lambda: ground(573, "#8e6a58", (), [(_stones, 280, ("#a87a64", "#8a5e4e", "#b48a72"), (4, 9))], scale=40, lo=0.55),
    "River Pebbles Ground": lambda: ground(574, "#8a8478", ("#807a6e",), [(_stones, 160, ("#a8a49a", "#8f948f", "#b8ad9a", "#7f857f"), (7, 14))], lo=0.55),
    "White Pebbles": lambda: ground(575, "#cfc8bc", (), [(_stones, 220, ("#ece8e0", "#d8d2c6", "#f4f0e8"), (5, 10))], lo=0.55),
    "Granite Ground": lambda: ground(576, "#9e968e", ("#948c84", "#a8a098"), [(_stones, 30, ("#b0a8a0", "#8e8680"), (14, 28)), (_dots, 900, "#5e5650", (0.5, 1.2)), (_dots, 400, "#d8c8c0", (0.5, 1.1))], lo=0.5),
    "Basalt Ground": lambda: ground(577, "#3e4044", ("#36383c", "#46484c"), [(_shards, 50, ("#4c4e54", "#36383c"), (12, 24)), (_dots, 300, "#22242a", (0.6, 1.4))], lo=0.5),
    "Sandstone Ground": lambda: ground(578, "#c8a676", ("#bc9a6c", "#d2b080"), [(_stones, 34, ("#d8b888", "#b4925e"), (14, 26)), (_ripples, "#a88a5c", 8, 3, 2, 1, 0.4)], lo=0.5),
    "Slate Shards": lambda: ground(579, "#5c626a", ("#545a62",), [(_shards, 120, ("#6a7078", "#4e545c", "#767c84"), (10, 22))], lo=0.5),
    "Limestone Ground": lambda: ground(580, "#d6d0c2", ("#ccc6b8", "#e0dacc"), [(_stones, 40, ("#e4dfd2", "#c2bcae"), (10, 22)), (_dots, 300, "#a8a294", (0.5, 1.1)), (_cracks, 8, 0.4)], lo=0.5),
    "Rubble Ground": lambda: ground(581, "#7e7870", ("#746e66",), [(_shards, 70, ("#9a948a", "#857f77", "#a8a296"), (8, 18)), (_stones, 60, ("#8e887e",), (3, 6))], lo=0.5),
    "Mossy Stones Ground": lambda: ground(582, "#6e7c58", ("#647250", "#7a8862"), [(_stones, 60, ("#9a968c", "#86827a"), (10, 18)), (_dots, 1000, "#5a7a36", (0.8, 2))], lo=0.55),
    "Cobble Rubble": lambda: ground(583, "#6e6860", (), [(_stones, 120, ("#a39d93", "#8e887e", "#b0aa9e"), (10, 18), 2.0), (_shards, 20, ("#7e786e",), (6, 12))], lo=0.5),
    # -- snow & ice ---------------------------------------------------------------------------
    "Fresh Snow": lambda: ground(591, "#f4f6f8", ("#eaeff4", "#fafbfc"), [(_dots, 150, "#d4dde6", (0.5, 1.2))], scale=120, lo=0.6, tint_k=0.03),
    "Snow with Footprints": lambda: ground(592, "#eef1f4", ("#e2e8ee", "#f6f8fa"), [(_footprints, 4, "#b8c6d4"), (_dots, 150, "#c0ccd8", (0.6, 1.4))], scale=110, lo=0.55, tint_k=0.04),
    "Snowy Grass": lambda: ground(593, "#e6ecee", ("#dce4e6", "#c8d6c4"), [(_strokes, 300, "#6e8a5e", (4, 8), 1.3), (_dots, 200, "#c4d0d8", (0.6, 1.2))], scale=96, lo=0.55, tint_k=0.04),
    "Icy Snow": lambda: ground(594, "#dfe9f0", ("#d2e0ea", "#ecf2f6", "#c4d8e6"), [(_ripples, "#b4c8d8", 7, 6, 2, 1.0, 0.5), (_cracks, 6, 0.35)], scale=110, lo=0.55, tint_k=0.04),
    "Slush": lambda: ground(595, "#c8ccc8", ("#b8bcb6", "#d8dcd8", "#a8a294"), [(_ripples, "#8e928c", 8, 4, 3, 1.4), (_dots, 300, "#8a8478", (0.6, 1.6))], lo=0.5),
    "Dirty Snow": lambda: ground(596, "#dcdcd6", ("#cfcfc6", "#e6e6e0", "#b8b0a2"), [(_dots, 500, "#8a8274", (0.5, 1.3)), (_footprints, 2, "#a8a294")], lo=0.55),
    "Cracked Ice": lambda: ground(597, "#b4d4e2", ("#a4c8d8", "#c4dee8"), [(_dried_cells, "#7ea8bc", 4), (_cracks, 14, 0.5)], lo=0.5, tint_k=0.05),
    "Blue Ice": lambda: ground(598, "#8ec0dc", ("#80b4d2", "#9ccae2"), [(_strokes, 120, "#c8e6f2", (16, 40), 1.6, 0.3, False, 0.6), (_cracks, 10, 0.4)], lo=0.5, tint_k=0.05),
    "Frost": lambda: ground(599, "#cde0e8", ("#c0d6e0", "#dae8ee"), [(_strokes, 500, "#f2f8fa", (4, 9), 1.1, 3.0, False, 0.8)], lo=0.55, tint_k=0.04),
    "Permafrost": lambda: ground(600, "#9aa0a0", ("#8e9494", "#c4d0d4"), [(_dried_cells, "#6e7676", 6), (_dots, 300, "#e6eef0", (0.6, 1.4), 0.7)], lo=0.5),
    # -- swamp, moss, forest ------------------------------------------------------------------
    "Bog": lambda: ground(611, "#4e5a3a", ("#445032", "#58643e", "#3e4a40"), [(_ripples, "#36402a", 8, 4, 3), (_dots, 300, "#6e7e4a", (1, 2.4)), (_strokes, 150, "#3a4a26", (6, 12), 1.4)], lo=0.5),
    "Marsh": lambda: ground(612, "#5e6e46", ("#546440", "#6a7a4e", "#4a5e5a"), [(_strokes, 500, "#3e5228", (8, 16), 1.5), (_dots, 120, "#7a9ab0", (2, 4), 0.5)], lo=0.55),
    "Swamp Muck": lambda: ground(613, "#4a4a36", ("#40402e", "#56563e"), [(_ripples, "#2e2e20", 10), (_dots, 200, "#7a8a3e", (1.2, 3), 0.7)], lo=0.5),
    "Thick Moss": lambda: ground(614, "#5e8a3a", ("#547e34", "#6a9642", "#4a7230"), [(_dots, 2400, "#3e6426", (0.8, 2.2)), (_dots, 800, "#86b05a", (0.6, 1.6))], lo=0.6),
    "Dry Moss": lambda: ground(615, "#8a8a52", ("#808048", "#94945c"), [(_dots, 1800, "#6a6a3a", (0.8, 2))], lo=0.55),
    "Lichen Rock": lambda: ground(616, "#8e8a82", ("#86827a",), [(_stones, 30, ("#9e9a90",), (14, 28)), (_dots, 400, "#c8c070", (1, 3), 0.7), (_dots, 300, "#9ab878", (1, 2.4), 0.7)], lo=0.5),
    "Pine Needles": lambda: ground(617, "#7a5e40", ("#6e5438", "#86684a"), [(_needles, 2600, ("#a8784a", "#8a6038", "#b88a58", "#6e4e30"))], lo=0.55),
    "Oak Leaves": lambda: ground(618, "#6e5a3e", ("#645036",), [(_leaves, 900, ("#a8783a", "#8a6a3a", "#b88a48", "#7a5a30"), (18, 28))], lo=0.55),
    "Red Leaves": lambda: ground(619, "#6e4a38", ("#644232",), [(_leaves, 900, ("#b8443a", "#c8603e", "#9a3a2e", "#d8783a"), (16, 26))], lo=0.55),
    "Yellow Leaves": lambda: ground(620, "#7a6a40", ("#706038",), [(_leaves, 900, ("#e0b84a", "#d4a43a", "#c8963a", "#e8c860"), (16, 26))], lo=0.55),
    "Green Leaves": lambda: ground(621, "#4e6a3a", ("#466234",), [(_leaves, 900, ("#6e9a4a", "#5a8a3e", "#86b05a", "#4a7a30"), (16, 26))], lo=0.55),
    "Twig Litter": lambda: ground(622, "#6e5a40", ("#645038", "#7a6448"), [(_strokes, 160, "#4a3624", (14, 30), 2.2, 3.2, False, 0.85), (_leaves, 120, ("#8a6a40", "#a8783a"), (10, 16))], lo=0.55),
    "Mushroom Floor": lambda: ground(623, "#5e5440", ("#54483a", "#6a5e48"), [(_dots, 500, "#3e3628", (0.6, 1.6)), (_stones, 50, ("#c84a3e", "#e6d6b0", "#a8845a"), (3, 6), 1.2)], lo=0.55),
    "Fungal Mat": lambda: ground(624, "#7a6a8a", ("#6e5e80", "#86769a", "#5e6a7a"), [(_dots, 1200, "#a898c0", (0.8, 2.2), 0.7), (_dots, 200, "#d8f0e0", (1, 2), 0.7)], lo=0.55),
    "Roots": lambda: ground(625, "#6a5440", ("#604a38",), [(_strokes, 60, "#4a3424", (40, 90), 4.0, 3.2, False, 0.85), (_dots, 300, "#4a3a2a", (0.6, 1.4))], lo=0.5),
    "Jungle Floor": lambda: ground(626, "#4a5e36", ("#40542e", "#566a3e"), [(_leaves, 200, ("#5a8a3e", "#4a7a30", "#6e9a4a"), (20, 34)), (_dots, 300, "#2e3a20", (0.8, 1.8))], lo=0.55),
    # -- volcanic & fantasy --------------------------------------------------------------------
    "Volcanic Ash": lambda: ground(631, "#5a5654", ("#4e4a48", "#666260"), [(_ripples, "#3a3634", 8, 4, 2, 1.2), (_dots, 800, "#2e2a28", (0.6, 1.6))], lo=0.5),
    "Cooled Lava": lambda: ground(632, "#2e2a2a", ("#262222", "#383232"), [(_dried_cells, "#141010", 5), (_ripples, "#4a4040", 6, 6, 3, 1.4, 0.4)], lo=0.5),
    "Glowing Lava Crust": lambda: ground(633, "#2a2220", ("#221a18", "#342a26"), [(_dried_cells, "#e9773a", 5), (_dots, 120, "#f6b444", (1, 2.2), 0.9)], lo=0.5),
    "Obsidian Field": lambda: ground(634, "#1e1c22", ("#18161c", "#26242a"), [(_shards, 80, ("#2e2c34", "#3c3a44", "#1a181e"), (10, 22))], lo=0.5),
    "Sulfur Ground": lambda: ground(635, "#b8a858", ("#ac9c4e", "#c4b466", "#8a8a7a"), [(_dots, 600, "#e8d860", (0.8, 2), 0.8), (_cracks, 10, 0.5)], lo=0.5),
    "Scorched Earth": lambda: ground(636, "#3e3630", ("#342e2a", "#4a403a", "#5a4a3a"), [(_dots, 700, "#1e1a18", (0.6, 1.8)), (_cracks, 14, 0.5)], lo=0.5),
    "Crystal Ground": lambda: ground(637, "#6e6a7e", ("#646074", "#787488"), [(_crystals, 70, ("#a888d8", "#8aa8e8", "#c0a8f0"), (5, 11)), (_dots, 400, "#4a4658", (0.6, 1.4))], lo=0.5),
    "Amethyst Bed": lambda: ground(638, "#4e3e62", ("#46385a", "#58486c"), [(_crystals, 120, ("#9a6ad0", "#b48ae0", "#7a4ab0"), (6, 13))], lo=0.5),
    "Emerald Ground": lambda: ground(639, "#3e5a4a", ("#365242", "#466452"), [(_crystals, 60, ("#4ec88a", "#6ad8a0", "#3aa070"), (5, 11)), (_dots, 400, "#2a3e32", (0.6, 1.4))], lo=0.5),
    "Shadow Ground": lambda: ground(640, "#2e2a36", ("#26222e", "#36323e"), [(_strokes, 200, "#4a4258", (10, 24), 1.4, 3.2, False, 0.6), (_dots, 300, "#5a5070", (0.8, 1.6), 0.6)], lo=0.5),
    "Bone Dust": lambda: ground(641, "#d6ccb4", ("#ccc2aa", "#e0d6be"), [(_strokes, 120, "#f0e8d6", (8, 18), 3.0, 3.2, False, 0.85), (_dots, 400, "#a89c80", (0.5, 1.2))], lo=0.5),
    "Bloodied Ground": lambda: ground(642, "#7a6248", ("#6e5640", "#86704e"), [(_dots, 300, "#6e5236", (0.5, 1.2)), (_stones, 26, ("#7a2420", "#8a2e26"), (8, 18), 0.8)], lo=0.5),
    "Riverbank": lambda: ground(644, "#7a7258", ("#706850", "#6a7a5a", "#8a8466"), [(_stones, 50, ("#a8a49a", "#8f948f"), (6, 12)), (_strokes, 300, "#4e6a36", (6, 12), 1.8), (_ripples, "#5a5440", 5, 4, 2, 1.2, 0.4)], lo=0.55),
    "Ancient Mosaic Ruins": lambda: ground(643, "#9a9284", ("#908878",), [(_shards, 90, ("#c4783e", "#4a7a9a", "#d8cfb8", "#8a5a3a"), (6, 12)), (_dots, 400, "#6a6458", (0.5, 1.2)), (_strokes, 120, "#6e8a4a", (4, 8), 1.2)], lo=0.5),
}
