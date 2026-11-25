#!/usr/bin/env python3
"""Verify the exact masks and package the integration art; reference inputs stay out of the ZIP."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parents[1];geo=D.parent/'Terres-EoS-Magenta'/'Sources'; b='Destiny-Style-DS-Magenta-1112x732.png';alpha='Destiny-Style-DS-Transparent-1112x732.png';h='Destiny-Style-DS-Magenta-5560x3660.png'; rev='Reverie-Style-DS-Apercu.png'
idx=np.asarray(Image.open(geo/'Index-terres-validees.png')); s=np.asarray(Image.open(D/b)); a=np.asarray(Image.open(D/alpha)); water=np.asarray(Image.open(geo/'Eaux-validees.png'))>0
assert np.array_equal(a[...,3],(idx>0).astype(np.uint8)*255)
assert np.array_equal(np.asarray(Image.open(D/'Calques/Index-terres-1112x732.png')),idx)
assert np.array_equal(np.asarray(Image.open(D/'Calques/Masque-eaux-1112x732.png'))>0,water)
assert np.array_equal(s[idx>0],a[idx>0,:3]) and np.array_equal(np.all(s==[255,0,255],axis=2),idx==0)
assert np.array_equal(np.asarray(Image.open(D/h)),np.repeat(np.repeat(s,5,axis=0),5,axis=1))
coords=json.loads((D/'Replacer-les-terres.json').read_text()); assert len([x for x in coords['lieux'] if x['existe_dans_le_projet']])==8
assert coords['ancres_de_rendu']['Reverie_Town']['ancre_racines_atlas']==[150,551]
files=[D/x for x in [b,h,alpha,rev,'Replacer-les-terres.json','Verification.json','Lisez-moi.md']]+sorted(D.glob('Calques/*.png'))+sorted(D.glob('Terres-separees/**/*.png'))
bundle=D/'Kit-Destiny-Style-DS.zip'
with ZipFile(bundle,'w',ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:z.write(f,f.relative_to(D).as_posix())
with ZipFile(bundle) as z:
 assert z.testzip() is None and len(z.namelist())==65 and {p.relative_to(D).as_posix() for p in files}==set(z.namelist())
print('OK:',len(files),'fichiers dans le kit;',bundle.stat().st_size,'octets; côtes, eaux, clé et zoom vérifiés.')
