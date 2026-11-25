-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fbs1_fin_bristle_sommet = {}

function fbs1_fin_bristle_sommet.Init(map)
end

function fbs1_fin_bristle_sommet.Enter(map)
  GAME:FadeIn(30)
end

function fbs1_fin_bristle_sommet.GameLoad(map)
  GAME:FadeIn(30)
end

function fbs1_fin_bristle_sommet.Update(map, time)
end

return fbs1_fin_bristle_sommet
