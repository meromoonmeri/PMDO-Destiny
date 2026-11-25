-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fst1_fin_star_cave = {}

function fst1_fin_star_cave.Init(map)
end

function fst1_fin_star_cave.Enter(map)
  GAME:FadeIn(30)
end

function fst1_fin_star_cave.GameLoad(map)
  GAME:FadeIn(30)
end

function fst1_fin_star_cave.Update(map, time)
end

return fst1_fin_star_cave
