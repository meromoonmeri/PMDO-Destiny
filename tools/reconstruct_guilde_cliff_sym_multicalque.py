#!/usr/bin/env python3
"""
1. Symétrie exacte des colonnes rocheuses & courbure à gauche de l'escalier central de `guilde_cliff_{jour,aube,crepuscule,nuit}`
   (`x = 0..207` symétrisé depuis `x = 272..479` sur `y = 152..519`, SANS régénérer la falaise), avec adaptation sans couture
   de `00_Mer_Animee_12Phases` (900 cellules 12 phases intactes) et organisation multicalque (`Floor`, `Walls`, `Shadows`,
   `Objects Under`, `Objects`, `Objects Over`, `Fringe`, `Supports`).
2. Reconstruction pixel par pixel style Nintendo DS (Explorers of Sky) de `Guilde_HD` (fermée, porte ouverte, ombre au sol)
   sur les 4 ambiances (`Jour`, `Aube`, `Crepuscule`, `Nuit`) : ~34 couleurs DS nettes, clusters cohérents, sel-out chauds,
   synchronisation `.png` + `.dir` + `.tile` (`build_guilde_hd_tiles.py`).
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
SPRITES_DIR = ROOT / "art/cliff-guilde/sprites"
OBJ_DIR = ROOT / "game/Content/Object"
TILE_DIR = ROOT / "game/Content/Tile"
GROUND_DIR = ROOT / "game/Data/Ground"

sys.path.insert(0, str(ROOT / "tools"))
import adapt_guilde_cliff_sea_from_promontoire as sea_adapter  # noqa: E402

AMBIANCES = [
    ("jour", "Jour"),
    ("aube", "Aube"),
    ("crepuscule", "Crepuscule"),
    ("nuit", "Nuit"),
]

WORLD_TINTS = {
    "jour": np.array([1.0, 1.0, 1.0], dtype=np.float32),
    "aube": np.array([224.0, 203.0, 212.0], dtype=np.float32) / 255.0,
    "crepuscule": np.array([179.0, 146.0, 173.0], dtype=np.float32) / 255.0,
    "nuit": np.array([97.0, 118.0, 159.0], dtype=np.float32) / 255.0,
}

GHD_RAMPS = {
    "leaf_green": np.array([
        [20, 42, 18],    # 0: pine sel-out
        [30, 64, 25],    # 1: deep canopy shadow
        [44, 90, 33],    # 2: forest leaf shadow
        [62, 118, 41],   # 3: emerald leaf mid
        [86, 146, 49],   # 4: sunlit emerald leaf
        [116, 172, 58],  # 5: bright leaf highlight
        [150, 198, 70],  # 6: crisp leaf vein tip
    ], dtype=np.uint8),
    "leaf_gold": np.array([
        [48, 42, 14],    # 0: warm olive-amber sel-out
        [86, 72, 18],    # 1: olive leaf shadow
        [130, 104, 22],  # 2: golden-olive leaf
        [168, 136, 26],  # 3: warm amber-chartreuse leaf
        [198, 166, 34],  # 4: sunlit golden leaf
        [224, 196, 52],  # 5: bright chartreuse-gold vein
    ], dtype=np.uint8),
    "pebble": np.array([
        [48, 36, 42],    # 0: slate-plum stone sel-out
        [82, 63, 70],    # 1: stone shadow
        [118, 94, 102],  # 2: cool river stone mid
        [154, 128, 136], # 3: lit river pebble
        [190, 166, 172], # 4: pebble highlight
    ], dtype=np.uint8),
    "wood_bark": np.array([
        [36, 17, 12],    # 0: warm deep mahogany sel-out (ZERO #000000!)
        [58, 28, 18],    # 1: deep root crevice
        [84, 41, 25],    # 2: dark cedar bark shadow
        [112, 55, 32],   # 3: shaded terracotta-cedar root
        [140, 71, 39],   # 4: rich warm cedar midtone
        [168, 90, 47],   # 5: lit cedar root / door plank
        [194, 113, 58],  # 6: warm honey-cedar rail
        [216, 139, 73],  # 7: sunlit balcony plank
        [236, 168, 94],  # 8: crisp sunlit wood rim
    ], dtype=np.uint8),
    "wood_emblem": np.array([
        [68, 35, 20],    # 0: carved wing groove
        [122, 68, 37],   # 1: emblem shadow
        [170, 103, 54],  # 2: warm honey mid
        [206, 138, 76],  # 3: carved Winged-Egg face
        [236, 174, 104], # 4: wing highlight
    ], dtype=np.uint8),
    "recess": np.array([
        [24, 12, 9],     # 0: deepest interior
        [40, 20, 14],    # 1: interior shadow
        [60, 31, 21],    # 2: dim threshold
    ], dtype=np.uint8),
}


def write_dir_object(path: Path, rgba_arr: np.ndarray) -> None:
    h, w, _ = rgba_arr.shape
    buf = io.BytesIO()
    Image.fromarray(rgba_arr, "RGBA").save(buf, format="PNG", optimize=True)
    png = buf.getvalue()
    path.write_bytes(struct.pack("<q", len(png)) + png + struct.pack("<iiii", w, h, 0, 1))


def read_dir_rgba(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    (plen,) = struct.unpack_from("<q", raw, 0)
    return np.array(Image.open(io.BytesIO(raw[8 : 8 + plen])).convert("RGBA"))


def reconstruct_ghd_ds_jour(rgba: np.ndarray) -> np.ndarray:
    h, w, _ = rgba.shape
    mask = rgba[..., 3] >= 112
    solid = rgba[..., 3] >= 235
    rgb = rgba[..., :3].astype(np.float32).copy()
    edge_semi = mask & (~solid)
    if np.any(edge_semi):
        _, idx = ndimage.distance_transform_edt(~solid, return_indices=True)
        rgb[edge_semi] = rgb[idx[0][edge_semi], idx[1][edge_semi]]

    L = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    lmin = ndimage.minimum_filter(L, size=3)
    lmax = ndimage.maximum_filter(L, size=3)
    span = lmax - lmin
    u = np.clip((L - lmin) / np.maximum(span, 1e-4), 0.0, 1.0)
    us = u * u * (3.0 - 2.0 * u)
    us = 0.35 * u + 0.65 * (us * us * (3.0 - 2.0 * us))
    gate = np.clip((span - 10.0) / 24.0, 0.0, 1.0)
    L_s = L + 0.60 * gate * ((lmin + us * span) - L)
    gain = (L_s + 1.0) / (L + 1.0)
    cmin = ndimage.minimum_filter(rgb, size=(3, 3, 1))
    cmax = ndimage.maximum_filter(rgb, size=(3, 3, 1))
    rgb_s = np.clip(rgb * gain[..., None], cmin, cmax)

    r, g, b = rgb_s[..., 0], rgb_s[..., 1], rgb_s[..., 2]
    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    is_green = mask & (((g > r + 4.0) & (g > b + 10.0)) | ((yy < 135) & (g >= r - 6.0) & (g > b + 18.0) & (r < 140.0)))

    wood_stump_keepout = ((xx >= 46) & (xx <= 92) & (yy >= 12) & (yy <= 56)) | ((xx >= 168) & (xx <= 204) & (yy >= 28) & (yy <= 62))
    yellow_ness = 0.5 * (r + g) - b
    g_over_r = g / np.maximum(r, 1.0)
    is_gold_leaf = mask & (~is_green) & (~wood_stump_keepout) & (yy < 146) & (
        ((yellow_ness > 48.0) & (g_over_r >= 0.65) & (b < 58.0) & (lum >= 55.0))
        | ((xx >= 115) & (yy >= 14) & (yy <= 122) & (b < 42.0) & (g_over_r >= 0.56) & (yellow_ness > 52.0))
    )
    is_gold_leaf = ndimage.binary_closing(is_gold_leaf, structure=np.ones((2, 2), dtype=bool)) & mask & (~is_green) & (~wood_stump_keepout) & (yy < 146)

    door_step_keepout = (xx >= 96) & (xx <= 166) & (yy >= 192)
    is_pebble = mask & (~is_green) & (~is_gold_leaf) & (~door_step_keepout) & (yy >= 102) & ((g - b) <= 14.0) & ((r - b) <= 58.0) & (lum >= 54.0)
    lbl_p, np_cnt = ndimage.label(is_pebble)
    if np_cnt > 0:
        sz_p = ndimage.sum(is_pebble, lbl_p, range(1, np_cnt + 1))
        is_pebble = np.isin(lbl_p, np.where(sz_p >= 4)[0] + 1)
    is_pebble = is_pebble | (ndimage.binary_dilation(is_pebble, iterations=1) & mask & (~is_green) & (~door_step_keepout) & ((g - b) <= 16.0) & (lum >= 42.0))

    is_recess = mask & (~is_green) & (~is_gold_leaf) & (~is_pebble) & (lum < 30.0) & (yy >= 88)
    in_egg = (xx >= 92) & (xx <= 170) & (yy >= 180) & (yy <= 223)
    is_emblem = mask & (~is_green) & (~is_gold_leaf) & (~is_pebble) & (~is_recess) & in_egg & (lum >= 102.0)
    is_bark = mask & (~is_green) & (~is_gold_leaf) & (~is_pebble) & (~is_recess) & (~is_emblem)

    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., 3] = np.where(mask, 255, 0)

    def map_ramp(m: np.ndarray, ramp: np.ndarray, lo: float, hi: float, gamma: float = 1.0) -> None:
        if not np.any(m):
            return
        n = len(ramp)
        t = np.clip((lum[m] - lo) / max(hi - lo, 1.0), 0.0, 1.0) ** gamma
        idx = np.clip(np.floor(t * (n - 0.001)).astype(np.int32), 0, n - 1)
        out[m, :3] = ramp[idx]

    map_ramp(is_green, GHD_RAMPS["leaf_green"], 24.0, 148.0, 0.95)
    map_ramp(is_gold_leaf, GHD_RAMPS["leaf_gold"], 42.0, 176.0, 0.95)
    map_ramp(is_pebble, GHD_RAMPS["pebble"], 50.0, 166.0, 0.95)
    map_ramp(is_recess, GHD_RAMPS["recess"], 8.0, 30.0, 1.0)
    map_ramp(is_emblem, GHD_RAMPS["wood_emblem"], 98.0, 178.0, 0.92)
    map_ramp(is_bark, GHD_RAMPS["wood_bark"], 22.0, 168.0, 0.94)

    out_lum = 0.299 * out[..., 0] + 0.587 * out[..., 1] + 0.114 * out[..., 2]
    editable = mask & (out_lum >= 58.0)
    codes = (out[..., 0].astype(np.int32) << 16) | (out[..., 1].astype(np.int32) << 8) | out[..., 2].astype(np.int32)
    s8 = np.ones((3, 3), dtype=bool)
    speck = np.zeros((h, w), dtype=bool)
    for c in np.unique(codes[editable]):
        cm = editable & (codes == c)
        lb, nc = ndimage.label(cm, structure=s8)
        if nc > 0:
            sz = ndimage.sum(cm, lb, range(1, nc + 1))
            s1 = np.where(sz == 1)[0] + 1
            if len(s1):
                speck |= np.isin(lb, s1)
    if np.any(speck):
        ys_s, xs_s = np.where(speck)
        cleaned = out.copy()
        for y, x in zip(ys_s, xs_s):
            y0, y1 = max(0, y - 1), min(h, y + 2)
            x0, x1 = max(0, x - 1), min(w, x + 2)
            nb = mask[y0:y1, x0:x1] & (~speck[y0:y1, x0:x1])
            if np.any(nb):
                vals, cnts = np.unique(codes[y0:y1, x0:x1][nb], return_counts=True)
                bc = int(vals[int(np.argmax(cnts))])
                cleaned[y, x, :3] = [(bc >> 16) & 255, (bc >> 8) & 255, bc & 255]
        out = cleaned

    eroded = ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool))
    sil = mask & (~eroded)
    out[sil & is_green, :3] = GHD_RAMPS["leaf_green"][0]
    out[sil & is_gold_leaf, :3] = GHD_RAMPS["leaf_gold"][0]
    out[sil & is_pebble, :3] = GHD_RAMPS["pebble"][0]
    out[sil & (~is_green) & (~is_gold_leaf) & (~is_pebble), :3] = GHD_RAMPS["wood_bark"][0]
    return out


def tint_ds_rgba(arr: np.ndarray, amb: str) -> np.ndarray:
    if amb == "jour":
        return arr.copy()
    out = arr.copy()
    nz = out[..., 3] > 0
    out[nz, :3] = np.clip(np.round(out[nz, :3].astype(np.float32) * WORLD_TINTS[amb][None, :]), 0, 255).astype(np.uint8)
    return out


def reconstruct_shadow_ds(rgba: np.ndarray) -> np.ndarray:
    """Crisp 2-step DS ground shadow (eliminates blurry Gaussian shadow gradient)."""
    out = np.zeros_like(rgba)
    a = rgba[..., 3]
    inner = a >= 84
    outer = (a >= 28) & (~inner)
    # Warm dark umber shadow (zero pure black, zero magenta)
    out[inner] = [28, 18, 14, 112]
    out[outer] = [28, 18, 14, 56]
    return out


def rebuild_guilde_hd_all() -> None:
    # Read from canonical Jour master in OBJ_DIR (or SPRITES_DIR)
    j_closed_src = read_dir_rgba(OBJ_DIR / "Guilde_HD_Jour.dir")
    j_open_src = read_dir_rgba(OBJ_DIR / "Guilde_HD_Porte_Ouverte_Jour.dir")

    ds_closed_jour = reconstruct_ghd_ds_jour(j_closed_src)
    ds_open_raw = reconstruct_ghd_ds_jour(j_open_src)
    ds_open_jour = ds_closed_jour.copy()
    ds_open_jour[164:240, 74:188] = ds_open_raw[164:240, 74:188]

    Image.fromarray(ds_closed_jour, "RGBA").save(SPRITES_DIR / "guilde_hd_fermee_master.png")
    Image.fromarray(ds_open_jour, "RGBA").save(SPRITES_DIR / "guilde_hd_porte_ouverte_master.png")

    for amb, cap in AMBIANCES:
        c_amb = tint_ds_rgba(ds_closed_jour, amb)
        o_amb = tint_ds_rgba(ds_open_jour, amb)
        sh_src = read_dir_rgba(OBJ_DIR / f"Guilde_HD_Ombre_{cap}.dir")
        sh_ds = reconstruct_shadow_ds(sh_src)

        Image.fromarray(c_amb, "RGBA").save(SPRITES_DIR / f"guilde_hd_{amb}.png")
        Image.fromarray(o_amb, "RGBA").save(SPRITES_DIR / f"guilde_hd_porte_ouverte_{amb}.png")
        Image.fromarray(sh_ds, "RGBA").save(SPRITES_DIR / f"guilde_hd_ombre_{amb}.png")

        write_dir_object(OBJ_DIR / f"Guilde_HD_{cap}.dir", c_amb)
        write_dir_object(OBJ_DIR / f"Guilde_HD_Porte_Ouverte_{cap}.dir", o_amb)
        write_dir_object(OBJ_DIR / f"Guilde_HD_Ombre_{cap}.dir", sh_ds)
        n_col = len(np.unique(c_amb[c_amb[..., 3] > 0, :3], axis=0))
        print(f"[OK] Guilde_HD {cap}: {n_col} DS colors (.png + .dir)")

    # Synchronize the 4 Guilde_HD_*.tile sheets via build_guilde_hd_tiles.py
    subprocess.run([sys.executable, str(ROOT / "tools/build_guilde_hd_tiles.py")], check=True)


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


def rebuild_guilde_cliff_sym_and_multicalque() -> None:
    GW, GH = 60, 65
    W, H = 480, 520

    for amb, cap in AMBIANCES:
        g_path = GROUND_DIR / f"guilde_cliff_{amb}.rsground"
        g_full = json.loads(g_path.read_text(encoding="utf-8-sig"))
        g_doc = g_full["Object"]
        sheet_name = f"Destiny_GuildeCliff_{cap}_059"
        bank = sea_adapter.decode_tile_sheet(TILE_DIR / f"{sheet_name}.tile")

        # Reconstruct current peninsula RGBA from all non-sea layers (idempotent if re-run!)
        cliff_rgba = np.zeros((H, W, 4), dtype=np.uint8)
        for lyr in g_doc["Layers"][1:]:
            for tx in range(GW):
                for ty in range(GH):
                    tl = lyr["Tiles"][tx][ty].get("Layers", [])
                    if tl and tl[0].get("Frames"):
                        loc = tl[0]["Frames"][0]["TexLoc"]
                        patch = bank[(loc["X"], loc["Y"])]
                        a = patch[..., 3:4] > 0
                        cliff_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = np.where(
                            a, patch, cliff_rgba[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
                        )

        # EXACT SYMMETRY LEFT OF CENTRAL STAIRCASE (WITHOUT regenerating the cliff!):
        # Central staircase is x = 208..271 (width 64, centered at 239.5).
        # Left flank x = 0..207 (width 208) is mirrored from right flank x = 272..479 (width 208)!
        sym_cliff = cliff_rgba.copy()
        sym_cliff[152:, :208] = cliff_rgba[152:, 272:][:, ::-1]

        # Encode symmetric peninsula into `Destiny_GuildeCliff_<Cap>_059.tile`
        cell_locs = encode_dedup_tile_bank(sheet_name, sym_cliff)

        # First write temporary 2-layer layout so `adapt_sea_to_guilde_cliff` reads exact symmetric `Layers[1]` alpha!
        full_cliff_grid = make_empty_grid(GW, GH)
        for (tx, ty), (lx, ly) in cell_locs.items():
            full_cliff_grid[tx][ty] = {
                "AutoTileset": "",
                "Associates": [],
                "Layers": [{"Frames": [{"Sheet": sheet_name, "TexLoc": {"X": lx, "Y": ly}}], "FrameLength": 60}],
                "NeighborCode": 0,
            }
        g_doc["Layers"] = [
            g_doc["Layers"][0],
            {"Name": "01_Guilde_Cliff", "Layer": 0, "Visible": True, "Tiles": full_cliff_grid},
        ]
        g_path.write_text(json.dumps(g_full, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

        # Re-adapt 12-phase sea cleanly to the symmetric cliff flanks
        sea_adapter.adapt_sea_to_guilde_cliff(amb, cap)

        # Reload updated .rsground (with exact 900-cell 12-phase `00_Mer_Animee_12Phases`) and split peninsula into
        # Halcyon-style multicalque layers after `00_Mer_Animee_12Phases`:
        #   [0] 00_Mer_Animee_12Phases (Layer=0)
        #   [1] Floor                  (Layer=0: walkable grassy plateau + central wooden staircase)
        #   [2] Walls                  (Layer=0: symmetric sculpted cliff rock columns, rim & outer ledges)
        #   [3] Shadows                (Layer=0: empty, ready for manual ground shadows)
        #   [4] Objects Under          (Layer=0: empty, ready for manual placement)
        #   [5] Objects                (Layer=0: empty, ready for manual placement)
        #   [6] Objects Over           (Layer=0: empty, ready for manual placement)
        #   [7] Fringe                 (Layer=4: overhead empty)
        #   [8] Supports               (Layer=4: overhead empty)
        g_full = json.loads(g_path.read_text(encoding="utf-8-sig"))
        g_doc = g_full["Object"]
        obs = g_doc["obstacles"]
        walk_tile = np.array([[obs[tx][ty]["Tags"] == 0 for ty in range(GH)] for tx in range(GW)], dtype=bool)
        # Include plateau tiles under the Guild building footprint (tx=18..41, ty=20..31) & staircase (tx=26..33, ty=31..64) in Floor!
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
        fl_n = sum(1 for tx in range(GW) for ty in range(GH) if floor_grid[tx][ty].get("Layers"))
        wa_n = sum(1 for tx in range(GW) for ty in range(GH) if walls_grid[tx][ty].get("Layers"))
        print(f"[OK] guilde_cliff_{amb}: sym left-of-stairs + multicalque (sea={sea_n}, Floor={fl_n}, Walls={wa_n})")


if __name__ == "__main__":
    rebuild_guilde_hd_all()
    rebuild_guilde_cliff_sym_and_multicalque()
