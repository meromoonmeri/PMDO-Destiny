-- Banc isolé : huit directions, arrondis, résistance, talent et K.O. à 1 PV.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='tapu_koko','Tokorico requis');GAME:CutsceneMode(true);map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=5,map.Height-6 do for x=5,map.Width-6 do
  local good=true
  for dy=-4,4 do for dx=-4,4 do local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then good=false end end end
  if good then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Pièce 9x9 requise')
 for dy=-4,4 do for dx=-4,4 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end
 map:MapModified(RogueElements.Loc(center.X-5,center.Y-5),RogueElements.Loc(11,11));map.ViewOffset=RogueElements.Loc(0,24)
 DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Down));map:UpdateExploration(hero)
 local function creer(species,faction,x,y)
  local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID(species,0,'normal',Gender.Female),100,'',0)
  team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e);e.CharLoc=RogueElements.Loc(center.X+x,center.Y+y);e.CharDir=Direction.Up;e:UpdateFrame();_DUNGEON:AddTeam(faction,team);e:RefreshTraits();e:FullRestore();return e
 end
 local cible=creer('lapras',d.Faction.Foe,1,0);local temoin=creer('lapras',d.Faction.Foe,-2,0);local acier=creer('klefki',d.Faction.Foe,-3,2);local allie=creer('lapras',d.Faction.Friend,2,2)
 local dirs={{'bas',0,1,Direction.Down,270},{'bas-gauche',-1,1,Direction.DownLeft,269},{'gauche',-1,0,Direction.Left,101},{'haut-gauche',-1,-1,Direction.UpLeft,7},{'haut',0,-1,Direction.Up,4},{'haut-droite',1,-1,Direction.UpRight,3},{'droite',1,0,Direction.Right,2},{'bas-droite',1,1,Direction.DownRight,100}}
 local function lancer(e,hp,dir,label,expected)
  hero:FullRestore();hero:ReplaceSkill('guardian_of_alola',0,true);e:FullRestore();e.HP=hp
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,dir));map:UpdateExploration(hero);local wt=temoin.HP;local wa=allie.HP;local result=d.ActionResult()
  PrintInfo('[COLERE Z] debut '..label..' cible='..hp);GAME:WaitFrames(15);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  PrintInfo('[COLERE Z] resultat '..label..' cible='..hp..'->'..e.HP..' attendu='..expected..' temoin='..wt..'->'..temoin.HP..' allie='..wa..'->'..allie.HP..' PP='..hero.Skills[0].Element.Charges)
  assert(e.HP==expected,'PV inattendus pour '..label);assert(temoin.HP==wt and allie.HP==wa,'Témoin ou allié blessé');assert(hero.Skills[0].Element.Charges==0,'Charge incorrecte');GAME:WaitFrames(20)
 end
 for _,v in ipairs(dirs) do
  cible.CharLoc=RogueElements.Loc(center.X+v[2],center.Y+v[3]);cible:UpdateFrame();temoin.CharLoc=RogueElements.Loc(center.X-2*v[2],center.Y-2*v[3]);temoin:UpdateFrame()
  lancer(cible,v[5],v[4],v[1],v[5]-math.max(1,math.floor(v[5]*3/4)))
 end
 cible.CharLoc=RogueElements.Loc(center.X-3,center.Y-2);cible:UpdateFrame();temoin.CharLoc=RogueElements.Loc(center.X-2,center.Y);temoin:UpdateFrame();acier.CharLoc=RogueElements.Loc(center.X+1,center.Y);acier:UpdateFrame()
 lancer(acier,100,Direction.Right,'resistance acier',25)
 acier:LearnIntrinsic('wonder_guard',0,true);assert(acier:HasIntrinsic('wonder_guard'),'Garde Mystik manquante')
 lancer(acier,100,Direction.Right,'garde mystik',100)
 acier.CharLoc=RogueElements.Loc(center.X-3,center.Y+2);acier:UpdateFrame();cible.CharLoc=RogueElements.Loc(center.X+1,center.Y);cible:UpdateFrame()
 lancer(cible,1,Direction.Right,'minimum 1 PV et KO',0)
 map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[COLERE Z] FIN OK')
end
return M
