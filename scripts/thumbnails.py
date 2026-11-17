"""The pack's own library thumbnails, as packs ship them:
`thumbnails/<md5 of the texture's res:// path>.png`, cut by the
usual rules (the ones src-tauri/src/pack/thumbs.rs follows for packs that ship
none).

Other editors that load the pack would make the missing ones themselves, on
many threads at once; for a pack of thousands of textures that can crash
them, so the pack must ship them all to load everywhere.

    python3 scripts/builtin-pack/thumbnails.py   (after build.py drew the pack)
"""

import hashlib
import io
import os
import sys

from PIL import Image

TILE_PX = 256  # one grid tile, in texture px
CELL_PX = 64  # thumbnail side of grid cells
STRIP_WIDTH = 228  # widest a wall or path strip thumbnail gets


def rule_for(rel):
    """How a texture's thumbnail is cut, by its category (`textures/<category>/…`)."""
    category = rel.split("/")[1] if rel.count("/") >= 1 else ""
    if category in ("tilesets", "patterns", "materials"):
        return ("tile", CELL_PX)
    if category == "walls":
        return ("strip", 32)
    if category == "paths":
        return ("strip", 48)
    if category == "terrain":
        return ("square", 160)
    return ("fit", CELL_PX)


def make(img, rule):
    """The thumbnail of an RGBA image by `rule` (see rule_for)."""
    kind, size = rule
    w, h = img.size
    shrink = lambda im, nw, nh: im.resize((max(1, nw), max(1, nh)), Image.BILINEAR)
    if kind == "tile":
        return shrink(img.crop((0, 0, min(w, TILE_PX), min(h, TILE_PX))), size, size)
    if kind == "strip":
        box = img.getchannel("A").getbbox() or (0, 0, w, h)
        trimmed = img.crop(box)
        bw, bh = trimmed.size
        scaled = shrink(trimmed, round(bw * size / bh), size)
        return scaled.crop((0, 0, min(scaled.width, STRIP_WIDTH), size))
    if kind == "square":
        # Terrain alpha is the height used to blend terrains, not transparency.
        t = shrink(img, size, size)
        t.putalpha(255)
        return t
    k = size / max(w, h)
    return img if k >= 1 else shrink(img, round(w * k), round(h * k))


def thumbnail_name(pack_id, rel):
    """File name of a texture's thumbnail: the md5 of its res:// path."""
    return hashlib.md5(f"res://packs/{pack_id}/{rel}".encode()).hexdigest() + ".png"


def thumbnail_files(files, pack_id):
    """The thumbnails of the textures among `files` ({pack-relative path:
    encoded bytes}, as the pack ships them), as more such files."""
    out = {}
    for rel, data in files.items():
        if not rel.startswith("textures/"):
            continue
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        buf = io.BytesIO()
        make(img, rule_for(rel)).save(buf, "PNG", optimize=True)
        out[f"thumbnails/{thumbnail_name(pack_id, rel)}"] = buf.getvalue()
    return out


if __name__ == "__main__":
    # Standalone: remake them for the pack already drawn in OUT.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from build import OUT, PACK_ID, write_dir

    pack_dir = os.path.join(OUT, PACK_ID)
    files = {}
    for root, _dirs, names in os.walk(pack_dir):
        for n in names:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, pack_dir).replace(os.sep, "/")
            if not rel.startswith("thumbnails/"):
                with open(full, "rb") as fh:
                    files[rel] = fh.read()
    files.update(thumbnail_files(files, PACK_ID))
    write_dir(files)
