#!/usr/bin/env python3
# Fulguro : essais dans la copie jetable uniquement, pas d'installation dans Destiny.
from pathlib import Path
from PIL import Image
import numpy as np,io,struct,json,copy,shutil
R=Path('/home/user/Capacites-Z'); G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'; P=R/'Prototypes/Fulguro-Lance-Gigavolt/Generation-PMDO';P.mkdir(parents=True,exist_ok=True)
frames=[]
for i in range(1,7):
 im=Image.open(P/f'image-{i:02}.png').convert('RGB').resize((64,64),Image.Resampling.NEAREST);a=np.array(im);m=(a[:,:,0]>180)&(a[:,:,2]>130)&(a[:,:,1]<115)
 rgba=np.dstack((a,np.where(m,0,255).astype('uint8')));f=Image.fromarray(rgba,'RGBA');f.save(P/f'pose-{i:02}-transparent-64.png');frames.append(f)
sheet=Image.new('RGBA',(64*len(frames),64*8))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(64*i,64*row))
name='Fulguro_IA_Impact';sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',64,64,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(x):return json.loads((G/'Data/Skill'/f'{x}.json').read_text(encoding='utf-8-sig'))
backup=P/'gigavolt_havoc-original.json'
if backup.exists():z=json.loads(backup.read_text())
else:z=read('gigavolt_havoc');backup.write_text(json.dumps(z,ensure_ascii=False,indent=2))
z=copy.deepcopy(z);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for st in a['Data']['SkillStates']:
 if st.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):st['Power']=100
act=copy.deepcopy(read('thunderbolt')['Object']['HitboxAction']);act['Rays']=0;act['Range']=4;act['Speed']=10;act['StopAtHit']=True;act['StopAtWall']=True;act['TargetAlignments']=4;act['HitTiles']=False
hit=copy.deepcopy(read('fire_blast')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']=name;hit['Emitter']['Anim']['Anim']['FrameTime']=4;hit['Emitter']['LocHeight']=8;hit['Sound']='DUN_Discharge_2'
a['HitboxAction']=act;a['Data']['HitFX']=hit
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'gigavolt_havoc-test-only.json').write_text(s);(G/'Data/Skill/gigavolt_havoc.json').write_text(s)
print('Fulguro : six poses, huit lignes radiales identiques, son DUN_Discharge_2. Fiche temporaire préparée.')
