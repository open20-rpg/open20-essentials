"""Builds the app's built-in asset pack (`src-tauri/resources/builtin.dungeondraft_pack`).

    python3 scripts/builtin-pack/build.py

Every texture is drawn by code (pen.py + the obj_*/tex_* modules, listed in
catalog.py), so the pack can be regenerated and tweaked; the output is
committed so builds don't need Python. Layout and data files follow
Dungeondraft's pack format, which the app already reads (see src-tauri/src/pack/).
Rendering runs in parallel; output order is deterministic.
"""

import hashlib
import io
import json
import os
import struct
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import catalog  # noqa: E402

PACK_ID = "open20-essentials"
PACK = {
    "name": "Open20 Essentials",
    "id": PACK_ID,
    # Bump to reinstall it for users that have an older one (see builtin.rs).
    "version": "2.0.0",
    "author": "Open20",
    "keywords": "open20, builtin, essentials",
}
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "src-tauri", "resources", "builtin.dungeondraft_pack")

# Object sections become folders and tags (English: pack data, not UI).
OBJECT_GROUPS = {
    "objects": "Essentials",
    "trees": "Trees",
    "obj_furniture": "Furniture",
    "obj_storage": "Storage and Kitchen",
    "obj_stone": "Stone and Fountains",
    "obj_nature": "Nature",
    "obj_pots": "Pots and Vases",
    "obj_craft": "Workshop",
    "obj_magic": "Magic and Alchemy",
    "obj_temple": "Temple",
    "obj_dungeon": "Dungeon",
    "obj_war": "Weapons and War",
    "obj_town": "Town",
    "obj_camp": "Camp and Travel",
    "obj_farm": "Farm and Harbor",
    "obj_tavern": "Tavern and Treasure",
    "obj_cave": "Cave and Ruins",
    "obj_decor": "Decor and Castle",
    "obj_shop": "Shops and Graveyard",
    "obj_variants": "Variants",
}


def webp(img, lossless=False):
    buf = io.BytesIO()
    if lossless:
        img.save(buf, "WEBP", lossless=True, method=6)
    else:
        img.save(buf, "WEBP", quality=88, method=6, alpha_quality=100)
    return buf.getvalue()


def res(rel):
    return f"res://packs/{PACK_ID}/{rel}"


def jobs():
    """(source index, row index) for every asset, in catalog order."""
    out = []
    for si, (mod, dname, _c, _t, kind, _p) in enumerate(catalog.SOURCES):
        items = getattr(__import__(mod), dname)
        out += [(si, k) for k in range(len(items))]
    return out


def render(job):
    """Worker: draw one asset and encode its files. Returns (job, [(rel, bytes)], colorable)."""
    si, k = job
    mod_name, dname, col_name, _title, kind, _prefix = catalog.SOURCES[si]
    mod = __import__(mod_name)
    name, fn = list(getattr(mod, dname).items())[k]
    colorable = kind == "pattern" or (col_name and name in getattr(mod, col_name, ()))
    img = fn()
    # Recolorable art stays lossless: lossy chroma would bleed into the red mask.
    lossless = bool(colorable)
    if kind == "object":
        parts = [(f"textures/objects/{OBJECT_GROUPS[mod_name]}/{name}.webp", img)]
    elif kind in ("tileset", "pattern"):
        parts = [(f"textures/tilesets/simple/{name}.webp", img)]
    elif kind == "terrain":
        parts = [(f"textures/terrain/{name}.webp", img)]
    elif kind == "path":
        parts = [(f"textures/paths/{name}.webp", img)]
    elif kind == "light":
        parts = [(f"textures/lights/{name}.webp", img)]
        lossless = True
    elif kind == "portal":
        parts = [(f"textures/portals/{name}.webp", img)]
    elif kind == "wall":
        strip, end = img
        parts = [(f"textures/walls/{name}.webp", strip), (f"textures/walls/{name}_end.webp", end)]
    elif kind == "cave":
        floor, wall = img
        parts = [(f"textures/caves/{name}/floor.webp", floor), (f"textures/caves/{name}/wall.webp", wall)]
    elif kind == "roof":
        parts = [(f"textures/roofs/{name}/{part}.webp", im) for part, im in zip(("tiles", "edge", "ridge", "hip"), img)]
    else:
        raise ValueError(kind)
    return job, [(rel, webp(im, lossless)) for rel, im in parts], bool(colorable)


def main():
    files = {}  # pack-relative path -> bytes
    tags = {"Colorable": []}
    all_jobs = jobs()
    results = {}
    with Pool(os.cpu_count() or 1) as pool:
        for n, (job, parts, colorable) in enumerate(pool.imap_unordered(render, all_jobs, chunksize=2)):
            results[job] = (parts, colorable)
            if n % 100 == 0:
                print(f"{n}/{len(all_jobs)}", flush=True)
    for job in all_jobs:
        si, _k = job
        mod_name, _d, _c, _t, kind, _p = catalog.SOURCES[si]
        parts, colorable = results[job]
        for rel, data in parts:
            if rel in files:
                raise SystemExit(f"duplicate pack path: {rel}")
            files[rel] = data
        rel = parts[0][0]
        name = os.path.splitext(os.path.basename(rel))[0]
        if kind in ("tileset", "pattern"):
            slug = name.lower().replace(" ", "_")
            files[f"data/tilesets/{slug}.dungeondraft_tileset"] = json.dumps(
                {"path": res(rel), "name": name, "type": "custom_color" if kind == "pattern" else "normal", "color": "ffffffff"},
                indent=1,
            ).encode()
        elif kind == "wall":
            slug = name.lower().replace(" ", "_")
            files[f"data/walls/{slug}.dungeondraft_wall"] = json.dumps({"path": res(rel), "color": "ffffffff"}, indent=1).encode()
        elif kind == "object":
            tags.setdefault(OBJECT_GROUPS[mod_name], []).append(rel)
            if colorable:
                tags["Colorable"].append(rel)
    files["data/default.dungeondraft_tags"] = json.dumps({"tags": tags, "sets": {}}, indent=1).encode()
    write_pck(files)


def write_pck(files):
    """A Godot 3 PCK (format 1), as `.dungeondraft_pack` files are."""
    entries = [(f"res://packs/{PACK_ID}.json", json.dumps(PACK, indent=1).encode())]
    entries += [(res(rel), data) for rel, data in sorted(files.items())]
    index_size = sum(4 + len(p.encode()) + 8 + 8 + 16 for p, _ in entries)
    offset = 88 + index_size
    header = struct.pack("<IIIII", 0x43504447, 1, 3, 4, 0) + b"\0" * 64 + struct.pack("<I", len(entries))
    index, blobs = b"", b""
    for path, data in entries:
        pb = path.encode()
        index += struct.pack("<I", len(pb)) + pb + struct.pack("<QQ", offset, len(data)) + hashlib.md5(data).digest()
        blobs += data
        offset += len(data)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(header + index + blobs)
    print(f"{OUT}: {len(entries)} files, {os.path.getsize(OUT) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
