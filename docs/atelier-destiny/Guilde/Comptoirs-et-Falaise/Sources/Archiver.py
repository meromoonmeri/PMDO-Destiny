#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import hashlib,json

P=Path(__file__).resolve().parents[1]; dst=P/'Kit-Destiny-Comptoirs-et-Falaise.zip'
content=[f for d in ('PNG-1x','Braseros','Falaise') for f in (P/d).rglob('*.png')]
content += [P/name for name in ['Planche-Comptoirs.png','Atlas-Comptoirs-1x.png','Cases-Atlas.json','Index-Comptoirs.json','Implantations.json','Releve-Cliff.json','Provenance-cliff.json','Verification-graphique.json','Verification-atelier.json','Lisez-moi.md']]
html=P.parent/'Guilde-Destiny-Comptoirs-et-Falaise.html'
assert len(content)==49 and all(f.is_file() for f in content)
assert json.loads((P/'Verification-graphique.json').read_text())['statut']=='PASS'
v=json.loads((P/'Verification-atelier.json').read_text());assert v['statut']=='PASS' and v['sha256_atelier']==hashlib.sha256(html.read_bytes()).hexdigest()
with ZipFile(dst,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(content):
        e=ZipInfo(f.as_posix().removeprefix(P.as_posix()+'/'),(2026,11,18,12,0,0));e.compress_type=ZIP_DEFLATED;e.external_attr=0o100644<<16
        z.writestr(e,f.read_bytes())
with ZipFile(dst) as z:assert z.testzip() is None and len(z.namelist())==len(content) and not any(n.endswith(('.lua','.rsground','.exe')) for n in z.namelist())
print(dst.name, dst.stat().st_size,'octets,',len(content),'fichiers, SHA256',hashlib.sha256(dst.read_bytes()).hexdigest())
