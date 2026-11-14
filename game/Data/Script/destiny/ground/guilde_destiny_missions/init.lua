-- Grande Salle aux deux murs plats de la Grande Guilde Destiny (1112x760, zéro mixel, sans motif ni mobilier),
-- raccordée par l'escalier nord à guilde_destiny_accueil.
require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'

local guilde_destiny_missions = {}
local sortie_en_cours = false

local function remonter_accueil()
  if sortie_en_cours then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then
    GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_accueil', 'EscalierNordMarker', true)
  else
    GAME:EnterZone('guilde_destiny_interieur', -1, 0, 0)
  end
end

function guilde_destiny_missions.Init(map)
  if map ~= nil and RogueEssence ~= nil and RogueEssence.Dungeon ~= nil and RogueEssence.Dungeon.BaseMap ~= nil then
    map.EdgeView = RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp
  end
end

function guilde_destiny_missions.Enter(map) suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function guilde_destiny_missions.GameLoad(map) suivi_interieurs.Activer(map); sortie_en_cours = false; GAME:FadeIn(20) end
function guilde_destiny_missions.Update(map, time) end
function guilde_destiny_missions.Exit(map) end
function guilde_destiny_missions.GameSave(map) end

function guilde_destiny_missions.EscalierNord_Touch(obj, activator)
  if activator ~= nil and activator.EntName ~= 'PLAYER' then return end
  remonter_accueil()
end

return guilde_destiny_missions
