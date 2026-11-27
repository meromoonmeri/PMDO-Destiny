#!/usr/bin/env python3
"""V2 de banc : disque animé centré au lanceur et événement de terrain intégré à la fiche."""
from pathlib import Path
from PIL import Image
import numpy as np,io,struct,json,copy,shutil,math
H=Path.home(); G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Trou-Noir-des-Ombres/Generation-PMDO'
def cut(name,size):
 a=np.array(Image.open(P/name).convert('RGB').resize((size,size),Image.Resampling.NEAREST));b=a.astype('int16');mask=(b[:,:,1]>125)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45)
 return Image.fromarray(np.dstack((a,np.where(mask,0,255).astype('uint8'))),'RGBA')
def bank(name,sheet,w,h,mode,count,where):
 sheet.save(P/(name+'.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();f=P/(name+'.dir');f.write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',w,h,mode,count));shutil.copy2(f,G/'Content'/where/f.name)
birth=cut('source-naissance-v2.png',92);ring=cut('source-vortex-geant-v2.png',130);N=160;frames=[]
def place(im,size,angle,opacity):
 part=im.resize((size,size),Image.Resampling.NEAREST).rotate(angle,resample=Image.Resampling.NEAREST,expand=True)
 part.putalpha(part.getchannel('A').point(lambda q:q*opacity//255));f=Image.new('RGBA',(N,N));f.alpha_composite(part,((N-part.width)//2,(N-part.height)//2));return f
# 32 frames : naissance, ouverture, rotation, repli et extinction.
for i in range(32):
 if i<5: f=place(birth,12+8*i,-i*12,150+i*20)
 elif i<12:
  t=i-5;f=place(ring,47+t*14,-i*10,145+t*14)
 elif i<22: f=place(ring,130,-i*10,225)
 else:
  t=i-22;f=place(ring,max(2,130-t*14),-i*10,max(0,225-t*24))
 frames.append(f)
sheet=Image.new('RGBA',(N*len(frames),N*8));control=Image.new('RGBA',(N*len(frames),N),(32,35,32,255))
for y in range(8):
 for x,f in enumerate(frames):sheet.alpha_composite(f,(x*N,y*N))
for x,f in enumerate(frames):control.alpha_composite(f,(x*N,0));f.save(P/f'v2-frame-{x:02}.png')
control.convert('RGB').save(P/'v2-progression.png');bank('Trou_Noir_5x5_V2',sheet,N,N,4,len(frames),'Particle')
# La texture de ciel V1 est conservée dans le dossier persistant.
shutil.copy2(P/'Trou_Noir_Vide.dir',G/'Content/BG/Trou_Noir_Vide.dir')
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
a=copy.deepcopy(json.loads((P/'black_hole_eclipse-original.json').read_text())['Object']);orig=read('black_hole_eclipse');z=copy.deepcopy(orig);z['Object']=a;a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=100
act=copy.deepcopy(read('petal_blizzard')['Object']['HitboxAction']);act['Range']=2;act['HitArea']=0;act['HitTiles']=True;act['TargetAlignments']=4;act['Speed']=10;act['LagBehindTime']=0
act['Emitter']={'$type':'RogueEssence.Content.EmptyCircleSquareEmitter, RogueEssence','LocHeight':0};act['TileEmitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0}
# Voile spécifique existant et unique vortex d'attaque, émis depuis le lanceur.
psy=read('psychic')['Object']['HitboxAction']['PreActions'][0];veil=copy.deepcopy(psy);ov=veil['Emitter'];ov['Anim']['AnimIndex']='Trou_Noir_Vide';ov['Anim']['Alpha']=180;ov['Anim']['FrameTime']=1;ov['Movement']={'X':-5,'Y':3};ov['FadeIn']=12;ov['FadeOut']=24;ov['TotalTime']=125;ov['Layer']=0;veil['Sound']='DUN_Dark_Void';veil['Delay']=0
vortex=copy.deepcopy(read('dig')['Object']['HitboxAction']['PreActions'][0]);vortex['Sound']='DUN_Dark_Pulse';vortex['Delay']=65;vortex['AbsoluteDelay']=True;e=vortex['Emitter'];e['LocHeight']=0;e['Layer']=0;e['Offset']=0;e['UseDest']=False;e['Anim']['Anim']['AnimIndex']='Trou_Noir_5x5_V2';e['Anim']['Anim']['FrameTime']=3;e['Anim']['Anim']['Alpha']=255
act['PreActions']=[veil,vortex];act['ActionFX']['Emitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0};act['ActionFX']['Sound']='EVT_EP_Darkrai_Portal_Break';a['HitboxAction']=act
# L'événement s'exécute via la capacité : retire les murs pendant l'apparition du vortex.
a['Data']['OnActions'].append({'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'TrouNoirV2_BriserMurs','ArgTable':'{}'}})
for sound in [veil['Sound'],vortex['Sound'],act['ActionFX']['Sound']]:assert (G/'Content/Sound/Battle'/(sound+'.ogg')).exists(),sound
s=json.dumps(z,indent=2,ensure_ascii=False);(P/'black_hole_eclipse-v2-test-only.json').write_text(s);(G/'Data/Skill/black_hole_eclipse.json').write_text(s)
# Installer la fonction dans l'événement d'origine en copie isolée, après sauvegarde.
p=G/'Data/Script/origin/event_battle.lua';bak=H/'.cache/destiny-test/event-battle-avant-trou-noir-v2.lua'
if not bak.exists():shutil.copy2(p,bak)
if 'function BATTLE_SCRIPT.TrouNoirV2_BriserMurs' in p.read_text(encoding='utf-8-sig'):
 raise RuntimeError('Événement V2 déjà présent : restaurer event_battle avant de réinstaller')
with p.open('a',encoding='utf-8') as f:f.write('\n\n'+(H/'Capacites-Z/Sources/trou-noir-v2-effet-terrain.lua').read_text())
print('V2 installée dans copie isolée : 32 poses, zone Full rayon 2, événement mur')
