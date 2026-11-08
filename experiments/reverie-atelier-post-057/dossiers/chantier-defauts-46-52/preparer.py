from pathlib import Path
import requests,json,hashlib,concurrent.futures,zipfile
R=Path(__file__).resolve().parent;D=R/'base';sha='ee39156a24f350b67e81740478be8505f4ff1a05';tree=json.loads((R/'arbre-057.json').read_text())['tree'];T={a['path']:a for a in tree if a['type']=='blob'}
old=json.load(open('/home/user/chantier-defauts-26-45/audit-pixel-integral/inventaire-pixel-et-references.json'));names=[n for n in old['banques_utilisees'] if n]+['Reverie_Fond_Transparences_056'];paths=[p for p in T if p.startswith('payload/') and p.endswith('.gz')]+['game/Content/Tile/'+n+'.tile' for n in names]+['tools/build_tile_index.py','engine/RogueEssence/RogueEssence/Dev/ImportHelper.cs','engine/RogueEssence/RogueEssence/Content/Indices/TileIndex.cs','game/Content/ContentParams.xml','base/Content/ContentParams.xml','.github/workflows/build-windows.yml']
assert len([p for p in paths if p.startswith('payload/')])==10
for p in paths:assert p in T,p
def fetch(p):
 x=T[p];url='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+sha+'/'+requests.utils.quote(p,safe='/');r=requests.get(url,timeout=150);r.raise_for_status();b=r.content;assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'],p;d=D/p;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:paths=list(ex.map(fetch,paths))
with zipfile.ZipFile(R/'sauvegarde-057-avant.zip','w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for p in paths:z.write(D/p,p)
 z.writestr('MANIFESTE.json',json.dumps({'commit':sha,'files':[{'path':p,'sha256':hashlib.sha256((D/p).read_bytes()).hexdigest(),'blob':T[p]['sha']} for p in paths]},indent=2,ensure_ascii=False))
with zipfile.ZipFile(R/'sauvegarde-057-avant.zip') as z:assert z.testzip() is None
print('PASS',len(paths),'blobs et archive CRC',flush=True)
