#!/usr/bin/env python3
"""Banc Sol : fissures radiales sous le lanceur, pointes surgissant sous les cibles."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,copy,json,shutil
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Eruption-Geo-Sismique/Generation-PMDO'
def cut(name,size):
 im=Image.open(P/name).convert('RGB');im.thumbnail((size,size),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');mask=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45);out=Image.fromarray(np.dstack((a,np.where(mask,0,255).astype('uint8'))),'RGBA');return out.crop(out.getbbox())
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));control=Image.new('RGBA',(N*len(frames),N),(36,32,27,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
 for i,f in enumerate(frames):control.alpha_composite(f,(i*N,0));f.save(P/(name+f'-{i:02}.png'))
 control.convert('RGB').save(P/(name+'-progression.png'));sheet.save(P/(name+'.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();f=P/(name+'.dir');f.write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(f,G/'Content/Particle'/f.name)
crack=cut('fissures-source.png',128);spike=cut('pointe-source.png',60)
# 24 poses : fissure naissante, ramification, tremblement, extinction.
N=144;frames=[]
for i in range(24):
 size=min(128,16+i*13);alpha=210 if i<17 else max(0,210-(i-16)*27);part=crack.resize((size,size),Image.Resampling.NEAREST);part.putalpha(part.getchannel('A').point(lambda x:x*alpha//255));f=Image.new('RGBA',(N,N));f.alpha_composite(part,((N-size)//2,(N-size)//2));frames.append(f)
bank('GeoSismique_Fissures',frames,N)
# 18 poses : roche qui surgit ancrée à sa base, halte, effritement et repli.
N=80;frames=[]
for i in range(18):
 f=Image.new('RGBA',(N,N));
 if i<6:height=4+i*8
 elif i<12:height=48
 else:height=max(0,48-(i-11)*8)
 if height:
  part=spike.resize((34,height),Image.Resampling.NEAREST);part.putalpha(part.getchannel('A').point(lambda x:x*(255 if i<13 else max(0,255-(i-12)*45))//255));f.alpha_composite(part,(23,52-height))
 if 5<=i<=14:
  draw=ImageDraw.Draw(f)
  for j in range(7):
   x=40+((j*19+i*7)%45)-22;y=48-((j*13+i*4)%30);draw.rectangle((x,y,x+1+(j%2),y+1),fill=(175+10*(j%3),91,32,max(0,230-max(0,i-10)*35)))
 frames.append(f)
bank('GeoSismique_Pointe',frames,N)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'tectonic_rage-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('tectonic_rage');p.write_text(json.dumps(orig,ensure_ascii=False,indent=2))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for st in a['Data']['SkillStates']:
 if st.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):st['Power']=65
# Séisme PMDO : aire Full autour du lanceur ; pas de destruction de terrain sur ce prototype.
act=copy.deepcopy(read('earthquake')['Object']['HitboxAction']);act['Range']=2;act['HitArea']=0;act['HitTiles']=False;act['TargetAlignments']=4;act['LagBehindTime']=0;act['Emitter']={'$type':'RogueEssence.Content.EmptyCircleSquareEmitter, RogueEssence','LocHeight':0};act['TileEmitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0}
pre=copy.deepcopy(read('dig')['Object']['HitboxAction']['PreActions'][0]);pre['Sound']='EVT_CH20_Tower_Cracks';pre['Delay']=30;pre['AbsoluteDelay']=True;em=pre['Emitter'];em['LocHeight']=0;em['Layer']=0;em['Anim']['Anim']['AnimIndex']='GeoSismique_Fissures';em['Anim']['Anim']['FrameTime']=3;act['PreActions']=[pre];act['ActionFX']['Sound']='DUN_Earth_Power';act['ActionFX']['ScreenMovement']={'MinShake':0,'MaxShake':9,'MaxShakeTime':35};a['HitboxAction']=act
hit=copy.deepcopy(read('bullet_punch')['Object']['Data']['HitFX']);hit['Delay']=30;hit['AbsoluteDelay']=True;hit['Sound']='DUN_Rock_Smash';hit['Emitter']['Anim']['Anim']['AnimIndex']='GeoSismique_Pointe';hit['Emitter']['Anim']['Anim']['FrameTime']=3;hit['Emitter']['LocHeight']=0;a['Data']['HitFX']=hit
for sound in [pre['Sound'],act['ActionFX']['Sound'],hit['Sound']]:assert (G/'Content/Sound/Battle'/(sound+'.ogg')).exists(),sound
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'tectonic_rage-test-only.json').write_text(s);(G/'Data/Skill/tectonic_rage.json').write_text(s)
print('Fissures 24 poses ; pointes 18 poses ; aire 5x5')
