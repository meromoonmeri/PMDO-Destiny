from pathlib import Path
import gzip,struct,io,json,hashlib,collections
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;SRC=R/'corrections-partielles';O=R/'corrections-en-cours';B=R/'base';REF=R/'reference-metano';geo='Reverie_Geo_14_Paysages_composites';eau='Reverie_Geo_12_Eaux_frames';part='Reverie_Rochers_Eau_056';bank='Reverie_Ondulations_Rochers_056'
pts=[(648,312),(648,416),(664,288),(856,288),(872,328),(880,376),(888,416)]
for sub in ['payload','game/Content/Tile','art/reverie/tilesheets']:(O/sub).mkdir(parents=True,exist_ok=True)
# Réemploie le correctif précédent sans toucher à ses fichiers.
for sub in ['game/Content/Tile','art/reverie/tilesheets']:
 for f in (SRC/sub).iterdir():(O/sub/f.name).write_bytes(f.read_bytes())
# Exactement les pixels ajoutés par l'animation originale de la pierre Métano.
source=Image.open(R/'reference-Metano_Town_Animation_Tileset.png').convert('RGBA')
frames=[np.array(source.crop(((1+5*k)*8,163*8,(5+5*k)*8,166*8))) for k in range(8)]
for k in range(1,8):
 diff=np.any(frames[k]!=frames[0],axis=2);assert diff.sum()==27 and np.all(frames[0][:,:,3][diff]==0) and np.all(frames[k][:,:,3][diff]==255)
# extraire uniquement les 27 pixels de vague, transparents en image initiale :
# ne repasser ni la pierre ni son fond par-dessus le panneau / la décoration.
mask=(frames[0][:,:,3]==0)&(frames[1][:,:,3]>0);assert mask.sum()==27
atlas=[]; sheet=Image.new('RGBA',(8*8,4*8))
for cx in range(4):
 for k in range(8):
  tile=np.zeros((8,8,4),dtype=np.uint8);tile[mask[16:24,cx*8:cx*8+8]]=frames[k][16:24,cx*8:cx*8+8][mask[16:24,cx*8:cx*8+8]]
  im=Image.fromarray(tile);atlas.append((k,cx,im));sheet.paste(im,(k*8,cx*8))
header=8+16*len(atlas);body=bytearray();rec=[]
for x,y,im in atlas:
 q=io.BytesIO();im.save(q,format='PNG');data=q.getvalue();rec.append((x,y,header+len(body)));body+=struct.pack('<q',len(data))+data
raw=struct.pack('<ii',8,len(atlas))+b''.join(struct.pack('<iiq',*v) for v in rec)+body
(O/'game/Content/Tile'/f'{bank}.tile').write_bytes(raw);sheet.save(O/'art/reverie/tilesheets'/f'{bank}.png')
# Étendre la première banque avec la variante du fragment sous la décoration.
p=O/'game/Content/Tile'/f'{part}.tile';raw=p.read_bytes();_,n=struct.unpack_from('<ii',raw);assert n==4
imgs=[]
for i in range(n):
 x,y,o=struct.unpack_from('<iiq',raw,8+16*i);ln=struct.unpack_from('<q',raw,o)[0];imgs.append(Image.open(io.BytesIO(raw[o+8:o+8+ln])).convert('RGBA'))
def get_tile(path,x,y):
 raw=path.read_bytes();_,n=struct.unpack_from('<ii',raw)
 for i in range(n):
  tx,ty,o=struct.unpack_from('<iiq',raw,8+16*i)
  if (x,y)==(tx,ty):
   ln=struct.unpack_from('<q',raw,o)[0];return Image.open(io.BytesIO(raw[o+8:o+8+ln])).convert('RGBA')
 raise ValueError((path,x,y))
a=get_tile(B/'game/Content/Tile'/f'{eau}.tile',200,157);before=a.copy();flat=(128,216,224,255)
for y in range(8):a.putpixel((0,y),flat)
for y in range(4):a.putpixel((1,y),flat)
assert sum(a.getpixel((x,y))!=before.getpixel((x,y)) for x in range(8) for y in range(8))==12
imgs.append(a);header=8+16*len(imgs);body=bytearray();rec=[];sheet=Image.new('RGBA',(len(imgs)*8,8))
for i,im in enumerate(imgs):
 q=io.BytesIO();im.save(q,format='PNG');data=q.getvalue();rec.append((i,0,header+len(body)));body+=struct.pack('<q',len(data))+data;sheet.paste(im,(8*i,0))
