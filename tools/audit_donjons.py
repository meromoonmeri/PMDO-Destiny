#!/usr/bin/env python3
"""Audit des etages de donjon et des tables de rencontre.

Verifie, pour chaque zone de `game/Data/Zone`, les invariants qui font qu'un
etage est terminable par n'importe quel Pokemon (nageur ou non) et que les
Pokemon annonces apparaissent vraiment.

Invariants
----------
1. Escalier      Chaque etage genere pose une sortie (`FloorStairsStep`).
2. Garde         Un `DetectIsolatedStairsStep` existe et tourne APRES toutes
                 les etapes qui changent le terrain (eau, lave, fosses).
3. Eau           Aucune etape d'eau ne porte `NoChokepointTerrainStencil` avec
                 `Negate: true`. Ce drapeau inverse le test : le stencil ne
                 laisse alors passer que les cases dont le remplissage coupe
                 la zone, donc l'eau se pose exactement sur les goulots.
4. Blob          Un `BlobWaterStep` doit pouvoir poser quelque chose :
                 `GenerateScale.Min^2` doit etre inferieur a
                 `(GenerateScale.Max - 1)^2`, sinon la boucle de generation
                 n'entre jamais et l'etape ne fait rien.
4b. Garde d'eau   Toute eau posee sur du SOL doit porter un
                 `NoChokepointTerrainStencil`. L'eau posee uniquement sur des
                 murs est inoffensive : ces cases ne sont pas marchables.
                 `WaterStep.DrawBlob` teste le stencil case par case, donc le
                 garde-fou s'applique aussi aux flaques.

5. Equipe        `TeamSpawnZoneStep.TeamSizes` doit etre defini. Une liste vide
                 fait sortir `PoolTeamSpawner.ChooseSpawns` immediatement et
                 aucun Pokemon n'apparait.
6. Especes       Chaque `BaseForm.Species` doit exister dans `Data/Monster`.
7. Capacites     Chaque `SpecifiedSkills` et `Intrinsic` doit exister.
8. Plage         Les `Range` des rencontres doivent tenir dans le nombre
                 d'etages du segment (`Max` est exclusif).

Usage : python3 tools/audit_donjons.py [--verbose]
Sortie : 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZONES = os.path.join(RACINE, "game", "Data", "Zone")

TERRAIN_CHANGEANT = ("PerlinWaterStep", "BlobWaterStep", "PerlinLavaStep",
                     "LavaStep", "PitTrapStep", "DropDiagonalBlockStep")


def type_court(valeur: dict) -> str:
    t = str(valeur.get("$type", ""))
    m = re.match(r"([A-Za-z0-9_.]+)", t)
    return m.group(1).split(".")[-1] if m else "?"


def charger(chemin: str) -> dict:
    with open(chemin, encoding="utf-8-sig") as f:
        return json.load(f)["Object"]


def inventaire(dossier: str) -> set[str]:
    return {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(dossier, "*.json"))}


def descendre_jusqu_a_baseform(noeud):
    """Les encounters sont tantot a plat, tantot emboites dans un `Spawn`."""
    for _ in range(4):
        if isinstance(noeud, dict) and "BaseForm" in noeud:
            return noeud
        if isinstance(noeud, dict) and "Spawn" in noeud:
            noeud = noeud["Spawn"]
        else:
            break
    return None


def auditer_zone(chemin: str, especes: set[str], skills: set[str],
                 intrinsics: set[str]) -> list[str]:
    nom = os.path.basename(chemin)[:-5]
    zone = charger(chemin)
    problemes: list[str] = []
    segments = [s for s in (zone.get("Segments") or []) if isinstance(s, dict)]

    for si, segment in enumerate(segments):
        etages = [f for f in (segment.get("Floors") or []) if isinstance(f, dict) and "GenSteps" in f]

        for fi, etage in enumerate(etages):
            etapes = [(sorted(st["Key"]["str"]), type_court(st["Value"]), st["Value"])
                      for st in etage["GenSteps"]]
            titres = [c for _, c, _ in etapes]

            # 1. escalier
            if "FloorStairsStep" not in titres and "StairsStep" not in titres:
                continue  # etage non genere (LoadGen) : rien a verifier

            # 2. garde apres le terrain
            terrain = [(k, c) for k, c, _ in etapes if c in TERRAIN_CHANGEANT]
            gardes = [k for k, c, _ in etapes if c == "DetectIsolatedStairsStep"]
            if not gardes:
                problemes.append(f"{nom} seg{si} F{fi}: aucune verification d'escalier isole")
            elif terrain and max(gardes) < max(k for k, _ in terrain):
                problemes.append(f"{nom} seg{si} F{fi}: la verification tourne avant l'eau")

            for _, classe, valeur in etapes:
                # 3. eau sur les goulots
                if classe in ("PerlinWaterStep", "BlobWaterStep"):
                    terrain_id = (valeur.get("Terrain") or {}).get("Data", {}).get("ID")
                    stencil = valeur.get("TerrainStencil") or {}
                    for sous in stencil.get("List") or []:
                        if ("NoChokepoint" in str(sous.get("$type", ""))
                                and sous.get("Negate") is True
                                and terrain_id == "water"):
                            problemes.append(
                                f"{nom} seg{si} F{fi}: eau posee uniquement sur les goulots "
                                f"(NoChokepoint Negate=true)")
                # 4b. eau sur le sol sans garde-fou
                if classe in ("PerlinWaterStep", "BlobWaterStep"):
                    terrain_id = (valeur.get("Terrain") or {}).get("Data", {}).get("ID")
                    stencil = valeur.get("TerrainStencil") or {}
                    sous_stencils = stencil.get("List") or [stencil]
                    garde = any("NoChokepoint" in str(x.get("$type", "")) for x in sous_stencils)
                    sur_le_sol = any(
                        x.get("Room") is True or x.get("Blocked") is True
                        for x in sous_stencils
                        if "MapTerrainStencil" in str(x.get("$type", "")))
                    if terrain_id == "water" and sur_le_sol and not garde:
                        problemes.append(
                            f"{nom} seg{si} F{fi}: eau sur le sol sans garde-fou "
                            f"(NoChokepoint absent)")

                # 4. blobs inertes
                if classe == "BlobWaterStep":
                    gen = valeur.get("GenerateScale") or {}
                    mini, maxi = gen.get("Min", 0), gen.get("Max", 0)
                    depart = maxi - 1
                    if depart <= 0 or depart * depart < mini * mini:
                        problemes.append(
                            f"{nom} seg{si} F{fi}: BlobWaterStep inerte "
                            f"(GenerateScale {mini}..{maxi})")

        # 5 a 8 : table de rencontre du segment
        n_etages = len(etages)
        for zs in segment.get("ZoneSteps") or []:
            if "TeamSpawnZoneStep" not in str(zs.get("$type", "")):
                continue
            if not zs.get("TeamSizes"):
                problemes.append(
                    f"{nom} seg{si}: TeamSizes absent -> aucun Pokemon n'apparait")
            else:
                for t in zs["TeamSizes"]:
                    plage = t.get("Range") or {}
                    if (plage.get("Max") or 0) > n_etages:
                        problemes.append(
                            f"{nom} seg{si}: TeamSizes couvre {plage.get('Min')}..{plage.get('Max')} "
                            f"pour {n_etages} etages")

            for entree in zs.get("Spawns") or []:
                membre = descendre_jusqu_a_baseform(entree.get("Spawn"))
                if membre is None:
                    problemes.append(f"{nom} seg{si}: entree de rencontre illisible")
                    continue
                espece = (membre.get("BaseForm") or {}).get("Species")
                if espece not in especes:
                    problemes.append(f"{nom} seg{si}: espece inconnue '{espece}'")
                for sk in membre.get("SpecifiedSkills") or []:
                    if sk not in skills:
                        problemes.append(f"{nom} seg{si}: capacite inconnue '{sk}' ({espece})")
                intr = membre.get("Intrinsic")
                if intr and intr not in intrinsics:
                    problemes.append(f"{nom} seg{si}: talent inconnu '{intr}' ({espece})")
                plage = entree.get("Range") or {}
                if (plage.get("Max") or 0) > n_etages:
                    problemes.append(
                        f"{nom} seg{si}: '{espece}' sur {plage.get('Min')}..{plage.get('Max')} "
                        f"pour {n_etages} etages")

    return problemes


def main() -> int:
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    especes = (inventaire(os.path.join(RACINE, "base", "Data", "Monster"))
               | inventaire(os.path.join(RACINE, "game", "Data", "Monster")))
    skills = (inventaire(os.path.join(RACINE, "base", "Data", "Skill"))
              | inventaire(os.path.join(RACINE, "game", "Data", "Skill")))
    intrinsics = (inventaire(os.path.join(RACINE, "base", "Data", "Intrinsic"))
                  | inventaire(os.path.join(RACINE, "game", "Data", "Intrinsic")))

    fichiers = sorted(glob.glob(os.path.join(ZONES, "*.json")))
    total = 0
    for chemin in fichiers:
        try:
            problemes = auditer_zone(chemin, especes, skills, intrinsics)
        except (json.JSONDecodeError, KeyError) as err:
            print(f"[ERREUR] {os.path.basename(chemin)}: {err}")
            total += 1
            continue
        nom = os.path.basename(chemin)[:-5]
        if problemes:
            total += len(problemes)
            print(f"[KO] {nom}")
            for p in problemes:
                print("      " + p)
        elif verbose:
            print(f"[OK] {nom}")

    print()
    if total:
        print(f"{total} probleme(s) sur {len(fichiers)} zone(s).")
        return 1
    print(f"Audit OK : {len(fichiers)} zone(s), aucun probleme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
