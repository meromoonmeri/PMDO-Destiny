import cv2,numpy as np
from PIL import Image,ImageDraw
im=np.array(Image.open('reverie-057-phase0.png').convert('RGB'));base=np.array(Image.open('calques/01_Base.png').convert('RGBA'));skip=np.zeros(base.shape[:2],np.uint8)
for name in ['02_Cliffs','03_River','05_Objects_Under','07_Objects','08_Objects_Anim','09_Objects_Over']:
 skip=np.maximum(skip,np.array(Image.open('calques/'+name+'.png').convert('RGBA'))[:,:,3])
img=cv2.cvtColor(im,cv2.COLOR_RGB2BGR);temp=img[614:630,1412:1492];res=cv2.matchTemplate(img,temp,cv2.TM_CCOEFF_NORMED);opts=[]
for _ in range(500):
 _,v,_,(x,y)=cv2.minMaxLoc(res);cv2.rectangle(res,(max(0,x-16),max(0,y-30)),(x+16,y+30),-1,-1)
 # donor patch x..x+80 and y-28..y+16; avoid same site and borders
 if v<0.84:break
 if y<28 or (abs(x-1412)<100 and abs(y-614)<100):continue
 ss=skip[y-28:y+16,x:x+80]
 if ss.size!=44*80 or np.count_nonzero(ss)>15:continue
 # Most center must be sand; margins mostly grass at top
 r=im[y-28:y,x:x+80];sand=(r[:,:,0]>210)&(r[:,:,1]>150)&(r[:,:,2]<170);grass=(r[:,:,0]>140)&(r[:,:,1]>160)&(r[:,:,2]<135)
 if sand[:,28:52].mean()<.9 or grass[:12,:6].mean()<.65 or grass[:12,-6:].mean()<.65:continue
 opts.append((v,x,y-28))
 if len(opts)>=16:break
print('candidates',opts)
out=Image.new('RGB',(600,((len(opts)+2)//3)*180),(35,35,35));d=ImageDraw.Draw(out)
for i,(score,x,y) in enumerate(opts):
 x0=(i%3)*200;y0=(i//3)*180;d.text((x0,y0),f'{score:.3f} ({x},{y})',fill='white');a=Image.fromarray(im[y:y+44,x:x+80]);a=a.resize((160,88),Image.Resampling.NEAREST);out.paste(a,(x0,y0+20))
out.save('donneurs-chemin51.png')
