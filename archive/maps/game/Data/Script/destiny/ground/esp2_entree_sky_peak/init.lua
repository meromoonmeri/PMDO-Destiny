-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local esp2_entree_sky_peak = {}

function esp2_entree_sky_peak.Init(map)
end

function esp2_entree_sky_peak.Enter(map)
  GAME:FadeIn(30)
end

function esp2_entree_sky_peak.GameLoad(map)
  GAME:FadeIn(30)
end

function esp2_entree_sky_peak.Update(map, time)
end

return esp2_entree_sky_peak
