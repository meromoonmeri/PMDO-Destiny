from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2
p=Path(__file__).parent;r=p.parent
for d,base,polygon in [
 ('droite',r/'revision-corpulence/repos-trois-quart-01.png',[(415,795),(660,795),(675,870),(675,1085),(405,1110),(400,895)]),
 ('gauche',r/'Huit-directions/avant-gauche.png',[(295,760),(540,760),(560,805),(570,915),(570,1060),(300,1060),(295,900)])]:
 a=np.array(Image.open(base).convert('RGB'));b=np.array(Image.open(p/f'avant-{d}-02-v2-original.png').convert('RGB'));h,w=a.shape[:2];b=b[:h,:w]; x1,x2=int(w*.23),int(w*.77);y1,y2=80,int(h*.6);A=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)[y1:y2,x1:x2];B=cv2.cvtColor(b,cv2.COLOR_RGB2GRAY)[y1:y2,x1:x2];warp=np.eye(2,3,dtype='float32');score,warp=cv2.findTransformECC(A,B,warp,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,150,1e-6),None,5)
 M=warp.copy();M[0,2]+=x1-warp[0,0]*x1-warp[0,1]*y1;M[1,2]+=y1-warp[1,0]*x1-warp[1,1]*y1
 b=cv2.warpAffine(b,M,(w,h),flags=cv2.INTER_NEAREST|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)
 mask=Image.new('L',(w,h),0);ImageDraw.Draw(mask).polygon(polygon,fill=255);m=np.array(mask)>0;z=a.copy();z[m]=b[m];assert np.array_equal(z[~m],a[~m]);Image.fromarray(z).save(p/f'avant-{d}-02-retouche.png');print(d,'corrélation',round(score,5),'changements hors masque 0')
