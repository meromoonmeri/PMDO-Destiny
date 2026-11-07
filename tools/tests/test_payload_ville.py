#!/usr/bin/env python3
"""Sécurité de la restauration et de la copie compacte de la ville.

Lancez `python tools/tests/test_payload_ville.py`. Les petits exemples créés
ici sont temporaires ; ils ne modifient jamais la carte du projet.
"""
from __future__ import annotations

import gzip
import hashlib
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import compacter_ville as compacter
import unpack_payload as payload


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def attend_refus(fonction):
    try:
        fonction()
    except ValueError:
        return
    raise AssertionError('La modification d’un fichier utilisateur aurait dû être refusée.')


def main():
    # Le compacteur et la carte publiée doivent toujours viser le même payload.
    _, attendu, taille = payload.PAYLOADS['payload/WaterfallVillageCapital.rsground.gz']
    assert compacter.ORIGINAL_SHA256 == attendu and compacter.ORIGINAL_SIZE == taille
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        contenu = b'carte native de test'
        archive = root / 'payload' / 'carte.gz'
        archive.parent.mkdir()
        archive.write_bytes(gzip.compress(contenu))
        payload.ROOT = root
        payload.PAYLOADS = {'payload/carte.gz': ('game/carte.rsground', digest(contenu), len(contenu))}
        cible = root / 'game' / 'carte.rsground'

        # Reconstitution, puis relance idempotente.
        assert payload.main() == 0 and cible.read_bytes() == contenu
        assert payload.main() == 0 and cible.read_bytes() == contenu
        # Ne jamais remplacer une carte éditée, même si elle a la même taille.
        edition = b'X' * len(contenu)
        cible.write_bytes(edition)
        assert payload.main() == 1 and cible.read_bytes() == edition
        # Une archive corrompue ne laisse pas un fichier partiel derrière elle.
        cible.unlink()
        archive.write_bytes(b'pas une archive gzip')
        assert payload.main() == 1 and not cible.exists()

        # La conversion ne remplace que les cellules dont les quatre valeurs
        # sont celles du constructeur : les autres octets restent identiques.
        entree = b'prefixe,' + compacter.EMPTY_TILE + b',autre,' + compacter.EMPTY_TILE + b',fin'
        sortie = entree.replace(compacter.EMPTY_TILE, b'{}')
        compacter.ORIGINAL_SIZE = len(entree)
        compacter.ORIGINAL_SHA256 = digest(entree)
        compacter.COMPACT_SHA256 = digest(sortie)
        compacter.EMPTY_COUNT = 2
        source, destination = root / 'source.rsground', root / 'copie.rsground'
        source.write_bytes(entree)
        assert compacter.compact(source, destination) == 2
        assert source.read_bytes() == entree and destination.read_bytes() == sortie
        assert compacter.compact(source, destination) == 2  # copie déjà compacte
        destination.write_bytes(b'mon edition')
        attend_refus(lambda: compacter.compact(source, destination))
        assert destination.read_bytes() == b'mon edition' and source.read_bytes() == entree
        attend_refus(lambda: compacter.compact(source, source))
        # Éviter aussi l'écrasement par un lien physique vers la source.
        destination.unlink()
        try:
            os.link(source, destination)
        except (OSError, NotImplementedError):  # certains systèmes refusent les hardlinks
            pass
        else:
            attend_refus(lambda: compacter.compact(source, destination))
            assert source.read_bytes() == entree
        destination.unlink(missing_ok=True)
        source.write_bytes(b'automatiquement refuse')
        attend_refus(lambda: compacter.compact(source, destination))
        assert not destination.exists()
    print('OK : payload non destructif et compactage des seules cellules vides.')


if __name__ == '__main__':
    main()
