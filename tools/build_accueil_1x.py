#!/usr/bin/env python3
"""
Reconstruit `guilde_destiny_accueil` à l'échelle native DS 1x (`512x384` px = `64x48` tuiles 8x8),
cohérente avec `guilde_destiny_missions` (`576x432`) et les 14 autres salles de la Guilde Destiny :
  - Base : `art/guilde_destiny_reseau/cartes_base_sans_decors/01_accueil_1x_base.png` (`512x384`, coin `#68482F`)
  - Verdure autonome : `art/guilde_destiny_reseau/guirlandes_verdure/guilde_destiny_accueil_verdure_1x.png`
    encodée sur `Layers[4]` (`Destiny_Guilde_Verdure.tile`, ajout sans altérer les indices des 14 autres salles)
  - 8 calques Halcyon (`Floor`, `Walls`, `Shadows`, `Objects Under`, `04 verdure separee`,
    `05 ombres mobilier guilde`, `06 immobilier guilde`, `Supports` en `Layer=4` sans débord sur tuile praticable)
  - Fenêtres 1x (`48x88` px) 4 ambiances (`Guilde_Fenetre_Accueil_{Gauche,Droite}_{Jour,Aube,Crepuscule,Nuit}.dir`)
    extraites sans perte (`[::3, ::3]`, diff=0) de la révision 3x NEAREST `120c6c7b`, posées en `(112, 56)` et `(352, 56)`
  - `Guilde_Verdure_Accueil.dir` ramené à l'échelle 1x (grille 8 px)
  - Grille d'obstacles `64x48` symétrique avec `Bounds` 8x8 exacts, marqueurs et capteurs alignés 8 px, BFS 16x16 vérifié.
"""
from __future__ import annotations

from collections import deque
import io
import json
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lib_tiles  # noqa: E402

GAME = ROOT / "game"
TILE_DIR = GAME / "Content/Tile"
OBJ_DIR = GAME / "Content/Object"
GROUND_DIR = GAME / "Data/Ground"
SCRIPT_DIR = GAME / "Data/Script/destiny"
ART_DIR = ROOT / "art/guilde_destiny_reseau"


def write_dir_rgba(path: Path, im: Image.Image) -> None:
    rgba = im.convert("RGBA")
    buf = io.BytesIO()
    rgba.save(buf, format="PNG", optimize=True)
    png = buf.getvalue()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<q", len(png)) + png + struct.pack("<iiii", rgba.width, rgba.height, 0, 1))


def read_dir_rgba_bytes(raw: bytes) -> np.ndarray:
    (plen,) = struct.unpack_from("<q", raw, 0)
    return np.array(Image.open(io.BytesIO(raw[8 : 8 + plen])).convert("RGBA"))


