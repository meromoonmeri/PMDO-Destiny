-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local eqs1_entree_sables_mouvants = {}

function eqs1_entree_sables_mouvants.Init(map)
end

function eqs1_entree_sables_mouvants.Enter(map)
  GAME:FadeIn(30)
end

function eqs1_entree_sables_mouvants.GameLoad(map)
  GAME:FadeIn(30)
end

function eqs1_entree_sables_mouvants.Update(map, time)
end

return eqs1_entree_sables_mouvants
