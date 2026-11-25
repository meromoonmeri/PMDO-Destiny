-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local rzd1_ruines_zarbi = {}

function rzd1_ruines_zarbi.Init(map)
end

function rzd1_ruines_zarbi.Enter(map)
  GAME:FadeIn(30)
end

function rzd1_ruines_zarbi.GameLoad(map)
  GAME:FadeIn(30)
end

function rzd1_ruines_zarbi.Update(map, time)
end

return rzd1_ruines_zarbi
