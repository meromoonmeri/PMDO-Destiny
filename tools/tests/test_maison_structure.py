#!/usr/bin/env python3
"""Vérifie la nouvelle carte et les obstacles, sans simuler le moteur."""
from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[2];G=R/'game';load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))['Object']
z=load(G/'Data/Zone/destiny_cliff_tests.json')['GroundMaps'];i=load(G/'Data/Zone/index.idx')['destiny_cliff_tests']['Grounds'];assert z==i==['cliffdaytest','cliffdaytest_nuit','cliffdaytest_source','cliffnordouesttest1','cliffnordouesttest1_nuit','maison_equipe_falaise','cliffdaytest_aube','cliffdaytest_crepuscule']
m=load(G/'Data/Ground/maison_equipe_falaise.rsground');assert m['AssetName']=='maison_equipe_falaise';e=m['Entities'][0];assert not e['MapChars'] and not e['Spawners'];assert any(x['EntName']=='entree' for x in e['Markers'])
objs={o['EntName']:o for o in e['GroundObjects']};assert set(objs)=={'SortieMaison','LitEquipe','LitPartenaire'} and objs['SortieMaison']['triggerType']==2
for name in ('LitEquipe','LitPartenaire'):assert objs[name]['ObjectAnim']['AnimIndex']=='Hay_Bed' and objs[name]['triggerType']==1 and not objs[name]['Passable']
g=m['obstacles'];walls=[objs[n]['Collider'] for n in ('LitEquipe','LitPartenaire')]
def overlap(a,b):return a[0]<b[0]+b[2] and a[0]+a[2]>b[0] and a[1]<b[1]+b[3] and a[1]+a[3]>b[1]
def free(x,y):return x>=0 and y>=0 and x+16<=len(g)*8 and y+16<=len(g[0])*8 and all(g[a][b]['Tags']==0 for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1)) and not any(overlap((x,y,16,16),(o['X'],o['Y'],o['Width'],o['Height'])) for o in walls)
q=collections.deque([(184,272)]);seen={(184,272)}
while q:
 x,y=q.popleft()
 for p in ((x+4,y),(x-4,y),(x,y+4),(x,y-4)):
  if p not in seen and free(*p):seen.add(p);q.append(p)
for o in walls:
 x,y=o['X'],o['Y'];assert any(p in seen for p in [(x-16,y),(x+24,y),(x,y-16),(x,y+24)]),o
assert (184,284) in seen
print('PASS zone et index, sortie et accès statique aux deux lits')
