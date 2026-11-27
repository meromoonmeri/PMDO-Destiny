from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
p=Path(__file__).parent;base=Image.open(p/'face-reprise-v2.png').convert('RGB')
mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon([(265,805),(520,805),(540,860),(540,1240),(250,1240),(250,860)],fill=255)
for i,name in [(2,'face-marche-02-v2-brut.png'),(4,'face-marche-04-brut.png')]:
 donor=Image.open(p/name).convert('RGB');assert donor.size==base.size
 out=Image.composite(donor,base,mask);m=np.array(mask)>0;assert np.array_equal(np.array(out)[~m],np.array(base)[~m]);out.save(p/f'face-marche-{i:02}-retouche.png')
