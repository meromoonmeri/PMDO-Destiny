-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local eff1_entree_foggy_forest = {}

function eff1_entree_foggy_forest.Init(map)
end

function eff1_entree_foggy_forest.Enter(map)
  GAME:FadeIn(30)
end

function eff1_entree_foggy_forest.GameLoad(map)
  GAME:FadeIn(30)
end

function eff1_entree_foggy_forest.Update(map, time)
end

return eff1_entree_foggy_forest
