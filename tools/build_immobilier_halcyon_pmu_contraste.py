#!/usr/bin/env python3
"""
Construit la banque complète `Destiny_Guilde_Immobilier` (.tile + objets .dir individuels prêts à poser en jeu) :
  1. Reprend fidèlement les textures et designs Pixel-Art 1x des immobiliers de Halcyon (`Content/Tile/Guild_*_Objects*`,
     `Content/Object/*.dir`) et de la banque PMU (`PMU_08_partie_03/04/05`).
  2. Adapte les couleurs pour un CONTRASTE franc et harmonieux sur le parquet et les murs chêne-miel de notre Guilde :
     - Bois des tableaux de quêtes, comptoirs, tonneaux et caisses virés vers le noyer torréfié / acajou profond
       (au lieu du jaune-orangé qui se confondait avec le chêne-miel).
     - Tapis en teintes profondes et riches (émeraude forêt, saphir royal, rubis cramoisi, améthyste, turquoise, corail, ivoire).
     - Tous les drapeaux suspendus de style Halcyon déclinés chacun dans une COULEUR DIFFÉRENTE (10 couleurs distinctes
       avec motif Œuf Ailé + variantes sans œuf pour `missions`).
     - Tableaux de quêtes fidèles aux panneaux PMU (à toit de bardeaux, à double poteau, à lierre, fléché) + cadre mural Halcyon,
       adaptés en bois noyer foncé contrastant + parchemins crème lumineux.
  3. Génère pour chaque sprite une ombre portée chaude translucide adaptée à notre Guilde (`rgba(36, 16, 6, alpha)`),
     sans aucun pixel noir `#000000` ni magenta.
"""
from __future__ import annotations

import colorsys
import io
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = Path("/var/tmp/PMDO-Destiny")
PMU_TILE_DIR = REPO / "game/Content/Tile"
OBJ_OUT_DIR = REPO / "game/Content/Object"
HAL_DIR = Path("/tmp/Halcyon")
OUT_DIR = Path("/home/user/guilde_destiny_reseau/immobilier_guilde")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SH_R, SH_G, SH_B = 36, 16, 6


def decode_tile_sheet_dict(path: Path) -> tuple[int, dict[tuple[int, int], Image.Image]]:
    raw = path.read_bytes()
    tsize, count = struct.unpack_from("<ii", raw, 0)
    entries = [struct.unpack_from("<iiq", raw, 8 + i * 16) for i in range(count)]
    d = {}
    for tx, ty, toff in entries:
        plen = struct.unpack_from("<q", raw, toff)[0]
        im = Image.open(io.BytesIO(raw[toff + 8 : toff + 8 + plen])).convert("RGBA")
        arr = np.array(im, dtype=np.float32)
        a = arr[:, :, 3:4] / 255.0
        if a.max() == 0:
            continue
        rgb = np.where(a > 0, np.clip(arr[:, :, :3] / np.maximum(a, 1e-4), 0, 255), 0)
        d[(tx, ty)] = Image.fromarray(np.dstack([rgb.round().astype(np.uint8), arr[:, :, 3].astype(np.uint8)]), "RGBA")
    return tsize, d


def load_pmu_sheet_rgba(tile_name: str) -> np.ndarray:
    tsize, d = decode_tile_sheet_dict(PMU_TILE_DIR / f"{tile_name}.tile")
    max_x = max(tx for tx, _ in d)
    max_y = max(ty for _, ty in d)
    canvas = Image.new("RGBA", ((max_x + 1) * tsize, (max_y + 1) * tsize), (0, 0, 0, 0))
    for (tx, ty), patch in d.items():
        canvas.paste(patch, (tx * tsize, ty * tsize))
    return np.array(canvas)


_hal_cache: dict[str, tuple[int, dict] | None] = {}
def get_hal_sheet(name: str):
    if name not in _hal_cache:
        p = HAL_DIR / "Content/Tile" / f"{name}.tile"
        _hal_cache[name] = decode_tile_sheet_dict(p) if (p.exists() and p.stat().st_size >= 16) else None
    return _hal_cache[name]


def render_hal_room_objects(stem: str) -> np.ndarray:
    doc = json.loads((HAL_DIR / "Data/Ground" / f"{stem}.rsground").read_text(encoding="utf-8-sig"))
    g = doc["Object"]
    tw, th = len(g["Layers"][0]["Tiles"]), len(g["Layers"][0]["Tiles"][0])
    c = Image.new("RGBA", (tw * 8, th * 8), (0, 0, 0, 0))
    for lyr in g["Layers"]:
        if "Object" not in lyr["Name"]:
            continue
        for tx in range(tw):
            for ty in range(th):
                for sub in lyr["Tiles"][tx][ty]["Layers"]:
                    fr = sub["Frames"][0]
                    res = get_hal_sheet(fr["Sheet"])
                    if res and (fr["TexLoc"]["X"], fr["TexLoc"]["Y"]) in res[1]:
                        c.alpha_composite(res[1][(fr["TexLoc"]["X"], fr["TexLoc"]["Y"])], (tx * 8, ty * 8))
    return np.array(c)


def trim_rgba(arr: np.ndarray) -> np.ndarray:
    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return arr
    return arr[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1].copy()


def isolate_main_component(crop: np.ndarray) -> np.ndarray:
    out = crop.copy()
    r, g, b, a = out[:, :, 0].astype(int), out[:, :, 1].astype(int), out[:, :, 2].astype(int), out[:, :, 3].astype(int)
    pink_helper = (a > 0) & (r > 225) & (b > 175) & ((r - g) > 65)
    out[pink_helper] = 0
    mask = out[:, :, 3] > 0
    if not mask.any():
        return out
    lbl, n = ndimage.label(mask, structure=np.ones((3, 3), bool))
    if n > 1:
        sizes = ndimage.sum(mask, lbl, range(1, n + 1))
        out[lbl != (int(np.argmax(sizes)) + 1)] = 0
    return trim_rgba(out)


