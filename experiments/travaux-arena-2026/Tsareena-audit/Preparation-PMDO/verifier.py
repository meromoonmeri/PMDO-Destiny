#!/usr/bin/env python3
"""Garde-fou de préparation, pas une preuve de conformité ou un import PMDO."""
from pathlib import Path
import argparse, json, xml.etree.ElementTree as ET
from PIL import Image
import numpy as np

root=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('folder',nargs='?',default=str(root/'brouillon-NE-PAS-IMPORTER'));args=ap.parse_args()
p=Path(args.folder); ref=ET.parse(root.parent/'refs-spritecollab/AnimData.xml').getroot();expected={n.findtext('Name'):n for n in ref.find('Anims')};problems=[];checks=[];colors=set()
try:
 actual=ET.parse(p/'AnimData.xml').getroot();items=list(actual.find('Anims')); names=[x.findtext('Name') for x in items]; data={x.findtext('Name'):x for x in items}
 if len(set(names))!=len(names):problems.append('Noms XML dupliqués')
except (FileNotFoundError,ET.ParseError,TypeError,AttributeError) as exc:
 problems.append(f'AnimData.xml absent ou invalide : {exc}');data={}
for name,reference in expected.items():
 node=data.get(name)
 if node is None:
  problems.append('Animation manquante : '+name);continue
 copy=reference.findtext('CopyOf')
 if copy:
  if node.findtext('CopyOf')!=copy:problems.append(f'{name} doit copier {copy}')
  continue
 if node.findtext('CopyOf'):problems.append(f'{name} est une copie mais doit être dessinée');continue
 for key in ('Index','FrameWidth','FrameHeight','RushFrame','HitFrame','ReturnFrame'):
  if node.findtext(key)!=reference.findtext(key):problems.append(f'{name}: {key} diffère de la référence')
 ticks=[x.text for x in node.findall('Durations/Duration')];ref_ticks=[x.text for x in reference.findall('Durations/Duration')]
 if ticks!=ref_ticks:problems.append(f'{name}: durées différentes de Tsareena normale')
 try:w=int(node.findtext('FrameWidth'));h=int(node.findtext('FrameHeight'))
 except (ValueError,TypeError):problems.append(f'{name}: dimensions XML invalides');continue
 if w%2 or h%2:problems.append(f'{name}: les dimensions de cellule doivent être paires')
 images={}
 for kind in ('Anim','Offsets','Shadow'):
  file=p/f'{name}-{kind}.png'
  if not file.exists():problems.append(f'Fichier manquant : {file.name}');continue
  try:images[kind]=Image.open(file).convert('RGBA')
  except Exception as exc:problems.append(f'Fichier illisible : {file.name} ({exc})')
 if 'Anim' in images:
  a=np.asarray(images['Anim']);height,width=a.shape[:2];nframes=len(ticks)
  if width!=w*nframes or height not in (h,8*h):problems.append(f'{name}: dimensions spritesheet incompatibles avec XML')
  if np.any((a[:,:,3]!=0)&(a[:,:,3]!=255)):problems.append(f'{name}: transparence partielle détectée')
  colors.update(map(tuple,a[a[:,:,3]>0,:3].tolist()))
  if name=='Walk' and height==h*8 and width==w*4:
   count=sum(bool(a[r*h:(r+1)*h,c*w:(c+1)*w,3].any()) for r in range(8) for c in range(4));checks.append(f'Walk : {count}/32 cases non vides, cellules {w}×{h}, durées {ticks}')
   if count!=32:problems.append('Walk: des cellules sont vides')
  for kind in ('Offsets','Shadow'):
   if kind in images and images[kind].size!=images['Anim'].size:problems.append(f'{name}-{kind}: taille différente de l’animation')
  if 'Offsets' in images and images['Offsets'].size==images['Anim'].size and width%w==0 and height%h==0:
   off=np.asarray(images['Offsets'])
   # For every cell, require exactly one opaque pure green body marker.
   for rr in range(height//h):
    for cc in range(width//w):
     f=off[rr*h:(rr+1)*h,cc*w:(cc+1)*w];green=(f[:,:,1]==255)&(f[:,:,3]>0)
     if green.sum()!=1:problems.append(f'{name}-Offsets : marqueur centre absent ou multiple, ligne {rr+1} image {cc+1}')
  if 'Shadow' in images and images['Shadow'].size==images['Anim'].size and width%w==0 and height%h==0:
   sh=np.asarray(images['Shadow'])
   for rr in range(height//h):
    for cc in range(width//w):
     f=sh[rr*h:(rr+1)*h,cc*w:(cc+1)*w];white=(f[:,:,0]==255)&(f[:,:,1]==255)&(f[:,:,2]==255)&(f[:,:,3]>0)
     if white.sum()!=1:problems.append(f'{name}-Shadow : centre blanc absent ou multiple, ligne {rr+1} image {cc+1}')
checks.append(f'Palette globale trouvée : {len(colors)} couleurs visibles')
if len(colors)>15:problems.append('Plus de 15 couleurs visibles dans les animations')
# A structural check cannot certify a design, hand offsets, actual engine import or gameplay.
problems.extend(['Validation artistique image par image non réalisée', 'Offsets/ombres et mouvements à contrôler dans PMDO', 'Transformation et intégration Destiny non réalisées', 'Test réel dans PMDO non réalisé'])
report={'etat':'BLOQUÉ – pas prêt à intégrer','dossier':str(p),'verifications':checks,'points_bloquants':problems,'note':'Les vérifications automatiques ne garantissent ni conformité artistique ni compatibilité réelle. Aucun import ou publication.'}
(root/'etat-controle.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(report['etat']);print('\n'.join(checks));print('\n'.join('- '+v for v in problems));raise SystemExit(1 if problems else 0)
