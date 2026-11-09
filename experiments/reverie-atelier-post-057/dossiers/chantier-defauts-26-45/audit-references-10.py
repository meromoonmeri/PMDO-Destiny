from pathlib import Path
import gzip,ijson,struct,io,json,hashlib,collections
import orjson
from PIL import Image
R=Path(__file__).resolve().parent;B=R/'base';W=R/'corrections-alpha-en-cours';O=R/'audit-pixel-integral';banks={};bad=[];missing=[];allmaps={}
def valid(fr):
 name=fr.get('Sheet','');q=fr.get('TexLoc',{});xy=q.get('X'),q.get('Y')
 if not name:return True
 if name not in banks:
  p=W/'game/Content/Tile'/f'{name}.tile';p=p if p.exists() else B/'game/Content/Tile'/f'{name}.tile'
  if not p.exists():banks[name]=None;return False
  raw=p.read_bytes();size,n=struct.unpack_from('<ii',raw);assert size==8
  idx={struct.unpack_from('<iiq',raw,8+16*i)[:2]:struct.unpack_from('<iiq',raw,8+16*i)[2] for i in range(n)};banks[name]=(raw,idx)
 if banks[name] is None or xy not in banks[name][1]:return False
 return True
for path in sorted((W/'payload').glob('*.gz')):
 print('Scan des références',path.name,flush=True);layers=[];nrefs=nseq=missingn=0
 with gzip.open(path,'rb') as f:
  f.read(3)
  for l in ijson.items(f,'Object.Layers.item'):
   assert len(l['Tiles'])==200
   nempty=0
   for x,col in enumerate(l['Tiles']):
    assert len(col)==500
    for y,c in enumerate(col):
     for a in c.get('Layers',[]):
      fs=a.get('Frames',[]);nseq+=bool(fs);nrefs+=len(fs)
      if len(fs)>1 and (not isinstance(a.get('FrameLength'),int) or a['FrameLength']<=0):bad.append([path.name,l['Name'],x,y,'invalid duration'])
      for fr in fs:
       if not valid(fr):bad.append([path.name,l['Name'],x,y,fr])
   layers.append({'name':l['Name'],'sha256':hashlib.sha256(orjson.dumps(l['Tiles'])).hexdigest()})
 allmaps[path.name]={'layers':layers,'sequences':nseq,'frames':nrefs}
print('banques',len(banks),'erreurs',len(bad),flush=True)
(O/'references-10-cartes.json').write_text(json.dumps({'maps':allmaps,'errors':bad,'bank_count':len(banks)},ensure_ascii=False,indent=2));assert len(allmaps)==10 and not bad
for i in range(11):
 h=collections.Counter(v['layers'][i]['sha256'] for v in allmaps.values());print('Couche',i,next(iter(allmaps.values()))['layers'][i]['name'],'profils',len(h),'effectifs',sorted(h.values(),reverse=True),flush=True)
print('PASS 10 cartes, frames, durées, index et coordonnées de tuiles',flush=True)
