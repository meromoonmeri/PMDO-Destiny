import numpy as np, cv2
from PIL import Image,ImageDraw
im=np.array(Image.open('reverie-057-phase0.png').convert('RGB'));h,w=im.shape[:2];a=im.astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
water=(r<170)&(g>150)&(b>150)&(b>r+25);grass=(r>130)&(r<235)&(g>150)&(g<235)&(b<130)&(g>r-25)
wl=cv2.boxFilter(water.astype('float32'),-1,(5,48),normalize=True);gr=cv2.boxFilter(grass.astype('float32'),-1,(5,48),normalize=True)
result=[]
for y in range(40,h-80,16):
 for x in range(32,w-40,8):
  if not (wl[y+24,x-16]>.95 and gr[y+24,x+15]>.93):continue
  sub=grass[y:y+48,x-12:x+13];first=np.argmax(sub,axis=1);valid=sub.any(axis=1)
  if valid.sum()<46:continue
  vals=first[valid];v=int(vals.max()-vals.min());changes=int(np.count_nonzero(np.diff(vals)))
  if 3<=v<=10 and changes>=4:
   result.append((v,changes,x,y, round(float(wl[y+24,x-16]),2),round(float(gr[y+24,x+15]),2)))
result.sort(reverse=True);r=[]
for z in result:
 if all(abs(z[2]-a[2])>40 or abs(z[3]-a[3])>60 for a in r):r.append(z)
 if len(r)>=20:break
print(r)
big=Image.fromarray(im);o=Image.new('RGB',(480, len(r)*110),'white');d=ImageDraw.Draw(o)
for i,(_,_,x,y,*_) in enumerate(r):
 d.text((0,i*110),str(r[i]),fill='black');tile=big.crop((x-24,y-4,x+32,y+52)).resize((168,168),Image.Resampling.NEAREST);tile.thumbnail((95,95));o.paste(tile,(300,i*110+15))
o.save('rives-candidates.png')
