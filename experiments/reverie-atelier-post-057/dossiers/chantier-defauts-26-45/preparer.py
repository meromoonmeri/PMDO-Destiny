from pathlib import Path
import requests,json,hashlib,concurrent.futures,zipfile
R=Path(__file__).resolve().parent;D=R/'base';sha='97847f618dd16d99f9475e75b74242c247146631';api='https://api.github.com/repos/meromoonmeri/PMDO-Destiny'
r=requests.get(api+'/git/trees/'+sha+'?recursive=1',timeout=90);r.raise_for_status();tree=r.json();assert not tree['truncated'];names=['WaterfallVillageCapital','WaterfallVillageCapital_Dev','reverie_centre','reverie_nord','reverie_residentiel','reverie_etang','reverie_centre_Dev','reverie_nord_Dev','reverie_residentiel_Dev','reverie_etang_Dev'];sel={'payload/'+n+'.rsground.gz' for n in names}
items=[x for x in tree['tree'] if x['type']=='blob' and (x['path'] in sel or x['path'].startswith('game/Content/Tile/Reverie_') and x['path'].endswith('.tile'))];assert sum(x['path'] in sel for x in items)==10

def fetch(x):
 p=x['path'];dest=D/p;url='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+sha+'/'+requests.utils.quote(p,safe='/');r=requests.get(url,timeout=150);r.raise_for_status();b=r.content
 assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'],p
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:paths=list(ex.map(fetch,items))
with zipfile.ZipFile(R/'sauvegarde-v055-cartes-banques.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in paths:z.write(D/p,p)
 z.writestr('base.json',json.dumps({'commit':sha,'fichiers':[{'path':a['path'],'blob':a['sha']} for a in items]},indent=2))
with zipfile.ZipFile(R/'sauvegarde-v055-cartes-banques.zip') as z:assert z.testzip() is None
print('PASS sauvegarde CRC et blobs :',len(paths),'ressources',flush=True)
