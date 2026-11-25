from pathlib import Path
import gzip,struct,io,json,collections,hashlib,shutil
from PIL import Image
import numpy as np,ijson
R=Path(__file__).resolve().parent;B=R/'base';S=R/'corrections-pont-en-cours';O=R/'corrections-escalier-en-cours';N='Reverie_Raccord_Escalier_056';
for sub in ['payload','game/Content/Tile','art/reverie/tilesheets']:(O/sub).mkdir(parents=True,exist_ok=True)
for sub in ['game/Content/Tile','art/reverie/tilesheets']:
 for p in (S/sub).iterdir():shutil.copy2(p,O/sub/p.name)
img=Image.open(R/'reverie-055-phase0.png').convert('RGBA');source=Image.open(R/'reference-Metano_Town_Trimmed.png').convert('RGBA');after=img.copy();donor=[(728,456,752,480),(736,536,752,560)];target=[(736,816),(744,896)];
for d,t in zip(donor,target):after.paste(source.crop(d),t)
a=np.asarray(img);b=np.asarray(after);patches={};atlas=[];lookup={}
for cy in list(range(816//8,840//8))+list(range(896//8,920//8)):
 for cx in range(736//8,760//8):
  old=a[cy*8:cy*8+8,cx*8:cx*8+8];new=b[cy*8:cy*8+8,cx*8:cx*8+8];m=np.any(old!=new,axis=2)
  if not m.any():continue
  t=np.zeros((8,8,4),dtype=np.uint8);t[m]=new[m];key=t.tobytes()
  if key not in lookup:lookup[key]=len(atlas);atlas.append(Image.fromarray(t))
  patches[(cx,cy)]=lookup[key]
assert patches
header=8+16*len(atlas);body=bytearray();rec=[];sheet=Image.new('RGBA',(256,8*((len(atlas)+31)//32)))
for i,im in enumerate(atlas):
 x,y=i%32,i//32;q=io.BytesIO();im.save(q,format='PNG');data=q.getvalue();rec.append((x,y,header+len(body)));body+=struct.pack('<q',len(data))+data;sheet.paste(im,(x*8,y*8))
(O/'game/Content/Tile'/f'{N}.tile').write_bytes(struct.pack('<ii',8,len(atlas))+b''.join(struct.pack('<iiq',*v) for v in rec)+body);sheet.save(O/'art/reverie/tilesheets'/f'{N}.png')
cache={};banks={}
def tile(fr):
 name=fr.get('Sheet','');xy=fr['TexLoc'];key=(name,xy['X'],xy['Y'])
 if not name:return None
 if key not in cache:
  if name not in banks:
   p=S/'game/Content/Tile'/f'{name}.tile';p=p if p.exists() else B/'game/Content/Tile'/f'{name}.tile';data=p.read_bytes();size,n=struct.unpack_from('<ii',data);assert size==8
   banks[name]=(data,{struct.unpack_from('<iiq',data,8+16*i)[:2]:struct.unpack_from('<iiq',data,8+16*i)[2] for i in range(n)})
  data,d=banks[name];off=d[xy['X'],xy['Y']];n=struct.unpack_from('<q',data,off)[0];cache[key]=Image.open(io.BytesIO(data[off+8:off+8+n])).convert('RGBA')
 return cache[key]
results=[]
for path in sorted((S/'payload').glob('*.gz')):
 print('Contrôle des phases',path.name,flush=True);comps={k:[Image.new('RGBA',(8,8)) for _ in range(4)] for k in patches};upper=[]
 with gzip.open(path,'rb') as f:
  f.read(3)
  for li,l in enumerate(ijson.items(f,'Object.Layers.item')):
   for cell,ix in patches.items():
    cx,cy=cell
    for anim in l['Tiles'][cx][cy].get('Layers',[]):
     fs=anim.get('Frames',[])
     if not fs:continue
     for frame in range(4):
      im=tile(fs[frame%len(fs)])
      if im:comps[cell][frame].alpha_composite(im)
      if li>8 and im:
       assert not np.any((np.array(atlas[ix])[:,:,3]>0)&(np.array(im)[:,:,3]>0)),(path.name,cell,li,'surimpression')
   if li==8:assert l['Name']=='Objects Over'
 for (cx,cy),phases in comps.items():
  m=np.asarray(atlas[patches[(cx,cy)]])[:,:,3]>0;reference=np.asarray(img.crop((cx*8,cy*8,cx*8+8,cy*8+8)))
  for frame,im in enumerate(phases):
   got=np.asarray(im);assert np.all(got[m]==reference[m]),(path.name,(cx,cy),frame,'variation animée ou couleur de carte distincte')
 # Ajouter une couche transparente uniquement aux cellules cibles.
 raw=gzip.decompress(path.read_bytes()).decode('utf8');start=raw.index('"Name":"Objects Over"');pos=raw.index('"Tiles":[',start)+len('"Tiles":[');dec=json.JSONDecoder();splices=[]
 for cx in range(200):
  col,end=dec.raw_decode(raw,pos);relevant=[(cy,ix) for (x,cy),ix in patches.items() if x==cx]
  if relevant:
   previous=json.loads(raw[pos:end]);changed={cy for cy,ix in relevant}
   for cy,ix in relevant:
    cell=col[cy]
    if not cell:cell.update({'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1})
    cell.setdefault('Layers',[]).append({'Frames':[{'Sheet':N,'TexLoc':{'X':ix%32,'Y':ix//32}}],'FrameLength':60})
   assert all(previous[y]==col[y] for y in range(len(col)) if y not in changed)
   for cy,ix in relevant:
    old=previous[cy];new=col[cy];assert (old.get('Layers',[])==new['Layers'][:-1]) and (old=={} or {k:v for k,v in old.items() if k!='Layers'}=={k:v for k,v in new.items() if k!='Layers'})
   splices.append((pos,end,json.dumps(col,ensure_ascii=False,separators=(',',':'))))
  pos=end
  if cx<199:assert raw[pos]==',';pos+=1
 parts=[];pos=0
 for lo,hi,v in splices:parts.extend([raw[pos:lo],v]);pos=hi
 parts.append(raw[pos:]);modified=''.join(parts).encode('utf8');dest=O/'payload'/path.name;dest.write_bytes(gzip.compress(modified,compresslevel=6,mtime=0));assert gzip.decompress(dest.read_bytes())==modified
 results.append({'carte':path.name,'sha256':hashlib.sha256(modified).hexdigest()})
assert len(results)==10
(O/'manifest-escalier.json').write_text(json.dumps({'base':'97847f618dd16d99f9475e75b74242c247146631','donneur_metano_1522c7a8':donor,'cible':target,'cases':len(patches),'tuiles':len(atlas),'pixels':int(sum(np.count_nonzero(np.asarray(atlas[i])[:,:,3]) for i in patches.values())),'cartes':results},ensure_ascii=False,indent=2))
print('PASS',len(patches),'cases et',len(atlas),'tuiles, 4 phases, 10 variantes',flush=True)
