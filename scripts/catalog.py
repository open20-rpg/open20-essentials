"""Every asset of the built-in pack, grouped as the review page and the
pack builder see them: (section title, kind, ID prefix, {name: fn},
colorable names). A module that doesn't exist yet is skipped, so this works
while sections are still being drawn."""

import importlib

# (module, dict name, colorable set name or None, section title, kind, prefix)
SOURCES = [
    ("objects", "OBJECTS", "COLORABLE", "Objetos base", "object", "OB"),
    ("trees", "TREES", "TREES_COLORABLE", "Árboles", "object", "T"),
    ("obj_furniture", "FURNITURE", "FURNITURE_COLORABLE", "Muebles", "object", "F"),
    ("obj_storage", "STORAGE", "STORAGE_COLORABLE", "Almacén, cocina y vajilla", "object", "S"),
    ("obj_stone", "STONE_OBJECTS", "STONE_COLORABLE", "Piedra y fuentes", "object", "P"),
    ("obj_nature", "NATURE", None, "Naturaleza", "object", "N"),
    ("obj_pots", "POTS", None, "Macetas y vasijas", "object", "V"),
    ("obj_craft", "CRAFT", None, "Taller y oficios", "object", "W"),
    ("obj_magic", "MAGIC", None, "Magia y alquimia", "object", "M"),
    ("obj_temple", "TEMPLE", "TEMPLE_COLORABLE", "Religión y templo", "object", "R"),
    ("obj_dungeon", "DUNGEON", None, "Mazmorra y prisión", "object", "D"),
    ("obj_war", "WAR", "WAR_COLORABLE", "Armas y guerra", "object", "A"),
    ("obj_town", "TOWN", "TOWN_COLORABLE", "Pueblo y exterior", "object", "U"),
    ("obj_camp", "CAMP", "CAMP_COLORABLE", "Campamento y viaje", "object", "C"),
    ("obj_farm", "FARM", "FARM_COLORABLE", "Granja, animales y puerto", "object", "G"),
    ("obj_tavern", "TAVERN", "TAVERN_COLORABLE", "Taberna, biblioteca y tesoro", "object", "K"),
    ("obj_cave", "CAVE", "CAVE_COLORABLE", "Cueva, ruinas e iluminación", "object", "Q"),
    ("obj_decor", "DECOR", "DECOR_COLORABLE", "Decoración, castillo y jardín", "object", "E"),
    ("obj_shop", "SHOP", "SHOP_COLORABLE", "Tiendas, cocina, cementerio y fantasía", "object", "H"),
    ("obj_variants", "VARIANTS", "VARIANTS_COLORABLE", "Variantes", "object", "X"),
    ("obj_srd_weapons", "SRD_WEAPONS", "SRD_WEAPONS_COLORABLE", "SRD: armas y munición", "object", "SA"),
    ("obj_srd_armor", "SRD_ARMOR", "SRD_ARMOR_COLORABLE", "SRD: armaduras, escudos y vestimenta", "object", "SB"),
    ("obj_srd_gear", "SRD_GEAR", "SRD_GEAR_COLORABLE", "SRD: equipo de aventura", "object", "SC"),
    ("obj_srd_tools", "SRD_TOOLS", "SRD_TOOLS_COLORABLE", "SRD: herramientas, kits e instrumentos", "object", "SD"),
    ("obj_srd_magic", "SRD_MAGIC", "SRD_MAGIC_COLORABLE", "SRD: objetos mágicos", "object", "SE"),
    ("obj_srd_wondrous", "SRD_WONDROUS", "SRD_WONDROUS_COLORABLE", "SRD: objetos maravillosos", "object", "SG"),
    ("obj_srd_mounts", "SRD_MOUNTS", "SRD_MOUNTS_COLORABLE", "SRD: monturas y vehículos", "object", "SF"),
    ("tex_ground", "FLOORS", None, "Pisos", "tileset", "PI"),
    ("tex_ground", "PATTERNS", None, "Patrones coloreables", "pattern", "PA"),
    ("tex_ground", "TERRAINS", None, "Terrenos", "terrain", "TE"),
    ("tex_ground", "PATHS", None, "Caminos", "path", "CA"),
    ("tex_ground", "LIGHTS", None, "Luces", "light", "LU"),
    ("tex_build", "WALLS", None, "Paredes", "wall", "PR"),
    ("tex_build", "PORTALS", None, "Puertas y ventanas", "portal", "PO"),
    ("tex_build", "CAVES", None, "Cuevas", "cave", "CU"),
    ("tex_build", "ROOFS", None, "Techos", "roof", "TC"),
    ("tex_floors2", "FLOORS2", None, "Pisos (más)", "tileset", "PJ"),
    ("tex_patterns2", "PATTERNS2", None, "Patrones coloreables (más)", "pattern", "PB"),
    ("tex_terrain2", "TERRAINS2", None, "Terrenos (más)", "terrain", "TF"),
    ("tex_paths2", "PATHS2", None, "Caminos (más)", "path", "CB"),
    ("tex_walls2", "WALLS2", None, "Paredes (más)", "wall", "PS"),
    ("tex_portals2", "PORTALS2", None, "Puertas y ventanas (más)", "portal", "PP"),
    ("tex_roofs2", "ROOFS2", None, "Techos (más)", "roof", "TD"),
    ("tex_caves2", "CAVES2", None, "Cuevas (más)", "cave", "CV"),
    ("tex_caves2", "LIGHTS2", None, "Luces (más)", "light", "LV"),
]


def sections():
    """Yield (title, kind, [(id, name, fn, colorable), ...]) for every
    section whose module is available."""
    for mod_name, dict_name, col_name, title, kind, prefix in SOURCES:
        try:
            mod = importlib.import_module(mod_name)
        except ImportError:
            continue
        items = getattr(mod, dict_name, None)
        if not items:
            continue
        colorable = set(getattr(mod, col_name, set()) or set()) if col_name else set()
        rows = [(f"{prefix}{i + 1:03d}", name, fn, name in colorable or kind == "pattern") for i, (name, fn) in enumerate(items.items())]
        yield title, kind, rows
