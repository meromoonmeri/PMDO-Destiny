#!/usr/bin/env python3
"""Installe ou restaure le banc jetable Symphonie des Ondines."""
from pathlib import Path
import shutil,sys
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';S=H/'Capacites-Z/Sources';P=H/'Capacites-Z/Prototypes/Symphonie-des-Ondines/Generation-PMDO';B=H/'.cache/destiny-test/backup-symphonie-v1';mode=sys.argv[1]
if mode=='restore':
 for rel in (B/'saved.txt').read_text().splitlines():
  p=G/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/rel,p);assert p.read_bytes()==(B/rel).read_bytes(),rel
 for rel in (B/'added.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 print('Banc restauré ; originaux comparés.');sys.exit()
assert mode=='install' and not B.exists()
paths=['Data/Skill/oceanic_operetta.json','Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs']
adds=['Content/Particle/Ondines_Impact.dir','Content/Particle/Ondines_Charge.dir','Data/Script/origin/test_symphonie.lua','Content/Particle/Ondines_Sphere.beam'];assert all(not (G/x).exists() for x in adds)
for rel in paths:
 p=G/rel
 if p.exists():q=B/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (B/x).exists()));(B/'added.txt').write_text('\n'.join(adds))
shutil.copy2(P/'oceanic_operetta-v1-test-only.json',G/paths[0]);shutil.copy2(P/'Ondines_Impact.dir',G/adds[0]);shutil.copy2(P/'Ondines_Charge.dir',G/adds[1]);shutil.copy2(S/'test-symphonie-ondines.lua',G/adds[2]);shutil.copy2(P/'Ondines_Sphere.beam',G/adds[3]);shutil.copy2(S/'intro-halo-banc-oratoria.lua',G/paths[3])
e=G/paths[1];e.write_text(e.read_text()+'\n'+(S/'symphonie-ondines-charge.lua').read_text())
d=G/paths[2];txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'''  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require('origin.test_symphonie').jouer() end) end )\n'''+txt[ix:];d.write_text(txt)
for rel in paths[-2:]:(G/rel).unlink(missing_ok=True)
print('Banc installé seulement dans la copie isolée.')
