#!/usr/bin/env python3
"""
Refonte Pixel-Art Pur Nintendo DS (Zéro Mixel, Zéro Pixel Parasite, Zéro Interstice) — v3 Finale
en Réseau Multicalque Paint.NET (.ora + 8 calques PNG + .tile + .rsground PMDO 0.8.12.0) :

1. Plancher 100 % synthétisé au pixel près (planches 12 px nettes, joints décalés 1 px,
   veinage pixel-art propre — ZÉRO bruit IA, ZÉRO pixel parasite, ZÉRO ombre au sol),
   glissé SOUS le contour organique 1 px des murs et jambages de racines (ZÉRO encoche, ZÉRO interstice).
2. Correction totale de l'interstice Sud (image-4.png) :
   - Suppression totale du trait noir sous alpha blanc qui créait la barre grise baveuse ;
   - Seuil courbe Chunsoft opaque sans interstice, encastré SOUS les deux jambages de racines
     organiques symétrisés (l3_walls / l7_top au-dessus de l1_floor et l6_halo), avec fondu
     concentrique doux du blanc-ivoire au centre vers l'or chaud près des racines.
3. Purification pixel-art intégrale des murs, escalier, fenêtres, racines et lianes :
   - Rampe Chunsoft DS stricte (~20 couleurs pures : 0 gris parasite, 0 bouillie de dégradés) ;
   - Élimination morphologique des amas parasites isolés (1 à 2 px) et symétrisation nette de la plinthe.
"""
from __future__ import annotations

import io
import json
import math
import struct
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

PDN_DIR = Path("/home/user/guilde_destiny_accueil_pdn")
LAYERS_OUT = PDN_DIR / "calques_paintnet"
V3_DIR = Path("/home/user/guilde_destiny_v3")
REPO_ROOT = Path("/var/tmp/PMDO-Destiny")
GAME = REPO_ROOT / "game"

# ==============================================================================
# Palette Pixel-Art Chunsoft DS Stricte (~22 couleurs pures, 0 gris parasite !)
# ==============================================================================
BG_LIGHT_BROWN = (198, 155, 110)   # #C69B6E marron clair chaud extérieur

OUTLINE_WOOD = (42, 23, 14)        # #2A170E trait 1px bois/racines
WOOD_RAMP = np.array([
    [42, 23, 14],    # 0: contour sombre #2A170E
    [70, 38, 20],    # 1: ombre profonde écorce #462614
    [98, 54, 26],    # 2: brun écorce foncé #62361A
    [128, 72, 32],   # 3: châtaignier moyen #804820
    [158, 92, 38],   # 4: bois chaud #9E5C26
    [188, 114, 44],  # 5: chêne doré sombre #BC722C
    [216, 138, 50],  # 6: chêne miel clair #D88A32
    [236, 162, 64],  # 7: rehaut bois ensoleillé #ECA240
    [248, 188, 90],  # 8: éclat corde/bordure #F8BC5A
], dtype=np.uint8)

WIN_RAMP = np.array([
    [220, 152, 54],  # 0: rebord doré fenêtre
    [242, 188, 86],  # 1: ambre lumineux
    [251, 228, 136], # 2: jaune solaire doux
    [255, 245, 186], # 3: ivoire solaire
    [255, 253, 242], # 4: blanc-crème pur vitre
], dtype=np.uint8)

LEAF_RAMP = np.array([
    [26, 52, 22],    # 0: contour feuillage #1A3416 (harmonisé au bois)
    [42, 86, 34],    # 1: vert forêt ombre
    [64, 120, 42],   # 2: vert feuillage franc
    [102, 154, 48],  # 3: vert tendre ensoleillé
    [152, 184, 58],  # 4: olive doré canopée
    [198, 202, 74],  # 5: pointe feuille dorée
], dtype=np.uint8)

# Couleurs nettes du plancher chêne miel pixel-art (planches 12 px, 0 bruit !)
PLANK_SEAM = (142, 74, 22)         # #8E4A16 joint horizontal/vertical 1px
PLANK_TOP_HI = (244, 174, 66)      # #F4AE42 biseau clair haut 1px
PLANK_BODY_A = (230, 148, 42)      # #E6942A corps planche chêne miel A
PLANK_BODY_B = (224, 142, 38)      # #E08E26 corps planche chêne miel B
PLANK_GRAIN = (208, 126, 32)       # #D07E20 veinage fin 1px propre
PLANK_BOT_SH = (196, 114, 28)      # #C4721C biseau bas 1px

# Couleurs Chunsoft OPAQUES / QUANTIFIÉES du halo d'entrée Sud (0 gris sale !)
HALO_LIP_WHITE = (255, 253, 242)   # #FFFDF2 cœur lèvre blanc-ivoire pur
HALO_BAND_1 = (255, 249, 220)      # #FFF9DC cœur lumineux
HALO_BAND_2 = (253, 234, 174)      # #FDEAAE couronne ivoire-or
HALO_BAND_3 = (246, 208, 120)      # #F6D078 couronne miel clair
HALO_BAND_4 = (238, 178, 76)       # #EEB24C fondu chêne solaire


def clean_magenta_mask(arr_rgb: np.ndarray) -> np.ndarray:
    r = arr_rgb[:, :, 0].astype(np.int16)
    g = arr_rgb[:, :, 1].astype(np.int16)
    b = arr_rgb[:, :, 2].astype(np.int16)
    is_mag = ((r > 195) & (g < 85) & (b > 195) & ((r + b - 2 * g) > 220)) | (
        (r > 165) & (g < 105) & (b > 165) & ((r - g) > 75) & ((b - g) > 75)
    )
    fg = ~is_mag
    labeled, ncomp = ndimage.label(fg)
    if ncomp > 1:
        sizes = ndimage.sum(fg, labeled, range(1, ncomp + 1))
        keep = set(np.where(sizes >= 100)[0] + 1)
        fg = np.isin(labeled, list(keep))
    return ~fg


def despill_magenta(arr_rgb: np.ndarray, mag_mask: np.ndarray, fallback_rgb: Tuple[int, int, int]) -> np.ndarray:
    out = arr_rgb.copy()
    fg = ~mag_mask
    dil_mag = ndimage.binary_dilation(mag_mask, iterations=3)
    fringe = fg & dil_mag
    r = out[:, :, 0].astype(np.int16)
    g = out[:, :, 1].astype(np.int16)
    b = out[:, :, 2].astype(np.int16)
    contaminated = fringe & (((r - g) > 28) & ((b - g) > 18))
    if np.any(contaminated):
        pure_fg = fg & (~contaminated)
        _, idx = ndimage.distance_transform_edt(~pure_fg, return_indices=True)
        out[contaminated] = out[idx[0][contaminated], idx[1][contaminated]]
    r2 = out[:, :, 0].astype(np.int16)
    g2 = out[:, :, 1].astype(np.int16)
    b2 = out[:, :, 2].astype(np.int16)
    purp = fg & ((r2 - g2) > 35) & ((b2 - g2) > 25)
    out[purp] = fallback_rgb
    return out


