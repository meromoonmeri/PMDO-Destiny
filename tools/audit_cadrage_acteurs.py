#!/usr/bin/env python3
"""Audit du cadrage : la boite de dialogue ne doit cacher aucun personnage.

Le moteur dessine en 320 x 240 et `MoveCamera(x, y)` vise le **centre** du
cadre. Un personnage pose en `(px, py)` a donc les pieds a l'ecran en

    pieds = py - y + 120

La boite de dialogue commence a 188 (cf. `DialogueBox.DefaultBounds`) et le
repere du projet, tenu par `reveil_nuit`, est 160 : 28 px de marge.

Un personnage dont les pieds tombent **sous 188** est caché par la boite. Il
suffit qu'il soit dans la largeur du cadre (|px - x| <= 152, sprite de 16 px
compris) pour que ce soit visible a l'ecran.

L'outil lit les `GAME:MoveCamera` des scripts, resout les constantes locales
(`ENTREE_Y - 30`, `PLACE_Y + 20`…), charge les personnages de la carte
correspondante (`.rsground`, ou la version compressee de `payload/`) et
signale chaque panoramique qui laisse un personnage derriere la boite.

Un personnage dont les pieds tombent entre 160 et 188 n'est pas caché, mais
n'a plus de marge : `--strict` les liste comme confort à améliorer, sans les
compter comme défauts.

Usage : python3 tools/audit_cadrage_acteurs.py [--verbose] [--strict]
Sortie : 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import gzip
import glob
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RACINE, "game", "Data", "Script", "destiny")
GROUND = os.path.join(RACINE, "game", "Data", "Ground")
PAYLOAD = os.path.join(RACINE, "payload")

DEMI_LARGEUR = 152     # demi-ecran 160, moins la demi-largeur d'un sprite
PIEDS_BOITE = 188      # haut de la boite de dialogue
PIEDS_CONFORT = 160    # repere du projet
HAUTEUR_ECRAN = 240    # bas de l'ecran

MOVE = re.compile(r"GAME:MoveCamera\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,)]+)")


def evaluer(expr: str, constantes: dict) -> float | None:
    """Resout une expression simple : nombre, constante, somme ou difference."""
    expr = expr.strip().strip("()")
    try:
        return float(expr)
    except ValueError:
        pass
    # NAME +/- nombre
    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*([+-])\s*([0-9.]+)", expr)
    if m and m.group(1) in constantes:
        base = constantes[m.group(1)]
        delta = float(m.group(3))
        return base + delta if m.group(2) == "+" else base - delta
    if expr in constantes:
        return constantes[expr]
    return None


def constantes_du_fichier(texte: str) -> dict:
    c = {}
    for m in re.finditer(r"^\s*local\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(-?[0-9.]+)\s*$",
                         texte, re.MULTILINE):
        c[m.group(1)] = float(m.group(2))
    return c


def charger_grounds(dossier: str, noms: set[str]) -> dict[str, list[tuple]]:
    """Rend, pour chaque carte demandee, la liste (nom, x, y) des personnages."""
    resultat: dict[str, list[tuple]] = {}
    for nom in noms:
        brut = None
        chemin = os.path.join(GROUND, nom + ".rsground")
        compresse = os.path.join(PAYLOAD, nom + ".rsground.gz")
        if os.path.exists(chemin):
            brut = open(chemin, "rb").read()
        elif os.path.exists(compresse):
            brut = gzip.decompress(open(compresse, "rb").read())
        if brut is None:
            continue
        try:
            objet = json.loads(brut.decode("utf-8-sig"))["Object"]
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        entites = []

        def parcourir(noeud):
            if isinstance(noeud, dict):
                if "EntName" in noeud and "serializationLoc" in noeud:
                    loc = noeud["serializationLoc"] or {}
                    if loc.get("X") is not None and loc.get("Y") is not None:
                        entites.append((noeud["EntName"], loc["X"], loc["Y"]))
                for valeur in noeud.values():
                    parcourir(valeur)
            elif isinstance(noeud, list):
                for valeur in noeud:
                    parcourir(valeur)

        parcourir(objet)
        resultat[nom] = entites
    return resultat


def cartes_du_script(chemin: str) -> set[str]:
    """La carte porte le nom du dossier du script, ou du fichier de scene."""
    dossier = os.path.basename(os.path.dirname(chemin))
    if dossier == "destiny":
        # module partage : il sert plusieurs cartes
        return set()
    return {dossier}


def main() -> int:
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    strict = "--strict" in sys.argv
    scripts = sorted(glob.glob(os.path.join(SCRIPTS, "**", "*.lua"), recursive=True))

    # premier passage : quelles cartes faut-il charger ?
    a_charger = set()
    plans = []
    for chemin in scripts:
        texte = open(chemin, encoding="utf-8").read()
        if "MoveCamera" not in texte:
            continue
        for carte in cartes_du_script(chemin):
            a_charger.add(carte)
        plans.append((chemin, texte))
    grounds = charger_grounds(GROUND, a_charger)

    problemes = 0
    for chemin, texte in plans:
        cartes = cartes_du_script(chemin)
        if not cartes or not any(c in grounds for c in cartes):
            if verbose:
                print(f"[--] {os.path.relpath(chemin, RACINE)} (carte absente)")
            continue
        entites = [e for c in cartes for e in grounds.get(c, [])]
        constantes = constantes_du_fichier(texte)
        trouves = []
        confort = []
        for m in MOVE.finditer(texte):
            cx = evaluer(m.group(1), constantes)
            cy = evaluer(m.group(2), constantes)
            duree = evaluer(m.group(3), constantes)
            if cx is None or cy is None or duree is None:
                continue
            if duree <= 1:
                continue          # recentrage instantane : rien a cadrer
            ligne = texte.count("\n", 0, m.start()) + 1
            for nom, px, py in entites:
                pieds = py - cy + 120
                # hors ecran, un personnage n'est pas « cache » : le defaut
                # n'existe que s'il est visible et que la boite le recouvre.
                if not abs(px - cx) <= DEMI_LARGEUR:
                    continue
                if strict and PIEDS_CONFORT < pieds < PIEDS_BOITE:
                    confort.append(
                        f"{os.path.relpath(chemin, RACINE)}:{ligne}: "
                        f"'{nom}' a {pieds:.0f} px, sous le repere de "
                        f"{PIEDS_CONFORT} (marge {PIEDS_BOITE - pieds:.0f} px avant la boite)")
                if PIEDS_BOITE <= pieds < HAUTEUR_ECRAN:
                    trouves.append(
                        f"{os.path.relpath(chemin, RACINE)}:{ligne}: "
                        f"panoramique ({cx:.0f}, {cy:.0f}) laisse '{nom}' "
                        f"derriere la boite (pieds a {pieds:.0f}, boite a {PIEDS_BOITE})")
        for c in confort:
            print("  ~ " + c)
        if trouves:
            problemes += len(trouves)
            for t in trouves:
                print("  " + t)
        elif verbose:
            print(f"[OK] {os.path.relpath(chemin, RACINE)}")

    print()
    if problemes:
        print(f"{problemes} personnage(s) masque(s) par la boite de dialogue.")
        return 1
    print("Audit OK : aucun personnage masque par la boite de dialogue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
