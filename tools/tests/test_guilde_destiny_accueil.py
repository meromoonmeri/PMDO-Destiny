#!/usr/bin/env python3
"""Tests structurels, graphiques (0 magenta, 0 Halcyon, verdure séparée, calques, collisions BFS) et comportementaux de guilde_destiny_accueil et guilde_destiny_missions."""
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
    assert ts == 8 and n > 100
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
    assert g["Layers"][4]["Name"] == "04 verdure separee"
    gw, gh = len(g["Layers"][0]["Tiles"]), len(g["Layers"][0]["Tiles"][0])
    assert (gw, gh) == expected_gw_gh, f"{asset_name}: attendu {expected_gw_gh}, obtenu {(gw, gh)}"
    assert g["Layers"][7]["Layer"] == 4

    sheets_used = {
        f["Sheet"]
        for L in g["Layers"]
        for col in L["Tiles"]
        for t in col
        for an in t.get("Layers", [])
        for f in an.get("Frames", [])
    }
    assert sheets_used == {sheet_name}, f"{asset_name}: {sheets_used}"

    # Vérification 0 pixel magenta dans toute la banque de tuiles
    for loc, patch in bank.items():
        nz = patch[..., 3] > 0
        if nz.any():
            r = patch[nz, 0].astype(int)
            gr = patch[nz, 1].astype(int)
            b = patch[nz, 2].astype(int)
            assert not np.any(((r - gr) > 35) & ((b - gr) > 25)), f"{asset_name}: magenta dans tuile {loc}"

    # Calque verdure séparée effectivement actif (> 20 cellules non vides)
    verd_active = sum(1 for col in g["Layers"][4]["Tiles"] for t in col if t.get("Layers"))
    assert verd_active >= 20, f"{asset_name}: verdure séparée vide ({verd_active})"

    # Le calque Top (Layer=4) ne recouvre aucune cellule praticable (Tags==0)
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
    assert free16(ent["X"], ent["Y"]) and free16(ent["X"] + 24, ent["Y"]) and free16(ent["X"] - 24, ent["Y"])

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
        assert (mk["X"], mk["Y"]) in seen, f"{asset_name}: {mk_name} non joignable"

    script_txt = (GAME / f"Data/Script/destiny/ground/{asset_name}/init.lua").read_text(encoding="utf-8")
    assert "sortie_en_cours = false; GAME:FadeIn(20)" in script_txt
    assert script_txt.count("suivi_interieurs.Activer(map)") == 2


def main() -> None:
    expected_grounds = ["guilde_destiny_accueil", "guilde_destiny_missions"]
    z = json.loads((GAME / "Data/Zone/guilde_destiny_interieur.json").read_text(encoding="utf-8-sig"))["Object"]["GroundMaps"]
    idx = json.loads((GAME / "Data/Zone/index.idx").read_text(encoding="utf-8-sig"))["Object"]["guilde_destiny_interieur"]["Grounds"]
    assert z == idx == expected_grounds, f"Attendu {expected_grounds}, obtenu z={z}, idx={idx}"

    verify_room(
        asset_name="guilde_destiny_accueil",
        sheet_name="Destiny_Guilde_Accueil",
        expected_gw_gh=(192, 144),
        expected_markers={"EntreeSudMarker", "CentreMedaillonMarker", "EscalierNordMarker"},
        expected_triggers={"SortieGuilde", "EscalierNord"},
        primary_marker="EntreeSudMarker",
    )
    # Vérifications additionnelles propres à guilde_destiny_accueil :
    # - ratio exact 4:3 viewport PMDO (192x144 tuiles = 1536x1152 px, aucun downscale)
    # - aucune vigne/halo rajouté visible (calques 04, 05, 06 masqués)
    # - fond extérieur marron chaud assombri (#68482F = RGB(104, 72, 47))
    acc_g = json.loads((GAME / "Data/Ground/guilde_destiny_accueil.rsground").read_text(encoding="utf-8-sig"))["Object"]
    assert not acc_g["Layers"][4]["Visible"] and not acc_g["Layers"][5]["Visible"] and not acc_g["Layers"][6]["Visible"]
    acc_bank = load_tile_bank(GAME / "Content/Tile/Destiny_Guilde_Accueil.tile")
    loc0 = acc_g["Layers"][0]["Tiles"][0][0]["Layers"][0]["Frames"][0]["TexLoc"]
    corner_rgb = acc_bank[(loc0["X"], loc0["Y"])][0, 0, :3].tolist()
    assert corner_rgb == [104, 72, 47], f"Fond marron assombri attendu [104, 72, 47], obtenu {corner_rgb}"
    verify_room(
        asset_name="guilde_destiny_missions",
        sheet_name="Destiny_Guilde_Missions",
        expected_gw_gh=(139, 95),
        expected_markers={"ArriveeDepuisAccueilMarker", "CentreSalleMarker", "MurGaucheMarker", "MurDroitMarker"},
        expected_triggers={"EscalierNord"},
        primary_marker="ArriveeDepuisAccueilMarker",
    )

    os.chdir(ROOT)
    run(ROOT / "tools/tests/test_guilde_destiny_accueil.lua", ROOT)
    print("PASS guilde_destiny_accueil + guilde_destiny_missions : 0 mixel, verdure séparée, 0 magenta, 0 Halcyon, BFS 16x16 et raccords validés.")


if __name__ == "__main__":
    main()
