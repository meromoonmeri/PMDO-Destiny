from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
im=Image.open(p/'tapis-circulaire-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>145)&(b>120)&(g<110)&(r-g>80)&(b-g>70),3]=0
im=Image.fromarray(a);im=im.crop(im.getbbox()).resize((144,80),Image.Resampling.NEAREST);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>110)&(b>75)&(r-g>40)&(b-g>30);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);im.save(p/'Tapis-des-missions-sprite.png');im.resize((576,320),Image.Resampling.NEAREST).save(p/'Tapis-des-missions-zoom.png')
print('sprite',im.size)
