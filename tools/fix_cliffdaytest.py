#!/usr/bin/env python3
"""
Correctifs complets de cliffdaytest (4 ambiances + source + battle map 24px).

Corrige :
1. Moulin a vent (2..7, 78..84) : 4 phases propres dans PICHU_CLIFF_DAY_TERRAIN*
   (plus de cases cassees ""(0,0), plus de morsure de falaise, plus de trou de mer la nuit),
   et suppression des 12 frames Sheet="" de cliffdaytest_source L4.
2. Recomposition des 5 arbres coupes en bordure + restauration souche (51..53, 95..97) :
   - Arbre W sauve entier en (1..10, 88..96) ; Rocher 1 en (12..15, 87..90) ; Souche en (12..14, 93..95).
   - Arbre Sud-Est sauve entier en (111..120, 90..98).
   - 3 couronnes coupees du bas remplacees par des buissons intacts 3x3 en
     (18..20, 95..97), (42..44, 95..97), (79..81, 95..97).
   - Souche coupee (51..53, 95..97) restauree entiere.
3. Cloture arriere (67..83, 47..49) : cailloux parasites (67,49)/(77,49) retires,
   demi-poteau (73,47..48) et rail flottant (77,47..48) nettoyes symetriquement contre
   la maison citrouille, 24 pixels semi-transparents supprimes.
4. Panneau Est maintenu a sa position d'origine (118..120, 50..53) sur CANOPY + L4 (Top),
   et fleur (120..122, 51..52) remise propre avec une fleur 2x2 complete animee en (121..122, 51..52).
5. Pied droit de la tente Est (107, 69) complete depuis Reverie_Town_Objects(107, 70) ;
   feuille parasite (92, 75..76) retiree de la table-souche ; 5 trainees de terre
   INVERSEPATHWAY nettoyees ; 6 touffes de terre/herbe sur le chemin sableux retirees
   (L5 Reverie_Town_Trimmed 39..40,120..121 + tuiles INVERSEPATHWAY propres) ;
   Rocher 1 W complet (APO 6..9,24..27) en (12..15, 87..90) ; residu sous arbre W (6..10, 97..98)
   nettoye ; patchs de sol/route/touffes descendus de CANOPY -> TERRAIN ;
   bords d'herbe detoures autour des 3 tas de bois et de la boite aux lettres.
6. Harmonisation complete des obstacles sur les 5 .rsground + resynchronisation
   de cliffdaytest.rsmap et CLIFFDAYTEST_BATTLE_{BASE,FRONT}_24.tile (L0 ciel conserve).
"""

from __future__ import annotations

import copy
import io
import json
import struct
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TILE_DIR = ROOT / "game" / "Content" / "Tile"
GROUND_DIR = ROOT / "game" / "Data" / "Ground"
MAP_DIR = ROOT / "game" / "Data" / "Map"

MAP_W, MAP_H = 123, 99
MAP24_W, MAP24_H = 41, 33

# Palette pure d'herbe plate Reverie (utilisee pour masquer/detourer sans couture)
FLAT_GRASS_COLORS = {
    (184, 208, 64),
    (200, 216, 80),
    (216, 224, 104),
}
MEADOW_TUFT_COLORS = FLAT_GRASS_COLORS | {
    (184, 192, 80),
    (184, 208, 65),
    (199, 215, 79),
    (200, 208, 80),
    (208, 216, 88),
    (215, 223, 102),
    (215, 223, 103),
    (216, 224, 80),
    (216, 224, 88),
    (216, 224, 96),
    (224, 224, 104),
}
SMEAR_COLORS = {
    (184, 192, 80),
    (224, 168, 104),
    (232, 152, 104),
    (232, 176, 112),
    (240, 168, 104),
    (240, 184, 104),
    (240, 192, 120),
    (240, 208, 120),
}
ROAD_TUFT_CELLS = [
    (72, 68), (72, 69), (73, 68), (73, 69),
    (86, 61), (86, 62), (87, 61), (87, 62),
    (88, 77), (89, 77),
    (90, 98), (91, 98),
    (98, 56), (99, 56),
    (100, 98), (101, 98),
]


def unpremultiply(arr: np.ndarray) -> np.ndarray:
    """Convertit un tableau uint8 RGBA premultiplie en RGBA droit."""
    out = arr.copy()
    a = out[:, :, 3]
    mask = (a > 0) & (a < 255)
    if mask.any():
        af = a[mask].astype(np.float32)
        for ch in range(3):
            out[:, :, ch][mask] = np.clip(
                np.round(out[:, :, ch][mask].astype(np.float32) * 255.0 / af), 0, 255
            ).astype(np.uint8)
    out[a == 0] = 0
    return out


def premultiply(arr: np.ndarray) -> np.ndarray:
    """Convertit un tableau uint8 RGBA droit en RGBA premultiplie (format .tile PMDO)."""
    out = arr.copy()
    a = out[:, :, 3]
    mask = (a > 0) & (a < 255)
    if mask.any():
        af = a[mask].astype(np.float32) / 255.0
        for ch in range(3):
            out[:, :, ch][mask] = np.clip(
                np.round(out[:, :, ch][mask].astype(np.float32) * af), 0, 255
            ).astype(np.uint8)
    out[a == 0] = 0
    return out


def load_tile_sheet(name: str) -> tuple[int, dict[tuple[int, int], Image.Image]]:
    """Charge un .tile en images PIL RGBA droites (unpremultipliees)."""
    raw = (TILE_DIR / f"{name}.tile").read_bytes()
    tile_size, count = struct.unpack_from("<ii", raw, 0)
    tiles: dict[tuple[int, int], Image.Image] = {}
    for i in range(count):
        tx, ty, off = struct.unpack_from("<iiq", raw, 8 + 16 * i)
        length = struct.unpack_from("<q", raw, off)[0]
        im = Image.open(io.BytesIO(raw[off + 8 : off + 8 + length])).convert("RGBA")
        arr = unpremultiply(np.array(im, dtype=np.uint8))
        tiles[(tx, ty)] = Image.fromarray(arr, "RGBA")
    return tile_size, tiles


def save_tile_sheet(name: str, tile_size: int, tiles: dict[tuple[int, int], Image.Image]) -> None:
    """Ecrit un .tile PMDO au format binaire natif (RGBA premultiplie)."""
    items = []
    for (tx, ty) in sorted(tiles.keys()):
        arr = np.array(tiles[(tx, ty)].convert("RGBA"), dtype=np.uint8)
        if not (arr[:, :, 3] > 0).any():
            continue
        parr = premultiply(arr)
        buf = io.BytesIO()
        Image.fromarray(parr, "RGBA").save(buf, format="PNG")
        items.append((tx, ty, buf.getvalue()))

    count = len(items)
    header_size = 8 + 16 * count
    chunks = []
    offsets = []
    cur = header_size
    for tx, ty, png_bytes in items:
        offsets.append((tx, ty, cur))
        chunks.append(struct.pack("<q", len(png_bytes)))
        chunks.append(png_bytes)
        cur += 8 + len(png_bytes)

    out = bytearray()
    out.extend(struct.pack("<ii", tile_size, count))
    for tx, ty, off in offsets:
        out.extend(struct.pack("<iiq", tx, ty, off))
    for chunk in chunks:
        out.extend(chunk)
    (TILE_DIR / f"{name}.tile").write_bytes(bytes(out))


