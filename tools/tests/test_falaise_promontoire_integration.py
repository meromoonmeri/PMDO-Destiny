#!/usr/bin/env python3
"""Vérifie le raccordement entre reverie_centre (chemin vers Forgelina) et falaise_promontoire."""
from __future__ import annotations

from collections import deque
import gzip
import json
from pathlib import Path
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
AMBIANCES = ('jour', 'aube', 'crepuscule', 'nuit')


def main() -> None:
    # 1. Zone dédiée débloquée sans modifier les 27 cartes de town02_waterfallvillage
    z_prom = json.loads((ROOT / 'game/Data/Zone/falaise_promontoire.json').read_text(encoding='utf-8-sig'))['Object']
    z_idx = json.loads((ROOT / 'game/Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']
    assert z_prom['Released'] is True
    assert z_idx['falaise_promontoire']['Released'] is True
    expected_maps = [f'falaise_promontoire_{a}' for a in AMBIANCES]
    assert z_prom['GroundMaps'] == expected_maps and z_idx['falaise_promontoire']['Grounds'] == expected_maps
    assert len(z_idx['town02_waterfallvillage']['Grounds']) == 27

    # 2. Intégrité des 4 cartes falaise_promontoire, boucle mer 12 frames et accessibilité bord ouest
    for amb in AMBIANCES:
        stem = f'falaise_promontoire_{amb}'
        rs = ROOT / 'game/Data/Ground' / f'{stem}.rsground'
        doc = json.loads(rs.read_text(encoding='utf-8-sig'))['Object']
        assert doc['AssetName'] == stem and doc['EdgeView'] == 1 and doc['Decorations'] == []
        assert doc.get('BlankBG') is not None
        sea_count = 0
        for layer in doc['Layers']:
            is_sea = layer.get('Name') == '00_Mer_Sharpedo_Animes'
            for col in layer['Tiles']:
                for cell in col:
                    for tl in cell.get('Layers', []):
                        if tl.get('Frames'):
                            assert isinstance(tl.get('FrameLength'), int) and tl['FrameLength'] > 0, (stem, tl)
                            if is_sea:
                                assert len(tl['Frames']) == 12, (stem, len(tl['Frames']))
                                sea_count += 1
        assert sea_count > 1000, (stem, sea_count)
        for bl in doc['Background']['Layers']:
            anim = bl['BG']['BGAnim']
            if 'ETOILES' in anim['AnimIndex']:
                assert anim['FrameTime'] == 8, (stem, anim)
        obs = [[c['Tags'] for c in col] for col in doc['obstacles']]
        assert len(obs) == 80 and len(obs[0]) == 64
        # Entrée (24,292) et bord retour ouest (0..7, 272..312) libres
        for tx in range(0, 6):
            for ty in range(280 // 8, 320 // 8):
                assert obs[tx][ty] == 0, (stem, tx, ty)

    # 3. reverie_centre : chemin 16x16 de la place (800,1160) vers Forgelina (1104,1064) puis sortie est (1576,1152)
    raw = gzip.decompress((ROOT / 'payload/reverie_centre.rsground.gz').read_bytes())
    oa = raw.index(b'"obstacles":') + len(b'"obstacles":')
    ob = raw.index(b',"rand":', oa)
    centre_obs = [[c['Tags'] for c in col] for col in json.loads(raw[oa:ob])]
    def free(px: int, py: int) -> bool:
        return px >= 0 and py >= 0 and px + 16 <= 1600 and py + 16 <= 4000 and all(
            centre_obs[tx][ty] == 0
            for tx in range(px // 8, (px + 15) // 8 + 1)
            for ty in range(py // 8, (py + 15) // 8 + 1)
        )
    assert free(800, 1160) and free(1104, 1064) and free(1536, 1152) and free(1560, 1152) and free(1576, 1152)
    q = deque([(800, 1160)])
    seen = {(800, 1160)}
    targets = {(1104, 1064), (1576, 1152)}
    while q and not targets.issubset(seen):
        px, py = q.popleft()
        for nx, ny in ((px + 4, py), (px - 4, py), (px, py + 4), (px, py - 4)):
            if (nx, ny) not in seen and free(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))
    assert targets.issubset(seen), f'Chemin manquant: {targets - seen}'

    tile_layer_cs = (ROOT / 'engine/RogueEssence/RogueEssence/Dungeon/Tiles/TileLayer.cs').read_text(encoding='utf-8')
    assert 'FrameLength <= 0' in tile_layer_cs, 'TileLayer.cs missing FrameLength <= 0 guard'

    # 4. Simulation Lua aller-retour et synchronisation 4 ambiances
    run(ROOT / 'tools/tests/test_falaise_promontoire_integration.lua', ROOT)
    print('TEST FALAISE PROMONTOIRE INTEGRATION OK')


if __name__ == '__main__':
    main()
