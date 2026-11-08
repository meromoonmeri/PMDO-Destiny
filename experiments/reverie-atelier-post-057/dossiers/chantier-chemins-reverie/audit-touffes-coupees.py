import numpy as np,cv2,math,json
from PIL import Image,ImageDraw,ImageFont
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB'));donor=im[2240:2248,336:352];out=[]
for side in ('gauche','droite'):
 template=donor[:,:8] if side=='gauche' else donor[:,8:];res=cv2.matchTemplate(im,template,cv2.TM_SQDIFF_NORMED);ys,xs=np.where(res<1e-7)
 for x,y in zip(xs,ys):
  x=int(x)-(8 if side=='droite' else 0);y=int(y)
  if x<0 or x+16>=1600 or y+8>=4000:continue
  t=im[y:y+8,x:x+16];dif=np.any(t!=donor,axis=2);changes=int(dif.sum());half=dif[:,:8] if side=='droite' else dif[:,8:]
  if 5<=changes<=50:
   out.append((x,y,side,changes))
out=sorted(set(out),key=lambda a:(a[1],a[0]));print('candidats',len(out),out[:100]);json.dump(out,open('touffes-candidates.json','w'))
if out:
 f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);o=Image.new('RGB',(5*200,math.ceil(len(out)/5)*158),'#202a2a');d=ImageDraw.Draw(o);base=Image.fromarray(im)
 for i,(x,y,side,n) in enumerate(out):
  ox=i%5*200;oy=i//5*158;d.text((ox,oy),f'{i+1}: {x},{y} {side[0]} {n}',font=f,fill='white');o.paste(base.crop((x-16,y-14,x+32,y+26)).resize((144,120),Image.Resampling.NEAREST),(ox,oy+19))
 o.save('touffes-candidates.png')