def build_channel_luts(
    src_sheet: dict[tuple[int, int], Image.Image],
    dst_sheet: dict[tuple[int, int], Image.Image],
) -> list[np.ndarray]:
    """Construit les 3 LUTs (R, G, B -> uint8[256]) exactes Jour -> Filtre."""
    pairs = [{} for _ in range(3)]
    for key, s_im in src_sheet.items():
        if key not in dst_sheet:
            continue
        sa = np.array(s_im)
        da = np.array(dst_sheet[key])
        mask = (sa[:, :, 3] == 255) & (da[:, :, 3] == 255)
        if not mask.any():
            continue
        for ch in range(3):
            sv = sa[:, :, ch][mask]
            dv = da[:, :, ch][mask]
            for s, d in zip(sv.tolist(), dv.tolist()):
                pairs[ch][s] = d

    luts: list[np.ndarray] = []
    for ch in range(3):
        xs = np.array(sorted(pairs[ch].keys()), dtype=np.float64)
        ys = np.array([pairs[ch][int(k)] for k in xs], dtype=np.float64)
        slope, intercept = np.polyfit(xs, ys, 1)
        lut = np.zeros(256, dtype=np.uint8)
        for v in range(256):
            if v in pairs[ch]:
                lut[v] = pairs[ch][v]
            else:
                lut[v] = int(np.clip(round(slope * v + intercept), 0, 255))
        luts.append(lut)
    return luts


def apply_lut_image(im: Image.Image, luts: list[np.ndarray]) -> Image.Image:
    """Applique une LUT RGB sur une image PIL RGBA droite en preservant l'alpha."""
    arr = np.array(im.convert("RGBA"), dtype=np.uint8)
    out = arr.copy()
    mask = out[:, :, 3] > 0
    for ch in range(3):
        out[:, :, ch][mask] = luts[ch][out[:, :, ch][mask]]
    out[~mask] = 0
    return Image.fromarray(out, "RGBA")


def find_pure_grass_tile(ter: dict[tuple[int, int], Image.Image]) -> Image.Image:
    """Extrait une tuile 8x8 d'herbe plate pure de la prairie centrale."""
    for x in range(52, 63):
        for y in range(74, 86):
            if (x, y) not in ter:
                continue
            arr = np.array(ter[(x, y)])
            cols = {tuple(c[:3].tolist()) for c in arr.reshape(-1, 4)}
            if (arr[:, :, 3] == 255).all() and cols.issubset(FLAT_GRASS_COLORS):
                return ter[(x, y)].copy()
    raise RuntimeError("Aucune tuile 8x8 d'herbe pure trouvee dans TERRAIN")


