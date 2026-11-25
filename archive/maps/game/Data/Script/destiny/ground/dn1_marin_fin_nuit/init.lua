-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local dn1_marin_fin_nuit = {}

function dn1_marin_fin_nuit.Init(map)
end

function dn1_marin_fin_nuit.Enter(map)
  GAME:FadeIn(30)
end

function dn1_marin_fin_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function dn1_marin_fin_nuit.Update(map, time)
end

return dn1_marin_fin_nuit
