-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local etx1_entree_traversee_cristalline = {}

function etx1_entree_traversee_cristalline.Init(map)
end

function etx1_entree_traversee_cristalline.Enter(map)
  GAME:FadeIn(30)
end

function etx1_entree_traversee_cristalline.GameLoad(map)
  GAME:FadeIn(30)
end

function etx1_entree_traversee_cristalline.Update(map, time)
end

return etx1_entree_traversee_cristalline
