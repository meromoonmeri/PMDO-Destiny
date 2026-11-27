#!/usr/bin/env python3
"""Trois dernières signatures : banques animées et fiches de banc."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,math,struct,io,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';ROOT=H/'Capacites-Z/Prototypes'
cfg=[('Rayons-Seleno-Explosifs','eclat-lunaire.png','Selene','menacing_moonraze_maelstrom'),('Apocalypsis-Luminis','pilier-prismatique.png','Apocalypse','light_that_burns_the_sky'),('Fauche-Ame-des-Sept-Etoiles','eclat-spectral.png','Fauche','soul_stealing_7_star_strike')]
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];s=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,cnt=struct.unpack_from('<iiii',b,k+8);return [s.crop((i*w,0,(i+1)*w,h)) for i in range(cnt)]
def clean(n):
 a=np.asarray(Image.open(n).convert('RGB'));r,g,b=[a[:,:,i].astype('int16') for i in range(3)];mask=(g>65)&(g>r*1.18)&(g>b*1.18);v=Image.fromarray(np.dstack((a,(~mask).astype('uint8')*255)),'RGBA');return v.crop(v.getbbox())
def paste(f,v,x,y,alpha=1):
 v=v.copy()
 if alpha<1:v.putalpha(v.getchannel('A').point(lambda q:round(q*max(0,alpha))))
 f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
def bank(P,name,fs):
 w,h=fs[0].size;assert w*len(fs)<16384;s=Image.new('RGBA',(w*len(fs),h*8));sheet=Image.new('RGBA',(w*8,h*math.ceil(len(fs)/8)))
 for i,f in enumerate(fs):
  sheet.alpha_composite(f,((i%8)*w,(i//8)*h))
  for d in range(8):s.alpha_composite(f,(w*i,h*d))
 z=io.BytesIO();s.save(z,format='PNG',optimize=True);raw=z.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,4,len(fs)));sheet.save(P/(name+'-planche.png'),optimize=True)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
def event(n,p):return {'Key':{'str':[p]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':n,'ArgTable':'{}'}}
refs={'Selene':native('Shadow_Force_Front'),'Apocalypse':native('Psycho_Boost_Front'),'Fauche':native('Shadow_Sneak_Hit')}
spark={'Selene':native('Dark_Pulse_Particle'),'Apocalypse':native('Psycho_Shift_Charge'),'Fauche':native('Shadow_Force_Hit_Light')}
for folder,source,tag,skill in cfg:
 P=ROOT/folder/'Generation-PMDO';src=clean(P/'Sources'/source);base=refs[tag];part=spark[tag];fs=[]
 for t in range(54):
  f=Image.new('RGBA',(96,96))
  for j in range(8):
   age=(t+j*6)%39;ang=j*math.tau/8+t*.09;rad=35-age*.65;v=part[min(len(part)-1,age//5)].resize((12,12),Image.Resampling.NEAREST);paste(f,v,48+math.cos(ang)*rad,48+math.sin(ang)*rad*.7)
  if t>10:paste(f,base[((t-10)//5)%len(base)].resize((52,52),Image.Resampling.NEAREST),48,48,min(1,(t-10)/8,(54-t)/7))
  fs.append(f)
 bank(P,tag+'V1_Charge',fs);fs=[]
 for t in range(64):
  f=Image.new('RGBA',(144,144));d=ImageDraw.Draw(f)
  if tag=='Selene':
   # Sept rayons qui convergent vers la cible, puis croissant spectral.
   for j in range(7):
    age=t-j*4
    if 0<=age<23:
     angle=j*math.tau/7;outer=max(4,60-age*2.2);inner=max(0,outer-25);x1=72+math.cos(angle)*outer;y1=72+math.sin(angle)*outer;x2=72+math.cos(angle)*inner;y2=72+math.sin(angle)*inner
     d.line((round(x1),round(y1),round(x2),round(y2)),fill=(99,47,190,255),width=5);d.line((round(x1),round(y1),round(x2),round(y2)),fill=(158,237,255,255),width=2)
   if t>=19 and t<57:
    size=min(108,16+(t-19)*10);paste(f,src.resize((size,size),Image.Resampling.NEAREST),72,72,min(1,(57-t)/10))
  elif tag=='Apocalypse':
   if t<52:
    size=min(130,20+t*11);v=src.resize((max(8,int(size*.75)),size),Image.Resampling.NEAREST);paste(f,v,72,70,min(1,t/3,(52-t)/10))
   for j in range(5):
    age=t-j*4
    if 0<=age<30:paste(f,part[min(len(part)-1,age//4)].resize((20,20),Image.Resampling.NEAREST),36+j*18,90-age*1.4,min(1,(30-age)/7))
  else:
   # Sept impacts visuels distincts, un seul calcul de dégâts.
   for j in range(7):
    age=t-j*6
    if 0<=age<19:
     ang=-math.pi/2+j*math.tau/7;xx=72+math.cos(ang)*27;yy=72+math.sin(ang)*23;size=min(23,5+age*5);paste(f,src.resize((size,size),Image.Resampling.NEAREST),xx,yy,min(1,(19-age)/5))
   if 40<=t<62:
    age=t-40;size=min(108,12+age*12);paste(f,src.resize((size,size),Image.Resampling.NEAREST),72,72,min(1,(62-t)/7))
  fs.append(f)
 bank(P,tag+'V1_Impact',fs)
 z=read(skill);o=z['Object'];o['Released']=True;o['BaseCharges']=1
 if tag=='Fauche':
  o['Data']['SkillStates'].insert(0,{'$type':'PMDC.Dungeon.ContactState, PMDC'});a=copy.deepcopy(read('night_slash')['Object']['HitboxAction']);a.update(Range=2,StopAtHit=True,StopAtWall=True,HitTiles=False,TargetAlignments=4,CharAnim=5,WideAngle=0);a['Emitter']=copy.deepcopy(read('acrobatics')['Object']['HitboxAction']['Emitter']);a['ActionFX']['Sound']='DUN_Shadow_Sneak'
 else:
  other=json.loads((ROOT/'Hurlement-des-Roches-Lames/Generation-PMDO/V3/splintered_stormshards-v3-test-only.json').read_text())['Object']['HitboxAction'];a=copy.deepcopy(other);a['TileEmitter']=copy.deepcopy(read('searing_sunraze_smash')['Object']['HitboxAction']['TileEmitter']);a['ActionFX']['Sound']='';a['LagBehindTime']=0
 o['HitboxAction']=a;o['Data']['BeforeActions']=[event(tag+'V1_Charge',0)]
 if tag in ('Selene','Apocalypse'):
  o['Data']['BeforeHits']=[event(tag+'V1_Ignore',-100)];o['Data']['AfterActions']=[event(tag+'V1_Restaure',100)]
 if tag=='Apocalypse':o['Data']['BeforeTryActions']=[event('ApocalypseV1_Categorie',-100)]
 fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']=tag+'V1_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=64,AbsoluteDelay=True,Sound={'Selene':'DUN_Shadow_Ball','Apocalypse':'DUN_Hyper_Beam','Fauche':'DUN_Sucker_Punch'}[tag]);fx['ScreenMovement']={'MinShake':0,'MaxShake':2,'MaxShakeTime':12};o['Data']['HitFX']=fx
 (P/(skill+'-v1-test-only.json')).write_text(json.dumps(z,ensure_ascii=False,indent=2));print(tag,skill,'ok')
