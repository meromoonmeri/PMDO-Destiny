-- Événement de banc : effets visuels centrés sur le lanceur.
function BATTLE_SCRIPT.ColereV1_Charge(owner,ownerChar,context,args)
 local c=context.User
 local pos=RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12)
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('ColereV1_Arriere',3),1)
 a:SetupEmitted(pos,0,c.CharDir);DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Back)
 local b=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('ColereV1_Avant',3),1)
 b:SetupEmitted(pos,0,c.CharDir);DUNGEON:PlayVFXAnim(b,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Flash_Cannon');GAME:WaitFrames(82)
 SOUND:PlayBattleSE('DUN_Explosion');GAME:WaitFrames(98)
end
