#!/usr/bin/env python3
"""Construction complète du complexe `dojo_kingambit` (3 salles raccordées) selon `METHODE_MAGENTA_ET_GENERATEUR.md` :
1. `dojo_kingambit` (`768 x 576`, 15 calques) : salle d'accueil spacieuse avec DEUX portes sarcelle au nord qui
   coulissent proprement dans leur arche de pierre (sans bris ni gravats : `0% -> 33% -> 66% -> 100% ouverte`),
   5 braseros sculptés à flammes EoS animées, 2 cristaux cyan animés, sceau runique central et ronces `Top`.
2. `dojo_kingambit_arene` (`768 x 576`, 9 calques) : grande arène de combat octogonale assortie derrière la porte
   nord gauche (6 braseros EoS animés, 2 cristaux cyan animés, grand octogone runique orange pulsant, estrade nord).
3. `dojo_kingambit_reliques` (`768 x 576`, 9 calques) : salle des reliques et archives du dojo derrière la porte
   nord droite (4 braseros EoS animés, 4 cristaux cyan animés, monument runique nord, coffres sarcelle, parchemin
   ancien et stèles gravées).
"""
from collections import deque
from pathlib import Path
import hashlib
import io
import json
import struct

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art/dojo_kingambit_magenta"
RAW = ART / "bruts"
TILE_DIR = ROOT / "game/Content/Tile"
GROUND_DIR = ROOT / "game/Data/Ground"
ZONE_DIR = ROOT / "game/Data/Zone"

W, H = 768, 576
GW, GH = W // 8, H // 8
SRC = (1200, 896)
SCALE = H / SRC[1]
SCALED_W = round(SRC[0] * SCALE)
CROP_X = (SCALED_W - W) // 2

PHASES = 12
ANIM_TICKS = 6
STATIC_TICKS = 60
FIDELITY_MAX = 35.0

FLAME_CMAP = {
    "W": (255, 247, 135),
    "Y": (255, 223, 7),
    "O": (255, 159, 0),
    "R": (247, 87, 7),
    "r": (247, 15, 7),
    "c": (207, 79, 55),
}

