#!/usr/bin/env python3
"""Vérifie la structure complète et les scripts du donjon Grotte Verdoyante (9 étages)."""
from __future__ import annotations

import io
import json
import struct
from collections import deque
from pathlib import Path
from PIL import Image

from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
BASE = ROOT / 'base'


def load_tile_headers(sheet_dir: Path, sheet: str) -> dict[tuple[int, int], bytes]:
    raw = (sheet_dir / f'{sheet}.tile').read_bytes()
    ts, cnt = struct.unpack_from('<ii', raw, 0)
    out = {}
    for i in range(cnt):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + 16 * i)
        ln = struct.unpack_from('<q', raw, off)[0]
        out[(tx, ty)] = raw[off + 8:off + 8 + ln]
    return out


def check_ground_tiles(rsground_path: Path) -> dict:
    doc = json.loads(rsground_path.read_text(encoding='utf-8-sig'))
    obj = doc['Object']
    assert obj['AssetName'] == rsground_path.stem
    assert obj['Released'] is True
    assert obj['EdgeView'] == 1
    tile_cache: dict[str, dict[tuple[int, int], bytes]] = {}
    missing = 0
    for lyr in obj['Layers']:
        for col in lyr['Tiles']:
            for cell in col:
                for sub in cell.get('Layers', []):
                    frs = sub.get('Frames', [])
                    if frs and (not isinstance(sub.get('FrameLength'), int) or sub['FrameLength'] <= 0):
                        raise AssertionError(f'FrameLength invalide dans {rsground_path.name}')
                    for fr in frs:
                        sh = fr.get('Sheet')
                        if not sh:
                            continue
                        if sh not in tile_cache:
                            d = GAME / 'Content/Tile' if (GAME / 'Content/Tile' / f'{sh}.tile').is_file() else BASE / 'Content/Tile'
                            assert (d / f'{sh}.tile').is_file(), f'Planche manquante: {sh}'
                            tile_cache[sh] = load_tile_headers(d, sh)
                        loc = (fr['TexLoc']['X'], fr['TexLoc']['Y'])
                        if loc not in tile_cache[sh]:
                            missing += 1
    assert missing == 0, f'{rsground_path.name}: {missing} TexLoc manquants'
    return obj


