#!/usr/bin/env python3
"""Fusion des obstacles, continuité des trois passages et quartiers préservés."""
from pathlib import Path
from collections import deque
import gzip,hashlib,json
R=Path(__file__).resolve().parents[2];ref=R/'tools/reverie_reference_0.4.19';game=R/'payload'
def read(root,name):return gzip.decompress((root/(name+'.rsground.gz')).read_bytes())
def part(data,key,end):
 a=data.index(('"'+key+'":').encode())+len(key)+3;b=data.index(end,a);return json.loads(data[a:b])
def grid(data):return part(data,'obstacles',b',"rand":')
# La fusion ne peut pas introduire un chemin inexistant sur la ville globale.
for suffix in ('','_Dev'):
 oc=grid(read(ref,'reverie_centre'+suffix));on=grid(read(ref,'reverie_nord'+suffix));c=grid(read(game,'reverie_centre'+suffix));n=grid(read(game,'reverie_nord'+suffix));global_=grid(read(game,'WaterfallVillageCapital'+suffix));changed=0
 for x in range(200):
  for y in range(500):
   expected=min(oc[x][y]['Tags'],on[x][y]['Tags'])
   if (x,y) in {(96,154),(96,155)}:
    # Panneau déplacé : deux cases sont volontairement bloquées et la connectivité a été vérifiée.
    assert expected==0 and c[x][y]['Tags']==n[x][y]['Tags']==global_[x][y]['Tags']==1
   else:
    assert c[x][y]['Tags']==n[x][y]['Tags']==expected;assert expected==1 or global_[x][y]['Tags']==0
   assert c[x][y]['Bounds']==oc[x][y]['Bounds'] and n[x][y]['Bounds']==on[x][y]['Bounds'];changed+=oc[x][y]['Tags']!=expected
 assert changed==7095
 for name in ['reverie_residentiel','reverie_etang']:
  original=grid(read(ref,name+suffix));current=grid(read(game,name+suffix));assert original==current,name
 print('PASS union exacte',suffix or 'jeu',changed,'cases et autres quartiers inchangés')
 if suffix=='':g=[bytes(v['Tags'] for v in col) for col in c]
# BFS avec enveloppe 16x16, à travers les anciens escaliers.
def free(x,y):return x>=0 and y>=0 and x+16<=1600 and y+16<=4000 and all(g[a][b]==0 for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1))
for start,target in [((120,952),(120,888)),((776,872),(776,808)),((1200,872),(1200,808))]:
 q=deque([start]);seen={start}
 while q and target not in seen:
  x,y=q.popleft()
  for p in ((x+4,y),(x-4,y),(x,y+4),(x,y-4)):
   if p not in seen and free(*p):seen.add(p);q.append(p)
 assert target in seen,(start,target);print('PASS passage',start,target)
z=json.loads((R/'game/Data/Zone/town02_waterfallvillage.json').read_text(encoding='utf-8-sig'))['Object']['GroundMaps'];idx=json.loads((R/'game/Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']['town02_waterfallvillage']['Grounds'];assert z==idx and z[19:]==['reverie_centre','reverie_nord','reverie_residentiel','reverie_etang']
for name in ['reverie_centre','reverie_nord','reverie_residentiel','reverie_etang']:
 s=(R/'game/Data/Script/destiny/ground'/name/'init.lua').read_text(encoding='utf8');assert "require 'destiny.ground.WaterfallVillageCapital.init'" in s
print('PASS zone, alias et liaisons existantes ; partie réelle nécessaire')

from executer_lua import run
run(R/'tools/tests/test_quartiers_reverie.lua', R)
