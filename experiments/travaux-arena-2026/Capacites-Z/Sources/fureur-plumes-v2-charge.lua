-- Animation de préparation V2 ; particules petites, le sprite natif reste visible.
function BATTLE_SCRIPT.FureurPlumesV2_Charge(owner, ownerChar, context, args)
 local c=context.User
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('FureurV2_Charge',1),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Dark_Pulse')
 local fly=RogueEssence.Dungeon.CharAnimFly(5);fly.AnimLoc=c.CharLoc;fly.CharDir=c.CharDir
 DUNGEON:CharSetAction(c,fly)
 GAME:WaitFrames(40)
 PrintInfo('[FUREUR PLUMES V2] preparation terminee')
end
