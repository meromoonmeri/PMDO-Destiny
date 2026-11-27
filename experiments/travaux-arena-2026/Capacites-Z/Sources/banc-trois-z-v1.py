#!/usr/bin/env python3
"""Installe/restaure un des trois bancs jetables. Usage : script TAG install|restore."""
from pathlib import Path
import shutil,sys
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';S=H/'Capacites-Z/Sources';ROOT=H/'Capacites-Z/Prototypes'
C={'Selene':('Rayons-Seleno-Explosifs','menacing_moonraze_maelstrom','lunala',0,'blissey'),'Apocalypse':('Apocalypsis-Luminis','light_that_burns_the_sky','necrozma',3,'umbreon'),'Fauche':('Fauche-Ame-des-Sept-Etoiles','soul_stealing_7_star_strike','marshadow',0,'blissey')}
tag,mode=sys.argv[1:];folder,skill,species,form,immune=C[tag];P=ROOT/folder/'Generation-PMDO';B=H/('.cache/destiny-test/backup-'+tag.lower()+'-v1')
if mode=='restore':
 for rel in (B/'saved.txt').read_text().splitlines():
  p=G/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/rel,p);assert p.read_bytes()==(B/rel).read_bytes(),rel
 for rel in (B/'added.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 print(tag,'restauré, originaux comparés');sys.exit()
assert mode=='install' and not B.exists()
paths=[f'Data/Skill/{skill}.json','Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs'];adds=[f'Content/Particle/{tag}V1_Charge.dir',f'Content/Particle/{tag}V1_Impact.dir','Data/Script/origin/test_trois_z.lua']
if tag=='Selene':adds.append('Content/Particle/HelioV1_Breche.dir')
assert all(not (G/x).exists() for x in adds)
for rel in paths:
 p=G/rel
 if p.exists():q=B/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (B/x).exists()));(B/'added.txt').write_text('\n'.join(adds))
shutil.copy2(P/(skill+'-v1-test-only.json'),G/paths[0])
for name in [tag+'V1_Charge',tag+'V1_Impact']:shutil.copy2(P/(name+'.dir'),G/'Content/Particle'/(name+'.dir'))
if tag=='Selene':shutil.copy2(ROOT/'Helio-Choc-Devastateur/Generation-PMDO/HelioV1_Breche.dir',G/adds[3])
txt=(S/'test-trois-z-v1.lua').read_text()
for a,b in [('__TAG__',tag),('__SKILL__',skill),('__SPECIES__',species),('__FORM__',str(form)),('__IMMUNE__',immune)]:txt=txt.replace(a,b)
(G/adds[2]).write_text(txt);(P/'test-v1.lua').write_text(txt)
intro=f'''local m={{}}
function m.Init(map) end
function m.Exit(map) end
function m.Update(map) end
function m.GameSave(map) end
function m.GameLoad(map) end
function m.Enter(map)
 local team=_DATA.Save.ActiveTeam;team.Players:Clear()
 local ch=team:CreatePlayer(_DATA.Save.Rand,RogueEssence.Dungeon.MonsterID('{species}',{form},'normal',Gender.Genderless),30,'',0)
 team.Players:Add(ch);team.Leader.IsFounder=true;_DATA.Save:UpdateTeamProfile(true);GAME:CutsceneMode(false)
 GAME:EnterDungeon('ambush_forest',0,0,0,RogueEssence.Data.GameProgress.DungeonStakes.None,true,true)
end
return m
''';(G/paths[3]).write_text(intro)
e=G/paths[1];e.write_text(e.read_text()+'\n'+(S/'trois-dernieres-z-v1-effets.lua').read_text());d=G/paths[2];txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'''  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require('origin.test_trois_z').jouer() end) end )\n'''+txt[ix:];d.write_text(txt)
for rel in paths[-2:]:(G/rel).unlink(missing_ok=True)
print(tag,'installé seulement en copie isolée')
