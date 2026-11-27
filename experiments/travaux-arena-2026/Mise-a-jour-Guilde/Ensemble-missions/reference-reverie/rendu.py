import io,struct,json
from pathlib import Path
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent;b=(p/'Reverie_Inn_Base.tile').read_bytes();sz,n=struct.unpack_from('<ii',b);assert sz==8;bank={}
for i in range(n):
 x,y,off=struct.unpack_from('<iiq',b,8+16*i);z=struct.unpack_from('<q',b,off)[0];a=np.array(Image.open(io.BytesIO(b[off+8:off+8+z])).convert('RGBA'));v=a[...,3].astype(float);m=v>0
 for c in range(3):a[...,c][m]=np.minimum(255,np.rint(a[...,c][m].astype(float)*255/v[m])).astype('uint8')
 bank[x,y]=Image.fromarray(a)
o=json.load(open(p/'reverie_inn.rsground',encoding='utf-8-sig'))['Object'];l=o['Layers'][0];w,h=len(l['Tiles']),len(l['Tiles'][0]);im=Image.new('RGBA',(w*8,h*8))
for x,col in enumerate(l['Tiles']):
 for y,t in enumerate(col):
  for l2 in t['Layers']:
   fr=l2['Frames'][0];loc=fr['TexLoc'];tile=bank.get((loc['X'],loc['Y']))
   if tile:im.alpha_composite(tile,(x*8,y*8))
im.save(p/'Auberge-Reverie-rendu-natif.png');print(im.size,len(bank))
