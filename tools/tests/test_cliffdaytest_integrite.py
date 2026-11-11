#!/usr/bin/env python3
"""Controle d'integrite des 5 cartes cliffdaytest*, des planches PICHU_CLIFF_DAY_* et de la battle map 24px."""
from __future__ import annotations

import io
import json
import struct
from collections import deque
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TILE_DIR = ROOT / 'game' / 'Content' / 'Tile'
GROUND_DIR = ROOT / 'game' / 'Data' / 'Ground'
MAP_DIR = ROOT / 'game' / 'Data' / 'Map'

MAP_W, MAP_H = 123, 99
MAP24_W, MAP24_H = 41, 33

SMEAR_COLORS = {
    (240, 208, 120),
    (232, 152, 104),
    (240, 168, 104),
    (240, 184, 104),
}


def load_tile_sheet(name: str) -> tuple[int, dict[tuple[int, int], Image.Image]]:
    raw = (TILE_DIR / f'{name}.tile').read_bytes()
    ts, count = struct.unpack_from('<ii', raw, 0)
    tiles: dict[tuple[int, int], Image.Image] = {}
    for i in range(count):
        tx, ty, off = struct.unpack_from('<iiq', raw, 8 + 16 * i)
        ln = struct.unpack_from('<q', raw, off)[0]
        im = Image.open(io.BytesIO(raw[off + 8:off + 8 + ln])).convert('RGBA')
        # Unpremultiply for exact pixel checks
        px = bytearray(im.tobytes())
        for k in range(0, len(px), 4):
            a = px[k + 3]
            if 0 < a < 255:
                px[k] = min(255, round(px[k] * 255.0 / a))
                px[k + 1] = min(255, round(px[k + 1] * 255.0 / a))
                px[k + 2] = min(255, round(px[k + 2] * 255.0 / a))
            elif a == 0:
                px[k] = px[k + 1] = px[k + 2] = 0
        tiles[(tx, ty)] = Image.frombytes('RGBA', im.size, bytes(px))
    return ts, tiles


