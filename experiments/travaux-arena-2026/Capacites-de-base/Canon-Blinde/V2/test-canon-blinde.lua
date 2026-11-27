-- Banc jetable : Carmadura ; huit directions et contrôle de collision.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='armarouge','Carmadura requis')
 GAME:CutsceneMode(true);hero:FullRestore();hero:ReplaceSkill('flamethrower',1,true)
 PrintInfo('[CANON BLINDE V2] espece='..hero.BaseForm.Species..' forme='..hero.BaseForm.Form..' attaque-base='..hero.Skills[1].Element.SkillNum)
 map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=4,map.Height-5 do for x=4,map.Width-5 do
  local ok=true
  for dy=-3,3 do for dx=-3,3 do local p=RogueElements.Loc(x+dx,y+dy);local t=map:GetTile(p);if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then ok=false end end end
  if ok then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Pas de pièce dégagée 7x7');for y=-3,3 do for x=-3,3 do map:GetTile(RogueElements.Loc(center.X+x,center.Y+y)).Data=d.TerrainTile(_DATA.GenFloor) end end;map:MapModified(RogueElements.Loc(center.X-4,center.Y-4),RogueElements.Loc(9,9));map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local enemies={}
 for i=1,5 do
  local species='blissey'
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
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:FullRestore();hero:ReplaceSkill('armor_cannon',0,true)
  local hp={};for i,e in ipairs(enemies) do hp[i]=e.HP end;local result=d.ActionResult()
  PrintInfo('[CANON BLINDE V2] début '..v[1])
  GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  for i,e in ipairs(enemies) do
   local para=(e:GetStatusEffect('burn')~=nil)
   PrintInfo('[CANON BLINDE V2] '..v[1]..' cible='..i..' PV='..hp[i]..'->'..e.HP..' brûlure='..tostring(para)..' charges='..hero.Skills[0].Element.Charges)
   if i<=3 then assert(e.HP<hp[i] and para,'Cible centrale ou latérale non touchée/brûlée') else assert(e.HP==hp[i] and not para,'Témoin hors zone touché') end
  end
  assert(hero.Skills[0].Element.Charges==4,'PP incorrects')
  assert(CANON_BLINDE_IMPACT_X==center.X+3*dx and CANON_BLINDE_IMPACT_Y==center.Y+3*dy,'Case finale incorrecte')
  local st=luanet.import_type('RogueEssence.Dungeon.StackState');local def=hero:GetStatusEffect('mod_defense');local spdef=hero:GetStatusEffect('mod_special_defense');assert(def and spdef,'Baisse des défenses manquante');local a=def.StatusStates:Get(luanet.ctype(st)).Stack;local b=spdef.StatusStates:Get(luanet.ctype(st)).Stack;PrintInfo('[CANON BLINDE V2] baisses def='..a..' defspe='..b);assert(a==-1 and b==-1,'Paliers défensifs incorrects')
  GAME:WaitFrames(35)
 end
 -- Mur frontal à deux cases : cible derrière intacte, impact sur le mur.
 for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X-2,center.Y-3+i);e:UpdateFrame();e:FullRestore() end
 local behind=enemies[1];behind.CharLoc=RogueElements.Loc(center.X+3,center.Y);behind:UpdateFrame();local wall=RogueElements.Loc(center.X+2,center.Y);map:GetTile(wall).Data=d.TerrainTile(_DATA.GenWall);map:MapModified(RogueElements.Loc(center.X-4,center.Y-4),RogueElements.Loc(9,9));hero:FullRestore();DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Right));hero:ReplaceSkill('armor_cannon',0,true);local before=behind.HP;PrintInfo('[CANON BLINDE V2] début collision mur');GAME:WaitFrames(15);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,d.ActionResult()));PrintInfo('[CANON BLINDE V2] mur impact='..tostring(CANON_BLINDE_IMPACT_X)..','..tostring(CANON_BLINDE_IMPACT_Y)..' attendu='..wall.X..','..wall.Y..' derrière='..before..'->'..behind.HP);assert(CANON_BLINDE_IMPACT_X==wall.X and CANON_BLINDE_IMPACT_Y==wall.Y,'Impact mal placé sur le mur');assert(behind.HP==before and behind:GetStatusEffect('burn')==nil,'Ennemi derrière mur touché');assert(map:GetTile(wall).Data.ID==_DATA.GenWall,'Mur détruit');map:GetTile(wall).Data=d.TerrainTile(_DATA.GenFloor)
 GAME:WaitFrames(45);map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[CANON BLINDE V2] FIN OK')
end
return M
