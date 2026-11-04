-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local canon1_JC1_finale_jour = {}

function canon1_JC1_finale_jour.Init(map)
end

function canon1_JC1_finale_jour.Enter(map)
  GAME:FadeIn(30)
end

function canon1_JC1_finale_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function canon1_JC1_finale_jour.Update(map, time)
end

return canon1_JC1_finale_jour
