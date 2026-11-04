-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ecc1_entree_crystal_cave = {}

function ecc1_entree_crystal_cave.Init(map)
end

function ecc1_entree_crystal_cave.Enter(map)
  GAME:FadeIn(30)
end

function ecc1_entree_crystal_cave.GameLoad(map)
  GAME:FadeIn(30)
end

function ecc1_entree_crystal_cave.Update(map, time)
end

return ecc1_entree_crystal_cave
