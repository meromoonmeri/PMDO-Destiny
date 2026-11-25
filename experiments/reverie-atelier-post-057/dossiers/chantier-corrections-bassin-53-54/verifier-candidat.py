import gzip,json,hashlib,gc
from pathlib import Path
from collections import Counter
R=Path('/home/user/chantier-corrections-bassin-53-54');j=json.loads((R/'journal-corrections.json').read_text());
for c in j['cartes']:
 old=json.loads(gzip.decompress((R/c['source']).read_bytes()).decode('utf-8-sig'));new=json.loads(gzip.decompress((R/'candidat/payload'/c['destination']).read_bytes()).decode('utf-8-sig'));o=old['Object'];n=new['Object'];assert old['Version']==new['Version'];assert o.keys()==n.keys()
 for k in o:
  if k!='Layers':assert o[k]==n[k],k
 expect={(x['layer'],x['x'],x['y']):x for x in c['modifications']};found=set();
 for a,b in zip(o['Layers'],n['Layers']):
  assert {k:v for k,v in a.items() if k!='Tiles'}=={k:v for k,v in b.items() if k!='Tiles'}
  for x,(ca,cb) in enumerate(zip(a['Tiles'],b['Tiles'])):
   for y,(ta,tb) in enumerate(zip(ca,cb)):
    if ta!=tb:
     key=a['Name'],x,y;assert key in expect,key;assert ta==expect[key]['avant'] and tb==expect[key]['apres'];found.add(key)
 assert found==set(expect);print(c['destination'],'PASS',len(found),'cases',dict(Counter(k[0] for k in found)),'collisions, entités, calques et autres cases inchangés',flush=True)
 del old,new,o,n;gc.collect()
