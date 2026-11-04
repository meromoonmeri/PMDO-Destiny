-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local eff2_entree_foggy_forest_sans_tentes = {}

function eff2_entree_foggy_forest_sans_tentes.Init(map)
end

function eff2_entree_foggy_forest_sans_tentes.Enter(map)
  GAME:FadeIn(30)
end

function eff2_entree_foggy_forest_sans_tentes.GameLoad(map)
  GAME:FadeIn(30)
end

function eff2_entree_foggy_forest_sans_tentes.Update(map, time)
end

return eff2_entree_foggy_forest_sans_tentes
