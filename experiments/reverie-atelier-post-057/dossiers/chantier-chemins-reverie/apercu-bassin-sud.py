from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import numpy as np,gzip,ijson,json
R=Path('.'); x1,y1,x2,y2=190,1940,420,2160; box=(x1,y1,x2,y2);L=[Image.open(p).convert('RGBA').crop(box) for p in sorted((R/'calques-publies-png').glob('*.png'))]; assert len(L)==11
# Proposition graphique uniquement, couleurs prélevées sur les rives et eau Réverie.
water=Image.new('RGBA',(x2-x1,y2-y1));d=ImageDraw.Draw(water)
def poly(points,fill):d.polygon([(x-x1,y-y1) for x,y in points],fill=fill)
# Bordure pixel-art de petit bassin, légèrement décalée à droite de la maison.
poly([(290,2037),(354,2037),(365,2040),(374,2046),(376,2053),(372,2059),(360,2062),(341,2063),(320,2062),(303,2060),(292,2056),(287,2050)],(80,128,184,255))
poly([(294,2039),(352,2039),(363,2042),(371,2047),(372,2053),(368,2057),(358,2059),(340,2060),(320,2059),(305,2057),(296,2054),(291,2049)],(128,216,224,255))
# Quelques reflets discrets issus de la palette de la carte.
for p in [(343,2051),(355,2056),(328,2057)]:
 x,y=p;d.line((x-x1,y-y1,x-x1+3,y-y1),fill=(189,239,239,255),width=1)
def compose(add):
 img=Image.new('RGBA',L[0].size)
 for i,layer in enumerate(L):
  img.alpha_composite(layer)
  if i==2 and add:img.alpha_composite(water)
 return img
before=compose(False);after=compose(True);can=Image.new('RGB',(1500,840),'#1c2624');d=ImageDraw.Draw(can);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);d.text((20,12),'Bassin sud — proposition visuelle uniquement',font=f,fill='white');d.text((20,42),'Maison et décors conservés devant le bassin ; collisions et accès à vérifier avant intégration.',font=small,fill='#d1dacf')
for x,label,im in [(20,'AVANT',before),(770,'PROPOSITION',after)]:
 d.text((x,70),label,font=f,fill='#ffce79');can.paste(im.convert('RGB').resize((690,660),Image.Resampling.NEAREST),(x,105))
can.save('apercu-bassin-sud-avant-apres.png');water.save('proposition-bassin-sud-composite-seul.png')
# Diagnostic d'emprise : compter les cellules terrain sous le dessin, sans les modifier.
m=np.array(water)[:,:,3]>0; coords={(int((x+x1)//8),int((y+y1)//8)) for y,x in np.argwhere(m)};par_carte={}
for p in sorted((R/'base/payload').glob('*.gz')):
 with gzip.open(p,'rb') as fi:
  if fi.read(3)!=b'\xef\xbb\xbf':fi.seek(0)
  cols=list(ijson.items(fi,'Object.obstacles.item'))
 blocked=sum(cols[x][y]['Tags']!=0 for x,y in coords);par_carte[p.name]={'deja_bloquees':blocked,'non_bloquees':len(coords)-blocked}
data={'emprise_boite':[287,2037,377,2064],'cases_touchees':len(coords),'cartes':par_carte,'interpretation':'Le bassin n est pas installé. Cases terrain contenant au moins un pixel du dessin, obstacles.Tags non nul : indicateur statique seulement. Ni cheminement, ni objets/PNJ, ni moteur testés. Certaines cases libres seraient concernées dans les cartes résidentielles.'}
(R/'bassin-sud-diagnostic-preliminaire.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(data)
