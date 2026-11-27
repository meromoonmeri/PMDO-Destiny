#!/usr/bin/env python3
# Montage des poses IA : détramage magenta puis planches radiales Dir8.
# Change uniquement la copie jetable dans ~/.cache/destiny-test.
from pathlib import Path
from PIL import Image
import numpy as np,io,struct,json,copy,shutil
R=Path('/home/user/Capacites-Z');G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'
sets=[('Pyro-Explosion-Cataclysmique','Pyro_IA_Impact',['image-01.png','image-02.png','image-02b.png','image-03.png','image-04.png']),('Super-Tourbillon-Abyssal','Tourbillon_IA_Impact',['image-01.png','image-02.png','image-03.png','image-04.png','image-05.png'])]
for folder,name,files in sets:
 p=R/'Prototypes'/folder/'Generation-PMDO'; frames=[]
 for f in files:
  im=Image.open(p/f).convert('RGB').resize((64,64),Image.Resampling.NEAREST)
  a=np.array(im);m=(a[:,:,0]>180)&(a[:,:,2]>130)&(a[:,:,1]<115)
  rgba=np.dstack((a,np.where(m,0,255).astype('uint8')));frame=Image.fromarray(rgba,'RGBA');frames.append(frame)
  frame.save(p/(f.replace('.png','-transparent-64.png')))
 sheet=Image.new('RGBA',(64*len(frames),64*8));
 for row in range(8):
  for i,frame in enumerate(frames):sheet.alpha_composite(frame,(64*i,64*row))
 sheet.save(p/(name+'.Dir8.png'));buf=io.BytesIO();sheet.save(buf,format='PNG');png=buf.getvalue(); (p/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',64,64,4,len(frames)))
 shutil.copy2(p/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
# Les JSON « test-only » V2 ont été produits sur la base des originaux conservés.
fire=R/'Prototypes/Pyro-Explosion-Cataclysmique/V2-PMDO/inferno_overdrive-test-only.json'; water=R/'Prototypes/Super-Tourbillon-Abyssal/V2-PMDO/hydro_vortex-test-only.json'
a=json.loads(fire.read_text());b=json.loads(water.read_text());
emitter=a['Object']['Data']['HitFX']['Emitter'];emitter['Anim']['Anim']['AnimIndex']='Pyro_IA_Impact';emitter['Anim']['Anim']['FrameTime']=5
a['Object']['Data']['HitFX']['Sound']='DUN_Fire_Blast_2'
b['Object']['Data']['HitFX']['Emitter']=copy.deepcopy(emitter);b['Object']['Data']['HitFX']['Emitter']['Anim']['Anim']['AnimIndex']='Tourbillon_IA_Impact';b['Object']['Data']['HitFX']['Sound']='DUN_Whirlpool'
for skill,folder,obj in [('inferno_overdrive',sets[0][0],a),('hydro_vortex',sets[1][0],b)]:
 s=json.dumps(obj,ensure_ascii=False,indent=2);(G/'Data/Skill'/f'{skill}.json').write_text(s);(R/'Prototypes'/folder/'Generation-PMDO'/f'{skill}-test-only.json').write_text(s)
print('Banques et fiches de test prêtes ; dessins radiaux identiques dans les huit lignes.')
