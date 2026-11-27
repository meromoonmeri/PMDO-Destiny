from PIL import Image
import numpy as np,cv2
from pathlib import Path
p=Path(__file__).parent;a=np.array(Image.open(p.parent/'Huit-directions/avant-gauche.png').convert('RGB'));h,w=a.shape[:2];y,x=np.indices((h,w))
for f,filename in [(2,'pas-gauche-02-brut.png'),(4,'pas-gauche-04-v2-brut.png')]:
 b=Image.open(p/filename).convert('RGB');
 if b.height==h-4:
  z=Image.new('RGB',(w,h),b.getpixel((0,0)));z.paste(b,(0,0));b=z
 b=np.asarray(b);assert a.shape==b.shape
 roi=(x>290)&(x<610)&(y>=758)&(y<1060)
 def red(z):
  r,g,b=[z[:,:,i].astype('int16') for i in range(3)];return (r>95)&(r>g*1.45)&(r>b*1.20)&roi
 core=(red(a)|red(b)).astype('uint8');m=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_RECT,(31,31)))>0;m&=roi
 out=a.copy();out[m]=b[m];Image.fromarray(out).save(p/f'pas-gauche-{f:02}-local.png');Image.fromarray((m*255).astype('uint8')).save(p/f'masque-local-{f:02}.png');print(f,'outside diff',np.any(out[~m]!=a[~m]))