def main() -> None:
    # 1. Cartes au sol ewc3 & fgv1 + continuité animation cascade L12/L13/L14
    ewc3 = check_ground_tiles(GAME / 'Data/Ground/ewc3_entree_waterfall_cave.rsground')
    fgv1 = check_ground_tiles(GAME / 'Data/Ground/fgv1_fin_grotte_vasques.rsground')
    markers_ewc3 = {m['EntName']: m for m in ewc3['Entities'][0]['Markers']}
    objs_ewc3 = {o['EntName']: o for o in ewc3['Entities'][0]['GroundObjects']}
    assert markers_ewc3['entrance']['Collider']['Y'] == 544
    assert 'SeuilDonjon' in objs_ewc3 and 'SortieRetourReverie' in objs_ewc3
    assert 'Statue_Kangourex' in objs_ewc3
    statue_ewc3 = objs_ewc3['Statue_Kangourex']
    assert statue_ewc3['ObjectAnim']['AnimIndex'] == 'Statue_Kangourex'
    assert statue_ewc3['Passable'] is False and statue_ewc3['triggerType'] == 1
    assert statue_ewc3['Collider'] == {'X': 428, 'Y': 236, 'Width': 24, 'Height': 12}
    # Accès libre devant (432, 248) et à gauche (412, 240) de la statue pour un acteur 16x16
    for ax, ay in ((432, 248), (412, 240)):
        assert all(
            ewc3['obstacles'][cx][cy]['Tags'] == 0
            for cx in range(ax // 8, (ax + 15) // 8 + 1)
            for cy in range(ay // 8, (ay + 15) // 8 + 1)
        ), (ax, ay)
    assert ewc3['Layers'][12]['Visible'] is True and ewc3['Layers'][17]['Visible'] is True
    assert ewc3['Layers'][13]['Visible'] is False and ewc3['Layers'][14]['Visible'] is False and ewc3['Layers'][18]['Visible'] is False

    tile_imgs: dict[str, dict[tuple[int, int], Image.Image]] = {}
    def render_layer(layer_idx: int, fr_idx: int) -> bytes:
        canvas = Image.new('RGBA', (96 * 8, 72 * 8), (0, 0, 0, 0))
        for x, col in enumerate(ewc3['Layers'][layer_idx]['Tiles']):
            for y, cell in enumerate(col):
                for sub in cell.get('Layers', []):
                    frs = sub.get('Frames', [])
                    if not frs:
                        continue
                    fr = frs[fr_idx % len(frs)]
                    sh = fr['Sheet']
                    if sh not in tile_imgs:
                        d = GAME / 'Content/Tile' if (GAME / 'Content/Tile' / f'{sh}.tile').is_file() else BASE / 'Content/Tile'
                        tile_imgs[sh] = {k: Image.open(io.BytesIO(v)).convert('RGBA') for k, v in load_tile_headers(d, sh).items()}
                    canvas.alpha_composite(tile_imgs[sh][(fr['TexLoc']['X'], fr['TexLoc']['Y'])], (x * 8, y * 8))
        return canvas.tobytes()

    assert render_layer(12, 0) == render_layer(13, 0), 'Désaccord pixel L12[0] != L13[0]'
    assert render_layer(13, 23) == render_layer(14, 11), 'Désaccord pixel L13[23] != L14[11]'

    # 2. Planche 24 px et carte de combat 9F end_grotte_verdoyante.rsmap (20x15 = 480x360)
    raw_t24 = (GAME / 'Content/Tile/FGV1_VASQUES_BASE_24.tile').read_bytes()
    ts, cnt24 = struct.unpack_from('<ii', raw_t24, 0)
    assert ts == 24 and cnt24 > 700
    t24_locs = {(tx, ty) for tx, ty, _ in (struct.unpack_from('<iiq', raw_t24, 8 + 16 * i) for i in range(cnt24))}

    rsmap = json.loads((GAME / 'Data/Map/end_grotte_verdoyante.rsmap').read_text(encoding='utf-8-sig'))['Object']
    assert rsmap['AssetName'] == 'end_grotte_verdoyante' and rsmap['NoRescue'] is True
    assert rsmap['Music'] == 'Boss Battle 2.ogg'
    assert rsmap['EntryPoints'] == [{'Loc': {'X': 10, 'Y': 12}, 'Dir': 4}]
    for rx in range(20):
        for ry in range(15):
            for sub in rsmap['Layers'][0]['Tiles'][rx][ry]['Layers']:
                for fr in sub['Frames']:
                    assert fr['Sheet'] == 'FGV1_VASQUES_BASE_24'
                    assert (fr['TexLoc']['X'], fr['TexLoc']['Y']) in t24_locs

    floors = {(x, y) for x in range(20) for y in range(15) if rsmap['Tiles'][x][y]['Data']['ID'] == 'floor'}
    q = deque([(10, 12)])
    seen = {(10, 12)}
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (cx + dx, cy + dy) in floors and (cx + dx, cy + dy) not in seen:
                seen.add((cx + dx, cy + dy))
                q.append((cx + dx, cy + dy))
    assert floors == seen and len(floors) == 36
    for st in [(10, 12), (9, 12), (11, 12), (10, 8), (8, 9), (12, 9), (10, 7)]:
        assert st in floors, st

    starts = [e['Value']['$type'] for e in rsmap['MapEffect']['OnMapStarts']]
    assert any('BattlePositionEvent' in s for s in starts)
    assert any('BeginBattleEvent' in s for s in starts)
    enemies = [(p['BaseForm']['Species'], p['Level']) for p in rsmap['MapTeams'][0]['Players']]
    assert enemies == [('garchomp', 14)], enemies
    for p in rsmap['MapTeams'][0]['Players']:
        assert (BASE / 'Data/Monster' / f"{p['BaseForm']['Species']}.json").is_file()
        for sk in p['Skills']:
            assert (BASE / 'Data/Skill' / f"{sk['Element']['SkillNum']}.json").is_file()
        for intr in p['Intrinsics']:
            assert (BASE / 'Data/Intrinsic' / f"{intr['Element']['ID']}.json").is_file()

    # 3. Zone grotte_verdoyante.json (9 étages) & index.idx
    zone = json.loads((GAME / 'Data/Zone/grotte_verdoyante.json').read_text(encoding='utf-8-sig'))['Object']
    assert zone['Released'] is True and len(zone['Segments']) == 2
    assert len(zone['Segments'][0]['Floors']) == 8
    assert len(zone['Segments'][1]['Floors']) == 1
    assert zone['GroundMaps'] == ['ewc3_entree_waterfall_cave', 'fgv1_fin_grotte_vasques']
    for i, fl in enumerate(zone['Segments'][0]['Floors']):
        tex_steps = [s['Value'] for s in fl['GenSteps'] if 'MapDictTextureStep' in s['Value']['$type']]
        assert len(tex_steps) == 1
        assert tex_steps[0]['TextureMap']['floor'].startswith('deep_limestone_cavern')
        for at_id in tex_steps[0]['TextureMap'].values():
            assert (BASE / 'Data/AutoTile' / f'{at_id}.json').is_file(), at_id

    zidx = json.loads((GAME / 'Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']['grotte_verdoyante']
    assert zidx['Released'] is True and zidx['CountedFloors'] == 9
    assert zidx['Maps'] == [[0, 1, 2, 3, 4, 5, 6, 7], [0]]
    assert zidx['Grounds'] == ['ewc3_entree_waterfall_cave', 'fgv1_fin_grotte_vasques']

    # 4. Vérifications de logique Lua (cascade, zone, boss, post-sauvetage, café, Nilo en ville)
    run(ROOT / 'tools/tests/test_grotte_verdoyante.lua', ROOT)
    print('PASS Grotte Verdoyante : 9 étages, cascade ewc3, arène 9F, scripts Lua et retours vérifiés.')


if __name__ == '__main__':
    main()
