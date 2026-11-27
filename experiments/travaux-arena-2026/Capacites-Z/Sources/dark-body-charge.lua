-- Charge générée et pulsation Ténèbres native ; images rémanentes pendant le dash natif.
function BATTLE_SCRIPT.DarkBody_Charge(owner, ownerChar, context, args)
 local c=context.User
 local pos=RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('DarkBody_Charge',1),1)
 anim:SetupEmitted(pos,0,c.CharDir);DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 local native=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('Dark_Pulse_Particle',3),1)
 native:SetupEmitted(pos,0,c.CharDir);DUNGEON:PlayVFXAnim(native,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Dark_Pulse');GAME:WaitFrames(48)
 PrintInfo('[DARK BODY] charge terminee')
end
