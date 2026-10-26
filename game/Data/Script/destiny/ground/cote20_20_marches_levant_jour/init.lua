-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local cote20_20_marches_levant_jour = {}

function cote20_20_marches_levant_jour.Init(map)
end

function cote20_20_marches_levant_jour.Enter(map)
  GAME:FadeIn(30)
end

function cote20_20_marches_levant_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function cote20_20_marches_levant_jour.Update(map, time)
end

return cote20_20_marches_levant_jour
