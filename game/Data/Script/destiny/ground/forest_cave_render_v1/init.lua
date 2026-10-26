-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local forest_cave_render_v1 = {}

function forest_cave_render_v1.Init(map)
end

function forest_cave_render_v1.Enter(map)
  GAME:FadeIn(30)
end

function forest_cave_render_v1.GameLoad(map)
  GAME:FadeIn(30)
end

function forest_cave_render_v1.Update(map, time)
end

return forest_cave_render_v1
