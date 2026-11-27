-- Décollage de banc avant la descente de la DashAction native.
function BATTLE_SCRIPT.PiqueSuper_Decollage(owner, ownerChar, context, args)
 local c=context.User
 local a=RogueEssence.Dungeon.CharAnimFly(5)
 a.AnimLoc=c.CharLoc
 a.CharDir=c.CharDir
 SOUND:PlayBattleSE('DUN_Fly')
 DUNGEON:CharSetAction(c,a)
 GAME:WaitFrames(24)
 PrintInfo('[PIQUE Z] décollage terminé')
end
