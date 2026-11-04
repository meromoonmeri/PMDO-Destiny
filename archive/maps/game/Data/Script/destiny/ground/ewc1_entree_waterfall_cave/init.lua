-- Squelette de script Destiny (carte importée sans script propre).
-- Simple fondu d'entrée ; cinématiques et raccordements : à écrire.
require 'origin.common'

local ewc1_entree_waterfall_cave = {}

function ewc1_entree_waterfall_cave.Init(map)
end

function ewc1_entree_waterfall_cave.Enter(map)
  GAME:FadeIn(30)
end

function ewc1_entree_waterfall_cave.GameLoad(map)
  GAME:FadeIn(30)
end

function ewc1_entree_waterfall_cave.Update(map, time)
end

return ewc1_entree_waterfall_cave
