#!/usr/bin/env python3
"""Installe et restaure uniquement le banc expérimental Hélio."""
from pathlib import Path
import shutil,sys
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';S=H/'Capacites-Z/Sources';P=H/'Capacites-Z/Prototypes/Helio-Choc-Devastateur/Generation-PMDO';B=H/'.cache/destiny-test/backup-helio-v1-controle';mode=sys.argv[1]
if mode=='restore':
 for rel in (B/'saved.txt').read_text().splitlines():
  p=G/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/rel,p);assert p.read_bytes()==(B/rel).read_bytes(),rel
 for rel in (B/'added.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 print('Banc restauré ; originaux comparés.');sys.exit()
assert mode=='install' and not B.exists()
paths=['Data/Skill/searing_sunraze_smash.json','Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs']
adds=['Content/Particle/HelioV1_Charge.dir','Content/Particle/HelioV1_Breche.dir','Content/Particle/HelioV1_Impact.dir','Data/Script/origin/test_helio.lua'];assert all(not (G/x).exists() for x in adds)
for rel in paths:
 p=G/rel
 if p.exists():q=B/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (B/x).exists()));(B/'added.txt').write_text('\n'.join(adds))
shutil.copy2(P/'searing_sunraze_smash-v1-test-only.json',G/paths[0])
for n in ['HelioV1_Charge','HelioV1_Breche','HelioV1_Impact']:shutil.copy2(P/(n+'.dir'),G/'Content/Particle'/ (n+'.dir'))
shutil.copy2(S/'test-helio-controle-talent.lua',G/adds[3]);shutil.copy2(S/'intro-halo-banc-solgaleo.lua',G/paths[3]);e=G/paths[1];e.write_text(e.read_text()+'\n'+(S/'helio-v1-effets.lua').read_text())
d=G/paths[2];txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'''  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require('origin.test_helio').jouer() end) end )\n'''+txt[ix:];d.write_text(txt)
for rel in paths[-2:]:(G/rel).unlink(missing_ok=True)
print('Banc installé uniquement en copie isolée.')
