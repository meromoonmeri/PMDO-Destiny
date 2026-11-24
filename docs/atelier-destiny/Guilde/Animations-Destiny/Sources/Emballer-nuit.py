#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,zipfile
from PIL import Image
import numpy as np

O=Path(__file__).resolve().parent.parent;G=O.parent;A=O/'Etoffes-animees';ATELIER=G/'Guilde-Destiny-Nuit-Vivante.html';KIT=O/'Kit-Nuit-Vivante-Destiny.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_bytes())

def main():
 index=load(A/'Index-etoffes.json');assert len(index['images'])==12
 for row in index['images']:
  src=A/row['carte'];test=A/row['boucle_PNG'];image=Image.open(src);apng=Image.open(test);assert sha(src)==row['empreinte'];assert apng.n_frames==16 and int(apng.info['loop'])==0
  for i,(x,y,w,h) in enumerate(row['rectangle_images']):
   apng.seek(i);assert apng.info['duration']==row['ms_par_image'];assert np.array_equal(np.asarray(apng.convert('RGBA')),np.asarray(image.crop((x,y,x+w,y+h)))),(row['id'],i)
 night=load(O/'Index-nuit-et-poteaux.json');rooms=night['rooms'];assert len(rooms)==15 and night['nb_poteaux']==42
 for room,folder in zip(rooms,sorted((O/'Calques-nuit').glob('??-*')),strict=True):
  assert folder.name[3:]==room['salle'].removeprefix('guilde_destiny_');files=list(folder.glob('*.png'));assert len(files)==11
  for f in files:
   with Image.open(f) as im:assert list(im.size)==room['dimensions'] and im.mode=='RGBA'
 payload={p.relative_to(O).as_posix():p for root in ('Etoffes-animees','Lianes-de-poteaux','Calques-nuit') for p in (O/root).rglob('*') if p.is_file()}
 for p in [O/'Lisez-moi.md',ATELIER,O/'Index-nuit-et-poteaux.json',O/'Extrait-Nuit-Vivante.mp4']:payload[p.name]=p
 for x in [O/'Tests-nuit-vivante.json']:
  if x.exists():assert load(x)['statut']=='PASS';payload[x.name]=x
 with zipfile.ZipFile(KIT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for path,p in sorted(payload.items()):z.write(p,path)
 with zipfile.ZipFile(KIT) as z:assert z.testzip() is None and set(z.namelist())==set(payload)
 report=dict(statut='PASS',salles=15,poteaux=night['nb_poteaux'],bourgeons=night['nb_bourgeons'],calques_png=165,animations=12,frames_par_animation=16,apng_equivalents_aux_planches=True,sha_atelier=sha(ATELIER),sha_zip=sha(KIT),fichiers_zip=len(payload),jeu_modifie=False)
 (O/'Verification-kit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('PASS · 12 APNG identiques aux planches à 16 images, 165 calques, ZIP',KIT.stat().st_size,'octets',flush=True)
if __name__=='__main__':main()
