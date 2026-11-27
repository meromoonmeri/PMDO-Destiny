from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np
p=Path(__file__).parent;base=Image.open(p/'reprise-dos-brut.png').convert('RGB');mask=Image.new('L',base.size);ImageDraw.Draw(mask).rectangle((335,935,565,1135),fill=255)
for n in [2,4]:
 f=p/('walk-dos-02-v2-original.png' if n==2 else 'walk-dos-04-original.png');d=Image.open(f).convert('RGB');assert d.size==base.size
 out=Image.composite(d,base,mask);m=np.asarray(mask)>0;assert np.array_equal(np.asarray(base)[~m],np.asarray(out)[~m]);out.save(p/f'walk-dos-{n:02}-retouche.png')
