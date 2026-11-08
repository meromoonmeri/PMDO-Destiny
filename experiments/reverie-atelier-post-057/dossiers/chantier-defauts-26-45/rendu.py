from pathlib import Path
R=Path('/home/user/chantier-defauts-26-45');D=R/'base'
from PIL import Image
import gzip,ijson,struct,io,re
sheets={};cache={};comp=Image.new('RGBA',(1600,4000));DOUT=R/'calques';DOUT.mkdir(exist_ok=True)
def tile(fr):
 name=fr.get('Sheet','');xy=fr['TexLoc'];key=(name,xy['X'],xy['Y'])
 if not name:return None
 if key in cache:return cache[key]
 if name not in sheets:
  b=(D/'game/Content/Tile'/f'{name}.tile').read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8
  idx={struct.unpack_from('<iiq',b,8+16*i)[:2]:struct.unpack_from('<iiq',b,8+16*i)[2] for i in range(n)};sheets[name]=(b,idx)
 b,idx=sheets[name];off=idx[(xy['X'],xy['Y'])];length=struct.unpack_from('<q',b,off)[0];im=Image.open(io.BytesIO(b[off+8:off+8+length])).convert('RGBA');cache[key]=im;return im
with gzip.open(D/'payload/reverie_centre.rsground.gz','rb') as f:
 if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
 for i,l in enumerate(ijson.items(f,'Object.Layers.item')):
  piece=Image.new('RGBA',(1600,4000));count=0
  for x,col in enumerate(l['Tiles']):
   for y,cell in enumerate(col):
    for anim in cell.get('Layers',[]):
     frames=anim.get('Frames',[])
     if frames:
      im=tile(frames[0])
      if im is not None:piece.alpha_composite(im,(8*x,8*y));comp.alpha_composite(im,(8*x,8*y));count+=1
  safe=re.sub('[^A-Za-z0-9]+','_',l['Name']).strip('_');piece.save(DOUT/f'{i+1:02}_{safe}.png');print('Calque',i+1,l['Name'],count,flush=True)
comp.save(R/'reverie-055-phase0.png');print('Rendu terminé',list(sheets),flush=True)
