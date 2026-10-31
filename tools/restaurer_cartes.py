#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restaure les 230 cartes ajoutées à la quête `destiny` depuis leurs `.gz`.

Pourquoi ce détour : les `.rsground` de la quête pèsent 3,6 Go à eux seuls, mais
le JSON se compresse ~50 fois (mesuré : 29,2 Mo -> 436 ko sur
`d262_generated_055`). Git ne peut pas héberger les fichiers bruts (limite dure
de 100 Mo par fichier, et 233 Mo pour WaterfallVillageCapital) : on versionne
donc les `.gz` et on les redéploie ici, avec vérification SHA-256.

Les **planches** `.tile` ne sont volontairement pas versionnées : elles ne se
compressent que ~1,5 fois (900 Mo). Elles sont fournies dans l'archive Drive et
vérifiables avec `ressources/PLANCHES/manifest.json`.

Usage :
    python restaurer_cartes.py <racine_quest> [--verifier-seulement]
"""
from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    racine = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    verif = '--verifier-seulement' in sys.argv
    src = racine / 'ressources' / 'CARTES_230'
    cible = racine / 'game' / 'Data' / 'Ground'
    man = json.loads((src / 'manifest.json').read_text())

    ok = manquants = erreurs = 0
    for e in man['cartes']:
        gz = src / f"{e['carte']}.gz"
        dst = cible / e['carte']
        if not gz.exists():
            print(f'  MANQUANT (gz) : {gz.name}')
            manquants += 1
            continue
        if dst.exists() and sha256(dst) == e['sha256']:
            ok += 1
            continue
        if verif:
            print(f'  à restaurer : {e["carte"]}')
            manquants += 1
            continue
        cible.mkdir(parents=True, exist_ok=True)
        with gzip.open(gz, 'rb') as f, open(dst, 'wb') as g:
            shutil.copyfileobj(f, g, 1 << 20)
        if dst.stat().st_size != e['octets'] or sha256(dst) != e['sha256']:
            print(f'  ERREUR SHA-256 : {e["carte"]}')
            erreurs += 1
        else:
            ok += 1

    print(f'cartons restaurées : {ok}/{len(man["cartes"])} '
          f'({man["octets_bruts"] / 1e6:.0f} Mo bruts)')
    if manquants or erreurs:
        print(f'  {manquants} manquantes, {erreurs} corrompues')

    # contrôle des planches
    pm = racine / 'ressources' / 'PLANCHES' / 'manifest.json'
    if pm.exists():
        tiles = json.loads(pm.read_text())
        dossier = racine / 'game' / 'Content' / 'Tile'
        absentes = [t['planche'] for t in tiles['planches'] if not (dossier / t['planche']).exists()]
        print(f'planches présentes : {tiles["total"] - len(absentes)}/{tiles["total"]}')
        if absentes:
            print(f'  {len(absentes)} planches absentes, ex. {absentes[:6]}')
            print('  -> les extraire de l’archive Drive puis relancer ce script.')
    return 1 if (manquants or erreurs) else 0


if __name__ == '__main__':
    raise SystemExit(main())
