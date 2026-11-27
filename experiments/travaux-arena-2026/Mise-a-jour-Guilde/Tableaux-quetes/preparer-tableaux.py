from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent
for nom in ('secours','exploration'):
 im=Image.open(p/(nom+'-mural-generation.png')).convert('RGBA'); a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');mask=(r>155)&(b>130)&(g<100)&(r-g>90)&(b-g>75);a[mask,3]=0
 # retirer seulement le magenta ; conserver les détails et des originaux intacts
 im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((64,46),Image.Resampling.LANCZOS)
 # éliminer le liseré magenta de la génération / anti-crénelage
 a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>135)&(b>100)&(r-g>65)&(b-g>50);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);im.save(p/(nom+'-mural-sprite.png'))
 im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(p/(nom+'-mural-zoom.png'));print(nom,im.size)
