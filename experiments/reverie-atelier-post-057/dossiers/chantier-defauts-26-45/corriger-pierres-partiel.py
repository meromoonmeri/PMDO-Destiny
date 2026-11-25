from pathlib import Path
import gzip,struct,io,hashlib,json
from PIL import Image
R=Path(__file__).resolve().parent;BASE=R/'base';OUT=R/'corrections-partielles';N='Reverie_Rochers_Eau_056';OUT.mkdir(exist_ok=True)
def img(name,x,y):
 b=(BASE/'game/Content/Tile'/f'{name}.tile').read_bytes();size,n=struct.unpack_from('<ii',b);assert size==8
 index={struct.unpack_from('<iiq',b,8+16*i)[:2]:struct.unpack_from('<iiq',b,8+16*i)[2] for i in range(n)};off=index[(x,y)];ln=struct.unpack_from('<q',b,off)[0];return Image.open(io.BytesIO(b[off+8:off+8+ln])).convert('RGBA')
geo='Reverie_Geo_14_Paysages_composites';eau='Reverie_Geo_12_Eaux_frames';sources=[(geo,91,112),(geo,91,113),(eau,172,157),(eau,173,157)];imgs=[];flat=(128,216,224,255)
for i,src in enumerate(sources):
 a=img(*src);before=a.copy()
 if i==0:
  for y in range(4,8):
   assert a.getpixel((0,y))==(104,200,224,255);a.putpixel((0,y),flat)
 else:
  # Seulement la fine bande tronquée, hors de la pierre ; la forme et le
  # reste des trois images de vague restent strictement identiques.
  for y in range(8):a.putpixel((0,y),flat)
  for y in range(4):a.putpixel((1,y),flat)
  if i==2 and a.getpixel((1,5))==(24,128,152,255):a.putpixel((1,5),flat)
 imgs.append(a)
 print('tuile',src,'pixels modifiés',sum(a.getpixel((x,y))!=before.getpixel((x,y)) for x in range(8) for y in range(8)),flush=True)
header=8+16*len(imgs);body=bytearray();rec=[];sheet=Image.new('RGBA',(32,8))
for i,a in enumerate(imgs):
 q=io.BytesIO();a.save(q,format='PNG');b=q.getvalue();rec.append((i,0,header+len(body)));body+=struct.pack('<q',len(b))+b;sheet.paste(a,(8*i,0))
bank=struct.pack('<ii',8,len(imgs))+b''.join(struct.pack('<iiq',*v) for v in rec)+body
p=OUT/'game/Content/Tile'/f'{N}.tile';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(bank)
p=OUT/'art/reverie/tilesheets'/f'{N}.png';p.parent.mkdir(parents=True,exist_ok=True);sheet.save(p)
def ref(name,x,y):return {'Sheet':name,'TexLoc':{'X':x,'Y':y}}
def j(v):return json.dumps(v,ensure_ascii=False,separators=(',',':')).encode()
top=j(ref(geo,91,112));top_new=j(ref(N,0,0))
old=j([ref(geo,91,113),ref(eau,172,157),ref(eau,173,157),ref(eau,173,157)])
new=j([ref(N,1,0),ref(N,2,0),ref(N,3,0),ref(N,3,0)])
res=[]
for path in sorted((BASE/'payload').glob('*.gz')):
 raw=gzip.decompress(path.read_bytes());n,m=raw.count(top),raw.count(old);assert n==7 and m==5,(path.name,n,m)
 modified=raw.replace(top,top_new).replace(old,new)
 assert modified.count(top_new)==7 and modified.count(new)==5
 assert modified.replace(top_new,top).replace(new,old)==raw,'changement hors références ciblées'
 out=OUT/'payload'/path.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(gzip.compress(modified,compresslevel=6,mtime=0));assert gzip.decompress(out.read_bytes())==modified
 res.append({'carte':path.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'haut':n,'animations':m});print(path.name,'PASS',flush=True)
assert len(res)==10
(OUT/'manifest.json').write_text(json.dumps({'base':'97847f618dd16d99f9475e75b74242c247146631','modification':'atténuation des fragments verticaux ; animations originales de bas de pierre préservées','limites':'ne restaure pas toutes les animations ni ne corrige les autres captures','cartes':res},ensure_ascii=False,indent=2))
print('Terminé : correction locale partielle, aucune publication.',flush=True)