p.write_bytes(struct.pack('<ii',8,len(imgs))+b''.join(struct.pack('<iiq',*v) for v in rec)+body);sheet.save(O/'art/reverie/tilesheets'/f'{part}.png')
def ref(name,x,y):return {'Sheet':name,'TexLoc':{'X':x,'Y':y}}
def wave(cx):return {'Frames':[ref(bank,k,cx) for k in [0,1,2,3,4,5,6,7,7]],'FrameLength':10}
def js(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
# L'exception animée conserve toutes ses images d'origine, sauf les 12 pixels de la coupure.
old=js([ref(geo,91,113),ref(eau,200,157),ref(eau,200,157),ref(eau,200,157)])
new=js([ref(part,1,0),ref(part,4,0),ref(part,4,0),ref(part,4,0)])
manifest=[]
for path in sorted((SRC/'payload').glob('*.gz')):
 print('Restitution',path.name,flush=True);raw=gzip.decompress(path.read_bytes()).decode('utf8');assert raw.count(old)==1
 raw=raw.replace(old,new)
 # Décoder une colonne à la fois de la couche Objects, conserver les autres segments octet à octet.
 start=raw.index('"Name":"Objects"');pos=raw.index('"Tiles":[',start)+len('"Tiles":[');dec=json.JSONDecoder();splices=[];cnt=0
 targets=collections.defaultdict(list)
 for sx,sy in pts:
  for cx in range(4):targets[sx//8+cx].append(((sy+8)//8,cx,sx,sy))
 for x in range(200):
  col,end=dec.raw_decode(raw,pos)
  if x in targets:
   previous=json.loads(raw[pos:end]); changed=set()
   for y,cx,sx,sy in targets[x]:
    cell=col[y]
    if not cell:cell.update({'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1})
    layers=cell.setdefault('Layers',[])
    # Case masquée par le panneau : retirer le fragment de rive en conservant toutes les autres couches.
    if (sx,sy,cx)==(648,312,0):
     hit=[a for a in layers if a.get('Frames')==[ref(geo,91,113)]];assert len(hit)==1;hit[0]['Frames']=[ref(part,1,0)]
    # Placer l'ondulation après la pierre, mais avant le panneau dans la même cellule.
    index=next((i for i,a in enumerate(layers) if any(z['Sheet']=='Reverie_Geo_08_Batiments_objets' for z in a.get('Frames',[]))),len(layers))
    layers.insert(index,wave(cx));changed.add(y);cnt+=1
   assert all(previous[y]==col[y] for y in range(len(col)) if y not in changed)
   splices.append((pos,end,js(col)))
  pos=end
  if x<199:assert raw[pos]==',';pos+=1
 assert cnt==28
 out=[];i=0
 for a,b,s in splices:out.extend([raw[i:a],s]);i=b
 out.append(raw[i:]);out=''.join(out).encode('utf8');dest=O/'payload'/path.name;dest.write_bytes(gzip.compress(out,compresslevel=6,mtime=0));assert gzip.decompress(dest.read_bytes())==out
 manifest.append({'carte':path.name,'animations_restituees':7,'cases':cnt,'sha256':hashlib.sha256(out).hexdigest()})
assert len(manifest)==10
(O/'manifest-pierres.json').write_text(json.dumps({'base':'97847f618dd16d99f9475e75b74242c247146631','source':'Palikadude/Halcyon@1522c7a8b7a34d70078e11ed605b21d563b0dc51, Metano_Town_Animation_Tileset, x=1..4, y=163..165, pas=5','sequence':[0,1,2,3,4,5,6,7,7],'duree':10,'pixels_animes':27,'points':pts,'cartes':manifest},indent=2,ensure_ascii=False))
print('PASS : 7 pierres et 9 phases natives, 10 cartes ; scène et décorations conservées.',flush=True)
