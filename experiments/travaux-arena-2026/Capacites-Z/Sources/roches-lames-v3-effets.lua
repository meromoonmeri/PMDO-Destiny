-- Hurlement orienté depuis Lougaroc, avant la frappe sur la cible.
function BATTLE_SCRIPT.RochesLames_Hurlement(owner, ownerChar, context, args)
 local c=context.User
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('RochesLamesV3_Onde',1),1)
 a:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Hyper_Voice');GAME:WaitFrames(48)
end
function BATTLE_SCRIPT.RochesLames_EffacerChamps(owner, ownerChar, context, args)
 for _,id in ipairs({'electric_terrain','grassy_terrain','misty_terrain','psychic_terrain'}) do
  if _ZONE.CurrentMap.Status:ContainsKey(id) then
   TASK:WaitTask(_DUNGEON:RemoveMapStatus(id))
   PrintInfo('[ROCHES LAMES CHAMP] retire='..id)
  end
 end
end
