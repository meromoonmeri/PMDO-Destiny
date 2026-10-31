#!/usr/bin/env python3
"""Copie de jeu moins gourmande de la ville, sans modifier la carte source.

Les objets AutoTile entièrement vides sont sérialisés sous la forme {} : le
constructeur PMDO 0.8.12 leur redonne exactement leurs quatre valeurs par
défaut. Toutes les autres données, dimensions, couches et références restent
inchangées. L'entrée doit être le fichier natif vérifié, pas une carte éditée.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

ORIGINAL_SIZE = 233727831
ORIGINAL_SHA256 = 'afc5081f7348b2afed306953bf5e66a358e442cb00f93fa139ec239cf94c98ee'
COMPACT_SHA256 = '2d755a510cb2fb923cc7acdb7803d4b9a6a10d2908dcba13a0114466d69187e9'
EMPTY_TILE = b'{\n"AutoTileset": "",\n"Associates": [],\n"Layers": [],\n"NeighborCode": -1\n}'
EMPTY_COUNT = 2645785


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact(source: Path, destination: Path) -> int:
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve() or (destination.exists() and os.path.samefile(source, destination)):
        raise ValueError('La copie de jeu doit être distincte de la carte source.')
    if destination.exists():
        if not destination.is_file():
            raise ValueError('La destination existe mais n’est pas un fichier.')
        h = hashlib.sha256()
        with destination.open('rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        if h.hexdigest() not in (ORIGINAL_SHA256, COMPACT_SHA256):
            raise ValueError('La destination contient une autre carte ; aucun écrasement.')
    original = source.read_bytes()
    if len(original) != ORIGINAL_SIZE or sha256(original) != ORIGINAL_SHA256:
        raise ValueError('Carte source différente de la version native vérifiée ; aucune copie produite.')
    count = original.count(EMPTY_TILE)
    if count != EMPTY_COUNT:
        raise ValueError('Nombre inattendu de cellules vides ; aucune copie produite.')
    result = original.replace(EMPTY_TILE, b'{}')
    if sha256(result) != COMPACT_SHA256:
        raise ValueError('Empreinte de la copie compacte inattendue.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(result)
    print(f'Carte de jeu : {len(original)} → {len(result)} octets ; {count} cellules par défaut.')
    return count


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit('Usage : python tools/compacter_ville.py CARTE_NATIVE COPIE_DE_JEU')
    compact(Path(sys.argv[1]), Path(sys.argv[2]))


if __name__ == '__main__':
    main()
