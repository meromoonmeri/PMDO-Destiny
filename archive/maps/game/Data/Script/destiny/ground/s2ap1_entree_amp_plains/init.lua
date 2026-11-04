-- Squelette de script Destiny pour une carte importée de l'atelier guilde-treehouse-pmd.
-- La carte ne déclare aucun callback : simple fondu d'entrée (règle L16 du manuel).
-- Cinématiques et raccordements : à écrire (voir PROJECT_CONTEXT.md).
require 'origin.common'

local s2ap1_entree_amp_plains = {}

function s2ap1_entree_amp_plains.Init(map)
end

function s2ap1_entree_amp_plains.Enter(map)
  GAME:FadeIn(30)
end

function s2ap1_entree_amp_plains.GameLoad(map)
  GAME:FadeIn(30)
end

function s2ap1_entree_amp_plains.Update(map, time)
end

return s2ap1_entree_amp_plains
