-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local bzf1_belvedere_zone_zero_fleuri = {}

function bzf1_belvedere_zone_zero_fleuri.Init(map)
end

function bzf1_belvedere_zone_zero_fleuri.Enter(map)
  GAME:FadeIn(30)
end

function bzf1_belvedere_zone_zero_fleuri.GameLoad(map)
  GAME:FadeIn(30)
end

function bzf1_belvedere_zone_zero_fleuri.Update(map, time)
end

return bzf1_belvedere_zone_zero_fleuri