def clamp_anti_magenta(rgb: np.ndarray, alpha_mask: np.ndarray) -> np.ndarray:
    """Guarantees 0 pixel triggers `(R - G > 35) & (B - G > 25)` while preserving rich lavender/amethyst/crimson."""
    out = rgb.copy()
    bad = alpha_mask & ((out[:, :, 0] - out[:, :, 1]) > 33) & ((out[:, :, 2] - out[:, :, 1]) > 22)
    if np.any(bad):
        # Slightly lift G or lower B depending on whether R > B (crimson) or B >= R (violet/amethyst)
        is_crimson = bad & (out[:, :, 0] > out[:, :, 2] + 18)
        is_violet  = bad & (~is_crimson)
        out[:, :, 2][is_crimson] = out[:, :, 1][is_crimson] + 20.0
        out[:, :, 1][is_violet]  = np.maximum(out[:, :, 1][is_violet], out[:, :, 0][is_violet] - 31.0)
    return out


def adapt_contrast_and_shadow(
    raw_crop: np.ndarray,
    kind: str = "standing",
    wood_mode: str = "keep",  # "keep" | "dark_walnut" | "slate_walnut"
    strip_pmu_black_shadow: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Preserves 100% of the authentic Halcyon/PMU pixel-art texture & design while adapting color for
    crisp contrast against our honey-oak `#C48442` Guild interior + generating warm Destiny Guild shadow!
    """
    c = raw_crop.copy()
    r, g, b, a = c[:, :, 0].astype(int), c[:, :, 1].astype(int), c[:, :, 2].astype(int), c[:, :, 3].astype(int)
    c[(a > 0) & (r > 220) & (g < 40) & (b > 220)] = 0

    if strip_pmu_black_shadow and kind in ("standing", "banner", "hearth"):
        is_black = (c[:, :, 3] > 0) & (c[:, :, :3].max(axis=2) <= 18)
        is_color = (c[:, :, 3] > 0) & (~is_black)
        adj_color = ndimage.binary_dilation(is_color, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
        black_core = ndimage.binary_erosion(is_black, structure=np.ones((2, 2), bool))
        black_blob = ndimage.binary_dilation(black_core, iterations=2, structure=np.ones((3, 3), bool)) & is_black
        strip_sh = is_black & (
            (~adj_color)
            | (black_blob & (~ndimage.binary_dilation(is_color, structure=np.array([[0, 1, 0], [1, 1, 0], [0, 0, 0]], bool))))
        )
        c[strip_sh] = 0

    c = trim_rgba(c)
    if c.size == 0:
        z = np.zeros((8, 8, 4), dtype=np.uint8)
        return z, z

    rgb = c[:, :, :3].astype(np.float32)
    alpha = c[:, :, 3] > 110
    out_rgb = rgb.copy()

    # Warm dark-chocolate pixel-art outlines `(34, 17, 9)` instead of cold `#000000`
    max_c = rgb.max(axis=2)
    dark_out = alpha & (max_c < 34)
    t_d = max_c / 34.0
    out_rgb[dark_out, 0] = 30.0 + t_d[dark_out] * 22.0
    out_rgb[dark_out, 1] = 15.0 + t_d[dark_out] * 12.0
    out_rgb[dark_out, 2] = 8.0 + t_d[dark_out] * 7.0

    if wood_mode == "dark_walnut":
        # Shift bright yellow-orange wood planks (`R > G > B`, NOT parchment `min_c > 155`, NOT green leaves `G > R`, NOT red pins `R - G > 95`)
        # into rich contrasting Roasted Walnut / Mahogany (`#5E341A` .. `#9E6034`) so PMU boards/tables POP on honey-oak!
        min_c = rgb.min(axis=2)
        is_orange_wood = (
            alpha
            & (~dark_out)
            & (rgb[:, :, 0] > rgb[:, :, 1] + 14)
            & (rgb[:, :, 1] > rgb[:, :, 2] + 12)
            & ((rgb[:, :, 0] - rgb[:, :, 1]) < 105)
            & (min_c < 155)
        )
        out_rgb[is_orange_wood, 0] = np.clip(rgb[is_orange_wood, 0] * 0.64 + 10.0, 42, 178)
        out_rgb[is_orange_wood, 1] = np.clip(rgb[is_orange_wood, 1] * 0.56 + 6.0,  24, 112)
        out_rgb[is_orange_wood, 2] = np.clip(rgb[is_orange_wood, 2] * 0.52 + 6.0,  12, 64)
    elif wood_mode == "slate_walnut":
        # Shift Halcyon's cool grey-purple stone counter toward rich dark slate-jade / roasted walnut while keeping the gold bell!
        is_grey = alpha & (~dark_out) & ((rgb.max(axis=2) - rgb.min(axis=2)) < 38)
        out_rgb[is_grey, 0] = np.clip(rgb[is_grey, 0] * 0.72 + 12.0, 38, 165)
        out_rgb[is_grey, 1] = np.clip(rgb[is_grey, 1] * 0.68 + 8.0,  32, 145)
        out_rgb[is_grey, 2] = np.clip(rgb[is_grey, 2] * 0.56 + 4.0,  22, 115)

    out_rgb = clamp_anti_magenta(out_rgb, alpha)

    oh, ow = c.shape[:2]
    pad_l, pad_t = 2, 2
    H = (((oh + pad_t + 6) + 7) // 8) * 8
    W = (((ow + pad_l + 6) + 7) // 8) * 8

    obj_canvas = np.zeros((H, W, 4), dtype=np.uint8)
    obj_patch = np.zeros((oh, ow, 4), dtype=np.uint8)
    obj_patch[:, :, :3] = np.clip(np.round(out_rgb), 0, 255).astype(np.uint8)
    obj_patch[:, :, 3] = np.where(alpha, 255, 0).astype(np.uint8)
    obj_canvas[pad_t : pad_t + oh, pad_l : pad_l + ow] = obj_patch

    # Custom warm Destiny Guild drop-shadow (`rgba(36, 16, 6, alpha)`)
    shd_alpha = np.zeros((H, W), dtype=np.float32)
    occ = obj_canvas[:, :, 3] > 0

    if kind == "rug":
        s1 = np.zeros_like(occ)
        s2 = np.zeros_like(occ)
        s1[1:, :] |= occ[:-1, :]
        s1[:, 1:] |= occ[:, :-1]
        s1[1:, 1:] |= occ[:-1, :-1]
        s2[2:, 1:] |= occ[:-2, :-1]
        s2[1:, 2:] |= occ[:-1, :-2]
        shd_alpha[s2 & (~occ)] = 54.0
        shd_alpha[s1 & (~occ)] = 115.0
    elif kind == "banner":
        for dx, dy, a_val in ((1, 2, 120.0), (2, 3, 96.0), (3, 4, 54.0)):
            shifted = np.zeros_like(occ)
            shifted[dy:, dx:] = occ[: H - dy, : W - dx]
            shd_alpha[shifted & (~occ)] = np.maximum(shd_alpha[shifted & (~occ)], a_val)
    else:
        y_indices = np.where(occ)[0]
        y_min, y_max = int(y_indices.min()), int(y_indices.max())
        y_cut = y_min + int(0.40 * (y_max - y_min))
        base_occ = occ.copy()
        base_occ[:y_cut, :] = False
        for dx, dy, wgt in ((0, 1, 1.0), (1, 1, 1.0), (2, 2, 0.92), (3, 2, 0.72), (2, 3, 0.68), (-1, 1, 0.62), (0, 2, 0.78)):
            sh = np.zeros_like(occ)
            y0, y1 = max(0, -dy), min(H, H - dy)
            x0, x1 = max(0, -dx), min(W, W - dx)
            sh[y0 + dy : y1 + dy, x0 + dx : x1 + dx] = base_occ[y0:y1, x0:x1]
            shd_alpha = np.maximum(shd_alpha, sh.astype(np.float32) * 132.0 * wgt)
        shd_alpha[occ] = 0.0
        shd_alpha = np.where(shd_alpha >= 102, 130, np.where(shd_alpha >= 64, 86, np.where(shd_alpha >= 28, 46, 0))).astype(np.float32)

    shd_canvas = np.zeros((H, W, 4), dtype=np.uint8)
    ms = shd_alpha > 0
    shd_canvas[:, :, 0][ms] = SH_R
    shd_canvas[:, :, 1][ms] = SH_G
    shd_canvas[:, :, 2][ms] = SH_B
    shd_canvas[:, :, 3][ms] = shd_alpha[ms].astype(np.uint8)
    return obj_canvas, shd_canvas


# ==============================================================================
# 1. Exact Halcyon Hanging Flag (`28x89`) with Destiny Emblem + 10 Distinct Contrasting Colors!
# ==============================================================================
def build_halcyon_flag_variants(raw_flag: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray, str]]:
    """
    Takes Halcyon's exact `28x89` braided-rope & pleated cloth flag (`guild_bedroom_hallway_1`),
    cleanly restores the vertical cloth pleats over Halcyon's mascot (`y=46..74`), stamps our crisp
    Destiny Winged-Egg (or Explorer Star sans œuf) in Halcyon's exact flat woven tapestry style,
    and recolors each flag into a DIFFERENT rich contrasting color!
    """
    base = raw_flag.copy()
    # Row `y=43` has the clean pleated cloth columns `x=2..25` right above Halcyon's mascot!
    clean_pleat_row = base[43, :, :].copy()
    # Restore clean vertical pleats inside the cloth above the yellow V-chevron:
    # Notice the yellow V-chevron starts along `y_chev(x) = 71 + abs(x - 13.5)` (let's detect non-green yellow pixels `R > 180`!).
    for y in range(44, 86):
        for x in range(3, 25):
            r, g, b, a = map(int, base[y, x])
            if a == 0:
                continue
            # The bottom golden V-chevron strictly satisfies `y + abs(x - 13.5) >= 83.5` (wait: V points DOWN at x=13.5, y=88, and rises up toward x=2, y=76 and x=25, y=76 -> `y - (11.5 - abs(x - 13.5)) >= 71.5`, i.e., `y + abs(x - 13.5) >= 83`? NO: at center x=13.5 chevron starts at y=77 and ends at y=88; at edges x=3 chevron starts at y=67 and ends at y=78 -> `y - abs(x - 13.5)`! Wait: at x=13.5, `77 - 0 = 77`; at x=3, `67 - 10.5 = 56.5` -> NO! Look at V-chevron: V points DOWN, so y is LARGER at center x=13.5 and SMALLER at edges x=3,24! Thus `y + abs(x - 13.5)` is CONSTANT along a V pointing down: at `(13.5, 78)`, `78 + 0 = 78`; at `(3, 67.5)`, `67.5 + 10.5 = 78`!!)!
            is_chevron = (y + abs(x - 13.5)) >= 77.5
            if not is_chevron:
                base[y, x] = clean_pleat_row[x]

    # Define 10 distinct rich contrasting cloth palettes: `(name, target_hue_deg, sat_mult, val_mult, trim_tint)`
    flag_palettes = [
        ("halcyon_drapeau_01_emeraude",  136.0, 0.92, 0.82, "gold"),
        ("halcyon_drapeau_02_saphir",    216.0, 0.88, 0.84, "gold"),
        ("halcyon_drapeau_03_rubis",       6.0, 0.84, 0.82, "cream"),
        ("halcyon_drapeau_04_amethyste", 258.0, 0.62, 0.80, "silver"),
        ("halcyon_drapeau_05_turquoise", 178.0, 0.86, 0.80, "gold"),
        ("halcyon_drapeau_06_ambre",      26.0, 0.90, 0.76, "cream"),
        ("halcyon_drapeau_07_bordeaux",  348.0, 0.72, 0.66, "gold"),
        ("halcyon_drapeau_08_ardoise",   212.0, 0.48, 0.56, "gold"),
        ("halcyon_drapeau_09_corail",     14.0, 0.78, 0.90, "cream"),
        ("halcyon_drapeau_10_ivoire",     42.0, 0.26, 0.96, "emerald_trim"),
    ]

    def recolor_flag(tpl: np.ndarray, hue_deg: float, sat_m: float, val_m: float, trim_mode: str, motif: str) -> np.ndarray:
        arr = tpl.copy()
        # First recolor the green cloth pixels (`y >= 41`, `G > R + 20`) while keeping wooden rod/ropes (`y < 41`) intact!
        for y in range(41, arr.shape[0]):
            for x in range(arr.shape[1]):
                r, g, b, a = map(int, arr[y, x])
                if a == 0:
                    continue
                if g > r + 18 and g > 50:
                    # Convert original Halcyon green pixel's relative brightness into target rich hue!
                    _, s0, v0 = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                    nv = np.clip(v0 * val_m, 0.14, 0.96)
                    ns = np.clip(0.82 * sat_m + 0.10 * s0, 0.12, 0.95)
                    nr, ng, nb = colorsys.hsv_to_rgb(hue_deg / 360.0, ns, nv)
                    arr[y, x, :3] = [int(round(nr * 255)), int(round(ng * 255)), int(round(nb * 255))]
                elif r > 180 and g > 170:
                    # Chevron V-tip highlight
                    if trim_mode == "silver":
                        arr[y, x, :3] = [232, 238, 246] if r > 245 else [194, 204, 220]
                    elif trim_mode == "cream":
                        arr[y, x, :3] = [252, 238, 184] if r > 245 else [224, 196, 122]
                    elif trim_mode == "emerald_trim":
                        arr[y, x, :3] = [72, 148, 84] if r > 245 else [48, 108, 58]

        # Now stamp the woven emblem centered at `(cx=14, cy=58)` in Halcyon's exact flat two-tone tapestry style!
        cx, cy = 14, 57
        # Compute darker-woven shade of this flag's cloth + golden/trim center!
        sample_rgb = arr[44, 14, :3].astype(np.float32)
        wing_col = np.clip(sample_rgb * 0.62, 18, 210).astype(np.uint8)
        if trim_mode == "emerald_trim":
            wing_col = np.array([52, 112, 62], dtype=np.uint8)
            egg_hi, egg_mid = np.array([238, 190, 84], dtype=np.uint8), np.array([198, 142, 52], dtype=np.uint8)
        elif trim_mode == "silver":
            egg_hi, egg_mid = np.array([242, 246, 252], dtype=np.uint8), np.array([198, 208, 226], dtype=np.uint8)
        else:
            egg_hi, egg_mid = np.array([250, 224, 118], dtype=np.uint8), np.array([228, 182, 72], dtype=np.uint8)

        pts_m = {}
        if motif == "egg":
            wing_rows = [(-5, 7, 9), (-4, 5, 9), (-3, 4, 8), (-2, 4, 8), (-1, 4, 7), (0, 4, 7), (1, 3, 6), (2, 3, 5)]
            for dy, x0, x1 in wing_rows:
                w_c = egg_hi if dy <= -3 else egg_mid
                for adx in range(x0, x1 + 1):
                    for sx in (cx - adx - 1, cx + adx):
                        if 4 <= sx <= 23:
                            pts_m[(sx, cy + dy)] = w_c
            for dy in range(-4, 5):
                for dx in range(-3, 3):
                    if ((dx + 0.5) / 2.9) ** 2 + (dy / 4.3) ** 2 <= 1.0:
                        pts_m[(cx + dx, cy + dy)] = egg_hi if (dx < 0 and dy <= 0) else egg_mid
        elif motif == "compass":
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    if (abs(dx) <= 1 and abs(dy) <= 5) or (abs(dy) <= 1 and abs(dx) <= 5) or (abs(dx) + abs(dy) <= 2):
                        pts_m[(cx + dx, cy + dy)] = egg_hi if (dx + dy <= 0) else egg_mid
        for (mx, my) in list(pts_m.keys()):
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if (mx + ox, my + oy) not in pts_m and 3 <= mx + ox <= 24:
                    arr[my + oy, mx + ox, :3] = wing_col
        for (mx, my), mcol in pts_m.items():
            arr[my, mx, :3] = mcol
        return arr

    out = {}
    for fname, h_deg, sm, vm, tmode in flag_palettes:
        f_arr = recolor_flag(base, h_deg, sm, vm, tmode, motif="egg")
        o_im, s_im = adapt_contrast_and_shadow(f_arr, kind="banner", strip_pmu_black_shadow=False)
        out[fname] = (o_im, s_im, "banner")

    # Also add 3 distinct-color Winged-Egg-free flags (`missions` safe per `5ff0569`!)
    for suffix, h_deg, sm, vm, tmode in (
        ("emeraude", 136.0, 0.92, 0.82, "gold"),
        ("saphir",   216.0, 0.88, 0.84, "gold"),
        ("rubis",      6.0, 0.84, 0.82, "cream"),
    ):
        f_arr = recolor_flag(base, h_deg, sm, vm, tmode, motif="compass")
        o_im, s_im = adapt_contrast_and_shadow(f_arr, kind="banner", strip_pmu_black_shadow=False)
        out[f"halcyon_drapeau_quetes_{suffix}"] = (o_im, s_im, "banner")

    return out


# ==============================================================================
# 2. Exact Halcyon Grand Greek-Key Carpet (`104x95`) with Destiny Emblem + Contrasting Editions!
# ==============================================================================
def build_halcyon_grand_rugs(raw_rug: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray, str]]:
    """
    Preserves 100% of Halcyon's `104x95` woven Greek-key border & checkered cream fringe (`guild_guildmasters_room_12`),
    clears Halcyon's mascot inside `(14..89, 14..80)`, stamps our crisp Destiny Winged-Egg (or Explorer Compass Rose
    sans œuf) in Halcyon's exact flat woven tapestry style, and produces 5 contrasting color editions!
    """
    clean = raw_rug.copy()
    # Field green in Halcyon's rug is `(78, 192, 15, 255)` inside `(y=14..80, x=14..89)`!
    clean[13:83, 13:91] = [78, 192, 15, 255]

    editions = [
        ("halcyon_tapis_embleme_emeraude",  138.0, 0.86, 0.72, "egg"),
        ("halcyon_tapis_embleme_rubis",       6.0, 0.80, 0.74, "egg"),
        ("halcyon_tapis_embleme_saphir",    216.0, 0.82, 0.76, "egg"),
        ("halcyon_tapis_embleme_amethyste", 256.0, 0.56, 0.74, "egg"),
        ("halcyon_tapis_quetes_sans_oeuf",  142.0, 0.84, 0.70, "compass"),
    ]

    out = {}
    for rname, h_deg, sm, vm, motif in editions:
        arr = clean.copy()
        # Recolor green carpet wool (`G > R + 25`) while keeping the cream/beige outer fringe (`R > 185, G > 185`) intact!
        for y in range(arr.shape[0]):
            for x in range(arr.shape[1]):
                r, g, b, a = map(int, arr[y, x])
                if a == 0:
                    continue
                if g > r + 25:
                    _, s0, v0 = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                    nv = np.clip(v0 * vm, 0.16, 0.92)
                    ns = np.clip(0.84 * sm + 0.10 * s0, 0.18, 0.94)
                    nr, ng, nb = colorsys.hsv_to_rgb(h_deg / 360.0, ns, nv)
                    arr[y, x, :3] = [int(round(nr * 255)), int(round(ng * 255)), int(round(nb * 255))]

        cx, cy = 52, 47
        field_rgb = arr[20, 20, :3].astype(np.float32)
        w_dark = np.clip(field_rgb * 0.64, 16, 200).astype(np.uint8)
        w_mid  = np.clip(field_rgb * 0.78, 22, 220).astype(np.uint8)
        gold_hi  = np.array([250, 226, 124], dtype=np.uint8)
        gold_mid = np.array([232, 188, 78], dtype=np.uint8)

        if motif == "egg":
            pts_r = {}
            wing_rows = [
                (-11, 18, 24), (-10, 15, 24), (-9, 13, 23), (-8, 11, 22), (-7, 10, 20), (-6, 9, 18),
                (-5, 10, 22), (-4, 9, 22), (-3, 9, 21), (-2, 9, 19), (-1, 9, 17),
                (0, 8, 19), (1, 8, 19), (2, 8, 17), (3, 8, 15), (4, 7, 14), (5, 7, 12),
            ]
            for dy, x0, x1 in wing_rows:
                col = gold_hi if dy in (-10, -9, -4, 0) else gold_mid
                for adx in range(x0, x1 + 1):
                    pts_r[(cx - adx, cy + dy)] = col
                    pts_r[(cx + adx - 1, cy + dy)] = col
            for dy in range(-11, 12):
                for dx in range(-8, 8):
                    if ((dx + 0.5) / 7.6) ** 2 + (dy / 11.2) ** 2 <= 1.0:
                        pts_r[(cx + dx, cy + dy)] = gold_hi if (dx <= -1 and dy <= 2) else gold_mid
            for (rx, ry) in list(pts_r.keys()):
                for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    if (rx + ox, ry + oy) not in pts_r:
                        arr[ry + oy, rx + ox, :3] = w_dark
            for (rx, ry), rcol in pts_r.items():
                arr[ry, rx, :3] = rcol
        else:
            # Grand woven Explorer Compass Rose (`missions` safe, zero egg!)
            for dy in range(-18, 19):
                for dx in range(-22, 22):
                    d_man = abs(dx) * 0.82 + abs(dy)
                    if 13.0 <= d_man <= 16.5:
                        arr[cy + dy, cx + dx, :3] = w_dark
                    elif (abs(dx) <= 3 and abs(dy) <= 17) or (abs(dy) <= 3 and abs(dx) <= 20):
                        arr[cy + dy, cx + dx, :3] = gold_hi if (dx + dy <= 0) else gold_mid
                    elif abs(dx) + abs(dy) <= 7:
                        arr[cy + dy, cx + dx, :3] = gold_hi if (dx <= 0 and dy <= 0) else w_mid

        o_im, s_im = adapt_contrast_and_shadow(arr, kind="rug", strip_pmu_black_shadow=False)
        out[rname] = (o_im, s_im, "rug")
    return out



def extract_ai_on_exact_1x_mask(ai_png_path: Path, ref_1x_rgba: np.ndarray) -> np.ndarray:
    """
    Crops the non-white bounding box of the AI-restyled reference sprite, samples it onto the exact
    `(w, h)` 1x pixel grid of `ref_1x_rgba`, and applies `ref_1x_rgba`'s exact 1x alpha mask + crisp dark outline!
    """
    ai_rgb = np.array(Image.open(ai_png_path).convert("RGB"))
    # Non-white foreground (`min(R,G,B) < 238` or `max - min > 18`)
    fg = (ai_rgb.min(axis=2) < 236) | ((ai_rgb.max(axis=2).astype(int) - ai_rgb.min(axis=2).astype(int)) > 18)
    lbl, n = ndimage.label(fg, structure=np.ones((3, 3), bool))
    if n > 1:
        sizes = ndimage.sum(fg, lbl, range(1, n + 1))
        fg = lbl == (int(np.argmax(sizes)) + 1)
    ys, xs = np.where(fg)
    crop_ai = ai_rgb[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]

    ref_trim = trim_rgba(ref_1x_rgba)
    th, tw = ref_trim.shape[:2]
    ah, aw = crop_ai.shape[:2]

    # Sample at the exact center of each 1x cell `(x + 0.5) * aw / tw` for zero blur!
    out = np.zeros((th, tw, 4), dtype=np.uint8)
    for y in range(th):
        sy = min(ah - 1, int((y + 0.5) * ah / th))
        for x in range(tw):
            if ref_trim[y, x, 3] > 110:
                sx = min(aw - 1, int((x + 0.5) * aw / tw))
                # Preserve original crisp 1px dark outline wherever `ref_trim` had dark outline (`max < 36`)!
                if int(ref_trim[y, x, :3].max()) < 36:
                    out[y, x] = [34, 17, 9, 255]
                else:
                    out[y, x, :3] = crop_ai[sy, sx]
                    out[y, x, 3] = 255
    return out

def pack_dir_object(rgba_combined: np.ndarray, out_path: Path) -> None:
    """Writes a valid single-frame PMDO `.dir` sprite (`8-byte len + premultiplied PNG + tw, th, 0, 1`)."""
    arr = rgba_combined.astype(np.float32)
    a = arr[..., 3:4] / 255.0
    arr[..., :3] = np.clip(np.round(arr[..., :3] * a), 0, 255)
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(buf, format="PNG", optimize=False)
    png_bytes = buf.getvalue()
    h, w = rgba_combined.shape[:2]
    payload = struct.pack("<q", len(png_bytes)) + png_bytes + struct.pack("<iiii", w, h, 0, 1)
    out_path.write_bytes(payload)


def main() -> None:
    s83 = load_pmu_sheet_rgba("PMU_08_partie_03")
    s84 = load_pmu_sheet_rgba("PMU_08_partie_04")
    s85 = load_pmu_sheet_rgba("PMU_08_partie_05")

    sprites: dict[str, tuple[np.ndarray, np.ndarray, str]] = {}

    # --- A. 13 Distinct-Color Halcyon-Design Hanging Guild Flags (10 Winged-Egg + 3 Quest Compass) ---
    bh_arr = render_hal_room_objects("guild_bedroom_hallway")
    lbl_bh, n_bh = ndimage.label(bh_arr[:, :, 3] > 0, structure=np.ones((3, 3), bool))
    raw_flag = None
    for cid in range(1, n_bh + 1):
        ys, xs = np.where(lbl_bh == cid)
        if (xs.max() - xs.min() + 1) == 28 and (ys.max() - ys.min() + 1) == 89:
            raw_flag = bh_arr[ys.min():ys.max()+1, xs.min():xs.max()+1].copy()
            raw_flag[lbl_bh[ys.min():ys.max()+1, xs.min():xs.max()+1] != cid] = 0
            break
    assert raw_flag is not None
    sprites.update(build_halcyon_flag_variants(raw_flag))

    # --- B. 5 Contrasting Halcyon-Design Grand Greek-Key Carpets (4 Winged-Egg + 1 Quest Compass) ---
    gm_arr = render_hal_room_objects("guild_guildmasters_room")
    lbl_gm, n_gm = ndimage.label(gm_arr[:, :, 3] > 0, structure=np.ones((3, 3), bool))
    raw_rug = None
    for cid in range(1, n_gm + 1):
        ys, xs = np.where(lbl_gm == cid)
        if (xs.max() - xs.min() + 1) == 104 and (ys.max() - ys.min() + 1) == 95:
            raw_rug = gm_arr[ys.min():ys.max()+1, xs.min():xs.max()+1].copy()
            raw_rug[lbl_gm[ys.min():ys.max()+1, xs.min():xs.max()+1] != cid] = 0
            break
    assert raw_rug is not None
    sprites.update(build_halcyon_grand_rugs(raw_rug))

    # --- C. Quest Notice Boards (PMU Standing Boards + Halcyon Wall Quest Frame) Adapted for High Contrast! ---
    def clean_scroll_banner(crop: np.ndarray) -> np.ndarray:
        c = crop.copy()
        dark = (c[:, :, 3] > 0) & (c[:, :, :3].max(axis=2) < 42)
        bright = (c[:, :, 3] > 0) & (c[:, :, 0] > 110)
        c[dark & (~ndimage.binary_dilation(bright, structure=np.ones((3, 3), bool)))] = 0
        return isolate_main_component(c)

    pmu_quest_and_rugs = [
        # Quest Notice Boards (`dark_walnut` contrast so they stand out crisply against honey-oak!)
        ("pmu_tableau_quetes_toit",    isolate_main_component(s83[3848:3904, 62:130]),  "standing", "dark_walnut"),
        ("pmu_tableau_quetes_poteaux", isolate_main_component(s83[3816:3872, 160:224]), "standing", "dark_walnut"),
        ("pmu_tableau_quetes_lierre",  isolate_main_component(s83[3876:3934, 190:256]), "standing", "dark_walnut"),
        ("pmu_panneau_fleches",        isolate_main_component(s83[3816:3872, 224:288]), "standing", "dark_walnut"),
        ("pmu_panneau_bois_double",    isolate_main_component(s83[3884:3934, 130:188]), "standing", "dark_walnut"),
        ("pmu_banniere_parchemin_1",   clean_scroll_banner(s83[3744:3814, 160:218]),    "banner",   "dark_walnut"),
        ("pmu_banniere_parchemin_2",   clean_scroll_banner(s83[3744:3814, 224:282]),    "banner",   "dark_walnut"),
        # PMU Rugs, Runners, Hearth, Banquet Table & Fur Bed
        ("pmu_tapis_bleu",             isolate_main_component(s83[3298:3388, 98:190]),  "rug",      "keep"),
        ("pmu_tapis_vert",             isolate_main_component(s83[3298:3388, 194:286]), "rug",      "keep"),
        ("pmu_tapis_jaune",            isolate_main_component(s83[3298:3388, 290:382]), "rug",      "keep"),
        ("pmu_tapis_rouge",            isolate_main_component(s83[3394:3484, 98:190]),  "rug",      "keep"),
        ("pmu_tapis_lavande",          isolate_main_component(s83[3394:3484, 194:286]), "rug",      "keep"),
        ("pmu_tapis_peche",            isolate_main_component(s83[3490:3580, 194:286]), "rug",      "keep"),
        ("pmu_paillasson_rouge",       isolate_main_component(s83[3330:3358, 36:90]),   "rug",      "keep"),
        ("pmu_paillasson_peche",       isolate_main_component(s83[3362:3390, 36:90]),   "rug",      "keep"),
        ("pmu_paillasson_bleu",        isolate_main_component(s83[3394:3422, 36:90]),   "rug",      "keep"),
        ("pmu_paillasson_vert",        isolate_main_component(s83[3458:3486, 36:90]),   "rug",      "keep"),
        ("pmu_paillasson_jaune",       isolate_main_component(s83[3490:3518, 36:90]),   "rug",      "keep"),
        ("pmu_tapis_royal_rouge",      isolate_main_component(s84[2196:2240, 96:146]),  "rug",      "keep"),
        ("pmu_tapis_rond_ambre",       isolate_main_component(s84[2108:2162, 300:356]), "rug",      "keep"),
        ("pmu_tapis_rond_sauge",       isolate_main_component(s84[2196:2250, 300:356]), "rug",      "keep"),
        ("pmu_tapis_tresse_ovale",     isolate_main_component(s85[182:232, 286:372]),   "rug",      "keep"),
        ("pmu_fourneau_cuisine",       isolate_main_component(s83[3904:3998, 4:64]),    "hearth",   "dark_walnut"),
        ("pmu_table_banquet_seule",    isolate_main_component(s83[3744:3806, 0:160]),   "standing", "keep"),
        ("pmu_lit_fourrure",           isolate_main_component(s85[248:298, 130:214]),   "standing", "keep"),
        ("pmu_table_rondin_grand",     isolate_main_component(s83[3692:3748, 270:328]), "standing", "dark_walnut"),
        ("pmu_table_rondin_moyen",     isolate_main_component(s83[3884:3934, 252:296]), "standing", "keep"),
        ("pmu_coffre_bois_bleu",       isolate_main_component(s85[480:512, 0:32]),      "standing", "keep"),
        ("pmu_coffre_bois_rouge",      isolate_main_component(s85[480:512, 64:96]),     "standing", "keep"),
        ("pmu_caisse_cordee",          isolate_main_component(s85[126:164, 88:128]),    "standing", "keep"),
        ("pmu_caisse_grise",           isolate_main_component(s84[2374:2408, 160:192]), "standing", "keep"),
        ("pmu_caisse_acajou",          isolate_main_component(s84[2374:2408, 192:224]), "standing", "keep"),
        ("pmu_buches_bois",            isolate_main_component(s83[3616:3648, 0:32]),    "standing", "dark_walnut"),
    ]
    for name, raw_c, knd, wmode in pmu_quest_and_rugs:
        sprites[name] = (*adapt_contrast_and_shadow(raw_c, kind=knd, wood_mode=wmode, strip_pmu_black_shadow=True), knd)

    # --- D. ALL Authentic Halcyon Guild Furniture, Rugs, Scroll Desk, Banquet Table, Crates, Chests & `.dir` Props ---
    # Extract every clean Halcyon sprite (excluding architectural windows `#21/#22`, stairs `#49/#50`, stone door `#69`,
    # merged flag+barrel `#57`, and raw mascot flags/rugs which we already adapted above!).
    seen_hal: set[bytes] = set()
    hal_rooms = [
        "guild_second_floor",
        "guild_third_floor_lobby",
        "guild_guildmasters_room",
        "guild_dining_room",
        "guild_storage_room",
        "guild_heros_room",
        "guild_top_left_bedroom",
        "guild_top_right_bedroom",
        "guild_bottom_left_bedroom",
        "guild_bottom_right_bedroom",
    ]
    hal_idx = 1
    for rstem in hal_rooms:
        rarr = render_hal_room_objects(rstem)
        lbl, n = ndimage.label(rarr[:, :, 3] > 0, structure=np.ones((3, 3), bool))
        for cid in range(1, n + 1):
            ys, xs = np.where(lbl == cid)
            if len(ys) < 16:
                continue
            cr = rarr[ys.min():ys.max()+1, xs.min():xs.max()+1].copy()
            cr[lbl[ys.min():ys.max()+1, xs.min():xs.max()+1] != cid] = 0
            h, w = cr.shape[:2]
            key = cr.tobytes()
            if key in seen_hal:
                continue
            seen_hal.add(key)

            # Skip architectural cutouts (round windows, stairs, stone cave doorway) & raw Bellossom flags/rugs & merged flag+barrel:
            if (w, h) in ((28, 89), (28, 81), (104, 95), (35, 111), (81, 69), (52, 59), (126, 89), (96, 65), (58, 54)):
                continue
            # Also skip small raw wall vine sprigs `(29x56)` if desired? Wait: keeping Halcyon's 2 wall ivy sprigs (`29x56`) as optional placeable decor is super handy for the user in-game!

            # Classify `kind` and `wood_mode` accurately for each Halcyon sprite!
            if (w, h) in ((72, 56), (56, 56), (56, 40), (40, 56), (128, 40), (40, 24), (72, 64), (64, 72)) and not (rstem == "guild_second_floor" and (w, h) == (56, 40)):
                knd, wmode = "rug", "keep"
                tag = f"halcyon_tapis_{hal_idx:02d}"
                # Shift neon lime-green Halcyon rugs to rich contrasting Forest Emerald!
                neon = (cr[:, :, 3] > 0) & (cr[:, :, 1].astype(int) > cr[:, :, 0].astype(int) + 55) & (cr[:, :, 2].astype(int) < 60)
                if neon.any():
                    cr[neon, 0] = np.clip((cr[neon, 0].astype(float) * 0.55 + 16), 20, 120).astype(np.uint8)
                    cr[neon, 1] = np.clip((cr[neon, 1].astype(float) * 0.68 + 8),  55, 165).astype(np.uint8)
                    cr[neon, 2] = np.clip((cr[neon, 2].astype(float) * 0.65 + 38), 32, 110).astype(np.uint8)
            elif rstem == "guild_second_floor" and (w, h) == (56, 40):
                knd, wmode = "banner", "keep"  # Already rich dark mahogany!
                tag = "halcyon_tableau_quetes_mural"
            elif (w, h) == (54, 28):
                knd, wmode = "standing", "slate_walnut"
                tag = "halcyon_comptoir_cloche"
            elif (w, h) == (177, 57):
                knd, wmode = "standing", "keep"
                tag = "halcyon_table_banquet_tapis"
            elif (w, h) == (48, 95):
                knd, wmode = "rug", "keep"
                tag = "halcyon_bureau_parchemin_maitre"
            elif (w, h) == (29, 56):
                knd, wmode = "banner", "keep"
                tag = f"halcyon_lierre_mural_{hal_idx:02d}"
            elif (w, h) in ((39, 28), (12, 12), (10, 10), (14, 14), (24, 25), (22, 24), (28, 23), (32, 24), (24, 18)):
                knd, wmode = "standing", "keep"
                tag = f"halcyon_objet_{hal_idx:02d}"
            else:
                knd, wmode = "standing", "dark_walnut"
                tag = f"halcyon_objet_{hal_idx:02d}"
            hal_idx += 1
            sprites[tag] = (*adapt_contrast_and_shadow(cr, kind=knd, wood_mode=wmode, strip_pmu_black_shadow=False), knd)

    # Also include Halcyon's standalone `.dir` objects (`Diary_*`, `Food*`, `Apricorn_Big`, `Yellow_Box`)!
    for dp in sorted((HAL_DIR / "Content/Object").glob("*.dir")):
        if any(k in dp.stem for k in ("Anima", "Core", "Night_Window", "Closed_Guild_Door")):
            continue
        raw = dp.read_bytes()
        plen = struct.unpack_from("<q", raw, 0)[0]
        im = Image.open(io.BytesIO(raw[8 : 8 + plen])).convert("RGBA")
        tw, th, _, _ = struct.unpack_from("<iiii", raw, 8 + plen)
        f0 = trim_rgba(np.array(im.crop((0, 0, tw, th))))
        if f0.size > 0:
            sprites[f"halcyon_{dp.stem.lower()}"] = (*adapt_contrast_and_shadow(f0, kind="rug", wood_mode="keep", strip_pmu_black_shadow=False), "rug")

    # --- E. 6 AI-Generated (`generate_image`) High-Contrast Dark-Mahogany/Slate Editions on Exact 1x Grids! ---
    ia_dir = OUT_DIR / "ia_bruts"
    d_tpl = np.load("/tmp/hal_tpl.npz")
    ai_specs = [
        ("ia_tableau_quetes_toit_emeraude",  ia_dir / "ia_pmu_tableau_toit_noyer.png",      isolate_main_component(s83[3848:3904, 62:130]),  "standing"),
        ("ia_tableau_quetes_poteaux_acajou", ia_dir / "ia_pmu_tableau_poteaux_noyer.png",   isolate_main_component(s83[3816:3872, 160:224]), "standing"),
        ("ia_tableau_quetes_lierre_acajou",  ia_dir / "ia_pmu_tableau_lierre_noyer.png",    isolate_main_component(s83[3876:3934, 190:256]), "standing"),
        ("ia_tableau_quetes_mural_ardoise",  ia_dir / "ia_halcyon_tableau_mural_noyer.png", d_tpl["board"],                                  "banner"),
        ("ia_comptoir_cloche_acajou",        ia_dir / "ia_halcyon_bell_desk_noyer.png",     d_tpl["desk"],                                   "standing"),
        ("ia_fourneau_brique_ardoise",       ia_dir / "ia_pmu_hearth_noyer.png",            isolate_main_component(s83[3904:3998, 4:64]),    "hearth"),
    ]
    for aname, apath, ref_1x, akind in ai_specs:
        if apath.exists():
            ai_1x = extract_ai_on_exact_1x_mask(apath, ref_1x)
            sprites[aname] = (*adapt_contrast_and_shadow(ai_1x, kind=akind, wood_mode="keep", strip_pmu_black_shadow=False), akind)

    # Pack complete Atlas (`896` px wide) & export individual `.dir` objects (`Guilde_Imm_*.dir`)!
    atlas_w = 896
    cur_x, cur_y, row_h = 8, 8, 0
    placements = {}
    for name, (obj_a, shd_a, kind) in sprites.items():
        sh, sw = obj_a.shape[:2]
        if cur_x + sw + 8 > atlas_w:
            cur_x = 8
            cur_y += row_h + 8
            row_h = 0
        placements[name] = {"x": cur_x, "y": cur_y, "w": sw, "h": sh, "kind": kind}
        cur_x += sw + 8
        row_h = max(row_h, sh)
    atlas_h = ((cur_y + row_h + 15) // 8) * 8

    atlas_obj = np.zeros((atlas_h, atlas_w, 4), dtype=np.uint8)
    atlas_shd = np.zeros((atlas_h, atlas_w, 4), dtype=np.uint8)

    # Clean any previous `Guilde_Imm_*.dir` files first
    for old_d in OBJ_OUT_DIR.glob("Guilde_Imm_*.dir"):
        old_d.unlink()

    for name, (obj_a, shd_a, _) in sprites.items():
        p = placements[name]
        x, y, w, h = p["x"], p["y"], p["w"], p["h"]
        atlas_obj[y : y + h, x : x + w] = obj_a
        atlas_shd[y : y + h, x : x + w] = shd_a

        # Combine `shd_a` + `obj_a` into a ready-to-drop `.dir` sprite for in-game placement!
        comb = Image.fromarray(shd_a, "RGBA")
        comb.alpha_composite(Image.fromarray(obj_a, "RGBA"))
        comb_trimmed = trim_rgba(np.array(comb))
        dir_name = f"Guilde_Imm_{name}.dir"
        pack_dir_object(comb_trimmed, OBJ_OUT_DIR / dir_name)
        p["dir_object"] = f"Guilde_Imm_{name}"

    Image.fromarray(atlas_obj, "RGBA").save(OUT_DIR / "Destiny_Guilde_Immobilier_Objets.png")
    Image.fromarray(atlas_shd, "RGBA").save(OUT_DIR / "Destiny_Guilde_Immobilier_Ombres.png")
    (OUT_DIR / "Destiny_Guilde_Immobilier_Manifest.json").write_text(
        json.dumps(placements, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # Render crystal-clear preview over our real honey-oak floor (`03_grand_salon_central_1x_base.png`)!
    sal_floor = Image.open("/home/user/guilde_destiny_reseau/cartes_base_sans_decors/03_grand_salon_central_1x_base.png").convert("RGB").crop((140, 180, 396, 308))
    oak_bg = Image.new("RGBA", (atlas_w, atlas_h), (186, 126, 62, 255))
    for ty in range(0, atlas_h, 128):
        for tx in range(0, atlas_w, 256):
            oak_bg.paste(sal_floor, (tx, ty))
    oak_bg.alpha_composite(Image.fromarray(atlas_shd, "RGBA"))
    oak_bg.alpha_composite(Image.fromarray(atlas_obj, "RGBA"))
    oak_bg.convert("RGB").save(OUT_DIR / "Apercu_Banque_Immobilier_Guilde_Sur_Parquet.png")
    print(f"[OK] Built {len(sprites)} Halcyon+PMU Contrast-Adapted Guild sprites ({atlas_w}x{atlas_h}) + {len(sprites)} .dir objects!")


if __name__ == "__main__":
    main()
