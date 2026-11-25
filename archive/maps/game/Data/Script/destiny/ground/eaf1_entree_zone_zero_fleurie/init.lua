-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local eaf1_entree_zone_zero_fleurie = {}

function eaf1_entree_zone_zero_fleurie.Init(map)
end

function eaf1_entree_zone_zero_fleurie.Enter(map)
  GAME:FadeIn(30)
end

function eaf1_entree_zone_zero_fleurie.GameLoad(map)
  GAME:FadeIn(30)
end

function eaf1_entree_zone_zero_fleurie.Update(map, time)
end

return eaf1_entree_zone_zero_fleurie