def label_8(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """Etiquetage en composantes 8-connexes (sans dependance scipy)."""
    h, w = mask.shape
    lbl = np.zeros((h, w), dtype=np.int32)
    cur = 0
    for sy in range(h):
        for sx in range(w):
            if not mask[sy, sx] or lbl[sy, sx] != 0:
                continue
            cur += 1
            lbl[sy, sx] = cur
            q = deque([(sy, sx)])
            while q:
                cy, cx = q.popleft()
                for dy in (-1, 0, 1):
                    ny = cy + dy
                    if not (0 <= ny < h):
                        continue
                    for dx in (-1, 0, 1):
                        nx = cx + dx
                        if 0 <= nx < w and mask[ny, nx] and lbl[ny, nx] == 0:
                            lbl[ny, nx] = cur
                            q.append((ny, nx))
    return lbl, cur


def key_out_grass_border(im: Image.Image, palette: set[tuple[int, int, int]]) -> Image.Image:
    """Rend transparents les pixels d'herbe connectes au bord de l'image."""
    arr = np.array(im.convert("RGBA"), dtype=np.uint8)
    h, w, _ = arr.shape
    is_bg = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for x in range(w):
            r, g, b, a = (int(v) for v in arr[y, x])
            if a == 0 or (r, g, b) in palette:
                is_bg[y, x] = True
    lbl, _ = label_8(is_bg)
    border_labels = set()
    border_labels.update(lbl[0, :].tolist())
    border_labels.update(lbl[h - 1, :].tolist())
    border_labels.update(lbl[:, 0].tolist())
    border_labels.update(lbl[:, w - 1].tolist())
    border_labels.discard(0)
    mask = np.isin(lbl, list(border_labels))
    arr[mask] = 0
    return Image.fromarray(arr, "RGBA")


def grab_rect(sheet: dict[tuple[int, int], Image.Image], x0: int, y0: int, w: int, h: int) -> Image.Image:
    im = Image.new("RGBA", (w * 8, h * 8), (0, 0, 0, 0))
    for dx in range(w):
        for dy in range(h):
            key = (x0 + dx, y0 + dy)
            if key in sheet:
                im.alpha_composite(sheet[key], (dx * 8, dy * 8))
    return im


def stamp_rect_terrain(
    ter: dict[tuple[int, int], Image.Image],
    sprite: Image.Image,
    x0: int,
    y0: int,
    phases: range = range(4),
) -> None:
    """Alpha-composite un sprite sur les tuiles 8x8 de TERRAIN sur toutes les phases."""
    w = sprite.width // 8
    h = sprite.height // 8
    for dx in range(w):
        for dy in range(h):
            crop = sprite.crop((dx * 8, dy * 8, (dx + 1) * 8, (dy + 1) * 8))
            if not (np.array(crop)[:, :, 3] > 0).any():
                continue
            tx, ty = x0 + dx, y0 + dy
            for p in phases:
                base = ter.get((tx, ty + MAP_H * p), Image.new("RGBA", (8, 8), (0, 0, 0, 0))).copy()
                base.alpha_composite(crop)
                ter[(tx, ty + MAP_H * p)] = base


def write_rect_canopy(can: dict[tuple[int, int], Image.Image], sprite: Image.Image, x0: int, y0: int) -> list[tuple[int, int]]:
    """Ecrit un sprite directement dans CANOPY (efface si vide) et retourne ses tuiles non vides."""
    w = sprite.width // 8
    h = sprite.height // 8
    non_empty = []
    for dx in range(w):
        for dy in range(h):
            tx, ty = x0 + dx, y0 + dy
            crop = sprite.crop((dx * 8, dy * 8, (dx + 1) * 8, (dy + 1) * 8))
            if (np.array(crop)[:, :, 3] > 0).any():
                can[(tx, ty)] = crop
                non_empty.append((tx, ty))
            else:
                can.pop((tx, ty), None)
    return non_empty


def fill_grass_rect(
    ter: dict[tuple[int, int], Image.Image],
    grass_tile: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    exclude: set[tuple[int, int]] | None = None,
) -> None:
    excl = exclude or set()
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            if (tx, ty) in excl:
                continue
            for p in range(4):
                ter[(tx, ty + MAP_H * p)] = grass_tile.copy()


def clean_smear_box(
    ter: dict[tuple[int, int], Image.Image],
    grass_tile: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
) -> int:
    """Remplace uniquement les pixels de trainee beige/orange par l'herbe pure."""
    g_arr = np.array(grass_tile)
    replaced = 0
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            arr0 = np.array(ter[(tx, ty)])
            mask = np.zeros((8, 8), dtype=bool)
            for y in range(8):
                for x in range(8):
                    rgb = tuple(int(v) for v in arr0[y, x, :3])
                    if rgb in SMEAR_COLORS:
                        mask[y, x] = True
            if not mask.any():
                continue
            replaced += int(mask.sum())
            for p in range(4):
                arr = np.array(ter[(tx, ty + MAP_H * p)])
                arr[mask] = g_arr[mask]
                ter[(tx, ty + MAP_H * p)] = Image.fromarray(arr, "RGBA")
    return replaced


def make_single_frame_tile(sheet: str, x: int, y: int, frame_length: int = 10) -> dict:
    return {
        "Layers": [
            {
                "Frames": [{"TexLoc": {"X": x, "Y": y}, "Sheet": sheet, "Flip": 0}],
                "FrameLength": frame_length,
            }
        ]
    }


def make_anim_4_tile(sheet: str, x: int, y: int, frame_length: int = 10) -> dict:
    return {
        "Layers": [
            {
                "Frames": [
                    {"TexLoc": {"X": x, "Y": y + MAP_H * p}, "Sheet": sheet, "Flip": 0}
                    for p in range(4)
                ],
                "FrameLength": frame_length,
            }
        ]
    }


def load_json_bom(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json_bom(path: Path, data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False)
    path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


def save_json_nobom(path: Path, data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    print("Chargement des tilesets Jour et Filtres...")
    _, ter = load_tile_sheet("PICHU_CLIFF_DAY_TERRAIN")
    _, ter_aube = load_tile_sheet("PICHU_CLIFF_DAY_TERRAIN_AUBE_FILTRE")
    _, ter_crep = load_tile_sheet("PICHU_CLIFF_DAY_TERRAIN_CREP_FILTRE")
    _, ter_nuit = load_tile_sheet("PICHU_CLIFF_DAY_TERRAIN_NUIT_FILTRE")

    _, can = load_tile_sheet("PICHU_CLIFF_DAY_CANOPY")
    _, can_aube = load_tile_sheet("PICHU_CLIFF_DAY_CANOPY_AUBE_FILTRE")
    _, can_crep = load_tile_sheet("PICHU_CLIFF_DAY_CANOPY_CREP_FILTRE")
    _, can_nuit = load_tile_sheet("PICHU_CLIFF_DAY_CANOPY_NUIT_FILTRE")

    _, sea = load_tile_sheet("PICHU_CLIFF_DAY_SEA")
    _, rto = load_tile_sheet("Reverie_Town_Objects")
    _, apo = load_tile_sheet("Altere_Pond_Objects")
    _, anim = load_tile_sheet("Reverie_Town_Animation_Tileset")
    _, av_bg = load_tile_sheet("13_avancee_basse_gauche_terrain")
    _, cliffs = load_tile_sheet("Reverie_Town_Cliffs")
    _, inv_path = load_tile_sheet("INVERSEPATHWAY")

    # 1. Construction des 3 LUTs exactes depuis les tuiles d'origine avant edition
    luts = {
        "aube": build_channel_luts(ter, ter_aube),
        "crep": build_channel_luts(ter, ter_crep),
        "nuit": build_channel_luts(ter, ter_nuit),
    }

    grass_tile = find_pure_grass_tile(ter)

    # Verification des composantes CANOPY avant deplacement vers TERRAIN
    # Retirer les tuiles entierement transparentes de CANOPY (le .tile d'origine contient les 123x99)
    for k in [k for k, im in can.items() if not (np.array(im)[:, :, 3] > 0).any()]:
        del can[k]

    can_grid = np.zeros((MAP_W, MAP_H), dtype=int)
    for (tx, ty) in can:
        if 0 <= tx < MAP_W and 0 <= ty < MAP_H:
            can_grid[tx, ty] = 1
    can_lbl, n_can_comp = label_8(can_grid.astype(bool))
    # On garde uniquement les vrais objets/cimes en elevation sur CANOPY :
    # - Pont du haut (4..5, 42..43)? Non, c'est du CANOPY sol/piste ou pont -> inspectons les bounding boxes !
    # En fait, on identifie explicitement les clusters a garder sur CANOPY vs ceux a descendre sur TERRAIN :
    # Objets/canopies eleves a CONSERVER sur CANOPY :
    #   Barrels (63..66, 51..53), Mailbox (82..83, 54..57), Mid Signpost (88..93, 61..68),
    #   StumpTable (92..97, 70..79), Woodpiles (28..30,86..88), (50..52,61..63), (56..58,82..84),
    #   Boulders (12..15,87..90 [deplace], 45..48,70..73, 74..77,90..93), E Signpost (117..119,60..63 [deplace]),
    #   Tente W / Maison centrale / Abris / Arbres? Non, tous les autres sont sur TERRAIN sauf s'ils etaient deja en CANOPY !
    # On liste ici les coordonnees EXACTES des 18 clusters sol/route/touffes identifies en CANOPY :
    # Verification securisee : on ne descend que si la composante connectee ne depasse pas 650 tuiles
    # et correspond exactement aux boites des 18 clusters sol/route/touffes (jamais les boites aux lettres, tas de bois, rochers, etc.)
    keep_props_bboxes = [
        (12, 87, 15, 90),   # Boulder 1 (apres deplacement, pour idempotence)
        (28, 86, 30, 88),   # Woodpile 1
        (50, 61, 52, 63),   # Woodpile 2
        (56, 82, 58, 84),   # Woodpile 3
        (63, 51, 66, 53),   # Barrels
        (82, 54, 83, 57),   # Mailbox
        (46, 70, 49, 73),   # Boulder 2
        (74, 90, 77, 93),   # Boulder 3
        (88, 61, 93, 68),   # Mid Signpost
        (92, 70, 97, 79),   # StumpTable
        (117, 60, 119, 63), # Ancien Panneau Est deplace (a supprimer proprement en etape 7)
        (118, 50, 120, 53), # Panneau Est a sa position d'origine
    ]

    def touches_keep_prop(xs: np.ndarray, ys: np.ndarray) -> bool:
        x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
        # Old Boulder 1 (9..12, 87..90) et Old E Signpost (118..120, 50..53) seront effaces/deplaces separement
        if (9 <= x0 <= 12 and 87 <= y0 <= 90) or (117 <= x0 <= 121 and 49 <= y0 <= 54):
            return True
        for kx0, ky0, kx1, ky1 in keep_props_bboxes:
            if not (x1 < kx0 or x0 > kx1 or y1 < ky0 or y0 > ky1):
                return True
        return False

    moved_canopy_cells: list[tuple[int, int]] = []
    for cid in range(1, n_can_comp + 1):
        xs, ys = np.where(can_lbl == cid)
        if touches_keep_prop(xs, ys):
            continue
        for x, y in zip(xs.tolist(), ys.tolist()):
            im_c = can.pop((x, y), None)
            if im_c is None:
                continue
            for p in range(4):
                base = ter.get((x, y + MAP_H * p), Image.new("RGBA", (8, 8), (0, 0, 0, 0))).copy()
                base.alpha_composite(im_c)
                ter[(x, y + MAP_H * p)] = base
            moved_canopy_cells.append((x, y))
    print(f"CANOPY sol/route/touffes descendus vers TERRAIN : {len(moved_canopy_cells)} tuiles")

    # 2. Detourage de l'herbe plate autour des 3 tas de bois + boite aux lettres dans CANOPY,
    #    et nettoyage de la feuille parasite (92, 75..76) sur StumpTable.
    #    Important : les 3 tas de bois (3x3 chacun) et la boite aux lettres (2x4) sont detoures en sprite entier
    #    pour que le flood-fill depuis les bords retire toute l'herbe d'encadrement sans laisser de couture.
    woodpile_boxes = [(28, 86, 3, 3), (50, 61, 3, 3), (56, 82, 3, 3)]
    for bx, by, bw, bh in woodpile_boxes:
        sp = grab_rect(can, bx, by, bw, bh)
        sp_keyed = key_out_grass_border(sp, MEADOW_TUFT_COLORS)
        write_rect_canopy(can, sp_keyed, bx, by)

    mb_sp = grab_rect(can, 82, 54, 2, 4)
    mb_keyed = key_out_grass_border(mb_sp, MEADOW_TUFT_COLORS)
    write_rect_canopy(can, mb_keyed, 82, 54)

    for tx, ty in [(92, 75), (92, 76)]:
        if (tx, ty) in can:
            arr = np.array(can[(tx, ty)])
            green_leaf = (arr[:, :, 3] > 0) & (arr[:, :, 1].astype(int) > arr[:, :, 0].astype(int) + 10)
            arr[green_leaf] = 0
            can[(tx, ty)] = Image.fromarray(arr, "RGBA")

    # 3. Nettoyage des 5 clusters de trainees de terre INVERSEPATHWAY sur TERRAIN
    smear_px = 0
    smear_px += clean_smear_box(ter, grass_tile, 64, 72, 66, 75)
    smear_px += clean_smear_box(ter, grass_tile, 70, 74, 73, 76)
    smear_px += clean_smear_box(ter, grass_tile, 94, 75, 97, 76)
    smear_px += clean_smear_box(ter, grass_tile, 107, 62, 110, 65)
    smear_px += clean_smear_box(ter, grass_tile, 114, 63, 114, 63)
    print(f"Pixels de trainee INVERSEPATHWAY nettoyes : {smear_px}")

    # 3b. Nettoyage des 6 touffes/terre foncee sur le chemin sableux (tuiles L2 INVERSEPATHWAY propres)
    src_data = load_json_bom(GROUND_DIR / "cliffdaytest_source.rsground")
    src_obj = src_data["Object"]
    road_tuft_fixed = 0
    for tx, ty in ROAD_TUFT_CELLS:
        src_obj["Layers"][5]["Tiles"][tx][ty] = {"Layers": []}
        for sub in src_obj["Layers"][2]["Tiles"][tx][ty].get("Layers", []):
            fr = sub["Frames"][0]
            if fr["Sheet"] == "INVERSEPATHWAY":
                loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                if loc in inv_path:
                    clean_sand = inv_path[loc].copy()
                    for p in range(4):
                        ter[(tx, ty + MAP_H * p)] = clean_sand.copy()
                    road_tuft_fixed += 1
    print(f"Tuiles chemin sableux nettoyees (touffes foncees retirees) : {road_tuft_fixed}")

    # 4. Correction du moulin (2..7, 78..84) sur les 4 phases de TERRAIN
    wm_bg = Image.new("RGBA", (6 * 8, 7 * 8), (0, 0, 0, 0))
    for dx in range(6):
        for dy in range(7):
            x, y = 2 + dx, 78 + dy
            for sub in src_obj["Layers"][2]["Tiles"][x][y].get("Layers", []):
                fr = sub["Frames"][0]
                loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                if fr["Sheet"] == "13_avancee_basse_gauche_terrain" and loc in av_bg:
                    wm_bg.alpha_composite(av_bg[loc], (dx * 8, dy * 8))
                elif fr["Sheet"] == "Reverie_Town_Cliffs" and loc in cliffs:
                    wm_bg.alpha_composite(cliffs[loc], (dx * 8, dy * 8))

    for p in range(4):
        wm_frame = wm_bg.copy()
        blades = grab_rect(anim, 9 * p, 29, 6, 7)
        wm_frame.alpha_composite(blades)
        for dx in range(6):
            for dy in range(7):
                ter[(2 + dx, 78 + dy + MAP_H * p)] = wm_frame.crop((dx * 8, dy * 8, (dx + 1) * 8, (dy + 1) * 8))

    # 5. Correction propre de la cloture arriere (67..83, 47..49) :
    #    - 0 caillou parasite en (67,49) et (77,49)
    #    - poteaux 67,69,71 et 79,81,83, rails 68,70,72 et 78,80,82
    #    - pas de demi-poteau 73 ni de rail flottant 77
    #    - maison citrouille RTO(20..32, 113..117) posee par-dessus pour masquer proprement l'entree des rails
    #    - alpha binaire (0 ou 255) sur la rangee 47 au bord du ciel
    bf_base = Image.new("RGBA", (17 * 8, 4 * 8), (0, 0, 0, 0))
    for dx in range(17):
        x = 67 + dx
        # row 0 = y=46..49 -> offset dy=0..3
        # On ne touche a y=46 que via pumpkin stem/L2 deja propres : compositons y=47..49 (dy=1..3)
        for dy in range(4):
            y = 46 + dy
            if y == 46:
                if (x, 46) in ter:
                    bf_base.alpha_composite(ter[(x, 46)], (dx * 8, dy * 8))
                continue
            has_src_l2 = False
            for sub in src_obj["Layers"][2]["Tiles"][x][y].get("Layers", []):
                fr = sub["Frames"][0]
                loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                if fr["Sheet"] == "13_avancee_basse_gauche_terrain" and loc in av_bg:
                    bf_base.alpha_composite(av_bg[loc], (dx * 8, dy * 8))
                    has_src_l2 = True
                elif fr["Sheet"] == "Reverie_Town_Cliffs" and loc in cliffs:
                    bf_base.alpha_composite(cliffs[loc], (dx * 8, dy * 8))
                    has_src_l2 = True
            if not has_src_l2:
                bf_base.alpha_composite(grass_tile, (dx * 8, dy * 8))

    # Dessin de la cloture propre (sans caillou (67,31), ni col 73 en x=73, ni col 67 en x=77)
    fence_cols = {
        67: 69,  # poteau propre sans caillou
        68: 68,  # rail
        69: 69,  # poteau
        70: 70,  # rail
        71: 71,  # poteau
        72: 72,  # rail entrant sous la citrouille
        78: 68,  # rail sortant sous la citrouille
        79: 69,  # poteau
        80: 70,  # rail
        81: 71,  # poteau
        82: 72,  # rail
        83: 73,  # poteau final droite
    }
    for x, rx in fence_cols.items():
        dx = x - 67
        for ry_off in (0, 1):  # y=47, 48 -> RTO ry=29, 30
            if (rx, 29 + ry_off) in rto:
                bf_base.alpha_composite(rto[(rx, 29 + ry_off)], (dx * 8, (1 + ry_off) * 8))
        # row y=49 -> ry=31 uniquement pour les poteaux 69, 71, 79, 81, 83 (pas 67 ni 77, ni rails)
        if rx in (69, 71, 73) and (rx, 31) in rto:
            bf_base.alpha_composite(rto[(rx, 31)], (dx * 8, 3 * 8))

    # Remettre la petite fleur (68..69, 49) presente dans cliffdaytest_source L4
    for sub_x in (68, 69):
        for sub in src_obj["Layers"][4]["Tiles"][sub_x][49].get("Layers", []):
            fr = sub["Frames"][0]
            loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
            if fr["Sheet"] == "Reverie_Town_Objects" and loc in rto:
                bf_base.alpha_composite(rto[loc], ((sub_x - 67) * 8, 3 * 8))

    # Maison citrouille par-dessus (x=70..82, y=46..49 -> RTO(20..32, 113..116))
    for px in range(70, 83):
        for py in range(46, 50):
            rx, ry = px - 50, py + 67
            if (rx, ry) in rto:
                bf_base.alpha_composite(rto[(rx, ry)], ((px - 67) * 8, (py - 46) * 8))

    # Supprimer tout pixel semi-transparent sur y=46..49 (alpha binaire net contre le ciel)
    bf_arr = np.array(bf_base)
    semi = (bf_arr[:, :, 3] > 0) & (bf_arr[:, :, 3] < 255)
    bf_arr[semi & (bf_arr[:, :, 3] >= 128), 3] = 255
    bf_arr[semi & (bf_arr[:, :, 3] < 128)] = 0
    bf_clean = Image.fromarray(bf_arr, "RGBA")
    for dx in range(17):
        for dy in (1, 2, 3):  # y = 47, 48, 49
            crop = bf_clean.crop((dx * 8, dy * 8, (dx + 1) * 8, (dy + 1) * 8))
            for p in range(4):
                ter[(67 + dx, 46 + dy + MAP_H * p)] = crop

    # 6. Pied droit de la tente Est (107, 69) depuis RTO(107, 70)
    if (107, 70) in rto:
        stamp_rect_terrain(ter, rto[(107, 70)].copy(), 107, 69)

    # 7. Retablissement du Panneau Est a sa place d'origine (118..120, 50..53)
    #    et remplacement de la fleur coupee (120..122, 51..52) par une fleur 2x2 intacte animee (121..122, 51..52).
    for tx in range(117, 120):
        for ty in range(60, 64):
            can.pop((tx, ty), None)
    e_sign = grab_rect(rto, 24, 29, 3, 4)
    write_rect_canopy(can, e_sign, 118, 50)

    fill_grass_rect(ter, grass_tile, 120, 51, 122, 52)
    flower_phase_x = (1, 5, 9, 9)
    for p, fx in enumerate(flower_phase_x):
        fl_sp = grab_rect(anim, fx, 1, 2, 2)
        stamp_rect_terrain(ter, fl_sp, 121, 51, phases=range(p, p + 1))

    # 8. Nettoyage des 5 arbres coupes + rocher W + souches, et recomposition propre
    # Effacement propre dans TERRAIN
    # - Coin W : vieux arbre (0..6, 88..96) + residu feuille (6..10, 97..98) + vieux rocher (9..12, 87..90) + vieille souche (8..10, 92..94)
    fill_grass_rect(ter, grass_tile, 0, 87, 15, 96)
    fill_grass_rect(ter, grass_tile, 6, 97, 10, 98)
    # - Bas 1 : (14..23, 96..98)
    fill_grass_rect(ter, grass_tile, 14, 96, 23, 98)
    # - Bas 2 + souche (51..53, 95..97) : ATTENTION a preserver l'arbre entier (45..54, 85..95) !
    #   L'ancien arbre coupe occupait (42..51, 96..98), la souche coupee (51..53, 95..97).
    #   L'arbre (45..54, 85..95) s'arrete a y=95 cols 45..50 (col 51..53 y=95 est la souche, pas l'arbre).
    fill_grass_rect(ter, grass_tile, 42, 96, 53, 98)
    fill_grass_rect(ter, grass_tile, 51, 95, 53, 95)
    # - Bas 3 : (74..83, 96..98)
    fill_grass_rect(ter, grass_tile, 74, 96, 83, 98)
    # - Bas-Est : (111..122, 90..98)
    fill_grass_rect(ter, grass_tile, 111, 90, 122, 98)

    # Ancien Rocher 1 dans CANOPY (9..12, 87..90) -> efface, puis APO(6..9, 24..27) complet en (12..15, 87..90)
    for tx in range(9, 13):
        for ty in range(87, 91):
            can.pop((tx, ty), None)
    boulder_sp = grab_rect(apo, 6, 24, 4, 4)
    boulder_cells = write_rect_canopy(can, boulder_sp, 12, 87)

    # Sprites intacts pour TERRAIN :
    rto_tree = grab_rect(rto, 34, 87, 10, 9)
    rto_stump = grab_rect(rto, 38, 48, 3, 3)
    rto_bush = key_out_grass_border(grab_rect(rto, 17, 83, 3, 3), MEADOW_TUFT_COLORS)

    # Arbre W sauve entier (1..10, 88..96) + Souche W decalee (12..14, 93..95)
    stamp_rect_terrain(ter, rto_tree, 1, 88)
    stamp_rect_terrain(ter, rto_stump, 12, 93)
    # 3 buissons intacts 3x3 sur les emplacements des couronnes du bas
    stamp_rect_terrain(ter, rto_bush, 18, 95)
    stamp_rect_terrain(ter, rto_bush, 42, 95)
    stamp_rect_terrain(ter, rto_bush, 79, 95)
    # Souche restauree (51..53, 95..97)
    stamp_rect_terrain(ter, rto_stump, 51, 95)
    # Arbre Sud-Est sauve entier (111..120, 90..98)
    stamp_rect_terrain(ter, rto_tree, 111, 90)

    # 9. Verification 0 pixel semi-transparent (<255 & >0) sur TERRAIN (sauf bords de falaise ? On verifie !)
    semi_ter = []
    for (tx, ty), im in ter.items():
        if ty < MAP_H:
            a = np.array(im)[:, :, 3]
            n_semi = int(((a > 0) & (a < 255)).sum())
            if n_semi:
                semi_ter.append((tx, ty, n_semi))
    print(f"TERRAIN tuiles semi-transparentes restantes (y<99) : {len(semi_ter)} -> {semi_ter[:10]}")

    # 10. Regeneration des 3 variantes FILTRE de TERRAIN et CANOPY via LUTs exactes
    print("Application des LUTs AUBE / CREP / NUIT sur TERRAIN et CANOPY...")
    ter_variants = {
        "PICHU_CLIFF_DAY_TERRAIN": ter,
        "PICHU_CLIFF_DAY_TERRAIN_AUBE_FILTRE": {k: apply_lut_image(v, luts["aube"]) for k, v in ter.items()},
        "PICHU_CLIFF_DAY_TERRAIN_CREP_FILTRE": {k: apply_lut_image(v, luts["crep"]) for k, v in ter.items()},
        "PICHU_CLIFF_DAY_TERRAIN_NUIT_FILTRE": {k: apply_lut_image(v, luts["nuit"]) for k, v in ter.items()},
    }
    can_variants = {
        "PICHU_CLIFF_DAY_CANOPY": can,
        "PICHU_CLIFF_DAY_CANOPY_AUBE_FILTRE": {k: apply_lut_image(v, luts["aube"]) for k, v in can.items()},
        "PICHU_CLIFF_DAY_CANOPY_CREP_FILTRE": {k: apply_lut_image(v, luts["crep"]) for k, v in can.items()},
        "PICHU_CLIFF_DAY_CANOPY_NUIT_FILTRE": {k: apply_lut_image(v, luts["nuit"]) for k, v in can.items()},
    }
    for nm, sheet in ter_variants.items():
        save_tile_sheet(nm, 8, sheet)
    for nm, sheet in can_variants.items():
        save_tile_sheet(nm, 8, sheet)

    # 11. Harmonisation des obstacles et mise a jour des couches des 4 .rsground jouables + _source
    def apply_harmonized_obstacles(obs: list[list[dict]]) -> None:
        def set_box(x0: int, y0: int, x1: int, y1: int, tag: int) -> None:
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 1):
                    obs[x][y]["Tags"] = tag

        # Deblocage anciens emplacements / fantomes
        set_box(0, 87, 15, 98, 0)     # Tout le coin W recompose avant re-blocage exact
        set_box(14, 95, 23, 98, 0)    # Ancien arbre Bas 1
        set_box(42, 96, 53, 98, 0)    # Ancien arbre Bas 2 + bas souche
        set_box(74, 94, 83, 98, 0)    # Ancien arbre Bas 3 (laisse Rocher 3 y=90..93)
        set_box(111, 89, 122, 98, 0)  # Ancien arbre Bas-Est
        set_box(118, 53, 120, 53, 0)  # Bas de l'ancien Panneau Est (y=46..52 reste cloture)
        # Anomalies de blocs fantomes sur herbe/fleurs/passages
        for bx0, by0, bx1, by1 in [
            (54, 78, 56, 79),  # fleur milieu-bas
            (70, 94, 71, 95),  # fleur bas
            (96, 65, 98, 66),  # fleur pres panneau central
            (105, 88, 106, 89),  # trefle Est
            (113, 61, 115, 62),  # fleur Est
            (118, 64, 120, 65),  # fleur sous nouveau Panneau Est
            (50, 74, 51, 75),  # verification herbe libre
            (43, 78, 45, 78),  # rangee vide sous souche (43..45, 75..77)
            (44, 84, 45, 85),  # coins d'herbe libres pres arbre (45..54, 85..95)
            (109, 80, 110, 82),  # herbe libre a gauche de l'arbre (112..121, 79..88)
        ]:
            set_box(bx0, by0, bx1, by1, 0)

        # Re-blocage exact de tous les elements solides (anciens + deplaces + nouveaux)
        # Bord falaise arriere + cloture arriere + citrouille :
        set_box(67, 46, 83, 46, 1)  # bord de falaise derriere cloture
        set_box(67, 47, 72, 49, 1)  # cloture arriere gauche
        set_box(78, 47, 83, 49, 1)  # cloture arriere droite
        # Cloture virevents Est + Panneau Est retabli en (118..120, 50..53) :
        # on preserve la marchabilite d'origine autour du panneau (y=52..53 libres, (117..119, 60..63) liberes)
        set_box(103, 46, 122, 51, 1)
        set_box(103, 52, 122, 53, 0)
        set_box(117, 60, 119, 63, 0)
        # Tonneaux (63..66, 51..52) + (64..66, 53)
        set_box(63, 51, 66, 52, 1)
        set_box(64, 53, 66, 53, 1)
        # Boite aux lettres (82..83, 54..57)
        set_box(82, 54, 83, 57, 1)
        # Meules de foin
        set_box(37, 63, 41, 66, 1)
        set_box(33, 67, 36, 69, 1)
        # Tas de bois
        set_box(28, 86, 30, 88, 1)
        set_box(50, 61, 52, 63, 1)
        set_box(56, 82, 58, 84, 1)
        # Souches
        set_box(43, 75, 45, 77, 1)
        set_box(12, 93, 14, 95, 1)
        set_box(51, 95, 53, 97, 1)
        # Rochers
        set_box(12, 87, 15, 90, 1)
        set_box(45, 70, 45, 73, 0)
        set_box(46, 70, 49, 73, 1)
        set_box(74, 90, 77, 93, 1)
        # Arbres de bordure sauves + buissons intacts 3x3
        set_box(1, 88, 10, 96, 1)
        set_box(111, 90, 120, 98, 1)
        set_box(18, 95, 20, 97, 1)
        set_box(42, 95, 44, 97, 1)
        set_box(79, 95, 81, 97, 1)
        # Verification finale : couloirs scriptes Dazzling / Pichu / sortie Est garantis libres
        for cx0, cy0, cx1, cy1 in [(75, 58, 81, 59), (85, 81, 95, 98), (106, 55, 121, 59)]:
            set_box(cx0, cy0, cx1, cy1, 0)

    playable_cfgs = [
        ("cliffdaytest", "", 2, 3, 4),
        ("cliffdaytest_aube", "_AUBE_FILTRE", 2, 3, 4),
        ("cliffdaytest_crepuscule", "_CREP_FILTRE", 2, 3, 4),
        ("cliffdaytest_nuit", "_NUIT_FILTRE", 1, 2, 3),
    ]
    for gname, suffix, l_ter, l_can, l_top in playable_cfgs:
        gpath = GROUND_DIR / f"{gname}.rsground"
        gdata = load_json_bom(gpath)
        gobj = gdata["Object"]
        ter_sheet_name = f"PICHU_CLIFF_DAY_TERRAIN{suffix}"
        can_sheet_name = f"PICHU_CLIFF_DAY_CANOPY{suffix}"

        # Moulin : 6 cases cassees (3,79),(3,80),(3,82),(3,83),(4,79),(5,79) -> 4 phases TERRAIN propres
        for tx, ty in [(3, 79), (3, 80), (3, 82), (3, 83), (4, 79), (5, 79)]:
            gobj["Layers"][l_ter]["Tiles"][tx][ty] = make_anim_4_tile(ter_sheet_name, tx, ty, 10)
            # La nuit, retirer l'ancien pansement SEA_NUIT_FILTRE en L1 ? l_ter == 1 en nuit, donc remplace directement !

        # Supprimer les cellules CANOPY descendues sur TERRAIN + anciens woodpile/boulder/signpost vides
        for tx, ty in moved_canopy_cells:
            gobj["Layers"][l_can]["Tiles"][tx][ty] = {"Layers": []}
        for tx in range(MAP_W):
            for ty in range(MAP_H):
                # Nettoyer L_CAN partout ou la tuile CANOPY est desormais absente/vide
                if gobj["Layers"][l_can]["Tiles"][tx][ty].get("Layers"):
                    # Garder uniquement si (tx, ty) est un vrai CANOPY (hors E Signpost / StumpTable qui vont en l_top)
                    if (tx, ty) not in can:
                        gobj["Layers"][l_can]["Tiles"][tx][ty] = {"Layers": []}
        # Ajouter nouveau Rocher 1 en (12..15, 87..90) sur L_CAN (et effacer vieux 9..12, 87..90)
        for tx, ty in boulder_cells:
            gobj["Layers"][l_can]["Tiles"][tx][ty] = make_single_frame_tile(can_sheet_name, tx, ty, 1)

        # Panneau Est retabli sur L_TOP en (118..120, 50..53), et ancien deplacement (117..119, 60..63) efface
        for tx in range(117, 120):
            for ty in range(60, 64):
                gobj["Layers"][l_top]["Tiles"][tx][ty] = {"Layers": []}
        for tx in range(118, 121):
            for ty in range(50, 54):
                gobj["Layers"][l_top]["Tiles"][tx][ty] = make_single_frame_tile(can_sheet_name, tx, ty, 1)
                gobj["Layers"][l_can]["Tiles"][tx][ty] = {"Layers": []}

        # Verifier StumpTable (92..97, 70..79) entierement en L_TOP si non vide dans CANOPY
        for tx in range(92, 98):
            for ty in range(70, 80):
                if (tx, ty) in can:
                    gobj["Layers"][l_top]["Tiles"][tx][ty] = make_single_frame_tile(can_sheet_name, tx, ty, 1)
                    gobj["Layers"][l_can]["Tiles"][tx][ty] = {"Layers": []}

        apply_harmonized_obstacles(gobj["obstacles"])
        save_json_bom(gpath, gdata)
        print(f"Sauvegarde {gname}.rsground")

    # 12. Mise a jour de cliffdaytest_source.rsground (0 frames Sheet="", obstacles + props synchronises)
    # Sur cliffdaytest_source, les 6 cases moulin en L4 recoivent les 4 phases propres de PICHU_CLIFF_DAY_TERRAIN
    for tx, ty in [(3, 79), (3, 80), (3, 82), (3, 83), (4, 79), (5, 79)]:
        src_obj["Layers"][4]["Tiles"][tx][ty] = make_anim_4_tile("PICHU_CLIFF_DAY_TERRAIN", tx, ty, 10)
    # Nettoyer les cailloux et demi-poteaux BackFence en L3 source
    src_obj["Layers"][3]["Tiles"][67][49] = {"Layers": []}
    src_obj["Layers"][3]["Tiles"][77][49] = {"Layers": []}
    src_obj["Layers"][3]["Tiles"][67][47] = make_single_frame_tile("Reverie_Town_Objects", 69, 29, 1)
    src_obj["Layers"][3]["Tiles"][67][48] = make_single_frame_tile("Reverie_Town_Objects", 69, 30, 1)
    src_obj["Layers"][3]["Tiles"][73][47] = {"Layers": []}
    src_obj["Layers"][3]["Tiles"][73][48] = {"Layers": []}
    src_obj["Layers"][3]["Tiles"][73][49] = {"Layers": []}
    src_obj["Layers"][3]["Tiles"][77][47] = {"Layers": []}
    src_obj["Layers"][3]["Tiles"][77][48] = {"Layers": []}
    # Retablir le panneau Est en L5 source (118..120, 50..53) + nettoyer ancien (117..119, 60..63)
    # et poser la fleur 2x2 complete en (121..122, 51..52) sur L4 source
    for tx in range(117, 120):
        for ty in range(60, 64):
            src_obj["Layers"][4]["Tiles"][tx][ty] = {"Layers": []}
            src_obj["Layers"][5]["Tiles"][tx][ty] = {"Layers": []}
    for dx in range(3):
        for dy in range(4):
            src_obj["Layers"][5]["Tiles"][118 + dx][50 + dy] = make_single_frame_tile(
                "Reverie_Town_Objects", 24 + dx, 29 + dy, 1
            )
    for dx in range(2):
        for dy in range(2):
            src_obj["Layers"][4]["Tiles"][121 + dx][51 + dy] = make_single_frame_tile(
                "Reverie_Town_Animation_Tileset", 1 + dx, 1 + dy, 10
            )
    # Synchroniser les arbres/buissons/souches/rocher/trainees/touffes/table-souche corriges sur cliffdaytest_source
    # via les tuiles propres PICHU_CLIFF_DAY_{TERRAIN,CANOPY} (sans alterer les tilesets Reverie partages).
    smear_boxes_src = [
        (64, 72, 66, 75),
        (70, 74, 73, 76),
        (94, 75, 97, 76),
        (107, 62, 110, 65),
        (114, 63, 114, 63),
    ]
    road_tuft_set = set(ROAD_TUFT_CELLS)
    for tx in range(MAP_W):
        for ty in range(MAP_H):
            in_recomp = (
                (0 <= tx <= 15 and 87 <= ty <= 98)
                or (14 <= tx <= 23 and 95 <= ty <= 98)
                or (42 <= tx <= 53 and 95 <= ty <= 98)
                or (74 <= tx <= 83 and 95 <= ty <= 98)
                or (111 <= tx <= 122 and 90 <= ty <= 98)
                or (tx == 107 and ty == 69)
                or (tx, ty) in road_tuft_set
                or any(sx0 <= tx <= sx1 and sy0 <= ty <= sy1 for sx0, sy0, sx1, sy1 in smear_boxes_src)
            )
            if in_recomp:
                src_obj["Layers"][2]["Tiles"][tx][ty] = make_single_frame_tile("PICHU_CLIFF_DAY_TERRAIN", tx, ty, 1)
                # Retirer d'eventuels residus L3 (hors vrais objets L3) dans les coins plantes en bordure
                if not (12 <= tx <= 15 and 87 <= ty <= 90) and (tx, ty) in moved_canopy_cells:
                    src_obj["Layers"][3]["Tiles"][tx][ty] = {"Layers": []}
    for tx, ty in [(92, 75), (92, 76)]:
        src_obj["Layers"][4]["Tiles"][tx][ty] = make_single_frame_tile("PICHU_CLIFF_DAY_CANOPY", tx, ty, 1)
    # Nettoyer ancien Rocher 1 et poser le nouveau complet APO(6..9, 24..27) en (12..15, 87..90) sur L3 source
    for tx in range(9, 13):
        for ty in range(87, 91):
            src_obj["Layers"][3]["Tiles"][tx][ty] = {"Layers": []}
    for dx in range(4):
        for dy in range(4):
            if (6 + dx, 24 + dy) in apo:
                src_obj["Layers"][3]["Tiles"][12 + dx][87 + dy] = make_single_frame_tile(
                    "Altere_Pond_Objects", 6 + dx, 24 + dy, 1
                )
    apply_harmonized_obstacles(src_obj["obstacles"])
    save_json_bom(GROUND_DIR / "cliffdaytest_source.rsground", src_data)
    print("Sauvegarde cliffdaytest_source.rsground")

    # 13. Regeneration de CLIFFDAYTEST_BATTLE_BASE_24, CLIFFDAYTEST_BATTLE_FRONT_24 et cliffdaytest.rsmap
    print("Regeneration de CLIFFDAYTEST_BATTLE_{BASE,FRONT}_24 et cliffdaytest.rsmap...")
    day_obj = load_json_bom(GROUND_DIR / "cliffdaytest.rsground")["Object"]
    _, base24_orig = load_tile_sheet("CLIFFDAYTEST_BATTLE_BASE_24")

    new_base24: dict[tuple[int, int], Image.Image] = {}
    # Conserver les tuiles y < 12 existantes (et l'eventuel marqueur (41, 0) transparent/technique si present)
    for (tx, ty), im in base24_orig.items():
        if ty < 12 or tx >= MAP24_W:
            new_base24[(tx, ty)] = im

    for ph in range(8):
        frame_img = Image.new("RGBA", (MAP_W * 8, MAP_H * 8), (0, 0, 0, 0))
        for li in (1, 2, 3):
            tiles = day_obj["Layers"][li]["Tiles"]
            for x in range(MAP_W):
                for y in range(MAP_H):
                    for sub in tiles[x][y].get("Layers", []):
                        frames = sub["Frames"]
                        fr = frames[ph % len(frames)]
                        sh_nm = fr["Sheet"]
                        sh = sea if "SEA" in sh_nm else (ter if "TERRAIN" in sh_nm else can)
                        loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                        if loc in sh:
                            frame_img.alpha_composite(sh[loc], (x * 8, y * 8))
        for rx in range(MAP24_W):
            for ry in range(12, MAP24_H):
                crop = frame_img.crop((rx * 24, ry * 24, (rx + 1) * 24, (ry + 1) * 24))
                new_base24[(rx, ry + MAP24_H * ph)] = crop
    save_tile_sheet("CLIFFDAYTEST_BATTLE_BASE_24", 24, new_base24)

    # FRONT_24 (L4 Top : StumpTable + nouveau Panneau Est)
    front_img = Image.new("RGBA", (MAP_W * 8, MAP_H * 8), (0, 0, 0, 0))
    l4_tiles = day_obj["Layers"][4]["Tiles"]
    for x in range(MAP_W):
        for y in range(MAP_H):
            for sub in l4_tiles[x][y].get("Layers", []):
                fr = sub["Frames"][0]
                loc = (fr["TexLoc"]["X"], fr["TexLoc"]["Y"])
                if loc in can:
                    front_img.alpha_composite(can[loc], (x * 8, y * 8))

    new_front24: dict[tuple[int, int], Image.Image] = {}
    rsmap_path = MAP_DIR / "cliffdaytest.rsmap"
    rsmap_data = load_json_bom(rsmap_path)
    rsmap_obj = rsmap_data["Object"]

    # Mise a jour de L1 (Falaise — avant-plan 24 px) et de Tiles (floor / unbreakable)
    for rx in range(MAP24_W):
        for ry in range(MAP24_H):
            crop = front_img.crop((rx * 24, ry * 24, (rx + 1) * 24, (ry + 1) * 24))
            if (np.array(crop)[:, :, 3] > 0).any():
                new_front24[(rx, ry)] = crop
                rsmap_obj["Layers"][1]["Tiles"][rx][ry] = make_single_frame_tile(
                    "CLIFFDAYTEST_BATTLE_FRONT_24", rx, ry, 10
                )
            else:
                rsmap_obj["Layers"][1]["Tiles"][rx][ry] = {"Layers": []}

            if ry >= 15:
                blocked = sum(
                    1
                    for dx in range(3)
                    for dy in range(3)
                    if day_obj["obstacles"][rx * 3 + dx][ry * 3 + dy]["Tags"] == 1
                )
                rsmap_obj["Tiles"][rx][ry]["Data"]["ID"] = "unbreakable" if blocked >= 4 else "floor"
            else:
                rsmap_obj["Tiles"][rx][ry]["Data"]["ID"] = "unbreakable"

    # Garantir EntryPoints=(29,30) et spawn zone (28..30,29) bien en floor
    for sx, sy in [(29, 30), (28, 29), (29, 29), (30, 29)]:
        rsmap_obj["Tiles"][sx][sy]["Data"]["ID"] = "floor"

    # Elaguer toute poche 'floor' isolee hors composante principale depuis EntryPoints (29, 30)
    floors = {
        (rx, ry)
        for rx in range(MAP24_W)
        for ry in range(MAP24_H)
        if rsmap_obj["Tiles"][rx][ry]["Data"]["ID"] == "floor"
    }
    ep = rsmap_obj["EntryPoints"][0]["Loc"]
    start = (ep["X"], ep["Y"])
    q = deque([start])
    seen = {start}
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            np_ = (cx + dx, cy + dy)
            if np_ in floors and np_ not in seen:
                seen.add(np_)
                q.append(np_)
    for rx, ry in floors - seen:
        rsmap_obj["Tiles"][rx][ry]["Data"]["ID"] = "unbreakable"

    save_tile_sheet("CLIFFDAYTEST_BATTLE_FRONT_24", 24, new_front24)
    save_json_nobom(rsmap_path, rsmap_data)
    print(f"FRONT_24 tuiles={sorted(new_front24.keys())}, rsmap floor connectes={len(seen)} (isoles retires={len(floors - seen)})")
    print("Termine avec succes !")


if __name__ == "__main__":
    main()
