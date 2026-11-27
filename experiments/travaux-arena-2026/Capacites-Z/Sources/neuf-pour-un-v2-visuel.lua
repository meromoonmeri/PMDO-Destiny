-- Effet de banc : les huit silhouettes sont des sprites visuels, pas des alliés invoqués.
function BATTLE_SCRIPT.NeufPourUnV2_Visuel(owner, ownerChar, context, args)
 local c=context.User
 local rayons=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('NeufPourUnV2_Rayons',2),1)
 rayons:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(rayons,RogueEssence.Content.DrawLayer.Back)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('NeufPourUnV2_Evolitions',2),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Cosmic_Power')
 GAME:WaitFrames(144)
 PrintInfo('[NEUF POUR UN V2] huit évolutions et rayons terminés')
end
