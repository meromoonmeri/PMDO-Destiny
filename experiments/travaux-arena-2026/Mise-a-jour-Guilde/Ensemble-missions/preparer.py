from pathlib import Path
from PIL import Image
import numpy as np
p=Path(__file__).resolve().parent
for name,maxsize in [('comptoir-cloche',(80,60)),('table-buche',(52,44)),('siege-buche',(18,18))]:
 im=Image.open(p/f'{name}-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>145)&(b>120)&(g<110)&(r-g>80)&(b-g>70),3]=0
 im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail(maxsize,Image.Resampling.NEAREST);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>110)&(b>75)&(r-g>40)&(b-g>30);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);im.save(p/f'{name}-sprite.png');im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(p/f'{name}-zoom.png');print(name,im.size)
