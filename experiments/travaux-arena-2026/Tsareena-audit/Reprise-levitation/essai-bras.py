from PIL import Image
from pathlib import Path
import numpy as np,cv2
p=Path(__file__).parent;im=np.array(Image.open(p/'essai-manuel-jambe-1.png').convert('RGB')); y,x=np.indices(im.shape[:2]);r,g,b=[im[:,:,i].astype(int) for i in range(3)]
red=((r>100)&(r>g*1.5)&(r>b*1.3)&(x>285)&(x<475)&(y>515)&(y<720)); n,lab,stats,_=cv2.connectedComponentsWithStats(red.astype('uint8'),8)
idx=[j for j in range(1,n) if stats[j,4]>500];core=np.isin(lab,idx).astype('uint8');mask=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_RECT,(21,21)))*255
clean=cv2.inpaint(im,mask,10,cv2.INPAINT_TELEA)
h,w=red.shape;yy,xx=np.indices((h,w),dtype='float32');displacement=np.maximum(0,np.minimum(1,(470-xx)/180))*10
# Shift the wrist end upwards, pivoting near shoulder.
mapy=yy+displacement;warped=cv2.remap(im,xx,mapy,cv2.INTER_NEAREST);wm=cv2.remap(mask,xx,mapy,cv2.INTER_NEAREST);clean[wm>0]=warped[wm>0]
Image.fromarray(clean).save(p/'essai-bras-non-valide.png')
