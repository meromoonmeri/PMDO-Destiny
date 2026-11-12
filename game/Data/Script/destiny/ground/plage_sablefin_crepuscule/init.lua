require 'origin.common'
local scene = require 'destiny.plage_sablefin_scene'

local CARTE = 'plage_sablefin_crepuscule'
local AMBIANCE = 'crepuscule'
local plage_sablefin_crepuscule = {}
local state = {sortie_en_cours = false}

function plage_sablefin_crepuscule.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function plage_sablefin_crepuscule.Enter(map)
  scene.EnterCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_crepuscule.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_crepuscule.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function plage_sablefin_crepuscule.Exit(map)
  scene.ExitCarte()
end

function plage_sablefin_crepuscule.GameSave(map) end

function plage_sablefin_crepuscule.SortieCarrefour_Touch(obj, activator)
  scene.SortieCarrefour_Touch(activator, state)
end

function plage_sablefin_crepuscule.SeuilPassageAquatique_Touch(obj, activator)
  scene.SeuilPassageAquatique_Touch(activator, state)
end

return plage_sablefin_crepuscule
