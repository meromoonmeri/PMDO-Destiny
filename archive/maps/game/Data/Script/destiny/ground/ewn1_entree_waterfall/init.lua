-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ewn1_entree_waterfall = {}

function ewn1_entree_waterfall.Init(map)
end

function ewn1_entree_waterfall.Enter(map)
  GAME:FadeIn(30)
end

function ewn1_entree_waterfall.GameLoad(map)
  GAME:FadeIn(30)
end

function ewn1_entree_waterfall.Update(map, time)
end

return ewn1_entree_waterfall
