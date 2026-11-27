#!/usr/bin/env python3
"""Roches-Lames V2 : petites lames de pierre animées et textures Roche natives."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,math,io,struct,json
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Hurlement-des-Roches-Lames/Generation-PMDO'
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,c=struct.unpack_from('<iiii',b,8+k);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(c)]
def at(f,v,x,y):f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
a=np.asarray(Image.open(P/'source-v2-eclat-roche.png').convert('RGB'));r,g,b=[a[:,:,i].astype(int) for i in range(3)];mask=(g<np.maximum(r,b)*1.13)|(g<60);y,x=np.where(mask);rock=Image.fromarray(np.dstack((a,mask.astype('uint8')*255)),'RGBA').crop((x.min(),y.min(),x.max()+1,y.max()+1)).resize((12,21),Image.Resampling.NEAREST)
native_rocks=native('Rock_Piece_Rotating');edge=native('Stone_Edge_Rock');N=96;frames=[]
for t in range(64):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
 # Six pierres apparaissent à la suite, puis convergent ; variation de position à chaque image.
 for j in range(6):
  age=t-j*2
  if 0<=age<48:
   ang=j*math.tau/6;fade=min(1,(age+1)/5,(48-age)/7);dist=34 if age<18 else max(6,34-(age-18)*1.6);x=48+math.cos(ang)*dist;y=48+math.sin(ang)*dist*.72-3*math.sin(min(age,18)*math.pi/18)
   v=rock.rotate(-math.degrees(ang)-90,Image.Resampling.NEAREST,expand=True);v.putalpha(v.getchannel('A').point(lambda z:round(z*fade)));at(f,v,x,y)
  if 21<=age<41:
   ang=j*math.tau/6;dist=7+(age-21)*1.2;x=48+math.cos(ang)*dist;y=48+math.sin(ang)*dist*.72;v=native_rocks[(age//2+j)%len(native_rocks)];at(f,v,x,y)
 if 24<=t<34:
  rad=3+max(0,5-abs(t-28));d.line((48-rad,48,48+rad,48),fill=(255,240,188,255));d.line((48,48-rad,48,48+rad),fill=(255,240,188,255))
 frames.append(f)
s=Image.new('RGBA',(N*len(frames),N*8))
for row in range(8):
 for i,f in enumerate(frames):s.alpha_composite(f,(i*N,row*N))
b=io.BytesIO();s.save(b,format='PNG');png=b.getvalue();(P/'RochesLamesV2_Impact.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)))
z=json.loads((P/'splintered_stormshards-v1-test-only.json').read_text());fx=z['Object']['Data']['HitFX'];fx['Emitter']['Anim']['Anim']['AnimIndex']='RochesLamesV2_Impact';fx['Delay']=64;(P/'splintered_stormshards-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Banque 64 images et fiche de banc préparées.')
