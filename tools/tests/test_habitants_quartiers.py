#!/usr/bin/env python3
"""Habitants et calques séparés, avec continuité visuelle vérifiée.

Les doublures Lua et la comparaison des tuiles ne remplacent pas une partie.
"""
from pathlib import Path
from collections import Counter
import gzip,json,shutil,subprocess
import ijson
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'game/Data/Ground/WaterfallVillageCapital.rsground'
NAMES={'centre':'reverie_centre','nord':'reverie_nord','residentiel':'reverie_residentiel','etang':'reverie_etang'}
RADIUS=176 # 1408 px : vue maximale 1280px + 128px de marge pour les décors.

def interp(x,pts):
 for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
  if x<=x1:return y0+(y1-y0)*(x-x0)/(x1-x0)
 return pts[-1][1]
def owner(x,y):
 if y<interp(x,[(0,920),(135,920),(400,880),(785,840),(1213,840),(1600,730)]):return 'nord'
 if x<840:return 'centre' if y<1944 else 'residentiel'
 if y<1872:return 'centre'
 return 'etang' if y<interp(x,[(840,2392),(1128,2392),(1250,2360),(1600,2220)]) else 'residentiel'

def read_items(file, prefix, compressed=False):
 op=gzip.open if compressed else open
 with op(file,'rb') as f:
  assert f.read(3)==b'\xef\xbb\xbf'
  return list(ijson.items(f,prefix))

orig_entity=read_items(source,'Object.Entities.item');assert len(orig_entity)==1
orig_chars=orig_entity[0]['MapChars'];orig_objects=orig_entity[0]['GroundObjects'];assert len(orig_chars)==26 and len(orig_objects)==7
original={c['EntName']:c for c in orig_chars};assert len(original)==26
original_objects={o['EntName']:o for o in orig_objects};assert len(original_objects)==7
original_deco=read_items(source,'Object.Decorations.item');seen_chars=[];seen_objects=[]
owners=[[owner(x*8+4,y*8+4) for y in range(500)] for x in range(200)]
for sector,name in NAMES.items():
 payload=ROOT/'payload'/f'{name}.rsground.gz';entity=read_items(payload,'Object.Entities.item',True);assert len(entity)==1
 local=entity[0]
 assert local['Markers']==orig_entity[0]['Markers'] and local['Spawners']==orig_entity[0]['Spawners']
 for c in local['MapChars']:
  n=c['EntName'];p=c['serializationLoc'];assert c==original[n] and owner(p['X']+8,p['Y']+8)==sector,(sector,n);seen_chars.append(n)
 for obj in local['GroundObjects']:
  n=obj['EntName'];p=obj['Collider'];assert obj==original_objects[n] and owner(p['X']+p['Width']/2,p['Y']+p['Height']/2)==sector,(sector,n);seen_objects.append(n)
 assert read_items(payload,'Object.Decorations.item',True)==original_deco
 # Integral image over the full sector shape, no optional numerical packages.
 integral=[[0]*501 for _ in range(201)]
 for x in range(200):
  n=0
  for y in range(500):
   n+=owners[x][y]==sector;integral[x+1][y+1]=integral[x][y+1]+n
 mask=[]
 for x in range(200):
  a=max(0,x-RADIUS);b=min(200,x+RADIUS+1);row=bytearray(500)
  for y in range(500):
   c=max(0,y-RADIUS);d=min(500,y+RADIUS+1)
   row[y]=bool(integral[b][d]-integral[a][d]-integral[b][c]+integral[a][c])
  mask.append(row)
 with open(source,'rb') as fi,gzip.open(payload,'rb') as fo:
  fi.read(3);fo.read(3);original_layers=ijson.items(fi,'Object.Layers.item');new_layers=ijson.items(fo,'Object.Layers.item');count=retained=removed=0
  for base,current in zip(original_layers,new_layers):
   count+=1
   assert {k:v for k,v in base.items() if k!='Tiles'}=={k:v for k,v in current.items() if k!='Tiles'}
   assert len(base['Tiles'])==len(current['Tiles'])==200
   for x in range(200):
    old=base['Tiles'][x];new=current['Tiles'][x];assert len(old)==len(new)==500
    for y in range(500):
     if mask[x][y]:assert new[y]==old[y],(sector,count,x,y,'décor visible modifié');retained+=bool(old[y])
     else:assert not new[y],(sector,count,x,y,'tuile distante conservée');removed+=bool(old[y])
  assert count==11 and next(original_layers,None) is None and next(new_layers,None) is None
  assert retained and removed,(sector,retained,removed)
 print('PASS',sector,len(local['MapChars']),'PNJ natifs, 11 calques propres,',retained,'tuiles conservées et',removed,'distantes retirées')
assert Counter(seen_chars)==Counter(original.keys()),'un PNJ natif perdu ou copié dans deux quartiers'
assert Counter(seen_objects)==Counter(original_objects.keys()),'un objet natif perdu ou copié dans deux quartiers'
city=(ROOT/'game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf8')
dev=(ROOT/'game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8');assert city==dev
visit=city[city.index('function ville.Visite()'):city.index('local function rediriger_ancienne_ville')]
for camera in ['GAME:MoveCamera(616, 925','GAME:MoveCamera(936, 940','GAME:MoveCamera(1100, 950','GAME:MoveCamera(500, 1010'] :assert camera in visit
for camera in ['GAME:MoveCamera(530, 2350','GAME:MoveCamera(800, 530','GAME:MoveCamera(1425, 320']:assert camera not in visit
for text in ['Bienvenue à [color=#F5D27A]Réverie Town','Tu ne te souviens toujours pas de ton passé','Notre prochaine aventure commencera quand nous serons prêts']:assert text in visit
assert 'preparer_habitants_quartier(map)' in city and 'GROUND:RemoveCharacter(h.nom)' in city
lua=shutil.which('lua5.4')
if lua:subprocess.run([lua,str(ROOT/'tools/tests/test_habitants_quartiers.lua'),str(ROOT)],check=True)
else:print('Lua 5.4 absent : test des migrations simulées ignoré.')
print('PASS : PNJ natifs uniques, animations préservées, visite centrée. Partie réelle à tester.')
