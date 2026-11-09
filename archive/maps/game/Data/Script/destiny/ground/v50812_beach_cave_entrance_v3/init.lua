-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local v50812_beach_cave_entrance_v3 = {}

function v50812_beach_cave_entrance_v3.Init(map)
end

function v50812_beach_cave_entrance_v3.Enter(map)
  GAME:FadeIn(30)
end

function v50812_beach_cave_entrance_v3.GameLoad(map)
  GAME:FadeIn(30)
end

function v50812_beach_cave_entrance_v3.Update(map, time)
end

return v50812_beach_cave_entrance_v3
