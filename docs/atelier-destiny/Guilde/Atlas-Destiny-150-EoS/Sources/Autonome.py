#!/usr/bin/env python3
"""Pack the server app as a single offline HTML file, for file viewers too."""
from base64 import b64encode
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/'Apercu';A=P/'assets'
files={name:'data:image/png;base64,'+b64encode((A/name).read_bytes()).decode() for name in ('Terrain.png','Lieux-150.png','Animations.png','Feuillets-EoS.png','Vignettes-carte.png','Chemins.png')}
state=json.dumps({'index':json.loads((A/'Lieux.json').read_text()),'files':files},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
style=(P/'atlas.css').read_text();script=(P/'atlas.js').read_text()
i=(P/'index.html').read_text();i=i.replace('<link rel="stylesheet" href="atlas.css">','<style>\n'+style+'</style>')
i=i.replace('<script src="atlas.js" defer></script>', '<script>window.atlasLocal='+state+';</script>\n<script>'+script+'</script>')
assert '<script src=' not in i and 'rel="stylesheet"' not in i
out=R/'Atlas-Destiny-EoS-Hors-Ligne.html';out.write_text(i,encoding='utf8');print(out.name,out.stat().st_size)
