-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local esc1_entree_star_cave = {}

function esc1_entree_star_cave.Init(map)
end

function esc1_entree_star_cave.Enter(map)
  GAME:FadeIn(30)
end

function esc1_entree_star_cave.GameLoad(map)
  GAME:FadeIn(30)
end

function esc1_entree_star_cave.Update(map, time)
end

return esc1_entree_star_cave
