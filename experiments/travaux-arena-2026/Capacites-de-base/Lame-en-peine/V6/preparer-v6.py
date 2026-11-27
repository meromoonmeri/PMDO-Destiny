#!/usr/bin/env python3
"""Neuf rémanences et coups individuels, puis un coup d'âme décisif ; pas de cage ni de distorsion."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import io,struct,math,json,shutil
P=Path(__file__).resolve().parent;BASE=P.parent
ns={'__file__':str(BASE/'V3/preparer-v3.py')};exec((BASE/'V3/preparer-v3.py').read_text().split('wisp=clean(')[0],ns)
clean,paste,poses=ns['clean'],ns['paste'],ns['sprites']();wisp=clean(BASE/'Sources/feu-follet-sombre.png',64)
N=160;T=84;dirs=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def xy(a,b,q):return (a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q)
def polyline(d,a,b,alpha,wide=False):
 if alpha<=0:return
 coords=[tuple(round(z) for z in a),tuple(round(z) for z in b)]
 d.line(coords,fill=(int(58*alpha),int(8*alpha),int(85*alpha),int(230*alpha)),width=7 if wide else 5)
 d.line(coords,fill=(int(142*alpha),int(52*alpha),int(214*alpha),int(250*alpha)),width=4 if wide else 3)
 d.line(coords,fill=(int(245*alpha),int(207*alpha),int(255*alpha),int(255*alpha)),width=1)
def spectral_masks(angle):
 # Masse spirituelle abstraite autour de la cible, séparée selon le plan du coup final.
 mask=Image.new('L',(N,N));d=ImageDraw.Draw(mask)
 d.ellipse((65,57,95,94),fill=105)
 d.polygon([(67,78),(63,88),(67,86),(65,100),(72,94),(75,104),(80,96),(85,104),(88,94),(95,101),(93,87),(98,90),(94,77)],fill=105)
 d.ellipse((70,62,90,88),fill=160);d.polygon([(75,61),(78,52),(80,60),(84,54),(85,64)],fill=125)
 a=np.asarray(mask);yy,xx=np.indices(a.shape);ux,uy=math.cos(angle),math.sin(angle)
 side=(xx-80)*(-uy)+(yy-80)*ux
 return [Image.fromarray(np.where(side<0,a,0).astype('uint8')),Image.fromarray(np.where(side>=0,a,0).astype('uint8'))]
def soul_layer(f,mask,offset,alpha):
 if alpha<=0:return
 arr=np.asarray(mask,dtype=np.float32);a=np.asarray(arr*alpha,dtype='uint8'); color=np.zeros((N,N,4),dtype='uint8');color[:,:,0]=45;color[:,:,1]=6;color[:,:,2]=100;color[:,:,3]=a
 v=Image.fromarray(color,'RGBA');f.alpha_composite(v,(round(offset[0]),round(offset[1])))
def final_slash(f,angle,age):
 d=ImageDraw.Draw(f);u=(math.cos(angle),math.sin(angle));n=(-u[1],u[0]);progress=ease((age+1)/3)
 start=(80-u[0]*72,80-u[1]*72);end=xy(start,(80+u[0]*72,80+u[1]*72),progress)
 fade=1 if age<=4 else max(0,1-(age-4)/8)
 # Fente épaisse et effilée, différente des traits de la rafale.
 for w,c in [(9,(38,2,56)),(6,(98,15,145)),(3,(225,115,255)),(1,(255,248,255))]:
  pts=[(start[0],start[1]),(start[0]+(end[0]-start[0])*.55+n[0]*w,start[1]+(end[1]-start[1])*.55+n[1]*w),(end[0],end[1]),(start[0]+(end[0]-start[0])*.55-n[0]*w,start[1]+(end[1]-start[1])*.55-n[1]*w)]
  d.polygon([(round(x),round(y)) for x,y in pts],fill=tuple(int(x*fade) for x in c)+(int(255*fade),))
 if age<5:
  for k in range(6):
   q=(k-2.5)*11;cen=(80+u[0]*q,80+u[1]*q);side=1 if k%2 else -1
   p=(cen[0]+n[0]*side*(4+age*1.5),cen[1]+n[1]*side*(4+age*1.5))
   d.line((round(p[0]),round(p[1]),round(p[0]+n[0]*side*6),round(p[1]+n[1]*side*6)),fill=(210,150,255,230),width=1)
def build(dx,dy):
 norm=math.hypot(dx,dy);direction=math.atan2(dy/norm,dx/norm);angle=direction+math.pi/3; masks=spectral_masks(angle)
 # Les neuf trajectories se croisent à proximité de la cible, sans dessiner de cage.
 strokes=[]
 for j in range(9):
  theta=direction+j*2.39996+.35; u=(math.cos(theta),math.sin(theta));n=(-u[1],u[0]);shift=((j%3)-1)*10
  center=(80+n[0]*shift,80+n[1]*shift);a=(center[0]-u[0]*39,center[1]-u[1]*39);b=(center[0]+u[0]*39,center[1]+u[1]*39)
  if j%2:a,b=b,a
  strokes.append((a,b))
 frames=[]
 for t in range(T):
  f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
  for j,(a,b) in enumerate(strokes):
   age=t-(2+j*4)
   if not 0<=age<14:continue
   q=ease((age+1)/4);end=xy(a,b,q);alpha=min(1,(age+1)/2,(14-age)/6)*.9
   polyline(d,a,end,alpha)
   if age<7:
    for lag,op in ((2,.18),(1,.30),(0,.83)):
     pos=xy(a,b,ease((age+1-lag)/4));appearance=min(1,(age+1)/2,(7-age)/3)
     paste(f,poses[j%len(poses)],pos[0],pos[1],23,28,appearance*op,flip=j%2==1)
  if 38<=t<68:
   age=t-42;separation=0 if age<0 else ease(age/10)*15;fade=(min(1,(t-37)/4) if age<0 else max(0,1-max(0,age-7)/18))
   nx,ny=-math.sin(angle),math.cos(angle)
   for side,mask in enumerate(masks):
    sign=-1 if side==0 else 1;soul_layer(f,mask,(sign*nx*separation,sign*ny*separation),fade)
  if 38<=t<=46:
   q=ease((t-38)/6);u=(math.cos(angle),math.sin(angle));pos=(80-u[0]*(53-48*q),80-u[1]*(53-48*q))
   alpha=min(1,(t-37)/2,(47-t)/4);paste(f,poses[5],pos[0],pos[1],30,36,alpha*.85,flip=dx<0)
  if 42<=t<54:final_slash(f,angle,t-42)
  # Braises d'âme libérées, attirées vers la case du lanceur.
  for j in range(6):
   age=t-(48+j*2)
   if age<0 or age>=27:continue
   a=angle+j*math.tau/6; src=(80+math.cos(a)*18,80+math.sin(a)*18);dest=(80-24*dx,80-24*dy);q=ease(age/21)
   x=src[0]+(dest[0]-src[0])*q+math.sin(q*math.pi)*math.cos(a+math.pi/2)*5
   y=src[1]+(dest[1]-src[1])*q+math.sin(q*math.pi)*math.sin(a+math.pi/2)*5
   fade=min(1,(age+1)/3,(27-age)/5);size=12*(1-.55*q);paste(f,wisp,x,y,size,size*1.1,fade)
  frames.append(f)
 return frames
sheet=Image.new('RGBA',(N*T,N*8));preview=Image.new('RGBA',(N*8,N*8))
for r,(dx,dy) in enumerate(dirs):
 frames=build(dx,dy)
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,(i*N,r*N))
 for i,idx in enumerate([4,12,20,31,40,43,47,59]):preview.alpha_composite(frames[idx],(i*N,r*N))
b=io.BytesIO();sheet.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/'LameV6_Ame.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T));preview.save(P/'LameV6-directions.png')
shutil.copy2(BASE/'LameEnPeine_Charge.dir',P/'LameEnPeine_Charge.dir')
z=json.loads((BASE/'bitter_blade-v1-test-only.json').read_text());data=z['Object']['Data'];data['BeforeHits']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'LameV6_Espace','ArgTable':'{}'}}]
data['HitFX']['Delay']=0;data['HitFX']['Sound']='';data['HitFX']['Emitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0};data['HitFX']['ScreenMovement']={'MinShake':0,'MaxShake':0,'MaxShakeTime':0}
(P/'bitter_blade-v6-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2));print('V6 : 9 coups de rémanence, dernier coup spectral tranchant, absorption, 8 directions.')
