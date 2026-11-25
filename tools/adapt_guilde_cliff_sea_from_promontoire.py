#!/usr/bin/env python3
"""
Adapte la mer pixel-art animée 12 phases de `falaise_promontoire_{jour,aube,crepuscule,nuit}`
au layout symétrique de la péninsule `guilde_cliff_{jour,aube,crepuscule,nuit}` (480x520 px = 60x65 tuiles) :
- Conserve 100 % intacts le rocher/pelouse (`Layer[1] 01_Guilde_Cliff`), les ciels/nuages (`Background`),
  le bâtiment HD de la Guilde (`Decorations`), les obstacles et `PorteGuilde`.
- Remplace uniquement `Layer[0] 00_Mer_Animee_12Phases` et `Destiny_GuildeCliff_<Cap>_Mer_059.tile` par la mer
  exacte de `falaise_promontoire_<amb>` (dégradé vertical Sharpedo, scintillements d'horizon stationnaires,
  vaguelettes au large et écume blanche animée épousant les DEUX flancs gauche et droit de la falaise).
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TILE_DIR = ROOT / "game/Content/Tile"
GROUND_DIR = ROOT / "game/Data/Ground"

AMBIANCES = [
    ("jour", "Jour"),
    ("aube", "Aube"),
    ("crepuscule", "Crepuscule"),
    ("nuit", "Nuit"),
]


def decode_tile_sheet(path: Path) -> dict[tuple[int, int], np.ndarray]:
    raw = path.read_bytes()
    _, cnt = struct.unpack_from("<ii", raw, 0)
    out: dict[tuple[int, int], np.ndarray] = {}
    cache: dict[int, np.ndarray] = {}
    for i in range(cnt):
        tx, ty, off = struct.unpack_from("<iiq", raw, 8 + i * 16)
        if off not in cache:
            (plen,) = struct.unpack_from("<q", raw, off)
            im = Image.open(io.BytesIO(raw[off + 8 : off + 8 + plen])).convert("RGBA")
            arr = np.array(im, dtype=np.float32)
            nz = arr[..., 3] > 0
            arr[nz, :3] = np.clip(np.round(arr[nz, :3] * 255.0 / arr[nz, 3:4]), 0, 255)
            cache[off] = arr.astype(np.uint8)
        out[(tx, ty)] = cache[off]
    return out


def premultiply_patch_bytes(patch_rgba: np.ndarray) -> bytes:
    arr = patch_rgba.astype(np.float32)
    alpha = arr[..., 3:4] / 255.0
    arr[..., :3] = np.clip(np.round(arr[..., :3] * alpha), 0, 255)
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def reconstruct_promontoire_sea_12f(amb: str, cap: str) -> tuple[np.ndarray, np.ndarray]:
    """Retourne `(sea_12f [12, 512, 640, 4], cliff_alpha [512, 640])` de `falaise_promontoire_<amb>`."""
    doc = json.loads((GROUND_DIR / f"falaise_promontoire_{amb}.rsground").read_text(encoding="utf-8-sig"))["Object"]
    bank = decode_tile_sheet(TILE_DIR / f"Destiny_Promontoire_{cap}.tile")

    sea = np.zeros((12, 512, 640, 4), dtype=np.uint8)
    cliff_a = np.zeros((512, 640), dtype=np.uint8)
    l0 = doc["Layers"][0]["Tiles"]
    l1 = doc["Layers"][1]["Tiles"]

    for tx in range(80):
        for ty in range(64):
            tl0 = l0[tx][ty].get("Layers", [])
            if tl0 and tl0[0].get("Frames"):
                frs = tl0[0]["Frames"]
                for fi in range(12):
                    loc = frs[fi % len(frs)]["TexLoc"]
                    sea[fi, ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = bank[(loc["X"], loc["Y"])]
            tl1 = l1[tx][ty].get("Layers", [])
            if tl1 and tl1[0].get("Frames"):
                loc1 = tl1[0]["Frames"][0]["TexLoc"]
                cliff_a[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = bank[(loc1["X"], loc1["Y"])][:, :, 3]

    # Sur `nuit`, `falaise_promontoire_nuit` possède un reflet de pleine lune centré en x ~ 554 (x in 506..602)
    # sous la lune droite de `FALAISE_PROMONTOIRE_NUIT_CIEL`. Or dans `guilde_cliff_nuit`, la lune est au centre
    # derrière le grand arbre de la Guilde (pas au-dessus des flancs marins gauche/droite).
    # On remplace donc proprement le cône lunaire x in [504..606] sur `sea` nuit par les colonnes d'océan nocturne
    # pur adjacentes x in [608..639] (en conservant l'écume de falaise intacte près du rocher x < 504) !
    if amb == "nuit":
        for y in range(152, 512):
            # Où finit le rocher à cette ligne ?
            c_xs = np.where(cliff_a[y] > 128)[0]
            c_max = int(c_xs.max()) if len(c_xs) else -1
            # Garder intacte la frange d'écume contre la falaise (jusqu'à c_max + 18 si hors cône vif)
            clean_start = max(504, c_max + 16)
            for x in range(clean_start, 608):
                src_x = 608 + ((x - clean_start) % 32)
                sea[:, y, x, :] = sea[:, y, src_x, :]
            # Pour la bande d'horizon haute (y=152..196) où c_max < 450, nettoyer dès x=504 avec x=460..500 ou 608..639
            if y < 200:
                for x in range(502, 608):
                    src_x = 608 + ((x - 502) % 32)
                    sea[:, y, x, :] = sea[:, y, src_x, :]

    return sea, cliff_a


def adapt_sea_to_guilde_cliff(amb: str, cap: str) -> None:
    sea_prom, prom_cliff_a = reconstruct_promontoire_sea_12f(amb, cap)

    g_path = GROUND_DIR / f"guilde_cliff_{amb}.rsground"
    g_full = json.loads(g_path.read_text(encoding="utf-8-sig"))
    g_doc = g_full["Object"]
    g_cliff_bank = decode_tile_sheet(TILE_DIR / f"Destiny_GuildeCliff_{cap}_059.tile")

    W, H = 480, 520
    GW, GH = 60, 65

    g_cliff_a = np.zeros((H, W), dtype=np.uint8)
    l1 = g_doc["Layers"][1]["Tiles"]
    for tx in range(GW):
        for ty in range(GH):
            tl1 = l1[tx][ty].get("Layers", [])
            if tl1 and tl1[0].get("Frames"):
                loc1 = tl1[0]["Frames"][0]["TexLoc"]
                g_cliff_a[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8] = g_cliff_bank[(loc1["X"], loc1["Y"])][:, :, 3]

    # Construire les 12 frames 480x520 de la mer adaptée au layout de `guilde_cliff` !
    out_sea = np.zeros((12, H, W, 4), dtype=np.uint8)

    for y in range(152, H):
        # Ligne source dans `falaise_promontoire` (512 px de haut -> pour y=512..519, prolonger proprement y_src=504..511)
        y_src = y if y < 512 else (504 + ((y - 512) % 8))

        # Bord droit du rocher sur `falaise_promontoire` à `y_src`
        p_xs = np.where(prom_cliff_a[y_src] > 128)[0]
        has_prom_cliff = len(p_xs) > 0 and y_src >= 164
        p_right = int(p_xs.max()) if has_prom_cliff else 480

        # Bords gauche et droit du rocher sur `guilde_cliff` à `y`
        g_xs = np.where(g_cliff_a[y] > 128)[0]
        has_g_cliff = len(g_xs) > 0

        if not has_g_cliff or y < 166:
            # Bande d'horizon haute continue (y=152..165) : échantillonner directement la bande d'horizon large
            # de `falaise_promontoire` (x_src = 480..639 bouclée sans couture ou x=0..479 là où la mer est ouverte) !
            for x in range(W):
                # Sur promontoire, y=152..159 a la mer ouverte sur x=340..639 (300 px de large !)
                # Pour y=160..165, x=450..639 (190 px de large !)
                span_start = 352 if y_src < 160 else 456
                span_w = 640 - span_start
                xs_open = span_start + (x % span_w)
                out_sea[:, y, x, :] = sea_prom[:, y_src, xs_open, :]
        else:
            g_left = int(g_xs.min())
            g_right = int(g_xs.max())
            g_mid = (g_left + g_right) // 2

            # 1) Moitié DROITE (x >= g_mid) : à partir de `g_right`, distance `dx = x - g_right` vers le large droit !
            #    Pour `dx < 0` (quelques pixels sous le bord anti-aliasé du rocher), on prolonge `p_right` proprement.
            for x in range(g_mid, W):
                dx = max(0, x - g_right)
                x_src = min(639, p_right + dx)
                # Si la mer de promontoire à `x_src` était encore transparente de 1-2px sous son propre rocher, avancer d'1-3px :
                while x_src < 639 and sea_prom[0, y_src, x_src, 3] < 250:
                    x_src += 1
                out_sea[:, y, x, :] = sea_prom[:, y_src, x_src, :]

            # 2) Moitié GAUCHE (x < g_mid) : miroir horizontal exact autour de `g_left` (`dx = g_left - x` vers le large gauche !),
            #    avec léger décalage de phase (+6 frames mod 12) sur les vagues animées (hors dither statique d'horizon)
            #    pour un rendu naturel et vivant des deux côtés de la falaise !
            for x in range(0, g_mid):
                dx = max(0, g_left - x)
                x_src = min(639, p_right + dx)
                while x_src < 639 and sea_prom[0, y_src, x_src, 3] < 250:
                    x_src += 1
                for fi in range(12):
                    src_fi = (fi + 6) % 12 if y >= 168 else fi
                    out_sea[fi, y, x, :] = sea_prom[src_fi, y_src, x_src, :]

    # Compiler uniquement les tuiles (tx, ty) de `ty >= 19` qui ne sont pas 100 % recouvertes par `g_cliff_a == 255` !
    ATLAS_COLS = 32
    patch_to_loc: dict[bytes, tuple[int, int]] = {}
    ordered_patches: list[tuple[int, int, np.ndarray]] = []

    zero_patch = np.zeros((8, 8, 4), dtype=np.uint8)
    patch_to_loc[zero_patch.tobytes()] = (0, 0)
    ordered_patches.append((0, 0, zero_patch))

    def get_loc(patch: np.ndarray) -> tuple[int, int]:
        key = patch.tobytes()
        loc = patch_to_loc.get(key)
        if loc is not None:
            return loc
        idx = len(ordered_patches)
        loc = (idx % ATLAS_COLS, idx // ATLAS_COLS)
        patch_to_loc[key] = loc
        ordered_patches.append((loc[0], loc[1], patch.copy()))
        return loc

    mer_sheet = f"Destiny_GuildeCliff_{cap}_Mer_059"
    empty_cell = {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}
    new_l0_cols = []
    active_sea_tiles = 0

    for tx in range(GW):
        col = []
        x0, x1 = tx * 8, (tx + 1) * 8
        for ty in range(GH):
            y0, y1 = ty * 8, (ty + 1) * 8
            if ty < 19 or bool((g_cliff_a[y0:y1, x0:x1] == 255).all()):
                col.append(dict(empty_cell))
                continue
            frames_json = []
            for fi in range(12):
                lx, ly = get_loc(out_sea[fi, y0:y1, x0:x1])
                frames_json.append({"Sheet": mer_sheet, "TexLoc": {"X": lx, "Y": ly}})
            col.append({
                "AutoTileset": "",
                "Associates": [],
                "Layers": [{"Frames": frames_json, "FrameLength": 8}],
                "NeighborCode": -1,
            })
            active_sea_tiles += 1
        new_l0_cols.append(col)

    if amb in ("aube", "crepuscule"):
        g_doc["Background"]["Layers"] = [
            bl for bl in g_doc["Background"]["Layers"]
            if not any(tag in bl["BG"]["BGAnim"]["AnimIndex"] for tag in ("NUAGES_MILIEU", "NUAGES_HAUT"))
        ]
    g_doc["Layers"][0]["Tiles"] = new_l0_cols
    g_path.write_text(json.dumps(g_full, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

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

    (TILE_DIR / f"{mer_sheet}.tile").write_bytes(bytes(out_tile))
    print(f"[OK] {amb}: adapted Promontoire 12-phase sea -> guilde_cliff_{amb} ({active_sea_tiles} active sea tiles, {n_tiles} unique 8x8 patches)")


def main() -> None:
    for amb, cap in AMBIANCES:
        adapt_sea_to_guilde_cliff(amb, cap)


if __name__ == "__main__":
    main()
