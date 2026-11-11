#!/usr/bin/env python3
"""Vérifie le raccordement entre reverie_centre (chemin vers Forgelina) et falaise_promontoire."""
from __future__ import annotations

from collections import deque
import gzip
import io
import json
from pathlib import Path
import struct
from PIL import Image
from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
AMBIANCES = ('jour', 'aube', 'crepuscule', 'nuit')


def _decode_tile_sheet(path: Path) -> dict[tuple[int, int], Image.Image]:
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

    # 4. Vérification pure Pillow/struct de la mer 1x1 (scintillement sur place sans dérive, pas de pics sombres, reflet lune nuit net)
    jour_doc = json.loads((ROOT / 'game/Data/Ground/falaise_promontoire_jour.rsground').read_text(encoding='utf-8-sig'))['Object']
    jour_dec = _decode_tile_sheet(ROOT / 'game/Content/Tile/Destiny_Promontoire_Jour.tile')
    sea_jour = jour_doc['Layers'][0]['Tiles']
    hz_frames = []
    for fi in range(12):
        row_im = Image.new('RGBA', (160, 16))
        for tx in range(60, 80):
            for ty in (19, 20):
                loc = sea_jour[tx][ty]['Layers'][0]['Frames'][fi]['TexLoc']
                row_im.paste(jour_dec[(loc['X'], loc['Y'])], ((tx - 60) * 8, (ty - 19) * 8))
        hz_frames.append(row_im)
    # Stationnaire sur place : la bande d'horizon y=12..15 (dither statique) ne glisse pas horizontalement
    p0_static = [hz_frames[0].getpixel((x, 12))[:3] for x in range(160)]
    for fi in range(1, 12):
        pfi_static = [hz_frames[fi].getpixel((x, 12))[:3] for x in range(160)]
        assert pfi_static == p0_static, f'Dérive horizontale inattendue sur y=12 frame {fi}'
    # Les étincelles y=0..7 scintillent d'une frame à l'autre sans simple décalage R->L
    row0_f0 = [hz_frames[0].getpixel((x, 2))[:3] for x in range(160)]
    row0_f1 = [hz_frames[1].getpixel((x, 2))[:3] for x in range(160)]
    assert row0_f1 != row0_f0, 'Les scintillements d horizon doivent s animer'
    for sx in range(1, 24):
        assert row0_f1 != row0_f0[sx:] + row0_f0[:sx], f'Défilement R->L interdit détecté (sx={sx})'
    # Aucun artefact de pics/tirets sombres sur la mer profonde x=520..639
    for ty in range(25, 58):
        for tx in range(65, 80):
            tl = sea_jour[tx][ty].get('Layers', [])
            if tl and tl[0].get('Frames'):
                loc = tl[0]['Frames'][0]['TexLoc']
                tile_im = jour_dec[(loc['X'], loc['Y'])]
                pxs = tile_im.get_flattened_data() if hasattr(tile_im, 'get_flattened_data') else tile_im.getdata()
                for r, g, b, _ in pxs:
                    assert (r, g, b) not in ((32, 88, 160), (32, 96, 200), (24, 128, 212), (24, 104, 198)), (
                        f'Artefact marin indésirable ({r},{g},{b}) en tx={tx},ty={ty}'
                    )
    # Nuit : reflet lunaire sans barre rectangulaire horizon ni traînée grise floue (228,226,224)
    nuit_doc = json.loads((ROOT / 'game/Data/Ground/falaise_promontoire_nuit.rsground').read_text(encoding='utf-8-sig'))['Object']
    nuit_dec = _decode_tile_sheet(ROOT / 'game/Content/Tile/Destiny_Promontoire_Nuit.tile')
    sea_nuit = nuit_doc['Layers'][0]['Tiles']
    # x=496..503 (MOON_CX - 58 -> hors cône, ne doit pas avoir de boîte horizon pâle)
    loc_edge = sea_nuit[62][19]['Layers'][0]['Frames'][0]['TexLoc']
    edge_px = nuit_dec[(loc_edge['X'], loc_edge['Y'])].getpixel((0, 0))[:3]
    loc_far = sea_nuit[79][19]['Layers'][0]['Frames'][0]['TexLoc']
    far_px = nuit_dec[(loc_far['X'], loc_far['Y'])].getpixel((7, 0))[:3]
    assert abs(edge_px[0] - far_px[0]) <= 20 and abs(edge_px[2] - far_px[2]) <= 20, (edge_px, far_px)
    # Vérifier absence du gris flou (228,226,224) sous le cône (ty=36..44, x=528..576)
    for ty in range(36, 45):
        for tx in range(66, 73):
            loc = sea_nuit[tx][ty]['Layers'][0]['Frames'][0]['TexLoc']
            tile_im = nuit_dec[(loc['X'], loc['Y'])]
            pxs = tile_im.get_flattened_data() if hasattr(tile_im, 'get_flattened_data') else tile_im.getdata()
            for r, g, b, _ in pxs:
                assert (r, g, b) != (228, 226, 224), f'Traînée grise floue résiduelle en tx={tx},ty={ty}'

    # 5. Simulation Lua aller-retour et synchronisation 4 ambiances
    run(ROOT / 'tools/tests/test_falaise_promontoire_integration.lua', ROOT)
    print('TEST FALAISE PROMONTOIRE INTEGRATION OK')


if __name__ == '__main__':
    main()
