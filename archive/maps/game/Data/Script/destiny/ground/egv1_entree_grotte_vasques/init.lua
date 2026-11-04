-- Squelette de script Destiny pour une carte importée de l'atelier projet-creation-pmdo.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local egv1_entree_grotte_vasques = {}

function egv1_entree_grotte_vasques.Init(map)
end

function egv1_entree_grotte_vasques.Enter(map)
  GAME:FadeIn(30)
end

function egv1_entree_grotte_vasques.GameLoad(map)
  GAME:FadeIn(30)
end

function egv1_entree_grotte_vasques.Update(map, time)
end

return egv1_entree_grotte_vasques
