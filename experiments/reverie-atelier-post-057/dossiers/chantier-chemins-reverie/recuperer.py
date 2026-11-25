from pathlib import Path
import requests,hashlib,json,concurrent.futures,zipfile
R=Path('/home/user/chantier-chemins-reverie');D=R/'base';sha='a2db214dc89e675347f670f26594df92158fc9d9';repo='https://api.github.com/repos/meromoonmeri/PMDO-Destiny';j=requests.get(repo+'/branches/wip/reverie-integration-kingambit-cafe',timeout=30).json();assert j['commit']['sha']==sha,j.get('commit');r=requests.get(repo+'/git/trees/'+sha+'?recursive=1',timeout=90);r.raise_for_status();j=r.json();assert not j['truncated'];items=[]
for x in j['tree']:
 p=x['path'];
 if x['type']!='blob':continue
 if p.startswith('payload/') and any(p=='payload/'+n+'.rsground.gz' for n in ['WaterfallVillageCapital','WaterfallVillageCapital_Dev','reverie_centre','reverie_nord','reverie_residentiel','reverie_etang','reverie_centre_Dev','reverie_nord_Dev','reverie_residentiel_Dev','reverie_etang_Dev']):items.append(x)
 if p.startswith('game/Content/Tile/Reverie_Geo_') and p.endswith('.tile') or p=='game/Content/Tile/Reverie_Corrections_Audit.tile' or p.startswith('art/reverie/tilesheets/Reverie_Geo_') and p.endswith('.png') or p=='game/Content/Tile/index.idx' or p=='tools/build_tile_index.py':items.append(x)

def get(x):
 p=x['path'];u='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+sha+'/'+requests.utils.quote(p,safe='/');r=requests.get(u,timeout=100);r.raise_for_status();b=r.content;assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'],p;f=D/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex: paths=list(ex.map(get,items))
with zipfile.ZipFile(R/'sauvegarde-avant-chemins-0.5.0.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(D/p,p)
with zipfile.ZipFile(R/'sauvegarde-avant-chemins-0.5.0.zip') as z:assert z.testzip() is None
print('Sauvegarde',len(paths),'fichiers, empreintes Git et CRC vérifiés',flush=True)
# Référence Halcyon en lecture seule.
j=json.loads(Path('/home/user/halcyon-reference-tree.json').read_text())['tree'];sel={'Data/Ground/metano_town.rsground','Content/Tile/Metano_Town_Base.tile','Content/Tile/Metano_Town_Cliffs.tile','Content/Tile/Metano_Town_Trimmed.tile','Content/Tile/Metano_Town_River.tile','Content/Tile/Metano_Town_Objects.tile'}
for x in j:
 if x['path'] in sel:
  r=requests.get('https://raw.githubusercontent.com/Palikadude/Halcyon/1522c7a8b7a34d70078e11ed605b21d563b0dc51/'+x['path'],timeout=120);r.raise_for_status();b=r.content;assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'];p=R/'metano-reference'/x['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);print('Référence',x['path'],flush=True)
