-- Banc séquentiel uniquement. Restaurer le drapeau d'origine après l'action.
local cible=nil
local precedent=nil
function BATTLE_SCRIPT.HelioV1_Charge(owner,ownerChar,context,args)
 assert(cible==nil,'Une suspension précédente n’a pas été nettoyée')
 local c=context.User;local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('HelioV1_Charge',1),1)
 a:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir);DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Charge_Beam');GAME:WaitFrames(64)
end
function BATTLE_SCRIPT.HelioV1_IgnoreTalentEtBreche(owner,ownerChar,context,args)
 local t=context.Target;cible=t;precedent=t.IntrinsicDisabled;t.IntrinsicDisabled=true
 PrintInfo('[HELIO TALENT] avant='..tostring(precedent)..' suspendu='..tostring(t.IntrinsicDisabled))
 local a=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('HelioV1_Breche',1),1)
 a:SetupEmitted(RogueElements.Loc(t.CharLoc.X*24+12,t.CharLoc.Y*24+12),0,t.CharDir);DUNGEON:PlayVFXAnim(a,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('DUN_Flash_Cannon');GAME:WaitFrames(54)
end
function BATTLE_SCRIPT.HelioV1_RestaureTalent(owner,ownerChar,context,args)
 if cible then cible.IntrinsicDisabled=precedent;PrintInfo('[HELIO TALENT] restaure='..tostring(cible.IntrinsicDisabled));cible=nil;precedent=nil end
end
