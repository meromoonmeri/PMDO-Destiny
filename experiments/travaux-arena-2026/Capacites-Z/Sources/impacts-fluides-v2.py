#!/usr/bin/env python3
"""Quatre fins PMD dessinées image par image ; conserve les autres étapes V1."""
from pathlib import Path
from PIL import Image,ImageDraw
import io,struct,math,json,shutil
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';R=H/'Capacites-Z/Prototypes'
cfg={'Selene':('Rayons-Seleno-Explosifs','SeleneV1_Impact',144,64),'Apocalypse':('Apocalypsis-Luminis','ApocalypseV1_Impact',144,64),'Helio':('Helio-Choc-Devastateur','HelioV1_Impact',144,56),'Colere':('Colere-du-Gardien-d-Alola','ColereV1_Avant',128,60)}
def native(name):
 raw=(G/'Content/Particle'/(name+'.dir')).read_bytes();size=struct.unpack_from('<q',raw)[0];im=Image.open(io.BytesIO(raw[8:8+size])).convert('RGBA');w,h,_,cnt=struct.unpack_from('<iiii',raw,8+size)
 return [im.crop((i*w,0,(i+1)*w,h)) for i in range(cnt)]
def paste(f,im,x,y,w,h,alpha=1):
 if w<1 or h<1 or alpha<=0:return
 v=im.resize((round(w),round(h)),Image.Resampling.NEAREST)
 if alpha<1:v.putalpha(v.getchannel('A').point(lambda a:round(a*max(0,alpha))))
 f.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def col(c,a):return tuple(round(x*clamp(a)) for x in c[:3])+(round(c[3]*clamp(a)),)
def ring(d,cx,cy,rx,ry,c,width=1):
 if rx>0 and ry>0:d.ellipse((round(cx-rx),round(cy-ry),round(cx+rx),round(cy+ry)),outline=c,width=width)
def ray(d,cx,cy,angle,r1,r2,c,width=2):d.line((round(cx+math.cos(angle)*r1),round(cy+math.sin(angle)*r1),round(cx+math.cos(angle)*r2),round(cy+math.sin(angle)*r2)),fill=c,width=width)
def sparkle(d,x,y,size,color):
 x=round(x);y=round(y);size=round(size)
 if size<1:return
 d.line((x-size,y,x+size,y),fill=color,width=1);d.line((x,y-size,x,y+size),fill=color,width=1)
expl=native('Explosion');bright=native('Shadow_Force_Hit_Light');moon=native('Moonlight_Sparkles');psy=native('Psycho_Shift_Charge');metal=native('Meteor_Mash_Star');flare=native('Flare_Blitz_Hit_Front')
# Lances d'origine : calcul identique à la maquette V1, sans son image d'explosion.
colere=R/cfg['Colere'][0]/'Generation-PMDO';raw=Image.open(colere/'Sources/lance-lumiere.png').convert('RGB')
import numpy as np
a=np.asarray(raw);r,g,b=[a[:,:,i].astype('int16') for i in range(3)];mask=(g>70)&(g>r*1.22)&(g>b*1.22);spear=Image.fromarray(np.dstack((a,(~mask).astype('uint8')*255)),'RGBA');spear=spear.crop(spear.getbbox()).resize((13,53),Image.Resampling.NEAREST)
def oldbank(path):
 data=path.read_bytes();n=struct.unpack_from('<q',data)[0];img=Image.open(io.BytesIO(data[8:8+n])).convert('RGBA');w,h,_,count=struct.unpack_from('<iiii',data,8+n);return [img.crop((i*w,0,(i+1)*w,h)) for i in range(count)]
oldcol=oldbank(colere/'ColereV1_Avant.dir')
positions=[(-34,-10),(-20,-22),(19,-22),(34,-10),(-40,8),(40,8),(-25,20),(25,20)]

