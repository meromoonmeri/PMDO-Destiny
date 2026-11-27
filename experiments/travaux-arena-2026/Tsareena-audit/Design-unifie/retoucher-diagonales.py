from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np
p=Path(__file__).parent;r=p.parent
sets=[('droite',r/'revision-corpulence/repos-trois-quart-01.png',p/'diag-droite-02-v3-original.png',r/'Sprite-Mega-approuve/avant-droite-04-original.png',[(408,790),(650,790),(660,860),(660,1130),(395,1130),(395,870)]),('gauche',r/'Huit-directions/avant-gauche.png',p/'diag-gauche-02-v3-original.png',r/'Marche-verrouillee/avant-gauche-04-brut.png',[(306,762),(532,762),(550,830),(550,1080),(302,1080),(302,840)])]
for d,basepath,a,b,poly in sets:
 base=Image.open(basepath).convert('RGB');mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon(poly,fill=255)
 for col,f in [(2,a),(4,b)]:
  donor=Image.open(f).convert('RGB');assert donor.size==base.size
  result=Image.composite(donor,base,mask);m=np.asarray(mask)>0;assert np.array_equal(np.asarray(result)[~m],np.asarray(base)[~m]);result.save(p/f'diag-{d}-{col:02}-retouche.png')
