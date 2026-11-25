-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local esj1_entree_southern_jungle = {}

function esj1_entree_southern_jungle.Init(map)
end

function esj1_entree_southern_jungle.Enter(map)
  GAME:FadeIn(30)
end

function esj1_entree_southern_jungle.GameLoad(map)
  GAME:FadeIn(30)
end

function esj1_entree_southern_jungle.Update(map, time)
end

return esj1_entree_southern_jungle
