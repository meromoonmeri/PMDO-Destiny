from pathlib import Path
from PIL import Image
import numpy as np
from scipy.spatial.distance import cdist
from skimage.color import rgb2lab
p=Path(__file__).parent;src=p.parent/'Design-unifie/Reprise-vues-POLISH-ESSAI.png';a=np.array(Image.open(src).convert('RGBA'))
palette=np.array([(0,0,0),(40,20,29),(67,32,54),(111,58,91),(144,93,122),(129,46,70),(175,56,88),(199,99,118),(81,104,70),(113,145,87),(140,180,87),(179,225,115),(249,224,108),(254,254,254),(180,174,184)],dtype='uint8')
px=a[:,:,:3].reshape(-1,3);unique,inverse=np.unique(px,axis=0,return_inverse=True);labs=rgb2lab(unique.reshape(1,-1,3)).reshape(-1,3);plabs=rgb2lab(palette.reshape(1,-1,3)).reshape(-1,3);idx=cdist(labs,plabs).argmin(axis=1);out=a.copy();out[:,:,:3]=palette[idx[inverse]].reshape(a.shape[0],a.shape[1],3);out[a[:,:,3]==0,:3]=0
Image.fromarray(out).save(p/'Walk-palette15-ESSAI.png');print('couleurs visibles',len(np.unique(out[out[:,:,3]>0,:3],axis=0)),'transparence inchangée',np.array_equal(a[:,:,3],out[:,:,3]))
images=[Image.fromarray(a),Image.fromarray(out)];o=Image.new('RGB',(8*128,8*224),'#c7d9bf')
for row in range(8):
 for col in range(4):
  for z,im in enumerate(images):
   im=im.crop((col*64,row*112,(col+1)*64,(row+1)*112)).resize((128,224),Image.Resampling.NEAREST);o.paste(im,(col*256+z*128,row*224),im)
o.save(p/'controle-palette15.png')
