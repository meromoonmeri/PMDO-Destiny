require 'origin.common'
local scene = require 'destiny.etangdudoyen_scene'

local CARTE = 'etangdudoyen_jour'
local AMBIANCE = 'jour'
local etangdudoyen_jour = {}
local state = {sortie_en_cours = false}

function etangdudoyen_jour.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function etangdudoyen_jour.Enter(map)
  scene.EnterCarte(map, CARTE, state)
end

function etangdudoyen_jour.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function etangdudoyen_jour.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function etangdudoyen_jour.PreparerNage(map, personnage, x, y, dir)
  return scene.PreparerNage(map, personnage, x, y, dir)
end

function etangdudoyen_jour.Exit(map) end
function etangdudoyen_jour.GameSave(map) end

return etangdudoyen_jour