CANON_FLAME_ROWS = [
    "................",
    "................",
    "..........rr....",
    "..........rrrr..",
    "..........rrRr..",
    "...........rRrr.",
    "...........rORr.",
    "...........rORr.",
    "...........rORr.",
    "..........rRRrr.",
    "....r.....rRrr..",
    "...rRr...rRrrr..",
    "..rRRr...rrrr...",
    "..rRrr..rrrr....",
    "..rrr...rrr.....",
    "...rc...rrr.....",
    ".....rr.rrr.....",
    ".....rrrrrrc....",
    ".....rrrrrrr....",
    ".....crrrrrr....",
    "......rrrRrr....",
    "......rrrRrrr...",
    "......rrROrrr...",
    ".....rrROYRrrr..",
    ".....rrRYORrrr..",
    "....crrRYORrrr..",
    "....rrrROYORrrc.",
    "...rrrRROYORrrr.",
    "...rrrRRYYORrrr.",
    "..rrrRROYYORrr..",
    "..rrrROWWYORrr..",
    "..crrRYWWWYRrc..",
    "...rrRWWWWYRr...",
    "...rrRYWWWYRr...",
    "....rROWWYOr....",
    ".....rRYYOR.....",
    "......rRRR......",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def keep_large(mask: np.ndarray, min_px: int) -> np.ndarray:
    lbl, n = nd.label(mask)
    if n == 0:
        return np.zeros_like(mask, dtype=bool)
    sizes = np.bincount(lbl.ravel())
    sizes[0] = 0
    return sizes[lbl] >= min_px


def key_magenta(rgb_arr: np.ndarray) -> np.ndarray:
    r, g, b = rgb_arr.transpose(2, 0, 1).astype(float)
    bg = (r > 70) & (b > 70) & (r > g * 1.45) & (b > g * 1.45)
    fringe = nd.binary_dilation(bg, iterations=2) & (r > g * 1.05) & (b > g * 1.05)
    return bg | fringe


def resize_plane(plane: np.ndarray) -> np.ndarray:
    im = Image.fromarray(plane.astype(np.float32), mode="F")
    resized = np.array(im.resize((SCALED_W, H), Image.Resampling.BOX))
    return resized[:, CROP_X : CROP_X + W]


def down_masked(rgb_arr: np.ndarray, fg_src: np.ndarray):
    w = resize_plane(fg_src.astype(np.float32))
    mask = keep_large(nd.binary_fill_holes(w >= 0.5), 400)
    cols = (
        np.stack([resize_plane(rgb_arr[..., ch] * fg_src) for ch in range(3)], axis=-1)
        / np.maximum(w, 1e-6)[..., None]
    )
    out = np.clip(np.round(cols), 0, 255).astype(np.uint8)
    out[~mask] = 0
    return out, mask


def down_full(rgb_arr: np.ndarray) -> np.ndarray:
    cols = np.stack([resize_plane(rgb_arr[..., ch].astype(np.float32)) for ch in range(3)], axis=-1)
    return np.clip(np.round(cols), 0, 255).astype(np.uint8)


def graft_brazier_domes(decor_rgb: np.ndarray, src_center: tuple, targets: list) -> np.ndarray:
    """Copie le dôme de pierre sculpté plein du brasero de référence sur les braseros ouverts."""
    out = decor_rgb.copy()
    scx, scy = src_center
    src_patch = out[scy - 30 : scy + 28, scx - 30 : scx + 30].copy()  # 58 x 60
    py, px = np.mgrid[:58, :60]
    dist = np.sqrt(((px - 30.0) / 28.5) ** 2 + ((py - 30.0) / 26.5) ** 2)
    alpha = np.clip((1.04 - dist) / 0.12, 0.0, 1.0)[..., None]
    for tcx, tcy, flip in targets:
        patch = src_patch[:, ::-1] if flip else src_patch
        y0, x0 = tcy - 30, tcx - 30
        dst = out[y0 : y0 + 58, x0 : x0 + 60].astype(np.float32)
        out[y0 : y0 + 58, x0 : x0 + 60] = np.clip(
            np.round(dst * (1.0 - alpha) + patch.astype(np.float32) * alpha), 0, 255
        ).astype(np.uint8)
    return out


def clear_doorway_sand_walkways(decor_rgb: np.ndarray, sol_rgb: np.ndarray, door_cxs: list) -> np.ndarray:
    """Dégage un chemin sableux net (sans cavités) menant jusqu'au seuil des deux portes nord."""
    out = decor_rgb.copy()
    for cx in door_cxs:
        wy0, wy1, wx0, wx1 = 152, 196, cx - 21, cx + 21
        py, px = np.mgrid[wy0:wy1, wx0:wx1]
        ax = np.clip((21.0 - np.abs(px - cx)) / 3.0, 0.0, 1.0)
        ay = np.clip(np.minimum((py - wy0) / 2.5, (wy1 - 1 - py) / 3.5), 0.0, 1.0)
        aw = (ax * ay)[..., None]
        shade = np.clip(0.80 + 0.20 * ((py - 152.0) / 14.0), 0.80, 1.0)[..., None]
        sand_patch = sol_rgb[wy0:wy1, wx0:wx1].astype(np.float32) * shade
        out[wy0:wy1, wx0:wx1] = np.clip(
            np.round(out[wy0:wy1, wx0:wx1] * (1.0 - aw) + sand_patch * aw), 0, 255
        ).astype(np.uint8)
    return out


def build_sliding_door_layers_and_open_bg(decor_rgb: np.ndarray, door_cxs: list):
    """Extrait les deux vantaux sarcelle de chaque porte et construit leurs états coulissants (sans bris).

    Retourne :
      - `open_decor_rgb` : le décor avec l'encadrement de pierre intact et l'ouverture sombre nette au fond
        (avec 3 px de rebord sarcelle rentré dans les rainures latérales) ;
      - `door_states` : dict `{cx: [stage0_closed_rgba, stage1_slide8_rgba, stage2_slide16_rgba]}`.
    """
    yy, xx = np.mgrid[:H, :W]
    open_rgb = decor_rgb.copy()
    door_states = {}

    for cx in door_cxs:
        # Détecter l'arche de pierre claire extérieure pour ne JAMAIS l'entamer
        r, g, b = decor_rgb.transpose(2, 0, 1).astype(float)
        lum = decor_rgb @ np.array([0.299, 0.587, 0.114])
        # L'ouverture correspond au disque intérieur sous l'arche de pierre (vantaux sarcelle + chaînes + médaillon C)
        ell_outer = (((xx - cx) / 28.0) ** 2 + ((yy - 137.0) / 32.5) ** 2 <= 1.0) & (yy >= 104) & (yy <= 149)
        is_teal = (g > r + 5) & (b >= r - 6) & (b < 148)
        central_clasp = (((xx - cx) / 14.0) ** 2 + ((yy - 132.0) / 15.0) ** 2) <= 1.0
        lower_slot = (((xx - cx) / 25.8) ** 2 + ((yy - 137.5) / 29.8) ** 2 <= 1.0) & (yy >= 108) & (yy <= 149)
        aperture = ell_outer & (nd.binary_closing(is_teal | central_clasp, iterations=2) | lower_slot)
        aperture = nd.binary_fill_holes(aperture) & (yy <= 149)

        leaf_src = decor_rgb.copy()

        # Peindre l'embrasure ouverte propre (sans aucun débris ni pierre cassée) sur `open_rgb`
        for y in range(104, 150):
            row_xs = np.where(aperture[y])[0]
            if len(row_xs) == 0:
                continue
            x_min, x_max = int(row_xs.min()), int(row_xs.max())
            for x in row_xs:
                edge_d = min(x - x_min, x_max - x)
                top_d = y - 104
                if y >= 145:
                    t = (y - 144) / 5.0
                    col = np.array([26, 22, 17]) * (1.0 - t * 0.55) + np.array([110, 96, 62]) * (t * 0.55)
                elif edge_d <= 1 or top_d <= 1:
                    col = np.array([48, 42, 31])
                elif edge_d <= 3 or top_d <= 3:
                    col = np.array([32, 28, 21])
                else:
                    col = np.array([18, 16, 13])
                open_rgb[y, x] = np.round(col).astype(np.uint8)

        def make_shifted(shift: int) -> np.ndarray:
            ov = np.zeros((H, W, 4), dtype=np.uint8)
            icx = int(round(cx))
            for y in range(104, 150):
                for x in range(icx - 30, icx + 31):
                    if not aperture[y, x]:
                        continue
                    if x <= icx - shift:
                        sx = x + shift
                        if sx <= icx and aperture[y, sx]:
                            c = leaf_src[y, sx]
                            if shift > 0 and sx == icx:
                                c = np.array([40, 52, 42], dtype=np.uint8)
                            elif shift > 0 and sx == icx - 1:
                                c = np.clip(c.astype(int) - 18, 0, 255).astype(np.uint8)
                            ov[y, x] = (*c, 255)
                    elif x > icx + shift:
                        sx = x - shift
                        if sx > icx and aperture[y, sx]:
                            c = leaf_src[y, sx]
                            if shift > 0 and sx == icx + 1:
                                c = np.array([40, 52, 42], dtype=np.uint8)
                            elif shift > 0 and sx == icx + 2:
                                c = np.clip(c.astype(int) - 18, 0, 255).astype(np.uint8)
                            ov[y, x] = (*c, 255)
            return ov

        # Garder une fine tranche de 3 px de vantail coulissé au fond des rainures latérales à l'état ouvert
        tucked = make_shifted(23)
        tm = tucked[..., 3] > 0
        open_rgb[tm] = tucked[tm, :3]

        door_states[cx] = [make_shifted(0), make_shifted(8), make_shifted(16)]

    return open_rgb, door_states


def make_shared_96_palette(rgb_samples_terrain: np.ndarray, rgb_samples_accent: np.ndarray):
    pal_t_im = Image.fromarray(rgb_samples_terrain.reshape(-1, 1, 3), mode="RGB").quantize(
        56, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
    )
    pal_t = np.array(pal_t_im.getpalette()[: 56 * 3], dtype=np.uint8).reshape(56, 3)

    pal_a_im = Image.fromarray(rgb_samples_accent.reshape(-1, 1, 3), mode="RGB").quantize(
        40, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
    )
    pal_a = np.array(pal_a_im.getpalette()[: 40 * 3], dtype=np.uint8).reshape(40, 3)

    pal = np.concatenate([pal_t, pal_a], axis=0)
    assert pal.shape == (96, 3)
    pal_im = Image.new("P", (1, 1))
    pal_im.putpalette(list(pal.ravel()) + list(pal[0]) * (256 - 96))
    return pal, pal_im


def apply_palette(rgb_arr: np.ndarray, mask: np.ndarray, pal: np.ndarray, pal_im: Image.Image) -> np.ndarray:
    idx = np.array(Image.fromarray(rgb_arr, mode="RGB").quantize(palette=pal_im, dither=Image.Dither.NONE))
    out = pal[idx]
    out[~mask] = 0
    return out


def apply_palette_rgba(rgba_arr: np.ndarray, pal: np.ndarray, pal_im: Image.Image) -> np.ndarray:
    m = rgba_arr[..., 3] > 0
    idx = np.array(Image.fromarray(rgba_arr[..., :3], mode="RGB").quantize(palette=pal_im, dither=Image.Dither.NONE))
    out = np.zeros_like(rgba_arr)
    out[..., :3] = pal[idx]
    out[m, 3] = rgba_arr[m, 3]
    out[~m] = 0
    return out


def classify_materials_for_fidelity(rgb_arr: np.ndarray, valid_mask: np.ndarray) -> dict:
    r, g, b = rgb_arr.transpose(2, 0, 1).astype(float)
    lum = rgb_arr @ np.array([0.299, 0.587, 0.114])
    flame = (r > 200) & (b < 55) & ((r > g + 45) | (g > 175))
    v = valid_mask & ~flame
    sol_sable = v & (r >= 132) & (r <= 172) & (g >= 115) & (g <= 156) & (b >= 70) & (b <= 108) & ((r - g) <= 24) & ((g - b) >= 28)
    cristal_cyan = v & (b > r * 1.45) & (b > 135)
    porte_sarcelle = v & (g > r + 8) & (b >= r - 4) & (b < 140) & (lum > 60) & (lum < 145)
    rune_orange = v & (r > 175) & (r > g * 1.25) & (g > b * 1.35) & (b < 95)
    paroi_roche = v & ~sol_sable & ~cristal_cyan & ~porte_sarcelle & ~rune_orange & (lum > 42) & (lum < 135) & (r >= g) & (g >= b)
    return {
        "sol_sable": sol_sable,
        "paroi_roche": paroi_roche,
        "porte_sarcelle": porte_sarcelle,
        "cristal_cyan": cristal_cyan,
        "rune_orange": rune_orange,
    }


def check_fidelity(q_decor: np.ndarray, fg_mask: np.ndarray, required_mats: tuple) -> dict:
    ref_rgba = np.array(Image.open(ART / "ref_canon_rgba.png").convert("RGBA"))
    ref_rgb = ref_rgba[..., :3]
    ref_valid = ref_rgba[..., 3] > 0
    fr = classify_materials_for_fidelity(ref_rgb, ref_valid)
    fd = classify_materials_for_fidelity(q_decor, fg_mask)
    report = {}
    for mat in required_mats:
        assert fr[mat].sum() > 50 and fd[mat].sum() > 30, (mat, int(fr[mat].sum()), int(fd[mat].sum()))
        mr = ref_rgb[fr[mat]].mean(axis=0)
        md = q_decor[fd[mat]].mean(axis=0)
        dist = float(np.linalg.norm(mr - md))
        assert dist < FIDELITY_MAX, f"Fidelity threshold exceeded for {mat}: {dist:.2f} >= {FIDELITY_MAX}"
        report[mat] = {
            "rip_rgb": [round(float(x), 1) for x in mr],
            "decor_rgb": [round(float(x), 1) for x in md],
            "distance": round(dist, 2),
        }
    return report


def poly_mask(points) -> np.ndarray:
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).polygon(points, fill=255)
    return np.array(im) > 0


