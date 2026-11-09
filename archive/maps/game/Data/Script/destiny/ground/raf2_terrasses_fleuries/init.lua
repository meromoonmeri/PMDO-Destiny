-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local raf2_terrasses_fleuries = {}

function raf2_terrasses_fleuries.Init(map)
end

function raf2_terrasses_fleuries.Enter(map)
  GAME:FadeIn(30)
end

function raf2_terrasses_fleuries.GameLoad(map)
  GAME:FadeIn(30)
end

function raf2_terrasses_fleuries.Update(map, time)
end

return raf2_terrasses_fleuries
