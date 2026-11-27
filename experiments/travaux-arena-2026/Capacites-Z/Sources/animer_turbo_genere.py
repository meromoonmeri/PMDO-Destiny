#!/usr/bin/env python3
"""Turbo-Charge : animer le dessin généré, calques PMDO Dir8 expérimentaux.
Le corps du Pokémon n'est pas inclus dans les VFX. Le test ne constitue pas
une capacité complète (déplacement, cible et dégâts restent à implémenter).
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, math, io,struct,json
P=Path(__file__).resolve().parent.parent/'Prototypes'/'Turbo-Charge-Bulldozer'
source=Image.open(P/'Source-generation-turbo.png').convert('RGB')
arr=np.array(source)
# Le fond noir et le trou central sont transparents. On ne prétend pas récupérer
# une transparence native : le dessin généré avait un fond noir opaque.
mask=(arr.max(axis=2)>48)&(arr[:,:,0]>arr[:,:,2]*1.12)
y,x=np.where(mask); box=(max(0,int(x.min())-4),max(0,int(y.min())-4),min(source.width,int(x.max())+5),min(source.height,int(y.max())+5))
rgba=np.dstack([arr,np.where(mask,255,0).astype('uint8')]); cut=Image.fromarray(rgba).crop(box)
# Réduction avec pixels francs, puis palette fixe cohérente avec le dessin source.
cut=cut.resize((100,48),Image.Resampling.NEAREST)
a=np.array(cut);palette=np.array([[101,50,16],[162,79,10],[218,125,13],[245,170,22],[255,206,63],[255,229,127],[255,244,190],[255,253,235]],dtype=np.int16)
rgb=a[:,:,:3].astype(np.int16);ds=((rgb[:,:,None,:]-palette[None,None,:,:]).astype(np.int32)**2).sum(3);a[:,:,:3]=palette[ds.argmin(2)].astype(np.uint8);a[a[:,:,3]==0,:3]=0
cut=Image.fromarray(a);cut.save(P/'Motif-turbo-detoure.png')
N=32; S=128
# PMDO Dir8 : down, down-left, left, up-left, up, up-right, right, down-right.
dirs=[('bas',90),('bas-gauche',135),('gauche',180),('haut-gauche',225),('haut',270),('haut-droite',315),('droite',0),('bas-droite',45)]
back=Image.new('RGBA',(S*N,S*8));front=Image.new('RGBA',(S*N,S*8))
def faded(img,a):
 p=np.array(img);p[:,:,3]=(p[:,:,3].astype(np.float32)*max(0,min(1,a))).astype('uint8');return Image.fromarray(p)
def rotate(im,angle): return im.rotate(-angle,resample=Image.Resampling.NEAREST,center=(S//2,S//2))
def star(draw,x,y,r, color):
 draw.line((x-r,y,x+r,y),fill=color,width=1);draw.line((x,y-r,x,y+r),fill=color,width=1);draw.point((x,y),fill=(255,255,232,color[3]))
for t in range(N):
 rear=Image.new('RGBA',(S,S)); rd=ImageDraw.Draw(rear)
 ground=Image.new('RGBA',(S,S)); gd=ImageDraw.Draw(ground)
 top=Image.new('RGBA',(S,S)); fd=ImageDraw.Draw(top)
 # Charge basse qui se resserre puis disparaît pour ne pas masquer le Pokémon.
 if t<12:
  r=35-1.1*t; op=int(185*min(1,(t+1)/3)*min(1,(12-t)/4))
  gd.ellipse((64-r,67-r*.32,64+r,67+r*.32),outline=(255,203,75,op),width=2)
  for j in range(8):
   a=j*math.tau/8+t*.24;x=int(64+math.cos(a)*r);y=int(67+math.sin(a)*r*.32);star(gd,x,y,2,(255,238,164,op))
 # Déploiement du motif généré ; il glisse vers l'avant puis s'éteint.
 if 7<=t<=24:
  start=min(1,(t-7)/4); end=min(1,(25-t)/5);opa=start*end
  advance=round(min(27,max(0,(t-10)*2.1)))
  patch=faded(cut,opa)
  rear.alpha_composite(patch,(-24+advance,40))
 # Le grand éclat est de l'autre côté du Pokémon, en direction de l'impact.
 if 15<=t<28:
  q=t-15;r=4+q*1.15;op=int(220*min(1,(q+1)/3)*min(1,(28-t)/8))
  x=88+round(min(8,q*.7));y=64
  fd.ellipse((x-r,y-r,x+r,y+r),outline=(255,238,169,op),width=2)
  for j in range(7):
   angle=j*math.tau/7+.3;distance=r+5+(q%4)
   xx=round(x+math.cos(angle)*distance);yy=round(y+math.sin(angle)*distance)
   star(fd,xx,yy,1+j%2,(255,212,93,op))
 # Un mince cercle près du corps rappelle la charge Z.
 if 7<=t<=16:
  op=int(140*min(1,(t-6)/3)*min(1,(17-t)/3))
  fd.ellipse((52,57,76,71),outline=(255,241,183,op),width=1)
 for row,(name,angle) in enumerate(dirs):
  layer=ground.copy();layer.alpha_composite(rotate(rear,angle))
  back.alpha_composite(layer,(t*S,row*S))
  front.alpha_composite(rotate(top,angle),(t*S,row*S))

def save(im,name):
 im.save(P/(name+'.Dir8.png'))
 a=np.array(im);alpha=a[:,:,3].astype(np.uint16);a[:,:,:3]=((a[:,:,:3].astype(np.uint16)*alpha[:,:,None]+127)//255).astype(np.uint8)
 buf=io.BytesIO();Image.fromarray(a).save(buf,format='PNG');z=buf.getvalue()
 (P/(name+'.dir')).write_bytes(struct.pack('<q',len(z))+z+struct.pack('<iiii',S,S,4,N))
save(back,'Turbo_Genere_Arriere');save(front,'Turbo_Genere_Avant')
(P/'manifest-generation.json').write_text(json.dumps({'source':'Source-generation-turbo.png','source_mode':'image générée puis détourée ; animation assemblée procéduralement','frame_size':[S,S],'poses':N,'ticks_per_frame':2,'direction_order':[d[0] for d in dirs],'layers':['Arriere','Avant'],'gameplay':'Non implémenté','reference_fidelite':'Adaptation expérimentale, non copie exacte des jeux officiels'},ensure_ascii=False,indent=2),encoding='utf-8')
# Planche de contrôle hors jeu.
preview=Image.new('RGBA',(S*4,S*8),(25,35,44,255))
for y in range(8):
 for col,t in enumerate([4,11,17,23]):
  area=(t*S,y*S,(t+1)*S,(y+1)*S); preview.alpha_composite(back.crop(area),(col*S,y*S));preview.alpha_composite(front.crop(area),(col*S,y*S))
preview.convert('RGB').save(P/'controle-generation-8-directions.png')
print('OK:',box, '32 poses, huit directions, deux calques')
