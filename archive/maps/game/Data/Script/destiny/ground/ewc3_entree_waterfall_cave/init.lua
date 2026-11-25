-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ewc3_entree_waterfall_cave = {}

function ewc3_entree_waterfall_cave.Init(map)
end

function ewc3_entree_waterfall_cave.Enter(map)
  GAME:FadeIn(30)
end

function ewc3_entree_waterfall_cave.GameLoad(map)
  GAME:FadeIn(30)
end

function ewc3_entree_waterfall_cave.Update(map, time)
end

return ewc3_entree_waterfall_cave
