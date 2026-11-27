from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
p=Path(__file__).parent;r=p.parent/'Design-unifie'
settings=[('profil-gauche',r/'profil-gauche-reprise-v2.png',[(2,p/'profil-gauche-02-original.png'),(4,p/'profil-gauche-04-v2-original.png')],[(340,770),(530,770),(550,830),(550,1085),(330,1085),(330,830)]),('arriere-droite',r/'arriere-droite-reprise-v3.png',[(2,p/'arriere-droite-02-original.png'),(4,p/'arriere-droite-04-v2-original.png')],[(395,945),(640,945),(650,1128),(390,1128)])]
for name,basepath,variants,poly in settings:
 base=Image.open(basepath).convert('RGB');mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon(poly,fill=255)
 for col,src in variants:
  donor=Image.open(src).convert('RGB');assert donor.size==base.size
  out=Image.composite(donor,base,mask);m=np.asarray(mask)>0;assert np.array_equal(np.asarray(out)[~m],np.asarray(base)[~m]);out.save(p/f'{name}-{col:02}-retouche.png')
more=[('profil-droite',r/'profil-droite-reprise-v2.png',[(2,p/'profil-droite-02-original.png'),(4,p/'profil-droite-04-original.png')],[(450,810),(670,810),(670,1130),(450,1130)]),('arriere-gauche',r/'arriere-gauche-reprise-v5.png',[(2,p/'arriere-gauche-02-original.png'),(4,p/'arriere-gauche-04-original.png')],[(270,940),(560,940),(560,1130),(270,1130)])]
for name,basepath,variants,poly in more:
 base=Image.open(basepath).convert('RGB');mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon(poly,fill=255)
 for col,src in variants:
  donor=Image.open(src).convert('RGB');assert donor.size==base.size
  out=Image.composite(donor,base,mask);m=np.asarray(mask)>0;assert np.array_equal(np.asarray(out)[~m],np.asarray(base)[~m]);out.save(p/f'{name}-{col:02}-retouche.png')
