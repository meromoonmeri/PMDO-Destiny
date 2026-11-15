require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local guilde_decors = require 'destiny.guilde_destiny_decors'

local guilde_destiny_couloir_est = {}
local sortie_en_cours = false

function guilde_destiny_couloir_est.Init(map)
  sortie_en_cours = false
  if DEBUG and DEBUG.EnableDbgCoro then DEBUG.EnableDbgCoro() end
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_couloir_est')
end

function guilde_destiny_couloir_est.Enter(map)
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_couloir_est')
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_couloir_est.GameLoad(map)
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_couloir_est')
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_couloir_est.Exit(map)
end

function guilde_destiny_couloir_est.Update(map)
  guilde_decors.SynchroniserAmbiance(map, 'guilde_destiny_couloir_est')
end

function guilde_destiny_couloir_est.SortieOuest_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_couloir_ouest', 'EntreeEstMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 8, 0) end
end
function guilde_destiny_couloir_est.SortieEst_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_chambre_heros', 'EntreeOuestMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 14, 0) end
end
function guilde_destiny_couloir_est.SortieNord_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_dortoir_nord_2', 'EntreeSudMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 11, 0) end
end
function guilde_destiny_couloir_est.SortieSud_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_dortoir_sud_2', 'EntreeNordMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 13, 0) end
end

return guilde_destiny_couloir_est
