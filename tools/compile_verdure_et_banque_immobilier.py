#!/usr/bin/env python3
"""
Compile :
  1. `Destiny_Guilde_Immobilier.tile` en disposition visuelle 2D intacte (`tx, ty` exacts de la planche `896x1000`),
     pour que l'utilisateur puisse sélectionner au rectangle n'importe quel tapis, drapeau, tableau de quête ou meuble
     directement dans l'éditeur de carte PMDO en jeu :
       - `ty = 0..124`   : Sprites complets avec leur ombre chaude de Guilde intégrée (pose en 1 clic).
       - `ty = 126..250` : Sprites seuls sans ombre.
       - `ty = 252..376` : Ombres chaudes seules.
     + Les 135 objets `.dir` individuels (`Guilde_Imm_*.dir` dans `game/Content/Object/`).
  2. `Destiny_Guilde_Verdure.tile` et l'intégration des Guirlandes de Verdure sur mesure sur leur propre calque dédié
     `Layers[4]` ("04 verdure separee", `Visible=True`) dans CHACUNE des 15 salles `.rsground`, tout en laissant les
     pièces non meublées (`Layers[5..6]` vides et propres) afin que l'utilisateur place lui-même ses objets en jeu.
"""
from __future__ import annotations

from collections import deque
import io
import json
import shutil
import struct
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = Path("/var/tmp/PMDO-Destiny") if Path("/var/tmp/PMDO-Destiny/game").exists() else Path(__file__).resolve().parents[1]
RESEAU = Path("/home/user/guilde_destiny_reseau") if Path("/home/user/guilde_destiny_reseau").exists() else (REPO / "art/guilde_destiny_reseau")
BASE_DIR = RESEAU / "cartes_base_sans_decors"
IMM_DIR = RESEAU / "immobilier_guilde"
VERD_DIR = RESEAU / "guirlandes_verdure"
VERD_DIR.mkdir(parents=True, exist_ok=True)

TILE_DIR = REPO / "game/Content/Tile"
GROUND_DIR = REPO / "game/Data/Ground"
ART_DEST = REPO / "art/guilde_destiny_reseau"


def sanitize_patch_anti_magenta(patch_rgba: np.ndarray) -> np.ndarray:
    p = patch_rgba.copy()
    nz = p[:, :, 3] > 0
    if nz.any():
        r = p[:, :, 0].astype(np.int16)
        g = p[:, :, 1].astype(np.int16)
        b = p[:, :, 2].astype(np.int16)
        bad = nz & ((r - g) > 33) & ((b - g) > 22)
        if bad.any():
            p[:, :, 1][bad] = np.maximum(p[:, :, 1][bad], (r[bad] - 31).astype(np.uint8))
    return p


