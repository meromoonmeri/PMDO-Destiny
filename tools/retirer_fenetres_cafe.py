#!/usr/bin/env python3
"""Retire les fenêtres nord des deux maps supérieures du café Spinda.

Les maps de référence sont celles de town02-main_BACKUP.  Le correctif ne
modifie que le calque 0 : chaque bloc de fenêtre 4×4 pointe vers le bloc de
mur voisin déjà présent dans la même planche.  Aucune collision, entité ou
décoration n'est touchée.  La sérialisation PMDO d'origine (BOM, CRLF,
JSON indenté à zéro) est reproduite octet pour octet hors des 32 X visés.

Usage :
  python3 tools/retirer_fenetres_cafe.py --check
  python3 tools/retirer_fenetres_cafe.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUND = ROOT / "game/Data/Ground"

# nom de map -> (MD5 source Drive, MD5 corrigé, [(x destination, x source), ...])
# Les blocs font 4 cases de large et couvrent y=9..12.
PATCHS = {
    "spindacaféétage1": (
        "32412da5458bb914b66d5289c72c0791",
        "4f5c87686530257bb70ce110e2a050fa",
        [(26, 30), (45, 41)],
    ),
    "spindacaféétage1salle2": (
        "3d737ef6a16d23927da2338efb7450d5",
        "5830da67d6329f6e228a23985bccb72d",
        [(24, 28), (46, 42)],
    ),
}
Y_DEPART = 9
TAILLE_BLOC = 4


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def serialiser(doc: dict) -> bytes:
    texte = json.dumps(doc, ensure_ascii=False, indent=0, separators=(",", ": "))
    return b"\xef\xbb\xbf" + texte.replace("\n", "\r\n").encode("utf-8")


def corriger(doc: dict, blocs: list[tuple[int, int]]) -> int:
    tiles = doc["Object"]["Layers"][0]["Tiles"]
    changements = 0
    for x_dest, x_source in blocs:
        delta = x_source - x_dest
        for x in range(x_dest, x_dest + TAILLE_BLOC):
            for y in range(Y_DEPART, Y_DEPART + TAILLE_BLOC):
                for calque in tiles[x][y].get("Layers", []):
                    for frame in calque.get("Frames", []):
                        frame["TexLoc"]["X"] += delta
                        changements += 1
    return changements


def traiter(nom: str, source_md5: str, attendu_md5: str,
            blocs: list[tuple[int, int]], check: bool) -> None:
    chemin = GROUND / f"{nom}.rsground"
    brut = chemin.read_bytes()
    actuel = md5(brut)
    if actuel == attendu_md5:
        print(f"OK déjà corrigé : {nom} ({actuel})")
        return
    if actuel != source_md5:
        raise SystemExit(
            f"{nom} : MD5 inattendu {actuel}; source Drive {source_md5} "
            f"ou version corrigée {attendu_md5} attendue. Aucun fichier modifié."
        )
    doc = json.loads(brut.decode("utf-8-sig"))
    if serialiser(doc) != brut:
        raise SystemExit(f"{nom} : la resérialisation ne reproduit pas l'original.")
    changements = corriger(doc, blocs)
    sortie = serialiser(doc)
    if changements != 32 or md5(sortie) != attendu_md5:
        raise SystemExit(
            f"{nom} : résultat inattendu ({changements} TexLoc, MD5 {md5(sortie)})."
        )
    if check:
        print(f"À corriger : {nom} ({changements} TexLoc -> {attendu_md5})")
    else:
        chemin.write_bytes(sortie)
        print(f"Corrigé : {nom} ({changements} TexLoc -> {attendu_md5})")


def main() -> int:
    check = "--check" in sys.argv[1:]
    for nom, (source, attendu, blocs) in PATCHS.items():
        traiter(nom, source, attendu, blocs, check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
