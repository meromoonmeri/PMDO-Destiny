from pathlib import Path
import gzip,json,struct,io,hashlib,zipfile,collections
import numpy as np, ijson
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent; B=R/'base'; O=R/'reprise-arrondie-27-51-52'; O.mkdir(exist_ok=True)
N='Reverie_Raccords_Arrondis_27_51_52_058'; base_sha='ee39156a24f350b67e81740478be8505f4ff1a05'
reference=np.array(Image.open(R/'reverie-057-phase0.png').convert('RGBA'))
cliff=np.array(Image.open(R/'calques/02_Cliffs.png').convert('RGBA'))[:,:,3]
# Donneur intégralement situé dans Base, sans animation ou objet. La duplication
# de colonnes dans la zone de sable élargit le chemin sans interpolation.
arr=reference.copy(); src=reference[1074:1118,764:844]; xx=np.arange(80); src=src[:,np.where(xx<40,xx+8,xx-8),:]
mask=cliff[586:630,1412:1492]==0; arr[586:630,1412:1492][mask]=src[mask]
# Deux retours de chemin prélevés sur un carrefour Métano natif, sans
# rotation, recoloration ou interpolation ; comparer les raccords en contexte.
metano=np.array(Image.open('/home/user/chantier-chemins-reverie/metano-reference-sol-falaises.png').convert('RGBA'))
for (x0,y0,x1,y1),(dx,dy) in [((1380,604,1440,648),(187,14)),((1466,604,1544,648),(186,30))]:
 assert not np.any(cliff[y0:y1,x0:x1]);arr[y0:y1,x0:x1]=metano[y0-dy:y1-dy,x0-dx:x1-dx]
