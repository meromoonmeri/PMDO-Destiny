-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fwc1_fin_waterfall_cave = {}

function fwc1_fin_waterfall_cave.Init(map)
end

function fwc1_fin_waterfall_cave.Enter(map)
  GAME:FadeIn(30)
end

function fwc1_fin_waterfall_cave.GameLoad(map)
  GAME:FadeIn(30)
end

function fwc1_fin_waterfall_cave.Update(map, time)
end

return fwc1_fin_waterfall_cave
