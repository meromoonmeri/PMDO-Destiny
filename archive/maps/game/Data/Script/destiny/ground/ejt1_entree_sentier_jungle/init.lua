-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ejt1_entree_sentier_jungle = {}

function ejt1_entree_sentier_jungle.Init(map)
end

function ejt1_entree_sentier_jungle.Enter(map)
  GAME:FadeIn(30)
end

function ejt1_entree_sentier_jungle.GameLoad(map)
  GAME:FadeIn(30)
end

function ejt1_entree_sentier_jungle.Update(map, time)
end

return ejt1_entree_sentier_jungle
