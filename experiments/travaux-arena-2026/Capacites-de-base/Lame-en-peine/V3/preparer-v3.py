#!/usr/bin/env python3
"""Banc V3 : chaque rémanence trace une coupe en perspective, puis verre spatial et absorption."""
from pathlib import Path
from PIL import Image,ImageDraw
import io,struct,math,json,shutil
import numpy as np
P=Path(__file__).resolve().parent;BASE=P.parent;G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny'

def clean(p,n):
 im=Image.open(p).convert('RGB');im.thumbnail((n,n),Image.Resampling.NEAREST);a=np.asarray(im).astype('int16');r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];mask=(g>100)&(g>r+45)&(g>b+45);out=Image.fromarray(np.dstack((a.astype('uint8'),np.where(mask,0,255).astype('uint8'))),'RGBA');return out.crop(out.getbbox())
def paste(c,im,x,y,w,h,alpha=1,flip=False):
 if min(w,h)<1 or alpha<=0:return
 v=im.resize((int(w),int(h)),Image.Resampling.NEAREST)
 if flip:v=v.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 if alpha<1:
  a=np.asarray(v).copy();a[:,:,:3]=(a[:,:,:3].astype('float32')*alpha).astype('uint8');a[:,:,3]=(a[:,:,3].astype('float32')*alpha).astype('uint8');v=Image.fromarray(a,'RGBA')
 c.alpha_composite(v,(round(x-v.width/2),round(y-v.height/2)))
def bank(name,rows):
 dirs=len(rows);T=len(rows[0]);w,h=rows[0][0].size;sheet=Image.new('RGBA',(w*T,h*dirs));preview=Image.new('RGBA',(w*8,h*math.ceil(T/8)))
 for r,frames in enumerate(rows):
  for i,f in enumerate(frames):
   sheet.alpha_composite(f,(i*w,r*h))
   if r==0:preview.alpha_composite(f,((i%8)*w,(i//8)*h))
 b=io.BytesIO();sheet.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/(name+'.dir')).write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',w,h,4 if dirs==8 else 0,T));preview.save(P/(name+'-planche.png'))
def sprites():
 b=(G/'Content/Chara/937.chara').read_bytes();i=b.find(b'\x89PNG\r\n\x1a\n');n=struct.unpack_from('<q',b,i-8)[0];im=Image.open(io.BytesIO(b[i:i+n])).convert('RGBA');w,h,_,_=struct.unpack_from('<iiii',b,i+n);poses=[]
 for row,col in [(2,1),(2,4),(2,7),(3,4),(4,0),(4,3),(5,2),(5,5)]:
  v=im.crop((col*w,row*h,(col+1)*w,(row+1)*h));poses.append(v.crop(v.getbbox()))
 return poses
wisp=clean(BASE/'Sources/feu-follet-sombre.png',64);shards=clean(P/'Sources/eclats-spatiaux.png',145);poses=sprites();N=160
# Vue en perspective d'une surface inclinée : lignes proches plus longues et espacées.
A=(45,26);B=(112,35);C=(7,125);D=(150,136)
def point(u,v):
 return ((1-v)*((1-u)*A[0]+u*B[0])+v*((1-u)*C[0]+u*D[0]),(1-v)*((1-u)*A[1]+u*B[1])+v*((1-u)*C[1]+u*D[1]))
# Neuf gestes : une silhouette, un trajet et une seule entaille liée à chacun.
segments=[]
for u in (.10,.30,.50,.70,.90):segments.append((point(u,.05),point(u,.97)))
for v in (.16,.37,.62,.87):segments.append((point(.02,v),point(.98,v)))
order=[0,5,3,6,1,7,4,8,2];events=[]
for j,k in enumerate(order):
 a,b=segments[k]
 if j%2:a,b=b,a
 events.append((5+j*5,a,b,j))
frames=[]
for t in range(65):
 f=Image.new('RGBA',(N,N))
 # Coup créé en avançant depuis l'apparition, et persistant ensuite dans l'espace.
 for start,a,b,j in events:
  age=t-start
  if age<0:continue
  progress=min(1,(age+1)/5);fade=min(1,max(0,(65-t)/12));end=(a[0]+(b[0]-a[0])*progress,a[1]+(b[1]-a[1])*progress)
  d=ImageDraw.Draw(f);coords=(int(a[0]),int(a[1]),int(end[0]),int(end[1]));d.line(coords,fill=(int(34*fade),int(7*fade),int(45*fade),int(230*fade)),width=5);d.line(coords,fill=(int(122*fade),int(42*fade),int(198*fade),int(240*fade)),width=3);d.line(coords,fill=(int(240*fade),int(213*fade),int(255*fade),int(255*fade)),width=1)
  # La silhouette glisse sur sa propre entaille ; les poses précédentes restent en rémanence.
  if age<10:
   appear=min(1,(age+1)/2,(10-age)/4)
   for lag,opacity in ((3,.16),(2,.25),(0,.75)):
    progress2=max(0,min(1,(age+1-lag)/5));x=a[0]+(b[0]-a[0])*progress2;y=a[1]+(b[1]-a[1])*progress2
    paste(f,poses[j%8],x,y,25,30,appear*opacity,flip=j%2==1)
   paste(f,wisp,end[0],end[1],12,14,appear*.7)
 frames.append(f)
bank('LameV3_Perspective',[frames])
# Direction = direction du lanceur : l'arrivée est exactement sur la case du lanceur.
dirs=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)];rows=[]
for dx,dy in dirs:
 frames=[]
 for t in range(56):
  f=Image.new('RGBA',(N,N));alpha=min(1,(t+1)/5,(56-t)/12)
  # Fracture et éclats transparents ; ce dessin est en plus du pli réel du rendu.
  if t<36:
   progress=min(1,(t+1)/8);fade=min(1,(36-t)/10);size=32+110*progress;paste(f,shards,80,80,size,size,fade*.72)
  # Six feux follets émergent de la fracture puis se dirigent tous vers Malvalame.
  for j in range(6):
   age=t-(4+j*3)
   if not 0<=age<42:continue
   q=min(1,age/35);a=j*math.tau/6;srcx=80+math.cos(a)*38;srcy=80+math.sin(a)*30
   destx=80-24*dx;desty=80-24*dy
   x=srcx+(destx-srcx)*q+math.sin(q*math.pi)*math.cos(a+math.pi/2)*7
   y=srcy+(desty-srcy)*q+math.sin(q*math.pi)*math.sin(a+math.pi/2)*7
   fade=min(1,(age+1)/4,(42-age)/8);sz=14*(1-.65*q)
   paste(f,wisp,x,y,sz,sz*1.15,fade*.95)
  frames.append(f)
 rows.append(frames)
bank('LameV3_VerreFeux',rows);shutil.copy2(BASE/'LameEnPeine_Charge.dir',P/'LameEnPeine_Charge.dir')
z=json.loads((BASE/'bitter_blade-v1-test-only.json').read_text());o=z['Object'];data=o['Data'];data['BeforeHits']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'LameV3_Espace','ArgTable':'{}'}}];data['HitFX']['Delay']=0;data['HitFX']['Sound']='';data['HitFX']['Emitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0};data['HitFX']['ScreenMovement']={'MinShake':0,'MaxShake':0,'MaxShakeTime':0};(P/'bitter_blade-v3-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
print('65 images synchronisées : 9 rémanences pour 9 slashs en perspective ; 56 images de verre et absorption, 8 directions.')
