from pathlib import Path
import gzip,ijson,struct,io,json,hashlib,collections
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;B=R/'base';O=R/'reprise-arrondie-51-52';N='Reverie_Raccords_Arrondis_51_52_058';cache={};banks={}
def tile(fr):
 n=fr.get('Sheet','');xy=fr['TexLoc'];key=(n,xy['X'],xy['Y'])
 if not n:return None
 if key not in cache:
  if n not in banks:
   data=(O/(n+'.tile')).read_bytes() if n==N else (B/'game/Content/Tile'/(n+'.tile')).read_bytes();sz,count=struct.unpack_from('<ii',data);assert sz==8
   banks[n]=(data,{struct.unpack_from('<iiq',data,8+i*16)[:2]:struct.unpack_from('<iiq',data,8+i*16)[2] for i in range(count)})
  data,idx=banks[n];off=idx[xy['X'],xy['Y']];length=struct.unpack_from('<q',data,off)[0];cache[key]=Image.open(io.BytesIO(data[off+8:off+8+length])).convert('RGBA')
 return cache[key]
regions=[(1376,584,1544,648),(1056,336,1080,520)]
def render(path):
 ret=[[Image.new('RGBA',(x1-x0,y1-y0)) for _ in range(4)] for x0,y0,x1,y1 in regions];found=collections.Counter()
 with gzip.open(path,'rb') as f:
  assert f.read(3)==b'\xef\xbb\xbf'
  for li,l in enumerate(ijson.items(f,'Object.Layers.item')):
   for ri,(x0,y0,x1,y1) in enumerate(regions):
    for x in range(x0//8,x1//8):
     for y in range(y0//8,y1//8):
      for a in l['Tiles'][x][y].get('Layers',[]):
       fs=a.get('Frames',[])
       if any(t.get('Sheet')==N for t in fs):
        found[(l['Name'],len(fs),a['FrameLength'])]+=1
       for i in range(4):
        if fs:
         im=tile(fs[i%len(fs)])
         if im:ret[ri][i].alpha_composite(im,(x*8-x0,y*8-y0))
 return [[np.array(im) for im in r] for r in ret],found
base=B/'payload/reverie_centre.rsground.gz';original,_=render(base);new,counts=render(O/'payload/reverie_centre.rsground.gz')
reference=np.array(Image.open(R/'reverie-057-phase0.png').convert('RGBA'));src=reference[1074:1118,764:844];idx=np.arange(80);src=src[:,np.where(idx<40,idx+8,idx-8)];cl=np.array(Image.open(R/'calques/02_Cliffs.png').convert('RGBA'))[:,:,3];expect=reference[584:648,1376:1544].copy();mask=cl[586:630,1412:1492]==0;expect[2:46,36:116][mask]=src[mask]
metano=np.array(Image.open('/home/user/chantier-chemins-reverie/metano-reference-sol-falaises.png').convert('RGBA'))
for (x0,y0,x1,y1),(dx,dy) in [((1380,604,1440,648),(187,14)),((1466,604,1544,648),(186,30))]:expect[y0-584:y1-584,x0-1376:x1-1376]=metano[y0-dy:y1-dy,x0-dx:x1-dx]
expect[628-584:648-584,1430-1376:1474-1376]=metano[595:615,1248:1292]
for i in range(4):assert np.array_equal(new[0][i],expect),('51',i)
pts=[(336,0),(346,1),(354,2),(362,3),(374,4),(384,3),(398,1),(405,0),(416,2),(425,3),(437,4),(451,2),(463,0),(472,1),(484,3),(496,4),(507,2),(514,1),(520,0)]
for i in range(4):
 expect=original[1][i].copy()
 for y in range(336,520):
  d=int(round(np.interp(y,*zip(*pts))))
  if d:expect[y-336,:16]=original[1][i][y-336,d:16+d]
 assert np.array_equal(new[1][i],expect),('52',i)
assert counts=={('Base',1,60):134,('Objects Over',4,10):46},counts
for cell,ref in enumerate(new[1][0]):pass
assert any(not np.array_equal(new[1][0],new[1][i]) for i in [1,2,3]),'eau figée'
manifest=json.loads((O/'manifest.json').read_text())
for c in manifest['cartes']:
 f=O/'payload'/c['carte'];assert hashlib.sha256(gzip.decompress(f.read_bytes())).hexdigest()==c['sha256']
print('PASS rendu indépendant : 51, 52 ; quatre phases, 10 empreintes de cartes ; banque et durée vérifiées ; eau animée')
