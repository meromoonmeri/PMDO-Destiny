from pathlib import Path
from lupa import LuaRuntime,LuaError
src=Path('travail/engine/RogueEssence/RogueEssence/Lua/LuaEngine.cs').read_text();block=src[src.index('public void CleanMapScript('):src.index('public void CreateGroundMapScriptDir(',src.index('public void CleanMapScript('))]
needle='String.Format(@"';start=block.index(needle,block.index('try\n'))+len(needle);end=block.index('", MapCurrentScriptSym)',start);script=block[start:end].replace('{0}','CURMAPSCR')
assert 'LuaState["__ground_cleanup_asset"] = mapassetname;' in block and 'finally' in block
for name in ['caféspindaaccueil','spindacaféétage1','spindacaféétage1salle2','reverie_centre',"x';error('injection')--"]:
 l=LuaRuntime(unpack_returned_tuples=True)
 g=l.globals();g.__ground_cleanup_asset=name
 l.execute("""calls=0; CURMAPSCR={Cleanup=function()calls=calls+1 end}; PrintStack=function(e)return e end""")
 g.package.loaded[name]=True;g.package.loaded['destiny.ground.'+name]=True;g.package.loaded['origin.ground.'+name]=True;g.package.loaded['origin.ground.autre']=True
 l.execute(script)
 assert g.calls==1 and g.CURMAPSCR is None and g.package.loaded[name] is None and g.package.loaded['destiny.ground.'+name] is None and g.package.loaded['origin.ground.'+name] is None and g.package.loaded['origin.ground.autre'] is True
 print('PASS nettoyage sans interpolation',repr(name))
try: LuaRuntime().execute('package.loaded.caféspindaaccueil = nil');raise AssertionError('le défaut initial devrait échouer')
except LuaError:print('PASS défaut initial reproduit : code Lua invalide avec accent')
