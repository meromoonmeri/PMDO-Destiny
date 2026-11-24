#!/usr/bin/env python3
"""Generate the standalone offline Destiny 4 reader, with no network or server dependencies."""
from pathlib import Path
from base64 import b64encode
import json,re
root=Path(__file__).resolve().parents[1];S=root/'Sources';C=root/'Calques'
a=json.loads((root/'Atlas.json').read_text());view=(S/'Page.html').read_text()
def uri(file,kind):return 'data:'+kind+';base64,'+b64encode((C/file).read_bytes()).decode('ascii')
a['images']={k:uri(f,'image/png') for k,f in a['art'].items()};a['son']=uri(a['audio'],'audio/mpeg')
parts={'CSS':(S/'Style.css').read_text(),'JS':(S/'Lecteur.js').read_text(),'DATA':json.dumps(a,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')}
out=re.sub(r'/\*__(CSS|JS|DATA)__\*/',lambda m:parts[m[1]],view);dest=root/'Carte-Miracle-Destiny-4.html';dest.write_text(out);print(dest.name,dest.stat().st_size,'octets')
