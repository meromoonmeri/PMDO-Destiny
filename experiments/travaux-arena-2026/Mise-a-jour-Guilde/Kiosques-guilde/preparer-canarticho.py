from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent
im=Image.open(p/'canarticho-kiosque-v2-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>155)&(b>130)&(g<110)&(r-g>80)&(b-g>70),3]=0
im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((112,104),Image.Resampling.LANCZOS);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>135)&(b>100)&(r-g>65)&(b-g>50);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);im.save(p/'canarticho-kiosque-v2-sprite.png');im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(p/'canarticho-kiosque-v2-zoom.png');print(im.size,'centre alpha',im.getpixel((im.width//2,im.height//2)))
