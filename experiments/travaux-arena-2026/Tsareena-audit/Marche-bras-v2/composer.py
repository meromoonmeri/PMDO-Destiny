from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
p=Path(__file__).parent
base=Image.open(p.parent/'Design-unifie/diag-droite-04-retouche.png').convert('RGB');src=Image.open(p/'avant-droite-04-original.png').convert('RGB');assert src.size==base.size
mask=Image.new('L',base.size);d=ImageDraw.Draw(mask)
d.rectangle((245,515,480,745),fill=255)
out=Image.composite(src,base,mask);m=np.asarray(mask)>0; assert np.array_equal(np.asarray(out)[~m],np.asarray(base)[~m]);out.save(p/'avant-droite-04-retouche.png')
base=Image.open(p.parent/'Design-unifie/diag-gauche-02-retouche.png').convert('RGB');src=Image.open(p/'avant-gauche-02-original.png').convert('RGB');assert src.size==base.size
mask=Image.new('L',base.size);d=ImageDraw.Draw(mask);d.rectangle((470,510,668,720),fill=255)
out=Image.composite(src,base,mask);m=np.asarray(mask)>0;assert np.array_equal(np.asarray(out)[~m],np.asarray(base)[~m]);out.save(p/'avant-gauche-02-retouche.png')
