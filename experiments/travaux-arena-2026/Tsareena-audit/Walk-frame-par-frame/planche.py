from PIL import Image
import numpy as np
from pathlib import Path
p=Path(__file__).parent;r=p.parent;normal=Image.open(r/'refs-spritecollab/Walk-Anim.png').convert('RGBA');dest=Image.new('RGBA',(256,896))
for row,name,base in [(1,'droite',r/'revision-corpulence/repos-trois-quart-01.png'),(7,'gauche',r/'Huit-directions/avant-gauche.png')]:
 im=Image.open(p/f'avant-{name}-02-retouche.png').convert('RGB'); a=np.array(im); v=a.astype(int);bg=v[0,0];m=(np.sqrt(((v-bg)**2).sum(axis=2))>38)|(v[:,:,2]<150);q=Image.fromarray(np.dstack([a,m.astype('uint8')*255]),'RGBA');box=q.getbbox();im=q.crop(box);boxes=[normal.crop((i*32,row*56,(i+1)*32,(row+1)*56)).getbbox() for i in range(4)];width=2*min(26,max(b[2]-b[0] for b in boxes));height=2*max(b[3]-b[1] for b in boxes);x=2*max(0,min(32-width//2,round((boxes[0][0]+boxes[0][2]-width//2)/2)));y=2*(boxes[0][3]-height//2);f=min(width/im.width,height/im.height);nw=round(im.width*f);nh=round(im.height*f);dest.alpha_composite(im.resize((nw,nh),Image.Resampling.NEAREST),(64+x+(width-nw)//2,row*112+y+height-nh))
dest.save(p/'Walk-frames-generees-PARTIEL.png');assert sum(bool(dest.crop((c*64,row*112,(c+1)*64,(row+1)*112)).getbbox()) for row in range(8) for c in range(4))==2
print('64×112, deux cases disponibles, 30 cases vides')
