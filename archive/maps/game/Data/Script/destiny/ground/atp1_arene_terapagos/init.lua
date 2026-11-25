-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local atp1_arene_terapagos = {}

function atp1_arene_terapagos.Init(map)
end

function atp1_arene_terapagos.Enter(map)
  GAME:FadeIn(30)
end

function atp1_arene_terapagos.GameLoad(map)
  GAME:FadeIn(30)
end

function atp1_arene_terapagos.Update(map, time)
end

return atp1_arene_terapagos
