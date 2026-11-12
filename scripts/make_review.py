"""Renders every asset in catalog.py into thumbnail atlases plus a JSON index
for the review page.

    python3 scripts/builtin-pack/make_review.py <outdir>

Writes <outdir>/atlas-N.webp (CELL px cells, COLS x ROWS each) and
<outdir>/assets.json: [{section, kind, items: [{id, name, atlas, x, y,
colorable, w, h}]}]."""

import json
import os
import sys
import traceback

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import catalog  # noqa: E402

CELL = 200
COLS = ROWS = 10
PAD = 8


def preview(img):
    """A single preview image for an asset (tuples are stacked: wall + end
    cap, cave floor + wall, roof tiles + lines)."""
    if isinstance(img, (tuple, list)):
        parts = [p.convert("RGBA") for p in img]
        w = max(p.width for p in parts)
        h = sum(p.height for p in parts) + 12 * (len(parts) - 1)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        y = 0
        for p in parts:
            out.paste(p, (0, y))
            y += p.height + 12
        return out
    return img.convert("RGBA")


def tiled(img):
    w, h = img.size
    t = Image.new("RGBA", (w * 2, h * 2))
    for dx in (0, w):
        for dy in (0, h):
            t.paste(img, (dx, dy))
    return t


def main(out):
    os.makedirs(out, exist_ok=True)
    index = []
    atlas = None
    atlas_n = -1
    slot = COLS * ROWS
    failures = []

    def flush():
        if atlas is not None:
            atlas.save(os.path.join(out, f"atlas-{atlas_n}.webp"), "WEBP", quality=82, method=5)

    for title, kind, rows in catalog.sections():
        sec = {"section": title, "kind": kind, "items": []}
        for iid, name, fn, colorable in rows:
            try:
                img = preview(fn())
            except Exception:  # noqa: BLE001 - keep going, report it
                failures.append((iid, name, traceback.format_exc(limit=2)))
                continue
            if kind in ("tileset", "pattern", "terrain"):
                img = tiled(img)
            ow, oh = img.size
            if slot >= COLS * ROWS:
                flush()
                atlas_n += 1
                atlas = Image.new("RGBA", (COLS * CELL, ROWS * CELL), (0, 0, 0, 0))
                slot = 0
            cx, cy = (slot % COLS) * CELL, (slot // COLS) * CELL
            th = img.copy()
            th.thumbnail((CELL - 2 * PAD, CELL - 2 * PAD), Image.LANCZOS)
            atlas.paste(th, (cx + (CELL - th.width) // 2, cy + (CELL - th.height) // 2), th)
            sec["items"].append({"id": iid, "name": name, "atlas": atlas_n, "x": cx, "y": cy, "colorable": colorable, "w": ow, "h": oh})
            slot += 1
            print(iid, name, flush=True)
        index.append(sec)
    flush()
    with open(os.path.join(out, "assets.json"), "w") as f:
        json.dump({"cell": CELL, "cols": COLS, "atlases": atlas_n + 1, "sections": index}, f, ensure_ascii=False)
    total = sum(len(s["items"]) for s in index)
    print(f"{total} assets, {atlas_n + 1} atlases, {len(failures)} failures")
    for iid, name, tb in failures:
        print("FAILED", iid, name, tb)


if __name__ == "__main__":
    main(sys.argv[1])
