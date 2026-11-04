-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local frp1_fin_ruine_puits = {}

function frp1_fin_ruine_puits.Init(map)
end

function frp1_fin_ruine_puits.Enter(map)
  GAME:FadeIn(30)
end

function frp1_fin_ruine_puits.GameLoad(map)
  GAME:FadeIn(30)
end

function frp1_fin_ruine_puits.Update(map, time)
end

return frp1_fin_ruine_puits
