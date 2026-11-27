#!/usr/bin/env python3
"""Turbo-Charge v3 : dessine indépendamment chaque pose pour PMDO.
Géométrie pixel par pixel ; phases de charge au sol et d'impact.
Les vues partagent un vocabulaire, mais direction et perspective sont recalculées.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math,struct,io,json
import numpy as np
P=Path(__file__).resolve().parent.parent/'Prototypes'/'Turbo-Charge-Bulldozer'/'V3-native';P.mkdir(parents=True,exist_ok=True)
S=96
D=[('bas',0,1),('bas-gauche',-1,1),('gauche',-1,0),('haut-gauche',-1,-1),('haut',0,-1),('haut-droite',1,-1),('droite',1,0),('bas-droite',1,1)]
C=[(154,77,19,255),(229,148,32,255),(255,202,72,255),(255,238,148,255),(255,255,221,255)]
def star(d,x,y,r,col):
 d.line((x-r,y,x+r,y),fill=col,width=1);d.line((x,y-r,x,y+r),fill=col,width=1)
def save(sheet,name,n):
 sheet.save(P/(name+'.Dir8.png'));arr=np.array(sheet);a=arr[:,:,3].astype(np.uint16);arr[:,:,:3]=((arr[:,:,:3].astype(np.uint16)*a[:,:,None]+127)//255).astype(np.uint8);b=io.BytesIO();Image.fromarray(arr).save(b,format='PNG');z=b.getvalue()
 (P/(name+'.dir')).write_bytes(struct.pack('<q',len(z))+z+struct.pack('<iiii',S,S,4,n))
def charge(n=18):
 back=Image.new('RGBA',(S*n,S*8));front=Image.new('RGBA',(S*n,S*8))
 for row,(_,dx,dy) in enumerate(D):
  for t in range(n):
   b=Image.new('RGBA',(S,S));f=Image.new('RGBA',(S,S));bd=ImageDraw.Draw(b);fd=ImageDraw.Draw(f)
   # Anneaux plats : la perspective reste horizontale quelle que soit la direction.
   radius=round(29-1.05*t);yb=48; a=max(0,min(255,int(min(1,(t+1)/3,(n-t)/4)*255)))
   bd.ellipse((48-radius,yb-radius//3,48+radius,yb+radius//3),outline=(*C[2][:3],a),width=2)
   if t>4:
    r=max(7,radius-7);bd.ellipse((48-r,yb-r//3,48+r,yb+r//3),outline=(*C[3][:3],a),width=1)
   for j in range(7):
    theta=j*math.tau/7+t*.32;r=max(12,31-t)
    x=round(48+math.cos(theta)*r);y=round(47+math.sin(theta)*r*.4-((t+j)%5))
    star(fd,x,y,1+(j+t)%3,(*C[3][:3],a))
   # étincelles se rapprochant de l'axe de charge, angle indépendant par vue
   for j in range(3):
    side=j-1;dist=max(6,26-t);x=round(48-dx*dist-dy*side*9);y=round(45-dy*dist+dx*side*7)
    bd.line((x-dx*5,y-dy*5,x,y),fill=(*C[2][:3],a),width=1)
   back.alpha_composite(b,(t*S,row*S));front.alpha_composite(f,(t*S,row*S))
 return back,front
def impact(n=18):
 back=Image.new('RGBA',(S*n,S*8));front=Image.new('RGBA',(S*n,S*8))
 for row,(_,dx,dy) in enumerate(D):
  for t in range(n):
   b=Image.new('RGBA',(S,S));f=Image.new('RGBA',(S,S));bd=ImageDraw.Draw(b);fd=ImageDraw.Draw(f)
   r=round(min(33,4+t*3.1));a=int(255*min(1,(n-t)/6))
   if t<12:
    bd.ellipse((48-r,48-int(r*.55),48+r,48+int(r*.55)),outline=(*C[1][:3],a),width=2)
    if r>7:bd.ellipse((48-r+4,48-int(r*.55)+3,48+r-4,48+int(r*.55)-3),outline=(*C[2][:3],a),width=1)
   if t<6:
    k=max(2,15-t*2); pts=[(48,48-k*2),(48+k//3,48-k//3),(48+k*2,48),(48+k//3,48+k//3),(48,48+k*2),(48-k//3,48+k//3),(48-k*2,48),(48-k//3,48-k//3)]
    fd.polygon(pts,fill=(*C[3][:3],a));fd.ellipse((44,44,52,52),fill=(*C[4][:3],a))
   for j in range(10):
    ang=j*math.tau/10;rr=8+t*2.1; px=round(48+math.cos(ang)*rr+dx*t*.3);py=round(48+math.sin(ang)*rr*.65+dy*t*.3)
    if 2<=px<S-2 and 2<=py<S-2:star(fd,px,py,max(1,3-t//6),(*C[2+j%2][:3],a))
   for j in [-1,0,1]:
    offset=j*7;dist=10+t*1.7;x=round(48+dx*dist-dy*offset);y=round(48+dy*dist+dx*offset*.7)
    ex=round(x+dx*max(1,10-t//2));ey=round(y+dy*max(1,10-t//2));fd.line((x,y,ex,ey),fill=(*C[3][:3],a),width=2)
   back.alpha_composite(b,(t*S,row*S));front.alpha_composite(f,(t*S,row*S))
 return back,front
for key, pair in [('Charge',charge()),('Impact',impact())]:
 for side,im in zip(['Arriere','Avant'],pair):save(im,'Turbo_V3_'+key+'_'+side,18)
(P/'manifest.json').write_text(json.dumps({'poses_par_phase':18,'direction_order':[x[0] for x in D],'canvas':S,'ticks_per_frame':2,'generation':'chaque pose est dessinée par algorithme avec ses paramètres propres ; pas une génération IA indépendante image par image','status':'prototype'},ensure_ascii=False,indent=2))
print('OK 18 poses charge et 18 impact, deux calques, 8 directions')
