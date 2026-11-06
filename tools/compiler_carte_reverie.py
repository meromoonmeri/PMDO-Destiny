#!/usr/bin/env python3
"""Produit une copie jouable à 11 calques depuis une carte d'édition à 37.
Dépendance : python -m pip install ijson
Exemple : python compiler-carte-reverie.py CARTE_EDITION.rsground DOSSIER_TILES CARTE_JEU_NOUVELLE.rsground
Ne remplace jamais le fichier source ou une destination existante.
"""
from pathlib import Path
import json,re,sqlite3,struct,sys,tempfile
try: import ijson
except ImportError: raise SystemExit('Installer ijson : python -m pip install ijson')

BOUNDS=(0,2,5,8,12,16,20,24,28,32,37)

def compile_map(source: Path,tile_dir: Path,destination: Path):
 source=source.resolve();tile_dir=tile_dir.resolve();destination=destination.resolve()
 if not source.is_file() or not tile_dir.is_dir():raise ValueError('Carte source ou dossier de planches absent.')
 if destination==source or destination.exists():raise ValueError('Destination existante ou identique à la source : aucun écrasement.')
 banks={}
 for p in tile_dir.glob('Reverie_WV_*.tile'):
  with p.open('rb') as f:
   hdr=f.read(8)
   if len(hdr)!=8:raise ValueError('Planche tronquée : '+p.name)
   size,n=struct.unpack('<ii',hdr)
   if size!=8 or n<0:raise ValueError('En-tête de planche invalide : '+p.name)
   raw=f.read(16*n)
   if len(raw)!=16*n:raise ValueError('Index tronqué : '+p.name)
   banks[p.stem]={struct.unpack_from('<ii',raw,16*i) for i in range(n)}
 if len(banks)!=14:raise ValueError('Il faut exactement les 14 banques Reverie_WV_ autonomes.')
 raw=source.read_bytes();starts=list(re.finditer(rb'"Layers"\s*:\s*\[\s*\{\s*"Name"\s*:',raw))
 if len(starts)!=1:raise ValueError('Structure des couches non reconnue : arrêt sans écrasement.')
 start=raw.find(b'[',starts[0].start());matches=list(re.finditer(rb'\]\s*,\s*"AssetName"\s*:',raw[start:]))
 if len(matches)!=1:raise ValueError('Fin des couches ambiguë : arrêt sans écrasement.')
 end=start+matches[0].start()+1;prefix=raw[:start];suffix=raw[end:]
 pattern=rb'("AssetName"\s*:\s*)"WaterfallVillageCapital_Dev"';suffix,n=re.subn(pattern,rb'\1"WaterfallVillageCapital"',suffix)
 if n!=1:raise ValueError('La source doit être la carte WaterfallVillageCapital_Dev.')
 width=height=None;frame_count=0;records=0
 destination.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='reverie-compiler-') as tmp:
  con=sqlite3.connect(Path(tmp)/'cells.sqlite3');con.execute('PRAGMA journal_mode=OFF');con.execute('PRAGMA synchronous=OFF');con.execute('CREATE TABLE cells (g INTEGER, cell INTEGER, origin INTEGER, payload TEXT, PRIMARY KEY(g,cell,origin)) WITHOUT ROWID')
  with source.open('rb') as fi:
   if fi.read(3)!=b'\xef\xbb\xbf':fi.seek(0)
   count=0
   for i,layer in enumerate(ijson.items(fi,'Object.Layers.item')):
    if i>=37:raise ValueError('Plus de 37 calques : regroupement annulé.')
    if layer['Layer']!=0 or layer['Visible'] is not True:raise ValueError(f'Calque {i+1} masqué ou d’un autre niveau : regroupement refusé.')
    if width is None:
     width=len(layer['Tiles']);height=len(layer['Tiles'][0]) if width else 0
    if width<=0 or height<=0 or len(layer['Tiles'])!=width or any(len(col)!=height for col in layer['Tiles']):raise ValueError('Dimensions incohérentes.')
    g=next(g for g in range(10) if BOUNDS[g]<=i<BOUNDS[g+1]);rows=[]
    for x,col in enumerate(layer['Tiles']):
     for y,t in enumerate(col):
      if set(t)-{'AutoTileset','Associates','Layers','NeighborCode'} or t.get('AutoTileset','') or t.get('Associates',[]) or t.get('NeighborCode',-1)!=-1:raise ValueError(f'Case non compatible avec l’empilement : {i},{x},{y}')
      ls=t.get('Layers',[])
      if not ls:continue
      for anim in ls:
       if not isinstance(anim.get('FrameLength'),int) or anim['FrameLength']<=0:raise ValueError('Durée d’animation invalide.')
       for frame in anim['Frames']:
        name=frame['Sheet']
        if not name:continue
        loc=frame['TexLoc'];xy=(loc['X'],loc['Y'])
        if name not in banks or xy not in banks[name]:raise ValueError(f'Tuile absente des 14 banques : {name} {xy}')
        frame_count+=1
      rows.append((g,x*height+y,i,json.dumps(ls,ensure_ascii=False,separators=(',',':'))));records+=1
    con.executemany('INSERT INTO cells VALUES (?,?,?,?)',rows);con.commit();count+=1
   if count!=37:raise ValueError(f'Il faut 37 calques d’édition, trouvé : {count}.')
  created=False
  try:
   handle=destination.open('xb');created=True
   with handle as f:
    f.write(prefix);f.write(b'[')
    for g in range(11):
     if g:f.write(b',')
     name=('Composite %02d — anciens calques %02d–%02d'%(g+1,BOUNDS[g]+1,BOUNDS[g+1])) if g<10 else 'Fringe (vide : rendu supérieur conservé)'
     f.write(('{"Name":'+json.dumps(name,ensure_ascii=False)+',"Layer":'+('0' if g<10 else '4')+',"Visible":true,"Tiles":[').encode())
     rows=iter(con.execute('SELECT cell,payload FROM cells WHERE g=? ORDER BY cell,origin',(g,)));current=next(rows,None)
     for x in range(width):
      if x:f.write(b',')
      f.write(b'[')
      for y in range(height):
       if y:f.write(b',')
       cell=x*height+y;seq=[]
       while current is not None and current[0]==cell:seq.extend(json.loads(current[1]));current=next(rows,None)
       if seq:f.write(b'{"AutoTileset":"","Associates":[],"Layers":'+json.dumps(seq,ensure_ascii=False,separators=(',',':')).encode()+b',"NeighborCode":-1}')
       else:f.write(b'{}')
      f.write(b']')
     if current is not None:raise ValueError('Données de cellules restantes.')
     f.write(b']}')
    f.write(b']');f.write(suffix)
  except Exception:
   if created:destination.unlink(missing_ok=True)
   raise
  finally:con.close()
 print(f'Copie créée : {width}×{height}, 11 calques, {records} cellules sources, {frame_count} références. Source inchangée.')

if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit('Usage : python compiler-carte-reverie.py CARTE_EDITION.rsground DOSSIER_TILES CARTE_JEU_NOUVELLE.rsground')
 compile_map(*(Path(x) for x in sys.argv[1:]))
