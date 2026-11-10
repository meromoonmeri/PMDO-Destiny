#!/usr/bin/env python3
"""Verify integrity of guilde_cliff_* ground maps and GroundMap BlankBG/rand guards."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AMBIANCES = ('jour', 'aube', 'crepuscule', 'nuit')
REQUIRED_FIELDS = (
    'TexSize', 'Name', 'obstacles', 'rand', 'Status', 'Background',
    'BlankBG', 'Layers', 'AssetName', 'EdgeView', 'Decorations', 'Entities',
)


def main() -> None:
    for amb in AMBIANCES:
        stem = f'guilde_cliff_{amb}'
        path = ROOT / 'game/Data/Ground' / f'{stem}.rsground'
        assert path.is_file(), f'Missing {path}'
        doc = json.loads(path.read_text(encoding='utf-8-sig'))
        obj = doc['Object']
        for key in REQUIRED_FIELDS:
            assert key in obj and obj[key] is not None, f'{stem} missing or null {key}'
        assert obj['AssetName'] == stem, f'{stem} AssetName={obj["AssetName"]!r}'
        assert isinstance(obj['BlankBG'], dict), f'{stem} BlankBG not dict'
        assert isinstance(obj['BlankBG'].get('Layers'), list), f'{stem} BlankBG.Layers invalid'
        assert isinstance(obj['BlankBG'].get('Associates'), list), f'{stem} BlankBG.Associates invalid'
        assert obj['rand'].get('$type') == 'RogueElements.ReRandom, RogueElements', f'{stem} rand $type invalid'
        assert len(obj['rand'].get('s', [])) == 4, f'{stem} rand.s invalid'
        for dec in obj.get('Decorations', []):
            for anim in dec.get('Anims', []):
                oa = anim.get('ObjectAnim', {})
                assert oa.get('AnimDir', 0) >= 0, f'{stem} negative AnimDir {oa.get("AnimDir")}'

    for rsground in sorted((ROOT / 'game/Data/Ground').glob('*.rsground')):
        if rsground.stat().st_size > 15 * 1024 * 1024:
            continue
        doc = json.loads(rsground.read_text(encoding='utf-8-sig'))
        obj = doc['Object']
        assert obj.get('BlankBG') is not None, f'{rsground.name} BlankBG is null'
        assert obj.get('rand') is not None, f'{rsground.name} rand is null'

    ground_map_cs = (ROOT / 'engine/RogueEssence/RogueEssence/Ground/Maps/GroundMap.cs').read_text(encoding='utf-8')
    assert 'if (BlankBG == null)' in ground_map_cs, 'GroundMap.cs missing BlankBG null guard'
    assert 'if (rand == null)' in ground_map_cs, 'GroundMap.cs missing rand null guard'

    tile_box_cs = (
        ROOT / 'engine/RogueEssence/RogueEssence.Editor.Avalonia/DataEditor/Editors/RogueEssence/Tiles/TileBoxViewModel.cs'
    ).read_text(encoding='utf-8')
    assert 'if (Tile == null)' in tile_box_cs, 'TileBoxViewModel.cs missing Tile null guard'

    print('TEST GUILDE CLIFF INTEGRITE OK')


if __name__ == '__main__':
    main()
