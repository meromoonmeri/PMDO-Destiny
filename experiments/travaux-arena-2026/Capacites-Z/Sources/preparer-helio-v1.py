#!/usr/bin/env python3
"""Banques d'Hélio-Choc pour un banc isolé."""
from pathlib import Path
from PIL import Image
import numpy as np,math,struct,io,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Helio-Choc-Devastateur/Generation-PMDO'
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];s=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,cnt=struct.unpack_from('<iiii',b,k+8);return [s.crop((i*w,0,(i+1)*w,h)) for i in range(cnt)]
def clean(n):
 im=np.asarray(Image.open(P/'Sources'/n).convert('RGB'));r,g,b=[im[:,:,i].astype('int16') for i in range(3)];mask=(g>60)&(g>r*1.18)&(g>b*1.18);z=Image.fromarray(np.dstack((im,(~mask).astype('uint8')*255)),'RGBA');return z.crop(z.getbbox())
def paste(f,v,x,y,alpha=1):
 v=v.copy()
 if alpha<1:v.putalpha(v.getchannel('A').point(lambda q:round(q*max(0,alpha))))
 f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
def bank(name,fs):
 w,h=fs[0].size;s=Image.new('RGBA',(w*len(fs),h*8));sheet=Image.new('RGBA',(w*8,h*math.ceil(len(fs)/8)))
 for i,f in enumerate(fs):
  sheet.alpha_composite(f,((i%8)*w,(i//8)*w))
  for d in range(8):s.alpha_composite(f,(w*i,h*d))
 z=io.BytesIO();s.save(z,format='PNG',optimize=True);raw=z.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,4,len(fs)));sheet.save(P/(name+'-planche.png'),optimize=True)
solar=native('Solar_Beam_Charge');flash=native('Flash_Cannon_Sparkle');fire=native('Flare_Blitz_Charge_Front');meteor=native('Meteor_Mash_Star');breche=clean('ultra-breche.png');impact=clean('impact-solaire.png')
fs=[]
for t in range(64):
 f=Image.new('RGBA',(96,96))
 for j in range(8):
  age=(t+j*7)%42;ang=j*math.tau/8+t*.08;radius=34-age*.62
  v=flash[min(len(flash)-1,age//5)].resize((12,12),Image.Resampling.NEAREST);paste(f,v,48+math.cos(ang)*radius,48+math.sin(ang)*radius*.7)
 if t>8:
  idx=min(len(solar)-1,(t-9)//4);paste(f,solar[idx].resize((64,64),Image.Resampling.NEAREST),48,48,min(1,(t-8)/8,(64-t)/8))
 if t>30:paste(f,fire[((t-30)//4)%len(fire)].resize((60,60),Image.Resampling.NEAREST),48,48,min(1,(t-30)/8,(64-t)/8))
 fs.append(f)
bank('HelioV1_Charge',fs)
fs=[]
for t in range(54):
 f=Image.new('RGBA',(96,96));size=min(78,8+t*7) if t<12 else (78 if t<38 else max(1,78-(t-38)*5));fade=min(1,t/5,(54-t)/8);v=breche.resize((size,size),Image.Resampling.NEAREST).rotate(t*5,Image.Resampling.NEAREST,expand=True);paste(f,v,48,48,fade)
 fs.append(f)
bank('HelioV1_Breche',fs)
fs=[]
for t in range(56):
 f=Image.new('RGBA',(144,144))
 if t<38:
  size=min(115,16+t*12) if t<9 else min(135,115+(t-9));fade=min(1,(38-t)/9);paste(f,impact.resize((size,size),Image.Resampling.NEAREST),72,72,fade)
 for j in range(8):
  age=t-j*2
  if 0<=age<30:
   ang=j*math.tau/8;rr=7+age*1.7;v=meteor[min(len(meteor)-1,age//4)].resize((12,12),Image.Resampling.NEAREST);paste(f,v,72+math.cos(ang)*rr,72+math.sin(ang)*rr,.9*min(1,(30-age)/7))
 fs.append(f)
bank('HelioV1_Impact',fs)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
z=read('searing_sunraze_smash');o=z['Object'];o['Released']=True;o['BaseCharges']=1;o['Data']['SkillStates'].insert(0,{'$type':'PMDC.Dungeon.ContactState, PMDC'})
act=copy.deepcopy(read('night_slash')['Object']['HitboxAction']);act.update(Range=2,StopAtHit=True,StopAtWall=True,HitTiles=False,TargetAlignments=4,CharAnim=5,WideAngle=0);act['Emitter']=copy.deepcopy(read('acrobatics')['Object']['HitboxAction']['Emitter']);act['ActionFX']['Sound']='DUN_Flare_Blitz'
trail=copy.deepcopy(act['TileEmitter']);trail['Anim']['Anim']['AnimIndex']='Flash_Cannon_Sparkle';trail['Anim']['Anim']['FrameTime']=2;act['TileEmitter']=trail;o['HitboxAction']=act
def event(n,p):return {'Key':{'str':[p]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':n,'ArgTable':'{}'}}
o['Data']['BeforeActions']=[event('HelioV1_Charge',0)];o['Data']['BeforeHits']=[event('HelioV1_IgnoreTalentEtBreche',-100)];o['Data']['AfterActions']=[event('HelioV1_RestaureTalent',100)]
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='HelioV1_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=56,AbsoluteDelay=True,Sound='DUN_Giga_Impact');fx['ScreenMovement']={'MinShake':0,'MaxShake':3,'MaxShakeTime':16};o['Data']['HitFX']=fx
(P/'searing_sunraze_smash-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Trois banques, fiche et attaque préparées.')
