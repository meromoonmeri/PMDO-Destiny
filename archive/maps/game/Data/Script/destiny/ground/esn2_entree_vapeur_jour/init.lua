-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local esn2_entree_vapeur_jour = {}

function esn2_entree_vapeur_jour.Init(map)
end

function esn2_entree_vapeur_jour.Enter(map)
  GAME:FadeIn(30)
end

function esn2_entree_vapeur_jour.GameLoad(map)
  GAME:FadeIn(30)
end

function esn2_entree_vapeur_jour.Update(map, time)
end

return esn2_entree_vapeur_jour
