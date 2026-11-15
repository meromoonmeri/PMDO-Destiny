#!/usr/bin/env python3
"""
Génère TOUTE la banque PMU intérieure, architecturale et décorative dans les touches
de la Guilde Destiny (contraste noyer foncé / acajou / ardoise / tons joyaux + ombres
chaudes + 10 nouvelles éditions IA `generate_image` recalées au pixel 1x exact),
sans jamais modifier les 40 fichiers `PMU_00..10.tile` d'origine (intégrité SHA-256).

Sorties produites dans `game/` :
  - `Content/Tile/Destiny_PMU_Guilde_01_Architecture.tile`      (448 x 3712 px, 2D intact)
  - `Content/Tile/Destiny_PMU_Guilde_02_Mobilier_Interieur.tile` (912 x 2080 px, Avec Ombre + Sans Ombre)
  - `Content/Tile/Destiny_PMU_Guilde_03_Decoratifs_A.tile`       (912 x 2976 px, Avec Ombre + Sans Ombre)
  - `Content/Tile/Destiny_PMU_Guilde_04_Decoratifs_B.tile`       (912 x 2528 px, Avec Ombre + Sans Ombre)
  - `Content/Tile/Destiny_PMU_Guilde_05_Comptoirs_Et_Tresors.tile` (912 x 2432 px, Avec Ombre + Sans Ombre + 10 IA)
  - `Content/Object/Guilde_PMU_*.dir` (160+ objets indépendants prêts à poser en GroundObject)
"""
from __future__ import annotations

import io
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

REPO = Path("/var/tmp/PMDO-Destiny")
GAME = REPO / "game"
IMM_DIR = Path("/home/user/guilde_destiny_reseau/immobilier_guilde")
OUT_PMU_DIR = IMM_DIR / "banque_pmu_destiny"


def decode_page_rgba(pages_meta: dict[str, dict], name: str) -> np.ndarray:
    p = pages_meta[name]
    w, h = p["largeur_px"], p["hauteur_px"]
    raw = (GAME / f"Content/Tile/{name}.tile").read_bytes()
    ts, n = struct.unpack_from("<ii", raw, 0)
    assert ts == 8
    canvas = np.zeros((h, w, 4), dtype=np.uint8)
    for i in range(n):
        tx, ty, ptr = struct.unpack_from("<iiq", raw, 8 + i * 16)
        plen = struct.unpack_from("<q", raw, ptr)[0]
        im = Image.open(io.BytesIO(raw[ptr + 8 : ptr + 8 + plen])).convert("RGBA")
        arr = np.array(im, dtype=np.float32)
        nz = arr[..., 3] > 0
        arr[nz, :3] = np.clip(np.round(arr[nz, :3] * 255.0 / arr[nz, 3:4]), 0, 255)
        y0, x0 = ty * 8, tx * 8
        if y0 + 8 <= h and x0 + 8 <= w:
            canvas[y0 : y0 + 8, x0 : x0 + 8] = arr.astype(np.uint8)
    return canvas


def stitch_source(manifest: dict, pages_meta: dict[str, dict], src_name: str) -> np.ndarray:
    src_pages = [p for p in manifest["pages"] if p["source"] == src_name]
    w = src_pages[0]["largeur_px"]
    h = max(p["fin_y_px_exclue"] for p in src_pages)
    full = np.zeros((h, w, 4), dtype=np.uint8)
    for p in src_pages:
        arr = decode_page_rgba(pages_meta, p["nom"])
        y0, y1 = p["debut_y_px"], p["fin_y_px_exclue"]
        full[y0:y1, :w] = arr[: y1 - y0, :w]
    return full


def strip_cyan_label_boxes(arr: np.ndarray) -> np.ndarray:
    """Efface proprement les cartouches d'étiquettes PMU `[130, 200, 200]` ET leur texte interne."""
    out = arr.copy()
    is_label_bg = (
        (out[..., 3] > 200)
        & (np.abs(out[..., 0].astype(int) - 130) <= 6)
        & (np.abs(out[..., 1].astype(int) - 200) <= 6)
        & (np.abs(out[..., 2].astype(int) - 200) <= 6)
    )
    lbl, n = ndimage.label(is_label_bg)
    for sl in ndimage.find_objects(lbl):
        if sl is None:
            continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if w >= 40 and h >= 12:
            out[sl[0].start : sl[0].stop, sl[1].start : sl[1].stop] = 0
    return out


