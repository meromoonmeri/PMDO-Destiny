from PIL import Image,ImageDraw
import numpy as np
from pathlib import Path
p=Path(__file__).parent;src=p.parent/'Huit-directions/avant-gauche.png';a=Image.open(src).convert('RGB');
for f,n in [(2,'pas-gauche-02-brut.png'),(4,'pas-gauche-04-v2-brut.png')]:
 b=Image.open(p/n).convert('RGB')
 if b.size==(a.width,a.height-4):
  canvas=Image.new('RGB',a.size,b.getpixel((0,0)));canvas.paste(b,(0,0));b=canvas
 assert b.size==a.size
 mask=Image.new('L',a.size);d=ImageDraw.Draw(mask);d.polygon([(295,755),(540,755),(570,805),(605,895),(605,1005),(565,1065),(310,1065),(300,1000),(278,900)],fill=255)
 z=Image.composite(b,a,mask);z.save(p/f'pas-gauche-{f:02}-retouche.png');mask.save(p/f'masque-{f:02}.png');x=np.asarray(a);y=np.asarray(z);m=np.asarray(mask)>0;assert not np.any(x[~m]!=y[~m]);print(f,'outside differences 0')
