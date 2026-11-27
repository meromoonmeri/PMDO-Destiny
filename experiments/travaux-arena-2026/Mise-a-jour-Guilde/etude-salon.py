import io,struct,json,base64
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).parent;src=root/'sources';html=(src/'docs/atelier-destiny/Guilde/Guilde-Destiny-Bourgeons-PMD.html').read_text();d=json.loads(html.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);r=next(x for x in d['rooms'] if x['id']=='guilde_destiny_grand_salon');q=d['balade_nuit'].get('ronces',{}).get(r['id'],d['lianes'][r['id']]);out=root/'etude-salon';out.mkdir(exist_ok=True)
def decode(u):return Image.open(io.BytesIO(base64.b64decode(u.split(',')[-1]))).convert('RGBA')
for k in ('s','t'):decode(q[k]).save(out/('verdure-'+k+'.png'))
decode(r['base']).save(out/'fond-apercu-base.png')
def tilebank(name):
 b=(src/f'game/Content/Tile/{name}.tile').read_bytes();sz,n=struct.unpack_from('<ii',b);assert sz==8;out={}
 for i in range(n):
  x,y,off=struct.unpack_from('<iiq',b,8+16*i);z=struct.unpack_from('<q',b,off)[0];a=np.array(Image.open(io.BytesIO(b[off+8:off+8+z])).convert('RGBA'));v=a[...,3].astype(float);m=v>0
  for c in range(3):a[...,c][m]=np.minimum(255,np.rint(a[...,c][m].astype(float)*255/v[m])).astype('uint8')
  out[x,y]=Image.fromarray(a)
 return out
banks={n:tilebank(n) for n in ['Destiny_Guilde_Grand_Salon','Destiny_Guilde_Verdure']}
o=json.loads((src/'game/Data/Ground/guilde_destiny_grand_salon.rsground').read_text())['Object'];layers=o['Layers'];w,h=len(layers[0]['Tiles']),len(layers[0]['Tiles'][0]);assert (w*8,h*8)==(r['w'],r['h']);before=Image.new('RGBA',(w*8,h*8));without=before.copy()
for l in layers:
 c=Image.new('RGBA',before.size)
 for x,col in enumerate(l['Tiles']):
  for y,t in enumerate(col):
   for l2 in t['Layers']:
    fr=l2['Frames'][0];sh=fr['Sheet'];xy=fr['TexLoc'];tile=banks[sh].get((xy['X'],xy['Y']))
    if tile:c.alpha_composite(tile,(x*8,y*8))
 before.alpha_composite(c)
 if 'verdure separee' not in l['Name']:without.alpha_composite(c)
before.save(out/'carte-native-0.7.8-sans-portes-sans-ambiances.png');without.save(out/'carte-native-sans-verdure.png');print('dimensions map',before.size,'aperçu',r['w'],r['h']);print('Fichiers de comparaison extraits. Le rendu statique ne tient pas compte des objets, portes et ambiances.');
