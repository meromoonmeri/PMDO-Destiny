from pathlib import Path
from PIL import Image
import numpy as np, cv2, hashlib
p=Path(__file__).parent
sources={'droite':p.parent/'revision-corpulence/repos-trois-quart-01.png','gauche':p.parent/'Huit-directions/avant-gauche.png'}
for n,source in sources.items():
 a=np.array(Image.open(source).convert('RGB'));h,w=a.shape[:2]; yy,xx=np.indices((h,w),dtype='float32')
 # Déplace rigidement le haut de 1,2 % de la hauteur ; le bas reste fixe.
 # La bande de transition est déformée : il s'agit d'un brouillon, pas de pixel art terminé.
 pivot1,pivot2=.60*h,.72*h; dy=.012*h*np.clip((pivot2-yy)/(pivot2-pivot1),0,1)
 out=cv2.remap(a,xx,yy-dy,cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=tuple(int(q) for q in a[0,0]));Image.fromarray(out).save(p/f'idle-02-{n}-provisoire.png')
 y0=int(np.ceil(pivot2));assert np.array_equal(a[y0:],out[y0:]);print(n,'original',hashlib.sha256(source.read_bytes()).hexdigest(),'pixels changés sous',y0,':',np.any(a[y0:]!=out[y0:],axis=2).sum())
