#!/usr/bin/env python3
"""
Construit les 4 ambiances de `guilde_cliff_{jour,aube,crepuscule,nuit}` (480x520 px = 60x65 tuiles) :
1. Conserve la Guilde 7.1 (tronc brun sans cailloux mauves : `Guilde_HD_*` + `Guilde_HD_Porte_Ouverte_*`)
   et restaure l'ombre verte 4 tons par ambiance (`Guilde_HD_Ombre_*` + `guilde_hd_ombre_*.png`),
   puis resynchronise les 4 banques `Guilde_HD_*.tile` via `tools/build_guilde_hd_tiles.py` (0.0 px d'écart).
2. Remplace le mur rocheux kaléidoscopique sud et la spline fondue de `guilde_cliff_*` par une suite
   symétrique de bastions cylindriques courbés authentiques style Nintendo DS / Étang du Doyen :
     - [64..96)   : bastion courbe gauche externe (32 px, crête haute y ~ 260)
     - [96..128)  : bastion courbe gauche médian  (32 px, crête y ~ 284)
     - [128..192) : grand bastion courbe gauche   (64 px, crête y ~ 316)
     - [192..288) : piliers arrondis + escalier central en pierre (96 px, marches x=216..264 dès y=352)
     - [288..352) : grand bastion courbe droit    (64 px, crête y ~ 316)
     - [352..384) : bastion courbe droit médian   (32 px, crête y ~ 284)
     - [384..416) : bastion courbe droit externe  (32 px, crête haute y ~ 260)
   Chaque bastion conserve son briquetage horizontal DS non-kaléidoscopique et est prolongé sans couture
   jusqu'en y = 520 (pas de répétition 48 px sur les assises de pierre, 16 px exact à 0.00 d'écart sur les marches),
   tout en préservant à 100 % la silhouette extérieure de la péninsule et les 900 cellules `00_Mer_Animee_12Phases`.
"""
from __future__ import annotations

import io
import json
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import adapt_guilde_cliff_sea_from_promontoire as sea_adapter  # noqa: E402
import lib_tiles  # noqa: E402

SPRITES_DIR = ROOT / "art/cliff-guilde/sprites"
OBJ_DIR = ROOT / "game/Content/Object"
TILE_DIR = ROOT / "game/Content/Tile"
GROUND_DIR = ROOT / "game/Data/Ground"

AMBIANCES = [
    ("jour", "Jour"),
    ("aube", "Aube"),
    ("crepuscule", "Crepuscule"),
    ("nuit", "Nuit"),
]


def read_dir_rgba(raw: bytes) -> np.ndarray:
    (plen,) = struct.unpack_from("<q", raw, 0)
    return np.array(Image.open(io.BytesIO(raw[8 : 8 + plen])).convert("RGBA"))


def write_dir_rgba(path: Path, arr: np.ndarray) -> None:
    h, w, _ = arr.shape
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, format="PNG", optimize=True)
    png = buf.getvalue()
    path.write_bytes(struct.pack("<q", len(png)) + png + struct.pack("<iiii", w, h, 0, 1))


def restore_4tone_green_guild_shadows() -> None:
    """Restaure les ombres vertes 4 tons par ambiance de c2766e54 et synchronise Guilde_HD_*.tile."""
    for amb, cap in AMBIANCES:
        dir_rel = f"game/Content/Object/Guilde_HD_Ombre_{cap}.dir"
        raw = subprocess.check_output(["git", "show", f"c2766e54:{dir_rel}"], cwd=ROOT)
        arr = read_dir_rgba(raw)
        assert arr.shape == (262, 262, 4), (amb, arr.shape)
        Image.fromarray(arr, "RGBA").save(SPRITES_DIR / f"guilde_hd_ombre_{amb}.png")
        write_dir_rgba(OBJ_DIR / f"Guilde_HD_Ombre_{cap}.dir", arr)
    subprocess.run([sys.executable, str(ROOT / "tools/build_guilde_hd_tiles.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/build_guilde_hd_tiles.py"), "--check"], cwd=ROOT, check=True)
    print("[OK] Ombres vertes 4 tons restaurées et Guilde_HD_*.tile synchronisées (0.0 px).")


