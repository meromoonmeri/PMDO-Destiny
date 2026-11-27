#!/usr/bin/env python3
"""Spatio-Rift : banque d'effet et fiche expérimentale, sans installer le jeu."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, json, copy, math, io, struct
H=Path.home(); P=H/'Capacites-de-base/Spatio-Rift'; G=H/'.cache/destiny-test/game/PMDO-Destiny';P.mkdir(parents=True,exist_ok=True)
src=Image.open(P/'Sources/faille-source.png').convert('RGB');src.thumbnail((92,92),Image.Resampling.NEAREST)
a=np.asarray(src).astype('int16');mask=(a[:,:,1]>130)&(a[:,:,1]>a[:,:,0]+45)&(a[:,:,1]>a[:,:,2]+45)
rgba=Image.fromarray(np.dstack((a.astype('uint8'),np.where(mask,0,255).astype('uint8'))),'RGBA');rgba=rgba.crop(rgba.getbbox())
N=96;frames=[]
for t in range(30):
 im=Image.new('RGBA',(N,N)); d=ImageDraw.Draw(im)
 # L'espace se fend, s'élargit, se referme puis libère quelques éclats.
 opening=min(1,(t+1)/7); closing=min(1,(30-t)/9); envelope=min(opening,closing)
 if t<26:
  w=int((10+54*opening)*max(.1,closing));h=int(10+65*opening)
  fx=rgba.resize((max(1,w),h),Image.Resampling.NEAREST)
  fx.putalpha(fx.getchannel('A').point(lambda v:round(v*min(1,closing*1.3))))
  im.alpha_composite(fx,(N//2-w//2,N//2-h//2))
 d=ImageDraw.Draw(im)
 if 5<=t<25:
  for j in range(6):
   angle=j*math.tau/6+t*.09;radius=10+max(0,t-5)*1.5;x=int(48+math.cos(angle)*radius);y=int(48+math.sin(angle)*radius*.8);alpha=int(230*envelope);r=2 if t<16 else 1
   d.polygon([(x,y-2*r),(x+r,y),(x,y+2*r),(x-r,y)],fill=(213,160,255,alpha))
 frames.append(im)
sheet=Image.new('RGBA',(N*len(frames),N*8))
for row in range(8):
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,(i*N,row*N))
sheet.save(P/'SpatioRift_Faille.Dir8.png');bio=io.BytesIO();sheet.save(bio,format='PNG');raw=bio.getvalue();(P/'SpatioRift_Faille.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,3,len(frames)))
def load(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=load('spacial_rend');z=copy.deepcopy(orig);o=z['Object'];ref=load('dragon_pulse')['Object'];meteor=load('draco_meteor')['Object'];
o['HitboxAction']['PreActions']=[copy.deepcopy(meteor['HitboxAction']['PreActions'][0])]
o['HitboxAction']['ActionFX']['Sound']='DUN_Dragon_Pulse'
fx=copy.deepcopy(ref['Data']['HitFX']);fx['Emitter']={'$type':'RogueEssence.Content.SingleEmitter, RogueEssence','LocHeight':0,'finished':False,'Offset':0,'Anim':{'$type':'RogueEssence.Content.StaticAnim, RogueEssence','Anim':{'AnimIndex':'SpatioRift_Faille','FrameTime':2,'StartFrame':-1,'EndFrame':-1,'AnimDir':-1,'Alpha':255,'AnimFlip':0},'TotalTime':0,'Cycles':1,'FrameOffset':0},'Layer':2,'UseDest':False};fx['Delay']=40;fx['Sound']='DUN_Dragon_Pulse';o['Data']['HitFX']=fx
(P/'spacial_rend-original.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2));(P/'spacial_rend-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
# Garantir que seules les sections visuelles explicitement concernées changent.
check=copy.deepcopy(z);check['Object']['HitboxAction']['PreActions']=orig['Object']['HitboxAction']['PreActions'];check['Object']['HitboxAction']['ActionFX']=orig['Object']['HitboxAction']['ActionFX'];check['Object']['Data']['HitFX']=orig['Object']['Data']['HitFX'];assert check==orig
print('Banque 30 poses et fiche de banc produites ; paramètres de combat inchangés.')
