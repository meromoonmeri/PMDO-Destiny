#!/usr/bin/env python3
"""Crée une animation IA complémentaire, sans écraser les textures Normal PMDO."""
from pathlib import Path
from PIL import Image
import numpy as np
import io, struct, json
H=Path.home();P=H/'Capacites-Z/Prototypes/Gare-au-Ronflex/Generation-PMDO';G=H/'.cache/destiny-test/game/PMDO-Destiny'
a=np.asarray(Image.open(P/'source-ia-impact-normal.png').convert('RGB')).astype('float32')
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];score=np.maximum(r,b)
alpha=np.clip((1-np.maximum(g-score,0)/255-.14)/.86,0,1);safe=np.maximum(alpha,1/255)
a[:,:,1]=np.minimum(np.clip((g-255*(1-alpha))/safe,0,255),score+18)
im=Image.fromarray(np.dstack([np.uint8(np.clip(a,0,255)),np.uint8(alpha*255)]),'RGBA');im=im.crop(im.getbbox());im.thumbnail((100,75),Image.Resampling.LANCZOS);im.save(P/'impact-normal-ia-detoure.png')
N=128;frames=[]
for t in range(24):
 frame=Image.new('RGBA',(N,N));p=min(1,(t+1)/6);w=max(1,round(im.width*(.35+.65*p)));h=max(1,round(im.height*(.35+.65*p)));s=im.resize((w,h),Image.Resampling.LANCZOS)
 opacity=min(1,(t+1)/3)*min(1,(24-t)/12)*.72;s.putalpha(s.getchannel('A').point(lambda x:round(x*opacity)))
 frame.alpha_composite(s,((N-w)//2,(N-h)//2));frames.append(frame)
sheet=Image.new('RGBA',(N*len(frames),N*8));preview=Image.new('RGBA',(N*6,N),(34,36,42,255))
for row in range(8):
 for i,f in enumerate(frames):sheet.alpha_composite(f,(i*N,row*N))
for col,i in enumerate([0,3,6,10,15,21]):preview.alpha_composite(frames[i],(col*N,0))
preview.convert('RGB').save(P/'progression-impact-normal.png')
b=io.BytesIO();sheet.save(b,format='PNG');raw=b.getvalue();(P/'Ronflex_Impact_Normal_IA.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,len(frames)))
fiche=json.loads((P/'pulverizing_pancake-brouillon-test-only.json').read_text())
giga=json.loads((G/'Data/Skill/giga_impact.json').read_text(encoding='utf-8-sig'))['Object']; string=json.loads((G/'Data/Skill/string_shot.json').read_text(encoding='utf-8-sig'))['Object']
# Giga Impact natif autour du point d'impact, sans reprendre sa zone de dégâts.
fiche['Object']['Explosion']['ExplodeFX']=giga['Explosion']['ExplodeFX']
hit=string['Data']['HitFX'];hit['Emitter']['Anim']['Anim']['AnimIndex']='Ronflex_Impact_Normal_IA';hit['Emitter']['Anim']['Anim']['FrameTime']=2;hit['Sound']='EVT_Tackle';hit['Delay']=25;hit['AbsoluteDelay']=True
fiche['Object']['Data']['HitFX']=hit
(P/'pulverizing_pancake-v1-test-only.json').write_text(json.dumps(fiche,ensure_ascii=False,indent=2),encoding='utf-8')
print('Effet IA animé et textures Giga Impact natives assemblés ; jeu intact.')
