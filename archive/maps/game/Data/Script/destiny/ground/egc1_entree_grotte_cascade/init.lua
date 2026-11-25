-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local egc1_entree_grotte_cascade = {}

function egc1_entree_grotte_cascade.Init(map)
end

function egc1_entree_grotte_cascade.Enter(map)
  GAME:FadeIn(30)
end

function egc1_entree_grotte_cascade.GameLoad(map)
  GAME:FadeIn(30)
end

function egc1_entree_grotte_cascade.Update(map, time)
end

return egc1_entree_grotte_cascade
