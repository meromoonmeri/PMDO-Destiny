#!/usr/bin/env python3
"""Patati V2 : déploiement, fermeture, secousses puis impact Fée."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,cv2,math,struct,io,json
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Patati-Patattrape/Generation-PMDO';V=P/'V2';V.mkdir(parents=True,exist_ok=True);N=128;T=112
im=Image.open(V/'Sources/tissu.png').convert('RGB');a=np.array(im);r,g,b=[a[:,:,i].astype('int16') for i in range(3)];m=((g>65)&(g>r*1.2)&(g>b*1.2));raw=Image.fromarray(np.dstack((a,(~m).astype('uint8')*255)),'RGBA');raw=raw.crop(raw.getbbox()).resize((62,68),Image.Resampling.NEAREST)
# Les textures natives de Câlinerie apparaissent au contact.
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();l=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+l])).convert('RGBA');w,h,_,c=struct.unpack_from('<iiii',b,8+l);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(c)]
stars=native('Lucky_Chant_Star_Yellow');smoke=native('Smoke_White');heart=native('Charm')
def paste(f,i,x,y,fade=1):
 i=i.copy()
 if fade<1:i.putalpha(i.getchannel('A').point(lambda q:round(q*max(0,fade))))
 f.alpha_composite(i,(round(x-i.width/2),round(y-i.height/2)))
frames=[]
for t in range(T):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
 # Deux pans s'élargissent, puis se croisent et cachent le centre.
 if t<34:
  p=min(1,t/13);close=max(0,(t-15)/19);l=64-48*p;rr=64+48*p;top=43-12*p;bottom=69+8*p
  for side in (-1,1):
   far=64+side*48*p;near=64+side*(6+12*(1-close));outer=far-side*22*close
   poly=[(64+side*8,45),(64+side*19,top),(outer,top+3),(far,bottom-2),(64+side*21,bottom+8),(near,71),(64+side*5,59)]
   d.polygon(poly,fill=(235,213,150,255),outline=(76,55,38,255),width=2)
   d.line([(64+side*17,top+4),(64+side*29,58),(64+side*20,72)],fill=(187,158,99,255),width=2)
 # Une étoffe déformée image par image, non une pose de personnage agrandie.
 if 21<=t<94:
  enter=min(1,(t-20)/15);fade=min(1,(94-t)/8);shrink=1-.10*math.sin((t-48)*.65) if 48<=t<81 else 1
  src=np.asarray(raw);y,x=np.indices((68,62),dtype=np.float32)
  dx=(1.8+2.4*(t>=34))*np.sin(y/10+t*.36);dy=1.5*np.sin(x/10+t*.24)
  distorted=cv2.remap(src,x+dx, y+dy,cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
  cloth=Image.fromarray(distorted,'RGBA');ww=max(1,round((35+27*enter)*shrink));hh=max(1,round(17+51*enter));cloth=cloth.resize((ww,hh),Image.Resampling.NEAREST)
  sway=(math.sin(t*.52)*3 if 35<=t<82 else 0);bob=(math.sin(t*.71)*2 if 48<=t<81 else 0);paste(f,cloth,64+sway,61+bob,fade)
  if enter>.75:
   d=ImageDraw.Draw(f);ox=round(sway);oy=round(bob);col=(62,42,31,round(255*fade));blush=(214,121,109,round(255*fade))
   d.rectangle((52+ox,47+oy,55+ox,50+oy),fill=col);d.rectangle((72+ox,47+oy,75+ox,50+oy),fill=col)
   d.line([(55+ox,56+oy),(59+ox,58+oy),(63+ox,55+oy),(67+ox,58+oy),(72+ox,56+oy)],fill=col,width=2)
   d.rectangle((47+ox,53+oy,50+ox,54+oy),fill=blush);d.rectangle((77+ox,53+oy,80+ox,54+oy),fill=blush)
 # Petits coups et éclats natifs Fée pour marquer l'étreinte, sans dégâts multiples.
 if 45<=t<92:
  for j in range(3):
   age=t-45-j*11
   if 0<=age<25:
    x=64+(-1 if j%2 else 1)*(30+age*.65);y=63+((-1)**j)*13-age*.3
    v=stars[min(len(stars)-1,age//3)].resize((14,14),Image.Resampling.NEAREST);paste(f,v,x,y,min(1,(25-age)/5))
 if t>=82:
  age=t-82
  for j in range(6):
   dx=math.cos(j*math.tau/6)*(15+age*.8);dy=math.sin(j*math.tau/6)*(10+age*.45);v=smoke[min(len(smoke)-1,age//2)].resize((20,20),Image.Resampling.NEAREST);paste(f,v,64+dx,66+dy,min(1,(T-t)/10))
  if age<23:
   v=heart[min(len(heart)-1,age)].resize((27,27),Image.Resampling.NEAREST);paste(f,v,64,52,min(1,(23-age)/6))
 frames.append(f)
s=Image.new('RGBA',(N*T,N*8));sheet=Image.new('RGBA',(N*8,N*14))
for row in range(8):
 for i,f in enumerate(frames):s.alpha_composite(f,(i*N,row*N))
for i,f in enumerate(frames):sheet.alpha_composite(f,((i%8)*N,(i//8)*N))
sheet.save(V/'Patati-V2-tissu-impact-112images.png',optimize=True)
b=io.BytesIO();s.save(b,format='PNG',optimize=True);png=b.getvalue();(V/'PatatiV2_Impact.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,T))
z=json.loads((P/'lets_snuggle_forever-v1-test-only.json').read_text());fx=z['Object']['Data']['HitFX'];fx['Emitter']['Anim']['Anim']['AnimIndex']='PatatiV2_Impact';fx['Delay']=T;(V/'lets_snuggle_forever-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('112 images préparées ; banque et fiche de banc créées.')
