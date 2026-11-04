-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ece1_entree_crevasse_enneigee = {}

function ece1_entree_crevasse_enneigee.Init(map)
end

function ece1_entree_crevasse_enneigee.Enter(map)
  GAME:FadeIn(30)
end

function ece1_entree_crevasse_enneigee.GameLoad(map)
  GAME:FadeIn(30)
end

function ece1_entree_crevasse_enneigee.Update(map, time)
end

return ece1_entree_crevasse_enneigee
