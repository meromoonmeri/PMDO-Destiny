#!/usr/bin/env python3
"""Chronique extérieure : cartes publiées, scénarios et interactions en Lua."""
from collections import deque
import gzip
import json
import os
from pathlib import Path

from lupa.lua54 import LuaRuntime

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = Path(os.environ.get('DESTINY_TEST_PAYLOAD', ROOT / 'payload'))
SCRIPTS = ROOT / 'game/Data/Script'
MAPS = ('WaterfallVillageCapital', 'reverie_centre', 'reverie_residentiel', 'reverie_etang')


def read_map(name):
    with gzip.open(PAYLOAD / f'{name}.rsground.gz', 'rb') as f:
        data = f.read()
    a = data.index(b'"obstacles":') + len(b'"obstacles":')
    b = data.index(b']],', a) + 2
    obstacles = [bytearray(o['Tags'] for o in col) for col in json.loads(data[a:b])]
    a = data.index(b'"MapChars":') + len(b'"MapChars":')
    b = data.index(b',"GroundObjects":', a)
    m = []
    for char in json.loads(data[a:b]):
        p = char['serializationLoc']
        m.append([char['EntName'], p['X'], p['Y'], char['Data']['BaseForm']['Species']])
    return obstacles, m


def reachable(grid, starts):
    """Trajet 16x16 vers le voisinage du poste (pas de franchissement d'eau)."""
    def free(x, y):
        return 0 <= x < len(grid) - 1 and 0 <= y < len(grid[0]) - 1 and not (
            grid[x][y] or grid[x+1][y] or grid[x][y+1] or grid[x+1][y+1])

    seen = {(x//8, y//8) for x,y in starts if free(x//8, y//8)}
    assert seen, starts
    q = deque(seen)
    while q:
        x,y = q.popleft()
        for p in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
            if p not in seen and free(*p):
                seen.add(p)
                q.append(p)
    return seen


maps = {name: read_map(name) for name in MAPS}
starts = {
    'reverie_centre': [(800, 1224), (700, 1904), (1552, 1600)],
    'reverie_residentiel': [(700, 1976), (1120, 2432)],
    'reverie_etang': [(1120, 2352)],
}
paths = {n:reachable(maps[n][0], anchors) for n,anchors in starts.items()}
lua = LuaRuntime(unpack_returned_tuples=True)
lua.globals().package.path = f'{SCRIPTS.as_posix()}/?.lua;' + lua.globals().package.path
lua.globals().arg = lua.table_from({1: ROOT.as_posix()})
lua.globals().NATIFS = lua.table_from({n: m for n, (_,m) in maps.items()}, recursive=True)
lua.globals().OBSTACLE = lambda n,x,y: maps[n][0][x][y] if 0 <= x < 200 and 0 <= y < len(maps[n][0][x]) else 1
lua.globals().ACCESSIBLE = lambda n,x,y: any((x//8+dx,y//8+dy) in paths[n]
                                              for dx,dy in [(2,0),(-2,0),(0,2),(0,-2),(0,0)])
comp = lua.eval('load')
# Ouverture Unicode via Python pour le runner Windows.
lua.globals().loadfile = lambda p: comp(Path(p).read_text(encoding='utf-8-sig'), '@'+p)
lua.execute((ROOT/'tools/tests/test_reverie_recit.lua').read_text(encoding='utf-8'))
