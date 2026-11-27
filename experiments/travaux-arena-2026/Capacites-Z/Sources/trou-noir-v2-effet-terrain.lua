-- Prototype de banc : événement appelé par la fiche de la capacité, pas par le script de test.
-- Les murs standard uniquement sont convertis en sol, sans toucher effets ni indestructibles.
function BATTLE_SCRIPT.TrouNoirV2_BriserMurs(owner, ownerChar, context, args)
  local map = _ZONE.CurrentMap
  local origin = context.User.CharLoc
  TASK:BranchCoroutine(function()
    -- Le vortex a le temps de naître avant la destruction. Le hitbox est lancé plus tard.
    GAME:WaitFrames(30)
    local count = 0
    for dy=-2,2 do
      for dx=-2,2 do
        local x, y = origin.X + dx, origin.Y + dy
        if x > 0 and y > 0 and x < map.Width-1 and y < map.Height-1 then
          local loc = RogueElements.Loc(x,y)
          local tile = map:GetTile(loc)
          if tile.Data.ID == _DATA.GenWall and tile.Effect.ID == '' then
            tile.Data = RogueEssence.Dungeon.TerrainTile(_DATA.GenFloor)
            count = count + 1
          end
        end
      end
    end
    map:MapModified(RogueElements.Loc(origin.X-3,origin.Y-3), RogueElements.Loc(7,7))
    PrintInfo('[TROU NOIR V2 TERRAIN] murs standards détruits='..count..' centre='..tostring(origin))
  end)
end
