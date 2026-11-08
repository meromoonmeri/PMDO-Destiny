from pathlib import Path
import gzip,struct,io,json,shutil,hashlib
from PIL import Image
import numpy as np,ijson
R=Path(__file__).resolve().parent;B=R/'base';S=R/'corrections-etang-en-cours';O=R/'corrections-berge-en-cours';N='Reverie_Animation_Berge_056'
for sub in ['payload','game/Content/Tile','art/reverie/tilesheets']:
 (O/sub).mkdir(parents=True,exist_ok=True)
 if sub!='payload':
  for p in (S/sub).iterdir():shutil.copy2(p,O/sub/p.name)
selection=json.loads((R/'selection-berge-40.json').read_text());assert len(selection)==38
base=np.asarray(Image.open(R/'reference-Metano_Town_Base.png').convert('RGBA'));anims=[np.asarray(Image.open(R/f'reference-Metano_Town_River_Animation_{i}.png').convert('RGBA')) for i in range(1,5)]
# Cadence et source originales présentes sur la carte Métano (pas seulement dans les PNG).
need={tuple(t['source']) for t in selection};valid={}
with open(R/'reference-metano/Data/Ground/metano_town.rsground','rb') as f:
 f.read(3)
 for l in ijson.items(f,'Object.Layers.item'):
  if l['Name']!='River':continue
  for x,y in need:
   candidates=[a for a in l['Tiles'][x][y].get('Layers',[]) if len(a.get('Frames',[]))==4 and all(fr['Sheet']==f'Metano_Town_River_Animation_{i+1}' and fr['TexLoc']=={'X':x,'Y':y} for i,fr in enumerate(a['Frames']))]
   assert len(candidates)==1 and candidates[0]['FrameLength']==10,(x,y,candidates)
   valid[x,y]=True
assert len(valid)==len(need)
# Tuiles transparentes : seules les parties variables et exclusivement aquatiques des originaux.
atlas=[];lookup={};cells={}
for item in selection:
 x,y=item['xy'];sx,sy=item['source'];srcbase=base[sy*8:sy*8+8,sx*8:sx*8+8];frames=[a[sy*8:sy*8+8,sx*8:sx*8+8] for a in anims];mask=np.any(np.stack([np.any(f!=frames[0],axis=2) for f in frames[1:]]),axis=0)
 assert int(mask.sum())==item['water'] and item['water']==item['delta']
 for z in [srcbase]+frames:assert np.all((z[:,:,3][mask]==255)&(z[:,:,2][mask]>z[:,:,0][mask])&(z[:,:,2][mask]>=z[:,:,1][mask]))
 ids=[]
 for fr in frames:
  out=np.zeros((8,8,4),dtype=np.uint8);out[mask]=fr[mask];key=out.tobytes()
  if key not in lookup:lookup[key]=len(atlas);atlas.append(Image.fromarray(out))
  ids.append(lookup[key])
 cells[x//8,y//8]=(ids,srcbase.tobytes())
header=8+16*len(atlas);rec=[];body=bytearray();sheet=Image.new('RGBA',(256,8*((len(atlas)+31)//32)))
for i,im in enumerate(atlas):
 x,y=i%32,i//32;q=io.BytesIO();im.save(q,format='PNG');b=q.getvalue();rec.append((x,y,header+len(body)));body+=struct.pack('<q',len(b))+b;sheet.paste(im,(x*8,y*8))
(O/'game/Content/Tile'/f'{N}.tile').write_bytes(struct.pack('<ii',8,len(atlas))+b''.join(struct.pack('<iiq',*v) for v in rec)+body);sheet.save(O/'art/reverie/tilesheets'/f'{N}.png')
banks={};cache={}
def tile(fr):
 name=fr['Sheet'];xy=fr['TexLoc'];key=(name,xy['X'],xy['Y'])
 if key not in cache:
  if name not in banks:
   p=S/'game/Content/Tile'/f'{name}.tile';p=p if p.exists() else B/'game/Content/Tile'/f'{name}.tile';b=p.read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8
   banks[name]=(b,{struct.unpack_from('<iiq',b,8+16*i)[:2]:struct.unpack_from('<iiq',b,8+16*i)[2] for i in range(n)})
  b,ix=banks[name];off=ix[key[1:]];ln=struct.unpack_from('<q',b,off)[0];cache[key]=Image.open(io.BytesIO(b[off+8:off+8+ln])).convert('RGBA').tobytes()
 return cache[key]
results=[]
for path in sorted((S/'payload').glob('*.gz')):
 print('Berge',path.name,flush=True);raw=gzip.decompress(path.read_bytes()).decode('utf8');start=raw.index('"Name":"River"');pos=raw.index('"Tiles":[',start)+len('"Tiles":[');dec=json.JSONDecoder();splices=[];changed=0
 for cx in range(200):
  col,end=dec.raw_decode(raw,pos);rel=[(y,vals) for (x,y),vals in cells.items() if x==cx]
  if rel:
   prev=json.loads(raw[pos:end]);ys={y for y,_ in rel}
   for cy,(ids,sourcebytes) in rel:
    cell=col[cy];layers=cell['Layers'];assert layers and all(len(a.get('Frames',[]))<=1 for a in layers),(path,cx,cy)
    assert tile(layers[-1]['Frames'][0])==sourcebytes,(path,cx,cy,'lien origine incorrect')
    layers.append({'Frames':[{'Sheet':N,'TexLoc':{'X':i%32,'Y':i//32}} for i in ids],'FrameLength':10});changed+=1
   assert all(prev[y]==col[y] for y in range(len(col)) if y not in ys)
   for cy,_ in rel:
    old,new=prev[cy],col[cy];assert old['Layers']==new['Layers'][:-1] and {k:v for k,v in old.items() if k!='Layers'}=={k:v for k,v in new.items() if k!='Layers'}
   splices.append((pos,end,json.dumps(col,ensure_ascii=False,separators=(',',':'))))
  pos=end
  if cx<199:assert raw[pos]==',';pos+=1
 assert changed==len(cells)
 parts=[];pos=0
 for lo,hi,v in splices:parts.extend([raw[pos:lo],v]);pos=hi
 parts.append(raw[pos:]);modified=''.join(parts).encode('utf8');dest=O/'payload'/path.name;dest.write_bytes(gzip.compress(modified,compresslevel=6,mtime=0));assert gzip.decompress(dest.read_bytes())==modified
 results.append({'carte':path.name,'cases':changed,'sha256':hashlib.sha256(modified).hexdigest()})
assert len(results)==10
(O/'manifest-berge.json').write_text(json.dumps({'base':'97847f618dd16d99f9475e75b74242c247146631','source':'Halcyon@1522c7a8b7a34d70078e11ed605b21d563b0dc51 : quatre banques Metano_Town_River_Animation, données de la carte metano_town','selection':selection,'nombre_tuiles':len(atlas),'duree':10,'cartes':results},ensure_ascii=False,indent=2))
print('PASS',len(cells),'cases,',len(atlas),'tuiles natives masquées, 4 phases, 10 variantes',flush=True)
