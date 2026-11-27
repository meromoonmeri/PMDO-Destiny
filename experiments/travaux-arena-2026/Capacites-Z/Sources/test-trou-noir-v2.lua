-- Banc jetable : le test prépare terrain et monstres ; la capacité elle-même détruit les murs.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='absol','Absol requis');GAME:CutsceneMode(true);map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=4,map.Height-5 do for x=4,map.Width-5 do
  local good=true
  for dy=-3,3 do for dx=-3,3 do
   local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then good=false end
  end end
  if good then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Pas de carré de banc 7x7 sans terrain protégé')
 -- Aménager un carré de test sans modifier les escaliers ou terrains spéciaux.
 for dy=-3,3 do for dx=-3,3 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end
 map:MapModified(RogueElements.Loc(center.X-4,center.Y-4),RogueElements.Loc(9,9));map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local enemies={}
 for i=1,4 do
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('blastoise',0,'normal',Gender.Male),50,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e)
  e.CharLoc=RogueElements.Loc(center.X+i-2,center.Y+1);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();enemies[i]=e
 end
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 for _,v in ipairs(dirs) do
  local dx,dy=v[2],v[3];local places={{2*dx,2*dy},{-dx,-dy},{-dy,dx},{3*dx,3*dy}}
  for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:ReplaceSkill('black_hole_eclipse',0,true)
  local before={};for i,e in ipairs(enemies) do before[i]=e.HP end
  local result=d.ActionResult();PrintInfo('[TROU NOIR V2] début '..v[1]..' centre='..tostring(center));GAME:WaitFrames(15)
  TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  local vals={};for i,e in ipairs(enemies) do vals[i]=before[i]..'->'..e.HP end
  PrintInfo('[TROU NOIR V2] résultat '..v[1]..' '..table.concat(vals,',')..' charges='..hero.Skills[0].Element.Charges..' action='..tostring(result.Success))
  assert(enemies[1].HP<before[1] and enemies[2].HP<before[2] and enemies[3].HP<before[3] and enemies[4].HP==before[4],'Dégâts zone incorrects');assert(hero.Skills[0].Element.Charges==0,'PP incorrects')
  GAME:WaitFrames(30)
 end
 -- Montage de murs pour vérifier l'événement autonome de la fiche.
 for i,e in ipairs(enemies) do local p=({{2,0},{-1,0},{0,2},{3,0}})[i];e.CharLoc=RogueElements.Loc(center.X+p[1],center.Y+p[2]);e:UpdateFrame();e:FullRestore() end
 local function set(x,y,id) map:GetTile(RogueElements.Loc(center.X+x,center.Y+y)).Data=d.TerrainTile(id) end
 local function get(x,y) return map:GetTile(RogueElements.Loc(center.X+x,center.Y+y)).Data.ID end
 set(1,0,_DATA.GenWall);set(-2,-1,_DATA.GenWall);set(3,-2,_DATA.GenWall);set(0,-1,_DATA.GenUnbreakable)
 map:MapModified(RogueElements.Loc(center.X-4,center.Y-4),RogueElements.Loc(9,9));DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Right));map:UpdateExploration(hero)
 hero:ReplaceSkill('black_hole_eclipse',0,true)
 PrintInfo('[TROU NOIR V2 MURS] avant interieur='..get(1,0)..','..get(-2,-1)..' dehors='..get(3,-2)..' incassable='..get(0,-1));GAME:WaitFrames(70)
 local hp1=enemies[1].HP;local result=d.ActionResult();TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result));GAME:WaitFrames(30)
 PrintInfo('[TROU NOIR V2 MURS] apres interieur='..get(1,0)..','..get(-2,-1)..' dehors='..get(3,-2)..' incassable='..get(0,-1)..' cible-derriere='..hp1..'->'..enemies[1].HP..' charges='..hero.Skills[0].Element.Charges)
 assert(get(1,0)==_DATA.GenFloor and get(-2,-1)==_DATA.GenFloor,'Murs intérieurs non détruits');assert(get(3,-2)==_DATA.GenWall,'Mur hors portée détruit');assert(get(0,-1)==_DATA.GenUnbreakable,'Mur incassable détruit');assert(enemies[1].HP<hp1,'Cible derrière le mur intacte')
 GAME:WaitFrames(90);map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[TROU NOIR V2] FIN OK')
end
return M
