import numpy as np,cv2,math,json
from PIL import Image,ImageDraw,ImageFont
im=np.asarray(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB'));r=im[:,:,0].astype(int);g=im[:,:,1].astype(int);b=im[:,:,2].astype(int);green=((g>=r+1)&(g>=150)&(b<125)&(r>=100)).astype('uint8');sand=(r>=224)&(g>=175)&(b>=96)&(r>g+4)
n,lab,stat,cent=cv2.connectedComponentsWithStats(green,8);out=[]
for x,y,w,h,sz in stat[1:]:
 if sz>40 or w>8 or h>8 or sz<1:continue
 if x<8 or y<8 or x+w+8>=1600 or y+h+8>=4000:continue
 rect=sand[y-5:y+h+5,x-5:x+w+5].copy();rect[5:5+h,5:5+w]=1
 if rect.mean()<.92:continue
 out.append([int(x),int(y),int(w),int(h),int(sz),round(float(rect.mean()),2)])
print('candidats',len(out));json.dump(out,open('petits-artefacts.json','w'))
base=Image.fromarray(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for page in range(math.ceil(len(out)/60)):
 o=Image.new('RGB',(6*160,10*146),'#202a2a');d=ImageDraw.Draw(o)
 for i,(x,y,w,h,n,s) in enumerate(out[page*60:(page+1)*60]):
  ox=i%6*160;oy=i//6*146;cro=base.crop((x-20,y-20,x+28,y+28)).resize((128,128),Image.Resampling.NEAREST);o.paste(cro,(ox,oy+17));d.text((ox,oy),f'{page*60+i+1}: {x},{y}',font=f,fill='white')
 o.save(f'petits-artefacts-{page+1:02}.png')
