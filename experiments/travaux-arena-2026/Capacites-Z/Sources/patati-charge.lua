-- Cœur de Charme natif avant le saut de Mimiqui.
function BATTLE_SCRIPT.Patati_Charge(owner, ownerChar, context, args)
 local c=context.User
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('Charm',1),1)
 a:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Charm');GAME:WaitFrames(24)
end
