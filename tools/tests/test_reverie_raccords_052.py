#!/usr/bin/env python3
"""Non-destructive checks for the v0.5.2 Reverie visual fixes."""
from pathlib import Path
import gzip,io,struct,json,hashlib
import ijson
from PIL import Image
R=Path(__file__).resolve().parents[2]
names=['WaterfallVillageCapital','WaterfallVillageCapital_Dev','reverie_centre','reverie_centre_Dev','reverie_nord','reverie_nord_Dev','reverie_residentiel','reverie_residentiel_Dev','reverie_etang','reverie_etang_Dev']
banks={}
for name,n in [('Reverie_Herbe_Vagues_051',54),('Reverie_Rives_Sable_051',10)]:
 b=(R/'game/Content/Tile'/f'{name}.tile').read_bytes();size,count=struct.unpack_from('<ii',b);assert size==8 and count==n;index={}
 for i in range(n):
  x,y,off=struct.unpack_from('<iiq',b,8+i*16);length=struct.unpack_from('<q',b,off)[0];im=Image.open(io.BytesIO(b[off+8:off+8+length])).convert('RGBA');assert im.size==(8,8);index[(x,y)]=im
 banks[name]=index
hashes=[]
for name in names:
 file=R/'payload'/f'{name}.rsground.gz';raw=gzip.decompress(file.read_bytes());a=raw.index(b'"Layers":')+len(b'"Layers":');b=raw.index(b'"AssetName":',a)-1;hashes.append(hashlib.sha256(raw[a:b]).hexdigest())
 with gzip.open(file,'rb') as f:
  if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
  layers=list(ijson.items(f,'Object.Layers.item'))
 assert len(layers)==11
 obj=layers[6]['Tiles'];anim=layers[7]['Tiles'];over=layers[8]['Tiles']
 def first(x,y):return obj[x][y]['Layers'][0]['Frames'][0]
 assert first(94,154)=={'Sheet':'Reverie_Geo_08_Batiments_objets','TexLoc':{'X':109,'Y':137}}
 assert first(103,231)=={'Sheet':'Reverie_Geo_08_Batiments_objets','TexLoc':{'X':294,'Y':0}}
 assert first(22,14)=={'Sheet':'Reverie_Geo_08_Batiments_objets','TexLoc':{'X':235,'Y':56}}
 assert not obj[93][154] and not obj[102][231] and not obj[20][14]
 assert len(anim[93][154]['Layers'][0]['Frames'])==4
 assert len(anim[20][14]['Layers'][0]['Frames'])==7
 assert layers[2]['Tiles'][85][179]=={}
 used={k:0 for k in banks}
 for col in over:
  for cell in col:
   for seq in cell.get('Layers',[]):
    for fr in seq['Frames']:
     if fr['Sheet'] in banks:
      xy=fr['TexLoc'];assert (xy['X'],xy['Y']) in banks[fr['Sheet']];used[fr['Sheet']]+=1
 assert used=={'Reverie_Herbe_Vagues_051':65,'Reverie_Rives_Sable_051':10},(name,used)
 del layers,raw
assert len(set(hashes))==1
print('OK : 10 cartes, objets entiers, animations, retouches et banques v0.5.2.')
