from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json
D=Path(__file__).resolve().parents[1]
files=[D/n for n in ['Carte-Miracle-Destiny-4.html','Lisez-moi.md','Atlas.json','Brut-Destiny-4-Magenta.png','Desert-et-Glace-Magenta.png','Destiny-4-Levee-des-nuages.mp4','Destiny-4-Depart-Voile.png','Destiny-4-Ouverture-Givre.png']];report=sorted(D.glob('Verification-*.json'));assert len(report)==3 and all(json.loads(p.read_text())['statut']=='PASS' for p in report);files+=report
for k in ['Calques','Generations','Sources']:
 files+=sorted(p for p in (D/k).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
target=D/'Kit-Carte-Miracle-Destiny-4.zip';tmp=target.with_suffix('.tmp')
with ZipFile(tmp,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(D).as_posix())
with ZipFile(tmp) as z:
 assert not z.testzip() and z.read(files[0].name)==files[0].read_bytes() and len(z.infolist())==len(files)
tmp.replace(target);print('PASS',len(files),'fichiers,',target.stat().st_size,'octets')
