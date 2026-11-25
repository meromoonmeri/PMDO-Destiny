#!/usr/bin/env python3
"""Contrôle les objets PMDO réels, puis les transactions des deux comptoirs."""
import json
from pathlib import Path
import re

from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]


def main():
    script = ROOT / 'game/Data/Script/destiny/boutiques_kecleon.lua'
    noms = set(re.findall(r"\{'([a-z_]+)',\s*\d+\}", script.read_text(encoding='utf-8')))
    assert {'food_apple', 'berry_oran', 'orb_escape'} <= noms
    assert all(any(n.startswith(c) for n in noms) for c in ('tm_', 'orb_', 'wand_', 'ammo_', 'held_'))
    for nom in noms:
        fichier = ROOT / 'game/Data/Item' / f'{nom}.json'
        if not fichier.exists():
            fichier = ROOT / 'base/Data/Item' / fichier.name
        data = json.loads(fichier.read_text(encoding='utf-8-sig'))['Object']
        assert data['Released'] and data['Price'] > 0, nom
        if nom.startswith('wand_'):
            assert data['MaxStack'] >= 4, nom
    run(Path(__file__).with_suffix('.lua'), ROOT)
    print(f'{len(noms)} références natives disponibles ; catalogue et transactions vérifiés.')


if __name__ == '__main__':
    main()
