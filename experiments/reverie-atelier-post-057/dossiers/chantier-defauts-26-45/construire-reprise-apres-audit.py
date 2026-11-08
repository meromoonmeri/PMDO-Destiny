from pathlib import Path
import gzip,ijson,json,hashlib,shutil
R=Path(__file__).resolve().parent;A=R/'base/payload';B=R/'corrections-alpha-en-cours/payload';K=R/'kit-reprise-visuel';K.mkdir(exist_ok=True)
for sub in ('game/Content/Tile','art/reverie/tilesheets'):
 (K/sub).mkdir(parents=True,exist_ok=True)
 for p in (R/'corrections-alpha-en-cours'/sub).iterdir():shutil.copy2(p,K/sub/p.name)
patches={};h=lambda b:hashlib.sha256(b).hexdigest()
for p in sorted(A.glob('*.gz')):
 original=p.read_bytes();updated=(B/p.name).read_bytes();changes=[]
 with gzip.open(p,'rb') as a,gzip.open(B/p.name,'rb') as b:
  a.read(3);b.read(3)
  for old,new in zip(ijson.items(a,'Object.Layers.item'),ijson.items(b,'Object.Layers.item'),strict=True):
   assert old['Name']==new['Name']
   for x,(oa,na) in enumerate(zip(old['Tiles'],new['Tiles'],strict=True)):
    for y,(o,n) in enumerate(zip(oa,na,strict=True)):
     if o!=n:changes.append([old['Name'],x,y,o,n])
 patches[p.name]={'source_gzip_sha256':h(original),'source_raw_sha256':h(gzip.decompress(original)),'result_raw_sha256':h(gzip.decompress(updated)),'cells':changes}
 print(p.name,len(changes),flush=True)
assert len(patches)==10
raw=json.dumps({'base_commit':'97847f618dd16d99f9475e75b74242c247146631','maps':patches},ensure_ascii=False,separators=(',',':')).encode();(K/'delta-cellules.json.gz').write_bytes(gzip.compress(raw,compresslevel=9,mtime=0));print('Delta',len(raw),'octets, compressé', (K/'delta-cellules.json.gz').stat().st_size,flush=True)
