#!/usr/bin/env python3
# Pikachute Foudroyante : prototype signature en copie de banc.
from pathlib import Path
from PIL import Image
import numpy as np,io,struct,json,copy,shutil
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Pikachute-Foudroyante/Generation-PMDO';N=64
frames=[]
for name in ('aura-01.png','aura-02.png'):
 im=Image.open(P/name).convert('RGB').resize((52,52),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');m=(b[:,:,1]>130)&(b[:,:,1]>b[:,:,0]+40)&(b[:,:,1]>b[:,:,2]+40);pic=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA');f=Image.new('RGBA',(N,N));f.alpha_composite(pic,(6,6));frames.append(f)
frames=[frames[0],frames[1],frames[0].transpose(Image.Transpose.FLIP_LEFT_RIGHT),frames[1].transpose(Image.Transpose.FLIP_LEFT_RIGHT)]
name='Pikachute_Aura_IA';sheet=Image.new('RGBA',(N*len(frames),N*8));check=Image.new('RGBA',(N*len(frames),N),(30,27,35,255))
for r in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,r*N))
for i,f in enumerate(frames):check.alpha_composite(f,(i*N,0));f.save(P/f'aura-frame-{i:02}.png')
check.convert('RGB').resize((512,128),Image.Resampling.NEAREST).save(P/'aura-controle.png');sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'catastropika-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('catastropika');p.write_text(json.dumps(orig,indent=2,ensure_ascii=False))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for state in a['Data']['SkillStates']:
 if state.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):state['Power']=100
# Electacle PMDO : charge avec collision. Conserver Pikachu visible et éclairer la charge.
act=copy.deepcopy(read('volt_tackle')['Object']['HitboxAction']);act['Range']=3;act['StopAtHit']=True;act['StopAtWall']=True;act['HitTiles']=False;act['TargetAlignments']=4;act['AppearanceMod']=0;act['Anim']['AnimIndex']=name;act['Anim']['FrameTime']=2
act['Emitter']={'$type':'RogueEssence.Content.EmptyAttachEmitter, RogueEssence'}
act['PreActions'][0]['Emitter']['Anim']['Anim']['AnimIndex']=name
act['PreActions'][0]['Emitter']['Anim']['Anim']['FrameTime']=4
act['PreActions'][0]['Emitter']['Anim']['TotalTime']=0
hit=copy.deepcopy(read('volt_tackle')['Object']['Data']['HitFX']);a['HitboxAction']=act;a['Data']['HitFX']=hit
text=json.dumps(z,indent=2,ensure_ascii=False);(P/'catastropika-test-only.json').write_text(text);(G/'Data/Skill/catastropika.json').write_text(text)
print('Pikachu visible, DashAction depuis volt_tackle, aura IA et impact électrique natif')
