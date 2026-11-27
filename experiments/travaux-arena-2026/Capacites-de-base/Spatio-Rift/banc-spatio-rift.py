#!/usr/bin/env python3
"""Installe ou restaure un contrôle original ou un prototype dans la copie isolée."""
from pathlib import Path
import sys,shutil
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';P=H/'Capacites-de-base/Spatio-Rift';B=H/'.cache/destiny-test/backup-spatio-rift';mode=sys.argv[1]
paths=['Data/Skill/spacial_rend.json','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs'];adds=['Content/Particle/SpatioRift_Faille.dir','Data/Script/origin/test_spatio_rift.lua']
if mode=='restore':
 for rel in (B/'saved.txt').read_text().splitlines():
  dest=G/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/rel,dest);assert dest.read_bytes()==(B/rel).read_bytes(),rel
 for rel in (B/'absent.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 for rel in (B/'added.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 shutil.rmtree(B);print('Originaux comparés, ajouts retirés.');sys.exit()
assert mode in ('original','v1') and not B.exists();assert all(not (G/x).exists() for x in adds);B.mkdir(parents=True)
for rel in paths:
 if (G/rel).exists():dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(G/rel,dest)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (B/x).exists()));(B/'absent.txt').write_text('\n'.join(x for x in paths if not (B/x).exists()));(B/'added.txt').write_text('\n'.join(adds))
if mode=='v1':
 shutil.copy2(P/'spacial_rend-v1-test-only.json',G/paths[0]);shutil.copy2(P/'SpatioRift_Faille.dir',G/adds[0])
txt=(P/'test-spatio-rift.lua').read_text().replace('__MODE__',mode.upper()).replace('__NBDIRS__','1' if mode=='original' else '8');(G/adds[1]).write_text(txt)
d=G/paths[1];txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'''  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require('origin.test_spatio_rift').jouer() end) end )\n'''+txt[ix:];d.write_text(txt)
intro='''local m={}
function m.Init(map) end
function m.Exit(map) end
function m.Update(map) end
function m.GameSave(map) end
function m.GameLoad(map) end
function m.Enter(map)
 local team=_DATA.Save.ActiveTeam;team.Players:Clear()
 local ch=team:CreatePlayer(_DATA.Save.Rand,RogueEssence.Dungeon.MonsterID('palkia',0,'normal',Gender.Genderless),50,'',0)
 team.Players:Add(ch);team.Leader.IsFounder=true;_DATA.Save:UpdateTeamProfile(true);GAME:CutsceneMode(false)
 GAME:EnterDungeon('ambush_forest',0,0,0,RogueEssence.Data.GameProgress.DungeonStakes.None,true,true)
end
return m
''';(G/paths[2]).write_text(intro)
for rel in paths[-2:]:(G/rel).unlink(missing_ok=True)
print('Banc',mode,'installé dans la copie isolée.')
