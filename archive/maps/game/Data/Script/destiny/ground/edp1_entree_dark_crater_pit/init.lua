-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local edp1_entree_dark_crater_pit = {}

function edp1_entree_dark_crater_pit.Init(map)
end

function edp1_entree_dark_crater_pit.Enter(map)
  GAME:FadeIn(30)
end

function edp1_entree_dark_crater_pit.GameLoad(map)
  GAME:FadeIn(30)
end

function edp1_entree_dark_crater_pit.Update(map, time)
end

return edp1_entree_dark_crater_pit
