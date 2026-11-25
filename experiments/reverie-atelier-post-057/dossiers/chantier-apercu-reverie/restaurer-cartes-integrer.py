from pathlib import Path
import json,hashlib,concurrent.futures,urllib.request,urllib.parse,zipfile
R=Path(__file__).resolve().parent;T={x['path']:x for x in json.loads((R/'arbre.json').read_text())['tree'] if x['type']=='blob'};sha='ee39156a24f350b67e81740478be8505f4ff1a05'
names=['maison_equipe_falaise','reverie_electric_home','reverie_fire_home','reverie_grass_home','reverie_hutte_aquatique','reverie_inn','reverie_normal_home','reverie_post_office','reverie_rock_home','reverie_water_home']
paths=['game/Data/Ground/'+n+'.rsground' for n in names]+['game/Data/Script/destiny/ground/'+n+'/init.lua' for n in ['cliffdaytest','cliffdaytest_nuit']]+['payload/'+n+'.rsground.gz' for n in ['reverie_etang','reverie_etang_Dev','reverie_residentiel','reverie_residentiel_Dev','WaterfallVillageCapital','WaterfallVillageCapital_Dev']]+['game/Data/Zone/town02_waterfallvillage.json']
def fetch(p):
 x=T[p];url='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+sha+'/'+urllib.parse.quote(p,safe='/')
 with urllib.request.urlopen(url,timeout=90) as r:b=r.read()
 assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'];f=R/'originaux'/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);return (p,b)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: a=list(ex.map(fetch,paths))
out=R/'sauvegarde-cartes-interieurs-bassin-057.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p,b in a:z.writestr(p,b)
 z.writestr('MANIFESTE.json',json.dumps({'commit':sha,'fichiers':[{'path':p,'git_blob':T[p]['sha'],'sha256':hashlib.sha256(b).hexdigest()} for p,b in a]},indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('Sauvegardé',len(paths),'blobs vérifiés, CRC OK',out.stat().st_size,flush=True)
