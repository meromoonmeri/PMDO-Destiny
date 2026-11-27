from pathlib import Path
from PIL import Image
import numpy as np,cv2
p=Path(__file__).parent;r=p.parent
for name,path,x0,x1,y0,y1 in [('droite',r/'revision-corpulence/repos-trois-quart-01.png',270,720,515,730),('gauche',r/'Huit-directions/avant-gauche.png',235,690,505,720)]:
 a=np.array(Image.open(path).convert('RGB'));b=np.array(Image.open(p/f'repos-02-{name}-brut.png').convert('RGB'));assert a.shape==b.shape
 h,w=a.shape[:2];y,x=np.indices((h,w));roi=(x>x0)&(x<x1)&(y>y0)&(y<y1)
 def red(z):
  rr,gg,bb=[z[:,:,i].astype('int16') for i in range(3)];return (rr>95)&(rr>gg*1.45)&(rr>bb*1.20)&roi
 core=(red(a)|red(b)).astype('uint8');m=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_RECT,(29,29)))>0;m &=roi
 # The original face and silhouette stay untouched; preserve original green hair/leaf areas unless new arms overlay them.
 rr,gg,bb=[a[:,:,i].astype('int16') for i in range(3)];green=(gg>rr*1.10)&(gg>bb*1.2)&(gg>80);m &= (~green | red(b))
 out=a.copy();out[m]=b[m]
 Image.fromarray(out).save(p/f'repos-02-{name}-local.png');Image.fromarray((m*255).astype('uint8')).save(p/f'masque-local-{name}.png');print(name,'changed outside',np.any(out[~m]!=a[~m]))
