#!/usr/bin/env python3
"""Contrôles structurels de la hutte sud. Ne remplace pas le jeu en PMDO."""
from pathlib import Path
import json,struct,io
from collections import deque
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];game=ROOT/'game';name='reverie_hutte_aquatique';sheet='Reverie_Hutte_Aquatique'
z=json.loads((game/'Data/Zone/town02_waterfallvillage.json').read_text(encoding='utf8'))['Object']['GroundMaps'];i=json.loads((game/'Data/Zone/index.idx').read_text(encoding='utf8'))['Object']['town02_waterfallvillage']['Grounds'];assert z==i and len(z)==23 and z[18]==name and z[17]=='dojo_kingambit' and z[19:]==['reverie_centre','reverie_nord','reverie_residentiel','reverie_etang']
g=json.loads((game/'Data/Ground'/f'{name}.rsground').read_text(encoding='utf-8-sig'))['Object'];assert g['AssetName']==name and g['TexSize']==1 and len(g['Layers'])==1
arr=g['Layers'][0]['Tiles'];assert len(arr)==49 and all(len(c)==36 for c in arr)
b=(game/'Content/Tile'/f'{sheet}.tile').read_bytes();size,count=struct.unpack_from('<ii',b);assert size==8 and count==1785
entries={}
for n in range(count):
 x,y,off=struct.unpack_from('<iiq',b,8+16*n);assert (x,y) not in entries;length=struct.unpack_from('<q',b,off)[0];assert 0<length<1000000 and off+8+length<=len(b);image=Image.open(io.BytesIO(b[off+8:off+8+length]));assert image.size==(8,8);image.verify();entries[x,y]=off
animated=0
for col in arr:
 for tile in col:
  layers=tile['Layers'];assert len(layers)==1
  f=layers[0]['Frames'];assert len(f) in (1,4)
  if len(f)==4:
   animated+=1;assert layers[0]['FrameLength']==10 and len({(t['TexLoc']['X'],t['TexLoc']['Y']) for t in f})==4
  for t in f:assert t['Sheet']==sheet and (t['TexLoc']['X'],t['TexLoc']['Y']) in entries
assert animated==7
obs=g['obstacles'];assert len(obs)==49 and all(len(c)==36 for c in obs)
def free(x,y):return 0<=x<=47 and 0<=y<=34 and all(obs[x+dx][y+dy]['Tags']==0 for dx in (0,1) for dy in (0,1))
start=(23,30);assert free(*start);visited={start};queue=deque([start])
while queue:
 x,y=queue.popleft()
 for point in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
  if point not in visited and free(*point):visited.add(point);queue.append(point)
assert (23,33) in visited and (21,30) in visited
ent=g['Entities'][0];assert len(ent['MapChars'])==0 and len(ent['GroundObjects'])==1
obj=ent['GroundObjects'][0];assert obj['EntName']=='Water_Home_Entrance' and obj['triggerType']==2 and obj['Collider']=={'X':160,'Y':280,'Width':64,'Height':8}
assert any(x['EntName']=='Main_Entrance_Marker' for x in ent['Markers'])
city=(game/'Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf8');dev=(game/'Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8');assert city==dev
assert "nom = 'PorteHutteSud', titre = 'Hutte aquatique', x = 608, y = 1680, largeur = 72, hauteur = 40, retour_x = 656, retour_y = 1744, interieur = 'reverie_hutte_aquatique'" in city
script=(game/'Data/Script/destiny/ground'/name/'init.lua').read_text(encoding='utf8');assert 'Water_Home_Entrance_Touch' in script and "ArriveeVille = 'batiment'" in script and 'sortie_en_cours = false; GAME:FadeIn(20)' in script
print('Hutte sud : zone, 1 785 tuiles, quatre phases et itinéraire statique contrôlés ; gameplay non testé.')
