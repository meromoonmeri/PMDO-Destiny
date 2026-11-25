from pathlib import Path
from PIL import Image
import json,gzip,struct,io,hashlib,copy,gc,collections,sys
R=Path('/home/user/chantier-corrections-bassin-55'); P=Path('/home/user/chantier-corrections-bassin-53-54');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
source=P/'candidat/payload/reverie_etang.rsground.gz';j=json.loads(gzip.decompress(source.read_bytes()).decode('utf-8-sig'));o=j['Object'];L={l['Name']:l for l in o['Layers']};banks={}
def get(frame):
 name=frame.get('Sheet','')
 if not name:return None
 if name not in banks:banks[name]=SheetReader(P/'banques'/(name+'.tile'))
 p=frame['TexLoc'];return banks[name].get_tile(p['X'],p['Y'])
def basecell(x,y):
 im=Image.new('RGBA',(8,8))
 for sub in L['Base']['Tiles'][x][y].get('Layers',[]):
  frames=sub.get('Frames',[]);assert len(frames)==1,'Ne pas retoucher un sol animé'
  im2=get(frames[0]);
  if im2:im.alpha_composite(im2)
 return im
ref=get({'Sheet':'Reverie_Geo_01_Sol_herbe','TexLoc':{'X':39,'Y':218}});assert ref and ref.size==(8,8)
patch={};stats=collections.Counter();skipped=collections.Counter();seen=set()
def patch_pixel(x,y,region,kind):
 if (x,y) in seen:return
 seen.add((x,y));tx,ty=x//8,y//8;old=basecell(tx,ty).getpixel((x%8,y%8));new=ref.getpixel((x%8,y%8))
 # target must be opaque or nearly opaque olive grass, not terrain/decoration/transparent
 r,g,b,a=old
 if a<200 or not(145<=r<=210 and 165<=g<=220 and 35<=b<=105 and g>=r):skipped[region]+=1;return
 if kind=='vert_fleur' and sum(old[:3])>=sum(new[:3])-12:return
 if old==new:return
 if (tx,ty) not in patch:patch[(tx,ty)]=Image.new('RGBA',(8,8))
 patch[(tx,ty)].putpixel((x%8,y%8),new);stats[region]+=1
# Remove only the photographed rectilinear grass seam, not the stump / foliage.
for x in range(1285,1381):
 for y in (2127,2128):patch_pixel(x,y,'trait_horizontal_souche','horizontal')
for x in (1379,1380):
 for y in range(2104,2129):patch_pixel(x,y,'trait_vertical_souche','vertical')
for x in (1187,1188):
 for y in range(2256,2320):patch_pixel(x,y,'trait_vertical_fleurs','vert_fleur')
print('seams',dict(stats),'ignored terrain non-sol',dict(skipped),'cells',len(patch),flush=True)
unique={};arr=[];indices={}
for xy,img in sorted(patch.items()):
 key=img.tobytes()
 if key not in unique:unique[key]=len(arr);arr.append(img)
 indices[xy]=unique[key]
blobs=[]
for im in arr:
 mem=io.BytesIO();im.save(mem,format='PNG');b=mem.getvalue();blobs.append(struct.pack('<q',len(b))+b)
pos=8+16*len(arr);head=bytearray(struct.pack('<ii',8,len(arr)))
for i,b in enumerate(blobs):head+=struct.pack('<iiq',i,0,pos);pos+=len(b)
OUT=R/'banques';OUT.mkdir(parents=True,exist_ok=True);sheet=OUT/'Reverie_Correction_Herbe_55.tile';sheet.write_bytes(head+b''.join(blobs));check=SheetReader(sheet)
for i,im in enumerate(arr):assert check.get_tile(i,0).tobytes()==im.tobytes()
check.close();del o,j,L;gc.collect()
logs=[];target=R/'candidat/payload';target.mkdir(parents=True,exist_ok=True)
for name in ('reverie_etang.rsground.gz','reverie_etang_Dev.rsground.gz'):
 src=P/'candidat/payload'/name;doc=json.loads(gzip.decompress(src.read_bytes()).decode('utf-8-sig'));o=doc['Object'];base=next(l for l in o['Layers'] if l['Name']=='Base')['Tiles'];logs_here=[]
 for (x,y),idx in sorted(indices.items()):
  old=copy.deepcopy(base[x][y]);new=copy.deepcopy(old)
  if not new:new={'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1}
  assert all(len(f.get('Frames',[]))==1 for f in new.get('Layers',[])),(x,y)
  new.setdefault('Layers',[]).append({'Frames':[{'Sheet':'Reverie_Correction_Herbe_55','TexLoc':{'X':idx,'Y':0}}],'FrameLength':60});base[x][y]=new;logs_here.append({'layer':'Base','x':x,'y':y,'avant':old,'apres':new})
 b=b'\xef\xbb\xbf'+json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode()
 with (target/name).open('wb') as fp:
  with gzip.GzipFile(fileobj=fp,mode='wb',mtime=0) as gz:gz.write(b)
 logs.append({'source':str(src),'destination':name,'modifications':logs_here});del doc,o,base,b;gc.collect()
(R/'journal-55.json').write_text(json.dumps({'pixels_par_zone':dict(stats),'pixels_non_retenus':dict(skipped),'tuiles_uniques':len(arr),'cartes':logs},ensure_ascii=False,indent=2));
for r in banks.values():r.close()
print('Candidats produits, pas installés',flush=True)