def premultiply_im(arr_rgba: np.ndarray) -> Image.Image:
    arr = arr_rgba.astype(np.float32)
    a = arr[..., 3:4] / 255.0
    arr[..., :3] = np.clip(np.round(arr[..., :3] * a), 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def encode_tile_sheet_from_dict(path: Path, cells: dict[tuple[int, int], np.ndarray]) -> int:
    """Écrit une banque `.tile` prémultipliée à partir d'un dict `(tx, ty) -> patch_rgba (8,8,4)` non-prémultiplié."""
    items: list[tuple[int, int, bytes]] = []
    for (tx, ty) in sorted(cells.keys(), key=lambda c: (c[1], c[0])):
        patch = cells[(tx, ty)]
        buf = io.BytesIO()
        premultiply_im(patch).save(buf, format="PNG", optimize=False)
        items.append((tx, ty, buf.getvalue()))
    n = len(items)
    header = bytearray(struct.pack("<ii", 8, n))
    body = bytearray()
    off = 8 + 16 * n
    for tx, ty, blob in items:
        header += struct.pack("<iiq", tx, ty, off)
        body += struct.pack("<q", len(blob)) + blob
        off += 8 + len(blob)
    path.write_bytes(bytes(header) + bytes(body))
    return n


def decode_unpremultiplied_tile_sheet(path: Path) -> dict[tuple[int, int], np.ndarray]:
    raw = path.read_bytes()
    ts, n = struct.unpack_from("<ii", raw, 0)
    assert ts == 8, (path, ts)
    out: dict[tuple[int, int], np.ndarray] = {}
    for i in range(n):
        tx, ty, ptr = struct.unpack_from("<iiq", raw, 8 + i * 16)
        (plen,) = struct.unpack_from("<q", raw, ptr)
        im = Image.open(io.BytesIO(raw[ptr + 8 : ptr + 8 + plen])).convert("RGBA")
        arr = np.array(im, dtype=np.float32)
        nz = arr[..., 3] > 0
        arr[nz, :3] = np.clip(np.round(arr[nz, :3] * 255.0 / arr[nz, 3:4]), 0, 255)
        out[(tx, ty)] = arr.astype(np.uint8)
    return out


def make_empty_cell() -> dict:
    return {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}


def make_cell(sheet: str, tx: int, ty: int) -> dict:
    return {
        "AutoTileset": "",
        "Associates": [],
        "Layers": [{"Frames": [{"Sheet": sheet, "TexLoc": {"X": tx, "Y": ty}}], "FrameLength": 60}],
        "NeighborCode": 0,
    }


def make_marker(name: str, x: int, y: int, direction: int, order: int) -> dict:
    return {
        "EntName": name,
        "Direction": direction,
        "EntEnabled": True,
        "EntOrder": order,
        "InteractOrder": order,
        "triggerType": 0,
        "Collider": {"X": x, "Y": y, "Width": 16, "Height": 16},
    }


def make_touch_trigger(name: str, x: int, y: int, w: int, h: int, order: int) -> dict:
    anim = {
        "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
        "AnimIndex": "",
        "FrameTime": 1,
        "StartFrame": -1,
        "EndFrame": -1,
        "AnimDir": -1,
        "Alpha": 255,
        "AnimFlip": 0,
    }
    return {
        "EntName": name,
        "Direction": 0,
        "EntEnabled": True,
        "EntOrder": order,
        "InteractOrder": order,
        "triggerType": 2,
        "ObjectAnim": dict(anim),
        "Passable": False,
        "CurrentAnim": dict(anim),
        "AnimTime": {"Ticks": 0},
        "Cycles": 0,
        "DrawOffset": {"X": 0, "Y": 0},
        "Collider": {"X": x, "Y": y, "Width": w, "Height": h},
    }


def build_1x_windows_and_verdure_obj() -> None:
    verd_full_init = np.array(Image.open(ART_DIR / "guirlandes_verdure/guilde_destiny_accueil_verdure_1x.png").convert("RGBA"))
    win_coords = {"Gauche": (112, 56), "Droite": (352, 56)}
    for side in ("Gauche", "Droite"):
        wx, wy = win_coords[side]
        v_sub = verd_full_init[wy : wy + 88, wx : wx + 48, 3] > 128
        for amb in ("Jour", "Aube", "Crepuscule", "Nuit"):
            name = f"Guilde_Fenetre_Accueil_{side}_{amb}.dir"
            raw_3x = subprocess.check_output(["git", "show", f"120c6c7b:game/Content/Object/{name}"], cwd=ROOT)
            arr_3x = read_dir_rgba_bytes(raw_3x)
            arr_1x = arr_3x[::3, ::3].copy()
            assert arr_1x.shape == (88, 48, 4), (name, arr_1x.shape)
            arr_1x[v_sub, 3] = 0
            write_dir_rgba(OBJ_DIR / name, Image.fromarray(arr_1x, "RGBA"))

    # Verdure objet `.dir` 1x alignée sur grille 8 px
    verd_full = np.array(Image.open(ART_DIR / "guirlandes_verdure/guilde_destiny_accueil_verdure_1x.png").convert("RGBA"))
    ys, xs = np.where(verd_full[..., 3] > 0)
    x0 = (int(xs.min()) // 8) * 8
    y0 = (int(ys.min()) // 8) * 8
    x1 = ((int(xs.max()) + 8) // 8) * 8
    y1 = ((int(ys.max()) + 8) // 8) * 8
    verd_crop = verd_full[y0:y1, x0:x1]
    write_dir_rgba(OBJ_DIR / "Guilde_Verdure_Accueil.dir", Image.fromarray(verd_crop, "RGBA"))
    print(f"[OK] 8 fenêtres Guilde_Fenetre_Accueil_*.dir (48x88 1x) + Guilde_Verdure_Accueil.dir ({x1-x0}x{y1-y0} 1x).")


def main() -> int:
    GW, GH = 64, 48
    W, H = 512, 384

    build_1x_windows_and_verdure_obj()

    # 1. Charger la référence HEAD (ou sauvegarde) pour construire la grille de marche 64x48 exacte
    raw_head = subprocess.check_output(["git", "show", "HEAD:game/Data/Ground/guilde_destiny_accueil.rsground"], cwd=ROOT)
    doc = json.loads(raw_head.decode("utf-8-sig"))
    g = doc["Object"]
    obs3 = g["obstacles"]

    walk = np.zeros((GW, GH), dtype=bool)
    for tx in range(GW):
        for ty in range(GH):
            cnt = sum(1 for dx in range(3) for dy in range(3) if obs3[tx * 3 + dx][ty * 3 + dy]["Tags"] == 0)
            walk[tx, ty] = cnt >= 5

    # Symétriser gauche/droite et combler les micro-trous isolés de l'ovale central
    walk = walk | walk[::-1, :]
    walk_closed = ndimage.binary_closing(walk, structure=np.ones((3, 3), dtype=bool))
    # Garder les couloirs nord (ty=13..17, tx=29..34) et sud (ty=34..43, tx=29..34) nets à 6 tuiles = 48 px :
    for ty in range(GH):
        for tx in range(GW):
            if 18 <= ty <= 33:
                walk[tx, ty] = walk_closed[tx, ty]
            elif 13 <= ty <= 17 or 34 <= ty <= 43:
                walk[tx, ty] = 29 <= tx <= 34
            else:
                walk[tx, ty] = False

    # 2. Charger la base visuelle 1x (512x384) et la verdure 1x (512x384)
    base_rgba = np.array(Image.open(ART_DIR / "cartes_base_sans_decors/01_accueil_1x_base.png").convert("RGBA"))
    assert base_rgba.shape == (H, W, 4), base_rgba.shape
    assert base_rgba[0, 0, :3].tolist() == [104, 72, 47], base_rgba[0, 0, :3].tolist()

    verd_rgba = np.array(Image.open(ART_DIR / "guirlandes_verdure/guilde_destiny_accueil_verdure_1x.png").convert("RGBA"))
    assert verd_rgba.shape == (H, W, 4), verd_rgba.shape
    # Assurer 0 débord de verdure sur les cases praticables si souhaité (cohérent avec polish_guilde_sauvegarde_8px)
    for tx in range(GW):
        for ty in range(GH):
            if walk[tx, ty]:
                verd_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8, 3] = 0

    # 3. Découper l'architecture en Floor (L0), Walls (L1) et Supports avant-plan (L7, Layer=4, hors walk)
    floor_img = np.zeros((H, W, 4), dtype=np.uint8)
    walls_img = np.zeros((H, W, 4), dtype=np.uint8)
    supports_img = np.zeros((H, W, 4), dtype=np.uint8)

    for tx in range(GW):
        for ty in range(GH):
            patch = base_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
            mr, mg, mb = float(patch[..., 0].mean()), float(patch[..., 1].mean()), float(patch[..., 2].mean())
            is_ext = abs(mr - 104.0) < 6.0 and abs(mg - 72.0) < 6.0 and abs(mb - 47.0) < 6.0
            if is_ext or walk[tx, ty]:
                floor_img[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = patch
            elif (
                not walk[tx, ty]
                and int(verd_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8, 3].max()) == 0
                and (
                    (ty <= 6 and 14 <= tx <= 49)
                    or (ty >= 34 and (tx <= 27 or tx >= 36))
                )
            ):
                # Couronne de racines haute & racines d'avant-plan sud (jamais sur walk[tx, ty] !)
                supports_img[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = patch
            else:
                walls_img[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = patch

    # 4. Construire `Destiny_Guilde_Accueil.tile` (dédupliquée 2D sur la grille 64x48)
    sheet_name = "Destiny_Guilde_Accueil"
    arch_cells: dict[tuple[int, int], np.ndarray] = {}
    arch_keymap: dict[bytes, tuple[int, int]] = {}
    arch_refs: list[dict[tuple[int, int], tuple[int, int]]] = [{}, {}, {}]  # floor, walls, supports

    for idx_l, arr_l in enumerate((floor_img, walls_img, supports_img)):
        for tx in range(GW):
            for ty in range(GH):
                patch = arr_l[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
                if int(patch[..., 3].max()) == 0:
                    continue
                key = patch.tobytes()
                loc = arch_keymap.get(key)
                if loc is None:
                    loc = (tx, ty)
                    while loc in arch_cells:
                        loc = (loc[0] + 1, loc[1])
                    arch_keymap[key] = loc
                    arch_cells[loc] = patch.copy()
                arch_refs[idx_l][(tx, ty)] = loc

    n_arch = encode_tile_sheet_from_dict(TILE_DIR / f"{sheet_name}.tile", arch_cells)

    # 5. Encoder `verd_rgba` dans `Destiny_Guilde_Verdure.tile` SANS modifier aucun `(tx, ty)` existant !
    verd_tile_path = TILE_DIR / "Destiny_Guilde_Verdure.tile"
    verd_cells = decode_unpremultiplied_tile_sheet(verd_tile_path)
    verd_keymap = {patch.tobytes(): loc for loc, patch in verd_cells.items()}
    max_vy = max((loc[1] for loc in verd_cells), default=0)
    next_idx = (max_vy + 1) * 32
    verd_refs: dict[tuple[int, int], tuple[int, int]] = {}

    for tx in range(GW):
        for ty in range(GH):
            patch = verd_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
            if int(patch[..., 3].max()) == 0:
                continue
            key = patch.tobytes()
            loc = verd_keymap.get(key)
            if loc is None:
                loc = (next_idx % 32, next_idx // 32)
                next_idx += 1
                verd_keymap[key] = loc
                verd_cells[loc] = patch.copy()
            verd_refs[(tx, ty)] = loc

    n_verd = encode_tile_sheet_from_dict(verd_tile_path, verd_cells)

    # 6. Assembler les 8 calques de `guilde_destiny_accueil.rsground`
    layer_defs = [
        ("Floor", 0, arch_refs[0], sheet_name),
        ("Walls", 0, arch_refs[1], sheet_name),
        ("Shadows", 0, {}, sheet_name),
        ("Objects Under", 0, {}, sheet_name),
        ("04 verdure separee", 0, verd_refs, "Destiny_Guilde_Verdure"),
        ("05 ombres mobilier guilde", 0, {}, sheet_name),
        ("06 immobilier guilde", 0, {}, sheet_name),
        ("Supports", 4, arch_refs[2], sheet_name),
    ]
    layers_json = []
    for lname, draw_layer, refs, sname in layer_defs:
        grid = [[make_empty_cell() for _ in range(GH)] for _ in range(GW)]
        for (tx, ty), (lx, ly) in refs.items():
            grid[tx][ty] = make_cell(sname, lx, ly)
        layers_json.append({"Name": lname, "Layer": draw_layer, "Visible": True, "Tiles": grid})

    obstacles_json = [
        [
            {
                "Bounds": {"X": tx * 8, "Y": ty * 8, "Width": 8, "Height": 8},
                "Tags": 0 if walk[tx, ty] else 2,
            }
            for ty in range(GH)
        ]
        for tx in range(GW)
    ]

    markers = [
        make_marker("EntreeSudMarker", 248, 312, 4, 0),
        make_marker("CentreMedaillonMarker", 248, 200, 0, 1),
        make_marker("EscalierNordMarker", 248, 136, 0, 2),
    ]
    triggers = [
        make_touch_trigger("SortieGuilde", 232, 336, 48, 16, 0),
        make_touch_trigger("EscalierNord", 232, 104, 48, 16, 1),
    ]

    # Vérifier BFS 16x16 depuis EntreeSudMarker vers tous les marqueurs et seuils
    def free16(px: int, py: int) -> bool:
        if px < 0 or py < 0 or px + 16 > W or py + 16 > H:
            return False
        return all(
            obstacles_json[cx][cy]["Tags"] == 0
            for cx in range(px // 8, (px + 15) // 8 + 1)
            for cy in range(py // 8, (py + 15) // 8 + 1)
        )

    assert free16(248, 312), "EntreeSudMarker non praticable"
    q = deque([(248, 312)])
    seen = {(248, 312)}
    while q:
        px, py = q.popleft()
        for nx, ny in ((px + 4, py), (px - 4, py), (px, py + 4), (px, py - 4)):
            if (nx, ny) not in seen and free16(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))
    for mk in markers:
        mc = mk["Collider"]
        assert (mc["X"], mc["Y"]) in seen, f"Marqueur {mk['EntName']} injoignable"

    g["Comment"] = (
        "Salle d'accueil de la Grande Guilde Destiny à l'échelle native DS 1x (512x384 px = 64x48 tuiles 8x8), "
        "0 magenta, verdure autonome sur calque dédié, fenêtres 48x88 4 ambiances, grille 8 px stricte."
    )
    g["obstacles"] = obstacles_json
    g["Layers"] = layers_json
    g["Decorations"] = []
    g["Entities"] = [
        {
            "Name": "EntitesAccueil",
            "Visible": True,
            "MapChars": [],
            "GroundObjects": triggers,
            "Spawners": [],
            "Markers": markers,
        }
    ]
    (GROUND_DIR / "guilde_destiny_accueil.rsground").write_text(
        json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )

    # Sauvegarder aussi l'aperçu PNG 512x384 dans `art/guilde_destiny_reseau/polish_sauvegarde_8px/` et `pmdo_reshade/`
    comp = Image.fromarray(base_rgba, "RGBA")
    comp.alpha_composite(Image.fromarray(verd_rgba, "RGBA"))
    for sub_d in ("polish_sauvegarde_8px", "pmdo_reshade"):
        out_p = ART_DIR / sub_d / "guilde_destiny_accueil.png"
        if out_p.parent.is_dir():
            comp.save(out_p)

    # 7. Mettre à jour `guilde_destiny_decors.lua` (fenêtres 1x en (112, 56, 48, 88) et (352, 56, 48, 88))
    decors_path = SCRIPT_DIR / "guilde_destiny_decors.lua"
    dtxt = decors_path.read_text(encoding="utf-8")
    dtxt = dtxt.replace(
        "{ name = 'Fenetre_Gauche', x = 336, y = 168, w = 144, h = 264,",
        "{ name = 'Fenetre_Gauche', x = 112, y = 56, w = 48, h = 88,",
    ).replace(
        "{ name = 'Fenetre_Droite', x = 1056, y = 168, w = 144, h = 264,",
        "{ name = 'Fenetre_Droite', x = 352, y = 56, w = 48, h = 88,",
    )
    decors_path.write_text(dtxt, encoding="utf-8")

    # 8. Mettre à jour le commentaire d'en-tête de `guilde_destiny_accueil/init.lua`
    acc_lua = SCRIPT_DIR / "ground/guilde_destiny_accueil/init.lua"
    ltxt = acc_lua.read_text(encoding="utf-8")
    ltxt = ltxt.replace("1536x1152 haute résolution 1:1 sans perte", "512x384 échelle native DS 1x (64x48 tuiles 8x8)")
    acc_lua.write_text(ltxt, encoding="utf-8")

    print(
        f"[OK] guilde_destiny_accueil 1x (64x48 = 512x384 px) : "
        f"arch={n_arch} tuiles, verdure_cellules={len(verd_refs)} (banque={n_verd}), "
        f"supports={len(arch_refs[2])}, BFS_16x16={len(seen)} positions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
