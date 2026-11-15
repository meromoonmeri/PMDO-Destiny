require 'origin.common'
local suivi_interieurs = require 'destiny.suivi_interieurs'
local guilde_decors = require 'destiny.guilde_destiny_decors'

local guilde_destiny_grand_salon = {}
local sortie_en_cours = false

function guilde_destiny_grand_salon.Init(map)
  sortie_en_cours = false
  if DEBUG and DEBUG.EnableDbgCoro then DEBUG.EnableDbgCoro() end
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_grand_salon')
  pcall(guilde_decors.SynchroniserPorteSalon, map)
end

function guilde_destiny_grand_salon.Enter(map)
  if map ~= nil then
    map.EdgeView = (RogueEssence and RogueEssence.Dungeon and RogueEssence.Dungeon.BaseMap and RogueEssence.Dungeon.BaseMap.ScrollEdge.Clamp) or 1
  end
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_grand_salon')
  pcall(guilde_decors.SynchroniserPorteSalon, map)
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_grand_salon.GameLoad(map)
  pcall(guilde_decors.AppliquerAmbianceEtFenetres, map, 'guilde_destiny_grand_salon')
  pcall(guilde_decors.SynchroniserPorteSalon, map)
  suivi_interieurs.Activer(map)
  sortie_en_cours = false; GAME:FadeIn(20)
end

function guilde_destiny_grand_salon.Exit(map)
end

function guilde_destiny_grand_salon.Update(map)
end

function guilde_destiny_grand_salon.OuvrirPorteMaitre(map)
  guilde_decors.OuvrirPorteSalonDirect(map or GAME:GetCurrentGround())
end

function guilde_destiny_grand_salon.SeuilSud_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_missions', 'EscalierNordMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 1, 0) end
end
function guilde_destiny_grand_salon.SortieBureauMaitre_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  if not (SV and SV.Destiny and SV.Destiny.GuildePorteMaitreOuverte == true) then
    guilde_decors.OuvrirPorteSalonDirect(_G.GAME and GAME:GetCurrentGround() or nil)
  end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_bureau_maitre', 'EntreeSudMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 3, 0) end
end
function guilde_destiny_grand_salon.CouloirOuest_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_carrefour', 'EntreeEstMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 4, 0) end
end
function guilde_destiny_grand_salon.CouloirEst_Touch(obj, activator)
  if sortie_en_cours then return end
  if activator == nil or activator.EntName ~= 'PLAYER' then return end
  sortie_en_cours = true
  GAME:FadeOut(false, 20)
  if GAME.EnterGroundMap ~= nil then GAME:EnterGroundMap('guilde_destiny_interieur', 'guilde_destiny_couloir_ouest', 'EntreeOuestMarker', true) else GAME:EnterZone('guilde_destiny_interieur', -1, 8, 0) end
end

return guilde_destiny_grand_salon
