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

CELL = int(os.environ.get("REVIEW_CELL", "200"))
COLS = ROWS = int(os.environ.get("REVIEW_COLS", "10"))
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


def opaque(img):
    img = img.convert("RGBA")
    img.putalpha(255)
    return img


def tiled(img):
    w, h = img.size
    t = Image.new("RGBA", (w * 2, h * 2))
    for dx in (0, w):
        for dy in (0, h):
            t.paste(img, (dx, dy))
    return t


def _render(job):
    """Worker: render one asset to a thumbnail (PNG bytes) and its size."""
    import io

    si, idx, kind = job
    title, kind, rows = list(catalog.sections())[si]
    iid, name, fn, colorable = rows[idx]
    try:
        img = preview(fn())
    except Exception:  # noqa: BLE001 - reported, not fatal
        return (si, idx, None, traceback.format_exc(limit=2))
    if kind == "terrain":
        # Terrain alpha is a height map for blending, not transparency: the
        # app draws the result opaque, so the preview must too.
        img = opaque(img)
    if kind in ("tileset", "pattern", "terrain"):
        img = tiled(img)
    ow, oh = img.size
    th = img.copy()
    th.thumbnail((CELL - 2 * PAD, CELL - 2 * PAD), Image.LANCZOS)
    buf = io.BytesIO()
    th.save(buf, "PNG")
    return (si, idx, (buf.getvalue(), ow, oh), None)


def main(out):
    import io
    from multiprocessing import Pool

    os.makedirs(out, exist_ok=True)
    secs = list(catalog.sections())
    # REVIEW_IDS=OB010,S003,... renders only those assets (a re-review batch).
    only = {i for i in os.environ.get("REVIEW_IDS", "").split(",") if i}
    jobs = [(si, idx, kind) for si, (title, kind, rows) in enumerate(secs) for idx in range(len(rows)) if not only or rows[idx][0] in only]
    results = {}
    failures = []
    with Pool(max(1, os.cpu_count() or 1)) as pool:
        for n, (si, idx, res, err) in enumerate(pool.imap_unordered(_render, jobs, chunksize=2)):
            if err:
                failures.append((secs[si][2][idx][0], secs[si][2][idx][1], err))
            else:
                results[(si, idx)] = res
            if n % 100 == 0:
                print(f"{n}/{len(jobs)}", flush=True)
    index = []
    atlas, atlas_n, slot = None, -1, COLS * ROWS

    def flush():
        if atlas is not None:
            atlas.save(os.path.join(out, f"atlas-{atlas_n}.webp"), "WEBP", quality=78, method=4)

    for si, (title, kind, rows) in enumerate(secs):
        sec = {"section": title, "kind": kind, "items": []}
        for idx, (iid, name, fn, colorable) in enumerate(rows):
            if (si, idx) not in results:
                continue
            data, ow, oh = results[(si, idx)]
            if slot >= COLS * ROWS:
                flush()
                atlas_n += 1
                atlas = Image.new("RGBA", (COLS * CELL, ROWS * CELL), (0, 0, 0, 0))
                slot = 0
            th = Image.open(io.BytesIO(data)).convert("RGBA")
            cx, cy = (slot % COLS) * CELL, (slot // COLS) * CELL
            atlas.paste(th, (cx + (CELL - th.width) // 2, cy + (CELL - th.height) // 2), th)
            sec["items"].append({"id": iid, "name": name, "atlas": atlas_n, "x": cx, "y": cy, "colorable": colorable, "w": ow, "h": oh})
            slot += 1
        if sec["items"]:
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
