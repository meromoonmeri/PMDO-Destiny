#!/usr/bin/env python3
"""Audit statique des fiches de capacités de la copie PMDO-Destiny.

Le résultat distingue les effets référencés et les effets procéduraux connus de
l'absence de référence directe. Cette dernière ne prouve pas l'absence d'animation
indirecte déclenchée par un statut, un événement natif ou un script.
"""
from pathlib import Path
import csv, json, collections, hashlib, zipfile
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

H=Path.home(); G=H/'.cache/destiny-test/game/PMDO-Destiny'; ROOT=H/'Capacites-Z'; O=ROOT/'Inventaire/Audit-animations-PMDO'; O.mkdir(parents=True,exist_ok=True)
Z={r['id_pmdo'] for r in csv.DictReader((ROOT/'Inventaire/35-capacites-z-et-audit.csv').open(encoding='utf-8-sig'))}
files=sorted((G/'Data/Skill').glob('*.json'))
with zipfile.ZipFile(O/'fiches-source-PMDO.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
 for f in files: archive.write(f,'Skill/'+f.name)
hash_archive=hashlib.sha256((O/'fiches-source-PMDO.zip').read_bytes()).hexdigest()

def traverse(o,path='',ancestry=()):
 if isinstance(o,dict):
  typ=o.get('$type','').split(',')[0].split('.')[-1]
  anc=ancestry+((typ,) if typ else ())
  if isinstance(o.get('AnimIndex'),str) and o['AnimIndex']:
   n=o['AnimIndex']
   # Le type le plus proche l'emporte : un StaticAnim imbriqué dans une
   # WaveMotionAction reste une particule, tandis que ColumnAnim est un rayon.
   kind=next((x for x in reversed(anc) if x in ('ColumnAnim','WaveMotionAction','FiniteOverlayEmitter','StaticAnim','ParticleAnim','EmittingAnim','ProjectileAction','DashAction','ThrowAction','MoveToEmitter','SpinEmitter','FiniteGatherEmitter','ClampEmitter','SwingSwitchEmitter','VortexEmitter')),None)
   sub,ext=('Beam','.beam') if kind in ('WaveMotionAction','ColumnAnim') else ('BG','.dir') if kind=='FiniteOverlayEmitter' else ('Particle','.dir')
   yield ('ref',path+'.AnimIndex',n,sub+'/'+n+ext,(G/'Content'/sub/(n+ext)).is_file())
  if typ=='AfterImageEmitter':yield ('procedural',path,typ,'rémanence du personnage',True)
  if typ in ('BattleScriptEvent','ScriptedConditionEvent'):
   yield ('script',path,str(o.get('Script','')),typ,None)
  for k,v in o.items():yield from traverse(v,path+'.'+k,anc)
 elif isinstance(o,list):
  for i,v in enumerate(o):yield from traverse(v,path+f'[{i}]',ancestry)

def data(f):
 raw=f.read_bytes();o=json.loads(raw.decode('utf-8-sig'))['Object'];t=list(traverse(o)); refs=[x for x in t if x[0]=='ref']; proc=[x for x in t if x[0]=='procedural'];scripts=[x for x in t if x[0]=='script'];bad=[x for x in refs if not x[4]]
 if refs and bad: status='Références présentes, fichier attendu manquant'
 elif refs:status='Effet graphique référencé'
 elif proc:status='Rémanence procédurale, sans fichier graphique direct'
 elif scripts:status='Script à examiner, sans fichier graphique direct'
 else:status='Sans effet graphique directement référencé'
 name=o.get('Name',{});fr=name.get('LocalTexts',{}).get('fr') or name.get('DefaultText','')
 action=o.get('HitboxAction',{}); char=action.get('CharAnim',action.get('CharAnimData',{}));
 return {'id':f.stem,'nom':fr,'anglais':name.get('DefaultText',''),'index':o.get('IndexNum',''),'published':o.get('Released',False),'etat':status,'refs':'; '.join(sorted({x[2] for x in refs})),'fichiers':'; '.join(sorted({x[3] for x in refs})),'absents':'; '.join(sorted({x[3] for x in bad})),'proc':'; '.join(sorted({x[2] for x in proc})),'scripts':'; '.join(sorted({x[2] for x in scripts})),'action':action.get('$type','').split(',')[0].split('.')[-1],'pose':json.dumps(char,ensure_ascii=False,separators=(',',':')) if isinstance(char,dict) else str(char),'sha256':hashlib.sha256(raw).hexdigest()}
allrows=[data(f) for f in files if f.stem not in Z and f.stem!='attack']; released=sorted([x for x in allrows if x['published']],key=lambda x:(x['nom'].casefold(),x['id'])); unavailable=sorted([x for x in allrows if not x['published']],key=lambda x:(x['nom'].casefold(),x['id']));cnt=collections.Counter(x['etat'] for x in released)
fields=['nom','anglais','id','index','published','etat','refs','fichiers','absents','proc','scripts','action','pose','sha256']
with (O/'audit-complet.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,delimiter=';');w.writeheader();w.writerows(released+unavailable)
missing=[x for x in released if x['etat']=='Sans effet graphique directement référencé']; procedural=[x for x in released if x['etat']=='Rémanence procédurale, sans fichier graphique direct'];ref=[x for x in released if x['refs']];uncertain=[x for x in released if x['scripts'] or x['absents']]
assert len(files)==len(allrows)+len(Z)+1
lines=['# Audit des animations des capacités de base PMDO','',f"Source : fiches de la copie isolée PMDO-Destiny, état restauré, {len(files)} fiches JSON. Empreinte SHA-256 de l'archive source : `{hash_archive}`.",'',f"Périmètre principal : {len(released)} capacités publiées (`Released=true`), hors 35 capacités Z et hors action interne `attack`. Les {len(unavailable)} autres fiches hors Z et action interne ne sont pas publiées et figurent à part dans le tableau.",'', '## Résultats de l’audit statique','',f"- {len(ref)} capacités ont au moins une référence directe à une ressource d'effet graphique dans leur fiche.",f"- {len(procedural)} autres ont une rémanence procédurale explicite sans référence directe à un fichier d'effet : "+', '.join(x['nom'] for x in procedural)+'.',f"- {len(missing)} n'ont ni référence directe à une ressource d'effet ni rémanence procédurale détectée ; ce sont des **candidates à vérifier**, pas des absences d’animation prouvées.",f"- {len(uncertain)} ont un script explicite ou une ressource attendue introuvable et demandent une vérification complémentaire.",'','Ces catégories portent sur les effets, pas sur la pose du Pokémon. Les fiches peuvent également déclencher des animations indirectes par les statuts ou le code natif. Les ressources sont vérifiées selon leur type attendu (particule, fond, rayon), mais leur rendu et leur qualité n’ont pas été testés dans le jeu. Une ressource partagée ou une simple image compte comme référence, sans présumer d’une animation unique ou fidèle.','', '## Candidates sans effet graphique directement référencé','']
for x in missing:lines.append('- '+x['nom']+' (`'+x['id']+'`)')
lines += ['', '## Fichiers','', '- `audit-complet.xlsx` : résultats, candidates, effets référencés et fiches non publiées.', '- `audit-complet.csv` : une ligne par capacité hors Z et action interne.', '- `fiches-source-PMDO.zip` : instantané des fiches utilisées.', '- `Capacites-Z/Sources/audit-animations-capacites.py` : méthode reproductible.']
(O/'Synthese.md').write_text('\n'.join(lines)+'\n')
wb=Workbook();ws=wb.active;ws.title='Synthèse'
for line in lines[:15]: ws.append([line.replace('# ','').replace('## ','')])
ws.column_dimensions['A'].width=130
for cell in ws['A']:cell.alignment=Alignment(wrap_text=True,vertical='top')
ws['A1'].font=Font(bold=True,size=16,color='FFFFFF');ws['A1'].fill=PatternFill('solid',fgColor='31506A')
headers=['Nom français','Nom anglais','Identifiant','Index','Publiée','Résultat statique','Animations référencées','Fichiers attendus','Fichiers manquants','Procédural','Script','Action','Pose ou processus','SHA-256 fiche']
def sheet(title,rows):
 s=wb.create_sheet(title);s.append(headers)
 for r in rows:s.append([r[k] for k in fields])
 s.freeze_panes='C2';s.auto_filter.ref=s.dimensions
 widths=[25,24,28,9,10,45,35,48,35,24,24,22,38,25]
 for i,n in enumerate(widths,1):s.column_dimensions[get_column_letter(i)].width=n
 for c in s[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='31506A');c.alignment=Alignment(wrap_text=True)
 for row in s.iter_rows(min_row=2):
  for c in row:c.alignment=Alignment(vertical='top',wrap_text=False)
  if row[5].value=='Sans effet graphique directement référencé':row[5].fill=PatternFill('solid',fgColor='FFF1C7')
sheet('À vérifier',missing);sheet('Rémanence procédurale',procedural);sheet('Effets référencés',ref);sheet('Non publiées',unavailable);sheet('Toutes hors Z',released+unavailable)
wb.save(O/'audit-complet.xlsx')
print('fiches',len(files),'Z exclues',len(Z),'action interne exclue 1','publiées',len(released),'non publiées',len(unavailable));print(cnt);print('scripts ou fichiers manquants',len(uncertain));print('archive SHA256',hash_archive)
