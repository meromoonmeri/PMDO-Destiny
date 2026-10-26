-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local ern1_entree_ruine = {}

function ern1_entree_ruine.Init(map)
end

function ern1_entree_ruine.Enter(map)
  GAME:FadeIn(30)
end

function ern1_entree_ruine.GameLoad(map)
  GAME:FadeIn(30)
end

function ern1_entree_ruine.Update(map, time)
end

return ern1_entree_ruine
