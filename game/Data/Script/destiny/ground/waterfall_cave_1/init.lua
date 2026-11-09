-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local waterfall_cave_1 = {}

function waterfall_cave_1.Init(map)
end

function waterfall_cave_1.Enter(map)
  GAME:FadeIn(30)
end

function waterfall_cave_1.GameLoad(map)
  GAME:FadeIn(30)
end

function waterfall_cave_1.Update(map, time)
end

return waterfall_cave_1
