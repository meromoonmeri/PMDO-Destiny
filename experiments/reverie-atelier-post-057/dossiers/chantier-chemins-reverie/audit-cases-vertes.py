import numpy as np,json
from PIL import Image,ImageDraw,ImageFont
I=Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGB');im=np.array(I).astype(float);r,g,b=im[:,:,0],im[:,:,1],im[:,:,2];grass=(g>=r+1)&(g>=160)&(b<=135)&(r>=120);t=grass.reshape(500,8,200,8).mean((1,3));rgb=im.reshape(500,8,200,8,3).mean((1,3));d=[]
for y in range(1,499):
 for x in range(1,199):
  if t[y,x]<.85 or min(t[y-1,x],t[y+1,x],t[y,x-1],t[y,x+1])<.85:continue
  v=rgb[y,x];n=rgb[[y-1,y+1,y,y],[x,x,x-1,x+1]];dd=np.linalg.norm(n-v,axis=1)
  if min(dd)>3.2:d.append((round(min(dd),2),x*8,y*8))
d.sort(reverse=True);s=[]
for v in d:
 if all((v[1]-z[1])**2+(v[2]-z[2])**2>30**2 for z in s):s.append(v)
print(len(d),len(s),s[:50]);json.dump(s,open('candidats-cases-vertes.json','w'));f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13);o=Image.new('RGB',(5*220,((min(80,len(s))+4)//5)*185),'#202a2a');dr=ImageDraw.Draw(o)
for i,(v,x,y) in enumerate(s[:80]):
 ox=i%5*220;oy=i//5*185;dr.text((ox,oy),f'{i+1}: {x},{y} {v}',font=f,fill='white');o.paste(I.crop((x-25,y-25,x+33,y+33)).resize((162,162),Image.Resampling.NEAREST),(ox,oy+18))
o.save('candidats-cases-vertes.png')
