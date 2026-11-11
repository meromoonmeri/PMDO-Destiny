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
PASSAGE_ETANG={(147,272),(148,272)}|{(x,y) for x in range(178,188) for y in range(256,262)}|{(x,y) for x in range(192,200) for y in range(256,262)}
# Audit visuel/obstacles : bosses fantômes dégagées (49,202 + diagonale 155..157,263..267),
# fente falaise est du Café (160..184,170) et poche eau cascade (146,249) refermées.
AUDIT_CLEAR={(49,202),(155,263),(155,264),(156,265),(156,266),(157,267)}
AUDIT_BLOCK_CLIFF={(x,170) for x in range(160,185)}
AUDIT_BLOCK_BASIN={(x,255) for x in range(32,48)}|{(x,256) for x in range(33,47)}|{(x,257) for x in range(34,46)}|{(x,258) for x in range(36,44)}|{(x,259) for x in range(38,42)}
for suffix in ('','_Dev'):
 oc=grid(read(ref,'reverie_centre'+suffix));on=grid(read(ref,'reverie_nord'+suffix));c=grid(read(game,'reverie_centre'+suffix));n=grid(read(game,'reverie_nord'+suffix));global_=grid(read(game,'WaterfallVillageCapital'+suffix));changed=0
 for x in range(200):
  for y in range(500):
   expected=min(oc[x][y]['Tags'],on[x][y]['Tags'])
   if (x,y) in {(96,154),(96,155)}|AUDIT_BLOCK_CLIFF:
    # Panneau déplacé (96,154..155) et mur de falaise est du Café (160..184,170) bloqués.
    assert expected==0 and c[x][y]['Tags']==n[x][y]['Tags']==global_[x][y]['Tags']==1
   elif (x,y) in AUDIT_CLEAR:
    assert expected==1 and c[x][y]['Tags']==n[x][y]['Tags']==global_[x][y]['Tags']==0
   elif (x,y) in AUDIT_BLOCK_BASIN:
    assert expected==1 and c[x][y]['Tags']==n[x][y]['Tags']==global_[x][y]['Tags']==1
   else:
    assert c[x][y]['Tags']==n[x][y]['Tags']==expected;assert expected==1 or global_[x][y]['Tags']==0
   assert c[x][y]['Bounds']==oc[x][y]['Bounds'] and n[x][y]['Bounds']==on[x][y]['Bounds'];changed+=oc[x][y]['Tags']!=expected
 assert changed==7095
 original=grid(read(ref,'reverie_residentiel'+suffix));current=grid(read(game,'reverie_residentiel'+suffix))
 for x in range(200):
  for y in range(500):
   if (x,y) in AUDIT_CLEAR:
    assert original[x][y]['Tags']==1 and current[x][y]['Tags']==0 and current[x][y]['Bounds']==original[x][y]['Bounds']
   elif (x,y) in AUDIT_BLOCK_BASIN:
    assert current[x][y]['Tags']==1 and current[x][y]['Bounds']==original[x][y]['Bounds']
   else:
    assert current[x][y]==original[x][y],('reverie_residentiel',x,y)
 orig_etang=grid(read(ref,'reverie_etang'+suffix));cur_etang=grid(read(game,'reverie_etang'+suffix));etang_cleared=0
 for x in range(200):
  for y in range(500):
   if (x,y) in PASSAGE_ETANG and orig_etang[x][y]['Tags']==1:
    # Coin du bassin (147..148,272) et deux arbres du chemin est dégagés vers falaise_promontoire.
    assert cur_etang[x][y]['Tags']==0 and global_[x][y]['Tags']==0 and cur_etang[x][y]['Bounds']==orig_etang[x][y]['Bounds']
    etang_cleared+=1
   elif (x,y) in AUDIT_CLEAR:
    assert orig_etang[x][y]['Tags']==1 and cur_etang[x][y]['Tags']==0 and global_[x][y]['Tags']==0 and cur_etang[x][y]['Bounds']==orig_etang[x][y]['Bounds']
   elif (x,y)==(146,249):
    assert orig_etang[x][y]['Tags']==0 and cur_etang[x][y]['Tags']==1 and global_[x][y]['Tags']==1 and cur_etang[x][y]['Bounds']==orig_etang[x][y]['Bounds']
   else:
    assert cur_etang[x][y]==orig_etang[x][y],('reverie_etang',x,y)
 assert etang_cleared==107,etang_cleared
 print('PASS union exacte',suffix or 'jeu',changed,'cases ; étang ouvert (',etang_cleared,'cases ) et résidentiel inchangé')
 if suffix=='':g=[bytes(v['Tags'] for v in col) for col in c];etang_g=[bytes(v['Tags'] for v in col) for col in cur_etang]
# BFS avec enveloppe 16x16, à travers les anciens escaliers.
def free(x,y):return x>=0 and y>=0 and x+16<=1600 and y+16<=4000 and all(g[a][b]==0 for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1))
for start,target in [((120,952),(120,888)),((776,872),(776,808)),((1200,872),(1200,808))]:
 q=deque([start]);seen={start}
 while q and target not in seen:
  x,y=q.popleft()
  for p in ((x+4,y),(x-4,y),(x,y+4),(x,y-4)):
   if p not in seen and free(*p):seen.add(p);q.append(p)
 assert target in seen,(start,target);print('PASS passage',start,target)
def free_etang(x,y):return x>=0 and y>=0 and x+16<=1600 and y+16<=4000 and all(etang_g[a][b]==0 for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1))
q=deque([(1120,2352)]);seen={(1120,2352)}
while q and (1576,2056) not in seen:
 x,y=q.popleft()
 for p in ((x+4,y),(x-4,y),(x,y+4),(x,y-4)):
  if p not in seen and free_etang(*p):seen.add(p);q.append(p)
assert (1576,2056) in seen;print('PASS passage étang vers falaise_promontoire (1120,2352) -> (1576,2056)')
z=json.loads((R/'game/Data/Zone/town02_waterfallvillage.json').read_text(encoding='utf-8-sig'))['Object']['GroundMaps'];idx=json.loads((R/'game/Data/Zone/index.idx').read_text(encoding='utf-8-sig'))['Object']['town02_waterfallvillage']['Grounds'];assert z==idx and z[19:]==['reverie_centre','reverie_nord','reverie_residentiel','reverie_etang','guilde_cliff_jour','guilde_cliff_aube','guilde_cliff_crepuscule','guilde_cliff_nuit']
for name in ['reverie_centre','reverie_nord','reverie_residentiel','reverie_etang']:
 s=(R/'game/Data/Script/destiny/ground'/name/'init.lua').read_text(encoding='utf8');assert "require 'destiny.ground.WaterfallVillageCapital.init'" in s
print('PASS zone, alias et liaisons existantes ; partie réelle nécessaire')

from executer_lua import run
run(R/'tools/tests/test_quartiers_reverie.lua', R)
