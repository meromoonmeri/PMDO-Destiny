-- Scène partagée des 4 ambiances de l'Étang du Doyen (etangdudoyen_*).
-- Prépare l'animation de nage du Grand Doyen devant la dernière pierre :
--   * Masque l'ombre standard au sol (HideShadow = true) pour éviter le disque noir sur l'eau
--   * Active et positionne le calque AnimLayer 'Nage_Grand_Doyen' (Etang_Nage_Ondes_<Ambiance>)
--     à (MapLoc.X - 8, MapLoc.Y + 4), soit exactement sous ShadowOffset = (0, 4).
require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'

local scene = {}
local NOMS_DOYEN = {'Grand_Doyen', 'Doyen_Draco', 'Draco'}

local function each_list(col, fn)
  if col == nil then return end
  if luanet ~= nil and luanet.each ~= nil then
    for item in luanet.each(col) do
      fn(item)
    end
    return
  end
  if type(col) == 'table' then
    for _, item in ipairs(col) do
      fn(item)
    end
  end
end

local function case_libre(map, x, y)
  if x < 0 or y < 0 then return false end
  if map == nil or map.Width == nil or map.Height == nil or map.GetObstacle == nil then
    return x <= 752 and y <= 560
  end
  if x + 16 > map.Width * 8 or y + 16 > map.Height * 8 then return false end
  for cx = math.floor(x / 8), math.floor((x + 15) / 8) do
    for cy = math.floor(y / 8), math.floor((y + 15) / 8) do
      if map:GetObstacle(cx, cy) ~= 0 then return false end
    end
  end
  return true
end

function scene.PositionPartenaire(map, hx, hy)
  local candidats = {
    {0, 24}, {-24, 0}, {24, 0}, {0, -24},
    {-16, 16}, {16, 16}, {-16, -16}, {16, -16},
  }
  for _, d in ipairs(candidats) do
    local px, py = hx + d[1], hy + d[2]
    if case_libre(map, px, py) then return px, py end
  end
  local max_y = (map ~= nil and map.Height ~= nil) and (map.Height * 8 - 24) or 552
  return hx, math.min(hy + 20, max_y)
end

function scene.TrouverDoyen()
  for _, nom in ipairs(NOMS_DOYEN) do
    local ch = CH(nom)
    if ch ~= nil then return ch end
  end
  return nil
end

function scene.AppliquerOndes(map, actif, x, y)
  if map == nil or map.Decorations == nil then return end
  each_list(map.Decorations, function(deco)
    if deco ~= nil and deco.Name == 'Nage_Grand_Doyen' then
      deco.Visible = (actif == true)
      if x ~= nil and y ~= nil and deco.Anims ~= nil then
        each_list(deco.Anims, function(anim)
          if anim ~= nil then
            anim.MapLoc = RogueElements.Loc(x - 8, y + 4)
          end
        end)
      end
    end
  end)
end

function scene.PreparerNage(map, personnage, x, y, dir)
  if personnage == nil then
    scene.AppliquerOndes(map, false)
    return nil
  end
  if x ~= nil and y ~= nil then
    GROUND:TeleportTo(personnage, x, y, dir or personnage.Direction or Direction.UpRight)
  elseif dir ~= nil then
    pcall(function() GROUND:EntTurn(personnage, dir) end)
  end
  pcall(function() personnage.HideShadow = true end)
  local px = personnage.Position ~= nil and personnage.Position.X or (x or 248)
  local py = personnage.Position ~= nil and personnage.Position.Y or (y or 272)
  scene.AppliquerOndes(map, true, px, py)
  return personnage
end

function scene.SynchroniserNageDoyen(map)
  local doyen = scene.TrouverDoyen()
  if doyen == nil then
    scene.AppliquerOndes(map, false)
    return nil
  end
  return scene.PreparerNage(map, doyen)
end

function scene.InitCarte(map, amb, state)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  state.sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
    if map.SetDestinyAmbiance ~= nil then
      pcall(function() map:SetDestinyAmbiance(amb, false) end)
    end
  end
  scene.SynchroniserNageDoyen(map)
  local hero = CH('PLAYER')
  if hero ~= nil and GAME ~= nil and GAME.GetPlayerPartyCount ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local px, py = scene.PositionPartenaire(map, hero.Position.X, hero.Position.Y)
    local partner = equipe_scene.Partenaire(px, py, hero.Direction)
    equipe_scene.Suivre(partner, hero)
  end
end

function scene.SynchroniserAmbiance(carte, state, avec_fondu)
  if not avec_fondu and meteo_reverie.AccesDirectDevSansScenario ~= nil
      and meteo_reverie.AccesDirectDevSansScenario() then
    return false
  end
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  local attendu = meteo_reverie.CarteEtangDoyen()
  if attendu == carte then return false end
  if state.sortie_en_cours then return true end
  state.sortie_en_cours = true
  local hero = CH('PLAYER')
  if hero ~= nil and (hero.Position.X > 0 or hero.Position.Y > 0) then
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.PassageAmbianceEtangDoyen = {
      carte = attendu,
      x = hero.Position.X,
      y = hero.Position.Y,
      dir = hero.Direction,
    }
  end
  if avec_fondu then GAME:FadeOut(false, 20) end
  GAME:EnterGroundMap('reverie', attendu, 'entrance')
  return true
end

function scene.RestaurerPassage(map, carte)
  local passage = SV ~= nil and SV.Destiny ~= nil and SV.Destiny.PassageAmbianceEtangDoyen or nil
  if passage ~= nil and passage.carte == carte then
    SV.Destiny.PassageAmbianceEtangDoyen = nil
    local hero = CH('PLAYER')
    if hero ~= nil and passage.x ~= nil and passage.y ~= nil then
      GROUND:TeleportTo(hero, passage.x, passage.y, passage.dir or hero.Direction)
      local partenaire = CH('Teammate1')
      if partenaire ~= nil then
        local px, py = scene.PositionPartenaire(map, passage.x, passage.y)
        GROUND:TeleportTo(partenaire, px, py, passage.dir or hero.Direction)
      end
    end
  end
end

function scene.EnterCarte(map, carte, state)
  state.sortie_en_cours = false
  if scene.SynchroniserAmbiance(carte, state, false) then return end
  scene.RestaurerPassage(map, carte)
  scene.SynchroniserNageDoyen(map)
  GAME:FadeIn(20)
  SOUND:PlayBGM('Luminous Spring.ogg', true)
end

function scene.GameLoadCarte(map, amb, carte, state)
  scene.InitCarte(map, amb, state)
  if scene.SynchroniserAmbiance(carte, state, false) then return end
  scene.RestaurerPassage(map, carte)
  scene.SynchroniserNageDoyen(map)
  GAME:FadeIn(20)
  SOUND:PlayBGM('Luminous Spring.ogg', true)
end

function scene.UpdateCarte(carte, state)
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.MomentScenario ~= nil
      and meteo_reverie.CarteEtangDoyen() ~= carte then
    scene.SynchroniserAmbiance(carte, state, true)
  end
end

return scene
