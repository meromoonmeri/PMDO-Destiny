#!/usr/bin/env python3
"""Audit statique du terrain Réverie existant, sans mutation de carte."""
from pathlib import Path
import gzip, io, json
from collections import deque
import ijson
R=Path(__file__).resolve().parent
result={}
for name in ('reverie_centre','reverie_nord'):
 p=R/'references/payload'/f'{name}.rsground.gz'
 with gzip.open(p,'rb') as raw:
  with io.TextIOWrapper(raw,encoding='utf-8-sig') as f:
   grid=[[int(cell.get('Tags',0)) for cell in col] for col in ijson.items(f,'Object.obstacles.item')]
 w=len(grid); h=len(grid[0]); assert (w,h)==(200,500) and all(len(c)==h for c in grid)
 def libre(x,y):
  return 0<=x<w-1 and 0<=y<h-1 and all(grid[x+i][y+j]==0 for i in (0,1) for j in (0,1))
 start=(95,4); assert libre(*start)
 q=deque([start]);seen={start}
 while q:
  x,y=q.popleft()
  for a,b in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
   if (a,b) not in seen and libre(a,b):seen.add((a,b));q.append((a,b))
 points=[(760,32),(784,32),(736,0),(752,8),(768,8),(784,8),(800,8),(760,160),(760,400),(800,1160)]
 checks={f'{x},{y}':{'libre':libre(x//8,y//8),'accessible_depuis_retour_760_32':(x//8,y//8) in seen} for x,y in points}
 result[name]={'dimensions_cases':[w,h],'taille_case_pixels':8,'collision_personnage':[16,16], 'cases_accessibles_depuis_retour_760_32':len(seen),'positions':checks}
 print(name, 'positions atteignables',len(seen),checks)
assert result['reverie_centre']['positions']['760,32']['libre']
assert result['reverie_centre']['positions']['784,32']['libre']
out=R/'rapports/audit-statique-escalier.json';out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
