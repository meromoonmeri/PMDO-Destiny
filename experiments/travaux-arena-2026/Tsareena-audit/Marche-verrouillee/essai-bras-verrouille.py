from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
p=Path(__file__).parent
for n,donor in [(2,'bras-droite-subtil-original.png'),(4,'avant-droite-bras-04-original.png')]:
 base=Image.open(p/f'avant-droite-{n:02}-retouche.png').convert('RGB');src=Image.open(p/donor).convert('RGB');assert base.size==src.size
 mask=Image.new('L',base.size);d=ImageDraw.Draw(mask)
 d.polygon([(445,513),(480,525),(466,580),(423,627),(370,680),(327,716),(283,729),(264,701),(303,673),(350,629),(405,578)],fill=255)
 d.polygon([(559,516),(589,532),(616,573),(657,601),(703,622),(743,650),(753,704),(726,727),(691,712),(651,688),(611,658),(578,624),(555,570)],fill=255)
 out=Image.composite(src,base,mask);m=np.array(mask)>0;assert np.array_equal(np.array(out)[~m],np.array(base)[~m]);out.save(p/f'avant-droite-{n:02}-bras-essai.png')
