#!/usr/bin/env python3
"""Prototype VFX Turbo-Charge : 8 rangées distinctes, 24 poses, non jouable.
L'effet est une étude PMD, pas une copie certifiée de l'animation officielle.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, io, struct
import numpy as np
P=Path(__file__).resolve().parent.parent/'Prototypes'/'Turbo-Charge-Bulldozer'
P.mkdir(parents=True,exist_ok=True)
SIZE=96; FRAMES=24
# Ordre indicatif des rangées PMD, à confirmer par le moteur pour les VFX Dir8.
dirs=[('bas',0,1),('bas-gauche',-1,1),('gauche',-1,0),('haut-gauche',-1,-1),('haut',0,-1),('haut-droite',1,-1),('droite',1,0),('bas-droite',1,1)]
atlas=Image.new('RGBA',(SIZE*FRAMES,SIZE*8))
for row,(_,dx,dy) in enumerate(dirs):
 length=math.hypot(dx,dy); ux,uy=dx/length,dy/length;vx,vy=-uy,ux
 for f in range(FRAMES):
  im=Image.new('RGBA',(SIZE,SIZE));d=ImageDraw.Draw(im);cx=cy=48
  def at(a,b): return (round(cx+a*ux+b*vx),round(cy+a*uy+b*vy))
  if f<8:
   # anneaux de charge rentrants, centre transparent pour le sprite joueur
   r=30-f*1.7; a=round(160+f*10)
   d.ellipse((cx-r,cy-r*.45,cx+r,cy+r*.45),outline=(255,210,103,a),width=1)
   for i in range(8):
    t=i*math.tau/8+f*.17; x=round(cx+math.cos(t)*r); y=round(cy+math.sin(t)*r*.45)
    d.rectangle((x-1,y-1,x+1,y+1),fill=(255,244,175,220))
  if 6<=f<20:
   fade=min(1,(f-6)/2,(20-f)/4); reach=min(32,5+(f-6)*3)
   # rubans de vitesse orientés selon la cible ; pas de sprite Pokémon dessiné
   for b in (-15,-9,9,15):
    start=at(-25,b);end=at(reach,b*.62)
    d.line((start,end),fill=(255,188,77,round(135*fade)),width=2)
   for b in (-7,7):
    d.line((at(-26,b),at(reach,b*.45)),fill=(255,246,206,round(230*fade)),width=2)
   # pointe en avant, distincte de l'impact radial
   tip=at(reach+6,0);left=at(reach-5,-8);right=at(reach-5,8)
   d.line((left,tip,right),fill=(255,235,167,round(220*fade)),width=2)
  if 14<=f<23:
   r=2+(f-14)*2.1;alpha=round(220*(23-f)/9); x,y=at(29,0)
   d.ellipse((x-r,y-r,x+r,y+r),outline=(255,243,186,alpha),width=2)
   for k in range(8):
    a=k*math.tau/8; sx=round(x+math.cos(a)*r*1.3);sy=round(y+math.sin(a)*r*1.3)
    d.line((sx-1,sy,sx+1,sy),fill=(255,202,104,alpha));d.line((sx,sy-1,sx,sy+1),fill=(255,202,104,alpha))
  atlas.alpha_composite(im,(f*SIZE,row*SIZE))
atlas.save(P/'Turbo_Charge_Z.Dir8.png')
a=np.array(atlas);alpha=a[:,:,3].astype(np.uint16);a[:,:,:3]=((a[:,:,:3].astype(np.uint16)*alpha[:,:,None]+127)//255).astype(np.uint8)
b=io.BytesIO();Image.fromarray(a).save(b,format='PNG');png=b.getvalue()
(P/'Turbo_Charge_Z.dir').write_bytes(struct.pack('<q',len(png))+png+struct.pack('<iiii',SIZE,SIZE,4,FRAMES))
(P/'NOTES.md').write_text('# Turbo-Charge Bulldozer — prototype\n\nVFX de charge, vitesse et impact ; 24 poses, huit rangées. Sans sprite Pokémon incrusté. Ordre des rangées et rendu en moteur à vérifier avant toute intégration. Ce n’est pas une capacité jouable ni une animation validée.\n',encoding='utf-8')
print('Prototype:',P)
