-- Chant suggéré, bulles d'Aria de l'Écume et naissance de la sphère.
function BATTLE_SCRIPT.OndinesV2_Charge(owner, ownerChar, context, args)
 local c=context.User
 local pos=RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('OndinesV2_Charge',1),1)
 anim:SetupEmitted(pos,0,c.CharDir);DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Bubble')
 for i=1,4 do
  local p=RogueElements.Loc(pos.X+((i%2)*2-1)*(8+i*3),pos.Y-4-i*3)
  local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('Bubble_Pop_Blue',3),1)
  a:SetupEmitted(p,0,c.CharDir);DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
  GAME:WaitFrames(13)
 end
 GAME:WaitFrames(20);PrintInfo('[SYMPHONIE] formation de la sphere terminee')
end
