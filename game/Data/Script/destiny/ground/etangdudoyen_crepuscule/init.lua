require 'origin.common'
local scene = require 'destiny.etangdudoyen_scene'

local CARTE = 'etangdudoyen_crepuscule'
local AMBIANCE = 'crepuscule'
local etangdudoyen_crepuscule = {}
local state = {sortie_en_cours = false}

function etangdudoyen_crepuscule.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function etangdudoyen_crepuscule.Enter(map)
  scene.EnterCarte(map, CARTE, state)
end

function etangdudoyen_crepuscule.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function etangdudoyen_crepuscule.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function etangdudoyen_crepuscule.PreparerNage(map, personnage, x, y, dir)
  return scene.PreparerNage(map, personnage, x, y, dir)
end

function etangdudoyen_crepuscule.Exit(map) end
function etangdudoyen_crepuscule.GameSave(map) end

return etangdudoyen_crepuscule
