-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local pmd_petal_clearing = {}

function pmd_petal_clearing.Init(map)
end

function pmd_petal_clearing.Enter(map)
  GAME:FadeIn(30)
end

function pmd_petal_clearing.GameLoad(map)
  GAME:FadeIn(30)
end

function pmd_petal_clearing.Update(map, time)
end

return pmd_petal_clearing
