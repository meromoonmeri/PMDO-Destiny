#!/usr/bin/env python3
"""Reconstruction de l'intérieur `dojo_kingambit` selon `METHODE_MAGENTA_ET_GENERATEUR.md` (projet-creation-pmdo).

Référence canonique fournie : salle souterraine PMD Explorers of Sky (parois rocheuses ocre-brun, sol sableux
avec couloir sud, palissades épineuses inclinées tenues par cordages et ronces, sceau circulaire central à runes
orange, deux cristaux cyan sur piédestal, rainures en L avec blocs gravés, braseros de pierre sculptés et porte
circulaire sarcelle enchaînée sous emblème solaire), adaptée en format 4:3 spacieux (768 x 576 px, 96 x 72 cases
de 8 px) avec DEUX portes scellées symétriques au mur nord.

Pipeline conforme à `METHODE_MAGENTA_ET_GENERATEUR.md` :
1. `bruts/decor_magenta.png` (1200 x 896) sur fond magenta #FF00FF + `bruts/sol_complet.png` (1200 x 896).
2. Détourage `key()` par rapport de canaux + dilatation 2 px de la frange antialiasée, assertion 0 pixel magenta.
3. Réduction uniforme non mélangeante `1200 x 896 -> 768 x 576` (`SCALE = 576 / 896`, `BOX` pondéré par masque).
4. Unification des dômes de pierre sculptée des 5 braseros nord + palette commune 96 couleurs (`MEDIANCUT`, sans dither).
5. Contrôle `fidelity()` (même classifieur matière sur le rip canonique et le décor quantifié, seuil bloquant < 35).
6. Découpe exacte en 9 calques PMDO (`TexSize = 1`, `EdgeView = 1`) :
   - `00 sol complet` (`Layer = 0`)
   - `01 sol` (`Layer = 0`)
   - `02 ombres` (`Layer = 0`)
   - `03 parois` (`Layer = 0`)
   - `04 blocs` (`Layer = 0`)
   - `05 flammes braseros 12 phases` (`Layer = 0`, 12 x 6 ticks, palette et forme canoniques EoS)
   - `06 reflets cristaux 12 phases` (`Layer = 0`, 12 x 6 ticks, onde facettes + éclats)
   - `07 lueur sceau 12 phases` (`Layer = 0`, 12 x 6 ticks, pulsation ambrée des runes)
   - `08 Vos elements avant-plan (Top)` (`Layer = 4`, ronces et cordages suspendus devant les personnages)
7. Encodage `.tile` RogueEssence (alpha prémultiplié, case `(0, 0)` transparente dédiée, déduplication native)
   dans `game/Content/Tile/Kingambit_Dojo_Interieur.tile` et écriture de `game/Data/Ground/dojo_kingambit.rsground`.
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
TILE_OUT = ROOT / "game/Content/Tile/Kingambit_Dojo_Interieur.tile"
GROUND_OUT = ROOT / "game/Data/Ground/dojo_kingambit.rsground"
SHEET_NAME = "Kingambit_Dojo_Interieur"

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

# Palette exacte des flammes relevée sur le rip canonique (IMG_5225.png)
FLAME_CMAP = {
    "W": (255, 247, 135),
    "Y": (255, 223, 7),
    "O": (255, 159, 0),
    "R": (247, 87, 7),
    "r": (247, 15, 7),
    "c": (207, 79, 55),
}

# Sprite exact 16x37 de la flamme canonique EoS relevé sur IMG_5225.png (x=150..166, y=113..150)
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
    """Détourage `key()` de `METHODE_MAGENTA_ET_GENERATEUR.md` §3 (+ dilatation 2 px de frange)."""
    r, g, b = rgb_arr.transpose(2, 0, 1).astype(float)
    bg = (r > 70) & (b > 70) & (r > g * 1.45) & (b > g * 1.45)
    fringe = nd.binary_dilation(bg, iterations=2) & (r > g * 1.05) & (b > g * 1.05)
    return bg | fringe


def resize_plane(plane: np.ndarray) -> np.ndarray:
    im = Image.fromarray(plane.astype(np.float32), mode="F")
    resized = np.array(im.resize((SCALED_W, H), Image.Resampling.BOX))
    return resized[:, CROP_X : CROP_X + W]


def down_masked(rgb_arr: np.ndarray, fg_src: np.ndarray):
    """Réduction uniforme 1200x896 -> 768x576 sans mélange avec le fond magenta."""
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


def unify_brazier_domes(decor_rgb: np.ndarray) -> np.ndarray:
    """Unifie les 3 braseros centraux avec le dôme de pierre sculpté canonique du brasero 1."""
    out = decor_rgb.copy()
    # Brasero 1 (cx=126, cy=136) possède exactement le dôme plein sculpté du rip canonique.
    src_patch = out[106:164, 96:156].copy()  # 58 x 60, centre (29, 30)
    py, px = np.mgrid[:58, :60]
    dist = np.sqrt(((px - 30.0) / 28.5) ** 2 + ((py - 29.0) / 26.5) ** 2)
    alpha = np.clip((1.04 - dist) / 0.12, 0.0, 1.0)[..., None]
    for tcx, tcy, flip in [(298, 136, False), (385, 138, True), (470, 136, True)]:
        patch = src_patch[:, ::-1] if flip else src_patch
        y0, x0 = tcy - 29, tcx - 30
        dst = out[y0 : y0 + 58, x0 : x0 + 60].astype(np.float32)
        out[y0 : y0 + 58, x0 : x0 + 60] = np.clip(
            np.round(dst * (1.0 - alpha) + patch.astype(np.float32) * alpha), 0, 255
        ).astype(np.uint8)
    return out


def quantize_shared_96(decor_rgb: np.ndarray, fg_mask: np.ndarray, sol_rgb: np.ndarray):
    """Palette commune 96 couleurs (MEDIANCUT, sans tramage) selon `METHODE_MAGENTA_ET_GENERATEUR.md` §6,
    avec stratification terrain (56) + accents portes sarcelle / cristaux cyan / runes orange / ronces (40)
    pour éviter que le sable majoritaire n'écrase les teintes minoritaires."""
    r, g, b = decor_rgb.transpose(2, 0, 1).astype(float)
    is_teal = fg_mask & (g > r + 6) & (b >= r - 6) & (b < 148)
    is_cyan = fg_mask & (b > r * 1.35) & (b > 125)
    is_orange = fg_mask & (r > 165) & (r > g * 1.2) & (g > b * 1.3)
    is_vine = fg_mask & (g > r + 5) & (g > b + 14)
    accent_m = is_teal | is_cyan | is_orange | is_vine
    terrain_m = fg_mask & ~accent_m

    pal_t_im = Image.fromarray(
        np.concatenate([decor_rgb[terrain_m], sol_rgb[fg_mask]], axis=0).reshape(-1, 1, 3), mode="RGB"
    ).quantize(56, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal_t = np.array(pal_t_im.getpalette()[: 56 * 3], dtype=np.uint8).reshape(56, 3)

    pal_a_im = Image.fromarray(decor_rgb[accent_m].reshape(-1, 1, 3), mode="RGB").quantize(
        40, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE
    )
    pal_a = np.array(pal_a_im.getpalette()[: 40 * 3], dtype=np.uint8).reshape(40, 3)

    pal = np.concatenate([pal_t, pal_a], axis=0)  # exactement 96 couleurs
    assert pal.shape == (96, 3)
    pal_im = Image.new("P", (1, 1))
    flat_pal = list(pal.ravel()) + list(pal[0]) * (256 - 96)
    pal_im.putpalette(flat_pal)

    q_decor_idx = np.array(Image.fromarray(decor_rgb, mode="RGB").quantize(palette=pal_im, dither=Image.Dither.NONE))
    q_decor = pal[q_decor_idx]
    q_decor[~fg_mask] = 0

    q_sol_idx = np.array(Image.fromarray(sol_rgb, mode="RGB").quantize(palette=pal_im, dither=Image.Dither.NONE))
    q_sol = pal[q_sol_idx]
    q_sol[~fg_mask] = 0
    return q_decor, q_sol


def classify_materials_for_fidelity(rgb_arr: np.ndarray, valid_mask: np.ndarray) -> dict:
    """Même classifieur de matières appliqué au rip canonique et au décor quantifié (§8 `fidelity()`)."""
    r, g, b = rgb_arr.transpose(2, 0, 1).astype(float)
    lum = rgb_arr @ np.array([0.299, 0.587, 0.114])
    # Exclure les flammes du rip si présentes (rouge/jaune vif B < 50, R > 200)
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


def check_fidelity(q_decor: np.ndarray, fg_mask: np.ndarray) -> dict:
    ref_rgba = np.array(Image.open(ART / "ref_canon_rgba.png").convert("RGBA"))
    ref_rgb = ref_rgba[..., :3]
    ref_valid = ref_rgba[..., 3] > 0
    fr = classify_materials_for_fidelity(ref_rgb, ref_valid)
    fd = classify_materials_for_fidelity(q_decor, fg_mask)
    report = {}
    for mat in fr:
        assert fr[mat].sum() > 50 and fd[mat].sum() > 50, (mat, int(fr[mat].sum()), int(fd[mat].sum()))
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


def partition_static_layers(q_decor: np.ndarray, fg_mask: np.ndarray) -> dict:
    """Découpe exacte et sans chevauchement de `q_decor` en `01 sol`, `02 ombres`, `03 parois`, `04 blocs`, `08 top`."""
    yy, xx = np.mgrid[:H, :W]
    r, g, b = q_decor.transpose(2, 0, 1).astype(float)
    lum = q_decor @ np.array([0.299, 0.587, 0.114])

    # 1. Calque 08 Top (DrawLayer=4) : ronces épineuses suspendues et extrémités hautes des cordages aux coins nord
    green_vines = fg_mask & (yy < 166) & ((xx < 252) | (xx > 516)) & (g > r + 5) & (g > b + 14)
    green_vines = keep_large(nd.binary_closing(green_vines, iterations=1), 18)
    vine_with_outline = nd.binary_dilation(green_vines, iterations=1) & fg_mask & (yy < 168)
    # Cordages hauts dépassant au-dessus de la paroi rocheuse (yy < 95 dans les coins)
    high_ropes = fg_mask & (yy < 88) & ((xx < 185) | (xx > 583))
    mask_top = vine_with_outline | high_ropes

    rem = fg_mask & ~mask_top

    # 2. Calque 04 Blocs : les 5 braseros sculptés, 2 cristaux cyan sur socle, blocs de pierre à cœur orange, rondins
    braziers = np.zeros((H, W), dtype=bool)
    for bcx, bcy in [(126, 136), (298, 136), (385, 138), (470, 136), (643, 136)]:
        braziers |= (((xx - bcx) / 28.0) ** 2 + ((yy - bcy) / 25.5) ** 2) <= 1.0

    # Socles + cristaux cyan
    is_flat_sand = (
        (r >= 126) & (r <= 170) & (g >= 112) & (g <= 155) & (b >= 68) & (b <= 106) & ((r - g) <= 23) & ((g - b) >= 28)
    )
    crystals = (
        ((xx >= 306) & (xx <= 335) & (yy >= 205) & (yy <= 249))
        | ((xx >= 433) & (xx <= 462) & (yy >= 205) & (yy <= 249))
    ) & ~is_flat_sand

    # Blocs carrés pierre + cœur orange (haut-gauche, bas-gauche, bas-droit)
    puzzle_blocks = (
        ((xx >= 168) & (xx <= 204) & (yy >= 316) & (yy <= 362))
        | ((xx >= 242) & (xx <= 278) & (yy >= 360) & (yy <= 408))
        | ((xx >= 542) & (xx <= 578) & (yy >= 358) & (yy <= 408))
    ) & ~is_flat_sand

    # Deux rondins de bois horizontaux aux coins nord-ouest et nord-est de l'arène
    logs = (
        ((xx >= 84) & (xx <= 128) & (yy >= 158) & (yy <= 185))
        | ((xx >= 640) & (xx <= 684) & (yy >= 158) & (yy <= 185))
    ) & ~is_flat_sand

    mask_blocs = rem & (braziers | crystals | puzzle_blocks | logs)
    rem2 = rem & ~mask_blocs

    # 3. Enveloppe du sol de la grande salle + couloir sud
    floor_env = poly_mask([
        (132, 152), (636, 152),
        (666, 188), (666, 344),
        (606, 424), (446, 444),
        (442, 576), (326, 576),
        (322, 444), (162, 424),
        (102, 344), (102, 188),
    ])
    # Sceau circulaire central + arcs orange (toujours dans `01 sol`)
    seal_zone = (((xx - 384.0) / 70.0) ** 2 + ((yy - 268.0) / 72.0) ** 2) <= 1.0
    # Rainures en L et rangées de trous au nord (dans `01 sol`)
    l_grooves_and_pits = (
        ((xx >= 140) & (xx <= 276) & (yy >= 158) & (yy <= 194))
        | ((xx >= 492) & (xx <= 628) & (yy >= 158) & (yy <= 194))
        | ((xx >= 194) & (xx <= 246) & (yy >= 324) & (yy <= 408))
        | ((xx >= 514) & (xx <= 576) & (yy >= 324) & (yy <= 408))
    )

    in_floor = rem2 & (floor_env | seal_zone)
    # 4. Calque 02 Ombres : bande de sable assombri le long des parois et au pied des blocs
    near_edge = ~nd.binary_erosion(floor_env, iterations=14)
    near_blocs = nd.binary_dilation(mask_blocs, iterations=5)
    mask_ombres = (
        in_floor
        & ~seal_zone
        & ~l_grooves_and_pits
        & (near_edge | near_blocs)
        & (lum < 118)
        & (lum > 62)
    )

    mask_sol = in_floor & ~mask_ombres
    mask_parois = rem2 & ~in_floor

    # Vérification stricte de partition exacte (comme dans `ledian_dojo_v1/build.py`)
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
    """Construit 12 phases pixel-art nettes à partir du sprite de flamme canonique EoS 16x37."""
    fh, fw = len(CANON_FLAME_ROWS), len(CANON_FLAME_ROWS[0])
    base = np.zeros((fh, fw, 4), dtype=np.uint8)
    code_grid = np.full((fh, fw), ".", dtype="<U1")
    for y, row in enumerate(CANON_FLAME_ROWS):
        for x, ch in enumerate(row):
            if ch != ".":
                code_grid[y, x] = ch
                base[y, x] = (*FLAME_CMAP[ch], 255)

    sprites = []
    for t in range(PHASES):
        ph = 2.0 * np.pi * t / PHASES
        canvas = np.zeros((fh + 4, fw + 6, 4), dtype=np.uint8)
        for y in range(fh):
            # La base (y >= 30) reste ancrée sur le brasero ; la langue de feu ondule doucement
            height_ratio = max(0.0, (32.0 - y) / 30.0)
            dx = int(round(height_ratio * 1.45 * np.sin(ph - y * 0.24)))
            dy = int(round((height_ratio ** 1.4) * 1.15 * np.cos(2.0 * ph - y * 0.12)))
            for x in range(fw):
                ch = code_grid[y, x]
                if ch == ".":
                    continue
                # Petite respiration du cœur incandescent
                c_use = ch
                if ch == "Y" and y >= 28 and np.sin(ph + x * 0.5) > 0.55:
                    c_use = "W"
                elif ch == "W" and y <= 31 and np.sin(ph) < -0.6:
                    c_use = "Y"
                ny = np.clip(y + 2 + dy, 0, fh + 3)
                nx = np.clip(x + 3 + dx, 0, fw + 5)
                canvas[ny, nx] = (*FLAME_CMAP[c_use], 255)
        # Flammèche / escarbille montante périodique (pixel-art net)
        ember_step = t % 6
        ex = 12 + (1 if ember_step in (2, 3) else 0)
        ey = max(0, 5 - ember_step)
        if ember_step < 4:
            canvas[ey, ex] = (*FLAME_CMAP["R" if ember_step < 2 else "r"], 255)
        sprites.append(canvas)
    return sprites


def build_brazier_flame_frames() -> list:
    """Calque 05 : 12 phases des 5 braseros nord avec déphasage naturel."""
    flame_sprites = make_canonical_flame_phases()
    brazier_specs = [
        (126, 135, 0, False),
        (298, 136, 5, False),
        (385, 138, 9, False),
        (470, 136, 3, True),
        (643, 135, 7, True),
    ]
    frames = []
    yy, xx = np.mgrid[:H, :W]
    for t in range(PHASES):
        frame = np.zeros((H, W, 4), dtype=np.uint8)
        im = Image.fromarray(frame, mode="RGBA")
        for bcx, bcy, offset, flip in brazier_specs:
            sp = flame_sprites[(t + offset) % PHASES]
            if flip:
                sp = sp[:, ::-1]
            # Léger reflet chaud discret sur la pierre juste sous la base de la flamme
            pulse = 0.5 + 0.5 * np.sin(2.0 * np.pi * ((t + offset) % PHASES) / PHASES)
            if pulse > 0.45:
                glow = (((xx - bcx) / 7.0) ** 2 + ((yy - (bcy + 10)) / 3.5) ** 2) <= 1.0
                arr = np.array(im)
                arr[glow] = (255, 159, 0, 72 if pulse > 0.78 else 44)
                im = Image.fromarray(arr, mode="RGBA")
            im.alpha_composite(Image.fromarray(sp, mode="RGBA"), (bcx - 11, bcy - 28))
        frames.append(np.array(im))
    return frames


def build_crystal_glint_frames(q_decor: np.ndarray, fg_mask: np.ndarray) -> list:
    """Calque 06 : onde de reflet cyan sur les facettes des 2 cristaux + éclats croisés pixel-art."""
    r, g, b = q_decor.transpose(2, 0, 1).astype(float)
    yy, xx = np.mgrid[:H, :W]
    cryst_zone = fg_mask & (yy >= 204) & (yy <= 246) & (((xx >= 306) & (xx <= 335)) | ((xx >= 433) & (xx <= 462)))
    facets = cryst_zone & (b > r * 1.45) & (b > 145)
    bright_facets = facets & (b > 185)

    # Éclats pixel-art canoniques (sans flou)
    star_small = [
        ".c.",
        "cWc",
        ".c.",
    ]
    star_big = [
        "..c..",
        ".cWc.",
        "cWWWc",
        ".cWc.",
        "..c..",
    ]
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
        halo = facets & (dist <= 5)
        core = bright_facets & (dist <= 2)
        f[halo] = (155, 232, 252, 255)
        f[core] = (238, 252, 255, 255)

        # Éclat étoilé discret au sommet du cristal gauche (t=1..4) puis droit (t=7..10)
        if t in (1, 4):
            stamp(f, star_small, 320, 213)
        elif t in (2, 3):
            stamp(f, star_big, 320, 213)
        if t in (7, 10):
            stamp(f, star_small, 447, 213)
        elif t in (8, 9):
            stamp(f, star_big, 447, 213)
        frames.append(f)
    return frames


def build_rune_pulse_frames(q_decor: np.ndarray, fg_mask: np.ndarray) -> list:
    """Calque 07 : pulsation douce des runes orange du sceau central, des blocs et des emblèmes solaires."""
    r, g, b = q_decor.transpose(2, 0, 1).astype(float)
    # Uniquement le cœur lumineux des sillons runiques orange
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


def build_obstacle_grid() -> np.ndarray:
    """Grille `obstacles` (GH, GW) : 0 = praticable, 1 = bloqué."""
    # Zone praticable : grande arène sableuse + couloir sud jusqu'au bord inférieur
    walk_poly = poly_mask([
        (276, 160), (492, 160),
        (492, 194), (636, 194),
        (658, 208), (658, 340),
        (598, 418), (438, 440),
        (424, 448), (424, 576),
        (344, 576), (344, 448),
        (330, 440), (170, 418),
        (110, 340), (110, 208),
        (132, 194), (276, 194),
    ])

    blocked_px = ~walk_poly
    yy, xx = np.mgrid[:H, :W]

    # Obstacles intérieurs 3D : socles des 2 cristaux cyan + rainures en L et blocs de pierre gravés
    blocked_px |= (xx >= 308) & (xx < 336) & (yy >= 212) & (yy < 248)
    blocked_px |= (xx >= 436) & (xx < 464) & (yy >= 212) & (yy < 248)

    # Ensemble rainure en L + 2 blocs côté gauche
    blocked_px |= (xx >= 168) & (xx < 204) & (yy >= 320) & (yy < 360)
    blocked_px |= (xx >= 196) & (xx < 232) & (yy >= 328) & (yy < 408)
    blocked_px |= (xx >= 196) & (xx < 276) & (yy >= 364) & (yy < 408)

    # Ensemble rainure en L + bloc côté droit
    blocked_px |= (xx >= 540) & (xx < 576) & (yy >= 328) & (yy < 408)
    blocked_px |= (xx >= 512) & (xx < 576) & (yy >= 352) & (yy < 408)

    # Agrégation par cellule 8x8 : une cellule est praticable si la majorité (>= 75 %) est dégagée
    cell_free = (~blocked_px).reshape(GH, 8, GW, 8).mean(axis=(1, 3)) >= 0.75
    blocked_cells = (~cell_free).astype(np.int32)
    return blocked_cells


def verify_navigation(blocked_cells: np.ndarray, markers_and_targets: list):
    """Vérifie par BFS 16x16 que le joueur circule librement entre l'entrée sud, Kaito, le sceau et les 2 portes."""
    def free16(px: int, py: int) -> bool:
        if px < 0 or py < 0 or px + 16 > W or py + 16 > H:
            return False
        for cx in range(px // 8, (px + 15) // 8 + 1):
            for cy in range(py // 8, (py + 15) // 8 + 1):
                if blocked_cells[cy, cx] != 0:
                    return False
        return True

    start = (376, 504)  # MarowakDojoExitMarker
    assert free16(*start), f"Start marker {start} is blocked!"
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 8, y), (x - 8, y), (x, y + 8), (x, y - 8)):
            if (nx, ny) not in seen and free16(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))

    for label, pt in markers_and_targets:
        assert pt in seen, f"Navigation target {label} at {pt} is NOT reachable from {start}!"


