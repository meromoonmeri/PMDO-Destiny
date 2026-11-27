-- Essai dans une copie isolée : vraie action de zone PMDO, cibles placées par script.
-- Trois cibles à l'intérieur du rayon de 2 cases, une à distance 3 (contrôle).
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero,'Donjon requis');GAME:CutsceneMode(true)
 -- Copie de banc uniquement : retirer les monstres déjà présents qui pourraient partager une case.
 map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=4,map.Height-5 do
  for x=4,map.Width-5 do
   local ok=true
   for dy=-3,3 do for dx=-3,3 do local p=RogueElements.Loc(x+dx,y+dy); if map:TileBlocked(p) or map:GetTile(p).Effect.ID~='' then ok=false end end end
   if ok then center=RogueElements.Loc(x,y);break end
  end
  if center then break end
 end
 assert(center,'Aucune salle dégagée 7x7 : test de zone interrompu')
 map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local enemies={}
 for i=1,4 do
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('blastoise',0,'normal',Gender.Male),50,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e)
  e.CharLoc=RogueElements.Loc(center.X+i-2,center.Y+1);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();enemies[i]=e
 end
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 for _,v in ipairs(dirs) do
  local dx,dy=v[2],v[3];local places
  if dx~=0 and dy~=0 then places={{2*dx,2*dy},{dx,2*dy},{2*dx,dy},{-dx,-dy}} else places={{2*dx,2*dy},{2*dx-dy,2*dy+dx},{2*dx+dy,2*dy-dx},{-dx,-dy}} end
  for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:ReplaceSkill('continental_crush',0,true)
  local before={};for i,e in ipairs(enemies) do before[i]=e.HP end
  local result=d.ActionResult();PrintInfo('[GIGALITHE Z] début '..v[1]..' centre='..tostring(center)..' cases: centre, aile1, aile2, temoin arriere')
  GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  local values={};for i,e in ipairs(enemies) do values[i]=tostring(before[i])..'->'..tostring(e.HP) end
  PrintInfo('[GIGALITHE Z] résultat '..v[1]..' '..table.concat(values,',')..' action='..tostring(result.Success)..' charges='..hero.Skills[0].Element.Charges)
  GAME:WaitFrames(40)
 end
 map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[GIGALITHE Z] FIN')
end
return M
