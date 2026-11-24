#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôles de non-régression pour la mise à jour café Spinda / Réverie Town /
reprises Bois Perdus (novembre 2026).

Ces contrôles sont statiques : ils ne remplacent pas un test du runtime PMDO.
Ils vérifient les seuils et les trajets sur la grille du café, l'appartenance
des salles à la zone de la ville, les ressources spécifiques à town02, ainsi
que les invariants des scripts Lua
(dialogues de reprise Bois Perdus, Kangourex sans banque, menus natifs).
"""

from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "game/Data/Script/destiny"

CAFE_MAPS = ("caféspindaaccueil", "spindacaféétage1", "spindacaféétage1salle2")
# Les points d'arrivée après transition peuvent être posés par Lua plutôt
# que par un marqueur. Les autres entrées sont lues dans les cartes.
ARRIVEES_CAFE = {
    "caféspindaaccueil": ("NewObject_17", (288, 152)),
    "spindacaféétage1": ("NewObject_3", (528, 216)),
    "spindacaféétage1salle2": ((32, 216),),
}
SEUILS_CAFE = {
    "caféspindaaccueil": ("PorteSortieCafe", "EscalierNordCafe"),
    "spindacaféétage1": ("EscalierCafe", "PassageSalleCafe"),
    "spindacaféétage1salle2": ("PorteSalleCafe",),
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
    return path.read_text(encoding="utf-8-sig")


def rectangle_contact(script: str, nom: str) -> tuple[int, int, int, int]:
    # Deux déclarations dans le mod : affectation EntName puis Rect, ou
    # appel au helper contact(map, nom, x, y, l, h).
    debut = (rf"(?:porte\.EntName = '{nom}'\s+porte\.Collider = RogueElements\.Rect\("
             rf"|contact\(map, '{nom}',\s*)")
    match = re.search(debut + r"(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", script)
    assert match, f"capteur non trouvé : {nom}"
    return tuple(map(int, match.groups()))


def verifier_trajets_cafe() -> None:
    pas, taille = 8, 16  # maille de collision et boîte du joueur
    for nom in CAFE_MAPS:
        carte = json.loads(lire(ROOT / "game/Data/Ground" / f"{nom}.rsground"))["Object"]
        assert carte["$type"] == "RogueEssence.Ground.GroundMap, RogueEssence", nom
        grille = carte["obstacles"]
        largeur, hauteur = len(grille) * pas, len(grille[0]) * pas
        marqueurs = {m['EntName']: (m['Collider']['X'], m['Collider']['Y'])
                     for e in carte['Entities'] for m in e['Markers']}
        script = lire(SCRIPT / "ground" / nom / "init.lua")
        seuils = {s: rectangle_contact(script, s) for s in SEUILS_CAFE[nom]}
        for x, y, w, h in seuils.values():
            assert 0 <= x < x + w <= largeur and 0 <= y < y + h <= hauteur, (nom, x, y, w, h)

        def libre(x: int, y: int) -> bool:
            return (0 <= x <= largeur - taille and 0 <= y <= hauteur - taille
                    and all(grille[a][b]['Tags'] == 0
                            for a in range(x // pas, (x + taille - 1) // pas + 1)
                            for b in range(y // pas, (y + taille - 1) // pas + 1)))

        for depart in ARRIVEES_CAFE[nom]:
            x0, y0 = marqueurs[depart] if isinstance(depart, str) else depart
            assert libre(x0, y0), f"{nom} : arrivée ({x0}, {y0}) bloquée"
            # Alignement à la grille à au plus une cellule du point d'arrivée.
            x0, y0 = x0 // pas * pas, y0 // pas * pas
            vus = {(x, y) for x in (x0, x0 + pas) for y in (y0, y0 + pas) if libre(x, y)}
            file = deque(vus)
            restants = set(seuils)
            while file and restants:
                x, y = file.popleft()
                for seuil in tuple(restants):
                    a, b, w, h = seuils[seuil]
                    # Atteindre la zone de contact sans supposer que le joueur
                    # peut traverser le capteur (les portes peuvent être solides).
                    horizontal = x < a + w and x + taille > a
                    vertical = y < b + h and y + taille > b
                    if (horizontal and y <= b + h and y + taille >= b
                            or vertical and x <= a + w and x + taille >= a):
                        restants.remove(seuil)
                for dx, dy in ((pas, 0), (-pas, 0), (0, pas), (0, -pas)):
                    voisin = (x + dx, y + dy)
                    if voisin not in vus and libre(*voisin):
                        vus.add(voisin)
                        file.append(voisin)
            assert not restants, f"{nom}, entrée {depart} : seuil(s) inaccessible(s) {sorted(restants)}"


def extraire_fonction(texte: str, nom: str) -> str:
    debut = texte.index(nom)
    fin = texte.index("\nfunction ville.", debut + 1)
    return texte[debut:fin]


def main() -> int:
    # Pas d'empreinte globale (elle change avec le décor) : protéger les
    # raccordements et les déplacements, sans restaurer une ancienne carte.
    verifier_trajets_cafe()

    # Les trois salles appartiennent à la zone de la ville, dans cet ordre
    # (indices utilisés par les transitions : 2, 3 et 4), et à elle seule.
    zones = ROOT / "game/Data/Zone"
    zone = json.loads(lire(zones / "town02_waterfallvillage.json"))
    grounds = zone["Object"]["GroundMaps"]
    assert grounds[2:5] == list(CAFE_MAPS) and all(grounds.count(s) == 1 for s in CAFE_MAPS)
    index = json.loads(lire(zones / "index.idx"))["Object"]
    assert index["town02_waterfallvillage"]["Grounds"] == grounds
    for fichier in zones.glob("*.json"):
        if fichier.stem != "town02_waterfallvillage":
            autres = json.loads(lire(fichier))["Object"].get("GroundMaps", [])
            assert not set(CAFE_MAPS).intersection(autres), fichier
    for id_zone, entree in index.items():
        if id_zone != "town02_waterfallvillage" and not id_zone.startswith('$'):
            assert not set(CAFE_MAPS).intersection(entree.get("Grounds", [])), id_zone

    # Ressources nécessaires à town02 dans le mod.
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

    # Bois Perdus : aucune relance sans le dialogue de choix, à l'aller (solo)
    # comme au retour (en duo).
    question = "Souhaitez-vous retourner dans les Bois Perdus ?"
    assert cliff.count(question) == 1 and reveil.count(question) == 1
    assert "LostWoodTrip = 'pause_aller'" in cliff
    assert "LostWoodTrip = 'pause_retour'" in reveil
    assert "LostWoodRetry" in zone_lost and "cause_echec" in zone_lost
    assert "Repartir dans la forêt maintenant ?" not in cliff

    # Pensées du réveil : voix intérieure sur fond noir, jamais de locuteur.
    for pensee in ("Où suis-je ?", "Tout est flou… Je ne me souviens de rien.",
                   "Sauf d’une chose.", "Mon prénom…"):
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

    print("Contrôles café / Réverie Town / Bois Perdus : OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
