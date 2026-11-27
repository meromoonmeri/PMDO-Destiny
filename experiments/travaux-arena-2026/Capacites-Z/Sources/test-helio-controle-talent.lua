local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero.BaseForm.Species=='solgaleo');GAME:CutsceneMode(true);map.MapTeams:Clear();map.AllyTeams:Clear()
 local center=nil
 for y=5,map.Height-6 do for x=5,map.Width-6 do local good=true;for dy=-4,4 do for dx=-4,4 do local t=map:GetTile(RogueElements.Loc(x+dx,y+dy));if t.Effect.ID~='' or (t.Data.ID~=_DATA.GenWall and t.Data.ID~=_DATA.GenFloor) then good=false end end end;if good then center=RogueElements.Loc(x,y);break end end if center then break end end
 assert(center);for dy=-4,4 do for dx=-4,4 do map:GetTile(RogueElements.Loc(center.X+dx,center.Y+dy)).Data=d.TerrainTile(_DATA.GenFloor) end end;map:MapModified(RogueElements.Loc(center.X-5,center.Y-5),RogueElements.Loc(11,11));map.ViewOffset=RogueElements.Loc(0,24)
 local team=d.MonsterTeam();local e=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('lapras',0,'normal',Gender.Female),100,'',0);team.Players:Add(e);e.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));e.Tactic:Initialize(e);e.CharLoc=RogueElements.Loc(center.X+1,center.Y);e.CharDir=Direction.Up;_DUNGEON:AddTeam(d.Faction.Foe,team);e:LearnIntrinsic('wonder_guard',0,true);e:FullRestore();e:UpdateFrame()
 local function act(skill)
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,Direction.Right));map:UpdateExploration(hero);hero:FullRestore();hero:ReplaceSkill(skill,0,true);e:FullRestore();local hp=e.HP;local result=d.ActionResult();PrintInfo('[HELIO CONTROLE] debut '..skill..' hp='..hp);TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result));PrintInfo('[HELIO CONTROLE] fin '..skill..' hp='..hp..'->'..e.HP..' garde='..tostring(e:HasIntrinsic('wonder_guard'))..' suspendu='..tostring(e.IntrinsicDisabled));return hp,e.HP
 end
 local a,b=act('metal_claw');assert(a==b,'Garde Mystik ne bloque pas le témoin Acier');local c,dmg=act('searing_sunraze_smash');assert(dmg<c and e:HasIntrinsic('wonder_guard') and not e.IntrinsicDisabled,'Contournement ou restauration incorrects')
 GAME:CutsceneMode(false);PrintInfo('[HELIO CONTROLE] FIN OK')
end
return M
