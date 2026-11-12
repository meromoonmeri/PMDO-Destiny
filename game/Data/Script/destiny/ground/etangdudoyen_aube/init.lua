require 'origin.common'
local scene = require 'destiny.etangdudoyen_scene'

local CARTE = 'etangdudoyen_aube'
local AMBIANCE = 'aube'
local etangdudoyen_aube = {}
local state = {sortie_en_cours = false}

function etangdudoyen_aube.Init(map)
  scene.InitCarte(map, AMBIANCE, state)
end

function etangdudoyen_aube.Enter(map)
  scene.EnterCarte(map, CARTE, state)
end

function etangdudoyen_aube.GameLoad(map)
  scene.GameLoadCarte(map, AMBIANCE, CARTE, state)
end

function etangdudoyen_aube.Update(map, time)
  scene.UpdateCarte(CARTE, state)
end

function etangdudoyen_aube.PreparerNage(map, personnage, x, y, dir)
  return scene.PreparerNage(map, personnage, x, y, dir)
end

function etangdudoyen_aube.Exit(map) end
function etangdudoyen_aube.GameSave(map) end

return etangdudoyen_aube
