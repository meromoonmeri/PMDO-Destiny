-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ful1_rive_underground_lake = {}

function ful1_rive_underground_lake.Init(map)
end

function ful1_rive_underground_lake.Enter(map)
  GAME:FadeIn(30)
end

function ful1_rive_underground_lake.GameLoad(map)
  GAME:FadeIn(30)
end

function ful1_rive_underground_lake.Update(map, time)
end

return ful1_rive_underground_lake
