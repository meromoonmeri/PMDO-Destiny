local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='solgaleo','Solgaleo requis');GAME:CutsceneMode(true);map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=5,map.Height-6 do for x=5,map.Width-6 do
  local good=true;for dy=-4,4 do for dx=-4,4 do local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then good=false end end end
  if good then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Pièce 9x9 requise')
 for dy=-4,4 do for dx=-4,4 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end
 map:MapModified(RogueElements.Loc(center.X-5,center.Y-5),RogueElements.Loc(11,11));map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local function creer(x,y)
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('lapras',0,'normal',Gender.Female),100,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e);e.CharLoc=RogueElements.Loc(center.X+x,center.Y+y);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();return e
 end
 local target=creer(2,0);local temoin=creer(0,2)
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 local function action(v,label)
  local dx,dy=v[2],v[3];target.CharLoc=RogueElements.Loc(center.X+2*dx,center.Y+2*dy);target:UpdateFrame();target:FullRestore();temoin.CharLoc=RogueElements.Loc(center.X-dy,center.Y+dx);temoin:UpdateFrame();temoin:FullRestore();hero:FullRestore();hero:ReplaceSkill('searing_sunraze_smash',0,true);DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero)
  local hp,wt=target.HP,temoin.HP;local result=d.ActionResult();PrintInfo('[HELIO Z] debut '..label..' cible='..hp..' garde='..tostring(target:HasIntrinsic('wonder_guard')));GAME:WaitFrames(20);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  PrintInfo('[HELIO Z] resultat '..label..' cible='..hp..'->'..target.HP..' temoin='..wt..'->'..temoin.HP..' PP='..hero.Skills[0].Element.Charges..' talent_desactive='..tostring(target.IntrinsicDisabled)..' garde='..tostring(target:HasIntrinsic('wonder_guard')))
  assert(target.HP<hp and temoin.HP==wt,'Dégâts ou témoin incorrects');assert(hero.Skills[0].Element.Charges==0,'Charge incorrecte');assert(not target.IntrinsicDisabled,'Talent non restauré');GAME:WaitFrames(25)
 end
 for _,v in ipairs(dirs) do action(v,v[1]) end
 target:LearnIntrinsic('wonder_guard',0,true);assert(target:HasIntrinsic('wonder_guard'),'Talent absent');action(dirs[7],'garde mystik contournee');assert(target:HasIntrinsic('wonder_guard'),'Talent perdu')
 map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[HELIO Z] FIN OK')
end
return M
