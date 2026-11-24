#!/usr/bin/env python3
"""Embed the atlas and each PNG and MP3: works in a file or a sandboxed iframe."""
from pathlib import Path
from base64 import b64encode
import json,re
D=Path(__file__).resolve().parents[1];S=D/'Sources';C=D/'Calques'
p=(S/'Page.html').read_text();a=json.loads((D/'Atlas.json').read_text());
# Cloud banks are a separate, reversible overlay. Do not change the geography or itinerary file.
nuages=json.loads((S/'Nuages.json').read_text()); zone_ids=set(nuages['zones']);sites={s['id']:s for s in a['sites']}
assert not {'reve','mer'}&zone_ids and zone_ids<=set(a['regions'])
assert [sites[k]['area'] for k in nuages['circuit']]==list(dict.fromkeys(sites[k]['area'] for k in nuages['circuit']))
assert {sites[k]['area'] for k in nuages['circuit']}==zone_ids
assert all(f'cloud{k}' in a['art'] for k in nuages['poses'])
for zone in nuages['zones'].values():
 for x,y,w,pose,dx,dy in zone['bancs']:
  assert 0<=x<a['width'] and 0<=y<a['height'] and w>0 and str(pose) in nuages['poses'] and (dx or dy)
a['nuages']=nuages;a['circuits']['nuages']=nuages['circuit']
def uri(f,mime):return 'data:'+mime+';base64,'+b64encode((C/f).read_bytes()).decode('ascii')
a['images']={k:uri(v,'image/png') for k,v in a['art'].items()};a['son']=uri(a['audio'],'audio/mpeg')
reps={'CSS':(S/'Style.css').read_text(),'JS':(S/'Lecteur.js').read_text(),'DATA':json.dumps(a,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c')}
out=re.sub(r'/\*__(CSS|JS|DATA)__\*/',lambda m:reps[m[1]],p)
output=D/'Carte-Miracle-Destiny.html';output.write_text(out);print(output.name,output.stat().st_size,'octets; carte et média intégrés')
