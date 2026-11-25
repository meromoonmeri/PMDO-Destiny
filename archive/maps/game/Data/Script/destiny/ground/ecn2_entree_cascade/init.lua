-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ecn2_entree_cascade = {}

function ecn2_entree_cascade.Init(map)
end

function ecn2_entree_cascade.Enter(map)
  GAME:FadeIn(30)
end

function ecn2_entree_cascade.GameLoad(map)
  GAME:FadeIn(30)
end

function ecn2_entree_cascade.Update(map, time)
end

return ecn2_entree_cascade
