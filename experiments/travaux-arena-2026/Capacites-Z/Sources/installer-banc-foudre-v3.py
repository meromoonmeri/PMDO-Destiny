#!/usr/bin/env python3
from pathlib import Path
import shutil,sys
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';S=H/'Capacites-Z/Sources';kind=sys.argv[1];B=H/('.cache/destiny-test/backup-'+kind+'-v3')
assert kind in ('giga','electro') and not B.exists()
paths=['Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs']
if kind=='giga':
 P=H/'Capacites-Z/Prototypes/Giga-Tonnerre/Generation-PMDO';skill='ten_million_volt_thunderbolt';intro='intro-halo-banc-pikachu.lua';test='test-giga-tonnerre-v3.lua';module='test_giga_v3';lua='giga-tonnerre-charge.lua';parts=['GigaTonnerre_Charge.dir','GigaV3_Colonne.dir'];beam='GigaV3_Colonne.beam';paths+=['Content/Chara/25.chara']
else:
 P=H/'Capacites-Z/Prototypes/Electro-Surf-Survolte/Generation-PMDO';skill='stoked_sparksurfer';intro='intro-halo-banc-raichu-alola.lua';test='test-electro-surf-v3.lua';module='test_electro_v3';lua='electro-surf-v3-charge.lua';parts=['ElectroSurfV3_Charge.dir','ElectroSurfV3_Impact.dir'];beam='ElectroSurfV3_Sphere.beam'
paths+=['Data/Skill/'+skill+'.json']
for item in paths:
 p=G/item
 if p.exists():q=B/item;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(P/(skill+'-v3-test-only.json'),G/'Data/Skill'/(skill+'.json'))
if kind=='giga':shutil.copy2(P/'25-banc-casquette-poses-statiques.chara',G/'Content/Chara/25.chara')
for n in parts:shutil.copy2(P/n,G/'Content/Particle'/n)
shutil.copy2(P/beam,G/'Content/Beam'/beam)
e=G/'Data/Script/origin/event_battle.lua';e.write_text(e.read_text()+'\n'+(S/lua).read_text())
shutil.copy2(S/intro,G/'Data/Script/destiny/ground/intro_halo/init.lua');shutil.copy2(S/test,G/'Data/Script/origin'/(module+'.lua'))
d=G/'Data/Script/origin/services/debug_tools/init.lua';txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require(\'origin.'+module+'\').jouer() end) end )\n'+txt[ix:];d.write_text(txt)
for item in ['SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs']:
 p=G/item
 if p.exists():p.unlink()
(B/'ajouts.txt').write_text('\n'.join(['Content/Particle/'+n for n in parts]+['Content/Beam/'+beam,'Data/Script/origin/'+module+'.lua']))
print(kind, 'installé temporairement',B)
