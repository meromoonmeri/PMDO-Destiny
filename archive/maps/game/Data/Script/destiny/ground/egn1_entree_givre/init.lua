-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local egn1_entree_givre = {}

function egn1_entree_givre.Init(map)
end

function egn1_entree_givre.Enter(map)
  GAME:FadeIn(30)
end

function egn1_entree_givre.GameLoad(map)
  GAME:FadeIn(30)
end

function egn1_entree_givre.Update(map, time)
end

return egn1_entree_givre
