-- Animation de banc uniquement : poses et fissures superposées, pli de rendu temporaire.
function BATTLE_SCRIPT.LameV3_Espace(owner, ownerChar, context, args)
 -- À ce stade du moteur, Hit n'est pas encore renseigné ; l'animation précède la résolution.
 local cible=context.Target;local user=context.User
 local loc=RogueElements.Loc(cible.CharLoc.X*24+12,cible.CharLoc.Y*24+12)
 local function jouer(nom,direction)
  local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData(nom,1),1)
  anim:SetupEmitted(loc,0,direction)
  DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 end
 PrintInfo('[LAME V3] 9 rema nences/9 entailles cible='..tostring(cible.CharLoc)..' lanceur='..tostring(user.CharLoc))
 jouer('LameV3_Perspective',user.CharDir)
 for i=1,5 do SOUND:PlayBattleSE('DUN_Night_Slash');GAME:WaitFrames(9) end
 GAME:WaitFrames(20)
 luanet.load_assembly('PliSpatial');local pli=luanet.import_type('PliSpatial.Effet');assert(pli,'Pli spatial indisponible')
 pli.Demarrer(cible,42)
 PrintInfo('[LAME V3] fracture et pli réel ; convergence vers '..tostring(user.CharLoc))
 jouer('LameV3_VerreFeux',user.CharDir);SOUND:PlayBattleSE('DUN_Shadow_Force')
 GAME:WaitFrames(56)
end
