from PIL import Image
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
p=Path(__file__).resolve().parent;r=p.parent;ref=r/'refs-spritecollab';prev=r/'Reprise-levitation';idle=r/'Repos-reprise';sleep=r/'Sommeil-reprise'

def detach(path):
 im=Image.open(path).convert('RGB'); a=np.array(im); bg=a[0,0].astype(int); pixels=a.astype(int);dist=np.sqrt(np.sum((pixels-bg)**2,axis=2));mask=(dist>38)|(pixels[:,:,2]<150);rgba=np.dstack([a,mask.astype('uint8')*255]);o=Image.fromarray(rgba,'RGBA');return o.crop(o.getbbox())

def fit(path, targetbbox, cell):
 im=detach(path);x1,y1,x2,y2=targetbbox;w=x2-x1;h=y2-y1;fac=min(w/im.width,h/im.height);nw=max(1,round(im.width*fac));nh=max(1,round(im.height*fac));res=im.resize((nw,nh),Image.Resampling.NEAREST);tile=Image.new('RGBA',cell); x=x1+(w-nw)//2;y=y2-nh;tile.alpha_composite(res,(x,y));return tile

def sheet(n,views):
 an=ET.parse(ref/'AnimData.xml').getroot().find('Anims');a=next(x for x in an if x.findtext('Name')==n);w=int(a.findtext('FrameWidth'));h=int(a.findtext('FrameHeight'));durs=a.findall('Durations/Duration'); normal=Image.open(ref/(n+'-Anim.png')).convert('RGBA'); rows=normal.height//h; dest=Image.new('RGBA',(w*len(durs),h*rows));
 for row,paths in views.items():
  assert len(paths)==len(durs)
  for f,path in enumerate(paths):
   box=normal.crop((f*w,row*h,(f+1)*w,(row+1)*h)).getbbox(); assert box
   # La taille est stabilisée sur l'ensemble de la boucle pour éviter les clignotements d'échelle.
   boxes=[normal.crop((k*w,row*h,(k+1)*w,(row+1)*h)).getbbox() for k in range(len(durs))];
   # Une seule taille pour toutes les frames d'une direction, alignée à une référence commune.
   width=min(26,max(v[2]-v[0] for v in boxes)); height=max(v[3]-v[1] for v in boxes); x=max(0,min(w-width, round((boxes[0][0]+boxes[0][2]-width)/2))); y=boxes[0][3]-height; box=(x,y,x+width,y+height)
   tile=fit(path,box,(w,h)); dest.alpha_composite(tile,(f*w,row*h))
 dest.save(p/(n+'-Anim-PARTIEL.png'));print(n,'canvas',dest.size,'directions renseignées',list(views))
 return dest
right=r/'revision-corpulence/repos-trois-quart-01.png';left=r/'Huit-directions/avant-gauche.png'
sheet('Sleep',{0:[r/'revision-corpulence/Sommeil-fidele-00.png',sleep/'sommeil-02-provisoire.png']})
sheet('Idle',{1:[right,idle/'idle-02-droite-provisoire.png'],7:[left,idle/'idle-02-gauche-provisoire.png']})
sheet('Walk',{1:[right,prev/'essai-manuel-jambe-1.png',right,prev/'essai-manuel-jambe-2.png']})
