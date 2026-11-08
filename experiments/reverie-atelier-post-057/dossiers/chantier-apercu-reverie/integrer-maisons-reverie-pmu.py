#!/usr/bin/env python3
from pathlib import Path
import sys,copy,json,hashlib
from collections import deque
R=Path(__file__).resolve().parent;sys.path.insert(0,'/home/user/PMU-Destiny-module');import pmu_core
selection={'reverie_rock_home':'s1142','reverie_fire_home':'s1143','reverie_grass_home':'s1144','reverie_normal_home':'s1145','reverie_water_home':'s1146','reverie_electric_home':'s1373'}
types=json.loads((R/'types-cartes-pmu.json').read_text())
for name,id in selection.items():
 f=R/'originaux/game/Data/Ground'/f'{name}.rsground';old=json.loads(f.read_text(encoding='utf-8-sig'));o=old['Object'];m=pmu_core.load(id);assert (m['width'],m['height'])==(20,15)
 data,missing=pmu_core.to_ground(m);assert not missing;v=json.loads(data.decode('utf-8-sig'))['Object'];o['Layers']=v['Layers'];o['TexSize']=1
 obstacle=[]
 for x in range(80):
  col=[]
  for y in range(60):col.append({'Bounds':{'X':x*8,'Y':y*8,'Width':8,'Height':8},'Tags':1 if types[id][f'{x//4},{y//4}']==1 else 0})
  obstacle.append(col)
 o['obstacles']=obstacle;e=o['Entities'][0]
 assert len(e['GroundObjects'])==1 and len(e['Spawners'])==1 and len(e['Markers'])==2
 trigger=e['GroundObjects'][0];trigger['Collider'].update(X=288,Y=384,Width=64,Height=8)
 e['Spawners'][0]['Collider'].update(X=328,Y=352,Width=16,Height=16)
 for marker in e['Markers']: marker['Collider'].update(X=304,Y=352,Width=16,Height=16)
 for x,y in [(304,352),(328,352),(304,368),(328,368)]:
  assert all(obstacle[cx][cy]['Tags']==0 for cx in range(x//8,(x+15)//8+1) for cy in range(y//8,(y+15)//8+1)), (name,x,y)
 start=(9,11);seen={start};q=deque([start]);ts=types[id]
 while q:
  x,y=q.popleft()
  for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
   a,b=x+dx,y+dy
   if 0<=a<20 and 0<=b<15 and ts[f'{a},{b}']!=1 and (a,b) not in seen:seen.add((a,b));q.append((a,b))
 assert (9,12) in seen and len(seen)>30,(name,len(seen))
 dest=R/'travail/game/Data/Ground'/f'{name}.rsground';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('\ufeff'+json.dumps(old,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print(name,id,m['name'],len(seen),'cases source accessibles',len(dest.read_bytes()),hashlib.sha256(dest.read_bytes()).hexdigest())
