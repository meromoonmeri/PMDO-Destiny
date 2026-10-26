-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local v50812_10_defile_brume_jour = {}

function v50812_10_defile_brume_jour.Init(map)
end

function v50812_10_defile_brume_jour.Enter(map)
  GAME:FadeIn(30)
end

function v50812_10_defile_brume_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function v50812_10_defile_brume_jour.Update(map, time)
end

return v50812_10_defile_brume_jour
