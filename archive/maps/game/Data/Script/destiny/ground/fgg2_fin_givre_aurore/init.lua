-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fgg2_fin_givre_aurore = {}

function fgg2_fin_givre_aurore.Init(map)
end

function fgg2_fin_givre_aurore.Enter(map)
  GAME:FadeIn(30)
end

function fgg2_fin_givre_aurore.GameLoad(map)
  GAME:FadeIn(30)
end

function fgg2_fin_givre_aurore.Update(map, time)
end

return fgg2_fin_givre_aurore
