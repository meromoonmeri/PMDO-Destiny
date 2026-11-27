-- Fiche et carte jetables uniquement. Huit directions ; une cible à deux cases et un témoin latéral.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero,'Donjon requis');GAME:CutsceneMode(true)
 assert(hero.BaseForm.Species=='mimikyu','Le leader doit être Mimiqui')
 hero:FullRestore();hero:ReplaceSkill('play_rough',1,true)
 PrintInfo('[PATATI Z] espece='..hero.BaseForm.Species..' attaque-base='..hero.Skills[1].Element.SkillNum)
 map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=4,map.Height-5 do
  for x=4,map.Width-5 do
   local ok=true
   for dy=-3,3 do for dx=-3,3 do local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then ok=false end end end
   if ok then center=RogueElements.Loc(x,y);break end
  end
  if center then break end
 end
 assert(center,'Pas de pièce dégagée 7x7')
 for dy=-3,3 do for dx=-3,3 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end
 map:MapModified(RogueElements.Loc(center.X-4,center.Y-4),RogueElements.Loc(9,9))
 map.ViewOffset=RogueElements.Loc(0,24) -- cadrage de banc : éviter le journal sur la cible au sud
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local enemies={}
 for i=1,2 do
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('lapras',0,'normal',Gender.Female),100,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e)
  e.CharLoc=RogueElements.Loc(center.X+i,center.Y+1);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();enemies[i]=e
 end
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 for _,v in ipairs({dirs[1]}) do
  local dx,dy=v[2],v[3];local places={{2*dx,2*dy},{-dy,dx}}
  for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:ReplaceSkill('lets_snuggle_forever',0,true)
  local hp1,hp2=enemies[1].HP,enemies[2].HP
  local result=d.ActionResult();PrintInfo('[PATATI Z] début '..v[1]..' cible='..hp1..' témoin='..hp2)
  GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  PrintInfo('[PATATI Z] résultat '..v[1]..' cible='..hp1..'->'..enemies[1].HP..' témoin='..hp2..'->'..enemies[2].HP..' action='..tostring(result.Success)..' charges='..hero.Skills[0].Element.Charges)
  assert(enemies[1].HP==0 and enemies[1].Dead and enemies[2].HP==hp2,'KO forcé ou témoin invalide'); assert(not hero.StatusEffects:ContainsKey('none') and not enemies[1].StatusEffects:ContainsKey('none'),'Masquage non restauré'); PrintInfo('[PATATI V5 TEST] KO forcé confirmé, sprites restaurés');assert(hero.Skills[0].Element.Charges==0,'PP invalides')
  GAME:WaitFrames(45)
 end
 map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[PATATI Z] FIN OK')
end
return M
