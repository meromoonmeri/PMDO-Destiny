import io,struct,json
from pathlib import Path
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent;banks={}
for path in p.glob('*.tile'):
 b=path.read_bytes();size,n=struct.unpack_from('<ii',b);bank={}
 for i in range(n):
  x,y,off=struct.unpack_from('<iiq',b,8+16*i);z=struct.unpack_from('<q',b,off)[0];a=np.array(Image.open(io.BytesIO(b[off+8:off+8+z])).convert('RGBA'));alpha=a[...,3].astype(float);m=alpha>0
  for c in range(3):a[...,c][m]=np.minimum(255,np.rint(a[...,c][m].astype(float)*255/alpha[m])).astype('uint8')
  bank[x,y]=Image.fromarray(a)
 banks[path.stem]=bank
 print(path.name,len(bank),max(x for x,y in bank),max(y for x,y in bank))
 out=Image.new('RGBA',((max(x for x,y in bank)+1)*8,(max(y for x,y in bank)+1)*8))
 for (x,y),tile in bank.items():out.alpha_composite(tile,(x*8,y*8))
 out.save(p/(path.stem+'-planche.png'))
o=json.load(open(p/'reverie_fire_home.rsground',encoding='utf-8-sig'))['Object'];w,h=len(o['Layers'][0]['Tiles']),len(o['Layers'][0]['Tiles'][0]);print('size',w,h)
for frame in range(6):
 im=Image.new('RGBA',(w*8,h*8))
 for layer in o['Layers']:
  for x,col in enumerate(layer['Tiles']):
   for y,t in enumerate(col):
    for l in t['Layers']:
     fr=l['Frames'][frame%len(l['Frames'])];loc=fr['TexLoc'];tile=banks[fr['Sheet']].get((loc['X'],loc['Y']))
     if tile: im.alpha_composite(tile,(x*8,y*8))
 im.save(p/f'fire-house-frame-{frame+1:02}.png')
