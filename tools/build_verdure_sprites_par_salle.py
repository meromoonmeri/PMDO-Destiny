#!/usr/bin/env python3
"""
Extrait, adapte au pixel près au layout de chacune des 15 salles intérieures `guilde_destiny_*`,
quantifie en Pixel-Art Nintendo DS (Explorers of Sky, 12 couleurs franches + ombre portée chaude 2 paliers, 0 magenta),
et compile :
  1. Les 15 sprites PNG autonomes sur fond transparent (`art/guilde_destiny_reseau/guirlandes_verdure/<salle>_verdure.png`
     et `/home/user/guilde_destiny_reseau/guirlandes_verdure/`).
  2. Les 15 objets `.dir` autonomes (`game/Content/Object/Guilde_Verdure_<Salle>.dir`).
  3. La planche `game/Content/Tile/Destiny_Guilde_Verdure.tile` disposée en **2D visuelle intacte** (chaque guirlande
     apparaît entière dans l'éditeur PMDO !).
  4. L'intégration directe sur le calque `Layers[6] == "Fringe"` (`Layer = 4`, au-dessus des personnages, 0 tuile sur sol
     marchable) des 15 cartes `.rsground`, SANS modifier un seul pixel des calques `Floor`, `Walls`, `Shadows` ou `Supports` !
"""
from __future__ import annotations

import io
import json
import shutil
import struct
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / "art/guilde_destiny_reseau/cartes_base_sans_decors"
VERD_ART_DIR = ROOT / "art/guilde_destiny_reseau/guirlandes_verdure"
USER_VERD_DIR = Path("/home/user/guilde_destiny_reseau/guirlandes_verdure")
GEN_DIR = Path("/tmp/verd_guides")

OBJ_DIR = ROOT / "game/Content/Object"
TILE_DIR = ROOT / "game/Content/Tile"
GROUND_DIR = ROOT / "game/Data/Ground"

DS_LEAF_RAMP = np.array([
    [22, 42, 17],    # 0: pine sel-out
    [34, 68, 24],    # 1: deep ivy shadow
    [50, 98, 32],    # 2: forest leaf
    [72, 130, 40],   # 3: mid emerald leaf
    [104, 162, 48],  # 4: sunlit lime leaf
    [144, 192, 62],  # 5: bright leaf vein highlight
], dtype=np.uint8)

DS_STEM_RAMP = np.array([
    [62, 35, 18],    # 0: dark vine stem
    [98, 58, 28],    # 1: mid woody stem
    [136, 84, 38],   # 2: lit woody vine
], dtype=np.uint8)

DS_BUD_RAMP = np.array([
    [146, 94, 28],   # 0: warm bud base
    [206, 148, 46],  # 1: golden forest bud
    [244, 202, 88],  # 2: sunlit bud tip
], dtype=np.uint8)


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
    arr[..., :3] = np.clip(np.round(arr[..., :3] * alpha), 0.0, 255.0)
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def write_dir(dir_path: Path, rgba_arr: np.ndarray) -> None:
    arr = sanitize_patch_anti_magenta(rgba_arr)
    h, w, _ = arr.shape
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, format="PNG", optimize=True)
    png = buf.getvalue()
    dir_path.parent.mkdir(parents=True, exist_ok=True)
    dir_path.write_bytes(struct.pack("<q", len(png)) + png + struct.pack("<iiii", w, h, 0, 1))


