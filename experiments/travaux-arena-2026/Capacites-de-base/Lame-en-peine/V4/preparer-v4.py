#!/usr/bin/env python3
"""Animation ininterrompue : chaque coupe devient un bord de fragments, puis des braises reviennent."""
from pathlib import Path
from PIL import Image, ImageDraw
import io, struct, math, json, shutil, importlib.util
P=Path(__file__).resolve().parent; BASE=P.parent
# Reprend les routines de chargement PMDO et les sprites natifs de la V3.
spec=importlib.util.spec_from_file_location('v3',BASE/'V3/preparer-v3.py')
# Ne pas exécuter le générateur V3 ; extraire seulement ses fonctions.
source=(BASE/'V3/preparer-v3.py').read_text().split('wisp=clean(')[0]
ns={'__file__':str(BASE/'V3/preparer-v3.py')};exec(source,ns)
clean,paste,poses=ns['clean'],ns['paste'],ns['sprites']()
wisp=clean(BASE/'Sources/feu-follet-sombre.png',64)
N=160;T=80 # largeur 12 800 pixels, compatible avec la limite de texture courante
A=(45,26);B=(112,35);C=(7,125);D=(150,136)
def p(u,v):return ((1-v)*((1-u)*A[0]+u*B[0])+v*((1-u)*C[0]+u*D[0]),(1-v)*((1-u)*A[1]+u*B[1])+v*((1-u)*C[1]+u*D[1]))
us=[.10,.30,.50,.70,.90]; vs=[.16,.37,.62,.87]
segments=[(p(u,vs[0]),p(u,vs[-1])) for u in us]+[(p(us[0],v),p(us[-1],v)) for v in vs]
order=[0,5,3,6,1,7,4,8,2]; events=[]
for j,k in enumerate(order):
 a,b=segments[k]
 if j%2:a,b=b,a
 events.append((4+j*5,a,b,j))
def mix(a,b,t):return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def line(d, pts, alpha=1, wid=1):
 pts=[(round(x),round(y)) for x,y in pts]
 if alpha<=0:return
 d.line(pts, fill=(int(92*alpha),int(28*alpha),int(143*alpha),int(230*alpha)),width=wid+2,joint='curve')
 d.line(pts, fill=(int(225*alpha),int(185*alpha),int(255*alpha),int(255*alpha)),width=wid,joint='curve')
def generate(dx,dy):
 out=[]
 for frame in range(T):
  t=frame*136/T
  f=Image.new('RGBA',(N,N)); d=ImageDraw.Draw(f)
  if t<64:
   for start,a,b,j in events:
    age=t-start
    if age<0:continue
    q=ease((age+1)/5); end=mix(a,b,q)
    pulse=0.85+0.15*math.sin(t*.23+j)
    line(d,[a,end],pulse,1)
    if age<11:
     appear=min(1,(age+1)/2,(11-age)/4)
     for lag,opacity in ((3,.14),(2,.25),(0,.8)):
      z=ease((age+1-lag)/5);x,y=mix(a,b,z)
      paste(f,poses[j%8],x,y,23,28,appear*opacity,flip=j%2==1)
  else:
   # Les contours des carreaux sont exactement les entailles de l'image précédente.
   q=ease((t-64)/30); fade=1-ease((t-91)/26)
   for iy in range(3):
    for ix in range(4):
     corners=[p(us[ix],vs[iy]),p(us[ix+1],vs[iy]),p(us[ix+1],vs[iy+1]),p(us[ix],vs[iy+1])]
     mx=sum(x for x,y in corners)/4;my=sum(y for x,y in corners)/4
     angle=q*((ix-1.5)*.045+(iy-1)*.07);scale=1-.22*q
     ox=(mx-80)*q*.17;oy=(my-80)*q*.17
     poly=[]
     for x,y in corners:
      x-=mx;y-=my
      poly.append((mx+ox+scale*(x*math.cos(angle)-y*math.sin(angle)),my+oy+scale*(x*math.sin(angle)+y*math.cos(angle))))
     line(d,poly+[poly[0]],fade*(.85+.15*math.sin(t*.26+ix)),1)
     # Fissures fines issues des bords existants, pas de texture de verre plaquée.
     crack=ease((t-68-(ix+iy)%4)/9)
     if crack>0 and fade>0:
      a=mix(poly[0],poly[1],.44); b=mix(poly[2],poly[3],.58);mid=mix(a,b,.5)
      mid=(mid[0]+(ix%2*2-1)*2,mid[1]+(iy%2*2-1)*2)
      if crack<.5: pts=[a,mix(a,mid,crack*2)]
      else:pts=[a,mid,mix(mid,b,(crack-.5)*2)]
      d.line([(round(x),round(y)) for x,y in pts], fill=(int(150*fade),int(100*fade),int(210*fade),int(180*fade)),width=1)
   # Les six feux apparaissent dans les fissures, avant la disparition des fragments.
   for j in range(6):
    age=t-(76+3*j)
    if not 0<=age<49:continue
    q=ease(age/39);a=j*math.tau/6+.25;src=(80+math.cos(a)*31,80+math.sin(a)*25);dest=(80-24*dx,80-24*dy)
    x=src[0]+(dest[0]-src[0])*q+math.sin(q*math.pi)*math.cos(a+math.pi/2)*5
    y=src[1]+(dest[1]-src[1])*q+math.sin(q*math.pi)*math.sin(a+math.pi/2)*5
    alpha=min(1,(age+1)/5,(49-age)/8);size=11*(1-.50*q)
    paste(f,wisp,x,y,size,size*1.1,alpha)
  out.append(f)
 return out
# Convention des rangées directionnelles de PMDO : bas, bas-gauche, gauche, haut-gauche, haut, haut-droite, droite, bas-droite.
dirs=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]
sheet=Image.new('RGBA',(N*T,N*8)); preview=Image.new('RGBA',(N*8,N*math.ceil(T/8)))
for r,(dx,dy) in enumerate(dirs):
 for i,frame in enumerate(generate(dx,dy)):
  sheet.alpha_composite(frame,(i*N,r*N))
  if r==0:preview.alpha_composite(frame,((i%8)*N,(i//8)*N))
b=io.BytesIO();sheet.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/'LameV4_Continu.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T));preview.save(P/'LameV4_Continu-planche.png')
shutil.copy2(BASE/'LameEnPeine_Charge.dir',P/'LameEnPeine_Charge.dir')
z=json.loads((BASE/'bitter_blade-v1-test-only.json').read_text());data=z['Object']['Data']
data['BeforeHits']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'LameV4_Espace','ArgTable':'{}'}}]
data['HitFX']['Delay']=0;data['HitFX']['Sound']='';data['HitFX']['Emitter']={'$type':'RogueEssence.Content.EmptyFiniteEmitter, RogueEssence','LocHeight':0};data['HitFX']['ScreenMovement']={'MinShake':0,'MaxShake':0,'MaxShakeTime':0}
(P/'bitter_blade-v4-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
print('V4 : 80 images continues, 8 directions, 9 entailles, fragments issus des entailles.')
