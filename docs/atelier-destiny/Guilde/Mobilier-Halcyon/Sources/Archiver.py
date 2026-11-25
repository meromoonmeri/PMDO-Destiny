#!/usr/bin/env python3
"""Paquet graphique autonome : aucune installation, aucune carte de jeu."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
S=Path(__file__).resolve().parent
O=S.parent
Z=O/'Kit-Mobilier-Halcyon-Destiny.zip'
index=json.loads((O/'Index.json').read_text(encoding='utf-8'))
expected={v['png'] for v in index['variantes']}
assert len(expected)==490
files=expected|{v['atlas'] for v in index['variantes']}|{m['source_png'] for m in index['models']}
files|={'Lisez-moi.md','Index.json','Index.csv','Verification-atelier.json','Verification-graphique.json','Planche-10-Palettes.png'}
files|={'Sources/'+name for name in ('Modeles.json','Provenance-brute.json','Palettes.json','Prelever.py','Fabriquer.py')}
with ZipFile(Z,'w',ZIP_DEFLATED,compresslevel=8) as z:
    for filed in sorted(files):
        z.write(O/filed, 'Mobilier-Halcyon-Destiny/'+filed)
with ZipFile(Z) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(files)
    assert len([n for n in z.namelist() if '/PNG-1x/' in n])==490
print(Z.name, '·', Z.stat().st_size, 'octets ·', len(files),'fichiers vérifiés')
