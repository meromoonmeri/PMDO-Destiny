from pathlib import Path
from lupa import LuaRuntime,LuaError
R=Path(__file__).resolve().parent
source=R/'travail/engine/RogueEssence/RogueEssence/Lua/LuaEngine.cs'
s=source.read_text();assert 'importpath.StartsWith("ground."' in s and 'importpath.Any(ch => ch > 127)' in s and 'File.ReadAllText(modulePath, Encoding.UTF8)' in s and 'preload[(object)qualifiedName]' in s
for name in ['caféspindaaccueil','spindacaféétage1','spindacaféétage1salle2']:
 lua=LuaRuntime(unpack_returned_tuples=True);g=lua.globals();pkg=g.package;pkg.path='';pkg.cpath=''
 dummy=lua.eval('function() return {} end')
 for dep in ['origin.common','destiny.suivi_interieurs','destiny.equipe_scene','destiny.cinematique','destiny.meteo_reverie']:pkg.preload[dep]=dummy
 key='destiny.ground.'+name
 try:g.require(key);raise AssertionError('la recherche sans fichier doit échouer')
 except LuaError:pass
 path=R/'travail/game/Data/Script/destiny/ground'/name/'init.lua'
 if not path.exists():path=R/'original/game/Data/Script/destiny/ground'/name/'init.lua'
 compiler=lua.eval('load');loader=compiler(path.read_text(encoding='utf-8-sig'),'@'+str(path));assert loader is not None
 pkg.preload[key]=loader
 result=g.require(key);table=result[0] if isinstance(result,tuple) else result
 assert table['Init'] and table['Enter'] and table['GameLoad']
 pkg.preload[key]=None
 cached=g.require(key);cached=cached[0] if isinstance(cached,tuple) else cached
 assert lua.eval('function(a,b) return rawequal(a,b) end')(cached,table)
 pkg.loaded[key]=None;pkg.preload[key]=loader
 fresh=g.require(key);fresh=fresh[0] if isinstance(fresh,tuple) else fresh
 assert not lua.eval('function(a,b) return rawequal(a,b) end')(fresh,table)
 print('PASS recherche absente, chargement mémoire, cache et rechargement:',name)
print('Simulation Lua uniquement : pas de test Windows / KeraLua ni de compilation C#')
