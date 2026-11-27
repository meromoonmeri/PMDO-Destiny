-- La case finale est celle calculée par WaveMotionAction. Explosion purement graphique.
function BATTLE_SCRIPT.CanonBlinde_Impact(owner, ownerChar, context, args)
 local tiles=context.StrikeLandTiles
 PrintInfo('[CANON BLINDE IMPACT] points='..tostring(tiles.Count))
 if tiles.Count==0 then return end
 local p=tiles[tiles.Count-1]
 CANON_BLINDE_IMPACT_X=p.X;CANON_BLINDE_IMPACT_Y=p.Y
 PrintInfo('[CANON BLINDE IMPACT] '..p.X..','..p.Y)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('CanonBlindeV2_DestructionFeu',1),1)
 anim:SetupEmitted(RogueElements.Loc(p.X*24+12,p.Y*24+12),0,context.User.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Self-Destruct')
 GAME:WaitFrames(68)
end