def clean_tiles8_editor_artifacts(arr: np.ndarray) -> np.ndarray:
    """Supprime 100 % des grilles d'éditeur PMU (vert menthe, violet, cyan) et blocs rouges de test."""
    out = arr.copy()
    r = out[..., 0].astype(int)
    g = out[..., 1].astype(int)
    b = out[..., 2].astype(int)
    a = out[..., 3].astype(int)

    # 1. Cartouche "Decoratives organized by Eture" en haut à gauche (relatif à y=10912 -> y=0..32, x=0..104)
    out[0:32, 0:104] = 0

    # 2. Grille violette [128, 0, 255] & grille vert menthe [48, 207, 155]
    purple_grid = (a > 0) & (np.abs(r - 128) <= 8) & (g <= 12) & (b >= 245)
    mint_grid = (a > 0) & (np.abs(r - 48) <= 8) & (np.abs(g - 207) <= 8) & (np.abs(b - 155) <= 8)
    out[purple_grid | mint_grid] = 0

    # 3. Blocs rectangulaires rouge pur / orange vif de remplissage PMU
    pure_red = (a > 200) & (r >= 245) & (g <= 15) & (b <= 15)
    lbl, _ = ndimage.label(pure_red)
    for sl in ndimage.find_objects(lbl):
        if sl is None:
            continue
        if (sl[0].stop - sl[0].start) >= 16 and (sl[1].stop - sl[1].start) >= 16:
            out[sl[0].start : sl[0].stop, sl[1].start : sl[1].stop] = 0

    # Bloc orange uni de test vers y_abs=11704..11736 (y_rel=792..824), x=144..184
    out[788:828, 144:184] = 0
    # Barres de calibration couleurs vers y_abs=14584..14648 (y_rel=3672..3736), x=192..416
    out[3672:3736, 192:416] = 0
    # 3 carrés roses unis de remplissage vers y_abs=15664..15736 (y_rel=4752..4824), x=160..288
    pink_fill = (a > 200) & (r >= 235) & (np.abs(g - 150) <= 35) & (np.abs(b - 175) <= 35)
    lbl_p, _ = ndimage.label(pink_fill)
    for sl in ndimage.find_objects(lbl_p):
        if sl is not None and (sl[0].stop - sl[0].start) >= 24 and (sl[1].stop - sl[1].start) >= 24:
            out[sl[0].start : sl[0].stop, sl[1].start : sl[1].stop] = 0

    return out


def clamp_zero_magenta(arr: np.ndarray) -> np.ndarray:
    """Garantit 0 pixel détecté comme magenta `((r - g) > 35) & ((b - g) > 25)` tout en gardant de riches améthystes/bordeaux."""
    out = arr.copy()
    nz = out[..., 3] > 0
    if not nz.any():
        return out
    r = out[..., 0].astype(np.int32)
    g = out[..., 1].astype(np.int32)
    b = out[..., 2].astype(np.int32)
    mag = nz & ((r - g) > 35) & ((b - g) > 25)
    if np.any(mag):
        # Réchauffe légèrement vers bordeaux/prune noble en abaissant B ou relevant légèrement G
        excess_b = (b[mag] - g[mag]) - 24
        excess_r = (r[mag] - g[mag]) - 34
        # Si c'est plutôt rubis/bordeaux (R >= B), on réduit B pour que (B - G) <= 24
        # Si c'est plutôt améthyste/prune (B > R), on relève légèrement G et adoucit R pour que (R - G) <= 34
        rm, gm, bm = r[mag], g[mag], b[mag]
        ruby = rm >= bm
        bm_new = np.where(ruby, gm + 23, bm)
        gm_new = np.where(ruby, gm, np.maximum(gm, np.minimum(rm - 33, bm - 23)))
        # Double sécurité mathématique stricte :
        still = ((rm - gm_new) > 35) & ((bm_new - gm_new) > 25)
        gm_new = np.where(still, np.maximum(gm_new, rm - 34), gm_new)
        out[mag, 0] = np.clip(rm, 0, 255).astype(np.uint8)
        out[mag, 1] = np.clip(gm_new, 0, 255).astype(np.uint8)
        out[mag, 2] = np.clip(bm_new, 0, 255).astype(np.uint8)
    return out