def render_etang_layer7(amb: str, cap: str) -> np.ndarray:
    doc = json.loads((GROUND_DIR / f"etangdudoyen_{amb}.rsground").read_text(encoding="utf-8-sig"))["Object"]
    _, tiles = lib_tiles.read_tilesheet(TILE_DIR / f"Destiny_Etang_Doyen_{cap}.tile")
    lyr = doc["Layers"][7]["Tiles"]
    canvas = Image.new("RGBA", (768, 576), (0, 0, 0, 0))
    for tx in range(96):
        for ty in range(72):
            for tl in lyr[tx][ty].get("Layers", []):
                fr = (tl.get("Frames") or [None])[0]
                if not fr or not fr.get("Sheet"):
                    continue
                loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                if loc in tiles:
                    canvas.alpha_composite(tiles[loc], (tx * 8, ty * 8))
    return np.array(canvas)


def place_bastion_slice(
    overlay: np.ndarray,
    block_rgba: np.ndarray,
    x_dst_start: int,
    y_dst_offset: int,
    is_stair_block: bool = False,
) -> None:
    """
    Pose un bloc complet de bastion DS (`block_rgba` de largeur 32, 64 ou 96 px) en `x_dst_start`
    avec décalage vertical `y_dst_offset`, et prolonge ses assises de briques sans couture jusqu'en bas (`H = 520`).
    """
    H, W, _ = overlay.shape
    bh, bw, _ = block_rgba.shape
    for dx in range(bw):
        x = x_dst_start + dx
        if not (0 <= x < W):
            continue
        col = block_rgba[:, dx]
        ys = np.where(col[:, 3] > 0)[0]
        if not len(ys):
            continue
        y_top = int(ys.min())
        y_bot = int(ys.max())

        if is_stair_block:
            valid_bot = y_bot
            # Marches centrales (dx = 20..76 => x = 212..268) : période exacte 16 px (0.00 diff !)
            # Piliers d'escalier encadrants : période 48 px (2 cycles de 24 px)
            period = 16 if 20 <= dx < 76 else 48
        else:
            # Exclure les 8 px tout en bas du bastion d'Étang du Doyen (bordure d'appui dans l'herbe basse)
            valid_bot = max(y_top + 40, y_bot - 8)
            period = 48

        for ys_i in range(y_top, valid_bot + 1):
            yg = ys_i + y_dst_offset
            if 0 <= yg < H and col[ys_i, 3] > 0:
                overlay[yg, x] = col[ys_i]

        valid_bot_g = valid_bot + y_dst_offset
        # Fenêtre de répétition prise au coeur franc de la maçonnerie (hors couronne dentelée et hors pied)
        if is_stair_block and 20 <= dx < 76:
            ref_end = valid_bot
            ref_start = ref_end - 16 + 1
        else:
            # Trouver la meilleure période (24 ou 48 px) minimisant le saut RGB entre valid_bot et ref_start !
            best_start = max(y_top + 18, valid_bot - 24 + 1)
            best_err = 1e9
            for cand_p in (24, 48):
                cand_s = valid_bot - cand_p + 1
                if cand_s >= y_top + 16:
                    # Comparer les 2 lignes de raccord pour éliminer toute couture horizontale
                    err = float(np.abs(col[valid_bot, :3].astype(int) - col[cand_s - 1, :3].astype(int)).mean())
                    if err < best_err:
                        best_err = err
                        best_start = cand_s
            ref_end = valid_bot
            ref_start = best_start

        span = max(1, ref_end - ref_start + 1)
        for yg in range(max(0, valid_bot_g + 1), H):
            src_y = ref_start + ((yg - (valid_bot_g + 1)) % span)
            px = col[src_y].copy()
            px[3] = 255
            overlay[yg, x] = px


