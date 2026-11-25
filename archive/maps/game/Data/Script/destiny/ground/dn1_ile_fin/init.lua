-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local dn1_ile_fin = {}

function dn1_ile_fin.Init(map)
end

function dn1_ile_fin.Enter(map)
  GAME:FadeIn(30)
end

function dn1_ile_fin.GameLoad(map)
  GAME:FadeIn(30)
end

function dn1_ile_fin.Update(map, time)
end

return dn1_ile_fin
