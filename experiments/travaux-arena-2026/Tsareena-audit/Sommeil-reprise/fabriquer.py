from PIL import Image
from pathlib import Path
import numpy as np, cv2, hashlib
p=Path(__file__).parent; source=p.parent/'revision-corpulence/Sommeil-fidele-00.png'; a=np.array(Image.open(source).convert('RGB'));h,w=a.shape[:2];y,x=np.indices((h,w),dtype='float32')
# Pose 2 : légère inclinaison verticale en faisant descendre le haut,
# puis transition progressive vers les jambes conservées en place.
d=14*np.clip((710-y)/220,0,1); mapy=y-d
frame=cv2.remap(a,x,mapy,cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=tuple(map(int,a[0,0])))
Image.fromarray(frame).save(p/'sommeil-02-provisoire.png')
print('dimensions',w,h,'SHA original',hashlib.sha256(source.read_bytes()).hexdigest());print('pixels changés sous y=710 :',np.count_nonzero(np.any(frame[710:]!=a[710:],axis=2)))
