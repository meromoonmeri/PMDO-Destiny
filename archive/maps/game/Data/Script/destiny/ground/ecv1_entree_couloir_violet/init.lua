-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ecv1_entree_couloir_violet = {}

function ecv1_entree_couloir_violet.Init(map)
end

function ecv1_entree_couloir_violet.Enter(map)
  GAME:FadeIn(30)
end

function ecv1_entree_couloir_violet.GameLoad(map)
  GAME:FadeIn(30)
end

function ecv1_entree_couloir_violet.Update(map, time)
end

return ecv1_entree_couloir_violet
