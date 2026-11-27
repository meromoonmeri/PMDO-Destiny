#!/usr/bin/env python3
# Prototype dans une copie isolée. Poses IA individuelles, puis deux couches.
from pathlib import Path
from PIL import Image
import io,struct,json,copy,shutil
import numpy as np
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Appel-des-Ombres-Eternelles/Generation-PMDO'
files=['image-06.png','image-02.png','image-03b.png','image-04b.png','image-03b.png','image-02.png','image-05b.png','image-06.png'];S=64
back=Image.new('RGBA',(S*len(files),S*8));front=Image.new('RGBA',(S*len(files),S*8))
for i,file in enumerate(files):
 im=Image.open(P/file).convert('RGB').resize((S,S),Image.Resampling.NEAREST);a=np.array(im);a16=a.astype('int16');m=(a16[:,:,1]>110)&(a16[:,:,1]>a16[:,:,0]+45)&(a16[:,:,1]>a16[:,:,2]+45)
 rgba=np.dstack((a,np.where(m,0,255).astype('uint8')));f=Image.fromarray(rgba,'RGBA');f.save(P/f'pose-{i+1:02}-transparent-64.png')
 b=f.copy();b.paste((0,0,0,0),(0,50,S,S));fr=f.copy();fr.paste((0,0,0,0),(0,0,S,50))
 for r in range(8):back.alpha_composite(b,(i*S,r*S));front.alpha_composite(fr,(i*S,r*S))
for side,sheet in [('Arriere',back),('Avant',front)]:
 name='Ombres_IA_'+side;sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',S,S,4,len(files)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'never_ending_nightmare-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('never_ending_nightmare');p.write_text(json.dumps(orig,indent=2,ensure_ascii=False))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for x in a['Data']['SkillStates']:
 if x.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):x['Power']=100
act=copy.deepcopy(read('twister')['Object']['HitboxAction']);act['Range']=2;act['HitArea']=0;act['HitTiles']=False;act['TargetAlignments']=4;act['Emitter']={'$type':'RogueEssence.Content.EmptyCircleSquareEmitter, RogueEssence','LocHeight':0};act['ActionFX']['Sound']='DUN_Night_Shade_3'
hit=copy.deepcopy(read('head_smash')['Object']['Data']['HitFX']);hit['Delay']=0;hit['Sound']='DUN_Night_Shade_2';hit['Emitter']['HeightBack']=4;hit['Emitter']['HeightFront']=4
for k,side in [('AnimBack','Arriere'),('AnimFront','Avant')]:hit['Emitter'][k]['Anim']['AnimIndex']='Ombres_IA_'+side;hit['Emitter'][k]['Anim']['FrameTime']=5
a['HitboxAction']=act;a['Data']['HitFX']=hit
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'never_ending_nightmare-test-only.json').write_text(s);(G/'Data/Skill/never_ending_nightmare.json').write_text(s)
print('8 poses IA, deux calques ; OffsetAction Tile à 2 cases.')
