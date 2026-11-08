from pathlib import Path
from collections import deque
import gzip,json
root=Path('/home/user/chantier-apercu-reverie/travail')
a=root/'game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua';b=root/'game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua'
s=a.read_text();assert s==b.read_text(); assert s.count('installer_doyen_draco(map)')==3
assert "map.AssetName ~= 'reverie_etang'" in s and "habitant('Doyen_Draco', 'dragonair', Gender.Male, 1120, 2080)" in s
assert 'acteur.HideShadow = true' in s and "{'Doyen', 'Drifloon'}" in s
with gzip.open('/home/user/chantier-edition-couches/sources/reverie_etang.rsground.gz','rt',encoding='utf-8-sig') as f:o=json.load(f)['Object']
g=o['obstacles'];W=len(g);H=len(g[0]);
def free(x,y):return 0<=x<W-1 and 0<=y<H-1 and all(g[x+dx][y+dy]['Tags']==0 for dx in (0,1) for dy in (0,1))
assert not free(1120//8,2080//8) and free(1104//8,2080//8)
start=(1104//8,2080//8);goal=(1072//8,2200//8);q=deque([start]);seen={start}
while q:
 x,y=q.popleft()
 for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
  n=(x+dx,y+dy)
  if n not in seen and free(*n):seen.add(n);q.append(n)
assert goal in seen
print('PASS : scripts identiques, personnage séparé, joueur libre, eau bloquée, chemin statique jusqu’aux pierres')
