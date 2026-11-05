#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrôles statiques des services du café Spinda (tranche novembre 2026).

Deux services sont vérifiés :

* le bar à jus de Spinda (`destiny.cafe_spinda`) : ingrédients issus du
  catalogue `COMMON.JUICE.BOOSTS` de la base, menus natifs du moteur
  (`JuiceShopMenu`, `InventorySelectMenu`, `TeamSelectMenu`, `LevelUpMenu`) ;
* l'atelier de recyclage d'Okéoké et Qulbutoké : cote de reprise, trouvailles
  du jour et persistance dans `SV.Destiny`.

Ces contrôles ne remplacent pas un test du runtime PMDO : ils garantissent
que chaque identifiant d'objet cité existe réellement dans les données, que
les scripts se chargent (syntaxe Lua via Lupa quand il est disponible) et que
les points d'entrée sont bien branchés sur les cartes du café.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "game/Data/Script/destiny"
MODULE = SCRIPT / "cafe_spinda.lua"
ACCUEIL = SCRIPT / "ground/caféspindaaccueil/init.lua"
ETAGE = SCRIPT / "ground/spindacaféétage1/init.lua"
VARS = SCRIPT / "scriptvars.lua"
BASE_JUS = ROOT / "base/Data/Script/origin/common_shop.lua"

INTERDITS = ("Halcyon", "Remixed")


