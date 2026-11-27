#!/usr/bin/env python3
"""Audit statique de toutes les fiches natives de la copie PMDO : ne prouve pas leur comportement en jeu."""
import json,csv,collections
from pathlib import Path
G=Path.home()/'.cache/destiny-test/game/PMDO-Destiny/Data/Skill';out=Path('/home/user/Capacites-Z/Inventaire'); rows=[]
for p in sorted(G.glob('*.json')):
 try:
  a=json.loads(p.read_text(encoding='utf-8-sig'))['Object']; h=a.get('HitboxAction') or {};typ=h.get('$type','').split(',')[0].split('.')[-1]
  rows.append({'id':p.stem,'nom_jeu':a.get('Name',{}).get('DefaultText',''),'released':a.get('Released',False),'action':typ,'portee':h.get('Range',''),'forme':h.get('HitArea',''),'rayons':h.get('Rays',''),'largeur':h.get('WideAngle',''),'stop_hit':h.get('StopAtHit',''),'stop_mur':h.get('StopAtWall',''),'cibles':h.get('TargetAlignments',''),'tuiles':h.get('HitTiles',''),'son_action':h.get('ActionFX',{}).get('Sound','')})
 except (KeyError,ValueError,TypeError) as e:print('Non lu',p.name,str(e))
with (out/'Audit-zones-attaques-PMDO.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Fiches',len(rows),'types',collections.Counter(r['action'] for r in rows))
