#!/usr/bin/env python3
"""Reconstruction locale de la maison d'équipe à partir de s1506.
Ne touche pas au dépôt publié. Lit uniquement les sources sauvegardées.
"""
from pathlib import Path
from collections import deque
import json,sys,copy,hashlib
R=Path(__file__).resolve().parent
sys.path.insert(0,'/home/user/PMU-Destiny-module')
import pmu_core
source=R/'originaux/game/Data/Ground/maison_equipe_falaise.rsground'
old=json.loads(source.read_text(encoding='utf-8-sig'))
mapid='s1506';m=pmu_core.load(mapid); assert (m['width'],m['height'])==(20,15)
data,missing=pmu_core.to_ground(m);assert not missing
vis=json.loads(data.decode('utf-8-sig'))['Object'];out=copy.deepcopy(old);o=out['Object']
assert o['AssetName']=='maison_equipe_falaise'
types=json.loads((R/'types-cartes-pmu.json').read_text())[mapid];assert len(types)==300
# Convertit uniquement les blocages explicites Type 1. Les autres types et
# scripts PMU ne sont pas importés comme mécanismes de jeu.
w,h=m['width']*4,m['height']*4
ob=[]
for x in range(w):
 col=[]
 for y in range(h):
  typ=types[f'{x//4},{y//4}'];col.append({'Bounds':{'X':x*8,'Y':y*8,'Width':8,'Height':8},'Tags':1 if typ==1 else 0})
 ob.append(col)
o['TexSize']=1;o['Layers']=vis['Layers'];o['obstacles']=ob
# Les identifiants d'événements et les scripts d'origine sont inchangés.
e=o['Entities'][0];objects={x['EntName']:x for x in e['GroundObjects']};markers={x['EntName']:x for x in e['Markers']}
assert set(objects)=={'SortieMaison','LitEquipe','LitPartenaire'} and 'entree' in markers
objects['SortieMaison']['Collider'].update(X=288,Y=416,Width=64,Height=8)
objects['LitEquipe']['Collider'].update(X=168,Y=312,Width=24,Height=24)
objects['LitPartenaire']['Collider'].update(X=456,Y=312,Width=24,Height=24)
markers['entree']['Collider'].update(X=304,Y=384,Width=16,Height=16)
# La position ancienne (184,272) est encore dans la carte ; vérifier qu'une
# ancienne sauvegarde à cet endroit n'apparaisse pas dans un obstacle.
def libre(x,y):
 return 0<=x and 0<=y and x+15<w*8 and y+15<h*8 and all(ob[xx][yy]['Tags']==0 for xx in range(x//8,(x+15)//8+1) for yy in range(y//8,(y+15)//8+1))
assert libre(304,384) and libre(328,384), 'entrée et partenaire'
assert libre(184,272),'ancien point d’entrée'
# BFS grossière à la grille d'origine ; cible : sortie et voisinages des lits.
start=(9,12);todo=deque([start]);visited={start}
while todo:
 x,y=todo.popleft()
 for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
  nx,ny=x+dx,y+dy
  if 0<=nx<20 and 0<=ny<15 and types[f'{nx},{ny}']!=1 and (nx,ny) not in visited:visited.add((nx,ny));todo.append((nx,ny))
assert (9,13) in visited and (5,10) in visited and (14,10) in visited
# Ne pas effacer l'identité, musique, nom, version, entités ou événements.
assert all(o[k]==old['Object'][k] for k in ['AssetName','Music','Name','Released','Comment'])
assert [x['EntName'] for x in e['GroundObjects']]==[x['EntName'] for x in old['Object']['Entities'][0]['GroundObjects']]
f=R/'travail/game/Data/Ground/maison_equipe_falaise.rsground';f.parent.mkdir(parents=True,exist_ok=True)
f.write_text('\ufeff'+json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('Maison équipe locale :',mapid,m['name'],'5 calques,',w,h,'cases, source types 1 bloqués ;',len(visited),'cases PMU accessibles')
print('Dimensions',f.stat().st_size,'SHA-256',hashlib.sha256(f.read_bytes()).hexdigest())
print('Attention : cadence animation indicative, Type spéciaux non convertis, ancienne sauvegarde seulement partiellement vérifiée, test moteur indispensable.')