def premultiply_png_bytes(patch_rgba: np.ndarray) -> bytes:
    arr = patch_rgba.astype(np.float32)
    alpha = arr[..., 3:4] / 255.0
    arr[..., :3] = np.clip(np.round(arr[..., :3] * alpha), 0, 255)
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def write_visual_2d_tile_sheet(sheet_name: str, rgba_sheet: np.ndarray, out_dir: Path) -> int:
    """Writes a `.tile` file preserving exact `(tx, ty)` 2D visual coordinates so sprites appear whole in PMDO's editor!"""
    h, w, _ = rgba_sheet.shape
    tw, th = w // 8, h // 8
    entries: list[tuple[int, int, bytes]] = []
    # Always include `(0, 0)` transparent anchor tile if `(0, 0)` is empty so `n_tiles >= 1`
    for ty in range(th):
        for tx in range(tw):
            patch = rgba_sheet[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
            if int(patch[:, :, 3].max()) == 0:
                if tx == 0 and ty == 0:
                    entries.append((0, 0, premultiply_png_bytes(patch)))
                continue
            entries.append((tx, ty, premultiply_png_bytes(sanitize_patch_anti_magenta(patch))))

    n_tiles = len(entries)
    out = bytearray()
    out += struct.pack("<ii", 8, n_tiles)
    off = 8 + n_tiles * 16
    for tx, ty, blob in entries:
        out += struct.pack("<iiq", tx, ty, off)
        off += 8 + len(blob)
    for _, _, blob in entries:
        out += struct.pack("<q", len(blob))
        out += blob
    (out_dir / f"{sheet_name}.tile").write_bytes(bytes(out))
    return n_tiles


class DedupTileBankBuilder:
    def __init__(self, sheet_name: str, cols: int = 32) -> None:
        self.sheet_name = sheet_name
        self.cols = cols
        self.patch_to_loc: dict[bytes, tuple[int, int]] = {}
        self.ordered_patches: list[tuple[int, int, np.ndarray]] = []
        zero = np.zeros((8, 8, 4), dtype=np.uint8)
        self.patch_to_loc[zero.tobytes()] = (0, 0)
        self.ordered_patches.append((0, 0, zero))

    def encode_rgba_layer(self, rgba_canvas: np.ndarray) -> list[list[dict]]:
        h, w, _ = rgba_canvas.shape
        tw, th = w // 8, h // 8
        grid = []
        for tx in range(tw):
            col = []
            for ty in range(th):
                patch = rgba_canvas[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
                if int(patch[:, :, 3].max()) == 0:
                    col.append({"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1})
                else:
                    p = sanitize_patch_anti_magenta(patch)
                    key = p.tobytes()
                    loc = self.patch_to_loc.get(key)
                    if loc is None:
                        idx = len(self.ordered_patches)
                        loc = (idx % self.cols, idx // self.cols)
                        self.patch_to_loc[key] = loc
                        self.ordered_patches.append((loc[0], loc[1], p))
                    col.append(
                        {
                            "AutoTileset": "",
                            "Associates": [],
                            "Layers": [{"Frames": [{"Sheet": self.sheet_name, "TexLoc": {"X": loc[0], "Y": loc[1]}}], "FrameLength": 60}],
                            "NeighborCode": 0,
                        }
                    )
            grid.append(col)
        return grid

    def write(self, out_dir: Path) -> int:
        n_tiles = len(self.ordered_patches)
        blobs = [premultiply_png_bytes(p) for _, _, p in self.ordered_patches]
        out = bytearray()
        out += struct.pack("<ii", 8, n_tiles)
        off = 8 + n_tiles * 16
        for (lx, ly, _), blob in zip(self.ordered_patches, blobs):
            out += struct.pack("<iiq", lx, ly, off)
            off += 8 + len(blob)
        for blob in blobs:
            out += struct.pack("<q", len(blob))
            out += blob
        (out_dir / f"{self.sheet_name}.tile").write_bytes(bytes(out))
        return n_tiles


def empty_tile_grid(tw: int, th: int) -> list[list[dict]]:
    return [[{"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1} for _ in range(th)] for _ in range(tw)]


def generate_room_garland_rgba(
    room_rgb: np.ndarray,
    windows: list[dict],
    north_arch_x: tuple[int, int] | None = None,
    split_gap_x: tuple[int, int] | None = None,
    seed: int = 7,
) -> np.ndarray:
    h, w, _ = room_rgb.shape
    rng = np.random.default_rng(seed)
    ext = (
        (np.abs(room_rgb[:, :, 0].astype(int) - 104) <= 6)
        & (np.abs(room_rgb[:, :, 1].astype(int) - 72) <= 6)
        & (np.abs(room_rgb[:, :, 2].astype(int) - 47) <= 6)
    )

    cornice_y = np.full(w, -1, dtype=int)
    for x in range(16, w - 16):
        non_ext = np.where(~ext[:, x])[0]
        if len(non_ext) < 40:
            continue
        yt = int(non_ext[0])
        if yt <= 6 or yt > int(h * 0.48):
            continue
        if split_gap_x is not None and split_gap_x[0] - 2 <= x <= split_gap_x[1] + 2:
            continue
        found_c = -1
        for y in range(yt + 8, min(int(h * 0.48), yt + 68)):
            r, g, b = int(room_rgb[y, x, 0]), int(room_rgb[y, x, 1]), int(room_rgb[y, x, 2])
            if r >= 156 and g >= 96 and b >= 38:
                found_c = y
                break
        cornice_y[x] = found_c if found_c != -1 else (yt + 20)

    valid_xs = np.where(cornice_y > 0)[0]
    if len(valid_xs) < 40:
        return np.zeros((h, w, 4), dtype=np.uint8)
    x_min, x_max = int(valid_xs[0]) + 10, int(valid_xs[-1]) - 10

    smooth_cy = np.interp(np.arange(w), valid_xs, cornice_y[valid_xs].astype(np.float32))
    smooth_cy = ndimage.gaussian_filter1d(smooth_cy, sigma=5.5)

    keepout = np.zeros((h, w), dtype=bool)
    win_spans = []
    for slot in windows:
        wx, wy, ww, wh = slot["x"], slot["y"], slot["w"], slot["h"]
        keepout[max(0, wy + 4) : min(h, wy + wh), max(0, wx + 3) : min(w, wx + ww - 3)] = True
        win_spans.append((wx, wx + ww, wy))
    if north_arch_x is not None:
        ax0, ax1 = north_arch_x
        y_k = 63 if (ax1 - ax0) >= 120 else (int(smooth_cy[(ax0 + ax1) // 2]) + 3)
        keepout[y_k:h, ax0 + 2 : ax1 - 2] = True
    if split_gap_x is not None:
        keepout[:, max(0, split_gap_x[0] - 2) : min(w, split_gap_x[1] + 2)] = True

    foliage = np.zeros((h, w), dtype=bool)
    buds: list[tuple[int, int]] = []

    def stamp_leaf_cluster(cx: int, cy: int, radius_x: int = 3, radius_y: int = 3, angle_dx: int = 0):
        for dy in range(-radius_y, radius_y + 1):
            for dx in range(-radius_x, radius_x + 1):
                sx = dx - (angle_dx * dy) * 0.35
                if (sx / (radius_x + 0.32)) ** 2 + (dy / (radius_y + 0.32)) ** 2 <= 1.0:
                    nx, ny = cx + dx, cy + dy
                    if 2 <= nx < w - 2 and 2 <= ny < h - 2 and (not ext[ny, nx]) and (not keepout[ny, nx]):
                        foliage[ny, nx] = True

    bay_anchors = [x_min]
    cur = x_min
    while cur < x_max - 34:
        step = int(rng.integers(42, 56))
        nxt = min(x_max, cur + step)
        for wx0, wx1, _ in win_spans:
            if abs(nxt - wx0) <= 18 and wx0 > cur + 18:
                nxt = wx0
                break
            if abs(nxt - wx1) <= 18 and wx1 > cur + 18:
                nxt = wx1
                break
        if north_arch_x is not None:
            for ax in north_arch_x:
                if abs(nxt - ax) <= 18 and ax > cur + 18:
                    nxt = ax
                    break
        bay_anchors.append(nxt)
        cur = nxt
    if bay_anchors[-1] < x_max - 12:
        bay_anchors.append(x_max)

    if split_gap_x is not None:
        sg0, sg1 = split_gap_x
        left_anc = [a for a in bay_anchors if a <= sg0 - 4]
        if left_anc and sg0 - 4 - left_anc[-1] >= 10:
            left_anc.append(sg0 - 4)
        right_anc = [a for a in bay_anchors if a >= sg1 + 4]
        if right_anc and right_anc[0] - (sg1 + 4) >= 10:
            right_anc.insert(0, sg1 + 4)
        bay_anchors = left_anc + right_anc

    for bi in range(len(bay_anchors) - 1):
        xa, xb = bay_anchors[bi], bay_anchors[bi + 1]
        if split_gap_x is not None and xa <= split_gap_x[0] and xb >= split_gap_x[1]:
            continue
        span = xb - xa
        if span < 12:
            continue
        mid_x = (xa + xb) // 2
        over_win = any(wx0 - 4 <= mid_x <= wx1 + 4 for wx0, wx1, _ in win_spans)
        over_arch = north_arch_x is not None and (north_arch_x[0] - 4 <= mid_x <= north_arch_x[1] + 4)

        ya = smooth_cy[xa] - 3.0
        yb = smooth_cy[xb] - 3.0
        if over_win:
            wy_min = min(wy for wx0, wx1, wy in win_spans if wx0 - 6 <= mid_x <= wx1 + 6)
            sag = -6.0
            ya = min(ya, float(wy_min + 2))
            yb = min(yb, float(wy_min + 2))
        elif over_arch:
            sag = -7.0
            if north_arch_x is not None and (north_arch_x[1] - north_arch_x[0]) >= 120:
                ya = min(ya, 57.0)
                yb = min(yb, 57.0)
            else:
                ya -= 5.0
                yb -= 5.0
        else:
            sag = min(9.5, max(5.5, span * 0.145))

        for x in range(xa, xb + 1, 2):
            t = (x - xa) / max(1, span)
            yc = int(round((1.0 - t) * ya + t * yb + sag * 4.0 * t * (1.0 - t)))
            phase = ((x - xa) // 4) % 3
            if phase == 0:
                stamp_leaf_cluster(x, yc, radius_x=3, radius_y=2, angle_dx=1)
                stamp_leaf_cluster(x, yc + 2, radius_x=2, radius_y=3, angle_dx=-1)
            elif phase == 1:
                stamp_leaf_cluster(x, yc, radius_x=2, radius_y=2, angle_dx=-1)
            else:
                stamp_leaf_cluster(x, yc, radius_x=3, radius_y=2, angle_dx=0)

    for idx, ax in enumerate(bay_anchors):
        drop_len = 13 if idx in (0, len(bay_anchors) - 1) else int(rng.integers(15, 23))
        ay0 = int(round(smooth_cy[ax] - 3.0))
        if idx % 2 == 1 and 4 <= ax < w - 4 and 4 <= ay0 < h - 4 and not ext[ay0, ax] and not keepout[ay0, ax]:
            buds.append((ax, ay0))
        for dy in range(0, drop_len, 3):
            sway = int(round(1.5 * np.sin(dy * 0.45 + idx)))
            rx = 2 if dy < drop_len - 4 else 1
            stamp_leaf_cluster(ax + sway, ay0 + dy, radius_x=rx, radius_y=2, angle_dx=(1 if dy % 6 == 0 else -1))

    out = np.zeros((h, w, 4), dtype=np.uint8)
    dil = ndimage.binary_dilation(foliage, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    outline = dil & (~foliage) & (~ext) & (~keepout)
    full_garland = foliage | outline

    sh1 = np.zeros_like(full_garland)
    sh2 = np.zeros_like(full_garland)
    sh1[2:, 1:] = full_garland[:-2, :-1]
    sh2[3:, 2:] = full_garland[:-3, :-2]
    sh_mask1 = sh1 & (~full_garland) & (~ext) & (~keepout)
    sh_mask2 = sh2 & (~full_garland) & (~sh_mask1) & (~ext) & (~keepout)
    out[sh_mask2] = [38, 17, 6, 52]
    out[sh_mask1] = [38, 17, 6, 98]

    ys, xs = np.where(foliage)
    for y, x in zip(ys, xs):
        up_empty = not foliage[y - 1, x] or not foliage[y, x - 1]
        dn_empty = not foliage[y + 1, x] or not foliage[y, x + 1]
        if up_empty and not dn_empty:
            out[y, x] = [118, 162, 54, 255]
        elif dn_empty and not up_empty:
            out[y, x] = [44, 78, 28, 255]
        else:
            out[y, x] = [74, 120, 42, 255] if (((x // 2) + y) % 3 == 0) else [64, 108, 36, 255]

    out[outline] = [26, 44, 18, 255]
    for bx, by in buds:
        if 2 <= bx < w - 2 and 2 <= by < h - 2:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                out[by + dy, bx + dx] = [62, 34, 14, 255]
            out[by, bx] = [238, 184, 74, 255]
            out[by - 1, bx] = [250, 214, 118, 255]
    return out


SPLIT_GAP_SPANS = {
    "guilde_destiny_carrefour": (196, 284),
    "guilde_destiny_reserve": (184, 264),
    "guilde_destiny_couloir_ouest": (196, 284),
    "guilde_destiny_couloir_est": (196, 284),
    "guilde_destiny_dortoir_sud_1": (184, 264),
    "guilde_destiny_dortoir_sud_2": (184, 264),
}

NORTH_ARCH_SPANS = {
    "guilde_destiny_missions": (252, 324),
    "guilde_destiny_grand_salon": (222, 354),
}


def main() -> None:
    decors_manifest = json.loads((RESEAU / "objets_pmdo/manifest_decors_pmdo.json").read_text(encoding="utf-8"))
    verd_bank = DedupTileBankBuilder("Destiny_Guilde_Verdure", cols=32)

    room_base_map = {
        "guilde_destiny_missions":       ("02_missions", False),
        "guilde_destiny_grand_salon":    ("03_grand_salon_central", False),
        "guilde_destiny_bureau_maitre":  ("04_bureau_maitre", False),
        "guilde_destiny_carrefour":      ("05b_carrefour_ouest", False),
        "guilde_destiny_refectoire":     ("05_refectoire", False),
        "guilde_destiny_cuisine":        ("06_cuisine", False),
        "guilde_destiny_reserve":        ("10_dortoir_sud", False),
        "guilde_destiny_couloir_ouest":  ("08_couloir_dortoirs", False),
        "guilde_destiny_couloir_est":    ("08_couloir_dortoirs", True),
        "guilde_destiny_dortoir_nord_1": ("09_dortoir_nord", False),
        "guilde_destiny_dortoir_nord_2": ("09_dortoir_nord", True),
        "guilde_destiny_dortoir_sud_1":  ("10_dortoir_sud", False),
        "guilde_destiny_dortoir_sud_2":  ("10_dortoir_sud", True),
        "guilde_destiny_chambre_heros":  ("11_chambre_heros", False),
    }

    for idx_r, (map_id, (src_stem, flip_h)) in enumerate(room_base_map.items()):
        rs_path = GROUND_DIR / f"{map_id}.rsground"
        doc = json.loads(rs_path.read_text(encoding="utf-8-sig"))
        g = doc["Object"]
        tw, th = len(g["obstacles"]), len(g["obstacles"][0])
        w, h = tw * 8, th * 8

        # Keep 100% of pure wood tiles on `Layers[0..3]` + `Layers[7]`
        for tx in range(tw):
            for ty in range(th):
                if g["Layers"][4]["Tiles"][tx][ty]["Layers"] and not g["Layers"][3]["Tiles"][tx][ty]["Layers"]:
                    sh = g["Layers"][4]["Tiles"][tx][ty]["Layers"][0]["Frames"][0]["Sheet"]
                    if sh.startswith("Destiny_Guilde_") and sh not in ("Destiny_Guilde_Verdure", "Destiny_Guilde_Immobilier"):
                        g["Layers"][3]["Tiles"][tx][ty] = g["Layers"][4]["Tiles"][tx][ty]

        base_im = Image.open(BASE_DIR / f"{src_stem}_1x_base.png").convert("RGB")
        if flip_h:
            base_im = base_im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        room_rgb = np.array(base_im)

        wins = []
        for s in decors_manifest["fenetres_par_salle"].get(src_stem, []):
            sx = (w - s["x"] - s["w"]) if flip_h else s["x"]
            wins.append({"x": sx, "y": s["y"], "w": s["w"], "h": s["h"]})

        garland_rgba = generate_room_garland_rgba(
            room_rgb,
            wins,
            north_arch_x=NORTH_ARCH_SPANS.get(map_id),
            split_gap_x=SPLIT_GAP_SPANS.get(map_id),
            seed=101 + idx_r * 17,
        )
        Image.fromarray(garland_rgba, "RGBA").save(VERD_DIR / f"{map_id}_verdure.png")

        g["Layers"][4]["Name"] = "04 verdure separee"
        g["Layers"][4]["Layer"] = 0
        g["Layers"][4]["Visible"] = True
        g["Layers"][4]["Tiles"] = verd_bank.encode_rgba_layer(garland_rgba)

        # Leave `Layers[5]` and `Layers[6]` empty & ready for the user to place furniture/rugs in-game!
        g["Layers"][5]["Name"] = "05 ombres mobilier guilde"
        g["Layers"][5]["Layer"] = 0
        g["Layers"][5]["Visible"] = True
        g["Layers"][5]["Tiles"] = empty_tile_grid(tw, th)

        g["Layers"][6]["Name"] = "06 immobilier guilde"
        g["Layers"][6]["Layer"] = 0
        g["Layers"][6]["Visible"] = True
        g["Layers"][6]["Tiles"] = empty_tile_grid(tw, th)

        rs_path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Also fit `guilde_destiny_accueil` (`1536x1152`) with its dedicated separate-layer Greenery Garland!
    acc_rs_path = GROUND_DIR / "guilde_destiny_accueil.rsground"
    acc_doc = json.loads(acc_rs_path.read_text(encoding="utf-8-sig"))
    acc_g = acc_doc["Object"]
    acc_tw, acc_th = len(acc_g["obstacles"]), len(acc_g["obstacles"][0])
    acc_1x_rgb = np.array(Image.open(BASE_DIR / "01_accueil_1x_base.png").convert("RGB"))
    acc_wins_1x = decors_manifest["fenetres_par_salle"]["01_accueil"]
    acc_garland_1x = generate_room_garland_rgba(acc_1x_rgb, acc_wins_1x, split_gap_x=(220, 292), seed=77)
    Image.fromarray(acc_garland_1x, "RGBA").save(VERD_DIR / "guilde_destiny_accueil_verdure_1x.png")
    acc_garland_3x = np.array(Image.fromarray(acc_garland_1x, "RGBA").resize((1536, 1152), Image.Resampling.NEAREST))

    acc_g["Layers"][4]["Name"] = "04 verdure separee"
    acc_g["Layers"][4]["Layer"] = 0
    acc_g["Layers"][4]["Visible"] = True
    acc_g["Layers"][4]["Tiles"] = verd_bank.encode_rgba_layer(acc_garland_3x)

    acc_g["Layers"][5]["Name"] = "05 ombres mobilier guilde"
    acc_g["Layers"][5]["Layer"] = 0
    acc_g["Layers"][5]["Visible"] = True
    acc_g["Layers"][5]["Tiles"] = empty_tile_grid(acc_tw, acc_th)

    acc_g["Layers"][6]["Name"] = "06 immobilier guilde"
    acc_g["Layers"][6]["Layer"] = 0
    acc_g["Layers"][6]["Visible"] = True
    acc_g["Layers"][6]["Tiles"] = empty_tile_grid(acc_tw, acc_th)
    acc_rs_path.write_text(json.dumps(acc_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    n_verd = verd_bank.write(TILE_DIR)

    # Compile `Destiny_Guilde_Immobilier.tile` in intact 2D visual layout (`Combined` on top, `Objets` middle, `Ombres` bottom)!
    atlas_obj = Image.open(IMM_DIR / "Destiny_Guilde_Immobilier_Objets.png").convert("RGBA")
    atlas_shd = Image.open(IMM_DIR / "Destiny_Guilde_Immobilier_Ombres.png").convert("RGBA")
    comb_im = atlas_shd.copy()
    comb_im.alpha_composite(atlas_obj)

    aw, ah = atlas_obj.size
    sep = 16
    full_sheet = Image.new("RGBA", (aw, ah * 3 + sep * 2), (0, 0, 0, 0))
    full_sheet.paste(comb_im, (0, 0))
    full_sheet.paste(atlas_obj, (0, ah + sep))
    full_sheet.paste(atlas_shd, (0, (ah + sep) * 2))

    n_imm = write_visual_2d_tile_sheet("Destiny_Guilde_Immobilier", np.array(full_sheet), TILE_DIR)

    # Sync art folder in repository
    (ART_DEST / "immobilier_guilde").mkdir(parents=True, exist_ok=True)
    for fn in (
        "Destiny_Guilde_Immobilier_Objets.png",
        "Destiny_Guilde_Immobilier_Ombres.png",
        "Destiny_Guilde_Immobilier_Manifest.json",
        "Apercu_Banque_Immobilier_Guilde_Sur_Parquet.png",
    ):
        src_f, dst_f = IMM_DIR / fn, ART_DEST / "immobilier_guilde" / fn
        if src_f.resolve() != dst_f.resolve():
            shutil.copy2(src_f, dst_f)

    print(f"[OK] Compiled Destiny_Guilde_Verdure.tile ({n_verd} tiles) across 15 unfurnished rooms + 2D visual Destiny_Guilde_Immobilier.tile ({n_imm} tiles)!")


if __name__ == "__main__":
    main()
