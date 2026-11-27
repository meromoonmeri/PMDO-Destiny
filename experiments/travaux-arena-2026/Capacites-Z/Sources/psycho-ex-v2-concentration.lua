-- Aura de concentration du banc Psycho-Pulvérisation EX.
function BATTLE_SCRIPT.PsychoEXV2_Concentration(owner, ownerChar, context, args)
 local c=context.User
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('PsychoEXV2_Concentration',2),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Confusion')
 GAME:WaitFrames(38)
 PrintInfo('[PSYCHO EX V2] concentration terminée')
end
