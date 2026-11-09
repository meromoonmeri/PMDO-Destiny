import json,requests,hashlib,pathlib,zipfile,concurrent.futures
R=pathlib.Path(__file__).parent;J=json.loads((R.parent/'chantier-defauts-46-52/arbre-057.json').read_text());T={x['path']:x for x in J['tree'] if x['type']=='blob'}
paths=['game/Data/Ground/caféspindaaccueil.rsground','game/Data/Ground/spindacaféétage1.rsground','game/Data/Ground/spindacaféétage1salle2.rsground','game/Data/Zone/town02_waterfallvillage.json','game/Data/Script/destiny/ground/caféspindaaccueil/init.lua','game/Data/Script/destiny/ground/spindacaféétage1/init.lua','game/Data/Script/destiny/ground/spindacaféétage1salle2/init.lua','game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua','game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua','game/Data/Script/destiny/suivi_interieurs.lua','game/Data/Script/destiny/equipe_scene.lua','game/Data/Script/destiny/cinematique.lua','game/Data/Script/destiny/meteo_reverie.lua']
paths += [p for p in T if p.startswith('engine/RogueEssence/RogueEssence/') and p.rsplit('/',1)[-1] in ['BaseGroundScene.cs','GroundMap.cs','GameManager.cs','ScriptGameAdventure.cs','GroundScene.cs','LuaEngine.cs','ScriptGameCamera.cs','ZoneManager.cs']]
def get(p):
 e=T[p];r=requests.get('https://raw.githubusercontent.com/meromoonmeri/PMDO-Destiny/ee39156a24f350b67e81740478be8505f4ff1a05/'+requests.utils.quote(p,safe='/'),timeout=90);r.raise_for_status();b=r.content;assert len(b)==e['size'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['sha'];out=R/'original'/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:list(ex.map(get,paths))
with zipfile.ZipFile(R/'sauvegarde-avant-cafe-057.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(R/'original'/p,p)
with zipfile.ZipFile(R/'sauvegarde-avant-cafe-057.zip') as z:assert z.testzip() is None
print('PASS',len(paths),'blobs Git, sauvegarde CRC',flush=True)
