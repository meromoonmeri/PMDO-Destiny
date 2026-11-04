-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ewl1_entree_waterfall_ledge = {}

function ewl1_entree_waterfall_ledge.Init(map)
end

function ewl1_entree_waterfall_ledge.Enter(map)
  GAME:FadeIn(30)
end

function ewl1_entree_waterfall_ledge.GameLoad(map)
  GAME:FadeIn(30)
end

function ewl1_entree_waterfall_ledge.Update(map, time)
end

return ewl1_entree_waterfall_ledge
