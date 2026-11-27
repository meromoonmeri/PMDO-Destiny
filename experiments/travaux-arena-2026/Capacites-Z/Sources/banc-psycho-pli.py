#!/usr/bin/env python3
"""Banc jetable : installer ou restaurer les seuls fichiers touchés dans la copie isolée."""
from pathlib import Path
import shutil,json,sys
H=Path.home(); G=H/'.cache/destiny-test/game/PMDO-Destiny'; S=H/'Capacites-Z/Sources'; P=H/'Capacites-Z/Prototypes/Psycho-Pulverisation-EX/Generation-PMDO'; B=H/'.cache/destiny-test/backup-psycho-pli-unique'
paths=['Data/Skill/shattered_psyche.json','Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs']
adds=['Content/Particle/PsychoEX_Concentration.dir','Content/Particle/PsychoEX_Impact.dir','Content/BG/PsychoEX_Fragment.dir','Data/Script/origin/test_psycho_pli.lua']
mode=sys.argv[1]
if mode=='restore':
 for rel in (B/'saved.txt').read_text().splitlines():
  p=G/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/rel,p);assert p.read_bytes()==(B/rel).read_bytes(),rel
 for rel in (B/'absent.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 for rel in (B/'added.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 print('Originaux restaurés et comparés ; ajouts supprimés.');sys.exit()
assert mode=='install' and not B.exists()
assert all(not (G/x).exists() for x in adds)
B.mkdir(parents=True)
for rel in paths:
 p=G/rel
 if p.exists():
  dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (G/x).exists()))
(B/'absent.txt').write_text('\n'.join(x for x in paths if not (G/x).exists()))
(B/'added.txt').write_text('\n'.join(adds))
z=json.loads((P/'shattered_psyche-test-only.json').read_text());data=z['Object']['Data']
data['BeforeActions'][0]['Value']['Script']='PsychoPli_Concentration'
data['BeforeHits']=[{'Key':{'str':[0]},'Value':{'$type':'RogueEssence.Dungeon.BattleScriptEvent, RogueEssence','Script':'PsychoPli_Cible','ArgTable':'{}'}}]
(G/paths[0]).write_text(json.dumps(z,ensure_ascii=False,indent=2));(P/'shattered_psyche-pli-test-only.json').write_text(json.dumps(z,ensure_ascii=False,indent=2))
for n in ['PsychoEX_Concentration.dir','PsychoEX_Impact.dir']:shutil.copy2(P/n,G/'Content/Particle'/n)
shutil.copy2(P/'PsychoEX_Fragment.dir',G/'Content/BG/PsychoEX_Fragment.dir')
shutil.copy2(S/'test-psycho-pulverisation-v2.lua',G/adds[3])
e=G/paths[1];e.write_text(e.read_text()+'\n'+(S/'psycho-pli-banc.lua').read_text())
d=G/paths[2];txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+'''  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require('origin.test_psycho_pli').jouer() end) end )\n'''+txt[ix:];d.write_text(txt)
intro='''local m={}
function m.Init(map) end
function m.Exit(map) end
function m.Update(map) end
function m.GameSave(map) end
function m.GameLoad(map) end
function m.Enter(map)
 local team=_DATA.Save.ActiveTeam;team.Players:Clear()
 local ch=team:CreatePlayer(_DATA.Save.Rand,RogueEssence.Dungeon.MonsterID('gardevoir',0,'normal',Gender.Female),50,'',0)
 team.Players:Add(ch);team.Leader.IsFounder=true;_DATA.Save:UpdateTeamProfile(true);GAME:CutsceneMode(false)
 GAME:EnterDungeon('ambush_forest',0,0,0,RogueEssence.Data.GameProgress.DungeonStakes.None,true,true)
end
return m
''';(G/paths[3]).write_text(intro)
for rel in paths[-2:]:(G/rel).unlink(missing_ok=True)
print('Banc installé dans la copie isolée.')
