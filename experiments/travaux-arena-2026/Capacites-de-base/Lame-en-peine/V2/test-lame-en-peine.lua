-- Banc expérimental : huit directions, témoin latéral et absorption des PV.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='ceruledge','Malvalame requis');GAME:CutsceneMode(true);map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=4,map.Height-5 do for x=4,map.Width-5 do
  local good=true
  for dy=-3,3 do for dx=-3,3 do
   local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then good=false end
  end end
  if good then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Carré de banc introuvable')
 for dy=-3,3 do for dx=-3,3 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end
 map:MapModified(RogueElements.Loc(center.X-4,center.Y-4),RogueElements.Loc(9,9));map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local enemies={}
 for i=1,2 do
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('blissey',0,'normal',Gender.Female),50,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e)
  e.CharLoc=RogueElements.Loc(center.X+i,center.Y+1);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();enemies[i]=e
 end
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 for _,v in ipairs(dirs) do
  local dx,dy=v[2],v[3];local places={{dx,dy},{-dy,dx}}
  for i,e in ipairs(enemies) do e.CharLoc=RogueElements.Loc(center.X+places[i][1],center.Y+places[i][2]);e.CharDir=Direction.Up;e:UpdateFrame();e:FullRestore() end
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);hero:FullRestore();hero.HP=1;hero:ReplaceSkill('bitter_blade',0,true)
  local hp=hero.HP;local hpmax=hero.MaxHP;local cible=enemies[1].HP;local temoin=enemies[2].HP
  local result=d.ActionResult();PrintInfo('[LAME EN PEINE V2] début '..v[1]);GAME:WaitFrames(18)
  TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  local damage=cible-enemies[1].HP;local heal=hero.HP-hp;local attendu=math.min(hpmax-hp,math.max(1,math.floor(damage/2)))
  PrintInfo('[LAME EN PEINE V2] '..v[1]..' cible='..cible..'->'..enemies[1].HP..' témoin='..temoin..'->'..enemies[2].HP..' lanceur='..hp..'->'..hero.HP..' soin-attendu='..attendu..' charges='..hero.Skills[0].Element.Charges)
  assert(damage>0,'Cible indemne');assert(enemies[2].HP==temoin,'Témoin latéral touché');assert(heal==attendu,'Absorption incorrecte');assert(hero.Skills[0].Element.Charges==9,'PP incorrects')
  GAME:WaitFrames(25)
 end
 GAME:WaitFrames(45);map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[LAME EN PEINE V2] FIN OK')
end
return M
