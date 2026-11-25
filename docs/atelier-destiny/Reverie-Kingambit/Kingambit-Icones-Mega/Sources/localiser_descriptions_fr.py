#!/usr/bin/env python3
"""Ajoute uniquement Desc.LocalTexts.fr aux 48 objets Méga de Réverie."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ADDON_ITEMS = Path('addons/Mega_Stones_Reverie/Data/Item')
BOM = b'\xef\xbb\xbf'
PAIRS = {'charizard', 'mewtwo'}


def descriptions(table: Path) -> dict[str, str]:
    result = {}
    variants = set()
    for line in table.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        _, key, _, species, name, form, *_ = line.split('|')
        item_id = 'mega_' + key
        assert item_id not in result
        if species in PAIRS:
            pokemon, variant = name.rsplit(' ', 1)
            assert variant == {'1': 'X', '2': 'Y'}[form] and key.endswith('_' + variant.lower())
            variants.add((species, variant))
            text = f'Permet à {pokemon} de prendre sa forme Méga-{name} une fois par étage.'
        elif item_id == 'mega_delta_meteorite':
            assert species == 'rayquaza' and name == 'Rayquaza'
            text = 'Une météorite qui brille de sept couleurs. Permet à Rayquaza de méga-évoluer une fois par étage.'
        else:
            text = f'Une mystérieuse Méga-Gemme. Permet à {name} de méga-évoluer une fois par étage.'
        result[item_id] = text
    assert len(result) == 48 and len(set(result.values())) == 48
    assert variants == {(species, v) for species in PAIRS for v in ('X', 'Y')}
    assert 'mega_delta_meteorite' in result
    return result


def localize(raw: bytes, fr: str) -> bytes:
    source = raw.decode('utf-8-sig')
    before = json.loads(source)
    desc = before['Object']['Desc']
    assert desc['DefaultText'].endswith('once per floor to Mega Evolve.')
    if desc['LocalTexts'].get('fr') == fr:
        return raw
    new = deepcopy(before)
    replacement = new['Object']['Desc']
    replacement['LocalTexts']['fr'] = fr
    match = re.search(r'(?m)^([ \t]*)"Desc"[ \t]*:[ \t]*', source)
    assert match is not None
    start = match.end()
    decoded, end = json.JSONDecoder().raw_decode(source, start)
    assert decoded == desc
    sep = '\r\n' if '\r\n' in source else '\n'
    block = json.dumps(replacement, ensure_ascii=False, indent=2).replace('\n', sep + match[1])
    text = source[:start] + block + source[end:]
    assert json.loads(text) == new
    return (BOM if raw.startswith(BOM) else b'') + text.encode('utf-8')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destiny', type=Path, required=True, help='Racine du dépôt Destiny')
    p.add_argument('--modeles', type=Path, default=HERE / 'Modeles-des-gemmes.tsv')
    p.add_argument('--check', action='store_true', help='Vérifier les fiches, sans écrire')
    a = p.parse_args()
    targets = descriptions(a.modeles)
    items = a.destiny / ADDON_ITEMS
    assert {p.stem for p in items.glob('mega_*.json')} == set(targets), 'Le catalogue du mod a changé.'
    edits = {}
    for name, fr in targets.items():
        file = items / (name + '.json')
        old = file.read_bytes()
        new = localize(old, fr)
        if old != new:
            edits[file] = new
    if a.check and edits:
        p.exit(1, f'{len(edits)} descriptions françaises manquantes ou différentes.\n')
    for file, content in edits.items():
        file.write_bytes(content)
    print(f'48 descriptions françaises vérifiées ; {len(edits)} fiches modifiées. Les autres langues et les effets sont intacts.')


if __name__ == '__main__':
    main()
