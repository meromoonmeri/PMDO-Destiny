#!/usr/bin/env python3
"""Inventaire des capacités Z d'après Poképédia + audit des fiches Destiny.
Usage : python inventorier.py /chemin/vers/PMDO-Destiny
"""
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup
from io import StringIO
import csv, json, sys
import pandas as pd
import requests

OUT=Path(__file__).resolve().parent.parent/'Inventaire'; OUT.mkdir(exist_ok=True)
base=Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/'.cache/destiny-test/game/PMDO-Destiny'
url='https://www.pokepedia.fr/Capacit%C3%A9_Z'
r=requests.get(url,timeout=30,headers={'User-Agent':'Mozilla/5.0'});r.raise_for_status()
soup=BeautifulSoup(r.text,'html.parser'); tables=soup.select('table'); selected={}
for t in tables:
 rows=t.select('tr')
 if not rows: continue
 headers=[e.get_text(' ',strip=True) for e in rows[0].find_all(['th','td'])]
 if headers==['Type','Nom','Cristal Z','Type','Nom','Cristal Z']: selected['generiques']=t
 if headers==['Capacité','Type','Capacité requise','Effet supplémentaire','Cristal Z']: selected['statut']=t
 if headers==['Pokémon','Type','Nom','Cristal Z','Capacité requise']: selected['signatures']=t
if len(selected)!=3: raise RuntimeError(f'Tableaux attendus introuvables: {selected.keys()}')
def typ(cell):
 im=cell.find('img');return im.get('alt','') if im else cell.get_text(' ',strip=True)
def text(cell): return cell.get_text(' ',strip=True).replace('\xa0',' ')
gens=[]
for tr in selected['generiques'].select('tr')[1:]:
 c=tr.find_all('td',recursive=False)
 if len(c)!=6: continue
 for i in (0,3): gens.append(dict(type=typ(c[i]),nom=text(c[i+1]),cristal=text(c[i+2]),pokemon='Tous compatibles',base='Capacité offensive du même type'))
status=[]
for tr in selected['statut'].select('tr')[1:]:
 c=tr.find_all('td',recursive=False)
 if len(c)==5: status.append(dict(nom=text(c[0]),type=typ(c[1]),base=text(c[2]),effet=text(c[3]),cristal=text(c[4])))
# read_html expands rowspans for the signature table; type is restored from crystal.
tab=pd.read_html(StringIO(str(selected['signatures'])))[0]
crystal_types={}
for tr in selected['signatures'].select('tr')[1:]:
 c=tr.find_all('td',recursive=False)
 for cell in c:
  im=cell.find('img',alt=True)
  if im and im.get('alt') in {'Normal','Électrik','Psy','Spectre','Ténèbres','Eau','Roche','Fée','Dragon','Acier'}:
   t=im['alt'];break
 else: t=None
 # rowspan merged with read_html: find crystal by its link title suffix.
 if t:
  for cell in c:
   v=text(cell)
   if v.endswith('zélite'):crystal_types[v]=t
crystal_types.update({'Tokozélite':'Fée','Solgazélite':'Acier','Lunazélite':'Spectre'})
group={}
for _,r in tab.iterrows():
 nom=r['Nom']; crystal=r['Cristal Z']
 row=group.setdefault(nom,dict(type=crystal_types.get(crystal,'À vérifier'),nom=nom,cristal=crystal,pokemon=[],base=r['Capacité requise']))
 row['pokemon'].append(r['Pokémon.1'])
sigs=list(group.values())
for s in sigs:s['pokemon']=' / '.join(s['pokemon'])
assert len(gens)==18 and len(sigs)==17 and len(status)==239,(len(gens),len(sigs),len(status))
assert all(s['type']!='À vérifier' for s in sigs),crystal_types
skills={}
for p in (base/'Data'/'Skill').glob('*.json'):
 try:
  a=json.loads(p.read_text(encoding='utf-8-sig'))['Object'];fr=a['Name']['LocalTexts'].get('fr')
  if fr:skills[fr]=(p,a)
 except (KeyError,ValueError):continue
rows=[]
for family,records in [('Générique',gens),('Signature',sigs)]:
 for r in records:
  p,a=skills.get(r['nom'],(None,None));d=(a or {}).get('Data',{}); h=(a or {}).get('HitboxAction',{})
  rows.append({'famille':family,**r,'id_pmdo':p.stem if p else '', 'nom_anglais':a['Name']['DefaultText'] if a else '', 'fiche_presente':bool(p),'released':a.get('Released') if a else '', 'action':h.get('$type','').split(',')[0].split('.')[-1], 'son_action':h.get('ActionFX',{}).get('Sound',''), 'son_impact':d.get('HitFX',{}).get('Sound',''),'animation_z':'Non créée','test_8_directions':'Non testé','gameplay_z':'Non vérifié'})
