#!/usr/bin/env python3
"""Prépare un banc Lougaroc : roches convergentes, Lame de Roc native."""
from pathlib import Path
from PIL import Image
import numpy as np,math,struct,io,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Hurlement-des-Roches-Lames/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
a=np.asarray(Image.open(P/'source-ia-roche-lame.png').convert('RGB')).astype('float32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];score=np.maximum(r,b);alpha=np.clip((1-np.maximum(g-score,0)/255-.14)/.86,0,1);safe=np.maximum(alpha,1/255);a[:,:,1]=np.minimum(np.clip((g-255*(1-alpha))/safe,0,255),score+18);rock=Image.fromarray(np.dstack([np.uint8(np.clip(a,0,255)),np.uint8(alpha*255)]),'RGBA');rock=rock.crop(rock.getbbox());rock.thumbnail((22,49),Image.Resampling.LANCZOS);rock.save(P/'roche-lame-detouree.png')
# Extraire la pierre native Lame de Roc et la semer en éclats au moment de l'impact.
raw=(G/'Content/Particle/Stone_Edge_Rock.dir').read_bytes();n=struct.unpack_from('<q',raw)[0];sheet=Image.open(io.BytesIO(raw[8:8+n])).convert('RGBA');w,h,_,count=struct.unpack_from('<iiii',raw,8+n);native=sheet.crop((min(3,count-1)*w,0,(min(3,count-1)+1)*w,h));native=native.crop(native.getbbox());native.thumbnail((12,12),Image.Resampling.NEAREST)
N=144;frames=[];T=68
for t in range(T):
 f=Image.new('RGBA',(N,N));fade=min(1,(T-t)/10)
 # Apparition, lévitation, puis convergence vers la cible.
 for j in range(6):
  phase=max(0,min(1,(t-j*2)/11));a=j*math.tau/6-math.pi/2;dist=51 if t<34 else max(7,51-(t-34)*4.4);x=72+dist*math.cos(a);y=72+dist*.72*math.sin(a)
  v=rock.rotate(90-math.degrees(a+math.pi),resample=Image.Resampling.BICUBIC,expand=True);v.putalpha(v.getchannel('A').point(lambda x:round(x*phase*fade)));f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
 if 43<=t<62:
  for j in range(9):
   ang=j*math.tau/9;dist=8+(t-43)*1.9;x=72+dist*math.cos(ang);y=72+dist*.7*math.sin(ang);v=native.copy();v.putalpha(v.getchannel('A').point(lambda x:round(x*min(1,(62-t)/9))));f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
 frames.append(f)
sheet=Image.new('RGBA',(N*T,N*8));prev=Image.new('RGBA',(N*8,N),(28,30,33,255))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
for j,i in enumerate([0,7,14,23,34,42,50,62]):prev.alpha_composite(frames[i],(j*N,0))
b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/'RochesLames_Impact.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,T));prev.convert('RGB').save(P/'RochesLames_Impact-progression.jpg')
z=read('splintered_stormshards');a=z['Object'];assert not a['Released'] and a['Data']['Element']=='rock' and a['Data']['Category']==1 and any(x.get('Power')==190 for x in a['Data']['SkillStates']);a['Released']=True;a['BaseCharges']=1
# Lame de Roc cible la case à deux cases. Texture et son natifs conservés.
act=copy.deepcopy(read('stone_edge')['Object']['HitboxAction']);act.update(HitTiles=False,TargetAlignments=4,Range=2);a['HitboxAction']=act
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='RochesLames_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=68,AbsoluteDelay=True,Sound='DUN_Rock_Slide');a['Data']['HitFX']=fx
event=lambda s:{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':s,'ArgTable':'{}'}}
a['Data']['BeforeActions']=[event('RochesLames_Hurlement')];a['Data']['AfterActions']=[event('RochesLames_EffacerChamps')]
(P/'splintered_stormshards-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Banque et fiche de banc créées ; jeu inchangé.')
