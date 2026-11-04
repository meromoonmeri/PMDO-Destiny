-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local plage_bc1_grande_jour = {}

function plage_bc1_grande_jour.Init(map)
end

function plage_bc1_grande_jour.Enter(map)
  GAME:FadeIn(30)
end

function plage_bc1_grande_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function plage_bc1_grande_jour.Update(map, time)
end

return plage_bc1_grande_jour
