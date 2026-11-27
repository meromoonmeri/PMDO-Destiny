-- Préparation de la vague électrique, en arrière du sprite natif de Raichu d'Alola.
function BATTLE_SCRIPT.ElectroSurfV5_Charge(owner, ownerChar, context, args)
 local c=context.User
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('ElectroSurfV5_Charge',1),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Charge_Beam_2')
 GAME:WaitFrames(96)
 PrintInfo('[ELECTRO SURF Z] charge et formation de la sphère terminées')
end
