#!/usr/bin/env python3
"""Prototype isolé Piqué Supersonique : décollage, DashAction de chute, impact aérien."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil,math
H=Path('/home/user');R=H/'Capacites-Z';G=H/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Pique-Supersonique/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
def cut(name,n):
 im=Image.open(P/name).convert('RGB');im.thumbnail((n,n),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45);o=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA');return o.crop(o.getbbox())
def paste(im,p,size,x,y,alpha=255):
 if alpha<=0:return
 s=p.resize((int(size),int(size)),Image.Resampling.NEAREST);s.putalpha(s.getchannel('A').point(lambda v:v*alpha//255));im.alpha_composite(s,(round(x-size/2),round(y-size/2)))
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));control=Image.new('RGBA',(N*len(frames),N),(25,30,38,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(N*i,N*row))
 for i,f in enumerate(frames):control.alpha_composite(f,(N*i,0))
 control.convert('RGB').save(P/(name+'-progression.png'));sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();p=P/(name+'.dir');p.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(p,G/'Content/Particle'/p.name)
wind=cut('source-sillage-vent.png',80);impact=cut('source-impact-aerien.png',80)
# Sillage tournant, attaché au corps pendant la descente.
N=96;frames=[]
for t in range(12):
 f=Image.new('RGBA',(N,N));rot=wind.rotate(-t*30,resample=Image.Resampling.NEAREST,expand=False);paste(f,rot,53,48,48,175);frames.append(f)
bank('PiqueSuper_Sillage',frames,N)
# Couronne, choc blanc-bleu et léger anneau de compression au sol.
N=112;frames=[]
for t in range(28):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
 if t<16:
  k=t;sz=[8,18,30,42,52,59,64,62,58,53,47,40,33,26,19,10][k];opacity=255 if k<7 else max(0,255-(k-6)*27);paste(f,impact,sz,56,56,opacity);d=ImageDraw.Draw(f)
 if 2<=t<24:
  k=t-2;r=min(42,k*3);a=max(0,190-k*9);d.ellipse((56-r,61-r//3,56+r,61+r//3),outline=(171,228,255,a),width=2)
 frames.append(f)
bank('PiqueSuper_Impact',frames,N)
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'supersonic_skystrike-original.json'
if p.exists():o=json.loads(p.read_text())
else:o=read('supersonic_skystrike');p.write_text(json.dumps(o,ensure_ascii=False,indent=2))
z=copy.deepcopy(o);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for st in a['Data']['SkillStates']:
 if st.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):st['Power']=90
act=copy.deepcopy(read('fly')['Object']['HitboxAction']);act['Range']=3;act['StopAtHit']=True;act['StopAtWall']=True;act['TargetAlignments']=4;act['HitTiles']=False;act['AppearanceMod']=1;act['Anim']['AnimIndex']='PiqueSuper_Sillage';act['Anim']['FrameTime']=2;act['ActionFX']['Sound']='DUN_Fly';a['HitboxAction']=act
hit=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='PiqueSuper_Impact';hit['Emitter']['Anim']['Anim']['FrameTime']=2;hit['Delay']=36;hit['AbsoluteDelay']=True;hit['Sound']='DUN_Sky_Attack';a['Data']['HitFX']=hit
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'PiqueSuper_Decollage','ArgTable':'{}'}}]
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'supersonic_skystrike-test-only.json').write_text(s);(G/'Data/Skill/supersonic_skystrike.json').write_text(s)
e=G/'Data/Script/origin/event_battle.lua';bak=H/'.cache/destiny-test/event-battle-avant-pique.lua'
if not bak.exists():shutil.copy2(e,bak)
shutil.copy2(bak,e)
with e.open('a') as f:f.write('\n'+(R/'Sources/pique-supersonique-decollage.lua').read_text())
print('Piqué : décollage natif + DashAction DropDown + sillage et choc ; fiche test-only')