def rgba_from(rgb_arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.zeros((H, W, 4), dtype=np.uint8)
    out[..., :3] = rgb_arr
    out[..., 3] = 255
    out[~mask] = 0
    return out


def partition_room_layers(
    q_decor: np.ndarray,
    fg_mask: np.ndarray,
    brazier_centers: list,
    crystal_boxes: list,
    extra_bloc_boxes: list,
    floor_seal_mask: np.ndarray,
) -> dict:
    yy, xx = np.mgrid[:H, :W]
    r, g, b = q_decor.transpose(2, 0, 1).astype(float)
    lum = q_decor @ np.array([0.299, 0.587, 0.114])

    # Top (DrawLayer = 4) : ronces épineuses suspendues + cordages hauts aux coins nord
    green_vines = fg_mask & (yy < 166) & ((xx < 252) | (xx > 516)) & (g > r + 5) & (g > b + 14)
    green_vines = keep_large(nd.binary_closing(green_vines, iterations=1), 18)
    vine_with_outline = nd.binary_dilation(green_vines, iterations=1) & fg_mask & (yy < 168)
    high_ropes = fg_mask & (yy < 88) & ((xx < 185) | (xx > 583))
    mask_top = vine_with_outline | high_ropes

    rem = fg_mask & ~mask_top

    # Blocs : braseros, cristaux, rondins, piédestaux/blocs/coffres
    braziers = np.zeros((H, W), dtype=bool)
    for bcx, bcy in brazier_centers:
        braziers |= (((xx - bcx) / 28.0) ** 2 + ((yy - bcy) / 25.5) ** 2) <= 1.0

    is_flat_sand = (
        (r >= 126) & (r <= 170) & (g >= 112) & (g <= 155) & (b >= 68) & (b <= 106) & ((r - g) <= 23) & ((g - b) >= 28)
    )
    crystals = np.zeros((H, W), dtype=bool)
    for x0, y0, x1, y1 in crystal_boxes:
        crystals |= (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1) & ~is_flat_sand

    extra_blocs = np.zeros((H, W), dtype=bool)
    for x0, y0, x1, y1 in extra_bloc_boxes:
        extra_blocs |= (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1) & ~is_flat_sand

    logs = (
        ((xx >= 84) & (xx <= 128) & (yy >= 158) & (yy <= 185))
        | ((xx >= 640) & (xx <= 684) & (yy >= 158) & (yy <= 185))
    ) & ~is_flat_sand

    mask_blocs = rem & (braziers | crystals | extra_blocs | logs)
    rem2 = rem & ~mask_blocs

    floor_env = poly_mask([
        (132, 152), (636, 152),
        (666, 188), (666, 344),
        (606, 424), (446, 444),
        (442, 576), (326, 576),
        (322, 444), (162, 424),
        (102, 344), (102, 188),
    ])

    in_floor = rem2 & (floor_env | floor_seal_mask)
    near_edge = ~nd.binary_erosion(floor_env, iterations=14)
    near_blocs = nd.binary_dilation(mask_blocs, iterations=5)
    mask_ombres = in_floor & ~floor_seal_mask & (near_edge | near_blocs) & (lum < 118) & (lum > 62)

    mask_sol = in_floor & ~mask_ombres
    mask_parois = rem2 & ~in_floor

    union = mask_sol | mask_ombres | mask_parois | mask_blocs | mask_top
    assert np.array_equal(union, fg_mask), "Partition mismatch with fg_mask"
    total_sum = (
        mask_sol.astype(int)
        + mask_ombres.astype(int)
        + mask_parois.astype(int)
        + mask_blocs.astype(int)
        + mask_top.astype(int)
    )
    assert np.all(total_sum[fg_mask] == 1) and np.all(total_sum[~fg_mask] == 0), "Overlapping masks!"
    return {
        "sol": mask_sol,
        "ombres": mask_ombres,
        "parois": mask_parois,
        "blocs": mask_blocs,
        "top": mask_top,
    }


def make_canonical_flame_phases() -> list:
    fh, fw = len(CANON_FLAME_ROWS), len(CANON_FLAME_ROWS[0])
    code_grid = np.full((fh, fw), ".", dtype="<U1")
    for y, row in enumerate(CANON_FLAME_ROWS):
        for x, ch in enumerate(row):
            if ch != ".":
                code_grid[y, x] = ch

    sprites = []
    for t in range(PHASES):
        ph = 2.0 * np.pi * t / PHASES
        canvas = np.zeros((fh + 4, fw + 6, 4), dtype=np.uint8)
        for y in range(fh):
            height_ratio = max(0.0, (32.0 - y) / 30.0)
            dx = int(round(height_ratio * 1.45 * np.sin(ph - y * 0.24)))
            dy = int(round((height_ratio ** 1.4) * 1.15 * np.cos(2.0 * ph - y * 0.12)))
            for x in range(fw):
                ch = code_grid[y, x]
                if ch == ".":
                    continue
                c_use = ch
                if ch == "Y" and y >= 28 and np.sin(ph + x * 0.5) > 0.55:
                    c_use = "W"
                elif ch == "W" and y <= 31 and np.sin(ph) < -0.6:
                    c_use = "Y"
                ny = np.clip(y + 2 + dy, 0, fh + 3)
                nx = np.clip(x + 3 + dx, 0, fw + 5)
                canvas[ny, nx] = (*FLAME_CMAP[c_use], 255)
        ember_step = t % 6
        ex = 12 + (1 if ember_step in (2, 3) else 0)
        ey = max(0, 5 - ember_step)
        if ember_step < 4:
            canvas[ey, ex] = (*FLAME_CMAP["R" if ember_step < 2 else "r"], 255)
        sprites.append(canvas)
    return sprites


FLAME_SPRITES = make_canonical_flame_phases()


def build_brazier_flame_frames(brazier_specs: list) -> list:
    frames = []
    yy, xx = np.mgrid[:H, :W]
    for t in range(PHASES):
        im = Image.fromarray(np.zeros((H, W, 4), dtype=np.uint8), mode="RGBA")
        for bcx, bcy, offset, flip in brazier_specs:
            sp = FLAME_SPRITES[(t + offset) % PHASES]
            if flip:
                sp = sp[:, ::-1]
            pulse = 0.5 + 0.5 * np.sin(2.0 * np.pi * ((t + offset) % PHASES) / PHASES)
            if pulse > 0.45:
                glow = (((xx - bcx) / 7.0) ** 2 + ((yy - (bcy + 10)) / 3.5) ** 2) <= 1.0
                arr = np.array(im)
                arr[glow] = (255, 159, 0, 72 if pulse > 0.78 else 44)
                im = Image.fromarray(arr, mode="RGBA")
            im.alpha_composite(Image.fromarray(sp, mode="RGBA"), (bcx - 11, bcy - 28))
        frames.append(np.array(im))
    return frames


def build_crystal_glint_frames(q_decor: np.ndarray, fg_mask: np.ndarray, crystal_tips: list) -> list:
    r, g, b = q_decor.transpose(2, 0, 1).astype(float)
    yy, xx = np.mgrid[:H, :W]
    facets = fg_mask & (b > r * 1.45) & (b > 145)
    bright_facets = facets & (b > 185)

    star_small = [".c.", "cWc", ".c."]
    star_big = ["..c..", ".cWc.", "cWWWc", ".cWc.", "..c.."]
    cmap = {"W": (255, 255, 255, 255), "c": (135, 223, 247, 255)}

    def stamp(arr, rows, cx, cy):
        sh, sw = len(rows), len(rows[0])
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".":
                    arr[cy - sh // 2 + dy, cx - sw // 2 + dx] = cmap[ch]

    frames = []
    u = xx + yy
    for t in range(PHASES):
        f = np.zeros((H, W, 4), dtype=np.uint8)
        band_center = (t * 6) % 72
        dist = np.minimum((u - band_center) % 72, (band_center - u) % 72)
        f[facets & (dist <= 5)] = (155, 232, 252, 255)
        f[bright_facets & (dist <= 2)] = (238, 252, 255, 255)
        for idx, (tcx, tcy) in enumerate(crystal_tips):
            tp = (t + idx * 3) % PHASES
            if tp in (1, 4):
                stamp(f, star_small, tcx, tcy)
            elif tp in (2, 3):
                stamp(f, star_big, tcx, tcy)
        frames.append(f)
    return frames


def build_rune_pulse_frames(q_decor: np.ndarray, fg_mask: np.ndarray) -> list:
    r, g, b = q_decor.transpose(2, 0, 1).astype(float)
    rune_core = fg_mask & (r > 195) & (r > g * 1.32) & (g > 82) & (b < 68)
    palette_steps = [
        None,
        (236, 118, 28, 255),
        (246, 138, 32, 255),
        (255, 162, 38, 255),
        (255, 186, 56, 255),
        (255, 204, 78, 255),
        (255, 216, 96, 255),
        (255, 204, 78, 255),
        (255, 186, 56, 255),
        (255, 162, 38, 255),
        (246, 138, 32, 255),
        (236, 118, 28, 255),
    ]
    frames = []
    for t in range(PHASES):
        f = np.zeros((H, W, 4), dtype=np.uint8)
        col = palette_steps[t]
        if col is not None:
            f[rune_core] = col
        frames.append(f)
    return frames


def premult(image: Image.Image) -> Image.Image:
    a = np.array(image.convert("RGBA"), dtype=np.uint16)
    a[:, :, :3] = (a[:, :, :3] * a[:, :, 3:4]) // 255
    return Image.fromarray(a.astype(np.uint8), mode="RGBA")


def png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG", compress_level=6)
    return buf.getvalue()


class TileBank:
    def __init__(self, name: str):
        self.name = name
        empty_raw = bytes(8 * 8 * 4)
        self.ids = {empty_raw: (0, 0)}
        self.data = {(0, 0): empty_raw}

    def add(self, tile_rgba: np.ndarray):
        im = premult(Image.fromarray(tile_rgba, mode="RGBA"))
        if not im.getchannel("A").getbbox():
            return None
        raw = im.tobytes()
        if raw not in self.ids:
            n = len(self.ids)
            loc = (n % 32, n // 32)
            self.ids[raw] = loc
            self.data[loc] = raw
        loc = self.ids[raw]
        return {"Sheet": self.name, "TexLoc": {"X": loc[0], "Y": loc[1]}}

    def write(self, path: Path):
        offset = 8 + 16 * len(self.data)
        offsets, payload, entries = {}, bytearray(), []
        for (tx, ty), raw in self.data.items():
            if raw not in offsets:
                enc = png_bytes(Image.frombytes("RGBA", (8, 8), raw))
                offsets[raw] = offset + len(payload)
                payload.extend(struct.pack("<q", len(enc)) + enc)
            entries.append(struct.pack("<iiq", tx, ty, offsets[raw]))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(struct.pack("<ii", 8, len(entries)) + b"".join(entries) + payload)


def make_layer(
    name: str,
    frames: list,
    ticks: int,
    bank: TileBank,
    draw_layer: int = 0,
    visible: bool = True,
) -> dict:
    tiles = []
    empty_ref = {"Sheet": bank.name, "TexLoc": {"X": 0, "Y": 0}}
    for x in range(GW):
        col = []
        for y in range(GH):
            fs = []
            for arr in frames:
                patch = arr[y * 8 : (y + 1) * 8, x * 8 : (x + 1) * 8]
                ref = bank.add(patch)
                fs.append(ref if ref is not None else empty_ref)
            if all(f["TexLoc"] == {"X": 0, "Y": 0} for f in fs):
                col.append({"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1})
            else:
                reduced = [fs[0]] if all(f == fs[0] for f in fs) else fs
                col.append(
                    {
                        "AutoTileset": "",
                        "Associates": [],
                        "Layers": [{"Frames": reduced, "FrameLength": ticks}],
                        "NeighborCode": 0,
                    }
                )
        tiles.append(col)
    return {"Name": name, "Layer": draw_layer, "Visible": visible, "Tiles": tiles}


def assert_zero_magenta(frames_list: list):
    for name, frames in frames_list:
        for idx, arr in enumerate(frames):
            opq = arr[..., 3] > 0
            if not np.any(opq):
                continue
            r, g, b = arr[opq, 0].astype(float), arr[opq, 1].astype(float), arr[opq, 2].astype(float)
            bad = (r > g * 1.45) & (b > g * 1.32) & (r > 135) & (b > 125)
            assert not np.any(bad), f"Residual magenta pixels ({int(bad.sum())}) in {name} frame {idx}!"


def verify_navigation(blocked_cells: np.ndarray, start: tuple, targets: list):
    def free16(px: int, py: int) -> bool:
        if px < 0 or py < 0 or px + 16 > W or py + 16 > H:
            return False
        for cx in range(px // 8, (px + 15) // 8 + 1):
            for cy in range(py // 8, (py + 15) // 8 + 1):
                if blocked_cells[cy, cx] != 0:
                    return False
        return True

    assert free16(*start), f"Start marker {start} is blocked!"
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 8, y), (x - 8, y), (x, y + 8), (x, y - 8)):
            if (nx, ny) not in seen and free16(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))
    for label, pt in targets:
        assert pt in seen, f"Navigation target {label} at {pt} NOT reachable from {start}!"


def make_trigger_obj(template_gobj: dict, name: str, direction: int, trigger_type: int, x: int, y: int, w: int, h: int) -> dict:
    g = json.loads(json.dumps(template_gobj))
    g["EntName"] = name
    g["Direction"] = direction
    g["triggerType"] = trigger_type
    g["Passable"] = False
    g["Collider"] = {"X": x, "Y": y, "Width": w, "Height": h}
    return g


def make_marker_obj(name: str, direction: int, x: int, y: int) -> dict:
    return {
        "EntName": name,
        "Direction": direction,
        "EntEnabled": True,
        "EntOrder": 0,
        "InteractOrder": 0,
        "triggerType": 0,
        "Collider": {"X": x, "Y": y, "Width": 16, "Height": 16},
    }


def count_frame_refs(layers_json: list) -> int:
    return sum(
        len(anim["Frames"])
        for L in layers_json
        for col in L["Tiles"]
        for tile in col
        for anim in tile.get("Layers", [])
    )


def build_all():
    base_template = json.loads((GROUND_DIR / "dojo_kingambit.rsground").read_text(encoding="utf-8-sig"))
    tpl_gobj = base_template["Object"]["Entities"][0]["GroundObjects"][0]
    tpl_spawners = json.loads(json.dumps(base_template["Object"]["Entities"][0]["Spawners"]))

    raw_sol = np.array(Image.open(RAW / "sol_complet.png").convert("RGB"))
    sol_768 = down_full(raw_sol)

    raw_accueil = np.array(Image.open(RAW / "decor_magenta.png").convert("RGB"))
    raw_arene = np.array(Image.open(RAW / "arene_decor_magenta.png").convert("RGB"))
    raw_reliques = np.array(Image.open(RAW / "reliques_decor_magenta.png").convert("RGB"))

    acc_768, acc_fg = down_masked(raw_accueil, ~key_magenta(raw_accueil))
    are_768, are_fg = down_masked(raw_arene, ~key_magenta(raw_arene))
    rel_768, rel_fg = down_masked(raw_reliques, ~key_magenta(raw_reliques))

    # Unification des dômes sculptés des braseros + dégagement des allées vers les 2 portes de l'accueil
    acc_768 = graft_brazier_domes(acc_768, (126, 136), [(298, 136, False), (385, 138, True), (470, 136, True)])
    acc_768 = clear_doorway_sand_walkways(acc_768, sol_768, [212, 556])
    acc_open_768, door_states_raw = build_sliding_door_layers_and_open_bg(acc_768, [212, 556])

    rel_768 = graft_brazier_domes(rel_768, (126, 136), [(294, 136, False), (474, 136, True)])

    # Palette commune 96 couleurs partagée par TOUTES les salles du Dojo Kingambit (cohérence totale)
    terrain_pool = []
    accent_pool = []
    for arr, fg in [(acc_768, acc_fg), (acc_open_768, acc_fg), (are_768, are_fg), (rel_768, rel_fg)]:
        r, g, b = arr.transpose(2, 0, 1).astype(float)
        acc_m = fg & (
            ((g > r + 6) & (b >= r - 6) & (b < 148))
            | ((b > r * 1.35) & (b > 125))
            | ((r > 165) & (r > g * 1.2) & (g > b * 1.3))
            | ((g > r + 5) & (g > b + 14))
        )
        terrain_pool.append(arr[fg & ~acc_m])
        accent_pool.append(arr[acc_m])
    terrain_pool.append(sol_768[acc_fg])

    pal, pal_im = make_shared_96_palette(
        np.concatenate(terrain_pool, axis=0),
        np.concatenate(accent_pool, axis=0),
    )

    q_sol_acc = apply_palette(sol_768, acc_fg, pal, pal_im)
    q_acc_closed = apply_palette(acc_768, acc_fg, pal, pal_im)
    q_acc_open = apply_palette(acc_open_768, acc_fg, pal, pal_im)
    q_door_states = {
        cx: [apply_palette_rgba(st, pal, pal_im) for st in states]
        for cx, states in door_states_raw.items()
    }

    q_sol_are = apply_palette(sol_768, are_fg, pal, pal_im)
    q_are = apply_palette(are_768, are_fg, pal, pal_im)

    q_sol_rel = apply_palette(sol_768, rel_fg, pal, pal_im)
    q_rel = apply_palette(rel_768, rel_fg, pal, pal_im)

    # Contrôles bloquants `fidelity()` < 35 sur chacune des trois salles
    fid_acc = check_fidelity(q_acc_closed, acc_fg, ("sol_sable", "paroi_roche", "porte_sarcelle", "cristal_cyan", "rune_orange"))
    fid_are = check_fidelity(q_are, are_fg, ("sol_sable", "paroi_roche", "cristal_cyan", "rune_orange"))
    fid_rel = check_fidelity(q_rel, rel_fg, ("sol_sable", "paroi_roche", "porte_sarcelle", "cristal_cyan", "rune_orange"))

    yy, xx = np.mgrid[:H, :W]

    # =========================================================================
    # 1. SALLE D'ACCUEIL : `dojo_kingambit` (15 calques dont portes coulissantes)
    # =========================================================================
    acc_seal = (((xx - 384.0) / 70.0) ** 2 + ((yy - 268.0) / 72.0) ** 2) <= 1.0
    acc_masks = partition_room_layers(
        q_acc_open,
        acc_fg,
        brazier_centers=[(126, 136), (298, 136), (385, 138), (470, 136), (643, 136)],
        crystal_boxes=[(306, 205, 335, 249), (433, 205, 462, 249)],
        extra_bloc_boxes=[(168, 316, 204, 362), (242, 360, 278, 408), (542, 358, 578, 408)],
        floor_seal_mask=acc_seal,
    )
    acc_layer_specs = [
        ("00 sol complet", [rgba_from(q_sol_acc, acc_fg)], STATIC_TICKS, 0, True),
        ("01 sol", [rgba_from(q_acc_open, acc_masks["sol"])], STATIC_TICKS, 0, True),
        ("02 ombres", [rgba_from(q_acc_open, acc_masks["ombres"])], STATIC_TICKS, 0, True),
        ("03 parois", [rgba_from(q_acc_open, acc_masks["parois"])], STATIC_TICKS, 0, True),
        ("04 blocs", [rgba_from(q_acc_open, acc_masks["blocs"])], STATIC_TICKS, 0, True),
        (
            "05 flammes braseros 12 phases",
            build_brazier_flame_frames(
                [(126, 135, 0, False), (298, 136, 5, False), (385, 138, 9, False), (470, 136, 3, True), (643, 135, 7, True)]
            ),
            ANIM_TICKS,
            0,
            True,
        ),
        ("06 reflets cristaux 12 phases", build_crystal_glint_frames(q_acc_open, acc_fg, [(320, 213), (447, 213)]), ANIM_TICKS, 0, True),
        ("07 lueur sceau 12 phases", build_rune_pulse_frames(q_acc_open, acc_fg), ANIM_TICKS, 0, True),
        ("08 porte gauche fermee", [q_door_states[212][0]], STATIC_TICKS, 0, True),
        ("09 porte gauche coulisse 1", [q_door_states[212][1]], STATIC_TICKS, 0, False),
        ("10 porte gauche coulisse 2", [q_door_states[212][2]], STATIC_TICKS, 0, False),
        ("11 porte droite fermee", [q_door_states[556][0]], STATIC_TICKS, 0, True),
        ("12 porte droite coulisse 1", [q_door_states[556][1]], STATIC_TICKS, 0, False),
        ("13 porte droite coulisse 2", [q_door_states[556][2]], STATIC_TICKS, 0, False),
        ("14 Vos elements avant-plan (Top)", [rgba_from(q_acc_open, acc_masks["top"])], STATIC_TICKS, 4, True),
    ]
    assert len(acc_layer_specs) == 15
    assert_zero_magenta([(n, fs) for n, fs, _, _, _ in acc_layer_specs])

    bank_acc = TileBank("Kingambit_Dojo_Interieur")
    acc_layers_json = [
        make_layer(n, fs, t, bank_acc, draw_layer=dl, visible=vis)
        for n, fs, t, dl, vis in acc_layer_specs
    ]
    bank_acc.write(TILE_DIR / "Kingambit_Dojo_Interieur.tile")

    # Obstacles accueil : allées dégagées jusqu'au seuil des deux portes (x=192..232 et x=536..576, y=148)
    acc_walk = poly_mask([
        (192, 148), (232, 148), (232, 194),
        (276, 194), (276, 160), (492, 160), (492, 194),
        (536, 194), (536, 148), (576, 148), (576, 194),
        (636, 194), (658, 208), (658, 340),
        (598, 418), (438, 440), (424, 448), (424, 576),
        (344, 576), (344, 448), (330, 440), (170, 418),
        (110, 340), (110, 208), (132, 194), (192, 194),
    ])
    acc_blk = ~acc_walk
    acc_blk |= (xx >= 308) & (xx < 336) & (yy >= 212) & (yy < 248)
    acc_blk |= (xx >= 436) & (xx < 464) & (yy >= 212) & (yy < 248)
    acc_blk |= (xx >= 168) & (xx < 204) & (yy >= 320) & (yy < 360)
    acc_blk |= (xx >= 196) & (xx < 232) & (yy >= 328) & (yy < 408)
    acc_blk |= (xx >= 196) & (xx < 276) & (yy >= 364) & (yy < 408)
    acc_blk |= (xx >= 540) & (xx < 576) & (yy >= 328) & (yy < 408)
    acc_blk |= (xx >= 512) & (xx < 576) & (yy >= 352) & (yy < 408)
    acc_obs = (~((~acc_blk).reshape(GH, 8, GW, 8).mean(axis=(1, 3)) >= 0.75)).astype(np.int32)
    verify_navigation(
        acc_obs,
        (376, 504),
        [
            ("Left Door threshold", (208, 152)),
            ("Left Door return marker", (208, 168)),
            ("Right Door threshold", (544, 152)),
            ("Right Door return marker", (544, 168)),
            ("Master Kaito front", (376, 208)),
            ("Central Rune Seal", (376, 256)),
        ],
    )

    doc_acc = json.loads(json.dumps(base_template))
    obj_acc = doc_acc["Object"]
    ent_acc = obj_acc["Entities"][0]
    kaito = ent_acc["MapChars"][0]
    kaito["Direction"] = 0
    kaito["serializationDir"] = 0
    kaito["serializationLoc"] = {"X": 376, "Y": 184}
    kaito["Collider"] = {"X": 376, "Y": 184, "Width": 16, "Height": 16}

    ent_acc["GroundObjects"] = [
        make_trigger_obj(tpl_gobj, "MarowakDojoExit", 4, 2, 352, 560, 64, 8),
        make_trigger_obj(tpl_gobj, "MarowakDojoDungeonEntrance", 0, 2, 188, 144, 48, 8),
        make_trigger_obj(tpl_gobj, "KingambitDojoNorthDoorRight", 0, 2, 532, 144, 48, 8),
    ]
    ent_acc["Spawners"] = json.loads(json.dumps(tpl_spawners))
    for sp, sx in zip(ent_acc["Spawners"], (352, 400)):
        sp["Direction"] = 4
        sp["Collider"] = {"X": sx, "Y": 504, "Width": 16, "Height": 16}
    ent_acc["Markers"] = [
        make_marker_obj("MarowakDojoDungeonEntranceMarker", 0, 204, 168),
        make_marker_obj("KingambitDojoNorthDoorRightMarker", 0, 548, 168),
        make_marker_obj("MarowakDojoExitMarker", 4, 376, 504),
    ]
    obj_acc["TexSize"] = 1
    obj_acc["EdgeView"] = 1
    obj_acc["AssetName"] = "dojo_kingambit"
    obj_acc["Background"] = {"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []}
    obj_acc["BlankBG"] = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}
    obj_acc["Layers"] = acc_layers_json
    obj_acc["obstacles"] = [
        [{"Bounds": {"X": x * 8, "Y": y * 8, "Width": 8, "Height": 8}, "Tags": int(acc_obs[y, x])} for y in range(GH)]
        for x in range(GW)
    ]
    doc_acc["Version"] = "0.8.12.0"
    (GROUND_DIR / "dojo_kingambit.rsground").write_text(json.dumps(doc_acc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # =========================================================================
    # 2. ARÈNE DE COMBAT : `dojo_kingambit_arene` (9 calques)
    # =========================================================================
    are_ring = (((xx - 384.0) / 120.0) ** 2 + ((yy - 282.0) / 112.0) ** 2) <= 1.0
    are_masks = partition_room_layers(
        q_are,
        are_fg,
        brazier_centers=[(126, 134), (200, 133), (296, 134), (472, 134), (568, 133), (642, 134)],
        crystal_boxes=[(232, 110, 258, 154), (510, 110, 538, 154)],
        extra_bloc_boxes=[(326, 96, 442, 166)],
        floor_seal_mask=are_ring,
    )
    are_layer_specs = [
        ("00 sol complet", [rgba_from(q_sol_are, are_fg)], STATIC_TICKS, 0, True),
        ("01 sol", [rgba_from(q_are, are_masks["sol"])], STATIC_TICKS, 0, True),
        ("02 ombres", [rgba_from(q_are, are_masks["ombres"])], STATIC_TICKS, 0, True),
        ("03 parois", [rgba_from(q_are, are_masks["parois"])], STATIC_TICKS, 0, True),
        ("04 blocs", [rgba_from(q_are, are_masks["blocs"])], STATIC_TICKS, 0, True),
        (
            "05 flammes braseros 12 phases",
            build_brazier_flame_frames(
                [
                    (126, 134, 0, False),
                    (200, 133, 4, False),
                    (296, 134, 8, False),
                    (472, 134, 2, True),
                    (568, 133, 6, True),
                    (642, 134, 10, True),
                ]
            ),
            ANIM_TICKS,
            0,
            True,
        ),
        ("06 reflets cristaux 12 phases", build_crystal_glint_frames(q_are, are_fg, [(244, 118), (524, 118)]), ANIM_TICKS, 0, True),
        ("07 lueur sceau 12 phases", build_rune_pulse_frames(q_are, are_fg), ANIM_TICKS, 0, True),
        ("08 Vos elements avant-plan (Top)", [rgba_from(q_are, are_masks["top"])], STATIC_TICKS, 4, True),
    ]
    assert len(are_layer_specs) == 9
    assert_zero_magenta([(n, fs) for n, fs, _, _, _ in are_layer_specs])

    bank_are = TileBank("Kingambit_Dojo_Arene")
    are_layers_json = [
        make_layer(n, fs, t, bank_are, draw_layer=dl, visible=vis)
        for n, fs, t, dl, vis in are_layer_specs
    ]
    bank_are.write(TILE_DIR / "Kingambit_Dojo_Arene.tile")

    are_walk = poly_mask([
        (144, 160), (328, 160), (328, 168), (440, 168), (440, 160), (624, 160),
        (658, 198), (658, 340), (598, 418), (438, 440),
        (424, 448), (424, 576), (344, 576), (344, 448),
        (330, 440), (170, 418), (110, 340), (110, 198),
    ])
    are_obs = (~(are_walk.reshape(GH, 8, GW, 8).mean(axis=(1, 3)) >= 0.75)).astype(np.int32)
    verify_navigation(
        are_obs,
        (376, 504),
        [
            ("Arena Center", (376, 280)),
            ("Challenger West", (288, 272)),
            ("Challenger East", (464, 272)),
            ("Referee Dais Front", (376, 176)),
        ],
    )

    doc_are = json.loads(json.dumps(base_template))
    obj_are = doc_are["Object"]
    obj_are["Name"] = {"DefaultText": "Kingambit Dojo - Combat Arena", "LocalTexts": {"fr": "Dojo Kingambit - Arène de combat"}}
    obj_are["AssetName"] = "dojo_kingambit_arene"
    obj_are["TexSize"] = 1
    obj_are["EdgeView"] = 1
    obj_are["Background"] = {"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []}
    obj_are["BlankBG"] = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}
    obj_are["Layers"] = are_layers_json
    obj_are["obstacles"] = [
        [{"Bounds": {"X": x * 8, "Y": y * 8, "Width": 8, "Height": 8}, "Tags": int(are_obs[y, x])} for y in range(GH)]
        for x in range(GW)
    ]
    ent_are = obj_are["Entities"][0]
    ent_are["MapChars"] = []
    ent_are["GroundObjects"] = [
        make_trigger_obj(tpl_gobj, "SortieArene", 4, 2, 352, 560, 64, 8),
        make_trigger_obj(tpl_gobj, "EstradeArbitre", 0, 1, 336, 136, 96, 28),
    ]
    ent_are["Spawners"] = json.loads(json.dumps(tpl_spawners))
    for sp, sx in zip(ent_are["Spawners"], (352, 400)):
        sp["Direction"] = 4
        sp["Collider"] = {"X": sx, "Y": 504, "Width": 16, "Height": 16}
    ent_are["Markers"] = [
        make_marker_obj("entree_sud", 4, 376, 504),
        make_marker_obj("combattant_ouest", 6, 288, 276),
        make_marker_obj("combattant_est", 2, 464, 276),
        make_marker_obj("arbitre_nord", 0, 376, 176),
    ]
    doc_are["Version"] = "0.8.12.0"
    (GROUND_DIR / "dojo_kingambit_arene.rsground").write_text(json.dumps(doc_are, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # =========================================================================
    # 3. SALLE DES RELIQUES ET ARCHIVES : `dojo_kingambit_reliques` (9 calques)
    # =========================================================================
    rel_seal = (((xx - 384.0) / 70.0) ** 2 + ((yy - 268.0) / 72.0) ** 2) <= 1.0
    rel_masks = partition_room_layers(
        q_rel,
        rel_fg,
        brazier_centers=[(126, 135), (294, 136), (474, 136), (642, 135)],
        crystal_boxes=[(162, 108, 190, 152), (235, 108, 262, 152), (506, 108, 534, 152), (578, 108, 606, 152)],
        extra_bloc_boxes=[
            (326, 86, 442, 174),
            (176, 188, 274, 270),
            (494, 188, 594, 270),
            (176, 330, 274, 406),
            (494, 330, 594, 406),
            (102, 212, 142, 316),
            (626, 212, 666, 316),
        ],
        floor_seal_mask=rel_seal,
    )
    rel_layer_specs = [
        ("00 sol complet", [rgba_from(q_sol_rel, rel_fg)], STATIC_TICKS, 0, True),
        ("01 sol", [rgba_from(q_rel, rel_masks["sol"])], STATIC_TICKS, 0, True),
        ("02 ombres", [rgba_from(q_rel, rel_masks["ombres"])], STATIC_TICKS, 0, True),
        ("03 parois", [rgba_from(q_rel, rel_masks["parois"])], STATIC_TICKS, 0, True),
        ("04 blocs", [rgba_from(q_rel, rel_masks["blocs"])], STATIC_TICKS, 0, True),
        (
            "05 flammes braseros 12 phases",
            build_brazier_flame_frames(
                [(126, 135, 0, False), (294, 136, 5, False), (474, 136, 2, True), (642, 135, 8, True)]
            ),
            ANIM_TICKS,
            0,
            True,
        ),
        (
            "06 reflets cristaux 12 phases",
            build_crystal_glint_frames(q_rel, rel_fg, [(175, 117), (248, 117), (520, 117), (592, 116)]),
            ANIM_TICKS,
            0,
            True,
        ),
        ("07 lueur sceau 12 phases", build_rune_pulse_frames(q_rel, rel_fg), ANIM_TICKS, 0, True),
        ("08 Vos elements avant-plan (Top)", [rgba_from(q_rel, rel_masks["top"])], STATIC_TICKS, 4, True),
    ]
    assert len(rel_layer_specs) == 9
    assert_zero_magenta([(n, fs) for n, fs, _, _, _ in rel_layer_specs])

    bank_rel = TileBank("Kingambit_Dojo_Reliques")
    rel_layers_json = [
        make_layer(n, fs, t, bank_rel, draw_layer=dl, visible=vis)
        for n, fs, t, dl, vis in rel_layer_specs
    ]
    bank_rel.write(TILE_DIR / "Kingambit_Dojo_Reliques.tile")

    rel_walk = poly_mask([
        (280, 160), (328, 160), (328, 176), (440, 176), (440, 160), (488, 160),
        (488, 188), (636, 188), (658, 206), (658, 340),
        (598, 418), (438, 440), (424, 448), (424, 576),
        (344, 576), (344, 448), (330, 440), (170, 418),
        (110, 340), (110, 206), (132, 188), (280, 188),
    ])
    rel_blk = ~rel_walk
    # Collisions des 4 socles de reliques/archives et des 2 stèles latérales
    rel_blk |= (xx >= 176) & (xx < 272) & (yy >= 196) & (yy < 268)
    rel_blk |= (xx >= 496) & (xx < 592) & (yy >= 196) & (yy < 268)
    rel_blk |= (xx >= 176) & (xx < 272) & (yy >= 336) & (yy < 404)
    rel_blk |= (xx >= 496) & (xx < 592) & (yy >= 336) & (yy < 404)
    rel_blk |= (xx >= 104) & (xx < 144) & (yy >= 216) & (yy < 312)
    rel_blk |= (xx >= 624) & (xx < 664) & (yy >= 216) & (yy < 312)
    rel_obs = (~((~rel_blk).reshape(GH, 8, GW, 8).mean(axis=(1, 3)) >= 0.75)).astype(np.int32)
    verify_navigation(
        rel_obs,
        (376, 504),
        [
            ("North Rune Monument front", (376, 184)),
            ("Central Seal", (376, 256)),
            ("NW Relic Chest aisle", (216, 280)),
            ("NE Ancient Scroll aisle", (536, 280)),
            ("West Stele front", (152, 264)),
            ("East Stele front", (600, 264)),
        ],
    )

    doc_rel = json.loads(json.dumps(base_template))
    obj_rel = doc_rel["Object"]
    obj_rel["Name"] = {"DefaultText": "Kingambit Dojo - Relics & Archives", "LocalTexts": {"fr": "Dojo Kingambit - Salle des reliques et archives"}}
    obj_rel["AssetName"] = "dojo_kingambit_reliques"
    obj_rel["TexSize"] = 1
    obj_rel["EdgeView"] = 1
    obj_rel["Background"] = {"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []}
    obj_rel["BlankBG"] = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}
    obj_rel["Layers"] = rel_layers_json
    obj_rel["obstacles"] = [
        [{"Bounds": {"X": x * 8, "Y": y * 8, "Width": 8, "Height": 8}, "Tags": int(rel_obs[y, x])} for y in range(GH)]
        for x in range(GW)
    ]
    ent_rel = obj_rel["Entities"][0]
    ent_rel["MapChars"] = []
    ent_rel["GroundObjects"] = [
        make_trigger_obj(tpl_gobj, "SortieReliques", 4, 2, 352, 560, 64, 8),
        make_trigger_obj(tpl_gobj, "MonumentRunesNord", 0, 1, 332, 140, 104, 32),
        make_trigger_obj(tpl_gobj, "CoffreReliqueNO", 0, 1, 176, 196, 96, 72),
        make_trigger_obj(tpl_gobj, "ParcheminAncienNE", 0, 1, 496, 196, 96, 72),
        make_trigger_obj(tpl_gobj, "CoffreReliqueSO", 0, 1, 176, 336, 96, 68),
        make_trigger_obj(tpl_gobj, "CoffreReliqueSE", 0, 1, 496, 336, 96, 68),
        make_trigger_obj(tpl_gobj, "SteleArchiveOuest", 6, 1, 104, 216, 40, 96),
        make_trigger_obj(tpl_gobj, "SteleArchiveEst", 2, 1, 624, 216, 40, 96),
    ]
    ent_rel["Spawners"] = json.loads(json.dumps(tpl_spawners))
    for sp, sx in zip(ent_rel["Spawners"], (352, 400)):
        sp["Direction"] = 4
        sp["Collider"] = {"X": sx, "Y": 504, "Width": 16, "Height": 16}
    ent_rel["Markers"] = [
        make_marker_obj("entree_sud", 4, 376, 504),
        make_marker_obj("centre_sceau", 4, 376, 256),
    ]
    doc_rel["Version"] = "0.8.12.0"
    (GROUND_DIR / "dojo_kingambit_reliques.rsground").write_text(json.dumps(doc_rel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # =========================================================================
    # 4. DÉCLARATION DE ZONE `dojo_kingambit_salles` + `Data/Zone/index.idx`
    # =========================================================================
    zone_doc = {
        "Version": "0.8.12.0",
        "Object": {
            "$type": "RogueEssence.Data.ZoneData, RogueEssence",
            "Name": {
                "DefaultText": "Kingambit Dojo Chambers",
                "LocalTexts": {"fr": "Salles intérieures du Dojo Kingambit"},
            },
            "Released": True,
            "Comment": "Arène de combat et salle des reliques/archives raccordées aux deux portes coulissantes nord de dojo_kingambit.",
            "NoEXP": False,
            "ExpPercent": 100,
            "Level": -1,
            "LevelCap": False,
            "KeepSkills": False,
            "TeamRestrict": False,
            "TeamSize": -1,
            "MoneyRestrict": False,
            "BagRestrict": -1,
            "KeepTreasure": False,
            "BagSize": -1,
            "Persistent": False,
            "Rescues": 0,
            "Rogue": 0,
            "Segments": [],
            "GroundMaps": ["dojo_kingambit_arene", "dojo_kingambit_reliques"],
        },
    }
    (ZONE_DIR / "dojo_kingambit_salles.json").write_text(
        json.dumps(zone_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    zidx_path = ZONE_DIR / "index.idx"
    zidx = json.loads(zidx_path.read_text(encoding="utf-8-sig"))
    zidx["Object"]["dojo_kingambit_salles"] = {
        "$type": "RogueEssence.Data.ZoneEntrySummary, RogueEssence",
        "ExpPercent": 100,
        "Level": -1,
        "LevelCap": False,
        "KeepSkills": False,
        "TeamRestrict": False,
        "TeamSize": -1,
        "MoneyRestrict": False,
        "BagRestrict": -1,
        "KeepTreasure": False,
        "BagSize": -1,
        "Rescues": 0,
        "CountedFloors": 0,
        "Rogue": 0,
        "Grounds": ["dojo_kingambit_arene", "dojo_kingambit_reliques"],
        "Maps": [],
        "Name": {
            "DefaultText": "Kingambit Dojo Chambers",
            "LocalTexts": {"fr": "Salles intérieures du Dojo Kingambit"},
        },
        "Released": True,
        "Comment": "Arène de combat et salle des reliques/archives raccordées aux deux portes coulissantes nord de dojo_kingambit.",
        "SortOrder": 28,
    }
    zidx_path.write_text(json.dumps(zidx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "method": "METHODE_MAGENTA_ET_GENERATEUR.md (projet-creation-pmdo)",
        "size_px": [W, H],
        "palette_colors": 96,
        "rooms": {
            "dojo_kingambit": {
                "layers": len(acc_layers_json),
                "unique_tiles": len(bank_acc.data),
                "frame_refs": count_frame_refs(acc_layers_json),
                "fidelity": fid_acc,
            },
            "dojo_kingambit_arene": {
                "layers": len(are_layers_json),
                "unique_tiles": len(bank_are.data),
                "frame_refs": count_frame_refs(are_layers_json),
                "fidelity": fid_are,
            },
            "dojo_kingambit_reliques": {
                "layers": len(rel_layers_json),
                "unique_tiles": len(bank_rel.data),
                "frame_refs": count_frame_refs(rel_layers_json),
                "fidelity": fid_rel,
            },
        },
        "sha256": {
            "ref_canon_magenta.png": sha256(ART / "ref_canon_magenta.png"),
            "decor_magenta.png": sha256(RAW / "decor_magenta.png"),
            "arene_decor_magenta.png": sha256(RAW / "arene_decor_magenta.png"),
            "reliques_decor_magenta.png": sha256(RAW / "reliques_decor_magenta.png"),
            "sol_complet.png": sha256(RAW / "sol_complet.png"),
            "Kingambit_Dojo_Interieur.tile": sha256(TILE_DIR / "Kingambit_Dojo_Interieur.tile"),
            "Kingambit_Dojo_Arene.tile": sha256(TILE_DIR / "Kingambit_Dojo_Arene.tile"),
            "Kingambit_Dojo_Reliques.tile": sha256(TILE_DIR / "Kingambit_Dojo_Reliques.tile"),
        },
    }
    (ART / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_all()
