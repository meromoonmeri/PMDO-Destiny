-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local foc1_fin_ocean_kyogre = {}

function foc1_fin_ocean_kyogre.Init(map)
end

function foc1_fin_ocean_kyogre.Enter(map)
  GAME:FadeIn(30)
end

function foc1_fin_ocean_kyogre.GameLoad(map)
  GAME:FadeIn(30)
end

function foc1_fin_ocean_kyogre.Update(map, time)
end

return foc1_fin_ocean_kyogre
