#!/usr/bin/env python3
"""
Version PMDO des 15 salles intérieures `guilde_destiny_*`, construite DEPUIS la version DS (673e05b).

Principe : les FORMES DS sont conservées à l'identique (le masque alpha ne bouge pas d'un pixel,
les collisions et les marqueurs non plus). Seul le rendu change :
  1. Re-shading « PMDO enrichi » : chaque aplat DS reçoit un volume (occlusion de bord + lumière
     du haut + rebond chaud du parquet) puis la couleur glisse le long d'une micro-ramp.
       parquet : doux      murs : medium     racines/supports : medium     verdure : léger
     Le fond marron #68482F du plan n'est jamais ombré.
  2. Nettoyage des pixels parasites : amas <= 3 px dont la couleur s'écarte de tout leur voisinage
     sont fondus dans la couleur dominante du voisinage. La silhouette reste intacte.
  3. Recompilation des 15 banques `.tile` en disposition 2D visuelle, dédupliquées, RGBA pur (alpha 0/255).
  4. Grille 8 px vérifiée : dimensions, calques, obstacles, entités, décorations, fenêtres .dir, porte.
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

sys.path.insert(0, str(Path("/var/tmp/work")))

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
TILE = 8
OUT_ART = ROOT / "art/guilde_destiny_reseau/pmdo_reshade"
USER_ART = Path("/home/user/guilde_destiny_reseau/pmdo_reshade")

LAYER_NAMES = ["Floor", "Walls", "Shadows", "Objects Under", "Objects", "Objects Over", "Fringe", "Supports"]
LAYER_DRAW = [0, 0, 0, 0, 0, 0, 4, 4]
LAYER_KIND = {0: "floor", 1: "walls", 2: "shadows", 6: "fringe", 7: "supports"}

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


def read_tilesheet(path: Path):
    raw = Path(path).read_bytes()
    ts, count = struct.unpack_from("<ii", raw, 0)
    cells = {}
    for i in range(count):
        tx, ty, off = struct.unpack_from("<iiq", raw, 8 + 16 * i)
        ln = struct.unpack_from("<q", raw, off)[0]
        cells[(tx, ty)] = Image.open(io.BytesIO(raw[off + 8:off + 8 + ln])).convert("RGBA")
    return ts, cells


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
    nx = len(obj["obstacles"]); ny = len(obj["obstacles"][0]) if nx else 0
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


def verify_grid() -> list:
    problems = []
    for room, _ in ROOMS:
        d, o = load_map(GAME / f"Data/Ground/{room}.rsground")
        nx, ny = map_dims(o)
        if (nx * TILE) % TILE or (ny * TILE) % TILE:
            problems.append(f"{room}: dimensions {nx*8}x{ny*8} px hors grille")
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
    return problems


def main() -> int:
    import pmdo_shade
    import speckle

    OUT_ART.mkdir(parents=True, exist_ok=True)
    USER_ART.mkdir(parents=True, exist_ok=True)
    stats = []

    for room, sheet in ROOMS:
        d, o = load_map(GAME / f"Data/Ground/{room}.rsground")
        nx, ny = map_dims(o)

        sheets_names = set()
        for li in range(len(o["Layers"])):
            for v in layer_cells(o, li).values():
                sheets_names.add(v[0])
        banks = {n: read_tilesheet(GAME / f"Content/Tile/{n}.tile")[1] for n in sheets_names}

        out_imgs, replaced, colors_in, colors_out = [], 0, 0, 0
        for li in range(8):
            rgba = np.array(render_layer(o, li, banks, nx, ny))
            if li in LAYER_KIND and rgba[..., 3].any():
                rgba, c_in, c_out = pmdo_shade.reskin(rgba, LAYER_KIND[li])
                colors_in += c_in; colors_out += c_out
                # on ne nettoie pas les calques d'ombre (semi-transparents, voulus)
                if li != 2:
                    rgba, rep = speckle.clean(rgba)
                    replaced += rep
            out_imgs.append(Image.fromarray(rgba, "RGBA"))

        # --- banque .tile de la salle : IDs uniques + déduplication par contenu ---
        # (l'ancienne version utilisait (x,y) comme ID : un mur et un sol de la même
        #  colonne s'écrasaient mutuellement -> plaques sombres sur le parquet)
        cells_out, keymap, refs_by_layer = {}, {}, []
        SHEET_W = 64
        for li in range(8):
            if li == 6:                                   # verdure : reste dans sa banque dédiée
                refs_by_layer.append(dict(layer_cells(o, 6)))
                continue
            img = out_imgs[li]
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
                        nid = len(keymap)
                        tid = (nid % SHEET_W, nid // SHEET_W)
                        keymap[key] = tid
                        cells_out[tid] = crop
                        refs[(x, y)] = tid
            refs_by_layer.append(refs)
        n_tiles = write_tilesheet(GAME / f"Content/Tile/{sheet}.tile", cells_out)

        # --- la verdure re-shadée doit être écrite dans sa propre banque ---
        #     (les 15 salles partagent Destiny_Guilde_Verdure : on la traite au premier passage)
        if room == ROOMS[0][0]:
            #    ATTENTION : la banque est partagée par les 15 salles -> on re-shade
            #    *toutes* ses tuiles, sinon les salles suivantes perdent leurs guirlandes.
            verd_bank_full = read_tilesheet(GAME / "Content/Tile/Destiny_Guilde_Verdure.tile")[1]
            verd_cells = {}
            for key, im in verd_bank_full.items():
                arr = np.array(im)
                if arr[..., 3].any():
                    arr = pmdo_shade.reskin(arr, "fringe")[0]
                verd_cells[key] = Image.fromarray(arr, "RGBA")
            if verd_cells:
                write_tilesheet(GAME / "Content/Tile/Destiny_Guilde_Verdure.tile", verd_cells)

        # --- .rsground : mapping remis à jour ---
        for li in range(8):
            if li == 6:
                continue
            tiles = o["Layers"][li]["Tiles"]
            for x in range(nx):
                for y in range(ny):
                    if (x, y) in refs_by_layer[li]:
                        tx, ty = refs_by_layer[li][(x, y)]
                        tiles[x][y] = {
                            "AutoTileset": "", "Associates": [],
                            "Layers": [{"Frames": [{"Sheet": sheet, "TexLoc": {"X": tx, "Y": ty}}], "FrameLength": 60}],
                            "NeighborCode": 0,
                        }
                    else:
                        tiles[x][y] = dict(EMPTY_CELL)
        # alignement 8 px des entités (marqueurs de centre décalés de 4 px à l'origine)
        for grp in o.get("Entities") or []:
            for key in ("GroundObjects", "Markers", "Spawners"):
                for e in grp.get(key) or []:
                    coll = e.get("Collider") or e.get("Location")
                    if coll:
                        coll["X"] = (coll["X"] // TILE) * TILE
                        coll["Y"] = (coll["Y"] // TILE) * TILE

        o["Comment"] = (
            "Version PMDO : formes DS 673e05b conservees, re-shading enrichi (degrades, volume, "
            "occlusion) + nettoyage des pixels parasites, 8 calques Halcyon, grille 8 px."
        )
        save_map(GAME / f"Data/Ground/{room}.rsground", d)

        # rendu de contrôle
        comp = Image.new("RGBA", (nx * TILE, ny * TILE), (0, 0, 0, 0))
        for im in out_imgs:
            comp.alpha_composite(im)
        comp.save(OUT_ART / f"{room}.png")
        comp.save(USER_ART / f"{room}.png")
        stats.append((room, nx, ny, n_tiles, colors_in, colors_out, replaced))
        print(f"OK {room:32s} {nx}x{ny} tuiles | {colors_in:3d}->{colors_out:4d} couleurs | {replaced:5d} pixels nettoyes | {n_tiles} tuiles")

    print("\n%-32s %4s %4s %8s %10s %10s %9s" % ("salle", "w", "h", "tuiles", "coul. DS", "coul. PMDO", "nettoyés"))
    for s in stats:
        print("%-32s %4d %4d %8d %10d %10d %9d" % s)
    print("\nTotal couleurs : %d (DS) -> %d (PMDO)" % (sum(s[4] for s in stats), sum(s[5] for s in stats)))
    print("Total pixels parasites nettoyés :", sum(s[6] for s in stats))

    problems = verify_grid()
    print("\n=== VÉRIFICATION GRILLE 8 px ===")
    if problems:
        for p in problems[:40]:
            print("  KO", p)
        return 1
    print("  OK 15/15 : dimensions, calques, obstacles, entités, décorations, fenêtres, porte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
