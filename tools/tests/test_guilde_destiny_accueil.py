#!/usr/bin/env python3
"""
Tests structurels, graphiques (0 magenta, 0 Halcyon, verdure séparée, calques, collisions BFS 16x16),
objets `.dir` indépendants (fenêtres 4 ambiances + double porte battante extérieure style PMD EoS)
et simulation comportementale Lua des 15 salles de `guilde_destiny_interieur` (avec filtre de luminosité
`SetDestinyAmbiance(moment, true)`).
"""
from __future__ import annotations

import io
import json
import os
import struct
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "game"


def load_tile_bank(path: Path) -> dict[tuple[int, int], np.ndarray]:
    raw = path.read_bytes()
    ts, n = struct.unpack_from("<ii", raw, 0)
    assert ts == 8 and n > 100, f"{path}: ts={ts}, n={n}"
    out: dict[tuple[int, int], np.ndarray] = {}
    for i in range(n):
        tx, ty, ptr = struct.unpack_from("<iiq", raw, 8 + i * 16)
        plen = struct.unpack_from("<q", raw, ptr)[0]
        im = Image.open(io.BytesIO(raw[ptr + 8 : ptr + 8 + plen])).convert("RGBA")
        arr = np.array(im, dtype=np.float32)
        nz = arr[..., 3] > 0
        arr[nz, :3] = np.clip(np.round(arr[nz, :3] * 255.0 / arr[nz, 3:4]), 0, 255)
        out[(tx, ty)] = arr.astype(np.uint8)
    return out


def verify_dir_object(path: Path, expected_frames: int = 1) -> tuple[int, int]:
    assert path.is_file(), f"Objet .dir manquant : {path}"
    raw = path.read_bytes()
    plen = struct.unpack_from("<q", raw, 0)[0]
    assert len(raw) == 8 + plen + 16, f"Taille .dir invalide : {path}"
    im = Image.open(io.BytesIO(raw[8 : 8 + plen])).convert("RGBA")
    tw, th, anim_f, dirs = struct.unpack_from("<iiii", raw, 8 + plen)
    assert tw == im.width and im.height == th * expected_frames and anim_f == 0 and dirs == 1, (
        path, im.size, (tw, th, anim_f, dirs)
    )
    return tw, th


