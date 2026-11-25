#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import hashlib,json
D=Path(__file__).resolve().parents[1];dest=D/'Kit-Destiny-Drapeaux-Foyers-Bibliotheque.zip'
fo=('Drapeaux','Cheminées','Rayonnages','Calques','Cliff-lumiere');items=[p for x in fo for p in (D/x).rglob('*') if p.suffix in ('.png','.json')]
items.extend(D/t for t in ('Lisez-moi.md','Verification-atelier.json','Verification-graphique.json'))
assert all(p.is_file() for p in items)
a=json.loads((D/'Verification-atelier.json').read_text()); assert a['statut']=='PASS' and a['sha256_atelier']==hashlib.sha256((D.parent/'Guilde-Destiny-Drapeaux-Foyers-Bibliotheque.html').read_bytes()).hexdigest()
assert json.loads((D/'Verification-graphique.json').read_text())['statut']=='PASS'
with ZipFile(dest,'w',compression=ZIP_DEFLATED,compresslevel=8) as z:
    for p in sorted(items):
        z0=ZipInfo(p.relative_to(D).as_posix(),(2026,11,18,12,0,0));z0.compress_type=ZIP_DEFLATED;z0.external_attr=0o100644<<16;z.writestr(z0,p.read_bytes())
with ZipFile(dest) as z: assert z.testzip() is None and len(z.namelist())==len(items)
print(dest.name, len(items),'fichiers,',dest.stat().st_size,'octets')
