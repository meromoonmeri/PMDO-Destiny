require 'origin.common'
local scene = require 'destiny.plage_sablefin_scene'

local CARTE = 'plage_sablefin_nuit'
local AMBIANCE = 'nuit'
local plage_sablefin_nuit = {}
local state = {sortie_en_cours = false}

function plage_sablefin_nuit.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function plage_sablefin_nuit.Enter(map)
  scene.EnterCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_nuit.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_nuit.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function plage_sablefin_nuit.Exit(map)
  scene.ExitCarte()
end

function plage_sablefin_nuit.GameSave(map) end

function plage_sablefin_nuit.SortieCarrefour_Touch(obj, activator)
  scene.SortieCarrefour_Touch(activator, state)
end

function plage_sablefin_nuit.SeuilPassageAquatique_Touch(obj, activator)
  scene.SeuilPassageAquatique_Touch(activator, state)
end

return plage_sablefin_nuit
