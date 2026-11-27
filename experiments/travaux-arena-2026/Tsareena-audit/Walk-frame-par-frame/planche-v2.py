from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).parent;r=p.parent;normal=Image.open(r/'refs-spritecollab/Walk-Anim.png').convert('RGBA');dest=Image.new('RGBA',(256,896))
items={0:{0:'face-01-original.png',1:'face-02-original.png'},1:{1:'avant-droite-02-retouche.png',3:'avant-droite-04-retouche.png'},4:{1:'dos-02-original.png',3:'dos-04-original.png'},7:{1:'avant-gauche-02-retouche.png'}}
def alpha(path):
 a=np.array(Image.open(path).convert('RGB'));v=a.astype(int);bg=v[0,0];d=np.sqrt(((v-bg)**2).sum(axis=2));return Image.fromarray(np.dstack([a,((d>38)|(v[:,:,2]<150)).astype('uint8')*255]),'RGBA')
for row,paths in items.items():
 ims={i:alpha(p/path) for i,path in paths.items()};assert len({im.size for im in ims.values()})==1
 boxes=[im.getbbox() for im in ims.values()];box=(min(x[0] for x in boxes),min(x[1] for x in boxes),max(x[2] for x in boxes),max(x[3] for x in boxes));sw=box[2]-box[0];sh=box[3]-box[1];refboxes=[normal.crop((i*32,row*56,(i+1)*32,(row+1)*56)).getbbox() for i in range(4)];width=2*min(26,max(q[2]-q[0] for q in refboxes));height=2*max(q[3]-q[1] for q in refboxes);x=2*max(0,min(32-width//2,round((refboxes[0][0]+refboxes[0][2]-width//2)/2)));y=2*(refboxes[0][3]-height//2);f=min(width/sw,height/sh);nw=round(sw*f);nh=round(sh*f)
 for col,im in ims.items():dest.alpha_composite(im.crop(box).resize((nw,nh),Image.Resampling.NEAREST),(col*64+x+(width-nw)//2,row*112+y+height-nh))
dest.save(p/'Walk-Anim-partiel-v2.png');assert sum(bool(dest.crop((c*64,i*112,(c+1)*64,(i+1)*112)).getbbox()) for i in range(8) for c in range(4))==7
print('7 cases générées sur 32, autres transparentes.')
