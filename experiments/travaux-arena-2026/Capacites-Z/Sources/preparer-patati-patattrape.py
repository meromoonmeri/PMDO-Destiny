#!/usr/bin/env python3
"""Banc Mimiqui : déguisement natif agrandi, effets Fée natifs et impact IA."""
from pathlib import Path
from PIL import Image
import numpy as np,math,struct,io,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Patati-Patattrape/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
a=np.asarray(Image.open(P/'source-ia-fouillis-feerique.png').convert('RGB')).astype('float32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];score=np.maximum(r,b);alpha=np.clip((1-np.maximum(g-score,0)/255-.14)/.86,0,1);safe=np.maximum(alpha,1/255);a[:,:,1]=np.minimum(np.clip((g-255*(1-alpha))/safe,0,255),score+18);cloud=Image.fromarray(np.dstack([np.uint8(np.clip(a,0,255)),np.uint8(alpha*255)]),'RGBA');cloud=cloud.crop(cloud.getbbox());cloud.thumbnail((103,103),Image.Resampling.LANCZOS);cloud.save(P/'fouillis-feerique-detoure.png')
raw=(G/'Content/Chara/778.chara').read_bytes();pos=raw.find(b'\x89PNG\r\n\x1a\n');length=struct.unpack_from('<q',raw,pos-8)[0];sheet=Image.open(io.BytesIO(raw[pos:pos+length])).convert('RGBA');w,h,_,_=struct.unpack_from('<iiii',raw,pos+length);sprite=sheet.crop((0,0,w,h));sprite=sprite.crop(sprite.getbbox());sprite.save(P/'mimiqui-pose-native.png')
N=128;T=80;frames=[]
for t in range(T):
 f=Image.new('RGBA',(N,N))
 if t<59:
  p=min(1,(t+1)/10);fade=min(1,(59-t)/8);sw=round(20+54*p);sh=round(24+63*p);s=sprite.resize((sw,sh),Image.Resampling.NEAREST);s=s.rotate(4*math.sin(t*.75) if t>10 else 0,Image.Resampling.NEAREST,expand=True);s.putalpha(s.getchannel('A').point(lambda x:round(x*fade)));f.alpha_composite(s,(round((N-s.width)/2+2*math.sin(t*.7)),round((N-s.height)/2)))
 if t>=34:
  phase=min(1,(t-34)/11);end=min(1,(T-t)/13);sz=round(45+60*phase);v=cloud.resize((sz,sz),Image.Resampling.LANCZOS);v.putalpha(v.getchannel('A').point(lambda x:round(x*phase*end*.8)));f.alpha_composite(v,((N-sz)//2,(N-sz)//2))
 frames.append(f)
sheet=Image.new('RGBA',(N*T,N*8));prev=Image.new('RGBA',(N*8,N),(28,30,33,255))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
for j,i in enumerate([0,8,15,25,35,45,55,70]):prev.alpha_composite(frames[i],(j*N,0))
b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/'Patati_Impact.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,T));prev.convert('RGB').save(P/'Patati-impact-progression.jpg')
z=read('lets_snuggle_forever');a=z['Object'];assert not a['Released'] and a['Data']['Element']=='fairy' and a['Data']['Category']==1 and any(x.get('Power')==190 for x in a['Data']['SkillStates']);a['Released']=True;a['BaseCharges']=1;a['Data']['SkillStates'].insert(0,{'$type':'PMDC.Dungeon.ContactState, PMDC'})
# Saut jusqu'à la première cible : Pounce + poussière et étoiles de Câlinerie.
rough=read('play_rough')['Object'];act=copy.deepcopy(read('pounce')['Object']['HitboxAction']);act.update(Range=2,StopAtHit=True,StopAtWall=True,HitTiles=False,TargetAlignments=4,AppearanceMod=4,WideAngle=1);act['TileEmitter']=copy.deepcopy(rough['HitboxAction']['TileEmitter']);act['PreActions']=[];act['ActionFX']['Sound']='DUN_Tackle';a['HitboxAction']=act
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='Patati_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=80,AbsoluteDelay=True,Sound='DUN_Wake_Up_Slap');a['Data']['HitFX']=fx
ex=copy.deepcopy(rough['HitboxAction']['ActionFX']);ex['Emitter']=copy.deepcopy(rough['HitboxAction']['Emitter']);a['Explosion']['ExplodeFX']=ex
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'Patati_Charge','ArgTable':'{}'}}]
(P/'lets_snuggle_forever-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Banque, fiche et textures natifs pour banc créés ; jeu inchangé.')
