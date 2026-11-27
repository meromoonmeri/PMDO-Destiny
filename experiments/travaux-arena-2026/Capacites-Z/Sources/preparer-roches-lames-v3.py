#!/usr/bin/env python3
"""Planches d'effets Hurlement V3, pas d'installation dans le jeu."""
from pathlib import Path
from PIL import Image, ImageDraw
import math,io,struct,json,numpy as np
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-Z/Prototypes/Hurlement-des-Roches-Lames/Generation-PMDO'; V=P/'V3'; S=V/'Sources';V.mkdir(exist_ok=True)
N=128

def key(path,box):
 a=np.array(Image.open(path).convert('RGB'));r,g,b=[a[:,:,i].astype('int16') for i in range(3)]; alpha=np.where((g>55)&(g>r*1.22)&(g>b*1.22),0,255).astype('uint8');im=Image.fromarray(np.dstack((a,alpha)),'RGBA');im=im.crop(im.getbbox());im.thumbnail(box,Image.Resampling.NEAREST);return im
wave=key(S/'onde-sonore.png',(24,35));crack=key(S/'fissure.png',(96,65));spike=key(S/'pic-roche-corrige.png',(25,47))
def native(n):
 b=(G/'Content/Particle'/f'{n}.dir').read_bytes();k=struct.unpack_from('<q',b)[0];im=Image.open(io.BytesIO(b[8:8+k])).convert('RGBA');w,h,_,c=struct.unpack_from('<iiii',b,8+k);return [im.crop((i*w,0,(i+1)*w,h)) for i in range(c)]
rocks=native('Rock_Piece_Rotating')
def paste(f,im,x,y,alpha=1):
 im=im.copy()
 if alpha<1:im.putalpha(im.getchannel('A').point(lambda v:round(v*max(0,alpha))))
 f.alpha_composite(im,(round(x-im.width/2),round(y-im.height/2)))
def pngsheet(frames,path):
 cols=8; rows=(len(frames)+cols-1)//cols;s=Image.new('RGBA',(N*cols,N*rows))
 for i,f in enumerate(frames):s.alpha_composite(f,((i%cols)*N,(i//cols)*N))
 s.save(path,optimize=True)
def dirsheet(rows,path):
 count=len(rows[0]);s=Image.new('RGBA',(N*count,N*8))
 for j,row in enumerate(rows):
  for i,f in enumerate(row):s.alpha_composite(f,(i*N,j*N))
 b=io.BytesIO();s.save(b,format='PNG',optimize=True);p=b.getvalue();path.write_bytes(struct.pack('<q',len(p))+p+struct.pack('<iiii',N,N,4,count))
# L'onde part du centre du lanceur, vers la droite dans l'image de référence.
son=[]
for t in range(48):
 f=Image.new('RGBA',(N,N))
 for j in range(3):
  age=t-j*6
  if 0<=age<32:
   progress=age/31;x=66+progress*45;y=64;scale=.56+.44*progress
   w=wave.resize((max(1,int(wave.width*scale)),max(1,int(wave.height*scale))),Image.Resampling.NEAREST)
   paste(f,w,x,y,min(1,age/4,(32-age)/7)*(.9-j*.1))
 son.append(f)
# Orientation du moteur : bas, bas-gauche, gauche, haut-gauche, haut, haut-droite, droite, bas-droite.
angles=[-90,-135,180,135,90,45,0,-45]; sonrows=[[f.rotate(deg,resample=Image.Resampling.NEAREST,center=(64,64)) for f in son] for deg in angles]
# Fissure qui se propage, révélée du centre vers l'extérieur puis se dissipe.
cracks=[]
for t in range(48):
 f=Image.new('RGBA',(N,N));r=min(58, max(0,(t+1)*2.1));mask=Image.new('L',(N,N));ImageDraw.Draw(mask).ellipse((64-r,64-r*.72,64+r,64+r*.72),fill=255)
 layer=Image.new('RGBA',(N,N));paste(layer,crack,64,68);a=np.array(layer);a[:,:,3]=(a[:,:,3].astype('float32')*np.asarray(mask)/255*min(1,(48-t)/8)).astype('uint8');f=Image.fromarray(a,'RGBA');cracks.append(f)
# Apparition par sortie du sol : le haut du pic est progressivement révélé au-dessus du socle.
spikes=[]
placements=[(-28,-6,0,0.78),(0,-18,3,1.0),(28,-6,6,0.82),(-34,11,9,0.82),(34,11,12,0.82),(-20,25,15,1.0),(20,25,18,1.0),(0,31,22,0.72)]
for t in range(72):
 f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
 for j,(dx,dy,start,scale) in enumerate(placements):
  age=t-start
  if age<0:continue
  grow=min(1,(age+1)/11);fade=min(1,(72-t)/10);sw=int(22*scale);sh=int(48*scale);v=spike.resize((sw,sh),Image.Resampling.NEAREST)
  if j%2:v=v.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  # Clipping dynamique plutôt qu'un simple agrandissement : le sommet émerge du sol.
  reveal=max(1,round(sh*grow));v=v.crop((0,0,sw,reveal));x=64+dx+round((1-grow)*(-dx)*.08);base=70+dy
  v.putalpha(v.getchannel('A').point(lambda a:round(a*fade)));f.alpha_composite(v,(round(x-sw/2),round(base-reveal)))
  if 0<=age<18:
   for k in range(2):
    d1=age*.65+3;x2=x+(-1 if k else 1)*d1;y2=base+math.sin(age*.23+k)*4-age*.16
    rock=rocks[(age//2+j+k)%len(rocks)].resize((7,7),Image.Resampling.NEAREST);paste(f,rock,x2,y2,fade)
 spikes.append(f)
# Impact : fissures d'abord, émergence progressivement, les pierres subsistent puis retombent.
impact=[]
for t in range(100):
 f=Image.new('RGBA',(N,N))
 if t<48:f.alpha_composite(cracks[t])
 if 28<=t<100:f.alpha_composite(spikes[t-28])
 impact.append(f)
pngsheet(son,V/'01-onde-sonore-48images-128px.png');pngsheet(cracks,V/'02-fissures-48images-128px.png');pngsheet(spikes,V/'03-pics-roche-72images-128px.png');pngsheet(impact,V/'04-impact-compose-100images-128px.png')
dirsheet(sonrows,V/'RochesLamesV3_Onde.dir');dirsheet([impact]*8,V/'RochesLamesV3_Impact.dir')
z=json.loads((P/'splintered_stormshards-v2-test-only.json').read_text());fx=z['Object']['Data']['HitFX'];fx['Emitter']['Anim']['Anim']['AnimIndex']='RochesLamesV3_Impact';fx['Delay']=100;fx['Sound']='DUN_Stone_Edge';(V/'splintered_stormshards-v3-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
print('Planches créées : 48 onde, 48 fissures, 72 pics, 100 impact composé ; 8 orientations onde.')
