-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local v40812_03_double_belvedere_nuit = {}

function v40812_03_double_belvedere_nuit.Init(map)
end

function v40812_03_double_belvedere_nuit.Enter(map)
  GAME:FadeIn(30)
end

function v40812_03_double_belvedere_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function v40812_03_double_belvedere_nuit.Update(map, time)
end

return v40812_03_double_belvedere_nuit
