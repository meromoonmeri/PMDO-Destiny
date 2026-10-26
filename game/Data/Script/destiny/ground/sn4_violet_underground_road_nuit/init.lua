-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local sn4_violet_underground_road_nuit = {}

function sn4_violet_underground_road_nuit.Init(map)
end

function sn4_violet_underground_road_nuit.Enter(map)
  GAME:FadeIn(30)
end

function sn4_violet_underground_road_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function sn4_violet_underground_road_nuit.Update(map, time)
end

return sn4_violet_underground_road_nuit
