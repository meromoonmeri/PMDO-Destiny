from pathlib import Path
import json,gzip,gc,copy
R=Path('/home/user/chantier-raccords-et-pmu');D=Path('/home/user/chantier-deplacement-arbres-bassin');j=json.loads((R/'journal-raccords.json').read_text());
for entry in j['cartes']:
 name=entry['carte'];b=json.loads(gzip.decompress((D/'candidat/payload'/name).read_bytes()).decode('utf-8-sig'));a=json.loads(gzip.decompress((R/'candidat/payload'/name).read_bytes()).decode('utf-8-sig'));ba=next(l['Tiles'] for l in b['Object']['Layers'] if l['Name']=='Base');aa=next(l['Tiles'] for l in a['Object']['Layers'] if l['Name']=='Base')
 for v in entry['modifications']:
  x,y=v['x'],v['y'];assert ba[x][y]==v['avant'] and aa[x][y]==v['apres'];aa[x][y]=copy.deepcopy(v['avant'])
 assert a==b;print(name,'PASS',len(entry['modifications']),'cases Base; collisions, entités, autres couches et trames inchangées');del a,b,aa,ba;gc.collect()
