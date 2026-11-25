-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local rvt2_no_jour = {}

function rvt2_no_jour.Init(map)
end

function rvt2_no_jour.Enter(map)
  GAME:FadeIn(30)
end

function rvt2_no_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function rvt2_no_jour.Update(map, time)
end

return rvt2_no_jour
