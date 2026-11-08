from pathlib import Path
from PIL import Image
import gzip,json,copy,sys,gc,struct,io
R=Path('/home/user/chantier-deplacement-arbres-bassin');F=Path('/home/user/chantier-corrections-bassin-55');P=Path('/home/user/chantier-corrections-bassin-53-54');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader
journal53=json.loads((P/'journal-corrections.json').read_text());trees=[('ouest-haut',97,253,-2,-1),('ouest-milieu',97,262,-2,-1),('ouest-bas',98,272,-3,-1),('est',158,263,0,-3)];sheet='Reverie_Geo_08_Batiments_objets';r=SheetReader(P/'banques'/(sheet+'.tile'));tem={(sx,sy):r.get_tile(sx,sy) for sx in range(124,134) for sy in range(15,24)};tem={k:v for k,v in tem.items() if v is not None};r.close();assert len(tem)==76
# Repair straight grass seams uncovered by moving the eastern tree, using the
# same native grass tile as candidate 55; patches apply only to Base.
rground=SheetReader(P/'banques/Reverie_Geo_01_Sol_herbe.tile');grass=rground.get_tile(39,218);assert grass;rground.close()
coords=set()
for x in (1283,1284):
 for y in range(2127,2160):coords.add((x,y))
for y in (2159,2160):
 for x in range(1252,1285):coords.add((x,y))
