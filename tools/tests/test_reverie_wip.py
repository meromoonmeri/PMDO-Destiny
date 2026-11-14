#!/usr/bin/env python3
"""Vérifications des fichiers intégrés ; ne remplace pas une partie PMDO."""
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
TILES = GAME / 'Content/Tile'
cache = {}


def bank(name):
    if name not in cache:
        path = TILES / f'{name}.tile'
        assert path.is_file(), name
        with path.open('rb') as f:
            size, count = struct.unpack('<ii', f.read(8))
            assert size == 8 and count >= 0
            table = f.read(16 * count)
            assert len(table) == 16 * count
            cache[name] = {(x, y) for x, y, _ in struct.iter_unpack('<iiq', table)}
    return cache[name]


counts = {}
for name in ('dojo_kingambit', 'caféspindaaccueil', 'spindacaféétage1', 'spindacaféétage1salle2'):
    path = GAME / 'Data/Ground' / f'{name}.rsground'
    ground = json.loads(path.read_text(encoding='utf-8-sig'))['Object']
    assert ground['AssetName'] == name and ground['Entities']
    if name == 'dojo_kingambit':
        assert ground['TexSize'] == 1 and len(ground['Layers']) == 9
        npcs = [x for e in ground['Entities'] for x in e['MapChars']]
        assert len(npcs) == 1 and npcs[0]['EntName'] == 'Kingambit'
        assert npcs[0]['Data']['BaseForm']['Species'] == 'kingambit'
    found = 0
    for layer in ground['Layers']:
        for col in layer['Tiles']:
            for tile in col:
                for anim in tile.get('Layers', []):
                    for frame in anim.get('Frames', []):
                        sheet, xy = frame['Sheet'], frame['TexLoc']
                        assert (xy['X'], xy['Y']) in bank(sheet), (name, frame)
                        found += 1
    counts[name] = found
assert counts == {'dojo_kingambit':7339, 'caféspindaaccueil':4514, 'spindacaféétage1':4913, 'spindacaféétage1salle2':5022}, counts

city = (GAME / 'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf-8')
dev = (GAME / 'Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf-8')
assert city == dev
assert 'PorteMaisonEquipe' not in city and 'PorteMaisonArcanine' not in city
assert "titre = 'Auberge'" in city and "interieur = 'reverie_inn'" in city
assert "PorteCafeSpinda', 1056, 1344, 32, 8" in city
assert "interieur = 'dojo_kingambit'" in city
assert len(list(TILES.glob('Reverie_Cafe_*.tile'))) == 10
print('Intérieurs WIP : 21 788 références de tuiles et associations statiques vérifiées.')
