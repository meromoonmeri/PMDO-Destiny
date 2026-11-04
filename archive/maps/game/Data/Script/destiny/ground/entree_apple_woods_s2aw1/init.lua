-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local entree_apple_woods_s2aw1 = {}

function entree_apple_woods_s2aw1.Init(map)
end

function entree_apple_woods_s2aw1.Enter(map)
  GAME:FadeIn(30)
end

function entree_apple_woods_s2aw1.GameLoad(map)
  GAME:FadeIn(30)
end

function entree_apple_woods_s2aw1.Update(map, time)
end

return entree_apple_woods_s2aw1
