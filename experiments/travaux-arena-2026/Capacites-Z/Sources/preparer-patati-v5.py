#!/usr/bin/env python3
"""Patati V5 : étoiles et yeux spiralés, puis sac opaque animé."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2,struct,io,math,json
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Patati-Patattrape/Generation-PMDO';V=P/'V5';N=128;T=120
def cut(name,dim):
 a=np.asarray(Image.open(V/'Sources'/name).convert('RGB'));r,g,b=[a[:,:,i].astype('int16') for i in range(3)];mask=(g>48)&(g>r*1.15)&(g>b*1.15);s=Image.fromarray(np.dstack((a,(~mask).astype('uint8')*255)),'RGBA');s=s.crop(s.getbbox());s.thumbnail(dim,Image.Resampling.NEAREST);return s
bag=cut('sac-ferme-oreilles-libres.png',(88,101)).resize((88,101),Image.Resampling.NEAREST); eyes=cut('yeux-spirale.png',(38,25));src=np.asarray(bag)
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,c=struct.unpack_from('<iiii',b,8+k);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(c)]
smoke=native('Smoke_Purple');stars=native('Lucky_Chant_Star_Yellow')
def paste(f,im,x,y,alpha=1):
 im=im.copy()
 if alpha<1:im.putalpha(im.getchannel('A').point(lambda q:round(q*max(0,alpha))))
 f.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))
charge=[]
for t in range(60):
 f=Image.new('RGBA',(N,N));fade=min(1,(t+1)/8,(60-t)/10);pulse=1+.06*math.sin(t*.45);v=eyes.resize((round(eyes.width*pulse),round(eyes.height*pulse)),Image.Resampling.NEAREST);paste(f,v,64,43,fade)
 for j in range(4):
  age=(t+j*6)%24;v=stars[min(len(stars)-1,age//3)].resize((11,11),Image.Resampling.NEAREST);x=64+math.cos(j*math.tau/4+t*.035)*27;y=44+math.sin(j*math.tau/4+t*.035)*17;paste(f,v,x,y,fade)
 charge.append(f)
impact=[]
for t in range(T):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f);enter=min(1,(t+1)/14);end=min(1,(T-t)/12)
 if t<111:
  d.ellipse((25,80,103,101),fill=(13,5,22,round(235*end)),outline=(100,44,130,round(170*end)),width=2)
  for j in range(4):
   age=(t+j*8)%32;v=smoke[min(len(smoke)-1,age//3)].resize((13,13),Image.Resampling.NEAREST);paste(f,v,41+j*15,91-age*.32,.35*end)
 if t<108:
  amp=1 if 20<=t<90 else .2;y,x=np.indices((101,88),dtype=np.float32);lower=np.clip((y-30)/71,0,1)
  mx=x+(1+3.5*amp*lower)*np.sin(y*.10+t*.40)+1.3*amp*np.sin(t*.27);my=y+1.8*amp*lower*np.sin(x*.14+t*.3)
  deform=Image.fromarray(cv2.remap(src,mx.astype('float32'),my.astype('float32'),cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0)),'RGBA')
  scale=.78+.22*enter;squash=1+(.07*math.sin((t-20)*.60) if 20<=t<90 else 0);w=round(88*scale*squash);h=round(99*scale/squash);deform=deform.resize((w,h),Image.Resampling.NEAREST);cx=64+(3*math.sin(t*.5) if 20<=t<90 else 0);cy=53-18*(1-enter)+(2*math.sin(t*.7) if 20<=t<90 else 0);paste(f,deform,cx,cy,min(1,(108-t)/9))
 if 30<=t<90:
  for j in range(2):
   age=(t-30-j*12)%25
   if age<15:
    v=stars[min(len(stars)-1,age//2)].resize((12,12),Image.Resampling.NEAREST);paste(f,v,22+j*84,60+math.sin(t*.2+j)*8,min(1,(15-age)/4))
 impact.append(f)
def output(frames,name):
 n=len(frames);sheet=Image.new('RGBA',(N*8,N*((n+7)//8)));bank=Image.new('RGBA',(N*n,N*8))
 for i,f in enumerate(frames):
  sheet.alpha_composite(f,((i%8)*N,(i//8)*N))
  for j in range(8):bank.alpha_composite(f,(i*N,j*N))
 sheet.save(V/(name+'-planche.png'),optimize=True);b=io.BytesIO();bank.save(b,format='PNG',optimize=True);raw=b.getvalue();(V/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,n))
output(charge,'PatatiV5_Yeux');output(impact,'PatatiV5_Sac')
z=json.loads((P/'V4/lets_snuggle_forever-v4-test-only.json').read_text());d=z['Object']['Data'];d['BeforeHits'][0]['Value']['Script']='PatatiV5_Sac';d['OnHits'][-1]['Value']['Script']='PatatiV5_ChanceKO';(V/'lets_snuggle_forever-v5-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Yeux : 60 images ; sac fermé : 120 images ; banques de test prêtes.')
