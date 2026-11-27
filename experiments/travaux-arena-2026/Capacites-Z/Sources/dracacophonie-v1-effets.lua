-- État de banc séquentiel : un lancement à la fois, remis à zéro avant chaque action.
local touche=false
local cible_avant=nil
local hp_avant=nil
function BATTLE_SCRIPT.Dracaco_Charge(owner,ownerChar,context,args)
 touche=false;cible_avant=nil;hp_avant=nil
 local c=context.User;local v=RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('Dracaco_Charge',1),1)
 v:SetupEmitted(RogueElements.Loc(c.CharLoc.X*24+12,c.CharLoc.Y*24+12),0,c.CharDir)
 DUNGEON:PlayVFXAnim(v,RogueEssence.Content.DrawLayer.Front)
 SOUND:PlayBattleSE('_UNK_DUN_Clank');GAME:WaitFrames(72)
end
function BATTLE_SCRIPT.Dracaco_Avant(owner,ownerChar,context,args)
 cible_avant=context.Target;hp_avant=context.Target.HP
end
function BATTLE_SCRIPT.Dracaco_Apres(owner,ownerChar,context,args)
 if cible_avant==context.Target and hp_avant and context.Target.HP<hp_avant then touche=true end
 PrintInfo('[DRACACO DEGATS] avant='..tostring(hp_avant)..' apres='..tostring(context.Target.HP)..' touche='..tostring(touche))
end
function CONDITION_SCRIPT.Dracaco_BonusSiTouche(owner,ownerChar,context,args)
 PrintInfo('[DRACACO BONUS] activer='..tostring(touche))
 -- L'itérateur du moteur ne transmet qu'une valeur yield, pas return.
 if touche then coroutine.yield(true) end
end
