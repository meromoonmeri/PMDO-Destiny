#!/usr/bin/env python3
"""Ressources et fiche expérimentale Canon Blindé, sans installation."""
from PIL import Image
from pathlib import Path
import numpy as np,math,io,struct,json,copy
P=Path(__file__).parent;G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'
def clean(name,size):
 im=Image.open(P/'Sources'/name).convert('RGB');im.thumbnail((size,size),Image.Resampling.NEAREST);a=np.asarray(im).astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];mask=(g>90)&(g>r+45)&(g>b+45);out=Image.fromarray(np.dstack((a.astype('uint8'),np.where(mask,0,255).astype('uint8'))),'RGBA');return out.crop(out.getbbox())
def paste(dst,src,x,y,w,h,alpha=1):
 if w<1 or h<1:return
 im=src.resize((int(w),int(h)),Image.Resampling.NEAREST)
 if alpha<1:im.putalpha(im.getchannel('A').point(lambda a:int(a*max(0,alpha))))
 dst.alpha_composite(im,(int(x-im.width/2),int(y-im.height/2)))
def pngbytes(img):
 s=io.BytesIO();img.save(s,format='PNG',optimize=True);return s.getvalue()
fire=clean('flamme-rayon.png',96);blast=clean('destruction-feu.png',128)
# Beam format: each row is head, 1-pixel-long body, tail; 12 distinct frames.
N=12;W=72;H=145;sheet=Image.new('RGBA',(W*N,H));rect=[]
for part in range(3):
 for t in range(N):
  z=Image.new('RGBA',(W,72 if part!=1 else 1));wave=math.sin(t*math.tau/N)
  if part==0:paste(z,fire,36,35,46+int(5*wave),69)
  elif part==2:paste(z,fire,36,35,42+int(4*wave),70)
  else:
   # Animated hot cross section; beam engine stretches the 1 px high body.
   import colorsys
   for x in range(W):
    a=abs((x-35.5)/(31+2*wave));c=(255,255,232,255) if a<.18 else (255,220,54,255) if a<.4 else (255,129,12,255) if a<.65 else (214,42,4,255) if a<.9 else (0,0,0,0)
    z.putpixel((x,0),c)
  y=[0,72,73][part];sheet.alpha_composite(z,(t*W,y));rect.append((t*W,y,W,z.height))
b=pngbytes(sheet);(P/'CanonBlinde_Rayon.beam').write_bytes(struct.pack('<q',len(b))+b+struct.pack('<i',len(rect))+b''.join(struct.pack('<iiii',*r) for r in rect)+struct.pack('<i',N));sheet.save(P/'CanonBlinde_Rayon-planche.png')
frames=[]
for t in range(42):
 out=Image.new('RGBA',(160,160));size=min(146,12+t*17);fade=min(1,(42-t)/12)
 if t<8:paste(out,blast,80,80,size,size,1)
 else:paste(out,blast,80,80, size,size,fade)
 frames.append(out)
sheet=Image.new('RGBA',(160*len(frames),160));preview=Image.new('RGBA',(160*7,160*6))
for i,f in enumerate(frames):sheet.alpha_composite(f,(160*i,0));preview.alpha_composite(f,(160*(i%7),160*(i//7)))
b=pngbytes(sheet);(P/'CanonBlinde_Impact.dir').write_bytes(struct.pack('<q',len(b))+b+struct.pack('<iiii',160,160,0,len(frames)));preview.save(P/'CanonBlinde_Impact-planche.png')
def load(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
orig=load('armor_cannon');z=copy.deepcopy(orig);o=z['Object'];o['Released']=True;o['Name']['LocalTexts']['fr']='Canon Blindé';o['Desc']['LocalTexts']['fr']='Tire un large rayon ardent puis abaisse les défenses du lanceur. Adaptation expérimentale : brûle les adversaires atteints.'
hyper=load('hyper_beam')['Object'];action=copy.deepcopy(hyper['HitboxAction']);action.update(Wide=True,Range=3,StopAtWall=True,StopAtHit=False,HitTiles=False,TargetAlignments=4,Speed=10,Linger=12);action['TileEmitter']=copy.deepcopy(load('fire_pledge')['Object']['HitboxAction']['TileEmitter']);action['Anim']['AnimIndex']='CanonBlinde_Rayon';action['Anim']['FrameTime']=2;action['ActionFX']['Sound']='DUN_Flamethrower';o['HitboxAction']=action
# Blast is visual only. The native beam hits each tile once; no explosion area damage is implied.
o['Data']['OnHits'].append(copy.deepcopy(load('flamethrower')['Object']['Data']['OnHits'][1]));o['Data']['SkillStates'].append({'$type':'PMDC.Dungeon.AdditionalEffectState, PMDC','EffectChance':100})
o['Data']['AfterActions']=[{'Key':{'str':[-1]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'CanonBlinde_Impact','ArgTable':'{}'}}]+copy.deepcopy(load('close_combat')['Object']['Data']['AfterActions']);o['Data']['OnHitTiles']=[]
(P/'armor_cannon-original.json').write_text(json.dumps(orig,ensure_ascii=False,indent=2));(P/'armor_cannon-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Rayon 12 images, impact 42 images et fiche expérimentale produits.')
