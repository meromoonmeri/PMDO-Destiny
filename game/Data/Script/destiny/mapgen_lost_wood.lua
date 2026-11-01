-- Variante Forêt aux lucioles de Lost Wood.
-- La géométrie des deux rives reprend le principe du donjon de rivière ;
-- les décors de ruines sont placés séparément par le générateur natif.
-- Les lucioles sont des animations sans collision. Les passages restent du
-- sol praticable ; les galets décoratifs ne changent pas l’eau.

local function est_eau(map, x, y)
  if x < 0 or x >= map.Width or y < 0 or y >= map.Height then return false end
  local tile = map:GetTile(RogueElements.Loc(x, y))
  return tile ~= nil and tile.ID == 'water'
end

FLOOR_GEN_SCRIPT = FLOOR_GEN_SCRIPT or {}

function FLOOR_GEN_SCRIPT.DestinyLostWoodRiviereEtLucioles(map, args)
  local center = math.ceil(map.Width / 2)
  local shift = map.Rand:Next(-2, 3)
  -- Le cours d'eau reste lisible sans occuper toute la forêt.
  local left = center - 3 + shift
  local right = center + 3 + shift
  local leftOffset, rightOffset = map.Rand:Next(-1, 2), map.Rand:Next(-1, 2)
  local leftCount, rightCount = map.Rand:Next(1, 5), map.Rand:Next(1, 5)
  local stoneCount = 0

  for y = 0, map.Height - 1 do
    if leftCount <= 0 then
      if leftOffset < 0 then leftOffset = map.Rand:Next(-1, 1)
      elseif leftOffset > 0 then leftOffset = map.Rand:Next(0, 2)
      else leftOffset = map.Rand:Next(-1, 2) end
      leftCount = map.Rand:Next(1, 5)
    end
    if rightCount <= 0 then
      if rightOffset < 0 then rightOffset = map.Rand:Next(-1, 1)
      elseif rightOffset > 0 then rightOffset = map.Rand:Next(0, 2)
      else rightOffset = map.Rand:Next(-1, 2) end
      rightCount = map.Rand:Next(1, 5)
    end
    for x = math.max(1, left + leftOffset), math.min(map.Width - 2, right + rightOffset) do
      local loc = RogueElements.Loc(x, y)
      local tile = map:GetTile(loc)
      -- Les murs seuls deviennent de l'eau : ruines indestructibles, salles,
      -- escaliers, herbes et couloirs restent à leur place.
      if tile ~= nil and tile:TileEquivalent(map.WallTerrain) and tile.Effect.ID == '' then
        map:TrySetTile(loc, RogueEssence.Dungeon.Tile('water'))
      end
    end
    leftCount, rightCount = leftCount - 1, rightCount - 1
  end

  -- Comme dans le donjon de référence, les couloirs de terre/herbe restent
  -- continus au-dessus de l'eau : ils ne sont pas changés en une file de
  -- galets. Quelques pierres moussues décorent au contraire l'eau des berges.
  -- Leur présence ne change aucune collision : l'eau reste de l'eau.
  map.Map:AddLayer('Galets de rivière')
  local coucheGalets = map.Map.Layers[map.Map.Layers.Count - 1]
  coucheGalets.Layer = RogueEssence.Content.DrawLayer.Bottom
  local galets = {}
  local function bord_sol(x, y)
    local tile = map:GetTile(RogueElements.Loc(x, y))
    return tile ~= nil and tile:TileEquivalent(map.RoomTerrain)
  end
  for y = 2, map.Height - 3 do
    for x = 2, map.Width - 3 do
      local bord = bord_sol(x - 1, y) or bord_sol(x + 1, y) or bord_sol(x, y - 1) or bord_sol(x, y + 1)
      if stoneCount < 6 and est_eau(map, x, y) and bord and map.Rand:Next(100) < 24 then
        local proche = false
        for _, p in ipairs(galets) do
          if math.abs(p.x - x) <= 2 and math.abs(p.y - y) <= 2 then proche = true break end
        end
        if not proche then
          local variant = (x * 29 + y * 17) % 6
          coucheGalets.Tiles[x][y].Layers:Add(RogueEssence.Dungeon.TileLayer(RogueElements.Loc(variant, 0), 'LostWoodPierresV3'))
          table.insert(galets, {x = x, y = y})
          stoneCount = stoneCount + 1
        end
      end
    end
  end

  -- Sentiers de terre discrets dans les couloirs du plan natif. Les raccords
  -- sont purement visuels, dessinés sous les personnages et les objets. Les
  -- tuiles de ruines et les gués gardent leur aspect et leurs collisions.
  local sentiers = {}
  local function cle(x, y) return y * map.Width + x end
  for hall = 0, map.RoomPlan.HallCount - 1 do
    local rect = map.RoomPlan:GetHall(hall).Draw
    for x = math.max(1, rect.Start.X), math.min(map.Width - 2, rect.Start.X + rect.Size.X - 1) do
      for y = math.max(1, rect.Start.Y), math.min(map.Height - 2, rect.Start.Y + rect.Size.Y - 1) do
        local tile = map:GetTile(RogueElements.Loc(x, y))
        local decor = false
        for i = 0, map.Map.Layers.Count - 1 do
          if not map.Map.Layers[i].Tiles[x][y]:IsEmpty() then decor = true break end
        end
        if tile ~= nil and tile:TileEquivalent(map.RoomTerrain) and tile.Effect.ID == '' and not tile.Data.StableTex and not decor then
          sentiers[cle(x, y)] = true
        end
      end
    end
  end
  map.Map:AddLayer('Sentiers de Lost Wood')
  local coucheSentier = map.Map.Layers[map.Map.Layers.Count - 1]
  coucheSentier.Layer = RogueEssence.Content.DrawLayer.Bottom
  for y = 1, map.Height - 2 do
    for x = 1, map.Width - 2 do
      if sentiers[cle(x, y)] then
        local masque = 0
        if sentiers[cle(x, y - 1)] then masque = masque + 1 end
        if sentiers[cle(x + 1, y)] then masque = masque + 2 end
        if sentiers[cle(x, y + 1)] then masque = masque + 4 end
        if sentiers[cle(x - 1, y)] then masque = masque + 8 end
        coucheSentier.Tiles[x][y].Layers:Add(RogueEssence.Dungeon.TileLayer(RogueElements.Loc(masque, 0), 'LostWoodSentiers'))
      end
    end
  end

  -- Six poses de l'atelier Treehouse assemblées en une boucle ; leur dessin
  -- est purement décoratif, indépendant du terrain et de la météo.
  local lights = RogueEssence.Ground.AnimLayer('Lucioles')
  lights.Layer = RogueEssence.Content.DrawLayer.Front
  for y = 1, map.Height - 2 do
    for x = 1, map.Width - 2 do
      local loc = RogueElements.Loc(x, y)
      if not map:TileBlocked(loc) and map.Rand:Next(100) < 10 then
        local anim = RogueEssence.Content.ObjAnimData('LostWoodLucioles', map.Rand:Next(7, 13))
        local pos = RogueElements.Loc(x * 24 + map.Rand:Next(-4, 5), y * 24 + map.Rand:Next(-8, 1))
        lights.Anims:Add(RogueEssence.Ground.GroundAnim(anim, pos))
      end
    end
  end
  map.Map.Decorations:Add(lights)

  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.LostWoodTrip == 'retour' and DestinyInverserEscaliersLostWood ~= nil then
    DestinyInverserEscaliersLostWood(map)
  end
end
