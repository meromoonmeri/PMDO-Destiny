local d=RogueEssence.Dungeon
local hero=d.DungeonScene.Instance.FocusedCharacter
local p=hero.CharLoc
local spot=RogueElements.Loc(p.X+2,p.Y)
local team=d.MonsterTeam()
local id=d.MonsterID('snorlax',0,'normal',Gender.Male)
local enemy=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,id,50,'',0)
team.Players:Add(enemy)
enemy.CharLoc=spot
enemy.CharDir=Direction.Left
enemy:UpdateFrame()
_DUNGEON:AddTeam(d.Faction.Foe,team)
PrintInfo('[DIAG2] ennemi ajouté PV='..enemy.HP)
GAME:WaitFrames(60)
PrintInfo('[DIAG2] attente ok')
