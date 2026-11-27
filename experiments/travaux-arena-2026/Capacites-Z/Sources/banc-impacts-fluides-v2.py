#!/usr/bin/env python3
"""Bancs isolés pour fins V2. Les noms PMDO originaux ne sont utilisés que dans la copie de jeu."""
from pathlib import Path
import sys,shutil
H=Path.home();G=H/'.cache/destiny-test/game/PMDO-Destiny';S=H/'Capacites-Z/Sources';R=H/'Capacites-Z/Prototypes'
config={
 'Selene':('Rayons-Seleno-Explosifs','menacing_moonraze_maelstrom','lunala',0,'blissey',['SeleneV1_Charge','SeleneV1_Impact','HelioV1_Breche'],'test_trois_z','trois-dernieres-z-v1-effets.lua'),
 'Apocalypse':('Apocalypsis-Luminis','light_that_burns_the_sky','necrozma',3,'umbreon',['ApocalypseV1_Charge','ApocalypseV1_Impact'],'test_trois_z','trois-dernieres-z-v1-effets.lua'),
 'Helio':('Helio-Choc-Devastateur','searing_sunraze_smash','solgaleo',0,'',['HelioV1_Charge','HelioV1_Breche','HelioV1_Impact'],'test_helio','helio-v1-effets.lua'),
 'Colere':('Colere-du-Gardien-d-Alola','guardian_of_alola','tapu_koko',0,'',['ColereV1_Arriere','ColereV1_Avant'],'test_colere','colere-v1-effets.lua')}
tag,mode=sys.argv[1:];folder,skill,species,form,immune,banks,test,effect=config[tag];P=R/folder/'Generation-PMDO';B=H/('.cache/destiny-test/backup-impacts-fluides-v2-'+tag.lower())
paths=[f'Data/Skill/{skill}.json','Data/Script/origin/event_battle.lua','Data/Script/origin/services/debug_tools/init.lua','Data/Script/destiny/ground/intro_halo/init.lua','SAVE/SAVE.rssv','SAVE/QUICKSAVE.rsqs'];adds=[f'Content/Particle/{x}.dir' for x in banks]+[f'Data/Script/origin/{test}.lua']
if mode=='restore':
 for rel in (B/'saved.txt').read_text().splitlines():
  p=G/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(B/rel,p);assert p.read_bytes()==(B/rel).read_bytes(),rel
 for rel in (B/'absent.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 for rel in (B/'added.txt').read_text().splitlines():(G/rel).unlink(missing_ok=True)
 shutil.rmtree(B);print(tag,'restauré, fichiers originaux comparés');sys.exit()
assert mode=='install' and not B.exists();assert all(not (G/x).exists() for x in adds),[str(G/x) for x in adds if (G/x).exists()];B.mkdir(parents=True)
for rel in paths:
 if (G/rel).exists():dst=B/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(G/rel,dst)
(B/'saved.txt').write_text('\n'.join(x for x in paths if (G/x).exists()));(B/'absent.txt').write_text('\n'.join(x for x in paths if not (G/x).exists()));(B/'added.txt').write_text('\n'.join(adds))
shutil.copy2(P/(skill+'-v1-test-only.json'),G/paths[0])
for name in banks:
 custom=P/'V2-impacts'/(name+'.dir')
 source=custom if custom.exists() else (R/'Helio-Choc-Devastateur/Generation-PMDO'/f'{name}.dir' if name=='HelioV1_Breche' and tag=='Selene' else P/f'{name}.dir')
 shutil.copy2(source,G/f'Content/Particle/{name}.dir')
if tag in ('Selene','Apocalypse'):
 txt=(S/'test-trois-z-v1.lua').read_text()
 for a,b in [('__TAG__',tag),('__SKILL__',skill),('__SPECIES__',species),('__FORM__',str(form)),('__IMMUNE__',immune)]:txt=txt.replace(a,b)
else:txt=(S/('test-helio-v1.lua' if tag=='Helio' else 'test-colere-v1.lua')).read_text()
(G/adds[-1]).write_text(txt);(P/'V2-impacts/test.lua').write_text(txt)
if tag in ('Helio','Colere'):
 shutil.copy2(S/('intro-halo-banc-solgaleo.lua' if tag=='Helio' else 'intro-halo-banc-tokorico.lua'),G/paths[3])
else:
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
e=G/paths[1];e.write_text(e.read_text()+'\n'+(S/effect).read_text());d=G/paths[2];txt=d.read_text();needle='  med:Subscribe("DebugTools", EngineServiceEvents.Init,';ix=txt.index(needle);txt=txt[:ix]+f'''  med:Subscribe("DebugTools", EngineServiceEvents.DungeonFloorEnter, function() TASK:BranchCoroutine(function() GAME:WaitFrames(80); require('origin.{test}').jouer() end) end )\n'''+txt[ix:];d.write_text(txt)
for rel in paths[-2:]:(G/rel).unlink(missing_ok=True)
print(tag,'installé uniquement dans la copie isolée')
