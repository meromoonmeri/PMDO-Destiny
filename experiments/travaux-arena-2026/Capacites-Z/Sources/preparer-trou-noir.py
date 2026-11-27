#!/usr/bin/env python3
"""Prototype isolé : vortex d'accrétion et voile du vide, à restaurer après capture."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, io, struct, json, copy, shutil, math
H=Path('/home/user'); G=H/'.cache/destiny-test/game/PMDO-Destiny'; P=H/'Capacites-Z/Prototypes/Trou-Noir-des-Ombres/Generation-PMDO'; P.mkdir(parents=True,exist_ok=True)
def bank(name,sheet,w,h,mode,count,where):
 sheet.save(P/(name+'.png')); f=io.BytesIO();sheet.save(f,format='PNG');raw=f.getvalue();b=P/(name+'.dir');b.write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,mode,count));shutil.copy2(b,G/'Content'/where/b.name)
# Le ciel est la propre texture de cette attaque ; miroir pour un pavage sans bords francs.
src=Image.open(P/'source-ciel-vide.png').convert('RGBA').resize((128,72),Image.Resampling.NEAREST);src.putalpha(115);bg=Image.new('RGBA',(256,144))
for x,y,t in [(0,0,None),(128,0,Image.Transpose.FLIP_LEFT_RIGHT),(0,72,Image.Transpose.FLIP_TOP_BOTTOM),(128,72,Image.Transpose.ROTATE_180)]:bg.alpha_composite(src if t is None else src.transpose(t),(x,y))
bank('Trou_Noir_Vide',bg,256,144,0,1,'BG')
# Une image source IA, dont la rotation, l'échelle et l'opacité fabriquent les intermédiaires.
a=np.array(Image.open(P/'source-vortex.png').convert('RGB').resize((78,78),Image.Resampling.NEAREST));c=a.astype('int16');mask=(c[:,:,1]>130)&(c[:,:,1]>c[:,:,0]+45)&(c[:,:,1]>c[:,:,2]+45);im=Image.fromarray(np.dstack((a,np.where(mask,0,255).astype('uint8'))),'RGBA')
N=96;frames=[]
for i in range(22):
 if i<6:size=18+i*10;alpha=min(255,90+i*32)
 elif i<14:size=78;alpha=255
 else:size=max(4,78-(i-13)*10);alpha=max(0,255-(i-13)*30)
 part=im.resize((size,size),Image.Resampling.NEAREST).rotate(-i*12,resample=Image.Resampling.NEAREST,expand=True);part.putalpha(part.getchannel('A').point(lambda x:x*alpha//255));f=Image.new('RGBA',(N,N));f.alpha_composite(part,((N-part.width)//2,(N-part.height)//2));frames.append(f)
sheet=Image.new('RGBA',(N*len(frames),N*8));check=Image.new('RGBA',(N*len(frames),N),(35,32,39,255))
for y in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,y*N))
for i,f in enumerate(frames):check.alpha_composite(f,(i*N,0));f.save(P/f'frame-{i:02}.png')
check.convert('RGB').save(P/'progression-controle.png');bank('Trou_Noir_Vortex',sheet,N,N,4,len(frames),'Particle')
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'black_hole_eclipse-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('black_hole_eclipse');p.write_text(json.dumps(orig,ensure_ascii=False,indent=2))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=100
# Cocon Fatal utilise une OffsetAction cible unique ; le pré-effet vient de Psyko.
act=copy.deepcopy(read('psychic')['Object']['HitboxAction']);act['Range']=2;act['HitTiles']=False;act['TargetAlignments']=4;act['LagBehindTime']=0
# Cible unique : case située à deux pas dans la direction de visée.
act['HitArea']=0;act['BurstTiles']=0
act['TileEmitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0}
ov=act['PreActions'][0]['Emitter'];ov['Anim']['AnimIndex']='Trou_Noir_Vide';ov['Anim']['Alpha']=230;ov['Anim']['FrameTime']=1;ov['Movement']={'X':-5,'Y':3};ov['FadeIn']=15;ov['FadeOut']=30;ov['TotalTime']=150;ov['Layer']=0
act['PreActions'][0]['Sound']='DUN_Radar_Orb';act['ActionFX']['Sound']='DUN_Thief'
hit=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='Trou_Noir_Vortex';hit['Emitter']['Anim']['Anim']['FrameTime']=3;hit['Emitter']['LocHeight']=4;hit['Sound']='DUN_Dark_Pulse';a['HitboxAction']=act;a['Data']['HitFX']=hit
for sound in [act['PreActions'][0]['Sound'],act['ActionFX']['Sound'],hit['Sound']]:assert (G/'Content/Sound/Battle'/(sound+'.ogg')).exists(),sound
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'black_hole_eclipse-test-only.json').write_text(s);(G/'Data/Skill/black_hole_eclipse.json').write_text(s)
print('22 poses recomposées, vortex et ciel du vide, action expérimentale')
