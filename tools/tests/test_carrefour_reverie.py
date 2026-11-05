#!/usr/bin/env python3
"""Contrôles statiques du carrefour ; ne remplace pas un essai dans PMDO."""
from collections import deque
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / 'game'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
carte = read(GAME / 'Data/Ground/crossroadreverietown2.rsground')['Object']
assert carte['AssetName'] == 'crossroadreverietown2'
assert carte['Music'] == "Wigglytuff's Guild.ogg"
assert carte['EdgeView'] != 0
assert len(carte['Layers']) == 6
entities = carte['Entities'][0]
assert len(entities['MapChars']) == 1
assert entities['MapChars'][0]['Data']['BaseForm']['Species'] == 'snorlax'
markers = {v['EntName']: v for v in entities['Markers']}
for name, x, y in (('entree_falaise', 480, 48), ('entree_ville', 880, 416)):
    assert markers[name]['Collider']['X'] == x and markers[name]['Collider']['Y'] == y
assert 'NewObject_6' in markers
zone = read(GAME / 'Data/Zone/reverie.json')['Object']['GroundMaps']
index = read(GAME / 'Data/Zone/index.idx')['Object']['reverie']['Grounds']
assert zone == index and zone.count('crossroadreverietown2') == 1
assert (GAME / "Content/Music/Wigglytuff's Guild.ogg").read_bytes().startswith(b'OggS')

# Toutes les tuiles référencées ont une case dans le tileset correspondant.
coordonnees = {}
for couche in carte['Layers']:
    for colonne in couche['Tiles']:
        for cellule in colonne:
            for sous_couche in cellule.get('Layers', []):
                for frame in sous_couche.get('Frames', []):
                    coordonnees.setdefault(frame['Sheet'], set()).add((frame['TexLoc']['X'], frame['TexLoc']['Y']))
for nom, attendues in coordonnees.items():
    donnees = (GAME / 'Content/Tile' / (nom + '.tile')).read_bytes()
    taille, nombre = struct.unpack_from('<ii', donnees)
    assert taille == 8
    presentes = {struct.unpack_from('<ii', donnees, 8 + i * 16) for i in range(nombre)}
    assert attendues <= presentes, nom

# Parcours conservateur sur la grille, avec une boîte de 16×16 et les objets
# statiques, dont Ronflex. La collision réelle reste à valider en jeu.
obstacles = carte['obstacles']
blocs = [(v['Collider']['X'], v['Collider']['Y'], v['Collider']['Width'], v['Collider']['Height'])
         for v in entities['GroundObjects'] if not v['Passable']]
ronflex = entities['MapChars'][0]['serializationLoc']
blocs.append((ronflex['X'], ronflex['Y'], 16, 16))
def libre(x, y):
    if not (0 <= x <= 944 and 0 <= y <= 944): return False
    if any(obstacles[i][k]['Tags'] for i in range(x//8, (x+15)//8+1)
           for k in range(y//8, (y+15)//8+1)): return False
    return not any(x < bx+bw and x+16 > bx and y < by+bh and y+16 > by
                   for bx, by, bw, bh in blocs)
debut, fin = (480, 48), (880, 416)
assert libre(*debut) and libre(*fin)
attendus = {debut}
file = deque([debut])
nord = est = False
while file:
    x, y = file.popleft()
    nord |= x < 512 and x+16 > 456 and y <= 16 and y+16 > 8
    est |= x < 948 and x+16 > 940 and y < 448 and y+16 > 400
    for dx, dy in ((8,0),(-8,0),(0,8),(0,-8)):
        point = (x+dx, y+dy)
        if point not in attendus and libre(*point):
            attendus.add(point)
            file.append(point)
assert fin in attendus and nord and est

carrefour = (GAME / 'Data/Script/destiny/ground/crossroadreverietown2/init.lua').read_text(encoding='utf-8')
falaise = (GAME / 'Data/Script/destiny/ground/cliffdaytest/init.lua').read_text(encoding='utf-8')
ville = (GAME / 'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf-8')
assert "aller('destiny_cliff_tests', 'cliffdaytest', 'Dazzling_Entry_South')" in carrefour
assert "aller('town02_waterfallvillage', 'WaterfallVillageCapital', 'entrance')" in carrefour
for script, marker in ((falaise, 'entree_falaise'), (ville, 'entree_ville')):
    assert "VisiteVille ~= 'terminee'" in script
    assert f"GAME:EnterGroundMap('reverie', 'crossroadreverietown2', '{marker}')" in script
assert "GAME:EnterZone('town02_waterfallvillage', -1, 0, 0)" in falaise
print('OK : carte, tuiles, musique, liaisons et parcours estimé ; essai PMDO encore nécessaire.')
