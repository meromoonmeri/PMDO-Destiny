-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local clairiere = {}

function clairiere.Init(map)
end

function clairiere.Enter(map)
  GAME:FadeIn(30)
end

function clairiere.GameLoad(map)
  GAME:FadeIn(30)
end

function clairiere.Update(map, time)
end

return clairiere
