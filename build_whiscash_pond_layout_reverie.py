#!/usr/bin/env python3
"""Build Whiscash Pond — Grand Doyen Spacious Reverie Map (768x576, 96x72 tiles, 1x1 zero-mixel, PMDO 0.8.12).

Combines:
- Expanded 3-cascade Whiscash Pond layout inspired by /home/user/uploads/image-16.png
  scaled smoothly via class SDFs to 768x576 (96x72 PMDO 8x8 tiles, TexSize=1) with a roomier
  pond basin, spacious central paw-print clearing, wider southern path, and expansive cliffs/meadows.
- 100% pure 1:1 Reverie Town grass (Reverie_Town_Base g16), 1:1 Reverie Town cliff masonry
  (Reverie_Town_Cliffs rock32 + 11-color mauve curved side shading), and 1:1 grass-to-cliff raccords
  (lip32 horizontal crowns, scalloped diagonal grass-over-cliff rims, rounded cliff feet & cast shadows).
- Authentic Reverie Town style path (Reverie_Town_Base sand48 + scalloped terracotta border +
  1:1 crisp Whiscash paw print, clean south trail without gray pebbles).
- Deep cascade-blue pond using Reverie Town pond animation (4-frame scalloped shore waves in
  #104078/#205090/#2C5898/#3860A0/#5090C0 + 6 native 4-frame 18x18 Reverie Town pond sparkles).
- Full uncompacted 1:1 Reverie Town centerpiece platform + 4 stepping stones + 4 animated river stones
  (8 frames x 5 ticks) + Grand Doyen swim ripples preparation (Etang_Nage_Ondes).
- Three genuine postless Tiles7 PMU cascades (48px / 96px / 48px, 8 frames x 5 ticks = 96px period)
  + canonical 3-pose PMU foam animation (FrameLength = 10 ticks).

Outputs in /home/user/:
- whiscash_pond_layout_reverie_projet_pmdo_0812.zip
- whiscash_pond_layout_reverie_multicalque.ora
- whiscash_pond_layout_reverie_calques.zip
- apercu_whiscash_pond_layout_reverie_jour.png
- apercu_whiscash_pond_layout_reverie_anime.gif
- apercu_whiscash_pond_layout_reverie_4_ambiances.png
- apercu_whiscash_pond_layout_reverie_collisions_marqueurs.png
- apercu_whiscash_pond_layout_reverie.html
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
import struct
import subprocess
import sys
import urllib.request
import uuid
import xml.etree.ElementTree as ET
import zipfile
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

ROOT = Path("/home/user")
INPUT_LAYOUT = ROOT / "uploads/image-16.png"
PROJET = Path("/var/tmp/projet_creation_pmdo")
T7_PATH = Path("/var/tmp/pmu_sheets/Tiles7.png")
APC_PATH = Path("/var/tmp/halcyon_tiles/Altere_Pond_Cliffs.png")
RTB_PATH = Path("/var/tmp/halcyon_tiles/Reverie_Town_Base.png")
RTC_PATH = Path("/var/tmp/halcyon_tiles/Reverie_Town_Cliffs.png")
RTA_PATH = Path("/var/tmp/halcyon_tiles/Reverie_Town_Animation_Tileset.png")
CC_CLEAN_PATH = Path("/var/tmp/cc_clean_cliffs.png")
REVERIE_ETANG_PATH = ROOT / "PMDO-Destiny/payload/reverie_etang.rsground.gz"
REVERIE_SHEETS_DIR = ROOT / "PMDO-Destiny/art/reverie/tilesheets"
STAGE = ROOT / "whiscash_pond_layout_reverie_stage"

W, H = 768, 576           # 96 x 72 PMDO 8x8 tiles (4:3, exact 1x1 Reverie & PMU cascade scale)
GW, GH = W // 8, H // 8
NN = Image.Resampling.NEAREST

# Waterfall gorge geometry (centered at x=384, exact 8px-aligned 1:1 Tiles7 widths)
CHUTE_LAYOUT = {
    "chute_L": (192, 240, 160),   # x0, x1 (48px native t7_medL), y_foot
    "chute_C": (336, 432, 162),   # x0, x1 (96px: 92px mouth + 2px cliff bleed), y_foot
    "chute_R": (528, 576, 160),   # x0, x1 (48px native t7_medR), y_foot
}

# Timing: 120 ticks = 2.00s master cycle -> 24 display frames @ 5 ticks (~83.3ms)
N_FRAMES = 24
FRAME_DURATIONS_MS = [round((i + 1) * 2000 / N_FRAMES) - round(i * 2000 / N_FRAMES) for i in range(N_FRAMES)]

# Authentic Reverie Town Pond & Sparkle Palette (reverie_etang.rsground.gz + Reverie_Town_Base)
REVERIE_WATER_PAL = {
    "surface": np.array([128, 216, 224], dtype=np.uint8),  # #80D8E0 exact Reverie pond water
    "swell":   np.array([104, 200, 224], dtype=np.uint8),  # #68C8E0 outer shore swell
    "mid":     np.array([ 88, 176, 200], dtype=np.uint8),  # #58B0C8 mid shore wave band
    "deep":    np.array([ 80, 128, 184], dtype=np.uint8),  # #5080B8 bank rim / deep shore
    "crest":   np.array([156, 234, 246], dtype=np.uint8),  # #9CEAF6 sunlit shore crest
    "glint":   np.array([156, 234, 246], dtype=np.uint8),  # #9CEAF6 sparkle halo
    "sparkle": np.array([247, 255, 255], dtype=np.uint8),  # #F7FFFF sparkle core
}

# Authentic Reverie Town Waterfall Palette (Reverie_Geo_11_Cascades_frames.png)
REVERIE_CASCADE_RAMP = np.array([
    [ 87, 135, 191],  # #5787BF deep cascade blue
    [ 82, 145, 197],  # #5291C5 deep-mid blue
    [ 95, 151, 199],  # #5F97C7 cerulean mid
    [ 57, 165, 213],  # #39A5D5 vibrant Reverie blue
    [ 95, 183, 207],  # #5FB7CF aqua-blue stream
    [111, 207, 231],  # #6FCFE7 bright cyan flow
    [156, 234, 246],  # #9CEAF6 pale mist streak
    [247, 255, 255],  # #F7FFFF bright white spray
], dtype=np.uint8)

# Authentic Metano Town Sandy Path Palette (Metano_Town_Base.tile)
METANO_PATH_PAL = {
    "sand_main":   np.array([248, 216, 152], dtype=np.uint8),  # #F8D898 warm cream sand body
    "sand_warm":   np.array([248, 208, 144], dtype=np.uint8),  # #F8D090 subtle sand pebble
    "sand_rim":    np.array([248, 200, 128], dtype=np.uint8),  # #F8C880 warm edge sand
    "bank_mid":    np.array([240, 192, 120], dtype=np.uint8),  # #F0C078 mid bank shade
    "bank_shade":  np.array([224, 152,  96], dtype=np.uint8),  # #E09860 scalloped terracotta bank
    "grass_edge":  np.array([160, 188,  54], dtype=np.uint8),  # #A0BC36 crisp grass blade edge
    "grass_dark":  np.array([184, 208,  64], dtype=np.uint8),  # #B8D040 Metano/Reverie grass tuft
    "grass_mid":   np.array([200, 216,  80], dtype=np.uint8),  # #C8D850 base grass blend
    "grass_hi":    np.array([216, 224, 104], dtype=np.uint8),  # #D8E068 sunlit grass tooth
}

# Canyon Camp + Reverie_Town_Cliffs Crown & Masonry Palette
CANYON_RIM_PAL = {
    "outline":     np.array([165,  95,  55], dtype=np.uint8),  # #A55F37 crisp dark outline
    "crown_spec":  np.array([248, 224, 192], dtype=np.uint8),  # #F8E0C0 sunlit corner highlight
    "crown_top":   np.array([241, 202, 125], dtype=np.uint8),  # #F1CA7D bright sandstone lip
    "crown_hi":    np.array([231, 191,  94], dtype=np.uint8),  # #E7BF5E warm golden bevel
    "crown_mid":   np.array([215, 165,  76], dtype=np.uint8),  # #D7A54C amber sandstone mid
    "crown_shade": np.array([192, 132,  77], dtype=np.uint8),  # #C0844D warm bevel shadow
}

# Exact 11-color Reverie_Town_Cliffs palette & mauve curved-column remap
RTC_PAL = {
    "outline":    np.array([165,  95,  55], dtype=np.uint8),
    "amber_dark": np.array([175, 112,  70], dtype=np.uint8),
    "amber_sh":   np.array([188, 123,  65], dtype=np.uint8),
    "amber_mid":  np.array([192, 132,  77], dtype=np.uint8),
    "lit_low":    np.array([215, 165,  76], dtype=np.uint8),
    "lit_mid":    np.array([219, 169, 101], dtype=np.uint8),
    "lit_hi":     np.array([231, 191,  94], dtype=np.uint8),
    "lit_top":    np.array([241, 202, 125], dtype=np.uint8),
    "mauve_hi":   np.array([208, 151, 112], dtype=np.uint8),
    "mauve_mid":  np.array([191, 131, 111], dtype=np.uint8),
    "mauve_dark": np.array([174,  95, 101], dtype=np.uint8),
}

# Reverie Town grass cast shadow tones (clean olive steps derived from g16)
REV_GRASS_SHADOW = (
    np.array([144, 174,  48], dtype=np.uint8),
    np.array([160, 188,  54], dtype=np.uint8),
    np.array([174, 200,  58], dtype=np.uint8),
)

# Exact 8-color Tiles7 RGB555 PMU foam ramp
T7_FOAM_RAMP = np.array([
    [120, 136, 192],
    [128, 160, 200],
    [152, 176, 216],
    [176, 192, 224],
    [184, 200, 232],
    [208, 216, 232],
    [232, 232, 240],
    [240, 248, 248],
], dtype=np.uint8)

# Official PMDO-Destiny 4-ambiance LUT multipliers (GroundMap.cs: WorldAmbianceTint)
DESTINY_AMBIANCES = (
    ("jour", "Jour", "Jour", (255, 255, 255)),
    ("aube", "Aube", "Aube", (224, 203, 212)),
    ("crepuscule", "Crepuscule", "Crepuscule", (179, 146, 173)),
    ("nuit", "Nuit", "Nuit", (97, 118, 159)),
)
RERANDOM_STATE = [16294208416658607535, 7960286522194355700, 487617019471545679, 17909611376780542444]


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def keep_large(m: np.ndarray, min_area: int) -> np.ndarray:
    lab, n = nd.label(m, np.ones((3, 3)))
    if n == 0:
        return np.zeros_like(m, bool)
    counts = np.bincount(lab.ravel())
    counts[0] = 0
    return np.isin(lab, np.flatnonzero(counts >= min_area))


def _hash_noise(yy: np.ndarray, xx: np.ndarray, seed: int = 17) -> np.ndarray:
    b2y, b2x = yy // 2, xx // 2
    n1 = 0.5 + 0.5 * np.sin(xx * 0.43 + yy * 0.37 + seed * 1.1) * np.cos(xx * 0.29 - yy * 0.51 + seed)
    n2 = ((b2x * 73856093 ^ b2y * 19349663 ^ seed * 83492791) & 255) / 255.0
    n3 = ((xx * 374761393 + yy * 668265263 + seed * 1274126177) & 255) / 255.0
    return 0.40 * n1 + 0.35 * n2 + 0.25 * n3


def smooth_sdf_resize(mask: np.ndarray, out_h: int, out_w: int) -> np.ndarray:
    """Resize binary mask smoothly via signed distance field bicubic interpolation (zero stair-stepping)."""
    sdf = nd.distance_transform_edt(mask) - nd.distance_transform_edt(~mask)
    im_f = Image.fromarray(sdf.astype(np.float32), mode="F")
    return np.array(im_f.resize((out_w, out_h), Image.Resampling.BICUBIC), dtype=float)


def premultiply_rgba(im: Image.Image) -> Image.Image:
    a = np.array(im.convert("RGBA"), dtype=np.uint16)
    alpha = a[:, :, 3:4]
    a[:, :, :3] = (a[:, :, :3] * alpha + 127) // 255
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def tint_rgba_lut(arr: np.ndarray, tint: tuple[int, int, int]) -> np.ndarray:
    if tint == (255, 255, 255):
        return arr.copy()
    out = arr.copy()
    m = out[:, :, 3] > 0
    if not m.any():
        return out
    t_arr = np.array(tint, dtype=float) / 255.0
    out[m, :3] = np.clip(np.rint(out[m, :3].astype(float) * t_arr), 0, 255).astype(np.uint8)
    return out


def apply_ambiance(im: Image.Image, mode: str, night_fn=None) -> Image.Image:
    tint_map = {a: t for a, _, _, t in DESTINY_AMBIANCES}
    arr = np.array(im.convert("RGBA"))
    return Image.fromarray(tint_rgba_lut(arr, tint_map[mode]), "RGBA")


def png_bytes(im: Image.Image) -> bytes:
    b = io.BytesIO()
    im.save(b, format="PNG")
    return b.getvalue()


def data_uri(raw: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


# ------------------------------------------------------------------ 1. Smooth 768x576 Layout + 100% Pure Reverie Town Terrain
def build_mauve_cliff_block(rock32: np.ndarray) -> np.ndarray:
    """Map lit Reverie_Town_Cliffs rock32 onto the exact mauve curved-wall palette from curve_L."""
    lut = {
        (241, 202, 125): (219, 169, 101),
        (231, 191,  94): (208, 151, 112),
        (219, 169, 101): (208, 151, 112),
        (215, 165,  76): (191, 131, 111),
        (193, 133,  78): (191, 131, 111),
        (192, 132,  77): (191, 131, 111),
        (188, 123,  65): (174,  95, 101),
        (175, 112,  70): (174,  95, 101),
        (191, 131, 111): (174,  95, 101),
        (174,  95, 101): (174,  95, 101),
        (165,  95,  55): (165,  95,  55),
    }
    out = rock32.copy()
    rgb = out[:, :, :3]
    for y in range(out.shape[0]):
        for x in range(out.shape[1]):
            if out[y, x, 3] == 0:
                continue
            key = (int(rgb[y, x, 0]), int(rgb[y, x, 1]), int(rgb[y, x, 2]))
            if key in lut:
                out[y, x, :3] = lut[key]
            else:
                best_k = min(lut.keys(), key=lambda k: sum((k[c] - key[c]) ** 2 for c in range(3)))
                out[y, x, :3] = lut[best_k]
    return out


def build_canyon_camp_cliff_layer() -> np.ndarray:
    """Assemble clean, seamless 768x576 Canyon Camp cliff architecture matching image-27.png."""
    cc = np.array(Image.open(CC_CLEAN_PATH).convert("RGBA"))
    cliffs_cc = np.zeros((H, W, 4), dtype=np.uint8)

    def keep_largest(arr: np.ndarray) -> np.ndarray:
        m = arr[:, :, 3] > 0
        lab, _ = nd.label(m)
        cnt = np.bincount(lab.ravel())
        if len(cnt) <= 1:
            return arr.copy()
        best = int(np.argmax(cnt[1:]) + 1)
        out = arr.copy()
        out[lab != best] = 0
        return out

    def paste_rgba(dst: np.ndarray, src: np.ndarray, x0: int, y0: int) -> None:
        sh, sw = src.shape[:2]
        x_s, y_s = max(0, -x0), max(0, -y0)
        x_d, y_d = max(0, x0), max(0, y0)
        w_c = min(sw - x_s, W - x_d)
        h_c = min(sh - y_s, H - y_d)
        if w_c <= 0 or h_c <= 0:
            return
        sub = src[y_s : y_s + h_c, x_s : x_s + w_c]
        m = sub[:, :, 3] > 0
        dst[y_d : y_d + h_c, x_d : x_d + w_c][m] = sub[m]

    wall_raw = cc[169:261, 0:120].copy()
    crest_r = int(np.where((wall_raw[:, :, 3] > 0).mean(axis=1) > 0.75)[0].min())
    wall_src = wall_raw[max(0, crest_r - 12):].copy()

    def horiz_wall(w: int, h_tot: int = 88) -> np.ndarray:
        unit = wall_src[:, 24:96]
        tiled = np.tile(unit, (1, (w // 72) + 2, 1))[:, :w]
        top = tiled[:22]
        bot = tiled[-18:]
        cyc = tiled[22:46]
        need = max(0, h_tot - 40)
        mid = np.tile(cyc, ((need // 24) + 2, 1, 1))[:need]
        return np.concatenate([top, mid, bot], axis=0)

    left_upper = keep_largest(cc[0:175, 0:340])
    right_upper = keep_largest(cc[0:225, 672:1152])
    ru_334 = right_upper[16:225, 334:480].copy()
    ru_crest = int(np.where(ru_334[:, 0, 3] > 0)[0].min())
    ru_bot0 = int(np.where(ru_334[:, 0, 3] > 0)[0].max()) + 1

    # 1) Upper-Center Waterfall Pillars (x=240..336 & x=432..528, y=42..162)
    p96 = horiz_wall(96, 120)
    paste_rgba(cliffs_cc, p96, 240, 42)
    paste_rgba(cliffs_cc, p96, 432, 42)

    # 2) Upper-Left Wing (0..192): flat horizontal wall curving cleanly up into chute_L
    ys_lu = np.where(left_upper[:, 120, 3] > 0)[0]
    lu_top, lu_bot = int(ys_lu.min()), int(ys_lu.max()) + 1
    ul_src = left_upper[0:172, 0:192].copy()
    hw_lu = horiz_wall(48, lu_bot - lu_top)
    ul_src[lu_top:lu_bot, 120:144] = hw_lu[:, :24]
    ul_src[lu_bot:, 120:144] = 0
    for dx in range(18):
        col = 144 + dx
        y_bot_c = int(round((lu_bot - 2) - (dx / 17.0) ** 0.85 * 19))
        ul_src[y_bot_c:, col] = 0
        for y_f in range(126, y_bot_c):
            if ul_src[y_f, col, 3] == 0 or y_f >= 132:
                ul_src[y_f, col] = ul_src[y_f - 24, col]
        ul_src[y_bot_c - 2 : y_bot_c, col] = (165, 95, 55, 255)
    paste_rgba(cliffs_cc, horiz_wall(128, lu_bot - lu_top), 0, 96 + lu_top)
    paste_rgba(cliffs_cc, ul_src[:, 120:], 120, 96)

    # 3) Upper-Right Wing (576..768): symmetric counterpart
    paste_rgba(cliffs_cc, cliffs_cc[96:268, 0:192][:, ::-1].copy(), 576, 96)

    # 4) Lower-Left Canyon Wall (0..356, y=324..576): flat outer wing + exact (96, 64) CanyonCamp stepped bastions
    hw_test = horiz_wall(48, ru_bot0 - ru_crest)
    hw_crest = int(np.where((hw_test[:, :16, 3] > 0).mean(axis=1) > 0.75)[0].min())
    ru_solid_crest = int(np.where((ru_334[:, :16, 3] > 0).mean(axis=1) > 0.75)[0].min())
    # Align +2px down so leftmost coping tooth blends right at y=324 with horiz_wall
    y0_ru = (324 + hw_crest) - ru_solid_crest + 2
    paste_rgba(cliffs_cc, horiz_wall(148, ru_bot0 - ru_crest), 0, 324)
    paste_rgba(cliffs_cc, ru_334, 144, y0_ru)
    # Trim any isolated tooth pixel sticking >2px above 324 on cols 144..152
    for xc_t in range(144, 152):
        cliffs_cc[314:326, xc_t] = cliffs_cc[314:326, 140]
        if cliffs_cc[324, xc_t, 3] == 0 and cliffs_cc[325, xc_t, 3] > 0:
            pass
    b_next = ru_334[:190, :120].copy()
    paste_rgba(cliffs_cc, b_next[:, 16:], 144 + 96 + 16, y0_ru + 64)
    if 144 + 96 + 120 < 358:
        paste_rgba(cliffs_cc, b_next[:, 16:], 144 + 2 * 96 + 16, y0_ru + 2 * 64)
    cliffs_cc[320:H, 356:412] = 0

    ys_full = [y for y in range(440, H) if (cliffs_cc[y, 316:356, 3] > 0).all()]
    y_solid_bot = max(ys_full)
    band = cliffs_cc[y_solid_bot - 24 : y_solid_bot, 316:356].copy()
    for yy_abs in range(y_solid_bot, H):
        for xx_abs in range(316, 356):
            if cliffs_cc[yy_abs, xx_abs, 3] == 0:
                cliffs_cc[yy_abs, xx_abs] = band[(yy_abs - y_solid_bot) % 24, xx_abs - 316]
    for yy_abs in range(y_solid_bot, H):
        if cliffs_cc[yy_abs, 315, 3] == 0 and cliffs_cc[yy_abs, 316, 3] > 0:
            cliffs_cc[yy_abs, 315] = (165, 95, 55, 255)

    # 5) Lower-Right Canyon Wall (412..768): symmetric counterpart
    paste_rgba(cliffs_cc, cliffs_cc[320:H, 0:356][:, ::-1].copy(), 768 - 356, 320)
    return cliffs_cc


def segment_and_expand_768():
    """Extract clean layout SDFs from image-16.png, expand smoothly to 768x576, and render 100% Reverie Town terrain & Canyon-Camp cliff-grass raccords."""
    a0 = Image.open(INPUT_LAYOUT).convert("RGBA")
    arr0 = np.array(a0)
    H0, W0 = arr0.shape[:2]
    yy0, xx0 = np.mgrid[:H0, :W0]

    r0, g0, b0 = arr0[:, :, 0].astype(float), arr0[:, :, 1].astype(float), arr0[:, :, 2].astype(float)
    is_mag = (r0 > 180) & (b0 > 170) & (g0 < 80)
    lum0 = 0.299 * r0 + 0.587 * g0 + 0.114 * b0

    non_w = ~is_mag
    grass0 = keep_large(non_w & (g0 > r0 + 3) & (g0 > b0 + 44) & (lum0 > 118), 60)
    grass0 = nd.binary_fill_holes(grass0) & non_w

    rem0 = non_w & ~grass0
    sand_cand = rem0 & (r0 > 192) & (g0 > 162) & (b0 > 98) & ((r0 - b0) < 118)
    sand_filled = nd.binary_fill_holes(nd.binary_closing(sand_cand, iterations=2)) & rem0
    # Fill any old paw-stone holes cleanly inside the clearing (no paw print!)
    paw_zone0 = (yy0 >= 280) & (xx0 >= 240) & (xx0 <= 355)
    paw_enclosed0 = sand_filled & ~sand_cand & paw_zone0
    paw_grey0 = rem0 & paw_zone0 & ((r0 - b0) < 62) & (lum0 < 226)
    paw0 = keep_large(paw_enclosed0 | paw_grey0, 4) & rem0

    cove_band0 = (yy0 >= 215) & (yy0 <= 285)
    sand_rim0 = cove_band0 & rem0 & ((r0 - b0) >= 100) & (b0 >= 75) & (g0 >= 120) & (r0 > 180)
    sand_all0 = (sand_filled | sand_cand | sand_rim0 | paw0) & rem0
    near_w0 = nd.binary_dilation(is_mag, iterations=18)
    plaza0 = (yy0 >= 265) & (yy0 < 368) & (xx0 >= 188) & (xx0 <= 408)
    trail0 = (yy0 >= 368) & (xx0 >= 266) & (xx0 <= 327)
    sand_raw0 = sand_all0 & (yy0 >= 205) & (near_w0 | plaza0 | trail0)
    sand0 = nd.binary_fill_holes(keep_large(sand_raw0, 400)) & non_w

    cliffs_pre0 = rem0 & ~sand0
    cove_open0 = nd.binary_opening(cliffs_pre0 & cove_band0, structure=np.ones((7, 7), bool))
    cove_spurs0 = (cliffs_pre0 & cove_band0) & ~cove_open0
    if cove_spurs0.any():
        sand0 = nd.binary_fill_holes(keep_large(sand_raw0 | cove_spurs0, 400)) & non_w
    cliffs0 = nd.binary_fill_holes(rem0 & ~sand0) & ~is_mag & ~sand0

    water0 = keep_large(is_mag & (yy0 >= 118), 500)
    sdf_basin = smooth_sdf_resize(water0, H, W)
    sdf_grass = smooth_sdf_resize(grass0, H, W)
    sdf_sand  = smooth_sdf_resize(sand0, H, W)
    sdf_cliff = smooth_sdf_resize(cliffs0, H, W)

    # Expand basin bays, central sandy clearing & south trail smoothly for 768x576
    yy, xx = np.mgrid[:H, :W]
    in_pond_zone = (yy >= 152) & (yy <= 372) & (xx >= 118) & (xx <= 650)
    sdf_basin_exp = np.where(in_pond_zone, sdf_basin + 5.5, sdf_basin - 30.0)
    in_plaza_zone = (yy >= 340) & (yy <= 480) & (xx >= 250) & (xx <= 518)
    sdf_sand_exp = np.where(in_plaza_zone, sdf_sand + 5.0, sdf_sand)
    south_trail_sdf = 32.0 - np.abs(xx - 384.0)
    in_south_zone = yy >= 464
    sdf_sand_exp = np.where(in_south_zone & (south_trail_sdf > -8.0), np.maximum(sdf_sand_exp, south_trail_sdf), sdf_sand_exp)
    outside_south_canyon = (yy >= 468) & (np.abs(xx - 384.0) >= 34.0)
    sdf_sand_exp = np.where(outside_south_canyon, -25.0, sdf_sand_exp)

    chute_L = (xx >= CHUTE_LAYOUT["chute_L"][0]) & (xx < CHUTE_LAYOUT["chute_L"][1]) & (yy < CHUTE_LAYOUT["chute_L"][2] + 6)
    chute_C = (xx >= CHUTE_LAYOUT["chute_C"][0]) & (xx < CHUTE_LAYOUT["chute_C"][1]) & (yy < CHUTE_LAYOUT["chute_C"][2] + 6)
    chute_R = (xx >= CHUTE_LAYOUT["chute_R"][0]) & (xx < CHUTE_LAYOUT["chute_R"][1]) & (yy < CHUTE_LAYOUT["chute_R"][2] + 6)
    chutes_all = chute_L | chute_C | chute_R

    land_scores = np.stack([sdf_basin_exp, sdf_grass, sdf_sand_exp, sdf_cliff], axis=0)
    win = land_scores.argmax(0)
    basin = (win == 0) & ~chutes_all
    grass = (win == 1) & ~chutes_all & ~basin
    sand  = (win == 2) & ~chutes_all & ~basin
    cliffs= (win == 3) & ~chutes_all & ~basin

    for cname, m_c in [("chute_L", chute_L), ("chute_C", chute_C), ("chute_R", chute_R)]:
        x0, x1, yf = CHUTE_LAYOUT[cname]
        m_c[yf:, :] = False
        gap = (xx >= x0) & (xx < x1) & (yy >= yf - 4) & (yy <= yf + 8) & ~basin
        basin |= gap
        cliffs &= ~gap
        grass &= ~gap
        sand &= ~gap

    # Ensure basin covers squarely beneath waterfall pillar bases (y=156..172) and tucks behind upper wings (y<248)
    under_pillars = (yy >= 156) & (yy <= 174) & (((xx >= 240) & (xx < 336)) | ((xx >= 432) & (xx < 528)))
    basin |= under_pillars
    basin[(yy < 248) & ((xx < 168) | (xx >= W - 168))] = False
    basin = keep_large(basin, 800)

    # Widen lower south trail flush to the CanyonCamp canyon gate (x=354..414 for y>=482)
    south_gate_sand = (yy >= 482) & (xx >= 354) & (xx < 414) & ~basin & ~chutes_all
    sand = (sand | south_gate_sand) & ~basin & ~chutes_all
    sand = keep_large(sand, 500)

    # Assemble exact CanyonCamp cliff geometry matching image-27.png
    cliffs_arr = build_canyon_camp_cliff_layer()
    cm_fin = cliffs_arr[:, :, 3] > 0
    # Ensure upper grass plateaus behind waterfall pillars & wings stay clean grass above the cliff crest
    cliffs[:] = cm_fin
    sand &= ~cm_fin
    basin &= ~cm_fin

    # Keep cove & south beach shoreline smoothing clean around the CanyonCamp cliffs
    near_upper_cove_cliff = (yy < 306) & ((xx < 218) | (xx >= W - 218))
    sand[near_upper_cove_cliff] = False
    sand_s = nd.binary_closing(sand, structure=np.ones((5, 5), bool))
    sand_s = nd.binary_opening(sand_s, structure=np.ones((5, 5), bool)) & ~basin & ~chutes_all & ~cm_fin
    sand = keep_large(sand_s, 500) | (south_gate_sand & ~cm_fin & ~basin)

    south_beach_band = (yy >= 294) & (yy <= 364) & ((xx < 362) | (xx > 406)) & ~cm_fin & ~chutes_all
    d_b = nd.distance_transform_edt(~basin)
    d_s = nd.distance_transform_edt(basin)
    beach_wave = 0.9 * np.sin(xx * 0.21) + 0.55 * np.cos(xx * 0.43 + 0.8)
    in_cove_mouth = south_beach_band & nd.binary_dilation(sand, iterations=4) & nd.binary_dilation(basin, iterations=4)
    push_sand = in_cove_mouth & basin & (d_s <= 1.2) & (beach_wave > 0.45)
    push_water = in_cove_mouth & sand & (d_b <= 1.2) & (beach_wave < -0.45)
    basin = (basin & ~push_sand) | push_water
    sand = (sand & ~push_water) | push_sand

    grass = ~(basin | chutes_all | cm_fin | sand)
    lab_g, ng = nd.label(grass)
    if ng > 0:
        cnt_g = np.bincount(lab_g.ravel())
        tiny_g = np.isin(lab_g, np.flatnonzero((cnt_g > 0) & (cnt_g < 40)))
        if tiny_g.any():
            grass &= ~tiny_g
            sand |= tiny_g & ~basin & ~chutes_all & ~cm_fin

    masks = {
        "basin": basin,
        "chute_L": chute_L & ~basin,
        "chute_C": chute_C & ~basin,
        "chute_R": chute_R & ~basin,
        "grass": grass,
        "sand": sand,
        "cliffs": cm_fin,
    }

    # --- Render 100% Native 1:1 Reverie Town Grass + Gorge & Lower-Cliff Cast Shadows ---
    rtb = np.array(Image.open(RTB_PATH).convert("RGBA"))
    g16 = rtb[0:16, 0:16].copy()

    sol_full = np.zeros((H, W, 4), dtype=np.uint8)
    sol_full[:, :] = g16[yy % 16, xx % 16]

    grass_arr = np.zeros((H, W, 4), dtype=np.uint8)
    grass_arr[grass] = sol_full[grass]

    water_all = basin | chutes_all
    grass_now = grass_arr[:, :, 3] > 0

    # Clean 2px gorge rock edge on upper grass plateaus directly flanking waterfall shafts (y = 0..42)
    chute_grass_rim1 = grass_now & nd.binary_dilation(chutes_all, iterations=1) & ~cm_fin & (yy < 46)
    chute_grass_rim2 = grass_now & nd.binary_dilation(chutes_all, iterations=2) & ~chute_grass_rim1 & ~cm_fin & (yy < 46)
    grass_arr[chute_grass_rim1, :3] = CANYON_RIM_PAL["outline"]
    grass_arr[chute_grass_rim2, :3] = REV_GRASS_SHADOW[0]

    # Subtle Canyon-Camp 2px dark gorge lip along waterfall pillar flanks facing chutes
    chute_edge1 = cm_fin & nd.binary_dilation(chutes_all, iterations=1) & (yy < 168)
    chute_edge2 = cm_fin & nd.binary_dilation(chutes_all, iterations=2) & ~chute_edge1 & (yy < 168)
    cliffs_arr[chute_edge1, :3] = CANYON_RIM_PAL["outline"]
    cliffs_arr[chute_edge2, :3] = RTC_PAL["mauve_dark"]

    # Clean Canyon-Camp 3px downward olive shadow onto lower grass beneath cliff feet (y >= 165)
    for dy_sh, sh_col in [
        (1, REV_GRASS_SHADOW[0]),
        (2, REV_GRASS_SHADOW[1]),
        (3, REV_GRASS_SHADOW[2]),
    ]:
        sh_src = np.zeros((H, W), dtype=bool)
        sh_src[dy_sh:, :] = cm_fin[:-dy_sh, :] & (yy[:-dy_sh, :] >= 165)
        sh_mask = sh_src & ~cm_fin & ~sand & ~water_all & grass_now
        if dy_sh == 1:
            grass_arr[sh_mask, :3] = sh_col
        else:
            already = np.all(grass_arr[:, :, :3] == REV_GRASS_SHADOW[0], axis=2) | (
                (dy_sh >= 3) & np.all(grass_arr[:, :, :3] == REV_GRASS_SHADOW[1], axis=2)
            )
            grass_arr[sh_mask & ~already, :3] = sh_col

    path_arr = apply_metano_path_style(masks, sand, cm_fin)

    masks["cliffs"] = cm_fin
    masks["grass"] = grass_arr[:, :, 3] > 0

    layers = {
        "sol_complet": sol_full,
        "grass": grass_arr,
        "path_sand": path_arr,
        "cliffs": cliffs_arr,
    }
    return masks, layers


def apply_metano_path_style(
    masks: dict[str, np.ndarray],
    sand_mask: np.ndarray,
    cliff_mask: np.ndarray,
) -> np.ndarray:
    """Render all paths, beach clearing, grass-sand AND water-sand/bank transitions in authentic Metano Town style."""
    yy, xx = np.mgrid[:H, :W]
    water_m = masks["basin"] | masks["chute_L"] | masks["chute_C"] | masks["chute_R"]
    sm = nd.binary_closing(sand_mask, structure=np.ones((5, 5)))
    sm = nd.binary_opening(sm, structure=np.ones((3, 3)))
    sm[564:H, 354:414] = sand_mask[564:H, 354:414]
    near_w_beach = nd.binary_dilation(masks["basin"], iterations=6) & ~masks["basin"] & ~cliff_mask & (yy >= 300)
    sm |= near_w_beach & nd.binary_dilation(sm, iterations=4)

    grass_walk = (~sm) & (~water_m) & (~cliff_mask)
    grass_walk[564:H, 354:414] = False
    lab_gw, ngw = nd.label(grass_walk)
    if ngw > 0:
        cnt_gw = np.bincount(lab_gw.ravel())
        tiny_gw = np.isin(lab_gw, np.flatnonzero((cnt_gw > 0) & (cnt_gw < 60)))
        sm |= tiny_gw
        grass_walk &= ~tiny_gw

    # Directional Metano embankment: top/left edges cast warm scalloped terracotta-amber shade, bottom/right stay soft sunlit gold
    sd_smooth = nd.gaussian_filter(sm.astype(float), 3.0)
    sy_g, sx_g = np.gradient(sd_smooth)
    g_mag = np.hypot(sx_g, sy_g) + 1e-6
    dir_shade = (sx_g + sy_g) / (1.414 * g_mag)

    # Richer organic Metano grass-tuft scalloping (Metano_Town_Base.tile amplitude ~3.5-4.5px)
    tuft_wave = 1.6 * np.sin(xx * 0.28 + yy * 0.17) + 1.2 * np.cos(yy * 0.31 - xx * 0.19)
    tuft_n = tuft_wave + (_hash_noise(yy, xx, 53) - 0.5) * 2.4 + (_hash_noise(yy // 2, xx // 2, 79) - 0.5) * 2.4
    d_to_grass = nd.distance_transform_edt(~grass_walk)
    d_from_grass = nd.distance_transform_edt(grass_walk)
    sd = np.where(grass_walk, -d_from_grass, d_to_grass) + tuft_n

    near_cliff = nd.binary_dilation(cliff_mask, iterations=2)
    near_water = nd.binary_dilation(water_m, iterations=5)
    grass_border_zone = ~near_cliff & ~near_water & ((d_to_grass <= 6.8) | (d_from_grass <= 4.5))

    path_met = np.zeros((H, W, 4), dtype=np.uint8)
    fill_sand = (sm | (nd.binary_dilation(sm, iterations=4) & cliff_mask)) & ~water_m
    path_met[fill_sand, :3] = METANO_PATH_PAL["sand_main"]
    path_met[fill_sand, 3] = 255

    # Authentic Metano sand specks + slightly denser warm grains near borders
    n_speck = _hash_noise(yy // 2, xx // 2, 131) * 0.65 + _hash_noise(yy, xx, 173) * 0.35
    warm_dot = fill_sand & (d_to_grass > 4.5) & (n_speck > 0.68) & (((xx + yy * 2) % 3) == 0)
    rim_dot  = fill_sand & (d_to_grass > 5.0) & (n_speck > 0.84) & (((xx * 2 - yy) % 5) == 0)
    path_met[warm_dot, :3] = METANO_PATH_PAL["sand_warm"]
    path_met[rim_dot, :3]  = METANO_PATH_PAL["sand_rim"]

    shade_bank = dir_shade >= -0.10
    d_pix = _hash_noise(yy, xx, 97)

    outside_border = grass_border_zone & (sd < -2.4)
    path_met[outside_border] = 0

    # Shaded top/left Metano embankment: deep terracotta -> apricot -> warm gold -> cream sand + scattered border pebbles
    in_b_shade = grass_border_zone & shade_bank & (sd >= -0.2) & (sd < 1.6)
    in_b_mid   = grass_border_zone & shade_bank & (sd >= 1.6)  & (sd < 3.2)
    in_b_rim   = grass_border_zone & shade_bank & (sd >= 3.2)  & (sd < 4.7)
    in_b_warm  = grass_border_zone & shade_bank & (sd >= 4.7)  & (sd < 6.2) & (d_pix > 0.35)

    # Sunlit bottom/right Metano embankment
    in_l_mid   = grass_border_zone & ~shade_bank & (sd >= 0.0) & (sd < 1.4)
    in_l_rim   = grass_border_zone & ~shade_bank & (sd >= 1.4) & (sd < 2.8)
    in_l_warm  = grass_border_zone & ~shade_bank & (sd >= 2.8) & (sd < 4.2) & (d_pix > 0.32)

    # Dense organic Metano grass tuft blades overlapping onto sand edge
    in_tuft_edge = grass_border_zone & (sd >= -1.4) & (sd < 0.2)
    in_tuft_tip  = grass_border_zone & (sd >= -2.4) & (sd < -1.1) & (d_pix > 0.36)

    path_met[in_b_warm, :3]    = METANO_PATH_PAL["sand_warm"];  path_met[in_b_warm, 3]    = 255
    path_met[in_b_rim, :3]     = METANO_PATH_PAL["sand_rim"];   path_met[in_b_rim, 3]     = 255
    path_met[in_b_mid, :3]     = METANO_PATH_PAL["bank_mid"];   path_met[in_b_mid, 3]     = 255
    path_met[in_b_shade, :3]   = np.where(d_pix[in_b_shade, None] > 0.38, METANO_PATH_PAL["bank_shade"], METANO_PATH_PAL["bank_mid"]); path_met[in_b_shade, 3] = 255

    path_met[in_l_warm, :3]    = METANO_PATH_PAL["sand_warm"];  path_met[in_l_warm, 3]    = 255
    path_met[in_l_rim, :3]     = METANO_PATH_PAL["sand_rim"];   path_met[in_l_rim, 3]     = 255
    path_met[in_l_mid, :3]     = np.where(d_pix[in_l_mid, None] > 0.50, METANO_PATH_PAL["bank_mid"], METANO_PATH_PAL["sand_rim"]); path_met[in_l_mid, 3] = 255

    path_met[in_tuft_edge, :3] = np.where(shade_bank[in_tuft_edge, None], METANO_PATH_PAL["grass_edge"], METANO_PATH_PAL["grass_dark"]); path_met[in_tuft_edge, 3] = 255
    path_met[in_tuft_tip, :3]  = METANO_PATH_PAL["grass_dark"]; path_met[in_tuft_tip, 3]  = 255

    # Metano Town Water <-> Sandy Path Shore Transition (image-26.png!)
    # Where water borders the sandy beach & south stepping-stone cove:
    # - North/lateral slopes overlooking water get a textured earthen-sand bank (#985828 / #B06858 / #C89850 / #E09860)
    # - South shores approaching the water from below get a scalloped wet-sand shoreline (#D88850 / #F0C078 / #F8C880)
    d_to_water = nd.distance_transform_edt(~masks["basin"])
    w_smooth = nd.gaussian_filter(masks["basin"].astype(float), 2.5)
    wy_g, wx_g = np.gradient(w_smooth)  # >0 wy_g means basin is BELOW -> land sits ABOVE water (north/side bank)
    w_shore_sand = fill_sand & ~cliff_mask & (d_to_water >= 0.5) & (d_to_water <= 5.5)
    bank_noise = (_hash_noise(yy, xx, 199) - 0.5) * 1.4 + 0.6 * np.sin(xx * 0.45 + yy * 0.35)
    dw = d_to_water + bank_noise

    # North/oblique bank walls (lateral walls of the stepping-stone channel & upper sand coves): textured Metano earth-sand bank
    top_bank_mask = w_shore_sand & ((wy_g > 0.15) | ((np.abs(wx_g) > 0.45) & (wy_g > -0.25)))
    path_met[top_bank_mask & (dw <= 1.8), :3] = np.array([152, 88, 40], dtype=np.uint8)     # #985828 deep Metano bank earth
    path_met[top_bank_mask & (dw > 1.8) & (dw <= 3.1), :3] = np.where(
        d_pix[top_bank_mask & (dw > 1.8) & (dw <= 3.1), None] > 0.45,
        np.array([176, 104, 88], dtype=np.uint8),   # #B06858 Metano bank terracotta
        np.array([200, 152, 80], dtype=np.uint8),   # #C89850 Metano warm earth
    )
    path_met[top_bank_mask & (dw > 3.1) & (dw <= 4.3), :3] = METANO_PATH_PAL["bank_shade"]  # #E09860
    path_met[top_bank_mask & (dw > 4.3) & (dw <= 5.1), :3] = METANO_PATH_PAL["bank_mid"]    # #F0C078

    # South beach shoreline meeting water from below (image-26.png): soft Metano wet-sand lip (#E0A868 -> #F0C078 -> #F8C880)
    south_bank_mask = w_shore_sand & ~top_bank_mask
    wet_sand_lip = np.array([224, 168, 104], dtype=np.uint8)  # #E0A868 warm wet sand (no harsh dark line on sunlit beach)
    path_met[south_bank_mask & (dw <= 1.4), :3] = wet_sand_lip
    path_met[south_bank_mask & (dw > 1.4) & (dw <= 2.7), :3] = METANO_PATH_PAL["bank_mid"]   # #F0C078
    path_met[south_bank_mask & (dw > 2.7) & (dw <= 3.8) & (d_pix > 0.35), :3] = METANO_PATH_PAL["sand_rim"]
    return path_met


# ------------------------------------------------------------------ 2. Deep Cascade-Blue Reverie Town Pond & Sparkles
def extract_reverie_pond_sparkle_4f() -> list[np.ndarray]:
    sheet_cache = {p.stem: np.array(Image.open(p).convert("RGBA")) for p in REVERIE_SHEETS_DIR.glob("*.png")}
    d_et = json.loads(gzip.decompress(REVERIE_ETANG_PATH.read_bytes()).decode("utf-8-sig"))
    layers_et = d_et["Object"]["Layers"]

    x0_cell, y0_cell, cw, ch = 123, 252, 5, 5
    out_4f = []
    bg_etang = np.array([128, 216, 224], dtype=np.uint8)
    for f_idx in range(4):
        blk = np.zeros((ch * 8, cw * 8, 4), dtype=np.uint8)
        for lay in layers_et[:9]:
            tiles = lay["Tiles"]
            for dx in range(cw):
                for dy in range(ch):
                    cell = tiles[x0_cell + dx][y0_cell + dy]
                    if not cell:
                        continue
                    for anim in cell.get("Layers", []):
                        frs = anim.get("Frames", [])
                        if not frs:
                            continue
                        f = frs[f_idx % len(frs)]
                        sh = f.get("Sheet", "")
                        if sh not in sheet_cache:
                            continue
                        tx, ty = f["TexLoc"]["X"] * 8, f["TexLoc"]["Y"] * 8
                        tile = sheet_cache[sh][ty : ty + 8, tx : tx + 8]
                        m = tile[:, :, 3] > 0
                        if m.any():
                            blk[dy * 8 : (dy + 1) * 8, dx * 8 : (dx + 1) * 8][m] = tile[m]
        spr = blk[11:29, 8:26].copy()
        is_bg = np.all(spr[:, :, :3] == bg_etang, axis=2)
        spr[is_bg] = 0
        m_hi = (spr[:, :, 3] > 0) & (spr[:, :, 0] > 210)
        m_lo = (spr[:, :, 3] > 0) & (spr[:, :, 0] <= 210)
        spr[m_hi, :3] = REVERIE_WATER_PAL["sparkle"]
        spr[m_lo, :3] = REVERIE_WATER_PAL["glint"]
        out_4f.append(spr)
    return out_4f


def build_reverie_pond_and_sparkles(masks: dict[str, np.ndarray], dry_mask: np.ndarray):
    yy, xx = np.mgrid[:H, :W]
    chutes_all = masks["chute_L"] | masks["chute_C"] | masks["chute_R"]
    visible_water = masks["basin"]
    water_domain = (
        visible_water
        | chutes_all
        | (nd.binary_dilation(visible_water | chutes_all, iterations=3) & dry_mask)
    )
    d_shore = nd.distance_transform_edt(visible_water)

    frames = []
    for p in range(4):
        ph = 2.0 * np.pi * p / 4.0
        scallop = 0.60 * np.sin(xx * 0.22 + ph) + 0.40 * np.cos(yy * 0.20 - xx * 0.10 + ph)

        a = np.zeros((H, W, 4), dtype=np.uint8)
        a[:, :, :3] = REVERIE_WATER_PAL["surface"]
        a[:, :, 3] = 255

        a[d_shore <= (4.90 + 0.85 * scallop)] = (*REVERIE_WATER_PAL["swell"], 255)
        a[d_shore <= (3.20 + 0.65 * scallop)] = (*REVERIE_WATER_PAL["mid"], 255)
        # Metano/Reverie animated shore wave glints & crest lines all around grass & sandy-path shorelines (image-26.png)
        crest_arc = (
            (d_shore >= 2.0)
            & (d_shore <= 3.6)
            & (np.sin(xx * 0.22 + ph) > 0.52)
            & (np.cos(yy * 0.30 - ph) > 0.10)
        )
        glint_arc = (
            (d_shore >= 1.5)
            & (d_shore <= 2.7)
            & (np.sin(xx * 0.30 - ph) > 0.68)
            & (np.cos(yy * 0.24 + ph) > 0.28)
        )
        a[crest_arc] = (*REVERIE_WATER_PAL["crest"], 255)
        a[glint_arc] = (*REVERIE_WATER_PAL["glint"], 255)
        a[d_shore <= (1.50 + 0.35 * scallop)] = (*REVERIE_WATER_PAL["deep"], 255)

        a[~water_domain] = 0
        under_shore = water_domain & ~visible_water
        a[under_shore] = (*REVERIE_WATER_PAL["deep"], 255)
        frames.append(a)

    rev_sp_4f = extract_reverie_pond_sparkle_4f()
    return frames, d_shore, rev_sp_4f, visible_water


def place_reverie_sparkles(
    rev_sp_4f: list[np.ndarray],
    visible_water: np.ndarray,
    d_shore: np.ndarray,
    foam_footprint: np.ndarray,
    cascade_footprint: np.ndarray,
    stones_footprint: np.ndarray | None = None,
):
    sp_any = np.maximum.reduce([s[:, :, 3] > 0 for s in rev_sp_4f])
    sp_pad = nd.binary_dilation(sp_any, iterations=2)
    no_go = nd.binary_dilation(foam_footprint | cascade_footprint, iterations=6)
    if stones_footprint is not None:
        no_go |= nd.binary_dilation(stones_footprint, iterations=5)
    safe = visible_water & (d_shore > 9.0) & ~no_go
    frames = [np.zeros((H, W, 4), dtype=np.uint8) for _ in range(4)]
    spots = [(168, 250), (225, 290), (298, 224), (470, 224), (543, 290), (600, 250)]
    ys_s, xs_s = np.where(safe)
    for idx_s, (cx, cy) in enumerate(spots):
        x0, y0 = max(0, min(W - 18, cx - 9)), max(0, min(H - 18, cy - 9))
        if not (visible_water[y0 : y0 + 18, x0 : x0 + 18][sp_pad].all() and not no_go[y0 : y0 + 18, x0 : x0 + 18][sp_pad].any()):
            if len(xs_s) > 0:
                j = int(np.argmin((xs_s - cx) ** 2 + (ys_s - cy) ** 2))
                cx, cy = int(xs_s[j]), int(ys_s[j])
                x0, y0 = max(0, min(W - 18, cx - 9)), max(0, min(H - 18, cy - 9))
        if not (visible_water[y0 : y0 + 18, x0 : x0 + 18][sp_pad].all() and not no_go[y0 : y0 + 18, x0 : x0 + 18][sp_pad].any()):
            continue
        for p4 in range(4):
            spr = rev_sp_4f[(p4 + idx_s) % 4]
            m = spr[:, :, 3] > 0
            frames[p4][y0 : y0 + 18, x0 : x0 + 18][m] = spr[m]
    return frames


def build_reverie_pond_stones(
    visible_water: np.ndarray,
    dry_terrain: np.ndarray,
    foam_footprint: np.ndarray,
    cascade_footprint: np.ndarray,
):
    """Place full uncompacted 1:1 Reverie Town pond platform + 4 stepping stones + flanking river stones (8 frames) in native Reverie water palette."""
    rta = np.array(Image.open(RTA_PATH).convert("RGBA"))

    def adapt_stone(arr: np.ndarray) -> np.ndarray:
        out = arr.copy()
        gm = (out[:, :, 3] > 0) & (out[:, :, 0] == 120) & (out[:, :, 1] == 184) & (out[:, :, 2] == 64)
        out[gm, :3] = (144, 140, 114)
        return out

    def extend_plat_4_steps(spr: np.ndarray) -> np.ndarray:
        step_slice = spr[106:130, :]
        return np.concatenate([spr[:130, :], step_slice, spr[130:, :]], axis=0)

    plat_slots = [
        (119, 992), (231, 992), (343, 992), (7, 1136),
        (119, 1136), (231, 1136), (343, 1136), (7, 992),
    ]
    sing_order = [1, 2, 3, 4, 5, 6, 7, 0]

    cx = W // 2
    ys_dock = np.where((~visible_water[:, cx]) & dry_terrain[:, cx] & (np.arange(H) >= 310))[0]
    y_dock = int(ys_dock[0]) if len(ys_dock) else 358
    y_plat = y_dock - 150
    y_sing_in = y_plat + 22
    dx_in = 122
    y_sing_out = y_plat - 6
    dx_out = 196

    no_stone = foam_footprint | cascade_footprint
    stone_frames = []
    bridge_walk_mask = np.zeros((H, W), dtype=bool)

    for idx_f in range(8):
        x0p, y0p = plat_slots[idx_f]
        pf = extend_plat_4_steps(adapt_stone(rta[y0p : y0p + 134, x0p : x0p + 98]))

        canvas = np.zeros((H, W, 4), dtype=np.uint8)
        ph, pw = pf.shape[:2]
        y_end = min(H, y_plat + ph)
        canvas[y_plat : y_end, cx - pw // 2 : cx - pw // 2 + pw] = pf[: y_end - y_plat]

        placements = [
            (cx - dx_in,  y_sing_in,  (idx_f + 2) % 8),
            (cx + dx_in,  y_sing_in,  (idx_f + 5) % 8),
            (cx - dx_out, y_sing_out, (idx_f + 1) % 8),
            (cx + dx_out, y_sing_out, (idx_f + 4) % 8),
        ]
        for sx_c, sy_t, ph_s in placements:
            k_s = sing_order[ph_s]
            sf = adapt_stone(rta[1336:1359, 12 + k_s * 40 : 36 + k_s * 40])
            if 0 <= sy_t and sy_t + 23 <= H and 0 <= sx_c - 12 and sx_c + 12 <= W:
                if visible_water[sy_t + 2 : sy_t + 20, sx_c - 9 : sx_c + 9].all():
                    canvas[sy_t : sy_t + 23, sx_c - 12 : sx_c + 12] = sf

        m = canvas[:, :, 3] > 0
        r_c, b_c = canvas[:, :, 0].astype(int), canvas[:, :, 2].astype(int)
        is_rip = m & (b_c > r_c + 20)
        is_body = m & ~is_rip

        keep_mask = (is_rip & visible_water & ~dry_terrain & ~no_stone) | (is_body & ~dry_terrain & ~no_stone)
        step_dock = is_body & (np.arange(H)[:, None] <= y_dock + 2) & (np.abs(np.arange(W)[None, :] - cx) <= 14) & ~no_stone
        keep_mask |= step_dock
        canvas[~keep_mask] = 0
        stone_frames.append(canvas)

        if idx_f == 0:
            x_p0, x_p1 = cx - pw // 2, cx - pw // 2 + pw
            yy_grid = np.arange(H)[:, None]
            deck_or_steps = (yy_grid <= y_plat + 43) | (yy_grid >= y_plat + 54)
            bridge_walk_mask[y_plat : y_end, x_p0:x_p1] = (
                is_body[y_plat : y_end, x_p0:x_p1]
                & keep_mask[y_plat : y_end, x_p0:x_p1]
                & deck_or_steps[y_plat : y_end, :]
            )

    stones_union = np.maximum.reduce([f[:, :, 3] > 0 for f in stone_frames])
    meta = {
        "y_plat": y_plat,
        "y_dock": y_dock,
        "y_sing_in": y_sing_in,
        "dx_in": dx_in,
        "y_sing_out": y_sing_out,
        "dx_out": dx_out,
    }
    return stone_frames, stones_union, bridge_walk_mask, meta


# ------------------------------------------------------------------ 3. Postless Tiles7 PMU Cascades (Zero-Mixel 1x1)
def build_1x1_cascade_strip(tex: np.ndarray, target_w: int) -> np.ndarray:
    th, tw = tex.shape[:2]
    if target_w == tw:
        return tex.copy()
    if target_w < tw:
        edge = min(6, target_w // 4)
        mid_w = target_w - 2 * edge
        s0 = (tw - mid_w) // 2
        return np.concatenate([tex[:, :edge], tex[:, s0 : s0 + mid_w], tex[:, tw - edge :]], axis=1)
    edge = 14
    extra = target_w - tw
    mid_src = tex[:, edge : tw - edge]
    mid_mir = mid_src[:, ::-1]
    tile_cycle = np.concatenate([mid_src, mid_mir], axis=1)
    need = (tw - 2 * edge) + extra
    reps = (need // tile_cycle.shape[1]) + 1
    full_mid = np.tile(tile_cycle, (1, reps, 1))[:, :need]
    return np.concatenate([tex[:, :edge], full_mid, tex[:, tw - edge :]], axis=1)


def recolor_cascade_to_reverie(tex: np.ndarray) -> np.ndarray:
    """Remap Tiles7 cascade blue-to-white streaks cleanly onto exact Reverie Town Cascade Palette."""
    out = tex.copy()
    m = out[:, :, 3] > 0
    if not m.any():
        return out
    rgb = out[m, :3].astype(float)
    lum = 0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2]
    src_lums = np.array([56.0, 73.0, 91.0, 112.0, 135.0, 165.0, 198.0, 244.0])
    recol = np.stack([np.rint(np.interp(lum, src_lums, REVERIE_CASCADE_RAMP[:, c])) for c in range(3)], axis=-1)
    out[m, :3] = np.clip(recol, 0, 255).astype(np.uint8)
    return out


def build_pmu_cascades(masks: dict[str, np.ndarray], dry_terrain: np.ndarray, cliffs_mask: np.ndarray):
    t7 = Image.open(T7_PATH).convert("RGBA")
    # Strip the 3-4px bright pale Tiles7 border rails & remap cleanly onto Reverie Town cascade palette
    t7_wide = recolor_cascade_to_reverie(np.array(t7.crop((0, 13664, 64, 13760)))[:, 4:-4])
    t7_medL = recolor_cascade_to_reverie(np.array(t7.crop((280, 13536, 328, 13632)))[:, 3:-3])
    t7_medR = recolor_cascade_to_reverie(np.array(t7.crop((376, 13536, 424, 13632)))[:, 3:-3])
    assert t7_wide.shape == (96, 56, 4) and t7_medL.shape == (96, 42, 4)

    yy, xx = np.mgrid[:H, :W]
    chute_specs = []
    configs = [
        ("chute_L", t7_medL, 3),
        ("chute_C", t7_wide, 0),
        ("chute_R", t7_medR, 5),
    ]
    for name, src_tex, phase_off in configs:
        cm = masks[name]
        x0, x1, y_foot = CHUTE_LAYOUT[name]
        cx = (x0 + x1) // 2
        gorge_w = x1 - x0
        strip_w = gorge_w + 4
        strip = build_1x1_cascade_strip(src_tex, strip_w)
        x_start = max(0, x0 - 2)
        x_end = min(W, x_start + strip.shape[1])

        # Bleed 2px ONLY behind cliffs_mask (which draws above cascades), NEVER onto grass (which draws below)!
        # Tuck outer cascade sides 5px above y_foot so zero cyan/white column edges ever poke past foam corners!
        in_shaft = (xx >= x_start) & (xx < x_end) & (yy < y_foot - 5)
        behind_cliff = nd.binary_dilation(cm, iterations=2) & ~cm & cliffs_mask
        in_mid = (np.abs(xx - cx) <= max(8, gorge_w // 2 - 7)) & (yy < y_foot + 1)
        in_throat = (np.abs(xx - cx) <= max(8, gorge_w // 2 - 11)) & (yy >= y_foot - 5) & (yy < y_foot + 6)
        mask_ext = (cm & (yy < y_foot - 5)) | (in_shaft & behind_cliff) | in_mid | in_throat
        mask_ext &= ~(dry_terrain & ~behind_cliff)

        chute_specs.append({
            "name": name,
            "strip": strip,
            "x_start": x_start,
            "x_end": x_end,
            "y_top": 0,
            "y_foot": y_foot,
            "cx": cx,
            "gorge_w": gorge_w,
            "phase_off": phase_off,
            "mask_ext": mask_ext,
        })

    cascade_frames = []
    for p8 in range(8):
        a = np.zeros((H, W, 4), dtype=np.uint8)
        for sp in chute_specs:
            strip = sp["strip"]
            x0, x1 = sp["x_start"], sp["x_end"]
            sw = x1 - x0
            ph = (p8 + sp["phase_off"]) % 8
            y_lim = min(H, sp["y_foot"] + 15)
            for y in range(sp["y_top"], y_lim):
                sy = (y - sp["y_top"] - 12 * ph) % 96
                row_m = sp["mask_ext"][y, x0:x1] & (strip[sy, :sw, 3] > 128)
                a[y, x0:x1][row_m] = strip[sy, :sw][row_m]
        cascade_frames.append(a)

    cascade_union = masks["chute_L"] | masks["chute_C"] | masks["chute_R"]
    return cascade_frames, chute_specs, cascade_union


# ------------------------------------------------------------------ 4. Canonical 3-Pose PMU Foam
def map_foam_to_t7_palette(im: Image.Image) -> np.ndarray:
    a = np.array(im.convert("RGBA"))
    m = a[:, :, 3] > 0
    pts = a[m][:, :3].astype(float)
    d2 = ((pts[:, None, :] - T7_FOAM_RAMP[None, :, :].astype(float)) ** 2).sum(axis=-1)
    a[m, :3] = T7_FOAM_RAMP[d2.argmin(axis=-1)]
    a[~m] = 0
    return a


def build_canonical_pmu_foam(
    chute_specs: list[dict],
    visible_water: np.ndarray,
    dry_terrain: np.ndarray,
    cascade_union: np.ndarray,
):
    refs_dir = PROJET / "source/antre_harmonie_v3/references"
    raw_foams = [Image.open(refs_dir / f"ecume_native_{i}.png").convert("RGBA") for i in range(3)]
    alphas = np.maximum.reduce([np.array(im)[:, :, 3] > 0 for im in raw_foams])
    ys_b, xs_b = np.where(alphas)
    shared_box = (int(xs_b.min()), int(ys_b.min()), int(xs_b.max()) + 1, int(ys_b.max()) + 1)
    # Larger, fluffier canonical PMU foam clouds at all 3 waterfall bases (image-25.png fix!)
    canon_wide = [np.array(Image.fromarray(map_foam_to_t7_palette(im.crop(shared_box))).resize((132, 58), NN)) for im in raw_foams]
    canon_small = [np.array(Image.fromarray(map_foam_to_t7_palette(im.crop(shared_box))).resize((84, 42), NN)) for im in raw_foams]

    phase_offsets = {"chute_L": 0, "chute_C": 1, "chute_R": 2}
    wet_pocket_all = (visible_water | cascade_union) & ~dry_terrain
    foam_frames = []
    for p3 in range(3):
        a = np.zeros((H, W, 4), dtype=np.uint8)
        for sp in chute_specs:
            name = sp["name"]
            pose_idx = (p3 + phase_offsets[name]) % 3
            spr = canon_wide[pose_idx] if name == "chute_C" else canon_small[pose_idx]
            fh, fw = spr.shape[:2]

            cx = sp["cx"]
            y_foot = sp["y_foot"]
            x0 = cx - fw // 2
            y0 = y_foot - (24 if name == "chute_C" else 19)

            canvas = np.zeros((H, W, 4), dtype=np.uint8)
            sx0, sy0 = max(0, x0), max(0, y0)
            sx1, sy1 = min(W, x0 + fw), min(H, y0 + fh)
            canvas[sy0:sy1, sx0:sx1] = spr[sy0 - y0 : sy1 - y0, sx0 - x0 : sx1 - x0]

            canvas[~wet_pocket_all] = 0
            throat = (
                (np.abs(np.arange(W)[None, :] - cx) <= max(6, fw // 5))
                & (np.abs(np.arange(H)[:, None] - (y_foot + 2)) <= 5)
                & wet_pocket_all
            )
            if throat.any():
                canvas[throat & (canvas[:, :, 3] == 0)] = (*T7_FOAM_RAMP[-1], 255)
                lab, _ = nd.label(canvas[:, :, 3] > 0, np.ones((3, 3)))
                keep_ids = np.unique(lab[throat])
                canvas[~np.isin(lab, keep_ids[keep_ids > 0])] = 0

            m = canvas[:, :, 3] > 0
            a[m] = canvas[m]
        foam_frames.append(a)

    foam_union = np.maximum.reduce([f[:, :, 3] > 0 for f in foam_frames])
    return foam_frames, foam_union


# ------------------------------------------------------------------ 5. PMDO 0.8.12 / Destiny Integration + Previews
def build_swim_ripple_4f() -> list[np.ndarray]:
    C_OUT = np.array([ 80, 128, 184, 210], dtype=np.uint8)
    C_MID = np.array([ 88, 176, 200, 228], dtype=np.uint8)
    C_INN = np.array([156, 234, 246, 242], dtype=np.uint8)
    C_HI  = np.array([247, 255, 255, 248], dtype=np.uint8)
    frames = []
    specs = [
        (13.8, 6.0, 0.84, 0.99, 0.55, 0.69),
        (14.4, 6.3, 0.86, 1.00, 0.58, 0.71),
        (14.8, 6.5, 0.87, 1.00, 0.61, 0.73),
        (14.3, 6.2, 0.85, 0.99, 0.57, 0.70),
    ]
    for rx, ry, o0, o1, i0, i1 in specs:
        fr = np.zeros((16, 32, 4), dtype=np.uint8)
        for yy in range(16):
            for xx in range(32):
                dx = (xx + 0.5 - 16.0) / rx
                dy = (yy + 0.5 - 8.0) / ry
                d = (dx * dx + dy * dy) ** 0.5
                if o0 <= d <= o1:
                    if yy >= 10 and abs(dx) < 0.72:
                        col = C_HI
                    elif yy >= 8 and abs(dx) < 0.84:
                        col = C_INN
                    else:
                        col = C_MID if d < (o0 + o1) * 0.54 else C_OUT
                    fr[yy, xx] = col
                elif i0 <= d <= i1:
                    if yy >= 9 and abs(dx) < 0.62:
                        col = C_HI
                    else:
                        col = C_INN if d < (i0 + i1) * 0.55 else C_MID
                    fr[yy, xx] = col
        frames.append(fr)
    return frames


def write_dir_sheet(dest: Path, tw: int, th: int, frames: list[np.ndarray]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    strip = Image.new("RGBA", (tw * len(frames), th), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        strip.paste(premultiply_rgba(Image.fromarray(fr)), (i * tw, 0))
    buf = io.BytesIO()
    strip.save(buf, format="PNG")
    png_raw = buf.getvalue()
    with dest.open("wb") as f:
        f.write(struct.pack("<q", len(png_raw)))
        f.write(png_raw)
        f.write(struct.pack("<iiii", tw, th, 1, len(frames)))


def save_dedup_tile_sheet(dest: Path, tile_size: int, sheet_imgs: dict[tuple[int, int], Image.Image]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    items: list[tuple[int, int, bytes]] = []
    for tx, ty in sorted(sheet_imgs.keys()):
        im = premultiply_rgba(sheet_imgs[(tx, ty)])
        if im.getchannel("A").getbbox() is None:
            continue
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        items.append((tx, ty, buf.getvalue()))
    count = len(items)
    cur = 8 + 16 * count
    offsets, chunks = [], []
    for _, _, blob in items:
        offsets.append(cur)
        ch = struct.pack("<q", len(blob)) + blob
        chunks.append(ch)
        cur += len(ch)
    with dest.open("wb") as f:
        f.write(struct.pack("<ii", tile_size, count))
        for (tx, ty, _), off in zip(items, offsets):
            f.write(struct.pack("<iiq", tx, ty, off))
        for ch in chunks:
            f.write(ch)


def write_ora(path: Path, named_layers: list[tuple[str, np.ndarray]], comp: Image.Image):
    root = ET.Element("image", w=str(W), h=str(H), name="Whiscash Pond Layout Reverie — Grand Doyen")
    stack = ET.SubElement(root, "stack")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        for i, (name, arr) in reversed(list(enumerate(named_layers))):
            fn = f"data/layer{i:02d}.png"
            ET.SubElement(
                stack, "layer", name=name, src=fn, x="0", y="0", opacity="1.0",
                visibility="visible", **{"composite-op": "svg:src-over"},
            )
            z.writestr(fn, png_bytes(Image.fromarray(arr)))
        z.writestr("mergedimage.png", png_bytes(comp))
        th = comp.copy()
        th.thumbnail((256, 256))
        z.writestr("Thumbnails/thumbnail.png", png_bytes(th))
        z.writestr("stack.xml", ET.tostring(root, encoding="utf-8", xml_declaration=True))


def bfs_16x16(blocked: np.ndarray, start_cell: tuple[int, int], goal_cell: tuple[int, int]) -> bool:
    gh, gw = blocked.shape
    def free(r, c):
        return 0 <= r and r + 1 < gh and 0 <= c and c + 1 < gw and not blocked[r : r + 2, c : c + 2].any()
    if not free(*start_cell) or not free(*goal_cell):
        return False
    seen = {start_cell}
    q = deque([start_cell])
    while q:
        r, c = q.popleft()
        if (r, c) == goal_cell:
            return True
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if (nr, nc) not in seen and free(nr, nc):
                seen.add((nr, nc))
                q.append((nr, nc))
    return False


def build_pmdo_pack(
    stack_specs: list[tuple[str, list[np.ndarray], int]],
    blocked: np.ndarray,
    entry_px: tuple[int, int],
    goal_px: tuple[int, int],
    doyen_px: tuple[int, int],
    swim_4f: list[np.ndarray],
):
    gfx = load_mod("pmdo_codec", PROJET / "source/pmdo_cote/build.py")
    tools = load_mod("index_tools", PROJET / "source/pmdo_cote/INSTALLER.py")

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ROOT / "whiscash_pond_metano_projet_pmdo_0812.zip") as z:
        tpl = json.loads(z.read("whiscash_pond_metano/Data/Ground/whiscash_pond_metano.rsground").decode())

    o = tpl["Object"]
    layers_json, banks = [], []
    pfx = "WPL1"
    for i, (title, frames, ticks) in enumerate(stack_specs):
        tag = title.split("_", 1)[1].upper()[:10]
        bank = gfx.TileBank(f"{pfx}_{i:02d}_{tag}")
        bank.ids[bytes(256)] = (0, 0)
        bank.data[(0, 0)] = bytes(256)

        def cell(x, y, frames=frames, bank=bank):
            fs = []
            for a in frames:
                f = bank.add(Image.fromarray(a[y * 8 : y * 8 + 8, x * 8 : x * 8 + 8]), x, y)
                fs.append(f if f else {"Sheet": bank.name, "TexLoc": {"X": 0, "Y": 0}})
            if all(f["TexLoc"] == {"X": 0, "Y": 0} for f in fs):
                return []
            return [fs[0]] if all(f == fs[0] for f in fs) else fs

        layers_json.append(gfx.layer(title, GW, GH, cell, ticks))
        banks.append(bank)

    layers_json.append(gfx.layer(f"{len(layers_json) + 1:02d}_avant_plan_arbres_plus_tard", GW, GH, draw=4))

    for bank in banks:
        bank.write(STAGE / f"Content/Tile/{bank.name}.tile")
    write_dir_sheet(STAGE / "Content/Object/Etang_Nage_Ondes_Jour.dir", 32, 16, swim_4f)

    nodes = {}
    for p in sorted((STAGE / "Content/Tile").glob("*.tile")):
        with p.open("rb") as f:
            nodes[p.stem] = tools.read_node(f)
    (STAGE / "Content/Tile/index.idx").write_bytes(tools.encode_index(nodes))

    ns = "whiscash_pond_layout_reverie"
    o.update(
        Name={"DefaultText": "Etang du Doyen — Rêverie Town (768x576)", "LocalTexts": {}},
        AssetName=ns,
        Released=False,
        TexSize=1,
        Music="",
        EdgeView=1,
        ViewCenter=None,
        ViewOffset={"X": 0, "Y": 0},
        ActiveChar=None,
        Status={},
        Layers=layers_json,
        Background={"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []},
        Comment=(
            f"PMDO 0.8.12. Etang du Doyen agrandi ({W}x{H}, {GW}x{GH} tuiles 8x8, 1x1 zero mixel) : "
            "herbe et falaises Reverie Town, raccords cliff-grass inspires de Canyon Camp, "
            "chemin sableux style Metano Town (sans empreinte), eau et 3 cascades couleur Reverie Town (animations conservees), "
            "plateforme complete + 4 river stones animees (8x5 ticks) + ecume canonique 3 poses."
        ),
    )
    o["obstacles"] = [
        [{"Bounds": {"X": x * 8, "Y": y * 8, "Width": 8, "Height": 8}, "Tags": int(blocked[y, x])} for y in range(GH)]
        for x in range(GW)
    ]
    mk = lambda n, p: {
        "EntName": n,
        "Direction": 4,
        "EntEnabled": True,
        "triggerType": 0,
        "Collider": {"X": int(p[0]), "Y": int(p[1]), "Width": 16, "Height": 16},
    }
    o["Entities"] = [
        {
            "Name": "Entrees et Marqueurs",
            "Visible": True,
            "MapChars": [],
            "GroundObjects": [],
            "Spawners": [],
            "Markers": [
                mk("entrance", entry_px),
                mk("centre_pierre", goal_px),
                mk("grand_doyen", doyen_px),
            ],
        }
    ]
    o["Decorations"] = [
        {
            "Name": "Nage_Grand_Doyen",
            "Layer": 0,
            "Visible": False,
            "Anims": [
                {
                    "MapLoc": {"X": doyen_px[0] - 8, "Y": doyen_px[1] + 4},
                    "ObjectAnim": {
                        "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
                        "AnimIndex": "Etang_Nage_Ondes_Jour",
                        "FrameTime": 10,
                        "StartFrame": -1,
                        "EndFrame": -1,
                        "AnimDir": 0,
                        "Alpha": 255,
                        "AnimFlip": 0,
                    },
                }
            ],
        }
    ]
    tpl["Version"] = "0.8.12.0"

    gfx.save(STAGE / f"Data/Ground/{ns}.rsground", json.dumps(tpl, ensure_ascii=False, separators=(",", ":")).encode())
    gfx.save(
        STAGE / f"Data/Script/{ns}/ground/{ns}/init.lua",
        f"-- {ns} : base d'edition PMDO 0.8.12, aucun warp.\nlocal {ns} = {{}}\nreturn {ns}\n".encode(),
    )

    ident = uuid.uuid5(uuid.NAMESPACE_URL, f"https://github.com/meromoonmeri/PMDO-Destiny/{ns}")
    (STAGE / "Mod.xml").write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
<Header>
  <Name>Etang du Doyen — 100% Reverie Town ({W}x{H}, PMDO 0.8.12)</Name>
  <Author>meromoonmeri</Author>
  <Description>Zone du Grand Doyen agrandie ({W}x{H}, {GW}x{GH} tuiles 8x8) en herbe, falaises et raccords 100% Reverie Town.</Description>
  <Namespace>{ns}</Namespace>
  <UUID>{ident}</UUID>
  <Version>1.1.0.0</Version>
  <GameVersion>0.8.12.0</GameVersion>
  <ModType>Quest</ModType>
  <Relationships />
</Header>
"""
    )

    with zipfile.ZipFile(ROOT / "whiscash_pond_metano_projet_pmdo_0812.zip") as z:
        installer_txt = z.read("whiscash_pond_metano/INSTALLER.py").decode()
    (STAGE / "INSTALLER.py").write_text(installer_txt)
    (STAGE / "README_PACK.md").write_text(
        f"# Whiscash Pond — Grand Doyen ({W}x{H}, PMDO 0.8.12)\n\n"
        f"- Format `TexSize = 1` (`8x8` px), `{GW} x {GH}` tuiles, zero mixel.\n"
        "- Herbe et falaises Reverie Town + raccords cliff-grass en altitude style Canyon Camp.\n"
        "- Chemin sableux style Metano Town (sans empreinte ni gravillons).\n"
        "- Etang et 3 cascades couleur Reverie Town (4x10 ticks + 6 scintillements 18x18, cascades 8x5 ticks + ecume 3 poses).\n"
        "- Plateforme complete + 4 river stones Reverie Town animees (8x5 ticks) + preparation nage Grand Doyen.\n"
    )

    zip_out = ROOT / "whiscash_pond_layout_reverie_projet_pmdo_0812.zip"
    with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as zout:
        for fpath in sorted(STAGE.rglob("*")):
            if fpath.is_file():
                zout.write(fpath, f"{ns}/{fpath.relative_to(STAGE).as_posix()}")
    return {b.name: len(b.data) for b in banks}


