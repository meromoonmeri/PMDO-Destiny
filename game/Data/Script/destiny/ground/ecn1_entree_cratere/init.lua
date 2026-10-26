-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ecn1_entree_cratere = {}

function ecn1_entree_cratere.Init(map)
end

function ecn1_entree_cratere.Enter(map)
  GAME:FadeIn(30)
end

function ecn1_entree_cratere.GameLoad(map)
  GAME:FadeIn(30)
end

function ecn1_entree_cratere.Update(map, time)
end

return ecn1_entree_cratere
