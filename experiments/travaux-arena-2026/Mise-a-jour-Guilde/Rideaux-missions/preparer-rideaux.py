from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent
im=Image.open(p/'rideau-fenetre-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>150)&(b>120)&(g<110)&(r-g>80)&(b-g>70),3]=0
im=Image.fromarray(a);im=im.crop(im.getbbox()).resize((64,106),Image.Resampling.NEAREST);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>110)&(b>75)&(r-g>40)&(b-g>30);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a)
for nom,obj in [('gauche',im),('droite',im.transpose(Image.Transpose.FLIP_LEFT_RIGHT))]:
 obj.save(p/f'rideau-{nom}-sprite.png');obj.resize((256,424),Image.Resampling.NEAREST).save(p/f'rideau-{nom}-zoom.png')
base=Image.open(p/'salle-base.png').convert('RGBA');base.alpha_composite(im,(70,57));base.alpha_composite(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(442,57));base.save(p/'essai-sur-fenetres.png')
