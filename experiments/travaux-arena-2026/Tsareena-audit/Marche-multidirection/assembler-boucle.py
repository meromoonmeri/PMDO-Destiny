from pathlib import Path
from PIL import Image,ImageOps
import numpy as np
p=Path(__file__).parent;r=p.parent;source=Image.open(r/'refs-spritecollab/Walk-Anim.png').convert('RGBA');sheet=Image.open(p/'Walk-Anim-PARTIEL.png').convert('RGBA')
base={'face':'face-v2-original.png','profil':'profil-droite-v2-original.png','arriere':'arriere-gauche-v2-original.png','dos':'dos-01-original.png'}
seq={0:('face',False,['face-02-retouche.png','face-04-retouche.png']),2:('profil',False,['profil-droite-02-retouche.png','profil-droite-04-retouche.png']),3:('arriere',True,['arriere-gauche-02-retouche.png','arriere-gauche-04-retouche.png']),4:('dos',False,['dos-02-retouche.png','dos-04-retouche.png']),5:('arriere',False,['arriere-gauche-02-retouche.png','arriere-gauche-04-retouche.png']),6:('profil',True,['profil-droite-02-retouche.png','profil-droite-04-retouche.png'])}
def transparent(path,flip):
 a=np.array(Image.open(path).convert('RGB'));v=a.astype(int);bg=v[0,0];d=np.sqrt(((v-bg)**2).sum(axis=2));m=(d>38)|(v[:,:,2]<150);im=Image.fromarray(np.dstack([a,m.astype('uint8')*255]),'RGBA');return ImageOps.mirror(im) if flip else im
for row,(name,flip,alternates) in seq.items():
 paths=[base[name],alternates[0],base[name],alternates[1]];ims=[transparent(p/q,flip) for q in paths];assert len({x.size for x in ims})==1
 boxes=[im.getbbox() for im in ims];box=(min(q[0] for q in boxes),min(q[1] for q in boxes),max(q[2] for q in boxes),max(q[3] for q in boxes));sw=box[2]-box[0];sh=box[3]-box[1]
 sboxes=[source.crop((i*32,row*56,(i+1)*32,(row+1)*56)).getbbox() for i in range(4)]; width=min(26,max(q[2]-q[0] for q in sboxes));height=max(q[3]-q[1] for q in sboxes);x=max(0,min(32-width,round((sboxes[0][0]+sboxes[0][2]-width)/2)));y=sboxes[0][3]-height;factor=min(width/sw,height/sh);nw=round(sw*factor);nh=round(sh*factor)
 for i,im in enumerate(ims):
  tile=im.crop(box).resize((nw,nh),Image.Resampling.NEAREST);sheet.alpha_composite(tile,(i*32+x+(width-nw)//2,row*56+y+height-nh))
 assert all(sheet.crop((i*32,row*56,(i+1)*32,(row+1)*56)).getbbox() for i in range(4))
sheet.save(p/'Walk-Anim-8-directions-BROUILLON.png')
control=Image.new('RGB',(640,2240),(202,219,190))
for row in range(8):
 for f in range(4):
  tile=sheet.crop((f*32,row*56,(f+1)*32,(row+1)*56)).resize((160,280),Image.Resampling.NEAREST);control.paste(tile,(f*160,row*280),tile)
control.save(p/'controle-boucle-8-directions.png')
for row in range(8):
 tiles=[np.array(sheet.crop((i*32,row*56,(i+1)*32,(row+1)*56))) for i in range(4)]
 print('direction',row,'cases',len(tiles),'changements pixels',*[np.count_nonzero(np.any(tiles[i]!=tiles[0],axis=2)) for i in (1,2,3)])
