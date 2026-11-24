"""Make the offline distribution and test that every shipped file survived the ZIP round-trip."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json

r=Path(__file__).resolve().parents[1]
reports=sorted(r.glob('Verification-*.json'));assert len(reports)==4 and all(json.loads(p.read_text())['statut']=='PASS' for p in reports)
assert len(json.loads((r/'Verification-video.json').read_text())['signals'])==5
assert len({e['zone'] for e in json.loads((r/'Verification-video-nuages.json').read_text())['signals']})==9
files=[r/n for n in ('Carte-Miracle-Destiny.html','Carte-Complete-Destiny.png','Archipels-Destiny-Magenta.png','Apercu-Expedition-Destiny.mp4','Ouverture-des-nuages-Destiny.mp4','Apercu-Nuages-Destiny.gif','Atlas.json','Lisez-moi.md')]
files+=reports+sorted(p for p in (r/'Calques').rglob('*') if p.is_file())
files+=sorted(p for p in (r/'Sources').glob('*') if p.suffix in ('.py','.cjs','.js','.html','.css','.json'))
files+=sorted((r/'Generations'/'Archipels').glob('*.png'))
archive=r/'Kit-Carte-Miracle-Destiny.zip';tmp=archive.with_suffix('.tmp')
with ZipFile(tmp,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(r).as_posix())
with ZipFile(tmp) as z:
    assert len(z.infolist())==len(files) and not z.testzip()
    for p in (files[0],files[1],files[2]):assert z.read(p.relative_to(r).as_posix())==p.read_bytes()
tmp.replace(archive)
print(f'PASS : {len(files)} fichiers · {archive.stat().st_size:,} octets · {archive.name}')
