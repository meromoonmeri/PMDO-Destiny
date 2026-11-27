-- Banc sans distorsion ni cage : rémanences, puis dernier coup d'âme.
function BATTLE_SCRIPT.LameV6_Espace(owner, ownerChar, context, args)
 local cible=context.Target;local user=context.User
 local loc=RogueElements.Loc(cible.CharLoc.X*24+12,cible.CharLoc.Y*24+12)
 local anim=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('LameV6_Ame',1),1)
 anim:SetupEmitted(loc,0,user.CharDir);DUNGEON:PlayVFXAnim(anim,RogueEssence.Content.DrawLayer.Front)
 PrintInfo('[LAME V6] neuf rémanences et neuf slashs, direction '..tostring(user.CharDir))
 for i=1,9 do GAME:WaitFrames(4);SOUND:PlayBattleSE('DUN_Night_Slash') end
 GAME:WaitFrames(6);SOUND:PlayBattleSE('DUN_Vacuum_Cut');SOUND:PlayBattleSE('DUN_Shadow_Force')
 PrintInfo('[LAME V6] dernier coup distinct, séparation spirituelle, absorption')
 GAME:WaitFrames(42)
end
