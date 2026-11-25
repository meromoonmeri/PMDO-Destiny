-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local agm3_arene_groudon_magma = {}

function agm3_arene_groudon_magma.Init(map)
end

function agm3_arene_groudon_magma.Enter(map)
  GAME:FadeIn(30)
end

function agm3_arene_groudon_magma.GameLoad(map)
  GAME:FadeIn(30)
end

function agm3_arene_groudon_magma.Update(map, time)
end

return agm3_arene_groudon_magma
