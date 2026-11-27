from pathlib import Path
from PIL import Image,ImageOps
import numpy as np
p=Path(__file__).parent;r=p.parent;src=r/'Marche-multidirection';mb=r/'Marche-bras';prev=r/'Reprise-levitation';source=Image.open(r/'refs-spritecollab/Walk-Anim.png').convert('RGBA')
baseR=r/'revision-corpulence/repos-trois-quart-01.png';baseL=r/'Huit-directions/avant-gauche.png'
def frames(base,two,four):return [base,two,base,four]
base={'face':src/'face-v2-original.png','profil':src/'profil-droite-v2-original.png','arriere':src/'arriere-gauche-v2-original.png','dos':src/'dos-01-original.png'}
views={0:(frames(base['face'],src/'face-02-retouche.png',src/'face-04-retouche.png'),False),1:(frames(baseR,prev/'essai-manuel-jambe-1.png',prev/'essai-manuel-jambe-2.png'),False),2:(frames(base['profil'],src/'profil-droite-02-retouche.png',src/'profil-droite-04-retouche.png'),False),3:(frames(base['arriere'],src/'arriere-gauche-02-retouche.png',src/'arriere-gauche-04-retouche.png'),True),4:(frames(base['dos'],src/'dos-02-retouche.png',src/'dos-04-retouche.png'),False),5:(frames(base['arriere'],src/'arriere-gauche-02-retouche.png',src/'arriere-gauche-04-retouche.png'),False),6:(frames(base['profil'],src/'profil-droite-02-retouche.png',src/'profil-droite-04-retouche.png'),True),7:(frames(baseL,mb/'pas-gauche-02-retouche.png',mb/'pas-gauche-04-retouche.png'),False)}
def detach(file,flip):
 a=np.array(Image.open(file).convert('RGB'));v=a.astype(int);bg=v[0,0];d=np.sqrt(((v-bg)**2).sum(axis=2));alpha=((d>38)|(v[:,:,2]<150)).astype('uint8')*255;im=Image.fromarray(np.dstack([a,alpha]),'RGBA');return ImageOps.mirror(im) if flip else im
sheet=Image.new('RGBA',(4*64,8*112)); metadata={}
for row,(paths,flip) in views.items():
 ims=[detach(f,flip) for f in paths];assert len({i.size for i in ims})==1
 boxes=[i.getbbox() for i in ims];box=(min(v[0] for v in boxes),min(v[1] for v in boxes),max(v[2] for v in boxes),max(v[3] for v in boxes)); sw=box[2]-box[0];sh=box[3]-box[1]
 refboxes=[source.crop((32*i,56*row,32*(i+1),56*(row+1))).getbbox() for i in range(4)];width=2*min(26,max(x[2]-x[0] for x in refboxes));height=2*max(x[3]-x[1] for x in refboxes);x=2*max(0,min(32-width//2,round((refboxes[0][0]+refboxes[0][2]-width//2)/2)));y=2*(refboxes[0][3]-height//2);f=min(width/sw,height/sh);nw=round(sw*f);nh=round(sh*f);dx=x+(width-nw)//2;dy=y+height-nh
 for k,im in enumerate(ims):sheet.alpha_composite(im.crop(box).resize((nw,nh),Image.Resampling.NEAREST),(k*64+dx,row*112+dy))
 metadata[row]=(nw,nh,dx,dy,box)
sheet.save(p/'Walk-Anim-BROUILLON-64x112.png')
# Comparison of nearest-neighbor baseline and new sheet; same final zoom, before/after.
old=Image.open(src/'Walk-Anim-8-directions-BROUILLON.png');control=Image.new('RGB',(512,3*448),(202,219,190))
for i,row in enumerate([1,7,4]):
 a=old.crop((0,row*56,32,(row+1)*56)).resize((256,448),Image.Resampling.NEAREST);b=sheet.crop((0,row*112,64,(row+1)*112)).resize((256,448),Image.Resampling.NEAREST);control.paste(a,(0,i*448),a);control.paste(b,(256,i*448),b)
control.save(p/'comparaison-avant-apres.png')
for i in range(8):
 assert all(sheet.crop((64*j,112*i,64*(j+1),112*(i+1))).getbbox() for j in range(4))
 print(i, metadata[i])
