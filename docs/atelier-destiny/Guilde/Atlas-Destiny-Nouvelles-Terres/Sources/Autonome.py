#!/usr/bin/env python3
"""Embed the illustration and the gazetteer into one independent HTML file."""
from pathlib import Path
from base64 import b64encode
import json
S=Path(__file__).resolve().parent; R=S.parent
m=json.loads((R/'Calques/Atlas.json').read_text()); coords=json.loads((S/'Geographie.json').read_text())

def data(b):return 'data:image/png;base64,'+b64encode(b).decode('ascii')
m['image']=data((R/m.pop('natif')).read_bytes());m['seaways']=data((R/m['layers']['traversees']).read_bytes());pmap={r['id']:r for r in coords['regions']}
for r in m['regions']:
    r['cote']=pmap[r['id']]['cote'];r['aires']=pmap[r['id']].get('aires',[])
for q in m['regions']+m['sites']:q['image']=data((R/q['image']).read_bytes())
for k in ['layers','ordre','couche_originale']:m.pop(k,None)
html=(S/'Page.html').read_text(encoding='utf-8').replace('/*STYLE*/',(S/'Style.css').read_text(encoding='utf-8')).replace('/*SCRIPT*/',(S/'Lecteur.js').read_text(encoding='utf-8')).replace('/*DATA*/',json.dumps(m,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
out=R/'Explorer-Nouvelles-Terres.html';out.write_text(html,encoding='utf-8');print(f'{out.name} : {out.stat().st_size:,} octets')
