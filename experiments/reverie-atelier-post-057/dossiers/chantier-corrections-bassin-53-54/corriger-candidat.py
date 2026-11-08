from pathlib import Path
from PIL import Image
import sys,gzip,json,copy,collections,struct,io,hashlib,zipfile
R=Path('/home/user/chantier-corrections-bassin-53-54');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
sheets={}
def get(f):
 n=f.get('Sheet','')
 if not n:return None
 if n not in sheets:sheets[n]=SheetReader(R/'banques'/(n+'.tile'))
 xy=f['TexLoc'];return sheets[n].get_tile(xy['X'],xy['Y'])
def cell(lays,x,y,phase=0):
 im=Image.new('RGBA',(8,8))
 for lay in lays:
  for sub in lay['Tiles'][x][y].get('Layers',[]):
   frames=sub.get('Frames',[])
   if frames:
    f=frames[phase%len(frames)];t=get(f)
    if t is not None:im.alpha_composite(t)
 return im
original=json.loads(gzip.decompress((R/'original-jeu.rsground.gz').read_bytes()).decode('utf-8-sig'));o=original['Object'];by={l['Name']:l for l in o['Layers']}
regions={'falaise_est':(162,263,172,278),'falaise_gauche_haut':(99,255,108,267),'falaise_gauche_milieu':(102,265,112,277),'falaise_gauche_bas':(102,278,112,292)}
# Exact opaque colors belonging to the tree's shadow and its rim. Restricted to marked zones.
colors={(128,112,88,255),(152,176,40,255),(128,152,40,255),(104,136,32,255)}
# Intact pixels and opaque cliff pixels only; never draw over leaf, trunk, or later decorations.
patch={};regions_stats=collections.Counter()
for region,(x1,y1,x2,y2) in regions.items():
 for x in range(x1,x2):
  for y in range(y1,y2):
   cliff=cell([by['Cliffs']],x,y);obj=cell([by['Objects']],x,y);above=cell([by[n] for n in ('Objects Anim','Objects Over','Objects Over Anim','Fringe')],x,y)
   p=Image.new('RGBA',(8,8));n=0
   for yy in range(8):
    for xx in range(8):
     c=cliff.getpixel((xx,yy));b=obj.getpixel((xx,yy));t=above.getpixel((xx,yy))
     if c[3]==255 and b in colors and t[3]==0:p.putpixel((xx,yy),c);n+=1
   if n:
    if (x,y) not in patch:
     patch[(x,y)]=p;regions_stats[region]+=n
print('pixels à dégager',dict(regions_stats),'cases',len(patch))
# Custom PMDO tilesheet, unique tiles; blobs follow native SheetReader format.
unique={}; entries=[];pos={}
for xy,img in sorted(patch.items()):
 raw=img.tobytes()
 if raw not in unique:
  unique[raw]=len(entries);entries.append(img)
 pos[xy]=unique[raw]
head=8+16*len(entries);blobs=[]
for im in entries:
 b=io.BytesIO();im.save(b,format='PNG');p=b.getvalue();blobs.append(struct.pack('<q',len(p))+p)
