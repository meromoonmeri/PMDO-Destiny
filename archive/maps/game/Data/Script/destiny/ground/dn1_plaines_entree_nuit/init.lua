-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local dn1_plaines_entree_nuit = {}

function dn1_plaines_entree_nuit.Init(map)
end

function dn1_plaines_entree_nuit.Enter(map)
  GAME:FadeIn(30)
end

function dn1_plaines_entree_nuit.GameLoad(map)
  GAME:FadeIn(30)
end

function dn1_plaines_entree_nuit.Update(map, time)
end

return dn1_plaines_entree_nuit
