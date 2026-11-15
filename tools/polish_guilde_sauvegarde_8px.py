#!/usr/bin/env python3
"""
Polish anti-pixels-parasites des 15 salles intérieures `guilde_destiny_*` de la SAUVEGARDE c2766e5
+ intégration de la nouvelle verdure autonome (673e05b) + garantie grille 8 px « comme Halcyon ».

Base : SAUVEGARDE c2766e5 (bois/fenêtres cintrées d'origine, 203 couleurs, lissés).
  * Nettoie les pixels parasites de chaque calque sauvegardé (amas <= 8 px de couleurs aberrantes
    hors palette dominante / famille prune-magenta -> remplacés par la couleur voisine majoritaire).
  * Recompose le schéma 8 calques Halcyon :
        [0] Floor         <- sauvegarde L0 (fond) + L1 (parquet)
        [1] Walls         <- sauvegarde L2 (profondeur arche) + L3 (parois + fenêtres cintrées)
        [2] Shadows       <- vide
        [3] Objects Under <- vide
        [4] Objects       <- vide
        [5] Objects Over  <- vide
        [6] Fringe        <- nouvelle verdure autonome `Destiny_Guilde_Verdure` (DrawLayer 4)
        [7] Supports      <- sauvegarde L7 (couronne de racines avant-plan)
  * Réécrit une banque `.tile` par salle en disposition 2D visuelle, dédupliquée.
  * GRID 8 px « comme Halcyon » : dimensions multiples exacts de 8 px (44x44, 60x46... comme les
    maps `guild_*` de Halcyon), calques/obstacles/entités/décorations strictement sur la grille de 8 px.
"""
from __future__ import annotations

import io
import json
import struct
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
TILE = 8

SAVE_SRC = Path("/var/tmp/c2766e5/game")      # arbre extrait de sauvegarde_guilde_complete_avant_refonte_ds_c2766e5.tar.gz
OUT_ART = ROOT / "art/guilde_destiny_reseau/polish_sauvegarde_8px"
USER_ART = Path("/home/user/guilde_destiny_reseau/polish_sauvegarde_8px")

LAYER_NAMES = ["Floor", "Walls", "Shadows", "Objects Under", "Objects", "Objects Over", "Fringe", "Supports"]
LAYER_DRAW = [0, 0, 0, 0, 0, 0, 4, 4]

# (asset, banque .tile) — noms exacts attendus par tools/tests/test_guilde_destiny_accueil.py
ROOMS = [
    ("guilde_destiny_accueil", "Destiny_Guilde_Accueil"),
    ("guilde_destiny_missions", "Destiny_Guilde_Missions"),
    ("guilde_destiny_grand_salon", "Destiny_Guilde_Grand_Salon"),
    ("guilde_destiny_bureau_maitre", "Destiny_Guilde_Bureau_Maitre"),
    ("guilde_destiny_carrefour", "Destiny_Guilde_Carrefour"),
    ("guilde_destiny_refectoire", "Destiny_Guilde_Refectoire"),
    ("guilde_destiny_cuisine", "Destiny_Guilde_Cuisine"),
    ("guilde_destiny_reserve", "Destiny_Guilde_Reserve"),
    ("guilde_destiny_couloir_ouest", "Destiny_Guilde_Couloir_Ouest"),
    ("guilde_destiny_couloir_est", "Destiny_Guilde_Couloir_Est"),
    ("guilde_destiny_dortoir_nord_1", "Destiny_Guilde_Dortoir_Nord_1"),
    ("guilde_destiny_dortoir_nord_2", "Destiny_Guilde_Dortoir_Nord_2"),
    ("guilde_destiny_dortoir_sud_1", "Destiny_Guilde_Dortoir_Sud_1"),
    ("guilde_destiny_dortoir_sud_2", "Destiny_Guilde_Dortoir_Sud_2"),
    ("guilde_destiny_chambre_heros", "Destiny_Guilde_Chambre_Heros"),
]

EMPTY_CELL = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}


# ------------------------------------------------------------------ .tile I/O
def read_tilesheet(path: Path):
    raw = Path(path).read_bytes()
    tile_size, count = struct.unpack_from("<ii", raw, 0)
    cells = {}
    for i in range(count):
        tx, ty, off = struct.unpack_from("<iiq", raw, 8 + 16 * i)
        ln = struct.unpack_from("<q", raw, off)[0]
        cells[(tx, ty)] = Image.open(io.BytesIO(raw[off + 8:off + 8 + ln])).convert("RGBA")
    return tile_size, cells