def build(tag,t,N):
 cx=cy=N//2;f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
 if tag=='Selene':
  # Les rayons d'origine se poursuivent dans une compression et éclat lunaire animé.
  for j in range(7):
   age=t-j*4
   if 0<=age<23:
    ang=j*math.tau/7;outer=max(4,60-age*2.2);inner=max(0,outer-25)
    ray(d,cx,cy,ang,inner,outer,(99,47,190,255),5);ray(d,cx,cy,ang,inner,outer,(158,237,255,255),2)
  age=t-22
  if 0<=age<32:
   a=min(1,(age+1)/3,(32-age)/10);r=6+36*ease(age/12)
   ring(d,cx,cy,r,r*.78,col((114,72,218,230),a),3);ring(d,cx,cy,r*.82,r*.65,col((140,235,255,230),a),1)
   for j in range(9):
    ang=j*math.tau/9+age*.035;rad=8+age*1.4;ray(d,cx,cy,ang,rad,rad+max(2,14-age*.3),col((135,220,255,255),a),2)
   if age<12:paste(f,bright[min(len(bright)-1,age//2)],cx,cy,40+age*3,40+age*3,a)
   # Croissant obtenu en soustrayant un disque à un autre, animé et partiellement transparent.
   mask=Image.new('L',(N,N));md=ImageDraw.Draw(mask);rr=8+13*ease(age/8);md.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=round(230*a));md.ellipse((cx-rr+rr*.52,cy-rr-rr*.20,cx+rr+rr*.52,cy+rr-rr*.20),fill=0)
   glow=Image.new('RGBA',(N,N),(135,105,255,0));glow.putalpha(mask);f.alpha_composite(glow)
 elif tag=='Apocalypse':
  # Poutre prismatique construite en traits animés, pas un pilier bitmap redimensionné.
  age=t;en=min(1,(t+1)/5,(55-t)/12) if t<55 else 0
  if en>0:
   reach=70*ease((t+1)/9);w=6+15*ease(t/12);bottom=cy+min(38,reach*.6);top=cy-reach
   for j in range(-4,5):
    x=cx+j*w/4+math.sin(t*.17+j)*2;phase=.35+.65*(.5+.5*math.sin(t*.22+j*1.7));color=[(255,246,189,230),(255,168,208,210),(196,201,255,210),(255,222,137,230)][(j+4)%4]
    d.line((round(x),round(bottom),round(x+math.sin(t*.14+j)*3),round(top)),fill=col(color,en*phase),width=3 if abs(j)<2 else 2)
   for k in range(3):
    rad=(t*2.6+k*23)%68;ring(d,cx,cy+5,rad,rad*.26,col((255,225,160,220),en*(1-rad/80)),1)
   if 8<=t<40:paste(f,psy[min(len(psy)-1,(t-8)//3)],cx,cy,72,72,en*.7)
   for j in range(10):
    a=j*2.4+t*.07;rad=12+(j*13+t*1.2)%49;sparkle(d,cx+math.cos(a)*rad,cy+math.sin(a)*rad*.8,2+(j%2),col((255,230,190,255),en))
 elif tag=='Helio':
  # Explosion native réellement animée, prolongée d'anneaux et de débris mouvants.
  en=min(1,(t+1)/3,(50-t)/12) if t<50 else 0
  if t<36:
   i=min(len(expl)-1,t//2);sz=58+34*ease(t/8);paste(f,expl[i],cx,cy,sz,sz,en)
  if 2<=t<28:
   age=t-2;paste(f,flare[min(len(flare)-1,age//2)],cx,cy,96,96,en*.8)
  d=ImageDraw.Draw(f)
  for j in range(2):
   age=t-4-j*8
   if 0<=age<25:
    radius=8+age*2.2;a=en*(1-age/25);ring(d,cx,cy,radius,radius*.65,col((255,212,78,245),a),2)
  for j in range(12):
   age=t-(j%4)*2
   if 0<=age<34:
    a=min(1,(34-age)/7);angle=j*math.tau/12+.1;rad=7+age*(1.2+(j%3)*.16)
    ray(d,cx,cy,angle,rad,rad+5+(j%3)*2,col((255,164+7*j,60,255),a),2)
    if j%3==0:paste(f,metal[min(len(metal)-1,age//4)],cx+math.cos(angle)*rad,cy+math.sin(angle)*rad,11,11,a)
 else:
  # Conserve octet pour octet l'avant des lances jusqu'au tout premier impact.
  if t<28:return oldcol[t].copy()
  real=t*3
  for j,(x,y) in enumerate(positions):
   age=real-(11+j*8)
   if y>=0 and 0<=age<19:
    if age<8:paste(f,spear,cx+x,cy+y-26-(8-age)*8,13,53)
    else:
     a=max(0,1-(age-8)/11);paste(f,spear,cx+x,cy+y-26,13,53,a)
     if age-8<len(moon):paste(f,moon[age-8],cx+x,cy+y,25,25,a)
  age=real-82
  if 0<=age<70:
   en=min(1,(age+1)/5,(70-age)/15);d=ImageDraw.Draw(f)
   if age<30:paste(f,expl[min(len(expl)-1,age//2)],cx,cy,75+20*ease(age/8),75+20*ease(age/8),en)
   d=ImageDraw.Draw(f)
   for k in range(3):
    p=age-k*8
    if 0<=p<35:
     radius=7+p*1.4;ring(d,cx,cy,radius,radius*.65,col((255,222,116,245),en*(1-p/35)),2)
   for j in range(12):
    p=age-(j%3)*2
    if 0<=p<38:
     a=min(1,(38-p)/10);ang=j*math.tau/12;rad=8+p*1.0
     ray(d,cx,cy,ang,rad,rad+7,col((255,225,150,255),a),2);sparkle(d,cx+math.cos(ang)*rad,cy+math.sin(ang)*rad,2,col((255,255,230,255),a))
   if age<40:paste(f,moon[min(len(moon)-1,age//4)],cx,cy,90,90,en*.9)
 return f
for tag,(folder,name,N,T) in cfg.items():
 P=R/folder/'Generation-PMDO/V2-impacts';P.mkdir(parents=True,exist_ok=True);sheet=Image.new('RGBA',(N*T,N*8));preview=Image.new('RGBA',(N*8,N*math.ceil(T/8)))
 for t in range(T):
  frame=build(tag,t,N);preview.alpha_composite(frame,((t%8)*N,(t//8)*N))
  for direction in range(8):sheet.alpha_composite(frame,(t*N,direction*N))
 b=io.BytesIO();sheet.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T));preview.save(P/(name+'-planche.png'))
 print(tag,'banque animée',T,'images',len(raw),'octets')
