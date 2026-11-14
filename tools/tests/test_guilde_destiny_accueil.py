#!/usr/bin/env python3
"""Tests structurels, graphiques (0 magenta, 0 Halcyon, calques, collisions BFS) et comportementaux de guilde_destiny_accueil."""
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


def main() -> None:
    z = json.loads((GAME / "Data/Zone/guilde_destiny_interieur.json").read_text(encoding="utf-8-sig"))["Object"]["GroundMaps"]
    idx = json.loads((GAME / "Data/Zone/index.idx").read_text(encoding="utf-8-sig"))["Object"]["guilde_destiny_interieur"]["Grounds"]
    assert z == idx == ["guilde_destiny_accueil"]

    tile_path = GAME / "Content/Tile/Destiny_Guilde_Accueil.tile"
    assert tile_path.is_file()
    bank = load_tile_bank(tile_path)

    g = json.loads((GAME / "Data/Ground/guilde_destiny_accueil.rsground").read_text(encoding="utf-8-sig"))["Object"]
    assert g["AssetName"] == "guilde_destiny_accueil"
    assert g["TexSize"] == 1 and g["EdgeView"] == 1 and g["Music"] == "Guildmaster.ogg"
    assert len(g["Layers"]) == 8
    gw, gh = len(g["Layers"][0]["Tiles"]), len(g["Layers"][0]["Tiles"][0])
    assert (gw, gh) == (80, 60)
    assert g["Layers"][7]["Layer"] == 4

    # Aucune référence à Guild_First_Floor ni aucune planche Halcyon
    sheets_used = {
        f["Sheet"]
        for L in g["Layers"]
        for col in L["Tiles"]
        for t in col
        for an in t.get("Layers", [])
        for f in an.get("Frames", [])
    }
    assert sheets_used == {"Destiny_Guilde_Accueil"}, sheets_used

    # Vérification 0 pixel magenta dans toute la banque de tuiles
    for loc, patch in bank.items():
        nz = patch[..., 3] > 0
        if nz.any():
            r = patch[nz, 0].astype(int)
            gr = patch[nz, 1].astype(int)
            b = patch[nz, 2].astype(int)
            assert not np.any(((r - gr) > 35) & ((b - gr) > 25)), f"Magenta détecté dans la tuile {loc}"

    # Le calque Top (Layer=4) ne recouvre aucune cellule praticable (Tags==0)
    obs = g["obstacles"]
    top_tiles = g["Layers"][7]["Tiles"]
    for tx in range(gw):
        for ty in range(gh):
            if obs[tx][ty]["Tags"] == 0:
                assert not top_tiles[tx][ty]["Layers"], f"Calque Top déborde sur sol praticable ({tx},{ty})"

    # Vérification marqueurs, capteur de sortie sud et accessibilité BFS 16x16
    markers = {m["EntName"]: m["Collider"] for m in g["Entities"][0]["Markers"]}
    assert {"EntreeSudMarker", "CentreMedaillonMarker", "EscalierNordMarker"} <= set(markers)
    gos = {o["EntName"]: o for o in g["Entities"][0]["GroundObjects"]}
    assert "SortieGuilde" in gos and gos["SortieGuilde"]["triggerType"] == 2 and not gos["SortieGuilde"]["Passable"]

    def free16(px: int, py: int) -> bool:
        if px < 0 or py < 0 or px + 16 > gw * 8 or py + 16 > gh * 8:
            return False
        return all(
            obs[cx][cy]["Tags"] == 0
            for cx in range(px // 8, (px + 15) // 8 + 1)
            for cy in range(py // 8, (py + 15) // 8 + 1)
        )

    ent = markers["EntreeSudMarker"]
    assert free16(ent["X"], ent["Y"]) and free16(ent["X"] + 24, ent["Y"]) and free16(ent["X"] - 24, ent["Y"])

    q = deque([(ent["X"], ent["Y"])])
    seen = {(ent["X"], ent["Y"])}
    while q:
        px, py = q.popleft()
        for nx, ny in ((px + 4, py), (px - 4, py), (px, py + 4), (px, py - 4)):
            if (nx, ny) not in seen and free16(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))

    for mk_name in ("CentreMedaillonMarker", "EscalierNordMarker"):
        mk = markers[mk_name]
        assert (mk["X"], mk["Y"]) in seen, f"{mk_name} non joignable"
    sc = gos["SortieGuilde"]["Collider"]
    assert any(
        (px, sc["Y"] - 16) in seen and px < sc["X"] + sc["Width"] and px + 16 > sc["X"]
        for px in range(sc["X"], sc["X"] + sc["Width"], 4)
    ), "SortieGuilde non joignable"

    script_txt = (GAME / "Data/Script/destiny/ground/guilde_destiny_accueil/init.lua").read_text(encoding="utf-8")
    assert "sortie_en_cours = false; GAME:FadeIn(20)" in script_txt
    assert script_txt.count("suivi_interieurs.Activer(map)") == 2

    os.chdir(ROOT)
    run(ROOT / "tools/tests/test_guilde_destiny_accueil.lua", ROOT)
    print("PASS guilde_destiny_accueil : 640x480, 8 calques, 0 magenta, 0 Halcyon, BFS 16x16 et raccord falaise <-> accueil validés.")


if __name__ == "__main__":
    main()
