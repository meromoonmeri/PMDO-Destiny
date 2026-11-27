#!/usr/bin/env python3
"""Explosion rouge et noire issue de la banque animée native de Destruction."""
from pathlib import Path
from PIL import Image
import io,struct,json
import numpy as np
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Dark-Body-Press/Generation-PMDO'
def unpack(p):
 b=p.read_bytes();n=struct.unpack_from('<q',b)[0];s=Image.open(io.BytesIO(b[8:8+n])).convert('RGBA');w,h,_,cnt=struct.unpack_from('<iiii',b,8+n);return [s.crop((i*w,0,(i+1)*w,h)) for i in range(cnt)]
old=unpack(P/'DarkBodyV2_Impact.dir');native=unpack(G/'Content/Particle/Explosion.dir');frames=[];N=176
# Début du choc, suivi de la séquence originale d'explosion à 3 temps par image.
for t in range(56):
 f=Image.new('RGBA',(N,N))
 if t<11:
  v=old[min(len(old)-1,t)].resize((96,96),Image.Resampling.NEAREST);f.alpha_composite(v,((N-96)//2,(N-96)//2))
 if t>=8:
  j=min(len(native)-1,(t-8)//3);v=native[j].resize((176,176),Image.Resampling.NEAREST);a=np.array(v); lum=(a[:,:,0].astype(float)*.30+a[:,:,1].astype(float)*.59+a[:,:,2].astype(float)*.11);alpha=a[:,:,3];
  # Palette faible et lisible : bords presque noirs, feu rouge profond, coeur rouge vif.
  out=np.zeros_like(a);out[:,:,0]=np.where(lum<52,22,np.where(lum<110,80,np.where(lum<180,160,np.where(lum<235,220,255))));out[:,:,1]=np.where(lum<110,4,np.where(lum<180,8,np.where(lum<235,24,84)));out[:,:,2]=np.where(lum<110,12,np.where(lum<180,18,np.where(lum<235,27,65)));out[:,:,3]=alpha;f.alpha_composite(Image.fromarray(out,'RGBA'))
 frames.append(f)
s=Image.new('RGBA',(N*len(frames),N*8))
for row in range(8):
 for i,f in enumerate(frames):s.alpha_composite(f,(N*i,N*row))
b=io.BytesIO();s.save(b,format='PNG');png=b.getvalue();(P/'DarkBodyV3_Impact.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',N,N,4,len(frames)))
z=json.loads((P/'malicious_moonsault-v2-test-only.json').read_text());fx=z['Object']['Data']['HitFX'];fx['Emitter']['Anim']['Anim']['AnimIndex']='DarkBodyV3_Impact';fx['Delay']=56;fx['Sound']='DUN_Self-Destruct';fx['ScreenMovement']={'MinShake':0,'MaxShake':3,'MaxShakeTime':20};(P/'malicious_moonsault-v3-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('Explosion de Destruction recolorée : 56 images, impact visuel uniquement.')
