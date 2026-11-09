

  -- Fleurs naturelles non bloquantes : aucune modification du sol ou des
  -- passages. La formule est déterministe et ne consomme pas map.Rand.
  local fleurs = RogueEssence.Ground.AnimLayer('Fleurs des Bois Perdus')
  fleurs.Layer = RogueEssence.Content.DrawLayer.Bottom
  local sortes = {'Flowers_Town_1', 'Flowers_Town_2', 'Flowers_Town_3', 'Flowers_Town_4', 'Flowers_Town_5'}
  for y = 2, map.Height - 3 do
    for x = 2, map.Width - 3 do
      local loc = RogueElements.Loc(x, y)
      local tile = map:GetTile(loc)
      local libre = tile ~= nil and tile:TileEquivalent(map.RoomTerrain)
        and tile.Effect.ID == '' and not tile.Data.StableTex
        and not map:TileBlocked(loc) and not sentiers[cle(x, y)]
      if libre then
        -- Pas de décor sur une case utilisée par un calque existant.
        for i = 0, map.Map.Layers.Count - 1 do
          if not map.Map.Layers[i].Tiles[x][y]:IsEmpty() then libre = false break end
        end
      end
      -- Éviter les bords et les couloirs étroits pour les plus grandes fleurs.
      if libre then
        for dx = -1, 1 do
          for dy = -1, 1 do
            local voisin = map:GetTile(RogueElements.Loc(x + dx, y + dy))
            if voisin == nil or not voisin:TileEquivalent(map.RoomTerrain)
              or voisin.Effect.ID ~= '' or map:TileBlocked(RogueElements.Loc(x + dx, y + dy)) then
              libre = false
            end
          end
        end
      end
      local h = (x * x * 17 + y * y * 31 + x * y * 13 + x * 7 + y * 19 + map.Width * 11 + map.Height * 5) % 997
      if libre and h % 97 < 6 then
        local choix = sortes[(math.floor(h / 7) % #sortes) + 1]
        local anim = RogueEssence.Content.ObjAnimData(choix, 15)
        -- Les deux plus grands objets mesurent 32 px ; les centrer sur la case.
        local offset = (choix == 'Flowers_Town_1' or choix == 'Flowers_Town_2') and -4 or 0
        fleurs.Anims:Add(RogueEssence.Ground.GroundAnim(anim, RogueElements.Loc(x * 24 + offset, y * 24 + offset)))
      end
    end
  end
  map.Map.Decorations:Add(fleurs)
