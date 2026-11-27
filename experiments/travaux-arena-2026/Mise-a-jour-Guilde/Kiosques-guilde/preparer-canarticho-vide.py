from pathlib import Path
from PIL import Image
import numpy as np
p=Path(__file__).resolve().parent
im=Image.open(p/'canarticho-comptoir-vide-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>155)&(b>130)&(g<110)&(r-g>80)&(b-g>70),3]=0
im=Image.fromarray(a); im=im.crop(im.getbbox()); print('crop size',im.size)
for algo in ('nearest','lanczos'):
 pic=im.resize((110,104),Image.Resampling.NEAREST if algo=='nearest' else Image.Resampling.LANCZOS);a=np.array(pic);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>110)&(b>75)&(r-g>40)&(b-g>30);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;pic=Image.fromarray(a)
 pic.save(p/f'canarticho-vide-{algo}-sprite.png');pic.resize((pic.width*4,pic.height*4),Image.Resampling.NEAREST).save(p/f'canarticho-vide-{algo}-zoom.png');print(algo,pic.size)
