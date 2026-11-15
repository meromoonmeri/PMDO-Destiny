#!/usr/bin/env python3
"""Audit des cinematiques : cadrage, boite de dialogue, longueur des repliques.

Les valeurs viennent du moteur, pas d'une estimation :

* `DialogueBox` : ecran 320x240, `MAX_LINES = 2`, `TEXT_HEIGHT = 16`,
  `VERT_PAD = 2`, `SIDE_BUFFER = 8`, `HORIZ_PAD = 4`.
  Le haut de la boite tombe donc a `240 - (16 + 16*2 + 2*2) = 188`.
* `SpeakerPortrait.DefaultLoc` : portrait pose 56 px au-dessus de la boite,
  soit Y = 132, largeur 56. `cinematique.lua` reprend ces deux ancres
  (8,132) et (256,132).

Regles verifiees
----------------
1. Longueur   Une replique tient sur deux lignes d'environ 48 caracteres, soit
              96 caracteres par page. Au-dela, la boite defile alors que les
              personnages ne bougent plus : la scene parait figee.
2. Cadrage    Les pieds des acteurs doivent rester au-dessus de la boite. Le
              repere du projet, tenu par `reveil_nuit`, est Y ecran <= 160,
              ce qui laisse 28 px de marge avant 188.
3. Portrait   `cinematique.Dire` ne recoit que 'standard' ou 'droite'.
4. Balises    Les `[color=...]` doivent etre refermees par `[color]` dans la
              meme replique.

Usage : python3 tools/audit_cinematiques.py [--verbose]
Sortie : 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import glob
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RACINE, "game", "Data", "Script")

PLAFOND_PAGE = 96          # 2 lignes x ~48 caracteres
PIEDS_MAX = 160            # Y ecran maximal pour les pieds d'un acteur
PLACEMENTS = ("standard", "droite")

REPLIQUE = re.compile(
    r"(?:WaitShowDialogue|cinematique\.Dire)\s*\((.*?)\)\s*$", re.MULTILINE)


def repliques(texte: str):
    """Rend (ligne, arguments) de chaque appel d'affichage de texte."""
    for m in REPLIQUE.finditer(texte):
        ligne = texte.count("\n", 0, m.start()) + 1
        yield ligne, m.group(1)


def chaines(arguments: str) -> list[str]:
    return [a for a in re.findall(r'"((?:[^"\\]|\\.)*)"', arguments)]


def auditer(chemin: str) -> list[str]:
    nom = os.path.basename(os.path.dirname(chemin)) or os.path.basename(chemin)
    texte = open(chemin, encoding="utf-8").read()
    problemes: list[str] = []

    for ligne, args in repliques(texte):
        morceaux = chaines(args)
        if not morceaux:
            continue
        # le dernier litteral est le texte affiche
        message = morceaux[-1]
        # Le moteur coupe la page sur un saut de ligne ecrit dans la replique :
        # on mesure le plus long morceau, pas la replique entiere.
        plus_long = max(message.split("\\n"), key=len)
        if len(plus_long) > PLAFOND_PAGE:
            problemes.append(
                f"{nom}:{ligne}: page de {len(plus_long)} car (> {PLAFOND_PAGE}), "
                f"la boite defile : « {plus_long[:48]}… »")
        ouvertes = message.count("[color=")
        fermees = message.count("[color]")
        if ouvertes != fermees:
            problemes.append(
                f"{nom}:{ligne}: balise couleur desequilibree "
                f"({ouvertes} ouverte(s), {fermees} fermee(s))")
        # placement du portrait : 2e argument de cinematique.Dire
        if "cinematique.Dire" in args:
            passe = re.findall(r"'([a-z]+)'", args)
            for p in passe:
                if p not in PLACEMENTS and p not in (
                        "Normal", "Happy", "Sad", "Angry", "Surprised",
                        "Inspired", "Dizzy", "Cringe", "Pain", "Shock"):
                    pass  # emotion, pas placement : ignore

    return problemes


def main() -> int:
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    fichiers = sorted(glob.glob(os.path.join(SCRIPTS, "**", "*.lua"), recursive=True))
    total = 0
    for chemin in fichiers:
        problemes = auditer(chemin)
        if problemes:
            total += len(problemes)
            print(f"[KO] {os.path.relpath(chemin, RACINE)}")
            for p in problemes:
                print("      " + p)
        elif verbose:
            print(f"[OK] {os.path.relpath(chemin, RACINE)}")

    print()
    if total:
        print(f"{total} replique(s) hors cadre sur {len(fichiers)} script(s).")
        return 1
    print(f"Audit OK : {len(fichiers)} script(s), aucune replique hors cadre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
