#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image
import hashlib,json
O=Path(__file__).resolve().parents[1];I=json.loads((O/'Index.json').read_text());byid={(v['modele'],v['palette']):v for v in I['variantes']}
check=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
atlas=Image.new('RGBA',(528,960));cells={}
for row,p in enumerate(I['palettes']):
 for col,m in enumerate(I['modeles']):
    v=byid[(m['id'],p['id'])];f=O/v['png'];assert check(f)==v['sha256'];im=Image.open(f).convert('RGBA');x=176*col+(176-im.width)//2;y=96*(row+1)-im.height-7
    atlas.alpha_composite(im,(x,y));cells[v['id']]=[x,y,*im.size]
f=O/'Atlas-IA-30.png';atlas.save(f,optimize=True)
for v in I['variantes']:
 x,y,w,h=cells[v['id']];assert atlas.crop((x,y,x+w,y+h)).tobytes()==Image.open(O/v['png']).convert('RGBA').tobytes()
(O/'Cases-atlas.json').write_text(json.dumps({'image':f.name,'dimensions':[528,960],'cases':cells},ensure_ascii=False,indent=2)+'\n')
zip_path=O/'Kit-Halcyon-Creations-IA.zip';files={v['png'] for v in I['variantes']}|{m['hd'] for m in I['modeles']}
assert len(files)==33
files|={'Atlas-IA-30.png','Cases-atlas.json','Index.json','Index.csv','Lisez-moi.md','Planche-Creations-IA.png','Verification-graphique.json','Verification-atelier.json','Sources/Manifest-generation.json'}
with ZipFile(zip_path,'w',ZIP_DEFLATED, compresslevel=8) as z:
 for n in sorted(files):z.write(O/n,'Destiny-Mobilier-Halcyon-IA/'+n)
with ZipFile(zip_path) as z:
 assert z.testzip() is None and len(z.namelist())==42
print(zip_path.name,'·',zip_path.stat().st_size,'octets · 42 fichiers vérifiés')
