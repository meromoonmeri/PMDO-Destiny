from pathlib import Path
import gzip,ijson,struct,io,json,hashlib,collections,shutil
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;B=R/'base';S=R/'corrections-chemin30-en-cours';O=R/'corrections-alpha-en-cours';N='Reverie_Fond_Transparences_056'
for sub in ['payload','game/Content/Tile','art/reverie/tilesheets']:
 (O/sub).mkdir(parents=True,exist_ok=True)
 if sub!='payload':
  for p in (S/sub).iterdir():shutil.copy2(p,O/sub/p.name)
# Chaque pixel est emprunté à un voisin du même sol/rive, jamais inventé.
source={(1591,807):(1591,808),(1592,807):(1592,808),(1593,807):(1593,808),(1594,807):(1594,808), (1119,1702):(1120,1702),(1118,1703):(1120,1703),(1119,1703):(1120,1703), (1048,1720):(1051,1720),(1049,1720):(1051,1720),(1050,1720):(1051,1720),(1048,1721):(1051,1721),(1049,1721):(1051,1721)}
image=Image.open(R/'audit-pixel-integral/rendu-phase0.png').convert('RGBA');possible=np.asarray(Image.open(R/'audit-pixel-integral/alpha-transparent-au-moins-une-phase.png'))
patches=collections.defaultdict(lambda:np.zeros((8,8,4),dtype=np.uint8))
for (x,y),(u,v) in source.items():
 assert image.getpixel((x,y))[3]==0 and possible[y,x]==255
 p=image.getpixel((u,v));assert p[3]==255;patches[x//8,y//8][y%8,x%8]=p
assert len(patches)==4 and len(source)==12
atlas=[Image.fromarray(a) for a in patches.values()];indices={k:i for i,k in enumerate(patches)};header=8+16*len(atlas);body=bytearray();rec=[];sheet=Image.new('RGBA',(len(atlas)*8,8))
for i,im in enumerate(atlas):
 q=io.BytesIO();im.save(q,format='PNG');data=q.getvalue();rec.append((i,0,header+len(body)));body+=struct.pack('<q',len(data))+data;sheet.paste(im,(i*8,0))
(O/'game/Content/Tile'/f'{N}.tile').write_bytes(struct.pack('<ii',8,len(atlas))+b''.join(struct.pack('<iiq',*r) for r in rec)+body);sheet.save(O/'art/reverie/tilesheets'/f'{N}.png')
cache={};banks={}
def tile(fr):
 name=fr.get('Sheet','');xy=fr['TexLoc'];key=(name,xy['X'],xy['Y'])
 if not name:return None
 if key not in cache:
  if name not in banks:
   p=S/'game/Content/Tile'/f'{name}.tile';p=p if p.exists() else B/'game/Content/Tile'/f'{name}.tile';b=p.read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8;bix={struct.unpack_from('<iiq',b,8+16*i)[:2]:struct.unpack_from('<iiq',b,8+16*i)[2] for i in range(n)};banks[name]=(b,bix)
  b,ix=banks[name];off=ix[key[1:]];ln=struct.unpack_from('<q',b,off)[0];cache[key]=np.asarray(Image.open(io.BytesIO(b[off+8:off+8+ln])).convert('RGBA'))
 return cache[key]
results=[]
for path in sorted((S/'payload').glob('*.gz')):
 print('Contrôle de toutes les images',path.name,flush=True)
 # Dans chaque variante aucune image de chaque calque ne doit déjà occuper ces pixels.
 with gzip.open(path,'rb') as f:
  f.read(3)
  for layer in ijson.items(f,'Object.Layers.item'):
   for (cx,cy),idx in indices.items():
    pm=np.asarray(atlas[idx])[:,:,3]>0
    for a in layer['Tiles'][cx][cy].get('Layers',[]):
     for fr in a.get('Frames',[]):
      img=tile(fr)
      if img is not None:assert not np.any((img[:,:,3]>0)&pm),(path.name,layer['Name'],cx,cy,fr)
 raw=gzip.decompress(path.read_bytes()).decode('utf8');start=raw.index('"Name":"Base"');pos=raw.index('"Tiles":[',start)+len('"Tiles":[');dec=json.JSONDecoder();splices=[]
 for x in range(200):
  col,end=dec.raw_decode(raw,pos);rel=[(y,i) for (cx,y),i in indices.items() if cx==x]
  if rel:
   prev=json.loads(raw[pos:end]);ys={y for y,i in rel}
   for y,i in rel:
    c=col[y]
    if not c:c.update({'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1})
    c.setdefault('Layers',[]).append({'Frames':[{'Sheet':N,'TexLoc':{'X':i,'Y':0}}],'FrameLength':60})
   assert all(prev[y]==col[y] for y in range(len(col)) if y not in ys)
   for y,i in rel:assert prev[y].get('Layers',[])==col[y]['Layers'][:-1] and (prev[y]=={} or {k:v for k,v in prev[y].items() if k!='Layers'}=={k:v for k,v in col[y].items() if k!='Layers'})
   splices.append((pos,end,json.dumps(col,ensure_ascii=False,separators=(',',':'))))
  pos=end
  if x<199:assert raw[pos]==',';pos+=1
 parts=[];pos=0
 for lo,hi,v in splices:parts.extend([raw[pos:lo],v]);pos=hi
 parts.append(raw[pos:]);updated=''.join(parts).encode('utf8');dest=O/'payload'/path.name;dest.write_bytes(gzip.compress(updated,compresslevel=6,mtime=0));assert gzip.decompress(dest.read_bytes())==updated
 results.append({'carte':path.name,'sha256':hashlib.sha256(updated).hexdigest()})
assert len(results)==10
(O/'manifest-transparences.json').write_text(json.dumps({'base':'97847f618dd16d99f9475e75b74242c247146631','pixels_copies':[{'trou':xy,'source':uv,'rgba':image.getpixel(uv)} for xy,uv in source.items()],'cellules':len(indices),'cartes':results},ensure_ascii=False,indent=2));print('PASS 12 pixels, 4 cases, aucune image existante modifiée ni masquée, 10 variantes',flush=True)
