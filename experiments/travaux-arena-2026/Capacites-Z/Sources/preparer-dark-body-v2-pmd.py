#!/usr/bin/env python3
"""Dark Body Press V2 : charge, traînée et impact adaptés aux sprites natifs."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,copy,io,struct,math
import numpy as np
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Dark-Body-Press/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
def native(n):
 raw=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',raw)[0];img=Image.open(io.BytesIO(raw[8:8+k])).convert('RGBA');w,h,_,count=struct.unpack_from('<iiii',raw,8+k);return [img.crop((i*w,0,(i+1)*w,h)) for i in range(count)]
def bank(n,frames):
 w,h=frames[0].size;s=Image.new('RGBA',(w*len(frames),h*8))
 for y in range(8):
  for i,f in enumerate(frames):s.alpha_composite(f,(i*w,y*h))
 b=io.BytesIO();s.save(b,format='PNG');png=b.getvalue();(P/(n+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',w,h,4,len(frames)))
def place(dst,im,x,y):dst.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))
a=np.asarray(Image.open(P/'source-v2-eclat-tenebres.png').convert('RGB'));r,g,b=[a[:,:,i].astype(int) for i in range(3)];mask=(g<np.maximum(r,b)*1.12)|(g<55);y,x=np.where(mask);shard=Image.fromarray(np.dstack((a,mask.astype('uint8')*255)),'RGBA').crop((x.min(),y.min(),x.max()+1,y.max()+1)).resize((12,12),Image.Resampling.NEAREST)
pulse=native('Dark_Pulse_Particle');smoke=native('Smoke_Purple');hit=native('Sucker_Punch_Hit')
# Amas en mouvement ascendant : aucune arène ou structure circulaire.
charge=[]
for t in range(48):
 f=Image.new('RGBA',(72,72))
 for j in range(7):
  age=(t+j*7)%38;px=36+((j*17)%31)-15+2*math.sin(age*.2+j);py=54-age*.7
  k=min(len(pulse)-1,age//8);v=pulse[k];place(f,v,px,py)
  if j%2==0 and age<26:
   v=smoke[min(len(smoke)-1,age//3)].resize((16,16),Image.Resampling.NEAREST);place(f,v,px,py)
 if t>17:
  for j in range(3):
   age=(t+j*9)%26;v=shard.rotate((j-1)*40,Image.Resampling.NEAREST,expand=True);place(f,v,27+j*9,52-age)
 charge.append(f)
bank('DarkBodyV2_Charge',charge)
# Impact construit de multiples éléments synchronisés, et non d'une image mise à l'échelle.
frames=[]
for t in range(40):
 f=Image.new('RGBA',(72,72));d=ImageDraw.Draw(f)
 if t<18:
  for j in range(4):
   age=t-j*2
   if 0<=age<12:
    dist=age*2.2;sign=-1 if j%2 else 1;x=36+sign*dist;y=36+(j-1.5)*5+sign*dist*.4
    d.line((round(x-sign*5),round(y+3),round(x+sign*5),round(y-3)),fill=(69,29,93,255),width=4)
    d.line((round(x-sign*5),round(y+3),round(x+sign*5),round(y-3)),fill=(207,123,222,255),width=1)
 if t<24:
  v=hit[min(len(hit)-1,t//4)].resize((52,52),Image.Resampling.NEAREST);place(f,v,36,36)
 for j in range(7):
  age=t-j*2
  if 3<=age<26:
   angle=j*math.tau/7;dist=5+(age-3)*1.2;x=36+math.cos(angle)*dist;y=36+math.sin(angle)*dist*.8
   v=shard.resize((7,7),Image.Resampling.NEAREST).rotate(j*50+age*4,Image.Resampling.NEAREST,expand=True);place(f,v,x,y)
 frames.append(f)
bank('DarkBodyV2_Impact',frames)
z=read('malicious_moonsault');a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['SkillStates'].insert(0,{'$type':'PMDC.Dungeon.ContactState, PMDC'})
act=copy.deepcopy(read('night_slash')['Object']['HitboxAction']);act.update(Range=3,StopAtHit=True,StopAtWall=True,HitTiles=True,TargetAlignments=4,CharAnim=5);act['Emitter']=copy.deepcopy(read('acrobatics')['Object']['HitboxAction']['Emitter']);act['ActionFX']['Sound']='DUN_Night_Slash'
# Les cases parcourues laissent une trace d'énergie native derrière l'image rémanente.
trail=copy.deepcopy(read('night_slash')['Object']['HitboxAction']['TileEmitter']);trail['Anim']['Anim']['AnimIndex']='Smoke_Purple';trail['Anim']['Anim']['FrameTime']=2;act['TileEmitter']=trail;a['HitboxAction']=act
a['Data']['OnHitTiles']=copy.deepcopy(read('head_smash')['Object']['Data']['OnHitTiles']);a['Explosion']['HitTiles']=True
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='DarkBodyV2_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=40,AbsoluteDelay=True,Sound='DUN_Giga_Impact');a['Data']['HitFX']=fx
a['Explosion']['ExplodeFX']=copy.deepcopy(read('night_slash')['Object']['Data']['HitFX']);a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'DarkBodyV2_Charge','ArgTable':'{}'}}]
(P/'malicious_moonsault-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Animations de 48 et 40 images et fiche de banc préparées.')
