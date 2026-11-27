#!/usr/bin/env python3
"""Recalibre uniquement la charge V6 : orbite centrée sur le corps et lueurs sur les lames d'idle."""
from pathlib import Path
from PIL import Image,ImageDraw
import io,struct,math,json
P=Path(__file__).resolve().parent; BASE=P.parent
ns={'__file__':str(BASE/'V3/preparer-v3.py')};exec((BASE/'V3/preparer-v3.py').read_text().split('wisp=clean(')[0],ns)
clean,paste=ns['clean'],ns['paste'];flame=clean(BASE/'Sources/feu-follet-sombre.png',64)
# Origine : pied/point d'émission du sprite 34x38, observé en banc. Axe du corps 13 px plus haut.
# Paires milieu de lame -> pointe, estimées depuis les sprites natifs idle : 5 directions + miroirs.
down=[((-7,-10),(-10,-4)),((7,-10),(10,-4))]
dl=[((-7,-11),(-10,-5)),((6,-10),(6,-4))]
left=[((3,-10),(4,-4))] # l'autre lame est masquée dans la pose de profil
ul=[((-7,-11),(-10,-4)),((5,-12),(7,-7))]
up=[((-7,-10),(-10,-4)),((7,-10),(10,-4))]
def mirror(pairs):return [((-a[0],a[1]),(-b[0],b[1])) for a,b in pairs]
anchors=[down,dl,left,ul,up,mirror(ul),mirror(left),mirror(dl)]
N=96;T=40;sheet=Image.new('RGBA',(N*T,N*8));preview=Image.new('RGBA',(N*8,N*8))
for direction in range(8):
 for t in range(T):
  f=Image.new('RGBA',(N,N));d=ImageDraw.Draw(f)
  env=min(1,t/5,(39-t)/5);pulse=.65+.35*(.5+.5*math.sin(t*.5)); cx,cy=48,35
  # Les quatre positions sont par paires opposées : leur centre géométrique reste exactement sur le corps.
  angle=t*.10
  for j in range(4):
   a=angle+j*math.pi/2;x=cx+math.cos(a)*24;y=cy+math.sin(a)*15
   size=10+2*(.5+.5*math.sin(t*.38+j));paste(f,flame,x,y,size,size*1.15,env*.8)
  for j,(a,b) in enumerate(anchors[direction]):
   ax,ay=48+a[0],48+a[1];bx,by=48+b[0],48+b[1]
   # Lueur filiforme restant sur la lame ; particules qui convergent de son côté vers la pointe.
   if env>0:
    d.line((ax,ay,bx,by),fill=(int(67*env),int(13*env),int(100*env),int(120*env)),width=3)
    d.line((ax,ay,bx,by),fill=(int(158*env*pulse),int(58*env*pulse),int(220*env*pulse),int(185*env)),width=1)
    paste(f,flame,bx,by,6+2*pulse,9+2*pulse,env*(.35+.25*pulse))
    for k in range(2):
     q=((t*.085+k*.5+j*.19)%1);x=ax+(bx-ax)*q+math.sin(t*.25+k)*1.5;y=ay+(by-ay)*q-2*(1-q)
     d.point((round(x),round(y)),fill=(int(200*env),int(145*env),int(255*env),int(230*env)))
  sheet.alpha_composite(f,(t*N,direction*N))
  if t in [4,8,12,16,20,24,30,36]:preview.alpha_composite(f,([4,8,12,16,20,24,30,36].index(t)*N,direction*N))
b=io.BytesIO();sheet.save(b,format='PNG',optimize=True);raw=b.getvalue();(P/'LameV6_ChargeCalibree.dir').write_bytes(struct.pack('<q',len(raw))+raw+struct.pack('<iiii',N,N,4,T));preview.save(P/'Charge-calibree-8-directions.png')
p=P/'bitter_blade-v6-test-only.json';z=json.loads(p.read_text());z['Object']['HitboxAction']['PreActions'][0]['Emitter']['Anim']['Anim']['AnimIndex']='LameV6_ChargeCalibree';p.write_text(json.dumps(z,ensure_ascii=False,indent=2))
print('Charge centrée : 8 directions, 40 images, lueurs orientées par pose, V6 inchangée.')
