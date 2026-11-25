require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local guilde_decors = require 'destiny.guilde_destiny_decors'

local guilde_destiny_dortoir_nord_1 = {}
local sortie_en_cours = false

function guilde_destiny_dortoir_nord_1.Init(map)
  sortie_en_cours = false
  if DEBUG and DEBUG.EnableDbgCoro then DEBUG.EnableDbgCoro() end
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_dortoir_nord_1')
end

function guilde_destiny_dortoir_nord_1.Enter(map)
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_dortoir_nord_1')
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_dortoir_nord_1.GameLoad(map)
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_dortoir_nord_1')
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_dortoir_nord_1.Exit(map)
end

function guilde_destiny_dortoir_nord_1.Update(map)
  guilde_decors.SynchroniserAmbiance(map, 'guilde_destiny_dortoir_nord_1')
end

function guilde_destiny_dortoir_nord_1.SortieSud_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_couloir_ouest', 'EntreeNordMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 8, 0) end
end

require('destiny.guilde_cadrage_sud').Attacher(guilde_destiny_dortoir_nord_1, 'guilde_destiny_dortoir_nord_1')

return guilde_destiny_dortoir_nord_1
