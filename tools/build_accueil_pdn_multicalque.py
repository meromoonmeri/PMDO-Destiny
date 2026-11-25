#!/usr/bin/env python3
"""
Compilation Pixel-Art Fidèle & Propre en Réseau Multicalque Paint.NET (.ora + 8 PNG + PMDO .tile/.rsground)
à partir de la régénération validée par l'utilisateur (`accueil_regenere_au_propre.png`) :

- Préservation 100 % fidèle du dessin pixel-art validé (murs sculptés, fenêtres cintrées, escalier Nord,
  œuf ailé, piliers cordés, plancher chêne miel sans ombre ni motif) par échantillonnage médoïde sans flou
  (ZÉRO couleur anti-aliasée inventée entre contour et bois, ZÉRO débordement du fond sur les bords).
- Fond extérieur marron clair uni (#C69B6E), ZÉRO interstice au seuil Sud (halo Chunsoft centré cx=319.5
  et plancher encastré de 3 px sous les jambages de racines).
- Séparation propre en 8 calques Paint.NET (.ora OpenRaster + PNG individuels + .tile/.rsground PMDO 0.8.12.0),
  avec la verdure suspendue isolée sur le calque 04.
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
REPO_ROOT = Path("/var/tmp/PMDO-Destiny")
GAME = REPO_ROOT / "game"

BG_LIGHT_BROWN = (198, 155, 110)   # #C69B6E marron clair extérieur
OUTLINE_DARK = (42, 23, 14)        # #2A170E contour extérieur net 1px

HALO_LIP_WHITE = (255, 253, 242)
HALO_BAND_1 = (255, 249, 220)
HALO_BAND_2 = (253, 234, 174)
HALO_BAND_3 = (246, 208, 120)
HALO_BAND_4 = (238, 178, 76)

LEAF_RAMP = np.array([
    [32, 54, 22],     # 0: contour 1px feuillage chaud harmonisé au bois
    [52, 94, 34],     # 1: vert forêt ombre
    [80, 132, 44],    # 2: vert franc
    [122, 166, 52],   # 3: vert tendre ensoleillé
    [176, 194, 66],   # 4: pointe dorée
], dtype=np.uint8)


def extract_clean_room_2x(src_path: Path, w2x: int = 1280, h2x: int = 960) -> Tuple[np.ndarray, np.ndarray]:
    """
    Charge `accueil_regenere_au_propre.png` (1448x1086, ratio 4:3 exact), ajoute une marge symétrique
    (#C69B6E : haut=32, bas=16, gauche=32, droite=32 -> 1512x1134, ratio 4:3 exact) pour que la pointe
    haute des racines ne touche pas le bord, isole le fond par remplissage depuis les 4 coins (0 fuite
    dans le plancher Sud !), et redimensionne proprement en 1280x960 pour échantillonnage médoïde 2x2 -> 640x480.
    """
    raw = np.array(Image.open(src_path).convert("RGB"))
    rh, rw, _ = raw.shape  # 1086 x 1448

    # Close the 2px top-edge contact on the two tiny crown root tips before padding
    top_fg = np.abs(raw[0, :, 2].astype(int) - 113) > 20
    if np.any(top_fg):
        xs_t = np.where(top_fg)[0]

    pad_t, pad_b, pad_l, pad_r = 32, 16, 32, 32
    ph, pw = rh + pad_t + pad_b, rw + pad_l + pad_r  # 1134 x 1512 (exact 4:3!)
    canvas = np.full((ph, pw, 3), BG_LIGHT_BROWN, dtype=np.uint8)
    canvas[pad_t : pad_t + rh, pad_l : pad_l + rw] = raw

    # Cap the 1px tip where the two highest twigs touched y_raw=0 so their outline closes naturally
    if np.any(top_fg):
        for x_raw in xs_t:
            canvas[pad_t - 2 : pad_t + 1, pad_l + x_raw] = OUTLINE_DARK

    # Flood-fill background strictly from the 4 corners where RGB matches the uniform #C69B6E-like tan background
    r = canvas[:, :, 0].astype(np.int16)
    g = canvas[:, :, 1].astype(np.int16)
    b = canvas[:, :, 2].astype(np.int16)
    bg_like = (np.abs(r - 199) <= 12) & (np.abs(g - 157) <= 12) & (np.abs(b - 112) <= 13)
    lbl_bg, _ = ndimage.label(bg_like)
    corner_labels = {
        int(lbl_bg[0, 0]), int(lbl_bg[0, -1]), int(lbl_bg[-1, 0]), int(lbl_bg[-1, -1])
    } - {0}
    ext_bg = np.isin(lbl_bg, list(corner_labels))

    # Keep ONLY the single main room connected component (deletes any tiny stray corner dust dot!)
    fg_main_raw = ~ext_bg
    lbl_fg, n_fg = ndimage.label(fg_main_raw)
    if n_fg > 1:
        sz = ndimage.sum(fg_main_raw, lbl_fg, range(1, n_fg + 1))
        fg_main_raw = lbl_fg == (int(np.argmax(sz)) + 1)

    canvas[~fg_main_raw] = BG_LIGHT_BROWN

    # Nearest-neighbor / exact-grid remap to 1280x960 (preserves sharp pixel edges without LANCZOS blur!)
    rgb_2x = np.array(Image.fromarray(canvas, "RGB").resize((w2x, h2x), Image.Resampling.NEAREST))
    fg_2x = np.array(Image.fromarray((fg_main_raw.astype(np.uint8) * 255), "L").resize((w2x, h2x), Image.Resampling.NEAREST)) > 127
    return rgb_2x, fg_2x


def medoid_downsample_clean_1x(rgb2x: np.ndarray, fg2x: np.ndarray, w1x: int = 640, h1x: int = 480) -> Tuple[np.ndarray, np.ndarray]:
    """
    Échantillonne chaque bloc 2x2 vers 1x1 par médoïde parmi les pixels de premier plan (0 mélange
    avec le fond #C69B6E, 0 couleur floue inventée), quantifie sur une palette fidèle de 42 couleurs
    et supprime uniquement les pixels parasites isolés de 1 px (sans jamais toucher aux traits !).
    """
    fg_blocks = fg2x.reshape(h1x, 2, w1x, 2).transpose(0, 2, 1, 3).reshape(h1x, w1x, 4)
    fg1x = fg_blocks.sum(axis=2) >= 2
    lbl1, n1 = ndimage.label(fg1x)
    if n1 > 1:
        sz1 = ndimage.sum(fg1x, lbl1, range(1, n1 + 1))
        fg1x = lbl1 == (int(np.argmax(sz1)) + 1)

    blocks = rgb2x.reshape(h1x, 2, w1x, 2, 3).transpose(0, 2, 1, 3, 4).reshape(h1x, w1x, 4, 3)
    w_mask = fg_blocks.astype(np.float32)
    w_sum = np.maximum(w_mask.sum(axis=2, keepdims=True), 1.0)
    mean_rgb = (blocks.astype(np.float32) * w_mask[:, :, :, None]).sum(axis=2) / w_sum[:, :, 0, None]
    dists = ((blocks.astype(np.float32) - mean_rgb[:, :, None, :]) ** 2).sum(axis=3)
    dists = np.where(fg_blocks, dists, 1e12)
    best_idx = np.argmin(dists, axis=2)

    yy, xx = np.meshgrid(np.arange(h1x), np.arange(w1x), indexing="ij")
    rgb1x = blocks[yy, xx, best_idx].astype(np.uint8)
    rgb1x[~fg1x] = BG_LIGHT_BROWN

    # Purge any accidentally grey/desaturated pixel inside foreground (keep 100% warm palette)
    r = rgb1x[:, :, 0].astype(np.int16)
    g = rgb1x[:, :, 1].astype(np.int16)
    b = rgb1x[:, :, 2].astype(np.int16)
    grey_p = fg1x & (np.abs(r - g) <= 6) & (np.abs(g - b) <= 6) & (r < 245)
    if np.any(grey_p):
        valid = fg1x & (~grey_p)
        _, idx_g = ndimage.distance_transform_edt(~valid, return_indices=True)
        rgb1x[grey_p] = rgb1x[idx_g[0][grey_p], idx_g[1][grey_p]]

    # Quantize foreground faithfully onto 42 warm pixel-art colors (dither=NONE)
    probe = rgb1x.copy()
    probe[~fg1x] = (64, 34, 18)
    q_pil = Image.fromarray(probe, "RGB").quantize(colors=42, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    qarr = np.array(q_pil)
    qarr[~fg1x] = BG_LIGHT_BROWN

    # Remove ONLY true single-pixel (size == 1 in 8-connectivity) isolated color specks on bright wood/planks
    # while preserving all dark outlines, grain lines, and bevel highlights!
    lum = 0.299 * qarr[:, :, 0] + 0.587 * qarr[:, :, 1] + 0.114 * qarr[:, :, 2]
    editable = fg1x & (lum >= 85.0)
    codes = (
        (qarr[:, :, 0].astype(np.int32) << 16)
        | (qarr[:, :, 1].astype(np.int32) << 8)
        | qarr[:, :, 2].astype(np.int32)
    )
    struct8 = np.ones((3, 3), dtype=bool)
    single_speck = np.zeros((h1x, w1x), dtype=bool)
    for c in np.unique(codes[editable]):
        cm = editable & (codes == c)
        lbl_c, nc = ndimage.label(cm, structure=struct8)
        if nc > 0:
            sz_c = ndimage.sum(cm, lbl_c, range(1, nc + 1))
            s1 = np.where(sz_c == 1)[0] + 1
            if len(s1):
                single_speck |= np.isin(lbl_c, s1)

    if np.any(single_speck):
        ys_s, xs_s = np.where(single_speck)
        cleaned = qarr.copy()
        for y, x in zip(ys_s, xs_s):
            y0, y1 = max(0, y - 1), min(h1x, y + 2)
            x0, x1 = max(0, x - 1), min(w1x, x + 2)
            nb_m = fg1x[y0:y1, x0:x1] & (~single_speck[y0:y1, x0:x1])
            if np.any(nb_m):
                vals, cnts = np.unique(codes[y0:y1, x0:x1][nb_m], return_counts=True)
                bc = int(vals[int(np.argmax(cnts))])
                cleaned[y, x] = [(bc >> 16) & 255, (bc >> 8) & 255, bc & 255]
        qarr = cleaned

    # Ensure crisp 8-connected 1px dark-brown exterior outline EXCEPT across the open South entrance sill!
    eroded8 = ndimage.binary_erosion(fg1x, structure=np.ones((3, 3), dtype=bool))
    ext_border = fg1x & (~eroded8)
    open_sill_zone = (yy >= 435) & (xx >= 274) & (xx <= 365)
    qarr[ext_border & (~open_sill_zone)] = OUTLINE_DARK
    qarr[~fg1x] = BG_LIGHT_BROWN

    return qarr, fg1x


def build_clean_vine_sprite(vines_path: Path, tw: int, th: int) -> Image.Image:
    raw = np.array(Image.open(vines_path).convert("RGB"))
    r, g, b = raw[:, :, 0].astype(int), raw[:, :, 1].astype(int), raw[:, :, 2].astype(int)
    is_mag = ((r > 195) & (g < 85) & (b > 195) & ((r + b - 2 * g) > 220)) | (
        (r > 165) & (g < 105) & (b > 165) & ((r - g) > 75) & ((b - g) > 75)
    )
    fg = ~is_mag
    lbl, n = ndimage.label(fg)
    sz = ndimage.sum(fg, lbl, range(1, n + 1))
    main_fg = lbl == (int(np.argmax(sz)) + 1)

    ys, xs = np.where(main_fg)
    pad = 24
    x0, x1 = max(0, int(xs.min()) - pad), min(raw.shape[1], int(xs.max()) + pad)
    y0, y1 = max(0, int(ys.min()) - pad), min(raw.shape[0], int(ys.max()) + pad)

    crop_rgb = raw[y0:y1, x0:x1].copy()
    crop_fg = main_fg[y0:y1, x0:x1]
    # Despill magenta fringe on leaves
    dil_bg = ndimage.binary_dilation(~crop_fg, iterations=3)
    fringe = crop_fg & dil_bg & (((crop_rgb[:, :, 0].astype(int) - crop_rgb[:, :, 1].astype(int)) > 20))
    if np.any(fringe):
        pure = crop_fg & (~fringe)
        _, idx = ndimage.distance_transform_edt(~pure, return_indices=True)
        crop_rgb[fringe] = crop_rgb[idx[0][fringe], idx[1][fringe]]
    crop_rgb[~crop_fg] = BG_LIGHT_BROWN

    rgb2x = np.array(Image.fromarray(crop_rgb, "RGB").resize((tw * 2, th * 2), Image.Resampling.NEAREST))
    fg2x = np.array(Image.fromarray((crop_fg.astype(np.uint8) * 255), "L").resize((tw * 2, th * 2), Image.Resampling.NEAREST)) > 127

    fg_blocks = fg2x.reshape(th, 2, tw, 2).transpose(0, 2, 1, 3).reshape(th, tw, 4)
    fg1x = fg_blocks.sum(axis=2) >= 2
    blocks = rgb2x.reshape(th, 2, tw, 2, 3).transpose(0, 2, 1, 3, 4).reshape(th, tw, 4, 3)
    rgb1x = blocks[:, :, 0]

    eroded8 = ndimage.binary_erosion(fg1x, structure=np.ones((3, 3), dtype=bool))
    ext1 = fg1x & (~eroded8)
    inner = fg1x & (~ext1)

    out = np.zeros((th, tw, 4), dtype=np.uint8)
    if np.any(inner):
        px = rgb1x[inner].astype(np.int32)
        d2 = ((px[:, None, :] - LEAF_RAMP[1:, :][None, :, :].astype(np.int32)) ** 2).sum(axis=-1)
        out[inner, :3] = LEAF_RAMP[1 + np.argmin(d2, axis=1)]
    out[ext1, :3] = LEAF_RAMP[0]
    out[fg1x, 3] = 255
    return Image.fromarray(out, "RGBA")


def build_accueil_from_validated() -> Tuple[Dict[str, List[np.ndarray]], List[Tuple[str, np.ndarray]], Image.Image, np.ndarray]:
    W, H = 640, 480
    GW, GH = W // 8, H // 8
    LAYERS_OUT.mkdir(parents=True, exist_ok=True)

    rgb2x, fg2x = extract_clean_room_2x(PDN_DIR / "accueil_regenere_au_propre.png", W * 2, H * 2)
    room_q, room_mask = medoid_downsample_clean_1x(rgb2x, fg2x, W, H)

    yy, xx = np.mgrid[0:H, 0:W]
    lum = 0.299 * room_q[:, :, 0] + 0.587 * room_q[:, :, 1] + 0.114 * room_q[:, :, 2]

    # Segment inner wooden plank floor + South entrance walkway cleanly along the room's own dark baseboard line!
    in_oval_cand = (((xx - 320.0) / 199.0) ** 2 + ((yy - 258.0) / 88.0) ** 2 <= 1.0) & (yy >= 166)
    in_south_cand = (yy >= 332) & (yy <= 456) & (xx >= 272) & (xx <= 367)
    # Baseboard / wall-base outline in `accueil_regenere_au_propre.png` is dark brown (lum <= 76), whereas planks + plank seams have lum > 82!
    wall_barrier = (lum <= 74.0) | (~room_mask)
    seed_walk = (in_oval_cand | in_south_cand) & (~wall_barrier)
    lbl_fl, _ = ndimage.label(seed_walk)
    floor_core = lbl_fl == lbl_fl[250, 320]
    floor_core = ndimage.binary_closing(floor_core, structure=np.ones((3, 3), dtype=bool))
    floor_core = ndimage.binary_fill_holes(floor_core)
    # Keep stairs strictly on wall/stair layer (discover exact bottom step line around y=166..178 at x=320)
    stair_base_candidates = np.where((lum[158:184, 320] <= 78.0))[0] + 158
    stair_bot_y = int(stair_base_candidates.max()) if len(stair_base_candidates) else 172
    floor_core[yy <= stair_bot_y] = False

    # Measure exact South doorway bottom row & width in `accueil_regenere_au_propre.png`!
    ys_s_fl, xs_s_fl = np.where(floor_core & (yy >= 410))
    sill_bot_y = int(ys_s_fl.max())
    xs_at_sill = np.where(floor_core[sill_bot_y - 2])[0]
    x_door_l, x_door_r = int(xs_at_sill.min()), int(xs_at_sill.max())
    cx_h = 0.5 * (x_door_l + x_door_r)
    half_w_vis = 0.5 * (x_door_r - x_door_l)

    # Wall shell = all room pixels outside floor_core
    wall_shell_mask = room_mask & (~floor_core)

    # Extend floor layer 3px UNDER wall_shell_mask (using nearest plank color) so Paint.NET layer 01 has ZERO lateral seam!
    plank_src = floor_core
    _, idx_pl = ndimage.distance_transform_edt(~plank_src, return_indices=True)
    plank_extended_rgb = room_q[idx_pl[0], idx_pl[1]]

    # Gentle Chunsoft curved doorway sill lip (+3px convex arc at center, 100% opaque -> ZERO interstice!)
    nx_vis = (xx - cx_h) / max(half_w_vis, 1.0)
    nx_under = (xx - cx_h) / (half_w_vis + 3.0)
    in_door_under = np.abs(nx_under) <= 1.0
    lip_bot_y = float(sill_bot_y) + 3.0 * np.maximum(0.0, 1.0 - nx_vis * nx_vis)
    lip_top_y = lip_bot_y - 2.5

    open_sill_fill = (~wall_shell_mask) & in_door_under & (yy >= sill_bot_y - 4) & (yy <= np.floor(lip_bot_y))
    floor_underlap = (ndimage.binary_dilation(floor_core, iterations=3) & room_mask) | open_sill_fill
    floor_underlap[yy <= stair_bot_y - 2] = False

    # Walkable 8x8 collision grid
    walk_grid = np.zeros((GW, GH), dtype=bool)
    poly_img = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(poly_img)
    chamber_poly = [
        (232, 180), (288, 180), (288, 120), (352, 120), (352, 180), (408, 180),
        (464, 200), (504, 228), (520, 260), (504, 292), (464, 320), (408, 340),
        (360, 344), (360, min(448, sill_bot_y)), (280, min(448, sill_bot_y)), (280, 344), (232, 340), (176, 320),
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
    # Assemblage des 8 Calques Paint.NET :
    # --------------------------------------------------------------------------
    # 00 : Fond Marron Clair Uni (#C69B6E) + assise bois sous la coque (strictement hors seuil Sud !)
    l0_bg = np.zeros((H, W, 4), dtype=np.uint8)
    l0_bg[:, :] = [BG_LIGHT_BROWN[0], BG_LIGHT_BROWN[1], BG_LIGHT_BROWN[2], 255]
    l0_bg[room_mask & (~(in_door_under & (yy >= sill_bot_y - 6)))] = [52, 30, 16, 255]

    # 01 : Plancher Chêne Miel Net (issu directement du rendu validé + encastrement 3 px sous les murs)
    l1_floor = np.zeros((H, W, 4), dtype=np.uint8)
    l1_floor[floor_underlap, :3] = plank_extended_rgb[floor_underlap]
    l1_floor[floor_core, :3] = room_q[floor_core]
    l1_floor[floor_underlap, 3] = 255

    # 07 (Top, Layer=4) : Couronne avant-plan de racines Sud (strictement hors sol praticable)
    m_top = wall_shell_mask & (~walk_tiles_px) & (
        (yy >= 348) | ((yy >= 308) & ((xx <= 148) | (xx >= 492)))
    )
    m_wall_bot = wall_shell_mask & (~m_top)

    # 02 : Profondeur sombre de l'arche d'escalier Nord
    in_arch_top = (yy >= 84) & (yy <= 132) & (xx >= 286) & (xx <= 354) & (lum <= 66.0)
    m_stair_depth = m_wall_bot & in_arch_top
    m_walls_main = m_wall_bot & (~m_stair_depth)

    l2_stair = np.zeros((H, W, 4), dtype=np.uint8)
    l2_stair[m_stair_depth, :3] = room_q[m_stair_depth]
    l2_stair[m_stair_depth, 3] = 255

    l3_walls = np.zeros((H, W, 4), dtype=np.uint8)
    l3_walls[m_walls_main, :3] = room_q[m_walls_main]
    l3_walls[m_walls_main, 3] = 255

    l7_top = np.zeros((H, W, 4), dtype=np.uint8)
    l7_top[m_top, :3] = room_q[m_top]
    l7_top[m_top, 3] = 255

    # 04 : Verdure & Lianes Suspendues séparées (modulaires dans Paint.NET)
    vine_spr = build_clean_vine_sprite(PDN_DIR / "pdn_lianes_suspendues_magenta.png", 128, 98)
    vine_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vine_r = vine_spr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    vine_canvas.paste(vine_spr, (158, 20), vine_spr)
    vine_canvas.paste(vine_r, (354, 20), vine_r)
    l4_vines = np.array(vine_canvas, dtype=np.uint8)
    win_glass = (room_q[:, :, 0] >= 242) & (room_q[:, :, 1] >= 220) & (yy < 195) & ((xx < 220) | (xx > 420))
    outside_room = ~ndimage.binary_dilation(room_mask, iterations=4)
    l4_vines[win_glass | outside_room, 3] = 0

    # 05 : Respiration lumineuse douce des vitres + grains de pollen 1px (12 phases)
    sun_frames: List[np.ndarray] = []
    aura_core = wall_shell_mask & win_glass
    motes = [
        (174, 152, 0), (186, 166, 4), (162, 168, 8),
        (466, 152, 2), (454, 166, 6), (478, 168, 10),
    ]
    for ph in range(12):
        fr = np.zeros((H, W, 4), dtype=np.uint8)
        breath = 0.5 + 0.5 * math.sin(2.0 * math.pi * ph / 12.0)
        fr[aura_core] = [255, 250, 212, int(round((18 + 12 * breath) / 4.0) * 4)]
        for mx0, my0, off in motes:
            t = (ph + off) % 12
            dx = int(round(2.0 * math.cos(2.0 * math.pi * t / 12.0)))
            dy = int(round(2.0 * math.sin(2.0 * math.pi * t / 12.0)))
            ma = 112 + int(64 * (0.5 + 0.5 * math.sin(2.0 * math.pi * t / 12.0)))
            px_x, px_y = mx0 + dx, my0 + dy
            if 0 <= px_x < W - 1 and 0 <= px_y < H - 1 and wall_shell_mask[px_y, px_x]:
                fr[px_y, px_x] = [255, 253, 224, ma]
        sun_frames.append(fr)

    # 06 : Halo d'Entrée Sud Chunsoft centré (cx_h) & sans aucun interstice (12 phases)
    open_south_canvas = (~wall_shell_mask) & in_door_under & (yy >= sill_bot_y - 54) & (yy <= np.floor(lip_bot_y))
    lip_mask = open_south_canvas & (yy >= np.floor(lip_top_y))
    lip_warm_rim = (~wall_shell_mask) & in_door_under & (yy == np.floor(lip_bot_y) + 1) & (np.abs(nx_vis) <= 0.96)

    rx_arc = half_w_vis * 0.96
    ry_arc = half_w_vis * 0.88
    rad_arc = np.sqrt(((xx - cx_h) / max(rx_arc, 1.0)) ** 2 + np.maximum(0.0, (float(sill_bot_y) + 1.0 - yy) / max(ry_arc, 1.0)) ** 2)

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
        fr[arc_b4] = [HALO_BAND_4[0], HALO_BAND_4[1], HALO_BAND_4[2], int(round((52 + 16 * pulse) / 4.0) * 4)]
        fr[arc_b3] = [HALO_BAND_3[0], HALO_BAND_3[1], HALO_BAND_3[2], int(round((100 + 18 * pulse) / 4.0) * 4)]
        fr[arc_b2] = [HALO_BAND_2[0], HALO_BAND_2[1], HALO_BAND_2[2], int(round((160 + 20 * pulse) / 4.0) * 4)]
        fr[arc_b1] = [HALO_BAND_1[0], HALO_BAND_1[1], HALO_BAND_1[2], int(round((216 + 20 * pulse) / 4.0) * 4)]
        fr[lip_warm_rim] = [226, 186, 124, 255]
        fr[lip_c2] = [250, 224, 152, 255]
        fr[lip_c1] = [255, 245, 204, 255]
        fr[lip_c0] = [HALO_LIP_WHITE[0], HALO_LIP_WHITE[1], HALO_LIP_WHITE[2], 255]
        inout_frames.append(fr)

    pdn_static_layers: List[Tuple[str, np.ndarray]] = [
        ("fond_marron_clair", l0_bg),
        ("plancher_chene_net_sans_ombre", l1_floor),
        ("profondeur_escalier_nord", l2_stair),
        ("parois_bois_escalier_et_fenetres", l3_walls),
        ("verdure_et_lianes_suspendues", l4_vines),
        ("lumiere_fenetres_et_pollen", sun_frames[3]),
        ("halo_entree_sud_chunsoft_sans_interstice", inout_frames[3]),
        ("avant_plan_racines_sud_top", l7_top),
    ]
    for idx, (lname, larr) in enumerate(pdn_static_layers):
        Image.fromarray(larr, "RGBA").save(LAYERS_OUT / f"{idx:02d}_{lname}.png")

    # Export OpenRaster .ora multi-layer Paint.NET file
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

    # Save version WITHOUT hanging vines as well so user has both immediate PNGs!
    comp_no_vines = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    for lname, l_arr in pdn_static_layers:
        if "verdure" not in lname:
            comp_no_vines = Image.alpha_composite(comp_no_vines, Image.fromarray(l_arr, "RGBA"))
    comp_no_vines.convert("RGB").save(PDN_DIR / "rendu_final_accueil_sans_verdure_1x.png")

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
    print(f"[INFO] Accueil segmenté : stair_bot_y={stair_bot_y}, sill_bot_y={sill_bot_y}, door=({x_door_l}..{x_door_r}, cx={cx_h:.1f})")
    return layers_pmdo, pdn_static_layers, comp_rgb, walk_grid


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


def compile_accueil_pmdo(layers_dict: Dict[str, List[np.ndarray]], walk_grid: np.ndarray) -> None:
    w, h = 640, 480
    gw, gh = w // 8, h // 8
    asset_name = "guilde_destiny_accueil"
    sheet_name = "Destiny_Guilde_Accueil"

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
        ("01 parquet chene dore net sans ombre", "01_parquet_chene_et_medaillon", 0, 60),
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
            "Name": {"DefaultText": "Destiny Guild - Reception Hall", "LocalTexts": {"fr": "Grande Guilde — Salle d’accueil"}},
            "Released": True,
            "Comment": "Salle d'accueil régénérée au propre (640x480, 8 calques Paint.NET/PMDO, fond marron clair #C69B6E, verdure séparée, 0 interstice Sud).",
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
                "GroundObjects": [
                    make_touch_obj("SortieGuilde", 280, 420, 80, 20),
                    make_touch_obj("EscalierNord", 288, 120, 64, 18),
                ],
                "Spawners": [],
                "Markers": [
                    make_marker("EntreeSudMarker", 312, 384, 4),
                    make_marker("CentreMedaillonMarker", 312, 248, 0),
                    make_marker("EscalierNordMarker", 312, 160, 0),
                ],
            }],
        },
    }
    rs_txt = json.dumps(ground_doc, ensure_ascii=False, indent=2) + "\n"
    if (GAME / "Data/Ground").exists():
        (GAME / f"Data/Ground/{asset_name}.rsground").write_text(rs_txt, encoding="utf-8")
    (PDN_DIR / f"{asset_name}.rsground").write_text(rs_txt, encoding="utf-8")
    print(f"[OK] {asset_name} ({w}x{h}): {sheet_name}.tile ({n_tiles} tuiles 8x8).")


def build_showcase_board(pdn_layers: List[Tuple[str, np.ndarray]], acc_rgb: Image.Image) -> None:
    W_B, H_B = 1520, 1090
    board = Image.new("RGB", (W_B, H_B), (36, 26, 20))
    dr = ImageDraw.Draw(board)

    dr.text((28, 16), "Rendu 1:1 (640x480) - Accueil Guilde Destiny regenere au propre (avec calque verdure activable)", fill=(252, 236, 196))
    board.paste(acc_rgb, (28, 42))

    dr.text((692, 16), "Zoom 3x Murs + Fenetre + Pilier + Oeuf aile + Escalier Nord (rendu propre valide)", fill=(204, 244, 196))
    z_win_st3 = acc_rgb.crop((130, 74, 394, 172)).resize((264 * 3, 98 * 3), Image.Resampling.NEAREST)
    board.paste(z_win_st3, (692, 42))

    dr.text((692, 348), "Zoom 3x Oeuf aile & Escalier + Zoom 3x Seuil Sud (halo Chunsoft, 0 interstice)", fill=(255, 228, 168))
    z_egg3 = acc_rgb.crop((258, 36, 382, 98)).resize((124 * 3, 62 * 3), Image.Resampling.NEAREST)
    board.paste(z_egg3, (692, 372))
    z_sill3 = acc_rgb.crop((258, 392, 382, 454)).resize((124 * 3, 62 * 3), Image.Resampling.NEAREST)
    board.paste(z_sill3, (1084, 372))

    dr.text((28, 566), "Reseau Multicalque Paint.NET (.ora OpenRaster + 8 calques PNG individuels) :", fill=(252, 236, 196))
    yy, xx = np.mgrid[0:216, 0:320]
    chk = np.where(((xx // 8) + (yy // 8)) % 2 == 0, 224, 192).astype(np.uint8)
    chk_rgba = np.stack([chk, chk, chk, np.full_like(chk, 255)], axis=-1)

    labels_fr = [
        "00. Fond marron clair uni (#C69B6E)",
        "01. Plancher chene net sans ombre",
        "02. Profondeur arche escalier Nord",
        "03. Parois bois, escalier & fenetres",
        "04. Verdure & lianes separees",
        "05. Lumiere fenetres & pollen (12 ph.)",
        "06. Halo Sud Chunsoft (0 interstice)",
        "07. Couronne racines avant-plan (Top)",
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
    acc_layers, pdn_layers, acc_rgb, acc_walk = build_accueil_from_validated()
    compile_accueil_pmdo(acc_layers, acc_walk)
    build_showcase_board(pdn_layers, acc_rgb)
    print("[OK] Compilation complète de l'accueil régénéré au propre terminée.")


if __name__ == "__main__":
    main()
