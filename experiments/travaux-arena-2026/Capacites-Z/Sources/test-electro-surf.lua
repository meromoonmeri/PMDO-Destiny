-- Banc jetable : Raichu d'Alola ; huit directions et contrôle de l'immunité Électrik.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='raichu' and hero.BaseForm.Form==1,'Raichu forme Alola requis')
 GAME:CutsceneMode(true);hero:FullRestore();hero:ReplaceSkill('thunderbolt',1,true)
 PrintInfo('[ELECTRO SURF Z] espece='..hero.BaseForm.Species..' forme='..hero.BaseForm.Form..' attaque-base='..hero.Skills[1].Element.SkillNum)
 map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=4,map.Height-5 do for x=4,map.Width-5 do
  local ok=true
  for dy=-3,3 do for dx=-3,3 do local p=RogueElements.Loc(x+dx,y+dy);if map:TileBlocked(p) or map:GetTile(p).Effect.ID~='' then ok=false end end end
  if ok then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Pas de pièce dégagée 7x7');map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local enemies={}
 for i=1,3 do
  local species=(i==3) and 'flaaffy' or 'snorlax'
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID(species,0,'normal',Gender.Male),50,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e)
  e.CharLoc=RogueElements.Loc(center.X+i,center.Y+1);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();enemies[i]=e
 end
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 for _,v in ipairs(dirs) do
  local dx,dy=v[2],v[3];local places={{2*dx,2*dy},{-dy,dx},{3,-2}}
  for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:ReplaceSkill('stoked_sparksurfer',0,true)
  local hp1,hp2=enemies[1].HP,enemies[2].HP;local result=d.ActionResult()
  PrintInfo('[ELECTRO SURF Z] début '..v[1]..' cible='..hp1..' témoin='..hp2)
  GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  local para=(enemies[1]:GetStatusEffect('paralyze')~=nil);local paraw=(enemies[2]:GetStatusEffect('paralyze')~=nil)
  PrintInfo('[ELECTRO SURF Z] résultat '..v[1]..' cible='..hp1..'->'..enemies[1].HP..' paralysie='..tostring(para)..' témoin='..hp2..'->'..enemies[2].HP..' paralysie='..tostring(paraw)..' charges='..hero.Skills[0].Element.Charges..' action='..tostring(result.Success))
  assert(enemies[1].HP<hp1 and enemies[2].HP==hp2,'Dégâts ou témoin invalides');assert(para and not paraw,'Paralysie incorrecte');assert(hero.Skills[0].Element.Charges==0,'PP incorrects')
  GAME:WaitFrames(35)
 end
 -- Cible électrique : une protection du statut est prévue par le système PMDO.
 local places={{3,-2},{0,1},{2,0}}
 for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Right));hero:FullRestore();hero:ReplaceSkill('stoked_sparksurfer',0,true)
 local hp=enemies[3].HP;local result=d.ActionResult();PrintInfo('[ELECTRO SURF Z] début immunité Électrik PV='..hp)
 GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
 local para=(enemies[3]:GetStatusEffect('paralyze')~=nil)
 PrintInfo('[ELECTRO SURF Z] immunité Électrik PV='..hp..'->'..enemies[3].HP..' paralysie='..tostring(para)..' charges='..hero.Skills[0].Element.Charges)
 assert(enemies[3].HP<hp and not para,'Immunité électrique ou dégâts invalides');assert(hero.Skills[0].Element.Charges==0,'PP incorrects')
 GAME:WaitFrames(45);map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[ELECTRO SURF Z] FIN OK')
end
return M
