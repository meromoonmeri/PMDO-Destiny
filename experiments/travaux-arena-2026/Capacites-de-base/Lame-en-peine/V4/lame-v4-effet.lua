-- Un seul sprite animé contient coupes, fracture et absorption, sans changement d'image plaquée.
function BATTLE_SCRIPT.LameV4_Espace(owner, ownerChar, context, args)
 local cible=context.Target;local user=context.User
 local loc=RogueElements.Loc(cible.CharLoc.X*24+12,cible.CharLoc.Y*24+12)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('LameV4_Continu',1),1)
 anim:SetupEmitted(loc,0,user.CharDir);DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 PrintInfo('[LAME V4] séquence continue de 9 coupes, fracture et convergence : '..tostring(user.CharLoc))
 for i=1,9 do GAME:WaitFrames(3);SOUND:PlayBattleSE('DUN_Night_Slash') end
 GAME:WaitFrames(11)
 luanet.load_assembly('PliSpatial');local pli=luanet.import_type('PliSpatial.Effet');assert(pli,'Pli spatial indisponible')
 pli.Demarrer(cible,34);SOUND:PlayBattleSE('DUN_Shadow_Force')
 PrintInfo('[LAME V4] pli du rendu déclenché au début de la fracture')
 GAME:WaitFrames(42)
end
