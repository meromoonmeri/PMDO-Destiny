#!/usr/bin/env python3
"""
Reconstruction pixel par pixel style Nintendo DS (Explorers of Sky) + Décomposition Multicalque Halcyon
pour l'intégralité des 15 cartes intérieures `guilde_destiny_*`, la double porte `Guilde_Destiny_Porte_Salon_{Fermee,Ouverte}`
et les 60 fenêtres `Guilde_Fenetre_*` (4 ambiances) :

- ZÉRO régénération IA (`generate_image`), ZÉRO texture reprise de la Guilde de Halcyon.
- Préservation à 100 % de l'architecture, des proportions, des ouvertures, des marqueurs, des capteurs et des collisions BFS.
- Palettes Nintendo DS harmonieuses (~24-28 couleurs chaudes par salle : chêne miel, cèdre sculpté, cordages sisal,
  profondeurs d'arches étagées, sel-out acajou chaud sans noir `#000000`, clusters cohérents sans flou ni mixels).
- Organisation Multicalque canonique style Halcyon sur les 15 `.rsground` :
    [0] "Floor"         (Layer = 0, plancher chêne miel, seuils & escaliers avec jupe sous-paroi)
    [1] "Walls"         (Layer = 0, parois verticales cèdre, plinthes, piliers cordés, encadrements & fond #68482F)
    [2] "Shadows"       (Layer = 0, ombres portées DS 2 paliers alpha au pied des parois & piliers)
    [3] "Objects Under" (Layer = 0, vierge — 0 tuile, prêt pour tapis/nattes en jeu)
    [4] "Objects"       (Layer = 0, vierge — 0 tuile, prêt pour mobilier/tableaux en jeu)
    [5] "Objects Over"  (Layer = 0, vierge — 0 tuile, prêt pour objets sur tables en jeu)
    [6] "Fringe"        (Layer = 4, guirlandes de verdure DS sur `Destiny_Guilde_Verdure`, hors sol praticable)
    [7] "Supports"      (Layer = 4, couronne haute & racines avant-plan Sud sculptées alpha, hors sol praticable)
"""
from __future__ import annotations

import io
import json
import shutil
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
ART_RESEAU = ROOT / "art/guilde_destiny_reseau"
BASE_DIR = ART_RESEAU / "cartes_base_sans_decors"
USER_RESEAU = Path("/home/user/guilde_destiny_reseau")
MANIFEST_PATH = (
    USER_RESEAU / "objets_pmdo/manifest_decors_pmdo.json"
    if (USER_RESEAU / "objets_pmdo/manifest_decors_pmdo.json").exists()
    else ART_RESEAU / "objets_pmdo/manifest_decors_pmdo.json"
)

OBJ_DIR = ROOT / "game/Content/Object"
TILE_DIR = ROOT / "game/Content/Tile"
GROUND_DIR = ROOT / "game/Data/Ground"

AMBIANCES = ("jour", "aube", "crepuscule", "nuit")
WORLD_TINTS = {
    "jour": np.array([255.0, 255.0, 255.0], dtype=np.float32) / 255.0,
    "aube": np.array([224.0, 203.0, 212.0], dtype=np.float32) / 255.0,
    "crepuscule": np.array([179.0, 146.0, 173.0], dtype=np.float32) / 255.0,
    "nuit": np.array([97.0, 118.0, 159.0], dtype=np.float32) / 255.0,
}

EXT_RGB = np.array([104, 72, 47], dtype=np.uint8)

# Handcrafted Nintendo DS (Explorers of Sky) Warm Honey-Oak & Cedar Ramps (100% Destiny identity, 0 Halcyon textures)
DS_RECESS = np.array([
    [22, 11, 7],     # 0: deepest stairwell shadow
    [38, 20, 12],    # 1: dark archway recess
    [58, 32, 18],    # 2: mid archway step
    [82, 47, 25],    # 3: lit threshold step
], dtype=np.uint8)

DS_FLOOR_OAK = np.array([
    [54, 27, 13],    # 0: crisp 1px plank seam / end-joint groove (warm chestnut, 0 #000000!)
    [96, 52, 22],    # 1: step riser / deep plank bevel
    [138, 79, 30],   # 2: shaded oak bevel
    [172, 103, 36],  # 3: warm honey-oak lower bevel / darker plank
    [194, 121, 42],  # 4: primary warm honey-oak plank face (clean solid DS fill!)
    [210, 136, 50],  # 5: sunlit honey-oak plank face
    [228, 156, 64],  # 6: crisp 1px top plank bevel highlight
], dtype=np.uint8)

DS_WALL_CEDAR = np.array([
    [38, 18, 11],    # 0: warm deep mahogany sel-out
    [64, 31, 17],    # 1: deep root crease / board groove
    [94, 47, 24],    # 2: dark sculpted cedar bark shadow
    [124, 65, 31],   # 3: shaded cedar root / baseboard
    [152, 84, 37],   # 4: rich warm cedar bark midtone
    [178, 104, 44],  # 5: warm vertical cedar wall board
    [202, 125, 52],  # 6: sunlit pillar / window frame
    [224, 149, 66],  # 7: pillar / root ridge highlight
], dtype=np.uint8)

DS_ROPE_GOLD = np.array([
    [70, 39, 16],    # 0: rope coil groove
    [130, 80, 30],   # 1: sisal shadow
    [180, 120, 44],  # 2: sisal mid
    [218, 158, 62],  # 3: lit golden sisal coil / window sill / carved Winged-Egg face
    [244, 194, 88],  # 4: bright sisal specular
], dtype=np.uint8)

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