def premult(image: Image.Image) -> Image.Image:
    a = np.array(image.convert("RGBA"), dtype=np.uint16)
    a[:, :, :3] = (a[:, :, :3] * a[:, :, 3:4]) // 255
    return Image.fromarray(a.astype(np.uint8), mode="RGBA")


def png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG", compress_level=6)
    return buf.getvalue()


class TileBank:
    """Encodeur `.tile` RogueEssence conforme à `source/pmdo_cote/build.py`."""

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


def make_layer(name: str, frames: list, ticks: int, bank: TileBank, draw_layer: int = 0) -> dict:
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
    return {"Name": name, "Layer": draw_layer, "Visible": True, "Tiles": tiles}


def assert_zero_magenta(frames_list: list):
    for name, frames in frames_list:
        for idx, arr in enumerate(frames):
            opq = arr[..., 3] > 0
            if not np.any(opq):
                continue
            r, g, b = arr[opq, 0].astype(float), arr[opq, 1].astype(float), arr[opq, 2].astype(float)
            bad = (r > g * 1.45) & (b > g * 1.32) & (r > 135) & (b > 125)
            assert not np.any(bad), f"Residual magenta pixels ({int(bad.sum())}) in {name} frame {idx}!"


def build():
    raw_decor = np.array(Image.open(RAW / "decor_magenta.png").convert("RGB"))
    raw_sol = np.array(Image.open(RAW / "sol_complet.png").convert("RGB"))
    assert raw_decor.shape[:2] == (SRC[1], SRC[0]) and raw_sol.shape[:2] == (SRC[1], SRC[0])

    # Étape 2 & 3 : détourage `key()` et réduction uniforme 1200x896 -> 768x576
    mag = key_magenta(raw_decor)
    decor_768, fg_mask = down_masked(raw_decor, ~mag)
    sol_768 = down_full(raw_sol)

    # Étape 4 : unification des dômes sculptés des 5 braseros + quantification commune 96 couleurs (sans dither)
    decor_768 = unify_brazier_domes(decor_768)
    q_decor, q_sol = quantize_shared_96(decor_768, fg_mask, sol_768)

    # Étape 5 : contrôle bloquant `fidelity()` < 35 vis-à-vis du rip canonique
    fidelity_report = check_fidelity(q_decor, fg_mask)

    # Étape 6 : partition exacte des calques statiques + calques animés
    masks = partition_static_layers(q_decor, fg_mask)
    l00_sol_complet = [rgba_from(q_sol, fg_mask)]
    l01_sol = [rgba_from(q_decor, masks["sol"])]
    l02_ombres = [rgba_from(q_decor, masks["ombres"])]
    l03_parois = [rgba_from(q_decor, masks["parois"])]
    l04_blocs = [rgba_from(q_decor, masks["blocs"])]
    l05_flammes = build_brazier_flame_frames()
    l06_reflets = build_crystal_glint_frames(q_decor, fg_mask)
    l07_sceau = build_rune_pulse_frames(q_decor, fg_mask)
    l08_top = [rgba_from(q_decor, masks["top"])]

    # Vérification de recomposition exacte du décor statique
    recomp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for part_arr in (l01_sol[0], l02_ombres[0], l03_parois[0], l04_blocs[0], l08_top[0]):
        recomp.alpha_composite(Image.fromarray(part_arr, mode="RGBA"))
    assert np.array_equal(np.array(recomp), rgba_from(q_decor, fg_mask)), "Exact recomposition check failed!"

    layer_specs = [
        ("00 sol complet", l00_sol_complet, STATIC_TICKS, 0),
        ("01 sol", l01_sol, STATIC_TICKS, 0),
        ("02 ombres", l02_ombres, STATIC_TICKS, 0),
        ("03 parois", l03_parois, STATIC_TICKS, 0),
        ("04 blocs", l04_blocs, STATIC_TICKS, 0),
        ("05 flammes braseros 12 phases", l05_flammes, ANIM_TICKS, 0),
        ("06 reflets cristaux 12 phases", l06_reflets, ANIM_TICKS, 0),
        ("07 lueur sceau 12 phases", l07_sceau, ANIM_TICKS, 0),
        ("08 Vos elements avant-plan (Top)", l08_top, STATIC_TICKS, 4),
    ]
    assert len(layer_specs) == 9
    assert_zero_magenta([(n, fs) for n, fs, _, _ in layer_specs])

    # Étape 7 : encodage `.tile` et construction de `dojo_kingambit.rsground`
    bank = TileBank(SHEET_NAME)
    layers_json = [
        make_layer(name, frames, ticks, bank, draw_layer=draw)
        for name, frames, ticks, draw in layer_specs
    ]
    bank.write(TILE_OUT)

    blocked_cells = build_obstacle_grid()
    verify_navigation(
        blocked_cells,
        [
            ("South Exit Trigger approach", (376, 544)),
            ("Central Orange Rune Seal", (376, 256)),
            ("Master Kaito front", (376, 208)),
            ("Left North Door approach", (208, 200)),
            ("Right North Door approach", (544, 200)),
            ("Spacious West Arena", (144, 272)),
            ("Spacious East Arena", (608, 272)),
        ],
    )

    # Lecture du gabarit d'entités existant pour conserver strictement tous les champs sérialisés PMDO 0.8.12
    existing = json.loads(GROUND_OUT.read_text(encoding="utf-8-sig"))
    obj = existing["Object"]
    ent_layer = obj["Entities"][0]

    # Maître Kaito (Kingambit) : centré au nord devant le pilier central, entre les deux portes du fond
    kaito = ent_layer["MapChars"][0]
    kaito["Direction"] = 0
    kaito["serializationDir"] = 0
    kaito["serializationLoc"] = {"X": 376, "Y": 184}
    kaito["Collider"] = {"X": 376, "Y": 184, "Width": 16, "Height": 16}

    # Capteurs de seuil : sortie sud + porte nord gauche (MarowakDojoDungeonEntrance) + porte nord droite
    base_gobj = ent_layer["GroundObjects"][0]

    def make_trigger(name: str, direction: int, x: int, y: int, w: int, h: int) -> dict:
        g = json.loads(json.dumps(base_gobj))
        g["EntName"] = name
        g["Direction"] = direction
        g["Passable"] = False
        g["Collider"] = {"X": x, "Y": y, "Width": w, "Height": h}
        return g

    ent_layer["GroundObjects"] = [
        make_trigger("MarowakDojoExit", 4, 352, 560, 64, 8),
        make_trigger("MarowakDojoDungeonEntrance", 0, 180, 144, 64, 8),
        make_trigger("KingambitDojoNorthDoorRight", 0, 524, 144, 64, 8),
    ]

    # Spawners équipiers dans le couloir sud dégagé
    for sp, sx in zip(ent_layer["Spawners"], (352, 400)):
        sp["Direction"] = 4
        sp["Collider"] = {"X": sx, "Y": 504, "Width": 16, "Height": 16}

    # Marqueurs : sortie sud + seuil porte nord gauche + seuil porte nord droite
    ent_layer["Markers"] = [
        {
            "EntName": "MarowakDojoDungeonEntranceMarker",
            "Direction": 0,
            "EntEnabled": True,
            "EntOrder": 0,
            "InteractOrder": 0,
            "triggerType": 0,
            "Collider": {"X": 204, "Y": 200, "Width": 16, "Height": 16},
        },
        {
            "EntName": "KingambitDojoNorthDoorRightMarker",
            "Direction": 0,
            "EntEnabled": True,
            "EntOrder": 0,
            "InteractOrder": 0,
            "triggerType": 0,
            "Collider": {"X": 548, "Y": 200, "Width": 16, "Height": 16},
        },
        {
            "EntName": "MarowakDojoExitMarker",
            "Direction": 4,
            "EntEnabled": True,
            "EntOrder": 0,
            "InteractOrder": 0,
            "triggerType": 0,
            "Collider": {"X": 376, "Y": 504, "Width": 16, "Height": 16},
        },
    ]

    obj["TexSize"] = 1
    obj["EdgeView"] = 1
    obj["AssetName"] = "dojo_kingambit"
    obj["Background"] = {"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []}
    obj["BlankBG"] = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}
    obj["Layers"] = layers_json
    obj["obstacles"] = [
        [
            {"Bounds": {"X": x * 8, "Y": y * 8, "Width": 8, "Height": 8}, "Tags": int(blocked_cells[y, x])}
            for y in range(GH)
        ]
        for x in range(GW)
    ]
    existing["Version"] = "0.8.12.0"

    GROUND_OUT.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Compter les références de frames pour le manifeste et `test_reverie_wip.py`
    frame_refs = sum(
        len(anim["Frames"])
        for L in layers_json
        for col in L["Tiles"]
        for tile in col
        for anim in tile.get("Layers", [])
    )

    manifest = {
        "asset": "dojo_kingambit",
        "method": "METHODE_MAGENTA_ET_GENERATEUR.md (projet-creation-pmdo)",
        "size_px": [W, H],
        "grid_8px": [GW, GH],
        "source_size_px": list(SRC),
        "palette_colors": 96,
        "phases": PHASES,
        "anim_ticks": ANIM_TICKS,
        "tile_sheet": SHEET_NAME,
        "unique_8x8_tiles": len(bank.data),
        "total_frame_refs": frame_refs,
        "sha256": {
            "ref_canon_magenta.png": sha256(ART / "ref_canon_magenta.png"),
            "decor_magenta.png": sha256(RAW / "decor_magenta.png"),
            "sol_complet.png": sha256(RAW / "sol_complet.png"),
            "Kingambit_Dojo_Interieur.tile": sha256(TILE_OUT),
        },
        "fidelity_vs_canonical_rip": fidelity_report,
    }
    (ART / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
