#!/usr/bin/env python3
# Prototype signature de Mew en copie jetable.
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,io,struct,json,copy,shutil
H=Path('/home/user');G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Supernova-Originelle/Generation-PMDO';N=80

def bank(name,sheet,w,h,mode,count,where):
 sheet.save(P/(name+'.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();f=P/(name+'.dir');f.write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',w,h,mode,count));shutil.copy2(f,G/'Content'/where/(name+'.dir'))
# Ciel cosmique créé pour cette attaque, avec tuilage miroir et alpha de visibilité.
src=Image.open(P/'constellation-source.png').convert('RGBA').resize((128,72),Image.Resampling.NEAREST);src.putalpha(105);bg=Image.new('RGBA',(256,144))
for x,y,tr in [(0,0,None),(128,0,Image.Transpose.FLIP_LEFT_RIGHT),(0,72,Image.Transpose.FLIP_TOP_BOTTOM),(128,72,Image.Transpose.ROTATE_180)]:bg.alpha_composite(src if tr is None else src.transpose(tr),(x,y))
bank('Supernova_Constellation',bg,256,144,0,1,'BG')
# Emblème orbital formé autour de chaque cible, puis se resserre et se dissout.
im=Image.open(P/'astre-cible.png').convert('RGB').resize((68,68),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>120)&(b[:,:,1]>b[:,:,0]+40)&(b[:,:,1]>b[:,:,2]+40);symbol=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA')
frames=[]
for size,ang,alpha in [(18,0,160),(30,0,200),(42,0,230),(54,0,255),(64,0,255),(68,0,255),(68,7,255),(68,14,255),(68,21,255),(68,28,255),(66,35,255),(58,42,230),(50,49,200),(36,56,160),(24,63,110),(10,70,60)]:
 part=symbol.resize((size,size),Image.Resampling.NEAREST).rotate(ang,resample=Image.Resampling.NEAREST,expand=True);part.putalpha(part.getchannel('A').point(lambda x:x*alpha//255));f=Image.new('RGBA',(N,N));f.alpha_composite(part,((N-part.width)//2,(N-part.height)//2));frames.append(f)
sheet=Image.new('RGBA',(N*len(frames),N*8));check=Image.new('RGBA',(N*len(frames),N),(25,23,35,255))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
for i,f in enumerate(frames):check.alpha_composite(f,(i*N,0));f.save(P/f'frame-{i:02}.png')
check.convert('RGB').resize((N*len(frames),N),Image.Resampling.NEAREST).save(P/'progression-controle.png');bank('Supernova_Orbite',sheet,N,N,4,len(frames),'Particle')
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'genesis_supernova-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('genesis_supernova');p.write_text(json.dumps(orig,ensure_ascii=False,indent=2))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for st in a['Data']['SkillStates']:
 if st.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):st['Power']=100
# Zone décalée, inspirée de Psyko ; paramètres provisoires et pas de Champ Psychique ici.
act=copy.deepcopy(read('psychic')['Object']['HitboxAction']);act['Range']=2;act['HitTiles']=False;act['TargetAlignments']=4;act['LagBehindTime']=0;act['TileEmitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0}
overlay=act['PreActions'][0]['Emitter'];overlay['Anim']['AnimIndex']='Supernova_Constellation';overlay['Anim']['Alpha']=230;overlay['Anim']['FrameTime']=1;overlay['Movement']={'X':2,'Y':-2};overlay['FadeIn']=15;overlay['FadeOut']=30;overlay['TotalTime']=145;overlay['Layer']=0
act['PreActions'][0]['Sound']='DUN_Cosmic_Power';act['ActionFX']['Sound']='DUN_Psybeam'
hit=copy.deepcopy(read('string_shot')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']='Supernova_Orbite';hit['Emitter']['Anim']['Anim']['FrameTime']=3;hit['Emitter']['LocHeight']=4;hit['Sound']='DUN_Aura_Sphere_2';a['HitboxAction']=act;a['Data']['HitFX']=hit
# Only sounds which exist in the test build.
for sound in (act['PreActions'][0]['Sound'],act['ActionFX']['Sound'],hit['Sound']):
 assert (G/'Content/Sound/Battle'/(sound+'.ogg')).exists(),sound
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'genesis_supernova-test-only.json').write_text(s);(G/'Data/Skill/genesis_supernova.json').write_text(s)
print('Supernova : zone, ciel cosmique IA, symbole orbital IA, 16 poses recomposées')
