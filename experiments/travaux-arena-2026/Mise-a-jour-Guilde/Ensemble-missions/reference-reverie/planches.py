import io,struct
from pathlib import Path
from PIL import Image
import numpy as np
p=Path(__file__).resolve().parent
for path in p.glob('*.tile'):
 if path.stem.endswith('Base'):continue
 b=path.read_bytes();sz,n=struct.unpack_from('<ii',b);entries=[]
 for i in range(n):
  x,y,off=struct.unpack_from('<iiq',b,8+16*i);z=struct.unpack_from('<q',b,off)[0];a=np.array(Image.open(io.BytesIO(b[off+8:off+8+z])).convert('RGBA'));v=a[...,3].astype(float);m=v>0
  for c in range(3):a[...,c][m]=np.minimum(255,np.rint(a[...,c][m].astype(float)*255/v[m])).astype('uint8')
  entries.append((x,y,Image.fromarray(a)))
 print(path.stem,sz,n,'coords',min(x for x,y,_ in entries),max(x for x,y,_ in entries),min(y for x,y,_ in entries),max(y for x,y,_ in entries))
 out=Image.new('RGBA',((max(x for x,y,_ in entries)+1)*8,(max(y for x,y,_ in entries)+1)*8))
 for x,y,im in entries:out.alpha_composite(im,(8*x,8*y))
 out.save(p/(path.stem+'-planche.png'))