def lire(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def bloc(texte: str, debut: str, fin: str) -> str:
    start = texte.index(debut)
    stop = texte.index(fin, start)
    return texte[start:stop]


def ids_catalogue_jus() -> list[str]:
    """Identifiants d'ingrédients du catalogue COMMON.JUICE.BOOSTS."""
    texte = lire(BASE_JUS)
    zone = bloc(texte, "COMMON.JUICE.BOOSTS", "COMMON.JUICE.SPECIALTIES")
    return re.findall(r"^\s{2}([a-z0-9_]+)\s*=\s*\{", zone, re.M)


def ids_table_lua(texte: str, nom: str, fin: str) -> list[str]:
    zone = bloc(texte, nom, fin)
    return re.findall(r"^\s*([a-z0-9_]+)\s*=", zone, re.M)


def existe_objet(item_id: str) -> bool:
    return (ROOT / f"game/Data/Item/{item_id}.json").is_file() or (
        ROOT / f"base/Data/Item/{item_id}.json"
    ).is_file()


def prix_catalogue(item_id: str) -> int:
    for chemin in (
        ROOT / f"game/Data/Item/{item_id}.json",
        ROOT / f"base/Data/Item/{item_id}.json",
    ):
        if chemin.is_file():
            doc = json.loads(chemin.read_text(encoding="utf-8-sig"))
            return int(doc["Object"].get("Price") or 0)
    raise AssertionError(f"objet inconnu : {item_id}")


def simulation_lua() -> str:
    """Exécute le module avec des doublures du moteur et vérifie sa logique."""
    from lupa import LuaRuntime

    lua = LuaRuntime(unpack_returned_tuples=True)
    texte_module = lire(MODULE)
    # Le catalogue d'ingrédients de la base est réutilisé tel quel.
    catalogue = bloc(lire(BASE_JUS), "COMMON.JUICE.BOOSTS", "COMMON.JUICE.SPECIALTIES")

    lua.execute(
        """
        package.preload['origin.common'] = function() end
        package.preload['origin.menu.juice.JuiceShopMenu'] = function() end
        package.preload['origin.menu.InventorySelectMenu'] = function() end
        package.preload['origin.menu.team.TeamSelectMenu'] = function() end

        COMMON = { JUICE = {} }
        """
        + catalogue
        + """
        PMDC = { Data = { MonsterFormData = { MAX_STAT_BOOST = 256 } }, Dungeon = {} }
        PMDC.Dungeon.PreTypeEvent = nil
        SV = { Destiny = {} }
        UI = {}
        SOUND = {}
        GAME = {}
        RogueEssence = { Data = { Stat = { HP = 1, Attack = 2, Defense = 3,
            MAtk = 4, MDef = 5, Speed = 6 } }, Menu = {}, Text = {} }

        -- Doublures d'objets : prix du catalogue PMDO et interdiction de dépôt.
        local fiches = {
          berry_oran = { prix = 50, interdit = false, nom = 'Baie Oran' },
          food_apple = { prix = 10, interdit = false, nom = 'Pomme' },
          gummi_red = { prix = 80, interdit = false, nom = 'Gomme Rouge' },
          tresor = { prix = 300, interdit = true, nom = 'Trophée' },
          inconnu = { prix = 300, interdit = false, nom = 'Objet' },
        }
        _DATA = { Save = {} }
        function _DATA:GetItem(id)
          local fiche = fiches[id]
          if fiche == nil then return nil end
          return { Price = fiche.prix, CannotDrop = fiche.interdit,
                   Name = { ToLocal = function() return fiche.nom end } }
        end
        function _DATA:GetMonster(_) error('doublure : pas de fiche monstre') end

        local sac = { { ID = 'berry_oran' }, { ID = 'food_apple' }, { ID = 'gummi_red' } }
        _DATA.Save.ActiveTeam = {
          GetInv = function(self, i) return sac[i + 1] end,
          GetInvCount = function(self) return #sac end,
        }
        """
    )

    lua.execute("cafe = (function(...) " + texte_module + " end)()")

    verifications = {
        # Un dépôt d'une baie vaut la moitié de sa cote (80 -> 40).
        ("cafe.valeur_de_reprise({ ID = 'berry_oran' })", 40),
        # Objet hors table : moitié du prix du catalogue PMDO (300 -> 150).
        ("cafe.valeur_de_reprise({ ID = 'inconnu' })", 150),
        # Objet non déposable : aucune valeur.
        ("cafe.valeur_de_reprise({ ID = 'tresor' })", 0),
        # Objet inconnu des données : aucune valeur, pas d'erreur.
        ("cafe.valeur_de_reprise({ ID = 'nexiste_pas' })", 0),
        ("cafe.valeur_de_reprise(nil)", 0),
        # Deux baies : 40 + 40.
        ("(function() local p = { { IsEquipped = false, Slot = 0 } }"
         " return cafe.valeur_de_reprise(cafe.objet_du_slot(p[1])) end)()", 40),
        # Nom du jus : deux baies donnent un jus double, quatre un grand.
        ("cafe.nom_du_jus({ { IsEquipped = false, Slot = 0 }, { IsEquipped = false, Slot = 0 } })",
         "Jus de baies double"),
        ("cafe.nom_du_jus({})", "Verre vide"),
        # Pomme (EXP 100) + baie Oran (PV 1) : effets additifs.
        ("cafe.total_boost({ { IsEquipped = false, Slot = 0 }, { IsEquipped = false, Slot = 1 } },"
         " { BaseForm = { Species = 'x', Form = 0 } }).EXP", 100),
        ("cafe.total_boost({ { IsEquipped = false, Slot = 0 }, { IsEquipped = false, Slot = 1 } },"
         " { BaseForm = { Species = 'x', Form = 0 } }).HP", 1),
    }
    for expression, attendu in verifications:
        obtenu = lua.eval(expression)
        assert obtenu == attendu, f"{expression} -> {obtenu!r} au lieu de {attendu!r}"

    # Les trois herbes de la base (Mentale, Puissance, Blanche) annulent tous
    # les gains : chaque statistique tombe à son plancher.
    lua.execute(
        """
        local ancien = _DATA.Save.ActiveTeam.GetInv
        _DATA.Save.ActiveTeam.GetInv = function(self, i)
          local sac = { { ID = 'herb_mental' }, { ID = 'herb_power' }, { ID = 'herb_white' } }
          return sac[i + 1]
        end
        local total = cafe.total_boost(
          { { IsEquipped = false, Slot = 0 }, { IsEquipped = false, Slot = 1 },
            { IsEquipped = false, Slot = 2 } },
          { BaseForm = { Species = 'x', Form = 0 } })
        _DATA.Save.ActiveTeam.GetInv = ancien
        resultat_herbes = total.HP + total.Atk + total.Def + total.SpAtk + total.SpDef + total.Speed
        """
    )
    assert lua.eval("resultat_herbes") == -1536, "les trois herbes doivent annuler tous les gains"

    # Les trouvailles du jour tournent avec la journée de ville.
    lua.execute("SV.Destiny.JourneeVille = 0")
    premier = lua.eval("cafe.trouvailles_du_jour()[1].index")
    lua.execute("SV.Destiny.JourneeVille = 1")
    second = lua.eval("cafe.trouvailles_du_jour()[1].index")
    assert premier != second, "la rotation des trouvailles ne suit pas JourneeVille"
    return f"{len(verifications)} vérifications, rotation des trouvailles effective"


def main() -> int:
    assert MODULE.is_file(), "module destiny/cafe_spinda.lua absent"
    texte_module = lire(MODULE)

    # --- 1. Syntaxe Lua (si Lupa est disponible) --------------------------
    try:
        from lupa import LuaRuntime

        charger = LuaRuntime().eval("load")
        for fichier in (MODULE, VARS, ACCUEIL, ETAGE):
            assert charger(lire(fichier)) is not None, f"Lua invalide : {fichier}"
    except ImportError:
        print("Lupa absent : analyse Lua ignorée (contrôles textuels seulement).")

    # --- 2. Bar à jus -----------------------------------------------------
    # Le service s'appuie sur les menus natifs, jamais sur un menu improvisé.
    for attendu in (
        "require 'origin.menu.juice.JuiceShopMenu'",
        "require 'origin.menu.InventorySelectMenu'",
        "require 'origin.menu.team.TeamSelectMenu'",
        "JuiceShopMenu.run(",
        "TeamSelectMenu.runPartyMenu()",
        "RogueEssence.Menu.LevelUpMenu(",
        "PMDC.Data.MonsterFormData.MAX_STAT_BOOST",
        "SOUND:PlayBattleSE('DUN_Drink')",
    ):
        assert attendu in texte_module, f"attendu dans le module : {attendu}"

    ingredients = ids_catalogue_jus()
    assert len(ingredients) >= 80, f"catalogue d'ingrédients suspect : {len(ingredients)}"
    manquants = [i for i in ingredients if not existe_objet(i)]
    assert not manquants, f"ingrédients sans données d'objet : {manquants}"

    # Le module utilise exactement le catalogue de la base (aucune copie qui
    # pourrait diverger) et non une liste maison.
    assert "local INGREDIENTS = COMMON.JUICE.BOOSTS" in texte_module

    # --- 3. Atelier de recyclage -----------------------------------------
    bloc_valeurs = bloc(texte_module, "local VALEURS = {", "local ASSORTIMENTS")
    valeurs = dict(
        (item_id, int(cote))
        for item_id, cote in re.findall(r"([a-z_][a-z0-9_]*) = (\d+)", bloc_valeurs)
    )
    assert len(valeurs) >= 50, f"table VALEURS incomplète : {len(valeurs)} entrées"
    for item_id, cote in valeurs.items():
        assert existe_objet(item_id), f"cote de reprise sur un objet absent : {item_id}"
        assert cote > 0, f"cote de reprise nulle pour {item_id}"

    assortiments = re.findall(r"\{ \{ index = '[a-z0-9_]+'.*?\} \}", texte_module)
    assert len(assortiments) >= 4, f"assortiments de trouvailles trop peu nombreux : {len(assortiments)}"
    index_assortiments = re.findall(r"index = '([a-z0-9_]+)', prix = (\d+)", texte_module)
    assert index_assortiments, "aucune trouvaille déclarée"
    for item_id, prix in index_assortiments:
        assert existe_objet(item_id), f"trouvaille absente des données : {item_id}"
        assert 1 <= int(prix) <= 2000, f"prix de trouvaille invraisemblable : {item_id} = {prix}"

    # Chaque assortiment garde une entrée bon marché : une seule baie
    # déposée (cote 80, donc 40 de reprise) suffit à repartir avec quelque
    # chose.
    for numero, ligne in enumerate(assortiments, start=1):
        prix = [int(p) for p in re.findall(r"prix = (\d+)", ligne)]
        assert len(prix) == 3, f"assortiment {numero} : {len(prix)} trouvailles au lieu de 3"
        assert min(prix) <= 40, f"assortiment {numero} sans trouvaille abordable"

    # Le dépôt est borné, la consommation passe par les fonctions du moteur.
    assert "cafe.MAX_DEPOT = 4" in texte_module
    assert "InventorySelectMenu.run(" in texte_module
    assert "GAME:TakePlayerBagItem(slot.Slot, true)" in texte_module
    assert "GAME:GivePlayerItem(trouvee.index, 1)" in texte_module
    assert "SOUND:PlayBattleSE('DUN_Money')" in texte_module

    # --- 4. Persistance ---------------------------------------------------
    for cle in (
        "JusDecouvert",
        "JusServis",
        "TourneeOfferte",
        "AtelierDecouvert",
        "RecyclageDons",
    ):
        assert cle in texte_module, f"clé SV.Destiny.{cle} non utilisée par le module"
        assert cle in lire(VARS), f"clé SV.Destiny.{cle} absente de scriptvars.lua"

    # --- 5. Branchements sur les cartes du café ---------------------------
    accueil = lire(ACCUEIL)
    etage = lire(ETAGE)
    assert "local cafe = require 'destiny.cafe_spinda'" in accueil
    assert "local cafe = require 'destiny.cafe_spinda'" in etage
    assert "cafe.servir_le_jus(personnage)" in accueil
    assert "'Commander un jus de Spinda'" in accueil
    # L'atelier est ouvert : plus aucune promesse d'ouverture future.
    assert "ouvrira quand toutes les caisses" not in accueil
    assert "Encore quelques étagères à monter" not in etage
    assert etage.count("cafe.ouvrir_atelier(") == 2, "les deux jumeaux doivent tenir le comptoir"

    # La sieste reste le seul moyen d'avancer d'une journée de ville.
    assert "SV.Destiny.JourneeVille = (SV.Destiny.JourneeVille or 0) + 1" in accueil
    # Les deux services suivent la journée de ville (rotation des trouvailles).
    assert "SV.Destiny.JourneeVille" in texte_module

    # --- 6. Propreté ------------------------------------------------------
    for fichier in (MODULE, ACCUEIL, ETAGE, VARS):
        texte = lire(fichier)
        for interdit in INTERDITS:
            assert interdit not in texte, f"{interdit} trouvé dans {fichier}"

    # --- 7. Exécution simulée des fonctions pures (Lupa) ------------------
    # Les appels au moteur sont remplacés par des doublures : on vérifie la
    # logique des noms de jus, des effets d'ingrédients et de la cote de
    # reprise, sans lancer le jeu.
    try:
        from lupa import LuaRuntime

        resultat = simulation_lua()
        print(f"Simulation Lua : {resultat}")
    except ImportError:
        print("Lupa absent : simulation Lua ignorée.")

    print(
        "Contrôles café Spinda (jus + recyclage) : OK — "
        f"{len(ingredients)} ingrédients, {len(assortiments)} assortiments de trouvailles, "
        f"{len(valeurs)} cotes de reprise."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
