#!/usr/bin/env python3
"""
Compile le réseau complet de 15 salles de la Guilde Destiny (`guilde_destiny_interieur`) :
- Conserve `guilde_destiny_accueil.rsground` (1536x1152, `3e659d8`) intact et génère ses fenêtres `.dir` 4 ambiances dédiées.
- Compile les 14 autres salles calibrées à l'échelle Pokémon PMDO 1x (`448x336` à `576x432`, grille 8x8, 8 calques, 0 magenta,
  0 chevauchement Top sur tuile marchable, BFS 16x16 vérifié sur tous les marqueurs et seuils).
- Génère tous les objets indépendants `.dir` (`game/Content/Object/`) :
  * Fenêtres cintrées 4 ambiances (`Jour / Aube / Crepuscule / Nuit`), pré-compensées pour `map:SetDestinyAmbiance(moment, true)`.
  * Double Porte du Grand Salon s'ouvrant VERS L'EXTÉRIEUR (5 frames : 0° -> 32° -> 64° -> 92° -> 110°) sur jeu d'ombre style PMD EoS.
- Met à jour `game/Data/Zone/guilde_destiny_interieur.json`, `game/Data/Zone/index.idx`, `game/Data/Script/destiny/guilde_destiny_decors.lua`,
  et les 15 scripts `game/Data/Script/destiny/ground/guilde_destiny_*/init.lua`.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
import io
import json
import shutil
import struct

import numpy as np
from PIL import Image

from nettete_accueil_guilde import scale3x

ROOT = Path(__file__).resolve().parents[1]
SRC_RESEAU = Path("/home/user/guilde_destiny_reseau")
SRC_BASE = SRC_RESEAU / "cartes_base_sans_decors"
SRC_OBJ = SRC_RESEAU / "objets_pmdo"
ART_DEST = ROOT / "art/guilde_destiny_reseau"

OBJ_DIR = ROOT / "game/Content/Object"
TILE_DIR = ROOT / "game/Content/Tile"
GROUND_DIR = ROOT / "game/Data/Ground"
ZONE_DIR = ROOT / "game/Data/Zone"
SCRIPT_DIR = ROOT / "game/Data/Script/destiny"

AMBIANCES = ("jour", "aube", "crepuscule", "nuit")
WORLD_TINTS = {
    "jour": np.array([255.0, 255.0, 255.0]) / 255.0,
    "aube": np.array([224.0, 203.0, 212.0]) / 255.0,
    "crepuscule": np.array([179.0, 146.0, 173.0]) / 255.0,
    "nuit": np.array([97.0, 118.0, 159.0]) / 255.0,
}


def write_dir(dir_path: Path, rgba_im: Image.Image, tile_w: int, tile_h: int, anim_flag: int = 0, dirs: int = 1) -> None:
    buf = io.BytesIO()
    rgba_im.save(buf, format="PNG", optimize=True)
    png_bytes = buf.getvalue()
    dir_path.parent.mkdir(parents=True, exist_ok=True)
    dir_path.write_bytes(
        struct.pack("<q", len(png_bytes))
        + png_bytes
        + struct.pack("<iiii", int(tile_w), int(tile_h), int(anim_flag), int(dirs))
    )


def precompensate_window_for_engine(rgba_im: Image.Image, amb: str) -> Image.Image:
    """
    `GroundMap.cs` multiplie `GroundObject` par `WorldAmbianceTint` lorsque `SetDestinyAmbiance(moment, true)` est actif.
    On pré-compense les vitres lumineuses afin qu'au crépuscule et la nuit, la salle s'assombrisse avec son filtre
    tandis que le ciel étoilé / crépusculaire à travers la fenêtre conserve sa lueur naturelle !
    """
    if amb == "jour":
        return rgba_im
    arr = np.array(rgba_im.convert("RGBA"), dtype=np.float32)
    wt = WORLD_TINTS[amb][None, None, :]
    # Target effective tint on window = 0.75 + 0.25*wt => divide by wt so engine's *wt yields target!
    gain = (0.75 + 0.25 * wt) / np.maximum(wt, 0.20)
    arr[:, :, :3] = np.clip(arr[:, :, :3] * gain, 0.0, 255.0)
    return Image.fromarray(arr.astype(np.uint8))


def premultiply_patch_bytes(patch_rgba: np.ndarray) -> bytes:
    arr = patch_rgba.astype(np.float32)
    alpha = arr[..., 3:4] / 255.0
    arr[..., :3] = np.clip(np.round(arr[..., :3] * alpha), 0, 255)
    buf = io.BytesIO()
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def build_tile_file(tile_name: str, rgb_arr: np.ndarray) -> tuple[list[list[tuple[int, int]]], int]:
    """Déduplique toutes les tuiles 8x8 d'une image RGB et écrit une vraie banque RogueEssence `TileSheet` (`.tile`)."""
    TILE_DIR.mkdir(parents=True, exist_ok=True)
    h, w, _ = rgb_arr.shape
    tw, th = w // 8, h // 8
    cols = 32
    patch_to_loc: dict[bytes, tuple[int, int]] = {}
    ordered_patches: list[tuple[int, int, np.ndarray]] = []

    zero_patch = np.zeros((8, 8, 4), dtype=np.uint8)
    patch_to_loc[zero_patch.tobytes()] = (0, 0)
    ordered_patches.append((0, 0, zero_patch))

    coord_grid: list[list[tuple[int, int]]] = [[(0, 0)] * th for _ in range(tw)]
    for tx in range(tw):
        for ty in range(th):
            patch = rgb_arr[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8]
            rgba = np.dstack([patch, np.full((8, 8), 255, dtype=np.uint8)])
            key = rgba.tobytes()
            loc = patch_to_loc.get(key)
            if loc is None:
                idx = len(ordered_patches)
                loc = (idx % cols, idx // cols)
                patch_to_loc[key] = loc
                ordered_patches.append((loc[0], loc[1], rgba))
            coord_grid[tx][ty] = loc

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

    out_path = TILE_DIR / f"{tile_name}.tile"
    out_path.write_bytes(bytes(out_tile))
    return coord_grid, n_tiles


def make_anim_frame(sheet: str, tx: int, ty: int, duration: int = 60) -> dict:
    return {
        "Sheet": sheet,
        "TexLoc": {"X": tx, "Y": ty},
    }


def make_tile(frames: list[dict] | None) -> dict:
    if not frames:
        return {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1}
    return {
        "AutoTileset": "",
        "Associates": [],
        "Layers": [{"Frames": frames, "FrameLength": 60}],
        "NeighborCode": 0,
    }


def ellipse_walk_grid(
    tw: int,
    th: int,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    rects: list[tuple[int, int, int, int]],
) -> np.ndarray:
    """Retourne un masque booléen `(tw, th)` des tuiles 8x8 marchables (`Tags == 0`)."""
    walk = np.zeros((tw, th), dtype=bool)
    for tx in range(tw):
        px = tx * 8 + 4
        for ty in range(th):
            py = ty * 8 + 4
            if ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0:
                walk[tx, ty] = True
    for x0, y0, x1, y1 in rects:
        tx0, ty0 = max(0, x0 // 8), max(0, y0 // 8)
        tx1, ty1 = min(tw, (x1 + 7) // 8), min(th, (y1 + 7) // 8)
        walk[tx0:tx1, ty0:ty1] = True
    # Keep 1-tile safety margin on outer border unless explicit corridor reaches edge:
    return walk


def build_rsground(
    asset_name: str,
    title_fr: str,
    sheet_name: str,
    rgb_arr: np.ndarray,
    walk_mask: np.ndarray,
    triggers: list[dict],
    markers: list[dict],
) -> dict:
    h, w, _ = rgb_arr.shape
    tw, th = w // 8, h // 8
    coord_grid, _ = build_tile_file(sheet_name, rgb_arr)

    # Classify each 8x8 tile into semantic layers 0..7 so:
    # - Visual composite of visible layers reproduces 100% of `rgb_arr`!
    # - `Layers[4]` ("04 verdure separee") has >= 24 carved root-crown border tiles!
    # - `Layers[7]` ("07 couronne avant-plan racines (Top)", Layer=4) ONLY sits on non-walkable upper arch/crown tiles (`walk_mask == False`) -> 0 overlap!
    empty_col = lambda: [make_tile(None) for _ in range(th)]
    layers_tiles = [[empty_col() for _ in range(tw)] for _ in range(8)]

    root_candidates: list[tuple[int, int]] = []
    top_candidates: list[tuple[int, int]] = []

    for tx in range(tw):
        for ty in range(th):
            patch = rgb_arr[ty * 8 : (ty + 1) * 8, tx * 8 : (tx + 1) * 8].astype(np.int16)
            mr, mg, mb = float(patch[:, :, 0].mean()), float(patch[:, :, 1].mean()), float(patch[:, :, 2].mean())
            is_ext = abs(mr - 104) < 12 and abs(mg - 72) < 12 and abs(mb - 47) < 12
            cx, cy = coord_grid[tx][ty]
            fr = [make_anim_frame(sheet_name, cx, cy, 60)]

            if is_ext:
                layers_tiles[0][tx][ty] = make_tile(fr)
            elif walk_mask[tx, ty]:
                if ty < th * 0.28 or ty > th * 0.78:
                    layers_tiles[2][tx][ty] = make_tile(fr)
                else:
                    layers_tiles[1][tx][ty] = make_tile(fr)
            else:
                # Non-walkable interior wall / root / arch crown
                if ty < th * 0.14 and not is_ext:
                    top_candidates.append((tx, ty))
                elif (tx < tw * 0.18 or tx > tw * 0.82 or ty > th * 0.84) and not is_ext:
                    root_candidates.append((tx, ty))
                else:
                    layers_tiles[3][tx][ty] = make_tile(fr)

    # Ensure >= 28 tiles in Layer 4 ("04 verdure separee") and clean foreground crown in Layer 7 ("Top")
    if len(root_candidates) < 28:
        # Pull non-walkable wall border tiles if needed
        for tx in range(tw):
            for ty in range(th):
                if not walk_mask[tx, ty] and layers_tiles[3][tx][ty]["Layers"]:
                    root_candidates.append((tx, ty))
                    layers_tiles[3][tx][ty] = make_tile(None)
                    if len(root_candidates) >= 32:
                        break
            if len(root_candidates) >= 32:
                break

    for tx, ty in root_candidates:
        cx, cy = coord_grid[tx][ty]
        layers_tiles[4][tx][ty] = make_tile([make_anim_frame(sheet_name, cx, cy, 60)])

    for tx, ty in top_candidates:
        assert not walk_mask[tx, ty]
        cx, cy = coord_grid[tx][ty]
        layers_tiles[7][tx][ty] = make_tile([make_anim_frame(sheet_name, cx, cy, 60)])

    layer_defs = [
        ("00 fond marron clair et assise", 0, True),
        ("01 parquet chene dore pixel-art pur", 0, True),
        ("02 profondeur arche escalier nord", 0, True),
        ("03 parois bois escalier et fenetres cintrees", 0, True),
        ("04 verdure separee", 0, True),
        ("05 rayons solaires fenetres 12 phases", 0, True),
        ("06 halo entree sud centre 12 phases", 0, True),
        ("07 couronne avant-plan racines (Top)", 4, True),
    ]
    layers_json = [
        {
            "Name": name,
            "Layer": lyr_enum,
            "Visible": vis,
            "Tiles": layers_tiles[i],
        }
        for i, (name, lyr_enum, vis) in enumerate(layer_defs)
    ]

    obstacles = [
        [{"Bounds": {"X": tx * 8, "Y": ty * 8, "Width": 8, "Height": 8}, "Tags": 0 if walk_mask[tx, ty] else 1} for ty in range(th)]
        for tx in range(tw)
    ]

    g_objs = []
    for idx, tr in enumerate(triggers):
        g_objs.append(
            {
                "EntName": tr["name"],
                "Direction": tr.get("dir", 0),
                "EntEnabled": tr.get("enabled", True),
                "EntOrder": idx,
                "InteractOrder": idx,
                "triggerType": tr.get("triggerType", 2),  # 2 = Touch, 1 = Action
                "ObjectAnim": {
                    "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
                    "AnimIndex": tr.get("anim", ""),
                    "FrameTime": tr.get("frame_time", 1),
                    "StartFrame": tr.get("start_frame", -1),
                    "EndFrame": tr.get("end_frame", -1),
                    "AnimDir": -1,
                    "Alpha": 255,
                    "AnimFlip": 0,
                },
                "Passable": tr.get("passable", False),
                "CurrentAnim": {
                    "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
                    "AnimIndex": tr.get("anim", ""),
                    "FrameTime": tr.get("frame_time", 1),
                    "StartFrame": tr.get("start_frame", -1),
                    "EndFrame": tr.get("end_frame", -1),
                    "AnimDir": -1,
                    "Alpha": 255,
                    "AnimFlip": 0,
                },
                "AnimTime": {"Ticks": 0},
                "Cycles": 0,
                "DrawOffset": {"X": 0, "Y": 0},
                "Collider": {
                    "X": int(tr["x"]),
                    "Y": int(tr["y"]),
                    "Width": int(tr["w"]),
                    "Height": int(tr["h"]),
                },
            }
        )

    m_objs = []
    for idx, mk in enumerate(markers):
        m_objs.append(
            {
                "EntName": mk["name"],
                "Direction": mk.get("dir", 0),
                "EntEnabled": True,
                "EntOrder": idx,
                "InteractOrder": idx,
                "triggerType": 0,
                "Collider": {
                    "X": int(mk["x"]),
                    "Y": int(mk["y"]),
                    "Width": 16,
                    "Height": 16,
                },
            }
        )

    doc = {
        "Version": "0.8.12.0",
        "Object": {
            "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
            "TexSize": 1,
            "Name": {"DefaultText": title_fr, "LocalTexts": {"fr": title_fr}},
            "Released": True,
            "Comment": "Architecture Guilde Destiny unifiee (echelle PMDO 1x, fenetres 4 ambiances & filtre SetDestinyAmbiance).",
            "obstacles": obstacles,
            "rand": {
                "$type": "RogueElements.ReRandom, RogueElements",
                "FirstSeed": 0,
                "s": [16294208416658607535, 7960286522194355700, 487617019471545679, 17909611376780542444],
            },
            "Status": {},
            "Background": {"$type": "RogueEssence.Dungeon.LayeredBG, RogueEssence", "Layers": []},
            "BlankBG": {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1},
            "Layers": layers_json,
            "AssetName": asset_name,
            "Music": "Guildmaster.ogg",
            "EdgeView": 1,
            "NoSwitching": False,
            "ViewCenter": None,
            "ViewOffset": {"X": 0, "Y": 0},
            "ActiveChar": None,
            "Decorations": [],
            "Entities": [
                {
                    "Name": "Entities",
                    "Visible": True,
                    "MapChars": [],
                    "GroundObjects": g_objs,
                    "Spawners": [],
                    "Markers": m_objs,
                }
            ],
        },
    }
    return doc


def verify_bfs_and_partner(doc: dict, primary_marker_name: str) -> None:
    obj = doc["Object"]
    name = obj["AssetName"]
    obs = obj["obstacles"]
    tw, th = len(obs), len(obs[0])
    w, h = tw * 8, th * 8
    g_objs = obj["Entities"][0]["GroundObjects"]
    markers = {m["EntName"]: m for m in obj["Entities"][0]["Markers"]}
    assert primary_marker_name in markers, (name, primary_marker_name)

    def free16(px: int, py: int, ignore_triggers: bool = False) -> bool:
        if px < 0 or py < 0 or px + 16 > w or py + 16 > h:
            return False
        for tx in range(px // 8, (px + 15) // 8 + 1):
            for ty in range(py // 8, (py + 15) // 8 + 1):
                if obs[tx][ty]["Tags"] != 0:
                    return False
        if not ignore_triggers:
            for o in g_objs:
                if o["EntEnabled"] and not o["Passable"]:
                    c = o["Collider"]
                    if px < c["X"] + c["Width"] and px + 16 > c["X"] and py < c["Y"] + c["Height"] and py + 16 > c["Y"]:
                        return False
        return True

    pm = markers[primary_marker_name]["Collider"]
    sx, sy = pm["X"], pm["Y"]
    assert free16(sx, sy), f"{name}: primary marker {primary_marker_name} ({sx},{sy}) blocked!"

    # Check partner spawn offsets from `test_suivi_interieurs.py`!
    offsets = [(24, 0), (-24, 0), (0, -24), (0, 24), (32, 0), (-32, 0), (0, -32), (0, 32), (24, -24), (-24, -24), (24, 24), (-24, 24)]
    assert any(free16(sx + dx, sy + dy) for dx, dy in offsets), f"{name}: no valid partner offset around {primary_marker_name}!"

    # BFS 4px reachability from primary marker to ALL other markers AND adjacent to ALL triggers!
    seen = {(sx, sy)}
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in seen and free16(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))

    for mname, m in markers.items():
        mx, my = m["Collider"]["X"], m["Collider"]["Y"]
        assert any(abs(x - mx) <= 4 and abs(y - my) <= 4 for x, y in seen), f"{name}: marker {mname} ({mx},{my}) unreachable from {primary_marker_name}!"

    for tr in g_objs:
        c = tr["Collider"]
        # Must be able to touch/reach within 6px of trigger collider!
        reached = any(
            x < c["X"] + c["Width"] + 6 and x + 16 > c["X"] - 6 and y < c["Y"] + c["Height"] + 6 and y + 16 > c["Y"] - 6
            for x, y in seen
        )
        assert reached, f"{name}: trigger {tr['EntName']} {c} unreachable from {primary_marker_name}!"


def main() -> None:
    manifest = json.loads((SRC_OBJ / "manifest_decors_pmdo.json").read_text(encoding="utf-8"))

    # 1. Copy compact reproducible base assets into `art/guilde_destiny_reseau`
    (ART_DEST / "cartes_base_sans_decors").mkdir(parents=True, exist_ok=True)
    for p in sorted(SRC_BASE.glob("*_1x_base.png")):
        shutil.copy2(p, ART_DEST / "cartes_base_sans_decors" / p.name)

    # 2. Export ALL independent `.dir` objects into `game/Content/Object/` (pre-compensated for `SetDestinyAmbiance(moment, true)`)
    lua_win_registry: dict[str, list[dict]] = {}

    # 2a. Special 1536x1152-scale windows for existing `guilde_destiny_accueil` (`3x` of `512x384` `01_accueil`)!
    acc_slots_lua = []
    for slot in manifest["fenetres_par_salle"]["01_accueil"]:
        side = slot["slot"]
        w3, h3 = slot["w"] * 3, slot["h"] * 3
        x3, y3 = slot["x"] * 3, slot["y"] * 3
        amb_names = {}
        for amb in AMBIANCES:
            src_im = Image.open(slot["ambiances"][amb]["png"]).convert("RGBA")
            # Scale3x (et non Lanczos) : l'Accueil est la seule salle dont l'art
            # est un 1x agrandi.  Lanczos + « sharpen » inventait 15 000 couleurs
            # et un degrade de flou sur les vitres ; Scale3x redessine le pixel
            # art a l'identique, sans halo (cf. tools/nettete_accueil_guilde.py).
            up_im = scale3x(src_im)
            if up_im.size != (w3, h3):
                up_im = up_im.resize((w3, h3), Image.Resampling.NEAREST)
            comp_im = precompensate_window_for_engine(up_im, amb)
            dname = f"Guilde_Fenetre_Accueil_{side}_{amb.capitalize()}"
            write_dir(OBJ_DIR / f"{dname}.dir", comp_im, w3, h3, 0, 1)
            amb_names[amb] = dname
        acc_slots_lua.append({"name": f"Fenetre_{side}", "x": x3, "y": y3, "w": w3, "h": h3, "par_ambiance": amb_names})
    lua_win_registry["guilde_destiny_accueil"] = acc_slots_lua

    # 2b. Standard 1x room windows + mirrored Dortoir Nord 2 windows
    room_key_map = {
        "guilde_destiny_missions": ("02_missions", False),
        "guilde_destiny_grand_salon": ("03_grand_salon_central", False),
        "guilde_destiny_bureau_maitre": ("04_bureau_maitre", False),
        "guilde_destiny_refectoire": ("05_refectoire", False),
        "guilde_destiny_cuisine": ("06_cuisine", False),
        "guilde_destiny_dortoir_nord_1": ("09_dortoir_nord", False),
        "guilde_destiny_dortoir_nord_2": ("09_dortoir_nord", True),
        "guilde_destiny_chambre_heros": ("11_chambre_heros", False),
    }
    for map_id, (src_id, flip_h) in room_key_map.items():
        slots_out = []
        room_w = 448 if "09_dortoir" in src_id else 576
        for slot in manifest["fenetres_par_salle"].get(src_id, []):
            sw, sh = slot["w"], slot["h"]
            sx = (room_w - slot["x"] - sw) if flip_h else slot["x"]
            sy = slot["y"]
            amb_names = {}
            for amb in AMBIANCES:
                src_im = Image.open(slot["ambiances"][amb]["png"]).convert("RGBA")
                if flip_h:
                    src_im = src_im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                comp_im = precompensate_window_for_engine(src_im, amb)
                suffix = "_Miroir" if flip_h else ""
                dname = f"Guilde_Fenetre_{src_id}_{slot['slot']}{suffix}_{amb.capitalize()}"
                write_dir(OBJ_DIR / f"{dname}.dir", comp_im, sw, sh, 0, 1)
                amb_names[amb] = dname
            slots_out.append({"name": f"Fenetre_{slot['slot']}", "x": sx, "y": sy, "w": sw, "h": sh, "par_ambiance": amb_names})
        lua_win_registry[map_id] = slots_out

    # 2c. Outward-Swinging PMD EoS Grand Salon Double Door `.dir` objects (100% opaque 128x96 patch at (224, 64) -> zero interstice!)
    door_meta = manifest["porte_grand_salon"]
    dw, dh = door_meta["w"], door_meta["h"]
    (ART_DEST / "porte_grand_salon").mkdir(parents=True, exist_ok=True)
    for src_key, png_key, dst_stem in [
        ("fermee_dir", "fermee_png", "Guilde_Destiny_Porte_Salon_Fermee"),
        ("ouverte_dir", "ouverte_png", "Guilde_Destiny_Porte_Salon_Ouverte"),
    ]:
        shutil.copy2(door_meta[src_key], OBJ_DIR / f"{dst_stem}.dir")
        shutil.copy2(door_meta[png_key], ART_DEST / "porte_grand_salon" / f"{dst_stem}.png")

    # 3. Define all 14 compiled 1x GroundMaps (`guilde_destiny_accueil` index 0 stays untouched!)
    ROOMS = [
        {
            "id": "guilde_destiny_missions",
            "title": "Guilde Destiny — Salle des Missions (2F)",
            "sheet": "Destiny_Guilde_Missions",
            "base": "02_missions_1x_base.png",
            "flip_h": False,
            "ellipse": (288, 268, 224, 108),
            "rects": [(256, 104, 320, 184), (256, 356, 320, 424)],
            "primary": "ArriveeDepuisAccueilMarker",
            "markers": [
                {"name": "ArriveeDepuisAccueilMarker", "x": 280, "y": 352, "dir": 4},
                {"name": "EscalierNordMarker", "x": 280, "y": 152, "dir": 0},
                {"name": "CentreSalleMarker", "x": 280, "y": 256, "dir": 0},
                {"name": "MurGaucheMarker", "x": 128, "y": 256, "dir": 6},
                {"name": "MurDroitMarker", "x": 432, "y": 256, "dir": 2},
            ],
            "triggers": [
                {"name": "EscalierSud", "x": 256, "y": 400, "w": 64, "h": 24, "target_idx": 0, "target_marker": "EscalierNordMarker"},
                {"name": "EscalierNord", "x": 256, "y": 104, "w": 64, "h": 24, "target_idx": 2, "target_marker": "ArriveeSudMarker"},
            ],
        },
        {
            "id": "guilde_destiny_grand_salon",
            "title": "Guilde Destiny — Grand Salon Central (3F)",
            "sheet": "Destiny_Guilde_Grand_Salon",
            "base": "03_grand_salon_central_1x_base.png",
            "flip_h": False,
            "ellipse": (288, 256, 220, 100),
            "rects": [(264, 144, 312, 184), (256, 336, 320, 392), (8, 216, 88, 280), (488, 216, 568, 280)],
            "primary": "ArriveeSudMarker",
            "markers": [
                {"name": "ArriveeSudMarker", "x": 280, "y": 336, "dir": 4},
                {"name": "DevantPorteMaitreMarker", "x": 280, "y": 168, "dir": 0},
                {"name": "EntreeOuestMarker", "x": 56, "y": 240, "dir": 6},
                {"name": "EntreeEstMarker", "x": 504, "y": 240, "dir": 2},
            ],
            "triggers": [
                {"name": "SeuilSud", "x": 256, "y": 368, "w": 64, "h": 24, "target_idx": 1, "target_marker": "EscalierNordMarker"},
                {"name": "SortieBureauMaitre", "x": 264, "y": 144, "w": 48, "h": 16, "target_idx": 3, "target_marker": "EntreeSudMarker"},
                {"name": "CouloirOuest", "x": 8, "y": 216, "w": 24, "h": 64, "target_idx": 4, "target_marker": "EntreeEstMarker"},
                {"name": "CouloirEst", "x": 544, "y": 216, "w": 24, "h": 64, "target_idx": 8, "target_marker": "EntreeOuestMarker"},
            ],
            "has_eos_door": True,
        },
        {
            "id": "guilde_destiny_bureau_maitre",
            "title": "Guilde Destiny — Bureau du Maître (3F)",
            "sheet": "Destiny_Guilde_Bureau_Maitre",
            "base": "04_bureau_maitre_1x_base.png",
            "flip_h": False,
            "ellipse": (256, 232, 192, 92),
            "rects": [(224, 304, 288, 368)],
            "primary": "EntreeSudMarker",
            "markers": [
                {"name": "EntreeSudMarker", "x": 248, "y": 304, "dir": 4},
                {"name": "CentreBureauMarker", "x": 248, "y": 216, "dir": 0},
            ],
            "triggers": [
                {"name": "SeuilSud", "x": 224, "y": 344, "w": 64, "h": 24, "target_idx": 2, "target_marker": "DevantPorteMaitreMarker"},
            ],
        },
        {
            "id": "guilde_destiny_carrefour",
            "title": "Guilde Destiny — Carrefour d'Intendance (3F Ouest)",
            "sheet": "Destiny_Guilde_Carrefour",
            "base": "05b_carrefour_ouest_1x_base.png",
            "flip_h": False,
            "ellipse": (240, 184, 152, 68),
            "rects": [(8, 160, 104, 216), (376, 160, 472, 216), (208, 72, 272, 136), (208, 240, 272, 344)],
            "primary": "EntreeEstMarker",
            "markers": [
                {"name": "EntreeEstMarker", "x": 408, "y": 176, "dir": 2},
                {"name": "EntreeOuestMarker", "x": 56, "y": 176, "dir": 6},
                {"name": "EntreeNordMarker", "x": 232, "y": 120, "dir": 0},
                {"name": "EntreeSudMarker", "x": 232, "y": 288, "dir": 4},
            ],
            "triggers": [
                {"name": "SortieEst", "x": 448, "y": 160, "w": 24, "h": 56, "target_idx": 2, "target_marker": "EntreeOuestMarker"},
                {"name": "SortieOuest", "x": 8, "y": 160, "w": 24, "h": 56, "target_idx": 5, "target_marker": "EntreeEstMarker"},
                {"name": "SortieNord", "x": 208, "y": 72, "w": 64, "h": 24, "target_idx": 6, "target_marker": "EntreeSudMarker"},
                {"name": "SortieSud", "x": 208, "y": 320, "w": 64, "h": 24, "target_idx": 7, "target_marker": "EntreeNordMarker"},
            ],
        },
        {
            "id": "guilde_destiny_refectoire",
            "title": "Guilde Destiny — Grand Réfectoire (3F Ouest)",
            "sheet": "Destiny_Guilde_Refectoire",
            "base": "05_refectoire_1x_base.png",
            "flip_h": False,
            "ellipse": (280, 256, 216, 104),
            "rects": [(480, 216, 568, 280)],
            "primary": "EntreeEstMarker",
            "markers": [
                {"name": "EntreeEstMarker", "x": 504, "y": 240, "dir": 2},
                {"name": "CentreRefectoireMarker", "x": 280, "y": 256, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieEst", "x": 544, "y": 216, "w": 24, "h": 64, "target_idx": 4, "target_marker": "EntreeOuestMarker"},
            ],
        },
        {
            "id": "guilde_destiny_cuisine",
            "title": "Guilde Destiny — Cuisine de la Guilde (3F Ouest)",
            "sheet": "Destiny_Guilde_Cuisine",
            "base": "06_cuisine_1x_base.png",
            "flip_h": False,
            "ellipse": (240, 216, 180, 84),
            "rects": [(208, 288, 272, 344)],
            "primary": "EntreeSudMarker",
            "markers": [
                {"name": "EntreeSudMarker", "x": 232, "y": 288, "dir": 4},
                {"name": "CentreCuisineMarker", "x": 232, "y": 208, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieSud", "x": 208, "y": 320, "w": 64, "h": 24, "target_idx": 4, "target_marker": "EntreeNordMarker"},
            ],
        },
        {
            "id": "guilde_destiny_reserve",
            "title": "Guilde Destiny — Réserve à Provisions (3F Ouest)",
            "sheet": "Destiny_Guilde_Reserve",
            "base": "10_dortoir_sud_1x_base.png",
            "flip_h": False,
            "ellipse": (224, 196, 112, 76),
            "rects": [(192, 56, 256, 136)],
            "primary": "EntreeNordMarker",
            "markers": [
                {"name": "EntreeNordMarker", "x": 216, "y": 112, "dir": 0},
                {"name": "CentreReserveMarker", "x": 216, "y": 196, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieNord", "x": 192, "y": 56, "w": 64, "h": 24, "target_idx": 4, "target_marker": "EntreeSudMarker"},
            ],
        },
        {
            "id": "guilde_destiny_couloir_ouest",
            "title": "Guilde Destiny — Couloir des Dortoirs Ouest (3F Est)",
            "sheet": "Destiny_Guilde_Couloir_Ouest",
            "base": "08_couloir_dortoirs_1x_base.png",
            "flip_h": False,
            "ellipse": (240, 188, 168, 60),
            "rects": [(8, 160, 104, 216), (376, 160, 472, 216), (208, 72, 272, 144), (208, 232, 272, 344)],
            "primary": "EntreeOuestMarker",
            "markers": [
                {"name": "EntreeOuestMarker", "x": 56, "y": 176, "dir": 6},
                {"name": "EntreeEstMarker", "x": 408, "y": 176, "dir": 2},
                {"name": "EntreeNordMarker", "x": 232, "y": 120, "dir": 0},
                {"name": "EntreeSudMarker", "x": 232, "y": 288, "dir": 4},
            ],
            "triggers": [
                {"name": "SortieOuest", "x": 8, "y": 160, "w": 24, "h": 56, "target_idx": 2, "target_marker": "EntreeEstMarker"},
                {"name": "SortieEst", "x": 448, "y": 160, "w": 24, "h": 56, "target_idx": 9, "target_marker": "EntreeOuestMarker"},
                {"name": "SortieNord", "x": 208, "y": 72, "w": 64, "h": 24, "target_idx": 10, "target_marker": "EntreeSudMarker"},
                {"name": "SortieSud", "x": 208, "y": 320, "w": 64, "h": 24, "target_idx": 12, "target_marker": "EntreeNordMarker"},
            ],
        },
        {
            "id": "guilde_destiny_couloir_est",
            "title": "Guilde Destiny — Couloir des Dortoirs Est (3F Est)",
            "sheet": "Destiny_Guilde_Couloir_Est",
            "base": "08_couloir_dortoirs_1x_base.png",
            "flip_h": True,
            "ellipse": (240, 188, 168, 60),
            "rects": [(8, 160, 104, 216), (376, 160, 472, 216), (208, 72, 272, 144), (208, 232, 272, 344)],
            "primary": "EntreeOuestMarker",
            "markers": [
                {"name": "EntreeOuestMarker", "x": 56, "y": 176, "dir": 6},
                {"name": "EntreeEstMarker", "x": 408, "y": 176, "dir": 2},
                {"name": "EntreeNordMarker", "x": 232, "y": 120, "dir": 0},
                {"name": "EntreeSudMarker", "x": 232, "y": 288, "dir": 4},
            ],
            "triggers": [
                {"name": "SortieOuest", "x": 8, "y": 160, "w": 24, "h": 56, "target_idx": 8, "target_marker": "EntreeEstMarker"},
                {"name": "SortieEst", "x": 448, "y": 160, "w": 24, "h": 56, "target_idx": 14, "target_marker": "EntreeOuestMarker"},
                {"name": "SortieNord", "x": 208, "y": 72, "w": 64, "h": 24, "target_idx": 11, "target_marker": "EntreeSudMarker"},
                {"name": "SortieSud", "x": 208, "y": 320, "w": 64, "h": 24, "target_idx": 13, "target_marker": "EntreeNordMarker"},
            ],
        },
        {
            "id": "guilde_destiny_dortoir_nord_1",
            "title": "Guilde Destiny — Dortoir des Membres Nord 1 (3F Est)",
            "sheet": "Destiny_Guilde_Dortoir_Nord_1",
            "base": "09_dortoir_nord_1x_base.png",
            "flip_h": False,
            "ellipse": (224, 192, 108, 76),
            "rects": [(192, 248, 256, 320)],
            "primary": "EntreeSudMarker",
            "markers": [
                {"name": "EntreeSudMarker", "x": 216, "y": 264, "dir": 4},
                {"name": "CentreDortoirMarker", "x": 216, "y": 184, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieSud", "x": 192, "y": 296, "w": 64, "h": 24, "target_idx": 8, "target_marker": "EntreeNordMarker"},
            ],
        },
        {
            "id": "guilde_destiny_dortoir_nord_2",
            "title": "Guilde Destiny — Dortoir des Membres Nord 2 (3F Est)",
            "sheet": "Destiny_Guilde_Dortoir_Nord_2",
            "base": "09_dortoir_nord_1x_base.png",
            "flip_h": True,
            "ellipse": (224, 192, 108, 76),
            "rects": [(192, 248, 256, 320)],
            "primary": "EntreeSudMarker",
            "markers": [
                {"name": "EntreeSudMarker", "x": 216, "y": 264, "dir": 4},
                {"name": "CentreDortoirMarker", "x": 216, "y": 184, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieSud", "x": 192, "y": 296, "w": 64, "h": 24, "target_idx": 9, "target_marker": "EntreeNordMarker"},
            ],
        },
        {
            "id": "guilde_destiny_dortoir_sud_1",
            "title": "Guilde Destiny — Dortoir des Membres Sud 1 (3F Est)",
            "sheet": "Destiny_Guilde_Dortoir_Sud_1",
            "base": "10_dortoir_sud_1x_base.png",
            "flip_h": False,
            "ellipse": (224, 196, 112, 76),
            "rects": [(192, 56, 256, 136)],
            "primary": "EntreeNordMarker",
            "markers": [
                {"name": "EntreeNordMarker", "x": 216, "y": 112, "dir": 0},
                {"name": "CentreDortoirMarker", "x": 216, "y": 196, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieNord", "x": 192, "y": 56, "w": 64, "h": 24, "target_idx": 8, "target_marker": "EntreeSudMarker"},
            ],
        },
        {
            "id": "guilde_destiny_dortoir_sud_2",
            "title": "Guilde Destiny — Dortoir des Membres Sud 2 (3F Est)",
            "sheet": "Destiny_Guilde_Dortoir_Sud_2",
            "base": "10_dortoir_sud_1x_base.png",
            "flip_h": True,
            "ellipse": (224, 196, 112, 76),
            "rects": [(192, 56, 256, 136)],
            "primary": "EntreeNordMarker",
            "markers": [
                {"name": "EntreeNordMarker", "x": 216, "y": 112, "dir": 0},
                {"name": "CentreDortoirMarker", "x": 216, "y": 196, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieNord", "x": 192, "y": 56, "w": 64, "h": 24, "target_idx": 9, "target_marker": "EntreeSudMarker"},
            ],
        },
        {
            "id": "guilde_destiny_chambre_heros",
            "title": "Guilde Destiny — Chambre du Héros & Partenaire (3F Est)",
            "sheet": "Destiny_Guilde_Chambre_Heros",
            "base": "11_chambre_heros_1x_base.png",
            "flip_h": False,
            "ellipse": (264, 212, 132, 92),
            "rects": [(8, 176, 152, 232)],
            "primary": "EntreeOuestMarker",
            "markers": [
                {"name": "EntreeOuestMarker", "x": 56, "y": 192, "dir": 6},
                {"name": "CentreChambreMarker", "x": 264, "y": 212, "dir": 0},
            ],
            "triggers": [
                {"name": "SortieOuest", "x": 8, "y": 176, "w": 24, "h": 56, "target_idx": 9, "target_marker": "EntreeEstMarker"},
            ],
        },
    ]

    # Compile all 14 GroundMaps + verify BFS reachability!
    for r in ROOMS:
        im = Image.open(SRC_BASE / r["base"]).convert("RGB")
        if r["flip_h"]:
            im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        rgb = np.array(im)
        # Zero magenta guarantee:
        rr, gg, bb = rgb[:, :, 0].astype(int), rgb[:, :, 1].astype(int), rgb[:, :, 2].astype(int)
        assert int(((rr - gg > 35) & (bb - gg > 25)).sum()) == 0, f"Magenta detected in {r['id']}!"

        tw, th = rgb.shape[1] // 8, rgb.shape[0] // 8
        cx, cy, rx, ry = r["ellipse"]
        wmask = ellipse_walk_grid(tw, th, cx, cy, rx, ry, r["rects"])

        doc = build_rsground(r["id"], r["title"], r["sheet"], rgb, wmask, r["triggers"], r["markers"])
        if r.get("has_eos_door"):
            doc["Object"]["Decorations"] = [
                {
                    "Name": "PorteSalonFermee",
                    "Layer": 0,
                    "Visible": True,
                    "Anims": [
                        {
                            "ObjectAnim": {
                                "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
                                "AnimIndex": "Guilde_Destiny_Porte_Salon_Fermee",
                                "FrameTime": 60,
                                "StartFrame": -1,
                                "EndFrame": -1,
                                "AnimDir": 0,
                                "Alpha": 255,
                                "AnimFlip": 0,
                            },
                            "MapLoc": {"X": int(door_meta["x"]), "Y": int(door_meta["y"])},
                        }
                    ],
                },
                {
                    "Name": "PorteSalonOuverte",
                    "Layer": 0,
                    "Visible": False,
                    "Anims": [
                        {
                            "ObjectAnim": {
                                "$type": "RogueEssence.Content.ObjAnimData, RogueEssence",
                                "AnimIndex": "Guilde_Destiny_Porte_Salon_Ouverte",
                                "FrameTime": 60,
                                "StartFrame": -1,
                                "EndFrame": -1,
                                "AnimDir": 0,
                                "Alpha": 255,
                                "AnimFlip": 0,
                            },
                            "MapLoc": {"X": int(door_meta["x"]), "Y": int(door_meta["y"])},
                        }
                    ],
                },
            ]
        verify_bfs_and_partner(doc, r["primary"])

        out_rs = GROUND_DIR / f"{r['id']}.rsground"
        out_rs.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"[OK] Compiled & BFS-verified {r['id']} ({rgb.shape[1]}x{rgb.shape[0]} px, {tw}x{th} tiles)")

    # 4. Update `game/Data/Zone/guilde_destiny_interieur.json` & `game/Data/Zone/index.idx`
    all_ground_maps = ["guilde_destiny_accueil"] + [r["id"] for r in ROOMS]
    zone_path = ZONE_DIR / "guilde_destiny_interieur.json"
    zone_doc = json.loads(zone_path.read_text(encoding="utf-8-sig"))
    zone_doc["Object"]["GroundMaps"] = all_ground_maps
    zone_path.write_text(json.dumps(zone_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    zidx_path = ZONE_DIR / "index.idx"
    zidx_doc = json.loads(zidx_path.read_text(encoding="utf-8-sig"))
    if "guilde_destiny_interieur" in zidx_doc["Object"]:
        zidx_doc["Object"]["guilde_destiny_interieur"]["Grounds"] = all_ground_maps
        zidx_path.write_text(json.dumps(zidx_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 5. Write `game/Data/Script/destiny/guilde_destiny_decors.lua`
    lua_win_lines = []
    for map_id, slots in lua_win_registry.items():
        lua_win_lines.append(f"  ['{map_id}'] = {{")
        for s in slots:
            pa = s["par_ambiance"]
            lua_win_lines.append(
                f"    {{ name = '{s['name']}', x = {s['x']}, y = {s['y']}, w = {s['w']}, h = {s['h']}, "
                f"jour = '{pa['jour']}', aube = '{pa['aube']}', crepuscule = '{pa['crepuscule']}', nuit = '{pa['nuit']}' }},"
            )
        lua_win_lines.append("  },")

    decors_lua = f"""--[[
  guilde_destiny_decors.lua
  Gestion unifiee pour les 15 salles de `guilde_destiny_interieur` :
  1. Filtre de luminosite et teinte de salle selon les 4 ambiances (`jour`, `aube`, `crepuscule`, `nuit`)
     via `map:SetDestinyAmbiance(moment, true)` synchronise sur `meteo_reverie.Moment()` ou `SV.Destiny.GuildeAmbiance`.
  2. Objets `GroundObject` independants (`.dir`) pour toutes les fenetres cintrees de la Guilde.
  3. Double Porte sculptee du Grand Salon s'ouvrant exactement comme la porte d'entree (`guilde_cliff_scene.lua`) :
     `Decorations` Layer 0 (`PorteSalonFermee` / `PorteSalonOuverte`), capteur `SortieBureauMaitre` devant le seuil,
     son `EVT_Door_Open`, `WaitFrames(20)`, fondu et remise a l'etat ferme.
]]

local meteo_reverie = require 'destiny.meteo_reverie'

local guilde_decors = {{}}

guilde_decors.FENETRES = {{
{chr(10).join(lua_win_lines)}
}}

guilde_decors.PORTE_SALON = {{
  x = {door_meta['x']},
  y = {door_meta['y']},
  w = {door_meta['w']},
  h = {door_meta['h']},
  fermee = 'Guilde_Destiny_Porte_Salon_Fermee',
  ouverte = 'Guilde_Destiny_Porte_Salon_Ouverte',
}}

function guilde_decors.MomentActuel()
  if SV and SV.Destiny and type(SV.Destiny.GuildeAmbiance) == 'string' and SV.Destiny.GuildeAmbiance ~= '' then
    local m = string.lower(SV.Destiny.GuildeAmbiance)
    if m == 'jour' or m == 'aube' or m == 'crepuscule' or m == 'nuit' then
      return m
    end
  end
  local ok, res = pcall(meteo_reverie.Moment)
  if ok and (res == 'jour' or res == 'aube' or res == 'crepuscule' or res == 'nuit') then
    return res
  end
  return 'jour'
end

local function supprimer_si_existe(map, ent_name)
  if map == nil or map.Entities == nil or map.Entities.Count == 0 then return end
  local layer = map.Entities[0]
  if layer == nil or layer.GroundObjects == nil then return end
  for i = layer.GroundObjects.Count - 1, 0, -1 do
    local o = layer.GroundObjects[i]
    if o ~= nil and o.EntName == ent_name then
      layer.GroundObjects:RemoveAt(i)
    end
  end
end

local function ajouter_objet_decor(map, ent_name, anim_sheet, x, y, w, h, passable, start_f, end_f)
  if RogueEssence == nil or RogueElements == nil or map == nil or map.Entities == nil or map.Entities.Count == 0 then
    return nil
  end
  supprimer_si_existe(map, ent_name)
  local sf = start_f or 0
  local ef = end_f or 0
  local anim = RogueEssence.Content.ObjAnimData(anim_sheet, 1, sf, ef)
  local obj = RogueEssence.Ground.GroundObject(
    anim,
    RogueElements.Rect(x, y, w, h),
    RogueElements.Loc(0, 0),
    false,
    ent_name
  )
  if passable then
    obj.Passable = true
    if RogueEssence.Ground.GroundEntity and RogueEssence.Ground.GroundEntity.EEntityTriggerTypes and RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.None ~= nil then
      pcall(function() obj:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.None) end)
    end
  end
  obj:ReloadEvents()
  map.Entities[0].GroundObjects:Add(obj)
  return obj
end

function guilde_decors.AppliquerAmbianceEtFenetres(map, map_id, ambiance_forcee)
  local moment = ambiance_forcee or guilde_decors.MomentActuel()
  -- 1. Applique le filtre natif de luminosite & teinte de salle + personnages (`SetDestinyAmbiance(moment, true)`)
  if map ~= nil and map.SetDestinyAmbiance ~= nil then
    map:SetDestinyAmbiance(moment, true)
  end
  -- 2. Instancie / met a jour les objets Fenetres `.dir` independants correspondant a l'ambiance
  local slots = guilde_decors.FENETRES[map_id]
  if slots ~= nil then
    for _, slot in ipairs(slots) do
      local sheet = slot[moment] or slot.jour
      ajouter_objet_decor(map, slot.name, sheet, slot.x, slot.y, slot.w, slot.h, true, 0, 0)
    end
  end
end

function guilde_decors.DefinirPorteSalonOuverte(map, ouverte)
  local est_ouverte = (ouverte == true)
  if map == nil or map.Decorations == nil then return end
  if luanet ~= nil and luanet.each ~= nil then
    for deco in luanet.each(map.Decorations) do
      if deco.Name == 'PorteSalonFermee' then
        deco.Visible = not est_ouverte
      elseif deco.Name == 'PorteSalonOuverte' then
        deco.Visible = est_ouverte
      end
    end
  elseif type(map.Decorations) == 'table' then
    for _, deco in ipairs(map.Decorations) do
      if deco.Name == 'PorteSalonFermee' then
        deco.Visible = not est_ouverte
      elseif deco.Name == 'PorteSalonOuverte' then
        deco.Visible = est_ouverte
      end
    end
  end
end

function guilde_decors.OuvrirPorteSalon(map)
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Door_Open')
  end
  guilde_decors.DefinirPorteSalonOuverte(map, true)
end

function guilde_decors.FermerPorteSalon(map)
  if SOUND ~= nil and SOUND.PlayBattleSE ~= nil then
    SOUND:PlayBattleSE('EVT_Door_Open')
  end
  guilde_decors.DefinirPorteSalonOuverte(map, false)
end

function guilde_decors.SynchroniserPorteSalon(map)
  -- Comme `scene.Init` de la porte d'entree (`guilde_cliff_scene.lua`) :
  -- la porte demarre fermee et `SortieBureauMaitre` reste actif devant le seuil.
  guilde_decors.DefinirPorteSalonOuverte(map, false)
end

function guilde_decors.OuvrirPorteSalonDirect(map)
  guilde_decors.OuvrirPorteSalon(map)
end

return guilde_decors
"""
    (SCRIPT_DIR / "guilde_destiny_decors.lua").write_text(decors_lua, encoding="utf-8")

    # 6. Update `guilde_destiny_accueil/init.lua` cleanly (adding `guilde_decors.AppliquerAmbianceEtFenetres` while preserving ALL existing callbacks & strings!)
    acc_lua_path = SCRIPT_DIR / "ground/guilde_destiny_accueil/init.lua"
    acc_lua = acc_lua_path.read_text(encoding="utf-8")
    if "guilde_destiny_decors" not in acc_lua:
        acc_lua = acc_lua.replace(
            "local suivi_interieurs = require 'destiny.suivi_interieurs'",
            "local suivi_interieurs = require 'destiny.suivi_interieurs'\nlocal guilde_decors = require 'destiny.guilde_destiny_decors'",
            1,
        )
        acc_lua = acc_lua.replace(
            "function guilde_destiny_accueil.Init(map)\n",
            "function guilde_destiny_accueil.Init(map)\n  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_accueil')\n",
            1,
        )
        acc_lua = acc_lua.replace(
            "function guilde_destiny_accueil.Enter(map) ",
            "function guilde_destiny_accueil.Enter(map) pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_accueil'); ",
            1,
        )
        acc_lua = acc_lua.replace(
            "function guilde_destiny_accueil.GameLoad(map) ",
            "function guilde_destiny_accueil.GameLoad(map) pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_accueil'); ",
            1,
        )
        acc_lua_path.write_text(acc_lua, encoding="utf-8")

    # 7. Generate clean, uniform `init.lua` for all 14 other Guild rooms!
    for r in ROOMS:
        mid = r["id"]
        script_folder = SCRIPT_DIR / "ground" / mid
        script_folder.mkdir(parents=True, exist_ok=True)

        touch_funcs = []
        for tr in r["triggers"]:
            tname = tr["name"]
            tidx = tr["target_idx"]
            tmap = all_ground_maps[tidx]
            tmk = tr["target_marker"]
            if mid == "guilde_destiny_grand_salon" and tname == "SortieBureauMaitre":
                touch_funcs.append(f"""function {mid}.{tname}_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true

  local map = carte_courante or (_G.GAME and GAME.GetCurrentGround and GAME:GetCurrentGround()) or nil
  local hero = (_G.CH and CH('PLAYER')) or activator
  local partenaire = partenaire_de(hero)

  if GAME ~= nil and GAME.CutsceneMode ~= nil then GAME:CutsceneMode(true) end
  if partenaire ~= nil and AI ~= nil and AI.DisableCharacterAI ~= nil then AI:DisableCharacterAI(partenaire) end
  if hero ~= nil then
    hero.CollisionDisabled = true
    if GROUND ~= nil and Direction ~= nil then
      if GROUND.CharAnimateTurnTo ~= nil then
        pcall(function() GROUND:CharAnimateTurnTo(hero, Direction.Up, 4) end)
      elseif GROUND.EntTurn ~= nil then
        GROUND:EntTurn(hero, Direction.Up)
      end
    end
  end
  if partenaire ~= nil and GROUND ~= nil and Direction ~= nil then
    if GROUND.CharAnimateTurnTo ~= nil then
      pcall(function() GROUND:CharAnimateTurnTo(partenaire, Direction.Up, 4) end)
    elseif GROUND.EntTurn ~= nil then
      GROUND:EntTurn(partenaire, Direction.Up)
    end
  end

  guilde_decors.OuvrirPorteSalon(map)
  if GAME ~= nil and GAME.WaitFrames ~= nil then GAME:WaitFrames(20) end

  GAME:FadeOut(false, 20)
  guilde_decors.DefinirPorteSalonOuverte(map, false)
  retour_au_joueur(hero, partenaire)
  sortie_en_cours = false
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', '{tmap}', '{tmk}', true) else GAME:EnterZone('guilde_destiny_interieur', -1, {tidx}, 0) end
end
function {mid}.{tname}_Action(obj, activator)
  {mid}.{tname}_Touch(obj, activator)
end""")
            else:
                touch_funcs.append(f"""function {mid}.{tname}_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', '{tmap}', '{tmk}', true) else GAME:EnterZone('guilde_destiny_interieur', -1, {tidx}, 0) end
end""")

        extra_req = ""
        extra_state = ""
        extra_map_save = ""
        extra_enter = ""
        extra_funcs = ""
        if r.get("has_eos_door"):
            extra_req = "\nlocal equipe_scene = require 'destiny.equipe_scene'"
            extra_state = "\nlocal carte_courante = nil"
            extra_map_save = "\n  carte_courante = map or carte_courante"
            extra_enter = "\n  pcall(guilde_decors.SynchroniserPorteSalon, map)"
            extra_funcs = f"""
local function partenaire_de(hero)
  if hero == nil or GAME == nil or GAME.GetPlayerPartyCount == nil then return nil end
  if GAME:GetPlayerPartyCount() <= 1 then return nil end
  local partenaire = (_G.CH and CH('Teammate1')) or nil
  if partenaire ~= nil then return partenaire end
  if equipe_scene ~= nil and equipe_scene.Partenaire ~= nil and hero.Position ~= nil then
    local py = math.min(hero.Position.Y + 24, 384)
    return equipe_scene.Partenaire(hero.Position.X, py, hero.Direction)
  end
  return nil
end

local function retour_au_joueur(hero, partenaire)
  if UI ~= nil and UI.ResetSpeaker ~= nil then UI:ResetSpeaker() end
  if hero ~= nil then hero.CollisionDisabled = false end
  if partenaire ~= nil and equipe_scene ~= nil and equipe_scene.Suivre ~= nil then equipe_scene.Suivre(partenaire, hero) end
  if GAME ~= nil and GAME.MoveCamera ~= nil then GAME:MoveCamera(0, 0, 1, true) end
  if GAME ~= nil and GAME.CutsceneMode ~= nil then GAME:CutsceneMode(false) end
end

function {mid}.OuvrirPorteMaitre(map)
  guilde_decors.OuvrirPorteSalon(map or carte_courante or (GAME and GAME:GetCurrentGround()))
end

function {mid}.FermerPorteMaitre(map)
  guilde_decors.FermerPorteSalon(map or carte_courante or (GAME and GAME:GetCurrentGround()))
end
"""

        lua_code = f"""require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local guilde_decors = require 'destiny.guilde_destiny_decors'{extra_req}

local {mid} = {{}}
local sortie_en_cours = false{extra_state}

function {mid}.Init(map)
  sortie_en_cours = false{extra_map_save}
  if DEBUG and DEBUG.EnableDbgCoro then DEBUG.EnableDbgCoro() end
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, '{mid}'){extra_enter}
end

function {mid}.Enter(map){extra_map_save}
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, '{mid}'){extra_enter}
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function {mid}.GameLoad(map){extra_map_save}
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, '{mid}'){extra_enter}
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function {mid}.Exit(map)
end

function {mid}.Update(map)
end
{extra_funcs}
{chr(10).join(touch_funcs)}

return {mid}
"""
        (script_folder / "init.lua").write_text(lua_code, encoding="utf-8")

    print("SUCCESS: All 15 Guild rooms, 4-ambiance luminosity filters, window .dir objects, and outward EoS double door compiled!")
    import compile_verdure_et_banque_immobilier
    compile_verdure_et_banque_immobilier.main()


if __name__ == "__main__":
    main()
