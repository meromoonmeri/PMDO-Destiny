from PIL import Image
from pathlib import Path
import numpy as np
p=Path(__file__).parent;r=p.parent
files={0:p/'face-reprise-v2.png',1:r/'revision-corpulence/repos-trois-quart-01.png',2:p/'profil-droite-reprise-v2.png',3:p/'arriere-droite-reprise-v3.png',4:p/'reprise-dos-brut.png',5:p/'arriere-gauche-reprise-v5.png',6:p/'profil-gauche-reprise-v2.png',7:r/'Huit-directions/avant-gauche.png'}
def rgba(path,clean_edge=False):
 a=np.array(Image.open(path).convert('RGB'));v=a.astype(int);bg=v[15,0] if clean_edge else v[0,0];dist=np.sqrt(((v-bg)**2).sum(2));alpha=((dist>38)|(v[:,:,2]<150)).astype('uint8')*255
 if clean_edge:alpha[:20,:]=0
 return Image.fromarray(np.dstack((a,alpha)),'RGBA')
out=Image.new('RGBA',(256,896))
for row,path in files.items():
 if row==0: frames=[rgba(path),rgba(p/'face-marche-02-bras-pas-court.png'),rgba(path),rgba(p/'face-marche-04-retouche.png')]
 elif row in (2,3,5,6):
  d={2:'profil-droite',3:'arriere-droite',5:'arriere-gauche',6:'profil-gauche'}[row]
  q=r/'Marche-autres-vues'
  frames=[rgba(path),rgba(q/f'{d}-02-retouche.png'),rgba(path),rgba(q/f'{d}-04-retouche.png')]
 elif row in (1,7):
  d='droite' if row==1 else 'gauche'
  arm=r/'Marche-bras-v2'
  a02=(arm/'avant-gauche-02-retouche.png') if row==7 else (p/f'diag-{d}-02-retouche.png')
  a04=(arm/'avant-droite-04-retouche.png') if row==1 else (p/f'diag-{d}-04-retouche.png')
  frames=[rgba(path),rgba(a02),rgba(path),rgba(a04)]
 elif row==4: frames=[rgba(path,True),rgba(p/'walk-dos-02-retouche.png',True),rgba(path,True),rgba(p/'walk-dos-04-retouche.png',True)]
 else: frames=[rgba(path,row==4)]
 boxes=[im.getbbox() for im in frames];bbox=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes));w=bbox[2]-bbox[0];h=bbox[3]-bbox[1];scale=min(54/(boxes[0][2]-boxes[0][0]),64/(boxes[0][3]-boxes[0][1]));size=(round(w*scale),round(h*scale));base_height=round((boxes[0][3]-boxes[0][1])*scale)
 offsets={0:[(0,0),(0,2),(0,0),(0,2)],1:[(0,0),(2,2),(0,0),(0,4)],2:[(0,0),(2,2),(0,0),(-2,4)],3:[(0,0),(0,0),(0,0),(2,-2)],4:[(0,0),(0,2),(0,0),(0,2)],5:[(0,0),(0,-2),(0,0),(-2,-2)],6:[(0,0),(-2,0),(0,0),(2,4)],7:[(0,0),(-2,2),(0,0),(0,4)]}
 for col,im in enumerate(frames):
  sp=im.crop(bbox).resize(size,Image.Resampling.NEAREST);dx,dy=offsets.get(row,[(0,0)]*4)[col];out.alpha_composite(sp,(col*64+(64-sp.width)//2+dx,row*112+70-base_height+dy))
 print('direction',row,'frames',len(frames),'cadrage fixe',bbox,size)
out.save(p/'Reprise-vues-PARTIEL.png')
