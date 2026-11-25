from pathlib import Path
import gzip,ijson,io,struct,collections,hashlib,json
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent;M=R/'reference-metano';B=R/'base';P=R/'corrections-etang-en-cours/payload/reverie_centre.rsground.gz'
def readbank(path):
 b=path.read_bytes();_,n=struct.unpack_from('<ii',b);d={}
 for i in range(n):
  x,y,o=struct.unpack_from('<iiq',b,8+16*i);ln=struct.unpack_from('<q',b,o)[0];d[x,y]=np.array(Image.open(io.BytesIO(b[o+8:o+8+ln])).convert('RGBA'))
 return d
base=readbank(M/'Content/Tile/Metano_Town_Base.tile'); animation=[readbank(M/f'Content/Tile/Metano_Town_River_Animation_{i}.tile') for i in range(1,5)]
orig={}
with open(M/'Data/Ground/metano_town.rsground','rb') as f:
 f.read(3)
 for l in ijson.items(f,'Object.Layers.item'):
  if l['Name']!='River':continue
  for x,col in enumerate(l['Tiles']):
   for y,c in enumerate(col):
    for a in c.get('Layers',[]):
     fs=a.get('Frames',[])
     if len(fs)==4 and all(i['Sheet']==f'Metano_Town_River_Animation_{z+1}' and i['TexLoc']=={'X':x,'Y':y} for z,i in enumerate(fs)):
      if all((x,y) in im for im in animation):
       aa=[im[x,y] for im in animation];diff=np.any(np.stack([np.any(z!=aa[0],axis=2) for z in aa[1:]]),axis=0)
       if diff.any():orig[x,y]=(aa,diff,a.get('FrameLength'))
print('animations rivière natives avec variations',len(orig),flush=True)
reverse=collections.defaultdict(list)
for xy,a in base.items():reverse[a.tobytes()].append(xy)
# Conservatively identify native donor sequences that all coincide, not simply first matching sprite.
def candidates(a):
 where=reverse.get(a.tobytes(),[]);out=[xy for xy in where if xy in orig]
 if not out:return (where,[],False)
 def signature(xy):
  arr,diff,dur=orig[xy];return (dur,hashlib.sha256(b''.join(z.tobytes() for z in arr)).digest())
 return (where,out,len({signature(xy) for xy in out})==1)
banks={};records=[]
with gzip.open(P,'rb') as f:
 f.read(3)
 for l in ijson.items(f,'Object.Layers.item'):
  if l['Name']!='River':continue
  for x,col in enumerate(l['Tiles']):
   for y,c in enumerate(col):
    layers=c.get('Layers',[])
    if not layers or any(len(a.get('Frames',[]))>1 for a in layers):continue
    a=layers[-1];fs=a.get('Frames',[])
    if len(fs)!=1 or not fs[0]['Sheet'].startswith('Reverie_Geo_'):continue
    s=fs[0]['Sheet'];xy=fs[0]['TexLoc'];
    if s not in banks:banks[s]=readbank(B/'game/Content/Tile'/f'{s}.tile')
    v=banks[s].get((xy['X'],xy['Y']))
    if v is None:continue
    where,out,unique=candidates(v)
    if out:
     records.append({'xy':[x*8,y*8],'sheet':s,'tex':[xy['X'],xy['Y']],'source_count':len(where),'animated_count':len(out),'unique':unique,'sources':out[:12]})
print('candidats statiques',len(records),'séquence unique',sum(r['unique'] for r in records),flush=True)
for r in records:
 if 430<=r['xy'][0]<=560 and 880<=r['xy'][1]<=1010:print(r,flush=True)
(R/'candidats-restauration-rivieres.json').write_text(json.dumps(records,indent=2))
