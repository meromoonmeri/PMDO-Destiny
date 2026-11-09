from pathlib import Path
import ijson,io,struct
from PIL import Image
R=Path('metano-reference'); cache={};sheets={};im=Image.new('RGBA',(1512,1512))
def get(f):
 name=f['Sheet'];x=f['TexLoc']['X'];y=f['TexLoc']['Y'];k=(name,x,y)
 if not name:return None
 if k in cache:return cache[k]
 if name not in sheets:
  p=R/'Content/Tile'/(name+'.tile')
  if not p.exists():return None
  b=p.read_bytes();_,n=struct.unpack_from('<ii',b);d={}
  for i in range(n):
   a,c,o=struct.unpack_from('<iiq',b,8+16*i);d[(a,c)]=o
  sheets[name]=(b,d)
 b,d=sheets[name];o=d[(x,y)];n=struct.unpack_from('<q',b,o)[0];cache[k]=Image.open(io.BytesIO(b[o+8:o+8+n])).convert('RGBA');return cache[k]
with open(R/'Data/Ground/metano_town.rsground','rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for i,l in enumerate(ijson.items(f,'Object.Layers.item')):
  if i>1:break
  for x,col in enumerate(l['Tiles']):
   for y,c in enumerate(col):
    for anim in c.get('Layers',[]):
     if anim['Frames']:
      p=get(anim['Frames'][0]);
      if p: im.alpha_composite(p,(8*x,8*y))
im.save('metano-reference-sol-falaises.png');im.resize((756,756),Image.Resampling.NEAREST).save('metano-reference-reduit.png')
