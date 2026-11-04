-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local sn_v3_forest_cave = {}

function sn_v3_forest_cave.Init(map)
end

function sn_v3_forest_cave.Enter(map)
  GAME:FadeIn(30)
end

function sn_v3_forest_cave.GameLoad(map)
  GAME:FadeIn(30)
end

function sn_v3_forest_cave.Update(map, time)
end

return sn_v3_forest_cave
