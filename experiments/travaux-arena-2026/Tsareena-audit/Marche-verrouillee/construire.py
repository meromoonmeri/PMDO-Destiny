from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
p=Path(__file__).parent;r=p.parent
sources={
 'droite':(r/'revision-corpulence/repos-trois-quart-01.png',p/'avant-droite-02-brut.png',r/'Sprite-Mega-approuve/avant-droite-04-original.png',[(408,790),(650,790),(660,860),(660,1120),(395,1120),(395,870)]),
 'gauche':(r/'Huit-directions/avant-gauche.png',p/'avant-gauche-02-brut.png',p/'avant-gauche-04-brut.png',[(306,762),(532,762),(550,830),(550,1070),(302,1070),(302,840)])}
sheet=Image.new('RGBA',(256,896))
for name,(fbase,f2,f4,polygon) in sources.items():
 base=Image.open(fbase).convert('RGB');mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon(polygon,fill=255)
 variants=[]
 for i,path in [(2,f2),(4,f4)]:
  donor=Image.open(path).convert('RGB')
  if donor.size!=base.size: raise ValueError(f'Canvas mismatch {path.name}: {donor.size} vs {base.size}')
  out=Image.composite(donor,base,mask);out.save(p/f'avant-{name}-{i:02}-retouche.png')
  m=np.asarray(mask)>0;assert np.array_equal(np.asarray(out)[~m],np.asarray(base)[~m])
  variants.append(out)
 def rgba(im):
  a=np.asarray(im);v=a.astype(int);dist=np.sqrt(((v-v[0,0])**2).sum(2));return Image.fromarray(np.dstack([a,((dist>38)|(v[:,:,2]<150)).astype('uint8')*255]),'RGBA')
 # fixed crop and scale: identical framing for all poses, as required by the locked design
 frames=[rgba(x) for x in (base,variants[0],base,variants[1])];boxes=[x.getbbox() for x in frames];bbox=(min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes));sw=bbox[2]-bbox[0];sh=bbox[3]-bbox[1];s=min(54/sw,64/sh);size=(round(sw*s),round(sh*s));row={'droite':1,'gauche':7}[name]
 for col,im in enumerate(frames):
  c=im.crop(bbox).resize(size,Image.Resampling.NEAREST);sheet.alpha_composite(c,(col*64+(64-size[0])//2,row*112+70-size[1]))
 print(name,'cadrage commun',bbox,size,'pixels hors jambes inchangés')
sheet.save(p/'Walk-Mega-verrouille-PARTIEL.png')
