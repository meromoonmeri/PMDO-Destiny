#!/usr/bin/env python3
"""Reprise des deux attaques électriques à partir des animations natives PMDO."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,copy,io,struct,math
import numpy as np
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';R=H/'Capacites-Z/Prototypes';E=R/'Electro-Surf-Survolte/Generation-PMDO';P=R/'Giga-Tonnerre/Generation-PMDO'
def particle(name):
 raw=(G/'Content/Particle'/f'{name}.dir').read_bytes();n=struct.unpack_from('<q',raw)[0];img=Image.open(io.BytesIO(raw[8:8+n])).convert('RGBA');w,h,_,ct=struct.unpack_from('<iiii',raw,8+n);return [img.crop((w*i,0,w*(i+1),h)) for i in range(ct)]
def source(path,sz):
 a=np.asarray(Image.open(path).convert('RGB'));r,g,b=a[:,:,0].astype(int),a[:,:,1].astype(int),a[:,:,2].astype(int); mask=(g<1.18*np.maximum(r,b))|(g<70); y,x=np.where(mask);q=np.dstack((a,(mask*255).astype('uint8')));return Image.fromarray(q,'RGBA').crop((x.min(),y.min(),x.max()+1,y.max()+1)).resize((sz,sz),Image.Resampling.NEAREST)
def part(path,frames):
 w,h=frames[0].size;im=Image.new('RGBA',(w*len(frames),h*8))
 for r in range(8):
  for i,f in enumerate(frames):im.alpha_composite(f,(w*i,h*r))
 b=io.BytesIO();im.save(b,format='PNG');png=b.getvalue();path.write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',w,h,4,len(frames)))
def beam(path,heads,bodies,tails):
 n=len(heads);hw,hh=heads[0].size;bw,bh=bodies[0].size;tw,th=tails[0].size;im=Image.new('RGBA',(max(hw,bw,tw)*n,hh+bh+th));rect=[]
 for seq,w,h,y in ((heads,hw,hh,0),(bodies,bw,bh,hh),(tails,tw,th,hh+bh)):
  for i,f in enumerate(seq):im.alpha_composite(f,(i*w,y));rect.append((i*w,y,w,h))
 b=io.BytesIO();im.save(b,format='PNG');raw=b.getvalue();path.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<i',len(rect))+b''.join(struct.pack('<iiii',*r) for r in rect)+struct.pack('<i',n))
def at(dst,src,x,y):dst.alpha_composite(src,(round(x-src.width/2),round(y-src.height/2)))
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
shock=particle('Shock_Wave');dis=particle('Discharge');spark=particle('Spark');impact=particle('Discharge_Hit');orb=source(E/'source-v5-energie-pixel.png',28)
# Projectile : animation native Boule Élek autour d'un coeur opaque, branches changeantes.
heads=[]
for t in range(24):
 f=Image.new('RGBA',(64,64)); at(f,orb,32,32); native=shock[(t//3)%len(shock)].resize((52,52),Image.Resampling.NEAREST);at(f,native,32,32);heads.append(f)
empty=[Image.new('RGBA',(1,1)) for _ in heads];beam(E/'ElectroSurfV5_Sphere.beam',heads,empty,empty)
# Croissance réellement progressive issue des 10 images de Décharge, puis transition vers la sphère.
charge=[]
for t in range(96):
 f=Image.new('RGBA',(96,96));idx=min(9,(t//4)%10) if t<48 else 9
 native=dis[idx].resize((72,72),Image.Resampling.NEAREST);at(f,native,48,48)
 if t>=48:
  sz=min(64,round(10+(t-48)*54/28));v=heads[t%24].resize((sz,sz),Image.Resampling.NEAREST);at(f,v,48,48)
 charge.append(f)
part(E/'ElectroSurfV5_Charge.dir',charge)
a=read(E/'stoked_sparksurfer-v3-test-only.json');a['Object']['HitboxAction']['Anim']['AnimIndex']='ElectroSurfV5_Sphere';a['Object']['Data']['BeforeActions'][0]['Value']['Script']='ElectroSurfV5_Charge';a['Object']['Data']['HitFX']=copy.deepcopy(read(G/'Data/Skill/discharge.json')['Object']['Data']['HitFX']);(E/'stoked_sparksurfer-v5-test-only.json').write_text(json.dumps(a,indent=2,ensure_ascii=False))
# Corps d'éclair provenant directement de la colonne Tonnerre native ; il est répété vers le haut de l'écran.
raw=(G/'Content/Beam/Lightning.beam').read_bytes();n=struct.unpack_from('<q',raw)[0];img=Image.open(io.BytesIO(raw[8:8+n])).convert('RGBA');i=n+8;cnt=struct.unpack_from('<i',raw,i)[0];i+=4;rect=[struct.unpack_from('<iiii',raw,i+j*16) for j in range(cnt)];nf=struct.unpack_from('<i',raw,i+cnt*16)[0];nativebody=[img.crop((x,y,x+w,y+h)) for x,y,w,h in rect[nf:2*nf]]
glitter=source(P/'source-v5-etincelle-pixel.png',9);hs=[];bs=[];ts=[]
colors=[(255,96,137),(255,179,53),(252,236,69),(90,219,193),(100,168,255),(196,120,251)]
for t in range(48):
 f=Image.new('RGBA',(96,96));frame=impact[min(len(impact)-1,(t//4)%len(impact))].resize((52,52),Image.Resampling.NEAREST);at(f,frame,48,50)
 for j,col in enumerate(colors):
  a=j*math.tau/6+t*.065;r=16+(t%9);x=48+math.cos(a)*r;y=50+math.sin(a)*r*.65
  if (t+j)%4!=0:
   s=glitter.copy(); arr=np.array(s);mask=arr[:,:,3]>0;arr[mask,0]=col[0];arr[mask,1]=col[1];arr[mask,2]=col[2];at(f,Image.fromarray(arr,'RGBA'),x,y)
 hs.append(f);bs.append(nativebody[(t//3)%len(nativebody)]);ts.append(Image.new('RGBA',(1,1)))
beam(P/'GigaV5_Colonne.beam',hs,bs,ts);part(P/'GigaV5_Colonne.dir',hs)
a=read(P/'ten_million_volt_thunderbolt-v3-test-only.json');a['Object']['Data']['HitFX']['Emitter']['Anim']['Anim']['AnimIndex']='GigaV5_Colonne';(P/'ten_million_volt_thunderbolt-v5-test-only.json').write_text(json.dumps(a,indent=2,ensure_ascii=False))
print('Banques et fiches V5 prêtes ; jeu inchangé.')
