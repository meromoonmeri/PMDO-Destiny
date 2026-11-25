from pathlib import Path
from lupa import LuaRuntime
R=Path(__file__).resolve().parent;T=R/'travail';city=T/'game/Data/Script/destiny/ground/WaterfallVillageCapital/init.lua';dev=T/'game/Data/Script/destiny/ground/WaterfallVillageCapital_Dev/init.lua';assert city.read_bytes()==dev.read_bytes()
for filename in ['test_visite_marchands.lua','test_entrees_reverie.lua','test_suivi_interieurs_complet.lua']:
 variants=['WaterfallVillageCapital','WaterfallVillageCapital_Dev'] if filename != 'test_suivi_interieurs_complet.lua' else ['WaterfallVillageCapital']
 for v in variants:
  print('TEST',filename,v,flush=True);lua=LuaRuntime(unpack_returned_tuples=True);lua.globals().arg=lua.table_from({1:str(T)});lua.globals().package.path = str(T/'game/Data/Script/?.lua')+';'+lua.globals().package.path;s=(T/'tools/tests'/filename).read_text();s=s.replace('ground/WaterfallVillageCapital/init.lua','ground/'+v+'/init.lua');lua.execute(s)
print('PASS : tests sur doublures, pas en jeu')
