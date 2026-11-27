-- Charge de type Ténèbres en arrière du sprite avant la ruée.
function BATTLE_SCRIPT.DarkBodyV2_Charge(owner, ownerChar, context, args)
 local c=context.User
 local pos=RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('DarkBodyV2_Charge',1),1)
 anim:SetupEmitted(pos,0,c.CharDir);DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Dark_Pulse');GAME:WaitFrames(48)
 PrintInfo('[DARK BODY V2] charge terminee')
end
