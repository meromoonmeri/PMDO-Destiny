import requests,concurrent.futures,time
from pathlib import Path
sha='7bd2dc104706571c91a2ea4a3c45282b94eabbb6';repo='meromoonmeri/PMDO-Destiny';root=Path(__file__).parent/'sources'
j=requests.get(f'https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1',timeout=45).json()
if j.get('truncated'):raise SystemExit('Arbre incomplet')
prefixes=['docs/atelier-destiny/Guilde/Falaise-Ombre-et-Lune/','docs/atelier-destiny/Guilde/Bourgeons-PMD/','art/guilde_destiny_reseau/guirlandes_verdure/']
exact=['docs/atelier-destiny/Guilde/Guilde-Destiny-Bourgeons-PMD.html','tools/build_guilde_destiny_reseau.py','tools/build_verdure_sprites_par_salle.py','tools/build_guilde_hd_tiles.py','tools/build_tile_index.py','tools/tests/test_guilde_cliff_integrite.py','tools/tests/test_guilde_destiny_accueil.py']
def want(p):
 return any(p.startswith(x) for x in prefixes) or p in exact or (p.startswith('game/Data/Ground/guilde_') and p.endswith('.rsground')) or (p.startswith('game/Content/Tile/Destiny_GuildeCliff_') and p.endswith('.tile'))
files=[x for x in j['tree'] if x['type']=='blob' and want(x['path'])];print('À récupérer',len(files),'fichiers',sum(x.get('size',0) for x in files),'octets',flush=True)
def get(x):
 p=x['path'];dest=root/p;dest.parent.mkdir(parents=True,exist_ok=True)
 url=f'https://raw.githubusercontent.com/{repo}/{sha}/{requests.utils.quote(p)}'
 for attempt in range(3):
  try:
   r=requests.get(url,timeout=60);r.raise_for_status(); data=r.content
   if len(data)!=x.get('size'):raise ValueError('Taille différente')
   dest.write_bytes(data);return p,None
  except Exception as e:
   if attempt==2:return p,str(e)
   time.sleep(1+attempt)
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex: results=list(ex.map(get,files))
errors=[(p,e) for p,e in results if e];print('Récupérés:',len(results)-len(errors),'erreurs:',len(errors),flush=True)
for p,e in errors:print(p,e,flush=True)
if errors:raise SystemExit(1)
