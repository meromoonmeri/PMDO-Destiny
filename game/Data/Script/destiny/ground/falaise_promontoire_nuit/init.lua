require 'origin.common'
local equipe_scene = require 'destiny.equipe_scene'
local meteo_reverie = require 'destiny.meteo_reverie'

local CARTE = 'falaise_promontoire_nuit'
local falaise_promontoire_nuit = {}
local SON_MER = 'Destiny_Falaise_Mer'
local sortie_en_cours = false

local function demarrer_mer()
  SOUND:StopBattleSE(SON_MER)
  SOUND:FadeInBattleSE(SON_MER, 90)
end

local function arreter_mer()
  SOUND:FadeOutBattleSE(SON_MER, 45)
end

local function case_libre(map, x, y)
  if x < 12 or y < 0 then return false end
  if map == nil or map.Width == nil or map.Height == nil or map.GetObstacle == nil then
    return x <= 624 and y <= 496
  end
  if x + 16 > map.Width * 8 or y + 16 > map.Height * 8 then return false end
  for cx = math.floor(x / 8), math.floor((x + 15) / 8) do
    for cy = math.floor(y / 8), math.floor((y + 15) / 8) do
      if map:GetObstacle(cx, cy) ~= 0 then return false end
    end
  end
  return true
end

local function position_partenaire(map, hx, hy)
  local candidats = {
    {0, 24}, {0, -24}, {-24, 0}, {24, 0},
    {16, 16}, {16, -16}, {-16, 16}, {-16, -16},
  }
  for _, d in ipairs(candidats) do
    local px, py = hx + d[1], hy + d[2]
    if case_libre(map, px, py) then return px, py end
  end
  return hx, math.min(hy + 24, 420)
end

local function installer_retour_reverie(map)
  if map == nil or map:FindObject('RetourCentreReverie') then return end
  local retour = RogueEssence.Ground.GroundObject()
  retour.EntName = 'RetourCentreReverie'
  retour.Collider = RogueElements.Rect(0, 176, 8, 256)
  retour.Passable = false
  retour:SetTriggerType(RogueEssence.Ground.GroundEntity.EEntityTriggerTypes.Touch)
  retour:OnMapInit()
  map:AddObject(retour)
end

local function synchroniser_ambiance(avec_fondu)
  if not avec_fondu and meteo_reverie.AccesDirectDevSansScenario ~= nil
      and meteo_reverie.AccesDirectDevSansScenario() then
    return false
  end
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  local attendu = meteo_reverie.CartePromontoire()
  if attendu == CARTE then return false end
  if sortie_en_cours then return true end
  sortie_en_cours = true
  local hero = CH('PLAYER')
  if hero ~= nil and (hero.Position.X > 0 or hero.Position.Y > 0) then
    SV.Destiny = SV.Destiny or {}
    SV.Destiny.PassageAmbiancePromontoire = {
      carte = attendu,
      x = hero.Position.X,
      y = hero.Position.Y,
      dir = hero.Direction,
    }
  end
  arreter_mer()
  if avec_fondu then GAME:FadeOut(false, 20) end
  GAME:EnterZone('falaise_promontoire', -1, meteo_reverie.IndexPromontoire(), 0)
  return true
end

local function restaurer_passage(map)
  local passage = SV ~= nil and SV.Destiny ~= nil and SV.Destiny.PassageAmbiancePromontoire or nil
  if passage ~= nil and passage.carte == CARTE then
    SV.Destiny.PassageAmbiancePromontoire = nil
    local hero = CH('PLAYER')
    if hero ~= nil and passage.x ~= nil and passage.y ~= nil then
      GROUND:TeleportTo(hero, passage.x, passage.y, passage.dir or hero.Direction)
      local partenaire = CH('Teammate1')
      if partenaire ~= nil then
        local px, py = position_partenaire(map, passage.x, passage.y)
        GROUND:TeleportTo(partenaire, px, py, passage.dir or hero.Direction)
      end
    end
  end
end

function falaise_promontoire_nuit.Init(map)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_retour_reverie(map)
  local hero = CH('PLAYER')
  if hero ~= nil and GAME:GetPlayerPartyCount() > 1 then
    local px, py = position_partenaire(map, hero.Position.X, hero.Position.Y)
    local partner = equipe_scene.Partenaire(px, py, hero.Direction)
    equipe_scene.Suivre(partner, hero)
  end
end

function falaise_promontoire_nuit.Enter(map)
  sortie_en_cours = false
  if synchroniser_ambiance(false) then return end
  restaurer_passage(map)
  demarrer_mer()
  GAME:FadeIn(20)
end

function falaise_promontoire_nuit.GameLoad(map)
  if meteo_reverie.SynchroniserZone ~= nil then meteo_reverie.SynchroniserZone() end
  sortie_en_cours = false
  if map ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
  installer_retour_reverie(map)
  if synchroniser_ambiance(false) then return end
  restaurer_passage(map)
  demarrer_mer()
  GAME:FadeIn(20)
end

function falaise_promontoire_nuit.Exit(map)
  arreter_mer()
end

function falaise_promontoire_nuit.Update(map, time)
  if SV ~= nil and SV.Destiny ~= nil and SV.Destiny.MomentScenario ~= nil
      and meteo_reverie.CartePromontoire() ~= CARTE then
    synchroniser_ambiance(true)
  end
end

function falaise_promontoire_nuit.RetourCentreReverie_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  if sortie_en_cours then return end
  sortie_en_cours = true
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PassageQuartier = {x = 1536, y = 1152, px = 1560, py = 1152, dir = 'Left'}
  arreter_mer()
  GAME:FadeOut(false, 20)
  GAME:EnterGroundMap('town02_waterfallvillage', 'reverie_centre', 'entrance')
end

function falaise_promontoire_nuit.GameSave(map)
end

return falaise_promontoire_nuit
