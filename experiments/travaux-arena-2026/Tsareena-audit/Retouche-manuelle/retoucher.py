from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).parent
im=Image.open(p/'profil-droite-brut.png').convert('RGB');a=np.array(im).astype('int16');h,w=a.shape[:2]; y,x=np.indices((h,w));r,g,b=[a[:,:,i] for i in range(3)]
# Le générateur avait ajouté un col rouge : recolorer cette zone en prune, sans toucher aux contours noirs ni à l'œil.
collar=(x>=390)&(x<=660)&(y>=350)&(y<=522)&(r>75)&(r>g*1.35)&(r>b*1.25)&(g<105)&(b<120)
a[collar]=np.stack([np.clip(r[collar]*.50,36,95),np.clip(g[collar]*.65,20,58),np.clip(b[collar]*.90,31,90)],axis=-1).astype('int16')
# Teinte de la robe : violet vif inventé remplacé par la palette prune du modèle approuvé.
r,g,b=[a[:,:,i] for i in range(3)];robe=(x>=135)&(x<=520)&(y>=580)&(y<=1050)&(r>75)&(b>75)&(b>g*1.35)&(abs(r-b)<40)
a[robe]=np.stack([np.clip(r[robe]*.84,0,255),np.clip(g[robe]*.89,0,255),np.clip(b[robe]*.68,0,255)],axis=-1).astype('int16')
Image.fromarray(a.clip(0,255).astype('uint8')).save(p/'profil-droite-retouche.png')
print('pixels retouchés : col',collar.sum(),'robe',robe.sum())
