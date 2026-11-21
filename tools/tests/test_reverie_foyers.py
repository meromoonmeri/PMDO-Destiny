#!/usr/bin/env python3
"""Foyers de Réverie : scripts Lua, collisions, accès et seuils des cartes livrées."""
from collections import deque
import json
import os
from pathlib import Path

from lupa.lua54 import LuaRuntime

ROOT = Path(__file__).resolve().parents[2]
GROUND = Path(os.environ.get('DESTINY_TEST_GROUND', ROOT / 'game/Data/Ground'))
NOMS = ('rock_home', 'grass_home', 'water_home', 'hutte_aquatique', 'fire_home')
MAPS = {}
for suffix in NOMS:
    name = f'reverie_{suffix}'
    o = json.loads((GROUND / f'{name}.rsground').read_text(encoding='utf-8-sig'))['Object']
    layer = o['Entities'][0]
    assert not layer['MapChars'], name  # Les PNG/sprites ne sont pas incrustés dans les cartes.
    assert len(layer['GroundObjects']) == 1 and layer['GroundObjects'][0]['triggerType'] == 2
    grid = [bytes(tile['Tags'] for tile in col) for col in o['obstacles']]
    markers = [m['Collider'] for m in layer['Markers']]
    entrance = next(m['Collider'] for m in layer['Markers'] if m['EntName'] == 'Main_Entrance_Marker')
    MAPS[name] = dict(grid=grid, w=len(grid), h=len(grid[0]), markers=markers,
                      entrance=dict(entrance), seuil=layer['GroundObjects'][0]['Collider'])


def overlap(x, y, r):
    return x < r['X']+r['Width'] and x+16 > r['X'] and y < r['Y']+r['Height'] and y+16 > r['Y']


def verifier_chemin(name, positions):
    data = MAPS[name]
    grid, w, h = (data[k] for k in ('grid', 'w', 'h'))
    sortie = data['seuil']
    pnj = [dict(X=p[1], Y=p[2], Width=16, Height=16) for p in positions.values()]
    for i, p in enumerate(pnj):
        x, y = p['X'], p['Y']
        assert not any(overlap(x, y, r) for r in [sortie, *data['markers'], *pnj[:i]]), (name, p)
        assert not any(grid[a][b] for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1)), (name,p)

    def libre(x, y):
        return (0 <= x <= w*8-16 and 0 <= y <= h*8-16
                and not any(grid[a][b] for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1))
                and not any(overlap(x, y, rect) for rect in pnj))

    depart = (data['entrance']['X'], data['entrance']['Y'])
    assert libre(*depart), (name, 'spawn')
    seen, q = {depart}, deque([depart])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x-8,y), (x+8,y), (x,y-8), (x,y+8)):
            if (nx,ny) not in seen and libre(nx,ny):
                q.append((nx,ny))
                seen.add((nx,ny))
    assert any(overlap(x,y,sortie) for x,y in seen), (name, 'seuil isolé')
    for r in pnj:
        x, y = r['X'], r['Y']
        assert any(p in seen for p in ((x-16,y), (x+16,y), (x,y-16), (x,y+16))), (name, 'PNJ isolé', r)


lua = LuaRuntime(unpack_returned_tuples=True)
g = lua.globals()
g.package.path = f'{(ROOT / "game/Data/Script").as_posix()}/?.lua;' + g.package.path
load = lua.eval('load')
g.loadfile = lambda path: load(Path(path).read_text(encoding='utf-8-sig'), '@'+path)
g.ARG_ROOT = ROOT.as_posix()
g.CARTES = lua.table_from({n: {k: v for k,v in m.items() if k != 'grid'} for n,m in MAPS.items()}, recursive=True)
g.TEST_CHEMINS = verifier_chemin
g.OBSTACLE = lambda n,x,y: MAPS[n]['grid'][x][y]
lua.execute((ROOT / 'tools/tests/test_reverie_foyers.lua').read_text(encoding='utf-8'))
