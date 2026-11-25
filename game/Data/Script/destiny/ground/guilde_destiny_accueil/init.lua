-- Salle d'accueil de la Grande Guilde Destiny (512x384 échelle native DS 1x (64x48 tuiles 8x8), ratio 4:3 viewport PMDO, fond marron assombri),
-- raccordée au sud à PorteGuilde (guilde_cliff_*) et au nord à guilde_destiny_missions.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local guilde_decors = require 'destiny.guilde_destiny_decors'
local meteo_reverie = require 'destiny.meteo_reverie'

local guilde_destiny_accueil = {}
local sortie_en_cours = false

local function retourner_falaise_guilde()
  if sortie_en_cours then return end
  sortie_en_cours = true
  if meteo_reverie ~= nil and meteo_reverie.SynchroniserZone ~= nil then
    meteo_reverie.SynchroniserZone()
  end
  local carte = (meteo_reverie ~= nil and meteo_reverie.CarteGuilde ~= nil and meteo_reverie.CarteGuilde()) or 'guilde_cliff_jour'
  local idx = (meteo_reverie ~= nil and meteo_reverie.IndexGuilde ~= nil and meteo_reverie.IndexGuilde()) or 23
  SV.Destiny = SV.Destiny or {}
  SV.Destiny.PassageAmbiance = {
    carte = carte,
    x = 232,
    y = 282,
    dir = (Direction ~= nil and Direction.Down) or 0,
  }
  GAME:FadeOut(false, 20)
  GAME:EnterZone('town02_waterfallvillage', -1, idx, 0)
end

local function entrer_grande_salle()
  if sortie_en_cours then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then
    GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_missions', 'ArriveeDepuisAccueilMarker', true)
  else
    GAME:EnterZone('guilde_destiny_interieur', -1, 1, 0)
  end
end

function guilde_destiny_accueil.Init(map)
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_accueil')
  if map ~= nil and RogueEssence ~= nil and RogueEssence.Dungeon ~= nil and RogueEssence.Dungeon.BaseMap ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
end

function guilde_destiny_accueil.Enter(map) pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_accueil'); suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function guilde_destiny_accueil.GameLoad(map) pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_accueil'); suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function guilde_destiny_accueil.Update(map, time)
  guilde_decors.SynchroniserAmbiance(map, 'guilde_destiny_accueil')
end
function guilde_destiny_accueil.Exit(map) end
function guilde_destiny_accueil.GameSave(map) end

function guilde_destiny_accueil.SortieGuilde_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  retourner_falaise_guilde()
end

function guilde_destiny_accueil.EscalierNord_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  entrer_grande_salle()
end

require('destiny.guilde_cadrage_sud').Attacher(guilde_destiny_accueil, 'guilde_destiny_accueil')

return guilde_destiny_accueil