def verify_room(
    asset_name: str,
    sheet_name: str,
    expected_gw_gh: tuple[int, int],
    expected_markers: set[str],
    expected_triggers: set[str],
    primary_marker: str,
) -> None:
    tile_path = GAME / f"Content/Tile/{sheet_name}.tile"
    assert tile_path.is_file(), f"Tile manquant : {tile_path}"
    bank = load_tile_bank(tile_path)

    g = json.loads((GAME / f"Data/Ground/{asset_name}.rsground").read_text(encoding="utf-8-sig"))["Object"]
    assert g["AssetName"] == asset_name
    assert g["TexSize"] == 1 and g["EdgeView"] == 1 and g["Music"] == "Guildmaster.ogg"
    assert len(g["Layers"]) == 8
    assert g["Layers"][4]["Name"] == "04 verdure separee" and g["Layers"][4]["Visible"] is True
    assert g["Layers"][5]["Name"] == "05 ombres mobilier guilde" and g["Layers"][5]["Visible"] is True
    assert g["Layers"][6]["Name"] == "06 immobilier guilde" and g["Layers"][6]["Visible"] is True
    gw, gh = len(g["Layers"][0]["Tiles"]), len(g["Layers"][0]["Tiles"][0])
    assert (gw, gh) == expected_gw_gh, f"{asset_name}: attendu {expected_gw_gh}, obtenu {(gw, gh)}"
    assert g["Layers"][7]["Layer"] == 4

    arch_sheets = {
        f["Sheet"]
        for li in (0, 1, 2, 3, 7)
        for col in g["Layers"][li]["Tiles"]
        for t in col
        for an in t.get("Layers", [])
        for f in an.get("Frames", [])
    }
    assert arch_sheets == {sheet_name}, f"{asset_name}: calques architecture {arch_sheets}"

    verd_sheets = {
        f["Sheet"]
        for col in g["Layers"][4]["Tiles"]
        for t in col
        for an in t.get("Layers", [])
        for f in an.get("Frames", [])
    }
    assert verd_sheets == {"Destiny_Guilde_Verdure"}, f"{asset_name}: calque verdure {verd_sheets}"

    # Les calques 05 et 06 restent vierges pour placement manuel en jeu par l'utilisateur
    for li in (5, 6):
        assert sum(1 for col in g["Layers"][li]["Tiles"] for t in col if t.get("Layers")) == 0

    for loc, patch in bank.items():
        nz = patch[..., 3] > 0
        if nz.any():
            r = patch[nz, 0].astype(int)
            gr = patch[nz, 1].astype(int)
            b = patch[nz, 2].astype(int)
            assert not np.any(((r - gr) > 35) & ((b - gr) > 25)), f"{asset_name}: magenta dans tuile {loc}"

    verd_active = sum(1 for col in g["Layers"][4]["Tiles"] for t in col if t.get("Layers"))
    assert verd_active >= 20, f"{asset_name}: verdure séparée vide ({verd_active})"

    obs = g["obstacles"]
    top_tiles = g["Layers"][7]["Tiles"]
    for tx in range(gw):
        for ty in range(gh):
            if obs[tx][ty]["Tags"] == 0:
                assert not top_tiles[tx][ty]["Layers"], f"{asset_name}: Top déborde sur sol praticable ({tx},{ty})"

    markers = {m["EntName"]: m["Collider"] for m in g["Entities"][0]["Markers"]}
    assert expected_markers <= set(markers), f"{asset_name}: marqueurs manquants {expected_markers - set(markers)}"
    gos = {o["EntName"]: o for o in g["Entities"][0]["GroundObjects"]}
    assert expected_triggers <= set(gos), f"{asset_name}: capteurs manquants {expected_triggers - set(gos)}"
    for tname in expected_triggers:
        assert gos[tname]["triggerType"] == 2 and not gos[tname]["Passable"]

    def free16(px: int, py: int) -> bool:
        if px < 0 or py < 0 or px + 16 > gw * 8 or py + 16 > gh * 8:
            return False
        return all(
            obs[cx][cy]["Tags"] == 0
            for cx in range(px // 8, (px + 15) // 8 + 1)
            for cy in range(py // 8, (py + 15) // 8 + 1)
        )

    ent = markers[primary_marker]
    assert free16(ent["X"], ent["Y"]), f"{asset_name}: {primary_marker} bloqué"
    offsets = [(24, 0), (-24, 0), (0, -24), (0, 24), (32, 0), (-32, 0), (0, -32), (0, 32)]
    assert any(free16(ent["X"] + dx, ent["Y"] + dy) for dx, dy in offsets), f"{asset_name}: aucun offset partenaire libre"

    q = deque([(ent["X"], ent["Y"])])
    seen = {(ent["X"], ent["Y"])}
    while q:
        px, py = q.popleft()
        for nx, ny in ((px + 4, py), (px - 4, py), (px, py + 4), (px, py - 4)):
            if (nx, ny) not in seen and free16(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))

    for mk_name in expected_markers:
        mk = markers[mk_name]
        assert any(abs(x - mk["X"]) <= 4 and abs(y - mk["Y"]) <= 4 for x, y in seen), f"{asset_name}: {mk_name} non joignable"

    script_txt = (GAME / f"Data/Script/destiny/ground/{asset_name}/init.lua").read_text(encoding="utf-8")
    assert "sortie_en_cours = false; GAME:FadeIn(20)" in script_txt
    assert script_txt.count("suivi_interieurs.Activer(map)") == 2
    assert "guilde_destiny_decors" in script_txt


def main() -> None:
    expected_grounds = [
        "guilde_destiny_accueil",
        "guilde_destiny_missions",
        "guilde_destiny_grand_salon",
        "guilde_destiny_bureau_maitre",
        "guilde_destiny_carrefour",
        "guilde_destiny_refectoire",
        "guilde_destiny_cuisine",
        "guilde_destiny_reserve",
        "guilde_destiny_couloir_ouest",
        "guilde_destiny_couloir_est",
        "guilde_destiny_dortoir_nord_1",
        "guilde_destiny_dortoir_nord_2",
        "guilde_destiny_dortoir_sud_1",
        "guilde_destiny_dortoir_sud_2",
        "guilde_destiny_chambre_heros",
    ]
    z = json.loads((GAME / "Data/Zone/guilde_destiny_interieur.json").read_text(encoding="utf-8-sig"))["Object"]["GroundMaps"]
    idx = json.loads((GAME / "Data/Zone/index.idx").read_text(encoding="utf-8-sig"))["Object"]["guilde_destiny_interieur"]["Grounds"]
    assert z == idx == expected_grounds, f"Attendu {expected_grounds}, obtenu z={z}, idx={idx}"

    # Vérification des objets `.dir` de la porte battante extérieure style PMD EoS + fenêtres 4 ambiances
    verify_dir_object(GAME / "Content/Object/Guilde_Destiny_Porte_Salon_Fermee.dir", expected_frames=1)
    verify_dir_object(GAME / "Content/Object/Guilde_Destiny_Porte_Salon_Ouverte.dir", expected_frames=1)
    assert not (GAME / "Content/Object/Guilde_Destiny_Porte_Salon_Ouverture.dir").exists(), "Aucune animation intermediaire ne doit subsister"
    for win_dir in sorted((GAME / "Content/Object").glob("Guilde_Fenetre_*.dir")):
        verify_dir_object(win_dir, expected_frames=1)

    room_specs = [
        ("guilde_destiny_accueil", "Destiny_Guilde_Accueil", (192, 144), {"EntreeSudMarker", "CentreMedaillonMarker", "EscalierNordMarker"}, {"SortieGuilde", "EscalierNord"}, "EntreeSudMarker"),
        ("guilde_destiny_missions", "Destiny_Guilde_Missions", (72, 54), {"ArriveeDepuisAccueilMarker", "EscalierNordMarker", "CentreSalleMarker", "MurGaucheMarker", "MurDroitMarker"}, {"EscalierSud", "EscalierNord"}, "ArriveeDepuisAccueilMarker"),
        ("guilde_destiny_grand_salon", "Destiny_Guilde_Grand_Salon", (72, 54), {"ArriveeSudMarker", "DevantPorteMaitreMarker", "EntreeOuestMarker", "EntreeEstMarker"}, {"SeuilSud", "SortieBureauMaitre", "CouloirOuest", "CouloirEst"}, "ArriveeSudMarker"),
        ("guilde_destiny_bureau_maitre", "Destiny_Guilde_Bureau_Maitre", (64, 48), {"EntreeSudMarker", "CentreBureauMarker"}, {"SeuilSud"}, "EntreeSudMarker"),
        ("guilde_destiny_carrefour", "Destiny_Guilde_Carrefour", (60, 45), {"EntreeEstMarker", "EntreeOuestMarker", "EntreeNordMarker", "EntreeSudMarker"}, {"SortieEst", "SortieOuest", "SortieNord", "SortieSud"}, "EntreeEstMarker"),
        ("guilde_destiny_refectoire", "Destiny_Guilde_Refectoire", (72, 54), {"EntreeEstMarker", "CentreRefectoireMarker"}, {"SortieEst"}, "EntreeEstMarker"),
        ("guilde_destiny_cuisine", "Destiny_Guilde_Cuisine", (60, 45), {"EntreeSudMarker", "CentreCuisineMarker"}, {"SortieSud"}, "EntreeSudMarker"),
        ("guilde_destiny_reserve", "Destiny_Guilde_Reserve", (56, 42), {"EntreeNordMarker", "CentreReserveMarker"}, {"SortieNord"}, "EntreeNordMarker"),
        ("guilde_destiny_couloir_ouest", "Destiny_Guilde_Couloir_Ouest", (60, 45), {"EntreeOuestMarker", "EntreeEstMarker", "EntreeNordMarker", "EntreeSudMarker"}, {"SortieOuest", "SortieEst", "SortieNord", "SortieSud"}, "EntreeOuestMarker"),
        ("guilde_destiny_couloir_est", "Destiny_Guilde_Couloir_Est", (60, 45), {"EntreeOuestMarker", "EntreeEstMarker", "EntreeNordMarker", "EntreeSudMarker"}, {"SortieOuest", "SortieEst", "SortieNord", "SortieSud"}, "EntreeOuestMarker"),
        ("guilde_destiny_dortoir_nord_1", "Destiny_Guilde_Dortoir_Nord_1", (56, 42), {"EntreeSudMarker", "CentreDortoirMarker"}, {"SortieSud"}, "EntreeSudMarker"),
        ("guilde_destiny_dortoir_nord_2", "Destiny_Guilde_Dortoir_Nord_2", (56, 42), {"EntreeSudMarker", "CentreDortoirMarker"}, {"SortieSud"}, "EntreeSudMarker"),
        ("guilde_destiny_dortoir_sud_1", "Destiny_Guilde_Dortoir_Sud_1", (56, 42), {"EntreeNordMarker", "CentreDortoirMarker"}, {"SortieNord"}, "EntreeNordMarker"),
        ("guilde_destiny_dortoir_sud_2", "Destiny_Guilde_Dortoir_Sud_2", (56, 42), {"EntreeNordMarker", "CentreDortoirMarker"}, {"SortieNord"}, "EntreeNordMarker"),
        ("guilde_destiny_chambre_heros", "Destiny_Guilde_Chambre_Heros", (60, 45), {"EntreeOuestMarker", "CentreChambreMarker"}, {"SortieOuest"}, "EntreeOuestMarker"),
    ]
    for spec in room_specs:
        verify_room(*spec)

    # Vérification stricte de la double porte du Grand Salon alignée sur le modèle de la porte d'entrée (`guilde_cliff_*`)
    sal_g = json.loads((GAME / "Data/Ground/guilde_destiny_grand_salon.rsground").read_text(encoding="utf-8-sig"))["Object"]
    sal_decos = sal_g["Decorations"]
    assert [d["Name"] for d in sal_decos] == ["PorteSalonFermee", "PorteSalonOuverte"], sal_decos
    assert sal_decos[0]["Layer"] == 0 and sal_decos[0]["Visible"] is True
    assert sal_decos[0]["Anims"][0]["ObjectAnim"]["AnimIndex"] == "Guilde_Destiny_Porte_Salon_Fermee"
    assert sal_decos[0]["Anims"][0]["MapLoc"] == {"X": 224, "Y": 64}
    assert sal_decos[1]["Layer"] == 0 and sal_decos[1]["Visible"] is False
    assert sal_decos[1]["Anims"][0]["ObjectAnim"]["AnimIndex"] == "Guilde_Destiny_Porte_Salon_Ouverte"
    assert sal_decos[1]["Anims"][0]["MapLoc"] == {"X": 224, "Y": 64}

    # Zéro interstice (100 % opaque `alpha == 255` sur tout le patch 128x96) et pleine hauteur d'arche :
    def _load_dir_rgba(path: Path) -> np.ndarray:
        raw = path.read_bytes()
        plen = struct.unpack("<q", raw[:8])[0]
        return np.array(Image.open(io.BytesIO(raw[8 : 8 + plen])).convert("RGBA"))

    fermee_rgba = _load_dir_rgba(GAME / "Content/Object/Guilde_Destiny_Porte_Salon_Fermee.dir")
    ouverte_rgba = _load_dir_rgba(GAME / "Content/Object/Guilde_Destiny_Porte_Salon_Ouverte.dir")
    assert fermee_rgba.shape == (96, 128, 4) and ouverte_rgba.shape == (96, 128, 4)
    assert int(fermee_rgba[:, :, 3].min()) == 255, "Aucun trou/interstice alpha autorisé dans PorteSalonFermee"
    assert int(ouverte_rgba[:, :, 3].min()) == 255, "Aucun trou/interstice alpha autorisé dans PorteSalonOuverte"
    diff_door = np.abs(fermee_rgba[:, :, :3].astype(int) - ouverte_rgba[:, :, :3].astype(int)).max(axis=2) > 10
    dys_l = np.where(diff_door[:, 14:20])[0]
    assert len(dys_l) > 0 and int(dys_l.min()) <= 14 and int(dys_l.max() - dys_l.min() + 1) >= 74, (
        "Les battants ouverts doivent atteindre la pleine hauteur de l'arche (y_global <= 78, h >= 74 px)"
    )

    sal_gos = {o["EntName"]: o for o in sal_g["Entities"][0]["GroundObjects"]}
    assert sal_gos["SortieBureauMaitre"]["Collider"] == {"X": 264, "Y": 144, "Width": 48, "Height": 16}
    assert sal_gos["SortieBureauMaitre"]["EntEnabled"] is True and sal_gos["SortieBureauMaitre"]["Passable"] is False
    assert sal_gos["SeuilSud"]["Collider"] == {"X": 256, "Y": 368, "Width": 64, "Height": 24}

    # Vérifie que l'entrée escalier sud en bois est bien présente sur `Destiny_Guilde_Grand_Salon` (pas du vide marron #68482F en y=376) :
    sal_bank = load_tile_bank(GAME / "Content/Tile/Destiny_Guilde_Grand_Salon.tile")
    stair_tile_rgb = None
    for layer in sal_g["Layers"][:4]:
        if layer["Visible"] and layer["Tiles"][35][47]["Layers"]:
            tloc = layer["Tiles"][35][47]["Layers"][0]["Frames"][0]["TexLoc"]
            stair_tile_rgb = sal_bank[(tloc["X"], tloc["Y"])][0, 4, :3].tolist()
    assert stair_tile_rgb is not None and stair_tile_rgb[0] > 125, (
        f"L'escalier sud en bois du Grand Salon doit être dessiné en (x=284, y=376), obtenu {stair_tile_rgb}"
    )

    for tx in range(33, 39):
        for ty in range(12, 18):
            assert sal_g["obstacles"][tx][ty]["Tags"] != 0, f"Intérieur porte fermée marchable en ({tx},{ty})"

    # Vérifie les banques dédiées `Destiny_Guilde_Verdure` et `Destiny_Guilde_Immobilier` + les 135 objets `.dir` d'immobilier :
    for extra_sheet in ("Destiny_Guilde_Verdure", "Destiny_Guilde_Immobilier"):
        ebank = load_tile_bank(GAME / f"Content/Tile/{extra_sheet}.tile")
        for loc, patch in ebank.items():
            nz = patch[..., 3] > 0
            if nz.any():
                r, gr, b = patch[nz, 0].astype(int), patch[nz, 1].astype(int), patch[nz, 2].astype(int)
                assert not np.any(((r - gr) > 35) & ((b - gr) > 25)), f"{extra_sheet}: magenta en {loc}"

    imm_dirs = sorted((GAME / "Content/Object").glob("Guilde_Imm_*.dir"))
    assert len(imm_dirs) >= 120, f"Attendu >= 120 objets Guilde_Imm_*.dir, trouvé {len(imm_dirs)}"
    for dp in imm_dirs:
        verify_dir_object(dp, expected_frames=1)
        rgba_d = _load_dir_rgba(dp)
        nz = rgba_d[..., 3] > 0
        if nz.any():
            # Unpremultiply before checking magenta
            a_f = rgba_d[nz, 3:4].astype(np.float32)
            rgb_u = np.clip(np.round(rgba_d[nz, :3].astype(np.float32) * 255.0 / a_f), 0, 255).astype(int)
            assert not np.any(((rgb_u[:, 0] - rgb_u[:, 1]) > 35) & ((rgb_u[:, 2] - rgb_u[:, 1]) > 25)), f"Magenta dans {dp.name}"

    acc_g = json.loads((GAME / "Data/Ground/guilde_destiny_accueil.rsground").read_text(encoding="utf-8-sig"))["Object"]
    assert acc_g["Layers"][4]["Visible"] and acc_g["Layers"][5]["Visible"] and acc_g["Layers"][6]["Visible"]
    acc_bank = load_tile_bank(GAME / "Content/Tile/Destiny_Guilde_Accueil.tile")
    loc0 = acc_g["Layers"][0]["Tiles"][0][0]["Layers"][0]["Frames"][0]["TexLoc"]
    corner_rgb = acc_bank[(loc0["X"], loc0["Y"])][0, 0, :3].tolist()
    assert corner_rgb == [104, 72, 47], f"Fond marron assombri attendu [104, 72, 47], obtenu {corner_rgb}"

    os.chdir(ROOT)
    run(ROOT / "tools/tests/test_guilde_destiny_accueil.lua", ROOT)
    print("PASS réseau complet Guilde Destiny (15 salles, 4 ambiances + filtre luminosité, fenêtres .dir, porte battante extérieure EoS, BFS 16x16).")


if __name__ == "__main__":
    main()
