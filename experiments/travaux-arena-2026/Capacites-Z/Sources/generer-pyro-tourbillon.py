#!/usr/bin/env python3
# Deux prototypes distincts, issus d'images générées, PMDO .Dir8 + .dir.
from PIL import Image, ImageDraw
from pathlib import Path
import numpy as np, math, io, struct
root=Path(__file__).resolve().parent.parent/'Prototypes'
S=128; N=32
D=[(0,1,90),(-1,1,135),(-1,0,180),(-1,-1,225),(0,-1,270),(1,-1,315),(1,0,0),(1,1,45)]
def cut(path, mode):
 a=np.array(Image.open(path).convert('RGB')); mx=a.max(2)
 if mode=='feu': mask=(mx>60)&((a[:,:,0].astype(float)>a[:,:,2].astype(float)*1.2)|(a.min(2)>180))
 else: mask=(mx>42)&(a[:,:,2]>a[:,:,0]*1.15)
 ys,xs=np.where(mask);box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
 rgba=np.dstack([a,np.where(mask,255,0).astype('uint8')]); im=Image.fromarray(rgba).crop(box)
 # Planche à la taille du jeu : interpolation nearest pour garder les pixels.
 return im.resize((54,42) if mode=='feu' else (70,48),Image.Resampling.NEAREST)
def write(im,path,name):
 im.save(path/(name+'.Dir8.png'))
 a=np.array(im);alpha=a[:,:,3].astype(np.uint16);a[:,:,:3]=((a[:,:,:3].astype(np.uint16)*alpha[:,:,None]+127)//255).astype('uint8')
 b=io.BytesIO();Image.fromarray(a).save(b,format='PNG');v=b.getvalue()
 (path/(name+'.dir')).write_bytes(struct.pack('<q',len(v))+v+struct.pack('<iiii',S,S,4,N))
def scale_alpha(im,f):
 a=np.array(im);a[:,:,3]=(a[:,:,3].astype(float)*max(0,min(1,f))).astype('uint8');return Image.fromarray(a)
# FEU : une boule distincte suit la direction depuis le lanceur et éclate à la cible.
p=root/'Pyro-Explosion-Cataclysmique';raw=cut(p/'source-pyro.png','feu');raw.save(p/'motif-detoure.png')
sheet=Image.new('RGBA',(S*N,S*8));
for row,(dx,dy,angle) in enumerate(D):
 for t in range(N):
  frame=Image.new('RGBA',(S,S));d=ImageDraw.Draw(frame)
  if 2<=t<=17:
   k=min(1,(t-2)/10); x=64+round(dx*24*k);y=64+round(dy*24*k)
   scale=0.55+min(1,(t-2)/5)*.45
   w,h=round(54*scale),round(42*scale)
   flame=raw.resize((w,h),Image.Resampling.NEAREST).rotate(-angle,Image.Resampling.NEAREST,expand=True)
   frame.alpha_composite(flame,(x-flame.width//2,y-flame.height//2))
  if 14<=t<=28:
   q=t-14;x=64+dx*24;y=64+dy*24;r=int(4+min(q,8)*2.5);alpha=int(255*min(1,(29-t)/6))
   d.ellipse((x-r,y-r,x+r,y+r),outline=(255,144,23,alpha),width=3)
   if q<5:d.ellipse((x-r//2,y-r//2,x+r//2,y+r//2),fill=(255,238,128,alpha))
   for j in range(10):
    a=j*math.tau/10+q*.08;rr=r+2+(q%4);px=round(x+math.cos(a)*rr);py=round(y+math.sin(a)*rr);d.rectangle((px,py,px+1,py+1),fill=(255,211,72,alpha))
  sheet.alpha_composite(frame,(t*S,row*S))
write(sheet,p,'Pyro_Z_Impact')
# EAU : tourbillon horizontal au sol autour de la cible ; on garde l'horizon
# horizontal dans chaque orientation. Le placement de la cible est directionnel.
p=root/'Super-Tourbillon-Abyssal';raw=cut(p/'source-tourbillon.png','eau');raw.save(p/'motif-detoure.png');sheet=Image.new('RGBA',(S*N,S*8))
for row,(dx,dy,angle) in enumerate(D):
 for t in range(N):
  im=Image.new('RGBA',(S,S));d=ImageDraw.Draw(im)
  if 2<=t<=27:
   phase=min(1,(t-2)/6);fin=min(1,(28-t)/6);siz=max(5,round(70*phase));h=max(4,round(48*phase))
   # Direction tourne à plat, puis ellipse recompressée : pas une roue verticale.
   square=raw.resize((70,70),Image.Resampling.NEAREST).rotate(-t*9,Image.Resampling.NEAREST)
   ring=scale_alpha(square.resize((siz,h),Image.Resampling.NEAREST),fin)
   im.alpha_composite(ring,(64-siz//2,66-h//2))
   for j in range(6):
    a=math.tau*j/6+t*.2;xx=int(64+math.cos(a)*siz*.53);yy=int(66+math.sin(a)*h*.53);r=1+(j%2);d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(132,235,255,int(220*fin)))
  sheet.alpha_composite(im,(t*S,row*S))
write(sheet,p,'Tourbillon_Z_Cible')
print('Création terminée : feu (Dir8 projectile) ; eau (vortex horizontal cible x8).')