def quantize_to_strict_chunsoft_ramps(rgb1x: np.ndarray, fg1x: np.ndarray, is_foliage: bool = False) -> np.ndarray:
    h, w, _ = rgb1x.shape
    out = np.zeros_like(rgb1x)
    out[~fg1x] = BG_LIGHT_BROWN

    if is_foliage:
        px = rgb1x[fg1x].astype(np.int32)
        d2 = ((px[:, None, :] - LEAF_RAMP[None, :, :].astype(np.int32)) ** 2).sum(axis=-1)
        out[fg1x] = LEAF_RAMP[np.argmin(d2, axis=1)]
        return out

    r = rgb1x[:, :, 0].astype(np.int32)
    g = rgb1x[:, :, 1].astype(np.int32)
    b = rgb1x[:, :, 2].astype(np.int32)

    yy = np.arange(h)[:, None]
    win_mask = fg1x & (yy < int(h * 0.52)) & (r >= 218) & (g >= 182) & (b >= 102)
    wood_mask = fg1x & (~win_mask)

    if np.any(win_mask):
        px_w = rgb1x[win_mask].astype(np.int32)
        d2_w = ((px_w[:, None, :] - WIN_RAMP[None, :, :].astype(np.int32)) ** 2).sum(axis=-1)
        out[win_mask] = WIN_RAMP[np.argmin(d2_w, axis=1)]

    if np.any(wood_mask):
        px_wd = rgb1x[wood_mask].astype(np.float32)
        lum = 0.299 * px_wd[:, 0] + 0.587 * px_wd[:, 1] + 0.114 * px_wd[:, 2]
        ramp_lum = (
            0.299 * WOOD_RAMP[:, 0].astype(np.float32)
            + 0.587 * WOOD_RAMP[:, 1].astype(np.float32)
            + 0.114 * WOOD_RAMP[:, 2].astype(np.float32)
        )
        d_lum = np.abs(lum[:, None] - ramp_lum[None, :])
        out[wood_mask] = WOOD_RAMP[np.argmin(d_lum, axis=1)]

    return out


def remove_parasite_speckles(qarr: np.ndarray, fg_mask: np.ndarray, outline_rgb: Tuple[int, int, int]) -> np.ndarray:
    out = qarr.copy()
    h, w, _ = out.shape
    outline_code = (outline_rgb[0] << 16) | (outline_rgb[1] << 8) | outline_rgb[2]
    struct8 = np.ones((3, 3), dtype=bool)

    for _pass in range(2):
        codes = (
            (out[:, :, 0].astype(np.int32) << 16)
            | (out[:, :, 1].astype(np.int32) << 8)
            | out[:, :, 2].astype(np.int32)
        )
        unique_codes = [int(c) for c in np.unique(codes[fg_mask]) if int(c) != outline_code]
        replace_mask = np.zeros((h, w), dtype=bool)

        for c in unique_codes:
            cmask = fg_mask & (codes == c)
            lbl, n = ndimage.label(cmask, structure=struct8)
            if n == 0:
                continue
            sizes = ndimage.sum(cmask, lbl, range(1, n + 1))
            small_ids = np.where(sizes <= 2)[0] + 1
            if len(small_ids) > 0:
                replace_mask |= np.isin(lbl, small_ids)

        if not np.any(replace_mask):
            break

        ys, xs = np.where(replace_mask)
        new_out = out.copy()
        for y, x in zip(ys, xs):
            y0, y1 = max(0, y - 1), min(h, y + 2)
            x0, x1 = max(0, x - 1), min(w, x + 2)
            nb_fg = fg_mask[y0:y1, x0:x1] & (~replace_mask[y0:y1, x0:x1])
            if not np.any(nb_fg):
                nb_fg = fg_mask[y0:y1, x0:x1]
            nb_codes = codes[y0:y1, x0:x1][nb_fg]
            if len(nb_codes) > 0:
                vals, cnts = np.unique(nb_codes, return_counts=True)
                best_c = int(vals[int(np.argmax(cnts))])
                new_out[y, x] = [(best_c >> 16) & 255, (best_c >> 8) & 255, best_c & 255]
        out = new_out

    eroded = ndimage.binary_erosion(fg_mask, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool))
    out[fg_mask & (~eroded)] = outline_rgb
    out[~fg_mask] = BG_LIGHT_BROWN
    return out


def pixelize_clean_shell(im2x: Image.Image, w1x: int, h1x: int, is_foliage: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    outline_rgb = tuple(int(v) for v in (LEAF_RAMP[0] if is_foliage else WOOD_RAMP[0]))
    arr2x = np.array(im2x.convert("RGB").resize((w1x * 2, h1x * 2), Image.Resampling.LANCZOS))
    mag2x = clean_magenta_mask(arr2x)
    fg_raw = ~mag2x
    lbl, n = ndimage.label(fg_raw)
    if n > 1:
        sizes = ndimage.sum(fg_raw, lbl, range(1, n + 1))
        mag2x = ~(lbl == (int(np.argmax(sizes)) + 1))
    arr2x = despill_magenta(arr2x, mag2x, outline_rgb)

    fg2x = (~mag2x).reshape(h1x, 2, w1x, 2)
    fg1x = fg2x.sum(axis=(1, 3)) >= 2
    fg1x = ndimage.binary_opening(fg1x, structure=np.ones((2, 2)))
    lbl1, n1 = ndimage.label(fg1x)
    if n1 > 1:
        sizes1 = ndimage.sum(fg1x, lbl1, range(1, n1 + 1))
        fg1x = lbl1 == (int(np.argmax(sizes1)) + 1)

    blocks = arr2x.reshape(h1x, 2, w1x, 2, 3).transpose(0, 2, 1, 3, 4).reshape(h1x, w1x, 4, 3)
    fg_blocks = (~mag2x).reshape(h1x, 2, w1x, 2).transpose(0, 2, 1, 3).reshape(h1x, w1x, 4)

    w_mask = fg_blocks.astype(np.float32)
    w_sum = np.maximum(w_mask.sum(axis=2, keepdims=True), 1.0)
    mean_rgb = (blocks.astype(np.float32) * w_mask[:, :, :, None]).sum(axis=2) / w_sum[:, :, 0, None]
    dists = ((blocks.astype(np.float32) - mean_rgb[:, :, None, :]) ** 2).sum(axis=3)
    dists = np.where(fg_blocks, dists, 1e12)
    best_idx = np.argmin(dists, axis=2)

    yy, xx = np.meshgrid(np.arange(h1x), np.arange(w1x), indexing="ij")
    rgb1x = blocks[yy, xx, best_idx].astype(np.uint8)

    qarr = quantize_to_strict_chunsoft_ramps(rgb1x, fg1x, is_foliage=is_foliage)
    qarr = remove_parasite_speckles(qarr, fg1x, outline_rgb)
    return qarr, fg1x


def synthesize_crisp_pixel_art_plank_floor(w: int, h: int, plank_h: int = 12, y_offset: int = 4) -> np.ndarray:
    floor = np.zeros((h, w, 3), dtype=np.uint8)
    offsets_cycle = [0, 38, 16, 54, 26, 62]

    for y in range(h):
        plank_idx = (y + y_offset) // plank_h
        ry = (y + y_offset) % plank_h
        body_col = PLANK_BODY_A if (plank_idx % 2 == 0) else PLANK_BODY_B

        if ry == 0:
            floor[y, :] = PLANK_SEAM
            continue
        if ry == 1:
            floor[y, :] = PLANK_TOP_HI
            continue
        if ry == plank_h - 1:
            floor[y, :] = PLANK_BOT_SH
            continue

        floor[y, :] = body_col

        if ry in (5, 8):
            shift_g = (plank_idx * 29 + ry * 13) % 72
            for gx in range(-shift_g, w, 72):
                seg_len = 26 if ry == 5 else 18
                x0 = max(0, gx + 14)
                x1 = min(w, gx + 14 + seg_len)
                if x1 - x0 >= 8:
                    floor[y, x0:x1] = PLANK_GRAIN

        v_shift = offsets_cycle[plank_idx % len(offsets_cycle)]
        for jx in range(v_shift, w, 72):
            if 1 <= jx < w - 2:
                floor[y, jx] = PLANK_SEAM
                floor[y, jx + 1] = PLANK_TOP_HI

    return floor


def build_vine_sprite(vines_path: Path, tw: int, th: int) -> Image.Image:
    raw = Image.open(vines_path).convert("RGB")
    arr = np.array(raw)
    mag = clean_magenta_mask(arr)
    fg = ~mag
    lbl, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lbl, range(1, n + 1))
    main_fg = lbl == (int(np.argmax(sizes)) + 1)

    ys, xs = np.where(main_fg)
    pad = 24
    x0, x1 = max(0, int(xs.min()) - pad), min(arr.shape[1], int(xs.max()) + pad)
    y0, y1 = max(0, int(ys.min()) - pad), min(arr.shape[0], int(ys.max()) + pad)
    clean_crop = arr.copy()
    clean_crop[~main_fg] = (255, 0, 255)
    sub = Image.fromarray(clean_crop[y0:y1, x0:x1], mode="RGB")

    qarr, fg1x = pixelize_clean_shell(sub, tw, th, is_foliage=True)
    rgba = np.zeros((th, tw, 4), dtype=np.uint8)
    rgba[:, :, :3] = qarr
    rgba[:, :, 3] = np.where(fg1x, 255, 0)
    return Image.fromarray(rgba, mode="RGBA")


