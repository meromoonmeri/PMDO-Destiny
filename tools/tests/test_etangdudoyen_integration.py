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
        assert len(doc['obstacles']) == 96 and len(doc['obstacles'][0]) == 72

        markers = {m['EntName']: m for m in doc['Entities'][0]['Markers']}
        assert 'entrance' in markers and 'centre_pierre' in markers and 'grand_doyen' in markers
        gd = markers['grand_doyen']
        assert gd['Collider']['X'] == 248 and gd['Collider']['Y'] == 272 and gd['Direction'] == 6

        decos = {d['Name']: d for d in doc['Decorations']}
        assert 'Nage_Grand_Doyen' in decos
        deco = decos['Nage_Grand_Doyen']
        assert deco['Visible'] is False and deco['Layer'] == 0
        assert len(deco['Anims']) == 1
        anim = deco['Anims'][0]
        assert anim['MapLoc']['X'] == 240 and anim['MapLoc']['Y'] == 276
        oa = anim['ObjectAnim']
        assert oa['AnimIndex'] == f'Etang_Nage_Ondes_{suffix}' and oa['FrameTime'] == 10 and oa['AnimDir'] >= 0

        dir_p = ROOT / 'game/Content/Object' / f'Etang_Nage_Ondes_{suffix}.dir'
        assert dir_p.is_file()
        tw, th, frames, dir_img = _decode_dir(dir_p)
        assert (tw, th, frames) == (32, 16, 4) and dir_img.size == (128, 16)

        tile_p = ROOT / 'game/Content/Tile' / f'Destiny_Etang_Doyen_{suffix}.tile'
        assert tile_p.is_file()
        tiles = _decode_tiles(tile_p)
        assert len(tiles) == 3872

        for layer in doc['Layers']:
            for col in layer['Tiles']:
                for cell in col:
                    for tl in cell.get('Layers', []):
                        if tl.get('Frames'):
                            assert isinstance(tl.get('FrameLength'), int) and tl['FrameLength'] > 0
                            assert (len(tl['Frames']), tl['FrameLength']) in {(1, 1), (3, 10), (4, 10), (8, 5)}, tl
                            for fr in tl['Frames']:
                                if fr['Sheet']:
                                    assert fr['Sheet'] == f'Destiny_Etang_Doyen_{suffix}'
                                    assert (fr['TexLoc']['X'], fr['TexLoc']['Y']) in tiles

        if amb == 'jour':
            obs = [[c['Tags'] for c in col] for col in doc['obstacles']]
            def free16(px: int, py: int) -> bool:
                return 0 <= px and 0 <= py and px + 16 <= 768 and py + 16 <= 576 and all(
                    obs[tx][ty] == 0
                    for tx in range(px // 8, (px + 15) // 8 + 1)
                    for ty in range(py // 8, (py + 15) // 8 + 1)
                )
            assert not free16(248, 272), 'grand_doyen (248,272) doit être placé sur l eau'
            ent_x, ent_y = markers['entrance']['Collider']['X'], markers['entrance']['Collider']['Y']
            plat_x, plat_y = markers['centre_pierre']['Collider']['X'], markers['centre_pierre']['Collider']['Y']
            assert free16(ent_x, ent_y)
            assert free16(plat_x, plat_y)
            q = deque([(ent_x, ent_y)])
            seen = {(ent_x, ent_y)}
            while q:
                px, py = q.popleft()
                for nx, ny in ((px + 4, py), (px - 4, py), (px, py + 4), (px, py - 4)):
                    if (nx, ny) not in seen and free16(nx, ny):
                        seen.add((nx, ny))
                        q.append((nx, ny))
            assert any(y >= 544 for _, y in seen)
            assert (plat_x, plat_y) in seen

            comp = Image.new('RGBA', (768, 576), (0, 0, 0, 255))
            for layer in doc['Layers']:
                for tx in range(96):
                    for ty in range(72):
                        for tl in layer['Tiles'][tx][ty].get('Layers', []):
                            fr = tl['Frames'][0]
                            if fr['Sheet']:
                                img = tiles[(fr['TexLoc']['X'], fr['TexLoc']['Y'])]
                                comp.alpha_composite(img, (tx * 8, ty * 8))
            px = comp.load()
            for x in range(358, 410):
                for y in range(472, 576):
                    r, g, b, _ = px[x, y]
                    assert not (abs(r - g) <= 10 and abs(g - b) <= 10 and r < 180), f'Gravier gris détecté à ({x},{y})={(r,g,b)}'
                    assert not (g > r + 10 and g > b + 40), f'Herbe résiduelle dans le chemin sud à ({x},{y})={(r,g,b)}'
            # Vérifie la présence effective de l'escalier en pierre (contraste marche éclairée / contremarche sombre)
            stair_lums = [0.299 * px[384, y][0] + 0.587 * px[384, y][1] + 0.114 * px[384, y][2] for y in range(480, 568)]
            assert max(stair_lums) - min(stair_lums) >= 75, 'Escalier sud absent ou sans relief de marches'
            # Vérifie la courbure rocheuse violette/mauve sur les bastions encadrant la cascade centrale
            for x0_flank, x1_flank in ((241, 272), (304, 335), (433, 464), (496, 527)):
                mauve_cnt = sum(
                    1
                    for xf in range(x0_flank, x1_flank)
                    for yf in range(45, 145)
                    if px[xf, yf][0] >= 160 and 80 <= px[xf, yf][1] <= 135 and 90 <= px[xf, yf][2] <= 135 and px[xf, yf][0] > px[xf, yf][1] + 45
                )
                assert mauve_cnt >= 300, f'Texture rocheuse violette manquante sur le flanc ({x0_flank}..{x1_flank}) : {mauve_cnt}'
            # Vérifie que l'écume PMU déborde bien par-dessus les falaises aux pieds des cascades
            for fx, fy in ((328, 152), (440, 152), (186, 150), (582, 150)):
                fr_c, fg_c, fb_c, _ = px[fx, fy]
                assert fr_c >= 150 and fg_c >= 170 and fb_c >= 210, f'Écume non superposée à la falaise en ({fx},{fy})={(fr_c,fg_c,fb_c)}'
            for y in range(576):
                for x in range(768):
                    r, g, b, _ = px[x, y]
                    assert not (r > g * 1.45 and b > g * 1.32 and r > 135 and b > 125), f'Magenta détecté à ({x},{y})'

    run(ROOT / 'tools/tests/test_etangdudoyen_integration.lua', ROOT)
    print('PASS test_etangdudoyen_integration (4 ambiances + swim prep + pixel checks + Lua)')


if __name__ == '__main__':
    main()
