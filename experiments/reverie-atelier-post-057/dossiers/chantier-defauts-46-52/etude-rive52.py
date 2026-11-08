from PIL import Image
import numpy as np
im=Image.open('reverie-057-phase0.png').convert('RGBA');a=np.array(im);out=a.copy();start,end=336,520
# translation de la rive existante en pixels entiers, retour progressif à la rive actuelle aux extrémités
# La courbe est volontairement irrégulière plutôt que périodique.
points=[(336,0),(346,1),(354,2),(362,3),(374,4),(384,3),(398,1),(405,0),(416,2),(425,3),(437,4),(451,2),(463,0),(472,1),(484,3),(496,4),(507,2),(514,1),(520,0)]
for y in range(start,end):
 d=int(round(np.interp(y,*zip(*points))))
 if d:out[y,1056:1078]=a[y,1056+d:1078+d]
Image.fromarray(out).crop((1028,320,1108,550)).resize((320,920),Image.Resampling.NEAREST).save('nouvelle-rive52-prototype.png')
