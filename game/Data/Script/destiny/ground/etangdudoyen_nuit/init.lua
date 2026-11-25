require 'origin.common'
local scene = require 'destiny.etangdudoyen_scene'

local CARTE = 'etangdudoyen_nuit'
local AMBIANCE = 'nuit'
local etangdudoyen_nuit = {}
local state = {sortie_en_cours = false}

function etangdudoyen_nuit.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function etangdudoyen_nuit.Enter(map)
  scene.EnterCarte(map, CARTE, state)
end

function etangdudoyen_nuit.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function etangdudoyen_nuit.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function etangdudoyen_nuit.PreparerNage(map, personnage, x, y, dir)
  return scene.PreparerNage(map, personnage, x, y, dir)
end

function etangdudoyen_nuit.Exit(map) end
function etangdudoyen_nuit.GameSave(map) end

return etangdudoyen_nuit
