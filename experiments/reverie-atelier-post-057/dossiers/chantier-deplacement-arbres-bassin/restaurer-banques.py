from pathlib import Path
import gzip,json,requests,urllib.parse,hashlib,concurrent.futures
R=Path('/home/user/chantier-deplacement-arbres-bassin'); F=Path('/home/user/chantier-corrections-bassin-55');P=Path('/home/user/chantier-corrections-bassin-53-54');C='ee39156a24f350b67e81740478be8505f4ff1a05';d=json.loads(gzip.decompress((F/'candidat/payload/reverie_etang.rsground.gz').read_bytes()).decode('utf-8-sig'))['Object'];names=set()
for l in d['Layers']:
 for col in l['Tiles']:
  for v in col:
   for a in v.get('Layers',[]):
    for f in a.get('Frames',[]):
     if f.get('Sheet'):names.add(f['Sheet'])
print('banques de la carte',len(names),sorted(names),flush=True)
s=requests.Session();u=f'https://api.github.com/repos/meromoonmeri/PMDO-Destiny/git/trees/{C}?recursive=1';r=s.get(u,timeout=90);r.raise_for_status();resp=r.json();assert not resp.get('truncated');index={x['path']:x for x in resp['tree'] if x['type']=='blob'}
result=[]
def fetch(n):
 p=f'game/Content/Tile/{n}.tile';meta=index.get(p)
 if not meta:
  assert any((x/'banques'/f'{n}.tile').exists() for x in (F,R)),n
  return n,'local'
 target=P/'banques'/f'{n}.tile'
 def verify(b):return len(b)==meta['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==meta['sha']
 if target.exists() and verify(target.read_bytes()):return n,'existant vérifié'
 url='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+C+'/'+urllib.parse.quote(p,safe='/');resp=requests.get(url,timeout=90);resp.raise_for_status();b=resp.content;assert verify(b),p;target.write_bytes(b);return n,'téléchargé vérifié'
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 for x in ex.map(fetch,sorted(names)):print(x,flush=True)