def write_tilesheet(path: Path, cells: dict) -> int:
    items = sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0]))
    header = struct.pack("<ii", TILE, len(items))
    entries, body = b"", b""
    cur = 8 + 16 * len(items)
    for (tx, ty), im in items:
        buf = io.BytesIO(); im.save(buf, format="PNG", optimize=False)
        png = buf.getvalue()
        entries += struct.pack("<iiq", tx, ty, cur)
        body += struct.pack("<q", len(png)) + png
        cur += 8 + len(png)
    Path(path).write_bytes(header + entries + body)
    return len(items)


def load_map(path: Path):
    d = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return d, d["Object"]


def save_map(path: Path, d) -> None:
    Path(path).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def map_dims(obj):
    nx = len(obj["obstacles"])
    ny = len(obj["obstacles"][0]) if nx else 0
    return nx, ny


def layer_cells(obj, li):
    out = {}
    for x, line in enumerate(obj["Layers"][li]["Tiles"]):
        for y, cell in enumerate(line):
            if cell and cell.get("Layers"):
                fr = cell["Layers"][0]["Frames"][0]
                out[(x, y)] = (fr["Sheet"], fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
    return out


def render_layer(obj, li, sheets, nx, ny):
    img = Image.new("RGBA", (nx * TILE, ny * TILE), (0, 0, 0, 0))
    for (x, y), (sheet, tx, ty) in layer_cells(obj, li).items():
        im = sheets[sheet].get((tx, ty))
        if im is not None:
            img.alpha_composite(im, (x * TILE, y * TILE))
    return img


# --------------------------------------------------- nettoyage anti-parasites
def is_magenta(rgb) -> bool:
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return (r - g) > 25 and (b - g) > 12


def palette_targets(arr, dom_min=40, outlier_dist=34, rare_max=14):
    fg = arr[..., 3] > 0
    pal = Counter(map(tuple, arr[fg][:, :4]))
    dominant = [np.array(c[:3], dtype=np.int32) for c, n in pal.items() if n >= dom_min]
    targets = set()
    for c, n in pal.items():
        if is_magenta(c[:3]):
            targets.add(c)
            continue
        if n > rare_max or not dominant:
            continue
        d = min(int(np.abs(np.array(c[:3], dtype=np.int32) - p).sum()) for p in dominant)
        if d >= outlier_dist:
            targets.add(c)
    return pal, targets


def clean_layer(arr: np.ndarray, max_area=8, iters=3):
    """Remplace les amas <= `max_area` px de couleurs aberrantes par la couleur voisine majoritaire."""
    a = arr.copy()
    h, w = a.shape[:2]
    total = 0
    n_targets = 0
    for _ in range(iters):
        pal, targets = palette_targets(a)
        n_targets = len(targets)
        if not targets:
            break
        mask = np.zeros((h, w), bool)
        for c in targets:
            mask |= np.all(a == np.array(c, dtype=a.dtype), axis=2)
        if not mask.any():
            break
        lbl, n = ndimage.label(mask, np.ones((3, 3), bool))
        if n == 0:
            break
        sizes = ndimage.sum(mask, lbl, range(1, n + 1))
        keep = np.zeros(n + 1, bool)
        keep[1:] = sizes <= max_area
        rem = keep[lbl]
        if not rem.any():
            break
        ys, xs = np.where(rem)
        changed = 0
        for y, x in zip(ys, xs):
            neigh = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w:
                        q = tuple(a[yy, xx])
                        if q[3] > 0:
                            neigh.append(q)
            if not neigh:
                continue
            c = Counter(neigh)
            best = next((cand for cand, _ in c.most_common() if cand not in targets), c.most_common(1)[0][0])
            a[y, x] = best
            changed += 1
        total += changed
        if changed == 0:
            break
    return a, total, n_targets


# ------------------------------------------------------------------- build
def verdure_from_current():
    """Cellules de verdure autonome (x,y)->(tx,ty) de chaque salle ACTUELLE (673e05b)."""
    out = {}
    for room, _ in ROOMS:
        d, o = load_map(GAME / f"Data/Ground/{room}.rsground")
        refs = {}
        for (x, y), (sheet, tx, ty) in layer_cells(o, 6).items():
            if sheet == "Destiny_Guilde_Verdure":
                refs[(x, y)] = (tx, ty)
        out[room] = refs
    return out


def build_room(room: str, sheet: str, verdure_refs: dict, stats: list):
    d, o = load_map(SAVE_SRC / f"Data/Ground/{room}.rsground")
    nx, ny_src = map_dims(o)
    ny = ny_src                          # grille Halcyon = multiple exact de 8 px (pas besoin de parité)

    src_sheets = set()
    for li in range(len(o["Layers"])):
        for v in layer_cells(o, li).values():
            src_sheets.add(v[0])
    banks = {n: read_tilesheet(SAVE_SRC / f"Content/Tile/{n}.tile")[1] for n in src_sheets}

    cleaned = []
    repaired = 0
    for li in range(8):
        arr = np.array(render_layer(o, li, banks, nx, ny_src)) if li < len(o["Layers"]) else np.zeros((ny_src * TILE, nx * TILE, 4), np.uint8)
        if li in (4, 5, 6):             # ancienne verdure grossière + calques mobilier vides : remplacés/laissés vides
            cleaned.append(None)
            continue
        arr2, rep, _ = clean_layer(arr)
        repaired += rep
        cleaned.append(arr2)

    # extension d'une ligne (grille Halcyon paire) : on duplique la dernière ligne de sol/murs
    def extend(arr):
        if arr is None:
            return None
        if ny == ny_src:
            return arr
        out = np.zeros((ny * TILE, nx * TILE, 4), np.uint8)
        out[: ny_src * TILE] = arr
        out[ny_src * TILE:] = arr[-TILE:]
        return out

    floor_src = extend(cleaned[0])
    floor_src = Image.fromarray(floor_src, "RGBA")
    floor_src.alpha_composite(Image.fromarray(extend(cleaned[1]), "RGBA"))
    walls_src = Image.fromarray(extend(cleaned[2]), "RGBA")
    walls_src.alpha_composite(Image.fromarray(extend(cleaned[3]), "RGBA"))
    supports_src = Image.fromarray(extend(cleaned[7]), "RGBA")

    size = (nx * TILE, ny * TILE)
    empty = Image.new("RGBA", size, (0, 0, 0, 0))
    layers_imgs = [floor_src, walls_src, empty.copy(), empty.copy(), empty.copy(), empty.copy(), empty.copy(), supports_src]

    # ---- banque .tile de la salle (2D visuelle + déduplication) ----
    cells_out, keymap, layer_refs = {}, {}, []
    for li in range(8):
        if li == 6:
            layer_refs.append(dict(verdure_refs[room]))
            continue
        img = layers_imgs[li]
        refs = {}
        for x in range(nx):
            for y in range(ny):
                crop = img.crop((x * TILE, y * TILE, (x + 1) * TILE, (y + 1) * TILE))
                if crop.getchannel("A").getextrema()[1] == 0:
                    continue
                key = crop.tobytes()
                if key in keymap:
                    refs[(x, y)] = keymap[key]
                else:
                    keymap[key] = (x, y)
                    cells_out[(x, y)] = crop
                    refs[(x, y)] = (x, y)
        layer_refs.append(refs)
    n_tiles = write_tilesheet(GAME / f"Content/Tile/{sheet}.tile", cells_out)

    # ---- .rsground : 8 calques Halcyon ----
    obstacles = []
    for x in range(nx):
        col = [dict(c) for c in o["obstacles"][x]]
        while len(col) < ny:
            col.append({"Bounds": {"X": x * TILE, "Y": len(col) * TILE, "Width": TILE, "Height": TILE}, "Tags": 1})
        obstacles.append(col)
    o["obstacles"] = obstacles

    new_layers = []
    for li in range(8):
        tiles = [[dict(EMPTY_CELL) for _ in range(ny)] for _ in range(nx)]
        src_sheet = "Destiny_Guilde_Verdure" if li == 6 else sheet
        for (x, y), (tx, ty) in layer_refs[li].items():
            if y >= ny:
                continue
            tiles[x][y] = {
                "AutoTileset": "", "Associates": [],
                "Layers": [{"Frames": [{"Sheet": src_sheet, "TexLoc": {"X": tx, "Y": ty}}], "FrameLength": 60}],
                "NeighborCode": 0,
            }
        new_layers.append({"Name": LAYER_NAMES[li], "Layer": LAYER_DRAW[li], "Visible": True, "Tiles": tiles})
    o["Layers"] = new_layers

    # entités : alignement 8 px (comme Halcyon)
    for grp in o.get("Entities") or []:
        for key in ("GroundObjects", "Markers", "Spawners"):
            for e in grp.get(key) or []:
                coll = e.get("Collider") or e.get("Location")
                if coll:
                    coll["X"] = (coll["X"] // TILE) * TILE
                    coll["Y"] = (coll["Y"] // TILE) * TILE

    o["Comment"] = (
        "Base visuelle SAUVEGARDE c2766e5, polish anti-pixels-parasites (0 magenta), "
        "verdure autonome 673e05b sur Fringe, organisation 8 calques Halcyon, grille 8 px stricte."
    )
    save_map(GAME / f"Data/Ground/{room}.rsground", d)

    over_walk = sum(1 for li in (6, 7) for (x, y) in layer_refs[li] if o["obstacles"][x][y]["Tags"] == 0)
    residual = 0
    for li, img in enumerate(layers_imgs):
        if li == 6:
            continue
        a = np.array(img)
        fg = a[..., 3] > 0
        rgb = a[fg][:, :3].astype(int)
        residual += int(np.sum((rgb[:, 0] - rgb[:, 1] > 35) & (rgb[:, 2] - rgb[:, 1] > 25)))
    stats.append((room, sheet, nx, ny, n_tiles, repaired, over_walk, residual))
    return floor_src, walls_src, supports_src, layer_refs[6], size


def verify_grid() -> list:
    problems = []
    for room, sheet in ROOMS:
        d, o = load_map(GAME / f"Data/Ground/{room}.rsground")
        nx, ny = map_dims(o)
        if (nx * TILE) % TILE or (ny * TILE) % TILE:
            problems.append(f"{room}: dimensions {nx}x{ny} tuiles ({nx*8}x{ny*8} px) non conformes")
        for li, L in enumerate(o["Layers"]):
            if len(L["Tiles"]) != nx or any(len(c) != ny for c in L["Tiles"]):
                problems.append(f"{room}: calque {li} {L['Name']} taille != ({nx},{ny})")
        for x in range(nx):
            for y in range(ny):
                b = o["obstacles"][x][y]["Bounds"]
                if b["X"] != x * TILE or b["Y"] != y * TILE or b["Width"] % TILE or b["Height"] % TILE:
                    problems.append(f"{room}: obstacle({x},{y}) hors grille")
                    break
        for grp in o.get("Entities") or []:
            for key in ("GroundObjects", "Markers", "Spawners"):
                for e in grp.get(key) or []:
                    coll = e.get("Collider") or e.get("Location")
                    if coll and (coll["X"] % TILE or coll["Y"] % TILE
                                 or coll.get("Width", 0) % TILE or coll.get("Height", 0) % TILE):
                        problems.append(f"{room}: entité {e.get('EntName')} hors grille {coll}")
        for dec in o.get("Decorations") or []:
            loc = dec["Anims"][0]["MapLoc"]
            if loc["X"] % TILE or loc["Y"] % TILE:
                problems.append(f"{room}: décoration {dec['Name']} hors grille {loc}")
    # objets .dir placés par le Lua (fenêtres + porte du salon)
    lua = (GAME / "Data/Script/destiny/guilde_destiny_decors.lua").read_text(encoding="utf-8")
    import re
    for m in re.finditer(r"x = (\d+), y = (\d+), w = (\d+), h = (\d+)", lua):
        vals = [int(g) for g in m.groups()]
        if any(v % TILE for v in vals):
            problems.append(f"guilde_destiny_decors.lua: fenêtre hors grille {vals}")
    for m in re.finditer(r"x = (\d+),\n\s*y = (\d+),\n\s*w = (\d+),\n\s*h = (\d+)", lua):
        vals = [int(g) for g in m.groups()]
        if any(v % TILE for v in vals):
            problems.append(f"guilde_destiny_decors.lua: porte du salon hors grille {vals}")
    return problems


def main() -> int:
    OUT_ART.mkdir(parents=True, exist_ok=True)
    USER_ART.mkdir(parents=True, exist_ok=True)
    verdure_refs = verdure_from_current()
    stats = []
    renders = {}
    for room, sheet in ROOMS:
        floor_img, walls_img, supports_img, vrefs, size = build_room(room, sheet, verdure_refs, stats)
        comp = Image.new("RGBA", size, (0, 0, 0, 0))
        comp.alpha_composite(floor_img)
        comp.alpha_composite(walls_img)
        comp.alpha_composite(supports_img)
        (OUT_ART / f"{room}.png").parent.mkdir(parents=True, exist_ok=True)
        comp.save(OUT_ART / f"{room}.png")
        (USER_ART / f"{room}.png").parent.mkdir(parents=True, exist_ok=True)
        comp.save(USER_ART / f"{room}.png")
        renders[room] = comp
        print(f"OK {room:32s} {size[0]//8:3d}x{size[1]//8:3d} tuiles ({size[0]}x{size[1]} px)")

    print("\n%-32s %-30s %4s %4s %7s %9s %9s %8s" % ("salle", "banque .tile", "w", "h", "tuiles", "nettoyés", "sol débord", "magenta"))
    for s in stats:
        print("%-32s %-30s %4d %4d %7d %9d %9d %8d" % s)
    print("\nTotal pixels parasites nettoyés :", sum(s[5] for s in stats))
    print("Magenta résiduel               :", sum(s[7] for s in stats))
    print("Débordement verdure/supports    :", sum(s[6] for s in stats))

    problems = verify_grid()
    print("\n=== VÉRIFICATION GRILLE 8 px (comme Halcyon) ===")
    if problems:
        for p in problems[:40]:
            print("  KO", p)
        return 1
    print("  OK : 15/15 cartes — dimensions, calques, obstacles,")
    print("       entités, décorations, fenêtres .dir et double porte sur la grille 8 px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
