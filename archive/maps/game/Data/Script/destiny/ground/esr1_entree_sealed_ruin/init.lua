-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local esr1_entree_sealed_ruin = {}

function esr1_entree_sealed_ruin.Init(map)
end

function esr1_entree_sealed_ruin.Enter(map)
  GAME:FadeIn(30)
end

function esr1_entree_sealed_ruin.GameLoad(map)
  GAME:FadeIn(30)
end

function esr1_entree_sealed_ruin.Update(map, time)
end

return esr1_entree_sealed_ruin
