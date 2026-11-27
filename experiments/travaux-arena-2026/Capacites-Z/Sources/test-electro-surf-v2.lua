-- Banc jetable : Raichu d'Alola ; huit directions et contrôle de l'immunité Électrik.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='raichu' and hero.BaseForm.Form==1,'Raichu forme Alola requis')
 GAME:CutsceneMode(true);hero:FullRestore();hero:ReplaceSkill('thunderbolt',1,true)
 PrintInfo('[ELECTRO SURF V2] espece='..hero.BaseForm.Species..' forme='..hero.BaseForm.Form..' attaque-base='..hero.Skills[1].Element.SkillNum)
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
 for i=1,5 do
  local species=(i==5) and 'flaaffy' or 'snorlax'
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID(species,0,'normal',Gender.Male),50,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e)
  e.CharLoc=RogueElements.Loc(center.X+i,center.Y+1);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();enemies[i]=e
 end
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 for _,v in ipairs(dirs) do
  local dx,dy=v[2],v[3]
  local lx,ly,rx,ry
  if dx~=0 and dy~=0 then lx,ly=dx,0;rx,ry=0,dy else lx,ly=-dy,dx;rx,ry=dy,-dx end
  local places={{2*dx,2*dy},{2*dx+lx,2*dy+ly},{2*dx+rx,2*dy+ry},{-2*dx,-2*dy},{-dx,-dy}}
  for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:ReplaceSkill('stoked_sparksurfer',0,true)
  local hp={};for i,e in ipairs(enemies) do hp[i]=e.HP end;local result=d.ActionResult()
  PrintInfo('[ELECTRO SURF V2] début '..v[1])
  GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  for i,e in ipairs(enemies) do
   local para=(e:GetStatusEffect('paralyze')~=nil)
   PrintInfo('[ELECTRO SURF V2] '..v[1]..' cible='..i..' PV='..hp[i]..'->'..e.HP..' paralysie='..tostring(para)..' charges='..hero.Skills[0].Element.Charges)
   if i<=3 then assert(e.HP<hp[i] and para,'Cible centrale ou latérale non touchée/paralysée') else assert(e.HP==hp[i] and not para,'Témoin hors zone touché') end
  end
  assert(hero.Skills[0].Element.Charges==0,'PP incorrects')
  GAME:WaitFrames(35)
 end
 -- Cible électrique : une protection du statut est prévue par le système PMDO.
 local places={{-2,-2},{-2,-1},{-2,0},{-2,1},{2,0}}
 for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Right));hero:FullRestore();hero:ReplaceSkill('stoked_sparksurfer',0,true)
 local hp=enemies[5].HP;local result=d.ActionResult();PrintInfo('[ELECTRO SURF V2] début immunité Électrik PV='..hp)
 GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
 local para=(enemies[5]:GetStatusEffect('paralyze')~=nil)
 PrintInfo('[ELECTRO SURF V2] immunité Électrik PV='..hp..'->'..enemies[5].HP..' paralysie='..tostring(para)..' charges='..hero.Skills[0].Element.Charges)
 assert(enemies[5].HP<hp and not para,'Immunité électrique ou dégâts invalides');assert(hero.Skills[0].Element.Charges==0,'PP incorrects')
 GAME:WaitFrames(45);map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[ELECTRO SURF V2] FIN OK')
end
return M
