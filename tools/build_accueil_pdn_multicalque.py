#!/usr/bin/env python3
"""
Refonte Pixel-Art Pur Nintendo DS v5 — ZÉRO MIXEL INTEGRAL (Murs, Fenêtres, Escalier, Piliers, Racines, Plancher, Seuil Sud)
en Réseau Multicalque Paint.NET (.ora + 8 calques PNG + .tile + .rsground PMDO 0.8.12.0) :

1. Murs, Piliers, Œuf Ailé, Arche & Racines :
   - Squelettisation Zhang-Suen + élagage des coins en L (traits intérieurs strictement 1x1 px, 8-connexes, 0 pâté 2x2/3x3) ;
   - Suppression par EDT des halos d'anti-aliasing LANCZOS autour des traits avant quantification ;
   - Cel-shading Chunsoft franc à 5 tons de bois chauds (+ contour 1 px 8-connexe #2A170E sans coins en L).
2. Escalier Central Nord (Accueil & Grande Salle) :
   - Reconstruction pixel-art 1x1 pure des marches horizontales (nez 1 px net, giron plat, contremarche nette,
     trait d'assise 1 px #2A170E et fondu progressif dans la voûte sombre — 0 marche ondulée).
3. Fenêtres Cintrées Gauche & Droite (Accueil & Grande Salle) :
   - Ouverture cintrée lissée au pixel près avec sel-out 1 px 8-connexe (#603418) ;
   - Vitre cel-shadée nette à 2 tons (#FFFDF2 + liseré #FCE89C) ;
   - Croisillons bois pixel-art nets (cœur doré 2 px + sel-out 1 px #8E5022, pas 2:1 régulier sans flou).
4. Plancher 12 px synthétisé (0 pixel parasite, 0 ombre) & Seuil Sud Chunsoft (0 interstice).
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
# Palette Cel-Shading Nintendo DS Chunsoft Stricte (Zéro Mixel, Zéro Halo Flou)
# ==============================================================================
BG_LIGHT_BROWN = (198, 155, 110)   # #C69B6E marron clair extérieur

OUTLINE_DARK = (42, 23, 14)        # #2A170E trait de contour 1px
CAVITY_DARK = (68, 36, 18)         # #442412 cavité d'ombre profonde
SEL_OUT_WOOD = (96, 52, 24)        # #603418 trait fin intérieur bois / sel-out

# 5 tons francs de bois cel-shadé (0 bande d'anti-aliasing intermédiaire !)
WOOD_CEL_5 = np.array([
    [96, 52, 24],     # 0: ombre écorce franche #603418
    [142, 80, 34],    # 1: châtaignier ombre #8E5022
    [188, 114, 44],   # 2: chêne moyen #BC722C
    [224, 146, 54],   # 3: chêne miel clair #E09236
    [246, 182, 82],   # 4: rehaut solaire #F6B652
], dtype=np.uint8)

WIN_GLASS_CORE = (255, 253, 242)   # #FFFDF2 vitre blanc-ivoire pur
WIN_GLASS_RIM = (252, 232, 156)    # #FCE89C liseré solaire vitre 2px
WIN_BAR_HI = (248, 196, 100)       # #F8C464 rehaut croisillon
WIN_BAR_BODY = (224, 146, 54)      # #E09236 corps croisillon
WIN_BAR_SEL = (142, 80, 34)        # #8E5022 contour 1px croisillon

LEAF_RAMP = np.array([
    [26, 52, 22],     # 0: contour 1px feuillage #1A3416
    [44, 90, 34],     # 1: vert forêt ombre
    [72, 128, 44],    # 2: vert franc
    [114, 164, 50],   # 3: vert tendre
    [172, 194, 64],   # 4: pointe feuille dorée
], dtype=np.uint8)

# Plancher chêne miel pixel-art pur (planches 12 px)
PLANK_SEAM = (142, 74, 22)         # #8E4A16 joint 1px
PLANK_TOP_HI = (244, 174, 66)      # #F4AE42 biseau haut 1px
PLANK_BODY_A = (230, 148, 42)      # #E6942A corps planche A
PLANK_BODY_B = (224, 142, 38)      # #E08E26 corps planche B
PLANK_GRAIN = (208, 126, 32)       # #D07E20 veinage 1px
PLANK_BOT_SH = (196, 114, 28)      # #C4721C biseau bas 1px

# Halo d'entrée Sud Chunsoft (0 interstice)
HALO_LIP_WHITE = (255, 253, 242)
HALO_BAND_1 = (255, 249, 220)
HALO_BAND_2 = (253, 234, 174)
HALO_BAND_3 = (246, 208, 120)
HALO_BAND_4 = (238, 178, 76)


# ==============================================================================
# Squelettisation Zhang-Suen Vectorisée + Élagage des Coins en L (1x1 px Pur !)
# ==============================================================================

def zhang_suen_thin(binary: np.ndarray) -> np.ndarray:
    """Réduit tout trait épais (2-4 px) à un squelette médian exact de 1 px (vectorisé NumPy)."""
    img = binary.astype(np.uint8).copy()
    img[0, :] = 0
    img[-1, :] = 0
    img[:, 0] = 0
    img[:, -1] = 0

    while True:
        changed = False
        for step in (1, 2):
            p2 = img[:-2, 1:-1]
            p3 = img[:-2, 2:]
            p4 = img[1:-1, 2:]
            p5 = img[2:, 2:]
            p6 = img[2:, 1:-1]
            p7 = img[2:, :-2]
            p8 = img[1:-1, :-2]
            p9 = img[:-2, :-2]
            p1 = img[1:-1, 1:-1]

            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            A = (
                ((p2 == 0) & (p3 == 1)).astype(np.uint8)
                + ((p3 == 0) & (p4 == 1)).astype(np.uint8)
                + ((p4 == 0) & (p5 == 1)).astype(np.uint8)
                + ((p5 == 0) & (p6 == 1)).astype(np.uint8)
                + ((p6 == 0) & (p7 == 1)).astype(np.uint8)
                + ((p7 == 0) & (p8 == 1)).astype(np.uint8)
                + ((p8 == 0) & (p9 == 1)).astype(np.uint8)
                + ((p9 == 0) & (p2 == 1)).astype(np.uint8)
            )
            if step == 1:
                m1 = p2 * p4 * p6
                m2 = p4 * p6 * p8
            else:
                m1 = p2 * p4 * p8
                m2 = p2 * p6 * p8

            rem = (p1 == 1) & (B >= 2) & (B <= 6) & (A == 1) & (m1 == 0) & (m2 == 0)
            if np.any(rem):
                img[1:-1, 1:-1][rem] = 0
                changed = True
        if not changed:
            break
    return img.astype(bool)


def prune_l_corners_1px(line_mask: np.ndarray) -> np.ndarray:
    """
    Élimine les coins en L redondants sur les diagonales pour obtenir un vrai trait pixel-art
    8-connexe d'épaisseur 1 px stricte (sans escaliers épais de 2 px).
    """
    m = line_mask.copy()
    h, w = m.shape
    for orient in range(4):
        p2 = m[:-2, 1:-1]
        p3 = m[:-2, 2:]
        p4 = m[1:-1, 2:]
        p5 = m[2:, 2:]
        p6 = m[2:, 1:-1]
        p7 = m[2:, :-2]
        p8 = m[1:-1, :-2]
        p9 = m[:-2, :-2]
        c = m[1:-1, 1:-1]

        if orient == 0:
            # North + East L-corner without opposite diagonal dependency
            hit = c & p2 & p4 & (~p7) & (~p6) & (~p8)
        elif orient == 1:
            hit = c & p4 & p6 & (~p9) & (~p8) & (~p2)
        elif orient == 2:
            hit = c & p6 & p8 & (~p3) & (~p2) & (~p4)
        else:
            hit = c & p8 & p2 & (~p5) & (~p4) & (~p6)
        m[1:-1, 1:-1][hit] = False
    return m


# ==============================================================================
# Détourage Magenta + Purification Pixel-Art 1x1 Sans Mixel
# ==============================================================================

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


def remove_small_color_clusters(qarr: np.ndarray, region_mask: np.ndarray, protected_mask: np.ndarray, max_size: int = 3) -> np.ndarray:
    """Supprime tous les micro-amas isolés (<= max_size px) hors traits 1px protégés."""
    out = qarr.copy()
    h, w, _ = out.shape
    edit_zone = region_mask & (~protected_mask)
    struct8 = np.ones((3, 3), dtype=bool)

    for _ in range(2):
        codes = (
            (out[:, :, 0].astype(np.int32) << 16)
            | (out[:, :, 1].astype(np.int32) << 8)
            | out[:, :, 2].astype(np.int32)
        )
        uniq = np.unique(codes[edit_zone])
        rep = np.zeros((h, w), dtype=bool)
        for c in uniq:
            cm = edit_zone & (codes == c)
            lbl, n = ndimage.label(cm, structure=struct8)
            if n == 0:
                continue
            sz = ndimage.sum(cm, lbl, range(1, n + 1))
            small = np.where(sz <= max_size)[0] + 1
            if len(small):
                rep |= np.isin(lbl, small)
        if not np.any(rep):
            break
        ys, xs = np.where(rep)
        nxt = out.copy()
        for y, x in zip(ys, xs):
            y0, y1 = max(0, y - 1), min(h, y + 2)
            x0, x1 = max(0, x - 1), min(w, x + 2)
            valid = edit_zone[y0:y1, x0:x1] & (~rep[y0:y1, x0:x1])
            if not np.any(valid):
                valid = edit_zone[y0:y1, x0:x1]
            nb = codes[y0:y1, x0:x1][valid]
            if len(nb):
                vals, cnts = np.unique(nb, return_counts=True)
                bc = int(vals[int(np.argmax(cnts))])
                nxt[y, x] = [(bc >> 16) & 255, (bc >> 8) & 255, bc & 255]
        out = nxt
    return out


def pixelize_demixel_shell(im2x: Image.Image, w1x: int, h1x: int, is_foliage: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Convertit l'image 2x en VRAI pixel-art Nintendo DS 1x1 sans mixels :
      - Contours extérieurs 1 px 8-connexes (sans coins en L 2x2) ;
      - Traits sombres intérieurs squelettisés Zhang-Suen à 1 px strict + élagage des coins en L ;
      - Suppression par EDT des halos mous d'anti-aliasing autour des traits AVANT quantification ;
      - Quantification franche à 5 tons cel-shadés (bois) ou 5 tons (feuillage) + nettoyage des amas <= 3 px.
    Retourne (qarr, fg1x, lum1x_orig).
    """
    outline_rgb = tuple(int(v) for v in (LEAF_RAMP[0] if is_foliage else OUTLINE_DARK))
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

    lum1x = (
        0.299 * rgb1x[:, :, 0].astype(np.float32)
        + 0.587 * rgb1x[:, :, 1].astype(np.float32)
        + 0.114 * rgb1x[:, :, 2].astype(np.float32)
    )

    # 8-connected exterior 1px outline (erode with 3x3 square -> ZERO L-corners on diagonal edges!)
    eroded8 = ndimage.binary_erosion(fg1x, structure=np.ones((3, 3), dtype=bool))
    ext_outline = fg1x & (~eroded8)

    if is_foliage:
        out = np.zeros_like(rgb1x)
        out[~fg1x] = BG_LIGHT_BROWN
        inner = fg1x & (~ext_outline)
        # Strip dark outline bleed inside leaves before cel-shading onto LEAF_RAMP[1:]
        clean_leaf = inner & (lum1x >= 46.0)
        if np.any(clean_leaf) and np.any(inner & (~clean_leaf)):
            _, idx_l = ndimage.distance_transform_edt(~clean_leaf, return_indices=True)
            rgb_leaf = rgb1x[idx_l[0], idx_l[1]]
        else:
            rgb_leaf = rgb1x
        px = rgb_leaf[inner].astype(np.int32)
        d2 = ((px[:, None, :] - LEAF_RAMP[1:, :][None, :, :].astype(np.int32)) ** 2).sum(axis=-1)
        out[inner] = LEAF_RAMP[1 + np.argmin(d2, axis=1)]
        # Skeletonize interior dark leaf vein lines cleanly to 1px
        leaf_veins = prune_l_corners_1px(zhang_suen_thin(inner & (lum1x < 46.0)))
        out[leaf_veins] = LEAF_RAMP[0]
        out[ext_outline] = LEAF_RAMP[0]
        out = remove_small_color_clusters(out, inner, leaf_veins, max_size=2)
        return out, fg1x, lum1x

    # ==========================================================================
    # BOIS / MURS / PILIERS / OEUF AILÉ / RACINES : DÉ-MIXELISATION 1x1 STRICTE
    # ==========================================================================
    inner_fg = fg1x & (~ext_outline)

    # 1. Separate true broad dark cavities strictly inside the central stair arch vault from fat 2-4px dark lines!
    cx_room = 0.5 * w1x
    in_central_vault = (np.abs(xx - cx_room) <= int(w1x * 0.09)) & (yy <= int(h1x * 0.36))
    deep_cavity = ndimage.binary_opening(inner_fg & in_central_vault & (lum1x < 54.0), structure=np.ones((5, 5), dtype=bool))
    deep_cavity = ndimage.binary_dilation(deep_cavity, iterations=1) & inner_fg & in_central_vault & (lum1x < 68.0)

    # 2. Detect fat dark lines & creases (restrict win_approx strictly to left/right window X-columns so winged egg stays 100% wood!)
    in_win_cols = (xx < int(w1x * 0.34)) | (xx > int(w1x * 0.66))
    win_approx = inner_fg & in_win_cols & (yy < int(h1x * 0.42)) & (rgb1x[:, :, 0] >= 216) & (rgb1x[:, :, 1] >= 180)
    fat_dark = inner_fg & (~deep_cavity) & (~win_approx) & (lum1x < 80.0)

    # 3. Zhang-Suen skeletonize fat_dark -> exact 1x1 pixel lineart + prune L-corners!
    thin_dark = prune_l_corners_1px(zhang_suen_thin(fat_dark))
    # Drop tiny 1-2px isolated dust dots in thin_dark
    lbl_td, n_td = ndimage.label(thin_dark, structure=np.ones((3, 3), dtype=bool))
    if n_td > 0:
        sz_td = ndimage.sum(thin_dark, lbl_td, range(1, n_td + 1))
        keep_td = np.where(sz_td >= 3)[0] + 1
        thin_dark = np.isin(lbl_td, keep_td)

    # 4. Strip LANCZOS anti-aliasing collar around fat_dark & ext_outline via EDT BEFORE cel-shading!
    aa_collar = (ndimage.binary_dilation(fat_dark | ext_outline, iterations=1) & inner_fg & (~deep_cavity) & (~win_approx))
    clean_wood_src = inner_fg & (~aa_collar) & (~fat_dark) & (~deep_cavity) & (~win_approx)
    lum_dehalo = lum1x.copy()
    if np.any(clean_wood_src) and np.any(aa_collar | fat_dark):
        _, idx_w = ndimage.distance_transform_edt(~clean_wood_src, return_indices=True)
        replace_z = (aa_collar | fat_dark) & (~deep_cavity)
        lum_dehalo[replace_z] = lum1x[idx_w[0][replace_z], idx_w[1][replace_z]]

    # 5. Smooth wood regions slightly (median 3x3) so flat cel-shaded clusters form crisp bands without noise!
    lum_smooth = ndimage.median_filter(lum_dehalo, size=3)

    # 6. Quantize wood strictly onto 5 crisp Chunsoft cel-shaded wood tones!
    wood_ramp_lum = (
        0.299 * WOOD_CEL_5[:, 0].astype(np.float32)
        + 0.587 * WOOD_CEL_5[:, 1].astype(np.float32)
        + 0.114 * WOOD_CEL_5[:, 2].astype(np.float32)
    )
    out = np.zeros_like(rgb1x)
    out[~fg1x] = BG_LIGHT_BROWN

    wood_fill_mask = inner_fg & (~deep_cavity)
    if np.any(wood_fill_mask):
        d_l = np.abs(lum_smooth[wood_fill_mask][:, None] - wood_ramp_lum[None, :])
        out[wood_fill_mask] = WOOD_CEL_5[np.argmin(d_l, axis=1)]

    # Clean small 1-3px speckles in the flat cel-shaded wood BEFORE stamping crisp 1px lines!
    out = remove_small_color_clusters(out, wood_fill_mask, np.zeros_like(fg1x), max_size=3)

    # Deep cavities (two-step crisp arch vault shadow)
    out[deep_cavity & (lum1x >= 42.0)] = CAVITY_DARK
    out[deep_cavity & (lum1x < 42.0)] = OUTLINE_DARK

    # 7. Stamp razor-sharp 1x1 pixel interior lineart (dark outline #2A170E where strong, warm #603418 sel-out where subtle)
    strong_line = thin_dark & (lum1x < 58.0)
    soft_line = thin_dark & (~strong_line)
    out[soft_line] = SEL_OUT_WOOD
    out[strong_line] = OUTLINE_DARK

    # 8. Stamp 8-connected 1x1 pixel exterior silhouette outline (#2A170E, 0 L-corners!)
    out[ext_outline] = OUTLINE_DARK

    return out, fg1x, lum1x


