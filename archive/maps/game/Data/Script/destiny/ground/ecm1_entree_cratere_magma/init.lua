-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ecm1_entree_cratere_magma = {}

function ecm1_entree_cratere_magma.Init(map)
end

function ecm1_entree_cratere_magma.Enter(map)
  GAME:FadeIn(30)
end

function ecm1_entree_cratere_magma.GameLoad(map)
  GAME:FadeIn(30)
end

function ecm1_entree_cratere_magma.Update(map, time)
end

return ecm1_entree_cratere_magma