assert len(rows)==35 and all(x['fiche_presente'] for x in rows)
for row in rows:
 if row['id_pmdo']=='breakneck_blitz':
  row['animation_z']='V3 expérimentale, charge et impact 18 poses, 2 couches'
  row['test_8_directions']='Capacité expérimentale exécutée en 8 directions, cible placée par script'
  row['gameplay_z']='Test natif partiel : pas de mécanique Z ni menu'
 if row['id_pmdo'] in ('inferno_overdrive','hydro_vortex','gigavolt_havoc','subzero_slammer','bloom_doom','devastating_drake','corkscrew_crash','never_ending_nightmare','savage_spin_out','continental_crush'):
  row['animation_z']='Prototype : impact avec poses générées par IA et action native ou procédurale'
  row['test_8_directions']='Capacité expérimentale exécutée en 8 directions, cible placée par script'
  row['gameplay_z']='Test natif partiel : pas de mécanique Z ni menu'
 if row['id_pmdo']=='tectonic_rage':
  row['animation_z']='Fissures radiales et pointes de terre IA recomposées, sons et tremblement'
  row['test_8_directions']='Carchacrok : huit orientations, trois cibles et témoin, terrain aménagé et lancement scripté'
  row['gameplay_z']='Banc : zone 5x5, dégâts et PP moteur ; règles Z et menu non intégrés'
 if row['id_pmdo']=='all_out_pummeling':
  row['animation_z']='V2 : rafale de traces et impacts abstraits sans mains, 26 poses recomposées orientées'
  row['test_8_directions']='Mackogneur : huit orientations, une cible adjacente et un témoin latéral'
  row['gameplay_z']='Test natif partiel : dégâts uniques, menu, cristal et règles Z non intégrés'
 if row['id_pmdo']=='black_hole_eclipse':
  row['animation_z']='V2 Absol : trou noir centré, 32 poses recomposées, zone 5x5, murs standards cassables'
  row['test_8_directions']='Absol : huit orientations, trois cibles et témoin ; murs intérieurs, extérieur et incassable testés'
  row['gameplay_z']='Banc : murs détruits par événement fiche ; menu, cristal, règles Z et sauvegarde restent à tester'
 if row['id_pmdo']=='genesis_supernova':
  row['animation_z']='Prototype Mew : ciel cosmique et orbite recomposée à partir de ressources IA'
  row['test_8_directions']='Mew dans huit orientations : trois cibles et un témoin, placement et lancement scriptés'
  row['gameplay_z']='Test natif partiel : pas de Champ Psychique, restriction, cristal ni menu Z'
 if row['id_pmdo']=='catastropika':
  row['animation_z']='Prototype signature Pikachu : charge et aura générée par IA'
  row['test_8_directions']='Pikachu exécuté dans 8 directions, cible et lancement scriptés'
  row['gameplay_z']='Test natif partiel : ni restriction signature ni cristal ni menu Z'
def writecsv(name,records):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
writecsv('35-capacites-z-et-audit.csv',rows);writecsv('239-capacites-statut-z.csv',status)
def table(headers,records,keys):
 out=['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']
 for r in records:out.append('| '+' | '.join(str(r.get(k,'')).replace('|','\\|') for k in keys)+' |')
 return '\n'.join(out)