def main() -> None:
    # 1. Integrite des 5 .rsground : 0 frame Sheet="", obstacles identiques, L0 ciel conserve
    obs_ref = None
    grounds: dict[str, dict] = {}
    for gname in ('cliffdaytest', 'cliffdaytest_aube', 'cliffdaytest_crepuscule', 'cliffdaytest_nuit', 'cliffdaytest_source'):
        obj = json.loads((GROUND_DIR / f'{gname}.rsground').read_text(encoding='utf-8-sig'))['Object']
        grounds[gname] = obj
        for lyr in obj['Layers']:
            for x in range(MAP_W):
                for y in range(MAP_H):
                    for sub in lyr['Tiles'][x][y].get('Layers', []):
                        assert sub.get('FrameLength', 0) > 0, (gname, lyr['Name'], x, y)
                        for fr in sub.get('Frames', []):
                            assert fr.get('Sheet'), f'Sheet vide dans {gname} ({lyr["Name"]}, {x}, {y})'
        if obs_ref is None:
            obs_ref = obj['obstacles']
        else:
            assert obj['obstacles'] == obs_ref, f'Desynchronisation obstacles sur {gname}'

        if gname in ('cliffdaytest', 'cliffdaytest_aube', 'cliffdaytest_crepuscule'):
            assert obj['Layers'][0]['Visible'] is False, f'L0 ciel doit rester cache sur {gname}'

    assert obs_ref is not None

    # 2. Moulin (2..7, 78..84) : 4 phases distinctes, 0 trou de mer la nuit, 0 morsure
    wm_broken = [(3, 79), (3, 80), (3, 82), (3, 83), (4, 79), (5, 79)]
    for gname, l_ter, expected_ter in [
        ('cliffdaytest', 2, 'PICHU_CLIFF_DAY_TERRAIN'),
        ('cliffdaytest_aube', 2, 'PICHU_CLIFF_DAY_TERRAIN_AUBE_FILTRE'),
        ('cliffdaytest_crepuscule', 2, 'PICHU_CLIFF_DAY_TERRAIN_CREP_FILTRE'),
        ('cliffdaytest_nuit', 1, 'PICHU_CLIFF_DAY_TERRAIN_NUIT_FILTRE'),
    ]:
        obj = grounds[gname]
        for tx, ty in wm_broken:
            subs = obj['Layers'][l_ter]['Tiles'][tx][ty].get('Layers', [])
            assert len(subs) == 1, (gname, tx, ty)
            frames = subs[0]['Frames']
            assert len(frames) == 4, (gname, tx, ty, len(frames))
            for p, fr in enumerate(frames):
                assert fr['Sheet'] == expected_ter, (gname, tx, ty, fr)
                assert fr['TexLoc'] == {'X': tx, 'Y': ty + MAP_H * p}, (gname, tx, ty, p, fr)

    # 3. Verifier les pixels de PICHU_CLIFF_DAY_TERRAIN* et PICHU_CLIFF_DAY_CANOPY*
    _, ter = load_tile_sheet('PICHU_CLIFF_DAY_TERRAIN')
    _, can = load_tile_sheet('PICHU_CLIFF_DAY_CANOPY')
    for suffix in ('_AUBE_FILTRE', '_CREP_FILTRE', '_NUIT_FILTRE'):
        _, t_var = load_tile_sheet(f'PICHU_CLIFF_DAY_TERRAIN{suffix}')
        _, c_var = load_tile_sheet(f'PICHU_CLIFF_DAY_CANOPY{suffix}')
        assert set(t_var.keys()) == set(ter.keys()), f'Cles TERRAIN divergentes pour {suffix}'
        assert set(c_var.keys()) == set(can.keys()), f'Cles CANOPY divergentes pour {suffix}'
        for tx, ty in wm_broken:
            imgs = [t_var[(tx, ty + MAP_H * p)].tobytes() for p in range(4)]
            assert len(set(imgs)) > 1, f'Moulin fige en ({tx},{ty}) sur TERRAIN{suffix}'

    # Moulin 4 phases distinctes sur Jour
    for tx, ty in wm_broken:
        imgs = [ter[(tx, ty + MAP_H * p)].tobytes() for p in range(4)]
        assert len(set(imgs)) > 1, f'Moulin fige en ({tx},{ty}) sur TERRAIN'

    # 0 pixel semi-transparent sur TERRAIN (y < 99) -> bord cloture arriere net
    for (tx, ty), im in ter.items():
        if ty < MAP_H:
            px = im.tobytes()
            for k in range(3, len(px), 4):
                assert px[k] in (0, 255), f'Pixel semi-transparent sur TERRAIN({tx},{ty}) alpha={px[k]}'

    # 0 pixel de trainee beige INVERSEPATHWAY dans les 5 anciennes zones
    for x0, y0, x1, y1 in [(64, 72, 66, 75), (70, 74, 73, 76), (94, 75, 97, 76), (107, 62, 110, 65), (114, 63, 114, 63)]:
        for tx in range(x0, x1 + 1):
            for ty in range(y0, y1 + 1):
                px = ter[(tx, ty)].tobytes()
                for k in range(0, len(px), 4):
                    assert (px[k], px[k + 1], px[k + 2]) not in SMEAR_COLORS, f'Trainee residuelle en ({tx},{ty})'

    # Cloture arriere sans caillou parasite en (67,49) ni (77,49) -> le bas de (67,49) est de l'herbe pure
    for py in range(2, 8):
        for px in range(8):
            r, g, b, _ = ter[(67, 49)].getpixel((px, py))
            assert g > r, f'Caillou parasite encore present en (67,49) px=({px},{py}) rgb={(r,g,b)}'

    # Table-souche sans feuille verte parasite en (92, 75..76)
    for tx, ty in [(92, 75), (92, 76)]:
        px = can[(tx, ty)].tobytes()
        for k in range(0, len(px), 4):
            if px[k + 3] > 0:
                assert not (px[k + 1] > px[k] + 10), f'Feuille verte parasite en CANOPY({tx},{ty})'

    # Sol/route/touffes descendus hors CANOPY (ex: route devant citrouille 71..84, 58..70)
    for tx in range(71, 85):
        for ty in range(58, 71):
            assert (tx, ty) not in can, f'Route encore en CANOPY({tx},{ty})'

    # Deplacement Panneau Est (118..120, 50..53) -> (117..119, 60..63) et Rocher 1 (12..15, 87..90)
    for tx in range(118, 121):
        for ty in range(50, 54):
            assert (tx, ty) not in can, f'Ancien panneau Est encore en CANOPY({tx},{ty})'
    for tx in range(117, 120):
        for ty in range(60, 64):
            assert (tx, ty) in can, f'Nouveau panneau Est absent de CANOPY({tx},{ty})'
            assert grounds['cliffdaytest']['Layers'][4]['Tiles'][tx][ty].get('Layers'), f'Panneau Est absent L4 ({tx},{ty})'
    for tx in range(9, 12):
        for ty in range(87, 91):
            assert (tx, ty) not in can, f'Ancien Rocher 1 encore en CANOPY({tx},{ty})'
    for tx in range(13, 16):
        assert (tx, 88) in can and (tx, 89) in can, f'Nouveau Rocher 1 absent de CANOPY({tx})'

    # 4. Obstacles harmonises : props solides bloques, fleurs fantomes et couloirs scriptes ouverts
    must_block = [
        (67, 47, 72, 49), (78, 47, 83, 49),  # cloture arriere
        (103, 46, 122, 51),                   # virevents Est
        (63, 51, 66, 52), (64, 53, 66, 53),   # tonneaux
        (82, 54, 83, 57),                     # boite aux lettres
        (37, 63, 41, 66), (33, 67, 36, 69),   # meules
        (28, 86, 30, 88), (50, 61, 52, 63), (56, 82, 58, 84),  # tas de bois
        (12, 87, 15, 90), (46, 70, 49, 73), (74, 90, 77, 93),  # rochers
        (12, 93, 14, 95), (43, 75, 45, 77), (51, 95, 53, 97),  # souches
        (1, 88, 10, 96), (111, 90, 120, 98),                   # arbres bordure sauves
        (18, 95, 20, 97), (42, 95, 44, 97), (79, 95, 81, 97),  # buissons 3x3
        (117, 61, 119, 63),                                    # nouveau panneau Est (base)
    ]
    for x0, y0, x1, y1 in must_block:
        for tx in range(x0, x1 + 1):
            for ty in range(y0, y1 + 1):
                assert obs_ref[tx][ty]['Tags'] == 1, f'Obstacle attendu en ({tx},{ty})'

    must_open = [
        (54, 78, 56, 79), (70, 94, 71, 95), (96, 65, 98, 66),
        (105, 88, 106, 89), (113, 61, 115, 62), (118, 64, 120, 65),
        (50, 74, 51, 75), (75, 58, 81, 59), (85, 81, 95, 98), (106, 55, 121, 59),
        (117, 60, 119, 60),
    ]
    for x0, y0, x1, y1 in must_open:
        for tx in range(x0, x1 + 1):
            for ty in range(y0, y1 + 1):
                assert obs_ref[tx][ty]['Tags'] == 0, f'Case libre attendue en ({tx},{ty})'

    # 5. Battle map cliffdaytest.rsmap + BATTLE_{BASE,FRONT}_24 synchronisees et connectees
    rsmap = json.loads((MAP_DIR / 'cliffdaytest.rsmap').read_text(encoding='utf-8-sig'))['Object']
    _, front24 = load_tile_sheet('CLIFFDAYTEST_BATTLE_FRONT_24')
    _, base24 = load_tile_sheet('CLIFFDAYTEST_BATTLE_BASE_24')
    _, sea = load_tile_sheet('PICHU_CLIFF_DAY_SEA')

    floors = {(rx, ry) for rx in range(MAP24_W) for ry in range(MAP24_H) if rsmap['Tiles'][rx][ry]['Data']['ID'] == 'floor'}
    ep = rsmap['EntryPoints'][0]['Loc']
    start = (ep['X'], ep['Y'])
    assert start in floors
    q = deque([start])
    seen = {start}
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            np_ = (cx + dx, cy + dy)
            if np_ in floors and np_ not in seen:
                seen.add(np_)
                q.append(np_)
    assert seen == floors, f'Cases floor deconnectees dans cliffdaytest.rsmap : {sorted(floors - seen)}'

    l1_non_empty = {
        (rx, ry)
        for rx in range(MAP24_W)
        for ry in range(MAP24_H)
        if rsmap['Layers'][1]['Tiles'][rx][ry].get('Layers')
    }
    assert l1_non_empty == set(front24.keys()), (l1_non_empty ^ set(front24.keys()))
    assert (39, 20) in l1_non_empty and (39, 21) in l1_non_empty
    assert (39, 16) not in l1_non_empty and (40, 16) not in l1_non_empty

    # Verification pixel exacte de BASE_24 sur les 4 phases du terrain
    day_obj = grounds['cliffdaytest']
    for ph in range(4):
        comp = Image.new('RGBA', (MAP_W * 8, MAP_H * 8), (0, 0, 0, 0))
        for li in (1, 2, 3):
            tiles = day_obj['Layers'][li]['Tiles']
            for x in range(MAP_W):
                for y in range(MAP_H):
                    for sub in tiles[x][y].get('Layers', []):
                        frs = sub['Frames']
                        fr = frs[ph % len(frs)]
                        sh = sea if 'SEA' in fr['Sheet'] else (ter if 'TERRAIN' in fr['Sheet'] else can)
                        loc = (fr['TexLoc']['X'], fr['TexLoc']['Y'])
                        if loc in sh:
                            comp.alpha_composite(sh[loc], (x * 8, y * 8))
        for rx in range(MAP24_W):
            for ry in range(12, MAP24_H):
                crop = comp.crop((rx * 24, ry * 24, (rx + 1) * 24, (ry + 1) * 24))
                assert crop.tobytes() == base24[(rx, ry + MAP24_H * ph)].tobytes(), (
                    f'CLIFFDAYTEST_BATTLE_BASE_24 desynchronise en ({rx},{ry}) phase {ph}'
                )

    print(f'TEST CLIFFDAYTEST INTEGRITE OK ({len(floors)} tuiles battle floor connectees, 4 ambiances + source + 24px verifies)')


if __name__ == '__main__':
    main()
