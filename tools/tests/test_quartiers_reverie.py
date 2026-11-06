#!/usr/bin/env python3
"""Vérification structurelle des quartiers ; ne remplace pas le test en jeu."""
from pathlib import Path
from collections import deque
import gzip,hashlib,json,re,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'game/Data/Ground/WaterfallVillageCapital.rsground'
NAMES=['reverie_centre','reverie_nord','reverie_residentiel','reverie_etang']
EXPECTED={
'reverie_centre':('571462d40da934f1dcf2640c1119dc27a245d44b93c554f1bc7a0ea3fb24557b',34956112),
'reverie_nord':('c386308c7957a4bbe795618e49aa0ef3009b3d65ddec819b23fa49d54455d75b',27801859),
'reverie_residentiel':('75f27960a4b79ddb70e0f05beb8688b9d2dc3f2617b4e1ca64103e5896c1367c',33247344),
'reverie_etang':('fb275dfd6723c62f4e1bd47f18991c47411bb8f9608d3bb4ad8788d1bd4297ab',32912839)}
# Axe joueur 16x16, du bas vers le haut si dir=Up.
GATES=[
 ('reverie_centre',104,928,48,8,'Up','reverie_nord',120,888,120,864),('reverie_nord',104,904,48,8,'Down','reverie_centre',120,952,120,976),
 ('reverie_centre',760,848,48,8,'Up','reverie_nord',776,808,776,784),('reverie_nord',760,824,48,8,'Down','reverie_centre',776,872,776,896),
 ('reverie_centre',1184,848,48,8,'Up','reverie_nord',1200,808,1200,784),('reverie_nord',1184,824,48,8,'Down','reverie_centre',1200,872,1200,896),
 ('reverie_residentiel',688,1952,40,8,'Up','reverie_centre',700,1904,700,1880),('reverie_centre',688,1920,40,8,'Down','reverie_residentiel',700,1976,700,2000),
 ('reverie_residentiel',1104,2400,48,8,'Up','reverie_etang',1120,2352,1120,2328),('reverie_etang',1104,2376,48,8,'Down','reverie_residentiel',1120,2432,1120,2456)]

def interp(x,pts):
 for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
  if x<=x1:return y0+(y1-y0)*(x-x0)/(x1-x0)
 return pts[-1][1]
def owner(x,y):
 if y<interp(x,[(0,920),(135,920),(400,880),(785,840),(1213,840),(1600,730)]):return 'reverie_nord'
 if x<840:return 'reverie_centre' if y<1944 else 'reverie_residentiel'
 if y<1872:return 'reverie_centre'
 return 'reverie_etang' if y<interp(x,[(840,2392),(1128,2392),(1250,2360),(1600,2220)]) else 'reverie_residentiel'

def extract(data):
 i=data.index(b'"obstacles":')+len(b'"obstacles":');j=data.index(b',"rand":',i)
 grid=json.loads(data[i:j]);assert len(grid)==200 and all(len(c)==500 for c in grid)
 return i,j,grid

def free(grid,x,y):
 return x>=0 and y>=0 and x+16<=1600 and y+16<=4000 and all(grid[a][b]==0 for a in range(x//8,(x+15)//8+1) for b in range(y//8,(y+15)//8+1))

z=json.loads((ROOT/'game/Data/Zone/town02_waterfallvillage.json').read_text())['Object']['GroundMaps'];idx=json.loads((ROOT/'game/Data/Zone/index.idx').read_text())['Object']['town02_waterfallvillage']['Grounds'];assert z==idx and len(z)==23 and z[19:]==NAMES
city=(ROOT/'game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua').read_text(encoding='utf8');dev=(ROOT/'game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua').read_text(encoding='utf8');assert city==dev
pattern=r"\{nom='([^']+)', carte='([^']+)', x=(\d+),y=(\d+),w=(\d+),h=(\d+), destination='([^']+)', ax=(\d+),ay=(\d+),px=(\d+),py=(\d+),dir='(Up|Down)'\}"
found=re.findall(pattern,city);assert len(found)==len(GATES)
for parsed,expected in zip(found,GATES):
 _,src,x,y,w,h,dst,ax,ay,px,py,direction=parsed
 actual=(src,int(x),int(y),int(w),int(h),direction,dst,int(ax),int(ay),int(px),int(py))
 assert actual==expected,(actual,expected)
source=BASE.read_bytes();i,j,old=extract(source);assert len(source)==38012912 and hashlib.sha256(source).hexdigest()=='d954caf4ab769688ac573749d5f003b415c789b297b1c2fdc36deae0576f65a3'
asset=b'"AssetName":"WaterfallVillageCapital"';grids={}
for name in NAMES:
 data=gzip.decompress((ROOT/'payload'/f'{name}.rsground.gz').read_bytes());assert (hashlib.sha256(data).hexdigest(),len(data))==EXPECTED[name]
 a,b,grid=extract(data);assert data[:a]==source[:i] and ('"AssetName":"'+name+'"').encode() in data[b:]
 for x in range(200):
  for y in range(500):
   o=old[x][y];n=grid[x][y]
   assert n['Bounds']==o['Bounds']
   assert n['Tags']==(o['Tags'] if owner(x*8+4,y*8+4)==name else 1)
 grids[name]=[bytes(cell['Tags'] for cell in col) for col in grid]
 del grid,data
 wrapper=(ROOT/'game/Data/Script/destiny/ground'/name/'init.lua').read_text();assert "require 'destiny.ground.WaterfallVillageCapital.init'" in wrapper
print('PASS empreintes, zone et obstacles sans passage créé sur les quatre cartes')
# Contacter chaque capteur depuis son propre quartier, au départ du point
# d'arrivée du sens inverse. Un pas de 8 pixels ou de un pixel est conservateur.
for k,g in enumerate(GATES):
 src,x,y,w,h,dir,dst,ax,ay,px,py=g;inverse=GATES[k^1];assert inverse[0]==dst and inverse[6]==src
 assert free(grids[dst],ax,ay),(g,'arrivée héros')
 assert free(grids[dst],px,py),(g,'arrivée partenaire')
 assert abs(ax-px)>=16 or abs(ay-py)>=16,(g,'superposition')
 sx,sy=inverse[7:9]; assert free(grids[src],sx,sy),(g,'départ')
 # BFS au pas de 4 : les positions initiales sont multiples de 4.
 q=deque([(sx,sy)]);seen={(sx,sy)};found=False
 while q:
  u,v=q.popleft()
  touches_x=u<x+w and u+16>x
  if touches_x and ((dir=='Up' and v==y+h) or (dir=='Down' and v+16==y)):
   found=True;break
  for p in ((u+4,v),(u-4,v),(u,v+4),(u,v-4)):
   if p not in seen and free(grids[src],*p):seen.add(p);q.append(p)
 assert found,(g,'capteur inaccessible depuis le point de retour')
 print('PASS escalier',src,'→',dst,'depuis',sx,sy,'jusqu’au capteur',x,y)
if shutil.which('lua5.4'):
 subprocess.run(['lua5.4',str(ROOT/'tools/tests/test_quartiers_reverie.lua'),str(ROOT)],check=True)
else:print('Lua absent : test avec doublures ignoré')
