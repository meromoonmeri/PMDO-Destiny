"""Assemble one self-contained UTF-8 HTML document. No runtime requests."""
from pathlib import Path
import json,base64
D=Path(__file__).resolve().parents[1];S=D/'Sources'
meta=json.loads((D/'Calques/Animation.json').read_text())
def pack(o):
    if isinstance(o,list):
        for v in o:pack(v)
    elif isinstance(o,dict):
        for v in list(o.values()):pack(v)
        if 'fichier' in o:
            file=D/o['fichier'];m={'.png':'image/png','.mp3':'audio/mpeg'}[file.suffix]
            o['uri']='data:'+m+';base64,'+base64.b64encode(file.read_bytes()).decode()
pack(meta)
html=(S/'Page.html').read_text()
for k,v in {'STYLE':(S/'Style.css').read_text(),'ENGINE':(S/'Moteur.js').read_text(),'SCRIPT':(S/'Lecteur.js').read_text(),
            'ASSETS':json.dumps(meta,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')}.items():
    assert html.count('/*__'+k+'__*/')==1
    html=html.replace('/*__'+k+'__*/',v)
out=D/'Carte-Miracle-En-Action.html';out.write_text(html,encoding='utf-8');print(f'{out.name}: {out.stat().st_size:,} bytes')
