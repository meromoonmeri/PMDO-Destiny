-- Banc V2 : aura au sol derrière le Pokémon pendant un tour complet de ses huit vues.
function BATTLE_SCRIPT.ChoupinovaV2_Rotation(owner, ownerChar, context, args)
 local c = context.User
 local original = c.CharDir
 local dirs = {Direction.Down, Direction.DownLeft, Direction.Left, Direction.UpLeft, Direction.Up, Direction.UpRight, Direction.Right, Direction.DownRight}
 local start = 1
 for i,v in ipairs(dirs) do if v == original then start = i end end
 local aura = RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('ChoupinovaV2_Aura', 2), 1)
 aura:SetupEmitted(RogueElements.Loc(c.CharLoc.X * 24 + 12, c.CharLoc.Y * 24 + 12), 0, original)
 DUNGEON:PlayVFXAnim(aura, RogueEssence.Content.DrawLayer.Back)
 SOUND:PlayBattleSE('DUN_Charm')
 for i=1,8 do
  DUNGEON:CharSetAction(c, RogueEssence.Dungeon.CharAnimIdle(c.CharLoc, dirs[((start-1+i)%8)+1]))
  GAME:WaitFrames(5)
 end
 DUNGEON:CharSetAction(c, RogueEssence.Dungeon.CharAnimIdle(c.CharLoc, original))
 PrintInfo('[CHOUPINOVA V2] tour complet : direction restaurée='..tostring(c.CharDir))
end
