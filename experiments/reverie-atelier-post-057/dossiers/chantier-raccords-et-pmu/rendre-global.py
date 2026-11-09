from pathlib import Path
from PIL import Image
import gzip,json,sys,collections,hashlib
R=Path('/home/user/chantier-raccords-et-pmu');K=Path('/home/user/apercu-global-reverie');D=Path('/home/user/chantier-deplacement-arbres-bassin');F=Path('/home/user/chantier-corrections-bassin-55');P=Path('/home/user/chantier-corrections-bassin-53-54');sys.path.insert(0,'/home/user/destiny-reference/tools');from preview_maps import SheetReader,DirReader
src=R/'candidat/payload/reverie_etang.rsground.gz';data=src.read_bytes();doc=json.loads(gzip.decompress(data).decode('utf-8-sig'));o=doc['Object'];assert len(o['Layers'])==11;w=len(o['Layers'][0]['Tiles']);h=len(o['Layers'][0]['Tiles'][0]);assert (w,h)==(200,500);img=Image.new('RGBA',(w*8,h*8),(0,0,0,0));cache={};missing=collections.Counter();used=collections.Counter();print('Ground',w,h,'SHA256',hashlib.sha256(data).hexdigest(),flush=True)
def tile(f):
 n=f.get('Sheet','')
 if not n:return None
 if n not in cache:
  pp=[d/'banques'/(n+'.tile') for d in (R,D,F,P)];p=next((x for x in pp if x.exists()),None)
  if p is None:missing[n]+=1;return None
  cache[n]=SheetReader(p);assert cache[n].tile_size==8
 t=f['TexLoc'];out=cache[n].get_tile(t['X'],t['Y']);used[n]+=1
 if out is None:missing[f'{n} ({t["X"]},{t["Y"]})']+=1
 return out
for li,l in enumerate(o['Layers']):
 if not l.get('Visible',True):print('hidden',l['Name']);continue
 for x,col in enumerate(l['Tiles']):
  for y,t in enumerate(col):
   for sub in t.get('Layers',[]):
    frames=sub.get('Frames',[])
    if not frames:continue
    im=tile(frames[0])
    if im is not None:img.alpha_composite(im,(x*8,y*8))
 # GroundAnim in this map: MapLoc and ObjectAnim as in GroundAnim.cs.
 for group in o.get('Decorations',[]):
  if group.get('Visible',True) and group.get('Layer',0)==l.get('Layer',li) and not any(later.get('Visible',True) and later.get('Layer',i)==group.get('Layer',0) for i,later in enumerate(o['Layers']) if i>li):
   for a in group.get('Anims',[]):
    assert a['ObjectAnim']['AnimIndex']=='Flowers_Town_1';dec=DirReader.frame0(K/'Flowers_Town_1.dir');loc=a['MapLoc'];img.alpha_composite(dec,(loc['X'],loc['Y']))
 print('calque',li,l['Name'],'ok',flush=True)
if missing:print('manquants',missing);raise SystemExit(1)
for x in cache.values():x.close()
# Transparent regions are retained in PNG, but preview uses a neutral backdrop.
img.save(R/'reverie-etang-candidat-global.png',optimize=True)
summary={'carte':'reverie_etang.rsground.gz','source_sha256':hashlib.sha256(data).hexdigest(),'dimensions_cases':[w,h],'dimensions_pixels':list(img.size),'calques':len(o['Layers']),'banques':sorted(used),'frames_manquantes':dict(missing),'decorations':3,'phase':'première image de chaque séquence ; non synchronisée','limitations':'Rendu statique, pas moteur ; les PNJ des scripts ne sont pas représentés.'}
(R/'preuve-rendu-carte.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print('Rendu créé',flush=True)
