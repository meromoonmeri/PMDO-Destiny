#!/usr/bin/env python3
"""Extrait sans transformation les bandes PNG d'un sprite PMU historique.
Usage : python exporter-sprite-pmu.py 25 dossier_vide
Sortie : images d'origine et manifeste. Ceci n'est PAS un CharSheet PMDO.
"""
import argparse,hashlib,io,json,struct,zipfile
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent
anims=['Idle','Walk','Attack','AttackArm','AltAttack','SpAttack','SpAttackCharge','SpAttackShoot','Hurt','Sleep']
dirs=['Down','Left','Up','Right','DownLeft','UpLeft','UpRight','DownRight']
p=argparse.ArgumentParser();p.add_argument('identifiant',type=int,choices=range(751),metavar='ID');p.add_argument('sortie',type=Path);a=p.parse_args()
if a.sortie.exists() and any(a.sortie.iterdir()):raise SystemExit('Refus : le dossier de sortie doit être vide.')
with zipfile.ZipFile(R/'pmu_reference/sprites-pmu-2014-original.zip') as z:b=z.read('Sprites/Sprite%d.sprite'%a.identifiant)
def i32(off):return struct.unpack_from('<i',b,off)[0]
def getstr(off):
 n=0;shift=0
 while True:
  v=b[off];off+=1;n|=(v&127)<<shift
  if not v&128:break
  shift+=7;assert shift<=28
 return b[off:off+n].decode('utf8'),off+n
count=i32(0);offset=4;forms=[]
for _ in range(count):
 name,offset=getstr(offset);position=i32(offset);size=i32(offset+4);offset+=8;forms.append((name,position,size))
head=offset;output=[]
for name,position,size in forms:
 off=head+position;end=off+size;assert 0<=off<=end<=len(b)
 for anim in anims:
  for direction in (dirs if anim!='Sleep' else ['Down']):
   frames=i32(off);length=i32(off+4);off+=8;assert frames>=0 and length>=0 and off+length<=end
   if length:
    data=b[off:off+length];im=Image.open(io.BytesIO(data));im.load();assert frames>0 and im.width%frames==0
    # Le nom de forme PMU est stocké en donnée, jamais interpolé dans un chemin.
    filename='forme%02d_%s_%s.png'%(forms.index((name,position,size)),anim,direction)
    output.append((filename,data,{'forme':name,'animation':anim,'direction':direction,'frames':frames,'largeur_frame':im.width//frames,'hauteur_frame':im.height,'sha256_png':hashlib.sha256(data).hexdigest()}))
   else:assert frames==0
   off+=length
 assert off==end
assert output
a.sortie.mkdir(parents=True,exist_ok=True)
for name,data,rec in output:(a.sortie/name).write_bytes(data)
meta={'source_commit':'c25c01f9879369647cd5a19731b2e4e5acd33e67','sprite_id':a.identifiant,'sha256_sprite':hashlib.sha256(b).hexdigest(),'bandes':[{**r,'fichier':n} for n,_,r in output],'avertissement':'Bandes source PMU exactes, non converties en personnage PMDO ; pivots et cadences non établis.'}
(a.sortie/'MANIFESTE.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(len(output),'bandes PNG originales extraites et vérifiées ; pas de conversion PMDO.')
