from pathlib import Path
import numpy as np,cv2
from PIL import Image
p=Path(__file__).parent; src=p.parent/'revision-corpulence/repos-trois-quart-01.png';a=np.array(Image.open(src).convert('RGB'));r,g,b=[a[:,:,i].astype(int) for i in range(3)]; y,x=np.indices(r.shape)
red=((r>95)&(r>g*1.55)&(r>b*1.28)&(y>780)&(y<1060)&(x>410)&(x<650)).astype('uint8'); n,labels,stats,_=cv2.connectedComponentsWithStats(red,8)
comps=sorted(range(1,n),key=lambda i:stats[i,4],reverse=True)[:2]
for no,c in enumerate(comps):
 core=(labels==c).astype('uint8');m=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_RECT,(29,29)));m[y<790]=0
 # Clear residual tip outline below the robe, within the local edit region.
 if no==0: m[950:1074,412:473]=1
 else: m[950:1045,531:591]=1
 # Preserve costume outside the neighborhood around the leg.
 patchmask=(m*255).astype('uint8'); clean=cv2.inpaint(a,patchmask,15,cv2.INPAINT_TELEA)
 # Below the hem, replace the exposed region with the sampled flat background.
 bg=a[1100,700].copy(); clean[(m>0)&(y>=950)]=bg
 # raise lower part, leaving root fixed; motion test only
 H,W=red.shape; yy,xx=np.indices((H,W),dtype='float32'); root=790.; scale=.78
 mapy=(yy-root)/scale+root; mapx=xx
 warped=cv2.remap(a,mapx,mapy,cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(204,220,192)); wm=cv2.remap(patchmask,mapx,mapy,cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
 out=clean.copy();out[wm>0]=warped[wm>0]
 # Retouche ciblée : suppression du résidu noir détaché en bas de la jambe gauche.
 if no==0: out[951:986,480:502]=bg
 Image.fromarray(out).save(p/f'essai-manuel-jambe-{no+1}.png')
