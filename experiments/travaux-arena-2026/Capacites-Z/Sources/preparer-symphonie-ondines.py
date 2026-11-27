#!/usr/bin/env python3
"""Oratoria, effets IA et ressources Aria de l'Écume pour banc isolé."""
from pathlib import Path
from PIL import Image
import numpy as np,math,struct,io,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Symphonie-des-Ondines/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
def detach(name,sz):
 a=np.asarray(Image.open(P/name).convert('RGB')).astype('float32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];score=np.maximum(r,b);alpha=np.clip((1-np.maximum(g-score,0)/255-.14)/.86,0,1);safe=np.maximum(alpha,1/255);a[:,:,1]=np.minimum(np.clip((g-255*(1-alpha))/safe,0,255),score+18);im=Image.fromarray(np.dstack([np.uint8(np.clip(a,0,255)),np.uint8(alpha*255)]),'RGBA');im=im.crop(im.getbbox());im.thumbnail((sz,sz),Image.Resampling.LANCZOS);im.save(P/name.replace('source-ia-','detoure-'));return im
def dirbank(name,frames):
 w,h=frames[0].size;sheet=Image.new('RGBA',(w*len(frames),h*8));prev=Image.new('RGBA',(w*8,h),(27,32,37,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*w,row*h))
 for j in range(8):prev.alpha_composite(frames[round(j*(len(frames)-1)/7)],(j*w,0))
 b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',w,h,4,len(frames)));prev.convert('RGB').save(P/(name+'-progression.jpg'))
def beam(name,heads):
 n=len(heads);w,h=heads[0].size;sheet=Image.new('RGBA',(w*n,h+2));rect=[]
 for seq,sw,sh,y in [(heads,w,h,0),([Image.new('RGBA',(1,1))]*n,1,1,h),([Image.new('RGBA',(1,1))]*n,1,1,h+1)]:
  for i,im in enumerate(seq):sheet.alpha_composite(im,(i*sw,y));rect.append((i*sw,y,sw,sh))
 b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();(P/(name+'.beam')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<i',len(rect))+b''.join(struct.pack('<iiii',*r) for r in rect)+struct.pack('<i',n))
sphere=detach('source-ia-sphere-eau.png',66);impact=detach('source-ia-impact-eau.png',112);heads=[]
for t in range(36):
 f=Image.new('RGBA',(80,80));s=sphere.rotate(4*math.sin(t*math.tau/36),resample=Image.Resampling.BICUBIC,expand=False);f.alpha_composite(s,((80-s.width)//2,(80-s.height)//2));heads.append(f)
beam('Ondines_Sphere',heads)
# Formation au-dessus du Pokémon : des bulles natives d'Aria accompagnent le chant.
frames=[];N=128
for t in range(72):
 f=Image.new('RGBA',(N,N));p=min(1,max(0,(t-12)/40));sz=round(8+61*p);v=heads[t%36].resize((sz,sz),Image.Resampling.LANCZOS);fade=min(1,(t+1)/8,(72-t)/5);v.putalpha(v.getchannel('A').point(lambda x:round(x*fade)));f.alpha_composite(v,((N-sz)//2,round(N/2-sz*.72)));frames.append(f)
dirbank('Ondines_Charge',frames)
frames=[];N=128
for t in range(42):
 f=Image.new('RGBA',(N,N));s=.25+.75*min(1,t/11);w=max(1,round(impact.width*s));h=max(1,round(impact.height*s));v=impact.resize((w,h),Image.Resampling.LANCZOS);fade=min(1,(t+1)/3,(42-t)/12);v.putalpha(v.getchannel('A').point(lambda x:round(x*fade*.9)));f.alpha_composite(v,((N-w)//2,(N-h)//2));frames.append(f)
dirbank('Ondines_Impact',frames)
z=read('oceanic_operetta');a=z['Object'];assert not a['Released'] and a['Data']['Element']=='water' and a['Data']['Category']==2 and any(x.get('Power')==195 for x in a['Data']['SkillStates']);a['Released']=True;a['BaseCharges']=1
# Projectile PMDO existant, première cible uniquement. Pas de statut Son ou retrait de brûlure : la Z n'a pas ces effets.
act=copy.deepcopy(read('water_pulse')['Object']['HitboxAction']);act.update(Range=4,StopAtHit=True,StopAtWall=True,TargetAlignments=4,HitTiles=False,Speed=8);act['Anim']['AnimIndex']='Ondines_Sphere';act['Anim']['FrameTime']=1;act['PreActions']=[];act['ActionFX']['Sound']='DUN_Bubble';a['HitboxAction']=act
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='Ondines_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=42,AbsoluteDelay=True,Sound='DUN_Hydro_Pump');a['Data']['HitFX']=fx
a['Explosion']['ExplodeFX']=copy.deepcopy(read('sparkling_aria')['Object']['Data']['HitFX'])
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'Ondines_Charge','ArgTable':'{}'}}]
(P/'oceanic_operetta-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Banques, projectile et fiche de banc créés ; jeu inchangé.')
