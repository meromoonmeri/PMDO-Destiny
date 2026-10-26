-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ebn1_entree_bristle = {}

function ebn1_entree_bristle.Init(map)
end

function ebn1_entree_bristle.Enter(map)
  GAME:FadeIn(30)
end

function ebn1_entree_bristle.GameLoad(map)
  GAME:FadeIn(30)
end

function ebn1_entree_bristle.Update(map, time)
end

return ebn1_entree_bristle
