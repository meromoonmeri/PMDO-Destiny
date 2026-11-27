#!/usr/bin/env python3
"""Rafale de poings pour le banc isolé ; ressources sources IA, poses intermédiaires composées."""
from pathlib import Path
from PIL import Image
import numpy as np,io,struct,shutil,copy,json
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Combo-Hyper-Furie/Generation-PMDO';N=80

def cut(name,size):
 im=Image.open(P/name).convert('RGB');im.thumbnail((size,size),Image.Resampling.NEAREST);a=np.array(im);b=a.astype('int16');mask=(b[:,:,1]>130)&(b[:,:,1]>b[:,:,0]+45)&(b[:,:,1]>b[:,:,2]+45);out=Image.fromarray(np.dstack((a,np.where(mask,0,255).astype('uint8'))),'RGBA');return out.crop(out.getbbox())
fist=cut('poing-rapide.png',48);spark=cut('impact-combat.png',48)
# Quatre coups distincts + un coup final : chaque phase entre, frappe et se retire.
frames=[]
for blow in range(4):
 y=(-10,8,-6,7)[blow]
 for stage in range(5):
  f=Image.new('RGBA',(N,N));size=(26,34,40,39,32)[stage];part=fist.resize((size,round(size*fist.height/fist.width)),Image.Resampling.NEAREST)
  x=(1,8,17,21,26)[stage];f.alpha_composite(part,(x,40+y-part.height//2))
  if stage in (2,3):
   p=spark.resize((28,28),Image.Resampling.NEAREST);p.putalpha(p.getchannel('A').point(lambda q:q*(200 if stage==2 else 140)//255));f.alpha_composite(p,(32,26+y))
  frames.append(f)
for i in range(6):
 f=Image.new('RGBA',(N,N));sz=(26,40,58,62,48,26)[i];p=spark.resize((sz,sz),Image.Resampling.NEAREST);p.putalpha(p.getchannel('A').point(lambda q:q*max(0,255-max(0,i-2)*65)//255));f.alpha_composite(p,((N-sz)//2,(N-sz)//2));frames.append(f)
# Ordre PMDO : bas, bas-gauche, gauche, haut-gauche, haut, haut-droite, droite, bas-droite.
# Le poing source vise à droite ; rotations géométriques, pas huit dessins IA indépendants.
angles=[-90,-135,180,135,90,45,0,-45];sheet=Image.new('RGBA',(N*len(frames),N*8));preview=Image.new('RGBA',(N*5,N*8),(31,28,31,255))
for row,angle in enumerate(angles):
 for i,f in enumerate(frames):
  rot=f.rotate(angle,resample=Image.Resampling.NEAREST,expand=False);sheet.alpha_composite(rot,(i*N,row*N))
  if i in (1,7,12,18,22):preview.alpha_composite(rot,((1,7,12,18,22).index(i)*N,row*N))
preview.convert('RGB').save(P/'controle-8-directions.png');name='Combo_HyperFurie_Dir8';sheet.save(P/(name+'.png'));buff=io.BytesIO();sheet.save(buff,format='PNG');png=buff.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)));shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
def read(n):return json.loads((G/'Data/Skill'/f'{n}.json').read_text(encoding='utf-8-sig'))
p=P/'all_out_pummeling-original.json'
if p.exists():orig=json.loads(p.read_text())
else:orig=read('all_out_pummeling');p.write_text(json.dumps(orig,ensure_ascii=False,indent=2))
z=copy.deepcopy(orig);a=z['Object'];a['Released']=True;a['BaseCharges']=1;a['Data']['Category']=1
for st in a['Data']['SkillStates']:
 if st.get('$type','').startswith('RogueEssence.Dungeon.BasePowerState'):st['Power']=75
# Combat rapproché : frappe une case devant, aucune case latérale.
act=copy.deepcopy(read('close_combat')['Object']['HitboxAction']);act['WideAngle']=0;act['HitTiles']=False;act['TargetAlignments']=4;act['LagBehindTime']=42
act['Emitter']['Anim']['Anim']['AnimIndex']=name;act['Emitter']['Anim']['Anim']['FrameTime']=2;act['Emitter']['Anim']['TotalTime']=0;act['ActionFX']['Sound']='DUN_Close_Combat'
a['HitboxAction']=act
s=json.dumps(z,ensure_ascii=False,indent=2);(P/'all_out_pummeling-test-only.json').write_text(s);(G/'Data/Skill/all_out_pummeling.json').write_text(s)
print('Combo Hyper-Furie :',len(frames),'poses recomposées × 8 orientations, contact adjacent')
