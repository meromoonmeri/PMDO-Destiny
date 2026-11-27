-- Événement de la fiche de banc ; rotation réelle des huit vues du lanceur.
function BATTLE_SCRIPT.Choupinova_Rotation(owner, ownerChar, context, args)
  local c = context.User
  local original = c.CharDir
  local dirs = {Direction.Down, Direction.DownLeft, Direction.Left, Direction.UpLeft,
                Direction.Up, Direction.UpRight, Direction.Right, Direction.DownRight}
  local start = 1
  for i,v in ipairs(dirs) do if v == original then start = i end end
  local glow = RogueEssence.Content.StaticAnim(RogueEssence.Content.AnimData('Choupinova_Aura', 2), 1)
  glow:SetupEmitted(RogueElements.Loc(c.CharLoc.X * 24 + 12, c.CharLoc.Y * 24 + 12), 0, original)
  DUNGEON:PlayVFXAnim(glow, RogueEssence.Content.DrawLayer.Front)
  SOUND:PlayBattleSE('DUN_Charm')
  for i=1,8 do
    local dir = dirs[((start - 1 + i) % 8) + 1]
    DUNGEON:CharSetAction(c, RogueEssence.Dungeon.CharAnimIdle(c.CharLoc, dir))
    GAME:WaitFrames(5)
  end
  DUNGEON:CharSetAction(c, RogueEssence.Dungeon.CharAnimIdle(c.CharLoc, original))
  PrintInfo('[CHOUPINOVA] tour complet terminé, direction restaurée='..tostring(c.CharDir))
end