arr[628:648,1430:1474]=metano[595:615,1248:1292]
# Une saillie tronquée de la capture 27 : module complet de sol Métano,
# sans transformation, n'affecte ni l'objet ni les couches supérieures.
arr[1752:1784,664:696]=metano[640:672,584:616]
patch27={}
for cy in range(1752//8,1784//8):
 for cx in range(664//8,696//8):
  old=reference[cy*8:cy*8+8,cx*8:cx*8+8];new=arr[cy*8:cy*8+8,cx*8:cx*8+8];m=np.any(old!=new,axis=2)
  if m.any():
   p=np.zeros((8,8,4),np.uint8);p[m]=new[m];patch27[cx,cy]=p
patch51={}
for cy in range(584//8,(648+7)//8):
 for cx in range(1376//8,(1544+7)//8):
  old=reference[cy*8:cy*8+8,cx*8:cx*8+8]; new=arr[cy*8:cy*8+8,cx*8:cx*8+8]
  m=np.any(old!=new,axis=2)
  if m.any():
   assert not np.any(m & (cliff[cy*8:cy*8+8,cx*8:cx*8+8]!=0))
   p=np.zeros((8,8,4),np.uint8); p[m]=new[m]; patch51[cx,cy]=p
# Source et destination sont rendues cellule par cellule depuis les vraies séquences.
bank={};cache={}
def tile(fr):
 name=fr.get('Sheet',''); xy=fr['TexLoc']; key=(name,xy['X'],xy['Y'])
 if not name:return None
 if key not in cache:
  if name not in bank:
   data=(B/'game/Content/Tile'/f'{name}.tile').read_bytes(); size,n=struct.unpack_from('<ii',data); assert size==8
   bank[name]=(data,{struct.unpack_from('<iiq',data,8+i*16)[:2]:struct.unpack_from('<iiq',data,8+i*16)[2] for i in range(n)})
  data,index=bank[name]; off=index[xy['X'],xy['Y']]; n=struct.unpack_from('<q',data,off)[0];cache[key]=Image.open(io.BytesIO(data[off+8:off+8+n])).convert('RGBA')
 return cache[key]
def get_region(path, cells51, region52):
 c51={k:[Image.new('RGBA',(8,8)) for _ in range(4)] for k in cells51}; c52={k:[Image.new('RGBA',(8,8)) for _ in range(4)] for k in region52}
 with gzip.open(path,'rb') as f:
  assert f.read(3)==b'\xef\xbb\xbf'
  for li,l in enumerate(ijson.items(f,'Object.Layers.item')):
   for cells, group in ((cells51,c51),(region52,c52)):
    for (cx,cy) in cells:
     for anim in l['Tiles'][cx][cy].get('Layers',[]):
      fs=anim.get('Frames',[])
      if not fs:continue
      if len(fs)>1 and (cx,cy) in region52:assert len(fs)==4 and anim['FrameLength']==10,(path,li,cx,cy)
      for frame in range(4):
       im=tile(fs[frame%len(fs)])
       if im:
        if (cx,cy) in cells51 and li>0:
         assert not np.any((cells51[cx,cy][:,:,3]>0)&(np.asarray(im)[:,:,3]>0)),(path,li,cx,cy)
        if (cx,cy) in region52 and li>8:
         assert not np.any(np.asarray(im)[:,:,3]),(path,'couche supérieure',li,cx,cy)
        group[cx,cy][frame].alpha_composite(im)
 return c51,c52
region52={(cx,cy):None for cx in range(132,135) for cy in range(42,65)} # x1056..1079
refpath=B/'payload/reverie_centre.rsground.gz'
c51,c52=get_region(refpath,{**patch51,**patch27},region52)
def region_image(cells,phase):
 out=Image.new('RGBA',(24,184))
 for (cx,cy),frames in cells.items():out.alpha_composite(frames[phase],(cx*8-1056,cy*8-336))
 return np.array(out)
phases=[region_image(c52,i) for i in range(4)]
assert np.array_equal(phases[0],reference[336:520,1056:1080])
points=[(336,0),(346,1),(354,2),(362,3),(374,4),(384,3),(398,1),(405,0),(416,2),(425,3),(437,4),(451,2),(463,0),(472,1),(484,3),(496,4),(507,2),(514,1),(520,0)]
newphases=[p.copy() for p in phases]
for y in range(336,520):
 d=int(round(np.interp(y,*zip(*points))))
 if d:
  for i in range(4):newphases[i][y-336,:16]=phases[i][y-336,d:16+d]
patch52={}
for cy in range(42,65):
 for cx in range(132,134):
  sx=(cx-132)*8;sy=(cy-42)*8
  old=[p[sy:sy+8,sx:sx+8] for p in phases];new=[p[sy:sy+8,sx:sx+8] for p in newphases]
  m=np.logical_or.reduce([np.any(o!=n,axis=2) for o,n in zip(old,new)])
  if m.any():
   ts=[]
   for n in new:
    p=np.zeros((8,8,4),np.uint8);p[m]=n[m];ts.append(p)
   patch52[cx,cy]=ts
# Banque unique ; dédupliquer sans changer les durées ni les couleurs.
atlas=[];lookup={}
def add(p):
 key=p.tobytes()
 if key not in lookup:lookup[key]=len(atlas);atlas.append(Image.fromarray(p))
 return lookup[key]
p51={k:[add(p)] for k,p in {**patch51,**patch27}.items()};p52={k:[add(p) for p in ps] for k,ps in patch52.items()}
header=8+16*len(atlas);body=bytearray();recs=[];sheet=Image.new('RGBA',(256,8*((len(atlas)+31)//32)))
for i,im in enumerate(atlas):
 x,y=i%32,i//32;q=io.BytesIO();im.save(q,format='PNG');dat=q.getvalue();recs.append((x,y,header+len(body)));body+=struct.pack('<q',len(dat))+dat;sheet.paste(im,(x*8,y*8))
tilebytes=struct.pack('<ii',8,len(atlas))+b''.join(struct.pack('<iiq',*r) for r in recs)+body
(O/f'{N}.tile').write_bytes(tilebytes);sheet.save(O/f'{N}.png')
# Contrôle phase et non-régression pour chaque carte originale, puis patch de deux seules couches.
results=[]
for path in sorted((B/'payload').glob('*.gz')):
 print('Vérification',path.name,flush=True)
 c51,c52=get_region(path,{**patch51,**patch27},region52)
 for cell,phs in c51.items():
  cx,cy=cell;m={**patch51,**patch27}[cell][:,:,3]>0;ref=reference[cy*8:cy*8+8,cx*8:cx*8+8]
  for im in phs:assert np.array_equal(np.asarray(im)[m],ref[m]),(path,cell,'51 différent')
 for i in range(4):assert np.array_equal(region_image(c52,i),phases[i]),(path,i,'52 différent')
 raw=gzip.decompress(path.read_bytes()).decode('utf-8'); dec=json.JSONDecoder();splices=[]
 for layer,patch in [('Base',p51),('Objects Over',p52)]:
  st=raw.index('"Name":"'+layer+'"');pos=raw.index('"Tiles":[',st)+len('"Tiles":[')
  for cx in range(200):
   col,end=dec.raw_decode(raw,pos); relevant=[(y,v) for (x,y),v in patch.items() if x==cx]
   if relevant:
    orig=json.loads(raw[pos:end]); touched={y for y,_ in relevant}
    for cy,idxs in relevant:
     cell=col[cy]
     if not cell:cell.update({'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1})
     cell.setdefault('Layers',[]).append({'Frames':[{'Sheet':N,'TexLoc':{'X':ix%32,'Y':ix//32}} for ix in idxs], 'FrameLength':10 if len(idxs)==4 else 60})
     assert cell['Layers'][:-1]==orig[cy].get('Layers',[])
     assert not orig[cy] or {k:v for k,v in cell.items() if k!='Layers'}=={k:v for k,v in orig[cy].items() if k!='Layers'}
    assert all(orig[y]==col[y] for y in range(len(col)) if y not in touched)
    splices.append((pos,end,json.dumps(col,ensure_ascii=False,separators=(',',':'))))
   pos=end
   if cx<199:assert raw[pos]==',';pos+=1
 parts=[];pos=0
 for lo,hi,s in sorted(splices):parts.extend([raw[pos:lo],s]);pos=hi
 parts.append(raw[pos:]); modified=''.join(parts).encode('utf8'); compressed=gzip.compress(modified,compresslevel=6,mtime=0)
 dest=O/'payload'/path.name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(compressed);assert gzip.decompress(compressed)==modified
 results.append({'carte':path.name,'sha256':hashlib.sha256(modified).hexdigest()})
assert len(results)==10
# Aperçus comparatifs et quatre phases réelles du nouveau rivage.
def panel(label1,label2,a,b,scale=4):
 a=Image.fromarray(a).resize((a.shape[1]*scale,a.shape[0]*scale),Image.Resampling.NEAREST);b=Image.fromarray(b).resize(a.size,Image.Resampling.NEAREST)
 out=Image.new('RGB',(a.width*2,a.height+25),'white');d=ImageDraw.Draw(out);d.text((5,5),label1,fill='black');d.text((a.width+5,5),label2,fill='black');out.paste(a,(0,25));out.paste(b,(a.width,25));return out
panel('v0.5.7','Reprise locale',reference[565:665,1368:1560],arr[565:665,1368:1560]).save(O/'escalier51-avant-apres.png')
panel('v0.5.7 phase 0','Reprise locale phase 0',reference[320:550,1028:1108],(lambda b:(b.__setitem__((slice(336,520),slice(1056,1080)),newphases[0]),b)[1])(reference.copy())[320:550,1028:1108],3).save(O/'rive52-avant-apres.png')
im=Image.new('RGBA',(24*4,184));
for i,p in enumerate(newphases):im.alpha_composite(Image.fromarray(p),(i*24,0))
im.resize((24*4*4,184*4),Image.Resampling.NEAREST).save(O/'rive52-quatre-phases.png')
manifest={'base':base_sha,'etat':'local non publié, validation moteur et autres captures restent à faire','escalier':{'donneur':[764,1074,844,1118],'destination':[1380,586,1544,648],'elargissement_pixels':8,'modules_metano':[{'source':[1193,590,1253,634],'destination':[1380,604,1440,648]},{'source':[1280,574,1358,618],'destination':[1466,604,1544,648]},{'source':[1248,595,1292,615],'destination':[1430,628,1474,648]}],'cases':len(patch51),'pixels':int(sum(np.count_nonzero(p[:,:,3]) for p in patch51.values()))},'rive':{'destination':[1056,336,1072,520],'deplacement_max_pixels':4,'phases':4,'duree_frames':10,'cases':len(patch52),'pixels':int(sum(np.count_nonzero(p[0][:,:,3]) for p in patch52.values()))},'chemin27':{'destination':[664,1752,696,1784],'source_metano':[584,640,616,672],'cases':len(patch27),'pixels':int(sum(np.count_nonzero(p[:,:,3]) for p in patch27.values()))},'tuiles':len(atlas),'cartes':results}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
panel('v0.5.7','Reprise locale',reference[1728:1845,635:770],arr[1728:1845,635:770]).save(O/'chemin27-avant-apres.png')
with zipfile.ZipFile(R/'sauvegarde-reprise-arrondie-27-51-52-local.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for p in O.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(O))
 z.write(R/'preparer-arrondis-27-51-52.py','preparer-arrondis-27-51-52.py')
panel('v0.5.7','Reprise locale',reference[1728:1845,635:770],arr[1728:1845,635:770]).save(O/'chemin27-avant-apres.png')
with zipfile.ZipFile(R/'sauvegarde-reprise-arrondie-27-51-52-local.zip') as z:assert z.testzip() is None
print('PASS',json.dumps(manifest,ensure_ascii=False),flush=True)
