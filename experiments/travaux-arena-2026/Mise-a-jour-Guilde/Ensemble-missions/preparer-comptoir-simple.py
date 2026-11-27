from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent
im=Image.open(p/'comptoir-simple-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>145)&(b>120)&(g<110)&(r-g>80)&(b-g>70),3]=0
im=Image.fromarray(a);im=im.crop(im.getbbox()).resize((54,28),Image.Resampling.NEAREST);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=((r>70)&(g<25)&(b>65)&(b>r*.75)&(r-g>45))|((r>110)&(b>75)&(r-g>40)&(b-g>30));a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);im.save(p/'comptoir-simple-halcyon-54x28.png');im.resize((648,336),Image.Resampling.NEAREST).save(p/'comptoir-simple-halcyon-zoom.png');print('dimensions',im.size)