def apply_destiny_touches(arr: np.ndarray, arch_mode: bool = False) -> np.ndarray:
    """
    Adapte toute une planche PMU aux touches esthétiques de la Guilde Destiny :
      - Bois clairs/orangés -> Noyer foncé / Acajou chaud (contraste franc sur notre parquet chêne miel)
      - Or, laiton, paille dorée, flammes, parchemins -> Préservés & réchauffés avec éclat
      - Pierres grises froides -> Ardoise chaude / Basalte bronze
      - Verts fluo -> Vert Émeraude Forêt Destiny
      - Violets/Magentas -> Bordeaux royal / Améthyste profonde (0 magenta)
    """
    out = arr.copy()
    nz = out[..., 3] > 0
    if not nz.any():
        return out

    r = out[..., 0].astype(np.float32)
    g = out[..., 1].astype(np.float32)
    b = out[..., 2].astype(np.float32)

    # 1. Détection fine des bois orangés / pin clair (en excluant l'or/paille/parchemin jaune lumineux)
    is_gold_or_straw = ((r >= 200) & (g >= 166) & (g >= 0.78 * r)) | ((g >= 0.84 * r) & (r >= 155) & (b <= 115))
    is_cream_parchment = (r >= 205) & (g >= 190) & (b >= 145)
    is_warm_wood = (
        nz
        & (~is_gold_or_straw)
        & (~is_cream_parchment)
        & (r > g + 10)
        & (g > b + 5)
        & ((r - b) >= 24)
        & (r >= 58)
    )

    if arch_mode:
        # Pour l'architecture bois, contraste cèdre/noyer chaleureux un peu plus doux
        r = np.where(is_warm_wood, np.clip(r * 0.76 + 14.0, 0, 255), r)
        g = np.where(is_warm_wood, np.clip(g * 0.66 + 8.0, 0, 255), g)
        b = np.where(is_warm_wood, np.clip(b * 0.68 + 10.0, 0, 255), b)
    else:
        # Pour le mobilier posé sur notre parquet chêne miel (#D99543), noyer/acajou bien contrasté !
        r = np.where(is_warm_wood, np.clip(r * 0.68 + 14.0, 0, 255), r)
        g = np.where(is_warm_wood, np.clip(g * 0.56 + 7.0, 0, 255), g)
        b = np.where(is_warm_wood, np.clip(b * 0.60 + 9.0, 0, 255), b)

    # 2. Pierres grises froides -> Ardoise bronze chaleureuse
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    is_neutral_gray = nz & ((cmax - cmin) <= 13) & (cmax >= 52) & (cmax <= 205)
    r = np.where(is_neutral_gray, np.clip(r * 0.95 + 7.0, 0, 255), r)
    g = np.where(is_neutral_gray, np.clip(g * 0.93 + 4.0, 0, 255), g)
    b = np.where(is_neutral_gray, np.clip(b * 0.98 + 9.0, 0, 255), b)

    # 3. Verts néon/fluo -> Vert Émeraude Forêt Destiny
    is_neon_green = nz & (g > r + 30) & (g > b + 28) & (g >= 168)
    r = np.where(is_neon_green, np.clip(r * 0.72 + 10.0, 0, 255), r)
    g = np.where(is_neon_green, np.clip(g * 0.76 + 10.0, 0, 255), g)
    b = np.where(is_neon_green, np.clip(b * 0.88 + 18.0, 0, 255), b)

    out[..., 0] = np.round(r).astype(np.uint8)
    out[..., 1] = np.round(g).astype(np.uint8)
    out[..., 2] = np.round(b).astype(np.uint8)
    return clamp_zero_magenta(out)


def make_warm_guild_shadow(obj_rgba: np.ndarray) -> np.ndarray:
    """Crée l'ombre portée chaude de la Guilde Destiny `rgba(36, 16, 6, alpha)` sous les meubles."""
    h, w = obj_rgba.shape[:2]
    solid = obj_rgba[..., 3] >= 128
    sh_alpha = np.zeros((h, w), dtype=np.float32)
    for dx, dy, weight in [(1, 2, 0.42), (2, 2, 0.28), (0, 2, 0.25), (1, 3, 0.22)]:
        shifted = np.zeros_like(solid)
        y_src_end = h - dy if dy > 0 else h
        x_src_end = w - dx if dx > 0 else w
        shifted[dy:h, dx:w] = solid[0:y_src_end, 0:x_src_end]
        sh_alpha = np.maximum(sh_alpha, shifted.astype(np.float32) * weight)

    sh = np.zeros((h, w, 4), dtype=np.uint8)
    mask = (sh_alpha > 0) & (~solid)
    sh[mask, 0] = 36
    sh[mask, 1] = 16
    sh[mask, 2] = 6
    sh[mask, 3] = np.clip(np.round(sh_alpha[mask] * 255.0), 0, 120).astype(np.uint8)
    return sh


