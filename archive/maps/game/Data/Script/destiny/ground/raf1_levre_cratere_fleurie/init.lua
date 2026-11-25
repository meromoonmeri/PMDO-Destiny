-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local raf1_levre_cratere_fleurie = {}

function raf1_levre_cratere_fleurie.Init(map)
end

function raf1_levre_cratere_fleurie.Enter(map)
  GAME:FadeIn(30)
end

function raf1_levre_cratere_fleurie.GameLoad(map)
  GAME:FadeIn(30)
end

function raf1_levre_cratere_fleurie.Update(map, time)
end

return raf1_levre_cratere_fleurie
