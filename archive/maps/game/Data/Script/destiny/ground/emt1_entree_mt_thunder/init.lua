-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local emt1_entree_mt_thunder = {}

function emt1_entree_mt_thunder.Init(map)
end

function emt1_entree_mt_thunder.Enter(map)
  GAME:FadeIn(30)
end

function emt1_entree_mt_thunder.GameLoad(map)
  GAME:FadeIn(30)
end

function emt1_entree_mt_thunder.Update(map, time)
end

return emt1_entree_mt_thunder
