#!/usr/bin/env python3
"""Fureur des Plumes Spectrales : préparation hors jeu, pour banc isolé."""
from pathlib import Path
from PIL import Image
import math,io,struct,json,copy
import numpy as np
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Fureur-des-Plumes-Spectrales/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
# Détourage propre de l'image IA : teinte verte retirée des bords aussi.
a=np.asarray(Image.open(P/'source-ia-plumes-spectrales.png').convert('RGB')).astype('float32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];score=np.maximum(r,b)
alpha=np.clip((1-np.maximum(g-score,0)/255-.14)/.86,0,1);safe=np.maximum(alpha,1/255)
a[:,:,1]=np.minimum(np.clip((g-255*(1-alpha))/safe,0,255),score+18)
im=Image.fromarray(np.dstack([np.uint8(np.clip(a,0,255)),np.uint8(alpha*255)]),'RGBA');im=im.crop(im.getbbox());im.thumbnail((92,92),Image.Resampling.LANCZOS);im.save(P/'plumes-spectrales-ia-detourees.png')
# Extraire une flèche originale de Tisse Ombre pour la volée sur la cible.
raw=(G/'Content/Particle/Arrow_Shot.dir').read_bytes();n=struct.unpack_from('<q',raw)[0];sheet=Image.open(io.BytesIO(raw[8:8+n])).convert('RGBA');arrow=sheet.crop((64,0,96,32));arrow=arrow.crop(arrow.getbbox());arrow.thumbnail((18,18),Image.Resampling.NEAREST)
N=128;T=48;frames=[]
for t in range(T):
 f=Image.new('RGBA',(N,N));fade=min(1,(t+1)/6,(T-t)/12);scale=.50+.50*min(1,t/12);size=max(1,round(100*scale));v=im.resize((size,size),Image.Resampling.LANCZOS).rotate(7*math.sin(t*.1),resample=Image.Resampling.BICUBIC,expand=False);v.putalpha(v.getchannel('A').point(lambda x:round(x*fade*.5)));f.alpha_composite(v,((N-size)//2,(N-size)//2))
 # Huit flèches natives entrent en séquence vers le centre.
 for j in range(8):
  age=t-j*2
  if 0<=age<22:
   a=j*math.tau/8;dist=max(3,52-age*3.2);x=N/2+dist*math.cos(a);y=N/2+dist*math.sin(a)
   rotated=arrow.rotate(90-j*45,resample=Image.Resampling.NEAREST,expand=True);o=min(1,(age+1)/3,(22-age)/6);rotated.putalpha(rotated.getchannel('A').point(lambda v:round(v*o)));f.alpha_composite(rotated,(round(x-rotated.width/2),round(y-rotated.height/2)))
 frames.append(f)
sheet=Image.new('RGBA',(N*T,N*8));preview=Image.new('RGBA',(N*8,N),(25,27,34,255))
for row in range(8):
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,(i*N,row*N))
for j,i in enumerate([0,5,10,15,20,27,36,45]):preview.alpha_composite(frames[i],(j*N,0))
b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/'FureurPlumes_Impact.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,T));preview.convert('RGB').save(P/'progression-impact.png')
# Une couronne de flèches natives apparaît autour d'Archéduc avant le tir.
charge=[]
for t in range(52):
 f=Image.new('RGBA',(N,N));fade=min(1,(t+1)/8,(52-t)/10)
 for j in range(6):
  a=j*math.tau/6+t*math.tau/104;radius=21+5*math.sin(t*.12+j);x=64+radius*math.cos(a);y=64+radius*.6*math.sin(a)
  rotated=arrow.rotate(-j*60-t*360/104,resample=Image.Resampling.NEAREST,expand=True);rotated.putalpha(rotated.getchannel('A').point(lambda v:round(v*fade)));f.alpha_composite(rotated,(round(x-rotated.width/2),round(y-rotated.height/2)))
 charge.append(f)
sheet=Image.new('RGBA',(N*len(charge),N*8))
for row in range(8):
 for i,frame in enumerate(charge):sheet.alpha_composite(frame,(i*N,row*N))
b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/'FureurPlumes_Charge.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(charge)))
z=read('sinister_arrow_raid');assert not z['Object']['Released'];a=z['Object'];a['Released']=True;a['BaseCharges']=1
assert a['Data']['Element']=='ghost' and a['Data']['Category']==1 and any(x.get('Power')==180 for x in a['Data']['SkillStates'])
# Tisse Ombre : flèche native, traînée Spectre, première cible uniquement.
act=copy.deepcopy(read('spirit_shackle')['Object']['HitboxAction']);act.update(Range=4,StopAtHit=True,StopAtWall=True,HitTiles=False,TargetAlignments=4);a['HitboxAction']=act
# Texture d'impact générée, sans ajouter l'entrave de Tisse Ombre.
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='FureurPlumes_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx['Delay']=48;fx['AbsoluteDelay']=True;fx['Sound']='DUN_Night_Slash';a['Data']['HitFX']=fx
# Pré-impact natif Tisse Ombre, en plus de la volée IA.
a['Explosion']['ExplodeFX']=copy.deepcopy(read('spirit_shackle')['Object']['Data']['HitFX'])
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'FureurPlumes_Charge','ArgTable':'{}'}}]
(P/'sinister_arrow_raid-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
print('Banque IA, flèches natives et fiche test-only prêtes. Aucun jeu modifié.')
