from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json
D=Path(__file__).resolve().parents[1]; G=D/'Generations';
files=[D/n for n in ('Carte-Miracle-Destiny-4.html','Carnet-des-50-lieux.html','Lisez-moi.md','Atlas.json','Brut-Destiny-4-Magenta.png','Desert-et-Glace-Magenta.png','Extension-EoS-Grand-Large.png','Destiny-4-Levee-des-nuages.mp4','Destiny-4-Depart-Voile.png')]
poster=D/'Destiny-4-Ouverture-Givre.png'
if poster.exists():files.append(poster)
report=sorted(D.glob('Verification-*.json'));assert len(report)==4 and all(json.loads(p.read_text())['statut']=='PASS' for p in report);files+=report
files+=sorted(G.glob('*.png'));files += [G/'Extension-EoS'/'Denses'/(n+'.png') for n in ('Ouest-nord','Ouest-sud','Est-nord','Est-sud')]
for k in ['Calques','Sources']:
 files+=sorted(p for p in (D/k).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
assert len(files)==len(set(files));target=D/'Kit-Destiny-4-Grand-Large.zip';tmp=target.with_suffix('.tmp')
with ZipFile(tmp,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(D).as_posix())
with ZipFile(tmp) as z:assert not z.testzip() and z.read(files[0].name)==files[0].read_bytes() and len(z.infolist())==len(files)
tmp.replace(target);print('PASS', len(files),'fichiers',target.stat().st_size,'octets')
