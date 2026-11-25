-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local etc1_entree_clairiere_tropicale = {}

function etc1_entree_clairiere_tropicale.Init(map)
end

function etc1_entree_clairiere_tropicale.Enter(map)
  GAME:FadeIn(30)
end

function etc1_entree_clairiere_tropicale.GameLoad(map)
  GAME:FadeIn(30)
end

function etc1_entree_clairiere_tropicale.Update(map, time)
end

return etc1_entree_clairiere_tropicale
