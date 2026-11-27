-- Banc isolé : zone adjacente, adversaires multiples, allié, Fée et absence de cible.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='kommo_o','Ékaïser requis');GAME:CutsceneMode(true);map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=5,map.Height-6 do for x=5,map.Width-6 do
  local good=true
  for dy=-4,4 do for dx=-4,4 do local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then good=false end end end
  if good then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Pièce 9x9 requise')
 for dy=-4,4 do for dx=-4,4 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end
 map:MapModified(RogueElements.Loc(center.X-5,center.Y-5),RogueElements.Loc(11,11));map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero);hero:ReplaceSkill('clanging_scales',1,true)
 local function creer(species,faction,x,y)
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID(species,0,'normal',Gender.Female),100,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e);e.CharLoc=RogueElements.Loc(center.X+x,center.Y+y);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(faction,team);e:RefreshTraits();e:FullRestore();return e
 end
 local foe={creer('lapras',d.Faction.Foe,1,0),creer('lapras',d.Faction.Foe,-1,0),creer('lapras',d.Faction.Foe,0,-1),creer('sylveon',d.Faction.Foe,1,1),creer('lapras',d.Faction.Foe,2,0)}
 local ally=creer('lapras',d.Faction.Friend,0,1)
 local stats={'mod_attack','mod_defense','mod_special_attack','mod_special_defense','mod_speed'};local stacktype=luanet.import_type('RogueEssence.Dungeon.StackState')
 local dirs={{'bas',Direction.Down},{'bas-gauche',Direction.DownLeft},{'gauche',Direction.Left},{'haut-gauche',Direction.UpLeft},{'haut',Direction.Up},{'haut-droite',Direction.UpRight},{'droite',Direction.Right},{'bas-droite',Direction.DownRight}}
 local function boosts(expected)
  local vals={};for _,id in ipairs(stats) do local st=hero:GetStatusEffect(id);local n=st and st.StatusStates:Get(luanet.ctype(stacktype)).Stack or 0;table.insert(vals,id..'='..n);assert(n==expected,'Bonus '..id..' attendu='..expected..' obtenu='..n) end
  return table.concat(vals,' ')
 end
 for _,dir in ipairs(dirs) do
  hero:FullRestore();hero:ReplaceSkill('clangorous_soulblaze',0,true);for _,e in ipairs(foe) do e:FullRestore() end;ally:FullRestore()
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,dir[2]));map:UpdateExploration(hero)
  local hp={};for i,e in ipairs(foe) do hp[i]=e.HP end;local allyhp=ally.HP;local result=d.ActionResult()
  PrintInfo('[DRACACO Z] début '..dir[1]);GAME:WaitFrames(15);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  local res={};for i,e in ipairs(foe) do table.insert(res,hp[i]..'->'..e.HP) end
  PrintInfo('[DRACACO Z] résultat '..dir[1]..' cibles='..table.concat(res,',')..' allie='..allyhp..'->'..ally.HP..' charges='..hero.Skills[0].Element.Charges)
  for i=1,3 do assert(foe[i].HP<hp[i],'Adversaire adjacent non touché '..i) end
  assert(foe[4].HP==hp[4],'Immunité Fée non respectée');assert(foe[5].HP==hp[5],'Témoin hors zone blessé');assert(ally.HP==allyhp,'Allié blessé');assert(hero.Skills[0].Element.Charges==0,'Charge incorrecte')
  PrintInfo('[DRACACO Z] boosts '..dir[1]..' '..boosts(1));GAME:WaitFrames(25)
 end
 -- Seule la Fée reste dans la portée ; les autres ennemis sont éloignés.
 for i,e in ipairs(foe) do local x,y=3,i-3;if i==4 then x,y=1,0 end;e.CharLoc=RogueElements.Loc(center.X+x,center.Y+y);e:UpdateFrame();e:FullRestore() end
 hero:FullRestore();ally:FullRestore();hero:ReplaceSkill('clangorous_soulblaze',0,true);DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Right));local hp=foe[4].HP;local result=d.ActionResult();PrintInfo('[DRACACO FEE SEULE] debut');TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result));assert(foe[4].HP==hp,'Fée blessée');PrintInfo('[DRACACO FEE SEULE] '..boosts(0)..' cible='..hp..'->'..foe[4].HP)
 -- Aucun ennemi adjacent, l'allié reste dans la zone.
 foe[4].CharLoc=RogueElements.Loc(center.X-3,center.Y+2);foe[4]:UpdateFrame();hero:FullRestore();hero:ReplaceSkill('clangorous_soulblaze',0,true);PrintInfo('[DRACACO SANS CIBLE] debut');TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result));PrintInfo('[DRACACO SANS CIBLE] '..boosts(0))
 map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[DRACACO Z] FIN OK')
end
return M
