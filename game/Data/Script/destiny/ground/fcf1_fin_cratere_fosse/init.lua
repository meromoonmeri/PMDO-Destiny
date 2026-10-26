-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local fcf1_fin_cratere_fosse = {}

function fcf1_fin_cratere_fosse.Init(map)
end

function fcf1_fin_cratere_fosse.Enter(map)
  GAME:FadeIn(30)
end

function fcf1_fin_cratere_fosse.GameLoad(map)
  GAME:FadeIn(30)
end

function fcf1_fin_cratere_fosse.Update(map, time)
end

return fcf1_fin_cratere_fosse
