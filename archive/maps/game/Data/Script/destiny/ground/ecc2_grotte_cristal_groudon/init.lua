-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ecc2_grotte_cristal_groudon = {}

function ecc2_grotte_cristal_groudon.Init(map)
end

function ecc2_grotte_cristal_groudon.Enter(map)
  GAME:FadeIn(30)
end

function ecc2_grotte_cristal_groudon.GameLoad(map)
  GAME:FadeIn(30)
end

function ecc2_grotte_cristal_groudon.Update(map, time)
end

return ecc2_grotte_cristal_groudon
