"""Construit les entrées manquantes depuis la banque existante : une vue source par objet."""
import json,zipfile,base64,io,collections,re,hashlib
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent;archive=Path('/home/user/.cache/guilde-tests/Atelier-8-Sens.zip');
if not archive.exists():
 import requests
 u='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/7bd2dc104706571c91a2ea4a3c45282b94eabbb6/docs/atelier-destiny/Guilde/Mobilier-Posable-8-Sens/Atelier-Immobilier-Destiny-8-Sens.zip';r=requests.get(u,timeout=120);r.raise_for_status();archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(r.content)
html=(P/'sources/docs/atelier-destiny/Guilde/Guilde-Destiny-Bourgeons-PMD.html').read_text();data=json.loads(html.split('<script id="donnees" type="application/json">')[1].split('</script>')[0]);ids={a['id'] for a in data['catalog']};extra=[]
with zipfile.ZipFile(archive) as z:
 t=z.read('Atelier/Banque.js').decode();bank=json.loads(t[len('window.DESTINY_POSE='):].rstrip().removesuffix(';'));assert len(bank['ob'])==1108
 groups=collections.defaultdict(list)
 for a in bank['ob']:
  if a['id'] not in ids:groups[a['v'][0][0]].append(a)
 family={'Auberge de Metano':'halcyon','Halcyon':'halcyon','Halcyon · créations':'halcyonia','Comptoirs & drapeaux':'comptoirs','PMU de Destiny':'pmucomplet','Immobilier natif 0.7.7':'natifcomplet'}
 for page,items in sorted(groups.items()):
  text=z.read(f'Atelier/Page-{page:02d}.js').decode();m=re.fullmatch(r'window\.bankPage\(\d+,"data:image/png;base64,([A-Za-z0-9+/=]+)"\);\s*',text);assert m
  sheet=Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA')
  for obj in items:
   pg,x,y,w,h,ax,ay=obj['v'][0];assert pg==page and 0<=x<x+w<=sheet.width and 0<=y<y+h<=sheet.height
   img=sheet.crop((x,y,x+w,y+h));assert img.getbbox();b=io.BytesIO();img.save(b,format='PNG',optimize=True)
   category='tapis' if obj['gabarit']=='tapis' or 'tapis' in obj['nom'].lower() else 'panneaux' if obj['mur'] else 'meubles'
   extra.append(dict(id=obj['id'],label=obj['nom'],category=category,collection=family[obj['famille']],w=w,h=h,wall=bool(obj['mur']),previewOnly=True,sourceFamille=obj['famille'],m=[base64.b64encode(b.getvalue()).decode()]))
  sheet.close()
assert len(extra)==951
for path in sorted((P.parent/'PMDO-Destiny-guilde/Objets-Interieur-PMD-60').glob('Kit-Objets-Guilde-PMD-*.zip')):
 with zipfile.ZipFile(path) as z:
  manifest=json.loads(z.read('Index.json'))
  for a in manifest['objets']:
   raw=z.read(a['png']);assert hashlib.sha256(raw).hexdigest()==a['sha256'];im=Image.open(io.BytesIO(raw));assert list(im.size)==a['taille_px']
   extra.append(dict(id='creation-pmd-'+str(a['numero']).zfill(3),label=a['nom']+' · '+manifest['titre'],category='tapis' if a['pose']=='tapis' else 'meubles',collection='creations40',w=im.width,h=im.height,wall=False,previewOnly=True,m=[base64.b64encode(raw).decode()]))
assert len(extra)==991 and len({a['id'] for a in extra})==991 and not ids.intersection(a['id'] for a in extra)
(P/'banque-complementaire.json').write_text(json.dumps(extra,ensure_ascii=False,separators=(',',':')),encoding='utf8');print('Ajouts prêts :',len(extra),collections.Counter(a['collection'] for a in extra))
