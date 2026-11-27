#!/usr/bin/env python3
# Essai uniquement dans la copie jetable Destiny/PMDO.
from pathlib import Path
from PIL import Image
import io,struct,json,copy,shutil
import numpy as np
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Petalexplosion-Eblouissante/Generation-PMDO';name='Petalexplosion_IA_Impact'
files=['image-01b.png','image-02.png','image-03.png','image-04.png','image-05.png'];frames=[]
for i,f in enumerate(files):
 im=Image.open(P/f).convert('RGB').resize((64,64),Image.Resampling.NEAREST);a=np.array(im);m=(a[:,:,0]>220)&(a[:,:,2]>210)&(a[:,:,1]<70);rgba=np.dstack((a,np.where(m,0,255).astype('uint8')));fr=Image.fromarray(rgba,'RGBA');fr.save(P/f'pose-{i+1:02}-transparent-64.png');frames.append(fr)
sheet=Image.new('RGBA',(len(frames)*64,64*8))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*64,row*64))
sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',64,64,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def load(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'bloom_doom-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=load('bloom_doom');p.write_text(json.dumps(orig,indent=2,ensure_ascii=False))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for x in a['Data']['SkillStates']:
 if x.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):x['Power']=100
# AreaAction Full, rayon carré de 2 cases : test de zone, inspiré de Petal Blizzard / Vent Mauvais.
act=copy.deepcopy(load('petal_blizzard')['Object']['HitboxAction']);act['Range']=2;act['Speed']=10;act['HitTiles']=False;act['TargetAlignments']=4
hit=copy.deepcopy(load('fire_blast')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']=name;hit['Emitter']['Anim']['Anim']['FrameTime']=4;hit['Emitter']['LocHeight']=8;hit['Sound']='DUN_Leaf_Storm_2'
a['HitboxAction']=act;a['Data']['HitFX']=hit
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'bloom_doom-test-only.json').write_text(s);(G/'Data/Skill/bloom_doom.json').write_text(s)
print('Pétalexplosion : AreaAction Full Range=2, cinq poses d’impact IA, fiche test.')
