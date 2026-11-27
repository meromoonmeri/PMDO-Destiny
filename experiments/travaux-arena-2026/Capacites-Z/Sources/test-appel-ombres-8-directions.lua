-- Test native du prototype Turbo-Charge sur copie jetable.
-- Appelle ProcessUseSkill ; la cible est placée par script pour chaque orientation.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero,'Donjon requis');GAME:CutsceneMode(true)
 local center=nil
 for y=3,map.Height-4 do
  for x=3,map.Width-4 do
   local ok=true
   for dy=-2,2 do for dx=-2,2 do local pt=RogueElements.Loc(x+dx,y+dy); if map:TileBlocked(pt) or map:GetTile(pt).Effect.ID ~= "" then ok=false end end end
   if ok then center=RogueElements.Loc(x,y);break end
  end
  if center then break end
 end
 assert(center,'Pas de pièce 5x5 libre')
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local team=d.MonsterTeam();local enemy=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('snorlax',0,'normal',Gender.Male),50,'',0)
 team.Players:Add(enemy);enemy.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));enemy.Tactic:Initialize(enemy);enemy.CharLoc=RogueElements.Loc(center.X,center.Y+2);enemy.CharDir=Direction.Up;enemy:UpdateFrame()
 _DUNGEON:AddTeam(d.Faction.Foe,team);enemy:RefreshTraits();enemy:FullRestore()
 local dirs={{'bas',0,1,Direction.Down,Direction.Up},{'bas-gauche',-1,1,Direction.DownLeft,Direction.UpRight},{'gauche',-1,0,Direction.Left,Direction.Right},{'haut-gauche',-1,-1,Direction.UpLeft,Direction.DownRight},{'haut',0,-1,Direction.Up,Direction.Down},{'haut-droite',1,-1,Direction.UpRight,Direction.DownLeft},{'droite',1,0,Direction.Right,Direction.Left},{'bas-droite',1,1,Direction.DownRight,Direction.UpLeft}}
 for _,v in ipairs(dirs) do
  local target=RogueElements.Loc(center.X+2*v[2],center.Y+2*v[3])
  enemy.CharLoc=target;enemy.CharDir=v[5];enemy:UpdateFrame();enemy:FullRestore()
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero)
  hero:ReplaceSkill('never_ending_nightmare',0,true)
  local hp=enemy.HP
  local result=d.ActionResult()
  PrintInfo('[OMBRES Z] début '..v[1]..' HP='..hp..' charges='..hero.Skills[0].Element.Charges)
  GAME:WaitFrames(20)
  TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  PrintInfo('[OMBRES Z] résultat '..v[1]..' HP='..hp..' -> '..enemy.HP..' action='..tostring(result.Success)..' charges='..hero.Skills[0].Element.Charges)
  GAME:WaitFrames(35)
 end
 GAME:CutsceneMode(false);PrintInfo('[OMBRES Z] FIN')
end
return M
