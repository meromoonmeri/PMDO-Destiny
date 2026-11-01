#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrait une entrée du journal docs/MISE_A_JOUR.md (notes de release GitHub).

Usage :
  python3 tools/release_notes.py            # dernière entrée (la plus récente)
  python3 tools/release_notes.py --tag v0.3.5-dev-quiz
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / 'docs' / 'MISE_A_JOUR.md'


def entrees(texte):
    """Retourne [(tag, corps)] dans l'ordre du journal (plus récent d'abord)."""
    decoupes = re.split(r'^## ', texte, flags=re.M)[1:]
    resultats = []
    for bloc in decoupes:
        titre, _, corps = bloc.partition('\n')
        tag = re.match(r'\S*\s*(v[\w.\-]+)', titre.strip())
        corps = re.sub(r'\n---\s*$', '', corps.strip())
        resultats.append((tag.group(1) if tag else titre.strip(), '## ' + bloc.split('\n---')[0].strip()))
    return resultats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', help='Version exacte à extraire (sinon la dernière).')
    args = parser.parse_args()
    journal = JOURNAL.read_text(encoding='utf-8')
    liste = entrees(journal)
    if not liste:
        raise SystemExit('Aucune entrée trouvée dans docs/MISE_A_JOUR.md.')
    if args.tag:
        for tag, corps in liste:
            if tag == args.tag:
                print(corps)
                return
        raise SystemExit(f'Entrée introuvable : {args.tag}')
    print(liste[0][1])


if __name__ == '__main__':
    sys.exit(main())