for y in range(2160,2193):coords.add((1251,y))
for y in range(2160,2168):coords.add((1252,y))
patch={}
for x,y in sorted(coords):
 xy=(x//8,y//8)
 if xy not in patch:patch[xy]=Image.new('RGBA',(8,8))
 patch[xy].putpixel((x%8,y%8),grass.getpixel((x%8,y%8)))
unique={};imgs=[];patchidx={}
for xy,img in sorted(patch.items()):
 raw=img.tobytes()
 if raw not in unique:unique[raw]=len(imgs);imgs.append(img)
 patchidx[xy]=unique[raw]
parts=[]
for img in imgs:
 b=io.BytesIO();img.save(b,format='PNG');buf=b.getvalue();parts.append(struct.pack('<q',len(buf))+buf)
off=8+16*len(imgs);head=bytearray(struct.pack('<ii',8,len(imgs)))
for i,b in enumerate(parts):head+=struct.pack('<iiq',i,0,off);off+=len(b)
bank=R/'banques';bank.mkdir(exist_ok=True);bankfile=bank/'Reverie_Correction_Deplacement_Bassin.tile';bankfile.write_bytes(head+b''.join(parts))
reader=SheetReader(bankfile)
for i,img in enumerate(imgs):assert reader.get_tile(i,0).tobytes()==img.tobytes()
reader.close()
out=R/'candidat/payload';out.mkdir(parents=True,exist_ok=True);logs=[]
for variant,name in enumerate(('reverie_etang.rsground.gz','reverie_etang_Dev.rsground.gz')):
 doc=json.loads(gzip.decompress((F/'candidat/payload'/name).read_bytes()).decode('utf-8-sig'));o=doc['Object'];layers={l['Name']:l['Tiles'] for l in o['Layers']};changes={};stats={};readers={}
 def get(f):
  n=f.get('Sheet','')
  if not n:return None
  if n not in readers:readers[n]=SheetReader((F/'banques' if (F/'banques'/(n+'.tile')).exists() else P/'banques')/(n+'.tile'))
  loc=f['TexLoc'];return readers[n].get_tile(loc['X'],loc['Y'])
 def remember(l,x,y):
  k=(l,x,y)
  if k not in changes:changes[k]=copy.deepcopy(layers[l][x][y])
 def haspixels(l,x,y):
  for sub in layers[l][x][y].get('Layers',[]):
   for f in sub.get('Frames',[]):
    im=get(f)
    if im and im.getchannel('A').getbbox():return True
  return False
 # Retire the prior artificial cliff overlays in these four zones; all other 53–55 work remains.
 for c in journal53['cartes'][variant]['modifications']:
  if c['layer']!='Objects Over':continue
  x,y=c['x'],c['y'];assert layers['Objects Over'][x][y]==c['apres'],(name,'patch differs',x,y)
  remember('Objects Over',x,y);layers['Objects Over'][x][y]=copy.deepcopy(c['avant'])
 # Grass assembly seams revealed by the displacement: only add masked pixels to Base.
 for (x,y),idx in patchidx.items():
  remember('Base',x,y);v=copy.deepcopy(layers['Base'][x][y]);
  if not v:v={'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1}
  v.setdefault('Layers',[]).append({'Frames':[{'Sheet':'Reverie_Correction_Deplacement_Bassin','TexLoc':{'X':idx,'Y':0}}],'FrameLength':60});layers['Base'][x][y]=v
 # Remove exactly the tree frames, including shared cells with other sprites.
 for label,x0,y0,dx,dy in trees:
  removed=0;missing=[]
  for (sx,sy) in tem:
   x=x0+sx-124;y=y0+sy-15;v=layers['Objects'][x][y];subs=v.get('Layers',[]);sel=[];keep=[]
   for sub in subs:
    frames=sub.get('Frames',[])
    if len(frames)==1 and frames[0].get('Sheet')==sheet and frames[0].get('TexLoc')=={'X':sx,'Y':sy}:sel.append(sub)
    else:keep.append(sub)
   assert len(sel)<=1
   if sel:
    remember('Objects',x,y);n=copy.deepcopy(v);n['Layers']=keep;layers['Objects'][x][y]=n;removed+=1
   else:missing.append((x,y,sx,sy))
  expected=4 if label=='ouest-haut' else 0;assert len(missing)==expected,(label,missing)
  stats[label]={'de': [x0,y0], 'vers':[x0+dx,y0+dy], 'fragments_retires':removed,'fragments_reconstitues':missing}
 # Insert entire native tree behind any pre-existing sprites, never discard them.
 for label,x0,y0,dx,dy in trees:
  for (sx,sy),im in tem.items():
   x=x0+dx+sx-124;y=y0+dy+sy-15;v=layers['Objects'][x][y];remember('Objects',x,y);n=copy.deepcopy(v)
   if not n:n={'AutoTileset':'','Associates':[],'Layers':[],'NeighborCode':-1}
   n.setdefault('Layers',[]).insert(0,{'Frames':[{'Sheet':sheet,'TexLoc':{'X':sx,'Y':sy}}],'FrameLength':60})
   layers['Objects'][x][y]=n
 # A nearby animated flower would otherwise overlap the relocated tree.
 # Translate its entire 3x3 cell pattern 8px left: all frame lists and durations are copied unchanged.
 flower={(x,y):copy.deepcopy(layers['Objects Anim'][x][y]) for x in range(95,98) for y in range(260,263)}
 for (x,y),v in flower.items():
  assert len(v.get('Layers',[]))==1 and len(v['Layers'][0]['Frames'])==3
  assert all(f.get('Sheet')=='Reverie_Geo_13_Objets_frames' for f in v['Layers'][0]['Frames'])
 for y in range(260,263):assert not layers['Objects Anim'][94][y].get('Layers')
 for x,y in flower:
  remember('Objects Anim',x,y);layers['Objects Anim'][x][y]={}
 for (x,y),v in flower.items():
  remember('Objects Anim',x-1,y);assert not layers['Objects Anim'][x-1][y].get('Layers');layers['Objects Anim'][x-1][y]=v
 # Update east collision footprint: preserve any cliff/other object and keep the original
 # source collision shape for the moved tree. West remains in the already blocked forest.
 x0,y0,dx,dy=158,263,0,-3;obs=o['obstacles'];obs_old={};orig={}
 for sx,sy in tem:
  x=x0+sx-124;y=y0+sy-15;orig[(sx,sy)]=obs[x][y]['Tags']
 dest={(x0+dx+sx-124,y0+dy+sy-15):orig[(sx,sy)] for sx,sy in tem}
 other=['Cliffs','River','Layer 4','Objects Under','Objects Under Anim','Objects','Objects Anim','Objects Over','Objects Over Anim','Fringe']
 for (sx,sy),tag in orig.items():
  x=x0+sx-124;y=y0+sy-15
  if tag!=1 or (x,y) in dest:continue
  if any(haspixels(l,x,y) for l in other):continue
  if obs[x][y]['Tags']==1:
   obs_old[(x,y)]=copy.deepcopy(obs[x][y]);obs[x][y]['Tags']=0
 for (x,y),tag in dest.items():
  if tag==1 and obs[x][y]['Tags']==0:
   if (x,y) not in obs_old:obs_old[(x,y)]=copy.deepcopy(obs[x][y])
   obs[x][y]['Tags']=1
 # Destination is not altered on other data, and the map retains object ordering and IDs.
 mods=[{'layer':l,'x':x,'y':y,'avant':old,'apres':layers[l][x][y]} for (l,x,y),old in sorted(changes.items()) if old!=layers[l][x][y]]
 obsmods=[{'x':x,'y':y,'avant':old,'apres':obs[x][y]} for (x,y),old in sorted(obs_old.items()) if old!=obs[x][y]]
 data=b'\xef\xbb\xbf'+json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode()
 with (out/name).open('wb') as fp:
  with gzip.GzipFile(fileobj=fp,mode='wb',mtime=0) as gz:gz.write(data)
 logs.append({'carte':name,'arbres':stats,'calques':mods,'collisions':obsmods})
 print(name,'cases calques',len(mods),'collisions',len(obsmods),'arbres',stats,flush=True)
 for rdr in readers.values():rdr.close()
 del doc,o,layers,data,obs;gc.collect()
(R/'journal-deplacement.json').write_text(json.dumps({'cartes':logs},ensure_ascii=False,indent=2))
