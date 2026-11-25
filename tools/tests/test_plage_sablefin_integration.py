#!/usr/bin/env python3
"""Vérifie Plage Sablefin (4 ambiances), Passage Aquatique (10F + fond) et la liaison crossroadreverietown2."""
from __future__ import annotations

import json
from pathlib import Path
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
AMBIANCES = ('jour', 'aube', 'crepuscule', 'nuit')


def main() -> None:
    z_pa = json.loads((ROOT / 'game/Data/Zone/passage_aquatique.json').read_text(encoding='utf-8-sig'))['Object']
    z_idx = json.loads((ROOT / 'game/Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']['passage_aquatique']
    expected_grounds = [f'plage_sablefin_{a}' for a in AMBIANCES] + ['passage_aquatique_fond']
    assert z_pa['GroundMaps'] == expected_grounds and z_idx['Grounds'] == expected_grounds
    assert z_pa['Released'] is True and z_idx['Released'] is True
    assert z_idx['SortOrder'] == 33
    assert len(z_pa['Segments']) == 1 and len(z_pa['Segments'][0]['Floors']) == 10

    for stem in expected_grounds:
        rs = ROOT / 'game/Data/Ground' / f'{stem}.rsground'
        assert rs.is_file() and rs.stat().st_size <= 15 * 1024 * 1024, (stem, rs.stat().st_size)
        doc = json.loads(rs.read_text(encoding='utf-8-sig'))['Object']
        assert doc['AssetName'] == stem and doc.get('BlankBG') is not None
        assert len(doc.get('rand', {}).get('s', [])) == 4
        if stem.startswith('plage_sablefin_'):
            suffix = stem.split('_')[-1].capitalize()
            assert (ROOT / 'game/Content/Tile' / f'Destiny_Plage_Sablefin_{suffix}.tile').is_file()
            markers = {m['EntName'] for m in doc['Entities'][0]['Markers']}
            assert {'entrance', 'retour_grotte'}.issubset(markers), (stem, markers)

    cr = json.loads((ROOT / 'game/Data/Ground/crossroadreverietown2.rsground').read_text(encoding='utf-8-sig'))['Object']
    cr_markers = {m['EntName']: m for m in cr['Entities'][0]['Markers']}
    assert 'entree_plage' in cr_markers
    ep = cr_markers['entree_plage']['Collider']
    assert ep['X'] == 488 and ep['Y'] == 912

    run(ROOT / 'tools/tests/test_plage_sablefin_integration.lua', ROOT)
    print('PASS test_plage_sablefin_integration (4 ambiances + 10F dungeon + secret cove + Lua)')


if __name__ == '__main__':
    main()
