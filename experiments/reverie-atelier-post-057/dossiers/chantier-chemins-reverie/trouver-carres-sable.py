from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,math
im=np.asarray(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB'));h,w=im.shape[:2];r,g,b=im[:,:,0].astype(int),im[:,:,1].astype(int),im[:,:,2].astype(int);pale=(r==248)&(g==216)&(b==152);dark=(r>220)&(r>g+5)&(g>=176)&(g<=208)&(b>95)&(b<=144);sand=(r>=224)&(g>=176)&(b>=96)&(r>g);out=[]
for y in range(16,h-24,8):
 for x in range(16,w-24,8):
  area=dark[y:y+8,x:x+8].sum();valid=sand[y:y+8,x:x+8].sum();rings=np.r_[pale[y-8:y,x:x+8].ravel(),pale[y+8:y+16,x:x+8].ravel(),pale[y:y+8,x-8:x].ravel(),pale[y:y+8,x+8:x+16].ravel()];
  if area>=14 and valid>=58 and rings.sum()>=200:out.append((x,y,int(area),int(rings.sum())))
print('candidats',len(out));out.sort(key=lambda i:-(i[2]*i[3]));json.dump(out,open('carres-sable-candidats.json','w'))
base=Image.fromarray(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for page in range(math.ceil(len(out)/60)):
 o=Image.new('RGB',(6*160,10*146),'#202a2a');d=ImageDraw.Draw(o)
 for i,(x,y,n,s) in enumerate(out[page*60:(page+1)*60]):
  ox=i%6*160;oy=i//6*146;cro=base.crop((x-20,y-20,x+28,y+28)).resize((128,128),Image.Resampling.NEAREST);o.paste(cro,(ox,oy+17));d.text((ox,oy),f'{page*60+i+1}: {x},{y}',font=f,fill='white')
 o.save(f'carres-sable-{page+1:02}.png')
