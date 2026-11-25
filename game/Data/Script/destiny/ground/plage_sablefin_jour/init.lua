require 'origin.common'
local scene = require 'destiny.plage_sablefin_scene'

local CARTE = 'plage_sablefin_jour'
local AMBIANCE = 'jour'
local plage_sablefin_jour = {}
local state = {sortie_en_cours = false}

function plage_sablefin_jour.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function plage_sablefin_jour.Enter(map)
  scene.EnterCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_jour.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_jour.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function plage_sablefin_jour.Exit(map)
  scene.ExitCarte()
end

function plage_sablefin_jour.GameSave(map) end

function plage_sablefin_jour.SortieCarrefour_Touch(obj, activator)
  scene.SortieCarrefour_Touch(activator, state)
end

function plage_sablefin_jour.SeuilPassageAquatique_Touch(obj, activator)
  scene.SeuilPassageAquatique_Touch(activator, state)
end

return plage_sablefin_jour
