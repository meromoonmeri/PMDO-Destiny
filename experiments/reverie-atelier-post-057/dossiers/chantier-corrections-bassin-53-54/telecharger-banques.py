import gzip,json,pathlib,collections,requests,hashlib,concurrent.futures,urllib.parse
R=pathlib.Path('/home/user/chantier-corrections-bassin-53-54');j=json.loads(gzip.decompress((R/'original-jeu.rsground.gz').read_bytes()).decode('utf-8-sig'))['Object'];names=set()
for l in j['Layers']:
 for x in range(90,180):
  for y in range(225,325):
   for a in l['Tiles'][x][y].get('Layers',[]):
    for f in a.get('Frames',[]):
     if f['Sheet']:names.add(f['Sheet'])
tree={x['path']:x for x in json.loads(pathlib.Path('/home/user/chantier-lostwood-amapola/arbre-destiny.json').read_text())['tree'] if x['type']=='blob'};s='ee39156a24f350b67e81740478be8505f4ff1a05'
def f(name):
 p=f'game/Content/Tile/{name}.tile';x=tree[p];r=requests.get('https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+s+'/'+urllib.parse.quote(p,safe='/'),timeout=45);r.raise_for_status();b=r.content;assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'];q=R/'banques'/f'{name}.tile';q.parent.mkdir(exist_ok=True);q.write_bytes(b);return name
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:out=list(ex.map(f,sorted(names)))
print('Banques vérifiées',len(out),out)
