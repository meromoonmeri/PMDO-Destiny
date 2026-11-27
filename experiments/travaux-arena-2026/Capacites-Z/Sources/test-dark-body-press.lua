-- Fiche et carte jetables uniquement. Huit directions ; une cible à deux cases et un témoin latéral.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero,'Donjon requis');GAME:CutsceneMode(true)
 assert(hero.BaseForm.Species=='incineroar','Le leader doit être Félinferno')
 hero:FullRestore();hero:ReplaceSkill('darkest_lariat',1,true)
 PrintInfo('[DARK BODY Z] espece='..hero.BaseForm.Species..' attaque-base='..hero.Skills[1].Element.SkillNum)
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
 for _,v in ipairs(dirs) do
  local dx,dy=v[2],v[3];local places={{2*dx,2*dy},{-dy,dx}}
  for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:ReplaceSkill('malicious_moonsault',0,true)
  local hp1,hp2=enemies[1].HP,enemies[2].HP
  local result=d.ActionResult();PrintInfo('[DARK BODY Z] début '..v[1]..' cible='..hp1..' témoin='..hp2)
  GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  PrintInfo('[DARK BODY Z] résultat '..v[1]..' cible='..hp1..'->'..enemies[1].HP..' témoin='..hp2..'->'..enemies[2].HP..' action='..tostring(result.Success)..' charges='..hero.Skills[0].Element.Charges)
  assert(enemies[1].HP<hp1 and enemies[2].HP==hp2,'Dégâts ou témoin invalides');assert(hero.Skills[0].Element.Charges==0,'PP invalides')
  GAME:WaitFrames(45)
 end
 -- Test autonome : un mur ordinaire sur la trajectoire, un latéral et un incassable.
 for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X-3,center.Y+i);e:UpdateFrame() end
 local function set(x,y,id) map:GetTile(RogueElements.Loc(center.X+x,center.Y+y)).Data=d.TerrainTile(id) end
 local function get(x,y) return map:GetTile(RogueElements.Loc(center.X+x,center.Y+y)).Data.ID end
 set(1,0,_DATA.GenWall);set(0,1,_DATA.GenWall);set(0,-1,_DATA.GenUnbreakable)
 map:MapModified(RogueElements.Loc(center.X-4,center.Y-4),RogueElements.Loc(9,9));DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Right));map:UpdateExploration(hero);hero:ReplaceSkill('malicious_moonsault',0,true)
 PrintInfo('[DARK BODY MURS] avant contact='..get(1,0)..' lateral='..get(0,1)..' incassable='..get(0,-1));GAME:WaitFrames(40)
 local result=d.ActionResult();TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result));GAME:WaitFrames(40)
 PrintInfo('[DARK BODY MURS] apres contact='..get(1,0)..' lateral='..get(0,1)..' incassable='..get(0,-1)..' charges='..hero.Skills[0].Element.Charges)
 assert(get(1,0)==_DATA.GenFloor,'Mur de contact non detruit');assert(get(0,1)==_DATA.GenWall and get(0,-1)==_DATA.GenUnbreakable,'Mur lateral ou incassable modifie')
 map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[DARK BODY Z] FIN OK')
end
return M
