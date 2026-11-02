#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôles de non-régression pour la mise à jour café Spinda / Réverie Town /
reprises Lost Wood (novembre 2026).

Ces contrôles sont statiques : ils ne remplacent pas un test du runtime PMDO.
Ils vérifient les empreintes des cartes café corrigées, l'appartenance des
salles à la zone de la ville, la présence des ressources town02 réellement
absentes de game/ et base/, ainsi que les invariants des scripts Lua
(dialogues de reprise Lost Wood, Kangourex sans banque, menus natifs).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "game/Data/Script/destiny"

CAFE_MAPS = {
    "caféspindaaccueil.rsground": "182e0a465947db903fb48fd00d70538c",
    "spindacaféétage1.rsground": "4f5c87686530257bb70ce110e2a050fa",
    "spindacaféétage1salle2.rsground": "5830da67d6329f6e228a23985bccb72d",
}

RESSOURCES = [
    "game/Content/Item/Berry_Aspear.dir",
    "game/Content/Item/Berry_Cheri.dir",
    "game/Content/Item/Berry_Chesto.dir",
    "game/Content/Item/Berry_Pecha.dir",
    "game/Content/Item/Berry_Persim.dir",
    "game/Content/Item/Berry_Rawst.dir",
    "game/Content/Item/MegaStone.dir",
    "game/Content/Item/MegaStoneDelta.dir",
    "game/Content/Particle/Ash_Fall.dir",
    "game/Content/Particle/Emote_Eating.dir",
    "game/Content/Particle/Leaf_Fall.dir",
    "game/Content/Particle/Sakura_Fall.dir",
    "game/Content/Particle/Slugma_Materialize.dir",
    "game/Content/Particle/Slugma_Materialize_Reverse.dir",
    "game/Content/Particle/Snow_Fall.dir",
]

LUA_MODIFIES = [
    SCRIPT / "scriptvars.lua",
    SCRIPT / "zone/lost_wood/init.lua",
    SCRIPT / "ground/cliffdaytest_nuit/init.lua",
    SCRIPT / "ground/reveil_nuit/init.lua",
    SCRIPT / "ground/WaterfallVillageCapital/init.lua",
    SCRIPT / "ground/caféspindaaccueil/init.lua",
    SCRIPT / "ground/spindacaféétage1/init.lua",
    SCRIPT / "ground/spindacaféétage1salle2/init.lua",
]


def lire(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def extraire_fonction(texte: str, nom: str) -> str:
    debut = texte.index(nom)
    fin = texte.index("\nfunction ville.", debut + 1)
    return texte[debut:fin]


def main() -> int:
    # Cartes café : accueil d'origine town02, étage et salle sans les deux
    # fenêtres visibles (voir tools/retirer_fenetres_cafe.py).
    for nom, empreinte in CAFE_MAPS.items():
        carte = ROOT / "game/Data/Ground" / nom
        assert carte.is_file(), f"carte café absente : {nom}"
        assert md5(carte) == empreinte, f"MD5 inattendu pour {nom}"

    # Les trois salles appartiennent à la zone de la ville, dans cet ordre
    # (indices utilisés par les transitions : 2, 3 et 4).
    zone = json.loads(lire(ROOT / "game/Data/Zone/town02_waterfallvillage.json"))
    grounds = zone["Object"]["GroundMaps"]
    assert grounds[2:5] == ["caféspindaaccueil", "spindacaféétage1", "spindacaféétage1salle2"]
    archives = json.loads(lire(ROOT / "game/Data/Zone/archives.json"))["Object"]["GroundMaps"]
    for salle in grounds[2:5]:
        assert salle not in archives
    index = json.loads(lire(ROOT / "game/Data/Zone/index.idx"))
    assert index["Object"]["town02_waterfallvillage"]["Grounds"] == grounds

    # Ressources town02 absentes de game/ et de base/.
    for relatif in RESSOURCES:
        assert (ROOT / relatif).is_file(), f"ressource absente : {relatif}"

    # Syntaxe Lua des fichiers modifiés, si Lupa est disponible.
    try:
        from lupa import LuaRuntime

        charger = LuaRuntime().eval("load")
        for fichier in LUA_MODIFIES:
            assert charger(lire(fichier)) is not None, f"Lua invalide : {fichier}"
    except ImportError:
        print("Lupa absent : analyse Lua ignorée (contrôles textuels seulement).")

    cliff = lire(SCRIPT / "ground/cliffdaytest_nuit/init.lua")
    reveil = lire(SCRIPT / "ground/reveil_nuit/init.lua")
    zone_lost = lire(SCRIPT / "zone/lost_wood/init.lua")
    ville = lire(SCRIPT / "ground/WaterfallVillageCapital/init.lua")
    accueil = lire(SCRIPT / "ground/caféspindaaccueil/init.lua")

    # Lost Wood : aucune relance sans le dialogue de choix, à l'aller (solo)
    # comme au retour (en duo).
    question = "Souhaitez-vous retourner dans Lost Wood ?"
    assert cliff.count(question) == 1 and reveil.count(question) == 1
    assert "LostWoodTrip = 'pause_aller'" in cliff
    assert "LostWoodTrip = 'pause_retour'" in reveil
    assert "LostWoodRetry" in zone_lost and "cause_echec" in zone_lost
    assert "Repartir dans la forêt maintenant ?" not in cliff

    # Pensées du réveil : voix intérieure sur fond noir, jamais de locuteur.
    for pensee in ("Où suis-je ?", "Qui suis-je ?", "J’ai sommeil…"):
        assert pensee in reveil
    assert "PenseesReveilVues = true" in reveil

    # Kangourex : dépôt/retrait d'objets uniquement. La banque est chez
    # Gimmighoul (NewObject_3).
    kangourex = extraire_fonction(ville, "function ville.Kangourex_Action")
    assert "UI:StorageMenu()" in kangourex and "UI:WithdrawMenu()" in kangourex
    assert "BankMenu" not in kangourex and "ShowTeamStorageMenu" not in kangourex
    gimmighoul = extraire_fonction(ville, "function ville.NewObject_3_Action")
    assert "UI:BankMenu()" in gimmighoul

    # Boutiques Kecleon natives (icônes d'objets), stocks persistés et
    # rotation par journée ; services Alakazam et Tinkaton natifs.
    assert "UI:ShopMenu(catalogue)" in ville
    assert "StocksKecleon" in ville and "JourneeVille" in ville
    assert "SkillSelectMenu.runRelearnMenu" in ville and "UI:ForgetMenu" in ville
    assert "UI:AppraiseMenu()" in ville and "UI:SpoilsMenu" in ville
    assert "COMMON.CreateWalkArea" in ville
    assert "JourneeVille = (SV.Destiny.JourneeVille or 0) + 1" in accueil

    # Raccordements du café : porte en ville, sortie sud, escalier, porte de
    # la salle, et circulation par le personnel.
    for marqueur in ("PorteCafeSpinda", "ArriveeVille == 'cafe'"):
        assert marqueur in ville
    assert "PorteSortieCafe" in accueil
    assert "EscalierCafe" in lire(SCRIPT / "ground/spindacaféétage1/init.lua")
    assert "PorteSalleCafe" in lire(SCRIPT / "ground/spindacaféétage1salle2/init.lua")

    # Aucun nom de la référence externe dans les livrables.
    for fichier in LUA_MODIFIES:
        texte = lire(fichier)
        assert "Halcyon" not in texte and "Remixed" not in texte

    print("Contrôles café / Réverie Town / Lost Wood : OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
