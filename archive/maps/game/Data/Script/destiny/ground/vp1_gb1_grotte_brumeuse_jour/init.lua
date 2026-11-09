-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local vp1_gb1_grotte_brumeuse_jour = {}

function vp1_gb1_grotte_brumeuse_jour.Init(map)
end

function vp1_gb1_grotte_brumeuse_jour.Enter(map)
  GAME:FadeIn(30)
end

function vp1_gb1_grotte_brumeuse_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function vp1_gb1_grotte_brumeuse_jour.Update(map, time)
end

return vp1_gb1_grotte_brumeuse_jour
