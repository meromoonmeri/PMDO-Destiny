from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).parent;r=p.parent
approved=[(1,r/'revision-corpulence/repos-trois-quart-01.png'),(7,r/'Huit-directions/avant-gauche.png')]
out=Image.new('RGBA',(256,896))
for row,path in approved:
 im=Image.open(path).convert('RGB');a=np.asarray(im);v=a.astype(int);bg=v[0,0];dist=np.sqrt(((v-bg)**2).sum(2));alpha=((dist>38)|(v[:,:,2]<150)).astype('uint8')*255
 rgba=Image.fromarray(np.dstack((a,alpha)),'RGBA');box=rgba.getbbox();assert box
 sprite=rgba.crop(box);scale=min(54/sprite.width,64/sprite.height);sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.NEAREST);out.alpha_composite(sprite,((64-sprite.width)//2,row*112+70-sprite.height));print(row,path.name,box,sprite.size)
out.save(p/'Modele-verrouille-2-vues-PARTIEL.png')