def write_dir(dir_path: Path, rgba_im: Image.Image, tile_w: int, tile_h: int) -> None:
    arr = sanitize_patch_anti_magenta(np.array(rgba_im.convert("RGBA")))
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, format="PNG", optimize=True)
    png_bytes = buf.getvalue()
    dir_path.parent.mkdir(parents=True, exist_ok=True)
    dir_path.write_bytes(
        struct.pack("<q", len(png_bytes)) + png_bytes + struct.pack("<iiii", int(tile_w), int(tile_h), 0, 1)
    )


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
        out = bytearray(struct.pack("<ii", 8, n_tiles))
        off = 8 + n_tiles * 16
        for (lx, ly, _), blob in zip(self.ordered_patches, blobs):
            out += struct.pack("<iiq", lx, ly, off)
            off += 8 + len(blob)
        for blob in blobs:
            out += struct.pack("<q", len(blob)) + blob
        (out_dir / f"{self.sheet_name}.tile").write_bytes(bytes(out))
        return n_tiles


def empty_tile_grid(tw: int, th: int) -> list[list[dict]]:
    return [[{"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1} for _ in range(th)] for _ in range(tw)]


def extract_exact_floor_mask(
    rgb: np.ndarray,
    fg: np.ndarray,
    walk_px: np.ndarray,
    seed_points: list[tuple[int, int]],
    scale: int = 1,
) -> np.ndarray:
    """
    Extracts the 1-pixel accurate visual floor & stairs boundary:
    - Stops cleanly at dark curved baseboards, pillar feet (never climbs vertical pillar shafts!), and South carved roots.
    """
    h, w, _ = rgb.shape
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    r = rgb[..., 0].astype(np.float32)
    b = rgb[..., 2].astype(np.float32)

    # Walkable character footprint (`walk_px` is top-left of 16x16 collider, plus baseboard margin; blocks climbing vertical pillars!)
    max_floor_env = ndimage.binary_dilation(walk_px, iterations=14 * scale) & fg

    bright_oak = max_floor_env & (lum >= 110.0) & ((r - b) >= 60.0)
    bridged = bright_oak.copy()
    max_dy = 2 * scale
    for dy in range(1, max_dy + 1):
        seam = (
            max_floor_env[dy:-dy, :]
            & (~bright_oak[dy:-dy, :])
            & bright_oak[: -2 * dy, :]
            & bright_oak[2 * dy :, :]
        )
        valid_seam = seam & ((lum[dy:-dy, :] >= 50.0) | ((lum[: -2 * dy, :] >= 126.0) & (lum[2 * dy :, :] >= 126.0)))
        bridged[dy:-dy, :] |= valid_seam

    lbl, _ = ndimage.label(bridged)
    chosen = set()
    rad = 6 * scale
    for sx, sy in seed_points:
        y0, y1 = max(0, sy - rad), min(h, sy + rad + 1)
        x0, x1 = max(0, sx - rad), min(w, sx + rad + 1)
        chosen |= set(np.unique(lbl[y0:y1, x0:x1])) - {0}
    # Also include any large oak component inside `walk_px`
    chosen |= set(np.unique(lbl[walk_px & bridged])) - {0}
    floor_core = np.isin(lbl, list(chosen)) | (walk_px & (lum >= 62.0))

    c_sz = 3 * scale
    floor_mask = ndimage.binary_closing(floor_core, structure=np.ones((c_sz, c_sz), dtype=bool)) & max_floor_env
    floor_mask = ndimage.binary_fill_holes(floor_mask) & max_floor_env
    return floor_mask


def reconstruct_ds_pixels(
    rgb: np.ndarray,
    is_ext: np.ndarray,
    is_floor_px: np.ndarray,
    scale: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic Nintendo DS (Explorers of Sky) pixel-by-pixel reconstructor (~25 warm colors, 0 Halcyon, 0 AI)."""
    h, w, _ = rgb.shape
    fg = ~is_ext

    rgb_clean = rgb.astype(np.float32).copy()
    _, fg_idx = ndimage.distance_transform_edt(~fg, return_indices=True)
    rgb_clean[~fg] = rgb_clean[fg_idx[0][~fg], fg_idx[1][~fg]]

    L0 = 0.299 * rgb_clean[..., 0] + 0.587 * rgb_clean[..., 1] + 0.114 * rgb_clean[..., 2]
    # Directional smoothing inside planks/boards (eliminates blotchy gradients while preserving 100% of joints & seams!)
    med_h = ndimage.median_filter(rgb_clean, size=(1, 7 * scale, 1))
    L_mh = 0.299 * med_h[..., 0] + 0.587 * med_h[..., 1] + 0.114 * med_h[..., 2]
    use_mh = is_floor_px & (L0 >= 105.0) & (np.abs(L0 - L_mh) < 11.0)
    rgb_clean[use_mh] = med_h[use_mh]

    med_v = ndimage.median_filter(rgb_clean, size=(5 * scale, 1, 1))
    L_mv = 0.299 * med_v[..., 0] + 0.587 * med_v[..., 1] + 0.114 * med_v[..., 2]
    use_mv = fg & (~is_floor_px) & (L0 >= 95.0) & (np.abs(L0 - L_mv) < 10.0)
    rgb_clean[use_mv] = med_v[use_mv]

    # Edge-preserving local S-curve sharpening
    win_s = 3 if scale == 1 else 5
    L = 0.299 * rgb_clean[..., 0] + 0.587 * rgb_clean[..., 1] + 0.114 * rgb_clean[..., 2]
    lmin = ndimage.minimum_filter(L, size=win_s)
    lmax = ndimage.maximum_filter(L, size=win_s)
    span = lmax - lmin
    u = np.clip((L - lmin) / np.maximum(span, 1e-4), 0.0, 1.0)
    us = u * u * (3.0 - 2.0 * u)
    us = 0.32 * u + 0.68 * (us * us * (3.0 - 2.0 * us))
    gate = np.clip((span - 12.0) / 24.0, 0.0, 1.0)
    L_s = L + 0.62 * gate * ((lmin + us * span) - L)
    gain = (L_s + 1.0) / (L + 1.0)
    cmin = ndimage.minimum_filter(rgb_clean, size=(win_s, win_s, 1))
    cmax = ndimage.maximum_filter(rgb_clean, size=(win_s, win_s, 1))
    rgb_s = np.clip(rgb_clean * gain[..., None], cmin, cmax)

    r, g, b = rgb_s[..., 0], rgb_s[..., 1], rgb_s[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b

    open_sz = 4 * scale
    dark_core = fg & (lum < 34.0)
    dark_core_open = ndimage.binary_opening(dark_core, structure=np.ones((open_sz, open_sz), dtype=bool))
    is_recess = ndimage.binary_dilation(dark_core_open, iterations=6 * scale) & fg & (lum < 72.0)

    g_over_r = g / np.maximum(r, 1.0)
    is_rope = fg & (~is_floor_px) & (~is_recess) & (
        ((lum >= 146.0) & (g_over_r >= 0.68))
        | ((lum >= 120.0) & (g_over_r >= 0.71) & ((r - b) >= 85.0))
    )
    rope_dil = ndimage.binary_dilation(is_rope, iterations=scale) & fg & (~is_floor_px) & (~is_recess)
    is_rope = is_rope | (rope_dil & (lum < 92.0))

    ds_rgb = np.zeros((h, w, 3), dtype=np.uint8)
    ds_rgb[is_ext] = EXT_RGB

    def apply_thresholds(m: np.ndarray, ramp: np.ndarray, thresholds: list[float]) -> None:
        if not np.any(m):
            return
        ds_rgb[m] = ramp[np.digitize(lum[m], thresholds)]

    apply_thresholds(is_recess, DS_RECESS, [22.0, 38.0, 56.0])
    apply_thresholds(is_floor_px & (~is_recess), DS_FLOOR_OAK, [66.0, 96.0, 122.0, 136.0, 156.0, 174.0])
    apply_thresholds(is_rope, DS_ROPE_GOLD, [88.0, 128.0, 156.0, 182.0])
    is_wall_wood = fg & (~is_floor_px) & (~is_recess) & (~is_rope)
    apply_thresholds(is_wall_wood, DS_WALL_CEDAR, [44.0, 68.0, 90.0, 110.0, 128.0, 146.0, 166.0])

    # Coherent DS Pixel-Cluster Cleanup (eliminates isolated specks on mid/bright wood)
    ds_lum = 0.299 * ds_rgb[..., 0] + 0.587 * ds_rgb[..., 1] + 0.114 * ds_rgb[..., 2]
    editable = fg & (ds_lum >= 82.0)
    codes = (ds_rgb[..., 0].astype(np.int32) << 16) | (ds_rgb[..., 1].astype(np.int32) << 8) | ds_rgb[..., 2].astype(np.int32)
    s8 = np.ones((3, 3), dtype=bool)
    speck = np.zeros((h, w), dtype=bool)
    max_speck = 2 if scale == 1 else 5
    for c in np.unique(codes[editable]):
        cm = editable & (codes == c)
        lb, nc = ndimage.label(cm, structure=s8)
        if nc > 0:
            sz = ndimage.sum(cm, lb, range(1, nc + 1))
            s_small = np.where(sz <= max_speck)[0] + 1
            if len(s_small):
                speck |= np.isin(lb, s_small)
    if np.any(speck):
        ys_s, xs_s = np.where(speck)
        cleaned = ds_rgb.copy()
        rad = 1 if scale == 1 else 2
        for y, x in zip(ys_s, xs_s):
            y0, y1 = max(0, y - rad), min(h, y + rad + 1)
            x0, x1 = max(0, x - rad), min(w, x + rad + 1)
            nb = fg[y0:y1, x0:x1] & (~speck[y0:y1, x0:x1])
            if np.any(nb):
                vals, cnts = np.unique(codes[y0:y1, x0:x1][nb], return_counts=True)
                bc = int(vals[int(np.argmax(cnts))])
                cleaned[y, x] = [(bc >> 16) & 255, (bc >> 8) & 255, bc & 255]
        ds_rgb = cleaned

    eroded_fg = ndimage.binary_erosion(fg, structure=np.ones((3, 3), dtype=bool))
    ext_sil = fg & (~eroded_fg) & (~is_floor_px)
    ds_rgb[ext_sil] = DS_WALL_CEDAR[0]
    return ds_rgb, is_recess


def decompose_halcyon_layers(
    ds_rgb: np.ndarray,
    is_ext: np.ndarray,
    is_floor_px: np.ndarray,
    is_recess: np.ndarray,
    walk_tile: np.ndarray,
    scale: int = 1,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Produces alpha-separated RGBA canvases for Halcyon's architectural layers:
      - Floor    (Layer = 0): floor planks & stairs + 6px under-wall skirt
      - Walls    (Layer = 0): vertical walls, pillars, baseboards, window frames & #68482F surround
      - Shadows  (Layer = 0): 2-step DS ambient contact shadows on the floor
      - Supports (Layer = 4): overhead carved upper root crown & South foreground root rim (strictly on `walk_tile == False`!)
    """
    h, w, _ = ds_rgb.shape
    tw, th = w // 8, h // 8
    fg = ~is_ext
    walk_px = np.repeat(np.repeat(walk_tile.T, 8, axis=0), 8, axis=1)
    non_walk_tile_px = ~walk_px

    # 1) Floor (`Layer = 0`)
    floor_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    skirt = ndimage.binary_dilation(is_floor_px, iterations=6 * scale) & (~is_floor_px) & fg
    floor_rgba[is_floor_px, :3] = ds_rgb[is_floor_px]
    floor_rgba[is_floor_px, 3] = 255
    if np.any(skirt):
        _, f_idx = ndimage.distance_transform_edt(~is_floor_px, return_indices=True)
        floor_rgba[skirt, :3] = ds_rgb[f_idx[0][skirt], f_idx[1][skirt]]
        floor_rgba[skirt, 3] = 255

    # 2) Supports (`Layer = 4` overhead):
    # Strictly on `walk_tile == False` AND with >= 24px*scale headroom above any walkable tile below it (prevents North-wall head clipping!),
    # PLUS South foreground carved roots below walkable floor (true 2.5D foreground depth!).
    headroom_tiles = 3 * scale  # 24px at 1x, 72px at 3x
    safe_overhead_tile = np.zeros((tw, th), dtype=bool)
    for tx in range(tw):
        w_ys = np.where(walk_tile[tx])[0]
        if len(w_ys) == 0:
            safe_overhead_tile[tx, :] = True
        else:
            min_wy, max_wy = int(w_ys.min()), int(w_ys.max())
            for ty in range(th):
                if not walk_tile[tx, ty]:
                    if ty <= min_wy - headroom_tiles or ty >= max_wy + 2:
                        safe_overhead_tile[tx, ty] = True

    safe_overhead_px = np.repeat(np.repeat(safe_overhead_tile.T, 8, axis=0), 8, axis=1)
    top_ext_dist = ndimage.distance_transform_edt(~is_ext)
    yy, _ = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    upper_crown = fg & (~is_floor_px) & (yy < int(h * 0.34)) & (top_ext_dist <= 12 * scale)
    south_roots = fg & (~is_floor_px) & (yy >= int(h * 0.72))
    supports_mask = (upper_crown | south_roots) & non_walk_tile_px & safe_overhead_px

    supports_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    supports_rgba[supports_mask, :3] = ds_rgb[supports_mask]
    supports_rgba[supports_mask, 3] = 255

    # 3) Walls (`Layer = 0`): all non-floor pixels not in `Supports`
    walls_mask = (~is_floor_px) & (~supports_mask)
    walls_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    walls_rgba[walls_mask, :3] = ds_rgb[walls_mask]
    walls_rgba[walls_mask, 3] = 255

    # 4) Shadows (`Layer = 0`): crisp 2-step DS ground contact shadows cast onto Floor by North/side walls & pillars
    wall_caster = fg & (~is_floor_px) & (~is_recess) & (yy < int(h * 0.74))
    sh_inner = np.zeros((h, w), dtype=bool)
    sh_outer = np.zeros((h, w), dtype=bool)
    for dy in range(1, 2 * scale + 1):
        sh_inner[dy:, :] |= wall_caster[:-dy, :]
    for dy in range(2 * scale + 1, 4 * scale + 1):
        sh_outer[dy:, :] |= wall_caster[:-dy, :]
    sh_inner &= is_floor_px & (~is_recess)
    sh_outer &= is_floor_px & (~is_recess) & (~sh_inner)

    shadows_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    shadows_rgba[sh_inner] = [42, 20, 8, 64]
    shadows_rgba[sh_outer] = [42, 20, 8, 32]

    return floor_rgba, walls_rgba, shadows_rgba, supports_rgba


def generate_ds_garland_rgba(
    room_rgb: np.ndarray,
    walk_tile: np.ndarray,
    windows: list[dict],
    north_arch_x: tuple[int, int] | None = None,
    split_gap_x: tuple[int, int] | None = None,
    door_keepout: tuple[int, int, int, int] | None = None,
    seed: int = 7,
) -> np.ndarray:
    """
    Generates a crisp DS pixel-art greenery garland (`Fringe` Layer = 4) strictly on non-walkable tiles
    and strictly outside window panes & `PorteSalonFermee`!
    """
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
            if r >= 152 and g >= 84 and b >= 36:
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
    # Keep garlands strictly inside the interior wall bay (never on outer carved bark arch rim!)
    top_ext_dist = ndimage.distance_transform_edt(~ext)
    keepout |= top_ext_dist <= 13
    # Never overlap any walkable 8x8 tile (nor within 16px headroom above walkable tiles!)
    tw, th = w // 8, h // 8
    for tx in range(tw):
        for ty in range(th):
            if walk_tile[tx, ty]:
                keepout[max(0, (ty - 2) * 8) : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = True

    win_spans = []
    for slot in windows:
        wx, wy, ww, wh = slot["x"], slot["y"], slot["w"], slot["h"]
        keepout[max(0, wy + 2) : min(h, wy + wh), max(0, wx + 2) : min(w, wx + ww - 2)] = True
        win_spans.append((wx, wx + ww, wy))

    if door_keepout is not None:
        dx, dy, dw, dh = door_keepout
        keepout[max(0, dy) : min(h, dy + dh), max(0, dx) : min(w, dx + dw)] = True

    if north_arch_x is not None:
        ax0, ax1 = north_arch_x
        y_k = 63 if (ax1 - ax0) >= 120 else (int(smooth_cy[(ax0 + ax1) // 2]) + 3)
        keepout[y_k:h, ax0 + 2 : ax1 - 2] = True

    if split_gap_x is not None:
        keepout[:, max(0, split_gap_x[0] - 2) : min(w, split_gap_x[1] + 2)] = True

    foliage = np.zeros((h, w), dtype=bool)
    buds: list[tuple[int, int]] = []

    def stamp_leaf_cluster(cx: int, cy: int, radius_x: int = 3, radius_y: int = 3, angle_dx: int = 0) -> None:
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

        ya = smooth_cy[xa] - 2.0
        yb = smooth_cy[xb] - 2.0
        if over_win:
            wy_min = min(wy for wx0, wx1, wy in win_spans if wx0 - 6 <= mid_x <= wx1 + 6)
            sag = -5.0
            ya = min(ya, float(wy_min - 2))
            yb = min(yb, float(wy_min - 2))
        elif over_arch:
            sag = -6.0
            if north_arch_x is not None and (north_arch_x[1] - north_arch_x[0]) >= 120:
                ya = min(ya, 56.0)
                yb = min(yb, 56.0)
            else:
                ya -= 4.0
                yb -= 4.0
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
        ay0 = int(round(smooth_cy[ax] - 2.0))
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
    out[sh_mask2] = [38, 17, 6, 48]
    out[sh_mask1] = [38, 17, 6, 92]

    ys, xs = np.where(foliage)
    for y, x in zip(ys, xs):
        up_empty = not foliage[y - 1, x] or not foliage[y, x - 1]
        dn_empty = not foliage[y + 1, x] or not foliage[y, x + 1]
        if up_empty and not dn_empty:
            out[y, x] = [122, 166, 52, 255]
        elif dn_empty and not up_empty:
            out[y, x] = [42, 76, 26, 255]
        else:
            out[y, x] = [78, 126, 40, 255] if (((x // 2) + y) % 3 == 0) else [62, 106, 34, 255]

    out[outline] = [26, 44, 18, 255]
    for bx, by in buds:
        if 2 <= bx < w - 2 and 2 <= by < h - 2 and not keepout[by, bx]:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                if not keepout[by + dy, bx + dx] and not ext[by + dy, bx + dx]:
                    out[by + dy, bx + dx] = [62, 34, 14, 255]
            out[by, bx] = [238, 184, 74, 255]
            if not keepout[by - 1, bx] and not ext[by - 1, bx]:
                out[by - 1, bx] = [250, 214, 118, 255]

    # Guarantee 0 pixel on any walkable 8x8 tile!
    for tx in range(tw):
        for ty in range(th):
            if walk_tile[tx, ty]:
                out[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = 0
    return out


def reconstruct_window_ds(
    src_rgba: np.ndarray,
    jour_rgba: np.ndarray,
    raw_base_crop: np.ndarray,
    ds_room_crop: np.ndarray,
    amb: str,
) -> Image.Image:
    """
    Reconstructs a window `.dir` object in crisp DS style:
    - Frame & mullions match `ds_room_crop` seamlessly (0 RGB seam when `SetDestinyAmbiance` tints by `WORLD_TINTS[amb]`!)
    - Sky/sunset/starlight panes quantized onto crisp 8-color DS sky palette + engine tint pre-compensation!
    """
    h, w, _ = src_rgba.shape
    mask = src_rgba[..., 3] >= 128

    # Identify wooden frame & mullions on Jour reference (`diff < 22` from raw base room crop, OR warm low-blue wood on Jour)
    diff_base = np.max(np.abs(jour_rgba[..., :3].astype(int) - raw_base_crop.astype(int)), axis=2)
    jr, jg, jb = jour_rgba[..., 0].astype(int), jour_rgba[..., 1].astype(int), jour_rgba[..., 2].astype(int)
    is_wood_frame = mask & ((diff_base < 22) | ((jg - jb >= 26) & (jr > jg + 16) & (jb < 95)))
    is_glass = mask & (~is_wood_frame)

    # S-curve sharpen & quantize sky/glass pixels to 8 crisp DS colors!
    glass_rgb = src_rgba[..., :3].astype(np.float32).copy()
    L = 0.299 * glass_rgb[..., 0] + 0.587 * glass_rgb[..., 1] + 0.114 * glass_rgb[..., 2]
    lmin = ndimage.minimum_filter(L, size=3)
    lmax = ndimage.maximum_filter(L, size=3)
    span = lmax - lmin
    u = np.clip((L - lmin) / np.maximum(span, 1e-4), 0.0, 1.0)
    us = u * u * (3.0 - 2.0 * u)
    gain = (L + 0.55 * ((lmin + us * span) - L) + 1.0) / (L + 1.0)
    glass_s = np.clip(glass_rgb * gain[..., None], 0.0, 255.0).astype(np.uint8)

    if np.any(is_glass):
        probe = glass_s.copy()
        # Fill non-glass with median glass color so MEDIANCUT spends all 8 palette entries on the sky/clouds/stars!
        med_g = np.median(glass_s[is_glass], axis=0).astype(np.uint8)
        probe[~is_glass] = med_g
        q_glass = np.array(
            Image.fromarray(probe, "RGB")
            .quantize(colors=8, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            .convert("RGB")
        )
    else:
        q_glass = glass_s

    # Precompensate ONLY the glowing sky/starlight glass panes for `SetDestinyAmbiance(moment, true)`!
    # Keep wooden frame at exact `ds_room_crop` so `ds_room_crop * wt == wall * wt` -> 0.0 seam in all 4 ambiances!
    if amb != "jour":
        wt = WORLD_TINTS[amb][None, None, :]
        gain_amb = (0.75 + 0.25 * wt) / np.maximum(wt, 0.20)
        q_glass = np.clip(np.round(q_glass.astype(np.float32) * gain_amb), 0.0, 255.0).astype(np.uint8)

    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[is_wood_frame, :3] = ds_room_crop[is_wood_frame]
    out[is_glass, :3] = q_glass[is_glass]
    out[mask, 3] = 255
    return Image.fromarray(sanitize_patch_anti_magenta(out), "RGBA")


def build_halcyon_layers_json(
    arch_bank: DedupTileBankBuilder,
    verd_bank: DedupTileBankBuilder,
    floor_rgba: np.ndarray,
    walls_rgba: np.ndarray,
    shadows_rgba: np.ndarray,
    garland_rgba: np.ndarray,
    supports_rgba: np.ndarray,
) -> list[dict]:
    h, w, _ = floor_rgba.shape
    tw, th = w // 8, h // 8
    return [
        {"Name": "Floor", "Layer": 0, "Visible": True, "Tiles": arch_bank.encode_rgba_layer(floor_rgba)},
        {"Name": "Walls", "Layer": 0, "Visible": True, "Tiles": arch_bank.encode_rgba_layer(walls_rgba)},
        {"Name": "Shadows", "Layer": 0, "Visible": True, "Tiles": arch_bank.encode_rgba_layer(shadows_rgba)},
        {"Name": "Objects Under", "Layer": 0, "Visible": True, "Tiles": empty_tile_grid(tw, th)},
        {"Name": "Objects", "Layer": 0, "Visible": True, "Tiles": empty_tile_grid(tw, th)},
        {"Name": "Objects Over", "Layer": 0, "Visible": True, "Tiles": empty_tile_grid(tw, th)},
        {"Name": "Fringe", "Layer": 4, "Visible": True, "Tiles": verd_bank.encode_rgba_layer(garland_rgba)},
        {"Name": "Supports", "Layer": 4, "Visible": True, "Tiles": arch_bank.encode_rgba_layer(supports_rgba)},
    ]


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    verd_bank = DedupTileBankBuilder("Destiny_Guilde_Verdure", cols=32)

    room_specs = [
        ("guilde_destiny_missions", "Destiny_Guilde_Missions", "02_missions", False),
        ("guilde_destiny_grand_salon", "Destiny_Guilde_Grand_Salon", "03_grand_salon_central", False),
        ("guilde_destiny_bureau_maitre", "Destiny_Guilde_Bureau_Maitre", "04_bureau_maitre", False),
        ("guilde_destiny_carrefour", "Destiny_Guilde_Carrefour", "05b_carrefour_ouest", False),
        ("guilde_destiny_refectoire", "Destiny_Guilde_Refectoire", "05_refectoire", False),
        ("guilde_destiny_cuisine", "Destiny_Guilde_Cuisine", "06_cuisine", False),
        ("guilde_destiny_reserve", "Destiny_Guilde_Reserve", "10_dortoir_sud", False),
        ("guilde_destiny_couloir_ouest", "Destiny_Guilde_Couloir_Ouest", "08_couloir_dortoirs", False),
        ("guilde_destiny_couloir_est", "Destiny_Guilde_Couloir_Est", "08_couloir_dortoirs", True),
        ("guilde_destiny_dortoir_nord_1", "Destiny_Guilde_Dortoir_Nord_1", "09_dortoir_nord", False),
        ("guilde_destiny_dortoir_nord_2", "Destiny_Guilde_Dortoir_Nord_2", "09_dortoir_nord", True),
        ("guilde_destiny_dortoir_sud_1", "Destiny_Guilde_Dortoir_Sud_1", "10_dortoir_sud", False),
        ("guilde_destiny_dortoir_sud_2", "Destiny_Guilde_Dortoir_Sud_2", "10_dortoir_sud", True),
        ("guilde_destiny_chambre_heros", "Destiny_Guilde_Chambre_Heros", "11_chambre_heros", False),
    ]

    ds_room_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    # 1. Reconstruct all 14 1x rooms + Grand Salon double door `.dir` objects
    door_meta = manifest["porte_grand_salon"]
    dx, dy, dw, dh = int(door_meta["x"]), int(door_meta["y"]), int(door_meta["w"]), int(door_meta["h"])

    for idx_r, (map_id, sheet_name, src_stem, flip_h) in enumerate(room_specs):
        rs_path = GROUND_DIR / f"{map_id}.rsground"
        doc = json.loads(rs_path.read_text(encoding="utf-8-sig"))
        g = doc["Object"]
        obs = g["obstacles"]
        tw, th = len(obs), len(obs[0])
        w, h = tw * 8, th * 8
        walk_tile = np.array([[obs[tx][ty]["Tags"] == 0 for ty in range(th)] for tx in range(tw)], dtype=bool)
        walk_px = np.repeat(np.repeat(walk_tile.T, 8, axis=0), 8, axis=1)

        base_im = Image.open(BASE_DIR / f"{src_stem}_1x_base.png").convert("RGB")
        if flip_h:
            base_im = base_im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        raw_rgb = np.array(base_im)

        is_ext = (
            (np.abs(raw_rgb[..., 0].astype(np.int16) - 104) <= 4)
            & (np.abs(raw_rgb[..., 1].astype(np.int16) - 72) <= 4)
            & (np.abs(raw_rgb[..., 2].astype(np.int16) - 47) <= 4)
        )
        lbl_e, _ = ndimage.label(is_ext)
        b_lbls = set(np.unique(lbl_e[0, :])) | set(np.unique(lbl_e[-1, :])) | set(np.unique(lbl_e[:, 0])) | set(np.unique(lbl_e[:, -1]))
        b_lbls.discard(0)
        is_ext = np.isin(lbl_e, list(b_lbls))
        fg = ~is_ext

        seeds = [(m["Collider"]["X"] + 8, m["Collider"]["Y"] + 8) for m in g["Entities"][0]["Markers"]]
        is_floor_px = extract_exact_floor_mask(raw_rgb, fg, walk_px, seeds, scale=1)
        ds_rgb, is_recess = reconstruct_ds_pixels(raw_rgb, is_ext, is_floor_px, scale=1)
        ds_room_cache[map_id] = (raw_rgb, ds_rgb)

        # If Grand Salon: reconstruct `PorteSalonFermee` & `PorteSalonOuverte` IN PLACE inside `raw_rgb` -> 0.0 RGB seam!
        if map_id == "guilde_destiny_grand_salon":
            (ART_RESEAU / "porte_grand_salon").mkdir(parents=True, exist_ok=True)
            for png_key, dst_stem in [
                ("fermee_png", "Guilde_Destiny_Porte_Salon_Fermee"),
                ("ouverte_png", "Guilde_Destiny_Porte_Salon_Ouverte"),
            ]:
                p_src = Path(door_meta[png_key])
                if not p_src.exists():
                    p_src = ART_RESEAU / "porte_grand_salon" / f"{dst_stem}.png"
                door_rgba = np.array(Image.open(p_src).convert("RGBA"))
                comp_door = raw_rgb.copy()
                a_m = door_rgba[..., 3:4] >= 128
                comp_door[dy : dy + dh, dx : dx + dw] = np.where(a_m, door_rgba[..., :3], comp_door[dy : dy + dh, dx : dx + dw])
                ds_door_full, _ = reconstruct_ds_pixels(comp_door, is_ext, is_floor_px, scale=1)
                door_crop_rgb = ds_door_full[dy : dy + dh, dx : dx + dw]
                door_out_rgba = np.dstack([door_crop_rgb, np.where(door_rgba[..., 3] >= 128, 255, 0).astype(np.uint8)])
                door_im = Image.fromarray(door_out_rgba, "RGBA")
                write_dir(OBJ_DIR / f"{dst_stem}.dir", door_im, dw, dh)
                door_im.save(ART_RESEAU / "porte_grand_salon" / f"{dst_stem}.png")
                print(f"[OK] Door {dst_stem}: {len(np.unique(door_crop_rgb.reshape(-1, 3), axis=0))} DS colors (0 seam)")

        floor_rgba, walls_rgba, shadows_rgba, supports_rgba = decompose_halcyon_layers(
            ds_rgb, is_ext, is_floor_px, is_recess, walk_tile, scale=1
        )

        wins = []
        for s in manifest["fenetres_par_salle"].get(src_stem, []):
            sx = (w - s["x"] - s["w"]) if flip_h else s["x"]
            wins.append({"x": sx, "y": s["y"], "w": s["w"], "h": s["h"]})

        garland_rgba = generate_ds_garland_rgba(
            ds_rgb,
            walk_tile,
            wins,
            north_arch_x=NORTH_ARCH_SPANS.get(map_id),
            split_gap_x=SPLIT_GAP_SPANS.get(map_id),
            door_keepout=(dx, dy, dw, dh) if map_id == "guilde_destiny_grand_salon" else None,
            seed=101 + idx_r * 17,
        )

        arch_bank = DedupTileBankBuilder(sheet_name, cols=32)
        g["Layers"] = build_halcyon_layers_json(
            arch_bank, verd_bank, floor_rgba, walls_rgba, shadows_rgba, garland_rgba, supports_rgba
        )
        n_arch = arch_bank.write(TILE_DIR)
        rs_path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        n_col = len(np.unique(ds_rgb.reshape(-1, 3), axis=0))
        fr_n = sum(1 for col in g["Layers"][6]["Tiles"] for t in col if t.get("Layers"))
        su_n = sum(1 for col in g["Layers"][7]["Tiles"] for t in col if t.get("Layers"))
        print(f"[OK] {map_id:32s}: {n_col} DS colors, {n_arch:4d} arch tiles, Fringe={fr_n:3d}, Supports={su_n:3d}")

    # 2. Reconstruct `guilde_destiny_accueil` (`1536x1152`, `192x144` tiles, `scale=3`) in DS + Halcyon 8-layer schema!
    acc_rs_path = GROUND_DIR / "guilde_destiny_accueil.rsground"
    acc_doc = json.loads(acc_rs_path.read_text(encoding="utf-8-sig"))
    acc_g = acc_doc["Object"]
    acc_obs = acc_g["obstacles"]
    acc_tw, acc_th = len(acc_obs), len(acc_obs[0])
    acc_walk_tile = np.array([[acc_obs[tx][ty]["Tags"] == 0 for ty in range(acc_th)] for tx in range(acc_tw)], dtype=bool)
    acc_walk_px = np.repeat(np.repeat(acc_walk_tile.T, 8, axis=0), 8, axis=1)

    acc_raw_rgb = np.array(Image.open(BASE_DIR / "00_accueil_1536x1152_base.png").convert("RGB"))
    acc_ext = (
        (np.abs(acc_raw_rgb[..., 0].astype(np.int16) - 104) <= 6)
        & (np.abs(acc_raw_rgb[..., 1].astype(np.int16) - 72) <= 6)
        & (np.abs(acc_raw_rgb[..., 2].astype(np.int16) - 47) <= 6)
    )
    lbl_ae, _ = ndimage.label(acc_ext)
    ab_lbls = set(np.unique(lbl_ae[0, :])) | set(np.unique(lbl_ae[-1, :])) | set(np.unique(lbl_ae[:, 0])) | set(np.unique(lbl_ae[:, -1]))
    ab_lbls.discard(0)
    acc_ext = np.isin(lbl_ae, list(ab_lbls))
    acc_fg = ~acc_ext

    acc_seeds = [(m["Collider"]["X"] + 8, m["Collider"]["Y"] + 8) for m in acc_g["Entities"][0]["Markers"]]
    acc_floor_px = extract_exact_floor_mask(acc_raw_rgb, acc_fg, acc_walk_px, acc_seeds, scale=3)
    acc_ds_rgb, acc_recess = reconstruct_ds_pixels(acc_raw_rgb, acc_ext, acc_floor_px, scale=3)
    acc_fl, acc_wa, acc_sh, acc_su = decompose_halcyon_layers(
        acc_ds_rgb, acc_ext, acc_floor_px, acc_recess, acc_walk_tile, scale=3
    )

    acc_1x_rgb = np.array(Image.open(BASE_DIR / "01_accueil_1x_base.png").convert("RGB"))
    acc_wins_1x = manifest["fenetres_par_salle"]["01_accueil"]
    acc_walk_1x = acc_walk_tile[::3, ::3]
    acc_garland_1x = generate_ds_garland_rgba(acc_1x_rgb, acc_walk_1x, acc_wins_1x, split_gap_x=(220, 292), seed=77)
    acc_garland_3x = np.array(Image.fromarray(acc_garland_1x, "RGBA").resize((1536, 1152), Image.Resampling.NEAREST))
    for tx in range(acc_tw):
        for ty in range(acc_th):
            if acc_walk_tile[tx, ty]:
                acc_garland_3x[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = 0

    acc_bank = DedupTileBankBuilder("Destiny_Guilde_Accueil", cols=64)
    acc_g["Layers"] = build_halcyon_layers_json(
        acc_bank, verd_bank, acc_fl, acc_wa, acc_sh, acc_garland_3x, acc_su
    )
    n_acc_tiles = acc_bank.write(TILE_DIR)
    n_verd_tiles = verd_bank.write(TILE_DIR)
    acc_rs_path.write_text(json.dumps(acc_doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(
        f"[OK] {'guilde_destiny_accueil':32s}: {len(np.unique(acc_ds_rgb.reshape(-1, 3), axis=0))} DS colors, "
        f"{n_acc_tiles:4d} arch tiles (Destiny_Guilde_Verdure={n_verd_tiles} tiles)"
    )

    # 3. Reconstruct all 60 `Guilde_Fenetre_*` `.dir` objects in crisp DS style (seamless wood frame + 8-color DS sky)!
    # 3a. Accueil 3x windows (`Guilde_Fenetre_Accueil_{Gauche,Droite}_{Amb}`)
    for slot in manifest["fenetres_par_salle"]["01_accueil"]:
        side = slot["slot"]
        w3, h3 = slot["w"] * 3, slot["h"] * 3
        x3, y3 = slot["x"] * 3, slot["y"] * 3
        raw_crop3 = acc_raw_rgb[y3 : y3 + h3, x3 : x3 + w3]
        ds_crop3 = acc_ds_rgb[y3 : y3 + h3, x3 : x3 + w3]
        jour_src3 = np.array(Image.open(slot["ambiances"]["jour"]["png"]).convert("RGBA").resize((w3, h3), Image.Resampling.NEAREST))
        for amb in AMBIANCES:
            src3 = np.array(Image.open(slot["ambiances"][amb]["png"]).convert("RGBA").resize((w3, h3), Image.Resampling.NEAREST))
            win_im = reconstruct_window_ds(src3, jour_src3, raw_crop3, ds_crop3, amb)
            write_dir(OBJ_DIR / f"Guilde_Fenetre_Accueil_{side}_{amb.capitalize()}.dir", win_im, w3, h3)

    # 3b. Standard 1x room windows + mirrored Dortoir Nord 2
    win_room_map = {
        "guilde_destiny_missions": ("02_missions", False),
        "guilde_destiny_grand_salon": ("03_grand_salon_central", False),
        "guilde_destiny_bureau_maitre": ("04_bureau_maitre", False),
        "guilde_destiny_refectoire": ("05_refectoire", False),
        "guilde_destiny_cuisine": ("06_cuisine", False),
        "guilde_destiny_dortoir_nord_1": ("09_dortoir_nord", False),
        "guilde_destiny_dortoir_nord_2": ("09_dortoir_nord", True),
        "guilde_destiny_chambre_heros": ("11_chambre_heros", False),
    }
    win_count = 8
    for map_id, (src_id, flip_h) in win_room_map.items():
        raw_r, ds_r = ds_room_cache[map_id]
        rw = raw_r.shape[1]
        for slot in manifest["fenetres_par_salle"].get(src_id, []):
            sw, sh = slot["w"], slot["h"]
            sx = (rw - slot["x"] - sw) if flip_h else slot["x"]
            sy = slot["y"]
            raw_c = raw_r[sy : sy + sh, sx : sx + sw]
            ds_c = ds_r[sy : sy + sh, sx : sx + sw]
            j_im = Image.open(slot["ambiances"]["jour"]["png"]).convert("RGBA")
            if flip_h:
                j_im = j_im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            jour_rgba = np.array(j_im)
            for amb in AMBIANCES:
                s_im = Image.open(slot["ambiances"][amb]["png"]).convert("RGBA")
                if flip_h:
                    s_im = s_im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                win_im = reconstruct_window_ds(np.array(s_im), jour_rgba, raw_c, ds_c, amb)
                suffix = "_Miroir" if flip_h else ""
                dname = f"Guilde_Fenetre_{src_id}_{slot['slot']}{suffix}_{amb.capitalize()}"
                write_dir(OBJ_DIR / f"{dname}.dir", win_im, sw, sh)
                win_count += 1
    print(f"[OK] Reconstructed {win_count} Guilde_Fenetre_*.dir objects in crisp DS style")


if __name__ == "__main__":
    main()
