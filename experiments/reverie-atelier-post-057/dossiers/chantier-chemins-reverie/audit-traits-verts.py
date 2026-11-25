import cv2,numpy as np,json,math
from PIL import Image,ImageDraw,ImageFont
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB'));r=im[:,:,0].astype(int);g=im[:,:,1].astype(int);b=im[:,:,2].astype(int);grass=(g>=r+1)&(g>=160)&(b<=130)&(r>=120);dark=((r>=120)&(r<183)&(g>=145)&(g<199)&(b>=35)&(b<=95)).astype('uint8');n,lab,stats,_=cv2.connectedComponentsWithStats(dark,8);out=[]
for x,y,w,h,sz in stats[1:]:
 if not (sz>=5 and x>6 and y>6 and x+w+6<1600 and y+h+6<4000 and ((w>=6 and h<=3) or (h>=6 and w<=3)) and w<=100 and h<=100):continue
 box=grass[y-5:y+h+5,x-5:x+w+5].copy();box[5:5+h,5:5+w]=1
 if box.mean()<.8:continue
 out.append([int(x),int(y),int(w),int(h),int(sz),round(float(box.mean()),2)])
print('candidats',len(out));json.dump(out,open('traits-verts-candidats.json','w'),indent=2);base=Image.fromarray(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for page in range(math.ceil(len(out)/50)):
 o=Image.new('RGB',(5*200,10*178),'#202a2a');d=ImageDraw.Draw(o)
 for i,(x,y,w,h,n,s) in enumerate(out[page*50:(page+1)*50]):
  ox=i%5*200;oy=i//5*178;d.text((ox,oy),f'{page*50+i+1}: {x},{y} ({w}x{h})',font=f,fill='white');o.paste(base.crop((x-20,y-20,x+30,y+30)).resize((150,150),Image.Resampling.NEAREST),(ox,oy+20))
 o.save(f'traits-verts-{page+1:02}.png')
