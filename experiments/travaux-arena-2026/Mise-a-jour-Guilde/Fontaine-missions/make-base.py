from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
im=Image.open(p/'fontaine-generation.png').convert('RGBA');a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');a[(r>145)&(b>120)&(g<110)&(r-g>80)&(b-g>70),3]=0
im=Image.fromarray(a);im=im.crop(im.getbbox());im.thumbnail((112,80),Image.Resampling.NEAREST);a=np.array(im);r,g,b=a[:,:,:3].transpose(2,0,1).astype('int16');bad=(r>110)&(b>75)&(r-g>40)&(b-g>30);a[bad,3]=0;a[:,:,3]=np.where(a[:,:,3]>=140,255,0).astype('uint8');a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a);canvas=Image.new('RGBA',(112,80));canvas.alpha_composite(im,((112-im.width)//2,80-im.height));canvas.save(p/'fontaine-base.png');canvas.resize((672,480),Image.Resampling.NEAREST).save(p/'fontaine-base-zoom.png');print('object',im.size,'canvas',canvas.size)
