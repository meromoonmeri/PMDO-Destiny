#!/usr/bin/env python3
"""Fureur V2 : séquences discrètes dessinées image par image, pour banc isolé."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,copy,struct,io,math
import numpy as np
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Fureur-des-Plumes-Spectrales/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
def bank(name,frames):
 w,h=frames[0].size; s=Image.new('RGBA',(w*len(frames),h*8))
 for y in range(8):
  for i,f in enumerate(frames):s.alpha_composite(f,(i*w,y*h))
 b=io.BytesIO();s.save(b,format='PNG');raw=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,4,len(frames)))
# Une plume IA convertie en petite particule pixelisée : alpha binaire, aucune image réaliste de fond.
a=np.array(Image.open(P/'source-ia-v2-plume-pixel.png').convert('RGB'));mask=(a[:,:,0]>a[:,:,1]*1.1)&(a[:,:,2]>a[:,:,1]*1.1); yy,xx=np.where(mask);rgba=np.dstack((a,mask.astype('uint8')*255));feather=Image.fromarray(rgba,'RGBA').crop((xx.min(),yy.min(),xx.max()+1,yy.max()+1)).resize((12,12),Image.Resampling.NEAREST);feather.save(P/'v2-plume-pixel-detouree.png')
# Les flèches d'origine : séquence d'émission en trois temps, puis éclats et plumes.
raw=(G/'Content/Particle/Arrow_Shot.dir').read_bytes();n=struct.unpack_from('<q',raw)[0];sh=Image.open(io.BytesIO(raw[8:8+n])).convert('RGBA');arrow=sh.crop((64,0,96,32));arrow=arrow.crop(arrow.getbbox());arrow.thumbnail((18,18),Image.Resampling.NEAREST)
N=64;frames=[]
for t in range(44):
 f=Image.new('RGBA',(N,N));draw=ImageDraw.Draw(f)
 for j in range(7):
  age=t-(j*3)
  if 0<=age<13:
   angle=math.pi*2*j/7;dist=max(3,31-age*3); x=32+math.cos(angle)*dist;y=32+math.sin(angle)*dist*.76
   v=arrow.rotate(-j*360/7,resample=Image.Resampling.NEAREST,expand=True)
   f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
  if 6<=age<22:
   p=(age-6)/16; ang=j*math.tau/7; dist=5+p*24;x=round(32+dist*math.cos(ang));y=round(32+dist*.8*math.sin(ang));
   if age<15:draw.line((x,y,x+round(math.cos(ang)*3),y+round(math.sin(ang)*3)),fill=(197,173,255,255),width=1)
   else: draw.point((x,y),fill=(118,83,170,255))
  if 9<=age<25:
   p=(age-9)/16;x=round(32+math.cos(j*math.tau/7)*(8+17*p));y=round(32+math.sin(j*math.tau/7)*(8+13*p)+p*4);v=feather.rotate((j*49+age*5)%360,Image.Resampling.NEAREST,expand=True);v.putalpha(v.getchannel('A').point(lambda q:q*(25-age)//8 if age>17 else q));f.alpha_composite(v,(x-v.width//2,y-v.height//2))
 if 8<=t<16:
  rad=3+min(t-8,15-t);draw.line((32-rad,32,32+rad,32),fill=(247,231,255,255));draw.line((32,32-rad,32,32+rad),fill=(247,231,255,255))
 frames.append(f)
bank('FureurV2_Impact',frames)
# Petites plumes aux positions et orientations évolutives, sans recouvrir le sprite du porteur.
charge=[]
for t in range(40):
 f=Image.new('RGBA',(64,64))
 for j in range(5):
  a=j*math.tau/5+t*.1;radius=17+2*math.sin(t*.16+j);x=32+radius*math.cos(a);y=30+radius*.50*math.sin(a)
  v=feather.resize((8,8),Image.Resampling.NEAREST).rotate(-j*72-t*5,Image.Resampling.NEAREST,expand=True);opacity=min(1,(t+1)/6,(40-t)/6);v.putalpha(v.getchannel('A').point(lambda q:round(q*opacity)));f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
 charge.append(f)
bank('FureurV2_Charge',charge)
z=read('sinister_arrow_raid');a=z['Object'];a['Released']=True;a['BaseCharges']=1
act=copy.deepcopy(read('spirit_shackle')['Object']['HitboxAction']);act.update(Range=4,StopAtHit=True,StopAtWall=True,HitTiles=False,TargetAlignments=4);a['HitboxAction']=act
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='FureurV2_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=44,AbsoluteDelay=True,Sound='DUN_Night_Slash');a['Data']['HitFX']=fx
a['Explosion']['ExplodeFX']=copy.deepcopy(read('spirit_shackle')['Object']['Data']['HitFX']);a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'FureurPlumesV2_Charge','ArgTable':'{}'}}]
(P/'sinister_arrow_raid-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Deux animations à 40 et 44 images créées ; jeu inchangé.')
