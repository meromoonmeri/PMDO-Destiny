#!/usr/bin/env python3
"""Installe ou restaure le banc jetable Patati-Patattrape."""
from pathlib import Path
import shutil,sys
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';S=H/'Capacites-Z/Sources';P=H/'Capacites-Z/Prototypes/Patati-Patattrape/Generation-PMDO';B=H/'.cache/destiny-test/backup-patati-v5-ko-force';mode=sys.argv[1]
if mode=='restore':
 for rel in (B/'saved.txt').read_text().splitlines():
  p=G/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/rel,p);assert p.read_bytes()==(B/rel).read_bytes(),rel
 for rel in (B/'added.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 print('Banc restauré ; originaux comparés.');sys.exit()
assert mode=='install' and not B.exists()
paths=['Data/Skill/lets_snuggle_forever.json','Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs','Data/Status/none.json']
adds=['Content/Particle/PatatiV5_Sac.dir','Data/Script/origin/test_patati.lua','Content/Particle/PatatiV5_Yeux.dir'];assert all(not (G/x).exists() for x in adds)
for rel in paths:
 p=G/rel
 if p.exists():q=B/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (B/x).exists()));(B/'added.txt').write_text('\n'.join(adds))
shutil.copy2(P/'V5/lets_snuggle_forever-v5-test-only.json',G/paths[0]);shutil.copy2(P/'V5/PatatiV5_Sac.dir',G/adds[0]);shutil.copy2(S/'test-patati-v5-ko-force.lua',G/adds[1]);shutil.copy2(P/'V5/PatatiV5_Yeux.dir',G/adds[2]);shutil.copy2(S/'intro-halo-banc-mimiqui.lua',G/paths[3])
e=G/paths[1];e.write_text(e.read_text()+'\n'+(S/'patati-v5-ko-force.lua').read_text())
d=G/paths[2];txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'''  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require('origin.test_patati').jouer() end) end )\n'''+txt[ix:];d.write_text(txt)
for rel in paths[4:6]:(G/rel).unlink(missing_ok=True)
shutil.copy2(P/'V3/none-visuel-temporaire.json',G/'Data/Status/none.json')
print('Banc installé seulement dans la copie isolée.')
