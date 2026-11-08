"""Vérifie pixels, conteneur PMDO .dir et absence de conflit avec 0.5.7.
Ce contrôle ne remplace pas l'ouverture dans l'éditeur ou le jeu.
"""
from pathlib import Path
from PIL import Image
import hashlib,io,json,struct
R=Path(__file__).resolve().parent;conf=json.loads((R/'catalogue-objets-pmu-selection.json').read_text());T={x['path'] for x in json.loads((R/'arbre-057.json').read_text())['tree'] if x['type']=='blob'};ids=set()
for item in conf['objets']:
 name=item['id'];assert name not in ids;ids.add(name);assert 'game/Content/Object/'+name+'.dir' not in T
 path=(R/item['source']).resolve();assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256_source'];src=Image.open(path).convert('RGBA');x,y,w,h=item['frames'][0];expected=src.crop((x,y,x+w,y+h));png=Image.open(R/'staging-objets/import-editeur/Object'/(name+'.1.png')).convert('RGBA');assert png.size==(w,h) and png.tobytes()==expected.tobytes() and png.getchannel('A').getbbox()
 data=(R/'staging-objets/game/Content/Object'/(name+'.dir')).read_bytes();size=struct.unpack_from('<q',data)[0];assert len(data)==8+size+16;im=Image.open(io.BytesIO(data[8:8+size])).convert('RGBA');assert struct.unpack_from('<iiii',data,8+size)==(w,h,0,1)
 premul=bytes(v for r,g,b,a in png.getdata() for v in (r*a//255,g*a//255,b*a//255,a));assert im.size==png.size and im.tobytes()==premul
 print('PASS',name,w,h,'pixels et format .dir')
print('PASS',len(ids),'noms non présents dans la base 0.5.7. Aucun objet installé ni test éditeur.')
