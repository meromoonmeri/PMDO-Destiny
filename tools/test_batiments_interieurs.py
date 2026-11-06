#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôles statiques des intérieurs de bâtiments de Réverie Town.

Vérifie l'import des cartes town02 et de leurs Tilesheets, la cohérence de
la zone et de l'index des tuiles, les portes installées en ville et les
sorties des intérieurs. Ne remplace pas un test du runtime PMDO : les
coordonnées des seuils, relevées sur le rendu de la carte, restent à
confirmer en jeu.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INTERIEURS = [
    "reverie_post_office", "reverie_fire_home", "reverie_water_home",
    "reverie_electric_home", "reverie_grass_home", "reverie_rock_home",
    "reverie_normal_home", "reverie_inn", "guild_storage_room",
    "guild_heros_room", "ledian_dojo", "dojo_ossatueur", "dojo_kingambit",
]

# Les huit coques Réverie de la 0.4.6 : architecture et sorties conservées,
# calques Objects et entités de mobilier/PNJ retirés.
COQUES_REVERIE = INTERIEURS[:8]

PORTES = [
    "PortePosteBekipan", "PorteCitrouilleNordOuest", "PorteHutteNordEst",
    "PorteDojoKingambit", "PorteHutteSud",
    "PorteTenteCentre", "PorteTenteEst",
    "PorteMaisonPierre", "PorteMaisonPlanteSud", "PorteCitrouilleSud",
]


def lire(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def feuilles(carte: Path) -> set[str]:
    doc = json.loads(carte.read_text(encoding="utf-8-sig"))
    noms = set()
    for calque in doc["Object"].get("Layers") or []:
        for colonne in calque.get("Tiles") or []:
            for tuile in colonne or []:
                if not isinstance(tuile, dict):
                    continue
                for sous in tuile.get("Layers") or []:
                    for frame in (sous or {}).get("Frames") or []:
                        if frame.get("Sheet"):
                            noms.add(frame["Sheet"])
    return noms


def main() -> int:
    zone = json.loads(lire(ROOT / "game/Data/Zone/town02_waterfallvillage.json"))
    grounds = zone["Object"]["GroundMaps"]
    assert grounds[5:] == INTERIEURS, grounds
    index = json.loads(lire(ROOT / "game/Data/Zone/index.idx"))
    assert index["Object"]["town02_waterfallvillage"]["Grounds"] == grounds

    for nom in INTERIEURS:
        carte = ROOT / "game/Data/Ground" / f"{nom}.rsground"
        assert carte.is_file(), f"intérieur absent : {nom}"
        brut = carte.read_bytes().lower()
        assert b"halcyon" not in brut and b"remixed" not in brut
        for feuille in feuilles(carte):
            assert (ROOT / "game/Content/Tile" / f"{feuille}.tile").is_file() or (
                ROOT / "base/Content/Tile" / f"{feuille}.tile"
            ).is_file(), f"{nom} : planche manquante {feuille}"
        script = ROOT / "game/Data/Script/destiny/ground" / nom / "init.lua"
        assert script.is_file(), f"script absent : {nom}"
        texte = lire(script)
        assert "_Touch(obj, activator) sortir()" in texte
        assert "ArriveeVille = 'batiment'" in texte
        assert "Halcyon" not in texte and "Remixed" not in texte
        if nom in COQUES_REVERIE:
            doc = json.loads(carte.read_text(encoding="utf-8-sig"))["Object"]
            assert doc["AssetName"] == nom
            assert doc["EdgeView"] == 1
            assert not (feuilles(carte) & {'Reverie_Town_Base', 'Reverie_Town_Fringe', 'Reverie_Town_Animated', 'Reverie_Town_River_Animation_1', 'Reverie_Town_River', 'Reverie_Town_Cliffs_Night', 'Reverie_Town_Objects_Under', 'Reverie_Altere_Transition_Base', 'Reverie_Town_Objects_Under_Night', 'Reverie_Town_Objects', 'Reverie_Town_Animation_Tileset_Night', 'Reverie_Town_Animated_Night', 'Reverie_Town_Cafe', 'Reverie_Town_Cafe_Base', 'Reverie_Town_River_Animation_2', 'Reverie_Town_Cave_Base', 'Reverie_Town_River_Animation_3_Night', 'Reverie_Town_Objects_Over', 'Reverie_Altere_Transition_Objects', 'Reverie_Town_River_Animation_4', 'Reverie_Town_Objects_Over_Night', 'Reverie_Town_River_Animation_3', 'Reverie_Town_Trimmed', 'Reverie_Town_Base_Night', 'Reverie_Town_Cliffs', 'Reverie_Town_Cafe_Objects', 'Reverie_Town_Objects_Night', 'Reverie_Town_Animation_Tileset'}), nom
            assert not any(f.endswith(("_Objects", "_Objects_Over")) for f in feuilles(carte)), nom
            if nom == "reverie_inn":
                assert "Reverie_Inn_Shadows" not in feuilles(carte)
                assert "Reverie_Inn_Floor_Decor" not in feuilles(carte)
            if nom == "reverie_post_office":
                assert feuilles(carte) == {"Reverie_Post_Office"}
            for groupe in doc.get("Entities") or []:
                assert not (groupe.get("MapChars") or []), nom
                for objet in groupe.get("GroundObjects") or []:
                    assert objet["EntName"] == "South_Exit" or objet["EntName"].endswith("_Entrance"), (nom, objet)

    resultat = subprocess.run(
        [sys.executable, str(ROOT / "tools/build_tile_index.py"), "--check"],
        capture_output=True, text=True,
    )
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr

    ville = lire(ROOT / "game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua")
    for porte in PORTES:
        assert porte in ville, f"porte absente : {porte}"
    for porte in ("PorteMaisonEquipe", "PorteMaisonArcanine"):
        assert porte not in ville, f"porte interdite encore active : {porte}"
    assert "GAME:EnterGroundMap('town02_waterfallvillage', porte.interieur, porte.marqueur)" in ville
    assert "ArriveeVille == 'batiment'" in ville and "RetourBatimentX" in ville

    try:
        from lupa import LuaRuntime

        charger = LuaRuntime().eval("load")
        fichiers = [ROOT / "game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua"]
        fichiers += [ROOT / "game/Data/Script/destiny/ground" / n / "init.lua" for n in INTERIEURS]
        for fichier in fichiers:
            assert charger(lire(fichier)) is not None, f"Lua invalide : {fichier}"
    except ImportError:
        print("Lupa absent : analyse Lua ignorée.")

    print("Contrôles bâtiments → intérieurs : OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
