-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local cote10_07_cap_ouest_jour = {}

function cote10_07_cap_ouest_jour.Init(map)
end

function cote10_07_cap_ouest_jour.Enter(map)
  GAME:FadeIn(30)
end

function cote10_07_cap_ouest_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function cote10_07_cap_ouest_jour.Update(map, time)
end

return cote10_07_cap_ouest_jour
