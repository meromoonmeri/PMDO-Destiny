-- Départ suggéré : flèches Spectre autour du porteur ; vol d'Archéduc.
function BATTLE_SCRIPT.FureurPlumes_Charge(owner, ownerChar, context, args)
 local c=context.User
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('FureurPlumes_Charge',1),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Dark_Pulse')
 local fly=RogueEssence.Dungeon.CharAnimFly(5);fly.AnimLoc=c.CharLoc;fly.CharDir=c.CharDir
 DUNGEON:CharSetAction(c,fly)
 GAME:WaitFrames(52)
 PrintInfo('[FUREUR PLUMES] preparation et envol termines')
end