def build_bastion_wall_overlay(etang_l7: np.ndarray, W: int = 480, H: int = 520) -> np.ndarray:
    """
    Assemble les 7 travées complètes (sans aucune coupe au milieu d'un bastion !) sur x = 56..424 :
      - [56..96)   : épaule côtière + bastion gauche externe (crête y ~ 256)
      - [96..128)  : bastion gauche médian 32 px (`sub[:, 96:128]`, crête y ~ 284)
      - [128..192) : grand bastion gauche 64 px (`sub[:, 128:192]`, crête y ~ 316)
      - [192..288) : piliers + escalier central 96 px (`sub[:, 192:288]`, marches y = 352..520)
      - [288..352) : grand bastion droit 64 px (`sub[:, 288:352]`, crête y ~ 316)
      - [352..384) : bastion droit médian 32 px (`sub[:, 352:384]`, crête y ~ 284)
      - [384..424) : bastion droit externe + épaule côtière (crête y ~ 256)
    """
    sub = etang_l7[320:576, 144:624].copy()  # shape (256, 480, 4), y_et = y_sub + 320
    overlay = np.zeros((H, W, 4), dtype=np.uint8)
    base_offset = 320 - 116  # +204 => y_et=468 tombe exactement en y_gc=352 !

    # 1. Travée centrale escalier + piliers [192..288)
    place_bastion_slice(overlay, sub[:, 192:288], 192, base_offset, is_stair_block=True)

    # 2. Grands bastions intérieurs 64 px : gauche [128..192) et droite [288..352)
    place_bastion_slice(overlay, sub[:, 128:192], 128, base_offset)
    place_bastion_slice(overlay, sub[:, 288:352], 288, base_offset)

    # 3. Bastions médians 32 px : gauche [96..128) (`top_y_et=400` -> `y_gc=284`)
    #    et droite [352..384) (`sub[:, 352:384]` a `top_y_et=402` -> aligné à +0 px sur `y_gc=286` !)
    place_bastion_slice(overlay, sub[:, 96:128], 96, base_offset)
    place_bastion_slice(overlay, sub[:, 352:384], 352, base_offset - 2)

    # 4. Bastions externes côtiers :
    #    - Gauche [64..96) : bastion complet 32 px `sub[:, 96:128]` remonté d'un palier DS (-28 px -> crête `y_gc=256`)
    #    - Droite [384..416) : bastion complet 32 px `sub[:, 352:384]` remonté d'un palier DS (-30 px -> crête `y_gc=256`)
    place_bastion_slice(overlay, sub[:, 96:128], 64, base_offset - 28)
    place_bastion_slice(overlay, sub[:, 352:384], 384, base_offset - 30)

    # 5. Épaulements d'extrême bord marin [48..64) et [416..432) (au cas où la silhouette `peninsula_alpha`
    #    déborde légèrement entre x=56..63 ou x=416..423 vers ty=26..34) :
    place_bastion_slice(overlay, sub[:, 0:16], 48, base_offset - 52)
    place_bastion_slice(overlay, sub[:, 464:480], 416, base_offset - 52)

    return overlay


