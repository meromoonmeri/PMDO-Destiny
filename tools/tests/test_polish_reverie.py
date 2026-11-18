#!/usr/bin/env python3
"""Vérifie le lot visuel de Réverie et les animations locales de ses habitants."""
from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

from executer_lua import run

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from lib_tiles import read_tilesheet
from polish_reverie_raccords import BANK, DONOR, GRASS, MAPS, TREES, frame, parts, tracks
from unpack_payload import PAYLOADS


def verify():
    info = json.loads((ROOT / 'tools/reverie_polish_manifest.json').read_text(encoding='utf-8'))
    city_layers = None
    for name in MAPS:
        rel = f'payload/{name}.rsground.gz'
        raw = gzip.decompress((ROOT / rel).read_bytes())
        _, data, _ = parts(raw)
        _unused, digest, size = PAYLOADS[rel]
        assert len(raw) == size == info['cartes'][name]['octets']
        assert hashlib.sha256(raw).hexdigest() == digest == info['cartes'][name]['sha256']
        if city_layers is None:
            city_layers = data
        else:
            assert data == city_layers, name
    assert city_layers is not None
    layers = json.loads(city_layers)
    assert len(layers) == 11
    ts, bank = read_tilesheet(ROOT / 'game/Content/Tile' / (BANK + '.tile'))
    assert ts == 8 and len(bank) == info['banque']['cellules']
    palette = Counter()
    boxes = Counter()
    for x, col in enumerate(layers[0]['Tiles']):
        for y, cell in enumerate(col):
            for t in tracks(cell):
                for ref in t['Frames']:
                    sheet, tx, ty = frame(ref)
                    assert (sheet, tx, ty) != (GRASS, 39, 218)
                    if sheet == BANK:
                        assert (tx, ty) in bank and bank[tx, ty].size == (8, 8)
                        palette[tx, ty] += 1
                        for route in info['chemins']:
                            x0, y0, x1, y1 = route['rectangle_px']
                            if x0 <= x*8 < x1 and y0 <= y*8 < y1:
                                boxes[route['nom']] += 1
                                break
                        else:
                            raise AssertionError(f'raccord hors du lot : {x},{y}')
    assert set(palette) == set(bank)
    assert boxes == {p['nom']: p['cellules'] for p in info['chemins']}
    objects = layers[6]['Tiles']
    sx, sy = DONOR
    for _old_x, y, x, _removed in TREES:
        for dx in range(10):
            for dy in range(9):
                donor = tracks(objects[sx + dx][sy + dy])
                if donor:
                    assert tracks(objects[x + dx][y + dy])[-len(donor):] == donor, (x, y, dx, dy)
    print('PASS : 10 variantes synchronisées, tuiles natives valides, 4 arbres complets et 4 raccords bornés.')
    run(ROOT / 'tools/tests/test_polish_reverie.lua', ROOT)


if __name__ == '__main__':
    verify()