def _decode_pmdo_tile(tile_path: Path, out_png: Path):
    raw = tile_path.read_bytes()
    ts, count = struct.unpack_from("<ii", raw, 0)
    entries = [struct.unpack_from("<iiq", raw, 8 + i * 16) for i in range(count)]
    max_x = max(x for x, _, _ in entries) + 1
    max_y = max(y for _, y, _ in entries) + 1
    canvas = Image.new("RGBA", (max_x * ts, max_y * ts), (0, 0, 0, 0))
    for x, y, pos in entries:
        sz = struct.unpack_from("<q", raw, pos)[0]
        if sz > 0:
            tile_im = Image.open(io.BytesIO(raw[pos + 8 : pos + 8 + sz])).convert("RGBA")
            canvas.paste(tile_im, (x * ts, y * ts))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_png)


def integrate_destiny_repo(
    repo_root: Path,
    stack_specs: list[tuple[str, list[np.ndarray], int]],
    blocked: np.ndarray,
    entry_px: tuple[int, int],
    goal_px: tuple[int, int],
    doyen_px: tuple[int, int],
    swim_4f: list[np.ndarray],
) -> None:
    tile_dir = repo_root / "game/Content/Tile"
    obj_dir = repo_root / "game/Content/Object"
    ground_dir = repo_root / "game/Data/Ground"
    zone_path = repo_root / "game/Data/Zone/reverie.json"
    zidx_path = repo_root / "game/Data/Zone/index.idx"

    obs_json = [[{"Tags": int(blocked[y, x])} for y in range(GH)] for x in range(GW)]

    def make_marker(name: str, x: int, y: int, direction: int) -> dict:
        return {
            "EntName": name,
            "Direction": direction,
            "EntEnabled": True,
            "EntOrder": 0,
            "InteractOrder": 0,
            "triggerType": 0,
            "Collider": {"X": int(x), "Y": int(y), "Width": 16, "Height": 16},
        }

    ripple_x = int(doyen_px[0]) - 8
    ripple_y = int(doyen_px[1]) + 4

    for amb, amb_cap, amb_fr, tint in DESTINY_AMBIANCES:
        stem = f"etangdudoyen_{amb}"
        sheet_name = f"Destiny_Etang_Doyen_{amb_cap}"
        ripple_sheet = f"Etang_Nage_Ondes_{amb_cap}"

        tinted_rip = [tint_rgba_lut(fr, tint) for fr in swim_4f]
        write_dir_sheet(obj_dir / f"{ripple_sheet}.dir", 32, 16, tinted_rip)

        tile_reg: dict[bytes, tuple[int, int]] = {}
        sheet_imgs: dict[tuple[int, int], Image.Image] = {}

        def reg_tile(arr8: np.ndarray) -> tuple[int, int]:
            t8 = tint_rgba_lut(arr8, tint)
            if not (t8[:, :, 3] > 0).any():
                return (-1, -1)
            raw = t8.tobytes()
            if raw not in tile_reg:
                idx = len(tile_reg)
                loc = (idx % 64, idx // 64)
                tile_reg[raw] = loc
                sheet_imgs[loc] = Image.fromarray(t8)
            return tile_reg[raw]

        layers_json = []
        for lname, frames, ticks in stack_specs:
            tiles_col = []
            for tx in range(GW):
                col = []
                for ty in range(GH):
                    locs = [reg_tile(fr[ty * 8 : ty * 8 + 8, tx * 8 : tx * 8 + 8]) for fr in frames]
                    if all(lc == (-1, -1) for lc in locs):
                        col.append({"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1})
                    else:
                        if all(lc == locs[0] for lc in locs):
                            frs = [{"Sheet": sheet_name, "TexLoc": {"X": locs[0][0], "Y": locs[0][1]}, "Flip": 0}]
                            fl = 1
                        else:
                            frs = [
                                {"Sheet": sheet_name, "TexLoc": {"X": lx, "Y": ly}, "Flip": 0}
                                if lx >= 0
                                else {"Sheet": "", "TexLoc": {"X": 0, "Y": 0}, "Flip": 0}
                                for lx, ly in locs
                            ]
                            fl = int(ticks)
                        col.append({
                            "AutoTileset": "",
                            "Associates": [],
                            "Layers": [{"Frames": frs, "FrameLength": fl, "Blend": False}],
                            "NeighborCode": -1,
                        })
                tiles_col.append(col)
            layers_json.append({"Name": lname, "Layer": 0, "Visible": True, "Tiles": tiles_col})

        save_dedup_tile_sheet(tile_dir / f"{sheet_name}.tile", 8, sheet_imgs)

        seed_h = hashlib.md5(stem.encode()).hexdigest()[:16]
        _ = seed_h
        ground_doc = {
            "Version": "0.8.12.0",
            "Object": {
                "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
                "TexSize": 1,
                "Name": {"DefaultText": f"Étang du Doyen ({amb_fr})", "LocalTexts": {"fr": f"Étang du Doyen ({amb_fr})"}},
                "Released": True,
                "Comment": f"Étang du Doyen {W}x{H} ({amb_fr}) 100% Reverie Town + CanyonCamp + nage Grand Doyen",
                "rand": {"$type": "RogueElements.ReRandom, RogueElements", "FirstSeed": 0, "s": RERANDOM_STATE},
                "Status": {},
                "Background": {"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []},
                "BlankBG": {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1},
                "AssetName": stem,
                "Music": "Luminous Spring.ogg",
                "EdgeView": 1,
                "NoSwitching": False,
                "ViewCenter": None,
                "ViewOffset": {"X": 0, "Y": 0},
                "ActiveChar": None,
                "Decorations": [
                    {
                        "Name": "Nage_Grand_Doyen",
                        "Layer": 0,
                        "Visible": False,
                        "Anims": [
                            {
                                "MapLoc": {"X": ripple_x, "Y": ripple_y},
                                "ObjectAnim": {
                                    "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
                                    "AnimIndex": ripple_sheet,
                                    "FrameTime": 10,
                                    "StartFrame": -1,
                                    "EndFrame": -1,
                                    "AnimDir": 0,
                                    "Alpha": 255,
                                    "AnimFlip": 0,
                                },
                            }
                        ],
                    }
                ],
                "Layers": layers_json,
                "obstacles": obs_json,
                "Entities": [
                    {
                        "Name": "New EntLayer",
                        "Visible": True,
                        "MapChars": [],
                        "GroundObjects": [],
                        "Spawners": [],
                        "Markers": [
                            make_marker("Main_Entrance_Marker", entry_px[0], entry_px[1], 4),
                            make_marker("entrance", entry_px[0], entry_px[1], 4),
                            make_marker("centre_pierre", goal_px[0], goal_px[1], 0),
                            make_marker("grand_doyen", doyen_px[0], doyen_px[1], 6),
                        ],
                    }
                ],
            },
        }
        (ground_dir / f"{stem}.rsground").write_text(
            json.dumps(ground_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
        print(f"  [OK] {stem}: {len(sheet_imgs)} tiles -> {sheet_name}.tile + {ripple_sheet}.dir")

    etang_stems = [f"etangdudoyen_{amb}" for amb, _, _, _ in DESTINY_AMBIANCES]
    z_doc = json.loads(zone_path.read_text(encoding="utf-8-sig"))
    orig_gmaps = list(z_doc["Object"]["GroundMaps"])
    if all(m in orig_gmaps for m in etang_stems):
        gmaps = orig_gmaps
    else:
        gmaps = [m for m in orig_gmaps if m not in etang_stems]
        insert_at = next((orig_gmaps.index(m) for m in etang_stems if m in orig_gmaps), None)
        if insert_at is None and "crossroadreverietown2" in gmaps:
            insert_at = gmaps.index("crossroadreverietown2") + 1
        if insert_at is not None:
            gmaps[insert_at:insert_at] = etang_stems
        else:
            gmaps.extend(etang_stems)
    z_doc["Object"]["GroundMaps"] = gmaps
    zone_path.write_text(json.dumps(z_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    zidx = json.loads(zidx_path.read_text(encoding="utf-8-sig"))
    zidx["Object"]["reverie"]["Grounds"] = gmaps
    zidx_path.write_text(json.dumps(zidx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    build_idx = repo_root / "tools/build_tile_index.py"
    if build_idx.is_file():
        subprocess.run([sys.executable, str(build_idx)], cwd=repo_root, check=True)


def ensure_refs():
    if not PROJET.exists():
        subprocess.run(
            ["git", "clone", "--depth", "1", "--quiet", "https://github.com/meromoonmeri/projet-creation-pmdo.git", str(PROJET)],
            check=True,
        )
    if not T7_PATH.exists():
        T7_PATH.parent.mkdir(parents=True, exist_ok=True)
        tl = T7_PATH.with_suffix(".tile")
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/PMUniverse/PMU-Client/c25c01f9879369647cd5a19731b2e4e5acd33e67/resources/GFX/Tiles/Tiles7.tile",
            tl,
        )
        raw = tl.read_bytes()
        w, h = struct.unpack_from("<ii", raw, 0)
        tc = (w // 32) * (h // 32)
        ds = 8 + tc * 12
        t7 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cols = w // 32
        for i in range(tc):
            off, sz = struct.unpack_from("<qi", raw, 8 + i * 12)
            if sz > 0:
                t7.paste(Image.open(io.BytesIO(raw[ds + off : ds + off + sz])).convert("RGBA"), ((i % cols) * 32, (i // cols) * 32))
        t7.save(T7_PATH)
    base_tile_url = "https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/wip/reverie-integration-kingambit-cafe/game/Content/Tile"
    for p_out, t_name in [
        (APC_PATH, "Altere_Pond_Cliffs"),
        (RTB_PATH, "Reverie_Town_Base"),
        (RTC_PATH, "Reverie_Town_Cliffs"),
        (RTA_PATH, "Reverie_Town_Animation_Tileset"),
    ]:
        if not p_out.exists():
            p_out.parent.mkdir(parents=True, exist_ok=True)
            tl = p_out.with_suffix(".tile")
            urllib.request.urlretrieve(f"{base_tile_url}/{t_name}.tile", tl)
            _decode_pmdo_tile(tl, p_out)
    if not CC_CLEAN_PATH.exists():
        CC_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        persisted_cc = ROOT / "beach_reverie_work/cc_clean_cliffs.png"
        if persisted_cc.exists():
            shutil.copyfile(persisted_cc, CC_CLEAN_PATH)
        else:
            raw_cc_url = "https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/wip/reverie-integration-kingambit-cafe/base"
            local_base = Path("/var/tmp/pmdo_repo/base")
            rs_p = local_base / "Data/Ground/canyon_camp.rsground"
            tl_p = local_base / "Content/Tile/CanyonCamp.tile"
            if not rs_p.exists():
                rs_p = CC_CLEAN_PATH.with_name("canyon_camp.rsground")
                urllib.request.urlretrieve(f"{raw_cc_url}/Data/Ground/canyon_camp.rsground", rs_p)
            if not tl_p.exists():
                tl_p = CC_CLEAN_PATH.with_name("CanyonCamp.tile")
                urllib.request.urlretrieve(f"{raw_cc_url}/Content/Tile/CanyonCamp.tile", tl_p)
            raw_tl = tl_p.read_bytes()
            ts, cnt = struct.unpack_from("<ii", raw_tl, 0)
            pos_map = {}
            off = 8
            for _ in range(cnt):
                tx, ty, pos = struct.unpack_from("<iiq", raw_tl, off)
                off += 16
                pos_map[(tx, ty)] = pos
            dec_tiles = {}
            rs_obj = json.loads(rs_p.read_text(encoding="utf-8-sig"))["Object"]
            l0 = rs_obj["Layers"][0]["Tiles"]
            nx_c, ny_c = len(l0), len(l0[0])
            c0 = Image.new("RGBA", (nx_c * ts, min(275, ny_c * ts)), (0, 0, 0, 0))
            for tx in range(nx_c):
                for ty in range(min(275 // ts + 1, ny_c)):
                    for tl_wrap in l0[tx][ty].get("Layers", []):
                        frames = tl_wrap.get("Frames", [])
                        if not frames:
                            continue
                        fr = frames[0]
                        k = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                        if k not in dec_tiles:
                            p_t = pos_map.get(k)
                            if p_t is None:
                                dec_tiles[k] = Image.new("RGBA", (ts, ts), (0, 0, 0, 0))
                            else:
                                pl = struct.unpack_from("<q", raw_tl, p_t)[0]
                                im_t = Image.open(io.BytesIO(raw_tl[p_t + 8 : p_t + 8 + pl])).convert("RGBA")
                                a_t = np.array(im_t, dtype=np.uint16)
                                al = a_t[:, :, 3:4]
                                m_t = al[:, :, 0] > 0
                                for ch in range(3):
                                    a_t[:, :, ch][m_t] = np.minimum(255, (a_t[:, :, ch][m_t] * 255 + al[:, :, 0][m_t] // 2) // al[:, :, 0][m_t])
                                dec_tiles[k] = Image.fromarray(a_t.astype(np.uint8), "RGBA")
                        if ty * ts < 275:
                            c0.alpha_composite(dec_tiles[k], (tx * ts, ty * ts))
            arr_cc = np.array(c0.crop((0, 0, 1152, 275)))
            r_cc, g_cc, b_cc = arr_cc[:, :, 0].astype(int), arr_cc[:, :, 1].astype(int), arr_cc[:, :, 2].astype(int)
            non_cliff = (g_cc > r_cc + 8) | (b_cc > r_cc + 15)
            lab_nc, _ = nd.label(non_cliff)
            edge_labels = set(lab_nc[0, :]) | set(lab_nc[-1, :]) | set(lab_nc[:, 0]) | set(lab_nc[:, -1])
            edge_labels.discard(0)
            arr_cc[np.isin(lab_nc, list(edge_labels))] = 0
            Image.fromarray(arr_cc, "RGBA").save(CC_CLEAN_PATH)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integrate-repo", type=Path, default=None, help="PMDO-Destiny checkout to update with etangdudoyen 4 ambiances + swim ripples")
    parser.add_argument("--skip-standalone", action="store_true")
    args = parser.parse_args()

    ensure_refs()
    night_fn = None

    print(f"1/6 Building expanded {W}x{H} ({GW}x{GH} tiles) 100% Reverie Town terrain & cliff-grass raccords...")
    masks, static_layers = segment_and_expand_768()
    dry_terrain = (
        (static_layers["cliffs"][:, :, 3] > 0)
        | (static_layers["grass"][:, :, 3] > 0)
        | (static_layers["path_sand"][:, :, 3] > 0)
    )

    print("2/6 Building authentic Reverie Town animated pond & Tiles7 postless cascades...")
    water_frames, d_shore, rev_sp_4f, visible_water = build_reverie_pond_and_sparkles(masks, dry_terrain)
    cascade_frames, chute_specs, cascade_union = build_pmu_cascades(masks, dry_terrain, masks["cliffs"])

    print("3/6 Building canonical 3-pose PMU foam, full Reverie Town platform/river stones & 6 sparkles...")
    foam_frames, foam_union = build_canonical_pmu_foam(
        chute_specs, visible_water, dry_terrain, cascade_union
    )
    stone_frames, stones_union, bridge_walk_mask, stone_meta = build_reverie_pond_stones(
        visible_water, dry_terrain, foam_union, cascade_union
    )
    sparkle_frames = place_reverie_sparkles(
        rev_sp_4f, visible_water, d_shore, foam_union, cascade_union, stones_union
    )

    stack_specs = [
        ("01_sol_herbe_reverie",      [static_layers["sol_complet"]], 60),
        ("02_eau_reverie_animee",     water_frames,                   10),
        ("03_scintillements_reverie", sparkle_frames,                 10),
        ("04_herbe_reverie",          [static_layers["grass"]],       60),
        ("05_chemin_sable_reverie",   [static_layers["path_sand"]],   60),
        ("06_rochers_etang_reverie",  stone_frames,                    5),
        ("07_cascades_pmu_reverie",   cascade_frames,                  5),
        ("08_falaises_reverie",       [static_layers["cliffs"]],      60),
        ("09_ecume_pmu_canonique",    foam_frames,                    10),
    ]

    print("4/6 Composing 24-frame scene & verifying full opacity + zero residual magenta...")
    scenes_jour = []
    for f_idx in range(N_FRAMES):
        tick = f_idx * 5
        p4 = (tick // 10) % 4
        p3 = (tick // 10) % 3
        p8 = (tick // 5) % 8
        comp = Image.new("RGBA", (W, H))
        for lname, frames, _ in stack_specs:
            if len(frames) == 1:
                idx = 0
            elif len(frames) == 4:
                idx = p4
            elif len(frames) == 3:
                idx = p3
            elif len(frames) == 8:
                idx = p8
            else:
                raise RuntimeError(lname)
            comp.alpha_composite(Image.fromarray(frames[idx]))
        arr = np.array(comp)
        assert np.all(arr[:, :, 3] == 255), f"Transparent pixel leaked in frame {f_idx}!"
        r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
        mag_leak = ((r > g * 1.45) & (b > g * 1.32) & (r > 135) & (b > 125)).sum()
        assert mag_leak == 0, f"Magenta pixel leaked: {mag_leak}"
        scenes_jour.append(comp)

    day_png = ROOT / "apercu_whiscash_pond_layout_reverie_jour.png"
    scenes_jour[0].save(day_png)

    gif_path = ROOT / "apercu_whiscash_pond_layout_reverie_anime.gif"
    scenes_jour[0].save(
        gif_path, save_all=True, append_images=scenes_jour[1:],
        duration=FRAME_DURATIONS_MS, loop=0, disposal=2,
    )

    amb_modes = [(amb, lbl_fr) for amb, _, lbl_fr, _ in DESTINY_AMBIANCES]
    sheet_4 = Image.new("RGBA", (W * 2, H * 2))
    dr4 = ImageDraw.Draw(sheet_4)
    for idx_a, (mode, label) in enumerate(amb_modes):
        im_a = apply_ambiance(scenes_jour[0], mode, night_fn)
        px = (idx_a % 2) * W
        py = (idx_a // 2) * H
        sheet_4.alpha_composite(im_a, (px, py))
        dr4.rectangle([px + 6, py + 6, px + 116, py + 28], fill=(16, 22, 32, 200))
        dr4.text((px + 12, py + 11), label, fill=(245, 240, 210, 255))
    sheet_4.save(ROOT / "apercu_whiscash_pond_layout_reverie_4_ambiances.png")

    z = Image.new("RGB", (W, H), (20, 24, 30))
    j_rgb = scenes_jour[0].convert("RGB")
    crops = [
        j_rgb.crop((140, 0, 524, 288)),
        j_rgb.crop((0, 240, 384, 528)),
        j_rgb.crop((384, 240, 768, 528)),
        j_rgb.crop((192, 180, 576, 468)),
    ]
    for idx_c, cr in enumerate(crops):
        z.paste(cr, ((idx_c % 2) * (W // 2), (idx_c // 2) * (H // 2)))
    z.save("/var/tmp/verify_layout_reverie_zooms.png")

    print("5/6 Exporting multicalque .ora, calques ZIP & verifying 16x16 BFS collisions...")
    ora_layers = [(lname + ("_f0" if len(fr) > 1 else ""), fr[0]) for lname, fr, _ in stack_specs]
    write_ora(ROOT / "whiscash_pond_layout_reverie_multicalque.ora", ora_layers, scenes_jour[0])

    calques_zip = ROOT / "whiscash_pond_layout_reverie_calques.zip"
    manifest_layers = []
    with zipfile.ZipFile(calques_zip, "w", zipfile.ZIP_DEFLATED) as zc:
        for lname, frames, ticks in stack_specs:
            if len(frames) == 1:
                fn = f"calques/{lname}.png"
                zc.writestr(fn, png_bytes(Image.fromarray(frames[0])))
                manifest_layers.append({"name": lname, "animated": False, "file": fn})
            else:
                flist = []
                for p, fr in enumerate(frames):
                    fn = f"calques/{lname}_f{p:02d}.png"
                    zc.writestr(fn, png_bytes(Image.fromarray(fr)))
                    flist.append(fn)
                manifest_layers.append({
                    "name": lname, "animated": True, "frame_length_ticks": ticks, "frames": flist,
                })
        zc.writestr(
            "manifest.json",
            json.dumps({
                "size": [W, H],
                "grid_cells": [GW, GH],
                "master_frames": N_FRAMES,
                "master_ticks": 120,
                "durations_ms": FRAME_DURATIONS_MS,
                "water_palette_source": "Reverie Town native pond water (#80D8E0/#68C8E0/#58B0C8/#5080B8/#9CEAF6) & Reverie cascade ramp (#5787BF..#F7FFFF)",
                "path_style_source": "Metano_Town_Base sandy path (no paw print)",
                "grass_cliff_raccord_source": "Reverie_Town_Base + Reverie_Town_Cliffs + CanyonCamp elevated cliff-grass raccords",
                "cascades_pmu": [
                    {"name": s["name"], "cx": s["cx"], "y_top": s["y_top"], "y_foot": s["y_foot"]}
                    for s in chute_specs
                ],
                "layers": manifest_layers,
            }, indent=2),
        )

    walkable_px = (static_layers["grass"][:, :, 3] > 0) | (static_layers["path_sand"][:, :, 3] > 0) | bridge_walk_mask
    blocking_px = (
        visible_water
        | cascade_union
        | foam_union
        | (static_layers["cliffs"][:, :, 3] > 0)
    ) & ~bridge_walk_mask
    walk_clean = walkable_px & ~blocking_px
    blocked = (~walk_clean).reshape(GH, 8, GW, 8).mean((1, 3)) > 0.25
    r_top = max(0, (stone_meta["y_plat"] + 8) // 8)
    r_bot = min(GH, (stone_meta["y_dock"] + 8) // 8)
    blocked[r_top:r_bot, GW // 2 - 1 : GW // 2 + 1] = False

    mid_c = GW // 2
    entry_c = min((c for c in range(GW - 1) if not blocked[GH - 2 :, c : c + 2].any()), key=lambda c: abs(c - (mid_c - 1)))
    entry_cell = (GH - 2, entry_c)
    entry_px = (entry_c * 8, (GH - 2) * 8)

    plat_r_t = max(0, (stone_meta["y_plat"] + 16) // 8)
    plat_cells = [
        (r, c)
        for r in range(plat_r_t - 1, plat_r_t + 4)
        for c in range(mid_c - 4, mid_c + 4)
        if not blocked[r : r + 2, c : c + 2].any()
    ]
    goal_cell = min(plat_cells, key=lambda rc: abs(rc[0] - plat_r_t) * 2 + abs(rc[1] - (mid_c - 1)))
    goal_px = (goal_cell[1] * 8, goal_cell[0] * 8)
    ok_bfs = bfs_16x16(blocked, entry_cell, goal_cell)
    assert ok_bfs, f"BFS failed from {entry_cell} to {goal_cell}!"

    doyen_x_cand = ((W // 2 - stone_meta["dx_in"] - 8) // 8) * 8
    doyen_y_cand = ((stone_meta["y_sing_in"] + 36) // 8) * 8
    doyen_px = (doyen_x_cand, doyen_y_cand)
    swim_4f = build_swim_ripple_4f()

    col_vis = scenes_jour[0].copy()
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for r_i, c_i in zip(*np.nonzero(blocked)):
        dr.rectangle([c_i * 8, r_i * 8, c_i * 8 + 7, r_i * 8 + 7], fill=(220, 40, 40, 86))
    dr.rectangle([entry_px[0], entry_px[1], entry_px[0] + 15, entry_px[1] + 15], outline=(255, 230, 40, 255), width=2)
    dr.rectangle([goal_px[0], goal_px[1], goal_px[0] + 15, goal_px[1] + 15], outline=(60, 230, 255, 255), width=2)
    dr.rectangle([doyen_px[0], doyen_px[1], doyen_px[0] + 15, doyen_px[1] + 15], outline=(180, 140, 255, 255), width=2)
    dr.rectangle([doyen_px[0] - 8, doyen_px[1] + 4, doyen_px[0] + 23, doyen_px[1] + 19], outline=(110, 210, 255, 220), width=1)
    col_vis.alpha_composite(ov)
    col_vis.save(ROOT / "apercu_whiscash_pond_layout_reverie_collisions_marqueurs.png")

    if args.integrate_repo is not None:
        print(f"6a/6 Integrating 4 ambiances + swim ripples into {args.integrate_repo}...")
        integrate_destiny_repo(args.integrate_repo, stack_specs, blocked, entry_px, goal_px, doyen_px, swim_4f)

    if args.skip_standalone:
        shutil.rmtree(STAGE, ignore_errors=True)
        return

    print("6/6 Packaging PMDO 0.8.12 project & interactive HTML viewer...")
    bank_counts = build_pmdo_pack(stack_specs, blocked, entry_px, goal_px, doyen_px, swim_4f)

    def webp_bytes(im: Image.Image) -> bytes:
        buf = io.BytesIO()
        im.save(buf, format="WEBP", lossless=True, quality=100)
        return buf.getvalue()

    amb_frames_uri = {}
    for mode, label in amb_modes:
        mode_imgs = [apply_ambiance(fr, mode, night_fn) for fr in scenes_jour]
        b = io.BytesIO()
        mode_imgs[0].save(
            b, format="WEBP", save_all=True, append_images=mode_imgs[1:],
            duration=FRAME_DURATIONS_MS, loop=0, lossless=True
        )
        amb_frames_uri[mode] = {
            "label": label,
            "gif": data_uri(b.getvalue(), "image/webp"),
            "frames": [data_uri(webp_bytes(im), "image/webp") for im in mode_imgs],
        }

    layer_items = []
    for lname, frames, ticks in stack_specs:
        if len(frames) == 1:
            layer_items.append({"name": f"{lname} (statique)", "src": data_uri(webp_bytes(Image.fromarray(frames[0])), "image/webp")})
        else:
            ims = [Image.fromarray(f) for f in frames]
            b = io.BytesIO()
            d_ms = round(ticks * 1000 / 60)
            ims[0].save(
                b, format="WEBP", save_all=True, append_images=ims[1:],
                duration=d_ms, loop=0, lossless=True
            )
            layer_items.append({
                "name": f"{lname} ({len(frames)} poses x {ticks} ticks)",
                "src": data_uri(b.getvalue(), "image/webp"),
            })
    swim_preview_frames = []
    rx, ry = doyen_px[0] - 8, doyen_px[1] + 4
    for f_idx, fr in enumerate(scenes_jour):
        p4 = ((f_idx * 5) // 10) % 4
        c_sw = fr.copy()
        c_sw.alpha_composite(Image.fromarray(swim_4f[p4]), (rx, ry))
        swim_preview_frames.append(c_sw)
    b_sw = io.BytesIO()
    swim_preview_frames[0].save(
        b_sw, format="WEBP", save_all=True, append_images=swim_preview_frames[1:],
        duration=FRAME_DURATIONS_MS, loop=0, lossless=True
    )
    layer_items.append({
        "name": f"Nage Grand Doyen — Etang_Nage_Ondes (4x10 ticks @ {rx},{ry})",
        "src": data_uri(b_sw.getvalue(), "image/webp"),
    })
    layer_items.append({
        "name": "Collisions & marqueurs (BFS 16x16 OK)",
        "src": data_uri(webp_bytes(col_vis), "image/webp"),
    })

    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Étang du Doyen — 100% Rêverie Town ({W}×{H}, PMDO 0.8.12)</title>
<style>
  :root {{ --bg:#131b24; --panel:#1b2633; --line:#2d3d4f; --text:#ecf2f7; --muted:#9db0c3; --acc:#5fb7cf; }}
  body {{ margin:0; padding:24px; background:var(--bg); color:var(--text); font:14px/1.55 system-ui, sans-serif; }}
  .wrap {{ max-width:1600px; margin:0 auto; }}
  h1 {{ margin:0 0 6px; font-size:20px; }}
  .sub {{ color:var(--muted); margin-bottom:16px; }}
  .bar {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; background:var(--panel); border:1px solid var(--line); padding:10px 12px; border-radius:8px; margin-bottom:14px; }}
  button, select {{ background:#243344; color:var(--text); border:1px solid #395069; border-radius:6px; padding:6px 10px; cursor:pointer; font:inherit; }}
  button.active {{ border-color:var(--acc); color:#83dae6; font-weight:600; }}
  .stage {{ position:relative; display:inline-block; border:1px solid var(--line); border-radius:6px; overflow:hidden;
            background:repeating-conic-gradient(#1d2834 0 25%,#263544 0 50%) 0/16px 16px; }}
  .stage img {{ display:block; image-rendering:pixelated; image-rendering:crisp-edges; }}
  .grid-ov {{ position:absolute; inset:0; pointer-events:none; display:none;
              background-image:linear-gradient(to right,rgba(255,255,255,.18) 1px,transparent 1px),
                               linear-gradient(to bottom,rgba(255,255,255,.18) 1px,transparent 1px); }}
  .grid-ov.on {{ display:block; }}
  .meta {{ margin-top:12px; color:var(--muted); font-size:13px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Étang du Doyen — Rêverie Town × Canyon Camp × Metano ({W}×{H}, 1×1 zéro mixel)</h1>
  <div class="sub">Zone agrandie ({GW}×{GH} tuiles 8×8) · Raccords cliff-grass en altitude style Canyon Camp · Chemin sableux Metano Town (sans patte) · Eau &amp; 3 cascades couleur Rêverie Town (animations conservées) · Plateforme &amp; 4 river stones animées (8×5 ticks) + écume canonique 3 poses</div>

  <div class="bar">
    <label>Vue :
      <select id="viewMode">
        <option value="scene">Scène animée (4 ambiances)</option>
        <option value="layer">Inspecteur multicalque</option>
      </select>
    </label>
    <label id="ambWrap">Ambiance :
      <select id="ambSel">
        <option value="jour">Jour</option>
        <option value="aube">Aube</option>
        <option value="crepuscule">Crépuscule</option>
        <option value="nuit">Nuit</option>
      </select>
    </label>
    <label id="layWrap" style="display:none">Calque :
      <select id="laySel"></select>
    </label>
    <button id="playBtn" class="active">Animation (boucle 24 frames)</button>
    <button id="prevBtn">◀ -1</button>
    <button id="nextBtn">+1 ▶</button>
    <span id="frameInfo" style="min-width:98px;color:#83dae6">GIF 24 frames</span>
    <label>Zoom :
      <select id="zoomSel">
        <option value="1">1× ({W}×{H})</option>
        <option value="2" selected>2× ({W*2}×{H*2})</option>
        <option value="3">3× ({W*3}×{H*3})</option>
      </select>
    </label>
    <button id="gridBtn">Grille 8×8</button>
  </div>

  <div class="stage">
    <img id="preview" alt="Étang du Doyen 100% Rêverie Town" width="{W*2}" height="{H*2}">
    <div id="gridOv" class="grid-ov"></div>
  </div>

  <div class="meta">
    Grille PMDO : {GW}×{GH} cases (TexSize=1, 8×8 px) · Cases bloquées : {int(blocked.sum())}/{GW*GH} · Chemin 16×16 entrée sud → plateforme : {"VALIDÉ" if ok_bfs else "ÉCHEC"} · Banques .tile : {len(bank_counts)}
  </div>
</div>
<script>
const AMB = {json.dumps(amb_frames_uri)};
const LAYERS = {json.dumps(layer_items)};
const W = {W}, H = {H};
const viewMode = document.getElementById('viewMode');
const ambWrap = document.getElementById('ambWrap');
const ambSel = document.getElementById('ambSel');
const layWrap = document.getElementById('layWrap');
const laySel = document.getElementById('laySel');
const playBtn = document.getElementById('playBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const frameInfo = document.getElementById('frameInfo');
const zoomSel = document.getElementById('zoomSel');
const gridBtn = document.getElementById('gridBtn');
const preview = document.getElementById('preview');
const gridOv = document.getElementById('gridOv');

LAYERS.forEach((x, i) => laySel.add(new Option(x.name, i)));
let playing = true, fidx = 0;

function applyZoom() {{
  const z = +zoomSel.value;
  preview.width = W * z;
  preview.height = H * z;
  gridOv.style.backgroundSize = (8 * z) + 'px ' + (8 * z) + 'px';
}}

function render() {{
  if (viewMode.value === 'layer') {{
    ambWrap.style.display = 'none';
    layWrap.style.display = '';
    playBtn.style.display = prevBtn.style.display = nextBtn.style.display = frameInfo.style.display = 'none';
    preview.src = LAYERS[+laySel.value].src;
  }} else {{
    ambWrap.style.display = '';
    layWrap.style.display = 'none';
    playBtn.style.display = prevBtn.style.display = nextBtn.style.display = frameInfo.style.display = '';
    const m = AMB[ambSel.value];
    if (playing) {{
      preview.src = m.gif;
      playBtn.classList.add('active');
      frameInfo.textContent = 'GIF 24 frames';
    }} else {{
      preview.src = m.frames[fidx];
      playBtn.classList.remove('active');
      frameInfo.textContent = 'Frame ' + (fidx + 1) + ' / 24';
    }}
  }}
}}

viewMode.onchange = render;
ambSel.onchange = render;
laySel.onchange = render;
zoomSel.onchange = applyZoom;
playBtn.onclick = () => {{ playing = !playing; render(); }};
prevBtn.onclick = () => {{ playing = false; fidx = (fidx + 23) % 24; render(); }};
nextBtn.onclick = () => {{ playing = false; fidx = (fidx + 1) % 24; render(); }};
gridBtn.onclick = () => {{ gridBtn.classList.toggle('active'); gridOv.classList.toggle('on'); }};
applyZoom();
render();
</script>
</body>
</html>
"""
    (ROOT / "apercu_whiscash_pond_layout_reverie.html").write_text(html, encoding="utf-8")

    print("DONE!")
    print("  Size:", W, "x", H, f"({GW}x{GH} cells)")
    print("  Blocked:", int(blocked.sum()), "/", GW * GH, "| BFS 16x16:", ok_bfs)
    print("  Tile banks:", bank_counts)
    print("  Chutes:", [(s["name"], s["cx"], s["y_top"], s["y_foot"], s["gorge_w"]) for s in chute_specs])
    print("  Markers:", {"entry_px": entry_px, "goal_px": goal_px, "doyen_px": doyen_px})
    shutil.rmtree(STAGE, ignore_errors=True)


if __name__ == "__main__":
    main()
