-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local cote10_01_long_cap_nuit = {}

function cote10_01_long_cap_nuit.Init(map)
end

function cote10_01_long_cap_nuit.Enter(map)
  GAME:FadeIn(30)
end

function cote10_01_long_cap_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function cote10_01_long_cap_nuit.Update(map, time)
end

return cote10_01_long_cap_nuit
