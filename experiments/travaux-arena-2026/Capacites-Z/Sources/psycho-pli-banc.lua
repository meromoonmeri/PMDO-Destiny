-- Effet de rendu expérimental : déclenché autour de chaque cible du banc.
function BATTLE_SCRIPT.PsychoPli_Concentration(owner, ownerChar, context, args)
 local c=context.User
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('PsychoEX_Concentration',2),1)
 anim:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Confusion');GAME:WaitFrames(38)
end
function BATTLE_SCRIPT.PsychoPli_Cible(owner, ownerChar, context, args)
 luanet.load_assembly('PliSpatial')
 local pli=luanet.import_type('PliSpatial.Effet')
 assert(pli,'Bibliothèque de pli introuvable')
 PrintInfo('[PLI SPATIAL] cible '..tostring(context.Target.CharLoc))
 pli.Demarrer(context.Target,60)
 SOUND:PlayBattleSE('DUN_Psybeam')
 GAME:WaitFrames(60)
end
