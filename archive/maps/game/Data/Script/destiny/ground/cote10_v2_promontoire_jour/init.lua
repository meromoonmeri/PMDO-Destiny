-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local cote10_v2_promontoire_jour = {}

function cote10_v2_promontoire_jour.Init(map)
end

function cote10_v2_promontoire_jour.Enter(map)
  GAME:FadeIn(30)
end

function cote10_v2_promontoire_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function cote10_v2_promontoire_jour.Update(map, time)
end

return cote10_v2_promontoire_jour
