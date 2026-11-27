from pathlib import Path
from PIL import Image, ImageOps
from scipy.ndimage import binary_propagation
import numpy as np
p=Path(__file__).parent;out=p/'derivees';out.mkdir(exist_ok=True)
items={'face':'images/reprise-face.png','avant-droite':'images/reprise-avant-droite.png','droite':'images/reprise-profil-droite.png','arriere-droite':'references/arriere-droite.png','dos':'references/dos.png','arriere-gauche':'references/arriere-gauche.png','avant-gauche':'images/reprise-avant-gauche.png','sommeil':'images/sommeil-face-01.png','attaque':'images/attaque-face-02.png','blessure':'images/blessure-face-01.png'}
for name,path in items.items():
 im=Image.open(p/path).convert('RGB'); a=np.array(im).astype(np.int16); bgcol=np.median(a[:25,:25,:].reshape(-1,3),axis=0); dist=np.sqrt(((a-bgcol)**2).sum(axis=2));mask=dist<35
 seed=np.zeros(mask.shape,bool);seed[0,:]=mask[0,:];seed[-1,:]=mask[-1,:];seed[:,0]=mask[:,0];seed[:,-1]=mask[:,-1]
 bg=binary_propagation(seed,mask=mask,structure=np.ones((3,3)));rgba=np.dstack((a.astype('uint8'),np.where(bg,0,255).astype('uint8'))); pic=Image.fromarray(rgba,'RGBA'); box=(247,90,811,918) if name in ('sommeil','attaque','blessure') else pic.getbbox();pic=pic.crop(box);pic.thumbnail((150,160),Image.Resampling.NEAREST); canvas=Image.new('RGBA',(160,180));canvas.alpha_composite(pic,((160-pic.width)//2,170-pic.height));canvas.save(out/(name+'.png'));print(name,box,pic.size)
ImageOps.mirror(Image.open(out/'droite.png')).save(out/'gauche.png')
