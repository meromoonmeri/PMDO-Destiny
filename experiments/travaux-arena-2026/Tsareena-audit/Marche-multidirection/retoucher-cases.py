from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import numpy as np
p=Path(__file__).parent

def replace(base,gen,out,region):
 a=Image.open(p/base).convert('RGB');b=Image.open(p/gen).convert('RGB'); assert a.size==b.size
 mask=Image.new('L',a.size,0);ImageDraw.Draw(mask).rectangle(region,fill=255);z=Image.composite(b,a,mask);z.save(p/out)
 aa=np.asarray(a);zz=np.asarray(z);mm=np.asarray(mask)>0;assert np.all(aa[~mm]==zz[~mm]);print(out,'modification hors region 0')
replace('face-v2-original.png','face-02-brut.png','face-02-retouche.png',(625,488,780,636))
a=Image.open(p/'face-02-retouche.png').convert('RGB');b=Image.open(p/'face-v2-original.png').convert('RGB');region=(625,488,780,636);b.paste(ImageOps.mirror(a.crop(region)),region[:2]);b.save(p/'face-04-retouche.png')
for n in [2,4]:replace('profil-droite-v2-original.png',f'profil-droite-0{n}-brut.png',f'profil-droite-0{n}-retouche.png',(400,850,660,1130))
replace('arriere-gauche-v2-original.png','arriere-gauche-04-brut.png','arriere-gauche-02-retouche.png',(255,920,610,1130))
# opposite step derived from the first frame in the same small leg region, keeping the entire robe unchanged
base=Image.open(p/'arriere-gauche-v2-original.png').convert('RGB'); reg=(300,925,605,1125);base.paste(ImageOps.mirror(base.crop(reg)),reg[:2]);ImageDraw.Draw(base).rectangle((500,912,570,924),fill=(0,0,0));base.save(p/'arriere-gauche-04-retouche.png')
for n in [2,4]:
 gen='dos-02-brut.png' if n==2 else 'dos-04-v2-brut.png'
 replace('dos-01-original.png',gen,f'dos-0{n}-retouche.png',(340,960,550,1130))
