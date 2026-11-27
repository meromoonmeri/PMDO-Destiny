local M={}
local TAG='Fauche';local SKILL='soul_stealing_7_star_strike';local SPECIES='marshadow';local FORM=0
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species==SPECIES and hero.BaseForm.Form==FORM,'Mauvais lanceur');GAME:CutsceneMode(true);map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=5,map.Height-6 do for x=5,map.Width-6 do local good=true;for dy=-4,4 do for dx=-4,4 do local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then good=false end end end;if good then center=RogueElements.Loc(x,y);break end end if center then break end end
 assert(center,'Pièce 9x9 requise');for dy=-4,4 do for dx=-4,4 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end;map:MapModified(RogueElements.Loc(center.X-5,center.Y-5),RogueElements.Loc(11,11));map.ViewOffset=RogueElements.Loc(0,24);DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local function creer(species,x,y)
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID(species,0,'normal',Gender.Female),100,'',0);team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e);e.CharLoc=RogueElements.Loc(center.X+x,center.Y+y);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);e:RefreshTraits();e:FullRestore();return e
 end
 local target=creer('lapras',2,0);local witness=creer('lapras',0,2);local immune=creer('blissey',-3,2)
 local dirs={{'bas',0,1,Direction.Down},{'bas-gauche',-1,1,Direction.DownLeft},{'gauche',-1,0,Direction.Left},{'haut-gauche',-1,-1,Direction.UpLeft},{'haut',0,-1,Direction.Up},{'haut-droite',1,-1,Direction.UpRight},{'droite',1,0,Direction.Right},{'bas-droite',1,1,Direction.DownRight}}
 local function act(e,v,label,shouldhit,mode)
  local dx,dy=v[2],v[3];e.CharLoc=RogueElements.Loc(center.X+2*dx,center.Y+2*dy);e:UpdateFrame();e:FullRestore();witness.CharLoc=RogueElements.Loc(center.X-dy,center.Y+dx);witness:UpdateFrame();witness:FullRestore();hero:FullRestore()
  if TAG=='Apocalypse' then if mode=='physique' then hero.ProxyAtk=200;hero.ProxyMAtk=50 else hero.ProxyAtk=50;hero.ProxyMAtk=200 end end
  hero:ReplaceSkill(SKILL,0,true);DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[4]));map:UpdateExploration(hero);local hp,wt=e.HP,witness.HP;local result=d.ActionResult();PrintInfo('['..TAG..' Z] debut '..label..' cible='..hp);GAME:WaitFrames(15);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  PrintInfo('['..TAG..' Z] resultat '..label..' cible='..hp..'->'..e.HP..' temoin='..wt..'->'..witness.HP..' PP='..hero.Skills[0].Element.Charges..' talent_desactive='..tostring(e.IntrinsicDisabled)..' garde='..tostring(e:HasIntrinsic('wonder_guard')))
  assert((shouldhit and e.HP<hp) or (not shouldhit and e.HP==hp),'PV incorrects '..label);assert(witness.HP==wt,'Témoin blessé');assert(hero.Skills[0].Element.Charges==0,'PP incorrects');assert(not e.IntrinsicDisabled,'Talent non restauré');GAME:WaitFrames(18)
 end
 for i,v in ipairs(dirs) do act(target,v,v[1],true,(i%2==0 and 'physique' or 'special')) end
 target.CharLoc=RogueElements.Loc(center.X-3,center.Y-2);target:UpdateFrame();act(immune,dirs[7],'immunite type',false,'special');immune.CharLoc=RogueElements.Loc(center.X-3,center.Y+2);immune:UpdateFrame()
 if TAG~='Fauche' then target:LearnIntrinsic('wonder_guard',0,true);act(target,dirs[7],'garde mystik',true,'special');assert(target:HasIntrinsic('wonder_guard'),'Talent perdu') end
 hero.ProxyAtk=-1;hero.ProxyMAtk=-1;map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('['..TAG..' Z] FIN OK')
end
return M
