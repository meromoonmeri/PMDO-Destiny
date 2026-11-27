#!/usr/bin/env python3
"""Installer/restaurer séparément chaque banc V4 ; jamais sur le dépôt original."""
from pathlib import Path
import shutil,sys
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';S=H/'Capacites-Z/Sources';mode,kind=sys.argv[1:];assert kind in ('giga','electro');B=H/('.cache/destiny-test/backup-'+kind+'-v5-pmd')
if mode=='restore':
 assert B.exists()
 for item in (B/'saved.txt').read_text().splitlines():
  p=G/item;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/item,p);assert p.read_bytes()==(B/item).read_bytes()
 for item in (B/'added.txt').read_text().splitlines():(G/item).unlink(missing_ok=True)
 print(kind,'restauré et comparé');sys.exit()
assert mode=='install' and not B.exists()
if kind=='giga':
 P=H/'Capacites-Z/Prototypes/Giga-Tonnerre/Generation-PMDO';skill='ten_million_volt_thunderbolt';intro='intro-halo-banc-pikachu.lua';test='test-giga-tonnerre-v3.lua';module='test_giga_v5';lua='giga-tonnerre-charge.lua';parts=['GigaTonnerre_Charge.dir','GigaV5_Colonne.dir'];beam='GigaV5_Colonne.beam';extra=['Content/Chara/25.chara']
else:
 P=H/'Capacites-Z/Prototypes/Electro-Surf-Survolte/Generation-PMDO';skill='stoked_sparksurfer';intro='intro-halo-banc-raichu-alola.lua';test='test-electro-surf-v3.lua';module='test_electro_v5';lua='electro-surf-v5-charge.lua';parts=['ElectroSurfV5_Charge.dir','ElectroSurfV3_Impact.dir'];beam='ElectroSurfV5_Sphere.beam';extra=[]
paths=['Data/Skill/'+skill+'.json','Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs']+extra
adds=['Content/Particle/'+x for x in parts]+['Content/Beam/'+beam,'Data/Script/origin/'+module+'.lua'];assert all(not (G/x).exists() for x in adds)
for rel in paths:
 p=G/rel
 if p.exists():q=B/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (B/x).exists()));(B/'added.txt').write_text('\n'.join(adds))
shutil.copy2(P/(skill+'-v5-test-only.json'),G/paths[0]);
if kind=='giga':shutil.copy2(P/'25-banc-casquette-poses-statiques.chara',G/'Content/Chara/25.chara')
for n in parts:shutil.copy2(P/n,G/'Content/Particle'/n)
shutil.copy2(P/beam,G/'Content/Beam'/beam)
e=G/'Data/Script/origin/event_battle.lua';e.write_text(e.read_text()+'\n'+(S/lua).read_text());shutil.copy2(S/intro,G/'Data/Script/destiny/ground/intro_halo/init.lua')
txt=(S/test).read_text().replace('V3','V5');(G/'Data/Script/origin'/f'{module}.lua').write_text(txt)
d=G/'Data/Script/origin/services/debug_tools/init.lua';txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require(\'origin.'+module+'\').jouer() end) end )\n'+txt[ix:];d.write_text(txt)
for x in ['SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs']:(G/x).unlink(missing_ok=True)
print(kind,'installé en copie isolée')
