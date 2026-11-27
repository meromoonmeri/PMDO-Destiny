from pathlib import Path
from PIL import Image
import math,json
p=Path(__file__).resolve().parent
original=Image.open(p/'rideau-gauche-sprite.png').convert('RGBA')
# Mur oblique : les verticales restent verticales ; y descend de 1 px pour 2 px en x.
face=original.resize((64,76),Image.Resampling.NEAREST)
left=Image.new('RGBA',(64,108))
for x in range(64):
 dy=round((63-x)*.5)
 left.paste(face.crop((x,0,x+1,76)),(x,dy))
right=left.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
for side,im in [('gauche',left),('droite',right)]:
 im.save(p/f'rideau-{side}-perspective-sprite.png')
 im.resize((256,432),Image.Resampling.NEAREST).save(p/f'rideau-{side}-perspective-zoom.png')
base=Image.open(p/'salle-base.png').convert('RGBA');base.alpha_composite(left,(70,57));base.alpha_composite(right,(442,57));base.save(p/'perspective-sur-fenetres.png')
print('pente: ±0,5 px/px ; angle dans le plan du dessin ≈ ±',round(math.degrees(math.atan(.5)),1),'°')
