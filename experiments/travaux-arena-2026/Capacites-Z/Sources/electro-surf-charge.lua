-- Préparation de la vague électrique, en arrière du sprite natif de Raichu d'Alola.
function BATTLE_SCRIPT.ElectroSurf_Charge(owner, ownerChar, context, args)
 local c=context.User
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('ElectroSurf_Charge',2),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Charge_Beam_2')
 GAME:WaitFrames(45)
 PrintInfo('[ELECTRO SURF Z] vague chargée')
end
