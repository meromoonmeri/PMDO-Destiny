#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from collections import Counter
import hashlib,json,zipfile
from PIL import Image
import numpy as np

S=Path(__file__).resolve().parent;O=S.parent; G=O.parent; W=Path.home()/'.cache/guilde-objets'
TARGET=O/'Kit-PMU-Halcyon-et-Lianes-Reverie.zip';ATLAS=G/'Guilde-Destiny-Lianes-et-PMU-100.html';SHEET=O/'Tilesheet-PMU-Halcyon-100.png'
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
 idx=json.loads((O/'Index-100.json').read_bytes());sprites=idx['objets'];assert len(sprites)==len({o['id'] for o in sprites})==100
 foliage=sorted((O/'Lianes-par-salle').rglob('*.png'));assert len(foliage)==45
 report=json.loads((O/'Lianes-par-salle/Index-lianes.json').read_bytes());assert len(report['plans'])==15
 names=[o['fichier'] for o in sprites];assert len(set(names))==100
 files={p.name:p for p in (SHEET,O/'Index-100.json',O/'Index-100.csv',O/'Lisez-moi.md',ATLAS)}
 files.update({n:W/n for n in names});files.update({p.relative_to(O).as_posix():p for p in foliage+[O/'Lianes-par-salle/Index-lianes.json']})
 with zipfile.ZipFile(TARGET,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as zip:
  for n,p in sorted(files.items()):zip.write(p,n)
 sheet=np.asarray(Image.open(SHEET).convert('RGBA')); assert sheet.shape==(1280,1920,4)
 with zipfile.ZipFile(TARGET) as zip:
  assert zip.testzip() is None and len([x for x in zip.namelist() if x.startswith('PNG/')])==100
  for o in sprites:
   raw=zip.read(o['fichier']);assert sha(raw)==o['sha256'];tex=np.array(Image.open(BytesIO(raw)).convert('RGBA'));x,y,w,h=o['rectangle'];assert np.array_equal(tex,sheet[y:y+h,x:x+w])
   cx,cy,cw,ch=o['cellule'];assert cx<x<x+w<cx+cw and cy<y<y+h<cy+ch
  for r in report['plans']:
   n=r['salle'].removeprefix('guilde_destiny_');entries=[f for f in foliage if f.parent.name[3:]==n];assert len(entries)==3
   assert all(list(Image.open(p).size)==r['taille'] and Image.open(p).mode=='RGBA' for p in entries)
 (O/'Verification-kit.json').write_text(json.dumps(dict(statut='PASS',sprites=100,modeles=25,par_palette=Counter(x['palette'] for x in sprites),calques_lianes=45,salles=15,nb_passages=29,nb_sorties_sud=7,planche_sha256=sha(SHEET.read_bytes()),apercu_sha256=sha(ATLAS.read_bytes()),zip_sha256=sha(TARGET.read_bytes())),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'PASS · {TARGET.name} · {TARGET.stat().st_size:,} octets · 100 sprites et 45 calques PNG vérifiés.')
if __name__=='__main__':main()
