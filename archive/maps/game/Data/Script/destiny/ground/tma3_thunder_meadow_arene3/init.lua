-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local tma3_thunder_meadow_arene3 = {}

function tma3_thunder_meadow_arene3.Init(map)
end

function tma3_thunder_meadow_arene3.Enter(map)
  GAME:FadeIn(30)
end

function tma3_thunder_meadow_arene3.GameLoad(map)
  GAME:FadeIn(30)
end

function tma3_thunder_meadow_arene3.Update(map, time)
end

return tma3_thunder_meadow_arene3
