function BATTLE_SCRIPT.GigaTonnerre_Charge(owner, ownerChar, context, args)
 local c=context.User
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('GigaTonnerre_Charge',2),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Charge')
 GAME:WaitFrames(55)
 PrintInfo('[GIGA Z] charge terminée')
end
