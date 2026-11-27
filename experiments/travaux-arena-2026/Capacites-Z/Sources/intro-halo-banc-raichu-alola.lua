local m={}
function m.Init(map) end
function m.Exit(map) end
function m.Update(map) end
function m.GameSave(map) end
function m.GameLoad(map) end
function m.Enter(map)
  PrintInfo('[BANC MEGA] Création du Raichu d’Alola de test')
  local team = _DATA.Save.ActiveTeam
  team.Players:Clear()
  local id=RogueEssence.Dungeon.MonsterID('raichu',1,'normal',Gender.Male)
  local ch=team:CreatePlayer(_DATA.Save.Rand,id,50,'',0)
  team.Players:Add(ch)
  team.Leader.IsFounder=true
  _DATA.Save:UpdateTeamProfile(true)
  GAME:CutsceneMode(false)
  GAME:EnterDungeon('ambush_forest',0,0,0,RogueEssence.Data.GameProgress.DungeonStakes.None,true,true)
end
return m
