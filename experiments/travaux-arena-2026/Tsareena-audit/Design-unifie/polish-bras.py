from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np
p=Path(__file__).parent;src=Image.open(p/'polish-bras-face-02-original.png').convert('RGB');base=Image.open(p/'face-marche-02-retouche.png').convert('RGB');assert src.size==base.size
mask=Image.new('L',base.size);d=ImageDraw.Draw(mask)
d.polygon([(315,525),(349,531),(344,566),(307,597),(265,631),(233,665),(209,701),(159,711),(138,684),(166,660),(214,627),(268,576)],fill=255)
d.polygon([(433,528),(460,528),(482,561),(529,595),(572,625),(620,657),(642,685),(629,705),(592,706),(555,673),(514,641),(474,612),(437,576)],fill=255)
out=Image.composite(src,base,mask);m=np.asarray(mask)>0;assert np.array_equal(np.asarray(out)[~m],np.asarray(base)[~m]);out.save(p/'face-marche-02-bras-essai.png')
src=Image.open(p/'polish-bras-dos-02-original.png').convert('RGB');base=Image.open(p/'walk-dos-02-retouche.png').convert('RGB');assert src.size==base.size
mask=Image.new('L',base.size);d=ImageDraw.Draw(mask)
d.polygon([(370,505),(398,510),(402,555),(383,588),(364,624),(335,660),(302,692),(280,690),(285,656),(316,616),(346,578)],fill=255)
d.polygon([(512,505),(540,510),(550,570),(580,610),(610,640),(641,674),(630,700),(604,699),(575,672),(546,642),(525,606),(513,562)],fill=255)
out=Image.composite(src,base,mask);m=np.asarray(mask)>0;assert np.array_equal(np.asarray(out)[~m],np.asarray(base)[~m]);out.save(p/'dos-marche-02-bras-essai.png')
