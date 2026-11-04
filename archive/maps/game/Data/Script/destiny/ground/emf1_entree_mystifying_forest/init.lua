-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local emf1_entree_mystifying_forest = {}

function emf1_entree_mystifying_forest.Init(map)
end

function emf1_entree_mystifying_forest.Enter(map)
  GAME:FadeIn(30)
end

function emf1_entree_mystifying_forest.GameLoad(map)
  GAME:FadeIn(30)
end

function emf1_entree_mystifying_forest.Update(map, time)
end

return emf1_entree_mystifying_forest