def extract_clean_gen_vine(gen_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Extracts clean foreground RGB & mask from pure-white (#FFFFFF) generated vine image."""
    rgb = np.array(Image.open(gen_path).convert("RGB"))
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    # White background: high brightness & low saturation
    is_white = (r >= 236) & (g >= 236) & (b >= 236) & (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) <= 18)
    fg = ~is_white
    # Remove tiny stray dust (< 12 px at high res)
    lbl, n = ndimage.label(fg)
    if n > 0:
        sz = ndimage.sum(fg, lbl, range(1, n + 1))
        fg = np.isin(lbl, np.where(sz >= 12)[0] + 1)
    # Erode 1px of white-blended anti-aliasing halo on outer silhouette at 1600px res so downsampling has 0 white fringe!
    fg_core = ndimage.binary_erosion(fg, iterations=1)
    _, idx = ndimage.distance_transform_edt(~fg_core, return_indices=True)
    clean_rgb = rgb.copy()
    halo = fg & (~fg_core)
    clean_rgb[halo] = rgb[idx[0][halo], idx[1][halo]]
    return clean_rgb, fg


def compute_room_cornice_and_keepout(
    base_rgb: np.ndarray,
    walk_tile: np.ndarray,
    wins: list[tuple[int, int, int, int]],
    split_gap: tuple[int, int] | None,
    door_box: tuple[int, int, int, int] | None,
) -> tuple[np.ndarray, int, int, np.ndarray]:
    h, w, _ = base_rgb.shape
    tw, th = w // 8, h // 8
    ext = (
        (np.abs(base_rgb[..., 0].astype(int) - 104) <= 6)
        & (np.abs(base_rgb[..., 1].astype(int) - 72) <= 6)
        & (np.abs(base_rgb[..., 2].astype(int) - 47) <= 6)
    )
    top_ext_dist = ndimage.distance_transform_edt(~ext)

    cornice_y = np.full(w, -1, dtype=int)
    for x in range(14, w - 14):
        non_ext = np.where(~ext[:, x])[0]
        if len(non_ext) < 36:
            continue
        yt = int(non_ext[0])
        if yt <= 4 or yt > int(h * 0.56):
            continue
        if split_gap is not None and split_gap[0] - 2 <= x <= split_gap[1] + 2:
            continue
        found = -1
        for y in range(yt + 12, min(int(h * 0.58), yt + 64)):
            if top_ext_dist[y, x] >= 13 and base_rgb[y, x, 0] >= 145:
                found = y
                break
        if found != -1:
            cornice_y[x] = found

    for wx, wy, ww, wh in wins:
        if wy >= 30:
            for x in range(wx - 4, wx + ww + 5):
                if 0 <= x < w and not ext[max(4, wy - 5), x]:
                    t = (x - (wx - 4)) / max(1, ww + 8)
                    arch_y = int(round(wy - 3 - 5.0 * np.sin(t * np.pi)))
                    cornice_y[x] = max(int(np.where(~ext[:, x])[0][0]) + 11, arch_y)

    vxs = np.where(cornice_y > 0)[0]
    x_min, x_max = int(vxs.min()) + 6, int(vxs.max()) - 6
    smooth_cy = np.interp(np.arange(w), vxs, cornice_y[vxs].astype(np.float32))
    smooth_cy = ndimage.gaussian_filter1d(smooth_cy, sigma=4.0)

    keepout = ext | (top_ext_dist <= 11)
    # Walkable tiles + 16px headroom above walkable tiles are strictly keepout!
    for tx in range(tw):
        for ty in range(th):
            if walk_tile[tx, ty]:
                keepout[max(0, (ty - 2) * 8) : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = True

    for wx, wy, ww, wh in wins:
        # True semicircular arch keepout matching the arched window silhouette (NOT a boxy rectangle!)
        wcx = wx + ww * 0.5
        w_rad = ww * 0.5 - 2.0
        wcy = wy + ww * 0.5
        yy_w, xx_w = np.ogrid[:h, :w]
        in_arch_top = (yy_w >= wy + 3) & (yy_w <= wcy) & (((xx_w - wcx) ** 2 + (yy_w - wcy) ** 2) <= w_rad ** 2)
        in_arch_body = (yy_w > wcy) & (yy_w < wy + wh) & (xx_w >= wx + 3) & (xx_w < wx + ww - 3)
        keepout |= in_arch_top | in_arch_body

    if door_box is not None:
        dx, dy, dw, dh = door_box
        dcx = dx + dw * 0.5
        d_rad = dw * 0.5 + 1.0
        dcy = dy + dw * 0.45
        yy_d, xx_d = np.ogrid[:h, :w]
        in_d_arch = (yy_d >= dy - 1) & (yy_d <= dcy) & (((xx_d - dcx) ** 2 + (yy_d - dcy) ** 2) <= d_rad ** 2)
        in_d_body = (yy_d > dcy) & (yy_d < dy + dh) & (xx_d >= dx - 1) & (xx_d < dx + dw + 1)
        keepout |= in_d_arch | in_d_body

    if split_gap is not None:
        keepout[:, max(0, split_gap[0] - 2) : min(w, split_gap[1] + 2)] = True

    return smooth_cy, x_min, x_max, keepout


def warp_and_quantize_ds_vine(
    src_rgb: np.ndarray,
    src_fg: np.ndarray,
    w: int,
    h: int,
    smooth_cy: np.ndarray,
    x_min: int,
    x_max: int,
    keepout: np.ndarray,
    wins: list[tuple[int, int, int, int]] = (),
    door_box: tuple[int, int, int, int] | None = None,
    split_gap: tuple[int, int] | None = None,
    v_scale: float = 0.25,
) -> np.ndarray:
    """
    Maps a standalone generated vine sprite onto the exact curved cornice `smooth_cy[x]` of the room,
    quantizes onto the 12-color Nintendo DS Foliage/Stem/Bud palette, applies crisp pine sel-out & 2-step shadow!
    """
    sh, sw, _ = src_rgb.shape
    u_cols = np.where(src_fg.any(axis=0))[0]
    u0, u1 = int(u_cols.min()), int(u_cols.max())

    # Smooth top envelope of source vine so local leaf serrations stay organic!
    raw_top_u = np.full(sw, -1.0, dtype=np.float32)
    for u in range(u0, u1 + 1):
        ys = np.where(src_fg[:, u])[0]
        if len(ys):
            raw_top_u[u] = float(ys[0])
    valid_u = np.where(raw_top_u >= 0)[0]
    smooth_src_top = np.interp(np.arange(sw), valid_u, raw_top_u[valid_u])
    smooth_src_top = ndimage.gaussian_filter1d(smooth_src_top, sigma=18.0)

    warped_rgb = np.zeros((h, w, 3), dtype=np.uint8)
    warped_fg = np.zeros((h, w), dtype=bool)

    # Map x in [x_min..x_max] -> u in [u0..u1] (preserving central split_gap alignment if present!)
    u_mid = (u0 + u1) // 2
    if split_gap is not None:
        g0, g1 = split_gap
        # Find left & right clusters around u_mid in src_fg
        left_us = valid_u[valid_u < u_mid]
        right_us = valid_u[valid_u > u_mid]
        lu0, lu1 = (int(left_us.min()), int(left_us.max())) if len(left_us) else (u0, u_mid - 10)
        ru0, ru1 = (int(right_us.min()), int(right_us.max())) if len(right_us) else (u_mid + 10, u1)
        x_segments = [(x_min, g0 - 3, lu0, lu1), (g1 + 3, x_max, ru0, ru1)]
    else:
        x_segments = [(x_min, x_max, u0, u1)]

    # Smooth per-column vertical scale `v_col[x]` so garlands gracefully slim down over arched windows & doorways (ZERO boxy cuts!)
    v_col = np.full(w, v_scale, dtype=np.float32)
    for wx, wy, ww, wh in wins:
        for x in range(max(0, wx - 14), min(w, wx + ww + 15)):
            dist_edge = min(abs(x - (wx + ww * 0.5)) / max(1.0, ww * 0.5 + 14.0), 1.0)
            v_col[x] = min(v_col[x], v_scale * (0.46 + 0.54 * (dist_edge ** 1.5)))
    if door_box is not None:
        dx, dy, dw, dh = door_box
        for x in range(max(0, dx - 16), min(w, dx + dw + 17)):
            dist_edge = min(abs(x - (dx + dw * 0.5)) / max(1.0, dw * 0.5 + 16.0), 1.0)
            v_col[x] = min(v_col[x], v_scale * (0.44 + 0.56 * (dist_edge ** 1.5)))
    v_col = ndimage.gaussian_filter1d(v_col, sigma=4.0)

    for xa, xb, ua, ub in x_segments:
        if xb <= xa + 6 or ub <= ua + 6:
            continue
        for x in range(xa, xb + 1):
            t = (x - xa) / max(1, xb - xa)
            u = int(round(ua + t * (ub - ua)))
            u = max(0, min(sw - 1, u))
            y_base = smooth_cy[x] - 5.0
            s_top = smooth_src_top[u]
            inv_vx = 1.0 / max(0.10, float(v_col[x]))
            for y in range(max(2, int(y_base - 8)), min(h - 2, int(y_base + 54))):
                if keepout[y, x]:
                    continue
                v = int(round(s_top + (y - y_base) * inv_vx))
                if 0 <= v < sh and src_fg[v, u]:
                    warped_fg[y, x] = True
                    warped_rgb[y, x] = src_rgb[v, u]

    # Prune disconnected fragments (< 45px) caused by keepout clipping so zero floating leaves ever appear!
    lbl, n = ndimage.label(warped_fg, structure=np.ones((3, 3), dtype=bool))
    if n > 0:
        sz = ndimage.sum(warped_fg, lbl, range(1, n + 1))
        keep_ids = np.where(sz >= 45)[0] + 1
        warped_fg = np.isin(lbl, keep_ids)

    # Quantize onto crisp 12-color Nintendo DS Foliage / Woody Stem / Golden Bud ramps!
    out = np.zeros((h, w, 4), dtype=np.uint8)
    if not np.any(warped_fg):
        return out

    r = warped_rgb[..., 0].astype(np.float32)
    g = warped_rgb[..., 1].astype(np.float32)
    b = warped_rgb[..., 2].astype(np.float32)
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    # 1) Golden buds / berries (warm yellow-orange OR purple berries converted to golden forest buds -> 0 magenta!)
    is_bud = warped_fg & (
        ((r > g + 14.0) & (lum >= 115.0) & ((r - b) >= 45.0))
        | ((r > g + 12.0) & (b > g + 8.0))
    )
    # 2) Woody vine stems (warm brown where R > G and not bright bud)
    is_stem = warped_fg & (~is_bud) & (r > g + 6.0) & (lum < 140.0)
    # 3) Emerald & lime DS ivy leaves
    is_leaf = warped_fg & (~is_bud) & (~is_stem)

    def apply_ramp(m: np.ndarray, ramp: np.ndarray, thresholds: list[float]) -> None:
        if np.any(m):
            out[m, :3] = ramp[np.digitize(lum[m], thresholds)]
            out[m, 3] = 255

    apply_ramp(is_bud, DS_BUD_RAMP, [135.0, 185.0])
    apply_ramp(is_stem, DS_STEM_RAMP, [68.0, 105.0])
    apply_ramp(is_leaf, DS_LEAF_RAMP, [42.0, 68.0, 96.0, 128.0, 162.0])

    # Clean isolated 1px color specks inside leaf clusters (`lum >= 75`)
    editable = is_leaf & (lum >= 75.0)
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
        for y, x in zip(ys_s, xs_s):
            y0, y1 = max(0, y - 1), min(h, y + 2)
            x0, x1 = max(0, x - 1), min(w, x + 2)
            nb = warped_fg[y0:y1, x0:x1] & (~speck[y0:y1, x0:x1])
            if np.any(nb):
                vals, cnts = np.unique(codes[y0:y1, x0:x1][nb], return_counts=True)
                bc = int(vals[int(np.argmax(cnts))])
                out[y, x, :3] = [(bc >> 16) & 255, (bc >> 8) & 255, bc & 255]

    # Crisp 1px warm pine sel-out around silhouette (closes any pruned tendril tip cleanly!)
    eroded4 = ndimage.binary_erosion(warped_fg, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool))
    sil = warped_fg & (~eroded4)
    out[sil, :3] = DS_LEAF_RAMP[0]
    out[sil, 3] = 255

    # Crisp 2-step warm DS cast shadow below/right of the garland (strictly outside keepout!)
    sh1 = np.zeros_like(warped_fg)
    sh2 = np.zeros_like(warped_fg)
    sh1[2:, 1:] = warped_fg[:-2, :-1]
    sh2[3:, 2:] = warped_fg[:-3, :-2]
    m_sh1 = sh1 & (~warped_fg) & (~keepout)
    m_sh2 = sh2 & (~warped_fg) & (~m_sh1) & (~keepout)
    out[m_sh2] = [38, 17, 6, 44]
    out[m_sh1] = [38, 17, 6, 88]

    return sanitize_patch_anti_magenta(out)


def build_hero_composite_gen() -> tuple[np.ndarray, np.ndarray]:
    """Combines West hallway vine (`08_couloir_dortoirs` left segment) + `04_bureau_maitre` window-flanking swags for `11_chambre_heros`."""
    c_rgb, c_fg = extract_clean_gen_vine(GEN_DIR / "gen_08_couloir_dortoirs.png")
    b_rgb, b_fg = extract_clean_gen_vine(GEN_DIR / "gen_04_bureau_maitre.png")
    # Build 1600x656 composite matching `11_chambre_heros` proportions:
    # x=0..420: West hallway vine; x=430..920: left bedroom swag; x=1120..1580: right bedroom swag
    H, W = 656, 1607
    out_rgb = np.full((H, W, 3), 255, dtype=np.uint8)
    out_fg = np.zeros((H, W), dtype=bool)

    # Left half of couloir shrunk into 0..420
    c_im = Image.fromarray(c_rgb[:, :760]).resize((410, 460), Image.Resampling.NEAREST)
    c_m = np.array(Image.fromarray((c_fg[:, :760].astype(np.uint8) * 255)).resize((410, 460), Image.Resampling.NEAREST)) > 127
    out_rgb[140:600, 16:426][c_m] = np.array(c_im)[c_m]
    out_fg[140:600, 16:426] |= c_m

    # Bureau Maitre full twin swags placed into 430..1590 (flanking window around x=920..1120!)
    b_im = Image.fromarray(b_rgb).resize((1160, 560), Image.Resampling.NEAREST)
    b_m = np.array(Image.fromarray((b_fg.astype(np.uint8) * 255)).resize((1160, 560), Image.Resampling.NEAREST)) > 127
    out_rgb[30:590, 435:1595][b_m] = np.array(b_im)[b_m]
    out_fg[30:590, 435:1595] |= b_m
    return out_rgb, out_fg


def main() -> None:
    VERD_ART_DIR.mkdir(parents=True, exist_ok=True)
    USER_VERD_DIR.mkdir(parents=True, exist_ok=True)

    gen_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for key in [
        "01_accueil", "02_missions", "03_grand_salon", "04_bureau_maitre", "05_refectoire",
        "05b_carrefour", "06_cuisine", "08_couloir_dortoirs", "09_dortoir_nord", "10_dortoir_sud",
    ]:
        gen_cache[key] = extract_clean_gen_vine(GEN_DIR / f"gen_{key}.png")
    gen_cache["11_chambre_heros"] = build_hero_composite_gen()

    # Exact specs for all 15 rooms:
    ROOMS_15 = [
        {
            "id": "guilde_destiny_accueil",
            "dir_name": "Guilde_Verdure_Accueil",
            "base": "01_accueil_1x_base.png",
            "gen_key": "01_accueil",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(112, 56, 48, 88), (352, 56, 48, 88)],
            "split_gap": (214, 298),  # Protects Winged-Egg emblem above North stairs!
            "door_box": None,
            "scale_3x": True,
        },
        {
            "id": "guilde_destiny_missions",
            "dir_name": "Guilde_Verdure_Missions",
            "base": "02_missions_1x_base.png",
            "gen_key": "02_missions",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(72, 64, 56, 96), (448, 64, 56, 96)],
            "split_gap": None,
            "door_box": (252, 62, 72, 90),  # Protects North stairwell arch interior!
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_grand_salon",
            "dir_name": "Guilde_Verdure_Grand_Salon",
            "base": "03_grand_salon_central_1x_base.png",
            "gen_key": "03_grand_salon",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(88, 64, 48, 96), (432, 64, 56, 96)],
            "split_gap": (222, 354),
            "door_box": (224, 64, 128, 96),
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_bureau_maitre",
            "dir_name": "Guilde_Verdure_Bureau_Maitre",
            "base": "04_bureau_maitre_1x_base.png",
            "gen_key": "04_bureau_maitre",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(224, 16, 64, 88)],
            "split_gap": (220, 292),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_carrefour",
            "dir_name": "Guilde_Verdure_Carrefour",
            "base": "05b_carrefour_ouest_1x_base.png",
            "gen_key": "05b_carrefour",
            "flip_base": False,
            "flip_vine": False,
            "wins": [],
            "split_gap": (196, 284),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_refectoire",
            "dir_name": "Guilde_Verdure_Refectoire",
            "base": "05_refectoire_1x_base.png",
            "gen_key": "05_refectoire",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(184, 40, 64, 80), (320, 40, 64, 80)],
            "split_gap": None,
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_cuisine",
            "dir_name": "Guilde_Verdure_Cuisine",
            "base": "06_cuisine_1x_base.png",
            "gen_key": "06_cuisine",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(136, 32, 48, 72), (296, 32, 48, 72)],
            "split_gap": None,
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_reserve",
            "dir_name": "Guilde_Verdure_Reserve",
            "base": "10_dortoir_sud_1x_base.png",
            "gen_key": "10_dortoir_sud",
            "flip_base": False,
            "flip_vine": True,
            "wins": [],
            "split_gap": (184, 264),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_couloir_ouest",
            "dir_name": "Guilde_Verdure_Couloir_Ouest",
            "base": "08_couloir_dortoirs_1x_base.png",
            "gen_key": "08_couloir_dortoirs",
            "flip_base": False,
            "flip_vine": False,
            "wins": [],
            "split_gap": (196, 284),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_couloir_est",
            "dir_name": "Guilde_Verdure_Couloir_Est",
            "base": "08_couloir_dortoirs_1x_base.png",
            "gen_key": "08_couloir_dortoirs",
            "flip_base": True,
            "flip_vine": True,
            "wins": [],
            "split_gap": (196, 284),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_dortoir_nord_1",
            "dir_name": "Guilde_Verdure_Dortoir_Nord_1",
            "base": "09_dortoir_nord_1x_base.png",
            "gen_key": "09_dortoir_nord",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(192, 16, 64, 72)],
            "split_gap": (188, 260),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_dortoir_nord_2",
            "dir_name": "Guilde_Verdure_Dortoir_Nord_2",
            "base": "09_dortoir_nord_1x_base.png",
            "gen_key": "09_dortoir_nord",
            "flip_base": True,
            "flip_vine": True,
            "wins": [(192, 16, 64, 72)],
            "split_gap": (188, 260),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_dortoir_sud_1",
            "dir_name": "Guilde_Verdure_Dortoir_Sud_1",
            "base": "10_dortoir_sud_1x_base.png",
            "gen_key": "10_dortoir_sud",
            "flip_base": False,
            "flip_vine": False,
            "wins": [],
            "split_gap": (184, 264),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_dortoir_sud_2",
            "dir_name": "Guilde_Verdure_Dortoir_Sud_2",
            "base": "10_dortoir_sud_1x_base.png",
            "gen_key": "10_dortoir_sud",
            "flip_base": True,
            "flip_vine": True,
            "wins": [],
            "split_gap": (184, 264),
            "door_box": None,
            "scale_3x": False,
        },
        {
            "id": "guilde_destiny_chambre_heros",
            "dir_name": "Guilde_Verdure_Chambre_Heros",
            "base": "11_chambre_heros_1x_base.png",
            "gen_key": "11_chambre_heros",
            "flip_base": False,
            "flip_vine": False,
            "wins": [(216, 24, 56, 72)],
            "split_gap": (212, 276),
            "door_box": None,
            "scale_3x": False,
        },
    ]

    # Stack all 15 trimmed 8px-aligned greenery bands into ONE visual 2D atlas for `Destiny_Guilde_Verdure.tile`!
    atlas_strips: list[tuple[str, dict, np.ndarray, int, int, int, int]] = []
    atlas_w_tiles = 0
    atlas_y_cursor_tiles = 0

    for spec in ROOMS_15:
        gid = spec["id"]
        rs_path = GROUND_DIR / f"{gid}.rsground"
        doc = json.loads(rs_path.read_text(encoding="utf-8-sig"))
        g = doc["Object"]
        obs = g["obstacles"]
        tw, th = len(obs), len(obs[0])
        walk_tile_full = np.array([[obs[tx][ty]["Tags"] == 0 for ty in range(th)] for tx in range(tw)], dtype=bool)

        base_im = Image.open(BASE_DIR / spec["base"]).convert("RGB")
        if spec["flip_base"]:
            base_im = base_im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        base_1x = np.array(base_im)
        h1, w1, _ = base_1x.shape

        walk_1x = walk_tile_full[::3, ::3] if spec["scale_3x"] else walk_tile_full
        smooth_cy, x_min, x_max, keepout = compute_room_cornice_and_keepout(
            base_1x, walk_1x, spec["wins"], spec["split_gap"], spec["door_box"]
        )

        s_rgb, s_fg = gen_cache[spec["gen_key"]]
        if spec["flip_vine"]:
            s_rgb = s_rgb[:, ::-1, :].copy()
            s_fg = s_fg[:, ::-1].copy()

        garland_1x = warp_and_quantize_ds_vine(
            s_rgb,
            s_fg,
            w1,
            h1,
            smooth_cy,
            x_min,
            x_max,
            keepout,
            wins=spec["wins"],
            door_box=spec["door_box"],
            split_gap=spec["split_gap"],
            v_scale=0.25,
        )

        if spec["scale_3x"]:
            garland_full = np.array(Image.fromarray(garland_1x, "RGBA").resize((tw * 8, th * 8), Image.Resampling.NEAREST))
        else:
            garland_full = garland_1x

        # Strictly enforce 0 pixel on any walkable 8x8 tile!
        for tx in range(tw):
            for ty in range(th):
                if walk_tile_full[tx, ty]:
                    garland_full[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = 0

        # Save full-room transparent PNG + cropped standalone `.dir` sprite!
        png_name = f"{gid}_verdure.png" if not spec["scale_3x"] else "guilde_destiny_accueil_verdure_1x.png"
        im_save = Image.fromarray(garland_1x if spec["scale_3x"] else garland_full, "RGBA")
        im_save.save(VERD_ART_DIR / png_name)
        im_save.save(USER_VERD_DIR / png_name)

        ys_nz, xs_nz = np.where(garland_full[..., 3] > 0)
        tx0 = int(xs_nz.min()) // 8
        tx1 = (int(xs_nz.max()) // 8) + 1
        ty0 = int(ys_nz.min()) // 8
        ty1 = (int(ys_nz.max()) // 8) + 1
        crop_rgba = garland_full[ty0 * 8 : ty1 * 8, tx0 * 8 : tx1 * 8]
        write_dir(OBJ_DIR / f"{spec['dir_name']}.dir", crop_rgba)

        strip_w_t = tx1 - tx0
        strip_h_t = ty1 - ty0
        atlas_w_tiles = max(atlas_w_tiles, strip_w_t)
        atlas_strips.append((gid, doc, garland_full, tx0, ty0, strip_w_t, atlas_y_cursor_tiles))
        atlas_y_cursor_tiles += strip_h_t + 1  # 1 empty separator tile row between rooms in visual 2D sheet!

    # Build visual 2D `Destiny_Guilde_Verdure.tile` + update `Layers[6] "Fringe"` in all 15 `.rsground` maps!
    entries: list[tuple[int, int, bytes]] = []
    # Anchor (0, 0) if empty
    wrote_origin = False

    for gid, doc, garland_full, tx0, ty0, strip_w_t, atlas_ty_off in atlas_strips:
        g = doc["Object"]
        tw, th = len(g["obstacles"]), len(g["obstacles"][0])
        fringe_grid = [[{"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1} for _ in range(th)] for _ in range(tw)]
        active_cnt = 0

        for tx in range(tw):
            for ty in range(th):
                patch = garland_full[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
                if int(patch[..., 3].max()) == 0:
                    continue
                atx = tx - tx0
                aty = atlas_ty_off + (ty - ty0)
                if atx == 0 and aty == 0:
                    wrote_origin = True
                entries.append((atx, aty, premultiply_png_bytes(sanitize_patch_anti_magenta(patch))))
                fringe_grid[tx][ty] = {
                    "AutoTileset": "",
                    "Associates": [],
                    "Layers": [{"Frames": [{"Sheet": "Destiny_Guilde_Verdure", "TexLoc": {"X": atx, "Y": aty}}], "FrameLength": 60}],
                    "NeighborCode": 0,
                }
                active_cnt += 1

        g["Layers"][6]["Name"] = "Fringe"
        g["Layers"][6]["Layer"] = 4
        g["Layers"][6]["Visible"] = True
        g["Layers"][6]["Tiles"] = fringe_grid
        (GROUND_DIR / f"{gid}.rsground").write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"[OK] {gid:32s}: Fringe={active_cnt:3d} 2D tiles (atlas y={atlas_ty_off}, .dir={strip_w_t*8}px wide)")

    if not wrote_origin:
        entries.insert(0, (0, 0, premultiply_png_bytes(np.zeros((8, 8, 4), dtype=np.uint8))))

    n_tiles = len(entries)
    out_tile = bytearray(struct.pack("<ii", 8, n_tiles))
    off = 8 + 16 * n_tiles
    for atx, aty, blob in entries:
        out_tile += struct.pack("<iiq", atx, aty, off)
        off += 8 + len(blob)
    for _, _, blob in entries:
        out_tile += struct.pack("<q", len(blob)) + blob
    tile_path = TILE_DIR / "Destiny_Guilde_Verdure.tile"
    tile_path.write_bytes(bytes(out_tile))
    print(f"[OK] Wrote visual 2D {tile_path.name}: {n_tiles} tiles ({len(out_tile)} bytes)")


if __name__ == "__main__":
    main()
