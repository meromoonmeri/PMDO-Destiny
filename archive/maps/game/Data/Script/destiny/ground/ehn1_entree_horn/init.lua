-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ehn1_entree_horn = {}

function ehn1_entree_horn.Init(map)
end

function ehn1_entree_horn.Enter(map)
  GAME:FadeIn(30)
end

function ehn1_entree_horn.GameLoad(map)
  GAME:FadeIn(30)
end

function ehn1_entree_horn.Update(map, time)
end

return ehn1_entree_horn
