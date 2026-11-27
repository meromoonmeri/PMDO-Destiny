-- Banc jetable en copie isolée : capacité de statut ciblant Évoli lui-même.
local M={}
function M.jouer()
 local d=RogueEssence.Dungeon;local hero=d.DungeonScene.Instance.FocusedCharacter;local map=_ZONE.CurrentMap
 assert(hero and hero.BaseForm.Species=='eevee','Évoli requis'); GAME:CutsceneMode(true)
 map.MapTeams:Clear();map.AllyTeams:Clear();hero:ReplaceSkill('last_resort',1,true)
 local center=nil
 for y=4,map.Height-5 do for x=4,map.Width-5 do
  local ok=true
  for dy=-3,3 do for dx=-3,3 do local p=RogueElements.Loc(x+dx,y+dy);if map:TileBlocked(p) or map:GetTile(p).Effect.ID~='' then ok=false end end end
  if ok then center=RogueElements.Loc(x,y);break end
 end if center then break end end
 assert(center,'Salle dégagée 7x7 requise');map.ViewOffset=RogueElements.Loc(0,24)
 local team=d.MonsterTeam();local enemy=_DATA.Save.ActiveTeam:CreatePlayer(_DATA.Save.Rand,d.MonsterID('snorlax',0,'normal',Gender.Male),50,'',0)
 team.Players:Add(enemy);enemy.Tactic=RogueEssence.Data.AITactic(_DATA:GetAITactic('wait_only'));enemy.Tactic:Initialize(enemy);enemy.CharLoc=RogueElements.Loc(center.X+2,center.Y);enemy.CharDir=Direction.Up;enemy:UpdateFrame();_DUNGEON:AddTeam(d.Faction.Foe,team);enemy:RefreshTraits();enemy:FullRestore()
 local stacktype=luanet.import_type('RogueEssence.Dungeon.StackState')
 local stats={'mod_attack','mod_defense','mod_special_attack','mod_special_defense','mod_speed'}
 local dirs={{'bas',Direction.Down},{'bas-gauche',Direction.DownLeft},{'gauche',Direction.Left},{'haut-gauche',Direction.UpLeft},{'haut',Direction.Up},{'haut-droite',Direction.UpRight},{'droite',Direction.Right},{'bas-droite',Direction.DownRight}}
 for _,v in ipairs(dirs) do
  hero:FullRestore();hero:ReplaceSkill('extreme_evoboost',0,true);enemy:FullRestore()
  DUNGEON:CharSetAction(hero,d.CharAnimIdle(center,v[2]));map:UpdateExploration(hero)
  local hp=enemy.HP;local result=d.ActionResult();PrintInfo('[NEUF POUR UN] début '..v[1]); GAME:WaitFrames(20)
  TASK:WaitTask(_DUNGEON:ProcessUseSkill(hero,0,result))
  local vals={}
  for _,id in ipairs(stats) do
   local status=hero:GetStatusEffect(id);assert(status~=nil,'Stat absente '..id)
   local stack=status.StatusStates:Get(luanet.ctype(stacktype)).Stack;table.insert(vals,id..'='..tostring(stack))
   assert(stack==2,'Stat pas à +2 '..id..'='..tostring(stack));assert(enemy:GetStatusEffect(id)==nil,'Témoin modifié '..id)
  end
  assert(enemy.HP==hp,'Témoin blessé');assert(hero.Skills[0].Element.Charges==0,'PP invalides')
  PrintInfo('[NEUF POUR UN] résultat '..v[1]..' '..table.concat(vals,' ')..' témoin='..hp..'->'..enemy.HP..' charges='..hero.Skills[0].Element.Charges..' action='..tostring(result.Success))
  GAME:WaitFrames(35)
 end
 map.ViewOffset=RogueElements.Loc(0,0);GAME:CutsceneMode(false);PrintInfo('[NEUF POUR UN] FIN OK')
end
return M
