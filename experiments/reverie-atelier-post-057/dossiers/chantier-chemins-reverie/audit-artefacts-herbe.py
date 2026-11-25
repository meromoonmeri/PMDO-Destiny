import cv2,numpy as np,json,math
from PIL import Image,ImageDraw,ImageFont
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB'));r=im[:,:,0].astype(int);g=im[:,:,1].astype(int);b=im[:,:,2].astype(int);green=(g>=r+1)&(g>=160)&(b<=135)&(r>=120);warm=((r>=216)&(g>=120)&(g<195)&(b>=72)&(b<145)&(r>g+25)).astype('uint8');n,lab,stats,_=cv2.connectedComponentsWithStats(warm,8);out=[]
for x,y,w,h,sz in stats[1:]:
 if not (2<=sz<=300 and w<=40 and h<=40 and x>8 and y>8 and x+w+8<1600 and y+h+8<4000):continue
 sub=green[y-5:y+h+5,x-5:x+w+5].copy();sub[5:5+h,5:5+w]=1
 if sub.mean()<.8:continue
 out.append([int(x),int(y),int(w),int(h),int(sz),round(float(sub.mean()),2)])
print('composantes',len(out));json.dump(out,open('artefacts-chauds-herbe.json','w'),indent=2);base=Image.fromarray(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for page in range(math.ceil(len(out)/50)):
 o=Image.new('RGB',(5*200,10*178),'#202a2a');d=ImageDraw.Draw(o)
 for i,(x,y,w,h,n,s) in enumerate(out[page*50:(page+1)*50]):
  ox=i%5*200;oy=i//5*178;d.text((ox,oy),f'{page*50+i+1}: {x},{y} ({w}x{h})',font=f,fill='white');o.paste(base.crop((x-20,y-20,x+30,y+30)).resize((150,150),Image.Resampling.NEAREST),(ox,oy+20))
 o.save(f'artefacts-chauds-{page+1:02}.png')
