import numpy as np,cv2
from PIL import Image
im=np.asarray(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB')).astype('int16');r,g,b=im[:,:,0],im[:,:,1],im[:,:,2];grass=(g>r+3)&(g>160)&(b<145)&(r>110);sand=(r>220)&(r>g+8)&(g>160)&(b>85)&(b<190)
out=[]
for y in range(8,im.shape[0]-16,8):
 for x in range(8,im.shape[1]-16,8):
  p=grass[y:y+8,x:x+8]; ring=sand[y-3:y+11,x-3:x+11].copy();ring[3:11,3:11]=0
  if p.mean()>.92 and ring.sum()>90:out.append((x,y,p.mean(),ring.sum()))
print(out)
