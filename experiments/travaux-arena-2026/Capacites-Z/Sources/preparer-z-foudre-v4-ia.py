#!/usr/bin/env python3
"""V4 : textures générées, préparées pour le banc isolé, jamais installées ici."""
from pathlib import Path
from PIL import Image
import numpy as np,struct,io,json,math,copy
H=Path.home();R=H/'Capacites-Z/Prototypes';GP=R/'Giga-Tonnerre/Generation-PMDO';EP=R/'Electro-Surf-Survolte/Generation-PMDO'
def dechroma(path):
 a=np.asarray(Image.open(path).convert('RGB')).astype('float32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];score=np.maximum(r,b)
 al=np.clip((1-np.maximum(g-score,0)/255-.14)/.86,0,1);safe=np.maximum(al,1/255)
 a[:,:,1]=np.minimum(np.clip((g-255*(1-al))/safe,0,255),score+18)
 out=Image.fromarray(np.dstack([np.uint8(np.clip(a,0,255)),np.uint8(al*255)]),'RGBA');return out.crop(out.getbbox())
def unpack_dir(path):
 data=path.read_bytes();n=struct.unpack_from('<q',data)[0];im=Image.open(io.BytesIO(data[8:8+n])).convert('RGBA');w,h,_,count=struct.unpack_from('<iiii',data,8+n);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(count)]
def unpack_beam(path):
 raw=path.read_bytes();n=struct.unpack_from('<q',raw)[0];im=Image.open(io.BytesIO(raw[8:8+n])).convert('RGBA');i=8+n;cnt=struct.unpack_from('<i',raw,i)[0];i+=4;rects=[struct.unpack_from('<iiii',raw,i+16*j) for j in range(cnt)];frames=struct.unpack_from('<i',raw,i+cnt*16)[0];imgs=[im.crop((x,y,x+w,y+h)) for x,y,w,h in rects];return imgs[:frames],imgs[frames:2*frames],imgs[2*frames:]
def dirbank(path,frames):
 w,h=frames[0].size;sheet=Image.new('RGBA',(w*len(frames),h*8))
 for j in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(w*i,h*j))
 o=io.BytesIO();sheet.save(o,format='PNG');raw=o.getvalue();path.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,4,len(frames)))
def beam(path,heads,bodies,tails):
 n=len(heads);assert len(bodies)==len(tails)==n
 hw,hh=heads[0].size;bw,bh=bodies[0].size;tw,th=tails[0].size;tex=Image.new('RGBA',(max(hw,bw,tw)*n,hh+bh+th));rect=[]
 for seq,w,h,y in ((heads,hw,hh,0),(bodies,bw,bh,hh),(tails,tw,th,hh+bh)):
  for i,f in enumerate(seq):tex.alpha_composite(f,(i*w,y));rect.append((i*w,y,w,h))
 out=io.BytesIO();tex.save(out,format='PNG');raw=out.getvalue();path.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<i',len(rect))+b''.join(struct.pack('<iiii',*r) for r in rect)+struct.pack('<i',n))
def preview(path,frames):
 indices=[0,6,12,18,24,30,36,42];w,h=frames[0].size;out=Image.new('RGBA',(w*len(indices),h),(28,30,37,255))
 for i,j in enumerate(indices):out.alpha_composite(frames[j],(w*i,0))
 out.convert('RGB').save(path)
# Sphère pleine et opaque : coeur de l'image IA, animé par de légers mouvements.
sphere=dechroma(EP/'source-ia-v4-sphere.png');sphere.thumbnail((72,72),Image.Resampling.LANCZOS);sphere.save(EP/'sphere-v4-detouree.png')
heads=[]
for t in range(48):
 image=sphere.rotate(7*math.sin(t*math.tau/48),resample=Image.Resampling.BICUBIC,expand=False);f=Image.new('RGBA',(80,80));f.alpha_composite(image,((80-image.width)//2,(80-image.height)//2));heads.append(f)
empty=[Image.new('RGBA',(1,1)) for _ in heads];beam(EP/'ElectroSurfV4_Sphere.beam',heads,empty,empty);preview(EP/'ElectroSurfV4-sphere-progression.png',heads)
oldcharge=unpack_dir(EP/'ElectroSurfV3_Charge.dir');frames=[]
for t in range(114):
 # Jusqu'à la formation, conserver les arcs de charge existants ; au-delà,
 # utiliser la sphère IA grandissante à la place de la sphère dessinée V3.
 f=oldcharge[min(t,56)].copy()
 if t>=58:
  p=min(1,(t-58)/26);sz=max(1,round(16+64*p));s=heads[t%48].resize((sz,sz),Image.Resampling.LANCZOS);f.alpha_composite(s,((96-sz)//2,(96-sz)//2))
 frames.append(f)
dirbank(EP/'ElectroSurfV4_Charge.dir',frames)
script=(H/'Capacites-Z/Sources/electro-surf-v3-charge.lua').read_text().replace('ElectroSurfV3_Charge','ElectroSurfV4_Charge');(H/'Capacites-Z/Sources/electro-surf-v4-charge.lua').write_text(script)
a=json.loads((EP/'stoked_sparksurfer-v3-test-only.json').read_text());a['Object']['HitboxAction']['Anim']['AnimIndex']='ElectroSurfV4_Sphere';a['Object']['Data']['BeforeActions'][0]['Value']['Script']='ElectroSurfV4_Charge';(EP/'stoked_sparksurfer-v4-test-only.json').write_text(json.dumps(a,ensure_ascii=False,indent=2))
# La colonne native répétable continue jusqu'au bord haut du cadre. L'image IA
# anime sa texture, fondue sur l'ancienne base continue pour éviter une pointe.
source=dechroma(GP/'source-ia-v4-foudre.png');source=source.resize((48,192),Image.Resampling.LANCZOS);source.save(GP/'foudre-v4-detouree.png')
h,b,t=unpack_beam(GP/'GigaV3_Colonne.beam');new=[]
for i,old in enumerate(b):
 layer=Image.new('RGBA',(48,24));shift=(i*4)%192
 for y in range(24):
  row=source.crop((0,(shift+y)%192,48,(shift+y)%192+1));layer.alpha_composite(row,(0,y))
 # fondre haut et bas sur la colonne procédurale, elle-même raccordable
 arr=np.asarray(layer).copy();weight=np.sin(np.pi*(np.arange(24)+.5)/24)**2;arr[:,:,3]=(arr[:,:,3].astype(float)*weight[:,None]*.9).astype('uint8');f=old.copy();f.alpha_composite(Image.fromarray(arr,'RGBA'));new.append(f)
beam(GP/'GigaV4_Colonne.beam',h,new,t);dirbank(GP/'GigaV4_Colonne.dir',h);preview(GP/'GigaV4-colonne-progression.png',new)
a=json.loads((GP/'ten_million_volt_thunderbolt-v3-test-only.json').read_text());a['Object']['Data']['HitFX']['Emitter']['Anim']['Anim']['AnimIndex']='GigaV4_Colonne';(GP/'ten_million_volt_thunderbolt-v4-test-only.json').write_text(json.dumps(a,ensure_ascii=False,indent=2))
print('Banques V4 IA générées ; aucun fichier du jeu modifié.')