# ==============================================================================
# Construction de `guilde_destiny_accueil` (640 x 480) — Zéro Mixel, Zéro Interstice
# ==============================================================================

def build_accueil_clean() -> Tuple[Dict[str, List[np.ndarray]], List[Tuple[str, np.ndarray]], Image.Image, np.ndarray]:
    W, H = 640, 480
    GW, GH = W // 8, H // 8
    LAYERS_OUT.mkdir(parents=True, exist_ok=True)

    im_orig = Image.open("/home/user/uploads/image-3.png").convert("RGB").resize((1280, 960), Image.Resampling.LANCZOS)
    a_orig = np.array(im_orig)
    a_orig[32:58, 566:594] = a_orig[32:58, 686:714][:, ::-1]

    # Cut ONLY the flat tan floor-guide between the sculpted South root jambs at 2x BEFORE pixelizing!
    # Look at image-3.png: inside y_2x=700..916, x_2x=540..740, the sculpted root jambs are rich bark
    # while the flat floor guide is uniform smooth tan (low local gradient & warm tan RGB).
    # Symmetrizing the left sculpted root jamb onto the right root jamb at 2x guarantees 100% organic
    # symmetry AND lets pixelize_clean_shell draw a continuous 1px #2A170E outline along the true organic root curve!
    a_orig[696:940, 640:820] = a_orig[696:940, 460:640][:, ::-1]

    shell_q, shell_mask = pixelize_clean_shell(Image.fromarray(a_orig), W, H, is_foliage=False)

    yy, xx = np.mgrid[0:H, 0:W]
    r_s = shell_q[:, :, 0].astype(int)

    in_candidate_oval = (((xx - 320.0) / 214.0) ** 2 + ((yy - 262.0) / 96.0) ** 2 <= 1.02) & (yy >= 174)
    in_candidate_south = (yy >= 344) & (yy <= 454) & (xx >= 266) & (xx <= 373)
    in_compass_1x = ((xx - 320.0) ** 2 + (yy - 265.0) ** 2) <= 52 ** 2

    is_dark_wall_line = ((r_s <= 102) & (~in_compass_1x)) | (~shell_mask)
    walk_seed_region = (in_candidate_oval | in_candidate_south) & (~is_dark_wall_line)
    lbl_fl, _ = ndimage.label(walk_seed_region)
    floor_interior = lbl_fl == lbl_fl[220, 320]

    # Intersection left/right blocks any single-sided highlight leak into the window baseboards!
    floor_sym = floor_interior & floor_interior[:, ::-1]
    # Remove the tiny dark shadow-tooth at the base of the stair pillars symmetrically (x=282..358, y=180..186)
    floor_sym[181:187, 252:388] |= (floor_interior[181:187, 252:388] | floor_interior[181:187, 252:388][:, ::-1])
    # Silky-smooth Chunsoft oval baseboard curve via circular disk closing + opening (0 jagged teeth!)
    dy_d, dx_d = np.mgrid[-4:5, -4:5]
    disk9 = (dx_d * dx_d + dy_d * dy_d) <= 16
    floor_sym = ndimage.binary_closing(floor_sym, structure=disk9)
    floor_sym = ndimage.binary_opening(floor_sym, structure=disk9)
    floor_sym = ndimage.binary_fill_holes(floor_sym)

    # Smooth monotonic Chunsoft curve for the two South root jambs (0 horizontal spikes!)
    raw_hw = np.zeros(453 - 344, dtype=np.float32)
    for idx_y, y in enumerate(range(344, 453)):
        # Measure inner edge of the sculpted root silhouette from image-3's warm flat guide vs textured bark
        xs_f = np.where(floor_sym[y] & (xx[y] >= 266) & (xx[y] <= 373))[0]
        if len(xs_f) >= 20:
            hw_v = 0.5 * (xs_f.max() - xs_f.min())
        else:
            hw_v = 45.0
        raw_hw[idx_y] = np.clip(hw_v, 41.0, 46.5)
    # Gentle inward rounding right at the bottom root tips (y=442..452: 45.5 -> 42.5), smoothed with Gaussian sigma=4.5
    tip_taper = np.linspace(0.0, 3.0, 14)
    raw_hw[-14:] = np.minimum(raw_hw[-14:], 45.5 - tip_taper)
    smooth_hw = ndimage.gaussian_filter1d(raw_hw, sigma=4.5, mode="nearest")

    south_smooth = np.zeros((H, W), dtype=bool)
    for idx_y, y in enumerate(range(344, 453)):
        hw_i = int(round(float(smooth_hw[idx_y])))
        south_smooth[y, (320 - hw_i) : (320 + hw_i)] = True

    floor_core = floor_sym.copy()
    floor_core[348:, :] = False
    floor_core[344:453, :] |= south_smooth[344:453, :]
    floor_core[yy < 176] = False

    # Wall shell mask = everything in shell_mask EXCEPT floor_core and EXCEPT open doorway below y=451
    door_below_451 = (yy >= 451) & (xx >= 274) & (xx <= 365)
    wall_shell_mask = shell_mask & (~floor_core) & (~door_below_451)
    lbl_ws, n_ws = ndimage.label(wall_shell_mask)
    if n_ws > 1:
        sz_ws = ndimage.sum(wall_shell_mask, lbl_ws, range(1, n_ws + 1))
        wall_shell_mask = lbl_ws == (int(np.argmax(sz_ws)) + 1)

    # Crisp 1px #2A170E inner outline along the ENTIRE smooth wall & root-jamb boundary!
    wall_inner_outline = wall_shell_mask & ndimage.binary_dilation(floor_core | door_below_451, iterations=1)
    shell_q[wall_inner_outline] = OUTLINE_WOOD

    # Walkable 8x8 collision grid
    walk_grid = np.zeros((GW, GH), dtype=bool)
    poly_img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(poly_img)
    chamber_poly = [
        (232, 180), (288, 180), (288, 120), (352, 120), (352, 180), (408, 180),
        (464, 200), (504, 228), (520, 260), (504, 292), (464, 320), (408, 340),
        (360, 344), (360, 448), (280, 448), (280, 344), (232, 340), (176, 320),
        (136, 292), (120, 260), (136, 228), (176, 200),
    ]
    dr.polygon(chamber_poly, fill=255)
    dr.polygon([(256, 160), (287, 160), (287, 186), (260, 186)], fill=0)
    dr.polygon([(353, 160), (384, 160), (380, 186), (353, 186)], fill=0)
    walk_px = np.array(poly_img) > 128
    for tx in range(GW):
        for ty in range(GH):
            walk_grid[tx, ty] = bool(walk_px[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8].all())
    walk_tiles_px = np.repeat(np.repeat(walk_grid.T, 8, axis=0), 8, axis=1)

    # --------------------------------------------------------------------------
    # Géométrie Chunsoft EoS du Seuil Courbe & Halo d'Entrée Sud (0 interstice !)
    # --------------------------------------------------------------------------
    # Measure exact inner doorway opening at y=450 between left & right sculpted root jambs:
    xs_open = np.where(~wall_shell_mask[450] & (xx[450] >= 266) & (xx[450] <= 373))[0]
    x_left_open, x_right_open = int(xs_open.min()), int(xs_open.max())
    cx_h = 319.5
    # Extend +4px UNDER both sculpted root jambs (which sit on l3_walls / l7_top ABOVE l1_floor & l6_halo!)
    # -> ZERO gap, ZERO corner poke, 100% organic root overlap!
    half_w_vis = 0.5 * (x_right_open - x_left_open)
    half_w_under = half_w_vis + 4.0

    nx_vis = (xx - cx_h) / max(half_w_vis, 1.0)
    nx_under = (xx - cx_h) / half_w_under
    in_door_under = np.abs(nx_under) <= 1.0

    # Gentle Chunsoft convex doorway threshold curve (y=451 at the root jambs -> y=455 at center x=320)
    lip_bot_y = 451.0 + 4.0 * np.maximum(0.0, 1.0 - nx_vis * nx_vis)
    lip_top_y = lip_bot_y - 3.0

    # Floor underlap extends 3px UNDER all walls & root jambs AND fills down to lip_bot_y -> ZERO interstice!
    door_plank_zone = in_door_under & (yy >= 348) & (yy <= np.floor(lip_bot_y))
    floor_underlap = (ndimage.binary_dilation(floor_core, iterations=3) & (wall_shell_mask | floor_core)) | door_plank_zone
    floor_underlap[yy < 174] = False
    # Never leak outside the outer silhouette of the root jambs!
    outer_hull = wall_shell_mask | floor_core | (in_door_under & (yy >= 348) & (yy <= np.floor(lip_bot_y)))
    floor_underlap &= outer_hull

    pure_planks = synthesize_crisp_pixel_art_plank_floor(W, H, plank_h=12, y_offset=2)
    bevel_ring = floor_core & ndimage.binary_dilation(wall_shell_mask, iterations=1) & (yy < 448)
    pure_planks[bevel_ring] = PLANK_SEAM

    # --------------------------------------------------------------------------
    # Construction des 8 Calques Paint.NET :
    #   Ordre de superposition :
    #     00 fond -> 01 plancher -> 02 ombre escalier -> 06 halo Sud (SOUS les racines !) -> 03 murs/racines -> 04 verdure -> 05 aura fenêtres -> 07 racines Top !
    #   Attends : dans le .ora et dans PMDO, si on clippe 06_halo sur (~wall_shell_mask), alors MÊME AU-DESSUS de 03,
    #   les jambages de racines (03 et 07) gardent 100 % de leur contour organique 1 px #2A170E sans AUCUN débordement blanc !
    # --------------------------------------------------------------------------
    l0_bg = np.zeros((H, W, 4), dtype=np.uint8)
    l0_bg[:, :] = [BG_LIGHT_BROWN[0], BG_LIGHT_BROWN[1], BG_LIGHT_BROWN[2], 255]
    # Keep l0_bg 100% #C69B6E under the open South doorway sill so ZERO dark pixel ever peeks below the white lip!
    l0_bg[(wall_shell_mask | floor_core) & (~(in_door_under & (yy >= 444)))] = [52, 30, 16, 255]

    l1_floor = np.zeros((H, W, 4), dtype=np.uint8)
    l1_floor[floor_underlap, :3] = pure_planks[floor_underlap]
    l1_floor[floor_underlap, 3] = 255

    m_top = wall_shell_mask & (~walk_tiles_px) & (
        (yy >= 352) | ((yy >= 312) & ((xx <= 148) | (xx >= 492)))
    )
    m_wall_bot = wall_shell_mask & (~m_top)

    in_arch = (((xx - 320.0) / 27.0) ** 2 + ((yy - 114.0) / 30.0) ** 2 <= 1.0) & (yy >= 82) & (yy <= 128)
    m_stair_depth = m_wall_bot & in_arch & (shell_q[:, :, 0] <= 98)
    m_walls_main = m_wall_bot & (~m_stair_depth)

    l2_stair = np.zeros((H, W, 4), dtype=np.uint8)
    l2_stair[m_stair_depth, :3] = shell_q[m_stair_depth]
    l2_stair[m_stair_depth, 3] = 255

    l3_walls = np.zeros((H, W, 4), dtype=np.uint8)
    l3_walls[m_walls_main, :3] = shell_q[m_walls_main]
    l3_walls[m_walls_main, 3] = 255

    l7_top = np.zeros((H, W, 4), dtype=np.uint8)
    l7_top[m_top, :3] = shell_q[m_top]
    l7_top[m_top, 3] = 255

    vine_spr = build_vine_sprite(PDN_DIR / "pdn_lianes_suspendues_magenta.png", 132, 104)
    vine_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vine_r = vine_spr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    vine_canvas.paste(vine_spr, (156, 12), vine_spr)
    vine_canvas.paste(vine_r, (352, 12), vine_r)
    l4_vines = np.array(vine_canvas, dtype=np.uint8)
    win_glass = (shell_q[:, :, 0] >= 240) & (shell_q[:, :, 1] >= 220) & (yy < 205)
    outside_room = ~ndimage.binary_dilation(wall_shell_mask | floor_core, iterations=5)
    l4_vines[win_glass | outside_room, 3] = 0

    sun_frames: List[np.ndarray] = []
    w_d1 = np.sqrt(((xx - 158.0) / 48.0) ** 2 + ((yy - 136.0) / 58.0) ** 2)
    w_d2 = np.sqrt(((xx - 482.0) / 48.0) ** 2 + ((yy - 136.0) / 58.0) ** 2)
    w_min = np.minimum(w_d1, w_d2)
    aura_core = wall_shell_mask & (yy < 204) & (w_min <= 0.58)
    aura_outer = wall_shell_mask & (yy < 204) & (w_min > 0.58) & (w_min <= 0.90)
    motes = [
        (178, 158, 0), (194, 174, 4), (166, 180, 8),
        (462, 158, 2), (446, 174, 6), (474, 180, 10),
    ]
    for ph in range(12):
        fr = np.zeros((H, W, 4), dtype=np.uint8)
        breath = 0.5 + 0.5 * math.sin(2.0 * math.pi * ph / 12.0)
        fr[aura_core] = [255, 248, 198, int(round((32 + 12 * breath) / 4.0) * 4)]
        fr[aura_outer] = [255, 242, 182, int(round((16 + 8 * breath) / 4.0) * 4)]
        for mx0, my0, off in motes:
            t = (ph + off) % 12
            dx = int(round(2.0 * math.cos(2.0 * math.pi * t / 12.0)))
            dy = int(round(2.0 * math.sin(2.0 * math.pi * t / 12.0)))
            ma = 96 + int(64 * (0.5 + 0.5 * math.sin(2.0 * math.pi * t / 12.0)))
            px_x, px_y = mx0 + dx, my0 + dy
            if 0 <= px_x < W - 1 and 0 <= px_y < H - 1 and wall_shell_mask[px_y, px_x]:
                fr[px_y : px_y + 2, px_x : px_x + 2] = [255, 252, 214, ma]
        sun_frames.append(fr)

    # 06 : Halo Chunsoft Concentrique + Lèvre Courbe Opaque (strictement hors wall_shell_mask = 0 débordement !)
    open_south_canvas = (~wall_shell_mask) & in_door_under & (yy >= 390) & (yy <= np.floor(lip_bot_y))
    lip_mask = open_south_canvas & (yy >= np.floor(lip_top_y))
    lip_warm_rim = (~wall_shell_mask) & in_door_under & (yy == np.floor(lip_bot_y) + 1) & (np.abs(nx_vis) <= 0.96)

    # Concentric radial distance from doorway center (cx=319.5, cy=453.0)
    rx_arc = half_w_vis * 0.98
    ry_arc = half_w_vis * 0.90
    rad_arc = np.sqrt(((xx - cx_h) / rx_arc) ** 2 + np.maximum(0.0, (453.0 - yy) / ry_arc) ** 2)

    # Notice how tapering the curved lip with the EXACT SAME concentric warmth near the roots
    # (pure ivory-white #FFFDF2 in center |nx_vis|<=0.58 -> warm cream #FFF6CE -> sunlit gold #FBE29A right at the root bark)
    # eliminates any white corner poke AND keeps 100% opaque zero-interstice contact!
    lip_c0 = lip_mask & (np.abs(nx_vis) <= 0.56)
    lip_c1 = lip_mask & (np.abs(nx_vis) > 0.56) & (np.abs(nx_vis) <= 0.82)
    lip_c2 = lip_mask & (np.abs(nx_vis) > 0.82)

    in_halo_planks = open_south_canvas & (~lip_mask)
    arc_b1 = in_halo_planks & (rad_arc <= 0.36)
    arc_b2 = in_halo_planks & (rad_arc > 0.36) & (rad_arc <= 0.62)
    arc_b3 = in_halo_planks & (rad_arc > 0.62) & (rad_arc <= 0.86)
    arc_b4 = in_halo_planks & (rad_arc > 0.86) & (rad_arc <= 1.04)

    inout_frames: List[np.ndarray] = []
    for ph in range(12):
        fr = np.zeros((H, W, 4), dtype=np.uint8)
        pulse = 0.5 + 0.5 * math.sin(2.0 * math.pi * ph / 12.0)
        fr[arc_b4] = [HALO_BAND_4[0], HALO_BAND_4[1], HALO_BAND_4[2], int(round((56 + 16 * pulse) / 4.0) * 4)]
        fr[arc_b3] = [HALO_BAND_3[0], HALO_BAND_3[1], HALO_BAND_3[2], int(round((104 + 18 * pulse) / 4.0) * 4)]
        fr[arc_b2] = [HALO_BAND_2[0], HALO_BAND_2[1], HALO_BAND_2[2], int(round((164 + 20 * pulse) / 4.0) * 4)]
        fr[arc_b1] = [HALO_BAND_1[0], HALO_BAND_1[1], HALO_BAND_1[2], int(round((220 + 20 * pulse) / 4.0) * 4)]
        # 100% OPAQUE Chunsoft curved threshold lip (0 grey gap, tapered gold-to-ivory into root jambs!)
        fr[lip_warm_rim] = [226, 186, 124, 255]
        fr[lip_c2] = [250, 224, 152, 255]
        fr[lip_c1] = [255, 245, 204, 255]
        fr[lip_c0] = [HALO_LIP_WHITE[0], HALO_LIP_WHITE[1], HALO_LIP_WHITE[2], 255]
        inout_frames.append(fr)

    pdn_static_layers: List[Tuple[str, np.ndarray]] = [
        ("fond_marron_clair", l0_bg),
        ("plancher_chene_pixel_art_pur", l1_floor),
        ("profondeur_escalier_nord", l2_stair),
        ("parois_bois_escalier_et_fenetres", l3_walls),
        ("verdure_et_lianes_suspendues", l4_vines),
        ("lumiere_fenetres_et_pollen", sun_frames[3]),
        ("halo_entree_sud_chunsoft_sans_interstice", inout_frames[3]),
        ("avant_plan_racines_sud_top", l7_top),
    ]
    for idx, (lname, larr) in enumerate(pdn_static_layers):
        Image.fromarray(larr, "RGBA").save(LAYERS_OUT / f"{idx:02d}_{lname}.png")

    stack_root = ET.Element("image", w=str(W), h=str(H), version="0.0.6")
    stack_el = ET.SubElement(stack_root, "stack")
    comp = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    for _, l_arr in pdn_static_layers:
        comp = Image.alpha_composite(comp, Image.fromarray(l_arr, "RGBA"))

    with zipfile.ZipFile(PDN_DIR / "guilde_destiny_accueil_multicalque.ora", "w") as zf:
        zf.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        for idx in range(len(pdn_static_layers) - 1, -1, -1):
            lname, l_arr = pdn_static_layers[idx]
            src_rel = f"data/{idx:02d}_{lname}.png"
            ET.SubElement(
                stack_el, "layer", name=f"{idx:02d}_{lname}", src=src_rel,
                x="0", y="0", opacity="1.0", visibility="visible", **{"composite-op": "svg:src-over"},
            )
            bio = io.BytesIO()
            Image.fromarray(l_arr, "RGBA").save(bio, format="PNG")
            zf.writestr(src_rel, bio.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
        ET.indent(stack_root, space="  ")
        zf.writestr("stack.xml", ET.tostring(stack_root, encoding="utf-8", xml_declaration=True), compress_type=zipfile.ZIP_DEFLATED)
        b_full = io.BytesIO()
        comp.save(b_full, format="PNG")
        zf.writestr("mergedimage.png", b_full.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
        b_th = io.BytesIO()
        comp.resize((256, 192), Image.Resampling.NEAREST).save(b_th, format="PNG")
        zf.writestr("Thumbnails/thumbnail.png", b_th.getvalue(), compress_type=zipfile.ZIP_DEFLATED)

    comp_rgb = comp.convert("RGB")
    comp_rgb.save(PDN_DIR / "rendu_final_accueil_marron_clair_1x.png")

    layers_pmdo = {
        "00_fond_eos_et_assise": [l0_bg],
        "01_parquet_chene_et_medaillon": [l1_floor],
        "02_ombres_et_profondeur_nord": [l2_stair],
        "03_parois_nervures_et_fenetres": [l3_walls],
        "04_verdure_separee": [l4_vines],
        "05_rayons_fenetres_12_phases": sun_frames,
        "06_lumiere_entree_sortie_12_phases": inout_frames,
        "07_couronne_avant_plan_top": [l7_top],
    }
    return layers_pmdo, pdn_static_layers, comp_rgb, walk_grid


# ==============================================================================
# Purification Pixel-Art identique de `guilde_destiny_missions` (1112 x 760)
# ==============================================================================

def build_missions_clean() -> Tuple[Dict[str, List[np.ndarray]], Image.Image, np.ndarray]:
    W, H = 1112, 760
    GW, GH = W // 8, H // 8

    opt2 = Image.open(V3_DIR / "grande_piece_deux_murs_magenta.png").convert("RGB").resize((1112, 712), Image.Resampling.LANCZOS)
    base = np.full((H, W, 3), (255, 0, 255), dtype=np.uint8)
    base[48:, :] = np.array(opt2)
    cr = np.array(Image.open(V3_DIR / "grande_piece_couronne_sans_motif_magenta.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS))

    yy, xx = np.mgrid[0:H, 0:W]
    w_rim = np.clip((72.0 - yy) / 18.0, 0.0, 1.0)
    wx = np.clip(1.0 - np.maximum(0.0, np.abs(xx - 556.0) - 68.0) / 18.0, 0.0, 1.0)
    wy = np.clip((136.0 - yy) / 16.0, 0.0, 1.0)
    blend = np.maximum(w_rim, wx * wy)[:, :, None]
    merged = np.clip(cr.astype(np.float32) * blend + base.astype(np.float32) * (1.0 - blend), 0, 255).astype(np.uint8)

    shell_q, shell_mask = pixelize_clean_shell(Image.fromarray(merged), W, H, is_foliage=False)

    r_s = shell_q[:, :, 0].astype(int)
    in_cand = (((xx - 556.0) / 456.0) ** 2 + ((yy - 446.0) / 232.0) ** 2 <= 1.02) & (yy >= 232)
    is_dark_line = (r_s <= 102) | (~shell_mask)
    lbl_m, _ = ndimage.label(in_cand & (~is_dark_line))
    fl_core = lbl_m == lbl_m[430, 556]
    fl_core = fl_core & fl_core[:, ::-1]
    dy_m, dx_m = np.mgrid[-4:5, -4:5]
    disk9_m = (dx_m * dx_m + dy_m * dy_m) <= 16
    fl_core = ndimage.binary_closing(fl_core, structure=disk9_m)
    fl_core = ndimage.binary_opening(fl_core, structure=disk9_m)
    fl_core = ndimage.binary_fill_holes(fl_core)
    fl_core[yy < 236] = False

    wall_shell = shell_mask & (~fl_core)
    wall_touch = wall_shell & ndimage.binary_dilation(fl_core, iterations=1)
    shell_q[wall_touch] = OUTLINE_WOOD

    fl_underlap = ndimage.binary_dilation(fl_core, iterations=3) & shell_mask
    fl_underlap[yy < 235] = False

    pure_planks = synthesize_crisp_pixel_art_plank_floor(W, H, plank_h=12, y_offset=2)
    bevel_ring = fl_core & ndimage.binary_dilation(wall_shell, iterations=1)
    pure_planks[bevel_ring] = PLANK_SEAM

    inner_safe = ndimage.binary_erosion(shell_mask, structure=np.ones((68, 68)))
    walk_grid = np.zeros((GW, GH), dtype=bool)
    for tx in range(GW):
        px = tx * 8 + 4
        for ty in range(GH):
            py = ty * 8 + 4
            if (512 <= px <= 600) and (196 <= py <= 256):
                walk_grid[tx, ty] = True
                continue
            if py < 224:
                continue
            if py < 264 and (px < 224 or px > 888):
                if ((px - 556.0) / 428.0) ** 2 + ((py - 442.0) / 224.0) ** 2 > 0.96:
                    continue
            if inner_safe[min(py, H - 1), min(px, W - 1)]:
                walk_grid[tx, ty] = True
    walk_tiles_px = np.repeat(np.repeat(walk_grid.T, 8, axis=0), 8, axis=1)

    l0_bg = np.zeros((H, W, 4), dtype=np.uint8)
    l0_bg[:, :] = [BG_LIGHT_BROWN[0], BG_LIGHT_BROWN[1], BG_LIGHT_BROWN[2], 255]
    l0_bg[shell_mask] = [52, 30, 16, 255]

    l1_floor = np.zeros((H, W, 4), dtype=np.uint8)
    l1_floor[fl_underlap, :3] = pure_planks[fl_underlap]
    l1_floor[fl_underlap, 3] = 255

    m_top = wall_shell & (~walk_tiles_px) & (
        (yy >= 540) | ((yy >= 460) & ((xx <= 180) | (xx >= 932)))
    )
    m_wall_bot = wall_shell & (~m_top)
    in_arch = (((xx - 556.0) / 42.0) ** 2 + ((yy - 168.0) / 36.0) ** 2 <= 1.0) & (yy >= 126) & (yy <= 186)
    m_stair = m_wall_bot & in_arch & (shell_q[:, :, 0] <= 98)
    m_walls_main = m_wall_bot & (~m_stair)

    l2_stair = np.zeros((H, W, 4), dtype=np.uint8)
    l2_stair[m_stair, :3] = shell_q[m_stair]
    l2_stair[m_stair, 3] = 255

    l3_walls = np.zeros((H, W, 4), dtype=np.uint8)
    l3_walls[m_walls_main, :3] = shell_q[m_walls_main]
    l3_walls[m_walls_main, 3] = 255

    l7_top = np.zeros((H, W, 4), dtype=np.uint8)
    l7_top[m_top, :3] = shell_q[m_top]
    l7_top[m_top, 3] = 255

    vine_spr = build_vine_sprite(PDN_DIR / "pdn_lianes_suspendues_magenta.png", 148, 112)
    vine_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vine_r = vine_spr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    vine_canvas.paste(vine_spr, (304, 18), vine_spr)
    vine_canvas.paste(vine_r, (660, 18), vine_r)
    l4_vines = np.array(vine_canvas, dtype=np.uint8)
    win_glass = (shell_q[:, :, 0] >= 240) & (shell_q[:, :, 1] >= 220) & (yy < 245)
    outside_room = ~ndimage.binary_dilation(shell_mask, iterations=5)
    l4_vines[win_glass | outside_room, 3] = 0

    sun_frames: List[np.ndarray] = []
    w_d1 = np.sqrt(((xx - 172.0) / 60.0) ** 2 + ((yy - 196.0) / 72.0) ** 2)
    w_d2 = np.sqrt(((xx - 940.0) / 60.0) ** 2 + ((yy - 196.0) / 72.0) ** 2)
    w_min = np.minimum(w_d1, w_d2)
    aura_core = wall_shell & (yy < 248) & (w_min <= 0.58)
    aura_outer = wall_shell & (yy < 248) & (w_min > 0.58) & (w_min <= 0.90)
    for ph in range(12):
        fr = np.zeros((H, W, 4), dtype=np.uint8)
        breath = 0.5 + 0.5 * math.sin(2.0 * math.pi * ph / 12.0)
        fr[aura_core] = [255, 248, 198, int(round((32 + 12 * breath) / 4.0) * 4)]
        fr[aura_outer] = [255, 242, 182, int(round((16 + 8 * breath) / 4.0) * 4)]
        sun_frames.append(fr)

    inout_frames = [np.zeros((H, W, 4), dtype=np.uint8) for _ in range(12)]

    comp = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    for arr_l in [l0_bg, l1_floor, l2_stair, l3_walls, l4_vines, sun_frames[3], inout_frames[3], l7_top]:
        comp = Image.alpha_composite(comp, Image.fromarray(arr_l, "RGBA"))

    return {
        "00_fond_eos_et_assise": [l0_bg],
        "01_parquet_chene_et_medaillon": [l1_floor],
        "02_ombres_et_profondeur_nord": [l2_stair],
        "03_parois_nervures_et_fenetres": [l3_walls],
        "04_verdure_separee": [l4_vines],
        "05_rayons_fenetres_12_phases": sun_frames,
        "06_lumiere_entree_sortie_12_phases": inout_frames,
        "07_couronne_avant_plan_top": [l7_top],
    }, comp.convert("RGB"), walk_grid


# ==============================================================================
# Compilation PMDO 0.8.12.0 (.tile + .rsground)
# ==============================================================================

def premultiply_patch_bytes(patch_rgba: np.ndarray) -> bytes:
    arr = patch_rgba.astype(np.float32)
    alpha = arr[..., 3:4] / 255.0
    arr[..., :3] = np.clip(np.round(arr[..., :3] * alpha), 0, 255)
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def make_marker(name: str, x: int, y: int, direction: int) -> dict:
    return {
        "EntName": name, "Direction": direction, "EntEnabled": True,
        "EntOrder": 0, "InteractOrder": 0, "triggerType": 0,
        "Collider": {"X": x, "Y": y, "Width": 16, "Height": 16},
    }


def make_touch_obj(name: str, x: int, y: int, w: int, h: int) -> dict:
    anim_proto = {
        "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
        "AnimIndex": "", "FrameTime": 1, "StartFrame": -1, "EndFrame": -1,
        "AnimDir": -1, "Alpha": 255, "AnimFlip": 0,
    }
    return {
        "EntName": name, "Direction": 0, "EntEnabled": True, "EntOrder": 0,
        "InteractOrder": 0, "triggerType": 2, "ObjectAnim": dict(anim_proto),
        "Passable": False, "CurrentAnim": dict(anim_proto),
        "AnimTime": {"Ticks": 0}, "Cycles": 0, "DrawOffset": {"X": 0, "Y": 0},
        "Collider": {"X": x, "Y": y, "Width": w, "Height": h},
    }


def compile_room_pmdo(
    asset_name: str,
    sheet_name: str,
    name_en: str,
    name_fr: str,
    comment_fr: str,
    w: int,
    h: int,
    layers_dict: Dict[str, List[np.ndarray]],
    walk_grid: np.ndarray,
    markers: List[dict],
    ground_objects: List[dict],
) -> None:
    gw, gh = w // 8, h // 8
    rs_ref_path = GAME / "Data/Ground/guilde_destiny_accueil.rsground"
    if not rs_ref_path.exists():
        rs_ref_path = PDN_DIR / "guilde_destiny_accueil.rsground"
    orig_rs = json.loads(rs_ref_path.read_text(encoding="utf-8-sig"))
    rand_proto = orig_rs["Object"]["rand"]
    empty_tile_proto = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}

    ATLAS_COLS = 32
    patch_to_loc: Dict[bytes, Tuple[int, int]] = {}
    ordered_patches: List[Tuple[int, int, np.ndarray]] = []

    zero_patch = np.zeros((8, 8, 4), dtype=np.uint8)
    patch_to_loc[zero_patch.tobytes()] = (0, 0)
    ordered_patches.append((0, 0, zero_patch))

    def get_loc(patch: np.ndarray) -> Tuple[int, int]:
        key = patch.tobytes()
        if key in patch_to_loc:
            return patch_to_loc[key]
        idx = len(ordered_patches)
        loc = (idx % ATLAS_COLS, idx // ATLAS_COLS)
        patch_to_loc[key] = loc
        ordered_patches.append((loc[0], loc[1], patch.copy()))
        return loc

    layer_specs = [
        ("00 fond marron clair et assise", "00_fond_eos_et_assise", 0, 60),
        ("01 parquet chene dore pixel-art pur", "01_parquet_chene_et_medaillon", 0, 60),
        ("02 profondeur arche escalier nord", "02_ombres_et_profondeur_nord", 0, 60),
        ("03 parois bois escalier et fenetres cintrees", "03_parois_nervures_et_fenetres", 0, 60),
        ("04 verdure separee", "04_verdure_separee", 0, 60),
        ("05 rayons solaires fenetres 12 phases", "05_rayons_fenetres_12_phases", 0, 8),
        ("06 halo entree sud centre 12 phases", "06_lumiere_entree_sortie_12_phases", 0, 8),
        ("07 couronne avant-plan racines (Top)", "07_couronne_avant_plan_top", 4, 60),
    ]

    rs_layers = []
    for display_name, key_name, layer_flag, frame_len in layer_specs:
        frames_imgs = layers_dict[key_name]
        n_frames = len(frames_imgs)
        cols = []
        for tx in range(gw):
            col = []
            x0, x1 = tx * 8, (tx + 1) * 8
            for ty in range(gh):
                y0, y1 = ty * 8, (ty + 1) * 8
                patches = [fr[y0:y1, x0:x1] for fr in frames_imgs]
                if all(int(p[..., 3].max()) == 0 for p in patches):
                    col.append(dict(empty_tile_proto))
                    continue
                if n_frames > 1 and all(np.array_equal(patches[0], p) for p in patches[1:]):
                    lx, ly = get_loc(patches[0])
                    frames_json = [{"Sheet": sheet_name, "TexLoc": {"X": lx, "Y": ly}}]
                    fl = 60
                else:
                    frames_json = [
                        {"Sheet": sheet_name, "TexLoc": {"X": get_loc(p)[0], "Y": get_loc(p)[1]}}
                        for p in patches
                    ]
                    fl = frame_len
                col.append({
                    "AutoTileset": "", "Associates": [],
                    "Layers": [{"Frames": frames_json, "FrameLength": fl}], "NeighborCode": 0,
                })
            cols.append(col)
        rs_layers.append({"Name": display_name, "Layer": layer_flag, "Visible": True, "Tiles": cols})

    n_tiles = len(ordered_patches)
    png_blobs = [premultiply_patch_bytes(p) for _, _, p in ordered_patches]
    out_tile = bytearray()
    out_tile += struct.pack("<ii", 8, n_tiles)
    offset = 8 + n_tiles * 16
    for (lx, ly, _), blob in zip(ordered_patches, png_blobs):
        out_tile += struct.pack("<iiq", lx, ly, offset)
        offset += 8 + len(blob)
    for blob in png_blobs:
        out_tile += struct.pack("<q", len(blob))
        out_tile += blob

    (GAME / f"Content/Tile/{sheet_name}.tile").write_bytes(bytes(out_tile))
    (PDN_DIR / f"{sheet_name}.tile").write_bytes(bytes(out_tile))

    obstacles = [
        [{"Bounds": {"X": tx * 8, "Y": ty * 8, "Width": 8, "Height": 8}, "Tags": 0 if walk_grid[tx, ty] else 1} for ty in range(gh)]
        for tx in range(gw)
    ]

    ground_doc = {
        "Version": "0.8.12.0",
        "Object": {
            "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
            "TexSize": 1,
            "Name": {"DefaultText": name_en, "LocalTexts": {"fr": name_fr}},
            "Released": True,
            "Comment": comment_fr,
            "obstacles": obstacles,
            "rand": dict(rand_proto),
            "Status": {},
            "Background": {"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []},
            "BlankBG": {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1},
            "Layers": rs_layers,
            "AssetName": asset_name,
            "Music": "Guildmaster.ogg",
            "EdgeView": 1,
            "NoSwitching": False,
            "ViewCenter": None,
            "ViewOffset": {"X": 0, "Y": 0},
            "ActiveChar": None,
            "Decorations": [],
            "Entities": [{
                "Name": "Entities", "Visible": True, "MapChars": [],
                "GroundObjects": ground_objects, "Spawners": [], "Markers": markers,
            }],
        },
    }
    rs_txt = json.dumps(ground_doc, ensure_ascii=False, indent=2) + "\n"
    (GAME / f"Data/Ground/{asset_name}.rsground").write_text(rs_txt, encoding="utf-8")
    (PDN_DIR / f"{asset_name}.rsground").write_text(rs_txt, encoding="utf-8")
    print(f"[OK] {asset_name} ({w}x{h}): {sheet_name}.tile ({n_tiles} tuiles 8x8 pures).")


def build_showcase_board(pdn_layers: List[Tuple[str, np.ndarray]], acc_rgb: Image.Image) -> None:
    W_B, H_B = 1480, 1080
    board = Image.new("RGB", (W_B, H_B), (36, 26, 20))
    dr = ImageDraw.Draw(board)

    dr.text((28, 16), "Rendu 1:1 Pur Pixel-Art DS - Accueil Guilde Destiny (640x480, 0 mixel, 0 pixel parasite, 0 interstice)", fill=(252, 236, 196))
    board.paste(acc_rgb, (28, 42))

    dr.text((696, 16), "Zoom 4x Seuil Sud : ZERO interstice + Plancher 12px net + Halo Chunsoft", fill=(255, 228, 168))
    z_s4 = acc_rgb.crop((258, 396, 382, 468)).resize((124 * 4, 72 * 4), Image.Resampling.NEAREST)
    board.paste(z_s4, (696, 42))

    dr.text((696, 344), "Zoom 2x Mur + Fenetres + Escalier + Plancher (rampe Chunsoft pure, 0 parasite)", fill=(204, 244, 196))
    z_n2 = acc_rgb.crop((140, 104, 500, 194)).resize((720, 180), Image.Resampling.NEAREST)
    board.paste(z_n2, (696, 366))

    dr.text((28, 552), "Reseau Multicalque Paint.NET (.ora OpenRaster + 8 calques RGBA nets sans pixels parasites) :", fill=(252, 236, 196))
    yy, xx = np.mgrid[0:216, 0:320]
    chk = np.where(((xx // 8) + (yy // 8)) % 2 == 0, 224, 192).astype(np.uint8)
    chk_rgba = np.stack([chk, chk, chk, np.full_like(chk, 255)], axis=-1)

    labels_fr = [
        "00. Fond marron clair uni (#C69B6E)",
        "01. Plancher pixel-art pur 12px (0 bruit)",
        "02. Profondeur arche escalier Nord",
        "03. Parois, escalier & fenetres (rampe DS)",
        "04. Verdure & lianes (rampe DS 6 tons)",
        "05. Lumiere fenetres & pollen (12 ph.)",
        "06. Halo Sud Chunsoft (0 interstice)",
        "07. Couronne racines avant-plan (Top)",
    ]
    for i, ((_, larr), lbl) in enumerate(zip(pdn_layers, labels_fr)):
        col = i % 4
        row = i // 4
        bx = 28 + col * 360
        by = 580 + row * 244
        dr.text((bx, by), lbl, fill=(238, 218, 184))
        thumb_l = Image.fromarray(larr, "RGBA").resize((320, 216), Image.Resampling.NEAREST)
        merged_t = Image.alpha_composite(Image.fromarray(chk_rgba, "RGBA"), thumb_l).convert("RGB")
        board.paste(merged_t, (bx, by + 20))

    board.save("/home/user/apercu_accueil_paintnet_multicalque.png")


def main() -> None:
    acc_layers, pdn_layers, acc_rgb, acc_walk = build_accueil_clean()
    compile_room_pmdo(
        asset_name="guilde_destiny_accueil",
        sheet_name="Destiny_Guilde_Accueil",
        name_en="Destiny Guild - Reception Hall",
        name_fr="Grande Guilde — Salle d’accueil",
        comment_fr="Salle d'accueil pixel-art pur DS (640x480, rampe Chunsoft stricte, plancher 12px sans pixel parasite, halo Sud Chunsoft sans interstice, fond marron clair #C69B6E).",
        w=640, h=480,
        layers_dict=acc_layers,
        walk_grid=acc_walk,
        markers=[
            make_marker("EntreeSudMarker", 312, 384, 4),
            make_marker("CentreMedaillonMarker", 312, 248, 0),
            make_marker("EscalierNordMarker", 312, 160, 0),
        ],
        ground_objects=[
            make_touch_obj("SortieGuilde", 280, 428, 80, 20),
            make_touch_obj("EscalierNord", 288, 120, 64, 18),
        ],
    )

    mis_layers, mis_rgb, mis_walk = build_missions_clean()
    mis_rgb.save(PDN_DIR / "rendu_final_missions_marron_clair_1x.png")
    compile_room_pmdo(
        asset_name="guilde_destiny_missions",
        sheet_name="Destiny_Guilde_Missions",
        name_en="Destiny Guild - Main Mission Hall",
        name_fr="Grande Guilde — Grande Salle",
        comment_fr="Grande Salle aux deux murs pixel-art pur DS (1112x760, rampe Chunsoft stricte, plancher 12px sans pixel parasite, fond marron clair #C69B6E).",
        w=1112, h=760,
        layers_dict=mis_layers,
        walk_grid=mis_walk,
        markers=[
            make_marker("ArriveeDepuisAccueilMarker", 544, 248, 0),
            make_marker("CentreSalleMarker", 544, 432, 0),
            make_marker("MurGaucheMarker", 368, 240, 4),
            make_marker("MurDroitMarker", 720, 240, 4),
        ],
        ground_objects=[
            make_touch_obj("EscalierNord", 512, 196, 88, 20),
        ],
    )

    build_showcase_board(pdn_layers, acc_rgb)
    print("[OK] Purification pixel-art DS v3 + suppression totale d'interstice terminées.")


if __name__ == "__main__":
    main()
