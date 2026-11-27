-- Banc : volume projeté selon l'orientation, puis pulsation et rupture ; aucune distorsion du rendu.
function BATTLE_SCRIPT.LameV5_Espace(owner, ownerChar, context, args)
 local cible=context.Target;local user=context.User
 local loc=RogueElements.Loc(cible.CharLoc.X*24+12,cible.CharLoc.Y*24+12)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('LameV5_Volume',1),1)
 anim:SetupEmitted(loc,0,user.CharDir);DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 PrintInfo('[LAME V5] cage de 16 slashs orientée '..tostring(user.CharDir))
 for i=1,8 do GAME:WaitFrames(4);SOUND:PlayBattleSE('DUN_Night_Slash') end
 GAME:WaitFrames(20)
 SOUND:PlayBattleSE('_UNK_DUN_Shatter')
 PrintInfo('[LAME V5] rupture après pulsation, sans distorsion')
 GAME:WaitFrames(38)
end
