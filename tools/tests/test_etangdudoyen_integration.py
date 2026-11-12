#!/usr/bin/env python3
"""Vérifie l'intégration complète de etangdudoyen (4 ambiances, rivière/cailloux corrigés, préparation de nage)."""
from __future__ import annotations

from collections import deque
import io
import json
from pathlib import Path
import struct
from PIL import Image
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
AMBIANCES = (
    ('jour', 'Jour'),
    ('aube', 'Aube'),
    ('crepuscule', 'Crepuscule'),
    ('nuit', 'Nuit'),
)


def _decode_tiles(path: Path) -> dict[tuple[int, int], Image.Image]:
    raw = path.read_bytes()
    _, cnt = struct.unpack_from('<ii', raw, 0)
    out: dict[tuple[int, int], Image.Image] = {}
    cache: dict[int, Image.Image] = {}
    for i in range(cnt):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + i * 16)
        if off not in cache:
            (plen,) = struct.unpack_from('<q', raw, off)
            cache[off] = Image.open(io.BytesIO(raw[off + 8 : off + 8 + plen])).convert('RGBA')
        out[(tx, ty)] = cache[off]
    return out


def _decode_dir(path: Path) -> tuple[int, int, int, Image.Image]:
    raw = path.read_bytes()
    (plen,) = struct.unpack_from('<q', raw, 0)
    png_bytes = raw[8 : 8 + plen]
    tw, th, _, frames = struct.unpack_from('<iiii', raw, 8 + plen)
    img = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
    return tw, th, frames, img


def main() -> None:
    z_rev = json.loads((ROOT / 'game/Data/Zone/reverie.json').read_text(encoding='utf-8-sig'))['Object']
    z_idx = json.loads((ROOT / 'game/Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']['reverie']
    assert z_rev['GroundMaps'][10] == 'zrv2_zone_reveil_nuit'
    assert z_rev['GroundMaps'][11] == 'crossroadreverietown2'
    expected_pond = [f'etangdudoyen_{a}' for a, _ in AMBIANCES]
    assert z_rev['GroundMaps'][12:16] == expected_pond
    assert z_idx['Grounds'][12:16] == expected_pond

    for amb, suffix in AMBIANCES:
        stem = f'etangdudoyen_{amb}'
        rs = ROOT / 'game/Data/Ground' / f'{stem}.rsground'
        assert rs.is_file() and rs.stat().st_size <= 15 * 1024 * 1024, (stem, rs.stat().st_size)
        doc = json.loads(rs.read_text(encoding='utf-8-sig'))['Object']
        assert doc['AssetName'] == stem and doc['EdgeView'] == 1
        assert doc['Music'] == 'Luminous Spring.ogg'
        assert doc.get('BlankBG') is not None
        assert len(doc.get('rand', {}).get('s', [])) == 4
        assert len(doc['obstacles']) == 60 and len(doc['obstacles'][0]) == 45

        markers = {m['EntName']: m for m in doc['Entities'][0]['Markers']}
        assert 'entrance' in markers and 'grand_doyen' in markers
        gd = markers['grand_doyen']
        assert gd['Collider']['X'] == 180 and gd['Collider']['Y'] == 170 and gd['Direction'] == 6

        decos = {d['Name']: d for d in doc['Decorations']}
        assert 'Nage_Grand_Doyen' in decos
        deco = decos['Nage_Grand_Doyen']
        assert deco['Visible'] is False and deco['Layer'] == 0
        assert len(deco['Anims']) == 1
        anim = deco['Anims'][0]
        assert anim['MapLoc']['X'] == 172 and anim['MapLoc']['Y'] == 174
        oa = anim['ObjectAnim']
        assert oa['AnimIndex'] == f'Etang_Nage_Ondes_{suffix}' and oa['FrameTime'] == 10 and oa['AnimDir'] >= 0

        dir_p = ROOT / 'game/Content/Object' / f'Etang_Nage_Ondes_{suffix}.dir'
        assert dir_p.is_file()
        tw, th, frames, dir_img = _decode_dir(dir_p)
        assert (tw, th, frames) == (32, 16, 4) and dir_img.size == (128, 16)

        tile_p = ROOT / 'game/Content/Tile' / f'Destiny_Etang_Doyen_{suffix}.tile'
        assert tile_p.is_file()
        tiles = _decode_tiles(tile_p)
        assert len(tiles) == 4229

        for layer in doc['Layers']:
            for col in layer['Tiles']:
                for cell in col:
                    for tl in cell.get('Layers', []):
                        if tl.get('Frames'):
                            assert isinstance(tl.get('FrameLength'), int) and tl['FrameLength'] > 0
                            assert (len(tl['Frames']), tl['FrameLength']) in {(1, 1), (3, 10), (4, 10), (8, 5)}, tl

        if amb == 'jour':
            obs = [[c['Tags'] for c in col] for col in doc['obstacles']]
            def free16(px: int, py: int) -> bool:
                return 0 <= px and 0 <= py and px + 16 <= 480 and py + 16 <= 360 and all(
                    obs[tx][ty] == 0
                    for tx in range(px // 8, (px + 15) // 8 + 1)
                    for ty in range(py // 8, (py + 15) // 8 + 1)
                )
            assert not free16(180, 170), 'grand_doyen (180,170) doit être placé sur l eau'
            ent_x, ent_y = markers['entrance']['Collider']['X'], markers['entrance']['Collider']['Y']
            assert free16(ent_x, ent_y)
            q = deque([(ent_x, ent_y)])
            seen = {(ent_x, ent_y)}
            while q:
                px, py = q.popleft()
                for nx, ny in ((px + 4, py), (px - 4, py), (px, py + 4), (px, py - 4)):
                    if (nx, ny) not in seen and free16(nx, ny):
                        seen.add((nx, ny))
                        q.append((nx, ny))
            assert any(y >= 340 for _, y in seen)
            assert any(224 <= x <= 256 and 236 <= y <= 264 for x, y in seen)

            comp = Image.new('RGBA', (480, 360), (0, 0, 0, 255))
            for layer in doc['Layers']:
                for tx in range(60):
                    for ty in range(45):
                        for tl in layer['Tiles'][tx][ty].get('Layers', []):
                            fr = tl['Frames'][0]
                            img = tiles[(fr['TexLoc']['X'], fr['TexLoc']['Y'])]
                            comp.alpha_composite(img, (tx * 8, ty * 8))
            px = comp.load()
            for x in range(216, 264):
                for y in range(304, 356):
                    r, g, b, _ = px[x, y]
                    assert not (abs(r - g) <= 10 and abs(g - b) <= 10 and r < 180), f'Gravier gris détecté à ({x},{y})={(r,g,b)}'
            brown_pts = 0
            for x in range(348, 362):
                for y in range(202, 214):
                    r, g, b, _ = px[x, y]
                    if r > b + 20 and g < 150:
                        brown_pts += 1
            assert brown_pts == 0, f'Pointe marron résiduelle à droite: {brown_pts} px'

    run(ROOT / 'tools/tests/test_etangdudoyen_integration.lua', ROOT)
    print('PASS test_etangdudoyen_integration (4 ambiances + swim prep + pixel checks + Lua)')


if __name__ == '__main__':
    main()
