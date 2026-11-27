local d=RogueEssence.Dungeon
local hero=d.DungeonScene.Instance.FocusedCharacter
GAME:CutsceneMode(true)
local p=hero.CharLoc
local spot=RogueElements.Loc(p.X+2,p.Y)
local team=d.MonsterTeam()
local id=d.MonsterID('snorlax',0,'normal',Gender.Male)
local enemy=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,id,50,'',0)
team.Players:Add(enemy)
PrintInfo('[DIAG] ennemi construit')
DUNGEON:CharSetAction(enemy,d.CharAnimIdle(spot,Direction.Left))
PrintInfo('[DIAG] ennemi pose')
_DUNGEON:AddTeam(d.Faction.Foe,team)
PrintInfo('[DIAG] ennemi ajouté '..enemy.HP)
DUNGEON:CharSetAction(hero,d.CharAnimIdle(p,Direction.Right))
PrintInfo('[DIAG] hero pose')
GAME:WaitFrames(60)
PrintInfo('[DIAG] attente ok')
