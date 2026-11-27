#!/usr/bin/env python3
# Prépare Chaos Draconique en zone orientée dans la copie de test, jamais dans le jeu réel.
from pathlib import Path
from PIL import Image
import io,struct,json,copy,shutil
import numpy as np
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny';P=R/'Prototypes/Chaos-Draconique/Generation-PMDO';name='Chaos_Draconique_IA_Impact';frames=[]
for i in range(1,7):
 im=Image.open(P/f'image-{i:02}.png').convert('RGB').resize((64,64),Image.Resampling.NEAREST);a=np.array(im);a16=a.astype('int16');m=(a16[:,:,1]>120)&(a16[:,:,1]>a16[:,:,0]+45)&(a16[:,:,1]>a16[:,:,2]+45)
 rgba=np.dstack((a,np.where(m,0,255).astype('uint8')));f=Image.fromarray(rgba,'RGBA');f.save(P/f'pose-{i:02}-transparent-64.png');frames.append(f)
sheet=Image.new('RGBA',(64*len(frames),64*8))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*64,row*64))
sheet.save(P/(name+'.Dir8.png'));b=io.BytesIO();sheet.save(b,format='PNG');png=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',64,64,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'devastating_drake-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('devastating_drake');p.write_text(json.dumps(orig,indent=2,ensure_ascii=False))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=2
for x in a['Data']['SkillStates']:
 if x.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):x['Power']=100
# AreaAction Cone hérité de Clanging Scales, rayon 2 pour cette expérience.
act=copy.deepcopy(read('clanging_scales')['Object']['HitboxAction']);act['Range']=2;act['Speed']=10;act['HitTiles']=False;act['TargetAlignments']=4;act['ActionFX']['Sound']='DUN_Dragon_Pulse';act['Emitter']['Anims'][0]['Anim']['AnimIndex']='Dragon_Pulse_Ball'
hit=copy.deepcopy(read('fire_blast')['Object']['Data']['HitFX']);hit['Emitter']['Anim']['Anim']['AnimIndex']=name;hit['Emitter']['Anim']['Anim']['FrameTime']=4;hit['Emitter']['LocHeight']=8;hit['Sound']='DUN_Dragon_Rush'
a['HitboxAction']=act;a['Data']['HitFX']=hit
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'devastating_drake-test-only.json').write_text(s);(G/'Data/Skill/devastating_drake.json').write_text(s)
print('Chaos Draconique : six poses IA, rayon carré 2, zone Cone, son natif.')
