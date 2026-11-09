#!/usr/bin/env python3
"""Restaure les anciens livrables archivés, sans écraser de fichiers locaux."""
from pathlib import Path
import json,hashlib,requests,zipfile,io
here=Path(__file__).resolve().parent;home=Path('/home/user');inv=json.loads((here/'inventaire.json').read_text());proof=json.loads((here/'preuve-push.json').read_text());prefix=proof['prefixe'];base='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+proof['commit']+'/'+prefix
parts=[]
for x in inv['parties']:
 r=requests.get(base+x['nom'],timeout=120);r.raise_for_status();b=r.content
 if len(b)!=x['octets'] or hashlib.sha256(b).hexdigest()!=x['sha256']:raise RuntimeError('Partie invalide : '+x['nom'])
 parts.append(b)
b=b''.join(parts)
if hashlib.sha256(b).hexdigest()!=inv['archive_sha256']:raise RuntimeError('Archive invalide')
with zipfile.ZipFile(io.BytesIO(b)) as z:
 for x in inv['fichiers']:
  rel=Path(x['chemin']);p=home/rel
  if rel.is_absolute() or '..' in rel.parts:raise RuntimeError('Chemin non sûr')
  data=z.read(str(rel))
  if len(data)!=x['taille'] or hashlib.sha256(data).hexdigest()!=x['sha256']:raise RuntimeError('Donnée invalide : '+str(rel))
  if p.exists():
   if hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:print('Fichier différent préservé :',p)
   continue
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);print('Restauré :',p)
print('Terminé sans écrasement.')
