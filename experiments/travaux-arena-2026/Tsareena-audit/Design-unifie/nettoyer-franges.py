from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import binary_propagation
p=Path(__file__).parent
im=np.array(Image.open(p/'Reprise-vues-PARTIEL.png').convert('RGBA')); before=im.copy(); counts=[]
for r in range(8):
 for c in range(4):
  a=im[r*112:(r+1)*112,c*64:(c+1)*64];v=a[:,:,:3].astype('int16');R,G,B=v[:,:,0],v[:,:,1],v[:,:,2];
  # Remove only low-chroma green-gray matte reachable from the exterior,
  # below the upper body, without modifying original generated sprites.
  halo=(a[:,:,3]>0)&(R>60)&(B>55)&(G>=R+4)&(G>=B+5)&((v.max(axis=2)-v.min(axis=2))<40)&(np.arange(112)[:,None]>=50)
  traversable=(a[:,:,3]==0)|halo
  seed=np.zeros((112,64),dtype=bool);seed[0,:]=traversable[0,:];seed[-1,:]=traversable[-1,:];seed[:,0]=traversable[:,0];seed[:,-1]=traversable[:,-1]
  reachable=binary_propagation(seed,mask=traversable);delete=reachable&halo
  counts.append(int(delete.sum()));a[delete,3]=0
Image.fromarray(im).save(p/'Reprise-vues-POLISH-ESSAI.png')
print('pixels retirés par cellule :',counts)
# reference comparison for local inspection
bg=(199,217,191);out=Image.new('RGB',(1024,448*2),bg)
for y,row in enumerate([1,4]):
 for f in range(2):
  data=before if f==0 else im
  for c in [0,1]:
   a=Image.fromarray(data[row*112:(row+1)*112,c*64:(c+1)*64]).resize((256,448),Image.Resampling.NEAREST);out.paste(a,(f*512+c*256,y*448),a)
out.save(p/'controle-franges-avant-apres.png')