def make_empty_grid(gw: int, gh: int) -> list[list[dict]]:
    return [[{"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1} for _ in range(gh)] for _ in range(gw)]


def encode_dedup_tile_bank(sheet_name: str, rgba_canvas: np.ndarray, cols: int = 32) -> dict[tuple[int, int], tuple[int, int]]:
    h, w, _ = rgba_canvas.shape
    gw, gh = w // 8, h // 8
    patch_to_loc: dict[bytes, tuple[int, int]] = {}
    ordered: list[tuple[int, int, np.ndarray]] = []

    zero = np.zeros((8, 8, 4), dtype=np.uint8)
    patch_to_loc[zero.tobytes()] = (0, 0)
    ordered.append((0, 0, zero))

    cell_locs: dict[tuple[int, int], tuple[int, int]] = {}
    for tx in range(gw):
        for ty in range(gh):
            patch = rgba_canvas[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
            if int(patch[..., 3].max()) == 0:
                continue
            key = patch.tobytes()
            loc = patch_to_loc.get(key)
            if loc is None:
                idx = len(ordered)
                loc = (idx % cols, idx // cols)
                patch_to_loc[key] = loc
                ordered.append((loc[0], loc[1], patch.copy()))
            cell_locs[(tx, ty)] = loc

    blobs = [sea_adapter.premultiply_patch_bytes(p) for _, _, p in ordered]
    out = bytearray(struct.pack("<ii", 8, len(ordered)))
    off = 8 + 16 * len(ordered)
    for (lx, ly, _), blob in zip(ordered, blobs):
        out += struct.pack("<iiq", lx, ly, off)
        off += 8 + len(blob)
    for blob in blobs:
        out += struct.pack("<q", len(blob)) + blob
    (TILE_DIR / f"{sheet_name}.tile").write_bytes(bytes(out))
    return cell_locs


def rebuild_guilde_cliff_bastions() -> None:
    GW, GH = 60, 65
    W, H = 480, 520

    for amb, cap in AMBIANCES:
        g_path = GROUND_DIR / f"guilde_cliff_{amb}.rsground"
        raw_head = subprocess.check_output(["git", "show", f"HEAD:game/Data/Ground/guilde_cliff_{amb}.rsground"], cwd=ROOT)
        g_full = json.loads(raw_head.decode("utf-8-sig"))
        g_doc = g_full["Object"]

        bg = g_doc.get("Background")
        if isinstance(bg, dict) and isinstance(bg.get("Layers"), list):
            for bgl in bg["Layers"]:
                inner = bgl.get("BG")
                if isinstance(inner, dict) and "$type" in inner:
                    del inner["$type"]

        sheet_name = f"Destiny_GuildeCliff_{cap}_059"
        raw_tile_head = subprocess.check_output(["git", "show", f"HEAD:game/Content/Tile/{sheet_name}.tile"], cwd=ROOT)
        tmp_tile = Path(f"/var/tmp/head_{sheet_name}.tile")
        tmp_tile.write_bytes(raw_tile_head)
        bank = sea_adapter.decode_tile_sheet(tmp_tile)

        orig_rgba = np.zeros((H, W, 4), dtype=np.uint8)
        for lyr in g_doc["Layers"][1:]:
            for tx in range(GW):
                for ty in range(GH):
                    tl = lyr["Tiles"][tx][ty].get("Layers", [])
                    if tl and tl[0].get("Frames"):
                        loc = tl[0]["Frames"][0]["TexLoc"]
                        patch = bank[(loc["X"], loc["Y"])]
                        a = patch[..., 3:4] > 0
                        orig_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = np.where(
                            a, patch, orig_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
                        )

        peninsula_alpha = orig_rgba[..., 3].copy()

        # Bloc d'herbe pure 48x48 du plateau
        grass_tile = orig_rgba[288:336, 192:240, :3].copy()

        # En haut du plateau (y < 256), conserver le liseré côtier d'origine sur 6 px ;
        # en bas (y >= 256), les bastions rocheux vont jusqu'au bord exact de la péninsule (avec sel-out rocheux 2 px) !
        top_rim_keep = (peninsula_alpha > 0) & (~ndimage.binary_erosion(peninsula_alpha == 255, structure=np.ones((3, 3), dtype=bool), iterations=6))
        outer_2px_edge = (peninsula_alpha > 0) & (~ndimage.binary_erosion(peninsula_alpha > 128, structure=np.ones((3, 3), dtype=bool), iterations=2))

        composed = orig_rgba.copy()
        for y in range(244, H):
            for x in range(W):
                if peninsula_alpha[y, x] > 0 and not (y < 260 and top_rim_keep[y, x]):
                    composed[y, x, :3] = grass_tile[(y - 288) % 48, (x - 192) % 48]
                    composed[y, x, 3] = peninsula_alpha[y, x]

        etang_l7 = render_etang_layer7(amb, cap)
        bastion_rgba = build_bastion_wall_overlay(etang_l7, W=W, H=H)

        # Couleur sel-out sombre chaude extraite des crevasses DS de cette ambiance
        rock_dark_rgb = np.percentile(bastion_rgba[bastion_rgba[..., 3] == 255, :3], 8, axis=0).astype(np.uint8)

        for y in range(236, H):
            for x in range(W):
                if peninsula_alpha[y, x] == 0:
                    continue
                if y < 256 and top_rim_keep[y, x]:
                    continue
                ba = int(bastion_rgba[y, x, 3])
                if ba == 255:
                    composed[y, x, :3] = bastion_rgba[y, x, :3]
                elif ba > 0:
                    af = ba / 255.0
                    composed[y, x, :3] = np.clip(
                        np.round(bastion_rgba[y, x, :3].astype(np.float32) * af + composed[y, x, :3].astype(np.float32) * (1.0 - af)),
                        0,
                        255,
                    ).astype(np.uint8)
                # Liseré sel-out rocheux propre de 1-2 px là où le flanc vertical des bastions touche la mer
                if ba > 128 and outer_2px_edge[y, x] and y >= 262:
                    composed[y, x, :3] = np.clip(
                        np.round(0.65 * rock_dark_rgb.astype(np.float32) + 0.35 * composed[y, x, :3].astype(np.float32)),
                        0,
                        255,
                    ).astype(np.uint8)

        composed[..., 3] = peninsula_alpha

        # Grille d'obstacles 60x65 recalibrée sur les bastions courbés
        obs = g_doc["obstacles"]
        coastal_interior = ndimage.binary_erosion(peninsula_alpha == 255, structure=np.ones((3, 3), dtype=bool), iterations=6)
        bastion_tile = np.zeros((GW, GH), dtype=bool)
        for tx in range(GW):
            for ty in range(GH):
                patch_b = bastion_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8, 3]
                if int((patch_b > 96).sum()) >= 16:
                    bastion_tile[tx, ty] = True

        for tx in range(GW):
            for ty in range(GH):
                if ty < 25 or ty >= 64:
                    obs[tx][ty]["Tags"] = 1 if obs[tx][ty]["Tags"] == 0 else obs[tx][ty]["Tags"]
                    continue
                if 27 <= tx <= 32 and 31 <= ty <= 63:
                    obs[tx][ty]["Tags"] = 0
                    continue
                if 16 <= tx <= 43 and 20 <= ty <= 30:
                    if obs[tx][ty]["Tags"] == 0:
                        obs[tx][ty]["Tags"] = 2
                    continue
                if ty <= 33:
                    continue
                in_coast = bool(coastal_interior[ty * 8 + 4, tx * 8 + 4])
                if in_coast and not bastion_tile[tx, ty] and ty <= 44:
                    obs[tx][ty]["Tags"] = 0
                else:
                    if obs[tx][ty]["Tags"] == 0:
                        obs[tx][ty]["Tags"] = 2

        cell_locs = encode_dedup_tile_bank(sheet_name, composed)
        walk_tile = np.array([[obs[tx][ty]["Tags"] == 0 for ty in range(GH)] for tx in range(GW)], dtype=bool)
        floor_tile = ndimage.binary_dilation(walk_tile, iterations=1)
        floor_tile[18:42, 20:33] = True
        floor_tile[26:34, 31:65] = True

        floor_grid = make_empty_grid(GW, GH)
        walls_grid = make_empty_grid(GW, GH)
        for (tx, ty), (lx, ly) in cell_locs.items():
            entry = {
                "AutoTileset": "",
                "Associates": [],
                "Layers": [{"Frames": [{"Sheet": sheet_name, "TexLoc": {"X": lx, "Y": ly}}], "FrameLength": 60}],
                "NeighborCode": 0,
            }
            if floor_tile[tx, ty]:
                floor_grid[tx][ty] = entry
            else:
                walls_grid[tx][ty] = entry

        g_doc["Layers"] = [
            g_doc["Layers"][0],
            {"Name": "Floor", "Layer": 0, "Visible": True, "Tiles": floor_grid},
            {"Name": "Walls", "Layer": 0, "Visible": True, "Tiles": walls_grid},
            {"Name": "Shadows", "Layer": 0, "Visible": True, "Tiles": make_empty_grid(GW, GH)},
            {"Name": "Objects Under", "Layer": 0, "Visible": True, "Tiles": make_empty_grid(GW, GH)},
            {"Name": "Objects", "Layer": 0, "Visible": True, "Tiles": make_empty_grid(GW, GH)},
            {"Name": "Objects Over", "Layer": 0, "Visible": True, "Tiles": make_empty_grid(GW, GH)},
            {"Name": "Fringe", "Layer": 4, "Visible": True, "Tiles": make_empty_grid(GW, GH)},
            {"Name": "Supports", "Layer": 4, "Visible": True, "Tiles": make_empty_grid(GW, GH)},
        ]
        g_path.write_text(json.dumps(g_full, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        sea_n = sum(1 for tx in range(GW) for ty in range(GH) if g_doc["Layers"][0]["Tiles"][tx][ty].get("Layers"))
        print(f"[OK] guilde_cliff_{amb}: bastions courbés DS complets sans coupe (sea={sea_n}, unique_tiles={len(cell_locs)})")


def main() -> int:
    restore_4tone_green_guild_shadows()
    rebuild_guilde_cliff_bastions()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
