#!/usr/bin/env python3
"""Cage de 16 slashs projetée d'un volume 3D orienté, pulsation puis rupture sans distorsion."""
from pathlib import Path
from PIL import Image, ImageDraw
import io, struct, math, json, shutil
P=Path(__file__).resolve().parent;BASE=P.parent
ns={'__file__':str(BASE/'V3/preparer-v3.py')};exec((BASE/'V3/preparer-v3.py').read_text().split('wisp=clean(')[0],ns)
clean,paste,poses=ns['clean'],ns['paste'],ns['sprites']()
wisp=clean(BASE/'Sources/feu-follet-sombre.png',64)
N=160; T=90
dirs=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]
def mix(a,b,f):return tuple(x+(y-x)*f for x,y in zip(a,b))
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def project(q,dx,dy):
 # Coordonnee longitudinale, laterale et hauteur d'un volume construit en 3D.
 length,width,z=q; norm=math.hypot(dx,dy); dx/=norm;dy/=norm
 x=length*dx-width*dy; y=length*dy+width*dx
 depth=210/(210+y*.65)
 return (80+x*depth,80+(y*.48-z*.92)*depth)
def shape(dx,dy):
 # Prisme effilé : sa pointe est orientée vers la cible et son volume varie vraiment selon la direction.
 sections=[]
 for l in (-49,0,49):
  width=28-(l+49)*.09;height=26-(l+49)*.035
  sections.append([(l,-width,-height),(l,width,-height),(l,width,height),(l,-width,height)])
 strokes=[]
 for section in sections:
  for k in range(4):strokes.append((section[k],section[(k+1)%4]))
 for k in range(4):strokes.append((sections[0][k],sections[2][k]))
 # D'abord les arêtes lointaines, puis les arêtes transversales et proches.
 order=[0,12,5,9,14,2,7,10,13,3,4,11,15,1,6,8]
 return [(project(strokes[i][0],dx,dy),project(strokes[i][1],dx,dy),i) for i in order]
def line(draw,a,b,alpha=1,pulse=0):
 if alpha<=0:return
 points=[(round(a[0]),round(a[1])),(round(b[0]),round(b[1]))]
 draw.line(points,fill=(int(65*alpha),int(13*alpha),int(99*alpha),int(210*alpha)),width=5 if pulse>.5 else 3)
 draw.line(points,fill=(int(188*alpha),int(88*alpha),int(244*alpha),int(255*alpha)),width=2 if pulse>.4 else 1)
 if pulse>.4:draw.line(points,fill=(int(255*alpha),int(239*alpha),int(255*alpha),int(255*alpha)),width=1)
def build(dx,dy):
 strokes=shape(dx,dy);frames=[]
 for t in range(T):
  f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
  if t<52:
   pulse=math.sin(math.pi*min(1,max(0,(t-40)/11))) if t>=40 else 0
   for j,(a,b,k) in enumerate(strokes):
    start=3+j*2;age=t-start
    if age<0:continue
    if j%2:a,b=b,a
    end=mix(a,b,smooth((age+1)/3))
    line(d,a,end,.77+.23*pulse,pulse)
    if age<6:
     for lag,op in ((2,.22),(0,.8)):
      pos=mix(a,b,smooth((age+1-lag)/3));alpha=min(1,(age+1)/2,(6-age)/2)*op
      paste(f,poses[j%len(poses)],pos[0],pos[1],21,26,alpha,flip=j%2==1)
  else:
   # Tous les bords éclatent immédiatement : ce sont bien les slashs existants, pas une image plaquée.
   age=t-52
   if age<17:
    fade=max(0,1-age/17)
    for j,(a,b,k) in enumerate(strokes):
     for part in range(3):
      p0=mix(a,b,part/3+.03);p1=mix(a,b,(part+1)/3-.04)
      mid=mix(p0,p1,.5); vx=(mid[0]-80)*.33+math.sin(j*4+part)*4;vy=(mid[1]-80)*.33+math.cos(j*5+part)*4
      dt=age/16; ox=vx*dt;oy=vy*dt;ang=dt*((j%5)-2)*.28;c=math.cos(ang);s=math.sin(ang)
      def trans(pt):
       x=pt[0]-mid[0];y=pt[1]-mid[1];return (mid[0]+ox+x*c-y*s,mid[1]+oy+x*s+y*c)
      line(d,trans(p0),trans(p1),fade,1 if age<3 else 0)
    if age<3:
     for x,y in (project(q,dx,dy) for q in [(-49,-28,-26),(-49,28,26),(49,-19,22),(49,19,-22)]):
      d.line((round(x)-3,round(y),round(x)+3,round(y)),fill=(255,238,255,255),width=1);d.line((round(x),round(y)-3,round(x),round(y)+3),fill=(255,238,255,255),width=1)
   # Six feux s'échappent des anciens bords puis sont absorbés.
   for j in range(6):
    age=t-(56+j*2)
    if age<0 or age>=28:continue
    a,b,_=strokes[(j*3)%len(strokes)];src=mix(a,b,.5);dest=(80-24*dx,80-24*dy);q=smooth(age/22)
    x=src[0]+(dest[0]-src[0])*q+math.sin(q*math.pi)*math.cos(j)*4
    y=src[1]+(dest[1]-src[1])*q+math.sin(q*math.pi)*math.sin(j)*4
    fade=min(1,(age+1)/3,(28-age)/5);size=11*(1-.45*q)
    paste(f,wisp,x,y,size,size*1.1,fade)
  frames.append(f)
 return frames
sheet=Image.new('RGBA',(N*T,N*8));preview=Image.new('RGBA',(N*8,N*8))
for r,(dx,dy) in enumerate(dirs):
 frames=build(dx,dy)
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,(i*N,r*N))
 for i,frame_index in enumerate([8,20,35,43,48,51,55,60]):preview.alpha_composite(frames[frame_index],(i*N,r*N))
b=io.BytesIO();sheet.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/'LameV5_Volume.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T));preview.save(P/'LameV5-8-directions.png')
shutil.copy2(BASE/'LameEnPeine_Charge.dir',P/'LameEnPeine_Charge.dir')
z=json.loads((BASE/'bitter_blade-v1-test-only.json').read_text());data=z['Object']['Data'];data['BeforeHits']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'LameV5_Espace','ArgTable':'{}'}}]
data['HitFX']['Delay']=0;data['HitFX']['Sound']='';data['HitFX']['Emitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0};data['HitFX']['ScreenMovement']={'MinShake':0,'MaxShake':0,'MaxShakeTime':0}
(P/'bitter_blade-v5-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('V5 : 8 projections 3D, 16 slashs, pulsation, rupture nette, feux ; sans distorsion.')