# ==============================================================================
# Reconstruction Pixel-Art 1x1 Pure de l'Escalier Central Nord (0 marche tordue !)
# ==============================================================================

def reconstruct_crisp_stairs_1px(
    shell_q: np.ndarray,
    lum_orig: np.ndarray,
    cx: float,
    y_top: int,
    y_bot: int,
    half_w_top: int,
    half_w_bot: int,
    arch_cy: int,
    arch_ry: int,
    step_ys: List[int],
) -> np.ndarray:
    """
    Reconstruit l'ouverture intérieure de l'escalier central en VRAI pixel-art DS 1x1 :
      - Marche par marche parfaitement horizontale (trait 1 px #2A170E en bas de contremarche,
        contremarche plane, nez de marche lumineux 1 px droit, giron plat + léger veinage 1 px) ;
      - Fondu progressif Chunsoft vers l'ombre chaude de la voûte Nord ;
      - Contours intérieurs 1 px 8-connexes le long des deux piliers de l'arche !
    """
    out = shell_q.copy()
    h, w, _ = out.shape

    # Palette progressive des marches du bas (ensoleillé) vers le haut (ombre sous l'arche)
    # Chaque entrée : (nose_hi_rgb, tread_rgb, grain_rgb, riser_rgb, riser_top_sh_rgb)
    step_palettes = [
        ((246, 182, 82), (224, 146, 54), (188, 114, 44), (142, 80, 34), (96, 52, 24)),   # Marche 0 (bas, pleine lumière)
        ((236, 164, 66), (206, 130, 48), (168, 98, 38),  (120, 66, 28), (82, 44, 20)),   # Marche 1
        ((214, 138, 52), (182, 108, 42), (142, 80, 34),  (96, 52, 24),  (68, 36, 18)),   # Marche 2
        ((182, 108, 42), (142, 80, 34),  (112, 62, 28),  (78, 42, 20),  (54, 29, 15)),   # Marche 3
        ((134, 74, 32),  (104, 56, 26),  (82, 44, 20),   (62, 33, 16),  (42, 23, 14)),   # Marche 4
        ((96, 52, 24),   (72, 39, 19),   (58, 31, 16),   (48, 26, 14),  (42, 23, 14)),   # Marche 5 (fond sous voûte)
    ]

    # Build exact smooth symmetrical archway mask for the stairs
    arch_mask = np.zeros((h, w), dtype=bool)
    for y in range(y_top, y_bot + 1):
        if y < arch_cy:
            dy = (arch_cy - y) / max(float(arch_ry), 1.0)
            if dy >= 1.0:
                continue
            hw = int(round(half_w_top * math.sqrt(max(0.0, 1.0 - dy * dy))))
        else:
            t = (y - arch_cy) / max(float(y_bot - arch_cy), 1.0)
            hw = int(round(half_w_top + t * (half_w_bot - half_w_top)))
        xl = int(round(cx - hw))
        xr = int(round(cx + hw))
        arch_mask[y, xl : xr + 1] = True

    # Draw 1px #2A170E outline on the wood jambs immediately bordering arch_mask
    jamb_border = (~arch_mask) & ndimage.binary_dilation(arch_mask, structure=np.ones((3, 3), dtype=bool))
    jamb_border[y_bot + 1 :, :] = False
    out[jamb_border] = OUTLINE_DARK

    # Fill upper arch vault above highest step with crisp 2-tone deep shadow
    top_step_y = step_ys[-1]
    for y in range(y_top, y_bot + 1):
        xs = np.where(arch_mask[y])[0]
        if len(xs) == 0:
            continue
        x0, x1 = int(xs.min()), int(xs.max())
        if y < top_step_y:
            # Smooth elliptical shadow cap at the very top of the vault
            out[y, x0 : x1 + 1] = OUTLINE_DARK if (y < top_step_y - 8) else CAVITY_DARK
            continue

        # Find which step `k` owns row `y` (step_ys = [y_bot, y_s1, y_s2, ..., y_top_step] descending!)
        k = 0
        for idx_s in range(len(step_ys) - 1):
            if step_ys[idx_s + 1] <= y <= step_ys[idx_s]:
                k = idx_s
                break
        yb = step_ys[k]
        yt = step_ys[k + 1]
        pal = step_palettes[min(k, len(step_palettes) - 1)]
        nose_col, tread_col, grain_col, riser_col, riser_sh_col = pal

        span_h = yb - yt
        riser_h = max(3, min(5, span_h // 3 + 1))
        nose_y = yb - riser_h

        if y == yb:
            row_col = OUTLINE_DARK
        elif y > nose_y:
            row_col = riser_sh_col if (y == nose_y + 1) else riser_col
        elif y == nose_y:
            row_col = nose_col
        else:
            row_col = tread_col

        out[y, x0 : x1 + 1] = row_col

        # Subtle clean 1px horizontal woodgrain line in middle of lower treads + 2px side shadow near jambs
        if yt < y < nose_y and k <= 3:
            if y == (yt + nose_y) // 2:
                gx0 = x0 + 8 + (k * 11) % 14
                gx1 = min(x1 - 8, gx0 + 18)
                if gx1 > gx0:
                    out[y, gx0:gx1] = grain_col
        if y != yb and (x1 - x0) >= 10:
            # Crisp 2px warm ambient occlusion right next to left & right arch pillars
            out[y, x0 : x0 + 2] = riser_sh_col
            out[y, x1 - 1 : x1 + 1] = riser_sh_col

    return out


# ==============================================================================
# Reconstruction Pixel-Art 1x1 Pure des Fenêtres Cintrées & Croisillons (0 flou !)
# ==============================================================================

def reconstruct_crisp_arched_windows_1px(
    shell_q: np.ndarray,
    x_left: int,
    x_right: int,
    v_spring: float,
    ry_arch: float,
    v_bot: float,
    transom_vs: List[float],
    sill_top_h: int = 8,
    sill_lip_h: int = 4,
    sill_protrude_r: int = 6,
) -> np.ndarray:
    """
    Reconstruit intégralement les 2 fenêtres cintrées en perspective 2:1 pixel-art pure (1x1 px, 0 mixel) :
      - Coordonnée cisaillée 2:1 `v(x, y) = y + 0.5 * (x - x_mid)` alignée au pixel près sur la perspective de la pièce ;
      - Toute l'ancienne zone vitre/croisillons/rebord floue est remplacée à 100 % par :
          * Vitre cel-shadée nette à 2 tons (#FFFDF2 + liseré #FCE89C de 2 px) entourée d'un sel-out 1 px 8-connexe (#603418) ;
          * 1 meneau vertical droit + 2 traverses en diagonale 2:1 exacte (cœur doré 2 px + sel-out 1 px #8E5022, 0 flou) ;
          * Rebord de fenêtre en bois ensoleillé 2:1 net (plateau clair #F6B652 + nez #E09236/#BC722C + contour 1 px #2A170E).
      - Symétrie miroir exacte gauche <-> droite autour de `w - 1 - x`.
    """
    out = shell_q.copy()
    h, w, _ = out.shape
    x_mid = 0.5 * (x_left + x_right)
    rx = 0.5 * (x_right - x_left)

    pad_x0 = max(0, x_left - 4)
    pad_x1 = min(w // 2, x_right + sill_protrude_r + 4)
    pad_y0 = max(0, int(v_spring - ry_arch - 0.5 * rx) - 6)
    pad_y1 = min(h, int(v_bot + 0.5 * rx + sill_top_h + sill_lip_h) + 8)

    pw = pad_x1 - pad_x0
    ph = pad_y1 - pad_y0
    yy_l, xx_l = np.mgrid[0:ph, 0:pw]
    gx = xx_l + pad_x0
    gy = yy_l + pad_y0

    # 2:1 sheared vertical coordinate (integer half-steps -> exact 2px horizontal per 1px vertical!)
    v_grid = gy.astype(np.float32) + 0.5 * (gx.astype(np.float32) - x_mid)
    u_grid = (gx.astype(np.float32) - x_mid) / max(rx, 1.0)

    in_x_pane = (gx >= x_left) & (gx <= x_right)
    arch_top_v = v_spring - ry_arch * np.sqrt(np.maximum(0.0, 1.0 - np.minimum(1.0, u_grid * u_grid)))
    pane = in_x_pane & (v_grid >= np.ceil(arch_top_v)) & (v_grid <= v_bot)

    # 8-connected 1px inner wooden frame outline around the glass pane
    frame_sel1 = (~pane) & ndimage.binary_dilation(pane, structure=np.ones((3, 3), dtype=bool))
    glass_core = ndimage.binary_erosion(pane, structure=np.ones((5, 5), dtype=bool))

    # Crisp 1x1 vertical mullion at x = round(x_mid)-1 .. round(x_mid)
    vx = int(round(x_mid)) - 1
    v_core = pane & ((gx == vx) | (gx == vx + 1))
    v_hi = pane & (gx == vx + 1)
    v_sel = pane & ((gx == vx - 1) | (gx == vx + 2))

    # Crisp 2:1 diagonal perspective transoms (exact 2px steps!)
    t_core = np.zeros((ph, pw), dtype=bool)
    t_hi = np.zeros((ph, pw), dtype=bool)
    t_sel = np.zeros((ph, pw), dtype=bool)
    for tv in transom_vs:
        # Integerized 2:1 line: yc(x) = int(floor(tv - 0.5 * (gx - x_mid)))
        yc = np.floor(tv - 0.5 * (gx.astype(np.float32) - x_mid)).astype(int)
        t_hi |= pane & (gy == yc)
        t_core |= pane & ((gy == yc) | (gy == yc + 1))
        t_sel |= pane & ((gy == yc - 1) | (gy == yc + 2))

    all_core = v_core | t_core
    all_hi = (v_hi | t_hi) & all_core
    all_sel = (v_sel | t_sel) & (~all_core) & pane

    # Crisp 2:1 3D isometric wooden window sill right below the glass pane!
    y_sill_top = np.floor(v_bot + 1.0 - 0.5 * (gx.astype(np.float32) - x_mid)).astype(int)
    dy_sill = gy - y_sill_top
    # True 3D perspective sill: projects inward into the room (+dy_sill//2 on left, up to x_right + sill_protrude_r on right)
    x_sill_l = x_left + np.clip(dy_sill // 2, 0, 5)
    x_sill_r = x_right + np.minimum(sill_protrude_r, np.maximum(2, dy_sill // 2 + 4))
    in_x_sill = (gx >= x_sill_l) & (gx <= x_sill_r)
    sill_top_plane = in_x_sill & (dy_sill >= 0) & (dy_sill < sill_top_h) & (~pane)
    sill_front_lip = in_x_sill & (dy_sill >= sill_top_h) & (dy_sill < sill_top_h + sill_lip_h) & (~pane)
    sill_total = sill_top_plane | sill_front_lip
    sill_hi_line = in_x_sill & (dy_sill == sill_top_h - 1) & (~pane)
    sill_crease = in_x_sill & (dy_sill == sill_top_h) & (~pane)
    sill_outline = (~sill_total) & (~pane) & ndimage.binary_dilation(sill_total, structure=np.ones((3, 3), dtype=bool))

    sub_out = out[pad_y0:pad_y1, pad_x0:pad_x1].copy()

    # 1. Paint crisp wooden sill first
    sub_out[sill_top_plane] = WOOD_CEL_5[4]     # #F6B652 sunlit sill top
    sub_out[sill_hi_line] = WIN_GLASS_RIM       # #FCE89C crisp nose catchlight
    sub_out[sill_front_lip] = WOOD_CEL_5[2]     # #BC722C front vertical lip
    sub_out[sill_crease] = SEL_OUT_WOOD         # #603418 1px step crease
    sub_out[sill_outline] = OUTLINE_DARK        # #2A170E 1px 8-connexe sill border

    # 2. Paint crisp arched glass + 1px sel-out + 2:1 muntin bars
    sub_out[frame_sel1 & (~sill_top_plane)] = SEL_OUT_WOOD
    sub_out[pane] = WIN_GLASS_RIM
    sub_out[glass_core] = WIN_GLASS_CORE
    sub_out[all_sel] = WIN_BAR_SEL
    sub_out[all_core] = WIN_BAR_BODY
    sub_out[all_hi] = WIN_BAR_HI
    # Clean 1px line right where glass meets sunlit sill
    glass_sill_joint = in_x_pane & (gy == y_sill_top)
    sub_out[glass_sill_joint] = WIN_BAR_SEL

    out[pad_y0:pad_y1, pad_x0:pad_x1] = sub_out

    # Mirror exact crisp window + sill onto right wall!
    edit_mask = pane | frame_sel1 | sill_total | sill_outline
    rx0, rx1 = w - pad_x1, w - pad_x0
    sub_right = out[pad_y0:pad_y1, rx0:rx1].copy()
    sub_mir = sub_out[:, ::-1]
    mir_m = edit_mask[:, ::-1]
    sub_right[mir_m] = sub_mir[mir_m]
    out[pad_y0:pad_y1, rx0:rx1] = sub_right

    return out


# ==============================================================================
# Plancher 12 px Synthétisé & Sprites de Lianes
# ==============================================================================

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
    qarr, fg1x, _ = pixelize_demixel_shell(sub, tw, th, is_foliage=True)
    rgba = np.zeros((th, tw, 4), dtype=np.uint8)
    rgba[:, :, :3] = qarr
    rgba[:, :, 3] = np.where(fg1x, 255, 0)
    return Image.fromarray(rgba, mode="RGBA")


# ==============================================================================
# Construction `guilde_destiny_accueil` (640 x 480) — Zéro Mixel, Zéro Interstice
# ==============================================================================

def build_accueil_clean() -> Tuple[Dict[str, List[np.ndarray]], List[Tuple[str, np.ndarray]], Image.Image, np.ndarray]:
    W, H = 640, 480
    GW, GH = W // 8, H // 8
    LAYERS_OUT.mkdir(parents=True, exist_ok=True)

    im_orig = Image.open("/home/user/uploads/image-3.png").convert("RGB").resize((1280, 960), Image.Resampling.LANCZOS)
    a_orig = np.array(im_orig)
    # Symmetrize architectural room left -> right so both windows, pillars, winged egg & root jambs have 100% clean symmetry
    a_orig[:, 640:] = a_orig[:, :640][:, ::-1]

    shell_q, shell_mask, lum_orig = pixelize_demixel_shell(Image.fromarray(a_orig), W, H, is_foliage=False)

    # Reconstruct 100% crisp 1x1 pixel-art arched windows & muntin bars + sunlit 2:1 sill!
    shell_q = reconstruct_crisp_arched_windows_1px(
        shell_q,
        x_left=140,
        x_right=190,
        v_spring=116.0,
        ry_arch=25.0,
        v_bot=164.0,
        transom_vs=[122.0, 143.0],
        sill_top_h=10,
        sill_lip_h=5,
        sill_protrude_r=7,
    )

    # Reconstruct 100% crisp 1x1 pixel-art central staircase inside the winged-egg arch!
    shell_q = reconstruct_crisp_stairs_1px(
        shell_q, lum_orig,
        cx=319.5,
        y_top=93,
        y_bot=179,
        half_w_top=28,
        half_w_bot=33,
        arch_cy=125,
        arch_ry=32,
        step_ys=[179, 166, 153, 140, 128, 116, 105],
    )

    yy, xx = np.mgrid[0:H, 0:W]
    in_candidate_oval = (((xx - 320.0) / 214.0) ** 2 + ((yy - 262.0) / 96.0) ** 2 <= 1.02) & (yy >= 174)
    in_candidate_south = (yy >= 344) & (yy <= 454) & (xx >= 266) & (xx <= 373)
    in_compass_1x = ((xx - 320.0) ** 2 + (yy - 265.0) ** 2) <= 52 ** 2

    is_dark_wall_line = ((lum_orig <= 92.0) & (~in_compass_1x)) | (~shell_mask)
    walk_seed_region = (in_candidate_oval | in_candidate_south) & (~is_dark_wall_line)
    lbl_fl, _ = ndimage.label(walk_seed_region)
    floor_interior = lbl_fl == lbl_fl[220, 320]

    floor_sym = floor_interior & floor_interior[:, ::-1]
    floor_sym[180:187, 252:388] |= (floor_interior[180:187, 252:388] | floor_interior[180:187, 252:388][:, ::-1])
    dy_d, dx_d = np.mgrid[-4:5, -4:5]
    disk9 = (dx_d * dx_d + dy_d * dy_d) <= 16
    floor_sym = ndimage.binary_closing(floor_sym, structure=disk9)
    floor_sym = ndimage.binary_opening(floor_sym, structure=disk9)
    floor_sym = ndimage.binary_fill_holes(floor_sym)

    raw_hw = np.zeros(453 - 344, dtype=np.float32)
    for idx_y, y in enumerate(range(344, 453)):
        xs_f = np.where(floor_sym[y] & (xx[y] >= 266) & (xx[y] <= 373))[0]
        hw_v = 0.5 * (xs_f.max() - xs_f.min()) if len(xs_f) >= 20 else 45.0
        raw_hw[idx_y] = np.clip(hw_v, 41.0, 46.5)
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
    floor_core[yy < 180] = False

    door_below_451 = (yy >= 451) & (xx >= 274) & (xx <= 365)
    wall_shell_mask = shell_mask & (~floor_core) & (~door_below_451)
    lbl_ws, n_ws = ndimage.label(wall_shell_mask)
    if n_ws > 1:
        sz_ws = ndimage.sum(wall_shell_mask, lbl_ws, range(1, n_ws + 1))
        wall_shell_mask = lbl_ws == (int(np.argmax(sz_ws)) + 1)

    # 8-connected 1px inner baseboard outline (erode wall_shell_mask or dilate floor_core with 3x3 + prune L-corners!)
    wall_inner_raw = wall_shell_mask & ndimage.binary_dilation(floor_core | door_below_451, structure=np.ones((3, 3), dtype=bool))
    wall_inner_1px = prune_l_corners_1px(zhang_suen_thin(wall_inner_raw)) | (
        wall_shell_mask & (~ndimage.binary_erosion(wall_shell_mask | (~(floor_core | door_below_451)), structure=np.ones((3, 3), dtype=bool)))
    )
    shell_q[wall_inner_1px] = OUTLINE_DARK

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

    xs_open = np.where(~wall_shell_mask[450] & (xx[450] >= 266) & (xx[450] <= 373))[0]
    x_left_open, x_right_open = int(xs_open.min()), int(xs_open.max())
    cx_h = 319.5
    half_w_vis = 0.5 * (x_right_open - x_left_open)
    half_w_under = half_w_vis + 4.0

    nx_vis = (xx - cx_h) / max(half_w_vis, 1.0)
    nx_under = (xx - cx_h) / half_w_under
    in_door_under = np.abs(nx_under) <= 1.0

    lip_bot_y = 451.0 + 4.0 * np.maximum(0.0, 1.0 - nx_vis * nx_vis)
    lip_top_y = lip_bot_y - 3.0

    door_plank_zone = in_door_under & (yy >= 348) & (yy <= np.floor(lip_bot_y))
    outer_hull = wall_shell_mask | floor_core | door_plank_zone
    floor_underlap = ((ndimage.binary_dilation(floor_core, iterations=3) & (wall_shell_mask | floor_core)) | door_plank_zone) & outer_hull
    floor_underlap[yy < 178] = False

    pure_planks = synthesize_crisp_pixel_art_plank_floor(W, H, plank_h=12, y_offset=2)
    bevel_ring = floor_core & ndimage.binary_dilation(wall_shell_mask, iterations=1) & (yy < 448)
    pure_planks[bevel_ring] = PLANK_SEAM

    l0_bg = np.zeros((H, W, 4), dtype=np.uint8)
    l0_bg[:, :] = [BG_LIGHT_BROWN[0], BG_LIGHT_BROWN[1], BG_LIGHT_BROWN[2], 255]
    l0_bg[(wall_shell_mask | floor_core) & (~(in_door_under & (yy >= 444)))] = [52, 30, 16, 255]

    l1_floor = np.zeros((H, W, 4), dtype=np.uint8)
    l1_floor[floor_underlap, :3] = pure_planks[floor_underlap]
    l1_floor[floor_underlap, 3] = 255

    m_top = wall_shell_mask & (~walk_tiles_px) & (
        (yy >= 352) | ((yy >= 312) & ((xx <= 148) | (xx >= 492)))
    )
    m_wall_bot = wall_shell_mask & (~m_top)

    in_arch_top = (yy >= 92) & (yy <= 122) & (xx >= 290) & (xx <= 349) & (shell_q[:, :, 0] <= 72)
    m_stair_depth = m_wall_bot & in_arch_top
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
    win_glass = (shell_q[:, :, 0] >= 248) & (shell_q[:, :, 1] >= 230) & (yy < 190)
    outside_room = ~ndimage.binary_dilation(wall_shell_mask | floor_core, iterations=5)
    l4_vines[win_glass | outside_room, 3] = 0

    sun_frames: List[np.ndarray] = []
    # Restrict window shimmer strictly to the glass panes + 1x1 pollen motes so flat cel-shaded wood has 0 alpha circle!
    aura_core = wall_shell_mask & win_glass
    motes = [
        (174, 152, 0), (186, 166, 4), (162, 168, 8),
        (466, 152, 2), (454, 166, 6), (478, 168, 10),
    ]
    for ph in range(12):
        fr = np.zeros((H, W, 4), dtype=np.uint8)
        breath = 0.5 + 0.5 * math.sin(2.0 * math.pi * ph / 12.0)
        fr[aura_core] = [255, 250, 208, int(round((20 + 12 * breath) / 4.0) * 4)]
        for mx0, my0, off in motes:
            t = (ph + off) % 12
            dx = int(round(2.0 * math.cos(2.0 * math.pi * t / 12.0)))
            dy = int(round(2.0 * math.sin(2.0 * math.pi * t / 12.0)))
            ma = 112 + int(64 * (0.5 + 0.5 * math.sin(2.0 * math.pi * t / 12.0)))
            px_x, px_y = mx0 + dx, my0 + dy
            if 0 <= px_x < W - 1 and 0 <= px_y < H - 1 and wall_shell_mask[px_y, px_x]:
                fr[px_y, px_x] = [255, 253, 224, ma]  # 1x1 pixel mote (never 2x2 mixel mote!)
        sun_frames.append(fr)

    open_south_canvas = (~wall_shell_mask) & in_door_under & (yy >= 390) & (yy <= np.floor(lip_bot_y))
    lip_mask = open_south_canvas & (yy >= np.floor(lip_top_y))
    lip_warm_rim = (~wall_shell_mask) & in_door_under & (yy == np.floor(lip_bot_y) + 1) & (np.abs(nx_vis) <= 0.96)

    rx_arc = half_w_vis * 0.98
    ry_arc = half_w_vis * 0.90
    rad_arc = np.sqrt(((xx - cx_h) / rx_arc) ** 2 + np.maximum(0.0, (453.0 - yy) / ry_arc) ** 2)

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
# Purification Identique de `guilde_destiny_missions` (1112 x 760) — Zéro Mixel
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
    merged[:, 556:] = merged[:, :556][:, ::-1]

    shell_q, shell_mask, lum_orig = pixelize_demixel_shell(Image.fromarray(merged), W, H, is_foliage=False)

    # Crisp 1x1 pixel-art arched windows + 2:1 sunlit sill on Grande Salle
    shell_q = reconstruct_crisp_arched_windows_1px(
        shell_q,
        x_left=142,
        x_right=206,
        v_spring=158.0,
        ry_arch=34.0,
        v_bot=238.0,
        transom_vs=[170.0, 204.0],
        sill_top_h=12,
        sill_lip_h=6,
        sill_protrude_r=9,
    )

    # Crisp 1x1 pixel-art central staircase on Grande Salle (0 motif on arch preserved!)
    shell_q = reconstruct_crisp_stairs_1px(
        shell_q, lum_orig,
        cx=555.5,
        y_top=128,
        y_bot=247,
        half_w_top=48,
        half_w_bot=57,
        arch_cy=168,
        arch_ry=40,
        step_ys=[247, 231, 215, 199, 183, 167, 152],
    )

    in_cand = (((xx - 556.0) / 456.0) ** 2 + ((yy - 446.0) / 232.0) ** 2 <= 1.02) & (yy >= 232)
    is_dark_line = (lum_orig <= 92.0) | (~shell_mask)
    lbl_m, _ = ndimage.label(in_cand & (~is_dark_line))
    fl_core = lbl_m == lbl_m[430, 556]
    fl_core = fl_core & fl_core[:, ::-1]
    dy_m, dx_m = np.mgrid[-4:5, -4:5]
    disk9_m = (dx_m * dx_m + dy_m * dy_m) <= 16
    fl_core = ndimage.binary_closing(fl_core, structure=disk9_m)
    fl_core = ndimage.binary_opening(fl_core, structure=disk9_m)
    fl_core = ndimage.binary_fill_holes(fl_core)
    fl_core[yy < 248] = False

    wall_shell = shell_mask & (~fl_core)
    wall_inner_1px = wall_shell & (~ndimage.binary_erosion(wall_shell | (~fl_core), structure=np.ones((3, 3), dtype=bool)))
    shell_q[wall_inner_1px] = OUTLINE_DARK

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
    in_arch = (yy >= 126) & (yy <= 155) & (xx >= 505) & (xx <= 606) & (shell_q[:, :, 0] <= 72)
    m_stair = m_wall_bot & in_arch
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
    win_glass = (shell_q[:, :, 0] >= 248) & (shell_q[:, :, 1] >= 230) & (yy < 260)
    outside_room = ~ndimage.binary_dilation(shell_mask, iterations=5)
    l4_vines[win_glass | outside_room, 3] = 0

    sun_frames: List[np.ndarray] = []
    aura_core = wall_shell & win_glass
    for ph in range(12):
        fr = np.zeros((H, W, 4), dtype=np.uint8)
        breath = 0.5 + 0.5 * math.sin(2.0 * math.pi * ph / 12.0)
        fr[aura_core] = [255, 250, 208, int(round((20 + 12 * breath) / 4.0) * 4)]
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
# Compilation PMDO 0.8.12.0 (.tile + .rsground) + Planche de Présentation
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
    if not rs_ref_path.exists():
        rs_ref_path = Path("/home/user/guilde_destiny_src/guilde_destiny_accueil.rsground")
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

    if (GAME / "Content/Tile").exists():
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
    if (GAME / "Data/Ground").exists():
        (GAME / f"Data/Ground/{asset_name}.rsground").write_text(rs_txt, encoding="utf-8")
    (PDN_DIR / f"{asset_name}.rsground").write_text(rs_txt, encoding="utf-8")
    print(f"[OK] {asset_name} ({w}x{h}): {sheet_name}.tile ({n_tiles} tuiles 8x8 pures 1x1).")


def build_showcase_board(pdn_layers: List[Tuple[str, np.ndarray]], acc_rgb: Image.Image) -> None:
    W_B, H_B = 1520, 1090
    board = Image.new("RGB", (W_B, H_B), (36, 26, 20))
    dr = ImageDraw.Draw(board)

    dr.text((28, 16), "Rendu 1:1 Pur Pixel-Art DS (1x1 px) - Accueil Guilde Destiny (0 mixel murs/fenetres/escalier/sol, 0 interstice)", fill=(252, 236, 196))
    board.paste(acc_rgb, (28, 42))

    # Zoom 3x Fenêtre + Pilier + Mur + Escalier + Oeuf ailé (preuve directe 1x1 px sans mixels !)
    dr.text((692, 16), "Zoom 3x Murs + Fenetre + Croisillons 1px + Oeuf aile + Escalier horizontal net", fill=(204, 244, 196))
    z_top3 = acc_rgb.crop((130, 42, 396, 190)).resize((266 * 3, 148 * 2), Image.Resampling.NEAREST)
    # Use exact uniform integer 3x zoom on (132..396 = 264px -> 792px, y=48..190 = 142px -> 426? Let's fit 264*3 x 96*3 = 792x288!)
    z_win_st3 = acc_rgb.crop((132, 88, 396, 186)).resize((264 * 3, 98 * 3), Image.Resampling.NEAREST)
    board.paste(z_win_st3, (692, 42))

    # Zoom 3x Oeuf ailé + Seuil Sud côte à côte
    dr.text((692, 348), "Zoom 3x Oeuf aile (traits 1px) + Zoom 3x Seuil Sud (0 interstice)", fill=(255, 228, 168))
    z_egg3 = acc_rgb.crop((258, 40, 382, 102)).resize((124 * 3, 62 * 3), Image.Resampling.NEAREST)
    board.paste(z_egg3, (692, 372))
    z_sill3 = acc_rgb.crop((258, 402, 382, 464)).resize((124 * 3, 62 * 3), Image.Resampling.NEAREST)
    board.paste(z_sill3, (1084, 372))

    dr.text((28, 566), "Reseau Multicalque Paint.NET (.ora OpenRaster + 8 calques RGBA 1x1 px sans mixel ni pixel parasite) :", fill=(252, 236, 196))
    yy, xx = np.mgrid[0:216, 0:320]
    chk = np.where(((xx // 8) + (yy // 8)) % 2 == 0, 224, 192).astype(np.uint8)
    chk_rgba = np.stack([chk, chk, chk, np.full_like(chk, 255)], axis=-1)

    labels_fr = [
        "00. Fond marron clair uni (#C69B6E)",
        "01. Plancher pixel-art pur 12px (0 bruit)",
        "02. Profondeur arche escalier Nord",
        "03. Murs, escalier & fenetres 1x1 px (0 mixel)",
        "04. Verdure & lianes 1x1 px (5 tons)",
        "05. Lumiere fenetres & pollen 1px (12 ph.)",
        "06. Halo Sud Chunsoft (0 interstice)",
        "07. Couronne racines avant-plan 1x1 px (Top)",
    ]
    for i, ((_, larr), lbl) in enumerate(zip(pdn_layers, labels_fr)):
        col = i % 4
        row = i // 4
        bx = 28 + col * 366
        by = 592 + row * 244
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
        comment_fr="Salle d'accueil pixel-art pur DS 1x1 px (640x480, 0 mixel murs/fenetres/escalier/plancher, 0 interstice Sud, fond marron clair #C69B6E).",
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
        comment_fr="Grande Salle aux deux murs pixel-art pur DS 1x1 px (1112x760, 0 mixel murs/fenetres/escalier/plancher, fond marron clair #C69B6E).",
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
    print("[OK] Dé-mixelisation intégrale v5 (murs, fenêtres, escalier, piliers, racines) terminée.")


if __name__ == "__main__":
    main()
