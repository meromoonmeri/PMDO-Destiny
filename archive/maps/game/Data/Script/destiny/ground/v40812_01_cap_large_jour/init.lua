-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local v40812_01_cap_large_jour = {}

function v40812_01_cap_large_jour.Init(map)
end

function v40812_01_cap_large_jour.Enter(map)
  GAME:FadeIn(30)
end

function v40812_01_cap_large_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function v40812_01_cap_large_jour.Update(map, time)
end

return v40812_01_cap_large_jour
