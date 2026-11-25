import ijson,gzip,json,collections
from pathlib import Path
from PIL import Image
import numpy as np
im=np.array(Image.open('reverie-0.5.0-rendu-phase0.png').convert('RGBA'));j=json.load(open('trous-alpha-candidats.json'));coords=set()
for x,y,w,h,n,rock in j:
 if (x,y) in [(1118,1702),(1048,1720),(1591,807)]:continue
 for yy in range(y,y+h):
  for xx in range(x,x+w):
   if im[yy,xx,3]==0:coords.add((xx//8,yy//8))
print('cases candidates',len(coords),flush=True);bad=collections.defaultdict(list)
for p in sorted(Path('base/payload').glob('*.gz')):
 with gzip.open(p,'rb') as f:
  if f.read(3)!=b'\xef\xbb\xbf':f.seek(0)
  for li,l in enumerate(ijson.items(f,'Object.Layers.item')):
   for cx,cy in coords:
    for a in l['Tiles'][cx][cy].get('Layers',[]):
     if len(a.get('Frames',[]))>1:bad[f'{cx},{cy}'].append([p.name,l['Name']])
print('cases animées à exclure',len(bad),bad,flush=True);json.dump({'cases':sorted([list(p) for p in coords]),'cases_animees':bad},open('trous-cases-securite.json','w'),indent=2)
