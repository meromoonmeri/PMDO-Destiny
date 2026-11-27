-- Décollage avec plumes et images rémanentes du véritable sprite du porteur.
function BATTLE_SCRIPT.PiqueSuperV2_Decollage(owner, ownerChar, context, args)
 local c=context.User
 local plume=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('PiqueSuperV2_Plumes',2),1)
 plume:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(plume,RogueEssence.Content.DrawLayer.Front)
 local a=RogueEssence.Dungeon.CharAnimFly(5)
 a.AnimLoc=c.CharLoc; a.CharDir=c.CharDir
 SOUND:PlayBattleSE('DUN_Fly')
 DUNGEON:CharSetAction(c,a)
 for i=1,8 do
  GAME:WaitFrames(3)
  local pos=RogueElements.Loc(c.MapLoc.X,c.MapLoc.Y-c.LocHeight)
  local ghost=RogueEssence.Content.CharAfterImage(pos,c.Appearance:ToCharID(),5,0,c.CharDir,0,11,110,0)
  DUNGEON:PlayVFXAnim(ghost,RogueEssence.Content.DrawLayer.Back)
 end
 PrintInfo('[PIQUE V2 Z] décollage plumes et rémanence terminé')
end
