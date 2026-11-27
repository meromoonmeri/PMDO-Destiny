#!/usr/bin/env python3
# Vrille Maximum : expérience uniquement en copie jetable.
from pathlib import Path
from PIL import Image
import io,struct,json,copy,shutil
import numpy as np
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Vrille-Maximum/Generation-PMDO';name='Vrille_IA_Impact';frames=[]
for i in range(1,5):
 im=Image.open(P/f'image-{i:02}.png').convert('RGB').resize((64,64),Image.Resampling.NEAREST);a=np.array(im);m=(a[:,:,0]>180)&(a[:,:,2]>130)&(a[:,:,1]<115);f=Image.fromarray(np.dstack((a,np.where(m,0,255).astype('uint8'))),'RGBA');f.save(P/f'pose-{i:02}-transparent-64.png');frames.append(f)
sheet=Image.new('RGBA',(64*len(frames),64*8))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*64,row*64))
sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',64,64,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'corkscrew_crash-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('corkscrew_crash');p.write_text(json.dumps(orig,indent=2,ensure_ascii=False))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for x in a['Data']['SkillStates']:
 if x.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):x['Power']=100
act=copy.deepcopy(read('gyro_ball')['Object']['HitboxAction']);act['Range']=3;act['StopAtHit']=True;act['StopAtWall']=True;act['HitTiles']=False;act['TargetAlignments']=4
hit=copy.deepcopy(read('gyro_ball')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']=name;hit['Emitter']['Anim']['Anim']['FrameTime']=4;hit['Emitter']['LocHeight']=8;hit['Sound']='DUN_Iron_Head'
a['HitboxAction']=act;a['Data']['HitFX']=hit
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'corkscrew_crash-test-only.json').write_text(s);(G/'Data/Skill/corkscrew_crash.json').write_text(s)
print('Vrille : DashAction, effet Gyro_Ball natif, quatre poses IA en impact.')