def composite_rgba(bottom: np.ndarray, top: np.ndarray) -> np.ndarray:
    b_im = Image.fromarray(bottom, "RGBA")
    t_im = Image.fromarray(top, "RGBA")
    b_im.alpha_composite(t_im)
    return np.array(b_im, dtype=np.uint8)


def extract_ai_on_exact_1x_mask(ai_path: Path, ref_1x_rgba: np.ndarray) -> np.ndarray:
    """Recale une image IA générée à partir d'une planche `6x` (marge 24px) sur la silhouette `1x` exacte."""
    h1, w1 = ref_1x_rgba.shape[:2]
    ai_im = Image.open(ai_path).convert("RGB")
    aw, ah = ai_im.size
    # La planche 6x avait `W6 = w1*6 + 48`, `H6 = h1*6 + 48`
    exp_w, exp_h = w1 * 6 + 48, h1 * 6 + 48
    sx = aw / exp_w
    sy = ah / exp_h
    x0 = int(round(24 * sx))
    y0 = int(round(24 * sy))
    x1 = int(round((24 + w1 * 6) * sx))
    y1 = int(round((24 + h1 * 6) * sy))
    cropped = ai_im.crop((x0, y0, x1, y1)).resize((w1, h1), Image.Resampling.BOX)
    rgb = np.array(cropped, dtype=np.uint8)
    out = np.zeros((h1, w1, 4), dtype=np.uint8)
    out[..., :3] = rgb
    out[..., 3] = ref_1x_rgba[..., 3]
    out[out[..., 3] == 0] = 0
    return clamp_zero_magenta(out)


def encode_premultiplied_png(rgba: np.ndarray) -> bytes:
    pm = rgba.copy().astype(np.float32)
    a = pm[..., 3:4] / 255.0
    pm[..., :3] = np.round(pm[..., :3] * a)
    buf = io.BytesIO()
    Image.fromarray(pm.astype(np.uint8), "RGBA").save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def write_visual_2d_tile_sheet(rgba: np.ndarray, out_tile_path: Path) -> int:
    """Écrit une feuille `.tile` PMDO en conservant les coordonnées visuelles 2D `(tx, ty)` intactes."""
    H, W = rgba.shape[:2]
    assert W % 8 == 0 and H % 8 == 0, f"Dimensions non multiples de 8 : {W}x{H}"
    gw, gh = W // 8, H // 8
    entries: list[tuple[int, int, bytes]] = []
    cache_bytes: dict[bytes, bytes] = {}

    for ty in range(gh):
        y0 = ty * 8
        row = rgba[y0 : y0 + 8]
        if not np.any(row[..., 3] > 0):
            continue
        for tx in range(gw):
            patch = row[:, tx * 8 : (tx + 1) * 8]
            if not np.any(patch[..., 3] > 0):
                continue
            raw_key = patch.tobytes()
            png_b = cache_bytes.get(raw_key)
            if png_b is None:
                png_b = encode_premultiplied_png(patch)
                cache_bytes[raw_key] = png_b
            entries.append((tx, ty, png_b))

    n = len(entries)
    header_size = 8 + n * 16
    # Déduplique les blobs PNG identiques par pointeur `ptr` TOUT EN GARDANT chaque `(tx, ty)` 2D intact !
    blob_offsets: dict[bytes, int] = {}
    blobs = bytearray()
    index_buf = bytearray(struct.pack("<ii", 8, n))

    for tx, ty, png_b in entries:
        ptr = blob_offsets.get(png_b)
        if ptr is None:
            ptr = header_size + len(blobs)
            blob_offsets[png_b] = ptr
            blobs.extend(struct.pack("<q", len(png_b)))
            blobs.extend(png_b)
        index_buf.extend(struct.pack("<iiq", tx, ty, ptr))

    out_tile_path.write_bytes(bytes(index_buf) + bytes(blobs))
    return n


def write_dir_object(rgba: np.ndarray, out_dir_path: Path) -> None:
    """Écrit un objet `.dir` PMDO mono-frame valide (PNG prémultiplié + trailer 16 octets)."""
    h, w = rgba.shape[:2]
    # Aligne sur multiple de 2 pour centrage propre
    pw = w + (w % 2)
    ph = h + (h % 2)
    canvas = np.zeros((ph, pw, 4), dtype=np.uint8)
    canvas[:h, :w] = rgba
    png_b = encode_premultiplied_png(canvas)
    trailer = struct.pack("<iiii", pw, ph, 0, 1)
    out_dir_path.write_bytes(struct.pack("<q", len(png_b)) + png_b + trailer)