off=head;hdr=bytearray(struct.pack('<ii',8,len(entries)))
for i,b in enumerate(blobs):hdr+=struct.pack('<iiq',i,0,off);off+=len(b)
tiled=R/'banques'/'Reverie_Correction_Ombres_5354.tile';tiled.write_bytes(hdr+b''.join(blobs));r=SheetReader(tiled)
for i,im in enumerate(entries):assert r.get_tile(i,0).tobytes()==im.tobytes()
r.close()
# Complete two trunks from an identical complete reference. Only empty cells filled.
restores=[(165,252,162,318),(166,252,163,318),(167,252,164,318),(168,252,165,318),(166,253,163,319),(167,253,164,319),(131,315,162,318),(132,315,163,318),(133,315,164,318),(134,315,165,318),(132,316,163,319),(133,316,164,319)]
# Check known source appearance: intact surrounding identical same tree parts.
for x,y,rx,ry in [(164,248,161,314),(165,248,162,314),(166,248,163,314),(164,249,161,315),(130,311,161,314),(131,312,162,315),(132,314,163,317)]:assert cell([by['Objects']],x,y).tobytes()==cell([by['Objects']],rx,ry).tobytes(),(x,y,rx,ry)
del original,o,by
import gc;gc.collect()
logs=[];outdir=R/'candidat'/'payload';outdir.mkdir(parents=True,exist_ok=True)
for source,dest in [('original-jeu.rsground.gz','reverie_etang.rsground.gz'),('original-dev.rsground.gz','reverie_etang_Dev.rsground.gz')]:
 doc=json.loads(gzip.decompress((R/source).read_bytes()).decode('utf-8-sig'));o2=doc['Object'];lay={l['Name']:l for l in o2['Layers']};changed=[]
 def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 before={k:digest(v) for k,v in o2.items() if k!='Layers'}
 before_layers={n:digest(v) for n,v in lay.items() if n not in ('Objects','Objects Over','Objects Anim')}
 for x,y,rx,ry in restores:
  old=lay['Objects']['Tiles'][x][y];ref=lay['Objects']['Tiles'][rx][ry]
  assert not old.get('Layers') and ref.get('Layers'),(source,x,y)
  lay['Objects']['Tiles'][x][y]=copy.deepcopy(ref);changed.append({'layer':'Objects','x':x,'y':y,'avant':old,'apres':ref,'cause':'pied entier prélevé sur un arbre identique'})
 # Remove only the isolated 5-pixel line: two non-empty images in this one cell;
 # neighbouring water/rock animations and their frame lists remain unchanged.
 x,y=141,260;old=copy.deepcopy(lay['Objects Anim']['Tiles'][x][y]);assert len(old.get('Layers',[]))==1
 frames=old['Layers'][0]['Frames'];assert len(frames)==7 and [f['TexLoc'] for f in frames[:2]]==[{'X':41,'Y':123},{'X':27,'Y':123}] and all(not f.get('Sheet') for f in frames[2:])
 lay['Objects Anim']['Tiles'][x][y]={};changed.append({'layer':'Objects Anim','x':x,'y':y,'avant':old,'apres':{},'cause':'trait isolé de cinq pixels sur deux phases, autres animations conservées'})
 for (x,y),idx in sorted(pos.items()):
  old=copy.deepcopy(lay['Objects Over']['Tiles'][x][y]);new=copy.deepcopy(old)
  if not new:new={'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1}
  new.setdefault('Layers',[]).append({'Frames':[{'Sheet':'Reverie_Correction_Ombres_5354','TexLoc':{'X':idx,'Y':0}}],'FrameLength':60})
  lay['Objects Over']['Tiles'][x][y]=new;changed.append({'layer':'Objects Over','x':x,'y':y,'avant':old,'apres':new,'cause':'sommet de falaise masqué par ombre'})
 # Other data must be identical byte-equivalent in JSON; no entities, obstacles or scripts changed.
 for k,v in before.items():assert v==digest(o2[k]),k
 for n,v in before_layers.items():assert v==digest(lay[n]),n
 raw=b'\xef\xbb\xbf'+json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode();
 with open(outdir/dest,'wb') as f:
  with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as gz:gz.write(raw)
 logs.append({'source':source,'destination':dest,'modifications':changed})
 del doc,o2,lay,raw;gc.collect()
(R/'journal-corrections.json').write_text(json.dumps({'zones_pixels':dict(regions_stats),'tuiles_uniques':len(entries),'cartes':logs},ensure_ascii=False,indent=2))
print('Sauvegarde statique : jeu et Dev corrigés, collisions / entités / autres couches inchangées; pieds restaurés:',len(restores),'cases; patch:',len(entries),'tuiles uniques')
for s in sheets.values():s.close()
