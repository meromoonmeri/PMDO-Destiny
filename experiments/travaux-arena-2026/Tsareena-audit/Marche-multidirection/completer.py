from PIL import Image,ImageDraw,ImageOps
from pathlib import Path
import numpy as np
p=Path(__file__).parent;r=p.parent;ref=r/'refs-spritecollab'; sheet=Image.open(p/'Walk-Anim-PARTIEL.png').convert('RGBA');source=Image.open(ref/'Walk-Anim.png').convert('RGBA')

def detach(path,flip=False):
 a=np.array(Image.open(path).convert('RGB'));v=a.astype(int);bg=v[0,0];dist=np.sqrt(((v-bg)**2).sum(axis=2));m=(dist>38)|(v[:,:,2]<150);im=Image.fromarray(np.dstack([a,m.astype('uint8')*255]),'RGBA');im=im.crop(im.getbbox());return ImageOps.mirror(im) if flip else im
spec={0:('face-v2-original.png',False),2:('profil-droite-v2-original.png',False),3:('arriere-gauche-v2-original.png',True),4:('dos-01-original.png',False),5:('arriere-gauche-v2-original.png',False),6:('profil-droite-v2-original.png',True)}
for row,(name,flip) in spec.items():
 im=detach(p/name,flip); boxes=[source.crop((i*32,row*56,(i+1)*32,(row+1)*56)).getbbox() for i in range(4)];width=min(26,max(q[2]-q[0] for q in boxes));height=max(q[3]-q[1] for q in boxes);x=max(0,min(32-width,round((boxes[0][0]+boxes[0][2]-width)/2)));y=boxes[0][3]-height;f=min(width/im.width,height/im.height);nw=round(im.width*f);nh=round(im.height*f);tile=Image.new('RGBA',(32,56));tile.alpha_composite(im.resize((nw,nh),Image.Resampling.NEAREST),(x+(width-nw)//2,y+height-nh));sheet.alpha_composite(tile,(0,row*56))
 # Temporal placeholders: only frame 1 has been drawn; do not falsely present repeated frames as a finished walk.
 # Frame 3 matches frame 1 as in the original cycle. Frames 2 and 4 remain transparent pending drawings.
 sheet.alpha_composite(tile,(2*32,row*56))
sheet.save(p/'Walk-Anim-8-directions-EN-COURS.png')
# enlarged contact sheet, line captions
out=Image.new('RGB',(4*32*5,8*56*5),(202,219,190))
for row in range(8):
 for f in range(4):
  tile=sheet.crop((f*32,row*56,(f+1)*32,(row+1)*56)).resize((160,280),Image.Resampling.NEAREST);out.paste(tile,(f*160,row*280),tile)
out.save(p/'controle-8-directions.png'); print('32 cases, 8 directions; 6 nouvelles vues, colonnes 2 et 4 manquantes')