released=sum(1 for r in rows if r['released'])
md='''# Inventaire des capacités Z — Destiny / PMDO\n\n## Périmètre\n\n- **18 attaques génériques** (une par type), **17 capacités signatures distinctes** : 35 capacités nommées au total. Neuf pour Un est une capacité signature de statut, pas une attaque infligeant des dégâts. Certaines signatures sont partagées par plusieurs formes ou Pokémon.\n- La source liste aussi **239 variantes de capacités de statut Z**. Elles figurent toutes dans `239-capacites-statut-z.csv`, avec type, capacité de base, effet Z et cristal. Ce nombre est celui du tableau de Poképédia consulté, pas une preuve que Destiny les gère.\n- Ce sont des règles des jeux principaux de génération VII : la conversion en donjon PMDO et ses conditions (une fois par combat, étage ou expédition, objets, rang, cibles, portée, bonus) restent à concevoir et à tester.\n\n## 18 capacités génériques\n\n'''+table(['Type','Capacité Z','Cristal','ID PMDO'],[r for r in rows if r['famille']=='Générique'],['type','nom','cristal','id_pmdo'])+'''\n\n## 17 capacités signatures\n\n'''+table(['Type','Capacité Z','Porteurs','Capacité requise','Cristal','ID PMDO'],[r for r in rows if r['famille']=='Signature'],['type','nom','pokemon','base','cristal','id_pmdo'])+f'''\n\n## Audit local de Destiny 0.7.8 (données PMDO 0.8.12)\n\n- Les **35 fiches JSON** existent dans `Data/Skill/` ; **{released}/35** sont marquées `Released: true` (les autres sont `false`). Existence d'une fiche ≠ capacité Z utilisable ou animation présente.\n- Les 35 fiches examinées utilisent `AttackAction`, leurs champs `ActionFX.Sound` et `Data.HitFX.Sound` sont vides. Les dégâts ou autres événements déclarés varient : leur présence ne prouve ni un fonctionnement Z complet ni une animation correcte.\n- `35-capacites-z-et-audit.csv` recense les identifiants, noms anglais, états et données de base. Seize prototypes VFX ont été testés en donjon : Turbo-Charge, Pyro-Explosion, Super Tourbillon, Fulguro-Lance, Laser Cryogénique, Pétalexplosion, Chaos Draconique, Vrille Maximum, Appel des Ombres Éternelles, Cocon Fatal, Apocalypse Gigalithique Pikachute Foudroyante Supernova Originelle Trou Noir des Ombres Combo Hyper-Furie et Éruption Géo-Sismique. Les quinze derniers comportent des éléments générés par IA ; Turbo est procédural. Tous ont été testés dans huit orientations avec cibles placées par script. Pétalexplosion a été testée en aire, Super Tourbillon en ligne traversante et Chaos Draconique en cône, chacun sur trois cibles et un témoin. Appel des Ombres expérimente une paire de mains par cible en aire, avec 0 à 3 cibles et huit orientations ; Cocon Fatal vise une case à deux cases, avec un témoin latéral ; Apocalypse Gigalithique utilise une zone décalée à trois cibles et un témoin arrière. Les règles Z et la fluidité finale restent à valider. Supernova Originelle a été testée avec Mew, trois cibles et un témoin dans chaque orientation ; son Champ Psychique reste à implémenter. Trou Noir des Ombres V2 a été testé avec Absol dans une zone centrée de 5 × 5 cases : trois cibles et un témoin par orientation, puis destruction de murs standards et conservation d’un mur extérieur et d’un mur indestructible. Combo Hyper-Furie a été testé avec Mackogneur : impacts abstraits sans mains, une cible adjacente et un témoin par orientation. Éruption Géo-Sismique a été testée avec Carchacrok en zone autour du lanceur, trois cibles et un témoin par orientation. Dix-neuf capacités n’ont pas encore de prototype testé.\n\n## Huit directions et production\n\nChaque capacité aura une fiche de suivi pour les huit orientations : bas, bas-droite, droite, haut-droite, haut, haut-gauche, gauche, bas-gauche. Pour les effets symétriques, une seule animation peut être réutilisée si son rendu est vérifié dans les huit directions ; pour les projectiles, trajectoires, attaques de contact ou cadrages asymétriques, il faut des vues adaptées. Ne pas confondre effets visuels (particules) et animation du corps du Pokémon : les signatures peuvent nécessiter des poses propres à l'espèce.\n\n## Sources\n\n- Poképédia : https://www.pokepedia.fr/Capacit%C3%A9_Z — tableaux génériques, signatures et statut.\n- PMDO, création de capacités : https://wiki.pmdo.pmdcollab.org/Creating_Moves\n- PMDO, ressources VFX directionnelles : https://wiki.pmdo.pmdcollab.org/Modding_Objects_and_VFX\n- PMDO, sprites : https://wiki.pmdo.pmdcollab.org/PMD_Sprite_Format\n\n**État : inventaire et audit statique terminés ; 16 prototypes VFX sur 35 testés dans les huit directions, pas de capacité complète jouable ; 19 capacités restent sans prototype testé.**\n'''
(OUT/'Inventaire-complet.md').write_text(md,encoding='utf-8')
print('OK',len(gens),'génériques',len(sigs),'signatures',len(status),'statut; présents',len(rows),'released',released)
