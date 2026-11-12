"""Builds the app's built-in asset pack (`src-tauri/resources/builtin.dungeondraft_pack`).

    python3 scripts/builtin-pack/build.py

Every texture is drawn by code (ink.py, textures.py, objects.py), so the pack
can be regenerated and tweaked; the output is committed so builds don't need
Python. Layout and data files follow Dungeondraft's pack format, which the
app already reads (see src-tauri/src/pack/).
"""

import hashlib
import io
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import objects as ob  # noqa: E402
import textures as tx  # noqa: E402

PACK_ID = "open20-essentials"
PACK = {
    "name": "Open20 Essentials",
    "id": PACK_ID,
    # Bump to reinstall it for users that have an older one (see builtin.rs).
    "version": "1.0.0",
    "author": "Open20",
    "keywords": "open20, builtin, essentials",
}
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "src-tauri", "resources", "builtin.dungeondraft_pack")


def webp(img, lossless=False):
    buf = io.BytesIO()
    if lossless:
        img.save(buf, "WEBP", lossless=True, method=6)
    else:
        img.save(buf, "WEBP", quality=88, method=6, alpha_quality=100)
    return buf.getvalue()


def res(rel):
    return f"res://packs/{PACK_ID}/{rel}"


def main():
    files = {}  # pack-relative path -> bytes
    tags = {"Colorable": []}

    def add(rel, img, **kw):
        files[rel] = webp(img, **kw)
        print(rel, len(files[rel]) // 1024, "KiB", flush=True)
        return rel

    def tileset(name, img, custom=False, lossless=False):
        rel = add(f"textures/tilesets/simple/{name}.webp", img, lossless=lossless)
        slug = name.lower().replace(" ", "_")
        files[f"data/tilesets/{slug}.dungeondraft_tileset"] = json.dumps(
            {"path": res(rel), "name": name, "type": "custom_color" if custom else "normal", "color": "ffffffff"},
            indent=1,
        ).encode()

    # Floors.
    tileset("Wood Planks", tx.wood_floor())
    tileset("Flagstones", tx.flagstones())
    tileset("Terracotta", tx.terracotta())
    tileset("Dungeon Stone", tx.dungeon_stone())
    tileset("Carpet", tx.carpet())
    tileset("Marble", tx.marble_checker())
    # Patterns (recolorable). Lossless: lossy chroma would bleed into the red mask.
    tileset("Tiles Pattern", tx.pattern_tiles(), custom=True, lossless=True)
    tileset("Basketweave Pattern", tx.pattern_basketweave(), custom=True, lossless=True)
    tileset("Hex Pattern", tx.pattern_hex(), custom=True, lossless=True)

    # Walls (+ end caps).
    for i, (kind, name) in enumerate((("stone", "Stone Wall"), ("brick", "Brick Wall"), ("wood", "Log Wall"), ("plaster", "Timber Wall"))):
        rel = add(f"textures/walls/{name}.webp", tx.wall_strip(kind, 100 + i))
        add(f"textures/walls/{name}_end.webp", tx.wall_end(kind, 200 + i))
        files[f"data/walls/{kind}.dungeondraft_wall"] = json.dumps({"path": res(rel), "color": "ffffffff"}, indent=1).encode()

    # Terrain.
    add("textures/terrain/Grass.webp", tx.grass())
    add("textures/terrain/Dirt.webp", tx.dirt())
    add("textures/terrain/Gravel.webp", tx.gravel())
    add("textures/terrain/Sand.webp", tx.sand())

    # Paths.
    add("textures/paths/Dirt Path.webp", tx.path_strip("dirt", 300))
    add("textures/paths/Cobblestone Path.webp", tx.path_strip("cobble", 301))

    # Caves.
    for i, name in enumerate(("Rocky Cave", "Pebbled Cave")):
        add(f"textures/caves/{name}/floor.webp", tx.cave_floor(400 + i))
        add(f"textures/caves/{name}/wall.webp", tx.cave_wall(410 + i))

    # Roofs.
    for i, (kind, name) in enumerate((("shingles", "Wood Shingles"), ("slate", "Slate"))):
        add(f"textures/roofs/{name}/tiles.webp", tx.roof_tiles(kind, 500 + i))
        for part in ("edge", "ridge", "hip"):
            add(f"textures/roofs/{name}/{part}.webp", tx.roof_line(kind, part, 510 + i))

    # Lights.
    add("textures/lights/Soft Light.webp", tx.light("soft"), lossless=True)
    add("textures/lights/Radiant Light.webp", tx.light("rays"), lossless=True)

    # Portals.
    for i, (kind, name) in enumerate((("door", "Door"), ("double_door", "Double Door"), ("window", "Window"), ("arch", "Archway"))):
        add(f"textures/portals/{name}.webp", tx.portal(kind, 600 + i))

    # Objects.
    for name, fn in ob.OBJECTS.items():
        colorable = name in ob.COLORABLE
        rel = add(f"textures/objects/{name}.webp", fn(), lossless=colorable)
        if colorable:
            tags["Colorable"].append(rel)
    for tag, names in ob.TAGS.items():
        tags[tag] = [f"textures/objects/{n}.webp" for n in names]
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
