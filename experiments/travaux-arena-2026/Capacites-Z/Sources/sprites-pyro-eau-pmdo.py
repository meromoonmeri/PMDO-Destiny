#!/usr/bin/env python3
"""Sprites d'effet dessinés pose par pose, selon la convention PMDO Dir8.
Deux prototypes distincts, créés par script : pas des images IA séparées.
"""
from PIL import Image,ImageDraw
from pathlib import Path
import math,io,struct
root=Path(__file__).resolve().parent.parent/'Prototypes'
fire=root/'Pyro-Explosion-Cataclysmique'/'V2-PMDO';water=root/'Super-Tourbillon-Abyssal'/'V2-PMDO'
fire.mkdir(parents=True,exist_ok=True);water.mkdir(parents=True,exist_ok=True)
D=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]
def write(sheet,path,name,size,n):
 sheet.save(path/(name+'.Dir8.png'));buf=io.BytesIO();sheet.save(buf,format='PNG');png=buf.getvalue()
 (path/(name+'.dir')).write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',size,size,4,n))
def coord(x,y):return round(x),round(y)
def poly(d,pts,col):d.polygon([coord(*p) for p in pts],fill=col)
# Projectile : silhouette et flammes redessinées à chaque pose, pas une image
# du projectile déplacée dans une planche ; la trajectoire appartient au moteur.
S=40;N=8;sheet=Image.new('RGBA',(S*N,S*8));F=[(128,36,12,255),(207,55,9,255),(249,112,9,255),(255,176,29,255),(255,225,93,255),(255,250,199,255)]
for row,(dx,dy) in enumerate(D):
 norm=math.hypot(dx,dy);ux=dx/norm;uy=dy/norm;vx=-uy;vy=ux
 def point(a,b):return (20+ux*a+vx*b,20+uy*a+vy*b)
 for t in range(N):
  im=Image.new('RGBA',(S,S));d=ImageDraw.Draw(im);f=(t%4)
  poly(d,[point(13,0),point(9,7),point(1,10),point(-5,7),point(-16-f,9),point(-10,2),point(-18+f,-1),point(-8,-4),point(-14,-10),point(-3,-7),point(3,-10),point(10,-7)],F[0])
  poly(d,[point(12,0),point(8,6),point(0,8),point(-5,4),point(-15+f,6),point(-9,0),point(-13-f,-3),point(-4,-4),point(0,-8),point(8,-6)],F[2])
  poly(d,[point(10,0),point(6,5),point(0,6),point(-3,3),point(-11-(t%3),2),point(-4,-1),point(-7,-5),point(1,-6),point(7,-4)],F[3])
  d.ellipse((15+(t%2),15,25+(t%2),25),fill=F[4]);d.ellipse((17+(t%2),17,23+(t%2),23),fill=F[5])
  for a,b in [(-14,12),(-19,-7),(-12,-13)]:
   x,y=coord(*point(a+f,b));d.rectangle((x,y,x+1,y+1),fill=F[2])
  sheet.alpha_composite(im,(t*S,row*S))
write(sheet,fire,'Pyro_PMDO_Projectile',S,N)
# Impact : 16 images différentes, expansion, étincelles et dissipation.
S=96;N=16;sheet=Image.new('RGBA',(S*N,S*8))
for row,(dx,dy) in enumerate(D):
 for t in range(N):
  im=Image.new('RGBA',(S,S));d=ImageDraw.Draw(im);r=min(30,4+3*t)
  if t<10:
   d.ellipse((48-r,48-r,48+r,48+r),fill=F[1],outline=F[0],width=2)
   r2=max(1,r-4-t//2);d.ellipse((48-r2,48-r2,48+r2,48+r2),fill=F[2])
   r3=max(1,r-8-t);d.ellipse((48-r3,48-r3,48+r3,48+r3),fill=F[4 if t<5 else 3])
  for k in range(10):
   a=k*math.tau/10+t*.08;dist=6+t*2.4;x=round(48+math.cos(a)*dist);y=round(48+math.sin(a)*dist*.75)
   if t>=3 and t<15:
    size=max(1,3-t//5);d.rectangle((x-size,y-size,x+size,y+size),fill=F[3 if (k+t)%2 else 2])
  sheet.alpha_composite(im,(t*S,row*S))
write(sheet,fire,'Pyro_PMDO_Impact',S,N)
# Vortex à la cible : arcs arrière/devant autour de la créature, perspective au
# sol conservée pour les 8 orientations ; écume et éclaboussures changent à chaque pose.
W=[(8,52,111,255),(13,103,163,255),(20,163,208,255),(66,209,235,255),(178,250,255,255)]
back=Image.new('RGBA',(S*N,S*8));front=Image.new('RGBA',(S*N,S*8))
for row,_ in enumerate(D):
 for t in range(N):
  b=Image.new('RGBA',(S,S));f=Image.new('RGBA',(S,S));bd=ImageDraw.Draw(b);fd=ImageDraw.Draw(f);r=min(34,8+t*4);end=1 if t<12 else max(.3,(16-t)/4)
  r=int(r*end);ry=max(3,int(r*.42));box=(48-r,51-ry,48+r,51+ry)
  bd.arc(box,180,355,fill=W[1],width=4);bd.arc((48-r+4,51-ry+3,48+r-4,51+ry-3),180,355,fill=W[3],width=2) if r>8 and ry>4 else None
  fd.arc(box,0,175,fill=W[2],width=4);fd.arc((48-r+4,51-ry+3,48+r-4,51+ry-3),0,175,fill=W[4],width=2) if r>8 and ry>4 else None
  for k in range(7):
   a=k*math.tau/7+t*.55;x=round(48+math.cos(a)*r);y=round(51+math.sin(a)*ry)
   d=fd if math.sin(a)>0 else bd;sz=1+(k+t)%2;d.rectangle((x-sz,y-sz,x+sz,y+sz),fill=W[3+(k%2)])
  for k in range(4):
   ang=k*math.tau/4+t*.2;x=round(48+math.cos(ang)*(r+4));y=round(48+math.sin(ang)*ry-((t*2+k*4)%16));fd.rectangle((x,y,x+1,y+3),fill=W[4])
  back.alpha_composite(b,(t*S,row*S));front.alpha_composite(f,(t*S,row*S))
write(back,water,'Tourbillon_PMDO_Arriere',S,N);write(front,water,'Tourbillon_PMDO_Avant',S,N)
print('Projectile feu 8x8 ; impact feu 16x8 ; vortex 16x8 sur deux calques')
