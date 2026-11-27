#!/usr/bin/env python3
"""Symphonie V2 : gouttes, sphère pixel et jaillissement à partir des ressources Eau."""
from pathlib import Path
from PIL import Image,ImageDraw
import io,struct,json,copy,math
import numpy as np
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Symphonie-des-Ondines/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,N=struct.unpack_from('<iiii',b,8+k);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(N)]
def at(dst,src,x,y):dst.alpha_composite(src,(round(x-src.width/2),round(y-src.height/2)))
def bank(n,frames):
 w,h=frames[0].size;im=Image.new('RGBA',(w*len(frames),h*8))
 for j in range(8):
  for i,f in enumerate(frames):im.alpha_composite(f,(w*i,h*j))
 b=io.BytesIO();im.save(b,format='PNG');png=b.getvalue();(P/(n+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',w,h,4,len(frames)))
def beam(n,heads):
 count=len(heads);w,h=heads[0].size;im=Image.new('RGBA',(w*count,h+2));rect=[]
 for seq,sw,sh,y in ((heads,w,h,0),([Image.new('RGBA',(1,1))]*count,1,1,h),([Image.new('RGBA',(1,1))]*count,1,1,h+1)):
  for i,f in enumerate(seq):im.alpha_composite(f,(i*sw,y));rect.append((i*sw,y,sw,sh))
 b=io.BytesIO();im.save(b,format='PNG');png=b.getvalue();(P/(n+'.beam')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<i',len(rect))+b''.join(struct.pack('<iiii',*r) for r in rect)+struct.pack('<i',count))
a=np.array(Image.open(P/'source-v2-goutte-eau.png').convert('RGB'));r,g,b=[a[:,:,i].astype(int) for i in range(3)];m=(g<np.maximum(r,b)*1.1)|(g<65);y,x=np.where(m);drop=Image.fromarray(np.dstack((a,m.astype('uint8')*255)),'RGBA').crop((x.min(),y.min(),x.max()+1,y.max()+1)).resize((7,9),Image.Resampling.NEAREST)
bubble=native('Bubble_Pop_Blue');column=native('Water_Column_Ranger')
# Coeur d'eau en palette réduite : détails de surface déplacés dans chaque image.
heads=[]
for t in range(24):
 f=Image.new('RGBA',(64,64));d=ImageDraw.Draw(f);cx=cy=32
 d.ellipse((12,12,52,52),fill=(25,112,180,255));d.ellipse((14,13,50,50),fill=(50,169,221,255));d.ellipse((16,14,48,45),fill=(106,215,242,255));d.ellipse((19,16,46,39),fill=(155,235,250,255))
 mask=Image.new('L',(64,64));ImageDraw.Draw(mask).ellipse((14,13,50,50),fill=255);layer=Image.new('RGBA',(64,64));ld=ImageDraw.Draw(layer)
 for j in range(3):
  yy=24+j*7+(t//4)%7;points=[(x,round(yy+2*math.sin((x+t*1.2+j*3)/5))) for x in range(12,53)];ld.line(points,fill=(41,154,210,170),width=2)
 layer.putalpha(Image.composite(layer.getchannel('A'),Image.new('L',(64,64)),mask));f.alpha_composite(layer);d=ImageDraw.Draw(f);d.rectangle((22,18,29,20),fill=(232,255,255,255));d.rectangle((20,20,23,23),fill=(232,255,255,255))
 for j in range(3):
  a=j*math.tau/3+t*.12;x=32+25*math.cos(a);y=32+21*math.sin(a);v=bubble[min(len(bubble)-1,4+(t//5+j)%4)].resize((12,12),Image.Resampling.NEAREST);at(f,v,x,y)
 heads.append(f)
beam('OndinesV2_Sphere',heads)
charge=[]
for t in range(72):
 f=Image.new('RGBA',(96,96))
 for j in range(5):
  age=(t+j*11)%45; x=48+((-1)**j)*(10+j*3)-age*.08;y=66-age*.7;v=bubble[min(12,age//4)].resize((12,12),Image.Resampling.NEAREST);at(f,v,x,y)
 if t>=12:
  sz=round(8+48*min(1,(t-12)/35));v=heads[t%24].resize((sz,sz),Image.Resampling.NEAREST);at(f,v,48,33)
 charge.append(f)
bank('OndinesV2_Charge',charge)
impacts=[]
for t in range(42):
 f=Image.new('RGBA',(80,80));v=column[min(len(column)-1,t//2)].resize((68,68),Image.Resampling.NEAREST);at(f,v,40,40)
 for j in range(8):
  age=t-j*2
  if 0<=age<24:
   ang=j*math.tau/8;dist=age*.9;x=40+dist*math.cos(ang);y=40+dist*math.sin(ang)+age*age*.014;v=drop.rotate(j*45,Image.Resampling.NEAREST,expand=True);at(f,v,x,y)
 impacts.append(f)
bank('OndinesV2_Impact',impacts)
z=read('oceanic_operetta');a=z['Object'];a['Released']=True;a['BaseCharges']=1
act=copy.deepcopy(read('water_pulse')['Object']['HitboxAction']);act.update(Range=4,StopAtHit=True,StopAtWall=True,TargetAlignments=4,HitTiles=False,Speed=8);act['Anim']['AnimIndex']='OndinesV2_Sphere';act['Anim']['FrameTime']=1;act['PreActions']=[];act['ActionFX']['Sound']='DUN_Bubble';a['HitboxAction']=act
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='OndinesV2_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=42,AbsoluteDelay=True,Sound='DUN_Hydro_Pump');a['Data']['HitFX']=fx;a['Explosion']['ExplodeFX']=copy.deepcopy(read('sparkling_aria')['Object']['Data']['HitFX'])
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'OndinesV2_Charge','ArgTable':'{}'}}];(P/'oceanic_operetta-v2-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Animations et fiche préparées pour test isolé.')
