-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local glacier_cliff_aurora_v1 = {}

function glacier_cliff_aurora_v1.Init(map)
end

function glacier_cliff_aurora_v1.Enter(map)
  GAME:FadeIn(30)
end

function glacier_cliff_aurora_v1.GameLoad(map)
  GAME:FadeIn(30)
end

function glacier_cliff_aurora_v1.Update(map, time)
end

return glacier_cliff_aurora_v1