def make_side_by_side_sheet(clean_obj: np.ndarray) -> np.ndarray:
    """Construit une planche 912px : Gauche (x=0..447) = Meuble + Ombre ; Droite (x=464..911) = Meuble seul."""
    h, w = clean_obj.shape[:2]
    assert w == 448
    pad_h = ((h + 7) // 8) * 8
    padded = np.zeros((pad_h, 448, 4), dtype=np.uint8)
    padded[:h, :w] = clean_obj
    sh = make_warm_guild_shadow(padded)
    with_sh = composite_rgba(sh, padded)
    full = np.zeros((pad_h, 912, 4), dtype=np.uint8)
    full[:, 0:448] = with_sh
    full[:, 464:912] = padded
    return full


def render_parquet_bg(w: int, h: int) -> Image.Image:
    """Génère un fond parquet chêne miel fidèle à notre Guilde Destiny pour vérifier le contraste."""
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[..., 0] = 214
    arr[..., 1] = 148
    arr[..., 2] = 70
    arr[..., 3] = 255
    # Lignes de planches horizontales tous les 16 px + joints verticaux décalés
    for y in range(0, h, 16):
        arr[y : min(y + 1, h), :, :3] = (168, 108, 44)
        if y + 1 < h:
            arr[y + 1 : min(y + 2, h), :, :3] = (228, 166, 86)
        offset = 32 if ((y // 16) % 2) else 0
        for x in range(offset, w, 64):
            arr[y : min(y + 16, h), x : min(x + 1, w), :3] = (176, 114, 48)
    return Image.fromarray(arr, "RGBA")


def main() -> None:
    OUT_PMU_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((REPO / "tools/pmu_banques_manifest.json").read_text(encoding="utf-8"))
    pages_meta = {p["nom"]: p for p in manifest["pages"]}

    print("1/6 Décodage des sources PMU (Tiles0, Tiles2, Tiles3, Tiles5, Tiles8, Tiles9)...")
    t0 = stitch_source(manifest, pages_meta, "Tiles0")
    t2 = stitch_source(manifest, pages_meta, "Tiles2")
    t3 = stitch_source(manifest, pages_meta, "Tiles3")
    t5 = stitch_source(manifest, pages_meta, "Tiles5")
    t8 = stitch_source(manifest, pages_meta, "Tiles8")
    t9 = stitch_source(manifest, pages_meta, "Tiles9")

    # --- BANQUE 01 : Architecture Bois, Escaliers, Barrières & Fenêtres (`Tiles5 y=9600..13312`) ---
    print("2/6 Transformation Destiny : Banque 01 Architecture Intérieure PMU...")
    s01_raw = strip_cyan_label_boxes(t5[9600:13312])
    s01_destiny = apply_destiny_touches(s01_raw, arch_mode=True)

    # --- BANQUE 02 : Mobilier Intérieur Complet (`Tiles5 y=14208..16288`) ---
    print("3/6 Transformation Destiny : Banque 02 Mobilier Intérieur Complet PMU...")
    s02_raw = strip_cyan_label_boxes(t5[14208:16288])
    s02_obj = apply_destiny_touches(s02_raw, arch_mode=False)
    s02_sheet = make_side_by_side_sheet(s02_obj)

    # --- BANQUE 03 & 04 : Toute la Banque Décorative Guilde/Base PMU (`Tiles8 y=10912..16416`) ---
    print("4/6 Transformation Destiny : Banques 03 & 04 Décoratifs Guilde/Base PMU (A & B)...")
    t8_clean = clean_tiles8_editor_artifacts(t8[10912:16416])
    t8_destiny = apply_destiny_touches(t8_clean, arch_mode=False)
    split_y = 13888 - 10912  # 2976 (multiple exact de 8)
    s03_obj = t8_destiny[:split_y]
    s04_obj = t8_destiny[split_y:]
    s03_sheet = make_side_by_side_sheet(s03_obj)
    s04_sheet = make_side_by_side_sheet(s04_obj)

    # --- BANQUE 05 : Comptoirs de Services Guilde (`Tiles2`), Intérieurs `Tiles0`, Cristaux/Or `Tiles3` & 10 Éditions IA ---
    print("5/6 Assemblage & Transformation Destiny : Banque 05 Comptoirs, Trésors & 10 Éditions IA...")
    s05_col = np.zeros((1888, 448, 4), dtype=np.uint8)
    # A) Tiles2 y=0..1152 nettoyé de ses deux rectangles noirs opaques vides `(0,0,0,255)`
    t2_sub = t2[0:1152, 0:224].copy()
    t2_sub[0:320, 192:224] = 0
    t2_sub[704:1152, 0:128] = 0
    s05_col[0:1152, 0:224] = apply_destiny_touches(t2_sub, arch_mode=False)
    s05_col[0:416, 224:448] = apply_destiny_touches(t3[0:416, 0:224], arch_mode=False)
    # B) Blocs intérieurs choisis de Tiles0 (bannières médiévales, tonneaux, plantes, tableaux, tapis, cheminées, charrette, rideaux)
    s05_col[424:568, 224:448] = apply_destiny_touches(t0[504:648, 64:288], arch_mode=False)
    s05_col[576:800, 224:448] = apply_destiny_touches(t0[2240:2464, 160:384], arch_mode=False)
    # Tapis/tableaux/cheminée de Tiles0 sans le feu de falaise extérieur
    t0_indoor = t0[3456:3800, 0:224].copy()
    t0_indoor[248:344, 0:112] = 0
    s05_col[808:1152, 224:448] = apply_destiny_touches(t0_indoor, arch_mode=False)
    # C) Lits/armoires (sans paroi de grotte) + rideaux/cadres de Tiles0 + nattes/peluches/totems de Tiles9
    t0_beds = t0[3944:4008, 0:288].copy()
    t0_beds[:, 0:32] = 0
    s05_col[1160:1224, 0:288] = apply_destiny_touches(t0_beds, arch_mode=False)
    s05_col[1160:1320, 288:448] = apply_destiny_touches(t0[5184:5344, 64:224], arch_mode=False)
    s05_col[1248:1472, 0:160] = apply_destiny_touches(t9[5700:5924, 64:224], arch_mode=False)
    s05_col[1328:1536, 232:360] = apply_destiny_touches(t9[592:800, 0:128], arch_mode=False)

    # D) Intégration des 10 nouvelles éditions IA `generate_image` (recalées sur silhouette `1x` exacte !)
    ref_dir = IMM_DIR / "refs_ia"
    ia_dir = IMM_DIR / "ia_bruts"
    ai_specs = [
        ("ia_cheminee_portrait", "pmu_cheminee_portrait_1x.png", "ia_pmu_cheminee_portrait_destiny.png", False),
        ("ia_grande_bibliotheque", "pmu_grande_bibliotheque_1x.png", "ia_pmu_grande_bibliotheque_destiny.png", False),
        ("ia_lit_baldaquin", "pmu_lit_baldaquin_1x.png", "ia_pmu_lit_baldaquin_destiny.png", False),
        ("ia_trone_royal", "pmu_trone_royal_1x.png", "ia_pmu_trone_royal_destiny.png", False),
        ("ia_orgue_guilde", "pmu_orgue_guilde_1x.png", "ia_pmu_orgue_guilde_destiny.png", False),
        ("ia_grande_armoire", "pmu_grande_armoire_1x.png", "ia_pmu_grande_armoire_destiny.png", False),
        ("ia_comptoir_reserve", "pmu_comptoir_kangourex_1x.png", "ia_pmu_comptoir_kangourex_destiny.png", False),
        ("ia_comptoir_oracle", "pmu_comptoir_kecleon_1x.png", "ia_pmu_comptoir_kecleon_destiny.png", False),
        ("ia_comptoir_techniques", "pmu_comptoir_stand_1_1x.png", "ia_pmu_comptoir_stand_destiny.png", True),
        ("ia_comptoir_banque", "pmu_comptoir_banque_1x.png", "ia_pmu_comptoir_banque_destiny.png", False),
    ]

    ai_extracted: list[tuple[str, np.ndarray]] = []
    cx, cy, row_h = 8, 1512, 0
    for ai_name, r1x_fn, ai_fn, trim_stand in ai_specs:
        ref_arr = np.array(Image.open(ref_dir / r1x_fn).convert("RGBA"), dtype=np.uint8)
        sp = extract_ai_on_exact_1x_mask(ia_dir / ai_fn, ref_arr)
        if trim_stand:
            # Retire le petit résidu 8px de tapis rayé sous `y=76` sur `pmu_comptoir_stand_1`
            sp[76:, :36] = 0
            ys, xs = np.where(sp[..., 3] > 0)
            sp = sp[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
        ai_extracted.append((ai_name, sp))
        sh_h, sh_w = sp.shape[:2]
        pw, ph = ((sh_w + 7) // 8) * 8, ((sh_h + 7) // 8) * 8
        if cx + pw + 8 > 448:
            cx = 8
            cy += row_h + 16
            row_h = 0
        s05_col[cy : cy + sh_h, cx : cx + sh_w] = sp
        cx += pw + 16
        row_h = max(row_h, ph)

    s05_col = clamp_zero_magenta(s05_col)
    s05_sheet = make_side_by_side_sheet(s05_col)

    # --- Écriture des 5 banques `.tile` 2D intactes + PNG sources ---
    print("6/6 Compilation des 5 feuilles `.tile` PMU-Destiny + extraction des objets `.dir`...")
    tile_banks = [
        ("Destiny_PMU_Guilde_01_Architecture", s01_destiny),
        ("Destiny_PMU_Guilde_02_Mobilier_Interieur", s02_sheet),
        ("Destiny_PMU_Guilde_03_Decoratifs_A", s03_sheet),
        ("Destiny_PMU_Guilde_04_Decoratifs_B", s04_sheet),
        ("Destiny_PMU_Guilde_05_Comptoirs_Et_Tresors", s05_sheet),
    ]
    bank_summary = {}
    for bname, barr in tile_banks:
        Image.fromarray(barr, "RGBA").save(OUT_PMU_DIR / f"{bname}.png")
        ntiles = write_visual_2d_tile_sheet(barr, GAME / f"Content/Tile/{bname}.tile")
        bank_summary[bname] = {"width": int(barr.shape[1]), "height": int(barr.shape[0]), "non_empty_8x8_tiles": ntiles}
        print(f"  [OK] {bname}.tile : {barr.shape[1]}x{barr.shape[0]} px ({ntiles} cases 8x8)")

    # --- Extraction automatique d'objets `.dir` autonomes (`Guilde_PMU_*.dir`) ---
    # 1) Les 10 nouvelles pièces maîtresses IA (avec leur ombre chaude intégrée)
    dir_manifest = {}
    for idx, (ai_name, sp) in enumerate(ai_extracted, start=1):
        pad = np.zeros((sp.shape[0] + 4, sp.shape[1] + 4, 4), dtype=np.uint8)
        pad[: sp.shape[0], : sp.shape[1]] = sp
        comp = composite_rgba(make_warm_guild_shadow(pad), pad)
        dname = f"Guilde_PMU_IA_{idx:02d}_{ai_name}"
        write_dir_object(comp, GAME / f"Content/Object/{dname}.dir")
        dir_manifest[dname] = {"w": int(comp.shape[1]), "h": int(comp.shape[0]), "source": "IA_Destiny"}

    # 2) Les grands meubles/comptoirs/bannières/totems multi-tuiles (>= 28x28 px) de Mobilier Intérieur, Comptoirs & Décoratifs
    auto_sources = [
        ("Mob", s02_obj, 28, 28),
        ("Cpt", s05_col[:1504], 32, 32),
        ("DecA", s03_obj, 36, 36),
        ("DecB", s04_obj, 36, 36),
    ]
    seen_hashes: set[bytes] = set()
    auto_idx = 1
    for prefix, src_arr, min_w, min_h in auto_sources:
        lbl, _ = ndimage.label(src_arr[..., 3] > 20)
        for sl in ndimage.find_objects(lbl):
            if sl is None:
                continue
            y0, y1 = sl[0].start, sl[0].stop
            x0, x1 = sl[1].start, sl[1].stop
            w, h = x1 - x0, y1 - y0
            if w < min_w or h < min_h or w > 220 or h > 200:
                continue
            crop = src_arr[y0:y1, x0:x1].copy()
            # Isole uniquement la composante connexe majoritaire si besoin
            h_key = crop.tobytes()
            if h_key in seen_hashes:
                continue
            seen_hashes.add(h_key)
            pad = np.zeros((h + 4, w + 4, 4), dtype=np.uint8)
            pad[:h, :w] = crop
            comp = composite_rgba(make_warm_guild_shadow(pad), pad)
            dname = f"Guilde_PMU_{prefix}_{auto_idx:03d}"
            write_dir_object(comp, GAME / f"Content/Object/{dname}.dir")
            dir_manifest[dname] = {"w": int(comp.shape[1]), "h": int(comp.shape[0]), "source": prefix}
            auto_idx += 1

    (OUT_PMU_DIR / "Destiny_PMU_Guilde_Manifest.json").write_text(
        json.dumps({"tile_banks": bank_summary, "dir_objects_count": len(dir_manifest), "dir_objects": dir_manifest}, indent=2),
        encoding="utf-8",
    )
    print(f"  [OK] {len(dir_manifest)} objets `Guilde_PMU_*.dir` générés dans Content/Object/ !")

    # --- Planches d'aperçu visuel sur notre parquet Chêne Miel ---
    # Planche 1 : Mobilier Intérieur (02) + Comptoirs, Trésors & 10 IA (05) sur parquet !
    p1_w = 468 + 468 + 24
    p1_h = max(s02_sheet.shape[0], s05_sheet.shape[0]) + 72
    board1 = Image.new("RGBA", (p1_w, p1_h), (34, 22, 14, 255))
    d1 = ImageDraw.Draw(board1)
    d1.text((16, 12), "BANQUE PMU -> TOUCHES DESTINY (PLANCHE 1/2) : MOBILIER INTERIEUR COMPLET + COMPTOIRS, TRESORS & 10 IA", fill=(255, 230, 170, 255))
    d1.text((16, 34), "Rendu réel avec ombres chaudes sur notre parquet Chêne Miel (Contraste Noyer / Acajou / Ardoise / Tons Joyaux)", fill=(214, 188, 148, 255))

    bg_02 = render_parquet_bg(448, s02_sheet.shape[0])
    bg_02.alpha_composite(Image.fromarray(s02_sheet[:, :448], "RGBA"))
    d1.text((16, 54), "Destiny_PMU_Guilde_02_Mobilier_Interieur.tile (colonne avec ombres)", fill=(255, 218, 145, 255))
    board1.alpha_composite(bg_02, (16, 70))

    bg_05 = render_parquet_bg(448, s05_sheet.shape[0])
    bg_05.alpha_composite(Image.fromarray(s05_sheet[:, :448], "RGBA"))
    d1.text((484, 54), "Destiny_PMU_Guilde_05_Comptoirs_Et_Tresors.tile (+ 10 nouvelles éditions IA en bas)", fill=(255, 218, 145, 255))
    board1.alpha_composite(bg_05, (484, 70))
    board1.convert("RGB").save(OUT_PMU_DIR / "Apercu_PMU_Destiny_Planche_1_Mobilier_Comptoirs_IA.jpg", quality=93)

    # Planche 2 : Décoratifs A (03) + Décoratifs B (04) + Architecture Bois/Fenêtres (01) sur parquet/fond !
    p2_w = 468 * 3 + 24
    p2_h = max(s03_sheet.shape[0], s04_sheet.shape[0], 3000) + 72
    board2 = Image.new("RGBA", (p2_w, p2_h), (34, 22, 14, 255))
    d2 = ImageDraw.Draw(board2)
    d2.text((16, 12), "BANQUE PMU -> TOUCHES DESTINY (PLANCHE 2/2) : TOUS LES DECORATIFS GUILDE/BASE (A & B) + ARCHITECTURE & FENETRES", fill=(255, 230, 170, 255))
    d2.text((16, 34), "100% nettoyé des grilles d'éditeur vertes/violettes et blocs rouges PMU — Prêt au placement en 1 clic dans RogueEssence", fill=(214, 188, 148, 255))

    bg_03 = render_parquet_bg(448, s03_sheet.shape[0])
    bg_03.alpha_composite(Image.fromarray(s03_sheet[:, :448], "RGBA"))
    d2.text((16, 54), "Destiny_PMU_Guilde_03_Decoratifs_A.tile", fill=(255, 218, 145, 255))
    board2.alpha_composite(bg_03, (16, 70))

    bg_04 = render_parquet_bg(448, s04_sheet.shape[0])
    bg_04.alpha_composite(Image.fromarray(s04_sheet[:, :448], "RGBA"))
    d2.text((484, 54), "Destiny_PMU_Guilde_04_Decoratifs_B.tile (drapeaux sans grille !)", fill=(255, 218, 145, 255))
    board2.alpha_composite(bg_04, (484, 70))

    bg_01 = Image.new("RGBA", (448, min(s01_destiny.shape[0], p2_h - 76)), (54, 38, 26, 255))
    # Affiche la section Murs/Sols/Barrières/Escaliers/Fenêtres (y=600..3600 de s01_destiny)
    crop_01 = s01_destiny[712 : 712 + bg_01.height]
    bg_01.alpha_composite(Image.fromarray(crop_01, "RGBA"))
    d2.text((952, 54), "Destiny_PMU_Guilde_01_Architecture.tile (murs, sols, escaliers, fenêtres)", fill=(255, 218, 145, 255))
    board2.alpha_composite(bg_01, (952, 70))
    board2.convert("RGB").save(OUT_PMU_DIR / "Apercu_PMU_Destiny_Planche_2_Decoratifs_Architecture.jpg", quality=92)

    print("TERMINÉ AVEC SUCCÈS !")


if __name__ == "__main__":
    main()
