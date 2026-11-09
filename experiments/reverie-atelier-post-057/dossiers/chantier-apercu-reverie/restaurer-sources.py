from pathlib import Path
import requests,json,hashlib,concurrent.futures,zipfile
R=Path(__file__).resolve().parent;sha='ee39156a24f350b67e81740478be8505f4ff1a05';tree={x['path']:x for x in json.loads((R/'arbre.json').read_text())['tree'] if x['type']=='blob'}
ids=['caféspindaaccueil','spindacaféétage1','spindacaféétage1salle2','reverie_electric_home','reverie_fire_home','reverie_grass_home','reverie_hutte_aquatique','reverie_inn','reverie_normal_home','reverie_post_office','reverie_rock_home','reverie_water_home','reverie_centre','reverie_etang','reverie_nord','reverie_residentiel','WaterfallVillageCapital','maison_equipe_falaise']
paths=['game/Data/Script/destiny/ground/'+n+'/init.lua' for n in ids]+['game/Data/Script/destiny/suivi_interieurs.lua','game/Data/Script/destiny/equipe_scene.lua']+['engine/RogueEssence/RogueEssence/'+p for p in ['Lua/ScriptGameZone.cs','Lua/ScriptSound.cs','Ground/GSceneZone.cs','Scene/GameManager.cs']]
def fetch(p):
 x=tree[p];u='https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/'+sha+'/'+requests.utils.quote(p,safe='/');r=requests.get(u,timeout=90);r.raise_for_status();b=r.content;assert len(b)==x['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==x['sha'];d=R/'originaux'/p;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:paths=list(ex.map(fetch,paths))
with zipfile.ZipFile(R/'sauvegarde-avant-interieurs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(R/'originaux'/p,p)
with zipfile.ZipFile(R/'sauvegarde-avant-interieurs.zip') as z:assert z.testzip() is None
print('PASS',len(paths),'blobs et sauvegarde CRC')
