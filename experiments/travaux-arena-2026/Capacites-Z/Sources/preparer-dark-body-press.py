#!/usr/bin/env python3
"""Produit banques et fiche expérimentale ; ne touche pas au jeu."""
from pathlib import Path
from PIL import Image
import numpy as np, math,io,struct,json,copy
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Dark-Body-Press/Generation-PMDO'
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
def detach(name,sz):
 a=np.asarray(Image.open(P/name).convert('RGB')).astype('float32');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];score=np.maximum(r,b);alpha=np.clip((1-np.maximum(g-score,0)/255-.14)/.86,0,1);safe=np.maximum(alpha,1/255);a[:,:,1]=np.minimum(np.clip((g-255*(1-alpha))/safe,0,255),score+18);im=Image.fromarray(np.dstack([np.uint8(np.clip(a,0,255)),np.uint8(alpha*255)]),'RGBA');im=im.crop(im.getbbox());im.thumbnail((sz,sz),Image.Resampling.LANCZOS);im.save(P/(name.replace('source-ia-','detoure-')));return im
def bank(name,frames,N):
 sheet=Image.new('RGBA',(N*len(frames),N*8));preview=Image.new('RGBA',(N*8,N),(25,27,34,255))
 for row in range(8):
  for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
 for j in range(8):preview.alpha_composite(frames[round(j*(len(frames)-1)/7)],(j*N,0))
 b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)));preview.convert('RGB').save(P/(name+'-progression.jpg'))
charge=detach('source-ia-charge-tenebres.png',82);impact=detach('source-ia-impact-tenebres.png',112)
frames=[];N=112
for t in range(48):
 f=Image.new('RGBA',(N,N));s=.54+.40*min(1,t/34);w=max(1,round(charge.width*s));h=max(1,round(charge.height*s));v=charge.resize((w,h),Image.Resampling.LANCZOS).rotate(t*1.8,resample=Image.Resampling.BICUBIC,expand=True);fade=min(1,(t+1)/8,(48-t)/7);v.putalpha(v.getchannel('A').point(lambda x:round(x*fade*.8)));f.alpha_composite(v,((N-v.width)//2,(N-v.height)//2));frames.append(f)
bank('DarkBody_Charge',frames,N)
frames=[];N=128
for t in range(36):
 f=Image.new('RGBA',(N,N));s=.25+.75*min(1,t/9);w=max(1,round(impact.width*s));h=max(1,round(impact.height*s));v=impact.resize((w,h),Image.Resampling.LANCZOS);fade=min(1,(t+1)/3,(36-t)/11);v.putalpha(v.getchannel('A').point(lambda x:round(x*fade*.88)));f.alpha_composite(v,((N-w)//2,(N-h)//2));frames.append(f)
bank('DarkBody_Impact',frames,N)
z=read('malicious_moonsault');a=z['Object'];assert not a['Released'];assert a['Data']['Element']=='dark' and a['Data']['Category']==1 and any(x.get('Power')==180 for x in a['Data']['SkillStates']);a['Released']=True;a['BaseCharges']=1;a['Data']['SkillStates'].insert(0,{'$type':'PMDC.Dungeon.ContactState, PMDC'})
act=copy.deepcopy(read('night_slash')['Object']['HitboxAction']);act.update(Range=3,StopAtHit=True,StopAtWall=True,HitTiles=True,TargetAlignments=4,CharAnim=5);act['Emitter']=copy.deepcopy(read('acrobatics')['Object']['HitboxAction']['Emitter']);act['ActionFX']['Sound']='DUN_Night_Slash';a['HitboxAction']=act
# Les murs ordinaires sont détruits par l'événement de terrain PMDO, seulement dans la trajectoire touchée.
a['Data']['OnHitTiles']=copy.deepcopy(read('head_smash')['Object']['Data']['OnHitTiles'])
fx=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);fx['Emitter']['Anim']['Anim']['AnimIndex']='DarkBody_Impact';fx['Emitter']['Anim']['Anim']['FrameTime']=1;fx.update(Delay=36,AbsoluteDelay=True,Sound='DUN_Giga_Impact');a['Data']['HitFX']=fx
a['Explosion']['HitTiles']=True
a['Explosion']['ExplodeFX']=copy.deepcopy(read('night_slash')['Object']['Data']['HitFX'])
a['Data']['BeforeActions']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'DarkBody_Charge','ArgTable':'{}'}}]
(P/'malicious_moonsault-v1-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Fiche de banc et banques créées ; aucun jeu modifié.')
