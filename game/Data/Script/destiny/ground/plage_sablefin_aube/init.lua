require 'origin.common'
local scene = require 'destiny.plage_sablefin_scene'

local CARTE = 'plage_sablefin_aube'
local AMBIANCE = 'aube'
local plage_sablefin_aube = {}
local state = {sortie_en_cours = false}

function plage_sablefin_aube.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function plage_sablefin_aube.Enter(map)
  scene.EnterCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_aube.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function plage_sablefin_aube.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function plage_sablefin_aube.Exit(map)
  scene.ExitCarte()
end

function plage_sablefin_aube.GameSave(map) end

function plage_sablefin_aube.SortieCarrefour_Touch(obj, activator)
  scene.SortieCarrefour_Touch(activator, state)
end

function plage_sablefin_aube.SeuilPassageAquatique_Touch(obj, activator)
  scene.SeuilPassageAquatique_Touch(activator, state)
end

return plage_sablefin_aube
