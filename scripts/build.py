"""Draws the app's built-in asset pack into `src-tauri/resources/builtin/`.

    npm run pack   (python3 scripts/builtin-pack/build.py)

Every texture is drawn by code (pen.py + the obj_*/tex_* modules, listed in
catalog.py). The output is the pack's files, unpacked, laid out as in the
pack (`<id>.json` manifest + `<id>/textures/...`, `<id>/data/...`) and
committed: drawing takes a while, so CI never does it. build.rs packs that
folder into the `.dungeondraft_pack` the app embeds. Only files whose bytes
changed are rewritten, so a commit shows exactly which assets changed.
"""

import io
import json
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import catalog  # noqa: E402

PACK_ID = "open20-essentials"
PACK = {
    "name": "Open20 Essentials",
    "id": PACK_ID,
    # Bump to reinstall it for users that have an older one (see builtin.rs).
    "version": "2.0.1",
    "author": "Open20",
    "keywords": "open20, builtin, essentials",
}
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "src-tauri", "resources", "builtin")

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
    write_dir(files)


def write_dir(files):
    """Sync OUT with the pack's files: rewrite only what changed, drop stale ones."""
    want = {f"{PACK_ID}.json": (json.dumps(PACK, indent=2) + "\n").encode()}
    want.update({f"{PACK_ID}/{rel}": data for rel, data in files.items()})
    changed = 0
    for rel, data in want.items():
        path = os.path.join(OUT, rel)
        try:
            with open(path, "rb") as f:
                if f.read() == data:
                    continue
        except FileNotFoundError:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        changed += 1
    removed = 0
    for dirpath, _dirs, names in os.walk(OUT, topdown=False):
        for n in names:
            rel = os.path.relpath(os.path.join(dirpath, n), OUT).replace(os.sep, "/")
            if rel not in want:
                os.remove(os.path.join(dirpath, n))
                removed += 1
        if dirpath != OUT and not os.listdir(dirpath):
            os.rmdir(dirpath)
    print(f"{OUT}: {len(want)} files ({changed} written, {removed} removed)")


if __name__ == "__main__":
    main()
